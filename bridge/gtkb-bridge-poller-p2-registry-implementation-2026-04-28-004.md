GO

# Loyal Opposition Review - GTKB-BRIDGE-POLLER-P2 Registry Implementation REVISED-1

Reviewed: 2026-04-29
Subject: `bridge/gtkb-bridge-poller-p2-registry-implementation-2026-04-28-003.md`
Scope: revised implementation proposal for P2 static harness registry slice
Verdict: GO

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P2 registry implementation CLI JSON hook sample"
```

Relevant results:

- `DELIB-1351`: prior Loyal Opposition NO-GO for P2 harness registry.
- `DELIB-1350`: prior Loyal Opposition NO-GO for P2 registry revised design.
- Bridge operational deliberations remain relevant background for static-only registry scope.

The immediate prior review is `bridge/gtkb-bridge-poller-p2-registry-implementation-2026-04-28-002.md`.

## Claim

GO. REVISED-1 resolves the two execution-contract blockers from `-002`: it selects one CLI module path and preserves a valid-JSON Codex hook sample while carrying the verification warning.

## Evidence

- `bridge/gtkb-bridge-poller-p2-registry-implementation-2026-04-28-003.md:21` drops `registry_cli.py` and puts the CLI in `registry.py`.
- `bridge/gtkb-bridge-poller-p2-registry-implementation-2026-04-28-003.md:31-64` adds a subprocess test for `python -m groundtruth_kb.bridge.registry register --harness-kind claude-code`.
- `bridge/gtkb-bridge-poller-p2-registry-implementation-2026-04-28-003.md:78-90` makes the Codex hook sample strict JSON with `_verification_warning` and `_verification_warning_adr_ref`.
- `bridge/gtkb-bridge-poller-p2-registry-implementation-2026-04-28-003.md:116-136` updates the acceptance criterion/tests to parse JSON and verify the warning and command string.

## Risk / Impact

Residual risk is implementation fidelity. The static-only registry scope still avoids liveness claims, heartbeat behavior, `psutil`, and process-name allowlists. The selected CLI path now matches the sample commands.

## Implementation Constraints

- The subprocess test must prove the exact command used in samples works:

```text
python -m groundtruth_kb.bridge.registry register --harness-kind claude-code
```

- If the subprocess test depends on an editable/package install rather than `PYTHONPATH`, the test/report should state that assumption clearly.
- The Codex sample must remain valid JSON. If implementation or schema testing shows top-level `_verification_warning` fields are rejected by the actual Codex hook loader, move the warning to a sibling README/metadata file and keep the active JSON sample schema-clean.
- Code and docs must not describe `recording_pid` or `recording_ppid` as a harness PID.
- P2 consumers must not treat registry records as live/stale authoritative.

## Decision Needed From Owner

None.
