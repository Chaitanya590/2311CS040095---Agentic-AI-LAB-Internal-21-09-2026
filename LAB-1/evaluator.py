import time
from database import DatabaseManager
from retriever import SchemaRetriever
from llm_client import LLMClient
from generator import SQLGenerator
from executor import SQLExecutor

# Define 5 benchmark evaluation cases
TEST_CASES = [
    {
        "id": 1,
        "question": "How many artists are there in the database?",
        "reference_sql": "SELECT COUNT(*) FROM Artist;"
    },
    {
        "id": 2,
        "question": "List the names of the top 3 longest tracks (in milliseconds) and their lengths.",
        "reference_sql": "SELECT Name, Milliseconds FROM Track ORDER BY Milliseconds DESC LIMIT 3;"
    },
    {
        "id": 3,
        "question": "How many customers are from Canada?",
        "reference_sql": "SELECT COUNT(*) FROM Customer WHERE Country = 'Canada';"
    },
    {
        "id": 4,
        "question": "What is the title of the album with AlbumId 10?",
        "reference_sql": "SELECT Title FROM Album WHERE AlbumId = 10;"
    },
    {
        "id": 5,
        "question": "List the employee IDs and last names of employees hired in 2002.",
        "reference_sql": "SELECT EmployeeId, LastName FROM Employee WHERE HireDate LIKE '2002%';"
    }
]

def run_evaluation():
    db = DatabaseManager()
    executor = SQLExecutor(db)
    retriever = SchemaRetriever()
    retriever.index_database(db)
    
    client = LLMClient()
    generator = SQLGenerator(client)

    print("\n" + "="*50)
    print("STARTING TEXT-TO-SQL PIPELINE EVALUATION")
    print("="*50)
    print(f"Provider: {client.provider} ({client.model_name})")
    
    correct_count = 0
    total_cases = len(TEST_CASES)

    for case in TEST_CASES:
        print(f"\n[Case {case['id']}] Question: {case['question']}")
        print(f"Reference SQL: {case['reference_sql']}")
        
        # Execute reference SQL to get reference results
        ref_res = db.execute_query(case["reference_sql"])
        
        start_time = time.time()
        # Retrieve context schema
        context = retriever.get_context_string(case["question"], top_k=3)
        
        # Generate SQL
        try:
            generated_sql = generator.generate_sql(case["question"], context)
            print(f"Generated SQL: {generated_sql}")
        except Exception as e:
            print(f"Generation Error: {e}")
            generated_sql = "ERROR"
        
        latency = time.time() - start_time
        
        # Execute generated SQL
        gen_res = executor.execute(generated_sql)
        
        # Evaluation check: compare execution rows
        # We sort or convert to sets to ensure minor ordering differences don't fail equivalent results,
        # but exact ordering might be part of the query (e.g. ORDER BY). We compare directly.
        match = False
        if not gen_res.get("error") and not ref_res.get("error"):
            # Compare rows
            if gen_res["rows"] == ref_res["rows"]:
                match = True
                correct_count += 1
            else:
                # Fallback: check if content is same but in different order (for queries where ordering wasn't requested)
                try:
                    if set(map(tuple, gen_res["rows"])) == set(map(tuple, ref_res["rows"])):
                        match = True
                        correct_count += 1
                except Exception:
                    pass

        status = "PASSED" if match else "FAILED"
        print(f"Status: {status} (Latency: {latency:.2f}s)")
        if not match:
            print(f"Expected: {ref_res['rows']}")
            print(f"Received: {gen_res['rows']}")
            if gen_res.get("error"):
                print(f"Execution Error: {gen_res['error']}")
                
    accuracy = (correct_count / total_cases) * 100
    print("\n" + "="*50)
    print("EVALUATION METRICS SUMMARY")
    print("="*50)
    print(f"Total Test Cases: {total_cases}")
    print(f"Passed Cases:    {correct_count}")
    print(f"Accuracy:        {accuracy:.2f}%")
    print("="*50 + "\n")
    return accuracy

if __name__ == "__main__":
    run_evaluation()
