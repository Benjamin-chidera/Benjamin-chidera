"""
Speech-to-Text (STT) module for converting audio to text.

Supports multiple STT providers:
- OpenAI Whisper (local and API)
- Google Speech Recognition
- Azure Speech Services
- Custom models

Author: Benjamin Chidera
"""

import asyncio
import logging
import io
from typing import Optional, Union, Dict, Any
from pathlib import Path

try:
    import whisper
    import speech_recognition as sr
    import pyaudio
    import wave
    import numpy as np
    from openai import OpenAI
except ImportError as e:
    logging.warning(f"Some STT dependencies not available: {e}")

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    """
    Speech-to-Text recognizer with support for multiple backends.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the speech recognizer.
        
        Args:
            config: Configuration dictionary containing STT settings
        """
        self.config = config
        self.provider = config.get("provider", "whisper_local")
        self.language = config.get("language", "en")
        
        # Audio recording settings
        self.sample_rate = config.get("sample_rate", 16000)
        self.chunk_size = config.get("chunk_size", 1024)
        self.channels = config.get("channels", 1)
        self.audio_format = pyaudio.paInt16
        
        # Initialize components based on provider
        self._initialize_provider()
        
        logger.info(f"SpeechRecognizer initialized with provider: {self.provider}")
    
    def _initialize_provider(self):
        """Initialize the selected STT provider."""
        try:
            if self.provider == "whisper_local":
                self.model = whisper.load_model(self.config.get("whisper_model", "base"))
                logger.info("Whisper local model loaded")
                
            elif self.provider == "whisper_api":
                self.openai_client = OpenAI(api_key=self.config.get("openai_api_key"))
                logger.info("OpenAI Whisper API client initialized")
                
            elif self.provider == "google":
                self.recognizer = sr.Recognizer()
                logger.info("Google Speech Recognition initialized")
                
            else:
                raise ValueError(f"Unsupported STT provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Failed to initialize STT provider: {e}")
            raise
    
    async def listen(self, duration: Optional[float] = None) -> Optional[bytes]:
        """
        Listen for audio input from microphone.
        
        Args:
            duration: Duration to record in seconds. If None, records until silence.
            
        Returns:
            Audio data as bytes or None if recording fails
        """
        try:
            audio = pyaudio.PyAudio()
            
            # Open audio stream
            stream = audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            logger.info("Recording audio... (speak now)")
            frames = []
            
            if duration:
                # Record for specified duration
                for _ in range(0, int(self.sample_rate / self.chunk_size * duration)):
                    data = stream.read(self.chunk_size)
                    frames.append(data)
            else:
                # Record until silence (simplified implementation)
                silence_threshold = 1000
                silent_chunks = 0
                max_silent_chunks = 30  # ~1 second of silence
                
                while True:
                    data = stream.read(self.chunk_size)
                    frames.append(data)
                    
                    # Simple silence detection
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    if np.abs(audio_data).mean() < silence_threshold:
                        silent_chunks += 1
                    else:
                        silent_chunks = 0
                    
                    if silent_chunks > max_silent_chunks:
                        break
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Convert to WAV format
            audio_data = b''.join(frames)
            wav_buffer = io.BytesIO()
            
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(self.channels)
                wav_file.setsampwidth(audio.get_sample_size(self.audio_format))
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data)
            
            wav_buffer.seek(0)
            return wav_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return None
    
    async def transcribe(self, audio_data: Union[bytes, str, Path]) -> Optional[str]:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Audio data as bytes, file path, or Path object
            
        Returns:
            Transcribed text or None if transcription fails
        """
        try:
            if self.provider == "whisper_local":
                return await self._transcribe_whisper_local(audio_data)
            elif self.provider == "whisper_api":
                return await self._transcribe_whisper_api(audio_data)
            elif self.provider == "google":
                return await self._transcribe_google(audio_data)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None
    
    async def _transcribe_whisper_local(self, audio_data: Union[bytes, str, Path]) -> str:
        """Transcribe using local Whisper model."""
        # Save audio data to temporary file if it's bytes
        if isinstance(audio_data, bytes):
            temp_file = "/tmp/temp_audio.wav"
            with open(temp_file, "wb") as f:
                f.write(audio_data)
            audio_path = temp_file
        else:
            audio_path = str(audio_data)
        
        # Run transcription in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, 
            lambda: self.model.transcribe(audio_path, language=self.language)
        )
        
        return result["text"].strip()
    
    async def _transcribe_whisper_api(self, audio_data: Union[bytes, str, Path]) -> str:
        """Transcribe using OpenAI Whisper API."""
        if isinstance(audio_data, bytes):
            audio_file = io.BytesIO(audio_data)
            audio_file.name = "audio.wav"
        else:
            audio_file = open(audio_data, "rb")
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=self.language
                )
            )
            return response.text.strip()
        finally:
            if hasattr(audio_file, 'close'):
                audio_file.close()
    
    async def _transcribe_google(self, audio_data: Union[bytes, str, Path]) -> str:
        """Transcribe using Google Speech Recognition."""
        if isinstance(audio_data, bytes):
            audio_source = sr.AudioData(audio_data, self.sample_rate, 2)
        else:
            with sr.AudioFile(str(audio_data)) as source:
                audio_source = self.recognizer.record(source)
        
        # Run recognition in thread pool
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(
            None,
            lambda: self.recognizer.recognize_google(audio_source, language=self.language)
        )
        
        return text.strip()
    
    async def transcribe_file(self, file_path: Union[str, Path]) -> Optional[str]:
        """
        Transcribe an audio file.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Transcribed text or None if transcription fails
        """
        return await self.transcribe(file_path)
    
    def set_language(self, language: str):
        """Set the recognition language."""
        self.language = language
        logger.info(f"Language set to: {language}")


# Convenience functions
async def transcribe_audio(audio_data: bytes, provider: str = "whisper_local") -> str:
    """
    Quick function to transcribe audio data.
    
    Args:
        audio_data: Audio data as bytes
        provider: STT provider to use
        
    Returns:
        Transcribed text
    """
    config = {"provider": provider}
    recognizer = SpeechRecognizer(config)
    result = await recognizer.transcribe(audio_data)
    return result or ""


async def transcribe_file(file_path: str, provider: str = "whisper_local") -> str:
    """
    Quick function to transcribe an audio file.
    
    Args:
        file_path: Path to audio file
        provider: STT provider to use
        
    Returns:
        Transcribed text
    """
    config = {"provider": provider}
    recognizer = SpeechRecognizer(config)
    result = await recognizer.transcribe_file(file_path)
    return result or ""