# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY src/ ./src/

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI app
CMD ["python", "-m", "backend.src.app"] 