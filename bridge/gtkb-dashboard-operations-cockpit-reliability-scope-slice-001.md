NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019ef218-0e11-7133-939d-e1d62c0025f0
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex desktop Prime Builder resumed LO advisory routing project-retirement session
author_metadata_source: explicit Codex runtime metadata passed to bridge-propose helper

bridge_kind: prime_proposal
Document: gtkb-dashboard-operations-cockpit-reliability-scope-slice
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-24 UTC
Project Authorization: PAUTH-PROJECT-GTKB-LO-ADVISORY-ROUTING-LO-ADVISORY-ROUTING-BOUNDED-IMPLEMENTATION-2026-06-23
Project Authorization Owner Decision: DELIB-20265586
Project: PROJECT-GTKB-LO-ADVISORY-ROUTING
Work Item: WI-3433
Source Advisory: bridge/gtkb-dashboard-operations-cockpit-advisory-001.md
Source Advisory Disposition: bridge/gtkb-dashboard-operations-cockpit-advisory-disposition-001.md
Source Advisory Disposition Review: bridge/gtkb-dashboard-operations-cockpit-advisory-disposition-002.md
target_paths: ["groundtruth-kb/src/groundtruth_kb/dashboard.py", "groundtruth-kb/src/groundtruth_kb/dashboard_service.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/tests/test_dashboard.py", "scripts/gtkb_dashboard/refresh_dashboard_db.py", "scripts/gtkb_dashboard/generate_grafana_dashboard.py", "docs/gtkb-dashboard/index.html", "docs/gtkb-dashboard/grafana/README.md", "docs/gtkb-dashboard/grafana/PACKAGE-INTEGRATION.md", "docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json", "platform_tests/scripts/test_gtkb_dashboard_grafana.py", "platform_tests/scripts/test_dashboard_subject_selector.py"]
allowed_mutation_classes: ["source", "test_addition", "cli_extension", "scaffold_update"]
implementation_scope: source,test_addition,cli_extension,scaffold_update
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
formal_artifact_mutation_in_scope: false
owner_input_required: false

---

# Prime Builder Proposal - Dashboard Operations Cockpit Reliability and Scope Slice

## Summary

Prime Builder proposes the first implementation slice for WI-3433, following the Loyal Opposition `GO` on the advisory disposition and the four owner scope decisions now captured in the Deliberation Archive.

This slice makes the dashboard more trustworthy before any broad visual redesign:

- Replace hardcoded or misleading current-metric status semantics with explicit per-metric status functions and focused tests.
- Present the default dashboard subject as combined GT-KB platform plus active adopter/application operations with explicit badges and evidence-source labels.
- Replace misleading local workspace `Open` affordances with copyable local path controls or non-executing path text.
- Keep refresh service wording and generated setup surfaces scoped to loopback/local-only operation.
- Treat package-facing `gt dashboard` commands as the primary visible setup path; maintainer scripts may remain secondary implementation details.

The proposal is intentionally bounded. It does not request database schema changes, broad Grafana redesign, shared/public refresh-service hardening, release/deployment work, Agent Red application-subtree changes, or formal GOV/SPEC/ADR/DCL/PB/REQ artifact mutation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` v2 (verified) - Prime Builder may author `NEW` implementation proposals through the file bridge, and must not author Loyal Opposition `GO`, `NO-GO`, or `VERIFIED` responses.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1 (specified) - this proposal carries `Project Authorization`, `Project`, and `Work Item` metadata lines.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1 (specified) - this proposal links the governing implementation, bridge, project, source-of-truth, advisory-gate, and dashboard-counter specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1 (specified) - the implementation report will include spec-derived test evidence tied to the requirements below.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` v1 (specified) - this work cites the snapshot-bound PAUTH and keeps the requested mutation classes within source, tests, CLI/scaffold, and generated dashboard support.
- `GOV-LO-ADVISORY-OWNER-GRILLING-GATE-001` v1 (specified) - the source advisory required owner clarification before adoption/adaptation; the captured owner decisions are listed below.
- `DCL-LO-ADVISORY-OWNER-GRILLING-GATE-001` v1 (specified) - the proposal includes durable owner-decision evidence for the advisory gate and carries those decisions into target scope.
- `SPEC-ADVISORY-DASHBOARD-COUNTERS-001` v1 (specified) - bridge/dashboard counts and labels must distinguish advisory, failed proposal, Prime-actionable, and Loyal-Opposition-actionable states.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v3 (specified) - dashboard status claims must derive from fresh canonical reads rather than stale summary substitutes.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` v1 (specified) - GT-KB platform work and adopter/application state must remain separable even when surfaced together.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` v1 (specified), `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` v1 (specified), and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` v1 (specified) - this implementation avoids unapproved formal-artifact mutation and preserves future-work boundaries.
- `.claude/rules/file-bridge-protocol.md` - proposal and later report must use the governed numbered bridge-file lifecycle.
- `.claude/rules/project-root-boundary.md` - all target paths are in-root under `E:\GT-KB`.
- `.claude/rules/peer-solution-advisory-loop.md` - the implementation follows the previously reviewed `adapt` disposition for a Loyal Opposition advisory.

Applicability and clause preflights are run before filing this proposal; final packet details are recorded in the `Pre-Filing Preflight` section.

## Project Authorization

- Authorization: `PAUTH-PROJECT-GTKB-LO-ADVISORY-ROUTING-LO-ADVISORY-ROUTING-BOUNDED-IMPLEMENTATION-2026-06-23`.
- Owner decision: `DELIB-20265586`.
- Project: `PROJECT-GTKB-LO-ADVISORY-ROUTING`.
- Work item: `WI-3433`.
- Snapshot scope: WI-3433 is one of the PAUTH's 19 included work item IDs. New work items added later to the project are outside this authorization and are not in scope here.
- Allowed mutation classes used by this proposal: `source`, `test_addition`, `cli_extension`, `scaffold_update`.
- Out of scope under this PAUTH request: new project work items, formal GOV/SPEC/ADR/DCL/PB/REQ mutation, deployment, credential changes, release approval, and production/shared-service hardening.

## Owner Decisions / Input

- `DELIB-20265586`: Owner authorized bounded implementation for the project's 19 current open member work items, with the ACID-invariant that new project items require fresh approval.
- `DELIB-20265873`: Default dashboard subject is combined operations with explicit badges, because during operation GT-KB health and application health are entangled.
- `DELIB-20265874`: Local workspace file controls should be copyable paths.
- `DELIB-20265875`: Refresh service scope is loopback/local-only.
- `DELIB-20265876`: Package-facing `gt dashboard` CLI commands are the primary visible setup path.

The four WI-3433 scope decisions above were direct owner replies in the resumed Codex thread and were captured into the Deliberation Archive because the interactive AUQ tool was not available in the current Default-mode restart. Prime Builder is citing those durable Deliberation Archive records rather than prose-only chat memory; Loyal Opposition should return `NO-GO` only if the specific advisory-gate rule requires re-attestation through an AUQ-only mechanism rather than Deliberation Archive owner-decision evidence.

## Requirement Sufficiency

Existing requirements sufficient.

The cited specs, PAUTH, prior `GO` disposition, and four owner decisions are sufficient for this first slice.

The implementation does not need a new spec because it repairs dashboard semantics and presentation so existing requirements are made truthful and operational. Any broader redesign, public/shared refresh service hardening, dashboard database schema expansion, or application-specific cockpit work should be proposed separately if needed.

## Prior Deliberations

- `bridge/gtkb-dashboard-operations-cockpit-advisory-001.md` - Loyal Opposition advisory that identified dashboard trust risks and required owner grilling before implementation.
- `bridge/gtkb-dashboard-operations-cockpit-advisory-disposition-001.md` - Prime Builder `adapt` disposition, narrowing the advisory to a first reliability/scope slice.
- `bridge/gtkb-dashboard-operations-cockpit-advisory-disposition-002.md` - Loyal Opposition `GO`, explicitly authorizing only the disposition and requiring owner decisions before implementation proposal.
- `DELIB-20265586` - PAUTH owner decision for snapshot-bound project implementation authority.
- `DELIB-20265873` through `DELIB-20265876` - owner answers to the four WI-3433 advisory-gate questions.
- `SPEC-ADVISORY-DASHBOARD-COUNTERS-001` and the bridge thread that verified it - prior dashboard-counter semantics that must remain true in generated/static dashboard surfaces.
- Existing dashboard implementation history, including the dashboard control-plane and headless start-mode bridge threads, is background only; this proposal does not reopen their verified scope.

## Target Path Rationale

- `groundtruth-kb/src/groundtruth_kb/dashboard.py` - package-facing dashboard generation, setup text, shortcut labels, subject/scope metadata, and status semantics.
- `groundtruth-kb/src/groundtruth_kb/dashboard_service.py` - loopback/local-only refresh service defaults and labels, if implementation needs explicit local-only presentation without behavior expansion.
- `groundtruth-kb/src/groundtruth_kb/cli.py` - package-facing `gt dashboard` command help or output wording, if needed to make the CLI-primary setup path visible.
- `groundtruth-kb/tests/test_dashboard.py` - package dashboard regression tests for metric status semantics, copyable paths, combined subject labels, local-only refresh posture, and `gt dashboard` setup guidance.
- `scripts/gtkb_dashboard/refresh_dashboard_db.py` - repo-local dashboard current-metric status generation and evidence-source/status semantics.
- `scripts/gtkb_dashboard/generate_grafana_dashboard.py` and `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` - generated Grafana dashboard JSON and its generator, including titles, tags, path affordances, status labels, and setup instructions.
- `docs/gtkb-dashboard/index.html`, `docs/gtkb-dashboard/grafana/README.md`, and `docs/gtkb-dashboard/grafana/PACKAGE-INTEGRATION.md` - dashboard scaffold/support pages that should show package CLI primary setup and loopback/local-only assumptions without formal-artifact mutation.
- `platform_tests/scripts/test_gtkb_dashboard_grafana.py` and `platform_tests/scripts/test_dashboard_subject_selector.py` - static/generated dashboard tests for generated JSON, subject/scope presentation, local path affordances, and package CLI setup text.

## Implementation Plan

1. Add or adjust small helper functions for current metric statuses so zero, warning, and blocker/failing cases are distinguishable and no metric is hardcoded to a failing color when the canonical source data is clean.
2. Update package and repo-local dashboard surfaces to expose combined operations explicitly: GT-KB platform state and active adopter/application state should be distinguishable through badges, source labels, or equivalent table/field names.
3. Replace local workspace path `Open` links or labels with copyable path text/shortcut fields, leaving browser-open behavior only for true HTTP/HTTPS links.
4. Update dashboard setup and refresh presentation to show local/loopback-only operation and package CLI primary commands (`gt dashboard init`, `gt dashboard install`, `gt dashboard start`, `gt dashboard stop`) while allowing maintainer scripts to remain secondary.
5. Regenerate `docs/gtkb-dashboard/grafana/dashboards/gtkb-dashboard.json` from the generator if generator changes alter the checked-in dashboard.
6. Add/update focused tests that pin metric status correctness, subject/scope labeling, copyable path behavior, local-only refresh labels, and package CLI setup wording.

## Out Of Scope

- Broad dashboard visual redesign or first-viewport layout overhaul.
- Refresh-service CSRF/rate-limit/public-network hardening.
- Formal GOV/SPEC/ADR/DCL/PB/REQ artifact mutation.
- Database schema changes unless Loyal Opposition explicitly requires them before `GO`.
- Agent Red application subtree work or lifecycle-independent application repository changes.
- New project work items or PAUTH scope expansion.

## Spec-Derived Test Plan

After `GO` and implementation-start authorization, Prime Builder will run:

- `python -m pytest groundtruth-kb/tests/test_dashboard.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_gtkb_dashboard_grafana.py platform_tests/scripts/test_dashboard_subject_selector.py platform_tests/groundtruth_kb/specs/test_spec_advisory_dashboard_counters.py -q --tb=short`
- `python scripts/gtkb_dashboard/generate_grafana_dashboard.py` when generator changes require JSON refresh, followed by a focused diff review of the generated dashboard JSON.
- `ruff check` on touched Python files.
- `ruff format --check` on touched Python files.

The post-implementation report will map each verification command to the cited specs and owner decisions, including explicit assertions for:

- Current metric status correctness for clean/warning/failing source states.
- Advisory/dashboard counter labels and state distinctions required by `SPEC-ADVISORY-DASHBOARD-COUNTERS-001`.
- Combined GT-KB plus adopter/application scope presentation with explicit badges/source labels.
- Copyable local path behavior and no misleading local `Open` affordances.
- Loopback/local-only refresh-service presentation.
- Package-facing `gt dashboard` setup commands as the primary visible path.

## Pre-Filing Preflight

- Applicability preflight: `PASS` against this proposal draft before dispatch. Required specs missing: `[]`. Advisory specs missing: `[]`.
- Clause preflight: `PASS` against this proposal draft before dispatch. Clauses evaluated: `5`; `must_apply`: `4`; `may_apply`: `1`; `not_applicable`: `0`; must-apply evidence gaps: `0`; blocking gaps: `0`.
- The bridge-propose helper is expected to rerun its governed credential scan, author-metadata injection, and bridge-compliance audit before writing the dispatchable numbered bridge file.

## Requested Loyal Opposition Review

Please review whether this first implementation slice satisfies the WI-3433 advisory disposition `GO`, the four owner decisions, the project PAUTH, and the cited spec/bridge requirements. A `GO` should authorize only the target paths and scope above; a `NO-GO` should identify the exact missing requirement, target-path issue, or owner-decision evidence gap.
