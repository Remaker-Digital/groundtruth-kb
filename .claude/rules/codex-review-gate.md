# Counterpart Review Gate — Mandatory Pre-Implementation Review

This rule auto-loads via `.claude/rules/` convention and is TRACKED in git.

## The Rule

**No implementation without Loyal Opposition review when the bridge is active. No exceptions.**

Before Prime Builder executes ANY of the following actions, a bridge proposal
MUST exist with Loyal Opposition GO status:

1. Writing or modifying source code files
2. Promoting, reverting, or changing spec statuses in the KB
3. Creating, resolving, or modifying work items in the KB
4. Modifying configuration files
5. Running deployment scripts
6. Any action that changes the state of either repository

The bridge proposal is not valid unless it includes a `Specification Links`
section that cites every relevant governing specification. Loyal Opposition must
NO-GO any implementation proposal that omits relevant specifications or treats
the links as placeholder/TBD content.

Loyal Opposition MUST reject all implementation proposals that are not linked to
specifications. Without linked specifications, there MUST NOT be an approved
implementation plan.

## Mechanical Implementation-Start Gate

Protected implementation mutations require a current local authorization packet
created from a live latest-`GO` bridge entry:

```text
python scripts/implementation_authorization.py begin --bridge-id <document-name>
```

The authorization packet is only machine-readable proof that the current session
is scoped to one GO'd bridge proposal. It is not a substitute for the bridge
`GO`, it does not authorize formal GOV/ADR/DCL/SPEC mutation, and it does not
weaken any formal-artifact approval gate.

Project-scoped implementation authorization records may satisfy the
owner-approval evidence for a bounded project scope, but they are additive to
this gate. A project authorization does not authorize implementation until a
bridge proposal cites the applicable project/work evidence, Loyal Opposition
records `GO`, and the implementation-start packet is created from that GO.

The hook `scripts/implementation_start_gate.py` must deny protected source,
test, script, hook, configuration, deployment, repository-state, and KB-mutation
work when the packet is missing, corrupt, expired, stale relative to live
`bridge/INDEX.md`, or outside the GO'd proposal's `target_paths`.

Implementation proposals filed after this gate lands must include a
`Requirement Sufficiency` subsection. It must state either that existing
requirements are sufficient and cite the governing requirements, or that new or
revised requirements are required before implementation. The second state
authorizes only requirement/specification capture through the governed approval
path, not source/config/test implementation.

## What Counts as "Implementation"

- Code changes (new files, edits, deletions)
- KB mutations (insert_spec, update_spec, insert_test, resolve_work_item, etc.)
- Configuration changes (groundtruth.toml, settings.json, CI workflows)
- Deployment operations (build, push, deploy)
- Git operations that change history (merge, rebase, tag)

## What Does NOT Require a Bridge Proposal

- Read-only exploration (grep, read, glob, git log)
- Running existing tests (pytest, ruff, mypy)
- Reading KB state (queries, list_specs, get_spec)
- Drafting bridge proposals themselves
- Updating MEMORY.md (session state, not canonical knowledge)
- Emergency bridge infrastructure repair (per bridge-essential.md)

## Enforcement

If Prime Builder catches itself about to implement without a GO:
1. STOP immediately
2. Draft a bridge proposal describing the intended change
3. Submit to bridge/INDEX.md as NEW
4. Wait for Loyal Opposition GO before proceeding
5. Run `python scripts/implementation_authorization.py begin --bridge-id <document-name>`
   before protected implementation edits

If Loyal Opposition is reviewing an implementation proposal:
1. Confirm the proposal links all relevant specifications.
2. Confirm the proposed tests are derived from those linked specifications.
3. Run `python scripts/bridge_applicability_preflight.py --bridge-id <document-name>`.
4. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id <document-name>`
   (no `--report-only`). Treat exit `5` as a `NO-GO` blocker unless the proposal
   carries an explicit owner-waiver line per blocking gap. The `--report-only`
   flag is diagnostic-only and cannot stand in for the mandatory check.
5. Include the generated `Applicability Preflight` section AND the
   `Clause Applicability` section (with `Blocking Gaps` subsection if non-empty)
   in any `GO` verdict.
6. Issue `NO-GO` if any required applicable specification is missing, if the
   test mapping is missing or incomplete, or if the clause preflight reports
   a blocking gap without an explicit owner-waiver line for the offending clause.

If Loyal Opposition is verifying an implementation:
1. Carry forward the proposal's linked specifications.
2. Confirm tests derived from those specifications were created or identified.
3. Confirm those tests were executed against the implementation.
4. Run `python scripts/bridge_applicability_preflight.py --bridge-id <document-name>`.
5. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id <document-name>`
   (no `--report-only`). Treat exit `5` as a `NO-GO` blocker per the same rules
   as proposal review.
6. Include the generated `Applicability Preflight` section AND the
   `Clause Applicability` section in any `VERIFIED` verdict.
7. Issue `NO-GO` instead of `VERIFIED` for any untested linked specification or
   blocking-gap clause unless an explicit owner waiver is documented.

This applies even when:
- The change "seems too small to review"
- The owner has given pre-approval on a work list
- The owner has authorized the containing project for implementation
- The tests are already passing
- The change is "just a KB status promotion"

Pre-approval on the work list, or project-scoped authorization in MemBase, means
"you may proceed through the bridge protocol autonomously" - it does NOT mean
"skip the bridge protocol."

## Rationale

Session S296 incident: SPEC-1834 was promoted to verified without a bridge
proposal. The change was correct (64 tests passing) but the governance gap
was real — no audit trail, no independent verification, no opportunity to catch
errors. The bridge protocol exists to prevent exactly this class of silent drift.

## Owner Decisions / Input Section Requirement

(Active per Sub-slice C of GTKB-GOV-AUQ-ENFORCEMENT-STACK; mechanically enforced by `.claude/hooks/bridge-compliance-gate.py`.)

Bridge proposals/reports that claim dependence on owner approval — citing the AUQ-only rule (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md`), referencing AskUserQuestion answers, or otherwise indicating owner-decision scope — MUST include a non-empty `## Owner Decisions / Input` section enumerating the relevant AskUserQuestion evidence.

Codex review checks for the section's presence and substantive content. Loyal Opposition issues NO-GO when applicable proposals/reports lack the section. The bridge-compliance-gate hook fails the Write before submission to prevent ambiguous packets from reaching review. Verdict files (GO/NO-GO/VERIFIED) are explicitly excluded.


## Prior Deliberations Section Requirement

(Active per Phase 2 of GTKB-DA-READ-SURFACE-CORRECTION; supported by GOV-GLOSSARY-AS-DA-READ-SURFACE-001 and ADR-DA-READ-SURFACE-PLACEMENT-001.)

Bridge implementation proposals MUST include a substantive ## Prior Deliberations section. The section anchors the proposal in the prior-decision history and is one of the named placement targets for the DA read-surface correction (the bridge-template surface).

The bridge-propose helper at .claude/skills/bridge-propose/helpers/write_bridge.py pre-populates this section by default via pre_populate_prior_deliberations: glossary-source seeding from .claude/rules/canonical-terminology.md plus optional semantic search. Authors review and prune the pre-populated entries.

Loyal Opposition MUST issue NO-GO when reviewing a NEW or REVISED proposal that meets ALL of these conditions:

1. The ## Prior Deliberations section is absent OR empty (no candidate entries, helper-suggested or author-supplied).
2. No _No prior deliberations: <reason>._ justification line is present (the explicit empty-justification convention for novel topics with genuinely no DA precedent).

The justification line is the authorized opt-out path for proposals on novel topics; it requires the author to state the reason in prose. NO-GO findings should cite this rule and the missing-section evidence.

Verdict files (lines starting with GO, NO-GO, or VERIFIED) are explicitly excluded from this check; they are evidence narratives, not authoring artifacts.

## © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
