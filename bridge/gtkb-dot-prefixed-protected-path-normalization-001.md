NEW

# gtkb-dot-prefixed-protected-path-normalization - Preserve Dot-Prefixed Protected Paths

bridge_kind: prime_proposal
Document: gtkb-dot-prefixed-protected-path-normalization
Version: 001
Author: Prime Builder (Codex automation)
Date: 2026-06-18T02:10:00Z

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: keep-working-20260618T0210Z
author_model: GPT-5 Codex
author_model_version: 2026-06-18
author_model_configuration: autonomous Hygiene PB automation

Project Authorization: PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION
Project: PROJECT-GTKB-MAY29-HYGIENE
Work Item: WI-4642

target_paths: ["scripts/implementation_start_gate.py", "scripts/protected_mutation_guard.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_protected_mutation_guard.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

`WI-4642` identifies a silent protected-path classification escape in two
implementation-governance classifiers. Both
`scripts/implementation_start_gate.py` and `scripts/protected_mutation_guard.py`
normalize candidate paths with `relative_path.replace("\\", "/").lstrip("./")`.
That call strips every leading dot and slash as a character set, so
`.claude/hooks/h.py` becomes `claude/hooks/h.py`, `.github/workflows/ci.yml`
becomes `github/workflows/ci.yml`, `.codex/hooks.json` becomes
`codex/hooks.json`, and `.env` becomes `env`. The normalized strings no longer
match the dot-prefixed protected exact paths or prefixes.

This proposal replaces character-set stripping with an explicit leading
`./` prefix strip that preserves real dotfile and dot-directory names. It also
adds focused regressions for both duplicated classifiers so `.claude/hooks/`,
`.claude/rules/`, `.codex/gtkb-hooks/`, `.github/`, `.claude/settings.json`,
`.codex/hooks.json`, and environment credential files continue to classify as
protected, while already-allowed bridge and diagnostic paths stay allowed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge authority and lifecycle rules govern this proposal, the required Loyal Opposition GO, and the post-implementation verification handoff.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this implementation proposal to cite the governing specification surfaces.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the project authorization, project, and work-item metadata carried in this file.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the eventual implementation report to include spec-derived tests and observed command results.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - governs use of the active May29 Hygiene authorization for this unimplemented work item.
- `GOV-STANDING-BACKLOG-001` - governs backlog/work-item traceability for `WI-4642`.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - defines the no-bridge-bypass invariant enforced by the implementation-start gate for protected mutations.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - frames this fix as artifact-graph preservation: the protected-mutation classifier must not let governance artifacts bypass bridge traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - applies because this proposal preserves explicit proposal -> GO -> implementation report -> VERIFIED lifecycle transitions for protected work.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - applies because the defect was captured as a durable work item and is being routed through a bridge proposal instead of ad hoc source mutation.

## Prior Deliberations

- `DELIB-PROJECT-MAY29-HYGIENE-AUTHORIZE-ALL-20260617` - owner authorization backing `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION` for proposing implementation of all unimplemented May29 Hygiene work items.
- `INTAKE-5a61f299` - claim-gated implementation-start intake; this proposal repairs one classifier that decides whether a mutation needs that gate.
- `gtkb-governance-hook-worktree-root-resolution` - prior bridge thread that closed a separate implementation-start gate path-normalization escape; this proposal is narrower and fixes dot-prefixed relative paths, not worktree root discovery.
- `gtkb-protected-commit-authorization-gate-001` - related May29 proposal for commit-time protected-surface evidence. It explicitly treats the shared `is_protected_path` bug as separate `WI-4642` scope, so this proposal avoids duplicating that commit-time gate work.

## Owner Decisions / Input

No new owner decision is required for this proposal. The work is linked to
`WI-4642`, a member of `PROJECT-GTKB-MAY29-HYGIENE`, and is covered by active
authorization `PAUTH-PROJECT-GTKB-MAY29-HYGIENE-ALL-UNIMPLEMENTED-AUTHORIZATION`,
which authorizes implementation proposals for all unimplemented May29 Hygiene
work items.

## Requirement Sufficiency

Existing requirements sufficient. `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
and `GOV-FILE-BRIDGE-AUTHORITY-001` already require protected mutations to be
gated by bridge GO authorization and work intent rather than silently bypassed.
`WI-4642` is an implementation defect in the classifier used to enforce that
existing rule; no new policy semantics are required.

## Spec-Derived Verification Plan

| Spec | Verification | Expected Result |
|------|--------------|-----------------|
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python -m pytest platform_tests/scripts/test_implementation_start_gate.py::test_is_protected_path_preserves_dot_prefixed_protected_paths platform_tests/scripts/test_implementation_start_gate.py::test_protected_path_classification_preserves_dot_prefixed_prefixes -q --tb=short` | The implementation-start gate classifies dot-prefixed exact paths and prefixes as protected and reports the correct protected classification token. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | `python -m pytest platform_tests/scripts/test_protected_mutation_guard.py::test_guard_classifies_dot_prefixed_protected_paths -q --tb=short` | The protected mutation guard classifies dot-prefixed protected exact paths, prefixes, and environment credential paths as protected. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python -m ruff check scripts/implementation_start_gate.py scripts/protected_mutation_guard.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_protected_mutation_guard.py` and `python -m ruff format --check scripts/implementation_start_gate.py scripts/protected_mutation_guard.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_protected_mutation_guard.py` | The source and focused regression tests are lint-clean and format-clean before the implementation report is filed. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Implementation report cites this bridge proposal, the eventual GO verdict, `WI-4642`, and focused regression evidence. | The fix remains connected to the durable work-item and bridge lifecycle records. |

## Risk / Rollback

Risk is low but security-sensitive: a normalization change can accidentally
broaden or narrow protected-surface detection. The implementation should avoid
generic trimming and only remove explicit leading `./` segments after separator
normalization. Rollback is a single source/test commit revert before filing the
implementation report, or a follow-up `NO-GO` revision if Loyal Opposition finds
an over-broad classification.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Do not introduce credential-shaped fixtures; use synthetic path strings only. | Bridge helper credential scan plus focused changed-file review. | |
| CQ-PATHS-001 | Yes | Keep implementation within the four declared target paths under the project root. | Implementation-start target-path packet and `git diff --name-only` against the target paths. | |
| CQ-COMPLEXITY-001 | Yes | Replace duplicate unsafe normalization with a narrow helper or prefix-strip behavior; do not redesign authorization flow. | Focused pytest coverage on exact and prefix protected-path classification. | |
| CQ-CONSTANTS-001 | Yes | Reuse the existing protected exact, prefix, allowed-write, and diagnostic-write constants. | Source review plus focused classifier tests. | |
| CQ-SECURITY-001 | Yes | Preserve fail-closed protected mutation gating for dot-prefixed hooks, config, CI, and credential files. | Negative classifier regressions proving dot-prefixed protected paths are protected. | |
| CQ-DOCS-001 | N/A |  |  | No product documentation changes are in scope. |
| CQ-TESTS-001 | Yes | Add regression tests before reporting implementation complete. | Focused implementation-start gate and protected-mutation guard pytest commands. | |
| CQ-LOGGING-001 | N/A |  |  | No runtime logging changes are in scope. |
| CQ-VERIFICATION-001 | Yes | Run spec-derived pytest plus Ruff check and format-check before filing the implementation report. | Commands listed in the verification plan. | |

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-dot-prefixed-protected-path-normalization`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

fix

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
