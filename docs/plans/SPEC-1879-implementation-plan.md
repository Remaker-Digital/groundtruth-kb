# SPEC-1879: Phone Identity Channel — Implementation Plan

**Canonical spec:** `docs/specs/SPEC-1879-phone-identity-channel.md`
**This plan:** `docs/plans/SPEC-1879-implementation-plan.md`

## Scope

Phone as **verified contact method** (v1), NOT full phone-primary identity. Narrower scope per Codex recommendation.

**Phase 1 does not implement canonical phone-linking or new merge semantics under ADR-004.** ADR-004 remains under Loyal Opposition NO-GO for first-writer-wins duplicate-claim resolution. Phase 1 is additive groundwork only: schema fields, E.164 validation, and SMS OTP endpoints. ContactAttribute(PHONE) linkage to canonical profiles is deferred to a later phase pending ADR-004 resolution.

## Phase 1: Additive Groundwork (Schema + SMS OTP Endpoints)

### Phase 1 File Manifest

| # | File | Change Type | Description |
|---|------|-------------|-------------|
| 1 | `src/multi_tenant/cosmos_schema.py` | Extend | Add `identity_phone`, `identity_sms_sent_at`, `identity_sms_attempts` to ConversationDocument |
| 2 | `src/chat/models.py` | Extend | Add `phone: str \| None` to VisitorIdentity |
| 3 | `src/multi_tenant/widget_otp_verification.py` | Extend | Add `POST /api/chat/otp/send-sms` + `POST /api/chat/otp/verify-sms` endpoints |
| 4 | `src/multi_tenant/admin_conversation_api.py` | Extend | Add `identity_phone` to conversation response models |
| 5 | `admin/shared/types/index.ts` | Extend | Add `identityPhone` to TypeScript types |

### Phase 1 Explicit Exclusions

- NO ContactAttribute(PHONE) linkage to canonical profiles
- NO CustomerRepository.link_attribute() calls
- NO find_or_create_by_attribute() for phone
- NO session/endpoint profile resolution changes
- NO identity_preprocessor phone flow (Phase 2)
- NO widget PhoneOtpVerification component (Phase 3)

### Phase 1 Deliverables

1. **ConversationDocument fields** (cosmos_schema.py):
   - `identity_phone: str | None` — phone collected in-conversation or pre-chat
   - `identity_sms_sent_at: str | None` — ISO 8601 timestamp of last SMS OTP send
   - `identity_sms_attempts: int` — rate limit counter (max 3 per conversation)

2. **VisitorIdentity phone field** (models.py):
   - `phone: str | None` — optional phone from pre-chat form

3. **SMS OTP endpoints** (widget_otp_verification.py):
   - `POST /api/chat/otp/send-sms`:
     - E.164 validation (`^\+[1-9]\d{1,14}$`)
     - Professional+ tier gate
     - Rate limit: 3 per 5 min per IP
     - Hash code (SHA-256 via sms_verification.hash_code()) before storage
     - Token ID: `otp:{tenant_id}:{phone}`, token_type: `widget_otp_sms`
     - 10-minute TTL
     - Send via SmsVerificationService.send_code()
   - `POST /api/chat/otp/verify-sms`:
     - Constant-time hash comparison
     - Single-use token consumption
     - Generate customer token with `phone` + `identity_type: "phone"` payload
     - **Does NOT link ContactAttribute** — returns verified token only

4. **Admin API** (admin_conversation_api.py):
   - Add `identity_phone` to conversation list/detail response models

5. **TypeScript types** (admin/shared/types/index.ts):
   - Add `identityPhone?: string` to conversation types

### Phase 1 Reuse (no new modules)

- `SmsVerificationService.send_code()` from `src/multi_tenant/sms_verification.py`
- `hash_code()` from `src/multi_tenant/sms_verification.py`
- `VerificationTokenRepository` from existing token collection
- `get_rate_limit_backend()` for request throttling

### Phase 1 Security Requirements

- [x] E.164 normalization before OTP send
- [x] Hashed token storage (SHA-256, not plaintext)
- [x] 10-minute TTL on verification tokens
- [x] Request throttling (3 per 5 min per IP)
- [x] Single-use token consumption
- [x] Professional+ tier gate
- [x] No plaintext code storage

## Phase 2: Identity Preprocessor Phone Flow (future, pending Phase 1 GO)

| File | Change |
|------|--------|
| `src/chat/identity_preprocessor.py` | Phone extraction + SMS OTP in-conversation flow |
| `src/chat/session.py` | Profile resolution: customer_id > email > phone |
| `src/chat/endpoints.py` | X-Customer-Phone-Token header, cache warmup |
| `src/multi_tenant/customer_profile_service.py` | Phone in asserted_identity enrichment |

## Phase 3: Widget Phone OTP Component (future)

| File | Change |
|------|--------|
| `widget/src/components/PhoneOtpVerification.tsx` | **NEW** — phone OTP UI |
| `widget/src/state/store.ts` | customerPhone, customerPhoneToken |
| `widget/src/transport/http.ts` | sendPhoneOtp(), verifyPhoneOtp() |
| `widget/src/components/PreChatForm.tsx` | Add 'phone' to allowed field types |
| `widget/src/components/Panel.tsx` | Phone OTP routing |
| `widget/src/locale/en.ts` | Phone OTP locale strings |

## Phase 4: Admin Display + Escalation Gate (future)

| File | Change |
|------|--------|
| `admin/standalone/pages/Inbox.tsx` | Phone display in inbox |
| `src/chat/pipeline/critic_escalation.py` | Phone-aware escalation gate |

## Codex Review Protocol

Each phase requires Codex GO before implementation begins. Post-implementation report sent after each phase.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
