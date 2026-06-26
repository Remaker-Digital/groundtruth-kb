NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: e6490e91-a7fd-489d-be63-363714e9ba47
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

bridge_kind: implementation_report
Document: gtkb-wi4818-storm-watchdog-cursor-coverage
Version: 005
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Responds-To: bridge/gtkb-wi4818-storm-watchdog-cursor-coverage-004.md (GO)
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4818
Project Authorization: PAUTH-WI-4818-STORM-WATCHDOG-CURSOR-COVERAGE
Recommended commit type: fix

## Implementation Report

Implemented per the GO (-004; supersedes -001 test-module scope) within the authorized target_paths. Changes are staged in the working tree (uncommitted) for Loyal Opposition inspection; per the protocol the VERIFIED finalization helper creates the commit with the verified paths plus the verdict.

## Files Changed

- scripts/ops/harness_storm_watchdog.ps1: added 'cursor_harness.py' to $NONCODEX_HARNESS_SCRIPTS (line 56), so dispatched Cursor workers (scripts/cursor_harness.py) are gathered and classified as dispatched roots, eligible for corpse/straggler reaping under the existing lease/liveness rules (WI-4828). One-line additive list change; no decider change.
- platform_tests/scripts/test_harness_storm_watchdog.py:
  - test_watchdog_detects_ollama_and_openrouter_backends: added `assert "cursor_harness.py" in text` so the watched-set presence check is explicit for all three python backends.
  - Replaced test_watchdog_covers_registry_lowcost_backends with test_watchdog_covers_registry_python_dispatch_harnesses: derives the expected python-dispatch *_harness.py set from ACTIVE registry harnesses whose headless argv invokes a scripts/*_harness.py backend (excludes codex/claude/gemini; does not filter on the low-cost tag or on can_receive_dispatch). Asserts the set is {ollama_harness.py, openrouter_harness.py, cursor_harness.py} and each is present in the watched-set text. The prior low-cost-only assertion (the root cause that let Cursor slip through) is retired, so no conflicting coverage definition remains.

No change to scripts/ops/storm_watchdog_reap.py or its decider unit tests (per the GO verdict).

## Specification Links

- ADR-DISPATCHER-ARCHITECTURE-001 (architecture_decision) — the storm-watchdog reaper now covers the Cursor python-dispatch harness.
- GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (governance) — the coverage test derives from the canonical registry, not a hand-maintained or low-cost-only list.
- DCL-HARNESS-STATE-SOT-READER-CONTRACT-001 (design_constraint) — the registry is the coverage source of truth; the parity test reads it.
- GOV-FILE-BRIDGE-AUTHORITY-001 (governance) — filed as the next append-only numbered bridge file (-005).
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (design_constraint) — all governing specs carried forward.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (design_constraint) — spec-to-test mapping with executed results below.
- GOV-STANDING-BACKLOG-001 (governance) — WI-4818 is the governing backlog item.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (architecture_decision) — durable artifact trail (thread, DELIB, PAUTH, tests).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (design_constraint) — work-item-to-test trigger honored.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (governance) — governed proposal/review/implement/verify cycle.

## Spec-to-Test Mapping (executed)

| Spec / clause | Test | Result |
|---|---|---|
| DCL-HARNESS-STATE-SOT-READER-CONTRACT-001 (registry is coverage source) | test_watchdog_covers_registry_python_dispatch_harnesses | PASS |
| ADR-DISPATCHER-ARCHITECTURE-001 (watchdog covers dispatched workers) | same test asserts cursor_harness.py in the watched-set text (would fail without the .ps1 change) | PASS |
| GOV-SOURCE-OF-TRUTH-FRESHNESS-001 (no silent drift) | same test fails if a future active python harness is absent from the watched-set | PASS |
| watched-set presence | test_watchdog_detects_ollama_and_openrouter_backends (now includes cursor) | PASS |
| No-regression | test_storm_watchdog_reap.py decider unit tests (10) + remaining watchdog tests | PASS |

## Commands + Results

- python -m pytest platform_tests/scripts/test_harness_storm_watchdog.py platform_tests/scripts/test_storm_watchdog_reap.py -q --tb=short -> 17 passed in 0.29s (exit 0)
- python -m ruff check platform_tests/scripts/test_harness_storm_watchdog.py -> All checks passed! (exit 0)
- python -m ruff format --check platform_tests/scripts/test_harness_storm_watchdog.py -> 1 file already formatted (exit 0)

## Requirement Sufficiency

Existing requirements sufficient — ADR-DISPATCHER-ARCHITECTURE-001 + DCL-HARNESS-STATE-SOT-READER-CONTRACT-001 constrain the fix. No new or revised requirement.

## Prior Deliberations

- DELIB-20266135 — owner decision authorizing WI-4818 under the bounded PAUTH envelope.
- DELIB-20266104 — surgical liveness-aware storm-watchdog reaper this fix extends.
- DELIB-20265899 — ADR-DISPATCHER-ARCHITECTURE-001 authorization.
- bridge/gtkb-wi4818-storm-watchdog-cursor-coverage-002.md / -004.md — the GO verdicts whose guidance this implementation adopts.

## Owner Decisions / Input

- DELIB-20266135 (AskUserQuestion, 2026-06-25): owner authorized WI-4818 implementation under PAUTH-WI-4818-STORM-WATCHDOG-CURSOR-COVERAGE (source + test). The implementation stays within that source+test envelope.

## Recommended Commit Type

fix — repairs the watchdog's incomplete harness coverage (a reliability defect) with no new capability surface.

## Verification Request

Requesting VERIFIED. The two changed files are uncommitted in the working tree for Loyal Opposition inspection; the VERIFIED finalization helper should commit the verified path set (scripts/ops/harness_storm_watchdog.ps1, platform_tests/scripts/test_harness_storm_watchdog.py) plus the verdict.
