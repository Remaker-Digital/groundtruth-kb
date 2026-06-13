NEW

# Pre-Spawn Launchability Gate + SessionStart Surfacing for Cross-Harness Dispatch

bridge_kind: implementation_proposal
Document: gtkb-dispatch-launchability-pre-spawn-gate
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-13 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 310b54b9-81d9-4fe5-b68e-f3340e9d9c42
author_model: claude-opus-4-7
author_model_version: 4.7
author_model_configuration: Claude Code interactive; Prime Builder durable role

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WI-4525-DISPATCH-LAUNCHABILITY-HARDENING
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4525

target_paths: ["scripts/cross_harness_bridge_trigger.py", "scripts/session_self_initialization.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py", "platform_tests/scripts/test_session_self_initialization.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

Close the temporal gap that made the 2026-06-13 dispatch-executor jam silent. On
that date, the LO dispatch interpreter `groundtruth-kb/.venv/Scripts/python.exe`
was a hollow husk (Scripts dir empty, no `pyvenv.cfg`). The cross-harness
trigger spawned ollama (D) + openrouter (F) into `WinError 2` / `exit 127`,
which the per-recipient circuit breaker then tripped after the `max_retries`
threshold. Bridge review halted for hours with no operator-visible signal — the
breaker's job is to suppress noisy transients, but a missing interpreter is a
static config defect that *should* shout, not whisper.

The static detection capability already exists: `_check_harness_launchability`
in `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (line 3863, attributed
to FAB-01 / HYG-001) iterates each active dispatch target's
`invocation_surfaces.headless.argv[0]`, normalizes it via
`_normalize_harness_argv_head`, and tests `shutil.which(resolved) or
os.path.isfile(resolved)`. It would have returned FAIL on the husk. Its only
shortcoming is that it runs **only when someone invokes `gt doctor`** — never in
the dispatch hot-path itself, and not at SessionStart. This proposal makes the
same detection logic run at the two moments where it would have surfaced the
2026-06-13 defect minutes after it appeared instead of hours.

Two changes:

1. **Pre-spawn launchability gate** in
   `scripts/cross_harness_bridge_trigger.py`: in `run_trigger()`'s main dispatch
   loop, immediately before the `_spawn_harness()` call (~line 3233, after the
   existing circuit-breaker, retry-delay, and self-review guards), check the
   resolved target's launchability by reusing the trigger's own
   `_normalize_argv_head()` (line 1556) + `(shutil.which(resolved) or
   os.path.isfile(resolved))`. If NOT launchable: do NOT spawn; set
   `recipient_state["last_result"] = "target_unlaunchable"`; record a distinct
   `_record_dispatch_failure()` entry with `reason: "target_unlaunchable"` and
   `launched: False`; continue. Because the spawn is skipped, control never
   reaches the post-dispatch exit-code failure path (lines 2712-2733) that
   increments `failure_count`, so a static config defect does NOT consume
   circuit-breaker retries or look like a transient.

2. **SessionStart surfacing** in `scripts/session_self_initialization.py`: call
   `groundtruth_kb.project.doctor._check_harness_launchability` from
   `build_startup_model()` (~line 3355), include the result in the model, and in
   `render_report()` (~line 4888) render a prominent "Harness Dispatch
   Launchability" alert section when `status == "fail"` (insert before the
   "### Active Work Subject" section, ~line 4966). The PASS case adds no
   visible noise.

Together: a static dispatch-target defect surfaces both at the moment of
attempted dispatch (loud, distinct, no breaker consumption) AND at the next
interactive SessionStart (operator-visible disclosure). The doctor check itself
is unchanged — this is a pure execution-surface addition.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge integrity is the top-priority duty;
  silent dispatch degradation that halts review for hours is the exact defect
  class this governance principle exists to prevent. This proposal hardens the
  bridge dispatch hot-path so a config defect is loud, not silent.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal
  cites all relevant governing specs (this list).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal cites the
  project (PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY) and work item (WI-4525)
  metadata in the body header.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the verification plan
  below maps each linked spec to a derived test.
- `REQ-HARNESS-REGISTRY-001` — the data the pre-spawn gate reads
  (`invocation_surfaces.*.argv[0]`) is governed by the harness registry
  contract; the gate uses the canonical projection rather than ad-hoc parsing.
- `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` — the SessionStart surfacing path
  reads the registry through `groundtruth_kb.harness_projection` (via the
  existing `_check_harness_launchability`'s already-conformant reader), not via
  hand-rolled JSON parsing. The trigger-side gate already operates on the
  resolved `DispatchTarget` produced by the canonical resolver.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — this proposal embodies clause (c) of
  the freshness principle: state claims (here, "this target is dispatchable")
  derive from fresh canonical reads of registry + filesystem at the moment of
  dispatch, rather than from a stale prior success.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — flagged applicable because this
  proposal references `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
  (the location of the existing `_check_harness_launchability` function the
  SessionStart surfacing will call). The proposal does NOT modify any file
  under `groundtruth-kb/src/groundtruth_kb/project/**`, does NOT introduce any
  artifact under `applications/`, and does NOT relocate the doctor module —
  the application/root placement boundary is unchanged. Cited for transparency
  because the proposal text mentions a path under that subtree.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — applicable because this proposal
  preserves the artifact graph: WI-4525 (re-homed to
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`) → `DELIB-20263168` (owner
  authorization) → `PAUTH-...-WI-4525-DISPATCH-LAUNCHABILITY-HARDENING` →
  this bridge proposal → derived tests → eventual VERIFIED record. Each
  artifact links to the next; no behavior is added outside the graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — applicable because this proposal
  participates in the bridge thread lifecycle (NEW → GO → implementation
  report → VERIFIED) and the WI-4525 lifecycle (candidate → active →
  resolved). The pre-spawn gate itself emits a new lifecycle-relevant state
  (`target_unlaunchable`) on the dispatch-failure log that is distinct from
  the transient-failure `subprocess_execution_failed` state.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — applicable because this proposal
  was originated through artifact-oriented governance: owner decisions captured
  via AskUserQuestion → DELIB → PAUTH → bridge proposal, with the WI
  re-homed and the project authorization triple validated before scaffold.

## Prior Deliberations

- `DELIB-20263168` (recorded this session, 2026-06-13) — owner_decision
  capturing the two AskUserQuestion answers that authorize this proposal:
  "Platform hardening" as the next branch after the executor fix, and "Both
  (pre-spawn gate + SessionStart surfacing)" as the WI-4525 reframe direction.
  This is the direct authorization basis.

Multiple deliberation searches were run as part of the mandatory pre-propose
sweep ("dispatch interpreter doctor check harness invocation_surfaces venv
launchability reliability", "harness registry doctor check dispatch executable
interpreter launchability boundary"); both returned no matches. The scaffold
seeded five `INTAKE-*` candidates by glossary similarity, but on inspection none
are substantively related to dispatch launchability (they concern advisory
grilling, harness-agnostic review eligibility, per-document leases, scoped batch
approval, and claim-gated implementation start). They are pruned here rather
than carried as decorative citations.

## Owner Decisions / Input

This proposal depends on owner approval. The authorizing evidence:

- `AUQ-2026-06-13-WI4525-BOTH` (AskUserQuestion, 2026-06-13, this session):
  owner selected "Both (pre-spawn gate + SessionStart surfacing)" as the
  WI-4525 reframe direction after the previously-authorized "add doctor check"
  scope was shown to be redundant (the check already exists).
- A prior session AskUserQuestion answer selected "Platform hardening" as the
  next branch after the dispatch-executor fix, which scopes WI-4525 to the
  GTKB-RELIABILITY-FIXES / PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY family.

Both AUQ answers are captured durably in `DELIB-20263168` (source_type
`owner_conversation`, outcome `owner_decision`, work_item_id `WI-4525`). No
further owner decision is required to file this proposal; LO review is the next
gate.

## Requirement Sufficiency

Existing requirements sufficient. The behavior this proposal adds is fully
governed by the cited specs:

- `REQ-HARNESS-REGISTRY-001` defines the registry schema the gate reads.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` clause (c) authorizes pre-action freshness
  checks against canonical state, which is exactly what the pre-spawn gate is.
- The `FAB-01 / HYG-001` lineage (cited inline in
  `_check_harness_launchability`'s docstring) already establishes the
  detection contract — this proposal operationalizes it at additional
  execution surfaces (dispatch hot-path + SessionStart) without changing the
  detection logic itself.

No new requirement or specification is needed before implementation.

## Spec-Derived Verification Plan

Two new pytests, plus the standard code-quality gates on changed files. Reuse
the project venv interpreter for reproducible evidence.

| Linked spec | Derived test / verification | Expected result |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` + `REQ-HARNESS-REGISTRY-001` (the pre-spawn gate consults fresh registry + filesystem state before dispatch) | New test in `platform_tests/scripts/test_cross_harness_bridge_trigger.py`: `test_spawn_gate_skips_unlaunchable_harness_with_distinct_failure`. Build a synthetic project whose harness-registry sets an unlaunchable argv head; invoke `run_trigger()` with one queued actionable entry. | Assert: (a) `_spawn_harness` was NOT called for the unlaunchable target; (b) `.gtkb-state/bridge-poller/dispatch-failures.jsonl` contains a record with `reason: "target_unlaunchable"` and `launched: false`; (c) the recipient's `failure_count` in `dispatch-state.json` is unchanged (no breaker consumption); (d) `last_result == "target_unlaunchable"`. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` + `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` (SessionStart surfaces dispatch-health defects via the canonical projection reader) | New test in `platform_tests/scripts/test_session_self_initialization.py`: `test_startup_disclosure_includes_harness_launchability_alert`. Build a synthetic project whose harness-registry has a failing launchability target. Call `build_startup_model()` then `render_report()`. | Assert: (a) the model contains a launchability check result with `status == "fail"`; (b) the rendered report includes a "Harness Dispatch Launchability" alert section with the failure message; (c) the PASS-case test (same setup with a launchable target) asserts the alert section is absent. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` + `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` + `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (this proposal/report carries the citations through) | Bridge applicability preflight + clause preflight on this slug; preserved in the implementation report. | `preflight_passed: true`, `missing_required_specs: []`; clause preflight exit 0, `Blocking gaps: 0`. |
| All changed-file Python conformance | `groundtruth-kb/.venv/Scripts/ruff.exe check <changed.py>` and `... ruff format --check <changed.py>` on each of the four target_paths. | Exit 0 for both on every changed file. |

Test execution commands:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py::test_spawn_gate_skips_unlaunchable_harness_with_distinct_failure -q --no-header
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py::test_startup_disclosure_includes_harness_launchability_alert -q --no-header
```

## Risk / Rollback

**Risk surface.** This is a hot-path change to the cross-harness dispatch
trigger. Mitigations:

- The gate is read-only at the OS layer (`shutil.which` + `os.path.isfile`); no
  process spawn, no side effects beyond appending one line to the existing
  fire-and-forget JSONL failure log.
- The gate is a pure ADDITION before the existing `_spawn_harness()` call;
  existing guards (circuit breaker, retry delay, self-review refusal) are
  unchanged and continue to apply.
- The unlaunchable path SKIPS the spawn but does NOT increment `failure_count`,
  so the circuit-breaker semantics for transient failures are untouched.
- The SessionStart surfacing is a pure addition that fires only on `status ==
  "fail"`; PASS adds no rendered noise. It calls an existing, tested doctor
  check function rather than reimplementing detection.
- Both changes are fully covered by new pytests asserting both the negative
  (unlaunchable target NOT spawned) and the positive (launchable target spawns
  normally) cases.

**Rollback.** Revert the two edited files
(`scripts/cross_harness_bridge_trigger.py`,
`scripts/session_self_initialization.py`). No schema, MemBase, or
on-disk-state migration; no new dependency. The two new test files can be
deleted or left in place (they will fail open if the source addition is
reverted, since the test fixtures construct the synthetic scenario the source
must handle).

Related but out of scope: `WI-4396` (keep normal bridge lease contention out of
dispatch failure logs) — coordinate any future change to the JSONL log schema,
but no conflict here (this proposal adds a NEW distinct `reason` value; it does
not modify existing entries).

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top
of the `gtkb-dispatch-launchability-pre-spawn-gate` document list in
`bridge/INDEX.md`; no prior version is deleted or rewritten (append-only).
`bridge/INDEX.md` remains the canonical workflow state per
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

`feat:` — net-new dispatch-time gate and net-new SessionStart surface section.
Adds new behavior surfaces (a distinct `target_unlaunchable` dispatch result
and a SessionStart "Harness Dispatch Launchability" alert section), backed by
new tests; not a behavior-preserving refactor and not a bug fix to existing
behavior.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
