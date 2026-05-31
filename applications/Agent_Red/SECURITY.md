# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Agent Red, please report it responsibly.

**Email:** security@remakerdigital.com

Please include:
- Description of the vulnerability
- Steps to reproduce
- Impact assessment
- Any suggested fixes

## Response Timeline

- **Acknowledgment:** Within 48 hours
- **Initial assessment:** Within 5 business days
- **Resolution target:** Based on severity (P0: 24h, P1: 72h, P2: 2 weeks, P3: next release)

## Scope

This policy covers the Agent Red platform including:
- API Gateway and backend services
- Chat widget (embedded on merchant sites)
- Admin dashboards (Shopify, standalone, provider)
- Azure infrastructure configuration

## Out of Scope

- Third-party services (Azure, Shopify, Stripe) — report to those vendors directly
- Social engineering attacks against team members
- Denial of service attacks

## Security Practices

Agent Red implements:
- Per-tenant AES-256-GCM envelope encryption with Azure Key Vault HSM-backed keys
- Managed identities for all service-to-service authentication
- Pre-authentication rate limiting
- Input and output sanitization
- Append-only audit logging
- Dependency vulnerability scanning in CI (pip-audit)
- No hardcoded secrets policy with automated guardrail enforcement

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
