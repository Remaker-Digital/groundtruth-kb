GO

# Loyal Opposition Review - GTKB-BRIDGE-POLLER-P1 Detector Implementation REVISED-3

Reviewed: 2026-04-29
Subject: `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-007.md`
Scope: revised implementation execution plan for P1 detector/parser/checkpoint/routing/audit slice
Verdict: GO

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P1 detector implementation git root groundtruth.toml"
```

Relevant results:

- `DELIB-1353`: prior Loyal Opposition NO-GO for the P1 detector/parser/checkpoint design.
- `DELIB-1354`: Loyal Opposition GO for the smart bridge trigger umbrella revision.
- Prior implementation-thread reviews: `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-002.md`, `-004.md`, and `-006.md`.

## Claim

GO. REVISED-3 closes the remaining root-resolution blocker by making `groundtruth.toml` the sole required live GT-KB host-root marker and by demoting `.git/` to candidate discovery only.

## Evidence

- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-007.md:23` states that `groundtruth.toml` is the single required marker for every live resolved GT-KB host root.
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-007.md:36-38` requires validation of `groundtruth.toml` for `GTKB_PROJECT_ROOT`, Git top-level discovery, and parent walking.
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-007.md:40-42` states that candidates without `groundtruth.toml` are rejected and `.git/` alone never qualifies.
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-007.md:48-56` rejects a `GTKB_PROJECT_ROOT` override without `groundtruth.toml`.
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-007.md:87` explicitly replaces the prior `AND/OR` wording with `groundtruth.toml` as the determining marker.
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-007.md:97-108` adds and revises path-resolution tests for strict marker behavior.

## Risk / Impact

Residual risk is now bounded to implementation fidelity. The proposal no longer authorizes home-directory state, pytest-temp production bypasses, `.git/`-only root qualification, root release-candidate-gate substitution for package-native verification, or mutation of legacy bridge modules.

## Implementation Constraints

- `resolve_project_root()` must require `groundtruth.toml` at the resolved root for every live path.
- `git rev-parse --show-toplevel` may discover a candidate, but the candidate is invalid unless it contains `groundtruth.toml`.
- `GTKB_STATE_DIR` must resolve under the validated root.
- No `Path.home() / ".gtkb-state"` fallback may be introduced.
- No `_is_pytest_tmp_path()` or naming-convention test bypass may be introduced in production code.
- Package-native verification is required:

```text
cd groundtruth-kb
python -m pytest -q --tb=short
python -m ruff check .
python -m ruff format --check .
```

## Test Note

The proposed test #11 uses `(fake_repo / ".git").mkdir()` as shorthand for a Git repository. During implementation, Prime should either initialize a real synthetic Git repository with `git init` or mock the `git rev-parse --show-toplevel` call so the test actually exercises the Git-top-level-without-`groundtruth.toml` branch. This is an implementation-quality constraint, not a remaining proposal blocker, because the resolver contract itself is now unambiguous.

## Decision Needed From Owner

None.
