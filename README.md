# Portal JM – Química

Sistema educacional em Flask com cadastro, login, sessões, permissões ALUNO/ADMINISTRADOR, CRUD de séries/matérias/conteúdos, explicações, PDFs, slides, vídeo-aulas e Google OAuth opcional.

## Rodar localmente

Python 3.11+ recomendado:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

Copie `.env.example` para `.env`, defina uma `SECRET_KEY`, `ADMIN_EMAIL` e `ADMIN_PASSWORD`, e rode:

```bash
python app.py
```

Acesse `http://127.0.0.1:5000`.

## Administrador

O sistema cria/atualiza somente um administrador usando as variáveis `ADMIN_EMAIL`, `ADMIN_PASSWORD` e `ADMIN_NAME`. O cadastro público sempre cria ALUNO.

Também existe o comando:

```bash
flask --app app.py create-admin
```

## Google OAuth

Crie um cliente OAuth no Google Cloud Console e configure a URI de callback exatamente como `GOOGLE_REDIRECT_URI`. Depois preencha `GOOGLE_CLIENT_ID` e `GOOGLE_CLIENT_SECRET` no `.env`. Em produção use HTTPS e a URL pública.

## Banco

Local: SQLite. Produção: PostgreSQL. Exemplo:

```env
DATABASE_URL=postgresql+psycopg2://usuario:senha@host:5432/banco
```

## PDFs

No desenvolvimento os PDFs ficam em `uploads/`. Em hospedagem com filesystem efêmero, use armazenamento persistente (disco persistente ou bucket externo). O banco guarda a referência do arquivo, permitindo trocar a camada de armazenamento depois.

## Render

Build: `pip install -r requirements.txt`  
Start: `gunicorn app:app`

Configure no painel do Render `SECRET_KEY`, `DATABASE_URL`, `ADMIN_NAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` e, se usar Google, as três variáveis OAuth. Para PostgreSQL, use a URL do banco do Render.

## Segurança

Senhas são armazenadas somente como hash; CSRF é aplicado aos POST; rotas administrativas verificam o papel no servidor; cadastro não permite promoção a administrador; segredos ficam no `.env`; arquivos não executáveis são aceitos como PDF apenas.
