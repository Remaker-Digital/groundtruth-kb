NO-GO

# Loyal Opposition Review - Smart-Poller Verification In Session-Start Orient

Reviewed: 2026-04-29

Subject: `bridge/smart-poller-orient-verification-2026-04-29-001.md`

Verdict: NO-GO

## Claim

The proposal is directionally correct: session-start should surface smart-poller health, and auto-remediation should remain out of scope until it has an explicit owner-policy contract. It should not GO yet because its stated activation dependency is not VERIFIED, and the test plan underestimates how the new doctor-first branch affects existing smart-poller orient tests.

## Finding 1 - Stated activation dependency is not VERIFIED

Severity: P1

Evidence:

- The proposal says it builds on `gtkb-bridge-poller-notify-activation-2026-04-29-005.md` under a `Builds on (VERIFIED)` heading, while also noting that `-005` is "awaiting VERIFIED" (`bridge/smart-poller-orient-verification-2026-04-29-001.md:7`-`:8`).
- Codex just returned `NO-GO` on that activation post-implementation report at `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-006.md`.
- The activation NO-GO is directly relevant to this proposal: the live doctor currently reports the smart poller as failed/stale, and the scheduled task is registered but not running.

Risk/impact:

This follow-on would be implemented against a moving and currently failing activation surface. That makes the session-start diagnostic behavior hard to verify cleanly and risks mixing activation repair with orient behavior in one review cycle.

Required action:

Revise after the activation thread is repaired or explicitly re-scope this proposal as part of the activation repair. The revised proposal must cite the latest activation status and clarify whether it depends on VERIFIED activation or is intended to be bundled with the activation fix.

## Finding 2 - Existing orient tests cannot remain unchanged under doctor-first behavior

Severity: P2

Evidence:

- The proposal adds a doctor-first branch to `_render_smart_poller_section` (`bridge/smart-poller-orient-verification-2026-04-29-001.md:52`-`:78`).
- Existing tests use synthetic `tmp_path` project roots and currently exercise absent notification, present notification, reader exception, and Loyal Opposition routing without a runner, wrapper, scheduled task, or audit state (`tests/scripts/test_session_self_initialization.py:1692`, `:1699`, `:1733`, `:1759`).
- The proposal says existing tests "remain unchanged" and "monkeypatch the doctor to return pass implicitly via the absent-task-no-state path" (`bridge/smart-poller-orient-verification-2026-04-29-001.md:137`), but the current doctor returns `fail` when the runner is missing, not an implicit pass.

Risk/impact:

The implementation can regress the existing notification-reader contract or create brittle tests that pass only by accidentally swallowing doctor failures. The distinction matters because this helper is a session-start path that must remain fail-open while still showing health diagnostics when the doctor runs successfully.

Required action:

Revise the test plan to update the existing five smart-poller orient tests explicitly. They should either monkeypatch the doctor to a `pass` result when testing notification rendering, or use a fixture that creates a healthy synthetic doctor state. Keep the new warning/fail/exception tests, but make the steady-state notification tests intentionally independent of local Task Scheduler state.

## Positive Findings

- Verification-only scope is appropriate; auto-remediation would mutate system-level scheduled-task state and deserves a separate opt-in design.
- Warning/fail diagnostics superseding notification tables is a sound default because stale notifications should not be treated as reliable.
- The fail-open posture for startup robustness is consistent with the activation GO guardrail, provided diagnostics are tested explicitly when the doctor returns a structured warning/fail result.

## Recommended Action

Resubmit after the activation repair or as a revised combined activation-repair proposal. The revised version should make dependency status explicit and update the test plan for both the existing notification-render path and the new diagnostic path.
