import click
import json
from pathlib import Path
from core.prompt_engine import generate_prompt_response, generate_definitions
from core.schema import validate_input, validate_output
from src.metrics.factory import MetricsAdapterFactory
from llm.providers import LLMProviderFactory
from backend.core.config import config_manager
from core.logger import setup_logger

logger = setup_logger(__name__)

@click.group()
def cli():
    """SREX - Service Reliability Experience Tool"""
    pass

@cli.command()
@click.option('--input', '-i', type=click.Path(exists=True), required=True, help='Input JSON file')
@click.option('--output', '-o', type=click.Path(), help='Output JSON file')
@click.option('--provider', '-p', type=click.Choice(['openai', 'ollama']), default='openai', help='LLM provider')
@click.option('--model', '-m', type=str, help='Model name')
@click.option('--temperature', '-t', type=float, default=0.7, help='Temperature for generation')
def generate(input, output, provider, model, temperature):
    """Generate SLIs, SLOs, and alerts from input data."""
    try:
        # Load and validate input
        with open(input) as f:
            input_data = json.load(f)
        
        if not validate_input(input_data):
            click.echo("Invalid input data", err=True)
            return 1

        # Create LLM provider
        llm_factory = LLMProviderFactory()
        llm_provider = llm_factory.create_provider(provider, {"model": model})

        # Generate response
        response = generate_prompt_response(input_data, llm_provider, temperature)
        
        # Validate output
        if not validate_output(response):
            click.echo("Invalid output data", err=True)
            return 1

        # Save output
        if output:
            with open(output, 'w') as f:
                json.dump(response, f, indent=2)
        else:
            click.echo(json.dumps(response, indent=2))

        return 0
    except Exception as e:
        logger.error(f"Error in generate command: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        return 1

@cli.command()
@click.option('--metrics', '-m', type=click.Choice(['prometheus', 'datadog']), required=True, help='Metrics provider')
@click.option('--config', '-c', type=click.Path(exists=True), help='Provider configuration file')
def validate_metrics(metrics, config):
    """Validate metrics provider connection."""
    try:
        # Load config if provided
        config_data = {}
        if config:
            with open(config) as f:
                config_data = json.load(f)

        # Create and validate adapter
        factory = MetricsAdapterFactory()
        adapter = factory.create_adapter(metrics, config_data)
        
        if adapter.validate_connection():
            click.echo(f"Successfully connected to {metrics}")
            return 0
        else:
            click.echo(f"Failed to connect to {metrics}", err=True)
            return 1
    except Exception as e:
        logger.error(f"Error in validate_metrics command: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        return 1

@cli.command()
@click.option('--metrics', '-m', type=click.Choice(['prometheus', 'datadog']), required=True, help='Metrics provider')
@click.option('--config', '-c', type=click.Path(exists=True), help='Provider configuration file')
def list_components(metrics, config):
    """List available components from metrics provider."""
    try:
        # Load config if provided
        config_data = {}
        if config:
            with open(config) as f:
                config_data = json.load(f)

        # Create adapter and list components
        factory = MetricsAdapterFactory()
        adapter = factory.create_adapter(metrics, config_data)
        components = adapter.get_available_components()
        
        click.echo("Available components:")
        for component in components:
            click.echo(f"- {component}")
        
        return 0
    except Exception as e:
        logger.error(f"Error in list_components command: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        return 1

@cli.group()
def config():
    """Configuration management commands."""
    pass

@config.command()
@click.option('--file', '-f', type=click.Path(), help='Path to save configuration')
def show(file):
    """Show current configuration."""
    try:
        config = config_manager.get_config()
        config_data = config.dict()
        
        if file:
            with open(file, 'w') as f:
                json.dump(config_data, f, indent=2)
        else:
            click.echo(json.dumps(config_data, indent=2))
        
        return 0
    except Exception as e:
        logger.error(f"Error in config show command: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        return 1

@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set a configuration value."""
    try:
        config = config_manager.get_config()
        
        # Parse key path
        keys = key.split('.')
        current = config
        for k in keys[:-1]:
            current = getattr(current, k)
        
        # Set value
        setattr(current, keys[-1], value)
        
        click.echo(f"Set {key} = {value}")
        return 0
    except Exception as e:
        logger.error(f"Error in config set command: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        return 1

@cli.group()
def template():
    """Template management commands."""
    pass

@template.command()
@click.option('--list', '-l', is_flag=True, help='List available templates')
@click.option('--show', '-s', type=str, help='Show template content')
def manage(list, show):
    """Manage prompt templates."""
    try:
        config = config_manager.get_config()
        templates_dir = Path(config.templates_dir)
        
        if list:
            click.echo("Available templates:")
            for template_file in templates_dir.glob("*.j2"):
                click.echo(f"- {template_file.stem}")
            return 0
        
        if show:
            template_path = templates_dir / f"{show}.j2"
            if not template_path.exists():
                click.echo(f"Template {show} not found", err=True)
                return 1
            
            click.echo(template_path.read_text())
            return 0
        
        click.echo("Please specify --list or --show")
        return 1
    except Exception as e:
        logger.error(f"Error in template manage command: {str(e)}")
        click.echo(f"Error: {str(e)}", err=True)
        return 1

if __name__ == '__main__':
    cli() 