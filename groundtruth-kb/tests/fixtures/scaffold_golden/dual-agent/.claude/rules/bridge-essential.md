# Bridge Is Essential

## The Mandate

Bridge uptime is the top-priority task.

The Prime↔Loyal Opposition bridge coordinates implementation proposals, reviews,
and verification. Keep the bridge visible and operational at all times.

## Bridge Readiness

Run `gt project doctor` to verify bridge readiness at any time.

Bridge scheduler commands are not implemented in this release.
Configure your OS-level bridge scanner and run `gt project doctor` to verify bridge readiness.

## Visibility Contract

Every response from Prime Builder should include a bridge status note showing
the bridge INDEX was checked and any actionable entries were processed.

## Incident Response

If the bridge becomes unresponsive:
1. Check `bridge/INDEX.md` for stale NEW or REVISED entries
2. Verify scanner logs for recent activity
3. Run `gt project doctor` to confirm bridge file readiness
4. Restart scanner if necessary — document the restart reason

## Invariants

- Never reprocess VERIFIED entries
- Use a lock file to prevent overlapping scanner runs
- Never delete bridge files — they form the audit trail
- Document scanner configuration in BRIDGE-INVENTORY.md
- The index is the source of truth for workflow state
