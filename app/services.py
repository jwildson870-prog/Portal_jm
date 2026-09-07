import os
from .extensions import db
from .models import User,Series,Subject,Content

def ensure_admin():
    email=os.getenv('ADMIN_EMAIL','professor@portaljm.com').strip().lower(); password=os.getenv('ADMIN_PASSWORD','PortalJM@2026')
    if not email or not password: return None,False
    admins=User.query.filter_by(role='admin').order_by(User.id).all()
    admin=admins[0] if admins else None
    if admin is None:
        admin=User(name=os.getenv('ADMIN_NAME','Professor JM'),email=email,role='admin'); admin.set_password(password); db.session.add(admin)
    else:
        admin.name=os.getenv('ADMIN_NAME',admin.name); admin.email=email; admin.set_password(password)
        for extra in admins[1:]:
            extra.role='student'
    # Se o e-mail configurado pertencer a outro usuário, ele não pode virar segundo admin.
    other=User.query.filter(User.email==email, User.id!=admin.id).first()
    if other:
        other.role='student'
    db.session.commit(); return admin, True

def seed_initial_content():
    data={'1ª Série':['Química Geral'], '2ª Série':['Química Orgânica'], '3ª Série':['Físico-Química'], '4ª Série':['Química Aplicada']}
    topics={('1ª Série','Química Geral'):['Estrutura Atômica','Prótons, nêutrons e elétrons','Tabela Periódica','Ligações Químicas'],('2ª Série','Química Orgânica'):['Funções Orgânicas','Hidrocarbonetos'],('3ª Série','Físico-Química'):['Eletroquímica','Termoquímica'],('4ª Série','Química Aplicada'):['Química Ambiental','Química no Cotidiano']}
    for sname,subjects in data.items():
        s=Series.query.filter_by(name=sname).first() or Series(name=sname); db.session.add(s); db.session.flush()
        for subname in subjects:
            sub=Subject.query.filter_by(name=subname,series_id=s.id).first() or Subject(name=subname,series_id=s.id); db.session.add(sub); db.session.flush()
            for title in topics[(sname,subname)]:
                if not Content.query.filter_by(title=title,subject_id=sub.id).first(): db.session.add(Content(title=title,description=f'Conteúdo introdutório de {title}.',kind='explanation',body=f'<p><strong>{title}</strong></p><p>Material inicial de demonstração do Portal JM – Química. O professor pode editar este conteúdo pelo painel administrativo.</p>',series_id=s.id,subject_id=sub.id))
    db.session.commit()
