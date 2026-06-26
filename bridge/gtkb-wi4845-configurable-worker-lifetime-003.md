NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: e6490e91-a7fd-489d-be63-363714e9ba47
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: Claude Code interactive Prime Builder (::init gtkb pb)

bridge_kind: implementation_report
Document: gtkb-wi4845-configurable-worker-lifetime
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-26 UTC
Responds-To: bridge/gtkb-wi4845-configurable-worker-lifetime-002.md (GO)
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4845
Project Authorization: PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4845-CONFIGURABLE-WORKER-LIFETIME-CAP
Recommended commit type: fix

## Implementation Report

Implemented per the GO (-002, "Implement per -001 scope and verification plan") within the authorized target_paths. Changes are staged in the working tree (uncommitted) for Loyal Opposition inspection; the VERIFIED finalization helper creates the commit with the verified paths plus the verdict.

## Files Changed

- scripts/run_with_status.py: added a `_parse_lifetime` validator and a `--lifetime <seconds>` argument to the leading flag-parse loop (alongside --stdin/--stdout/--stderr). When --lifetime is absent the existing module default DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS (600) applies, preserving current behavior and the test monkeypatch surface; the parsed value drives p.wait(timeout=...) and the lifetime-timeout message. A non-positive or non-numeric value fails closed (exit 2). Incidental hygiene to keep the changed file ruff-clean: 3 targeted `# noqa: SIM115` on the cross-block stdin/stdout/stderr file handles (a legitimate pattern SIM115 mis-flags -- the handles must outlive a single `with` block and are closed in the `finally`), and removal of one pre-existing UP015 unnecessary "r" mode argument. These ruff findings predate WI-4845.
- scripts/cross_harness_bridge_trigger.py: added the module constant LO_REVIEW_WORKER_LIFETIME_SECONDS (1800) and an importable helper worker_lifetime_seconds(role_label) returning 1800 for "loyal-opposition" and None otherwise; wired it into the spawn wrapped_command so a Loyal Opposition / verification dispatch gets `--lifetime 1800` and every other role keeps run_with_status.py's default (no override passed). Additive; non-LO dispatch behavior is unchanged.
- platform_tests/scripts/test_run_with_status.py: added the four spec-derived tests.

The 80-turn ceiling (DEFAULT_MAX_TURNS), the 240s per-HTTP-call timeout, the WI-4828 lease/liveness storm-watchdog, and the WI-4472 concurrency cap are unchanged, so the longer LO lifetime does not re-open the storm.

## Specification Links

- ADR-DISPATCHER-ARCHITECTURE-001 (architecture_decision) — dispatch-substrate parameterization; the lifetime cap becomes a parameter the daemon can later own.
- SPEC-CENTRALIZED-DISPATCH-SERVICE-001 (requirement) — reliable verdict production; LO reviews can now complete within budget.
- DCL-DISPATCH-ENVELOPE-RULES-001 (design_constraint) — the lifetime stays bounded (default 600; LO 1800), never removed.
- GOV-FILE-BRIDGE-AUTHORITY-001 (governance) — filed as the next append-only numbered bridge file (-003).
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 (design_constraint) — spec-to-test mapping with executed results below.
- GOV-RELIABILITY-FAST-LANE-001 (governance) — reliability-defect context; followed the full bridge protocol.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 (design_constraint) — all governing specs carried forward.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 (architecture_decision) — durable artifact trail (thread, DELIB-20266136, PAUTH, tests).
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 (design_constraint) — work-item-to-test trigger honored.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 (governance) — governed proposal/review/implement/verify cycle.

## Spec-to-Test Mapping (executed)

| Spec / clause | Test | Result |
|---|---|---|
| SPEC-CENTRALIZED-DISPATCH-SERVICE-001 (--lifetime applied as wait timeout) | test_lifetime_arg_sets_wait_timeout | PASS |
| DCL-DISPATCH-ENVELOPE-RULES-001 (bounded default preserved) | test_default_lifetime_preserved_when_absent | PASS |
| ADR-DISPATCHER-ARCHITECTURE-001 (substrate parameter validated, fail-closed) | test_lifetime_rejects_nonpositive | PASS |
| SPEC-CENTRALIZED-DISPATCH-SERVICE-001 (LO budget routing) | test_dispatch_lo_gets_review_lifetime | PASS |
| No-regression | test_run_with_status.py (5 existing) + test_cross_harness_bridge_trigger.py (99 passed) | PASS (no new regression) |

## Commands + Results

- python -m pytest platform_tests/scripts/test_run_with_status.py -q -> 9 passed in 1.64s (exit 0)
- python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q -> 1 failed, 99 passed in 7.90s. The single failure, test_prime_spawn_creates_dispatch_authorization_packet_and_env (assert at line 1233), is PRE-EXISTING and unrelated to this change: it is a prime-spawn test, and this change is loyal-opposition-only (prime resolves worker_lifetime_seconds to None, leaving the prime wrapped_command identical). Confirmed by stashing only scripts/cross_harness_bridge_trigger.py and re-running the test -- it fails identically (same line 1233) without this change.
- python -m ruff check scripts/run_with_status.py scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_run_with_status.py -> All checks passed! (exit 0)
- python -m ruff format --check (same 3 files) -> 3 files already formatted (exit 0)

## Requirement Sufficiency

Existing requirements sufficient — SPEC-CENTRALIZED-DISPATCH-SERVICE-001, ADR-DISPATCHER-ARCHITECTURE-001, DCL-DISPATCH-ENVELOPE-RULES-001, and the WI-4806 deferred-configurability intent constrain the fix. No new or revised requirement.

## Prior Deliberations

- DELIB-20266136 — owner decision authorizing this fix (configurable cap + LO budget), AUQ 2026-06-25.
- DELIB-20266132 — WI-4670 re-scope/close that forked the cloud-LO-completion residual into WI-4845.
- bridge/gtkb-run-with-status-worker-lifetime-timeout-002.md — the WI-4806 thread that added the 600s cap and deferred configurability; this realizes that deferred work.
- bridge/gtkb-wi4845-configurable-worker-lifetime-002.md — the GO whose scope/verification plan this implementation follows.

## Owner Decisions / Input

- DELIB-20266136 (AskUserQuestion, 2026-06-25): owner selected "Configurable cap + LO budget" for WI-4845, authorizing draft, cross-review, and implementation under PAUTH-PROJECT-GTKB-DISPATCHER-RELIABILITY-WI-4845-CONFIGURABLE-WORKER-LIFETIME-CAP (source + test).

## Recommended Commit Type

fix — repairs a dispatch-reliability defect (cloud LO workers killed mid-review by the hardcoded 600s cap) by making the cap configurable; no new product capability surface beyond the internal --lifetime parameter.

## Verification Request

Requesting VERIFIED. The three changed files are uncommitted in the working tree for Loyal Opposition inspection; the VERIFIED finalization helper should commit the verified path set (scripts/run_with_status.py, scripts/cross_harness_bridge_trigger.py, platform_tests/scripts/test_run_with_status.py) plus the verdict.
