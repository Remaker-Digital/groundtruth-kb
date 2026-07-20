Title: WI-4479 Codex Dispatch Disposition Advisory
Date: 2026-06-13
Author: Loyal Opposition (Codex harness A)
WIs: WI-4479
Specs: GOV-FILE-BRIDGE-AUTHORITY-001, REQ-HARNESS-REGISTRY-001, GOV-SOURCE-OF-TRUTH-FRESHNESS-001

# WI-4479 Codex Dispatch Disposition Advisory

## Claim

WI-4479 is still a useful backlog item, but its current title and root-cause
framing are stale. The live workspace no longer has the suspected deprecated
Codex hook flag. The remaining defect is narrower and should be reframed as:
headless Codex dispatch can start, but Codex hook failures and dispatch-state
attribution make it unsafe to claim Codex AXIS-1 review dispatch is healthy.

## Evidence

- Live role projection still makes Codex a dispatch receiver:
  `python -m groundtruth_kb.cli harness roles` reports harness `A` / `codex`
  with role `["loyal-opposition"]`, `status: active`, and
  `can_receive_dispatch: true`.
- Live Codex config has already moved past the suspected root cause:
  `.codex/config.toml` now uses `[features]` with `hooks = true`, not
  `codex_hooks`.
- The historical Codex dispatch run cited by WI-4479 did not die before
  startup. `2026-06-13T08-50-41Z-loyal-opposition-A-150ece.stderr.log`
  shows Codex v0.130.0-alpha.5 starting, loading the prompt, firing
  `SessionStart`, `UserPromptSubmit`, `PreToolUse`, and `PostToolUse`, and
  successfully executing the first shell read of `.codex/skills/bridge/SKILL.md`.
- That same log shows repeated hook failures: `SessionStart Failed`,
  `UserPromptSubmit Failed`, many `PreToolUse Failed` lines, and five
  `PostToolUse Failed` lines before process termination.
- Current dispatch state no longer shows a fresh Codex selected-candidate run.
  `scripts/cross_harness_bridge_trigger.py --diagnose` reports Codex/A idle
  with no pending LO work, Antigravity/C dispatched, and one missing
  OpenRouter/F state record. The overall dispatch health is still DEGRADED.
- Current dispatch state contains confusing attribution for `loyal-opposition:A`:
  the `loyal-opposition:A` record's `selected_candidate` and `last_launch`
  can point at Ollama/D. Recent failure records also include
  `recipient: loyal-opposition:A` for dispatch IDs whose file stem is
  `loyal-opposition-D-*`.
- The ordered-fallback behavior itself has regression coverage:
  `python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short`
  passed `77` tests. The relevant tests cover preferred-recipient selection,
  not-ready fallback, same-harness author refusal, and no-ready results.

## Finding

### P1 - WI-4479 currently mixes a stale root-cause claim with a still-real dispatch-health gap

Observation:
The backlog row says the candidate root cause is `.codex/config.toml` using
deprecated `[features].codex_hooks`. Live config no longer has that setting.
The old Codex run also got far enough to process at least one shell command, so
the failure mode is not simply "Codex cannot start." The observed remaining
symptoms are hook failures inside the headless Codex process and ambiguous
dispatch-state/failure attribution across `loyal-opposition:A` and
Ollama-selected dispatch IDs.

Deficiency rationale:
Leaving WI-4479 as written invites Prime to fix a configuration value that is
already corrected while missing the remaining evidence. That creates duplicate
effort with FAB-01 / WI-4413 and the newer ordered-fallback work, and it also
keeps the owner-facing backlog overstating the current failure mode.

Recommended action:
Do not implement WI-4479 as "replace `codex_hooks`." Reframe it through a normal
bridge proposal as one of these explicit dispositions:

1. Supersede or close the deprecated-config portion against the live
   `.codex/config.toml` state.
2. Keep a narrowed residual work item for headless Codex hook-failure diagnosis,
   with acceptance criteria that a synthetic or real headless Codex dispatch can
   finish at least one no-op bridge-review turn without hook failures.
3. Add dispatch-state attribution checks so a recipient-specific state record
   cannot persist another harness's `selected_candidate` / `last_launch` as if it
   were its own live launch.

## Prime Builder Context

Objective:
Clarify WI-4479 so Prime work targets the remaining defect instead of the stale
deprecated-config theory.

Preconditions:
No owner decision is required for the advisory disposition. Any source change
still needs a normal bridge proposal and GO.

Evidence paths:
- `.codex/config.toml`
- `.gtkb-state/bridge-poller/dispatch-state.json`
- `.gtkb-state/bridge-poller/dispatch-runs/2026-06-13T08-50-41Z-loyal-opposition-A-150ece.stderr.log`
- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`

Expected file touchpoints for an implementation proposal:
- `scripts/cross_harness_bridge_trigger.py`
- `platform_tests/scripts/test_cross_harness_bridge_trigger.py`
- Codex hook/config tests if the residual hook-failure path is retained

Verification:
- Existing baseline: `python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short` currently passes.
- Future verification should include a regression that fails if
  `loyal-opposition:A` state records carry another harness's selected candidate
  or last launch.
- Future verification should include one explicit headless Codex dispatch
  launchability/smoke path or a deterministic substitute if live model dispatch
  is too expensive for CI.

Open decisions:
None for this LO report.

## Commands Run

```text
python -m groundtruth_kb.cli harness roles
python .claude\skills\bridge\helpers\scan_bridge.py --role loyal-opposition --format json
python scripts\cross_harness_bridge_trigger.py --diagnose
python -m groundtruth_kb.cli backlog list --id WI-4479 --json
Select-String -LiteralPath .codex\config.toml -Pattern '\[features\]|codex_hooks|hooks|approval|sandbox' -Context 2,2
codex --version
Select-String -LiteralPath .gtkb-state\bridge-poller\dispatch-runs\2026-06-13T08-50-41Z-loyal-opposition-A-150ece.stderr.log -Pattern 'Failed|ERROR|error|BLOCKED|blocked|panic|exit|hook:'
python -m pytest platform_tests\scripts\test_cross_harness_bridge_trigger.py -q --tb=short
```

## Result

- Bridge scan: no current LO-actionable latest `NEW` or `REVISED` entries.
- Test result: `77 passed`.
- No owner action required.
