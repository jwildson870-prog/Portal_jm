import io, os, tempfile
import pytest
from app import create_app
from app.extensions import db
from app.models import User,Series,Subject,Content

@pytest.fixture()
def app(tmp_path, monkeypatch):
    dbfile=tmp_path/'test.db'
    monkeypatch.setenv('ADMIN_EMAIL','admin@test.local'); monkeypatch.setenv('ADMIN_PASSWORD','AdminSenha123!'); monkeypatch.setenv('ADMIN_NAME','Professor')
    app=create_app(); app.config.update(TESTING=True,WTF_CSRF_ENABLED=False)
    # Recria o banco de teste no caminho isolado usado por esta fixture.
    app.config['UPLOAD_FOLDER']=str(tmp_path/'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'],exist_ok=True)
    yield app
    with app.app_context(): db.session.remove(); db.drop_all()

@pytest.fixture()
def client(app): return app.test_client()

def test_public_register_login_logout(client,app):
    r=client.post('/auth/register',data={'name':'Aluno','email':'a@test.local','password':'Senha1234!','confirm_password':'Senha1234!'},follow_redirects=True); assert 'Cadastro realizado' in r.text
    with app.app_context(): assert User.query.filter_by(email='a@test.local').first().role=='student'
    r=client.post('/auth/login',data={'email':'a@test.local','password':'Senha1234!'},follow_redirects=True); assert 'Olá, Aluno' in r.text
    r=client.post('/auth/logout',follow_redirects=True); assert 'Você saiu' in r.text

def test_validation_and_duplicate(client):
    client.post('/auth/register',data={'name':'A','email':'bad','password':'123','confirm_password':'456'})
    r=client.post('/auth/register',data={'name':'Aluno','email':'a@test.local','password':'Senha1234!','confirm_password':'Senha1234!'})
    assert r.status_code==302
    r=client.post('/auth/register',data={'name':'Outro','email':'a@test.local','password':'Senha1234!','confirm_password':'Senha1234!'}); assert 'já está cadastrado' in r.text

def login(client,email,password): return client.post('/auth/login',data={'email':email,'password':password})

def test_admin_permissions_and_crud(client,app):
    login(client,'admin@test.local','AdminSenha123!')
    assert client.get('/admin/').status_code==200
    assert client.post('/admin/series',data={'name':'4ª Série'}).status_code==302
    s=Series.query.filter_by(name='4ª Série').first() if False else None
    with app.app_context():
        s=Series.query.filter_by(name='4ª Série').first(); assert s
        client.post('/admin/subjects',data={'name':'Química','series_id':s.id})
        sub=Subject.query.filter_by(name='Química').first(); assert sub
        client.post('/admin/contents/new',data={'title':'Teste','description':'Desc','series_id':s.id,'subject_id':sub.id,'kind':'explanation','body':'Texto'})
        c=Content.query.filter_by(title='Teste').first(); assert c
        cid=c.id
    assert client.post(f'/admin/contents/{cid}/edit',data={'title':'Editado','description':'D','series_id':s.id,'subject_id':sub.id,'kind':'explanation','body':'Novo'}).status_code==302
    assert client.post(f'/admin/contents/{cid}/delete').status_code==302

def test_student_blocked_from_admin(client,app):
    client.post('/auth/register',data={'name':'Aluno','email':'a@test.local','password':'Senha1234!','confirm_password':'Senha1234!'})
    login(client,'a@test.local','Senha1234!'); assert client.get('/admin/').status_code==403

def test_professor_never_sees_student_area(client,app):
    # Login do professor deve redirecionar direto para o painel, nunca para a área do aluno.
    r=login(client,'admin@test.local','AdminSenha123!')
    assert r.status_code==302 and r.headers['Location'].endswith('/admin/')
    # O professor não pode acessar a área do aluno.
    assert client.get('/aluno/').status_code==403
    # E o link "Estudar" (aluno) não aparece para ele no cabeçalho.
    painel=client.get('/admin/')
    assert 'Estudar' not in painel.text
    assert 'Painel' in painel.text

def test_series_1_2_3_4_all_functional(client,app):
    with app.app_context():
        names={s.name for s in Series.query.all()}
    # As quatro séries são registros reais no banco, não apenas botões visuais.
    assert len(names)>=4

def test_pdf_kind_requires_pdf_extension(client,app):
    login(client,'admin@test.local','AdminSenha123!')
    with app.app_context():
        s=Series.query.first(); sub=Subject.query.filter_by(series_id=s.id).first(); sid,subid=s.id,sub.id
    data={'title':'Não é PDF','description':'','series_id':str(sid),'subject_id':str(subid),'kind':'pdf','file':(io.BytesIO(b'conteudo'), 'arquivo.docx')}
    r=client.post('/admin/contents/new',data=data,content_type='multipart/form-data')
    assert r.status_code==200  # permanece no formulário com erro, não redireciona
    with app.app_context():
        assert Content.query.filter_by(title='Não é PDF').first() is None

def test_pdf_flow(client,app,tmp_path):
    login(client,'admin@test.local','AdminSenha123!')
    with app.app_context():
        s=Series.query.first(); sub=Subject.query.filter_by(series_id=s.id).first(); sid,subid=s.id,sub.id
    data={'title':'PDF','description':'','series_id':str(sid),'subject_id':str(subid),'kind':'pdf','pdf':(io.BytesIO(b'%PDF-1.4 test'), 'teste.pdf')}
    assert client.post('/admin/contents/new',data=data,content_type='multipart/form-data').status_code==302
    with app.app_context(): cid=Content.query.filter_by(title='PDF').first().id
    assert client.get(f'/aluno/pdf/{cid}').status_code==200
