"""
Text-to-Speech (TTS) module for converting text to natural-sounding speech.

Supports multiple TTS providers:
- pyttsx3 (offline)
- Google Text-to-Speech (gTTS)
- ElevenLabs (premium)
- OpenAI TTS API
- Azure Speech Services

Author: Benjamin Chidera
"""

import asyncio
import logging
import io
import tempfile
from typing import Optional, Dict, Any, Union
from pathlib import Path

try:
    import pyttsx3
    from gtts import gTTS
    import pygame
    from openai import OpenAI
    import requests
except ImportError as e:
    logging.warning(f"Some TTS dependencies not available: {e}")

logger = logging.getLogger(__name__)


class SpeechSynthesizer:
    """
    Text-to-Speech synthesizer with support for multiple backends.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the speech synthesizer.
        
        Args:
            config: Configuration dictionary containing TTS settings
        """
        self.config = config
        self.provider = config.get("provider", "pyttsx3")
        self.language = config.get("language", "en")
        self.voice_id = config.get("voice_id", None)
        
        # Audio settings
        self.speed = config.get("speed", 150)  # Words per minute
        self.volume = config.get("volume", 0.9)  # 0.0 to 1.0
        
        # Initialize components based on provider
        self._initialize_provider()
        
        logger.info(f"SpeechSynthesizer initialized with provider: {self.provider}")
    
    def _initialize_provider(self):
        """Initialize the selected TTS provider."""
        try:
            if self.provider == "pyttsx3":
                self.engine = pyttsx3.init()
                self._configure_pyttsx3()
                logger.info("pyttsx3 engine initialized")
                
            elif self.provider == "openai":
                self.openai_client = OpenAI(api_key=self.config.get("openai_api_key"))
                logger.info("OpenAI TTS client initialized")
                
            elif self.provider == "elevenlabs":
                self.elevenlabs_api_key = self.config.get("elevenlabs_api_key")
                if not self.elevenlabs_api_key:
                    raise ValueError("ElevenLabs API key required")
                logger.info("ElevenLabs TTS initialized")
                
            # Initialize pygame for audio playback
            pygame.mixer.init()
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS provider: {e}")
            raise
    
    def _configure_pyttsx3(self):
        """Configure pyttsx3 engine settings."""
        try:
            # Set speech rate
            self.engine.setProperty('rate', self.speed)
            
            # Set volume
            self.engine.setProperty('volume', self.volume)
            
            # Set voice if specified
            if self.voice_id:
                voices = self.engine.getProperty('voices')
                if voices and len(voices) > int(self.voice_id):
                    self.engine.setProperty('voice', voices[int(self.voice_id)].id)
            
        except Exception as e:
            logger.warning(f"Could not configure pyttsx3: {e}")
    
    async def synthesize(self, text: str, output_file: Optional[str] = None) -> Optional[bytes]:
        """
        Convert text to speech audio.
        
        Args:
            text: Text to convert to speech
            output_file: Optional file path to save audio
            
        Returns:
            Audio data as bytes or None if synthesis fails
        """
        try:
            if self.provider == "pyttsx3":
                return await self._synthesize_pyttsx3(text, output_file)
            elif self.provider == "gtts":
                return await self._synthesize_gtts(text, output_file)
            elif self.provider == "openai":
                return await self._synthesize_openai(text, output_file)
            elif self.provider == "elevenlabs":
                return await self._synthesize_elevenlabs(text, output_file)
            else:
                raise ValueError(f"Unsupported TTS provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            return None
    
    async def _synthesize_pyttsx3(self, text: str, output_file: Optional[str] = None) -> bytes:
        """Synthesize speech using pyttsx3."""
        if output_file:
            # Save to file
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.engine.save_to_file(text, output_file)
            )
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.engine.runAndWait
            )
            
            # Read file content
            with open(output_file, 'rb') as f:
                return f.read()
        else:
            # Use temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
            
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.engine.save_to_file(text, temp_path)
            )
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.engine.runAndWait
            )
            
            # Read and return content
            with open(temp_path, 'rb') as f:
                audio_data = f.read()
            
            # Clean up
            Path(temp_path).unlink(missing_ok=True)
            return audio_data
    
    async def _synthesize_gtts(self, text: str, output_file: Optional[str] = None) -> bytes:
        """Synthesize speech using Google Text-to-Speech."""
        tts = gTTS(text=text, lang=self.language, slow=False)
        
        if output_file:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: tts.save(output_file)
            )
            with open(output_file, 'rb') as f:
                return f.read()
        else:
            # Use BytesIO buffer
            buffer = io.BytesIO()
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: tts.write_to_fp(buffer)
            )
            buffer.seek(0)
            return buffer.getvalue()
    
    async def _synthesize_openai(self, text: str, output_file: Optional[str] = None) -> bytes:
        """Synthesize speech using OpenAI TTS API."""
        voice = self.voice_id or "alloy"  # Default voice
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.openai_client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text,
                response_format="mp3"
            )
        )
        
        audio_data = response.content
        
        if output_file:
            with open(output_file, 'wb') as f:
                f.write(audio_data)
        
        return audio_data
    
    async def _synthesize_elevenlabs(self, text: str, output_file: Optional[str] = None) -> bytes:
        """Synthesize speech using ElevenLabs API."""
        voice_id = self.voice_id or "21m00Tcm4TlvDq8ikWAM"  # Default voice
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.post(url, json=data, headers=headers)
        )
        
        if response.status_code == 200:
            audio_data = response.content
            
            if output_file:
                with open(output_file, 'wb') as f:
                    f.write(audio_data)
            
            return audio_data
        else:
            raise Exception(f"ElevenLabs API error: {response.status_code}")
    
    async def speak(self, text: str) -> bool:
        """
        Synthesize and immediately play speech.
        
        Args:
            text: Text to speak
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.provider == "pyttsx3":
                # For pyttsx3, we can speak directly
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.engine.say(text)
                )
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.engine.runAndWait
                )
                return True
            else:
                # For other providers, synthesize then play
                audio_data = await self.synthesize(text)
                if audio_data:
                    return await self._play_audio(audio_data)
                return False
                
        except Exception as e:
            logger.error(f"Error speaking text: {e}")
            return False
    
    async def _play_audio(self, audio_data: bytes) -> bool:
        """Play audio data using pygame."""
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # Play audio
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            
            # Clean up
            Path(temp_path).unlink(missing_ok=True)
            return True
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False
    
    def set_voice(self, voice_id: str):
        """Set the voice for speech synthesis."""
        self.voice_id = voice_id
        
        if self.provider == "pyttsx3":
            self._configure_pyttsx3()
        
        logger.info(f"Voice set to: {voice_id}")
    
    def set_speed(self, speed: int):
        """Set the speech speed (words per minute)."""
        self.speed = speed
        
        if self.provider == "pyttsx3":
            self.engine.setProperty('rate', speed)
        
        logger.info(f"Speed set to: {speed} WPM")
    
    def set_volume(self, volume: float):
        """Set the speech volume (0.0 to 1.0)."""
        self.volume = max(0.0, min(1.0, volume))
        
        if self.provider == "pyttsx3":
            self.engine.setProperty('volume', self.volume)
        
        logger.info(f"Volume set to: {self.volume}")
    
    def get_available_voices(self) -> list:
        """Get list of available voices."""
        if self.provider == "pyttsx3":
            try:
                voices = self.engine.getProperty('voices')
                return [{"id": i, "name": voice.name, "lang": getattr(voice, 'languages', ['unknown'])} 
                       for i, voice in enumerate(voices)]
            except:
                return []
        else:
            # For other providers, return common voice options
            return [
                {"id": "alloy", "name": "Alloy", "lang": ["en"]},
                {"id": "echo", "name": "Echo", "lang": ["en"]},
                {"id": "fable", "name": "Fable", "lang": ["en"]},
                {"id": "onyx", "name": "Onyx", "lang": ["en"]},
                {"id": "nova", "name": "Nova", "lang": ["en"]},
                {"id": "shimmer", "name": "Shimmer", "lang": ["en"]}
            ]


# Convenience functions
async def text_to_speech(text: str, provider: str = "pyttsx3", voice_id: Optional[str] = None) -> bytes:
    """
    Quick function to convert text to speech.
    
    Args:
        text: Text to convert
        provider: TTS provider to use
        voice_id: Optional voice ID
        
    Returns:
        Audio data as bytes
    """
    config = {"provider": provider}
    if voice_id:
        config["voice_id"] = voice_id
    
    synthesizer = SpeechSynthesizer(config)
    audio_data = await synthesizer.synthesize(text)
    return audio_data or b""


async def speak_text(text: str, provider: str = "pyttsx3") -> bool:
    """
    Quick function to speak text immediately.
    
    Args:
        text: Text to speak
        provider: TTS provider to use
        
    Returns:
        True if successful, False otherwise
    """
    config = {"provider": provider}
    synthesizer = SpeechSynthesizer(config)
    return await synthesizer.speak(text)