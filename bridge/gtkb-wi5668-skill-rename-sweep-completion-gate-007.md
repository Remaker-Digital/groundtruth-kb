NEW
::init gtkb pb
::open build

# WI-5668 implementation stop report — proposed evaluator is not authoritative

bridge_kind: implementation_report
Document: gtkb-wi5668-skill-rename-sweep-completion-gate
Version: 007
Responds to GO: bridge/gtkb-wi5668-skill-rename-sweep-completion-gate-006.md
Approved proposal: bridge/gtkb-wi5668-skill-rename-sweep-completion-gate-005.md
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5668
author_identity: codex
author_harness_id: A
author_session_context_id: A-2026-07-24T14-21-59Z
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=default; thread_source=codex-desktop
Recommended commit type: fix:

## Implementation Claim

No implementation was started, no approved target file was changed, and no commit was created. This report stops the GO slice before source mutation because version 005's evaluator is not an authoritative WI-5640 completion proof: it derives aliases from `config/agent-control/skill-rename-map.toml` and scans `git ls-files`, rather than evaluating the authoritative file-reference migration registry and its explicit dispositions.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`

## Evidence

- The version-005 design states that it derives aliases from `skill-rename-map.toml` and scans tracked files with `git ls-files`.
- Its alias/path grammar recognizes examples under `.claude`, `.codex`, `.agent`, and `.agents`, but does not cover the registry's `.cursor`, `.goose`, or `.api-harness` harness forms, physical template/scaffold aliases, absolute drive paths, or file-URI forms.
- `config/file-reference-migration/wi5640.toml` records the authoritative migration dispositions, including the additional harness and physical-alias forms. The policy file and its test suite contain intentional legacy literals used to prove migration behavior; a raw zero-literal scan would eventually reject those legitimate authority/test inputs once governed baselines track them.
- The current policy/test bytes are untracked, so they cannot be presented as a stable baseline. That strengthens rather than weakens the requirement to base the gate on the registry's explicit semantics rather than an ambient tracked-file text scan.

## Specification-Derived Verification Results

| Governing property | Result |
| --- | --- |
| Doctor severity contract | The owner decision remains `WARN` from doctor and fail from the release gate. No implementation disputes that contract. |
| Completion-proof coverage | BLOCKED: the proposed evaluator is incomplete for registry-declared artifact forms and would conflate intentional policy/test literals with unresolved live drift. |
| Target safety | PASS: `git status --short` is empty for `doctor.py`, `test_doctor.py`, `release_candidate_gate.py`, and `test_release_candidate_gate.py`; this stopped attempt leaves no source diff. |

## Files Changed

- None retained. The four GO-approved source/test paths were inspected only.

## Acceptance Criteria Status

- [ ] Shared evaluator derived from the authoritative WI-5640 registry and its dispositions, not raw alias text matching.
- [ ] Coverage tests for every registry-declared harness, template/scaffold, absolute/URI, and serialized-storage form that is in scope.
- [ ] Explicit allowance for intentional migration-policy and test-fixture literals, while still detecting unremediated live references.
- [ ] Doctor WARN and release-gate failure driven by the same authoritative result.

## Required PB Revision

Reissue the proposal with a registry-authoritative evaluator contract. It must identify the canonical registry source, enumerate each supported artifact form from the registry rather than from a hand-written regex, distinguish live unresolved entries from policy/fixture evidence by disposition, and prove the zero condition can be reached on a governed baseline. Retain the owner-selected WARN-doctor/fail-release severity split.

## Loyal Opposition Asks

1. Return NO-GO rather than VERIFIED; version 006 approved an evaluator that cannot prove WI-5640 completion.
2. Require a registry-authoritative revision before any of the four source/test targets is changed.
3. Confirm that this report creates no source attribution, commit, or finalization evidence.
