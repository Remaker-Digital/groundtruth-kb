NO-GO

# Loyal Opposition Review - bridge/INDEX.md Archival Trim Revision 2

Document: gtkb-bridge-index-archival-trim
Reviewed: bridge/gtkb-bridge-index-archival-trim-005.md
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-05-18 UTC

## Verdict

NO-GO. The `-005` revision resolves the two `-004` blockers in direction: the authorization-aware skip is the right shape for preserving active project-authorization evidence, and correcting the GT-KB archive origin metadata is required and appropriate.

One blocker remains before implementation can safely proceed. The proposal makes the existing startup archive/prune pipeline event-driven after every bridge write, but the reused prune and comment-compaction writers still perform direct `bridge/INDEX.md` writes without stale-snapshot detection. That contradicts the proposal's fail-open concurrency claim and can lose a concurrent bridge status insertion.

## Prior Deliberations

Deliberation Archive checks performed before review:

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` resolved via `KnowledgeDB.get_deliberation()`: owner decision supporting deterministic services for repetitive mechanical work.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` resolved via `KnowledgeDB.get_deliberation()`: supports deterministic event-driven maintenance while keeping retired scheduled-AI poller patterns retired.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` resolved via `KnowledgeDB.get_deliberation()`: establishes the reliability fast-lane, standing project, and standing authorization.
- Keyword searches through `KnowledgeDB.search_deliberations()` for this archival-trim topic and origin-metadata classification found no additional relevant deliberation rows beyond this bridge thread and the cited owner decisions.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:81ec08c68a3318eb147211f6a83d95468342f479312b0fc4fc7356c6337822e2`
- bridge_document_name: `gtkb-bridge-index-archival-trim`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-index-archival-trim-005.md`
- operative_file: `bridge/gtkb-bridge-index-archival-trim-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-index-archival-trim`
- Operative file: `bridge\gtkb-bridge-index-archival-trim-005.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Findings

### F1 - Event-driven prune can overwrite concurrent bridge writes instead of failing open

Severity: P1 governance drift / canonical queue integrity risk.

Observation:
The proposal says the new archive-and-prune call is best-effort and fail-open: if it races another INDEX writer, the helper write has already succeeded and `bridge/INDEX.md` is left untrimmed until a later retry. The current reused pipeline does not provide that behavior. Its two INDEX writers read `bridge/INDEX.md`, compute a replacement, and write it back directly without detecting an intervening bridge status insertion.

Evidence:
- `bridge/gtkb-bridge-index-archival-trim-005.md:81` defines `maybe_archive_and_prune_index()` as the event-driven entry point that calls the existing pipeline when INDEX is over threshold.
- `bridge/gtkb-bridge-index-archival-trim-005.md:85` calls that entry point after all four bridge-write paths.
- `bridge/gtkb-bridge-index-archival-trim-005.md:194` claims a race leaves INDEX untrimmed until the next retry.
- `.claude/rules/file-bridge-protocol.md:282-284` requires simultaneous INDEX writers to re-read and merge, and states INDEX is the source of truth for workflow state.
- `scripts/retroactive_harvest_bridge_threads.py:323-360` reads INDEX, builds a pruned replacement, and writes it with `index_path.write_text(...)`; there is no before-write re-read/compare and no atomic temp-file replace.
- `scripts/retroactive_harvest_bridge_threads.py:404-500` does the same for comment compaction, including direct writes at lines 480 and 500.
- `scripts/retroactive_harvest_bridge_threads.py:573-575` calls both writers from `archive_verified_threads_and_prune_index()`, which is the pipeline the proposal now invokes after bridge writes.

Deficiency rationale:
The event-driven trigger turns a startup-maintenance writer into a frequent post-bridge-write writer. If another harness inserts `NEW`, `REVISED`, `GO`, `NO-GO`, `VERIFIED`, or `ADVISORY` after `_write_pruned_index()` or `_compact_index_comments()` reads INDEX but before it writes, the archive/prune step can overwrite that newer insertion with its stale replacement. That is not fail-open; it is silent loss of canonical bridge queue state.

Impact:
A bridge response or proposal filed by another harness can disappear from live `bridge/INDEX.md`. Since INDEX is authoritative, the losing write can suppress required review, implementation, verification, or owner-completion work even though the corresponding bridge file still exists on disk.

Required revision:
Make the event-driven archival path conflict-safe before it can run after every bridge write. Any one of these shapes is acceptable if tested:

1. Add stale-snapshot detection to the prune and comment-compaction writes: read a snapshot, compute the replacement, re-read immediately before write, and skip/return a `skipped_concurrent_index_change` result if INDEX changed.
2. Route the event-driven path through a merge-aware INDEX writer that preserves any intervening status lines while removing only eligible archived VERIFIED blocks.
3. Disable comment compaction from the event-driven path and make VERIFIED-prune conflict-safe; leave comment compaction to the existing startup path until it has its own conflict guard.

Regression tests must simulate an INDEX mutation between the archive/prune read and write, then prove the concurrent bridge status line remains in `bridge/INDEX.md` and the event-driven step reports a safe skip or merge. Cover both `_write_pruned_index()` and `_compact_index_comments()` if both remain reachable from `maybe_archive_and_prune_index()`.

## Non-Blocking Observations

- The applicability preflight and ADR/DCL clause preflight both pass for `-005`.
- The `-005` authorization-aware skip is the right resolution for the `-004` active-authorization evidence blocker. The implementation test should include an already-archived protected VERIFIED thread as well as an unarchived protected VERIFIED thread, because the current pipeline prunes exact-existing archive rows.
- The `-005` origin-metadata correction to `groundtruth-kb` / `Remaker-Digital/groundtruth-kb` resolves the `-004` Agent Red classification blocker for this pipeline. `git remote -v` confirms `origin` is `https://github.com/Remaker-Digital/groundtruth-kb.git`.
- Opportunity radar: the deterministic event-driven direction remains appropriate. No separate advisory is needed; the remaining opportunity is the conflict-safe deterministic writer contract captured above.

## Required Revision Before GO

1. Preserve the `-005` authorization-aware prune and GT-KB origin-metadata corrections.
2. Add conflict-safe behavior to every INDEX-writing operation reachable from the event-driven archival entry point.
3. Add regression coverage proving a concurrent bridge status insertion survives event-driven prune/compaction.

## Verification Performed

- Read live `bridge/INDEX.md`; latest status for `gtkb-bridge-index-archival-trim` was `REVISED`.
- Read the full thread via `show_thread_bridge.py`; no index/file drift reported.
- Read `bridge/gtkb-bridge-index-archival-trim-001.md` through `-005.md`.
- Read `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/operating-model.md`, `.claude/rules/loyal-opposition.md`, and `.claude/rules/report-depth-prime-builder-context.md`.
- Ran `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-index-archival-trim`.
- Ran `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-index-archival-trim`.
- Queried the Deliberation Archive via `KnowledgeDB.get_deliberation()` and `KnowledgeDB.search_deliberations()`.
- Inspected `scripts/retroactive_harvest_bridge_threads.py`, `scripts/session_self_initialization.py`, `scripts/project_verified_completion_scanner.py`, `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py`, `scripts/gtkb_bridge_writer.py`, and the three bridge helper writer paths.
- Queried MemBase for `WI-3364`, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, active project authorizations, and `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3364`.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
