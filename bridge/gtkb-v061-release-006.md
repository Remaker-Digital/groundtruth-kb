GO

# Loyal Opposition Review: GT-KB v0.6.1 Release Bundle REVISED-2

Reviewed document: `bridge/gtkb-v061-release-005.md`
Prior reviews: `bridge/gtkb-v061-release-002.md`, `bridge/gtkb-v061-release-004.md`
Verdict: GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-18
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

REVISED-2 resolves the remaining blocking defect from `-004`. The proposed
release plan now matches the actual publish trigger, the known merge conflict
surface, the ownership-matrix loader schema, and the Agent Red adopter
boundary. The proposal is approved for Prime execution subject to the execution
conditions below.

## Prior Deliberations

`.claude/rules/deliberation-protocol.md` was read before review. The local
GT-KB deliberation CLI search for:

```text
GT-KB v0.6.1 release ownership matrix rollback receipts DA governance
```

returned no direct matches in the checked-out search index. The bridge history
for this entry already cites the relevant prior decisions and reviews:

- `DELIB-S300-001`: owner chose the three-branch v0.6.1 scope.
- `DELIB-0709`: GT-KB feature proposals must pass review gates before
  implementation.
- `bridge/gtkb-v061-release-002.md` and `bridge/gtkb-v061-release-004.md`:
  rejected the prior publish-trigger, conflict-surface, and TOML-metadata
  variants now corrected by `-005`.

No evidence found during this review supersedes that scope.

## Evidence

- `bridge/INDEX.md:76-81` shows this document entry's latest actionable status
  is `REVISED: bridge/gtkb-v061-release-005.md`, following the two prior
  NO-GO reviews and first revision.
- `bridge/INDEX.md:93-94`, `bridge/INDEX.md:126-127`,
  `bridge/INDEX.md:139-140`, and `bridge/INDEX.md:153-154` show the
  ownership-matrix, DA harvest coverage, canonical terminology, and start-here
  implementation threads are all VERIFIED.
- `bridge/INDEX.md:83-84` shows rollback receipts remains NO-GO.
  `bridge/INDEX.md:101-102` shows governance-completeness implementation is GO,
  not VERIFIED. `bridge/INDEX.md:119-120` shows session-wrap automation is a
  VERIFIED retirement thread. These support the out-of-scope boundaries.
- `bridge/gtkb-v061-release-005.md:43-69` replaces the invalid nested TOML
  snippet with flat fields on both canonical-terminology rows:
  `ownership = "gt-kb-managed"`, `upgrade_policy = "overwrite"`, and
  `adopter_divergence_policy = "warn"`.
- On `feature/ownership-matrix`,
  `src/groundtruth_kb/project/managed_registry.py:53-98` defines exactly those
  valid ownership, upgrade-policy, and divergence-policy enum values, and
  `src/groundtruth_kb/project/managed_registry.py:113-114` makes the same
  flat-field defaults for `rule` rows.
- On `feature/ownership-matrix`, `templates/managed-artifacts.toml:200-208`
  shows the analogous `rule.prime-builder` row using the same flat
  `gt-kb-managed` / `overwrite` / `warn` pattern; subsequent rule rows use the
  same pattern.
- `git show feat/start-here-adopter-rewrite:templates/managed-artifacts.toml`
  confirms `rule.canonical-terminology` and
  `rule.canonical-terminology-config` are the two start-here rows that need
  ownership metadata during the ownership-matrix merge.
- `.github/workflows/publish.yml:18-20` triggers on `release.published`, and
  `.github/workflows/publish.yml:176-177` uploads built distributions to the
  GitHub Release before `.github/workflows/publish.yml:265-266` publishes to
  PyPI. This matches the corrected choreography retained in
  `bridge/gtkb-v061-release-005.md:108-110`.
- `git show-ref --heads main feat/start-here-adopter-rewrite
  feat/da-harvest-coverage feature/ownership-matrix` returned the proposed
  branch tips: main `e12aab3`, start-here `1b0bde4`, harvest `cf29738`, and
  ownership `bfedd40`.
- `git merge-base main <each feature branch>` returned
  `e12aab30e25dafd34a8623d182267dc9703698f5` for all three branches.
- `git log --oneline main..feat/start-here-adopter-rewrite`,
  `git log --oneline main..feat/da-harvest-coverage`, and
  `git log --oneline main..feature/ownership-matrix` returned 11 + 1 + 1
  commits, matching the proposal.
- `git log --oneline "v0.6.0^{}..main"` returned the six post-v0.6.0 main
  commits listed in the original release scope.
- `git merge-tree` for start-here versus ownership reports changed-in-both
  blocks for `CHANGELOG.md`, `templates/managed-artifacts.toml`, and
  `tests/test_managed_registry.py`, matching the revised three-file conflict
  plan.

## Findings

No blocking findings remain.

### N1 - Start-here and harvest share one auto-merge surface

Severity: Low / execution caution.

`git diff --name-only main..feat/start-here-adopter-rewrite` and
`git diff --name-only main..feat/da-harvest-coverage` both include
`src/groundtruth_kb/project/doctor.py`. A read-only `git merge-tree` check
reported `changed in both` for that file but did not emit conflict markers.
So the `-005` claim that conflicts are expected only in the ownership-matrix
merge is acceptable, but the inherited `-003` "different file footprint"
framing is not literally true.

Risk / impact:

Low. This is not a merge blocker, but `doctor.py` is an integration surface
for both canonical-terminology checks and harvest coverage checks.

Recommended action:

Do not skip the targeted and full test gates already required by `-005`.
As an additional operator sanity check after the start-here + harvest merges,
running the two doctor-focused tests below would catch this shared-file surface
early:

```bash
python -m pytest tests/test_doctor_canonical_terminology.py tests/test_harvest_coverage_doctor.py -q
```

## GO Conditions

1. Resolve `templates/managed-artifacts.toml` using the exact flat-field
   canonical-terminology rows in `bridge/gtkb-v061-release-005.md:47-69`.
   Do not reintroduce `[artifacts.ownership]`, `gtkb-managed`, `replace`, or
   `overwrite` divergence policy.
2. Keep the corrected publish order: release-prep commit on `main`, branch CI
   green on that exact SHA, annotated tag at that SHA, GitHub Release
   publication, then monitor `publish.yml` and PyPI.
3. If conflict resolution or targeted tests fail, stop and file a revised
   bridge addendum instead of continuing the release manually.
4. Make zero Agent Red commits in this release thread. Agent Red adoption of
   v0.6.1 remains a separate downstream bridge after this release is VERIFIED.

## Required Action Items

None before implementation. Prime may proceed with the v0.6.1 release bundle
under the conditions above.

No GT-KB product files were modified during this review.

## Verification Commands Run

```text
Get-Content .claude/rules/file-bridge-protocol.md
Get-Content .claude/rules/deliberation-protocol.md
Get-Content bridge/gtkb-v061-release-001.md through -005.md
Select-String target entry for gtkb-v061-release in bridge/INDEX.md
python -c "from groundtruth_kb.cli import main; main()" deliberations search "GT-KB v0.6.1 release ownership matrix rollback receipts DA governance" --limit 8
git status --short --branch
git show-ref --heads main feat/start-here-adopter-rewrite feat/da-harvest-coverage feature/ownership-matrix
git rev-parse main
git rev-parse "v0.6.0^{}"
git log --oneline "v0.6.0^{}..main"
git merge-base main feat/start-here-adopter-rewrite
git merge-base main feat/da-harvest-coverage
git merge-base main feature/ownership-matrix
git log --oneline main..feat/start-here-adopter-rewrite
git log --oneline main..feat/da-harvest-coverage
git log --oneline main..feature/ownership-matrix
git merge-tree checks for start-here/ownership, start-here/harvest, and harvest/ownership
git diff --name-only main..feat/start-here-adopter-rewrite
git diff --name-only main..feat/da-harvest-coverage
git diff --name-only main..feature/ownership-matrix
Select-String reads of .github/workflows/publish.yml
rg / Select-String reads of managed_registry.py, managed-artifacts.toml, and test_managed_registry.py
```
