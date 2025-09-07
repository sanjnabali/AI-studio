"""
Voice Agent Implementation for AI Studio
Specialized agent for voice processing, speech-to-text, text-to-speech, and audio analysis.
"""

import asyncio
import logging
import io
import os
import tempfile
import librosa
import numpy as np
import torch
import torchaudio
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import whisper
import soundfile as sf
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from datasets import load_dataset
import wave

from .base_agent import BaseAgent, AgentType, AgentCapability, AgentTask, AgentStatus
from app.services.llm import llm_service

logger = logging.getLogger(__name__)

@dataclass
class AudioMetrics:
    """Metrics for audio analysis"""
    duration: float
    sample_rate: int
    channels: int
    format: str
    size_bytes: int
    signal_to_noise_ratio: float
    average_amplitude: float
    peak_amplitude: float

@dataclass
class TranscriptionResult:
    """Result of speech-to-text transcription"""
    text: str
    language: str
    confidence: float
    segments: List[Dict[str, Any]]
    processing_time: float
    audio_metrics: AudioMetrics

@dataclass
class SynthesisResult:
    """Result of text-to-speech synthesis"""
    audio_data: bytes
    sample_rate: int
    duration: float
    format: str
    processing_time: float
    voice_model: str

class VoiceAgent(BaseAgent):
    """
    Specialized agent for voice processing tasks including:
    - Speech-to-text transcription (Whisper)
    - Text-to-speech synthesis
    - Audio analysis and enhancement
    - Voice activity detection
    - Speaker identification
    - Audio format conversion
    - Real-time audio streaming
    """
    
    def __init__(self, agent_id: str = "voice_agent"):
        capabilities = [
            AgentCapability(
                name="speech_to_text",
                description="Convert speech audio to text using Whisper",
                input_types=["audio", "file"],
                output_types=["text", "transcription"],
                complexity_score=7,
                estimated_time=3.0,
                memory_usage=400,
                cpu_intensive=True,
                requires_gpu=False
            ),
            AgentCapability(
                name="text_to_speech",
                description="Convert text to speech audio",
                input_types=["text"],
                output_types=["audio", "wav"],
                complexity_score=8,
                estimated_time=4.0,
                memory_usage=600,
                cpu_intensive=True,
                requires_gpu=False
            ),
            AgentCapability(
                name="audio_analysis",
                description="Analyze audio properties and characteristics",
                input_types=["audio", "file"],
                output_types=["analysis", "metrics"],
                complexity_score=5,
                estimated_time=2.0,
                memory_usage=200
            ),
            AgentCapability(
                name="voice_activity_detection",
                description="Detect speech segments in audio",
                input_types=["audio", "file"],
                output_types=["segments", "timestamps"],
                complexity_score=4,
                estimated_time=1.5,
                memory_usage=150
            ),
            AgentCapability(
                name="audio_enhancement",
                description="Enhance audio quality and reduce noise",
                input_types=["audio", "file"],
                output_types=["enhanced_audio"],
                complexity_score=6,
                estimated_time=3.5,
                memory_usage=300,
                cpu_intensive=True
            ),
            AgentCapability(
                name="audio_format_conversion",
                description="Convert between different audio formats",
                input_types=["audio", "file"],
                output_types=["audio", "converted_file"],
                complexity_score=3,
                estimated_time=1.0,
                memory_usage=100
            ),
            AgentCapability(
                name="speaker_identification",
                description="Identify and separate different speakers",
                input_types=["audio", "file"],
                output_types=["speakers", "segments"],
                complexity_score=8,
                estimated_time=5.0,
                memory_usage=500,
                cpu_intensive=True
            )
        ]
        
        super().__init__(
            agent_id=agent_id,
            agent_type=AgentType.VOICE,
            capabilities=capabilities,
            max_concurrent_tasks=2
        )
        
        # Voice processing configurations
        self.supported_audio_formats = {
            "wav": {"extension": ".wav", "mime": "audio/wav"},
            "mp3": {"extension": ".mp3", "mime": "audio/mpeg"},
            "flac": {"extension": ".flac", "mime": "audio/flac"},
            "ogg": {"extension": ".ogg", "mime": "audio/ogg"},
            "m4a": {"extension": ".m4a", "mime": "audio/mp4"}
        }
        
        self.whisper_models = {
            "tiny": {"size": "39MB", "speed": "fast", "accuracy": "basic"},
            "base": {"size": "74MB", "speed": "medium", "accuracy": "good"},
            "small": {"size": "244MB", "speed": "slow", "accuracy": "better"},
            "medium": {"size": "769MB", "speed": "slower", "accuracy": "excellent"}
        }
        
        # Model instances
        self.whisper_model = None
        self.tts_processor = None
        self.tts_model = None
        self.tts_vocoder = None
        self.speaker_embeddings = None
        
        # Processing settings
        self.default_sample_rate = 16000
        self.chunk_duration = 30  # seconds for processing chunks
        self.silence_threshold = 0.01
        self.min_segment_duration = 0.5
    
    async def initialize(self) -> bool:
        """Initialize the voice agent"""
        try:
            logger.info(f"Initializing {self.agent_id}")
            
            # Initialize Whisper model (start with tiny for speed)
            await self._load_whisper_model("tiny")
            
            # Initialize TTS models
            await self._load_tts_models()
            
            # Load speaker embeddings dataset for TTS
            await self._load_speaker_embeddings()
            
            self.status = AgentStatus.IDLE
            logger.info(f"{self.agent_id} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.agent_id}: {e}")
            self.status = AgentStatus.ERROR
            return False
    
    async def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute voice processing tasks"""
        task_type = task.type
        input_data = task.input_data
        
        try:
            if task_type == "speech_to_text":
                return await self._transcribe_audio(input_data)
            elif task_type == "text_to_speech":
                return await self._synthesize_speech(input_data)
            elif task_type == "audio_analysis":
                return await self._analyze_audio(input_data)
            elif task_type == "voice_activity_detection":
                return await self._detect_voice_activity(input_data)
            elif task_type == "audio_enhancement":
                return await self._enhance_audio(input_data)
            elif task_type == "audio_format_conversion":
                return await self._convert_audio_format(input_data)
            elif task_type == "speaker_identification":
                return await self._identify_speakers(input_data)
            else:
                raise ValueError(f"Unsupported task type: {task_type}")
                
        except Exception as e:
            logger.error(f"Task execution failed in {self.agent_id}: {e}")
            raise
    
    async def _transcribe_audio(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transcribe audio to text using Whisper"""
        audio_file = input_data.get("audio_file")
        audio_data = input_data.get("audio_data")
        language = input_data.get("language", None)
        model_size = input_data.get("model_size", "tiny")
        include_segments = input_data.get("include_segments", True)
        
        if not audio_file and not audio_data:
            raise ValueError("Either audio_file or audio_data must be provided")
        
        start_time = datetime.now()
        
        # Load appropriate Whisper model if needed
        if model_size != "tiny":  # Default is tiny
            await self._load_whisper_model(model_size)
        
        try:
            # Process audio file or data
            if audio_file:
                audio_path = audio_file
            else:
                # Save audio data to temporary file
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio_data)
                    audio_path = tmp.name
            
            # Get audio metrics first
            audio_metrics = await self._get_audio_metrics(audio_path)
            
            # Transcribe with Whisper
            result = self.whisper_model.transcribe(
                audio_path,
                language=language,
                word_timestamps=include_segments,
                fp16=False  # Use fp32 for better compatibility
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Extract segments if requested
            segments = []
            if include_segments and "segments" in result:
                for segment in result["segments"]:
                    segments.append({
                        "start": segment.get("start", 0),
                        "end": segment.get("end", 0),
                        "text": segment.get("text", "").strip(),
                        "confidence": segment.get("avg_logprob", 0.0)
                    })
            
            transcription_result = TranscriptionResult(
                text=result["text"].strip(),
                language=result.get("language", "unknown"),
                confidence=np.exp(result.get("avg_logprob", -1.0)),
                segments=segments,
                processing_time=processing_time,
                audio_metrics=audio_metrics
            )
            
            # Cleanup temporary file if created
            if not audio_file and "audio_data" in input_data:
                try:
                    os.unlink(audio_path)
                except:
                    pass
            
            return {
                "transcription": transcription_result.text,
                "language": transcription_result.language,
                "confidence": transcription_result.confidence,
                "segments": transcription_result.segments,
                "processing_time": transcription_result.processing_time,
                "audio_metrics": transcription_result.audio_metrics.__dict__,
                "model_used": model_size
            }
            
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise
    
    async def _synthesize_speech(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert text to speech"""
        text = input_data.get("text", "")
        voice_id = input_data.get("voice_id", 0)
        speed = input_data.get("speed", 1.0)
        output_format = input_data.get("format", "wav")
        
        if not text:
            raise ValueError("Text is required for speech synthesis")
        
        if output_format not in self.supported_audio_formats:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        start_time = datetime.now()
        
        try:
            # Process text through TTS processor
            inputs = self.tts_processor(text=text, return_tensors="pt")
            
            # Get speaker embeddings
            speaker_embeddings = self.speaker_embeddings[voice_id % len(self.speaker_embeddings)]
            
            # Generate speech
            with torch.no_grad():
                speech = self.tts_model.generate_speech(
                    inputs["input_ids"],
                    speaker_embeddings,
                    vocoder=self.tts_vocoder
                )
            
            # Convert to numpy and adjust speed if needed
            audio_np = speech.numpy()
            if speed != 1.0:
                audio_np = librosa.effects.time_stretch(audio_np, rate=speed)
            
            # Convert to desired format
            sample_rate = 16000  # SpeechT5 default
            duration = len(audio_np) / sample_rate
            
            # Convert to bytes
            with tempfile.NamedTemporaryFile(suffix=f".{output_format}") as tmp:
                sf.write(tmp.name, audio_np, sample_rate, format=output_format.upper())
                tmp.seek(0)
                audio_data = tmp.read()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            synthesis_result = SynthesisResult(
                audio_data=audio_data,
                sample_rate=sample_rate,
                duration=duration,
                format=output_format,
                processing_time=processing_time,
                voice_model="speecht5"
            )
            
            return {
                "audio_data": synthesis_result.audio_data,
                "sample_rate": synthesis_result.sample_rate,
                "duration": synthesis_result.duration,
                "format": synthesis_result.format,
                "processing_time": synthesis_result.processing_time,
                "voice_model": synthesis_result.voice_model,
                "text_processed": text,
                "voice_id": voice_id
            }
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            raise
    
    async def _analyze_audio(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze audio properties and characteristics"""
        audio_file = input_data.get("audio_file")
        audio_data = input_data.get("audio_data")
        detailed_analysis = input_data.get("detailed", False)
        
        if not audio_file and not audio_data:
            raise ValueError("Either audio_file or audio_data must be provided")
        
        try:
            # Load audio
            if audio_file:
                y, sr = librosa.load(audio_file)
                file_path = audio_file
            else:
                # Save data to temp file first
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio_data)
                    file_path = tmp.name
                y, sr = librosa.load(file_path)
            
            # Basic metrics
            metrics = await self._get_audio_metrics(file_path)
            
            analysis_result = {
                "basic_metrics": metrics.__dict__,
                "sample_rate": sr,
                "duration": len(y) / sr,
                "channels": 1 if len(y.shape) == 1 else y.shape[0]
            }
            
            if detailed_analysis:
                # Advanced analysis
                analysis_result.update({
                    "spectral_features": await self._extract_spectral_features(y, sr),
                    "tempo_rhythm": await self._analyze_tempo_rhythm(y, sr),
                    "pitch_analysis": await self._analyze_pitch(y, sr),
                    "energy_analysis": await self._analyze_energy(y, sr)
                })
            
            # Cleanup temp file
            if not audio_file:
                try:
                    os.unlink(file_path)
                except:
                    pass
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            raise
    
    async def _detect_voice_activity(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect voice activity segments in audio"""
        audio_file = input_data.get("audio_file")
        audio_data = input_data.get("audio_data")
        threshold = input_data.get("threshold", self.silence_threshold)
        min_duration = input_data.get("min_duration", self.min_segment_duration)
        
        if not audio_file and not audio_data:
            raise ValueError("Either audio_file or audio_data must be provided")
        
        try:
            # Load audio
            if audio_file:
                y, sr = librosa.load(audio_file)
            else:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio_data)
                    tmp_path = tmp.name
                y, sr = librosa.load(tmp_path)
                os.unlink(tmp_path)
            
            # Compute frame-wise RMS energy
            frame_length = int(0.025 * sr)  # 25ms frames
            hop_length = int(0.01 * sr)    # 10ms hop
            
            rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            
            # Detect voice activity
            voice_frames = rms > threshold
            
            # Convert to time segments
            frame_times = librosa.frames_to_time(np.arange(len(voice_frames)), sr=sr, hop_length=hop_length)
            
            segments = []
            start_time = None
            
            for i, is_voice in enumerate(voice_frames):
                if is_voice and start_time is None:
                    start_time = frame_times[i]
                elif not is_voice and start_time is not None:
                    end_time = frame_times[i]
                    duration = end_time - start_time
                    
                    if duration >= min_duration:
                        segments.append({
                            "start": float(start_time),
                            "end": float(end_time),
                            "duration": float(duration),
                            "confidence": float(np.mean(rms[int(start_time/0.01):int(end_time/0.01)]))
                        })
                    
                    start_time = None
            
            # Handle case where audio ends with voice
            if start_time is not None:
                end_time = frame_times[-1]
                duration = end_time - start_time
                if duration >= min_duration:
                    segments.append({
                        "start": float(start_time),
                        "end": float(end_time),
                        "duration": float(duration),
                        "confidence": float(np.mean(rms[int(start_time/0.01):]))
                    })
            
            total_speech_duration = sum(seg["duration"] for seg in segments)
            total_audio_duration = len(y) / sr
            speech_ratio = total_speech_duration / total_audio_duration
            
            return {
                "voice_segments": segments,
                "total_segments": len(segments),
                "total_speech_duration": float(total_speech_duration),
                "total_audio_duration": float(total_audio_duration),
                "speech_ratio": float(speech_ratio),
                "silence_threshold": threshold,
                "min_segment_duration": min_duration
            }
            
        except Exception as e:
            logger.error(f"Voice activity detection failed: {e}")
            raise
    
    async def _enhance_audio(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance audio quality and reduce noise"""
        audio_file = input_data.get("audio_file")
        audio_data = input_data.get("audio_data")
        enhancement_type = input_data.get("type", "noise_reduction")
        strength = input_data.get("strength", 0.5)
        
        if not audio_file and not audio_data:
            raise ValueError("Either audio_file or audio_data must be provided")
        
        try:
            # Load audio
            if audio_file:
                y, sr = librosa.load(audio_file)
            else:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio_data)
                    tmp_path = tmp.name
                y, sr = librosa.load(tmp_path)
                os.unlink(tmp_path)
            
            enhanced_y = y.copy()
            
            if enhancement_type == "noise_reduction":
                # Simple spectral gating noise reduction
                enhanced_y = await self._reduce_noise(y, sr, strength)
            elif enhancement_type == "normalize":
                # Normalize audio levels
                enhanced_y = librosa.util.normalize(y)
            elif enhancement_type == "compress":
                # Dynamic range compression
                enhanced_y = await self._compress_dynamic_range(y, strength)
            elif enhancement_type == "eq":
                # Basic equalization
                enhanced_y = await self._apply_equalization(y, sr, strength)
            
            # Convert enhanced audio to bytes
            with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
                sf.write(tmp.name, enhanced_y, sr)
                tmp.seek(0)
                enhanced_data = tmp.read()
            
            return {
                "enhanced_audio": enhanced_data,
                "sample_rate": sr,
                "enhancement_type": enhancement_type,
                "strength": strength,
                "original_duration": len(y) / sr,
                "enhanced_duration": len(enhanced_y) / sr
            }
            
        except Exception as e:
            logger.error(f"Audio enhancement failed: {e}")
            raise
    
    async def _convert_audio_format(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert between different audio formats"""
        audio_file = input_data.get("audio_file")
        audio_data = input_data.get("audio_data")
        target_format = input_data.get("target_format", "wav")
        target_sample_rate = input_data.get("sample_rate", None)
        
        if not audio_file and not audio_data:
            raise ValueError("Either audio_file or audio_data must be provided")
        
        if target_format not in self.supported_audio_formats:
            raise ValueError(f"Unsupported target format: {target_format}")
        
        try:
            # Load audio
            if audio_file:
                y, sr = librosa.load(audio_file)
                original_format = Path(audio_file).suffix[1:]
            else:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio_data)
                    tmp_path = tmp.name
                y, sr = librosa.load(tmp_path)
                original_format = "wav"
                os.unlink(tmp_path)
            
            # Resample if needed
            if target_sample_rate and target_sample_rate != sr:
                y = librosa.resample(y, orig_sr=sr, target_sr=target_sample_rate)
                sr = target_sample_rate
            
            # Convert to target format
            with tempfile.NamedTemporaryFile(suffix=f".{target_format}") as tmp:
                sf.write(tmp.name, y, sr, format=target_format.upper())
                tmp.seek(0)
                converted_data = tmp.read()
            
            return {
                "converted_audio": converted_data,
                "original_format": original_format,
                "target_format": target_format,
                "sample_rate": sr,
                "duration": len(y) / sr,
                "file_size": len(converted_data)
            }
            
        except Exception as e:
            logger.error(f"Audio format conversion failed: {e}")
            raise
    
    async def _identify_speakers(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify and separate different speakers"""
        audio_file = input_data.get("audio_file")
        audio_data = input_data.get("audio_data")
        num_speakers = input_data.get("num_speakers", None)
        
        if not audio_file and not audio_data:
            raise ValueError("Either audio_file or audio_data must be provided")
        
        try:
            # Load audio
            if audio_file:
                y, sr = librosa.load(audio_file)
            else:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio_data)
                    tmp_path = tmp.name
                y, sr = librosa.load(tmp_path)
                os.unlink(tmp_path)
            
            # Simple speaker diarization using spectral features
            # In a production system, you'd use specialized models like pyannote-audio
            
            # Extract MFCC features for speaker characteristics
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # Segment audio into chunks
            chunk_duration = 2.0  # 2 seconds per chunk
            chunk_samples = int(chunk_duration * sr)
            
            chunks = []
            features = []
            
            for i in range(0, len(y), chunk_samples):
                chunk = y[i:i + chunk_samples]
                if len(chunk) >= chunk_samples // 2:  # At least half chunk duration
                    chunk_mfcc = librosa.feature.mfcc(y=chunk, sr=sr, n_mfcc=13)
                    chunk_feature = np.mean(chunk_mfcc, axis=1)
                    
                    chunks.append({
                        "start": i / sr,
                        "end": min((i + chunk_samples) / sr, len(y) / sr),
                        "features": chunk_feature
                    })
                    features.append(chunk_feature)
            
            # Simple clustering to identify speakers
            if len(features) > 0:
                features_array = np.array(features)
                
                if num_speakers is None:
                    # Estimate number of speakers (simplified)
                    num_speakers = min(4, max(1, len(chunks) // 10))
                
                # K-means clustering (simplified speaker identification)
                from sklearn.cluster import KMeans
                
                if len(features_array) >= num_speakers:
                    kmeans = KMeans(n_clusters=num_speakers, random_state=42)
                    labels = kmeans.fit_predict(features_array)
                    
                    # Assign speaker labels to chunks
                    for i, chunk in enumerate(chunks):
                        chunk["speaker_id"] = int(labels[i])
                        chunk["confidence"] = 0.7  # Placeholder confidence
                else:
                    # Not enough chunks for clustering
                    for chunk in chunks:
                        chunk["speaker_id"] = 0
                        chunk["confidence"] = 1.0
            
            # Group consecutive chunks by speaker
            speaker_segments = []
            current_segment = None
            
            for chunk in chunks:
                if current_segment is None or current_segment["speaker_id"] != chunk["speaker_id"]:
                    if current_segment:
                        speaker_segments.append(current_segment)
                    
                    current_segment = {
                        "speaker_id": chunk["speaker_id"],
                        "start": chunk["start"],
                        "end": chunk["end"],
                        "confidence": chunk["confidence"]
                    }
                else:
                    current_segment["end"] = chunk["end"]
                    current_segment["confidence"] = (current_segment["confidence"] + chunk["confidence"]) / 2
            
            if current_segment:
                speaker_segments.append(current_segment)
            
            # Calculate speaker statistics
            speaker_stats = {}
            for segment in speaker_segments:
                speaker_id = segment["speaker_id"]
                duration = segment["end"] - segment["start"]
                
                if speaker_id not in speaker_stats:
                    speaker_stats[speaker_id] = {
                        "total_duration": 0,
                        "segment_count": 0,
                        "avg_confidence": 0
                    }
                
                speaker_stats[speaker_id]["total_duration"] += duration
                speaker_stats[speaker_id]["segment_count"] += 1
                speaker_stats[speaker_id]["avg_confidence"] = (
                    (speaker_stats[speaker_id]["avg_confidence"] * (speaker_stats[speaker_id]["segment_count"] - 1) + 
                     segment["confidence"]) / speaker_stats[speaker_id]["segment_count"]
                )
            
            return {
                "speaker_segments": speaker_segments,
                "num_speakers_detected": len(speaker_stats),
                "speaker_statistics": speaker_stats,
                "total_duration": len(y) / sr,
                "analysis_method": "mfcc_clustering"
            }
            
        except Exception as e:
            logger.error(f"Speaker identification failed: {e}")
            raise
    
    # Helper methods
    async def _load_whisper_model(self, model_size: str = "tiny"):
        """Load Whisper model"""
        try:
            if self.whisper_model is None or getattr(self, '_current_whisper_size', None) != model_size:
                logger.info(f"Loading Whisper {model_size} model...")
                self.whisper_model = whisper.load_model(model_size)
                self._current_whisper_size = model_size
                logger.info(f"Whisper {model_size} model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    async def _load_tts_models(self):
        """Load text-to-speech models"""
        try:
            logger.info("Loading TTS models...")
            
            self.tts_processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
            self.tts_model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
            self.tts_vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
            
            logger.info("TTS models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load TTS models: {e}")
            # Continue without TTS if loading fails
            pass
    
    async def _load_speaker_embeddings(self):
        """Load speaker embeddings for TTS"""
        try:
            # Load speaker embeddings dataset
            embeddings_dataset = load_dataset("Matthijs/cmu-arctic-xvectors", split="validation")
            self.speaker_embeddings = torch.tensor(embeddings_dataset[0]["xvector"]).unsqueeze(0)
            
            # Add a few more speaker embeddings for variety
            for i in range(1, min(len(embeddings_dataset), 5)):
                embedding = torch.tensor(embeddings_dataset[i]["xvector"]).unsqueeze(0)
                self.speaker_embeddings = torch.cat([self.speaker_embeddings, embedding])
            
        except Exception as e:
            logger.warning(f"Failed to load speaker embeddings: {e}")
            # Create dummy embeddings if loading fails
            self.speaker_embeddings = torch.randn(1, 512)
    
    async def _get_audio_metrics(self, audio_path: str) -> AudioMetrics:
        """Extract basic audio metrics"""
        try:
            # Load with librosa
            y, sr = librosa.load(audio_path)
            
            # Get file info
            file_size = os.path.getsize(audio_path)
            duration = len(y) / sr
            
            # Calculate audio properties
            rms_energy = librosa.feature.rms(y=y)[0]
            avg_amplitude = float(np.mean(np.abs(y)))
            peak_amplitude = float(np.max(np.abs(y)))
            
            # Estimate SNR (simplified)
            signal_power = np.mean(y ** 2)
            noise_floor = np.percentile(rms_energy, 10)  # Bottom 10% as noise estimate
            snr = 10 * np.log10(signal_power / (noise_floor ** 2 + 1e-10))
            
            return AudioMetrics(
                duration=duration,
                sample_rate=sr,
                channels=1 if len(y.shape) == 1 else y.shape[0],
                format="wav",  # Simplified
                size_bytes=file_size,
                signal_to_noise_ratio=float(snr),
                average_amplitude=avg_amplitude,
                peak_amplitude=peak_amplitude
            )
        except Exception as e:
            logger.warning(f"Failed to extract audio metrics: {e}")
            return AudioMetrics(0, 0, 0, "unknown", 0, 0.0, 0.0, 0.0)
    
    async def _extract_spectral_features(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract spectral features from audio"""
        try:
            # Spectral centroid
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
            
            # Spectral rolloff
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
            
            # Zero crossing rate
            zcr = librosa.feature.zero_crossing_rate(y)[0]
            
            # MFCCs
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            
            return {
                "spectral_centroid": {
                    "mean": float(np.mean(spectral_centroids)),
                    "std": float(np.std(spectral_centroids))
                },
                "spectral_rolloff": {
                    "mean": float(np.mean(spectral_rolloff)),
                    "std": float(np.std(spectral_rolloff))
                },
                "zero_crossing_rate": {
                    "mean": float(np.mean(zcr)),
                    "std": float(np.std(zcr))
                },
                "mfcc": {
                    "mean": [float(x) for x in np.mean(mfccs, axis=1)],
                    "std": [float(x) for x in np.std(mfccs, axis=1)]
                },
                "chroma": {
                    "mean": [float(x) for x in np.mean(chroma, axis=1)],
                    "std": [float(x) for x in np.std(chroma, axis=1)]
                }
            }
        except Exception as e:
            logger.warning(f"Failed to extract spectral features: {e}")
            return {}
    
    async def _analyze_tempo_rhythm(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze tempo and rhythm"""
        try:
            # Tempo estimation
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            
            # Rhythm patterns
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            
            return {
                "tempo": float(tempo),
                "num_beats": len(beats),
                "beat_times": [float(t) for t in librosa.frames_to_time(beats, sr=sr)],
                "rhythmic_regularity": float(np.std(np.diff(beats))),  # Lower is more regular
                "onset_strength": {
                    "mean": float(np.mean(onset_env)),
                    "max": float(np.max(onset_env))
                }
            }
        except Exception as e:
            logger.warning(f"Failed to analyze tempo/rhythm: {e}")
            return {}
    
    async def _analyze_pitch(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze pitch characteristics"""
        try:
            # Fundamental frequency estimation
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7')
            )
            
            # Remove NaN values
            f0_clean = f0[~np.isnan(f0)]
            
            if len(f0_clean) > 0:
                return {
                    "fundamental_frequency": {
                        "mean": float(np.mean(f0_clean)),
                        "std": float(np.std(f0_clean)),
                        "min": float(np.min(f0_clean)),
                        "max": float(np.max(f0_clean))
                    },
                    "voiced_ratio": float(np.mean(voiced_flag)),
                    "pitch_stability": float(1.0 / (np.std(f0_clean) + 1e-6)),
                    "pitch_range": float(np.max(f0_clean) - np.min(f0_clean))
                }
            else:
                return {"fundamental_frequency": None, "error": "No voiced segments found"}
                
        except Exception as e:
            logger.warning(f"Failed to analyze pitch: {e}")
            return {}
    
    async def _analyze_energy(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze energy characteristics"""
        try:
            # RMS energy
            rms = librosa.feature.rms(y=y)[0]
            
            # Short-time energy
            frame_length = 2048
            energy = []
            for i in range(0, len(y) - frame_length, frame_length // 2):
                frame = y[i:i + frame_length]
                energy.append(np.sum(frame ** 2))
            
            energy = np.array(energy)
            
            return {
                "rms_energy": {
                    "mean": float(np.mean(rms)),
                    "std": float(np.std(rms)),
                    "max": float(np.max(rms))
                },
                "energy_distribution": {
                    "mean": float(np.mean(energy)),
                    "std": float(np.std(energy)),
                    "dynamic_range": float(np.max(energy) / (np.min(energy) + 1e-10))
                },
                "silence_ratio": float(np.mean(rms < 0.01))
            }
        except Exception as e:
            logger.warning(f"Failed to analyze energy: {e}")
            return {}
    
    async def _reduce_noise(self, y: np.ndarray, sr: int, strength: float) -> np.ndarray:
        """Simple noise reduction using spectral gating"""
        try:
            # Compute STFT
            D = librosa.stft(y)
            magnitude, phase = np.abs(D), np.angle(D)
            
            # Estimate noise floor (bottom percentile of magnitudes)
            noise_floor = np.percentile(magnitude, 10 * (1 - strength))
            
            # Apply spectral gating
            mask = magnitude > (noise_floor * (1 + strength))
            magnitude_cleaned = magnitude * mask
            
            # Reconstruct audio
            D_cleaned = magnitude_cleaned * np.exp(1j * phase)
            y_cleaned = librosa.istft(D_cleaned)
            
            return y_cleaned
        except Exception as e:
            logger.warning(f"Noise reduction failed: {e}")
            return y
    
    async def _compress_dynamic_range(self, y: np.ndarray, strength: float) -> np.ndarray:
        """Apply dynamic range compression"""
        try:
            # Simple compression using tanh
            threshold = 0.1 * (1 - strength)
            ratio = 1 + strength * 5  # Compression ratio
            
            y_compressed = np.copy(y)
            above_threshold = np.abs(y) > threshold
            
            # Apply compression to samples above threshold
            y_compressed[above_threshold] = (
                np.sign(y[above_threshold]) * 
                (threshold + (np.abs(y[above_threshold]) - threshold) / ratio)
            )
            
            return y_compressed
        except Exception as e:
            logger.warning(f"Dynamic range compression failed: {e}")
            return y
    
    async def _apply_equalization(self, y: np.ndarray, sr: int, strength: float) -> np.ndarray:
        """Apply basic equalization"""
        try:
            # Simple EQ using filtering
            from scipy import signal
            
            # High-pass filter to remove low-frequency noise
            if strength > 0:
                nyquist = sr / 2
                high_freq = 80 * (1 + strength)  # 80-160 Hz cutoff
                high_freq = min(high_freq, nyquist * 0.99)
                
                b, a = signal.butter(2, high_freq / nyquist, btype='high')
                y_eq = signal.filtfilt(b, a, y)
                
                return y_eq
            
            return y
        except Exception as e:
            logger.warning(f"Equalization failed: {e}")
            return y
    
    async def cleanup(self) -> None:
        """Cleanup voice agent resources"""
        logger.info(f"Cleaning up {self.agent_id}")
        
        # Clear model references to free memory
        self.whisper_model = None
        self.tts_processor = None
        self.tts_model = None
        self.tts_vocoder = None
        self.speaker_embeddings = None
        
        # Force garbage collection
        import gc
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

# Example usage and testing
async def test_voice_agent():
    """Test the voice agent functionality"""
    agent = VoiceAgent()
    
    # Initialize
    if not await agent.initialize():
        print("Failed to initialize voice agent")
        return
    
    print("Voice agent initialized successfully")
    
    # Test TTS
    tts_task = AgentTask(
        type="text_to_speech",
        input_data={
            "text": "Hello, this is a test of the text to speech system.",
            "voice_id": 0,
            "format": "wav"
        }
    )
    
    try:
        tts_result = await agent.execute_task(tts_task)
        print(f"TTS completed in {tts_result['processing_time']:.2f}s")
        print(f"Generated {tts_result['duration']:.2f}s of audio")
    except Exception as e:
        print(f"TTS test failed: {e}")
    
    # Test voice activity detection
    if 'audio_data' in locals():  # If we have audio from TTS
        vad_task = AgentTask(
            type="voice_activity_detection",
            input_data={
                "audio_data": tts_result['audio_data'],
                "threshold": 0.01
            }
        )
        
        try:
            vad_result = await agent.execute_task(vad_task)
            print(f"VAD found {vad_result['total_segments']} voice segments")
            print(f"Speech ratio: {vad_result['speech_ratio']:.2f}")
        except Exception as e:
            print(f"VAD test failed: {e}")
    
    # Cleanup
    await agent.cleanup()
    print("Voice agent test completed")

if __name__ == "__main__":
    asyncio.run(test_voice_agent())