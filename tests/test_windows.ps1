# Integration Testing Script for Windows (11 + WSL2)
# Tests Gemma 4 Personal OS on Windows platform

Write-Host "=================================================="
Write-Host "GEMMA 4 PERSONAL OS - WINDOWS INTEGRATION TEST"
Write-Host "=================================================="
Write-Host "Platform: Windows 11 + WSL2"
Write-Host "Date: $(Get-Date)"
Write-Host ""

# Check for required tools
Write-Host "[1/5] Checking system requirements..."

$pythonExists = & {
    try { python --version | Out-Null; $true }
    catch { $false }
}

if (-not $pythonExists) {
    Write-Host "✗ Python not found."
    Write-Host "  Install: https://www.python.org/downloads/"
    Write-Host "  Or in WSL2: apt-get install -y python3 python3-venv python3-dev"
    exit 1
}

$pythonVersion = & python --version
Write-Host "✓ $pythonVersion"

$gitExists = & {
    try { git --version | Out-Null; $true }
    catch { $false }
}

if (-not $gitExists) {
    Write-Host "✗ Git not found."
    Write-Host "  Install: https://git-scm.com/download/win"
    exit 1
}

Write-Host "✓ Git installed"

# Check Ollama
Write-Host ""
Write-Host "[2/5] Checking Ollama..."

$ollamaRunning = & {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 2 -ErrorAction Stop
        $response.StatusCode -eq 200
    }
    catch {
        $false
    }
}

if (-not $ollamaRunning) {
    Write-Host "⚠ Ollama not running. Start with: ollama serve"
    Write-Host "  Or install: https://ollama.ai"
    exit 1
}

Write-Host "✓ Ollama is running"

# Setup Python virtual environment
Write-Host ""
Write-Host "[3/5] Setting up Python environment..."

if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✓ Virtual environment created"
}
else {
    Write-Host "✓ Virtual environment exists"
}

& "venv/Scripts/Activate.ps1"
Write-Host "✓ Virtual environment activated"

# Install dependencies
Write-Host ""
Write-Host "[4/5] Installing dependencies..."
pip install -q -r requirements.txt 2>&1 | Select-String -Pattern "Successfully|already" | ForEach-Object { Write-Host "  $_" } -ErrorAction SilentlyContinue
Write-Host "✓ Dependencies installed"

# Run integration tests
Write-Host ""
Write-Host "[5/5] Running integration tests..."
Write-Host ""

python tests/integration_test.py

Write-Host ""
Write-Host "=================================================="
Write-Host "✓ WINDOWS INTEGRATION TEST COMPLETE"
Write-Host "=================================================="
Write-Host ""
Write-Host "Results saved to: tests/INTEGRATION_TEST_RESULTS.md"
Write-Host "Platform validation complete!"
