NEW

bridge_kind: prime_proposal
Document: gtkb-fab-12-agent-red-residue-sweep
Version: 001
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-10

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4424
Project Authorization: PAUTH-FAB12-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: d2f32e6b-5441-45b3-b355-097a2507f5f7
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["groundtruth.toml", "pyproject.toml", "memory/MEMORY.md", "CLAUDE.md", ".github/workflows/groundtruth-kb-tests.yml", ".github/workflows/python-tests.yml", "sonar-project.properties", ".github/dependabot.yml", "scripts/membase_ci_seed.py", "scripts/session_self_initialization.py", "scripts/seed_tenant.py", ".claude/skills/deploy/**", ".claude/skills/seed-tenant/**", ".claude/skills/run-tests/**", ".claude/agents/**", ".claude/commands/**", "applications/Agent_Red/**", "config/governance/hygiene-sweep-patterns.toml", "platform_tests/scripts/**"]

No KB mutation: all FAB-12 changes are config/CI/narrative/source/file-relocation; no `groundtruth.db` write. `groundtruth.db` is intentionally NOT in target_paths. Existing-WI overlap is absorbed by scope; any backlog-state reconciliation is a separate post-VERIFIED operational step, not part of this proposal.

---

# FAB-12 — Agent-Red Residue Sweep Across Platform Surfaces

WI-4424 (FAB-12) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-012, HYG-016, HYG-024, HYG-034, HYG-043
(plus the absorbed sub-findings: .claude/agents+commands Agent-Red scope, .github PR/issue templates,
dependabot.yml stale dirs). Source advisory: `bridge/gtkb-fable-investigation-advisory-001.md`.

Common root cause: platform surfaces still self-identify as, or silently resolve to, the Agent Red
adopter — the exact failure class the 2026-05-04 tooling-reference narrowing prohibits
(`GOV-AGENT-RED-GTKB-CONFORMANCE-001`).

## Summary

- **HYG-012 (config identity):** the platform-root canonical `groundtruth.toml` sets
  `project_name = "Agent Red Customer Experience"`, live-read by 14 modules, so `gt config`/doctor at
  the platform root self-identify as the adopter.
- **HYG-016 (memory authority):** two divergent session-memory stores are live — repo `memory/MEMORY.md`
  (titled "# Agent Red Memory") and the home-directory auto-memory (276 files / 1.37 MB), which the
  harness mechanically auto-loads every session despite CLAUDE.md L12's in-root mandate.
- **HYG-024 (root build config):** `pyproject.toml` is Agent Red's config — wrong identity header, phantom
  `mutmut`/`ruff` paths (`src/`, `tests/` absent at root), and `addopts --timeout=30` that breaks any
  pytest environment lacking `pytest-timeout`.
- **HYG-043 (red CI):** all four CI test/quality lanes (GT-KB Tests, Python Tests, SonarCloud, RC Gate)
  fail every triggering push on stale `tests/`→`platform_tests/` + Agent-Red-relocation paths; the
  v0.7.0-rc1 tag was cut with a red lane. `dependabot.yml` targets deleted `/widget`,`/admin` and omits
  the platform package.
- **HYG-034 (tooling resolution):** `session_self_initialization.py` silently falls back into
  `applications/Agent_Red` for path/version/test evidence; generically-named platform skills
  `deploy`/`seed-tenant`/`run-tests` + `scripts/seed_tenant.py` + the `.claude/agents`+`commands` are all
  Agent-Red-scoped, so unqualified platform tooling operates on the adopter.

## Specification Links

- `GOV-AGENT-RED-GTKB-CONFORMANCE-001` — the 2026-05-04 tooling-reference narrowing; the cluster's
  governing principle (HYG-012, HYG-034, the whole theme).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — Agent-Red tooling relocates UNDER `applications/Agent_Red/`
  (its contract-correct home); see Isolation Placement Compliance below.
- `ADR-0001` (Three-Tier Memory Architecture) — governs the HYG-016 memory-store authority decision
  (MemBase / MEMORY.md notepad / Deliberation Archive).
- `GOV-08` (Knowledge Database is the single source of truth) — governs the config-identity authority and
  the memory-notepad authority.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` — the four CI lanes are the governed test-evidence surface
  this restores (HYG-043, HYG-024 addopts).
- `GOV-STANDING-BACKLOG-001` — WI-4424 is the governed backlog authority; this cluster absorbs the listed
  overlapping backlog items without re-filing them.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact governance for the config/narrative/skill
  surfaces under change.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `NEW` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-012/016/024/034/043).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB12-REMEDIATION-20260610` — this cluster's four owner dispositions (below).
- `DELIB-0834` / `GOV-AGENT-RED-GTKB-CONFORMANCE-001` — the reference-adopter framing + tooling-reference
  narrowing this cluster operationalizes.
- _The full platform/application config split is the ISOLATION-018 cutover thread; this cluster does the
  residue sweep, not the split._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB12-REMEDIATION-20260610`:

1. **HYG-012 = Migrate [project] identity to GT-KB; keep [scoped_service].** Rename the `[project]`
   identity to the GT-KB platform; keep `[scoped_service] application_id='agent-red'` as the intended
   application binding; bump stale `scaffold_version`; regression-test the 14 consumers.
2. **HYG-016 = Repo authoritative; home-dir = harness cache; amend CLAUDE.md L12.** Make repo
   `memory/MEMORY.md` the single authoritative ADR-0001 notepad (retitled), migrate divergent home-dir
   lessons in, and amend CLAUDE.md L12 to classify the home-dir path as a non-authoritative harness cache.
3. **HYG-024 + HYG-043 = Fix all platform-affecting config + CI now; defer full split.** Minimal pyproject
   repair + all four stale CI-path fixes + `pytest-timeout` + dependabot repair; restore green CI; leave
   the full platform/application config split to ISOLATION-018.
4. **HYG-034 = Full relocation + strip session-init fallbacks.** Relocate the three Agent-Red skills +
   `scripts/seed_tenant.py` + AR agents/commands under `applications/Agent_Red/.claude/`; replace the
   `session_self_initialization.py` Agent_Red reads with platform-scoped equivalents; un-exclude
   `.claude/**` from the hygiene sweep.

## Requirement Sufficiency

**Existing requirements sufficient.** The dispositions are fixed by `DELIB-FAB12-REMEDIATION-20260610`;
the governing specifications (`GOV-AGENT-RED-GTKB-CONFORMANCE-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
`ADR-0001`, `GOV-08`, `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`) already constrain the
tooling-reference, isolation-placement, memory-architecture, source-of-truth, and release-testing
surfaces. No new or revised requirement is needed before implementation. The CLAUDE.md L12 amendment is a
text reconciliation to existing intent, not a new requirement.

## Scope and Boundaries

In scope: the four decisions above across all five findings + the absorbed sub-findings. Out of scope and
explicitly excluded: the full platform/application config SPLIT (ISOLATION-018 cutover); migrating the
Agent Red spec corpus (separate); any deploy/push; and the external Agent Red lifecycle repository (this
cluster touches only in-root `applications/Agent_Red/` surfaces). This proposal **absorbs** the advisory's
listed existing-WI overlap for FAB-12 — the sonar project-key item (3417, partly repaired at S363), the
`.github` template/workflow Agent-Red-residue items (the 3419/3430/3431/3466 set), and the memory
index-template + topic-split items (4346/4347) — folding them into WI-4424's scope and describing them
here rather than re-filing. Backlog-state reconciliation for those items is a post-VERIFIED operational
step.

## Proposed Implementation

**Area 1 — HYG-012 root config identity.** Edit `groundtruth.toml` `[project]`: rename `project_name`,
`owner`, `copyright` to the GT-KB platform identity; bump `scaffold_version`; KEEP `[scoped_service]`
unchanged. Inventory what each of the 14 `project_name` consumers emits; add regression tests asserting
doctor/scaffold/dashboard outputs carry the platform identity (not "Agent Red Customer Experience").

**Area 2 — HYG-016 memory authority.** Retitle repo `memory/MEMORY.md` off "# Agent Red Memory" to a
platform title; migrate the divergent home-dir lessons into the repo store (or its topic files); amend
CLAUDE.md L12 (narrative-artifact-approval packet at implementation time) to designate repo
`memory/MEMORY.md` authoritative and the home-directory path a non-authoritative harness cache, with a
wrap-time reconciliation note. Stays within the GOV-01 300-line CLAUDE.md limit (small edit).

**Area 3 — HYG-024 + HYG-043 config + CI.** `pyproject.toml`: GT-KB identity header; remove the phantom
`[tool.mutmut]` and `tests/**` `ruff` per-file-ignore paths; resolve the `addopts --timeout=30` mismatch
(scope it or declare `pytest-timeout` a hard dep in the CI envs that run root pytest). CI: point
`groundtruth-kb-tests.yml` pytest at `tests/` (relative to `groundtruth-kb`); drop/re-point the two
nonexistent `python-tests.yml` core-shard files; remove `tests` from `sonar.tests` and install
`pytest-timeout` in the sonar pytest step; fix `membase_ci_seed.py` `DEFAULT_FIXTURE` to the
`applications/Agent_Red/tests/fixtures/` path; repair `dependabot.yml` (`/widget`,`/admin` →
`applications/Agent_Red/*` + add a `groundtruth-kb/` job). Verify each lane via `workflow_dispatch`.

**Area 4 — HYG-034 Agent-Red tooling relocation.** Move the `deploy`, `seed-tenant`, `run-tests` skill
dirs + `scripts/seed_tenant.py` + the Agent-Red `.claude/agents` (code-reviewer, security-analyzer) and
the Agent-Red `.claude/commands` (preflight, refresh-creds, check-db, quick-review, check-security) under
`applications/Agent_Red/.claude/` / `applications/Agent_Red/scripts/`. Replace the
`session_self_initialization.py` Agent_Red path/version/test reads with platform-scoped (or
subject-gated) equivalents. Remove `.claude/**` from the `hygiene-sweep-patterns.toml` exclusion for the
Agent-Red pattern so recurrence is mechanically detectable. Re-scope the `.github/pull_request_template.md`
+ ISSUE_TEMPLATE to platform-neutral (or GT-KB) vocabulary.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: FAB-12 is isolation-**positive**. It MOVES Agent-Red tooling
INTO `applications/Agent_Red/.claude/` and `applications/Agent_Red/scripts/` — the contract-correct home
for adopter files — and removes Agent-Red identity/residue from platform-root config, memory, CI, and
session-start surfaces. It writes no out-of-root artifact (this bridge file is under `E:\GT-KB\bridge\`),
touches only in-root `applications/Agent_Red/` (not the external Agent Red repository), and the full
platform/application config split is explicitly deferred to ISOLATION-018.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-AGENT-RED-GTKB-CONFORMANCE-001` (HYG-012/034) | test: platform-root `groundtruth.toml` `project_name` resolves to GT-KB (not "Agent Red Customer Experience"); doctor/scaffold output carries platform identity; no platform skill/agent/command remains under `.claude/` resolving to Agent Red |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (HYG-034) | test: `deploy`/`seed-tenant`/`run-tests` + `seed_tenant.py` + AR agents/commands live under `applications/Agent_Red/`; `session_self_initialization.py` reads no `applications/Agent_Red` path on a platform-subject session; hygiene sweep no longer excludes `.claude/**` |
| `ADR-0001` + `GOV-08` (HYG-016) | test: repo `memory/MEMORY.md` is not titled "Agent Red Memory"; CLAUDE.md L12 designates repo store authoritative + home-dir as cache; CLAUDE.md stays ≤300 lines (GOV-01) |
| `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` (HYG-024/043) | test: each of the four CI lanes passes on a `workflow_dispatch` run; root `pyproject` contains no path that does not exist; `dependabot.yml` references only extant dirs + covers `groundtruth-kb/` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` for the identity/relocation regression tests + `ruff check` AND `ruff format --check` on changed Python |

## Acceptance Criteria

1. **Area 1:** root `groundtruth.toml` identifies GT-KB; `[scoped_service]` retained; the 14 consumers
   emit platform identity; regression tests pass.
2. **Area 2:** repo `memory/MEMORY.md` retitled + authoritative; CLAUDE.md L12 amended (with packet) and
   ≤300 lines; home-dir lessons migrated.
3. **Area 3:** root `pyproject` is platform-identified with only extant paths; all four CI lanes green on
   `workflow_dispatch`; dependabot repaired.
4. **Area 4:** the three skills + `seed_tenant.py` + AR agents/commands live under `applications/Agent_Red/`;
   session-init reads no adopter path on platform-subject sessions; hygiene sweep detects `.claude/**`
   recurrence; `.github` templates platform-neutral.
5. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-12-agent-red-residue-sweep-001.md` with a matching `NEW` entry at the top of
`bridge/INDEX.md`; append-only, no prior bridge version deleted or rewritten. `GOV-FILE-BRIDGE-AUTHORITY-001`
is honored — nothing implements until Loyal Opposition records `GO` on this thread.

## Risk and Rollback

- **Risk — renaming `project_name` breaks a consumer:** inventory all 14 consumers first; add regression
  tests on doctor/scaffold/dashboard output before merging. **Rollback:** revert the one-file config edit.
- **Risk — CLAUDE.md edit (protected narrative):** gated by the narrative-artifact-approval packet at
  implementation time; the L12 change is a small text reconciliation. **Rollback:** revert the edit.
- **Risk — session_self_initialization.py is load-bearing startup code:** the Agent_Red-fallback removal
  gets bridge review + per-path regression evidence; subject-gating preserves behavior for application
  sessions. **Rollback:** restore the fallback branch.
- **Risk — relocating skills/commands changes owner-invocable surfaces:** the relocation preserves the
  skill bodies under `applications/Agent_Red/.claude/`; platform sessions simply no longer surface them
  generically. **Rollback:** move the dirs back.
- **Risk — CI changes:** verified per-lane via `workflow_dispatch` before relying on push triggers.

## Recommended Implementation Routing

**Opus/Codex-supervised for Areas 1, 2, 4** (config-identity with 14 consumers, the protected CLAUDE.md
narrative, and the load-bearing session-init relocation). **Area 3 (CI/config path fixes)** is the most
mechanical and cheap-model-draftable once GO'd, with Opus/Codex confirming the workflow_dispatch evidence.
Coordinate Area 3 with any sibling CI work; sequence the session-init change (Area 4) carefully.

## Recommended Commit Type

`fix:` — repairs platform misidentification (config, memory, CI) and removes Agent-Red tooling residue,
with `refactor:`-class file relocations (skills/agents/commands → `applications/Agent_Red/`).
