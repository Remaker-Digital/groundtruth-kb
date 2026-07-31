GO

# Loyal Opposition Verdict — GO — gtkb-wi5007-prime-unchanged-pending-residue

bridge_kind: prime_proposal
Document: gtkb-wi5007-prime-unchanged-pending-residue
Version: 002
Date: 2026-07-04T07:26:20Z
author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-04T07-26-13Z-loyal-opposition-D-a42957
author_model: deepseek-v4-pro:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route deepseek-v4-pro-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

## Applicability Preflight

- packet_hash: sha256:09b429fa52e5505fa076307e6f22b324bb61cf614faaf96192c3d5e2a2d7aa95
- bridge_document_name: gtkb-wi5007-prime-unchanged-pending-residue
- content_source: bridge_file_operative
- content_file: bridge/gtkb-wi5007-prime-unchanged-pending-residue-001.md
- operative_file: bridge/gtkb-wi5007-prime-unchanged-pending-residue-001.md
- preflight_passed: true
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | advisory | no | content:deliberation |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | advisory | no | content:candidate, content:verified, content:retired |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | blocking | yes | doc:*, content:Specification Links |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | blocking | yes | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | advisory | no | content:owner decision, content:requirement, content:specification, content:DCL, content:work item |
| GOV-FILE-BRIDGE-AUTHORITY-001 | blocking | yes | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: gtkb-wi5007-prime-unchanged-pending-residue
- Operative file: bridge\gtkb-wi5007-prime-unchanged-pending-residue-001.md
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | must_apply | yes | blocking | blocking |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL | GOV-FILE-BRIDGE-AUTHORITY-001 | must_apply | yes | blocking | blocking |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | must_apply | yes | blocking | blocking |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | must_apply | yes | blocking | blocking |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | GOV-STANDING-BACKLOG-001 | may_apply | — | blocking | blocking |

## Defect Confirmation

Code inspection confirms the residue pattern in both live paths:

**dispatcher_runtime.py line 5325**: `recipient_state["pending_count"] = len(dispatched_filtered)` is set unconditionally before the unchanged check at line 5386. When `prior_dispatched == dispatched_signature` and `previous_launch_failure is None`, the branch sets `last_result = "unchanged"` but never clears `pending_count`. The `pending_count` from line 5325 persists as residue.

**gtkb_dispatcher_daemon.py line 1010**: `recipient_state["pending_count"] = len(selected)` is set inside the unchanged branch alongside `last_result = "unchanged"` and `selected_count = 0`. The `pending_count` is set to the length of the selected items even though zero items are dispatched.

**Health impact**: The `_runtime_classification_for_recipient` function in `bridge_dispatch_config.py` computes `has_pending_work = pending_count > 0 or selected_count > 0`. When `pending_count > 0` with `last_result = "unchanged"`, the health system sees pending work with no live inflight worker and no dispatchable changed work — a false-positive WARN that can make normal PB NO-GO/GO queue recovery look stuck.

## Proposed Fix Assessment

The proposed scope is minimal and targeted:

1. **dispatcher_runtime.py**: In the unchanged branch (line ~5386), add `recipient_state["pending_count"] = 0` and `recipient_state["selected_count"] = 0` to clear the residue set at line 5325.
2. **gtkb_dispatcher_daemon.py**: In the unchanged branch (line ~1010), change `recipient_state["pending_count"] = len(selected)` to `recipient_state["pending_count"] = 0`.
3. Normal dispatch of genuinely new or changed PB candidates is preserved — the unchanged branch is only entered when the signature matches the prior dispatched signature.
4. Regression tests in both `test_dispatcher_runtime.py` and `test_gtkb_dispatcher_daemon.py` to assert `pending_count == 0` after an unchanged cycle.

The fix is consistent with the existing `terminal_bridge_reconciled` pattern at dispatcher_runtime.py line 2877, which already clears `pending_count = 0` when reconciling terminal bridge residue.

## Requirement Sufficiency

Existing requirements are sufficient. The owner-directed headless dispatch stability goal (DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL) and the WI-5007 project authorization narrow the scope to this reproducible dispatcher health/runtime defect. No new specs are required.

## Specification Links Assessment

All blocking specs are cited with concrete evidence. Three advisory specs (ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001) are not explicitly cited but their concerns are addressed through the proposal's structure (deliberation references, artifact lifecycle handling, owner decision and requirement sections). Advisory spec absence is not a rejection criterion per the harness instructions.

## Prior Deliberations

- DELIB-20260703-HEADLESS-DISPATCH-STABILITY-GOAL — Owner-directed operating goal for stable headless dispatch with Codex as PB and Claude/Ollama/Antigravity as LO targets; also used as the owner-decision anchor for the WI-5007 project authorization.

## Verdict

**GO**. The defect is real, reproducible, and confirmed by code inspection. The proposed fix is minimal, targeted, and preserves normal dispatch behavior. All blocking preflight checks pass. The implementation scope is well-defined and the target paths are within the GT-KB root. The proposal includes the required project authorization, specification links, and bridge file chain evidence.
