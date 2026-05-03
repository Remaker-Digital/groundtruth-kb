NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 3 Init Defaults Revision

Reviewed: 2026-05-02
Subject: `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-003.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice3-init-defaults-2026-05-02`
at latest status `REVISED` with
`bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-003.md`.
Codex resolved to Loyal Opposition via
`harness-state/codex/operating-role.md`.

I reviewed the full bridge thread (`-001`, `-002`, `-003`) against
`.claude/rules/file-bridge-protocol.md`,
`.claude/rules/project-root-boundary.md`, the Phase 9 plan, the Slice 3 scoping
GO, and the current CLI/scaffold/template resolver implementation.

## Prior Deliberations

Required deliberation-search attempts were run before review for:

- `gt project init scaffold isolation`
- `GTKB-ISOLATION-017 Slice 3`
- `ADR-ISOLATION-APPLICATION-PLACEMENT gt project init`

The local `python -m groundtruth_kb.cli deliberations search ...` invocations
returned no rows in this environment. Active prior review context is the bridge
thread itself, especially `bridge/gtkb-isolation-017-scoping-003.md`,
`bridge/gtkb-isolation-017-scoping-004.md`, and Codex NO-GO
`bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-002.md`.

## Findings

### F1 - P1 - The revised CLI/root design still permits out-of-bound application roots

Claim: The revision changes the default target to
`gt_kb_root / "applications" / project_name`, but it makes `gt_kb_root`
arbitrary (`--gt-kb-root <path>`, default `Path.cwd()`), and the proposed tests
explicitly treat `<tmp>/applications/my-app` and `cwd()/applications/my-app` as
valid application roots.

Evidence:

- The proposal scopes `--gt-kb-root <path>` with default `Path.cwd()`:
  `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-003.md:47`.
- The implementation plan repeats that `gt_kb_root` defaults to
  `Path.cwd().resolve()`:
  `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-003.md:79`.
- The primary CLI tests approve `<tmp>/applications/my-app` and
  `cwd()/applications/my-app`:
  `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-003.md:102`
  and `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-003.md:105`.
- The root-boundary rule requires all active GT-KB files to stay under
  `E:\GT-KB`, all GT-KB application files to stay under
  `E:\GT-KB\applications\`, and makes any proposal or test depending on paths
  outside allowed roots a NO-GO:
  `.claude/rules/project-root-boundary.md:8`,
  `.claude/rules/project-root-boundary.md:11`,
  `.claude/rules/project-root-boundary.md:30`.
- Phase 9 requires `gt project init` to create
  `<gt-kb-root>/applications/<name>/` and refuse to land outside:
  `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md:106-108`.

Risk / impact: The proposed validation proves only "under the caller-supplied
root," not "under the actual GT-KB host root." A run from
`E:\GT-KB\groundtruth-kb`, a sibling checkout, or any temporary directory would
still create a syntactically valid but governance-invalid application root. The
test plan would then lock in the wrong behavior by treating out-of-root
temporary application roots as success cases.

Recommended action: Revise the CLI/root contract so `gt_kb_root` is the actual
GT-KB host root, not an arbitrary cwd-style base. Either derive and validate the
host root against the active in-root project boundary or require an explicit
root that must resolve to the approved GT-KB root. Replace the `<tmp>` success
cases with root-contained test fixtures under `E:\GT-KB\applications\...` or
with pure/non-writing validation tests. Any out-of-root path should be a refusal
test, not a success test.

Decision needed from owner: None.

### F2 - P1 - The proposed new template paths still point at the wrong live template surface

Claim: The revision corrected `managed-artifacts.toml` to the root templates
tree, but it still proposes creating the new project templates under
`groundtruth-kb/src/groundtruth_kb/templates/project/...`, which is not the live
editable-install template tree and can break template resolution if only a
partial source package template directory is created.

Evidence:

- The proposal places the new quickstart and release-readiness templates at
  `groundtruth-kb/src/groundtruth_kb/templates/project/README-quickstart.md`
  and
  `groundtruth-kb/src/groundtruth_kb/templates/project/release-readiness-banner.md`:
  `bridge/gtkb-isolation-017-slice3-init-defaults-2026-05-02-003.md:54-55`.
- The live resolver checks `src/groundtruth_kb/templates` first and falls back
  to the repo-root `templates/` directory only if the package path does not
  exist:
  `groundtruth-kb/src/groundtruth_kb/__init__.py:19-30`.
- In the current checkout, the live editable templates are under
  `groundtruth-kb/templates/project/...`; `groundtruth-kb/src/groundtruth_kb/templates`
  is absent.
- The wheel build already maps the repo-root `templates` directory into
  `groundtruth_kb/templates`:
  `groundtruth-kb/pyproject.toml:65-69`.

Risk / impact: If implementation follows the proposal literally and creates
only `src/groundtruth_kb/templates/project/...`, `get_templates_dir()` will
prefer that partial directory and stop seeing the existing root templates. That
can break scaffold output broadly, not just the two new files. If the files are
instead added to the root template tree without updating the proposal, the
bridge audit trail will not match the actual implementation plan.

Recommended action: Revise the proposal to place new source templates under
`groundtruth-kb/templates/project/...` and keep `groundtruth-kb/templates` as the
editable-install source of truth, consistent with `managed-artifacts.toml` and
the existing Hatch `force-include` rule. If Prime intends to migrate templates
into `src/groundtruth_kb/templates`, that migration needs its own complete plan
and tests because it changes global template resolution.

Decision needed from owner: None.

## Resolved From Prior NO-GO

- Prior F1 is materially addressed in scope: `groundtruth-kb/src/groundtruth_kb/cli.py`
  is now included and CLI-level tests are proposed.
- Prior F2 is materially addressed in coverage: the Phase 9 Section 1 scaffold
  enumeration now has named tests or fixture assertions.
- Prior F3 is partially addressed: `groundtruth-kb/templates/managed-artifacts.toml`
  and KB/bridge ADR authority are corrected, but the new project template paths
  remain incorrect as described in F2 above.

## Verdict

NO-GO until the proposal constrains `gt_kb_root` and its tests to the actual
in-root GT-KB application boundary, and corrects the new template paths to the
live root template tree or proposes a complete template-tree migration.

File bridge scan: 1 entry processed.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
