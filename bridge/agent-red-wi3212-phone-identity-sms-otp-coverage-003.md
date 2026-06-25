NEW
author_identity: prime-builder/cursor
author_harness_id: E
author_session_context_id: 2026-06-25T04-52-00Z-prime-builder-E-f7a3b2
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor interactive Prime Builder; bridge-clearance loop

# GT-KB Bridge Implementation Report - agent-red-wi3212-phone-identity-sms-otp-coverage - 003

bridge_kind: implementation_report
Document: agent-red-wi3212-phone-identity-sms-otp-coverage
Version: 003
Date: 2026-06-25 UTC
Responds to: bridge/agent-red-wi3212-phone-identity-sms-otp-coverage-002.md
Approved proposal: bridge/agent-red-wi3212-phone-identity-sms-otp-coverage-001.md
Recommended commit type: test

Project Authorization: PAUTH-PROJECT-AGENT-RED-TEST-COVERAGE-GAPS-AGENT-RED-TEST-COVERAGE-GAPS-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-AGENT-RED-TEST-COVERAGE-GAPS
Work Item: WI-3212

target_paths: ["applications/Agent_Red/tests/unit/test_spec1879_phone_identity_coverage.py"]
implementation_scope: test_addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Implementation Claim

Implemented the bounded `test_addition` approved at `-002`: added
`applications/Agent_Red/tests/unit/test_spec1879_phone_identity_coverage.py`
(10 deterministic pytest tests) closing the six SPEC-1879 clauses the existing
`test_widget_otp_verification.py::TestSmsOtpEndpoints` suite left unasserted:

1. **E.164 normalization** (`TestNormalizeE164`) — valid passthrough, formatting
   strip, invalid rejection.
2. **Security-parameter contract** (`TestSpec1879ParameterContract`) — `_OTP_TTL`,
   `_RATE_MAX`, `_RATE_WINDOW`, `_OTP_LENGTH`, `_SMS_OTP_TOKEN_TYPE`, and
   `_MAX_VERIFY_ATTEMPTS`.
3. **Tier gate** — starter tier returns `reason="tier_blocked"` with no SMS send.
4. **Hashed storage** — `send-sms` persists `otp_code_hash` via `hash_code`, not
   plaintext.
5. **Successful verify** — `verified=True`, normalized phone, single
   `consume_token` invocation.
6. **Replay and lockout** — already-used token and `verify_attempts >= 5` both
   return `verified=False`; lockout path does not patch attempts.

Reuses `_build_app` and `_mock_tenant_context` from the existing widget OTP test
module. No production source was modified.

## Specification Links

- `SPEC-1879` - phone-identity SMS OTP (E.164, tier gate, hashed storage, verify/replay).
- `SPEC-1686` - `hash_code` reuse for OTP storage.
- `GOV-10` - tests exercise live `/api/chat/otp/send-sms` and `/verify-sms` endpoints.
- `SPEC-1649` - master test plan / live-interface policy.
- `GOV-12` - work-item remediation creates executable test evidence.
- `GOV-13` - test visibility and phase governance.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - PAUTH + implementation-start packet.
- `SPEC-CODE-QUALITY-CHECKLIST-001` - ruff + pytest hygiene.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - numbered bridge chain.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project/PAUTH/WI metadata.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root Agent Red test path.
- `GOV-STANDING-BACKLOG-001` - authorized WI-3212 backlog member.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - durable bridge/test evidence.

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `SPEC-1879` (E.164) | `TestNormalizeE164` (3 tests) | yes | PASS |
| `SPEC-1879` (constants) | `TestSpec1879ParameterContract` (2 tests) | yes | PASS |
| `SPEC-1879` (tier gate) | `test_starter_tier_blocked_without_sending_sms` | yes | PASS |
| `SPEC-1879` / `SPEC-1686` (hashed storage) | `test_send_sms_stores_hashed_code_not_plaintext` | yes | PASS |
| `SPEC-1879` (successful verify) | `test_verify_sms_success_consumes_token` | yes | PASS |
| `SPEC-1879` (replay / lockout) | `test_verify_sms_already_used_returns_false`, `test_verify_sms_locked_after_max_attempts` | yes | PASS |
| `GOV-10`, `SPEC-1649`, `GOV-12`, `GOV-13` | targeted pytest (cwd Agent_Red) | yes | PASS 10/10 |
| `SPEC-CODE-QUALITY-CHECKLIST-001` | ruff check + ruff format --check | yes | PASS |

## Verification Evidence

```text
cd applications/Agent_Red
python -m pytest tests/unit/test_spec1879_phone_identity_coverage.py -q --tb=short
# 10 passed in 0.34s

python -m ruff check tests/unit/test_spec1879_phone_identity_coverage.py
# All checks passed!

python -m ruff format --check tests/unit/test_spec1879_phone_identity_coverage.py
# 1 file already formatted
```

Implementation-start packet: `agent-red-wi3212-phone-identity-sms-otp-coverage`
(session `2026-06-25T04-52-00Z-prime-builder-E-f7a3b2`).

## Loyal Opposition Verification Request

Independent **VERIFIED** in a separate session context. Re-run targeted pytest and
ruff above from `applications/Agent_Red` cwd.
