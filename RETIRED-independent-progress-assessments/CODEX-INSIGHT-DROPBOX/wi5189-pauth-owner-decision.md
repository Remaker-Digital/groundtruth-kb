## Owner Decision

Approve exact WI-5189 PAUTH text.

## Approved Scope

Authorize only the document-authoritative GO-implementation claim-role repair
in `scripts/bridge_work_intent_registry.py` and its focused regression tests in
`platform_tests/scripts/test_work_intent_role_eligibility.py`.

The repair must admit only a validated current Prime Builder worker session
document, deny every invalid or non-Prime document, and remove role-authorization
dependence on dispatcher/default configuration and role-marker data.

## Exclusions

Do not change dispatcher configuration, harness identity or role maps, routing,
selection, provider behavior, credentials, deployment, unrelated files, or
automatic production tuning. An independent Loyal Opposition GO, matching
work-intent claim, and implementation-start authorization remain mandatory.
