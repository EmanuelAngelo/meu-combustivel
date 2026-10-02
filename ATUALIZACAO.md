# Atualização para a versão 0.4

## O que mudou

- Frontend movido para `frontend/` e separado em views, forms, exibição, mapas, serviços, tipos e utilitários.
- Cadastro de posto com Google Maps: buscar região, mover o mapa, buscar postos na área e selecionar para preencher nome, endereço, cidade, UF e coordenadas. Cadastro manual continua disponível.
- Deduplicação pelo Place ID usando `external_id`, incluindo cadastros manuais idênticos.
- Comparação de preço comum (Pix, dinheiro ou débito) e crédito; valor ausente é desconhecido, não igual ao comum. Valores e diferenças usam três casas decimais por litro.
- Filtros por combustível e pagamento no ranking; informações com datas diferentes são sinalizadas.
- Preços adicionais opcionais no abastecimento, publicados somente se o compartilhamento estiver marcado.

## 1. Atualizar o repositório

O ZIP contém a estrutura completa, sem `venv`, `node_modules`, `.git`, banco, `.env` real ou chave Google.

Preserve `backend/.env`, `backend/data/db.sqlite3` e sua pasta `.git`. Atualize o código na cópia de trabalho do repositório e remova os arquivos antigos do frontend na raiz que agora estão em `frontend/`: `src`, `public`, `package.json`, `package-lock.json`, `index.html`, `tsconfig.json`, `vite.config.ts`, `vercel.json`, `.env.demo`, `.env.django` e o antigo `scripts/configure-vercel.mjs`. Não remova `backend`, `deploy` ou `scripts/start-local.py`. Se possuía `.env.local` para o frontend, mova-o para `frontend/.env.local`.

Confira `git status` e envie as mudanças. Não publique a venv, banco ou arquivos `.env` reais.

## 2. Backend no PythonAnywhere

Faça backup consistente do SQLite, usando o caminho real se você personalizou `SQLITE_PATH`:

```bash
cd ~/meu-combustivel
source venv/bin/activate
python - <<'PY'
import sqlite3
from datetime import datetime
from pathlib import Path
source = Path('backend/data/db.sqlite3')
if not source.exists():
    raise SystemExit('Confira o caminho do banco antes de continuar.')
backup = source.with_name('db-backup-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.sqlite3')
with sqlite3.connect(source) as current, sqlite3.connect(backup) as target:
    current.backup(target)
print('Backup criado:', backup)
PY
git pull origin master
python -m pip install -r backend/requirements.txt
python backend/manage.py migrate
python backend/manage.py collectstatic --noinput
```

A migração `0002` preserva os registros e permite mais de uma observação de pagamento por abastecimento. Não apague o banco nem execute `makemigrations` em produção. Depois, use **Web → Reload**. Mantenha a chave Django e as configurações de CORS/CSRF já funcionando.

## 3. Frontend no Vercel

Em **Settings → Build and Deployment**, configure:

| Configuração | Valor |
| --- | --- |
| Root Directory | `frontend` |
| Framework | Vite |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

Em **Environment Variables**:

```dotenv
VITE_API_BASE_URL=/api
VITE_GOOGLE_MAPS_API_KEY=SUA_CHAVE_GOOGLE
VITE_GOOGLE_MAPS_MAP_ID=DEMO_MAP_ID
```

`DEMO_MAP_ID` permite testar marcadores avançados; para produção, substitua por seu Map ID JavaScript criado no Google Cloud. Um Map ID não é a chave da API. As variáveis `VITE_*` são públicas no navegador. Restrinja a chave por sites e APIs. Faça um novo deploy depois de mudar variáveis, pois o Vite as incorpora durante o build.

A rota funcional permanece em `frontend/vercel.json`:

```json
{"source":"/api/:path*/","destination":"https://emanuelangelo1992.pythonanywhere.com/api/:path*/"}
```

## 4. Chave Google

Sua captura mostra Maps JavaScript API e Places API (New) selecionadas. Na mesma tela, troque **Restrições do aplicativo → Nenhum** por **Sites**, adicionando os sites que realmente usar:

```text
https://meu-combustivel-ochre.vercel.app/*
http://localhost:4173/*
http://127.0.0.1:4173/*
```

Restrinja as APIs à **Maps JavaScript API** e **Places API (New)**. A busca de região usa Places Text Search; não exige Geocoding API. Confira o faturamento ativo e acompanhe cotas/uso no Google Cloud. A captura não permite confirmar faturamento nem se alterações pendentes foram salvas.

Os mapas carregam sob demanda; buscas só ocorrem ao clicar, sem consultar novamente a cada movimento. Cada busca na área retorna até 20 postos num raio de até 50 km baseado na área visível. Não é uma lista completa de todos os postos. Preços de combustível são da comunidade: não vêm do Google.

Dados das buscas não ficam no service worker ou localStorage; resultados aparecem sobre Google Maps. O formulário permite revisar as informações antes de salvar. O Place ID pode ser mantido como referência. Antes de disponibilizar o recurso amplamente, adeque termos/privacidade do aplicativo e o uso/armazenamento de conteúdo às condições Google Maps Platform; a permissão de armazenamento de Place ID não se estende automaticamente a todos os outros campos.

Referências: https://developers.google.com/maps/documentation/javascript/nearby-search e https://developers.google.com/maps/documentation/javascript/policies

## 5. Testar após publicar

1. `/api/auth/session/` no Vercel deve continuar retornando JSON.
2. Entre na conta, abra Cadastrar posto, encontre uma região e clique em Buscar postos nesta área.
3. Selecione um posto e confira os campos antes de salvar. Selecioná-lo novamente deve reutilizar o cadastro.
4. Registre um abastecimento Pix de R$ 6,200/L e informe crédito de R$ 6,499/L. Com compartilhamento habilitado, a comparação deve mostrar R$ 0,299/L a mais no crédito.
5. Confira outro combustível e outros pagamentos: valores não informados devem permanecer desconhecidos.
6. Feche e reabra as abas/PWA antigas para ativar a nova versão do service worker.

O teste de Google com sua chave e o faturamento deve ser concluído no domínio autorizado após o deploy; a chave não foi incluída neste pacote.
