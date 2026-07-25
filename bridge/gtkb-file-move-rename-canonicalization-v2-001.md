NEW
::init gtkb lo
::open build

author_identity: prime-builder/goose
author_harness_id: G
author_session_context_id: G-2026-07-21T08-15-00Z
author_model: deepseek-v4-pro
author_model_version: deepseek-v4-pro
author_model_configuration: Goose Desktop interactive Prime Builder; owner-declared role via ::init gtkb pb; sandbox=danger-full-access
author_metadata_source: explicit current-session bridge filing metadata

# Implementation Proposal - Canonical control-surface relocation and gtkb prefix rollout (v2)

bridge_kind: prime_proposal
Document: gtkb-file-move-rename-canonicalization-v2
Version: 001
Date: 2026-07-22 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

target_paths: ["gtkb-file-move-and-rename-list.csv", ".claude/hooks", ".claude/rules", ".claude/settings.json", ".claude/skills/gtkb-bridge/SKILL.md", ".claude/skills/gtkb-send-review/SKILL.md", ".codex/hooks.json", ".codex/gtkb-hooks", ".codex/skills/gtkb-bridge/SKILL.md", ".codex/skills/gtkb-send-review/SKILL.md", "config/hooks", "config/agent-control", "groundtruth-kb/src", "groundtruth-kb/tests", "groundtruth-kb/docs", "groundtruth-kb/templates", "platform_tests", "tests", "scripts", "dashboard", "docs", "bridge", "memory", ".github", "pyproject.toml", "groundtruth.toml"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## First-Line Role Eligibility Check

PASS. The active session envelope resolves to `role_resolved = prime-builder`, `harness_id = G`, `harness_name = goose`. `NEW` is a Prime Builder bridge status under `GOV-FILE-BRIDGE-AUTHORITY-001`. No prior bridge file exists for this thread.

## Summary

This proposal supersedes the broken bridge chain `gtkb-file-move-rename-canonicalization` v001-v007, which has an invalid transition (NEW→REVISED at v001→v002) that prevents the lifecycle resolver from issuing an implementation-start authorization packet. The scope, CSV manifest, compatibility strategy, verification plan, and GO conditions are identical to the v006 proposal and v007 GO verdict in the original chain. The original chain is preserved as provenance per the Never-Delete Rule (C-013).

This proposal also corrects bridge metadata defects discovered during implementation-start authorization: v001's `author_identity` was `codex` (unprefixed), and v002-v004 were missing `Responds to:` metadata. Those corrections are preserved in the original chain files.

## Supersession Of Broken Chain

The original chain `gtkb-file-move-rename-canonicalization` v001-v007 is preserved as historical provenance. It cannot be used for implementation-start authorization because `bridge_lifecycle_resolver._validate_ordinary_transitions` rejects the NEW→REVISED transition at v001→v002. This fresh thread starts a clean lifecycle with correct transitions.

The v007 GO verdict in the original chain performed a thorough review (all five blocking findings from v005 NO-GO closed, all four non-blocking observations resolved, CSV manifest verified at 90 rows with correct category counts). That review substance is carried forward by reference; this fresh proposal does not re-litigate the same scope.

## Requirement Sufficiency

Existing requirements remain sufficient for WI-5640. Same as v006 original: no new specifications are needed.

## In-Root Placement Evidence

All declared targets are inside `E:\GT-KB`. No target path escapes the project root.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - governing work-item specification for cross-harness skill/control-surface parity.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - keeps the proposal, verdict, implementation report, and verification evidence artifact-oriented.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - protects owner-question and approval surfaces during control-surface moves.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps all work inside GT-KB platform scope and out of adopter applications.
- `GOV-STANDING-BACKLOG-001` - preserves future-work capture rather than silent scope absorption.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - requires Codex hook parity/fallback surfaces to keep resolving after hook relocation.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires durable evidence for decisions, risks, plans, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - governs artifact lifecycle transitions and derived work.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - requires cross-harness enforcement surfaces to remain functional.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - requires Claude/Codex parity after path canonicalization.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires modernization to preserve or improve existing behavior.

## Prior Deliberations

- `DELIB-202667106` - Loyal Opposition Review: Canonical Skill Renaming Rollout (gtkb- prefix)
- `DELIB-20260966` - Loyal Opposition Review - gtkb-sweep-commit Skill Parity Registration
- `DELIB-20261165` - Loyal Opposition Review - gtkb-sweep-commit Skill Parity Registration
- `DELIB-202666362` - GT-KB WI-5142 Bounded Registry Readiness Repair - Corrected Loyal Opposition Verdict
- `DELIB-202665597` - Loyal Opposition Review - WI-4840 Advisory Disposition Skill Scaffold
- `bridge/gtkb-file-move-rename-canonicalization-005.md` - Loyal Opposition NO-GO verdict (original chain, provenance)
- `bridge/gtkb-file-move-rename-canonicalization-006.md` - Prime Builder REVISED proposal (original chain, provenance; scope carried forward)
- `bridge/gtkb-file-move-rename-canonicalization-007.md` - Loyal Opposition GO verdict (original chain, provenance; review substance carried forward)

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5640`.
- Owner approved the inferred filename corrections for `spec-before-code.py` and `skill-scenarios.toml` in the original Codex session before proposal filing.
- Owner selected option A (file fresh NEW proposal in new bridge thread) to resolve the broken chain transition defect.

## Cleaned Manifest Evidence

`gtkb-file-move-and-rename-list.csv` has been verified:

- Row count: 90
- Source categories: `.claude/hooks` = 33, `.claude/rules` = 38, `config/agent-control` = 19
- Missing normalized sources: 0
- Untracked/runtime/generated sources: 0
- Existing destination collisions: 0
- `.claude/skills` source rows: 0
- Typo rows (`conytol`): 0
- Runtime/log/cache/README rows: 0

## Proposed Scope

1. Parse `E:\GT-KB\gtkb-file-move-and-rename-list.csv` using a structured CSV parser. Normalize absolute `E:\GT-KB\...` home directories to repository-relative paths, trim filename whitespace, and fail closed on missing source, untracked source, directory source, or destination collision.
2. Create `config/hooks/` and move/rename only the 33 tracked hook script rows from `.claude/hooks/` to `config/hooks/gtkb-*`. Do not move generated state/log/cache files.
3. Update `.claude/settings.json`, `.codex/hooks.json`, `.codex/gtkb-hooks`, hook launch wrappers, generated registry copies, and tests so hook command resolution uses the canonical `config/hooks/gtkb-*` scripts.
4. For the 38 `.claude/rules/` rows, create canonical `config/agent-control/gtkb-*` copies and preserve `.claude/rules/<original-name>` as a native Claude Code compatibility surface (content mirrors, not pointer stubs).
5. Rename the 19 cleaned `config/agent-control` rows in place to `gtkb-*`, with reference repair for startup overlays, command-surface registries, system-interface maps, docs, tests, generated registry copies, and prompt/startup surfaces.
6. Repair stale live references to the retired `.claude/skills/bridge-propose` path. The authorized `.claude/skills` mutations are limited to `.claude/skills/gtkb-bridge/SKILL.md` and `.claude/skills/gtkb-send-review/SKILL.md`; the authorized `.codex/skills` mutations are limited to `.codex/skills/gtkb-bridge/SKILL.md` and `.codex/skills/gtkb-send-review/SKILL.md`.
7. Treat archive/provenance/history references separately from live dependencies.
8. Stop and file a revised proposal if implementation requires mutating a path outside `target_paths`, moving a skill file, absorbing WI-5584 work, deleting compatibility mirrors, or rewriting history/provenance content.

## Compatibility Strategy For `.claude/rules/`

The `.claude/rules/` directory is a native Claude Code rule-discovery surface. This proposal does not permit a hard delete of the old rule paths.

- Every CSV rule mapping must produce `config/agent-control/gtkb-<name>` as the canonical control artifact.
- Every old `.claude/rules/<name>` path must remain readable after implementation as a compatibility mirror (content mirror, not pointer stub).
- Compatibility mirrors must preserve the operational rule text available to Claude Code.
- A follow-up bridge proposal may later retire the compatibility mirrors after all harness startups resolve canonical config paths.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` | Run cross-harness reference scans and parity tests: `python -m pytest platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_generate_codex_skill_adapters.py -q --tb=short` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm implementation started only after GO and worker claim; cite `scripts/bridge_claim_cli.py status gtkb-file-move-rename-canonicalization-v2` and claim evidence. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Preserve this bridge chain, file a formal implementation report, and classify any derived future work. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-file-move-rename-canonicalization-v2` after filing and after implementation report. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map each spec to concrete commands, scan outputs, and compatibility evidence before LO can VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-file-move-rename-canonicalization-v2` and confirm no blocking gaps. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run startup/owner-action tests: `platform_tests/scripts/test_canonical_init_keyword_syntax.py` and related startup/control tests if touched. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify every touched file remains under `E:\GT-KB` and no `applications/Agent_Red/` file is mutated. |
| `GOV-STANDING-BACKLOG-001` | Confirm WI-5584 remains separate; no cross-project scope is silently absorbed. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run Codex hook parity/resolution tests: `platform_tests/scripts/test_codex_hook_parity.py` and `platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py` where applicable. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Implementation report must include durable manifest, reference, compatibility, and verification evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Do not mark implementation verified until LO reviews the implementation report and bridge status advances correctly. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Run repo-native tests that exercise hook resolution, skill loading, startup-control loading, bridge proposal filing, and implementation authorization after relocation. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Verify Claude/Codex-facing control surfaces agree on canonical `config/hooks`, `config/agent-control`, and `gtkb-bridge-propose` paths. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run targeted regression: `python -m pytest platform_tests groundtruth-kb/tests -q --tb=short`, or a documented narrower suite if full runtime is prohibitive. |

## Acceptance Criteria

- Cleaned CSV manifest remains at 90 rows with 0 missing sources, 0 untracked sources, 0 destination collisions, and category counts 33 hook scripts, 38 rule files, 19 agent-control files.
- Every hook script move has a destination under `config/hooks/gtkb-*`, updated command references, and passing hook parity tests.
- Every rule mapping has a canonical `config/agent-control/gtkb-*` destination and a readable `.claude/rules/<old>` compatibility mirror.
- Every cleaned `config/agent-control` rename has load-bearing references updated or documented as historical/provenance-only.
- `.claude/skills/bridge-propose` live references are repaired to the canonical `gtkb-bridge-propose` path.
- Repository-wide scans find no remaining live references to retired paths except documented compatibility and historical exceptions.
- Session startup, bridge proposal/review, hook command resolution, skill loading, implementation-start authorization, and cross-harness parity tests pass after relocation.
- Implementation report includes exact commands, manifest evidence, move inventory, compatibility mirror inventory, reference exception table, test evidence, and worker-quality observations.

## Risks / Rollback

Risk is high because the slice touches startup, hooks, rules, tests, templates, generated registries, and harness parity surfaces. Principal risks: broken Claude Code rule discovery, hook command drift, stale generated registry copies, overbroad reference rewriting of historical records.

Rollback is a controlled revert of the approved source/test/config changes only. Bridge files, verdicts, implementation reports, and verification artifacts are append-only audit records and must not be deleted.

## Files Expected To Change

- `gtkb-file-move-and-rename-list.csv`
- `.claude/hooks`
- `.claude/rules`
- `.claude/settings.json`
- `.claude/skills/gtkb-bridge/SKILL.md`
- `.claude/skills/gtkb-send-review/SKILL.md`
- `.codex/hooks.json`
- `.codex/gtkb-hooks`
- `.codex/skills/gtkb-bridge/SKILL.md`
- `.codex/skills/gtkb-send-review/SKILL.md`
- `config/hooks`
- `config/agent-control`
- `groundtruth-kb/src`
- `groundtruth-kb/tests`
- `groundtruth-kb/docs`
- `groundtruth-kb/templates`
- `platform_tests`
- `tests`
- `scripts`
- `dashboard`
- `docs`
- `bridge`
- `memory`
- `.github`
- `pyproject.toml`
- `groundtruth.toml`

## Recommended Commit Type

`feat`
