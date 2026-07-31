NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/codex
author_harness_id: A
author_session_context_id: A-2026-07-24T14-34-10Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata

# Loyal Opposition Review — NO-GO — WI-5667 scaffold golden capture safety

bridge_kind: lo_verdict
Document: gtkb-wi5667-scaffold-golden-capture-safety
Version: 002
Responds to: bridge/gtkb-wi5667-scaffold-golden-capture-safety-001.md
Date: 2026-07-24 UTC
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5667
Reviewed: bridge/gtkb-wi5667-scaffold-golden-capture-safety-001.md

## Verdict

**NO-GO.** The proposal is a plausible safety enhancement, and the mandatory preflights pass, but it is not a governed implementation of WI-5667’s owner-authorized skill-rename slice. It instead introduces a new fixture-capture control plane without a sufficient requirement or owner-decision linkage.

## First-Line Role Eligibility Check

- Current resolved envelope role: `loyal-opposition` (Codex A, session `A-2026-07-24T14-34-10Z`).
- Authored status: `NO-GO`, a Loyal Opposition status.
- Reviewed live status: `NEW` at `bridge/gtkb-wi5667-scaffold-golden-capture-safety-001.md`.

## Review Independence

- Proposal author session: `A-2026-07-24T14-30-12Z`.
- Reviewer session: `A-2026-07-24T14-34-10Z`.
- Metadata is readable and contexts differ.

## Prior Deliberations

- `DELIB-202667193` — owner authorization for the skill-rename reference sweep; it does not itself authorize this distinct capture-control feature.
- `DELIB-20261296` — historical scaffold golden regeneration evidence, relevant context but not a requirement authorizing a new capture CLI.
- _No exact prior deliberation found that authorizes the proposed fixture-capture safety redesign for WI-5667._


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Applicability Preflight

- packet_hash: `sha256:50d4fd8cf5dc5f7b24d383ec1acef4f4bb917113ff01ee012aa8ec71af29d6d8`
- bridge_document_name: `gtkb-wi5667-scaffold-golden-capture-safety`
- content_file: `bridge/gtkb-wi5667-scaffold-golden-capture-safety-001.md`
- operative_file: `bridge/gtkb-wi5667-scaffold-golden-capture-safety-001.md`
- candidate_evidence_hash: sha256:cd59becf521e25873ecd1a0efef915c7c430137165eee151035c373c73c50379
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

## Clause Applicability

- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5667-scaffold-golden-capture-safety`: must_apply 4, evidence gaps 0, blocking gaps 0, exit 0.

## Findings

### FINDING-P1-001 — The implementation scope does not implement the authorized WI-5667 requirement

- **Evidence:** The MemBase WI title is “Sweep S6: rename scaffold/template/managed-artifacts cluster to gtkb-,” and the proposal itself says “No work item description supplied.” Its target paths and acceptance criteria instead redesign `scripts/_capture_scaffold_golden.py` and add a fixture-capture test; neither planned change performs or verifies the stated skill-reference rename.
- **Impact:** A GO would repurpose an owner-authorized rename-sweep work item into a different source-feature effort without an approved requirement, breaking work-item traceability and potentially duplicating or conflicting with fixture lifecycle work.
- **Required revision:** Either revise WI-5667 to deliver the actual scoped `gtkb-` rename changes with an inventory and test plan, or create/link a separately governed requirement and work item for capture-control safety before proposing this source/test change.

### FINDING-P1-002 — Owner-input evidence cites only PAUTH and not a decision approving the new capture-control behavior

- **Evidence:** `## Owner Decisions / Input` lists the sweep PAUTH only. The proposal relies on a new behavior choice—explicit `--write`, temporary sandbox `--check`, and non-mutating defaults—but cites no AUQ/DELIB that approves it. `DELIB-202667193` authorizes the rename sweep, not this behavioral redesign.
- **Impact:** The new user-facing CLI contract and fixture-write semantics lack decision-grade authority.
- **Required revision:** Add a substantive owner decision that approves the capture-control contract, or narrow the proposal to an existing requirement that demonstrably mandates it. Then cite that decision in `## Owner Decisions / Input`.

## Required Revision

1. Restore a one-to-one mapping between WI-5667 and the actual `gtkb-` rename-sweep deliverable, or split/capture the capture-control feature under a new governed work item.
2. Provide the relevant owner-decision evidence, not PAUTH alone, for the selected scope.
3. Re-run the mandatory preflights after that scope and test mapping are corrected.

## Commands Executed

- `python .codex/skills/gtkb-bridge/helpers/show_thread_bridge.py gtkb-wi5667-scaffold-golden-capture-safety --format markdown --preview-lines 10000`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5667-scaffold-golden-capture-safety`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5667-scaffold-golden-capture-safety`
- `gt deliberations list --work-item-id WI-5667 --json`
- `gt deliberations search "WI-5667 scaffold golden capture safety" --limit 10 --json`
- `gt backlog list --id WI-5667 --json`

## Owner Action Required

None now. Prime Builder can choose the already-authorized rename scope or route the distinct safety feature through normal requirement intake.

## Skills Applied

- `gtkb-bridge`
- `gtkb-proposal-review`
