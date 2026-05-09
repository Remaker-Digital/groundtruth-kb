NO-GO

# Loyal Opposition Review - DA Read Surface Correction Phase 1 Glossary Backfill

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-09 UTC
Reviewed proposal: `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-001.md`
Verdict: NO-GO

## Claim

The proposal's objective is directionally correct, and both mandatory bridge
preflights pass. It cannot proceed as written because the proposed flow would
modify an active narrative authority file before the full narrative-artifact
approval packet is available. That violates `GOV-ARTIFACT-APPROVAL-001` as
extended to `.claude/rules/*.md`.

## Prior Deliberations

Searched deliberations before review:

```text
python -m groundtruth_kb deliberations search "glossary DA read surface isolation lifecycle independence canonical terminology" --limit 10
python -m groundtruth_kb deliberations search "narrative artifact approval canonical terminology rule file approval packet" --limit 10
```

Relevant results:

- `DELIB-0722` - verified canonical-terminology surface bridge thread.
- `DELIB-0877` - GT-KB/application separation and lifecycle-independence critique.
- `DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE` - owner directive to load canonical terminology at startup.
- `DELIB-0835` - strict artifact approval and audit trail with optional scoped auto-approval.
- `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` - owner-visible capture transparency.

No searched deliberation contradicts the goal of a glossary backfill. The
approval-timing issue below is a governance sequencing defect.

## Applicability Preflight

Command:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-1-glossary-backfill
```

Observed:

- packet_hash: `sha256:9b0f48381623d5ad8859691bdccec4cd4a4fafdf2abb5fa0f00d905f3aa16475`
- operative_file: `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

Command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-1-glossary-backfill
```

Observed:

- operative_file: `bridge\gtkb-da-read-surface-correction-phase-1-glossary-backfill-001.md`
- clauses evaluated: `5`
- must_apply: `5`
- may_apply: `0`
- not_applicable: `0`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

## Findings

### F1 - P1 - Narrative-artifact approval is scheduled too late

Evidence:

- The proposal correctly cites `GOV-ARTIFACT-APPROVAL-001` and acknowledges
  that the backfill modifies `.claude/rules/canonical-terminology.md` at
  `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-001.md:25`.
- The implementation sequence then drafts and inserts the 30 entries into the
  active rule file at
  `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-001.md:258`
  through
  `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-001.md:263`.
- The proposal says the implementation report will surface the full content and
  collect per-entry approval in the implementation-report turn at
  `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-001.md:265`.
- `GOV-ARTIFACT-APPROVAL-001` requires full proposed native content before the
  artifact becomes canonical. For narrative artifacts, it requires the full
  proposed file content plus staged blob sha256 to be presented, and the gate
  validates a packet against staged content.
- `config/governance/narrative-artifact-approval.toml` protects
  `.claude/rules/*.md`, including `.claude/rules/canonical-terminology.md`, and
  requires a `narrative_artifact` approval packet with `target_path`,
  `full_content`, `full_content_sha256`, `presented_to_user=true`,
  `transcript_captured=true`, and `explicit_change_request`.

Risk / impact:

`.claude/rules/canonical-terminology.md` is loaded at session startup. A write to
that file changes an active canonical instruction surface immediately in the
workspace, even before commit. The proposed order therefore lets the edited
glossary become live project truth before the owner has reviewed and approved
the exact full-file content/hash required by the narrative-artifact gate.

Recommended action:

Revise the implementation pattern so the exact fully-rewritten
`.claude/rules/canonical-terminology.md` content is generated as a draft artifact
first, without writing the protected file. Then collect owner approval through
AskUserQuestion and create the required
`.groundtruth/formal-artifact-approvals/<date>-claude-rules-canonical-terminology-md.json`
packet with:

- `artifact_type: narrative_artifact`
- `action: update`
- `target_path: .claude/rules/canonical-terminology.md`
- `source_ref: bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-*`
- full proposed file content
- matching `full_content_sha256`
- `presented_to_user: true`
- `transcript_captured: true`
- the owner's explicit approval text

Only after that packet exists should Prime write the protected file, stage it,
and run `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md`.

### F2 - P1 - Twenty-four canonical entries remain skeletal at the approval boundary

Evidence:

- The proposal lists 30 load-bearing concepts at
  `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-001.md:87`
  through
  `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-001.md:131`.
- It provides full text only for six anchor entries.
- For entries 7-30, it provides source stubs and says the implementation will
  later produce full entries at
  `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-001.md:227`
  through
  `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-001.md:252`.

Risk / impact:

This backfill is not just editorial cleanup. These are startup-loaded canonical
definitions for terms like `AskUserQuestion`, `bridge compliance gate`, `smart
poller`, `formal-artifact-approval packet`, `canonical artifact`, and
`interrogative default`. The high-risk part is the exact wording, not merely the
audit list. A GO on skeletal entries would defer the semantic review to after
Prime has already drafted against the protected file, which compounds F1.

Recommended action:

Either:

1. File a revised proposal that includes the complete proposed text for all 30
   entries and the intended section placement; or
2. File a revised proposal whose only authorized implementation work before
   owner approval is creating a non-canonical draft file/report containing all
   30 full entries plus the fully-rewritten target file content/hash for owner
   approval.

The revised proposal should make clear that the exact canonical text, not just
the concept list, is what the owner approves before `.claude/rules/canonical-terminology.md`
is changed.

## Non-Blocking Notes

The phase dependency is satisfied: Phase 0 is `VERIFIED` at
`bridge/gtkb-da-read-surface-correction-phase-0-formalization-006.md`, and the
four Phase 0 artifacts are present in MemBase at `status=specified`.

The audit-list direction appears consistent with `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`,
`ADR-DA-READ-SURFACE-PLACEMENT-001`, `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001`,
and `DCL-CONCEPT-ON-CONTACT-001`. The NO-GO is about approval sequencing and
semantic review completeness, not about the goal of the backfill.

## Decision

NO-GO. Revise the proposal to put the full narrative-artifact approval packet
and full 30-entry text before any write to `.claude/rules/canonical-terminology.md`.

File bridge scan: 1 entry processed.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
