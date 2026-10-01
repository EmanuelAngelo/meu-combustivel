# Validação da versão 0.3

- 24 testes do backend passaram, incluindo isolamento de contas, CORS permitido/negado, CSRF obrigatório, renovação da sessão e logout.
- 4 testes de cálculo passaram.
- Build Vue/TypeScript concluído.
- Verificado modo real em development, production e django; demo somente no modo explícito demo.
- Integração HTTP com Vite e Django em processos separados: obtenção de CSRF, cadastro, criação e leitura de veículo, restauração de sessão e logout passaram.

Não houve publicação ou teste nos serviços Vercel/PythonAnywhere. O destino da API e os domínios permitidos precisam ser preenchidos conforme DEPLOY.md e validados após a publicação.
