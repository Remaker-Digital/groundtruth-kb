REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-22T00-52-24Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder; cwd=E:\GT-KB; sandbox=danger-full-access; approval_policy=never; task=CSV move/rename program oversight and proposal revision
author_metadata_source: explicit-codex-session

# Implementation Proposal - Canonical control-surface relocation and gtkb prefix rollout

bridge_kind: prime_proposal
Document: gtkb-file-move-rename-canonicalization
Version: 006
Responds to: bridge/gtkb-file-move-rename-canonicalization-005.md
Date: 2026-07-22 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

target_paths: ["gtkb-file-move-and-rename-list.csv", ".claude/hooks", ".claude/rules", ".claude/settings.json", ".claude/skills/gtkb-bridge/SKILL.md", ".claude/skills/gtkb-send-review/SKILL.md", ".codex/hooks.json", ".codex/gtkb-hooks", ".codex/skills/gtkb-bridge/SKILL.md", ".codex/skills/gtkb-send-review/SKILL.md", "config/hooks", "config/agent-control", "groundtruth-kb/src", "groundtruth-kb/tests", "groundtruth-kb/docs", "groundtruth-kb/templates", "platform_tests", "tests", "scripts", "dashboard", "docs", "bridge", "memory", ".github", "pyproject.toml", "groundtruth.toml"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## First-Line Role Eligibility Check

PASS. The active session envelope resolves to `role_resolved = prime-builder`, `harness_id = A`, `harness_name = codex`, and `session_id = A-2026-07-22T00-52-24Z`. `REVISED` is a Prime Builder bridge status under `GOV-FILE-BRIDGE-AUTHORITY-001`. The live bridge head before this filing is the Loyal Opposition `NO-GO` verdict at `bridge/gtkb-file-move-rename-canonicalization-005.md`, so a Prime Builder revision is role-eligible.

## Summary

Revision 006 responds to the Loyal Opposition `NO-GO` in version 005. It narrows and clarifies the proposal by cleaning the CSV manifest, removing WI-5584 absorption, separating physical file moves from reference repairs, and adding a compatibility strategy for `.claude/rules/` so Claude Code startup keeps a native rule surface after canonical copies are created under `config/agent-control/`.

This proposal still selects GPT 5.2 as the implementation worker model with the lowest expected error probability among the available options for governed bulk refactor work. Workers must claim only after GO, use the cleaned manifest, produce manifest/reference/test evidence, and stop rather than improvise when reference repair escapes the target set.

## Requirement Sufficiency

Existing requirements remain sufficient for WI-5640 after scope cleanup. The proposal no longer absorbs WI-5584 or any work from `PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE`; any future WI-5584 work must be authorized separately or by explicit owner decision.

## In-Root Placement Evidence

All declared targets are inside `E:\GT-KB`. No target path escapes the project root. The cleaned CSV file is itself in the project root and is in scope as the owner-provided implementation manifest.

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
- `bridge/gtkb-file-move-rename-canonicalization-005.md` - Loyal Opposition NO-GO verdict that this revision addresses

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5640`.
- Owner approved the inferred filename corrections for `spec-before-code.py` and `skill-scenarios.toml` in this Codex session before proposal filing.
- No owner decision authorizing WI-5584 absorption is cited; therefore WI-5584 absorption is removed from this proposal.

## Cleaned Manifest Evidence

`gtkb-file-move-and-rename-list.csv` has been corrected before this revision:

- Row count is now 90, down from 104.
- Remaining sources: 33 tracked `.claude/hooks` Python hook scripts, 38 tracked `.claude/rules` files, and 19 tracked `config/agent-control` files.
- Missing normalized sources: 0.
- Untracked/runtime/generated sources: 0.
- Existing destination collisions: 0.
- `.claude/skills` source rows: 0 by design; skill files are not physical move entries in this CSV.
- Corrected `CONTROL-MAP.md` destination: `gtkb-control-map.md`.
- Corrected hook source typo: `spec-before-code.py`.
- Corrected agent-control source typo: `skill-scenarios.toml`.
- Removed generated/runtime rows: `__pycache__`, bridge/codex log rows, `last-session-start.*`, `last-user-visible-startup*.md`, `last-user-visible-startup*.meta.json`, `scanner-safe-writer.log`, and `session-lifecycle-guard.json`.
- Removed no-op row: `config/agent-control/README.md` to `config/agent-control/README.md`.

## NO-GO Closure Matrix

| Finding | Revision 006 disposition |
| --- | --- |
| F1 CSV typo `gtkb-conytol-map.md` | Corrected in the CSV to `gtkb-control-map.md`; manifest check shows no missing source and no destination collision. |
| F2 `.claude/skills` manifest gap | Physical moves are limited to CSV rows. Skill-file work is narrowed to explicit reference repair in `.claude/skills/gtkb-bridge/SKILL.md` and `.claude/skills/gtkb-send-review/SKILL.md`; no `.claude/skills` file move is authorized by this proposal. |
| F3 `.claude/rules` compatibility | Added a mandatory compatibility mirror strategy: canonical copies are created under `config/agent-control/gtkb-*`, while `.claude/rules/<original-name>` remains as a native Claude Code compatibility surface for at least one migration window. |
| F4 runtime state/log/err rows | Removed all untracked/generated hook runtime rows from the CSV, including the runtime Markdown startup cache rows that were not tracked source. |
| F5 WI-5584 absorption | Removed absorption claim. WI-5584 remains separate unless the owner provides explicit future authorization. |
| O1 `__pycache__` row | Removed. |
| O2 `README.md` no-op | Removed. |
| O3 `gtbk` typo | Remains corrected as of v004. |
| O4 generic verification | Replaced with concrete manifest, compatibility, reference-scan, parity, and regression verification below. |

## Proposed Scope

1. Parse `E:\GT-KB\gtkb-file-move-and-rename-list.csv` using a structured CSV parser. Normalize absolute `E:\GT-KB\...` home directories to repository-relative paths, trim filename whitespace, and fail closed on missing source, untracked source, directory source, or destination collision.
2. Create `config/hooks/` and move/rename only the 33 tracked hook script rows from `.claude/hooks/` to `config/hooks/gtkb-*`. Do not move generated state/log/cache files.
3. Update `.claude/settings.json`, `.codex/hooks.json`, `.codex/gtkb-hooks`, hook launch wrappers, generated registry copies, and tests so hook command resolution uses the canonical `config/hooks/gtkb-*` scripts.
4. For the 38 `.claude/rules/` rows, create canonical `config/agent-control/gtkb-*` copies and preserve `.claude/rules/<original-name>` as compatibility mirrors or symlink-equivalent shims. Because Windows symlink availability is not guaranteed, the default implementation must use content mirrors unless the worker proves symlink support and tests it. The compatibility surface is allowed to remain at old paths and must be documented in the implementation report.
5. Rename the 19 cleaned `config/agent-control` rows in place to `gtkb-*`, with reference repair for startup overlays, command-surface registries, system-interface maps, docs, tests, generated registry copies, and prompt/startup surfaces.
6. Repair stale live references to the retired `.claude/skills/bridge-propose` path. The authorized `.claude/skills` mutations are limited to `.claude/skills/gtkb-bridge/SKILL.md` and `.claude/skills/gtkb-send-review/SKILL.md`; the authorized `.codex/skills` mutations are limited to `.codex/skills/gtkb-bridge/SKILL.md` and `.codex/skills/gtkb-send-review/SKILL.md` unless a worker files a revised proposal.
7. Treat archive/provenance/history references separately from live dependencies. Historical mentions in `bridge/`, `memory/`, reports, release notes, evidence fixtures, and old worktrees may remain only when classified and documented.
8. Stop and file a revised proposal if implementation requires mutating a path outside `target_paths`, moving a skill file, absorbing WI-5584 work, deleting compatibility mirrors, or rewriting history/provenance content as if it were live configuration.

## Compatibility Strategy For `.claude/rules/`

The `.claude/rules/` directory is a native Claude Code rule-discovery surface. This proposal therefore does not permit a hard delete of the old rule paths in the implementation slice.

Required behavior:

- Every CSV rule mapping must produce `config/agent-control/gtkb-<name>` as the canonical control artifact.
- Every old `.claude/rules/<name>` path must remain readable after implementation as a compatibility mirror or tested symlink-equivalent shim.
- Compatibility mirrors must preserve the operational rule text available to Claude Code. One-line pointer stubs are not sufficient unless a test proves the startup loader follows them and loads the canonical target content.
- The implementation report must list every rule compatibility mirror and its canonical target.
- The reference scan may classify `.claude/rules/<name>` compatibility mirrors as intentional live compatibility exceptions. Other live references to `.claude/rules/` must be repaired to the canonical `config/agent-control/gtkb-*` path or documented as historical/provenance-only.
- A follow-up bridge proposal may later retire the compatibility mirrors after Claude Code startup, Codex startup, and dispatcher startup all resolve canonical config paths without depending on `.claude/rules/`.

## Cross-Harness Disposition

- GPT 5.2 remains the selected worker model for implementation after GO.
- GPT 5.2 workers must claim the GO verdict before implementation, run manifest verification before mutation, and file an implementation report with exact scan and test evidence.
- Prime Builder oversight will spot-check manifest normalization, reference classification, and compatibility-mirror quality to evaluate GPT 5.2 performance on governed bulk refactors.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5640; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE; revised after bridge/gtkb-file-move-rename-canonicalization-005.md NO-GO",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and governed bridge proposal review",
  "primary_route": "gtkb-bridge-propose helper via propose_bridge_codex_non_bypass",
  "before_behavior": "Legacy hook scripts, rule files, and agent-control files use mixed locations and non-gtkb-prefixed names; stale bridge-propose references point to retired skill paths.",
  "after_behavior": "Tracked source artifacts have canonical gtkb-prefixed destinations; hook/runtime references resolve to config/hooks; agent-control references resolve to config/agent-control; Claude Code retains .claude/rules compatibility mirrors during the migration window.",
  "self_descriptive_naming": "The cleaned manifest, target paths, scope, and compatibility section name the proposed effect and the allowed old-path exceptions.",
  "obsolete_guidance_disposition": "WI-5584 absorption is removed; obsolete or historical references are classified instead of blindly rewritten.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback does not delete bridge or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5640",
    "project": "PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY",
    "manifest": "gtkb-file-move-and-rename-list.csv",
    "manifest_row_count": 90,
    "manifest_source_categories": {
      ".claude/hooks": 33,
      ".claude/rules": 38,
      "config/agent-control": 19,
      ".claude/skills": 0
    },
    "target_paths": [
      "gtkb-file-move-and-rename-list.csv",
      ".claude/hooks",
      ".claude/rules",
      ".claude/settings.json",
      ".claude/skills/gtkb-bridge/SKILL.md",
      ".claude/skills/gtkb-send-review/SKILL.md",
      ".codex/hooks.json",
      ".codex/gtkb-hooks",
      ".codex/skills/gtkb-bridge/SKILL.md",
      ".codex/skills/gtkb-send-review/SKILL.md",
      "config/hooks",
      "config/agent-control",
      "groundtruth-kb/src",
      "groundtruth-kb/tests",
      "groundtruth-kb/docs",
      "groundtruth-kb/templates",
      "platform_tests",
      "tests",
      "scripts",
      "dashboard",
      "docs",
      "bridge",
      "memory",
      ".github",
      "pyproject.toml",
      "groundtruth.toml"
    ],
    "linked_specifications": [
      "ADR-CROSS-HARNESS-PARITY-001",
      "GOV-FILE-BRIDGE-AUTHORITY-001",
      "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
      "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
      "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
      "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
      "SPEC-AUQ-POLICY-ENGINE-001",
      "ADR-ISOLATION-APPLICATION-PLACEMENT-001",
      "GOV-STANDING-BACKLOG-001",
      "ADR-CODEX-HOOK-PARITY-FALLBACK-001",
      "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
      "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
      "DCL-CROSS-HARNESS-ENFORCEMENT-001",
      "DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001",
      "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001"
    ]
  },
  "expected_result": {
    "summary": "CSV-driven canonical relocation and gtkb-prefix rename of tracked hook, rule, and agent-control artifacts, with explicit .claude/rules compatibility mirrors and repository-wide live reference repair.",
    "scope": [
      "Move or copy only cleaned tracked CSV rows after manifest preflight.",
      "Exclude runtime state/log/cache files from source moves.",
      "Preserve .claude/rules as a compatibility mirror surface while config/agent-control becomes the canonical control-artifact location.",
      "Repair retired .claude/skills/bridge-propose references without moving skill files.",
      "Classify historical references instead of rewriting provenance content."
    ],
    "acceptance_criteria": [
      "Cleaned manifest has 90 rows, 0 missing sources, 0 untracked sources, and 0 destination collisions.",
      "Hook commands resolve to config/hooks/gtkb-* scripts.",
      "Rule canonical copies exist under config/agent-control/gtkb-* and compatibility mirrors remain readable under .claude/rules/.",
      "Live retired-path references are repaired or explicitly classified as compatibility/historical exceptions.",
      "Startup, bridge, hook, skill, implementation-start, and parity tests pass."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source, test, config, hook, and manifest changes under separate authority; preserve bridge files, verdicts, reports, and verification records.",
    "verification": "Rerun manifest preflight, bridge preflights, startup/hook parity tests, and reference scans after rollback."
  },
  "hard_invariants": [
    "No implementation starts before a GO verdict and worker claim.",
    "Only cleaned CSV rows are physical move entries.",
    "Runtime state/log/cache rows are not source-move entries.",
    "Claude Code .claude/rules compatibility remains in place unless a later GO retires it."
  ],
  "fail_closed_conditions": [
    "Manifest row count differs from 90 without a revised proposal.",
    "Any manifest source is missing, untracked, a directory, or collides with an unrelated destination.",
    "A worker needs to mutate a path outside target_paths.",
    "A worker needs to move a skill file rather than repair explicit references.",
    "A worker needs to delete .claude/rules compatibility mirrors.",
    "A worker needs to absorb WI-5584 or another work item without owner-decision evidence."
  ],
  "essential_context_preservation": "The revision preserves PAUTH, project, work item, target paths, linked specifications, prior deliberations, owner decisions, cleaned manifest evidence, NO-GO closure, scope, compatibility strategy, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Implementation Runbook For GPT 5.2 Workers

1. Claim the GO verdict through the governed bridge claim path and record the claim evidence in the implementation report.
2. Run the manifest preflight before mutation. Required output: row count 90, missing sources 0, untracked sources 0, destination collisions 0, category counts 33/38/19.
3. Snapshot live reference counts for `.claude/hooks/`, `.claude/rules/`, `.claude/skills/bridge-propose`, and pre-prefix `config/agent-control` filenames, excluding `.claude/worktrees/`, evidence fixtures, and historical bridge/report/memory content where appropriate.
4. Move/rename hook scripts to `config/hooks/gtkb-*`; update hook command surfaces and tests in the same slice.
5. Copy/rename rule files to `config/agent-control/gtkb-*`; preserve `.claude/rules/<old>` compatibility mirrors and test their readability.
6. Rename cleaned `config/agent-control` files in place; update startup/control references.
7. Repair exact stale skill references in the authorized skill adapter files; do not move skill files.
8. Run targeted tests and reference scans. If any old-path live reference remains outside compatibility mirrors, fix it or document why it is historical-only.
9. File an implementation report with manifest diff, moved-file inventory, compatibility mirror inventory, reference-scan exception table, exact commands, test results, and any GPT 5.2 worker-quality observations.

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` | Run cross-harness reference scans and parity tests covering `.claude`, `.codex`, generated registries, skills, tests, scripts, docs, and config surfaces. Include `python -m pytest platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_generate_codex_skill_adapters.py -q --tb=short` or an implementation-equivalent narrower target with justification. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm implementation started only after GO and worker claim; implementation report must cite `gt bridge show gtkb-file-move-rename-canonicalization --json` and claim status evidence. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Preserve this bridge chain, file a formal implementation report, and classify any derived future work instead of absorbing unrelated WI scope. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Rerun `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-file-move-rename-canonicalization` after filing and after implementation report filing. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report must map each spec to concrete commands, scan outputs, and compatibility evidence before LO can VERIFIED. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-file-move-rename-canonicalization` and confirm no blocking gaps. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run startup/owner-action tests that cover owner-question visibility and session startup surfaces after agent-control path repair. Include `platform_tests/scripts/test_canonical_init_keyword_syntax.py` and related startup/control tests if touched. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Verify every touched file remains under `E:\GT-KB` and no `applications/Agent_Red/` file is mutated by this slice. |
| `GOV-STANDING-BACKLOG-001` | Confirm WI-5584 remains separate or is filed as future work; no cross-project scope is silently absorbed. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run Codex hook parity/resolution tests, including `platform_tests/scripts/test_codex_hook_parity.py` and `platform_tests/scripts/test_check_codex_hook_parity_resolution_table.py` where applicable. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Implementation report must include durable manifest, reference, compatibility, and verification evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Do not mark implementation verified until LO reviews the implementation report and bridge status advances correctly. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Run repo-native tests that exercise hook resolution, skill loading, startup-control loading, bridge proposal filing, and implementation authorization after relocation. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Verify Claude/Codex-facing control surfaces agree on canonical `config/hooks`, `config/agent-control`, and `gtkb-bridge-propose` paths. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run targeted regression plus broad regression as feasible: `python -m pytest platform_tests groundtruth-kb/tests -q --tb=short`, or a documented narrower suite if full runtime is prohibitive. |

## Acceptance Criteria

- Cleaned CSV manifest remains at 90 rows with 0 missing sources, 0 untracked sources, 0 destination collisions, and category counts 33 hook scripts, 38 rule files, 19 agent-control files.
- Every hook script move has a destination under `config/hooks/gtkb-*`, updated command references, and passing hook parity tests.
- Every rule mapping has a canonical `config/agent-control/gtkb-*` destination and a readable `.claude/rules/<old>` compatibility mirror or tested symlink-equivalent shim.
- Every cleaned `config/agent-control` rename has load-bearing references updated or documented as historical/provenance-only.
- `.claude/skills/bridge-propose` live references are repaired to the canonical `gtkb-bridge-propose` path in the explicit skill adapter files and related source/test/template surfaces.
- Repository-wide scans find no remaining live references to retired hook paths, retired pre-prefix config names, or retired skill paths except documented compatibility and historical exceptions.
- Session startup, bridge proposal/review, hook command resolution, skill loading, implementation-start authorization, and cross-harness parity tests pass after relocation.
- Implementation report includes exact commands, manifest evidence, move inventory, compatibility mirror inventory, reference exception table, test evidence, and GPT 5.2 worker-quality observations.

## Risks / Rollback

Risk is high enough to require worker discipline because the slice touches startup, hooks, rules, tests, templates, generated registries, and harness parity surfaces. The principal risks are broken Claude Code rule discovery, hook command drift, stale generated registry copies, and overbroad reference rewriting of historical records.

Rollback is a controlled revert of the approved source/test/config changes only. Bridge files, verdicts, implementation reports, and verification artifacts are append-only audit records and must not be deleted by rollback. If rollback is needed after rule relocation, restore canonical content at both `config/agent-control/gtkb-*` and `.claude/rules/<old>` until a follow-up bridge proposal chooses one authority path.

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
