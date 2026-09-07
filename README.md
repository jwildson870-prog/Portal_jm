# Portal JM – Química

Portal educacional em Flask/Jinja com autenticação, separação entre PROFESSOR e ALUNO, PostgreSQL/Neon, publicação de materiais e PWA instalável no Android.

## O que foi preservado e corrigido

- Login separado do painel interno.
- Professor entra em `/admin/`; aluno entra em `/aluno/`.
- Proteção das rotas no backend por papel de usuário.
- PostgreSQL continua sendo configurado por `DATABASE_URL` — não há migração para SQLite em produção.
- Séries, matérias, conteúdos, links e uploads existentes continuam usando as mesmas tabelas.
- Rotas de arquivos agora enviam o MIME correto e abrem PDFs/imagens/arquivos em vez de depender de HTML intermediário.
- `UPLOAD_FOLDER` é configurável para usar um diretório persistente no Render.
- Interface responsiva com menu lateral no desktop, menu lateral fechado por padrão no celular e barra inferior fixa no mobile.
- PWA com `manifest.json`, service worker e ícones existentes.
- Templates reorganizados para evitar blocos Jinja duplicados, especialmente `base.html`.

## Rodar localmente

Recomendado: Python 3.11+.

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

Copie `.env.example` para `.env` e configure pelo menos:

```env
SECRET_KEY=uma-chave-grande-e-aleatoria
DATABASE_URL=postgresql+psycopg2://USUARIO:SENHA@HOST:5432/BANCO
ADMIN_NAME=Professor JM
ADMIN_EMAIL=professor@portaljm.com
ADMIN_PASSWORD=troque-esta-senha
UPLOAD_FOLDER=./uploads
SESSION_COOKIE_SECURE=false
```

Depois:

```bash
python app.py
```

Acesse `http://127.0.0.1:5000`.

### Desenvolvimento sem Neon

Para testes locais, o projeto ainda aceita SQLite quando `DATABASE_URL` não estiver definido. Isso é apenas um fallback de desenvolvimento; o ambiente de produção deve usar o PostgreSQL do Neon.

## Neon / PostgreSQL

O código usa diretamente a variável `DATABASE_URL`. Exemplos aceitos:

```env
DATABASE_URL=postgresql://usuario:senha@host:5432/banco
```

ou:

```env
DATABASE_URL=postgresql+psycopg2://usuario:senha@host:5432/banco
```

Não apague essa variável no Render. O banco guarda usuários, séries, matérias e referências dos materiais; ele não é usado como armazenamento binário dos uploads.

## Uploads e armazenamento persistente no Render

O banco PostgreSQL/Neon e os arquivos são camadas diferentes.

Por padrão, os arquivos são salvos em `UPLOAD_FOLDER` (localmente, `./uploads`). Em um serviço Render com filesystem efêmero, arquivos gravados no disco local podem desaparecer após um novo deploy/restart. Para manter PDFs e imagens enviados pelo professor, configure um **Persistent Disk** no serviço web do Render e aponte `UPLOAD_FOLDER` para um diretório dentro do ponto de montagem, por exemplo:

```env
UPLOAD_FOLDER=/var/data/portal_jm/uploads
```

Crie/monte o disco no Render em `/var/data/portal_jm`. A aplicação cria automaticamente a pasta `uploads` se ela não existir.

Essa configuração permite manter o sistema atual sem misturar arquivos com o Neon. Se futuramente você optar por um bucket S3/R2/GCS, a camada de armazenamento pode ser substituída sem alterar as tabelas de usuários, séries, matérias e conteúdos.

## Render

O projeto já possui `Procfile`:

```text
web: gunicorn --bind 0.0.0.0:$PORT app:app
```

Configuração típica:

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn --bind 0.0.0.0:$PORT app:app`
- **Environment:** Python

Variáveis recomendadas:

```env
SECRET_KEY=...
DATABASE_URL=postgresql://...   # Neon
ADMIN_NAME=Professor JM
ADMIN_EMAIL=...
ADMIN_PASSWORD=...
UPLOAD_FOLDER=/var/data/portal_jm/uploads
SESSION_COOKIE_SECURE=true
```

Se usar Google OAuth:

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=https://SEU-DOMINIO/auth/google/callback
```

Depois do deploy, confirme que o domínio público está cadastrado no Google Cloud como URI de redirecionamento.

## Login e perfis

O cadastro público sempre cria ALUNO. A conta administrativa é garantida pelas variáveis `ADMIN_EMAIL`, `ADMIN_PASSWORD` e `ADMIN_NAME` na inicialização.

Por padrão, se você não alterar as variáveis, a conta de demonstração é:

- E-mail: `professor@portaljm.com`
- Senha: `PortalJM@2026`

**Em produção, altere essas credenciais.**

Comando opcional:

```bash
flask --app app.py create-admin
```

## Google OAuth

O login Google é opcional. Sem as variáveis OAuth, o login por e-mail e senha continua funcionando normalmente.

## PWA / Android

O site usa o mesmo backend e o mesmo banco em todas as plataformas. Não existe um segundo aplicativo independente.

Arquivos principais:

- `app/static/manifest.json`
- `app/static/service-worker.js`
- `app/static/icons/icon-192.png`
- `app/static/icons/icon-512.png`

Em Android, abra o site publicado no Chrome. Quando o navegador oferecer **Instalar app** / **Adicionar à tela inicial**, confirme. O manifest usa `display: standalone` e o service worker é registrado pelo frontend.

Para o PWA funcionar corretamente em produção, publique o site com HTTPS.

## Materiais e rotas de arquivos

Materiais enviados pelo professor são identificados no banco por `Content.file_name`. O arquivo físico fica no `UPLOAD_FOLDER`.

Rotas principais:

- `/aluno/arquivo/<id>` — abre arquivo/imagem com MIME detectado pela extensão.
- `/aluno/pdf/<id>` — abre PDF explicitamente como `application/pdf`.
- `/admin/file/<filename>` — acesso de arquivo para o professor.

Os nomes físicos dos uploads são UUIDs, reduzindo colisões entre arquivos com o mesmo nome original. O caminho é servido pelo Flask com `send_from_directory`, sem aceitar caminhos arbitrários enviados pelo usuário.

## Segurança

- Senhas armazenadas com hash.
- CSRF habilitado nos POSTs.
- Professor/aluno separados no backend.
- Cadastro público não cria administrador.
- Cookies de sessão HTTP-only e SameSite Lax.
- Em produção, `SESSION_COOKIE_SECURE=true` deve ser usado com HTTPS.
- Upload limitado a 25 MB e extensões permitidas.

## Testes

Execute:

```bash
pytest -q
```

A suíte verifica login/isolamento de perfis, séries oficiais, criação de materiais, links externos e validação de PDF. Também há verificações manuais recomendadas no ambiente publicado: login, logout, navegação mobile, abertura de PDF/imagem, painel do professor, painel do aluno e instalação do PWA.
