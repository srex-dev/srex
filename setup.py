from setuptools import setup, find_packages

setup(
    name="srex",
    version="0.1.0",
    packages=find_packages(include=["srex", "srex.*", "src", "src.*", "llm", "llm.*", "core", "core.*"]),
    install_requires=[
        "pydantic>=2.0.0",
        "pyyaml>=6.0.0",
        "click>=8.0.0",
        "python-dotenv>=1.0.0",
        "openai>=1.0.0",
        "ollama>=0.1.0",
        "prometheus-api-client>=0.5.0",
        "datadog-api-client>=2.0.0",
        "newrelic>=8.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "pytest-asyncio>=0.23.5",
            "pytest-xdist>=3.5.0",
            "pytest-timeout>=2.2.0",
            "pytest-env>=1.1.3",
            "pytest-sugar>=1.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
            "flake8>=6.0.0",
        ]
    },
    python_requires=">=3.9",
) 