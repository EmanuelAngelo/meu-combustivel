# Meu Combustível · v0.2

Aplicação de abastecimentos com **Vue 3 + TypeScript + Tailwind CSS**, **Django REST Framework** e **SQLite**. Interface em português, responsiva, verde-petróleo, com instalação PWA em navegadores compatíveis.

## Estado da entrega

O código contém frontend e backend conectados. A versão publicada no link de avaliação continua em **modo de demonstração**, pois a hospedagem da prévia não executa Django. Para contas reais e persistência, execute o pacote localmente ou hospede a aplicação em um servidor Python, usando as instruções abaixo.

A versão real inicia sem contas, veículos, postos ou dados fictícios. Cada usuário deve criar sua conta e seus primeiros registros.

## Começar no computador

Instale **Python 3.12+** e **Node.js 22+**. Extraia o projeto, abra um terminal nessa pasta e execute:

```sh
python scripts/start-local.py
```

No Windows, também pode usar:

```powershell
py scripts/start-local.py
```

O iniciador cria o ambiente Python, instala as versões fixadas das dependências, compila o frontend no modo Django, aplica as migrações e abre o servidor em **http://127.0.0.1:8000**. Ele escuta somente no próprio computador e usa DEBUG para desenvolvimento. Não exponha esse servidor diretamente à internet.

O banco persistente fica em `backend/data/db.sqlite3`. Fechar e reabrir o aplicativo preserva os dados. A pasta deve ter permissão de escrita. Para backup local, pare o servidor antes de copiar o arquivo; em produção, use backup consistente do SQLite.

## Implementado

- Cadastro com e-mail, login, logout e sessões protegidas por cookie HttpOnly.
- CSRF também nos endpoints de login e cadastro; senhas protegidas pelo mecanismo do Django.
- Recuperação de senha por e-mail, ativada quando SMTP estiver configurado; tokens expiram em uma hora e não podem ser reutilizados.
- Vários veículos, capacidade do tanque e um veículo principal por conta.
- Abastecimentos privados com preço anunciado, total pago, litros, combustível, pagamento, quilometragem, tanque cheio e observação.
- Conferência no servidor usando Decimal, com arredondamento em centavos. Volume acima do tanque ou divergência relevante requer confirmação.
- Proteção contra duplicação na repetição de uma requisição de abastecimento.
- Cadastro compartilhado de postos com validação de coordenadas e deduplicação normalizada por nome, endereço, cidade, estado e país.
- Observações públicas de preço separadas do registro privado, sem expor usuário, veículo, total, quilometragem ou observação pessoal.
- API de preços por combustível e condição de pagamento, com validade de 7 dias. Preços antigos não entram no ranking atual.
- Histórico com filtros e exportação CSV; a exportação neutraliza células com prefixos de fórmula.
- Relatos privados pendentes, sem aprovação automática; moderação pelo administrador Django.
- Manifesto, ícones PWA, instalação quando suportada, service worker e aviso de falta de conexão.
- Estado de carregamento e erro; falha na API nunca aciona demonstração silenciosamente.

## PWA e privacidade offline

A PWA armazena somente arquivos públicos da interface. **Não armazena respostas da API, credenciais ou registros pessoais em cache, localStorage ou IndexedDB.** Com a tela aberta, os campos permanecem na memória durante uma interrupção de rede; salvar exige reconexão. Fechar/recarregar descarta formulários não enviados. Uma inicialização totalmente offline mostra o estado de conexão indisponível, sem recuperar o histórico privado.

HTTPS é necessário em produção. A instalação e o comportamento visual variam por navegador; não houve validação em aparelhos reais nesta entrega.

## Desenvolvimento separado

Backend (Linux/macOS; no Windows use `.venv\\Scripts\\python.exe` e defina `$env:DJANGO_DEBUG="true"` no PowerShell):

```sh
python -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
DJANGO_DEBUG=true .venv/bin/python backend/manage.py migrate
DJANGO_DEBUG=true .venv/bin/python backend/manage.py runserver 127.0.0.1:8000
```

Frontend, em outro terminal:

```sh
npm ci
npm run dev:server
```

O Vite encaminha `/api` ao Django local. Para a experiência completa em uma origem, `npm run build:server` e acesse o Django diretamente. `npm run dev` e `npm run build` mantêm o modo demonstração usado no link de avaliação. Não compile a versão pública real com esse modo.

## Hospedagem com Docker

Incluídos `Dockerfile` de múltiplos estágios e `compose.yaml`. A imagem usa um usuário sem privilégios. O SQLite fica em volume persistente. A definição de container foi preparada, mas o build Docker não foi executado neste ambiente.

1. Copie `.env.example` para `.env` e preencha domínio, origens confiáveis e uma chave secreta forte. Não envie o `.env` para Git.
2. Para gerar uma chave localmente: `python -c "import secrets; print(secrets.token_urlsafe(64))"`.
3. Configure um proxy reverso com HTTPS para a porta local 8000. Ative `TRUST_PROXY_SSL_HEADER=true` somente se o proxy sobrescrever, de forma confiável, `X-Forwarded-Proto`.
4. Execute `docker compose up --build -d`.
5. Crie o administrador com `docker compose exec app python manage.py createsuperuser`.
6. Acesse `/admin/` para revisar postos e moderar relatos.

A configuração mantém um único processo de aplicação, adequado à etapa inicial com SQLite. Antes de crescimento público, migrar para PostgreSQL e configurar limitação de requisições no proxy/armazenamento compartilhado, backups monitorados, e-mail e observabilidade. O limitador DRF desta entrega usa cache em memória por processo.

### E-mail

Preencha `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL` e `PUBLIC_APP_URL`. Sem SMTP, a recuperação não é anunciada como disponível. Nenhum e-mail real foi enviado durante os testes.

## API

Todas as rotas têm barra final. Cookies de sessão e o token CSRF retornado em `/api/auth/session/` são necessários para mutações. Não há tokens de autenticação persistidos no navegador.

| Rota | Uso |
| --- | --- |
| `GET /api/auth/session/` | Sessão, token CSRF e disponibilidade de recuperação |
| `POST /api/auth/register/` | Criar conta |
| `POST /api/auth/login/` | Entrar |
| `POST /api/auth/logout/` | Sair |
| `POST /api/auth/password-reset/` | Solicitar recuperação |
| `POST /api/auth/password-confirm/` | Definir nova senha com token |
| `/api/vehicles/` | Cadastro e manutenção dos veículos do usuário |
| `/api/refuelings/` | Registros do usuário; `client_id` evita repetição |
| `/api/stations/` | Leitura compartilhada e cadastro autenticado |
| `/api/reports/` | Criar e listar os próprios relatos |

O filtro `fuel` + `payment` em `/api/stations/` seleciona os preços comparáveis. A interface atual apresenta o ranking de gasolina comum / Pix. Os demais tipos são armazenados corretamente e têm consulta pela API; ampliar os seletores da interface é uma evolução prevista.

## Limites e próximas etapas

- **Django ainda não está hospedado**: depende de um servidor Python/domínio. O link de demonstração não oferece contas reais.
- Google Maps/Places ainda não conectado: a interface usa Leaflet/OpenStreetMap e cadastro manual com coordenadas. A próxima integração exige configuração de projeto/chaves, limites de consumo e adequação às políticas de armazenamento/atribuição. Não há chave embutida no código.
- Deduplicação manual exata está implementada; revisão de semelhança/proximidade e integração pelo identificador Google ainda são futuras.
- O cadastro atual aceita Brasil; moeda BRL e unidade litro. Internacionalização completa ainda não está implementada.
- O seletor de região filtra São Luís, Maranhão ou Brasil; busca genérica de cidades e ranking por proximidade ainda serão ampliados.
- Relatos são moderados no admin; a leitura pública dos relatos aprovados, evidências e contestações ainda precisa de implementação.
- Não há cálculo de consumo km/l, combustível restante, anexos ou sincronização offline de registros nesta versão.
- Termos, política de privacidade, verificação de e-mail e fluxo de exclusão da conta precisam ser concluídos antes do lançamento público.
- O administrador de infraestrutura tem acesso técnico ao banco; “privado” significa isolamento entre usuários da aplicação, não criptografia de ponta a ponta.

## Testes e validação

```sh
npm test
npm run build:server
DJANGO_DEBUG=true .venv/bin/python backend/manage.py test fuel
```

A suíte cobre isolamento entre contas, leitura/edição/exclusão por ID, vínculo de veículo alheio, CSRF no login, logout, validação de senha, recuperação com token de uso único, precisão Decimal, divergência, volume, repetição de requisição, deduplicação de posto, privacidade da projeção pública, validade do preço, separação por combustível/pagamento, moderação e entrega dos arquivos PWA.

Não houve automação visual de navegador nem teste de instalação em dispositivos nesta entrega. A ferramenta WebMCP opcional de conferência segue protegida por detecção de suporte; não foi validada em contexto WebMCP real.

## Referências técnicas

- [Autenticação no Django REST Framework](https://www.django-rest-framework.org/api-guide/authentication/)
- [CSRF com aplicações JavaScript](https://www.django-rest-framework.org/topics/ajax-csrf-cors/)
- [Políticas do Google Places para a integração futura](https://developers.google.com/maps/documentation/places/web-service/policies)
