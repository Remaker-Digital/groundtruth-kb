NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: dbc5c1cd-13f2-4ff8-81a5-a80c06799bae
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal
Document: gtkb-wi5677-begin-report-nogo-recommit-authorization
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5677

target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_authorization.py"]

# Defect-Fix Proposal — begin must support commit-under-existing-GO after a report-level NO-GO

## Claim

`implementation_authorization.py begin` fails closed when a bridge thread's
latest status is a report-level `NO-GO`, even when the same thread carries a
prior live `GO` for the same target scope. This makes the remediation that a
Loyal Opposition report-`NO-GO` itself directs — "commit under the existing GO,
then file a revised report" — mechanically unreachable.

## Defect / Reproduction

Observed session dbc5c1cd (2026-07-24) on thread
`gtkb-wi5668-sweep-completion-gate` (chain: `001 NEW`, `002 GO`, `003 NEW`
implementation report, `004 NO-GO`).

1. A Prime Builder work-intent claim was acquired successfully
   (`acting_role: prime-builder`, `claim_kind: draft`).
2. `python scripts/implementation_authorization.py begin --bridge-id gtkb-wi5668-sweep-completion-gate`
   returned exit 2:

       {"authorized": false, "error": "Bridge 'gtkb-wi5668-sweep-completion-gate'
       does not have a GO-implementation claim or project_authorization_bootstrap
       claim"}

3. A GO-implementation claim requires latest status = `GO`. The thread's latest
   is `NO-GO` (`004`), so no packet can be issued.

The `004` NO-GO's own Required Action reads: "Prime Builder must isolate, stage,
and commit the approved function, its registration line, and the net-new test
under the existing GO; then file a revised implementation report with the exact
commit SHA." The authorization layer cannot express that state, so the thread
stalls or invites an ungoverned commit outside any authorization packet.

## Proposed Scope

Permit a GO-implementation authorization packet when ALL of the following hold:

1. The thread's latest status is a report-level `NO-GO` (a `NO-GO` responding to
   an implementation report, not to a proposal).
2. The same thread carries a prior `GO` whose approved `target_paths` are a
   superset of the requested implementation scope.
3. The issued packet is scoped to those prior-GO `target_paths` only — it must
   NOT widen scope.

The packet must record the originating `GO` version and the report-`NO-GO`
version it is remediating, so the audit trail shows exactly which approval the
commit runs under. Proposal-level `NO-GO` (a `NO-GO` responding to a `NEW`/
`REVISED` proposal with no prior GO) must continue to fail closed — that state
has no approval to commit under.

Exact predicate placement and helper naming are left to implementation within
these constraints; no change to the claim CLI, the resolver, or the protected-
commit checker is proposed.

## In-Root Placement Evidence

Both target paths are inside `E:\GT-KB`: `scripts/implementation_authorization.py`,
`platform_tests/scripts/test_implementation_authorization.py`.

## Domain-Ownership Note (for reviewer judgment)

The session's standing rules assign the bridge-runtime finalizer/checker/resolver
stack to Codex, naming `scripts/bridge_lifecycle_resolver.py` and
`scripts/check_protected_commit_authorization.py`. Neither file is in this
proposal's target set, but `scripts/implementation_authorization.py` is adjacent
to that stack in spirit. This is surfaced deliberately so the reviewing role can
decide whether to `GO` here or reassign the fix to Codex ownership.

No file collision exists with the concurrently-approved `WI-5670`
(`gtkb-wi5670-resolver-legacy-provenance-tolerance`, latest `GO`), whose
`target_paths` are `scripts/bridge_lifecycle_resolver.py` and
`platform_tests/scripts/test_bridge_lifecycle_resolver.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge authority and the GO/NO-GO discipline this fix must preserve.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied by the verification plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied by the project-linkage triple above.
- `GOV-RELIABILITY-FAST-LANE-001` — fast-lane eligibility basis for this bounded defect fix.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable capture of the defect and its remedy.

## Prior Deliberations

- `DELIB-202667470` — owner authorization to implement WI-5677.
- `DELIB-202666312` — inter-harness isolation restriction; per-access owner approval supplied by `DELIB-202667470`.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — standing reliability fast-lane authorization basis.
- `DELIB-202666252` — WI-5249 Prime NO-ACTION claim/filer (adjacent claim-mechanics precedent).
- `DELIB-202665620` — WI-4853 session-role marker claim eligibility (adjacent claim-eligibility precedent).
- Source advisory: `bridge/gtkb-wi5677-begin-commit-after-report-nogo-gap-001.md` (ADVISORY).

## Owner Decisions / Input

- `DELIB-202667470` (owner authorization, 2026-07-24): "I authorize these: WI-5676, WI-5677, WI-5678. Please proceed with implementation." Authorization permits autonomous progress through the bridge protocol; it does not waive LO `GO`, the implementation-start packet, the report, or `VERIFIED`.
- Reviewer decision requested: whether this fix should proceed here or be reassigned to Codex per the domain-ownership note above.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` already
establishes that a `GO` authorizes implementation of its approved scope and that
implementation requires a current authorization packet. This fix makes the
authorization layer able to express an approval state the protocol already
contemplates (remediating a report-level `NO-GO` under the thread's existing
`GO`). It narrows an over-broad refusal rather than granting new authority, so
no new or revised requirement is needed before implementation.

## Specification-Derived Verification Plan

| Requirement (linked spec) | Test / command | Expected |
| --- | --- | --- |
| Report-NO-GO over prior GO authorizes (`GOV-FILE-BRIDGE-AUTHORITY-001`) | new test: chain `NEW, GO, report NEW, NO-GO` → `begin` | packet issued, scoped to prior-GO target_paths |
| Scope never widens (`GOV-FILE-BRIDGE-AUTHORITY-001`) | new test: request path outside prior-GO target_paths | refused |
| Proposal-NO-GO still fails closed (`GOV-FILE-BRIDGE-AUTHORITY-001`) | new test: chain `NEW, NO-GO` (no prior GO) → `begin` | refused (unchanged) |
| Normal latest-GO path unaffected | existing begin tests | unchanged, pass |
| Audit trail records provenance | new test asserts packet records originating GO version + remediated NO-GO version | present |
| No regression | `python -m pytest platform_tests/scripts/test_implementation_authorization.py -q` | all pass |
| Code quality | `ruff check` AND `ruff format --check` on both target paths | pass |

## Acceptance Criteria

- `begin` issues a correctly-scoped packet for a report-`NO-GO`-over-`GO` thread.
- Proposal-level `NO-GO` with no prior `GO` still fails closed.
- Issued packet cannot exceed the prior `GO`'s approved `target_paths`.
- Focused suite passes; ruff check and ruff format --check both pass.
- Scoped commit contains only the two declared target paths.

## Risks / Rollback

Risk: loosening `begin` could authorize a commit the reviewer did not intend.
Mitigated by requiring a prior `GO` on the same thread, clamping scope to that
`GO`'s `target_paths`, preserving fail-closed behavior for proposal-level
`NO-GO`, and recording both version references in the packet. Rollback: revert
the scoped commit; `begin` returns to current fail-closed behavior.

## Recommended Commit Type

Recommended commit type: `fix`
