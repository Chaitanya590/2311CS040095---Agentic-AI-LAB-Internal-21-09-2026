import sys
from database import DatabaseManager
from retriever import SchemaRetriever
from llm_client import LLMClient
from generator import SQLGenerator
from executor import SQLExecutor

def main():
    print("="*60)
    print("Welcome to Project 1: Text-to-SQL Workflow (Chinook DB)")
    print("="*60)
    
    # 1. Initialize Components
    db = DatabaseManager()
    
    retriever = SchemaRetriever()
    retriever.index_database(db)
    
    client = LLMClient()
    generator = SQLGenerator(client)
    executor = SQLExecutor(db)
    
    print("\nSystem ready! You can now query the Chinook Database in natural language.")
    print("Commands:")
    print("  Type 'exit' or 'quit' to end.")
    print("  Type 'eval' to run the evaluation suite.")
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
            
        print("\n[Step 1] Retrieving relevant schema...")
        context = retriever.get_context_string(question, top_k=2)
        retrieved_tables = [item["table_name"] for item in retriever.retrieve(question, top_k=2)]
        print(f"-> Retrieved tables: {', '.join(retrieved_tables)}")
        
        print("[Step 2] Generating SQL Query...")
        sql_query = generator.generate_sql(question, context)
        print(f"-> Generated SQL:\n   {sql_query}")
        
        print("[Step 3] Executing SQL Query...")
        res = executor.execute(sql_query)
        
        if res.get("error"):
            print(f"-> Error: {res['error']}")
            continue
            
        print(f"-> Executed successfully. Returned {len(res['rows'])} rows.")
        
        print("[Step 4] Summarizing Results...")
        answer = generator.generate_answer(question, sql_query, res)
        print(f"\nFinal Answer:\n{answer}")
        print("-" * 60)

if __name__ == "__main__":
    main()
