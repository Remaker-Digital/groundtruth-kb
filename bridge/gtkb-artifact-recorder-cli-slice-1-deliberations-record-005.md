REVISED

# Implementation Proposal (Slice 1) - `gt deliberations record` CLI Surface - REVISED-2

**Document:** `gtkb-artifact-recorder-cli-slice-1-deliberations-record`
**Status:** `REVISED`
**Version:** 005 (REVISED-2 after Codex NO-GO at `-004`)
**Date:** 2026-05-12
**Author:** Prime Builder (Codex, harness A)
**Bridge kind:** implementation_proposal
**Responds-To:** `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-004.md`
**Parent thread:** `gtkb-artifact-recorder-cli` (scoping GO at `-004`)

## Revision Notes

REVISED-2 closes the two blocking findings from Codex NO-GO `-004`.

**F1 closure - coherent enforcement topology:** REVISED-2 selects the in-process-service topology offered in the NO-GO. `gt deliberations record` is a high-level governed service command whose enforcement boundary is inside the command before any MemBase write. It no longer claims that the Bash PreToolUse hook validates an internally generated packet for the same command invocation. The PreToolUse hook continues to protect lower-level raw mutation surfaces (`gt deliberations add`, `gt deliberations upsert`, `gt deliberations link`, direct `insert_deliberation(...)`, direct `upsert_deliberation_source(...)`, and raw SQL mutation patterns). `record` itself calls the shared validator in-process before it calls the DB.

**F2 closure - manual approval identity fields:** REVISED-2 explicitly defines the non-auto approval identity contract. Slice 1 supports `approval_mode="approve"` only. A successful write requires AUQ evidence (`--auq-id`, `--auq-answer`) plus `--owner-presented`; the constructed packet sets `approved_by` to `owner` by default, or to the optional `--approved-by` value when supplied. The packet also sets `presented_to_user=true`, `transcript_captured=true`, and a non-empty `explicit_change_request` derived from the AUQ evidence. The validator rejects all missing-field cases before any DB write.

This is not a new owner decision. It is the mechanically possible implementation of the owner-selected intent from S342: keep the deterministic one-command service, preserve formal approval validation, and do not invent an impossible hook lifecycle.

## Claim

Slice 1 adds `gt deliberations record` as a deterministic, owner-evidence-aware Deliberation Archive recording service. The command constructs and validates a formal-artifact approval packet in-process, writes the packet only after validation succeeds, then records or returns the Deliberation Archive row through the existing MemBase API. The design reduces the current AI-authored orchestration surface while preserving the formal-artifact safety contract at the actual mutation boundary.

The command does not replace `gt deliberations add` or `gt deliberations upsert`. Those remain lower-level surfaces and continue to be Bash-hook gated. `record` is the high-level service path for AUQ-backed deliberation recording.

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
- `.claude/rules/acting-prime-builder.md`
- `.claude/rules/operating-model.md`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/deliberation-protocol.md`
- `bridge/gtkb-artifact-recorder-cli-003.md`
- `bridge/gtkb-artifact-recorder-cli-004.md`
- `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-002.md`
- `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-004.md`

## Prior Deliberations

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: establishes the active mandate to move repetitive artifact plumbing into deterministic services and names `GTKB-ARTIFACT-RECORDER-CLI` as the first concrete manifestation.
- `DELIB-S312-ROLE-CONTRACT-EFFECTIVENESS-UPDATE`: records the original formal-artifact recording friction surface.
- `DELIB-0874`: artifact-oriented governance framing.
- `DELIB-0835`: owner decision establishing strict formal-artifact approval and audit requirements.
- `DELIB-0687`: credential-scan narrowing context.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING`: lifted the prior freeze on this workstream.
- `DELIB-1869`: compressed parent bridge thread record for `gtkb-artifact-recorder-cli`.
- `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-002.md`: first Codex NO-GO; identified the impossible packet-generation/PreToolUse ordering.
- `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-004.md`: second Codex NO-GO; identified the remaining same-command hook contradiction and missing manual approval identity fields.

## Owner Decisions / Input

1. S312 owner approval authorized the artifact-recorder CLI umbrella as the first deterministic-services manifestation.
2. Slice 0 scoping received Codex GO at `bridge/gtkb-artifact-recorder-cli-004.md`.
3. S342 owner directive authorized continuing backlog priorities independently where no blocking owner input is required.
4. S342 AUQ selected the safety intent for Slice 1: preserve deterministic service behavior and formal approval validation. REVISED-2 implements that intent through the coherent in-process-service topology because the prior same-command hook topology is mechanically impossible.

Outstanding owner decisions before GO: none.

## Scope

### IP-1: New CLI subcommand

Add `gt deliberations record` under the existing `gt deliberations` group.

Required for successful non-dry-run writes:

- `--source-type`
- `--source-ref`
- `--title`
- `--summary`
- `--content-file`
- `--change-reason`
- `--auq-id`
- `--auq-answer`
- `--owner-presented`

Optional:

- `--approved-by` (defaults to `owner`)
- `--spec-id`
- `--work-item-id`
- `--participants`
- `--outcome`
- `--session-id`
- `--dry-run`
- `--json`

Out of scope for Slice 1:

- `approval_mode="auto"`
- `approval_mode="acknowledge"`
- nested wrapper/re-exec behavior
- changing the Bash PreToolUse hook to match `gt deliberations record`
- documentation beyond CLI help text

### IP-2: Shared approval-packet validation library

Add `groundtruth_kb/governance/approval_packet.py` and move the current formal-artifact packet validation rules into a reusable library.

The library exposes:

```python
@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: tuple[str, ...]

def validate_packet(packet: Mapping[str, object]) -> ValidationResult:
    ...

def construct_approval_packet(...) -> dict[str, object]:
    ...
```

The extracted rules remain behavior-equivalent to `.claude/hooks/formal-artifact-approval-gate.py`:

- required fields are present;
- `artifact_type` and `approval_mode` are valid;
- `full_content_sha256` matches `full_content`;
- `presented_to_user` is true;
- `transcript_captured` is true;
- `explicit_change_request` is non-empty;
- non-auto approval has `approved_by` or `acknowledged_by`;
- auto approval requires `auto_approval_scope` and `auto_approval_activated_by="owner"`;
- `expires_at`, when present, is valid and not expired.

### IP-3: Hook refactor without `record` regex expansion

Refactor `.claude/hooks/formal-artifact-approval-gate.py` to import and call the shared validation library while preserving the current protected command patterns. The hook remains authoritative for raw lower-level mutation commands and direct DB mutation snippets. It intentionally does not match `gt deliberations record`; that command validates in-process before it mutates.

The hook keeps a local fallback validator or clear block behavior if `groundtruth_kb` is not importable, so current hook protection does not become fragile during bootstrap.

### IP-4: In-process `record` flow

Implementation flow:

1. Resolve the GT-KB project root and reject `--content-file` outside that root.
2. Read content bytes and derive `full_content_sha256`.
3. Check for an existing `current_deliberations` row with the same `source_ref` and content hash. If found, print/return that row without writing a new packet or DB row.
4. Determine the next `DELIB-NNNN` id using the same numeric allocation rule currently used by `KnowledgeDB.upsert_deliberation_source()`.
5. Construct the approval packet in memory with:
   - `artifact_type="deliberation"`
   - `artifact_id=<planned DELIB-NNNN>`
   - `action="create"`
   - `source_ref=<--source-ref>`
   - `full_content=<content-file text>`
   - `full_content_sha256=<hash>`
   - `approval_mode="approve"`
   - `presented_to_user=true`
   - `transcript_captured=true`
   - `explicit_change_request="AUQ <auq-id>: <auq-answer>"`
   - `approved_by=<--approved-by or "owner">`
   - `changed_by=<resolved harness identity, fallback "gt-cli">`
   - `change_reason=<--change-reason>`
6. Call `validate_packet(packet)` before writing any packet file or DB row.
7. Write the packet to `.groundtruth/formal-artifact-approvals/<date>-<artifact-id>.json`.
8. Call `KnowledgeDB.insert_deliberation()` with the planned id, after one final collision check. If a collision is detected, recompute the id and regenerate/revalidate the packet once.
9. Print the created or existing `DELIB-NNNN` id.

`--dry-run` performs steps 1-6 and prints the proposed packet and DB operation. It does not write a packet file and does not call the DB.

### IP-5: Tests

Add `platform_tests/groundtruth_kb/governance/test_approval_packet.py`:

- T-AP-1: valid manual approval packet passes.
- T-AP-2: packet missing `approved_by` or `acknowledged_by` fails.
- T-AP-3: hash mismatch fails.
- T-AP-4: `presented_to_user=false` fails.
- T-AP-5: `transcript_captured=false` fails.
- T-AP-6: auto mode requires owner-activated scope, preserving existing hook semantics even though `record` does not use auto mode in Slice 1.

Add `platform_tests/groundtruth_kb/cli/test_deliberations_record.py`:

- T-DR-1: invalid record call without `--owner-presented` exits non-zero before DB write.
- T-DR-2: invalid record call without `--auq-id` or `--auq-answer` exits non-zero before DB write.
- T-DR-3: constructed packet includes `approved_by`.
- T-DR-4: constructed packet hash matches the content file.
- T-DR-5: content file outside project root is rejected.
- T-DR-6: dry-run writes no packet and no DB row.
- T-DR-7: successful record call creates a packet and a DELIB row.
- T-DR-8: duplicate `(source_ref, content_hash)` returns the existing DELIB id and writes no second row.
- T-DR-9: `--approved-by` overrides the default manual identity.
- T-DR-10: exact Bash hook command string `python -m groundtruth_kb deliberations record ...` is not hook-matched, while the same CLI invocation still blocks through in-process validation when approval evidence is missing.

Update `platform_tests/hooks/test_formal_artifact_approval_gate.py`:

- T-HOOK-1: existing `add`/`upsert` commands still block without packet.
- T-HOOK-2: existing valid packet still allows lower-level commands.
- T-HOOK-3: hook and library return the same pass/fail results for representative packet fixtures.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/cli.py` - modified; add `record` subcommand registration and handler wiring.
- `groundtruth-kb/src/groundtruth_kb/cli/_deliberations_record.py` - new; implementation of the high-level command.
- `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py` - new; shared packet construction/validation.
- `groundtruth-kb/src/groundtruth_kb/governance/__init__.py` - modified; export the new validation module.
- `.claude/hooks/formal-artifact-approval-gate.py` - modified; use shared validation logic without adding `record` to formal mutation patterns.
- `platform_tests/groundtruth_kb/governance/test_approval_packet.py` - new.
- `platform_tests/groundtruth_kb/cli/test_deliberations_record.py` - new.
- `platform_tests/hooks/test_formal_artifact_approval_gate.py` - modified.

No source file outside `E:\GT-KB` is in scope. No Agent Red live artifact is in scope.

## Test Plan

Pre-implementation review gates:

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-1-deliberations-record`
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-artifact-recorder-cli-slice-1-deliberations-record`

Implementation verification:

3. `python -m pytest platform_tests/groundtruth_kb/governance/test_approval_packet.py -q --tb=short`
4. `python -m pytest platform_tests/groundtruth_kb/cli/test_deliberations_record.py -q --tb=short`
5. `python -m pytest platform_tests/hooks/test_formal_artifact_approval_gate.py -q --tb=short`
6. `python -m pytest platform_tests/groundtruth_kb/ -q --tb=short -k "deliberation or approval_packet"`

Live smoke after implementation:

7. Run `python -m groundtruth_kb deliberations record` with AUQ evidence against an in-root content fixture; confirm packet file and DELIB row.
8. Re-run the same command and confirm the existing DELIB id is returned without a duplicate row.

## Spec-To-Test Mapping

| Spec | Verifying tests |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | preflight 1; T-DR-6 |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | preflight 1 |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | preflight 2; this table; implementation tests 3-8 |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | T-DR-5 |
| `GOV-ARTIFACT-APPROVAL-001` | T-AP-1 through T-AP-6; T-DR-1 through T-DR-4 |
| `PB-ARTIFACT-APPROVAL-001` | T-DR-3; T-DR-4; live smoke 7 |
| `ADR-ARTIFACT-FORMALIZATION-GATE-001` | T-HOOK-1 through T-HOOK-3 |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | T-HOOK-1 through T-HOOK-3 |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | live smoke 7 |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | live smoke 7 and 8 |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | T-DR-7; live smoke 8 |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | T-DR-7; live smoke 7 and 8 |

## Acceptance Criteria

- [ ] Applicability preflight passes with `missing_required_specs: []`.
- [ ] Clause preflight exits 0 with no blocking gaps.
- [ ] Loyal Opposition returns GO on this REVISED-2.
- [ ] Implementation adds the `record` command and shared approval-packet validator.
- [ ] Existing lower-level formal mutation hook behavior is preserved.
- [ ] Invalid approval evidence is rejected before any DB mutation.
- [ ] Valid AUQ-backed manual approval packet creates a packet file and a DELIB row.
- [ ] Re-running the same source/content returns the existing DELIB id.
- [ ] Post-implementation report carries forward this spec-to-test mapping.

## Risk And Rollback

Risk R1: Extracting hook validation could weaken existing hook behavior. Mitigation: retain existing hook tests and add hook/library equivalence tests.

Risk R2: Planned DELIB id allocation could race with another insert. Mitigation: perform a final collision check immediately before insert; on collision, recompute once and regenerate/revalidate the packet.

Risk R3: Defaulting `approved_by` to `owner` could hide missing AUQ evidence. Mitigation: default is allowed only when `--owner-presented`, `--auq-id`, and `--auq-answer` are all present; otherwise validation fails.

Rollback: revert the Slice 1 implementation commit. Existing `gt deliberations add` and `gt deliberations upsert` remain unchanged and continue to be hook-gated.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is not a bulk backlog or MemBase inventory operation. It creates one CLI service path and related tests. No `work_items` rows, `memory/work_list.md` rows, or bridge history files are bulk-updated. The formal-artifact-approval discipline applies per single deliberation record invocation.

## Bridge Protocol Compliance

This REVISED-2 file is appended as `bridge/gtkb-artifact-recorder-cli-slice-1-deliberations-record-005.md`, and `bridge/INDEX.md` receives a new `REVISED:` line at the top of this document's version chain. Prior versions are not edited or deleted.

## Recommended Commit Type

`feat:` - this slice adds a net-new high-level CLI capability and supporting governance validation module.

## Loyal Opposition Asks

1. Confirm the in-process-service topology closes F1 by removing the impossible same-command PreToolUse claim.
2. Confirm keeping `record` out of `FORMAL_MUTATION_PATTERNS` is acceptable because `record` validates before mutation while the hook continues to protect lower-level raw mutation surfaces.
3. Confirm the explicit AUQ evidence plus default `approved_by="owner"` contract closes F2 without weakening current packet validation.
4. Confirm the revised test plan proves the actual enforcement boundary rather than a simulated wrapper boundary.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
