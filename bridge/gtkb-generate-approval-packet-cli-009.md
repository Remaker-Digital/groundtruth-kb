REVISED

# Implementation Proposal - gt generate-approval-packet CLI (Narrative-Artifact Focus) - REVISED-4 (WI-3279)

bridge_kind: prime_proposal
Document: gtkb-generate-approval-packet-cli
Version: 009
Responds to: bridge/gtkb-generate-approval-packet-cli-008.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S354+

Project Authorization: PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BATCH
Project: PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS
Work Item: WI-3279

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py", "groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py", "groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py", "platform_tests/groundtruth_kb/cli/test_generate_approval_packet.py"]

This REVISED-4 (`-009`) implements `WI-3279`: a deterministic `gt generate-approval-packet` CLI that builds an approval packet (narrative-artifact or formal-artifact) bound to the exact target-file content — including LF-normalization of the packet content and an LF-preserving packet write so the packet is internally deterministic across platforms, plus an optional staging convenience.

## Revision Notes

This `-009` REVISED-4 addresses the single finding in the `-008` NO-GO (round-4 review), and carries forward all `-007` (round-3), `-005` (round-2), and `-003` (round-1) fixes without regression.

### Round-4 NO-GO (`-008`) — finding-to-fix mapping

- **F1 (P1) — `--stage` does not guarantee the staged blob matches the LF-normalized packet content.** Resolved via the `-008` NO-GO's third acceptable shape (narrow the claim). The `-007` proposal claimed that `--stage` makes the staged target blob equal the LF-normalized packet content, so `scripts/check_narrative_artifact_evidence.py` would see a staged blob whose raw-byte sha256 matches the packet `full_content_sha256`. But the concrete `-007` implementation only runs `git add <target> <packet-path>`, and what bytes `git add` writes into the index is decided by local Git configuration (`core.autocrlf`) and `.gitattributes`, not by the CLI. With the repository's `.gitattributes` empty, a CRLF-on-disk target stages a CRLF blob unless ambient `core.autocrlf` happens to normalize it — so the `-007` claim was an assumption, not an implementation guarantee. This revision narrows the `--stage` claim to match what the implementation actually guarantees:
  - `--stage` is kept, and it still runs `git add <target> <packet-path>` as a **convenience** so the caller does not have to stage the two files manually. The implementation is unchanged in this respect.
  - Every statement that `--stage` *guarantees* `scripts/check_narrative_artifact_evidence.py` will see a staged blob whose sha256 matches the packet `full_content_sha256` is removed. The narrowed surfaces are `## Claim`, `## Staging and LF-Preservation` (renamed and rewritten), the acceptance criteria, and the verification-plan row for the staging evidence-checker test.
  - The proposal now states explicitly that deterministic agreement between the staged blob and the LF-normalized packet content requires the repository's narrative-artifact paths to be governed by a `.gitattributes` `eol=lf` rule, and that establishing that repo-level determinism is a separate named deferred follow-on (`## Deferred Follow-On - Repo-Wide Narrative-Artifact .gitattributes LF Rule`).
  - The `test_emitted_packet_passes_evidence_checker_after_staging` test is made **config-independent**: it sets up a `.gitattributes` rule inside its own throwaway test repository, so it proves "the packet + staging chain works in an LF-governed repo" rather than depending on the GT-KB checkout's ambient `core.autocrlf`.
  The genuine `-007` positives are kept unchanged: LF-normalized packet `full_content` and `full_content_sha256` (the packet is internally deterministic — the narrative-gate hook recomputes the hash from `full_content` alone), the LF-preserving packet-file `write_bytes`, and the live narrative-gate validation.

### Round-3 NO-GO (`-006`) fixes carried forward

- **F1 (P1) — WI-3279's LF-normalization and packet-write requirements were missing from the proposal.** Resolved and carried forward unchanged. The narrative builder reads the target file and normalizes line endings to LF (`CRLF`/`CR` -> `LF`) before computing `full_content`; `full_content_sha256` is the sha256 of UTF-8-encoded LF bytes — the deterministic, platform-independent hash WI-3279 calls for, and the value the live gate (`narrative-artifact-approval-gate.py:186-188`) and evidence checker (`check_narrative_artifact_evidence.py:147-149`) recompute from the packet's own `full_content`. The packet JSON is written with `Path.write_bytes(json_text.encode("utf-8"))` (LF preserved), not `write_text`, so the emitted packet file keeps LF on Windows. The `-005` REVISED-2 fixes (narrative packet schema matching the live gate; `full_content_sha256` test) were confirmed closed by the `-006` review and are carried forward unchanged. The earlier `-003` F1 fix (CLI registration target-path) likewise carries forward unchanged.

### Round-2 and round-1 fixes carried forward

- The `-005` REVISED-2 narrative packet schema (matching `config/governance/narrative-artifact-approval.toml` `[approval_packet]` and `narrative-artifact-approval-gate.py` `REQUIRED_PACKET_FIELDS`) carries forward unchanged.
- The `-003` REVISED CLI registration target-path (`cli.py` included in `target_paths`; the `@main.command` registration pattern) carries forward unchanged.

## Claim

`gt generate-approval-packet --kind narrative --target <path> --artifact-id <id> --action <create|update|delete> --source-ref <bridge-id|DELIB-id> --explicit-change-request <text> --change-reason <text> --approval-mode <approve|acknowledge|edit-and-approve|auto> --changed-by <harness-id> [--out <path>] [--stage/--no-stage]` produces a narrative-artifact approval packet whose JSON satisfies the live narrative-artifact gate. `full_content` is the LF-normalized target content; `full_content_sha256` is the sha256 of its UTF-8 LF bytes — the packet is therefore internally deterministic across platforms, and the narrative-gate hook (`narrative-artifact-approval-gate.py`), which recomputes the hash from `full_content` alone, is satisfied. The packet file is written LF-preserving. `--stage` is a convenience that runs `git add` on the target and the packet after writing, so the caller need not stage them manually. The `--kind formal` variant produces a formal-artifact-approval packet validated by the existing `validate_packet()` validator.

`--stage` does NOT by itself guarantee that the staged git blob of the target equals the LF-normalized packet content: what `git add` writes into the index is decided by the repository's `.gitattributes` and the caller's local `core.autocrlf`, not by this CLI. The evidence checker `scripts/check_narrative_artifact_evidence.py` additionally requires the staged blob's raw-byte sha256 to equal the packet `full_content_sha256`; that comparison passes deterministically only when the repository governs the narrative-artifact paths with a `.gitattributes` `eol=lf` rule. Establishing that repo-level determinism is out of scope for this proposal and is a separate named deferred follow-on (see `## Deferred Follow-On - Repo-Wide Narrative-Artifact .gitattributes LF Rule`).

## In-Root Placement Evidence

All `target_paths` are inside `E:\GT-KB`. The packet output default `.groundtruth/formal-artifact-approvals/` is in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` - formal + narrative artifact approval discipline; the packet the CLI emits is the evidence record this governance requires.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - the approval-gate hook contract; the emitted packet must satisfy the hook's required-field validation. The narrative-gate hook recomputes the hash from the packet's own `full_content`, so an LF-normalized internally-consistent packet satisfies it.
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
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - repetitive deterministic plumbing belongs in services, not sessions; the LF-normalization / hash / packet-write ceremony WI-3279 names is exactly such plumbing, and this CLI is its service.
- `DELIB-1901` - narrative-artifact-approval extension.
- `DELIB-1575` - verified narrative-artifact approval extension (cited in the `-004` review as the canonical narrative-artifact-extension deliberation).
- `DELIB-0835` - owner decision requiring full native-format artifact presentation and approval evidence; the packet's `full_content` field carries that full content.
- `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` - owner-visibility rule for approval / rejection with the full proposed artifact text.
- `bridge/gtkb-narrative-artifact-approval-extension-001-011.md` - the verified narrative-artifact bridge thread whose schema this CLI must emit.

No prior deliberation rejected a deterministic approval-packet generator. The `-008` NO-GO objected that the `-007` `--stage` claim promised deterministic staged-blob agreement that the implementation did not guarantee; `-009` corrects that by narrowing the claim to what the CLI actually guarantees and recording the repo-level `.gitattributes` determinism as a named deferred follow-on. The `-008` review confirmed no retrieved deliberation waives deterministic staged-blob agreement for this WI — `-009` does not waive it; it removes the claim that this CLI delivers it and assigns it to a follow-on.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by:

- 2026-05-14 UTC, S350: owner approved the `GTKB-APPROVAL-PACKET-ERGONOMICS` project authorization including WI-3279 (recorded as `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`).

No new owner decision is required for this revision. `-009` is a pure claim-narrowing revision: it narrows the `--stage` claim so the CLI no longer promises deterministic staged-blob LF agreement, records the repo-wide `.gitattributes` determinism as a named deferred follow-on, and makes the staging test config-independent. The genuine LF-normalization, LF-preserving-write, and live-gate-validation positives are carried forward unchanged; the `target_paths` are unchanged from `-007`.

## Requirement Sufficiency

Existing requirements sufficient. WI-3279 specifies the deterministic approval-packet generation surface, including LF-normalized read, sha256 of LF bytes, LF-preserving write, and an optional staging step the CLI should absorb. The narrative-artifact gate (`.claude/hooks/narrative-artifact-approval-gate.py`), its config (`config/governance/narrative-artifact-approval.toml`), and the evidence checker (`scripts/check_narrative_artifact_evidence.py`) define the required packet shape; this proposal implements a generator that produces a packet satisfying the gate and its config schema. Deterministic staged-blob LF agreement enforced by the evidence checker depends on a repository-level `.gitattributes` rule, which is a separate governed follow-on; no new or revised requirement or specification is created by this proposal.

## Deferred Follow-On - Repo-Wide Narrative-Artifact .gitattributes LF Rule

`scripts/check_narrative_artifact_evidence.py` compares the packet's `full_content_sha256` to the **staged git blob's raw-byte sha256** (`_staged_blob_sha256` hashes the raw bytes of `git show :<path>`). That comparison passes deterministically only when the staged blob bytes are LF. What bytes `git add` writes into the index for a narrative-artifact path is governed by the repository's `.gitattributes` and the caller's local `core.autocrlf` — not by this CLI. The repository's `.gitattributes` is currently empty, and `git check-attr text eol` reports `unspecified` for the protected narrative surfaces (`.claude/rules/*.md`, `AGENTS.md`, `memory/work_list.md`, etc.).

A `gt generate-approval-packet` CLI cannot make that evidence-checker comparison deterministic on its own. Doing so requires a repo-level change: adding a `.gitattributes` rule (e.g. `eol=lf` for the narrative-artifact path family) so `git add` always stages an LF blob for those paths regardless of the caller's `core.autocrlf`. That is a repository-governance change with its own blast radius (it affects how every contributor's Git stages those files, and may renormalize already-tracked blobs), and it deserves its own bridge proposal, in-root-placement evidence, and Loyal Opposition review.

This proposal therefore does NOT add a repo-wide `.gitattributes` change to its scope. Repo-wide narrative-artifact `.gitattributes` `eol=lf` governance is deferred to a separate NEW bridge implementation proposal. Suggested slug: `gtkb-narrative-artifact-gitattributes-lf`. That follow-on will add the `.gitattributes` rule for the narrative-artifact path family, include `.gitattributes` in its `target_paths`, and verify (in a throwaway repo with that rule, and against the live checkout after the rule lands) that a CRLF-on-disk narrative file stages an LF blob whose sha256 equals an LF-normalized packet hash. Once that follow-on lands, `--stage` from this CLI plus the governed `.gitattributes` rule together make the evidence-checker staged-blob comparison deterministic; until then, `--stage` remains a staging convenience and deterministic staged-blob agreement is not claimed.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-WI implementation proposal (WI-3279). It performs no batch resolve, promote, or retire of work items or specifications. References to "work item", "backlog", and "standing backlog" describe WI-3279 and its governed filing path only. The review-packet inventory is one bridge thread: IP-1 (CLI registration) + IP-2 (narrative builder) + IP-3 (formal builder + staging dispatch) + IP-4 (tests). WI-3279's project membership is recorded under the formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`.

## Bridge INDEX Maintenance

This proposal keeps `bridge/INDEX.md` as the canonical bridge workflow state. The `-009` REVISED line is inserted under the existing `Document: gtkb-generate-approval-packet-cli` entry; the prior `-001` NEW, `-002` NO-GO, `-003` REVISED, `-004` NO-GO, `-005` REVISED, `-006` NO-GO, `-007` REVISED, and `-008` NO-GO lines are preserved unchanged (append-only audit trail).

## Narrative Packet Schema (carried forward from -005; LF normalization carried forward from -007)

The narrative builder emits exactly the schema enforced by `config/governance/narrative-artifact-approval.toml` `[approval_packet]` and `.claude/hooks/narrative-artifact-approval-gate.py` `REQUIRED_PACKET_FIELDS`:

| Field | Source | Notes |
|---|---|---|
| `artifact_type` | constant | literal `"narrative_artifact"` |
| `artifact_id` | `--artifact-id` | stable id, e.g. `claude-rules-canonical-terminology-md` |
| `action` | `--action` | one of `create` / `update` / `delete` |
| `target_path` | `--target` | normalized to a project-root-relative POSIX path; the gate checks `Path(target).as_posix()` equals the write target |
| `source_ref` | `--source-ref` | bridge-id or DELIB reference authorizing the change |
| `full_content` | LF-normalized read of `--target` file | the full proposed file content with line endings normalized to LF (`CRLF`/`CR` -> `LF`) |
| `full_content_sha256` | computed | `hashlib.sha256(full_content.encode("utf-8")).hexdigest()` over the LF-normalized content — the deterministic UTF-8 LF-byte hash WI-3279 names; matches the gate recomputation at `narrative-artifact-approval-gate.py:186-188` and the evidence-checker recomputation at `check_narrative_artifact_evidence.py:147-149` |
| `approval_mode` | `--approval-mode` | one of `approve` / `acknowledge` / `edit-and-approve` / `auto` |
| `presented_to_user` | constant | `true` |
| `transcript_captured` | constant | `true` |
| `explicit_change_request` | `--explicit-change-request` | verbatim owner approval text |
| `changed_by` | `--changed-by` | harness identifier |
| `change_reason` | `--change-reason` | short rationale, typically cites the bridge thread |
| `approved_by` / `acknowledged_by` | derived from `approval_mode` | included when the approval mode requires owner confirmation |

**LF-normalization rationale (carried forward from -007).** `full_content` is the LF-normalized content of the target file, and `full_content_sha256` is the sha256 of its UTF-8 LF bytes. This makes the packet **internally deterministic**: the narrative-gate hook (`narrative-artifact-approval-gate.py:186-188`) and the evidence checker (`check_narrative_artifact_evidence.py:147-149`) both recompute `sha256(full_content.encode("utf-8"))` from the packet's own `full_content`, so an LF-normalized packet is internally consistent on every platform. The narrative-gate hook is satisfied by any such internally-consistent packet. The evidence checker imposes an *additional* check — `full_content_sha256` must also equal the **staged git blob's raw-byte sha256** (`check_narrative_artifact_evidence.py:154-159`) — and that additional check passes deterministically only when the staged blob is LF, which depends on the repository `.gitattributes` rule that is the deferred follow-on above. LF-normalizing `full_content` is necessary for the packet to be internally deterministic; it is not by itself sufficient to make the evidence checker's staged-blob comparison deterministic.

The packet is written to `.groundtruth/formal-artifact-approvals/<date>-<artifact_id>.json` (the `packet_directory` + `packet_filename_pattern` from the config); `--out` overrides the path when given. The packet file is written with `Path.write_bytes(json_text.encode("utf-8"))` so its own line endings stay LF on Windows. The CLI does NOT write to a separate `.groundtruth/narrative-artifact-approvals/` directory — that invented directory is removed.

## Staging and LF-Preservation

WI-3279's manual ceremony is absorbed by the CLI as follows:

1. **LF-normalized read** — `narrative_artifact_packet` reads the target file with `encoding="utf-8"` and normalizes line endings to LF before computing `full_content`. This is the LF-normalized-read step.
2. **sha256 of UTF-8 LF bytes** — `full_content_sha256 = hashlib.sha256(full_content.encode("utf-8")).hexdigest()`; because `full_content` is already LF-normalized, the digest is over LF bytes. This makes the packet internally deterministic.
3. **LF-preserving write** — the packet JSON is serialized to a string with `json.dumps(..., indent=2)` (which emits `\n`) and written with `Path.write_bytes(json_text.encode("utf-8"))`. `write_text` is not used, because on Windows it re-introduces CRLF. This keeps the emitted packet file's own line endings LF.
4. **Optional staging convenience** — `--stage` (a flag; default `--no-stage`) instructs the CLI, after writing the packet, to run `git add <target> <packet-path>` from the project root. This is a **convenience**: it saves the caller from staging the two files manually. `--no-stage` leaves the working tree untouched (for callers who stage separately or run in a non-git context); the default is `--no-stage` so the CLI never mutates git index state unless explicitly asked.

**What `--stage` does and does not guarantee.** `--stage` guarantees the target and the packet are passed to `git add`. It does NOT guarantee that the resulting staged blob of the target equals the LF-normalized packet content: the bytes `git add` writes into the index are decided by the repository's `.gitattributes` and the caller's local `core.autocrlf`, not by this CLI. The CLI does not rewrite the target's working-tree bytes to LF before staging and does not write a blob directly into the index. Therefore, `scripts/check_narrative_artifact_evidence.py` — which requires the staged blob's raw-byte sha256 to equal the packet `full_content_sha256` — will pass deterministically only when the repository governs the narrative-artifact paths with a `.gitattributes` `eol=lf` rule. That repo-level governance is the named deferred follow-on (`## Deferred Follow-On - Repo-Wide Narrative-Artifact .gitattributes LF Rule`). Until it lands, in a repository whose narrative-artifact paths are LF-governed (`.gitattributes` `eol=lf`), `--stage` plus the LF-normalized packet make the evidence-checker comparison pass; in a repository without that governance, the staged-blob comparison depends on ambient Git config and is not guaranteed by this CLI.

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
              help="For --kind narrative: convenience git add of the target and packet after writing. Does not by itself guarantee a staged blob whose sha256 matches the packet; see the proposal.")
@click.option("--validate-after/--no-validate-after", default=True, show_default=True)
def generate_approval_packet(**kwargs):
    return _cli_approval_packet.run_generate(**kwargs)
```

### IP-2: Narrative-artifact packet builder (LF normalization — primary)

In `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py` (new module):

```python
def _read_lf_normalized(path: Path) -> str:
    """Read a file as UTF-8 and normalize line endings to LF (WI-3279)."""
    raw = path.read_text(encoding="utf-8")
    return raw.replace("\r\n", "\n").replace("\r", "\n")


def build_narrative_packet(
    target_path: Path, artifact_id: str, action: str, source_ref: str,
    approval_mode: str, explicit_change_request: str, changed_by: str,
    change_reason: str, project_root: Path,
) -> dict:
    """Build a narrative-artifact packet per config/governance/narrative-artifact-approval.toml."""
    full_content = _read_lf_normalized(target_path)                 # LF-normalized read
    sha = hashlib.sha256(full_content.encode("utf-8")).hexdigest()  # sha256 of UTF-8 LF bytes
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
    """Write the packet JSON LF-preserving (write_bytes, not write_text)."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(packet, indent=2, ensure_ascii=False) + "\n"
    out_path.write_bytes(json_text.encode("utf-8"))
```

Default output path: `.groundtruth/formal-artifact-approvals/<date>-<artifact_id>.json`. `--validate-after` (default on) invokes `scripts/check_narrative_artifact_evidence.py` against the emitted packet to confirm it satisfies the narrative-gate evidence checker's packet-validation logic.

### IP-3: Formal-artifact packet builder + staging dispatch (--kind formal variant + --stage)

In `groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py` (new module):
- The `--kind formal` path builds a formal-artifact-approval packet (`artifact_type`, `artifact_id`, `action`, `source_ref`, `full_content`, `full_content_sha256`, `approval_mode`, `changed_by`, `change_reason`, plus `presented_to_user` / `transcript_captured`). Formal-packet `full_content` is read from `--content-file` and is likewise LF-normalized for hash determinism.
- It validates the built packet with the existing `groundtruth_kb.governance.approval_packet.validate_packet`.
- `cli_approval_packet.run_generate` dispatches on `--kind` to either builder, writes the JSON LF-preserving via `narrative_artifact_packet.write_packet` (shared writer), and optionally runs the post-write validation.
- When `--kind narrative` and `--stage` are set, `run_generate` runs `subprocess.run(["git", "add", str(target), str(out_path)], cwd=project_root, check=True)` after the packet is written — the staging convenience. On a non-zero git exit it surfaces a clear error; `--no-stage` skips this step entirely. The staging step does not rewrite the target or write a normalized blob into the index; deterministic staged-blob LF agreement depends on the repository `.gitattributes` rule that is the deferred follow-on.

### IP-4: Tests in the live narrative-test layout

`platform_tests/groundtruth_kb/cli/test_generate_approval_packet.py`, co-located with the existing `test_deliberations_record.py` / `test_spec_record.py` recorder tests. The staging tests initialize a throwaway git repository in a `tmp_path` fixture so `git add` and `git show :<path>` operate against a real index without touching the GT-KB repository. The `test_emitted_packet_passes_evidence_checker_after_staging` test additionally writes a `.gitattributes` rule into that throwaway repository so the test is config-independent (see the verification plan).

## Specification-Derived Verification Plan

Every linked specification maps to at least one test in `platform_tests/groundtruth_kb/cli/test_generate_approval_packet.py`.

| Linked spec | Behavior verified | Test |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `gt generate-approval-packet --help` resolves through the real `gt` console entrypoint | `test_command_registered_on_main_cli` |
| `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` | the narrative packet contains all 13 required fields from `config/governance/narrative-artifact-approval.toml` `[approval_packet].required_fields` | `test_narrative_packet_has_all_required_fields` |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | `full_content_sha256` equals `sha256(full_content.encode("utf-8"))` over the LF-normalized content — the exact gate computation | `test_narrative_full_content_sha256` |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | a target file containing CRLF line endings on disk yields a packet whose `full_content` and `full_content_sha256` are LF-normalized | `test_narrative_target_read_normalizes_crlf` |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | the emitted packet JSON file is written with LF line endings (no CRLF) | `test_packet_file_written_with_lf` |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` | `--kind narrative --stage` runs `git add` for both the target and the packet, so both appear staged (the staging convenience) | `test_stage_flag_stages_target_and_packet` |
| `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` | in a throwaway repo whose `.gitattributes` governs the target path with `eol=lf`, `--stage` produces a staged target blob whose sha256 equals the packet `full_content_sha256` and `scripts/check_narrative_artifact_evidence.py` reports the path cleared — config-independent because the test sets up the `.gitattributes` rule itself | `test_emitted_packet_passes_evidence_checker_after_staging` |
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
- Both bridge preflights PASS for this proposal (`-009`).
- `gt generate-approval-packet --help` resolves on the installed `gt` entrypoint.
- The narrative builder reads the target LF-normalized; a CRLF-on-disk target yields an LF-hash packet; a test proves it.
- The packet JSON file is written LF-preserving (`write_bytes`, not `write_text`); a test proves the emitted file has no CRLF.
- `--kind narrative --stage` runs `git add` for the target and the packet (the staging convenience); a test proves both are staged.
- In a throwaway repo whose `.gitattributes` governs the target path with `eol=lf`, after `--stage` the staged target blob's sha256 equals the packet `full_content_sha256` and `scripts/check_narrative_artifact_evidence.py` reports the path cleared; the test sets up the `.gitattributes` rule itself, so it is config-independent (round-4 F1 resolved by claim narrowing — the proposal does not claim `--stage` alone guarantees this in an ungoverned repo).
- A narrative packet emitted for a real `.claude/rules/*.md` file passes the live `.claude/hooks/narrative-artifact-approval-gate.py`.
- The narrative packet contains all 13 required fields; `full_content_sha256` matches the gate's recomputation.
- The default packet directory is `.groundtruth/formal-artifact-approvals/`; the CLI does not create a separate `.groundtruth/narrative-artifact-approvals/` directory.
- `--kind formal` emits a packet passing `validate_packet()`.
- `ruff check` is clean on the touched files.
- The proposal does not add a repo-wide `.gitattributes` change to its scope; repo-level narrative-artifact LF governance is explicitly deferred to a named follow-on proposal.

## Risks / Rollback

- Risk: the narrative-gate schema may evolve. Mitigation: the builder field set mirrors `config/governance/narrative-artifact-approval.toml`; a test asserts the emitted field set against that config so drift is caught.
- Risk: `--stage` mutates the caller's git index. Mitigation: `--stage` is opt-in and defaults to `--no-stage`; the CLI never touches git index state unless explicitly asked. The staging tests use a throwaway `tmp_path` git repository so test runs never stage GT-KB working-tree files.
- Risk: a caller expects `--stage` alone to make the evidence checker pass on an ungoverned repo. Mitigation: the proposal explicitly narrows the `--stage` claim and the `--stage` flag help text states `--stage` does not by itself guarantee a staged blob whose sha256 matches the packet; deterministic staged-blob agreement is the named deferred follow-on (`gtkb-narrative-artifact-gitattributes-lf`).
- Risk: LF normalization changes content for a target that legitimately needs CRLF. Mitigation: narrative artifacts under `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE*.md`, and `memory/work_list.md` are text governance files; the evidence checker already documents (`check_narrative_artifact_evidence.py:150-159`) that the staged-blob comparison only works for LF content, so LF normalization is the required behavior for this artifact class, not a regression.
- Risk: `--kind formal` vs `narrative` coupling adds complexity. Mitigation: `--kind` is a required argument; the two builders are independent code paths with a shared LF-preserving writer and no shared mutable state.
- Risk: `full_content` of a large target file makes the packet large. Mitigation: acceptable — the gate requires the full content; the packet is a one-off evidence record, not a hot path.
- Rollback: revert the `@main.command` registration in `cli.py`; remove the two new modules (`cli_approval_packet.py`, `narrative_artifact_packet.py`). No existing surface is modified.

## Recommended Commit Type

`feat` - new `gt generate-approval-packet` CLI command plus a narrative-artifact builder module (with LF-normalized read, LF-preserving write, and an optional staging convenience) and a formal-artifact builder module; a new capability with no behavior change to existing surfaces.

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-009` content after filing the INDEX entry; outputs are embedded in `## Applicability Preflight` and `## Clause Applicability` below.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-generate-approval-packet-cli`

- packet_hash: `sha256:1d0d3ad1643f9192140eca3e67e873d2451d24b5c4ebf21e401ea3508983f181`
- bridge_document_name: `gtkb-generate-approval-packet-cli`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-generate-approval-packet-cli-009.md`
- operative_file: `bridge/gtkb-generate-approval-packet-cli-009.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-generate-approval-packet-cli`

- Bridge id: `gtkb-generate-approval-packet-cli`
- Operative file: `bridge\gtkb-generate-approval-packet-cli-009.md`
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

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
