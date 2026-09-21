import os
import sqlite3
import requests

CHINOOK_URL = "https://github.com/lerocha/chinook-database/raw/master/ChinookDatabase/DataSources/Chinook_Sqlite.sqlite"
DB_FILE = "Chinook_Sqlite.sqlite"

def download_database(dest_path: str = DB_FILE):
    """Downloads the Chinook SQLite database if it does not already exist."""
    if os.path.exists(dest_path):
        print(f"Database already exists at {dest_path}")
        return dest_path
    
    print(f"Downloading Chinook database from {CHINOOK_URL}...")
    response = requests.get(CHINOOK_URL, stream=True)
    response.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Database downloaded successfully to {dest_path}")
    return dest_path

class DatabaseManager:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            download_database(self.db_path)

    def get_connection(self):
        # Establish a secure, read-only connection to prevent LLM-generated write operations
        db_uri = f"file:{self.db_path}?mode=ro"
        return sqlite3.connect(db_uri, uri=True)

    def execute_query(self, query: str):
        """Executes a query and returns column names and row results."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return {"columns": columns, "rows": rows, "error": None}
        except sqlite3.Error as e:
            return {"columns": [], "rows": [], "error": str(e)}
        finally:
            conn.close()

    def get_table_names(self):
        """Returns all user table names in the database."""
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        res = self.execute_query(query)
        return [row[0] for row in res["rows"]]

    def get_table_ddl(self, table_name: str) -> str:
        """Returns the CREATE TABLE statement (DDL) for a table."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name = ?;", (table_name,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else ""

    def get_table_sample_rows(self, table_name: str, limit: int = 3) -> list:
        """Returns the first few rows of a table to serve as examples."""
        query = f"SELECT * FROM `{table_name}` LIMIT {limit};"
        res = self.execute_query(query)
        return res["rows"]

    def get_db_schema_summary(self) -> dict:
        """Returns a dict mapping table names to their DDL schema."""
        summary = {}
        for table in self.get_table_names():
            ddl = self.get_table_ddl(table)
            summary[table] = ddl
        return summary

if __name__ == "__main__":
    # Test execution
    db = DatabaseManager()
    tables = db.get_table_names()
    print("Tables in Chinook Database:", tables)
    if tables:
        print("\nDDL for first table:")
        print(db.get_table_ddl(tables[0]))
        print("\nSample rows:")
        print(db.get_table_sample_rows(tables[0], 2))
