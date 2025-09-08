"""
Speak-to-LLM: A comprehensive text-to-speech, speech-to-text, and LLM integration application.

This module provides the main SpeakToLLM class that orchestrates the entire workflow:
1. Speech-to-Text conversion
2. LLM processing
3. Text-to-Speech output

Author: Benjamin Chidera
Email: benjaminchidera72@gmail.com
"""

import asyncio
import logging
from typing import Optional, Dict, Any

from .stt.speech_recognizer import SpeechRecognizer
from .tts.speech_synthesizer import SpeechSynthesizer
from .llm.llm_processor import LLMProcessor
from .utils.audio_utils import AudioUtils
from .utils.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SpeakToLLM:
    """
    Main application class that integrates speech-to-text, LLM processing, and text-to-speech.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Speak-to-LLM application.
        
        Args:
            config_path: Optional path to configuration file
        """
        self.config = Config(config_path)
        
        # Initialize components
        self.speech_recognizer = SpeechRecognizer(self.config.stt_config)
        self.speech_synthesizer = SpeechSynthesizer(self.config.tts_config)
        self.llm_processor = LLMProcessor(self.config.llm_config)
        self.audio_utils = AudioUtils()
        
        self.is_listening = False
        self.conversation_history = []
        
        logger.info("Speak-to-LLM initialized successfully")
    
    async def process_voice_input(self) -> Optional[str]:
        """
        Capture and process voice input.
        
        Returns:
            Transcribed text or None if recognition fails
        """
        try:
            logger.info("Listening for voice input...")
            audio_data = await self.speech_recognizer.listen()
            
            if audio_data:
                text = await self.speech_recognizer.transcribe(audio_data)
                logger.info(f"Transcribed: {text}")
                return text
            
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
        
        return None
    
    async def process_text_with_llm(self, text: str) -> Optional[str]:
        """
        Process text through the LLM.
        
        Args:
            text: Input text to process
            
        Returns:
            LLM response or None if processing fails
        """
        try:
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": text})
            
            # Process with LLM
            response = await self.llm_processor.generate_response(
                text, 
                conversation_history=self.conversation_history
            )
            
            if response:
                self.conversation_history.append({"role": "assistant", "content": response})
                logger.info(f"LLM Response: {response}")
                return response
                
        except Exception as e:
            logger.error(f"Error processing with LLM: {e}")
        
        return None
    
    async def speak_response(self, text: str) -> bool:
        """
        Convert text to speech and play it.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info("Converting text to speech...")
            audio_data = await self.speech_synthesizer.synthesize(text)
            
            if audio_data:
                await self.audio_utils.play_audio(audio_data)
                return True
                
        except Exception as e:
            logger.error(f"Error in text-to-speech: {e}")
        
        return False
    
    async def process_conversation_turn(self) -> bool:
        """
        Process one complete conversation turn: listen -> LLM -> speak.
        
        Returns:
            True if the turn was processed successfully, False otherwise
        """
        # Step 1: Voice input
        user_text = await self.process_voice_input()
        if not user_text:
            return False
        
        # Step 2: LLM processing
        llm_response = await self.process_text_with_llm(user_text)
        if not llm_response:
            return False
        
        # Step 3: Voice output
        success = await self.speak_response(llm_response)
        return success
    
    async def start_conversation(self):
        """
        Start an interactive voice conversation.
        """
        logger.info("Starting voice conversation. Say 'goodbye' to exit.")
        
        try:
            self.is_listening = True
            
            # Welcome message
            welcome_msg = "Hello! I'm your AI assistant. How can I help you today?"
            await self.speak_response(welcome_msg)
            
            while self.is_listening:
                success = await self.process_conversation_turn()
                
                if not success:
                    logger.warning("Failed to process conversation turn")
                    continue
                
                # Check for exit condition
                if (self.conversation_history and 
                    any(word in self.conversation_history[-2]["content"].lower() 
                        for word in ["goodbye", "exit", "quit", "stop"])):
                    break
                
                # Small delay between turns
                await asyncio.sleep(0.5)
            
        except KeyboardInterrupt:
            logger.info("Conversation interrupted by user")
        except Exception as e:
            logger.error(f"Error in conversation: {e}")
        finally:
            self.is_listening = False
            goodbye_msg = "Goodbye! Have a great day!"
            await self.speak_response(goodbye_msg)
    
    async def process_text_input(self, text: str) -> Optional[str]:
        """
        Process text input directly (without speech-to-text).
        
        Args:
            text: Input text
            
        Returns:
            LLM response
        """
        response = await self.process_text_with_llm(text)
        return response
    
    def get_conversation_history(self) -> list:
        """Get the current conversation history."""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")


# Convenience function for quick usage
async def quick_chat(message: str) -> str:
    """
    Quick function to get an LLM response for a text message.
    
    Args:
        message: Input message
        
    Returns:
        LLM response
    """
    app = SpeakToLLM()
    response = await app.process_text_input(message)
    return response or "Sorry, I couldn't process that."


if __name__ == "__main__":
    # Example usage
    async def main():
        app = SpeakToLLM()
        await app.start_conversation()
    
    asyncio.run(main())