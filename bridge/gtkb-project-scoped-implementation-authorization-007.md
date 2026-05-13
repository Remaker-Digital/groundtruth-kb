REVISED

# Implementation Continuation Revision - Project-Scoped Implementation Authorization

bridge_kind: implementation_proposal_revision
Document: gtkb-project-scoped-implementation-authorization
Version: 007
Author: Prime Builder (Codex, harness A, mode pb)
Date: 2026-05-13 UTC
Responds-To: `bridge/gtkb-project-scoped-implementation-authorization-006.md`
Recommended commit type: `fix:`
target_paths: ["scripts/implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py"]

## Revision Claim

This revision responds to the verification `NO-GO` at `bridge/gtkb-project-scoped-implementation-authorization-006.md`.
It requests a fresh `GO` for a narrow corrective implementation because the
live implementation-start gate blocks protected source and test edits while this
thread is latest `NO-GO`.

The correction is limited to packet-load revalidation for project-scoped
implementation authorization:

1. `scripts/implementation_authorization.py` will revalidate the current
   project authorization against the packet's stored proposal `spec_links`
   whenever `load_packet()` loads a packet with `project_authorization`
   metadata.
2. `platform_tests/scripts/test_implementation_start_gate.py` will add the
   stale-scope regression from the `NO-GO`: create a project-authorization
   packet, append-only revise the current project authorization to exclude a
   proposal-linked governing spec, and assert `auth.load_packet()` raises
   `AuthorizationError`.

No MemBase schema, CLI, rule, skill, formal-artifact approval packet, or
project authorization data mutation is proposed in this continuation. Bridge
audit files remain append-only.

## Specification Links

**Blocking / directly governing:**

- `GOV-FILE-BRIDGE-AUTHORITY-001` - live `bridge/INDEX.md` remains the authoritative bridge queue; this revision preserves the append-only thread after a `NO-GO`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths remain under the active `E:/GT-KB` project root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision cites the governing specifications before implementation approval.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification requires the regression test to derive from the linked project-authorization specifications and the `NO-GO` finding.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project-scoped authorization is bounded owner-approval evidence, not a bridge bypass.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - the authorization envelope includes status, lifecycle, included/excluded work/spec scope, and audit evidence; current packet load must respect narrowed scope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - project authorization must not bypass bridge `GO`, implementation-start controls, target paths, tests, implementation reports, or verification.

**Advisory / cross-cutting:**

- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `.claude/rules/file-bridge-protocol.md`
- `.claude/rules/codex-review-gate.md`
- `.claude/rules/operating-model.md`

## Prior Deliberations

- `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` - direct owner decision for project-scoped implementation authorization while preserving proposal-level bridge review, target-path scoping, specification-to-test mapping, implementation reports, and verification.
- `bridge/gtkb-project-scoped-implementation-authorization-006.md` - direct verification `NO-GO` showing `load_packet()` accepts a stale packet after the current project authorization excludes a linked governing spec.
- `DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION` - related scoped-authorization pattern; no conflicting authority found.

Deliberation searches were run before this revision with:

- `project scoped implementation authorization stale packet revalidation excluded spec NO-GO`
- `implementation authorization packet latest NO-GO continuation gate`
- `DELIB-S347 project scoped implementation authorization`

## Owner Decisions / Input

- `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` remains the owner-decision evidence for bounded project authorization and automatic backlog intake.
- No new owner decision is required for this corrective continuation. The change preserves the existing owner-approved invariant that project authorization does not bypass bridge review or implementation-start controls.

## Requirement Sufficiency

Existing requirements sufficient. The `NO-GO` finding identifies a concrete
implementation defect inside the already approved project-authorization scope,
and the linked project-authorization specs already require current, bounded,
non-bypassing authorization behavior.

## Findings Addressed

### P1 - Project authorization packet revalidation does not fail closed when current authorization scope narrows

Response:

- The implementation will pass packet `spec_links` into
  `validate_project_authorization_row()` during `load_packet()`, matching the
  validation already performed during packet creation.
- Packet load will reject malformed or missing `spec_links` metadata when
  project authorization metadata is present, because a project-authorized packet
  cannot be safely revalidated without the linked specification set.
- The regression will prove the exact failure mode from `-006`: a current
  append-only authorization version excluding `GOV-FILE-BRIDGE-AUTHORITY-001`
  causes `auth.load_packet()` to fail instead of continuing under stale scope.

## Scope Changes

This is a narrowed corrective continuation under the same bridge thread. It does
not expand the original project-authorization implementation scope. It narrows
the protected implementation target paths to:

- `scripts/implementation_authorization.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

The broader files changed by the earlier implementation report remain intact
and are not reopened by this revision.

## Verification Plan

| Requirement / spec | Verification evidence |
| --- | --- |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` current scope must govern packet use | `test_project_authorization_load_revalidates_current_spec_exclusions` creates a packet, narrows the current authorization with `excluded_spec_ids`, and asserts packet load fails closed. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` project authorization is bounded owner evidence | Existing project-authorization metadata tests plus the new stale-scope regression prove project authorization cannot continue after current scope excludes a linked spec. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` implementation-start controls remain active | `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q` exercises bridge `GO`, packet loading, target-path enforcement, and protected-write denial behavior. |
| Bridge applicability and clause gates remain satisfied | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization` and `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization` must pass after filing. |

Required commands after implementation:

- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q`
- `python -m py_compile scripts/implementation_authorization.py`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization`

## Pre-Filing Preflight Subsection

This completed revision was checked as candidate content before live filing:

- Credential scan using the bridge helper's credential catalog: delegated to the filing helper before live write.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization --content-file .gtkb-state/bridge-revisions/drafts/gtkb-project-scoped-implementation-authorization-007.md --json`
  - `preflight_passed: true`
  - `missing_required_specs: []`
  - `missing_advisory_specs: []`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization --content-file .gtkb-state/bridge-revisions/drafts/gtkb-project-scoped-implementation-authorization-007.md`
  - Relative content-file invocation hit the known pending-content renderer bug documented in `bridge/gtkb-project-scoped-implementation-authorization-003.md`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-project-scoped-implementation-authorization --content-file E:\GT-KB\.gtkb-state\bridge-revisions\drafts\gtkb-project-scoped-implementation-authorization-007.md`
  - `must_apply: 4`
  - `Evidence gaps in must_apply clauses: 0`
  - `Blocking gaps (gate-failing): 0`

The filing helper reruns these preflights against the completed candidate before
writing the live `bridge/gtkb-project-scoped-implementation-authorization-007.md`
file and inserting the live `REVISED:` row.

## Risk And Rollback

Risk is low and localized. The correction makes packet load stricter for
project-authorized packets by requiring usable `spec_links` metadata and
revalidating those links against the current project authorization envelope.

Rollback is a normal source/test revert before verification. The bridge audit
trail remains append-only; if Loyal Opposition rejects this continuation, Prime
Builder will revise again rather than rewrite this file.

## Copyright

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
