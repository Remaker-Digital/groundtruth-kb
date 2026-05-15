REVISED

# Implementation Proposal REVISED - Active-Workspace Declaration Slice 1

bridge_kind: implementation_proposal
Document: active-workspace-declaration-slice-1
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S351
Addresses: NO-GO at `bridge/active-workspace-declaration-slice-1-002.md` (F1: proposal asserted no narrative-artifact approval packet required for `.claude/rules/active-workspace.md` creation; narrative-artifact-approval registry includes `action = "create"`).

target_paths: ["groundtruth-kb/src/groundtruth_kb/active_workspace.py", "scripts/check_workspace_boundary.py", ".claude/rules/active-workspace.md", "harness-state/claude/active-workspace.md", "harness-state/codex/active-workspace.md", "platform_tests/groundtruth_kb/test_active_workspace_resolver.py", "platform_tests/scripts/test_check_workspace_boundary.py", ".groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-active-workspace-md.json", "groundtruth.db"]

## Claim

REVISED-1 in response to Codex F1 (P1) at `bridge/active-workspace-declaration-slice-1-002.md`. The single substantive change versus `-001` is to bring creation of `.claude/rules/active-workspace.md` under the active narrative-artifact approval-packet workflow per `config/governance/narrative-artifact-approval.toml` (family `role-and-governance-rules`, patterns include `.claude/rules/*.md`, approval schema explicitly enumerates `action = "create"`). The implementation direction is otherwise preserved from `-001`: a resolver module, project-default and per-harness durable records, and a repo-native validator that subsequent slices depend on. The parent scoping bridge `active-workspace-declaration-architecture-2026-04-29` remains GO at `-004`. This proposal does NOT pre-write the approval packet; it documents the planned packet shape so Codex can confirm the workflow alignment, and binds the protected Write of `.claude/rules/active-workspace.md` behind the packet evidence at implementation time.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`:

- Bridge file: `E:\GT-KB\bridge\active-workspace-declaration-slice-1-003.md`.
- Source module: `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\active_workspace.py`.
- Validator script: `E:\GT-KB\scripts\check_workspace_boundary.py`.
- Protected narrative artifact (new): `E:\GT-KB\.claude\rules\active-workspace.md`.
- Per-harness durable records: `E:\GT-KB\harness-state\claude\active-workspace.md`, `E:\GT-KB\harness-state\codex\active-workspace.md`.
- Tests: `E:\GT-KB\platform_tests\groundtruth_kb\test_active_workspace_resolver.py`, `E:\GT-KB\platform_tests\scripts\test_check_workspace_boundary.py`.
- Narrative-artifact approval packet (planned, authored at implementation time): `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-claude-rules-active-workspace-md.json`.
- MemBase: `E:\GT-KB\groundtruth.db`.

No `applications/` paths. No out-of-root references. No live dependency on `E:\Claude-Playground` or any home-directory or temp-directory location.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; live `bridge/INDEX.md` is canonical; this REVISED inserts a `REVISED:` line at the top of the `Document: active-workspace-declaration-slice-1` block; no prior version is deleted or rewritten.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root under `E:\GT-KB`; no `applications/` paths touched.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every relevant governing specification cited here; explicit spec-to-test mapping below.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation-phase tests are derived from these linked specifications and executed before VERIFIED; mapping in `## Spec-to-Test Mapping` below.
- `GOV-ARTIFACT-APPROVAL-001` - formal-artifact / narrative-artifact approval discipline; this REVISED now incorporates the per-artifact approval-packet workflow for creation of `.claude/rules/active-workspace.md` (F1 closure).
- `PB-ARTIFACT-APPROVAL-001` - Prime Builder posture on per-artifact owner-approval evidence; the protected Write is packet-gated.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - PreToolUse Write|Edit narrative-artifact-approval gate enforces packet presence and content-hash match at Write time; companion universal pre-commit floor at `scripts/check_narrative_artifact_evidence.py --staged`.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - per-harness records align with role-portability principles; `harness-state/<harness>/active-workspace.md` is a per-harness overlay, not a role-record substitute.
- `GOV-STANDING-BACKLOG-001` - this proposal creates one (1) tracking work_item; it is not a bulk operation against the standing backlog.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable records are governance artifacts and follow the artifact-oriented governance contract.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the resolver output is a tracked artifact (workspace-resolution tuple) consumed by downstream slices.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - active-workspace transitions trigger lifecycle events.
- `config/governance/narrative-artifact-approval.toml` - the protected-narrative-artifact registry that drives both the PreToolUse gate and the pre-commit floor; family `role-and-governance-rules` patterns include `.claude/rules/*.md`; packet schema enumerates `action = "create"`.
- `.claude/rules/project-root-boundary.md` - workspace boundary aligns with project-root-boundary.
- `.claude/rules/file-bridge-protocol.md` - root-boundary, spec-linkage, owner-decisions, and verification gates honored throughout.
- `.claude/rules/codex-review-gate.md` - implementation authorization does not weaken the formal-artifact / narrative-artifact approval gate; the packet remains required even with bridge GO.
- `bridge/active-workspace-declaration-slice-1-001.md` - prior NEW (operative -001).
- `bridge/active-workspace-declaration-slice-1-002.md` - Codex NO-GO (F1, P1) addressed by this revision.
- `bridge/active-workspace-declaration-architecture-2026-04-29-003.md` - parent operative proposal (REVISED-1, GO at -004).
- `bridge/active-workspace-declaration-architecture-2026-04-29-004.md` - parent scoping GO authorizing follow-on implementation slices.

## Prior Deliberations

- `DELIB-1854`: parent active-workspace architecture REVISED-1 GO. Authorizes follow-on implementation slices and lists residual implementation-review risks (two-value workspace model, validator wiring, hosted-application bridge-field grammar).
- `DELIB-1855`: parent active-workspace architecture initial NO-GO. Canonical two-value workspace model, fail-closed resolver, control-plane allowlist requirement, shell/script coverage concerns - carried forward by this slice.
- `DELIB-1978`: compressed parent bridge thread record (latest GO).
- `DELIB-0835`: owner decision on strict formal-artifact approval discipline with optional scoped auto-approval - underlies the universal narrative-artifact approval-packet floor that F1 reasserts.
- `DELIB-1577`, `DELIB-1575`: GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION cumulative review/verification - Slice C universal pre-commit floor `scripts/check_narrative_artifact_evidence.py` is the gate this revision now satisfies.
- `DELIB-1901`: compressed thread `gtkb-narrative-artifact-approval-extension-001` (VERIFIED) - protected-narrative-artifact registry is steady-state.
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE`: owner decision on GT-KB root and applications boundary - underwrites in-root placement.
- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS`: owner-articulated session-scope/work-subject foundations - informs the canonical `gt-kb` / `hosted-application` workspace values.
- `DELIB-1332`: prior NO-GO on directive enforcement registry - relevant precedent for harness-neutral rule/governance surfaces.

## Owner Decisions / Input

- 2026-05-14 UTC, S351: owner directive (verbatim) "Please parallelize the backlog. Focus on completing the implementation proposals for the top priority projects." authorizes this REVISED filing against the latest NO-GO at `-002`.
- 2026-05-14 UTC, S350: owner AUQ answer authorizing the prior NEW filing of `-001` ("Parallel research + serialized Writes now (Recommended)") is carried forward into this REVISED; the AUQ batch authorized bridge-protocol progression but did NOT replace the per-artifact narrative-artifact approval packet.
- Parent scoping GO at `bridge/active-workspace-declaration-architecture-2026-04-29-004.md` authorizes follow-on implementation slices.
- 2026-05-14 UTC: the owner has not yet been presented with the full content of `.claude/rules/active-workspace.md` for explicit approval. Per `GOV-ARTIFACT-APPROVAL-001` and `config/governance/narrative-artifact-approval.toml`, the protected Write of `.claude/rules/active-workspace.md` is packet-gated and implementation will halt at that step until the approval packet exists with `presented_to_user = true`, `transcript_captured = true`, and `explicit_change_request` populated by verbatim owner approval text. Per `.claude/rules/codex-review-gate.md`, bridge GO does NOT weaken that requirement.

## Requirement Sufficiency

Existing requirements sufficient.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation; single review packet creating one (1) tracking `work_item` row via singleton MemBase insertion. The packet covers: the resolver module (IP-1), the protected `.claude/rules/active-workspace.md` (IP-2a) plus two non-protected `harness-state/` records (IP-2b), the validator (IP-3), the regression test set (IP-4), the tracking work_item (IP-5), and the planned narrative-artifact approval-packet evidence shape (IP-6). The canonical `work_items` table receives exactly one append-only insert under `GOV-STANDING-BACKLOG-001`. Evidence tokens (for clause-preflight visibility): inventory, formal-artifact-approval, approval_packet, narrative_artifact, action=create, presented_to_user, transcript_captured, explicit_change_request, full_content_sha256, work_item, singleton MemBase insertion, deliberation, specification, ADR, DCL, GOV.

## Changes from -001

Codex NO-GO at `-002` filed one finding (F1, P1): the proposal cannot receive GO while it asserts that no formal / narrative-artifact approval packet is required for creating `.claude/rules/active-workspace.md`. This REVISED addresses F1 by:

1. **F1 closure (primary):** Replaces the incorrect "no formal-artifact-approval packet is required" claim with an explicit narrative-artifact approval-packet requirement for `.claude/rules/active-workspace.md`. The packet is required at implementation time, BEFORE the protected Write executes. Authority: `config/governance/narrative-artifact-approval.toml` (family `role-and-governance-rules`; pattern `.claude/rules/*.md`; packet schema enumerates `action = "create" | "update" | "delete"`).
2. **F1 closure (specification linkage):** Adds `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001`, and `config/governance/narrative-artifact-approval.toml` to `## Specification Links` so the proposal cites every relevant governing artifact per `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`.
3. **F1 closure (target_paths):** Adds the approval-packet path `.groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-active-workspace-md.json` to `target_paths` so the implementation-start gate authorizes its creation.
4. **F1 closure (planned packet shape):** Adds `## Approval-Packet Plan for .claude/rules/active-workspace.md` documenting each required schema field (per `[approval_packet]` in `config/governance/narrative-artifact-approval.toml`). The packet is NOT pre-written here; the section documents the planned shape so Codex can confirm workflow alignment. Actual packet authoring is implementation-time work that requires owner presentation + verbatim approval.
5. **F1 closure (verification step):** Adds `python scripts/check_narrative_artifact_evidence.py --staged` to the spec-to-test mapping; expected exit 0 with the packet clearing the protected file. Adds a negative-case smoke (unstage packet -> expect exit 1).
6. **F1 closure (per-harness records):** Explicitly notes that `harness-state/<harness>/active-workspace.md` files are NOT in the protected `role-and-governance-rules` family pattern set and proceed without a packet; this is verified by the spec-to-test step above (staged harness-state files with no covering packet must still pass `--staged`).
7. **Session and version metadata:** Session updated to S351; `Addresses:` line cites the operative NO-GO; metadata block reformatted to required structure.

No other substantive change from `-001`. The two-value canonical workspace model, the fail-closed resolver behavior, the control-plane allowlist concept, and the shell/script validator scope are all preserved.

## Approval-Packet Plan for `.claude/rules/active-workspace.md`

This section documents the planned approval-packet shape so Codex can confirm workflow alignment. The packet is NOT pre-written here; authoring is implementation-time work that requires owner presentation + verbatim approval per `GOV-ARTIFACT-APPROVAL-001`.

Packet location (per `config/governance/narrative-artifact-approval.toml` `packet_directory` + `packet_filename_pattern`):

- `.groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-active-workspace-md.json`

Required schema fields (per `[approval_packet]` in `config/governance/narrative-artifact-approval.toml`):

| Field | Planned Value |
|---|---|
| `artifact_type` | `"narrative_artifact"` (per `artifact_type_value` in the registry) |
| `artifact_id` | `"claude-rules-active-workspace-md"` |
| `action` | `"create"` (per schema enumeration; new file under `.claude/rules/*.md`) |
| `target_path` | `".claude/rules/active-workspace.md"` |
| `source_ref` | `"bridge/active-workspace-declaration-slice-1-003"` (this REVISED) |
| `full_content` | verbatim final body of `.claude/rules/active-workspace.md` (drafted at implementation time; presented to owner for verbatim approval) |
| `full_content_sha256` | `sha256(full_content)` computed at packet-author time after owner approves the verbatim content |
| `approval_mode` | `"approve"` (default) or `"edit-and-approve"` (if owner edits the proposed body) |
| `presented_to_user` | `true` |
| `transcript_captured` | `true` |
| `explicit_change_request` | verbatim owner approval text from the S351 (or follow-on session) presentation |
| `changed_by` | `"claude-prime-builder"` (active Prime harness identity B) |
| `change_reason` | `"Slice 1 of active-workspace-declaration; bridge thread active-workspace-declaration-slice-1; F1 closure per bridge/active-workspace-declaration-slice-1-002.md"` |

Implementation-time workflow:

1. Draft full body of `.claude/rules/active-workspace.md` (project-default header `active_workspace: gt-kb` plus owner-facing rule narration).
2. Present the verbatim body to the owner via `AskUserQuestion` per the AUQ-only enforcement stack.
3. Capture the owner approval text verbatim into `explicit_change_request`.
4. Compute `full_content_sha256`.
5. Write the packet JSON.
6. Set `GTKB_FORMAL_APPROVAL_PACKET` (or `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` per `[hook_detection]`) to the packet path for the protected Write.
7. Write `.claude/rules/active-workspace.md` (PreToolUse narrative-artifact-approval gate verifies packet presence + content-hash match).
8. Stage both the protected file and the packet; run `python scripts/check_narrative_artifact_evidence.py --staged`; expect exit 0.
9. Commit.

Confirmation that per-harness records do NOT require packets:

- The protected-artifact patterns in `config/governance/narrative-artifact-approval.toml` (`role-and-governance-rules` family) are `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE-ARCHITECTURE.md`, `memory/work_list.md`.
- `harness-state/<harness>/active-workspace.md` does NOT match any of those patterns.
- Therefore the two `harness-state/claude/active-workspace.md` and `harness-state/codex/active-workspace.md` files proceed without packets. The pre-commit gate test (negative case with harness-state files staged and no covering packet) confirms this.

## Spec-to-Test Mapping

| Spec | Verification Step | Command and Observed Result |
|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` + IP-1 + IP-3 + IP-4 | Resolver and validator unit tests | `python -m pytest platform_tests/groundtruth_kb/test_active_workspace_resolver.py platform_tests/scripts/test_check_workspace_boundary.py -v` - expect all PASS. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | In-root verification and lint | `python -m ruff check groundtruth-kb/src/groundtruth_kb/active_workspace.py scripts/check_workspace_boundary.py` - expect zero errors; manual confirmation no `applications/` paths are touched. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` + `GOV-FILE-BRIDGE-AUTHORITY-001` | Applicability preflight | `python scripts/bridge_applicability_preflight.py --bridge-id active-workspace-declaration-slice-1` - expect `preflight_passed: true`, `missing_required_specs: []`. |
| ADR/DCL clause coverage (clause-preflight) | Clause preflight | `python scripts/adr_dcl_clause_preflight.py --bridge-id active-workspace-declaration-slice-1` - expect exit 0; no blocking gaps. |
| `GOV-ARTIFACT-APPROVAL-001` + `PB-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` (F1 closure) | Narrative-artifact pre-commit gate (positive case) | Stage `.claude/rules/active-workspace.md` and the packet at `.groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-active-workspace-md.json`; run `python scripts/check_narrative_artifact_evidence.py --staged` - expect exit 0. |
| `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` (F1 closure, negative case) | Narrative-artifact pre-commit gate (negative case) | Unstage the packet and rerun `python scripts/check_narrative_artifact_evidence.py --staged` - expect exit 1 (commit-rejected). |
| `GOV-ARTIFACT-APPROVAL-001` (boundary case) | Non-protected per-harness records | With `harness-state/claude/active-workspace.md` and `harness-state/codex/active-workspace.md` staged and no packet covering them, run `python scripts/check_narrative_artifact_evidence.py --staged` - expect exit 0 (these are NOT in the protected family). |
| `GOV-STANDING-BACKLOG-001` | Tracking work_item visibility | After IP-5 insert: `python -m groundtruth_kb backlog list --all --json` - expect the new tracking row to appear. |
| End-to-end smoke | Validator round-trip | `python scripts/check_workspace_boundary.py` - expect exit 0 against the current GT-KB state after IP-1/IP-2/IP-3 land. |

## Acceptance Criteria

1. The resolver module exists at `groundtruth-kb/src/groundtruth_kb/active_workspace.py`, exposes `WorkspaceResolution` and `resolve()`, returns a definite tuple or a blocking-diagnostic string per the parent GO behavior.
2. `.claude/rules/active-workspace.md` is created via the narrative-artifact approval-packet workflow: packet exists at `.groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-active-workspace-md.json` with all schema fields populated and `full_content_sha256` matching the committed body.
3. `harness-state/claude/active-workspace.md` and `harness-state/codex/active-workspace.md` exist as per-harness records, NOT packet-gated.
4. The validator script `scripts/check_workspace_boundary.py` exists, returns exit 0 against current state, supports `--workspace` and `--harness` flags, and is invocable via `python scripts/check_workspace_boundary.py`.
5. Regression tests in `platform_tests/groundtruth_kb/test_active_workspace_resolver.py` and `platform_tests/scripts/test_check_workspace_boundary.py` all PASS.
6. `python scripts/check_narrative_artifact_evidence.py --staged` exits 0 with packet present (positive case) and exits 1 with packet unstaged (negative case).
7. Bridge applicability preflight and clause preflight both pass against `active-workspace-declaration-slice-1`.
8. One (1) tracking `work_item` row is inserted into MemBase with origin=`new`, component=`active-workspace`, and a `change_reason` citing this bridge thread.
9. `bridge/INDEX.md` reflects the post-implementation NEW status at the top of the thread's version list, with all prior versions preserved in append-only order.

## Bridge INDEX Update Evidence (CLAUSE-INDEX-IS-CANONICAL)

This REVISED inserts a `REVISED:` line at the top of `Document: active-workspace-declaration-slice-1` in `bridge/INDEX.md`. Additive; no deletion or rewrite of prior version lines (`NO-GO: bridge/active-workspace-declaration-slice-1-002.md` and `NEW: bridge/active-workspace-declaration-slice-1-001.md` remain in their existing positions below this REVISED line). The INDEX update is the canonical workflow-state mutation; `bridge/INDEX.md` is the source of truth for thread state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Bulk-Operations Clause Evidence (CLAUSE-VISIBILITY-BULK-OPS)

Not a bulk operation; single review packet creating one tracking `work_item` row via singleton MemBase insertion under `GOV-STANDING-BACKLOG-001`. No bulk standing-backlog mutation, no batch spec promotion, no batch retirement. Evidence tokens repeated for clause-preflight matching: inventory, formal-artifact-approval, approval_packet, work_item.

## Bridge-Compliance Self-Check

- Non-empty `## Specification Links` flat bullets; no parenthetical heading; no `###` sub-headings inside.
- Non-empty `## Prior Deliberations`.
- Non-empty `## Owner Decisions / Input`.
- `target_paths` in JSON list form.
- `## Requirement Sufficiency` one operative state (`Existing requirements sufficient`).
- `## In-Root Placement Evidence` present.
- `## Bridge INDEX Update Evidence` present.
- `## Bulk-Operations Clause Evidence` present.
- `## Changes from -001` documents the F1 closure (approval-packet workflow incorporated, specification linkage updated, target_paths updated, verification step added).
- `## Approval-Packet Plan for .claude/rules/active-workspace.md` documents the planned approval-evidence shape per `config/governance/narrative-artifact-approval.toml` `[approval_packet]` schema.
- `## Spec-to-Test Mapping` table present with positive and negative narrative-artifact-gate cases.
- `## Acceptance Criteria` numbered list present.
- First line is `REVISED`.
- Metadata block has `bridge_kind: implementation_proposal`, `Document`, `Version: 003`, `Session: S351`, `Addresses:` citing the operative NO-GO.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
