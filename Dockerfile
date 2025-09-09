# RunPod GPU Serverless Dockerfile for Chatterbox TTS API
FROM runpod/pytorch:2.4.0-py3.11-cuda12.1.1-devel-ubuntu22.04

# Set working directory
WORKDIR /app

# Install minimal system dependencies for GPU TTS
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with GPU optimizations
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy only necessary files for API (exclude GUI apps)
COPY src/ ./src/
COPY pyproject.toml .
COPY handler.py .
COPY LICENSE .

# Install Chatterbox in production mode
RUN pip install --no-deps -e .

# Pre-download models to GPU cache for faster cold starts
# Download to CPU first, then they'll be moved to GPU on first use
RUN python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}, Devices: {torch.cuda.device_count()}')"
RUN python -c "from chatterbox.tts import ChatterboxTTS; ChatterboxTTS.from_pretrained(device='cpu')" || echo "English model download failed"
RUN python -c "from chatterbox.mtl_tts import ChatterboxMultilingualTTS; ChatterboxMultilingualTTS.from_pretrained(device='cpu')" || echo "Multilingual model download failed"

# Set environment variables for GPU optimization
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0
ENV TORCH_CUDA_ARCH_LIST="7.5;8.0;8.6;8.9;9.0"

# RunPod serverless handler
CMD ["python", "handler.py"]
