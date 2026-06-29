NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f1377-e9fc-7c91-a7e3-a18d9b259858
author_model: GPT-5
author_model_version: GPT-5
author_model_configuration: Codex desktop automation; Prime Builder; autonomous auto-builder run
author_metadata_source: codex-auto-builder-explicit-runtime-envelope

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4801

# Legacy Harness-Language Scan (WI-4801)

Document: gtkb-wi4801-legacy-harness-language-scan
Version: 001
Author: Prime Builder (Codex, harness A)
Date: 2026-06-29 UTC
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4801
Recommended commit type: feat

## Summary

Implement the first WI-4801 tranche as a deterministic, read-only scanner for legacy harness-name, legacy reviewer-harness, and hard-coded role/harness coupling language in load-bearing GT-KB artifacts. The scanner produces a classified inventory that separates STRIP candidates from KEEP fixtures and historical/audit text before any prose edits occur.

This is deliberately a scan/classification tranche, not a broad rewrite. Live searches show the residue class spans narrative rules, harness parity skill docs, tests, scripts, and historical bridge/audit material. A direct cleanup without a deterministic inventory would risk deleting valid fixture language or editing bridge audit-trail content, both of which are outside the project authorization bounds.

This proposal is filed as the append-only numbered bridge file `bridge/gtkb-wi4801-legacy-harness-language-scan-001.md`; any future response must use the next versioned bridge file rather than deleting or rewriting prior versions.

## Specification Links

- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` - standing obligation to pair retirement/replacement work with obsolete-reference cleanup.
- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` - requires machine-checkable purge-pairing enforcement and motivates deterministic inventory before cleanup.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal includes linked governing specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification derives from the specs above and from WI-4801 acceptance.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal is filed through the governed append-only versioned bridge files path.
- `GOV-STANDING-BACKLOG-001` - WI-4801 remains a MemBase backlog item under the obsolete-reference purge project.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (CLAUSE-IN-ROOT) - all target paths are in `E:\GT-KB`.

## Prior Deliberations

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` - owner directive authorizing obsolete-reference cleanup and the paired purge project.
- Owner AUQ on 2026-06-25 selected full project scope for `PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE`, producing `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25`.
- `gtkb-obsolete-reference-purge-methodology-adr-dcl` (GO at -004) - establishes the methodology ADR/DCL for purge pairing.
- `gtkb-index-md-classified-inventory` (GO at -002) - establishes the KEEP/STRIP/QUARANTINE style classification precedent for residue cleanup.
- `gtkb-obsolete-reference-purge-deterministic-check` (VERIFIED at -004) - implemented the general purge-pairing check; WI-4801 is a separate residue-family cleanup tranche.

## Requirement Sufficiency

Existing requirements are sufficient. WI-4801 names the required cleanup family: legacy harness-name/role linkages and reviewer-harness legacy language in bridge-dispatcher load-bearing artifacts. The active PAUTH includes WI-4801 and permits source, test, config, hook, docs, skill-docs, narrative, and memory mutation, while forbidding bridge audit-trail deletion, blanket `bridge/INDEX.md` guard stripping, and formal GOV/ADR/DCL/SPEC mutation without a separate packet.

## Target Paths

target_paths: ["scripts/check_legacy_harness_language.py", "platform_tests/scripts/test_check_legacy_harness_language.py"]

- `scripts/check_legacy_harness_language.py` (new) - read-only scanner that walks configured in-root load-bearing surfaces and reports candidate matches as KEEP, STRIP, QUARANTINE, or EXCLUDED.
- `platform_tests/scripts/test_check_legacy_harness_language.py` (new) - hermetic tests for term matching, path classification, exclusions, output contract, and live-root smoke behavior.

## Design

The scanner will use an explicit path policy rather than ad hoc grep:

- Included load-bearing families: `.claude/rules/`, `.claude/skills/`, `.codex/skills/`, `.cursor/rules/`, `config/`, `scripts/`, `groundtruth-kb/src/`, `platform_tests/`, `AGENTS.md`, and `CLAUDE.md`.
- Excluded historical/audit/runtime families: `bridge/`, `.claude/worktrees/`, `memory/`, `independent-progress-assessments/`, `.gtkb-state/`, and temporary pytest directories.
- Candidate phrase families: hard-coded reviewer harness phrasing, hard-coded Codex/Claude role pairings, legacy harness-name/role coupling, and comments that make a specific harness identity load-bearing where the canonical role registry should be the authority.
- Classification outputs:
  - `STRIP` - live load-bearing text that should be rewritten in a later cleanup tranche.
  - `KEEP` - fixture/test text where a fixed harness name or ID is the test data under assertion.
  - `QUARANTINE` - generated, temporary, or ambiguous live text that must not be edited in this tranche.
  - `EXCLUDED` - historical/audit/runtime families intentionally out of scope.

The initial implementation is advisory: it exits 0, emits JSON and text summaries, and does not mutate any target file. Later WI-4801 edit tranches can cite the scanner output and propose narrowly-scoped source/doc edits with concrete target paths.

## Verification Plan

### Specification-Derived Verification - Spec-to-Test Mapping

| Linked spec / requirement | Test or command | Expected result |
|---|---|---|
| WI-4801 cleanup family | `test_detects_legacy_reviewer_harness_phrases` | Candidate phrases are detected deterministically. |
| PAUTH forbidden-operation bounds | `test_excludes_bridge_audit_and_runtime_state` | `bridge/`, `.claude/worktrees/`, `.gtkb-state/`, memory, and assessment archives are excluded. |
| Classification precedent from `gtkb-index-md-classified-inventory` | `test_classifies_keep_strip_quarantine` | Scanner distinguishes live cleanup candidates from fixtures and ambiguous generated text. |
| In-root boundary | `test_rejects_out_of_root_paths` | Scanner refuses paths outside `E:\GT-KB`. |
| CLI output contract | `test_json_and_text_outputs_are_stable` | JSON schema and text summary are stable for downstream proposal authors. |
| Live smoke | `python scripts/check_legacy_harness_language.py --project-root . --json` | Exits 0 and emits a candidate summary without mutating files. |
| Code quality | `python -m ruff check scripts/check_legacy_harness_language.py platform_tests/scripts/test_check_legacy_harness_language.py` and `python -m ruff format --check <same>` | Pass. |

## Risk / Rollback

- Risk: false positives on fixture text. Mitigated by explicit KEEP classification and hermetic tests using fixture paths.
- Risk: accidental pressure to edit historical bridge audit records. Mitigated by excluding `bridge/` and treating audit/history as out of scope for WI-4801 edits.
- Risk: scanner becomes another stale authority. Mitigated by making it a read-only advisory helper whose output must be cited by later bridge proposals rather than treated as self-executing cleanup approval.
- Rollback: remove the new script and test. There is no state migration and no source prose mutation in this tranche.

## Owner Decisions / Input

No new owner decision is required. This proposal proceeds under the active obsolete-reference purge PAUTH and asks Loyal Opposition only to review whether the scan/classification tranche is the correct first legal WI-4801 implementation step.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
