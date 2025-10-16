# Backend/app/api/endpoints/voice_to_text.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
import io
import librosa
import torch
import numpy as np
from transformers import (
    WhisperProcessor, WhisperForConditionalGeneration,
    SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan,
    pipeline
)
import tempfile
import os
import soundfile as sf
from pydub import AudioSegment
import base64
import threading
import asyncio

from ...models.user import User
from ...api.deps import get_current_user
from ...core.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

class VoiceToTextResponse(BaseModel):
    text: str
    confidence: float
    duration: float
    language: str
    processing_time: float

class TextToSpeechRequest(BaseModel):
    text: str
    voice_style: str = "neutral"
    speed: float = 1.0

class TextToSpeechResponse(BaseModel):
    audio_data: str  # base64 encoded WAV
    duration: float
    processing_time: float
    text: str

class VoiceService:
    def __init__(self):
        self.whisper_model = None
        self.whisper_processor = None
        self.tts_processor = None
        self.tts_model = None
        self.vocoder = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._loading_lock = asyncio.Lock()
        
    async def load_whisper_model(self):
        """Load Whisper model for speech-to-text"""
        if self.whisper_model is None:
            async with self._loading_lock:
                if self.whisper_model is None:
                    try:
                        logger.info("Loading Whisper model for speech-to-text...")
                        self.whisper_processor = WhisperProcessor.from_pretrained("openai/whisper-base")
                        self.whisper_model = WhisperForConditionalGeneration.from_pretrained(
                            "openai/whisper-base",
                            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                        )
                        if self.device == "cuda":
                            self.whisper_model = self.whisper_model.cuda()
                        self.whisper_model.eval()
                        logger.info(f"Whisper model loaded successfully on {self.device}")
                    except Exception as e:
                        logger.error(f"Error loading Whisper model: {str(e)}")
                        # Fallback to smaller model
                        try:
                            logger.info("Falling back to Whisper tiny model...")
                            self.whisper_processor = WhisperProcessor.from_pretrained("openai/whisper-tiny")
                            self.whisper_model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-tiny")
                            self.whisper_model.eval()
                            logger.info("Whisper tiny model loaded successfully")
                        except Exception as e2:
                            logger.error(f"Failed to load fallback model: {str(e2)}")
                            raise HTTPException(
                                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Could not load speech recognition model"
                            )
    
    async def load_tts_models(self):
        """Load SpeechT5 models for text-to-speech"""
        if self.tts_model is None:
            async with self._loading_lock:
                if self.tts_model is None:
                    try:
                        logger.info("Loading SpeechT5 models for text-to-speech...")
                        
                        # Load processor and model
                        self.tts_processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
                        self.tts_model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
                        
                        # Load vocoder
                        self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
                        
                        if self.device == "cuda":
                            self.tts_model = self.tts_model.cuda()
                            self.vocoder = self.vocoder.cuda()
                        
                        self.tts_model.eval()
                        self.vocoder.eval()
                        
                        logger.info(f"SpeechT5 models loaded successfully on {self.device}")
                        
                    except Exception as e:
                        logger.error(f"Error loading SpeechT5 models: {str(e)}")
                        # Create a simple beep generator as fallback
                        logger.info("Using fallback audio generation")
    
    async def speech_to_text(self, audio_data: bytes, original_filename: str) -> dict:
        """Convert speech to text using Whisper"""
        try:
            await self.load_whisper_model()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Convert audio to proper format if needed
                try:
                    # Try to load with pydub first for format conversion
                    audio_segment = AudioSegment.from_file(temp_file_path)
                    audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
                    
                    # Save as WAV
                    wav_path = temp_file_path.replace(temp_file_path.split('.')[-1], "wav")
                    audio_segment.export(wav_path, format="wav")
                    
                    # Load with librosa
                    waveform, sample_rate = librosa.load(wav_path, sr=16000)
                    
                except Exception as e:
                    logger.warning(f"Format conversion failed, trying direct load: {str(e)}")
                    # Direct load with librosa
                    waveform, sample_rate = librosa.load(temp_file_path, sr=16000)
                
                duration = len(waveform) / sample_rate
                
                if duration < 0.1:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Audio too short (minimum 0.1 seconds)"
                    )
                
                if duration > 30:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Audio too long (maximum 30 seconds)"
                    )
                
                # Normalize audio
                waveform = waveform / np.max(np.abs(waveform)) if np.max(np.abs(waveform)) > 0 else waveform
                
                # Process with Whisper
                inputs = self.whisper_processor(
                    waveform, 
                    sampling_rate=16000, 
                    return_tensors="pt"
                )
                
                if self.device == "cuda":
                    inputs = {k: v.cuda() for k, v in inputs.items()}
                
                # Generate transcription
                with torch.no_grad():
                    predicted_ids = self.whisper_model.generate(
                        inputs["input_features"],
                        max_length=448,
                        num_beams=5,
                        early_stopping=True
                    )
                
                # Decode transcription
                transcription = self.whisper_processor.batch_decode(
                    predicted_ids, 
                    skip_special_tokens=True
                )[0]
                
                # Clean up transcription
                transcription = transcription.strip()
                
                if not transcription:
                    transcription = "[No speech detected]"
                
                # Estimate confidence (Whisper doesn't provide this directly)
                confidence = 0.9 if len(transcription) > 10 else 0.7
                
                return {
                    "text": transcription,
                    "confidence": confidence,
                    "duration": duration,
                    "language": "auto-detected"
                }
                
            finally:
                # Clean up temp files
                for path in [temp_file_path, wav_path if 'wav_path' in locals() else None]:
                    if path and os.path.exists(path):
                        os.remove(path)
                        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in speech-to-text: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing audio: {str(e)}"
            )
    
    async def text_to_speech(self, text: str, voice_style: str = "neutral", speed: float = 1.0) -> dict:
        """Convert text to speech using SpeechT5"""
        try:
            await self.load_tts_models()
            
            if len(text) > 500:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Text too long (maximum 500 characters)"
                )
            
            if not text.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Text cannot be empty"
                )
            
            # Clean and prepare text
            text = text.strip()
            
            # Process text
            inputs = self.tts_processor(text=text, return_tensors="pt")
            
            if self.device == "cuda":
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Create speaker embeddings (default speaker)
            # In a real implementation, you could have multiple speaker embeddings
            speaker_embeddings = torch.zeros((1, 512))
            if self.device == "cuda":
                speaker_embeddings = speaker_embeddings.cuda()
            
            # Generate speech
            with torch.no_grad():
                speech = self.tts_model.generate_speech(
                    inputs["input_ids"], 
                    speaker_embeddings, 
                    vocoder=self.vocoder
                )
            
            # Convert to numpy and adjust for speed
            speech_np = speech.cpu().numpy()
            
            if speed != 1.0:
                # Simple speed adjustment by resampling
                import scipy.signal
                speech_np = scipy.signal.resample(
                    speech_np, 
                    int(len(speech_np) / speed)
                )
            
            # Save to temporary WAV file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                sf.write(temp_file.name, speech_np, 16000)
                
                # Read back as base64
                with open(temp_file.name, "rb") as f:
                    audio_data = base64.b64encode(f.read()).decode()
                
                duration = len(speech_np) / 16000
                
                # Clean up
                os.remove(temp_file.name)
            
            return {
                "audio_data": audio_data,
                "duration": duration,
                "text": text
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in text-to-speech: {str(e)}")
            
            # Fallback: generate a simple tone as audio
            try:
                # Generate a simple beep pattern
                sample_rate = 16000
                duration_sec = min(len(text) * 0.1, 5.0)  # 0.1s per character, max 5s
                t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), False)
                
                # Generate multiple tones to represent speech
                audio = np.zeros_like(t)
                frequencies = [440, 523, 659, 784]  # Musical notes
                
                for i, char in enumerate(text[:40]):  # Max 40 characters
                    if char.isalpha():
                        freq = frequencies[ord(char.lower()) % len(frequencies)]
                        start_idx = int(i * len(t) / len(text))
                        end_idx = min(start_idx + len(t) // 40, len(t))
                        audio[start_idx:end_idx] += 0.1 * np.sin(2 * np.pi * freq * t[start_idx:end_idx])
                
                # Normalize
                audio = audio / (np.max(np.abs(audio)) + 1e-6)
                
                # Save to temp file and encode
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                    sf.write(temp_file.name, audio, sample_rate)
                    
                    with open(temp_file.name, "rb") as f:
                        audio_data = base64.b64encode(f.read()).decode()
                    
                    os.remove(temp_file.name)
                
                return {
                    "audio_data": audio_data,
                    "duration": duration_sec,
                    "text": text
                }
                
            except Exception as fallback_error:
                logger.error(f"Fallback TTS also failed: {str(fallback_error)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="TTS service unavailable"
                )

# Global voice service instance
voice_service = VoiceService()

@router.post("/speech-to-text", response_model=VoiceToTextResponse)
async def speech_to_text(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Convert speech to text using Whisper"""
    import time
    start_time = time.time()
    
    try:
        # Validate file
        if not audio.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No audio file provided"
            )
        
        # Check file size (max 25MB)
        audio_content = await audio.read()
        if len(audio_content) > 25 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Audio file too large (max 25MB)"
            )
        
        # Process audio
        result = await voice_service.speech_to_text(audio_content, audio.filename)
        
        processing_time = time.time() - start_time
        
        # Update usage stats
        current_user.usage_stats["total_requests"] += 1
        db.commit()
        
        return VoiceToTextResponse(
            text=result["text"],
            confidence=result["confidence"],
            duration=result["duration"],
            language=result["language"],
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in speech-to-text endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing speech: {str(e)}"
        )

@router.post("/text-to-speech", response_model=TextToSpeechResponse)
async def text_to_speech(
    request: TextToSpeechRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Convert text to speech using SpeechT5"""
    import time
    start_time = time.time()
    
    try:
        # Process text-to-speech
        result = await voice_service.text_to_speech(
            request.text, 
            request.voice_style, 
            request.speed
        )
        
        processing_time = time.time() - start_time
        
        # Update usage stats
        current_user.usage_stats["total_requests"] += 1
        db.commit()
        
        return TextToSpeechResponse(
            audio_data=result["audio_data"],
            duration=result["duration"],
            processing_time=processing_time,
            text=result["text"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in text-to-speech endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating speech: {str(e)}"
        )

@router.get("/supported-formats")
async def get_supported_formats():
    """Get supported audio formats"""
    return {
        "input_formats": ["wav", "mp3", "m4a", "ogg", "flac", "aac"],
        "output_format": "wav",
        "max_file_size": "25MB",
        "max_duration": "30 seconds",
        "sample_rate": "16kHz",
        "channels": "mono"
    }