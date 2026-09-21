import os
import requests

WIKI_API_URL = "https://en.wikipedia.org/w/api.php"
TOPICS = {
    "Generative_artificial_intelligence": "generative_ai.txt",
    "Retrieval-augmented_generation": "rag.txt",
    "Large_language_model": "large_language_models.txt"
}
DOCUMENTS_DIR = "documents"

def fetch_wikipedia_content(title: str) -> str:
    """Fetches clean plain text for a Wikipedia article using the MediaWiki API."""
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": "1", # Return plain text, not HTML
        "titles": title,
        "format": "json"
    }
    headers = {
        "User-Agent": "RAGEducationalApp/1.0 (contact@example.com)"
    }
    print(f"Fetching '{title}' from Wikipedia...")
    try:
        response = requests.get(WIKI_API_URL, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if "extract" in page_data:
                return page_data["extract"]
        
        print(f"No content found in Wikipedia extract for '{title}'.")
        return ""
    except Exception as e:
        print(f"Error fetching '{title}': {e}")
        return ""

BACKUP_CONTENT = {
    "Generative_artificial_intelligence": (
        "Generative artificial intelligence (generative AI, GenAI, or GAI) is artificial intelligence capable "
        "of generating text, images, videos, or other data using generative models, often in response to prompts. "
        "Generative AI models learn the patterns and structure of their input training data and then generate new data "
        "that has similar characteristics. Pre-training is the initial phase where an LLM is trained on massive datasets "
        "to learn general language patterns, while fine-tuning adapts the model to specific domains."
    ),
    "Retrieval-augmented_generation": (
        "Retrieval-augmented generation (RAG) is an artificial intelligence framework for improving the quality of "
        "LLM responses by grounding the model on external sources of knowledge. RAG stands for Retrieval-Augmented Generation. "
        "The core stages of RAG are: 1. Indexing (processing, chunking, and storing documents in a database), "
        "2. Retrieval (finding relevant document chunks based on a vector query), and 3. Generation (synthesizing a grounded "
        "answer using the context). Unlike pre-training which requires heavy compute to update model weights, RAG dynamically "
        "fetches external information at query time to answer questions."
    ),
    "Large_language_model": (
        "A large language model (LLM) is a computerized language model consisting of an artificial neural network with "
        "many parameters, trained on vast amounts of unlabeled text using self-supervised learning or semi-supervised learning. "
        "LLMs are general-purpose models that can be fine-tuned or adapted for a wide variety of downstream tasks, such as "
        "question answering, text summarization, translation, and code generation. They are the foundation of modern "
        "conversational AI assistants."
    )
}

def load_all_documents(dest_dir: str = DOCUMENTS_DIR):
    """Downloads Wikipedia pages and saves them locally as plain text files, with local backups."""
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created directory: {dest_dir}")
        
    for topic, filename in TOPICS.items():
        filepath = os.path.join(dest_dir, filename)
        if os.path.exists(filepath):
            print(f"File already exists: {filepath}")
            continue
            
        content = fetch_wikipedia_content(topic)
        if not content:
            print(f"Using local backup content for {topic}...")
            content = BACKUP_CONTENT.get(topic, "")
            
        if content:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Saved content to {filepath} ({len(content)} characters)")
        else:
            print(f"Skipping saving for {topic} due to empty content.")

if __name__ == "__main__":
    load_all_documents()
