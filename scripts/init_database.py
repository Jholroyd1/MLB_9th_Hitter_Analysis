"""
Initialize MLB Stats Database
"""

import sqlite3
import os

DB_PATH = "../data/mlb_data.db"
SCHEMA_PATH = "../schema.sql"


def init_database():
    """Create database and tables from schema"""
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Read schema
    with open(SCHEMA_PATH, 'r') as f:
        schema_sql = f.read()
    
    # Create database and execute schema
    print("Creating MLB database...")
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema_sql)
    conn.commit()
    
    # Verify tables created
    tables = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name
    """).fetchall()
    
    print(f"\n✓ Database created: {DB_PATH}")
    print(f"\nTables created ({len(tables)}):")
    for table in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {table[0]}").fetchone()[0]
        print(f"  - {table[0]}: {count} rows")
    
    conn.close()
    print("\n✅ Database initialized successfully!")


if __name__ == "__main__":
    init_database()
