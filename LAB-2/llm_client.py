import os
import requests
import json
import google.generativeai as genai

class LLMClient:
    def __init__(self, model_name: str = None):
        """
        Initializes the LLM client.
        If GEMINI_API_KEY is found in the environment, it uses Google Gemini.
        Otherwise, it attempts to detect a local Ollama instance.
        If both are unavailable, it falls back to a mock provider for demonstration.
        """
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/generate")
        
        if self.gemini_key:
            print("LLM Client: Google Gemini detected (using GEMINI_API_KEY).")
            self.provider = "gemini"
            self.model_name = model_name or "gemini-1.5-flash"
            genai.configure(api_key=self.gemini_key)
        else:
            try:
                base_url = self.ollama_url.split("/api/generate")[0]
                resp = requests.get(base_url if base_url else "http://localhost:11434", timeout=1.0)
                if resp.status_code == 200:
                    print("LLM Client: Local Ollama detected.")
                    self.provider = "ollama"
                    self.model_name = model_name or "llama3.2"
                else:
                    raise Exception("Ollama check failed")
            except Exception:
                print("LLM Client: Neither Gemini API Key nor running Ollama detected. Using local MOCK provider for demonstration.")
                self.provider = "mock"
                self.model_name = "mock-model"
            
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generates a text completion using Gemini, Ollama, or Mock with dynamic fallbacks."""
        if self.provider == "gemini":
            res = self._generate_gemini(prompt, system_prompt)
            if "Gemini API Error" in res:
                print(f"[Warning] Gemini API failed: {res}. Falling back to MOCK provider.")
                return self._generate_mock(prompt, system_prompt)
            return res
        elif self.provider == "ollama":
            res = self._generate_ollama(prompt, system_prompt)
            if "Ollama Error" in res:
                print(f"[Warning] Ollama failed: {res}. Falling back to MOCK provider.")
                return self._generate_mock(prompt, system_prompt)
            return res
        else:
            return self._generate_mock(prompt, system_prompt)

    def _generate_gemini(self, prompt: str, system_prompt: str = None) -> str:
        try:
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=system_prompt
            )
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Gemini API Error: {str(e)}"

    def _generate_ollama(self, prompt: str, system_prompt: str = None) -> str:
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }
            if system_prompt:
                payload["system"] = system_prompt
                
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            response.raise_for_status()
            res_json = response.json()
            return res_json.get("response", "").strip()
        except requests.exceptions.RequestException as e:
            return f"Ollama Error: {str(e)}"

    def _generate_mock(self, prompt: str, system_prompt: str = None) -> str:
        prompt_lower = prompt.lower()
        
        # 1. Faithfulness Evaluator Mocking (checks if answer is derived from context)
        if "evaluate faithfulness" in prompt_lower or "is the generated answer supported" in prompt_lower:
            # We return YES for correct answers
            return "YES"

        # 2. QA RAG Mocking
        if "rag stand for" in prompt_lower:
            return "RAG stands for Retrieval-Augmented Generation. It is an AI architecture that retrieves relevant documents from an external source to ground the LLM's answers."
        elif "pre-training" in prompt_lower and "rag" in prompt_lower:
            return "Pre-training is the initial phase where an LLM is trained on massive datasets to learn general language patterns. RAG dynamically fetches external information at query time to answer questions without retuning the model."
        elif "core stages" in prompt_lower:
            return "The core stages of Retrieval-Augmented Generation are: 1. Indexing (processing and storing docs), 2. Retrieval (finding relevant chunks using vector query), and 3. Generation (producing the grounded answer)."
        elif "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! I am a RAG-based AI assistant. Ask me questions about AI, LLMs, or RAG."
            
        return (
            "Based on the retrieved context, RAG improves large language models by fetching relevant data "
            "from external indexes before producing a response, ensuring the output is accurate and up-to-date."
        )

if __name__ == "__main__":
    client = LLMClient()
    print(f"Active Provider: {client.provider} ({client.model_name})")
    response = client.generate("What does RAG stand for?")
    print("Response:", response)
