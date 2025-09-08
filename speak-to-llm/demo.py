#!/usr/bin/env python3
"""
Demo script for Speak-to-LLM that works without external dependencies.

This demonstrates the project structure and basic functionality
without requiring API keys or audio libraries.

Author: Benjamin Chidera
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demo_configuration():
    """Demo configuration management."""
    print("🔧 Configuration Demo")
    print("=" * 30)
    
    try:
        from utils.config import Config
        
        config = Config()
        print("✅ Configuration loaded successfully")
        
        print(f"STT Provider: {config.stt_config.get('provider')}")
        print(f"TTS Provider: {config.tts_config.get('provider')}")
        print(f"LLM Provider: {config.llm_config.get('provider')}")
        
        # Test configuration validation
        issues = config.validate_config()
        if issues:
            print(f"\nConfiguration issues (expected without API keys):")
            for issue in issues:
                print(f"  - {issue}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration demo failed: {e}")
        return False

def demo_project_structure():
    """Demo project structure."""
    print("\n📁 Project Structure Demo")
    print("=" * 30)
    
    structure = {
        "src/": "Core application code",
        "src/stt/": "Speech-to-Text modules", 
        "src/tts/": "Text-to-Speech modules",
        "src/llm/": "LLM integration",
        "src/utils/": "Utility functions",
        "examples/": "Usage examples",
        "tests/": "Test suite",
        "docs/": "Documentation"
    }
    
    for path, description in structure.items():
        full_path = os.path.join(os.path.dirname(__file__), path)
        exists = "✅" if os.path.exists(full_path) else "❌"
        print(f"{exists} {path:<15} - {description}")
    
    return True

def demo_features():
    """Demo key features."""
    print("\n🚀 Features Demo")
    print("=" * 30)
    
    features = [
        "🎤 Multiple STT providers (Whisper, Google, etc.)",
        "🗣️ Multiple TTS providers (pyttsx3, ElevenLabs, etc.)", 
        "🧠 Multiple LLM providers (OpenAI, Ollama, HuggingFace)",
        "⚙️ Flexible configuration management",
        "🔧 Audio processing utilities",
        "📝 Example scripts and documentation",
        "🧪 Test suite for validation",
        "🎯 Command-line interface with multiple modes"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    return True

def demo_usage():
    """Demo basic usage patterns."""
    print("\n💡 Usage Examples")
    print("=" * 30)
    
    print("Basic text processing (when dependencies are available):")
    print("```python")
    print("from src import SpeakToLLM")
    print("")
    print("app = SpeakToLLM()")
    print("response = await app.process_text_input('Hello!')")
    print("print(response)")
    print("```")
    
    print("\nVoice conversation:")
    print("```python")
    print("await app.start_conversation()")
    print("```")
    
    print("\nCommand line usage:")
    print("```bash")
    print("python main.py --mode voice")
    print("python main.py --text-only")
    print("python main.py --validate-config")
    print("```")
    
    return True

def main():
    """Run the demo."""
    print("🎯 Speak-to-LLM Project Demo")
    print("Created a text to speech-speech to text/llm integration application")
    print("=" * 60)
    
    demos = [
        demo_project_structure,
        demo_configuration,
        demo_features,
        demo_usage
    ]
    
    results = []
    for demo in demos:
        try:
            result = demo()
            results.append(result)
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Demo Summary")
    print("=" * 60)
    
    successful = sum(results)
    total = len(results)
    
    print(f"Demo sections completed: {successful}/{total}")
    
    if successful == total:
        print("🎉 All demos completed successfully!")
        print("\n📖 Next Steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Configure API keys in .env file")
        print("  3. Run: python main.py --validate-config")
        print("  4. Start with: python examples/basic_usage.py")
    else:
        print("⚠️ Some demos had issues")
    
    return 0 if successful == total else 1

if __name__ == "__main__":
    exit(main())