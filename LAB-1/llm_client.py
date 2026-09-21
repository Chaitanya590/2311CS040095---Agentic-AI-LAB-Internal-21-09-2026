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
            # Check if Ollama is responsive
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
        
        # 1. SQL Generation Mocking
        if "sql query:" in prompt_lower or "sqlite query" in prompt_lower:
            if "artists" in prompt_lower and "how many" in prompt_lower:
                return "SELECT COUNT(*) FROM Artist;"
            elif "top 3 longest tracks" in prompt_lower or "longest tracks" in prompt_lower:
                return "SELECT Name, Milliseconds FROM Track ORDER BY Milliseconds DESC LIMIT 3;"
            elif "customers" in prompt_lower and "canada" in prompt_lower:
                return "SELECT COUNT(*) FROM Customer WHERE Country = 'Canada';"
            elif "albumid 10" in prompt_lower:
                return "SELECT Title FROM Album WHERE AlbumId = 10;"
            elif "employees hired in 2002" in prompt_lower or "employee" in prompt_lower and "2002" in prompt_lower:
                return "SELECT EmployeeId, LastName FROM Employee WHERE HireDate LIKE '2002%';"
            elif "top 5 tracks" in prompt_lower:
                return "SELECT Name FROM Track LIMIT 5;"
            elif "customers" in prompt_lower and "brazil" in prompt_lower:
                return "SELECT COUNT(*) FROM Customer WHERE Country = 'Brazil';"
            else:
                # Default generic SQL fallback
                return "SELECT Name FROM Artist LIMIT 5;"
                
        # 2. Answer Summarization Mocking
        if "database query results:" in prompt_lower or "results:" in prompt_lower:
            if "count(*)" in prompt_lower:
                if "artist" in prompt_lower:
                    return "There are 275 artists in the database."
                elif "customer" in prompt_lower:
                    return "There are 8 customers from Canada."
            elif "albumid 10" in prompt_lower or "title" in prompt_lower:
                return "The title of the album with AlbumId 10 is 'Audioslave'."
            elif "employeeid" in prompt_lower or "hiredate" in prompt_lower:
                return "The employees hired in 2002 are Adams (ID 1), Edwards (ID 2), and Peacock (ID 3)."
            elif "longest tracks" in prompt_lower or "milliseconds" in prompt_lower:
                return "The top 3 longest tracks are: 1. 'Occupation / Precipice' (5,286,953 ms), 2. 'Through a Looking Glass' (5,088,838 ms), and 3. 'Greetings from Earth, Pt. 1' (2,960,293 ms)."
            
            return "Here are the query results from the database."

        return "This is a mock response from the LLM client since no active API key or local Ollama was detected."

if __name__ == "__main__":
    client = LLMClient()
    print(f"Active Provider: {client.provider} ({client.model_name})")
    response = client.generate("How many artists are there in the database? SQL Query:")
    print("Response:", response)

