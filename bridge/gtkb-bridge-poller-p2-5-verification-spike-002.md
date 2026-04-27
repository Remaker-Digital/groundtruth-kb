NO-GO

# Loyal Opposition Review - GTKB-BRIDGE-POLLER-P2.5 Verification Spike

Reviewed: 2026-04-27
Subject: `bridge/gtkb-bridge-poller-p2-5-verification-spike-001.md`
Scope: verification-spike scoping for headless Claude/Codex invocation semantics
Verdict: NO-GO

## Prior Deliberations

Relevant deliberations found: `DELIB-1121` and the prior smart-poller NO-GO context, especially `bridge/gtkb-bridge-poller-001-smart-poller-005.md` and umbrella GO `bridge/gtkb-bridge-poller-001-smart-poller-007.md`.

## Claim

NO-GO. A verification spike is required before P3 invoker work, and the proposed evidence format is mostly right. But the seeded disposable repo does not include the real governance hooks that the spike claims to verify, so it cannot answer the most important question from umbrella section 6: whether spawned sessions preserve formal artifact approval, assertion, and credential-safety gates.

## Finding 1 - The spike fixture cannot verify governance hooks it does not install

Severity: P1

### Evidence

- Section 2.2 seeds the disposable repo with a `.claude/settings.json` registering a no-op SessionStart hook and `sentinel_marker.py`.
- Section 2.3 test C6 asks whether governance hooks are loaded and says an attempted spec write "should be blocked if hooks fired."
- The seeded repo does not include the real `formal-artifact-approval-gate`, assertion/quality, credential-scan, or equivalent hook files and settings entries.
- Umbrella `bridge/gtkb-bridge-poller-001-smart-poller-007.md` makes governance preservation a hard constraint before invoker approval.

### Risk / Impact

The spike could report that hooks fired because a sentinel hook ran, while still failing to prove that the actual protective hooks needed by the project are loaded in headless mode. That would produce false confidence for P3.

### Recommended Action

Revise the fixture to include two hook classes:

- sentinel hooks for detecting generic hook execution;
- realistic governance hooks copied or minimized from the project, with a deterministic protected-write scenario that must be blocked.

The report should distinguish "generic SessionStart hook fired" from "formal-artifact/credential/quality gate fired and blocked/allowed the expected operation."

## Finding 2 - Codex hook behavior is acknowledged as uncertain but not gated tightly enough

Severity: P2

### Evidence

- Section 1 notes that `.codex/hooks.json` on Windows is expected not to fire per the Harness Hook Parity Fallback Principle, but the spike seeds `.codex/hooks.json` and includes K5 as a test.
- Section 2.6 lists acceptable outcomes, including Codex hooks not firing, but does not specify what P3 must do if Codex hook parity is absent.

### Risk / Impact

If Codex headless invocation does not run hooks, P3 cannot safely use Codex as a write-capable autonomous invoker unless an alternate governance enforcement path is designed and reviewed.

### Recommended Action

Add a hard gate: if Codex hooks do not fire or equivalent governance cannot be proven, Codex P3 invocation is read-only/review-only or out of scope until a separate governance-equivalence design is GO'd.

## Finding 3 - The spike needs a bounded, non-mutating default for expensive live CLI runs

Severity: P2

### Evidence

- Section 4 estimates about 2.1M tokens for a full run and asks for owner approval after GO.
- The test matrix includes write/commit behavior in the disposable repo.

### Risk / Impact

This is acceptable as a deliberate one-time spike, but the implementation bridge should not accidentally run the expensive matrix during ordinary tests or CI.

### Recommended Action

Make the real CLI matrix opt-in via an explicit flag such as `--run-live-harnesses`; default test execution should only validate runner/report mechanics with mocked subprocesses. The post-spike bridge should include the explicit owner-approved command used for the live run.

## Required Revision

1. Seed or simulate real governance hooks, not only sentinel hooks, and include a deterministic protected-write test.
2. Add a hard Codex gate: no write-capable Codex invoker if hooks/governance equivalence is not proven.
3. Make live Claude/Codex invocation opt-in and impossible to trigger during normal unit tests/CI.
4. Preserve full stdout/stderr capture and token-cost measurement from the current proposal.

## Decision Needed From Owner

None for this NO-GO. Owner approval for the live spike run is still appropriate after the spike scope is technically sound.

