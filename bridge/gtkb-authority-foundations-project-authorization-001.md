NEW
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript override ::init gtkb pb; reasoning xhigh

bridge_kind: governance_advisory
Document: gtkb-authority-foundations-project-authorization
Version: 001
Date: 2026-07-15 UTC

Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5277
target_paths: ["groundtruth.db"]
implementation_scope: metadata
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

# Project Authorization Activation - Authority Foundations

## Claim

Prime Builder requests independent review of one project-level authorization
for `PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS`. The
authorization implements the owner's project-level decision while preserving
the bridge, exact-target, claim, implementation-start, verification, and
focused-commit gates for every later implementation slice.

This proposal authorizes only the exact `gt projects authorize` metadata
transaction below. It does not adopt, stage, report, verify, or commit any
existing dirty source, test, or configuration change.

## Requirement Sufficiency

Existing requirements are sufficient for the project-authorization metadata
transaction. The approved project charter, the owner's explicit activation
decision, `WI-5277`, and the governing project-authorization specifications
define the boundary. Every protected implementation remains separately gated.

## Owner Decisions / Input

- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` records Mike's
  explicit authorization for the project-level envelope and quarantine rule.
- The owner confirmed that authorization is per project. A project with work
  already begun must have applicable project authorization; otherwise the
  condition is a governance defect.

## Exact Proposed PAUTH Envelope

```toml
id = "PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715"
authorization_name = "Authority Foundations project implementation authorization"
project_id = "PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS"
owner_decision_deliberation_id = "DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION"
scope_summary = "Authorize governed Authority Foundations project work under the approved charter. Each protected slice still requires an exact independent bridge GO, exact target paths, a matching claim, successful implementation-start authorization, executed tests, independent verification, and a focused commit. Existing pre-authorization dirty work remains quarantined candidate evidence. Direct harness contact, dispatcher or runtime mutation, credentials, destructive cleanup, unrelated work, push, deployment, and release are excluded."
allowed_mutation_classes = ["bridge", "metadata", "source", "test", "configuration", "governance_evidence"]
forbidden_operations = ["credential_lifecycle", "destructive_cleanup", "dispatcher_mutation", "external_system_mutation", "git_history_rewrite", "git_push", "production_deployment", "release"]
included_work_item_ids = []
excluded_work_item_ids = []
included_spec_ids = []
excluded_spec_ids = []
expires_at = ""
plan_incomplete = true
```

The empty `expires_at` value above means the CLI omits `--expires-at`, so the
persisted field is `null`.

`governance_evidence` is the registered mutation class for formal-artifact
mutation and approval-packet evidence. The proposal deliberately does not add
unregistered free-form operation labels for direct harness contact or unrelated
work. Those remain explicit owner prohibitions, while exact project membership,
bridge target paths, claims, implementation-start packets, and focused commits
provide the mechanical implementation boundary.

## Exact Metadata Transaction

After independent `GO`, matching Prime Builder claim, and successful
implementation-start authorization for this thread, run exactly:

```text
gt projects authorize PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
  --id PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715
  --owner-decision DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION
  --name "Authority Foundations project implementation authorization"
  --scope "Authorize governed Authority Foundations project work under the approved charter. Each protected slice still requires an exact independent bridge GO, exact target paths, a matching claim, successful implementation-start authorization, executed tests, independent verification, and a focused commit. Existing pre-authorization dirty work remains quarantined candidate evidence. Direct harness contact, dispatcher or runtime mutation, credentials, destructive cleanup, unrelated work, push, deployment, and release are excluded."
  --allowed-mutation bridge
  --allowed-mutation metadata
  --allowed-mutation source
  --allowed-mutation test
  --allowed-mutation configuration
  --allowed-mutation governance_evidence
  --forbid credential_lifecycle
  --forbid destructive_cleanup
  --forbid dispatcher_mutation
  --forbid external_system_mutation
  --forbid git_history_rewrite
  --forbid git_push
  --forbid production_deployment
  --forbid release
  --plan-incomplete
  --change-reason "Activate the owner-approved Authority Foundations project envelope after independent bridge GO and implementation-start authorization."
  --json
```

The displayed command is line-wrapped for review; execution uses the same
arguments in one canonical CLI transaction.

## Quarantined Candidate Evidence

At base `4ba39a438b84ec40c646cfc46c2741d6e7c6a60f`, the following current
worktree files contain substantive operation-time implementation or tests but
have no applicable pre-existing Authority Foundations PAUTH, WI-5178
implementation proposal, implementation GO, claim, or start packet. They are
evidence only and remain untouched by this proposal.

| Path | Status | Current SHA-256 |
| --- | --- | --- |
| `config/governance/project-authorization-operation-taxonomy.toml` | untracked | `E726688AC19484CB1105EC4965C53F3F1CC4E6198E28F71D66D79838878387D8` |
| `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py` | untracked | `5EAB50B26F0EAC3E99C1670007983D7DFFF071B758D062B215FBDDBF3379A9CA` |
| `groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py` | untracked | `DBD48C408512612AE039326894DE22276607DA27704D392FB172D54E7C6A9B3A` |
| `scripts/implementation_authorization.py` | modified and commingled | `CC0C2DD861709826EE5755696BC10D1240DAC39024BF72F67C86185A925B57E3` |
| `scripts/bridge_work_intent_registry.py` | modified and commingled | `58B78A9FB8934100DCB71C69D358B1F0BF4859E1DAAE32EF880D4455EF5E30F2` |
| `platform_tests/scripts/test_implementation_authorization.py` | modified and commingled | `A20B947635E466A2F7AB082803C9800255DD5812FA9CC29F82CF4A8DA21B6C41` |
| `platform_tests/scripts/test_bridge_work_intent_registry.py` | modified and commingled | `FC25DCE70A8388E4137CFAC73EA8B38559E0300332A10AC10ACECDAFAD3A4647` |

The modified-file aggregate diffs are commingled and may not be adopted as
whole-file Authority Foundations work. Any later proposal must derive an exact
HEAD-relative candidate, disclose every hunk, and exclude PAUTH-amendment,
schema-v3 implementation-start, worker-provenance, NO-ACTION claim, and other
foreign work unless separately governed.

## Governance Defect Recovery

`WI-5277` and linked `TEST-11432` record the systemic defect: protected project
work existed without applicable project-authorization provenance. The recovery
order is:

1. Independently review and activate this project authorization.
2. Keep all pre-authorization dirty implementation quarantined.
3. File exact implementation proposals for the project work that should be
   recovered, beginning with the PAUTH operation-time substrate needed by
   `WI-5249`.
4. For each slice, obtain independent GO, acquire the matching claim, complete
   implementation-start authorization, materialize an exact isolated candidate,
   run spec-derived tests, file an implementation report, obtain independent
   verification, and create only the focused reviewed commit.
5. Implement the WI-5277 provenance detector so this condition fails closed
   before future implementation or finalization.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` - controlling
  owner authorization and quarantine boundary.
- `DELIB-20260710-GTKB-MODERNIZATION-AUTHORITY-FOUNDATIONS-CHARTER` - approved
  project charter.
- `DELIB-20260710-GTKB-PLATFORM-MODERNIZATION-PARENT-CHARTER` - parent boundary.
- `DELIB-20260710-GTKB-MODERNIZATION-GATE-1-25-EXECUTION-DESIGN` - design-only
  sequencing context if present; it does not grant implementation authority.
- `bridge/gtkb-modernization-gate-1-25-execution-design-001.md` and `-002.md` -
  reviewed non-implementation design and its explicit authority boundary.
- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` supersedes no
  prior implementation PAUTH because no such project authorization existed.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| Exact owner/project binding | Read back the authorization by ID and require exact project ID, owner decision ID, name, status, and scope. |
| Project-level membership semantics | Require empty include/exclude WI arrays so active project membership, not a WI-specific pseudo-authorization, controls eligibility. |
| Registered envelope vocabulary | Require every allowed mutation class and forbidden operation to normalize against the canonical operation taxonomy with no unknown value. |
| Exact one-row effect | Compare before/after project-authorization state and require one new version-1 authorization plus its plan-incomplete guard, with no pre-existing row modified. |
| Quarantine preservation | Re-hash the seven candidate files and require byte identity before and after PAUTH activation. |
| No bypass | Require independent GO, matching claim, and implementation-start packet before the CLI transaction. |
| Independent completion | File an implementation report with exact readback and quarantine hashes, then obtain independent VERIFIED. |

## Acceptance Criteria

1. The exact project authorization exists once, is active, and names
   `PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS`.
2. It is project-level: no WI-specific include list is used; active project
   membership remains the mechanical work-item boundary.
3. Allowed classes are exactly `bridge`, `metadata`, `source`, `test`,
   `configuration`, and `governance_evidence`.
4. Forbidden operations are exactly the eight registered IDs shown above.
5. The plan-incomplete guard keeps the project open while authorized project
   work remains non-terminal.
6. All seven quarantined candidate files remain byte-identical.
7. No source, test, configuration, bridge-runtime, dispatcher, harness,
   credential, Git, external-system, deployment, or release effect occurs.

## Risks / Rollback

Risk is bounded to one project-authorization metadata row and its
plan-incomplete completion guard. The project envelope is intentionally broad
at the project level but every actual implementation is still constrained by
active project membership, separately reviewed exact target paths, claims, and
implementation-start packets.

Rollback is `gt projects revoke-authorization` through a separately governed
metadata transaction. Append-only owner, project, PAUTH, bridge, and
verification evidence remains preserved. Rollback does not delete or rewrite
the quarantined worktree changes.

## Requested Loyal Opposition Disposition

- `GO` approves only the exact project-authorization metadata transaction.
- `NO-GO` must identify any owner-evidence, project-boundary, vocabulary,
  quarantine, target, test, rollback, or non-impairment defect.
- A later source implementation still requires its own proposal and GO.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
