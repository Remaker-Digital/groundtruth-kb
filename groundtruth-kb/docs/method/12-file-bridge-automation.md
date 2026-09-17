# 12. Native bridge coordination

GT-KB coordinates agent-authored work through the ordinary CLI and canonical
domain services. Bridge payloads are transient messages; attempt, claim, review
and terminal facts remain recoverable without them. A message is authoritative
at receipt and has no continuing authority. It is not a durable specification,
owner decision, project-authorization record or Git-completion fact.

## Current operation

The owner selects work until Dispatcher Next is independently qualified and
activated. Dispatcher Next design does not activate it. Do not install or restore
a retired dispatcher, poller or watchdog as a fallback. A scheduled-task label,
heartbeat, file age or source test does not prove dispatch or host qualification.

Harnesses consume their own mechanically derived configuration and interact only
through CLI/domain services and bridge/dispatcher. No peer configuration, runtime
state, prompt exchange or direct harness contact coordinates work. Configuration
and invocation details belong to the existing registered sources; an inventory
or diagnostic report is not a second editable control plane.

## Read, claim, deliver

Use `gt context work-item <WI-ID> --json` for current work and
`gt bridge show <document> --content --json` for the assigned attempt. Revalidate
formal requirements, one parent project, tests, prerequisites and registered
checkout at the required boundary.

The native claim atomically binds full predecessor retrieval to one exact next
artifact: document, predecessor digest, next version, intended status, claimant,
fence, idempotency identity and fixed expiry. Delivery consumes the claim in the
same transaction. Expiry or exact release ends an undelivered claim; a retry
cannot extend it. A successor obtains a fresh claim from current state, with no
work-item tenure or requirement that an earlier author return.

Only agents author proposals, reports and verdicts. The service validates the
complete authored routing and bytes; it never repairs a header or invents a
verdict. The harness transports the work and checks the exact assigned delivery
through `gt bridge check-delivery`; final model prose alone is incomplete.

| Current response | Role receiving work |
| --- | --- |
| NEW, REVISED, READY, VERDICT-REJECTED | Loyal Opposition |
| GO, NO-GO, NOT-READY | Prime Builder |
| ADVISORY, BLOCKED, VERIFIED, WITHDRAWN, SUPERSEDED | No agent dispatch from the status alone |

Use the current native bridge skill and formal transition contract for the
permitted next response. An owner assignment may select fresh independent
verification from canonical failure/change state without inserting a dispatcher
verdict. Delivery, dispatch, verification and commitment are distinct facts.

## Recovery and evidence

On unavailable authority or a refused action, preserve bytes and inspect the
specific canonical error and recovery route. Do not create another queue, repair
an author's message, inherit a stale fence or switch to raw storage. Inspect an
uncertain delivery before retrying. Diagnose the exact running process before
restarting it; an observation timeout does not establish termination.

Recover an abandoned or irreparable attempt through the supported native restart
route and current formal facts. It grants no inherited GO or claim. Preserve
unrelated work. After the complete project commit, purge disposable bridge
payloads and retain only the minimal non-content anti-replay/terminal attribution
facts; Git supplies the committed work product and backups provide recovery.

Qualification must exercise actual invalid/valid delivery, concurrent successor
contention, failed-delivery rollback, fixed expiry, stale fences, independent
review, exact Git mode/object identity, complete-project commitment, failed-commit
recovery and payload-free canonical recovery. Actual-host fresh/successor work and
independent Dispatcher Next design review remain separate requirements.

See [independent review](06-dual-agent.md) and [project completion](14-lifecycle.md).
Formal retrieval: GOV-FILE-BRIDGE-AUTHORITY-001, DCL-BRIDGE-CLAIM-LIFECYCLE-001,
DCL-SESSION-ROLE-RESOLUTION-001, GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001.
