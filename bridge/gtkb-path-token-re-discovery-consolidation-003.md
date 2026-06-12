REVISED

bridge_kind: prime_proposal
Document: gtkb-path-token-re-discovery-consolidation
Version: 003
Author: Codex Prime Builder
Date: 2026-06-12
Responds-To: bridge/gtkb-path-token-re-discovery-consolidation-002.md
Recommended commit type: refactor:

Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4485
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING

author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: 019ebc0a-181f-7791-a64b-482f97486014
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never

target_paths: ["scripts/implementation_authorization.py", "scripts/adr_dcl_applicability_discovery.py", "platform_tests/scripts/test_fab14_path_token_dedup.py"]

---

# PATH_TOKEN_RE Discovery Consolidation - REVISED

## Revision Summary

This revision responds to `bridge/gtkb-path-token-re-discovery-consolidation-002.md`.
The NO-GO found the technical proposal plausible, but the ADR/DCL clause preflight
failed `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` because the
proposal did not explicitly state the bridge filing and `bridge/INDEX.md`
evidence. This revision preserves the implementation intent from `-001` and
adds the `## Bridge Protocol Compliance` section below.

## Summary

`PATH_TOKEN_RE` was consolidated to a single canonical source in
`scripts/implementation_authorization.py` during FAB-14. `scripts/bridge_applicability_preflight.py`
already imports that canonical object, and the dead copy in
`scripts/implementation_start_gate.py` was removed.

`scripts/adr_dcl_applicability_discovery.py` still defines a third private copy.
That copy has drifted in both directions:

| Directory token | Canonical | Discovery copy |
| --- | --- | --- |
| `memory/` | present | missing |
| `.claude/skills` | missing | present |
| `.codex/skills` | missing | present |

The owner chose the superset consolidation on 2026-06-12: extend the canonical
to the true union, then repoint discovery to import it. All three consumers
then share one object and future divergence is made mechanically visible by the
identity test.

## Problem Statement

1. `scripts/adr_dcl_applicability_discovery.py` defines a private `PATH_TOKEN_RE`
   that is not the same object as the canonical `PATH_TOKEN_RE` in
   `scripts/implementation_authorization.py`.
2. The discovery copy lacks `memory/`, so its document-wide harvest silently
   misses memory paths that the canonical path vocabulary now recognizes.
3. The discovery copy includes `.claude/skills` and `.codex/skills`, so a
   one-way import of the current canonical would accidentally remove those
   advisory-discovery matches.
4. No regression test asserts that the discovery helper imports the canonical
   object, so the third-copy drift can recur.

## Proposed Change

1. Extend `scripts/implementation_authorization.py` `PATH_TOKEN_RE` to include
   `.claude/skills` and `.codex/skills`, preserving the existing `memory/`
   member and creating the union of the historical vocabularies.
2. Replace the local `PATH_TOKEN_RE` definition in
   `scripts/adr_dcl_applicability_discovery.py` with the same canonical import
   pattern used by `scripts/bridge_applicability_preflight.py`.
3. Extend `platform_tests/scripts/test_fab14_path_token_dedup.py` to assert:
   - `adr_dcl_applicability_discovery.PATH_TOKEN_RE is implementation_authorization.PATH_TOKEN_RE`;
   - the canonical matches `.claude/skills/...` and `.codex/skills/...`;
   - the existing memory and prose `word/word` safeguards remain intact.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `SPEC-AUQ-NO-LLM-CLASSIFIER-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements already exist:
the HYG-046 single-deterministic-source intent, the owner-approved `memory/`
membership, and the anchored enumerated-repo-directory design. The 2026-06-12
owner decision selected the superset implementation shape among compatible
options and introduced no new requirement.

## Spec-Derived Verification Plan

| Linked spec / decision | Derived test |
| --- | --- |
| `SPEC-AUQ-NO-LLM-CLASSIFIER-001` single-source deterministic matcher | `test_path_token_re_is_one_shared_object` plus a new discovery identity assertion. |
| Owner-selected superset members | New assertions that the canonical pattern matches `.claude/skills/...` and `.codex/skills/...`. |
| Existing `memory/` membership | Existing `test_path_token_re_matches_memory_paths` remains green. |
| Anchored-pattern design | Existing prose `word/word` non-match assertion remains green. |
| Discovery runtime behavior | `platform_tests/scripts/test_adr_dcl_applicability_discovery.py` remains green. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest plus ruff check and ruff format check on changed Python files. |

Planned verification commands:

```text
python -m pytest platform_tests/scripts/test_fab14_path_token_dedup.py platform_tests/scripts/test_adr_dcl_applicability_discovery.py platform_tests/scripts/test_bridge_applicability_preflight.py -q
python -m ruff check scripts/implementation_authorization.py scripts/adr_dcl_applicability_discovery.py platform_tests/scripts/test_fab14_path_token_dedup.py
python -m ruff format --check scripts/implementation_authorization.py scripts/adr_dcl_applicability_discovery.py platform_tests/scripts/test_fab14_path_token_dedup.py
```

## Owner Decisions / Input

The design decision was captured via AskUserQuestion on 2026-06-12: choose the
superset canonical pattern, then repoint discovery to import it. The decision is
also recorded in WI-4485 history. No further owner input is required before
implementation once Loyal Opposition records `GO`.

## Prior Deliberations

- `bridge/gtkb-fab-14-gate-fp-feedback-loop-005.md` and `-007.md` flagged the
  third `PATH_TOKEN_RE` copy in `scripts/adr_dcl_applicability_discovery.py` as
  an out-of-scope follow-on.
- `bridge/gtkb-impl-start-gate-path-token-memory-prefix-fix-001.md` through
  `-004.md` established the owner-approved `memory/` membership.
- `bridge/gtkb-s358-w4-enforcement-calibration-001.md` through `-008.md`
  established the anchored enumerated-directory path-token design.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-path-token-re-discovery-consolidation-003.md` with a
matching `REVISED` line inserted at the top of the document entry in
`bridge/INDEX.md`, above the `-002` NO-GO line. `bridge/INDEX.md` remains the
canonical queue state. Append-only discipline is preserved: prior versions
`bridge/gtkb-path-token-re-discovery-consolidation-001.md` and
`bridge/gtkb-path-token-re-discovery-consolidation-002.md` remain on disk and in
the INDEX; no prior bridge file is deleted, renamed, or rewritten.

## Risk / Rollback

- Risk: extending the canonical pattern changes harvested path tokens. Mitigation:
  the added skills prefixes preserve the existing discovery vocabulary, and the
  preflight applicability config has no required-spec trigger for those prefixes.
- Risk: discovery gains `memory/` harvesting. Mitigation: that is the intended
  defect fix and affects an advisory helper, not a blocking gate.
- Rollback: revert the three target-path edits and remove the new test
  assertions. No data migration or external state change is involved.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
