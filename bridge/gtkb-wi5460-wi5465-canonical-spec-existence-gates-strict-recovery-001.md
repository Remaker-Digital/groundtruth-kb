NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; owner-declared ::init gtkb pb; delegated current-state audit; dispatcher/TAFE deliberately disabled
author_metadata_source: explicit current owner transcript and parent Prime Builder session context

bridge_kind: prime_proposal
Document: gtkb-wi5460-wi5465-canonical-spec-existence-gates-strict-recovery
Version: 001
Date: 2026-08-01 UTC
Quarantines structurally invalid predecessor: bridge/gtkb-wi5460-wi5465-canonical-spec-existence-gates-001.md through bridge/gtkb-wi5460-wi5465-canonical-spec-existence-gates-008.md

Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5460-WI5465-SPEC-EXISTENCE-GATE-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5460
Related Work Items: WI-5465, WI-5403, WI-5502, WI-5387, WI-5408, WI-5178, WI-5521, WI-5554, WI-5760, WI-5823, WI-5828, WI-5837, WI-5841
included_work_item_ids: ["WI-5460", "WI-5465"]

target_paths: ["scripts/bridge_applicability_preflight.py", "scripts/implementation_authorization.py", "platform_tests/scripts/test_bridge_applicability_preflight.py", "platform_tests/scripts/test_implementation_authorization_spec_existence.py"]

implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: fix:

# WI-5460/WI-5465 Strict Recovery — Canonical Specification-Existence Gates

## Summary

Create a fresh strict-valid implementation carrier for the bounded WI-5460 and
WI-5465 canonical specification-existence repair. The predecessor cannot accept
a governed successor: its version 002 made the invalid ordinary lifecycle
transition `NEW -> REVISED`, so strict resolution fails before the later
version-006 GO or version-008 NO-GO can supply implementation authority.

The predecessor remains immutable audit evidence. This proposal does not edit,
normalize, delete, rename, or append version 009 to that malformed chain.

The substantive repair remains the four-target design approved historically:

1. bridge applicability must fail closed when an identifier asserted as a
   governing specification, or included by the applicable project
   authorization, does not exist in canonical `current_specifications`; and
2. implementation start must independently revalidate the same existence
   invariant before it creates an implementation-start packet.

Planned or candidate specification identifiers may remain explanatory context,
but they must not satisfy governing-linkage, project-authorization,
requirement-sufficiency, or specification-derived-verification requirements
until they exist canonically.

This proposal is dependency-bearing and does not request immediate
implementation. The WI-5403, WI-5502/WI-5387, WI-5408, and possible WI-5178
shared-target ownership fronts must be governed and cleared before claim/start.

## First-Line Role Eligibility Check

The owner declared this interactive session Prime Builder through `::init gtkb
pb`. `NEW` is Prime Builder-authorized under
`GOV-FILE-BRIDGE-AUTHORITY-001`. This proposal authors no `GO`, `NO-GO`, or
`VERIFIED` status.

## Strict Recovery Evidence

- Canonical physical latest predecessor: version 008 `NO-GO`, SHA-256
  `06D4C7D029F0788509110B618352A2F035D5F63720587C74A92B60CA31D803E9`.
- Predecessor claim: null.
- Strict resolver result: `INVALID_BRIDGE_TRANSITION` with detail `Invalid
  bridge transition NEW -> REVISED` at version 002.
- No strict recovery successor existed when this draft claim was acquired.
- Draft claim row `36237` is held by Prime Builder session
  `019fb19b-7814-73c1-8707-204e432cbf00` through
  `2026-08-01T22:33:19Z`. It authorizes drafting only and is not
  implementation-start authority.

## Finding-by-Finding Response to Version 008

### P1 — `NO-ACTION` cannot close an idle GO

Accepted. Version 007's `Disposition-Close` interpretation is withdrawn.
Inactivity, absence of a claim, and unmet implementation preconditions do not
make a compliant LO verdict stale or terminal. This fresh controller preserves
the work as pending and requests ordinary independent proposal review.

### P1 — Both work items require owner disposition before activation

Corrected in part. Legacy work-item `approval_state` is not operation-time
implementation authority under the owner's project-only authorization doctrine.
Fresh governed reads show both WI-5460 and WI-5465 are active direct members of
the active parent project. The exact bounded authorization
`PAUTH-DISPATCHER-BLACK-BOX-WI5460-WI5465-SPEC-EXISTENCE-GATE-20260717` is
active, unexpired, explicitly includes both WIs, allows bridge, source, test,
metadata, and governance-evidence work, and covers exactly the four declared
targets. No new owner approval is required for this carrier.

That correction does not approve the separate WI-5502 dependency. Current
evidence finds WI-5502 open with no bridge proposal and no active PAUTH that
includes it. Under the same project-only doctrine, WI-5502 must receive owner
approval through an AUQ and a governed proposal before its repair can execute.
This proposal does not absorb or approve WI-5502.

## Current Project and Authorization Evidence

- Parent project
  `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING`
  is active at version 15.
- The project retains a historical `completed_at` value while active. That
  metadata anomaly grants no authority and is outside this proposal.
- `PWM-...-WI-5460` and `PWM-...-WI-5465` are active direct memberships.
- WI-5460 is recorded resolved/resolved but its current status detail still
  identifies this shared proposal and its predecessor gates as incomplete.
- WI-5465 is open/backlogged.
- The exact PAUTH is active at version 1, has no expiry, includes WI-5460 and
  WI-5465, and has no excluded-work-item list.
- The PAUTH permits `source` and `test`; its ordinary bridge, claim,
  implementation-start, testing, independent verification, and finalization
  gates remain mandatory.
- The project has no incoming project dependency that blocks its own work; its
  current dependency list is empty. Shared-file predecessor ordering below is
  the governing readiness constraint.

## Current Target Baseline

Fresh exact-path reads at `HEAD`
`75decbfa704fe50288aecbc5669def329a0825df` establish:

| Target | Current state | SHA-256 / disposition |
| --- | --- | --- |
| `scripts/bridge_applicability_preflight.py` | tracked and dirty; preserved foreign WI-5554 verdict-candidate preparation hunk | `E6E7F98AB4F078648A3AB4E64A07A76B8502E65D638B5AC03FB84EFC18D30230` |
| `scripts/implementation_authorization.py` | tracked and clean | `BB9F5C731D8920793D17305CD5D78F8B8F038CED8189C0D1E4ED9E953BBD3891` |
| `platform_tests/scripts/test_bridge_applicability_preflight.py` | tracked and dirty; preserved foreign WI-5554 verdict-candidate preparation tests | `6A1FEB9AC2F0E1652DCD5E01D7308CAEC34B558D44FC6670E70DC12E9B7E6EAD` |
| `platform_tests/scripts/test_implementation_authorization_spec_existence.py` | absent | planned new test target |

An exact four-target cross-claim collision check returned no collision and the
current implementation-packet inventory reported zero valid packets. Those
negative checks do not make the dirty WI-5554 bytes available: its strict
recovery is physically `GO` at version 002, SHA-256
`B89E26DA4C9A31C919D9FA79B9198D778E296FAE00661EC43E7DD516D58542C7`,
but its claim is null and its implementation was stopped after current
coordination evidence showed the proposal's strict prerequisite condition was
false. The foreign hunk is preserved without adoption. All ownership, packet,
claim, target, and hash checks are point-in-time and must be rerun after an
independent GO and immediately before implementation start.

## Current Dependency and Ownership Gates

Implementation remains held behind all of the following:

1. **WI-5403:** its physical latest is version 012 `NO-GO`, claim null, and
   strict resolution fails at decorated version-003 metadata. It requires a
   fresh strict recovery and independently verified/finalized disposition of
   its shared applicability-preflight behavior.
2. **WI-5502 / WI-5387:** WI-5387's physical version 004 says `VERIFIED`, but
   strict resolution fails at version 003 because `Responds to` is absent.
   WI-5502 remains the exact open repair owner, has no live bridge carrier, and
   currently lacks project authorization. WI-5502 must be owner-approved,
   proposed, independently reviewed, implemented, verified, and finalized; a
   malformed physical `VERIFIED` token or resolved MemBase state is not
   sufficient.
3. **WI-5408:** the malformed predecessor is quarantined and strict recovery
   `gtkb-wi5408-pauth-amendment-owner-evidence-strict-recovery` version 001 is
   currently `NEW`, SHA-256
   `29D31ADC2CE3CC4ECC9DAD966240E0900BD9E23635A0DD41C87959C36E83EBF8`,
   awaiting independent review. WI-5408 must reach independent verification
   and focused finalization before this carrier starts.
4. **WI-5554:** strict recovery version 002 is physically `GO`, but the
   applicability source/test now contain its preserved foreign implementation
   hunk. The implementing session stopped and released its claim after
   coordination established that strict WI-5445/WI-5524 prerequisites were
   not satisfied and packet-first collision detection had missed an overlapping
   WI-5576 claim at admission. WI-5554 must receive a governed disposition and
   focused finalization or its owner must reconcile/remove only its own hunk
   before this carrier starts. This proposal neither adopts nor repairs it.
5. **WI-5178:** both current WI-5178 fronts are `NO-GO` and strict-invalid.
   If a future WI-5178 recovery obtains live ownership of
   `scripts/implementation_authorization.py` before this carrier starts, its
   ownership must be sequenced and finalized first.
6. **Fresh ownership scan:** all four paths must become clean, the new test
   target must remain absent or explicitly owned by this carrier, and no
   foreign claim, valid implementation packet, non-terminal peer report, or
   incompatible target owner may exist at implementation start.

This is strict sequence, not scope absorption. WI-5460/WI-5465 receives no
authority over any dependency's files, bridge history, work item, PAUTH,
claims, report, or finalization.

## Current Defect

The clean applicability preflight enriches mechanically applicable registry
specifications from `current_specifications`, but it does not fail the proposal
when an arbitrary identifier asserted in `## Specification Links` is absent.
It also reads PAUTH included-spec metadata for a separate amendment check rather
than enforcing general canonical existence of every included governing ID.

The clean implementation-start validator checks proposal structure,
requirement-sufficiency phrasing, PAUTH identity, mutation classes, and other
authorization constraints, but it lacks an independent general existence gate
covering every governing citation and PAUTH included-spec identifier before
packet creation.

The planned fourth target does not exist, confirming that the dedicated
cross-layer fail-closed regression module still needs to be created.

## Requirement Sufficiency

Existing requirements sufficient. The defect is missing mechanical enforcement
of existing canonical-linkage and authorization-envelope constraints, not a
missing requirement.

## Proposed Scope

1. Parse identifiers asserted as governing inside the proposal's
   `## Specification Links` section separately from merely contextual planned
   IDs elsewhere in the document.
2. Resolve every governing identifier against canonical
   `current_specifications`; emit deterministic, stable-sorted blocking errors
   identifying the missing proposal citations.
3. Resolve every `included_spec_ids` identifier from the applicable current
   PAUTH against the same canonical view; report that category separately and
   prevent it from authorizing implementation when any entry is absent.
4. Apply the existence invariant in bridge applicability without mutating
   MemBase, consuming claims, creating implementation packets, or changing
   bridge state.
5. Independently revalidate the invariant during schema-v3 implementation
   start before packet creation or any protected mutation.
6. Preserve legitimate requirement/spec-intake proposals that explicitly state
   new or revised requirements are required and do not treat planned IDs as
   existing governing evidence.
7. Preserve WI-5403 declared-target/applicability-path behavior, WI-5408
   canonical PAUTH-amendment validation behavior, PAUTH operation-time
   enforcement, packet hashing, diagnostics, and every unrelated preflight
   rule.
8. Add focused cross-layer regression tests in the declared new test module and
   extend the existing applicability module only where its layer-specific
   behavior is exercised.
9. Introduce no new hard-coded timeout. Existing timeout/concurrency
   centralization remains owned by the Timer Governance project.

## Out of Scope

- No dependency implementation or finalization.
- No MemBase, project, work-item, PAUTH, specification, dispatcher, TAFE,
  runtime, harness, credential, deployment, release, external-system, Git
  index/history, push, or cleanup mutation.
- No rewriting or appending the structurally invalid predecessor.
- No acceptance of a nonexistent identifier as governing evidence.
- No broad validation of prose-only strings outside the authoritative
  Specification Links and PAUTH include-set surfaces.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` — owner evidence
  for the exact WI-5460/WI-5465 PAUTH and bounded four-target repair.
- `DELIB-20260717-CANONICAL-ARTIFACT-REFERENCE-BOUNDARY` — canonical in-root
  evidence boundary.
- `DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE` — mechanically reviewable
  proposal structure.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` and
  `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — project-level
  authority controls; legacy per-WI approval state does not.
- Predecessor versions 001 through 008 — original design, shared-target
  sequencing, GO, invalid stale disposition, and current correction findings.
- Current numbered WI-5387, WI-5403, WI-5408, and WI-5178 chains plus MemBase
  WI-5502 — current dependency evidence.

## Owner Decisions / Input

- The exact active bounded PAUTH already authorizes WI-5460 and WI-5465 under
  the normal bridge and operation-time gates.
- The owner has established that implementation approval is per project and
  member WIs inherit active project authorization; legacy WI approval fields
  are non-authoritative.
- The owner has deliberately disabled the TAFE dispatcher for repairs. This
  proposal does not activate, configure, mutate, or use it.
- No new owner decision is required for this carrier.
- WI-5502 remains a separate unapproved backlog dependency and must be routed
  to the owner through an AUQ before its implementation proposal.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "after_behavior": "both proposal applicability and schema-v3 implementation start reject absent governing and PAUTH-included specification IDs using canonical current_specifications",
  "applicability": "applicable",
  "before_behavior": "nonexistent identifiers can be presented as governing citations or PAUTH include-set members without a general canonical existence blocker at both layers",
  "baseline": {
    "active_same_path_fronts_requiring_sequence_clearance": [
      "WI-5408",
      "WI-5521",
      "WI-5554",
      "WI-5760",
      "WI-5823",
      "WI-5828",
      "WI-5837",
      "WI-5841"
    ],
    "cross_claim_collision_result": "none; the canonical helper returned null",
    "dependency_holds": {
      "WI-5178": "strict-invalid bridge fronts; sequence if it reaches scripts/implementation_authorization.py first",
      "WI-5387": "physical VERIFIED is not strict-terminal and requires governed repair/focused finalization",
      "WI-5403": "strict-invalid NO-GO chain requires fresh recovery and terminal focused finalization",
      "WI-5408": "strict-recovery proposal remains NEW and must become terminal/focused-finalized",
      "WI-5554": "physical strict-recovery GO v002 has a preserved dirty source/test hunk; stopped claim is null and governed disposition/focused finalization is required",
      "WI-5502": "no live bridge carrier or operation-time PAUTH; owner AUQ and governed approval are required"
    },
    "predecessor": {
      "latest_physical_sha256": "06D4C7D029F0788509110B618352A2F035D5F63720587C74A92B60CA31D803E9",
      "latest_physical_status": "NO-GO",
      "latest_physical_version": 8,
      "strict_error_code": "INVALID_BRIDGE_TRANSITION",
      "strict_error_detail": "Invalid bridge transition NEW -> REVISED at version 002"
    },
    "project_authority": {
      "authorization_id": "PAUTH-DISPATCHER-BLACK-BOX-WI5460-WI5465-SPEC-EXISTENCE-GATE-20260717",
      "authorization_status": "active",
      "authorization_version": 1,
      "project_id": "PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING",
      "project_status": "active",
      "project_version": 15,
      "work_item_memberships": {
        "WI-5460": "active",
        "WI-5465": "active"
      }
    },
    "protected_mutation_performed": false,
    "targets": {
      "platform_tests/scripts/test_bridge_applicability_preflight.py": {
        "sha256": "6A1FEB9AC2F0E1652DCD5E01D7308CAEC34B558D44FC6670E70DC12E9B7E6EAD",
        "status": "existing and dirty; preserved foreign WI-5554 test hunk"
      },
      "platform_tests/scripts/test_implementation_authorization_spec_existence.py": {
        "sha256": "not applicable; target is absent",
        "status": "absent planned test"
      },
      "scripts/bridge_applicability_preflight.py": {
        "sha256": "E6E7F98AB4F078648A3AB4E64A07A76B8502E65D638B5AC03FB84EFC18D30230",
        "status": "existing and dirty; preserved foreign WI-5554 source hunk"
      },
      "scripts/implementation_authorization.py": {
        "sha256": "BB9F5C731D8920793D17305CD5D78F8B8F038CED8189C0D1E4ED9E953BBD3891",
        "status": "existing; matches recorded clean preimage"
      }
    }
  },
  "canonical_authority": "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001; DCL-PROJECT-AUTHORIZATION-ENVELOPE-001; GOV-SOURCE-OF-TRUTH-FRESHNESS-001",
  "essential_context_preservation": "preserve requirement/spec-intake planned-ID context, WI-5403 applicability-path evidence, WI-5408 canonical amendment validation, operation-time PAUTH checks, stable packet hashing, and unrelated diagnostics",
  "expected_result": "missing governing IDs fail closed in stable sorted category-specific diagnostics before bridge approval or implementation packet creation",
  "fail_closed_conditions": [
    "missing governing Specification Links ID",
    "missing current PAUTH included_spec_ids entry",
    "unreadable canonical current_specifications",
    "target drift or foreign ownership at implementation start"
  ],
  "hard_invariants": [
    "no MemBase mutation during either existence check",
    "no claim consumption during applicability preflight",
    "no dispatcher or TAFE action",
    "no new hard-coded timeout",
    "no dependency-scope absorption"
  ],
  "history_preservation": "retain the malformed predecessor and every dependency chain as immutable evidence",
  "obsolete_guidance_disposition": "version 007 idle-GO closure and version 008 per-WI approval-state gating are historical evidence, not current authority",
  "primary_route": "one canonical existence classifier shared by applicability and implementation-start adapters",
  "provenance": "WI-5460; WI-5465; TEST-11567; predecessor versions 001-008; fresh 2026-08-01 project, PAUTH, target, claim, and strict-lifecycle reads",
  "rollback": {
    "instructions": "revert only the eventual WI-5460/WI-5465 four-target hunks through a separately governed successor",
    "verification": "dependency commits and unrelated preflight/authorization behavior remain unchanged"
  },
  "schema_version": 1,
  "self_descriptive_naming": "missing_governing_spec_ids and missing_pauth_included_spec_ids"
}
```

## Specification-Derived Verification Plan

| Governing surface | Verification | Required result |
| --- | --- | --- |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Add cases for present, absent, duplicate, and stable-sorted governing IDs; exercise `Existing requirements sufficient` and `New or revised requirement required before implementation`. | Absent governing IDs block; planned contextual IDs do not masquerade as existing authority. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Add PAUTH cases containing present, absent, mixed, duplicate, and empty include sets. | Missing included IDs are category-specific, stable-sorted blockers; valid or list-free PAUTH behavior remains intact. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Exercise both layers against canonical current-specification fixtures and an unavailable/read-failure condition. | Both layers use the canonical view and fail closed when required existence cannot be established. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / operation-time enforcement | After dependencies and independent GO, acquire an exact claim and run schema-v3 begin for the fresh strict slug. | The active exact PAUTH permits only the four-target cohort and packet creation occurs only after existence checks pass. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Re-read strict states, terminal/finalization evidence, exact hashes, claims, valid packets, and peer collisions immediately before start. | WI-5403, WI-5502/WI-5387, WI-5408, and the preserved WI-5554 hunk are governed and focused-finalized; WI-5178 does not own the shared source; targets are current, clean, and collision-free. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the complete focused applicability module plus adjacent implementation-authorization tests. | WI-5403/WI-5408 and unrelated behavior remain intact. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry this mapping, exact commands, and observed results into the later implementation report. | Every linked implementation constraint has executed evidence before independent verification. |

Planned commands after a lawful start:

```text
python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_implementation_authorization_spec_existence.py -q --tb=short
python -m pytest platform_tests/scripts/test_implementation_authorization.py -q --tb=short
python -m ruff check scripts/bridge_applicability_preflight.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_implementation_authorization_spec_existence.py
python -m ruff format --check scripts/bridge_applicability_preflight.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_implementation_authorization_spec_existence.py
git diff --check -- scripts/bridge_applicability_preflight.py scripts/implementation_authorization.py platform_tests/scripts/test_bridge_applicability_preflight.py platform_tests/scripts/test_implementation_authorization_spec_existence.py
```

Applicability and clause preflights must also pass against the exact live
proposal before filing and against the later implementation report.

## Pre-Filing Gate Evidence

Both mandatory gates were run against this completed non-live draft after the
current target, project, PAUTH, claim, and dependency evidence above was
re-derived:

- Applicability preflight: PASS; `missing_required_specs: []`,
  `missing_advisory_specs: []`, `blocking_errors: []`; the exact PAUTH
  operation-time evaluator allowed `implementation_packet_create` and
  `implementation_start` for the four-target cohort. This is proposal-phase
  evidence only and creates no implementation packet.
- Mandatory clause preflight: PASS; five clauses evaluated, four
  `must_apply`, zero evidence gaps, and zero blocking gaps.

These results do not clear the dependency hold and must be rerun against the
exact live numbered proposal immediately before governed filing.

## Acceptance Criteria

1. A fresh strict numbered chain receives independent review; the predecessor
   remains immutable and no version 009 is appended.
2. Every absent governing Specification Links identifier blocks applicability
   in deterministic stable order and cannot satisfy requirement sufficiency.
3. Every absent current PAUTH included-spec identifier blocks both
   applicability and implementation start with category-specific diagnostics.
4. Planned specification context remains legal only when it is not asserted as
   current governing or authorization evidence.
5. Both enforcement layers use canonical current specification state and make
   no MemBase mutation.
6. No implementation packet or protected mutation occurs after an existence
   failure.
7. WI-5403, WI-5502/WI-5387, WI-5408, and the preserved WI-5554 hunk reach
   governed, focused-finalized dispositions before implementation; WI-5178
   has no unresolved ownership collision.
8. All four targets match their implementation-start preimages, all focused and
   adjacent tests pass, Ruff lint and format pass, and both proposal/report
   preflight gates pass.
9. No new hard-coded timer is introduced.

## Risks / Rollback

The main functional risk is rejecting legitimate requirement capture merely
because it names a future specification. The classifier therefore operates on
authoritative governing-link and PAUTH include-set surfaces, not every ID-like
string in prose. The main concurrency risk is absorbing shared-file behavior;
the predecessor sequence and fresh claim/packet/currentness checks fail closed.

Rollback is a separately governed focused revert of only WI-5460/WI-5465-owned
hunks, followed by the same focused and adjacent verification. It must not
rewrite bridge history, change specifications or work items, reset shared files,
or disturb any dependency's evidence.

## Non-Approval Boundary

This draft authorizes no implementation. Protected mutation remains prohibited
until the dependency gates are satisfied, this exact fresh proposal receives an
independent `GO`, the current Prime Builder session holds the exact claim, and
schema-v3 implementation start succeeds for the unchanged four-target cohort.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
