import os
from pathlib import Path
from urllib.parse import urlparse

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from flask import current_app


def b2_enabled():
    return all(os.getenv(name, '').strip() for name in (
        'B2_APPLICATION_KEY_ID', 'B2_APPLICATION_KEY', 'B2_BUCKET_NAME', 'B2_ENDPOINT'
    ))


def _client():
    endpoint = os.getenv('B2_ENDPOINT', '').strip()
    return boto3.client(
        's3',
        endpoint_url=endpoint,
        aws_access_key_id=os.getenv('B2_APPLICATION_KEY_ID', '').strip(),
        aws_secret_access_key=os.getenv('B2_APPLICATION_KEY', '').strip(),
        region_name=os.getenv('B2_REGION', 'us-east-1').strip() or 'us-east-1',
    )


def upload(file_storage, original_filename, content_type=None):
    """Upload permanently to B2 when configured; otherwise save locally."""
    if b2_enabled():
        safe_name = Path(original_filename).name.replace(' ', '_')
        import uuid
        key = f"materials/{uuid.uuid4().hex}-{safe_name}"
        extra = {'ContentType': content_type or 'application/octet-stream'}
        _client().upload_fileobj(file_storage, os.getenv('B2_BUCKET_NAME').strip(), key, ExtraArgs=extra)
        return key

    folder = Path(current_app.config['UPLOAD_FOLDER'])
    folder.mkdir(parents=True, exist_ok=True)
    import uuid
    extension = Path(original_filename).suffix.lower()
    filename = f'{uuid.uuid4().hex}{extension}'
    file_storage.save(folder / filename)
    return filename


def delete(key):
    if not key:
        return
    if b2_enabled():
        try:
            _client().delete_object(Bucket=os.getenv('B2_BUCKET_NAME').strip(), Key=key)
        except (BotoCoreError, ClientError):
            current_app.logger.exception('Falha ao excluir arquivo do Backblaze B2: %s', key)
        return
    try:
        (Path(current_app.config['UPLOAD_FOLDER']) / key).unlink()
    except FileNotFoundError:
        pass


def presigned_url(key, expires=900):
    if b2_enabled():
        return _client().generate_presigned_url(
            'get_object',
            Params={'Bucket': os.getenv('B2_BUCKET_NAME').strip(), 'Key': key},
            ExpiresIn=expires,
        )
    return None


def is_b2_key(key):
    return bool(key and key.startswith('materials/'))
