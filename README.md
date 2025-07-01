# Jarvis

A multi-model AI assistant with personality, supporting OpenAI, Anthropic Claude, and Google Gemini models.

## Features

- 🤖 Multiple AI providers support (OpenAI, Anthropic Claude, Google Gemini)
- 🎨 Rich terminal interface with syntax highlighting
- ⚡ Async streaming responses
- 🔧 Easy configuration management
- 📝 Comprehensive logging
- 🎯 Type-safe with Pydantic models

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/jarvis.git
cd jarvis

# Install the package
pip install -e .
```

## Configuration

Before using Jarvis, you need to configure your API keys:

```bash
jarvis setup
```

This will guide you through setting up:
- OpenAI API key
- Anthropic API key
- Google Gemini API key
- Default provider
- Model settings
- Temperature and token limits

## Usage

Start a chat session:

```bash
jarvis chat
```

### Keyboard Shortcuts

- `Ctrl+L`: Clear the screen
- `Ctrl+C`: Exit the chat session

## Development

### Project Structure

```
jarvis/
├── jarvis/
│   ├── __init__.py
│   ├── cli.py          # Command-line interface
│   ├── config.py       # Configuration management
│   └── providers.py    # AI provider implementations
├── setup.py
└── README.md
```

### Requirements

- Python 3.8+
- OpenAI API key
- Anthropic API key (optional)
- Google Gemini API key (optional)

## License

MIT License - see LICENSE file for details
