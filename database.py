import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extensions import connection as PsycopgConnection

# Load the environment variables from the .env file
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")
EMBEDDING_DIMENSION=768 # Change these in ai_service.py too if changed here

def get_db_connection() -> PsycopgConnection | None:
    """Returns a psycopg2 database connection."""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except psycopg2.Error as err:
        print(f"Database connection error: {str(err)}")
        return None

def init_db() -> None:
    """Creates the bookmarks table if it doesn't exist."""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()

        # SQL Schema
        create_table_query = """
        CREATE TABLE IF NOT EXISTS bookmarks(
            id SERIAL PRIMARY KEY,
            url TEXT NOT NULL UNIQUE,
            title TEXT,
            content TEXT,
            session_id TEXT DEFAULT 'demo_user',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        cur.execute(create_table_query)

        create_chunks_table_query = f"""
        CREATE TABLE IF NOT EXISTS bookmark_chunks(
            id SERIAL PRIMARY KEY,
            bookmark_id INTEGER REFERENCES bookmarks(id) ON DELETE CASCADE,
            chunk_text TEXT NOT NULL,
            embedding vector({EMBEDDING_DIMENSION})
        );
        """ # Vector dimensions are 768 for Gemini API
        cur.execute(create_chunks_table_query)

        conn.commit()
        print("Database initialized successfully.")
        
    except psycopg2.Error as err:
        print(f"Error creating table: {str(err)}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

# Run this file directly to test the connection and create the table
if __name__ == "__main__":
    init_db()