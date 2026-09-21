from database import DatabaseManager

class SQLExecutor:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def execute(self, sql_query: str) -> dict:
        """
        Validates and executes the generated SQL query.
        Ensures queries are read-only for safety.
        """
        # Clean query whitespace for analysis
        cleaned_query = sql_query.strip().upper()
        
        # Simple read-only guardrails
        forbidden_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER", "REPLACE", "TRUNCATE"]
        
        for keyword in forbidden_keywords:
            # Check for keyword surrounded by word boundaries to avoid false positives (e.g. "TrackId" containing "id")
            import re
            if re.search(r'\b' + keyword + r'\b', cleaned_query):
                return {
                    "columns": [],
                    "rows": [],
                    "error": f"Security Exception: Operation '{keyword}' is prohibited. Only SELECT operations are allowed."
                }
        
        if not cleaned_query.startswith("SELECT"):
            # Some queries might start with WITH, which is okay
            if not cleaned_query.startswith("WITH"):
                return {
                    "columns": [],
                    "rows": [],
                    "error": "Security Exception: SQL query must begin with SELECT or WITH."
                }

        # Run query via DatabaseManager
        return self.db.execute_query(sql_query)

if __name__ == "__main__":
    db = DatabaseManager()
    executor = SQLExecutor(db)
    
    # Test safe execution
    print("Testing safe query:")
    print(executor.execute("SELECT Name FROM Artist LIMIT 3;"))
    
    # Test unsafe query
    print("\nTesting unsafe query:")
    print(executor.execute("DROP TABLE Artist;"))
