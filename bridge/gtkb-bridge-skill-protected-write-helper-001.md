NEW

# Implementation Proposal - bridge-skill Protected-File Write Helper (WI-3281)

bridge_kind: implementation_proposal
Document: gtkb-bridge-skill-protected-write-helper
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350

Project Authorization: PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BATCH
Project: PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS
Work Item: WI-3281

target_paths: [".claude/skills/bridge/helpers/protected_write.py", ".claude/skills/bridge/SKILL.md", "tests/skills/test_protected_write_helper.py"]

This NEW proposal adds a bridge-skill helper that issues protected-file Writes with the proper `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` env var visible to the hook, eliminating the recurring blocked-Write friction observed when manually authoring narrative artifacts.

## Claim

Helper invocation: `python .claude/skills/bridge/helpers/protected_write.py --target <path> --content-file <path> --packet <packet-path>`. The helper sets the env var, validates the packet against the file's content-hash expectation, and performs the Write through a Python subprocess that the PreToolUse hook intercepts cleanly.

## In-Root Placement Evidence

All target paths in-root. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` - helper preserves the gate's evidence contract.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - helper sets the env var the hook validates.
- `SPEC-AUQ-POLICY-ENGINE-001` - policy engine surface.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge skill surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping.
- `GOV-STANDING-BACKLOG-001` - WI-3281 tracked.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - owner-decision evidence.

## Prior Deliberations

- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 authorization.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved GTKB-APPROVAL-PACKET-ERGONOMICS authorization including WI-3281.

## Requirement Sufficiency

Existing requirements sufficient. WI-3281 description specifies the helper need.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS per `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. Review-packet inventory: IP-1 + IP-2 + IP-3 single thread.

## Bridge INDEX Update Evidence

NEW filed; new top entry prepended to `bridge/INDEX.md`.

## Proposed Scope

### IP-1: Helper module

`.claude/skills/bridge/helpers/protected_write.py`:
1. Parse args: `--target`, `--content-file` (or `--content-stdin`), `--packet`.
2. Validate packet via `groundtruth_kb.governance.approval_packet.validate_packet`.
3. Confirm packet's `full_content_sha256` matches the content file's sha256.
4. Set `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET=<packet>` env var.
5. Write the content to target via `Path.write_text` (LF-normalized).
6. Exit 0 on success; non-zero with cited rule on failure.

### IP-2: SKILL.md update

In `.claude/skills/bridge/SKILL.md`, document the helper under a new "Protected-file Writes" section. Reference helper for any narrative artifact author flow.

### IP-3: Tests

Test fixture: a sample narrative-artifact target + matching packet; verify success path + 3 failure cases (bad packet, hash mismatch, missing target).

## Specification-Derived Verification Plan

| Behavior | Test |
|---|---|
| Success path with matching hash | `test_helper_writes_with_valid_packet` |
| Hash mismatch fails | `test_helper_rejects_hash_mismatch` |
| Invalid packet fails | `test_helper_rejects_invalid_packet` |
| Env var visible to subprocess | `test_helper_env_var_propagates` |
| LF normalization | `test_helper_lf_normalizes_content` |
| Skill markdown documents helper | `test_skill_md_references_helper` |

Run: `python -m pytest tests/skills/test_protected_write_helper.py -v`.

## Acceptance Criteria

- IP-1 helper landed; 5 helper tests PASS.
- IP-2 SKILL.md updated; 1 markdown test PASS.
- Both preflights PASS.

## Risks / Rollback

- Risk: env var leakage to other subprocesses. Mitigation: helper uses os.environ.copy + subprocess.run with explicit env dict.
- Rollback: remove helper script + revert SKILL.md.

## Recommended Commit Type

`feat` - new skill helper. ~70 LOC.
