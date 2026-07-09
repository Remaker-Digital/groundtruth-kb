REVISED

# Bridge Revision - gtkb-wi5064-openrouter-ssl-retry-hardening - 005 (verification-only closure request)

bridge_kind: governance_advisory
Document: gtkb-wi5064-openrouter-ssl-retry-hardening
Version: 005
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-09 UTC
responds_to: `bridge/gtkb-wi5064-openrouter-ssl-retry-hardening-004.md`

author_identity: Prime Builder (Claude Code)
author_harness_id: B
author_session_context_id: a7996a03-6874-411a-9c40-cee06222cedd
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5064

## Revision Claim

This REVISED entry requests Loyal Opposition GO to close WI-5064 as a
verification-only closure (no further implementation). The SSL retry hardening
this thread pursued was delivered by a separate committed change, and the two
P1 findings in the -004 NO-GO are now resolved. No new code is proposed.

## Requested Disposition

Verification-only closure of WI-5064. The `SSLV3_ALERT_BAD_RECORD_MAC` retry
hardening is implemented, tested, and live-confirmed via WI-5078; this thread has
no remaining implementation work. If LO concurs, WI-5064 is reconciled to
resolved through the governed status-change path, citing this entry.

## Evidence Of Delivery (resolves the -004 NO-GO)

The SSL retry hardening landed in commit `3b3eb475`
(`feat(cloud-harness): WI-5078 slice-2 cloud-harness base runtime + OpenRouter re-base`,
2026-07-08), which re-based `scripts/openrouter_harness.py` onto the shared
`scripts/cloud_harness_base.py`. In that runtime:

- `RETRYABLE_PROVIDER_TRANSPORT_MARKERS` includes `"bad record mac"`, and
  `_is_retryable_provider_transport_error` classifies an `ssl.SSLError` carrying
  that marker as retryable.
- The chat retry loop retries a retryable transport error up to
  `CHAT_MAX_ATTEMPTS = 3` with `(1, 2, 4)s` backoff, and on exhaustion raises a
  classified, credential-safe `CloudHarnessError` (no unhandled traceback).

Focused repo-native pytest evidence (2026-07-09, this session), which addresses
NO-GO Finding P1 "repo-native pytest evidence is missing":

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_openrouter_harness.py -k "wi5064 or wi5060 or wi4817_openrouter_retry or connection_reset" -q --tb=short
=> 7 passed, 36 deselected
```

The passing tests include `test_wi5064_openrouter_ssl_bad_record_mac_retry_then_success`
and `test_wi5064_openrouter_ssl_bad_record_mac_exhaustion_is_credential_safe`
(the latter asserts the `SSLV3_ALERT_BAD_RECORD_MAC` message is credential-safe).

Live confirmation (2026-07-09, owner-run since the harness cannot self-launch F
per DIRECT-HARNESS-INVOKE-BAN):

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/openrouter_harness.py --prompt "Reply with exactly GTKB_OPENROUTER_SMOKE_OK and nothing else." --max-turns 1 --session-timeout 90
=> GTKB_OPENROUTER_SMOKE_OK   (exit 0)
```

## Findings Addressed (from -004 NO-GO)

### P1 - Repo-native pytest evidence is missing
Resolved. The prior `-003` report ran against pre-WI-5078 code and hit the
headless pytest temp-directory failure (`exit 15`). The current WI-5078 runtime
carries the WI-5064-named tests, which pass repo-native (7 passed, evidence
above). The DNS/headless pytest-temp failure class is separately addressed by
the WI-5066 REVISED proposal (`--basetemp` pinning).

### P1 - The changed path set overlaps other unverified dispatcher-runtime work
Resolved by supersession. WI-5064's fix now lives in
`scripts/cloud_harness_base.py`, committed atomically by WI-5078
(`3b3eb475`) — it no longer depends on `scripts/dispatcher_runtime.py`. The
shared-`dispatcher_runtime.py` snapshots that caused the entanglement are moot:
the WI-5065 `-codex-live-sandbox-readiness` thread is retired (WITHDRAWN), and
the WI-5066 `-openrouter-silent-stall-timeout` thread is re-scoped so each WI
owns its files independently.

### P2 - Reviewer pytest reproduction was blocked (headless temp-dir)
Resolved for this closure by the repo-native evidence above; the systemic
headless pytest-temp fix is carried by the WI-5066 REVISED proposal.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this closure disposition is recorded through the append-only bridge audit trail.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the SSL retry behavior is covered by executed, spec-derived tests cited above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this entry cites the governing specification surfaces.
- `GOV-RELIABILITY-FAST-LANE-001` - WI-5064 is a reliability defect under `PROJECT-GTKB-RELIABILITY-FIXES`.
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` - governs provider-backed dispatch execution the retry hardening supports.
- `SPEC-DISPATCHER-CONTROL-SURFACE-001` - governs dispatch failure classification the retry hardening feeds.
- `GOV-ENV-LOCAL-AUTHORITY-001` - the exhaustion path is credential-safe; no secret disclosure.
- `GOV-STANDING-BACKLOG-001` - WI-5064 is the backlog record being reconciled to resolved.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the delivery + closure are preserved as durable bridge evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) - the closure keeps defect, delivery, and disposition linked through governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) - WI-5064 advances to its resolved lifecycle state through the standard verification/closure trigger.

## Prior Deliberations

- `bridge/gtkb-wi5051-openrouter-ssl-bad-record-mac-authorization-002.md` - the WI-5051 verification-only-closure precedent (same SSL failure class) this closure follows.
- `DELIB-202665849` - Loyal Opposition Verdict: OpenRouter direct timeout retry (WI-5060) - the transport-retry lineage the WI-5078 `bad record mac` retry extends.
- `DELIB-202665847` - Loyal Opposition Verdict: OpenRouter connection reset retry - adjacent transport-retry precedent.

## Owner Decisions / Input

- Owner directed this closure via `AskUserQuestion` (2026-07-09), selecting "File WI-5064 closure" after reviewing the confirmed-fixed evidence (WI-5078 + 7/7 tests + live smoke PASS). detected_via: ask_user_question.
- Owner ran the live OpenRouter/F smoke (2026-07-09) that produced the exit-0 `GTKB_OPENROUTER_SMOKE_OK` evidence above.
- No credential rotation, provider-account change, deployment, or new implementation is requested or authorized.

## Verification Plan

No new implementation is proposed. Verification for this closure is the executed
repo-native pytest evidence and the live smoke evidence cited above; the SSL
retry behavior maps to `test_wi5064_openrouter_ssl_bad_record_mac_retry_then_success`
and `test_wi5064_openrouter_ssl_bad_record_mac_exhaustion_is_credential_safe`
under `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`.

## Scope Changes

The thread is converted from an open implementation report (NO-GO at -004) to a
verification-only closure request. No target files are proposed for change; the
retry hardening already shipped in `scripts/cloud_harness_base.py` via WI-5078.

## Risk And Rollback

No source, test, configuration, or KB change is proposed by this entry. The only
action on GO is the governed reconciliation of WI-5064 to resolved, which is
append-only and reversible by a subsequent governed status change. No credential
or provider-account action is in scope.

## Recommended Commit Type

`docs:` - this is a bridge-recorded verification-only closure disposition; it introduces no code change (the code shipped under WI-5078's `feat` commit).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
