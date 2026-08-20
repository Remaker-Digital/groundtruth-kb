VERIFIED

# Loyal Opposition Verdict — VERIFIED — WI-5105 Finalization Commingle Guard

bridge_kind: lo_verdict
Document: gtkb-wi5105-finalization-commingle-guard
Version: 004
Responds to: bridge/gtkb-wi5105-finalization-commingle-guard-003.md
Approved proposal: bridge/gtkb-wi5105-finalization-commingle-guard-001.md
Reviewer: Loyal Opposition (Ollama, harness D)
Date: 2026-07-10 UTC

author_identity: Ollama Loyal Opposition
author_harness_id: D
author_session_context_id: 2026-07-10T08-26-26Z-loyal-opposition-D-f7c484
author_model: kimi-k2.7-code:cloud
author_model_version: cloud
author_model_configuration: Ollama harness shim; route kimi-k2-7-code-cloud; skill bridge-review; guarded tools Read, Write, Edit, Grep, Glob, Bash

---

## Verdict

**VERIFIED.** The implementation report at version 003 satisfies the approved
proposal and the Loyal Opposition GO conditions C1–C3. The commingle guard is
implemented deterministically, fail-closed on positive evidence, additive to
existing gates, and covered by executed focused tests with clean static
analysis. I am approving finalization of the four approved target paths.

## Recommended commit type

Recommended commit type: `fix(bridge): WI-5105 released-claim finalization commingle guard` (matches the implementation report's stated recommended commit type).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Applicability Preflight

- packet_hash: `sha256:5cb879f60d37a358260fab0d5cedd55cd829897cdba5621aa64852fde896c71a`
- bridge_document_name: `gtkb-wi5105-finalization-commingle-guard`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5105-finalization-commingle-guard-003.md`
- operative_file: `bridge/gtkb-wi5105-finalization-commingle-guard-003.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`

## Clause Applicability

- Bridge id: `gtkb-wi5105-finalization-commingle-guard`
- Operative file: `bridge\gtkb-wi5105-finalization-commingle-guard-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- must_apply clauses satisfied:
  - `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL`
  - `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`
  - `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`

## Verified Paths

- `scripts/implementation_authorization.py`
- `scripts/implementation_start_gate.py`
- `platform_tests/scripts/test_implementation_authorization.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

## Spec-to-Test Mapping

| Spec | Test evidence | Executed |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_create_packet_blocks_dirty_path_claimed_by_nonterminal_peer_report` and `test_gate_blocks_dirty_path_claimed_by_nonterminal_peer_report` prove block/allow decisions derive from the versioned bridge chain and named packets. | yes | pass |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | The guard is called after existing project/GO/claim/WI-4471 checks in both `create_authorization_packet` and `gate_decision`; `test_create_packet_allows_when_peer_claim_registry_read_fails` shows existing gates still pass while the new guard stays additive. | yes | pass |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Peer scope comes from `target_path_globs` in the peer's named packet; report paths come from the peer's versioned `implementation_report` `## Files Changed` section. | yes | pass |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The focused suite and Ruff checks cover the implementation; see Evidence below. | yes | pass |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Tests distinguish terminal `VERIFIED` peers, clean paths, same-thread reports, and non-overlapping paths from attributable non-terminal peer evidence. | yes | pass |

## Evidence

### Implementation scope and placement

The guard is placed at both implementation chokepoints named in the proposal:

- `scripts/implementation_authorization.py` calls
  `peer_report_dirty_path_collision_reason(project_root, targets=target_paths,
  bridge_id=bridge_id)` during packet creation, after the existing project
  authorization, GO, claim, and WI-4471 active-claim collision checks.
- `scripts/implementation_start_gate.py` imports the same helper and applies it
  in `gate_decision` immediately before a protected mutation, with the
  WI-4471 active-claim guard still running first.

The implementation is additive, not a bypass, matching condition C3.

### Guard precision

`peer_report_dirty_path_collision_reason` blocks only when all three facts are
positive (per condition C2):

1. A non-terminal peer `implementation_report` names a concrete path.
2. The peer's hash-verified historical named packet authorizes that path.
3. Git reports the same concrete path dirty in the current worktree.

It ignores same-thread packets, terminal (`VERIFIED`, `WITHDRAWN`) peers, clean
paths, non-overlapping paths, unreadable peer chains, and missing peer packets.
This matches the approved design's fail-soft, fail-closed-on-positive-evidence
bias.

### LO conditions C1–C3 coverage

The focused test suite adds and executes:

- `test_create_packet_blocks_dirty_path_claimed_by_nonterminal_peer_report`
  (authorization block, names peer and path).
- `test_peer_report_dirty_path_guard_allows_terminal_clean_same_thread_and_nonoverlap`
  (allow cases).
- `test_peer_report_dirty_path_guard_fails_soft_for_unreadable_peer_chain`
  (fail-soft).
- `test_create_packet_allows_when_peer_claim_registry_read_fails` (registry
  failure does not block, preserving existing own-claim fail-closed behavior).
- `test_gate_blocks_dirty_path_claimed_by_nonterminal_peer_report`
  (protected-mutation block, additive to active-claim gate).

### Commands executed and results

```
$ groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py -q --tb=short --basetemp .harness-tmp/wi5105
================= 296 passed, 2 warnings in 77.92s (0:01:17) ==================

$ groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py
All checks passed!

$ groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py
4 files already formatted
```

## Commands Executed

```
$ groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py -q --tb=short --basetemp .harness-tmp/wi5105
================= 296 passed, 2 warnings in 77.92s (0:01:17) ==================

$ groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py
All checks passed!

$ groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py
4 files already formatted
```

## Dispatcher health advisory

`gt bridge dispatch status` reports `health: FAIL` because no active
prime-builder harness is dispatchable. This does not affect the LO review and is
recorded as advisory context for the Prime Builder / owner.

## Prior Deliberations

- `bridge/gtkb-wi5105-finalization-commingle-guard-001.md` — approved proposal.
- `bridge/gtkb-wi5105-finalization-commingle-guard-002.md` — independent GO with
  conditions C1–C3.
- `bridge/gtkb-wi5105-finalization-commingle-guard-003.md` — implementation
  report under review.
