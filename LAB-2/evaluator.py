import time
from retriever import RAGRetriever
from llm_client import LLMClient
from generator import RAGGenerator

# Benchmark test cases
EVAL_TEST_CASES = [
    {
        "id": 1,
        "question": "What does RAG stand for?",
        "expected_keywords": ["retrieval", "augmented", "generation"]
    },
    {
        "id": 2,
        "question": "Explain the difference between pre-training and RAG.",
        "expected_keywords": ["pre-training", "retriev", "fine-tuning"]
    },
    {
        "id": 3,
        "question": "What are the core stages of RAG?",
        "expected_keywords": ["indexing", "retrieval", "generation"]
    }
]

def evaluate_faithfulness(llm_client: LLMClient, context: str, answer: str) -> bool:
    """Uses the LLM-as-a-judge method to evaluate if the answer is faithful to the context."""
    system_prompt = (
        "You are an objective AI evaluator. Your job is to determine if a generated answer is "
        "completely supported by the provided Context Chunks. You must output ONLY 'YES' or 'NO'. "
        "Do not write any introductory or concluding text."
    )
    
    prompt = f"""Context Chunks:
{context}

Generated Answer: {answer}

Is the generated answer supported by the context? Output YES if the answer is completely supported without extrapolating, otherwise output NO.
Evaluation:"""

    response = llm_client.generate(prompt, system_prompt=system_prompt).strip().upper()
    return "YES" in response

def run_evaluation():
    # 1. Initialize retriever and generator
    try:
        retriever = RAGRetriever()
    except FileNotFoundError:
        # Build index if not present
        from indexer import DocumentIndexer
        indexer = DocumentIndexer()
        indexer.process_and_index()
        retriever = RAGRetriever()
        
    client = LLMClient()
    generator = RAGGenerator(client)

    print("\n" + "="*50)
    print("STARTING RAG QA PIPELINE EVALUATION")
    print("="*50)
    print(f"Provider: {client.provider} ({client.model_name})")

    retrieval_success = 0
    faithfulness_success = 0
    total_cases = len(EVAL_TEST_CASES)

    for case in EVAL_TEST_CASES:
        print(f"\n[Case {case['id']}] Question: {case['question']}")
        
        # 1. Retrieve
        start_time = time.time()
        context_str = retriever.get_context_string(case["question"], top_k=2)
        latency = time.time() - start_time
        
        # 2. Check Retrieval Relevance (Keyword check)
        context_lower = context_str.lower()
        keyword_match = any(kw.lower() in context_lower for kw in case["expected_keywords"])
        if keyword_match:
            retrieval_success += 1
            retrieval_status = "PASSED"
        else:
            retrieval_status = "FAILED"
            
        print(f"-> Retrieval Relevance: {retrieval_status} (Latency: {latency:.2f}s)")
        
        # 3. Generate Answer
        answer = generator.generate_answer(case["question"], context_str)
        print(f"-> Generated Answer: {answer}")
        
        # 4. Check Faithfulness (LLM-as-a-judge)
        is_faithful = evaluate_faithfulness(client, context_str, answer)
        if is_faithful:
            faithfulness_success += 1
            faithfulness_status = "YES"
        else:
            faithfulness_status = "NO"
        print(f"-> Faithfulness Check: {faithfulness_status}")

    retrieval_acc = (retrieval_success / total_cases) * 100
    faithfulness_acc = (faithfulness_success / total_cases) * 100

    print("\n" + "="*50)
    print("EVALUATION METRICS SUMMARY")
    print("="*50)
    print(f"Total Test Cases:       {total_cases}")
    print(f"Retrieval Recall Acc:   {retrieval_acc:.2f}%")
    print(f"Answer Faithfulness:    {faithfulness_acc:.2f}%")
    print("="*50 + "\n")

    return retrieval_acc, faithfulness_acc

if __name__ == "__main__":
    run_evaluation()
