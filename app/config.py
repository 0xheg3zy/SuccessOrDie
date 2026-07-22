import os


DEFAULT_OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434/api/chat"
)

DEFAULT_OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:8b"
)

DEFAULT_COLLECTION_PATH = (
    "collections/collection.json"
)

DEFAULT_ENVIRONMENT_PATH = (
    "environments/local.json"
)

DEFAULT_REPORT_PATH = (
    "reports/results.json"
)

DEFAULT_REQUEST_TIMEOUT = 30

DEFAULT_LLM_TIMEOUT = 300