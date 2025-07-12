# Backend

This is the backend service for the ReadingBooks web app. It provides API endpoints for uploading and processing book files (PDF, etc.), extracting people and relationships using LLMs, and serving data to the frontend.

## Structure

- `src/` - Source code for the FastAPI backend
  - `app.py` - FastAPI app entry point
  - `pdf_parser.py` - PDF parsing utilities (using pdfplumber)
  - `llm_pipeline.py` - LLM pipeline (using LangChain, Ollama, or cloud APIs)
  - `utils.py` - Utility functions
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker build instructions

## Running Locally

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the backend:
   ```sh
   python -m backend.src.app
   ```

## Running with Docker

1. Build the Docker image:
   ```sh
   docker build -t readingbooks-backend .
   ```
2. Run the container:
   ```sh
   docker run -p 8000:8000 readingbooks-backend
   ```

Or use `docker-compose` from the project root to run both backend and frontend:
```sh
docker-compose up --build
``` 