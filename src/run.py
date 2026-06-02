import subprocess
import threading
import time
import re

def run_streamlit():
    subprocess.run([
        "python", "-m", "streamlit", "run", "assistente_virtual.py",
        "--server.port=8501", "--server.headless=true"
    ])

# Inicia o Streamlit em uma thread separada
threading.Thread(target=run_streamlit, daemon=True).start()
time.sleep(6)  # tempo para iniciar o servidor

# Executa o cloudflared
tunnel = subprocess.Popen(
    ["cloudflared.exe", "tunnel", "--url", "http://localhost:8501"],
    stderr=subprocess.PIPE, stdout=subprocess.PIPE
)

# Captura a URL gerada pelo Cloudflare
for line in tunnel.stderr:
    line = line.decode()
    if "trycloudflare.com" in line:
        url = re.search(r'https://\S+\.trycloudflare\.com', line)
        if url:
            print(f"✅ Acesse aqui: {url.group()}")
            break
