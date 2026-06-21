NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - PB startup-disclosure cache fails freshness contract validation

bridge_kind: prime_proposal
Document: gtkb-pb-startup-disclosure-cache-freshness-contract
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3447

target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The init-keyword startup-disclosure relay gate in `scripts/workstream_focus.py` (`_startup_relay_pointer` / `_startup_gate_response`) self-heals ONLY the freshness-stale case. When the harness-scoped relay cache (`.claude/hooks/last-user-visible-startup-pb.md`) and its metadata sidecar (`...-pb.meta.json`) disagree on `sha256`/`byte_length` (a *re-derivable content drift*, e.g. a parallel session re-rendered the disclosure body without an in-sync sidecar write), `consistent_except_freshness` is `False`, so the existing self-heal branch is skipped and the gate emits the hard `STARTUP RELAY FAILURE` for `::init gtkb pb`, refusing to mark startup satisfied — even though the active harness can deterministically re-render its own role disclosure. The cache content is regenerable by the same render path the freshness self-heal already uses; a sha256/byte-length drift between cache and sidecar (with harness id and role still matching the active harness) should be recovered by regenerating cache+sidecar atomically rather than hard-failing.

## Defect / Reproduction

Observed incident (origin of WI-3447, 2026-05-29): the SessionStart hook reported `startup service freshness contract validation failed` and the UserPromptSubmit init-keyword relay reported `cache file .claude/hooks/last-user-visible-startup-pb.md does not match its metadata sidecar (sha256, byte-length, harness id, role, freshness, or startup-disclosure shape mismatch)`. Multiple startup sources were modified in the working tree by a parallel session (`.claude/hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/session_start_dispatch.py`, `.codex/gtkb-hooks/last-user-visible-startup.md`, `.codex/gtkb-hooks/last-user-visible-startup.meta.json`), the probable proximate cause: a concurrent re-render displaced the cache body without writing a matching sidecar. The owner AUQ-selected proceed-minimal (skip the canonical disclosure for the session) and deferred root-cause; this WI is that capture.

Reproduction (logical, against `scripts/workstream_focus.py::_startup_relay_pointer`): write a relay cache body whose shape passes (`# GroundTruth-KB Fresh Session Startup` + `## Startup Disclosure`) for the active harness id/role `pb`, but write a sidecar whose `sha256` (and/or `byte_length`) does not match the body bytes. With no `GTKB_BRIDGE_POLLER_RUN_ID` (interactive), the pointer computes `consistent_except_freshness = False` (because `meta["sha256"] != actual_sha`); the self-heal branch at the current line ~1547 is gated on `consistent_except_freshness`, so it does NOT fire; `consistent` is `False`; `_startup_gate_response` returns the `STARTUP RELAY FAILURE` diagnostic and the gate refuses to mark startup satisfied. This is exactly the behavior the existing `test_startup_gate_no_self_heal_on_non_freshness_inconsistency` asserts — but that test conflates two sub-cases: (a) genuine non-recoverable inconsistency (wrong harness / wrong role / shape failure) which SHOULD hard-fail, and (b) a re-derivable content drift (sha256/byte-length mismatch while harness id and role still match the active harness) which SHOULD self-heal. Expected after fix: case (b) regenerates the cache + sidecar from the harness's own deterministic render and proceeds; case (a) still hard-fails.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/workstream_focus.py`, `platform_tests/hooks/test_workstream_focus.py`.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001` - governing authority for the fresh-session self-initialization disclosure experience; the relay gate must deliver the canonical `::init gtkb pb` disclosure, and a re-derivable cache/sidecar drift currently blocks that disclosure when it could be deterministically regenerated.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the relay gate is part of the startup/bridge-adjacent disclosure surface; the fix keeps the gate's fail-closed posture (hard-fail on genuine inconsistency) while restoring delivery on recoverable drift, preserving the authoritative-signal discipline.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the relay cache + sidecar are durable lifecycle artifacts; the fix keeps them consistent (atomic regenerate of both) rather than leaving a stranded mismatched pair.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing spec (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives each regression test from a cited spec clause (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `SPEC-AUQ-POLICY-ENGINE-001` - the relay-failure path produces an owner-facing diagnostic that asks how to proceed; reducing spurious hard-fails lowers needless owner-decision interruptions, keeping owner-input surfaces reserved for genuine blockers.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform hook script (`scripts/workstream_focus.py`) and its platform test; no adopter/application surface or application-placement boundary is touched.
- `GOV-STANDING-BACKLOG-001` - WI-3447 is a standing-backlog work item (P2, origin=defect) under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the relay cache is harness-scoped (`.claude/hooks/...-pb.md` for Claude, `.codex/gtkb-hooks/...` for Codex) and the shared self-heal renders via `session_start_dispatch_core`; the fix lives in the shared consumer path so Claude- and Codex-harness behavior stays at parity.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the regenerated disclosure remains artifact-backed (deterministic render → cache + sidecar), not inferred or hand-patched.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - aligns the self-heal regeneration trigger with the cache-drift lifecycle state that should drive it (recoverable drift → regenerate; non-recoverable mismatch → hard-fail).

## Prior Deliberations

- `DELIB-20264941` - Loyal Opposition Verification, Startup Relay Truncation Fix Refile - directly governs the relay-cache disclosure surface this fix touches; confirms the cache must deliver the full disclosure body, which the recoverable-drift hard-fail currently prevents.
- `DELIB-2333` - Loyal Opposition Review, Startup Enhancements P2 Freshness Contract - the freshness-contract review whose self-heal direction this fix extends from "freshness-stale only" to "freshness-stale + re-derivable content drift."
- `DELIB-20261470` - Loyal Opposition Verdict, Interactive Session Role Override Slice 5 Focus-Menu Role-Awareness - role-scoped (`pb`/`lo`) startup surface context; the relay cache is role-scoped and the fix must preserve the role match guard (only same-role drift self-heals).
- `DELIB-2623` - Loyal Opposition Verdict, Interactive Session Role Override Slice 5 Focus-Menu Role-Awareness - sibling role-awareness verdict for the same role-scoped startup surface; same preservation constraint on the role guard.
- `DELIB-1081` - Startup First-Response Directive Repair - prior repair of the first-response startup behavior; establishes that the gate's job is to deliver the disclosure, not to spuriously block it, which the recoverable-drift case violates.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-3447 is origin=defect, single-concern, introduces no new public surface and no new/revised spec, and is bounded to ~1 source file + 1 test (well under the fast-lane size guide), so it is covered by the reliability fast-lane standing authorization through active project membership in PROJECT-GTKB-RELIABILITY-FIXES.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (P1/P2 first); WI-3447 is P2 and in scope for this batch.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-SESSION-SELF-INITIALIZATION-001` already requires the fresh-session disclosure to be delivered, and the freshness self-heal mechanism (per `DELIB-2333`) already establishes that a recoverable cache state should be regenerated rather than hard-failed. This fix extends that established self-heal contract to the re-derivable content-drift sub-case; it does not introduce or revise any requirement/specification, and it preserves the fail-closed posture for genuinely non-recoverable inconsistencies.

## Proposed Scope

1. In `scripts/workstream_focus.py::_startup_relay_pointer`, broaden the self-heal trigger so it also fires on a **re-derivable content drift**: cache body bytes do not match the sidecar `sha256`/`byte_length`, BUT `harness_ok`, `harness_id_ok`, and `role_ok` are all true and the body still satisfies the startup-disclosure shape check (`disclosure_ok`). In that sub-case, regenerate the cache + sidecar atomically via the existing `session_start_dispatch_core._render_role_startup_report` / `_write_startup_relay_cache` path already used for the freshness-stale self-heal, then recompute `actual_sha`/`byte_length`/`freshness_ok`/`consistent` from the regenerated files.
   - Reuse the existing self-heal preconditions verbatim: skip when `headless_dispatch` (i.e. `GTKB_BRIDGE_POLLER_RUN_ID` is set) is true, and keep the whole block `try/except`-guarded and fail-soft (a regeneration failure falls through to the existing hard-fail diagnostic).
   - Do NOT self-heal genuine non-recoverable inconsistencies: wrong `harness_name`/`harness_id` (`harness_ok`/`harness_id_ok` false), wrong `role_mode` (`role_ok` false), or shape failure (`disclosure_ok` false) MUST still produce `consistent = False` and the existing `STARTUP RELAY FAILURE` diagnostic. The regeneration path must not be entered for those.
   - No new bridge-reading or render surface is introduced; the fix reuses the already-imported `session_start_dispatch_core` render path and the existing predicate fields.
2. Update the conflated regression test and add new regressions in `platform_tests/hooks/test_workstream_focus.py` (see verification plan). `test_startup_gate_no_self_heal_on_non_freshness_inconsistency` currently uses a sha256-only mismatch (a recoverable drift) to assert NO self-heal; that case is exactly what should now self-heal, so the test is re-scoped to assert non-self-heal on a genuinely non-recoverable inconsistency (wrong harness id and/or shape failure), and new tests cover the recoverable-drift self-heal plus the preserved hard-fail and headless-skip behaviors.

This is the defect-removal path. Modeling/displaying that automatic completion can proceed with a known-mismatched cache (i.e. relaxing the consistency contract itself) is a behavior/contract change requiring a new requirement and is explicitly out of scope for this fast-lane defect fix.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-SESSION-SELF-INITIALIZATION-001` (deliver the fresh-session disclosure) | `test_startup_gate_self_heals_rederivable_content_drift` | A `pb` cache whose body bytes do not match the sidecar `sha256`/`byte_length`, but whose harness id + role + shape match the active harness, is regenerated (cache + sidecar rewritten from the render path) and the response does NOT contain `STARTUP RELAY FAILURE`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (fail-closed on genuine inconsistency) | `test_startup_gate_no_self_heal_on_non_recoverable_inconsistency` (re-scoped from `test_startup_gate_no_self_heal_on_non_freshness_inconsistency`) | A cache with wrong harness id and/or a shape failure (`disclosure_ok` false) does NOT trigger regeneration and DOES emit `STARTUP RELAY FAILURE`. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (no self-heal under headless dispatch) | `test_startup_gate_no_self_heal_on_headless_dispatch` (retained) | With `GTKB_BRIDGE_POLLER_RUN_ID` set, a drifted cache is NOT regenerated and `STARTUP RELAY FAILURE` is emitted (regression-guard that the new branch honors the headless skip). |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (no over-trigger on healthy state) | `test_startup_gate_no_self_heal_on_fresh_consistent_cache` (retained) | A fresh, fully-consistent cache is NOT regenerated (the render path is not called). |

Execution commands:
- `python -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short`
- `python -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py`
- `python -m ruff format --check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py`

## Acceptance Criteria

1. `_startup_relay_pointer` regenerates the cache + sidecar (via the existing render path) and yields `consistent = True` when the only inconsistency is a re-derivable content drift (sha256/byte-length mismatch) and the active harness id + role + disclosure shape match.
2. A genuinely non-recoverable inconsistency (wrong harness id, wrong role, or shape failure) still yields `consistent = False` and the `STARTUP RELAY FAILURE` diagnostic (no regression in fail-closed posture).
3. The headless-dispatch skip and the fresh-consistent no-op are preserved (render path not called in those cases).
4. The new and re-scoped tests pass; `ruff check` and `ruff format --check` are clean on the two changed files.

## Risks / Rollback

- Risk: broadening the self-heal could mask a genuine cross-harness/wrong-role displacement. Mitigation: regeneration fires only when `harness_ok` AND `harness_id_ok` AND `role_ok` AND `disclosure_ok` are all true; wrong-harness/wrong-role/shape failures keep hard-failing.
- Risk: regenerating during a headless dispatch could populate an interactive cache from a non-interactive context. Mitigation: the existing `headless_dispatch` guard is reused verbatim, so the new branch is skipped when `GTKB_BRIDGE_POLLER_RUN_ID` is set.
- Risk: a render failure mid-regeneration could leave a partially-written pair. Mitigation: the block stays `try/except`-guarded and fail-soft; on any error it falls through to the existing hard-fail diagnostic rather than asserting a healed state, and `_write_startup_relay_cache` writes body then sidecar so a recompute after write detects any residual mismatch.
- Rollback: revert the predicate broadening in `_startup_relay_pointer` and restore the prior `test_startup_gate_no_self_heal_on_non_freshness_inconsistency` assertion; the change is a single guarded condition plus tests, fully reversible with no migration.

## Files Expected To Change

- `scripts/workstream_focus.py`
- `platform_tests/hooks/test_workstream_focus.py`

## Recommended Commit Type

`fix`
