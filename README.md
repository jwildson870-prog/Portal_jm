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

## Publicação de materiais — painel do professor

O painel do professor mantém a interface do Portal JM e oferece uma área de publicação rápida com quatro fontes:

- **Meu dispositivo:** abre o seletor de arquivos do computador/celular e aceita PDF, imagens, PowerPoint, Word e TXT, até 25 MB.
- **Google Drive:** abre o Drive em uma nova aba para o professor escolher o arquivo e colar o link de compartilhamento no Portal JM.
- **Outro lugar:** aceita links HTTP/HTTPS de OneDrive, Dropbox, sites e outros serviços.
- **Escrever aqui:** permite publicar uma explicação diretamente no portal.

A integração do seletor oficial do Google Drive (Picker dentro do próprio Portal JM) exige credenciais/API do Google Cloud e pode ser adicionada em uma etapa posterior. O fluxo por link já funciona sem expor credenciais do Drive.

A remoção de materiais permanece disponível no backend, mas foi retirada da interface desta etapa para ser trabalhada depois.


## Acesso de demonstração
Por padrão, o sistema usa `professor@portaljm.com` / `PortalJM@2026` como administrador. Em produção, recomenda-se alterar essas variáveis no Render.
