# Validação da versão 0.4

## Verificações concluídas

- 30 testes Django passaram: isolamento de contas, sessões, CSRF/CORS, preços por combustível/pagamento, comparação comum/crédito, preços ausentes/iguais, validade das informações, atualização e remoção do compartilhamento e duplicidade por Place ID.
- Migrações aplicadas em SQLite temporário; `makemigrations --check --dry-run` não identificou alterações pendentes.
- Build de produção com Vue/TypeScript/Vite concluído. O modo de produção continua usando Django; demonstração somente com o comando explícito.
- Testes de cálculo do frontend passaram (`npm test`, um arquivo com quatro cenários).
- Navegador com frontend e backend reais locais: criação de conta, veículo, posto manual, abastecimento com comum/crédito, filtro por crédito, persistência de sessão após recarregar e ausência de erros JavaScript.
- Conferida diferença de R$ 0,299/L entre R$ 6,200 e R$ 6,499 no fluxo real.
- Navegador com Google Maps simulado: busca de região, consulta de postos somente ao clicar, seleção, preenchimento de nome/cidade/UF/coordenadas, salvamento e reabertura limpa do formulário.
- Layout de 390 px revisado: sem transbordamento horizontal e navegação lateral recolhida.
- Rotas com barra final preservadas no Vercel; script de configuração também mantém esse formato.

A verificação no navegador encontrou e corrigiu uma corrida no carregamento dos dados após login/cadastro: a conta agora é ativada pelo orquestrador após receber o evento do formulário. Também foi corrigida a associação do rótulo do seletor de posto, que envolvia o botão de cadastro.

## Limites da validação

Nenhum deploy foi realizado no Vercel ou PythonAnywhere. Sua chave Google não foi usada nem incluída no código. A integração visual com Maps foi exercitada com respostas simuladas, sem chamadas faturáveis. Confirme a chave, as restrições, o faturamento, o carregamento dos mapas e os resultados reais depois do deploy, seguindo `ATUALIZACAO.md`.

## Comandos

```bash
# Na raiz, com a venv e o backend/.env configurados para desenvolvimento
python backend/manage.py test fuel
python backend/manage.py makemigrations --check --dry-run
cd frontend
npm ci
npm test
npm run build
```
