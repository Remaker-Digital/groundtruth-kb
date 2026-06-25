NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: abf38f9d-9205-44ac-a4c4-92490c175d3e
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: Interactive Prime Builder session (::init gtkb pb); envelope-disposition drive

# Implementation Proposal — WI-4688 Slice B: Scope-Transition Project Template

bridge_kind: prime_proposal
Document: gtkb-wi4688-scope-transition-project-template
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4688

target_paths: ["config/project-templates/scope-transition.toml", "scripts/scope_transition_project.py", "platform_tests/scripts/test_scope_transition_project_template.py"]

## Summary

Implements WI-4688 Slice B: a **reusable scope-transition project template** so a GT-KB→application-exclusive scope transition is *instantiated, not hand-built*. Per SPEC-1830 (operational procedures must be code), the template is a declarative skeleton plus a deterministic instantiation helper, not a prose checklist. The Slice-A procedure `GOV-SCOPE-TRANSITION-PROCEDURE-001` (created earlier this session) defines the 5 steps; this template instantiates a project whose member work items map to those steps.

## Specification Links

- `GOV-SCOPE-TRANSITION-PROCEDURE-001` v1 — the procedure this template instantiates (the 5-step sequence).
- `SPEC-1830` — Operational Procedures Must Be Code, Not Conversation (motivates the deterministic helper over a hand-built checklist).
- `GOV-STANDING-BACKLOG-001` — projects/work-items authority (the template creates governed project + WI records).
- `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (all paths in-root); `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-SCOPE-TRANSITION-PROCEDURE-001` v1 defines the procedure; this proposal builds the reusable template that instantiates it. No new/revised requirement needed.

## Implementation Plan

1. **`config/project-templates/scope-transition.toml`** (new scaffold) — declarative template:
   - `[template]`: `id = "scope-transition"`, `procedure_spec = "GOV-SCOPE-TRANSITION-PROCEDURE-001"`, a `name_pattern` (e.g., `"Scope Transition: GT-KB to {application}"`), `purpose`, `target_outcome`, `scope_note` citing the procedure.
   - `[[work_items]]` × 5 — one per procedure step (self-test, triage at-risk WIs, drive blockers to VERIFIED, flip active-subject config, record disposition), each with `title`, `component`, `origin`, `priority`. Titles parameterize the target application name.
2. **`scripts/scope_transition_project.py`** (new source/CLI) — deterministic instantiation helper:
   - `load_template(path) -> dict`, `plan_project(template, application) -> ProjectPlan` (pure, testable), and `instantiate(template, application, *, dry_run=True)` which creates the project + member WIs through the `groundtruth_kb` projects API. CLI: `instantiate --template <path> --application <name> [--apply]` (dry-run by default; `--apply` performs the creation). No new project is created during tests (dry-run).
3. **`platform_tests/scripts/test_scope_transition_project_template.py`** (new test) — asserts: the template parses and is well-formed; it cites `GOV-SCOPE-TRANSITION-PROCEDURE-001`; it defines exactly the five procedure-step work items; and `plan_project(...)` / `instantiate(..., dry_run=True)` produce the expected project skeleton (name, purpose, 5 member-WI titles) without mutating MemBase.

## Spec-Derived Verification Plan (spec-to-test mapping)

| Specification | Test / verification | Command |
|---|---|---|
| `GOV-SCOPE-TRANSITION-PROCEDURE-001` (template instantiates the 5 steps + cites the procedure) | `test_template_defines_five_procedure_steps`, `test_template_cites_procedure_spec` | `python -m pytest platform_tests/scripts/test_scope_transition_project_template.py -q` |
| `SPEC-1830` (deterministic instantiation, not hand-built) | `test_instantiate_dry_run_produces_project_skeleton` (helper plans the project deterministically; dry-run, no MemBase write) | same suite |
| `GOV-STANDING-BACKLOG-001` (governed project/WI creation) | dry-run asserts the planned project + 5 WIs match the template; `--apply` path uses the governed projects API | same suite |

Code-quality gates on touched files: `python -m ruff check <files>` and `python -m ruff format --check <files>`.

## Prior Deliberations

- `DELIB-20265891` — envelope-disposition drive owner decision (the authorization for this slice).
- `GOV-SCOPE-TRANSITION-PROCEDURE-001` provenance — WI-4688 Slice A (the procedure this template instantiates).
- No prior deliberation conflicts (deliberation search 2026-06-25 found no opposing decision and no existing project-template mechanism to reconcile against).


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- AUQ 2026-06-25 (DELIB-20265891): owner chose "Drive formal work inline; AUQ each."
- AUQ 2026-06-25 (WI-4688 structure): owner chose "Two slices: procedure (A) then template (B)" and "Keep driving WI-4688 Slice B now," authorizing this template implementation.

## Risk / Rollback

- Risk: low — three new files; the instantiation helper defaults to dry-run, so no project is created without an explicit `--apply`. Tests do not mutate MemBase.
- Rollback: delete the three new files. The Slice-A procedure spec remains (owner-ratified). New, isolated surface — no existing behavior changed.
