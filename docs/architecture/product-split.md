# GroundTruth Product Architecture

## Overview

GroundTruth is a single Python package (`groundtruth-kb`) organized into three
functional layers plus file-bridge automation guidance for dual-agent projects.
All layers ship together and are installed from a single wheel.

---

## Architecture Layers

### Layer 1 - Core Knowledge Database (MemBase)

The foundation: an append-only SQLite database with governance gates and an
assertion engine.

| Capability | CLI commands |
|------------|--------------|
| MemBase (knowledge database) | `gt init` - create project config and database |
| Seed data | `gt seed` - populate governance specs and optional examples |
| Assertions | `gt assert` - run machine-checkable spec assertions |
| Web dashboard | `gt serve` - optional FastAPI UI (`[web]` extra) |
| Summary | `gt summary` - quick project overview |
| Desktop bootstrap | `gt bootstrap-desktop` - same-day prototype scaffold |

Layer 1 is what ADR-0001: Three-Tier Memory Architecture calls MemBase — the canonical knowledge and specifications tier.

### Layer 2 - Project Scaffold

Project initialization, profile-based setup, and scaffold maintenance.

| Capability | CLI commands |
|------------|--------------|
| Project scaffold | `gt project init` - generate or retrofit a repo with rules, hooks, bridge inventory, and report templates |
| Profiles | `gt project init my-project --profile <profile>` - pre-built configurations (`local-only`, `dual-agent`, `dual-agent-webapp`) |
| Scaffold upgrade | `gt project upgrade` - update managed scaffold files when the package version changes |

### Layer 3 - Workstation Doctor

Environment verification and readiness reporting.

| Capability | CLI commands |
|------------|--------------|
| Doctor | `gt project doctor` - detect installed tools, verify config, produce readiness reports |

### File Bridge Automation

Dual-agent projects use a project-owned file bridge:

- `bridge/INDEX.md` is the authoritative review queue.
- Bridge documents under `bridge/` hold implementation reports, reviews, and
  verdicts.
- Prime Builder writes `NEW` and `REVISED`.
- Loyal Opposition writes `GO`, `NO-GO`, and terminal `VERIFIED`.
- OS-level pollers run the Prime and Loyal Opposition scans independently of
  active chat sessions.
- `BRIDGE-INVENTORY.md` captures scheduler names, scripts, prompts, CLI
  commands, plugins, MCP servers, skills, logs, locks, and recovery procedure.
- `bridge-os-poller-setup-prompt.md` provides a reusable setup prompt for
  Claude Code or Codex.

The older SQLite/MCP bridge runtime remains in the package only as legacy
compatibility code. New projects should not use it as the active bridge.

---

## Package Contents

| Component | Location |
|-----------|----------|
| KB engine, CLI, web UI, gates | `groundtruth_kb/` |
| Legacy SQLite/MCP bridge runtime | `groundtruth_kb/bridge/` |
| Project scaffold commands | `gt project init`, `gt project doctor`, `gt project upgrade` |
| Method documentation | `docs/method/` |
| File bridge setup docs | `docs/method/12-file-bridge-automation.md` |
| Reference templates | `templates/` (CLAUDE.md, AGENTS.md, MEMORY.md, bridge inventory, setup prompt, hooks, rules, CI/CD) |
| Built-in governance gates | ADRDCLAssertionGate, OwnerApprovalGate |

---

## Scope Boundary

`groundtruth-kb` initializes MemBase, provides the tools to manage
specifications, tests, work items, and assertions, scaffolds project structure
from profiles, and verifies workstation readiness.

It does not provision cloud infrastructure, create external accounts, install
OS scheduled tasks, or deploy applications. Production infrastructure and
project-specific bridge poller setup are the responsibility of the downstream
project, using the package templates and setup prompt.

---

## Reference Implementation

The patterns packaged by `groundtruth-kb` were developed and validated in a
production commercial SaaS project. The current reusable dual-agent pattern is:

- File bridge queue and status protocol
- OS-level scheduled pollers
- Prompt and agent-configuration capture
- Session hook and rule file conventions
- Operational expectations for evidence, auditability, and owner burden

---

## Current Status

| Component | Version | Status |
|-----------|---------|--------|
| groundtruth-kb | 0.6.0 | Alpha / developer-preview — extracted from production system (2,000+ specs, 11,000+ tests) |

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
