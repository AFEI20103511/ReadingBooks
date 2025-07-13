# Import FastAPI components for building the web API
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
# Import CORS middleware to allow cross-origin requests from frontend
from fastapi.middleware.cors import CORSMiddleware
# Import uvicorn for running the FastAPI server
import uvicorn
import json
import asyncio

# Import our organized modules
from .modules.pdf_parser import extract_text_from_pdf, get_text_preview
from .modules.llm_pipeline import process_text_with_llm
from .modules.utils import validate_file_type
from .config.settings import ALLOWED_ORIGINS, TEXT_PREVIEW_LENGTH

# Create FastAPI application instance
app = FastAPI()

# Configure CORS (Cross-Origin Resource Sharing) to allow frontend requests
# This is necessary because frontend runs on localhost:3000 and backend on localhost:8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,           # Allow requests from React development server
    allow_credentials=True,                   # Allow credentials (cookies, headers)
    allow_methods=["*"],                     # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],                     # Allow all headers
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Handle PDF file upload from frontend.
    
    Args:
        file: The uploaded PDF file from the frontend
        
    Returns:
        JSON response with filename, text preview, entities, and relationships
    """
    # Validate file type
    if not validate_file_type(file.filename):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Read the uploaded PDF file into memory
    contents = await file.read()
    
    # Extract text from PDF using our organized module
    text = extract_text_from_pdf(contents)
    if text is None:
        raise HTTPException(status_code=400, detail="Failed to extract text from PDF")
    
    # Process text with LLM pipeline to extract entities and relationships
    llm_results = process_text_with_llm(text)
    
    # Get text preview for verification
    preview = get_text_preview(text, TEXT_PREVIEW_LENGTH)
    
    # Return comprehensive results
    return {
        "filename": file.filename,
        "preview": preview,
        "entities": llm_results["entities"],
        "relationships": llm_results["relationships"],
        "text_length": llm_results["text_length"]
    }

@app.post("/upload-with-progress")
async def upload_file_with_progress(file: UploadFile = File(...)):
    """
    Handle PDF file upload with real-time progress updates.
    
    Args:
        file: The uploaded PDF file from the frontend
        
    Returns:
        Streaming response with progress updates and final results
    """
    async def progress_generator():
        # Validate file type
        if not validate_file_type(file.filename):
            yield f"data: {json.dumps({'error': 'Only PDF files are supported'})}\n\n"
            return
        
        # Progress: File uploaded (10%)
        yield f"data: {json.dumps({'progress': 10, 'message': 'File uploaded successfully'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Read the uploaded PDF file into memory
        contents = await file.read()
        
        # Progress: File read (20%)
        yield f"data: {json.dumps({'progress': 20, 'message': 'PDF file read'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Extract text from PDF using our organized module
        text = extract_text_from_pdf(contents)
        if text is None:
            yield f"data: {json.dumps({'error': 'Failed to extract text from PDF'})}\n\n"
            return
        
        # Progress: Text extracted (40%)
        yield f"data: {json.dumps({'progress': 40, 'message': f'Text extracted ({len(text)} characters)'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Process text with LLM pipeline to extract entities and relationships
        # Progress: LLM processing started (50%)
        yield f"data: {json.dumps({'progress': 50, 'message': 'Processing with AI...'})}\n\n"
        await asyncio.sleep(0.1)
        
        llm_results = process_text_with_llm(text)
        
        # Progress: LLM processing complete (80%)
        entity_count = len(llm_results["entities"])
        yield f"data: {json.dumps({'progress': 80, 'message': f'AI processing complete. Found {entity_count} people'})}\n\n"
        await asyncio.sleep(0.1)
        
        # Get text preview for verification
        preview = get_text_preview(text, TEXT_PREVIEW_LENGTH)
        
        # Progress: Complete (100%)
        final_result = {
            "filename": file.filename,
            "preview": preview,
            "entities": llm_results["entities"],
            "relationships": llm_results["relationships"],
            "text_length": llm_results["text_length"]
        }
        
        yield f"data: {json.dumps({'progress': 100, 'message': 'Processing complete!', 'result': final_result})}\n\n"
    
    return StreamingResponse(
        progress_generator(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.get("/")
def read_root():
    """
    Root endpoint to verify the backend is running.
    
    Returns:
        Simple JSON message confirming backend status
    """
    return {"message": "Backend is running!"}

def run():
    """
    Function to start the FastAPI server using uvicorn.
    This is called by main.py to run the backend.
    """
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True) 