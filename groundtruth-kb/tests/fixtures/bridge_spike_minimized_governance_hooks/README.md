# Minimized Governance Hooks — Spike Fixtures

These hooks are **minimized ports** of the project's real governance hooks,
seeded into the disposable repo created by
`scripts/bridge_poller_verification_spike.py` to test whether Claude Code
and Codex headless modes load and execute hooks per the Claude Code hook
protocol.

Per design `bridge/gtkb-bridge-poller-p2-5-verification-spike-003.md`
section 2.2, the fixture seeds **two hook classes**:

1. **Generic sentinel** (`sentinel_marker.py`) — fires on `SessionStart`,
   writes `SENTINEL_HOOK_FIRED-{ts}` marker file. Tests whether ANY hook
   fires in a given harness × mode combination.
2. **Governance hooks** (`formal_artifact_approval_gate.py`,
   `credential_scan.py`) — minimized ports of the real project hooks.
   Test whether the **governance class** of hooks fires AND blocks the
   protected-write attempt (the F2 governance test from `-003 §2.4`).

## Relationship to real hooks

| Minimized port | Real hook | Preserved | Omitted |
|---|---|---|---|
| `formal_artifact_approval_gate.py` | `.claude/hooks/formal-artifact-approval-gate.py` | Trigger condition (writes to `protected-spec.json` are blocked); `exit(2)` deny semantics; sentinel marker emission | Project-specific KB integration; full approval-packet validation; manifest hashing |
| `credential_scan.py` | `.claude/hooks/credential-scan.py` | Trigger condition (`AR-[A-Z0-9]{8}` pattern in `tool_input.content`); deny semantics; sentinel marker | Full credential pattern set; quarantine logic |
| `sentinel_marker.py` | (no real-hook analog) | n/a | n/a — purely a "did SessionStart fire at all?" marker |

## Sentinel markers

Each hook writes its own sentinel file at the spike's evidence directory
when triggered:

- `SENTINEL_HOOK_FIRED-<ts>` — generic SessionStart hook fired (any mode)
- `SENTINEL_GOV_HOOK_FIRED-<ts>` — formal-artifact gate fired
- `SENTINEL_CRED_HOOK_FIRED-<ts>` — credential-scan hook fired

The spike runner's findings derivation distinguishes:

- **F1 (Generic SessionStart hook semantics):** did `SENTINEL_HOOK_FIRED` appear?
- **F2 (Governance hook semantics):** did `SENTINEL_GOV_HOOK_FIRED` appear AND was `protected-spec.json` content unchanged after the modify-attempt test?

## Why minimized vs. real hooks

The disposable repo is a hermetic test environment. Real hooks have
project-specific dependencies (KB API, approval-packet schema, manifest
generation) that would either:

- Pull in the entire project (defeating hermetic isolation), or
- Fail in unexpected ways inside the disposable repo (false-negative on
  hook-firing).

Minimized hooks share the **protocol shape** (stdin JSON in, JSON decision
out, deny via `exit(2)`) and **trigger semantics** (blocking writes to
specific protected paths) without the full project integration. This lets
the spike answer "did the hook protocol load correctly in this harness ×
mode?" without confounding the answer with unrelated dependency failures.

## Drift management

These fixtures are **not** auto-synchronized with the real hooks. If the
real hooks' trigger conditions or exit-code semantics change in a way that
matters for spike validity, the fixtures must be updated by hand. A
follow-on bridge thread may add a release-candidate-gate test that asserts
the fixtures' protocol shape still matches the real hooks'; this is out of
P2.5 scope.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
