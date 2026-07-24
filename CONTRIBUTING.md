# Contributing to 拓漫 TouMan

Thank you for considering contributing to 拓漫 TouMan! This project is built on
[Hermes Agent](https://github.com/NousResearch/hermes-agent) by Nous Research.

## Development Setup

### Prerequisites

- Python 3.11, 3.12, or 3.13
- Git
- (Windows) PowerShell 5.1+

### Quick Start

```bash
# Clone the repo
git clone https://github.com/eren11qq/tuoman-sales.git
cd tuoman-sales

# Create venv and install
python -m venv .venv
.venv\Scripts\pip install -e ".[dev]"

# Run tests
.venv\Scripts\python -m pytest tests/ -v
```

### Using uv (recommended for lockfile consistency)

```bash
uv sync --frozen
uv pip install -e ".[dev]"
```

## Code Style

- **Linting**: Ruff with preview rules. Run `ruff check .` before committing.
- **Types**: Use type hints for all function signatures.
- **Tests**: pytest. New features require tests. Run `python -m pytest tests/ -v`.
- **Logging**: Use `logging.getLogger(__name__)` — never `print()`.
- **Prompts**: Add prompts to `config/prompts.yaml`, never hardcode in Python.

## Pull Request Process

1. Create a feature branch from `main`.
2. Make your changes with clear commit messages.
3. Ensure all tests pass: `python -m pytest tests/ -v`.
4. Run lint: `ruff check .`.
5. Open a PR with description of what and why.

## Project Structure

```
tuoman-sales/
├── skills/              # 拓漫 sales skills (auto-discovered by Hermes)
│   ├── lead-finder/
│   ├── company-researcher/
│   ├── enterprise-filter/
│   ├── outreach-generator/
│   ├── daily-report/
│   └── sales-outreach/
├── scripts/
│   ├── tuoman_daily.py  # Daily pipeline orchestrator
│   ├── tuoman-install.ps1  # Windows installer
│   ├── setup_scheduler.ps1  # Task scheduler setup
│   └── lib/             # Reusable data modules
│       ├── lead_utils.py
│       ├── scoring.py
│       ├── outreach.py
│       └── report_gen.py
├── config/
│   └── prompts.yaml     # Externalized pipeline prompts
├── tests/               # pytest test suite
└── .github/workflows/   # CI/CD pipelines
```

## Adding a New Skill

1. Create `skills/<skill-name>/SKILL.md` with YAML frontmatter.
2. Add the skill prompt to `config/prompts.yaml`.
3. Add pipeline stage to `scripts/tuoman_daily.py` (if needed).
4. Add tests for any new `lib/` module code.

## License

MIT — see [LICENSE](LICENSE).
