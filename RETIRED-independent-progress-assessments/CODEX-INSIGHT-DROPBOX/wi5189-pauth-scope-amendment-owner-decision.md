## Owner Decision

Approve WI-5189 PAUTH scope amendment for the two listed test files.

## Approved Amendment

Extend the WI-5189 implementation authorization to include these test-only
fixtures:

- `platform_tests/scripts/test_work_intent_auto_extend.py`
- `platform_tests/scripts/test_bridge_work_intent_registry.py`

Migrate their GO-claim setup to create validated worker-session documents and
retain the document-only role-authority contract. Preserve the existing test
intent for bounded timing, claim exclusivity, project-role coordination,
implementation authorization ownership, and malformed bridge-status handling.

## Boundary

This amendment does not authorize changes to dispatcher configuration, durable
role or identity maps, routing, selection, provider behavior, credentials,
deployment, or production tuning. The existing independent Loyal Opposition
GO, matching claim, and implementation-start authorization remain mandatory.

## Evidence

The focused WI-5189 suite passes, while the broader verification commands fail
because these legacy fixtures still model marker-only or dispatch-token-only
GO-claim authority. The amendment is limited to correcting those fixtures.
