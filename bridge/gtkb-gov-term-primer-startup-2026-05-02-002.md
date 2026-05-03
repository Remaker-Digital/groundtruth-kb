NO-GO

# Loyal Opposition Review: GTKB-GOV-TERM-PRIMER-STARTUP

Reviewed document: `bridge/gtkb-gov-term-primer-startup-2026-05-02-001.md`
Verdict: NO-GO
Reviewer: Codex Loyal Opposition
Date: 2026-05-02

## Claim

The owner directive is valid and the proposed sibling scope is directionally
right: GT-KB needs a compact startup-loaded terminology primer, and the
smart-poller dispatch surface is the correct high-risk place to wire it.

The proposal is not ready for GO because it is not reconciled with the existing
VERIFIED canonical-terminology machinery and it asks implementation to derive
22 required terms from an authority file that currently defines fewer terms.
As written, implementation would likely create a parallel terminology surface
instead of extending the current one.

## Prior Deliberations

I searched deliberations before review per
`.claude/rules/deliberation-protocol.md`.

Relevant results:

- `DELIB-0722` / `DELIB-1180` - prior bridge thread for
  `gtkb-canonical-terminology-surface-implementation`, latest verified as
  canonical terminology managed artifacts under `.claude/rules/`.
- `DELIB-GTKB-IDP-TERMINOLOGY` - owner decision that GT-KB is formally an
  Internal Developer Platform and that IDP terminology should be used across
  docs, reports, and adopter materials.
- `DELIB-1138`, `DELIB-1016`, `DELIB-1017`, `DELIB-1018`, and `DELIB-1019` -
  prior bridge/review history for GT-KB IDP terminology formalization.

These prior deliberations do not reject the new owner directive. They do require
the revised proposal to treat this work as a dogfood/adaptation of the existing
canonical-terminology surface, or explicitly justify why a separate GT-KB primer
contract is needed.

## Blocking Findings

### F1 - Wrong canonical-terminology template paths invalidate the linkage surface

The proposal cites
`groundtruth-kb/templates/project/canonical-terminology.md` and
`groundtruth-kb/templates/project/canonical-terminology.toml` as specification
links and test inputs (`bridge/gtkb-gov-term-primer-startup-2026-05-02-001.md:52`,
`:53`, `:161`). Those files do not exist.

The actual managed artifacts are:

- `groundtruth-kb/templates/rules/canonical-terminology.md`
- `groundtruth-kb/templates/rules/canonical-terminology.toml`
- registry rows `rule.canonical-terminology` and
  `rule.canonical-terminology-config` in
  `groundtruth-kb/templates/managed-artifacts.toml:410`-`:428`
- existing doctor implementation at
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py:953`,
  with the glossary/config paths enforced at `:1005`-`:1012`

Because the proposal's test plan derives from the wrong paths, T11 and the
doctor-check reuse story cannot be trusted. Under the bridge protocol's
mandatory specification linkage gate, a proposal with materially wrong linked
specification surfaces must be revised before GO.

Required revision: replace the nonexistent template paths with the real
`templates/rules/` paths, cite the managed-artifact registry rows, and explain
whether the GT-KB root primer is an adoption of those managed artifacts, a new
product-dogfood overlay, or a deliberate fork.

### F2 - The proposal omits the prior VERIFIED canonical-terminology implementation

The proposal describes the problem as if GT-KB only has `AGENTS.md`,
`operating-model.md` Section 2, and an adopter template that has not been
integrated into the current design (`-001.md:61`-`:66`). That skips the prior
VERIFIED canonical-terminology implementation thread:

- `bridge/gtkb-canonical-terminology-surface-implementation-012.md` verified
  that `.claude/rules/canonical-terminology.md` and `.toml` are registry-backed
  managed rule artifacts.
- `groundtruth-kb/tests/test_doctor_canonical_terminology.py:203`-`:208`
  already asserts `run_doctor()` includes the canonical terminology check.
- `groundtruth-kb/tests/test_doctor_canonical_terminology.py:49`-`:102`
  already tests startup-term presence for the existing profile matrix.

The new proposal introduces a new `_check_canonical_terminology_primer`, new
`gt term-primer ...` CLI commands, and a new required-terms matrix without
explaining why the existing `_check_canonical_terminology` and
`canonical-terminology.toml` should not be extended.

Risk: two terminology systems diverge: the adopter-managed
`canonical-terminology` surface and the GT-KB-root `term-primer` surface. That
would recreate the same drift class the owner is asking this work to remove.

Required revision: add a prior-deliberations section and an explicit
architecture decision for reuse-vs-extension. The default should be to extend
the existing canonical terminology surface unless Prime can show a concrete
reason a second CLI/check namespace is necessary.

### F3 - The proposed source-of-truth rule cannot cover the owner-required 22 terms

The proposal requires each primer entry to cite
`.claude/rules/operating-model.md Section 2 <Term>` as the authoritative source
(`-001.md:83`-`:87`) and proposes T3/T7/T11 to enforce Section 2 as the source
(`-001.md:153`, `:157`, `:161`). But the proposal also says Section 2 is
missing several of the owner-required terms (`-001.md:66`), including `GTKB`,
`GroundTruth-KB`, `Agent Red`, `adopter`, `bridge`, `Prime Builder`, and
`Loyal Opposition`.

Those two claims conflict. Implementation cannot both source every 22-term
entry from Section 2 and include required terms that Section 2 does not define.
Generating the primer from Section 2 alone would be incomplete; fabricating
definitions for missing terms would bypass the proposal's stated authority
model.

Required revision: choose one governed path:

- first update `.claude/rules/operating-model.md` Section 2 through the required
  formal artifact approval flow, then generate/cite all 22 terms from it; or
- make the primer a multi-source artifact, with per-term sources such as
  operating-model Section 2, `AGENTS.md`, role rules, `file-bridge-protocol.md`,
  and `DELIB-GTKB-IDP-TERMINOLOGY`.

The test plan must then match that source model. T3 cannot require
`operating-model.md Section 2 <Term>` for terms that are intentionally sourced
elsewhere.

## Non-Blocking Notes

- The smart-poller dispatch change should preserve the existing durable-role
  deferral and live-index authority language in
  `groundtruth-kb/scripts/bridge_poller_runner.py:268`-`:300`. A fixture test
  that only checks for the primer reference is too narrow; it should also
  assert the role-record and `bridge/INDEX.md` live-state instructions remain
  present.
- The proposal's open decision on doctor severity is mostly resolved by the
  prior terminology work: missing required startup terms were already treated
  as ERROR in the existing `canonical-terminology.toml` profile matrix.

## Required Action

Revise and resubmit with:

1. Correct specification links to the live terminology artifacts and registry
   rows.
2. Prior-deliberation citations for the prior canonical-terminology and IDP
   terminology threads.
3. A clear architecture decision on extending existing
   `canonical-terminology` vs. introducing a separate `term-primer` system.
4. A source model that can actually cover all 22 owner-required terms.
5. Updated tests that derive from that corrected source model.

## Decision Needed From Owner

None. The owner directive is clear; Prime needs to correct the implementation
architecture and specification linkage.

## Verification Commands Run

```text
Get-Content -Raw harness-state/codex/operating-role.md
Get-Content -Raw .claude/rules/operating-role.md
Get-Content -Raw bridge/INDEX.md
Get-Content -Raw bridge/gtkb-gov-term-primer-startup-2026-05-02-001.md
Get-Content -Raw .claude/rules/file-bridge-protocol.md
Get-Content -Raw .claude/rules/operating-model.md
Get-Content -Raw .claude/rules/deliberation-protocol.md
Get-Content -Raw CLAUDE.md
Get-ChildItem .claude/rules -Filter '*terminolog*'
python -c "from groundtruth_kb.cli import main; main()" deliberations search "term primer startup canonical terminology GT-KB" --limit 8
Get-ChildItem -Recurse -File groundtruth-kb/templates -Filter 'canonical-terminology.*'
Get-Content -Raw groundtruth-kb/templates/rules/canonical-terminology.md
Get-Content -Raw groundtruth-kb/templates/rules/canonical-terminology.toml
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-012.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-006.md
Get-Content -Raw bridge/gtkb-idp-terminology-formalization-009.md
Select-String -Path groundtruth-kb/templates/managed-artifacts.toml -Pattern 'rule.canonical-terminology|canonical-terminology.md|canonical-terminology.toml|doctor_required_profiles' -Context 0,4
Select-String -Path groundtruth-kb/src/groundtruth_kb/project/doctor.py -Pattern 'def _check_canonical_terminology|canonical-terminology.toml|canonical-terminology.md|run_doctor' -Context 0,2
Select-String -Path groundtruth-kb/scripts/bridge_poller_runner.py -Pattern 'def _dispatch_prompt|Read your durable role|bridge/INDEX.md|Selected entries|latest status' -Context 0,4
Test-Path groundtruth-kb/templates/project/canonical-terminology.md
Test-Path groundtruth-kb/templates/rules/canonical-terminology.md
Test-Path .claude/rules/canonical-terminology.md
```

No product tests were run because this was a pre-implementation proposal
review, not implementation verification.

