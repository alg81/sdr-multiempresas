import os

# Diretórios do projeto
BASE_QA_DIR = os.path.join("data", "base_de_conhecimento")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
BASE_CONHECIMENTO_DIR = os.path.join(DATA_DIR, "base_de_conhecimento")
FAISS_DIR = os.path.join(DATA_DIR, "faiss_indices")
PDF_DIR = os.path.join(DATA_DIR, "pdfs")
LOG_DIR = os.path.join(BASE_DIR, "logs")

# Modelos utilizados via LM Studio
NOME_MODELO_EMBEDDING = "text-embedding-nomic-embed-text-v1.5"
NOME_MODELO_LLM = "openai/gpt-oss-20b"  # Pode ser alterado depois

# API local LM Studio (ajustar porta se necessário)
LM_STUDIO_API_BASE = "http://localhost:1234/v1"

# Empresas disponíveis no sistema
EMPRESAS_DISPONIVEIS = ["vivo"]

# Parâmetros do sistema
NUM_DOCUMENTS_FAISS = 5
MOSTRAR_CITACOES = False  # Pode ser alternado por botão na UI
DEBUG = True
