# 🔖 Semantic Bookmark AI

Semantic Bookmark AI is a full-stack, AI-powered knowledge base that allows users to save web articles and query them using natural language.

Built with a Modern 3-Tier Architecture, it combines a highly concurrent **FastAPI** backend with a **Streamlit** visual client. It utilizes **Google Gemini** for vector embeddings and text generation, and **Supabase (PostgreSQL + pgvector)** for mathematically performing Cosine Similarity searches via Retrieval-Augmented Generation (RAG).

## ⚡ Key Features

* **Intelligent Web Scraping:** Automatically extracts readable text from URLs while gracefully handling edge cases such as Timeouts, 404 Not Found, and Invalid Schemas.
* **Semantic Search (RAG):** Understands the meaning of your questions to find exact answers buried in massive articles, rather than  matching keywords .
* **Optimized AI Pipeline:**
    * **Token-Based Chunking:** Uses the C-based `tiktoken` library to slice articles into mathematically optimal, overlapping chunks (300 tokens/50 overlap) to preserve context.
    * **State-of-the-Art Models:** Powered by `gemini-embedding-001` for high-dimensional vectorization and `gemini-2.5-flash` for final answer generation.
* **Robust Database Security:** Raw SQL implementation with connection pooling, graceful transaction rollbacks, and protection against prompt-injection attacks.
* **Modern API Design:** Fully documented Swagger UI (`/docs`) with strictly typed Pydantic data schemas (`schemas.py`).

## 🧮 Tech Stack & Architecture

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | `FastAPI` (Python) | High-performance and async-ready REST API. |
| **Vector Database** | `Supabase` + `pgvector` | Cloud PostgreSQL storing 768-dimensional embeddings. |
| **AI / LLM** | `Google GenAI SDK` | Generates vectors and human-readable chat responses. |
| **Frontend UI** | `Streamlit` | Stateless, interactive web client for the API. |
| **Package Manager** | `uv` | Fast Rust-based dependency resolution. |

## 📂 Complete Project Structure

```text
bookmark-api/
├── .venv/                # Isolated virtual environment (Managed by uv)
├── .env                  # Environment variables (Ignored in Git)
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
## ⚙️ How to Build & Run Locally

This project uses [uv](https://github.com/astral-sh/uv), an extremely fast Python package manager that automatically isolates dependencies in a local `.venv` folder, keeping your system perfectly clean.

**1. Prerequisites:**

* Python 3.10+
* A [Supabase](https://supabase.com/) Project (with `pgvector` enabled)
* A [Google Gemini API Key](https://aistudio.google.com/)

**2. Clone & Setup Environment:**

```bash
git clone https://github.com/m-hamza-atif/semantic-bookmark-api.git
cd semantic-bookmark-api
```

**3. Configure API Keys:**

Create a .env file in the root directory and add your credentials:
```code snippet
DATABASE_URL="postgresql://postgres.[YOUR_PROJECT]:[YOUR_PASSWORD]@[aws-0-region.pooler.supabase.com:6543/postgres](https://aws-0-region.pooler.supabase.com:6543/postgres)"
GEMINI_API_KEY="your_gemini_api_key"
```

**4. Install Dependencies:**

```bash
uv sync
```
**5. Initialize the Database:**

Run this once to create the PostgreSQL tables and vector schemas:
```bash
uv run python database.py
```
**6. Run the Microservices:**

You will need two terminal windows.
- **Terminal 1 (Backend API):**
```bash
uv run uvicorn main:app --reload
```
*(Swagger API documentation will be available at https://www.google.com/search?q=http://127.0.0.1:8000/docs)*
- **Terminal 2 (Frontend Client):**
```bash
uv run streamlit run app.py
```
*(The UI will open in your browser at http://localhost:8501)*

If any `uv run <command>` fails with `uv trampoline failed to canonicalize script path`, fix that package launcher with:
```bash
uv sync --reinstall-package <package-name>
```
For example:
```bash
uv sync --reinstall-package streamlit
```

## ✍️ Author
Muhammad Hamza Atif - BS Software Engineering, FAST NUCES Islamabad