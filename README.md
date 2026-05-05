# piped

![Python](https://img.shields.io/badge/python-3.12+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Tests](https://img.shields.io/badge/tests-37%20passed-brightgreen)
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
piped diff --source .env.production --target .env.staging

# output
KEY          SOURCE      TARGET      STATUS
──────────────────────────────────────────────
DB_HOST      localhost   localhost   in sync
DB_PORT      5432        5432        in sync
API_KEY      ••••••••    (not set)   source only
STRIPE_KEY   (not set)   ••••••••    target only
DB_PASS      ••••••••    ••••••••    differs
```

## Supported platforms

| Platform | Read | Write | Status |
|---|---|---|---|
| `.env` files | ✅ | ✅ | available |
| GitLab CI Variables | ✅ | ✅ | coming soon |
| Terraform Cloud | ✅ | ✅ | coming soon |
| GitHub Actions | ✅ | ✅ | coming soon |

## Installation

```bash
pip install piped
```

## Usage

```bash
# diff two .env files
piped --source .env.production --target .env.staging
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

## License

MIT