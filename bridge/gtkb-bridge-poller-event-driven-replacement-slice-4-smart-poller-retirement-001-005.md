REVISED

# Implementation Proposal — Bridge Poller Event-Driven Replacement Slice 4 (Smart-Poller Retirement) — REVISED-2

bridge_kind: implementation_slice
Document: gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001
Version: 005 (REVISED-2 post NO-GO at `-001-004`)
Author: Prime Builder (Claude, harness B)
Date: 2026-05-09 UTC
Supersedes: `bridge/gtkb-bridge-poller-event-driven-replacement-slice-4-smart-poller-retirement-001-003.md`

## Claim

REVISED-2 carries forward all REVISED-1 scope and adds the three remaining active test/import + status/interface surfaces Codex `-001-004` flagged as P1 omissions. The expanded surface list is now:

- Test surfaces tied to retired script imports (F1+F2 of `-001-004`):
  - `tests/scripts/test_bridge_notify_reader.py` — imports `bridge_notify_reader.py` via `importlib.util.spec_from_file_location`; would fail collection post-archive.
  - `groundtruth-kb/tests/test_doctor_smart_poller.py` (15,239 bytes) — directly imports `_check_smart_bridge_poller` and exercises smart-poller fixtures; would fail collection post-removal.
- Operational status + system-interface surfaces still publishing smart-poller as active (F3 of `-001-004`):
  - `groundtruth-kb/src/groundtruth_kb/operating_state.py` lines 23 (COMPONENTS tuple), 102 (probe registration), 250-260 (`_probe_smart_poller` reads `.gtkb-state/bridge-poller/notifications/`).
  - `groundtruth-kb/src/groundtruth_kb/cli.py` line 290 (`gt state` component choices).
  - `config/agent-control/system-interface-map.toml:188-209` (`[[systems]] id = "smart-poller" lifecycle_state = "active"`).

## Prior Deliberations

(Carried forward from `-001-003` plus this revision's predecessor NO-GO.)

- `DELIB-S337-CODEX-HOOKS-WINDOWS-RETEST-2026-05-08`, `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08`, `DELIB-0836` (superseded), `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`, `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`, `DELIB-1418`, `DELIB-1419`, `DELIB-1104`.
- Slice 3 closure at `bridge/gtkb-bridge-poller-event-driven-replacement-slice-3-hook-registrations-006.md`.
- This thread `-001-002` (first NO-GO; F1-F4 found in `-001`).
- This thread `-001-004` (second NO-GO; 3 P1 surfaces missed in `-001-003`).

## Specification Links

(Carried forward from `-001-003` with additions for the new F1+F2+F3 surfaces.)

**Cross-cutting (blocking):** `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-ARTIFACT-APPROVAL-001` v3.

**Cross-cutting (advisory):** `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`.

**Smart-poller-specific specs being dispositioned (unchanged from `-001-003` F1):**

| Spec | Disposition |
|---|---|
| `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` v1 | Supersede with v2 (event-driven trigger as new mechanism) |
| `DCL-SMART-POLLER-AUTO-TRIGGER-001` v1 | Supersede with v2 (impl pointer updated) |
| `DCL-SPAWNED-HARNESS-ROLE-DEFER-DURABLE-RECORD-001` v1 | Supersede with v2 (impl pointer updated) |
| `PB-INCIDENT-S321-DAEMON-DISPATCH-DISABLED-001` v1 | Supersede with v2 (protected behavior reframed for trigger) |
| `PB-INCIDENT-S321-PROPOSAL-WITHOUT-SPEC-LINKAGE-001` v1 | Preserve unchanged (mechanism-agnostic) |

Plus new `DELIB-S337-SMART-POLLER-RETIREMENT-2026-05-09` capturing the retirement decision.

**Operational artifacts archived (carried forward from `-001-003`):**

`scripts/run_smart_bridge_poller.vbs`, `.ps1`, `install_smart_poller_task.ps1`, `uninstall_smart_poller_task.ps1`, `groundtruth-kb/scripts/bridge_poller_runner.py`, `groundtruth-kb/tests/test_bridge_poller_runner.py`, `scripts/bridge_notify_reader.py`. Plus `archive/smart-poller-2026-05-09/README.md` (NEW).

**NEW per `-001-004` F1+F2:**

| Path | Size | Disposition |
|---|---|---|
| `tests/scripts/test_bridge_notify_reader.py` | (active; loads reader via importlib) | Archive to `archive/smart-poller-2026-05-09/tests/test_bridge_notify_reader.py`. No replacement test needed (reader itself is gone). |
| `groundtruth-kb/tests/test_doctor_smart_poller.py` | 15,239 bytes | Archive. Replace with NEW `groundtruth-kb/tests/test_doctor_cross_harness_trigger.py` (NEW; covers the new `_check_cross_harness_trigger` doctor check). |

**Notification cleanup (D8; unchanged from `-001-003`):**

`.gtkb-state/bridge-poller/notifications/*` removed; `_render_smart_poller_section` disabled.

**Authority-narrative surfaces being edited (D5; unchanged from `-001-003`):**

`.claude/rules/bridge-essential.md`, `.claude/rules/canonical-terminology.md`, `AGENTS.md`. (3 narrative-approval-packet edits.)

**Scaffold + template surfaces being edited (D5b; unchanged from `-001-003`):**

`groundtruth-kb/src/groundtruth_kb/project/scaffold.py` lines 783-802, `groundtruth-kb/templates/bridge-os-poller-setup-prompt.md` (DEPRECATED stub), `groundtruth-kb/templates/rules/bridge-poller-canonical.md` (DEPRECATED stub).

**Tutorial DEPRECATED headers (D5d; unchanged from `-001-003`):**

`groundtruth-kb/docs/tutorials/bridge-smart-poller.md`, `bridge-smart-poller-activation.md`. Full rewrite as Open Follow-On §3.

**NEW per `-001-004` F3 — Operational status + system-interface transition (D9 NEW):**

| File | Lines | Disposition |
|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/operating_state.py` | 23 (COMPONENTS), 102 (probe map), 250-260 (`_probe_smart_poller`) | Replace `"smart-poller"` component with `"cross-harness-trigger"`. Replace `_probe_smart_poller` with NEW `_probe_cross_harness_trigger` that: (a) checks `scripts/cross_harness_bridge_trigger.py` exists; (b) checks hook registrations present in `.claude/settings.json` + `.codex/hooks.json`; (c) reads `.gtkb-state/bridge-poller/dispatch-state.json` for recent activity (`updated_at` within freshness window). Status: PASS / WARN (no recent activity) / FAIL (script missing or hooks unregistered). |
| `groundtruth-kb/src/groundtruth_kb/cli.py` | 290 | Replace `"smart-poller"` with `"cross-harness-trigger"` in `gt state --component` choice list. |
| `config/agent-control/system-interface-map.toml` | 188-209 | Two-step: (a) mark existing `[[systems]] id = "smart-poller"` block with `lifecycle_state = "retired"` + supersession reference; (b) add NEW `[[systems]] id = "cross-harness-trigger"` block with `lifecycle_state = "active"`, canonical name "cross-harness event-driven trigger", authoritative source `scripts/cross_harness_bridge_trigger.py`, related_specs citing the v2 ADR/DCL/PB and Slice 3+4 bridge threads. Preserves historical-record + makes active surface correct. |
| `groundtruth-kb/tests/test_operating_state.py` | (no smart-poller string match per probe) | Update if any hardcoded component-list assertions break post-rename. |
| `tests/scripts/test_system_interface_map.py` | (no smart-poller string match per probe) | Update if any required-seed-id checks reference `"smart-poller"`. |

The `system-interface-map.toml` two-block approach preserves the historical record (the smart-poller is now `lifecycle_state = "retired"` with its provenance + supersession link) while the new `cross-harness-trigger` block becomes the active automation runtime. This matches the pattern Slice 1 used for ADR supersession (v1 verified, v2 active).

## Owner Decisions / Input

(Unchanged from `-001-003`.)

S337 owner authorization is direct: "Please proceed..." and "Remember to disable and clean up the old smart-poller when the new notifier becomes active."

The 8-packet approval batch from `-001-003` (5 spec v2 + 1 new DELIB + 3 narrative) extends with:
- Whether to also wrap the system-interface-map.toml change in a packet — proposing NOT (it's a config file, not a narrative authority surface; standard code review applies).

Total batch: 8 packets unchanged. Per-spec activations: owner acknowledgement of the first packet activates the batch.

## Pre-Filing Preflight

The applicability preflight will be re-run after this REVISED-2 entry is added to `bridge/INDEX.md`. Predecessor `-001-003` reported `preflight_passed: true` packet_hash `sha256:1117eeaa...`. REVISED-2's content delta is the F1+F2+F3 fixes; spec linkage stays within the registered cross-cutting set.

## Implementation Plan (REVISED-2)

D1-D5d are unchanged from `-001-003`. D7-D8 are unchanged. New additions:

### D2 (EXPANDED) — Archive surfaces

Carries forward `-001-003` D2 list and adds:

- `tests/scripts/test_bridge_notify_reader.py` → `archive/smart-poller-2026-05-09/tests/test_bridge_notify_reader.py` (no replacement test).
- `groundtruth-kb/tests/test_doctor_smart_poller.py` → `archive/smart-poller-2026-05-09/tests/test_doctor_smart_poller.py`.

### D4 (EXPANDED) — Doctor refactor + new test

Carries forward `-001-003` D4 (remove `_check_smart_bridge_poller`, add `_check_cross_harness_trigger`, preserve `_check_bridge_poller`). Adds:

- NEW `groundtruth-kb/tests/test_doctor_cross_harness_trigger.py` — exercises `_check_cross_harness_trigger` with synthetic project trees:
  - All conditions pass (script + Claude hooks + Codex hooks + recent dispatch-state) → PASS.
  - Script missing → FAIL.
  - Claude hooks not registered → FAIL.
  - Codex hooks not registered → FAIL.
  - Dispatch-state stale (or absent) → WARN.
  - At least 5 tests covering the status mapping.

### D9 NEW — Operating-state + CLI + system-interface-map transition (per `-001-004` F3)

1. **`groundtruth-kb/src/groundtruth_kb/operating_state.py`**:
   - Line 23 COMPONENTS tuple: replace `"smart-poller"` with `"cross-harness-trigger"`.
   - Line 102 probe_map: replace `"smart-poller": lambda: _probe_smart_poller(root)` with `"cross-harness-trigger": lambda: _probe_cross_harness_trigger(root)`.
   - Lines 250-260: replace `_probe_smart_poller` with `_probe_cross_harness_trigger`. New probe logic:
     - Check `scripts/cross_harness_bridge_trigger.py` exists.
     - Check `.claude/settings.json` has PostToolUse + Stop registrations invoking the trigger.
     - Check `.codex/hooks.json` has PostToolUse + Stop registrations invoking the trigger.
     - Read `.gtkb-state/bridge-poller/dispatch-state.json` for last `updated_at` timestamp.
     - Status: FAIL (script missing or hook missing); WARN (state file absent or stale > N minutes); PASS (script + hooks + recent state).
2. **`groundtruth-kb/src/groundtruth_kb/cli.py` line 290**:
   - Replace `"smart-poller"` with `"cross-harness-trigger"` in the Click `Choice` for `gt state --component`.
3. **`config/agent-control/system-interface-map.toml` lines 188-209**:
   - Mark existing `[[systems]] id = "smart-poller"` block: `lifecycle_state = "retired"`; add `superseded_by = "cross-harness-trigger"`; update `harness_caveats` to point at event-driven trigger.
   - Add NEW `[[systems]] id = "cross-harness-trigger"` block immediately after, with `lifecycle_state = "active"`, canonical name, authoritative source, read/mutation/role/visibility fields populated, `related_specs` citing the v2 ADR/DCL/PB and the Slice 3 + Slice 4 bridge threads.
4. **`groundtruth-kb/tests/test_operating_state.py`**:
   - Probed: no direct smart-poller string match. May need updates if any test enumerates the COMPONENTS tuple or tests `_probe_smart_poller` specifically.
   - Add 1-2 tests for `_probe_cross_harness_trigger` covering PASS/WARN/FAIL.
5. **`tests/scripts/test_system_interface_map.py`**:
   - Probed: no direct smart-poller string match. May need updates if `REQUIRED_SEED_IDS` includes `"smart-poller"`.
   - Add assertion that `"cross-harness-trigger"` is in the loaded system map; assertion that `"smart-poller"` (if still present) has `lifecycle_state = "retired"`.

### D6 (EXPANDED) — Verification

D6 verification list from `-001-003` plus:

16. (D2 expansion) `ls tests/scripts/test_bridge_notify_reader.py groundtruth-kb/tests/test_doctor_smart_poller.py` returns "no such file"; archive copies present.
17. (D4 expansion) `python -m pytest groundtruth-kb/tests/test_doctor_cross_harness_trigger.py -q` passes ≥ 5 tests.
18. (D9.1) `python -c "import groundtruth_kb.operating_state as os; assert 'cross-harness-trigger' in os.COMPONENTS; assert 'smart-poller' not in os.COMPONENTS"` succeeds.
19. (D9.2) `gt state --component cross-harness-trigger` returns valid output; `gt state --component smart-poller` errors with "invalid choice".
20. (D9.3) `python -c "from pathlib import Path; import tomllib; m = tomllib.loads(Path('config/agent-control/system-interface-map.toml').read_text()); ids = {s['id']: s['lifecycle_state'] for s in m['systems']}; assert ids.get('smart-poller') == 'retired'; assert ids.get('cross-harness-trigger') == 'active'"` succeeds.
21. (D9.4+5) `pytest groundtruth-kb/tests/test_operating_state.py tests/scripts/test_system_interface_map.py -q` passes.

## Spec-Derived Test Plan (REVISED-2)

Carries forward all rows from `-001-003`. Adds:

| Test | Spec/Requirement | Method |
|---|---|---|
| T-4-test-bridge-notify-reader-archived | D2 expansion (F1) | `tests/scripts/test_bridge_notify_reader.py` not at active path; archive copy present. |
| T-4-test-doctor-smart-poller-archived | D2 expansion (F2) | `groundtruth-kb/tests/test_doctor_smart_poller.py` not at active path; archive copy present. |
| T-4-doctor-cross-harness-trigger-tests | D4 expansion | `groundtruth-kb/tests/test_doctor_cross_harness_trigger.py` exists with ≥ 5 tests covering PASS/WARN/FAIL/script-missing/hook-missing. |
| T-4-operating-state-component-renamed | D9.1 | COMPONENTS tuple has `cross-harness-trigger`, NOT `smart-poller`. |
| T-4-operating-state-probe-renamed | D9.1 | `_probe_cross_harness_trigger` defined; `_probe_smart_poller` removed. |
| T-4-cli-component-renamed | D9.2 | `gt state --component` accepts `cross-harness-trigger`, rejects `smart-poller`. |
| T-4-system-interface-map-smart-poller-retired | D9.3 | `[[systems]] id = "smart-poller"` has `lifecycle_state = "retired"`. |
| T-4-system-interface-map-trigger-active | D9.3 | `[[systems]] id = "cross-harness-trigger"` exists with `lifecycle_state = "active"`. |
| T-4-pytest-collection-clean-post-archive | D6 expansion | `pytest --collect-only -q tests/scripts/ groundtruth-kb/tests/` succeeds with no `ImportError` or missing-file errors after D2 archives. |
| T-4-no-active-smart-poller-import | D6 expansion | `grep -rln "from groundtruth_kb.project.doctor import _check_smart_bridge_poller" .` returns no live tests. |

## Acceptance Criteria

- [ ] Codex confirms F1 fix (`test_bridge_notify_reader.py` archived) is sufficient.
- [ ] Codex confirms F2 fix (`test_doctor_smart_poller.py` archived + new `test_doctor_cross_harness_trigger.py`) is the right shape.
- [ ] Codex confirms F3 fix (D9: operating_state.py + cli.py + system-interface-map.toml two-block transition) is sufficient.
- [ ] Codex confirms the system-interface-map two-block approach (smart-poller block marked retired + new cross-harness-trigger block active) preserves the right historical record.
- [ ] Codex confirms scope is finally complete — or identifies remaining surfaces.

## Risk / Rollback

Carries forward `-001-003`. New rollback paths for D2 expansion + D9:
- D2 expansion: move archived test files back to active paths.
- D9.1+9.2: revert COMPONENTS tuple + cli choice list + restore `_probe_smart_poller`.
- D9.3: revert system-interface-map.toml; the smart-poller block returns to `lifecycle_state = "active"`; remove the cross-harness-trigger block.

## Files Expected To Change (REVISED-2)

Carries forward all entries from `-001-003`. New additions:

**Test surfaces archived (D2 expansion; F1+F2 fix):**

- `tests/scripts/test_bridge_notify_reader.py` → archive
- `groundtruth-kb/tests/test_doctor_smart_poller.py` → archive

**Doctor test (D4 expansion):**

- `groundtruth-kb/tests/test_doctor_cross_harness_trigger.py` (NEW; covers `_check_cross_harness_trigger`)

**Operating-state + CLI + system-interface (D9 NEW):**

- `groundtruth-kb/src/groundtruth_kb/operating_state.py` — component rename + probe replacement
- `groundtruth-kb/src/groundtruth_kb/cli.py` — component choice rename
- `config/agent-control/system-interface-map.toml` — two-block transition (smart-poller retired + cross-harness-trigger active)
- `groundtruth-kb/tests/test_operating_state.py` — add probe coverage for `_probe_cross_harness_trigger`
- `tests/scripts/test_system_interface_map.py` — assertions for both lifecycle blocks

## Open Follow-Ons

(Unchanged from `-001-003`.)

## Recommended Commit Type

`refactor:` — unchanged justification.

## Loyal Opposition Asks

1. Confirm F1 fix (archive `test_bridge_notify_reader.py`) is sufficient.
2. Confirm F2 fix (archive `test_doctor_smart_poller.py` + add new `test_doctor_cross_harness_trigger.py` covering the new doctor check) is the right shape.
3. Confirm D9 (operating_state.py + cli.py + system-interface-map.toml) addresses F3 fully.
4. Confirm the two-block system-interface-map approach (smart-poller retired + cross-harness-trigger active) is the right historical-record pattern.
5. Confirm scope is finally complete, or identify remaining surfaces.
6. Confirm the 8-packet approval batch (unchanged from `-001-003`) is still right; no new packets needed for the system-interface-map change since it's config-class not narrative-authority-class.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
