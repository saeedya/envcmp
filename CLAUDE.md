# piped — Claude guide

## What is this project?
A CLI tool to sync CI/CD variables and secrets between platforms.
Example: GitLab CI → Terraform Cloud, or GitHub Actions → .env file

## Key commands

```bash
# Install for development
pip install -e ".[dev]"

# Run all tests
pytest

# Unit tests only (fast, no external API calls)
pytest tests/unit/

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Security scan
bandit -r src/
```

## Project structure

src/piped/
├── models.py          ← Variable, DiffResult, ProviderKind
├── cli.py             ← entry point — diff/push/pull commands
├── differ.py          ← comparison logic between two providers
└── providers/
├── base.py        ← abstract class — all providers inherit from this
├── env_file.py    ← read/write .env files
├── gitlab.py      ← GitLab CI Variables API
├── github.py      ← GitHub Actions Secrets API
└── terraform.py   ← Terraform Cloud Variables API

## Coding rules

- All public functions must have type hints and docstrings
- Never print a real secret value — always use `masked_value()`
- Every new file must have tests — coverage must stay above 80%
- Unit tests must never call external APIs — always mock them

## Do not

- Print real secret values anywhere
- Add new dependencies without a good reason — keep this tool lightweight
- Write a new provider without inheriting from `BaseProvider`
- Write integration tests without mocking external APIs

## Current status

### Phase 1 ✅
- [x] models.py — Variable, DiffResult, ProviderKind
- [x] providers/base.py
- [x] providers/env_file.py
- [x] differ.py
- [x] cli.py

### Phase 2 ✅
- [x] providers/gitlab.py
- [x] providers/terraform.py
- [x] providers/github.py

### Phase 3
- [x] config.py — read credentials from .env or ~/.piped.toml
- [ ] update cli.py — support --from and --to flags with real providers