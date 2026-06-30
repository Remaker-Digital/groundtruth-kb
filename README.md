# GroundTruth KB (GT-KB)

> **An Internal Developer Platform for AI-assisted software development.**
> You supply specifications, clarifications, and decisions. GT-KB and its AI agents preserve the durable artifacts, draft and review the work, implement what's approved, and verify it against the specs — so the project's *truth* and its *reasoning* both survive past any single session.

[![Python Tests](https://github.com/Remaker-Digital/groundtruth-kb/actions/workflows/python-tests.yml/badge.svg?branch=main)](https://github.com/Remaker-Digital/groundtruth-kb/actions/workflows/python-tests.yml)
[![Lint](https://github.com/Remaker-Digital/groundtruth-kb/actions/workflows/lint.yml/badge.svg?branch=main)](https://github.com/Remaker-Digital/groundtruth-kb/actions/workflows/lint.yml)
![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)
![Version 0.7.0-rc1](https://img.shields.io/badge/version-0.7.0--rc1-orange)
![License AGPL-3.0-or-later](https://img.shields.io/badge/package%20license-AGPL--3.0--or--later-green)

---

## Why GT-KB?

Most AI-assisted development loses the plot between sessions: decisions live in chat scrollback, "done" means "the model said so," and the next session re-derives context that was already settled. GT-KB makes the project a network of **durable, traceable artifacts** instead of a conversation.

- 🧭 **Owner role stays small.** Your job is specifications, clarifications, and trade-off decisions. Routine implementation, traceability, and verification are the platform's job.
- 🗄️ **One source of truth.** Specifications, tests, work items, and decisions live in an append-only knowledge database (**MemBase**) — every change versioned with *who*, *when*, and *why*. No silent overwrites.
- 🧠 **Reasoning is preserved.** The **Deliberation Archive** records *why* the project is the way it is — decisions, reviews, and rejected alternatives — so future sessions inherit judgement, not just state.
- 🤝 **Two AI roles, checks and balances.** A **Prime Builder** proposes and implements; a **Loyal Opposition** reviews, critiques, and verifies. Nothing ships without independent review.
- ✅ **"Verified" means verified.** Completion requires specification-derived tests that actually ran — not an assertion that a spec exists.
- 🔌 **Harness-agnostic.** The Prime Builder and Loyal Opposition roles attach to whatever AI coding harness you assign (Claude Code, Codex CLI, and others) — swap or combine harnesses without rewriting the governance.

---

## How it works

```
 owner direction ─▶ specification ─▶ implementation proposal ─▶ review (GO / NO-GO)
                                                                      │
                          VERIFIED ◀─ verification ◀─ implementation ─┘
```

1. **Owner direction** surfaces requirements; candidate requirements become specifications only with your visible confirmation.
2. **Prime Builder** drafts an implementation proposal citing the governing specifications and the tests that will prove it.
3. **Loyal Opposition** reviews via the **file bridge** and records `GO` or `NO-GO`. Implementation never starts without `GO`.
4. **Prime Builder** implements and files a report; **Loyal Opposition** runs the specification-derived tests and records `VERIFIED`.

Every step is a versioned artifact. The owner reads results and makes decisions — not boilerplate.

---

## Quick start

GT-KB is published as the Python package `groundtruth-kb`:

```sh
pip install groundtruth-kb

# Scaffold a new governed project (rules, MemBase, bridge protocol)
gt project init my-project
cd my-project

# Daily operating commands
gt summary                    # current state of specs, tests, work items
gt backlog list               # the standing backlog
gt deliberations search "…"   # why was this decided?
gt project doctor             # health checks across the platform
```

`gt project init` places the governance rules (canonical terminology, file-bridge protocol, project-root boundary) under your project root and initializes MemBase. See **[start-here.md](groundtruth-kb/docs/start-here.md)** for the full first-run flow, the dual-agent topology, and the operating-model walkthrough.

---

## Key components

| Component | What it is |
|-----------|-----------|
| **MemBase** | The canonical, append-only knowledge database for governed records — specifications, tests, work items, procedures, documents, environment config. Implemented as `groundtruth.db` (SQLite); every mutation is a new versioned row with `changed_by` / `changed_at` / `change_reason`. See [MEMBASE-4-CLAUDE.md](MEMBASE-4-CLAUDE.md). |
| **Deliberation Archive** | The design-reasoning tier: a searchable archive of decisions, reviews, and rejected alternatives that answers *why*. Implemented as the `deliberations` table with semantic indexing. |
| **File bridge protocol** | The dual-agent coordination surface (Prime Builder ↔ Loyal Opposition), versioned markdown under `bridge/`. After WI-4510 Phase-3 cutover, dispatcher/TAFE bridge state is canonical; retired bridge-index artifacts are not live queue authority. See [file-bridge-protocol.md](.claude/rules/file-bridge-protocol.md). |
| **`gt` CLI** | The platform command surface — `gt project init`, `gt summary`, `gt assert`, `gt backlog`, `gt deliberations`, `gt project doctor`, `gt project upgrade`. |
| **Dashboard** | KPI surface for governance, release-readiness, drift, and bridge state. Optional Grafana integration; core surfaces are always available via the CLI. |

---

## Documentation

| Resource | Where |
|----------|-------|
| **New-adopter guide** | [groundtruth-kb/docs/start-here.md](groundtruth-kb/docs/start-here.md) |
| **Evaluator guide** | [groundtruth-kb/docs/cto-evaluation.md](groundtruth-kb/docs/cto-evaluation.md) |
| **Package README** | [groundtruth-kb/README.md](groundtruth-kb/README.md) |
| **MemBase concepts** | [MEMBASE-4-CLAUDE.md](MEMBASE-4-CLAUDE.md) |
| **Harness governance** | [AGENTS.md](AGENTS.md), [.claude/rules/](.claude/rules/) |
| **Release health wiki source** | [groundtruth-kb/docs/wiki/release-health.md](groundtruth-kb/docs/wiki/release-health.md) |
| **Changelog** | [CHANGELOG.md](CHANGELOG.md) |
| **Contributing** | [CONTRIBUTING.md](CONTRIBUTING.md) |
| **Security policy** | [SECURITY.md](SECURITY.md) |

---

## Project status

GT-KB is at **`0.7.0-rc1`** (release candidate). The version source of truth is [`groundtruth-kb/src/groundtruth_kb/__init__.py`](groundtruth-kb/src/groundtruth_kb/__init__.py); release-readiness is gated by [`scripts/release_candidate_gate.py`](scripts/release_candidate_gate.py), the file bridge, dispatcher health, clean-candidate test evidence, and the dashboard release-health metrics. The release branch is `main`; README badges and published wiki pages should be compared against `main` before a formal release announcement.

Local dashboard refresh:

```powershell
groundtruth-kb/.venv/Scripts/python.exe scripts/gtkb_dashboard/refresh_dashboard_db.py --db-path .tmp/gtkb-dashboard-health.sqlite --project-root E:\GT-KB
```

Wiki source comparison:

```powershell
groundtruth-kb/.venv/Scripts/python.exe scripts/update_wiki_pages.py compare --wiki-dir .tmp/groundtruth-kb.wiki
```

This repository builds and governs the GT-KB platform itself — it is, by design, a working example of the platform applied to its own development.

---

## Contributing

GT-KB development uses the file-bridge protocol: every implementation proposal is reviewed before code is written, and every implementation is verified against linked specifications before it is treated as done. See **[CONTRIBUTING.md](CONTRIBUTING.md)** for contributor onboarding and **[.claude/rules/file-bridge-protocol.md](.claude/rules/file-bridge-protocol.md)** for the protocol details.

---

## License

GT-KB has two license surfaces:

- The published **`groundtruth-kb` package** (everything under [`groundtruth-kb/`](groundtruth-kb/)) is licensed under **[AGPL-3.0-or-later](groundtruth-kb/LICENSE)**. New code added under `groundtruth-kb/` inherits the package terms.
- The **repository root** carries a separate **proprietary** [`LICENSE`](LICENSE) covering platform-host material outside the package.

For code added elsewhere in the repository, consult both license files or contact the maintainer via the [project repository](https://github.com/Remaker-Digital/groundtruth-kb).

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. The `groundtruth-kb` package is distributed under AGPL-3.0-or-later; all other rights reserved with respect to the proprietary root [`LICENSE`](LICENSE).
