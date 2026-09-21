# Project 1: Text-to-SQL Workflow

An end-to-end Text-to-SQL system that translates natural language questions into executable SQLite queries, executes them on a local Chinook database, and provides a natural language summary of the result.

## Architecture

1. **Database Module (`database.py`)**: Downloads the Chinook SQLite database and extracts schemas.
2. **Retriever Module (`retriever.py`)**: Indexes schemas using `sentence-transformers` and `FAISS` to select the most relevant tables for the LLM.
3. **LLM Client (`llm_client.py`)**: Integrates with local Ollama (`llama3.2` or `qwen2.5`) or free-tier Google Gemini API.
4. **Generator Module (`generator.py`)**: Prompts the LLM to generate the SQL query and summaries.
5. **Executor Module (`executor.py`)**: Executes read-only queries safely.
6. **Evaluator Module (`evaluator.py`)**: Benchmarks execution accuracy on standard test cases.
7. **Main Interface (`main.py`)**: Starts the interactive CLI session.

## Setup Instructions

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Choose your LLM Backend:
   * **Option A (Free Gemini API - Recommended)**: Set the `GEMINI_API_KEY` environment variable:
     ```cmd
     set GEMINI_API_KEY=your_gemini_api_key_here
     ```
   * **Option B (Local Ollama)**: Install Ollama locally and download a model:
     ```bash
     ollama run llama3.2
     # or
     ollama run qwen2.5:1.5b
     ```
     Ensure Ollama is running in the background.

3. Run the interactive console:
   ```bash
   python main.py
   ```

4. Run the automated evaluation suite:
   ```bash
   python evaluator.py
   ```
