#!/usr/bin/env python3
"""
Basic usage example for Speak-to-LLM application.

This example demonstrates how to use the main SpeakToLLM class
for basic voice conversations.

Author: Benjamin Chidera
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from speak_to_llm import SpeakToLLM


async def basic_example():
    """Basic usage example."""
    print("🎤 Speak-to-LLM Basic Example")
    print("=" * 40)
    
    try:
        # Initialize the application
        print("Initializing Speak-to-LLM...")
        app = SpeakToLLM()
        
        # Test text-to-speech
        print("\n1. Testing Text-to-Speech...")
        await app.speak_response("Hello! I am your AI assistant.")
        
        # Test text processing with LLM
        print("\n2. Testing LLM Processing...")
        response = await app.process_text_input("What is the capital of France?")
        print(f"LLM Response: {response}")
        
        # Test full conversation (commented out for demo)
        # print("\n3. Starting Voice Conversation...")
        # print("Say 'goodbye' to exit")
        # await app.start_conversation()
        
        print("\n✅ Basic example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have the required dependencies installed and API keys configured.")


async def text_only_example():
    """Text-only interaction example."""
    print("\n🔤 Text-Only Interaction Example")
    print("=" * 40)
    
    try:
        app = SpeakToLLM()
        
        # Simulate a conversation
        questions = [
            "Hello, who are you?",
            "Can you help me with programming?",
            "What is machine learning?",
            "Thank you for your help!"
        ]
        
        for question in questions:
            print(f"\nUser: {question}")
            response = await app.process_text_input(question)
            print(f"Assistant: {response}")
            
            # Add small delay for readability
            await asyncio.sleep(1)
        
        print("\n✅ Text-only example completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


async def configuration_example():
    """Example showing different configuration options."""
    print("\n⚙️ Configuration Example")
    print("=" * 40)
    
    try:
        # Custom configuration
        from src.utils.config import Config
        
        # Create custom config
        config = Config()
        
        # Show current configuration
        print("Current STT Provider:", config.stt_config.get('provider'))
        print("Current TTS Provider:", config.tts_config.get('provider'))
        print("Current LLM Provider:", config.llm_config.get('provider'))
        
        # Validate configuration
        issues = config.validate_config()
        if issues:
            print("\nConfiguration Issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("\n✅ Configuration is valid!")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")


def main():
    """Main function to run examples."""
    print("🎯 Speak-to-LLM Examples")
    print("=" * 50)
    
    # Choose which example to run
    examples = {
        "1": ("Basic Example", basic_example),
        "2": ("Text-Only Example", text_only_example),
        "3": ("Configuration Example", configuration_example),
        "4": ("All Examples", None)
    }
    
    print("\nAvailable Examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    choice = input("\nSelect an example (1-4): ").strip()
    
    if choice == "4":
        # Run all examples
        async def run_all():
            await basic_example()
            await text_only_example()
            await configuration_example()
        
        asyncio.run(run_all())
    elif choice in examples:
        name, func = examples[choice]
        if func:
            print(f"\nRunning: {name}")
            asyncio.run(func())
        else:
            print("Invalid selection")
    else:
        print("Invalid selection")


if __name__ == "__main__":
    main()