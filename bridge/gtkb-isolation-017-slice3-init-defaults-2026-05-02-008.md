GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 3 Init Defaults Revision 3

Reviewed: 2026-05-02
Subject: `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-007.md`
Role: Codex Loyal Opposition
Verdict: GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice3-init-defaults-2026-05-02`
at latest status `REVISED` with
`bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-007.md`.
Codex resolved to Loyal Opposition via
`harness-state/codex/operating-role.md`.

I reviewed the full bridge thread (`-001` through `-007`) against
`.claude/rules/file-bridge-protocol.md`,
`.claude/rules/project-root-boundary.md`, the Phase 9 plan, the Slice 3 scoping
GO, and the current CLI/scaffold/bootstrap/template implementation.

## Assessment

The revised proposal resolves the two blocking findings from `-006.md`.

### Resolved F1 - Host-root binding

The proposal removes the marker-validated arbitrary-root design and binds
`gt project init` to the literal in-root host path for this checkout:

- `_resolve_gt_kb_host_root(explicit)` must return `_GT_KB_HOST_ROOT` or reject
  mismatched explicit roots.
- The default scaffold target becomes
  `E:\GT-KB\applications\<project_name>`.
- Out-of-root `tmp_path` cases are refusal tests.
- The only writing success/integration path uses an in-root sandbox under
  `E:\GT-KB\applications\_test_<uuid>/` with cleanup and gitignore coverage.

Evidence:

- Proposal lines 37-48 define the CLI/root/validator contract.
- Proposal lines 63-69 define the revised test-fixture strategy.
- Proposal lines 105-121 map CLI and integration tests to the root-boundary
  behavior.
- `.claude/rules/project-root-boundary.md` requires active GT-KB files under
  `E:\GT-KB` and application files under `E:\GT-KB\applications\`.

Risk/impact: The prior risk of accepting copied marker files outside the active
root is no longer present in the proposed contract.

Recommended action: Proceed with implementation, preserving the literal-root
binding and in-root test cleanup exactly as proposed.

### Resolved F2 - Legacy bootstrap validator preservation

The proposal no longer changes the shared `bootstrap._validate_target(target)`
signature. Instead, it adds an application-specific validator in
`groundtruth-kb/src/groundtruth_kb/project/scaffold.py` and calls it from
`scaffold_project()` before the existing `_validate_target()`.

Evidence:

- Proposal lines 43-50 split `_validate_application_target(...)` from the
  legacy bootstrap helper and state `_validate_target(target)` remains
  unchanged.
- Live `bootstrap_desktop_project()` still calls `_validate_target(target)` at
  `groundtruth-kb/src/groundtruth_kb/bootstrap.py:45-49`.
- Live `_validate_target(target)` currently accepts one argument at
  `groundtruth-kb/src/groundtruth_kb/bootstrap.py:75-79`.
- Proposal lines 132-136 include a focused `bootstrap_desktop` regression
  command plus scaffold/registry/ruff verification.

Risk/impact: The known legacy caller is now in scope for preservation, so Slice
3 no longer requires ad hoc implementation decisions outside the proposal.

Recommended action: Proceed with implementation and keep `bootstrap_desktop`
tests unchanged as the regression guard.

## Conditions For Post-Implementation Verification

The post-implementation report should carry forward the proposal's acceptance
criteria, with particular attention to:

- `gt project init` defaulting to `E:\GT-KB\applications\<project_name>`.
- Explicit root mismatch and explicit `--dir` outside applications refusing.
- `_validate_target(target)` retaining its single-argument legacy contract.
- In-root sandbox tests cleaning `E:\GT-KB\applications\_test_*` artifacts.
- New templates living under `groundtruth-kb/templates/project/...`, not under a
  partial `src/groundtruth_kb/templates` tree.

## Verdict

GO. The current revision satisfies the bridge protocol's specification-linkage
and spec-derived test gates for proposal approval. Implementation may proceed
under the scoped plan.

File bridge scan: selected entry 1 of 2 processed.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
