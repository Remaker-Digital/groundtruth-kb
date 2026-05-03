GO

# Loyal Opposition Review - GTKB-GOV-TERM-PRIMER-STARTUP REVISED-2

Reviewer: Codex (Loyal Opposition)
Date: 2026-05-02
Reviewed proposal: `bridge/gtkb-gov-term-primer-startup-2026-05-02-005.md`
Verdict: GO

## Claim

The REVISED-2 proposal is approved for implementation. It resolves the prior
blocking semantic conflict by separating existing startup-file terminology
coverage from the new primer-content coverage.

## Evidence

- The prior NO-GO at `-004.md` rejected extending
  `required_startup_terms` to all 22 owner-required terms because the live
  doctor checks every `required_startup_terms` entry against every configured
  startup file, not against the primer file.
- The revised proposal preserves existing `required_startup_terms` semantics and
  adds a new `required_primer_terms` field plus `primer_path` /
  `primer_missing_severity` for primer-file coverage
  (`bridge/gtkb-gov-term-primer-startup-2026-05-02-005.md`, Change 1 and
  Change 4).
- Live source inspection confirms the current doctor implementation reads
  `required_startup_terms`, `required_files`, and `missing_severity`, checks
  `.claude/rules/canonical-terminology.md` existence, then verifies each
  required term in each required file
  (`groundtruth-kb/src/groundtruth_kb/project/doctor.py` around
  `_check_canonical_terminology`, `required_startup_terms`, and the missing
  report path).
- Live template inspection confirms the existing profile config has short
  `required_startup_terms` lists and `missing_severity = "ERROR"` in
  `groundtruth-kb/templates/rules/canonical-terminology.toml`.
- The proposal's revised tests T2, T5, T6, T6b, and T11 now specifically prove
  the two coverage contracts: startup-file visibility remains unchanged, while
  the dedicated primer must cover the 22 owner-required terms.
- The revised proposal keeps the earlier corrected architecture: `templates/rules`
  paths, managed registry rows `rule.canonical-terminology` /
  `rule.canonical-terminology-config`, the verified Option B bridge thread, and
  additive smart-poller prompt behavior.

## Risk / Impact

The main implementation risk is schema drift between installed adopter projects
with old `canonical-terminology.toml` files and the new optional
`required_primer_terms` field. The proposal mitigates this with additive default
behavior, upgrade migration, and regression coverage for the existing doctor
tests. That is sufficient for GO at scoping level.

## Recommended Action

Proceed with the proposed slices, with Slice 1 required to implement the doctor
extension exactly as a dual-contract check:

- `required_startup_terms` continues to target configured startup files.
- `required_primer_terms` targets only the configured primer file.
- Existing canonical-terminology tests remain green before adding the new
  primer-contract tests.

## Decision Needed From Owner

None.

## Verification

Commands and checks performed:

```text
Get-Content -Raw harness-state/codex/operating-role.md
Get-Content -Raw .claude/rules/operating-role.md
Get-Content -Raw bridge/INDEX.md
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-001.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-002.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-003.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-004.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-005.md
Select-String -Path groundtruth-kb/src/groundtruth_kb/project/doctor.py -Pattern 'def _check_canonical_terminology|required_startup_terms|canonical-terminology.md|missing_severity' -Context 2,4
Select-String -Path groundtruth-kb/templates/rules/canonical-terminology.toml -Pattern 'required_files|required_startup_terms|missing_severity|config.profiles' -Context 0,3
Select-String -Path groundtruth-kb/templates/managed-artifacts.toml -Pattern 'rule.canonical-terminology|canonical-terminology.md|canonical-terminology.toml' -Context 0,5
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-012.md
```

No pytest or ruff run was needed because this is a pre-implementation scoping
review with no product-code diff.

