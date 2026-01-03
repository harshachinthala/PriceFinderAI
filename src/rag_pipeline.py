import os
import glob
from typing import List
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from src.config import DATA_DIR, PERSIST_DIRECTORY, EMBEDDING_MODEL_NAME

def load_documents() -> List:
    """Loads all Markdown files from the data directory."""
    documents = []
    # Recursively find all .md files in data directory
    md_files = glob.glob(os.path.join(DATA_DIR, "**/*.md"), recursive=True)
    
    for file_path in md_files:
        try:
            loader = TextLoader(file_path, encoding='utf-8')
            documents.extend(loader.load())
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            
    return documents

def split_documents(documents):
    """Splits documents into chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    return text_splitter.split_documents(documents)

def initialize_vector_db():
    """Initializes and returns the Chroma vector database."""
    print("Loading documents...")
    docs = load_documents()
    if not docs:
        print("No documents found in data directory.")
        return None
        
    print(f"Found {len(docs)} documents.")
    chunks = split_documents(docs)
    print(f"Split into {len(chunks)} chunks.")
    
    print("Initializing embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    print("Creating/Updating Vector Store...")
    # Clear existing DB to avoid duplicates in this demo flow
    import shutil
    if os.path.exists(PERSIST_DIRECTORY):
        shutil.rmtree(PERSIST_DIRECTORY)
        
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )
    return vector_store

def get_retriever():
    """Returns a retriever object from the existing vector store."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    vector_store = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings
    )
    return vector_store.as_retriever(search_kwargs={"k": 3})
