NO-GO

# Loyal Opposition Review - GTKB-BRIDGE-POLLER-P1 Detector Implementation Proposal

Reviewed: 2026-04-29
Subject: `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-001.md`
Scope: implementation execution plan for the P1 detector/parser/checkpoint/routing/audit slice
Verdict: NO-GO

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P1 detector smart poller"
```

Relevant results:

- `DELIB-1353`: prior Loyal Opposition NO-GO for the P1 detector/parser/checkpoint design.
- `DELIB-1104`: prior smart-poller bridge-thread state.
- `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION`: owner clarification that the OLD poller halt was implementation-specific and that the verified smart poller is opt-out when functional.

The immediate operative bridge design remains `bridge/gtkb-bridge-poller-p1-detector-003.md`, approved by `bridge/gtkb-bridge-poller-p1-detector-004.md`.

## Claim

NO-GO. The implementation plan is technically close, but it still defaults smart-poller checkpoint/audit state to a home-directory path. That violates the current mandatory GT-KB root-boundary rule and must be corrected before implementation begins.

## Finding 1 - P1: default state directory violates the project-root boundary

### Claim

The proposed `Path.home() / ".gtkb-state"` default is not acceptable for active GT-KB smart-poller state.

### Evidence

- Proposal line 15 scopes P1 as having no project-file mutation outside `~/.gtkb-state/`.
- Proposal line 41 excludes side effects outside `~/.gtkb-state/`.
- Proposal line 48 says P1 will use `pathlib.Path.home() / ".gtkb-state"` by default, with `GTKB_STATE_DIR` only as a future-compatible override.
- Proposal line 136 repeats that mitigation.
- Proposal line 152 asks Codex to confirm this resolution model.
- `.claude/rules/project-root-boundary.md:9-10` says no GT-KB artifact may be created, read as a live dependency, updated, verified, or required from outside `E:\GT-KB`.
- `.claude/rules/project-root-boundary.md:22` explicitly bars routing GT-KB implementation, verification, bridge, dashboard, harness, hook, skill, plugin-cache, role-record, lifecycle-guard, or knowledge-base work to home-directory paths.
- `.claude/rules/project-root-boundary.md:30-31` says any proposal, review, implementation, or test that depends on a path outside the allowed roots is a NO-GO until revised to be root-contained.

### Risk / Impact

Checkpoint and audit state are live bridge artifacts. If their default location is under the user profile, GT-KB would again depend on live state outside `E:\GT-KB`, weakening portability, backup/release evidence, root-boundary enforcement, and future cleanup safety. This also leaves the owner supervising hidden machine-local state instead of keeping smart-poller state inspectable inside the project boundary.

### Recommended Action

Revise the implementation plan so the default state root is inside `E:\GT-KB`, for example `E:\GT-KB\.gtkb-state\bridge-poller\` or another explicitly governed in-root path. Keep `GTKB_STATE_DIR` only as a test/dev override, and require it to resolve inside the project root unless a test deliberately uses a temporary directory under pytest control. Tests should assert that production/default resolution fails closed for home-directory and sibling-checkout paths.

### Owner Decision Needed

No owner decision is needed. This is a mandatory boundary-rule correction.

## Finding 2 - P2: verification plan mixes GT-KB package work with the Agent Red release gate

### Claim

The proposal should add the GT-KB package's native verification commands, not rely mainly on the root `scripts/release_candidate_gate.py` lane.

### Evidence

- Proposal lines 19, 46, and 100-104 place new source under `groundtruth-kb/src/groundtruth_kb/bridge/`.
- `groundtruth-kb/pyproject.toml` configures package-local `testpaths = ["tests"]`, `pythonpath = ["src"]`, and Ruff `src = ["src", "tests"]`.
- Root `scripts/release_candidate_gate.py` describes itself as the non-deploying release-candidate gate for Agent Red and its `_python_gates()` Ruff/Bandit/import-cycle checks target root `src/` and root `tests/`, not `groundtruth-kb/src/`.
- The session startup checklist separately identifies the recent GroundTruth KB verification workflow as `python -m pytest -q --tb=short`, `python -m ruff check .`, and `python -m ruff format --check .` against that checkout's own workflow scope.

### Risk / Impact

If Prime only wires the root release-candidate gate, the new package modules may be covered by selected root tests but not by the package's native lint/format/test scope. That can produce a false clean signal for code that will live in the GroundTruth KB package.

### Recommended Action

Keep any root gate integration that is useful for adopter coordination, but make the required implementation verification explicit:

```text
cd groundtruth-kb
python -m pytest -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

If the new tests intentionally belong in root `tests/scripts/` instead of `groundtruth-kb/tests/`, the revised proposal should explain that cross-root placement and prove how those tests import the package source under `groundtruth-kb/src`.

### Owner Decision Needed

No owner decision is needed. This is a verification-scope correction.

## Non-Blocking Confirmations

- Module location under `groundtruth-kb/src/groundtruth_kb/bridge/` is acceptable as a pre-Phase-2 path, provided the implementation remains root-contained and Phase 2 relocation is still expected to move it mechanically.
- The no-touch boundary around existing legacy `poller.py`, `worker.py`, `launcher.py`, `runtime.py`, `context.py`, and `handshake.py` is sound for this P1 slice.
- Capturing a frozen live `bridge/INDEX.md` snapshot at implementation time is preferable to pinning stale S315 line numbers.
- The per-commit sequence is acceptable; the important condition is that each commit is independently verified before continuing.

## Required Revision

Revise `-001` into `-003` with:

1. In-root default state/audit path and fail-closed path validation.
2. Tests covering default path resolution, env override validation, and corrupt-checkpoint/bootstrap behavior under an in-root state path.
3. GT-KB package-native verification commands in the acceptance criteria.
4. Clarification of whether tests land under root `tests/scripts/` or `groundtruth-kb/tests/`, with import-path evidence either way.

Once revised, return the thread as `REVISED` for review.
