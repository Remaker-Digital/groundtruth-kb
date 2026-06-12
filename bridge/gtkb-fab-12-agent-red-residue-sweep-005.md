NEW

bridge_kind: implementation_report
Document: gtkb-fab-12-agent-red-residue-sweep
Version: 005
Author: Codex Prime Builder
Date: 2026-06-12
Responds-To: bridge/gtkb-fab-12-agent-red-residue-sweep-004.md
Implements: bridge/gtkb-fab-12-agent-red-residue-sweep-003.md
Recommended commit type: fix:

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4424
Project Authorization: PAUTH-FAB12-20260610

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

target_paths: ["groundtruth.toml", "pyproject.toml", "memory/MEMORY.md", "CLAUDE.md", ".groundtruth/formal-artifact-approvals/*.json", ".github/workflows/groundtruth-kb-tests.yml", ".github/workflows/python-tests.yml", ".github/pull_request_template.md", ".github/ISSUE_TEMPLATE/**", "sonar-project.properties", ".github/dependabot.yml", "scripts/membase_ci_seed.py", "scripts/session_self_initialization.py", "scripts/seed_tenant.py", ".claude/skills/deploy/**", ".claude/skills/seed-tenant/**", ".claude/skills/run-tests/**", ".claude/agents/**", ".claude/commands/**", "applications/Agent_Red/**", "config/governance/hygiene-sweep-patterns.toml", "platform_tests/scripts/**"]

---

# FAB-12 Agent-Red Residue Sweep - Implementation Report

## Implementation Claim

Implemented the FAB-12 GO scope from `bridge/gtkb-fab-12-agent-red-residue-sweep-004.md` against the revised proposal `bridge/gtkb-fab-12-agent-red-residue-sweep-003.md`.

The implementation stayed in-root and did not read or depend on `C:/Users/micha/.claude/...` home-cache content. It did not mutate the external Agent Red repository, did not perform the deferred ISOLATION-018 full platform/application config split, and does not claim the deferred divergent-home-cache lesson merge as complete.

## Implementation Authorization

Prime Builder activated the live GO authorization packet:

```text
python scripts\implementation_authorization.py activate --bridge-id gtkb-fab-12-agent-red-residue-sweep
```

Observed result: latest status `GO`, authorization `PAUTH-FAB12-20260610`, work item `WI-4424`, packet hash `sha256:103ff229e72074af7704e2c988b5480d7a1f27e298bbd3d9d68441e9943e96af`.

## Summary

- HYG-012: changed root `groundtruth.toml` project identity from Agent Red to `GroundTruth-KB Platform` while retaining `[scoped_service].application_id = "agent-red"`.
- HYG-016: retitled repo `memory/MEMORY.md` to `# GroundTruth-KB Platform Memory` and amended the `CLAUDE.md` platform-memory line so repo `memory/MEMORY.md` is authoritative and home-directory auto-memory is a non-authoritative harness cache. A narrative approval packet was written at `.groundtruth/formal-artifact-approvals/2026-06-12-fab12-claude-md-memory-authority.json`.
- HYG-024/HYG-043: repaired root `pyproject.toml` platform identity/path assumptions, removed the phantom root mutmut block and root `tests/**` Ruff ignore, corrected stale CI/Sonar/Dependabot/template paths, and updated `scripts/membase_ci_seed.py` fixture/test references.
- HYG-034: moved Agent Red-specific skills, agents, commands, and `seed_tenant.py` under `applications/Agent_Red/`; stripped platform-mode Agent Red package/path fallback reads from `scripts/session_self_initialization.py`; and restored `.claude/**/*.md` / `.claude/**/*.json` hygiene sweep coverage for recurrence detection.
- Added focused FAB12 regression coverage and updated existing startup/governance tests to assert the new platform/application boundary.

## Files Changed

FAB12 implementation files:

- `groundtruth.toml`
- `memory/MEMORY.md`
- `CLAUDE.md`
- `.groundtruth/formal-artifact-approvals/2026-06-12-fab12-claude-md-memory-authority.json` (ignored working governance packet; parsed and hash-verified locally)
- `pyproject.toml`
- `.github/workflows/groundtruth-kb-tests.yml`
- `.github/workflows/python-tests.yml`
- `.github/workflows/sonarcloud.yml`
- `.github/dependabot.yml`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `sonar-project.properties`
- `scripts/membase_ci_seed.py`
- `scripts/session_self_initialization.py`
- `config/governance/hygiene-sweep-patterns.toml`
- `platform_tests/scripts/test_fab12_agent_red_residue_sweep.py`
- `platform_tests/scripts/test_groundtruth_governance_adoption.py`
- `platform_tests/scripts/test_session_self_initialization.py`

Relocated Agent Red files:

- `.claude/skills/deploy/**` to `applications/Agent_Red/.claude/skills/deploy/**`
- `.claude/skills/run-tests/**` to `applications/Agent_Red/.claude/skills/run-tests/**`
- `.claude/skills/seed-tenant/**` to `applications/Agent_Red/.claude/skills/seed-tenant/**`
- `.claude/agents/code-reviewer.md` to `applications/Agent_Red/.claude/agents/code-reviewer.md`
- `.claude/agents/security-analyzer.md` to `applications/Agent_Red/.claude/agents/security-analyzer.md`
- `.claude/commands/preflight.md` to `applications/Agent_Red/.claude/commands/preflight.md`
- `.claude/commands/refresh-creds.md` to `applications/Agent_Red/.claude/commands/refresh-creds.md`
- `.claude/commands/check-db.md` to `applications/Agent_Red/.claude/commands/check-db.md`
- `.claude/commands/quick-review.md` to `applications/Agent_Red/.claude/commands/quick-review.md`
- `.claude/commands/check-security.md` to `applications/Agent_Red/.claude/commands/check-security.md`
- `scripts/seed_tenant.py` to `applications/Agent_Red/scripts/seed_tenant.py`

Residual local note: after patch-based file moves, empty root directories under `.claude/skills/{deploy,run-tests,seed-tenant}/references` may remain on disk because the shell deletion path was blocked by the local LO file-safety hook. No root files remain in those relocated skill directories, and Git records the former tracked files as deleted at root and newly present under `applications/Agent_Red/`.

## Same-File Scope Disclosure

The repository was already dirty before FAB12 implementation. Some FAB12-touched files had same-file staged/unstaged overlap from earlier bridge work, notably `CLAUDE.md`, `pyproject.toml`, `scripts/session_self_initialization.py`, and `platform_tests/scripts/test_session_self_initialization.py`. This implementation preserved pre-existing staged content and did not revert or unstage unrelated work.

The helper report plan also saw broad unrelated dirty worktree drift from other bridge items. The file list above is the FAB12 implementation scope.

## Specification Links

- `GOV-AGENT-RED-GTKB-CONFORMANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-0001`
- `GOV-08`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Prior Deliberations

- `DELIB-FAB12-REMEDIATION-20260610` records the four owner dispositions implemented here.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` charters the Fable Investigation remediation set.
- `DELIB-0834` and `GOV-AGENT-RED-GTKB-CONFORMANCE-001` provide the reference-adopter and tooling-reference framing.
- `bridge/gtkb-fab-12-agent-red-residue-sweep-003.md` is the approved revised proposal.
- `bridge/gtkb-fab-12-agent-red-residue-sweep-004.md` is the Loyal Opposition GO verdict.

## Specification-Derived Verification

| Spec / requirement | Executed verification evidence |
|---|---|
| `GOV-AGENT-RED-GTKB-CONFORMANCE-001` | `platform_tests/scripts/test_fab12_agent_red_residue_sweep.py` asserts root `groundtruth.toml` identifies `GroundTruth-KB Platform`, root `.github` templates are platform-neutral, and root relocated Agent Red tool files no longer exist. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | FAB12 regression asserts `deploy`, `run-tests`, `seed-tenant`, Agent Red agents/commands, and `seed_tenant.py` live under `applications/Agent_Red/`; `test_groundtruth_governance_adoption.py` now expects those application-owned skills under the application subtree. |
| `ADR-0001` + `GOV-08` | FAB12 regression asserts `memory/MEMORY.md` is titled `# GroundTruth-KB Platform Memory`, `CLAUDE.md` names repo memory authoritative and home-directory auto-memory non-authoritative, `CLAUDE.md` is <=300 lines, and the narrative packet hash matches current `CLAUDE.md`. |
| `GOV-ARTIFACT-APPROVAL-001` | `.groundtruth/formal-artifact-approvals/2026-06-12-fab12-claude-md-memory-authority.json` parses as JSON and contains the full current `CLAUDE.md` content and matching SHA-256 hash. |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` | FAB12 regression asserts `groundtruth-kb-tests.yml`, `python-tests.yml`, `sonarcloud.yml`, `sonar-project.properties`, and `dependabot.yml` no longer point at stale root test/app paths and only reference extant configured directories. `workflow_dispatch` was not executed locally because no remote push/run was performed in this implementation pass. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused FAB12 pytest, adjacent startup/governance pytest, Ruff check, Ruff format check, Python compile checks, and TOML/JSON parse checks passed. |

## Commands Run

### Bridge Preflights

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-fab-12-agent-red-residue-sweep --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-fab-12-agent-red-residue-sweep-005.md
```

Observed result: `preflight_passed: true`, packet hash `sha256:4fdf330f968ce69588785c302e8a946a8538192bf6ccf13d52d7b04ed9c247b4`, `missing_required_specs: []`, `missing_advisory_specs: []`. Non-blocking warning: `warnings.missing_parent_dirs: ["tests/**"]`, inherited from the operative target-path text.

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-fab-12-agent-red-residue-sweep --content-file .gtkb-state\bridge-impl-reports\drafts\gtkb-fab-12-agent-red-residue-sweep-005.md
```

Observed result: `must_apply: 3`, `may_apply: 2`, `Evidence gaps in must_apply clauses: 0`, `Blocking gaps (gate-failing): 0`.

### Verification

```text
python -m pytest platform_tests\scripts\test_fab12_agent_red_residue_sweep.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-fab12-b
```

Observed result: `7 passed in 0.46s`.

```text
python -m pytest platform_tests\scripts\test_groundtruth_governance_adoption.py platform_tests\scripts\test_session_self_initialization.py platform_tests\scripts\test_collect_dev_environment_inventory.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-fab12-reg-d
```

Observed result: `106 passed in 64.00s`.

```text
python -m ruff check scripts\membase_ci_seed.py scripts\session_self_initialization.py platform_tests\scripts\test_fab12_agent_red_residue_sweep.py platform_tests\scripts\test_groundtruth_governance_adoption.py platform_tests\scripts\test_session_self_initialization.py applications\Agent_Red\scripts\seed_tenant.py
```

Observed result: `All checks passed!`.

```text
python -m ruff format --check scripts\membase_ci_seed.py scripts\session_self_initialization.py platform_tests\scripts\test_fab12_agent_red_residue_sweep.py platform_tests\scripts\test_groundtruth_governance_adoption.py platform_tests\scripts\test_session_self_initialization.py applications\Agent_Red\scripts\seed_tenant.py
```

Observed result: `6 files already formatted`.

```text
python -m py_compile scripts\session_self_initialization.py scripts\membase_ci_seed.py applications\Agent_Red\scripts\seed_tenant.py platform_tests\scripts\test_fab12_agent_red_residue_sweep.py
```

Observed result: command exited 0.

```text
python -c "import json, tomllib, pathlib; [tomllib.loads(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['pyproject.toml','groundtruth.toml','config/governance/hygiene-sweep-patterns.toml']]; json.loads(pathlib.Path('.groundtruth/formal-artifact-approvals/2026-06-12-fab12-claude-md-memory-authority.json').read_text(encoding='utf-8')); print('config artifacts ok')"
```

Observed result: `config artifacts ok`.

## Not Run

- GitHub Actions `workflow_dispatch` runs for the four CI lanes were not executed in this local implementation pass. The report relies on local path/config regressions plus static workflow assertions; remote CI verification remains a post-push/remote-run activity.
- No out-of-root home-cache reconciliation was attempted; that work remains deferred exactly as stated in REVISED-003 and GO-004.

## Risk And Residual Follow-Up

- Because `.groundtruth/formal-artifact-approvals/` is gitignored for session-noise control, the FAB12 approval packet is present and verified in the working tree but will require the normal governance/commit handling if a future commit needs to preserve it as a tracked packet.
- Empty root skill directories may remain locally after patch-based moves; no root skill files remain, and tests assert file-level relocation.
- Agent Red-local commands still invoke some legacy `scripts/...` operational helpers from the repository root. FAB12 moved the approved Agent Red command surfaces under `applications/Agent_Red/.claude/`; broader command dependency relocation is outside this slice unless LO requires it.

## Conclusion

FAB12 implementation is complete within the revised GO scope and is ready for Loyal Opposition verification.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
