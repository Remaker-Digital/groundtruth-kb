NEW

# WI-4540 (POST-IMPLEMENTATION REPORT): Per-session/per-context session-role marker — additive transition, R-B1

bridge_kind: implementation_report
Document: gtkb-wi4540-per-session-role-marker-context-envelope
Version: 005
Author: Prime Builder (Claude Code, harness B — auto-dispatched bridge worker)
Date: 2026-06-14 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 2026-06-14T16-13-30Z-prime-builder-B-7b703b
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: Auto-dispatched cross-harness bridge worker (GTKB_BRIDGE_POLLER_RUN_ID set); Prime Builder durable role (harness B); explanatory output style; model claude-opus-4-8[1m]

Project Authorization: PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-4540-PER-SESSION-MARKER
Project: PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE
Work Item: WI-4540

target_paths: ["scripts/workstream_focus.py", "scripts/bridge_work_intent_registry.py", "scripts/session_start_dispatch_core.py", "scripts/session_role_resolution.py", "scripts/gtkb_session_id.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/scripts/test_bridge_work_intent_registry.py", "platform_tests/hooks/test_session_start_marker_invalidation.py", "platform_tests/hooks/test_workstream_focus_session_role_marker.py"]

implementation_scope: source, test
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

Recommended commit type: fix:

---

## Summary of Implemented Changes

Implements the GO at `-004` (Ollama harness D verdict on REVISED `-003`): **R-B1 id-reconciliation + additive transition**. The single shared marker `.claude/session/active-session-role.json` is supplemented (not replaced) by per-session markers `.claude/session/role-<sanitized_session_id>.json` keyed under the querying context id. The legacy single-file writer, its clobber heuristic, and the legacy SessionStart invalidation are **byte-unchanged** (their pinned tests still pass), so a single-commit revert restores prior behavior.

Implementation start was authorized from the live latest-`GO` via `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi4540-per-session-role-marker-context-envelope` (packet `sha256:54f57ce236d9ad97ec2e57d830f501f6907713d3d48f2d81586c139ea2625480`). The in-flight WI-4527 `maybe_auto_extend` block in `scripts/bridge_work_intent_registry.py` was preserved (all edits were surgical `Edit` replacements localized to `_interactive_marker_role` / `_resolve_go_implementation_eligibility`, far from the `maybe_auto_extend` region).

### Source changes

1. **`scripts/gtkb_session_id.py` (single path authority).** Added the per-session marker path + sanitizer helpers — `sanitize_session_id`, `per_session_role_marker_name`, `session_marker_dir`, `per_session_role_marker_path`, and the `PER_SESSION_ROLE_MARKER_*` constants (incl. the sweep glob) — exported via `__all__`. stdlib-only (`re` + `pathlib`); no import-time side effects, so the hook-safe contract holds. This is the single home so the writer, guard reader, resolver, and sweeper cannot drift apart.

2. **`scripts/workstream_focus.py` (writer — R-B1 multi-key, additive).** Added `_candidate_marker_session_ids` (payload/transcript id + each currently-set `MARKER_CONTINUITY_ORDER` env candidate, de-duplicated, payload-first), `_write_per_session_role_marker` (no clobber-rejection — per-session keying has no contention), and `_write_per_session_role_markers`. Both writer call sites (startup init-keyword + explicit-role-hint) now ALSO write per-session markers, independent of the legacy single-file write result, on the interactive (non-headless) path only. The legacy writer is unchanged.

3. **`scripts/session_role_resolution.py` (resolver — per-session authority).** `resolve_interactive_session_role` now reads the per-session marker keyed under `current_session_id` first (validating the stored `session_id` per assertion 6, role per assertion 7), then falls back to the legacy single-file marker for the transition window. Added the read-only `_read_per_session_marker` helper. Existing legacy resolution rows are unchanged.

4. **`scripts/bridge_work_intent_registry.py` (WI-4534 guard reader — session-id-validating).** `_interactive_marker_role(project_root, session_id)` now prefers the per-session marker keyed+validated under the querying `session_id`, then falls back to the legacy single-file marker (existing, unvalidated, SessionStart-invalidated behavior). The caller `_resolve_go_implementation_eligibility` threads `session_id` through. This is the GO's required demonstration that the guard's interactive branch finds the marker written from the same interactive context under the canonical id.

5. **`scripts/session_start_dispatch_core.py` (context-id-scoped + freshness sweep).** Added `_sweep_stale_per_session_role_markers` (+ `_per_session_marker_is_fresh`), called in `main()` immediately after the unchanged legacy `_invalidate_session_role_marker()` and before the mode-switch drain. A per-session marker is RETAINED when it belongs to `current_session_id` (resolved best-effort from `MARKER_CONTINUITY_ORDER`) OR is younger than a generous 24h freshness window (a concurrent live session); abandoned markers are reclaimed. The legacy single-file unconditional delete is preserved, and per-session markers are explicitly NOT touched by it — so the current context's marker survives a SessionStart (compaction/resume), realizing the `DELIB-20263212` invariant, while a peer SessionStart no longer clobbers a live session's marker (WI-4463).

## Specification Links

Carried forward from `-003`:

- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` — per-context keying realizes the interactive role-override contract; additive transition preserves the `-002` no-regression criterion.
- `DCL-SESSION-ROLE-RESOLUTION-001` — assertions 6 (session-id match) and 7 (valid role) enforced uniformly in both the resolver and the guard reader.
- `GOV-SESSION-ROLE-AUTHORITY-001` — unchanged; headless dispatch still keys to the durable role (the writer's per-session path is gated to the non-headless branch).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — links + project triple carried forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping below.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — the WI-4534 write-time guard is preserved; the change removes the false-negative (marker-not-found), not the enforcement.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — no `bridge/INDEX.md` write surface beyond this report's append; bridge-authority model untouched.
- `GOV-STANDING-BACKLOG-001` — `WI-4540` (P2, defect, `bridge_dispatch`); also addresses `WI-4463` and the advisory's Defect 2.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changed paths are in-root (`scripts/`, `platform_tests/`).

## Spec-to-Test Mapping

| Behavior / spec | Test | File |
|---|---|---|
| Per-context marker write keyed to the querying id (DCL-SESSION-ROLE-RESOLUTION-001 a6/a7) | `test_per_session_marker_written_on_interactive_init_keyword` | `platform_tests/hooks/test_workstream_focus_session_role_marker.py` |
| Legacy single-file marker still WRITTEN (no regression — Finding A) | `test_per_session_marker_legacy_single_file_still_written` + all retained legacy writer tests | same |
| R-B1 defensive multi-key (payload AND env candidate) | `test_per_session_marker_multikey_includes_env_candidate` | same |
| No cross-session clobber (WI-4463 root cause) | `test_per_session_marker_no_cross_session_clobber` | same |
| Explicit-role-hint path writes per-session marker | `test_per_session_marker_written_on_explicit_role_hint` | same |
| Headless dispatch writes no per-session marker | `test_per_session_marker_not_written_under_headless_dispatch` | same |
| Per-session marker is resolver authority over legacy + a6/a7 + read-only + path parity | 8 tests incl. `test_per_session_marker_is_authority_over_legacy`, `test_per_session_stored_id_mismatch_falls_back`, `test_per_session_path_matches_writer` | `platform_tests/scripts/test_session_role_resolution.py` (new) |
| WI-4534 guard's interactive branch finds a valid per-session marker under the canonical id (Finding B / R-B) | `test_go_impl_allowed_for_uuid_session_with_per_session_prime_marker` + 5 sibling guard tests | `platform_tests/scripts/test_bridge_work_intent_registry.py` (new) |
| Current context's marker SURVIVES a same-id SessionStart (DELIB-20263212) | `test_per_session_marker_retained_for_current_context` | `platform_tests/hooks/test_session_start_marker_invalidation.py` |
| Concurrent live session's marker not swept by a peer SessionStart (WI-4463) | `test_per_session_marker_concurrent_live_session_retained` | same |
| Stale marker swept; fresh retained | `test_per_session_marker_stale_swept_live_retained` | same |
| Legacy invalidation does not touch per-session markers | `test_legacy_invalidation_leaves_per_session_markers` | same |

## Verification Evidence

Focused command (GO `-004`; the two `platform_tests/scripts/` test files were created at the `target_paths` locations):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= \
  platform_tests/scripts/test_session_role_resolution.py \
  platform_tests/scripts/test_bridge_work_intent_registry.py \
  platform_tests/hooks/test_session_start_marker_invalidation.py \
  platform_tests/hooks/test_workstream_focus_session_role_marker.py -q
=> 65 passed, 1 warning in 5.07s
```

Broader session-role substrate suite (no regression):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest -o addopts= \
  platform_tests/hooks/test_session_role_resolution.py \
  platform_tests/scripts/test_work_intent_role_eligibility.py \
  platform_tests/scripts/test_work_intent_auto_extend.py \
  platform_tests/scripts/test_gtkb_session_id.py \
  platform_tests/scripts/test_session_role_resolution_table.py \
  platform_tests/scripts/test_session_role_marker_invalidation_both_harnesses.py \
  platform_tests/scripts/test_doctor_session_role_marker.py \
  platform_tests/scripts/test_kb_attribution_session_role.py -q
=> 102 passed, 1 warning in 5.77s
```

Code-quality gates (BOTH, on every changed file):

```text
ruff check <9 files>            => All checks passed!
ruff format --check <9 files>   => 9 files already formatted
```

(`test_session_start_marker_invalidation.py` required one `ruff format` pass for line-wrapping; re-checked clean.)

## Path-discrepancy note (for the verifier)

The `-003` proposal's `target_paths` / verification command named `platform_tests/scripts/test_session_role_resolution.py` and `platform_tests/scripts/test_bridge_work_intent_registry.py`. Those files did not exist on disk; the pre-existing legacy resolver test lives at `platform_tests/hooks/test_session_role_resolution.py` and there was no `test_bridge_work_intent_registry.py`. Per the proposal's `test_addition` scope, the two `platform_tests/scripts/` files were **created** (new) at the declared `target_paths`, holding the per-session-specific coverage; the pre-existing `platform_tests/hooks/` tests were left unmodified and confirmed green in the substrate suite. No out-of-scope file was modified.

## Owner Decisions / Input

Authorized by durable owner-decision evidence; no new owner AskUserQuestion is pending. As an auto-dispatched worker I cannot ask the owner interactively; none was required.

- `DELIB-20263212` — owner AUQ (2026-06-14): "Capture spec + scope fix now" then "Author now, anchor on WI-4540". Authorizes implementation under `PAUTH-PROJECT-GTKB-INTERACTIVE-SESSION-ROLE-OVERRIDE-WI-4540-PER-SESSION-MARKER` (allowed: `source` + `test_addition`; forbids formal-artifact, narrative-artifact, KB bulk status, config/hook registration, deploy/release, force pushes, credential lifecycle). All edits stayed within `source` + `test_addition`.
- The `-004` GO's R-B1 adjudication (default R-B1; R-B2 only with extra evidence) was followed exactly: R-B1 was implemented; `scripts/bridge_claim_cli.py` and `gtkb_session_id.resolve_session_id` precedence were left out of scope (no R-B2).

## Constraint Compliance (GO -004)

1. PAUTH scope (source + test only) — honored; no canonical-terminology/DCL/hook-registration/KB/release edits.
2. Additive transition (legacy written + readable; per-session is guard/resolver/sweep authority) — honored.
3. WI-4527 `maybe_auto_extend` preserved — honored (surgical edits only).
4. R-B1 path — implemented.
5. `bridge/INDEX.md` + bridge-authority untouched — honored (this report is an append-only NEW entry).

## Known Limitation / Follow-on

The SessionStart per-session sweep uses a generous `written_at`-age freshness window (24h) plus current-id retention rather than the transcript-mtime signal sketched in `-001` change 5. This honors `DELIB-20263212` for realistic contiguous contexts and never deletes a fresh or current-id marker; a transcript-mtime refinement (which would refresh per turn and harden very-long contexts whose env id changed at compaction) is a documented follow-on. The deferred `.claude/rules/canonical-terminology.md` + `DCL-SESSION-ROLE-RESOLUTION-001` "does not survive compaction or resume" clause revision (its own `narrative-artifact-approval` + `formal-artifact-approval` packets) also remains outstanding per `-003`.

## Risk / Rollback

- **Additive dual-write** — the legacy file's clobber-rejection is now latent (the guard reads per-session first), so it can no longer lock out an owner-Prime session.
- **R-B1 id choice** — implemented per the GO's default; the multi-key write guarantees the guard's `CLAUDE_CODE_SESSION_ID` lookup and the resolver's transcript-id lookup both hit a marker.
- **Rollback** — single-commit revert; no KB schema, bridge-authority, or hook-registration change.

## Recommended Commit Type

`fix:` — repairs two coupled reliability defects (cross-session marker clobber + mid-context vanish/lockout). The per-session keying + id reconciliation are structural changes in service of the fix. Diff is net-new helpers in 5 source modules + 2 new test files + additive tests in 2 existing test files (no behavior removed).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
