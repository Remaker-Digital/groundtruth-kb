---
sidebar_position: 19
title: Securing Agent Red
description: Authentication, multi-factor security, platform admin management, login notifications, backup recovery codes, and tenant account recovery.
---

# Securing Agent Red

Agent Red uses API key authentication with optional multi-factor security layers. This guide covers all security features available to both tenant admins and platform (SPA) administrators.

## Authentication overview

Agent Red uses two separate authentication domains:

| Domain | Who | How they log in | Console |
|---|---|---|---|
| **Tenant admin** | Store owners and their team members | API key or magic link | Standalone admin console |
| **Platform admin (SPA)** | Service provider administrators | SPA API key (prefix `ar_spa_`) | Provider admin console |

Each domain has its own security features. Tenant API keys start with `ar_user_` and are scoped to a single tenant. SPA keys start with `ar_spa_plat_` and have access to the provider-level management console.

---

## Tenant admin security

### API key authentication

Every team member receives a unique API key when invited. The key is tied to their email address and role.

1. Go to the standalone admin login page.
2. Enter your API key.
3. The console loads with pages and permissions matching your role.

:::warning Protect your API key
Your API key is equivalent to a password. Do not share it in emails, chat messages, or code repositories. If you believe your key has been compromised, ask an admin to regenerate it from the Team page.
:::

### Magic link authentication

For passwordless login, tenant team members can use magic links:

1. Click **Sign in with magic link** on the login page.
2. Enter your registered email address.
3. Check your inbox for the magic link email.
4. Click the link to be automatically authenticated.

Magic links expire after 15 minutes and can only be used once. The session preserves your role and permissions.

### SMS-based 2FA for team members

Tenant admin team members can enable SMS-based two-factor authentication:

1. Navigate to **Team** in the sidebar.
2. Select your team member profile or ask an admin to enable MFA on your account.
3. Register your phone number.
4. Verify via a one-time SMS code.

After enrollment, logging in requires two steps:

1. **API key login** — enter your API key as usual.
2. **SMS challenge** — enter the 6-digit code sent to your registered phone number.

**MFA management for admins:**

| Action | Description |
|---|---|
| **Check status** | View whether a team member has MFA enabled, enrolled, and phone verified |
| **Grant opt-out** | Allow a team member to bypass MFA (for members who cannot use SMS) |
| **Revoke opt-out** | Remove the opt-out exemption, requiring MFA enrollment |
| **Disable** | Turn off MFA for a team member |

**Brute-force protection:** Failed 2FA attempts are tracked. After repeated failures, the account is temporarily locked with exponential backoff.

---

## Platform admin (SPA) security

The Provider admin console has its own security model designed for service provider operations.

### TOTP multi-factor authentication

Platform admins can enable TOTP-based MFA for an extra layer of security:

1. Navigate to **Account → MFA Settings** in the Provider console.
2. Click **Enable MFA** to generate a TOTP seed.
3. Scan the QR code with your authenticator app (Google Authenticator, Authy, 1Password, etc.).
4. Enter the 6-digit code from your authenticator to verify setup.
5. Save your **10 backup codes** in a secure location.

With MFA enabled, the login flow becomes:

1. **API key login** — enter your SPA API key.
2. **MFA challenge** — enter the 6-digit TOTP code from your authenticator app.
3. **Authenticated session** — access the full Provider console.

Sessions last 8 hours. After expiry, you must re-authenticate.

### Platform admin user hierarchy

The SPA supports multiple administrators with two roles:

| Role | Access | Can manage users? |
|---|---|---|
| **Superadmin** | Full access to all SPA features including user management | Yes — can create and deactivate operators |
| **Operator** | Full access to SPA features except user management | No — cannot create or remove other admins |

The superadmin account is created automatically when Agent Red is provisioned. Additional operator accounts can be created by the superadmin.

#### Adding an operator

1. Navigate to **User Management** in the Provider console sidebar (under Account).
2. Click **Add Operator**.
3. Enter the operator's email address and display name.
4. Click **Create**. A new SPA API key is generated.
5. **Copy the API key immediately** — it is only shown once. Send it securely to the new operator.

#### Removing an operator

1. Navigate to **User Management**.
2. Find the operator in the table.
3. Click **Remove** and confirm.
4. The operator's API key is immediately invalidated.

:::info
The superadmin account cannot be deleted. You also cannot delete your own account.
:::

### Login notification emails

Every time a platform admin (superadmin or operator) logs in, an email notification is sent automatically. This provides an audit trail and early warning of unauthorized access.

**What the email contains:**

- Timestamp of the login
- IP address of the login source
- User agent (browser/client information)

**Notification email address:**

By default, login notifications are sent to the admin's account email. You can configure a different notification email address:

1. Navigate to **User Management**.
2. Click the **Notification Email** field for your account.
3. Enter the email address where you want login notifications sent (e.g., a shared security inbox).
4. Save.

Login notifications are non-blocking — if the email fails to send, login is not affected.

### Emergency key recovery with backup codes

If you lose your SPA API key, you can recover access using backup recovery codes.

#### Generating backup codes

1. Navigate to **User Management** in the Provider console.
2. Click **Generate Backup Codes**.
3. Eight recovery codes are generated and displayed.
4. **Save these codes immediately** — they are only shown once. Store them in a password manager or print them and keep them in a secure location.

Each code is a single-use 8-character hex string. After use, the code is consumed and cannot be reused.

#### Using a backup code to recover access

If you have lost your API key and cannot log in:

1. On the Provider console login page, click **Lost access? Use a backup code**.
2. Enter your **email address** and one of your **backup codes**.
3. Click **Recover**.
4. If the code is valid, a new API key is generated and sent to your email address.
5. Check your inbox for the new key and use it to log in.

:::warning
Each backup code can only be used once. After using a code for recovery, the remaining code count decreases. Generate new backup codes if your supply is running low.
:::

**Rate limiting:** Recovery attempts are limited to 3 per 15 minutes per IP address to prevent brute-force attacks. The response is always the same generic message regardless of whether the email/code combination was valid — this prevents account enumeration.

### SPA key regeneration

If you believe your API key has been compromised but you still have access:

1. Log in to the Provider console with your current key.
2. Navigate to **User Management** or use the key regeneration endpoint.
3. Click **Regenerate Key**.
4. A new key is generated immediately. The old key stops working.
5. **Copy the new key** — it is only shown once.

All key changes are logged as security events with an audit trail.

---

## Tenant account recovery (SPA-initiated)

Platform administrators can help tenants recover access to their admin console by activating a recovery email address.

### Setting up a recovery address

1. Navigate to the **Tenant Directory** in the Provider console.
2. Select the tenant that needs recovery assistance.
3. Click **Set Recovery Address**.
4. Enter the recovery email address (typically the store owner's email).
5. Save.

### Sending a one-time auth link

When a tenant contacts you because they cannot log in:

1. Navigate to the **Tenant Directory** in the Provider console.
2. Find the tenant and click **Send Auth Link**.
3. Confirm the action. A one-time authentication link is sent to the tenant's recovery email address.
4. The link expires after 15 minutes and can only be used once.

When the tenant clicks the link, they are authenticated directly into their admin console with superadmin access. From there, they can regenerate API keys for their team members.

---

## Security best practices

1. **Store API keys in a password manager.** Never share keys in plain text via email or chat.
2. **Enable MFA** for all platform admin accounts and encourage tenant team members to enable SMS 2FA.
3. **Generate backup codes** immediately after setting up your SPA account. Store them separately from your API key.
4. **Set a notification email** for SPA login alerts so you are aware of all access to the platform console.
5. **Review the Team page regularly.** Disable team members who no longer need access. Delete accounts for people who have left the organization.
6. **Rotate API keys** if you suspect unauthorized access. Both tenant widget keys and admin API keys can be regenerated without downtime.
7. **Use the principle of least privilege.** Assign the Viewer role (read-only) to team members who only need to monitor conversations and analytics. Use the Escalation agent role for team members who only handle escalated conversations.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
