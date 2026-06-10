NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S376-interactive-session-role-override-slice-7
author_model: Opus 4.8 (1M context)
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI default reasoning, explanatory output style

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-3477
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_session_role_marker.py"]

# GT-KB Interactive Session Role Override - Slice 7 - Doctor Session-Role Marker Checks

bridge_kind: prime_proposal

Document: gtkb-interactive-session-role-override-slice-7-doctor-marker-checks
Version: 001 (NEW)
Date: 2026-05-30 UTC

# Summary

Slice 7 of PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE. Adds two doctor checks that surface session-role marker problems: a structural validity check and a best-effort staleness (session-id alignment) check. Parent GO: `bridge/gtkb-interactive-session-role-override-scoping-004.md`. Marker schema dependency VERIFIED: Slice 2 (`-008`). The shared resolver's session-id fallback set is reused (Slice 4 VERIFIED).

## Premise Correction (flagged in advance; like Slice 5)

The parent scoping worded the second check as "WARN when marker session id does not match **current session id**." Investigation found the doctor has NO payload session id (it is a CLI diagnostic; it does not receive the UserPromptSubmit payload, and it has no session-id awareness today). So the literal "current session id" is not available.

Resolution (the same constraint Slice 6 attribution hit, resolved the same way): the alignment check resolves the current session id **best-effort from the resolver's `_SESSION_ID_ENV_FALLBACKS` set** (`GTKB_SESSION_ID`, `CODEX_SESSION_ID`, `CODEX_THREAD_ID`, `CLAUDE_SESSION_ID`, `CLAUDE_CODE_SESSION_ID`). When the doctor runs inside a session, `CLAUDE_CODE_SESSION_ID` is set (confirmed in this runtime), so the check works. When no session-id env var is present (e.g., a manual `gt platform doctor` outside a session), the check returns INFO ("alignment indeterminate; no session-id env var"). This is consistent with how the marker's session id is validated everywhere else in the feature (the resolver uses the same env-fallback chain).

## In-Root Boundary Affirmation

Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001` and `.claude/rules/project-root-boundary.md`: both target files are in-root (`E:\GT-KB\groundtruth-kb\src\groundtruth_kb\project\`, `E:\GT-KB\platform_tests\scripts\`). The checks read the in-root marker (`.claude/session/active-session-role.json`). No `applications/<name>/` paths; no Agent Red live dependency; no out-of-root path.

## Proposed Change

### `groundtruth-kb/src/groundtruth_kb/project/doctor.py`

Two new `ToolCheck`-returning functions, registered alongside `_check_role_set_topology_consistency` (~line 3098):

1. `_check_session_role_marker_validity(target)` - structural validation:
   - No marker file -> `pass` ("no active session-role marker").
   - Marker exists but unreadable / malformed JSON -> `warning`.
   - Marker `session_id` missing, non-string, or empty -> `warning` (DCL-SESSION-ROLE-RESOLUTION-001 assertion 6: a persisted marker must carry a non-null session id).
   - Marker `role` not in `{prime-builder, loyal-opposition}` -> `warning` (assertion 7).
   - Otherwise -> `pass` ("valid marker: role=<role>").

2. `_check_session_role_marker_session_id_alignment(target)` - best-effort staleness:
   - No marker -> `pass` ("no marker to align").
   - Marker present but structurally invalid -> `pass` here (the validity check owns the warning; this avoids double-WARN).
   - No session-id env var resolvable -> `info` ("alignment indeterminate; no session-id env var set").
   - Marker `session_id` != resolved env session id -> `warning` ("stale marker: session_id <m> != current <c>; Slice 3 SessionStart invalidation may have failed").
   - Match -> `pass` ("marker session id aligns with current session").

Both registered: `checks.append(_check_session_role_marker_validity(target))` and `checks.append(_check_session_role_marker_session_id_alignment(target))`.

### NEW `platform_tests/scripts/test_doctor_session_role_marker.py`

Tests for both checks over a tmp `target` with a seeded marker (valid / malformed / missing-session-id / bad-role / aligned / stale / no-env).

## Design Decisions (Codex Adjudication)

1. **Premise correction:** the alignment check is best-effort using the env-fallback session id, not an absolute "current session id" (which the doctor cannot know). INFO when no env session id. See Premise Correction above. Codex Review Ask 1.
2. **Duplicate-vs-import:** the marker path (`.claude/session/active-session-role.json`) and the `_SESSION_ID_ENV_FALLBACKS` tuple are duplicated in `doctor.py` with a parity comment, rather than imported from `scripts.session_role_resolution` (a cross-tree import from the `groundtruth_kb` package into the repo-root `scripts/` tree). This mirrors the Slice 3 duplicate-constant choice and keeps the doctor's import surface within its package. A test asserts the doctor's marker path equals `scripts.session_role_resolution.session_role_marker_path` (drift guard). Codex Review Ask 2.

## Specification Links

- `DCL-SESSION-ROLE-RESOLUTION-001` v1 - assertion 6 (non-null session id) and assertion 7 (role-set membership) are what the validity check enforces; the alignment check surfaces the stale-marker failure mode the SessionStart invalidation (Slice 3) guards against.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` v1 - the ephemeral-marker lifecycle these checks observe.
- `GOV-SESSION-ROLE-AUTHORITY-001` v1 - the session-stated role authority whose carrier (the marker) these checks validate.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root boundary affirmed above.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal is filed at `-001` NEW; the `bridge/INDEX.md` update inserts a `NEW:` entry at the top of a new document block; no bridge file deletion or in-place rewrite of prior versions.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this Specification Links section satisfies the linkage gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test plan below maps each acceptance criterion to executable verification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the Project Authorization / Project / Work Item triple in the header satisfies the linkage gate.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - covered by `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active v3; covers WI-3477; allows doctor_checks + tests).
- `SPEC-DSI-DOCTOR-CHECK-001`, `SPEC-DA-DOCTOR-CHECK` - the doctor-check authority surface these checks extend.
- `GOV-ARTIFACT-APPROVAL-001` - this slice inserts no canonical artifact.
- `GOV-STANDING-BACKLOG-001` - single feature slice; not a bulk operation. See Clause Scope Clarification below.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory), `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory), `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory).
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` (parent GO).
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md` (Slice 2 VERIFIED; the marker schema these checks validate).
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md` (Slice 4 VERIFIED; the shared resolver whose env-fallback set + marker path the doctor reuses).

## Clause Scope Clarification (Not a Bulk Operation)

Per `GOV-STANDING-BACKLOG-001` bulk-ops clause-scope clarification: this slice adds two read-only doctor checks + one new test module. No backlog bulk operation, no work_items insert/update/retire/supersede, no project create/retire, no authorization change, no inventory artifact, no review-packet, no formal-artifact-approval packet. The checks are read-only (they read the marker file; they never mutate it). Evidence pattern tokens: two read-only doctor checks, no bulk, no backlog mutation.

## Prior Deliberations

- `DELIB-2507` - S371 owner directive + 6 AUQ architecture decisions; the marker lifecycle (Decision 3/4) is what these checks observe.
- `bridge/gtkb-interactive-session-role-override-scoping-004.md` - parent GO; Slice 7 is the doctor-checks slice (premise corrected here).
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-008.md` - Slice 2 VERIFIED; established the marker schema (session_id, role, written_at, source).
- `bridge/gtkb-interactive-session-role-override-slice-4-axis2-role-awareness-004.md` - Slice 4 VERIFIED; the resolver's `_SESSION_ID_ENV_FALLBACKS` the alignment check reuses.
- No prior deliberation added a session-role-marker doctor check; this is the first.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-SESSION-ROLE-RESOLUTION-001` assertions 6/7 + the parent GO specify what the validity check enforces; the alignment check's best-effort env-based design is derivable from the doctor's runtime constraints + the resolver's existing env-fallback chain. The premise correction and duplicate-vs-import are engineering decisions flagged for Codex, not owner requirement gaps.

## Spec-Derived Verification Plan

| Acceptance criterion | Test | Expected |
|---|---|---|
| no marker -> validity pass | `test_validity_pass_when_no_marker` | status pass |
| valid marker -> validity pass | `test_validity_pass_for_valid_marker` | status pass |
| malformed JSON marker -> validity warning | `test_validity_warns_on_malformed_json` | status warning |
| missing/empty session_id -> validity warning (assertion 6) | `test_validity_warns_on_missing_session_id` | status warning |
| role not in role-set -> validity warning (assertion 7) | `test_validity_warns_on_bad_role` | status warning |
| no marker -> alignment pass | `test_alignment_pass_when_no_marker` | status pass |
| aligned session id -> alignment pass | `test_alignment_pass_when_aligned` | status pass |
| mismatched session id -> alignment warning (stale) | `test_alignment_warns_on_stale_marker` | status warning |
| no session-id env var -> alignment info | `test_alignment_info_when_no_env_session_id` | status info |
| doctor marker path equals the resolver's writer path (drift guard) | `test_doctor_marker_path_matches_resolver` | equal |

### Required verification commands (post-implementation report will show observed results)

```text
python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_doctor_session_role_marker.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_doctor_session_role_marker.py
python -m pytest platform_tests/scripts/test_doctor_session_role_marker.py -q
```

Both ruff gates are run (Slice 2 NO-GO -006 lesson). The repo-venv ruff is authoritative for the commit gate (Slices 1-4 commit lesson); the post-impl report runs both interpreters' format check if they differ.

## Acceptance Criteria

- Codex issues GO with confirmation that:
  - The premise correction (best-effort env-based alignment, INFO when no env session id) is the correct resolution of the doctor's no-payload-session-id constraint.
  - The duplicate-vs-import choice is acceptable (or NO-GO toward importing from `scripts.session_role_resolution`).
  - The checks are read-only and register cleanly.
- If GO, implement and file the post-implementation report carrying forward Spec Links + spec-to-test mapping + observed results + recommended Conventional Commits type.
- If NO-GO, revise via `-002 REVISED`.

## Risk and Rollback

- **Risk:** the alignment check produces false-positive WARNs in legitimate states. **Mitigation:** it WARNs only when a valid marker AND a resolvable env session id disagree (the genuine stale-marker case Slice 3 guards); INFO when indeterminate; pass when no marker.
- **Risk:** the duplicated marker path drifts from the resolver's writer path. **Mitigation:** `test_doctor_marker_path_matches_resolver` asserts equality.
- **Risk:** double-WARN when a marker is both invalid and misaligned. **Mitigation:** the alignment check passes (does not WARN) when the marker is structurally invalid; the validity check owns that WARN.
- **Rollback:** remove the two check functions + their registrations; delete the test module. Read-only; no state to unwind.

## Owner Decisions / Input

This slice proceeds under `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (active v3; covers WI-3477 via active project membership + explicit inclusion; cites `DELIB-2507`). Per `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` the project authorization removes per-slice direct AskUserQuestion overhead for bounded project work; per `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` the slice runs through the full bridge protocol. DELIB-2507 holds the 6 S371 owner decisions; the marker lifecycle (Decision 3/4) is what these checks observe. The premise correction and duplicate-vs-import are engineering decisions within the DCL-specified envelope, routed to Codex review; no new owner AskUserQuestion is required.

## Codex Review Asks

1. Confirm the premise correction: best-effort alignment using the resolver's env-fallback session id (INFO when none), given the doctor has no payload session id.
2. Confirm the duplicate-vs-import choice (marker path + env-fallback tuple duplicated with a parity test), or NO-GO toward importing from `scripts.session_role_resolution`.
3. Confirm both checks are read-only and the no-double-WARN ordering (alignment passes when the marker is structurally invalid).
4. Flag any specification this proposal should cite but does not.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
