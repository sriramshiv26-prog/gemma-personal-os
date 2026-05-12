# Contributing to Gemma 4 Personal OS

Thank you for your interest in contributing! This guide explains how to contribute code, SKILLs, and documentation.

## Code of Conduct

- Be respectful and inclusive
- Focus on technical merit
- Help others learn

## Getting Started

1. **Fork the repository**
   ```bash
   git clone https://github.com/sriramshiv26-prog/gemma-personal-os.git
   cd gemma-personal-os
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes and commit**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

4. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Adding SKILLs

SKILLs are the easiest way to contribute domain expertise:

1. **Create SKILL.md** in `skills/your-domain/SKILL.md`

```markdown
---
name: your-skill-name
version: 1.0
domain: Your Domain
---

# Your SKILL Name

## Reference Patterns
- Pattern 1: [description]
- Pattern 2: [description]

## Tools
- `tool_name(param)` → output

## Examples
[Example usage]
```

2. **Test your SKILL**
   ```bash
   python3 -m gemma_os.main --skill your-skill-name --test
   ```

3. **Submit PR** with SKILL documentation

## Code Style

- **Python:** PEP 8 (use `black` formatter)
- **Documentation:** GitHub Flavored Markdown
- **Commits:** Conventional commits (feat:, fix:, docs:)

## Testing

Run tests before submitting:

```bash
pytest tests/
pytest tests/test_workflows.py -v
```

## Documentation

- Update README.md for new features
- Add docstrings to functions
- Include examples in SKILLs

## Pull Request Process

1. Update CHANGELOG.md
2. Run tests and linting
3. Describe changes clearly
4. Link relevant issues
5. Wait for review

---

Questions? Open an issue or check [ARCHITECTURE.md](docs/ARCHITECTURE.md).

Last updated: May 2026
