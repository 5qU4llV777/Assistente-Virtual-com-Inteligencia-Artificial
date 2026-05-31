## Base de Conhecimento
### Dados Utilizados

# Arquivos do Agente

| Arquivo                    | Formato | Para que serve no Gandalf                     |
|----------------------------|---------|-----------------------------------------------|
| dataset_conceitos.csv      | CSV     | Contextualizar erros e acertos                |
| dataset_investimentos.csv  | CSV     | Personalizar recomendações                    |
| dataset_juros.csv          | CSV     | Ensina o que é juros compostos e simples      |
| dataset_orcamento.csv      | CSV     | Analisar padrão de gastos do cliente          |

### [Gerador de Arquivos .csv](https://github.com/5qU4llV777/Assistente-Virtual-com-Inteligencia-Artificial/blob/main/data/geradorcsv.py)

Quer um dataset mais robusto? Você pode utilizar datasets públicos do [Hugging Face](https://huggingface.co/datasets) relacionados a finanças, desde que sejam adequados ao contexto do desafio


## Estratégia de Integração
### Como os dados são carregados?

Serão carregados no inicio da sessão pelo botão de upload 

## Como os dados são usados no prompt?
Você é um analista de dados experiente.
Responda a pergunta do usuário com base nos trechos do dataset abaixo.

Se não encontrar a informação: Isto esta além da minha compreensão

### regras
1. sempre baseia suas respostas nos dados fornecidos

2. Nunca inventa informações financeiras

3. Se não souber algo,avisa que esta além da minha compreenão e que os dados fornecidos são sobre financeiros 
