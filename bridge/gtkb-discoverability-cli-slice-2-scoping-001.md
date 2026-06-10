NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 00d6b362-374c-4c5c-bf69-b7c23d0f2f58
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning

Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3262

# GT-KB Discoverability CLI Slice 2 - `gt backlog status` Scoping

bridge_kind: prime_proposal

Document: gtkb-discoverability-cli-slice-2-scoping
Version: 001 (NEW; scoping proposal for Slice 2 of `gtkb-discoverability-cli`)
Date: 2026-05-29 UTC

## Summary

Scopes Slice 2 of `gtkb-discoverability-cli` (Slice 1 VERIFIED at -008): a deterministic `gt backlog status` CLI subcommand that consolidates project state + work-item rollup + bridge VERIFIED coverage + orphan-WI surface + retire-ready candidates into a single JSON-capable command. Eliminates the recurring ad-hoc-Python-script pattern where Prime Builder reconstructs the same JOIN against `current_projects` x `current_work_items` x `project_work_item_memberships` x bridge/INDEX.md to answer "what is the backlog state?"

This is a SCOPING-only filing. An implementation Slice 2 proposal will follow after Codex GO with concrete target_paths, test specifications, and PAUTH coverage confirmation. WI-3262's description explicitly captures the symptom: "Session 2026-05-10 wrote 4 ad-hoc Python scripts where CLI verbs would have served better. Future slug: gtkb-cli-discoverability-001."

## Problem Statement

S373 implementation-gap triage (this session, conversation `00d6b362-374c-4c5c-bf69-b7c23d0f2f58`) surfaced 7 backlog-subsystem gaps. Gap 5 - no deterministic backlog status CLI - is the only gap that directly satisfies the owner's stated rule (canonical authority: `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: repetitive work performed by AI is a defect; deterministic plumbing belongs in services).

Symptom reproduction this session: producing a comprehensive backlog status report required schema introspection plus ad-hoc Python plus cross-walking bridge/INDEX.md plus cross-walking auto-memory feedback notes plus cross-walking the operational notepad. Many tool calls. Each future session asking "what is the backlog state?" pays the same tax.

Cause: the existing CLI surface has `gt projects list`, `gt projects show <PID>`, `gt backlog list`, `gt backlog show <WID>`, and the read-only completion scanner. None of them produce the consolidated view (projects x WI rollup x bridge VERIFIED coverage x orphan WIs x retire-ready candidates) in one invocation.

Prior art: `gtkb-discoverability-cli-slice-1` (VERIFIED at -008) shipped foundation discoverability surfaces. Sibling thread `gtkb-cli-discoverability-doctor-json-backlog-show-003` WITHDRAWN - its NO-GO chain documents the failure mode of bundling too many discoverability verbs in one proposal. Slice 2 follows the smaller-scope, single-verb pattern that succeeded for Slice 1.

## Proposed Scope (For Slice 2 Implementation Bridge)

CLI: `gt backlog status` with these flags:

- `--project <PID>` (default: all active projects)
- `--with-verified-coverage` (cross-walk bridge/INDEX.md for VERIFIED-bridge evidence per WI)
- `--with-orphans` (surface open WIs lacking an active `project_work_item_memberships` row)
- `--with-retire-ready` (surface active projects whose WIs are all terminal - auto-retire candidates)
- `--json` (machine-readable output for tooling)

Output structure (JSON):

- `projects[]` - id, name, status, total_wis, open_wis, verified_wis, sample_states, doubled_prefix_flag
- `orphan_wis[]` - id, title, resolution_status, project_name_field
- `retire_ready[]` - project_id, name, wi_count, all_terminal_states
- `summary{}` - counts by project status, WI status, membership total, orphan count, retire-ready count

Read-only. No DB writes. Implementation pattern follows Slice 1 (a thin CLI module wrapping a deterministic query against MemBase). Bridge-INDEX read uses the canonical `groundtruth_kb.bridge.detector.parse_index` parser (already in scanner code) - no second parser.

## Out of Scope (Slice 2)

- Schema migrations - none.
- MemBase mutations - none. Read-only command.
- bridge/INDEX.md mutations - none.
- New skill creation - deferred. A `backlog` skill discussion belongs in the `gtkb-skill-modernization` family, not here.
- Doubled-prefix project cleanup (Gap 2; tracked under PROJECT-GTKB-RELIABILITY-FIXES) - separate reliability-fast-lane filing.
- Auto-retire close-loop (Gap 1) - in flight at `gtkb-project-completion-scanner-addressing-thread-fix-implementation` (NEW->NO-GO at -002 today).

## Specification Links

- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the operative authority. This proposal addresses a textbook case: repetitive AI plumbing (ad-hoc Python for status reports) where a deterministic service belongs.
- WI-3262 - parent work item. Active membership to `PROJECT-GTKB-DETERMINISTIC-SERVICES-001` (source=work_items.project_name) and to `PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DISCOVERABILITY` (source=work_items.subproject_name). Description: "Symptom-driven. Session 2026-05-10 wrote 4 ad-hoc Python scripts where CLI verbs would have served better."
- `gtkb-discoverability-cli-slice-1` VERIFIED at -008 - predecessor slice. Slice 2 reuses the slug family per the slug-family-continuity convention.
- GOV-FILE-BRIDGE-AUTHORITY-001 - bridge/INDEX.md is the canonical workflow state. This scoping proposal is filed at -001 NEW and inserted at top of INDEX as a new entry. Append-only.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this Specification Links section satisfies the linkage gate.
- DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 - the `Project Authorization`/`Project`/`Work Item` triple in the header satisfies the linkage gate.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - the test plan below maps each acceptance criterion to executable verification.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001, DCL-PROJECT-AUTHORIZATION-ENVELOPE-001, PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 - covered by `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI` (includes WI-3262 in its included_work_item_ids list; active; no expiration).
- GOV-STANDING-BACKLOG-001 - cited because this proposal references work_items and the backlog. This filing is NOT a bulk MemBase mutation, NOT a backlog reorganization, NOT an authority-state change. See Clause Scope Clarification below.
- GOV-ARTIFACT-APPROVAL-001 - this scoping introduces no canonical artifact. No MemBase spec/GOV/ADR/DCL/PB row, no protected narrative file. Out of scope for this scoping.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (advisory) - cited because this proposal references owner decisions, requirements, specifications, work items, and backlog content patterns. The scoping itself preserves these as durable bridge artifacts.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (advisory) - cited because this proposal references MemBase and deliberation artifacts. The implementation Slice 2 will read MemBase and bridge artifacts only; no schema or artifact mutation.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (advisory) - cited because the scoping discusses `verified` and `retired` lifecycle states in the retire-ready candidate surface. The CLI exposes these states as observability outputs; it does not transition them.

## Clause Scope Clarification (Not a Bulk Operation)

Per the GOV-STANDING-BACKLOG-001 bulk-ops clause-scope clarification convention: this proposal scopes a READ-ONLY status-report CLI. It introduces no backlog mutation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change. The implementation Slice 2 will likewise be read-only. Evidence pattern: this is an inventory and observability proposal; matched tokens include "status", "report", "JSON output", "read-only", "no DB writes".

## Prior Deliberations

- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE - the principle's first concrete manifestation cited in canonical rule files is `GTKB-ARTIFACT-RECORDER-CLI`. Slice 2 is a second concrete manifestation under the same principle.
- DELIB-S342-BACKLOG-WORK-ITEMS-CANONICAL-PIVOT - MemBase work_items is the canonical backlog source of truth. This proposal's status CLI reads from that canonical surface.
- `bridge/gtkb-discoverability-cli-slice-1-008.md` (VERIFIED) - Slice 1 design and acceptance pattern. Slice 2 follows the same scope-discipline approach (single CLI verb per slice).
- `bridge/gtkb-cli-discoverability-doctor-json-backlog-show-003.md` (WITHDRAWN) - failed sibling that tried bundling multiple discoverability verbs in one proposal. Slice 2 deliberately picks one verb (`backlog status`) to follow Slice 1's successful pattern.
- `bridge/gtkb-gt-backlog-add-cli-007.md` (WITHDRAWN) - `gt backlog add` shipped under separate slug `gtkb-backlog-add-cli-slice-1` (VERIFIED). Slice 2 here is a sibling verb to `add`/`list`/`show`, not a duplicate.
- `bridge/gtkb-s373-triage-umbrella-001.md` (NEW, this morning) - the parallel S373 session's working-tree commit-organization triage. Distinct scope from this implementation-gap triage filing; the umbrella explicitly defers gaps 2-7 to a later session, which this filing satisfies.

## Requirement Sufficiency

Existing requirements sufficient. No new specification capture required. The proposed CLI is a read-only observability surface on existing MemBase tables and bridge/INDEX.md. The deterministic-services principle (DELIB-S312) authorizes deterministic plumbing without per-feature requirement capture. The Slice 1 VERIFIED precedent established the pattern of read-only discoverability CLI work proceeding under this principle without per-slice requirement specification.

## target_paths (Scoping output)

This SCOPING proposal does not authorize source mutation. The Slice 2 implementation proposal that follows GO will list concrete target_paths from this set (subject to PAUTH envelope coverage):

- `groundtruth-kb/src/groundtruth_kb/cli_backlog_status.py` (planned new module)
- `groundtruth-kb/src/groundtruth_kb/cli.py` (planned subcommand registration only)
- `platform_tests/scripts/test_cli_backlog_status.py` (planned new tests)

Only the planned files above are subject to mutation by the follow-on implementation. No protected-narrative path edit. No schema migration. No MemBase write path. No bridge/INDEX.md mutation by the implementation itself.

## Spec-Derived Verification Plan (for Slice 2 implementation)

Per DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, each acceptance criterion maps to an executable test:

| Acceptance criterion | Verification |
|---|---|
| `gt backlog status` exits 0 and prints projects-with-WI-rollup | unit test: assert exit 0, parse JSON output, schema-validate against expected keys |
| `--project <PID>` filters output to one project | unit test: assert single-project output |
| `--with-orphans` surfaces open WIs without active membership | unit test with fixture: 1 orphan WI, output contains its id |
| `--with-retire-ready` surfaces projects whose WIs are all terminal | unit test with fixture: 1 retire-ready project, output flags it |
| `--with-verified-coverage` annotates each WI with bridge VERIFIED count | unit test with fixture bridge/INDEX.md and fixture VERIFIED file citing WI |
| `--json` produces machine-parseable output | unit test: `json.loads(stdout)` succeeds, schema-validates |
| Read-only (no DB writes) | unit test: snapshot db file checksum before and after; assert unchanged |
| Doubled-prefix flag surfaces phantom PROJECT-PROJECT-* projects | unit test with fixture: project named `PROJECT-PROJECT-X`, output flags it |

## Acceptance Criteria

- Codex issues GO on this scoping proposal with explicit confirmation that:
  - Slice 2's read-only single-verb scope is appropriate (vs the WITHDRAWN bundled-verb sibling's approach).
  - `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI` is appropriate authorization vehicle for the follow-on implementation, or names a focused PAUTH variant to create.
  - The Slice 2 implementation proposal that follows is authorized to be filed under this thread family's slug pattern.
- If GO, file `gtkb-discoverability-cli-slice-2-implementation-001` next session as the implementation NEW.
- If NO-GO, revise scope per Codex findings via -002 REVISED (not in-place edit of -001).

## Risk and Rollback

- Risk: scope creep at Slice 2 implementation (adding `gt projects status-report` and similar without separate scoping). Mitigation: this scoping deliberately constrains to one verb; the implementation proposal must match this scope.
- Risk: bridge/INDEX.md parse fragility in `--with-verified-coverage`. Mitigation: reuse the canonical `groundtruth_kb.bridge.detector.parse_index` parser already in scanner code; do not write a second parser.
- Risk: the auto-retire scanner defect (Gap 1, in flight at `gtkb-project-completion-scanner-addressing-thread-fix-implementation` at NO-GO -002 today) overlaps with the `--with-retire-ready` flag. Mitigation: Slice 2 implementation reads the scanner's `verified_work_items()` function as a library after the D3+D4 fix lands; if the fix is unmerged when Slice 2 lands, document the temporary over-broad-citation caveat in the `--help` output.
- Risk: doubled-prefix project rows (caused by the `backlog add` defect tracked in PROJECT-GTKB-RELIABILITY-FIXES) contaminate the projects-list output. Mitigation: Slice 2 emits a `doubled_prefix_flag` per project to surface the drift; cleanup is out of scope (separate reliability-fast-lane filing).
- Rollback: scoping introduces no system state changes. Withdrawal is via the WITHDRAWN status convention on a fresh -002 if needed.

## Owner Decisions / Input

This scoping proposal proceeds on owner AskUserQuestion approvals captured in this session:

1. DECISION-0758 (S373 this session, conversation `00d6b362-374c-4c5c-bf69-b7c23d0f2f58`): resolved with "start the triage" via UserPromptSubmit hook capture. Opens the implementation-gap triage path.
2. Triage scope choice (this session AUQ): "Implementation gaps (Recommended)" - owner selected this option via AskUserQuestion. Durable evidence is the AUQ tool record.
3. Gap 5 filing choice (this session AUQ): "File slice-2 scoping now (Recommended)" - owner selected this option via AskUserQuestion. Durable evidence is the AUQ tool record. Authorizes this filing as `gtkb-discoverability-cli-slice-2-scoping-001`.

The parallel S373 session (same harness B, conversation `8c70eac3-4056-47ed-9910-27f1a0b42708`) filed `gtkb-s373-triage-umbrella-001` and `gtkb-project-completion-scanner-addressing-thread-fix-implementation-001` earlier today against the same DECISION-0758 resolution but with a different scope interpretation (working-tree commit triage plus Gap 1 LIVE-RISK fix). This filing is the planned next step that the umbrella explicitly defers ("triage umbrella stays as a working-tree draft"). No scope collision.

## Codex Review Asks

1. Confirm or NO-GO the single-verb scope discipline (vs the bundled-verb pattern that WITHDREW in `gtkb-cli-discoverability-doctor-json-backlog-show-003`).
2. Confirm `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI` is appropriate authorization vehicle for the follow-on Slice 2 implementation, or require a focused PAUTH variant.
3. Flag any specification this proposal should cite but does not.
4. Flag any scope element that belongs in a sibling scoping proposal rather than Slice 2.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
