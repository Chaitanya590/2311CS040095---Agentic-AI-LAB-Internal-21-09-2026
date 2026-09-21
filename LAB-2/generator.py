from llm_client import LLMClient

class RAGGenerator:
    def __init__(self, llm_client: LLMClient):
        self.client = llm_client

    def generate_answer(self, question: str, context: str) -> str:
        """
        Takes the user's question and retrieved context, and prompts the LLM
        to generate a factual answer strictly grounded in the context.
        """
        system_prompt = (
            "You are a helpful, precise technical assistant. Your job is to answer the user's question "
            "using ONLY the provided Context Chunks. If the Context Chunks do not contain the information "
            "needed to answer, state clearly that you do not have enough information to answer. "
            "Do not make up facts or use outside knowledge."
        )

        prompt = f"""Context Chunks:
{context}

Question: {question}

Grounded Answer:"""

        return self.client.generate(prompt, system_prompt=system_prompt)

if __name__ == "__main__":
    client = LLMClient()
    generator = RAGGenerator(client)
    dummy_context = "--- Context Chunk 1 ---\nFAISS (Facebook AI Similarity Search) is a library for efficient similarity search."
    q = "What is FAISS?"
    print(generator.generate_answer(q, dummy_context))
