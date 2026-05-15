REVISED

# Implementation Proposal REVISED-2 - Active-Workspace Declaration Slice 1

bridge_kind: implementation_proposal
Document: active-workspace-declaration-slice-1
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S351
Addresses: NO-GO at `bridge/active-workspace-declaration-slice-1-004.md` (F1: MemBase `work_items` insertion lacked specified `id`, `title`, and field-level read-back assertion).

target_paths: ["groundtruth-kb/src/groundtruth_kb/active_workspace.py", "scripts/check_workspace_boundary.py", ".claude/rules/active-workspace.md", "harness-state/claude/active-workspace.md", "harness-state/codex/active-workspace.md", "platform_tests/groundtruth_kb/test_active_workspace_resolver.py", "platform_tests/scripts/test_check_workspace_boundary.py", ".groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-active-workspace-md.json", "groundtruth.db"]

## Claim

REVISED-2 in response to Codex F1 (P2) at `bridge/active-workspace-declaration-slice-1-004.md`. The single substantive change versus `-003` is to specify the exact MemBase `work_items` row that IP-5 inserts (`id`, `title`, `origin`, `component`, `resolution_status`, `stage`, `source_spec_id`, `changed_by`, `change_reason`, `related_bridge_threads`, `related_deliberation_ids`) plus a named read-back assertion test (`test_tracking_work_item_inserted_with_expected_fields`) that asserts each enumerated field. This closes the F1 finding that the proposal left part of the `groundtruth.db` mutation unapproved and not machine-verifiable. The prior closure of the narrative-artifact approval-packet workflow for `.claude/rules/active-workspace.md` (closed at `-003` against the `-002` NO-GO) is preserved verbatim. No change to scope, resolver behavior, validator design, control-plane allowlist, two-value workspace model, fail-closed resolver, or shell/script coverage. The parent scoping bridge `active-workspace-declaration-architecture-2026-04-29` remains GO at `-004`.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`:

- Bridge file: `E:\GT-KB\bridge\active-workspace-declaration-slice-1-005.md`.
- Source module: `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\active_workspace.py`.
- Validator script: `E:\GT-KB\scripts\check_workspace_boundary.py`.
- Protected narrative artifact (new): `E:\GT-KB\.claude\rules\active-workspace.md`.
- Per-harness durable records: `E:\GT-KB\harness-state\claude\active-workspace.md`, `E:\GT-KB\harness-state\codex\active-workspace.md`.
- Tests: `E:\GT-KB\platform_tests\groundtruth_kb\test_active_workspace_resolver.py`, `E:\GT-KB\platform_tests\scripts\test_check_workspace_boundary.py`.
- Narrative-artifact approval packet (planned, authored at implementation time): `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-claude-rules-active-workspace-md.json`.
- MemBase: `E:\GT-KB\groundtruth.db`.

No `applications/` paths. No out-of-root references. No live dependency on `E:\Claude-Playground` or any home-directory or temp-directory location.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; live `bridge/INDEX.md` is canonical; this REVISED-2 inserts a `REVISED:` line at the top of the `Document: active-workspace-declaration-slice-1` block; no prior version is deleted or rewritten.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root under `E:\GT-KB`; no `applications/` paths touched.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every relevant governing specification cited here; explicit spec-to-test mapping below.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - implementation-phase tests are derived from these linked specifications and executed before VERIFIED; mapping in `## Spec-to-Test Mapping` below; the new `test_tracking_work_item_inserted_with_expected_fields` covers the `GOV-STANDING-BACKLOG-001` field-level visibility requirement.
- `GOV-ARTIFACT-APPROVAL-001` - formal-artifact / narrative-artifact approval discipline; this proposal incorporates the per-artifact approval-packet workflow for creation of `.claude/rules/active-workspace.md` (closed at `-003`).
- `PB-ARTIFACT-APPROVAL-001` - Prime Builder posture on per-artifact owner-approval evidence; the protected Write is packet-gated.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - PreToolUse Write|Edit narrative-artifact-approval gate enforces packet presence and content-hash match at Write time; companion universal pre-commit floor at `scripts/check_narrative_artifact_evidence.py --staged`.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - per-harness records align with role-portability principles; `harness-state/<harness>/active-workspace.md` is a per-harness overlay, not a role-record substitute.
- `GOV-STANDING-BACKLOG-001` - this proposal creates one (1) tracking work_item via singleton MemBase insertion with field-level row-identity specification (closed at this REVISED-2); not a bulk operation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - durable records are governance artifacts and follow the artifact-oriented governance contract.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the resolver output is a tracked artifact (workspace-resolution tuple) consumed by downstream slices.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - active-workspace transitions trigger lifecycle events.
- `config/governance/narrative-artifact-approval.toml` - the protected-narrative-artifact registry that drives both the PreToolUse gate and the pre-commit floor; family `role-and-governance-rules` patterns include `.claude/rules/*.md`; packet schema enumerates `action = "create"`.
- `.claude/rules/project-root-boundary.md` - workspace boundary aligns with project-root-boundary.
- `.claude/rules/file-bridge-protocol.md` - root-boundary, spec-linkage, owner-decisions, and verification gates honored throughout.
- `.claude/rules/codex-review-gate.md` - implementation authorization does not weaken the formal-artifact / narrative-artifact approval gate; the packet remains required even with bridge GO.
- `bridge/active-workspace-declaration-slice-1-001.md` - prior NEW.
- `bridge/active-workspace-declaration-slice-1-002.md` - Codex NO-GO (first round; closed at `-003`).
- `bridge/active-workspace-declaration-slice-1-003.md` - prior REVISED-1 (operative proposal text; carried forward verbatim except where explicitly noted in `## Changes from -003`).
- `bridge/active-workspace-declaration-slice-1-004.md` - Codex NO-GO on REVISED-1 (F1: tracking work_item row identity not machine-verifiable); addressed here.
- `bridge/active-workspace-declaration-architecture-2026-04-29-003.md` - parent operative proposal (REVISED-1, GO at -004).
- `bridge/active-workspace-declaration-architecture-2026-04-29-004.md` - parent scoping GO authorizing follow-on implementation slices.

## Prior Deliberations

- `DELIB-1854`: parent active-workspace architecture REVISED-1 GO. Authorizes follow-on implementation slices and lists residual implementation-review risks (two-value workspace model, validator wiring, hosted-application bridge-field grammar).
- `DELIB-1855`: parent active-workspace architecture initial NO-GO. Canonical two-value workspace model, fail-closed resolver, control-plane allowlist requirement, shell/script coverage concerns - carried forward by this slice.
- `DELIB-1978`: compressed parent bridge thread record (latest GO).
- `DELIB-0835`: owner decision on strict formal-artifact approval discipline with optional scoped auto-approval - underlies the universal narrative-artifact approval-packet floor that the prior F1 (closed at `-003`) reasserted.
- `DELIB-1577`, `DELIB-1575`: GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION cumulative review/verification - Slice C universal pre-commit floor `scripts/check_narrative_artifact_evidence.py` is the gate the prior F1 closure satisfies.
- `DELIB-1901`: compressed thread `gtkb-narrative-artifact-approval-extension-001` (VERIFIED) - protected-narrative-artifact registry is steady-state.
- `DELIB-1562`, `DELIB-1567`, `DELIB-1788`: approval-packet and backlog/work-item governance precedents (cited by `-004` as relevant precedents for machine-verifiable MemBase mutations).
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE`: owner directive on formal backlog DB schema. Underwrites the requirement that `work_items` inserts specify enumerated row identity (the basis for this REVISED-2 closure).
- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE`: owner decision on GT-KB root and applications boundary - underwrites in-root placement.
- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS`: owner-articulated session-scope/work-subject foundations - informs the canonical `gt-kb` / `hosted-application` workspace values.
- `DELIB-1332`: prior NO-GO on directive enforcement registry - relevant precedent for harness-neutral rule/governance surfaces.

No prior deliberation supersedes the current requirement that MemBase work-item mutations be reviewable and verifiable from the proposal text; this REVISED-2 satisfies that requirement.

## Owner Decisions / Input

- 2026-05-14 UTC, S351: owner directive (verbatim) "Please parallelize the backlog. Focus on completing the implementation proposals for the top priority projects." authorizes this REVISED-2 filing against the latest NO-GO at `-004`.
- 2026-05-14 UTC, S351: owner AUQ answer "Continue parallel REVISED" authorizing this `-005` as part of the next parallel batch of REVISED filings.
- 2026-05-14 UTC, S350: owner AUQ answer authorizing the original NEW filing of `-001` ("Parallel research + serialized Writes now (Recommended)") is carried forward into this REVISED; the AUQ batch authorized bridge-protocol progression but did NOT replace the per-artifact narrative-artifact approval packet (which remains required at implementation time per the prior closure).
- Parent scoping GO at `bridge/active-workspace-declaration-architecture-2026-04-29-004.md` authorizes follow-on implementation slices.
- 2026-05-14 UTC: the owner has not yet been presented with the full content of `.claude/rules/active-workspace.md` for explicit approval. Per `GOV-ARTIFACT-APPROVAL-001` and `config/governance/narrative-artifact-approval.toml`, the protected Write of `.claude/rules/active-workspace.md` is packet-gated and implementation will halt at that step until the approval packet exists with `presented_to_user = true`, `transcript_captured = true`, and `explicit_change_request` populated by verbatim owner approval text. Per `.claude/rules/codex-review-gate.md`, bridge GO does NOT weaken that requirement.
- No new owner decision required by this REVISED-2. The fix path is "specify the tracking work_item row identity + read-back assertion," which does not narrow or expand parent or slice scope.

## Requirement Sufficiency

Existing requirements sufficient.

## Approval-Packet Plan for `.claude/rules/active-workspace.md`

This section documents the planned approval-packet shape so Codex can confirm workflow alignment. The packet is NOT pre-written here; authoring is implementation-time work that requires owner presentation + verbatim approval per `GOV-ARTIFACT-APPROVAL-001`. Carried forward verbatim from `-003`.

Packet location (per `config/governance/narrative-artifact-approval.toml` `packet_directory` + `packet_filename_pattern`):

- `.groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-active-workspace-md.json`

Required schema fields (per `[approval_packet]` in `config/governance/narrative-artifact-approval.toml`):

| Field | Planned Value |
|---|---|
| `artifact_type` | `"narrative_artifact"` (per `artifact_type_value` in the registry) |
| `artifact_id` | `"claude-rules-active-workspace-md"` |
| `action` | `"create"` (per schema enumeration; new file under `.claude/rules/*.md`) |
| `target_path` | `".claude/rules/active-workspace.md"` |
| `source_ref` | `"bridge/active-workspace-declaration-slice-1-005"` (this REVISED-2; updated from `-003`) |
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

## Tracking Work-Item Specification

This section closes F1 from `bridge/active-workspace-declaration-slice-1-004.md` by enumerating the exact MemBase `work_items` row IP-5 inserts. The insertion uses `KnowledgeDB.insert_work_item(...)` (`groundtruth-kb/src/groundtruth_kb/db.py:3253-3261`) with these fields:

- `id="WI-ACTIVE-WORKSPACE-DECLARATION-SLICE-1"`
- `title="Active-workspace declaration Slice 1 (resolver + durable records + validator)"`
- `origin="new"`
- `component="active-workspace"`
- `resolution_status="in_progress"`
- `stage="implementing"`
- `source_spec_id=None` (placeholder spec `SPEC-ACTIVE-WORKSPACE-DECLARATION` not yet inserted in MemBase; created in a later slice's ADR/SPEC capture; this WI is updated to link the spec id when the spec lands)
- `changed_by="claude-prime-builder"`
- `change_reason="Track Slice 1 implementation of active-workspace declaration (resolver + durable records + validator) per parent GO bridge/active-workspace-declaration-architecture-2026-04-29-003.md (REVISED-2 of slice-1 closes work_item identity NO-GO at bridge/active-workspace-declaration-slice-1-004.md)"`
- `related_bridge_threads="active-workspace-declaration-slice-1"`
- `related_deliberation_ids="DELIB-1854,DELIB-1855,DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE"`
- All other optional fields: NULL (omitted from kwargs).

Read-back assertion (the F1-closing machine-verifiable check): the test `test_tracking_work_item_inserted_with_expected_fields` in `platform_tests/groundtruth_kb/test_active_workspace_resolver.py` queries MemBase by id via `KnowledgeDB.get_work_item("WI-ACTIVE-WORKSPACE-DECLARATION-SLICE-1")`, asserts exactly one current row, and asserts each enumerated field above matches the inserted value. The test is added to the existing resolver test module rather than a new test file because it exercises the IP-5 MemBase artifact created as part of Slice 1 implementation. The test executes after IP-5 lands; before IP-5, the test is expected to be present and skipped (or fail with a clear "tracking work_item not yet inserted" message, depending on test-framework conventions); after IP-5, the test passes with the enumerated fields.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation; single review packet creating one (1) tracking `work_item` row via singleton MemBase insertion. The packet covers: the resolver module (IP-1), the protected `.claude/rules/active-workspace.md` (IP-2a) plus two non-protected `harness-state/` records (IP-2b), the validator (IP-3), the regression test set (IP-4), the tracking work_item with enumerated row identity (IP-5), and the planned narrative-artifact approval-packet evidence shape (IP-6). The canonical `work_items` table receives exactly one append-only insert under `GOV-STANDING-BACKLOG-001`; the row identity and read-back assertion are specified in `## Tracking Work-Item Specification` above. Evidence tokens (for clause-preflight visibility): inventory, formal-artifact-approval, approval_packet, narrative_artifact, action=create, presented_to_user, transcript_captured, explicit_change_request, full_content_sha256, work_item, singleton MemBase insertion, deliberation, specification, ADR, DCL, GOV, read-back assertion.

## Changes from -003

Codex NO-GO at `-004` filed one finding (F1, P2): the proposal proposed a MemBase `work_items` insertion without specifying the row `id`, `title`, or a field-level read-back assertion, leaving part of the `groundtruth.db` mutation unapproved and not machine-verifiable. This REVISED-2 addresses F1 by:

1. **F1 closure (primary):** Adds `## Tracking Work-Item Specification` enumerating the exact `KnowledgeDB.insert_work_item(...)` call fields - `id="WI-ACTIVE-WORKSPACE-DECLARATION-SLICE-1"`, `title="Active-workspace declaration Slice 1 (resolver + durable records + validator)"`, `origin="new"`, `component="active-workspace"`, `resolution_status="in_progress"`, `stage="implementing"`, `source_spec_id=None`, `changed_by="claude-prime-builder"`, `change_reason` (cites this thread + parent GO), `related_bridge_threads="active-workspace-declaration-slice-1"`, `related_deliberation_ids="DELIB-1854,DELIB-1855,DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE"`. All other optional fields are explicitly NULL.
2. **F1 closure (read-back assertion):** Adds a named test `test_tracking_work_item_inserted_with_expected_fields` in `platform_tests/groundtruth_kb/test_active_workspace_resolver.py` that queries MemBase by id, asserts exactly one current row, and asserts each enumerated field value. The test replaces the prior broad `python -m groundtruth_kb backlog list --all --json` check with a field-level read-back per `-004` recommended action.
3. **F1 closure (spec-to-test mapping):** Updates `## Spec-to-Test Mapping` to add a row for the new read-back assertion test mapped to `GOV-STANDING-BACKLOG-001`; the prior backlog-list row is preserved as a complementary visibility check but is no longer the only `GOV-STANDING-BACKLOG-001` verification.
4. **F1 closure (acceptance criteria):** Updates acceptance criterion 8 from "One (1) tracking `work_item` row is inserted..." to "One (1) tracking `work_item` row is inserted with the exact fields enumerated in `## Tracking Work-Item Specification` and verified by `test_tracking_work_item_inserted_with_expected_fields`."
5. **Session and version metadata:** `Version: 005`; `Addresses:` line cites the operative NO-GO at `-004`; `source_ref` in approval-packet plan updated to `-005`.

No other substantive change from `-003`. The F1 closure from `-002` (narrative-artifact approval-packet workflow for `.claude/rules/active-workspace.md`) is preserved verbatim. The two-value canonical workspace model, the fail-closed resolver behavior, the control-plane allowlist concept, the shell/script validator scope, the per-harness records, and the spec-to-test mapping for IP-1 / IP-2 / IP-3 / IP-4 are all preserved.

## Spec-to-Test Mapping

| Spec | Verification Step | Command and Observed Result |
|---|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` + IP-1 + IP-3 + IP-4 | Resolver and validator unit tests | `python -m pytest platform_tests/groundtruth_kb/test_active_workspace_resolver.py platform_tests/scripts/test_check_workspace_boundary.py -v` - expect all PASS. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | In-root verification and lint | `python -m ruff check groundtruth-kb/src/groundtruth_kb/active_workspace.py scripts/check_workspace_boundary.py` - expect zero errors; manual confirmation no `applications/` paths are touched. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` + `GOV-FILE-BRIDGE-AUTHORITY-001` | Applicability preflight | `python scripts/bridge_applicability_preflight.py --bridge-id active-workspace-declaration-slice-1` - expect `preflight_passed: true`, `missing_required_specs: []`. |
| ADR/DCL clause coverage (clause-preflight) | Clause preflight | `python scripts/adr_dcl_clause_preflight.py --bridge-id active-workspace-declaration-slice-1` - expect exit 0; no blocking gaps. |
| `GOV-ARTIFACT-APPROVAL-001` + `PB-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` (prior F1 closure) | Narrative-artifact pre-commit gate (positive case) | Stage `.claude/rules/active-workspace.md` and the packet at `.groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-active-workspace-md.json`; run `python scripts/check_narrative_artifact_evidence.py --staged` - expect exit 0. |
| `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` (prior F1 closure, negative case) | Narrative-artifact pre-commit gate (negative case) | Unstage the packet and rerun `python scripts/check_narrative_artifact_evidence.py --staged` - expect exit 1 (commit-rejected). |
| `GOV-ARTIFACT-APPROVAL-001` (boundary case) | Non-protected per-harness records | With `harness-state/claude/active-workspace.md` and `harness-state/codex/active-workspace.md` staged and no packet covering them, run `python scripts/check_narrative_artifact_evidence.py --staged` - expect exit 0 (these are NOT in the protected family). |
| `GOV-STANDING-BACKLOG-001` (this REVISED-2 closure; field-level row identity) | Tracking work_item read-back assertion (named test) | `python -m pytest platform_tests/groundtruth_kb/test_active_workspace_resolver.py::test_tracking_work_item_inserted_with_expected_fields -v` - expect PASS with exactly one current row at id `WI-ACTIVE-WORKSPACE-DECLARATION-SLICE-1` and each enumerated field matching. |
| `GOV-STANDING-BACKLOG-001` (complementary visibility check) | Tracking work_item appears in backlog list | After IP-5 insert: `python -m groundtruth_kb backlog list --all --json` - expect the row `WI-ACTIVE-WORKSPACE-DECLARATION-SLICE-1` to appear (complementary to the read-back assertion; not the sole `GOV-STANDING-BACKLOG-001` verification). |
| End-to-end smoke | Validator round-trip | `python scripts/check_workspace_boundary.py` - expect exit 0 against the current GT-KB state after IP-1/IP-2/IP-3 land. |

## Acceptance Criteria

1. The resolver module exists at `groundtruth-kb/src/groundtruth_kb/active_workspace.py`, exposes `WorkspaceResolution` and `resolve()`, returns a definite tuple or a blocking-diagnostic string per the parent GO behavior.
2. `.claude/rules/active-workspace.md` is created via the narrative-artifact approval-packet workflow: packet exists at `.groundtruth/formal-artifact-approvals/2026-05-14-claude-rules-active-workspace-md.json` with all schema fields populated and `full_content_sha256` matching the committed body.
3. `harness-state/claude/active-workspace.md` and `harness-state/codex/active-workspace.md` exist as per-harness records, NOT packet-gated.
4. The validator script `scripts/check_workspace_boundary.py` exists, returns exit 0 against current state, supports `--workspace` and `--harness` flags, and is invocable via `python scripts/check_workspace_boundary.py`.
5. Regression tests in `platform_tests/groundtruth_kb/test_active_workspace_resolver.py` and `platform_tests/scripts/test_check_workspace_boundary.py` all PASS.
6. `python scripts/check_narrative_artifact_evidence.py --staged` exits 0 with packet present (positive case) and exits 1 with packet unstaged (negative case).
7. Bridge applicability preflight and clause preflight both pass against `active-workspace-declaration-slice-1`.
8. One (1) tracking `work_item` row is inserted with the exact fields enumerated in `## Tracking Work-Item Specification` (`id="WI-ACTIVE-WORKSPACE-DECLARATION-SLICE-1"`, `title="Active-workspace declaration Slice 1 (resolver + durable records + validator)"`, plus the full enumerated field list), and verified by `test_tracking_work_item_inserted_with_expected_fields` asserting each enumerated field value via `KnowledgeDB.get_work_item("WI-ACTIVE-WORKSPACE-DECLARATION-SLICE-1")`.
9. `bridge/INDEX.md` reflects the post-implementation NEW status at the top of the thread's version list, with all prior versions preserved in append-only order.

## Bridge INDEX Update Evidence (CLAUSE-INDEX-IS-CANONICAL)

This REVISED-2 inserts a `REVISED:` line at the top of `Document: active-workspace-declaration-slice-1` in `bridge/INDEX.md`. Additive; no deletion or rewrite of prior version lines (`NO-GO: bridge/active-workspace-declaration-slice-1-004.md`, `REVISED: bridge/active-workspace-declaration-slice-1-003.md`, `NO-GO: bridge/active-workspace-declaration-slice-1-002.md`, and `NEW: bridge/active-workspace-declaration-slice-1-001.md` remain in their existing positions below this REVISED line). The INDEX update is the canonical workflow-state mutation; `bridge/INDEX.md` is the source of truth for thread state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Bulk-Operations Clause Evidence (CLAUSE-VISIBILITY-BULK-OPS)

Not a bulk operation; single review packet creating one tracking `work_item` row via singleton MemBase insertion under `GOV-STANDING-BACKLOG-001`. The row identity is enumerated in `## Tracking Work-Item Specification` (id `WI-ACTIVE-WORKSPACE-DECLARATION-SLICE-1` plus full field list) and verified by a named read-back assertion test. No bulk standing-backlog mutation, no batch spec promotion, no batch retirement. Evidence tokens repeated for clause-preflight matching: inventory, formal-artifact-approval, approval_packet, work_item, read-back assertion, machine-verifiable row identity.

## Bridge-Compliance Self-Check

- First line is `REVISED`.
- Non-empty `## Specification Links` flat bullets; no parenthetical heading; no `###` sub-headings inside.
- Non-empty `## Prior Deliberations` with real DELIB IDs.
- Non-empty `## Owner Decisions / Input` with substantive AUQ evidence.
- `target_paths` JSON list; all in-root under `E:\GT-KB`.
- `## Requirement Sufficiency` exactly one operative state (`Existing requirements sufficient`).
- `## In-Root Placement Evidence` present.
- `## Approval-Packet Plan for .claude/rules/active-workspace.md` present (carried forward verbatim from `-003`).
- `## Tracking Work-Item Specification` present (new; closes `-004` F1) with enumerated `id`, `title`, `origin`, `component`, `resolution_status`, `stage`, `source_spec_id`, `changed_by`, `change_reason`, `related_bridge_threads`, `related_deliberation_ids`, plus named read-back assertion test `test_tracking_work_item_inserted_with_expected_fields`.
- `## Clause Scope Clarification (Not a Bulk Operation)` present.
- `## Changes from -003` documents the F1 closure.
- `## Spec-to-Test Mapping` table present with the new read-back assertion row mapped to `GOV-STANDING-BACKLOG-001`.
- `## Acceptance Criteria` numbered list present; criterion 8 updated for the enumerated work_item + read-back assertion.
- `## Bridge INDEX Update Evidence (CLAUSE-INDEX-IS-CANONICAL)` present.
- `## Bulk-Operations Clause Evidence (CLAUSE-VISIBILITY-BULK-OPS)` present.
- Metadata block has `bridge_kind: implementation_proposal`, `Document: active-workspace-declaration-slice-1`, `Version: 005`, `Session: S351`, `Addresses:` citing the operative NO-GO at `-004`.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
