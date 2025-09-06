from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
import tempfile
import time
import logging
from typing import Optional
import torch
from transformers import pipeline
import librosa
import soundfile as sf
from app.models.chat import VoiceRequest, VoiceResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# Global whisper pipeline - will be initialized on startup
whisper_pipeline = None

async def initialize_whisper():
    """Initialize Whisper model"""
    global whisper_pipeline
    try:
        device = 0 if torch.cuda.is_available() else -1
        logger.info(f"Loading Whisper model on device: {'cuda' if device == 0 else 'cpu'}")
        
        whisper_pipeline = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-tiny.en",  # Fast, small model
            device=device,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
        )
        logger.info("Whisper model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load Whisper model: {e}")
        raise

@router.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    await initialize_whisper()

@router.post("/transcribe", response_model=VoiceResponse)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = Form("en"),
    model_size: Optional[str] = Form("tiny")
):
    """Transcribe uploaded audio file to text"""
    
    if not whisper_pipeline:
        raise HTTPException(status_code=503, detail="Whisper model not loaded")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type: {file.content_type}. Expected audio file."
        )
    
    try:
        start_time = time.time()
        
        # Read audio file
        audio_bytes = await file.read()
        if len(audio_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
        
        # Process audio with temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file.flush()
            
            try:
                # Load and preprocess audio
                audio_data, sample_rate = librosa.load(tmp_file.name, sr=16000)
                duration_seconds = len(audio_data) / sample_rate
                
                # Validate audio duration
                if duration_seconds > 300:  # 5 minutes max
                    raise HTTPException(
                        status_code=400, 
                        detail="Audio file too long. Maximum duration is 5 minutes."
                    )
                
                if duration_seconds < 0.1:  # Minimum duration
                    raise HTTPException(
                        status_code=400, 
                        detail="Audio file too short. Minimum duration is 0.1 seconds."
                    )
                
                # Transcribe using Whisper
                logger.info(f"Transcribing audio: {duration_seconds:.2f}s duration")
                
                result = whisper_pipeline(
                    audio_data,
                    return_timestamps=False,
                    generate_kwargs={
                        "language": language if language != "auto" else None,
                        "task": "transcribe"
                    }
                )
                
                transcription = result["text"].strip()
                
                # Calculate processing metrics
                latency_ms = (time.time() - start_time) * 1000
                
                logger.info(f"Transcription completed in {latency_ms:.2f}ms")
                
                return VoiceResponse(
                    transcription=transcription,
                    confidence=None,  # Whisper doesn't provide confidence scores
                    language_detected=language,
                    duration_seconds=duration_seconds,
                    latency_ms=latency_ms
                )
                
            except Exception as processing_error:
                logger.error(f"Audio processing error: {processing_error}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Audio processing failed: {str(processing_error)}"
                )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Transcription failed: {str(e)}"
        )

@router.post("/transcribe-realtime")
async def transcribe_realtime(
    file: UploadFile = File(...),
    chunk_length: Optional[int] = Form(5),  # Process in 5-second chunks
    language: Optional[str] = Form("en")
):
    """Transcribe audio in real-time chunks (for streaming)"""
    
    if not whisper_pipeline:
        raise HTTPException(status_code=503, detail="Whisper model not loaded")
    
    try:
        audio_bytes = await file.read()
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_file.flush()
            
            # Load audio
            audio_data, sample_rate = librosa.load(tmp_file.name, sr=16000)
            duration = len(audio_data) / sample_rate
            
            # Process in chunks
            chunk_samples = chunk_length * sample_rate
            chunks = []
            
            for i in range(0, len(audio_data), chunk_samples):
                chunk = audio_data[i:i + chunk_samples]
                if len(chunk) < sample_rate * 0.5:  # Skip chunks shorter than 0.5s
                    continue
                
                result = whisper_pipeline(chunk)
                chunk_text = result["text"].strip()
                
                if chunk_text:
                    chunks.append({
                        "start_time": i / sample_rate,
                        "end_time": min((i + chunk_samples) / sample_rate, duration),
                        "text": chunk_text
                    })
            
            return {
                "transcription_chunks": chunks,
                "full_transcription": " ".join([chunk["text"] for chunk in chunks]),
                "total_duration": duration,
                "num_chunks": len(chunks)
            }
            
    except Exception as e:
        logger.error(f"Real-time transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def voice_health_check():
    """Health check for voice processing service"""
    try:
        status = {
            "whisper_loaded": whisper_pipeline is not None,
            "device": "cuda" if torch.cuda.is_available() else "cpu",
            "supported_formats": ["wav", "mp3", "ogg", "m4a"],
            "max_duration_seconds": 300,
            "supported_languages": ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh", "ja", "hi"]
        }
        
        if torch.cuda.is_available():
            status["gpu_memory"] = {
                "allocated_mb": torch.cuda.memory_allocated() / 1024**2,
                "reserved_mb": torch.cuda.memory_reserved() / 1024**2
            }
        
        return status
        
    except Exception as e:
        logger.error(f"Voice health check error: {e}")
        return {"status": "error", "error": str(e)}

@router.post("/text-to-speech")
async def text_to_speech(text: str = Form(...), voice: str = Form("default")):
    """Convert text to speech (placeholder for TTS functionality)"""
    # This would require a TTS model like Tacotron2, FastSpeech2, or similar
    # For now, return a placeholder response
    
    if len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    if len(text) > 1000:
        raise HTTPException(status_code=400, detail="Text too long. Maximum 1000 characters.")
    
    # Placeholder response - in production, implement actual TTS
    return {
        "message": "TTS functionality not implemented yet",
        "text": text,
        "voice": voice,
        "estimated_duration": len(text) * 0.1,  # Rough estimate
        "status": "placeholder"
    }

@router.get("/supported-languages")
async def get_supported_languages():
    """Get list of supported languages for transcription"""
    return {
        "languages": {
            "en": "English",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "pl": "Polish",
            "tr": "Turkish",
            "ru": "Russian",
            "nl": "Dutch",
            "cs": "Czech",
            "ar": "Arabic",
            "zh": "Chinese",
            "ja": "Japanese",
            "hi": "Hindi",
            "auto": "Auto-detect"
        },
        "default": "en",
        "auto_detection": True
    }