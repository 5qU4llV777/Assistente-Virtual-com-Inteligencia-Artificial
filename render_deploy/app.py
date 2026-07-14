import os
from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
import chromadb
from fastembed import TextEmbedding

app = FastAPI()

# fastembed usa ONNX Runtime em vez de PyTorch — muito mais leve em memória,
# essencial pra caber nos 512MB do plano gratuito do Render
embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
chroma_client = chromadb.Client()

client = Groq(api_key=os.environ["GROQ_API_KEY"])


class Pergunta(BaseModel):
    texto: str


@app.get("/")
def raiz():
    return {"status": "Gandalf, Mentor do Dinheiro, está no ar"}


@app.post("/pergunta")
def responder(pergunta: Pergunta):
    query_embedding = list(embedding_model.embed([pergunta.texto]))[0].tolist()

    resultados = chroma_client.get_collection("datasets").query(
        query_embeddings=[query_embedding], n_results=5
    )
    contexto = "\n\n".join(resultados["documents"][0])

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