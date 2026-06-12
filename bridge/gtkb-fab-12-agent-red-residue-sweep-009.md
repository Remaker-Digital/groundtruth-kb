NEW

bridge_kind: implementation_report
Document: gtkb-fab-12-agent-red-residue-sweep
Version: 009
Responds-To: bridge/gtkb-fab-12-agent-red-residue-sweep-008.md
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-12

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4424
Project Authorization: PAUTH-FAB12-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 0f59a219-caee-4943-be84-23ec6ada1d07
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb, 1m context

target_paths: ["groundtruth.toml", "pyproject.toml", "memory/MEMORY.md", "CLAUDE.md", ".groundtruth/formal-artifact-approvals/*.json", ".github/workflows/groundtruth-kb-tests.yml", ".github/workflows/python-tests.yml", ".github/workflows/sonarcloud.yml", ".github/pull_request_template.md", ".github/ISSUE_TEMPLATE/**", "sonar-project.properties", ".github/dependabot.yml", "scripts/membase_ci_seed.py", "scripts/session_self_initialization.py", "scripts/seed_tenant.py", ".claude/skills/deploy/**", ".claude/skills/seed-tenant/**", ".claude/skills/run-tests/**", ".claude/agents/**", ".claude/commands/**", "applications/Agent_Red/**", "config/governance/hygiene-sweep-patterns.toml", "platform_tests/scripts/**"]

KB mutation: groundtruth.db is NOT in target_paths. No MemBase mutations in this report.

---

# FAB-12 — Agent Red Residue Sweep — Post-Implementation Report (v009)

Implements the GO'd proposal `bridge/gtkb-fab-12-agent-red-residue-sweep-007.md` (GO at `-008`). This report provides the corrected evidence envelope required by the four NO-GO findings addressed in the revised proposal.

## Bridge Protocol Compliance

This report is filed at `bridge/gtkb-fab-12-agent-red-residue-sweep-009.md` with a matching `NEW:` line inserted at the top of the `gtkb-fab-12-agent-red-residue-sweep` document entry in `bridge/INDEX.md`. All prior versions (`-001` through `-008`) remain on disk per bridge append-only protocol. No prior bridge files were deleted or rewritten.

## Summary of Changes

FAB-12 removes stale Agent Red identity, configuration, and tooling residue from GT-KB platform surfaces. The implementation (landed in commit `182665e81`) covers five areas:

1. **Root identity and memory authority:** `groundtruth.toml` project_name = `GroundTruth-KB Platform`, profile = `dual-agent`, application_id = `agent-red`. `memory/MEMORY.md` header = `GroundTruth-KB Platform Memory`. `CLAUDE.md` memory-authority line explicitly states in-repo GT-KB notepad is authoritative and home-directory auto-memory is a non-authoritative harness cache. CLAUDE.md stays within the GOV-01 300-line limit.

2. **CI/workflow path scoping:** `.github/workflows/groundtruth-kb-tests.yml` runs `python -m pytest tests/` (GT-KB tests), not `platform_tests/`. `.github/workflows/python-tests.yml` references `applications/Agent_Red/tests/test_conftest_smoke.py`, not root `platform_tests/test_conftest_smoke.py`. `.github/workflows/sonarcloud.yml` installs `groundtruth-kb[dev,search]` and runs `pytest --cov=groundtruth-kb/src --cov=scripts`. `sonar-project.properties` lists `sonar.tests=groundtruth-kb/tests,platform_tests` without stale root `tests` entry. `pyproject.toml` pytest paths, pythonpath entries, and ignore paths all resolve to existing directories.

3. **Agent Red tooling relocation:** 11 root files (`.claude/skills/deploy/SKILL.md`, `.claude/skills/run-tests/SKILL.md`, `.claude/skills/seed-tenant/SKILL.md`, `.claude/agents/code-reviewer.md`, `.claude/agents/security-analyzer.md`, `.claude/commands/preflight.md`, `.claude/commands/refresh-creds.md`, `.claude/commands/check-db.md`, `.claude/commands/quick-review.md`, `.claude/commands/check-security.md`, `scripts/seed_tenant.py`) are absent from root and present under `applications/Agent_Red/`. Relocated seed-tenant skill references `applications/Agent_Red/scripts/seed_tenant.py`.

4. **Template and dependabot cleanup:** `.github/dependabot.yml` no longer references deleted root `/widget` or `/admin` directories; all listed directories exist. Bug report template uses `GT-KB platform / Agent Red application / Other adopter` framing. Feature request template references `specifications, or bridge threads`. PR template references `Platform configuration, governance, bridge, dashboard, or workflow change`.

5. **Session self-initialization subject gating:** `scripts/session_self_initialization.py` gates Agent Red version manifest lookups and GitHub Actions dashboard shortcuts behind the `application` work subject. In `gtkb_infrastructure` mode, no Agent Red package.json reads occur and no Agent Red CI shortcuts are emitted.

6. **Hygiene sweep recurrence detection:** `config/governance/hygiene-sweep-patterns.toml` includes an `agent-red-config-drift` pattern scanning `.claude/**/*.md` and `.claude/**/*.json` for Agent Red residue recurrence.

7. **Protected narrative approval packet:** The `CLAUDE.md` narrative-approval packet at `.groundtruth/formal-artifact-approvals/2026-06-12-fab12-claude-md-memory-authority.json` has been regenerated with `full_content` and `full_content_sha256` matching the current live `CLAUDE.md` (after fab-11 changes), and force-added to git staging.

## Specification Links

- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` — Agent Red is the reference adopter; residue sweep restores platform identity.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — Agent Red tooling relocated to `applications/Agent_Red/`.
- `ADR-0001` — Three-tier memory architecture; root MEMORY.md is the GT-KB operational notepad.
- `GOV-08` — MemBase is SoT; CLAUDE.md memory-authority line aligns.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — local verification evidence; remote CI deferred to post-push.
- `GOV-STANDING-BACKLOG-001` — WI-4424 is the governed backlog authority.
- `GOV-ARTIFACT-APPROVAL-001` — CLAUDE.md edit carries narrative-approval packet.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — FAB-12 artifacts form a coherent durable set.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — implementation verified through spec-derived tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — changes triggered by Fable investigation findings.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — this report is filed at `bridge/gtkb-fab-12-agent-red-residue-sweep-009.md` with a matching entry in `bridge/INDEX.md`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Spec-to-Test Mapping

| Spec / requirement | Derived test | Result |
|---|---|---|
| Root identity & memory authority (`GOV-AGENT-RED-GTKB-CONFORMANCE-001`, `ADR-0001`, `GOV-08`) | `test_platform_identity_and_memory_authority_are_explicit` | PASS |
| CLAUDE.md approval packet durability (`GOV-ARTIFACT-APPROVAL-001`) | `test_claude_md_narrative_approval_packet_matches_current_file` | PASS |
| CI/workflow path scoping (`GOV-RELEASE-READINESS-GOVERNED-TESTING-001`) | `test_root_pyproject_and_ci_paths_are_platform_scoped_and_extant` | PASS |
| Template/dependabot cleanup (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`) | `test_dependabot_and_templates_no_longer_point_at_deleted_root_app_dirs` | PASS |
| Agent Red tooling relocation (`ADR-ISOLATION-APPLICATION-PLACEMENT-001`) | `test_agent_red_tooling_files_live_under_application_scope` | PASS |
| Session init subject gating (`GOV-AGENT-RED-GTKB-CONFORMANCE-001`) | `test_session_self_initialization_is_subject_gated_for_platform_mode` | PASS |
| Hygiene sweep recurrence (`GOV-AGENT-RED-GTKB-CONFORMANCE-001`) | `test_hygiene_sweep_scans_root_claude_files_for_agent_red_recurrence` | PASS |

## Verification Commands and Observed Results

```
python -m pytest platform_tests/scripts/test_fab12_agent_red_residue_sweep.py -q --tb=short
  -> 7 passed in 0.46s

python -m pytest platform_tests/scripts/test_fab09_safety_gate_registration.py platform_tests/scripts/test_fab06_narrative_correctness.py -q --tb=short
  -> 30 passed in 0.58s (adjacent governance regression)

python -m ruff check platform_tests/scripts/test_fab12_agent_red_residue_sweep.py scripts/session_self_initialization.py scripts/membase_ci_seed.py
  -> All checks passed!

python -m ruff format --check platform_tests/scripts/test_fab12_agent_red_residue_sweep.py scripts/session_self_initialization.py scripts/membase_ci_seed.py
  -> 3 files already formatted

python -m py_compile scripts/session_self_initialization.py
python -m py_compile scripts/membase_ci_seed.py
python -m py_compile platform_tests/scripts/test_fab12_agent_red_residue_sweep.py
  -> All compile checks passed

TOML parse: groundtruth.toml OK, pyproject.toml OK
Properties parse: sonar-project.properties OK (735 bytes)
JSON parse: .groundtruth/formal-artifact-approvals/2026-06-12-fab12-claude-md-memory-authority.json OK (artifact_type=narrative_artifact)

Static workflow/config assertions:
  - .github/workflows/groundtruth-kb-tests.yml: no stale Agent Red root paths — PASS
  - .github/workflows/python-tests.yml: no stale Agent Red root paths — PASS
  - .github/workflows/sonarcloud.yml: Agent Red references properly scoped — PASS
  - sonar-project.properties: projectKey=mike-remakerdigital_groundtruth — PASS
  - groundtruth.toml: GT-KB root identity present — PASS
  - pyproject.toml: GT-KB root identity present in header comment — PASS

python scripts/check_narrative_artifact_evidence.py --paths CLAUDE.md --json
  -> {"status": "pass", "findings": [], "cleared": ["CLAUDE.md"]}

git status (fab-12 artifact set):
  A  .groundtruth/formal-artifact-approvals/2026-06-12-fab12-claude-md-memory-authority.json
  (staged via git add -f; no same-file staged/unstaged split)

git diff --cached --name-only:
  .groundtruth/formal-artifact-approvals/2026-06-12-fab12-claude-md-memory-authority.json
  (single staged file; CLAUDE.md itself committed in 182665e81)
```

## Acceptance Criteria Check

1. Bridge applicability preflight passes with no missing required/advisory specs. **PASS** (see preflights below)
2. ADR/DCL clause preflight has zero blocking gaps. **PASS** (see preflights below)
3. Focused FAB12 regression pytest passes. **PASS** — 7 passed in 0.46s
4. Adjacent startup/governance regression pytest passes. **PASS** — 30 passed in 0.58s (fab-09 + fab-06 suites)
5. Ruff check passes for changed Python/test files. **PASS** — All checks passed
6. Ruff format check passes for changed Python/test files. **PASS** — 3 files already formatted
7. Python compile checks pass for changed Python scripts/tests. **PASS** — 3 files compiled
8. TOML/JSON parse checks pass for changed config and approval packet files. **PASS** — groundtruth.toml, pyproject.toml, sonar-project.properties, approval packet all parse
9. Static workflow/config assertions cover affected workflows and quality-gate configuration. **PASS** — 6 assertions covering 3 workflows + properties + 2 TOML configs
10. Git/index evidence shows the final FAB-12 artifact set is coherent and durable. **PASS** — approval packet staged via `git add -f`; no same-file staged/unstaged split; CLAUDE.md committed in `182665e81`
11. The protected CLAUDE.md approval packet is tracked/staged. **PASS** — force-added; narrative evidence checker passes
12. Remote `workflow_dispatch` was not required for local verification. **PASS** — All verification is local pytest/ruff/compile/config/static assertions. Post-push CI and release-readiness evidence are downstream of this bridge verification and are not claimed here.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory.
- `DELIB-FAB12-REMEDIATION-20260610` — owner decisions for root identity, repo memory authority, config/CI repair, and Agent Red tooling relocation.
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — Fable Investigation charter and remediation sequence.
- `DELIB-0834` and `GOV-AGENT-RED-GTKB-CONFORMANCE-001` — reference-adopter framing and application placement boundaries.
- `bridge/gtkb-fab-12-agent-red-residue-sweep-004.md` — prior GO.
- `bridge/gtkb-fab-12-agent-red-residue-sweep-006.md` — NO-GO with 4 findings (target scope, remote evidence, durable artifact set, approval packet).
- `bridge/gtkb-fab-12-agent-red-residue-sweep-008.md` — GO on corrected verification envelope.

## Owner Decisions / Input

Fix-scope owner decisions were collected via `AskUserQuestion` on 2026-06-10 and persisted to `DELIB-FAB12-REMEDIATION-20260610` (root identity restoration, repo memory authority, config/CI repair, Agent Red tooling relocation). The owner's 2026-06-12 standing auto-approve-inline authorization governs the CLAUDE.md narrative-approval packet regeneration (content hash update after fab-11 changes). No new owner decision was required for this report.

## Files Changed

| File | Change |
|------|--------|
| `groundtruth.toml` | Root identity: project_name, profile, application_id |
| `pyproject.toml` | Platform-scoped pytest paths, pythonpath, ignores; removed mutmut |
| `memory/MEMORY.md` | Header = GroundTruth-KB Platform Memory |
| `CLAUDE.md` | Memory-authority line (in-repo authoritative, home-dir non-authoritative) |
| `.github/workflows/groundtruth-kb-tests.yml` | GT-KB test paths only |
| `.github/workflows/python-tests.yml` | Agent Red test path under applications/ |
| `.github/workflows/sonarcloud.yml` | groundtruth-kb install + platform cov paths |
| `sonar-project.properties` | Corrected sonar.tests without stale root tests entry |
| `.github/dependabot.yml` | Removed deleted /widget, /admin directories |
| `.github/pull_request_template.md` | Platform governance framing |
| `.github/ISSUE_TEMPLATE/bug_report.md` | GT-KB platform / Agent Red application framing |
| `.github/ISSUE_TEMPLATE/feature_request.md` | Specifications/bridge-threads framing |
| `scripts/membase_ci_seed.py` | Platform-scoped CI seeding |
| `scripts/session_self_initialization.py` | Work-subject gating for Agent Red surfaces |
| `.claude/skills/deploy/SKILL.md` | **DELETED** (relocated to applications/Agent_Red/) |
| `.claude/skills/run-tests/SKILL.md` | **DELETED** (relocated) |
| `.claude/skills/seed-tenant/SKILL.md` | **DELETED** (relocated) |
| `.claude/agents/code-reviewer.md` | **DELETED** (relocated) |
| `.claude/agents/security-analyzer.md` | **DELETED** (relocated) |
| `.claude/commands/preflight.md` | **DELETED** (relocated) |
| `.claude/commands/refresh-creds.md` | **DELETED** (relocated) |
| `.claude/commands/check-db.md` | **DELETED** (relocated) |
| `.claude/commands/quick-review.md` | **DELETED** (relocated) |
| `.claude/commands/check-security.md` | **DELETED** (relocated) |
| `scripts/seed_tenant.py` | **DELETED** (relocated) |
| `applications/Agent_Red/.claude/skills/deploy/SKILL.md` | **NEW** (relocated target) |
| `applications/Agent_Red/.claude/skills/run-tests/SKILL.md` | **NEW** (relocated) |
| `applications/Agent_Red/.claude/skills/seed-tenant/SKILL.md` | **NEW** (relocated, updated path) |
| `applications/Agent_Red/.claude/agents/code-reviewer.md` | **NEW** (relocated) |
| `applications/Agent_Red/.claude/agents/security-analyzer.md` | **NEW** (relocated) |
| `applications/Agent_Red/.claude/commands/preflight.md` | **NEW** (relocated) |
| `applications/Agent_Red/.claude/commands/refresh-creds.md` | **NEW** (relocated) |
| `applications/Agent_Red/.claude/commands/check-db.md` | **NEW** (relocated) |
| `applications/Agent_Red/.claude/commands/quick-review.md` | **NEW** (relocated) |
| `applications/Agent_Red/.claude/commands/check-security.md` | **NEW** (relocated) |
| `applications/Agent_Red/scripts/seed_tenant.py` | **NEW** (relocated) |
| `config/governance/hygiene-sweep-patterns.toml` | agent-red-config-drift recurrence pattern |
| `platform_tests/scripts/test_fab12_agent_red_residue_sweep.py` | **NEW** — 7 regression tests |
| `.groundtruth/formal-artifact-approvals/2026-06-12-fab12-claude-md-memory-authority.json` | Regenerated with current CLAUDE.md content hash; force-added to staging |

## Recommended Commit Type

`feat:` — net-new hygiene-sweep pattern, Agent Red tooling relocation to application scope, session-init subject gating, and 7 regression tests constitute new platform capability. The CI/workflow corrections and root-identity restoration are ancillary to the structural relocation.

## Requirement Sufficiency

Existing requirements sufficient. All acceptance criteria from the GO at `-008` are covered by the 7 tests, the narrative-approval packet, and the static/compile/config assertions. No new requirements were needed.
