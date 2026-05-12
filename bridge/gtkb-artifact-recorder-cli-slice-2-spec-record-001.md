NEW

# Implementation Proposal (Slice 2) - `gt spec record` CLI Surface

**Document:** `gtkb-artifact-recorder-cli-slice-2-spec-record`
**Status:** `NEW`
**Version:** 001
**Date:** 2026-05-12
**Author:** Prime Builder (Codex, harness A)
**Bridge kind:** implementation_proposal
**Parent thread:** `gtkb-artifact-recorder-cli` (Slice 0 scoping GO at `bridge/gtkb-artifact-recorder-cli-004.md`)
**Predecessor slice:** `gtkb-artifact-recorder-cli-slice-1-deliberations-record` (VERIFIED at `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-008.md`)
**Recommended commit type:** `feat:`

## Claim

Slice 2 adds `gt spec record` as the governed formal-spec recording service for
GOV/SPEC/PB/ADR/DCL/REQ records. The command mirrors the Slice 1 topology: it is
a high-level deterministic service that validates owner/AUQ evidence and a
formal-artifact approval packet in-process before calling the MemBase API. The
lower-level raw mutation surfaces remain protected by the existing Bash
PreToolUse hook.

This proposal requests authorization for implementation only after Loyal
Opposition GO. No source, hook, MemBase, or approval-packet mutation is
authorized by this `NEW` file itself.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `PB-ARTIFACT-APPROVAL-001`
- `ADR-ARTIFACT-FORMALIZATION-GATE-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`
- `DELIB-0874`
- `.claude/hooks/formal-artifact-approval-gate.py`
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/gtkb-artifact-recorder-cli-003.md`
- `bridge/gtkb-artifact-recorder-cli-004.md`
- `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-008.md`

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: owner decision establishing the active mandate to move repetitive formal-artifact plumbing into deterministic services.
- `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE`: original friction surface for manual formal-artifact insertion.
- `DELIB-0874`: artifact-oriented governance framing.
- `DELIB-0835`: strict formal-artifact approval and audit-trail owner decision.
- `DELIB-0687`: credential-safety narrowing context relevant to approval packets and hook behavior.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING`: lifted the prior feature-freeze block on this workstream.
- `bridge/gtkb-artifact-recorder-cli-004.md`: Slice 0 GO authorizing per-slice bridge filings only.
- `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-008.md`: verifies the shared approval-packet validator and in-process governed-service topology that this slice reuses.

No cited deliberation waives formal-artifact approval evidence.

## Owner Decisions / Input

Existing owner decisions already authorize this proposal filing:

1. S312 approved the artifact-recorder CLI as the named first manifestation of the Deterministic Services Principle.
2. Slice 0 received GO at `bridge/gtkb-artifact-recorder-cli-004.md`, authorizing per-slice bridge filings.
3. The owner directed continued autonomous top-priority work where no blocking owner input is required.

Outstanding owner decisions before GO: none.

## Live State Probed

Observed current implementation surfaces before filing:

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb --help
```

Result: no top-level `spec` or `specs` record command exists. Current spec-adjacent
commands are scaffold/check/intake/seed surfaces, not a governed formal-spec
recording service.

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb deliberations record --help
```

Result: Slice 1 exposes the high-level `deliberations record` service with
`--owner-presented`, AUQ evidence, `--dry-run`, and JSON output. Slice 2 should
reuse this user-facing evidence pattern.

Code probes:

- `groundtruth-kb/src/groundtruth_kb/db.py` already exposes `KnowledgeDB.insert_spec(...)`.
- `KnowledgeDB._auto_detect_spec_type(...)` maps `GOV-`, `PB-`, `ADR-`, and `DCL-` prefixes; `SPEC-` and `REQ-` remain `requirement`.
- `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py` already accepts spec artifact types: `governance`, `requirement`, `protected_behavior`, `architecture_decision`, and `design_constraint`.
- `.claude/hooks/formal-artifact-approval-gate.py` still matches direct `insert_spec(...)` and `update_spec(...)` snippets, but does not match a future high-level `gt spec record` command. That is the intended topology: high-level `record` validates in-process; lower-level raw mutation paths remain hook-gated.

## Scope

### IP-1: New top-level `spec` command group

Add a top-level `gt spec record` command. The singular group name follows the
parent Slice 0 wording and keeps this slice narrow. Broader spec list/get/update
CLI surfaces remain out of scope.

Required options:

- `--id`
- `--title`
- `--status`
- `--content-file`
- `--change-reason`
- `--auq-id`
- `--auq-answer`
- `--owner-presented`

Optional options:

- `--type` with choices matching MemBase types: `requirement`, `governance`, `protected_behavior`, `architecture_decision`, `design_constraint`
- `--priority`
- `--scope`
- `--section`
- `--handle`
- `--tags-json`
- `--assertions-json`
- `--constraints-json`
- `--affected-by-json`
- `--testability`
- `--source-paths-json`
- `--approved-by` (defaults to `owner`)
- `--dry-run`
- `--json`

### IP-2: Type and subtype validation

Resolve artifact type before any packet or DB write:

| ID prefix | Resolved type |
| --- | --- |
| `GOV-` | `governance` |
| `PB-` | `protected_behavior` |
| `ADR-` | `architecture_decision` |
| `DCL-` | `design_constraint` |
| `SPEC-` | `requirement` |
| `REQ-` | `requirement` |

If `--type` is supplied, it must match the prefix-derived type. Unknown prefixes
are rejected in Slice 2.

Subtype checks:

- `PB-*` requires a non-empty `--assertions-json` list.
- `ADR-*` content must include a decision/rationale/consequences structure and either an alternatives-considered or rejected-alternatives section.
- `DCL-*` content must include an explicit constraint section.
- `GOV-*`, `SPEC-*`, and `REQ-*` require non-empty content and normal metadata only.

### IP-3: In-process approval and insert flow

Implementation flow:

1. Resolve the GT-KB project root and reject `--content-file` outside that root.
2. Read the content file as the spec `description` and approval-packet `full_content`.
3. Validate required owner evidence: `--owner-presented`, `--auq-id`, `--auq-answer`, and `--change-reason`.
4. Resolve spec type from prefix and optional `--type`.
5. Run subtype validation.
6. Reject existing current specs with the same `--id`; Slice 2 is create-only and must not silently create a new version of an existing spec. A future slice can add an explicit update/version command.
7. Construct a formal approval packet with:
   - `artifact_type=<resolved type>`
   - `artifact_id=<--id>`
   - `action="create"`
   - `source_ref=<--id>`
   - `full_content=<content-file text>`
   - `approval_mode="approve"`
   - `presented_to_user=true`
   - `transcript_captured=true`
   - `explicit_change_request="AUQ <auq-id>: <auq-answer>"`
   - `approved_by=<--approved-by or "owner">`
   - `changed_by=<resolved harness identity, fallback "gt-cli">`
   - `change_reason=<--change-reason>`
8. Call `validate_packet(packet)` before writing any packet file or DB row.
9. Write `.groundtruth/formal-artifact-approvals/<date>-<spec-id>.json`.
10. Call `KnowledgeDB.insert_spec(...)`.
11. Print the created spec id, or JSON payload when `--json` is supplied.

`--dry-run` performs steps 1 through 8 and prints the proposed packet and DB
operation. It writes no packet file and does not call `insert_spec(...)`.

### IP-4: Hook boundary preservation

Do not add `gt spec record` to `FORMAL_MUTATION_PATTERNS`. The direct raw
mutation patterns remain protected:

- direct `insert_spec(...)`
- direct `update_spec(...)`
- raw SQL against `specifications`

Slice 2 adds tests proving that `gt spec record` is not hook-matched while the
CLI itself still blocks missing approval evidence before any DB write.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py` - add the `spec` command group and `record` wiring.
- `groundtruth-kb/src/groundtruth_kb/cli_spec_record.py` - new governed spec-record service implementation.
- `platform_tests/groundtruth_kb/cli/test_spec_record.py` - new CLI service tests.
- `platform_tests/hooks/test_formal_artifact_approval_gate.py` - extend hook-boundary tests for `gt spec record`.

No Agent Red live artifact is in scope. No file outside `E:\GT-KB` is in scope.

## Spec-to-Test Mapping

| Spec / requirement | Proposed verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Proposal/report filed in `bridge/`; `bridge/INDEX.md` top-of-thread entry preserved append-only. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight on this bridge thread passes with no missing required specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this mapping forward with exact commands and observed results. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Tests reject content files outside `config.project_root`; all touched files remain under `E:\GT-KB`. |
| `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `ADR-ARTIFACT-FORMALIZATION-GATE-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | Packet construction/validation tests prove required owner presentation, transcript capture, hash binding, manual approval identity, and no DB write before validation. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Spec status/type tests cover create-only behavior and reject existing IDs to avoid accidental version churn. |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | Dry-run/no-write, valid-create, and subtype-validation tests prove deterministic service behavior replaces manual script boilerplate. |

## Test Plan

Pre-implementation bridge gates:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-2-spec-record
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-2-spec-record
```

Implementation verification after GO:

```powershell
$env:PYTHONPATH='groundtruth-kb/src'; python -m pytest platform_tests/groundtruth_kb/cli/test_spec_record.py -q --tb=short
$env:PYTHONPATH='groundtruth-kb/src'; python -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short
$env:PYTHONPATH='groundtruth-kb/src'; python -m pytest platform_tests/groundtruth_kb/governance/test_approval_packet.py -q --tb=short
$env:PYTHONPATH='groundtruth-kb/src'; python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_spec_record.py platform_tests/groundtruth_kb/cli/test_spec_record.py platform_tests/hooks/test_formal_artifact_approval_gate.py
$env:PYTHONPATH='groundtruth-kb/src'; python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_spec_record.py platform_tests/groundtruth_kb/cli/test_spec_record.py platform_tests/hooks/test_formal_artifact_approval_gate.py
```

Test cases to add:

- T-SR-1: missing `--owner-presented` exits non-zero before packet or DB write.
- T-SR-2: missing AUQ evidence exits non-zero before packet or DB write.
- T-SR-3: dry-run constructs a valid approval packet and writes nothing.
- T-SR-4: content file outside project root is rejected.
- T-SR-5: GOV/SPEC/PB/ADR/DCL/REQ prefixes resolve to the expected MemBase type.
- T-SR-6: explicit `--type` mismatch is rejected.
- T-SR-7: existing spec id is rejected instead of creating a new version.
- T-SR-8: PB without assertions is rejected.
- T-SR-9: ADR missing alternatives/rejected-alternatives structure is rejected.
- T-SR-10: successful GOV and DCL records create one packet and one current spec row.
- T-SR-11: `--approved-by` overrides the default manual identity.
- T-SR-12: `gt spec record` is not hook-matched, while the CLI still blocks missing evidence in-process.

## Risks And Rollback

| Risk | Mitigation |
| --- | --- |
| Prefix/type ambiguity creates wrong spec type | Prefix-derived type is canonical; supplied `--type` must match. |
| Create command accidentally versions existing specs | Slice 2 rejects existing IDs; future update/version command must be separately proposed. |
| Subtype validation becomes too broad | Slice 2 keeps validation structural and minimal; richer schemas can be added in later slices. |
| Hook boundary confusion repeats Slice 1's early mistake | Proposal explicitly preserves the in-process `record` topology and tests the hook boundary. |

Rollback after implementation is `git revert <implementation commit>`. The bridge
proposal itself is append-only and can be superseded by a later REVISED file if
Loyal Opposition requests changes.

## Pre-Filing Preflight

Commands to run after this file and the INDEX entry are written:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-2-spec-record
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-2-spec-record
```

Observed results after filing:

- Applicability preflight passed with `missing_required_specs: []` and `missing_advisory_specs: []`.
- ADR/DCL clause preflight passed with `must_apply: 4`, `Evidence gaps in must_apply clauses: 0`, and `Blocking gaps (gate-failing): 0`.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
