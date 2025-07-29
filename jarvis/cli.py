"""Command-line interface for Jarvis HAL."""

import asyncio
import random
import time
from typing import List, Dict, Optional
import typer
from rich.console import Console
from rich.prompt import Prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from loguru import logger
from pydantic import SecretStr

from .config import Config
from .providers import get_provider, OpenAIProvider, AnthropicProvider, GeminiProvider

# Initialize Typer app
app = typer.Typer(help="Jarvis HAL - A multi-model AI assistant with personality")
console = Console()

# ASCII Art for JARVIS
JARVIS_ART = """
  ██████║ █████╗ ██████╗ ██╗   ██╗██╗███████╗
     ██║ ██╔══██╗██╔══██╗██║   ██║██║██╔════╝
     ██║ ███████║██████╔╝██║   ██║██║███████╗
     ██║ ██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║
 ██║ ██║ ██║  ██║██║  ██║ ╚████╔╝ ██║███████║
   ██║   ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝
"""

def setup_logging():
    """Configure logging."""
    logger.remove()
    logger.add(
        "jarvis.log",
        rotation="1 day",
        retention="7 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )

@app.command()
def setup():
    """Configure Jarvis HAL."""
    config = Config.load()
    
    console.print("[bold yellow]Let's configure your API keys:[/bold yellow]")
    config.api.openai_api_key = SecretStr(Prompt.ask("OpenAI API Key", default=config.api.openai_api_key.get_secret_value() if config.api.openai_api_key else ""))
    config.api.anthropic_api_key = SecretStr(Prompt.ask("Anthropic API Key", default=config.api.anthropic_api_key.get_secret_value() if config.api.anthropic_api_key else ""))
    config.api.gemini_api_key = SecretStr(Prompt.ask("Google Gemini API Key", default=config.api.gemini_api_key.get_secret_value() if config.api.gemini_api_key else ""))
    
    config.default_provider = Prompt.ask(
        "Default provider",
        choices=["openai", "claude", "gemini"],
        default=config.default_provider
    )
    
    config.model.name = Prompt.ask("Model name", default=config.model.name)
    config.model.temperature = float(Prompt.ask("Temperature", default=str(config.model.temperature)))
    config.model.max_tokens = int(Prompt.ask("Max tokens", default=str(config.model.max_tokens)))
    
    config.save()
    console.print("\n[bold green]✅ Configuration saved successfully![/bold green]")

def print_character_by_character(text: str, delay: float = 0.01):
    """Print text character by character with a specified delay."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)

def chat_loop(provider, messages: List[Dict[str, str]], session: PromptSession, kb: KeyBindings, config: Config):
    """Main chat loop."""
    while True:
        try:
            # Use Rich's console for colored output
            console.print("You:", style="cyan", end=" ")
            user_input = session.prompt("", key_bindings=kb)
            
            # Check for LLM shortcuts
            current_provider = provider
            original_input = user_input
            
            if user_input.startswith("g:"):
                user_input = user_input[2:].strip()
                if "gemini" in config.get_available_providers():
                    current_provider = get_provider("gemini", config.model_dump())
                else:
                    console.print("[bold yellow]⚠️  Gemini is unavailable currently. Using available provider.[/bold yellow]")
            elif user_input.startswith("o:"):
                user_input = user_input[2:].strip()
                if "openai" in config.get_available_providers():
                    current_provider = get_provider("openai", config.model_dump())
                else:
                    console.print("[bold yellow]⚠️  OpenAI is unavailable currently. Using available provider.[/bold yellow]")
            elif user_input.startswith("c:"):
                user_input = user_input[2:].strip()
                if "claude" in config.get_available_providers():
                    current_provider = get_provider("claude", config.model_dump())
                else:
                    console.print("[bold yellow]⚠️  Claude is unavailable currently. Using available provider.[/bold yellow]")
            
            # If no input after shortcut, skip this iteration
            if not user_input:
                continue
                
            messages.append({"role": "user", "content": user_input})
            
            # Show which provider is being used (if different from default)
            provider_name = "Jarvis"
            if current_provider != provider:
                if isinstance(current_provider, OpenAIProvider):
                    provider_name = "Jarvis (OpenAI)"
                elif isinstance(current_provider, AnthropicProvider):
                    provider_name = "Jarvis (Claude)"
                elif isinstance(current_provider, GeminiProvider):
                    provider_name = "Jarvis (Gemini)"
            
            console.print(f"{provider_name}:", style="bold red", end=" ")
            
            full_response = ""
            for chunk in current_provider.generate_response_sync(messages):
                print_character_by_character(chunk, delay=0.005)  # Fast character printing
                full_response += chunk
            print("\n")
            
            messages.append({"role": "assistant", "content": full_response})
            
        except KeyboardInterrupt:
            console.print("\n[bold yellow]Jarvis shutting down. Have a great day![/bold yellow]")
            break
        except Exception as e:
            logger.error(f"Error in chat loop: {e}")
            console.print(f"[bold red]Error: {str(e)}[/bold red]")

@app.command()
def chat(
    provider: Optional[str] = typer.Option(None, help="Specific provider to use (openai, claude, or gemini)")
):
    """Start an interactive chat session with Jarvis."""
    config = Config.load()
    available_providers = config.get_available_providers()
    
    if not available_providers:
        console.print("[bold red]No providers configured. Run 'jarvis setup' first.[/bold red]")
        raise typer.Exit(1)
    
    chosen = provider if provider in available_providers else random.choice(available_providers)

    # Print ASCII art
    console.print(JARVIS_ART, style="bold blue")
    console.print("==============================")
    console.print(f"[bold red]🟥 Jarvis online. Provider: {chosen.upper()}[/bold red]")
    console.print("==============================")
    
    # Show available shortcuts
    available_providers = config.get_available_providers()
    shortcuts_info = []
    if "openai" in available_providers:
        shortcuts_info.append("o: for OpenAI")
    if "claude" in available_providers:
        shortcuts_info.append("c: for Claude")
    if "gemini" in available_providers:
        shortcuts_info.append("g: for Gemini")
    
    if shortcuts_info:
        console.print("\n[bold cyan]Available shortcuts:[/bold cyan]")
        for shortcut in shortcuts_info:
            console.print(f"  • {shortcut}")
        console.print("")
    
    system_prompt = {
        "role": "system",
        "content": "You are Jarvis, a brilliant AI assistant with a witty personality. Keep responses short, precise, and to the point. Be helpful and slightly witty, but concise."
    }
    
    messages: List[Dict[str, str]] = [system_prompt]
    session = PromptSession()
    kb = KeyBindings()
    
    @kb.add("c-l")
    def clear(event):
        console.clear()
    
    provider = get_provider(chosen, config.model_dump())
    chat_loop(provider, messages, session, kb, config)

def main():
    """Main entry point."""
    setup_logging()
    app() 