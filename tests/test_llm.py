import pytest
from unittest.mock import Mock, patch
from llm.providers.factory import LLMProviderFactory
from llm.providers.ollama import OllamaProvider
from llm.providers.openai import OpenAIProvider

@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client."""
    with patch('requests.post') as mock_post, patch('requests.get') as mock_get:
        # Mock POST /api/generate
        mock_post_response = Mock()
        mock_post_response.raise_for_status.return_value = None
        mock_post_response.json.return_value = {
            'response': 'Test response',
            'model': 'llama2',
            'created_at': '2024-01-01T00:00:00Z'
        }
        mock_post.return_value = mock_post_response

        # Mock GET /api/tags
        mock_get_response = Mock()
        mock_get_response.raise_for_status.return_value = None
        mock_get_response.json.return_value = {
            'models': [
                {'name': 'llama2'},
                {'name': 'mistral'}
            ]
        }
        mock_get.return_value = mock_get_response

        yield mock_post, mock_get

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    with patch('llm.providers.openai.OpenAI') as mock:
        mock_instance = Mock()
        # Mock the chat completions response (non-streaming)
        mock_chat_completion = Mock()
        mock_chat_completion.choices = [
            Mock(
                message=Mock(
                    content='Test response',
                    role='assistant'
                )
            )
        ]
        # For non-streaming
        mock_instance.chat.completions.create.return_value = mock_chat_completion
        
        # For streaming, return an iterable of chunks
        def create_side_effect(*args, **kwargs):
            if kwargs.get('stream'):
                chunk = Mock()
                chunk.choices = [Mock(delta=Mock(content='Test response'))]
                return iter([chunk])
            return mock_chat_completion
        mock_instance.chat.completions.create.side_effect = create_side_effect
        
        # Mock the models list response
        mock_models = Mock()
        mock_models.data = [
            Mock(id='gpt-4'),
            Mock(id='gpt-3.5-turbo')
        ]
        mock_instance.models.list.return_value = mock_models
        
        mock.return_value = mock_instance
        yield mock_instance

def test_ollama_provider(mock_ollama_client):
    """Test Ollama provider."""
    provider = OllamaProvider(model="llama2")
    
    # Test completion
    response = provider.complete("Test prompt", temperature=0.7)
    assert response is not None
    assert response.text == "Test response"
    assert response.model == "llama2"
    
    # Test streaming
    stream = provider.complete_stream("Test prompt", temperature=0.7)
    assert stream is not None
    for chunk in stream:
        assert chunk.text == "Test response"
        assert chunk.model == "llama2"

def test_openai_provider(mock_openai_client):
    """Test OpenAI provider."""
    provider = OpenAIProvider(api_key="test", model="gpt-4")
    
    # Test completion
    response = provider.complete("Test prompt", temperature=0.7)
    assert response is not None
    assert response.text == "Test response"
    assert response.model == "gpt-4"
    
    # Test streaming
    stream = provider.complete_stream("Test prompt", temperature=0.7)
    assert stream is not None
    for chunk in stream:
        assert chunk.text == "Test response"
        assert chunk.model == "gpt-4"
    
    # Test get_available_models
    models = provider.get_available_models()
    assert len(models) == 2
    assert "gpt-4" in models
    assert "gpt-3.5-turbo" in models

def test_llm_provider_factory():
    """Test LLM provider factory."""
    factory = LLMProviderFactory()
    
    # Test provider registration
    assert "ollama" in factory.get_available_providers()
    assert "openai" in factory.get_available_providers()
    
    # Test provider creation
    ollama_provider = factory.create_provider("ollama", {"model": "llama2"})
    assert isinstance(ollama_provider, OllamaProvider)
    
    openai_provider = factory.create_provider("openai", {"api_key": "test", "model": "gpt-4"})
    assert isinstance(openai_provider, OpenAIProvider)
    
    # Test invalid provider type
    with pytest.raises(ValueError):
        factory.create_provider("invalid", {}) 