# Changelog

## [0.1.0] - 2026-05-05

### Added
- `diff-cmd` command — show differences between two providers
- `push` command — sync variables from source to target (with `--dry-run`)
- `pull` command — sync variables from target to source (with `--dry-run`)
- Providers: `.env` files, GitLab CI, Terraform Cloud, GitHub Actions
- Secret masking — values never exposed in output or repr
- Config loader from environment variables
- pre-commit hooks — ruff, mypy, bandit
- GitHub Actions CI pipeline
- 77 unit and security tests — 100% coverage