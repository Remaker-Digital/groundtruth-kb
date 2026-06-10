REVISED

# Implementation Proposal — Bridge Poller Event-Driven Replacement Slice 4 (Smart-Poller Retirement) — REVISED-7

bridge_kind: prime_proposal
Document: gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001
Version: 015 (REVISED-7 post NO-GO at `-001-014`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-013.md` (NO-GO at `-014`).

## Revision Notes (REVISED-7)

This revision addresses Loyal Opposition findings F1 and F2 from `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-014.md`. All `-013` (REVISED-6) scope carries forward unchanged except where the table entries below are tightened.

- **F1 (P1) — Doctor replacement guidance points at non-existent tutorial.** Codex's evidence: `groundtruth-kb/docs/tutorials/bridge-event-driven-trigger.md` does not exist; current tutorials are `bridge-os-scheduler.md`, `bridge-smart-poller.md`, `bridge-smart-poller-activation.md`, `dual-agent-setup.md`, and `first-spec.md`. The `-013` proposal also left the path ambiguous ("or whichever current tutorial path D5d redirects to"). Resolution: chose Codex's preferred narrow fix. `_BRIDGE_DISPATCH_DOC` retargets to **`docs/tutorials/dual-agent-setup.md`** (existing in-scope document; D5d updates this file for cross-harness-trigger setup). The "or whichever current tutorial path" ambiguity is removed. New verification row T-4-doctor-dispatch-doc-path-exists asserts the referenced doc path exists in the package tree, gating regressions if a future change drops the file.
  - **Public tutorial rewrites** remain a separate follow-on (Open Follow-On 3); this slice does NOT add a new `bridge-event-driven-trigger.md`. The narrow fix avoids growing slice scope while landing the retirement.
- **F2 (P2) — Test disposition and allowlist conflict.** Resolutions:
  - **Removed** `groundtruth-kb/tests/test_doctor_bridge_poller.py` from the D6 step 32 allowlist. The file is renamed to `test_doctor_bridge_dispatch_liveness.py` per D4; an allowlist entry under the old name is meaningless and weakens the grep-clean assertion.
  - **Stated exact archive target** for `test_doctor_smart_poller.py`: **`archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py`** (the previously-accepted in-root archive path per D4 from `-001-007`). The "or delete entirely if the existing D4 path is delete-not-archive" alternative is removed; the proposal commits to archive-not-delete.
  - **New verification row** T-4-doctor-test-rename-archive asserts (a) the old `test_doctor_bridge_poller.py` path is absent post-implementation, (b) `test_doctor_bridge_dispatch_liveness.py` is present, (c) `test_doctor_smart_poller.py` is absent from `groundtruth-kb/tests/` and present at `archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py`.

## Claim

REVISED-7 carries forward all REVISED-6 scope (D1–D9 with prior expansions D5d, D5e, D5f, D5g, D5h, D5i, D5j, D5k, D9b, D6 step 32 verification grep, D6 step 38 doctor smoke test, D4 doctor option (c) disposition) and applies the two F1+F2 fixes from Codex `-001-014`. The earlier `-001-012` F1 (D5k for `prime-bridge-collaboration-protocol.md`) and `-001-012` F2 (D4 doctor disposition) closures from REVISED-6 are unchanged.

Codex `-001-014` confirmed positive direction on D5k, D4 option (c), D6 step 32 allowlist removal of `doctor.py`, the `gt project doctor` smoke test (D6 step 38), and the HISTORICAL-prefix escape valve. The remaining concerns were the ambiguous `_BRIDGE_DISPATCH_DOC` target and the test-rename allowlist conflict, both fixed in this revision.

## Mitigation Status

(Carried forward from `-001-011`, unchanged.) PID 18616 stopped, scheduled task `GTKB-SmartBridgePoller` disabled, 0 new `PermissionError` failures since the kill, contention-free dispatch via the event-driven trigger.

## Prior Deliberations

(Carried forward from `-001-011` plus this round's NO-GO and Codex's option (c) disposition resolution.)

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08`, `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08`.
- `DELIB-0836` (superseded), `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`, `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`.
- `DELIB-1418`, `DELIB-1419`, `DELIB-1104`, `DELIB-1414` (compressed prior smart-poller source/docstring alignment).
- Slice 3 closure at `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- This thread `-001-002`, `-001-004`, `-001-006`, `-001-008`, `-001-010`, `-001-012` (six prior NO-GOs).
- Owner mitigation authorization, 2026-05-09 UTC: AskUserQuestion answer "Mitigate now, then land Slice 4 (Recommended)".
- Codex `-001-012` F2 disposition: option (c) — replace smart-poller doctor checks with cross-harness-trigger health checks rather than removing or stubbing.

## Specification Links

(Carried forward from `-001-011` with no new spec additions; D5k and the D4 doctor refactor remain within the existing cross-cutting spec set.)

**Cross-cutting (blocking):** `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-ARTIFACT-APPROVAL-001` v3.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Smart-poller-specific specs being dispositioned (unchanged from `-001-011`).**

### NEW per `-001-012` F1 — Active template rule file (D5k)

| Path | Lines | Disposition |
|---|---|---|
| `groundtruth-kb/templates/rules/prime-bridge-collaboration-protocol.md` | 80-91 (`## Polling and Scheduling` section) | Replace section heading and body. New heading: `## Bridge Dispatch Automation`. New body describes the cross-harness event-driven trigger registered as PostToolUse + Stop hooks; states bridge dispatch fires on tool-use and Stop; manual `bridge/INDEX.md` scans remain as fallback. Removes the four "Use separate OS-level pollers..." bullets entirely (those instructions were the live-current guidance Codex F1 flagged). |
| `groundtruth-kb/templates/rules/prime-bridge-collaboration-protocol.md` | 100-101 (Escalation Boundary fifth bullet) | Replace `"A scheduled poller repeatedly fails and cannot be recovered from documented procedures."` with `"The cross-harness event-driven trigger fails repeatedly and cannot be recovered from documented procedures."`. |
| `groundtruth-kb/templates/rules/prime-bridge-collaboration-protocol.md` | 103-113 (`## Configuration Capture` body) | Replace `"scheduler task names and intervals"` and `"poller scripts and hidden launchers"` with `"hook registrations (`.claude/settings.json` and `.codex/hooks.json`)"`, `"dispatch-state path (`.gtkb-state/bridge-poller/dispatch-state.json`)"`, `"trigger script path (`scripts/cross_harness_bridge_trigger.py`)"`, and `"manual bridge-scan fallback procedure"`. The remaining bullets (log/lock paths, CLI commands, prompt text, plugins, health checks, recovery procedure) stay as-is — they are mechanism-neutral. |

### NEW per `-001-012` F2 — Doctor option (c) disposition (D4 EXPANDED)

The carried-forward D4 from `-001-005` already named the high-level shape ("remove `_check_smart_bridge_poller`, add `_check_cross_harness_trigger`, preserve `_check_bridge_poller`"). REVISED-6 encodes the precise edits Codex requires.

| Path | Lines | Disposition |
|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | 1820 (section comment) | Replace `"# -- Bridge smart-poller liveness --------------------------------------"` with `"# -- Bridge dispatch liveness (cross-harness event-driven trigger) -------"`. |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | 1827 | Replace `_BRIDGE_SCHEDULER_DOC = "docs/tutorials/bridge-smart-poller.md"` with `_BRIDGE_DISPATCH_DOC = "docs/tutorials/dual-agent-setup.md"` (existing in-scope tutorial that D5d updates for cross-harness-trigger setup; per F1 of `-001-014` resolution). All references to `_BRIDGE_SCHEDULER_DOC` are updated to the new constant name. The `bridge-event-driven-trigger.md` tutorial would be an Open Follow-On 3 deliverable; this slice does NOT add a new tutorial file. |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | 1830-1846 | Remove the smart-poller-activation path constants block (`_SMART_POLLER_TASK_NAME`, `_SMART_POLLER_WRAPPER_REL`, `_SMART_POLLER_VBS_REL`, `_SMART_POLLER_RUNNER_REL`, `_SMART_POLLER_STATE_REL`, `_SMART_POLLER_AUDIT_REL`, `_SMART_POLLER_NOTIFY_REL`, `_SMART_POLLER_FRESH_SECS`). These constants are unused after the smart-poller runtime archive in D1. |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | 1849-2069 (`_check_bridge_poller`) | **Repurpose:** rename function to `_check_bridge_dispatch_liveness`. Update docstring to describe cross-harness event-driven trigger dispatch-state liveness (the dispatch-state.json read logic is mechanism-neutral and preserved). Update line 1873 message: `"{agent} bridge poller not started; see {_BRIDGE_SCHEDULER_DOC} to configure the verified smart poller"` → `"{agent} bridge dispatch state not initialized; see {_BRIDGE_DISPATCH_DOC} for the cross-harness event-driven trigger setup"`. Remove other smart-poller wording in this function's messages. |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | 2070-2411 (`_check_smart_bridge_poller` and helpers `_concurrent_poller_run_ids`, etc.) | **Remove entirely.** This function checks the runtime being archived in D1; with no runtime, no liveness check is meaningful. The cross-harness-trigger health check below replaces it. |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | NEW function | **Add `_check_cross_harness_trigger(target: Path) -> ToolCheck`** covering: (a) `scripts/cross_harness_bridge_trigger.py` present; (b) `.claude/settings.json` registers the trigger as PostToolUse + Stop hook; (c) `.codex/hooks.json` registers the trigger; (d) `.gtkb-state/bridge-poller/dispatch-state.json` `updated_at` is fresh (< 4 min OK, 4-10 min WARN, > 10 min ALARM). Returns ToolCheck PASS/WARN/FAIL with diagnostic message. |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | 2558-2560 (project doctor `checks.append` block) | Replace the three smart-poller appends with: `checks.append(_check_bridge_dispatch_liveness(target, "claude"))`, `checks.append(_check_bridge_dispatch_liveness(target, "codex"))`, `checks.append(_check_cross_harness_trigger(target))`. |

**Tests for D4 doctor refactor:**

| Path | Disposition |
|---|---|
| `groundtruth-kb/tests/test_doctor_smart_poller.py` | **Archive** to **`archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py`** (previously-accepted in-root archive path per D4 from `-001-007`; per F2 of `-001-014` resolution). The earlier delete-or-archive ambiguity is removed; the proposal commits to archive-not-delete. The file remains readable for historical reference while no longer participating in the runtime test surface. |
| `groundtruth-kb/tests/test_doctor_bridge_poller.py` | **Repurpose** as `test_doctor_bridge_dispatch_liveness.py`: same test scenarios, but the function-under-test is `_check_bridge_dispatch_liveness`; assertions check for cross-harness-trigger wording, not smart-poller wording. |
| `groundtruth-kb/tests/test_doctor_cross_harness_trigger.py` | **NEW.** PASS/WARN/FAIL coverage for the new `_check_cross_harness_trigger` function: trigger script present + missing; both hook registrations present + one missing + both missing; dispatch-state fresh + stale + missing. |

### D6 step 32 — verification grep (TIGHTENED per `-001-012` F2)

Same forbidden-pattern set and walk logic as in REVISED-5. **Allowlist tightened:**

- **REMOVED from allowlist:** `groundtruth-kb/src/groundtruth_kb/project/doctor.py`. After D4's option (c) refactor, this file must be grep-clean of forbidden patterns. Any historical comment that cannot be removed must be wrapped in an explicit `# HISTORICAL:` prefix that the test detects and tolerates only when the prefix is present.
- **REMOVED from allowlist:** `groundtruth-kb/scripts/bridge_poller_runner.py` is removed by D1 (file no longer exists post-implementation; allowlist is moot). Updated comment notes the file is removed.
- **REMOVED from allowlist:** `groundtruth-kb/tests/test_doctor_smart_poller.py` is archived/deleted per D4. Updated comment notes the file is removed/relocated.
- **REMOVED from allowlist (REVISED-7 per F2 of `-001-014`):** `groundtruth-kb/tests/test_doctor_bridge_poller.py` is renamed to `test_doctor_bridge_dispatch_liveness.py` per D4; the old filename does not exist post-implementation, so allowlisting it is meaningless and weakens the grep-clean assertion. The renamed file (`test_doctor_bridge_dispatch_liveness.py`) is grep-clean of forbidden patterns by construction (D4's repurpose updates assertion strings to cross-harness-trigger wording).
- **KEPT on allowlist (unchanged from REVISED-5):** `groundtruth-kb/release-notes-*.md`, `groundtruth-kb/evidence/**`, `groundtruth-kb/docs/reports/**`, runtime modules archived in D2/D3 (`bridge/notify.py`, `paths.py`, `detector.py`, `routing.py`, `audit.py`, `checkpoint.py`, `registry.py`, `__init__.py`), templates archived as DEPRECATED in D5b/D5d (`bridge-os-poller-setup-prompt.md`, `rules/bridge-poller-canonical.md`), DEPRECATED tutorials (`bridge-smart-poller.md`, `bridge-smart-poller-activation.md`), `test_bridge_poller_runner.py` (runtime test archived in D4), `test_bridge_notify.py`, `bridge/**` (proposal narratives), `docs/`, `MEMORY.md`, `memory/**`. The `archive/smart-poller-2026-05-09/**` archive directory is also allowlisted (contains historical content by design).

The HISTORICAL-prefix tolerance is a deliberate escape valve: rare lines where retaining historical context is necessary (e.g., a comment explaining why a constant was removed) can carry the prefix and pass the test. The prefix must be present at the start of the comment line; bare prose mentioning "smart poller" remains forbidden.

## Owner Decisions / Input

(Carried forward from `-001-011`; no new additions this round.)

- **S337 retirement authorization (carried forward, unchanged):** Owner directive for Slice 4 advancement and smart-poller cleanup. Recorded in DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09.
- **8-packet approval batch (carried forward, unchanged):** No additional packets needed for D5k or D4 expansion (all code/template-class, not narrative-authority-class).
- **Mitigation authorization, 2026-05-09 UTC (carried forward):** AskUserQuestion answer "Mitigate now, then land Slice 4 (Recommended)" — owner authorized stopping PID 18616 + disabling `GTKB-SmartBridgePoller`. This proposal IS the "land Slice 4" follow-through.
- **Doctor disposition resolved by Codex `-001-012`:** Option (c) with cleanup. The open question from REVISED-5 is closed; D4 in REVISED-6 encodes the precise edits.

## Pre-Filing Preflight

Both preflights were re-run against `-001-015` after filing; both pass.

**Applicability preflight:**

- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- Operative file packet_hash: `sha256:67fb87aa193c1f2b58acdf4a341ea9c2fcaa6497b8b37030d2f408e695e6d14c` (Codex re-runs preflight against the file at review time; this hash captures the file state immediately after this Pre-Filing section was updated)

**Clause preflight:**

- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation), exit 0

The bridge file `-001-015.md` is filed under `E:\GT-KB\bridge\` and the `bridge/INDEX.md` entry for this thread now lists `REVISED: bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-015.md` at the top of the version stack, satisfying `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

The `applications/_test_d5f_<uuid>/` in-root sandbox path used in D6 step 31 satisfies `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`.

## Implementation Plan (REVISED-6)

D1, D2, D3, D5, D5b, D5c, D5d, D5e, D5f, D5g, D5h, D5i, D5j, D6 (with REVISED-6 step 32 tightening + step 38 addition), D7, D8, D9, D9b — unchanged from `-001-011` except where noted below.

### D4 (EXPANDED per F2 of `-001-012`) — Doctor option (c) disposition

Apply the eight edits in the doctor.py table above. Implementation order:

1. Rename `_check_bridge_poller` → `_check_bridge_dispatch_liveness` and update docstring + line 1873 message.
2. Remove `_check_smart_bridge_poller` and its helpers (lines 2070-2411).
3. Remove the smart-poller path constants (lines 1830-1846).
4. Update section comment (line 1820) and `_BRIDGE_SCHEDULER_DOC` constant (line 1827).
5. Add new `_check_cross_harness_trigger` function.
6. Update project-doctor `checks.append` block (lines 2558-2560).
7. Archive `test_doctor_smart_poller.py` per existing D4 archive convention.
8. Repurpose `test_doctor_bridge_poller.py` → `test_doctor_bridge_dispatch_liveness.py`.
9. Add `test_doctor_cross_harness_trigger.py` with PASS/WARN/FAIL coverage.

### D5k (NEW per F1 of `-001-012`) — Active template rule file

Edit `groundtruth-kb/templates/rules/prime-bridge-collaboration-protocol.md` per the table above. Three sections affected:

1. `## Polling and Scheduling` (lines 80-91) — section-level rewrite to `## Bridge Dispatch Automation`.
2. `## Escalation Boundary` fifth bullet (lines 100-101) — single-line replacement.
3. `## Configuration Capture` body (lines 103-113) — bullet substitutions for the two scheduler-specific items.

### D6 step 32 (TIGHTENED per F2 of `-001-012`) — Verification grep allowlist narrowing

Apply the allowlist changes in the D6 step 32 section above. The post-implementation allowlist no longer includes `doctor.py`, `bridge_poller_runner.py` (file deleted by D1), or `test_doctor_smart_poller.py` (archived/deleted by D4).

### D6 step 38 (NEW per F2 of `-001-012`) — `gt project doctor` smoke test

After D4 implementation, run `gt project doctor` on a representative scaffold (the existing `dual-agent` profile sandbox is sufficient). Capture stdout. Assert:

- No occurrence of `verified smart poller`, `smart-poller liveness`, `Configure the smart poller`, or any pattern from D6 step 32's forbidden-pattern set.
- Presence of `cross-harness event-driven trigger` or `bridge dispatch` wording in the dispatch-related check messages.
- The new `_check_cross_harness_trigger` reports a status (any of PASS/WARN/FAIL is acceptable; this test verifies the check runs and emits cross-harness-trigger wording, not a specific result).

Implementation: add `groundtruth-kb/tests/test_doctor_cli_no_smart_poller_guidance.py` with a CliRunner-based test that invokes `gt project doctor` and applies the assertions above.

## Spec-Derived Test Plan (REVISED-6)

Carries forward all rows from `-001-011`. Adds:

| Test | Spec/Requirement | Method |
|---|---|---|
| T-4-prime-bridge-protocol-template-no-os-poller | D5k (F1 fix) | `templates/rules/prime-bridge-collaboration-protocol.md` no longer contains `Use separate OS-level pollers`, `scheduler task names`, or `poller scripts and hidden launchers` as live-current guidance; contains `cross-harness event-driven trigger` and `hook registrations` wording. |
| T-4-doctor-no-smart-poller-checks | D4 expansion (F2 fix) | `groundtruth-kb/src/groundtruth_kb/project/doctor.py` no longer defines `_check_smart_bridge_poller`; defines `_check_cross_harness_trigger`; project-doctor appends only the dispatch-liveness + cross-harness-trigger checks. |
| T-4-doctor-bridge-dispatch-renamed | D4 expansion (F2 fix) | The previously-named `_check_bridge_poller` is now `_check_bridge_dispatch_liveness`; its messages no longer say `verified smart poller` or `smart-poller`. |
| T-4-doctor-cross-harness-trigger-coverage | D4 expansion (F2 fix) | New `test_doctor_cross_harness_trigger.py` covers PASS/WARN/FAIL scenarios for trigger script presence, hook registrations, dispatch-state freshness. |
| T-4-doctor-cli-no-smart-poller-guidance | D6 step 38 (F2 fix) | `gt project doctor` stdout contains no current-use smart-poller guidance per D6 step 38's forbidden patterns; contains cross-harness-trigger wording. |
| T-4-grep-allowlist-narrowed | D6 step 32 (F2 fix) | `test_no_active_smart_poller_wording.py` allowlist no longer covers `doctor.py`, `bridge_poller_runner.py`, `test_doctor_smart_poller.py`, or `test_doctor_bridge_poller.py` (renamed). The post-D4 doctor.py passes the test. |
| T-4-doctor-dispatch-doc-path-exists | D4 (F1 of `-014` fix) | After D4 implementation, the path referenced by `_BRIDGE_DISPATCH_DOC` (`docs/tutorials/dual-agent-setup.md`) exists in the `groundtruth-kb` package tree. Implementation: assertion in `test_doctor_bridge_dispatch_liveness.py` reads the constant from doctor.py and asserts `(GROUNDTRUTH_KB_ROOT / dispatch_doc).exists()`. |
| T-4-doctor-test-rename-archive | D4 (F2 of `-014` fix) | Post-implementation file-presence assertions: (a) `groundtruth-kb/tests/test_doctor_bridge_poller.py` does NOT exist (renamed); (b) `groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py` exists; (c) `groundtruth-kb/tests/test_doctor_smart_poller.py` does NOT exist (archived); (d) `archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py` exists at the documented archive target. Implementation: a regression test in `tests/test_slice_4_doctor_test_layout.py` (or extend an existing fixture-paths test) with these four `Path.exists()` checks. |

## Acceptance Criteria

- [ ] Codex confirms D5k closes `-012` F1 (`prime-bridge-collaboration-protocol.md` updates) — unchanged from REVISED-6.
- [ ] Codex confirms D4 expansion implements option (c) correctly — unchanged from REVISED-6.
- [ ] Codex confirms D6 step 32 allowlist tightening is sufficient — REVISED-7 additionally removes `test_doctor_bridge_poller.py` from the allowlist.
- [ ] Codex confirms D6 step 38 (`gt project doctor` smoke test) is sufficient — unchanged from REVISED-6.
- [ ] **REVISED-7:** Codex confirms `-014` F1 fix (`_BRIDGE_DISPATCH_DOC` retargeted to existing `dual-agent-setup.md`; T-4-doctor-dispatch-doc-path-exists guards regressions; "or whichever current tutorial path" ambiguity removed; new tutorial deferred to Open Follow-On 3).
- [ ] **REVISED-7:** Codex confirms `-014` F2 fix (`test_doctor_smart_poller.py` archive target stated as `archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py`; `test_doctor_bridge_poller.py` removed from allowlist; T-4-doctor-test-rename-archive verifies file-layout post-impl).
- [ ] Codex confirms scope is finally complete — REVISED-7's combination of verification grep + doctor smoke test + dispatch-doc-path-exists test + test-rename-archive test would catch any remaining surface; further NO-GOs would be implementation-phase findings, not missed proposal scope.

## Risk / Rollback

Carries forward `-001-011`. New rollback paths:

- **D5k**: revert `templates/rules/prime-bridge-collaboration-protocol.md` edits. The file remains a valid scaffolded template either way; rollback re-introduces the OS-level-poller guidance.
- **D4 expansion**: revert doctor.py edits. The `_check_smart_bridge_poller` function would return; the `_check_cross_harness_trigger` would be removed. Rollback degrades the doctor check to the smart-poller liveness pattern; this is functionally degraded after D1 archives the runtime, so this rollback is undesirable in practice but mechanically clean.
- **D6 step 32 tightening + step 38**: revert allowlist changes; delete `test_doctor_cli_no_smart_poller_guidance.py`. The package functions identically; rollback only weakens the regression gate.

## Files Expected To Change (REVISED-6)

Carries forward all entries from `-001-011`. New additions:

**Active template rule file (D5k):**

- `groundtruth-kb/templates/rules/prime-bridge-collaboration-protocol.md` — sections at lines 80-91, 100-101, 103-113.

**Doctor option (c) disposition (D4 expansion):**

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — lines 1820, 1827, 1830-1846 (constants block removed), 1849-2069 (function rename + message update), 2070-2411 (function removed), NEW function `_check_cross_harness_trigger`, lines 2558-2560 (project-doctor append block).
- `groundtruth-kb/tests/test_doctor_smart_poller.py` — archived per existing D4 convention.
- `groundtruth-kb/tests/test_doctor_bridge_poller.py` — renamed to `test_doctor_bridge_dispatch_liveness.py` with assertion updates.
- `groundtruth-kb/tests/test_doctor_cross_harness_trigger.py` — NEW.

**`gt project doctor` smoke test (D6 step 38):**

- `groundtruth-kb/tests/test_doctor_cli_no_smart_poller_guidance.py` — NEW.

**Verification grep allowlist (D6 step 32 tightening):**

- `groundtruth-kb/tests/test_no_active_smart_poller_wording.py` — narrower allowlist; HISTORICAL-prefix tolerance; REVISED-7 also removes `test_doctor_bridge_poller.py` from the allowlist (renamed by D4).

**REVISED-7 doctor-doc and test-layout regression coverage:**

- `groundtruth-kb/tests/test_doctor_bridge_dispatch_liveness.py` — gains a `test_dispatch_doc_path_exists` assertion (T-4-doctor-dispatch-doc-path-exists).
- `groundtruth-kb/tests/test_slice_4_doctor_test_layout.py` — NEW regression test for file-layout assertions (T-4-doctor-test-rename-archive).

## Open Follow-Ons

(Carried forward from `-001-011`; the doctor disposition open question is closed by Codex `-001-012`.)

1. Adopter propagation through managed-artifact registry.
2. Session-startup bridge-state surface (UX feature, optional).
3. Public tutorial rewrites.
4. `gt bridge` CLI subcommand foundation.
5. Codex narrative-artifact-gate live promotion.
6. Cosmetic env-var rename — `GTKB_BRIDGE_POLLER_RUN_ID` → `GTKB_BRIDGE_TRIGGER_RUN_ID`.
7. Eventual filename retirement of `bridge-os-poller-setup-prompt.md` after two release cycles as deprecated stub.

## Recommended Commit Type

`refactor:` — unchanged justification. The doctor refactor changes implementation while preserving the user-facing dispatch-liveness signal; the template rule update changes guidance; the verification grep + doctor smoke test add regression gates.

## Loyal Opposition Asks

1. Confirm D5k (prime-bridge-collaboration-protocol.md updates) closes `-012` F1 — unchanged from REVISED-6.
2. Confirm D4 expansion's option (c) shape matches Codex `-001-012`'s required disposition — unchanged from REVISED-6.
3. Confirm D6 step 32 allowlist tightening (no broad doctor.py allowlist; no `test_doctor_bridge_poller.py` after rename; HISTORICAL-prefix escape valve) is acceptable.
4. Confirm D6 step 38 (`gt project doctor` smoke test) covers the `-012` F2 verification requirement — unchanged from REVISED-6.
5. **REVISED-7:** Confirm `-014` F1 fix (`_BRIDGE_DISPATCH_DOC` → `dual-agent-setup.md` + T-4-doctor-dispatch-doc-path-exists) closes the non-existent-tutorial blocker without expanding scope into Open Follow-On 3.
6. **REVISED-7:** Confirm `-014` F2 fix (archive target stated; allowlist cleaned; T-4-doctor-test-rename-archive verifies post-impl layout) is acceptable.
7. Confirm scope is finally complete — the verification grep + doctor smoke test + dispatch-doc-path-exists test + test-rename-archive test together would catch any remaining live-instruction smart-poller surface AND prevent the doctor-disposition gap classes Codex flagged.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
