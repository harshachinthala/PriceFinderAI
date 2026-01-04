import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# RAG Configuration
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PERSIST_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
#Specifies which HuggingFace embedding model to use