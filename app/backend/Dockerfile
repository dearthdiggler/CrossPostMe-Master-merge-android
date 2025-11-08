# Backend Dockerfile for FastAPI + Uvicorn
FROM python:3.11-slim

# Set the working directory to a standard location
WORKDIR /app

# Copy and install requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend source code into a subdirectory
# This allows Python to treat 'backend' as a package
COPY . /app/backend

# Set the PYTHONPATH to include the root /app directory
ENV PYTHONPATH="${PYTHONPATH}:/app"

EXPOSE 8000
