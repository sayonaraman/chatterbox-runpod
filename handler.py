"""
RunPod GPU Serverless Handler for Chatterbox TTS API
Optimized for GPU-only serverless deployment with maximum performance
"""

import runpod
import torch
import torchaudio
import base64
import tempfile
import os
from typing import Optional, Dict, Any
import logging
import gc

# Configure logging for production
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global model instances (loaded once on container start)
english_model = None
multilingual_model = None
device = None

def load_models():
    """Load TTS models on container startup with GPU optimization"""
    global english_model, multilingual_model, device
    
    try:
        # Force GPU usage for serverless
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA not available! This container requires GPU.")
        
        device = "cuda"
        torch.cuda.empty_cache()  # Clear GPU cache
        
        logger.info(f"GPU Device: {torch.cuda.get_device_name()}")
        logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
        
        # Load models with GPU optimization
        from chatterbox.tts import ChatterboxTTS
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        
        logger.info("Loading English model to GPU...")
        english_model = ChatterboxTTS.from_pretrained(device=device)
        
        logger.info("Loading Multilingual model to GPU...")
        multilingual_model = ChatterboxMultilingualTTS.from_pretrained(device=device)
        
        # Optimize for inference
        english_model.eval()
        multilingual_model.eval()
        
        # Enable GPU optimizations
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
        
        logger.info("✅ All models loaded successfully on GPU")
        logger.info(f"GPU Memory Used: {torch.cuda.memory_allocated() / 1024**3:.1f}GB")
        
    except Exception as e:
        logger.error(f"❌ Error loading models: {str(e)}")
        raise e

def audio_to_base64(audio_tensor: torch.Tensor, sample_rate: int = 22050) -> str:
    """Convert audio tensor to base64 encoded WAV"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            # Save audio to temporary file
            torchaudio.save(tmp_file.name, audio_tensor.cpu(), sample_rate)
            
            # Read file and encode to base64
            with open(tmp_file.name, 'rb') as f:
                audio_data = f.read()
            
            # Clean up temporary file
            os.unlink(tmp_file.name)
            
            # Encode to base64
            return base64.b64encode(audio_data).decode('utf-8')
            
    except Exception as e:
        logger.error(f"Error converting audio to base64: {str(e)}")
        raise e

def base64_to_audio_file(base64_data: str) -> str:
    """Convert base64 audio data to temporary file path"""
    try:
        # Decode base64
        audio_data = base64.b64decode(base64_data)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_file.write(audio_data)
            return tmp_file.name
            
    except Exception as e:
        logger.error(f"Error converting base64 to audio file: {str(e)}")
        raise e

def handler(job: Dict[str, Any]) -> Dict[str, Any]:
    """
    GPU-optimized RunPod handler for TTS generation
    
    Input format:
    {
        "text": "Text to synthesize",
        "language_id": "en|ru|zh|..." (optional, for multilingual),
        "audio_prompt": "base64_audio" (optional, for voice cloning),
        "exaggeration": 0.5 (optional, 0.0-1.0),
        "cfg_weight": 0.5 (optional, 0.0-1.0),
        "model_type": "english|multilingual" (default: "english")
    }
    
    Returns: {"audio": "base64_wav", "sample_rate": 22050, "duration": 2.5, ...}
    """
    
    start_time = torch.cuda.Event(enable_timing=True)
    end_time = torch.cuda.Event(enable_timing=True)
    start_time.record()
    
    try:
        # Extract and validate input
        job_input = job.get("input", {})
        text = job_input.get("text")
        
        if not text or len(text.strip()) == 0:
            return {"error": "Text parameter is required and cannot be empty"}
        
        if len(text) > 5000:  # Limit text length for GPU memory
            return {"error": "Text too long (max 5000 characters)"}
        
        language_id = job_input.get("language_id", "en")
        model_type = job_input.get("model_type", "english")
        exaggeration = max(0.0, min(1.0, job_input.get("exaggeration", 0.5)))
        cfg_weight = max(0.0, min(1.0, job_input.get("cfg_weight", 0.5)))
        audio_prompt_b64 = job_input.get("audio_prompt")
        
        logger.info(f"🎯 TTS Request: '{text[:50]}...', model={model_type}, lang={language_id}")
        
        # Handle audio prompt for voice cloning
        audio_prompt_path = None
        if audio_prompt_b64:
            try:
                audio_prompt_path = base64_to_audio_file(audio_prompt_b64)
                logger.info("🎤 Voice cloning enabled")
            except Exception as e:
                logger.warning(f"⚠️ Audio prompt failed: {str(e)}")
        
        # GPU memory management
        torch.cuda.empty_cache()
        
        # Generate audio with selected model
        with torch.no_grad():  # Disable gradients for inference
            if model_type == "multilingual" and multilingual_model:
                logger.info("🌍 Using multilingual model")
                wav = multilingual_model.generate(
                    text=text,
                    language_id=language_id,
                    audio_prompt_path=audio_prompt_path,
                    exaggeration=exaggeration,
                    cfg_weight=cfg_weight
                )
                sample_rate = multilingual_model.sr
                
            elif model_type == "english" and english_model:
                logger.info("🇺🇸 Using English model")
                wav = english_model.generate(
                    text=text,
                    audio_prompt_path=audio_prompt_path,
                    exaggeration=exaggeration,
                    cfg_weight=cfg_weight
                )
                sample_rate = english_model.sr
                
            else:
                return {"error": f"Model '{model_type}' not available"}
        
        # Convert to base64 and calculate metrics
        audio_b64 = audio_to_base64(wav, sample_rate)
        duration = wav.shape[-1] / sample_rate
        
        # Cleanup
        if audio_prompt_path and os.path.exists(audio_prompt_path):
            os.unlink(audio_prompt_path)
        
        # GPU timing
        end_time.record()
        torch.cuda.synchronize()
        gpu_time = start_time.elapsed_time(end_time) / 1000.0  # Convert to seconds
        
        logger.info(f"✅ Generated {duration:.2f}s audio in {gpu_time:.2f}s GPU time")
        logger.info(f"📊 GPU Memory: {torch.cuda.memory_allocated() / 1024**3:.1f}GB")
        
        return {
            "audio": audio_b64,
            "sample_rate": sample_rate,
            "duration": duration,
            "text": text,
            "language": language_id,
            "model_type": model_type,
            "gpu_time": gpu_time,
            "gpu_memory_gb": torch.cuda.memory_allocated() / 1024**3
        }
        
    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        logger.error("💥 GPU Out of Memory")
        return {"error": "GPU out of memory. Try shorter text or restart container."}
        
    except Exception as e:
        logger.error(f"💥 Handler error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    # Load models on startup
    load_models()
    
    # Start RunPod serverless
    logger.info("Starting RunPod Serverless handler...")
    runpod.serverless.start({"handler": handler})
