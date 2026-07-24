# Security Policy for 拓漫 TouMan

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.19.x  | ✅ |
| < 0.19  | ❌ |

## Reporting a Vulnerability

拓漫 TouMan is built on top of Hermes Agent (Nous Research). Security vulnerabilities
in the upstream Hermes Agent should be reported via their [security policy](https://github.com/NousResearch/hermes-agent/security).

For vulnerabilities specific to the 拓漫 customization layer (scripts/, skills/, config/):

1. **Do NOT open a public GitHub issue** for security vulnerabilities.
2. Email the maintainers directly or open a [security advisory](https://github.com/eren11qq/tuoman-sales/security/advisories).
3. You should receive a response within 48 hours.

## Supply Chain Security

拓漫 manages dependencies through exact version pins in `pyproject.toml`:

- All core dependencies are pinned to `==X.Y.Z` (no version ranges)
- `uv.lock` is committed and must stay in sync with `pyproject.toml`
- Dependabot is configured for weekly automated updates
- OSV-scanner runs weekly to detect known vulnerabilities
- The `[all]` extra excludes any package that can be lazy-installed at runtime
  (supply-chain risk reduction per [Hermes Agent policy](https://github.com/NousResearch/hermes-agent))

### Dependency Review Process

1. A dependency is added only if it's needed by every session (core deps).
2. Provider-specific packages (Anthropic, Firecrawl, Exa, FAL, etc.) live in
   optional extras and are lazy-installed at first use.
3. Before bumping a pin, run `uv lock` to regenerate the lock file.
4. Pin bumps are reviewed for CVE fixes and supply-chain incidents.

## Secret Handling

- API keys are loaded from `~/.hermes/.env` (not in the repo).
- The `cli-config.yaml` file is gitignored (may contain SSH paths).
- No secrets, tokens, or credentials are committed to the repository.

## Runtime Security

- Tool execution supports sandboxed environments (Docker, Modal, SSH).
- Command approval system for destructive operations.
- Tool guardrails classify tools as idempotent vs mutating.
- Credential pool with scope-based access control.
