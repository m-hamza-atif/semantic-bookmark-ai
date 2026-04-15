# 🔖 Semantic Bookmark AI

🔗 **Live Frontend App (Streamlit):** [Click here to use the AI](https://semantic-bookmark-ai.streamlit.app)
⚙️ **Live Backend API (Swagger UI):** [Click here to view the endpoints](https://semantic-bookmark-ai.onrender.com/docs)

---

Semantic Bookmark AI is a full-stack, AI-powered knowledge base that allows users to save web articles and query them using natural language.

Based on a 3-Tier Architecture, it combines a highly concurrent **FastAPI** backend with a **Streamlit** visual client. It utilizes **Google Gemini** for vector embeddings and text generation, and **Supabase (PostgreSQL + pgvector)** for mathematically performing Cosine Similarity searches to answer user queries via Retrieval-Augmented Generation (RAG).

## ⚡ Key Features

* **Intelligent Web Scraping:** Automatically extracts readable text from URLs while gracefully handling edge cases such as invalid URLs, timeouts, blocked pages, and non-HTML content.
* **Semantic Search:** Understands the meaning of your questions to find exact answers buried in massive articles, rather than  matching keywords.
* **Token-Based Chunking:** Uses `tiktoken` library to slice articles into optimal, overlapping chunks (300 tokens/50 overlap) to preserve context.
* **Gemini Models:** Powered by `gemini-embedding-001` for high-dimensional vectorization and `gemini-2.5-flash` for final answer generation.
* **Robust Database Security:** Raw SQL implementation with connection pooling, graceful transaction rollbacks, and protection against prompt-injection attacks.
* **Modern API Design:** Fully documented Swagger UI at `/docs`.

## 🧮 Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| Backend API | FastAPI | High-performance and async-ready REST API. |
| Frontend UI | Streamlit | Stateless, interactive web client for the API. |
| Database | Supabase + pgvector | Cloud PostgreSQL storing 768-dimensional embeddings. |
| AI SDK | Google GenAI SDK | Generates vectors and human-readable chat responses. |
| Package Manager | uv | Dependency resolution, and virtual environments. |

## 📂 Complete Project Structure

```text
semantic-bookmark-ai/
├── ai_service.py         # Gemini API logic, Prompt Engineering, and Tiktoken Chunking
├── app.py                # Streamlit Frontend Client
├── database.py           # Raw psycopg2 Supabase Connection & Table Initialization
├── main.py               # FastAPI Router & CRUD Endpoints
├── schemas.py            # Pydantic Objects
├── scraper.py            # Web Scraping & Error Handling Logic
├── requirements.txt      # Production Dependencies for Cloud Deployment
├── pyproject.toml        # Modern Python Project Metadata
└── README.md             # Project Documentation
```

## Prerequisites

- Python 3.12+
* A [Supabase](https://supabase.com/) Project (with `pgvector` enabled)
* A [Gemini API Key](https://aistudio.google.com/)
- `uv` installed

## Environment Variables

Create a `.env` file in the project root directory and add your credentials:

```env
DATABASE_URL="postgresql://USER:PASSWORD@HOST:PORT/DBNAME"
GEMINI_API_KEY="your_gemini_api_key"
```

Notes:
- `DATABASE_URL` is used by `database.py` and `main.py`.
- The GenAI client in `ai_service.py` reads `GEMINI_API_KEY` from environment variables.

## Setup and Run

1. Clone & Setup Environment:

```bash
git clone https://github.com/m-hamza-atif/semantic-bookmark-ai.git
cd semantic-bookmark-ai
```

2. Install dependencies:

```bash
uv sync
```

3. Initialize database tables once:

```bash
uv run python database.py
```

4. Start backend API:

```bash
uv run uvicorn main:app --reload
```

5. Start frontend app in a second terminal:

```bash
uv run streamlit run app.py
```

Local URLs:
- API health: `http://127.0.0.1:8000/`
- Swagger docs: `http://127.0.0.1:8000/docs`
- Streamlit UI: `http://localhost:8501`

## API Summary

- `GET /` and `HEAD /`: Health check
- `GET /api/v1/bookmarks`: List saved bookmarks
- `POST /api/v1/bookmarks`: Scrape and save a bookmark, then generate and store embeddings
- `POST /api/v1/search`: Retrieve top matching chunks and generate an accurate answer

## Troubleshooting

If a `uv run ...` command fails on Windows with `uv trampoline failed to canonicalize script path`, reinstall the failing launcher package:

```bash
uv sync --reinstall-package <package-name>
```
For example:
```bash
uv sync --reinstall-package streamlit
```

## ✍️ Author
Muhammad Hamza Atif
