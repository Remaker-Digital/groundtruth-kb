# GT-KB Development Environment Inventory

Generated: 2026-06-16T12:17:01Z
Collector: gtkb-dev-environment-inventory-v1 (sha256:61d23cb8e64e6a66d45eb02faf81eac9ebba575138a86c907369e89dfb6dbc12)

## Project

- Name: GroundTruth-KB host workspace
- Configured project name: GroundTruth-KB Platform
- GT-KB package version: 0.7.0rc1
- Scaffold version: 0.7.0rc1

## Redaction

- Status: pass
- Sensitive local environment entries detected: 1
- Public output excludes raw credential values, local-only key names, and absolute local paths.

## Toolchain

| Tool | Status | Version | Evidence |
|---|---|---|---|
| `gh` | verified | `2.83.2` | `gh --version` |
| `git` | verified | `2.51.2.windows.1` | `git --version` |
| `node` | verified | `24.11.1` | `node --version` |
| `npm` | verified | `11.6.2` | `npm --version` |
| `pip` | verified | `26.1.2` | `python -m pip --version` |
| `playwright` | unsupported | `unknown` | `playwright --version` |
| `pytest` | verified | `9.0.2` | `python -m pytest --version` |
| `python` | verified | `3.14.0` | `python --version` |
| `ruff` | verified | `0.15.5` | `python -m ruff --version` |

## Harness And Repo Surfaces

- Harness identity source present: True
- Role assignment source present: True
- Skills: 35
- Claude hooks: 33
- Codex hooks: 26
- GitHub workflows: 17
- MCP config: local_only presence only

## Role By Harness Compatibility

| Harness | Role | Assignment Status | Configured/Verified Capabilities |
|---|---|---|---:|
| claude | prime-builder | configured | 13 |
| codex | prime-builder | configured | 15 |
| claude | loyal-opposition | configured | 13 |
| codex | loyal-opposition | configured | 15 |

## Verification

- Latest command: `python scripts/collect_dev_environment_inventory.py`
- Release gate check: `python scripts/release_candidate_gate.py --skip-python --skip-frontend`
