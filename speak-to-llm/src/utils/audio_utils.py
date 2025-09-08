"""
Audio utilities for the Speak-to-LLM application.

Provides audio processing, playback, recording, and format conversion utilities.

Author: Benjamin Chidera
"""

import asyncio
import logging
import io
import wave
import tempfile
from typing import Optional, Tuple, List, Dict
from pathlib import Path

try:
    import pyaudio
    import numpy as np
    import pygame
    import librosa
    import soundfile as sf
except ImportError as e:
    logging.warning(f"Some audio dependencies not available: {e}")

logger = logging.getLogger(__name__)


class AudioUtils:
    """
    Utilities for audio processing and playback.
    """
    
    def __init__(self):
        """Initialize audio utilities."""
        # Audio settings
        self.sample_rate = 16000
        self.channels = 1
        self.chunk_size = 1024
        self.format = pyaudio.paInt16
        
        # Initialize pygame for playback
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.pygame_available = True
        except:
            self.pygame_available = False
            logger.warning("Pygame not available for audio playback")
        
        logger.info("AudioUtils initialized")
    
    async def play_audio(self, audio_data: bytes, file_format: str = "wav") -> bool:
        """
        Play audio data.
        
        Args:
            audio_data: Audio data as bytes
            file_format: Audio format (wav, mp3, etc.)
            
        Returns:
            True if playback successful, False otherwise
        """
        try:
            # Save to temporary file
            suffix = f".{file_format}"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            if self.pygame_available:
                # Use pygame for playback
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                
                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
            else:
                # Fallback to system audio player
                import subprocess
                subprocess.run(["aplay", temp_path], check=True, capture_output=True)
            
            # Clean up
            Path(temp_path).unlink(missing_ok=True)
            return True
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            return False
    
    async def record_audio(self, duration: Optional[float] = None) -> Optional[bytes]:
        """
        Record audio from microphone.
        
        Args:
            duration: Duration to record in seconds. If None, records until silence.
            
        Returns:
            Audio data as WAV bytes or None if recording fails
        """
        try:
            audio = pyaudio.PyAudio()
            
            # Find input device
            input_device_index = self._get_input_device()
            
            # Open audio stream
            stream = audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=input_device_index,
                frames_per_buffer=self.chunk_size
            )
            
            logger.info("Recording audio...")
            frames = []
            
            if duration:
                # Record for specified duration
                frames_to_record = int(self.sample_rate / self.chunk_size * duration)
                for _ in range(frames_to_record):
                    data = stream.read(self.chunk_size)
                    frames.append(data)
            else:
                # Record until silence
                frames = await self._record_until_silence(stream)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Convert to WAV
            return self._frames_to_wav(frames)
            
        except Exception as e:
            logger.error(f"Error recording audio: {e}")
            return None
    
    async def _record_until_silence(self, stream) -> List[bytes]:
        """Record audio until silence is detected."""
        frames = []
        silence_threshold = 1000  # Adjust based on environment
        silent_chunks = 0
        max_silent_chunks = 30  # ~1 second of silence
        min_recording_chunks = 15  # Minimum recording time
        
        while True:
            data = stream.read(self.chunk_size)
            frames.append(data)
            
            # Analyze audio level
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.abs(audio_data).mean()
            
            if volume < silence_threshold:
                silent_chunks += 1
            else:
                silent_chunks = 0
            
            # Stop if we have enough silence and minimum recording time
            if (silent_chunks > max_silent_chunks and 
                len(frames) > min_recording_chunks):
                break
            
            # Safety limit
            if len(frames) > 1000:  # ~30 seconds max
                break
        
        return frames
    
    def _frames_to_wav(self, frames: List[bytes]) -> bytes:
        """Convert audio frames to WAV format."""
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(pyaudio.get_sample_size(self.format))
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(b''.join(frames))
        
        wav_buffer.seek(0)
        return wav_buffer.getvalue()
    
    def _get_input_device(self) -> Optional[int]:
        """Get the best available input device."""
        try:
            audio = pyaudio.PyAudio()
            
            # Look for default input device
            default_device = audio.get_default_input_device_info()
            if default_device:
                return default_device['index']
            
            # Fallback to any available input device
            for i in range(audio.get_device_count()):
                device_info = audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    return i
            
        except Exception as e:
            logger.warning(f"Could not find input device: {e}")
        
        return None
    
    def get_audio_devices(self) -> List[Dict]:
        """Get list of available audio devices."""
        devices = []
        
        try:
            audio = pyaudio.PyAudio()
            
            for i in range(audio.get_device_count()):
                device_info = audio.get_device_info_by_index(i)
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'max_input_channels': device_info['maxInputChannels'],
                    'max_output_channels': device_info['maxOutputChannels'],
                    'default_sample_rate': device_info['defaultSampleRate']
                })
            
            audio.terminate()
            
        except Exception as e:
            logger.error(f"Error getting audio devices: {e}")
        
        return devices
    
    async def convert_audio_format(
        self, 
        audio_data: bytes, 
        input_format: str, 
        output_format: str,
        target_sample_rate: Optional[int] = None
    ) -> Optional[bytes]:
        """
        Convert audio between different formats.
        
        Args:
            audio_data: Input audio data
            input_format: Input format (wav, mp3, etc.)
            output_format: Output format (wav, mp3, etc.)
            target_sample_rate: Target sample rate for conversion
            
        Returns:
            Converted audio data or None if conversion fails
        """
        try:
            # Save input to temporary file
            with tempfile.NamedTemporaryFile(suffix=f".{input_format}", delete=False) as input_file:
                input_file.write(audio_data)
                input_path = input_file.name
            
            # Load audio with librosa
            audio, sr = librosa.load(input_path, sr=target_sample_rate)
            
            # Save in output format
            with tempfile.NamedTemporaryFile(suffix=f".{output_format}", delete=False) as output_file:
                output_path = output_file.name
            
            # Use soundfile for output
            sf.write(output_path, audio, sr)
            
            # Read converted data
            with open(output_path, 'rb') as f:
                converted_data = f.read()
            
            # Clean up
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)
            
            return converted_data
            
        except Exception as e:
            logger.error(f"Error converting audio format: {e}")
            return None
    
    def analyze_audio(self, audio_data: bytes) -> Dict:
        """
        Analyze audio properties.
        
        Args:
            audio_data: Audio data to analyze
            
        Returns:
            Dictionary with audio properties
        """
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # Load with librosa
            audio, sr = librosa.load(temp_path)
            
            # Analyze properties
            properties = {
                'duration': len(audio) / sr,
                'sample_rate': sr,
                'channels': 1,  # librosa loads as mono by default
                'rms_energy': float(np.sqrt(np.mean(audio**2))),
                'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(audio))),
                'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(audio)[0])),
                'tempo': float(librosa.beat.tempo(audio)[0]) if len(audio) > sr else 0
            }
            
            # Clean up
            Path(temp_path).unlink(missing_ok=True)
            
            return properties
            
        except Exception as e:
            logger.error(f"Error analyzing audio: {e}")
            return {}
    
    def detect_silence(self, audio_data: bytes, threshold: float = 0.01) -> List[Tuple[float, float]]:
        """
        Detect silence segments in audio.
        
        Args:
            audio_data: Audio data to analyze
            threshold: Silence threshold (0.0 to 1.0)
            
        Returns:
            List of (start_time, end_time) tuples for silence segments
        """
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # Load audio
            audio, sr = librosa.load(temp_path)
            
            # Calculate RMS energy
            hop_length = 512
            frame_length = 2048
            rms = librosa.feature.rms(y=audio, frame_length=frame_length, hop_length=hop_length)[0]
            
            # Find silence frames
            silence_frames = rms < threshold
            
            # Convert frames to time segments
            times = librosa.frames_to_time(range(len(rms)), sr=sr, hop_length=hop_length)
            
            # Group consecutive silence frames
            silence_segments = []
            start_time = None
            
            for i, is_silent in enumerate(silence_frames):
                if is_silent and start_time is None:
                    start_time = times[i]
                elif not is_silent and start_time is not None:
                    silence_segments.append((start_time, times[i]))
                    start_time = None
            
            # Handle silence at end
            if start_time is not None:
                silence_segments.append((start_time, times[-1]))
            
            # Clean up
            Path(temp_path).unlink(missing_ok=True)
            
            return silence_segments
            
        except Exception as e:
            logger.error(f"Error detecting silence: {e}")
            return []
    
    def trim_silence(self, audio_data: bytes, threshold: float = 0.01) -> Optional[bytes]:
        """
        Remove silence from beginning and end of audio.
        
        Args:
            audio_data: Audio data to trim
            threshold: Silence threshold
            
        Returns:
            Trimmed audio data or None if processing fails
        """
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            # Load and trim audio
            audio, sr = librosa.load(temp_path)
            trimmed_audio, _ = librosa.effects.trim(audio, top_db=20)
            
            # Save trimmed audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output_file:
                output_path = output_file.name
            
            sf.write(output_path, trimmed_audio, sr)
            
            # Read trimmed data
            with open(output_path, 'rb') as f:
                trimmed_data = f.read()
            
            # Clean up
            Path(temp_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)
            
            return trimmed_data
            
        except Exception as e:
            logger.error(f"Error trimming silence: {e}")
            return None


# Convenience functions
async def play_audio_file(file_path: str) -> bool:
    """
    Play an audio file.
    
    Args:
        file_path: Path to audio file
        
    Returns:
        True if playback successful
    """
    try:
        with open(file_path, 'rb') as f:
            audio_data = f.read()
        
        utils = AudioUtils()
        return await utils.play_audio(audio_data)
    except Exception as e:
        logger.error(f"Error playing audio file: {e}")
        return False


async def record_audio_to_file(file_path: str, duration: Optional[float] = None) -> bool:
    """
    Record audio and save to file.
    
    Args:
        file_path: Output file path
        duration: Recording duration in seconds
        
    Returns:
        True if recording successful
    """
    try:
        utils = AudioUtils()
        audio_data = await utils.record_audio(duration)
        
        if audio_data:
            with open(file_path, 'wb') as f:
                f.write(audio_data)
            return True
        
        return False
    except Exception as e:
        logger.error(f"Error recording audio to file: {e}")
        return False