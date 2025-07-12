from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import uvicorn

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Read the uploaded PDF file into memory
    contents = await file.read()
    text = ""
    try:
        with pdfplumber.open(file.file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        return {"error": f"Failed to extract text: {str(e)}"}
    # Return the first 500 characters for preview
    return {"filename": file.filename, "preview": text[:500]}

@app.get("/")
def read_root():
    return {"message": "Backend is running!"}

def run():
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True) 