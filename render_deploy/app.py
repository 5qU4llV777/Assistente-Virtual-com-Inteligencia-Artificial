import os
import hashlib
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from groq import Groq
import chromadb
from fastembed import TextEmbedding
from fastapi.responses import HTMLResponse

app = FastAPI()

embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
chroma_client = chromadb.PersistentClient(path="/tmp/chroma")
client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

class Pergunta(BaseModel):
    texto: str

@app.get("/")
def raiz():
    return {"status": "Gandalf, Mentor do Dinheiro, está no ar"}

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)

        try:
            collection = chroma_client.get_collection("datasets")
        except:
            collection = chroma_client.create_collection("datasets")

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

@app.post("/pergunta")
def responder(pergunta: Pergunta):
    try:
        query_embedding = list(embedding_model.embed([pergunta.texto]))[0].tolist()
        resultados = chroma_client.get_collection("datasets").query(
            query_embeddings=[query_embedding], n_results=5
        )
        contexto = "\n\n".join(resultados["documents"][0]) if resultados["documents"] else ""

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

# 🔮 Interface web simples
@app.get("/ui", response_class=HTMLResponse)
def ui():
    return """
    <html>
      <head>
        <title>Gandalf, Mentor do Dinheiro</title>
        <style>
          body { font-family: Arial; background-color: #0b0c10; color: #c5c6c7; text-align: center; padding: 50px; }
          input, button { padding: 10px; margin: 10px; border-radius: 5px; border: none; }
          button { background-color: #45a29e; color: white; cursor: pointer; }
          button:hover { background-color: #66fcf1; color: #0b0c10; }
          .resposta { margin-top: 20px; font-size: 18px; }
          .erro { margin-top: 20px; font-size: 16px; color: #ff5555; }
        </style>
      </head>
      <body>
        <h1>🧙‍♂️ Gandalf, Mentor do Dinheiro</h1>
        <form id="uploadForm">
          <input type="file" id="file" />
          <button type="submit">Enviar arquivo</button>
        </form>
        <form id="form">
          <input id="texto" placeholder="Digite sua pergunta..." />
          <button type="submit">Perguntar</button>
        </form>
        <div class="resposta" id="resposta"></div>
        <div class="erro" id="erro"></div>
        <script>
          document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const fileInput = document.getElementById('file');
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            const resp = await fetch('/upload', { method: 'POST', body: formData });
            const data = await resp.json();
            alert(data.status || data.erro);
          });

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
