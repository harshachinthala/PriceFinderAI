
# PriceFinder AI 🛍️

A Dynamic RAG application that helps users find the best prices and sellers for products by combining an internal knowledge base with real-time web search.

Demo Link: https://huggingface.co/spaces/harshachinthala/PriceFinderAI

### 🧠 Tech Stack & Skills

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![LLM](https://img.shields.io/badge/LLM-OpenAI-black)
![Dynamic%20RAG](https://img.shields.io/badge/Dynamic%20RAG-Enabled-purple)
![LangChain](https://img.shields.io/badge/LangChain-Orchestration-green)
![VectorDB](https://img.shields.io/badge/VectorDB-ChromaDB-orange)
![Embeddings](https://img.shields.io/badge/Embeddings-Text%20Embeddings-red)
![Web%20Search](https://img.shields.io/badge/Web%20Search-Serper%20API-blueviolet)
![Price%20Comparison](https://img.shields.io/badge/Price%20Comparison-Automated-success)
![Gradio](https://img.shields.io/badge/Gradio-UI-yellow)
![Deployment](https://img.shields.io/badge/Deployment-HuggingFace%20%7C%20Render-lightgrey)


## Features

- **Internal Knowledge Base**: Stores product specs and seller details (in `data/`).
- **Real-Time Data**: Uses Serper API to fetch live competitor prices and listings.
- **Dynamic RAG**: Merges internal static data with live external data for the LLM.
- **Smart Comparison**: Identifies the cheapest seller and compares options.
- **Interactive UI**: Built with Gradio.

## Project Structure

```
├── data/
│   ├── products/       # Product markdown files
│   └── sellers/        # Seller markdown files
├── src/
│   ├── app.py          # Gradio UI interface creation
│   ├── config.py       # Configuration & env vars
│   ├── llm_engine.py   # Core logic (LangChain + prompting)
│   ├── rag_pipeline.py # ChromaDB vector store management
│   └── serper_tool.py  # Serper API integration
├── app.py              # Main entry point for Hugging Face
└── requirements.txt    # Project dependencies
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   
   **For Local Development**: Create a `.env` file in the root directory and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_key
   SERPER_API_KEY=your_serper_key
   ```
   
   **For Hugging Face Deployment**: Add your API keys as Secrets in your Space settings:
   - Go to Settings → Repository Secrets
   - Add `OPENAI_API_KEY` with your OpenAI API key
   - Add `SERPER_API_KEY` with your Serper API key

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Usage**:
   - Open the browser link provided (usually `http://127.0.0.1:7860`).
   - Enter a query like:
     - "Describe iPhone 15 Pro Max"
     - "Best price for Sony WH-1000XM5"
     - "Who sells Samsung Galaxy S24 Ultra?"

## 🌐 Deployment

### Deploy to Render (Free)

1. **Create a new Web Service** on [Render](https://render.com)
2. **Connect your GitHub repository**
3. **Configure**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. **Deploy!**

### Deploy to Railway (Free)

1. **Create a new project** on [Railway](https://railway.app)
2. **Deploy from GitHub**
3. Railway will auto-detect the Procfile and deploy

### Deploy to Hugging Face Spaces

1. **Create a new Space** on [Hugging Face](https://huggingface.co/spaces)
2. **Choose "Gradio" SDK** (or convert to Gradio)
3. **Upload files** and deploy


## How it Works

1. **Query**: The user asks a question.
2. **Retrieve**: The system searches the local `data/` directory (ChromaDB) for relevant product/seller info.
3. **Search**: The system simultaneously queries the web (Serper) for real-time pricing and availability.
4. **Synthesize**: The LLM combines both contexts to provide a comprehensive answer, recommending the best deal.
