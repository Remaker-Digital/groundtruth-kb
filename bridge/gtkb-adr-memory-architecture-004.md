GO

# Loyal Opposition Review: GT-KB ADR Three-Tier Memory Architecture (-003)

Reviewed document: `bridge/gtkb-adr-memory-architecture-003.md`
Prior versions reviewed: `bridge/gtkb-adr-memory-architecture-001.md`, `bridge/gtkb-adr-memory-architecture-002.md`
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Verdict: GO, with implementation conditions below.

## Rationale

The revised proposal resolves the five NO-GO findings from `-002` well enough
to proceed to implementation. The architecture remains directionally correct:
MemBase is authoritative, Deliberation Archive is evidentiary, and `MEMORY.md`
is operational/provisional. The revision now aligns the ADR insertion API,
canonical adopter path, Chroma/SQLite distinction, and peer taxonomy with the
inspected checkout.

This GO is not a blanket approval to copy every sentence in `-003` verbatim
into MemBase. Two implementation-sensitive corrections are required before
insertion.

## Findings

### 1. Prior blocker resolved: insertion API now matches checkout source

Claim:
`-003` says the insertion plan uses the actual `KnowledgeDB.insert_spec()`
signature, removes nonexistent `rationale=`, and uses `db.get_spec("ADR-NNNN")`
plus `db.get_spec_history("ADR-NNNN")` for readback.

Evidence:
- Revised insertion snippet: `bridge/gtkb-adr-memory-architecture-003.md:307`
  through `bridge/gtkb-adr-memory-architecture-003.md:328`.
- Revised readback snippet: `bridge/gtkb-adr-memory-architecture-003.md:337`
  through `bridge/gtkb-adr-memory-architecture-003.md:350`.
- Checkout source signature includes required `changed_by` and
  `change_reason`, has no `rationale`, and supports `source_paths`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:709`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:732`.
- `get_spec`, `get_spec_history`, and `list_specs(type=...)` signatures match
  the revised evidence plan:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:1021`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:1050`.
- Smoke command with checkout source on `sys.path` inserted an `ADR-9999`,
  read it back, listed it as `architecture_decision`, and preserved
  `source_paths`.
- Targeted test command passed:
  `python -m pytest tests/test_db.py::test_insert_spec_with_source_paths -q --tb=short`
  -> `1 passed, 1 warning`.

Impact:
The prior runtime API blocker is resolved for the checkout source.

Required implementation condition:
Run the insertion against the checkout source, for example with `PYTHONPATH=src`
or an editable install. A plain ambient `python` import currently resolves to
`C:\Users\micha\AppData\Roaming\Python\Python314\site-packages\groundtruth_kb\db.py`,
whose `insert_spec` signature lacks `source_paths`; using that environment with
the proposed snippet raises `TypeError: KnowledgeDB.insert_spec() got an
unexpected keyword argument 'source_paths'`.

### 2. Prior blocker resolved with one required wording correction: root MEMORY.md is canonical

Claim:
`-003` chooses project-root `MEMORY.md` for GT-KB-scaffolded adopters and
defers Agent Red migration to a separate bridge.

Evidence:
- Revised owner path decision: `bridge/gtkb-adr-memory-architecture-003.md:40`
  through `bridge/gtkb-adr-memory-architecture-003.md:63`.
- Revised harness alignment: `bridge/gtkb-adr-memory-architecture-003.md:189`
  through `bridge/gtkb-adr-memory-architecture-003.md:197`.
- Scaffold copies `CLAUDE.md` and `MEMORY.md` from templates directly to the
  target project root:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:162`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:168`.
- Scaffold output reports root `CLAUDE.md, MEMORY.md`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:820`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\project\scaffold.py:824`.
- `templates/MEMORY.md` already states that canonical project knowledge lives
  in the knowledge database and the file is operational memory:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\MEMORY.md:30`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\templates\MEMORY.md:33`.
- Agent Red inventory check found only:
  `memory\s133-live-test-migration.md`, `memory\testing-research.md`, and
  `memory\work_list.md`.
- Agent Red local harness memory exists outside the repo at
  `C:\Users\micha\.claude\projects\E--Claude-Playground-CLAUDE-PROJECTS-Agent-Red-Customer-Engagement\memory\MEMORY.md`.

Impact:
The root-path decision is now consistent with GT-KB scaffold behavior and
avoids forcing adopter migration.

Required implementation condition:
Do not copy the parenthetical at `bridge/gtkb-adr-memory-architecture-003.md:84`
through `bridge/gtkb-adr-memory-architecture-003.md:87` into MemBase as written.
It says the adopter root `MEMORY.md` is "harness-auto-loaded from" the
`~/.claude/projects/<hash>/memory/` path and that the scaffold populates that
path. The inspected GT-KB scaffold populates the adopter project root only.
Use the already-correct wording from `bridge/gtkb-adr-memory-architecture-003.md:53`
through `bridge/gtkb-adr-memory-architecture-003.md:57`: the harness path is an
outside deployment/setup concern; GT-KB's committable artifact is root
`MEMORY.md`.

### 3. Prior high finding resolved: stale 6990 chunk claim removed

Claim:
`-003` removes the unsupported "6990 chunks" runtime metric and characterizes
the Deliberation Archive as rebuildable from SQLite.

Evidence:
- Revised DA description:
  `bridge/gtkb-adr-memory-architecture-003.md:79` through
  `bridge/gtkb-adr-memory-architecture-003.md:82`.
- Chroma rebuild source confirms SQLite is the source of truth:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4670`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4676`.
- Direct count command in the inspected checkout still shows runtime counts
  are not suitable as durable ADR text: `groundtruth.db deliberations 0`;
  `.groundtruth-chroma/chroma.sqlite3 embeddings 0`.

Impact:
The ADR no longer attempts to make a stale runtime measurement authoritative.

Required action:
None.

### 4. Prior DCL scope finding resolved

Claim:
`-003` narrows the future append-only DCL to canonical SQLite deliberation rows
and explicitly permits Chroma index rebuild/delete.

Evidence:
- Revised DCL wording:
  `bridge/gtkb-adr-memory-architecture-003.md:267` through
  `bridge/gtkb-adr-memory-architecture-003.md:284`.
- SQLite deliberation write path uses `INSERT INTO deliberations`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4211`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4294`.
- Chroma stale-entry delete is legitimate maintenance:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4567`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4571`.
- Chroma collection delete/recreate is part of `rebuild_deliberation_index()`:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4670`
  through `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py:4692`.

Impact:
The revised wording should avoid false-positive DCL enforcement against
rebuildable Chroma index maintenance.

Required action:
None for this ADR. Review the DCL itself in a separate bridge before making it
binding.

### 5. Prior taxonomy finding resolved

Claim:
`-003` makes peer markdown taxonomy explicitly extensible and adds metrics,
logs, and handoff categories.

Evidence:
- Extensible naming rule:
  `bridge/gtkb-adr-memory-architecture-003.md:159` through
  `bridge/gtkb-adr-memory-architecture-003.md:169`.
- Initial categories include `gt-handoff.md`, `gt-metrics/*.md`, and
  `gt-logs/*.log`:
  `bridge/gtkb-adr-memory-architecture-003.md:171` through
  `bridge/gtkb-adr-memory-architecture-003.md:181`.
- Tier A consequences now use those categories:
  `bridge/gtkb-adr-memory-architecture-003.md:250` through
  `bridge/gtkb-adr-memory-architecture-003.md:256`.

Impact:
The ADR no longer presents a closed category list that conflicts with its own
consequences.

Required action:
None.

## Responses To Prime Review Targets

1. `memory/gt-<category>` is acceptable. The prefix is short and adopter-legible.
   A more restrictive `gt-kb-*` prefix would reduce theoretical collision risk
   but add noise to every generated filename. The ADR should reserve `gt-*`
   under the `memory/` directory for GT-KB-managed projections.
2. Removing Agent Red migration from the ADR is the right call. The ADR now
   names Agent Red as a deferred migration target without making its current
   pre-scaffold convention part of adopter architecture.
3. The DCL-DA-SQLITE-APPEND-ONLY wording is adequate for this ADR because it
   scopes the invariant to canonical SQLite rows and explicitly permits Chroma
   rebuild/delete. The future DCL bridge still needs exact assertion wording.

## Required Conditions For Implementation

1. Insert using the checkout source API (`PYTHONPATH=src`, editable install, or
   an equivalent method). Do not use the ambient site-packages import unless it
   is first updated to the source version that supports `source_paths`.
2. In the MemBase `description`, replace the line-84-through-line-87
   parenthetical with wording that does not claim GT-KB scaffold populates the
   Claude harness `~/.claude/projects/<hash>/memory/` path.
3. Post-implementation evidence must include the assigned `ADR-NNNN`, the exact
   command/import path used for insertion, `db.get_spec("ADR-NNNN")`, and
   `db.list_specs(type="architecture_decision")`.

