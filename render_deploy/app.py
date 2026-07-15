import os
import hashlib
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from groq import Groq
import chromadb
from fastembed import TextEmbedding

app = FastAPI()

# Embeddings leves
embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Cliente ChromaDB persistente em disco
chroma_client = chromadb.PersistentClient(path="/tmp/chroma")

# Inicializa cliente Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

class Pergunta(BaseModel):
    texto: str

@app.get("/")
def raiz():
    return {"status": "Gandalf, Mentor do Dinheiro, está no ar"}

# Endpoint para upload de arquivos CSV/Excel
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        # Lê arquivo
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)

        # Cria ou pega coleção
        try:
            collection = chroma_client.get_collection("datasets")
        except:
            collection = chroma_client.create_collection("datasets")

        # Indexa em chunks
        chunk_size = 20
        chunks, ids = [], []
        for i in range(0, len(df), chunk_size):
            chunk = df.iloc[i:i+chunk_size]
            texto = f"Arquivo: {file.filename}\nLinhas {i} a {i+len(chunk)}:\n{chunk.to_string()}"
            chunk_id = hashlib.md5(texto.encode()).hexdigest()
            chunks.append(texto)
            ids.append(chunk_id)

        embeddings = list(embedding_model.embed(chunks))
        collection.add(documents=chunks, embeddings=embeddings, ids=ids)

        return {"status": f"{file.filename} indexado em {len(chunks)} blocos"}
    except Exception as e:
        return {"erro": str(e)}

# Endpoint para perguntas
@app.post("/pergunta")
def responder(pergunta: Pergunta):
    try:
        query_embedding = list(embedding_model.embed([pergunta.texto]))[0].tolist()

        # Busca contexto
        resultados = chroma_client.get_collection("datasets").query(
            query_embeddings=[query_embedding], n_results=5
        )
        contexto = "\n\n".join(resultados["documents"][0]) if resultados["documents"] else ""

        # Prompt
        system_prompt = f"""
        Você é Gandalf, Mentor do Dinheiro.
        Responda de forma amigável e didática.
        Pergunta: {pergunta.texto}
        Contexto: {contexto}
        """

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=1024
        )

        return {"resposta": response.choices[0].message.content}
    except Exception as e:
        return {"erro": str(e)}
