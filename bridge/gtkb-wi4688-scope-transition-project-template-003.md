NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: abf38f9d-9205-44ac-a4c4-92490c175d3e
author_model: claude-opus-4-8
author_model_version: opus-4-8
author_model_configuration: Interactive Prime Builder session (::init gtkb pb); envelope-disposition drive

# Implementation Report — WI-4688 Slice B: Scope-Transition Project Template

bridge_kind: implementation_report
Document: gtkb-wi4688-scope-transition-project-template
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Responds-To: bridge/gtkb-wi4688-scope-transition-project-template-002.md (GO)

Project Authorization: PAUTH-PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-ENVELOPE-DISPOSITION-AND-AUTONOMOUS-DISPATCH
Work Item: WI-4688

target_paths: ["config/project-templates/scope-transition.toml", "scripts/scope_transition_project.py", "platform_tests/scripts/test_scope_transition_project_template.py"]

## Recommended Commit Type

Recommended commit type: `feat` — new reusable scope-transition project template + deterministic instantiation helper (net-new capability surface).

## Summary

Implements WI-4688 Slice B per the GO at `-002`: a reusable scope-transition project template (declarative skeleton + deterministic instantiation helper) so a GT-KB→application-exclusive transition is instantiated, not hand-built, per SPEC-1830. Member work items map 1:1 to the five `GOV-SCOPE-TRANSITION-PROCEDURE-001` steps (Slice A, created earlier this session). With WI-4688 Slice A (procedure) + Slice B (template) both landed, WI-4688 is complete.

## Files Changed (3 new, in-root)

- `config/project-templates/scope-transition.toml` — declarative template: `[template]` (id, `procedure_spec = GOV-SCOPE-TRANSITION-PROCEDURE-001`, name_pattern, purpose, target_outcome, scope_note) + five `[[work_items]]` (one per procedure step: self-test, triage, drive-blockers, flip-config, record-disposition), parameterized on `{application}`.
- `scripts/scope_transition_project.py` — deterministic instantiation helper: pure `load_template` / `plan_project` / `render_commands` + `instantiate(dry_run=True)` (dry-run default; `--apply` performs creation via the governed `gt projects create` / `gt backlog add` CLI). CLI `--application <name> [--apply]`.
- `platform_tests/scripts/test_scope_transition_project_template.py` — six spec-derived tests (well-formedness, procedure-spec citation, 5-step coverage, application substitution, governed-command rendering, dry-run non-mutation).

## Specification Links (carried forward)

- `GOV-SCOPE-TRANSITION-PROCEDURE-001` v1 — the procedure the template instantiates.
- `SPEC-1830` — operational procedures must be code (motivates the deterministic helper).
- `GOV-STANDING-BACKLOG-001` — governed project/WI creation.
- `GOV-FILE-BRIDGE-AUTHORITY-001`; `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`; `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (all paths in-root); `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`.

## Spec-to-Test Mapping (executed)

| Specification | Test | Result |
|---|---|---|
| `GOV-SCOPE-TRANSITION-PROCEDURE-001` (template instantiates 5 steps + cites procedure) | `test_template_defines_five_procedure_steps`, `test_template_cites_procedure_spec`, `test_template_is_well_formed` | pass |
| `GOV-SCOPE-TRANSITION-PROCEDURE-001` (deterministic plan per application) | `test_plan_project_substitutes_application` | pass |
| `SPEC-1830` (deterministic instantiation, not hand-built) | `test_render_commands_are_governed_gt_calls`, `test_instantiate_dry_run_produces_project_skeleton` | pass |
| `GOV-STANDING-BACKLOG-001` (dry-run mutates nothing; `--apply` uses governed CLI) | `test_instantiate_dry_run_produces_project_skeleton` (asserts `subprocess.run` not called) | pass |

## Verification Commands & Results

```text
python -m pytest platform_tests/scripts/test_scope_transition_project_template.py -q
  => 6 passed

python -m ruff check scripts/scope_transition_project.py platform_tests/scripts/test_scope_transition_project_template.py
  => All checks passed!

python -m ruff format --check <same two files>
  => 2 files already formatted

python scripts/scope_transition_project.py --application "Agent Red"   # CLI dry-run smoke
  => [DRY-RUN] PROJECT-SCOPE-TRANSITION-AGENT-RED :: Scope Transition: GT-KB to Agent Red
     (5 member-WI steps listed; 6 governed gt commands would run with --apply)
```

## Owner Decisions / Input

- AUQ 2026-06-25 (DELIB-20265891): "Drive formal work inline; AUQ each."
- AUQ 2026-06-25 (WI-4688 structure): "Two slices: procedure (A) then template (B)" + "Keep driving WI-4688 Slice B now," authorizing this implementation.

## Prior Deliberations

- `DELIB-20265891` — envelope-disposition drive owner decision.
- `GOV-SCOPE-TRANSITION-PROCEDURE-001` provenance — WI-4688 Slice A (the procedure this template instantiates).
- No prior deliberation conflicts (no pre-existing project-template mechanism to reconcile against).

## Risk / Rollback

- Risk: low — three new isolated files; the helper defaults to dry-run (no project created without explicit `--apply`); tests mock `subprocess` so no MemBase mutation. No existing behavior changed.
- Rollback: delete the three new files. The Slice-A procedure spec remains (owner-ratified).
