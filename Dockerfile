# RunPod GPU Serverless Dockerfile for Chatterbox TTS API
# Using EXACT environment as original project: Python 3.11 + Debian 11
FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies (same as original project environment)
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    ffmpeg \
    libsndfile1 \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch first (CPU version for building, will work on GPU)
RUN pip install --no-cache-dir --upgrade pip
RUN pip install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cpu

# Install other dependencies manually to avoid conflicts
RUN pip install --no-cache-dir \
    "numpy>=1.24.0,<1.26.0" \
    librosa==0.11.0 \
    transformers==4.46.3 \
    diffusers==0.29.0 \
    conformer==0.3.2 \
    safetensors==0.5.3 \
    "pkuseg==0.0.25" \
    pykakasi==2.3.0 \
    resemble-perth==1.0.1 \
    s3tokenizer

# Copy project files
COPY src/ ./src/
COPY pyproject.toml .
COPY handler.py .
COPY LICENSE .

# Install project without dependencies (since we installed them manually)
RUN pip install --no-deps -e .

# Install RunPod SDK
RUN pip install runpod>=1.5.0

# Pre-download models for faster cold starts
RUN python -c "from chatterbox.tts import ChatterboxTTS; ChatterboxTTS.from_pretrained(device='cpu')" || echo "English model download failed"
RUN python -c "from chatterbox.mtl_tts import ChatterboxMultilingualTTS; ChatterboxMultilingualTTS.from_pretrained(device='cpu')" || echo "Multilingual model download failed"

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# RunPod serverless handler
CMD ["python", "handler.py"]
