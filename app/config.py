import os


OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/chat"
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:8b"
)

COLLECTION_PATH = os.getenv(
    "COLLECTION_PATH",
    "collections/collection.json"
)

REPORT_PATH = os.getenv(
    "REPORT_PATH",
    "reports/results.json"
)

REQUEST_TIMEOUT = int(
    os.getenv(
        "REQUEST_TIMEOUT",
        "30"
    )
)