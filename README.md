# Portal JM – Química

Sistema educacional em Flask com cadastro, login, sessões, separação real entre PROFESSOR e ALUNO, quatro turmas oficiais (1º, 2º, 3º e 4º ano), CRUD de séries/matérias/conteúdos, uploads, explicações, PDFs, slides, vídeo-aulas, links externos e Google OAuth opcional.

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

## Professor / administrador

Por padrão, a conta pré-definida é:

- E-mail: `professor@portaljm.com`
- Senha: `PortalJM@2026`
- Nome: `Professor JM`

As variáveis `ADMIN_EMAIL`, `ADMIN_PASSWORD` e `ADMIN_NAME` podem ser configuradas no Render para trocar as credenciais sem alterar o código. O cadastro público nunca cria administrador: contas cadastradas pela tela pública são sempre ALUNO.

O login do professor redireciona diretamente para `/admin/`. No servidor, todas as rotas `/admin/*` exigem `role=admin`, enquanto `/aluno/*` bloqueia administradores. Portanto, esconder botões no frontend não é a única proteção. O cadastro público sempre cria ALUNO.

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

## Arquivos, imagens e PDFs

Todos os arquivos enviados (imagens, PDFs, PowerPoint, Word e TXT) são servidos por uma rota do Flask com o MIME correto. O caminho do armazenamento pode ser configurado pela variável `UPLOAD_FOLDER`.

**Importante no Render:** o filesystem normal do serviço é efêmero. Se o banco continuar apontando para um arquivo que foi salvo antes de um redeploy/restart, o link pode retornar 404 porque o arquivo deixou de existir. Para uploads que precisam sobreviver a reinícios, anexe um Persistent Disk e configure `UPLOAD_FOLDER` para um diretório dentro do disco, por exemplo `/var/data/uploads`. O Render documenta que somente os dados escritos dentro do mount path do disco são preservados entre deploys e reinícios.

Se estiver usando um serviço gratuito sem Persistent Disk, os uploads locais não devem ser tratados como armazenamento permanente; nesse caso, use um armazenamento de objetos externo para os materiais.

## Render

Build: `pip install -r requirements.txt`  
Start: `gunicorn --bind 0.0.0.0:$PORT app:app`

O `Procfile` já está configurado com esse comando.

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

Cada fonte também tem um campo **Tipo de material**:
- Meu dispositivo → Arquivo ou PDF (PDF exige que o arquivo enviado seja realmente `.pdf`).
- Google Drive / Outro lugar → Link externo, Slides ou Vídeo.
- Escrever aqui → sempre Explicação.

A remoção de materiais permanece disponível no backend, mas foi retirada da interface desta etapa para ser trabalhada depois.


## Acesso de demonstração
Por padrão, o sistema usa `professor@portaljm.com` / `PortalJM@2026` como administrador. Em produção, recomenda-se alterar essas variáveis no Render.


## Quatro anos e compatibilidade com dados existentes

O banco continua usando a tabela `series`; 1º, 2º, 3º e 4º ano são registros reais relacionados a `subjects` e `contents`. Na inicialização, nomes legados como `1ª Série`/`4ª Série` são migrados para `1º ano`/`4º ano` sem apagar os IDs, matérias ou materiais existentes. Nenhuma tabela é recriada ou apagada.

## Testes

A suíte em `tests/test_app.py` cobre isolamento professor/aluno, redirecionamento do login, quatro séries, criação de material no 4º ano, link externo e validação/upload de PDF.
