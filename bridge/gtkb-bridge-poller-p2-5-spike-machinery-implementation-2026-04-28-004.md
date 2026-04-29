GO

# Loyal Opposition Review - GTKB-BRIDGE-POLLER-P2.5 Spike Machinery Implementation REVISED-1

Reviewed: 2026-04-29
Subject: `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-003.md`
Scope: revised implementation proposal for P2.5 verification spike runner, fixtures, and tests
Verdict: GO

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P2.5 spike machinery in-root approval evidence"
```

Relevant results:

- `DELIB-1348`: prior Loyal Opposition NO-GO for the P2.5 verification spike.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`: owner clarification that the OLD poller halt was implementation-specific and that the verified smart poller is opt-out when functional.
- `DELIB-1353`: prior Loyal Opposition NO-GO for the P1 detector/parser/checkpoint design.
- GT-KB root migration deliberation context reinforces the in-root evidence boundary.

The immediate prior review is `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-002.md`.

## Claim

GO. REVISED-1 closes the two blockers from `-002`: disposable verification work now defaults under the validated GT-KB root, and live mode now requires machine-verifiable approval evidence before any live harness invocation.

## Evidence

- `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-003.md:21` moves the default disposable workspace inside the GT-KB host root.
- `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-003.md:26-45` defines the in-root layout under `.gtkb-state/bridge-poller/spikes/<run_id>/`.
- `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-003.md:47` resolves `<project_root>` through the P1 `resolve_project_root()` contract.
- `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-003.md:51-79` adds synthetic in-root tests and an out-of-root workspace rejection test.
- `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-003.md:94` adds required `--owner-approval-file` validation before live subprocess execution.
- `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-003.md:98-115` defines the approval-file schema.
- `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-003.md:122-153` makes live mode fail before real CLI calls when approval evidence is absent or invalid.

## Risk / Impact

Residual risk is implementation fidelity around path validation and subprocess test setup. The proposal no longer authorizes temp-directory default workspaces or post-hoc approval receipts as the first proof of owner approval.

## Implementation Constraints

- The approval file path must itself be validated as in-root before live execution. Out-of-root approval files should fail closed, just like out-of-root spike workspaces.
- Subprocess tests that execute `scripts/bridge_poller_verification_spike.py` from a synthetic root must invoke the real script path or set `cwd`/`PYTHONPATH` so the command actually reaches the implementation under test.
- `--run-live-harnesses` must remain opt-in and must perform all approval validation before any `claude` or `codex` subprocess call.
- The default mocked mode must not call real CLIs under any path.
- The spike report must preserve full stdout/stderr and per-command evidence; do not compress the verification record into summary-only output.
- P3 must not treat any harness/mode as write-capable unless the spike classifies it `WRITE_CAPABLE`.

## Decision Needed From Owner

None for implementation scoping. The live run itself remains gated on the validated approval file and on this machinery implementation reaching VERIFIED.
