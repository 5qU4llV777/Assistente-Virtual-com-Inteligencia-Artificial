
import pandas as pd

# Dataset 1 - Orçamento
orcamento = pd.DataFrame([
    {"categoria": "Moradia", "tipo": "necessidade", "percentual_recomendado": 30, "exemplo": "Aluguel/financiamento", "dica": "Não ultrapasse 30% da renda"},
    {"categoria": "Alimentação", "tipo": "necessidade", "percentual_recomendado": 15, "exemplo": "Supermercado/restaurante", "dica": "Cozinhar em casa economiza 40%"},
    {"categoria": "Transporte", "tipo": "necessidade", "percentual_recomendado": 10, "exemplo": "Combustível/transporte público", "dica": "Considere transporte público"},
    {"categoria": "Lazer", "tipo": "desejo", "percentual_recomendado": 10, "exemplo": "Streaming/passeios", "dica": "Lazer saudável é necessário"},
    {"categoria": "Investimentos", "tipo": "prioridade", "percentual_recomendado": 20, "exemplo": "Poupança/Tesouro Direto", "dica": "Pague-se primeiro"},
    {"categoria": "Dívidas", "tipo": "atenção", "percentual_recomendado": 15, "exemplo": "Cartão/empréstimo", "dica": "Quite as de maior juros primeiro"},
])
orcamento.to_csv("dataset_orcamento.csv", index=False)

# Dataset 2 - Juros
juros = pd.DataFrame([
    {"tipo_juro": "Juros simples", "definicao": "Calculado só sobre o valor inicial", "formula": "J = P x i x t", "exemplo_pratico": "Carnê de loja", "armadilha": "Parece barato mas não é"},
    {"tipo_juro": "Juros compostos", "definicao": "Juros sobre juros", "formula": "M = P x (1+i)^t", "exemplo_pratico": "Poupança e cartão de crédito", "armadilha": "No cartão corrói rápido"},
    {"tipo_juro": "CDI", "definicao": "Taxa interbancária de referência", "formula": "Referência para investimentos", "exemplo_pratico": "CDB 100% CDI", "armadilha": "Comparar sempre com inflação"},
    {"tipo_juro": "Selic", "definicao": "Taxa básica da economia", "formula": "Definida pelo Banco Central", "exemplo_pratico": "Tesouro Selic", "armadilha": "Varia com política monetária"},
    {"tipo_juro": "Rotativo cartão", "definicao": "Juros mais altos do Brasil", "formula": "~400% ao ano", "exemplo_pratico": "Pagar mínimo da fatura", "armadilha": "Armadilha mais perigosa"},
])
juros.to_csv("dataset_juros.csv", index=False)

# Dataset 3 - Investimentos
investimentos = pd.DataFrame([
    {"investimento": "Poupança", "tipo": "Renda fixa", "risco": "Baixo", "liquidez": "Diária", "rentabilidade": "~6% ao ano", "valor_minimo": "R$1", "indicado_para": "Iniciantes", "obs": "Pode perder para inflação"},
    {"investimento": "Tesouro Selic", "tipo": "Renda fixa", "risco": "Baixo", "liquidez": "D+1", "rentabilidade": "Selic atual", "valor_minimo": "R$30", "indicado_para": "Reserva de emergência", "obs": "Mais seguro do Brasil"},
    {"investimento": "CDB", "tipo": "Renda fixa", "risco": "Baixo/médio", "liquidez": "Varia", "rentabilidade": "100-120% CDI", "valor_minimo": "R$1", "indicado_para": "Iniciantes", "obs": "Verificar cobertura FGC"},
    {"investimento": "LCI/LCA", "tipo": "Renda fixa", "risco": "Baixo", "liquidez": "Carência", "rentabilidade": "CDI isento IR", "valor_minimo": "R$1000", "indicado_para": "Quem paga IR", "obs": "Isento de imposto de renda"},
    {"investimento": "Ações", "tipo": "Renda variável", "risco": "Alto", "liquidez": "D+3", "rentabilidade": "Variável", "valor_minimo": "R$1", "indicado_para": "Perfil arrojado", "obs": "Estudar antes de investir"},
    {"investimento": "FIIs", "tipo": "Renda variável", "risco": "Médio", "liquidez": "D+3", "rentabilidade": "Dividendos mensais", "valor_minimo": "R$10", "indicado_para": "Renda passiva", "obs": "Diversificar entre fundos"},
])
investimentos.to_csv("dataset_investimentos.csv", index=False)

# Dataset 4 - Conceitos
conceitos = pd.DataFrame([
    {"conceito": "Inflação", "definicao": "Alta geral dos preços", "exemplo": "R$100 comprava mais em 2020", "erro_comum": "Deixar dinheiro parado", "como_evitar": "Investir acima da inflação"},
    {"conceito": "Reserva de emergência", "definicao": "Dinheiro para imprevistos", "exemplo": "Perda de emprego/doença", "erro_comum": "Não ter nenhuma", "como_evitar": "Guardar 6x os gastos mensais"},
    {"conceito": "Juros do rotativo", "definicao": "Maior taxa do Brasil", "exemplo": "Pagar mínimo da fatura", "erro_comum": "Achar que é normal", "como_evitar": "Sempre pagar fatura total"},
    {"conceito": "Financiamento", "definicao": "Compra parcelada com juros", "exemplo": "Carro/imóvel financiado", "erro_comum": "Olhar só a parcela", "como_evitar": "Calcular o total pago"},
    {"conceito": "Previdência privada", "definicao": "Investimento para aposentadoria", "exemplo": "PGBL e VGBL", "erro_comum": "Depender só do INSS", "como_evitar": "Começar cedo"},
    {"conceito": "FGC", "definicao": "Garante depósitos até R$250k", "exemplo": "CDB/poupança se banco quebrar", "erro_comum": "Não saber que existe", "como_evitar": "Diversificar entre bancos"},
])
conceitos.to_csv("dataset_conceitos.csv", index=False)

print("✅ 4 datasets criados com sucesso!")
