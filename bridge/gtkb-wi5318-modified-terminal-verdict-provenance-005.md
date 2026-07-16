REVISED

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: A-2026-07-16T12-17-36Z
author_model: OpenAI Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder

# WI-5318 Revised Modified Terminal-Verdict Provenance Guard

bridge_kind: prime_proposal
Document: gtkb-wi5318-modified-terminal-verdict-provenance
Version: 005
Responds to: bridge/gtkb-wi5318-modified-terminal-verdict-provenance-004.md
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5318
target_paths: ["groundtruth-kb/src/groundtruth_kb/hygiene/auto_resolve.py", "platform_tests/scripts/test_worktree_finalization_triage.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Claim

Prime Builder holds the exact live claim for this thread under session
`A-2026-07-16T12-17-36Z`. This revision resets the review provenance after the
version-002 verdict failed closed; it does not reuse that verdict as authority.

## Summary

Correct the report-only worktree finalization planner so terminal bridge status
does not masquerade as ownership of modified audit bytes. The bounded design is
unchanged from version 001: a newly created, untracked terminal verdict may
remain eligible for the evidence-gated `safe_commit` candidate path, while a
tracked modification or deletion of an existing terminal verdict must remain
`manual_owner_review`.

The proposal changes classification only. It does not alter the index, commit a
verdict, add an actuator bypass, or authorize any source mutation until a fresh
independent Loyal Opposition verdict and implementation-start packet exist.

## Findings Addressed

### F1 (P0, blocking) - Invalid Reviewer Provenance

Version 002 is retained only as historical evidence and is not cited as live
implementation authority. This version carries a complete six-field Prime
Builder author block and explicitly requests a new Loyal Opposition review
whose actual `author_session_context_id` must differ from both the original
proposal session `019f5f6d-60cd-7040-b73f-c7d23757c4bc` and this revision
session `A-2026-07-16T12-17-36Z`. Any implementation claim and start packet
must bind the resulting fresh GO, not version 002.

## Scope Changes

None. The two target paths, classifier behavior, tests, risk boundary, and
rollback remain exactly as proposed in version 001. The only revision is the
review-provenance reset required by version 004.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `INTAKE-afbe241e` establishes that artifact metadata does not prove ownership
  of later modified bytes.
- `INTAKE-9314e628` defines required VERIFIED verdict fields without granting
  Git-finalization authority for a modified artifact.
- `DELIB-202665792` establishes the report-only finalization-triage boundary.
- Versions 001 through 004 preserve the original design, the invalid verdict,
  the failed-closed correction, and the independent NO-GO review.

## Owner Decisions / Input

No new owner decision is required. The active Tree Stabilization authorization
covers this bounded source/test proposal, and the existing provenance rules
deterministically require a fresh independent review.

## Requirement Sufficiency

Existing requirements are sufficient. `GOV-WORK-TREE-HYGIENE-001` requires
specific ownership evidence before mutation, while
`GOV-FILE-BRIDGE-AUTHORITY-001` defines terminal bridge state without granting
rewrite authority.

## Specification-Derived Verification Plan

| Requirement | Verification evidence |
| --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_worktree_finalization_triage.py -q --tb=short` proves tracked modified/deleted terminal verdicts require `manual_owner_review`, while a new untracked terminal verdict retains the evidence-gated candidate path. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | The same suite preserves append-only status recognition without inferring ownership from `VERIFIED` alone. |
| Provenance and no-bypass controls | The fresh verdict contains complete author metadata, has an independent session context, and a new `implementation_authorization.py begin` succeeds only after that verdict and a fresh claim. |
| Artifact lifecycle controls | `gt backlog show WI-5318 --json` and `gt bridge threads --wi WI-5318 --json --compact` expose the durable work-item and bridge chain. |
| Report-only behavior | `python scripts/worktree_finalization_triage.py --root E:\\GT-KB --format json` classifies the existing tracked modified terminal verdicts for manual review without index or worktree mutation. |

## Pre-Filing Preflight Subsection

The governed revision helper must pass credential scanning, exact-content
applicability preflight, mandatory clause preflight, project linkage, author
provenance, concurrency, and numbered-file checks before filing version 005.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5318; version-004 NO-GO; version-001 unchanged two-file design",
  "canonical_authority": "GOV-WORK-TREE-HYGIENE-001",
  "primary_route": "python scripts/worktree_finalization_triage.py --root E:\\\\GT-KB --format json",
  "before_behavior": "A terminal status token can be mistaken for ownership of later tracked modifications or deletions.",
  "after_behavior": "Tracked modified or deleted terminal verdicts remain manual_owner_review while newly created untracked terminal verdicts retain the evidence-gated candidate route.",
  "self_descriptive_naming": "The safe_commit and manual_owner_review outcomes directly describe whether deterministic finalization authority exists.",
  "obsolete_guidance_disposition": "Version-002 GO is retained as invalid historical evidence and is explicitly excluded from implementation authority.",
  "history_preservation": "All prior numbered bridge files remain append-only and independently queryable.",
  "rollback": {
    "instructions": "Restore only the exact two-file implementation change under separately authorized Git finalization; do not rewrite bridge history.",
    "test": "Rerun the focused finalization-triage suite and the report-only JSON command."
  }
}
```

## Risk And Rollback

The principal risk is over-tightening classification so genuinely new terminal
verdicts lose their evidence-gated candidate path. The focused suite covers both
sides. Rollback is limited to the exact two-file implementation scope after
separate authorization; this revision itself is append-only governance evidence.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
