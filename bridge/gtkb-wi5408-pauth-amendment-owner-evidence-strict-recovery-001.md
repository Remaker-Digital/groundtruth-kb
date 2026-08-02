NEW
::init gtkb pb
::open build
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6
author_model_version: gpt-5.6
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined Prime Builder role; delegated draft audit; dispatcher/TAFE deliberately disabled
author_metadata_source: explicit_owner_direction plus current session envelope

# WI-5408 Strict Recovery Proposal — Canonical PAUTH Amendment Validation in Applicability Preflight

bridge_kind: prime_proposal
Document: gtkb-wi5408-pauth-amendment-owner-evidence-strict-recovery
Version: 001
Quarantines structurally invalid predecessor: bridge/gtkb-wi5408-pauth-amendment-owner-evidence-applicability-001.md through bridge/gtkb-wi5408-pauth-amendment-owner-evidence-applicability-007.md
Date: 2026-08-01 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5408

target_paths: ["scripts/bridge_applicability_preflight.py", "platform_tests/scripts/test_bridge_applicability_preflight.py"]

implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: fix:

This proposal performs no MemBase mutation.
This proposal performs no approval-evidence work and writes no approval packet.

## In-Root Placement Evidence

The completed numbered revision will reside under `E:\GT-KB\bridge\`, and
both implementation targets reside under the same mandatory GT-KB project
root: `E:\GT-KB\scripts\bridge_applicability_preflight.py` and
`E:\GT-KB\platform_tests\scripts\test_bridge_applicability_preflight.py`.
No generated or live dependency path outside `E:\GT-KB` is proposed.

## Revision Claim

This fresh strict-valid controller is required because the predecessor cannot
accept a governed successor. Its version 005 declares `Responds to` version 003
instead of the immediately preceding version 004. Typed publication therefore
rejects a would-be v008 with `WRONG_RESPONDS_TO_LINK` before capability mint,
pending-sidecar creation, or physical write. The failed append created no v008
and its old-thread claim was released. Every predecessor file remains immutable
audit evidence; this replacement does not edit, normalize, delete, rename, or
use that malformed chain as implementation-start authority.

The current implementation scope and evidence below are restated in full so
this new version 001 is self-sufficient for independent review.

Version 007 correctly rejects version 006's attempt to use `NO-ACTION` as an
idle-GO closure. This revision leaves the thread active and presents the current
implementation proposal against the now-clean shared-file baseline.

Version 007's separate claim that `WI-5408` is unapproved is not controlling.
The current project-only doctrine makes the active parent project authorization
the implementation-approval source; legacy `work_items.approval_state` is
non-authoritative. Fresh governed CLI reads show that `WI-5408` is an active
member of the active Authority Foundations project and that the project has an
active, unexpired, list-free authorization with no included or excluded work-item
list. No new owner approval or AUQ is required for this project member.

This revision does not itself authorize protected mutation. Implementation
still requires an independent current `GO`, a fresh exact-session work-intent
claim, a successful implementation-start packet, exact target currentness and
collision checks, executed specification-derived tests, an implementation
report, and independent verification/finalization.

## Finding-by-Finding Response

### Version 007 P1 — `NO-ACTION` is not closure

Accepted. Version 006's closure interpretation is withdrawn. This fresh `NEW`
controller is an ordinary current-baseline implementation proposal and does not
claim completion, withdrawal, deferral, or terminal state.

### Version 007 P1 — WI-5408 remains unapproved

Corrected under the owner-established project-only authority model:

- `gt backlog list --member-of PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS --id WI-5408 --json` returns the work item as a member of that project.
- `gt projects show PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS --json` reports the project `active` at version 4 and reports active membership `PWM-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-WI-5408`.
- `gt projects authorizations PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS --json` reports `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715` as `active`, unexpired, and list-free: both `included_work_item_ids` and `excluded_work_item_ids` are null. Its allowed mutation classes include `source` and `test`.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` and `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` explicitly make the parent project's authority controlling and retire operational reliance on individual WI approval state.

The `approval_state: unapproved` compatibility field returned by
`gt backlog show WI-5408 --json` is therefore not an implementation gate. The
active list-free project authorization is controlling per
`DELIB-202667719` as well.

## Current-State Re-Derivation

### Exact target baseline

Both target paths are currently tracked, clean, and byte-identical to `HEAD`
`75decbfa704fe50288aecbc5669def329a0825df`:

| Target | Current SHA-256 | Current state |
| --- | --- | --- |
| `scripts/bridge_applicability_preflight.py` | `5F16BADECCB1B5D49438C62C5DFD3AA1FF5E6AE092F1C424A454F035D9C0C4D9` | tracked and clean |
| `platform_tests/scripts/test_bridge_applicability_preflight.py` | `C54DA28106122607A1E4BE26D4792BA5F83AA37AC9E61C3655FF8681790D4BB9` | tracked and clean |

The prior WI-5403/WI-5408 dirty-byte collision no longer exists as an
uncommitted-path collision. The shared baseline now includes WI-5403's
substantively accepted declared-target/applicability-evidence separation and
the rejected parallel PAUTH-amendment validator. WI-5403 remains latest
`NO-GO` at version 012 for a finalization-chain parser blocker, not for the
shared source/test behavior. WI-5403 has no current claim, and its old
implementation-start packet expired on 2026-07-18.

All implementation packets found under the exact source target are expired;
the newest such packet expired on 2026-07-30. WI-5408 has no current
implementation-start packet, and its earlier draft claim is expired. These
facts remove the old active collision but do not waive the required fresh
operation-time collision check after a new independent GO.

### Current defect

The clean source still implements a second PAUTH-amendment parser/validator in
`_pauth_amendment_blocking_errors()` instead of delegating to the canonical
`validate_structured_pauth_spec_amendment()` function in
`scripts/implementation_authorization.py`. The duplicate path:

- treats literal mention of the PAUTH-amendment approval DCL plus any unrelated
  JSON object as a structured replacement envelope;
- falsely rejects a proposal with no real PAUTH amendment;
- duplicates owner-packet schema, identity, and coverage logic;
- computes current authorization specs through a separate read path; and
- embeds a local two-second SQLite wait in that duplicate read path.

A fresh preflight against version 001 reproduced both live blockers:

1. false amendment classification: `No packet path detected in owner evidence`;
2. the version-001 citation to the retired `...20260715-PROJECT-SCOPE`
   authorization, which is corrected to the current active authorization in
   this revision.

The complete focused preflight module currently passes (`43 passed in 1.13s`),
showing that its tests encode the duplicate implementation but omit the
known unrelated-JSON false-positive case. The canonical validator/backstop
selection remains healthy (`9 passed in 1.39s`).

## Requirement Sufficiency

Existing requirements are sufficient. Version 001 remains the full original
specification carrier, including the exact machine-readable ID of the
PAUTH-amendment approval design constraint. This revision deliberately refers
to that one ID descriptively rather than repeating its hyphenated spelling:
the current defect is a literal whole-document string trigger that would make
this corrective proposal fail its own preflight before the repair can be
reviewed. Versions 004 and 005 independently documented and accepted this
one-thread self-deadlock handling. The omission is not a waiver, amendment, or
claim that the constraint is inapplicable; its exact citation remains durable
in version 001 and governs the implementation and verification plan below.

No new specification or project-authorization amendment is proposed.

## Proposed Scope

1. Replace the parallel PAUTH-amendment parsing/validation path in
   `scripts/bridge_applicability_preflight.py` with a thin adapter around the
   canonical `validate_structured_pauth_spec_amendment(project_root, content)`
   function and canonical `AuthorizationError` diagnostics.
2. Preserve the existing `blocking_errors` packet field and fail-closed
   formatting. A real malformed, identity-conflicting, owner-evidence-missing,
   out-of-root, non-owner, or non-covering amendment must still produce one
   deterministic blocking error.
3. Treat content with no actual structured replacement envelope as
   non-applicable even when it cites the governing amendment constraint and
   carries unrelated JSON evidence.
4. Remove only the now-obsolete duplicate helpers/constants/tests owned by the
   parallel validator. Preserve WI-5403's `declared_target_paths` and
   `applicability_path_evidence` behavior and every unrelated operative-version,
   PAUTH operation-time, hashing, warning, and formatting behavior.
5. Remove the duplicate validator's local SQLite read/wait rather than adding a
   new hard-coded timer. Timer/concurrency centralization remains governed by
   the existing Timer Governance project and its inventory/externalization
   work; this proposal creates no duplicate timer WI.
6. Change only the two declared target paths. Do not mutate MemBase,
   dispatcher, TAFE, runtime leases beyond the required work-intent claim, Git
   history, credentials, deployment, release, or external systems.

## Specification Links

- The exact PAUTH-amendment approval design-constraint ID is carried forward from version 001; see `Requirement Sufficiency` for the documented self-deadlock exception to repeating its literal spelling in this revision.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — preserves role-correct append-only bridge continuation and independent review.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — corrects version 006's invalid closure interpretation through a fresh strict controller.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — preserves the complete original specification carrier and supplies a current spec-derived plan.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — keeps terminal verification conditional on executed tests derived from the linked constraints.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — supplies the current active PAUTH, active project, member WI, and exact target paths.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — makes active project authorization controlling without bypassing GO or operation-time gates.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — requires a fresh claim and implementation-start evaluation after GO.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` — preserves the WI-5403 shared-file behavior and requires a fresh collision check.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — requires preservation of unrelated applicability behavior and explicit before/after evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — preserves the defect, correction, tests, and independent verdict as durable artifacts.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — keeps proposal, code, tests, report, and verification traceable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — records the malformed predecessor quarantine and lawful fresh proposal rather than false closure.
- `GOV-STANDING-BACKLOG-001` — keeps WI-5408 and the current project membership visible in the MemBase backlog.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — keeps both platform targets inside the mandatory GT-KB root.
- `SPEC-AUQ-POLICY-ENGINE-001` — preserves the owner-decision evidence path while correctly avoiding a redundant AUQ.

## Prior Deliberations

- `DELIB-202667044` — harvested independent corrected-GO investigation reproducing the false positive, tracing the duplicate validator, and selecting canonical delegation.
- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` — owner authorization for the active parent project under the normal bridge and implementation-start gates.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` — individual WI approval state is not operational authority.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — every member WI inherits active authorized parent-project authority; orphan WIs remain ineligible.
- `DELIB-202667719` — where a list-free grant exists it is controlling; the Authority Foundations project now has such a grant.
- `bridge/gtkb-wi5408-pauth-amendment-owner-evidence-applicability-001.md` through `-007.md` — complete proposal, review, correction, stale-disposition, and current NO-GO history.
- `bridge/gtkb-wi5403-declared-applicability-target-scope-004.md` and `-012.md` — independent duplicate-validator rejection and current finalization-only blocker context.
- `bridge/gtkb-wi5346-restore-wi5254-pauth-amendment-preflight-001.md` through `-009.md` — canonical validator recovery and later bridge-state context.

## Owner Decisions / Input

- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` authorizes the bounded parent project subject to all unchanged implementation gates.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` makes that active parent-project authorization the controlling implementation-approval evidence for member WI-5408.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` makes the legacy WI `approval_state` field non-authoritative.
- `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715` is the current active, unexpired, list-free project authorization.

No new owner decision is requested or inferred. This revision stays within the
already-approved project scope and does not amend the authorization.

## Intuitiveness / Non-Impairment Disposition

```json
{
  "after_behavior": "applicability preflight delegates actual structured PAUTH-amendment validation to the canonical validator and ignores unrelated JSON evidence",
  "applicability": "applicable",
  "baseline": {
    "canonical_validator": "9 passed in 1.39s",
    "focused_applicability_preflight": "43 passed in 1.13s while omitting the known unrelated-JSON false-positive regression"
  },
  "before_behavior": "a duplicate whole-document literal trigger mistakes unrelated JSON for a PAUTH amendment and requires owner evidence for a nonexistent amendment",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 plus the exact PAUTH-amendment approval constraint carried by version 001",
  "essential_context_preservation": "preserve WI-5403 declared-target/applicability-evidence separation, operative-version resolution, conservative spec applicability, packet hashing, warnings, and operation-time PAUTH evaluation",
  "expected_result": {
    "canonical_validator": "all focused canonical amendment tests pass",
    "focused_applicability_preflight": "all tests pass including the unrelated-JSON false-positive regression"
  },
  "fail_closed_conditions": [
    "real amendment with malformed structured envelope",
    "project or authorization identity conflict",
    "real spec delta without valid owner evidence",
    "no approval-packet mutation; reject out-of-root, malformed, non-owner, or non-covering evidence",
    "target drift or peer collision before implementation start"
  ],
  "hard_invariants": [
    "do not consume an implementation claim during applicability preflight",
    "do not mutate dispatcher or TAFE",
    "do not alter WI-5403 declared-target/applicability-evidence behavior",
    "do not introduce a new local hard-coded timer"
  ],
  "history_preservation": "retain all numbered bridge files and distinguish the committed clean baseline from its earlier dirty-byte provenance",
  "obsolete_guidance_disposition": "version 006 idle-GO closure language and version 007 WI approval_state gating are historical evidence, not current authority",
  "primary_route": "thin bridge-applicability adapter over the canonical implementation-authorization validator",
  "provenance": "WI-5408 versions 001-007, DELIB-202667044, and fresh 2026-08-01 CLI/test/current-byte re-derivation",
  "rollback": {
    "instructions": "revert only WI-5408-owned hunks in the two declared targets while preserving WI-5403 behavior",
    "test": "rerun the focused applicability and canonical-validator commands"
  },
  "schema_version": 1,
  "self_descriptive_naming": "retain blocking_errors and use canonical structured-PAUTH-amendment terminology"
}
```

## Specification-Derived Verification Plan

| Governing surface | Verification |
| --- | --- |
| PAUTH-amendment approval constraint carried by version 001 | Add and execute cases for no real envelope plus unrelated JSON, no-delta real envelope, missing evidence for real delta, malformed lists, identity conflict, out-of-root/malformed/non-owner/non-covering evidence, and multiple envelopes. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Run the complete focused preflight module and assert WI-5403 declared/applicability path fields and all existing unrelated cases remain unchanged. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; operation-time enforcement | After independent GO, acquire a fresh claim and run `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5408-pauth-amendment-owner-evidence-applicability`; confirm the current active list-free PAUTH and exact two-target cohort. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; bridge authority | Run applicability and clause preflights against the completed revision and implementation report; require no missing specs or blocking gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Carry this mapping, exact commands, and observed results into the implementation report before independent verification. |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Recompute target hashes, `git status`, active claims, and non-expired implementation packets immediately before mutation; stop on target drift or collision. |
| Timer Governance owner direction | Confirm the obsolete duplicate helper and its local two-second wait are removed; do not add a replacement literal timer. Existing centralized Timer Governance WIs remain the non-duplicative follow-on authority. |

Planned commands:

```text
python -m pytest platform_tests/scripts/test_bridge_applicability_preflight.py -q --tb=short
python -m pytest platform_tests/scripts/test_implementation_authorization.py -k "structured_pauth_amendment or backstops_structured_pauth_amendment" -q --tb=short
python -m ruff check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py
python -m ruff format --check scripts/bridge_applicability_preflight.py platform_tests/scripts/test_bridge_applicability_preflight.py
python scripts/bridge_applicability_preflight.py --content-file bridge/gtkb-wi5408-pauth-amendment-owner-evidence-strict-recovery-001.md --json
python scripts/adr_dcl_clause_preflight.py --content-file bridge/gtkb-wi5408-pauth-amendment-owner-evidence-strict-recovery-001.md
```

At implementation-report time, rerun the same two preflights against the exact
new numbered report path before filing it.

The repository-wide pytest timeout observed during focused evidence collection
is already tracked under WI-5873 and the active Timer Governance project. Both
focused commands completed in under two seconds, so this audit supplies no new
evidence that requires a duplicate timer WI.

## Acceptance Criteria

1. Content with no actual structured PAUTH replacement envelope yields no
   amendment blocking error even when the governing constraint is cited and
   unrelated JSON evidence exists.
2. Real structured amendments are validated by the canonical function; every
   canonical fail-closed class remains a deterministic `blocking_errors`
   diagnostic.
3. No duplicate approval-packet schema, spec-delta, project-identity, coverage,
   or owner-evidence implementation remains in the applicability preflight.
4. WI-5403's `declared_target_paths` and `applicability_path_evidence` behavior
   remains intact and covered by the complete focused test module.
5. No replacement hard-coded timer is added; removal of the obsolete local
   SQLite wait is verified by the diff.
6. Both target files match their recorded preimages at implementation start or
   implementation stops for collision/currentness re-evaluation.
7. Applicability and clause preflights pass for the completed proposal/report,
   all planned tests pass, Ruff lint passes, and Ruff format check passes.

## Risks / Rollback

Risk is moderate because applicability preflight participates in bridge review
and implementation-start evidence. The main regression risk is accidentally
turning a real amendment into a no-op or disturbing WI-5403's shared-file
behavior. Canonical-validator delegation, complete fail-closed test coverage,
the clean preimage boundary, and a fresh operation-time collision check contain
that risk.

Rollback reverts only the WI-5408-owned source/test hunks and reruns both
focused modules. Numbered bridge history, project records, and deliberations
remain append-only. No dispatcher/TAFE action is part of implementation or
rollback.

## Files Expected To Change

- `scripts/bridge_applicability_preflight.py`
- `platform_tests/scripts/test_bridge_applicability_preflight.py`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
