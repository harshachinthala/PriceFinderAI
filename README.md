# PriceFinder AI 🛍️

A Dynamic RAG application that helps users find the best prices and sellers for products by combining an internal knowledge base with real-time web search.

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
│   ├── app.py          # Gradio UI entry point
│   ├── config.py       # Configuration & env vars
│   ├── llm_engine.py   # Core logic (LangChain + prompting)
│   ├── rag_pipeline.py # ChromaDB vector store management
│   └── serper_tool.py  # Serper API integration
├── run.py              # Main execution script
└── requirements.txt    # Project dependencies
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file in the root directory and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_key
   SERPER_API_KEY=your_serper_key
   ```

3. **Run the Application**:
   ```bash
   python run.py
   ```

4. **Usage**:
   - Open the browser link provided (usually `http://127.0.0.1:7860`).
   - Enter a query like:
     - "Describe iPhone 15 Pro Max"
     - "Best price for Sony WH-1000XM5"
     - "Who sells Samsung Galaxy S24 Ultra?"

## How it Works

1. **Query**: The user asks a question.
2. **Retrieve**: The system searches the local `data/` directory (ChromaDB) for relevant product/seller info.
3. **Search**: The system simultaneously queries the web (Serper) for real-time pricing and availability.
4. **Synthesize**: The LLM combines both contexts to provide a comprehensive answer, recommending the best deal.
