REVISED
::init gtkb lo
::open build

# WI-5460/WI-5465 Canonical Specification-Existence Gates

bridge_kind: prime_proposal
Document: gtkb-wi5460-wi5465-canonical-spec-existence-gates
Version: 002
Responds to: bridge/gtkb-wi5460-wi5465-canonical-spec-existence-gates-001.md
Corrects: bridge/gtkb-wi5460-wi5465-canonical-spec-existence-gates-001.md
revision_reason: Replace the noncanonical secondary-work-item label with a second exact Work Item metadata line so both governed parents are mechanically discoverable; no implementation scope, target, requirement, or authorization change.
Author: Prime Builder (Codex, harness A)
Date: 2026-07-17 UTC

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5460-WI5465-SPEC-EXISTENCE-GATE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5460
Work Item: WI-5465
included_work_item_ids: ["WI-5460", "WI-5465"]

target_paths: ["scripts/bridge_applicability_preflight.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_bridge_applicability_preflight.py", "platform_tests/scripts/test_implementation_authorization_spec_existence.py"]

implementation_scope: source | protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Add the same canonical specification-existence invariant at both enforcement
layers that approved implementation work crosses. The bridge applicability
preflight must fail an implementation-targeting proposal when a specification
identified as governing in `## Specification Links`, or included by its active
project authorization, does not exist in canonical `current_specifications`.
The implementation-start gate must independently revalidate that invariant
before writing an implementation-start packet.

This closes WI-5460 and WI-5465 as one bounded carrier. WI-5460 covers the
incorrect classification of "Existing requirements sufficient" when its cited
requirements are absent. WI-5465 covers the earlier proposal/GO review gap that
allowed those same nonexistent identifiers through applicability preflight.
An identifier for a planned specification may remain proposal context, but it
must be explicitly described as planned and must not satisfy governing-link,
project-authorization, requirement-sufficiency, or spec-derived-verification
requirements until the specification exists canonically.

The implementation must be deterministic and read-only with respect to
MemBase. Diagnostics must identify every absent specification in stable sorted
order and distinguish proposal citations from authorization-included
identifiers. No bridge, packet, claim, source, test, dispatcher, TAFE, runtime,
or Git mutation may occur after either gate detects an absent governing
specification.

Implementation is sequenced behind terminal disposition of WI-5387 and any
other active owner of the currently dirty applicability-preflight target
bytes. This proposal grants no authority to absorb, overwrite, or finalize
foreign hunks.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - requires the numbered bridge chain and role-authorized statuses to remain canonical.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires concrete governing specification linkage; nonexistent identifiers cannot satisfy that contract.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the project, authorization, and work-item tuple to remain mechanically valid.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires verification to be derived from specifications that canonically exist.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - makes the active PAUTH specification include-set an enforced boundary rather than decorative metadata.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - requires the discovered enforcement gap, implementation, tests, and verification to remain durable linked artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - keeps both work items open until independently verified and focused-finalized.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - requires the two findings, shared implementation carrier, tests, and terminal evidence to remain linked in the durable artifact graph.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - keeps the implementation and all verification evidence inside `E:\GT-KB` platform surfaces.
- `GOV-STANDING-BACKLOG-001` - keeps both derived findings visible until the shared implementation is independently verified.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes bounded carriers for bridge/TAFE/harness defects while preserving proposal, GO, claim, implementation-start, verification, and finalization gates.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` - established mechanically reviewable implementation-proposal structure; this proposal closes a semantic validity gap inside that structure.
- `bridge/gtkb-dispatcher-black-box-spec-foundation-019.md` - supplied the live reproducing case: its report names foundation specifications that the in-root canonical CLI cannot resolve.
- `bridge/gtkb-wi5269-activity-envelope-authority-validators-004.md`, `bridge/gtkb-wi5271-mediated-bridge-packet-views-004.md`, and `bridge/gtkb-wi5272-ordinary-worker-prompt-skill-contract-004.md` - preserve independent NO-GO evidence that nonexistent governing citations passed the earlier mechanical gates.

## Owner Decisions / Input

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes this bounded two-work-item repair carrier.
- The owner's active goal requires all black-box bridge/TAFE/harness child and derived work to reach terminal verified/closed state.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5460-WI5465-SPEC-EXISTENCE-GATE-20260717` limits this proposal to WI-5460, WI-5465, the four declared targets, and the ordinary downstream gates.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, and
`DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` already require concrete canonical
governing linkage and enforceable authorization boundaries. The defect is
missing existence enforcement, not a missing requirement.

## Spec-Derived Verification Plan

| Specification | Verification | Expected result |
| --- | --- | --- |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_implementation_authorization_spec_existence.py -q --tb=short` | An implementation proposal declaring existing requirements sufficient fails before packet write when any governing citation is absent; canonically present citations pass. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | The same focused module plus PAUTH-included-spec cases in `platform_tests/scripts/test_bridge_applicability_preflight.py` | Missing PAUTH include-set identifiers are reported in stable order and cannot authorize implementation. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short` | Existing project/work-item/PAUTH linkage remains valid while nonexistent governing identifiers become blocking errors. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Reproduce the WI-5269/WI-5271/WI-5272 absent-foundation-spec pattern in both focused suites | Both layers fail closed with actionable missing-spec diagnostics; no nonexistent identifier can count as spec-derived evidence. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --content-file .gtkb-state/propose-drafts/gtkb-wi5460-wi5465-canonical-spec-existence-gates-001.md --json` and implementation-start dry-run after GO | Candidate proposal passes before filing; implementation-start remains impossible without a later independent GO and exact claim. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-5460 --json`, `groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-5465 --json`, and latest bridge-chain inspection | Both work items remain open until one implementation report is independently VERIFIED and focused-finalized; terminal bookkeeping cites that shared evidence. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-STANDING-BACKLOG-001` | Read back both work items, TEST-11567, the shared PAUTH, and the numbered bridge chain | The durable graph retains both findings and their shared carrier; neither work item disappears or resolves early. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Resolve every declared target and evidence path, then run `git diff --check -- <four target paths>` | Every path remains inside `E:\GT-KB`; no adopter or external path is read as authority or mutated. |

Also run:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/bridge_applicability_preflight.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_implementation_authorization_spec_existence.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/bridge_applicability_preflight.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_implementation_authorization_spec_existence.py
git diff --check -- scripts/bridge_applicability_preflight.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_implementation_authorization_spec_existence.py
```

## Risk / Rollback

The principal risk is rejecting a legitimate requirement-capture proposal that
mentions a not-yet-created specification. The implementation must therefore
distinguish contextual planned identifiers from identifiers asserted as
governing or included by an implementation PAUTH. A planned identifier never
satisfies implementation requirement sufficiency before canonical creation.
Focused tests must preserve governance/spec-intake flows that declare a
requirement gap and perform no source/test/config mutation.

Rollback is a governed successor that reverts the four-file implementation
commit. It must not rewrite the bridge chain, remove either work item, or
restore acceptance of nonexistent governing citations.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-wi5460-wi5465-canonical-spec-existence-gates`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` - the change closes two demonstrated fail-open governance defects without
adding a new workflow or authority.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
