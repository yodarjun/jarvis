"""Configuration management for Jarvis HAL."""

from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, SecretStr
import json
from loguru import logger

class APIConfig(BaseModel):
    """API configuration model."""
    openai_api_key: Optional[SecretStr] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[SecretStr] = Field(default=None, description="Anthropic API key")
    gemini_api_key: Optional[SecretStr] = Field(default=None, description="Google Gemini API key")

class ModelConfig(BaseModel):
    """Model configuration."""
    name: str = Field(default="gpt-4", description="Model name to use")
    temperature: float = Field(default=0.7, description="Model temperature")
    max_tokens: int = Field(default=1024, description="Maximum tokens per response")

class Config(BaseModel):
    """Main configuration model."""
    api: APIConfig = Field(default_factory=APIConfig)
    model: ModelConfig = Field(default_factory=ModelConfig)
    default_provider: str = Field(default="openai", description="Default AI provider to use")

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file."""
        config_path = Path.home() / ".jarvis" / "config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                return cls(**data)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in config file: {e}")
                # Backup the corrupted file
                backup_path = config_path.with_suffix('.json.bak')
                try:
                    config_path.rename(backup_path)
                    logger.info(f"Backed up corrupted config to {backup_path}")
                except Exception as backup_error:
                    logger.error(f"Failed to backup corrupted config: {backup_error}")
                return cls()
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return cls()
        return cls()

    def model_dump_for_json(self) -> Dict[str, Any]:
        """Convert model to dict with SecretStr values properly handled."""
        data = self.model_dump()
        # Convert SecretStr objects to their string values
        api_data = data["api"]
        for key in ["openai_api_key", "anthropic_api_key", "gemini_api_key"]:
            if api_data[key] is not None:
                api_data[key] = api_data[key].get_secret_value()
            else:
                api_data[key] = None
        return data

    def save(self) -> None:
        """Save configuration to file."""
        config_path = Path.home() / ".jarvis" / "config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            # First write to a temporary file
            temp_path = config_path.with_suffix('.json.tmp')
            with open(temp_path, 'w') as f:
                json.dump(self.model_dump_for_json(), f, indent=2)
            # Then rename to the actual file
            temp_path.replace(config_path)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            if temp_path.exists():
                temp_path.unlink()

    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers based on configured API keys."""
        providers = []
        if self.api.openai_api_key:
            providers.append("openai")
        if self.api.anthropic_api_key:
            providers.append("claude")
        if self.api.gemini_api_key:
            providers.append("gemini")
        return providers 