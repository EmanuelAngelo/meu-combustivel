# Meu Combustível

Aplicação web para controle de abastecimentos, veículos e consulta de preços de combustíveis.

O projeto foi desenvolvido com **Vue 3 + TypeScript + Tailwind CSS** no frontend e **Django REST Framework** no backend. Atualmente utiliza **SQLite** como banco de dados e também possui suporte a instalação como **PWA** em navegadores compatíveis.

## Tecnologias

### Frontend

- Vue 3
- TypeScript
- Vite
- Tailwind CSS
- Leaflet
- PWA / Service Worker

### Backend

- Python 3.12+
- Django
- Django REST Framework
- SQLite

## Funcionalidades

Atualmente o sistema possui:

- Cadastro de usuários
- Login e logout
- Sessões protegidas com cookies HttpOnly
- Proteção CSRF
- Recuperação de senha por e-mail
- Cadastro de múltiplos veículos
- Definição de veículo principal
- Registro de abastecimentos
- Histórico de abastecimentos
- Filtros de histórico
- Exportação para CSV
- Cadastro e consulta de postos
- Registro de preços por combustível e forma de pagamento
- Ranking de preços recentes
- Sistema de relatos
- Área administrativa pelo Django Admin
- Instalação como PWA
- Tratamento de indisponibilidade de conexão

Cada usuário possui acesso apenas aos próprios veículos e abastecimentos.

Os dados públicos dos postos e preços são tratados separadamente dos dados privados de cada usuário.

---

## Estrutura do projeto

O repositório contém frontend e backend no mesmo projeto.

```text
meu-combustivel/
├── backend/
├── scripts/
├── src/
├── public/
├── Dockerfile
├── compose.yaml
├── package.json
└── README.md
```

O frontend pode ser executado separadamente durante o desenvolvimento ou compilado para ser servido diretamente pelo Django.

---

## Executando localmente

### Requisitos

Antes de começar, instale:

- Python 3.12 ou superior
- Node.js 22 ou superior

Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
cd meu-combustivel
```

### Inicialização automática

O projeto possui um script que prepara todo o ambiente local.

No Windows:

```powershell
py scripts/start-local.py
```

Ou:

```powershell
python scripts/start-local.py
```

O script realiza automaticamente:

- criação do ambiente virtual Python;
- instalação das dependências do backend;
- instalação das dependências do frontend;
- build do frontend;
- aplicação das migrations;
- inicialização do servidor Django.

Depois disso, acesse:

```text
http://127.0.0.1:8000
```

> O servidor de desenvolvimento deve ser utilizado apenas localmente. Para publicação, utilize uma configuração apropriada de produção.

---

## Banco de dados

Por padrão, o projeto utiliza SQLite.

O banco fica localizado em:

```text
backend/data/db.sqlite3
```

Os dados permanecem salvos mesmo após fechar e iniciar novamente a aplicação.

Para realizar backup manual do banco, é recomendado parar a aplicação antes de copiar o arquivo.

Para ambientes com maior volume de usuários, a migração para **PostgreSQL** é recomendada.

---

## Desenvolvimento separado

Durante o desenvolvimento, frontend e backend também podem ser executados separadamente.

### Backend

Crie o ambiente virtual:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
.venv/bin/pip install -r backend/requirements.txt

DJANGO_DEBUG=true .venv/bin/python backend/manage.py migrate

DJANGO_DEBUG=true .venv/bin/python backend/manage.py runserver 127.0.0.1:8000
```

No Windows PowerShell:

```powershell
.venv\Scripts\pip.exe install -r backend\requirements.txt

$env:DJANGO_DEBUG="true"

.venv\Scripts\python.exe backend\manage.py migrate

.venv\Scripts\python.exe backend\manage.py runserver 127.0.0.1:8000
```

### Frontend

Em outro terminal:

```bash
npm ci
npm run dev:server
```

Durante o desenvolvimento, o Vite encaminha as requisições de `/api` para o Django executando localmente.

Para gerar a versão que será servida pelo backend:

```bash
npm run build:server
```

---

## Autenticação e segurança

A autenticação utiliza sessões do Django.

Os cookies de sessão são configurados como **HttpOnly** e as operações de escrita utilizam proteção CSRF.

O frontend não armazena tokens permanentes de autenticação em:

- localStorage
- IndexedDB
- cache da aplicação

As senhas são armazenadas utilizando o sistema de hashing do próprio Django.

A recuperação de senha utiliza tokens temporários de uso único.

---

## Registro de abastecimentos

Cada abastecimento pode armazenar informações como:

- veículo
- posto
- tipo de combustível
- preço por litro
- valor total
- quantidade de litros
- forma de pagamento
- quilometragem
- indicação de tanque cheio
- observações

Os cálculos financeiros são realizados no backend utilizando `Decimal`, evitando problemas comuns de precisão com números de ponto flutuante.

O servidor também realiza validações para identificar:

- volume superior à capacidade do tanque;
- divergências relevantes entre litros, preço e valor total;
- repetição da mesma requisição.

---

## Postos e preços

Os postos fazem parte de um cadastro compartilhado entre os usuários.

A aplicação possui normalização e deduplicação utilizando informações como:

- nome
- endereço
- cidade
- estado
- país

Os preços possuem identificação por:

- tipo de combustível
- forma de pagamento

Para o ranking atual, são considerados preços registrados nos últimos **7 dias**.

Registros mais antigos continuam armazenados, mas deixam de participar da comparação atual.

---

## Privacidade

Os abastecimentos são privados.

Informações como:

- usuário
- veículo
- quilometragem
- valor total
- observações pessoais

não fazem parte das informações públicas de preço dos postos.

Os dados públicos utilizados na comparação são mantidos separadamente dos dados privados de abastecimento.

---

## PWA e funcionamento offline

O Meu Combustível pode ser instalado como PWA em navegadores compatíveis.

O Service Worker armazena apenas os arquivos públicos necessários para carregar a interface.

Respostas privadas da API, credenciais e registros pessoais não são armazenados em cache offline.

Se a conexão cair enquanto a tela estiver aberta, informações ainda não enviadas podem permanecer temporariamente na memória da página.

Recarregar ou fechar a aplicação descarta formulários que ainda não tenham sido enviados ao servidor.

Para funcionamento correto da PWA em produção é necessário utilizar **HTTPS**.

---

## Recuperação de senha

Para ativar a recuperação de senha por e-mail, configure as variáveis SMTP no arquivo `.env`.

Exemplo:

```env
EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=
DEFAULT_FROM_EMAIL=
PUBLIC_APP_URL=
```

Sem configuração SMTP, o envio real de e-mails permanece desativado.

---

## Variáveis de ambiente

Copie o arquivo de exemplo:

```bash
cp .env.example .env
```

No Windows:

```powershell
Copy-Item .env.example .env
```

Preencha as configurações necessárias antes de executar o projeto em produção.

Nunca publique o arquivo `.env` no repositório.

Para gerar uma chave secreta:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

---

## Docker

O projeto possui:

```text
Dockerfile
compose.yaml
```

Para iniciar:

```bash
docker compose up --build -d
```

O SQLite é armazenado em volume persistente.

Para criar um administrador:

```bash
docker compose exec app python manage.py createsuperuser
```

Depois acesse:

```text
/admin/
```

A área administrativa pode ser utilizada para gerenciamento e moderação dos dados da aplicação.

Em produção, recomenda-se utilizar um proxy reverso com HTTPS.

A variável:

```env
TRUST_PROXY_SSL_HEADER=true
```

deve ser ativada somente quando o proxy estiver configurado corretamente para enviar `X-Forwarded-Proto`.

---

## API

As rotas da API utilizam barra final.

### Autenticação

| Método | Rota | Descrição |
| --- | --- | --- |
| GET | `/api/auth/session/` | Consulta sessão, CSRF e recursos disponíveis |
| POST | `/api/auth/register/` | Criação de conta |
| POST | `/api/auth/login/` | Login |
| POST | `/api/auth/logout/` | Logout |
| POST | `/api/auth/password-reset/` | Solicitação de recuperação de senha |
| POST | `/api/auth/password-confirm/` | Definição de nova senha |

### Recursos

| Rota | Descrição |
| --- | --- |
| `/api/vehicles/` | Veículos do usuário |
| `/api/refuelings/` | Abastecimentos |
| `/api/stations/` | Postos e consulta de preços |
| `/api/reports/` | Relatos enviados pelo usuário |

O endpoint de postos aceita filtros como:

```text
fuel
payment
```

permitindo consultar preços comparáveis pelo tipo de combustível e forma de pagamento.

---

## Testes

Frontend:

```bash
npm test
```

Build integrado ao Django:

```bash
npm run build:server
```

Backend:

Linux/macOS:

```bash
DJANGO_DEBUG=true .venv/bin/python backend/manage.py test fuel
```

Windows PowerShell:

```powershell
$env:DJANGO_DEBUG="true"
.venv\Scripts\python.exe backend\manage.py test fuel
```

Os testes do backend cobrem pontos como:

- isolamento de dados entre usuários;
- criação, alteração e exclusão de registros;
- acesso indevido a veículos de outros usuários;
- autenticação;
- CSRF;
- logout;
- validação de senha;
- recuperação de senha;
- tokens de uso único;
- cálculos financeiros com Decimal;
- validação da capacidade do tanque;
- prevenção de registros duplicados;
- deduplicação de postos;
- privacidade dos dados;
- validade dos preços;
- separação por combustível e pagamento;
- moderação de relatos.

---

## Situação atual

O projeto já possui frontend e backend integrados e pode ser executado localmente ou publicado em um servidor com suporte a Python.

Alguns recursos ainda podem ser ampliados nas próximas versões:

- integração com Google Maps / Places;
- busca avançada de cidades;
- ranking de postos por proximidade;
- cálculo de consumo em km/l;
- estimativa de combustível restante;
- anexos em relatos;
- sincronização offline;
- verificação de e-mail;
- exclusão de conta;
- política de privacidade;
- termos de uso;
- migração para PostgreSQL;
- melhorias de observabilidade e monitoramento.

Atualmente o mapa utiliza **Leaflet + OpenStreetMap** e o cadastro de localização dos postos pode ser feito manualmente.

---

## Produção

Antes de disponibilizar o sistema publicamente, é recomendado:

- desativar `DEBUG`;
- utilizar uma `SECRET_KEY` segura;
- configurar HTTPS;
- configurar corretamente `ALLOWED_HOSTS`;
- configurar `CSRF_TRUSTED_ORIGINS`;
- manter backups do banco;
- configurar SMTP;
- configurar monitoramento de erros;
- aplicar limitação de requisições no proxy;
- considerar PostgreSQL para maior volume de dados.

O SQLite é suficiente para desenvolvimento, testes e uma implantação inicial de baixo volume.

---

## Referências

- [Django](https://www.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Vue.js](https://vuejs.org/)
- [Vite](https://vite.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Leaflet](https://leafletjs.com/)
- [OpenStreetMap](https://www.openstreetmap.org/)

## Licença

Este projeto é distribuído sob a licença MIT.

Consulte o arquivo [`LICENSE`](LICENSE) para mais informações.
