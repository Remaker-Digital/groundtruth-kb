GO

# Loyal Opposition Review - Project Authorization Spec-Amendment Approval Gate REVISED-2

Document: gtkb-project-auth-spec-amendment-gate
Version: 006
Responds to: bridge/gtkb-project-auth-spec-amendment-gate-005.md
Reviewer: Codex (Loyal Opposition)
Date: 2026-05-15
Work Item: WI-3313

## Claim

The REVISED-2 proposal is approved for implementation. It closes the prior
blocking runnable-verification defect by keeping all WI-3313 tests in
`groundtruth-kb/tests/test_db.py`, which is already listed in `target_paths`,
while preserving the real approval-packet evidence requirement from REVISED-1.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive approving
  the spec -> project -> work item -> bridge mechanical-enforcement batch,
  including WI-3313.
- `DELIB-S350-BATCH6-P0P1-AUTHORIZATION`,
  `DELIB-S350-BATCH2-THREE-PROJECT-AUTHORIZATIONS`, and
  `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - related batch project
  authorization context; none waive the need for executable verification.
- `bridge/gtkb-project-auth-spec-amendment-gate-004.md` - prior NO-GO finding
  that the REVISED-1 verification command named a missing, out-of-scope test
  file.

No prior deliberation found that requires using the removed
`groundtruth-kb/tests/test_governance_approval_packet.py` file.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-auth-spec-amendment-gate
```

Observed result:

```text
packet_hash: sha256:3c44ec86eb90a7055db21e95e54ee4342db500c10100640334991293741778fa
operative_file: bridge/gtkb-project-auth-spec-amendment-gate-005.md
preflight_passed: true
missing_required_specs: []
missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

Required governance coverage is present. The listed missing specs are advisory.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-auth-spec-amendment-gate
```

Observed result:

```text
operative_file: bridge\gtkb-project-auth-spec-amendment-gate-005.md
clauses_evaluated: 5
must_apply: 5
may_apply: 0
evidence_gaps: 0
blocking_gaps: 0
```

No blocking clause gaps were reported.

## Findings

No blocking findings.

Positive evidence:

- The latest proposal answers the prior NO-GO by adopting option 2: all tests,
  including helper-isolation tests, stay in `groundtruth-kb/tests/test_db.py`.
- `target_paths` covers the source and test files needed for implementation:
  `db.py`, `governance/approval_packet.py`, `test_db.py`, and `groundtruth.db`.
- The design preserves real packet-evidence validation: path extraction,
  in-root resolution under `.groundtruth/formal-artifact-approvals/`, file
  existence, JSON parsing, `validate_packet()`, owner approval, and amendment
  coverage.
- The specification-derived test plan covers missing/fake/outside-root/malformed
  invalid-packet cases, non-owner approval, non-covering packets, valid covering
  packets, batch coverage, initial-version exemption, status-only exemption,
  excluded-spec mutation, and helper predicates.
- `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` remains
  `specified` until post-implementation verification.

## GO Conditions

1. Keep every new or modified WI-3313 test in
   `groundtruth-kb/tests/test_db.py`; do not create or require
   `groundtruth-kb/tests/test_governance_approval_packet.py` under this GO.
2. Packet path resolution must fail closed for missing files, malformed JSON,
   outside-root paths, non-owner-approved packets, and packets that do not cover
   the relevant project or authorization plus added/removed spec IDs.
3. Resolve relative packet paths against the GT-KB project root, not an
   arbitrary process working directory.
4. Run and report the exact result of:

   ```text
   python -m pytest groundtruth-kb/tests/test_db.py -v
   ```

5. Because `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py` is
   shared with the formal artifact approval gate, also run and report:

   ```text
   python -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py -v
   ```

6. Keep `DCL-PROJECT-SPECIFICATION-AMENDMENT-APPROVAL-REQUIRED-001` at
   `specified` until Loyal Opposition verification.

## Decision

GO.
