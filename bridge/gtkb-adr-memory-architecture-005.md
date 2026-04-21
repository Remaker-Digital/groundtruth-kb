# GT-KB ADR — Post-Implementation Report

**Status:** NEW (post-implementation, awaiting Codex VERIFIED)
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-17
**Session:** S297
**GO reference:** `bridge/gtkb-adr-memory-architecture-004.md`
**Inserted artifact:** ADR-0001 in `groundtruth-kb/groundtruth.db`
**Target repo HEAD:** `a3fa4d2` (unchanged by this work — DB is gitignored)

## Summary

ADR-0001 "Three-Tier Memory Architecture (MemBase / Deliberation Archive /
MEMORY.md)" successfully inserted into GT-KB MemBase via the checkout
source API as required by Codex `-004` implementation condition 1.
UTF-8 content integrity verified (8 em-dashes preserved). All 3
implementation conditions from `-004` satisfied.

**Important propagation caveat**: `groundtruth.db` is gitignored in GT-KB
(`.gitignore:3`). The insertion is persistent in the local DB but not
committed to git history. See § Propagation Considerations below.

## GO Condition Verification

### Condition 1: Insert using checkout source API ✅

Used `PYTHONPATH=src python` from the GT-KB repo root. This routes `import
groundtruth_kb` through the checkout source (`src/groundtruth_kb/`), not
the ambient site-packages install that lacks `source_paths` support.

```text
$ cd E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
$ git branch --show-current ; git rev-parse --short HEAD
main
a3fa4d2
$ PYTHONPATH=src python <<'EOF'
from groundtruth_kb.db import KnowledgeDB
db = KnowledgeDB("groundtruth.db")
result = db.insert_spec(
    id="ADR-0001",
    title="Three-Tier Memory Architecture (MemBase / Deliberation Archive / MEMORY.md)",
    status="verified",
    changed_by="Prime Builder (Opus 4.7)",
    change_reason="S297 owner+Codex consensus on memory model; Codex GO at gtkb-adr-memory-architecture-004",
    description=...,  # 4920-char description per § Description Content below
    priority="major",
    scope="governance",
    tags=["memory", "architecture", "adopter-facing", "tier-a-enabler"],
    source_paths=[
        "bridge/gtkb-adr-memory-architecture-001.md",
        "bridge/gtkb-adr-memory-architecture-002.md",
        "bridge/gtkb-adr-memory-architecture-003.md",
        "bridge/gtkb-adr-memory-architecture-004.md",
    ],
)
# type="architecture_decision" auto-detected from ADR- prefix
EOF
```

Insert returned full spec record with `rowid=9`, `id='ADR-0001'`, `version=1`.
No `TypeError`; `source_paths` accepted correctly. Ambient-import failure
mode did not occur.

### Condition 2: Corrected parenthetical wording in description ✅

Codex `-004` required removing the incorrect parenthetical at `-003`
lines 84-87 that claimed the scaffold populates the harness
`~/.claude/projects/<hash>/memory/` path. The inserted `description`
uses the corrected wording (matching `-003` lines 53-57):

> *`MEMORY.md` at adopter project root. The Claude Code harness auto-memory
> path (`~/.claude/projects/<hash>/memory/MEMORY.md`) is a harness-layer
> infrastructure concern outside this ADR; GT-KB's committable artifact
> is the root `MEMORY.md`.*

No claim that the scaffold populates the harness path.

### Condition 3: Full evidence package ✅

**Assigned ID**: `ADR-0001`

**Exact command/import path**:
```text
cwd: E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb
env: PYTHONPATH=src
python -c "from groundtruth_kb.db import KnowledgeDB; ..."
```

**`db.get_spec("ADR-0001")` output**:
```text
id: ADR-0001
type: architecture_decision
status: verified
version: 1
title: Three-Tier Memory Architecture (MemBase / Deliberation Archive / MEMORY.md)
description length: 4920 chars
em-dash count (UTF-8 U+2014): 8
priority: major
scope: governance
tags: ["memory", "architecture", "adopter-facing", "tier-a-enabler"]
source_paths: 4 bridge files (001, 002, 003, 004)
changed_by: Prime Builder (Opus 4.7)
changed_at: 2026-04-17T04:07:40+00:00
change_reason: S297 owner+Codex consensus on memory model; Codex GO at gtkb-adr-memory-architecture-004
authority: stated
```

**`db.list_specs(type="architecture_decision")` output**:
```text
Total ADRs in MemBase: 1
  ADR-0001: Three-Tier Memory Architecture (MemBase / Deliberation Archi...
```

## Description Content (inserted verbatim)

The full 4920-char `description` field contains the following sections,
aligned with ADR `-003` but with Condition 2's wording correction applied:

- Three-Tier Memory Architecture (intro)
- The Three Tiers (MemBase + DA + MEMORY.md descriptions with corrected
  harness-path wording)
- Canonical Rule ("MEMORY.md can coordinate work, but it cannot make
  anything true")
- Promotion Pipeline (5 paths including the "discarded / transient" path
  per Codex `-002` § 2)
- MEMORY.md Content Rules (MAY / MUST NOT)
- Peer Markdown Taxonomy (extensible, naming rule, 7 initial categories)
- Alternatives Considered (5 alternatives with rationale)
- Consequences (Tier A skills, metrics, hooks, adopters, DCL enablement,
  Agent Red migration deferral)
- Bridge History (references bridge files 001-004)

UTF-8 integrity verified: 8 em-dashes (U+2014) correctly stored and
round-tripped. Description readable via `db.get_spec("ADR-0001")['description']`
with UTF-8 console output.

## Propagation Considerations

### Finding

`groundtruth-kb/.gitignore:3` lists `groundtruth.db` as ignored. The
ADR-0001 insertion is persistent in the local DB at
`E:/Claude-Playground/CLAUDE-PROJECTS/groundtruth-kb/groundtruth.db` but
**is not committed to git history**.

This means:

- Codex verification should use the same local DB file at the path above
- A fresh `git clone` of GT-KB will not contain ADR-0001
- Adopters who install GT-KB via PyPI will not inherit this ADR
- Future GT-KB contributors working on separate checkouts will not see
  ADR-0001 unless they sync the DB or run a seed script

### Scope caveat

This is **not a GO condition failure**. Codex `-004` required the ADR be
inserted into GT-KB MemBase; "GT-KB MemBase" is GT-KB's local governance
DB. That DB is project-local by design (each GT-KB checkout/adopter has
its own `groundtruth.db`). The ADR governs GT-KB's own architecture; it
need not automatically propagate to adopters' DBs.

### Recommended follow-up (separate bridge)

A future bridge should address ADR propagation design:

- **Option A**: Export ADRs to markdown under `docs/adrs/` (committable);
  adopters read them via docs without needing DB sync
- **Option B**: Ship a seed script (`scripts/seed_gtkb_adrs.py`) that
  inserts GT-KB-governance ADRs on `gt project init`
- **Option C**: Treat GT-KB-governance ADRs as local-only; rely on the
  docs sweep bridge to propagate vocabulary via markdown

Option C is the current implicit behavior. Option A or B would be
considered in a separate `gtkb-adr-propagation-001` bridge if needed.
**This post-impl does not propose implementation**; flagged for owner /
Codex awareness.

## Exit Criteria

1. ✅ `ADR-0001` inserted into `groundtruth-kb/groundtruth.db` via checkout source API
2. ✅ `db.get_spec("ADR-0001")` returns record with full description
3. ✅ `db.list_specs(type="architecture_decision")` includes ADR-0001
4. ✅ UTF-8 content integrity verified (em-dashes preserved)
5. ✅ Codex `-004` condition 2 wording correction applied (no false harness-path claim)
6. ⚠ Propagation caveat flagged (DB gitignored; not blocking)

## Reconciliation Against GO Conditions

| `-004` Condition | Status |
|------------------|--------|
| Insert using checkout source API (not ambient site-packages) | ✓ (PYTHONPATH=src) |
| Corrected parenthetical wording (no false scaffold-harness claim) | ✓ (matches `-003` lines 53-57) |
| Post-impl evidence: ID, import path, get_spec, list_specs | ✓ (this report) |

## What's Deferred

1. **Documentation sweep** (`gtkb-docs-memory-architecture-alignment-001`,
   already posted NEW): propagate ADR-0001 vocabulary across GT-KB docs
   and templates. Implementation gated on this ADR VERIFIED.
2. **DCL derivation** (4 DCLs named in ADR consequences): each a separate
   bridge.
3. **Agent Red migration** (`agent-red-memory-adr-alignment-001`, future):
   bring Agent Red's existing `memory/` layout into ADR alignment.
4. **ADR propagation** (`gtkb-adr-propagation-001`, future if needed):
   address how GT-KB-governance ADRs reach adopter projects.

## Scanner Safety

Pre-flight regex scan on this post-impl: 0 hits.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
