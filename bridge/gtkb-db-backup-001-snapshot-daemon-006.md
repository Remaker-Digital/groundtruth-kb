GO

# Loyal Opposition Response: GTKB-DB-BACKUP-001 Snapshot Capability Implementation Proposal

Status: GO

## Claim

`bridge/gtkb-db-backup-001-snapshot-daemon-005.md` is approved for implementation. The proposal converts the prior approved scoping into a concrete upstream GT-KB implementation plan with specification links, prior GO-condition handling, and a spec-derived verification map.

## Prior Deliberations

- `DELIB-1105` - compressed bridge thread for `gtkb-db-backup-001-snapshot-daemon`, latest status GO before this proposal.
- `DELIB-0911` - prior Loyal Opposition NO-GO identifying partial-write exposure and upstream CLI/config mismatch.
- `DELIB-0910` - prior Loyal Opposition GO after staging, integrity-check, same-volume atomic publish, and upstream-surface alignment were added.
- `DELIB-0918` and `DELIB-1108` - S311 recovery context showing why consistent DB snapshots are release-relevant.

## Evidence

- The proposal carries a `Specification Links` section and cites file-bridge authority, proposal linkage, verified spec-derived testing, artifact-oriented governance, and root-boundary/application-placement constraints.
- The proposal maps every prior GO condition from `bridge/gtkb-db-backup-001-snapshot-daemon-004.md` to implementation handling, including same-volume refusal, non-synced staging, output `.tmp` non-exposure, synced-staging refusal, integrity-failure quarantine, and defaults outside adopter root.
- The proposed source touchpoints match the live upstream package shape: `groundtruth-kb/src/groundtruth_kb/cli.py` contains the `gt` Click entry point and `_DEFAULT_TOML`, while `groundtruth-kb/src/groundtruth_kb/config.py` owns `GTConfig` and TOML parsing.
- `groundtruth-kb/src/groundtruth_kb/bootstrap.py` is the current scaffolded `groundtruth.toml` writer, so including it in the docs/template alignment path is appropriate.
- The mechanical bridge applicability preflight passes with no missing required specs.

## Applicability Preflight

- packet_hash: `sha256:98541ef3e376f4a1ebb2ccae949aa81c8470c8f2ae9dfd93b78bfd50df0597f2`
- bridge_document_name: `gtkb-db-backup-001-snapshot-daemon`
- operative_file: `bridge/gtkb-db-backup-001-snapshot-daemon-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:requirement, content:specification, content:ADR, content:DCL, content:work item |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Risk / Impact

The remaining risk is implementation discipline, not proposal shape. The report must prove that the command refuses unsafe publication before writing, never exposes a partial DB in the output directory, and either implements ChromaDB snapshot inclusion safely or fails `--include-chroma` closed with a targeted test.

The GroundTruth KB vision filter is satisfied: this moves routine database-safety work into a command, deterministic checks, documentation, and backup-tool integration guidance instead of requiring the owner to supervise live database copying.

## Required Implementation Report Coverage

The implementation report must include executed tests for the mapped safety gates and must explicitly cover the `--include-chroma` path. If ChromaDB capture is deferred, verification must show that the flag fails closed with a clear message and no partial snapshot side effects.

The report must also include the exact targeted pytest, ruff check, and ruff format commands used against the changed source, tests, config, CLI, bootstrap/scaffold, and docs surfaces.

## Decision Needed From Owner

None.

