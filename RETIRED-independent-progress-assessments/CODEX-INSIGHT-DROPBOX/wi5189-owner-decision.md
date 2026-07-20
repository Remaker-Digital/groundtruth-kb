## Owner Decision

Approve exact WI-5189 spec text.

## Approved Scope

Formalize the corrective requirement that GO-implementation claim authorization
derives the worker role exclusively from the exact current worker session
document and its validated `worker_role_provenance`. The repair is limited to
the work-intent claim implementation and its focused regression coverage.

## Exclusions

Do not change dispatcher configuration, durable role or identity maps,
dispatch selection, routing, provider behavior, credentials, deployment, or
unrelated work. Protected-source implementation still requires a separate
PAUTH, independent Loyal Opposition GO, matching work-intent claim, and
implementation-start authorization.
