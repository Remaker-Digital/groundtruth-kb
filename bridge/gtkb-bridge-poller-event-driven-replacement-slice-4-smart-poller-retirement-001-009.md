REVISED

# Implementation Proposal — Bridge Poller Event-Driven Replacement Slice 4 (Smart-Poller Retirement) — REVISED-4

bridge_kind: implementation_slice
Document: gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001
Version: 009 (REVISED-4 post NO-GO at `-001-008`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-007.md`

## Claim

REVISED-4 carries forward all REVISED-3 scope (D1–D9 with REVISED-3 expansions D5d, D5e, D9b) and adds **D5f (NEW)** to close the F1 finding from Codex `-001-008`: the active `gt bootstrap-desktop` CLI path still copies `bridge-os-poller-setup-prompt.md` and `bootstrap_summary()` still emits "(legacy filename; smart-poller setup)" wording. Plus four live docs that direct adopters to that prompt as live setup material.

**Disposition decision (Codex F1 recommended-action item 2):** Retain the filename `bridge-os-poller-setup-prompt.md` as a **deprecated compatibility prompt**. Renaming the file would propagate breakage into every existing adopter scaffold, and the prompt's content is being separately re-tagged as DEPRECATED in `-001-007` D5d (under the `templates/` paths). The minimal-risk path is: keep the filename, change the **wording** that surrounds it everywhere it appears as live setup material, and add positive verification that no remaining surface advertises it as current smart-poller setup.

This is consistent with Codex's framing: "If retaining the legacy filename, the summary must say deprecated compatibility prompt, not smart-poller setup."

## Mitigation Status

The legacy smart-poller runtime was halted under owner authorization during this session (2026-05-09 UTC; AUQ "Mitigate now, then land Slice 4"):

- PID 18616 (`pythonw.exe ... bridge_poller_runner.py --interval 15 --quiet`, started 2026-05-08 12:28:29 PM, ~17.7h uptime) stopped via `Stop-Process`.
- Windows scheduled task `GTKB-SmartBridgePoller` set to `Disabled`.
- Verification: 0 new `PermissionError` failures in `dispatch-failures.jsonl` since the kill (was 69 historical); `bridge-poller-runner.lock` released; `dispatch-state.json` continues to update via the cross-harness event-driven trigger alone (verified at 2026-05-09T06:12:56Z, contention-free).

This mitigation is **not** a substitute for Slice 4 retirement — the runtime files, archived references, and the active surfaces flagged by Codex F1 still need the formal disposition this proposal defines. The mitigation simply stops the active token cost and dispatch-state contention while the formal retirement audit trail lands.

## Prior Deliberations

(Carried forward from `-001-007` plus this round's predecessor NO-GO and the session's mitigation authorization.)

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08`, `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08`.
- `DELIB-0836` (superseded), `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`, `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`.
- `DELIB-1418`, `DELIB-1419`, `DELIB-1104`.
- Slice 3 closure at `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- This thread `-001-002`, `-001-004`, `-001-006`, `-001-008` (four prior NO-GOs).
- Owner mitigation authorization, 2026-05-09 UTC: AskUserQuestion answer "Mitigate now, then land Slice 4 (Recommended)" — recorded in `memory/pending-owner-decisions.md` via the AUQ-only enforcement stack. Pending explicit DELIB capture.

## Specification Links

(Carried forward from `-001-007` with no additions; D5f surfaces remain within the existing cross-cutting spec set because they are CLI/source-code paths and live documentation, all governed by the same ADR/DCL surfaces already cited.)

**Cross-cutting (blocking):** `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-ARTIFACT-APPROVAL-001` v3.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Smart-poller-specific specs being dispositioned (unchanged from `-001-007`):** ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001 (v2 supersede); DCL-SMART-POLLER-AUTO-TRIGGER-001 (v2); DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001 (v2); PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001 (v2); PB-INCIDENT-S321-PROPOSAL-WITHOUT-SPEC-LINKAGE-001 (preserve); plus new DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09.

**NEW per `-001-008` F1 — Active desktop bootstrap path (D5f):**

| Path | Lines | Disposition |
|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/bootstrap.py` | 146-148 (`_copy_templates`) | **Retain** the `shutil.copy2(bridge_prompt, ...)` call. The file still ships as a deprecated compatibility prompt for adopters who reference it. No code change here. |
| `groundtruth-kb/src/groundtruth_kb/bootstrap.py` | 257 (`bootstrap_summary` line) | **Replace** `"  - bridge-os-poller-setup-prompt.md (legacy filename; smart-poller setup)"` with `"  - bridge-os-poller-setup-prompt.md (deprecated compatibility prompt; bridge dispatch is event-driven via PostToolUse + Stop hooks — see .claude/settings.json and .codex/hooks.json)"`. |
| `groundtruth-kb/src/groundtruth_kb/bootstrap.py` | 265 (Next steps line) | **Replace** `"  2. Open CLAUDE.md, MEMORY.md, BRIDGE-INVENTORY.md, and the bridge setup prompt."` with `"  2. Open CLAUDE.md, MEMORY.md, and BRIDGE-INVENTORY.md. (The bridge setup prompt file is preserved as a deprecated stub; bridge dispatch needs no per-project setup beyond the scaffolded hook registrations.)"`. |

The change is to `bootstrap.py` — code, not narrative-class. No formal-artifact-approval packet needed.

**NEW per `-001-008` F1 — Live documentation (D5f docs sweep):**

| Path | Lines | Disposition |
|---|---|---|
| `groundtruth-kb/docs/bootstrap.md` | 188 + surrounding | The `cp "$TEMPLATES/bridge-os-poller-setup-prompt.md" ./bridge-os-poller-setup-prompt.md` line stays (manual scaffold path); add a deprecation note immediately after: "**Note:** `bridge-os-poller-setup-prompt.md` is a deprecated compatibility prompt. Bridge dispatch is now event-driven via `PostToolUse` + `Stop` hooks registered in `.claude/settings.json` and `.codex/hooks.json`. The prompt is preserved for adopters that reference it but is not active setup material." Also update line 202-203 ("the bridge setup prompt") to remove the implication that the prompt is live setup material. |
| `groundtruth-kb/docs/architecture/product-split.md` | 56-61 | Replace `"OS-level pollers run the Prime and Loyal Opposition scans independently of active chat sessions."` with `"Bridge dispatch is event-driven via PostToolUse + Stop hooks; the retired OS poller and retired smart poller are no longer used."`. Replace `"`bridge-os-poller-setup-prompt.md` provides a reusable setup prompt for Claude Code or Codex."` with `"`bridge-os-poller-setup-prompt.md` is preserved as a deprecated compatibility stub; current bridge dispatch needs no per-project setup beyond scaffolded hook registrations."`. |
| `groundtruth-kb/docs/reference/templates.md` | 82-86 | Change row description from `"Prompt template for setting up OS-level bridge pollers"` to `"Deprecated compatibility stub; preserved for adopter scaffold continuity. Current bridge dispatch is event-driven via PostToolUse + Stop hooks."`. Optionally relabel section heading from "Bridge Automation" to "Bridge Automation (Deprecated Templates)" — accept reviewer preference. |
| `groundtruth-kb/docs/method/12-file-bridge-automation.md` | 237-251 ("Setup prompt" section) | Add a leading note: "**Deprecated.** The `bridge-os-poller-setup-prompt.md` template was for OS-level pollers, both of which (OS poller and smart poller) are retired as of 2026-05-09. New projects do not need to run this prompt; bridge dispatch is event-driven via `PostToolUse` + `Stop` hooks scaffolded into `.claude/settings.json` and `.codex/hooks.json`. The prompt content is preserved for adopters with existing references." Then keep the existing 5-step list as historical guidance. |

**NEW per `-001-008` F1 — Tests for the desktop bootstrap fix (D5f tests):**

| Path | Disposition |
|---|---|
| `groundtruth-kb/tests/test_cli.py` | In `TestBootstrapDesktop.test_bootstrap_desktop_creates_scaffold` (lines 398-439): **add** `summary_text = result.output` capture; **add** `assert "smart-poller setup" not in summary_text` (negative — confirms the F1 wording is gone); **add** `assert "deprecated compatibility prompt" in summary_text` (positive — confirms the new wording is present); **add** `assert "event-driven" in summary_text` (positive — confirms event-driven trigger context is present in the summary). The existing `assert (target / "bridge-os-poller-setup-prompt.md").exists()` line stays — the file is still copied, just relabeled. |
| `groundtruth-kb/tests/test_cli.py` | NEW test `test_bootstrap_desktop_summary_text_does_not_advertise_smart_poller_setup` — direct unit test of `bootstrap_summary()` (no CLI runner): asserts the negative + positive cases above. Catches regression if a future change reintroduces "smart-poller setup" wording in `bootstrap_summary()` without changing the CLI invocation. |

## Owner Decisions / Input

(Carried forward from `-001-007` with one new addition for the in-session mitigation.)

- **S337 retirement authorization (carried forward, unchanged):** Owner directive: "Please proceed..." (Slice 4 advancement) and "Remember to disable and clean up the old smart-poller when the new notifier becomes active." Recorded in DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09.
- **8-packet approval batch (carried forward, unchanged):** unchanged from `-001-005`. No additional packets needed for D5f (all code/doc-class, not narrative-authority-class).
- **Mitigation authorization, 2026-05-09 UTC (NEW this round):** AskUserQuestion answer "Mitigate now, then land Slice 4 (Recommended)" — owner authorized stopping PID 18616 + disabling `GTKB-SmartBridgePoller` task as a temporary mitigation while the formal retirement audit trail lands. Recorded in `memory/pending-owner-decisions.md` via the AUQ-only enforcement stack. This proposal IS the "land Slice 4" follow-through that the owner directive named.
- **D5f disposition decision (NEW this round):** Codex F1 recommended-action item 2 offered two paths — "deprecated stub with retained filename" or "rename to event-driven setup prompt". This proposal selects the first (retain filename, relabel surfaces) as the minimal-risk path. If Codex prefers a rename, that becomes the next REVISED.

## Pre-Filing Preflight

Both preflights were run by Prime Builder against `-001-009` after the INDEX entry was added; both pass.

**Applicability preflight (run 2026-05-09 UTC; current content):**

- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- Predecessor `-001-007` packet_hash for reference: `sha256:66ba0ae628f0440b89d6e8c22a9a44931a6fdfcd5bf4ee2c906d70546cb713af`. REVISED-4's packet_hash will be reported in Codex's verdict file at review time (the value depends on the file's exact byte content, which the verdict capture canonicalizes).

**Clause preflight (run 2026-05-09 UTC, after fixing the in-root path violation in D6 step 5):**

- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation), exit 0

The bridge file `-001-009.md` is filed under `E:\GT-KB\bridge\` and the `bridge/INDEX.md` entry for this thread now lists `REVISED: bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-009.md` at the top of the version stack, satisfying `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

The blocking-gap fix between the first preflight run and the passing run: D6 step 5 originally proposed a smoke test using an out-of-root sandbox path, which `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` correctly flagged. The verification step now uses `applications/_test_d5f_<uuid>/`, mirroring the established in-root sandbox pattern at `groundtruth-kb/tests/test_cli.py:450-451`.

## Implementation Plan (REVISED-4)

D1, D2, D3, D4, D5, D5b, D5c, D5d (REVISED-3 expansion), D5e (REVISED-3), D6 (REVISED-3 expansion), D7, D8, D9, D9b (REVISED-3) — all unchanged from `-001-007`.

### D5f (NEW per F1 of `-001-008`) — Desktop bootstrap path + live docs sweep

1. `groundtruth-kb/src/groundtruth_kb/bootstrap.py:257` — replace summary-line text per the table above.
2. `groundtruth-kb/src/groundtruth_kb/bootstrap.py:265` — replace Next-steps line per the table above.
3. `groundtruth-kb/docs/bootstrap.md:188 + 202-203` — add deprecation note after the `cp` line; remove implication that the prompt is live setup material.
4. `groundtruth-kb/docs/architecture/product-split.md:56-61` — replace OS-poller bullet and prompt description with event-driven + deprecated-stub language.
5. `groundtruth-kb/docs/reference/templates.md:86` — replace row description.
6. `groundtruth-kb/docs/method/12-file-bridge-automation.md:237-251` — prepend deprecated note to "Setup prompt" section.
7. `groundtruth-kb/tests/test_cli.py:398-439` — extend `test_bootstrap_desktop_creates_scaffold` with summary-text assertions.
8. `groundtruth-kb/tests/test_cli.py` — add new direct unit test `test_bootstrap_desktop_summary_text_does_not_advertise_smart_poller_setup`.

### D6 (EXPANDED per F1) — Verification additions

(Carry forward all REVISED-3 verifications. Add:)

27. (D5f.1) `python -c "from pathlib import Path; src = Path('groundtruth-kb/src/groundtruth_kb/bootstrap.py').read_text(); assert 'smart-poller setup' not in src; assert 'deprecated compatibility prompt' in src"` succeeds.
28. (D5f.2) `pytest groundtruth-kb/tests/test_cli.py::TestBootstrapDesktop -v` passes including the new assertions.
29. (D5f.3) `pytest groundtruth-kb/tests/test_cli.py::test_bootstrap_desktop_summary_text_does_not_advertise_smart_poller_setup -v` passes.
30. (D5f.4) `grep -nF "smart-poller setup\|smart-poller automation\|setting up OS-level bridge pollers" groundtruth-kb/docs/bootstrap.md groundtruth-kb/docs/architecture/product-split.md groundtruth-kb/docs/reference/templates.md groundtruth-kb/docs/method/12-file-bridge-automation.md` returns no live-instruction matches (only DEPRECATED redirect text is acceptable, and the regex is wired to allow that case via post-filter — exact form documented in D5f code in the implementation phase).
31. (D5f.5) Manual smoke test under the in-root sandbox per ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT: invoke `gt bootstrap-desktop test-prj --dir applications/_test_d5f_<uuid>/` (mirrors the established test pattern at `groundtruth-kb/tests/test_cli.py:450-451` `target = _GT_KB_HOST_ROOT / "applications" / sandbox_name`). Assert the printed summary contains "deprecated compatibility prompt" and does NOT contain the legacy smart-poller-setup wording. Clean up the sandbox after the assertion.

## Spec-Derived Test Plan (REVISED-4)

Carries forward all rows from `-001-007`. Adds:

| Test | Spec/Requirement | Method |
|---|---|---|
| T-4-bootstrap-summary-no-smart-poller-wording | D5f.1 (F1 fix) | `bootstrap.py` source contains no "smart-poller setup" string in `bootstrap_summary()`. |
| T-4-bootstrap-summary-event-driven-language | D5f.1 (F1 fix) | `bootstrap.py` source contains "deprecated compatibility prompt" and "event-driven" in `bootstrap_summary()`. |
| T-4-bootstrap-desktop-scaffold-summary-positive | D5f.2 (F1 fix) | `TestBootstrapDesktop.test_bootstrap_desktop_creates_scaffold` includes summary-text assertions: positive ("deprecated compatibility prompt", "event-driven") + negative ("smart-poller setup" not in output). |
| T-4-bootstrap-desktop-summary-direct-unit-test | D5f.3 (F1 fix) | New test `test_bootstrap_desktop_summary_text_does_not_advertise_smart_poller_setup` provides regression coverage independent of the CLI runner. |
| T-4-bootstrap-docs-no-live-smart-poller-instructions | D5f.4 (F1 fix) | The four flagged live docs contain no live-instruction text directing users to set up smart-poller / OS-level pollers; deprecation/redirect notes only. |

## Acceptance Criteria

- [ ] Codex confirms F1 fix (D5f: bootstrap.py summary text + Next-steps line + 4 live docs + 2 tests).
- [ ] Codex confirms the disposition decision (retain filename as deprecated stub, relabel surfaces) is acceptable per the F1 recommended-action item 2 framing. If Codex prefers a rename, escalate to REVISED-5.
- [ ] Codex confirms scope is finally complete — or identifies remaining surfaces.
- [ ] Codex confirms the in-session mitigation (PID 18616 stop + scheduled task disable) is documented as a separate step from the formal retirement audit trail in this proposal.

## Risk / Rollback

Carries forward `-001-007`. New rollback paths:

- **D5f**: revert `bootstrap.py:257` + `:265` summary-text edits; revert the four live docs to their pre-D5f wording; revert the two `test_cli.py` test additions. The deprecated-stub file `bridge-os-poller-setup-prompt.md` continues to ship either way (no change to the copy logic at `bootstrap.py:146-148`); only the wording around it changes.

The cross-harness trigger remains live throughout rollback. Even mid-rollback, the bootstrap path still works (just with the older "smart-poller setup" wording, which is the F1 defect — so rollback would reintroduce the misdirection surface, not break functionality).

The in-session mitigation (PID 18616 + task disable) is independently rollback-able: re-enabling the scheduled task and starting a new `bridge_poller_runner.py` process restores the pre-mitigation state. That restoration is **not** part of D5f rollback because the mitigation is an owner-authorized operational state change separate from the proposal's audit-trail scope.

## Files Expected To Change (REVISED-4)

Carries forward all entries from `-001-007`. New additions:

**Desktop bootstrap path (D5f):**

- `groundtruth-kb/src/groundtruth_kb/bootstrap.py` — `bootstrap_summary()` line 257 + line 265 wording.

**Live documentation (D5f docs sweep):**

- `groundtruth-kb/docs/bootstrap.md` — line 188 + 202-203 area.
- `groundtruth-kb/docs/architecture/product-split.md` — lines 56-61.
- `groundtruth-kb/docs/reference/templates.md` — line 86 (and optionally section heading).
- `groundtruth-kb/docs/method/12-file-bridge-automation.md` — lines 237-251 (Setup prompt section).

**Tests (D5f):**

- `groundtruth-kb/tests/test_cli.py` — `TestBootstrapDesktop.test_bootstrap_desktop_creates_scaffold` extended; new `test_bootstrap_desktop_summary_text_does_not_advertise_smart_poller_setup`.

## Open Follow-Ons

(Unchanged from `-001-007`.)

1. Adopter propagation through managed-artifact registry (`gtkb-bridge-trigger-adopter-propagation-001`).
2. Session-startup bridge-state surface (UX feature, optional).
3. Public tutorial rewrites (`gtkb-bridge-event-driven-tutorial-001`).
4. `gt bridge` CLI subcommand foundation.
5. Codex narrative-artifact-gate live promotion.
6. Cosmetic env-var rename — `GTKB_BRIDGE_POLLER_RUN_ID` → `GTKB_BRIDGE_TRIGGER_RUN_ID`; files separately as `gtkb-bridge-trigger-env-var-rename-001` after Slice 4 VERIFIED.
7. **NEW: Eventual filename retirement of `bridge-os-poller-setup-prompt.md`** — separate from this slice. After two release cycles where the file ships as a deprecated stub, retire the filename entirely. Files separately as `gtkb-bridge-os-poller-setup-prompt-filename-retirement-001` once adopter propagation is stable.

## Recommended Commit Type

`refactor:` — unchanged justification from `-001-007`. The retirement removes runtime infrastructure and relabels documentation surfaces without changing the user-facing dispatch behavior (which is already provided by the cross-harness event-driven trigger from Slices 1–3).

## Loyal Opposition Asks

1. Confirm F1 fix (D5f: bootstrap.py wording + 4 live docs + 2 test additions) is sufficient.
2. Confirm the deprecated-stub disposition decision is acceptable, or direct the rename path.
3. Confirm scope is finally complete — or identify remaining surfaces (this is REVISED-4; four prior NO-GOs found surfaces incrementally).
4. Confirm the in-session mitigation log in this proposal accurately separates operational-state mitigation from the formal retirement audit trail.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
