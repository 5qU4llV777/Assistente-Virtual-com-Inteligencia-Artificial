import streamlit as st
import pandas as pd
from groq import Groq
import chromadb
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import hashlib

st.title("🧙 IA com RAG - Gandalf")
st.caption("Busca vetorial — aguenta qualquer tamanho")

api_key = st.text_input("API Key do Groq:", type="password")

@st.cache_resource
def carregar_modelos():
    # Embeddings para busca semântica
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Cliente ChromaDB
    chroma_client = chromadb.Client()
    
    # Pipeline de QA com Transformers (DistilBERT)
    qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
    
    return embedding_model, chroma_client, qa_pipeline

embedding_model, chroma_client, qa_pipeline = carregar_modelos()

uploaded_files = st.file_uploader(
    "📂 Envie seus CSVs ou Excel",
    type=["csv", "xlsx", "xls"],
    accept_multiple_files=True
)

def indexar_dataframe(df, nome_arquivo, collection):
    chunk_size = 50
    chunks, ids = [], []
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size]
        texto = f"Arquivo: {nome_arquivo}\nLinhas {i} a {i+len(chunk)}:\n{chunk.to_string()}"
        chunk_id = hashlib.md5(texto.encode()).hexdigest()
        chunks.append(texto)
        ids.append(chunk_id)
    embeddings = embedding_model.encode(chunks).tolist()
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
        if not api_key:
            st.error("Insira sua API key primeiro!")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)

            # Busca chunks relevantes
            query_embedding = embedding_model.encode([prompt]).tolist()
            resultados = collection.query(query_embeddings=query_embedding, n_results=5)
            contexto = "\n\n".join(resultados["documents"][0])

            # Resposta inicial com NLP avançado (DistilBERT)
            resposta_nlp = qa_pipeline(question=prompt, context=contexto)["answer"]
            st.write(f"🔎 Resposta baseada em NLP: {resposta_nlp}")

            # Refinamento com Groq
            system_prompt = f"""Você é um analista de dados experiente.
Responda a pergunta do usuário com base nos trechos do dataset abaixo.
Se não encontrar a informação, diga: Isto está além da minha compreensão.

TRECHOS RELEVANTES:
{contexto}
"""
            client = Groq(api_key=api_key)
            mensagens = [{"role": "system", "content": system_prompt}, *st.session_state.messages]

            with st.chat_message("assistant"):
                with st.spinner("Entendi pequeno mestre, vou verificar para você"):
                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=mensagens,
                        max_tokens=2048
                    )
                    reply = response.choices[0].message.content
                    st.write(reply)

            st.session_state.messages.append({"role": "assistant", "content": reply})
else:
    st.info("⬆️ Envie seus arquivos para começar")
