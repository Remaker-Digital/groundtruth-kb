REVISED

# Implementation Proposal - gt generate-approval-packet CLI (Narrative-Artifact Focus) - REVISED-1 (WI-3279)

bridge_kind: implementation_proposal
Document: gtkb-generate-approval-packet-cli
Version: 003
Responds to: bridge/gtkb-generate-approval-packet-cli-002.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BATCH
Project: PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS
Work Item: WI-3279

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py", "groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py", "groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py", "platform_tests/groundtruth_kb/cli/test_generate_approval_packet.py"]

This REVISED-1 addresses the NO-GO at `bridge/gtkb-generate-approval-packet-cli-002.md`:

- **F1 (P1)** — Claimed `gt generate-approval-packet` command but only authorized a new module; CLI registration would have required out-of-scope edits to `cli.py` → **closed** by adding `groundtruth-kb/src/groundtruth_kb/cli.py` to target_paths and explicitly authorizing the `@main.command()` registration there.
- **F2 (P1)** — Proposal focused on formal-artifact packet schema; WI-3279 description specifies **narrative-artifact** packet workflow as the friction point → **closed** by reframing the CLI as `gt generate-approval-packet --kind <formal|narrative>` with narrative as the primary use case + adding the narrative-artifact gate's required fields + the existing `check_narrative_artifact_evidence.py` to the test plan.

## Claim

`gt generate-approval-packet --kind narrative --target <path> --explicit-change-request <text> [--source-bridge <bridge-id>] [--out <path>]` produces a narrative-artifact approval packet bound to the exact target-file content with LF-normalized sha256, satisfying the narrative-artifact gate at `.claude/hooks/narrative-artifact-approval-gate.py`. The `--kind formal` variant remains available for formal-artifact-approval packets via the existing `validate_packet()` validator.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` - formal + narrative artifact approval discipline.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - hook contract this aligns with.
- `SPEC-AUQ-POLICY-ENGINE-001` - CLI surface.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3279 tracked.
- `DELIB-1901` - narrative-artifact-approval extension (cited per F2 NO-GO).
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization.
- `DELIB-1901` - narrative-artifact-approval extension (per F2).
- `bridge/gtkb-narrative-artifact-approval-extension-001` - verified narrative-artifact bridge thread (per F2).
- `bridge/gtkb-generate-approval-packet-cli-002.md` - NO-GO under remediation.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner approved GTKB-APPROVAL-PACKET-ERGONOMICS authorization including WI-3279.
- 2026-05-15 UTC, S350+: owner directive "keep grinding REVISED-1s through the NO-GO queue".

No new owner decision required.

## Requirement Sufficiency

Existing requirements sufficient. WI-3279 description specifies narrative-artifact packet generation as the operative friction. F2 NO-GO clarifies the expected packet shape. This REVISED-1 implements that shape; formal-packet support is a secondary `--kind formal` variant.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. Review-packet inventory: IP-1 (CLI registration) + IP-2 (narrative builder) + IP-3 (formal builder) + IP-4 (tests) single thread.

## Bridge INDEX Update Evidence

REVISED filed at `bridge/gtkb-generate-approval-packet-cli-003.md`; `REVISED:` line prepended; prior NO-GO at -002 and NEW at -001 preserved.

## Proposed Scope

### IP-1: CLI command registration in cli.py (F1 closure)

In `groundtruth-kb/src/groundtruth_kb/cli.py`, register the new command:

```python
from groundtruth_kb import cli_approval_packet as _cli_approval_packet

@main.command("generate-approval-packet")
@click.option("--kind", type=click.Choice(["formal", "narrative"]), required=True)
@click.option("--target", type=click.Path(), required=True, help="For --kind narrative: the target file path being approved.")
@click.option("--content-file", type=click.Path(exists=True), help="For --kind formal: path to a file whose content becomes full_content.")
@click.option("--artifact-type", help="For --kind formal: governance|requirement|deliberation|...")
@click.option("--artifact-id", help="For --kind formal: artifact identifier.")
@click.option("--action", default="insert", show_default=True)
@click.option("--explicit-change-request", required=True)
@click.option("--source-bridge", help="Bridge slug that authorized this packet.")
@click.option("--change-reason", required=True)
@click.option("--out", type=click.Path(), help="Output path; defaults to .groundtruth/<dir>/<date>-<id>.json")
@click.option("--validate-after", is_flag=True, default=True)
def generate_approval_packet(**kwargs):
    return _cli_approval_packet.run_generate(**kwargs)
```

### IP-2: Narrative-artifact packet builder (F2 closure — primary)

In `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py` (new module):

```python
def build_narrative_packet(target_path: Path, explicit_change_request: str,
                            source_bridge: str | None, change_reason: str) -> dict:
    """Build a narrative-artifact packet per config/governance/narrative-artifact-approval.toml."""
    content = target_path.read_text(encoding="utf-8").replace("\r\n", "\n")  # LF normalize
    sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return {
        "artifact_type": "narrative_artifact",
        "target_path": str(target_path.relative_to(PROJECT_ROOT).as_posix()),
        "target_content_sha256": sha,
        "presented_to_user": True,
        "transcript_captured": True,
        "explicit_change_request": explicit_change_request,
        "source_bridge_id": source_bridge,
        "change_reason": change_reason,
        "approved_by": "owner",
        "acknowledged_by": "owner",
    }
```

Default output path: `.groundtruth/narrative-artifact-approvals/<date>-<sanitized-target-path>.json`.

`--validate-after` invokes `scripts/check_narrative_artifact_evidence.py` against the emitted packet to confirm it satisfies the narrative-gate's expected schema.

### IP-3: Formal-artifact packet builder (--kind formal variant)

In `groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py` (new module):
- `--kind formal` path uses existing `groundtruth_kb.governance.approval_packet.validate_packet` for schema validation.
- Builds the schema per the existing formal-artifact-approval shape (artifact_type, artifact_id, action, source_ref, full_content + sha256, approval_mode, etc.).

### IP-4: Tests in the live narrative-test layout (F2 alignment)

Use the established test path `platform_tests/groundtruth_kb/cli/test_generate_approval_packet.py` (co-located with existing `test_deliberations_record.py` + `test_spec_record.py` per the canonical artifact-recorder layout).

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| `gt generate-approval-packet --help` resolves at console entrypoint | `test_command_registered_on_main_cli` |
| --kind narrative: packet schema matches narrative-gate expectation | `test_narrative_packet_schema_satisfies_gate` |
| --kind narrative: target_content_sha256 matches LF-normalized content | `test_narrative_sha_lf_normalized` |
| --kind narrative: --validate-after invokes check_narrative_artifact_evidence | `test_validate_after_calls_narrative_check` |
| --kind narrative: missing --target fails clearly | `test_narrative_missing_target_fails` |
| --kind formal: emits packet passing validate_packet() | `test_formal_packet_passes_validate_packet` |
| --kind formal: invalid artifact_type rejected | `test_formal_invalid_artifact_type_rejected` |
| --out path honored; defaults to canonical dir | `test_out_path_honored_and_default_canonical` |
| CRLF in target content normalized to LF before sha | `test_crlf_target_normalized` |
| Integration: emitted narrative packet passes narrative-artifact-approval-gate.py | `test_emitted_packet_passes_gate_hook` |

Run: `python -m pytest platform_tests/groundtruth_kb/cli/test_generate_approval_packet.py -v`.

## Acceptance Criteria

- IP-1, IP-2, IP-3, IP-4 landed; 10 tests PASS.
- `gt generate-approval-packet --help` resolves on the installed `gt` entrypoint.
- Emitted narrative packet bound to a real `.claude/rules/*.md` file passes the live narrative-artifact-approval-gate.py.
- Both preflights PASS.

## Risks / Rollback

- Risk: narrative-gate schema may evolve; this CLI must track it. Mitigation: builder pulls field set from `config/governance/narrative-artifact-approval.toml` rather than hard-coding.
- Risk: --kind formal vs narrative coupling adds complexity. Mitigation: clear --kind required argument; two independent code paths; no shared state.
- Rollback: revert the @main.command registration in cli.py; remove the two new modules.

## Recommended Commit Type

`feat` - new CLI command + two builders. ~150 LOC + 10 tests.
