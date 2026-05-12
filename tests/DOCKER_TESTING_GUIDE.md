# Docker-Based Integration Testing Guide

**Purpose:** Run integration tests across platforms using Docker containers  
**Platforms:** Ubuntu 22.04, Alpine Linux, other Linux distributions  
**Benefits:** No Ollama installation needed, reproducible test environment, cross-platform validation

---

## Quick Start

### Prerequisites

```bash
# Install Docker
https://docs.docker.com/get-docker/

# Install Docker Compose
https://docs.docker.com/compose/install/

# Verify installation
docker --version
docker-compose --version
```

### Run Tests in Docker

**Option 1: Docker Compose (Recommended)**

```bash
cd tests/
docker-compose up
```

This will:
1. Build Ubuntu 22.04 container
2. Install dependencies
3. Start Ollama daemon
4. Pull Gemma models
5. Run integration tests
6. Save results to `tests/results-ubuntu/`

**Option 2: Individual Container**

```bash
cd tests/

# Build Ubuntu image
docker build -f Dockerfile.ubuntu -t gemma-test-ubuntu ..

# Run tests
docker run --rm \
  -v $(pwd)/results-ubuntu:/app/results \
  gemma-test-ubuntu
```

---

## Understanding Docker Setup

### File Structure

```
tests/
├── docker-compose.yml          # Multi-container orchestration
├── Dockerfile.ubuntu            # Ubuntu 22.04 test environment
├── Dockerfile.alpine            # Alpine Linux test environment (optional)
├── integration_test.py          # Core test suite
├── test_linux.sh               # Linux shell script runner
├── CROSS_PLATFORM_TEST_GUIDE.md # Manual testing guide
└── results-*/                   # Test output directories
```

### Container Specifications

**Ubuntu 22.04 Container**
- Base: `ubuntu:22.04`
- Python: 3.10
- Ollama: Latest
- Gemma Models: 2B + 26B
- Port: 11434

**Alpine Linux Container**
- Base: `alpine:latest`
- Python: 3.10
- Ollama: Latest
- Gemma Models: 2B + 26B
- Port: 11435

---

## Advanced Usage

### Build Images Separately

```bash
# Build Ubuntu image
docker build -f tests/Dockerfile.ubuntu \
  -t gemma-test:ubuntu \
  .

# Build Alpine image
docker build -f tests/Dockerfile.alpine \
  -t gemma-test:alpine \
  .

# View built images
docker images | grep gemma-test
```

### Run with Custom Options

```bash
# Run with interactive shell
docker run -it \
  -v $(pwd):/app \
  gemma-test:ubuntu \
  /bin/bash

# Run with specific port mapping
docker run -p 9999:11434 \
  gemma-test:ubuntu

# Run with environment variables
docker run -e PYTHONUNBUFFERED=1 \
  -e DEBUG=1 \
  gemma-test:ubuntu
```

### View Container Logs

```bash
# View Ubuntu container logs
docker logs gemma-test-ubuntu

# Follow logs in real-time
docker logs -f gemma-test-ubuntu

# Save logs to file
docker logs gemma-test-ubuntu > ubuntu_test.log
```

### Access Container Shell

```bash
# Start container in interactive mode
docker run -it gemma-test:ubuntu /bin/bash

# From running container
docker exec -it gemma-test-ubuntu /bin/bash

# Inside container:
# - Run manual tests
# - Check database
# - Inspect logs
# - Debug issues
```

---

## Test Output & Results

### Docker Compose Output

```
Creating network "tests_gemma-network" with driver "bridge"
Building test-ubuntu
Step 1/11 : FROM ubuntu:22.04
...
Successfully built abc123def456
Creating gemma-test-ubuntu ... done
Attaching to gemma-test-ubuntu
gemma-test-ubuntu | Starting Ollama daemon...
gemma-test-ubuntu | Pulling Gemma models...
gemma-test-ubuntu | Running integration tests...
gemma-test-ubuntu | ==============================...
```

### Accessing Results

Results are saved to mounted volumes:

```bash
# Ubuntu test results
ls -la tests/results-ubuntu/

# Alpine test results
ls -la tests/results-alpine/

# Copy specific results
cp tests/results-ubuntu/integration_test.json .

# View results
cat tests/results-ubuntu/INTEGRATION_TEST_RESULTS.md
```

---

## Performance Considerations

### Container Startup Time

| Phase | Duration | Notes |
|-------|----------|-------|
| Build | 2-5 min | One-time, cached afterwards |
| Ollama daemon start | 5-10s | Fast, cached model |
| Model pulling | 5-10 min | First time only, cached |
| Tests | 1-5 sec | Actual test execution |
| **Total** | **~10 min** | First run, ~10s subsequent |

### Resource Requirements

```
Memory:     4GB minimum (8GB recommended)
CPU:        2 cores minimum (4+ cores recommended)
Disk:       20GB (for models)
Network:    For model downloads
```

### Optimizing Performance

```bash
# Use Docker BuildKit for faster builds
export DOCKER_BUILDKIT=1
docker build ...

# Limit resource usage
docker run --memory="4g" --cpus="2" gemma-test:ubuntu

# Use tmpfs for faster I/O
docker run --tmpfs /tmp:rw,size=1g gemma-test:ubuntu
```

---

## Troubleshooting Docker Tests

### Issue: Out of Memory

```bash
# Solution: Increase Docker memory limit
# macOS/Windows: Docker Desktop Settings → Resources
# Linux: Check free memory (free -h)

# Alternative: Use Alpine (lighter weight)
docker build -f Dockerfile.alpine .
```

### Issue: Model Pull Timeout

```bash
# Solution: Increase timeout
docker run --timeout 900 gemma-test:ubuntu

# Alternative: Pull models in advance
docker run -it gemma-test:ubuntu ollama pull gemma2:26b
```

### Issue: Ollama Connection Refused

```bash
# Solution: Check Ollama health
docker exec gemma-test-ubuntu curl http://localhost:11434/api/tags

# Alternative: Verify port mapping
docker port gemma-test-ubuntu
```

### Issue: Test Results Not Saved

```bash
# Solution: Verify volume mounts
docker inspect gemma-test-ubuntu | grep Mounts

# Alternative: Copy from container
docker cp gemma-test-ubuntu:/app/results/ ./results-backup/
```

---

## Comparing Container Results

### Multi-Platform Comparison Script

```bash
#!/bin/bash
# compare_platforms.sh

echo "Comparing integration test results across platforms..."

echo ""
echo "=== Ubuntu Results ==="
cat results-ubuntu/INTEGRATION_TEST_RESULTS.md | grep -A 5 "TEST SUMMARY"

echo ""
echo "=== Alpine Results ==="
cat results-alpine/INTEGRATION_TEST_RESULTS.md | grep -A 5 "TEST SUMMARY"

echo ""
echo "=== Performance Comparison ==="
diff <(jq '.model_inference' results-ubuntu/*.json) \
     <(jq '.model_inference' results-alpine/*.json)
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests (Docker)

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v1
      
      - name: Run tests
        run: |
          cd tests
          docker-compose up --abort-on-container-exit
      
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: tests/results-*/
```

---

## Production Deployment Validation

### Pre-Deployment Checklist

- [ ] All Docker tests passing (6/6)
- [ ] Performance baseline established
- [ ] Resource requirements documented
- [ ] Container images built and tested
- [ ] Results committed to GitHub
- [ ] Cross-platform comparison complete

### Scaling Tests

```bash
# Run tests in parallel across platforms
docker-compose up -d  # Start all containers
docker-compose logs -f  # Monitor all

# Scale to multiple instances
docker-compose up -d --scale test-ubuntu=3

# Stop and cleanup
docker-compose down -v  # Remove volumes too
```

---

## Next Steps

### After Successful Docker Testing

1. **Document results**
   ```bash
   mkdir -p tests/results-summary
   cp tests/results-*/*.md tests/results-summary/
   ```

2. **Commit to GitHub**
   ```bash
   git add tests/results-*
   git commit -m "test: docker-based cross-platform validation"
   git push origin main
   ```

3. **Update README**
   - Add Docker testing instructions
   - Document platform test status
   - Link to results

4. **Cleanup images (optional)**
   ```bash
   docker image prune -a  # Remove unused images
   docker volume prune    # Remove unused volumes
   ```

---

## Docker Best Practices

### Security

```bash
# Run as non-root user
docker run --user appuser gemma-test:ubuntu

# Read-only filesystem
docker run --read-only gemma-test:ubuntu

# No privileged mode
# (don't use --privileged unless necessary)
```

### Optimization

```bash
# Multi-stage builds (in Dockerfile)
FROM ubuntu:22.04 as builder
# ... build dependencies ...

FROM ubuntu:22.04
COPY --from=builder /app /app
# ... smaller final image ...
```

### Monitoring

```bash
# Monitor container resources
docker stats gemma-test-ubuntu

# Inspect container details
docker inspect gemma-test-ubuntu

# View container processes
docker top gemma-test-ubuntu
```

---

## Reference

- Docker Docs: https://docs.docker.com
- Docker Compose: https://docs.docker.com/compose
- Ollama: https://ollama.ai
- Gemma: https://ai.google.dev/gemma

---

**Guide Version:** 1.0  
**Last Updated:** 2026-05-12  
**Applicable to:** Gemma 4 Personal OS v1.0+
