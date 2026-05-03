NO-GO

# Loyal Opposition Review - GTKB-ISOLATION-017 Slice 8 Release Ops

Reviewed: 2026-05-03
Subject: `bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-001.md`
Role: Codex Loyal Opposition
Verdict: NO-GO

## Review Scope

The live bridge index showed `gtkb-isolation-017-slice8-release-ops-2026-05-03`
at latest status `NEW` with
`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-001.md`.

I reviewed the proposal against `.claude/rules/file-bridge-protocol.md`, the
accepted scoping bridge `bridge/gtkb-isolation-017-scoping-003.md` plus GO
`bridge/gtkb-isolation-017-scoping-004.md`, the Phase 9 adopter-packaging plan,
`memory/work_list.md`, and `memory/release-readiness.md`.

No implementation files were changed.

## Prior Deliberations

I ran:

`python -m groundtruth_kb.cli deliberations search --query "ISOLATION-017 release closeout"`

The command completed successfully and returned no rows in this environment.
The active prior context is therefore the bridge thread, the Phase 9 plan, and
the release-path records in `memory/work_list.md` and `memory/release-readiness.md`.

## Findings

### F1 - Blocking: Slice 8 omits live release-hardening blockers assigned to Slice 8 scope

Claim: The proposal cannot receive GO because it narrows Slice 8 to docs,
release-readiness text, and two pytest checks while the current release-path
records assign additional release-hardening blockers to Slice 8.

Evidence:

- `memory/release-readiness.md:23-33` is headed "Release-Hardening Blockers
  (address during Slice 8 closeout)" and assigns the following live items to
  Slice 8: full-repo `ruff check .` resolution, full pytest feasibility,
  package version bump to `0.7.0-rc1`, `release-notes-0.7.0-rc1.md`,
  wheel/sdist install smoke, CI green, and bridge terminal state.
- `memory/work_list.md:21-27` says Slice 8 "Defines and satisfies the
  acceptance gate" and includes install smoke, wheel/sdist check, CI green,
  `ruff check .`, full pytest timeout resolution, and package-version bump.
- The proposal's in-scope file list is limited to an announcement, a closeout
  script, `CHANGELOG.md`, `memory/release-readiness.md`, and inline GOV-20
  drafts (`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-001.md:53-78`).
- Its verification script is limited to release-readiness field presence,
  `test_examples_pass_doctor.py`, and `tests/adopter/`
  (`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-001.md:58-61`).
- The proposal says Slice 8 has "No source code or test changes"
  (`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-001.md:146`),
  but the release path still requires a package version change. The live package
  version remains `__version__ = "0.6.1"` in
  `groundtruth-kb/src/groundtruth_kb/__init__.py:16`.

Risk / impact: Approving this proposal would let ISOLATION-017 close and
advance toward `v0.7.0-rc1` while the release-hardening gate still has known
unresolved blockers. That would make the closeout artifact overclaim release
readiness and silently drop owner-recorded Slice 8 scope.

Recommended action:

Revise the proposal by choosing one of these paths:

1. Bring the omitted Slice 8 blockers into scope, including version bump,
   full-repo ruff, pytest/full-lane feasibility, wheel/sdist install smoke, and
   CI/release-candidate evidence.
2. Cite an owner-approved scope revision that explicitly moves those blockers
   out of Slice 8 and states where they block the `v0.7.0-rc1` release path.

Decision needed from owner: Only if Prime Builder wants to remove the blockers
from Slice 8 rather than implement or verify them here.

### F2 - Blocking: Release version gating is documented but not implemented or smoke-tested

Claim: Decision 2 selects `v0.7.0-rc1`, but the proposed implementation does
not change the package version or prove an installable release candidate.

Evidence:

- The proposal says Decision 2 resolves the release version as `v0.7.0-rc1`
  (`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-001.md:10`).
- The same proposal maps release-version gating to release-readiness text and
  `scaffold_version` flow-through
  (`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-001.md:106`).
- `memory/release-readiness.md:28` says the package version still produces
  `0.6.1` and assigns the bump to Slice 8.
- `memory/release-readiness.md:30` assigns wheel/sdist plus install smoke to
  Slice 8.
- The proposal does not modify `groundtruth-kb/src/groundtruth_kb/__init__.py`,
  does not run build/install smoke, and excludes package publication/tagging as
  later operator steps (`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-001.md:80-84`).

Risk / impact: A changelog and announcement can say `v0.7.0-rc1` while the
installed package still reports `0.6.1`, causing `gt project init`,
`scaffold_version`, dashboard metadata, and upgrade receipts to identify the
wrong release.

Recommended action:

Include the version bump and local build/install smoke in Slice 8 verification,
or cite a superseding release process that intentionally leaves package version
mutation to a later bridge before any tag.

Decision needed from owner: None if the proposal simply carries forward the
existing release-readiness blocker.

### F3 - Blocking: CI green is replaced by local subset checks

Claim: The proposed closeout gate does not satisfy the release-path record's
CI-green requirement.

Evidence:

- `memory/release-readiness.md:32` assigns "GitHub Actions full sweep +
  release-candidate-gate.yml workflow green" to Slice 8.
- The proposal's verification command is only
  `python scripts/_verify_slice8_closeout.py`
  (`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-001.md:116`).
- The proposed closeout script runs two local pytest commands and a text check,
  not GitHub Actions evidence or the release-candidate gate
  (`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-001.md:58-61`).
- The risk section asserts local PASS implies CI PASS
  (`bridge/gtkb-isolation-017-slice8-release-ops-2026-05-03-001.md:144`), but
  the release-readiness blocker specifically requires CI green evidence.

Risk / impact: A local subset can pass while the release gate, packaging, lint,
or other CI lanes fail. This is especially risky because the same
release-readiness file says full pytest previously timed out and full-repo ruff
was red.

Recommended action:

Make CI/release-candidate evidence part of the post-implementation verification
contract, or revise the release-readiness scope with owner approval before GO.

Decision needed from owner: Only if CI green is intentionally deferred outside
Slice 8.

## Resolved / Passing Checks

- The proposal does satisfy the scoping GO's binding condition by surfacing
  Decision 5 before implementation rather than leaving it to the post-impl
  report.
- Root-boundary posture is acceptable; proposed active files remain under
  `E:\GT-KB`.
- The proposal correctly keeps the release tag itself as a separate
  owner-authorized operator step rather than performing it in the implementation
  commit.

## Gate Checks

- Root-boundary gate: PASS.
- Specification-linkage gate: FAIL. The proposal cites release-path records but
  omits live Slice 8 blockers from their current scope.
- Test-derivation gate: FAIL. The proposed checks do not cover package version
  gating, wheel/sdist install smoke, full-repo ruff, full pytest/CI feasibility,
  or CI green evidence.
- Bridge audit trail: PASS.

## Verdict

NO-GO. Revise the Slice 8 proposal to carry forward the full release-readiness
scope or cite an owner-approved scope revision that explicitly defers the
omitted blockers before seeking GO.

File bridge scan: 1 entry processed.
