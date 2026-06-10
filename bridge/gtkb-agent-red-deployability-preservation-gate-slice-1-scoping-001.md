# Implementation Proposal - Agent Red Deployability and Maintainability Preservation Gate (Slice 1: Scoping)

bridge_kind: prime_proposal
Document: gtkb-agent-red-deployability-preservation-gate-slice-1-scoping
Version: 001
Status: NEW
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Source: WI-3248 (P0; project AGENT-RED-RELEASE-READINESS; origin hygiene; source_spec_id GOV-ARTIFACT-ORIENTED-GOVERNANCE-001)
Recommended commit type: docs
target_paths: ["bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md"]

## Summary

This Slice 1 proposal is a **scoping document only**. It defines:

1. What the GT-KB-side "Agent Red deployability and maintainability preservation gate" means.
2. The catalog of GT-KB-side gate predicates that, taken together, constitute the preservation gate.
3. The structure of a future predicate registry under `config/governance/` plus a runner under `scripts/`.
4. The explicit project-boundary rule: every gate predicate **reads** Agent Red-related state that already lives inside `E:\GT-KB` (CI evidence captured under GT-KB control, deliberation archive records, MemBase rows, release-readiness markdown), and produces deployability / maintainability boolean outputs. **No Agent Red repository mutation is in scope** for this slice or any downstream implementation slice authorized by this scoping document.

No implementation code, no config files, no Agent Red-repo interaction. Slice 1 lands one bridge proposal artifact under `bridge/`; implementation slices (registry schema, predicate runner, doctor integration, predicate population) are downstream bridge threads authorized one-by-one after this scoping VERIFIED.

## Project Boundary Clarification

This proposal explicitly honors the Agent Red separate-project boundary as recorded in `.claude/rules/acting-prime-builder.md` § "Agent Red Separate-Project Boundary":

> Owner correction 2026-05-04 supersedes the prior Agent Red conformance framing for current GT-KB work: Agent Red is not part of GT-KB. It is a separate project whose repository is `https://github.com/mike-remakerdigital/agent-red`.

Consequences enforced by this proposal:

- `target_paths` contains exactly one entry: the bridge proposal file itself, which is `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md` (within `E:\GT-KB\bridge\`).
- No Agent Red repository clone, fetch, write, push, tag, or branch operation is in scope. No Agent Red source file is read or modified.
- All gate predicates defined in the catalog below operate on **GT-KB-side state**: MemBase rows owned by GT-KB, GT-KB-owned CI evidence files, GT-KB-owned deliberation archive records, GT-KB-owned release-readiness markdown, GT-KB doctor surfaces. CI evidence about Agent Red builds is harvested into GT-KB-side files under owner-approved bridge threads; the predicates consume those harvested files, not the live Agent Red repo.
- The GT-KB-side `scripts/release_candidate_gate.py` (which currently references Agent Red local-build checks) is observed as **pre-existing** infrastructure. This proposal does NOT modify it. Downstream slices may modify its consumption pattern (e.g., emit predicate inputs alongside its current output), but that work requires its own bridge thread and is not authorized here.
- `.claude/rules/project-root-boundary.md` § Directive applies: all active GT-KB files are within `E:\GT-KB`; Agent Red files are not GT-KB files and must not be treated as live GT-KB artifacts.

If any downstream implementation slice attempts to extend `target_paths` outside `E:\GT-KB`, it is a NO-GO under `.claude/rules/file-bridge-protocol.md` § "Mandatory Root Boundary Gate" until revised.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - live `bridge/INDEX.md` remains the authoritative bridge queue; this proposal files governed scoping work for Loyal Opposition review before any predicate implementation begins.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites every relevant governing specification, rule, and prior-decision record that constrains a GT-KB-side preservation gate scoped against a separate project.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification of this scoping slice requires that the proposal's acceptance criteria are demonstrably satisfied by inspection; no source code is added in Slice 1, so the spec-to-test mapping covers acceptance-criteria checks, not runtime tests.
- GOV-STANDING-BACKLOG-001 - WI-3248 is a P0 standing-backlog item in project AGENT-RED-RELEASE-READINESS; this proposal advances that work item through Slice 1 scoping without making it a bulk operation against the backlog.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - GT-KB platform/application placement rules apply; this scoping document is GT-KB-platform-scoped and all paths are inside `E:\GT-KB`.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the preservation gate is structured as a durable, traceable artifact (predicate registry plus runner plus doctor surface) rather than transient session prose.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - WI-3248's `source_spec_id`; concrete deployability/maintainability requirements, decisions, predicates, and gate evidence must be preserved as durable artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the predicate runner's canonical outcomes (PASS / WARN / FAIL) follow the lifecycle-triggers pattern; downstream consumers (release-readiness, doctor, dashboard) read the runner output via standard adapter shape.
- GOV-ARTIFACT-APPROVAL-001 - any MemBase spec or governance artifact created by a downstream implementation slice (e.g., the per-predicate SPECs) requires formal-artifact-approval packets; this Slice 1 creates no MemBase records.
- `.claude/rules/acting-prime-builder.md` § "Agent Red Separate-Project Boundary" - the authoritative statement of the boundary this proposal enforces.
- `.claude/rules/project-root-boundary.md` - the active-root and applications-directory constraint; all target_paths comply.
- `.claude/rules/file-bridge-protocol.md` - bridge protocol authority; including the Mandatory Root Boundary Gate, Mandatory Specification Linkage Gate, Mandatory Owner Decisions / Input Section Gate, and Conventional Commits Type Discipline (this proposal recommends `docs:` because it adds no executable code).
- `.claude/rules/codex-review-gate.md` - Loyal Opposition gating obligations; this proposal includes all required sections for review.

## Prior Deliberations

- 2026-05-04 owner correction (recorded in `.claude/rules/acting-prime-builder.md`): Agent Red is not part of GT-KB; Agent Red files must not be live GT-KB artifacts. This scoping proposal is authored under that correction.
- `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` (2026-05-03 S330): canonical Agent Red repo migration prerequisite remains a release blocker; v0.7.0-rc1 tag authorization is gated on canonical migration + canonical CI binding. The preservation gate must respect this and treat the canonical-vs-de-facto-repo dual listing in the canonical-terminology glossary (Agent Red entry) as the operative boundary state.
- `DELIB-S330-ISOLATION-017-SLICE8-5-PYTHON-TESTS-WAIVER` and the in-flight Slice 8.5 / Slice 8.6 CI work (`bridge/gtkb-isolation-017-slice-8-5-ci-green-*`, `bridge/gtkb-isolation-017-slice-8-6-ci-failure-triage-*`): pre-existing GT-KB-side bridge threads that capture Agent Red CI evidence under owner-approved waivers. The preservation gate's deployability predicates consume the artifacts produced by these threads (CI evidence files, waiver DELIB IDs, release-readiness markdown rows); the gate does NOT re-fetch live CI state from the Agent Red repo.
- `bridge/agent-red-repo-migration-001-005.md` (2026-05-06 VERIFIED inventory): read-only inventory pattern established; Agent Red repository mutation explicitly out of scope. This preservation-gate proposal inherits that pattern: GT-KB-side reads only.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (S312 owner directive): repetitive plumbing belongs in services. The preservation gate is a deterministic measurement service; per-session ad hoc "is Agent Red still deployable?" checks are exactly the friction this principle targets.
- `DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE`: improvement opportunities flow to MemBase backlog. WI-3248's existence in MemBase under project AGENT-RED-RELEASE-READINESS is the canonical instance of this directive applied to the preservation-gate concern.
- `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` P0 elevation (2026-05-05): groups Agent Red Tier A credential-scan adoption as a related concern. The preservation gate's maintainability predicates will eventually include a "credential-scan coverage current?" predicate that consumes this workstream's outputs; in Slice 1 it is named in the catalog but not implemented.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: Owner direction "Please parallelize work and start as many priority backlog projects as possible". This authorizes batch filing of priority backlog proposals (per S350 standing parallelization directive); each per-proposal Codex GO is still required before any implementation step. WI-3248 is P0 (priority backlog), so this proposal is in scope of that direction.
- 2026-05-04 + maintained through 2026-05-14: Owner has separately and consistently maintained the Agent Red boundary correction throughout the period from 2026-05-04 onward. This proposal's scope (GT-KB-side gate predicates only; no Agent Red repo mutation) is the only scope compatible with that maintained correction.
- WI-3248's P0 priority and `source_spec_id = GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` together authorize the scoping work to proceed: the work item is owner-approved by virtue of its presence in MemBase at P0; the source spec authorizes artifact-oriented preservation of the deployability/maintainability concern.
- No additional AskUserQuestion is required for this Slice 1 scoping artifact. Downstream implementation slices that create MemBase SPECs, modify `scripts/release_candidate_gate.py`, add doctor checks, or wire predicates into release-readiness output will each require their own bridge GO and may require formal-artifact-approval packets per `GOV-ARTIFACT-APPROVAL-001`.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is **not** a bulk operation against the standing backlog. It advances exactly one work item (WI-3248) through one slice (Slice 1: Scoping). The scope is limited to:

- Authoring one bridge proposal file (this file) and one verdict file (the future Codex review verdict).
- Producing one durable artifact: the scoping document at `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md`.

The proposal does not retire, supersede, batch-update, batch-create, or reorder any standing-backlog work items. The deployability/maintainability **inventory** described below in the Gate Predicate Catalog is a descriptive enumeration of GT-KB-side predicates that downstream slices will register; it is not a bulk-create operation against MemBase. No MemBase mutation is in scope for Slice 1. Per `GOV-STANDING-BACKLOG-001` clause-scope semantics, the standing backlog evidence required is the single WI-3248 row plus its parent project AGENT-RED-RELEASE-READINESS, both of which already exist; no inventory mutation is performed.

The formal-artifact-approval discipline applies to downstream slices (where MemBase SPEC rows or governance rows are created), not to this Slice 1 scoping artifact. No formal-artifact-approval packet is created or required for the proposal file itself.

## Requirement Sufficiency

Existing requirements sufficient.

WI-3248's `description` and `failure_description` together specify the requirement clearly: GT-KB must verify Agent Red remains deployable, maintainable, and enhanceable before any irreversible Agent Red migration / cutover / extraction / deletion / restructuring work proceeds. The verification surface is enumerated in the WI description (Agent Red release-candidate path, Python 3.12 gate, frontend/admin/widget build surfaces, Docker/container build surfaces, deployment workflow inputs/artifacts, safe maintain/enhance smoke path) and is sufficient to drive the gate-predicate catalog in this Slice 1 scoping document. No new requirements need to be captured before this scoping artifact can be reviewed.

Downstream implementation slices may discover that specific gate predicates need finer-grained specifications; those will be captured then as new specs through the standard formal-artifact-approval-packet workflow.

## Gate Predicate Catalog

Each predicate is a GT-KB-side boolean (or trivalent PASS / WARN / FAIL) check that consumes GT-KB-owned state and emits a structured result. No predicate reads the live Agent Red repository. The catalog is presented here for Slice 1 review and will be formalized as a registry under `config/governance/` in a downstream implementation slice.

### Deployability predicates

DEPL-1. **Agent Red release-candidate evidence current**. Reads the most recent GT-KB-side CI evidence file (currently produced under `bridge/gtkb-isolation-017-slice-8-5-ci-green-*` and successor threads). Result: PASS if the most recent evidence file is within an owner-configured staleness window AND records all-required-workflows green (per Slice 8.6 required-workflow inventory). WARN if within window but missing one or more workflows. FAIL if absent or older than window.

DEPL-2. **Python 3.12 gate evidence present**. Reads the CI evidence file's recorded Python version markers (captured at evidence-harvest time, not re-fetched). Result: PASS if 3.12 markers present and pass. WARN if markers present but a waiver DELIB applies. FAIL if absent or failing without waiver.

DEPL-3. **Frontend / admin / widget build surfaces covered**. Reads the CI evidence file's recorded build-job results. Result: PASS if all three surfaces present and green. WARN if one or more under owner-approved waiver. FAIL otherwise.

DEPL-4. **Docker / container build surfaces covered**. Reads the CI evidence file's recorded container-build and security-scan job results. Result: PASS if all green or under cited waiver DELIB. WARN with cited waiver. FAIL otherwise.

DEPL-5. **Deployment workflow inputs / artifacts inventoried**. Reads a GT-KB-side inventory artifact (produced by the existing `bridge/agent-red-repo-migration-001-*` inventory pattern). Result: PASS if inventory current and complete. WARN if inventory stale. FAIL if absent.

DEPL-6. **Canonical Agent Red repo migration status known**. Reads `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` status from MemBase and the canonical-terminology glossary's Agent Red entry. Result: PASS if migration recorded as complete. WARN during the documented dual-listing transient. FAIL if no record exists.

### Maintainability predicates

MAINT-1. **Agent Red-related MemBase spec coverage current**. Reads MemBase for specs tagged or named with Agent Red scope (e.g., release-readiness, isolation-017 Slice 8.5/8.6 specs). Result: PASS if all such specs are at `implemented` or `verified` and have current assertions. WARN if at `specified`. FAIL if a verified spec's assertions are failing.

MAINT-2. **Deliberation Archive Agent Red boundary records present**. Searches DA for the boundary-correction deliberations (2026-05-04 owner correction, DELIB-S330 migration prerequisite, DELIB-S330 Slice 8.5/8.6 waivers). Result: PASS if all expected DELIB IDs resolve. WARN if one is missing. FAIL if multiple missing.

MAINT-3. **Harness parity green for Agent Red-touching skills**. Reads doctor's harness-parity output (existing surface). Result: PASS / WARN / FAIL passed through from doctor.

MAINT-4. **Dev environment inventory current**. Reads a GT-KB-side dev-environment inventory artifact (produced under an existing inventory workstream, not authored here). Result: PASS / WARN / FAIL based on inventory recency and completeness.

MAINT-5. **Credential-scan coverage current**. Reads `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` Slice 1+2 outputs (current-tracked-scan and all-local-refs-scan reports). Result: PASS if both reports recent and clean. WARN if recent with cited candidate-high count under triage. FAIL if absent or with verified-provider findings.

MAINT-6. **Supersession tracking complete for Agent Red-related work items**. Reads MemBase work_items for project AGENT-RED-RELEASE-READINESS; checks that completed items carry valid `superseded_by` or `completion_evidence`. Result: PASS / WARN / FAIL based on field population. (WI-3248 itself is included in this predicate's input set.)

MAINT-7. **Doctor checks for Agent Red dependency green**. Reads doctor surfaces that already exist (e.g., bridge-dispatch-liveness, role-set-topology-consistency, harness-parity, scaffold-drift). Result: PASS / WARN / FAIL passed through.

### Composite output

The runner emits one composite result (`deployable_and_maintainable: bool`) plus the per-predicate detail. The composite is FAIL if any predicate is FAIL; WARN if any predicate is WARN and none FAIL; PASS only if all predicates PASS. The composite output is consumed by release-readiness, doctor, and dashboard surfaces in downstream slices (each via its own bridge thread).

## Implementation Plan

### Slice 1 (this proposal)

1. Author this scoping document at `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md`. **DONE** by virtue of this proposal being filed.
2. Loyal Opposition reviews the scoping document. NO-GO surfaces missing predicates or boundary violations; GO authorizes proceeding to Slice 2.

### Downstream slices (NOT authorized by this Slice 1)

Each requires its own bridge proposal, its own Loyal Opposition GO, and its own implementation/verification cycle:

- **Slice 2: Predicate registry schema.** Add `config/governance/agent-red-preservation-predicates.toml` with one `[[predicate]]` block per catalog entry above. Add a JSON-Schema-style validation test under `platform_tests/`. No runtime predicate evaluation yet; just the registry structure and validation.
- **Slice 3: Predicate runner.** Add `scripts/agent_red_preservation_gate.py` that reads the registry, dispatches per-predicate handlers, and emits structured output (JSON + markdown summary) to `.gtkb-state/preservation-gate/<run_id>/`. Each handler is a small read-only function consuming GT-KB-side state per the catalog. No mutation.
- **Slice 4: Per-predicate SPEC creation.** Create MemBase SPECs for each predicate via formal-artifact-approval packets, encoding the predicate's pass/fail criteria as machine-checkable assertions.
- **Slice 5: Doctor integration.** Add a doctor check (`_check_agent_red_preservation_gate`) that runs the runner and reports composite PASS/WARN/FAIL.
- **Slice 6: Release-readiness wiring.** Have `scripts/release_candidate_gate.py` (or the GT-KB release-readiness surface, depending on owner direction) consume the runner output as a pre-release gate input. (This is the only slice that touches `scripts/release_candidate_gate.py`; it is the natural integration point but is explicitly out of scope here.)

No downstream slice introduces Agent Red repository interaction. All slices keep target_paths within `E:\GT-KB`.

## Test Mapping

Slice 1 is a scoping artifact; it adds no source code. The spec-to-test mapping for this slice covers acceptance criteria via inspection:

| Linked specification | Slice 1 evidence |
|----------------------|------------------|
| GOV-FILE-BRIDGE-AUTHORITY-001 | Proposal is filed via the bridge protocol; INDEX.md update is a separate step authored by the bridge protocol harness, not this proposal. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | This proposal's `Specification Links` section cites every relevant governing spec; Codex inspects for omissions during review. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This proposal's `Test Mapping`, `Acceptance Criteria`, and `Verification Plan` sections define how downstream verification will work; Slice 1 itself adds no executable test. |
| GOV-STANDING-BACKLOG-001 | WI-3248 already exists in MemBase as P0 in project AGENT-RED-RELEASE-READINESS; this proposal advances it through Slice 1 without bulk operation. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 / `.claude/rules/project-root-boundary.md` | `target_paths` contains exactly one path, inside `E:\GT-KB\bridge\`; no Agent Red repo path is referenced. |
| `.claude/rules/acting-prime-builder.md` § "Agent Red Separate-Project Boundary" | Proposal's "Project Boundary Clarification" section explicitly cites and enforces this rule. |

Downstream slices add executable tests (registry validation, runner unit tests, doctor-check tests, integration smoke tests) under their own bridge threads.

## Risk and Rollback

**Risk: scoping document drifts from implementation.** Mitigation: each downstream slice cites this scoping document as its source-of-truth predicate catalog; deviations require an updated scoping bridge thread, not silent slice-level drift.

**Risk: gate predicates become a maintenance burden.** Mitigation: the catalog is explicitly small (13 predicates total) and biased toward consuming pre-existing GT-KB-side state rather than introducing new harvest mechanisms. The downstream runner is a deterministic service per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, not a per-session ceremony.

**Risk: predicate failures cause false alarms during normal Agent Red work.** Mitigation: WARN is a first-class state in the trivalent model; owner-approved waivers (cited via DELIB IDs) downgrade FAIL to WARN with audit trail. The composite output is informational in Slices 1-5 and becomes release-gate-blocking only when Slice 6 explicitly wires it in.

**Rollback for Slice 1:** delete `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md` from disk (and from `bridge/INDEX.md` once entered). No other GT-KB state is changed. Bridge files are append-only by protocol, so rollback in practice is "supersede with a new scoping document" rather than physical deletion; either path preserves audit trail.

## Acceptance Criteria

A1. Proposal file exists at `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md` with all mandatory sections present.

A2. `target_paths` contains exactly one entry: this proposal file. No path outside `E:\GT-KB` appears.

A3. "Project Boundary Clarification" section explicitly cites `.claude/rules/acting-prime-builder.md` § "Agent Red Separate-Project Boundary" and states no Agent Red repo mutation is in scope.

A4. Gate Predicate Catalog enumerates at least the deployability surfaces named in WI-3248's `description` field (release-candidate path, Python 3.12 gate, frontend/admin/widget builds, Docker/container builds, deployment workflow inputs/artifacts, safe maintain/enhance smoke) and at least one maintainability predicate per WI-3248's "maintainable" framing.

A5. Implementation Plan enumerates downstream slices and explicitly states none are authorized by this Slice 1 GO.

A6. Applicability Preflight passes with `preflight_passed: true` and `missing_required_specs: []`.

A7. Clause Preflight exits 0 (advisory mode in Slice 1 of `gtkb-adr-dcl-clause-test-enforcement`; this proposal does not introduce blocking-clause violations).

## Verification Plan

Slice 1 verification is by inspection of the proposal file against the Acceptance Criteria:

1. `git ls-files bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-001.md` confirms file presence (after staging).
2. Open the proposal file; grep for the section headings listed in this proposal's "mandatory sections" enumeration. Each must appear exactly once.
3. Parse `target_paths` from the front matter; confirm exactly one entry, equal to the proposal file path, within `E:\GT-KB\bridge\`.
4. Grep the proposal text for "`.claude/rules/acting-prime-builder.md`" and "Agent Red Separate-Project Boundary"; both must appear in the Project Boundary Clarification section.
5. Count predicate entries in the Gate Predicate Catalog; confirm the deployability surfaces named in WI-3248's description are each covered by at least one DEPL-* entry, and maintainability is covered by at least one MAINT-* entry.
6. Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate-slice-1-scoping` and inspect the JSON output; record `packet_hash` and confirm `preflight_passed: true`.
7. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate-slice-1-scoping`; expect exit 0.

Loyal Opposition's VERIFIED verdict for Slice 1 should confirm all seven checks pass by inspection.

## Applicability Preflight

Run prior to filing INDEX entry; result embedded here for self-check evidence:

```
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate-slice-1-scoping
```

Expected result: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. The proposal triggers the following cross-cutting rules per `config/governance/spec-applicability.toml`:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (path: `bridge/**`; doc match: `*`) - cited.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (content: "implementation proposal", "Specification Links", "bridge proposal") - cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (content: "VERIFIED", "verification", "spec-to-test") - cited.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (content: "Agent Red", "applications/", "project root boundary") - cited.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (content: "owner decision", "requirement", "specification", "ADR", "DCL", "work item", "backlog") - advisory, cited.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (content: "artifact", "traceability", "deliberation") - advisory, cited.

The preflight result with `packet_hash` will be recorded by Loyal Opposition's verdict file per the standard review protocol.

End of proposal.
