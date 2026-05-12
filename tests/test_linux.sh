#!/bin/bash
# Integration Testing Script for Linux (Ubuntu 20.04+)
# Tests Gemma 4 Personal OS on Linux platform

set -e

echo "=================================================="
echo "GEMMA 4 PERSONAL OS - LINUX INTEGRATION TEST"
echo "=================================================="
echo "Platform: Linux (Ubuntu/RHEL/Fedora)"
echo "Date: $(date)"
echo ""

# Check for required tools
echo "[1/5] Checking system requirements..."

if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found. Install: sudo apt-get install -y python3 python3-venv python3-dev"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "✗ Git not found. Install: sudo apt-get install -y git"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION"
echo "✓ Git installed"

# Check Ollama
echo ""
echo "[2/5] Checking Ollama..."

if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "⚠ Ollama not running. Start with: ollama serve &"
    echo "  Or install: curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi

echo "✓ Ollama is running"

# Setup Python virtual environment
echo ""
echo "[3/5] Setting up Python environment..."

if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi

source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "[4/5] Installing dependencies..."
pip install -q -r requirements.txt 2>&1 | grep -E "(Successfully|already)" || true
echo "✓ Dependencies installed"

# Run integration tests
echo ""
echo "[5/5] Running integration tests..."
echo ""

python3 tests/integration_test.py

echo ""
echo "=================================================="
echo "✓ LINUX INTEGRATION TEST COMPLETE"
echo "=================================================="
echo ""
echo "Results saved to: tests/INTEGRATION_TEST_RESULTS.md"
echo "Next: Test on Windows or proceed with deployment"
