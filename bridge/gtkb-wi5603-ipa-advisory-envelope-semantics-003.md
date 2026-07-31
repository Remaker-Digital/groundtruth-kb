REVISED
::init gtkb lo
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: reasoning_effort=xhigh; thread_source=user
author_metadata_source: x-codex-turn-metadata

# WI-5603 Advisory-Envelope Retirement Semantics - Revised Proposal

bridge_kind: prime_proposal
Document: gtkb-wi5603-ipa-advisory-envelope-semantics
Version: 003
Responds to: bridge/gtkb-wi5603-ipa-advisory-envelope-semantics-002.md
Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5603-ADVISORY-ENVELOPE-SEMANTICS-2026-07-19
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-5603
target_paths: ["groundtruth-kb/src/groundtruth_kb/activity/profiles.py", "groundtruth-kb/src/groundtruth_kb/session/envelope.py", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/activity-disposition-profiles.toml", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/agent-control/system-interface-map.toml", "platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py"]
implementation_scope: source
requires_review: true
requires_verification: true
Recommended commit type: fix:

## Revision Claim

This revision keeps the exact five-file technical correction from version 001
and fixes every finding in the independent NO-GO. It replaces the unrelated
approval-state PAUTH with an active, exact WI-5603 PAUTH derived from the
owner's retirement decision, corrects the top-level remediation commit
attribution to `64897bd7`, and removes the unfilled helper scaffold.

## Requirement Sufficiency

Existing requirements sufficient. The owner retirement decision, exact WI-5603
PAUTH, and linked specifications fully define the five-file semantic
synchronization. No new or revised requirement is needed before implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `SPEC-INTAKE-8161dc`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT`
- `DELIB-20260718-WI5492-NARRATIVE-PACKET-APPROVAL`
- `bridge/gtkb-retire-ipa-refs-rules-skills-001.md` through
  `bridge/gtkb-retire-ipa-refs-rules-skills-012.md`
- `bridge/gtkb-wi5603-ipa-advisory-envelope-semantics-001.md`
- `bridge/gtkb-wi5603-ipa-advisory-envelope-semantics-002.md`

## Owner Decisions / Input

`DELIB-20260717-INDEPENDENT-PROGRESS-ASSESSMENTS-RETIREMENT` is the direct
owner decision for retiring the deleted surface and is the owner-decision
source of the exact WI-5603 PAUTH. No waiver or additional owner decision is
requested.

## Findings Addressed

### Finding 1 (blocking) - Cited Project Authorization is a scope mismatch, repeating a defect already NO-GO'd once in this exact lineage

Response: replace the mismatched PAUTH with
`PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-WI-5603-ADVISORY-ENVELOPE-SEMANTICS-2026-07-19`.
The canonical readback shows it is active, includes exactly WI-5603, allows
the bridge/metadata/source/test/configuration classes required by this
proposal, and cites the on-topic owner retirement decision.

### Finding 2 (non-blocking, P3) - Problem Statement misattributes the commit that corrected the 4 top-level narrative surfaces

Response: corrected. The top-level narrative/configuration correction is
attributed to `64897bd7`, not `aab90256`. The proposed five-file change remains
unchanged.

### Finding 3 (non-blocking, hygiene) - Unfilled helper-scaffold placeholder left in filed proposal

Response: removed. This revision contains concrete prior deliberations and no
draft placeholder.

## Scope Changes

No implementation-path change from version 001. The scope remains the two
shared Python modules, two packaged v1 registry files, and the focused
advisory-envelope regression test listed in `target_paths`. Dispatcher
configuration/runtime, credentials, Git history, deployment, release,
destructive cleanup, and unrelated paths remain excluded.

## Pre-Filing Preflight Subsection

The governed revision helper executes candidate-content applicability and
ADR/DCL clause preflights before filing and fails closed on any nonzero result.
The live thread must then pass both preflights again before implementation.

## Verification Plan

| Governing requirement | Verification |
| --- | --- |
| `SPEC-INTAKE-8161dc` | Verify the corrected retirement marker remains present in generated advisory-aware activity envelopes. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run all four cases in `platform_tests/scripts/test_advisory_proposal_envelope_scaffold.py` and report observed results. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Read back the exact active WI-5603 PAUTH and require exact project, work-item, and target-path coverage. |
| Packaged registry parity | Compare the affected packaged v1 entries with the already-corrected top-level canonical registry semantics. |
| Python quality | Run `ruff check`, `ruff format --check`, and `git diff --check` on the five approved paths. |

## Risk And Rollback

Risk is low because the repair synchronizes mutually referential source,
packaged registries, and focused tests to an already accepted canonical
retirement rule. Rollback is a focused revert of only the five approved
implementation paths under separate authority. Bridge and MemBase audit
records remain append-only.
