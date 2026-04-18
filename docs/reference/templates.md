# Templates Reference

GroundTruth KB ships 30 template files used by `gt project init` and
`gt bootstrap-desktop` to scaffold new projects. Templates are organized
by category and copied selectively based on the chosen profile and options.

## Template Inventory

### Project Files

| Template | Copied to | Description |
|----------|-----------|-------------|
| `templates/CLAUDE.md` | `CLAUDE.md` | Claude Code project instructions |
| `templates/MEMORY.md` | `MEMORY.md` | Session state and operational memory |
| `templates/rules/canonical-terminology.md` | `.claude/rules/canonical-terminology.md` | Canonical ADR-0001 glossary (MemBase, DA, Prime Builder, Loyal Opposition, etc.) |
| `templates/rules/canonical-terminology.toml` | `.claude/rules/canonical-terminology.toml` | Profile-aware doctor config (required terms + required files + severity) |
| `templates/BRIDGE-INVENTORY.md` | `BRIDGE-INVENTORY.md` | Bridge automation component registry |
| `templates/README.md` | `README.md` | Project README with setup instructions |
| `templates/project/Makefile` | `Makefile` | Common tasks: test, lint, serve, assert |
| `templates/project/.editorconfig` | `.editorconfig` | Editor settings (indent, charset, EOL) |
| `templates/project/.pre-commit-config.yaml` | `.pre-commit-config.yaml` | Pre-commit hooks (ruff, trailing whitespace) |
| `templates/project/env.example` | `.env.example` | Environment variable template |

### Dual-Agent Files

These are included when the profile is `dual-agent` or `dual-agent-webapp`:

| Template | Copied to | Description |
|----------|-----------|-------------|
| `templates/project/AGENTS.md` | `AGENTS.md` | Loyal Opposition operating contract |
| `templates/project/codex-bootstrap/CODEX-REVIEW-OPERATING-CONTRACT.md` | `independent-progress-assessments/` | Review ground rules |
| `templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md` | `independent-progress-assessments/` | Codex session startup checklist |
| `templates/project/codex-bootstrap/CODEX-WAY-OF-WORKING.md` | `independent-progress-assessments/` | Codex operating principles |
| `templates/project/codex-bootstrap/LOYAL-OPPOSITION-LOG.md` | `independent-progress-assessments/` | Running review log |

### Web Application Files

These are included when the profile is `dual-agent-webapp`:

| Template | Copied to | Description |
|----------|-----------|-------------|
| `templates/project/Dockerfile` | `Dockerfile` | Container build for the web UI |
| `templates/project/docker-compose.yml` | `docker-compose.yml` | Local multi-container setup |
| `templates/project/settings.local.json` | `.claude/settings.local.json` | Claude Code local settings |

### CI Workflows

Included unless `--no-include-ci` is passed:

| Template | Copied to | Description |
|----------|-----------|-------------|
| `templates/ci/build.yml` | `.github/workflows/build.yml` | Docker build and push |
| `templates/ci/deploy.yml` | `.github/workflows/deploy.yml` | Deployment pipeline |
| `templates/ci/test.yml` | `.github/workflows/test.yml` | Test and lint checks |

### Hooks

Claude Code automation hooks, copied to `.claude/hooks/`:

| Template | Copied to | Description |
|----------|-----------|-------------|
| `templates/hooks/assertion-check.py` | `.claude/hooks/assertion-check.py` | Session-start assertion runner |
| `templates/hooks/credential-scan.py` | `.claude/hooks/credential-scan.py` | Pre-commit credential scanner |
| `templates/hooks/destructive-gate.py` | `.claude/hooks/destructive-gate.py` | Dangerous command blocker |
| `templates/hooks/intake-classifier.py` | `.claude/hooks/intake-classifier.py` | Requirement intake classifier (F5) |
| `templates/hooks/scheduler.py` | `.claude/hooks/scheduler.py` | Bridge poller scheduler |
| `templates/hooks/session-health.py` | `.claude/hooks/session-health.py` | Session health snapshot on Stop (F7) |
| `templates/hooks/spec-classifier.py` | `.claude/hooks/spec-classifier.py` | Spec-first workflow enforcer (legacy) |

### Rules

Agent behavior rules, copied to `.claude/rules/`:

| Template | Copied to | Description |
|----------|-----------|-------------|
| `templates/rules/prime-builder.md` | `.claude/rules/prime-builder.md` | Prime Builder operating rules |
| `templates/rules/loyal-opposition.md` | `.claude/rules/loyal-opposition.md` | Loyal Opposition rules |
| `templates/rules/prime-bridge-collaboration-protocol.md` | `.claude/rules/prime-bridge-collaboration-protocol.md` | Bridge exchange protocol |
| `templates/rules/bridge-poller-canonical.md` | `.claude/rules/bridge-poller-canonical.md` | Canonical bridge poller pattern |
| `templates/rules/report-depth.md` | `.claude/rules/report-depth.md` | Report quality standard |

### Bridge Automation

| Template | Description |
|----------|-------------|
| `templates/bridge-os-poller-setup-prompt.md` | Prompt template for setting up OS-level bridge pollers |

## Profile Matrix

Which templates are included per profile:

| Category | `local-only` | `dual-agent` | `dual-agent-webapp` |
|----------|:---:|:---:|:---:|
| Project files | yes | yes | yes |
| Hooks | yes | yes | yes |
| Rules (prime-builder) | yes | yes | yes |
| CI workflows | opt-in | opt-in | opt-in |
| Dual-agent files | | yes | yes |
| Rules (LO, bridge, report) | | yes | yes |
| Web app files | | | yes |
| Bridge automation | | yes | yes |

## Customization

Template files are copied once at scaffold time. After creation, they belong
to your project — edit them freely. The `gt project upgrade` command can
refresh templates to the current version, but respects customization flags
and defaults to dry-run mode.

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
