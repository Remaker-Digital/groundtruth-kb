REVISED
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019e9c98-a8e6-7a92-9d75-bd9e7b54064a
author_model: GPT-5 Codex
author_model_version: gpt-5-codex
author_model_configuration: Codex desktop automation; Prime Builder; Keep Working PB
author_metadata_source: explicit Codex automation session metadata; corrected revision 002

bridge_kind: implementation_proposal
Document: gtkb-hygiene-cli-utf8-portability-slice-2-guidance
Version: 002
Revises: bridge/gtkb-hygiene-cli-utf8-portability-slice-2-guidance-001.md
Author: Prime Builder (Codex, harness A)
Date: 2026-06-06 UTC
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HYGIENE-CLUSTER
Work Item: WI-4250
Owner Decision: DELIB-20260630
Recommended commit type: docs
target_paths: [".claude/skills/gtkb-hygiene-sweep/SKILL.md", ".codex/skills/gtkb-hygiene-sweep/SKILL.md", ".codex/skills/MANIFEST.json", "platform_tests/scripts/test_hygiene_sweep_skill.py"]

# Implementation Proposal - Hygiene CLI UTF-8 + portability Slice 2 guidance

## Summary

Revision 002 corrects the generated bridge author metadata in version 001 so the artifact header, body author line, and Prime Builder harness identity all refer to Codex harness A. The implementation scope and verification plan are otherwise unchanged.

This proposal closes the deferred documentation side of WI-4250. Slice 1
(`bridge/gtkb-hygiene-cli-utf8-portability-slice-1-004.md`) VERIFIED the CLI-wide
UTF-8 stream fix and the mechanical `python -m groundtruth_kb` fallback route,
but explicitly deferred SKILL.md guidance because documentation was not yet in
the active PAUTH mutation classes. `DELIB-20260630` then authorized WI-4250 Slice
2 guidance and amended `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-HYGIENE-CLUSTER`
to include `documentation` for that work.

The implementation should make the hygiene skill's fallback instruction durable
and test-pinned: the canonical `.claude` skill must tell operators to run
`gt hygiene sweep` first and fall back to `python -m groundtruth_kb hygiene sweep`
with `PYTHONPATH=groundtruth-kb/src` when `gt` is unavailable; the generated Codex
adapter must carry equivalent content through the adapter pipeline; and the skill
test should assert that guidance so the work item can be resolved without relying
on human memory.

Current-state note: live inspection on 2026-06-06 shows the guidance already
present in `.claude/skills/gtkb-hygiene-sweep/SKILL.md` and in the generated
Codex adapter. This proposal is still necessary because there is no separate
VERIFIED bridge artifact for the deferred WI-4250 Slice 2 documentation closure.
If implementation finds no text delta needed, Prime should still add or confirm
a focused regression assertion and file a post-implementation report with the
no-op/content-confirmation evidence.

## Requirement Sufficiency

Existing requirements sufficient.

WI-4250 plus `DELIB-20260630` are sufficient: the work item requires deterministic
fallback guidance/tests and UTF-8 regression coverage, and the owner decision
authorizes Slice 2 SKILL.md guidance under the hygiene-cluster PAUTH doc-class
amendment. No new owner decision is required.

## Specification Links

Blocking:
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this work proceeds through the indexed file bridge.
- `GOV-STANDING-BACKLOG-001` - WI-4250 is the governed backlog item being closed.
- `GOV-08` - the hygiene workflow read surface should reflect usable current-state commands instead of a PATH-sensitive command only.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the cited PAUTH is active, includes WI-4250, and allows documentation plus test additions.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - implementation must stay inside the PAUTH mutation envelope and target paths.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project, Project Authorization, and Work Item metadata are present above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section cites the governing requirements and constraints.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below maps requirements to tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are inside `E:/GT-KB`.

Advisory:
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the deferred Slice 2 documentation requirement is preserved as a bridge artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability must connect WI-4250, DELIB-20260630, skill text, adapter output, tests, and the eventual backlog closure.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this proposal moves the deferred Slice 2 guidance from authorized/deferred to in-flight, with explicit bridge lifecycle evidence.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the CLI owns deterministic enumeration; the skill owns operator routing and fallback guidance.

## Prior Deliberations

- `DELIB-20260630` - owner authorized WI-4250 Slice 2 fallback guidance and the doc-class PAUTH amendment covering both WI-4250 and WI-4259.
- `DELIB-20260623` - parent hygiene-cluster authorization context.
- `bridge/gtkb-hygiene-cli-utf8-portability-slice-1-004.md` - VERIFIED Slice 1 for the UTF-8 stream fix and mechanical module-entrypoint fallback.
- `bridge/gtkb-hygiene-sweep-skill-008.md` / `DELIB-2673` - VERIFIED hygiene skill precedent and adapter/test expectations.
- `bridge/gtkb-hygiene-sweep-cli-004.md` - VERIFIED companion `gt hygiene sweep` deterministic CLI.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - CLI/skill split rationale.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
| --- | --- | --- | --- | --- |
| CQ-SECRETS-001 | N/A | No credential material is introduced. | Bridge helper credential scan plus no secret-like strings in target text. | Documentation/test-only proposal; no credentials, tokens, or env values. |
| CQ-PATHS-001 | Yes | Keep edits inside declared in-root target paths and use the adapter generator for Codex output. | `implementation_authorization.py begin`, adapter check, and bridge preflights. |  |
| CQ-COMPLEXITY-001 | N/A | No algorithmic code is planned. | Review diff should show skill prose and simple test assertions only. | No control-flow or complexity-bearing source change. |
| CQ-CONSTANTS-001 | N/A | Exact command strings are intentional regression anchors. | Skill test asserts command guidance text. | Literal command strings are the requirement being protected. |
| CQ-SECURITY-001 | N/A | No runtime permission, auth, or credential surface changes. | Target-path review and no source/security code edit. | Documentation/test-only closure. |
| CQ-DOCS-001 | Yes | Update canonical skill guidance and regenerate the Codex adapter. | Skill text assertion and adapter generator `--check`. |  |
| CQ-TESTS-001 | Yes | Add or confirm focused regression coverage for fallback guidance in canonical and Codex skill text. | `python -m pytest platform_tests/scripts/test_hygiene_sweep_skill.py -q --tb=short`. |  |
| CQ-LOGGING-001 | N/A | No logging behavior is changed. | Diff review confirms no logging code or log text. | No runtime logging surface in target paths. |
| CQ-VERIFICATION-001 | Yes | Execute the spec-derived tests, adapter check, and bridge preflights before filing the implementation report. | Commands listed in the verification plan and reported in the post-implementation report. |  |

## Proposed Change

Implementation should:

1. Ensure `.claude/skills/gtkb-hygiene-sweep/SKILL.md` says the primary command is `gt hygiene sweep` and the repo-local fallback is `python -m groundtruth_kb hygiene sweep` with `PYTHONPATH=groundtruth-kb/src` when needed.
2. Regenerate the Codex adapter through `python scripts/generate_codex_skill_adapters.py --update-registry` rather than hand-editing `.codex/skills/gtkb-hygiene-sweep/SKILL.md`.
3. Add or update a focused assertion in `platform_tests/scripts/test_hygiene_sweep_skill.py` that checks the canonical skill text and generated Codex adapter both carry the fallback guidance.
4. Run adapter parity checks so `.codex/skills/MANIFEST.json` remains current if the adapter generator updates metadata.

Out of scope:
- No change to `groundtruth-kb/src/groundtruth_kb/cli.py`; Slice 1 already VERIFIED that source fix.
- No change to the hygiene pattern engine or pattern registry; that belongs to WI-4249.
- No direct MemBase mutation in this implementation report. If LO VERIFIES the implementation report, a later Prime backlog reconciliation may resolve WI-4250 per `DELIB-S345-BRIDGE-VERIFICATION-RETIRES-PARENT-BACKLOG-ITEM`.

## Spec-Derived Verification Plan

- WI-4250 fallback guidance is durable in the skill surface: run `python -m pytest platform_tests/scripts/test_hygiene_sweep_skill.py -q --tb=short`. Expected result: the test asserts canonical and Codex skill text include `python -m groundtruth_kb hygiene sweep` and `PYTHONPATH=groundtruth-kb/src`.
- Codex adapter parity and generated artifact discipline: run `python scripts/generate_codex_skill_adapters.py --update-registry --check`. Expected result: PASS with no stale adapter or manifest drift.
- Existing CLI fallback mechanics remain tested: run `python -m pytest groundtruth-kb/tests/test_cli_utf8_portability.py -q --tb=short`. Expected result: the 5 Slice-1 tests still pass.
- Hygiene CLI and pattern tests remain green: run `python -m pytest platform_tests/scripts/test_hygiene_sweep_cli.py groundtruth-kb/tests/test_hygiene_sweep_patterns.py -q --tb=short`. Expected result: existing hygiene CLI and pattern tests pass.
- Bridge proposal completeness: run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-hygiene-cli-utf8-portability-slice-2-guidance` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-hygiene-cli-utf8-portability-slice-2-guidance`. Expected result: no missing required specs and no blocking clause gaps.

## Owner Decisions / Input

No owner action required. `DELIB-20260630` is the owner approval for this Slice 2
guidance and the active PAUTH doc-class amendment.

## Risk / Rollback

Risk is low. The change is documentation/test-only and keeps source behavior from
Slice 1 unchanged. Rollback is to revert the canonical skill wording, regenerate
the Codex adapter, and remove the focused test assertion.

## Recommended Commit Type

`docs` if only the skill wording and generated adapter change; `test` is also
acceptable if implementation is limited to adding the regression assertion.
