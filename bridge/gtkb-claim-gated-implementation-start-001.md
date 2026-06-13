NEW
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: prime-interactive-claim-gate-filing
author_model: GPT-5 Codex coding agent
author_model_version: GPT-5 family; exact runtime build not exposed in session context
author_model_configuration: Codex desktop session; Prime Builder override; approval_policy=never
author_metadata_source: Codex Prime Builder session; .gtkb-state/bridge-author-metadata/current.json

# Claim-Gated Implementation-Start (SPEC-INTAKE-9cb2ee)

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-AUTO-SPEC-INTAKE-9CB2EE

target_paths: ["scripts/implementation_authorization.py", "scripts/implementation_start_gate.py", "platform_tests/scripts/test_implementation_authorization.py", "platform_tests/scripts/test_implementation_start_gate.py"]

## Summary

Make holding the GO-implementation work-intent claim a required precondition for
mutating a GO'd bridge thread's `target_paths`. Today GT-KB has two independent
concurrency primitives that are never wired together: the implementation
**authorization packet** (scopes a session to one GO'd thread's `target_paths`)
and the work-intent **claim** (a TTL mutual-exclusion lock on a thread slug). The
packet answers *"is this edit in scope?"* but NOT *"am I the only one editing?"*
Because a packet is minted from the GO, N sessions can each independently run
`begin --bridge-id X` against the same live GO and all receive a valid packet for
the same files. This slice closes that seam by adding a claim-holder check at the
two enforcement points the owner named: `implementation_authorization.py begin`
(early, friendly failure) and `implementation_start_gate.py` (the load-bearing
mutation gate).

## Problem / Evidence

The motivating incident was a live two-session source-edit collision on the
time-box implementation itself (the predecessor slice, `SPEC-INTAKE-be073a`,
bridge thread `gtkb-go-impl-claim-timebox`, now VERIFIED). Two Prime sessions
each held a valid authorization packet minted from the same GO and both edited
the same `target_paths`, producing conflicting work. The authorization packet
prevented out-of-scope edits but provided no mutual exclusion, so neither session
was blocked.

The work-intent claim registry (`scripts/bridge_work_intent_registry.py`) already
provides the missing mutual exclusion and is already enforced at *bridge-file
draft* time by `.claude/hooks/bridge-compliance-gate.py`
(`_bridge_work_intent_deny_reason`). It is simply not consulted at
*source-implementation* time. This slice extends the existing primitive to the
implementation boundary rather than inventing a new lock.

## Specification Links

- `SPEC-INTAKE-9cb2ee` — governing requirement: holding the GO-implementation
  claim is required before editing a GO'd thread's target paths (status
  `specified`, `type=requirement`).
- `SPEC-INTAKE-be073a` — predecessor: GO-implementation claims are time-boxed
  with deadline/grace (VERIFIED). This slice depends on its claim-kind/lapse
  semantics (`current_holder` returns `None` past grace).
- `GOV-RELIABILITY-FAST-LANE-001` — reliability fast-lane basis for the standing
  project authorization that covers this bounded defect fix.
- `.claude/rules/codex-review-gate.md` — § "Mechanical Implementation-Start
  Gate"; this slice strengthens that gate.
- `.claude/rules/file-bridge-protocol.md` — § "Mandatory Implementation-Start
  Authorization Metadata" and § "Mandatory Pre-Drafting Claim Step" (the claim
  primitive this slice extends to implementation).

## Prior Deliberations

- `INTAKE-5a61f299` — owner intake establishing this requirement
  (source_type=owner_conversation, outcome=owner_decision).
- `DELIB-20260667` — `gtkb-impl-start-gate-pretooluse-restore` (VERIFIED): the
  PreToolUse implementation-start gate this slice extends.
- `DELIB-20260645` — `gtkb-claude-code-session-id-env-var-gap` (VERIFIED): the
  session-id env-var membership fix; this slice reuses the resulting shared
  resolver so the claim and the gate agree on identity.
- `DELIB-20260625` — WI-4270 shared session-id resolver unification: source of
  `gtkb_session_id.BRIDGE_WORK_INTENT_ORDER`, reused here verbatim.
- Predecessor bridge thread `gtkb-go-impl-claim-timebox` (VERIFIED) — the
  time-box layer this builds on.
- No prior deliberation rejected a claim-gated implementation-start approach;
  this slice is the next sequenced layer after the time-box.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Requirement Sufficiency

Existing requirements are sufficient for this scope. `SPEC-INTAKE-9cb2ee` fully
specifies the claim-gate behavior and `SPEC-INTAKE-be073a` supplies the claim
lifecycle it depends on; no new or revised requirement is needed before
implementation. This change performs no MemBase mutation — it adds only
read-only `current_holder` claim lookups.

## Design

### Identity resolution (reuse the existing, VERIFIED precedent)

The draft-time gate already solved the session-identity-duality problem in
`bridge-compliance-gate.py::_resolve_work_intent_session_id`: resolve env-first
via `gtkb_session_id.BRIDGE_WORK_INTENT_ORDER`, then fall back to the PreToolUse
payload `session_id`. The implementation-start gate will resolve identity the
same way, and `begin` (a CLI with no payload) will resolve via the shared
`resolve_session_id()` plus an optional `--session-id` override. This guarantees
the claim holder and the gate/`begin` challenger agree on identity, including the
headless-dispatch case where the worker resolves `GTKB_BRIDGE_POLLER_RUN_ID`.

### Shared helper (in `implementation_authorization.py`)

Add a small, importable helper that both enforcement points use, so identity +
holder logic lives in exactly one place:

- `resolve_work_intent_session_id(payload=None, *, environ=None)` — env-first via
  `BRIDGE_WORK_INTENT_ORDER`, then payload `session_id`. Delegates to
  `gtkb_session_id.resolve_session_id`.
- `work_intent_claim_block_reason(project_root, bridge_id, session_id)` →
  `str | None` — returns `None` when `session_id` holds the live claim for
  `bridge_id`; otherwise a clear, actionable reason string. Mirrors
  `_bridge_work_intent_deny_reason`'s 3-state logic (no session id → ask for one;
  no/lapsed holder → "claim first"; holder is another session → "claimed by X").
  Bootstrap exemption: `bridge_id in BOOTSTRAP_BRIDGE_IDS` returns `None`.

`implementation_authorization.py` gains two stdlib-safe imports
(`bridge_work_intent_registry.current_holder`, `gtkb_session_id`); both are
local modules already used by the dispatcher, so no new dependency surface.

### Enforcement point 1 — `implementation_start_gate.py` (load-bearing)

`gate_decision()` currently calls `validate_targets(root, protected)` only for
its raise side-effect. Change it to capture the return value, extract the
authorizing packet's `bridge_id` (`result["packet"]["bridge_id"]`), resolve the
session id (env-first then payload fallback), and call
`work_intent_claim_block_reason`. If it returns a reason, emit the existing
`permissionDecision: deny` PreToolUse block with that reason appended. This is
where the collision is actually prevented: the second, unclaimed session is
blocked at edit time even though its packet is valid.

This does **not** break headless dispatch: the dispatcher acquires the claim
under `dispatch_id` (`_acquire_prime_work_intent_batch(..., session_id=
_work_intent_session_id(dispatch_id))`) and then sets
`env["GTKB_BRIDGE_POLLER_RUN_ID"] = dispatch_id` on the worker, so the worker's
env-resolved id equals the claim holder id. The gate passes for legitimate
workers and only bites a second, unclaimed session.

### Enforcement point 2 — `implementation_authorization.py begin` (early failure)

Add an optional `--session-id` to the `begin` subparser. In `main()`'s `begin`
branch (the interactive CLI path), after resolving the session id, call
`work_intent_claim_block_reason(root, bridge_id, session_id)`; on a non-`None`
reason, print the error and exit `2` **without** writing any packet. This gives
an early failure ("acquire the claim first") instead of discovery at first edit.

### Scope protection — NOT inside `create_authorization_packet`

The claim check is deliberately placed on the `begin` CLI branch and the gate,
**never inside `create_authorization_packet`**. That function is shared by
`issue_dispatch_authorization_packets`, which runs in the *trigger* process where
`GTKB_BRIDGE_POLLER_RUN_ID` is not yet the dispatch id — a claim check there would
false-block automated dispatch. Keeping the check out of the shared minting
function preserves the dispatcher and honors the owner's two-file scope.

### Lapse / TTL behavior (inherited from the time-box layer)

`current_holder` returns the holder only when `ttl_expires_at > now`; for a GO'd
thread `acquire` sets `ttl_expires_at = deadline + grace`. So a lapsed claim makes
`current_holder` return `None`, and the gate cleanly says "no claim, re-claim"
with no extra logic. The gate is kind-agnostic (holder-session match only),
mirroring the draft-time gate; the time-box layer governs the window.

### Registry-error policy (fail-closed, with rationale)

If the work-intent registry raises (`WorkIntentRegistryError`) the gate fails
**closed** (blocks with a clear reason), matching `bridge-compliance-gate`'s
existing registry-error handling and GT-KB's fail-closed governance bias. The
registry is the always-present root `groundtruth.db`, so "registry unavailable"
indicates a severe condition. `begin` likewise fails closed. Alternative
(fail-open when a valid packet already exists) is noted and rejected: it would
reopen the collision window precisely during the registry-degraded state.

## Files Expected To Change

- `scripts/implementation_authorization.py` — add `resolve_work_intent_session_id`
  + `work_intent_claim_block_reason` helpers; add `--session-id` to `begin`; call
  the block-reason check in the `begin` branch (fail-closed, exit 2). New imports:
  `bridge_work_intent_registry.current_holder`, `gtkb_session_id`.
- `scripts/implementation_start_gate.py` — capture `validate_targets` return;
  resolve session id (env-first + payload fallback); call
  `work_intent_claim_block_reason` on the authorizing packet's `bridge_id`; emit
  the deny block on a non-`None` reason.
- `platform_tests/scripts/test_implementation_authorization.py` — claim-gate unit
  tests for the helpers and the `begin` path.
- `platform_tests/scripts/test_implementation_start_gate.py` — claim-gate unit
  tests for `gate_decision` (held / not-held / other-session / lapsed / bootstrap
  / dispatch-id parity / registry-error fail-closed).

## Specification-Derived Verification

Spec-to-test mapping (each `SPEC-INTAKE-9cb2ee` clause maps to at least one test):

| Spec clause (SPEC-INTAKE-9cb2ee) | Test |
|---|---|
| Holding the claim is required before mutating a GO'd thread's target_paths | `test_gate_blocks_mutation_when_claim_not_held`, `test_gate_allows_mutation_when_claim_held` |
| The holder must be THIS session | `test_gate_blocks_when_claim_held_by_other_session` |
| Lapsed claim is treated as not-held | `test_gate_blocks_when_claim_lapsed_past_grace` |
| `begin` fails closed without the claim | `test_begin_refuses_without_claim`, `test_begin_succeeds_with_claim` |
| Headless dispatch (dispatch_id) still authorized | `test_gate_allows_when_holder_is_dispatch_id` |
| Registry error fails closed | `test_gate_blocks_on_registry_error` |
| Bootstrap thread exempt | `test_claim_check_exempts_bootstrap_bridge_ids` |
| `create_authorization_packet`/dispatch packet issuance unaffected | `test_issue_dispatch_packets_does_not_require_claim` |

Verification commands (run against the changed files):

```
python -m pytest platform_tests/scripts/test_implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py -q --tb=short
python -m ruff check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py
python -m ruff format --check scripts/implementation_authorization.py scripts/implementation_start_gate.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py
```

## Risk / Rollback

- **Risk: false-block of a legitimate interactive Prime** whose env session id
  differs from the id it claimed under (the documented Claude session-id
  duality). Mitigation: the gate's payload-`session_id` fallback mirrors the
  already-VERIFIED draft-time gate; `begin` exposes `--session-id`. Net behavior
  matches the existing claim primitive operators already use.
- **Risk: breaking headless dispatch.** Mitigation: verified the dispatcher
  acquires the claim under `dispatch_id` and exports it as
  `GTKB_BRIDGE_POLLER_RUN_ID`; covered by `test_gate_allows_when_holder_is_dispatch_id`.
- **Risk: registry outage halts protected edits.** Accepted (fail-closed) per the
  Registry-error policy above; the registry is the always-present root DB.
- **Rollback:** revert the two source files; the new tests are additive. No
  schema change, no MemBase mutation, no migration. The work-intent registry and
  the authorization-packet shapes are untouched.

## Recommended Commit Type

`feat:` — adds a new enforcement capability (claim-required implementation-start)
across two scripts plus tests; not a pure repair of broken behavior.
