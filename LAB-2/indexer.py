import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from data_loader import load_all_documents, DOCUMENTS_DIR

class DocumentIndexer:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"Loading local embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.metadata = []

    def split_text(self, text: str, chunk_size: int = 500, overlap: int = 100) -> list:
        """
        Splits text into chunks of specified size, attempting to break on word/sentence boundaries.
        """
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = min(start + chunk_size, text_len)
            
            # Find a clean boundary (period, newline, or space) near the end point
            if end < text_len:
                boundary_found = False
                # Look back up to 50 characters for sentence boundary
                for lookback in range(50):
                    char = text[end - lookback]
                    if char in [".", "!", "?"]:
                        end = end - lookback + 1
                        boundary_found = True
                        break
                
                # If no sentence boundary, look back for newline or space
                if not boundary_found:
                    for lookback in range(30):
                        if text[end - lookback] in ["\n", " "]:
                            end = end - lookback + 1
                            boundary_found = True
                            break
            
            chunk = text[start:end].strip()
            if len(chunk) > 30: # Avoid tiny noise chunks
                chunks.append(chunk)
                
            start = end - overlap
            # Guard against infinite loops or past-boundary start points
            if start <= 0 or start >= text_len - overlap:
                break
                
        return chunks

    def process_and_index(self, doc_dir: str = DOCUMENTS_DIR, index_file: str = "faiss_index.bin", meta_file: str = "metadata.json"):
        """Reads all local files, chunks them, embeds them, and saves the FAISS index."""
        # Ensure files are downloaded
        load_all_documents(doc_dir)

        all_chunks = []
        self.metadata = []

        # 1. Read files and chunk them
        for filename in os.listdir(doc_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(doc_dir, filename)
                print(f"Processing and chunking file: {filepath}...")
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
                
                chunks = self.split_text(text, chunk_size=500, overlap=100)
                print(f"-> Generated {len(chunks)} chunks.")
                
                for chunk in chunks:
                    all_chunks.append(chunk)
                    self.metadata.append({
                        "text": chunk,
                        "source": filename
                    })

        if not all_chunks:
            print("No text chunks generated. Cannot build index.")
            return

        # 2. Embed all chunks
        print(f"Generating embeddings for {len(all_chunks)} chunks...")
        embeddings = self.model.encode(all_chunks, convert_to_numpy=True)
        faiss.normalize_L2(embeddings)

        # 3. Save to FAISS Index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

        # 4. Write index and metadata to disk
        faiss.write_index(self.index, index_file)
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            
        print(f"Indexing complete! Saved FAISS index to '{index_file}' and metadata to '{meta_file}'.")

if __name__ == "__main__":
    indexer = DocumentIndexer()
    indexer.process_and_index()
