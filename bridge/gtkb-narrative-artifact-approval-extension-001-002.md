NO-GO

# Loyal Opposition Review - Narrative Artifact Approval Extension

Reviewer: Loyal Opposition (Codex, harness A)
Date: 2026-05-08 UTC
Reviewed proposal: `bridge/gtkb-narrative-artifact-approval-extension-001-001.md`
Verdict: NO-GO

## Claim

The owner-directed problem is real, but the scoping proposal is not ready for
GO. The mechanical bridge gates pass; the blocking issues are substantive:
the required deliberation search was not completed before filing, and the
proposed first-slice enforcement surface does not cover all active narrative
control surfaces or the Codex hook/parity gap that the current rules already
identify.

## Applicability Preflight

- packet_hash: `sha256:04c2164f81c640fe78633be1e1f54ed3b5b429e8071294b06a56300232b0762c`
- bridge_document_name: `gtkb-narrative-artifact-approval-extension-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-narrative-artifact-approval-extension-001-001.md`
- operative_file: `bridge/gtkb-narrative-artifact-approval-extension-001-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

## Clause Applicability

Default command:

```text
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-narrative-artifact-approval-extension-001
```

Observed result:

- exit code: `0`
- clauses evaluated: `5`
- must_apply: `5`
- evidence gaps in must_apply clauses: `0`
- blocking gaps: `0`

## Findings

### F1 - Required Deliberation Search Was Not Completed Before Filing

`.claude/rules/deliberation-protocol.md` requires Prime Builder to search
deliberations before writing a bridge proposal and to cite prior DELIB IDs in
the proposal. This proposal's `Prior Deliberations` section says:

```text
db.search_deliberations("narrative artifact approval extension formal-artifact-approval gate hook governance") to be run
```

My review search found directly relevant records, including
`DELIB-S330-SPEC-CAPTURE-TRANSPARENCY`, `DELIB-0835`,
`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`,
`DELIB-S327-TERM-DISAMBIGUATION-MECHANICAL-OWNER-DIRECTIVE`, and prior
artifact/managed-registry bridge records. A revision must run the search before
filing, cite the relevant records, and explain whether any prior NO-GO or
approval-packet decision constrains this extension.

### F2 - Narrative Path Set Omits Active Control Surfaces

Slice A's proposed path set includes `.claude/rules/*.md`,
`memory/work_list.md`, selected `memory/*.md`, and `CLAUDE*.md`, but it omits
`AGENTS.md`. That file is an active Codex-facing instruction surface in this
workspace; `config/governance/protected-artifact-inventory-drift.toml` already
classifies `AGENTS.md` with `.claude/rules/**` and `CLAUDE.md` under
`role-and-governance-rules`, and `config/agent-control/REVIEW-MODE-SETUP.md`
uses `AGENTS.md` for review-mode setup. A narrative-artifact approval gate that
excludes `AGENTS.md` leaves one of the same class of active instruction
surfaces unprotected.

### F3 - Proposed Write Gate Does Not Account For Codex Hook Parity

The proposal frames the failure as "agents can edit canonical narrative
artifacts" but Slice A's enforcement path is a Claude `Write|Edit` hook (or a
sibling hook) plus template parity. That does not hard-block Codex
`apply_patch` or other Codex filesystem edits in this Windows harness.
`.claude/rules/acting-prime-builder.md` states that `.codex/hooks.json` must
not be represented as a live Windows interception boundary while Codex hooks
remain disabled on Windows, and the verified `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
test pins that behavior. A revised proposal must either:

1. Scope Slice A honestly as Claude-hook enforcement plus later pre-commit
   defense, or
2. Add a Codex-specific enforceable path and tests that do not claim disabled
   Windows Codex hooks as live blocking controls.

Without this correction, Slice A's acceptance criterion "Writes/Edits to
narrative artifacts without an approval packet are hard-blocked" overclaims
coverage.

### F4 - AskUserQuestion Decision-Class Mechanism Is Underspecified

Slice B says the agent will declare a structured `decision_class` annotation
on `AskUserQuestion`, but the proposal does not define an actual hook-observable
transport. Current hooks parse existing transcript/tool payload shapes for
`AskUserQuestion`; there is no cited schema support for an added metadata field.
The proposal acknowledges this question later, but the implementation scope and
tests should be revised to choose a concrete transport before GO, or defer
Slice B into an investigation spike instead of an implementation slice.

## Answers To Prime Questions

1. Do not merge Slice A and Slice B as currently written. Slice A can be first,
   but only after it accurately scopes Claude-vs-Codex enforcement and includes
   all active narrative instruction surfaces.
2. `MEMORY.md` and `memory/*.md` should not be broadly gated in the first hard
   blocking slice. Start with canonical instruction/governance surfaces
   (`.claude/rules/*.md`, `AGENTS.md`, `CLAUDE*.md`, `memory/work_list.md`)
   and treat broader operational memory as a separate decision because it is a
   high-churn notepad tier.
3. Use a side-channel only if it is machine-observable in the transcript/hook
   payload and regression-tested. Do not assume the `AskUserQuestion` tool
   schema can be extended without proving that capability.
4. Retiring `feedback_surface_artifact_owner_contradictions.md` should be an
   explicit owner-AUQ moment after structural enforcement has run cleanly.

## Evidence Checked

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-narrative-artifact-approval-extension-001` passed with no missing required/advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-narrative-artifact-approval-extension-001` exited 0 with 0 blocking gaps.
- `python -m groundtruth_kb secrets scan --paths bridge/gtkb-narrative-artifact-approval-extension-001-001.md --json --fail-on=` returned `finding_count: 0`.
- Deliberation searches found relevant prior records not cited in the proposal.
- `config/governance/protected-artifact-inventory-drift.toml` includes `AGENTS.md` in the same protected role/governance rule family as `.claude/rules/**` and `CLAUDE.md`.
- `.claude/rules/acting-prime-builder.md` states `.codex/hooks.json` must not be represented as a live Windows interception boundary while Codex hooks remain disabled.

## Required Revision

File a revised proposal that:

1. Runs and cites the required deliberation search.
2. Includes `AGENTS.md` or explicitly justifies excluding it despite its active
   Codex instruction role.
3. Separates Claude hook enforcement, Codex fallback/parity, and pre-commit
   enforcement claims so no slice overstates what it can block.
4. Chooses a concrete, testable transport for `decision_class`, or scopes Slice
   B as an investigation before implementation.
