import logging
import pytest
from pathlib import Path
from core.logger import setup_logger, CustomFormatter

@pytest.fixture
def temp_log_file(tmp_path):
    """Create a temporary log file path."""
    return str(tmp_path / "test.log")

def test_logger_setup():
    """Test basic logger setup."""
    logger = setup_logger("test_logger")
    
    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger"
    assert logger.level == logging.INFO
    assert len(logger.handlers) > 0

def test_logger_file_output(temp_log_file):
    """Test logger file output."""
    logger = setup_logger("test_logger", log_file=temp_log_file)
    test_message = "Test log message"
    
    logger.info(test_message)
    
    log_content = Path(temp_log_file).read_text()
    assert test_message in log_content

def test_logger_levels():
    """Test different logging levels."""
    logger = setup_logger("test_logger", level="DEBUG")
    
    assert logger.level == logging.DEBUG
    
    logger = setup_logger("test_logger", level="WARNING")
    assert logger.level == logging.WARNING

def test_custom_formatter():
    """Test custom formatter with colors."""
    formatter = CustomFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    formatted = formatter.format(record)
    
    assert "Test message" in formatted
    assert formatter.grey in formatted
    assert formatter.reset in formatted

def test_logger_multiple_handlers(temp_log_file):
    """Test logger with multiple handlers."""
    logger = setup_logger("test_logger", log_file=temp_log_file)
    
    assert len(logger.handlers) == 2  # Console and file handlers
    
    # Test both handlers
    test_message = "Test message for both handlers"
    logger.info(test_message)
    
    # Check file output
    log_content = Path(temp_log_file).read_text()
    assert test_message in log_content

def test_logger_config_integration():
    """Test logger integration with config system."""
    from core.config import config_manager
    
    # Set up test config
    config = config_manager.get_config()
    config.logging.level = "DEBUG"
    config.logging.format = "%(message)s"
    
    logger = setup_logger("test_logger")
    
    assert logger.level == logging.DEBUG
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            assert handler.formatter._fmt == "%(message)s" 