"""
Tests for the Speak-to-LLM application.

Basic test suite to verify core functionality.

Author: Benjamin Chidera
"""

import pytest
import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.config import Config
from utils.audio_utils import AudioUtils


class TestConfig:
    """Test configuration management."""
    
    def test_default_config(self):
        """Test default configuration loading."""
        config = Config()
        
        assert config.stt_config is not None
        assert config.tts_config is not None
        assert config.llm_config is not None
        assert config.audio_config is not None
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = Config()
        issues = config.validate_config()
        
        # Should be a list (may contain issues due to missing API keys)
        assert isinstance(issues, list)
    
    def test_config_update(self):
        """Test configuration updates."""
        config = Config()
        
        # Update a config value
        config.update_config("stt.provider", "whisper_local")
        assert config.stt_config["provider"] == "whisper_local"
        
        # Test getting config value
        value = config.get_config_value("stt.provider")
        assert value == "whisper_local"


class TestAudioUtils:
    """Test audio utilities."""
    
    def test_audio_utils_init(self):
        """Test AudioUtils initialization."""
        audio_utils = AudioUtils()
        
        assert audio_utils.sample_rate > 0
        assert audio_utils.channels > 0
        assert audio_utils.chunk_size > 0
    
    def test_get_audio_devices(self):
        """Test getting audio devices."""
        audio_utils = AudioUtils()
        devices = audio_utils.get_audio_devices()
        
        # Should return a list (may be empty if no audio devices)
        assert isinstance(devices, list)


@pytest.mark.asyncio
class TestAsyncFunctionality:
    """Test async functionality."""
    
    async def test_audio_processing(self):
        """Test basic audio processing."""
        audio_utils = AudioUtils()
        
        # Test with dummy audio data
        dummy_audio = b'dummy_audio_data'
        properties = audio_utils.analyze_audio(dummy_audio)
        
        # Should return a dict (may be empty if processing fails)
        assert isinstance(properties, dict)


class TestImports:
    """Test that required modules can be imported."""
    
    def test_core_imports(self):
        """Test core module imports."""
        try:
            from utils.config import Config
            from utils.audio_utils import AudioUtils
            assert True
        except ImportError as e:
            pytest.fail(f"Core import failed: {e}")
    
    def test_optional_imports(self):
        """Test optional dependency imports."""
        optional_imports = [
            ('openai', 'OpenAI client'),
            ('whisper', 'Whisper model'),
            ('transformers', 'Hugging Face transformers'),
            ('pyttsx3', 'Text-to-speech engine'),
            ('pyaudio', 'Audio processing'),
            ('pygame', 'Audio playback')
        ]
        
        for module_name, description in optional_imports:
            try:
                __import__(module_name)
                print(f"✅ {description} available")
            except ImportError:
                print(f"⚠️ {description} not available (optional)")


def test_project_structure():
    """Test that project structure is correct."""
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    
    # Check key directories exist
    required_dirs = [
        'src',
        'src/stt',
        'src/tts', 
        'src/llm',
        'src/utils',
        'examples',
        'tests',
        'docs'
    ]
    
    for dir_path in required_dirs:
        full_path = os.path.join(base_dir, dir_path)
        assert os.path.exists(full_path), f"Directory {dir_path} should exist"
    
    # Check key files exist
    required_files = [
        'README.md',
        'requirements.txt',
        'package.json',
        '.env.example',
        'src/__init__.py'
    ]
    
    for file_path in required_files:
        full_path = os.path.join(base_dir, file_path)
        assert os.path.exists(full_path), f"File {file_path} should exist"


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])