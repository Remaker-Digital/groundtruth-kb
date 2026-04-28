# Email — Operational Lessons

> Full architecture: KB DOC-EMAIL

## ACS domain configuration (S85-S86)
ACS requires sender domain linked before sending. The module-level `SENDER_ADDRESS` and class-level `SENDER_ADDRESS` must both point to the Azure managed domain. A branding session changed only one — always change both.

## ACS 429 hourly rate limit (S86)
Azure Managed Domains have very low hourly quotas (~10/hour). SDK's default `RetryPolicy` honours the `retry-after` header (3703s = 62 min), blocking the request. Fix: `RetryPolicy(retry_total=2, retry_backoff_factor=1, retry_backoff_max=5)` and catch `HttpResponseError` 429.

## ACS poller.result() timeout (S85)
Azure SDK LRO `poller.result()` defaults to `timeout=None` (indefinite wait). Always pass explicit timeout: `poller.result(timeout=60)`.

## Titan SMTP silent drops on Azure (S86)
Titan accepts at SMTP level (`250 Ok: queued`) even when rate-limited, then silently drops. Triggered by 7+ sends in 5 minutes. Pod rotation resolves. For testing, space sends 2-3 min apart.

## SMTP From address standardization (S86)
All SMTP paths use `SMTP_FROM` env var (not `SMTP_FROM_ADDRESS`, not `EmailAlertChannel.SENDER_ADDRESS`). Falls back to `SMTP_USERNAME`.

## Email SVG incompatibility (S82)
Gmail and Outlook block `<img src="...svg">`. All email templates must use PNG.

## Email image cache busting (S86)
Outlook aggressively caches images. Append version query param (e.g., `?v=2`) when updating hosted email logos.
