# Protected Behaviors Registry

**Purpose:** This file lists behaviors that MUST exist in the codebase and MUST NOT be removed, modified, or weakened without explicit owner approval in the current session. Every entry has a machine-verifiable assertion that is checked by the Build & Deploy procedure's Phase 0 regression gate.

**Rule:** If something in this file looks wrong or unnecessary, ASK the owner — do not act. The absence of documentation for a behavior means "I don't know its purpose" — not "it has no purpose."

**Maintenance:** When a protected behavior is added, modified, or intentionally retired, update this file AND the regression gate script. Only the owner may retire a behavior.

---

## How to Read Each Entry

```
### PB-NNN: Short title
- **Behavior:** What must happen
- **File(s):** Where it is implemented
- **Assert:** grep/test command that must pass (exit 0) for the build to proceed
- **Added:** Date and reason
```

---

## UI Behaviors

### PB-001: Widget displays on admin console when Active
- **Behavior:** The tenant's chat widget bubble (red circle, bottom-right) MUST appear on the standalone admin console whenever `activationStatus?.is_active === true`. This is intentional — it serves as a live preview of the tenant's customer-facing chat agent.
- **File(s):** `admin/standalone/layouts/StandaloneLayout.tsx`
- **Assert:** `grep -c "injectWidget" admin/standalone/layouts/StandaloneLayout.tsx` → ≥1
- **Added:** 2026-02-25. Owner correction — behavior has existed since 1.0 across 30+ builds. Documented after uncontrolled memory loss incident (S95).

### PB-002: Favicon on standalone admin console
- **Behavior:** The standalone admin SPA must include an SVG favicon (`icon-master.svg`).
- **File(s):** `admin/standalone/index.html`
- **Assert:** `grep -c "icon-master.svg" admin/standalone/index.html` → ≥1
- **Added:** 2026-02-25. Beta feedback (Scott Carey, Fix #3).

### PB-003: Favicon on provider admin console
- **Behavior:** The provider admin SPA must include an SVG favicon (`icon-master.svg`).
- **File(s):** `admin/provider/index.html`
- **Assert:** `grep -c "icon-master.svg" admin/provider/index.html` → ≥1
- **Added:** 2026-02-25. Beta feedback (Scott Carey, Fix #3).

---

## Error Messages & User-Facing Text

### PB-010: User-friendly "no draft to activate" error
- **Behavior:** When a tenant attempts to activate with no draft config, the error message must say "Save your configuration first" — not the raw technical message "No draft to activate".
- **File(s):** `src/multi_tenant/activation_service.py`
- **Assert:** `grep -c "Save your configuration first" src/multi_tenant/activation_service.py` → ≥2
- **Added:** 2026-02-25. Beta feedback (Scott Carey, Fix #1).

### PB-011: Memory & Privacy tier-gated fields filtered on save
- **Behavior:** `MemoryPrivacy.tsx` must NOT send `pattern_learning_enabled` for Starter-tier tenants. Pro+ fields are conditionally included based on `isProOrHigher`.
- **File(s):** `admin/standalone/pages/MemoryPrivacy.tsx`
- **Assert:** `grep -c "isProOrHigher" admin/standalone/pages/MemoryPrivacy.tsx` → ≥1
- **Added:** 2026-02-25. Beta feedback (Scott Carey, Fix #2).

---

## Email & Notifications

### PB-020: Team invite email sent to invitee on member creation
- **Behavior:** When a team member is created via `POST /api/team`, an invitation email must be sent to the invitee's email address (not the tenant admin).
- **File(s):** `src/multi_tenant/admin_team_api.py`
- **Assert:** `grep -c "send_team_invite_alert" src/multi_tenant/admin_team_api.py` → ≥1
- **Added:** 2026-02-25. Beta feedback (Scott Carey). Owner directive: "Invitations to team members must be sent to their Email."

### PB-021: Team invite email includes admin dashboard link
- **Behavior:** The team invitation email must contain a link to the admin UI (`APP_BASE_URL/admin/standalone/`).
- **File(s):** `src/multi_tenant/alert_delivery.py`
- **Assert:** `grep -c "admin_url" src/multi_tenant/alert_delivery.py` → ≥2
- **Added:** 2026-02-25. Owner directive: "Invitations to team members must include a link to the administrator UI."

### PB-022: Re-send invitation endpoint exists
- **Behavior:** `POST /api/team/{member_id}/resend-invite` must exist so admins and superadmins can re-send invitation emails.
- **File(s):** `src/multi_tenant/admin_team_api.py`
- **Assert:** `grep -c "resend-invite" src/multi_tenant/admin_team_api.py` → ≥1
- **Added:** 2026-02-25. Owner directive: "it must be possible for administrators (and superadmin) to re-send invitations to team members."

### PB-023: Escalation email routes to assigned agent with superadmin fallback
- **Behavior:** Escalation notification emails must be sent to the assigned escalation agent's email. If no agent is assigned, the email goes to the superadmin. The tenant notification_email is the last fallback.
- **File(s):** `src/chat/pipeline/critic_escalation.py`, `src/multi_tenant/alert_delivery.py`
- **Assert:** `grep -c "find_superadmin_email" src/chat/pipeline/critic_escalation.py` → ≥1
- **Assert:** `grep -c "recipient_emails" src/multi_tenant/alert_delivery.py` → ≥3
- **Added:** 2026-02-25. Owner directive: "Superadmin must be the default receiver of all messages unless another team member is specified."

---

## Build & Deploy

### PB-030: VITE_API_URL must be empty at Docker build time
- **Behavior:** Admin SPAs must use same-origin relative URLs in Docker containers. `VITE_API_URL` must be cleared before building admin dist directories. The build procedure must verify with `grep -c "orangeglacier"` → 0.
- **File(s):** `docs/operations/build-deploy-procedure.md` (Step 1.0)
- **Assert:** `grep -c "VITE_API_URL" docs/operations/build-deploy-procedure.md` → ≥1
- **Added:** 2026-02-25. Root cause of staging login failure (S95). VITE_API_URL baked production FQDN into staging SPA.

---

## Protected Files (DO NOT MODIFY)

These files must not be edited under any circumstances:

- `branding/logo/SVG/icon-master.svg`
- `branding/logo/SVG/primary-logo-no-wordmark.svg`
- `branding/logo/PNG/icon-master.png`
- `branding/logo/PNG/primary-logo-no-wordmark.png`

---

## Retired Behaviors

_None yet. When a behavior is retired, move it here with the date and reason._

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
*Last Updated: 2026-02-25*
