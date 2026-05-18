GO

# Loyal Opposition Review - test_build_contract.py orphan relocation

Reviewed proposal: `bridge/gtkb-test-build-contract-orphan-relocation-003.md`
Document: `gtkb-test-build-contract-orphan-relocation`
Reviewer: Codex, durable harness A, Loyal Opposition
Date: 2026-05-18 UTC

## Verdict

GO.

The revised proposal resolves the prior P1 finding from
`bridge/gtkb-test-build-contract-orphan-relocation-002.md`. Scope is now a
content-preserving `git mv` between the two authorized `target_paths`, with no
`__pycache__` or directory cleanup included in the implementation or acceptance
criteria. The mandatory applicability preflight passes, the mandatory clause
preflight reports zero blocking gaps, and the project authorization evidence
supports proceeding through the reliability fast-lane.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, from `harness-state/role-assignments.json`.
- Live `bridge/INDEX.md` latest status for this document was
  `REVISED: bridge/gtkb-test-build-contract-orphan-relocation-003.md`, so this
  entry was actionable for Loyal Opposition.

## Prior Deliberations

Deliberation searches were run before review using the in-repo GT-KB CLI
environment:

```text
$env:PYTHONPATH='groundtruth-kb/src'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "test_build_contract platform_tests collection orphan" --limit 10
$env:PYTHONPATH='groundtruth-kb/src'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "isolation 18.E.1 test_host atomic move" --limit 10
$env:PYTHONPATH='groundtruth-kb/src'; .\groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "Agent Red test relocation platform tests" --limit 10
```

All three searches returned no matches for this specific orphaned-file defect.

Relevant governing background remains:

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` records the owner decision to
  establish the standing reliability fast-lane.
- `PROJECT-GTKB-RELIABILITY-FIXES` is active.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active, has no expiry,
  and covers work items by active project membership.
- `WI-3371` is an active member via
  `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3371`.

## Applicability Preflight

Command:
`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-test-build-contract-orphan-relocation`

```text
## Applicability Preflight

- packet_hash: `sha256:0e7aefa9bbabe14698369b6815a84565e77961acc4fabdece7ba46107d6ff40b`
- bridge_document_name: `gtkb-test-build-contract-orphan-relocation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-test-build-contract-orphan-relocation-003.md`
- operative_file: `bridge/gtkb-test-build-contract-orphan-relocation-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

## Clause Applicability

Command:
`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-test-build-contract-orphan-relocation`

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-test-build-contract-orphan-relocation`
- Operative file: `bridge\gtkb-test-build-contract-orphan-relocation-003.md`
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
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._
```

## Review Evidence

- `bridge/gtkb-test-build-contract-orphan-relocation-003.md:17` lists exactly
  two authorized target paths: the current platform-test file and the Agent Red
  destination file.
- `bridge/gtkb-test-build-contract-orphan-relocation-003.md:43-50` explicitly
  narrows IP-1 to the tracked `git mv` and drops stale-cache and empty-directory
  cleanup from scope.
- `bridge/gtkb-test-build-contract-orphan-relocation-003.md:217-219` states
  IP-1 is the only implementation step, mutating exactly the two `target_paths`.
- `bridge/gtkb-test-build-contract-orphan-relocation-003.md:238-245` acceptance
  criteria require only the tracked rename and post-move platform collection
  check; no cleanup acceptance criterion remains.
- Current tree state before implementation: `platform_tests/test_host/test_build_contract.py`
  exists and `applications/Agent_Red/tests/test_host/test_build_contract.py`
  does not yet exist.
- `platform_tests/test_host/test_build_contract.py:123` contains the module-level
  `from test_host.suites import SUITE_CONFIGS` import. Sibling files under
  `applications/Agent_Red/tests/test_host/` already use the same `test_host`
  import family.
- `python -m groundtruth_kb projects show PROJECT-GTKB-RELIABILITY-FIXES --json`
  confirms `PROJECT-GTKB-RELIABILITY-FIXES` is active and `WI-3371` has active
  membership.
- `python -m groundtruth_kb projects authorizations PROJECT-GTKB-RELIABILITY-FIXES --json`
  confirms `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active, has no
  expiry, and covers work items by active project membership.

## Spec-To-Test Mapping Review

The proposal maps the operative requirement and linked placement ADR to
observable post-implementation checks:

| Linked requirement/specification | Required evidence after implementation | Review result |
|---|---|---|
| `WI-3371` and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m pytest platform_tests/ -q --collect-only` exits 0 with no `ModuleNotFoundError` | Adequate for this pure relocation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | source path absent and destination path present after tracked rename | Adequate for this pure relocation |

Prime Builder's post-implementation report must carry this mapping forward and
include the exact command output observed after implementation.

## Findings

No blocking findings.

## Positive Confirmations

- The prior NO-GO finding is closed by removing the unauthorized cleanup scope.
- The proposal includes project authorization, project, work item,
  `target_paths`, `Requirement Sufficiency`, `Owner Decisions / Input`,
  `Prior Deliberations`, concrete specification links, acceptance criteria,
  rollback, and a spec-derived verification plan.
- The core relocation direction is consistent with the root-boundary placement
  rule: both paths are under `E:\GT-KB`, and the destination is under
  `applications/Agent_Red/`.
- The recommended commit type `fix:` matches the claimed diff: a defect repair
  by content-preserving file relocation, with no new public capability.

## Implementation Constraints For Prime Builder

- Proceed only after creating a current implementation-start authorization
  packet from this GO.
- Keep implementation to the approved tracked rename:
  `platform_tests/test_host/test_build_contract.py` to
  `applications/Agent_Red/tests/test_host/test_build_contract.py`.
- Do not delete `platform_tests/test_host/__pycache__/` or the empty directory
  under this GO; those paths are explicitly out of scope.
- File a post-implementation report with the executed
  `python -m pytest platform_tests/ -q --collect-only` result and the
  source/destination path evidence.

## Opportunity Radar

No new material opportunity finding is added in this review. The deterministic
cross-check candidate from the prior NO-GO (compare concrete implementation
steps and acceptance criteria against `target_paths`) remains valid and is
already acknowledged in the revised proposal. The oversized `bridge/INDEX.md`
condition is also already owned by the separate bridge-index archival thread.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
