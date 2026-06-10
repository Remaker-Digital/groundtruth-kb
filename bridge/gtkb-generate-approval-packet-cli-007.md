REVISED

# Implementation Proposal - gt generate-approval-packet CLI (Narrative-Artifact Focus) - REVISED-3 (WI-3279)

bridge_kind: prime_proposal
Document: gtkb-generate-approval-packet-cli
Version: 007
Responds to: bridge/gtkb-generate-approval-packet-cli-006.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BATCH
Project: PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS
Work Item: WI-3279

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py", "groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py", "groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py", "platform_tests/groundtruth_kb/cli/test_generate_approval_packet.py"]

This REVISED-3 (`-007`) implements `WI-3279`: a deterministic `gt generate-approval-packet` CLI that builds an approval packet (narrative-artifact or formal-artifact) bound to the exact target-file content — including the LF-normalization, LF-preserving packet write, and optional staging that make the packet survive the Windows newline failure modes WI-3279 was created to remove.

## Revision Notes

This `-007` REVISED-3 addresses the single finding in the `-006` NO-GO. The `-005` REVISED-2 fixes (narrative packet schema matching the live gate; `full_content_sha256` test) were confirmed closed by the `-006` review and are carried forward unchanged. The earlier `-003` F1 fix (CLI registration target-path) likewise carries forward unchanged.

- **F1 (P1) — WI-3279's staging and LF-preservation requirement was missing from the proposal.** Resolved. The live WI-3279 row describes the manual friction as four steps — (a) text-mode LF-normalized read, (b) sha256 of UTF-8 LF bytes, (c) `write_bytes` to preserve LF on Windows since `write_text` re-introduces CRLF, (d) `git add` to expose the staged blob hash for `scripts/check_narrative_artifact_evidence.py` — and asks for a CLI handling normalization + hash computation + JSON packet write + optional staging. The `-005` proposal instead stated `full_content` is read "verbatim (no normalization)" and exposed no staging option. `-007` reverses both:
  - **LF-normalized target read.** The narrative builder now reads the target file and normalizes line endings to LF (`CRLF`/`CR` -> `LF`) before computing `full_content`. `full_content_sha256` is therefore the sha256 of UTF-8-encoded LF bytes — the deterministic, platform-independent hash WI-3279 step (b) calls for. This is consistent with the live gates: both `.claude/hooks/narrative-artifact-approval-gate.py:186-188` and `scripts/check_narrative_artifact_evidence.py:147-149` recompute `sha256(full_content.encode("utf-8"))` from the packet's own `full_content`, so an LF-normalized `full_content` keeps the packet internally consistent; and the evidence checker additionally requires that hash to equal the **staged git blob's raw-bytes sha256** (`check_narrative_artifact_evidence.py:154-159`), which only matches when the staged blob bytes are LF. See the Verbatim-vs-LF correction in the Narrative Packet Schema section.
  - **LF-preserving packet write.** The packet JSON is serialized and written with `Path.write_bytes(json_text.encode("utf-8"))` (LF in the JSON text preserved), not `write_text`, so the emitted packet file keeps LF on Windows. This is WI-3279 step (c) applied to the packet artifact itself.
  - **Optional staging surface.** The CLI gains a `--stage/--no-stage` option (default `--no-stage`). When `--stage` is given for `--kind narrative`, after the packet is written the CLI runs `git add <target> <packet-path>` so the staged target blob is the LF content the packet hashed — WI-3279 step (d). This is what lets `scripts/check_narrative_artifact_evidence.py` find a staged blob whose sha256 equals the packet's `full_content_sha256`.
  - **Staging / LF tests.** The verification plan adds `test_narrative_target_read_normalizes_crlf` (a CRLF-on-disk target yields an LF-hash packet), `test_packet_file_written_with_lf` (the emitted packet JSON keeps LF bytes), `test_stage_flag_stages_target_and_packet` (`--stage` stages both files), and `test_emitted_packet_passes_evidence_checker_after_staging` (with `--stage`, the staged target's blob sha256 equals the packet `full_content_sha256` and `scripts/check_narrative_artifact_evidence.py` reports the path cleared). The pre-existing `test_emitted_packet_passes_evidence_checker` is retained for the validator-shape coverage but is no longer the sole evidence-checker test.

The `-006` review explicitly preferred this option ("implement the complete WI-3279 scope") over narrowing the claim, because the target paths already cover the CLI implementation and focused tests and the remaining work is local to those surfaces. `-007` takes that option; the acceptance criteria continue to claim full WI-3279 completion.

## Claim

`gt generate-approval-packet --kind narrative --target <path> --artifact-id <id> --action <create|update|delete> --source-ref <bridge-id|DELIB-id> --explicit-change-request <text> --change-reason <text> --approval-mode <approve|acknowledge|edit-and-approve|auto> --changed-by <harness-id> [--out <path>] [--stage/--no-stage]` produces a narrative-artifact approval packet whose JSON satisfies the live narrative-artifact gate. `full_content` is the LF-normalized target content; `full_content_sha256` is the sha256 of its UTF-8 LF bytes; the packet file is written LF-preserving; and `--stage` stages the target and packet so `scripts/check_narrative_artifact_evidence.py` sees a staged blob whose sha256 matches the packet. The `--kind formal` variant produces a formal-artifact-approval packet validated by the existing `validate_packet()` validator.

## In-Root Placement Evidence

All `target_paths` are inside `E:\GT-KB`. The packet output default `.groundtruth/formal-artifact-approvals/` is in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` - formal + narrative artifact approval discipline; the packet the CLI emits is the evidence record this governance requires.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - the approval-gate hook contract; the emitted packet must satisfy the hook's required-field validation and the staged-blob hash agreement the evidence checker enforces.
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
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - repetitive deterministic plumbing belongs in services, not sessions; the LF-normalization / hash / staging ceremony WI-3279 names is exactly such plumbing, and this CLI is its service.
- `DELIB-1901` - narrative-artifact-approval extension.
- `DELIB-1575` - verified narrative-artifact approval extension (cited in the `-004` review as the canonical narrative-artifact-extension deliberation).
- `DELIB-0835` - owner decision requiring full native-format artifact presentation and approval evidence; the packet's `full_content` field carries that full content.
- `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` - owner-visibility rule for approval / rejection with the full proposed artifact text.
- `bridge/gtkb-narrative-artifact-approval-extension-001-011.md` - the verified narrative-artifact bridge thread whose schema this CLI must emit.

No prior deliberation rejected a deterministic approval-packet generator; the `-006` NO-GO objected only that the proposal was narrower than the live WI-3279 definition, which `-007` corrects by implementing the full LF-normalization / staging scope.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by:

- 2026-05-14 UTC, S350: owner approved the `GTKB-APPROVAL-PACKET-ERGONOMICS` project authorization including WI-3279 (recorded as `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`).

No new owner decision is required for this revision; `-007` only widens the implementation to cover the LF-normalization and staging scope WI-3279 already specifies.

## Requirement Sufficiency

Existing requirements sufficient. WI-3279 specifies the deterministic approval-packet generation surface in full, including the four-step manual friction (LF-normalized read, sha256 of LF bytes, LF-preserving write, optional staging) the CLI must absorb. The narrative-artifact gate (`.claude/hooks/narrative-artifact-approval-gate.py`), its config (`config/governance/narrative-artifact-approval.toml`), and the evidence checker (`scripts/check_narrative_artifact_evidence.py`) already define the exact required packet shape and the staged-blob hash agreement; this proposal implements a generator that produces a packet satisfying all three. No new or revised requirement or specification is created.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-WI implementation proposal (WI-3279). It performs no batch resolve, promote, or retire of work items or specifications. References to "work item", "backlog", and "standing backlog" describe WI-3279 and its governed filing path only. The review-packet inventory is one bridge thread: IP-1 (CLI registration) + IP-2 (narrative builder) + IP-3 (formal builder) + IP-4 (tests). WI-3279's project membership is recorded under the formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-007` REVISED line is inserted under the existing `Document: gtkb-generate-approval-packet-cli` entry; the prior `-001` NEW, `-002` NO-GO, `-003` REVISED, `-004` NO-GO, `-005` REVISED, and `-006` NO-GO lines are preserved unchanged.

## Narrative Packet Schema (carried forward from -005; LF correction resolves -006 F1)

The narrative builder emits exactly the schema enforced by `config/governance/narrative-artifact-approval.toml` `[approval_packet]` and `.claude/hooks/narrative-artifact-approval-gate.py` `REQUIRED_PACKET_FIELDS`:

| Field | Source | Notes |
|---|---|---|
| `artifact_type` | constant | literal `"narrative_artifact"` |
| `artifact_id` | `--artifact-id` | stable id, e.g. `claude-rules-canonical-terminology-md` |
| `action` | `--action` | one of `create` / `update` / `delete` |
| `target_path` | `--target` | normalized to a project-root-relative POSIX path; the gate checks `Path(target).as_posix()` equals the write target |
| `source_ref` | `--source-ref` | bridge-id or DELIB reference authorizing the change |
| `full_content` | LF-normalized read of `--target` file | the full proposed file content with line endings normalized to LF (`CRLF`/`CR` -> `LF`) |
| `full_content_sha256` | computed | `hashlib.sha256(full_content.encode("utf-8")).hexdigest()` over the LF-normalized content — the deterministic UTF-8 LF-byte hash WI-3279 step (b) names; matches the gate recomputation at `narrative-artifact-approval-gate.py:186-188` and the evidence-checker recomputation at `check_narrative_artifact_evidence.py:147-149` |
| `approval_mode` | `--approval-mode` | one of `approve` / `acknowledge` / `edit-and-approve` / `auto` |
| `presented_to_user` | constant | `true` |
| `transcript_captured` | constant | `true` |
| `explicit_change_request` | `--explicit-change-request` | verbatim owner approval text |
| `changed_by` | `--changed-by` | harness identifier |
| `change_reason` | `--change-reason` | short rationale, typically cites the bridge thread |
| `approved_by` / `acknowledged_by` | derived from `approval_mode` | included when the approval mode requires owner confirmation |

**Verbatim-vs-LF correction (resolves -006 F1).** The `-005` proposal said `full_content` is read "verbatim (no normalization)". `-007` reverses that: `full_content` is the **LF-normalized** content of the target file. Rationale: `scripts/check_narrative_artifact_evidence.py:154-159` requires `packet["full_content_sha256"]` to equal the **staged git blob's raw-bytes sha256** (`_staged_blob_sha256` computes `sha256` over the raw bytes of `git show :<path>`). The repository's `.gitattributes` is currently empty (no `text=auto eol=lf` rule), so a target with CRLF bytes on disk stages a CRLF blob and a verbatim read would hash CRLF content — making the packet hash diverge from the staged-blob hash on Windows. By normalizing the read to LF AND staging the LF content (see the `--stage` flow), the packet's `full_content_sha256`, the gate recomputation, and the staged-blob sha256 all agree. The narrative-gate hook itself (`narrative-artifact-approval-gate.py`) only recomputes from `full_content`, so it is satisfied by any internally-consistent packet; LF normalization is what additionally makes the *evidence checker's* staged-blob comparison pass deterministically.

The packet is written to `.groundtruth/formal-artifact-approvals/<date>-<artifact_id>.json` (the `packet_directory` + `packet_filename_pattern` from the config); `--out` overrides the path when given. The packet file is written with `Path.write_bytes(json_text.encode("utf-8"))` so its own line endings stay LF on Windows. The CLI does NOT write to a separate `.groundtruth/narrative-artifact-approvals/` directory — that invented directory is removed.

## Staging and LF-Preservation (resolves -006 F1)

WI-3279's four-step manual ceremony is absorbed by the CLI as follows:

1. **LF-normalized read** — `narrative_artifact_packet` reads the target file with `encoding="utf-8"` and normalizes line endings to LF before computing `full_content`. This is WI-3279 step (a).
2. **sha256 of UTF-8 LF bytes** — `full_content_sha256 = hashlib.sha256(full_content.encode("utf-8")).hexdigest()`; because `full_content` is already LF-normalized, the digest is over LF bytes. This is WI-3279 step (b).
3. **LF-preserving write** — the packet JSON is serialized to a string with `json.dumps(..., indent=2)` (which emits `\n`) and written with `Path.write_bytes(json_text.encode("utf-8"))`. `write_text` is not used, because on Windows it re-introduces CRLF. This is WI-3279 step (c) applied to the packet artifact.
4. **Optional staging** — `--stage` (a flag; default `--no-stage`) instructs the CLI, after writing the packet, to run `git add <target> <packet-path>` from the project root. Staging the target makes the staged blob the LF content the packet hashed; staging the packet exposes it for evidence-checker discovery. This is WI-3279 step (d). `--no-stage` leaves the working tree untouched (for callers who stage separately or run in a non-git context); the default is `--no-stage` so the CLI never mutates git index state unless explicitly asked.

When `--stage` is used, `scripts/check_narrative_artifact_evidence.py` evaluating the staged target will: read the staged blob, compute its raw-bytes sha256 (which equals the packet `full_content_sha256` because the staged content is LF), find the packet under `.groundtruth/formal-artifact-approvals/` by matching `target_path` + `full_content_sha256`, validate the packet, and report the path cleared. A test exercises exactly this path.

## Proposed Scope

### IP-1: CLI command registration in cli.py (carryforward — confirmed by -004)

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
@click.option("--stage/--no-stage", default=False, show_default=True,
              help="For --kind narrative: git add the target and packet after writing, so the evidence checker sees the staged blob.")
@click.option("--validate-after/--no-validate-after", default=True, show_default=True)
def generate_approval_packet(**kwargs):
    return _cli_approval_packet.run_generate(**kwargs)
```

### IP-2: Narrative-artifact packet builder (F1 closure — primary)

In `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py` (new module):

```python
def _read_lf_normalized(path: Path) -> str:
    """Read a file as UTF-8 and normalize line endings to LF (WI-3279 step a)."""
    raw = path.read_text(encoding="utf-8")
    return raw.replace("\r\n", "\n").replace("\r", "\n")


def build_narrative_packet(
    target_path: Path, artifact_id: str, action: str, source_ref: str,
    approval_mode: str, explicit_change_request: str, changed_by: str,
    change_reason: str, project_root: Path,
) -> dict:
    """Build a narrative-artifact packet per config/governance/narrative-artifact-approval.toml."""
    full_content = _read_lf_normalized(target_path)              # WI-3279 step (a)
    sha = hashlib.sha256(full_content.encode("utf-8")).hexdigest()  # WI-3279 step (b)
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


def write_packet(packet: dict, out_path: Path) -> None:
    """Write the packet JSON LF-preserving (WI-3279 step c — write_bytes, not write_text)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(packet, indent=2, ensure_ascii=False) + "\n"
    out_path.write_bytes(json_text.encode("utf-8"))
```

Default output path: `.groundtruth/formal-artifact-approvals/<date>-<artifact_id>.json`. `--validate-after` (default on) invokes `scripts/check_narrative_artifact_evidence.py` against the emitted packet to confirm it satisfies the narrative-gate evidence checker.

### IP-3: Formal-artifact packet builder + staging dispatch (--kind formal variant + --stage)

In `groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py` (new module):
- The `--kind formal` path builds a formal-artifact-approval packet (`artifact_type`, `artifact_id`, `action`, `source_ref`, `full_content`, `full_content_sha256`, `approval_mode`, `changed_by`, `change_reason`, plus `presented_to_user` / `transcript_captured`). Formal-packet `full_content` is read from `--content-file` and is likewise LF-normalized for hash determinism.
- It validates the built packet with the existing `groundtruth_kb.governance.approval_packet.validate_packet`.
- `cli_approval_packet.run_generate` dispatches on `--kind` to either builder, writes the JSON LF-preserving via `narrative_artifact_packet.write_packet` (shared writer), and optionally runs the post-write validation.
- When `--kind narrative` and `--stage` are set, `run_generate` runs `subprocess.run(["git", "add", str(target), str(out_path)], cwd=project_root, check=True)` after the packet is written (WI-3279 step d). On a non-zero git exit it surfaces a clear error; `--no-stage` skips this step entirely.

### IP-4: Tests in the live narrative-test layout

`platform_tests/groundtruth_kb/cli/test_generate_approval_packet.py`, co-located with the existing `test_deliberations_record.py` / `test_spec_record.py` recorder tests. The staging tests initialize a throwaway git repository in a `tmp_path` fixture so `git add` and `git show :<path>` operate against a real index without touching the GT-KB repository.

## Specification-Derived Verification Plan

Every linked specification maps to at least one test in `platform_tests/groundtruth_kb/cli/test_generate_approval_packet.py`.

| Linked spec | Behavior verified | Test |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt generate-approval-packet --help` resolves through the real `gt` console entrypoint | `test_command_registered_on_main_cli` |
| `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` | the narrative packet contains all 13 required fields from `config/governance/narrative-artifact-approval.toml` `[approval_packet].required_fields` | `test_narrative_packet_has_all_required_fields` |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | `full_content_sha256` equals `sha256(full_content.encode("utf-8"))` over the LF-normalized content — the exact gate computation | `test_narrative_full_content_sha256` |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | a target file containing CRLF line endings on disk yields a packet whose `full_content` and `full_content_sha256` are LF-normalized (WI-3279 step a/b) | `test_narrative_target_read_normalizes_crlf` |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | the emitted packet JSON file is written with LF line endings (no CRLF) — WI-3279 step c | `test_packet_file_written_with_lf` |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | `--kind narrative --stage` runs `git add` for both the target and the packet, so both appear staged — WI-3279 step d | `test_stage_flag_stages_target_and_packet` |
| `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` | after `--stage`, the staged target blob's sha256 equals the packet `full_content_sha256` and `scripts/check_narrative_artifact_evidence.py` reports the target path cleared | `test_emitted_packet_passes_evidence_checker_after_staging` |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | a narrative packet bound to a real `.claude/rules/*.md` file is accepted by the live `.claude/hooks/narrative-artifact-approval-gate.py` | `test_emitted_packet_passes_gate_hook` |
| `GOV-ARTIFACT-APPROVAL-001` | a narrative packet's schema passes `scripts/check_narrative_artifact_evidence.py` packet-validation logic | `test_emitted_packet_passes_evidence_checker` |
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
- Both bridge preflights PASS for this proposal (`-007`).
- `gt generate-approval-packet --help` resolves on the installed `gt` entrypoint.
- The narrative builder reads the target LF-normalized; a CRLF-on-disk target yields an LF-hash packet; a test proves it.
- The packet JSON file is written LF-preserving (`write_bytes`, not `write_text`); a test proves the emitted file has no CRLF.
- `--kind narrative --stage` runs `git add` for the target and the packet; a test proves both are staged.
- After `--stage`, the staged target blob's sha256 equals the packet `full_content_sha256` and `scripts/check_narrative_artifact_evidence.py` reports the path cleared; a test proves it.
- A narrative packet emitted for a real `.claude/rules/*.md` file passes the live `.claude/hooks/narrative-artifact-approval-gate.py`.
- The narrative packet contains all 13 required fields; `full_content_sha256` matches the gate's recomputation.
- The default packet directory is `.groundtruth/formal-artifact-approvals/`; the CLI does not create a separate `.groundtruth/narrative-artifact-approvals/` directory.
- `--kind formal` emits a packet passing `validate_packet()`.
- `ruff check` is clean on the touched files.

## Risks / Rollback

- Risk: the narrative-gate schema may evolve. Mitigation: the builder field set mirrors `config/governance/narrative-artifact-approval.toml`; a test asserts the emitted field set against that config so drift is caught.
- Risk: `--stage` mutates the caller's git index. Mitigation: `--stage` is opt-in and defaults to `--no-stage`; the CLI never touches git index state unless explicitly asked. The staging tests use a throwaway `tmp_path` git repository so test runs never stage GT-KB working-tree files.
- Risk: LF normalization changes content for a target that legitimately needs CRLF. Mitigation: narrative artifacts under `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE*.md`, and `memory/work_list.md` are text governance files; the evidence checker already documents (`check_narrative_artifact_evidence.py:150-159`) that the staged-blob comparison only works for LF content, so LF normalization is the required behavior for this artifact class, not a regression.
- Risk: `--kind formal` vs `narrative` coupling adds complexity. Mitigation: `--kind` is a required argument; the two builders are independent code paths with a shared LF-preserving writer and no shared mutable state.
- Risk: `full_content` of a large target file makes the packet large. Mitigation: acceptable — the gate requires the full content; the packet is a one-off evidence record, not a hot path.
- Rollback: revert the `@main.command` registration in `cli.py`; remove the two new modules (`cli_approval_packet.py`, `narrative_artifact_packet.py`). No existing surface is modified.

## Recommended Commit Type

`feat` - new `gt generate-approval-packet` CLI command plus a narrative-artifact builder module (with LF-normalized read, LF-preserving write, and optional staging) and a formal-artifact builder module; a new capability with no behavior change to existing surfaces.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-generate-approval-packet-cli`

- packet_hash: `sha256:4d04d0e80bfb0449f38d9d233fb0bfd00a4cb4c8fc783ef2558b5fa6cf0104e3`
- bridge_document_name: `gtkb-generate-approval-packet-cli`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-generate-approval-packet-cli-007.md`
- operative_file: `bridge/gtkb-generate-approval-packet-cli-007.md`
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
- Operative file: `bridge\gtkb-generate-approval-packet-cli-007.md`
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
