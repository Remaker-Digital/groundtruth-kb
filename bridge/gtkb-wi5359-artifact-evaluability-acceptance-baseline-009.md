REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive; resolved_role=prime-builder; dispatcher/TAFE deliberately disabled

# Revised Proposal - Accept the current tracked artifact-evaluability baseline

bridge_kind: prime_proposal
Document: gtkb-wi5359-artifact-evaluability-acceptance-baseline
Version: 009
Responds to: bridge/gtkb-wi5359-artifact-evaluability-acceptance-baseline-008.md
Date: 2026-07-30 UTC
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5359

target_paths: ["scripts/check_artifact_evaluability.py", "platform_tests/scripts/test_check_artifact_evaluability.py"]

implementation_scope: test,governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## First-Line Role Eligibility Check

PASS. The resolved session role is Prime Builder. Prime Builder may author
`REVISED`, and the active draft claim for this thread is held by session
`019fb1f2-2f91-7b82-ac15-acdd56e13d1e`. This proposal performs no target,
dispatcher, TAFE, Git, release, deployment, credential, or external-system
mutation.

## Revision Claim

Version 008 correctly rejected the stale version-001 premise. Both target files
are now tracked at current HEAD, and the checker source hash differs from the
original untracked candidate. This revision replaces the obsolete exact-byte
table and untracked-path conditions with a current-HEAD acceptance baseline.

The current bytes are accepted as the intended present baseline because they
are clean, have no path commits after the sweep that introduced them, pass all
14 focused tests, remain Ruff-clean, and preserve the intentionally unsupported
future scoped CLI. This is an acceptance and evidence transaction only: it
does not retroactively claim that WI-5359 authorized the earlier sweep commit,
and it does not propose changing either protected target.

## Current Exact Baseline

Observed at repository HEAD
`8a35eabc8cae297cbd295223d6ec904aa15212b8`:

| Path | State | Bytes | SHA-256 | Git index blob |
|---|---|---:|---|---|
| `scripts/check_artifact_evaluability.py` | tracked and clean | 14,451 | `2E02AD3911D419BE4EA4A56C8AAE8E0D4A5F25B829406664BE9FD9673B61B862` | `bebfc1f0a98a15a96a519a417f1461cc76fab56f` |
| `platform_tests/scripts/test_check_artifact_evaluability.py` | tracked and clean | 7,933 | `69E4FAC09572619DCCD6C9FA526FBC14BA795AE1225949691E4574B612F15B67` | `3799fa92a02c6d22c63f7b59fa7ff88163cf0e16` |

Both paths entered HEAD in commit
`42a252ab57b5a203e9406b626c741d897e8fb196` (`chore(gtkb): sweep
governable platform work`) and have no later path commits. That provenance is
preserved as historical fact; it is not rewritten as an implementation under
this bridge thread.

## Findings Addressed

### Stale hash and length premise

Response: the source baseline is updated from 14,503 bytes / SHA-256
`AE6B58F5...` to the exact 14,451-byte hash above. The focused test retains its
original length and hash.

### Stale untracked-path premise

Response: both paths are explicitly treated as tracked and clean. The former
fail-closed condition "target becomes tracked before the baseline transaction"
is retired because tracking has already occurred and is part of the observed
baseline.

### Current-byte intent

Response: Prime Builder accepts the current clean bytes as the intended
baseline, subject to independent review. Fresh focused execution produced
`14 passed` in 5.14 seconds. The future `--spec-id`, `--work-item`, and `--gate`
interface remains intentionally absent and exits 2, preserving WI-5153's later
ownership. Ruff check and format checks pass for both paths.

### Premature sweep provenance

Response: the proposal records the sweep commit and makes no retroactive
authorization claim. A future GO authorizes only a no-byte-change acceptance
run, an implementation report containing current evidence, and independent
verification. No Git operation is proposed or required.

### Conflicting backlog projection

Response: WI-5359 remains an active member of the active Assurance project, but
its compatibility backlog row was marked resolved by the prior VERIFIED
reconciler even though the current canonical numbered-file head is NO-GO. This
revision preserves that discrepancy as evidence and follows the authoritative
version-008 correction route. It does not mutate or rely on the stale resolved
projection as proof of completion.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - the current tracked bytes and their historical
  sweep provenance must be explicit rather than silently absorbed.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - the checker and focused
  tests expose the current acceptance contract.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - the baseline
  remains executable and fail closed.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - acceptance must not change the
  current checker, tests, or descendant ownership boundary.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - any post-GO
  acceptance run still requires a matching claim and implementation-start
  packet under the live project authorization.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the append-only numbered chain, independent
  GO, implementation report, and independent VERIFIED remain mandatory.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, authorization,
  work item, and exact paths are explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - each acceptance
  claim is linked to its governing requirement.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - independent verification
  must rerun the exact tests and byte checks below.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` - WI-5153 retains ownership of later
  scoped-evaluability behavior.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the drift finding, correction, and
  terminal evidence remain durable artifacts.
- `GOV-STANDING-BACKLOG-001` - WI-5359 remains the durable carrier despite the
  stale compatibility resolution projection.

## Prior Deliberations

- `DELIB-202666274` - owner authorization for the modernization program while
  retaining bridge, claim/start, independent verification, and exact Git
  boundaries.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` - current
  project-level implementation approval applies to member work items without a
  per-WI approval list.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` - work-item approval is
  inherited from the authorized parent project.

## Owner Decisions / Input

No new owner decision is required. WI-5359 is an active first-class member of
the active Assurance project, and the controlling list-free project PAUTH v3
covers bridge, test, and governance-evidence work. The PAUTH continues to
forbid `git_commit`, push, history rewrite, dispatcher mutation, external
mutation, credentials, deployment, release, and destructive cleanup. This
revision requests none of those operations.

## Requirement Sufficiency

Existing requirements sufficient. The linked evaluability, worktree-hygiene,
mechanical-enforcement, non-impairment, bridge-authority, and
spec-derived-testing carriers already define the exact acceptance and evidence
obligations. This revision corrects stale observed state and proposes no new
normative behavior.

## Scope Changes

1. Replace the stale version-001 untracked byte table with the exact current
   tracked byte table above.
2. Accept current behavior only; add no source, test, configuration, database,
   or Git change.
3. After independent GO, acquire an exact implementation claim and schema-v3
   start packet before running the governed acceptance transaction.
4. Revalidate current HEAD, exact hashes, index blobs, clean status, focused
   tests, Ruff checks, and the expected future-CLI rejection.
5. File an implementation report stating that target byte changes are zero and
   citing the historical sweep honestly.
6. Require independent VERIFIED before treating this thread as terminal.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "bridge version 008 current-state re-observation",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python -m pytest platform_tests/scripts/test_check_artifact_evaluability.py -q --tb=short --timeout=180",
  "before_behavior": "The numbered chain names stale untracked bytes even though both targets are tracked at current HEAD.",
  "after_behavior": "The append-only chain records and independently verifies the exact current tracked baseline without changing either target.",
  "self_descriptive_naming": "The two-path hash table and tracked-state language state the acceptance boundary directly.",
  "obsolete_guidance_disposition": "The version-001 untracked premise is superseded by this append-only revision; prior files remain immutable audit history.",
  "history_preservation": "The sweep commit, stale premise, corrected NO-GO, current behavior, and descendant ownership are all preserved.",
  "baseline": {
    "target_count": 2,
    "tracked_target_count": 2,
    "focused_tests": 14,
    "scoped_cli_supported": false
  },
  "expected_result": {
    "target_count": 2,
    "byte_changes": 0,
    "focused_tests": 14,
    "tracked_target_count": 2,
    "scoped_cli_supported": false
  },
  "rollback": "No target rollback is needed because the acceptance transaction changes no target bytes; supersede only this bridge revision if its evidence is disproved.",
  "hard_invariants": [
    "both current target hashes, lengths, and index blobs remain exact",
    "both targets remain clean and tracked",
    "no WI-5153 behavior is added",
    "no Git operation occurs",
    "no third target is included"
  ],
  "fail_closed_conditions": [
    "target hash, length, index blob, tracked state, or clean status changes",
    "focused collection is not 14 tests or any focused test fails",
    "the future scoped CLI becomes accepted",
    "any target byte or Git mutation is proposed or observed"
  ],
  "essential_context_preservation": "The current checker, focused tests, unsupported future CLI boundary, historical sweep, and WI-5153 ownership remain queryable."
}
```

## Pre-Filing Preflight Subsection

- Candidate applicability preflight: PASS (`preflight_passed: true`); no
  missing required specs, no missing advisory specs, and no blocking errors.
- Project-authorization operation-time evaluation: allowed for both declared
  targets under PAUTH v3 for `implementation_packet_create` and
  `implementation_start`.
- Mandatory clause preflight: PASS; 5 clauses evaluated, 3 `must_apply`, 2
  `may_apply`, zero evidence gaps, and zero blocking gaps.

The governed revision helper remains fail closed on a changed numbered-file
head, missing claim, or failed validation.

## Specification-Derived Verification Plan

| Requirement | Verification | Expected result |
|---|---|---|
| Exact tracked baseline | Record `git rev-parse HEAD`, file lengths and SHA-256 values, `git hash-object`, `git ls-files --error-unmatch`, and scoped `git status --short` | HEAD and the two exact table rows match; both paths are tracked and clean. |
| Current executable behavior | `python -m pytest platform_tests/scripts/test_check_artifact_evaluability.py -q --tb=short --timeout=180` | Exactly 14 tests pass. |
| Descendant boundary | `python scripts/check_artifact_evaluability.py --spec-id DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001 --work-item WI-5158 --gate verification --json` | Exit 2 rejects the future scoped arguments; WI-5153 remains their owner. |
| Code quality | `python -m ruff check scripts/check_artifact_evaluability.py platform_tests/scripts/test_check_artifact_evaluability.py` and matching `ruff format --check` | Both commands pass without mutation. |
| Non-impairment | Rehash and recheck scoped Git status after all commands | Exact values remain unchanged and no target diff exists. |
| Governance completeness | Verify project PAUTH, exact claim/start packet, implementation report, and independent verdict | All gates are current and traceable; only independent VERIFIED may close the thread. |

## Risk And Rollback

The principal risk is laundering a historical sweep into a fabricated claim of
WI-5359 implementation provenance. This revision avoids that by naming the
sweep commit, authorizing no target or Git mutation, and limiting the post-GO
transaction to current evidence and reporting. A second risk is treating the
stale backlog `resolved` projection as terminal authority; the numbered bridge
head and independent verdict remain authoritative.

Because no target bytes change, target rollback is not applicable. If any
baseline observation is disproved, preserve version 009 and file a later
append-only correction. Broad checkout/reset/cleanup, Git commit, dispatcher or
TAFE mutation, release, deployment, credential, and external-system actions are
out of scope.

## Recommended Commit Type

None. The governed acceptance transaction changes no source, test,
configuration, or Git state.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
