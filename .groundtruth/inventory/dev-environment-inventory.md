# GT-KB Development Environment Inventory

Generated: 2026-06-26T21:49:02Z
Collector: gtkb-dev-environment-inventory-v1 (sha256:8212ae6b1de0eca07cb3f425165ffb5dcd13b4b1b68981b6a2dfa221eae808e0)

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
| `pip` | verified | `25.2` | `python -m pip --version` |
| `playwright` | unsupported | `unknown` | `playwright --version` |
| `pytest` | verified | `9.0.3` | `python -m pytest --version` |
| `python` | verified | `3.14.0` | `python --version` |
| `ruff` | verified | `0.15.12` | `python -m ruff --version` |

## Harness And Repo Surfaces

- Harness identity source present: True
- Role assignment source present: True
- Skills: 37
- Claude hooks: 32
- Codex hooks: 27
- GitHub workflows: 17
- MCP config: local_only presence only

## Role By Harness Compatibility

| Harness | Role | Assignment Status | Configured/Verified Capabilities |
|---|---|---|---:|
| claude | prime-builder | configured | 14 |
| codex | prime-builder | configured | 16 |
| claude | loyal-opposition | configured | 14 |
| codex | loyal-opposition | configured | 16 |

## Verification

- Latest command: `python scripts/collect_dev_environment_inventory.py`
- Release gate check: `python scripts/release_candidate_gate.py --skip-python --skip-frontend`
