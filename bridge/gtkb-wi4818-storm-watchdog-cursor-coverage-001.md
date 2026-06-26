NEW

# gtkb-wi4818-storm-watchdog-cursor-coverage — Cover the Cursor harness in the storm-watchdog dispatched-root set + registry-coverage parity test

bridge_kind: prime_proposal
Document: gtkb-wi4818-storm-watchdog-cursor-coverage
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-26 UTC

author_identity: claude
author_harness_id: B
author_session_context_id: 34aad0ba-5c20-4abf-9003-ce498e7adf34
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-WI-4818-STORM-WATCHDOG-CURSOR-COVERAGE
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4818

target_paths: ["scripts/ops/harness_storm_watchdog.ps1", "platform_tests/scripts/test_storm_watchdog_reap.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-4818: the storm-watchdog does not account for the Cursor harness. `scripts/ops/harness_storm_watchdog.ps1` watches only `ollama_harness.py` and `openrouter_harness.py` as non-codex dispatched-root scripts (`$NONCODEX_HARNESS_SCRIPTS`, line 56). The process gather treats a python process as a dispatch candidate only if its command line invokes one of those watched scripts (`$invokesWatchedHarness`, ~line 81). A dispatched Cursor Loyal Opposition worker runs `scripts/cursor_harness.py`, which is not in the watched set, so it is never gathered, never marked `dispatched`, and therefore never reaped when it becomes a corpse or over-lifetime straggler. No registry-coverage test catches this drift.

With the current topology (Cursor E = Loyal Opposition, the active headless reviewer), this is the unattended-safety hole: orphaned Cursor worker families would accumulate uncollected, and a future harness added without updating the watchdog would silently regress the same way.

## Problem detail (for LO review)

- `harness_storm_watchdog.ps1:56` — `$NONCODEX_HARNESS_SCRIPTS = @('ollama_harness.py', 'openrouter_harness.py')`; `cursor_harness.py` is absent.
- The gather (lines 80-86) requires `$invokesWatchedHarness` (command line matches `$NONCODEX_HARNESS_SCRIPT_PATTERN`, derived from that list) AND `$isProjectHarness`. cursor_harness.py fails the first predicate, so it is excluded from `$candidates` entirely.
- The dispatched-flag assignment (lines 104-111) marks non-codex harness python as `dispatched=$true`, but only for already-gathered candidates — so it never reaches cursor_harness.py.
- The harness registry (`harness-registry.json`) carries E (cursor) with `can_receive_dispatch` and headless argv `groundtruth-kb/.venv/Scripts/python.exe scripts/cursor_harness.py ...` — confirming cursor is a dispatch-capable non-codex python harness the watchdog must cover.
- The pure-decision module (`storm_watchdog_reap.py`) is harness-agnostic — it consumes the `dispatched` flag — so no change is needed there. The gap is purely the watched-script set and the absence of a parity test.

## Proposed change

1. `scripts/ops/harness_storm_watchdog.ps1`: add `'cursor_harness.py'` to `$NONCODEX_HARNESS_SCRIPTS` so dispatched Cursor workers are gathered and classified as dispatched roots (eligible for corpse/straggler reaping under the same liveness rules as ollama/openrouter).
2. `platform_tests/scripts/test_storm_watchdog_reap.py`: add a registry-coverage parity test that (a) parses `$NONCODEX_HARNESS_SCRIPTS` from the .ps1 and (b) derives the expected set of non-codex python harness scripts from `harness-registry.json` (each dispatch-capable harness whose headless argv invokes a `scripts/*_harness.py`), and asserts the watchdog set covers the registry set. This test fails for the cursor gap before the fix and guards against the same drift for any future harness.

No change to the pure decider or its existing unit tests; the fix is the watched-set entry plus the parity guard.

## Specification Links

- `ADR-DISPATCHER-ARCHITECTURE-001` — dispatcher architecture-of-record; the storm-watchdog is the dispatch-reliability reaper this fix keeps complete across harnesses.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the registry-coverage parity test makes the watchdog's harness set derive from the canonical registry rather than a hand-maintained list that drifts.
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` — the harness registry is the source of truth for dispatch-capable harnesses; the parity test reads it as the canonical coverage source.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority; filed as the next numbered bridge file (`bridge/gtkb-wi4818-storm-watchdog-cursor-coverage-001.md`) in the append-only versioned bridge chain, with no prior version rewritten.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied: cites all governing specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied: Project / Work Item / Project Authorization metadata present.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied: spec-to-test mapping below.
- `GOV-STANDING-BACKLOG-001` — WI-4818 is the governing backlog item.

## Prior Deliberations

- `DELIB-20266135` — this session's owner decision to draft/file WI-4818 and authorize the bounded envelope.
- `DELIB-20266104` — owner authorization of the surgical storm-watchdog liveness-awareness reaper this fix extends to the Cursor harness.
- `DELIB-20265899` — owner authorization of ADR-DISPATCHER-ARCHITECTURE-001, the dispatcher architecture this reaper serves.
- `DELIB-20266132` / `DELIB-20266133` — dispatcher work re-scope / re-home to PROJECT-GTKB-DISPATCHER-RELIABILITY.

## Owner Decisions / Input

- Owner directive this session (2026-06-25): after filing the control-plane eligibility fix, owner directed staging the WI-4818 proposal next ("WI-4818 proposal"). Recorded as `DELIB-20266135`, which also authorizes the bounded WI-4818 envelope (`PAUTH-WI-4818-STORM-WATCHDOG-CURSOR-COVERAGE`, source + test).
- Owner directive (2026-06-25): topology Claude(B)=Prime Builder, Cursor(E)=Loyal Opposition; Codex(A) and Antigravity(C) unavailable today. Cursor (E) reviews this proposal as Loyal Opposition.
- No further owner decision is required; the fix changes no runtime dispatch behavior on its own (it extends corpse-reaping coverage to one more harness and adds a guard test).

## Requirement Sufficiency

Existing requirements sufficient — `ADR-DISPATCHER-ARCHITECTURE-001` + `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` fully constrain the fix (the watchdog must cover every dispatch-capable harness the registry declares). No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| DCL-HARNESS-STATE-SOT-READER-CONTRACT-001 (registry is coverage source) | `test_watchdog_covers_all_registry_python_harnesses` (new) | The set of `*_harness.py` scripts in the .ps1 `$NONCODEX_HARNESS_SCRIPTS` covers every dispatch-capable non-codex python harness script declared in `harness-registry.json`; includes `cursor_harness.py`. |
| ADR-DISPATCHER-ARCHITECTURE-001 (watchdog covers dispatched workers) | same test, pre-fix behavior | Before adding cursor, the parity check reports cursor_harness.py as an uncovered registry harness (drift detected); after, it passes. |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (no silent drift) | same test | A future dispatch-capable python harness absent from the watchdog set fails the parity test (drift guard). |
| No-regression | existing `test_storm_watchdog_reap.py` decider unit tests; `ruff check` / `ruff format --check` on the changed test; PowerShell list-edit parse smoke (no syntax error) | green |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_storm_watchdog_reap.py -q --tb=short`; `ruff check <changed .py>`; `ruff format --check <changed .py>`.

## Risk / Rollback

- Risk: low. Adding one entry to the watched-script set only widens corpse/straggler reaping to dispatched Cursor workers, under the exact liveness rules already proven for ollama/openrouter (lease-aware, lifetime-bounded, never reaps healthy in-flight lease-holders or interactive sessions). It cannot reap an interactive Cursor IDE session because that is not a `cursor_harness.py` python dispatch process.
- Rollback: revert the one-line list change and remove the parity test; prior behavior returns. No schema change; append-only KB untouched.
- Out of scope: pid-provenance precise orphan attribution (separate follow-on), claude.exe headless coverage (separate concern; if the parity test surfaces it, captured as a finding), the reviewer-layer 600s timeouts, and the daemon cutover.
