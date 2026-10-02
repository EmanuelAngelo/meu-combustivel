# Meu Combustível

Aplicação para controlar veículos e abastecimentos, conferir os valores da bomba e consultar preços de postos.

Vue 3, TypeScript e Tailwind CSS no frontend. Django REST Framework e SQLite no backend. Interface em português, responsiva e instalável como PWA.

**Atualizando a versão já publicada? Siga [ATUALIZACAO.md](ATUALIZACAO.md): o Root Directory do Vercel agora é `frontend`.**

## Executar no computador

Requisitos: Python 3.12 ou 3.13 e Node.js 22 ou superior.

Na raiz do projeto, usando PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
Copy-Item backend/.env.example backend/.env
python backend/manage.py migrate
python backend/manage.py runserver
```

Se já possui `backend/.env`, ajuste-o sem sobrescrever suas configurações. O Django agora lê esse arquivo automaticamente, tanto no terminal quanto no WSGI. Variáveis já definidas no ambiente têm prioridade.

Em outro terminal, na pasta `frontend/`:

```powershell
cd frontend
npm ci
npm run dev
```

Acesse **http://localhost:4173**. O backend fica em **http://127.0.0.1:8000**. O Vite encaminha `/api` para o Django; são processos separados.

A aplicação abre na tela de login/cadastro. Se a API estiver indisponível, apresenta um erro de conexão; não substitui seus dados por exemplos.

Também é possível iniciar os dois processos com `python scripts/start-local.py`, que prepara o ambiente e executa as migrações. O script força o modo de desenvolvimento e deve ser usado apenas no computador.

## Publicação

- **Backend:** PythonAnywhere, com WSGI.
- **Frontend:** Vercel, com `npm run build` e saída `dist`.
- **API:** o Vercel encaminha `/api/*` para o PythonAnywhere via `vercel.json`.

O código Python e o banco permanecem no PythonAnywhere; o Vercel entrega a interface e encaminha as requisições. O navegador usa a mesma origem para interface e API, preservando os cookies de sessão sem depender de cookies de terceiros.

Siga **[DEPLOY.md](DEPLOY.md)** para configurar os dois serviços. Antes de publicar, informe o domínio do backend:

```bash
cd frontend
npm run configure:vercel -- https://SEU-USUARIO.pythonanywhere.com
```

Envie o `vercel.json` atualizado ao repositório antes do deploy. Preencha também `backend/.env` com a chave secreta e o domínio real do frontend.

## Comandos do frontend

| Comando | Resultado |
| --- | --- |
| `npm run dev` | Aplicação real na porta 4173 |
| `npm run build` | Build da aplicação real em `dist` |
| `npm run dev:demo` | Demonstração com dados fictícios na porta 4174 |
| `npm run build:demo` | Build demonstrativo; não usar no Vercel de produção |
| `npm run dev:server` | Alias compatível para desenvolvimento real |
| `npm run build:server` | Build real, compatível com a hospedagem antiga |
| `npm test` | Testes de cálculo |

O modo demonstrativo só é ativado por `--mode demo`. Um `.env.local` antigo com `VITE_API_MODE=demo` não muda o comportamento de `npm run dev` ou `npm run build`.

## Configurações

Frontend: `frontend/.env.local` opcional, baseado em `frontend/.env.example`. Backend: `backend/.env`, baseado em `backend/.env.example` para desenvolvimento ou `backend/.env.production.example` para produção.

| Variável | Finalidade |
| --- | --- |
| `VITE_API_BASE_URL` | Base da API; padrão `/api`, recomendado com os proxies |
| `DEV_API_TARGET` | Destino local do proxy Vite; padrão `http://127.0.0.1:8000` |
| `DJANGO_SECRET_KEY` | Chave privada do Django, obrigatória em produção |
| `DJANGO_DEBUG` | `true` apenas no desenvolvimento |
| `DJANGO_ALLOWED_HOSTS` | Hosts aceitos pelo backend, separados por vírgula, sem protocolo |
| `DJANGO_CORS_ALLOWED_ORIGINS` | Origens exatas autorizadas, com protocolo e sem barra final |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Origens confiáveis para operações de escrita |
| `PUBLIC_APP_URL` | Endereço do frontend para recuperação de senha |
| `DJANGO_COOKIE_SAMESITE` | `Lax` com o proxy recomendado |
| `TRUST_PROXY_SSL_HEADER` | Ativa reconhecimento de HTTPS atrás do proxy da hospedagem |
| `DJANGO_SERVE_FRONTEND` | `false` por padrão; `true` para a hospedagem antiga no Django |

Nunca coloque segredos em variáveis `VITE_*`: seus valores entram no JavaScript público. Os arquivos `.env` reais e o banco não devem ir para o repositório.

## Funcionalidades e privacidade

- Cadastro, login, logout e recuperação de senha com SMTP configurado.
- Vários veículos por conta, capacidade do tanque e veículo principal.
- Abastecimentos com preço anunciado, total pago, litros e conferência de valores.
- Histórico, filtros e exportação CSV.
- Cadastro compartilhado de postos e preços por combustível e pagamento.
- Ranking de preços recentes, relatos para moderação e Django Admin.
- Estrutura PWA com cache dos arquivos públicos da interface.

Cada conta acessa somente seus veículos, abastecimentos e relatos. Os preços públicos ficam separados do histórico privado. A autenticação usa cookies HttpOnly e proteção CSRF; tokens permanentes não são armazenados em localStorage. CORS usa uma lista explícita de origens, não `*`.

A conferência financeira usa Decimal no backend e não comprova qualidade do combustível nem volume realmente entregue. Preços com mais de sete dias saem do ranking atual. Os relatos não comprovam adulteração.

O cadastro de postos permite Google Maps/Places com seleção no mapa e preenchimento dos dados, além do modo manual. A duplicidade é verificada por Place ID e campos normalizados. Recuperação de senha depende de SMTP. O modo offline não sincroniza novos abastecimentos: formulários não enviados permanecem apenas na memória da página.

## Banco e atualização

SQLite em `backend/data/db.sqlite3`. Preserve esse arquivo e `backend/.env` ao atualizar um projeto existente. Faça backup antes de aplicar alterações. O pacote não inclui banco com dados pessoais.

A migração `0002` adiciona preços opcionais comum/crédito e permite múltiplas observações por abastecimento. Aplique com `migrate`, preservando o banco existente.

## Testes

Com o ambiente virtual ativo e `backend/.env` configurado para desenvolvimento:

```bash
python backend/manage.py test fuel
cd frontend
npm test
npm run build
```

A suíte verifica isolamento dos dados, cálculos, CSRF, sessão, CORS permitido e negado, cookies de produção e respostas sem cache da API.

## Estrutura

| Caminho | Conteúdo |
| --- | --- |
| `backend/` | API Django, modelos, migrações e testes |
| `frontend/` | Aplicação Vue, package.json, Vite e vercel.json |
| `frontend/src/components/forms/` | Formulários |
| `frontend/src/components/exibicao/` | Resumos, detalhes e preços |
| `frontend/src/components/mapas/` | Mapas e seleção Google |
| `frontend/src/views/` | Telas |
| `frontend/src/composables/` | Estado e ações |
| `frontend/src/services/` | HTTP, Google Maps e PWA |
| `frontend/src/types/` e `utils/` | Contratos e cálculos |
| `scripts/` e `deploy/` | Inicialização local e WSGI |

Veja [ARQUITETURA.md](ARQUITETURA.md) e [ATUALIZACAO.md](ATUALIZACAO.md).

O Docker mantém o modo conjunto como opção: usa `backend/.env` e ativa `DJANGO_SERVE_FRONTEND=true`. A configuração principal desta versão é frontend e backend separados.
