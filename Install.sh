#!/bin/bash
sudo apt install zstd screen -y
curl -fsSL https://ollama.com/install.sh | sh
screen -dmS ollama ollama serve
sleep 5
ollama pull qwen3:8b
