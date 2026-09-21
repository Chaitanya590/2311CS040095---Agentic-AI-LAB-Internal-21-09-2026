import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from database import DatabaseManager

class SchemaRetriever:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initializes the local HuggingFace embedding model."""
        print(f"Loading local embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.table_metadata = [] # List of dicts matching FAISS indices

    def index_database(self, db: DatabaseManager):
        """Creates embeddings for all tables in the database and stores them in FAISS."""
        print("Indexing database schema...")
        tables = db.get_table_names()
        self.table_metadata = []
        documents = []

        for table in tables:
            ddl = db.get_table_ddl(table)
            # Create a rich text description of the table schema
            sample_rows = db.get_table_sample_rows(table, limit=2)
            sample_str = ""
            if sample_rows:
                sample_str = f"\nSample data: {str(sample_rows)}"
            
            doc_content = f"Table: {table}\nDDL:\n{ddl}{sample_str}"
            documents.append(doc_content)
            self.table_metadata.append({
                "table_name": table,
                "ddl": ddl,
                "document": doc_content
            })

        # Generate embeddings
        embeddings = self.model.encode(documents, convert_to_numpy=True)
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)

        # Initialize FAISS Index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension) # Inner Product on normalized vectors = Cosine Similarity
        self.index.add(embeddings)
        print(f"Indexed {len(tables)} tables in local FAISS.")

    def retrieve(self, query: str, top_k: int = 3) -> list:
        """Retrieves top_k most relevant tables for the given natural language query."""
        if self.index is None or not self.table_metadata:
            raise ValueError("The database schema has not been indexed yet. Call index_database first.")

        query_vector = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_vector)

        # Search FAISS
        similarities, indices = self.index.search(query_vector, top_k)
        
        results = []
        for rank, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.table_metadata):
                meta = self.table_metadata[idx]
                results.append({
                    "table_name": meta["table_name"],
                    "ddl": meta["ddl"],
                    "document": meta["document"],
                    "score": float(similarities[0][rank])
                })
        return results

    def get_context_string(self, query: str, top_k: int = 3) -> str:
        """Returns the retrieved DDLs formatted as a single string context."""
        retrieved = self.retrieve(query, top_k)
        context = []
        for item in retrieved:
            context.append(f"-- Table schema for: {item['table_name']}\n{item['ddl']}")
        return "\n\n".join(context)

if __name__ == "__main__":
    # Test execution
    db = DatabaseManager()
    retriever = SchemaRetriever()
    retriever.index_database(db)
    
    test_query = "Find tracks by the artist AC/DC"
    print(f"\nTesting retrieval for: '{test_query}'")
    results = retriever.retrieve(test_query, top_k=2)
    for r in results:
        print(f"- Table: {r['table_name']} (Score: {r['score']:.4f})")
