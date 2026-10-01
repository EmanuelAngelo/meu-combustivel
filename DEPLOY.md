# Publicar no PythonAnywhere e no Vercel

Substitua `SEU-USUARIO` e `SEU-PROJETO` pelos nomes reais. Não publique com esses exemplos. Se já tem banco de produção, preserve `backend/data/db.sqlite3`, `backend/.env` e sua chave secreta existente.

## 1. Backend no PythonAnywhere

Envie o código ou clone seu repositório em `/home/SEU-USUARIO/meu-combustivel`.

Na console Bash, ative sua venv existente ou crie uma usando a mesma versão de Python escolhida na aba Web. Exemplo com Python 3.13, se disponível na sua conta:

```bash
cd ~/meu-combustivel
python3.13 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.production.example backend/.env
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Copie a chave gerada para `DJANGO_SECRET_KEY` em `backend/.env`. Não compartilhe essa chave. Na atualização de uma instalação existente, mantenha a chave atual e não execute o `cp` sobre seu arquivo.

Configure:

```dotenv
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=SUA-CHAVE-PRIVADA
DJANGO_ALLOWED_HOSTS=SEU-USUARIO.pythonanywhere.com
DJANGO_CORS_ALLOWED_ORIGINS=https://SEU-PROJETO.vercel.app
DJANGO_CSRF_TRUSTED_ORIGINS=https://SEU-PROJETO.vercel.app
PUBLIC_APP_URL=https://SEU-PROJETO.vercel.app
DJANGO_COOKIE_SAMESITE=Lax
DJANGO_SERVE_FRONTEND=false
TRUST_PROXY_SSL_HEADER=true
```

Use o domínio completo que a aba Web mostrar, inclusive se sua conta tiver um sufixo regional diferente. `ALLOWED_HOSTS` leva apenas hosts; CORS e CSRF levam origem completa, sem caminho ou barra final. Múltiplas origens são separadas por vírgula.

O carregamento de `backend/.env` foi incluído no Django. Ele funciona para `migrate` e WSGI, sem precisar repetir `export` na console. Variáveis já exportadas prevalecem: remova definições antigas conflitantes, como `DJANGO_DEBUG=true`.

```bash
chmod 600 backend/.env
python backend/manage.py migrate
python backend/manage.py collectstatic --noinput
python backend/manage.py createsuperuser
python backend/manage.py check --deploy
```

Na aba **Web**, escolha **Manual configuration** e a mesma versão Python da venv. Configure:

- Source code e Working directory: `/home/SEU-USUARIO/meu-combustivel/backend`
- Virtualenv: `/home/SEU-USUARIO/meu-combustivel/venv`
- Arquivos estáticos: URL `/static/`, diretório `/home/SEU-USUARIO/meu-combustivel/backend/staticfiles`

Abra o arquivo WSGI pelo link da aba **Web** e use o conteúdo de `deploy/pythonanywhere_wsgi.py`, ajustando o usuário e o caminho. Não basta editar apenas `backend/config/wsgi.py`.

Clique em **Reload**. Não use `runserver` para manter a aplicação pública.

Abra `https://SEU-USUARIO.pythonanywhere.com/`: deve retornar JSON identificando a API. `https://SEU-USUARIO.pythonanywhere.com/api/auth/session/` deve retornar JSON com `user: null` quando não autenticado. `/admin/` é acessado diretamente pelo domínio do PythonAnywhere.

## 2. Frontend no Vercel

Na raiz do projeto, em seu computador:

```bash
npm run configure:vercel -- https://SEU-USUARIO.pythonanywhere.com
```

Isso grava o destino real de `/api/:path*` em `vercel.json`. Envie esse arquivo e as alterações ao seu repositório. O Vercel lê as regras antes de executar o build, portanto configure o arquivo **antes** do deploy.

Importe o repositório no Vercel:

| Configuração | Valor |
| --- | --- |
| Root Directory | Raiz, onde está `package.json` |
| Framework Preset | Vite |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Node.js | 22 ou superior |
| `VITE_API_BASE_URL` | `/api` (ou deixe ausente) |

Não use `npm run build:demo`. Não copie variáveis do backend para o Vercel. Remova uma eventual `VITE_API_BASE_URL` antiga apontando diretamente ao PythonAnywhere para usar a configuração recomendada.

Após obter a URL final do Vercel, atualize no PythonAnywhere `DJANGO_CORS_ALLOWED_ORIGINS`, `DJANGO_CSRF_TRUSTED_ORIGINS` e `PUBLIC_APP_URL`, depois clique em **Reload**. Um domínio personalizado também precisa estar explicitamente autorizado.

Deploys de preview têm outras URLs: autorize apenas o preview específico que você realmente precisa testar, ou use um backend de testes separado. Não libere todos os projetos `*.vercel.app`.

## 3. Como a autenticação funciona

O navegador chama `https://SEU-PROJETO.vercel.app/api/...`. O Vercel encaminha a requisição para `https://SEU-USUARIO.pythonanywhere.com/api/...`. O Django continua responsável pela sessão e pelo banco.

Cookies não recebem um `Domain` fixo: ficam associados ao domínio pelo qual o navegador acessa a API. Em produção são Secure, HttpOnly e SameSite=Lax. O token CSRF é recebido no JSON de sessão e renovado após login; as escritas enviam `X-CSRFToken`.

CSRF permanece obrigatório mesmo para origens permitidas. A API retorna `Cache-Control: private, no-store`, e `vercel.json` também impede cache na CDN para `/api`. O service worker não armazena respostas da API.

CORS e CSRF são mecanismos distintos. A lista CORS permite que o navegador leia respostas em chamadas diretas autorizadas; ela não substitui autenticação, permissões nem validação CSRF.

### Chamada direta entre origens, opcional

O cliente suporta `VITE_API_BASE_URL=https://SEU-USUARIO.pythonanywhere.com/api` com `credentials: include`. Para domínios não relacionados seria necessário `DJANGO_COOKIE_SAMESITE=None` e HTTPS, além das listas CORS/CSRF. Mesmo assim, bloqueios de cookies de terceiros podem impedir o login. Por isso a configuração entregue usa o proxy `/api`; não mude apenas a URL do frontend esperando que CORS resolva tudo.

## 4. Validação depois de publicar

1. Acesse o domínio do Vercel: deve abrir login/cadastro, sem dados fictícios.
2. Crie uma conta e um veículo. Recarregue a página e confira a sessão e os dados.
3. Registre um abastecimento, saia da conta e entre novamente.
4. Use outra conta para confirmar que não vê seus veículos e abastecimentos.
5. Confira em Network que as requisições usam `/api/` no domínio do Vercel e que as respostas não vêm do cache.
6. Se configurar SMTP, teste a recuperação de senha. O link deve abrir o Vercel.

Os testes locais não substituem essa validação nos domínios reais.

## Diagnóstico

| Sintoma | Verifique |
| --- | --- |
| Interface demonstrativa | Build deve ser `npm run build`. Publique novamente e feche todas as abas/PWA antigas para ativar o service worker atualizado. Se persistir, limpe os dados desse site. |
| Falha de conexão ou HTML no lugar de JSON | Destino real em `vercel.json`, backend ativo e `VITE_API_BASE_URL=/api`. |
| `403 CSRF` | Origem exata do Vercel em `DJANGO_CSRF_TRUSTED_ORIGINS`, Reload no PythonAnywhere e cookies habilitados. |
| `DisallowedHost` | Host do PythonAnywhere em `DJANGO_ALLOWED_HOSTS`. Não resolva com `*`. |
| Redirecionamento HTTPS repetido | `TRUST_PROXY_SSL_HEADER=true` no PythonAnywhere. Use essa opção somente atrás de proxy confiável. |
| Login funciona, mas desaparece | Não misture acesso direto ao backend com proxy no mesmo fluxo. Confira os cookies e a base `/api`. |
| Erro de chave no `migrate` | `backend/.env` precisa existir e conter `DJANGO_SECRET_KEY` em produção. |
| CSS do Admin ausente | `collectstatic` e mapeamento de `/static/`. |

## Referências

- https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/
- https://vercel.com/docs/routing/rewrites
- https://github.com/adamchainz/django-cors-headers
