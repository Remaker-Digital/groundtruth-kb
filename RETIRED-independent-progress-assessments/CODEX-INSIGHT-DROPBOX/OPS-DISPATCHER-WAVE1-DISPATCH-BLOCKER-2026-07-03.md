Claim: Wave 1 OPS dispatcher modernization remains blocked on Loyal Opposition verification dispatch, not on Prime Builder implementation scope.

Generated: 2026-07-03T01:00Z
Author: Codex Prime Builder, harness A
Parent project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION
Wave work items: WI-4960, WI-4957, WI-4958, WI-4959

## Current Wave State

- WI-4960 is terminal by bridge verification: `bridge/gtkb-dispatcher-portfolio-reconciliation-006.md` latest `VERIFIED`.
- WI-4958 is terminal by bridge verification: `bridge/gtkb-dispatch-lane-scoring-registry-projections-006.md` latest `VERIFIED`; exact-target amendment latest `VERIFIED` at `bridge/gtkb-dispatch-lane-scoring-registry-projections-exact-target-amendment-004.md`.
- WI-4957 implementation is filed but not LO-terminal: `bridge/gtkb-ops-lifecycle-protocol-foundation-011.md` latest `NEW`.
- WI-4959 implementation reports are filed but not LO-terminal:
  - `bridge/gtkb-auq-headless-hook-launch-hygiene-003.md` latest `NEW`.
  - `bridge/gtkb-auq-headless-hook-launch-hygiene-exact-target-amendment-003.md` latest `NEW`.

## Evidence

- `gt projects show PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION --json` showed the project active with WI-4960/WI-4957/WI-4958 resolved in MemBase and WI-4959 still open/backlogged; bridge latest state remains authoritative for unverified implementation reports.
- `python scripts/verify_ollama_dispatch.py --readiness-only --json` passed after local model inventory was restored.
- `python scripts/ollama_harness.py -p "...Dispatch smoke probe..." --skill bridge-review --model deepseek-v4-pro-cloud --timeout 30 --session-timeout 45` returned `OK`.
- Required Ollama inventory is now present: `deepseek-v4-pro:cloud`, `kimi-k2.6:cloud`, `kimi-k2.7-code:cloud`, `qwen3-coder-next:cloud`, and `qwen3.6:latest`.
- `gt bridge dispatch reset --soft --json` cleared stale recipient/runtime dispatch state; `gt bridge dispatch daemon start --interval 15` restarted the dispatcher daemon.
- LO worker `2026-07-03T00-53-26Z-loyal-opposition-D-44cc3c` selected `gtkb-ops-lifecycle-protocol-foundation` and exited nonzero. Its stderr was: `ollama_harness: Ollama chat request timed out before retry`.
- LO worker `2026-07-03T00-53-43Z-loyal-opposition-D-177e60` selected `harness-equivalence-phase-3-umbrella` and exited nonzero with the same timeout.
- `.api-harness/routing.toml` sets `[routing.ollama] timeout_seconds = 180`, so `scripts/ollama_harness.py` derives a 240 second session budget for dispatched bridge-review work.
- A draft LO verdict was written at `bridge/harness-equivalence-phase-3-umbrella-004-draft.md`, but `gt bridge show harness-equivalence-phase-3-umbrella --json` still reports latest status `NEW` at `bridge/harness-equivalence-phase-3-umbrella-003.md`. The draft is not a canonical versioned bridge response.

## Risk / Impact

- Wave 1 cannot reach governed terminal state while latest `NEW` implementation reports fail LO dispatch before a canonical `VERIFIED` or `NO-GO` file is written.
- The dispatcher currently records terminal-reconciliation evidence for a noncanonical `*-draft.md` verdict, while bridge-state helpers still correctly report the source thread as latest `NEW`. That creates a state split between runtime dispatch bookkeeping and the status-bearing file chain.
- Raising route timeouts or changing harness routing would touch protected configuration and requires a matching bridge GO and work-intent claim. No protected source/config/test mutation was performed for this blocker note.

## Architecture Alignment Ledger

- OPS consolidation: the build envelope preserved the bridge/file-chain authority boundary and did not treat runtime dispatcher bookkeeping as authoritative over status-bearing bridge files.
- Dispatcher daemon architecture: runtime recovery used governed dispatcher commands (`status`, `reset --soft`, `daemon start`) and did not edit daemon/runtime implementation directly.
- Lifecycle-first/scoring-last precedence: no lane-scoring changes were made to bypass lifecycle gates; latest bridge status remains the gate for PB/LO actionability.
- Portfolio reconciliation: WI-4960 findings remain the control lane; stale/overlapping state was checked before treating WI-4957 MemBase resolution as terminal.

## Recommended Action

Open or route a governed follow-up for the LO dispatch timeout/draft-finalization problem before further protected config/source changes:

- Either adjust the Ollama bridge-review session budget through an approved config/source slice, or route Wave verification to a harness/provider whose bridge-review path can complete within the current budget.
- Ensure headless LO verdict filing writes the canonical next versioned bridge file, not only `*-draft.md`, before dispatcher runtime reconciliation marks a document terminal.

Decision needed from owner: none at this moment. This is a governed-dispatch blocker record; any protected repair must come through the bridge with a live GO and work-intent claim.
