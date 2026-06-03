NEW

# Post-implementation report: shared session-id resolver unification (WI-4270)

bridge_kind: implementation_report

author_identity: Prime Builder
author_harness_id: B
author_session_context_id: f4e17460-820d-4c6b-a150-24162f87f415
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: explanatory output style; Claude Code

target_paths: ["scripts/gtkb_session_id.py", "scripts/bridge_claim_cli.py", "scripts/workstream_focus.py", ".claude/hooks/bridge-compliance-gate.py", ".claude/hooks/bridge-axis-2-surface.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_gtkb_session_id.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/hooks/test_bridge_compliance_gate_work_intent.py", "platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py", "platform_tests/skills/test_bridge_propose_helper_work_intent.py", "platform_tests/hooks/test_workstream_focus_session_role_marker.py", "platform_tests/scripts/test_doctor_session_role_marker.py"]

Project Authorization: PAUTH-WI-4270-SESSION-ID-SHARED-RESOLVER
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4270

## Summary

Implements the GO'd REVISED-1 proposal at
`bridge/gtkb-session-id-shared-resolver-unification-003.md` (Codex GO at
`-004`). Behavior-preserving unification of the session-id env-var membership
into one authority module while preserving both deliberate per-surface
precedence policies. The underlying defect (the `CLAUDE_CODE_SESSION_ID`
membership omission) was already fixed and committed at `ea2040a5` (VERIFIED at
the predecessor thread `-012`); this change does NOT re-fix it — it only
de-duplicates.

New module `scripts/gtkb_session_id.py` (stdlib-only, hook-safe) is the single
membership authority (`SESSION_ID_ENV_VARS`, a frozen 7-member set) and the home
of both order constants (`BRIDGE_WORK_INTENT_ORDER`, the 7-member
live-harness-first permutation; `MARKER_CONTINUITY_ORDER`, the 5-member
`GTKB_SESSION_ID`-first documented subset) plus `resolve_session_id`. Consumers
migrated to share that authority; the marker family preserves its
`GTKB_SESSION_ID`-first behavior, and the packaged doctor keeps a parity-tested
verbatim copy (no repo-root `scripts/` import).

## Specification Links

Blocking (required) cross-cutting specs:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (v1, verified) — a single membership authority
  hardens the work-intent contract against the recurrence class.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (v1, specified).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` (v1, specified) — concrete
  PAUTH/Project/WI metadata cited above.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` (v1, specified) — WI-4270
  is an active member of `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, included by
  the cited PAUTH (validated by `implementation_authorization.py begin`).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (v1, specified) — the
  spec-to-test mapping below maps each spec to executed tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (v1, specified) — all touched files
  are in-root; `applications/Agent_Red/` untouched.

Advisory cross-cutting specs:

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `GOV-STANDING-BACKLOG-001` (v1).

Predecessor + precedent:

- `bridge/gtkb-claude-code-session-id-env-var-gap-001.md` … `-012.md` (minimal
  fix VERIFIED + committed `ea2040a5`).
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` + `DCL-SESSION-ROLE-RESOLUTION-001`
  (v1, specified) — established the marker-continuity precedence and
  `CLAUDE_CODE_SESSION_ID` recognition this change centralizes.

Rule-cited soft authority:

- `.claude/rules/file-bridge-protocol.md`;
  `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (one membership authority +
  drift-lock tests are the deterministic-service realization of duplicated
  env-list plumbing).

## Owner Decisions / Input

Owner AskUserQuestion decisions authorizing this work (the only valid
owner-decision channel per `.claude/rules/prime-builder-role.md`):

1. **DELIB-20260625** — owner authorization to implement WI-4270 via
   `PAUTH-WI-4270-SESSION-ID-SHARED-RESOLVER` (2026-06-03 "Authorize + file
   now").
2. **2026-06-03 marker-precedence AUQ — "Shared SET, per-surface order (full
   unification)"** — the owner chose to keep the marker writer + doctor unified
   to the shared module while preserving their distinct `GTKB_SESSION_ID`-first
   precedence (over scoping the marker writer out, and over parking the thread).
   This is the design implemented here.

No new owner decision was required during implementation. One pre-existing
condition (the gate template-parity drift, below) is surfaced for owner/LO
awareness but is out of WI-4270 scope and required no owner decision.

## Prior Deliberations

- `DELIB-20260625` — owner authorization to implement WI-4270.
- `bridge/gtkb-session-id-shared-resolver-unification-002.md` — Codex NO-GO F1
  (marker precedence conflict); closed by REVISED-1 `-003`.
- `bridge/gtkb-session-id-shared-resolver-unification-004.md` — Codex GO with the
  five implementation-start conditions carried into this report (below).
- `bridge/gtkb-claude-code-session-id-env-var-gap-012.md` — predecessor minimal
  fix VERIFIED.

## Implemented Changes

New module:

- `scripts/gtkb_session_id.py` — `SESSION_ID_ENV_VARS` (frozenset, membership
  authority), `BRIDGE_WORK_INTENT_ORDER` (7-tuple), `MARKER_CONTINUITY_ORDER`
  (5-tuple), `resolve_session_id(explicit, *, order, environ)`. Stdlib-only
  (`os`, `collections.abc`); no import-time side effects.

Bridge work-intent family (membership now sourced from the shared authority;
each surface's resolution behavior unchanged):

- `scripts/bridge_claim_cli.py` — direct import of `resolve_session_id` +
  `BRIDGE_WORK_INTENT_ORDER`; `SESSION_ENV_VARS` aliases the canonical order;
  `_resolve_session_id` delegates to the shared resolver (arg-first) and keeps
  the CLI raise-on-empty contract.
- `.claude/hooks/bridge-compliance-gate.py` and its byte-for-byte template
  mirror `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` — fail-soft
  `try/except` import of `BRIDGE_WORK_INTENT_ORDER as WORK_INTENT_SESSION_ENV_VARS`
  with a verbatim local fallback (same pattern the gate already uses for
  `REQUIRED_AUTHOR_METADATA_FIELDS`). Payload-first precedence in
  `_resolve_work_intent_session_id` is unchanged.
- `.claude/hooks/bridge-axis-2-surface.py` — same fail-soft import; local
  resolvers unchanged.
- `.claude/skills/bridge-propose/helpers/write_bridge.py` and its template mirror
  `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` —
  same fail-soft import; `resolve_work_intent_session_id` keeps its env-only
  resolution + raise contract.

Marker-continuity family (`GTKB_SESSION_ID`-first preserved):

- `scripts/workstream_focus.py` — `_SESSION_ID_ENV_FALLBACKS` delegates to
  `MARKER_CONTINUITY_ORDER` via this module's existing dual-import idiom
  (`scripts.*` package path; bare-name fallback under direct script execution).
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — verbatim copy retained
  (NOT imported, per the packaging constraint / Codex Review Ask 2); only the
  stale comment was corrected to reference `gtkb_session_id.MARKER_CONTINUITY_ORDER`
  (the prior `scripts.session_role_resolution._SESSION_ID_ENV_FALLBACKS`
  reference named a constant that does not exist there).

Tests (T1-T7) added/extended — see the mapping below.

## Spec-to-Test Mapping

| Spec / clause | Tests / evidence |
|---|---|
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | T1 `test_gtkb_session_id.py` (7 precedence tests) + T2 (5 drift-lock tests). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (single membership authority) | T2 drift-lock: `set(BRIDGE_WORK_INTENT_ORDER) == set(SESSION_ID_ENV_VARS)`, `set(MARKER_CONTINUITY_ORDER) <= set(SESSION_ID_ENV_VARS)`, no duplicates/unknown members, `CLAUDE_CODE_SESSION_ID` locked into all surfaces. |
| Bridge family behavior preserved | T3 `test_bridge_claim_cli.py` (CLI resolves `CLAUDE_CODE_SESSION_ID` end-to-end without `--session-id`; `SESSION_ENV_VARS` aliases canonical); T4 `test_bridge_compliance_gate_work_intent.py` (payload-first preserved; env equals canonical; fail-soft fallback == canonical for live AND template); T5 `test_bridge_axis_2_surface_work_intent.py` + `test_bridge_propose_helper_work_intent.py` (equals-canonical + fail-soft fallback). |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` + `DCL-SESSION-ROLE-RESOLUTION-001` (marker behavior preserved) | T6 `test_workstream_focus_session_role_marker.py` (existing `GTKB_SESSION_ID`-first assertions still pass; new parity to `MARKER_CONTINUITY_ORDER`); T7 `test_doctor_session_role_marker.py` (existing parity + new parity to `MARKER_CONTINUITY_ORDER`). |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All 16 changed files are in-root; no `applications/` paths touched. |

## Test Execution (commands + observed results)

Workspace python is the canonical PowerShell-workspace interpreter (pytest 9.0.2;
the `gt`-venv lacks a runnable pytest, matching CI's `python -m pytest`).

```
python -m pytest platform_tests/scripts/test_gtkb_session_id.py `
  platform_tests/scripts/test_bridge_claim_cli.py `
  platform_tests/hooks/test_bridge_compliance_gate_work_intent.py `
  platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py `
  platform_tests/skills/test_bridge_propose_helper_work_intent.py `
  platform_tests/hooks/test_workstream_focus_session_role_marker.py `
  platform_tests/scripts/test_doctor_session_role_marker.py -q
=> 88 passed
```

Per-file: `test_gtkb_session_id.py` 12; `test_bridge_claim_cli.py` 8;
`test_bridge_compliance_gate_work_intent.py` 20;
`test_bridge_axis_2_surface_work_intent.py` 7;
`test_bridge_propose_helper_work_intent.py` 6;
`test_workstream_focus_session_role_marker.py` 17;
`test_doctor_session_role_marker.py` 18.

## Code-Quality Gates (separate: lint AND format)

Run on all 15 changed `.py` files via `groundtruth-kb\.venv\Scripts\ruff.exe`:

```
ruff check <15 changed .py>           => All checks passed!
ruff format --check <15 changed .py>  => 15 files already formatted
```

## Template Mirror Parity

The two template mirrors received the byte-identical edit applied to their live
counterparts:

- `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` — same fail-soft
  import block as `.claude/hooks/bridge-compliance-gate.py`.
- `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py` —
  same fail-soft import block as the live helper.

The gate template-parity test
(`platform_tests/hooks/test_bridge_compliance_gate_hard_block_workspace.py::test_hook_matches_template_or_documented_divergence`)
was ALREADY FAILING at the pre-change baseline (live 1303 lines vs template 1261
lines — a ~42-line pre-existing content divergence unrelated to WI-4270, e.g.
the template lacks the `DEFERRED` author-metadata status and the `DEFERRED`
gate-handling lines). After this change the live/template count-difference is
still exactly 42 lines, and the new shared-resolver import block does NOT appear
in the live-vs-template diff (it is byte-identical in both mirrors). My change
neither introduces nor removes divergence; reconciling the pre-existing 42-line
drift is out of WI-4270 scope (Codex GO `-004` condition 5: do not bundle
unrelated changes). The `write_bridge.py` template is a scaffold variant that was
never byte-identical to the live helper (no byte-parity test exists for it; only
substring/function-presence checks, which still pass).

## Pre-Existing Failures Outside WI-4270 Scope (full disclosure)

A broader `platform_tests/hooks/` regression sweep surfaced 45 failures. NONE are
caused by WI-4270. Proof:

1. My change surface is exactly the 16 target files (`git diff --stat` plus two
   untracked new files); no other file was modified or deleted.
2. My 88-test suite for the exact changed modules all passes.
3. The shared working tree is contaminated by concurrent sessions: large in-flight
   edits to `.claude/hooks/session_start_dispatch.py` (-690 lines),
   `.codex/gtkb-hooks/session_start_dispatch.py` (-684 lines), `cli.py`,
   `lifecycle.py`, `AGENTS.md`, `CLAUDE.md`, `bridge/INDEX.md`,
   `pending-owner-decisions.md` — none of which are WI-4270 files. These explain
   the `session_start_marker_invalidation`, glossary, narrative, credential-scan,
   and SKILL-adapter-parity failures.
4. `.claude/hooks/bridge-stop-drain.py` is absent at HEAD (confirmed via
   `git cat-file -e HEAD:...`), explaining the 12 `test_bridge_stop_drain.py`
   FileNotFoundError failures.
5. The only failing files that load a module I changed are
   `test_workstream_focus.py` (startup-relay cache failure) and
   `test_codex_bridge_compliance_gate.py` (work-intent claim-missing deny). Both
   were reproduced IDENTICALLY in a clean detached-HEAD git worktree under `.tmp/`
   that contains NONE of my changes — confirming they are pre-existing. (In that
   clean worktree, `test_codex_skill_adapter_parity_check` passes, confirming its
   main-tree failure is concurrent-session SKILL contamination.)

## Recommended Commit Type

`refactor` — behavior-preserving de-duplication of duplicated env-var lists into
one shared authority + drift-lock tests. No new capability surface; the
underlying defect was already fixed at `ea2040a5`.

The commit will be path-scoped to ONLY the 16 WI-4270 files plus this bridge
thread's audit-trail files (exact `git add`; never `git add -A`) because the
working tree is shared with active concurrent sessions, and the dev-environment
inventory-drift pre-commit gate requires a `bridge/*.md` staged in the same
commit.

## Risk / Rollback

Low. Behavior-preserving: both families keep their exact current order +
membership; the gate import is fail-soft (never throws); the doctor keeps a
parity-tested copy honoring the packaging boundary; drift-lock + parity tests
prevent silent divergence. Rollback: `git revert` the implementation commit; the
committed minimal fix `ea2040a5` stays in force, so reverting does not
reintroduce the original `CLAUDE_CODE_SESSION_ID` defect.

## KB/MemBase Mutation

None. This implementation performs no KB/MemBase mutation and writes no
`groundtruth.db` row; it touches only source files and tests (see `target_paths`).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
