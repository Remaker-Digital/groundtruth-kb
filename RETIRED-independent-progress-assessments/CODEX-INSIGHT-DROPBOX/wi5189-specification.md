### Requirement

Every `go_implementation` claim MUST derive the acting worker role exclusively
from the validated `worker_role_provenance` carried by the exact current worker
session document. A claim is Prime-eligible only when that document resolves
the current session as `prime-builder`.

The document resolver MUST fail closed when the document is missing, malformed,
closed, ambiguous, keyed to a different session, internally inconsistent, or
contains an unsupported role. A document that resolves to `loyal-opposition`
MUST be denied. A valid document must be read-only during claim resolution.

Dispatcher/default role configuration, dispatch-ID role tokens, durable role
registry entries, vendor identity, shared role markers, and per-session role
markers MAY be retained as routing or audit evidence but MUST NOT contribute to
worker-role authorization for a claim. A dispatch event confirms dispatcher
intent; it cannot supply or override the worker role. The persisted claim's
`acting_role` MUST equal the validated document role.

### Scope

This requirement applies only to work-intent claim role authorization and
claim-record attribution. It does not authorize changes to dispatcher
configuration, harness identities or roles, dispatch eligibility, selection,
routing, provider invocation, credentials, deployment, or any unrelated
writer.

### Acceptance Criteria

Automated tests MUST prove all of the following:

1. A Prime Builder session document permits a GO-implementation claim even
   when a stale or conflicting marker says Loyal Opposition.
2. A Loyal Opposition document denies a GO-implementation claim even when a
   marker, dispatch token, or registry entry suggests Prime Builder.
3. Missing, malformed, closed, ambiguous, mismatched, or internally
   inconsistent documents deny the claim without creating or replacing a claim
   record.
4. The claim records the same acting role carried by the validated document.
5. Claim role resolution makes no role-authorization read from dispatcher
   configuration, durable role registry, shared marker, or per-session marker.
6. Existing non-GO drafting claims and bounded GO-claim timing behavior remain
   unchanged.
