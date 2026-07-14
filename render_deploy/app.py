import os
from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
import chromadb
from fastembed import TextEmbedding
from fastapi.responses import HTMLResponse

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


# 🔮 Interface web simples
@app.get("/ui", response_class=HTMLResponse)
def ui():
    return """
    <html>
      <head>
        <title>Gandalf, Mentor do Dinheiro</title>
        <style>
          body { font-family: Arial; background-color: #0b0c10; color: #c5c6c7; text-align: center; padding: 50px; }
          input { width: 60%; padding: 10px; margin: 10px; border-radius: 5px; border: none; }
          button { padding: 10px 20px; background-color: #45a29e; color: white; border: none; border-radius: 5px; cursor: pointer; }
          button:hover { background-color: #66fcf1; color: #0b0c10; }
          .resposta { margin-top: 20px; font-size: 18px; }
        </style>
      </head>
      <body>
        <h1>🧙‍♂️ Gandalf, Mentor do Dinheiro</h1>
        <form id="form">
          <input id="texto" placeholder="Digite sua pergunta..." />
          <button type="submit">Perguntar</button>
        </form>
        <div class="resposta" id="resposta"></div>
        <script>
          document.getElementById('form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const texto = document.getElementById('texto').value;
            const resp = await fetch('/pergunta', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify({texto})
            });
            const data = await resp.json();
            document.getElementById('resposta').innerText = data.resposta;
          });
        </script>
      </body>
    </html>
    """
