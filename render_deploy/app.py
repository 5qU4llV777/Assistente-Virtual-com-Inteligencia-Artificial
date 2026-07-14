import os
import streamlit as st
import pandas as pd
import chromadb
from fastembed import TextEmbedding
from transformers import pipeline
import hashlib
from groq import Groq

# ⚙️ Configuração inicial para evitar cache pesado
st.cache_resource.clear()
st.set_page_config(page_title="Gandalf", layout="wide")

st.title("🧙 IA com RAG - Gandalf")
st.caption("Busca vetorial — otimizado para Render Free")

@st.cache_resource
def carregar_modelos():
    # Embeddings leves com ONNX Runtime
    embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    # Cliente ChromaDB persistente em disco (economiza RAM)
    chroma_client = chromadb.PersistentClient(path="/tmp/chroma")

    # Pipeline de QA leve
    qa_pipeline = pipeline(
        "text-generation",
        model="google/flan-t5-small"  # versão menor e mais rápida
    )

    return embedding_model, chroma_client, qa_pipeline

embedding_model, chroma_client, qa_pipeline = carregar_modelos()

# Inicializa cliente Groq com variável de ambiente
client = Groq(api_key=os.environ["GROQ_API_KEY"])

uploaded_files = st.file_uploader(
    "📂 Envie seus CSVs ou Excel",
    type=["csv", "xlsx", "xls"],
    accept_multiple_files=True
)

def indexar_dataframe(df, nome_arquivo, collection):
    chunk_size = 20  # reduzido para economizar memória
    chunks, ids = [], []
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        texto = f"Arquivo: {nome_arquivo}\nLinhas {i} a {i+len(chunk)}:\n{chunk.to_string()}"
        chunk_id = hashlib.md5(texto.encode()).hexdigest()
        chunks.append(texto)
        ids.append(chunk_id)
    embeddings = list(embedding_model.embed(chunks))
    collection.add(documents=chunks, embeddings=embeddings, ids=ids)
    return len(chunks)

if uploaded_files:
    try:
        collection = chroma_client.get_collection("datasets")
    except:
        collection = chroma_client.create_collection("datasets")

    for file in uploaded_files:
        file_hash = hashlib.md5(file.name.encode()).hexdigest()
        if f"indexed_{file_hash}" not in st.session_state:
            with st.spinner(f"Indexando {file.name}..."):
                df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
                n_chunks = indexar_dataframe(df, file.name, collection)
                st.session_state[f"indexed_{file_hash}"] = True
                st.success(f"✅ {file.name} indexado em {n_chunks} blocos ({df.shape[0]} linhas)")
        else:
            st.info(f"✅ {file.name} já está indexado")

    st.divider()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("olá sou Gandalf, seu Mentor do Dinheiro, como posso te ajudar hoje?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Busca chunks relevantes
        query_embedding = list(embedding_model.embed([prompt]))[0].tolist()
        resultados = collection.query(query_embeddings=[query_embedding], n_results=5)
        contexto = "\n\n".join(resultados["documents"][0])

        # Resposta inicial com NLP leve
        entrada = f"Pergunta: {prompt}\nContexto: {contexto}\nResposta:"
        resposta_nlp = qa_pipeline(entrada, max_length=150)[0]["generated_text"]

        st.write(f"🔎 Resposta baseada em NLP: {resposta_nlp}")

        # Escolha do modo de resposta
        modo = st.radio(
            "Escolha o modo de resposta:",
            ["Resposta direta", "Resumo", "Insights"]
        )

        if modo == "Resumo":
            system_prompt = f"""Você é um analista de dados experiente.
Resuma os trechos abaixo em até 5 pontos principais.
Se não encontrar a informação, diga: Isto está além da minha compreensão.

TRECHOS RELEVANTES:
{contexto}
"""
        elif modo == "Insights":
            system_prompt = f"""Você é um consultor financeiro.
Analise os trechos abaixo e gere insights práticos para o usuário.
Se não encontrar a informação, diga: Isto está além da minha compreensão.

TRECHOS RELEVANTES:
{contexto}
"""
        else:
            system_prompt = f"""Você é Gandalf, Mentor do Dinheiro.
Responda de forma amigável e didática, adaptando ao estilo do usuário.
Se não encontrar a informação, diga: Isto está além da minha compreensão.

Pergunta:
{prompt}

TRECHOS RELEVANTES:
{contexto}
"""

        mensagens = [{"role": "system", "content": system_prompt}, *st.session_state.messages]

        with st.chat_message("assistant"):
            with st.spinner("Entendi pequeno mestre, vou verificar para você"):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=mensagens,
                    max_tokens=1024  # reduzido para economizar memória
                )
                reply = response.choices[0].message.content
                st.write(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})
else:
    st.info("⬆️ Envie seus arquivos para começar")
