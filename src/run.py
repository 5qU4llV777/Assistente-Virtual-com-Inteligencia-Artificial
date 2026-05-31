import subprocess
import threading
import time
import re

# Baixa e configura o cloudflared
subprocess.run([
    "wget", "-q",
    "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64",
    "-O", "cloudflared"
])
subprocess.run(["chmod", "+x", "cloudflared"])

def run_streamlit():
    subprocess.run(["streamlit", "run", "assistente_virtual.py", "--server.port=8501", "--server.headless=true"])

threading.Thread(target=run_streamlit, daemon=True).start()
time.sleep(6)  # tempo para iniciar o servidor

tunnel = subprocess.Popen(
    ["./cloudflared", "tunnel", "--url", "http://localhost:8501"],
    stderr=subprocess.PIPE, stdout=subprocess.PIPE
)

for line in tunnel.stderr:
    line = line.decode()
    if "trycloudflare.com" in line:
        url = re.search(r'https://\S+\.trycloudflare\.com', line)
        if url:
            print(f"✅ Acesse aqui: {url.group()}")
            break
