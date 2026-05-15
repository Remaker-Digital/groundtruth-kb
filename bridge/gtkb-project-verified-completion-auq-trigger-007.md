# Implementation Report (post-implementation): Project VERIFIED-Completion Owner-Confirmed AUQ Trigger (WI-3316)

Status: NEW
Document: gtkb-project-verified-completion-auq-trigger
Version: 007
Responds to: bridge/gtkb-project-verified-completion-auq-trigger-006.md (Codex GO)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-15
Session: S352
Project Authorization: PAUTH-GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001-MECHANICAL-ENFORCEMENT-OF-THE-GOVERNANCE-CHAIN
Project: GTKB-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT-001
Work Item: WI-3316
target_paths: ["scripts/project_verified_completion_scanner.py", ".claude/hooks/project-completion-surface.py", ".codex/gtkb-hooks/project-completion-surface.py", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "platform_tests/scripts/test_project_verified_completion_scanner.py", "platform_tests/hooks/test_project_completion_surface.py", "groundtruth-kb/tests/test_project_artifacts.py", ".claude/settings.json", ".codex/hooks.json"]

## Summary

The GO'd REVISED-2 proposal (`-005`, Codex GO at `-006`) is implemented. IP-1
through IP-4 landed within the nine approved target paths. The full
verification suite passes (25 tests) and ruff is clean. IP-5 (`GOV-PROJECT-
VERIFIED-COMPLETION-RETIREMENT-001` remaining `specified`) is unchanged.

## Implementation-Start Authorization

`python scripts/implementation_authorization.py begin --bridge-id gtkb-project-verified-completion-auq-trigger`
was run before any protected edit.

- packet_hash: `sha256:1c5a825dc1753fc69d2c96ec50d462cd5c12e5249cbff3efcd488674fc3fdac7`
- proposal_file: `bridge/gtkb-project-verified-completion-auq-trigger-005.md`
- go_file: `bridge/gtkb-project-verified-completion-auq-trigger-006.md`
- target_path_globs: the nine approved paths.

Concurrent Prime sessions overwrote the shared `current.json` pointer during
this work (the documented packet-contention race); the packet remains intact in
the per-bridge cache at
`.gtkb-state/implementation-authorizations/by-bridge/gtkb-project-verified-completion-auq-trigger.json`.

## Changes Made

**IP-1 — `scripts/project_verified_completion_scanner.py` (new).** Read-only
CLI + library. `scan()` queries `current_project_authorizations` for active
rows; for each, an authorization is completion-ready iff it lists at least one
work item and every listed work item is cited by a bridge thread whose latest
`bridge/INDEX.md` status is `VERIFIED`. VERIFIED detection uses the canonical
`groundtruth_kb.bridge.detector.parse_index` parser, not ad-hoc regex. `--json`
and `--all` flags. No DB or bridge-file writes.

**IP-2 / IP-2b — `.claude/hooks/project-completion-surface.py` and
`.codex/gtkb-hooks/project-completion-surface.py` (new).** UserPromptSubmit
Axis-2 surface hooks, kept byte-identical for Claude/Codex parity
(`parents[2]` resolves the repo root from either location). On each prompt the
hook runs the IP-1 scanner and surfaces ONE completion-ready authorization not
yet surfaced this session as `additionalContext`, instructing the agent to
confirm completion via `AskUserQuestion`. Per-session idempotency via a cache
under `.gtkb-state/project-completion-surface/`. Fire-and-forget; never mutates
state; `GTKB_NO_PROJECT_COMPLETION_SURFACE=1` disables it.

**IP-3 — `groundtruth-kb/src/groundtruth_kb/project/lifecycle.py` (modified).**
Added `ProjectLifecycleService.complete_project_authorization()` plus the
`COMPLETED_PROJECT_AUTHORIZATION_STATUS` constant, the `_WORK_ITEM_LINE_RE`
metadata-line regex, and the `_authorization_work_item_ids` / `_verified_work_items`
helpers. The method's state machine: (1) load authorization, reject if not
active; (2) owner-confirmation gate — the cited deliberation must exist, have
`source_type='owner_conversation'` AND `outcome='owner_decision'`, and its text
must reference the project or authorization being completed; (3) re-run the
readiness check; (4) `update_project_authorization(status="completed")`;
(5) retire the project iff no other active authorization remains; (6) return
`{"authorization": ..., "project_retired": ...}`.

**IP-4 — `.claude/settings.json` and `.codex/hooks.json` (modified).** Registered
`project-completion-surface.py` as a `UserPromptSubmit` hook in both files.

**IP-5.** `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` remains `specified`.
Promotion to `implemented` is a separate governed mutation (formal-artifact-
approval packet); it is recommended now that IP-1..IP-4 have landed and is not
performed in this report.

### Deviations from the GO'd proposal (disclosed)

Two minor, necessary refinements within the approved target paths:

1. **IP-3 readiness re-check mechanism.** Proposal IP-3 step 3 said "re-run the
   IP-1 readiness check." Rather than importing the `scripts/` scanner from
   package code (a fragile cross-layer import), `_verified_work_items()` in
   `lifecycle.py` re-implements the check inline by delegating to the same
   canonical `groundtruth_kb.bridge.detector.parse_index` parser. Both call
   sites compute identical results from the same parser; the duplication is two
   thin wrappers, not two parsers.
2. **`complete_project_authorization()` signature.** The proposal's signature
   snippet omitted a way to locate `bridge/INDEX.md`. The implemented method
   adds a required keyword-only `project_root: Path` parameter so the readiness
   re-check (step 3) is explicit and unit-testable. No other parameter changed.

## Specification Links

- GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001 — source spec; owner-confirmed-via-AUQ completion + retirement.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 — parent governance for project authorizations.
- DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 — envelope schema; the `completed` status lives here.
- PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 — preserved; the scanner is read-only and the surface never mutates.
- SPEC-AUQ-POLICY-ENGINE-001 — AUQ-only enforcement; the surface drives an AskUserQuestion.
- SPEC-AUQ-NO-LLM-CLASSIFIER-001 — deterministic VERIFIED detection, no LLM.
- ADR-CODEX-HOOK-PARITY-FALLBACK-001 — the two hook files are kept byte-identical for Claude/Codex parity.
- GOV-FILE-BRIDGE-AUTHORITY-001 — the scanner reads `bridge/INDEX.md` as canonical state.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — every target path is in-root under `E:\GT-KB`.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — governing specs cited.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — spec-to-test mapping below.
- GOV-STANDING-BACKLOG-001 — WI-3316 is a tracked work item.
- GOV-ARTIFACT-APPROVAL-001 — project completion/retirement is a governed mutation; the owner-decision deliberation is the approval evidence.
- DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT — owner-decision evidence.

## Clause Scope Clarification (Not a Bulk Operation)

This report references WI-3316 only as its own provenance metadata. It performs
no bulk work-item transition and no standing-backlog cleanup. The feature itself
surfaces completion-ready authorizations one at a time and never auto-mutates.
The `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` clause, if triggered by
the literal token `work item`, is satisfied by the bridge thread's own audit
trail and the formal-artifact-approval evidence cited under Owner Decisions /
Input, and is not applicable as a bulk operation.

## In-Root Placement Evidence

All nine target paths resolve inside `E:\GT-KB`. The two new hook files live
under `.claude/hooks/` and `.codex/gtkb-hooks/`; the scanner under `scripts/`;
the service change under `groundtruth-kb/src/`; the three test files under
`platform_tests/` and `groundtruth-kb/tests/`. Session idempotency state under
`.gtkb-state/project-completion-surface/` is gitignored runtime state and is
intentionally not a target path. No path is under `applications/`, none leaves
`E:\GT-KB`.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`
specifies the detection trigger, AUQ confirmation channel, transition target,
and the prohibition on auto-transition. No new or revised requirement was needed.

## Prior Deliberations

- `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT` — owner directive; AUQ selecting the Owner-confirmed-via-AUQ variant.
- `bridge/gtkb-project-verified-completion-auq-trigger-002.md` / `-004.md` — the two prior NO-GOs (omitted paths/layer inversion; owner-confirmation semantics + parity false-floor) closed by REVISED-1 and REVISED-2.
- `bridge/gtkb-project-verified-completion-auq-trigger-006.md` — the Codex GO whose Implementation Conditions this report satisfies.

## Specification-Derived Verification

All tests in the three approved test files. Spec-to-test mapping:

| Requirement | Test | File |
|---|---|---|
| all WIs VERIFIED -> completion-ready | `test_scanner_marks_all_verified_authorization_completion_ready` | test_project_verified_completion_scanner.py |
| one WI non-VERIFIED -> not ready | `test_scanner_skips_authorization_with_one_non_verified_wi` | scanner test |
| scanner is read-only | `test_scanner_makes_no_db_writes` | scanner test |
| surface one-at-a-time | `test_hook_surfaces_one_authorization_per_prompt` | test_project_completion_surface.py |
| surface idempotent per session | `test_hook_does_not_resurface_same_authorization_same_session` | hook test |
| Claude hook exercises both files (parity) | `test_claude_hook_surfaces_completion_ready_authorization` | hook test |
| Codex hook exercises both files (parity) | `test_codex_hook_surfaces_completion_ready_authorization` | hook test |
| surface silent when nothing ready | `test_hook_silent_when_no_completion_ready_authorization` | hook test |
| owner-confirmation: missing deliberation rejected | `test_complete_rejects_missing_deliberation` | test_project_artifacts.py |
| owner-confirmation: LO-review deliberation rejected | `test_complete_rejects_lo_review_deliberation` | service test |
| owner-confirmation: informational deliberation rejected | `test_complete_rejects_informational_deliberation` | service test |
| owner-confirmation: no-go deliberation rejected | `test_complete_rejects_no_go_deliberation` | service test |
| owner-confirmation: owner-decision for wrong project rejected | `test_complete_rejects_owner_decision_for_other_project` | service test |
| owner-confirmation: valid owner-decision accepted | `test_complete_accepts_valid_owner_decision_deliberation` | service test |
| transition rejected when authorization not active | `test_complete_rejects_non_active_authorization` | service test |
| transition rejected when not all WIs VERIFIED | `test_complete_rejects_when_a_wi_not_verified` | service test |
| sole active authorization -> project retired | `test_complete_sole_active_authorization_retires_project` | service test |
| other active authorizations remain -> project NOT retired | `test_complete_with_other_active_authorization_keeps_project_active` | service test |

Commands executed and observed results:

```text
python -m pytest platform_tests/scripts/test_project_verified_completion_scanner.py platform_tests/hooks/test_project_completion_surface.py groundtruth-kb/tests/test_project_artifacts.py -q
=> 25 passed in 15.36s

python -m ruff check scripts/project_verified_completion_scanner.py groundtruth-kb/src/groundtruth_kb/project/lifecycle.py .claude/hooks/project-completion-surface.py .codex/gtkb-hooks/project-completion-surface.py platform_tests/scripts/test_project_verified_completion_scanner.py platform_tests/hooks/test_project_completion_surface.py groundtruth-kb/tests/test_project_artifacts.py
=> All checks passed!
```

Per REVISED-2 F2, `check_codex_hook_parity.py` is not used; parity is proven by
the explicit dual-hook tests `test_claude_hook_*` and `test_codex_hook_*`. The
bare `ruff` executable is not on PATH in this environment; the lint command
actually used was `python -m ruff check ...` (one import-ordering issue was
auto-fixed; the suite was re-run green afterward).

## Acceptance Criteria Check

- IP-1 scanner lands; 3 scanner tests PASS — PASS.
- IP-2/IP-2b surface hooks land (Claude + Codex parity); the hook test file exercises BOTH hook files; all hook tests PASS — PASS.
- IP-3 `complete_project_authorization()` lands in `lifecycle.py` (not `db.py`); owner-confirmation gate validates owner-decision semantics; all 10 service tests PASS, including the negative owner-confirmation tests and both retirement-rule cases — PASS.
- IP-4 hook registered in both `.claude/settings.json` and `.codex/hooks.json` (both files validated as well-formed JSON) — PASS.
- IP-5 `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` remains `specified` — PASS.
- No regression: the pre-existing `test_project_artifacts.py` tests still pass within the 25-test run — PASS.

## Recommended Commit Type

`feat:` — a new owner-confirmed project-completion + retirement governance
surface across a read-only scanner, Axis-2 parity hooks, a project-lifecycle
service method, and two hook registrations. No spec status promotion in this
slice.

## Owner Decisions / Input

- **2026-05-14 S350 (AskUserQuestion)** — owner answered "VERIFIED→COMPLETED transition: automatic or owner-confirmed?" with "Owner-confirmed via AUQ"; archived in `DELIB-S350-SPEC-PROJECT-WI-BRIDGE-ENFORCEMENT`. This is the requirement the owner-confirmation gate enforces.
- **2026-05-15 S350+** — owner directive "Proceed with WI-3316 and WI-3317"; reaffirmed S352 by the owner surfacing this GO'd thread as Prime-actionable.
- No new owner decision is required to verify this report. The change does not deploy, does not promote a specification, and crosses no release gate.
