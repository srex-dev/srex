# SREX - Service Reliability Experience Tool

SREX is a powerful tool for generating and managing Service Level Indicators (SLIs), Service Level Objectives (SLOs), and alerts based on your service metrics.

## Features

- Generate SLIs, SLOs, and alerts using LLM-powered analysis
- Support for multiple metrics providers (Prometheus, Datadog)
- Support for multiple LLM providers (OpenAI, Ollama)
- Comprehensive configuration management
- CLI interface for easy interaction
- Schema validation for inputs and outputs
- Detailed logging system

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/srex.git
cd srex
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

SREX can be configured using environment variables or a YAML configuration file. The configuration file should be placed at `~/.srex/config.yaml`.

Example configuration:
```yaml
llm:
  provider: openai
  model: gpt-4
  api_key: your-api-key
  temperature: 0.7

metrics:
  provider: prometheus
  url: http://localhost:9090
  timeout: 30

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: logs/srex.log
```

## Usage

### CLI Commands

1. Generate SLIs, SLOs, and alerts:
```bash
srex generate -i input.json -o output.json --provider openai --model gpt-4
```

2. Validate metrics provider connection:
```bash
srex validate-metrics -m prometheus -c config.yaml
```

3. List available components:
```bash
srex list-components -m prometheus -c config.yaml
```

### Input Format

The input JSON file should follow this structure:
```json
{
  "service": "api",
  "service_name": "API Service",
  "sli_inputs": [
    {
      "component": "api",
      "sli_type": "availability",
      "value": 99.9,
      "unit": "percent",
      "query": "sum(rate(http_requests_total{status=~\"2..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100",
      "source": "prometheus",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  ],
  "temperature": 0.7
}
```

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest
```

3. Run linting:
```bash
flake8
black .
isort .
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.