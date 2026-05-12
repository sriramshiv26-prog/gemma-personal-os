# Gemma 4 Personal OS - Testing Roadmap

**Phase:** 5 (Final Validation)  
**Current Status:** macOS Complete, Linux/Windows Ready  
**Target:** Cross-platform validation complete by 2026-05-15

---

## Test Status Summary

| Platform | Status | Completion | Next Steps |
|----------|--------|-----------|-----------|
| **macOS** | ✓ Complete | 100% | N/A |
| **Linux** | ⏳ Ready | 0% | Run tests (manual or Docker) |
| **Windows** | ⏳ Ready | 0% | Run tests (WSL2 or native + Docker) |

---

## Testing Options by Platform

### Option 1: Manual Installation (Recommended for Learning)

**Linux:**
```bash
bash tests/test_linux.sh
# Or follow: tests/CROSS_PLATFORM_TEST_GUIDE.md (Part 1)
```

**Windows:**
```powershell
powershell -File tests/test_windows.ps1
# Or follow: tests/CROSS_PLATFORM_TEST_GUIDE.md (Part 2)
```

### Option 2: Docker (Recommended for Speed)

**Ubuntu 22.04:**
```bash
cd tests/
docker build -f Dockerfile.ubuntu -t gemma-test-ubuntu ..
docker run --rm gemma-test-ubuntu
```

**Alpine (Lightweight):**
```bash
cd tests/
docker build -f Dockerfile.alpine -t gemma-test-alpine ..
docker run --rm gemma-test-alpine
```

**Multi-Platform (Simultaneous):**
```bash
cd tests/
docker-compose up
# Follow: tests/DOCKER_TESTING_GUIDE.md for details
```

---

## Linux Testing Checklist

### Prerequisites
- [ ] Ubuntu 20.04+ OR RHEL/Fedora OR Alpine
- [ ] Python 3.8+
- [ ] Git installed
- [ ] 10GB free disk space (for models)
- [ ] 4GB+ RAM available

### Installation
- [ ] Clone repository: `git clone ...`
- [ ] Install Ollama
- [ ] Pull Gemma models: `ollama pull gemma2:{2b,26b}`
- [ ] Create Python venv
- [ ] Install dependencies: `pip install -r requirements.txt`

### Testing
- [ ] Run integration tests: `python3 tests/integration_test.py`
- [ ] Verify 6/6 tests passing
- [ ] Save results: `python3 tests/integration_test.py > linux_results.txt`

### Documentation
- [ ] Create `LINUX_TEST_RESULTS.md` from template
- [ ] Document system info (`uname -a`, `python --version`)
- [ ] Record performance metrics
- [ ] Note any platform-specific issues

### Submission
- [ ] Add results to git: `git add LINUX_TEST_RESULTS.md`
- [ ] Commit: `git commit -m "test: linux integration test results"`
- [ ] Push: `git push origin main`

---

## Windows Testing Checklist

### Prerequisites
- [ ] Windows 11 with WSL2 OR Windows with native Ollama
- [ ] Python 3.8+
- [ ] Git installed
- [ ] Docker installed (optional, but recommended)
- [ ] 10GB free disk space (for models)
- [ ] 4GB+ RAM available

### WSL2 Installation
- [ ] Enable WSL2: `wsl --install`
- [ ] Set default version: `wsl --set-default-version 2`
- [ ] Launch Ubuntu in WSL2: `wsl`
- [ ] Follow Linux testing checklist above (inside WSL2)

### Native Windows Installation (Alternative)
- [ ] Install Python from python.org
- [ ] Install Git from git-scm.com
- [ ] Install Ollama from ollama.ai
- [ ] Follow Windows-specific PowerShell commands

### Testing
- [ ] Run integration tests: `python tests/integration_test.py`
- [ ] Verify 6/6 tests passing
- [ ] Save results: `python tests/integration_test.py | Tee-Object -FilePath windows_results.txt`

### Documentation
- [ ] Create `WINDOWS_TEST_RESULTS.md` from template
- [ ] Document system info (`systeminfo`, `python --version`)
- [ ] Record performance metrics
- [ ] Note any platform-specific issues

### Submission
- [ ] Add results to git
- [ ] Commit and push results

---

## Expected Test Results

### All Platforms Should Show:

```
✓ Ollama Health Check: PASS
✓ Model Inference (2B): PASS
✓ Model Inference (26B): PASS
✓ Model Routing: PASS (4/4 correct routing decisions)
✓ Database Logging: PASS (task creation, update, retrieval)
✓ SKILL Loading: PASS (framework ready)
✓ Workflow Execution: PASS (end-to-end execution)

Results: 6/6 passing
```

### Performance Baseline:

- Inference latency: <1s (test mode)
- Database operations: <5ms
- Workflow execution: <10ms
- Total test suite: <30s

---

## Success Criteria

### Linux Testing
- [ ] 6/6 tests passing
- [ ] No critical errors
- [ ] Results committed to GitHub
- [ ] Performance baseline documented

### Windows Testing
- [ ] 6/6 tests passing
- [ ] No critical errors
- [ ] Results committed to GitHub
- [ ] Performance baseline documented

### Overall Completion
- [ ] All three platforms tested
- [ ] Cross-platform comparison created
- [ ] No regressions vs macOS baseline
- [ ] System marked "production ready"

---

## Troubleshooting Matrix

| Issue | Linux | Windows | Docker | Solution |
|-------|-------|---------|--------|----------|
| Models not found | Check `ollama list` | Check `ollama list` | Build fails | Run `ollama pull gemma2:2b` first |
| Connection refused | Start daemon | Start daemon | Check port | `ollama serve &` or `-p 11434:11434` |
| Permission denied | `chmod +x test_linux.sh` | Run as Admin | N/A | Fix file permissions |
| Out of memory | Increase RAM | Increase RAM | Increase Docker RAM | Use Alpine image (lighter) |
| Python version | `python3 --version` | `python --version` | Check image | Need 3.8+ |

---

## Timeline Estimate

| Task | Time | Notes |
|------|------|-------|
| Manual Linux (Ubuntu) | 30-45 min | Ollama pull takes ~10 min |
| Manual Windows/WSL2 | 45-60 min | WSL2 setup, then Linux steps |
| Docker Ubuntu | 10-15 min | First run (model pull), ~10s after |
| Docker Alpine | 5-10 min | Faster, uses less disk |
| Docker Compose (both) | 15-20 min | Parallel testing |

**Recommended:** Use Docker for speed, manual for learning

---

## GitHub Integration

### Create Results Branch (Optional)

```bash
# Create feature branch for test results
git checkout -b test/linux-windows-validation

# Add results
git add LINUX_TEST_RESULTS.md WINDOWS_TEST_RESULTS.md
git commit -m "test: cross-platform validation complete"

# Create pull request
gh pr create --title "test: Linux and Windows validation" \
  --body "Cross-platform integration testing complete. All platforms passing."

# Merge when ready
gh pr merge --merge
```

### Results Documentation

Each platform should document:

```markdown
# Integration Test Results - Linux

**Platform:** Ubuntu 22.04  
**Date:** 2026-05-13  
**Tester:** [Your Name]

## System Information
- Kernel: [uname -r]
- Python: [python3 --version]
- Ollama: [ollama --version]
- RAM: [free -h]

## Test Summary
- Health Check: ✓ PASS
- Model Inference: ✓ PASS
- Model Routing: ✓ PASS (4/4)
- Database: ✓ PASS
- SKILL Loading: ✓ PASS
- Workflow Execution: ✓ PASS

**Overall: 6/6 PASS**

## Performance Metrics
- 2B Inference: _ms
- 26B Inference: _ms
- Database ops: _ms
- Total test time: _s

## Notes
[Any observations or issues]
```

---

## Post-Testing Activities

### When All Platforms Pass (6/6)

1. **Create Cross-Platform Comparison**
   ```bash
   # Create comparison document
   cat > CROSS_PLATFORM_RESULTS.md <<EOF
   # Cross-Platform Test Results Summary
   
   | Platform | Date | Status | Notes |
   |----------|------|--------|-------|
   | macOS | 2026-05-12 | ✓ 6/6 | Baseline |
   | Linux | 2026-05-13 | ✓ 6/6 | [notes] |
   | Windows | 2026-05-13 | ✓ 6/6 | [notes] |
   EOF
   ```

2. **Update Main README**
   ```markdown
   ## Platform Support Status
   - ✓ macOS (Apple Silicon & Intel)
   - ✓ Linux (Ubuntu, RHEL, Alpine)
   - ✓ Windows 11 (WSL2 & Native)
   
   See [CROSS_PLATFORM_RESULTS.md](CROSS_PLATFORM_RESULTS.md) for details.
   ```

3. **Mark System as Production Ready**
   ```bash
   # Update version
   echo "1.0.0-validated" > VERSION.txt
   
   # Final commit
   git add VERSION.txt CROSS_PLATFORM_RESULTS.md
   git commit -m "feat: mark system production ready (all platforms validated)"
   git push origin main
   ```

4. **Create Release Tag**
   ```bash
   git tag -a v1.0.0-beta -m "Cross-platform validation complete"
   git push origin v1.0.0-beta
   ```

---

## What's Next After Testing

### Phase 6: Production Deployment
- [ ] Performance optimization
- [ ] Load testing (100+ concurrent tasks)
- [ ] Security audit
- [ ] Team onboarding

### Phase 7: Advanced Features
- [ ] Implement additional SKILLs
- [ ] Add web dashboard
- [ ] Create Slack/Teams integrations
- [ ] Setup CI/CD pipeline

---

## Reference Documents

### For Linux Testing
- `tests/CROSS_PLATFORM_TEST_GUIDE.md` (Part 1)
- `tests/test_linux.sh`
- `tests/Dockerfile.ubuntu`

### For Windows Testing
- `tests/CROSS_PLATFORM_TEST_GUIDE.md` (Part 2)
- `tests/test_windows.ps1`
- `tests/docker-compose.yml`

### For Docker Testing
- `tests/DOCKER_TESTING_GUIDE.md`
- `tests/Dockerfile.ubuntu`
- `tests/Dockerfile.alpine`
- `tests/docker-compose.yml`

### Guides & Documentation
- `tests/INTEGRATION_TEST_RESULTS.md` (macOS baseline)
- `tests/CROSS_PLATFORM_TEST_GUIDE.md` (Complete manual guide)
- `tests/DOCKER_TESTING_GUIDE.md` (Docker instructions)
- `SKILLS_TESTING_LOG.md` (Phase 5 summary)

---

## Quick Command Reference

### macOS (Already Done)
```bash
# Already tested and passing
git show a2d6800  # Integration testing commit
git show 5272f15  # Testing log commit
```

### Linux (Ready)
```bash
# Option 1: Manual
bash tests/test_linux.sh

# Option 2: Docker
docker build -f tests/Dockerfile.ubuntu -t gemma-test:ubuntu .
docker run --rm gemma-test:ubuntu
```

### Windows (Ready)
```powershell
# Option 1: Manual (WSL2)
wsl bash tests/test_linux.sh

# Option 2: PowerShell
powershell -File tests/test_windows.ps1

# Option 3: Docker
docker run --rm -f tests/Dockerfile.windows gemma-test:windows
```

### Multi-Platform (Ready)
```bash
# Docker Compose (simultaneous testing)
cd tests/
docker-compose up
docker-compose logs -f
docker-compose down
```

---

## Support & Issues

If tests fail:

1. **Check Troubleshooting Section** in CROSS_PLATFORM_TEST_GUIDE.md
2. **Review Docker Logs** for container-based tests
3. **Verify System Requirements** (Python 3.8+, RAM, disk space)
4. **Check Ollama Status** (`ollama serve`, model availability)
5. **Create GitHub Issue** with:
   - Platform & version
   - Error output
   - Test log (full output)
   - System specs

---

## Completion Checklist

### Individual Platform Testing

**Linux:**
- [ ] Prerequisites met
- [ ] Repository cloned
- [ ] Ollama installed & models pulled
- [ ] Python venv created
- [ ] Dependencies installed
- [ ] Tests executed
- [ ] 6/6 passing
- [ ] Results documented
- [ ] Results committed to GitHub

**Windows:**
- [ ] Prerequisites met
- [ ] WSL2 enabled (or native Ollama installed)
- [ ] Repository cloned
- [ ] Ollama installed & models pulled
- [ ] Python venv created
- [ ] Dependencies installed
- [ ] Tests executed
- [ ] 6/6 passing
- [ ] Results documented
- [ ] Results committed to GitHub

### Final Validation

- [ ] All three platforms tested
- [ ] 6/6 passing on each
- [ ] Cross-platform comparison created
- [ ] README updated with status
- [ ] System marked "Production Ready"
- [ ] Release tag created (v1.0.0 or similar)
- [ ] Team notified of completion

---

**Roadmap Version:** 1.0  
**Created:** 2026-05-12  
**Last Updated:** 2026-05-12  
**Target Completion:** 2026-05-15  
**Status:** Ready for Linux & Windows Testing
