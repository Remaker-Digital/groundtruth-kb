# GroundTruth KB (GT-KB)

> **An Internal Developer Platform for AI-assisted software development.** GT-KB reduces an owner's routine role to specifications, clarifications, and decisions while AI agents preserve durable artifacts, create tests, implement approved work, verify outcomes, and maintain release-readiness evidence.

[![Python Tests](https://github.com/Remaker-Digital/groundtruth-kb/actions/workflows/python-tests.yml/badge.svg?branch=develop)](https://github.com/Remaker-Digital/groundtruth-kb/actions/workflows/python-tests.yml)
[![Lint](https://github.com/Remaker-Digital/groundtruth-kb/actions/workflows/lint.yml/badge.svg?branch=develop)](https://github.com/Remaker-Digital/groundtruth-kb/actions/workflows/lint.yml)
![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)

---

## What GT-KB is

In GT-KB terminology, an **application** is the lifecycle object the platform manages — a software project under governance. The **platform** is GT-KB itself, the lifecycle infrastructure. A **hosted application** is an application deployed and running in service, distinct from its lifecycle record.

Application development progresses through **backlog selection**: the unified view of all known work for an application or platform, organized by project and sub-project groupings. Owner direction surfaces requirements; AI agents draft implementation proposals reviewed via the file bridge; only approved proposals are implemented; only specification-derived tests can verify completion.

Two AI roles coordinate through versioned bridge artifacts: **Prime Builder** proposes and implements; **Loyal Opposition** reviews, critiques, and verifies. Owner decisions, deliberations, and rationale are preserved in the **Deliberation Archive** so future sessions inherit the project's reasoning, not just its current state.

---

## Key components

- **MemBase** — the canonical, append-only knowledge database for governed records (specifications, tests, work items, procedures, documents, environment configuration). Implemented as `groundtruth.db` (SQLite). Every mutation creates a new versioned row with `changed_by`, `changed_at`, and `change_reason`. See [`MEMBASE-4-CLAUDE.md`](MEMBASE-4-CLAUDE.md).

- **Deliberation Archive** — the design-reasoning tier. A searchable archive of decisions, reviews, and rejected alternatives that answers *why* the project is the way it is. Implemented as the `deliberations` table in `groundtruth.db` with semantic indexing.

- **File bridge protocol** — the dual-agent coordination surface (Prime Builder ↔ Loyal Opposition) implemented via versioned markdown files under `bridge/` and the canonical [`bridge/INDEX.md`](bridge/INDEX.md). Statuses: NEW → GO/NO-GO → NEW post-impl → VERIFIED. See [`.claude/rules/file-bridge-protocol.md`](.claude/rules/file-bridge-protocol.md).

- **`gt` CLI** — the platform command surface. `gt project init` scaffolds a project; `gt summary`, `gt assert`, `gt deliberations search`, `gt status`, `gt project doctor`, and `gt project upgrade` are daily operating commands. See [`groundtruth-kb/docs/start-here.md`](groundtruth-kb/docs/start-here.md).

- **Dashboard** — the KPI surface for governance, release-readiness, drift, and bridge state. Optional Grafana integration; basic surfaces always available via the `gt` CLI.

---

## Quick links

| Resource | Path |
|----------|------|
| **Repository** | [github.com/Remaker-Digital/groundtruth-kb](https://github.com/Remaker-Digital/groundtruth-kb) |
| **Package README & quick-start** | [`groundtruth-kb/README.md`](groundtruth-kb/README.md) |
| **New-adopter guide** | [`groundtruth-kb/docs/start-here.md`](groundtruth-kb/docs/start-here.md) |
| **Evaluator guide** | [`groundtruth-kb/docs/cto-evaluation.md`](groundtruth-kb/docs/cto-evaluation.md) |
| **Harness governance** | [`AGENTS.md`](AGENTS.md), [`.claude/rules/`](.claude/rules/) |
| **Contributing** | [`groundtruth-kb/CONTRIBUTING.md`](groundtruth-kb/CONTRIBUTING.md) |
| **Security policy** | [`SECURITY.md`](SECURITY.md) |
| **Package license (AGPL-3.0-or-later)** | [`groundtruth-kb/LICENSE`](groundtruth-kb/LICENSE) |
| **Root license (legacy)** | [`LICENSE`](LICENSE) |

---

## Adopting GT-KB

Adopters install the package and scaffold a project:

```sh
pip install groundtruth-kb
gt project init <project-name>
```

The scaffold places governance rules (canonical terminology, file bridge protocol, root-boundary contract) under your project root and initializes MemBase. See [`groundtruth-kb/docs/start-here.md`](groundtruth-kb/docs/start-here.md) for the full first-run flow, the dual-agent (Prime Builder / Loyal Opposition) topology, and the operating-model walkthrough.

---

## Repository status

This repository builds the GT-KB platform itself. Current platform version: **`0.7.0rc1`** (release candidate). The version source of truth is [`groundtruth-kb/src/groundtruth_kb/__init__.py`](groundtruth-kb/src/groundtruth_kb/__init__.py); release-readiness evidence is gated by [`scripts/release_candidate_gate.py`](scripts/release_candidate_gate.py). Documentation references to earlier `0.6.0` / `0.6.1` versions in `groundtruth-kb/docs/` are scheduled for harmonization in an upcoming docs slice.

---

## Contributing

GT-KB development uses the file bridge protocol: every implementation proposal is reviewed before code is written, every implementation is verified against linked specifications before it is treated as done. See [`groundtruth-kb/CONTRIBUTING.md`](groundtruth-kb/CONTRIBUTING.md) for contributor onboarding and [`.claude/rules/file-bridge-protocol.md`](.claude/rules/file-bridge-protocol.md) for the protocol details.

---

## Licensing

GT-KB has two license surfaces:

- The **GT-KB package** distributed under [`groundtruth-kb/`](groundtruth-kb/) is licensed under [**AGPL-3.0-or-later**](groundtruth-kb/LICENSE). New code added under `groundtruth-kb/` inherits the package AGPL terms. This is the license under which GT-KB is published as a Python package.

- The **repository-root [`LICENSE`](LICENSE)** is a separate proprietary file that predates this repository's role as the GT-KB platform host. It is pending license-coherence reconciliation in a future bridge slice. The proprietary signal is *not* the canonical license for new GT-KB platform code; it remains in place as a legacy artifact while reconciliation work is scoped.

For code added elsewhere in the repository (outside `groundtruth-kb/`), consult both license files and contact the maintainer at the [project repository](https://github.com/Remaker-Digital/groundtruth-kb) for clarification.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved with respect to the proprietary signal at [`LICENSE`](LICENSE); GT-KB package contributions are governed by the AGPL terms at [`groundtruth-kb/LICENSE`](groundtruth-kb/LICENSE).
