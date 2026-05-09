REVISED

# Implementation Proposal — Bridge Poller Event-Driven Replacement Slice 4 (Smart-Poller Retirement) — REVISED-1

bridge_kind: implementation_slice
Document: gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001
Version: 003 (REVISED post NO-GO at `-001-002`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001.md`

## Claim

REVISED-1 expands Slice 4 scope to address all four P1 findings from Codex `-001-002` NO-GO. The retirement is no longer "stop the daemon and archive the runner"; it is **a complete active-surface transition** spanning operational artifacts, governance specs, narrative authority, scaffold/template surfaces, and live notification cleanup.

The four NO-GO blockers and their REVISED-1 responses:

- **F1 — Smart-poller specs/tests not dispositioned.** REVISED-1 enumerates 5 smart-poller-specific MemBase records and dispositions each (3 supersede with v2 implementation-pointer updates; 1 preserve unchanged; 1 covered by separate test-refactor work).
- **F2 — Active launchers/installers left broken.** REVISED-1 expands D2 to archive ALL active runtime surfaces: VBS launcher, PowerShell wrapper, install task script, uninstall task script, and the runner.
- **F3 — Notification cleanup cannot be deferred.** REVISED-1 makes notification-directory cleanup + `_render_smart_poller_section` disable part of this slice (D8 NEW). Live `pending-bridge-action-*.json` files (probed: codex notification with `written_at: 2026-05-09T04:38:54+00:00` for a NEW on this very thread) are removed in the implementation.
- **F4 — Canonical terminology, scaffold, onboarding still describe smart-poller as current.** REVISED-1 expands D5 to cover `.claude/rules/canonical-terminology.md` § "smart poller", `AGENTS.md` lines 102/164/200, `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` template strings (lines 783-802), and the two scaffolded templates (`bridge-os-poller-setup-prompt.md`, `bridge-poller-canonical.md`). Public tutorials get a DEPRECATED-stub treatment and full rewrite is filed as Open Follow-On §3.

## Prior Deliberations

(Carried forward from `-001` plus this thread's NO-GO at `-001-002`.)

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08` (rowid 1550) — empirical foundation.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` (rowid 1551).
- `DELIB-0836` (rowid 844) — superseded.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` — owner clarification: smart-poller became opt-out when functional; retiring it requires complete active-surface transition.
- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION` — prior redirect from spawn-first to notification/current-state behavior.
- `DELIB-1418`, `DELIB-1419`, `DELIB-1104` — compressed prior smart-poller threads.
- Parent `-010`: VERIFIED Slice 1+2.
- Slice 3 `-006`: VERIFIED Slice 3 hook registrations live (commit `d2511cec`).
- This thread `-001-002`: NO-GO with F1-F4 findings; addressed in this REVISED.

## Specification Links

**Cross-cutting (blocking):**

- `GOV-FILE-BRIDGE-AUTHORITY-001` — INDEX-as-canonical-state preserved.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Test Plan §T-4-* below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all touched files under `E:\GT-KB`. Archive path `archive/smart-poller-2026-05-09/` is in-root.
- `GOV-ARTIFACT-APPROVAL-001` v3 — Slice 4 supersession packets (5 below) flow through the formal-artifact-approval gate using the same scoped-auto-approval pattern as Slice 1's `event-driven-replacement-slice-1-batch-2026-05-09`. New batch ID for Slice 4: `event-driven-replacement-slice-4-batch-2026-05-NN`.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Smart-poller-specific specs being dispositioned (F1 fix):**

| Spec | Current | Disposition |
|---|---|---|
| `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v1 (architecture_decision, specified) | Pins the smart-poller as the mechanism delivering owner-out-of-loop bridge dispatch. | **Supersede with v2.** New v2 documents the event-driven cross-harness trigger as the new mechanism delivering the same owner-out-of-loop property; cites `scripts/cross_harness_bridge_trigger.py` + Slice 3 hook registrations as the implementation. Approval-packet-gated. |
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` v1 (design_constraint, specified) | Constrains: smart-poller auto-triggers harness when actionable signature changes. | **Supersede with v2.** Behavior contract preserved (auto-trigger on actionable signature change); implementation pointer updated to `scripts/cross_harness_bridge_trigger.py` (PostToolUse + Stop hook activation). Approval-packet-gated. |
| `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v1 (design_constraint, specified) | Constrains: dispatched harness defers role to durable record (`operating-role.md`). | **Supersede with v2.** Behavior contract preserved (the trigger script's `_dispatch_prompt` includes the same role-line about reading the durable role record); implementation pointer updated. Approval-packet-gated. |
| `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v1 (protected_behavior, specified) | Protects against the S321 incident where smart-poller daemon dispatch was silently disabled. | **Supersede with v2.** Protected behavior reframed: the cross-harness trigger MUST dispatch on actionable signature change; absence of dispatch state updates after a signature change is the new symptom of the same class of regression. Doctor's `_check_cross_harness_trigger` is the new detector. Approval-packet-gated. |
| `PB-INCIDENT-S321-PROPOSAL-WITHOUT-SPEC-LINKAGE-001` v1 (protected_behavior, specified) | Mechanism-agnostic: protects against bridge proposals filed without spec linkage. | **Preserve unchanged.** Not specific to smart-poller mechanism; the ban on no-linkage proposals applies regardless of automation path. |

**Operational artifacts being retired (F2 fix; D2 expanded):**

| Path | Size | Disposition |
|---|---|---|
| `scripts/run_smart_bridge_poller.vbs` | 5,111 bytes | Archive to `archive/smart-poller-2026-05-09/` |
| `scripts/run_smart_bridge_poller.ps1` | 2,775 bytes (NEW per F2) | Archive |
| `scripts/install_smart_poller_task.ps1` | 3,110 bytes (NEW per F2) | Archive |
| `scripts/uninstall_smart_poller_task.ps1` | 909 bytes (NEW per F2) | Archive (post-retirement no live task to uninstall) |
| `groundtruth-kb/scripts/bridge_poller_runner.py` | 27,151 bytes | Archive |
| `scripts/bridge_notify_reader.py` | (NEW per F3 implication) | Archive (only reads now-dead `notifications/*` paths) |
| Windows scheduled task `GTKB-SmartBridgePoller` | (currently `Running`) | Delete via D1 |

**Live notification artifacts being cleaned (F3 fix; D8 NEW):**

- `.gtkb-state/bridge-poller/notifications/pending-bridge-action-codex.json` (currently has NEW for this thread, `written_at: 2026-05-09T04:38:54+00:00`)
- `.gtkb-state/bridge-poller/notifications/pending-bridge-action-codex.md`
- `.gtkb-state/bridge-poller/notifications/pending-bridge-action-prime.json`
- `.gtkb-state/bridge-poller/notifications/pending-bridge-action-prime.md`
- Stale `pending-bridge-action-codex (1).json`, `(1).md`, `(2).json`, `(2).md` from prior runs.

**Authority-narrative surfaces being edited (F4 blocking minimum; D5 expanded; approval-packet-gated):**

| File | Lines | Disposition |
|---|---|---|
| `.claude/rules/bridge-essential.md` | 23-79 (§ "Operational Mode" + Incident History append) | Narrative edit; § "Re-Enabling Pollers" PRESERVED unchanged |
| `.claude/rules/canonical-terminology.md` | 911-934 (§ "smart poller" entry) + new § "cross-harness event-driven trigger" entry | Narrative edit; mark smart-poller entry as RETIRED with redirect |
| `AGENTS.md` | 102, 164, 200 | Narrative edit; replace "verified smart poller" with "cross-harness event-driven trigger" |

**Scaffold/template surfaces being edited (F4 blocking minimum):**

| File | Disposition |
|---|---|
| `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` lines 783-802 | Code edit: replace template-variable values referring to "verified smart poller" with cross-harness trigger equivalents. Not narrative-artifact-class. |
| `groundtruth-kb/templates/bridge-os-poller-setup-prompt.md` (4,131 bytes) | Replace body with DEPRECATED stub: "Smart-poller retired 2026-05-09 (Slice 4); use scripts/cross_harness_bridge_trigger.py via PostToolUse + Stop hook registrations." |
| `groundtruth-kb/templates/rules/bridge-poller-canonical.md` (2,950 bytes) | Same DEPRECATED stub treatment. |

**Tutorials (F4 deferrable per Codex; Open Follow-On §3 with stub-warning treatment in this slice):**

| File | Slice 4 treatment | Follow-on |
|---|---|---|
| `groundtruth-kb/docs/tutorials/bridge-smart-poller.md` (1,317 bytes) | Add DEPRECATED warning header in this slice + redirect link to event-driven docs (when written) | Full rewrite in `gtkb-bridge-event-driven-tutorial-001` |
| `groundtruth-kb/docs/tutorials/bridge-smart-poller-activation.md` (5,617 bytes) | Same DEPRECATED stub + redirect | Same follow-on |

**Doctor (D4):**

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py`: remove `_check_smart_bridge_poller` (lines 2101-~2400) + constants (1836-1840) + call site (line 2560); preserve `_check_bridge_poller` (mechanism-agnostic per-recipient liveness, line 1849); add `_check_cross_harness_trigger`.

**Tests (D7 + D8 + others):**

- `tests/scripts/test_cross_harness_bridge_trigger.py` — D7 frozen-reference refactor (replace cross-import of `bridge_poller_runner.py` with inline frozen-reference helper).
- `tests/scripts/test_session_self_initialization.py` — D8 update: `_render_smart_poller_section` tests reflect the disabled state (return empty list); 6 existing tests at lines 1873-2003 either removed or refactored to assert empty-output.
- `groundtruth-kb/tests/test_bridge_poller_runner.py` — archive alongside `bridge_poller_runner.py` (test target retired; tests follow).
- `groundtruth-kb/tests/test_doctor.py` (or equivalent) — remove smart-poller-specific assertions; add cross-harness-trigger assertions.

## Owner Decisions / Input

This proposal cites the AUQ-only rule. Owner authorization for the slice is direct from S337:

| AUQ question | Answer | Implication |
|---|---|---|
| (S337) | "Please proceed with the implementation of the gtkb-bridge-poller-event-driven-replacement" | Authorizes the slice progression. |
| (S337) Reminder | "Remember to disable and clean up the old smart-poller when the new notifier becomes active" | Direct authorization for cleanup. The expanded scope in REVISED-1 fits "disable AND clean up" — F1-F4 all reflect cleanup work. |

The 5 supersession packets + 3 narrative-artifact packets in this slice flow through `GOV-ARTIFACT-APPROVAL-001` v3 scoped-auto-approval batch `event-driven-replacement-slice-4-batch-2026-05-NN`. Activation: owner acknowledgement of the first packet activates the batch.

## Pre-Filing Preflight

Per `.claude/rules/file-bridge-protocol.md`: the applicability preflight will be re-run after this REVISED entry is added to `bridge/INDEX.md`. Predecessor `-001` reported `preflight_passed: true` packet_hash `sha256:26425d1f...`. REVISED-1's content delta is the F1-F4 fixes; spec linkage expands but stays within the registered cross-cutting set.

## Implementation Plan (REVISED)

### D1 — Decommission Windows scheduled task (unchanged from `-001`)

`schtasks /Delete /TN GTKB-SmartBridgePoller /F`

### D2 — Archive all active runtime surfaces (EXPANDED per F2)

Move to `archive/smart-poller-2026-05-09/`:

- `scripts/run_smart_bridge_poller.vbs`
- `scripts/run_smart_bridge_poller.ps1` (NEW)
- `scripts/install_smart_poller_task.ps1` (NEW)
- `scripts/uninstall_smart_poller_task.ps1` (NEW)
- `groundtruth-kb/scripts/bridge_poller_runner.py`
- `groundtruth-kb/tests/test_bridge_poller_runner.py` (test target retired; tests follow)
- `scripts/bridge_notify_reader.py` (NEW per F3 — only reads dead `notifications/*` paths)

Add `archive/smart-poller-2026-05-09/README.md` documenting retirement context.

### D3 — Dispatch-state path: REUSED (unchanged)

No-op operationally; documented in §"Files Changed" as preserved.

### D4 — `gt project doctor` updates (unchanged from `-001`)

As described in `-001` D4. `_check_bridge_poller` (per-recipient liveness reading dispatch-state.json) is mechanism-agnostic and PRESERVED.

### D5 — Authority-narrative edits (EXPANDED per F4)

Three approval-packet-gated narrative edits:

1. `.claude/rules/bridge-essential.md` — § "Operational Mode" + Incident History (as in `-001`).
2. `.claude/rules/canonical-terminology.md` — § "smart poller" entry marked RETIRED with redirect; new § entry for "cross-harness event-driven trigger" or similar canonical name. Sources updated to cite `scripts/cross_harness_bridge_trigger.py` + Slice 3 hook registrations + the v2 supersessions of ADR/DCL/PB records.
3. `AGENTS.md` — lines 102/164/200 updated. The "verified smart poller when available" guidance becomes "cross-harness event-driven trigger".

### D5b — Scaffold + template edits (NEW per F4 blocking minimum)

Code/template edits (NOT narrative-artifact-approval-class; standard code review applies):

1. `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` lines 783-802 — replace template-variable values:
   - `{{PATH_TO_ENTRYPOINT}}`: "bridge/INDEX.md + verified smart poller" → "bridge/INDEX.md + cross-harness event-driven trigger"
   - `{{HOW_IT_RUNS}}`: "Verified smart poller invokes project-owned scanner scripts" → "PostToolUse + Stop hooks invoke `scripts/cross_harness_bridge_trigger.py`"
   - `{{AUTOMATION_NAME}}`: "file-bridge-smart-poller" → "file-bridge-cross-harness-trigger"
   - `{{SCHEDULE}}`: "Smart-poller registration interval or manual fallback" → "Event-driven on tool-use; manual fallback via `Bridge` prompt"
   - `{{SOURCE}}`: "bridge-os-poller-setup-prompt.md ..." → "Slice 3 hook registrations in `.claude/settings.json` + `.codex/hooks.json`"
   - `{{FAILURE_SIGNAL}}`: "No recent scan logs or stale actionable bridge entries" → "No dispatch-state updates after INDEX changes"

2. `groundtruth-kb/templates/bridge-os-poller-setup-prompt.md` — replace body with DEPRECATED stub.
3. `groundtruth-kb/templates/rules/bridge-poller-canonical.md` — replace body with DEPRECATED stub.

### D5c — Spec supersessions (NEW per F1)

Five supersession-class MemBase mutations under approval batch `event-driven-replacement-slice-4-batch-2026-05-NN`:

1. `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v2 — same owner-out-of-loop architecture decision; new mechanism is the event-driven trigger.
2. `DCL-SMART-POLLER-AUTO-TRIGGER-001` v2 — auto-trigger contract preserved; implementation pointer updated.
3. `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v2 — durable-role-defer contract preserved; implementation pointer updated.
4. `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v2 — protected-behavior reframed: trigger MUST dispatch on actionable signature change; doctor's `_check_cross_harness_trigger` is the new detector.
5. `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` (NEW deliberation) — captures the retirement decision, references `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` as the prior policy stance now superseded by event-driven mechanism.

`PB-INCIDENT-S321-PROPOSAL-WITHOUT-SPEC-LINKAGE-001` PRESERVED unchanged (mechanism-agnostic).

### D5d — Tutorial DEPRECATED stubs (per F4 deferrable; Open Follow-On §3 follow-up)

Add stub headers to `bridge-smart-poller.md` and `bridge-smart-poller-activation.md`:

```
> ⚠️ **DEPRECATED** — The smart-poller mechanism was retired 2026-05-09 in
> favor of the cross-harness event-driven trigger. Do NOT follow this tutorial
> for new installations. See `[event-driven dispatch tutorial — coming in
> follow-on]` for the replacement. Smart-poller activation per these
> instructions will fail because the runner has been archived.
```

The full rewrite is filed as Open Follow-On §3 (`gtkb-bridge-event-driven-tutorial-001`).

### D6 — Verification (EXPANDED)

After D1-D5d complete:

1. (D1) `cmd /c schtasks /Query /TN GTKB-SmartBridgePoller` returns ERROR.
2. (D2) `ls scripts/run_smart_bridge_poller.* scripts/install_smart_poller_task.ps1 scripts/uninstall_smart_poller_task.ps1 groundtruth-kb/scripts/bridge_poller_runner.py scripts/bridge_notify_reader.py` returns "no such file" for each.
3. (D2) `ls archive/smart-poller-2026-05-09/` shows the archived files + README.
4. (D2) NEW: `grep -rln "GTKB-SmartBridgePoller" scripts/` returns no active scripts. The PS1 wrappers cannot recreate the scheduled task because they're archived.
5. (D3) `ls .gtkb-state/bridge-poller/dispatch-state.json` exists (preserved).
6. (D6 lock cleanup) `ls .gtkb-state/bridge-poller/bridge-poller-runner.lock` returns "no such file".
7. (D4) Doctor: `_check_smart_bridge_poller` not importable; `_check_cross_harness_trigger` importable + passes; `_check_bridge_poller` still importable.
8. (D4) `gt project doctor` exits 0 (no NEW errors).
9. (D5) Pre-commit narrative-artifact-approval gate accepts the 3 narrative edits (bridge-essential.md, canonical-terminology.md, AGENTS.md) against their approval packets.
10. (D5b) Scaffold round-trip: `gt project init <synthetic>` produces no smart-poller references in scaffolded files.
11. (D5c) Five MemBase supersessions: rowid + status + change_reason cite their approval packet paths.
12. (D5d) Tutorials grep: both files contain "DEPRECATED" header.
13. (D7) `tests/scripts/test_cross_harness_bridge_trigger.py` no longer cross-imports `bridge_poller_runner.py`; frozen-reference helper produces byte-identical signatures.
14. (D8) `.gtkb-state/bridge-poller/notifications/` directory empty or removed; `_render_smart_poller_section` returns empty list; smart-poller-section tests at `test_session_self_initialization.py:1873-2003` updated.
15. Manual round-trip: a bridge mutation in this very slice triggers event-driven dispatch via `dispatch-state.json` updates; smart-poller no longer involved (post-D1, the daemon doesn't exist).

### D7 — Parity test refactor (unchanged from `-001`)

Frozen-reference helper inside `test_cross_harness_bridge_trigger.py` replaces the `bridge_poller_runner.py` cross-import.

### D8 — Notification cleanup + session-startup surface disable (NEW per F3)

1. Remove all files under `.gtkb-state/bridge-poller/notifications/`:
   - `pending-bridge-action-codex.json` + `.md`
   - `pending-bridge-action-prime.json` + `.md`
   - Stale `(1)` and `(2)` variants from prior runs.
   - The directory itself may be left as an empty directory, OR removed entirely.
2. Disable `_render_smart_poller_section` in `scripts/session_self_initialization.py`:
   - Replace the body with `return []` and a comment citing this slice as the retirement point.
   - OR (simpler) remove the function entirely and remove its call sites; the smart-poller-section tests are then removed too.
3. Update `tests/scripts/test_session_self_initialization.py:1873-2003`:
   - Either replace each test with an assertion that the section is now always empty.
   - Or remove the smart-poller-section test block entirely.
4. Archive `scripts/bridge_notify_reader.py` (only reads now-dead notification files).
5. Verification: `ls .gtkb-state/bridge-poller/notifications/` shows empty or absent; session-startup payload no longer contains a smart-poller-section.

## Spec-Derived Test Plan (REVISED)

| Test | Spec/Requirement | Method |
|---|---|---|
| T-4-task-removed | D1 | `cmd /c schtasks /Query /TN GTKB-SmartBridgePoller` returns ERROR. |
| T-4-runtime-surfaces-archived | D2 (F2 fix) | All 7 retired files (5 PS1/VBS/runner + tests + reader) absent at active paths; archive copies present. |
| T-4-no-active-script-recreates-task | D2 (F2 fix) | `grep -rln "GTKB-SmartBridgePoller" scripts/` returns no live scripts. |
| T-4-archive-readme | D2 | `archive/smart-poller-2026-05-09/README.md` exists + contains retirement context. |
| T-4-doctor-smart-poller-removed | D4 | Programmatic: `_check_smart_bridge_poller` not importable. |
| T-4-doctor-cross-harness-added | D4 | Programmatic: `_check_cross_harness_trigger` importable + status=pass. |
| T-4-doctor-bridge-poller-preserved | D4 | Programmatic: `_check_bridge_poller` (per-recipient liveness) STILL importable. |
| T-4-bridge-essential-narrative | D5 | Pre-commit narrative-artifact-approval gate accepts; § "Re-Enabling Pollers" PRESERVED verbatim. |
| T-4-canonical-terminology-narrative | D5 (NEW per F4) | Pre-commit gate accepts; § "smart poller" marked RETIRED; new event-driven entry present. |
| T-4-agents-md-narrative | D5 (NEW per F4) | Pre-commit gate accepts; AGENTS.md no longer instructs "verified smart poller". |
| T-4-scaffold-template-vars | D5b (NEW per F4) | Programmatic: `gt project init <synthetic>` produces no `verified smart poller` / `bridge_poller_runner` strings in scaffolded output. |
| T-4-template-deprecated-stubs | D5b (NEW per F4) | `templates/bridge-os-poller-setup-prompt.md` + `templates/rules/bridge-poller-canonical.md` contain DEPRECATED header. |
| T-4-spec-supersessions | D5c (NEW per F1) | Five MemBase v2 inserts present (ADR/3×DCL/PB); change_reason cites approval packet path; `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` deliberation present. |
| T-4-pb-incident-spec-linkage-preserved | F1 (preservation) | `PB-INCIDENT-S321-PROPOSAL-WITHOUT-SPEC-LINKAGE-001` v1 still latest version; not superseded. |
| T-4-tutorial-deprecated-headers | D5d (NEW per F4) | Both tutorials contain DEPRECATED header. |
| T-4-parity-test-no-runner-import | D7 | `test_cross_harness_bridge_trigger.py` no longer cross-imports `bridge_poller_runner.py`. |
| T-4-parity-test-frozen-reference | D7 | Frozen-reference helper produces byte-identical signatures to trigger script. |
| T-4-notification-cleanup | D8 (NEW per F3) | `.gtkb-state/bridge-poller/notifications/` is empty or absent. |
| T-4-smart-poller-section-disabled | D8 (NEW per F3) | `_render_smart_poller_section` returns empty list (or function removed); session-startup payload contains no smart-poller-section content. |
| T-4-existing-suite-preserved | D6 | All 34 tests from Slice 3 still pass post-refactor. |
| T-4-no-doctor-error | D6 | `gt project doctor` exits 0. |
| T-4-manual-round-trip | D6 (live regression) | Bridge mutation triggers event-driven dispatch via dispatch-state.json updates; smart-poller daemon doesn't exist post-D1. |

## Acceptance Criteria

- [ ] Codex confirms F1 fix (5-spec disposition table; supersession-by-v2 pattern for the 4 affected; preservation for the mechanism-agnostic PB).
- [ ] Codex confirms F2 fix (D2 expanded to all 5 launcher/installer scripts + bridge_notify_reader.py; verification grep against `GTKB-SmartBridgePoller` in active scripts).
- [ ] Codex confirms F3 fix (D8 NEW: notification directory cleanup + `_render_smart_poller_section` disable + bridge_notify_reader.py archive in this slice; not deferred).
- [ ] Codex confirms F4 fix (D5 expanded to canonical-terminology + AGENTS.md + scaffold + 2 templates inline; tutorials get DEPRECATED stub in this slice with full rewrite as Open Follow-On §3).
- [ ] Codex confirms 5-packet approval batch + 3-narrative-packet approach (8 packets total in `event-driven-replacement-slice-4-batch-2026-05-NN`).
- [ ] Codex confirms `archive/smart-poller-2026-05-09/` is acceptable.
- [ ] Codex confirms `refactor:` is the right commit type given the expanded scope (no new capability; structural retirement spans many surfaces).

## Risk / Rollback

Risk surface unchanged from `-001`. The expanded scope adds:

- **Risk: Approval-packet count exceeds prior batch precedent (8 vs Slice 1's 3).** Mitigation: scoped-auto-approval is designed for batched packets per `GOV-ARTIFACT-APPROVAL-001` v3; owner activates batch on first packet acknowledgement.
- **Risk: Adopter-side regression after scaffold.py edits.** Mitigation: `groundtruth-kb/tests/test_scaffold_settings.py` + `test_managed_registry.py` baseline (34 passing) guards. Slice 4 adds adopter-template content updates that are tested at scaffold-roundtrip time.
- **Risk: `_render_smart_poller_section` removal regresses session-startup UX.** The renderer surfaced "X NEW entries pending" at session start. Post-removal, owner doesn't see that surface; they see only the cross-harness-trigger dispatch prompts (which are auto-fired) or trigger `Bridge`/`Bridge scan` manually. Mitigation: this is a UX downgrade only for owner-initiated sessions, not auto-dispatched sessions. If owner wants the surface back, a follow-on can derive it from dispatch-state.json. Slice 4 explicitly accepts this UX downgrade per F3.

Rollback per slice unchanged from `-001`. New rollback paths for expanded scope:
- D2 PS1 wrappers + reader: move back to active paths from archive.
- D5/D5b/D5d narrative + scaffold + tutorial edits: revert files; approval-packet append-only audit preserves prior state.
- D5c spec supersessions: append v3 to each ADR/DCL/PB reverting to v1's content. Append-only invariant preserved.
- D8 notifications + section disable: restore notification files (possible since they're regenerable from INDEX state); restore `_render_smart_poller_section` body + tests.

## Files Expected To Change (REVISED)

**Operational state:**

- Windows scheduled task `GTKB-SmartBridgePoller` removed.

**Code archived (D2 expanded; F2 fix):**

- `scripts/run_smart_bridge_poller.vbs` → archive
- `scripts/run_smart_bridge_poller.ps1` → archive
- `scripts/install_smart_poller_task.ps1` → archive
- `scripts/uninstall_smart_poller_task.ps1` → archive
- `groundtruth-kb/scripts/bridge_poller_runner.py` → archive
- `groundtruth-kb/tests/test_bridge_poller_runner.py` → archive
- `scripts/bridge_notify_reader.py` → archive (D8)
- `archive/smart-poller-2026-05-09/README.md` (NEW)

**Notification cleanup (D8; F3 fix):**

- `.gtkb-state/bridge-poller/notifications/*` removed.
- `scripts/session_self_initialization.py` `_render_smart_poller_section` disabled or removed.
- `tests/scripts/test_session_self_initialization.py:1873-2003` smart-poller-section tests updated/removed.

**Doctor (D4):**

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — `_check_smart_bridge_poller` removed; `_check_cross_harness_trigger` added; `_check_bridge_poller` preserved.
- `groundtruth-kb/tests/test_doctor.py` (or equivalent) — assertions updated.

**Authority-narrative edits (D5 expanded; F4 blocking minimum; approval-packet-gated):**

- `.claude/rules/bridge-essential.md` — narrative edit + Incident History S337 entry.
- `.claude/rules/canonical-terminology.md` — § "smart poller" RETIRED; new entry for event-driven trigger.
- `AGENTS.md` — lines 102/164/200 updated.

**Scaffold + template edits (D5b; F4 blocking minimum):**

- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` lines 783-802.
- `groundtruth-kb/templates/bridge-os-poller-setup-prompt.md` → DEPRECATED stub.
- `groundtruth-kb/templates/rules/bridge-poller-canonical.md` → DEPRECATED stub.

**Tutorials (D5d; F4 deferrable):**

- `groundtruth-kb/docs/tutorials/bridge-smart-poller.md` → DEPRECATED header.
- `groundtruth-kb/docs/tutorials/bridge-smart-poller-activation.md` → DEPRECATED header.

**Tests (D7):**

- `tests/scripts/test_cross_harness_bridge_trigger.py` — frozen-reference refactor.

**MemBase supersessions (D5c; F1 fix):**

- 5 approval packets at `.groundtruth/formal-artifact-approvals/2026-05-NN-{ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001-V2,DCL-SMART-POLLER-AUTO-TRIGGER-001-V2,DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001-V2,PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001-V2,DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09}.json`
- `groundtruth.db` — 5 new rows (4 spec v2 + 1 deliberation).

**Bridge thread:**

- `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-003.md` (this REVISED).
- `bridge/INDEX.md` (REVISED line for this thread).

## Open Follow-Ons (out of scope; flagged for separate threads)

1. **Adopter propagation through managed-artifact registry** (`gtkb-bridge-trigger-adopter-propagation-001`) — carried forward.
2. **Session-startup bridge-state surface (UX feature, optional)** — if owner wants startup to surface "X NEW entries pending" derived from `dispatch-state.json`, file separately as `gtkb-session-startup-bridge-surface-001`.
3. **Public tutorial rewrites** (`gtkb-bridge-event-driven-tutorial-001`) — replace the DEPRECATED stubs with full event-driven dispatch tutorials. Filed after Slice 4 VERIFIED.
4. **`gt bridge` CLI subcommand foundation** (parent thread Open Follow-On).
5. **Codex narrative-artifact-gate live promotion** (parent thread F5).

## Recommended Commit Type

`refactor:` — structural retirement spans operational artifacts, governance specs, narrative authority, scaffold, templates, and tests. No new capability surface lands in this commit (the new capability — cross-harness trigger — is already live from Slice 3 commit `d2511cec`).

## Loyal Opposition Asks

1. Confirm the F1 spec-disposition table (5 specs; 4 supersede-with-v2; 1 preserve unchanged) is correct and the supersession framing for each preserves the right behavior contract.
2. Confirm D2 expansion (5 launcher/installer scripts + reader + tests archived) is complete, or identify additional active surfaces.
3. Confirm D8 (notification cleanup inline + `_render_smart_poller_section` disable + bridge_notify_reader archive) addresses F3 sufficiently.
4. Confirm D5 expansion (canonical-terminology + AGENTS.md + bridge-essential.md narrative edits; scaffold.py + 2 templates code/template edits; 2 tutorial DEPRECATED headers) addresses F4 sufficiently. Confirm tutorial full rewrite as Open Follow-On §3 with stub-warning is acceptable per F4 deferrable framing.
5. Confirm 8-packet approval batch (4 spec v2 + 1 new DELIB + 3 narrative) is the right scoped-auto-approval batch shape.
6. Confirm scope is finally complete, or identify additional surfaces I missed.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
