NEW

# Implementation Proposal (Slice 3) - `gt spec update` Governed Versioning Service

Document: gtkb-artifact-recorder-cli-slice-3-scoping
Status: NEW
Version: 001
Date: 2026-05-14
Session: S350
Author: Prime Builder (Claude Code, harness B)
Bridge kind: implementation_proposal
Parent thread: gtkb-artifact-recorder-cli (Slice 0 scoping GO at bridge/gtkb-artifact-recorder-cli-004.md)
Predecessor slices: gtkb-artifact-recorder-cli-slice-1-deliberations-record (VERIFIED at -008); gtkb-artifact-recorder-cli-slice-2-spec-record (VERIFIED at -006)
Source: WI-3263 (project GTKB-DETERMINISTIC-SERVICES-001, sub-project "Artifact recording")
Recommended commit type: feat:
target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_spec_update.py", "platform_tests/groundtruth_kb/cli/test_spec_update.py", "platform_tests/hooks/test_formal_artifact_approval_gate.py"]

## Summary

Slice 3 adds `gt spec update` as the governed companion to the verified `gt spec record` create-only service. The command produces a new version of an existing spec via `KnowledgeDB.update_spec(...)` after validating owner/AUQ evidence and writing a formal-artifact approval packet with `action="update"`. Like Slice 2 it is an in-process deterministic service: the high-level CLI surface validates evidence before any DB write, while the raw `update_spec(...)` mutation pattern remains protected by the existing PreToolUse hook for direct-API callers.

This proposal extends the verified Slice-2 pattern (`groundtruth-kb/src/groundtruth_kb/cli_spec_record.py`) into the spec-versioning surface explicitly deferred by Slice 2 IP-3 step 6 ("A future slice can add an explicit update/version command"). Slice 3 closes the spec-mutation half of the artifact-recorder workstream without altering Slice 1 or Slice 2 behavior, the approval-packet schema, or hook-matching rules.

No source, hook, MemBase, or approval-packet schema mutation is authorized by this NEW file. Implementation begins only after Loyal Opposition GO and a fresh implementation-authorization packet for this bridge id.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-ARTIFACT-APPROVAL-001
- PB-ARTIFACT-APPROVAL-001
- ADR-ARTIFACT-FORMALIZATION-GATE-001
- DCL-ARTIFACT-APPROVAL-HOOK-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- GOV-STANDING-BACKLOG-001
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE
- DELIB-0835
- DELIB-0874
- .claude/rules/acting-prime-builder.md
- .claude/rules/operating-model.md
- .claude/rules/file-bridge-protocol.md
- .claude/rules/codex-review-gate.md
- .claude/rules/deliberation-protocol.md
- .claude/hooks/formal-artifact-approval-gate.py
- bridge/gtkb-artifact-recorder-cli-004.md
- bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-008.md
- bridge/gtkb-artifact-recorder-cli-slice-2-spec-record-006.md

## Prior Deliberations

- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - owner decision establishing the active-pursuit mandate to move repetitive formal-artifact plumbing behind deterministic services; names `GTKB-ARTIFACT-RECORDER-CLI` as the first concrete manifestation.
- DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE - original friction surface (~150 LOC of manual orchestration per formal artifact); spec-update is one of the recurring friction points alongside spec-create.
- DELIB-0835 - strict formal-artifact approval and audit-trail owner decision; constrains approval-packet behavior the update path must preserve (presentation, transcript capture, identity binding, hash binding).
- DELIB-0874 - artifact-oriented governance broader framing.
- DELIB-S319-MEMBASE-EFFECTIVE-USE-ASSESSMENT - retrieval-side governance for MemBase reads/writes informing the update-path scope.
- bridge/gtkb-artifact-recorder-cli-004.md - Slice 0 scoping GO authorizing per-slice bridge filings; explicitly does not authorize source-code, MemBase, hook, or approval-packet schema changes.
- bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-008.md - VERIFIED record of the shared in-process governed-service topology this slice reuses.
- bridge/gtkb-artifact-recorder-cli-slice-2-spec-record-006.md - VERIFIED record of the spec-record create-only service; IP-3 step 6 explicitly defers update/version handling to a future slice (this proposal).

No retrieved deliberation contradicts filing this slice or waives the formal-artifact approval and spec-derived verification requirements.

## Owner Decisions / Input

Owner authorizations enabling this proposal filing:

1. Owner approval at S312 (2026-04-27, captured at memory/work_list.md row 113) - authorizes the GTKB-ARTIFACT-RECORDER-CLI workstream as the named first manifestation of `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.
2. Slice 0 GO at bridge/gtkb-artifact-recorder-cli-004.md - authorizes per-slice bridge filings.
3. Owner direction 2026-05-14 S350: "Please parallelize work and start as many priority backlog projects as possible" - authorizes batch filing of priority backlog proposals; per-proposal Codex GO still required before implementation. Source: WI-3263 (P1 hygiene item in project GTKB-DETERMINISTIC-SERVICES-001) names the artifact-recorder advance as the targeted action.

Outstanding owner decisions before GO: none. The proposal itself does not request a new owner decision; per-spec update operations executed post-GO will each carry their own owner-presentation evidence inside the approval packet, exactly as Slice 2's create path does today.

## Requirement Sufficiency

Existing requirements sufficient. The linked governance specs already constrain spec-update behavior identically to spec-create (same approval-packet shape, same hook boundary, same isolation constraints). No new specs are required for Slice 3.

## Implementation Plan

IP-1: Add `gt spec update` subcommand to the existing `spec` command group in `groundtruth-kb/src/groundtruth_kb/cli.py`. The subcommand wires to a new `cli_spec_update.py` service module mirroring `cli_spec_record.py`'s topology.

IP-2: Required CLI options:

- `--id` (existing spec id; required)
- `--change-reason` (required)
- `--auq-id`, `--auq-answer`, `--owner-presented` (required AUQ evidence)
- `--content-file` (in-root file whose contents become the new spec description and the approval-packet `full_content`; required for update because the approval-packet schema requires non-empty `full_content`)

Optional mutation options (carry-forward semantics handled by `KnowledgeDB.update_spec(...)`):

- `--title`, `--status`, `--priority`, `--scope`, `--section`, `--handle`, `--testability`
- `--tags-json`, `--assertions-json`, `--constraints-json`, `--affected-by-json`, `--source-paths-json`
- `--approved-by` (defaults to `owner`)
- `--dry-run`, `--json`

IP-3: In-process update flow:

1. Resolve GT-KB project root and reject `--content-file` outside that root.
2. Validate required owner evidence: `--owner-presented`, `--auq-id`, `--auq-answer`, `--change-reason`.
3. Resolve spec via `KnowledgeDB.get_spec(id)`. Reject when no current spec row exists for the id (update of a non-existent spec is rejected; use `gt spec record` for create).
4. Compute the new packet's `artifact_type` from the live spec row's `type` field (not from the id prefix; this preserves the canonical type assignment made at create time).
5. Read `--content-file` as the new spec description and the approval-packet `full_content`.
6. Construct the approval packet with `action="update"`, `source_ref="<id>@v<current_version>"` (anchors the update to the version being superseded), `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request="AUQ <auq-id>: <auq-answer>"`, `approved_by=<--approved-by or "owner">`, `changed_by=<resolved harness identity, fallback "gt-cli">`, `change_reason=<--change-reason>`, plus `artifact_type` from step 4 and `full_content` from step 5.
7. Call `validate_packet(packet)` from `groundtruth_kb.governance.approval_packet` before any write.
8. Write `.groundtruth/formal-artifact-approvals/<date>-<spec-id>-v<new_version>.json` (the `-v<n>` suffix avoids collision with the create-time packet file from Slice 2).
9. Call `KnowledgeDB.update_spec(id, changed_by, change_reason, **fields)` with the merged mutation fields.
10. Print the new version metadata, or JSON payload when `--json` is supplied.

`--dry-run` performs steps 1 through 7 and prints the proposed packet and the merged field set. It writes no packet file and does not call `update_spec(...)`.

IP-4: Hook boundary preservation. Do not add `gt spec update` to `FORMAL_MUTATION_PATTERNS` in `.claude/hooks/formal-artifact-approval-gate.py`. The direct raw mutation pattern `update_spec(...)` remains protected by the existing pattern at line 56 of that hook. Slice 3 adds a focused hook test asserting that `python -m groundtruth_kb spec update --id ...` is not hook-matched, while the CLI itself still blocks missing evidence in-process.

## Test Mapping

| Spec / requirement | Verification |
| --- | --- |
| GOV-FILE-BRIDGE-AUTHORITY-001 | Proposal filed in `bridge/`; bridge/INDEX.md top-of-thread entry preserved append-only by parent session. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Applicability preflight on this bridge thread passes with `missing_required_specs: []`. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Implementation report carries this mapping forward with exact commands and observed results. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | Tests reject `--content-file` outside `config.project_root`; all touched files remain under `E:\GT-KB`. |
| GOV-ARTIFACT-APPROVAL-001, PB-ARTIFACT-APPROVAL-001, ADR-ARTIFACT-FORMALIZATION-GATE-001, DCL-ARTIFACT-APPROVAL-HOOK-001 | Packet construction/validation tests prove required owner presentation, transcript capture, hash binding, manual approval identity, and no DB write before validation. |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | Update behavior tests cover existing-id requirement, version-increment semantics, and carry-forward of unchanged fields. |
| DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE | Dry-run/no-write, valid-update, and missing-id rejection tests prove deterministic service behavior replaces manual update-script boilerplate. |
| GOV-STANDING-BACKLOG-001 | See `## Clause Scope Clarification (Not a Bulk Operation)` below. |

Concrete test cases (in `platform_tests/groundtruth_kb/cli/test_spec_update.py`):

- T-SU-1: missing `--owner-presented` exits non-zero before packet or DB write.
- T-SU-2: missing AUQ evidence exits non-zero before packet or DB write.
- T-SU-3: missing `--change-reason` exits non-zero.
- T-SU-4: dry-run constructs a valid update approval packet and writes nothing.
- T-SU-5: content file outside project root is rejected.
- T-SU-6: non-existent spec id is rejected (cannot update what does not exist).
- T-SU-7: successful update creates one new packet file (`-v<n>.json`) and one new spec row at version = previous + 1.
- T-SU-8: carry-forward semantics - omitted optional fields preserve previous-version values per `KnowledgeDB.update_spec` contract.
- T-SU-9: `artifact_type` is derived from the live spec row's `type`, not from the id prefix.
- T-SU-10: `source_ref` in the packet anchors to the previous version (`<id>@v<previous>`).
- T-SU-11: `--approved-by` overrides the default manual identity.
- T-SU-12: invalid `--assertions-json` raises before packet write (delegated to existing `validate_assertion_list`).

Hook-boundary tests (extending `platform_tests/hooks/test_formal_artifact_approval_gate.py`):

- T-HG-SU-1: `python -m groundtruth_kb spec update --id ...` command string is NOT matched by `FORMAL_MUTATION_PATTERNS`.
- T-HG-SU-2: direct `update_spec(...)` call in command string IS matched (regression test for the existing hook behavior).

## Risk and Rollback

| Risk | Mitigation |
| --- | --- |
| Update path silently changes `artifact_type` if id prefix conflicts with stored type | IP-3 step 4 fixes type to the stored row's value; explicit `--type` option deliberately omitted. |
| Approval-packet file collision between create-time and update-time packets | IP-3 step 8 uses `-v<new_version>` suffix; tests verify two distinct files after create+update. |
| Carry-forward semantics drift between CLI service and `update_spec` API | T-SU-8 covers a representative carry-forward subset; further drift surfaces in existing `db.py` tests. |
| Hook over-matching breaks Slice 3 invocations | T-HG-SU-1 regression test asserts the negative; matches Slice 2's hook-boundary test pattern. |

Rollback after implementation: `git revert <implementation commit>`. The bridge proposal itself is append-only and can be superseded by a REVISED file if Loyal Opposition requests changes.

## Acceptance Criteria

- [ ] Applicability preflight: `missing_required_specs: []`, `missing_advisory_specs: []`.
- [ ] Clause preflight exit 0; zero blocking gaps.
- [ ] Loyal Opposition issues GO on this NEW.
- [ ] (post-GO, separate bridge round) Implementation lands, all T-SU-* and T-HG-SU-* tests pass, full ruff and the targeted pytest suites pass.
- [ ] (post-GO) Loyal Opposition issues VERIFIED on the implementation report.

## Verification Plan

Pre-implementation gates (run by Codex during review):

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-3-scoping`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-3-scoping`

Post-implementation verification (in the eventual implementation report):

- `$env:PYTHONPATH='groundtruth-kb/src'; python -m pytest platform_tests/groundtruth_kb/cli/test_spec_update.py -q --tb=short`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -m pytest platform_tests/groundtruth_kb/cli/test_spec_record.py platform_tests/groundtruth_kb/cli/test_deliberations_record.py platform_tests/groundtruth_kb/governance/test_approval_packet.py -q --tb=short` (regression of Slice 1, Slice 2, and packet-validation suites)
- `$env:PYTHONPATH='groundtruth-kb/src'; python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_spec_update.py platform_tests/groundtruth_kb/cli/test_spec_update.py platform_tests/hooks/test_formal_artifact_approval_gate.py`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -m ruff format --check <same paths>`
- `$env:PYTHONPATH='groundtruth-kb/src'; python -m groundtruth_kb spec update --help` (smoke check that the new command renders)

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is NOT a bulk standing-backlog operation. It adds a single deterministic-service command that operates on one spec at a time per invocation. The work item WI-3263 is a single inventory entry surfaced by the existing standing-backlog and converted into a properly governed bridge proposal at filing time. No work_items are mutated, retired, or batch-resolved by this proposal; no `memory/work_list.md` row is touched. The MemBase `work_items` table is the authoritative backlog source and is unchanged by Slice 3.

Each future `gt spec update` invocation post-implementation produces exactly one formal-artifact-approval packet and one new spec row version, with full per-invocation owner presentation and transcript capture. The standing-backlog visibility requirement of `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` is therefore not applicable to this proposal's authorization scope.

## Applicability Preflight

Preflight commands and their results will be embedded below by the author session after writing this file. Expected outcome: `preflight_passed: true` with both `missing_required_specs` and `missing_advisory_specs` empty, mirroring the Slice 2 NEW result.

Preflight result (embedded post-write):

```text
## Applicability Preflight

- packet_hash: `sha256:84db73cc9c7c81cf1e8352af673fc15c16d578fd9d0724c2b2b8eefa85ba399e`
- bridge_document_name: `gtkb-artifact-recorder-cli-slice-3-scoping`
- content_source: `pending_content`
- content_file: `bridge/gtkb-artifact-recorder-cli-slice-3-scoping-001.md`
- operative_file: `(none)`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

Clause preflight result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-artifact-recorder-cli-slice-3-scoping`
- Operative file: `bridge\gtkb-artifact-recorder-cli-slice-3-scoping-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass.
```

End of proposal.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
