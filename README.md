# Portal JM – Química

Protótipo educacional em Flask para demonstração de um portal de Química.

## Acesso de demonstração

- E-mail: `professor@portaljm.com`
- Senha: `PortalJM@2026`
- Perfil: Professor / Administrador

A conta é criada/atualizada automaticamente na inicialização do aplicativo. As variáveis `ADMIN_EMAIL`, `ADMIN_PASSWORD` e `ADMIN_NAME` também podem ser usadas para sobrescrever os dados.

## Conteúdo inicial

O sistema cria exemplos para a 1ª Série, 2ª Série, 3ª Série e 4º Ano. O professor pode adicionar, editar e excluir séries, matérias e conteúdos pelo painel administrativo.

## Executar localmente

```bash
pip install -r requirements.txt
python app.py
```

O projeto também possui `Procfile`/`wsgi.py` para deploy com Gunicorn.
