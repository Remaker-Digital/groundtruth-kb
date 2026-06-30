NEW

# WI-4907 Routed Advisory Placeholder Triage

bridge_kind: prime_proposal
Document: gtkb-wi4907-routed-advisory-placeholder-triage
Version: 001
Author: Prime Builder (Codex harness A)
Date: 2026-06-30 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: auto-builder-2026-06-30T01-05Z-codex-A
author_model: gpt-5-codex
author_model_version: 2026-06
author_model_configuration: Codex desktop Auto-builder automation; approval_policy=never; workspace=E:\GT-KB

Project Authorization: PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29
Project: PROJECT-HARNESS-PARITY-PHASE-2
Work Item: WI-4907

target_paths: ["groundtruth.db", "bridge/gtkb-wi4907-routed-advisory-placeholder-triage-*.md"]

implementation_scope: governance_record, project_metadata, backlog_hygiene
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

Triage `WI-4907` by auditing generic routed-advisory backlog rows that mention
harnesses, parity, Ollama, Antigravity, Cursor, Codex, Claude, dispatcher, or
role behavior. Each concrete finding will be classified as one of: promote into
an executable Harness Parity Phase 2 work item, attach to the Phase 2 project if
already represented, retire/no-op as stale or duplicate, or explicitly leave
outside Phase 2 with evidence.

The implementation is intentionally non-source. It may update MemBase backlog
and project metadata through governed `gt backlog` / `gt projects` commands and
will file a post-implementation report. It will not edit source, tests, hooks,
dispatcher configuration, provider credentials, production settings, or
harness-local scratchpads.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal, any later implementation
  report, and verification verdict use the numbered bridge file chain as the
  governed workflow record.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the backlog triage
  work cites the governing backlog, project-authorization, and harness parity
  specifications before any MemBase mutation.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries
  the active Phase 2 project, PAUTH, work item, and target-path metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the implementation report
  will map each verification command to the governing specification it proves.
- `GOV-STANDING-BACKLOG-001` - backlog rows and project memberships are the
  authoritative surfaces being reconciled.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - PAUTH
  `PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` authorizes
  project metadata and governance-record work for current Phase 2 members,
  including `WI-4907`.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - routed advisory rows that describe
  harness capability, parity, or role-behavior gaps must be promoted into
  explicit, enforceable parity work or waived with evidence.
- `ADR-DISPATCHER-ARCHITECTURE-001` - dispatcher and harness-routing findings
  must remain attached to the governed dispatcher/parity work graph rather than
  unstructured advisory placeholders.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - concrete advisory findings that have
  crossed into backlog-worthy work must be preserved as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the implementation preserves the
  decision and evidence trail for promoted or retired advisory findings.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - stale, duplicate, promoted, and
  deferred advisory rows receive explicit lifecycle states instead of being
  left as ambiguous placeholders.

## Prior Deliberations

- `DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` - owner directive
  and PAUTH source for the release-blocking Harness Parity Phase 2 scope.
- `DELIB-20266426` - VERIFIED WI-4899 baseline matrix; this triage uses the
  matrix as evidence for whether a routed advisory is already represented.
- `DELIB-20266425` - GO for WI-4900 baseline evaluator; this triage complements
  the evaluator by turning generic placeholders into concrete work or evidence.
- `DELIB-20266462` - VERIFIED WI-4902 projection registry repair; this triage
  avoids duplicating already-closed projection gaps.
- `DELIB-20266458` and `DELIB-20266459` - GO verdicts for WI-4901 release-waiver
  closure; this triage preserves the same distinction between real gaps and
  explicit waivers.
- `DELIB-S20260626-PARITY-IMPL-AUTHORIZATION` - earlier owner authorization for
  cross-harness parity work; Phase 2 is the current bounded continuation.

## Owner Decisions / Input

No new owner decision is required for this proposal. The active owner directive
`DELIB-20260629-HARNESS-PARITY-PHASE-2-OWNER-DIRECTIVE` and PAUTH
`PAUTH-PROJECT-HARNESS-PARITY-PHASE-2-IMPLEMENTATION-2026-06-29` explicitly
include `WI-4907`, project metadata, governance records, and documentation
work. This proposal only asks Loyal Opposition to review the bounded triage
plan before any MemBase mutation.

## Requirement Sufficiency

Existing requirements sufficient. `WI-4907` defines the accepted outcome, the
active Phase 2 PAUTH authorizes the work item and mutation class, and
`GOV-STANDING-BACKLOG-001`, `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`,
`DCL-CROSS-HARNESS-ENFORCEMENT-001`, and the artifact-oriented governance
records define the required handling for promoted, retired, duplicate, and
out-of-scope advisory rows. No source, credential, deployment, or new formal
specification decision is needed before implementation.

## Spec-Derived Verification Plan

Specification-Derived Verification in the implementation report will include:

```text
gt backlog list --json --priority P0 --priority P1 --priority P2 --resolution-status open --limit 1000
gt backlog list --json --stage backlogged --priority P0 --priority P1 --priority P2 --limit 1000
gt projects show PROJECT-HARNESS-PARITY-PHASE-2 --json
gt projects authorizations PROJECT-HARNESS-PARITY-PHASE-2 --json
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-wi4907-routed-advisory-placeholder-triage
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-wi4907-routed-advisory-placeholder-triage
python -m pytest <focused verification tests, if any code/tests are touched> -q --tb=short
```

Expected results:

- `GOV-STANDING-BACKLOG-001`: every harness-related routed-advisory placeholder
  found in the P0/P1/P2 open/backlogged set is classified with evidence.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`: every MemBase mutation is
  within `WI-4907` and the active Phase 2 PAUTH.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001`: concrete harness parity gaps are
  promoted, attached, or waived instead of remaining generic placeholders.
- `GOV-FILE-BRIDGE-AUTHORITY-001` and linkage specs: bridge preflights pass
  before implementation and on the final report.

## Risk / Rollback

Risk: advisory placeholders can be misclassified, especially when one generic
row overlaps several harness parity threads. Mitigation: use live `gt backlog`
and `gt projects` output as evidence, classify one row at a time, and include
before/after row IDs in the implementation report.

Rollback: the implementation is limited to MemBase backlog/project metadata and
the bridge thread. If a classification is wrong, a follow-up governed backlog
update can supersede or restore the affected row state without reverting source
or configuration files.

## Bridge Filing

This proposal is filed under the bridge directory as the next status-bearing numbered
bridge file for `gtkb-wi4907-routed-advisory-placeholder-triage`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`chore:` - backlog/project governance hygiene, with no source or test
implementation claimed by this proposal.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
