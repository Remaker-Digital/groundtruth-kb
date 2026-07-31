REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5 Codex
author_model_version: 2026-07-13 runtime
author_model_configuration: Codex desktop interactive Prime Builder session

bridge_kind: prime_proposal
Document: gtkb-modernization-trust-enforcement-slice
Version: 005
Addresses: bridge/gtkb-modernization-trust-enforcement-slice-004.md

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-WI-5138-TRUST-ENFORCEMENT-20260713
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION
Work Item: WI-5138
target_paths: ["scripts/implementation_start_gate.py","scripts/controlled_artifact_paths.py","scripts/cursor_harness.py","platform_tests/scripts/test_implementation_start_gate.py","platform_tests/scripts/test_controlled_artifact_paths.py","platform_tests/scripts/test_cursor_harness.py"]

# WI-5138 Trust-Enforcement Reconciliation Slice

## Summary

Re-enter the exact six-file modernization trust-enforcement slice through the
strict bridge lifecycle. Existing working-tree bytes at these paths are
preserved as unaccepted draft material from the earlier invalid execution
interpretation. This proposal does not claim those bytes as implemented or
verified. After a fresh independent `GO`, matching claim, and successful
implementation-start packet, Prime Builder will inspect and, only where
necessary, correct the five bounded behaviors below, run the complete targeted
evidence, and submit final hashes and hunk attribution for independent
`VERIFIED` review.

## Finding Response

Version 004 required a proper `REVISED` implementation proposal with an active
bounded PAUTH, exact project/work-item metadata, exact target paths, a valid
requirement-sufficiency state, specification-derived tests, fresh `GO`, claim,
start, implementation report, and independent `VERIFIED`.

That prerequisite is satisfied only when
`gtkb-modernization-wi5138-pauth-activation` is terminal `VERIFIED` and the
cited PAUTH remains active. This draft must not be filed before that state is
observed. No target mutation is authorized by preparing this draft.

## Requirement Sufficiency

Existing requirements sufficient

The frozen modernization acceptance contract, active PAUTH, version 004
corrected `NO-GO`, linked specifications, and existing focused tests are
sufficient for this bounded reconciliation. No new requirement or scope
expansion is proposed.

## Exact Target Baseline

These hashes identify the current draft bytes for concurrency detection only;
they do not approve or attribute every existing hunk to this slice. Before
filing and again after `GO`/claim/start, Prime Builder must rehash all six. Any
pre-filing drift requires refreshing this proposal. Any post-`GO` drift from a
foreign worker requires stopping and returning through the bridge rather than
absorbing the change.

| Path | Bytes | SHA-256 |
|---|---:|---|
| `scripts/implementation_start_gate.py` | 63706 | `ABEC3FEE9F3E3D019681EF22E5984B741094947EF29448F99713733573F7C294` |
| `scripts/controlled_artifact_paths.py` | 6028 | `B773426D5D408C541C1B29CFE27F316A4367C8A0B93E524A1B2860955167ED79` |
| `scripts/cursor_harness.py` | 17800 | `73D25ED71447811B6A61DB49C70E4CF377EAFED72818D9353BE417D03A9CEFF8` |
| `platform_tests/scripts/test_implementation_start_gate.py` | 90394 | `2FBB2D7E7DD11FDB45AD56C83075CE471BEC64D20F19E8B1F4F2B4278A807BA1` |
| `platform_tests/scripts/test_controlled_artifact_paths.py` | 4238 | `E753E6EEAD97BC577511A10728A7BAE8337440BDBF83B0FEE8EEDD9CFFA0E4CB` |
| `platform_tests/scripts/test_cursor_harness.py` | 20283 | `D93D3113167FC1606DC5B409869F9859C65942B9A17A69FF3F8F534EDF00EBBE` |

## Bounded Implementation Scope

1. Recursively inspect common `cmd`, PowerShell, and POSIX shell wrappers for
   direct Git effects. Encoded, malformed, or excessively nested wrappers fail
   closed rather than inheriting read-only treatment.
2. Treat CR and LF command boundaries as separators so a later physical-line
   mutating Git command cannot hide behind an earlier read-only command.
3. Classify the complete mutating Git lifecycle verb set (`create`, `attach`,
   `preserve`, `promote`, `close`, `resume`, `recover`, `drain`) as mutation;
   keep `show` and `validate` read-only.
4. Classify direct writes under `harness-state/`,
   `.gtkb-state/git-lifecycle/`, and
   `.gtkb-state/modernization-release-candidate/` as controlled runtime
   authority mutations requiring governed services.
5. Permit the Cursor harness to pass an explicit read-only `plan` or `ask`
   mode for independent inspection without granting mutation mode.

No other behavior, refactor, formatting sweep, file replacement, or ownership
claim over pre-existing unrelated hunks is in scope. If a required correction
cannot be made within the six targets and five behaviors, stop and file a new
proposal rather than expanding this GO.

## Implementation Plan

1. Confirm the PAUTH activation thread is terminal `VERIFIED`, the PAUTH is
   active, and its operation-time envelope authorizes this proposal's exact
   source/test targets while denying the nine excluded operations.
2. Acquire the matching Prime Builder claim and run both no-write and durable
   `implementation_authorization.py begin` checks for this thread.
3. Rehash the six targets and check for foreign claim/report collisions. Stop
   on unexplained drift.
4. Inspect the exact bounded implementation/test hunks. Preserve unrelated
   concurrent bytes. Apply only corrections needed for the five behaviors.
5. Run the complete targeted pytest and Ruff commands below. Correct only
   in-scope failures and rerun until clean or return `NO-ACTION`/revision.
6. Capture final hashes, explicit hunk attribution, exact commands, counts, and
   observed behavior in a post-implementation report. Obtain independent LO
   `VERIFIED` before counting the slice complete.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5138 trust-enforcement slice; DELIB-20260713-MODERNIZATION-STRICT-BRIDGE-PROTOCOL; DELIB-20260713-MODERNIZATION-BOUNDED-IMPLEMENTATION-AUTHORITY",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "fresh bridge GO, Prime claim, implementation_authorization begin, targeted pytest and Ruff evidence, implementation report, independent VERIFIED",
  "before_behavior": "draft bytes existed from an invalid lifecycle interpretation and trust enforcement around wrapped Git commands, controlled runtime paths, and Cursor read-only mode was not accepted evidence",
  "after_behavior": "ordinary read-only Git inspection remains usable while wrapped or multiline direct Git mutation, mutating Git lifecycle verbs, and direct controlled-runtime writes fail closed; Cursor review can be forced read-only",
  "self_descriptive_naming": "target files and tests keep existing names that identify implementation-start gating, controlled artifact paths, and Cursor harness behavior",
  "obsolete_guidance_disposition": "version 004 remains corrective history; version 005 does not rely on the invalid earlier GO or historical draft test output as implementation evidence",
  "history_preservation": "the numbered bridge chain, PAUTH activation thread, baseline hashes, final hashes, test output, and independent verdict remain append-only evidence",
  "baseline": {
    "proposal_state": "latest bridge version 004 is NO-GO",
    "target_count": 6,
    "accepted_implementation_evidence": "none before a fresh GO and start chain"
  },
  "expected_result": {
    "bounded_behaviors": 5,
    "target_count": 6,
    "excluded_operations": "git commit, push, cleanup, release, deployment, dispatcher mutation, credentials, external-system mutation"
  },
  "rollback": {
    "instructions": "file a separately reviewed successor that reverts only attributed slice hunks while preserving unrelated concurrent bytes and regression tests",
    "test": "rerun the same targeted pytest and Ruff commands from the rollback proposal"
  },
  "hard_invariants": [
    "no protected mutation before GO, active Prime claim, and implementation-start evidence",
    "no ownership claim over pre-existing unrelated hunks",
    "no direct Git, credential, cleanup, release, deployment, dispatcher, or external-system effect",
    "no historical draft test result counted as fresh implementation evidence"
  ],
  "fail_closed_conditions": [
    "PAUTH activation is not terminal VERIFIED or PAUTH envelope is no longer active",
    "any target hash drifts before filing or after GO without attribution",
    "preflight, claim, start, targeted pytest, or Ruff evidence fails",
    "the required correction expands beyond the six target files or five bounded behaviors"
  ],
  "essential_context_preservation": "worker instructions preserve the obvious path: read-only inspection is allowed, mutation routes through governed lifecycle services, and evidence must be current and independently verified"
}
```

## Owner Decisions / Input

- `DELIB-20260713-MODERNIZATION-STRICT-BRIDGE-PROTOCOL`
- `DELIB-20260713-MODERNIZATION-BOUNDED-IMPLEMENTATION-AUTHORITY`

These decisions authorize bounded modernization implementation only after the
strict bridge gates. They do not authorize Git commit/push, credentials,
cleanup, release, deployment, dispatcher mutation, external-system mutation,
unrelated work, or target expansion.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - requires the active bounded
  PAUTH before protected implementation.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - requires live
  envelope evaluation at claim, packet, start, and protected effects.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - bounds mutation classes,
  forbidden operations, included work item, and linked specs.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - keeps PAUTH subordinate to
  exact proposal, GO, target, claim/start, report, and verification gates.
- `DCL-GIT-BRANCH-BINDING-PROMOTION-001` - requires Git effects to use the
  canonical lifecycle and remain fail-closed.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires role-correct numbered bridge
  proposal, verdict, report, and verification states.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the exact
  PAUTH, project, work item, and target metadata above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires complete
  applicable specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires every linked
  behavior to have executed evidence before `VERIFIED`.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - requires the explicit
  intuitiveness/non-impairment disposition and preserved worker paths.
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001` - requires deterministic
  classification and observable evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - preserves the PAUTH, proposal,
  implementation, test, report, and verdict graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps draft, active, blocked, and
  verified states explicit.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - preserves decisions and findings as
  durable artifacts without allowing governance output to replace tests.

## Specification-Derived Verification Plan

| Requirement | Objective test evidence |
|---|---|
| Wrapped and multiline direct Git effects fail closed | `test_shell_wrapped_direct_git_effects_require_lifecycle`, `test_uninspectable_nested_shell_commands_fail_closed`, and direct-Git parameterized cases in `platform_tests/scripts/test_implementation_start_gate.py` |
| Wrapped read-only Git remains usable | `test_shell_wrapped_read_only_git_commands_remain_allowed` |
| Every mutating lifecycle subcommand is gated | `test_git_lifecycle_mutating_subcommands_are_mutation_signals` covers all eight mutating verbs and preserves read-only verbs |
| Authority runtime files cannot be forged by direct write | controlled-artifact parameterized cases for harness, Git-lifecycle, and release-candidate paths |
| Cursor review can be forced read-only | `test_main_can_force_read_only_plan_mode` plus existing Cursor command-construction tests |
| PAUTH/bridge/claim/start remain load-bearing | operation-time and implementation-start tests in `test_implementation_start_gate.py`, plus the live no-write/durable-start receipts |
| No regression outside bounded behavior | Complete targeted suites and Ruff over all six targets |

Execute after `GO`, claim, and start:

```text
python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=short
python -m pytest platform_tests/scripts/test_controlled_artifact_paths.py platform_tests/scripts/test_cursor_harness.py -q --tb=short
python -m ruff check scripts/implementation_start_gate.py scripts/controlled_artifact_paths.py scripts/cursor_harness.py platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_controlled_artifact_paths.py platform_tests/scripts/test_cursor_harness.py
```

The earlier observed `204 passed`, `48 passed`, and Ruff-clean results are
historical draft evidence only. They must be rerun after the valid start chain
and may not be copied into the implementation report as fresh results.

## Acceptance Criteria

1. All five bounded behaviors pass their positive and negative tests.
2. The complete targeted suites and Ruff checks pass from the post-start state.
3. Final hashes and attributed hunks are reported for all six exact targets;
   unrelated dirty bytes are neither reverted nor claimed by this slice.
4. The active PAUTH, exact GO, claim, start, and target bounds remain valid at
   every protected effect.
5. No excluded operation, target expansion, Git action, credential, cleanup,
   release, deployment, dispatcher, or external-system effect occurs.
6. The slice remains incomplete until the post-implementation report receives
   independent LO `VERIFIED` with no open P0/P1/P2 finding.

## Risk And Rollback

The main risks are false positives that block unusual read-only wrappers and
misattribution inside heavily dirty shared files. Positive read-only tests and
exact hunk attribution mitigate those risks. Rollback requires a separately
approved successor and affects only attributed slice hunks; it must not revert
unrelated concurrent work or delete bridge/evidence history.

## Prior Deliberations

- Versions 001-004 preserve the invalid earlier review interpretation and the
  corrected requirement for a fresh pre-implementation lifecycle.
- `gtkb-modernization-wi5138-pauth-activation` supplies the active PAUTH only
  after its independent terminal `VERIFIED` state is observed.
- The two cited 2026-07-13 owner decisions preserve strict bridge review and
  bounded implementation authority.

## Pre-Filing Preflight

- Reconfirm the PAUTH activation is terminal `VERIFIED` and the six baseline
  hashes are current before filing.
- Applicability preflight must pass with no missing required or advisory specs.
- Mandatory ADR/DCL clause preflight must exit zero with no blocking gap.
