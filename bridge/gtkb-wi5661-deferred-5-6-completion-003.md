REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata


# WI-5661 deferred findings 5–6: complete source, fixture, and hunk boundary

bridge_kind: prime_proposal
Document: gtkb-wi5661-deferred-5-6-completion
Version: 003
Responds to: bridge/gtkb-wi5661-deferred-5-6-completion-002.md
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5661-SKILL-RENAME-LIVE-BREAK-20260724
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5661
target_paths: ["scripts/harness_parity_phase2.py", "scripts/verify_antigravity_dispatch.py", "platform_tests/scripts/test_harness_parity_phase2.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py"]

## Revision Disposition

This is a new, provenance-valid carrier for only deferred findings 5 and 6.
The original `gtkb-wi5661-skill-rename-live-breaks` terminal chain is retained
as historical partial-scope evidence, never as current implementation
authority. The active singleton PAUTH above, a future independent GO, claim,
and implementation-start packet are the sole authority for any later edit.

No source or test mutation occurs through this revision. All targets are
in-root under `E:\GT-KB`.

## Complete Scope

Finding 5 repairs the capability-registry and managed skill path references in
`scripts/harness_parity_phase2.py`. Its required matching regression fixture is
`platform_tests/scripts/test_harness_parity_phase2.py`: it must build the
renamed `config/agent-control/gtkb-harness-capability-registry.toml` fixture
input so the focused suite resolves the same path as production.

Finding 6 repairs the Antigravity verdict-evidence anchors in
`scripts/verify_antigravity_dispatch.py` and its direct fixture/assertion file
`platform_tests/scripts/test_verify_antigravity_dispatch.py`.

No dispatcher configuration, bridge history, provider runtime, registry
content, or unrelated test fixture is in scope.

## Foreign-Hunk Isolation

The recorded HEAD preimage for `scripts/harness_parity_phase2.py` is
`d1b43f78af4c479fda6b2188c87c55eac905900e`. The allowed WI-5661 patch is
limited to the capability-registry filename and the path literals in the
`_bridge_write_path_status`/`_provider_settings_status` mapping. Any leading
UTF-8 BOM or other byte outside those mapping literals is foreign evidence.

After a future GO, Prime Builder must capture the current unstaged diff,
construct a reviewed WI-5661-only patch against that recorded preimage, use
`git apply --cached --check` then `git apply --cached`, and prove that cached
diff excludes the BOM/foreign preimage while the unstaged diff preserves it.
Whole-file formatting or whole-file staging of this source is prohibited.

## Requirement Sufficiency

Existing requirements are sufficient. The active PAUTH, bridge authority,
skill-rename work item, and test-derived verification obligations define the
complete bounded repair; no new requirement is requested.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5661 deferred findings 5 and 6; v002 NO-GO focused failure evidence.",
  "canonical_authority": "The active WI-5661 singleton PAUTH and fresh bridge lifecycle, not the older terminal partial chain.",
  "primary_route": "Fresh LO GO, exact claim/packet, reviewed four-path patch, immutable scoped commit, report, and independent verification.",
  "before_behavior": "The renamed capability registry is absent from a required fixture tree and live references retain bare managed-skill paths.",
  "after_behavior": "Production mappings and matching test fixtures resolve the canonical gtkb-prefixed paths, without foreign byte attribution.",
  "baseline": "Focused command 27 passed/11 failed because test_harness_parity_phase2 fixtures retained the old registry path; source has foreign BOM evidence.",
  "expected_result": "The two focused modules pass with only the four declared source/test paths committed.",
  "self_descriptive_naming": "The title names WI-5661 deferred findings and the complete source/fixture boundary.",
  "obsolete_guidance_disposition": "The old terminal chain remains evidence only and cannot authorize this retry.",
  "history_preservation": "Prior bridge files and the foreign source hunk remain append-only or unstaged evidence.",
  "nonimpairment": "No test is weakened, no provider runtime changes, and no whole-file formatting absorbs foreign bytes.",
  "hard_invariants": ["four declared paths only", "fresh PAUTH/GO/claim/packet", "fixture mirrors registry path", "BOM excluded from staged patch"],
  "fail_closed_conditions": ["missing fixture path", "preimage mismatch", "foreign diff enters cache", "focused test failure", "extra staged path"],
  "essential_context_preservation": "Deferred findings 5 and 6 are completed as a coherent source-and-test slice rather than a partial terminal claim.",
  "rollback": "Revert only the committed WI-5661 patch under a new governed change; never reset the shared worktree."
}
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Registry fixture parity | `python -m pytest platform_tests/scripts/test_harness_parity_phase2.py -q --tb=short` | no `FileNotFoundError`; mapping assertions pass |
| Antigravity anchor repair | `python -m pytest platform_tests/scripts/test_verify_antigravity_dispatch.py -q --tb=short` | canonical gtkb-verify anchors pass |
| Combined contract | both modules in one pytest invocation | all collected tests pass |
| Foreign-hunk protection | cached/unstaged diff evidence before and after commit | BOM/foreign bytes excluded and preserved |
| Quality | Ruff check and format check on four targets | clean without whole-file source formatting |
| Closure | report includes commit SHA/path list plus independent LO review | no VERIFIED without immutable scope proof |

## Owner Decisions / Input

No new owner decision is required. `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`
retains a lighter reliability path while preserving all bridge, authorization,
provenance, and independent verification controls.

## Pre-Filing Preflight

Run both applicability and clause preflights against this completed revision.
Preflight success permits filing only; it does not authorize a protected edit.

## Risk / Rollback

The risks are a false-green fixture repair and absorption of a foreign BOM.
The explicit source/test scope and cached-versus-unstaged proof fail both
closed. This filing changes no source or test bytes.
