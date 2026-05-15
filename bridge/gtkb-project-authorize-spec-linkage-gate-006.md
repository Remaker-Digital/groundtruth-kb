GO

# Loyal Opposition Review - Project Authorize Spec-Linkage Gate REVISED-2

Document: gtkb-project-authorize-spec-linkage-gate
Version: 006
Responds to: bridge/gtkb-project-authorize-spec-linkage-gate-005.md
Reviewer: Codex (Loyal Opposition)
Date: 2026-05-15
Work Item: WI-3312

## Claim

The REVISED-2 proposal is approved for implementation. It closes the prior
blocking false-negative class by removing the brittle `type` allowlist and
using the durable predicate that an active project authorization must cite at
least one `specifications`-table row returned by `db.get_spec()` whose lifecycle
status is one of `specified`, `implemented`, or `verified`.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` - owner directive approving
  the project/work-item/spec bridge-enforcement batch.
- `bridge/gtkb-project-authorize-spec-linkage-gate-004.md` - prior NO-GO that
  identified the REVISED-1 `type` allowlist as excluding live `SPEC-*` rows.

No prior deliberation found that requires project authorization linkage to use
a `type` allowlist instead of MemBase table membership plus lifecycle status.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-authorize-spec-linkage-gate
```

Observed result:

```text
preflight_passed: true
packet_hash: sha256:c6f2c9b6c13ad8d46fddd2fe01fa8c637dc513851e0dd47facfe837ac0812649
operative_file: bridge/gtkb-project-authorize-spec-linkage-gate-005.md
missing_required_specs: []
missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

The advisory omissions are non-blocking for this review. Required governance
coverage is present.

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-authorize-spec-linkage-gate
```

Observed result:

```text
preflight_passed: true
operative_file: bridge\gtkb-project-authorize-spec-linkage-gate-005.md
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

- The proposal includes implementation authorization metadata for
  `Project Authorization`, `Project`, and `Work Item: WI-3312`.
- `target_paths` stays within `E:\GT-KB` and covers the DB, service, CLI, tests,
  and `groundtruth.db` surfaces needed for this gate.
- The revised validation predicate removes the defective `type` allowlist and
  keeps lifecycle status as the approval discriminator.
- The verification plan includes negative coverage for missing, empty, unknown,
  and retired spec IDs, plus positive coverage for heterogeneous live spec row
  types (`specification`, `requirement`, and `governance`).
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` remains at `specified` until
  post-implementation verification.

## GO Conditions

1. Do not add a replacement `type` allowlist unless a new owner decision or
   governing specification explicitly requires that discriminator.
2. Implement the typed service exception and CLI `click.UsageError` translation
   within the approved target paths.
3. Run this verification command and report the observed result in the
   post-implementation report:

   ```text
   python -m pytest groundtruth-kb/tests/test_db.py groundtruth-kb/tests/test_cli_projects.py -v
   ```

4. The post-implementation report must show that
   `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` remains `specified` until
   Loyal Opposition verification.
5. The post-implementation report must include observed evidence for the three
   positive type-coverage tests and state explicitly that no `type` filter was
   introduced.

## Decision

GO.
