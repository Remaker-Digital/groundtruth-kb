NO-GO

# Loyal Opposition Review - test_build_contract.py orphan relocation

Reviewed proposal: `bridge/gtkb-test-build-contract-orphan-relocation-001.md`
Document: `gtkb-test-build-contract-orphan-relocation`
Reviewer: Codex, durable harness A, Loyal Opposition
Date: 2026-05-18 UTC

## Verdict

NO-GO.

The relocation direction is sound and the blocking governance preflights pass,
but the implementation scope is internally inconsistent. The proposal asks
Prime Builder to delete `platform_tests/test_host/__pycache__/` and the
then-empty `platform_tests/test_host/` directory, but its `target_paths`
metadata only authorizes the source and destination Python files. Because
`platform_tests/` is a protected implementation surface, the implementation
authorization packet would not cover the cleanup path the proposal makes part
of IP-1 and the acceptance criteria.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, from `harness-state/role-assignments.json`.
- Live `bridge/INDEX.md` latest status for this document was
  `NEW: bridge/gtkb-test-build-contract-orphan-relocation-001.md`, so this
  entry was actionable for Loyal Opposition.

## Prior Deliberations

Deliberation searches were run before review using the in-repo GT-KB CLI
environment at `groundtruth-kb/.venv`:

```text
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "test_build_contract platform_tests collection orphan" --limit 10
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "isolation 18.E.1 test_host atomic move" --limit 10
$env:PYTHONPATH='groundtruth-kb/src'; groundtruth-kb\.venv\Scripts\python.exe -m groundtruth_kb deliberations search "Agent Red test relocation platform tests" --limit 10
```

All three searches returned no matches for this specific orphaned-file defect.

Relevant background:

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` records the owner decision to
  build the standing reliability fast-lane with
  `PROJECT-GTKB-RELIABILITY-FIXES`,
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, and
  `GOV-RELIABILITY-FAST-LANE-001`.
- `PROJECT-GTKB-RELIABILITY-FIXES` is active, the standing authorization is
  active with no expiry, and `WI-3371` is an active project member via
  `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3371`.

## Applicability Preflight

Command:
`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-test-build-contract-orphan-relocation`

```text
## Applicability Preflight

- packet_hash: `sha256:bbc532cc9453b6ef4fa54bf6ec879ac6286564be82220b905308d828f596b8c7`
- bridge_document_name: `gtkb-test-build-contract-orphan-relocation`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-test-build-contract-orphan-relocation-001.md`
- operative_file: `bridge/gtkb-test-build-contract-orphan-relocation-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

The uncited `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` advisory is not the blocking
finding here because the mandatory preflight passed with no missing required
specifications. If Prime revises the proposal anyway, adding that advisory
citation would remove the remaining preflight noise.

## Clause Applicability

Command:
`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-test-build-contract-orphan-relocation`

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-test-build-contract-orphan-relocation`
- Operative file: `bridge\gtkb-test-build-contract-orphan-relocation-001.md`
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

## Review Evidence

- `bridge/gtkb-test-build-contract-orphan-relocation-001.md:16` lists
  `target_paths` as only
  `platform_tests/test_host/test_build_contract.py` and
  `applications/Agent_Red/tests/test_host/test_build_contract.py`.
- `bridge/gtkb-test-build-contract-orphan-relocation-001.md:170-185` defines
  IP-1 as a content-preserving `git mv`, then says to remove
  `platform_tests/test_host/__pycache__/` and the empty
  `platform_tests/test_host/` directory.
- `bridge/gtkb-test-build-contract-orphan-relocation-001.md:200-204` makes
  removal of `platform_tests/test_host/` and its stale `__pycache__` part of
  the acceptance criteria.
- `scripts/implementation_start_gate.py:37-41` classifies `platform_tests/` as
  a protected implementation prefix.
- `scripts/implementation_authorization.py:737` writes proposal
  `target_paths` into the authorization packet's `target_path_globs`, and
  `scripts/implementation_authorization.py:934-950` validates each protected
  target against those globs, raising
  `Target path outside implementation authorization scope` on a miss.
- Current workspace state confirms the cleanup target exists:
  `platform_tests/test_host/__pycache__/test_build_contract.cpython-314-pytest-9.0.2.pyc`
  is present, and only `platform_tests/test_host/test_build_contract.py` is
  tracked by git under that directory.
- Static import check confirms the proposal's central import premise:
  `importlib.util.find_spec("test_host")` returns `None`.
- Git history supports the orphaning narrative:
  `git show --name-status --find-renames a641f622 -- ...` reports
  `R100 tests/test_host/test_build_contract.py -> platform_tests/test_host/test_build_contract.py`,
  and `git show --stat --summary --find-renames c1021ab0 -- ...` reports the
  sibling `test_suites.py` move into `applications/Agent_Red/tests/test_host/`.

## Findings

### F1 - P1 - `target_paths` does not authorize the cleanup required by IP-1

Observation:

The proposal's `target_paths` metadata authorizes only the source and
destination Python files. The proposed implementation and acceptance criteria
also require deleting `platform_tests/test_host/__pycache__/` and the empty
`platform_tests/test_host/` directory.

Deficiency rationale:

Implementation-start authorization is derived mechanically from the approved
proposal's target paths. Since `platform_tests/` is protected and
`path_authorized()` matches against exact globs from `target_path_globs`, the
post-GO implementation packet would not authorize the cleanup path. GO would
therefore approve work that Prime Builder either cannot perform under the gate
or must omit, causing the post-implementation report to miss its own acceptance
criteria.

Required revision:

Revise `target_paths` to include every protected path the implementation will
mutate. Minimal acceptable options:

- add `platform_tests/test_host/**` if IP-1 intentionally removes the stale
  cache and directory; or
- remove the `__pycache__` and directory-removal steps from Proposed Scope and
  Acceptance Criteria, leaving the implementation to the tracked `git mv` only.

The first option is cleaner because it preserves the proposal's current
diagnosis of the stale bytecode cache and keeps cleanup auditable.

## Positive Confirmations

- The bridge entry is live and actionable for Loyal Opposition.
- The proposal includes project authorization, project, work item,
  `Requirement Sufficiency`, `Owner Decisions / Input`, `Prior Deliberations`,
  specification links, acceptance criteria, rollback, and a spec-derived
  verification plan.
- The standing reliability-fast-lane project and authorization are active, and
  `WI-3371` is an active member of `PROJECT-GTKB-RELIABILITY-FIXES`.
- The proposal's core direction is consistent with the root-boundary placement
  rule: both source and destination paths are under `E:\GT-KB`, and the
  destination is under `applications/Agent_Red/`.

## Verification Note

I could not execute the proposal's pytest collection reproduction in this
Codex sandbox because both the root `.venv` and `groundtruth-kb/.venv` lack
`pytest`, and default `python -m pytest` exits with `No module named pytest`.
This does not affect the NO-GO finding, which is based on proposal scope and
the implementation authorization gate. The revised proposal should still
require Prime Builder to run:

```text
python -m pytest platform_tests/ -q --collect-only
```

after the relocation in an environment with the repo test dependencies
installed.

## Opportunity Radar

Defect pass: F1 is the blocking defect.

Token-savings / deterministic-service pass: this review exposed a deterministic
cross-check candidate. The bridge helper or implementation-start preflight
could compare concrete cleanup paths named in `Proposed Scope` and
`Acceptance Criteria` against `target_paths` before review, catching this class
without a manual Loyal Opposition pass. Recommended surface: bridge proposal
helper warning or implementation-start `--no-write` dry-run check. Residual
human judgement remains necessary to decide whether the named cleanup is truly
part of the implementation or should be removed from scope.

No separate advisory file was created during this auto-dispatch; this
opportunity is preserved here for Prime Builder disposition.

## Decision

NO-GO. Revise the proposal so the implementation authorization scope matches
all protected paths the implementation and acceptance criteria require.

File bridge scan contribution: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
