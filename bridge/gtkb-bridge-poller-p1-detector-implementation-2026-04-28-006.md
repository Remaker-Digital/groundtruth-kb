NO-GO

# Loyal Opposition Review - GTKB-BRIDGE-POLLER-P1 Detector Implementation REVISED-2

Reviewed: 2026-04-29
Subject: `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-005.md`
Scope: revised implementation execution plan for P1 detector/parser/checkpoint/routing/audit slice
Verdict: NO-GO

## Prior Deliberations

Deliberation search command:

```text
python -m groundtruth_kb deliberations search "bridge poller P1 detector implementation pytest state directory project root"
```

Relevant results:

- `DELIB-1353`: prior Loyal Opposition NO-GO for the P1 detector/parser/checkpoint design.
- `DELIB-1352`: Loyal Opposition GO for the revised P1 detector design.
- Prior bridge reviews in this implementation thread: `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-002.md` and `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-004.md`.

## Claim

NO-GO. REVISED-2 closes the pytest-temp bypass and clarifies host-root behavior, but it leaves root qualification too broad by allowing `.git/` alone to identify a GT-KB project root. For live GT-KB smart-poller state, the resolver must require the active GT-KB root marker, not any Git checkout.

## Finding 1 - P1: `.git/`-only root qualification can accept non-GT-KB roots

### Claim

`resolve_project_root()` must not treat `.git/` alone as sufficient proof of a valid GT-KB host root for smart-poller state.

### Evidence

- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-005.md:143` states that `resolve_project_root()` returns the GT-KB host root as the directory containing `groundtruth.toml` **AND/OR** `.git/`.
- `bridge/gtkb-bridge-poller-p1-detector-implementation-2026-04-28-005.md:145` confirms the current valid root contains both `groundtruth.toml` and `.git/`.
- Live verification confirms `E:\GT-KB\groundtruth.toml` exists and `E:\GT-KB\.git` exists, while `E:\GT-KB\groundtruth-kb\groundtruth.toml` and `E:\GT-KB\groundtruth-kb\.git` do not exist.
- `.claude/rules/project-root-boundary.md:9-10` says no GT-KB artifact may be created, read as a live dependency, updated, verified, or required from outside `E:\GT-KB`.
- `.claude/rules/project-root-boundary.md:22` explicitly bars routing GT-KB work to home-directory paths, temp-directory paths, sibling checkouts, or legacy project locations.
- `.claude/rules/project-root-boundary.md:29-31` says unknown live paths must fail closed and that any proposal depending on an outside path is NO-GO until root-contained.

### Risk / Impact

If `.git/` alone qualifies a root, `GTKB_PROJECT_ROOT` or a future working-directory context could point smart-poller state at an arbitrary sibling Git checkout that is not the active GT-KB host. The state directory would still be "under a root" by the helper's local logic, but it would not necessarily be under `E:\GT-KB` or under a valid GroundTruth project. That reopens the same class of hidden live-state and cleanup-safety risk the previous revisions were trying to close.

### Recommended Action

Revise `resolve_project_root()` so a valid live root must contain `groundtruth.toml`. `git rev-parse --show-toplevel` can remain a discovery mechanism, but the discovered Git top-level must then be validated by checking for `groundtruth.toml`.

For this project, expected semantics should be:

```text
valid root = resolved directory containing groundtruth.toml
git top-level = candidate discovery only, not sufficient by itself
state root = <valid root>/.gtkb-state/bridge-poller/
```

Add tests that prove:

1. `GTKB_PROJECT_ROOT` pointing to a Git repo without `groundtruth.toml` raises `ProjectRootNotFoundError` or a specific invalid-root error.
2. `git rev-parse --show-toplevel` returning a path without `groundtruth.toml` is rejected.
3. Invoking from `groundtruth-kb/` still resolves to `E:\GT-KB` because the discovered top-level contains `groundtruth.toml`.

### Owner Decision Needed

No owner decision is needed. This is a boundary-enforcement correction.

## Confirmed Closures

- `GTKB_STATE_DIR` no longer accepts pytest temp paths by naming convention.
- Tests now use a synthetic in-root project under pytest `tmp_path`, which is sound.
- Host-root semantics are now explicit: state belongs at `E:\GT-KB\.gtkb-state\bridge-poller\`, not under `E:\GT-KB\groundtruth-kb\`.
- Package-native test placement and verification remain correct.

## Required Revision

Revise `-005` into `-007` with:

1. `groundtruth.toml` required for every live resolved GT-KB root.
2. `.git/` treated only as a candidate-discovery aid, never sufficient by itself.
3. Tests covering Git repo without `groundtruth.toml` rejection and nested `groundtruth-kb/` resolution success.

Once revised, return the thread as `REVISED` for review.
