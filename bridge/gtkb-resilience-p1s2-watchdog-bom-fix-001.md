NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 75cea783-a1f3-4f8b-b834-cca62d92299c
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal

# gtkb-resilience-p1s2-watchdog-bom-fix — Resilience P1 Slice 2: repair the storm-watchdog FAILSAFE (UTF-8 BOM breaks the reap decider)

Document: gtkb-resilience-p1s2-watchdog-bom-fix
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-27 UTC
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4882
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION
Recommended commit type: fix

target_paths: ["scripts/ops/storm_watchdog_reap.py", "scripts/ops/harness_storm_watchdog.ps1", "platform_tests/scripts/test_storm_watchdog_reap.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Slice 2 of WI-4882 repairs the storm-watchdog, which has been stuck in FAILSAFE (reaping nothing) — confirmed live from `.gtkb-state/ops/storm-watchdog.log`: every ~60s cycle logs `candidates=9 reaped=0 reason=decider exit=1 output-empty=True`. The watchdog is GT-KB's storm-recovery mechanism (DELIB-20266276 D2: storm → reaped within one watchdog cycle); while it fails safe (no false kills), it provides NO actual storm protection, so a real dispatch storm would go unreaped.

### Root cause (diagnosed against live state)

`harness_storm_watchdog.ps1` (line 143) writes the candidate-process JSON with `Set-Content -Path $procFile -Value $procJson -Encoding utf8`. On Windows PowerShell 5.1 (the scheduled-task host), `-Encoding utf8` prepends a UTF-8 byte-order mark (BOM). The decider `storm_watchdog_reap.py` (line 422) reads that file with `read_text(encoding="utf-8")`, which does NOT strip the BOM, so `json.loads` raises `JSONDecodeError: Unexpected UTF-8 BOM` → the decider exits 1 with empty stdout → the `.ps1` enters FAILSAFE. Reproduced manually: running the decider against the live `storm-watchdog-candidates.json` with stderr visible shows exactly this traceback.

### Deliverables (precise)

1. `scripts/ops/storm_watchdog_reap.py` — change the three file reads (`--processes-file` read at line 422, the lease read at line 301, the provenance-ledger read at line 331) from `encoding="utf-8"` to `encoding="utf-8-sig"`. `utf-8-sig` transparently strips a leading BOM when present and is identical to `utf-8` when absent, so the decider parses BOM-prefixed and BOM-less inputs alike. This is the robust consumer-side fix.

2. `scripts/ops/harness_storm_watchdog.ps1` — change the candidate-file write (line 143) from `Set-Content ... -Encoding utf8` to a BOM-less write via `[System.IO.File]::WriteAllText($procFile, $procJson)` (UTF-8 no BOM on all PowerShell versions). Defense in depth: the BOM never gets written in the first place.

3. `platform_tests/scripts/test_storm_watchdog_reap.py` — add a regression test: `main()` invoked with a `--processes-file` whose bytes begin with a UTF-8 BOM returns exit 0 and emits a valid `{"reap": ..., "reasons": ...}` decision (previously raised JSONDecodeError → exit 1).

No change to the reap DECISION logic (`decide_reap` is untouched); this is an I/O-encoding repair only.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; this proposal is filed as the next numbered bridge file (`bridge/gtkb-resilience-p1s2-watchdog-bom-fix-001.md`) in the append-only versioned bridge chain, with the report and verdict to follow as later numbered versions.
- `ADR-DISPATCHER-ARCHITECTURE-001` — the dispatcher storm-recovery surface this repairs.
- `GOV-17` (Automation script modification approval gate) — modifies dispatcher automation (the watchdog runner + decider); owner-authorized via `DELIB-20266276` D2 + the cited PAUTH.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: cites governing specs; test mapped below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: WI-4882 + PROJECT-GTKB-DISPATCHER-RELIABILITY + active PAUTH present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: the BOM-parse repair maps to the derived regression test.
- `GOV-STANDING-BACKLOG-001` — WI-4882 is an authorized standing-backlog item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — the fix + regression test are durable tracked surfaces.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — tracked as durable artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — repair triggered by a work-item-tracked defect.

## Prior Deliberations

- `DELIB-20266276` — Daemon Resilience scope-lock. D2 (full auto-recovery, all modes — storm reaped within one watchdog cycle) requires a functioning watchdog; this slice restores it.
- `DELIB-20266104` — owner decision authorizing the WI-4828 storm-watchdog liveness-awareness slice (the decider this repair fixes the I/O for).
- `DELIB-20266272` — PHASE-Y go-live, during which the watchdog FAILSAFE state was observed and captured as a WI-4882 finding.

## Owner Decisions / Input

Implementation-authorized under `PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-DAEMON-RESILIENCE-PROGRAM-IMPLEMENTATION` (active; includes WI-4882 + ADR-DISPATCHER-ARCHITECTURE-001 + GOV-17; allowed mutations source, test, config; cites `DELIB-20266276`). The owner's D2 decision (full auto-recovery including storm reaping within one watchdog cycle) requires a working watchdog; this slice is the repair that makes D2's storm-recovery real. No new owner decision is required — this is a defect fix within the authorized scope.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement is `DELIB-20266276` D2's storm-auto-recovery clause; the watchdog already implements the correct liveness-aware reap decision (WI-4828) but is non-functional due to the BOM I/O defect. This slice restores the existing intended behavior; no new requirement.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| D2 storm-recovery: decider parses the watchdog's processes file | `test_main_parses_bom_prefixed_processes_file` (new) | `main()` with a `--processes-file` whose bytes start with a UTF-8 BOM returns exit 0 and prints a valid `{"reap":...,"reasons":...}` JSON decision (no JSONDecodeError). |
| No decision-logic regression | existing `test_storm_watchdog_reap.py` suite | PASS — `decide_reap` protection/reap classification unchanged. |

Commands (pre-report): targeted `pytest` over `test_storm_watchdog_reap.py` via the repo venv; `ruff check` AND `ruff format --check` on the changed Python file. The BOM input is constructed deterministically in the test (a leading BOM character prepended to the JSON, written to a tmp file); no real watchdog run or process kill in the test path.

## Risk / Rollback

- **Risk:** `utf-8-sig` on a file that is genuinely UTF-8 without a BOM is a no-op, so the read change is strictly safe. The `.ps1` BOM-less write changes only the byte prefix, not the JSON content.
- **Isolation:** no change to `decide_reap` (the reap decision), to dispatch, or to harness identity (DELIB-20265888 preserved). The watchdog still fails safe on any genuine error.
- **Rollback:** single-commit revert restores the prior encoding. No KB mutation (`kb_mutation_in_scope: false`); append-only bridge history untouched.

## Recommended Commit Type

`fix` — repairs the storm-watchdog FAILSAFE defect (BOM I/O mismatch) so storm reaping works; no new capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
