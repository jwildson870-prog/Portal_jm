import os,re,uuid
from urllib.parse import urlparse
from pathlib import Path
from flask import Blueprint,render_template,request,redirect,url_for,flash,abort,current_app
from flask_login import login_required,current_user
from ..extensions import db
from ..models import Series,Subject,Content,User
admin_bp=Blueprint('admin',__name__,url_prefix='/admin')
ALLOWED={'explanation','pdf','slide','video'}
def guard():
    if not current_user.is_authenticated: return login_required(lambda:None)()
    if not current_user.is_admin: abort(403)
@admin_bp.before_request
def admin_guard():
    if not current_user.is_authenticated: return redirect(url_for('auth.login',next=request.path))
    if not current_user.is_admin: abort(403)
def valid_url(v):
    p=urlparse(v or ''); return p.scheme in ('http','https') and bool(p.netloc)
def save_pdf(file):
    if not file or not file.filename: return None
    if not file.filename.lower().endswith('.pdf'): return False
    name=f'{uuid.uuid4().hex}.pdf'; Path(current_app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True); file.save(Path(current_app.config['UPLOAD_FOLDER'])/name); return name
@admin_bp.get('/')
def dashboard(): return render_template('admin/dashboard.html',series=Series.query.count(),subjects=Subject.query.count(),contents=Content.query.count(),users=User.query.count())
@admin_bp.route('/series',methods=['GET','POST'])
def series_list():
    if request.method=='POST':
        name=request.form.get('name','').strip()
        if not name: flash('Informe o nome da série.','error')
        elif Series.query.filter_by(name=name).first(): flash('Série já existe.','error')
        else: db.session.add(Series(name=name)); db.session.commit(); flash('Série criada.','success')
    return render_template('admin/series.html',series=Series.query.order_by(Series.id).all())
@admin_bp.route('/series/<int:id>/editar',methods=['GET','POST'])
def series_edit(id):
    s=Series.query.get_or_404(id)
    if request.method=='POST':
        n=request.form.get('name','').strip(); other=Series.query.filter(Series.name==n,Series.id!=id).first()
        if not n or other: flash('Nome inválido ou já utilizado.','error')
        else: s.name=n; db.session.commit(); flash('Série atualizada.','success'); return redirect(url_for('admin.series_list'))
    return render_template('admin/edit_simple.html',title='Editar série',value=s.name,action=url_for('admin.series_edit',id=id))
@admin_bp.post('/series/<int:id>/excluir')
def series_delete(id):
    s=Series.query.get_or_404(id); db.session.delete(s); db.session.commit(); flash('Série excluída.','success'); return redirect(url_for('admin.series_list'))
@admin_bp.route('/subjects',methods=['GET','POST'])
def subjects_list():
    if request.method=='POST':
        name=request.form.get('name','').strip(); sid=request.form.get('series_id','')
        s=Series.query.get(int(sid)) if sid.isdigit() else None
        if not name or not s: flash('Informe matéria e série.','error')
        elif Subject.query.filter_by(name=name,series_id=s.id).first(): flash('Matéria já existe nessa série.','error')
        else: db.session.add(Subject(name=name,series_id=s.id)); db.session.commit(); flash('Matéria criada.','success')
    return render_template('admin/subjects.html',subjects=Subject.query.order_by(Subject.id).all(),series=Series.query.order_by(Series.id).all())
@admin_bp.route('/subjects/<int:id>/editar',methods=['GET','POST'])
def subject_edit(id):
    s=Subject.query.get_or_404(id)
    if request.method=='POST':
        n=request.form.get('name','').strip(); sid=request.form.get('series_id',''); series=Series.query.get(int(sid)) if sid.isdigit() else None
        dup=Subject.query.filter(Subject.name==n,Subject.series_id==series.id if series else False,Subject.id!=id).first() if series else None
        if not n or not series or dup: flash('Dados inválidos ou duplicados.','error')
        else: s.name=n; s.series_id=series.id; db.session.commit(); flash('Matéria atualizada.','success'); return redirect(url_for('admin.subjects_list'))
    return render_template('admin/subject_edit.html',subject=s,series=Series.query.all())
@admin_bp.post('/subjects/<int:id>/excluir')
def subject_delete(id):
    s=Subject.query.get_or_404(id); db.session.delete(s); db.session.commit(); flash('Matéria excluída.','success'); return redirect(url_for('admin.subjects_list'))
@admin_bp.get('/contents')
def contents(): return render_template('admin/contents.html',contents=Content.query.order_by(Content.id.desc()).all())
def content_form(c=None):
    series=Series.query.order_by(Series.id).all(); subjects=Subject.query.order_by(Subject.id).all()
    if request.method=='POST':
        sid=request.form.get('series_id',''); subid=request.form.get('subject_id',''); kind=request.form.get('kind',''); title=request.form.get('title','').strip(); desc=request.form.get('description','').strip(); body=request.form.get('body','').strip(); url=request.form.get('external_url','').strip()
        s=Series.query.get(int(sid)) if sid.isdigit() else None; sub=Subject.query.get(int(subid)) if subid.isdigit() else None
        if not title or not s or not sub or sub.series_id!=s.id or kind not in ALLOWED: flash('Preencha os dados obrigatórios corretamente.','error'); return None,series,subjects
        if kind in ('slide','video') and not valid_url(url): flash('Informe uma URL HTTP/HTTPS válida.','error'); return None,series,subjects
        if kind=='explanation' and not body: flash('Informe o texto da explicação.','error'); return None,series,subjects
        old_file=c.file_name if c else None; new_file=old_file
        if kind=='pdf':
            uploaded=save_pdf(request.files.get('pdf'))
            if uploaded is False: flash('Envie um arquivo PDF.','error'); return None,series,subjects
            if uploaded: new_file=uploaded
            elif not old_file: flash('Envie um arquivo PDF.','error'); return None,series,subjects
        else: new_file=None
        if c is None: c=Content()
        c.title=title;c.description=desc;c.kind=kind;c.body=body if kind=='explanation' else None;c.external_url=url if kind in ('slide','video') else None;c.file_name=new_file;c.series_id=s.id;c.subject_id=sub.id
        db.session.add(c); db.session.commit()
        if old_file and old_file!=new_file:
            try: os.remove(Path(current_app.config['UPLOAD_FOLDER'])/old_file)
            except FileNotFoundError: pass
        return c,None,None
    return c,series,subjects
@admin_bp.route('/contents/new',methods=['GET','POST'])
def content_new():
    c,series,subjects=content_form()
    if c: flash('Conteúdo criado.','success'); return redirect(url_for('admin.contents'))
    return render_template('admin/content_form.html',content=None,series=series,subjects=subjects)
@admin_bp.route('/contents/<int:id>/edit',methods=['GET','POST'])
def content_edit(id):
    c=Content.query.get_or_404(id); result,series,subjects=content_form(c)
    if result and result.id: flash('Conteúdo atualizado.','success'); return redirect(url_for('admin.contents'))
    return render_template('admin/content_form.html',content=c,series=series,subjects=subjects)
@admin_bp.post('/contents/<int:id>/delete')
def content_delete(id):
    c=Content.query.get_or_404(id); f=c.file_name; db.session.delete(c); db.session.commit()
    if f:
        try: os.remove(Path(current_app.config['UPLOAD_FOLDER'])/f)
        except FileNotFoundError: pass
    flash('Conteúdo excluído.','success'); return redirect(url_for('admin.contents'))
@admin_bp.get('/users')
def users(): return render_template('admin/users.html',users=User.query.order_by(User.id).all())
@admin_bp.get('/settings')
def settings(): return render_template('admin/settings.html')
