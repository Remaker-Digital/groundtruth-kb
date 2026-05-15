VERIFIED

# Loyal Opposition Verification - Project Authorization Spec-Amendment Gate

Document: gtkb-project-auth-spec-amendment-gate
Version: 008
Responds to: bridge/gtkb-project-auth-spec-amendment-gate-007.md
Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-15 UTC
Work Item: WI-3313

## Verdict

VERIFIED.

The implementation report carries forward the linked specifications, maps the
source DCL to executable tests, and the current code/test state satisfies the
GO conditions from `bridge/gtkb-project-auth-spec-amendment-gate-006.md`.
Project authorization spec-set amendments now require a real owner-approved
formal-artifact approval packet that resolves inside the project root, passes
packet validation, is approved by `owner`, and covers the project or
authorization plus every added or removed spec. Initial versions and
status-only changes with unchanged spec sets remain exempt. The source DCL
remains `specified`.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this thread was `NEW`, actionable for Loyal Opposition.
- Read the full bridge thread from `-001` through `-007`.
- Reviewed the implementation report at `bridge/gtkb-project-auth-spec-amendment-gate-007.md`.
- Inspected current implementation in:
  - `groundtruth-kb/src/groundtruth_kb/db.py`
  - `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py`
  - `groundtruth-kb/tests/test_db.py`
- Ran mandatory bridge preflights, Deliberation Archive search, the reported pytest suite, targeted ruff check, and a source DCL status check.

## Prior Deliberations

Deliberation Archive search was run before verification:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations search "WI-3313 post implementation project authorization spec amendment owner approved packet VERIFIED" --limit 8
```

Relevant results:

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive establishing the spec -> project -> work item -> bridge enforcement chain and authorizing this project scope.
- `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS` - contextual owner direction for project authorizations.
- `DELIB-S350-BATCH6-P0P1-AUTHORIZATION` - contextual owner direction to keep parallelizing remaining P0/P1 work.
- Prior bridge evidence in this thread: `bridge/gtkb-project-auth-spec-amendment-gate-002.md`, `-004.md`, and `-006.md`.

No prior deliberation was found that waives the amendment packet requirement or
contradicts this verification.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-auth-spec-amendment-gate
```

Observed result:

```text
packet_hash: sha256:105720ad7ba74dac636a9397c24856560b9bcf6941c426abd4f67d5c38e32081
operative_file: bridge/gtkb-project-auth-spec-amendment-gate-007.md
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

No required specification omissions were reported.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-auth-spec-amendment-gate
```

Observed result:

```text
operative_file: bridge\gtkb-project-auth-spec-amendment-gate-007.md
clauses_evaluated: 5
must_apply: 4
may_apply: 1
evidence_gaps: 0
blocking_gaps: 0
```

No blocking clause gaps were reported.

## Verification Evidence

### Claim: DB-layer spec-amendment gate is enforced

Evidence:

- `groundtruth-kb/src/groundtruth_kb/db.py:3975` defines `_validate_spec_amendment_approval_packet()`.
- `groundtruth-kb/src/groundtruth_kb/db.py:4002-4005` compares prior and new included/excluded spec sets and returns only when they are unchanged.
- `groundtruth-kb/src/groundtruth_kb/db.py:4014-4052` requires a cited packet path, in-root resolution, file existence, readable JSON, schema validity, `approved_by == "owner"`, and amendment coverage.
- `groundtruth-kb/src/groundtruth_kb/db.py:4090-4101` invokes the gate for later authorization versions before inserting the replacement row.

Result: PASS. The implementation matches the report's claim that spec-set
mutations are fail-closed unless a real owner-approved covering packet is
cited.

### Claim: approval packet helpers cover path extraction and coverage tests

Evidence:

- `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:62-73` defines `parse_packet_path_from_change_reason()`.
- `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:76-103` defines `packet_covers_amendment()`, requiring the packet text to mention the project id or authorization id and every added/removed spec id.
- `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:106` retains the shared `validate_packet()` schema gate.

Result: PASS.

### Claim: specification-derived test coverage exists and passes

Evidence:

- `groundtruth-kb/tests/test_db.py:1142` defines `TestProjectAuthorizationSpecAmendment`.
- `groundtruth-kb/tests/test_db.py:1232-1302` covers blocked cases for missing packet paths, fake paths, outside-root paths, malformed JSON, schema-invalid packets, non-owner packets, and non-covering packets.
- `groundtruth-kb/tests/test_db.py:1313-1326` covers successful covering and batch-packet cases.
- `groundtruth-kb/tests/test_db.py:1366-1380` covers helper isolation.
- `groundtruth-kb/tests/test_db.py:1105-1109` keeps the WI-3312 status-only test as a pure status change so WI-3313 correctly owns spec-set amendments.

Reviewer rerun:

```text
python -m pytest groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_cli_projects.py platform_tests/hooks/test_formal_artifact_approval_gate.py -q
```

Observed result:

```text
103 passed, 1 warning in 35.68s
```

Result: PASS.

### Claim: source DCL was not promoted prematurely

Command:

```text
$env:PYTHONPATH='groundtruth-kb/src'; python -c "from groundtruth_kb.db import KnowledgeDB; kb=KnowledgeDB('groundtruth.db'); row=kb.get_spec('DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001'); print(row['status'])"
```

Observed result:

```text
specified
```

Result: PASS. `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001`
remains `specified`.

### Additional check: targeted lint

Command:

```text
python -m ruff check groundtruth-kb/src/groundtruth_kb/db.py groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py groundtruth-kb/tests/test_db.py
```

Observed result:

```text
All checks passed!
```

Result: PASS.

## Findings

No blocking findings.

## Acceptance Criteria

- `IP-1` DB-layer enforcement for spec-set amendments: PASS.
- `IP-2` cited approval packet must be real, in-root, JSON-readable, schema-valid, owner-approved, and covering: PASS.
- `IP-3` invalid/missing/non-covering packet cases fail closed: PASS.
- `IP-4` initial authorization versions and pure status changes remain exempt: PASS.
- `IP-5` source DCL remains `specified`: PASS.
- Mandatory bridge applicability and ADR/DCL clause gates: PASS.

## Decision

VERIFIED.
