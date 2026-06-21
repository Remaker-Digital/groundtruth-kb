NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 600b3b4c-edc3-4090-9217-267db92defe8
author_model: claude-opus-4-8
author_model_version: Opus 4.8
author_model_configuration: interactive Prime Builder session (::init gtkb pb)

# Per-role concurrency cap for cross-harness auto-dispatch (Slice 1) (WI-AUTO-SPEC-INTAKE-CA9165 / SPEC-INTAKE-ca9165)

bridge_kind: implementation_proposal
Document: gtkb-perrole-concurrency-cap-dispatch
Version: 001 (NEW)
Recommended commit type: feat:

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-P1-DISPATCH-RELIABILITY-SPEC-IMPLEMENTATION-22C078-9CB2EE-CA9165
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-AUTO-SPEC-INTAKE-CA9165

target_paths: ["scripts/cross_harness_bridge_trigger.py", "platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Problem / Diagnosis

`SPEC-INTAKE-ca9165` requires two things: (a) the cross-harness trigger MUST NOT
suppress spawning a same-role headless worker merely because another session of
that role is active, and (b) a *per-role concurrency cap* MUST bound the number
of concurrent same-role headless workers (the named S308 runaway-spawn
safeguard). Investigation of the live code shows requirement (a) is already
satisfied but requirement (b) is genuinely unimplemented — there is no per-role
cap anywhere in the dispatch path.

Requirement (a) — already satisfied (this is why the prior thread was withdrawn):
- The binary same-role active-session suppression predicate `check_target_active`
  (`scripts/cross_harness_bridge_trigger.py:2634`) and its alias
  `check_counterpart_active` (`:2676`) have NO live call sites. Confirmed by repo
  grep: every non-definition reference is in test files
  (`platform_tests/scripts/test_cross_harness_trigger_suppression.py`,
  `test_bridge_dispatch_per_document_lease.py`,
  `test_cross_harness_bridge_trigger.py`); the only in-module references are the
  def, the alias, and a docstring mention (`:2125`).
- The live `run_trigger` dispatch decision suppresses per *document*, not per
  *role*: `leased_items = [it for it in selected if is_lease_held(it.document_name, ...)]`
  (`:3716`); it suppresses only when ALL selected documents are already leased
  (`:3718`, result `TARGET_ACTIVE_SESSION_RESULT`), and otherwise dispatches the
  NON-leased documents (`:3732`). Per-document leases are `SPEC-INTAKE-57a736`
  (per-document lease, `scripts/bridge_lease_registry.py`, 300s TTL). Two
  same-role workers on DIFFERENT documents therefore already run in parallel.
- The design constraint the withdrawn proposal targeted,
  `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001`, is already `retired` (version 3).
  No DCL supersession is needed by this proposal.

Requirement (b) — the genuine gap. The only concurrency bound today is the
GLOBAL cap `MAX_LIVE_DISPATCHED_PROCESSES` (WI-4472, default 8,
`GTKB_MAX_LIVE_DISPATCHED_PROCESSES`), enforced in `_spawn_harness` at
`:2760-2778` via `_count_live_dispatched_processes(runs_dir)` (`:1412`), which
counts ALL live `.pid` sidecars regardless of role. Nothing bounds how many of
those 8 belong to a SINGLE role. One role (e.g. loyal-opposition fanning out
over many NEW/REVISED threads, or prime-builder over many GO threads) can
monopolize the entire global pool and starve the other role's dispatch. The spec
names the per-role cap as a mandatory safeguard; the existing global cap does not
satisfy it. The prior withdrawal (`bridge/gtkb-bounded-parallel-cross-harness-dispatch-003.md`)
explicitly recorded that "the only genuinely-unimplemented element ca9165 named
is a per-role concurrency cap" and accepted the global cap as sufficient under an
owner AUQ at the time; this proposal implements the cap the spec actually
requires, closing that residual gap.

## Proposed Change

Slice 1 (this proposal): add a deterministic per-role live-worker concurrency cap
to the existing global-cap gate. No change to the suppression model (per-document
lease + work-intent claim are retained unchanged); no reintroduction of
`check_target_active` into the live path.

The dispatch_id already encodes the role. `_new_dispatch_id(recipient_key)`
(`:774`) builds `{timestamp}-{recipient}-{uuid6}` where `recipient` is the
`dispatch_state_key` `"{needed_role_label}:{harness_id}"` (`:2153`) with `:`
replaced by `-`, e.g. `2026-06-20T..-prime-builder-B-ab12cd`. The `.pid` sidecar
filename therefore carries the role label as an embedded component, so a per-role
live count is derivable from the same runs-dir the global cap already scans — no
new state file, no schema change.

1. Add `GTKB_MAX_LIVE_DISPATCHED_PER_ROLE` env var + `DEFAULT_MAX_LIVE_DISPATCHED_PER_ROLE = 3`
   and a fail-safe reader `_max_live_dispatched_per_role()` mirroring
   `_max_live_dispatched_processes()` (`:1337`) exactly (blank/invalid/<=0 ->
   default). Default 3 sits inside the global default of 8 and matches the spec's
   "default 2-3".
2. Add `_count_live_dispatched_processes_for_role(runs_dir, role_label)`: reuse
   the liveness logic of `_count_live_dispatched_processes` (`:1412`) — `.pid`
   present, `.exit_code` absent/empty, `_pid_alive(pid)` — but count only
   sidecars whose dispatch_id matches the role token (match on the
   `-{role_label}-` segment produced by `_new_dispatch_id`; the two role labels
   `prime-builder` / `loyal-opposition` are non-overlapping substrings, so the
   match is unambiguous). Prune dead/malformed sidecars on the pass, identical to
   the global counter.
3. In `_spawn_harness`, immediately AFTER the existing global-cap gate
   (`:2768`) and before `_is_spawn_rate_limited`, add the per-role gate: compute
   `role_label = target.needed_role_label`, `per_role_cap = _max_live_dispatched_per_role()`,
   `per_role_live = _count_live_dispatched_processes_for_role(runs_dir, role_label)`;
   when `per_role_live >= per_role_cap`, record a dispatch-failure meta with a
   NEW distinct `reason = "per_role_concurrency_cap_reached"` (plus
   `role`, `per_role_live`, `per_role_cap`) and return without spawning,
   issuing no authorization packet and acquiring no claim (same fail-closed shape
   as the global cap). Add `"per_role_concurrency_cap_reached"` to the
   expected-results set near `:255`.
4. Fail-open-to-safety on counting error: if `_count_live_dispatched_processes_for_role`
   raises, treat as 0 only if the global cap already passed (the global cap is the
   hard blast-radius bound and remains authoritative); never over-spawn past the
   global cap. (Implementation note: wrap the per-role count in the same defensive
   style as the global counter, which never raises on a single bad sidecar.)

Composition / sequencing with sibling threads on the same file
(`scripts/cross_harness_bridge_trigger.py`):
- `gtkb-wi4703-dispatch-non-transient-fast-trip` (NEW..-011, in flight): edits the
  failure-classification / circuit-breaker tier (`FATAL_WORKER_OUTPUT_MARKERS`,
  `_process_pending_exit_codes`, ~`:206`, ~`:3199`). Disjoint region from this
  proposal's gate at `:2768`. No logical conflict; whichever lands first, the
  other rebases trivially (different functions).
- `WI-4662` (LO failover): edits `_detect_previous_launch_failure` (`:643`) and the
  LO target-selection/failover path. Also disjoint from the spawn-gate region.
  Recommend this Slice-1 cap land independently; WI-4662 failover and this cap are
  orthogonal (failover picks a DIFFERENT recipient; the cap bounds per-role live
  count across recipients).
- This proposal does NOT touch `single_harness_bridge_dispatcher.py`: in
  single-harness topology the cross-harness trigger is inert and at most one role
  worker is in-process at a time, so the per-role cap is a no-op there
  (`ADR-SINGLE-HARNESS-OPERATING-MODE-001`). Slice 2 may extend the cap to that
  substrate if measurement shows a need.

Deferred to later slices (explicitly OUT of Slice 1):
- Slice 2: per-role cap configurability surfaced through `config/dispatcher/rules.toml`
  (per-role overrides) rather than a single env var; optional per-harness sub-caps.
- Slice 3: dispatch-starvation telemetry / doctor surfacing of
  `per_role_concurrency_cap_reached` frequency (compose with WI-4480 telemetry).
- Slice 4 (only if measured): extend the per-role cap to the single-harness
  dispatcher substrate.

## Specification Links

- `SPEC-INTAKE-ca9165` — the governing requirement this proposal implements:
  bounded parallel cross-harness auto-dispatch with a per-role concurrency cap
  superseding binary same-role active-session suppression. (specified)
- `SPEC-INTAKE-be073a` — time-boxed GO-implementation claim; the per-item
  ownership-coordination prerequisite the intake names. VERIFIED
  (`WI-AUTO-SPEC-INTAKE-BE073A` resolved via
  `bridge/gtkb-go-impl-claim-timebox-004.md`); the spec's sequencing
  precondition ("AFTER SPEC-INTAKE-be073a is VERIFIED") is satisfied.
- `SPEC-INTAKE-9cb2ee` — claim-gated implementation-start; the Prime-side
  per-item dedup (`_filter_prime_selected_by_work_intent`, `:845`) that makes
  same-role parallelism collision-safe on GO threads. (specified)
- `SPEC-INTAKE-57a736` — per-document lease; the live LO-side per-document
  suppression (`is_lease_held`, `:3716`) that already provides same-role
  parallelism on different documents. (specified)
- `GOV-AUTOMATION-VALUE-VS-COST-001` — the per-role cap is the cheap
  deterministic gate in front of the expensive same-role spawn (the S308
  lesson the spec cites). (specified)
- `GOV-FILE-BRIDGE-AUTHORITY-001` — dispatch automation serves the bridge; this
  is dispatch-mechanism-only and the versioned bridge file chain remains
  canonical. (verified)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites
  all relevant governing specs (this list). (specified)
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project / Work Item /
  authorization metadata present in the header. (specified)
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan below
  maps each ca9165 acceptance criterion to a derived test. (specified)
- `GOV-STANDING-BACKLOG-001` — `WI-AUTO-SPEC-INTAKE-CA9165` is the governed
  backlog item, admitted to `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`. (verified)
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all changed files are under
  `E:\GT-KB`. (specified)
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — single-harness and multi-harness are
  both first-class; the per-role cap is a no-op in single-harness topology and
  does not perturb that substrate. (specified)

## Owner Decisions / Input

- Authorized: `DELIB-20263189` (owner AUQ 2026-06-13, AskUserQuestion) authorized
  implementing the 3 P1 dispatch specs and named ca9165's scope verbatim ("Enable
  bounded parallel cross-harness auto-dispatch; supersede binary same-role
  active-session suppression"), under PAUTH
  `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-P1-DISPATCH-RELIABILITY-SPEC-IMPLEMENTATION-22C078-9CB2EE-CA9165`.
  `WI-AUTO-SPEC-INTAKE-CA9165` is admitted to PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
  under this PAUTH.
- Re-open note: `WI-AUTO-SPEC-INTAKE-CA9165` was previously marked `resolved` after an
  owner AUQ accepted the existing global concurrency cap as the ca9165 safeguard. This
  proposal is filed under the interactive Prime Builder session's owner AskUserQuestion
  re-opening ca9165 to implement the per-role concurrency cap the spec names as
  mandatory and that the prior withdrawal flagged as the only genuinely-unimplemented
  element. The WI is reset from `resolved` to active under that owner decision.
- No coupled formal-artifact (DCL) approval packet is required:
  `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001` is already retired, and this proposal
  is source+test only (`kb_mutation_in_scope: false`).
- One design value warrants an owner AUQ at GO/implement-time (does NOT block
  filing or review): the default per-role cap. The spec says "default 2-3"; this
  proposal proposes 3. If the owner prefers a more conservative 2, it is a
  one-constant change with no structural impact.

## Prior Deliberations

- `bridge/gtkb-bounded-parallel-cross-harness-dispatch-001/-002/-003.md` — the
  WITHDRAWN prior thread on this exact topic (NEW `-001`, GO `-002`
  Antigravity/harness C = `DELIB-20263313`, WITHDRAWN `-003`). It was withdrawn
  because its premise was stale: it framed the work as superseding the binary
  `check_target_active` suppression and a coupled `DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001`
  supersession, but `check_target_active` was already dead in the live path
  (replaced by the per-document lease, `SPEC-INTAKE-57a736` VERIFIED) and parallel
  same-role dispatch on different documents already worked. The owner AUQ
  reconciled `WI-AUTO-SPEC-INTAKE-CA9165` as already-implemented and accepted the
  global cap as the runaway-spawn safeguard. WHAT CHANGED in this proposal: it
  drops the obsolete suppression-supersession framing and the coupled DCL action
  entirely (DCL now retired), and instead implements the ONE element the
  withdrawal itself flagged as genuinely unimplemented — the per-role concurrency
  cap the spec mandates — as a small additive gate beside the existing global cap.
  New slug (`gtkb-perrole-concurrency-cap-dispatch`); the dead slug is not reused.
- `INTAKE-2ce995f2` — the ca9165 intake (confirmed -> `SPEC-INTAKE-ca9165`); the
  verbatim requirement text and named safeguards this proposal implements.
- `DELIB-20263189` — owner AUQ authorization (2026-06-13) for the 3 P1 dispatch
  specs; the direct authorization basis under the cited PAUTH.
- `DELIB-20263313` — the prior pre-implementation GO verdict (now retracted with
  its thread); recorded for audit continuity, not relied upon.

## Requirement Sufficiency

Existing requirements sufficient. `SPEC-INTAKE-ca9165` defines the required
behavior (a per-role concurrency cap bounding concurrent same-role headless
workers) and the prerequisite (`SPEC-INTAKE-be073a`, VERIFIED) is met; no new or
revised requirement is needed before implementing this Slice-1 cap.

## Specification-Derived Verification Plan

New unit tests in `platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py`,
plus regression and code-quality gates. (Spec-to-test mapping.)

| ca9165 acceptance criterion | Derived test | Expected |
| --- | --- | --- |
| Per-role cap bounds concurrent same-role workers | `test_per_role_cap_suppresses_at_limit`: seed `runs_dir` with `per_role_cap` live same-role `.pid` sidecars (alive PIDs, no `.exit_code`); attempt one more same-role spawn | no spawn; `reason == "per_role_concurrency_cap_reached"`; meta carries `role`/`per_role_live`/`per_role_cap` |
| Same-role parallelism allowed below the cap (no binary suppression) | `test_per_role_below_cap_allows_same_role_spawn`: with `per_role_cap-1` live same-role workers and a same-role active session present, attempt a same-role spawn for a DIFFERENT document | spawn proceeds; result is NOT a suppression reason |
| Per-role count is role-scoped, not global | `test_per_role_count_excludes_other_role`: seed `runs_dir` with live workers of the OTHER role only; attempt a spawn for this role at per-role 0 | spawn proceeds; other-role sidecars do not count toward this role |
| Global cap remains authoritative (WI-4472) | `test_global_cap_still_enforced_independently`: live count >= `MAX_LIVE_DISPATCHED_PROCESSES` with per-role headroom | no spawn; `reason == "concurrency_cap_reached"` (global gate fires first) |
| Per-item dedup unbroken under parallelism (`SPEC-INTAKE-9cb2ee` / `57a736`) | `test_same_item_not_double_dispatched_under_cap`: two same-role candidates for the SAME document under the cap | second blocked by work-intent claim / per-document lease, not by the cap |
| Fail-safe config reader | `test_max_live_dispatched_per_role_env_parsing`: unset / blank / `"0"` / `"-1"` / `"abc"` / `"5"` | default(3) for unset/blank/invalid/<=0; 5 for `"5"` |
| Event-driven only; no interval regression (S308) | regression: full `test_cross_harness_bridge_trigger.py` + `test_bridge_dispatch_concurrency.py` + `test_bridge_dispatch_per_document_lease.py` | all green; dispatch stays signature-gated |
| Code quality | `ruff check` + `ruff format --check` on changed files | clean |

Commands (from repo root `E:\GT-KB`):

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py platform_tests/scripts/test_bridge_dispatch_concurrency.py platform_tests/scripts/test_bridge_dispatch_per_document_lease.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/cross_harness_bridge_trigger.py platform_tests/scripts/test_perrole_concurrency_cap_dispatch.py
```

The implementation report will also include the two mandatory bridge preflights
(`bridge_applicability_preflight.py`, `adr_dcl_clause_preflight.py`) for this
bridge id.

## Risk And Rollback

- Risk: per-role cap set too low throttles legitimate same-role throughput.
  Mitigation: default 3 (inside the global 8), env-overridable
  (`GTKB_MAX_LIVE_DISPATCHED_PER_ROLE`) for live tuning; cap only suppresses
  ADDITIONAL same-role spawns once the role is already at N live workers.
- Risk: per-role count miscounts after a crash leaves a stale `.pid`. Mitigation:
  reuses the exact liveness+prune logic of the global counter (`.exit_code`
  presence + `_pid_alive` + prune-on-pass), so stale sidecars are reclaimed
  identically; a transient miscount can only UNDER-count (reclaim a dead worker),
  never over-suppress, and the global cap is the hard backstop.
- Risk: regression to the per-document-lease / work-intent suppression model.
  Mitigation: this change is purely additive at the spawn gate; no edit to
  `is_lease_held`, `_filter_prime_selected_by_work_intent`, or the `run_trigger`
  lease branch; the suppression model is unchanged and the full suppression
  regression suite is in the plan.
- Risk: S308 interval-polling regression. Mitigation: no change to the
  actionable-signature event-driven path; the cap is evaluated only inside an
  already-triggered spawn attempt.
- Rollback: single-commit revert of `scripts/cross_harness_bridge_trigger.py`;
  the new test file is additive. No state-file schema change (reuses the runs-dir
  `.pid`/`.exit_code` sidecars), no MemBase mutation, no new runtime dependency.

## Acceptance Criteria

- [ ] `GTKB_MAX_LIVE_DISPATCHED_PER_ROLE` (default 3) is read fail-safe, mirroring
  the global cap reader.
- [ ] A same-role spawn is suppressed with `reason == "per_role_concurrency_cap_reached"`
  when the role is at the per-role cap; below the cap, a same-role spawn for a
  different document proceeds (no binary same-role suppression).
- [ ] The per-role count is role-scoped (other-role live workers do not count) and
  reuses the global counter's liveness+prune semantics.
- [ ] The global cap (WI-4472) remains enforced and authoritative; the per-role
  gate sits beside it, never above it.
- [ ] Per-item dedup (work-intent claim + per-document lease) still prevents two
  workers on one document under parallelism.
- [ ] `check_target_active` is NOT reintroduced into the live dispatch path.
- [ ] New unit tests pass; suppression/concurrency/per-document-lease regression
  suites pass; ruff check + format clean.
- [ ] No KB mutation; no DCL supersession (DCL-SINGLE-ACTIVE-PER-ROLE-DISPATCH-001
  already retired).

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
