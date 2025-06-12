
import os
import json
import random
import time
import importlib
import subprocess
import sys
from pathlib import Path

# Attempt safe imports with fallbacks
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.key_binding import KeyBindings
except ImportError:
    print("Missing dependency: prompt_toolkit. Please run 'jarvis setup' first.")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("Missing dependency: python-dotenv. Please run 'jarvis setup' first.")
    sys.exit(1)

try:
    from rich.console import Console
except ImportError:
    print("Missing dependency: rich. Please run 'jarvis setup' first.")
    sys.exit(1)

# === GLOBALS ===
console = Console()
load_dotenv()
CONFIG_PATH = Path.home() / ".jarvis" / "config.json"
REQUIRED_PACKAGES = ["openai", "anthropic", "google-generativeai", "prompt_toolkit", "python-dotenv", "rich", "wcwidth"]

# === UTILITIES ===
def install_packages():
    for package in REQUIRED_PACKAGES:
        subprocess.call([sys.executable, "-m", "pip", "install", package])

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)

# === SETUP ===
def setup():
    console.print("[bold green]Installing dependencies...[/bold green]")
    install_packages()

    console.print("[bold yellow]Let's configure your API keys:[/bold yellow]")
    config = {}
    config['openai_api_key'] = console.input("OpenAI API Key: ")
    config['anthropic_api_key'] = console.input("Anthropic (Claude) API Key: ")
    config['gemini_api_key'] = console.input("Google Gemini API Key: ")

    save_config(config)
    console.print("\n[bold green]✅ Configuration saved successfully![/bold green]")

# === CHAT SESSION ===
def slow_print(text, delay=0.03):
    for c in text:
        print(c, end='', flush=True)
        time.sleep(delay)
    print("\n")

def chat():
    try:
        import openai
        import anthropic
        import google.generativeai as genai
    except ImportError as e:
        console.print(f"[bold red]Missing module: {e.name}. Run 'jarvis setup' first.[/bold red]")
        sys.exit(1)

    config = load_config()

    openai.api_key = config.get("openai_api_key")
    anthropic_client = anthropic.Anthropic(api_key=config.get("anthropic_api_key"))
    genai.configure(api_key=config.get("gemini_api_key"))

    providers = []
    if config.get("openai_api_key"): providers.append("openai")
    if config.get("anthropic_api_key"): providers.append("claude")
    if config.get("gemini_api_key"): providers.append("gemini")

    if not providers:
        console.print("[bold red]No providers found. Run 'jarvis setup' first.[/bold red]")
        exit(1)

    chosen = random.choice(providers)
    console.print("==============================")
    console.print(f"[bold red]🟥 HAL (Jarvis) online. Provider: {chosen.upper()}[/bold red]")
    console.print("==============================")

    system_prompt = {
        "role": "system",
        "content": "You are Jarvis, a brilliant, witty, and highly capable AI assistant. You are always helpful, slightly humorous, and very smart."
    }

    messages = [system_prompt]
    session = PromptSession()
    kb = KeyBindings()

    @kb.add("c-l")
    def clear(event):
        console.clear()

    while True:
        try:
            user_input = session.prompt("[cyan]You:[/cyan] ", key_bindings=kb)
            messages.append({"role": "user", "content": user_input})
            print("[bold red]Jarvis:[/bold red]", end=" ", flush=True)

            if chosen == "openai":
                response = openai.ChatCompletion.create(
                    model="gpt-4o",
                    messages=messages,
                    stream=True
                )
                reply = ""
                for chunk in response:
                    delta = chunk.choices[0].delta.get("content", "")
                    print(delta, end="", flush=True)
                    reply += delta
                print("\n")
            elif chosen == "claude":
                full_prompt = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages]) + "\nAssistant:"
                resp = anthropic_client.completions.create(
                    model="claude-3-opus-20240229",
                    prompt=full_prompt,
                    max_tokens_to_sample=1024
                )
                slow_print(resp.completion)
                reply = resp.completion
            elif chosen == "gemini":
                model = genai.GenerativeModel('gemini-2.5-flash-preview-05-20')
                history = [{"role": m["role"], "parts": [m["content"]]} for m in messages]
                resp = model.generate_content(history)
                slow_print(resp.text)
                reply = resp.text
            else:
                console.print("Unknown provider.")
                break
            
            messages.append({"role": "assistant", "content": reply})

        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold yellow]Jarvis shutting down. Have a great day![/bold yellow]")
            break

# === ENTRY POINT ===
def main():
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup()
    else:
        chat()
