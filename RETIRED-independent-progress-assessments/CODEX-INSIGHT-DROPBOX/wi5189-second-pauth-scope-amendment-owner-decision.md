## Owner Decision

Approve WI-5189 second PAUTH scope amendment for the four listed regression
test files.

## Approved Amendment

Extend the WI-5189 implementation authorization to include these test-only
fixtures:

- `platform_tests/scripts/test_dispatcher_runtime_work_intent.py`
- `platform_tests/scripts/test_implementation_authorization.py`
- `platform_tests/scripts/test_implementation_start_gate.py`
- `platform_tests/scripts/test_protected_mutation_guard.py`

Migrate their successful GO-implementation claim setup to create validated
worker-session documents. Preserve each fixture's existing assertion intent,
including dispatcher work-intent lifecycle, project authorization, the
implementation-start gate, and protected-mutation enforcement.

## Boundary

The canonical backlog and claim writer must derive the worker role exclusively
from the validated worker session document. Dispatcher data may confirm intent
but must not supply role authority. This amendment does not authorize changes
to dispatcher configuration, durable role or identity maps, routing, selection,
provider behavior, credentials, deployment, automatic production tuning, or
unrelated files. A fresh independent Loyal Opposition GO over the expanded
eight-path proposal, a matching work-intent claim, and implementation-start
authorization remain mandatory.

## Evidence

The approved four-path WI-5189 suite passes. Broader claim-registry regression
coverage still fails because these four legacy fixtures model successful
GO-implementation claims without validated worker-session documents. The
amendment is limited to migrating those positive fixtures to the approved
document-only authority contract.
