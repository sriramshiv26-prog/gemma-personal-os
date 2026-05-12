# Cross-Platform Integration Testing Guide

**Objective:** Validate Gemma 4 Personal OS on Linux and Windows platforms  
**Baseline:** macOS results (Task 4, 2026-05-12)  
**Status:** macOS ✓ Complete | Linux ⏳ Ready | Windows ⏳ Ready

---

## Part 1: Linux Integration Testing

### Prerequisites Check

```bash
# Verify Python 3.8+
python3 --version

# Verify Git
git --version

# Verify curl (for Ollama health check)
curl --version
```

### Step 1: Clone Repository

```bash
git clone https://github.com/sriramshiv26-prog/gemma-personal-os.git
cd gemma-personal-os
```

### Step 2: Install Ollama (if not already installed)

**Ubuntu/Debian:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
# Start daemon
ollama serve &
```

**RHEL/Fedora/CentOS:**
```bash
# Install from source or pre-built binary
curl -L https://ollama.ai/download/ollama-linux-amd64.tgz | tar xz
sudo mv ollama /usr/local/bin/
ollama serve &
```

**Alpine Linux:**
```bash
apk add --no-cache curl
curl -L https://ollama.ai/download/ollama-linux-alpine.tgz | tar xz
./ollama serve &
```

### Step 3: Pull Gemma 2 Models

```bash
# Pull 2B model (lightweight)
ollama pull gemma2:2b

# Pull 26B model (expert)
ollama pull gemma2:26b

# Verify models loaded
ollama list
```

**Expected Output:**
```
NAME            ID              SIZE    MODIFIED
gemma2:2b       c1864c3881a8    1.6 GB  2 minutes ago
gemma2:26b      91556a8e1f24    16 GB   5 minutes ago
```

### Step 4: Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 5: Run Integration Tests

**Option A: Automatic Test Script**
```bash
bash tests/test_linux.sh
```

**Option B: Manual Test Execution**
```bash
python3 tests/integration_test.py
```

**Option C: With Verbose Output**
```bash
python3 -u tests/integration_test.py 2>&1 | tee linux_test_results.log
```

### Step 6: Document Results

After tests complete, capture:
```bash
# Save test output
python3 tests/integration_test.py > LINUX_TEST_OUTPUT.txt 2>&1

# Verify database created
ls -lh ~/.gemma-os/gemma_os.db

# Check system info for report
uname -a > LINUX_SYSTEM_INFO.txt
python3 --version >> LINUX_SYSTEM_INFO.txt
```

### Expected Linux Results

Based on macOS baseline, Linux should show:

| Test | Expected Result | Tolerance |
|-----|---|---|
| Health Check | ✓ PASS | Strict |
| Model Inference | ✓ PASS | Strict |
| Model Routing | ✓ PASS | Strict |
| Database Logging | ✓ PASS | Strict |
| SKILL Loading | ✓ PASS | Strict |
| Workflow Execution | ✓ PASS | Strict |

**Success Criteria:** 6/6 passing (same as macOS)

---

## Part 2: Windows Integration Testing

### Prerequisites Check (PowerShell)

```powershell
# Verify Python
python --version

# Verify Git
git --version

# Verify WSL2 (Windows 11)
wsl --list --verbose
```

### Step 1: Enable WSL2 (Windows 11)

```powershell
# Run as Administrator
wsl --install

# Set default version
wsl --set-default-version 2

# List distributions
wsl --list --verbose

# Launch Ubuntu in WSL2
wsl
```

### Step 2: Inside WSL2 Terminal

Clone repository and follow Linux instructions above:

```bash
git clone https://github.com/sriramshiv26-prog/gemma-personal-os.git
cd gemma-personal-os

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve &

# Pull models
ollama pull gemma2:2b
ollama pull gemma2:26b

# Setup Python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python3 tests/integration_test.py
```

### Alternative: Native Windows Ollama

If not using WSL2:

```powershell
# Install Ollama for Windows
# Download from: https://ollama.ai

# Start Ollama (via GUI or command)
ollama serve

# In PowerShell terminal:
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python tests/integration_test.py
```

### Step 3: Document Results

```powershell
# Save output
python tests/integration_test.py | Tee-Object -FilePath WINDOWS_TEST_OUTPUT.txt

# System info
systeminfo | Tee-Object -FilePath WINDOWS_SYSTEM_INFO.txt
python --version | Add-Content WINDOWS_SYSTEM_INFO.txt

# WSL2 info (if using WSL2)
wsl -- uname -a | Add-Content WINDOWS_SYSTEM_INFO.txt
```

### Expected Windows Results

Same as Linux/macOS:

| Test | Expected Result |
|-----|---|
| Health Check | ✓ PASS |
| Model Inference | ✓ PASS |
| Model Routing | ✓ PASS |
| Database Logging | ✓ PASS |
| SKILL Loading | ✓ PASS |
| Workflow Execution | ✓ PASS |

**Success Criteria:** 6/6 passing

---

## Part 3: Comparing Results Across Platforms

### Test Output Analysis

Each platform should produce similar JSON structure:

```json
{
  "health_check": {"status": "PASS"},
  "model_inference": {
    "gemma2:2b": {"status": "PASS", "time_seconds": <value>},
    "gemma2:26b": {"status": "PASS", "time_seconds": <value>}
  },
  "model_routing": {
    "simple_task": {"model": "gemma2:2b", "complexity": "simple"},
    "complex_task": {"model": "gemma2:26b", "complexity": "complex"}
  },
  "database_logging": {"status": "PASS", "task_id": "<id>"},
  "skill_loading": {"status": "PASS"},
  "workflow_execution": {"status": "PASS", "execution_time": <ms>}
}
```

### Performance Comparison Template

Create `CROSS_PLATFORM_COMPARISON.md`:

```markdown
# Cross-Platform Test Comparison

## Inference Performance

| Platform | Gemma 2B | Gemma 26B | Average |
|----------|----------|-----------|---------|
| macOS    | 0.00s    | 0.00s     | 0.00s   |
| Linux    | _s       | _s        | _s      |
| Windows  | _s       | _s        | _s      |

## Model Routing Accuracy

| Platform | Simple → 2B | Complex → 26B | Overall |
|----------|----------|-----------|---------|
| macOS    | 2/2 ✓     | 2/2 ✓     | 100% ✓  |
| Linux    | _         | _         | _%      |
| Windows  | _         | _         | _%      |

## Database Operations

| Platform | Creation | Update | Query | Average |
|----------|----------|--------|-------|---------|
| macOS    | <1ms     | <1ms   | <5ms  | <2ms    |
| Linux    | _ms      | _ms    | _ms   | _ms     |
| Windows  | _ms      | _ms    | _ms   | _ms     |

## Overall Status

- macOS:   ✓ COMPLETE (6/6 passing)
- Linux:   ⏳ PENDING
- Windows: ⏳ PENDING
```

---

## Part 4: Troubleshooting

### Common Issues

**Issue: Ollama connection refused**
```
Solution: Ensure Ollama is running
$ ollama serve &

Verify:
$ curl http://localhost:11434/api/tags
```

**Issue: Models not found**
```
Solution: Pull models first
$ ollama pull gemma2:2b
$ ollama pull gemma2:26b
```

**Issue: Python version mismatch**
```
Solution: Use Python 3.8+
$ python3 --version
# If older, install Python 3.9+ or use venv
```

**Issue: Permission denied on test scripts**
```
Solution (Linux):
$ chmod +x tests/test_linux.sh
$ bash tests/test_linux.sh

Solution (Windows PowerShell):
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
powershell -File tests/test_windows.ps1
```

**Issue: Database locked**
```
Solution: Remove old database and reinitialize
$ rm ~/.gemma-os/gemma_os.db
$ python3 tests/integration_test.py
```

---

## Part 5: Reporting Results

### Result Template

Create a file: `PLATFORM_TEST_RESULTS_<PLATFORM>.md`

```markdown
# Integration Test Results - <PLATFORM>

**Platform:** <OS Name and Version>
**Test Date:** <Date>
**Tester:** <Name>
**Duration:** <Total Time>

## System Information
- OS: <uname output>
- Python: <python --version>
- Ollama: <ollama --version>
- CPU: <processor info>
- RAM: <memory available>

## Test Results Summary
- Health Check: <PASS/FAIL>
- Model Inference: <PASS/FAIL>
- Model Routing: <PASS/FAIL>
- Database Logging: <PASS/FAIL>
- SKILL Loading: <PASS/FAIL>
- Workflow Execution: <PASS/FAIL>

**Overall:** X/6 Passing

## Performance Metrics
- Inference (2B): <time>s
- Inference (26B): <time>s
- Routing accuracy: <percentage>%
- Database latency: <time>ms
- Workflow execution: <time>ms

## Notes
<Any observations, issues, solutions>

## Raw Output
<Attach full test output or save separately>
```

### Push Results to GitHub

```bash
# Create results document
# ... fill template above ...

# Commit results
git add PLATFORM_TEST_RESULTS_*.md
git add CROSS_PLATFORM_COMPARISON.md
git commit -m "test: document <PLATFORM> integration test results"
git push origin main
```

---

## Part 6: Success Criteria

### Completion Checklist

**Linux Testing:**
- [ ] Ollama installed and running
- [ ] Both Gemma models pulled
- [ ] Python venv created and activated
- [ ] Dependencies installed
- [ ] Integration test suite executed
- [ ] All 6 tests passing
- [ ] Results documented
- [ ] Results committed to GitHub

**Windows Testing:**
- [ ] WSL2 installed (or native Ollama)
- [ ] Ollama installed and running
- [ ] Both Gemma models pulled
- [ ] Python venv created and activated
- [ ] Dependencies installed
- [ ] Integration test suite executed
- [ ] All 6 tests passing
- [ ] Results documented
- [ ] Results committed to GitHub

### Final Validation

Once all platforms tested:

```bash
# Review cross-platform comparison
cat CROSS_PLATFORM_COMPARISON.md

# Verify all results committed
git log --oneline | head -10

# Summary
echo "Platform Validation Complete!"
```

---

## Next Steps After Testing

1. **All platforms passing (6/6)?**
   - ✓ YES → Proceed to Phase 6 (Performance Optimization)
   - ✗ NO → Review troubleshooting section

2. **Document any platform-specific observations**
   - Performance differences
   - Installation gotchas
   - Ollama model load times
   - Database initialization times

3. **Update main README with platform test status**
   - Add test results link
   - Document platform-specific notes

4. **Ready for production deployment**
   - All platforms validated
   - Installation guides proven
   - Performance baseline established
   - Ready for team rollout

---

## Support

For issues during testing:
1. Check troubleshooting section above
2. Review GitHub Issues: https://github.com/sriramshiv26-prog/gemma-personal-os/issues
3. Consult platform-specific documentation
4. File detailed issue with test output

---

**Guide Version:** 1.0  
**Last Updated:** 2026-05-12  
**Applicable to:** Gemma 4 Personal OS v1.0+
