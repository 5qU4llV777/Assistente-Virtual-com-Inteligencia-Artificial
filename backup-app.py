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

# Inicializa cliente Groq com chave de ambiente
client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))


class Pergunta(BaseModel):
    texto: str


@app.get("/")
def raiz():
    return {"status": "Gandalf, Mentor do Dinheiro, está no ar"}


@app.post("/pergunta")
def responder(pergunta: Pergunta):
    try:
        # Gera embedding da pergunta
        query_embedding = list(embedding_model.embed([pergunta.texto]))[0].tolist()

        # Garante que a coleção exista
        if "datasets" not in [c.name for c in chroma_client.list_collections()]:
            chroma_client.create_collection("datasets")

        # Busca contexto
        resultados = chroma_client.get_collection("datasets").query(
            query_embeddings=[query_embedding], n_results=5
        )
        contexto = "\n\n".join(resultados["documents"][0]) if resultados["documents"] else ""

        # Prompt para o modelo
        system_prompt = f"""
        Você é Gandalf, Mentor do Dinheiro.
        Responda de forma amigável e didática.
        Pergunta: {pergunta.texto}
        Contexto: {contexto}
        """

        # Chamada ao modelo Groq
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}],
            max_tokens=1024
        )

        return {"resposta": response.choices[0].message.content}

    except Exception as e:
        # Retorna erro como JSON válido
        return {"erro": str(e)}


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
          .erro { margin-top: 20px; font-size: 16px; color: #ff5555; }
        </style>
      </head>
      <body>
        <h1>🧙‍♂️ Gandalf, Mentor do Dinheiro</h1>
        <form id="form">
          <input id="texto" placeholder="Digite sua pergunta..." />
          <button type="submit">Perguntar</button>
        </form>
        <div class="resposta" id="resposta"></div>
        <div class="erro" id="erro"></div>
        <script>
          document.getElementById('form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const texto = document.getElementById('texto').value;
            document.getElementById('resposta').innerText = '';
            document.getElementById('erro').innerText = '';
            try {
              const resp = await fetch('/pergunta', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({texto})
              });
              const data = await resp.json();
              if (data.resposta) {
                document.getElementById('resposta').innerText = data.resposta;
              } else {
                document.getElementById('erro').innerText = '⚠️ ' + data.erro;
              }
            } catch (err) {
              document.getElementById('erro').innerText = '❌ Erro de conexão com o servidor.';
            }
          });
        </script>
      </body>
    </html>
    """
