REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; build activity envelope; approval_policy=never
author_metadata_source: explicit_interactive_session_metadata

# WI-5458 Revised Deterministic Work-Item PAUTH Selection

bridge_kind: prime_proposal
Document: gtkb-wi5458-proposal-pauth-precedence
Version: 005
Responds to: bridge/gtkb-wi5458-proposal-pauth-precedence-004.md
Revises: bridge/gtkb-wi5458-proposal-pauth-precedence-003.md
Date: 2026-07-18 UTC

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5458-PROPOSAL-PAUTH-PRECEDENCE-V2-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5458
Related Work Items: WI-5420, WI-5294, WI-5466, WI-5476, WI-5488

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "platform_tests/groundtruth_kb/test_cli_bridge_propose.py"]

implementation_scope: source | test | governance_evidence
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## Revision Claim

Version 004's sole new blocking finding is corrected through canonical
MemBase project state and this bridge revision. WI-5466 is now a disclosed
member of the first-class `bridge-proposal-filing` child project and is
explicitly ordered after WI-5458 and before WI-5488:

1. WI-5476
2. WI-5420
3. WI-5294
4. WI-5458
5. WI-5466
6. WI-5488

The child project's version-3 `target_outcome`, `scope_note`, and `notes`
replace the incomplete five-item statement. They now describe one serialized
shared-target gate stack, identify WI-5466 as the live sibling claimant on
`cli_bridge_propose.py`, preserve each work item's independent lifecycle
gates, and forbid dispatcher configuration or runtime mutation.

WI-5466's own MemBase work item now records that it must wait for WI-5458
terminal VERIFIED/focused finalization in addition to its existing WI-5156,
clean-preimage, claim, and schema-v3 start gates. This revision adds WI-5466
to `Related Work Items` and to the hard implementation-start model. No source,
test, dispatcher, TAFE, harness, runtime, Git, deployment, release,
credential, or bridge-history mutation was performed.

## Response To Version 004

### Blocking Finding 3 - Undisclosed live sibling claimant WI-5466

Accepted and corrected.

1. `gt projects add-item` added WI-5466 to
   `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-BRIDGE-PROPOSAL-FILING`.
2. `gt projects reorder` recorded the complete six-member order shown above.
   WI-5458 precedes WI-5466 because PAUTH-selection behavior should settle
   before the later NO-ACTION publication command extends the same CLI file.
   WI-5488 remains last so it validates the combined final gate stack.
3. `gt projects update` corrected the child project's `target_outcome`,
   `scope_note`, and `notes`; the prior "one final gate stack" statement no
   longer omits WI-5466.
4. WI-5466's current work-item version records WI-5458 as a terminal
   predecessor and preserves its current GO v004 without treating that GO as
   authority to bypass the new canonical project order.
5. This revision adds WI-5466 to related-work metadata and the hard gates.

The governed CLI-only current-backlog check repeated
`gt backlog list --contains <target-filename> --json` for
`proposal_filing.py`, `cli_bridge_propose.py`, and
`test_cli_bridge_propose.py`. Beyond the already governed project members, it
surfaced WI-5466 and WI-5484. WI-5466 is now ordered. WI-5484 remains a
withdrawn exploration: its single-use PAUTH is revoked, it has no live bridge
thread, and its canonical status states that no source/test or runtime
mutation occurred. It is not an active shared-target claimant. No additional
live claimant was found by this fresh filtered scan.

## Current Source Ownership

- WI-5420 is terminal VERIFIED at
  `bridge/gtkb-wi5420-canonical-parity-disposition-cli-008.md`; focused commit
  `bb539c8148ed8c4477c65c5fd0f7aa2841d6adc0` is an ancestor of current HEAD.
- WI-5294 is latest REVISED at
  `bridge/gtkb-wi5294-proposal-generator-nonimpairment-schema-003.md` and
  awaits independent review. Its four declared targets are currently clean,
  but those bytes are not WI-5458's implementation baseline until WI-5294 is
  terminal VERIFIED and focused-finalized.
- WI-5466 is latest GO at
  `bridge/gtkb-wi5466-prime-no-action-publication-cli-004.md`; the child
  project now places it after WI-5458, so it is not eligible to claim the
  shared file first.
- WI-5458 performs no source or test work while WI-5294 is nonterminal, while
  the three targets are dirty or claimed, or while fresh reviewed terminal
  preimages are unavailable.

## Requirement Sufficiency

Existing requirements remain sufficient. Version 004 identified incomplete
use of the already-governed project-membership order and backlog-conflict
disclosure obligation, not a missing requirement. The corrected MemBase
project version, six membership versions, WI-5466 work-item status, and this
numbered revision supply the missing durable state.

## Proposed Scope

- Rank every active PAUTH covering the requested work item by:
  - exact singleton `included_work_item_ids` first;
  - then explicit multi-work-item lists, with fewer included IDs more
    specific than larger lists;
  - unrestricted project-membership fallback last.
- Make selection independent of database insertion and row order.
- Fail closed when multiple covering active PAUTHs tie at the most-specific
  rank. Do not choose an arbitrary row.
- Preserve the existing restrictive coverage truth table; this ranks
  multiple already-covering authorizations and does not broaden eligibility.
- Return the selected PAUTH ID in dry-run JSON and successful filing metadata.
- Ensure ambiguous or invalid selection fails before bridge-file or
  dispatcher/TAFE publication.
- Add focused insertion-order, specificity, ambiguity, disclosure, and
  zero-write regression cases to the existing proposal-filing test module.
- Preserve terminal WI-5420 and future terminal WI-5294 bytes outside the
  bounded selection delta.
- Preserve WI-5458-before-WI-5466 source ownership.

Out of scope:

- Dispatcher/TAFE configuration or runtime, harness configuration, routing,
  eligibility, workers, leases, providers, or process control.
- Modification of WI-5466 implementation scope or its existing GO.
- Bridge-history rewrite, direct database access, credentials, Git staging or
  push, deployment, release, destructive cleanup, or unrelated files.

## Hard Implementation-Start Gates

1. WI-5476 is independently VERIFIED/finalized or confirmed non-overlapping.
2. WI-5420 remains terminal VERIFIED and focused-finalized. Satisfied at v008.
3. WI-5294 is independently VERIFIED and focused-finalized.
4. The first-class child project still records the complete order
   WI-5476, WI-5420, WI-5294, WI-5458, WI-5466, WI-5488.
5. WI-5466 remains sequenced after WI-5458 and has not claimed or dirtied
   `cli_bridge_propose.py`.
6. The WI-5458 V2 PAUTH remains active and is selected for WI-5458.
7. This thread is latest independent `GO`.
8. All three targets are clean, unclaimed, and match fresh reviewed terminal
   preimages.
9. One exact `go_implementation` claim and schema-v3 implementation-start
   packet authorize all three paths.
10. Operation-time authorization passes immediately before every mutation.

Any failed gate returns the thread for renewed review. No foreign-hunk
adoption, current-dirty-baseline implementation, or timing-based claimant
selection is authorized.

## Cross-Harness Disposition

- Harness A (Codex), B (Claude Code), C (Antigravity), and E (Cursor):
  applicable as supported interactive consumers of the shared governed
  `gt bridge file-implementation-proposal` CLI. They receive identical PAUTH
  ranking and ambiguity behavior.
- Harness D (Ollama), F (OpenRouter), and H (Alibaba): not source-projection
  targets. Provider workers consume governed packets and do not own these
  proposal-filing source files.

No parity waiver is requested. Existing WI-5420 cross-harness behavior and
the ordered shared-source baseline must remain green.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5458; TEST-11559; bridge/gtkb-wi5458-proposal-pauth-precedence-004.md; DELIB-20266083; bridge-proposal-filing project version 3",
  "canonical_authority": "DCL-PROJECT-AUTHORIZATION-ENVELOPE-001; DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001; DCL-PROJECT-DEPENDENCY-ORDERING-001; GOV-STANDING-BACKLOG-001",
  "primary_route": "gt bridge file-implementation-proposal --wi <WI-ID> --slug <slug> --target-path <path> --dry-run --json",
  "before_behavior": "The first covering active PAUTH can be selected by database row order, while an incomplete project sequence can leave shared-file claimants to session timing.",
  "after_behavior": "The most-specific covering PAUTH is selected deterministically, equal-rank ambiguity fails before publication, and all current shared proposal-filing claimants follow one explicit MemBase order.",
  "self_descriptive_naming": "Selected project_authorization_id, candidate ranks, ambiguity reasons, and the bridge-proposal-filing membership order expose the governing choice.",
  "obsolete_guidance_disposition": "Database insertion order, first-row selection, and the prior five-member one-final-gate-stack statement are superseded as authority.",
  "history_preservation": "Existing bridge chains, terminal predecessor commits, PAUTH versions, and project/work-item versions remain append-only evidence.",
  "baseline": {
    "ordered_subproject": "PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-BRIDGE-PROPOSAL-FILING",
    "membership_order": ["WI-5476", "WI-5420", "WI-5294", "WI-5458", "WI-5466", "WI-5488"],
    "shared_sibling": "WI-5466 follows WI-5458 on cli_bridge_propose.py",
    "linked_test": "TEST-11559"
  },
  "expected_result": {
    "success": "Exact singleton beats multi-WI coverage, which beats unrestricted fallback, independent of row order.",
    "ambiguity": "Equal most-specific candidates fail closed with no publication.",
    "source_ownership": "WI-5294 terminalizes before WI-5458; WI-5458 terminalizes before WI-5466; WI-5488 validates the combined result.",
    "predecessor_preservation": "Terminal WI-5420 and WI-5294 bytes remain unchanged outside the reviewed WI-5458 delta."
  },
  "rollback": {
    "instructions": "Under separate authority, revert only the eventual WI-5458 ranking and focused-test hunks.",
    "verification": "Rerun the proposal-filing suite, compare predecessor hashes, and re-read the six-member project order."
  },
  "hard_invariants": [
    "Restrictive PAUTH coverage semantics do not change.",
    "Selection is independent of database row order.",
    "No equal-rank arbitrary selection.",
    "No publication after failed selection.",
    "WI-5458 does not claim shared source before WI-5294 terminalizes.",
    "WI-5466 does not claim cli_bridge_propose.py before WI-5458 terminalizes.",
    "No dispatcher or TAFE configuration/runtime mutation."
  ],
  "fail_closed_conditions": [
    "No active covering PAUTH.",
    "Multiple equally most-specific covering PAUTHs.",
    "Six-member project order is absent or changed.",
    "WI-5294 is nonterminal or WI-5466 has claimed the shared path.",
    "Target preimage drift, active peer claim, or dirty peer report.",
    "Independent GO, exact claim, schema-v3 start, operation-time authority, tests, VERIFIED, or focused finalization is absent."
  ],
  "essential_context_preservation": "Results retain the WI, project, selected PAUTH, candidate ranks, blocking reason, publication outcome, six-member source order, predecessor state, test mapping, and rollback evidence."
}
```

## Specification Links

- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes the
  bounded PAUTH and proposal path while retaining all later gates.
- `DELIB-20266083` records the owner's restrictive
  `included_work_item_ids` semantics and is the direct decision ancestor for
  deterministic specific-authorization selection.
- `DELIB-20265833` records the earlier independent review history for those
  restrictive semantics.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` keeps all
  dispatcher configuration outside this build proposal.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` permits the
  WI-5458-specific V2 authorization and governed revision.
- No new owner choice is required. This revision uses the project-membership
  ordering mechanism already specified by
  `DCL-PROJECT-DEPENDENCY-ORDERING-001`.
- The dispatcher-configuration hold remains binding. Neither this revision
  nor the implementation may inspect or mutate dispatcher configuration or
  runtime state.

## Specification-Derived Verification Plan

| Requirement | Executable verification | Required result |
| --- | --- | --- |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`; `DCL-PAUTH-INCLUDED-WORK-ITEM-IDS-RESTRICTIVE-001` | Seed exact singleton, explicit multi-WI, and unrestricted PAUTHs in both insertion orders. | Exact singleton wins; then smallest explicit list; unrestricted is fallback. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Seed two equally most-specific active PAUTHs. | Dry-run and live calls fail before writer invocation. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Inspect temporary bridge/publication fakes after denied cases. | No file or dispatcher/TAFE publication occurs. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001`; `GOV-STANDING-BACKLOG-001` | Read child project and repeat target-filename backlog filters immediately before start. | Exact six-member order; no undisclosed live claimant. |
| Cross-harness parity specs | Exercise shared CLI result behavior through existing supported-harness fixtures. | Identical selected PAUTH and ambiguity result for supported interactive consumers. |
| Project/spec linkage authorities | Execute candidate and live proposal preflights. | Exact project, V2 PAUTH, WI, targets, related work, and specs pass. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused proposal-filing modules, Ruff check/format, py_compile, and diff checks. | Existing behavior and all TEST-11559 cases pass. |
| `GOV-WORK-TREE-HYGIENE-001` | Recheck exact target hashes/status and focused finalizer scope. | Only reviewed WI-5458 hunks and bridge chain enter finalization. |

Required commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_cli_bridge_propose.py groundtruth-kb/tests/test_cli_bridge_propose.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py
git diff --check -- groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/groundtruth_kb/test_cli_bridge_propose.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5458-proposal-pauth-precedence
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5458-proposal-pauth-precedence
```

## Acceptance Criteria

1. Exact singleton PAUTH coverage wins over broader active coverage.
2. Smaller explicit lists win over larger lists; unrestricted project
   coverage is fallback only.
3. Equal most-specific candidates fail closed before any publication.
4. Dry-run and live output identify the selected PAUTH and candidate ranks.
5. The canonical child project retains the six-member order, with WI-5458
   before WI-5466 and WI-5488 last.
6. A fresh current-backlog target scan finds no undisclosed active claimant.
7. WI-5420 and terminal WI-5294 behavior remains green.
8. Focused tests, Ruff, format, py_compile, both bridge preflights,
   independent VERIFIED, and focused finalization pass.
9. No dispatcher/TAFE configuration/runtime, harness state, credential,
   deployment, release, push, or unrelated mutation occurs.

## Scope Changes

The three implementation targets and PAUTH-selection behavior are unchanged
from v003. This revision adds only:

- WI-5466 related-work disclosure;
- the six-member canonical project order;
- WI-5458-before-WI-5466 implementation gating;
- corrected child-project outcome/scope/notes; and
- fresh current-backlog claimant-scan evidence.

## Pre-Filing Preflight Subsection

Candidate-content checks executed against these exact completed bytes:

- Applicability preflight: PASS, `preflight_passed: true`,
  `missing_required_specs: []`, `missing_advisory_specs: []`,
  `blocking_errors: []`, packet
  `sha256:e8de15ac9139f2643096ced051dc374cd0213ab27911de290eefe9db2b4881bf`.
- Mandatory clause preflight: PASS, five clauses evaluated, three
  `must_apply`, two `may_apply`, zero mandatory evidence gaps, zero blocking
  gaps, exit `0`.
- First-line role eligibility: active Prime Builder is authorized to file
  `REVISED`; the latest exact thread status is independent `NO-GO` v004.
- The governed revision helper must still pass credential, author,
  project-linkage, related-work collision, target coverage, cross-harness,
  non-impairment, and publication-admission checks before writing v005.

## Risk And Rollback

The principal risk is shared-file churn across WI-5294, WI-5458, and WI-5466.
The six-member MemBase order, cross-claim rejection, dirty-peer-report gate,
fresh preimages, and per-item independent lifecycle make that order
mechanical and reviewable. The implementation risk remains PAUTH ranking
ambiguity; equal-rank cases fail before writer invocation.

Rollback requires separate authority and reverts only the eventual WI-5458
source/test delta. Project, PAUTH, work-item, bridge, verdict, and predecessor
history remain append-only. No dispatcher, TAFE, runtime, carrier, or Git
history rollback is in scope.

## Files Expected To Change

- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_filing.py`
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`
- `platform_tests/groundtruth_kb/test_cli_bridge_propose.py`

## Recommended Commit Type

`fix(bridge)`: select the most-specific work-item PAUTH deterministically.

---

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
