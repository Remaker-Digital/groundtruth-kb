REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6bf6-3e6d-7761-be14-fb894a0e84d2
author_model: gpt-5.5
author_model_version: gpt-5.5
author_model_configuration: OpenAI Codex desktop interactive; reasoning=xhigh; approval_policy=never

# Revised Defect-Fix Proposal - Restore Codex A Effective Workspace Capability

bridge_kind: prime_proposal
Document: gtkb-wi5310-codex-effective-workspace-profile
Version: 005
Responds to: bridge/gtkb-wi5310-codex-effective-workspace-profile-004.md
Date: 2026-07-16 UTC

Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5310-CODEX-PERMISSION-PROFILE-V2-20260716
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5310

target_paths: ["harness-state/harness-registry.json", "scripts/codex_no_window_smoke_probe.py", "scripts/verify_codex_dispatch.py", "platform_tests/scripts/test_codex_no_window_smoke_probe.py", "platform_tests/scripts/test_verify_codex_dispatch.py"]

implementation_scope: configuration, runtime_state, source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

## Revision Claim

This revision preserves the five-path technical design from version 001 and
corrects the authorization defect confirmed by versions 003 and 004. The new
V2 PAUTH is active, includes the `runtime_state` mutation class required for
`harness-state/harness-registry.json`, and remains bounded to WI-5310, the same
five paths, and the original forbidden operations.

The implementation will restore a genuinely write-capable, headless Codex A
Prime Builder worker. Static argv text or a successful read-only command is not
sufficient evidence. Readiness must be proven by the actual `codex exec`
invocation using `-c default_permissions=\":workspace\"`, an in-root
create/read/remove sentinel lifecycle, private-desktop containment with zero
visible windows, and one substantive dispatcher-produced governed A/PB bridge
artifact.

No implementation begins under this revision until a fresh independent GO,
matching `go_implementation` claim, and successful implementation-start packet
exist for version 005.

## Requirement Sufficiency

Existing requirements remain sufficient. WI-5310 corrects an implementation
and verification defect against the centralized dispatcher, harness onboarding,
Codex parity fallback, bridge authority, and project-authorization contracts.
It creates no new product or governance requirement.

## In-Root Placement Evidence

Every target is inside `E:\GT-KB`: `harness-state/harness-registry.json`,
`scripts/codex_no_window_smoke_probe.py`, `scripts/verify_codex_dispatch.py`,
`platform_tests/scripts/test_codex_no_window_smoke_probe.py`, and
`platform_tests/scripts/test_verify_codex_dispatch.py`.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - readiness must describe the
  effective headless worker, not only its configured argv.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - an active PB harness must execute its
  declared governed write surface.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - native Windows Codex must preserve the
  governed boundary when native hook support differs.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - proposal, GO, claim, start, report, and
  independent verdict remain mandatory.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the V2 PAUTH is the bounded
  implementation envelope.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` - operation-time
  authorization must pass before target mutation.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` - allowed mutation classes and
  forbidden operations remain explicit.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - bridge GO cannot bypass
  project authorization or target-path ownership.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision
  carries all applicable requirements.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - terminal verification
  requires mapped automated and real-dispatch evidence.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, work item,
  PAUTH, and exact target paths are machine-readable.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - targets and sentinel remain
  inside the GT-KB project root.
- `GOV-STANDING-BACKLOG-001` - WI-5310 and TEST-11453 preserve the defect and
  regression contract.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - transient runtime evidence is
  promoted into durable WI, bridge, test, report, verdict, and commit evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - implementation evidence remains
  durable and independently reviewable.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the ordinary governed lifecycle is
  preserved.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` - version 005 carries explicit author,
  harness, session, model, and configuration provenance.

## Prior Deliberations

- `DELIB-202665713` - WI-4985 Codex headless write-boundary VERIFIED lineage.
- `DELIB-202665293` - prior independent evidence that nominal workspace-write
  configuration can still fail at the effective sandbox identity.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authority
  for the bounded WI-5310 repair and corrected V2 PAUTH.
- Version 001 proposed the five-path repair; version 002 issued conditional GO;
  version 003 rejected that GO after the operation-time PAUTH denial; version
  004 independently confirmed the missing `runtime_state` class and required a
  substantive revision after correction.
- WI-5308 remains dependency-blocked until WI-5310 proves a correct effective
  profile; it must not renew the old false-positive proof contract.

## Owner Decisions / Input

- Mike directed: "Codex must be restored to a fully dispatchable state in which
  headless PB workers are spawned on demand."
- Mike requires functional, budgeted harnesses to remain dispatchable; the
  console-window defect must be repaired without disabling Codex or the bridge.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` permits this
  bounded carrier but does not waive GO, claim, implementation-start, testing,
  independent verification, or focused-commit gates.
- The original PAUTH has been revoked. Active V2 PAUTH
  `PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-WI5310-CODEX-PERMISSION-PROFILE-V2-20260716`
  adds only the required `runtime_state` class while preserving the exact
  five-path scope and prohibitions.

## Findings Addressed

### F1 (P0, blocking) - Insufficient Project Authorization Class Coverage

Response: corrected. Canonical `gt projects show-authorization` readback shows
the V2 PAUTH is active and allows `bridge`, `metadata`, `configuration`,
`runtime_state`, `source`, and `test`. Its scope names WI-5310 and the same five
targets. It forbids credential lifecycle, destructive cleanup, dispatcher
mutation, external mutation, Git history rewrite, push, production deployment,
and release. The superseded PAUTH is revoked. A new operation-time claim and
implementation-start packet remain mandatory after fresh GO.

### Prior GO Finding 1 - Dispatch Cap Correction

Response: corrected. A's `dispatch_max_items` is **1 and must remain 1**. The
implementation must not change caps, eligibility, routing, precedence, role,
or any unrelated harness record. Version 001's reference to max-items 4 is
withdrawn and is not an acceptance criterion.

### Prior GO Finding 2 - Efficacy Evidence Must Exercise the Actual Surface

Response: binding. Acceptance rests on the actual headless form
`codex exec -c default_permissions=\":workspace\"`, not on
`codex sandbox windows ... echo`. Each smoke run must observe an exact
workspace-capable effective profile and create, read, then remove a unique
in-root sentinel. A read-only, unknown, ambiguous, or full-access profile fails
even when every process exits 0. One genuine dispatcher-produced substantive
A/PB artifact is additionally required.

### Prior GO Finding 3 - Canonical Readback Command

Response: corrected. Before/after harness readback uses
`gt harness show --harness A`, which already emits JSON. The invalid
`gt harness show A --json` form is withdrawn.

### Prior GO Finding 4 - Foreign Registry Projection Divergence

Response: binding. The canonical `gt harness set-invocation-surface` writer is
required, but the implementation must compare exact A headless argv before and
after, preserve the current A PB-only role and max-items 1, and neither adopt
nor overwrite pre-existing event-source or other foreign projection changes.
If canonical regeneration exposes foreign fields, finalization waits for clean
ownership or uses an authorized hunk-exact path. Whole-file staging is not
permitted. Operation-time peer-report collision checks remain mandatory.

### Prior GO Finding 5 - Project Traceability

Response: no scope change. The fleet-harness project placement is intentional
and explicitly covered by the WI-5310 V2 PAUTH. This does not create Goose/G as
a harness; Goose does not exist in the operative fleet.

## Revised Implementation Scope

### 1. Canonical Invocation Migration

After fresh GO, exact claim, and implementation-start, use
`gt harness set-invocation-surface` to update A's `headless` surface. Do not
hand-edit `harness-state/harness-registry.json` or `groundtruth.db`.

Preserve model `gpt-5.5`, approval `never`, reasoning `xhigh`, project-root
selection, `.codex` add-dir, PB-only role, eligibility, max-items 1, routing,
and precedence while replacing only the legacy selector:

```text
--sandbox workspace-write
```

with:

```text
-c default_permissions=":workspace"
```

Legacy and new selectors must never coexist.

### 2. Runtime-Capable Private-Desktop Smoke

Update `scripts/codex_no_window_smoke_probe.py` to exercise the same canonical
`codex exec` selector and require, for each run:

- requested profile `:workspace` and an observed exact workspace-capable
  effective profile with no read-only fallback;
- create, exact readback, and removal of a unique sentinel under the existing
  in-root smoke directory;
- no residual sentinel after bounded cleanup;
- complete marker attribution, dispatcher wrapper, and private desktop;
- zero visible windows; and
- bounded sanitized requested-profile, effective-profile, sentinel, and
  transcript evidence.

Any ambiguity, mismatch, missing lifecycle step, residue, visible window,
nonzero wrapper status, or read-only/full-access fallback writes failed proof
immediately. A prior success cannot survive a later failure.

### 3. Static and Live Verifier Contract

Update `scripts/verify_codex_dispatch.py` to require exactly
`default_permissions=\":workspace\"`, reject all legacy `--sandbox` selectors,
reject unknown/read-only/full-access proof values, and require every stronger
runtime field. Static argv plus stale or incomplete proof cannot yield
`live_headless_ready=true` or effective dispatch readiness.

### 4. Focused Tests and Genuine PB Proof

Add focused fixtures for command composition, exact profile parsing,
read-only/full-access/ambiguous rejection, sentinel success/failure/cleanup,
visible-window failure, static verifier rejection, and current-proof
acceptance. Then route one fresh substantive governed PB item to A through the
dispatcher/private desktop. The A-authored bridge artifact must be published
through canonical helpers; prose-only or read-only exit 0 does not count.

## Specification-Derived Verification Plan

| Specification | Executed evidence required before verification | Expected result |
| --- | --- | --- |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | `python -m pytest platform_tests/scripts/test_codex_no_window_smoke_probe.py platform_tests/scripts/test_verify_codex_dispatch.py -q --tb=short` | Effective-profile, sentinel, containment, and verifier cases pass. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | `gt harness show --harness A` before/after plus focused argv assertions | A remains active, PB-only, max-items 1, and uses only `:workspace` with all pins preserved. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `python scripts/codex_no_window_smoke_probe.py --project-root . --dispatch-wrapper --json` | Two private-desktop runs complete write/read/remove with zero visible windows. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Fresh independently approved substantive A/PB dispatch | A publishes a valid governed PB bridge artifact through canonical helpers. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and PAUTH DCLs | Claim status plus `implementation_authorization.py begin` readback | Exact claim/start succeed for all five targets with no peer conflict. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report maps every linked spec to commands/results; independent LO review | Every required row has observed evidence before VERIFIED. |
| Nonimpairment and parity | Dispatcher report/status/health and all three harness parity phase commands | No role, cap, routing, live-worker, containment, or parity regression. |

## Acceptance Criteria

1. A's canonical headless argv uses `default_permissions=\":workspace\"` and
   contains no legacy `--sandbox` selector.
2. A remains active, `can_receive_dispatch=true`, PB-only, max-items **1
   unchanged**, model `gpt-5.5`, approval `never`, reasoning `xhigh`, and
   `.codex` add-dir intact.
3. Two private-desktop smoke runs prove actual in-root create/read/remove
   capability and zero visible windows through the same `codex exec` form.
4. Read-only, unknown, ambiguous, full-access, stale, incomplete, or residual
   sentinel evidence fails readiness even when process return codes are zero.
5. `verify_codex_dispatch.py` cannot report live readiness from legacy argv or
   incomplete runtime evidence.
6. A fresh dispatcher-produced A/PB worker publishes one substantive governed
   PB bridge artifact through canonical helpers.
7. Focused tests, ruff, parity phases, dispatcher health/status, and independent
   LO verification pass.
8. Pre-existing registry and worktree changes remain preserved and excluded
   from the focused commit through hunk-exact ownership.

## Pre-Filing Preflight Subsection

Candidate applicability preflight against the completed version-005 content:

- `bridge_document_name`: `gtkb-wi5310-codex-effective-workspace-profile`
- `content_source`: `pending_content`
- `preflight_passed`: `true`
- `missing_required_specs`: `[]`
- `missing_advisory_specs`: `[]`
- `warnings.missing_parent_dirs`: `[]`
- `warnings.spec_links_section.status`: `harvested`

Candidate mandatory ADR/DCL clause preflight against the same content:

- clauses evaluated: 5
- must_apply: 4
- may_apply: 1
- evidence gaps in must_apply clauses: 0
- blocking gaps: 0
- exit code: 0

The four satisfied must-apply clauses are the in-root placement clause, the
numbered bridge-chain authority clause, concrete specification linkage, and
spec-derived verification mapping. Live filing remains prohibited if the
helper-mediated final rerun reports a blocking gap.

## Risks / Rollback

- **Permissions-profile compatibility:** unsupported or misreported
  `:workspace` fails closed; there is no silent read-only or full-access
  fallback.
- **Generated registry concurrency:** canonical projection may expose foreign
  fields. Preserve them, compare exact A argv, and finalize only owned hunks.
- **Sentinel residue:** unique run paths and bounded cleanup are mandatory; any
  residue fails the proof.
- **Window containment:** any visible console revokes readiness; the repair does
  not disable Codex, the bridge, or dispatcher.
- **Rollback:** use the canonical invocation-surface writer to restore the exact
  pre-change A argv, write a failed readiness proof, and preserve all unrelated
  fields. Do not hand-edit the registry, disable automation, or mutate
  dispatcher/TAFE state.

## Files Expected To Change

- `harness-state/harness-registry.json`
- `scripts/codex_no_window_smoke_probe.py`
- `scripts/verify_codex_dispatch.py`
- `platform_tests/scripts/test_codex_no_window_smoke_probe.py`
- `platform_tests/scripts/test_verify_codex_dispatch.py`

## Recommended Commit Type

`fix`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
