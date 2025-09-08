"""
Configuration management for Speak-to-LLM application.

Handles loading and managing configuration from files, environment variables,
and default settings.

Author: Benjamin Chidera
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

logger = logging.getLogger(__name__)


class Config:
    """
    Configuration manager for the Speak-to-LLM application.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_path: Optional path to configuration file
        """
        # Load environment variables
        if load_dotenv:
            load_dotenv()
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Parse component configurations
        self.stt_config = self._get_stt_config()
        self.tts_config = self._get_tts_config()
        self.llm_config = self._get_llm_config()
        self.audio_config = self._get_audio_config()
        
        logger.info("Configuration loaded successfully")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = self._get_default_config()
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                
                # Merge with defaults
                config = {**default_config, **file_config}
                logger.info(f"Configuration loaded from {config_path}")
                
            except Exception as e:
                logger.warning(f"Could not load config file {config_path}: {e}")
                config = default_config
        else:
            config = default_config
            logger.info("Using default configuration")
        
        # Override with environment variables
        self._override_with_env_vars(config)
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "stt": {
                "provider": "whisper_local",
                "whisper_model": "base",
                "language": "en",
                "sample_rate": 16000,
                "chunk_size": 1024,
                "channels": 1
            },
            "tts": {
                "provider": "pyttsx3",
                "language": "en",
                "speed": 150,
                "volume": 0.9,
                "voice_id": None
            },
            "llm": {
                "provider": "openai",
                "model_name": "gpt-3.5-turbo",
                "max_tokens": 150,
                "temperature": 0.7,
                "system_prompt": None
            },
            "audio": {
                "input_device": None,
                "output_device": None,
                "silence_threshold": 1000,
                "silence_duration": 1.0
            },
            "app": {
                "log_level": "INFO",
                "save_conversations": True,
                "conversation_dir": "./conversations"
            }
        }
    
    def _override_with_env_vars(self, config: Dict[str, Any]):
        """Override configuration with environment variables."""
        # API Keys
        if os.getenv("OPENAI_API_KEY"):
            config["stt"]["openai_api_key"] = os.getenv("OPENAI_API_KEY")
            config["llm"]["openai_api_key"] = os.getenv("OPENAI_API_KEY")
        
        if os.getenv("ELEVENLABS_API_KEY"):
            config["tts"]["elevenlabs_api_key"] = os.getenv("ELEVENLABS_API_KEY")
        
        if os.getenv("HUGGINGFACE_API_KEY"):
            config["llm"]["huggingface_api_key"] = os.getenv("HUGGINGFACE_API_KEY")
        
        # Provider overrides
        if os.getenv("STT_PROVIDER"):
            config["stt"]["provider"] = os.getenv("STT_PROVIDER")
        
        if os.getenv("TTS_PROVIDER"):
            config["tts"]["provider"] = os.getenv("TTS_PROVIDER")
        
        if os.getenv("LLM_PROVIDER"):
            config["llm"]["provider"] = os.getenv("LLM_PROVIDER")
        
        # Model overrides
        if os.getenv("LLM_MODEL"):
            config["llm"]["model_name"] = os.getenv("LLM_MODEL")
        
        if os.getenv("WHISPER_MODEL"):
            config["stt"]["whisper_model"] = os.getenv("WHISPER_MODEL")
        
        # Ollama URL
        if os.getenv("OLLAMA_URL"):
            config["llm"]["ollama_url"] = os.getenv("OLLAMA_URL")
    
    def _get_stt_config(self) -> Dict[str, Any]:
        """Get Speech-to-Text configuration."""
        return self.config.get("stt", {})
    
    def _get_tts_config(self) -> Dict[str, Any]:
        """Get Text-to-Speech configuration."""
        return self.config.get("tts", {})
    
    def _get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        return self.config.get("llm", {})
    
    def _get_audio_config(self) -> Dict[str, Any]:
        """Get audio configuration."""
        return self.config.get("audio", {})
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration."""
        return self.config.get("app", {})
    
    def save_config(self, file_path: str):
        """
        Save current configuration to file.
        
        Args:
            file_path: Path to save configuration file
        """
        try:
            # Remove sensitive information before saving
            safe_config = self._remove_sensitive_data(self.config.copy())
            
            with open(file_path, 'w') as f:
                json.dump(safe_config, f, indent=2)
            
            logger.info(f"Configuration saved to {file_path}")
            
        except Exception as e:
            logger.error(f"Could not save configuration: {e}")
    
    def _remove_sensitive_data(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data like API keys from config."""
        sensitive_keys = [
            "openai_api_key",
            "elevenlabs_api_key", 
            "huggingface_api_key",
            "azure_api_key",
            "google_api_key"
        ]
        
        def remove_keys(obj):
            if isinstance(obj, dict):
                return {k: remove_keys(v) for k, v in obj.items() if k not in sensitive_keys}
            elif isinstance(obj, list):
                return [remove_keys(item) for item in obj]
            else:
                return obj
        
        return remove_keys(config)
    
    def update_config(self, path: str, value: Any):
        """
        Update a configuration value.
        
        Args:
            path: Dot-separated path to configuration key (e.g., "stt.provider")
            value: New value
        """
        keys = path.split('.')
        current = self.config
        
        # Navigate to parent of target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the value
        current[keys[-1]] = value
        
        # Update component configs
        self.stt_config = self._get_stt_config()
        self.tts_config = self._get_tts_config()
        self.llm_config = self._get_llm_config()
        self.audio_config = self._get_audio_config()
        
        logger.info(f"Configuration updated: {path} = {value}")
    
    def get_config_value(self, path: str, default: Any = None) -> Any:
        """
        Get a configuration value by path.
        
        Args:
            path: Dot-separated path to configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = path.split('.')
        current = self.config
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def validate_config(self) -> List[str]:
        """
        Validate configuration and return list of issues.
        
        Returns:
            List of validation error messages
        """
        issues = []
        
        # Check for required API keys based on providers
        stt_provider = self.stt_config.get("provider")
        if stt_provider == "whisper_api" and not self.stt_config.get("openai_api_key"):
            issues.append("OpenAI API key required for Whisper API")
        
        tts_provider = self.tts_config.get("provider")
        if tts_provider == "elevenlabs" and not self.tts_config.get("elevenlabs_api_key"):
            issues.append("ElevenLabs API key required for ElevenLabs TTS")
        
        llm_provider = self.llm_config.get("provider")
        if llm_provider == "openai" and not self.llm_config.get("openai_api_key"):
            issues.append("OpenAI API key required for OpenAI LLM")
        
        # Check model compatibility
        if stt_provider == "whisper_local":
            whisper_model = self.stt_config.get("whisper_model", "base")
            valid_models = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
            if whisper_model not in valid_models:
                issues.append(f"Invalid Whisper model: {whisper_model}")
        
        # Check numeric ranges
        temperature = self.llm_config.get("temperature", 0.7)
        if not 0.0 <= temperature <= 2.0:
            issues.append("LLM temperature must be between 0.0 and 2.0")
        
        volume = self.tts_config.get("volume", 0.9)
        if not 0.0 <= volume <= 1.0:
            issues.append("TTS volume must be between 0.0 and 1.0")
        
        return issues


# Global configuration instance
_config_instance = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    Get the global configuration instance.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        Configuration instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = Config(config_path)
    
    return _config_instance


def reload_config(config_path: Optional[str] = None):
    """
    Reload the global configuration.
    
    Args:
        config_path: Optional path to configuration file
    """
    global _config_instance
    _config_instance = Config(config_path)