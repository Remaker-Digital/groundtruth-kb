REVISED

# Implementation Proposal - Agent Red Deployability and Maintainability Preservation Gate (Slice 1: Scoping)

bridge_kind: implementation_proposal
Document: gtkb-agent-red-deployability-preservation-gate-slice-1-scoping
Version: 003
Status: REVISED
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+
Source: WI-3248 (P0; origin hygiene; source_spec_id GOV-ARTIFACT-ORIENTED-GOVERNANCE-001)
Recommended commit type: docs

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH-P0-DEPLOYABILITY-GATE
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: WI-3248

target_paths: ["bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-003.md"]

## Revision Notes (-003 vs -001)

This `-003` revises `-001` to address the two P1 findings in the `-002` NO-GO.
There is no scope change: this remains a Slice 1 scoping document only, with a
single `target_paths` entry (the proposal file itself).

| `-002` finding | How `-003` addresses it |
|----------------|--------------------------|
| P1 - The proposal omits the formal `SPEC-DEPLOY-*` family that directly governs WI-3248 | The `## Specification Links` section below now cites all seven `SPEC-DEPLOY-*` specifications (`SPEC-DEPLOY-SOURCE-BUILD-001`, `-RC-GATE-PYTHON-3-12-001`, `-CONTAINER-BUILD-001`, `-FRONTEND-BUNDLES-001`, `-WORKFLOW-INPUTS-001`, `-MAINTAIN-ENHANCE-PATH-001`, `-EVIDENCE-FRESHNESS-001`) as first-class governing specifications. A new `## Spec-to-Predicate Matrix` section maps every `SPEC-DEPLOY-*` spec to the DEPL/MAINT predicate(s) that satisfy it, and a new predicate `DEPL-0` covers source-build evidence explicitly (closing the gap the NO-GO flagged). |
| P1 - The downstream predicate model is not reconciled with the formal deployability evidence contract | A new `## Reconciliation With the SPEC-DEPLOY Evidence Contract` section states explicitly that the GT-KB-side preservation gate is a **validator/wrapper over the existing `SPEC-DEPLOY-*` evidence**, NOT a replacement evidence surface. The runner consumes `SPEC-DEPLOY-*` proof evidence at the spec-defined path `.gtkb-state/deployability-evidence/<application-id>/<proof-id>-<ulid>.json` and honors the `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` 30-day window and per-proof manifest overrides. The composite-result file under `.gtkb-state/preservation-gate/<run_id>/` is reframed as a derived, regenerable *report* artifact (not authoritative evidence); it does not split or duplicate the canonical evidence store. |

Both mandatory preflights were re-run on this `-003` content; results are embedded
in `## Applicability Preflight` and `## Clause Applicability` below.

## Supersession / Filing Note

`-001` (NEW) and `-002` (NO-GO) are preserved unchanged on disk per the
append-only bridge audit-trail invariant. This `-003` is filed as the `REVISED`
version of the same thread; `bridge/INDEX.md` records the latest status as
`REVISED`.

## Summary

This Slice 1 proposal is a **scoping document only**. It defines:

1. What the GT-KB-side "Agent Red deployability and maintainability preservation gate" means.
2. The catalog of GT-KB-side gate predicates that, taken together, constitute the preservation gate.
3. The structure of a future predicate registry under `config/governance/` plus a runner under `scripts/`.
4. The explicit project-boundary rule: every gate predicate **reads** Agent Red-related state that already lives inside `E:\GT-KB` (CI evidence captured under GT-KB control, deliberation archive records, MemBase rows, release-readiness markdown, and the `SPEC-DEPLOY-*` deployability-evidence proof files), and produces deployability / maintainability boolean outputs. **No Agent Red repository mutation is in scope** for this slice or any downstream implementation slice authorized by this scoping document.

No implementation code, no config files, no Agent Red-repo interaction. Slice 1 lands one bridge proposal artifact under `bridge/`; implementation slices (registry schema, predicate runner, doctor integration, predicate population) are downstream bridge threads authorized one-by-one after this scoping VERIFIED.

## Project Boundary Clarification

This proposal explicitly honors the Agent Red separate-project boundary as recorded in `.claude/rules/acting-prime-builder.md` § "Agent Red Separate-Project Boundary":

> Owner correction 2026-05-04 supersedes the prior Agent Red conformance framing for current GT-KB work: Agent Red is not part of GT-KB. It is a separate project whose repository is `https://github.com/mike-remakerdigital/agent-red`.

Consequences enforced by this proposal:

- `target_paths` contains exactly one entry: the bridge proposal file itself, which is `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-003.md` (within `E:\GT-KB\bridge\`).
- No Agent Red repository clone, fetch, write, push, tag, or branch operation is in scope. No Agent Red source file is read or modified.
- All gate predicates defined in the catalog below operate on **GT-KB-side state**: MemBase rows owned by GT-KB, GT-KB-owned CI evidence files, GT-KB-owned deliberation archive records, GT-KB-owned release-readiness markdown, the `SPEC-DEPLOY-*` deployability-evidence proof files written under GT-KB control at `.gtkb-state/deployability-evidence/`, and GT-KB doctor surfaces. CI evidence about Agent Red builds is harvested into GT-KB-side files under owner-approved bridge threads; the predicates consume those harvested files, not the live Agent Red repo.
- The GT-KB-side `scripts/release_candidate_gate.py` (which currently references Agent Red local-build checks) is observed as **pre-existing** infrastructure. This proposal does NOT modify it. Downstream slices may modify its consumption pattern (e.g., emit predicate inputs alongside its current output), but that work requires its own bridge thread and is not authorized here.
- `.claude/rules/project-root-boundary.md` § Directive applies: all active GT-KB files are within `E:\GT-KB`; Agent Red files are not GT-KB files and must not be treated as live GT-KB artifacts.

If any downstream implementation slice attempts to extend `target_paths` outside `E:\GT-KB`, it is a NO-GO under `.claude/rules/file-bridge-protocol.md` § "Mandatory Root Boundary Gate" until revised.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 - live `bridge/INDEX.md` remains the authoritative bridge queue; this proposal files governed scoping work for Loyal Opposition review before any predicate implementation begins.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 - this proposal cites every relevant governing specification, rule, and prior-decision record that constrains a GT-KB-side preservation gate scoped against a separate project.
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 - verification of this scoping slice requires that the proposal's acceptance criteria are demonstrably satisfied by inspection; no source code is added in Slice 1, so the spec-to-test mapping covers acceptance-criteria checks, not runtime tests.
- GOV-STANDING-BACKLOG-001 - WI-3248 is a P0 standing-backlog item; this proposal advances that work item through Slice 1 scoping without making it a bulk operation against the backlog.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 - GT-KB platform/application placement rules apply; this scoping document is GT-KB-platform-scoped and all paths are inside `E:\GT-KB`.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 - the preservation gate is structured as a durable, traceable artifact (predicate registry plus runner plus doctor surface) rather than transient session prose.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 - WI-3248's `source_spec_id`; concrete deployability/maintainability requirements, decisions, predicates, and gate evidence must be preserved as durable artifacts.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 - the predicate runner's canonical outcomes (PASS / WARN / FAIL) follow the lifecycle-triggers pattern; downstream consumers (release-readiness, doctor, dashboard) read the runner output via standard adapter shape.
- GOV-ARTIFACT-APPROVAL-001 - any MemBase spec or governance artifact created by a downstream implementation slice (e.g., the per-predicate SPECs) requires formal-artifact-approval packets; this Slice 1 creates no MemBase records.
- SPEC-DEPLOY-SOURCE-BUILD-001 - owner-approved deployability specification: the application source build must produce expected artifacts without errors from a clean checkout, against a `deployability_manifest.toml` artifact list. Directly governs predicate DEPL-0 and DEPL-1.
- SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001 - owner-approved deployability specification: the release-candidate gate must pass on Python 3.12 for Python-based application instances. Directly governs predicate DEPL-2.
- SPEC-DEPLOY-CONTAINER-BUILD-001 - owner-approved deployability specification: the container/Docker build path must produce an image with expected metadata. Directly governs predicate DEPL-4.
- SPEC-DEPLOY-FRONTEND-BUNDLES-001 - owner-approved deployability specification: frontend / admin / widget bundles must build to expected artifacts. Directly governs predicate DEPL-3.
- SPEC-DEPLOY-WORKFLOW-INPUTS-001 - owner-approved deployability specification: deployment workflow inputs and artifacts must be intact and discoverable from a clean checkout. Directly governs predicate DEPL-5.
- SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001 - owner-approved deployability specification: the maintain/enhance path (clone, edit, test, build, deploy-ready) must remain sane after GT-KB isolation work. Directly governs predicate MAINT-3.
- SPEC-DEPLOY-EVIDENCE-FRESHNESS-001 - owner-approved deployability specification: deployability evidence is timestamped at capture, stored at `.gtkb-state/deployability-evidence/<application-id>/<proof-id>-<ulid>.json`, has a default 30-day freshness window with per-proof manifest override, and stale evidence is treated as MISSING. This is the canonical evidence-storage and freshness contract the preservation-gate runner consumes; predicates DEPL-0 through DEPL-5 and the composite all honor it.
- `.claude/rules/acting-prime-builder.md` § "Agent Red Separate-Project Boundary" - the authoritative statement of the boundary this proposal enforces.
- `.claude/rules/project-root-boundary.md` - the active-root and applications-directory constraint; all target_paths comply.
- `.claude/rules/file-bridge-protocol.md` - bridge protocol authority; including the Mandatory Root Boundary Gate, Mandatory Specification Linkage Gate, Mandatory Owner Decisions / Input Section Gate, and Conventional Commits Type Discipline (this proposal recommends `docs:` because it adds no executable code).
- `.claude/rules/codex-review-gate.md` - Loyal Opposition gating obligations; this proposal includes all required sections for review.

## Prior Deliberations

- DELIB-0319 - earlier Agent Red release/deployability concern (hard release paths, hotfix isolation, staging/prod promotion, immutable release evidence). The preservation gate's deployability predicates inherit this concern; the SPEC-DEPLOY family is the formalization of it.
- DELIB-0327 - companion earlier Agent Red release/deployability deliberation cited alongside DELIB-0319 in the `-002` NO-GO; preserved here as governing prior-decision context for the deployability predicate catalog.
- DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE (2026-05-03 S330) - canonical Agent Red repo migration prerequisite remains a release blocker; v0.7.0-rc1 tag authorization is gated on canonical migration + canonical CI binding. The preservation gate must respect this and treat the canonical-vs-de-facto-repo dual listing in the canonical-terminology glossary (Agent Red entry) as the operative boundary state.
- DELIB-1748 - a prior Loyal Opposition NO-GO for Agent Red file migration work; confirms the pattern that Agent Red boundary and bridge preflight omissions remain blocking when governing artifacts are incomplete. This `-003` revision closes the analogous SPEC-DEPLOY linkage omission the `-002` NO-GO surfaced.
- DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE - boundary history for Agent Red placement/migration decisions; relevant background to the Project Boundary Clarification above.
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE (S312 owner directive) - repetitive plumbing belongs in services. The preservation gate is a deterministic measurement service; per-session ad hoc "is Agent Red still deployable?" checks are exactly the friction this principle targets.
- DELIB-S341-SELF-IMPROVEMENT-STANDING-DIRECTIVE - improvement opportunities flow to MemBase backlog. WI-3248's existence in MemBase is the canonical instance of this directive applied to the preservation-gate concern.

No prior deliberation waives the deployability specification-linkage requirement for this scoping proposal; this `-003` revision satisfies it.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: Owner direction "Please parallelize work and start as many priority backlog projects as possible". This authorizes batch filing of priority backlog proposals; each per-proposal Codex GO is still required before any implementation step. WI-3248 is P0 (priority backlog), so this proposal is in scope of that direction.
- WI-3248 is an active member of project `PROJECT-GTKB-ADOPTER-EXPERIENCE`, covered by the active project authorization `PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH-P0-DEPLOYABILITY-GATE` (owner-decision `DELIB-S350-BATCH6-P0P1-AUTHORIZATION`; authorization is active, unexpired, and explicitly includes `WI-3248` in its `included_work_item_ids`). This project authorization provides the owner-approval evidence for the bounded project scope; it does not replace the bridge GO or any formal-artifact-approval packet for downstream slices.
- 2026-05-04 + maintained through 2026-05-15: Owner has separately and consistently maintained the Agent Red boundary correction. This proposal's scope (GT-KB-side gate predicates only; no Agent Red repo mutation) is the only scope compatible with that maintained correction.
- No additional AskUserQuestion is required for this Slice 1 scoping artifact. Downstream implementation slices that create MemBase SPECs, modify `scripts/release_candidate_gate.py`, add doctor checks, or wire predicates into release-readiness output will each require their own bridge GO and may require formal-artifact-approval packets per `GOV-ARTIFACT-APPROVAL-001`.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is **not** a bulk operation against the standing backlog. It advances exactly one work item (WI-3248) through one slice (Slice 1: Scoping). The scope is limited to:

- Authoring one bridge proposal file (this file) and one verdict file (the future Codex review verdict).
- Producing one durable artifact: the scoping document at `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-003.md`.

The proposal does not retire, supersede, batch-update, batch-create, or reorder any standing-backlog work items. The deployability/maintainability **inventory** described below in the Gate Predicate Catalog is a descriptive enumeration of GT-KB-side predicates that downstream slices will register; it is not a bulk-create operation against MemBase. No MemBase mutation is in scope for Slice 1. The applicable standing-backlog evidence is the single WI-3248 row plus its active project membership in `PROJECT-GTKB-ADOPTER-EXPERIENCE`, both of which already exist; no inventory mutation is performed.

The formal-artifact-approval discipline applies to downstream slices (where MemBase SPEC rows or governance rows are created), not to this Slice 1 scoping artifact. No formal-artifact-approval packet is created or required for the proposal file itself.

## Requirement Sufficiency

Existing requirements sufficient.

The owner-approved `SPEC-DEPLOY-*` family (seven specifications) together with WI-3248's `description` and `failure_description` specify the requirement clearly: GT-KB must verify Agent Red remains deployable, maintainable, and enhanceable before any irreversible Agent Red migration / cutover / extraction / deletion / restructuring work proceeds. Each `SPEC-DEPLOY-*` spec carries owner-approved acceptance criteria covering source build, Python 3.12 RC gate, container build, frontend bundles, workflow inputs, maintain/enhance path, and evidence freshness. The verification surface is fully specified by these specs; this scoping document derives its predicate catalog directly from them (see `## Spec-to-Predicate Matrix`). No new requirements need to be captured before this scoping artifact can be reviewed.

Downstream implementation slices may discover that a specific gate predicate needs finer-grained operational detail; any such detail will be captured then as a new spec (or a new version of an existing `SPEC-DEPLOY-*` spec) through the standard formal-artifact-approval-packet workflow. This scoping document does not create or revise any specification.

## Reconciliation With the SPEC-DEPLOY Evidence Contract

This section addresses `-002` finding P1 ("the downstream predicate model is not
reconciled with the formal deployability evidence contract").

**Decision: the GT-KB-side preservation gate is a validator/wrapper over the
existing `SPEC-DEPLOY-*` evidence. It does NOT create a new authoritative
evidence surface and does NOT supersede the `SPEC-DEPLOY-*` evidence contract.**

Concretely:

1. **Canonical evidence store is unchanged.** The seven `SPEC-DEPLOY-*` proofs
   (SOURCE-BUILD, RC-GATE-PYTHON-3-12, CONTAINER-BUILD, FRONTEND-BUNDLES,
   WORKFLOW-INPUTS, MAINTAIN-ENHANCE-PATH) are captured and stored exactly as
   `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` requires: timestamped at capture,
   written to `.gtkb-state/deployability-evidence/<application-id>/<proof-id>-<ulid>.json`.
   The preservation-gate runner is a **reader** of these files. It does not
   write proof evidence, does not relocate it, and does not introduce a second
   proof-evidence path.

2. **Freshness contract is honored, not re-implemented.** The runner applies the
   `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` rule directly: the default 30-day window
   from `captured_at`, plus any per-proof override declared in the application's
   `deployability_manifest.toml`. Evidence beyond its window is treated as
   MISSING for predicate evaluation, exactly as the spec mandates. The runner
   does not invent a separate staleness window; "owner-configured staleness
   window" language in `-001`'s catalog is hereby bound to the
   `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` window + manifest override.

3. **`.gtkb-state/preservation-gate/<run_id>/` is a derived report, not
   evidence.** The composite-result file the runner emits under
   `.gtkb-state/preservation-gate/<run_id>/` is a regenerable *report* artifact:
   it records the per-predicate PASS/WARN/FAIL outcome and the composite
   `deployable_and_maintainable` boolean computed from the canonical
   `SPEC-DEPLOY-*` evidence at run time. It is not authoritative evidence; it can
   be deleted and regenerated by re-running the gate. It does not split,
   duplicate, or shadow the `.gtkb-state/deployability-evidence/` store. This
   matches the established benchmark/report convention
   (`.gtkb-state/benchmarks/<run_id>/`) where run outputs are regenerable
   evidence directories, not canonical state.

4. **No new per-predicate SPECs for the core six proofs.** `-001`'s downstream
   "Slice 4: Per-predicate SPEC creation" is narrowed: the six core deployability
   proofs already have formal specifications (`SPEC-DEPLOY-SOURCE-BUILD-001`,
   `-RC-GATE-PYTHON-3-12-001`, `-CONTAINER-BUILD-001`, `-FRONTEND-BUNDLES-001`,
   `-WORKFLOW-INPUTS-001`, `-MAINTAIN-ENHANCE-PATH-001`). Downstream slices MUST
   reuse those specs as the predicate authority rather than creating duplicate
   predicate SPECs. A downstream slice MAY still create a new SPEC only for a
   genuinely new maintainability predicate that has no `SPEC-DEPLOY-*` coverage
   (e.g., a credential-scan-coverage predicate); any such new SPEC goes through
   the formal-artifact-approval-packet workflow.

5. **If a future need arises to change the evidence contract**, that is a
   revision to `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` (or a sibling spec) through
   the governed formal-artifact-approval path - not a silent divergence in the
   runner. This scoping document does not authorize any such change.

The net effect: one canonical evidence store (`SPEC-DEPLOY-*` proofs under
`.gtkb-state/deployability-evidence/`), one freshness contract
(`SPEC-DEPLOY-EVIDENCE-FRESHNESS-001`), and the preservation gate is a
deterministic reader/validator that rolls those proofs up into a composite
deployability/maintainability verdict.

## Spec-to-Predicate Matrix

This section addresses `-002` finding P1 ("the proposal omits the formal
SPEC-DEPLOY family"). Each owner-approved `SPEC-DEPLOY-*` specification is mapped
to the gate predicate(s) that satisfy it. Predicate `DEPL-0` is new in `-003` to
cover source-build evidence explicitly, as the NO-GO required.

| SPEC-DEPLOY spec | Satisfying predicate(s) | What the predicate reads |
|------------------|--------------------------|---------------------------|
| `SPEC-DEPLOY-SOURCE-BUILD-001` | DEPL-0 (source-build evidence), DEPL-1 (RC evidence currency) | The `source-build` proof file under `.gtkb-state/deployability-evidence/<application-id>/`, validated against the `deployability_manifest.toml` artifact list and the freshness window. |
| `SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001` | DEPL-2 (Python 3.12 gate evidence) | The `rc-gate-python-3-12` proof file recording the Python 3.12 RC-gate result. |
| `SPEC-DEPLOY-CONTAINER-BUILD-001` | DEPL-4 (container build surfaces) | The `container-build` proof file recording image metadata vs manifest. |
| `SPEC-DEPLOY-FRONTEND-BUNDLES-001` | DEPL-3 (frontend / admin / widget builds) | The `frontend-bundles` proof file recording per-bundle build results. |
| `SPEC-DEPLOY-WORKFLOW-INPUTS-001` | DEPL-5 (deployment workflow inputs / artifacts) | The `workflow-inputs` proof file recording the discovered workflow input inventory. |
| `SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001` | MAINT-3 (maintain/enhance path sane) | The `maintain-enhance-path` proof file recording the end-to-end clone/edit/test/build smoke result. |
| `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` | Cross-cutting: every DEPL-* predicate + the composite | The `captured_at` timestamp of each proof file; the per-proof manifest freshness override; stale-as-missing evaluation per the spec. |

The maintainability predicates MAINT-1, MAINT-2, MAINT-4, MAINT-5, MAINT-6, and
MAINT-7 cover GT-KB-side maintainability concerns (MemBase spec coverage,
Deliberation Archive boundary records, dev-environment inventory, credential-scan
coverage, supersession tracking, doctor health) that are not within the
`SPEC-DEPLOY-*` scope; they remain part of the catalog as the "maintainable"
half of the preservation gate per WI-3248's framing.

## Gate Predicate Catalog

Each predicate is a GT-KB-side boolean (or trivalent PASS / WARN / FAIL) check that consumes GT-KB-owned state and emits a structured result. No predicate reads the live Agent Red repository. The catalog is presented here for Slice 1 review and will be formalized as a registry under `config/governance/` in a downstream implementation slice. Per `## Reconciliation With the SPEC-DEPLOY Evidence Contract`, every DEPL-* predicate reads the corresponding `SPEC-DEPLOY-*` proof file from the canonical `.gtkb-state/deployability-evidence/` store and honors the `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` freshness window.

### Deployability predicates

DEPL-0. **Agent Red source-build evidence present and current** (new in `-003`). Reads the `source-build` proof file under `.gtkb-state/deployability-evidence/<application-id>/`. Result: PASS if the proof exists, is within its `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` window, and records the manifest artifact list produced without errors. WARN if present but within window with an owner-cited waiver. FAIL if absent, stale (treated as MISSING per the freshness spec), or recording a source-level error. Satisfies `SPEC-DEPLOY-SOURCE-BUILD-001`.

DEPL-1. **Agent Red release-candidate evidence current**. Reads the most recent GT-KB-side CI evidence and the relevant `SPEC-DEPLOY-*` proof files. Result: PASS if the most recent evidence is within the freshness window AND records all-required-workflows green. WARN if within window but missing one or more workflows. FAIL if absent or stale. Contributes to `SPEC-DEPLOY-SOURCE-BUILD-001` currency.

DEPL-2. **Python 3.12 gate evidence present**. Reads the `rc-gate-python-3-12` proof file's recorded Python version markers (captured at evidence-harvest time, not re-fetched). Result: PASS if 3.12 markers present and pass. WARN if markers present but a waiver DELIB applies. FAIL if absent or failing without waiver. Satisfies `SPEC-DEPLOY-RC-GATE-PYTHON-3-12-001`.

DEPL-3. **Frontend / admin / widget build surfaces covered**. Reads the `frontend-bundles` proof file's recorded per-bundle build-job results. Result: PASS if all three surfaces present and green. WARN if one or more under owner-approved waiver. FAIL otherwise. Satisfies `SPEC-DEPLOY-FRONTEND-BUNDLES-001`.

DEPL-4. **Docker / container build surfaces covered**. Reads the `container-build` proof file's recorded container-build and image-metadata results. Result: PASS if all green or under cited waiver DELIB. WARN with cited waiver. FAIL otherwise. Satisfies `SPEC-DEPLOY-CONTAINER-BUILD-001`.

DEPL-5. **Deployment workflow inputs / artifacts inventoried**. Reads the `workflow-inputs` proof file's recorded discovered-input inventory. Result: PASS if inventory current and complete. WARN if inventory stale. FAIL if absent. Satisfies `SPEC-DEPLOY-WORKFLOW-INPUTS-001`.

DEPL-6. **Canonical Agent Red repo migration status known**. Reads `DELIB-S330-SLICE-8-6-PHASE-4-CANONICAL-AGENT-RED-REPO-MIGRATION-PREREQUISITE` status from MemBase and the canonical-terminology glossary's Agent Red entry. Result: PASS if migration recorded as complete. WARN during the documented dual-listing transient. FAIL if no record exists. (Boundary-state predicate; not directly a `SPEC-DEPLOY-*` proof.)

### Maintainability predicates

MAINT-1. **Agent Red-related MemBase spec coverage current**. Reads MemBase for specs tagged or named with Agent Red scope (including the `SPEC-DEPLOY-*` family and the isolation-017 Slice 8.5/8.6 specs). Result: PASS if all such specs are at `implemented` or `verified` and have current assertions. WARN if at `specified`. FAIL if a verified spec's assertions are failing.

MAINT-2. **Deliberation Archive Agent Red boundary records present**. Searches DA for the boundary-correction deliberations (2026-05-04 owner correction, DELIB-S330 migration prerequisite, DELIB-S330 Slice 8.5/8.6 waivers). Result: PASS if all expected DELIB IDs resolve. WARN if one is missing. FAIL if multiple missing.

MAINT-3. **Maintain/enhance path sane**. Reads the `maintain-enhance-path` proof file recording the end-to-end clone/edit/test/build smoke result. Result: PASS if the smoke proof is present, current, and records no GT-KB platform interference. WARN if present with a cited waiver. FAIL if absent, stale, or recording unwaived GT-KB platform interference. Satisfies `SPEC-DEPLOY-MAINTAIN-ENHANCE-PATH-001`.

MAINT-4. **Dev environment inventory current**. Reads a GT-KB-side dev-environment inventory artifact (produced under an existing inventory workstream, not authored here). Result: PASS / WARN / FAIL based on inventory recency and completeness.

MAINT-5. **Credential-scan coverage current**. Reads `GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT` Slice 1+2 outputs (current-tracked-scan and all-local-refs-scan reports). Result: PASS if both reports recent and clean. WARN if recent with cited candidate-high count under triage. FAIL if absent or with verified-provider findings.

MAINT-6. **Supersession tracking complete for Agent Red-related work items**. Reads MemBase work_items for Agent Red-scoped projects; checks that completed items carry valid `superseded_by` or `completion_evidence`. Result: PASS / WARN / FAIL based on field population. (WI-3248 itself is included in this predicate's input set.)

MAINT-7. **Doctor checks for Agent Red dependency green**. Reads doctor surfaces that already exist (e.g., bridge-dispatch-liveness, role-set-topology-consistency, harness-parity, scaffold-drift). Result: PASS / WARN / FAIL passed through.

### Composite output

The runner emits one composite result (`deployable_and_maintainable: bool`) plus the per-predicate detail. The composite is FAIL if any predicate is FAIL; WARN if any predicate is WARN and none FAIL; PASS only if all predicates PASS. The composite output is written as a derived, regenerable report under `.gtkb-state/preservation-gate/<run_id>/` (not authoritative evidence; see `## Reconciliation With the SPEC-DEPLOY Evidence Contract`). It is consumed by release-readiness, doctor, and dashboard surfaces in downstream slices (each via its own bridge thread).

## Implementation Plan

### Slice 1 (this proposal)

1. Author this scoping document. **DONE** by virtue of this proposal being filed.
2. Loyal Opposition reviews the scoping document. NO-GO surfaces missing predicates, missing spec linkage, evidence-contract conflicts, or boundary violations; GO authorizes proceeding to Slice 2.

### Downstream slices (NOT authorized by this Slice 1)

Each requires its own bridge proposal, its own Loyal Opposition GO, and its own implementation/verification cycle:

- **Slice 2: Predicate registry schema.** Add `config/governance/agent-red-preservation-predicates.toml` with one `[[predicate]]` block per catalog entry above. Each `[[predicate]]` block references the governing `SPEC-DEPLOY-*` spec ID for DEPL-* predicates. Add a JSON-Schema-style validation test under `platform_tests/`. No runtime predicate evaluation yet; just the registry structure and validation.
- **Slice 3: Predicate runner.** Add `scripts/agent_red_preservation_gate.py` that reads the registry, dispatches per-predicate handlers, reads the canonical `SPEC-DEPLOY-*` proof files from `.gtkb-state/deployability-evidence/<application-id>/`, applies the `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` window, and emits a regenerable composite report (JSON + markdown summary) to `.gtkb-state/preservation-gate/<run_id>/`. Each handler is a small read-only function. No mutation of the canonical evidence store.
- **Slice 4: New maintainability-predicate SPEC creation (narrowed).** The six core deployability proofs already have `SPEC-DEPLOY-*` specs and are NOT re-specified. This slice creates MemBase SPECs only for genuinely new maintainability predicates lacking `SPEC-DEPLOY-*` coverage, via formal-artifact-approval packets.
- **Slice 5: Doctor integration.** Add a doctor check (`_check_agent_red_preservation_gate`) that runs the runner and reports composite PASS/WARN/FAIL.
- **Slice 6: Release-readiness wiring.** Have `scripts/release_candidate_gate.py` (or the GT-KB release-readiness surface, depending on owner direction) consume the runner output as a pre-release gate input. This is the only slice that touches `scripts/release_candidate_gate.py`; it is the natural integration point but is explicitly out of scope here.

No downstream slice introduces Agent Red repository interaction. All slices keep target_paths within `E:\GT-KB`.

## Test Mapping

Slice 1 is a scoping artifact; it adds no source code. The spec-to-test mapping for this slice covers acceptance criteria via inspection:

| Linked specification | Slice 1 evidence |
|----------------------|------------------|
| GOV-FILE-BRIDGE-AUTHORITY-001 | Proposal is filed via the bridge protocol; INDEX.md update is a separate step. |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | This proposal's `Specification Links` section cites every relevant governing spec, including the full `SPEC-DEPLOY-*` family; Codex inspects for omissions during review. |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | This proposal's `Test Mapping`, `Acceptance Criteria`, and `Verification Plan` sections define how downstream verification will work; Slice 1 itself adds no executable test. |
| GOV-STANDING-BACKLOG-001 | WI-3248 already exists in MemBase as P0; this proposal advances it through Slice 1 without bulk operation. |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 / `.claude/rules/project-root-boundary.md` | `target_paths` contains exactly one path, inside `E:\GT-KB\bridge\`; no Agent Red repo path is referenced. |
| SPEC-DEPLOY-SOURCE-BUILD-001 ... SPEC-DEPLOY-EVIDENCE-FRESHNESS-001 (all 7) | The `Spec-to-Predicate Matrix` maps each `SPEC-DEPLOY-*` spec to its satisfying predicate; the `Reconciliation` section binds the runner to the spec-defined evidence path and freshness window. Slice 1 evidence is the matrix + reconciliation by inspection; downstream slices add executable tests that exercise each predicate against the corresponding `SPEC-DEPLOY-*` proof file. |
| `.claude/rules/acting-prime-builder.md` § "Agent Red Separate-Project Boundary" | Proposal's "Project Boundary Clarification" section explicitly cites and enforces this rule. |

Downstream slices add executable tests (registry validation, runner unit tests, doctor-check tests, integration smoke tests) under their own bridge threads.

## Risk and Rollback

**Risk: scoping document drifts from implementation.** Mitigation: each downstream slice cites this scoping document and the `Spec-to-Predicate Matrix` as its source-of-truth predicate catalog; deviations require an updated scoping bridge thread, not silent slice-level drift.

**Risk: gate predicates become a maintenance burden.** Mitigation: the catalog is explicitly small (14 predicates total) and biased toward consuming pre-existing GT-KB-side state - the `SPEC-DEPLOY-*` proof files and existing doctor/inventory surfaces - rather than introducing new harvest mechanisms. The downstream runner is a deterministic service per `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`.

**Risk: evidence-store divergence.** Mitigation: the `Reconciliation` section binds the runner to the single canonical `.gtkb-state/deployability-evidence/` store and the `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` freshness contract; the `.gtkb-state/preservation-gate/<run_id>/` directory holds only regenerable derived reports.

**Risk: predicate failures cause false alarms during normal Agent Red work.** Mitigation: WARN is a first-class state; owner-approved waivers (cited via DELIB IDs) downgrade FAIL to WARN with audit trail. The composite output is informational in Slices 1-5 and becomes release-gate-blocking only when Slice 6 explicitly wires it in.

**Rollback for Slice 1:** bridge files are append-only by protocol; rollback in practice is "supersede with a new scoping document" rather than physical deletion. No other GT-KB state is changed.

## Acceptance Criteria

A1. Proposal file exists at `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-003.md` with all mandatory sections present.

A2. `target_paths` contains exactly one entry: this proposal file. No path outside `E:\GT-KB` appears.

A3. "Project Boundary Clarification" section explicitly cites `.claude/rules/acting-prime-builder.md` § "Agent Red Separate-Project Boundary" and states no Agent Red repo mutation is in scope.

A4. `Specification Links` cites all seven `SPEC-DEPLOY-*` specifications; the `Spec-to-Predicate Matrix` maps each `SPEC-DEPLOY-*` spec to a satisfying DEPL/MAINT predicate; a source-build predicate (DEPL-0) is present.

A5. The `Reconciliation With the SPEC-DEPLOY Evidence Contract` section states explicitly whether the GT-KB-side runner wraps, validates, or supersedes the `SPEC-DEPLOY-*` evidence contract, and binds the runner to the canonical `.gtkb-state/deployability-evidence/` path and the `SPEC-DEPLOY-EVIDENCE-FRESHNESS-001` freshness window.

A6. Implementation Plan enumerates downstream slices and explicitly states none are authorized by this Slice 1 GO; Slice 4 is narrowed to not re-specify the six core deployability proofs.

A7. Applicability Preflight passes with `preflight_passed: true` and `missing_required_specs: []`.

A8. Clause Preflight exits 0 with zero blocking gaps.

## Verification Plan

Slice 1 verification is by inspection of the proposal file against the Acceptance Criteria:

1. `git ls-files bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-003.md` confirms file presence (after staging).
2. Open the proposal file; grep for the mandatory section headings. Each must appear.
3. Parse `target_paths` from the front matter; confirm exactly one entry, equal to the proposal file path, within `E:\GT-KB\bridge\`.
4. Grep the proposal text for "`.claude/rules/acting-prime-builder.md`" and "Agent Red Separate-Project Boundary"; both must appear in the Project Boundary Clarification section.
5. Confirm all seven `SPEC-DEPLOY-*` IDs appear in `Specification Links` and each is mapped in the `Spec-to-Predicate Matrix`.
6. Confirm the `Reconciliation` section states the wrap/validate/supersede decision and cites the canonical evidence path + freshness window.
7. Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate-slice-1-scoping`; record `packet_hash`; confirm `preflight_passed: true`.
8. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate-slice-1-scoping`; expect exit 0.

Loyal Opposition's VERIFIED verdict for Slice 1 should confirm all eight checks pass by inspection.

## Applicability Preflight

Run on this `-003` content after the INDEX entry was updated:

```
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate-slice-1-scoping
```

```
## Applicability Preflight

- packet_hash: `sha256:90e53630e0de49f0118aae31643781c24bd2e0e79ed142c8ed99604bdc95419d`
- bridge_document_name: `gtkb-agent-red-deployability-preservation-gate-slice-1-scoping`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-003.md`
- operative_file: `bridge/gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |
```

`preflight_passed: true`; `missing_required_specs: []`; `missing_advisory_specs: []`.

## Clause Applicability

```
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-agent-red-deployability-preservation-gate-slice-1-scoping
```

```
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-agent-red-deployability-preservation-gate-slice-1-scoping`
- Operative file: `bridge\gtkb-agent-red-deployability-preservation-gate-slice-1-scoping-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |
```

Exit 0; zero blocking gaps. All five `must_apply` clauses report evidence found.

End of proposal.
