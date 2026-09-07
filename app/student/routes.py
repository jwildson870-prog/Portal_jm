from pathlib import Path
from mimetypes import guess_type
from flask import Blueprint,render_template,abort,send_from_directory,current_app,redirect,url_for
from flask_login import login_required,current_user
from ..models import Series,Subject,Content

student_bp=Blueprint('student',__name__,url_prefix='/aluno')

@student_bp.before_request
def guard():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login', next='/aluno/'))
    if current_user.is_admin:
        abort(403)

@student_bp.get('/')
def dashboard():
    return render_template('student/dashboard.html',series=Series.query.order_by(Series.id).all())

@student_bp.get('/serie/<int:id>')
def series(id):
    return render_template('student/series.html',series=Series.query.get_or_404(id))

@student_bp.get('/materia/<int:id>')
def subject(id):
    return render_template('student/subject.html',subject=Subject.query.get_or_404(id))

@student_bp.get('/conteudo/<int:id>')
def content(id):
    return render_template('student/content.html',content=Content.query.get_or_404(id))


def _send_content_file(content, force_mimetype=None):
    if content.kind not in ('file', 'pdf') or not content.file_name:
        abort(404)

    upload_folder = Path(current_app.config['UPLOAD_FOLDER'])
    file_path = upload_folder / content.file_name
    if not file_path.is_file():
        # The database may survive a Render redeploy while local uploads do not.
        abort(404, description='Este arquivo não está disponível no armazenamento do servidor.')

    mimetype = force_mimetype or guess_type(file_path.name)[0] or 'application/octet-stream'
    return send_from_directory(
        upload_folder,
        file_path.name,
        mimetype=mimetype,
        as_attachment=False,
        conditional=True,
        max_age=0,
    )


@student_bp.get('/arquivo/<int:id>')
def arquivo(id):
    return _send_content_file(Content.query.get_or_404(id))


@student_bp.get('/pdf/<int:id>')
def pdf(id):
    content = Content.query.get_or_404(id)
    if content.kind != 'pdf':
        abort(404)
    return _send_content_file(content, 'application/pdf')
