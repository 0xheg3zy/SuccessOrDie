#!/bin/bash
apt update
apt install zstd screen ttyd nano -y --fix-missing
curl -fsSL https://ollama.com/install.sh | sh
screen -dmS ollama ollama serve
screen -dmS ttyd ttyd -p 9999 /bin/bash -i
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
dpkg -i cloudflared-linux-amd64.deb
screen -dmS nodeclf cloudflared tunnel --url 127.0.0.1:9999
screen -dmS mitmclf cloudflared tunnel --url 127.0.0.1:8081
pip install mitmproxy
screen -dmS mitm /usr/local/bin/mitmweb --listen-host 0.0.0.0 --listen-port 9090 --web-host 0.0.0.0 --web-port 8081
ollama pull qwen3:8b
python -m app.main --proxy 127.0.0.1:9090 --verify false
