# NO-GO: GT-KB Mass Adoption Readiness Proposal Review

Verdict: NO-GO

Reviewed proposal: `bridge/gtkb-mass-adoption-readiness-001.md`
Target checkout inspected: `E:\Claude-Playground\CLAUDE-PROJECTS\groundtruth-kb`
Target commit inspected: `2a324c6`
Reviewer: Codex Loyal Opposition
Date: 2026-04-15

## Claim

The proposal's top-level answer is correct: GroundTruth-KB is not ready for unqualified mass adoption across all 12 owner-stated components.

The proposal is not ready for implementation as written. It combines a valid product direction with stale current-state claims, an unresolved command-surface change, credential-management risk, and a 37.5-55.5 day roadmap that is too broad to GO as one implementation packet.

## Prior Deliberations

I searched the deliberation archive before review.

- `SPEC-GTKB-SCOPE` exists in Agent Red `groundtruth.db` as `verified`, `authority=stated`, and defines the 12 first-class GT-KB components. Query output showed title `GroundTruth-KB Product Scope: 12 First-Class Components`, changed by `owner`, changed at `2026-04-15T22:34:02+00:00`.
- Agent Red deliberation search for `GroundTruth KB mass adoption SPEC-GTKB-SCOPE` returned relevant prior records including `DELIB-0469`, `DELIB-0633`, and `DELIB-0474`.
- `DELIB-0633` is directly relevant: its executive verdict was "promising but still alpha" and "not yet proven as a repeatable software-factory system across projects."
- `DELIB-0469` framed the same bootstrap gap as a layered product problem, not a simple package-only feature.
- `DELIB-0474` recommended staged execution with explicit boundaries, human-controlled cloud apply, and external validation before external developer claims.
- GroundTruth-KB's own `groundtruth.db` returned no deliberations for `GroundTruth-KB mass adoption readiness` or `SPEC-GTKB-SCOPE`, so Agent Red is the authoritative archive source for these cited deliberations.

## Evidence

- Proposal scope and objective: `bridge/gtkb-mass-adoption-readiness-001.md:6`, `bridge/gtkb-mass-adoption-readiness-001.md:31-35`.
- Proposal says a `pip install groundtruth-kb` user does not get project scaffolding with Terraform or GitHub CI: `bridge/gtkb-mass-adoption-readiness-001.md:20`.
- Proposal targets `gt init` as the single all-component entry point: `bridge/gtkb-mass-adoption-readiness-001.md:33-35`, `bridge/gtkb-mass-adoption-readiness-001.md:68`, `bridge/gtkb-mass-adoption-readiness-001.md:209`.
- Proposal says current dev setup assumes Windows and Python 3.14: `bridge/gtkb-mass-adoption-readiness-001.md:48`, `bridge/gtkb-mass-adoption-readiness-001.md:199`.
- Proposal includes `gt bridge start` and built-in auth-token management: `bridge/gtkb-mass-adoption-readiness-001.md:67-69`, `bridge/gtkb-mass-adoption-readiness-001.md:211`.
- Current `gt init` creates only `groundtruth.toml` and `groundtruth.db`: `src/groundtruth_kb/cli.py:80-105`.
- Current scaffold entry point is `gt project init`, with profiles `local-only`, `dual-agent`, and `dual-agent-webapp`: `src/groundtruth_kb/cli.py:558-610`, `src/groundtruth_kb/project/profiles.py:23-60`.
- Product architecture intentionally separates Layer 1 `gt init` from Layer 2 `gt project init`: `docs/architecture/product-split.md:18-35`.
- CLI reference explicitly says full scaffold users should use `gt project init` or `gt bootstrap-desktop`, not `gt init`: `docs/reference/cli.md:26-47`, `docs/reference/cli.md:321-347`.
- `pyproject.toml` requires Python `>=3.11`, advertises 3.11-3.13, and sets ruff target `py311`: `pyproject.toml:11`, `pyproject.toml:20-23`, `pyproject.toml:76`.
- CI already tests Python 3.11, 3.12, 3.13 on Ubuntu and has a cross-platform Ubuntu/Windows/macOS job on Python 3.12: `.github/workflows/ci.yml:24-30`, `.github/workflows/ci.yml:100-105`, `.github/workflows/ci.yml:123-164`.
- Current top-level CLI help has no `bridge` command. Command run: `PYTHONPATH=src python -m groundtruth_kb --help`; output listed `assert`, `bootstrap-desktop`, `config`, `deliberations`, `project`, `scaffold`, etc., but no `bridge`.
- Targeted verification passed: `python -m pytest tests/test_scaffold_project.py tests/test_doctor.py tests/test_bridge_import_hygiene.py -q --tb=short` returned `43 passed, 1 warning in 1.57s`.
- Generated-project smoke check: `python -m groundtruth_kb project init sample --profile dual-agent-webapp --cloud-provider azure --no-seed-example --no-include-ci` created `AGENTS.md`, `BRIDGE-INVENTORY.md`, `.claude/settings.local.json`, `infrastructure/terraform/main.tf`, and `.github/workflows/test.yml`, but `bridge/INDEX.md` was absent.
- Current scaffold implementation copies dual-agent templates but does not create `bridge/INDEX.md`: `src/groundtruth_kb/project/scaffold.py:163-221`.
- Current Terraform fallback is only provider and placeholder stubs: `src/groundtruth_kb/project/scaffold.py:479-494`.
- File bridge setup is still documented as project-owned OS scheduler work: `templates/bridge-os-poller-setup-prompt.md:29-52`, `templates/bridge-os-poller-setup-prompt.md:68-75`.
- Existing templates hardcode Codex/Claude role language: `templates/project/AGENTS.md:3-5`, `templates/project/AGENTS.md:23-29`.

## Findings

### P1 - The proposed `gt init` entry point conflicts with the shipped command architecture

The proposal makes `gt init` the one-command mass-adoption entry point, but the package has an explicit Layer 1/Layer 2 split: `gt init` is core DB initialization and `gt project init` is project scaffolding. This is documented in both architecture and CLI reference, and implemented in code.

Risk / impact:

Changing `gt init` into an interactive full scaffold can break existing users, invalidate docs, and blur the product split that prior deliberations were trying to preserve. It also makes the implementation larger than necessary, because the current scaffold engine already exists behind `gt project init`.

Required action:

Revise the proposal to choose one command-surface strategy before implementation:

1. Preferred: keep `gt init` as the core DB command and make the mass-adoption entry point `gt project init --profile ...`, with docs that teach that path; or
2. Propose an explicit backward-compatible alias/deprecation plan where `gt init` remains non-interactive by default and a new flag or mode invokes project scaffolding.

Also align `gt doctor` language with the shipped `gt project doctor` command, or propose aliases with compatibility tests.

### P1 - The current-state inventory is stale and will send Prime into duplicate or mis-scoped work

The proposal says the dev setup assumes Windows and Python 3.14, and asks whether CI should add 3.10-3.14. The target checkout already requires Python 3.11+, tests 3.11/3.12/3.13 in CI, and has a cross-platform Ubuntu/Windows/macOS CI job. The proposal also treats project scaffolding, Terraform, and GitHub CI as absent from the install path, but `gt project init --profile dual-agent-webapp --cloud-provider azure` already generates partial versions of those artifacts.

Risk / impact:

Prime could spend implementation time adding already-existing CI/platform coverage while missing the real gaps: `bridge/INDEX.md` is not created, the bridge scheduler is not implemented as a package command, Terraform is only placeholder-level, and profile output is not yet an end-to-end working 12-component project.

Required action:

Add a Phase 0 baseline table generated from commit `2a324c6` before any implementation begins. It must separate:

- already shipped and tested;
- shipped but partial/placeholder;
- documented but manual;
- absent.

Use repo evidence, not Agent Red memory, for each row. The baseline must correct the Python version and CI claims.

### P1 - Built-in auth-token management is a security-sensitive design, not a small bridge subtask

P1.4 proposes token persistence and refresh for the bridge scheduler, replacing a fragile local Claude token path. That would put CLI/provider credential handling inside a package feature before the provider model, storage location, threat model, redaction behavior, and rotation contract are defined.

Risk / impact:

Mass adoption fails badly if a scaffolding tool normalizes local OAuth/API-token capture without a clear security boundary. This also conflicts with the proposal's provider abstraction: Claude, Codex, and custom agents do not share one token model.

Required action:

Remove token persistence/refresh from the initial implementation scope unless Prime provides a separate credential-management design for review. MVP should validate external CLI auth state and report actionable fixes through doctor output. Do not persist or refresh provider tokens from GT-KB code until the owner approves the security model.

### P1 - The bridge work is not yet specified enough to replace project-owned OS pollers

The proposal calls for `gt bridge start`, a Python scheduler, background behavior on every OS, liveness state, lock behavior, and 3-minute cadence. Current GT-KB docs and templates still frame bridge automation as project-owned OS scheduler work, with setup prompts that implement scripts and schedulers per project. There is no top-level `gt bridge` command today.

Risk / impact:

If this is implemented directly, GT-KB can end up with two active bridge models: generated project-owned OS pollers and package-owned long-running scheduler commands. That ambiguity is exactly what the file bridge protocol and inventory templates are trying to avoid.

Required action:

Before coding, add a bridge scheduler architecture section that defines:

- whether `gt bridge start` replaces or wraps OS schedulers;
- foreground/background semantics on Windows, macOS, and Linux;
- lock files, logs, status schema, and liveness state paths;
- exact behavior when the agent CLI is missing or unauthenticated;
- whether scheduled runs invoke `claude`, `codex`, or only emit work items for external runners;
- migration path from existing Agent Red PS1/VBS pollers without breaking Agent Red.

Include one cross-platform generated-project smoke test for a no-work scan and one safe status-cycle test before claiming Phase 1 exit.

### P2 - The proposal is too large to GO as one implementation packet

The plan contains 21 work items across bridge runtime, init UX, agent templates, MemBase, CI templates, integrations, doctor, test scaffolding, Terraform, zero-knowledge patterns, multi-tenant patterns, API docs, and adopter docs. Its own estimate is 37.5-55.5 days. P4 explicitly includes underspecified zero-knowledge and multi-tenant architecture patterns.

Risk / impact:

A single GO would authorize a multi-month product rewrite without reviewable acceptance slices. That bypasses the bridge's purpose: independent review of concrete work before Prime implements it.

Required action:

Split this into separate bridge proposals. The first eligible implementation packet should be a small MVP adoption slice, for example:

1. command-surface decision and baseline correction;
2. generated `bridge/INDEX.md` + bridge protocol scaffold;
3. provider-parameterized AGENTS/CLAUDE/MEMORY templates;
4. generated-project smoke tests proving no Agent Red-specific paths remain.

Defer advanced Terraform, zero-knowledge, multi-tenant, and broad integration scaffolding until each has its own spec-backed proposal and acceptance tests.

### P2 - Existing generated output can look more complete than it is

The generated `dual-agent-webapp` scaffold currently reports "Bridge rules and hooks" and "infrastructure/terraform/ stubs." In the smoke check, `bridge/INDEX.md` was absent. The Terraform fallback writes only provider and placeholder files. The bridge setup prompt says the setup agent must still implement poller scripts and scheduler definitions.

Risk / impact:

Developers can mistake template presence for a functional bridge or production-grade infrastructure. That creates false readiness signals and pushes manual debugging back onto the owner or adopter.

Required action:

Add acceptance checks that validate generated behavior, not just file existence. At minimum:

- generated dual-agent projects contain `bridge/INDEX.md` and protocol rules;
- `gt project doctor` fails or warns clearly when no scheduler/poller is configured;
- generated Terraform is labeled as stubs unless it provisions the named Azure resources;
- generated docs state exactly what remains manual.

### P2 - Provider configurability needs a schema before template changes

The proposal correctly identifies current Codex/Claude hardcoding, but it does not define a provider schema or generated ownership model. Existing `AGENTS.md` template text hardcodes Codex and Claude Code role names.

Risk / impact:

Naive string replacement can produce inconsistent instructions, broken bridge prompts, or provider claims that the generated project cannot execute. This is especially risky because agent instructions become operational control surfaces.

Required action:

Define a small provider schema before P2 implementation:

- provider id;
- CLI command;
- model/runtime label;
- required config files;
- auth-check command;
- invocation prompt source;
- bridge role capabilities.

Then generate AGENTS/CLAUDE/bridge inventory from that schema and add tests for Codex, Claude-only, and custom-provider outputs.

## Answers To Prime's Open Decisions

1. Phase ordering: interleave documentation with P1. Write the Getting Started / first scaffold walkthrough as an executable acceptance contract while building P1, not after P4.
2. Bridge scheduler technology: do not choose in this proposal yet. For an MVP package scheduler, prefer stdlib `asyncio` or a very small explicit loop over `apscheduler`; avoid a third-party scheduler until persistence and job-store requirements are proven.
3. Template engine: do not add Jinja2 to the base dependency set without a dependency decision. If complex workflow templates truly need it, make the dependency explicit and test wheel/install impact. Otherwise start with simple structured templates.
4. Minimum Python version: keep `>=3.11` unless the owner explicitly wants 3.10 support. The checkout already tests 3.11-3.13 and cross-OS 3.12; add 3.14 when CI support is available, but do not claim the repo is currently 3.14-only.
5. MVP scope: ship P1/P2 as a developer preview only after the corrected baseline, command-surface decision, and generated-project smoke tests pass. Do not wait for all five phases, but do not label P1/P2 as mass adoption.

## Required Conditions For GO

1. Replace the stale current-state table with a verified baseline against `groundtruth-kb@2a324c6`.
2. Resolve the `gt init` vs `gt project init` command-surface decision with backward-compatibility and docs/test impacts.
3. Remove auth-token persistence/refresh from MVP or submit a separate credential-management design for review.
4. Define the package bridge scheduler architecture and migration path before implementing `gt bridge start`.
5. Split this roadmap into smaller bridge proposals with specific acceptance tests.
6. Add generated-project smoke tests for the chosen MVP path on Windows, macOS, and Linux, including `bridge/INDEX.md`, agent templates, doctor output, and absence of Agent Red-specific paths.
7. Reframe success criteria from "mass adoption" to "developer preview" until a second non-Agent-Red project completes the intended flow.

## Decision Needed From Owner

Owner decision is needed on the command-surface posture:

- preserve `gt init` as the core DB command and promote `gt project init` as the mass-adoption entry point; or
- explicitly expand `gt init` into a scaffold command with a backward-compatible migration plan.

Owner decision is also needed before GT-KB stores or refreshes any provider auth tokens.
