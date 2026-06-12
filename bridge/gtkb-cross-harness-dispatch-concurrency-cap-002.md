NO-GO
author_identity: codex
author_harness_id: A
author_session_context_id: 2026-06-12T01-56-13Z-loyal-opposition:A-a2c824
author_model: GPT-5 Codex
author_metadata_source: bridge auto-dispatch
reviewed_document: bridge/gtkb-cross-harness-dispatch-concurrency-cap-001.md
reviewed_status: NEW
Date: 2026-06-12 UTC

# Loyal Opposition Review: Cross-Harness Dispatch Concurrency Cap

Document: gtkb-cross-harness-dispatch-concurrency-cap
Version Reviewed: 001 (NEW)
Verdict: NO-GO

## Summary

NO-GO. The root-cause claim is credible, the target paths are in-root, the mechanical applicability preflight is clean, the clause preflight reports no blocking gaps, and the proposed implementation shape is directionally sound.

The proposal still relies on `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` without citing the governing fast-lane specification, `GOV-RELIABILITY-FAST-LANE-001`, in `## Specification Links` or mapping it in the verification plan. Because the standing PAUTH is explicitly the reliability fast-lane authorization, that spec is a relevant governing specification under `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`.

No owner decision is requested in this auto-dispatch context. Prime Builder can revise the proposal by adding the missing fast-lane linkage and eligibility evidence.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this thread was `NEW`, actionable for Loyal Opposition.
- Resolved Codex harness identity from `harness-state/harness-identities.json` as harness ID `A`.
- Read roles through `groundtruth_kb.harness_projection.read_roles`; harness ID `A` is assigned `loyal-opposition`.
- Read the full bridge thread with `show_thread_bridge.py`; this thread currently has one proposal version, `-001`.
- Read the bridge protocol, Codex review gate, deliberation protocol, operating model, Loyal Opposition rule, report-depth rule, and bridge-essential rule.
- Inspected `scripts/cross_harness_bridge_trigger.py` around `_spawn_harness`, active-session TTL handling, `Popen`, and exit-code failure counting.
- Queried project authorization and project membership for `PROJECT-GTKB-RELIABILITY-FIXES`.
- Searched the Deliberation Archive for exact and related prior decisions.
- Ran the mandatory applicability and ADR/DCL clause preflights.

## Prior Deliberations

Commands run:

```text
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; .\.venv\Scripts\python.exe -m groundtruth_kb deliberations search 'dispatch concurrency cap dispatch storm live process limit WI-4472' --limit 10 --json
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; .\.venv\Scripts\python.exe -m groundtruth_kb deliberations search 'cross harness trigger active session suppression dispatch retry delay livelock global concurrency cap' --limit 8 --json
$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; .\.venv\Scripts\python.exe -m groundtruth_kb deliberations get DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION --json
```

Relevant results:

- The two searches for a prior global live-process cap decision returned `[]`.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` exists with `source_type = owner_conversation`, `outcome = owner_decision`, and content recording the owner's decision to build a standing reliability fast-lane with `PROJECT-GTKB-RELIABILITY-FIXES`, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, and `GOV-RELIABILITY-FAST-LANE-001`.
- `bridge/gtkb-work-subject-aware-testing-integration-probe-002.md` is a directly relevant review precedent: it NO-GO'd a proposal that relied on the same standing PAUTH but omitted `GOV-RELIABILITY-FAST-LANE-001` from `## Specification Links`.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-cross-harness-dispatch-concurrency-cap
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:d0e5b677c7d1aa823e58d0742c2f9cc34ba4ff69aa746db7456d81969418ba2e`
- bridge_document_name: `gtkb-cross-harness-dispatch-concurrency-cap`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-cross-harness-dispatch-concurrency-cap-001.md`
- operative_file: `bridge/gtkb-cross-harness-dispatch-concurrency-cap-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-cross-harness-dispatch-concurrency-cap
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-cross-harness-dispatch-concurrency-cap`
- Operative file: `bridge\gtkb-cross-harness-dispatch-concurrency-cap-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Positive Confirmations

- Root-boundary scope is clean: the proposal's target paths are `scripts/cross_harness_bridge_trigger.py` and `platform_tests/scripts/test_dispatch_concurrency_cap.py`, both inside `E:\GT-KB`.
- The defect claim is supported by current code: `_spawn_harness` launches via `subprocess.Popen`, returns the process PID in metadata, and relies on `<dispatch_id>.exit_code` files for later failure accounting. No existing `GTKB_MAX_LIVE_DISPATCHED_PROCESSES`, `_count_live_dispatched_processes`, or `_pid_alive` implementation is present.
- The proposed tests are relevant to the claimed defect class: count semantics, cap skip/no `Popen`, audit logging, below-cap behavior, and env parsing are the right behavioral edges.
- Live project evidence confirms `WI-4472` is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`, and `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active with mutation classes `source`, `test_addition`, and `hook_upgrade`.

## Review Findings

### Finding P1-001: Missing Governing Fast-Lane Specification

Observation: The proposal cites `Project: PROJECT-GTKB-RELIABILITY-FIXES`, `Work Item: WI-4472`, and `Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` at `bridge/gtkb-cross-harness-dispatch-concurrency-cap-001.md:17-19`. It cites the standing PAUTH again in `## Owner Decisions / Input` at `bridge/gtkb-cross-harness-dispatch-concurrency-cap-001.md:68`. Its `## Specification Links` section begins at `bridge/gtkb-cross-harness-dispatch-concurrency-cap-001.md:45` and does not cite `GOV-RELIABILITY-FAST-LANE-001`.

Evidence:

- `bridge/gtkb-cross-harness-dispatch-concurrency-cap-001.md:17-19`, `:45`, and `:68`.
- `bridge/gtkb-reliability-fast-lane-006.md:42` records that `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` created the standing fast-lane with `PROJECT-GTKB-RELIABILITY-FIXES`, `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, and `GOV-RELIABILITY-FAST-LANE-001`.
- `bridge/gtkb-reliability-fast-lane-006.md:136` confirms `GOV-RELIABILITY-FAST-LANE-001` exists as a specified governance spec.
- `bridge/gtkb-reliability-fast-lane-006.md:138` confirms `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is the active standing authorization with `owner_decision_deliberation_id = DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`.
- `bridge/gtkb-work-subject-aware-testing-integration-probe-002.md:82-92` is prior Loyal Opposition precedent requiring this same fast-lane spec citation when a proposal relies on this PAUTH.

Deficiency rationale: `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` requires an implementation proposal to cite every relevant governing specification. This proposal uses the standing reliability fast-lane PAUTH as implementation authority, so the fast-lane governance spec is not optional context; it defines the eligibility criteria and reduced approval ceremony for that PAUTH. The proposal cannot be approved until it shows that WI-4472 qualifies under that governance surface.

Impact: Prime Builder could implement a live dispatch-path change under a standing authorization without demonstrating that the work satisfies the authorization's governing eligibility constraints. That weakens the bridge review gate and makes future PAUTH misuse harder to detect.

Recommended action: Revise the proposal to add `GOV-RELIABILITY-FAST-LANE-001` to `## Specification Links`, add a short fast-lane eligibility statement, and map it in the specification-derived verification plan. The eligibility statement should cover, at minimum, that this is a defect/reliability fix, target paths consume only `source` and `test_addition` mutation classes, and no deploy, force-push, spec deletion, formal spec mutation, or unrelated cleanup is in scope.

## Required Revision Response

1. Add `GOV-RELIABILITY-FAST-LANE-001` to `## Specification Links`.
2. Add a fast-lane eligibility paragraph tied to `WI-4472`, `PROJECT-GTKB-RELIABILITY-FIXES`, and `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
3. Add a verification-plan row or acceptance criterion proving the implementation stayed within the fast-lane PAUTH scope.
4. Keep the current target scope unless Prime Builder discovers a new technical blocker during revision.

## Owner Action Required

None. This is a proposal-revision blocker, not an owner-decision blocker.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
