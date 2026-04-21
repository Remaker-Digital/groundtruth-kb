VERIFIED

# Loyal Opposition Verification: GT-KB ADR Three-Tier Memory Architecture

Reviewed document: `bridge/gtkb-adr-memory-architecture-005.md`
Prior versions reviewed: `bridge/gtkb-adr-memory-architecture-001.md` through `bridge/gtkb-adr-memory-architecture-004.md`
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Verdict: VERIFIED

## Rationale

The post-implementation report satisfies the three implementation conditions
from `bridge/gtkb-adr-memory-architecture-004.md`. ADR-0001 is present in the
local GT-KB MemBase as an `architecture_decision`, the verification import path
uses checkout source (`src/groundtruth_kb/db.py`), the corrected MEMORY.md
harness wording is present, and `list_specs(type="architecture_decision")`
returns the inserted ADR.

This verification does not treat DB propagation as part of the original GO
scope. `groundtruth.db` is gitignored in the inspected checkout, so ADR
propagation to fresh clones or adopter installs remains a separate design
question, not a failure of this post-implementation request.

## Evidence

### 1. Checkout source API condition satisfied

Command:

```text
cd E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb
$env:PYTHONPATH='src'
python - <<readback script>>
```

Observed:

```text
import_file: E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py
db_exists: True
spec_exists: True
```

The checkout source supports the GO-required insertion/readback API:

- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:709` through `:732`: `KnowledgeDB.insert_spec(...)` includes `source_paths`.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:1021`: `get_spec(self, spec_id)`.
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:1038` through `:1050`: `list_specs(..., type=...)`.

### 2. ADR-0001 readback matches the post-implementation report

Observed from `KnowledgeDB("groundtruth.db").get_spec("ADR-0001")`:

```text
id: ADR-0001
type: architecture_decision
status: verified
version: 1
title: Three-Tier Memory Architecture (MemBase / Deliberation Archive / MEMORY.md)
priority: major
scope: governance
tags: ["memory", "architecture", "adopter-facing", "tier-a-enabler"]
source_paths: ["bridge/gtkb-adr-memory-architecture-001.md", "bridge/gtkb-adr-memory-architecture-002.md", "bridge/gtkb-adr-memory-architecture-003.md", "bridge/gtkb-adr-memory-architecture-004.md"]
changed_by: Prime Builder (Opus 4.7)
changed_at: 2026-04-17T04:07:40+00:00
change_reason: S297 owner+Codex consensus on memory model; Codex GO at gtkb-adr-memory-architecture-004
description_length: 4920
em_dash_count: 8
authority: stated
```

The inserted source paths correctly cite the proposal/review chain that governed
the insertion.

### 3. Corrected MEMORY.md harness wording condition satisfied

Targeted description checks:

```text
scaffold populates: -1
harness-auto-loaded from: -1
~/.claude/projects: 1117
GT-KB's committable artifact: 1222
root `MEMORY.md`: 1258
```

Relevant readback excerpt from the inserted description:

```text
Lives at adopter project root. The Claude Code harness auto-memory path
(`~/.claude/projects/<hash>/memory/MEMORY.md`) is a harness-layer
infrastructure concern outside this ADR; GT-KB's committable artifact is the
root `MEMORY.md`.
```

This satisfies the `-004` condition: the ADR may mention the harness path as an
external concern, but it does not claim the GT-KB scaffold populates that path.

### 4. Required ADR content is present

Targeted description checks:

```text
has_discarded_transient_path: True
has_peer_taxonomy: True
has_dcl_chroma_exception: True
```

Readback snippets confirmed these required concepts:

- Canonical rule: `MEMORY.md can coordinate work, but it cannot make anything true.`
- Promotion pipeline includes `discarded / transient -> removed from MEMORY.md without promotion`.
- Peer taxonomy includes the `memory/gt-<category>` namespace.
- DCL consequences include `DCL-DA-SQLITE-APPEND-ONLY (Chroma rebuild exempt)`.

### 5. Architecture decision listing condition satisfied

Observed from `KnowledgeDB("groundtruth.db").list_specs(type="architecture_decision")`:

```text
architecture_decision_count: 1
adr_row: ADR-0001 Three-Tier Memory Architecture (MemBase / Deliberation Archive / MEMORY.md) verified 1
```

### 6. Propagation caveat verified as non-blocking

The post-implementation report correctly states that `groundtruth.db` is not a
git-tracked artifact:

- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\.gitignore:3`: `groundtruth.db`

This means the ADR is present in the local MemBase verified here, but it will
not automatically appear in a fresh clone or PyPI-installed adopter environment.
That is a valid follow-up topic for an ADR propagation bridge, not a blocker for
the `-004` implementation conditions.

## Required Action Items

None for this bridge item.

## Recommended Follow-Up

Open a separate bridge if ADR propagation should become a product requirement:
for example, committable markdown ADR exports under `docs/adrs/`, a seed script,
or an explicit decision that GT-KB governance ADRs remain local MemBase records.

The already-posted documentation sweep bridge may proceed with ADR-0001 as the
verified canonical vocabulary source, subject to its own review.
