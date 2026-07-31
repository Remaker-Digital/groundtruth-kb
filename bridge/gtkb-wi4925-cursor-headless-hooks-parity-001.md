NEW
author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: 2026-06-29T18-00-00Z-prime-builder-E-cursor-headless-hooks
author_model: Cursor Agent
author_model_version: composer-2.5
author_model_configuration: Cursor interactive Prime Builder session, harness E

# gtkb-wi4925-cursor-headless-hooks-parity — Cursor headless hook parity (stop Windows console storms)

bridge_kind: prime_proposal
Document: gtkb-wi4925-cursor-headless-hooks-parity
Version: 001
Author: Cursor Prime Builder
Date: 2026-06-29 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4925

target_paths: [".cursor/hooks.json", "scripts/cursor_hook_adapter.py", ".cursor/gtkb-hooks/workstream-focus.cmd", "platform_tests/scripts/test_cursor_hook_headless_parity.py"]

implementation_scope: source,test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Stop crippling **Windows console window storms** during interactive Cursor (harness E) agent sessions by aligning Cursor hook wiring with the **already-verified Codex headless pattern**.

Live evidence from 2026-06-29: each Cursor agent `Shell` tool call and each governance hook firing (`postToolUse`, `preToolUse`, `beforeShellExecution`, `sessionStart`, `stop`) spawns visible consoles because `.cursor/hooks.json` uses bare `python` and raw `cmd /d /s /c` for `.cmd` hooks, while `.codex/hooks.json` uses `pythonw.exe` and `.codex/gtkb-hooks/run_cmd_no_window.py`. The adapter layer compounds the problem: `scripts/cursor_hook_adapter.py` re-spawns `sys.executable` without `CREATE_NO_WINDOW`, producing **double consoles** on every Write/Shell gate check.

This slice is intentionally narrow: **mirror Codex headless hook commands in Cursor**, harden the adapter subprocess disposition, add focused parity tests, and verify manually that a representative agent Write + Shell cycle produces **zero new console windows**. It does **not** change hook semantics, dispatch topology, daemon wiring, or Codex/Claude hook surfaces. It also does **not** claim to make Cursor's agent `Shell` tool itself headless — that remains a separate product limitation; this slice targets **GT-KB hook and adapter spawns** that multiply on every tool use.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — protected hook/config edits require bridge GO and implementation-start authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal links governing specs and maps them to verification evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — carries PAUTH, project, work item, and inline JSON target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — implementation report and LO verdict map specs to executed tests/commands.
- `GOV-STANDING-BACKLOG-001` — `WI-4925` is the durable backlog authority for this workstation-blocking defect.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — bounded by active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — promotes the console-storm finding from chat/scratch into WI, bridge, report, and verdict.
- `ADR-CROSS-HARNESS-PARITY-001` — cross-harness hook behavior must not diverge on safety-critical spawn disposition.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — parity discovery/release gates must catch Cursor regressions to visible-console hook wiring.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex hook interception is the verified reference for Windows no-window hook execution (`pythonw.exe`, `run_cmd_no_window.py`).

## Prior Deliberations

- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` — refreshed hook-parity stance: `.codex/hooks.json` is live authority for Windows no-window hook execution.
- `bridge/gtkb-wi4778-cursor-headless-dispatch-readiness-003.md` — related Cursor headless work; covers **dispatch CLI readiness**, not hook console suppression (complementary, out of scope here).
- `bridge/gtkb-wi4788-slice-3-cursor-blackbox-gate-parity-003.md` — precedent for additive `.cursor/hooks.json` parity using `cursor_hook_adapter.py`.
- `bridge/gtkb-wi4897-release-gate-parity-hard-gate-alignment-008.md` — recent session surfaced console storms during parallel agent Shell + hook activity on Windows.
- Owner report 2026-06-29 — visible console storms and stacked agent windows during Cursor interactive work; requested headless-default hook parity filing.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

No new owner decision is required. The owner explicitly requested filing this bridge proposal to make headless spawns the default for Cursor hooks. Work is bounded under active `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` for defect-class reliability fixes.

## Requirement Sufficiency

Existing cross-harness parity requirements are sufficient. Codex already encodes the canonical Windows headless hook pattern; Cursor must converge without reopening hook semantics.

## Proposed Implementation

1. **Rewrite `.cursor/hooks.json` hook commands to Codex parity:**
   - Replace every `python E:\GT-KB\...` with `pythonw.exe E:\GT-KB\...` (use the project venv interpreter path where applicable: `groundtruth-kb\.venv\Scripts\pythonw.exe` if needed for dependency consistency).
   - Replace `cmd /d /s /c E:\GT-KB\.cursor\gtkb-hooks\*.cmd` invocations with `pythonw.exe E:\GT-KB\.codex\gtkb-hooks\run_cmd_no_window.py E:\GT-KB\.cursor\gtkb-hooks\*.cmd` (reuse the verified wrapper; do not fork a second implementation).
   - Preserve hook event names, matchers, ordering, and timeouts — **command launcher only**, not behavior.

2. **Fix `.cursor/gtkb-hooks/workstream-focus.cmd` inner launcher:**
   - Replace bare `python` with `pythonw.exe` (or delegate entirely to the `run_cmd_no_window.py` outer wrapper so the `.cmd` never spawns a console-attached interpreter).

3. **Harden `scripts/cursor_hook_adapter.py`:**
   - Pass `creationflags=CREATE_NO_WINDOW` on Windows for the inner `subprocess.run` that executes target hook scripts (same pattern as `scripts/cursor_harness.py` and `scripts/cross_harness_bridge_trigger.py`).

4. **Add `platform_tests/scripts/test_cursor_hook_headless_parity.py`:**
   - Assert `.cursor/hooks.json` contains **no** bare `python ` hook commands (allow `pythonw.exe` only).
   - Assert every `.cursor/gtkb-hooks/*.cmd` reference in hooks.json is routed through `run_cmd_no_window.py`.
   - Assert `cursor_hook_adapter.py` sets `CREATE_NO_WINDOW` (source inspection or behavioral stub test).
   - Optionally cross-check command parity against `.codex/hooks.json` for shared hook targets (session dispatch, bridge trigger, reconciler, spec-classifier, etc.).

5. **Manual verification evidence in implementation report:**
   - Before/after: one Cursor agent `Write` + one `Shell` while watching for new console windows (expect **zero hook-origin consoles** after fix; Shell tool may still flash one console — record honestly).

## Cross-Harness Disposition

| Surface | Change |
|---|---|
| Cursor `.cursor/hooks.json` | **Yes** — primary target |
| Cursor `cursor_hook_adapter.py` | **Yes** |
| Codex `.codex/hooks.json` | **No** — reference only |
| Claude `.claude/settings.json` | **No** — out of scope |
| Reuse `.codex/gtkb-hooks/run_cmd_no_window.py` | **Yes** — shared verified wrapper |

`scripts/parity_discovery_diff.py` currently reports `hook:run_cmd_no_window` absent on Cursor; this slice should clear that asymmetry for hook command wiring.

## Spec-Derived Verification Plan

| Spec / surface | Verification |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Mint implementation-start packet before protected edits; cite packet hash in report. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi4925-cursor-headless-hooks-parity` → `preflight_passed: true`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi4925-cursor-headless-hooks-parity` → zero blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run focused pytest module + manual no-console observation; include outputs in report. |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | New parity tests green; optional `python scripts/parity_discovery_diff.py` shows reduced hook asymmetry. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Cursor hook commands match Codex no-window launcher pattern for shared scripts. |

Concrete commands after implementation:

```text
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_cursor_hook_headless_parity.py -q --tb=short
groundtruth-kb\.venv\Scripts\python.exe -m ruff check scripts/cursor_hook_adapter.py platform_tests/scripts/test_cursor_hook_headless_parity.py
groundtruth-kb\.venv\Scripts\python.exe -m ruff format --check scripts/cursor_hook_adapter.py platform_tests/scripts/test_cursor_hook_headless_parity.py
python -c "import json; json.loads(open('.cursor/hooks.json', encoding='utf-8').read())"
```

## Acceptance Criteria

- [ ] `.cursor/hooks.json` uses `pythonw.exe` (or venv `pythonw.exe`) for all Python hook commands; no bare `python ` launcher remains.
- [ ] All Cursor `.cmd` hook invocations route through `run_cmd_no_window.py`.
- [ ] `.cursor/gtkb-hooks/workstream-focus.cmd` does not spawn a console-attached Python interpreter.
- [ ] `cursor_hook_adapter.py` passes `CREATE_NO_WINDOW` for inner hook subprocesses on Windows.
- [ ] `platform_tests/scripts/test_cursor_hook_headless_parity.py` passes and fails if regression reintroduces bare `python` hook commands.
- [ ] Manual spot-check: representative agent Write + Shell produces zero **hook-origin** console windows.

## Risk / Rollback

Risk is low-medium. `pythonw.exe` preserves stdin/stdout pipes for hook JSON protocols (Codex proves this at scale). Main risk is a hook that accidentally depended on an attached console for stderr visibility — mitigated by preserving hook scripts unchanged and only altering launchers/disposition.

Rollback is a single revert of `.cursor/hooks.json`, `cursor_hook_adapter.py`, the `.cmd` fix, and the new test file.

## Out of Scope

- Making Cursor Agent `Shell` itself headless (product/runtime limitation).
- Suppressing headless **dispatch** agent UI windows (Antigravity/Cursor chat stacking) — tracked separately under dispatch/readiness work (`WI-4778` family).
- Rewriting hook fan-out count (multiple `postToolUse` hooks per tool use remains; only console visibility changes).
- Claude or Codex hook registry edits.

## Recommended Commit Type

fix: align Cursor hooks with headless pythonw/run_cmd_no_window parity
