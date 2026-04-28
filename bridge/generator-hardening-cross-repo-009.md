VERIFIED

# GENERATOR-HARDENING-CROSS-REPO - Codex Verification of REVISED-1

**Status:** VERIFIED
**Date:** 2026-04-28
**Reviewer:** Codex Loyal Opposition
**Reviewed:** `bridge/generator-hardening-cross-repo-008.md`

## Claim

VERIFIED for the narrowed GH-CROSS-REPO scope.

The row-18 implementation at commit `c116d627` satisfies the cross-repo
subprocess contract: outside-project-root checkout inspection degrades before
live git subprocess work. The remaining lane violation is now assigned to
follow-on bridge `bridge/harness-state-preferences-path-cli-2026-04-28`, which
Codex reviewed as GO in
`bridge/harness-state-preferences-path-cli-2026-04-28-002.md`.

## Evidence

- `bridge/generator-hardening-cross-repo-007.md` accepted the implementation
  shape for GO conditions 1, 2, and 3.
- Local targeted verification passed:
  `python -m pytest tests/scripts/test_session_self_initialization.py::test_git_checkout_info_returns_degraded_when_outside_project_root -q`
  returned `1 passed`.
- Local targeted lint verification passed:
  `python -m ruff check scripts/session_self_initialization.py tests/scripts/test_session_self_initialization.py scripts/rehearse/_dashboard_regen.py tests/scripts/test_rehearse_dashboard_regen.py --select E,F`
  returned `All checks passed!`.
- `bridge/harness-state-preferences-path-cli-2026-04-28-002.md` provides a
  narrow GO path for the canonical harness-state preferences read leak that
  prevented literal lane-wide cleanliness in `-006`.

## Condition 4 Disposition

Condition 4 is narrowed for this thread to the violation class this bridge was
created to address: cross-repo git subprocesses from `_git_checkout_info` for a
checkout path outside `--project-root`.

The broader lane-wide condition, `status: ok` and `audit_hook_violations: 0`,
is delegated to the harness-state preferences path bridge. That follow-on must
produce the clean lane evidence before any downstream claim says the Slice 11
dashboard lane is fully clean.

## Boundary On Downstream Closure

This verification closes GH-CROSS-REPO only. It does not by itself verify the
harness-state preferences leak, and it should not be used as evidence that the
Slice 11 lane is clean across all violation classes.

GH-001 closure may cite this bridge for the cross-repo subprocess class, but
any claim of lane-wide cleanliness must wait for the harness-state preferences
path bridge to be implemented and VERIFIED, or must explicitly disclose that
the lane-wide condition remains open.

## Decision Needed From Owner

None.

