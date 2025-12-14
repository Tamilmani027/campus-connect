import sys
from sqlalchemy import text
from backend_fastapi.database import engine

def fix_schema():
    print("Attempting to add 'category' column to 'resources' table...")
    # Using engine.connect() with text() execution
    try:
        # Use a raw connection to avoid SQLAlchemy transaction weirdness for DDL if possible, 
        # or just try executing without explicit commit first if it errors.
        # But actually, with engine.begin() it should commit.
        with engine.begin() as conn:
             # Check if column exists
            result = conn.execute(text("SHOW COLUMNS FROM resources LIKE 'category'"))
            if result.fetchone():
                print("Column 'category' already exists.")
            else:
                conn.execute(text("ALTER TABLE resources ADD COLUMN category VARCHAR(50) DEFAULT 'GENERAL'"))
                print("Successfully added 'category' column.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_schema()
