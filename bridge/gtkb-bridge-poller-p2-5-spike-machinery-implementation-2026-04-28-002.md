NO-GO

# Loyal Opposition Review - GTKB-BRIDGE-POLLER-P2.5 Spike Machinery Implementation

Reviewed: 2026-04-29
Subject: `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-001.md`
Scope: implementation proposal for P2.5 verification spike runner, fixtures, and tests
Verdict: NO-GO

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P2.5 verification spike machinery implementation"
```

Relevant results:

- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`: owner clarification that the OLD poller halt was implementation-specific and that the verified smart poller is opt-out when functional.
- `DELIB-1348`: prior Loyal Opposition NO-GO for the P2.5 verification spike.
- `DELIB-1353`: prior Loyal Opposition NO-GO for the P1 detector/parser/checkpoint design.
- `DELIB-1351`: prior Loyal Opposition NO-GO for the P2 harness registry.

The immediate authorizing bridge review is `bridge/gtkb-bridge-poller-p2-5-verification-spike-004.md`.

## Claim

NO-GO. The spike machinery scope preserves the key opt-in live-run and mocked-default constraints, but the proposal routes the disposable verification repository to `${TMP}` by default. Under the active GT-KB root-boundary rule, this is still GT-KB verification work and must remain inside `E:\GT-KB`.

## Finding 1 - P1: disposable verification repo is outside the mandatory GT-KB root

### Claim

The spike runner must not create or verify its disposable repository under `${TMP}` as the default path.

### Evidence

- `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-001.md` section 1.3 sets the disposable repo default to `${TMP}/agent-red-bridge-poller-spike/`.
- The same section says the GT-KB project root resolver is not used because the disposable repo is intentionally not GT-KB-compliant.
- Section 5.2 says tests assert the disposable repo path is under `${TMP}` or pytest `tmp_path`.
- `.claude/rules/project-root-boundary.md:9-10` says no GT-KB artifact may be created, read as a live dependency, updated, verified, or required from outside `E:\GT-KB`.
- `.claude/rules/project-root-boundary.md:22` explicitly bars routing GT-KB implementation, verification, bridge, dashboard, harness, hook, skill, plugin-cache, role-record, lifecycle-guard, or knowledge-base work to temp-directory paths.
- `.claude/rules/project-root-boundary.md:30-31` says any proposal, review, implementation, or test that depends on a path outside the allowed roots is a NO-GO until revised to be root-contained.

### Risk / Impact

The disposable repo is not a production source artifact, but it is an active GT-KB verification workspace that seeds governance hooks, runs harness behavior tests, produces evidence, and gates P3 invoker decisions. Putting that workspace under `%TEMP%` creates an out-of-root live dependency/evidence surface and weakens cleanup, auditability, and reproducibility. It also contradicts the root-boundary correction already enforced in P1.

### Recommended Action

Revise the proposal so the default disposable workspace is under the validated GT-KB host root, for example:

```text
<project_root>/.gtkb-state/bridge-poller/spikes/<run_id>/disposable-repo/
<project_root>/.gtkb-state/bridge-poller/spikes/<run_id>/evidence/
```

The runner may still delete that directory by default after the run, and `--keep-disposable-repo` may preserve it for inspection, but the path must remain under `E:\GT-KB`.

For tests, use a synthetic GT-KB root under pytest `tmp_path` with `groundtruth.toml`, then create the disposable repo under that synthetic root. That mirrors the P1 synthetic-root testing pattern without adding a production temp-directory exception.

### Owner Decision Needed

No owner decision is needed. This is mandatory root-boundary enforcement.

## Finding 2 - P2: owner-approval gate must be machine-verifiable before live mode

### Claim

The implementation proposal should specify the exact approval-evidence input the runner checks before `--run-live-harnesses` executes.

### Evidence

- `bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-001.md` says owner approval was captured in S319: “I approve of the live run.”
- Section 2.2 says the runner writes `live-run-approval.json` when `--run-live-harnesses` is passed.
- The same section says the runner refuses to execute if owner-approval evidence is missing, but it does not define how the pre-existing approval evidence is supplied to the runner before the run.

### Risk / Impact

If approval evidence is only written after `--run-live-harnesses` starts, it is not a pre-execution gate. The runner needs a concrete machine-verifiable input before token-consuming execution begins, such as an approval file path, CLI argument, or committed bridge reference.

### Recommended Action

Revise live mode to require an explicit input before any live subprocess call, for example:

```text
--owner-approval-ref bridge/gtkb-bridge-poller-p2-5-spike-machinery-implementation-2026-04-28-003.md
```

or:

```text
--owner-approval-file <project_root>/.gtkb-state/bridge-poller/spikes/<run_id>/approval.json
```

The runner should validate the approval text, timestamp/source reference, estimated token cost acknowledgement, and run identifier before executing live CLIs. The generated `live-run-approval.json` can then be a copy/receipt of that validated input, not the first proof of approval.

### Owner Decision Needed

No new owner decision is needed if the existing S319 approval is encoded in a validated in-root approval artifact before live execution.

## Confirmed Non-Blockers

- Mocked-subprocess default mode is the right CI-safe default.
- `--run-live-harnesses` as an opt-in flag is necessary and should remain.
- The `WRITE_CAPABLE` / `REVIEW_ONLY` / `OUT_OF_SCOPE` classification matrix is the right P3 input contract.
- Minimized governance hooks are acceptable as hermetic fixtures if their protocol shape and deny exit-code semantics match the real hooks.
- The live run remains out of scope until this machinery implementation is VERIFIED.

## Required Revision

Revise `-001` into `-003` with:

1. In-root default disposable workspace and evidence paths under the validated GT-KB host root.
2. Tests that use a synthetic in-root GT-KB project rather than `${TMP}` as an accepted production-equivalent location.
3. A precise pre-execution approval-evidence mechanism for live mode, validated before any real CLI invocation.
4. Updated acceptance criteria proving no default or live-mode verification artifact is routed outside the selected in-root workspace.

Once revised, return the thread as `REVISED` for review.
