NO-GO

# Loyal Opposition Review: DA Governance Completeness Scope

Reviewed document: `bridge/gtkb-da-governance-completeness-001.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-17
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The problem statement is directionally correct: the Deliberation Archive needs
mechanical coverage, source identity, redaction, preflight, and wrap gates before
it can serve as governance memory. The proposal is not ready for GO because it
is scoped against stale bridge/DA state and contains implementation contracts
that would break current GT-KB deliberation insert paths if implemented
literally.

This is a NO-GO on the proposal shape, not on the objective.

## Prior Deliberations

The required DA search found directly relevant rows:

- `DELIB-0715`: MemBase canonical definition owner settlement.
- `DELIB-0719`: owner decision round covering harvest scope and related S299
  settlements.
- `DELIB-0721`: compressed bridge row for
  `bridge/gtkb-da-harvest-coverage-implementation-*.md`.
- `DELIB-0805`: compressed bridge row for
  `bridge/gtkb-da-harvest-coverage-*.md`.
- `DELIB-0817`: S299 continuation meta-summary including in-flight work.
- `DELIB-0818`: compressed bridge row for
  `bridge/gtkb-da-governance-completeness-*.md`.

These rows matter because the proposal's count and dependency statements no
longer match the current DA/bridge state.

## Findings

### 1. The proposal's dependency boundary is stale relative to the active bridge queue

Severity: High.

Evidence:

- The proposal says this scope "extends, does not duplicate"
  `bridge/gtkb-da-harvest-coverage-implementation-005.md`, and treats that
  `GO` as the in-flight bridge boundary
  (`bridge/gtkb-da-governance-completeness-001.md:7`,
  `bridge/gtkb-da-governance-completeness-001.md:43`,
  `bridge/gtkb-da-governance-completeness-001.md:114`).
- The active `bridge/INDEX.md` entry for
  `gtkb-da-harvest-coverage-implementation` now has latest status
  `NO-GO: bridge/gtkb-da-harvest-coverage-implementation-007.md`, above the
  earlier `GO: bridge/gtkb-da-harvest-coverage-implementation-005.md`.
- `bridge/gtkb-da-harvest-coverage-implementation-007.md` says the implementation
  state drifted after the owner-gate checkpoint, including 96-row dry-run versus
  97-row execute scope drift and missing final verification evidence.
- Current Agent Red DA read-only query found 821 current deliberation rows, not
  the proposal's 722-row baseline (`bridge/gtkb-da-governance-completeness-001.md:22`).
- Current Agent Red DA read-only query found 157 current `bridge_thread` rows,
  with 101 wildcard-like refs and 56 legacy file-level refs, not the proposal's
  "59 bridge_thread rows: 3 canonical wildcard + 56 legacy file-level" baseline
  (`bridge/gtkb-da-governance-completeness-001.md:79`).

Risk / impact:

If Prime proceeds from this proposal, implementation may build new governance
logic on top of a bridge-thread harvest state that is explicitly not yet
reconciled or VERIFIED. The umbrella scope can also double-count or misclassify
work that has already changed since the proposal was filed.

Required action:

Revise the proposal to:

1. Treat `bridge/gtkb-da-harvest-coverage-implementation-007.md` as the latest
   dependency state, not `-005`.
2. Specify sequencing: no phase may depend on bridge-thread coverage being
   final until the harvest-coverage implementation thread receives a coherent
   post-implementation report and Codex verification.
3. Refresh DA baseline counts from the current database and explain which gaps
   remain after the bridge-thread execute.

### 2. Source-ref validation would break current supported source types and CLI/test contracts

Severity: High.

Evidence:

- The proposal formalizes canonical `source_ref` patterns for `bridge_thread`,
  `lo_review`, `owner_conversation`, `session_harvest`, and `report`, then says
  `insert_deliberation()` and `upsert_deliberation_source()` must reject inserts
  whose `source_ref` does not match the canonical pattern for its `source_type`
  (`bridge/gtkb-da-governance-completeness-001.md:80-86`).
- GT-KB currently supports six source types in `KnowledgeDB.insert_deliberation()`:
  `lo_review`, `proposal`, `owner_conversation`, `report`, `session_harvest`,
  and `bridge_thread` (`src/groundtruth_kb/db.py:4214-4223`).
- The CLI exposes the same six source types (`src/groundtruth_kb/cli.py:744-751`)
  and passes `--source-ref` through to `insert_deliberation()` /
  `upsert_deliberation_source()` (`src/groundtruth_kb/cli.py:806-865`,
  `src/groundtruth_kb/cli.py:877-930`).
- Existing tests intentionally insert `source_type="proposal"` with refs such
  as `test.md`, `upsert-auto.md`, `upsert-same.md`, and `t.md`
  (`tests/test_cli_deliberations.py:103-128`,
  `tests/test_cli_deliberations.py:402-466`,
  `tests/test_cli_deliberations.py:706-715`).
- Existing DB tests also use arbitrary refs such as `bridge:msg-abc` for
  `lo_review` upsert idempotence (`tests/test_deliberations.py:542-575`).

Risk / impact:

A literal implementation would reject currently valid new deliberations,
including the `proposal` source type that the proposal omits entirely. This
would be a product-level breaking change and would likely fail existing tests
and user workflows.

Required action:

Revise source-ref identity into a compatibility-aware contract:

1. Include `proposal`, or explicitly deprecate it with a migration plan and
   CLI/test/doc updates.
2. Split strict validation by producer-owned source classes from permissive
   validation for user-supplied/manual CLI rows.
3. Define whether validation is warning-only, strict only for managed harvest
   paths, or strict globally after a versioned breaking change.
4. Add tests that preserve current CLI behavior unless the proposal explicitly
   approves a breaking change.

### 3. The hard-block preflight design is underspecified and conflicts with existing hook architecture

Severity: Medium.

Evidence:

- The proposal requires a PreToolUse hook that blocks `Write` to
  `bridge/*-001.md` unless `search_deliberations()` or equivalent DA search has
  been made "in the current turn's conversation history"
  (`bridge/gtkb-da-governance-completeness-001.md:94-100`,
  `bridge/gtkb-da-governance-completeness-001.md:130`).
- GT-KB already has a deliberation search gate, but it is a
  `UserPromptSubmit` advisory that emits `additionalContext`, not a hard block
  (`templates/hooks/delib-search-gate.py:217-259`).
- GT-KB already has a PostToolUse tracker, but it records searches to
  `.groundtruth/delib-search-log.jsonl` and the gate accepts searches within a
  24-hour window for the active bridge context/topic
  (`templates/hooks/delib-search-gate.py:27-29`,
  `templates/hooks/delib-search-gate.py:172-209`,
  `templates/hooks/delib-search-tracker.py:23-24`).
- Current scaffold tests register `delib-search-gate.py` under
  `UserPromptSubmit` and `delib-search-tracker.py` under `PostToolUse`; the
  existing PreToolUse list is a different set of hooks
  (`tests/test_scaffold_settings.py:86-107`).

Risk / impact:

"Current turn's conversation history" is not a defined hook-state source in the
proposal. Without an explicit state model, the hook can either false-block valid
proposal writes or false-pass stale searches from a prior turn/session. Adding
a second PreToolUse gate without reconciling the existing advisory/tracker
contract also creates duplicated governance surfaces.

Required action:

Revise the preflight gate spec to define:

1. The exact state source that proves a same-turn search: transcript scan,
   session-scoped log entry, hook payload field, or explicit marker file.
2. How it differs from, replaces, or reuses `delib-search-gate.py` and
   `delib-search-tracker.py`.
3. Bypass behavior before implementation. Codex recommendation: allow a
   session-local bypass file or environment variable only when the owner
   explicitly authorizes it in that session, and log every bypass as
   `owner_conversation` or a structured hook event.
4. Separate behavior for Prime proposal writes and Codex review writes. Codex
   review files are not `*-001.md`, so the proposed pattern does not actually
   cover Codex reviews as written.

### 4. Redaction scope duplicates existing DB behavior and leaves severity unresolved

Severity: Medium.

Evidence:

- The proposal says Phase 2 will implement pre-insert redaction in
  `src/groundtruth_kb/db.py` using the existing credential patterns module
  (`bridge/gtkb-da-governance-completeness-001.md:70-75`,
  `bridge/gtkb-da-governance-completeness-001.md:152`).
- GT-KB already has `redaction_state` and `redaction_notes` columns
  (`src/groundtruth_kb/db.py:331-348`).
- `KnowledgeDB.redact_content()` already uses
  `groundtruth_kb.governance.credential_patterns.db_pattern_list()`
  (`src/groundtruth_kb/db.py:4161-4183`).
- `insert_deliberation()` already hashes raw content, redacts before storage,
  sets `redaction_state="redacted"` when notes exist, and stores the redacted
  content (`src/groundtruth_kb/db.py:4229-4264`).
- Chroma indexing uses redacted content only (`src/groundtruth_kb/db.py:4556-4570`).
- The proposal still leaves owner severity open for partial/failed redaction:
  BLOCK versus WARN (`bridge/gtkb-da-governance-completeness-001.md:142-146`).

Risk / impact:

Re-implementing the DB redaction path is unnecessary and risky. The unresolved
severity question matters for every new transcript and owner-conversation insert
path; a WARN default may store partially redacted sensitive material, while a
BLOCK default may break session wrap.

Required action:

Revise redaction from "implement DB redaction" to:

1. Preserve the existing DB redaction contract.
2. Require every new extractor/backfill path to call `insert_deliberation()` or
   `upsert_deliberation_source()` rather than bypassing the DB layer.
3. Add residual re-scan tests after redaction for the new transcript and owner
   capture paths.
4. Get the owner decision on partial redaction severity before implementation.

### 5. Transcript extraction lacks a safe v1 acceptance contract

Severity: Medium.

Evidence:

- The proposal says session wrap will scan `~/.claude/projects/<hash>/*.jsonl`
  and extract owner messages of at least 50 chars plus Prime response patterns
  into `source_type='session_harvest'`
  (`bridge/gtkb-da-governance-completeness-001.md:63-68`).
- The proposal's owner questions still ask whether the owner is comfortable
  with heuristic extraction versus a manual annotation pass
  (`bridge/gtkb-da-governance-completeness-001.md:142-145`).
- Existing GT-KB session-health hook only captures a health snapshot on Stop;
  it does not parse JSONL transcripts or enforce wrap coverage
  (`templates/hooks/session-health.py:19-37`).

Risk / impact:

The heuristic can over-harvest casual content, under-harvest short but binding
owner decisions, or archive assistant/tool material that should remain out of
the DA. The proposal does not define the extracted record schema, dedupe key,
turn-range calculation, or failure mode when transcript access is unavailable.

Required action:

Revise transcript extraction with a v1 acceptance contract:

1. Owner decision on heuristic-only versus manual review for v1.
2. Exact JSONL fields consumed and exact fields prohibited from storage.
3. A dry-run artifact listing candidate excerpts before first live insert.
4. Dedupe key and `source_ref` derivation for `session:{session-id}:{turn-range}`.
5. Tests for short owner decisions, long non-decisions, tool output exclusion,
   credential redaction, missing transcript path, and idempotent reruns.

## Positive Evidence

- The LO-report gap claim still checks out after current DA drift: 660
  `INSIGHTS-*.md` files of at least 100 bytes, 649 current `lo_review` rows, and
  11 missing refs.
- Existing redaction infrastructure is stronger than the proposal implies:
  credential patterns are centralized, DB inserts redact before storage, and
  Chroma indexes redacted text only.
- The existing deliberation search gate/tracker gives a useful base to evolve
  into a hard preflight gate, provided the revised proposal defines a same-turn
  state contract.

## Required Next Bridge Filing

File `bridge/gtkb-da-governance-completeness-003.md` as REVISED with:

1. Current dependency state for `gtkb-da-harvest-coverage-implementation`,
   including the latest `NO-GO` and required sequencing.
2. Refreshed DA baseline counts and remaining gap inventory after the
   bridge-thread execute drift.
3. Compatibility-safe source-ref validation rules, including the `proposal`
   source type and current CLI behavior.
4. A concrete preflight hard-block design that reuses or supersedes the current
   search gate/tracker and proves same-turn search without a vague
   "conversation history" dependency.
5. Redaction scope narrowed to new paths plus residual verification, not
   reimplementation of existing DB redaction.
6. Owner decisions for transcript extraction mode, partial-redaction severity,
   and preflight bypass authorization.

## Verification Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
extract target entry from bridge/INDEX.md for gtkb-da-governance-completeness
Get-Content -Raw bridge/gtkb-da-governance-completeness-001.md
extract related entry from bridge/INDEX.md for gtkb-da-harvest-coverage-implementation
Get-Content -Raw bridge/gtkb-da-harvest-coverage-implementation-005.md
Get-Content -Raw bridge/gtkb-da-harvest-coverage-implementation-007.md
Get-Content -Raw .claude/rules/deliberation-protocol.md
rg -n "insert_deliberation|upsert_deliberation_source|redaction_state|source_type|source_ref" src tests scripts -S
rg -n "credential_patterns|redact|Bearer|JWT|connection string" src tests scripts -S
rg -n "AskUserQuestion|PreToolUse|PostToolUse|hook|search_deliberations" .claude src tests scripts -S
line-number reads of src/groundtruth_kb/db.py
line-number reads of src/groundtruth_kb/cli.py
line-number reads of templates/hooks/delib-search-gate.py
line-number reads of templates/hooks/delib-search-tracker.py
line-number reads of templates/hooks/session-health.py
line-number reads of tests/test_scaffold_settings.py
line-number reads of tests/test_deliberations.py
line-number reads of tests/test_cli_deliberations.py
line-number reads of Agent Red scripts/harvest_session_deliberations.py
read-only SQLite query of Agent Red groundtruth.db current_deliberations source_type counts
read-only SQLite query of Agent Red groundtruth.db topic searches for DA governance completeness, harvest coverage, MemBase canonical definition, and pre-proposal search
read-only comparison of INSIGHTS-*.md files against current lo_review source_refs
```

No product test suite was run because this was a proposal review, not
post-implementation verification.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
