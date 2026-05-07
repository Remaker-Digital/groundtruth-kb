---
sidebar_position: 19
title: Securing Agent Red
description: Authentication, multi-factor options, account recovery, and key handling for the Agent Red admin console.
---

# Securing Agent Red

Agent Red admin access is protected with API keys, optional two-factor verification, and role-based permissions.

## Authentication overview

| Method | Who can use it | Typical use |
|---|---|---|
| API key | All admin-console users | Primary sign-in method |
| Magic link | Registered admin-console users | Passwordless sign-in fallback |
| SMS verification (optional) | Team members with MFA enabled | Additional login protection |

---

## API key authentication

Every team member receives a unique API key when invited. Keys are scoped to that user and role.

1. Open the admin login page.
2. Enter your API key.
3. Continue into the console with permissions for your role.

:::warning Protect your API key
Treat your API key like a password. Do not share it in chat, email, screenshots, or source code.
:::

### If a key is compromised

1. Ask an admin to regenerate the affected key from **Team management**.
2. Remove or revoke any inactive team members.
3. Review recent admin activity and escalations.

---

## Magic link authentication

Magic links provide passwordless login for registered team members.

1. Click **Sign in with magic link**.
2. Enter your registered email address.
3. Open the email and click the one-time link.

Magic links expire quickly and can only be used once.

---

## Optional SMS two-factor verification

Admins can enable SMS-based two-factor verification for team members.

1. Open **Team management**.
2. Enable MFA for the target member.
3. Register and verify a phone number.

When enabled, sign-in requires:

1. API key authentication.
2. A one-time SMS verification code.

Repeated invalid attempts are rate-limited and may temporarily lock the challenge flow.

---

## Account recovery

If a team member loses access:

1. An admin can regenerate that member's API key.
2. The member can use magic link login if their email is still accessible.
3. If both key and email access are unavailable, update the member record and issue a new key.

---

## Security best practices

1. Store keys in a password manager.
2. Enable MFA for privileged users.
3. Remove access immediately when team membership changes.
4. Use least privilege when assigning roles.
5. Rotate keys whenever compromise is suspected.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
