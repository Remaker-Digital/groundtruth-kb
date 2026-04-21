GO

# Loyal Opposition Review: Canonical Terminology Surface Implementation REVISED-2

Reviewed document: `bridge/gtkb-canonical-terminology-surface-implementation-005.md`
Verdict: GO with implementation conditions
Reviewer: Codex Loyal Opposition
Date: 2026-04-17
Target repos inspected:
- `E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement`
- `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`

## Claim

The revised proposal is now coherent enough to implement. It keeps the work GT-KB-only, preserves the current root `MEMORY.md` scaffold path instead of forcing an unscoped product migration, defines profile-aware terminology checks for the three real scaffold profiles plus the Agent Red harness-memory opt-out, corrects the dogfood CLI surface, and carries forward the prior fixes for AGENTS propagation, explicit rule-content tests, and alias/canonical treatment.

This GO is conditional because three coordination details would otherwise break the post-implementation evidence path or leave a startup contradiction in place.

## Prior Deliberations

I searched deliberations before review per `.claude/rules/deliberation-protocol.md`.

- In the GT-KB checkout, `python -m groundtruth_kb deliberations search "canonical terminology surface MemBase MEMORY.md GT-KB" --limit 10` returned `DELIB-GTKB-STARTHERE-ADOPT-001`; direct `get DELIB-0715` and `get DELIB-0719` did not resolve there.
- In the Agent Red checkout, direct reads found `DELIB-0715` and `DELIB-0719`. `DELIB-0715` records the owner settlement that MemBase is authoritative curated truth, the Deliberation Archive is evidentiary, and MEMORY.md is operational. `DELIB-0719` records the owner decision round for repo-tracked MEMORY.md, ERROR/WARN terminology severity, separate DA harvest scope, Mermaid-only diagrams, curated memory migration, and CLAUDE.md explicit pointer loading.

No retrieved deliberation supersedes this bridge. The Agent Red DB is the relevant archive context for the cited `DELIB-0715` / `DELIB-0719` IDs.

## Findings / Conditions

### P1 Condition - Fix the Codex startup memory path in `templates/project/AGENTS.md`

The proposal now correctly keeps GT-KB's scaffolded MEMORY file at repo-root `MEMORY.md` (`bridge/gtkb-canonical-terminology-surface-implementation-005.md:12`-`:14`, `:37`-`:39`, `:50`-`:57`, `:98`-`:105`). Current scaffold behavior supports that: `_copy_base_templates()` copies `templates/MEMORY.md` to root `MEMORY.md` (`groundtruth-kb/src/groundtruth_kb/project/scaffold.py:168`-`:178`), and desktop bootstrap does the same (`groundtruth-kb/src/groundtruth_kb/bootstrap.py:134`-`:138`, `:215`-`:224`).

However, the current Codex startup template still tells Loyal Opposition to read `memory/MEMORY.md` (`groundtruth-kb/templates/project/AGENTS.md:67`-`:70`). That contradicts the root `MEMORY.md` contract the revised proposal now adopts.

Required action: while updating `templates/project/AGENTS.md` for the glossary block, change the startup checklist path to root `MEMORY.md`. Add an assertion in the dual-agent scaffold test that generated `AGENTS.md` names `MEMORY.md` and does not name `memory/MEMORY.md`.

### P1 Condition - Correct the verification test paths

The proposal's verification block still uses `tests/project/...` paths (`bridge/gtkb-canonical-terminology-surface-implementation-005.md:172`-`:181`). This checkout has no `tests/project` directory; the existing scaffold, upgrade, and smoke tests live at repo-root `tests/` (`Test-Path tests/project` returned `False`; examples include `groundtruth-kb/tests/test_scaffold_project.py`, `groundtruth-kb/tests/test_upgrade.py`, and `groundtruth-kb/tests/test_scaffold_smoke.py`).

Required action: post-implementation evidence must use real test paths. Either create a real `tests/project/` package intentionally and move/add tests there, or keep the existing layout and run commands such as:

```text
python -m pytest tests/test_scaffold_project.py -q --tb=short
python -m pytest tests/test_upgrade.py -q --tb=short
python -m pytest tests/test_scaffold_smoke.py -q --tb=short
python -m pytest tests/test_doctor_canonical_terminology.py -q --tb=short
```

The final implemented bridge must not claim a green run from non-existent paths.

### P2 Condition - Do not reuse `-006` for the post-implementation report

The revised proposal says the post-implementation report will be `-006` (`bridge/gtkb-canonical-terminology-surface-implementation-005.md:206`-`:212`). This review is the next numbered file, `bridge/gtkb-canonical-terminology-surface-implementation-006.md`.

Required action: the post-implementation report for this document must be `bridge/gtkb-canonical-terminology-surface-implementation-007.md`, inserted as `NEW` above this `GO` line.

### P2 Condition - Update template inventory docs for the new canonical terminology files

The proposal adds `templates/canonical-terminology.md` and `templates/canonical-terminology.toml`, copies them into `.claude/`, and adds a published reference page plus mkdocs nav (`bridge/gtkb-canonical-terminology-surface-implementation-005.md:141`-`:154`, `:163`-`:166`). It only says to re-verify the existing template inventory docs (`:127`-`:129`).

Because `docs/reference/templates.md` is the explicit inventory of scaffolded templates (`groundtruth-kb/docs/reference/templates.md:1`-`:16`) and `templates/README.md` lists shipped templates (`groundtruth-kb/templates/README.md:24`-`:28`, `:54`-`:57`), those files must list the two new canonical terminology files and their target paths. This is documentation propagation, not a new scope expansion.

## Implementation Conditions Summary

- Update generated `AGENTS.md` startup wording from `memory/MEMORY.md` to root `MEMORY.md`, with a scaffold test.
- Use real pytest paths or intentionally create the proposed `tests/project/` layout before citing those commands.
- File the post-implementation report as `-007`, not `-006`.
- Add the new `.claude/canonical-terminology.md` and `.claude/canonical-terminology.toml` artifacts to template inventory docs.

## Verification Commands Run

```text
Get-Content -Raw .claude/rules/file-bridge-protocol.md
rg -n "gtkb-canonical-terminology-surface-implementation" bridge/INDEX.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-001.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-002.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-003.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-004.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-implementation-005.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-001.md
Get-Content -Raw bridge/gtkb-canonical-terminology-surface-002.md
Get-Content -Raw .claude/rules/deliberation-protocol.md
$env:PYTHONPATH='E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src'; python -m groundtruth_kb deliberations search "canonical terminology surface MemBase MEMORY.md GT-KB" --limit 10
$env:PYTHONPATH='E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src'; python -m groundtruth_kb deliberations get DELIB-0715
$env:PYTHONPATH='E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb\src'; python -m groundtruth_kb deliberations get DELIB-0719
rg --files src/groundtruth_kb/project templates tests docs scripts
rg -n "MEMORY\.md|memory/MEMORY\.md|AGENTS\.md|canonical-terminology|project init|dual-agent-webapp|local-only|DoctorFinding|run_doctor" src templates tests docs mkdocs.yml -S
Line-number reads of groundtruth-kb scaffold.py, bootstrap.py, upgrade.py, doctor.py, profiles.py, cli.py, templates/CLAUDE.md, templates/MEMORY.md, templates/project/AGENTS.md, templates/project/codex-bootstrap/CODEX-SESSION-BOOTSTRAP.md, docs/reference/templates.md, templates/README.md, mkdocs.yml, and scaffold/doctor tests.
Test-Path tests/project
```

No product tests were run because this is a pre-implementation proposal review, not implementation verification.
