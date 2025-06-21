"""AI provider implementations for Jarvis HAL."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict, Any, Optional, Generator
import openai
import anthropic
import google.generativeai as genai
from loguru import logger
import asyncio
from pydantic import SecretStr

class AIProvider(ABC):
    """Base class for AI providers."""
    
    def __init__(self, api_key: SecretStr, model: str, temperature: float = 0.7, max_tokens: int = 1024):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """Generate a response from the AI model."""
        pass

    def generate_response_sync(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Synchronous version of generate_response."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            async_gen = self.generate_response(messages)
            while True:
                try:
                    chunk = loop.run_until_complete(async_gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
        finally:
            loop.close()

class OpenAIProvider(AIProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, api_key: SecretStr, model: str, temperature: float = 0.7, max_tokens: int = 1024):
        super().__init__(api_key, model, temperature, max_tokens)
        self.client = openai.AsyncOpenAI(api_key=api_key.get_secret_value())

    async def generate_response(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            yield f"Error: {str(e)}"

class AnthropicProvider(AIProvider):
    """Anthropic provider implementation."""
    
    def __init__(self, api_key: SecretStr, model: str, temperature: float = 0.7, max_tokens: int = 1024):
        super().__init__(api_key, model, temperature, max_tokens)
        self.client = anthropic.AsyncAnthropic(api_key=api_key.get_secret_value())

    async def generate_response(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        try:
            # Convert messages to Anthropic format
            prompt = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages]) + "\nAssistant:"
            response = await self.client.completions.create(
                model=self.model,
                prompt=prompt,
                temperature=self.temperature,
                max_tokens_to_sample=self.max_tokens,
                stream=True
            )
            async for chunk in response:
                if chunk.completion:
                    yield chunk.completion
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            yield f"Error: {str(e)}"

class GeminiProvider(AIProvider):
    """Google Gemini provider implementation."""
    
    def __init__(self, api_key: SecretStr, model: str, temperature: float = 0.7, max_tokens: int = 1024):
        super().__init__(api_key, model, temperature, max_tokens)
        genai.configure(api_key=api_key.get_secret_value())
        self.model = genai.GenerativeModel(model)

    async def generate_response(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        try:
            # Filter out system messages and convert to Gemini format
            filtered_messages = []
            system_content = None
            
            for message in messages:
                if message["role"] == "system":
                    system_content = message["content"]
                else:
                    filtered_messages.append(message)
            
            # Convert to Gemini format
            history = []
            for message in filtered_messages:
                if message["role"] == "user":
                    history.append({"role": "user", "parts": [message["content"]]})
                elif message["role"] == "assistant":
                    history.append({"role": "model", "parts": [message["content"]]})
            
            # If we have system content, prepend it to the first user message
            if system_content and history:
                if history[0]["role"] == "user":
                    history[0]["parts"][0] = f"{system_content}\n\n{history[0]['parts'][0]}"
            
            # Use synchronous generate_content since it's not async
            response = self.model.generate_content(
                history,
                generation_config={
                    "temperature": self.temperature,
                    "max_output_tokens": self.max_tokens,
                }
            )
            yield response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            yield f"Error: {str(e)}"

def get_provider(name: str, config: Dict[str, Any]) -> AIProvider:
    """Factory function to get the appropriate provider."""
    providers = {
        "openai": lambda: OpenAIProvider(
            config["api"]["openai_api_key"],
            config["model"]["name"],
            config["model"]["temperature"],
            config["model"]["max_tokens"]
        ),
        "claude": lambda: AnthropicProvider(
            config["api"]["anthropic_api_key"],
            config["model"]["name"],
            config["model"]["temperature"],
            config["model"]["max_tokens"]
        ),
        "gemini": lambda: GeminiProvider(
            config["api"]["gemini_api_key"],
            config["model"]["name"],
            config["model"]["temperature"],
            config["model"]["max_tokens"]
        )
    }
    
    if name not in providers:
        raise ValueError(f"Unknown provider: {name}")
    
    return providers[name]() 