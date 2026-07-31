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


# Correct WI-5668 completion evaluation before any source retry

bridge_kind: prime_proposal
Document: gtkb-wi5668-sweep-completion-gate
Version: 005
Responds to: bridge/gtkb-wi5668-sweep-completion-gate-004.md
Date: 2026-07-24 UTC

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5668
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_skill_rename_sweep.py"]

## Revision Disposition

This revision supersedes the prior `git grep` / `git ls-files` completion
theory. It requests no source mutation now. The existing doctor hunk and
untracked focused test are read-only, quarantined evidence: neither is staged,
attributed, reverted, or committed by WI-5668.

All current and future WI-5668 artifacts remain in-root under `E:\GT-KB`;
the append-only bridge entry is under `E:\GT-KB\bridge\` and no output is
created outside the project root.

A future implementation may begin only after fresh independent GO, matching
claim, and implementation-start packet. It must use a new WI-5668-only patch
and leave the foreign doctor skill-presence rewrites intact and unstaged.

## Corrected Evaluation Contract

The artifact universe must be loaded through
`groundtruth_kb.project.sot_registry` from
`config/registry/sot-artifacts.toml`. The separate authority
`config/file-reference-migration/wi5640.toml` supplies accepted mapping,
alias-form, and disposition rules; it is not the artifact registry.

The evaluator must classify references in registered source-of-truth artifacts,
not merely enumerate tracked files. It must cover the rename grammar across
`.claude`, `.codex`, `.cursor`, `.goose`, and `.api-harness`, including nested
`groundtruth-kb/templates/skills/...`, absolute `E:/GT-KB/...`, `file:///...`,
and SQLite/URI forms where the registry and migration policy require them.

Alias derivation must consume the canonical
`config/agent-control/gtkb-skill-rename-map.toml`, not the retained obsolete
`config/agent-control/skill-rename-map.toml`.

The completion result is zero *unresolved violations* after mapping and
disposition. It must not demand zero raw matches: intentional authority
mappings in `config/file-reference-migration/wi5640.toml` and literal fixture
coverage in `platform_tests/scripts/test_gtkb_file_reference_migration.py`
are expected classified evidence, not failures.

## Consumer Semantics

The doctor remains a warning surface: it reports unresolved violations with
evidence and reports pass only when the classified unresolved set is empty.
The release-completion gate is a distinct consumer of the same corrected,
classified evidence and must fail while any unresolved violation remains. The
doctor warning is not, by itself, WI-5640 closure proof or a release gate.

## Required Verification

| Requirement | Evidence / expected result |
| --- | --- |
| Authoritative artifact universe | Tests load `sot-artifacts.toml` via `groundtruth_kb.project.sot_registry`; unregistered tracked files do not define completion. |
| Mapping/disposition classification | Tests prove intentional policy mappings and fixture literals classify as non-violations. |
| Rename-form coverage | Positive detections cover every harness root, template/scaffold nesting, absolute path, file URI, and registered SQLite form. |
| Canonical alias authority | A regression proves the evaluator reads `gtkb-skill-rename-map.toml` and cannot silently use its obsolete predecessor. |
| Consumer split | Doctor reports warning for unresolved findings; independent release completion fails on the same set and passes only at zero unresolved. |
| Worktree hygiene | Cached/committed patch contains only a future WI-5668 patch; pre-existing doctor and test evidence is preserved until a governed clean baseline or exact hunk isolation is independently re-reviewed. |

## Requirement Sufficiency

Existing requirements are sufficient. WI-5668's accepted outcome is a
deterministic completion signal, while the governing SoT registry and WI-5640
migration policy already define the artifact and disposition authorities this
revision must consume. No new requirement is created.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5668 v004 NO-GO; WI-5640 coordination evidence; read-only inspection of the current doctor candidate.",
  "before_behavior": "A tracked-file regex reports an incomplete and permanently nonzero raw-match count as sweep completion evidence.",
  "after_behavior": "A registry-backed evaluator classifies only unresolved violations, with a warning doctor surface and a separate failing release-completion consumer.",
  "canonical_authority": "config/registry/sot-artifacts.toml via groundtruth_kb.project.sot_registry; config/file-reference-migration/wi5640.toml for mapping and dispositions; config/agent-control/gtkb-skill-rename-map.toml for aliases.",
  "primary_route": "Fresh LO review of this corrected proposal, then a fresh claim and implementation-start packet before a WI-5668-only source/test patch.",
  "baseline": "The prior detector scans git-tracked literals, misses registered reference forms, consumes an obsolete alias map, and counts intentional policy and fixture evidence.",
  "expected_result": "Only unresolved registry-backed violations remain; doctor warns on them and the distinct release-completion gate fails on them.",
  "self_descriptive_naming": "The bridge slug and doctor check name retain WI-5668 and sweep-completion terminology.",
  "obsolete_guidance_disposition": "The previous git-grep zero-condition is retained as historical evidence and must not be used as release or WI-5640 closure proof.",
  "history_preservation": "All prior bridge versions and foreign worktree hunks remain append-only/read-only evidence; none is rewritten or absorbed.",
  "nonimpairment": "No production behavior or source bytes change in this revision; policy mappings and regression literals remain intentional non-violations.",
  "hard_invariants": ["Artifact universe comes from the SoT registry.", "Mappings and dispositions come from the WI-5640 policy.", "A raw literal count never defines completion.", "Doctor warning and release failure remain separate consumers."],
  "fail_closed_conditions": ["Unknown registered reference form", "Stale alias authority", "Unclassified mapping disposition", "Any unresolved violation in the release consumer"],
  "essential_context_preservation": "The self-driving sweep remains loud until true classified completion, while intentional migration policy and test fixtures remain auditable evidence.",
  "rollback": "Do not reset shared files; any future implementation is a new scoped patch under a fresh GO and packet."
}
```

## Specification Links

- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

The owner selected a warning doctor surface and a failing release gate. The
existing self-driving-sweep decision `DELIB-202667193` remains in force, but
does not authorize a detector that reads the wrong universe, treats intentional
policy/test evidence as residuals, or relies on a stale alias authority.

## Pre-Filing Preflight

Run the applicability and clause preflights against this completed revision.
File only if both have no blocking gap; no implementation is authorized by
preflight success alone.

## Risks / Rollback

An incomplete grammar could recreate a false pass; a raw-match zero condition
could make completion permanently unattainable. This revision therefore fails
closed on unknown registered forms and preserves explicit dispositions. No
source bytes are changed by this filing. A future scoped patch is rolled back
only through a new governed change; no shared worktree reset or cleanup is
permitted.
