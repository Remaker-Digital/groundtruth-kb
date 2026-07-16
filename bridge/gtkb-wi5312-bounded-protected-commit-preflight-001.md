NEW

# WI-5312 - Bounded protected-commit authorization preflight

bridge_kind: prime_proposal
Document: gtkb-wi5312-bounded-protected-commit-preflight
Version: 001
Author: Prime Builder Codex A
Date: 2026-07-16 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f6d-60cd-7040-b73f-c7d23757c4bc
author_model: OpenAI Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop default reasoning configuration

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-WI5312-BOUNDED-COMMIT-PREFLIGHT-20260715
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5312

target_paths: ["scripts/check_protected_commit_authorization.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", "platform_tests/groundtruth_kb/governance/test_commit_preflight.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Make the mandatory protected-commit authorization preflight scale with the
number of evidence records plus paths instead of their product. The current
checker calls `list_named_packets()` for every protected path and independently
rescans every by-bridge packet, terminal bridge chain, approved proposal, and
target-path list for every protected path. With 343 staged paths the canonical
preflight exceeded 300 seconds and remained CPU-active beyond six minutes.

Load and validate live-GO packets once, resolve terminal-VERIFIED target sets
once, then evaluate every protected path against that immutable in-memory
evidence snapshot using the existing `path_authorized` matcher. Preserve exact
fail-closed semantics, corrupt-evidence diagnostics, bridge finalization checks,
source attribution, and CLI exit codes. This is a performance repair only; it
does not widen any authorization, infer authority, suppress a finding, or
introduce cached authority across invocations.

## Intended Implementation

1. Build one evaluation-local live-GO evidence snapshot from
   `list_named_packets()`: valid packets, their bridge/source labels, and every
   packet error currently surfaced by the checker.
2. Build one evaluation-local terminal-VERIFIED snapshot by scanning each
   by-bridge packet and bridge thread once, resolving the GO-approved proposal
   and its exact target globs once, and retaining all current error text.
3. Pass those snapshots into protected-path evaluation. Continue using
   `path_authorized` unchanged for matching and preserve the current live-GO
   precedence over terminal-VERIFIED evidence.
4. Keep versioned VERIFIED bridge-file `Commit Finalization Evidence` checks
   independent and unchanged. Add evidence-scan counts to JSON diagnostics so a
   slow or unexpectedly large evaluation is observable without progress writes
   or runtime state.
5. Add decision-parity fixtures for valid GO, valid VERIFIED, corrupt packets,
   missing proposals, unauthorized paths, mixed evidence, and duplicate paths.
   Add a 343-path scaling regression that asserts each evidence source is loaded
   once per evaluation rather than once per path.

## Performance Contract

For `P` protected paths, `L` live packets, and `V` by-bridge VERIFIED packets,
evidence loading is `O(L + V)` and path matching is `O(P * (L + V))` in-memory.
Filesystem, Git, bridge-chain, JSON, and proposal reads must be `O(L + V)`, not
`O(P * (L + V))`. No persistent cache is introduced; every invocation reads
current governed evidence exactly once.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the gate must continue recognizing only governed live-GO and terminal-VERIFIED evidence.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal links the authorization, PAUTH scope, hygiene, and non-impairment requirements it affects.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - WI-5312, its tree-stabilization project, and bounded PAUTH are declared above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification must prove decision parity and bounded evidence loading.
- `GOV-STANDING-BACKLOG-001` - the observed timeout is tracked as P0 WI-5312 instead of bypassing the mandatory preflight.
- `GOV-WORK-TREE-HYGIENE-001` - exact finalization requires a usable mandatory preflight on realistic dirty scopes.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project authorization remains evaluated from current governed records without widening.
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` - restrictive PAUTH work-item scope and target matching remain fail-closed.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - latency improves while every authorization denial and diagnostic remains semantically identical.

## Prior Deliberations

- `DELIB-202666332` - assigns exact independently VERIFIED finalization as the clean-tree path and forbids broad capture.
- `DELIB-WI5116-PHASE1-SWEEP-DIAGNOSIS-20260709` - establishes that finalization must preserve fail-safe evidence behavior rather than bypass it.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - supports a deterministic service implementation with no AI judgment or persistent stale cache.

## Owner Decisions / Input

`DELIB-202666332` authorizes the exact work required to finalize independently
VERIFIED scopes and clear the worktree. The bounded PAUTH permits only this
source/test repair and expressly excludes bypass, destructive cleanup, push,
deployment, release, credentials, and dispatcher mutation.

## Requirement Sufficiency

Existing requirements sufficient. The current project-authorization, PAUTH
restriction, bridge authority, and worktree-hygiene requirements fully define
which decisions the checker must make. WI-5312 changes evaluation complexity,
not authority semantics, so no new or revised requirement is needed.

## Spec-Derived Verification Plan

- `GOV-FILE-BRIDGE-AUTHORITY-001`, project linkage, and standing backlog:
  proposal applicability and mandatory clause preflights pass with no blocking
  gaps; valid GO and VERIFIED fixtures still clear only matching paths.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`: mixed valid/invalid PAUTH
  fixtures produce byte-for-byte-equivalent decision payloads and errors before
  and after the refactor.
- `GOV-WORK-TREE-HYGIENE-001`: the 343-path scaling fixture loads each evidence
  source once and the live checker completes within the 300-second wrapper on
  the current staged scope.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`: no denial disappears, live-GO
  precedence stays intact, corrupt evidence remains fail-closed, and no
  persistent cache or bridge/runtime write is introduced.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: independent Loyal
  Opposition reruns focused, integration, and live timing evidence.

Expected commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py platform_tests/groundtruth_kb/governance/test_commit_preflight.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py platform_tests/groundtruth_kb/governance/test_commit_preflight.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/check_protected_commit_authorization.py platform_tests/scripts/test_check_protected_commit_authorization.py platform_tests/groundtruth_kb/governance/test_commit_preflight.py
groundtruth-kb/.venv/Scripts/python.exe scripts/check_protected_commit_authorization.py --staged --json
```

The live command may return authorization findings for the current mixed staged
set; success means it completes within the wrapper and returns deterministic
diagnostics, not that unrelated staged paths are authorized.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666332",
  "canonical_authority": "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 and GOV-FILE-BRIDGE-AUTHORITY-001",
  "primary_route": "gt commit preflight invokes scripts/check_protected_commit_authorization.py --staged",
  "before_behavior": "Each protected path reloads all live packets and rescans all terminal VERIFIED bridge evidence, exceeding 300 seconds for 343 staged paths.",
  "after_behavior": "Each evidence source is loaded once per invocation and all paths receive the same fail-closed decisions from one current snapshot.",
  "self_descriptive_naming": "LiveGoEvidence, VerifiedEvidence, and evaluation-local evidence summary fields expose what was loaded and matched.",
  "obsolete_guidance_disposition": "No guidance changes; repeated per-path I/O is removed as an implementation defect, not retained as policy.",
  "history_preservation": "All governed packet, proposal, bridge-chain, and diagnostic sources remain read-only and unchanged.",
  "baseline": {
    "staged_paths": 343,
    "wrapper_limit_seconds": 300,
    "observed_result": "timeout with checker still CPU-active"
  },
  "expected_result": {
    "evidence_loads_per_invocation": 1,
    "decision_parity": "all authorized, denied, and corrupt-evidence fixtures unchanged",
    "live_wrapper_result": "deterministic completion before timeout"
  },
  "rollback": {
    "instructions": "Revert only the exact WI-5312 source/test commit; no evidence, bridge, index, or runtime state restoration is needed.",
    "test": "Run the focused authorization and commit-preflight suites."
  },
  "hard_invariants": [
    "No authorization broadening or inferred authority",
    "Corrupt or unreadable evidence remains fail-closed and visible",
    "Live-GO evidence retains precedence over terminal VERIFIED evidence",
    "path_authorized matching semantics remain unchanged",
    "No persistent cache, bridge write, dispatcher mutation, staging, or cleanup"
  ],
  "fail_closed_conditions": [
    "missing or unreadable live packet inventory",
    "unresolvable terminal bridge thread",
    "missing GO-approved proposal",
    "unparseable target paths",
    "decision-parity mismatch"
  ],
  "essential_context_preservation": "The snapshot retains every source label and evidence error needed to explain each protected-path decision."
}
```

## Risk / Rollback

The primary risk is accidentally treating a scan error as an empty evidence set
or changing first-match/precedence behavior while consolidating reads. Golden
decision payloads, mixed-error fixtures, unchanged `path_authorized`, and an
evaluation-local immutable snapshot mitigate that risk. Rollback is an exact
revert of the eventual WI-5312 commit; no governance or runtime artifact is
mutated by either implementation or rollback.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5312-bounded-protected-commit-preflight`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - preserve the protected-commit gate's decisions while removing repeated
evidence I/O that makes mandatory finalization inconclusive.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
