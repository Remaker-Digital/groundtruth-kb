REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher/TAFE deliberately disabled
author_metadata_source: explicit_owner_direction

bridge_kind: prime_proposal
Document: gtkb-wi5369-cursor-dispatch-telemetry-provenance
Version: 009
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5369-cursor-dispatch-telemetry-provenance-008.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5369-CURSOR-TELEMETRY-PROVENANCE-20260717
Project Authorization Version: 2
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5369
Related Work Items: WI-5427, WI-5227, WI-5451
target_paths: ["platform_tests/scripts/test_cursor_dispatch_telemetry_provenance.py"]
implementation_scope: focused test only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
Recommended commit type: test

No KB mutation: this proposal performs no MemBase mutation and no
`groundtruth.db` write; `groundtruth.db` is intentionally absent from
`target_paths`.

# Revised Implementation Proposal — Cursor E Dispatcher Telemetry Provenance

## Revision Claim

Prime Builder accepts version 008. Versions 005 and 007 did not implement,
verify, withdraw, or supersede the substantive version 003 test design, and
their `NO-ACTION` carrier/closure language is withdrawn. This revision restores
the one-test implementation proposal, updates its stale dependency evidence,
and requires a fresh independent `GO`, exact same-session work-intent claim,
and schema-v3 implementation-start packet before any target byte is created.

The scope remains exactly the version 003 scope: add one isolated integration
test proving that the existing committed, role-neutral dispatch telemetry
reconciliation records trusted Cursor E identity, model, success, timeout/fail
status, exit code, diagnostic, and session provenance. No production source
change is proposed.

Version 003's requirement that WI-5427 become `VERIFIED` is no longer a
satisfiable or accurate gate. The canonical WI-5427 carrier is now terminal
`WITHDRAWN` at version 007. That withdrawal explicitly preserves the prior
candidate as unverified history and grants no implementation authority. It did,
however, retire the stale carrier whose dirty source ownership originally
motivated WI-5369's hold. This revision therefore does not call WI-5427
complete, does not adopt its candidate, and does not wait for an impossible
verdict. Instead, it binds implementation to the committed current `HEAD` and
requires every exercised production path to be clean and hash-frozen before
claim acquisition and again before the implementation report.

## Current Authority And Baseline

| Surface | Current evidence | Consequence |
| --- | --- | --- |
| WI-5369 lifecycle | Version 008 is current `NO-GO`; version 004's earlier `GO` is not current | This version 009 requires fresh independent review and `GO`. |
| Project authorization | The exact stable PAUTH id is active at version 2, includes only WI-5369, allows bridge/metadata/test/governance-evidence, and uses only canonical forbidden-operation tokens | Owner approval is sufficient for the bounded test-only proposal; it does not bypass later gates. |
| WI-5427 | Canonical version 007 is terminal `WITHDRAWN`, not `VERIFIED` | Do not adopt the withdrawn candidate or treat it as completed behavior; use committed clean-source evidence instead. |
| WI-5227 | Canonical version 008 is `VERIFIED`; its dispatcher-runtime correction is committed | Treat its current committed bytes as part of the exercised baseline. |
| WI-5451 | Canonical physical head is `GO` at version 004; the file is currently untracked and no live claim exists | It remains a potential shared-source owner on `scripts/gtkb_dispatcher_daemon.py`; serialize if it becomes implementation-active. |
| New test | `platform_tests/scripts/test_cursor_dispatch_telemetry_provenance.py` is absent | The implementation may create this path only after fresh GO, claim, and start. |
| Exercised production paths | `scripts/dispatcher_runtime.py`, `scripts/ensure_dispatcher_daemon.py`, and `scripts/gtkb_dispatcher_daemon.py` are clean relative to `HEAD` | Their exact pre-start hashes must be frozen; they are evidence inputs, never mutation targets. |
| Claims | WI-5369's historical implementation claim is expired; WI-5427 and WI-5227 have none; WI-5451's historical draft claim is expired | A fresh exact-session WI-5369 claim is mandatory, and any new active source owner blocks start. |

Current read-only baseline at `HEAD`
`75decbfa704fe50288aecbc5669def329a0825df`:

- `scripts/dispatcher_runtime.py` — SHA-256
  `02A54EA1E819157C6C41C2232E7244D73AAFEFF3D1BA47FD3F53A89DE9FE4189`.
- `scripts/ensure_dispatcher_daemon.py` — SHA-256
  `5F172CE9A0917532500632E91F37625975D5C4C140524428A27F3AEDE4B9C317`.
- `scripts/gtkb_dispatcher_daemon.py` — SHA-256
  `E9A9DFB96D94D6623ACE9110A861AA901DFFC38864187C5D10B21BD3BFD2DE1C`.
- Existing telemetry and focused exit-reconciliation baseline: 26 tests passed
  in 3.19 seconds under the repository's existing test configuration.

These hashes are proposal-time evidence only. Operation-time start must re-read
the then-current committed `HEAD`, require clean exact paths, and record fresh
hashes. Drift does not authorize adoption; it requires re-evaluation and, when
load-bearing, return through the bridge.

## Requirement Sufficiency

Existing requirements sufficient. Version 002 accepted the underlying
test-only design and version 004 independently approved version 003's clean
baseline control. This revision changes lifecycle and dependency evidence, not
the telemetry contract or implementation scope.

The PAUTH's machine-readable version 2 canonicalization is exact and bounded:
it retains the same WI-5369, owner decision, specification, and one-test scope;
it removes the invalid `tafe_mutation` and `runtime_state_mutation` taxonomy
tokens from `forbidden_operations` while preserving those narrower
prohibitions in the binding scope summary. No fallback authorization is used.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5369; TEST-11485; PAUTH-DISPATCHER-BLACK-BOX-WI5369-CURSOR-TELEMETRY-PROVENANCE-20260717 v2; bridge/gtkb-wi5369-cursor-dispatch-telemetry-provenance-008.md",
  "canonical_authority": "SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001; SPEC-CENTRALIZED-DISPATCH-SERVICE-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "one isolated test exercising the committed production reconciliation API without modifying that API",
  "before_behavior": "Generic telemetry coverage passes, but no isolated committed-baseline regression proves trusted Cursor E provenance for success and timeout/failure reconciliation.",
  "after_behavior": "The focused test proves Cursor E dispatch identity, harness identity, provider, model, terminal status, exit code, diagnostic, and session provenance through the existing role-neutral path.",
  "self_descriptive_naming": "The test module and cases name Cursor dispatch telemetry provenance and success or failure behavior directly.",
  "obsolete_guidance_disposition": "Withdraw versions 005 and 007 closure claims and replace version 003's impossible WI-5427 VERIFIED predicate with current withdrawn-carrier and operation-time clean-baseline evidence.",
  "history_preservation": "All prior bridge versions and the withdrawn WI-5427 candidate remain history; no prior file or production byte is rewritten or adopted.",
  "baseline": {
    "wi5427": "WITHDRAWN at version 007; not implementation evidence",
    "wi5227": "VERIFIED at version 008",
    "wi5451": "GO at version 004; no active claim",
    "new_test_target": "absent",
    "production_source": "three exercised paths clean at proposal time"
  },
  "expected_result": {
    "success_case": "trusted Cursor E worker provenance is persisted with completed status and no fabricated failure",
    "timeout_or_failure_case": "trusted Cursor E provenance is persisted with the real classified outcome, exit code, and bounded diagnostic",
    "production_source": "unchanged"
  },
  "rollback": "Remove only the new governed test file through an independently approved successor; never delete bridge history.",
  "hard_invariants": [
    "No production source mutation.",
    "No withdrawn WI-5427 candidate adoption.",
    "No implementation while an exercised production path is dirty or actively owned by another session.",
    "No dispatcher, TAFE, runtime, lease, eligibility, routing, harness, credential, external-system, deployment, release, or Git-history mutation.",
    "No new hard-coded timer, TTL, sleep, retry, throttle, threshold, fan-out, or concurrency literal."
  ],
  "fail_closed_conditions": [
    "The exact PAUTH is not active at version 2 or no longer includes WI-5369.",
    "The new test target exists with foreign bytes.",
    "Any exercised production path is dirty relative to committed HEAD.",
    "Any other session actively claims or reserves an exercised production path.",
    "The test cannot exercise the real production reconciliation API.",
    "Cursor E identity, model, status, exit code, diagnostic, or session provenance is absent, conflicting, or synthetic."
  ],
  "essential_context_preservation": "Preserve trusted dispatcher/session evidence, richer provider telemetry, exact terminal outcome, source attribution, and existing fleet-neutral behavior."
}
```

## Specification Links

- `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `GOV-SESSION-ROLE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `DCL-DISPATCH-ENVELOPE-RULES-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `GOV-ENV-LOCAL-AUTHORITY-001`

## Prior Deliberations And Related Work

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` — owner decision
  backing the exact PAUTH and bounded fleet-defect proposal lifecycle.
- `DELIB-202666260`, `DELIB-202666374`, `DELIB-202666410`,
  `DELIB-202666551`, and `DELIB-202666230` — telemetry and fail-closed
  dispatch lineage carried forward from the reviewed v003 proposal.
- `bridge/gtkb-wi5369-cursor-dispatch-telemetry-provenance-008.md` — current
  independent `NO-GO`, whose invalid-closure finding is accepted here.
- `bridge/gtkb-wi5427-daemon-generation-handoff-007.md` — terminal withdrawal
  of the stale carrier; not implementation or verification evidence.
- `bridge/gtkb-wi5227-ollama-abrupt-exit-diagnostics-008.md` — terminal
  `VERIFIED` correction on the exercised dispatcher-runtime surface.
- `bridge/gtkb-wi5451-runtime-dependency-closure-004.md` — current `GO` on a
  future source owner that includes `scripts/gtkb_dispatcher_daemon.py` and
  therefore requires serialization if it becomes implementation-active.

## Owner Decisions / Input

No new owner decision is required. The active exact PAUTH at version 2 remains
bound to the same owner decision and includes only WI-5369. It permits the one
test addition after the complete bridge and operation-time gates. Its scope
summary expressly forbids direct harness contact, dispatcher or TAFE mutation,
runtime/lease/eligibility/routing changes, source/config edits, credentials,
external-system mutation, destructive cleanup, unrelated mutation, Git
history rewrite or push, production deployment, and release.

## Proposed Scope And Start Contract

1. Obtain a fresh independent `GO` on this exact version 009 proposal.
2. Immediately before claim acquisition, confirm:
   - the exact PAUTH is active at version 2 and includes only WI-5369;
   - the test target is absent or clean;
   - all three exercised production paths are clean relative to committed
     `HEAD`, and record their fresh hashes;
   - no other session has an active claim/start packet reserving any exercised
     production path, including an implementation-active WI-5451 carrier.
3. Acquire a fresh exact-session `go_implementation` claim and mint a fresh
   schema-v3 start packet authorizing only
   `platform_tests/scripts/test_cursor_dispatch_telemetry_provenance.py`.
4. Add success and timeout/failure integration coverage through the committed
   production reconciliation entry point. Assert dispatch id, harness id E,
   provider, actual model, terminal status, exit code, bounded diagnostic, and
   matching session linkage. Missing or conflicting authority must fail closed.
5. Use existing governed configuration and fixtures. Do not introduce a
   hard-coded duration, `sleep`, timeout, TTL, retry, throttle, threshold,
   fan-out, or concurrency value. A timeout outcome must be modeled through
   existing classified evidence rather than a new live wait budget.
6. Run the focused test, the complete shim telemetry suite, the mapped runtime
   reconciliation tests, Ruff check and format-check, and exact diff/status
   checks. Re-read source hashes after testing.
7. If any exercised production path or claim ownership changes, stop and return
   through the bridge without filing an implementation report.
8. Otherwise file the first post-implementation report as `NEW`, carrying the
   schema-v3 packet, exact pre/post source hashes, commands, results, and
   specification-to-test mapping for independent verification.

## Out Of Scope

- Any edit to `scripts/dispatcher_runtime.py`,
  `scripts/ensure_dispatcher_daemon.py`, or
  `scripts/gtkb_dispatcher_daemon.py`.
- Any adoption, verification, repair, or reoffer of the withdrawn WI-5427
  candidate, and any implementation of WI-5227 or WI-5451.
- Dispatcher or TAFE configuration or runtime mutation, activation, restart,
  routing, eligibility, worker, lease, harness, registry, or identity mutation.
- Direct harness contact or live Cursor-capacity proof during implementation;
  the PAUTH retains fresh genuine E proof as a later acceptance requirement
  when capacity is available.
- Runtime telemetry files, scratch paths, copied projections, or retired
  evidence as authority.
- New timer or concurrency literals, credential operations, external-system
  mutation, destructive cleanup, Git staging/commit/push/history rewrite,
  deployment, or release.

## Cross-Harness Disposition

- A, B, C, D, F, and H: no production behavior change; existing fleet-neutral
  telemetry regressions remain required.
- E: receives direct success and timeout/failure integration coverage through
  the same committed role-neutral reconciliation path. No Cursor-specific
  production branch is authorized.

## Specification-Derived Verification Plan

| Governing requirement | Executed evidence required in implementation report | Expected result |
| --- | --- | --- |
| Active PAUTH v2; `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`; `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | Fresh exact PAUTH readback before claim and start | Active version 2, exact project/WI, test class allowed, canonical forbidden-operation tokens only. |
| `GOV-WORK-TREE-HYGIENE-001`; `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`; `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Scoped status, `HEAD`, hashes, WI-5427/WI-5227/WI-5451 current heads, and claim/packet collision scan before claim and before report | Test absent/clean; all exercised source paths clean and unchanged; no active foreign owner. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`; `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Fresh exact-session claim and schema-v3 implementation-start packet | Packet authorizes only the one test path and no production source. |
| `SPEC-SHIM-HARNESS-DISPATCH-TELEMETRY-001`; `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | New Cursor E success and timeout/failure tests; complete shim telemetry suite; focused dispatcher-runtime reconciliation tests | Trusted E identity/model/status/error/session provenance persists through the production path. |
| `GOV-SESSION-ROLE-AUTHORITY-001`; `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`; `DCL-DISPATCH-ENVELOPE-RULES-001` | Positive matching-session case and negative missing/conflicting-authority cases | No verdict-prose inference or synthetic provenance is accepted. |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001`; `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Fleet-neutral regression subset and before/after production hashes | Cursor E gains evidence without a production branch or regression to other harnesses. |
| `GOV-ENV-LOCAL-AUTHORITY-001`; owner timer/concurrency directive | Static scan of the new test and exact diff for duration/retry/concurrency literals | No new hard-coded control literal; existing governed configuration/fixtures are reused. |
| Bridge/spec linkage family | Candidate/live applicability and clause preflights, exact numbered filing, and independent review | No missing required/advisory specs or blocking clause gaps. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Implementation report carries this mapping and exact executed output; independent reviewer reruns or independently validates it | Every carried requirement has executable evidence before `VERIFIED`. |

## Acceptance Criteria

- A fresh independent `GO` responds to this version 009 proposal.
- The test target is absent or clean and every exercised production path is
  clean, hash-frozen, and free of active foreign claim ownership immediately
  before claim/start and again before report filing.
- The exact same-session schema-v3 packet authorizes only
  `platform_tests/scripts/test_cursor_dispatch_telemetry_provenance.py`.
- The new test exercises the real committed production reconciliation entry
  point for Cursor E success and timeout/failure outcomes.
- Trusted identity, model, status, exit, diagnostic, and matching-session
  provenance pass; missing/conflicting authority fails closed.
- Existing shim telemetry and focused runtime-reconciliation regressions pass.
- Ruff check and format-check pass for the new test.
- Production source hashes remain unchanged and no new hard-coded timer or
  concurrency literal exists.
- No out-of-scope dispatcher, TAFE, runtime, harness, Git, credential,
  external-system, deployment, or release action occurs.

## Risk And Rollback

The principal risk is proving behavior against moving or foreign production
bytes. Two operation-time cleanliness/hash checks and an active-owner scan
bound that risk. The second risk is mistaking WI-5427's withdrawal for
verification; this revision expressly rejects that inference and uses only
committed current source as evidence. The third is colliding with WI-5451's
current GO; any active claim or source dirt blocks WI-5369 before target write
and before report.

Rollback is a separately governed removal of only the new test file. Bridge,
MemBase, Deliberation Archive, and withdrawn-carrier history remain append-only.

## Files Expected To Change

- `platform_tests/scripts/test_cursor_dispatch_telemetry_provenance.py`

## Pre-Filing Preflight

- Candidate applicability preflight passed with
  `missing_required_specs: []`, `missing_advisory_specs: []`, and
  `blocking_errors: []`; the exact PAUTH v2 operation-time evaluation allowed
  the one declared test target.
- Mandatory ADR/DCL clause preflight evaluated five clauses, found three
  `must_apply` and two `may_apply` clauses, and reported zero evidence gaps and
  zero blocking gaps (exit 0).
- The governed revision helper must repeat both checks against this completed
  content before it creates the numbered bridge file.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
