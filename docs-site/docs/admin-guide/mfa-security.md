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

## Magic link authentication

For tenant admin team members, Agent Red offers passwordless login via magic links:

1. Click **Sign in with magic link** on the login page.
2. Enter your registered email address.
3. Check your inbox for the magic link email.
4. Click the link to be automatically authenticated.

Magic links expire after 15 minutes and can only be used once.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
