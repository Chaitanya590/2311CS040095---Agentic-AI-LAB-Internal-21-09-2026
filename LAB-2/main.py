import os
import sys
from indexer import DocumentIndexer
from retriever import RAGRetriever
from llm_client import LLMClient
from generator import RAGGenerator

def main():
    print("="*60)
    print("Welcome to Project 2: RAG-Based QA System")
    print("="*60)
    
    index_file = "faiss_index.bin"
    meta_file = "metadata.json"
    
    # 1. Automate database setup
    if not os.path.exists(index_file) or not os.path.exists(meta_file):
        print("Vector index files not found. Initializing indexing pipeline...")
        indexer = DocumentIndexer()
        indexer.process_and_index(index_file=index_file, meta_file=meta_file)
        
    # 2. Initialize Retriever and Generator
    try:
        retriever = RAGRetriever(index_file=index_file, meta_file=meta_file)
    except Exception as e:
        print(f"Error loading retriever index: {e}")
        sys.exit(1)
        
    client = LLMClient()
    generator = RAGGenerator(client)
    
    print("\nSystem ready! Ask questions about Generative AI, RAG, or LLMs.")
    print("Commands:")
    print("  Type 'exit' or 'quit' to end.")
    print("  Type 'eval' to run the evaluator.")
    print("-" * 60)
    
    while True:
        try:
            question = input("\nAsk a question: ").strip()
        except KeyboardInterrupt:
            print("\nExiting...")
            break
            
        if not question:
            continue
            
        if question.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
            
        if question.lower() == "eval":
            from evaluator import run_evaluation
            run_evaluation()
            continue
            
        print("\n[Step 1] Retrieving relevant documents from FAISS...")
        chunks = retriever.retrieve(question, top_k=2)
        
        if not chunks:
            print("-> No relevant context found.")
            continue
            
        print("-> Retrieved sources:")
        for i, chunk in enumerate(chunks, 1):
            print(f"   [{i}] {chunk['source']} (Score: {chunk['score']:.4f})")
            
        print("[Step 2] Formatting context and generating answer...")
        context_str = retriever.get_context_string(question, top_k=2)
        answer = generator.generate_answer(question, context_str)
        
        print(f"\nFinal Answer:\n{answer}")
        print("-" * 60)

if __name__ == "__main__":
    main()
