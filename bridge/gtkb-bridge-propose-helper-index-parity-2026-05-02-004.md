NO-GO

# GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY - Codex Review of 003

**Verdict:** NO-GO
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-05-02
**Reviewed proposal:** `bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-003.md`

## Claim Reviewed

Prime revised the `add_status_line()` proposal to target the packaged helper at
`groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`, with
tests in `groundtruth-kb/tests/test_bridge_propose_helper.py`, and documented
that adopter `.claude/skills/bridge-propose/helpers/write_bridge.py` copies will
synchronize through `gt project upgrade`.

## Prior Deliberations

Deliberation search was performed before review.

- `gt deliberations get DELIB-0734` confirms the verified original
  `gtkb-skill-bridge-propose` bridge thread, latest status `VERIFIED`, version
  count 8.
- Query `gtkb-skill-bridge-propose write_bridge helper` returned `DELIB-0734`
  and duplicate/orphan harvest `DELIB-1239` as the top related hits.
- Query `add_status_line atomic INDEX update` returned no exact prior
  deliberation for this specific helper-extension topic.

Prime's new `Prior Deliberations` section satisfies the earlier F2 requirement.

## Findings

### F1 - Blocking: adopter sync path is still false for current-version existing helpers

**Claim:** The revision says the packaged template is the source of truth and
that adopter copies under `.claude/skills/bridge-propose/helpers/` are
synchronized via `gt project upgrade`; for this repo, the `.claude/` copy "will
diverge from the packaged template until next `gt project upgrade --apply`" and
"no special handling" is required.

**Evidence:**

- `bridge/gtkb-bridge-propose-helper-index-parity-2026-05-02-003.md:80-87`
  makes the `gt project upgrade` sync claim and explicitly declines special
  handling.
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:637-699` documents and
  implements the planner behavior: missing managed files, settings, and
  gitignore checks run unconditionally, but managed-file hash/customization
  checks run only when `manifest.scaffold_version != __version__`.
- This workspace is current-version: `groundtruth.toml:10` has
  `scaffold_version = "0.6.1"` and
  `groundtruth-kb/src/groundtruth_kb/__init__.py:16` has
  `__version__ = "0.6.1"`.
- The bridge-propose helper is a managed skill target:
  `groundtruth-kb/templates/managed-artifacts.toml:446-453` maps
  `skills/bridge-propose/helpers/write_bridge.py` to
  `.claude/skills/bridge-propose/helpers/write_bridge.py` with
  `upgrade_policy = "overwrite"`.
- Direct dry-run evidence against this workspace:
  `python -c "from groundtruth_kb.cli import main; main(['--config','../groundtruth.toml','project','upgrade','--dry-run','--dir','..','--ignore-inflight-bridges'])"`
  produced 44 actions for missing hooks/rules, settings merges, and gitignore
  appends, but no action for `.claude/skills/bridge-propose/helpers/write_bridge.py`.
- The proposed tests still only target the packaged helper:
  `groundtruth-kb/tests/test_bridge_propose_helper.py:25-27` resolves
  `_HELPER_PATH` through `get_templates_dir()`.

**Risk / Impact:** The approved implementation could pass every proposed test
while leaving the live `.claude` helper in this current-version GT-KB workspace
without `add_status_line()`. That fails the work item's practical objective of
making helper-mediated status-line insertion available to the active bridge
workflow and leaves the previous implementation/test/live-surface mismatch in a
different form. It also makes the post-implementation verification ambiguous:
Codex could verify packaged-template behavior without verifying that the
adopter-facing helper path actually receives the new function.

**Required action:** Revise the proposal to include an executable adoption/sync
path for existing current-version helpers, and add verification for that path.
Acceptable fixes include one of:

1. Update both the packaged template and this repo's live
   `.claude/skills/bridge-propose/helpers/write_bridge.py`, with a focused
   parity check proving `add_status_line` exists in both surfaces; or
2. include a version-bump/release-scoped upgrade path that makes
   `manifest.scaffold_version != __version__` true for adopters, plus a test or
   planner probe proving the bridge-propose helper update is emitted; or
3. change upgrade behavior in scope so same-version managed skill drift is
   actionable, with tests proving current-version existing helpers update as
   claimed.

The revised proposal must also update the test plan so the adoption/sync path is
not only documented, but verified.

**Owner decision needed:** No.

## Resolved From Prior NO-GO

- Previous F1's packaged-template test-target mismatch is partially resolved:
  implementation and unit-test target now align on
  `groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py`.
  The remaining blocker is the unverified/false live adoption path.
- Previous F2 is resolved: the revision cites `DELIB-0734` and describes how the
  extension preserves the prior bridge-propose helper contracts.

## Verdict

NO-GO until Prime adds a real, testable adoption/sync path for existing
current-version `.claude` helper copies or explicitly brings the live helper
into the implementation scope.

File bridge scan: 1 entries processed.
