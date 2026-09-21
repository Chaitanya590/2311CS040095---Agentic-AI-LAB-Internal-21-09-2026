import json
import os
import faiss
from sentence_transformers import SentenceTransformer

class RAGRetriever:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", index_file: str = "faiss_index.bin", meta_file: str = "metadata.json"):
        self.index_file = index_file
        self.meta_file = meta_file
        
        # Load embedding model
        print(f"Loading local embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        
        # Load FAISS index and metadata
        if not os.path.exists(index_file) or not os.path.exists(meta_file):
            raise FileNotFoundError(
                f"Index files '{index_file}' or '{meta_file}' not found. "
                "Run `python indexer.py` to build the vector index first."
            )
            
        print("Loading FAISS index...")
        self.index = faiss.read_index(index_file)
        
        print("Loading metadata...")
        with open(meta_file, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def retrieve(self, query: str, top_k: int = 3) -> list:
        """Retrieves top_k most similar chunks for the query."""
        query_vector = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_vector)

        similarities, indices = self.index.search(query_vector, top_k)
        
        results = []
        for rank, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                meta = self.metadata[idx]
                results.append({
                    "text": meta["text"],
                    "source": meta["source"],
                    "score": float(similarities[0][rank])
                })
        return results

    def get_context_string(self, query: str, top_k: int = 3) -> str:
        """Retrieves top chunks and formats them as a clean string block for the LLM."""
        chunks = self.retrieve(query, top_k)
        formatted_chunks = []
        for i, chunk in enumerate(chunks, 1):
            formatted_chunks.append(
                f"--- Context Chunk {i} [Source: {chunk['source']}] (Similarity: {chunk['score']:.4f}) ---\n"
                f"{chunk['text']}"
            )
        return "\n\n".join(formatted_chunks)

if __name__ == "__main__":
    # Test retrieval
    try:
        retriever = RAGRetriever()
        test_q = "What is retrieval-augmented generation?"
        print(f"\nRetrieving for: '{test_q}'")
        res = retriever.retrieve(test_q, top_k=2)
        for r in res:
            print(f"\nScore: {r['score']:.4f} | Source: {r['source']}")
            print(r['text'][:150] + "...")
    except Exception as e:
        print(e)
