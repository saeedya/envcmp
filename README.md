# envcmp

![Python](https://img.shields.io/badge/python-3.12+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-77%20passed-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![CI](https://github.com/saeedya/envcmp/actions/workflows/ci.yml/badge.svg)

A lightweight CLI tool to sync CI/CD variables and secrets between platforms.

## The problem

Your variables live in multiple places:

- Terraform Cloud workspace
- GitLab CI variables
- GitHub Actions secrets
- `.env` files

They should always be in sync — but no tool does this automatically.

## Solution

```bash
# see what's different
envcmp diff --from gitlab:my-project --to terraform:my-workspace

# output
KEY          SOURCE      TARGET      STATUS
──────────────────────────────────────────────
DB_HOST      localhost   localhost   in sync
DB_PORT      5432        5432        in sync
API_KEY      ••••••••    (not set)   source only
STRIPE_KEY   (not set)   ••••••••    target only
DB_PASS      ••••••••    ••••••••    differs

# push changes from source to target
envcmp push --from gitlab:my-project --to terraform:my-workspace

# dry run — see what would be pushed
envcmp push --from gitlab:my-project --to terraform:my-workspace --dry-run
```

## Supported platforms

| Platform | Read | Write | Status |
|---|---|---|---|
| `.env` files | ✅ | ✅ | available |
| GitLab CI Variables | ✅ | ✅ | available |
| Terraform Cloud | ✅ | ✅ | available |
| GitHub Actions | ✅ | ✅ | beta — write requires repo admin |

## Installation

```bash
pip install envcmp
```

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```dotenv
GITLAB_URL=https://gitlab.com
GITLAB_TOKEN=glpat-...
GITLAB_PROJECT_ID=12345678

GITHUB_TOKEN=ghp_...
GITHUB_ORGANIZATION=my-org
GITHUB_REPOSITORY=my-repo

TERRAFORM_TOKEN=...
TERRAFORM_ORGANIZATION=my-org
TERRAFORM_WORKSPACE=my-workspace
```

## Usage

```bash
# diff between two providers
envcmp diff --from gitlab:my-project --to terraform:my-workspace

# diff between two .env files
envcmp diff --from env:.env.production --to env:.env.staging

# push changes
envcmp push --from gitlab:my-project --to terraform:my-workspace

# dry run
envcmp push --from env:.env --to env:.env.staging --dry-run

# pull changes from target to source
envcmp pull --from env:.env.local --to gitlab:my-project

# dry run
envcmp pull --from env:.env.local --to gitlab:my-project --dry-run

```

## Development

```bash
git clone https://github.com/your-username/envcmp.git
cd envcmp
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Security

- Secret values are never printed in plain text
- All output uses masked values (`••••••••`)
- Dependencies scanned with `pip-audit` and `bandit`

## Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a branch: `git checkout -b feat/your-feature`
3. Make your changes
4. Run tests: `pytest tests/unit/ tests/security/`
5. Run pre-commit: `pre-commit run --all-files`
6. Commit: `git commit -m "feat: your feature"`
7. Push and open a Pull Request

See [docs/contributing.md](docs/contributing.md) for more details.

## License

MIT