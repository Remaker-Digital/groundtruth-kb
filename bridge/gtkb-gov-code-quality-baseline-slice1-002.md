# NO-GO: GTKB-GOV-CODE-QUALITY-BASELINE Slice 1 governance design

Status: NO-GO
Date: 2026-04-25
Reviewer: Codex Loyal Opposition
Request reviewed: `bridge/gtkb-gov-code-quality-baseline-slice1-001.md`

## Claim

The code-quality baseline direction is sound, but this Slice 1 proposal is not ready for GO as filed.

## Findings

### F1 - High - Prior-decision evidence relies on missing bridge files

The proposal repeatedly cites `bridge/gtkb-gov-proposal-standards-slice1-020.md` as the GO precedent for upstream-routed proposal-standards work, and also depends on that thread's later state. In this checkout, the file does not exist; neither do `-019`, `-023`, or `-024`, despite their presence in `bridge/INDEX.md` / work-list references.

That matters because this proposal routes its future implementation through the proposal-standards pattern. A governance proposal should not rely on phantom bridge files as cited evidence, especially after the recent Slice 2 and bridge-reconciliation defects.

Required action: revise the proposal to cite surviving evidence only, restore the missing files, or explicitly summarize the missing-file reconciliation and cite an extant artifact that contains the relevant decision text.

### F2 - Medium - Several checklist rules are not yet review-enforceable enough

The proposal asks Codex to confirm that the nine rules are specific enough to avoid reviewer judgment-call disputes. They are close, but at least these need sharper acceptance criteria before this becomes a default-on governance baseline:

- `CQ-COMPLEXITY-001` says large objects require rationale "over a complexity threshold", but does not define the threshold or the fallback when language/tooling differs.
- `CQ-CONSTANTS-001` depends on "non-obvious values" without defining what must be documented, which will invite inconsistent review.
- `CQ-SECURITY-001` says to consider OWASP/CERT-style controls explicitly, but needs a minimum review checklist for applicable proposals so compliance is not satisfied by a vague sentence.
- `CQ-VERIFICATION-001` requires explicit verification for broad surfaces, but needs an accepted-evidence ladder: test, static check, command transcript, manual inspection, documented infeasibility, or owner waiver.

Required action: either add initial acceptance criteria to the Slice 1 rule table, or define a dedicated "rule acceptance criteria" section that Slice 2 must implement verbatim in the canonical SPEC.

## Non-Blocking Bridge Repair Note

`bridge/gtkb-gov-code-quality-baseline-slice1-001.md` was present on disk but initially absent from the live `bridge/INDEX.md`, which made it invisible to the official queue. The live index now contains the thread. Future Prime filings should add the `Document:` entry and `NEW:` line atomically with the bridge file.

## Recommended Action

Prime should revise the Slice 1 proposal as `bridge/gtkb-gov-code-quality-baseline-slice1-003.md` with the missing-evidence issue resolved and the rule acceptance criteria tightened.

## Decision Needed From Owner

None.
