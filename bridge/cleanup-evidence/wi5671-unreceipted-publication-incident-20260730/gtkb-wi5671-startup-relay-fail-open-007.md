REVISED
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 473984c5-2fd8-49a7-917e-00c997560e8f
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb
author_metadata_source: harness-session-context

# WI-5671 startup relay: durable detached refresh worker

bridge_kind: prime_proposal
Document: gtkb-wi5671-startup-relay-fail-open
Version: 007
Responds to: bridge/gtkb-wi5671-startup-relay-fail-open-006.md
Date: 2026-07-30 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY-WI-5671-SLICE-B-STARTUP-RELAY-FAIL-OPEN-DETACHED-BACKGROUND-REFRESH
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY
Work Item: WI-5671
target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py"]

implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Disposition — version 006 P1 is resolved by intervening tracked state

Version 006 raised exactly one P1 finding and no owner decision: the proposed
relay-parity assertion read `config/hooks/gtkb-workstream-focus.py`, which the
reviewing session found untracked, so a committed test depending on it would
fail in a clean checkout. Adding the wrapper would have mutated a third,
undeclared configuration path outside the exact two-path authorization.

**That finding was accurate when written and is no longer true at current HEAD.**

Verified provenance:

- `config/hooks/gtkb-workstream-focus.py` was added to version control in commit
  `db07f9dcfe7e7de8addc850729209278472cb0fe` ("Synching backlog"),
  authored `2026-07-24T18:34:04-07:00` (`2026-07-25T01:34:04Z`).
- The version 006 reviewing session context is `A-2026-07-24T23-52-15Z`
  (`2026-07-24T23:52:15Z`). The commit therefore landed approximately one hour
  and forty-two minutes **after** that review session opened.
- Current HEAD evidence: `git ls-tree --name-only HEAD -- config/hooks/` lists
  `config/hooks/gtkb-workstream-focus.py`; `git status --short -- config/hooks`
  returns no rows.

The version 006 verdict was correct review work that raced an unrelated
backlog-sync commit. The clean-checkout failure mode it identified no longer
exists, and no scope expansion is required to remove it: the wrapper became
tracked through separate committed work, so this slice still mutates only the
two declared target paths.

For completeness, the current project authorization already permits
"cross-harness parity surfaces if required by
`ADR-CODEX-HOOK-PARITY-FALLBACK-001`". The contingency the version 006 verdict
offered was therefore already authorized. This revision does not exercise it,
because it is not needed.

## Revision Disposition — hardened parity assertion

This revision satisfies the version 006 Required Revision directly, and then
strengthens it so the same defect class cannot recur silently.

The focused relay-parity assertion asserts behavior across the wrappers named
in the Required Revision — `.claude/hooks/workstream-focus.py`,
`.codex/gtkb-hooks/workstream-focus.cmd`, and
`.codex/gtkb-hooks/run_py_no_window.py` — all three of which are version
controlled at HEAD.

`config/hooks/gtkb-workstream-focus.py` is included **only behind an explicit
tracked-ness precondition assertion**. The test resolves each wrapper's tracked
state through `git ls-files --error-unmatch` before asserting on its contents.
If any wrapper is not tracked, the test fails with an explicit
"wrapper not version controlled" message naming the path, rather than reading a
file that a clean checkout would not contain.

That inverts the version 006 failure mode: an untracked wrapper now produces a
loud, self-describing test failure instead of a checkout-dependent one. The
assertion set can never again silently depend on untracked state.

## Revision Disposition — carried forward from versions 003 and 005

Versions 002 and 004 remain addressed and are not reopened:

- Version 002 correctly rejected the daemon-thread refresh: a daemon thread
  belongs to the short-lived UserPromptSubmit process and dies when that process
  exits. The design uses a durable detached child process. The current prompt
  never joins, renders, waits, or polls.
- Version 004 correctly rejected the global Codex hook-parity command as a green
  acceptance gate for this two-path slice. The global checker remains a recorded
  non-gating baseline; its current configuration failures remain separate
  remediation work and are not waived or described as green.

Both declared targets are clean at filing time
(`git status --short -- scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py`
returns no rows). No source or test mutation occurs through this filing.
Implementation requires fresh independent GO, the exact WI-5671 claim, and a
successful implementation-start packet.

## New Operational Evidence — first observed production manifestation

Slice B has now failed in live use, which was not available to versions 001-006.

On `2026-07-30T00:04:50Z` a fresh interactive Prime Builder session on harness B
issued `::init gtkb pb`. The relay found the PB disclosure cache
identity-intact and content-consistent with its metadata sidecar but past the
`STARTUP_RELAY_CACHE_MAX_AGE_SECONDS` TTL — precisely the
`consistent_except_freshness` condition this slice governs. The bounded
self-heal was abandoned at its 5-second budget and the relay **failed closed**
with `GTKB STARTUP RELAY FAILURE`, so no startup disclosure was presented and
the session could not satisfy `GOV-SESSION-SELF-INITIALIZATION-001` without
manual owner intervention.

Two contributing measurements were taken in that session against
`scripts/session_self_initialization.py --emit-startup-service-payload`:

| Run | Elapsed | `emit_latency_ms` | Resolved role |
| --- | --- | --- | --- |
| 1 | 48.9 s | 46000 | loyal-opposition (registry fallback) |
| 2 | 65.4 s | 58000 | prime-builder (init-keyword channel) |

`DELIB-202667181` (Slice A observability) measured a 35-39 second render against
the hard 5-second budget. The observed 46-58 second emit latency indicates the
gap has widened, and run 2 exceeded even the 55-second SessionStart hook budget,
which is why SessionStart itself also timed out in that session.

**This evidence is explicitly not a scope expansion.** Render-cost reduction is
excluded from this authorization and owned by WI-4564/FAB21. The measurements are
recorded here only because they confirm the Slice B premise: the gap between
render cost and the 5-second self-heal budget is widening, so a bounded
synchronous self-heal cannot be made to work by tuning, and the fail-open plus
durable detached refresh design is the correct remedy. Nothing in this revision
changes TTL policy, disclosure content, render cost, or cache schema authority.

The additional live probe cost observed in the same runs — Grafana health and
the dashboard URL each failing with `WinError 10061` against a 3-second timeout,
and `gh` unauthenticated — is likewise recorded as context only and remains
outside this slice.

## Durable Worker Design

### Parent hook path

Replace `_refresh_startup_relay_cache_bounded` with a fail-soft launcher. When
`_startup_relay_pointer` finds `consistent_except_freshness`, it captures the
validated stale pointer and invokes `subprocess.Popen` for a dedicated worker
mode in this same script:

```text
<sys.executable> <absolute workstream_focus.py> --startup-relay-refresh-worker
  --project-root <absolute root> --role-mode <pb|lo>
  --harness-name <resolved name> --harness-id <resolved id>
```

The command uses an argument vector with `shell=False`, `stdin/stdout/stderr`
set to `DEVNULL`, and `close_fds=True`. On Windows it uses
`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW`; on POSIX it
uses `start_new_session=True`. Spawn failure is recorded fail-soft and never
blocks the current prompt. The parent does not call `join`, `wait`, `poll`, or
the startup renderer.

### Worker mode and identity

The worker entry point accepts only the explicit root, role, harness name, and
harness ID above. It resolves the root, rejects an out-of-root cache target,
and verifies the supplied harness identity against the same canonical identity
reader used by the relay before rendering. A mismatch records `identity_error`
and exits without replacing any cache. It imports
`session_start_dispatch_core`, selects the existing role profile, renders once,
and publishes with the existing atomic cache writer.

### Single-flight lock

Before rendering, the child atomically acquires a lock keyed to the resolved
cache path, harness ID, and role under the harness-scoped startup diagnostic
directory. Acquisition uses exclusive creation; a second child records
`deduplicated` and exits without rendering. The lock stores version, cache
path, role, harness identity, PID, and started-at time. It is removed in the
worker's `finally` block only by the holder token. A lock is reclaimable only
when its bounded age is exceeded and the recorded PID is not live; unreadable
or identity-mismatched locks fail closed for refresh and never block stale
relay delivery.

### Lifecycle receipt

Extend the existing harness-scoped `startup-relay-refresh.jsonl` receipt with
one append-only record per launch/worker outcome. Records include schema
version, recorded-at, PID, parent PID where available, cache path, role,
harness name/ID, outcome (`launched`, `completed`, `deduplicated`,
`spawn_error`, `identity_error`, `render_error`, or `publish_error`), elapsed
seconds, generated-at, and a bounded error classification. No report contains
cache content or secrets. Receipt failure stays fail-soft.

## Relay Semantics

For `consistent_except_freshness`, `_startup_gate_response` returns the normal
startup relay instruction with a leading `STALE BUT IDENTITY-VALID` banner.
The banner names the cache `generated_at` value, the
`STARTUP_RELAY_CACHE_MAX_AGE_SECONDS` TTL, and states that any current project,
bridge, work-item, or release claim must come from fresh canonical reads. The
return is validated/relayable and does not contain `GTKB STARTUP RELAY FAILURE`.

Missing, empty, malformed, content-hash/byte-length mismatched,
startup-disclosure-shape invalid, wrong-harness, wrong-harness-ID, or wrong-role
caches remain fail-closed. Content drift is not treated as mere staleness and
does not launch a refresh from untrusted cache identity.

## In-Root Placement Evidence

All implementation and runtime outputs remain under `E:/GT-KB`. The only
source/test targets are `E:/GT-KB/scripts/workstream_focus.py` and
`E:/GT-KB/platform_tests/hooks/test_workstream_focus.py`; the worker cache,
lock, and JSONL receipt use the existing harness-scoped diagnostic directory
inside the project root. The append-only proposal is filed under
`E:/GT-KB/bridge/`. No external application or out-of-root artifact is read as
authority, generated, or required.

## Requirement Sufficiency

Existing requirements sufficient. This is the owner-authorized Slice B repair
for an existing startup-relay contract. It does not change TTL policy, startup
disclosure content, render cost, cache schema authority, or the separate
WI-4564/FAB21 optimization lanes.

## Specification Links

- `GOV-SESSION-SELF-INITIALIZATION-001`
- `DCL-INIT-KEYWORD-STARTUP-DISCLOSURE-RELAY-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`

## Specification-Derived Verification Plan

All behavior tests live in the already-declared
`platform_tests/hooks/test_workstream_focus.py` target:

| Requirement | Test assertion | Expected result |
| --- | --- | --- |
| Current prompt remains responsive | Patch `Popen` and renderer; stale pointer returns without renderer, join, wait, or poll and stays within a bounded elapsed threshold | prompt returns immediately and one detached argv is recorded |
| Durable worker, not daemon thread | Assert Windows flags or POSIX new-session kwargs and no `threading.Thread` refresh path | worker survives hook-process exit contract |
| Single flight | Start two worker invocations for the same cache key | one renders/publishes; the other records `deduplicated` |
| Worker completion | Execute worker mode with a bounded fake renderer and canonical identity | atomic cache/meta pair becomes fresh, identity-valid, and receipt records `completed` with PID/outcome |
| Next-prompt proof | Run stale gate, complete the worker, then call the gate again | second response validates a fresh cache and carries no stale/failure banner |
| Honest stale relay | Use identity- and content-valid stale cache | disclosure relay remains available; banner includes exact `generated_at`, TTL, and fresh-read direction |
| Fail-closed boundary | Missing/malformed/content mismatch/wrong harness ID/wrong role cases | `GTKB STARTUP RELAY FAILURE`; no trusted relay and no refresh launch |
| Existing timeout contract migration | Update the prior stale timeout test | it expects prompt relay plus detached launch, not deterministic failure |
| Lifecycle observability | Spawn error, render error, publish error, and dedup fixtures | bounded JSONL receipt contains correct outcome and no content |
| Wrapper tracked-ness precondition | For each asserted wrapper, resolve `git ls-files --error-unmatch` before reading contents | an untracked wrapper fails with an explicit "wrapper not version controlled" message naming the path |
| Shared relay-path parity | Focused test inspects Claude/config imports, Codex no-window delegation + harness identity, and UserPromptSubmit batch inclusion, for tracked wrappers only | both harness paths reach the same shared relay logic; no claim about global registration parity |

Required execution gates:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5671-startup-relay-fail-open
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5671-startup-relay-fail-open
```

Non-gating configuration baseline (recorded, not a required green gate): the
global `scripts/check_codex_hook_parity.py` result remains FAIL at the current
configuration baseline for the reasons enumerated in version 005 (hooks disabled
in `.codex/config.toml`; missing formal-artifact and workstream-focus PreToolUse
registration; missing Bash/apply_patch matchers; missing workstream-focus and
session-lifecycle UserPromptSubmit registration; forced rather than discovered
wrap-up profile). That failure is expected, is separate remediation work, and
can neither fail nor pass this relay-only slice. The focused test must still
fail if either harness wrapper ceases to reach the shared relay path.

## Prior Deliberations And Rejected Approaches

- `DELIB-WI5671-SLICE-B-AUTHORIZATION` authorizes exactly the fail-open stale
  relay and detached background refresh within these two paths while retaining
  independent review and start gates.
- `DELIB-202667181` is the Slice A observability decision: it measured the
  35-39 second render against a hard 5-second budget but did not authorize this
  fix. The 46-58 second emit latency recorded above updates that measurement.
- `DELIB-20262426` and `DELIB-20264935` established the cache TTL and bounded
  self-heal. This revision preserves TTL/honesty but rejects the joined daemon
  thread because process exit makes it non-durable.
- Raising the five-second cap is rejected because it would block the current
  prompt and still couple correctness to renderer latency. Broad render-cost
  work remains with WI-4564/FAB21. Silent stale relay is rejected because it
  would violate freshness disclosure.
- Removing the configuration-wrapper assertion outright is rejected in favor of
  a tracked-ness-guarded assertion, because deleting coverage would leave the
  Claude/config import path unasserted while the guard achieves the version 006
  clean-checkout requirement.

## Owner Decisions / Input

The owner selected and authorized Slice B through
`DELIB-WI5671-SLICE-B-AUTHORIZATION`, and the authorization
`PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY-WI-5671-SLICE-B-STARTUP-RELAY-FAIL-OPEN-DETACHED-BACKGROUND-REFRESH`
is current and `active`.

Additional owner input in the filing session, 2026-07-30: after the live relay
failure described above, the owner directed via `AskUserQuestion` that the
startup disclosure be regenerated ("Regenerate disclosure"), and then directed
in transcript that the underlying issues be checked against existing bridge and
backlog coverage and driven to conclusion by the owning Prime Builder. That
direction authorizes continuing this existing thread; it does not expand the
authorized scope, and no new owner decision is required for this revision. The
version 006 verdict states that no owner decision is required.

## Intuitiveness / Non-Impairment Disposition

- `launch_startup_relay_refresh_worker`, worker-mode naming, cache-keyed lock,
  and lifecycle outcome names expose purpose directly.
- Existing valid fresh-cache behavior is unchanged.
- Stale-but-valid cache becomes explicitly relayable; invalid identity/content
  remains fail-closed.
- The wrapper tracked-ness precondition makes an untracked-wrapper regression
  self-describing rather than checkout-dependent.
- Historical receipts are append-only. No startup cache or lock is used as
  formal project authority.
- Implementation fails closed before source mutation on missing GO, claim,
  packet, target cleanliness, targeted relay-parity, test, lint, format, or
  preflight evidence.

## Risks / Rollback

Risks are duplicate workers, orphaned locks, detached-process invisibility, and
stale content being mistaken for current truth. Atomic single-flight,
PID/age-bounded reclamation, lifecycle receipts, explicit banner text, and
next-prompt tests address those risks. A further risk is that the widening
render-cost gap eventually exceeds the SessionStart budget so consistently that
no fresh cache is ever produced; that risk belongs to WI-4564/FAB21 and is
recorded, not addressed, here. Rollback is one governed two-path revert; no
schema, KB, deployment, credential, or external-system mutation is in scope.

## Recommended Commit Type

`fix`
