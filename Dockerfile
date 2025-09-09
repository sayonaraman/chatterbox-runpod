# RunPod GPU Serverless Dockerfile for Chatterbox TTS API
# Based on proven Chatterbox-TTS-Server setup with multilingual support
FROM nvidia/cuda:12.8.1-runtime-ubuntu22.04

# Set environment variables (from proven setup)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
ENV HF_HOME=/app/hf_cache

# Install system dependencies (proven working setup)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsndfile1 \
    ffmpeg \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create python symlink
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Install PyTorch with CUDA support (latest compatible version)
RUN pip3 install --no-cache-dir --upgrade pip
RUN pip3 install torch==2.6.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu128

# Copy project files
COPY src/ ./src/
COPY pyproject.toml .
COPY handler.py .
COPY LICENSE .

# Install project with ALL dependencies as original project intended
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
