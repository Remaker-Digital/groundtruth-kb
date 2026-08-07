REVISED
::init gtkb pb
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 12142541-773d-4560-8095-1fcc131101ff
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; build activity envelope
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: prime_proposal
Document: gtkb-wi6019-substrate-set-reject-permanence
Version: 005
Responds to: bridge/gtkb-wi6019-substrate-set-reject-permanence-004.md
Work Item: WI-6019
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-AUTHORIZE-WI-6019-IMPLEMENTATION

target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py", "platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# WI-6019 REVISED -- Fifth Module With the Same Fixture Pattern

## Why This Revision Exists

`-004` recorded `GO` and **the approved design is unchanged and still correct**. This REVISED
corrects one thing only: `target_paths` remained insufficient by exactly one test module.

`-003` widened scope from 2 paths to 4 after implementation revealed a wider blast radius. That
widening was derived from one executed pytest run over a hand-chosen cohort. It found four modules.
It did not find the fifth, because the fifth was not in the cohort that was run.

Disclosing rather than quietly widening scope, for the same reason `-003` gave: `target_paths` is
the implementation-start gate's binding constraint, and editing outside it is a gate violation even
though the mutation class (`test`) is PAUTH-allowed.

## What The Approved Implementation Revealed

The approved change is implemented and green **within the `-004` declared scope**:

```text
python -m pytest platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py \
                 platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py \
                 platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py \
                 platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py -q
-> 31 passed
```

(28 at the `-003` baseline, plus three cases added per the approved change plan: refusal-vs-unknown
distinctness, `"none"` selectable under both topologies, and READ-acceptance of a persisted legacy
value.)

Both mandatory code-quality gates pass on all four touched files:

```text
python -m ruff check <4 files>          -> All checks passed!
python -m ruff format --check <4 files> -> 4 files already formatted
```

`ruff format` initially wanted one reflow in `validation.py`; it was applied before this filing.
The two gates are separate and `ruff check` passing did not imply the format gate passed.

## The Regression Outside Declared Scope

```text
platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py
  ::test_session_start_drains_pending_before_role_resolution   FAILED
  :81  assert state_path.exists()  -> AssertionError: assert False
```

Cause is the identical fixture pattern `-003` documented, in a module `-003` did not enumerate:

| Line | Code |
| --- | --- |
| `:73` | `defer_bridge_substrate_switch(project_root, "dispatcher_daemon", change_reason="session start drain test")` |
| `:83` | `assert state_data["substrate"] == "dispatcher_daemon"` |

The test's subject is the **session-start pending drain**, not substrate selectability. It needed
*a* selectable value and `"dispatcher_daemon"` was one while it remained so. The fix is the same
substitution applied to the other fixture-pattern modules: `"none"` for `"dispatcher_daemon"`.

**Conversion, not deletion.** Consistent with `-003` and `CLAUDE.md` § Protected Behaviors.

## Blast Radius: What Was Run And What Was Not

Stating this explicitly, because an incomplete sweep is what produced both this revision and `-003`.

A repository-wide search for `validate_bridge_substrate|apply_bridge_substrate_switch|set-bridge-substrate|dispatcher_daemon`
across `platform_tests/` returns **25 modules**. Executed this session:

| Module | Result |
| --- | --- |
| The four `-004` declared modules + `test_doctor_dispatcher_substrate.py` | 31 passed |
| `test_session_start_dispatch_drains_bridge_substrate_pending.py` | **1 failed** -- this revision |
| `test_dispatcher_runtime_drains_pending_before_recipient_resolution.py` | passed |
| `test_bridge_dispatch_reset_stale_runs.py` | passed |
| `test_dispatcher_next_foundation.py` | 1 failed -- **not attributable**; see below |
| `test_gtkb_dispatcher_daemon.py`, `test_bridge_dispatch_config.py`, `cli/test_bridge_dispatch_daemon_supervisor.py` | **not completed** -- 30s timeout |

**`test_dbos_runs_sixteen_stub_subprocess_workflows_idempotently` is not attributable to this
change.** `test_dispatcher_next_foundation.py` contains no call into `validate_bridge_substrate` or
`apply_bridge_substrate_switch`; its sole matching reference is `:562`
`assert "gtkb_dispatcher_daemon" not in source`. Its subject is DBOS stub subprocess workflows. It
is reported here as observed-but-unattributed rather than silently omitted or wrongly claimed.

**Three modules could not be completed.** Each timed out at the 30s pytest limit inside
`daemon_process_alive` -> `_matching_daemon_loop_pids` -> `_is_daemon_loop_command` ->
`Path.resolve()` in `scripts/gtkb_dispatcher_daemon.py:585`. That file is untouched by this change
(`git status --porcelain` over it is empty) and is inside the legacy dispatcher complex, which the
owner has directed be left alone. These are reported as **unverified**, not as passing.

## Corrected `target_paths`

One test module added. No source path added; the production change is still confined to one
function in one file.

1. `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py` *(unchanged)*
2. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py` *(unchanged)*
3. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py` *(unchanged)*
4. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py` *(unchanged)*
5. `platform_tests/scripts/test_session_start_dispatch_drains_bridge_substrate_pending.py` **(added)**

All five fall inside the PAUTH's allowed mutation classes (`source`, `test`).

## Change Plan For The Added File

`test_session_start_dispatch_drains_bridge_substrate_pending.py` -- substitute `"none"` for
`"dispatcher_daemon"` at `:73` and `:83`. The test's subject (drain-before-role-resolution
ordering) is unchanged; only the substrate fixture changes.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirement remains `DELIB-20260807011938`.
This revision changes no requirement and no design; it corrects a declared file list.

## Prior Deliberations

- `DELIB-20260807011938` -- owner decision selecting mechanical SET-rejection; the requirement this
  slice implements.
- `DELIB-20260806011917` -- purge before probative language. Governs the docstring, which states
  what *is* selectable rather than prohibiting what is not. The refusal diagnostic itself is
  machine-readable enforcement and is out of purge scope per `DELIB-20260807011937`.
- `DELIB-20260807011937` -- purge scope: machine-readable enforcement is explicitly NOT a purge
  target, because it is the mechanism keeping the legacy substrate off. This slice adds enforcement
  rather than removing narrative, and is therefore separate from `WI-6018`.
- `bridge/gtkb-wi6019-substrate-set-reject-permanence-003.md` -- the first target_paths correction,
  whose disclosure discipline this revision follows.

## Specification Links

Carried forward unchanged from `-001` and `-003`.

- `DELIB-20260807011938` -- owner decision selecting mechanical SET-rejection.
- `DELIB-20260807-DISPATCHER-DISABLED-MANUAL-BRIDGE-OPERATION` -- the standing prohibition enforced.
- `DELIB-20260807011937` / `DELIB-20260807011940` -- D3 purge scope.
- `DELIB-20260806011917` -- purge before probative language.
- `GOV-ACTING-PRIME-BUILDER-001` -- the READ-accept / SET-reject precedent being mirrored.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` -- registered `authority_spec_id` for the
  `harness-bridge-substrate` SoT artifact.
- `GOV-PLATFORM-SOT-REGISTRY-001` / `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` -- SoT registration of
  `harness-state/bridge-substrate.json`, unchanged by this slice.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` -- the failure mode this change defends against.
- `GOV-FILE-BRIDGE-AUTHORITY-001` -- bridge audit-trail authority; this REVISED appends to the
  append-only chain rather than amending `-003` or `-004` in place.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` -- proposal must cite every relevant
  governing specification; satisfied by this section plus § Prior Deliberations.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` -- verification requires tests derived from the
  linked specifications; satisfied by § Spec-to-Test Mapping, with the unverified and unattributed
  modules named explicitly in § Blast Radius rather than presented as passing.

## Spec-to-Test Mapping

| Requirement clause | Test |
| --- | --- |
| SET of the legacy substrate is refused permanently | `test_validate_refuses_dispatcher_daemon_at_every_readiness_state` (all three readiness states, incl. fully-ready) |
| Refusal is independent of runtime readiness | `test_dispatcher_daemon_refused_irrespective_of_heartbeat` |
| Refusal on a bare tree precedes any probe | `test_substrate_selection_refused_on_bare_tree` |
| Diagnostic cites the owner decision | `DELIB-20260807011938` asserted in all refusal tests |
| Refusal is distinct from the unknown-value path | `test_refusal_diagnostic_is_distinct_from_unknown_substrate` |
| `"none"` remains selectable | `test_none_remains_selectable_under_both_topologies` |
| READ-accept of a persisted legacy value | `test_existing_record_carrying_legacy_value_still_loads` |
| Refusal surfaces through the pending-apply path | `test_apply_pending_records_failed_entries_with_error` |

## Consequence Disclosed: One Function Becomes Unreachable

`_probe_dispatcher_daemon_readiness` (`validation.py:196`) has exactly one caller -- the branch
replaced by this change. After it lands the function is dead code. It is **not** removed by this
slice: removal exceeds the approved design, and `DISPATCHER_DAEMON_SUBSTRATE` must be retained
regardless because `doctor.py` reads it on the READ path at `:5185`, `:5189`, `:5237`, `:5240`,
`:5258`, `:5468`, `:5480`, `:5497`. Flagged for a follow-on hygiene item rather than absorbed
silently.

## Risk And Rollback

Risk is confined to test fixtures plus one source function. Rollback is `git checkout` of the five
declared paths; no migration, no state change, no registry mutation.

## Recommended Commit Type

`fix:` -- repairs a gap in an existing gate (selection could previously succeed whenever the daemon
happened to be ready) with no new capability surface.

## Owner Decisions / Input

- Owner directive, 2026-08-07 (this session): "I am manually driving LO and PB work. Do not touch
  the legacy TAFE dispatcher complex: it is disabled for a reason." This revision honors both --
  it adds mechanical enforcement of that disablement and mutates nothing inside the complex.
- Owner `AskUserQuestion`, 2026-08-07 (this session): asked how the out-of-scope regression should
  close; owner selected **"File a REVISED adding the module"** over filing the report with the
  defect deferred, investigating further first, or parking the thread.
- Owner `AskUserQuestion`, 2026-08-07 (this session): asked how to clear the stale authorization
  packet; owner selected **"Implement wi6019 under its live -004 GO"**, which authorized this
  implementation work.
- `DELIB-20260807011938` -- the originating owner decision, carried forward from `-001`.

---

When you are finished working, close your session envelope by invoking ::wrap.
