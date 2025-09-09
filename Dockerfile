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

# Copy project files (same structure as original)
COPY src/ ./src/
COPY pyproject.toml .
COPY handler.py .
COPY LICENSE .

# Install EXACTLY as original project recommends
RUN pip install --no-cache-dir --upgrade pip
RUN pip install -e .

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
