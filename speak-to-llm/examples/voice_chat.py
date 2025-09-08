#!/usr/bin/env python3
"""
Voice chat example for Speak-to-LLM application.

This example demonstrates a full voice conversation with the AI assistant.

Author: Benjamin Chidera
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from speak_to_llm import SpeakToLLM


async def voice_chat_example():
    """Full voice chat example."""
    print("🎤 Voice Chat Example")
    print("=" * 30)
    print("This example will start a voice conversation with the AI.")
    print("Make sure you have a microphone connected and working.")
    print("Say 'goodbye', 'exit', 'quit', or 'stop' to end the conversation.")
    
    input("\nPress Enter to start the voice chat...")
    
    try:
        # Initialize the application
        app = SpeakToLLM()
        
        # Start voice conversation
        await app.start_conversation()
        
        # Show conversation history
        history = app.get_conversation_history()
        if history:
            print("\n📝 Conversation Summary:")
            print("-" * 30)
            for i, message in enumerate(history):
                role = "You" if message["role"] == "user" else "AI"
                content = message["content"][:100] + "..." if len(message["content"]) > 100 else message["content"]
                print(f"{i+1}. {role}: {content}")
        
        print("\n✅ Voice chat completed!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Voice chat interrupted by user")
    except Exception as e:
        print(f"❌ Error during voice chat: {e}")
        print("Possible issues:")
        print("  - Microphone not available or not working")
        print("  - Audio dependencies not installed")
        print("  - API keys not configured")
        print("  - Network connectivity issues")


async def quick_voice_test():
    """Quick test of individual voice components."""
    print("\n🔧 Quick Voice Component Test")
    print("=" * 40)
    
    try:
        app = SpeakToLLM()
        
        # Test TTS
        print("1. Testing Text-to-Speech...")
        await app.speak_response("Testing text to speech functionality.")
        
        # Test STT (record a short message)
        print("\n2. Testing Speech-to-Text...")
        print("Please say something for 3 seconds...")
        
        # Record for 3 seconds
        audio_data = await app.speech_recognizer.listen(duration=3.0)
        if audio_data:
            text = await app.speech_recognizer.transcribe(audio_data)
            print(f"You said: '{text}'")
            
            # Generate response
            response = await app.process_text_with_llm(text)
            print(f"AI response: '{response}'")
            
            # Speak the response
            await app.speak_response(response)
        else:
            print("No audio captured")
        
        print("\n✅ Component test completed!")
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")


def main():
    """Main function."""
    print("🎙️ Speak-to-LLM Voice Chat")
    print("=" * 40)
    
    # Check audio dependencies
    try:
        import pyaudio
        import pygame
        print("✅ Audio dependencies available")
    except ImportError as e:
        print(f"❌ Missing audio dependencies: {e}")
        print("Please install: pip install pyaudio pygame")
        return
    
    # Choose test type
    print("\nVoice Tests:")
    print("1. Full Voice Chat")
    print("2. Quick Component Test")
    
    choice = input("\nSelect test (1-2): ").strip()
    
    if choice == "1":
        asyncio.run(voice_chat_example())
    elif choice == "2":
        asyncio.run(quick_voice_test())
    else:
        print("Invalid selection")


if __name__ == "__main__":
    main()