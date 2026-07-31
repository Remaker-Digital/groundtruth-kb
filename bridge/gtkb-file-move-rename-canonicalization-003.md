REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: A-2026-07-22T00-52-24Z
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex desktop interactive Prime Builder; cwd=E:\GT-KB; sandbox=danger-full-access; approval_policy=never; task=CSV move/rename program oversight
author_metadata_source: explicit-codex-session

# Implementation Proposal - Canonical skill renaming rollout (gtkb- prefix)

bridge_kind: prime_proposal
Document: gtkb-file-move-rename-canonicalization
Version: 003
Responds to: bridge/gtkb-file-move-rename-canonicalization-002.md
Date: 2026-07-22 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project Authorization Candidates: [{"project_authorization_id":"PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE","coverage":"project_membership_fallback","included_work_item_count":null,"specificity_rank":[2,0],"selected":true}]
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

target_paths: [".claude/hooks", ".claude/rules", ".claude/skills", ".claude/settings.json", ".codex/hooks.json", ".codex/skills", ".codex/gtkb-hooks", "config/hooks", "config/agent-control", "groundtruth-kb/src", "groundtruth-kb/tests", "groundtruth-kb/docs", "groundtruth-kb/templates", "platform_tests", "tests", "scripts", "dashboard", "docs", "bridge", "memory", ".github", "pyproject.toml", "groundtruth.toml"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Summary

Revision notes:
- Version 002 corrected author_identity metadata from the underspecified `codex` value in version 001 to `prime-builder/codex`.
- Version 003 adds `.claude/skills` to authorized target paths and explicitly includes stale bridge-propose skill references in scope after oversight spot-checks found live references under `.claude/skills`.

CSV-driven canonical relocation and gtkb-prefix rename of legacy .claude hook, rule, skill, and agent-control artifacts, with repository-wide load-bearing reference repair and verification.

Work item description: Roll out renamed canonical skills (gtkb- prefix) across GT-KB: canonical .claude/skills, harness projections, capability registry, managed-artifact templates, doctor/upgrade coupling, and rules/docs. Absorbs WI-5584 config-canonicalization scope. Bridge: gtkb-skill-rename-rollout.

## Claim

Prime Builder proposes a bounded implementation slice for `WI-5640` and keeps the bridge, project authorization, owner-decision, and verification gates intact.

## Requirement Sufficiency

Existing requirements are sufficient for filing this proposal. The work item and active project authorization define the implementation boundary; any missing membership or PAUTH state is created only when explicit owner-decision evidence is supplied.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `.claude/hooks`, `.claude/rules`, `.claude/skills`, `.claude/settings.json`, `.codex/hooks.json`, `.codex/skills`, `.codex/gtkb-hooks`, `config/hooks`, `config/agent-control`, `groundtruth-kb/src`, `groundtruth-kb/tests`, `groundtruth-kb/docs`, `groundtruth-kb/templates`, `platform_tests`, `tests`, `scripts`, `dashboard`, `docs`, `bridge`, `memory`, `.github`, `pyproject.toml`, `groundtruth.toml`.

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` - auto-linked governing or work-item specification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - preserves role-correct bridge authority and numbered-file filing.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - auto-linked governing or work-item specification.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete specification links in implementation proposals.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires spec-derived verification evidence before VERIFIED.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires project authorization, project, work item, and target path metadata.
- `SPEC-AUQ-POLICY-ENGINE-001` - auto-linked governing or work-item specification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps this platform command out of adopter application scope.
- `GOV-STANDING-BACKLOG-001` - auto-linked governing or work-item specification.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - auto-linked governing or work-item specification.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - auto-linked governing or work-item specification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - auto-linked governing or work-item specification.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - auto-linked governing or work-item specification.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - auto-linked governing or work-item specification.

## Prior Deliberations

- `DELIB-202667106` - Loyal Opposition Review: Canonical Skill Renaming Rollout (gtkb- prefix)
- `DELIB-20260966` - Loyal Opposition Review - gtkb-sweep-commit Skill Parity Registration
- `DELIB-20261165` - Loyal Opposition Review - gtkb-sweep-commit Skill Parity Registration
- `DELIB-202666362` - GT-KB WI-5142 Bounded Registry Readiness Repair — Corrected Loyal Opposition Verdict (terminal-conflicting and dependency-blocked GO)
- `DELIB-202665597` - Loyal Opposition Review — WI-4840 Advisory Disposition Skill Scaffold

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE` - active project authorization covering `WI-5640`.

## Proposed Scope

- Parse E:\GT-KB\gtkb-file-move-and-rename-list.csv into a normalized manifest before mutation, applying the owner-approved inferred corrections for hidden dot-log/json filenames, spec-before-code.py, and skill-scenarios.toml.
- Move and rename each manifest source to its canonical destination, preserving file contents, executable behavior, bridge proposal filing, and session startup semantics; create config/hooks as needed.
- Update load-bearing references across the authorized repository surfaces so hooks, rules, skills, startup envelopes, templates, tests, generated registry copies, dashboard/docs references, and CI/runtime commands resolve to the new canonical paths.
- Repair stale bridge-propose helper references that still point to the retired .claude/skills/bridge-propose path, including canonical .claude skills, Codex skill adapters, tests, templates, and source loaders.
- Treat historical/archive citations separately from live dependencies: record intentionally historical references in the implementation report instead of blindly rewriting provenance text.
- If a load-bearing reference requires mutation outside the authorized target paths, stop that slice and file a revised bridge proposal before editing that surface.

## Cross-Harness Disposition

- **gpt-5-2-worker**: Selected executor/reviewer model for the program because it has the lowest expected error probability among the available models for large governed refactor work; each worker claim must include manifest evidence, reference-scan evidence, and test evidence.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5640; PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE; generated by gt bridge file-implementation-proposal",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed bridge proposal generators",
  "primary_route": "gt bridge file-implementation-proposal",
  "before_behavior": "Roll out renamed canonical skills (gtkb- prefix) across GT-KB: canonical .claude/skills, harness projections, capability registry, managed-artifact templates, doctor/upgrade coupling, and rules/docs. Absorbs WI-5584 config-canonicalization scope. Bridge: gtkb-skill-rename-rollout.",
  "after_behavior": "CSV-driven canonical relocation and gtkb-prefix rename of legacy .claude hook, rule, skill, and agent-control artifacts, with repository-wide load-bearing reference repair and verification.",
  "self_descriptive_naming": "The generated title, work-item id, target paths, scope, and acceptance criteria name the proposed effect.",
  "obsolete_guidance_disposition": "No guidance is retired by proposal filing; implementation must explicitly disposition obsolete guidance.",
  "history_preservation": "The numbered bridge chain remains append-only; rollback never deletes proposal or verdict artifacts.",
  "baseline": {
    "work_item": "WI-5640",
    "project": "PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY",
    "target_paths": [
      ".claude/hooks",
      ".claude/rules",
      ".claude/skills",
      ".claude/settings.json",
      ".codex/hooks.json",
      ".codex/skills",
      ".codex/gtkb-hooks",
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
    "summary": "CSV-driven canonical relocation and gtkb-prefix rename of legacy .claude hook, rule, skill, and agent-control artifacts, with repository-wide load-bearing reference repair and verification.",
    "scope": [
      "Parse E:\\GT-KB\\gtkb-file-move-and-rename-list.csv into a normalized manifest before mutation, applying the owner-approved inferred corrections for hidden dot-log/json filenames, spec-before-code.py, and skill-scenarios.toml.",
      "Move and rename each manifest source to its canonical destination, preserving file contents, executable behavior, bridge proposal filing, and session startup semantics; create config/hooks as needed.",
      "Update load-bearing references across the authorized repository surfaces so hooks, rules, skills, startup envelopes, templates, tests, generated registry copies, dashboard/docs references, and CI/runtime commands resolve to the new canonical paths.",
      "Repair stale bridge-propose helper references that still point to the retired .claude/skills/bridge-propose path, including canonical .claude skills, Codex skill adapters, tests, templates, and source loaders.",
      "Treat historical/archive citations separately from live dependencies: record intentionally historical references in the implementation report instead of blindly rewriting provenance text.",
      "If a load-bearing reference requires mutation outside the authorized target paths, stop that slice and file a revised bridge proposal before editing that surface."
    ],
    "acceptance_criteria": [
      "A pre-move manifest report accounts for every CSV row, including existence, corrected source name, destination path, tracked/untracked status, directory-vs-file classification, and collision status.",
      "Every moved artifact exists at its destination, every source path is absent or explicitly documented as an allowed compatibility shim, and no destination collision overwrites unrelated content.",
      "Repository-wide text and structured scans find no remaining live references to the retired .claude/hooks, .claude/rules, .claude/skills/bridge-propose, or pre-prefix config/agent-control names except documented historical/provenance references.",
      "Session startup, bridge proposal/review, hook command resolution, skill loading, and harness parity tests continue to pass after relocation.",
      "The implementation report includes exact commands run, scan evidence, intentional historical exceptions, unresolved out-of-scope references if any, and model-quality observations for GPT 5.2 worker performance."
    ]
  },
  "rollback": {
    "instructions": "Revert only the approved source and test implementation targets under separate authority.",
    "verification": "Rerun the proposal's specification-derived tests and bridge preflights."
  },
  "hard_invariants": [
    "Bridge review, implementation-start, and independent verification gates remain mandatory.",
    "Only the declared in-root target paths are attributable to this implementation proposal.",
    "Dispatcher, TAFE, credential, deployment, release, and unrelated work remain outside generated authority."
  ],
  "fail_closed_conditions": [
    "Project membership or active PAUTH coverage is missing.",
    "Target paths escape the project root or candidate/live preflights fail.",
    "Required proposal evidence is empty, malformed, duplicated, or still contains authoring placeholders."
  ],
  "essential_context_preservation": "The generated proposal retains PAUTH, project, work item, targets, specifications, prior deliberations, owner decisions, scope, verification, acceptance, risk, rollback, and expected file changes."
}
```

## Specification-Derived Verification Plan

| Spec | Verification |
| --- | --- |
| `ADR-CROSS-HARNESS-PARITY-001` | Run cross-harness path/reference parity scans covering .claude, .codex, config, generated registry copies, skills, tests, scripts, dashboard, docs, and bridge surfaces. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Confirm all implementation slices begin only from GO verdicts, preserve status-token authority, and avoid Prime Builder authoring LO verdicts. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Confirm the filed proposal links WI-5640, the active project authorization, and governing specs before work starts. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Provide spec-mapped verification evidence suitable for the Loyal Opposition VERIFIED/NO-GO decision. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `GOV-STANDING-BACKLOG-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Run candidate and live bridge applicability preflights; implementation report must add targeted tests. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | Run repo-native tests that exercise hook resolution, skill loading, startup-control loading, bridge proposal filing, and implementation authorization after relocation. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Verify Claude/Codex-facing control surfaces agree on the canonical config/hooks, config/agent-control, and gtbk-prefixed skill locations after the move. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run a broad regression subset such as python -m pytest -q --tb=short or a documented narrower equivalent if full suite cost is prohibitive. |

## Acceptance Criteria

- A pre-move manifest report accounts for every CSV row, including existence, corrected source name, destination path, tracked/untracked status, directory-vs-file classification, and collision status.
- Every moved artifact exists at its destination, every source path is absent or explicitly documented as an allowed compatibility shim, and no destination collision overwrites unrelated content.
- Repository-wide text and structured scans find no remaining live references to the retired .claude/hooks, .claude/rules, .claude/skills/bridge-propose, or pre-prefix config/agent-control names except documented historical/provenance references.
- Session startup, bridge proposal/review, hook command resolution, skill loading, and harness parity tests continue to pass after relocation.
- The implementation report includes exact commands run, scan evidence, intentional historical exceptions, unresolved out-of-scope references if any, and model-quality observations for GPT 5.2 worker performance.

## Risks / Rollback

Risk is moderate because implementation proposals authorize later protected-file work. The service must fail closed around owner-decision evidence, target paths, bridge slug collisions, author metadata, and preflight failures.

Rollback is a revert of the source and test changes. Bridge files and project authorization records are append-only audit artifacts and must not be deleted by rollback.

## Files Expected To Change

- `.claude/hooks`
- `.claude/rules`
- `.claude/skills`
- `.claude/settings.json`
- `.codex/hooks.json`
- `.codex/skills`
- `.codex/gtkb-hooks`
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
