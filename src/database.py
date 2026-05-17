import sqlite3
from pathlib import Path

DB_PATH = Path("data/processed/pharmasense.db")

def get_connection():
    """Returns a SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    """Creates all tables from schema.sql."""
    schema_path = Path("sql/schema.sql")
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
    
    # Ensure the data/processed directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = get_connection()
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully.")
    print(f"✓ Database created at: {DB_PATH}")

if __name__ == "__main__":
    init_db()