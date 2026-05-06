# envcmp — Claude guide

## What is this project?
A CLI tool to sync CI/CD variables and secrets between platforms.
Example: GitLab CI → Terraform Cloud, or GitHub Actions → .env file

## Key commands

```bash
# Install for development
pip install -e ".[dev]"

# Run all tests
pytest tests/unit/ tests/security/

# Unit tests only
pytest tests/unit/

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Security scan
bandit -r src/

# Audit dependencies
pip-audit

# Run pre-commit hooks
pre-commit run --all-files
```

## Project structure

```text
src/envcmp/
├── models.py          ← Variable, DiffResult, ProviderKind
├── cli.py             ← diff, push, pull commands
├── differ.py          ← comparison logic between two providers
├── config.py          ← read credentials from .env
└── providers/
├── base.py        ← abstract class
├── env_file.py    ← read/write .env files
├── gitlab.py      ← GitLab CI Variables API
├── github.py      ← GitHub Actions Secrets API
└── terraform.py   ← Terraform Cloud Variables API
```

## Coding rules

- All public functions must have type hints and docstrings
- Never print a real secret value — always use `masked_value()`
- Every new file must have tests — coverage must stay above 80%
- Unit tests must never call external APIs — always mock them

## Do not

- Print real secret values anywhere
- Add new dependencies without a good reason
- Write a new provider without inheriting from `BaseProvider`
- Write integration tests without mocking external APIs

## Current status

### Phase 1 ✅
- [x] models.py
- [x] providers/base.py
- [x] providers/env_file.py
- [x] differ.py
- [x] cli.py — diff, push, pull commands

### Phase 2 ✅
- [x] providers/gitlab.py
- [x] providers/terraform.py
- [x] providers/github.py
- [x] config.py

### Phase 3 ✅
- [x] security tests
- [x] pre-commit hooks
- [x] GitHub Actions CI
- [x] PyPI publish — pip install envcmp
- [x] Landing page — envcmp.dev

### Phase 4 — Next
- [ ] --filter flag
- [ ] TUI — envcmp ui
- [ ] HashiCorp Vault provider
- [ ] AWS Secrets Manager provider
- [ ] Pulumi ESC provider