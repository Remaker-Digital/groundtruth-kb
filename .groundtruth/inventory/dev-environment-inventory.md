# GT-KB Development Environment Inventory

Generated: 2026-05-07T04:20:11Z
Collector: gtkb-dev-environment-inventory-v1 (sha256:7741a1bc3e166a958e3c689cf28eb27c56a46b4c4471ecc77f1140a6a763c449)

## Project

- Name: GroundTruth-KB host workspace
- Configured project name: Agent Red Customer Experience
- GT-KB package version: 0.7.0rc1
- Scaffold version: 0.6.1

## Redaction

- Status: pass
- Sensitive local environment entries detected: 2
- Public output excludes raw credential values, local-only key names, and absolute local paths.

## Toolchain

| Tool | Status | Version | Evidence |
|---|---|---|---|
| `gh` | verified | `2.83.2` | `gh --version` |
| `git` | verified | `2.51.2.windows.1` | `git --version` |
| `node` | verified | `24.11.1` | `node --version` |
| `npm` | verified | `11.6.2` | `npm --version` |
| `pip` | verified | `25.3` | `python -m pip --version` |
| `playwright` | unsupported | `unknown` | `playwright --version` |
| `pytest` | verified | `9.0.2` | `python -m pytest --version` |
| `python` | verified | `3.14.0` | `python --version` |
| `ruff` | verified | `0.15.5` | `python -m ruff --version` |

## Harness And Repo Surfaces

- Harness identity source present: True
- Role assignment source present: True
- Skills: 25
- Claude hooks: 11
- Codex hooks: 7
- GitHub workflows: 16
- MCP config: local_only presence only

## Role By Harness Compatibility

| Harness | Role | Assignment Status | Configured/Verified Capabilities |
|---|---|---|---:|
| claude | prime-builder | verified | 14 |
| codex | prime-builder | configured | 16 |
| claude | loyal-opposition | configured | 14 |
| codex | loyal-opposition | verified | 16 |

## Verification

- Latest command: `python scripts/collect_dev_environment_inventory.py --public-json docs/release/dev-environment-inventory.json --public-markdown docs/release/dev-environment-inventory.md --local-json .gtkb-state/dev-environment-inventory/local.json`
- Release gate check: `python scripts/release_candidate_gate.py --skip-python --skip-frontend`
