NO-GO

# Loyal Opposition Review - GTKB-BRIDGE-POLLER-P2 Registry Implementation

Reviewed: 2026-04-29
Subject: `bridge/gtkb-bridge-poller-p2-registry-implementation-2026-04-28-001.md`
Scope: implementation proposal for P2 static harness registry slice
Verdict: NO-GO

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P2 registry implementation static registry smart poller"
```

Relevant results:

- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`: owner clarification that the OLD poller halt was implementation-specific and that the verified smart poller is opt-out when functional.
- `DELIB-1351`: prior Loyal Opposition NO-GO for P2 harness registry.
- `DELIB-1350`: prior Loyal Opposition NO-GO for P2 registry revised design.
- External poller liveness watcher deliberations are relevant background for why P2 remains static-only.

The immediate authorizing bridge review is `bridge/gtkb-bridge-poller-p2-registry-006.md`, which GO'd the static-record-only P2 registry scope.

## Claim

NO-GO. The static-only registry scope is directionally correct and consumes the P1 path contract appropriately, but the implementation proposal has two execution-contract defects that would make the samples or CLI ambiguous at implementation time.

## Finding 1 - P1: CLI module and hook invocation are inconsistent

### Claim

The proposal must specify one executable module path for registration and align source files, samples, and tests to that path.

### Evidence

- `bridge/gtkb-bridge-poller-p2-registry-implementation-2026-04-28-001.md` section 1.1 says to add `registry_cli.py`.
- The same section describes that file as the entry point for `python -m groundtruth_kb.bridge.registry register --harness-kind <claude-code|codex>`.
- `bridge/gtkb-bridge-poller-p2-registry-005.md` section 3.2 shows SessionStart samples invoking `python -m groundtruth_kb.bridge.registry register --harness-kind ...`.
- If the CLI lives in `registry_cli.py`, the direct module command would normally be `python -m groundtruth_kb.bridge.registry_cli ...`; if the command is `python -m groundtruth_kb.bridge.registry ...`, then `registry.py` must own the `if __name__ == "__main__"` / argument parser surface.

### Risk / Impact

The hook samples are the primary consumer of this slice. If the CLI surface is ambiguous, Prime can implement a registry module that passes unit tests but leaves the shipped SessionStart samples calling a module without a command entry point. That would make registration silently unavailable at startup.

### Recommended Action

Revise the proposal to choose one of these options:

1. Put the CLI in `registry.py` and keep hook commands as `python -m groundtruth_kb.bridge.registry register --harness-kind ...`.
2. Put the CLI in `registry_cli.py` and change all samples/tests to `python -m groundtruth_kb.bridge.registry_cli register --harness-kind ...`.

Add a test that runs the selected module command through `subprocess.run(..., check=True)` against a synthetic GT-KB root so the sample command is proven executable, not just present in JSON.

### Owner Decision Needed

No owner decision is needed.

## Finding 2 - P2: verification-gated “header” conflicts with JSON hook samples unless represented validly

### Claim

The Codex sample must remain valid JSON while carrying the required verification-gated warning.

### Evidence

- `bridge/gtkb-bridge-poller-p2-registry-implementation-2026-04-28-001.md` section 1.1 proposes `samples/codex/.codex/hooks-bridge-poller.json`.
- Section 4 acceptance criterion 9 says the Codex hook sample carries the verification-gated header.
- `bridge/gtkb-bridge-poller-p2-registry-005.md` section 4.2 says the Codex sample ships with a `# WARNING: ...` header comment.
- Live `.codex/hooks.json` in this checkout is strict JSON, not a comment-tolerant format.

### Risk / Impact

JSON does not allow `#` header comments. If the implementation places a literal warning header in a `.json` sample, the sample becomes invalid and cannot safely be copied or parsed as hook configuration. If the implementation omits the warning, it violates the GO condition that Codex hook samples remain verification-gated on Windows.

### Recommended Action

Revise the proposal to encode the warning without breaking JSON. Acceptable options include:

1. Add a top-level metadata field such as `_verification_warning` or `_comment` inside the JSON sample, and test both `json.loads()` and presence of the warning text.
2. Keep the hook sample as strict JSON and add a sibling `README.md` or `.md` note carrying the warning, with tests verifying both the JSON sample and warning artifact exist.

Do not implement a `.json` file with `#` comments unless the consumer is explicitly proven to accept JSONC-like syntax, which is not established here.

### Owner Decision Needed

No owner decision is needed.

## Confirmed Non-Blockers

- `<state_dir>/registry/<harness_id>.json` is a sound storage location because it reuses the P1 in-root state contract.
- Static-only scope correctly preserves the P2 design GO: no heartbeat, no live/stale classification, no process-name allowlist, and no `psutil`.
- `recording_pid` / `recording_ppid` are acceptable diagnostic fields as long as code and docs never describe either as the harness PID.
- `since_days=7` can ship as a default convenience filter without a separate owner decision.
- Tests should live under `groundtruth-kb/tests/`, matching the P1 package-native convention.

## Required Revision

Revise `-001` into `-003` with:

1. A single selected CLI module path, aligned across source layout, hook samples, and tests.
2. A subprocess test proving the selected `python -m ... register --harness-kind ...` command works.
3. A valid-JSON Codex hook sample strategy that preserves the verification-gated warning without illegal comments.
4. Tests that parse the sample JSON and verify the warning surface.

Once revised, return the thread as `REVISED` for review.
