import re
from llm_client import LLMClient

class SQLGenerator:
    def __init__(self, llm_client: LLMClient):
        self.client = llm_client

    def generate_sql(self, question: str, schema_context: str) -> str:
        """
        Generates a SQLite query based on a user question and retrieved database schema.
        """
        system_prompt = (
            "You are a strict SQLite expert database administrator. Your job is to generate "
            "syntactically correct SQLite queries. You must output ONLY the raw SQL query. "
            "Do NOT write any explanations, markdown blocks, introductory text, or concluding text."
        )

        prompt = f"""Given the following database schema context:
{schema_context}

Translate the natural language question into a valid, executable SQLite query.
Use only table names and columns present in the schema.
Do NOT use advanced features not supported in SQLite.

Question: {question}

SQL Query:"""

        response = self.client.generate(prompt, system_prompt=system_prompt)
        
        # Clean the response to ensure only the SQL remains
        cleaned_sql = self._clean_sql_response(response)
        return cleaned_sql

    def generate_answer(self, question: str, sql_query: str, sql_result: dict) -> str:
        """
        Generates a natural language answer based on the user's question,
        the generated SQL query, and the database execution results.
        """
        if sql_result.get("error"):
            return f"Error executing query: {sql_result['error']}"

        rows = sql_result.get("rows", [])
        columns = sql_result.get("columns", [])

        # Format execution results for the LLM
        result_str = f"Columns: {columns}\nRows: {rows[:10]}" # Limit rows to avoid flooding context
        if len(rows) > 10:
            result_str += f"\n... (and {len(rows) - 10} more rows)"

        system_prompt = (
            "You are a helpful data analyst. Your job is to explain database query results "
            "to users in simple, conversational natural language. Be concise and accurate."
        )

        prompt = f"""User Question: {question}
SQL Query Executed: {sql_query}
Database Query Results:
{result_str}

Summarize the database results to answer the user's question directly.
"""

        return self.client.generate(prompt, system_prompt=system_prompt)

    def _clean_sql_response(self, response: str) -> str:
        """Helper to extract clean SQL from any potential markdown blocks or extra text."""
        # Remove markdown code blocks if present
        sql_match = re.search(r"```(?:sql)?\s*(.*?)\s*```", response, re.DOTALL | re.IGNORECASE)
        if sql_match:
            sql = sql_match.group(1)
        else:
            sql = response

        # Remove line breaks/comments that can wrap the single-line sql
        sql = sql.strip()
        # Strip trailing semicolon if the generator added it, SQLite doesn't strictly need it
        # but let's keep it clean
        if sql.endswith(";"):
            sql = sql[:-1]
        
        return sql.strip() + ";"

if __name__ == "__main__":
    # Test generator with dummy values
    from database import DatabaseManager
    from retriever import SchemaRetriever
    
    db = DatabaseManager()
    retriever = SchemaRetriever()
    retriever.index_database(db)
    
    client = LLMClient()
    generator = SQLGenerator(client)
    
    q = "Who is the top artist by track count?"
    context = retriever.get_context_string(q)
    
    try:
        sql = generator.generate_sql(q, context)
        print("Generated SQL:", sql)
    except Exception as e:
        print("Generation test failed:", e)
