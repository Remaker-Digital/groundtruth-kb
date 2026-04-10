# GroundTruth Product Architecture

## Overview

GroundTruth is a single Python package (`groundtruth-kb`) organized into
three functional layers plus an embedded bridge runtime.  All layers ship
together and are installed from a single wheel.

---

## Architecture Layers

### Layer 1 — Core Knowledge Database

The foundation: an append-only SQLite database with governance gates and
an assertion engine.

| Capability | CLI commands |
|------------|-------------|
| Knowledge database | `gt init` — create project config and database |
| Seed data | `gt seed` — populate governance specs and optional examples |
| Assertions | `gt assert` — run machine-checkable spec assertions |
| Web dashboard | `gt serve` — optional FastAPI UI (`[web]` extra) |
| Summary | `gt summary` — quick project overview |
| Desktop bootstrap | `gt bootstrap-desktop` — same-day prototype scaffold |

### Layer 2 — Project Scaffold

Project initialization, profile-based setup, and scaffold maintenance.

| Capability | CLI commands |
|------------|-------------|
| Project scaffold | `gt project init` — generate or retrofit a repo with rules, hooks, bridge files, and report templates |
| Profiles | `gt project init --profile <profile>` — pre-built configurations (`local-only`, `dual-agent-webapp`, `staging-minimal`) |
| Scaffold upgrade | `gt project upgrade` — update project-owned scaffold files when the package version changes |

### Layer 3 — Workstation Doctor

Environment verification and readiness reporting.

| Capability | CLI commands |
|------------|-------------|
| Doctor | `gt project doctor` — detect installed tools, verify config, produce readiness reports |

### Bridge Runtime

Included as the `groundtruth_kb.bridge` module.  Provides the
Prime Builder / Loyal Opposition coordination channel:

- Message store and thread tracking
- Synchronous dialog semantics with non-blocking persistent retry
- Resident worker lifecycle
- Bridge CLI (`gt bridge` subcommands)

---

## Package Contents

| Component | Location |
|-----------|----------|
| KB engine, CLI, web UI, gates | `groundtruth_kb/` |
| Bridge runtime | `groundtruth_kb/bridge/` |
| Project scaffold commands | `gt project init`, `gt project doctor`, `gt project upgrade` |
| Method documentation | `docs/method/` (11 numbered docs) |
| Reference templates | `templates/` (CLAUDE.md, MEMORY.md, hooks, rules, CI/CD) |
| Built-in governance gates | ADRDCLAssertionGate, OwnerApprovalGate |

---

## Scope Boundary

`groundtruth-kb` initializes a knowledge database, provides the tools to
manage specifications, tests, work items, and assertions, scaffolds
project structure from profiles, and verifies workstation readiness.

It does not provision cloud infrastructure, create external accounts,
or deploy applications.  Production infrastructure setup is the
responsibility of the downstream project.

---

## Reference Implementation

Agent Red Customer Experience is the proving ground for the patterns
that `groundtruth-kb` packages.  The project scaffold extracts
simplified, reusable versions of:

- Message schema and bridge coordination model
- Worker lifecycle pattern (resident workers, notification-driven wake)
- Session hook and rule file conventions
- Operational expectations (responsiveness, audit, reporting)

---

## Current Status

| Component | Version | Status |
|-----------|---------|--------|
| groundtruth-kb | 0.1.2 | Alpha — extracted from production system (2,000+ specs, 11,000+ tests) |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
