NO-GO

# Loyal Opposition Review: GT-KB v0.6.1 Release Bundle REVISED-1

Reviewed document: `bridge/gtkb-v061-release-003.md`
Prior review: `bridge/gtkb-v061-release-002.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-04-18
Target repo inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

REVISED-1 fixes the publish-trigger choreography, the bridge-numbering issue,
and the high-level merge-conflict surface from the prior NO-GO. One blocking
conflict-resolution defect remains: the proposed `templates/managed-artifacts.toml`
manual resolution gives invalid ownership metadata syntax and enum values for
the two canonical-terminology records.

If followed literally during the release merge, the plan can produce a registry
that fails the ownership-matrix loader before release tests can run.

## Prior Deliberations

Required deliberation search was run before review.

- `DELIB-S300-001`: owner chose the three-branch v0.6.1 bundle scope.
- `DELIB-0709`: prior owner decision that GT-KB feature proposals must pass
  review gates before implementation.
- No searched deliberation supersedes the release workflow or ownership-matrix
  bridge conditions.

## Evidence

- `bridge/gtkb-v061-release-003.md:167-189` instructs the release operator to
  add an ownership metadata block to the two new canonical-terminology
  `[[artifacts]]` rows.
- The same snippet uses nested table syntax:
  `[artifacts.ownership]` at `bridge/gtkb-v061-release-003.md:180`.
- The same snippet uses values:
  `ownership = "gtkb-managed"`, `upgrade_policy = "replace"`, and
  `adopter_divergence_policy = "overwrite"` at
  `bridge/gtkb-v061-release-003.md:181-183`.
- Current ownership-matrix loader valid enums in
  `src/groundtruth_kb/project/managed_registry.py` on
  `feature/ownership-matrix` are:
  - ownership: `gt-kb-managed`, `gt-kb-scaffolded`, `shared-structured`,
    `adopter-owned`, `legacy-exception`
  - upgrade policy: `overwrite`, `structured-merge`, `adopter-opt-in`,
    `preserve`, `transient`
  - divergence policy: `warn`, `error`, `force-merge-on-upgrade`
- The ownership-matrix version of `templates/managed-artifacts.toml` uses flat
  TOML fields on rule rows, not a nested `[artifacts.ownership]` table:
  `ownership = "gt-kb-managed"`, `upgrade_policy = "overwrite"`,
  `adopter_divergence_policy = "warn"`.
- The start-here branch adds the two rows that need metadata:
  `rule.canonical-terminology` and `rule.canonical-terminology-config`.
- The revised proposal correctly identifies the three conflict files:
  `CHANGELOG.md`, `tests/test_managed_registry.py`, and
  `templates/managed-artifacts.toml`.
- `publish.yml` was verified to trigger on `release.published`, matching the
  revised release choreography.

## Finding

### F1 - Manual registry conflict-resolution snippet would produce invalid ownership metadata

Severity: Blocking.

The revised plan asks Prime to add ownership metadata to the two
canonical-terminology records, which is correct. But the concrete TOML snippet
uses nested ownership-table syntax and three invalid enum values. The current
loader expects flat fields on the artifact record, and the ownership-matrix
branch validates enum membership.

Risk / impact:

The release operator can resolve the merge exactly as documented and create a
broken `templates/managed-artifacts.toml`. That is especially risky in a release
bridge because this is the one conflict-resolution area where the two verified
feature branches must be reconciled by hand.

Required action:

File `bridge/gtkb-v061-release-005.md` as `REVISED` with the exact target TOML
for both canonical-terminology rows. The acceptable pattern is flat fields,
matching analogous managed `rule` records:

```toml
[[artifacts]]
class = "rule"
id = "rule.canonical-terminology"
template_path = "rules/canonical-terminology.md"
target_path = ".claude/rules/canonical-terminology.md"
initial_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
managed_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
doctor_required_profiles = []
ownership = "gt-kb-managed"
upgrade_policy = "overwrite"
adopter_divergence_policy = "warn"

[[artifacts]]
class = "rule"
id = "rule.canonical-terminology-config"
template_path = "rules/canonical-terminology.toml"
target_path = ".claude/rules/canonical-terminology.toml"
initial_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
managed_profiles = ["local-only", "dual-agent", "dual-agent-webapp"]
doctor_required_profiles = []
ownership = "gt-kb-managed"
upgrade_policy = "overwrite"
adopter_divergence_policy = "warn"
```

Also add a targeted post-merge check that parses the resolved registry through
the ownership-matrix loader before proceeding:

```bash
python -m pytest tests/test_managed_registry.py tests/test_ownership_loader_agreement.py -q
```

## Non-Blocking Notes

- The corrected publish sequence is acceptable: push green release-prep commit
  to `main`, tag that exact commit, create/publish the GitHub Release, then
  monitor `publish.yml`.
- The tightened tag-move rule is acceptable: tag moves only before GitHub
  Release publication and before the release workflow starts.
- The revised merge order remains acceptable. Do not use an octopus merge for
  this bundle.
- Governance-completeness and rollback receipts remain correctly out of scope.
- Agent Red adoption remains correctly out of scope.

## Required Action Items

1. Replace the invalid nested ownership TOML snippet with the exact flat-field
   target rows above.
2. Keep the existing corrected publish choreography and three-file conflict
   plan from `-003`.
3. Add the targeted registry/ownership-loader parse test after conflict
   resolution and before release prep.
4. File the revised proposal as the next bridge version.

No GT-KB product files were modified during this review.

## Verification Commands Run

```text
Get-Content bridge/gtkb-v061-release-001.md
Get-Content bridge/gtkb-v061-release-002.md
Get-Content bridge/gtkb-v061-release-003.md
python -c "from groundtruth_kb.cli import main; main()" deliberations search "GT-KB v0.6.1 release ownership matrix rollback receipts DA governance" --limit 8
git show-ref --heads main feat/start-here-adopter-rewrite feat/da-harvest-coverage feature/ownership-matrix
git merge-base main feat/start-here-adopter-rewrite
git merge-base main feat/da-harvest-coverage
git merge-base main feature/ownership-matrix
git log --oneline main..feat/start-here-adopter-rewrite
git log --oneline main..feat/da-harvest-coverage
git log --oneline main..feature/ownership-matrix
git merge-tree $(git merge-base feat/start-here-adopter-rewrite feature/ownership-matrix) feat/start-here-adopter-rewrite feature/ownership-matrix
line-number reads of .github/workflows/publish.yml
branch-content reads of src/groundtruth_kb/project/managed_registry.py
branch-content reads of templates/managed-artifacts.toml
branch-content reads of tests/test_managed_registry.py
```

