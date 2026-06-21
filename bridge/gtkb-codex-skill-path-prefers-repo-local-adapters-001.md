NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Codex skill-path resolution prefers repo-local adapters and reports fallbacks

bridge_kind: prime_proposal
Document: gtkb-codex-skill-path-prefers-repo-local-adapters
Version: 001
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4364

target_paths: ["scripts/session_self_initialization.py", "platform_tests/scripts/test_session_self_initialization.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

GT-KB's session-startup Codex skill discovery in `scripts/session_self_initialization.py` (`_discover_skill_files`) does not prefer the in-root repo-local `.codex/skills` adapters over the home-directory `~/.codex/skills` copies, and it does not report when a Codex skill is resolved only via a home-directory fallback. When opt-in user-extension discovery is active (`GTKB_DISCOVER_USER_EXTENSIONS=1`), the function scans `~/.codex/skills` and `~/.agents/skills` but never adds the in-root `.codex/skills` adapter tree to the discovery roots; a skill present only in the home directory is therefore resolved silently, with no fallback signal surfaced to the operator. This is the mechanical cause of the observed incident where the Codex `bridge` skill resolved from the out-of-root user-home Codex `.system` location (`~/.codex/skills/.system/bridge/SKILL.md`) and the missing-before-recovery state was not surfaced.

## Defect / Reproduction

Observed incident (origin of WI-4364, component `codex-skills`): the Codex `bridge` skill was missing at the out-of-root user-home Codex location `~/.codex/skills/.system/bridge/SKILL.md` before recovery, and the resolution path did not surface that the skill was being sourced from a home-directory fallback rather than the in-root repo-local adapter. The in-root `.codex/skills/bridge/SKILL.md` adapter exists (it is the canonical, root-contained projection per `.claude/rules/project-root-boundary.md`), but `_discover_skill_files` does not include the in-root `.codex/skills` tree at all, so it cannot prefer it and cannot report the divergence.

Reproduction (logical, exercised in the verification plan):
1. With `GTKB_DISCOVER_USER_EXTENSIONS=1` and `Path.home()` pointed at a fixture home that contains a `~/.codex/skills/<name>/SKILL.md` for a skill name that ALSO exists under the in-root `.codex/skills/<name>/SKILL.md`, call `_discover_skill_files(project_root)`. Current behavior: the in-root `.codex/skills` adapter is absent from the result set (only `~/.codex/skills` is scanned for Codex skills), so the home-directory copy is the resolved surface with no repo-local preference and no fallback report.
2. With the same opt-in fixture but a skill name present ONLY in `~/.codex/skills` (no in-root adapter), call the discovery surface. Current behavior: the home-directory skill is resolved silently; no fallback signal is recorded in the startup model. Expected behavior: the in-root `.codex/skills` adapter is preferred when both exist, and home-directory-only resolutions are reported as fallbacks in the startup payload.

This is a deterministic skill-resolution defect: the fix is to (a) include the in-root `.codex/skills` adapter tree in the Codex discovery roots ahead of the home-directory location, with in-root preference on skill-name collision, and (b) surface a fallback report enumerating Codex skills that resolved only from a home-directory location.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/session_self_initialization.py`, `platform_tests/scripts/test_session_self_initialization.py`. The fix strengthens root-containment by preferring the in-root `.codex/skills` adapters over out-of-root home-directory copies per `.claude/rules/project-root-boundary.md`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the Codex `bridge` skill is the operator's entrypoint to the bridge protocol; resolving it from an unreported home-directory fallback (instead of the in-root adapter) degrades bridge-function reliability, which this spec makes a first-duty concern.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - skill discovery is a durable-artifact lifecycle surface; the fix keeps resolution consistent with the in-root, governed `.codex/skills` adapters rather than transient home-directory state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant governing specs (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives regression tests from the cited specs and the defect behavior (mandatory spec-derived testing).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `SPEC-AUQ-POLICY-ENGINE-001` - cited because the proposal references owner-decision/AUQ-derived authorization; the change introduces no new owner-decision surface and relies on the standing fast-lane authorization, so no AUQ policy change is required.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform startup module (`scripts/...`) and platform tests; no application/adopter surface is touched and no placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-4364 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - establishes the Codex-side fallback discipline (verify-then-fall-back, surface the fallback state); this fix applies the same "prefer canonical, report the fallback" principle to Codex skill-path resolution.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - resolution preference is anchored to the artifact-backed in-root adapters rather than inferred from whichever copy happens to be on disk in the home directory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - aligns the skill-discovery trigger with the in-root adapter lifecycle that should govern which surface is resolved.

## Prior Deliberations

- `DELIB-20265446` - Loyal Opposition GO, gtkb-codex-skill-adapter-helper-packaging - prior decision on Codex skill adapter packaging; this fix governs how those adapters are preferred at resolution time.
- `DELIB-20261506` - Loyal Opposition Verification, gtkb-hygiene-sweep Skill Implementation Report REVISED-1 - prior Codex-skill-adapter verification context (the hygiene-sweep adapter is one of the in-root `.codex/skills` surfaces this fix prefers).
- `DELIB-20261508` - Loyal Opposition Verification, gtkb-hygiene-sweep Skill Implementation Report - sibling Codex-skill-adapter verification context for the same adapter family.
- `DELIB-20265457` - Owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (this WI is in scope).
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - standing fast-lane authorization that, via PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING, covers this small single-concern defect fix.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-4364 is origin=defect, single-concern, introduces no new public API/CLI/behavior beyond removing the defect, and is bounded to ~1 source file + 1 test (well under the fast-lane size guide), so it is covered by the reliability fast-lane standing authorization through active project membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work items; WI-4364 (P2) is in scope.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the standing reliability fast-lane direction that authorizes small defect fixes of this class to proceed through the bridge protocol under the standing PAUTH without a fresh per-item owner approval.

## Requirement Sufficiency

Existing requirements sufficient. The governing specs already establish the contract this fix enforces: `GOV-FILE-BRIDGE-AUTHORITY-001` makes reliable resolution of the bridge skill a first-duty concern, `.claude/rules/project-root-boundary.md` (root-containment) requires in-root artifacts to be the canonical resolution target, and `ADR-CODEX-HOOK-PARITY-FALLBACK-001` establishes the prefer-canonical/report-the-fallback discipline. This is a defect fix that brings `_discover_skill_files` into conformance with those existing requirements; no new or revised requirement/specification is introduced.

## Proposed Scope

1. In `scripts/session_self_initialization.py`, modify `_discover_skill_files` so that, when opt-in user-extension discovery is active (`GTKB_DISCOVER_USER_EXTENSIONS=1`), the in-root repo-local `.codex/skills` adapter tree (`project_root / ".codex" / "skills"`) is added to the Codex discovery roots ahead of the home-directory `~/.codex/skills` location. On skill-name collision between the in-root adapter and a home-directory copy, the in-root adapter is the preferred resolved surface (the home-directory copy is treated as a non-preferred fallback). The default (env var unset) behavior remains root-contained and unchanged: no home-directory scan, no `Path.home()` call (preserving the existing GH-002 default-secure contract).
2. Add a small fallback-reporting accessor (e.g., `_codex_skill_fallbacks(project_root)` returning the list of Codex skill names that resolved only from a home-directory location) and surface it in the startup model alongside the existing `user_extension_discovery` field (e.g., a `codex_skill_fallbacks` list). When opt-in discovery is inactive the list is empty. This makes a home-directory-only resolution visible to the operator instead of silent, satisfying the "reports fallbacks" half of the WI.
3. Add regression tests in `platform_tests/scripts/test_session_self_initialization.py` (see verification plan), reusing the established `monkeypatch.setattr(module.Path, "home", ...)` + `GTKB_DISCOVER_USER_EXTENSIONS=1` fixture pattern already present in that file.

This is the defect-removal path. It does not change the default-secure (env-var-unset) behavior, does not add any new public CLI surface, and does not alter the external Codex CLI's own loader (out of GT-KB scope); it corrects GT-KB's in-root preference and adds fallback visibility within the existing startup-discovery surface.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `.claude/rules/project-root-boundary.md` via `GOV-FILE-BRIDGE-AUTHORITY-001` (in-root adapters are the preferred resolution target) | `test_codex_skill_discovery_prefers_in_root_adapter_over_home` | With opt-in active and a skill name present in BOTH the in-root `.codex/skills` and a fixture `~/.codex/skills`, `_discover_skill_files` includes the in-root adapter path and treats the home-directory copy as a non-preferred fallback (in-root is the resolved surface). |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (report the fallback state) | `test_codex_skill_home_only_resolution_reported_as_fallback` | With opt-in active and a skill present ONLY under fixture `~/.codex/skills` (no in-root adapter), the startup model's `codex_skill_fallbacks` list names that skill. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (default-secure root-containment, no regression) | `test_codex_skill_discovery_default_no_home_scan_no_fallbacks` | With `GTKB_DISCOVER_USER_EXTENSIONS` unset, `_discover_skill_files` does not call `Path.home()` and `codex_skill_fallbacks` is empty (existing GH-002 default-secure contract preserved). |

Execution commands:
- `python -m pytest platform_tests/scripts/test_session_self_initialization.py -q --tb=short`
- `python -m ruff check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py`
- `python -m ruff format --check scripts/session_self_initialization.py platform_tests/scripts/test_session_self_initialization.py`

## Acceptance Criteria

1. When opt-in discovery is active, `_discover_skill_files` includes the in-root `.codex/skills` adapter tree and prefers it over a home-directory copy of the same skill name.
2. Codex skills that resolve only from a home-directory location are surfaced as a fallback in the startup model (`codex_skill_fallbacks`), instead of resolving silently.
3. The default (env-var-unset) behavior is unchanged: no home-directory scan, no `Path.home()` call, empty fallback list (no regression to the GH-002 default-secure contract).
4. The three derived tests pass; `ruff check` and `ruff format --check` are clean on the changed files.

## Risks / Rollback

- Risk: adding the in-root `.codex/skills` tree to discovery could surface Codex adapter skills in the startup inventory that were previously not enumerated there. Mitigation: this is the intended, root-contained behavior; the in-root adapters are governed artifacts and the change only adds them when opt-in discovery is already active, leaving the default path untouched.
- Risk: a skill-name collision could be mis-ordered. Mitigation: the preference rule is deterministic (in-root wins on collision) and is covered by `test_codex_skill_discovery_prefers_in_root_adapter_over_home`.
- Risk: over-reporting fallbacks. Mitigation: the fallback list is populated only for home-directory-only resolutions under active opt-in discovery; it is empty by default, asserted by `test_codex_skill_discovery_default_no_home_scan_no_fallbacks`.
- Rollback: revert the `_discover_skill_files` change and the startup-model field addition in `scripts/session_self_initialization.py`; the change is additive (a new discovery root, a deterministic preference rule, and a reporting field) plus tests, fully reversible with no migration.

## Files Expected To Change

- `scripts/session_self_initialization.py`
- `platform_tests/scripts/test_session_self_initialization.py`

## Recommended Commit Type

`fix`
