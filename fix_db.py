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

            # Add streak columns to students table
            print("Checking 'students' table for streak columns...")
            res_streak = conn.execute(text("SHOW COLUMNS FROM students LIKE 'current_streak'"))
            if not res_streak.fetchone():
                conn.execute(text("ALTER TABLE students ADD COLUMN current_streak INT DEFAULT 0"))
                print("Added 'current_streak' column.")
            
            res_date = conn.execute(text("SHOW COLUMNS FROM students LIKE 'last_active_date'"))
            if not res_date.fetchone():
                conn.execute(text("ALTER TABLE students ADD COLUMN last_active_date DATE DEFAULT NULL"))
                print("Added 'last_active_date' column.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_schema()
