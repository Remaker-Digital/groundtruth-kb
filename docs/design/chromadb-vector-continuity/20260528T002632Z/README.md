# ChromaDB Vector Continuity — Design Document Tree

**Bridge thread:** `gtkb-chromadb-vector-continuity-v1-cut-scoping`
**Work item:** WI-3395
**Investigation run:** 20260528T002632Z
**Date:** 2026-05-28 UTC
**Author:** Prime Builder (Claude Code, harness B)

## Overview

This directory contains the five design-contract artifacts produced under bridge thread `gtkb-chromadb-vector-continuity-v1-cut-scoping` REVISED-5 GO at -006. The artifacts collectively scope ChromaDB semantic-search continuity across the proposed v1.0 identifier-reset cut described in `memory/v1-release-strategy-deliberation-S347.md`.

This is a **governance review** deliverable per `bridge_kind: governance_review`. No production code is created; no live ChromaDB or MemBase substrate is mutated. The design is a candidate requirement set pending owner-approved spec intake per `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`.

## Document Tree

| File | Purpose |
|---|---|
| [README.md](README.md) | This file — overview and reading order. |
| [current-state-analysis.md](current-state-analysis.md) | Read-only inspection of the live ChromaDB substrate, MemBase deliberations table, query API surface, and citation footprint. Quantifies what exists today. |
| [gap-analysis.md](gap-analysis.md) | Concrete failure modes of an identifier-reset cut without vector backfill. Quantifies what would break. |
| [design-contract.md](design-contract.md) | The HIST-DELIB-NNNN backfill design — identifier convention, script contract, search-API behavior, rollback story, verification approach, candidate requirements. |
| [risk-and-blast-radius.md](risk-and-blast-radius.md) | Seven enumerated risks with mitigations and aggregate severity assessment. |
| [recommended-followon.md](recommended-followon.md) | Owner decisions needed before implementation, follow-on bridge-thread structure, candidate-requirement wording, and explicit "not recommended" paths. |

## Reading Order

Recommended for review:
1. **current-state-analysis.md** — grounds the discussion in real substrate measurements (20,224 ChromaDB chunks; 2,622 DELIB IDs; ~18,631 citations across the codebase).
2. **gap-analysis.md** — concrete failure modes and the architectural tension between text-translation manifest (S347 §8.4 Option A) and vector retrieval.
3. **design-contract.md** — the proposed solution shape: HIST- prefix convention, backfill script contract, search-API modes.
4. **risk-and-blast-radius.md** — seven risks with mitigations; aggregate severity P2-manageable.
5. **recommended-followon.md** — owner decisions, follow-on bridge threads, candidate-requirement wording.

## What This Design Is

- A grounded gap analysis (not abstract speculation).
- A concrete design contract for a one-time backfill operation.
- An enumeration of risks and mitigations.
- A roadmap of owner decisions and follow-on bridge threads.

## What This Design Is NOT

- An owner-approved formal specification (it's candidate-only).
- An implementation. No code is created by this slice.
- A v1.0 cut commitment. The scoping is conditional on the broader S347 v1.0 strategy.
- A substrate-agnostic abstraction. The design is ChromaDB-specific by deliberate scoping choice.

## Provenance

- **Originating signal:** Finding 3 of `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-27-08-52-V1-RELEASE-STRATEGY-REVIEW.md`.
- **Originating evaluation:** Prime Builder evaluation of the LO report during the 2026-05-27 session, accepting Finding 3 as the LO report's one genuinely novel substantive contribution.
- **Originating owner direction:** 2026-05-27 — "advance Finding 3 to a bridge proposal."
- **Bridge thread chain:** `bridge/gtkb-chromadb-vector-continuity-v1-cut-scoping-001.md` (NEW) → `-002.md` (NO-GO) → `-003.md` (REVISED) → `-004.md` (GO) → `-005.md` (REVISED — wording fix) → `-006.md` (GO) → `-007.md` (post-implementation report; in progress at this artifact set's authoring time).
- **MemBase WI:** `WI-3395` (standalone backlog candidate; PROJECT-V1-RELEASE-STRATEGY-PREP creation deferred to owner decision Q3 in `recommended-followon.md`).

## Audit Trail

This directory is tracked in git under `docs/design/chromadb-vector-continuity/`. Any future revision should add a new timestamped subdirectory (`docs/design/chromadb-vector-continuity/<UTC-timestamp>/`) rather than mutating these files in place. Append-only design-document discipline mirrors the MemBase append-only convention.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
