REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f9329-a174-7763-8f7e-29679f39e6bd
author_model: gpt-5.6
author_model_version: gpt-5.6
author_model_configuration: reasoning_effort=high; thread_source=codex-desktop
author_metadata_source: x-codex-turn-metadata



# WI-5671 startup relay: durable detached refresh worker

bridge_kind: prime_proposal
Document: gtkb-wi5671-startup-relay-fail-open
Version: 005
Responds to: bridge/gtkb-wi5671-startup-relay-fail-open-004.md
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY-WI-5671-SLICE-B-STARTUP-RELAY-FAIL-OPEN-DETACHED-BACKGROUND-REFRESH
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING-SESSION-STARTUP-LATENCY
Work Item: WI-5671
target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py"]

implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Revision Disposition

Version 002 is correct: a daemon thread belongs to the short-lived
UserPromptSubmit process and dies when that process exits. This revision removes
that mechanism from the design. The current prompt never joins, renders, or
waits for refresh work. It relays an identity- and content-valid stale cache
with a conspicuous age banner and launches a durable no-window child process
whose result is observable on the next prompt.

Both declared targets are currently clean. No source or test mutation occurs
through this filing. A future implementation requires fresh independent GO,
the exact WI-5671 claim, and a successful implementation-start packet.

## Revision Disposition — targeted relay parity

Version 004 correctly rejects the global Codex hook-parity command as a green
acceptance gate for this two-path relay slice. This revision keeps the exact
authorized source/test targets and does not expand into `.codex/config.toml`,
`.codex/hooks.json`, dispatcher profiles, or hook registration.

The global checker remains a visible non-gating baseline. Its current failures
are: hooks disabled in `.codex/config.toml`; missing formal-artifact and
workstream-focus PreToolUse registration; missing Bash/apply_patch matchers;
missing workstream-focus and session-lifecycle UserPromptSubmit registration;
and forced rather than discovered wrap-up profile. Those configuration defects
remain separate remediation work and are not waived or described as green.

This slice instead proves behavior-level shared-relay parity in the declared
test target. The focused assertion reads the tracked wrappers and confirms:

- `.claude/hooks/workstream-focus.py` and
  `config/hooks/gtkb-workstream-focus.py` import the shared
  `scripts/workstream_focus.py` surface;
- `.codex/gtkb-hooks/workstream-focus.cmd` sets
  `GTKB_HARNESS_NAME=codex` and delegates through `run_py_no_window.py` to the
  Claude workstream-focus wrapper; and
- the relevant `run_py_no_window.py` UserPromptSubmit batch includes
  `workstream-focus.cmd`.

That is relay-path parity only, not global registration/configuration parity.

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

Existing requirements are sufficient. This is the owner-authorized Slice B
repair for an existing startup-relay contract. It does not change TTL policy,
startup disclosure content, render cost, cache schema authority, or the
separate WI-4564/FAB21 optimization lanes.

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
| Shared relay-path parity | Focused test inspects Claude/config imports, Codex no-window delegation + harness identity, and UserPromptSubmit batch inclusion | both harness paths reach the same shared relay logic; no claim about global registration parity |

Required execution gates:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_workstream_focus.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/workstream_focus.py platform_tests/hooks/test_workstream_focus.py
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5671-startup-relay-fail-open
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5671-startup-relay-fail-open
```


Non-gating configuration baseline (recorded, not a required green gate):

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/check_codex_hook_parity.py
Codex hook parity: FAIL
- .codex/config.toml must set [features].hooks = true
- .codex/hooks.json does not register the formal artifact approval PreToolUse hook
- .codex/hooks.json does not register the workstream focus PreToolUse hook
- Codex workstream focus PreToolUse hook must cover matcher = 'Bash'
- Codex workstream focus PreToolUse hook must cover matcher = 'apply_patch'
- .codex/hooks.json does not register the workstream focus UserPromptSubmit hook
- .codex/hooks.json does not register the UserPromptSubmit session lifecycle hook
- Codex wrap-up trigger dispatcher must discover the role profile instead of forcing one
```

This failure is expected at the current configuration baseline and cannot fail
or pass this relay-only slice. The focused test must still fail if either
harness wrapper ceases to reach the shared relay path.

## Prior Deliberations And Rejected Approaches

- `DELIB-WI5671-SLICE-B-AUTHORIZATION` authorizes exactly the fail-open stale
  relay and detached background refresh within these two paths while retaining
  independent review and start gates.
- `DELIB-202667181` is the Slice A observability decision: it measured the
  35–39 second render against a hard 5-second budget but did not authorize this
  fix.
- `DELIB-20262426` and `DELIB-20264935` established the cache TTL and bounded
  self-heal. This revision preserves TTL/honesty but rejects the joined daemon
  thread because process exit makes it non-durable.
- Raising the five-second cap is rejected because it would block the current
  prompt and still couple correctness to renderer latency. Broad render-cost
  work remains with WI-4564/FAB21. Silent stale relay is rejected because it
  would violate freshness disclosure.

## Owner Decisions / Input

The owner selected and authorized Slice B through
`DELIB-WI5671-SLICE-B-AUTHORIZATION`. No additional owner decision is needed
for this corrected mechanism.

## Intuitiveness / Non-Impairment Disposition

- `launch_startup_relay_refresh_worker`, worker-mode naming, cache-keyed lock,
  and lifecycle outcome names expose purpose directly.
- Existing valid fresh-cache behavior is unchanged.
- Stale-but-valid cache becomes explicitly relayable; invalid identity/content
  remains fail-closed.
- Historical receipts are append-only. No startup cache or lock is used as
  formal project authority.
- Implementation fails closed before source mutation on missing GO, claim,
  packet, target cleanliness, targeted relay-parity, test, lint, format, or preflight evidence.

## Risks / Rollback

Risks are duplicate workers, orphaned locks, detached-process invisibility, and
stale content being mistaken for current truth. Atomic single-flight,
PID/age-bounded reclamation, lifecycle receipts, explicit banner text, and
next-prompt tests address those risks. Rollback is one governed two-path revert;
no schema, KB, deployment, credential, or external-system mutation is in scope.

## Recommended Commit Type

`fix`
