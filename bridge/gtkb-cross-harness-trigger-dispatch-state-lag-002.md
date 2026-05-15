NO-GO

# Loyal Opposition Review - Cross-Harness Trigger Dispatch-State Refresh Lag

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-14 UTC
Reviewed proposal: `bridge/gtkb-cross-harness-trigger-dispatch-state-lag-001.md`
Verdict: NO-GO

## Claim

The proposal addresses a real bridge reliability concern, but it is not ready for implementation. The proposed fix is hypothesis-driven and does not match the current trigger state machine closely enough to be a safe implementation authorization. The verification command also targets a non-existent `tests/` tree.

## Prior Deliberations

Deliberation search was performed against `groundtruth.db` in read-only mode for `WI-3265`, `cross harness trigger`, `dispatch-state`, `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES`, and `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08`.

Relevant results:

- `DELIB-S350-BATCH3-DETERMINISTIC-SERVICES` - owner authorization for the deterministic-services batch containing WI-3265.
- `DELIB-1496` - prior NO-GO on cross-harness trigger Codex exec hook firing.
- `DELIB-1497`, `DELIB-1498`, `DELIB-1499` - prior Windows rename race and liveness diagnostics thread.
- `DELIB-1532`, `DELIB-1535` - prior active-session suppression verification/review context.

The proposal cites the batch authorization and Codex hook retest, but it does not incorporate the current trigger state-machine history that directly constrains this change.

## Applicability Preflight

- packet_hash: `sha256:2f50e527c1378bd10dd5052bb3b851d40ae2b9b4b3e15807d4b6e931bb40a7cd`
- bridge_document_name: `gtkb-cross-harness-trigger-dispatch-state-lag`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-cross-harness-trigger-dispatch-state-lag-001.md`
- operative_file: `bridge/gtkb-cross-harness-trigger-dispatch-state-lag-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-cross-harness-trigger-dispatch-state-lag`
- Operative file: `bridge\gtkb-cross-harness-trigger-dispatch-state-lag-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory default invocation. Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Findings

### F1 - P1 - The proposed fix is not derived from the current trigger state machine

Observation: The proposal claims the Stop pass may read a cached or pre-Write `bridge/INDEX.md` copy and proposes a Stop-branch re-read plus a 200 ms mtime-stabilization loop (`-001.md:22`, `-001.md:75`, `-001.md:77`). The live trigger already reads `bridge/INDEX.md` from disk once per `run_trigger()` invocation before computing actionable work (`scripts/cross_harness_bridge_trigger.py:295`, `scripts/cross_harness_bridge_trigger.py:935`, `scripts/cross_harness_bridge_trigger.py:936`). It then writes dispatch state after the recipient state has been recomputed (`scripts/cross_harness_bridge_trigger.py:1089`).

Deficiency rationale: The current code has an explicit active-session suppression model: when the counterpart is active, it records `last_suppressed_signature` and intentionally does not advance `last_dispatched_signature` (`scripts/cross_harness_bridge_trigger.py:1001`, `scripts/cross_harness_bridge_trigger.py:1048`, `scripts/cross_harness_bridge_trigger.py:1075`). The proposal does not distinguish stale state from suppressed/retryable state, selected-batch signature state, or a real missed Stop invocation. A post-Write re-read and mtime wait can add hook latency while still failing to address the actual failure mode if the lag is caused by suppression, dispatch target resolution, selected-batch state, or a missing child-hook reconciliation.

Recommended action: Revise into either a diagnostic-only proposal or a fix proposal with an evidence-backed root cause. The revised packet should include before/after examples of the relevant `dispatch-state.json` fields, define which state transition is wrong, and map tests to that transition. If the defect is truly an INDEX freshness issue, add a failing test that proves the current `_read_index_live()` path observes stale content despite the current direct file read.

### F2 - P1 - The verification command targets a non-existent test tree

Observation: The proposal authorizes `tests/scripts/test_cross_harness_bridge_trigger.py` and tells Prime to run `python -m pytest tests/scripts/test_cross_harness_bridge_trigger.py -v` (`-001.md:16`, `-001.md:94`). This checkout has no `tests/` directory; the root pytest configuration points at `platform_tests` and `applications/Agent_Red/tests` (`pyproject.toml:9`). The existing trigger tests are under `platform_tests/scripts/`.

Deficiency rationale: A GO verdict would authorize implementation against a verification plan that cannot run as written. That breaks the mandatory specification-derived verification gate because the proposed command is not an executable acceptance check in this repo.

Recommended action: Replace all `tests/scripts/...` target paths and commands with the actual `platform_tests/scripts/...` paths, or explicitly create a new in-root test package and update pytest configuration in scope. For this proposal, the minimal fix is to use the existing `platform_tests/scripts/test_cross_harness_bridge_trigger.py` and any new targeted files under `platform_tests/scripts/`.

### F3 - P2 - Prior trigger governance and dispatch history are under-cited

Observation: Deliberation search surfaced multiple prior cross-harness trigger reviews and verifications, including the Codex exec hook-firing NO-GO, Windows rename race/liveness diagnostics, and active-session suppression. The proposal's Prior Deliberations section cites only batch authorization plus the S337 Codex hooks retest (`-001.md:41`).

Deficiency rationale: This proposal changes the same active trigger surface. Missing the recent trigger-specific history increases the risk of reintroducing already-reviewed misconceptions, especially around active-session suppression and dispatch-state semantics.

Recommended action: Carry forward the relevant prior bridge threads or DELIB IDs in the revised proposal, and explicitly state how the new defect differs from the verified rename-race and active-session-suppression behavior.

## Required Revision

Submit a REVISED proposal that:

1. Separates diagnostic evidence from implementation, or proves the implementation root cause with a failing test.
2. Uses the actual `platform_tests/` test paths and executable commands.
3. Incorporates prior cross-harness trigger deliberations and bridge threads.
4. States whether the observed lag is a stale-INDEX read, active-session suppression, selected-batch signature behavior, or missed child-session reconciliation.

Decision needed from owner: None.

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-trigger-dispatch-state-lag` - pass; missing required specs: none.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-trigger-dispatch-state-lag` - pass; blocking gaps: 0.
- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-cross-harness-trigger-dispatch-state-lag --format json` - no drift.
- Read-only SQLite deliberation searches over `groundtruth.db` for WI-3265 and cross-harness trigger terms.
- Source/config inspection of `scripts/cross_harness_bridge_trigger.py`, `.codex/hooks.json`, `.claude/settings.json`, `pyproject.toml`, and existing trigger tests.

File bridge scan contribution: 1 selected entry processed.
