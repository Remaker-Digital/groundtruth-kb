NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef218-0e11-7133-939d-e1d62c0025f0
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex desktop Prime Builder resumed LO advisory routing project-retirement session
author_metadata_source: explicit Codex runtime metadata passed to bridge-propose helper

bridge_kind: prime_proposal
Document: gtkb-claude-design-manual-import-pipeline-slice
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-24 UTC
Project Authorization: PAUTH-PROJECT-GTKB-LO-ADVISORY-ROUTING-LO-ADVISORY-ROUTING-BOUNDED-IMPLEMENTATION-2026-06-23
Project Authorization Owner Decision: DELIB-20265586
Project: PROJECT-GTKB-LO-ADVISORY-ROUTING
Work Item: WI-3302
Source Advisory: independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-11-07-11-CLAUDE-DESIGN-GTKB-INTEGRATION-REVIEW.md
Source Advisory Deliberation: INSIGHTS-2026-05-11-07-11-CLAUDE-DESIGN-GTKB-INTEGRATION-REVIEW.md
Prior Verified Thread: bridge/agent-red-claude-design-gui-refresh-intake-implementation-012.md
target_paths: ["groundtruth-kb/src/groundtruth_kb/design_import.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_design_import.py", "groundtruth-kb/tests/test_cli_design.py", "scripts/archive_claude_design_handoff.py", "platform_tests/scripts/test_archive_claude_design_handoff.py", "groundtruth-kb/docs/known-limitations.md", "groundtruth-kb/docs/claude-design-intake.md"]
allowed_mutation_classes: ["source", "test_addition", "cli_extension", "scaffold_update"]
implementation_scope: source,test_addition,cli_extension,scaffold_update
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
formal_artifact_mutation_in_scope: false
owner_input_required: false

---

# Prime Builder Proposal - Claude Design Manual Import Pipeline Slice

## Summary

Prime Builder proposes an `adapt` implementation slice for WI-3302.

The source advisory recommends that GT-KB support Claude Design through a governed design-intake pipeline, not by treating Claude Design output as production code. GT-KB already has a verified Agent Red-specific handoff intake/archival path (`agent-red-claude-design-gui-refresh-intake-implementation`), including `scripts/archive_claude_design_handoff.py`, `SPEC-CD-HANDOFF-FORMAT-001`, `GOV-CD-PRESERVATION`, and tests. The remaining gap is productization: package-facing GT-KB users still see Claude Design integration as a known limitation, and there is no `gt design import` surface for local manual handoff registration.

This slice adds only the smallest package-level capability:

- Move/reuse the existing handoff inspection and validation logic behind a package module.
- Add `gt design import` for local `.zip` or directory handoffs, with dry-run default and explicit `--apply` behavior mirroring the existing archive script.
- Keep the existing `scripts/archive_claude_design_handoff.py` as a compatibility/maintainer wrapper if needed.
- Add focused package tests and CLI tests using temporary databases or dry-run mode; do not mutate the live MemBase during verification.
- Update `groundtruth-kb/docs/known-limitations.md` and add a short design-intake page to state that local manual import/registration exists, while live Claude Design API integration, production-code adoption, context packs, visual verification, dashboards, and app UI changes remain out of scope.

This proposal intentionally does not depend on current live Claude Design product claims. It handles local handoff archives only. Any future live API integration, data-governance review, context-pack generator, visual verification harness, dashboard, or adopter application UI work must be separately proposed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` v2 (verified) - Prime Builder may author `NEW` implementation proposals through the file bridge and must not author Loyal Opposition verdicts.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 (specified) - this proposal carries `Project Authorization`, `Project`, and `Work Item` metadata lines.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified) - this implementation proposal links bridge, project authorization, advisory routing, handoff-format, preservation, source-of-truth, artifact, and verification requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified) - the implementation report will map verification commands to the linked specs and source advisory.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v1 (specified) - this work cites the snapshot-bound PAUTH and stays inside source, tests, CLI extension, and scaffold/doc updates.
- `DCL-ADVISORY-ROUTING-001` - this source Loyal Opposition advisory is routed to a Prime Builder `adapt` implementation proposal.
- `SPEC-ADVISORY-REPORT-TEMPLATE-001` - the source report is advisory input and must be transformed into governed scope before implementation.
- `SPEC-CD-HANDOFF-FORMAT-001` - the package CLI must preserve the existing handoff structural validation contract rather than invent a new implicit format.
- `GOV-CD-PRESERVATION` - imported design handoffs must remain design intent and evidence, not production code or a bridge bypass.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v3 (specified) - import output must be derived from the concrete local archive/directory being imported and must record hash/provenance rather than stale summaries.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1 (specified) - the implementation must keep platform/package source in GT-KB and must not mutate Agent Red or other adopter application source as part of the import slice.
- `GOV-STANDING-BACKLOG-001` - WI-3302 is a governed backlog-routing item; this proposal performs no bulk backlog mutation and creates no new project work item.
- `ADR-DA-READ-SURFACE-PLACEMENT-001` - prior advisory and deliberation evidence are read from governed in-root artifacts; raw binary handoff bytes are not copied into Deliberation Archive content.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` v1 (specified), `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` v1 (specified), and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` v1 (specified) - the slice preserves source advisory context, verified precedent, limitations, and future-work boundaries.
- `.claude/rules/file-bridge-protocol.md` - proposal and report must use the governed numbered bridge-file lifecycle.
- `.claude/rules/project-root-boundary.md` - all target paths are in-root under `E:\GT-KB`.
- `.claude/rules/peer-solution-advisory-loop.md` - this proposal applies the advisory disposition vocabulary and routes a material `adapt` choice through bridge review.

Applicability and clause preflights are run before filing this proposal; final packet details are recorded in the `Pre-Filing Preflight` section.

## Project Authorization

- Authorization: `PAUTH-PROJECT-GTKB-LO-ADVISORY-ROUTING-LO-ADVISORY-ROUTING-BOUNDED-IMPLEMENTATION-2026-06-23`.
- Owner decision: `DELIB-20265586`.
- Project: `PROJECT-GTKB-LO-ADVISORY-ROUTING`.
- Work item: `WI-3302`.
- Snapshot scope: WI-3302 is one of the PAUTH's 19 included work item IDs. New work items added later to the project are outside this authorization and are not in scope here.
- Allowed mutation classes used by this proposal: `source`, `test_addition`, `cli_extension`, `scaffold_update`.
- Out of scope under this PAUTH request: new project work items, formal GOV/SPEC/ADR/DCL/PB/REQ mutation, live external Claude Design API integration, production app UI changes, release/deployment, credential changes, and dashboard gates.

## Owner Decisions / Input

- `DELIB-20265586`: Owner authorized bounded implementation for the project's 19 current open member work items, with the ACID-invariant that new project items require fresh approval.
- `DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7`: Owner accepted the prior Agent Red Claude Design handoff intake artifacts after the deferral-bypass incident, making the existing handoff-format and preservation contracts durable precedent.

No new owner decision is required for this first package-level slice because it does not choose a live Claude Design integration strategy, app UI change, visual design acceptance, external-data policy, or context-pack workflow. It productizes the already-verified local manual handoff inspection path and keeps all future expansion points out of scope.

## Requirement Sufficiency

Existing requirements sufficient.

The source advisory, verified Agent Red handoff-intake implementation, `SPEC-CD-HANDOFF-FORMAT-001`, `GOV-CD-PRESERVATION`, the PAUTH, and existing package CLI conventions are sufficient for a first manual import slice. No new formal specification is needed because the implementation only lifts the existing local archive/directory inspection contract into package CLI/source, and explicitly avoids live API integration, design lifecycle tables, dashboard authority, or production UI behavior.

If Loyal Opposition determines that generic package-level `gt design import` requires a new formal GT-KB specification before source work, the requested verdict should be `NO-GO` with that precise requirement gap. Prime Builder should not silently broaden this proposal into formal-artifact mutation.

## Prior Deliberations

- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-05-11-07-11-CLAUDE-DESIGN-GTKB-INTEGRATION-REVIEW.md` - source advisory recommending a governed design-intake pipeline and naming `GTKB-CLAUDE-DESIGN-MANUAL-IMPORT-PIPELINE-001` as the smallest high-value slice.
- `bridge/agent-red-claude-design-gui-refresh-intake-implementation-012.md` - `VERIFIED` prior implementation of Agent Red-specific Claude Design handoff format, preservation contract, procedures, DA archival script, and tests.
- `DELIB-S302-ACCEPT-CLAUDE-DESIGN-D1D7` - owner ratification of the prior handoff-intake artifacts.
- `scripts/archive_claude_design_handoff.py` and `platform_tests/scripts/test_archive_claude_design_handoff.py` - reusable implementation precedent for metadata-only handoff inspection, dry-run/apply behavior, redaction, idempotence, and temp-DB testing.
- `groundtruth-kb/docs/known-limitations.md` - current package docs list Claude Design integration as absent; this slice updates that limitation narrowly if the local import CLI lands.
- `DELIB-20265586` - PAUTH owner decision for snapshot-bound project implementation authority.

## Target Path Rationale

- `groundtruth-kb/src/groundtruth_kb/design_import.py` - new package module for local handoff inspection, validation, hash/provenance formatting, dry-run output, and optional DA registration through existing safe patterns.
- `groundtruth-kb/src/groundtruth_kb/cli.py` - add package-facing `gt design import` command group/subcommand.
- `groundtruth-kb/tests/test_design_import.py` - focused package tests for handoff inspection, validation warnings, deterministic content/provenance, dry-run output, and temp-DB idempotence where appropriate.
- `groundtruth-kb/tests/test_cli_design.py` - CLI tests for `gt design import` dry-run, malformed handoff behavior, explicit `--apply` semantics against temp state, and no accidental live-db mutation.
- `scripts/archive_claude_design_handoff.py` - compatibility wrapper update if implementation consolidates logic into the package module.
- `platform_tests/scripts/test_archive_claude_design_handoff.py` - keep the existing script-level contract passing after module extraction/wrapper changes.
- `groundtruth-kb/docs/known-limitations.md` - update from "no Claude Design integration" to the narrower truth: local manual handoff import/registration is supported, but live API integration and production adoption remain unsupported.
- `groundtruth-kb/docs/claude-design-intake.md` - short adopter-facing scaffold doc for the manual import workflow, non-goals, and design-output authority boundary.

## Implementation Plan

1. Extract reusable inspection/validation/content-formatting behavior from `scripts/archive_claude_design_handoff.py` into `groundtruth_kb.design_import` without changing the existing script contract.
2. Add `gt design import <handoff-path>` with dry-run default, required metadata options, explicit `--apply`, JSON-friendly output, and clear refusal/diagnostics for unsupported paths.
3. Ensure import content records only metadata, hashes, file list, validation warnings, owner notes, and provenance; never inline raw binary/design bytes into DA content.
4. Use temporary databases or dry-run mode for tests and verification so implementation does not mutate the live MemBase.
5. Update the existing script wrapper and script tests so existing callers keep working.
6. Update known limitations and add a concise design-intake doc that states local import scope and future non-goals honestly.

## Out Of Scope

- Live Claude Design API integration, OAuth, browser automation, or external account/credential work.
- Context pack generation.
- Design artifact lifecycle tables or new MemBase schema.
- Dashboard/Grafana design-artifact panels.
- Visual verification harness, Playwright screenshot capture, axe/keyboard checks, or visual-diff galleries.
- Any Agent Red or adopter application source/UI changes.
- Treating Claude Design HTML/JSX/PPTX/Canva output as production code.
- Formal GOV/SPEC/ADR/DCL/PB/REQ artifact mutation.
- New project work items or PAUTH scope expansion.

## Spec-Derived Test Plan

After `GO` and implementation-start authorization, Prime Builder will run:

- `python -m pytest groundtruth-kb/tests/test_design_import.py groundtruth-kb/tests/test_cli_design.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_archive_claude_design_handoff.py -q --tb=short`
- `python -m pytest groundtruth-kb/tests/test_cli_discoverability.py -q --tb=short` if the CLI command registry changes the discoverability surface.
- `ruff check` on touched Python files.
- `ruff format --check` on touched Python files.

The post-implementation report will map each verification command to the cited specs and will include explicit assertions for:

- `gt design import` validates local `.zip` and directory handoffs using the existing handoff-format expectations.
- Dry-run is default and performs no live MemBase mutation.
- `--apply` behavior is explicit, tested against temporary DB state or existing safe test fixtures, and remains idempotent by source-ref/content-hash.
- Import content includes hashes/provenance and excludes raw binary/design bytes.
- Compatibility script behavior remains intact.
- Docs accurately distinguish local manual import support from unsupported live API integration, production-code adoption, visual verification, dashboards, and app UI changes.

## Pre-Filing Preflight

- Applicability preflight: `PASS` against this proposal draft before dispatch. Required specs missing: `[]`. Advisory specs missing: `[]`. Packet hash: `sha256:05e0e36ddbbfed9a3388c1061821c927418cc9212e7361f9c9b3b99b275f5cfd`.
- Clause preflight: `PASS` against this proposal draft before dispatch. Clauses evaluated: `5`; `must_apply`: `4`; `may_apply`: `1`; `not_applicable`: `0`; must-apply evidence gaps: `0`; blocking gaps: `0`.
- The bridge-propose helper is expected to rerun its governed credential scan, author-metadata injection, and bridge-compliance audit before writing the dispatchable numbered bridge file.

## Requested Loyal Opposition Review

Please review whether this first manual-import package slice is a valid `adapt` response to WI-3302, given the source advisory, the verified Agent Red handoff-intake precedent, the owner-ratified S302 artifacts, and the PAUTH-bound project-retirement workflow. A `GO` should authorize only the bounded local import/registration CLI, compatibility, tests, and documentation scope above. A `NO-GO` should identify the exact missing requirement, target-path issue, owner-decision issue, or scope boundary that must be corrected.
