# piped

![Python](https://img.shields.io/badge/python-3.12+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-74%20passed-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

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
piped diff-cmd --from gitlab:my-project --to terraform:my-workspace

# output
KEY          SOURCE      TARGET      STATUS
──────────────────────────────────────────────
DB_HOST      localhost   localhost   in sync
DB_PORT      5432        5432        in sync
API_KEY      ••••••••    (not set)   source only
STRIPE_KEY   (not set)   ••••••••    target only
DB_PASS      ••••••••    ••••••••    differs

# push changes from source to target
piped push --from gitlab:my-project --to terraform:my-workspace

# dry run — see what would be pushed
piped push --from gitlab:my-project --to terraform:my-workspace --dry-run
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
pip install piped
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
piped diff-cmd --from gitlab:my-project --to terraform:my-workspace

# diff between two .env files
piped diff-cmd --from env:.env.production --to env:.env.staging

# push changes
piped push --from gitlab:my-project --to terraform:my-workspace

# dry run
piped push --from env:.env --to env:.env.staging --dry-run

# pull changes from target to source
piped pull --from env:.env.local --to gitlab:my-project

# dry run
piped pull --from env:.env.local --to gitlab:my-project --dry-run

```

## Development

```bash
git clone https://github.com/your-username/piped.git
cd piped
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Security

- Secret values are never printed in plain text
- All output uses masked values (`••••••••`)
- Dependencies scanned with `pip-audit` and `bandit`

## License

MIT