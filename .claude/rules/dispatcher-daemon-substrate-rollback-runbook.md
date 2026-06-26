# Dispatcher daemon substrate rollback runbook (WI-4848 slice 3c)

Use this runbook when rolling back from `dispatcher_daemon` to the transitional
cross-harness trigger substrate. **Do not** edit `harness-state/bridge-substrate.json`
manually — use the governed transaction only.

## When to roll back

- Live daemon substrate is active but dispatch health is failing after go-live.
- Owner-directed rollback during cutover rehearsal or incident response.
- Doctor reports substrate/daemon mismatch (see `gt doctor`).

## Preconditions

- Dispatch should remain **quiesced** (`can_receive_dispatch=false`) unless the
  owner explicitly re-enables harness dispatchability as part of a deliberate go-live.
- Confirm current substrate: `gt bridge dispatch status` and read
  `harness-state/bridge-substrate.json` (observation only).

## Rollback procedure

1. **Governed substrate switch** (required):

   ```powershell
   gt mode set-bridge-substrate --substrate cross_harness_trigger --reason "owner rollback from dispatcher_daemon"
   ```

   Use `--defer-to-next-session` only when mid-session deferral is intentional.

2. **Verify dispatch surfaces**:

   ```powershell
   gt bridge dispatch health
   gt bridge dispatch daemon status --json
   ```

3. **Optional daemon stop** (documented only; not automated here): stop the
   dispatcher daemon process if the owner wants shadow-only daemon ticks while
   on `cross_harness_trigger`.

## Post-rollback expectations

- Cross-harness trigger hooks resume dispatch decisions when dispatch is re-enabled.
- Daemon may continue in shadow mode recording decisions without spawning.
- Re-go-live requires owner approval: substrate flip + dispatch re-enable.

## References

- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `.claude/rules/operating-role.md` (governed substrate changes)
