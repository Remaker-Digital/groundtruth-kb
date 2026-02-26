---
sidebar_position: 19
title: MFA & Security
---

# Multi-Factor Authentication

Agent Red supports TOTP-based two-factor authentication for Provider admin accounts, adding an extra layer of security beyond API key authentication.

## Setting up MFA

1. Navigate to **Account → MFA Settings** in the Provider console.
2. Click **Enable MFA** to generate a TOTP seed.
3. Scan the QR code with your authenticator app (Google Authenticator, Authy, 1Password, etc.).
4. Enter the 6-digit code from your authenticator to verify setup.
5. Save your **10 backup codes** in a secure location.

## Login flow

With MFA enabled, the Provider console uses a three-state authentication flow:

1. **API key login** — enter your provider API key.
2. **MFA challenge** — enter the 6-digit TOTP code from your authenticator app.
3. **Authenticated session** — access the full Provider console.

Sessions last 8 hours. After expiry, you'll need to re-authenticate.

## Backup codes

During MFA setup, you receive 10 single-use backup codes. Each code can only be used once. Use a backup code if you lose access to your authenticator app.

To regenerate backup codes, disable and re-enable MFA from the MFA Settings page.

## SMS-based 2FA for team members

In addition to Provider console TOTP, tenant admin team members can enable SMS-based two-factor authentication for an extra layer of account security.

### How it works

1. Navigate to **Team** in the sidebar.
2. Select your team member profile or ask an admin to enable MFA on your account.
3. Register your phone number.
4. Verify via a one-time SMS code.

After enrollment, logging in requires two steps:

1. **API key login** — enter your API key as usual.
2. **SMS challenge** — enter the 6-digit code sent to your registered phone number.

### MFA management

Admins can manage MFA settings for all team members:

| Action | Description |
|--------|-------------|
| **Check status** | View whether a team member has MFA enabled, enrolled, and phone verified |
| **Grant opt-out** | Allow a team member to bypass MFA (for members who cannot use SMS) |
| **Revoke opt-out** | Remove the opt-out exemption, requiring MFA enrollment |
| **Disable** | Turn off MFA for a team member |

### Brute-force protection

Failed 2FA attempts are tracked. After repeated failures, the account is temporarily locked with exponential backoff to prevent unauthorized access.

---

## Magic link authentication

For tenant admin team members, Agent Red offers passwordless login via magic links:

1. Click **Sign in with magic link** on the login page.
2. Enter your registered email address.
3. Check your inbox for the magic link email.
4. Click the link to be automatically authenticated.

Magic links expire after 15 minutes and can only be used once. Magic link sessions now correctly identify the team member who clicked the link, preserving their role and permissions throughout the session.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
