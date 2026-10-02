# Arquitetura do Meu Combustível

O repositório contém duas aplicações independentes: `frontend/` (Vue 3 + TypeScript + Vite) e `backend/` (Django REST Framework). O frontend conhece a API por `/api`; modelos, permissões, persistência e regras financeiras pertencem ao backend.

## Frontend

| Pasta | Responsabilidade |
| --- | --- |
| `src/views/` | Composição das telas: visão geral, abastecimento, histórico, veículos e postos |
| `src/components/forms/` | Formulários `AbastecimentoForms`, `VeiculoForms`, `PostoForms`, `PrecosForms`, `RelatoForms` e autenticação |
| `src/components/exibicao/` | Detalhes, resumo da bomba e comparação de preços, sem acesso direto à API |
| `src/components/mapas/` | Busca/seleção de postos e mapa de exploração |
| `src/composables/` | Estado reativo, ações e ciclo de vida da aplicação |
| `src/services/` | Cliente HTTP com sessão/CSRF, carregamento Google Maps e PWA |
| `src/types/` | Contratos TypeScript de veículos, postos e abastecimentos |
| `src/utils/` | Cálculos puros, normalização e testes |
| `src/assets/` | Estilos da interface |
| `public/` | Manifesto, ícones e service worker |

`App.vue` compõe a estrutura, navegação e modais. `useApplication` cria o estado por instância de aplicação e orquestra as ações. `useStationForm` e `useVehicleForm` concentram as ações dos respectivos cadastros. `appContext` expõe esse estado por `provide/inject` com `InjectionKey` tipada, sem singleton com dados de usuários. As telas e formulários de negócio usam esse contexto; componentes reutilizáveis como `PrecosForms`, `PrecosExibicao` e os mapas usam props, modelos e eventos explícitos.

Regras de organização:

- Nova tela em `views/NomeView.vue`; novo formulário em `components/forms/NomeForms.vue`; exibição em `components/exibicao/NomeExibicao.vue`.
- Chamadas HTTP devem passar por `services/api.ts`; não duplicar lógica de CSRF em componentes.
- Integração com fornecedores fica em `services/`; o mapa só emite a seleção para o formulário.
- Cálculos puros ficam em `utils/`; validações definitivas permanecem no backend.
- Novos domínios podem ganhar composables próprios, evitando ampliar indefinidamente o orquestrador.
- Execute `npm run format` em `frontend/` para manter a formatação.

## Backend

`config/` contém configuração e roteamento; `fuel/models.py` define persistência; `serializers.py` valida entradas; `views.py` aplica permissões e coordena operações; `migrations/` versiona o esquema. Os testes cobrem isolamento entre contas, sessão, CORS/CSRF e projeção pública de preços.

Um abastecimento continua privado. Se autorizado por `share`, gera observações públicas por forma de pagamento. A unicidade `(source, payment)` impede duplicação; editar ou remover compartilhamento atualiza/remove todas as observações correspondentes. Comparações usam o mesmo combustível e a janela de atualização existente (7 dias), com data independente para cada pagamento. Não presumimos que Pix, dinheiro e débito tenham o mesmo preço.

O campo existente `Station.external_id` guarda o Place ID para evitar duplicidades na seleção Google. Cadastros manuais continuam usando a impressão dos campos normalizados. O backend não armazena chave Google nem respostas brutas de busca.

## Deploy

Vercel: diretório raiz `frontend`, saída `dist`, proxy da API em `frontend/vercel.json`.
PythonAnywhere: continua em `backend`, com banco e variáveis existentes.

O modo combinado opcional do Docker foi ajustado para `frontend/dist`; ele não muda o modelo de publicação separado.
