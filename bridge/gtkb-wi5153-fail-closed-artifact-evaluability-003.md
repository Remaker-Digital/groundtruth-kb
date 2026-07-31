REVISED

# Revised Implementation Proposal - Fail-closed assertion evaluability two-file slice

bridge_kind: prime_proposal
Document: gtkb-wi5153-fail-closed-artifact-evaluability
Version: 003
Responds to: bridge/gtkb-wi5153-fail-closed-artifact-evaluability-002.md
Author: Prime Builder (Codex A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6d63-9c6e-7521-89ae-4d97407e443c
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop Prime Builder bridge-revision worker; approval_policy=never; sandbox=danger-full-access

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5153

target_paths: ["groundtruth-kb/src/groundtruth_kb/assertions.py", "groundtruth-kb/tests/test_assertions.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Response

Prime Builder accepts every condition in version 002 and takes the expressly
permitted scope split. This revision authorizes intent for exactly the assertion
engine and its focused test module. No evaluator file, database, formal carrier,
schema, gate module, configuration, dispatcher state, harness state, Git
operation, release, deployment, credential action, or cleanup is in scope.

Both mandatory candidate preflights are run before filing and both live
preflights are rerun after filing. A failure or blocking gap stops the revision.

## Governance Of Pre-Existing Bytes

The worktree is not a clean implementation baseline. Current bytes are evidence
only and receive no retroactive approval from this proposal:

| Path | Worktree status | Current SHA-256 | HEAD/index Git blob | Governance disposition |
| --- | --- | --- | --- | --- |
| `groundtruth-kb/src/groundtruth_kb/assertions.py` | tracked, unstaged modified; 97 insertions and 31 deletions relative to HEAD | `4B23634A43171094D576438C806B26D132307CBE6B23F3AFC54A07201750F71C` | `175a67d798ffe77e67818f4ebec90c5a058f447b` | Foreign review evidence. Do not assume authorship, approval, ownership, or finalization eligibility. |
| `groundtruth-kb/tests/test_assertions.py` | tracked and clean at HEAD/index | `F83C87A27F2D0F0CC87959A1021552E76FC13418E32F02D8C1E78453E9BFA8EE` | `724e501bc335fc542a7cba65e39977d5561665f2` | Clean baseline for post-GO WI-5153 regression tests. |

After a fresh independent GO, Prime Builder must acquire a matching
`go_implementation` claim and schema-v3 implementation-start packet before any
protected mutation. Prime then compares each scoped worktree hunk to HEAD and
current foreign ownership evidence, attributes only WI-5153 semantics, preserves
all unrelated bytes, and reconciles conflicts without overwriting or absorbing
foreign work. Any ambiguous hunk, changed hash/status, target drift, PAUTH denial,
claim denial, or start-packet denial fails closed and returns to the bridge.

The implementation report must identify exact WI-5153 hunks and their final
hashes. Independent verification and governed Git finalization remain separate
gates; this proposal grants neither.

## Summary

Make assertion execution and aggregation fail closed for unsupported, skipped,
partial, and zero-executable required evidence while preserving legitimate
machine-executable PASS and FAIL behavior. Add focused regression coverage in
the assertion test module. This slice does not add a separate evaluator.

## Claim

WI-5153 may change only the two declared target paths to introduce explicit
assertion-result states and fail-closed aggregation. Pre-existing dirty bytes
remain foreign until a post-GO Prime Builder mechanically attributes and
reconciles the approved semantics.

## Requirement Sufficiency

Existing requirements are sufficient. `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
defines complete, current, machine-evaluable, fail-closed evidence;
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` protects legitimate behavior and
history; the bridge, project-authorization, linkage, and verification carriers
govern execution. No owner decision or formal-carrier amendment is required.

## Specification Links

- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - required assertion evidence must be complete, machine-evaluable, and fail closed when unsupported or indeterminate.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - required evidence cannot pass through omission, prose, or skipped execution.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - preserve legitimate executable outcomes, APIs, and history while making incomplete evidence explicit.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation requires the active project PAUTH and operation-time authorization.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - fresh claim and start-packet checks must succeed before mutation.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - target paths and permitted mutation classes remain bounded by the active PAUTH.
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` - this work item remains linked to its governing specifications.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization does not bypass bridge GO, claim, start, report, or verification gates.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected implementation requires independent GO and later independent VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, PAUTH, work item, and parseable targets are explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - each proposed behavior is tied to governing requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification must rerun the mapped positive, negative, compatibility, and isolation checks.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - this two-file split excludes unresolved descendant work and may proceed only on its own approved scope.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserve durable proposal, report, and verdict evidence through the governed lifecycle.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - implementation intent advances only through explicit lifecycle states.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the revision records scope, evidence, and dependencies without treating worktree state as authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - both platform targets and all verification output remain inside `E:\GT-KB`.

## Prior Deliberations

- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-ASSURANCE-INVARIANT-PLAN` - establishes fail-closed evaluability before hard-invariant projection.
- `DELIB-202666274` - authorizes the modernization program while retaining PAUTH, bridge, review, nonimpairment, and Git gates.

## Owner Decisions / Input

No new owner decision is required. Active PAUTH
`PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE`,
version 3, is active, project-scoped, and owner-backed by `DELIB-202666274`.
Its parsed mutation classes include source and test. Its registered forbidden
operations continue to prohibit credential lifecycle, destructive cleanup,
dispatcher mutation, external-system mutation, Git commit/history rewrite/push,
production deployment, and release.

## In-Root Placement Evidence

Both declared targets resolve beneath `E:\GT-KB`. Test output and transient
verification state must remain beneath the same root. No outside-root dependency
or artifact is permitted.

## Proposed Scope

1. Represent assertion outcomes with explicit `PASS`, `FAIL`, `PARTIAL`, `UNASSESSED`, and `NOT_APPLICABLE` states while retaining the compatibility `passed` boolean.
2. Make unsupported required assertion types and skipped required children non-passing.
3. Propagate incomplete evidence through `all_of` and `any_of` instead of filtering skipped children out before composition.
4. Report no defined assertions as `NOT_APPLICABLE`, all unsupported assertions as `UNASSESSED`, mixed complete/incomplete results as `PARTIAL`, and direct executable failure as `FAIL`.
5. Make aggregate success require every applicable carrier to pass and expose deterministic partial/unassessed counts and diagnostics.
6. Add focused tests for unsupported, zero-executable, mixed, composite, all-pass, direct-fail, compatibility-boolean, and summary-format behavior.
7. Preserve public assertion APIs, supported assertion execution, stored/prose reconciliation, historical classification, and unrelated concurrent changes.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "DELIB-202666274",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "groundtruth_kb.assertions.run_spec_assertions and run_all_assertions",
  "before_behavior": "Unsupported, skipped, or zero-executable required evidence can be omitted from aggregation and appear passing.",
  "after_behavior": "Every applicable assertion set exposes an explicit result and only complete supported executable PASS evidence satisfies the aggregate.",
  "self_descriptive_naming": "PASS, FAIL, PARTIAL, UNASSESSED, and NOT_APPLICABLE directly identify the evidence state.",
  "obsolete_guidance_disposition": "The compatibility passed boolean remains, but skipped required evidence is no longer interpreted as passing.",
  "history_preservation": "Existing assertion definitions, public APIs, legitimate executable outcomes, stored/prose reconciliation, and historical evidence remain available.",
  "baseline": {
    "assertion_tests": "78 passed",
    "schema_and_gate_tests": "49 passed",
    "source_worktree_status": "foreign unstaged modification",
    "test_worktree_status": "clean"
  },
  "expected_result": {
    "supported_all_pass": "PASS",
    "direct_failure": "FAIL",
    "all_unsupported": "UNASSESSED",
    "mixed_complete_and_incomplete": "PARTIAL",
    "no_defined_assertions": "NOT_APPLICABLE"
  },
  "rollback": "Through a separately governed transaction, remove only independently verified WI-5153 hunks and preserve all foreign or unrelated bytes.",
  "hard_invariants": [
    "no unsupported required evidence passes",
    "no skipped required child is discarded",
    "no incomplete aggregate passes",
    "no unrelated tracked hunk is claimed",
    "no evaluator, schema, gate, database, or configuration path changes"
  ],
  "fail_closed_conditions": [
    "unknown assertion type",
    "malformed assertion data",
    "incomplete composite evidence",
    "ambiguous pre-existing hunk attribution",
    "target hash or status drift",
    "claim, PAUTH, or implementation-start denial"
  ],
  "essential_context_preservation": "Preserve supported assertion behavior, compatibility booleans, deterministic diagnostics, public APIs, history, and exact foreign-byte provenance."
}
```

## Specification-Derived Verification Plan

| Requirement | Exact verification | Required result |
| --- | --- | --- |
| Fail-closed core semantics and compatibility | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_assertions.py -q --tb=short --timeout=600` | All focused tests pass, including explicit unsupported, zero-executable, partial, composite, direct-fail, all-pass, compatibility, and formatting cases. Pre-filing baseline: `78 passed in 9.14s`. |
| Schema and gate nonimpairment | `groundtruth-kb/.venv/Scripts/python.exe -m pytest groundtruth-kb/tests/test_assertion_schema.py groundtruth-kb/tests/test_gates.py -q --tb=short --timeout=600` | Existing modules remain unchanged and all tests pass. Pre-filing baseline: `49 passed in 3.36s`. |
| Static quality | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check groundtruth-kb/src/groundtruth_kb/assertions.py groundtruth-kb/tests/test_assertions.py` | Exit 0 with `All checks passed!`. |
| Formatting | `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check groundtruth-kb/src/groundtruth_kb/assertions.py groundtruth-kb/tests/test_assertions.py` | Exit 0 with both files formatted. |
| Scope and foreign-byte isolation | `git diff --check -- groundtruth-kb/src/groundtruth_kb/assertions.py groundtruth-kb/tests/test_assertions.py` plus `git diff --numstat --` and SHA-256/Git-blob readback for both paths | No whitespace errors; implementation report attributes only WI-5153 hunks, lists final hashes, and preserves every unrelated byte. |
| Governance applicability | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5153-fail-closed-artifact-evaluability` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5153-fail-closed-artifact-evaluability` | Both filed-content gates exit 0 with no missing required specification and no blocking clause gap. |

## Acceptance Criteria

1. Unsupported, skipped, zero-executable, partial, and malformed required evidence cannot produce aggregate PASS.
2. Complete supported executable evidence preserves legitimate PASS and FAIL outcomes.
3. Composite and aggregate results retain incomplete children and emit deterministic explicit states.
4. Compatibility booleans and existing public assertion APIs remain available without weakening explicit-state authority.
5. The focused assertion suite, schema/gate nonimpairment suite, Ruff check, and Ruff format check pass.
6. The implementation report proves exact hunk attribution and final hashes for only the two declared paths.
7. No pre-GO dirty byte is treated as approved; no foreign or unrelated hunk is overwritten, absorbed, staged, committed, or reported as WI-5153 work.

## Risk / Rollback

The intended change may expose previously false-green carriers as incomplete.
That is required behavior, not a reason to relax the result states. The main
implementation risk is accidental ownership of foreign dirty bytes; post-GO
hunk attribution and exact hash evidence are mandatory controls.

Rollback is a separately proposed and independently reviewed removal of only
verified WI-5153 hunks. It must preserve all foreign work, assertion history,
public APIs, and append-only governance evidence.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/assertions.py`
- `groundtruth-kb/tests/test_assertions.py`

## Recommended Commit Type

`fix`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
