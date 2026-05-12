# Installation Guide — macOS (Apple Silicon)

**Tested on:** macOS 13.0+, Apple M1/M2/M3 with 32GB RAM  
**Installation time:** ~15 minutes  
**Difficulty:** Intermediate

---

## System Requirements

### Minimum
- **CPU:** Apple M1 (8-core GPU, 8GB performance cores)
- **RAM:** 24GB (16GB for 2B only, 32GB recommended for both models)
- **Storage:** 100GB SSD free
- **OS:** macOS 13.0+ (Ventura, Sonoma)

### Recommended
- **CPU:** Apple M2/M3
- **RAM:** 32GB+ (allows model hot-swapping)
- **Storage:** 250GB SSD
- **Network:** Gigabit ethernet (for RAG large documents)

---

## Pre-Installation Checklist

```bash
# Check OS version
system_profiler SPSoftwareDataType | grep "System Version"

# Check available RAM
vm_stat | grep "Pages free:" | awk '{print ($3 * 4096 / 1024 / 1024 / 1024) "GB"}'

# Check free disk space
df -h / | grep -oE "[0-9]+\.[0-9]+Gi" | tail -1
```

All three should meet minimum requirements before proceeding.

---

## Step 1: Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Verify installation
brew --version
# Should output: Homebrew 4.x.x
```

---

## Step 2: Install Dependencies

```bash
# Update Homebrew
brew update

# Install core dependencies
brew install \
  python@3.11 \
  git \
  curl \
  graphviz \
  libffi \
  openssl \
  sqlite

# Install PostgreSQL (for distributed deployments)
brew install postgresql

# Verify Python installation
python3 --version
# Should output: Python 3.11.x
```

---

## Step 3: Install Ollama

Ollama is the runtime for Gemma models on Apple Silicon.

```bash
# Download and install Ollama
# https://ollama.ai/download/mac

# Or via Homebrew (if available)
brew install ollama

# Verify installation
ollama --version
# Should output: ollama version x.x.x
```

### Configure Ollama for Optimal Performance

Create `~/.ollama/config.yaml`:

```yaml
# macOS Ollama Configuration
num_parallel: 2              # Parallel inference (adjust for M1/M2/M3)
num_gpu: -1                  # Use GPU (-1 = auto-detect)
mmap: true                   # Memory-mapped model loading
num_thread: 8                # CPU threads (M1 = 4 performance cores available)
embedding_batch_size: 32

# Memory management
gpu_memory_limit: 24gb       # Reserve 24GB for models
gpu_memory_fraction: 0.85    # Use 85% of GPU VRAM
```

---

## Step 4: Download Gemma Models

```bash
# Start Ollama daemon
ollama serve &

# In another terminal, pull models
ollama pull gemma2:26b       # Expert reasoning model (~15GB)
ollama pull gemma2:2b        # Fast response model (~2GB)

# Verify models loaded
ollama list
# Output should show:
# NAME              ID              SIZE    MODIFIED
# gemma2:26b        a5f9edb3e2f6    15 GB   2 minutes ago
# gemma2:2b         59bf8a49b7be    2.0 GB  1 minute ago
```

**Time estimate:** 10-15 minutes (depends on internet speed)

---

## Step 5: Set Up Python Virtual Environment

```bash
# Navigate to project directory
cd ~/gemma-personal-os

# Create virtual environment
python3 -m venv venv

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
  sqlalchemy==2.0.0
```

---

## Step 6: Configure Environment Variables

```bash
# Create .env file from template
cp config/.env.example .env

# Edit with your configuration
nano .env
```

**Essential variables:**

```bash
# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_NUM_PARALLEL=2
OLLAMA_GPU_MEMORY=24gb

# Model Selection
CREW_AI_LLM=gemma2:26b         # Expert model
CREW_AI_LLM_FAST=gemma2:2b     # Fast model

# AnythingLLM Configuration
ANYTHINGLLM_HOST=http://localhost:3001
ANYTHINGLLM_API_KEY=default

# Serper.dev (optional, for web search)
SERPER_API_KEY=your_serper_key_here

# Logging
AUDIT_LOG_PATH=/var/log/gemma-os/audit.log
LOG_LEVEL=INFO
```

---

## Step 7: Install AnythingLLM (Private RAG)

```bash
# Create directory for AnythingLLM
mkdir -p ~/anythingllm

# Install via Docker (recommended) or direct
# Option A: Docker
docker run -d \
  --name anythingllm \
  -p 3001:3001 \
  -v ~/anythingllm:/data \
  mintplexlabs/anythingllm:latest

# Option B: Direct installation (requires Node.js)
# npm install -g anythingllm
# anythingllm start
```

**Verify installation:**
```bash
curl http://localhost:3001
# Should return AnythingLLM web interface
```

---

## Step 8: Initialize Project

```bash
# Activate virtual environment
source venv/bin/activate

# Create required directories
mkdir -p \
  ~/.gemma-os/results \
  ~/.gemma-os/cache \
  ~/.gemma-os/skills \
  /var/log/gemma-os

# Initialize database
python3 -c "from src.gemma_os import init_db; init_db()"

# Load default SKILLs
python3 -c "from src.gemma_os import load_skills; load_skills()"
```

---

## Step 9: Verification

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Test CrewAI
python3 << 'EOF'
from crewai import Agent, Task, Crew
print("✓ CrewAI imported successfully")
EOF

# Test AnythingLLM
python3 << 'EOF'
import requests
response = requests.get("http://localhost:3001/api/system/health")
print(f"✓ AnythingLLM status: {response.status_code}")
EOF

# Test basic inference
python3 << 'EOF'
import ollama
response = ollama.generate(model="gemma2:2b", prompt="Hello!")
print(f"✓ Ollama 2B model: {response['response'][:50]}...")
EOF
```

**All checks should pass before proceeding.**

---

## Step 10: Configure Launchd (Optional - Auto-Start)

To auto-start Ollama and AnythingLLM on login:

```bash
# Create Ollama launch agent
cat > ~/Library/LaunchAgents/local.ollama.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>local.ollama</string>
    <key>Program</key>
    <string>/usr/local/bin/ollama</string>
    <key>ProgramArguments</key>
    <array>
        <string>serve</string>
    </array>
    <key>StandardOutPath</key>
    <string>/var/log/ollama.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/ollama-error.log</string>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Load the agent
launchctl load ~/Library/LaunchAgents/local.ollama.plist
```

---

## Quick Start

```bash
# Terminal 1: Start Ollama (if not using launchd)
ollama serve

# Terminal 2: Activate venv and run a task
source venv/bin/activate
python3 -m gemma_os.main --task "security-audit" --file code.py

# Terminal 3: View results
cat ~/.gemma-os/results/latest.md
```

---

## Performance Tuning

### For M1 (8GB GPU, 8 CPU cores):

```bash
# .env tuning
OLLAMA_NUM_PARALLEL=1          # Single task at a time
CREW_AI_LLM_FAST=gemma2:2b    # Use fast model by default
```

### For M2/M3 (10GB+ GPU):

```bash
# .env tuning
OLLAMA_NUM_PARALLEL=2          # Two concurrent tasks
OLLAMA_GPU_MEMORY=28gb        # Allocate more VRAM
```

### Memory Optimization:

```bash
# Reduce context window if RAM-constrained
python3 -m gemma_os.main --context-length 4096 --task <name>

# Monitor memory usage
vm_stat | grep "Pages free:" | awk '{print ($3 * 4096 / 1024 / 1024 / 1024) "GB free"}'
```

---

## Troubleshooting

### Issue: "Ollama: command not found"
```bash
# Reinstall Ollama
brew uninstall ollama
brew install ollama
# Or download from: https://ollama.ai/download/mac
```

### Issue: "Out of memory" errors
```bash
# Reduce GPU memory allocation in ~/.ollama/config.yaml
gpu_memory_limit: 18gb    # Reduce from 24gb

# Restart Ollama
launchctl unload ~/Library/LaunchAgents/local.ollama.plist
launchctl load ~/Library/LaunchAgents/local.ollama.plist
```

### Issue: Models not loading
```bash
# Check Ollama logs
tail -f /var/log/ollama.log

# Re-pull models
ollama pull gemma2:26b --verbose
```

### Issue: AnythingLLM connection refused
```bash
# Check if Docker is running
docker ps | grep anythingllm

# Restart AnythingLLM
docker restart anythingllm

# Check logs
docker logs anythingllm
```

### Issue: Slow inference (>30 seconds)
```bash
# Check model not being swapped to disk
ps aux | grep ollama

# Monitor GPU usage
powermetrics -n 1 | grep "GPU Power"

# Reduce parallel tasks
OLLAMA_NUM_PARALLEL=1
```

---

## Monitoring

```bash
# Check Ollama performance
curl http://localhost:11434/api/ps

# View audit logs
tail -f ~/.gemma-os/audit.log

# Check disk usage
du -sh ~/.gemma-os/

# Monitor system resources
top -o %GPU    # Shows GPU usage
vm_stat | grep -E "Pages (free|wire)" | awk '{sum += $3} END {print sum * 4096 / 1024 / 1024 / 1024 "GB"}'
```

---

## Next Steps

1. **Configure SKILLs** — Copy skills to `~/.gemma-os/skills/`
2. **Load documents** — Add PDFs to AnythingLLM for RAG
3. **Test workflows** — Run example tasks from [WORKFLOWS.md](WORKFLOWS.md)
4. **Monitor performance** — Check metrics and adjust tuning

---

## Additional Resources

- [Ollama Documentation](https://github.com/ollama/ollama)
- [Gemma Model Card](https://huggingface.co/google/gemma-7b)
- [CrewAI Docs](https://crewai.readthedocs.io/)
- [AnythingLLM Setup](https://docs.anythingllm.com/)

---

**Installation complete!** Proceed to [WORKFLOWS.md](WORKFLOWS.md) for example use cases.

Last updated: May 2026
