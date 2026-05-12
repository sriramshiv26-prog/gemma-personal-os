# Installation Guide — Linux

**Tested on:** Ubuntu 22.04 LTS, RHEL 9, Fedora 40  
**Installation time:** ~20 minutes  
**Difficulty:** Intermediate

---

## System Requirements

### Minimum
- **CPU:** Intel i7/Xeon, AMD Ryzen 7 (8 cores minimum)
- **RAM:** 24GB
- **Storage:** 100GB SSD free
- **GPU:** Optional (NVIDIA CUDA recommended for 26B model)
- **OS:** Ubuntu 22.04 LTS, RHEL 9, Fedora 40

### Recommended
- **CPU:** Intel i9/Xeon, AMD Ryzen 9
- **RAM:** 32GB+ (allows concurrent model loading)
- **Storage:** 250GB SSD
- **GPU:** NVIDIA RTX 3090 / A100 (for fast inference)
- **Network:** Gigabit ethernet

---

## Pre-Installation Checklist

```bash
# Check OS version
cat /etc/os-release | grep "VERSION="

# Check available RAM (in GB)
free -h | grep Mem | awk '{print $7}'

# Check free disk space
df -h / | tail -1 | awk '{print $4}'

# Check CPU cores
nproc

# Check NVIDIA GPU (if available)
nvidia-smi  # CUDA availability check
```

---

## Step 1: Update System Packages

### Ubuntu/Debian:
```bash
sudo apt update
sudo apt upgrade -y
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
```

### RHEL/Fedora:
```bash
sudo dnf check-update
sudo dnf upgrade -y
sudo dnf install -y \
  curl \
  wget \
  git \
  python3.11 \
  python3.11-devel \
  gcc \
  make \
  openssl-devel \
  libffi-devel \
  sqlite \
  graphviz \
  postgresql-server
```

---

## Step 2: Install NVIDIA CUDA (Optional - For GPU acceleration)

### For NVIDIA RTX 3090 / A100:

```bash
# Download NVIDIA CUDA toolkit
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb

# Ubuntu:
sudo apt-get update
sudo apt-get install -y cuda-toolkit

# RHEL:
sudo dnf install -y cuda-toolkit

# Verify installation
nvcc --version  # Should output CUDA version 12.x
```

### Set CUDA environment variables:

```bash
# Add to ~/.bashrc or ~/.zshrc
export CUDA_HOME=/usr/local/cuda
export PATH=$CUDA_HOME/bin:$PATH
export LD_LIBRARY_PATH=$CUDA_HOME/lib64:$LD_LIBRARY_PATH

# Source the file
source ~/.bashrc
```

---

## Step 3: Install Ollama

```bash
# Download and install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installation
ollama --version
# Should output: ollama version x.x.x

# Start Ollama daemon
ollama serve &
```

---

## Step 4: Download Gemma Models

```bash
# Pull models (requires Ollama running)
ollama pull gemma2:26b       # Expert reasoning (~15GB)
ollama pull gemma2:2b        # Fast response (~2GB)

# Verify models
ollama list
# Output:
# NAME              ID              SIZE    MODIFIED
# gemma2:26b        a5f9edb3e2f6    15 GB   2 minutes ago
# gemma2:2b         59bf8a49b7be    2.0 GB  1 minute ago
```

**Time:** 10-15 minutes (depends on internet speed)

---

## Step 5: Configure Ollama (for GPU)

If using NVIDIA GPU, create `~/.ollama/config.yaml`:

```yaml
# GPU-optimized configuration
num_parallel: 4                  # Parallel inference tasks
num_gpu: -1                      # Use GPU (-1 = all available)
mmap: true                       # Memory-mapped loading
num_thread: 16                   # CPU threads (adjust for your CPU)
embedding_batch_size: 64

# GPU memory management
gpu_memory_limit: 24gb           # Reserve 24GB for models
gpu_memory_fraction: 0.90        # Use 90% of VRAM
cuda_compute_cap: 86             # RTX 3090 = 86, A100 = 80
```

---

## Step 6: Set Up Python Virtual Environment

```bash
# Navigate to project directory
mkdir -p ~/gemma-personal-os
cd ~/gemma-personal-os

# Create virtual environment with Python 3.11
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
  python-dotenv==1.0.0

# Install optional dependencies
pip install \
  requests==2.31.0 \
  beautifulsoup4==4.12.0 \
  lxml==4.9.0 \
  redis==5.0.0 \
  sqlalchemy==2.0.0 \
  psycopg2-binary==2.9.0  # PostgreSQL support

# For CUDA support (if using GPU)
pip install \
  torch==2.1.0+cu121 \
  torchvision==0.16.0+cu121 \
  torchaudio==2.1.0+cu121 -f https://download.pytorch.org/whl/torch_stable.html
```

---

## Step 7: Configure Environment Variables

```bash
# Create .env file
cp config/.env.example .env

# Edit configuration
nano .env
```

**Essential variables for Linux:**

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_NUM_PARALLEL=4
OLLAMA_GPU=1                    # Enable GPU (1 = on)

# Model Selection
CREW_AI_LLM=gemma2:26b
CREW_AI_LLM_FAST=gemma2:2b

# AnythingLLM
ANYTHINGLLM_HOST=http://localhost:3001
ANYTHINGLLM_API_KEY=default

# Serper.dev (optional)
SERPER_API_KEY=your_key_here

# Logging
AUDIT_LOG_PATH=/var/log/gemma-os/audit.log
LOG_LEVEL=INFO

# PostgreSQL (optional, for distributed setup)
DATABASE_URL=postgresql://user:pass@localhost:5432/gemma_os
```

---

## Step 8: Install AnythingLLM (Private RAG)

### Option A: Docker (Recommended)

```bash
# Ensure Docker is installed
sudo apt install docker.io docker-compose

# Create data directory
mkdir -p ~/anythingllm

# Run AnythingLLM container
docker run -d \
  --name anythingllm \
  -p 3001:3001 \
  -v ~/anythingllm:/data \
  -e EMBEDDED_DB=true \
  mintplexlabs/anythingllm:latest

# Verify
docker logs anythingllm
```

### Option B: Direct Installation

```bash
# Install Node.js (if not present)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install AnythingLLM
npm install -g anythingllm

# Start service
anythingllm start
```

---

## Step 9: Initialize Project

```bash
# Activate venv
source venv/bin/activate

# Create required directories
mkdir -p \
  ~/.gemma-os/results \
  ~/.gemma-os/cache \
  ~/.gemma-os/skills \
  ~/.gemma-os/logs

# Set permissions
chmod 755 ~/.gemma-os/*
sudo mkdir -p /var/log/gemma-os
sudo chown $USER:$USER /var/log/gemma-os
sudo chmod 755 /var/log/gemma-os

# Initialize database
python3 -c "from src.gemma_os import init_db; init_db()"

# Load default SKILLs
python3 -c "from src.gemma_os import load_skills; load_skills()"
```

---

## Step 10: Set Up Systemd Service (Auto-Start)

```bash
# Create Ollama systemd service
sudo cat > /etc/systemd/system/ollama.service << 'EOF'
[Unit]
Description=Ollama Service
After=network-online.target

[Service]
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable ollama.service
sudo systemctl start ollama.service

# Verify
sudo systemctl status ollama.service
```

---

## Step 11: Verification

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Test models
python3 << 'EOF'
import ollama
response = ollama.generate(model="gemma2:2b", prompt="Hello")
print(f"✓ Ollama 2B: {response['response'][:50]}")
EOF

# Test CrewAI
python3 << 'EOF'
from crewai import Agent, Task, Crew
print("✓ CrewAI imported successfully")
EOF

# Test AnythingLLM
curl http://localhost:3001/api/system/health
```

---

## Performance Tuning

### For CPU-only (no GPU):

```bash
# .env tuning
OLLAMA_NUM_PARALLEL=1
CREW_AI_LLM_FAST=gemma2:2b    # Prefer fast model
```

### For NVIDIA GPU (RTX 3090):

```bash
# .env tuning
OLLAMA_NUM_PARALLEL=4
OLLAMA_GPU=1
OLLAMA_GPU_MEMORY=24gb
```

### For NVIDIA GPU (A100):

```bash
# .env tuning
OLLAMA_NUM_PARALLEL=8
OLLAMA_GPU=1
OLLAMA_GPU_MEMORY=40gb
```

---

## Monitoring

```bash
# Check GPU utilization (NVIDIA)
watch nvidia-smi

# Monitor Ollama service
journalctl -u ollama -f

# View audit logs
tail -f ~/.gemma-os/audit.log

# Check system resources
top
htop  # If installed: sudo apt install htop
```

---

## Troubleshooting

### Issue: "Ollama: command not found"
```bash
# Reinstall Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

### Issue: NVIDIA CUDA not detected
```bash
# Check CUDA installation
nvcc --version
nvidia-smi

# Reinstall CUDA drivers
sudo apt remove --purge nvidia-* cuda-*
sudo apt install -y nvidia-driver-550 cuda-toolkit
```

### Issue: Out of memory errors
```bash
# Check memory usage
free -h

# Reduce GPU memory allocation
# In ~/.ollama/config.yaml:
gpu_memory_limit: 18gb    # Reduce from 24gb

# Restart Ollama
sudo systemctl restart ollama.service
```

### Issue: Slow inference on CPU
```bash
# Check CPU usage
top
# Look for cpu% per ollama process

# Reduce parallel tasks
OLLAMA_NUM_PARALLEL=1
```

---

## Distributed Setup (Optional)

For scaling to multiple machines:

```bash
# On inference nodes:
OLLAMA_HOST=0.0.0.0:11434   # Listen on all interfaces

# On client machines:
OLLAMA_HOST=http://inference-server:11434

# PostgreSQL setup for audit logs:
sudo -u postgres createdb gemma_os
```

---

## Next Steps

1. **Load SKILLs** — Copy to `~/.gemma-os/skills/`
2. **Add documents** — Upload PDFs to AnythingLLM
3. **Test workflows** — Run examples from [WORKFLOWS.md](WORKFLOWS.md)

---

## Additional Resources

- [Ollama on Linux](https://github.com/ollama/ollama/blob/main/README.md)
- [NVIDIA CUDA Setup](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/)
- [CrewAI Documentation](https://crewai.readthedocs.io/)

---

**Installation complete!** Proceed to [WORKFLOWS.md](WORKFLOWS.md) for example use cases.

Last updated: May 2026
