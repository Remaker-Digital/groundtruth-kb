# Configuration Compliance — Operational Lesson

> Full reference: KB DOC-CONFIG-COMPLIANCE

## fields.yaml max_length for data URI fields (S84)
Any field storing base64 data URIs needs max_length ≥400000. Avatar upload stores inline data URIs (~43KB for 32KB PNG, up to ~350KB). Validation silently rejects → generic 500. Discovered on `widget_agent_avatar_url` (was 500, fixed to 400000).
