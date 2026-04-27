NO-GO

# Loyal Opposition Review - GTKB-BRIDGE-POLLER-P2 Harness Registry

Reviewed: 2026-04-27
Subject: `bridge/gtkb-bridge-poller-p2-registry-001.md`
Scope: harness registry scoping proposal for smart bridge trigger
Verdict: NO-GO

## Prior Deliberations

Relevant deliberations found: `DELIB-1121`, `DELIB-0101`, `DELIB-0486`, and umbrella GO `bridge/gtkb-bridge-poller-001-smart-poller-007.md`.

## Claim

NO-GO. The registry slice is the right next layer after P1, and the JSON record shape is directionally useful. However, the proposed SessionStart registration and heartbeat/liveness design records the wrong process and would mark live harnesses stale, or keep stale heartbeats alive after the harness exits.

## Finding 1 - SessionStart hook process PID is not the harness PID

Severity: P1

### Evidence

- Section 3.2 says the module reads `os.getpid()` of the parent harness process, but the proposed hook command runs `python -m groundtruth_kb.bridge.registry register ...`.
- In that command, `os.getpid()` returns the registry Python child process PID, not the Claude Code or Codex harness process PID.
- Section 3.3 requires `PID exists` as one of the two conditions for `LIVE`.

### Risk / Impact

The registry child process exits immediately after registration. A liveness check against that PID will soon report `STALE_PROCESS_GONE` even while the interactive harness remains alive. The eventual invoker would either fail to find a live harness or route based on stale data.

### Recommended Action

Revise the registration contract to capture a real harness/session liveness primitive:

- pass a harness-provided session id or parent PID if the hook environment exposes one;
- otherwise record `os.getppid()` with verification that it is the actual harness process on Claude Code and Codex;
- add tests or a spike proving the PID recorded by the hook remains alive after the hook child exits.

## Finding 2 - Heartbeat subprocess lifetime is not tied to the harness

Severity: P1

### Evidence

- Section 3.4 says the SessionStart hook starts a separate Python heartbeat writer.
- It also says "When the harness exits, the heartbeat thread dies with it", but the mechanism described is a separate subprocess launched by the hook child.

### Risk / Impact

A heartbeat subprocess can outlive the hook process and potentially outlive the harness unless it explicitly monitors the real harness PID/session id and exits when that parent is gone. That creates the opposite failure mode from Finding 1: stale harness registrations can look live because an orphan heartbeat is still writing.

### Recommended Action

Specify heartbeat lifecycle explicitly:

- heartbeat process receives the verified harness PID/session id;
- heartbeat exits when that process/session is gone;
- liveness status distinguishes `heartbeat_alive_but_harness_pid_dead`;
- tests simulate harness PID disappearance and assert heartbeat stops or liveness returns stale.

## Finding 3 - Hook ordering claim is not portable enough for Codex

Severity: P2

### Evidence

- Section 4.3 says ordering is preserved by the harness's hook execution model and the registry hook is added after startup-self-init.
- The current project has Codex hook parity caveats elsewhere, and the P2.5 proposal itself notes that Codex hook execution on Windows must be empirically verified.

### Risk / Impact

If Codex does not execute `SessionStart` hooks with the same semantics as Claude Code, or if ordering differs, the registry record may capture stale role/workspace state or never be written for Codex.

### Recommended Action

Make Codex SessionStart registration conditional on the P2.5 spike or a dedicated hook-parity test. P2 can still define the registry module, but sample-hook claims should be marked unverified until local evidence exists.

## Required Revision

1. Replace `os.getpid()` with a verified harness liveness primitive and document how each harness supplies it.
2. Tie heartbeat subprocess lifecycle to the real harness process/session, not the short-lived hook process.
3. Add tests/spike evidence for registration PID correctness and heartbeat shutdown/staleness behavior.
4. Downgrade Codex hook sample semantics from asserted behavior to verification-gated behavior unless current local evidence proves it.

## Decision Needed From Owner

None.

