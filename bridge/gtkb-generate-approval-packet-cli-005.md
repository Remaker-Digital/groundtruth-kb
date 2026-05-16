REVISED

# Implementation Proposal - gt generate-approval-packet CLI (Narrative-Artifact Focus) - REVISED-2 (WI-3279)

bridge_kind: implementation_proposal
Document: gtkb-generate-approval-packet-cli
Version: 005
Responds to: bridge/gtkb-generate-approval-packet-cli-004.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BATCH
Project: PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS
Work Item: WI-3279

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py", "groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py", "groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py", "platform_tests/groundtruth_kb/cli/test_generate_approval_packet.py"]

This REVISED-2 (`-005`) implements `WI-3279`: a deterministic `gt generate-approval-packet` CLI that builds an approval packet (narrative-artifact or formal-artifact) bound to the exact target-file content, removing the manual packet-authoring friction.

## Revision Notes

This `-005` REVISED-2 addresses every finding in the `-004` NO-GO:

- **F1 (P1) — the proposed narrative packet schema did not satisfy the live narrative-artifact gate.** Resolved. IP-2 is rewritten to emit the **exact** narrative-artifact packet schema enforced by `config/governance/narrative-artifact-approval.toml` `[approval_packet]` and `.claude/hooks/narrative-artifact-approval-gate.py` `REQUIRED_PACKET_FIELDS`. The builder now emits all 13 required fields — `artifact_type` (literal `narrative_artifact`), `artifact_id`, `action`, `target_path`, `source_ref`, `full_content`, `full_content_sha256`, `approval_mode`, `presented_to_user`, `transcript_captured`, `explicit_change_request`, `changed_by`, `change_reason` — plus `approved_by` / `acknowledged_by` as the `approval_mode` requires. The invented `target_content_sha256` and `source_bridge_id` fields are removed. The default output directory is now `.groundtruth/formal-artifact-approvals/<date>-<artifact_id>.json` per `packet_directory` and `packet_filename_pattern` in the config. The `--target-content-sha256`-style flag is gone; the CLI exposes `--artifact-id`, `--action`, `--source-ref`, `--approval-mode`, and `--changed-by` so every required field has a deterministic source. See the updated IP-1 / IP-2 and the Narrative Packet Schema section.
- **F2 (P1) — the test mapping preserved the wrong field name.** Resolved. The SHA test is renamed `test_narrative_full_content_sha256` and asserts `full_content_sha256` equals `sha256(full_content.encode("utf-8"))` (the exact computation the live gate performs at `narrative-artifact-approval-gate.py:186-188`). The test plan now requires two validator-exercising tests: (a) direct packet-schema validation against the required-field set from `config/governance/narrative-artifact-approval.toml`, and (b) live behavior against `.claude/hooks/narrative-artifact-approval-gate.py` and `scripts/check_narrative_artifact_evidence.py`. See the Specification-Derived Verification Plan.
- **Advisory preflight omissions (carried from the `-002` F1 / surfaced again in the `-004` preflight).** Resolved. `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` are now cited in `## Specification Links`. Both preflights were re-run on this `-005` content; results are embedded in `## Applicability Preflight` and `## Clause Applicability`.

The prior `-003` F1 fix (CLI registration target-path) is confirmed resolved by the `-004` review and is carried forward unchanged.

## Claim

`gt generate-approval-packet --kind narrative --target <path> --artifact-id <id> --action <create|update|delete> --source-ref <bridge-id|DELIB-id> --explicit-change-request <text> --change-reason <text> --approval-mode <approve|acknowledge|edit-and-approve|auto> --changed-by <harness-id> [--out <path>]` produces a narrative-artifact approval packet whose JSON satisfies the live narrative-artifact gate. The `--kind formal` variant produces a formal-artifact-approval packet validated by the existing `validate_packet()` validator.

## In-Root Placement Evidence

All `target_paths` are inside `E:\GT-KB`. The packet output default `.groundtruth/formal-artifact-approvals/` is in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` - formal + narrative artifact approval discipline; the packet the CLI emits is the evidence record this governance requires.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - the approval-gate hook contract; the emitted packet must satisfy the hook's required-field validation.
- `SPEC-AUQ-POLICY-ENGINE-001` - the CLI is a deterministic surface in the artifact-approval toolchain.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority governing this proposal.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below derives every test from a linked spec.
- `GOV-STANDING-BACKLOG-001` - WI-3279 is tracked as a member of an authorized project.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; the packet is a governed artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; WI, bridge thread, packet, and linked specs form the artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the CLI lowers the cost of the approval-packet lifecycle step.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 owner authorization for `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS` and WI-3279.
- `DELIB-1901` - narrative-artifact-approval extension.
- `DELIB-1575` - verified narrative-artifact approval extension (cited in the `-004` review as the canonical narrative-artifact-extension deliberation).
- `DELIB-0835` - owner decision requiring full native-format artifact presentation and approval evidence; the packet's `full_content` field carries that full content.
- `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` - owner-visibility rule for approval / rejection with the full proposed artifact text.
- `bridge/gtkb-narrative-artifact-approval-extension-001-011.md` - the verified narrative-artifact bridge thread whose schema this CLI must emit.

No prior deliberation rejected a deterministic approval-packet generator; the `-004` NO-GO objected only to schema mismatch, which `-005` corrects.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by:

- 2026-05-14 UTC, S350: owner approved the `GTKB-APPROVAL-PACKET-ERGONOMICS` project authorization including WI-3279 (recorded as `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`).

No new owner decision is required for this revision; `-005` only corrects the packet schema to match an already-governed gate.

## Requirement Sufficiency

Existing requirements sufficient. WI-3279 specifies deterministic approval-packet generation as the operative friction. The narrative-artifact gate (`.claude/hooks/narrative-artifact-approval-gate.py`) and its config (`config/governance/narrative-artifact-approval.toml`) already define the exact required packet shape; this proposal implements a generator that emits that shape. No new or revised requirement or specification is created.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-WI implementation proposal (WI-3279). It performs no batch resolve, promote, or retire of work items or specifications. References to "work item", "backlog", and "standing backlog" describe WI-3279 and its governed filing path only. The review-packet inventory is one bridge thread: IP-1 (CLI registration) + IP-2 (narrative builder) + IP-3 (formal builder) + IP-4 (tests). WI-3279's project membership is recorded under the formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-005` REVISED line is inserted under the existing `Document: gtkb-generate-approval-packet-cli` entry; the prior `-001` NEW, `-002` NO-GO, `-003` REVISED, and `-004` NO-GO lines are preserved unchanged.

## Narrative Packet Schema (resolves F1)

The narrative builder emits exactly the schema enforced by `config/governance/narrative-artifact-approval.toml` `[approval_packet]` and `.claude/hooks/narrative-artifact-approval-gate.py` `REQUIRED_PACKET_FIELDS`:

| Field | Source | Notes |
|---|---|---|
| `artifact_type` | constant | literal `"narrative_artifact"` |
| `artifact_id` | `--artifact-id` | stable id, e.g. `claude-rules-canonical-terminology-md` |
| `action` | `--action` | one of `create` / `update` / `delete` |
| `target_path` | `--target` | normalized to a project-root-relative POSIX path; the gate checks `Path(target).as_posix()` equals the write target |
| `source_ref` | `--source-ref` | bridge-id or DELIB reference authorizing the change |
| `full_content` | read from `--target` file | the full proposed file content, verbatim (no normalization) |
| `full_content_sha256` | computed | `hashlib.sha256(full_content.encode("utf-8")).hexdigest()` — the exact computation the gate performs at `narrative-artifact-approval-gate.py:186-188` |
| `approval_mode` | `--approval-mode` | one of `approve` / `acknowledge` / `edit-and-approve` / `auto` |
| `presented_to_user` | constant | `true` |
| `transcript_captured` | constant | `true` |
| `explicit_change_request` | `--explicit-change-request` | verbatim owner approval text |
| `changed_by` | `--changed-by` | harness identifier |
| `change_reason` | `--change-reason` | short rationale, typically cites the bridge thread |
| `approved_by` / `acknowledged_by` | derived from `approval_mode` | included when the approval mode requires owner confirmation |

`full_content` is read verbatim from the target file (no CRLF→LF normalization), so `full_content_sha256` matches the gate's byte-exact recomputation. The packet is written to `.groundtruth/formal-artifact-approvals/<date>-<artifact_id>.json` (the `packet_directory` + `packet_filename_pattern` from the config); `--out` overrides the path when given. The CLI does NOT write to a separate `.groundtruth/narrative-artifact-approvals/` directory — that invented directory is removed.

## Proposed Scope

### IP-1: CLI command registration in cli.py (F1 carryforward — confirmed by -004)

In `groundtruth-kb/src/groundtruth_kb/cli.py`, register the new command following the existing `@main.command()` pattern:

```python
from groundtruth_kb import cli_approval_packet as _cli_approval_packet

@main.command("generate-approval-packet")
@click.option("--kind", type=click.Choice(["formal", "narrative"]), required=True)
@click.option("--target", type=click.Path(exists=True), help="For --kind narrative: the target file being approved.")
@click.option("--content-file", type=click.Path(exists=True), help="For --kind formal: file whose content becomes full_content.")
@click.option("--artifact-type", help="For --kind formal: governance|requirement|deliberation|...")
@click.option("--artifact-id", required=True, help="Stable artifact id.")
@click.option("--action", type=click.Choice(["create", "update", "delete"]), default="update", show_default=True)
@click.option("--source-ref", required=True, help="Bridge-id or DELIB reference authorizing this packet.")
@click.option("--approval-mode", type=click.Choice(["approve", "acknowledge", "edit-and-approve", "auto"]), default="approve", show_default=True)
@click.option("--explicit-change-request", required=True)
@click.option("--changed-by", required=True, help="Harness identifier, e.g. prime-builder/claude/B.")
@click.option("--change-reason", required=True)
@click.option("--out", type=click.Path(), help="Output path; defaults to .groundtruth/formal-artifact-approvals/<date>-<artifact_id>.json")
@click.option("--validate-after/--no-validate-after", default=True, show_default=True)
def generate_approval_packet(**kwargs):
    return _cli_approval_packet.run_generate(**kwargs)
```

### IP-2: Narrative-artifact packet builder (F1 closure — primary)

In `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py` (new module):

```python
def build_narrative_packet(
    target_path: Path, artifact_id: str, action: str, source_ref: str,
    approval_mode: str, explicit_change_request: str, changed_by: str,
    change_reason: str, project_root: Path,
) -> dict:
    """Build a narrative-artifact packet per config/governance/narrative-artifact-approval.toml."""
    full_content = target_path.read_text(encoding="utf-8")  # verbatim, no normalization
    sha = hashlib.sha256(full_content.encode("utf-8")).hexdigest()
    packet = {
        "artifact_type": "narrative_artifact",
        "artifact_id": artifact_id,
        "action": action,
        "target_path": target_path.resolve().relative_to(project_root).as_posix(),
        "source_ref": source_ref,
        "full_content": full_content,
        "full_content_sha256": sha,
        "approval_mode": approval_mode,
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": explicit_change_request,
        "changed_by": changed_by,
        "change_reason": change_reason,
    }
    if approval_mode in ("approve", "edit-and-approve"):
        packet["approved_by"] = "owner"
    elif approval_mode == "acknowledge":
        packet["acknowledged_by"] = "owner"
    return packet
```

Default output path: `.groundtruth/formal-artifact-approvals/<date>-<artifact_id>.json`. `--validate-after` (default on) invokes `scripts/check_narrative_artifact_evidence.py` against the emitted packet to confirm it satisfies the narrative-gate evidence checker.

### IP-3: Formal-artifact packet builder (--kind formal variant)

In `groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py` (new module):
- The `--kind formal` path builds a formal-artifact-approval packet (`artifact_type`, `artifact_id`, `action`, `source_ref`, `full_content`, `full_content_sha256`, `approval_mode`, `changed_by`, `change_reason`, plus `presented_to_user` / `transcript_captured`).
- It validates the built packet with the existing `groundtruth_kb.governance.approval_packet.validate_packet`.
- `cli_approval_packet.run_generate` dispatches on `--kind` to either builder, writes the JSON, and optionally runs the post-write validation.

### IP-4: Tests in the live narrative-test layout

`platform_tests/groundtruth_kb/cli/test_generate_approval_packet.py`, co-located with the existing `test_deliberations_record.py` / `test_spec_record.py` recorder tests.

## Specification-Derived Verification Plan

Every linked specification maps to at least one test in `platform_tests/groundtruth_kb/cli/test_generate_approval_packet.py`.

| Linked spec | Behavior verified | Test |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt generate-approval-packet --help` resolves through the real `gt` console entrypoint | `test_command_registered_on_main_cli` |
| `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` | the narrative packet contains all 13 required fields from `config/governance/narrative-artifact-approval.toml` `[approval_packet].required_fields` | `test_narrative_packet_has_all_required_fields` |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | `full_content_sha256` equals `sha256(full_content.encode("utf-8"))` — the exact gate computation | `test_narrative_full_content_sha256` |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | a narrative packet bound to a real `.claude/rules/*.md` file is accepted by the live `.claude/hooks/narrative-artifact-approval-gate.py` | `test_emitted_packet_passes_gate_hook` |
| `GOV-ARTIFACT-APPROVAL-001` | a narrative packet passes `scripts/check_narrative_artifact_evidence.py` | `test_emitted_packet_passes_evidence_checker` |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | the packet's `artifact_type` is the literal `narrative_artifact` and `approval_mode` is a member of the valid set | `test_narrative_artifact_type_and_mode` |
| `GOV-ARTIFACT-APPROVAL-001` | default output path is `.groundtruth/formal-artifact-approvals/<date>-<artifact_id>.json`; `--out` overrides it | `test_out_path_default_and_override` |
| `SPEC-AUQ-POLICY-ENGINE-001` | missing `--target` for `--kind narrative` fails with a clear error | `test_narrative_missing_target_fails` |
| `GOV-ARTIFACT-APPROVAL-001` | `--kind formal` emits a packet that passes `groundtruth_kb.governance.approval_packet.validate_packet` | `test_formal_packet_passes_validate_packet` |
| `SPEC-AUQ-POLICY-ENGINE-001` | `--kind formal` with an invalid `artifact_type` is rejected | `test_formal_invalid_artifact_type_rejected` |
| `GOV-STANDING-BACKLOG-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | the generated packet is a complete governed artifact for the WI-tracked work | `test_narrative_packet_has_all_required_fields`, `test_emitted_packet_passes_gate_hook` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | the default packet path is in-root | `test_out_path_default_and_override` |

Run: `python -m pytest platform_tests/groundtruth_kb/cli/test_generate_approval_packet.py -v --tb=short`.

Lint: `python -m ruff check groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py`.

## Acceptance Criteria

- IP-1, IP-2, IP-3, IP-4 landed; all tests in `test_generate_approval_packet.py` PASS.
- Both bridge preflights PASS for this proposal (`-005`).
- `gt generate-approval-packet --help` resolves on the installed `gt` entrypoint.
- A narrative packet emitted for a real `.claude/rules/*.md` file passes the live `.claude/hooks/narrative-artifact-approval-gate.py` AND `scripts/check_narrative_artifact_evidence.py`.
- The narrative packet contains all 13 required fields; `full_content_sha256` matches the gate's recomputation.
- The default packet directory is `.groundtruth/formal-artifact-approvals/`; the CLI does not create a separate `.groundtruth/narrative-artifact-approvals/` directory.
- `--kind formal` emits a packet passing `validate_packet()`.
- `ruff check` is clean on the touched files.

## Risks / Rollback

- Risk: the narrative-gate schema may evolve. Mitigation: the builder field set mirrors `config/governance/narrative-artifact-approval.toml`; a test asserts the emitted field set against that config so drift is caught.
- Risk: `--kind formal` vs `narrative` coupling adds complexity. Mitigation: `--kind` is a required argument; the two builders are independent code paths with no shared mutable state.
- Risk: `full_content` of a large target file makes the packet large. Mitigation: acceptable — the gate requires the full content; the packet is a one-off evidence record, not a hot path.
- Rollback: revert the `@main.command` registration in `cli.py`; remove the two new modules. No existing surface is modified.

## Recommended Commit Type

`feat` - new `gt generate-approval-packet` CLI command plus a narrative-artifact builder module and a formal-artifact builder module; a new capability with no behavior change to existing surfaces.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-generate-approval-packet-cli`

- packet_hash: `sha256:c652baba6758f65a82215685b0b1753d3109af3cb5a7a02fc31df1dcc4b9cd40`
- bridge_document_name: `gtkb-generate-approval-packet-cli`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-generate-approval-packet-cli-005.md`
- operative_file: `bridge/gtkb-generate-approval-packet-cli-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-generate-approval-packet-cli`

- Bridge id: `gtkb-generate-approval-packet-cli`
- Operative file: `bridge\gtkb-generate-approval-packet-cli-005.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation); exit code `0`

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
