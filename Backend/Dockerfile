FROM python:3.11-slim

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
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .

# Upgrade pip and install wheel first
RUN pip install --upgrade pip setuptools wheel

# Install PyTorch CPU (lighter version)
RUN pip install torch==2.1.0+cpu torchvision==0.16.0+cpu torchaudio==2.1.0+cpu -f https://download.pytorch.org/whl/torch_stable.html

# Install other requirements
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/models /app/rag_storage /app/logs /app/temp

# Copy application code
COPY . .

# Set ownership
RUN chown -R app:app /app

# Switch to app user
USER app

# Create a simple model download script
RUN echo '#!/bin/bash\n\
echo "Downloading models in background..."\n\
python -c "\
import warnings; warnings.filterwarnings(\"ignore\")\n\
try:\n\
    from transformers import AutoTokenizer\n\
    print(\"Downloading Phi-2 tokenizer...\")\n\
    AutoTokenizer.from_pretrained(\"microsoft/phi-2\", cache_dir=\"/app/models\")\n\
    print(\"Tokenizer downloaded\")\n\
except Exception as e:\n\
    print(f\"Tokenizer download failed: {e}\")\n\
try:\n\
    from sentence_transformers import SentenceTransformer\n\
    print(\"Downloading embedding model...\")\n\
    SentenceTransformer(\"all-MiniLM-L6-v2\", cache_folder=\"/app/models\")\n\
    print(\"Embedding model downloaded\")\n\
except Exception as e:\n\
    print(f\"Embedding model download failed: {e}\")\n\
" &' > /app/download_models.sh && chmod +x /app/download_models.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start script
CMD ["/bin/bash", "-c", "/app/download_models.sh && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1"]