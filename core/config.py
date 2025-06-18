from pathlib import Path
from typing import Dict, Optional, List
from pydantic import BaseModel, Field
import yaml
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMConfig(BaseModel):
    """LLM provider configuration."""
    provider: str = Field(..., description="LLM provider name")
    model: str = Field(..., description="Model name")
    api_key: Optional[str] = Field(None, description="API key for the provider")
    temperature: float = Field(0.7, description="Temperature for generation")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")

class MetricsConfig(BaseModel):
    """Metrics provider configuration."""
    provider: str = Field(..., description="Metrics provider name")
    url: Optional[str] = Field(None, description="Provider URL")
    api_key: Optional[str] = Field(None, description="API key")
    app_key: Optional[str] = Field(None, description="Application key")
    timeout: int = Field(1800, description="Request timeout in seconds (default: 30 minutes)")

class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = Field("INFO", description="Logging level")
    format: str = Field("%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="Log format")
    file: Optional[str] = Field(None, description="Log file path")

class Config(BaseModel):
    """Main configuration."""
    llm: LLMConfig
    metrics: MetricsConfig
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    templates_dir: str = Field("templates", description="Directory containing templates")
    output_dir: str = Field("output", description="Directory for output files")

    def get(self, key: str, default=None):
        """Get configuration value with optional default."""
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    class Config:
        """Pydantic model configuration."""
        arbitrary_types_allowed = True

class ConfigManager:
    """Configuration manager."""
    _instance = None
    _config: Optional[Config] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_config(self, config_path: str = None) -> Config:
        """Load configuration from file or environment."""
        if self._config is not None:
            return self._config

        # Try to load from file
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                config_data = yaml.safe_load(f)
        else:
            # Load from environment variables
            config_data = {
                "llm": {
                    "provider": os.getenv("SREX_LLM_PROVIDER", "openai"),
                    "model": os.getenv("SREX_LLM_MODEL", "gpt-4"),
                    "api_key": os.getenv("SREX_LLM_API_KEY"),
                    "temperature": float(os.getenv("SREX_LLM_TEMPERATURE", "0.7")),
                },
                "metrics": {
                    "provider": os.getenv("SREX_METRICS_PROVIDER", "prometheus"),
                    "url": os.getenv("SREX_METRICS_URL", "http://localhost:9090"),  # Set default URL
                    "api_key": os.getenv("SREX_METRICS_API_KEY"),
                    "app_key": os.getenv("SREX_METRICS_APP_KEY"),
                    "timeout": int(os.getenv("SREX_METRICS_TIMEOUT", "1800")),
                },
                "logging": {
                    "level": os.getenv("SREX_LOG_LEVEL", "INFO"),
                    "format": os.getenv("SREX_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
                    "file": os.getenv("SREX_LOG_FILE"),
                },
                "templates_dir": os.getenv("SREX_TEMPLATES_DIR", "templates"),
                "output_dir": os.getenv("SREX_OUTPUT_DIR", "output"),
            }

        self._config = Config(**config_data)
        return self._config

    def get_config(self) -> Config:
        """Get current configuration."""
        if self._config is None:
            return self.load_config()
        return self._config

    def save_config(self, config_path: str) -> None:
        """Save current configuration to file."""
        if self._config is None:
            raise ValueError("No configuration loaded")
        
        config_data = self._config.dict()
        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)

# Global configuration manager instance
config_manager = ConfigManager()

# Export the configuration instance
CONFIG = config_manager.get_config()

settings = CONFIG