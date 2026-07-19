REVISED
::init gtkb lo
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6668-9974-7d72-a456-826f9a67e627
author_model: OpenAI Codex
author_model_version: GPT-5.5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined PB role; build activity envelope; approval_policy=never

# WI-5427 Revised Proposal - Self-healing generation handoff requests

bridge_kind: prime_proposal
Document: gtkb-wi5427-daemon-generation-handoff
Version: 005
Responds to: bridge/gtkb-wi5427-daemon-generation-handoff-004.md
Carries forward approved proposal: bridge/gtkb-wi5427-daemon-generation-handoff-001.md
Carries forward implementation report: bridge/gtkb-wi5427-daemon-generation-handoff-003.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5427-DAEMON-GENERATION-HANDOFF-20260717
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5427

target_paths: ["scripts/gtkb_dispatcher_daemon.py", "scripts/ensure_dispatcher_daemon.py", "platform_tests/scripts/test_gtkb_dispatcher_daemon.py", "platform_tests/scripts/test_dispatcher_daemon_supervision.py"]

implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: feat:

---

## Revision Claim

Version 004's blocking finding is accepted. The existing generation-handoff
candidate can permanently suspend dispatch when
`generation-handoff-request.json` is unreadable, expired, or bound to a
different daemon identity because every error branch returns `wait` and the
request has no bounded lifetime.

This revision seeks fresh GO for one correction:

1. give every handoff request a bounded TTL;
2. recover requests that are expired or positively proven to belong to a
   different daemon identity;
3. keep malformed, unreadable, ambiguous, live-work, and provenance-unknown
   cases fail-closed until deterministic recovery is safe; and
4. test both daemon-side and supervisor-side self-healing.

No source or test byte has changed after the version 004 NO-GO. The complete
version 003 candidate remains present and foreign to this revision until a
fresh GO, exact `go_implementation` claim, and schema-v3 implementation-start
packet authorize the correction. This proposal does not inspect or mutate
dispatcher configuration, dispatcher runtime state, TAFE, harness
configuration, roles, routing, workers, leases, Git state, credentials,
external systems, deployment, or release state.

## Findings Addressed

### P1 - Unbounded handoff-request state can permanently suspend dispatch

Accepted in full.

The correction will add a small request-lifetime contract owned by the
existing daemon/supervisor implementation:

- A request carries its existing `requested_at` timestamp and is valid only
  for a bounded configured duration. The default follows the existing
  short-lived daemon-lock sanity pattern.
- A readable request that exceeds the TTL is stale. The process that proves
  staleness may clear only that request file, record a stable recovery reason,
  and continue through the existing canonical dispatch or supervisor path.
- A readable request whose PID and process-create-time tuple is positively
  inconsistent with the current provenance-verified live daemon is stale for
  that daemon. The daemon or serialized supervisor may clear it and continue
  or issue one fresh request for the current daemon identity.
- An unreadable request uses its file modification time only as a bounded
  age fallback. It remains fail-closed before expiry and may be cleared only
  after the file itself is older than the TTL.
- Missing, future-dated, malformed, or otherwise ambiguous timestamps remain
  fail-closed. No guessed clock value grants recovery.
- A valid unexpired request for the current daemon retains the version 003
  behavior: dispatch quiescence is required, live workers or leases defer
  handoff, commit phase causes self-exit, and only the supervisor starts the
  attested hidden successor.

The correction does not add an owner-quiesce mode because the requirement can
be met with deterministic TTL and identity recovery. It does not delete lease,
claim, recipient, provenance, TAFE, bridge, or dispatcher audit evidence.

## Exact Scope

Only these existing targets remain authorized:

- `scripts/gtkb_dispatcher_daemon.py`
  - parse request age with strict UTC handling;
  - expose bounded stale-request classification;
  - clear only expired or positively foreign-identity requests;
  - continue dispatch after safe recovery;
  - preserve `wait` for every unresolved case.
- `scripts/ensure_dispatcher_daemon.py`
  - use the same classifier under the existing supervisor lock;
  - replace a stale or positively foreign request with at most one fresh
    current-daemon request;
  - preserve exact-once hidden successor launch and attestation.
- `platform_tests/scripts/test_gtkb_dispatcher_daemon.py`
  - test valid, expired, malformed, unreadable, future-dated, current-identity,
    foreign-identity, live-work, and unknown-provenance request behavior.
- `platform_tests/scripts/test_dispatcher_daemon_supervision.py`
  - test stale identity recovery, TTL recovery, pre-expiry fail-closed
    behavior, fresh-request replacement, supervisor serialization, and no
    process termination or live-state mutation.

No new module, configuration file, state schema, dispatcher registration,
scheduled task, CLI, runtime-state migration, or target path is added.

Current whole-file SHA-256 values form the fail-closed pre-start byte baseline:

| Target | SHA-256 |
|---|---|
| `scripts/gtkb_dispatcher_daemon.py` | `dc1e1a077cb83c1d2dc9c69180d01d8cca77e56cd179d5f8ddf859deaf608556` |
| `scripts/ensure_dispatcher_daemon.py` | `de7011e204ed9e97be23aba7889c2716ebf61d8b4d6defcb5b5b1e0cd5e810b3` |
| `platform_tests/scripts/test_gtkb_dispatcher_daemon.py` | `153af7f6d53db772acce98b940b19fb5dc0a83bd931f9ec43025f6e913110995` |
| `platform_tests/scripts/test_dispatcher_daemon_supervision.py` | `225d1dbfae5d461258687e5649798757e5529f7536a75c9d495b929aed4a7ac7` |

Any pre-start hash drift requires a new ownership review before mutation.

## Requirement Sufficiency

Existing requirements sufficient.

`DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001` and
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` require supervised recovery
without indefinite disablement or impairment of healthy dispatch.
`DELIB-20260706-DISPATCHER-SUPERVISOR-SELF-HEALING-WI` supplies the exact
owner decision identified by version 004: any dispatcher supervisor disable
must carry a TTL or explicit owner quiesce record. This revision chooses the
TTL route and does not revise a requirement.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Prior Deliberations

- `DELIB-20260706-DISPATCHER-SUPERVISOR-SELF-HEALING-WI` requires bounded
  expiry or explicit owner quiescence for dispatcher supervisor disablement.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` authorizes this
  bounded defect-repair carrier while preserving bridge GO, claim,
  implementation-start, independent verification, and focused-finalization
  gates.
- `DELIB-20260717-DISPATCHER-CONFIGURATION-TROUBLESHOOTER-HOLD` keeps
  dispatcher configuration and runtime-state mutation outside this work.
- The canonical bridge versions 001 through 004 preserve the approved design,
  implementation report, and independent blocking finding.

## Owner Decisions / Input

No new owner decision is required.

The bounded source/test correction remains inside
`PAUTH-DISPATCHER-BLACK-BOX-WI5427-DAEMON-GENERATION-HANDOFF-20260717` and
the cited fleet defect-repair authorization. The current build envelope
permits direct black-box internal mutation only after this case-specific
revision receives independent GO and the ordinary claim/start gates pass.
The dispatcher-configuration troubleshooter hold remains controlling.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5427; bridge/gtkb-wi5427-daemon-generation-handoff-004.md; DELIB-20260706-DISPATCHER-SUPERVISOR-SELF-HEALING-WI",
  "canonical_authority": "DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; GOV-FILE-BRIDGE-AUTHORITY-001",
  "primary_route": "Bound every generation-handoff request, recover only expiry or a positively foreign daemon identity, and retain the existing serialized supervisor plus self-exit successor path.",
  "before_behavior": "Any persistent handoff-request error can return wait forever and suppress every daemon dispatch with no TTL or owner-quiesce record.",
  "after_behavior": "Valid current-daemon requests preserve quiescent handoff; expired or positively foreign requests self-heal; unreadable or ambiguous evidence remains fail-closed until bounded expiry.",
  "self_descriptive_naming": "generation_handoff_request_ttl_seconds, request_age_seconds, handoff_request_expired, and handoff_request_identity_recovered expose the bounded recovery decision.",
  "obsolete_guidance_disposition": "Version 003 guidance that every request error waits indefinitely is replaced only for proven expiry or proven foreign identity; all other fail-closed behavior remains.",
  "history_preservation": "Bridge, MemBase, Deliberation Archive, worker, lease, claim, recipient, provenance, TAFE, and audit records remain unchanged; only the ephemeral coordination request may be cleared after deterministic stale classification.",
  "baseline": {
    "candidate": "version 003 four-file implementation remains byte-preserved at the listed hashes",
    "blocking_finding": "version 004 P1 unbounded handoff-request disable",
    "configuration_and_runtime": "out of scope"
  },
  "expected_result": {
    "valid_request": "existing quiescence and self-exit behavior is unchanged",
    "expired_request": "cleared with stable diagnostics and normal dispatch resumes",
    "foreign_identity_request": "cleared only after current daemon identity is provenance-verified",
    "ambiguous_request": "waits until safe bounded recovery is proven"
  },
  "rollback": {
    "instructions": "Revert only the correction hunks after separate governance; never reset the four shared files or live dispatcher state.",
    "verification": "Original version 003 candidate hashes and behavior are restored while the canonical bridge history remains append-only."
  },
  "hard_invariants": [
    "No dispatcher configuration, runtime-state, TAFE, harness, role, routing, eligibility, worker, lease, claim, Git, credential, deployment, or release mutation.",
    "No external worker termination or daemon kill path.",
    "No request is cleared from unknown identity evidence before expiry.",
    "No handoff bypasses live-worker or live-lease quiescence.",
    "At most one serialized supervisor writes a replacement request or starts a successor.",
    "Every protected source/test edit requires fresh GO, exact claim, and schema-v3 implementation start."
  ],
  "fail_closed_conditions": [
    "Current target hashes drift before implementation start.",
    "Request time is missing, malformed, future-dated, or not strict UTC.",
    "File age or daemon identity cannot be established.",
    "Current daemon PID provenance is not verified.",
    "A valid request has not expired.",
    "Any worker or document lease is live.",
    "Supervisor lock, spawn, exit, or successor attestation is uncertain.",
    "Focused tests or mandatory preflights fail."
  ],
  "essential_context_preservation": "The implementation report must retain exact before/after target hashes, TTL value, request age source, stale classification reason, PID/create-time evidence, quiescence evidence, recovery action, replacement-request count, successor attestation, and no-mutation assertions."
}
```

## Specification-Derived Verification Plan

| Specification / invariant | Test or check | Required result |
|---|---|---|
| `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`; `DELIB-20260706-DISPATCHER-SUPERVISOR-SELF-HEALING-WI` | Focused daemon and supervisor tests for expiry, unreadable-before-expiry, unreadable-after-expiry, foreign identity, and current identity | Every disable is bounded; safe stale requests recover; current valid requests retain handoff behavior. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`; `ADR-DISPATCHER-ARCHITECTURE-001` | Existing generation-handoff, hidden spawn, supervisor lock, and successor attestation tests | One canonical daemon and supervisor path remains; no alternate queue or process controller is added. |
| `GOV-SESSION-ROLE-AUTHORITY-001`; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | PID/create-time mismatch, unknown provenance, live-worker, and live-lease fixtures | Only positively verified foreign identity or expiry recovers; ambiguous/live work remains fail-closed and untouched. |
| `GOV-WORK-TREE-HYGIENE-001` | Compare exact four-file baseline hashes and diff ownership before/after correction | Version 003 bytes are preserved and only attributable correction hunks are added. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Read latest fresh GO, claim, and named schema-v3 packet before edits; independent review after report | Role-correct append-only lifecycle and exact mutation authority. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Full two target test files, Ruff check, Ruff format check, `py_compile`, `git diff --check`, applicability preflight, and clause preflight | All pass with zero blocking gaps and exact command evidence in the implementation report. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Exact changed-path inventory | All changes stay inside the four in-root targets; no adopter or out-of-root path. |

## Acceptance Criteria

- Every new request carries a strict UTC creation time and a bounded TTL.
- A valid unexpired current-daemon request preserves version 003 behavior.
- An expired request is cleared with stable diagnostics and cannot continue
  suppressing normal dispatch.
- A request positively bound to another PID/create-time identity is recovered
  only when the current daemon identity is provenance verified.
- An unreadable request remains fail-closed before file-age expiry and
  self-heals after deterministic expiry.
- Missing, malformed, future-dated, or ambiguous evidence never grants early
  recovery.
- Live workers, live document leases, unknown quiescence, supervisor-lock
  contention, spawn failure, and successor-attestation failure remain
  fail-closed.
- No process is externally terminated; no dispatcher configuration/runtime
  state, TAFE, harness, role, routing, eligibility, lease, claim, credential,
  Git, deployment, or release state is mutated.
- The full four-file focused suite and all static/governance checks pass.

## Pre-Filing Preflight Subsection

Both mandatory preflights were executed against this completed revision:

- `groundtruth-kb\.venv\Scripts\python.exe scripts\bridge_applicability_preflight.py --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5427-daemon-generation-handoff-005.md`
  - PASS: `preflight_passed: true`; all four declared targets resolved; no
    missing required or advisory specifications; no blocking errors.
- `groundtruth-kb\.venv\Scripts\python.exe scripts\adr_dcl_clause_preflight.py --content-file .gtkb-state\bridge-revisions\drafts\gtkb-wi5427-daemon-generation-handoff-005.md`
  - PASS: five clauses evaluated; four `must_apply`; zero evidence gaps and
    zero blocking gaps.

## Risk And Rollback

The principal risk is clearing a request that still belongs to live handoff
work. Recovery therefore requires either bounded expiry or a positively
verified foreign daemon identity. All clock, identity, provenance, and
quiescence ambiguity remains fail-closed. The supervisor lock continues to
serialize replacements and successor launch.

Rollback is a separately governed hunk-scoped revert of only the new
self-healing correction. It must not reset the four shared files, remove the
version 003 candidate, or mutate live dispatcher state.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
