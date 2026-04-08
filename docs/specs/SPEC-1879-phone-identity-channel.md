# SPEC-1879: Phone Identity Channel — SMS OTP via Azure Communication Services

**Status:** specified (v3)
**Type:** requirement
**Tags:** INV-1, identity, phone, ACS, professional+
**Changed by:** S267
**Change reason:** Phase-scope requirements per Codex NO-GO (P1-1). Requirements now split into Phase 1 (active) and Later Phases (deferred) to eliminate contradictory sources of truth for the phase boundary.

## Description

Customers verify identity via SMS OTP through ACS as a parallel channel alongside email (v1 scope: verified contact method, not full phone-primary identity).

## Requirements

### Phase 1 — Additive Groundwork (Active)

1. E.164 phone normalization before any identity claim or canonical lookup
2. SMS OTP via existing SmsVerificationService (ACS) — not a parallel stack
3. Hashed token storage (SHA-256) with 10-minute TTL — reuse sms_verification.hash_code()
4. Request throttling (3 per 5 min per IP) — Phase 1 guard is IP-rate-limit only; per-conversation attempt throttling (3 per conversation) deferred to Phase 2
5. Single-use token consumption with constant-time hash comparison
6. Professional+ tier gate (starter tier blocked)
7. ConversationDocument schema fields (identity_phone, identity_sms_sent_at, identity_sms_attempts)
8. Admin API and TypeScript types include identity_phone (prep-only — no population path in Phase 1)

### Later Phases — Deferred (NOT active until phase-specific Codex GO)

9. ContactAttribute(PHONE, verified=True) linkage via existing CustomerRepository (requires ADR-004 resolution)
10. Widget pre-chat phone collection + PhoneOtpVerification component
11. In-conversation phone detection (identity_preprocessor.py) + SMS OTP flow
12. Admin inbox displays identity_phone when identity_email absent
13. Escalation gate accepts identity_phone OR identity_email (v1: email still required for escalation)
14. Phone customer_token issuance (requires reviewed phone-aware session/endpoint path)

## Security Boundary

SMS OTP provides weaker identity assurance than Shopify HMAC. Phone verification must not silently supersede stronger identity claims. Identity resolution priority: Shopify HMAC > email OTP > phone OTP.

## Dependencies

- ACS provisioning (ACS_SMS_FROM + AZURE_COMM_CONNECTION_STRING)
- ADR-004 ContactAttributeType.PHONE (exists in schema, but ADR-004 remains under Loyal Opposition NO-GO for first-writer-wins semantics)
- **Phase 1 constraint:** No canonical phone-to-profile linking until ADR-004 duplicate-claim resolution is fixed. Phase 1 is additive groundwork only (schema fields, OTP endpoints, E.164 validation). Canonical linking deferred to a later phase pending ADR-004 resolution.

## Scope Exclusions

- WhatsApp escalation (INV-2/SPEC-1880)
- Phone as primary replacing email
- Shopify phone passthrough
- Cross-channel profile merge
- Canonical phone-to-profile linking (deferred pending ADR-004)

## Affected Surfaces (20 files)

### Backend (Python)
| File | Change |
|------|--------|
| `src/multi_tenant/cosmos_schema.py` | ConversationDocument: identity_phone, identity_sms_sent_at, identity_sms_attempts |
| `src/chat/models.py` | VisitorIdentity: phone field |
| `src/multi_tenant/widget_otp_verification.py` | POST /api/chat/otp/send-sms, POST /api/chat/otp/verify-sms |
| `src/multi_tenant/admin_conversation_api.py` | identity_phone in response models |
| `src/chat/identity_preprocessor.py` | Phone extraction + SMS OTP flow |
| `src/chat/session.py` | Profile resolution: customer_id > email > phone |
| `src/chat/endpoints.py` | X-Customer-Phone-Token header, cache warmup |
| `src/multi_tenant/customer_profile_service.py` | Phone in asserted_identity enrichment |
| `src/chat/pipeline/critic_escalation.py` | Phone-aware escalation gate |

### Reuse (no changes needed)
| File | Role |
|------|------|
| `src/multi_tenant/sms_verification.py` | ACS SMS send + hash_code() |
| `src/multi_tenant/sms_mfa_service.py` | SMS OTP pattern reference |
| `src/multi_tenant/repositories/customer.py` | ContactAttribute linkage (deferred) |

### Frontend (TypeScript/Preact)
| File | Change |
|------|--------|
| `widget/src/state/store.ts` | customerPhone, customerPhoneToken |
| `widget/src/transport/http.ts` | sendPhoneOtp(), verifyPhoneOtp() |
| `widget/src/components/PhoneOtpVerification.tsx` | **NEW** — phone OTP UI |
| `widget/src/components/PreChatForm.tsx` | Add 'phone' to allowed field types |
| `widget/src/components/Panel.tsx` | Phone OTP routing |
| `widget/src/locale/en.ts` | Phone OTP locale strings |

### Admin
| File | Change |
|------|--------|
| `admin/shared/types/index.ts` | identityPhone type |
| `admin/standalone/pages/Inbox.tsx` | Phone display |

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
