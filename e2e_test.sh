#!/bin/bash

set -e

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Ollama is installed
if ! command_exists ollama; then
    echo "❌ Ollama is not installed. Please install it first:"
    echo "   Visit https://ollama.ai/download for installation instructions"
    exit 1
fi

# Check if Ollama service is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama service is not running. Starting Ollama..."
    # Try to start Ollama in the background
    ollama serve &
    OLLAMA_PID=$!
    
    # Wait for Ollama to start (up to 10 seconds)
    for i in {1..10}; do
        if curl -s http://localhost:11434/api/tags > /dev/null; then
            echo "✅ Ollama service started successfully"
            break
        fi
        if [ $i -eq 10 ]; then
            echo "❌ Failed to start Ollama service. Please start it manually:"
            echo "   ollama serve"
            exit 1
        fi
        sleep 1
    done
fi

# Check if the required model is available
if ! curl -s http://localhost:11434/api/tags | grep -q "llama2"; then
    echo "❌ Llama2 model not found. Pulling it now..."
    ollama pull llama2
    if [ $? -ne 0 ]; then
        echo "❌ Failed to pull Llama2 model. Please try manually:"
        echo "   ollama pull llama2"
        exit 1
    fi
fi

# Set environment variables
export SREX_LLM_PROVIDER=ollama
export SREX_LLM_MODEL=llama2
export SREX_LLM_TEMPERATURE=0.7
export SREX_METRICS_PROVIDER=prometheus
export SREX_METRICS_URL=http://localhost:9090
export SREX_LOG_LEVEL=INFO

# Create output directory if it doesn't exist
mkdir -p output

# 1. Generate SLOs, Alerts, Analysis, Runbooks using LLM
echo "Generating SLOs with LLM..."
python main.py generate --input examples/slo_generation_input.json --template templates/slo_generation.j2 --output output/slo_generation_output.json

echo "Generating Alerts with LLM..."
python main.py generate --input examples/alert_generation_input.json --template templates/alert_generation.j2 --output output/alert_generation_output.json

echo "Generating Analysis with LLM..."
python main.py generate --input examples/analysis_input.json --template templates/analysis.j2 --output output/analysis_output.json

echo "Generating Runbook with LLM..."
python main.py generate --input examples/runbook_input.json --template templates/runbook.j2 --output output/runbook_output.json

# 2. Show LLM output
echo "=== SLO Generation Output ==="
cat output/slo_generation_output.json

echo "=== Alert Generation Output ==="
cat output/alert_generation_output.json

echo "=== Analysis Output ==="
cat output/analysis_output.json

echo "=== Runbook Output ==="
cat output/runbook_output.json

# 3. Run scorecard and drift tools
echo "=== SRE Scorecard ==="
python -m cli.scorecard --snapshot output/slo_generation_output.json

# For drift, you need two snapshots. This is just an example:
# echo "=== SLO Drift ==="
# python -m cli.drift compare output/slo_generation_output.json output/slo_generation_output.json

echo "End-to-end test complete."

# Cleanup: Kill Ollama if we started it
if [ ! -z "$OLLAMA_PID" ]; then
    kill $OLLAMA_PID 2>/dev/null || true
fi 