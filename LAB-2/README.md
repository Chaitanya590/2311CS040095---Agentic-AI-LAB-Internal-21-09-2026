# Project 2: RAG-Based Question Answering System

A local Retrieval-Augmented Generation (RAG) system that extracts articles from Wikipedia dynamically, indexes them in a local FAISS vector database, retrieves relevant contexts, and answers questions using grounded LLM completions.

## Architecture

1. **DataLoader Module (`data_loader.py`)**: Fetches plain text extracts for target topics ("Generative artificial intelligence", "Retrieval-augmented generation", "Large language model") using the open Wikipedia Web API.
2. **Indexer Module (`indexer.py`)**: Splits documents into clean, word-aligned 500-character chunks (with 100-character overlap) and embeddings them using `all-MiniLM-L6-v2`. Saves them in local `faiss_index.bin` and `metadata.json` files.
3. **Retriever Module (`retriever.py`)**: Reads the local index files and performs similarity searches.
4. **LLM Client (`llm_client.py`)**: Standardizes local Ollama / Gemini API routes, with dynamic MOCK fallback.
5. **Generator Module (`generator.py`)**: Injects context into prompt templates to ground the model responses.
6. **Evaluator Module (`evaluator.py`)**: Computes Retrieval Recall accuracy and Response Faithfulness using LLM-as-a-judge checking.
7. **Main Interface (`main.py`)**: Starts the interactive Q&A session.

## Setup Instructions

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Select LLM Backend:
   * **Gemini**: Export your key: `set GEMINI_API_KEY=your_key_here`
   * **Ollama**: Run your local model: `ollama run llama3.2`
   * **Default Fallback**: Runs instantly in Mock fallback mode.

3. Run the interactive console:
   ```bash
   python main.py
   ```

4. Run the evaluation suite:
   ```bash
   python evaluator.py
   ```
