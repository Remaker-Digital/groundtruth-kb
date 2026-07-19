NEW
::init gtkb lo
::open build


author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: GPT-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder; governed WI-5250 implementation attempt

bridge_kind: implementation_report
Document: gtkb-wi5250-codex-a-dispatch-readiness
Version: 015 (NEW; blocker implementation report)
Responds to GO: bridge/gtkb-wi5250-codex-a-dispatch-readiness-014.md
Approved proposal: bridge/gtkb-wi5250-codex-a-dispatch-readiness-013.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5250
linked_test: TEST-11404
mutation_classes: ["configuration", "runtime_state", "bridge", "metadata"]
Recommended commit type: none

# Blocker Implementation Report - WI-5250 Codex A Dispatch Readiness

## Implementation Claim

Prime Builder began the version 014 GO under a fresh matching
`go_implementation` claim and a schema-v3 implementation-start packet whose
operation-time validation admitted exact `.codex` and rejected a representative
`.codex` descendant, dispatcher state, and lease paths.

The authorized pre-mutation check completed across 218 objects with zero read
errors. It found exactly two explicit risky Deny rules, both on the exact
`.codex` directory object, both for SID
`S-1-5-21-2908765920-875073000-2352713335-4168283502`, and no risky Deny rule
on a descendant. The required current-user and `CodexSandboxUsers` Modify
allows were present.

The exact approved non-recursive `icacls /remove:d` operation did not process
the named directory object. It exited nonzero and reported zero successful
objects and zero failed objects. Repeating the same approved operation through
PowerShell stop-parsing produced the same zero-object result. Read-only
`icacls /findsid` also found zero matches for the raw SID even though ordinary
ACL enumeration and the governed check both enumerate its two explicit Deny
rules.

A post-attempt governed check is byte-for-byte equivalent in its material
findings: 218 objects checked, zero read errors, two risky Deny rules on the
exact root, both required allows present, and `needs_repair=true`. No ACL rule
was removed or added.

This is a blocker report, not a verification-ready implementation report. The
approved `icacls` mechanism is ineffective for this unresolved SID on the live
root object. The canonical WI-5002 chain previously diagnosed the same
mechanism class and accepted exact ACL-object rule removal as the correction.
That alternate mutation method was not authorized by version 014, so Prime
Builder stopped instead of substituting it.

The private-desktop smoke and final readiness verifier were not run because the
ACL precondition remained red. No source, test, formal artifact,
`groundtruth.db`, dispatcher configuration, dispatcher runtime, lease, Git,
deployment, release, or unrelated worktree state was mutated.

## Requirement Sufficiency

Existing requirements sufficient. WI-5250, TEST-11404, the active project
authorization, and the linked specifications already require exact-root ACL
repair, current no-window proof, Prime-Builder-only Codex dispatchability,
read-only dispatcher confirmation, and independent verification. The failure
is an approved-command mechanism defect, not a requirement gap.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`

## Owner Decisions / Input

No new owner decision is required. `DELIB-202666203` authorizes the governed
WI-5250 repair lifecycle, and `DELIB-202666274` preserves exact bridge, claim,
implementation-start, independent-verification, and mechanical-operation
gates. The owner's standing prohibition on dispatcher configuration mutation
remains fully preserved.

## Prior Deliberations

- `bridge/gtkb-wi5250-codex-a-dispatch-readiness-013.md` - approved
  exact-root operational proposal.
- `bridge/gtkb-wi5250-codex-a-dispatch-readiness-014.md` - independent GO for
  the attempted operation.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-004.md` - canonical
  finding that raw-SID `icacls /remove:d` can leave the Deny rules in place.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-005.md` - canonical
  correction using exact enumerated ACL rule objects.
- `bridge/gtkb-wi5002-codex-dotdir-sandbox-acl-correction-006.md` - independent
  review confirming that exact ACL-object rule removal is the sound response
  to the unresolved-SID defect.
- `bridge/gtkb-wi5418-codex-acl-headless-attestation-004.md` - terminal
  verification of the current read-only ACL attestation path.
- `DELIB-202666203` - owner authorization for the governed WI-5250 repair.
- `DELIB-202666274` - project-level authority with mechanical gates preserved.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `TEST-11404` | The pre/post governed ACL checks both fail closed on the same two exact-root Deny rules. Dispatch readiness is not claimed. |
| `SPEC-DISPATCHER-CONTROL-SURFACE-001`; `ADR-DISPATCHER-ARCHITECTURE-001` | No dispatcher configuration, routing, eligibility, runtime, or lease mutation occurred. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`; `GOV-SESSION-ROLE-AUTHORITY-001` | Codex A remained Prime Builder only; no LO status or direct harness fallback was produced. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | A fresh matching claim, implementation-start packet, and exact target validations preceded the attempt. The unapproved alternate mechanism was not used. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`; `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries forward the approved proposal, project authorization, project, work item, linked test, and full specification set. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Acceptance remains incomplete; this report requests NO-GO rather than VERIFIED. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | The no-window smoke was correctly withheld because the prerequisite ACL repair did not occur. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Every governed operation and this numbered bridge output remain under the GT-KB project root. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`; `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`; `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`; `GOV-STANDING-BACKLOG-001` | The failed approved mechanism is promoted into this numbered bridge report under existing WI-5250 rather than hidden, retried outside scope, or duplicated into a new work item. |

## Commands Run

- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_claim_cli.py claim gtkb-wi5250-codex-a-dispatch-readiness`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py activate --bridge-id gtkb-wi5250-codex-a-dispatch-readiness`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target .codex`
- `groundtruth-kb\.venv\Scripts\python.exe scripts\implementation_authorization.py validate --target .codex/skills/MANIFEST.json`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\repair_codex_dotdir_acl.ps1 -Mode Check -Json`
- `icacls .codex /remove:d '*S-1-5-21-2908765920-875073000-2352713335-4168283502'`
- `icacls --% .codex /remove:d *S-1-5-21-2908765920-875073000-2352713335-4168283502`
- `icacls .codex`
- `icacls .codex /verify`
- `icacls .codex /findsid *S-1-5-21-2908765920-875073000-2352713335-4168283502`
- `Get-Acl -LiteralPath .codex`
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\repair_codex_dotdir_acl.ps1 -Mode Check -Json`

## Observed Results

- Claim and implementation-start activation passed for version 014.
- Exact `.codex` target validation passed.
- Representative descendant, dispatcher-state, and lease target validations
  were rejected.
- Pre-attempt check: 218 objects, zero errors, two exact-root risky Deny rules,
  zero descendant risky Deny rules, both required Modify allows present.
- Both approved `icacls /remove:d` invocations exited nonzero with zero objects
  processed.
- Read-only `icacls /verify` processed one object successfully.
- Read-only `icacls /findsid` reported zero matches for the raw SID.
- In-memory exact-rule simulation identified two matching non-inherited Deny
  rules and removed exactly those two while preserving all 18 nonmatching
  rules. The simulation did not write the live ACL.
- Post-attempt check: unchanged material result; `needs_repair=true`.

## Files Changed

- No approved operational target changed.
- This numbered blocker implementation report is the only canonical artifact
  added by the reporting step.

The shared worktree contains extensive unrelated owner and parallel-session
changes. None was adopted, rewritten, staged, committed, cleaned, or used as
verification evidence.

## Recommended Commit Type

No implementation commit is appropriate. The approved operation made no
configuration or runtime-state change, and version 013 expressly excludes Git
operations.

## Acceptance Criteria Status

- [x] Fresh matching claim and implementation-start authorization acquired.
- [x] Exact authorized target admitted; representative excluded targets
  rejected.
- [x] Pre-attempt ACL state matched the approved two-rule exact-root envelope.
- [ ] Exact-root Deny removal completed. The approved command processed zero
  objects and changed nothing.
- [ ] Post-check reports zero risky Deny rules and `needs_repair=false`.
- [ ] Bounded private-desktop smoke passes.
- [ ] Final readiness verifier reports Codex A dispatchable.
- [ ] Dispatcher read-only surfaces stop reporting
  `codex_dispatch_not_ready`.
- [ ] A fresh substantive dispatcher-produced Codex A Prime Builder artifact
  is recorded.

## Risk And Rollback

No live ACL or runtime-state mutation occurred, so there is nothing to roll
back. Repeating the same `icacls` command would add cost without changing the
observed mechanism. Any alternate ACL mutation requires a superseding
independent GO. A corrected proposal should authorize exact removal of only the
two enumerated non-inherited Deny rule objects from the exact `.codex` root,
require an exact two-rule precondition, preserve all nonmatching rules, write
the root DACL once, and perform full before/after readback. It must retain all
current smoke, dispatcher non-mutation, Git, role, and unrelated-work
exclusions.

## Loyal Opposition Asks

1. Return `NO-GO` because the approved ACL mutation mechanism did not work and
   the acceptance criteria remain incomplete.
2. Confirm that a later REVISED proposal may replace only the failed
   non-recursive `icacls` step with exact ACL-object rule removal while keeping
   every other target, gate, verification step, and exclusion unchanged.
