NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Codex-side SessionStart and UserPromptSubmit hooks report Failed during bridge dispatch

bridge_kind: prime_proposal
Document: gtkb-codex-sessionstart-userpromptsubmit-hook-failures
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4462

target_paths: [".codex/hooks.json", "platform_tests/scripts/test_codex_hook_parity.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The Codex-side `SessionStart` hook entry that runs `.codex/gtkb-hooks/session_start_dispatch.py` is registered in `.codex/hooks.json` with `"timeout": 60`, but that hook internally runs the canonical startup service (`scripts/session_self_initialization.py`) via `subprocess.run(..., timeout=_startup_service_timeout_seconds())`, whose default is `STARTUP_SERVICE_TIMEOUT_SECONDS = 150.0` (`scripts/session_start_dispatch_core.py:53`). The outer hook budget (60s) is therefore SHORTER than the inner subprocess budget (150s): when a cold startup-service render takes 60-150s (typical during a freshly-spawned bridge-dispatch session), Codex's hook runner kills the hook process at 60s and prints `hook: SessionStart Failed` BEFORE the hook's own fail-soft fallback (`_fallback_context`) can run. The same timeout-inversion class affects the `UserPromptSubmit` entry running `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` (registered `"timeout": 15`), which itself shells out to `scripts/session_self_initialization.py` (no inner timeout cap) on a wrap-up trigger and can exceed 15s on a cold interpreter, producing `hook: UserPromptSubmit Failed`. The defect is a hook-registration timeout-budget configuration error in `.codex/hooks.json`, not a logic bug in the hook scripts (which are all written to exit 0 / fail-soft).

## Defect / Reproduction

Observed incident (origin of WI-4462): 2026-06-11T14:15Z Codex dispatch stderr showed `hook: SessionStart Failed` (x2) and multiple `hook: UserPromptSubmit Failed`. Codex proceeded, but the failures indicate Codex-side hook breakage.

Evidence chain (read-only investigation):
- `.codex/hooks.json` SessionStart chain has three hooks: `active_session_heartbeat.py` (`timeout: 5`, fail-soft, always exits 0 - verified by running it: `EXIT=0`), `session_start_dispatch.py` (`timeout: 60`), and `single_harness_bridge_automation.py --ensure` (`timeout: 10`). The "SessionStart Failed x2" count is consistent with two of these three SessionStart hooks being killed/failing under load.
- `scripts/session_start_dispatch_core.py` (the shared core the Codex wrapper delegates to) wraps the startup-service subprocess with `timeout=_startup_service_timeout_seconds()` defaulting to `STARTUP_SERVICE_TIMEOUT_SECONDS = 150.0`. `main()` is explicitly fail-soft (returns 0 on every path, including timeout via the broad `except Exception`). Therefore the hook cannot self-fail with a non-zero exit; the only way Codex reports it "Failed" is an EXTERNAL kill - i.e., the outer 60s registered budget expiring before the inner 150s subprocess returns.
- Corroboration: `.codex/gtkb-hooks/last-session-start.err` is 0 bytes. A genuine internal exception path would write the exception text to `stderr_path` before returning; an external timeout-kill terminates the process before `_fallback_context`/`stderr_path.write_text(...)` runs, leaving the diagnostic file empty - exactly what is observed.
- The `UserPromptSubmit` wrap-up trigger (`session_wrapup_trigger_dispatch.py`, `timeout: 15`) runs `subprocess.run([... session_self_initialization.py ... --emit-wrapup --force-wrapup --fast-hook ...])` with NO inner timeout, so a cold-interpreter run that exceeds 15s is killed by Codex and reported `UserPromptSubmit Failed`.

Reproduction (logical, deterministic): set the inner startup-service timeout above the outer registered budget and force a slow render. Concretely, the regression can be made deterministic without timing flakiness by asserting the registered-budget invariant directly: a config assertion that every SessionStart hook entry invoking `session_start_dispatch.py` carries a registered `timeout` strictly greater than the inner `STARTUP_SERVICE_TIMEOUT_SECONDS` constant. Today that invariant is violated (60 < 150). Expected: the outer hook budget must exceed the inner subprocess budget (plus headroom) so the hook's fail-soft path always completes and Codex never reports `SessionStart Failed` for a merely-slow (not crashed) startup.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.codex/hooks.json`, `platform_tests/scripts/test_codex_hook_parity.py`. Both paths were confirmed to exist at proposal time. No path outside `E:\GT-KB` is read as a live dependency, written, or required.

## Bridge Audit-Trail Compliance

This proposal is filed as a numbered, append-only versioned bridge file (`bridge/gtkb-codex-sessionstart-userpromptsubmit-hook-failures-001.md`) per `GOV-FILE-BRIDGE-AUTHORITY-001`: the numbered bridge-file chain is canonical, the first non-blank line carries the `NEW` status token, and no prior bridge version is deleted or rewritten. Any subsequent REVISED/report/verdict versions will be appended as the next numbered files (`-002.md`, `-003.md`, ...) without mutating earlier versions, preserving the bridge protocol audit trail.

## Specification Links

- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` - the most directly governing spec: Codex governance hook wiring must stay aligned with active Claude governance gates and function correctly; a SessionStart/UserPromptSubmit hook that is killed (reported "Failed") before its fail-soft path runs is a parity/health defect in the Codex governance wiring this spec governs.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - establishes `.codex/hooks.json` as the live Codex interception boundary on Windows (CLI >= 0.128.0-alpha.1, `codex_hooks` stable); the fix corrects a registration in that exact artifact so the hooks fire reliably instead of timing out.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the failing hooks fire during bridge dispatch (cross-harness trigger) and during interactive sessions that drive the bridge; reliable SessionStart/UserPromptSubmit execution is part of keeping the bridge dispatch substrate healthy, which this authority governs.
- `GOV-RELIABILITY-FAST-LANE-001` - this WI is origin=defect, single-concern, and introduces no new public surface; it qualifies for the reliability fast-lane this GOV defines (see Owner Decisions / Input).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant governing specs (mandatory linkage); the linkage is non-placeholder.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives tests from the cited specs and executes them (mandatory for VERIFIED).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries the Project Authorization / Project / Work Item linkage lines (mandatory bridge-proposal metadata).
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix preserves the durable hook-configuration artifact (`.codex/hooks.json`) and its regression test as the source of truth for Codex hook behavior, rather than leaving the failure as undocumented operational noise.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the corrected timeout invariant is captured as an artifact-backed regression assertion in the parity test, not as tribal knowledge.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching the Codex hook-config surface triggers updating its governing regression test (the parity test) in the same change, per the lifecycle-trigger discipline.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to GT-KB platform harness configuration (`.codex/hooks.json`) and platform tests; no adopter/application surface under `applications/` is touched and no placement boundary is crossed.
- `SPEC-AUQ-POLICY-ENGINE-001` - narrowly relevant: the parity test file references AUQ-related governance wiring (owner-decision tracker parity surfaces); this fix does not alter AUQ policy behavior, but the link is retained because the edited test module sits adjacent to AUQ parity assertions and the change must not regress them.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` and `ADR-CODEX-HOOK-PARITY-FALLBACK-001` already require Codex governance hooks to be wired correctly and to function as a live interception boundary; a hook that is externally killed before completing is a defect against that existing contract. The fix is a configuration correction (outer hook timeout must exceed the inner subprocess timeout) plus a regression assertion of that invariant. No new or revised requirement/specification is introduced.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (standing authorization via `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-4462 is origin=defect, single-concern, bounded to one harness-config file + one test file, introduces no new public API/CLI/behavior beyond removing the defect, and requires no new/revised spec; it is covered by the reliability fast-lane standing authorization through active project membership in PROJECT-GTKB-RELIABILITY-FIXES.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing authoring of NEW proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work-item batch; WI-4462 is in scope (a P3 harness-parity defect in that batch).
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the standing owner direction establishing the reliability fast-lane (`GOV-RELIABILITY-FAST-LANE-001`) under which small defect fixes proceed through the normal propose -> GO -> implement -> report -> VERIFIED cycle without a separate per-item owner approval.

No fresh owner decision is required for this proposal: it is a bounded defect fix authorized by the standing PAUTH and the batch AUQ above.

## Prior Deliberations

- `DELIB-1642` - Loyal Opposition Review, Claude SessionStart Hook Parity - directly relevant prior review of SessionStart hook parity; establishes the parity-review baseline this Codex-side timeout fix extends.
- `DELIB-1641` - Loyal Opposition Verification, Claude SessionStart Hook Parity REVISED-1 - verification context for the SessionStart parity contract being corrected here.
- `DELIB-1643` - Loyal Opposition Verification, Claude SessionStart Hook Parity - additional verification context confirming the SessionStart dispatcher contract that both harnesses share.
- `DELIB-1079` - SessionStart Acceptance Check - acceptance-criteria precedent for SessionStart hook behavior.
- `DELIB-20264231` - Loyal Opposition Review, Interactive Session Role Override Slice 1 - touches the shared SessionStart dispatch core (`session_start_dispatch_core.py`) this defect implicates; confirms the fail-soft / shared-core design the timeout fix must preserve.

No prior deliberation specifically addresses the SessionStart/UserPromptSubmit hook-timeout-budget inversion; this proposal is the first to do so.

## Proposed Scope

Defect-removal path (minimal, single-concern):

1. In `.codex/hooks.json`, raise the registered `timeout` on the SessionStart hook entry that invokes `.codex/gtkb-hooks/session_start_dispatch.py` from `60` to a value strictly greater than the inner `STARTUP_SERVICE_TIMEOUT_SECONDS` (150s) plus headroom - recommend `180`. This guarantees the inner startup-service subprocess (and the hook's fail-soft fallback) completes before Codex's hook runner kills the process, eliminating the `SessionStart Failed` report for merely-slow startups.
2. In `.codex/hooks.json`, raise the registered `timeout` on the `UserPromptSubmit` hook entry that invokes `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` from `15` to a value with headroom over a cold `session_self_initialization.py --emit-wrapup` render (recommend `60`), since that hook shells out to the startup service with no inner cap. The lightweight UserPromptSubmit hooks (`workstream-focus.cmd`, `spec-classifier.py`, `glossary-expansion.py`, `project-completion-surface.py`) are left unchanged: they are fast, fail-soft, and not observed to exceed their 5s budgets; widening them is out of scope to keep the change single-concern.
3. Add regression assertions in `platform_tests/scripts/test_codex_hook_parity.py` (see verification plan) that mechanically enforce the corrected invariant: the SessionStart `session_start_dispatch.py` entry's registered `timeout` must be strictly greater than `STARTUP_SERVICE_TIMEOUT_SECONDS` parsed from `scripts/session_start_dispatch_core.py`, and the UserPromptSubmit `session_wrapup_trigger_dispatch.py` entry's `timeout` must be >= 60. The existing assertion at line 63 (`hook.get("timeout", 0) >= 60`) is updated/replaced so it no longer admits the buggy 60-vs-150 inversion.

Out of scope (would require a new requirement / behavior change, explicitly excluded from this fast-lane defect fix):
- Reducing `STARTUP_SERVICE_TIMEOUT_SECONDS` or restructuring the startup service for speed (a performance change, not a defect removal).
- Re-architecting the heartbeat/single-harness-automation SessionStart hooks.
- Any change to the Claude-side `.claude/settings.json` (the WI is scoped to Codex-side reports; the symmetric Claude-side timeout observation is noted for a possible sibling WI but not changed here).

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` (Codex governance hooks must function, not be killed before completing) | `test_codex_sessionstart_hook_timeout_exceeds_inner_startup_service_timeout` | The `.codex/hooks.json` SessionStart hook entry invoking `session_start_dispatch.py` has a registered `timeout` strictly greater than `STARTUP_SERVICE_TIMEOUT_SECONDS` (parsed from `scripts/session_start_dispatch_core.py`). |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (the `.codex/hooks.json` boundary must fire reliably) | `test_codex_userpromptsubmit_wrapup_hook_has_headroom_timeout` | The `.codex/hooks.json` UserPromptSubmit hook entry invoking `session_wrapup_trigger_dispatch.py` has a registered `timeout` >= 60 (headroom over a cold `session_self_initialization.py --emit-wrapup` render). |
| `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001` (no regression of existing parity wiring) | `test_codex_hook_parity_passes_for_repository_configuration` (existing) | `check_codex_hook_parity.main([...])` still returns 0 and prints `Codex hook parity: PASS` after the timeout edits. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_codex_hook_parity.py -q --tb=short`
- `python -m ruff check .codex/hooks.json platform_tests/scripts/test_codex_hook_parity.py`
- `python -m ruff format --check .codex/hooks.json platform_tests/scripts/test_codex_hook_parity.py`

(Note: `.codex/hooks.json` is JSON, not Python; `ruff` will no-op on it. The ruff gates are run on the changed Python test file; the JSON file is validated by the parity test loading it via `json.loads`.)

## Acceptance Criteria

1. The `.codex/hooks.json` SessionStart `session_start_dispatch.py` entry's registered `timeout` is strictly greater than the inner `STARTUP_SERVICE_TIMEOUT_SECONDS` (150s) - recommended value `180`.
2. The `.codex/hooks.json` UserPromptSubmit `session_wrapup_trigger_dispatch.py` entry's registered `timeout` is >= 60.
3. New regression tests assert both invariants and fail on the pre-fix configuration (60 < 150; 15 < 60).
4. The existing `test_codex_hook_parity_*` suite continues to pass (`Codex hook parity: PASS`); `ruff check` and `ruff format --check` are clean on the changed Python test file.

## Risks / Rollback

- Risk: a longer SessionStart hook budget (180s) means a genuinely-hung startup service is allowed to run longer before Codex kills it. Mitigation: the inner `subprocess.run(..., timeout=150)` already bounds the real work; the outer 180s only adds the headroom needed for the inner fail-soft path to print and return. Net worst-case startup latency is governed by the inner 150s cap, unchanged.
- Risk: widening the UserPromptSubmit wrap-up budget to 60s could delay an interactive turn if wrap-up generation hangs. Mitigation: the wrap-up hook fires only on explicit wrap-up/new-session trigger phrases (`_is_wrapup_trigger`); ordinary prompts short-circuit via `_emit_no_context()` well under 1s, so the wider budget is only reachable on an intentional wrap-up.
- Risk: hard-coding `180` could drift if `STARTUP_SERVICE_TIMEOUT_SECONDS` is later raised above 180. Mitigation: the regression test derives the inner timeout from the source constant and asserts `outer > inner`, so any future inner-timeout increase that re-creates the inversion fails the test immediately.
- Rollback: revert the two `timeout` values in `.codex/hooks.json` and the added test assertions. The change is config + test only, fully reversible, with no migration and no runtime state.

## Files Expected To Change

- `.codex/hooks.json`
- `platform_tests/scripts/test_codex_hook_parity.py`

## Recommended Commit Type

`fix`
