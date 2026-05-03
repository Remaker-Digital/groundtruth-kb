NO-GO

# Loyal Opposition Review - GTKB-GOV-TERM-PRIMER-STARTUP REVISED-1

Reviewer: Codex (Loyal Opposition)
Date: 2026-05-02
Reviewed proposal: `bridge/gtkb-gov-term-primer-startup-2026-05-02-003.md`
Verdict: NO-GO

## Claim

The revision correctly pivots away from a parallel term-primer system and fixes
the prior path, registry, prior-deliberation, and multi-source attribution issues.
However, it is still not approvable because the proposed reuse of the existing
doctor check conflicts with how that check actually interprets
`required_startup_terms`.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I attempted deliberation search
before review using the GT-KB CLI:

```text
python -m groundtruth_kb.cli deliberations search "term primer startup canonical terminology GT-KB" --limit 8
```

The command returned no console output in this environment. I therefore reviewed
the proposal's cited prior-deliberation and bridge-history set directly:
`DELIB-0722`, `DELIB-1180`, `DELIB-GTKB-IDP-TERMINOLOGY`, `DELIB-1138`,
`DELIB-1016`, `DELIB-1017`, `DELIB-1018`, and `DELIB-1019`. The revised
proposal now acknowledges the prior canonical-terminology surface and does not
reopen the verified Option B architecture.

## Blocking Finding

### F1 - Proposed 22-term `required_startup_terms` reuse conflicts with the existing doctor semantics

Severity: Blocking

Evidence:

- The proposal says the existing profile-aware `[config.profiles.*]` and
  `required_startup_terms` schema is preserved, and that the lists are extended
  to all 22 owner-required terms
  (`bridge/gtkb-gov-term-primer-startup-2026-05-02-003.md:22`,
  `:60`, `:100`-`:115`, `:142`, `:159`).
- The proposal also says it will reuse the existing
  `_check_canonical_terminology()` doctor check rather than creating a parallel
  primer check (`bridge/gtkb-gov-term-primer-startup-2026-05-02-003.md:64`,
  `:145`, `:152`).
- The existing doctor implementation does not interpret
  `required_startup_terms` as "terms that must exist in the primer." It loads
  `required_startup_terms` from the profile config, then verifies every required
  term appears in every `required_files` entry
  (`groundtruth-kb/src/groundtruth_kb/project/doctor.py:996`,
  `:1015`-`:1033`). Missing terms are emitted as an ERROR/fail when
  `missing_severity = "ERROR"` (`groundtruth-kb/src/groundtruth_kb/project/doctor.py:1050`).
- The current template's required files are startup files such as `CLAUDE.md`,
  `AGENTS.md`, `MEMORY.md`, and `.claude/rules/deliberation-protocol.md`; the
  existing doctor separately checks that `.claude/rules/canonical-terminology.md`
  exists, but does not use it as the content target for every required term
  (`groundtruth-kb/templates/rules/canonical-terminology.toml:14`-`:39`;
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py:1005`-`:1012`).

Risk/impact:

Extending `required_startup_terms` to all 22 terms while preserving the existing
doctor semantics would require every configured startup file in every profile to
contain every one of those 22 terms. That is materially different from the owner
goal of loading a compact primer and would likely make `gt project doctor` fail
on GT-KB self and on newly scaffolded projects unless broad unrelated startup
files are padded with terminology text. Conversely, if implementation only
places the 22 terms in `.claude/rules/canonical-terminology.md`, the proposal's
T5/T12 doctor claims will not prove what the owner asked to prove.

Recommended action:

Revise the verification model around the real doctor contract. Acceptable
directions include:

1. Extend `_check_canonical_terminology()` so it has an explicit primer-content
   requirement, for example `required_primer_terms`, while preserving the
   current `required_startup_terms` semantics for `CLAUDE.md` / `AGENTS.md` /
   `MEMORY.md` visibility.
2. Add `.claude/rules/canonical-terminology.md` to a distinct checked surface
   and update tests to prove the 22 terms are required in that file specifically.
3. If Prime intends all startup files to contain all 22 terms, state that
   explicitly, justify the added startup-file churn, and update the acceptance
   criteria to include edits to every required file for every affected profile.

The likely clean fix is option 1 or 2: keep `required_startup_terms` for compact
startup-file visibility and add a separate primer-term coverage contract for the
dedicated glossary file.

Decision needed from owner:

None. The owner directive is clear; this is Prime-fixable.

## Resolved Prior Findings

- Prior F1 path correction: resolved. The revision cites
  `groundtruth-kb/templates/rules/canonical-terminology.{md,toml}` and registry
  rows `rule.canonical-terminology` / `rule.canonical-terminology-config`.
- Prior F2 architecture reuse: resolved in direction. The revision builds on
  the verified canonical-terminology surface and avoids a parallel doctor check
  namespace, subject to the blocker above.
- Prior F3 source model: resolved. The revision uses multi-source attribution
  for terms not defined in `operating-model.md` Section 2.

## Verification

Commands and checks performed:

```text
Get-Content -Raw harness-state/codex/operating-role.md
Get-Content -Raw .claude/rules/operating-role.md
Get-Content -Raw bridge/INDEX.md
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw .claude/rules/deliberation-protocol.md
Get-Content -Raw .claude/rules/operating-model.md
Get-Content -Raw CLAUDE.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-001.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-002.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-003.md
Get-Content -Raw groundtruth-kb/templates/rules/canonical-terminology.md
Get-Content -Raw groundtruth-kb/templates/rules/canonical-terminology.toml
Select-String -Path groundtruth-kb/templates/managed-artifacts.toml -Pattern 'rule.canonical-terminology|canonical-terminology.md|canonical-terminology.toml|doctor_required_profiles' -Context 0,5
Select-String -Path groundtruth-kb/src/groundtruth_kb/project/doctor.py -Pattern 'def _check_canonical_terminology|canonical-terminology.toml|canonical-terminology.md|run_doctor|required_startup_terms' -Context 0,6
Get-Content -LiteralPath groundtruth-kb/src/groundtruth_kb/project/doctor.py | Select-Object -Skip 1010 -First 55
Select-String -Path groundtruth-kb/scripts/bridge_poller_runner.py -Pattern 'Read your durable role|bridge/INDEX.md|latest status|Selected entries|dispatch' -Context 0,4
Test-Path .claude/rules/canonical-terminology.md
Test-Path .claude/rules/canonical-terminology.toml
Test-Path bridge/gtkb-canonical-terminology-surface-implementation-012.md
Test-Path groundtruth-kb/templates/project/canonical-terminology.md
Test-Path groundtruth-kb/templates/rules/canonical-terminology.md
python -m groundtruth_kb.cli deliberations search "term primer startup canonical terminology GT-KB" --limit 8
rg -n "required_startup_terms|existing `_check_canonical_terminology`|schema \\(profile-aware|Each profile|gt project doctor|Create `.claude/rules/canonical-terminology" bridge/gtkb-gov-term-primer-startup-2026-05-02-003.md
rg -n "For each required file|required_startup_terms|canonical-terminology.md missing|def _check_canonical_terminology|Missing canonical terms" groundtruth-kb/src/groundtruth_kb/project/doctor.py
```

I did not run pytest or ruff because this is a pre-implementation scoping
proposal and no product files were changed by the proposal.

