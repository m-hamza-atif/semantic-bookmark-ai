from fastapi import FastAPI, HTTPException
import psycopg2
from typing import Any

from schemas import BookmarkRequest, BookmarkResponse, BookmarksListResponse, SearchRequest
from scraper import fetch_article
from database import get_db_connection
from ai_service import AIServiceError, chunk_text, get_embedding, generate_rag_answer


app = FastAPI(
    title="Semantic Bookmark AI - Backend API",
    description="An intelligent knowledge base that scrapes web articles, generates vector embeddings via Gemini, and allows conversational search using RAG (Retrieval-Augmented Generation).",
    version="1.0.0"
)

@app.head("/", tags=["Health"])
@app.get("/", tags=["Health"])
def read_root() -> dict[str, str]:
    return {"status": "Bookmark API is running"}

@app.get("/api/v1/bookmarks", response_model=BookmarksListResponse, tags=["Knowledge Base"])
def get_all_bookmarks() -> BookmarksListResponse:
    """Retrieves bookmarks from the database."""
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        # Select metadata of the URLs
        cur.execute("SELECT id, url, title, created_at FROM bookmarks ORDER BY created_at DESC;")
        rows = cur.fetchall()

        # Convert SQL tuples into a list of BookmarkResponse dictionaries
        bookmarks_list = []
        for row in rows:
            bookmarks_list.append(
                BookmarkResponse(
                    id=row[0],
                    url=row[1],
                    title=row[2],
                    created_at=row[3],
                )
            )
        return {"count": len(bookmarks_list), "bookmarks": bookmarks_list}
        
    except psycopg2.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {str(err)}")
    finally:
        if conn:
            conn.close()

@app.post("/api/v1/bookmarks", response_model=BookmarkResponse, tags=["Knowledge Base"])
def create_bookmark(request: BookmarkRequest) -> dict[str, Any]:
    """Fetches content from the provided URL, validates it, and stores it in the database."""
    # 1. Scrape the article
    article = fetch_article(request.url)

    # 2. Check for scraper errors
    if isinstance(article, dict) and "Error" in article:
        raise HTTPException(status_code=400, detail=article["Error"])
    elif not hasattr(article, 'title') or not hasattr(article, 'text'):
        raise HTTPException(status_code=400, detail="Failed to retrieve article content")
    
    title = article.title
    full_text = article.text

    # 3. Save to database
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cur = conn.cursor()
        insert_bookmark_query = """
            INSERT INTO bookmarks(url, title, content)
            VALUES (%s, %s, %s)
            RETURNING id, created_at;
        """ # Returning id and created_at to show metadata of the URL stored
        cur.execute(insert_bookmark_query, (request.url, title, full_text[:500])) # Saving first 500 char as potential preview
        result = cur.fetchone()
        new_id = result[0]
        created_at = result[1]

        # 4. Chunking and embedding
        chunks = chunk_text(full_text)
        insert_chunk_query = """
            INSERT INTO bookmark_chunks(bookmark_id, chunk_text, embedding)
            VALUES (%s, %s, %s);
        """
        
        # 5. Loop through chunks, convert to vectors, and save to database
        for chunk in chunks:
            vector_embedding = get_embedding(chunk)
            cur.execute(insert_chunk_query, (new_id, chunk, vector_embedding))

        # 5. Commit
        conn.commit()
        return {
            "id": new_id, 
            "url": request.url, 
            "title": title, 
            "created_at": created_at
        }

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=400, detail="This URL is already saved in bookmarks.") 
    except psycopg2.Error as err:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Server error: {str(err)}")
    except AIServiceError as err:
        conn.rollback()
        raise HTTPException(status_code=502, detail=str(err))
    finally:
        if conn:
            conn.close()

@app.post("/api/v1/search", tags=["AI Search"])
def ask_questions(request: SearchRequest):
    """Searches and retrieves chunks relevant to user query, acquires a human-readable response, and sends it to the user."""
    # 1. Convert the user's question into a vector
    try:
        query_vector = get_embedding(request.query)
    except Exception as err:
        raise HTTPException(status_code=502, detail=str(err))

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cur = conn.cursor()
        # 2. Find the top 3 most similar chunks based on cosine distance (lower distance = higher similarity)
        search_query = """
            SELECT chunk_text 
            FROM bookmark_chunks 
            ORDER BY embedding <=> %s::vector 
            LIMIT 3;
        """ # Using <=> requires explicit casting to vector to ensure Postgres properly resolves the operands
        # psycopg2 adapts the python list of floats to a string format Postgres can easily cast to a vector using ::vector
        cur.execute(search_query, (str(query_vector),))
        results = cur.fetchall()
        
        if not results:
            return {"answer": "You don't have any bookmarks saved yet!"}

        # Extract the text from the SQL tuple results
        top_chunks = [row[0] for row in results]

        # 3. Generate the human-readable answer
        final_answer = generate_rag_answer(request.query, top_chunks)

        return {
            "query": request.query,
            "answer": final_answer,
            "sources_used": len(top_chunks)
        }

    except psycopg2.Error as err:
        raise HTTPException(status_code=500, detail=f"Database search error: {str(err)}")
    finally:
        if conn:
            conn.close()