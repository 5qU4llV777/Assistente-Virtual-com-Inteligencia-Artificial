Subir para AWS Lambda
Vá no console AWS → Lambda → Create function.

Escolha Container image se usar Docker, ou zip do código se for simples.

Configure memória (mínimo 1GB) e timeout (30s).

 Configurar API Gateway
Vá em API Gateway → Create API → REST API.

Crie um recurso /pergunta.

Configure método POST → integração com sua função Lambda.

Habilite CORS se quiser consumir via navegador.

Testar
Faça um POST para o endpoint gerado:

bash
curl -X POST https://SEU_ENDPOINT.amazonaws.com/prod/pergunta \
     -H "Content-Type: application/json" \
     -d '{"texto": "Qual é o total de dívidas no dataset?"}'
Você deve receber:

json
{"resposta": "O total de dívidas é ..."}