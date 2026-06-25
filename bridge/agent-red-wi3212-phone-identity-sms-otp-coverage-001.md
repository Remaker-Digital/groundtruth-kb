NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 4e30eeba-5f51-4cad-89fd-793ac8f59e98
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: Claude Code interactive; role=prime-builder; output_style=explanatory
author_metadata_source: interactive Claude runtime envelope plus hand-authored bridge proposal

# Implementation Proposal - WI-3212 Phone Identity Channel SMS OTP Coverage

bridge_kind: prime_proposal
Document: agent-red-wi3212-phone-identity-sms-otp-coverage
Version: 001 (NEW)
Date: 2026-06-25 UTC

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3212

target_paths: ["applications/Agent_Red/tests/unit/test_spec1879_phone_identity_coverage.py"]

## Claim

WI-3212 should add explicit deterministic coverage for the live `SPEC-1879`
"Phone Identity Channel: SMS OTP via Azure Communication Services" contract and
route that evidence through the bridge for Loyal Opposition verification.

`SPEC-1879` is an implemented Agent Red application feature. Its phone-identity
SMS OTP flow lives in `applications/Agent_Red/src/multi_tenant/widget_otp_verification.py`
(the `/api/chat/otp/send-sms` and `/api/chat/otp/verify-sms` endpoints,
`normalize_e164()`, the professional+ tier gate, hashed-token storage reusing
`sms_verification.hash_code()`, the 10-minute TTL, and the constant-time
`secrets.compare_digest` verification). `gt tests list --spec-id SPEC-1879`
returns **zero** mapped tests, and the WI was classified γ' (phantom-only
evidence) by the 16.B methodology review (`DELIB-0712`).

As with the sibling backend WIs in this project, the historical "phantom-only"
framing is partially stale: `applications/Agent_Red/tests/unit/test_widget_otp_verification.py`
already has a `TestSmsOtpEndpoints` class that covers the SMS endpoints'
**transport-failure** paths (`_send_sms` raising, `_send_sms` returning False)
and the **wrong-code attempt-increment** path. This proposal scopes around that
honestly and is **non-duplicative**: it adds the SPEC-1879 clauses the existing
suite leaves unasserted:

1. **E.164 normalization** (`normalize_e164`, req 1) — a pure function with no
   existing tests.
2. **Tier gate** (req 7) — starter tier is blocked (`reason="tier_blocked"`); the
   existing SMS tests all patch the tier gate open, so the block path is unasserted.
3. **Successful verify + single-use consumption** (req 5) — `verified=True`, the
   normalized phone returned, and `consume_token` invoked; the existing suite only
   tests the wrong-code path.
4. **Replay / lockout** — already-`used` token and locked-after-max-attempts both
   return `verified=False` for the SMS endpoint (the existing suite tests these for
   the email endpoint only).
5. **Hashed storage** (req 3, security) — `send-sms` stores `otp_code_hash`
   (SHA-256 via `hash_code`), never plaintext.
6. **SPEC-1879 security-parameter contract** — `_OTP_TTL == 600` (10-min TTL),
   `_RATE_MAX == 3` / `_RATE_WINDOW == 300` (3 requests per 5 min per IP, req 4),
   `_OTP_LENGTH == 6`, and the dedicated `_SMS_OTP_TOKEN_TYPE`.

This is a bounded `test_addition` item. It adds one Agent Red test module and
expects no production source mutation; `widget_otp_verification.py` remains the
read-only implementation surface under test.

## Requirement Sufficiency

Existing requirements sufficient.

`SPEC-1879` enumerates the phone-identity OTP requirements (E.164 normalization,
SMS OTP via the existing ACS service, hashed SHA-256 storage with 10-minute TTL,
request throttling 3/5min per IP, attempt throttling 3 per conversation,
single-use consumption with constant-time comparison, professional+ tier gate),
and the implementation in `widget_otp_verification.py` realizes them. That is
enough detail for deterministic coverage of the listed clauses.

The current WI is a test-coverage gap, not a new feature request. No owner
clarification is required because the proposal only adds tests over the
already-implemented, in-root Agent Red behavior and does not change application
behavior, formal artifacts, release/deployment state, or credentials.

Scope boundaries observed during scoping (documented, not in scope to change):

- **Phase-1 deferral (not a defect):** `verify_sms_otp` deliberately does NOT mint
  a `customer_token` or link `ContactAttribute(PHONE)` (SPEC-1879 req 6); the code
  documents this as a reviewed Phase-1 constraint ("Codex P1-2 blocker"). The test
  asserts the implemented Phase-1 behavior (verified status + phone only), not the
  deferred token/linkage path.
- **Throttle layering (verified, not a drift):** SPEC-1879 req 4's "3 per
  conversation" attempt throttle is implemented in the in-conversation flow
  (`identity_preprocessor.py` `_MAX_SMS_OTP_ATTEMPTS = 3`, counter
  `identity_sms_attempts`). The widget endpoint's `_MAX_VERIFY_ATTEMPTS = 5` is a
  separate per-token lock on the pre-chat flow. Both are correct; this proposal
  asserts the widget endpoint's actual lock value and scopes the per-conversation
  throttle to the in-conversation flow (covered separately).

## In-Root Placement Evidence

The implementation target is the Agent Red application test tree, which is
in-root under `E:\GT-KB\applications\Agent_Red\` per
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`:

- `E:\GT-KB\applications\Agent_Red\tests\unit\test_spec1879_phone_identity_coverage.py`

Read-only verification may inspect these in-root paths:

- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\widget_otp_verification.py`
  (the `/send-sms` + `/verify-sms` endpoints, `normalize_e164`, tier gate,
  constants)
- `E:\GT-KB\applications\Agent_Red\src\multi_tenant\sms_verification.py`
  (`hash_code`, `_send_sms` reused by SPEC-1879)
- `E:\GT-KB\applications\Agent_Red\src\chat\identity_preprocessor.py`
  (in-conversation 3-per-conversation throttle; out of this file's scope)
- `E:\GT-KB\applications\Agent_Red\tests\unit\test_widget_otp_verification.py`
  (existing partial SMS coverage + mock pattern reused here)

## Specification Links

- `SPEC-1879` - Direct requirement: phone-identity SMS OTP (E.164 normalization,
  hashed SHA-256 storage, 10-min TTL, request throttling, single-use constant-time
  verification, professional+ tier gate).
- `SPEC-1686` - The SMS Verification Service (`hash_code`, ACS `_send_sms`) that
  SPEC-1879 reuses; the test asserts SPEC-1879's reuse of `hash_code` for hashed
  storage.
- `GOV-10` - Test artifacts must exercise live project interfaces; this proposal
  adds executable tests over the production endpoints instead of phantom-only
  evidence.
- `SPEC-1649` - Master test plan / live-interface policy.
- `GOV-12` - Work-item remediation must create or map test evidence.
- `GOV-13` - Test visibility and phase governance.
- `GOV-08` - Canonical MemBase behavior; the WI's coverage gap is tracked in the KB.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - Project-scoped owner
  authorization is required but does not replace bridge review, `GO`, target
  paths, implementation-start packet, report, or verification.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - Applies changed-file hygiene; Python coverage
  uses targeted pytest (cwd `applications/Agent_Red`) plus ruff check and ruff
  format checks on the touched test file.
- `SPEC-AUQ-POLICY-ENGINE-001` - Owner decisions are cited from existing AUQ-backed
  project authorization; this proposal requests no new owner decision.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - Governs status-bearing bridge file authority,
  role eligibility, and numbered append-only bridge chains.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Requires this proposal
  to cite all relevant specifications.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Requires verification to map
  linked specs to executed tests.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Requires project
  authorization, project id, and work-item metadata lines.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Agent Red application tests live
  under `applications/Agent_Red/`; this target honors that boundary.
- `GOV-STANDING-BACKLOG-001` - Governs backlog/work-item handling; this proposal
  uses the existing authorized WI and does not add project scope.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - Requires durable bridge/test evidence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Requires implementation intent and
  review evidence to be preserved as governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Frames this proposal as a lifecycle
  artifact for the work item.

## Owner Decisions / Input

No new owner decision is required. This proposal uses active project authorization
`PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23`,
citing owner decision `DELIB-20265586` (2026-06-23), and remains inside
snapshot-bound project member `WI-3212`. The only mutation class exercised is
`test_addition`.

## Prior Deliberations

- `DELIB-20265586` - Owner project authorization for the snapshot-bound Agent Red
  test-coverage-gap project; the standing authority for this WI's implementation.
- `DELIB-0712` - POR Step 16.B methodology review classifying `SPEC-1879` as γ'
  (phantom-only evidence) and scheduling it for live-interface remediation per
  GOV-10. This proposal is the remediation.
- `DELIB-0713` - Owner accepted multi-stream remediation and rejected
  assertion-only verification for behavioral requirements; this proposal supplies
  executable endpoint test evidence.
- `gt bridge threads --wi WI-3212 --json` returned `match_count: 0` before this
  proposal, so there is no prior WI-specific bridge chain to revise.

## Current-State Evidence

- `gt projects show PROJECT-AGENT-RED-TEST-COVERAGE-GAPS --json` shows `WI-3212`
  open/backlogged among 7 remaining members; the PAUTH `included_work_item_ids`
  snapshot includes `WI-3212`.
- `gt spec show SPEC-1879` shows status `implemented`, type `requirement`, and the
  11-requirement phone-identity OTP contract.
- `gt tests list --spec-id SPEC-1879` returns no tests (true phantom; not even a
  placeholder row).
- `widget_otp_verification.py` implements `normalize_e164` (line 535),
  `send_sms_otp` (`/send-sms`, line 610) with the tier gate + hashed storage +
  10-min `_OTP_TTL`, and `verify_sms_otp` (`/verify-sms`, line 716) with the
  used/locked checks, constant-time `secrets.compare_digest`, and single-use
  `consume_token`.
- `applications/Agent_Red/tests/unit/test_widget_otp_verification.py::TestSmsOtpEndpoints`
  covers the SMS transport-failure and wrong-code-increment paths and provides the
  FastAPI + `AsyncClient` + Cosmos/repo/tier-gate/`_send_sms` mock pattern reused
  here. It does NOT cover `normalize_e164`, the tier-gate block, successful verify,
  replay/lockout for SMS, hashed storage, or the parameter contract.

## Proposed Scope

1. Add `applications/Agent_Red/tests/unit/test_spec1879_phone_identity_coverage.py`
   (Agent Red copyright; runs with cwd `applications/Agent_Red`; mirrors the
   existing `TestSmsOtpEndpoints` mock pattern).
2. `normalize_e164`: valid E.164 passthrough, formatting-character stripping
   (spaces/dashes/parens/dots), and rejection of non-E.164 input (returns `None`).
3. SPEC-1879 parameter contract: assert `_OTP_TTL == 600`, `_RATE_MAX == 3`,
   `_RATE_WINDOW == 300`, `_OTP_LENGTH == 6`, and `_SMS_OTP_TOKEN_TYPE` is the
   dedicated SMS token type distinct from `_OTP_TOKEN_TYPE`.
4. Tier gate: starter tier (`_check_tier_gate` → False) yields a
   `reason="tier_blocked"` response and does not send an SMS.
5. Hashed storage: a successful `send-sms` patches `otp_code_hash` (the SHA-256
   hash of the code, never the plaintext `otp_code`); assert the stored value
   equals `hash_code(code)` and not the raw code, using the existing
   `_send_sms`/Cosmos mock pattern.
6. Successful verify + single-use: a matching hash yields `verified=True` with the
   normalized phone returned and `consume_token` awaited once.
7. Replay / lockout: `used=True` yields `verified=False`; `verify_attempts >= 5`
   yields `verified=False` with no further `patch_item` (mirroring the email lock
   test for the SMS endpoint).
8. Do not change production source, formal artifacts, project membership,
   release/deployment state, existing tests, credentials, or Agent Red runtime
   behavior.

## Specification-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `SPEC-1879` (E.164, req 1) | `normalize_e164` valid/strip/invalid tests. |
| `SPEC-1879` (TTL + throttle params, reqs 3-4) | Parameter-contract assertions on `_OTP_TTL`, `_RATE_MAX`, `_RATE_WINDOW`, `_OTP_LENGTH`, `_SMS_OTP_TOKEN_TYPE`. |
| `SPEC-1879` (tier gate, req 7) | Starter tier → `reason="tier_blocked"`, no SMS. |
| `SPEC-1879` + `SPEC-1686` (hashed storage, req 3) | `send-sms` stores `otp_code_hash` = `hash_code(code)`, not plaintext. |
| `SPEC-1879` (single-use + constant-time, req 5) | Successful verify → `verified=True` + phone + `consume_token`; matching hash via `secrets.compare_digest`. |
| `SPEC-1879` (replay/lockout) | `used` and locked-after-max return `verified=False`. |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | Repository-native pytest over the live Agent Red endpoints (cwd `applications/Agent_Red`). |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation starts only after LO `GO`, work-intent claim, and `implementation_authorization.py begin --bridge-id agent-red-wi3212-phone-identity-sms-otp-coverage`. |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | `ruff check` + `ruff format --check` + `git diff --check` on the touched file. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Target under `applications/Agent_Red/tests/`. |

Required commands after implementation (Agent Red tests run with cwd `applications/Agent_Red`):

```text
python -m pytest tests/unit/test_spec1879_phone_identity_coverage.py -q --tb=short
python -m ruff check tests/unit/test_spec1879_phone_identity_coverage.py
python -m ruff format --check tests/unit/test_spec1879_phone_identity_coverage.py
git diff --check -- applications/Agent_Red/tests/unit/test_spec1879_phone_identity_coverage.py
```

## Acceptance Criteria

- PASS when `normalize_e164` accepts valid E.164, strips formatting, and rejects
  non-E.164 input.
- PASS when the SPEC-1879 parameter contract (`_OTP_TTL`, `_RATE_MAX`,
  `_RATE_WINDOW`, `_OTP_LENGTH`, `_SMS_OTP_TOKEN_TYPE`) holds.
- PASS when the starter tier is blocked with `reason="tier_blocked"` and no SMS is sent.
- PASS when `send-sms` stores the SHA-256 hash, never the plaintext code.
- PASS when a matching code yields `verified=True` + phone + single-use consume.
- PASS when used/locked tokens yield `verified=False`.
- PASS when targeted pytest, ruff check, ruff format check, and diff whitespace
  checks pass.
- PASS when no production source, formal artifacts, project membership, new work
  items, credentials, release tags, deployment state, or Agent Red runtime
  behavior are changed.

## Risks / Rollback

Risk is low. This is additive test coverage over an implemented application
feature. The main risk is brittle coupling to Cosmos/ACS internals; the proposal
mitigates that by reusing the established `TestSmsOtpEndpoints` mock pattern
(FastAPI dependency overrides + patched `get_cosmos_manager`,
`VerificationTokenRepository`, `_check_tier_gate`, `_send_sms`, `_is_rate_limited`)
and asserting the endpoint contract at the response/patch boundary.

Rollback is to delete `applications/Agent_Red/tests/unit/test_spec1879_phone_identity_coverage.py`.
Bridge audit files remain append-only.

## Files Expected To Change

- `applications/Agent_Red/tests/unit/test_spec1879_phone_identity_coverage.py`

## Pre-Filing Preflight Evidence

Both mandatory preflights were run against this draft body (`--content-file`)
before filing. Loyal Opposition should rerun both against the operative bridge file.

Applicability preflight:

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `work_items: ["WI-3212"]`
- Benign warning `missing parent directories: tests/unit/test_spec1879_phone_identity_coverage.py`:
  this is the cwd-relative pytest command literal (Agent Red tests run from
  `applications/Agent_Red/`); the authoritative `target_paths` is the full in-root
  path `applications/Agent_Red/tests/unit/...`, whose parent
  `applications/Agent_Red/tests/unit/` exists. Non-blocking (`preflight_passed: true`).

Clause preflight:

- must_apply: `4`, may_apply: `1`, not_applicable: `0`
- evidence gaps in must-apply clauses: `0`
- blocking gaps: `0`
- exit code: `0`

Phantom-spec sweep: all cited ids (the WI-3217 proven governance battery plus
`SPEC-1879` and `SPEC-1686`) confirmed present in the live `specifications` table.
`SPEC-1694` (rate-limit, retired) is referenced in prose only, not cited as a link.

## Recommended Commit Type

`test:`
