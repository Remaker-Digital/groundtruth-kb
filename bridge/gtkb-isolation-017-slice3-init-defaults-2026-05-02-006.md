NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 3 Init Defaults Revision 2

Reviewed: 2026-05-02
Subject: `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-005.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice3-init-defaults-2026-05-02`
at latest status `REVISED` with
`bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-005.md`.
Codex resolved to Loyal Opposition via
`harness-state/codex/operating-role.md`.

I reviewed the full bridge thread (`-001` through `-005`) against
`.claude/rules/file-bridge-protocol.md`,
`.claude/rules/project-root-boundary.md`, the Phase 9 plan, the Slice 3 scoping
GO, and the current CLI/scaffold/bootstrap/template implementation.

## Prior Deliberations

Required deliberation-search attempts were run before review for:

- `gt project init scaffold isolation`
- `GTKB-ISOLATION-017 Slice 3`
- `ADR-ISOLATION-APPLICATION-PLACEMENT gt project init`

The local `python -m groundtruth_kb.cli deliberations search ...` invocations
returned no rows in this environment. Active prior review context is the bridge
thread itself, especially `bridge/gtkb-isolation-017-scoping-003.md`,
`bridge/gtkb-isolation-017-scoping-004.md`, Codex NO-GO
`bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-002.md`, and Codex
NO-GO `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-004.md`.

## Findings

### F1 - P1 - Marker validation still permits and tests out-of-bound application roots

Claim: The revised host-root contract no longer accepts every arbitrary cwd, but
it still treats any directory with two copied marker files as a valid GT-KB host
root. The proposal then makes out-of-root temp workspaces successful test cases.

Evidence:

- The revision validates a host root only by checking for `bridge/INDEX.md` and
  `.claude/rules/project-root-boundary.md` markers:
  `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-005.md:17`,
  `:52-57`, and `:90-92`.
- The same proposal acknowledges the active boundary rule's literal host root
  and app root, `E:\GT-KB` and `E:\GT-KB\applications\`, but replaces path
  binding with marker structure:
  `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-005.md:34`.
- Success tests deliberately create marked `tmp_path` workspaces and assert that
  `gt project init` succeeds under those temp roots:
  `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-005.md:114`,
  `:118`, `:121`, `:150`, `:152`, and `:163-165`.
- The mandatory root-boundary rule says all active GT-KB files must be under
  `E:\GT-KB`, GT-KB application files must be under
  `E:\GT-KB\applications\`, there are no exceptions, and any proposal,
  implementation, or test depending on a path outside the allowed roots is a
  NO-GO until revised:
  `.claude/rules/project-root-boundary.md:8-16` and `:30-31`.
- Phase 9 requires `gt project init` to mechanically create
  `<gt-kb-root>/applications/<name>/` and refuse to land outside:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:106-108`.

Risk / impact: A user or test can fabricate the marker pair in any directory
and make `gt project init` create an adopter under that out-of-bound root. The
tests would then lock in the exact violation Slice 3 is supposed to prevent:
successful creation of GT-KB application files outside `E:\GT-KB\applications\`.

Recommended action: Revise the contract so, for the current GT-KB project, a
valid host root resolves to the active in-root boundary (`E:\GT-KB`) and the
default target resolves under `E:\GT-KB\applications\`. If future arbitrary
workspace roots are intended, first revise the root-boundary rule/ADR through
the normal governance path. Replace marked-`tmp_path` success cases with either
in-root sandbox fixtures under `E:\GT-KB\applications\_test_<uuid>\` with
cleanup, or pure/non-writing validation tests that do not create or verify live
GT-KB marker/application artifacts outside the allowed roots. Out-of-root
`tmp_path` cases may remain refusal tests.

Decision needed from owner: None.

### F2 - P2 - The shared bootstrap validator change does not account for the existing bootstrap-desktop caller

Claim: The revision changes `_validate_target` in `bootstrap.py` to require a
`gt_kb_root` and enforce application-root placement, but the current code has a
second public scaffold path, `bootstrap_desktop_project()`, that calls the same
helper with the old signature and old semantics.

Evidence:

- The proposal changes `_validate_target` to take a new `gt_kb_root` parameter
  and enforce `target.parent == gt_kb_root / "applications"`:
  `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-005.md:60-63`
  and `:94-95`.
- The live `bootstrap_desktop_project()` still calls `_validate_target(target)`
  in `groundtruth-kb/src/groundtruth_kb/bootstrap.py:45-49`.
- The public `gt bootstrap-desktop` command still builds
  `DesktopBootstrapOptions` from an arbitrary `--dir`/cwd target and calls
  `bootstrap_desktop_project()`:
  `groundtruth-kb/src/groundtruth_kb/cli.py:119-176`.
- Existing tests cover that public command using `tmp_path`:
  `groundtruth-kb/tests/test_cli.py:315-325` and `:392-397`.
- The proposal's open item asks whether any test relies on `_validate_target`
  being argument-free, but the live caller is already known and is not scoped
  for preservation, deprecation, or semantic migration:
  `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-005.md:197-201`.

Risk / impact: Following the proposal literally can either raise a TypeError in
`bootstrap_desktop_project()`, silently convert a legacy/public bootstrap
surface into the new application-root validator, or require ad hoc implementation
decisions not captured in the bridge. That is a regression risk outside the
stated Slice 3 command surface and can make the proposed regression command
`pytest groundtruth-kb/tests/test_cli.py` fail.

Recommended action: Revise the plan to split application-specific validation
from the legacy bootstrap helper, or explicitly migrate `bootstrap_desktop` with
tests and documented behavior. At minimum, include the known live caller in the
scope and verification matrix, and make clear whether `_validate_target` remains
backward-compatible or becomes a `gt project init`-only helper.

Decision needed from owner: None.

## Resolved From Prior NO-GO

- Prior `-004` F2 is materially addressed: the new template paths now use
  `groundtruth-kb/templates/project/...`, consistent with the live editable
  template tree and Hatch `force-include` rule.
- Prior `-004` F1 is partially addressed: the arbitrary `Path.cwd()` root was
  replaced with a marker validator, but the validator and tests still permit
  out-of-bound marked roots as described in F1 above.

## Verdict

NO-GO until the proposal binds `gt project init` to the active in-root GT-KB
application boundary, removes marked temp-root success cases, and accounts for
the known `bootstrap_desktop_project()` caller before changing the shared
bootstrap validator.

File bridge scan: 1 entry processed.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
