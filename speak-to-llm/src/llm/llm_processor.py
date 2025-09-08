"""
Large Language Model (LLM) processor for generating intelligent responses.

Supports multiple LLM providers:
- OpenAI GPT models
- Hugging Face Transformers
- Ollama (local models)
- Anthropic Claude
- Custom models

Author: Benjamin Chidera
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Union
import json
import aiohttp

try:
    from openai import OpenAI
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
    from langchain.llms import OpenAI as LangChainOpenAI
    from langchain.llms import Ollama
    from langchain.schema import HumanMessage, AIMessage, SystemMessage
except ImportError as e:
    logging.warning(f"Some LLM dependencies not available: {e}")

logger = logging.getLogger(__name__)


class LLMProcessor:
    """
    Large Language Model processor for generating intelligent responses.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the LLM processor.
        
        Args:
            config: Configuration dictionary containing LLM settings
        """
        self.config = config
        self.provider = config.get("provider", "openai")
        self.model_name = config.get("model_name", "gpt-3.5-turbo")
        self.max_tokens = config.get("max_tokens", 150)
        self.temperature = config.get("temperature", 0.7)
        self.system_prompt = config.get("system_prompt", self._default_system_prompt())
        
        # Initialize components based on provider
        self._initialize_provider()
        
        logger.info(f"LLMProcessor initialized with provider: {self.provider}")
    
    def _default_system_prompt(self) -> str:
        """Default system prompt for the AI assistant."""
        return """You are a helpful and friendly AI assistant with voice capabilities. 
        You can engage in natural conversations through speech. 
        Keep your responses conversational, concise, and appropriate for spoken dialogue.
        Avoid using special characters, formatting, or overly long explanations unless specifically requested.
        When speaking, use natural language that sounds good when read aloud."""
    
    def _initialize_provider(self):
        """Initialize the selected LLM provider."""
        try:
            if self.provider == "openai":
                self.client = OpenAI(api_key=self.config.get("openai_api_key"))
                logger.info("OpenAI client initialized")
                
            elif self.provider == "huggingface":
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None
                )
                logger.info(f"Hugging Face model {self.model_name} loaded")
                
            elif self.provider == "ollama":
                self.ollama_url = self.config.get("ollama_url", "http://localhost:11434")
                logger.info(f"Ollama client initialized for {self.ollama_url}")
                
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider: {e}")
            raise
    
    async def generate_response(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> Optional[str]:
        """
        Generate a response to the given message.
        
        Args:
            message: User message
            conversation_history: Previous conversation messages
            **kwargs: Additional parameters for generation
            
        Returns:
            Generated response or None if generation fails
        """
        try:
            if self.provider == "openai":
                return await self._generate_openai(message, conversation_history, **kwargs)
            elif self.provider == "huggingface":
                return await self._generate_huggingface(message, conversation_history, **kwargs)
            elif self.provider == "ollama":
                return await self._generate_ollama(message, conversation_history, **kwargs)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return None
    
    async def _generate_openai(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """Generate response using OpenAI API."""
        # Build messages array
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history
        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 messages
                messages.append(msg)
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Generate response
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", self.temperature),
                stream=False
            )
        )
        
        return response.choices[0].message.content.strip()
    
    async def _generate_huggingface(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """Generate response using Hugging Face model."""
        # Build conversation context
        context = self.system_prompt + "\n\n"
        
        if conversation_history:
            for msg in conversation_history[-5:]:  # Keep last 5 messages
                role = "Human" if msg["role"] == "user" else "Assistant"
                context += f"{role}: {msg['content']}\n"
        
        context += f"Human: {message}\nAssistant:"
        
        # Tokenize input
        inputs = self.tokenizer.encode(context, return_tensors="pt")
        
        # Generate response
        with torch.no_grad():
            outputs = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.generate(
                    inputs,
                    max_new_tokens=kwargs.get("max_tokens", self.max_tokens),
                    temperature=kwargs.get("temperature", self.temperature),
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            )
        
        # Decode response
        response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
        return response.strip()
    
    async def _generate_ollama(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> str:
        """Generate response using Ollama."""
        # Build conversation context
        context = self.system_prompt + "\n\n"
        
        if conversation_history:
            for msg in conversation_history[-5:]:
                role = "Human" if msg["role"] == "user" else "Assistant"
                context += f"{role}: {msg['content']}\n"
        
        prompt = context + f"Human: {message}\nAssistant:"
        
        # Make request to Ollama API
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", self.temperature),
                    "num_predict": kwargs.get("max_tokens", self.max_tokens)
                }
            }
            
            async with session.post(f"{self.ollama_url}/api/generate", json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get("response", "").strip()
                else:
                    raise Exception(f"Ollama API error: {response.status}")
    
    async def generate_streaming_response(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Generate a streaming response (yields chunks as they're generated).
        
        Args:
            message: User message
            conversation_history: Previous conversation messages
            
        Yields:
            Response chunks as they're generated
        """
        if self.provider == "openai":
            async for chunk in self._generate_openai_streaming(message, conversation_history):
                yield chunk
        else:
            # For non-streaming providers, yield the complete response
            response = await self.generate_response(message, conversation_history)
            if response:
                yield response
    
    async def _generate_openai_streaming(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using OpenAI API."""
        # Build messages array
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if conversation_history:
            for msg in conversation_history[-10:]:
                messages.append(msg)
        
        messages.append({"role": "user", "content": message})
        
        # Create streaming response
        stream = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=True
            )
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    async def summarize_conversation(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Generate a summary of the conversation history.
        
        Args:
            conversation_history: List of conversation messages
            
        Returns:
            Conversation summary
        """
        if not conversation_history:
            return "No conversation to summarize."
        
        # Build summary prompt
        conversation_text = "\n".join([
            f"{msg['role'].title()}: {msg['content']}" 
            for msg in conversation_history
        ])
        
        summary_prompt = f"""Please provide a brief summary of this conversation:

{conversation_text}

Summary:"""
        
        response = await self.generate_response(summary_prompt)
        return response or "Unable to generate summary."
    
    def set_system_prompt(self, prompt: str):
        """Set a custom system prompt."""
        self.system_prompt = prompt
        logger.info("System prompt updated")
    
    def set_temperature(self, temperature: float):
        """Set the generation temperature."""
        self.temperature = max(0.0, min(2.0, temperature))
        logger.info(f"Temperature set to: {self.temperature}")
    
    def set_max_tokens(self, max_tokens: int):
        """Set the maximum number of tokens to generate."""
        self.max_tokens = max(1, max_tokens)
        logger.info(f"Max tokens set to: {self.max_tokens}")


# Convenience functions
async def chat_with_llm(message: str, provider: str = "openai", model: str = "gpt-3.5-turbo") -> str:
    """
    Quick function to chat with an LLM.
    
    Args:
        message: User message
        provider: LLM provider to use
        model: Model name
        
    Returns:
        LLM response
    """
    config = {"provider": provider, "model_name": model}
    processor = LLMProcessor(config)
    response = await processor.generate_response(message)
    return response or "Sorry, I couldn't generate a response."


async def get_conversation_summary(conversation: List[Dict[str, str]], provider: str = "openai") -> str:
    """
    Quick function to summarize a conversation.
    
    Args:
        conversation: List of conversation messages
        provider: LLM provider to use
        
    Returns:
        Conversation summary
    """
    config = {"provider": provider}
    processor = LLMProcessor(config)
    return await processor.summarize_conversation(conversation)