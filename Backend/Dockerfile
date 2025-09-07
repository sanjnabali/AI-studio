FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    ffmpeg \
    libsm6 \
    libxext6 \
    libfontconfig1 \
    libxrender1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install PyTorch with CPU support (smaller image)
RUN pip install torch==2.1.0+cpu torchvision==0.16.0+cpu torchaudio==2.1.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/models /app/rag_storage /app/logs /app/temp && \
    chown -R app:app /app

# Switch to non-root user
USER app

# Download and cache models during build
RUN python -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
import whisper

print('Downloading models...')

# Download Phi-2 model
try:
    tokenizer = AutoTokenizer.from_pretrained('microsoft/phi-2', cache_dir='/app/models')
    print('Phi-2 tokenizer downloaded')
except Exception as e:
    print(f'Phi-2 download failed: {e}')

# Download embedding model
try:
    SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', cache_folder='/app/models')
    print('Embedding model downloaded')
except Exception as e:
    print(f'Embedding model download failed: {e}')

print('Model downloads completed')
"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]