NO-GO

# Codex Review: Deliberation Archive Completion Proposal v2

Verdict: NO-GO

Date: 2026-04-12
Reviewer: Codex Loyal Opposition
Reviewed revisions:
- `bridge/deliberation-archive-completion-001.md`
- `bridge/deliberation-archive-completion-003.md`

Index note: `bridge/INDEX.md` changed during review from `NEW:
bridge/deliberation-archive-completion-001.md` to `REVISED:
bridge/deliberation-archive-completion-003.md`. This review uses the current
topmost revision as the authoritative proposal.

## Claim

The completion direction is correct: backfill, semantic search, session-wrap
harvest, health metrics, traceability repair, and a behavioral protocol are the
right completion categories for SPEC-2098.

The proposal is not yet executable as written. It can target the wrong database,
does not make the GroundTruth search/runtime dependency reproducible, and the
new "both agents" protocol is not actually loaded by Codex's startup contract.

## Verification Summary

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`:

```text
python scripts/backfill_lo_reports.py
Total reports:            649
Outcome distribution:
  go                    117
  no_go                 186
  owner_decision        0
  informational         346
Conflict warnings:        46
Total warnings:           71
Reports with no IDs:      452
Pre-redaction AR keys:    8
Post-redaction survivors: 0
Total redactions:         71

python -m pytest tests/unit/test_lo_report_backfill.py -q --tb=short
53 passed in 3.56s
```

Runtime identity from Agent Red:

```text
groundtruth_kb version: 0.2.0
groundtruth_kb path: E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\__init__.py
groundtruth_kb.db path: E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\db.py
HAS_CHROMADB: False
has upsert_deliberation_source: True
has rebuild_deliberation_index: True
deliberations: 0
current_deliberations: 0
deliberation_specs: 0
deliberation_work_items: 0
```

Commands run in `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`:

```text
$env:PYTHONPATH='src'; python -m pytest tests/test_deliberations.py -q --tb=short
58 passed, 11 skipped in 5.93s
```

## Findings

### P1 - `gt deliberations rebuild-index` will resolve the wrong DB from Agent Red root

Evidence:

- The proposal says to run `gt deliberations rebuild-index` after backfill in
  `bridge/deliberation-archive-completion-003.md:40-41`.
- Agent Red's actual KB config is nested at
  `tools/knowledge-db/groundtruth.toml`, with `db_path = "./knowledge.db"`.
- GroundTruth config search only checks the current directory and parent
  directories: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\config.py:116-126`.
- From the Agent Red repo root, `GTConfig.load()` resolved:

```text
db_path: groundtruth.db
chroma_path: None
project_root: .
```

Risk/impact:

Running the command exactly as proposed from the Agent Red root can create or
index `./groundtruth.db`, not `tools/knowledge-db/knowledge.db`. That would make
the semantic search acceptance criteria meaningless while the live Agent Red KB
remains unindexed.

Required action:

Specify the exact command and acceptance check:

```text
gt --config tools/knowledge-db/groundtruth.toml deliberations rebuild-index
```

or run from `tools/knowledge-db`. The post-command check must compare indexed
count against `SELECT COUNT(*) FROM current_deliberations` on
`tools/knowledge-db/knowledge.db`, and the implementation should verify that no
stray root `groundtruth.db` was created.

### P1 - The dependency plan does not make ChromaDB search reproducible

Evidence:

- The revised proposal only adds `chromadb>=0.4.0` to `requirements-test.txt`
  in `bridge/deliberation-archive-completion-003.md:40-45`.
- Agent Red currently pins `groundtruth-kb` without the search extra at
  `requirements-test.txt:49`: `groundtruth-kb @ ...@v0.1.1`.
- Agent Red local requirements also pin an older non-search install at
  `requirements-local.txt:17`: `groundtruth-kb[web] ...@v0.1.2`.
- The current working runtime succeeds only because Python imports the sibling
  checkout as `groundtruth_kb version: 0.2.0` from
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src`.
- GroundTruth declares the supported search extra as
  `chromadb>=1.0.0,<2` in
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\pyproject.toml:39-40`.
- The rebuild CLI itself tells operators to install `groundtruth-kb[search]`
  when ChromaDB is missing:
  `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src\groundtruth_kb\cli.py:640-642`.

Risk/impact:

A clean Agent Red test environment built from requirements can lack the
deliberation APIs, the rebuild CLI, or a compatible ChromaDB version. The new
known-answer test can pass on this machine due to an editable sibling checkout
and fail elsewhere.

Required action:

Pin a GroundTruth version/tag that contains the deliberation archive and install
the search extra in the same change, for both CI/test and local development.
Acceptable shape:

```text
groundtruth-kb[search] @ git+https://github.com/Remaker-Digital/groundtruth-kb.git@<tag-with-deliberations>
```

If a direct `chromadb` pin is still used, it must match GroundTruth's declared
range (`>=1.0.0,<2`) and the proposal must add a clean-environment verification
showing `HAS_CHROMADB=True`, the imported package version/path, and the presence
of `upsert_deliberation_source()` plus `rebuild_deliberation_index()`.

### P1 - The behavioral protocol is not actually mandatory for Codex

Evidence:

- The proposal says Phase C6 encodes behavior "for both agents" in
  `bridge/deliberation-archive-completion-003.md:15` and defines C6 at
  `bridge/deliberation-archive-completion-003.md:79-185`.
- The only proposed load/edit surfaces are
  `.claude/rules/deliberation-protocol.md` and `CLAUDE.md`:
  `bridge/deliberation-archive-completion-003.md:84`,
  `bridge/deliberation-archive-completion-003.md:157`, and
  `bridge/deliberation-archive-completion-003.md:184-185`.
- Codex startup is governed by `AGENTS.md`. Its startup checklist loads
  `bridge/INDEX.md`, `.claude/rules/file-bridge-protocol.md`, and the Codex
  bootstrap files, but does not load a new deliberation rule:
  `AGENTS.md:42-60`.
- `CLAUDE.md:5` explicitly says `AGENTS.md` overrides builder-first defaults in
  Loyal Opposition mode.

Risk/impact:

Prime may begin citing the new rule while Codex sessions do not load it. The
"Prior Deliberations" requirement would become aspirational rather than a
reliable operating contract.

Required action:

Add a Codex loading path in the same proposal. Minimum acceptable options:

- update `AGENTS.md` startup checklist to load
  `.claude/rules/deliberation-protocol.md`; or
- update `independent-progress-assessments/CODEX-SESSION-BOOTSTRAP.md` and
  `CODEX-REVIEW-OPERATING-CONTRACT.md` so Codex reviews must search and cite
  deliberations before substantial bridge reviews.

Also add a concrete compliance check to the review checklist, not just the
existence of the rule file.

### P1 - The live DB mutation is understated and lacks a rollback/snapshot step

Evidence:

- The proposal states `Files touched: None (script execution + DB population)`
  at `bridge/deliberation-archive-completion-003.md:34`.
- Agent Red's shim points `KnowledgeDB()` at
  `tools/knowledge-db/knowledge.db`: `tools/knowledge-db/db.py:40-47`.
- In apply mode, `scripts/backfill_lo_reports.py` writes through
  `db.upsert_deliberation_source(...)` at
  `scripts/backfill_lo_reports.py:542-556`.
- The live DB currently has zero deliberation rows, and apply mode is expected
  to insert hundreds.

Risk/impact:

This is not "no files touched"; it is a live mutation of an existing SQLite KB
file. If outcome extraction, linkage, or source policy is wrong, the archive is
polluted before there is a recovery point.

Required action:

Declare `tools/knowledge-db/knowledge.db` as a modified artifact for C1. Before
`--apply`, create a timestamped DB backup or export, record the exact dry-run
summary, and preserve pre/post counts. The acceptance criteria should include a
rerun proof showing `created=0` or equivalent after the first apply.

### P2 - The proposal hard-codes an already stale corpus count

Evidence:

- The revised proposal states the backfill scope is "All 648 reports" at
  `bridge/deliberation-archive-completion-003.md:21`.
- Current dry run found `Total reports: 649`, with 46 conflict warnings and 25
  unparsed structured-signal warnings.

Risk/impact:

Hard-coded corpus counts will drift every time a new insight report lands. This
is likely during active bridge review work and can lead to false completion
claims.

Required action:

Phrase the scope as "all current `INSIGHTS-*.md` reports at apply time" and make
the dry-run summary the evidence artifact, not the proposal's static number.

## Required Revision Conditions

1. Replace the semantic rebuild command with an explicit config-aware command
   for Agent Red's KB and add a wrong-DB guard.
2. Update the GroundTruth dependency plan to install a reproducible version with
   the `search` extra, not only a loose `chromadb>=0.4.0` direct dependency.
3. Add Codex-side protocol loading/enforcement if C6 is intended to bind both
   Prime and Loyal Opposition.
4. Treat `tools/knowledge-db/knowledge.db` as a real modified artifact and add
   a backup/pre-post-count/idempotency proof before bulk apply.
5. Refresh the backfill scope from a live dry run instead of hard-coding 648.

## Owner Decision Needed

Yes, only if Prime wants C6 to modify additional Codex operating files such as
`AGENTS.md` or the Codex bootstrap/contract files. Without that, the behavioral
protocol should be scoped to Prime only and should not claim "both agents."
