# Installation Guide — Windows 11 + WSL2

**Tested on:** Windows 11 + WSL2 (Ubuntu 22.04 LTS)  
**Installation time:** ~25 minutes  
**Difficulty:** Intermediate

---

## System Requirements

### Minimum
- **OS:** Windows 11 (Build 22000+) with WSL2 enabled
- **CPU:** Intel Core i7 / AMD Ryzen 7 (8 cores minimum)
- **RAM:** 24GB (allocated to WSL2)
- **Storage:** 100GB SSD free
- **GPU:** Optional (NVIDIA CUDA on desktop, USB GPU support for WSL2)

### Recommended
- **OS:** Windows 11 Pro/Enterprise with Hyper-V
- **CPU:** Intel Core i9 / AMD Ryzen 9
- **RAM:** 32GB+
- **Storage:** 250GB SSD
- **GPU:** NVIDIA RTX 3090 with WSL2 CUDA support

---

## Pre-Installation Checklist

```powershell
# Run in PowerShell (Admin)

# Check Windows version
Get-ComputerInfo | Select-Object -Property WindowsProductName, WindowsVersion

# Check RAM
Get-ComputerInfo | Select-Object -Property CsPhyicallyInstalledSystemMemory | 
  ForEach-Object { $_.CsPhyicallyInstalledSystemMemory / 1GB }

# Check WSL2 version
wsl --version

# Check available storage
Get-Volume | Select-Object DriveLetter, SizeRemaining | 
  ForEach-Object { [PSCustomObject]@{Drive = $_.DriveLetter; FreeGB = $_.SizeRemaining / 1GB} }
```

All checks should pass before proceeding.

---

## Step 1: Enable WSL2

Run PowerShell as Administrator:

```powershell
# Enable WSL2 feature
wsl --install

# Or manually:
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Restart computer
Restart-Computer

# Set WSL2 as default
wsl --set-default-version 2
```

---

## Step 2: Install Ubuntu 22.04 LTS

After WSL2 is enabled:

```powershell
# Install Ubuntu
wsl --install -d Ubuntu-22.04

# Launch Ubuntu
wsl --distribution Ubuntu-22.04
```

This opens a terminal. Complete Ubuntu setup (create username/password).

---

## Step 3: Update Ubuntu Inside WSL2

Inside WSL2 Ubuntu terminal:

```bash
# Update package lists
sudo apt update
sudo apt upgrade -y

# Install core dependencies
sudo apt install -y \
  curl \
  wget \
  git \
  python3.11 \
  python3.11-venv \
  python3.11-dev \
  build-essential \
  libssl-dev \
  libffi-dev \
  sqlite3 \
  graphviz \
  postgresql

# Verify Python
python3.11 --version
```

---

## Step 4: Configure WSL2 Memory (Windows Side)

Create or edit `%UserProfile%\.wslconfig`:

```ini
[wsl2]
memory=24GB
processors=8
swap=4GB
localhostForwarding=true
```

**Then restart WSL2:**

```powershell
wsl --shutdown
# Wait 10 seconds
wsl --distribution Ubuntu-22.04
```

---

## Step 5: Install Ollama (Windows Native)

Ollama has native Windows support. Install on Windows (not WSL2):

```powershell
# Download Ollama for Windows
# https://ollama.ai/download/windows

# Or use Chocolatey (if installed):
choco install ollama

# Start Ollama (runs as system service)
# Ollama will be available at http://localhost:11434
```

**Verify from WSL2:**

```bash
# Inside WSL2 Ubuntu
curl http://localhost:11434/api/tags
```

---

## Step 6: Download Gemma Models (Windows)

Inside WSL2 or Windows native terminal:

```bash
# Models download to Windows installation directory
ollama pull gemma2:26b       # ~15GB
ollama pull gemma2:2b        # ~2GB

# Verify
ollama list
```

**Time:** 10-15 minutes

---

## Step 7: Set Up Python Environment (WSL2)

Back inside WSL2 Ubuntu terminal:

```bash
# Create project directory
mkdir -p ~/gemma-personal-os
cd ~/gemma-personal-os

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install core dependencies
pip install \
  crewai==0.17.0 \
  anything-llm==1.0.0 \
  ollama==0.0.13 \
  pydantic==2.0.0 \
  python-dotenv==1.0.0 \
  requests==2.31.0 \
  beautifulsoup4==4.12.0 \
  sqlalchemy==2.0.0
```

---

## Step 8: Configure Environment

```bash
# Create .env file
cp config/.env.example .env

# Edit with nano
nano .env
```

**Essential variables:**

```bash
# Ollama (Windows native host)
OLLAMA_HOST=http://localhost:11434

# Models
CREW_AI_LLM=gemma2:26b
CREW_AI_LLM_FAST=gemma2:2b

# AnythingLLM
ANYTHINGLLM_HOST=http://localhost:3001

# Logging
AUDIT_LOG_PATH=/home/username/.gemma-os/audit.log
LOG_LEVEL=INFO
```

---

## Step 9: Install AnythingLLM (Windows)

### Option A: Docker for Windows

```powershell
# Install Docker Desktop for Windows
# https://www.docker.com/products/docker-desktop

# In PowerShell (Admin):
docker run -d `
  --name anythingllm `
  -p 3001:3001 `
  -v anythingllm_data:/data `
  mintplexlabs/anythingllm:latest

# Verify
docker logs anythingllm
```

### Option B: Native Windows Installation

```bash
# In WSL2 or Windows terminal with Node.js installed:
npm install -g anythingllm
anythingllm start
# Runs on http://localhost:3001
```

---

## Step 10: Initialize Project (WSL2)

```bash
# Inside WSL2
source venv/bin/activate

# Create directories
mkdir -p \
  ~/.gemma-os/results \
  ~/.gemma-os/cache \
  ~/.gemma-os/skills \
  ~/.gemma-os/logs

# Initialize database
python3 -c "from src.gemma_os import init_db; init_db()"

# Load skills
python3 -c "from src.gemma_os import load_skills; load_skills()"
```

---

## Step 11: Verification

```bash
# Test Ollama connectivity (from WSL2)
curl http://localhost:11434/api/tags

# Test model inference
python3 << 'EOF'
import ollama
response = ollama.generate(model="gemma2:2b", prompt="Hello!")
print(f"✓ Model working: {response['response'][:50]}")
EOF

# Test CrewAI
python3 << 'EOF'
from crewai import Agent, Task, Crew
print("✓ CrewAI ready")
EOF

# Test AnythingLLM
curl http://localhost:3001/api/system/health
```

---

## WSL2-Specific Tips

### File Sharing Between Windows and WSL2

```bash
# Access Windows files from WSL2
cd /mnt/c/Users/YourUsername/Documents

# Access WSL2 files from Windows
# Explorer: \\wsl$\Ubuntu-22.04\home\username
```

### Persistent Bash Aliases

Edit `~/.bashrc` in WSL2:

```bash
# Add aliases for easier access
alias win='cd /mnt/c/Users/YourUsername'
alias proj='cd ~/gemma-personal-os && source venv/bin/activate'
```

### GPU Support (Optional)

For NVIDIA GPU with WSL2:

```bash
# Inside WSL2
# Install CUDA toolkit
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt update
sudo apt install cuda-toolkit

# Verify
nvidia-smi  # Should show GPU
```

---

## Performance Tuning

### For 24GB RAM allocation:

```bash
# In .wslconfig
[wsl2]
memory=20GB     # Reserve 4GB for Windows
processors=6    # Leave 2 cores for system
swap=4GB
```

### Optimize disk usage:

```powershell
# Compact WSL2 vhdx file
wsl --shutdown
Optimize-VHD -Path "$env:LOCALAPPDATA\Packages\CanonicalGroupLimited.Ubuntu22.04LTS_79rhkp1fndgsc\LocalState\ext4.vhdx" -Mode Full
```

---

## Troubleshooting

### Issue: WSL2 not installed
```powershell
# Check WSL version
wsl --version

# If not installed, follow Step 1 again
# May require Windows Update
```

### Issue: Ollama not accessible from WSL2
```bash
# Test connectivity
curl http://localhost:11434/api/tags

# If fails, ensure Ollama is running on Windows:
# Check Windows: ollama serve (in Command Prompt)
```

### Issue: Out of memory in WSL2
```powershell
# Increase memory in .wslconfig
[wsl2]
memory=28GB    # Increase allocation
```

### Issue: AnythingLLM fails to start
```powershell
# Check Docker is running
docker ps

# If using native, ensure Node.js is installed:
node --version
npm --version
```

### Issue: Slow disk access
```bash
# Check if using /mnt/c (Windows partition)
# Better performance on WSL2 native filesystem (~)
# Move project:
mv /mnt/c/Users/username/project ~

# Use native location for better speed
```

---

## Monitoring

```bash
# WSL2 Resource Usage
wsl --list --verbose

# Check WSL2 memory inside WSL2
free -h

# Monitor from Windows PowerShell
wsl -- free -h
```

---

## Next Steps

1. **Test workflows** — Run examples from [WORKFLOWS.md](WORKFLOWS.md)
2. **Load SKILLs** — Copy to `~/.gemma-os/skills/`
3. **Configure AnythingLLM** — Add documents for RAG

---

## Windows-Specific Resources

- [WSL2 Documentation](https://learn.microsoft.com/en-us/windows/wsl/)
- [Ollama Windows Guide](https://github.com/ollama/ollama)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)

---

**Installation complete!** Proceed to [WORKFLOWS.md](WORKFLOWS.md) for example use cases.

Last updated: May 2026
