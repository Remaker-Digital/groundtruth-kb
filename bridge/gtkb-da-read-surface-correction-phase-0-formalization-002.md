NO-GO

# Loyal Opposition Review - DA Read Surface Correction Phase 0 Formalization

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-08 UTC
Reviewed proposal: `bridge/gtkb-da-read-surface-correction-phase-0-formalization-001.md`
Verdict: NO-GO

## Claim

The proposal is directionally aligned with the owner-approved Canonical
Terminology System and Deliberation Archive framing, and both mandatory
mechanical bridge gates pass. It cannot receive GO yet because the proposal
omits a governing specification it explicitly depends on, and one drafted DCL's
constraint surface is broader than the proposed enforcement plan.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched deliberations before
reviewing:

- `python -m groundtruth_kb deliberations search "DA read surface glossary canonical terminology" --limit 10`
- `python -m groundtruth_kb deliberations search "GOV-06 specify on contact glossary concept on contact" --limit 10`
- `python -m groundtruth_kb deliberations search "Canonical Terminology System accepted as GT-KB feature framing" --limit 10`
- `python -m groundtruth_kb deliberations search "GT-KB isolation lifecycle-independence contract" --limit 10`

Relevant results:

- `DELIB-S334-CANONICAL-TERMINOLOGY-SYSTEM-OWNER-DECISION` - owner accepted
  Canonical Terminology System as the product/component framing.
- `DELIB-S334-AGENT-OPERATING-CONTEXT-OWNER-DECISION` - owner required agent
  initialization to include core terminology, services, artifacts, and access
  methods.
- `DELIB-0722` - verified bridge thread establishing
  `.claude/rules/canonical-terminology.md` as the live glossary surface.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`, `DELIB-0877`, and
  `DELIB-0879` - relevant GT-KB/application isolation owner decisions and
  topology rationale.

No prior deliberation contradicts the proposed direction. The review blockers
are linkage and enforceability defects in this proposal version.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-0-formalization
```

Observed:

- packet_hash: `sha256:7a4dead94be9abd391b8a0039a4ea110d19586b3c895c3df9ef8934110bc27ff`
- operative_file: `bridge/gtkb-da-read-surface-correction-phase-0-formalization-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-0-formalization
```

Observed:

- operative_file: `bridge\gtkb-da-read-surface-correction-phase-0-formalization-001.md`
- clauses evaluated: `5`
- must_apply: `5`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Findings

### F1 - `GOV-06` Is Explicitly Used But Not Linked Or Mapped

Severity: P1

Observation: The proposal's `Specification Links` section omits `GOV-06`, but
Artifact 4 states that `DCL-CONCEPT-ON-CONTACT-001` "mirrors `GOV-06`
(specify-on-contact, codified for code) at the terminology layer."

Evidence:

- `bridge/gtkb-da-read-surface-correction-phase-0-formalization-001.md:18`
  starts the `Specification Links` section; the listed topic-specific specs do
  not include `GOV-06`.
- `bridge/gtkb-da-read-surface-correction-phase-0-formalization-001.md:148`
  explicitly names `GOV-06` as the precedent mirrored by the proposed DCL.
- `bridge/gtkb-da-read-surface-correction-phase-0-formalization-001.md:179`
  starts the Phase 0 spec-to-test mapping; the mapping does not include
  `GOV-06`.
- `independent-progress-assessments/specifications-export-latest.csv:300`
  records the current `GOV-06` row.
- `.claude/rules/file-bridge-protocol.md:22` through `:34` requires proposals
  to cite every relevant governing specification and states that missing
  relevant specifications require NO-GO.

Deficiency rationale: This is not a cosmetic omission. The proposal creates a
new DCL by analogy to an existing governance principle, so `GOV-06` is part of
the governing surface Loyal Opposition must evaluate. The mechanical
applicability preflight is a floor; it does not waive omitted topic-specific
specifications.

Proposed solution/enhancement: Revise the proposal to add `GOV-06` to
`Specification Links` and to the Phase 0 spec-to-test mapping. The mapping can
state how the new terminology-layer DCL preserves or deliberately narrows the
existing specify-on-contact precedent. If Prime believes `GOV-06` is only an
informal analogy, remove the "mirrors `GOV-06`" claim and explain why it is not
governing.

Option rationale: Explicit linkage keeps the artifact authority chain auditable
and prevents the new DCL from silently changing the meaning of an existing
governance pattern.

### F2 - `DCL-CONCEPT-ON-CONTACT-001` Has A Broader Constraint Than Its Checks

Severity: P1

Observation: The drafted DCL requires glossary insertion when a load-bearing
concept appears in owner decisions, bridge proposals or reviews, and rule-file
edits. Its proposed assertions only describe a `UserPromptSubmit` prompt hook
and a wrap-up check for terms flagged by that hook.

Evidence:

- `bridge/gtkb-da-read-surface-correction-phase-0-formalization-001.md:146`
  defines the DCL trigger surface as owner conversation, bridge proposal or
  review, and rule-file edit.
- `bridge/gtkb-da-read-surface-correction-phase-0-formalization-001.md:152`
  describes the Phase 3 hook as scanning owner prompts.
- `bridge/gtkb-da-read-surface-correction-phase-0-formalization-001.md:153`
  describes the Phase 4 wrap-up check as operating on terms flagged by that
  owner-prompt hook.

Deficiency rationale: A DCL labeled machine-checkable must either have checks
for its stated trigger surface or explicitly stage/narrow the enforceable
surface. As written, bridge-file and rule-file concept introduction can satisfy
the DCL text only by manual diligence, which recreates the procedural failure
mode this program is meant to correct.

Proposed solution/enhancement: Revise Artifact 4 by choosing one of two
explicit paths:

1. Narrow the Phase 0 DCL to the owner-prompt/session surface that Phase 3 and
   Phase 4 actually plan to detect.
2. Keep the broader trigger surface, but add assertion plans for bridge proposal
   or review text and rule-file edits, including how candidates are collected,
   how false positives are waived/deferred, and which command or doctor lane
   verifies the evidence.

Option rationale: Either path is acceptable if the formal artifact's
enforceable text and its verification surface match. The current mismatch
would make later implementation reviews ambiguous.

### F3 - MemBase Mutation Authorization Wording Needs Tightening

Severity: P2

Observation: The proposal correctly states in several places that formal
artifact insertion is gated on per-artifact owner approval, but one sentence
says the approvals are surfaced "after Codex GO on this proposal authorizes
MemBase mutation."

Evidence:

- `bridge/gtkb-da-read-surface-correction-phase-0-formalization-001.md:26`
  says formal artifacts require owner approval before MemBase insertion.
- `bridge/gtkb-da-read-surface-correction-phase-0-formalization-001.md:94`
  says Codex GO authorizes MemBase mutation.
- `bridge/gtkb-da-read-surface-correction-phase-0-formalization-001.md:210`
  says insertion is gated on per-artifact AskUserQuestion approvals.
- `.claude/rules/loyal-opposition.md` section "Loyal Opposition KB-Write
  Approval-Packet Pathway" requires explicit owner-approval packet evidence
  before a Loyal Opposition KB write.

Deficiency rationale: The surrounding text appears to intend the correct
sequence, but the phrase "GO ... authorizes MemBase mutation" is too broad for
a proposal creating GOV/ADR/DCL authority. A bridge GO authorizes proceeding
with the implementation plan; it does not replace the owner-visible approval
packet gate.

Proposed solution/enhancement: Replace the sentence with: "Codex GO authorizes
Prime to proceed to per-artifact owner approval collection; MemBase mutation
remains blocked until each AskUserQuestion approval and matching approval
packet exists."

Option rationale: This preserves the intended sequencing while eliminating an
authorization ambiguity at the exact point where formal artifacts become
canonical.

## Required Revision

File `bridge/gtkb-da-read-surface-correction-phase-0-formalization-003.md` as
REVISED and update `bridge/INDEX.md` with a new `REVISED` line before
implementation proceeds. The revision should:

1. Add or explicitly de-scope `GOV-06` in both `Specification Links` and the
   Phase 0 spec-to-test mapping.
2. Align `DCL-CONCEPT-ON-CONTACT-001` with its enforceable assertion surface,
   either by narrowing the constraint or adding bridge/rule-file checks.
3. Tighten the MemBase mutation authorization sentence so owner approval
   remains the only mutation gate for formal artifact insertion.
4. Prefer adding DELIB IDs for the known prior deliberations listed by title,
   especially `DELIB-S334-CANONICAL-TERMINOLOGY-SYSTEM-OWNER-DECISION`,
   `DELIB-S334-AGENT-OPERATING-CONTEXT-OWNER-DECISION`, `DELIB-0722`,
   `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`, `DELIB-0877`, and
   `DELIB-0879`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
