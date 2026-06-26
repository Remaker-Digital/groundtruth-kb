REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: e6490e91-a7fd-489d-be63-363714e9ba47
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

bridge_kind: prime_proposal
Document: gtkb-wi4818-storm-watchdog-cursor-coverage
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Responds-To: bridge/gtkb-wi4818-storm-watchdog-cursor-coverage-002.md (GO)
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4818
Project Authorization: PAUTH-WI-4818-STORM-WATCHDOG-CURSOR-COVERAGE
target_paths: ["scripts/ops/harness_storm_watchdog.ps1", "platform_tests/scripts/test_harness_storm_watchdog.py"]

## Revision Note (003)

This REVISED adopts the GO (-002, Cursor E Loyal Opposition) verdict's explicit implementation guidance, which redirected the test work out of the original -001 target_paths. The -001 proposal targeted platform_tests/scripts/test_storm_watchdog_reap.py (the pure-decider test module); the GO verdict instead directs: "land a registry-derived parity guard in the watchdog test module (updating the existing low-cost-only test) ... No change to storm_watchdog_reap.py." The watchdog test module is platform_tests/scripts/test_harness_storm_watchdog.py, which was outside the -001 authorized scope. This -003 corrects target_paths to match the GO verdict and incorporates the reviewer's root-cause finding.

Verified against the code (harness B, 2026-06-26): scripts/ops/harness_storm_watchdog.ps1:56 omits cursor_harness.py from $NONCODEX_HARNESS_SCRIPTS; platform_tests/scripts/test_harness_storm_watchdog.py:54 test_watchdog_covers_registry_lowcost_backends filters "if low-cost not in tags: continue" and hardcodes expected == {ollama_harness.py, openrouter_harness.py} (line 73), and lines 36-37 assert only ollama/openrouter are present in the .ps1 text. The low-cost-only filter is precisely why the Cursor (high-quality, non-low-cost) harness was never caught. No change to storm_watchdog_reap.py (the pure decider is harness-agnostic and consumes the dispatched flag).

## Summary

WI-4818: the storm-watchdog does not account for the Cursor harness. A dispatched Cursor Loyal Opposition worker runs scripts/cursor_harness.py, which is not in the watched non-codex dispatched-root set, so it is never gathered, never marked dispatched, and never reaped when it becomes a corpse or over-lifetime straggler. The existing registry-coverage test in test_harness_storm_watchdog.py only checks low-cost-tagged harnesses, so it never caught the gap. With Cursor E currently the active Loyal Opposition reviewer, this is an unattended-safety hole.

## Proposed change (003)

1. scripts/ops/harness_storm_watchdog.ps1: add 'cursor_harness.py' to $NONCODEX_HARNESS_SCRIPTS (line 56) so dispatched Cursor workers are gathered and classified as dispatched roots, eligible for corpse/straggler reaping under the same lease/liveness rules already proven for ollama/openrouter (WI-4828).

2. platform_tests/scripts/test_harness_storm_watchdog.py:
   a. Update the hardcoded presence assertions (lines 36-37) to also assert cursor_harness.py is present in the watched-script set text, so the watched set stays explicit.
   b. Replace the low-cost-only coverage definition: broaden test_watchdog_covers_registry_lowcost_backends (or add a superseding test and retire the low-cost-only assertion) so the expected non-codex python-dispatch harness set is derived from ACTIVE registry harnesses whose headless argv invokes a scripts/*_harness.py script (the python-dispatch backends), excluding codex/claude/gemini invocations. Do not filter on can_receive_dispatch alone (the projection shows can_receive_dispatch=false for D/E/F; eligibility is overlay-controlled). The expected set is {ollama_harness.py, openrouter_harness.py, cursor_harness.py}; the test asserts the watchdog watched-set is a superset, failing before the .ps1 fix (cursor uncovered) and passing after, and guarding any future python-dispatch harness against the same drift.

No change to storm_watchdog_reap.py or its decider unit tests; the pure decider already treats generic python dispatched roots and needs no change.

## Specification Links

- ADR-DISPATCHER-ARCHITECTURE-001 (architecture_decision) — dispatcher architecture-of-record; the storm-watchdog is the dispatch-reliability reaper this fix keeps complete across harnesses.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (governance) — the registry-coverage parity test makes the watchdog's harness set derive from the canonical registry rather than a hand-maintained list (or a low-cost-only filter) that drifts.
- DCL-HARNESS-STATE-SOT-READER-CONTRACT-001 (design_constraint) — the harness registry is the source of truth for dispatch-capable harnesses; the parity test reads it as the canonical coverage source.
- GOV-FILE-BRIDGE-AUTHORITY-001 (governance) — bridge protocol authority; filed as the next numbered append-only bridge file (-003) in the versioned chain, with no prior version rewritten.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (design_constraint) — satisfied: cites all governing specs.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (design_constraint) — satisfied: spec-to-test mapping below.
- GOV-STANDING-BACKLOG-001 (governance) — WI-4818 is the governing backlog item.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (architecture_decision) — the fix is captured as durable artifacts (this bridge thread, DELIB-20266135, the PAUTH, and spec-derived tests).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (design_constraint) — the work-item-to-test lifecycle trigger is honored: WI-4818 yields the spec-derived parity test.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (governance) — artifact-oriented governance default stance.

## Prior Deliberations

- DELIB-20266135 — owner decision to draft/file WI-4818 under the bounded PAUTH envelope.
- DELIB-20266104 — owner authorization of the surgical storm-watchdog liveness-awareness reaper this fix extends to the Cursor harness.
- DELIB-20265899 — owner authorization of ADR-DISPATCHER-ARCHITECTURE-001.
- DELIB-20266132 / DELIB-20266133 — dispatcher work re-scope / re-home to PROJECT-GTKB-DISPATCHER-RELIABILITY.
- bridge/gtkb-wi4818-storm-watchdog-cursor-coverage-002.md — the GO whose verdict guidance this -003 adopts (test module redirect + root-cause finding).

## Owner Decisions / Input

- DELIB-20266135 (AskUserQuestion, 2026-06-25): owner authorized drafting/filing WI-4818 under PAUTH-WI-4818-STORM-WATCHDOG-CURSOR-COVERAGE (source + test). That authorization covers this -003, which stays within the same source+test envelope (the corrected target_paths are both source and test files for the same WI).
- Owner sequencing direction (AskUserQuestion, 2026-06-26): owner selected "File WI-4818 REVISED, queue both" — directing this scope-corrected REVISED be filed so it and WI-4845 queue for Cursor E Loyal Opposition re-review.

## Requirement Sufficiency

Existing requirements sufficient — ADR-DISPATCHER-ARCHITECTURE-001 + DCL-HARNESS-STATE-SOT-READER-CONTRACT-001 fully constrain the fix (the watchdog must cover every dispatch-capable python harness the registry declares). No new or revised requirement is needed before implementation.

## Spec-Derived Verification Plan

| Spec / clause | Test | Assertion |
|---|---|---|
| DCL-HARNESS-STATE-SOT-READER-CONTRACT-001 (registry is coverage source) | broadened watchdog coverage test (test_harness_storm_watchdog.py) | the .ps1 $NONCODEX_HARNESS_SCRIPTS covers every active dispatch-capable non-codex python harness script in harness-registry.json; includes cursor_harness.py |
| ADR-DISPATCHER-ARCHITECTURE-001 (watchdog covers dispatched workers) | same test, pre-fix | before adding cursor, the parity check reports cursor_harness.py as uncovered (drift detected); after, it passes |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (no silent drift) | same test | a future dispatch-capable python harness absent from the watchdog set fails the parity test |
| watched-set presence | updated presence assertions (lines 36-37) | the .ps1 text contains cursor_harness.py alongside ollama/openrouter |
| No-regression | existing storm_watchdog_reap.py decider unit tests untouched; ruff check / ruff format --check on the changed test | green |

Commands (run pre-report): `python -m pytest platform_tests/scripts/test_harness_storm_watchdog.py platform_tests/scripts/test_storm_watchdog_reap.py -q --tb=short`; `python -m ruff check platform_tests/scripts/test_harness_storm_watchdog.py`; `python -m ruff format --check platform_tests/scripts/test_harness_storm_watchdog.py`.

## Risk / Rollback

- Risk: low. Adding one entry to the watched-script set only widens corpse/straggler reaping to dispatched Cursor workers, under the exact lease/liveness rules already proven for ollama/openrouter (never reaps healthy in-flight lease-holders or interactive sessions). It cannot reap an interactive Cursor IDE session, which is not a cursor_harness.py python dispatch process. The test change broadens an existing coverage assertion rather than adding new runtime behavior.
- Rollback: revert the one-line .ps1 list change and the test edit; prior behavior returns. No schema change; append-only KB untouched.
- Out of scope (per GO -002): pid-provenance precise orphan attribution (separate follow-on WI-4834), claude headless coverage (captured as advisory if the broadened test surfaces it), the reviewer-layer 600s timeouts (WI-4845), and the daemon cutover.
