NEW

# gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority — Projects Skill Query Authority and Backlog Filtering

bridge_kind: prime_proposal
Document: gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority
Version: 001
Author: Prime Builder (Codex)
Date: 2026-06-30T18:22:00Z

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: codex-interactive-2026-06-30-projects-skill-query-authority
author_model: GPT-5 Codex
author_model_version: current Codex desktop runtime
author_model_configuration: default Codex desktop coding-agent configuration

Project Authorization: PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-AUTO-SPEC-INTAKE-C2C7FF-PROJECTS-SKILL-FILTERING
Project: PROJECT-BACKLOG-TRIAGE-AND-HYGIENE
Work Item: WI-AUTO-SPEC-INTAKE-C2C7FF

target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/backlog.py", "groundtruth-kb/src/groundtruth_kb/backlog/**", "groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", "platform_tests/scripts/test_cli_backlog*.py", "platform_tests/scripts/test_projects_cli.py", "platform_tests/scripts/test_project_authorization.py", ".claude/skills/projects/SKILL.md", ".codex/skills/projects/SKILL.md", ".agent/skills/projects/SKILL.md", ".api-harness/skills/projects/SKILL.md", ".cursor/skills/projects/SKILL.md"]

implementation_scope: source | cli_extension | skill_adapter | tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Owner identified the current Projects skill and CLI access pattern as defective for backlog/project work. The immediate failure mode is that agents must either over-fetch backlog data and locally post-filter it or bypass the intended skill/CLI surface. That violates the desired authority boundary: project/backlog access and mutation should go through governed skill/CLI surfaces, not direct SQLite/MemBase access or ad hoc local query code.

This proposal implements a bounded repair: extend the Projects/backlog CLI query surface so agents can filter and sort backlog/project data through the governed CLI itself, including field-specific filters, pattern matching, range specifications, and approval-state filtering. It also updates the Projects skill documentation and generated adapters so agents are instructed to use the CLI surface as the only supported project/backlog access path.

## Specification Links

- `SPEC-INTAKE-c2c7ff` — owner-stated requirement: Projects skill/CLI must be the only supported way agents access or update backlog/project information; direct MemBase/SQLite access for backlog/project work is prohibited; query/filter/sort support must cover all backlog values, pattern matching, and range specifications.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — implementation must proceed through an implementation proposal, LO review, implementation report, and verification chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites its governing spec and links the implementation to that requirement.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal includes Project Authorization, Project, and Work Item metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification must map the new query-authority requirement to concrete CLI and skill-adapter tests.
- `GOV-STANDING-BACKLOG-001` — the backlog remains the MemBase-backed canonical work-item source; implementation must improve its governed access surface rather than create another backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — changes under `groundtruth-kb/src/groundtruth_kb/project/` must preserve GT-KB root/application placement boundaries and must not reinterpret project/backlog queries as application-placement authority.
- `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — Projects skill guidance changes touch multiple harness skill surfaces and must preserve equivalent backlog/project access behavior across applicable harnesses.

## Prior Deliberations

- `INTAKE-1f0b4c4c` — owner requirement and confirmation for Projects skill backlog authority and filtering. This proposal implements that requirement.
- `INTAKE-f8bc08a3` — prior intake favoring CLI surfaces as primary mutating UI for GT-KB artifact operations. This proposal applies that same principle specifically to project/backlog read and mutation workflows.

## Owner Decisions / Input

Owner directive in the current session: "Do not defer this. It is an urgent requirement that should proceed immediately to an active Work Item and implementation proposal." The requirement was confirmed from `INTAKE-1f0b4c4c` into `SPEC-INTAKE-c2c7ff`; the auto-created work item `WI-AUTO-SPEC-INTAKE-C2C7FF` was attached to `PROJECT-BACKLOG-TRIAGE-AND-HYGIENE`; and `PAUTH-PROJECT-BACKLOG-TRIAGE-AND-HYGIENE-WI-AUTO-SPEC-INTAKE-C2C7FF-PROJECTS-SKILL-FILTERING` authorizes bounded implementation.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-c2c7ff` states the operative product requirement, and the governance specs above define proposal linkage, backlog authority, and verification obligations. No additional owner decision is required before implementation.

## Cross-Harness Disposition

This slice changes the governed Projects/backlog CLI surface and the Projects skill instructions/adapters used by multiple harnesses. The intended behavior is parity: every applicable harness must route backlog/project read and mutation work through the same governed CLI/skill contract, including the new filter/sort capabilities, and none may document or rely on direct SQLite/MemBase backlog access.

| Harness surface | Disposition |
| --- | --- |
| Claude skill surface | Update `.claude/skills/projects/SKILL.md` as the canonical Projects skill guidance for CLI-only backlog/project access and the new filter/sort grammar. |
| Codex skill surface | Update `.codex/skills/projects/SKILL.md` to mirror the canonical Projects guidance and preserve Prime Builder automation behavior through the CLI-only contract. |
| Cursor skill surface | Update `.cursor/skills/projects/SKILL.md` to the same Projects guidance so Cursor Prime Builder sessions do not bypass the CLI. |
| Antigravity / agent skill surface | Update `.agent/skills/projects/SKILL.md` to the same Projects guidance when present, preserving equivalent agent behavior. |
| API harness skill surface | Update `.api-harness/skills/projects/SKILL.md` to the same Projects guidance when present, preserving equivalent headless/API-harness behavior. |

No typed waiver is requested. The implementation must either update every targeted skill surface consistently or narrow `target_paths` and explain why a surface is not applicable in the implementation report.

## Spec-Derived Verification Plan

Spec-to-test mapping:

```text
SPEC-INTAKE-c2c7ff
  - Add/extend CLI tests proving backlog/project query surfaces support:
    - exact-value filters for every surfaced backlog field, including approval_state;
    - field-specific pattern matching;
    - numeric/date/string range filters where field type supports ranges;
    - explicit sort keys and direction;
    - project-membership-aware filtering without direct SQLite access in agent workflows.
  - Add/extend skill-adapter tests proving the Projects skill documents the CLI-only backlog/project access rule and the supported query/filter/sort controls.

GOV-STANDING-BACKLOG-001
  - Add/extend tests proving no new backlog authority is introduced and query output continues to read canonical MemBase-backed work_items/project membership data through the existing CLI/service layer.

ADR-ISOLATION-APPLICATION-PLACEMENT-001
  - Verify the implementation changes only the GT-KB project/backlog CLI/query surface and does not alter adopter application placement, `applications/` boundaries, or project/application terminology.

DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 and DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
  - Run bridge applicability and clause preflights against this proposal.

DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
  - Implementation report must include the focused CLI/skill tests and the preflight results.
```

Expected verification commands:

```text
python -m pytest platform_tests/scripts/test_cli_backlog*.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_authorization.py platform_tests/skills/test_projects_skill_adapter.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/backlog.py groundtruth-kb/src/groundtruth_kb/backlog groundtruth-kb/src/groundtruth_kb/project/lifecycle.py platform_tests/scripts/test_cli_backlog*.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_authorization.py platform_tests/skills/test_projects_skill_adapter.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/backlog.py groundtruth-kb/src/groundtruth_kb/backlog groundtruth-kb/src/groundtruth_kb/project/lifecycle.py platform_tests/scripts/test_cli_backlog*.py platform_tests/scripts/test_projects_cli.py platform_tests/scripts/test_project_authorization.py platform_tests/skills/test_projects_skill_adapter.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority
```

## Risk / Rollback

Risk is concentrated in CLI query semantics and agent documentation. The implementation must preserve existing `gt backlog list` behavior for current flags and add new filters/sorts compatibly. It must not introduce a second backlog authority, direct agent-facing SQLite guidance, or hidden local post-processing requirements. Rollback is a single commit reverting the CLI/query extensions, tests, and Projects skill adapter changes.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi-auto-spec-intake-c2c7ff-projects-skill-backlog-query-authority`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

feat — adds a governed query capability to close a backlog/project access defect, with tests and skill-adapter documentation.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
