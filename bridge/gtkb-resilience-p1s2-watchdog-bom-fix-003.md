NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 75cea783-a1f3-4f8b-b834-cca62d92299c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: implementation_report
Document: gtkb-resilience-p1s2-watchdog-bom-fix
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4882
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Responds to: bridge/gtkb-resilience-p1s2-watchdog-bom-fix-002.md (GO)
Recommended commit type: fix

target_paths: ["scripts/ops/storm_watchdog_reap.py", "scripts/ops/harness_storm_watchdog.ps1", "platform_tests/scripts/test_storm_watchdog_reap.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Implemented the GO'd `-001` spec. The storm-watchdog FAILSAFE is repaired: the UTF-8 BOM that Windows PowerShell 5.1 `Set-Content -Encoding utf8` prepended to the candidate-process file is now both tolerated by the decider (utf-8-sig reads) and no longer written (BOM-less `.ps1` write). Implemented by the interactive Prime Builder (harness B); the daemon did not dispatch a headless PB worker for the GO within ~20 min, so the interactive PB carried it (the daemon's headless PB dispatch reliability is P3a / WI-4881). Review independence holds: `-001` author + this report are session `75cea783...` (harness B); the `-002` GO is from independent Cursor session `cursor-e-20260626-lo-autoproc-5` (harness E).

### Implemented changes

1. `scripts/ops/storm_watchdog_reap.py` — the three file reads now use `encoding="utf-8-sig"` (BOM-tolerant): the `--processes-file` read (the PS-written candidates file), the lease `*.lock` read, and the provenance-ledger read. Writes remain plain `utf-8` (no BOM). `decide_reap` (the reap decision) is unchanged.

2. `scripts/ops/harness_storm_watchdog.ps1` — the candidate-file write is now `[System.IO.File]::WriteAllText($procFile, $procJson)` (UTF-8, no BOM on all PowerShell versions), with an explanatory comment. Defense in depth alongside the utf-8-sig read.

3. `platform_tests/scripts/test_storm_watchdog_reap.py` — added `test_main_parses_bom_prefixed_processes_file`: `main()` with a BOM-prefixed `--processes-file` returns exit 0 and prints a valid decision (previously raised JSONDecodeError → exit 1).

## Specification Links

(Carried forward from `-001`.)

- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed as the next numbered bridge file in the append-only versioned chain.
- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher storm-recovery surface repaired.
- `GOV-17` (Automation script modification approval gate) — dispatcher automation modified; owner-authorized via `DELIB-20266276` D2 + the cited PAUTH.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied; WI-4882 + PAUTH present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied; spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` — WI-4882 authorized standing-backlog item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — durable tracked surfaces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — tracked as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — repair triggered by a work-item-tracked defect.

## Spec-to-Test Mapping

| Spec / clause | Test | Result |
|---|---|---|
| D2 storm-recovery: decider parses the watchdog's processes file | `test_main_parses_bom_prefixed_processes_file` (new) | PASS — BOM-prefixed `--processes-file` → exit 0 + valid `{reap,protect,reasons}` |
| No decision-logic regression | existing `test_storm_watchdog_reap.py` suite (15 tests) | PASS — `decide_reap` protect/reap tiers + provenance attribution unchanged |

## Verification Evidence

pytest over the test module via the repo venv: **16 passed in 0.48s** (15 existing + 1 new BOM regression test).

`ruff check` on the changed Python files: All checks passed! `ruff format --check`: 2 files already formatted.

**Real-world proof:** running the patched decider against the LIVE `.gtkb-state/ops/storm-watchdog-candidates.json` (which carries the BOM, and which produced `exit=1` / FAILSAFE before this fix) now returns **exit 0** with a valid decision `{"protect": [], "reap": [], "reasons": {}}` — the watchdog will no longer sit in FAILSAFE. (`reap=[]` is correct here: the live candidates are the owner's interactive Codex session, which the safety scoping correctly leaves untouched.)

## Files Changed

- `scripts/ops/storm_watchdog_reap.py` (modified — 3 reads → utf-8-sig)
- `scripts/ops/harness_storm_watchdog.ps1` (modified — BOM-less candidate-file write)
- `platform_tests/scripts/test_storm_watchdog_reap.py` (modified — BOM regression test)
- `bridge/gtkb-resilience-p1s2-watchdog-bom-fix-003.md` (this report)

## Owner Decisions / Input

No new owner decision required. Implementation authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION` (owner scope-lock `DELIB-20266276` D2 — full auto-recovery including storm reaping within one watchdog cycle, which requires a working watchdog).

## Recommended Commit Type

`fix` — repairs the storm-watchdog FAILSAFE (BOM I/O mismatch) so storm reaping works; no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
