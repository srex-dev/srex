import os
import pytest
from pathlib import Path
from backend.core.config import ConfigManager, Config, LLMConfig, MetricsConfig, LoggingConfig

@pytest.fixture
def config_manager():
    """Create a fresh config manager instance."""
    manager = ConfigManager()
    manager._config = None
    return manager

@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file."""
    config_path = tmp_path / "config.yaml"
    config_data = """
    llm:
      provider: openai
      model: gpt-4
      api_key: test-key
      temperature: 0.7
    metrics:
      provider: prometheus
      url: http://localhost:9090
      timeout: 1800
    logging:
      level: INFO
      format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    """
    config_path.write_text(config_data)
    return str(config_path)

def test_config_loading_from_file(config_manager, temp_config_file):
    """Test loading configuration from file."""
    config = config_manager.load_config(temp_config_file)
    
    assert isinstance(config, Config)
    assert config.llm.provider == "openai"
    assert config.llm.model == "gpt-4"
    assert config.llm.api_key == "test-key"
    assert config.metrics.provider == "prometheus"
    assert config.metrics.url == "http://localhost:9090"

def test_config_loading_from_env(config_manager):
    """Test loading configuration from environment variables."""
    os.environ["SREX_LLM_PROVIDER"] = "ollama"
    os.environ["SREX_LLM_MODEL"] = "llama2"
    os.environ["SREX_METRICS_PROVIDER"] = "datadog"
    
    config = config_manager.load_config()
    
    assert config.llm.provider == "ollama"
    assert config.llm.model == "llama2"
    assert config.metrics.provider == "datadog"
    
    # Clean up
    del os.environ["SREX_LLM_PROVIDER"]
    del os.environ["SREX_LLM_MODEL"]
    del os.environ["SREX_METRICS_PROVIDER"]

def test_config_saving(config_manager, tmp_path):
    """Test saving configuration to file."""
    # Create initial config
    config = Config(
        llm=LLMConfig(provider="openai", model="gpt-4"),
        metrics=MetricsConfig(provider="prometheus", url="http://localhost:9090"),
        logging=LoggingConfig()
    )
    config_manager._config = config
    
    # Save to file
    save_path = tmp_path / "saved_config.yaml"
    config_manager.save_config(str(save_path))
    
    # Load from saved file
    loaded_config = config_manager.load_config(str(save_path))
    
    assert loaded_config.llm.provider == config.llm.provider
    assert loaded_config.llm.model == config.llm.model
    assert loaded_config.metrics.provider == config.metrics.provider
    assert loaded_config.metrics.url == config.metrics.url

def test_config_validation():
    """Test configuration validation."""
    # Valid config
    valid_config = Config(
        llm=LLMConfig(provider="openai", model="gpt-4"),
        metrics=MetricsConfig(provider="prometheus", url="http://localhost:9090"),
        logging=LoggingConfig()
    )
    assert isinstance(valid_config, Config)
    
    # Invalid config - missing required fields
    with pytest.raises(ValueError):
        Config(
            llm=LLMConfig(provider="openai"),  # Missing model
            metrics=MetricsConfig(provider="prometheus"),  # Missing url
            logging=LoggingConfig()
        )

def test_config_singleton():
    """Test that ConfigManager is a singleton."""
    manager1 = ConfigManager()
    manager2 = ConfigManager()
    assert manager1 is manager2 