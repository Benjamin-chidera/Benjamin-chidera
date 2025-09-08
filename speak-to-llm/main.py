#!/usr/bin/env python3
"""
Main entry point for the Speak-to-LLM application.

This script provides a command-line interface to run the application
with different modes and configurations.

Author: Benjamin Chidera
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src import SpeakToLLM
from src.utils.config import Config


def create_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Speak-to-LLM: AI-powered voice assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                          # Start interactive voice chat
  python main.py --text-only              # Text-only chat mode
  python main.py --config custom.json     # Use custom configuration
  python main.py --stt-provider whisper_api --llm-provider openai
        """
    )
    
    # Mode selection
    parser.add_argument(
        "--mode", 
        choices=["voice", "text", "demo"],
        default="voice",
        help="Interaction mode (default: voice)"
    )
    
    parser.add_argument(
        "--text-only",
        action="store_true",
        help="Run in text-only mode (no voice)"
    )
    
    # Configuration
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    
    # Provider overrides
    parser.add_argument(
        "--stt-provider",
        choices=["whisper_local", "whisper_api", "google"],
        help="Speech-to-text provider"
    )
    
    parser.add_argument(
        "--tts-provider", 
        choices=["pyttsx3", "gtts", "elevenlabs", "openai"],
        help="Text-to-speech provider"
    )
    
    parser.add_argument(
        "--llm-provider",
        choices=["openai", "huggingface", "ollama"],
        help="LLM provider"
    )
    
    # Model selection
    parser.add_argument(
        "--llm-model",
        type=str,
        help="LLM model name"
    )
    
    parser.add_argument(
        "--whisper-model",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size"
    )
    
    # Utility commands
    parser.add_argument(
        "--test-audio",
        action="store_true",
        help="Test audio input/output devices"
    )
    
    parser.add_argument(
        "--validate-config",
        action="store_true", 
        help="Validate configuration and exit"
    )
    
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio devices"
    )
    
    return parser


async def run_voice_mode(app):
    """Run in voice conversation mode."""
    print("🎤 Starting voice conversation mode...")
    print("Say 'goodbye', 'exit', 'quit', or 'stop' to end the conversation.")
    print("Press Ctrl+C to interrupt.\n")
    
    try:
        await app.start_conversation()
    except KeyboardInterrupt:
        print("\n⏹️ Conversation interrupted by user")


async def run_text_mode(app):
    """Run in text-only mode."""
    print("💬 Starting text conversation mode...")
    print("Type 'quit', 'exit', or 'goodbye' to end the conversation.\n")
    
    try:
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'goodbye', 'stop']:
                print("AI: Goodbye! Have a great day!")
                break
            
            if not user_input:
                continue
            
            response = await app.process_text_input(user_input)
            print(f"AI: {response}\n")
            
    except KeyboardInterrupt:
        print("\n⏹️ Conversation interrupted by user")
    except EOFError:
        print("\n👋 Goodbye!")


async def run_demo_mode(app):
    """Run demonstration mode."""
    print("🎯 Running demonstration mode...\n")
    
    # Demo conversation
    demo_inputs = [
        "Hello, who are you?",
        "What can you help me with?", 
        "Tell me about artificial intelligence",
        "Thank you for the information!"
    ]
    
    for i, input_text in enumerate(demo_inputs, 1):
        print(f"Demo {i}: {input_text}")
        response = await app.process_text_input(input_text)
        print(f"AI: {response}\n")
        
        # Speak the response
        await app.speak_response(response)
        
        # Pause between demo steps
        await asyncio.sleep(2)
    
    print("✅ Demo completed!")


async def test_audio_devices():
    """Test audio input/output devices."""
    print("🔧 Testing audio devices...\n")
    
    try:
        from src.utils.audio_utils import AudioUtils
        
        audio_utils = AudioUtils()
        devices = audio_utils.get_audio_devices()
        
        print("Available Audio Devices:")
        print("-" * 40)
        
        for device in devices:
            device_type = []
            if device['max_input_channels'] > 0:
                device_type.append("Input")
            if device['max_output_channels'] > 0:
                device_type.append("Output")
            
            print(f"Device {device['index']}: {device['name']}")
            print(f"  Type: {', '.join(device_type)}")
            print(f"  Sample Rate: {device['default_sample_rate']}")
            print()
        
        # Test recording
        print("Testing microphone (3 seconds)...")
        audio_data = await audio_utils.record_audio(duration=3.0)
        
        if audio_data:
            print("✅ Microphone test successful!")
            
            # Analyze audio
            properties = audio_utils.analyze_audio(audio_data)
            if properties:
                print(f"Audio duration: {properties.get('duration', 'unknown')} seconds")
                print(f"Audio energy: {properties.get('rms_energy', 'unknown')}")
        else:
            print("❌ Microphone test failed!")
            
    except Exception as e:
        print(f"❌ Audio test failed: {e}")


def validate_configuration(config_path=None):
    """Validate configuration."""
    print("⚙️ Validating configuration...\n")
    
    try:
        config = Config(config_path)
        issues = config.validate_config()
        
        if not issues:
            print("✅ Configuration is valid!")
            
            # Show current settings
            print("\nCurrent Configuration:")
            print(f"  STT Provider: {config.stt_config.get('provider')}")
            print(f"  TTS Provider: {config.tts_config.get('provider')}")
            print(f"  LLM Provider: {config.llm_config.get('provider')}")
            print(f"  LLM Model: {config.llm_config.get('model_name')}")
        else:
            print("❌ Configuration issues found:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    return True


async def main():
    """Main function."""
    parser = create_parser()
    args = parser.parse_args()
    
    print("🎯 Speak-to-LLM Application")
    print("=" * 40)
    
    # Handle utility commands
    if args.list_devices:
        await test_audio_devices()
        return
    
    if args.test_audio:
        await test_audio_devices()
        return
    
    if args.validate_config:
        validate_configuration(args.config)
        return
    
    # Load configuration
    try:
        config = Config(args.config)
        
        # Apply command line overrides
        if args.stt_provider:
            config.update_config("stt.provider", args.stt_provider)
        
        if args.tts_provider:
            config.update_config("tts.provider", args.tts_provider)
            
        if args.llm_provider:
            config.update_config("llm.provider", args.llm_provider)
            
        if args.llm_model:
            config.update_config("llm.model_name", args.llm_model)
            
        if args.whisper_model:
            config.update_config("stt.whisper_model", args.whisper_model)
        
        # Validate configuration
        if not validate_configuration():
            print("\nPlease fix configuration issues before continuing.")
            return
        
        # Initialize application
        print("\n🚀 Initializing Speak-to-LLM...")
        app = SpeakToLLM(args.config)
        
        # Determine mode
        if args.text_only:
            mode = "text"
        else:
            mode = args.mode
        
        # Run application
        if mode == "voice":
            await run_voice_mode(app)
        elif mode == "text":
            await run_text_mode(app)
        elif mode == "demo":
            await run_demo_mode(app)
        
    except Exception as e:
        print(f"❌ Application error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check your configuration and API keys")
        print("  2. Verify audio devices are working")
        print("  3. Run --validate-config to check setup")
        print("  4. Try --test-audio to test audio devices")


if __name__ == "__main__":
    asyncio.run(main())