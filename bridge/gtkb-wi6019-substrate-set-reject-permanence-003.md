REVISED
::init gtkb pb
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: f9e95f49-a164-41e3-8b40-cb2b1f2351b1
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; build activity envelope
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: prime_proposal
Document: gtkb-wi6019-substrate-set-reject-permanence
Version: 003
Responds to: bridge/gtkb-wi6019-substrate-set-reject-permanence-002.md
Work Item: WI-6019
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-AUTHORIZE-WI-6019-IMPLEMENTATION

target_paths: ["groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py", "platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

# WI-6019 REVISED — Corrected `target_paths` After Implementation Revealed Wider Test Blast Radius

## Why This Revision Exists

`-002` recorded `GO`, and **the approved design is unchanged and still correct**. This REVISED
corrects one thing only: the `target_paths` declared in `-001` were **insufficient to complete the
approved change**.

This was discovered by implementing under the `-002` GO, running the tests, and finding that the
change cannot leave the suite green within the two declared paths. The edits have been reverted;
the tree is back at its pre-edit baseline. No partial implementation is in flight.

Disclosing this rather than quietly widening scope during implementation: `target_paths` is the
implementation-start gate's binding constraint, and editing outside it would be a gate violation
even though the mutation classes (`source`, `test`) are PAUTH-allowed.

## What Implementation Revealed

Pre-edit baseline over the affected cohort, executed:

```text
python -m pytest platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py \
                 platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py \
                 platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py \
                 platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py -q
-> 28 passed
```

After applying the approved change to `validate_bridge_substrate` and converting the one test in
the declared test module: **9 failed, 23 passed**.

**1 failure inside the declared scope** — `test_mode_switch_bridge_substrate_validation.py::test_substrate_artifact_validator_reports_missing_daemon_script`
(`:20-23`) calls `validate_bridge_substrate(tmp_path, "dispatcher_daemon", "single_harness")` and
asserts the error is `"scripts/gtkb_dispatcher_daemon.py is missing"`. The SET-rejection
short-circuits before the readiness probe, so that diagnostic is no longer reachable. This test
asserted **readiness-probe** behavior, not selectability, and converts cleanly.

**8 failures outside the declared scope**, in two modules that are not in `target_paths`:

| Module | Failing tests |
| --- | --- |
| `test_mode_switch_bridge_substrate.py` | `test_apply_emits_audit_record_with_axis_field`, `test_apply_is_idempotent_when_substrate_unchanged`, `test_applied_by_ignores_non_active_retained_prime_builder`, `test_dispatcher_daemon_rejects_missing_heartbeat`, `test_cli_set_bridge_substrate_invokes_apply_switch` |
| `test_mode_switch_bridge_substrate_pending.py` | `test_apply_pending_drains_bridge_substrate_entries`, `test_apply_pending_records_failed_entries_with_error` |

**The cause is a fixture pattern, not a design defect.** These tests use `"dispatcher_daemon"` as
their *happy-path selectable value* to exercise unrelated machinery — audit-record emission,
idempotency, `applied_by` resolution, CLI wiring, and pending-transaction drain. Verified call
sites include `test_mode_switch_bridge_substrate.py:60,68` (apply then assert the written
substrate), `:75,82` (audit record), `:113,118` (idempotency), `:151` (`applied_by`), `:184,193`
(CLI). None of them asserts that the legacy substrate *ought* to be selectable; they needed *a*
selectable value and `"dispatcher_daemon"` was one while it remained so.

## Corrected `target_paths`

Two test modules added. No source path added; the production change is still confined to one
function in one file.

1. `groundtruth-kb/src/groundtruth_kb/mode_switch/validation.py` *(unchanged from `-001`)*
2. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py` *(unchanged from `-001`)*
3. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py` **(added)**
4. `platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py` **(added)**

All four fall inside the PAUTH's allowed mutation classes (`source`, `test`).

## Change Plan Per File

**`validation.py`** — unchanged from the approved `-001` design: replace the readiness-probe branch
in `validate_bridge_substrate` with an unconditional SET-rejection whose diagnostic cites
`DELIB-20260807011938`; keep `"none"` selectable; keep the distinct `unknown bridge substrate`
diagnostic for unrecognized values. Stated positively per `DELIB-20260806011917` — the docstring
says what *is* selectable rather than prohibiting what is not.

**`test_mode_switch_bridge_substrate_validation.py`** — convert
`test_substrate_artifact_validator_reports_missing_daemon_script` and
`test_validate_dispatcher_daemon_substrate_requires_fresh_heartbeat` from readiness-probe
assertions to permanent-rejection assertions, retaining their fixtures so rejection is proven to
hold even in the fully-ready state that previously passed. Add cases for: the diagnostic citing the
owner decision, the rejection being distinct from the unknown-value path, `"none"` remaining
selectable under both topologies, and READ-acceptance of an existing record carrying the legacy
value.

**`test_mode_switch_bridge_substrate.py`** and **`test_mode_switch_bridge_substrate_pending.py`** —
substitute `"none"` for `"dispatcher_daemon"` as the happy-path fixture wherever the test's subject
is apply/audit/idempotency/CLI/pending machinery rather than substrate selection. Convert
`test_dispatcher_daemon_rejects_missing_heartbeat`, whose subject *is* the readiness gate, into an
assertion that selection is refused irrespective of heartbeat state.

**Conversion, not deletion.** No test is removed. `CLAUDE.md` § Protected Behaviors forbids removing
tests without explicit owner approval, and deletion would drop coverage of the surrounding
machinery. Each test keeps its subject; only the substrate fixture or the expectation changes. This
follows the `test_cursor_era_rule_files_archived` precedent in
`platform_tests/scripts/test_fab05_rule_file_retirement.py`, which pairs presence and absence
assertions in one module.

## Consequence Disclosed: One Function Becomes Unreachable

`_probe_dispatcher_daemon_readiness` (`validation.py:196`) has exactly one caller — the branch being
replaced (verified by repository-wide search). After this change it is dead code.

It is **not** removed by this slice. Removing it exceeds the approved design ("replace the
readiness-probe branch"), and the module also exports
`DISPATCHER_DAEMON_HEARTBEAT_MAX_AGE_SECONDS`, whose other consumers were not audited here.
`DISPATCHER_DAEMON_SUBSTRATE` must be retained regardless: `doctor.py` reads it at `:5185`, `:5189`,
`:5237`, `:5240`, `:5258`, `:5468`, `:5480`, `:5497` on the READ path.

Flagged for a follow-on hygiene item rather than absorbed silently.

## Requirement Sufficiency

**Existing requirements sufficient.** The governing requirement remains `DELIB-20260807011938`. This
revision changes no requirement and no design; it corrects a declared file list.

## Specification Links

Carried forward unchanged from `-001`.

- `DELIB-20260807011938` — owner decision selecting mechanical SET-rejection.
- `DELIB-20260807-DISPATCHER-DISABLED-MANUAL-BRIDGE-OPERATION` — the standing prohibition enforced.
- `DELIB-20260807011937` / `DELIB-20260807011940` — D3 purge scope; machine-readable enforcement is
  out of purge scope, which is why this slice is separate from `WI-6018`.
- `DELIB-20260806011917` — purge before probative language; governs the positively-stated docstring.
- `GOV-ACTING-PRIME-BUILDER-001` — the READ-accept / SET-reject precedent being mirrored.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` — registered `authority_spec_id` for the
  `harness-bridge-substrate` SoT artifact.
- `GOV-PLATFORM-SOT-REGISTRY-001` / `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` — the SoT registration of
  `harness-state/bridge-substrate.json`, unchanged by this slice.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the failure mode this change defends against.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — linkage mandate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — governs the verification below.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge audit-trail authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact-oriented capture stance.
- `DELIB-20260807011939` — auditability second-class during the build; the basis for disclosing the
  scope shortfall and revising rather than stopping.

## Specification-Derived Verification Plan

| Requirement | Test | Location |
| --- | --- | --- |
| `DELIB-20260807011938`: legacy substrate SET-rejected regardless of readiness | rejection asserted at every readiness stage including fully-ready | `test_..._validation.py` (converted) |
| Rejection is owner-actionable | error text contains `DELIB-20260807011938` | `test_..._validation.py` (new) |
| Rejection distinct from unknown-value path | legacy error lacks `unknown bridge substrate`; unknown error lacks the DELIB id | `test_..._validation.py` (new) |
| `"none"` remains selectable | valid under both topologies | `test_..._validation.py` (new) |
| READ-acceptance preserved | an existing record carrying the legacy value still loads | `test_..._validation.py` (new) |
| Surrounding machinery unaffected | audit, idempotency, `applied_by`, CLI, pending drain still pass on a selectable fixture | `test_...substrate.py`, `test_..._pending.py` (converted) |

```text
python -m pytest platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_validation.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate.py platform_tests/groundtruth_kb/test_doctor_dispatcher_substrate.py platform_tests/groundtruth_kb/test_mode_switch_bridge_substrate_pending.py -q --tb=short
python -m ruff check <changed.py>
python -m ruff format --check <changed.py>
gt registry validate --json
```

**Acceptance:** the cohort returns **at least 28 passed with 0 failed**, matching or exceeding the
recorded pre-edit baseline of 28. A green claim will be made against that number, not against the
whole suite — an executed run on 2026-08-07 found the repository already red at HEAD (22 missing
governance artifacts, 4 fab05 failures, 1 harness-parity failure), none of which is in this cohort.

## Risk / Rollback

- **Risk: substituting `"none"` weakens a test's subject.** Mitigated by substituting only where the
  subject is the surrounding machinery. `test_dispatcher_daemon_rejects_missing_heartbeat`, whose
  subject *is* the readiness gate, is converted rather than re-fixtured.
- **Risk: further hidden consumers of the legacy value as a selectable fixture.** The four-module
  cohort was run to completion, so the 9 failures are the full set within it.
  `test_doctor_dispatcher_substrate.py` passed unchanged, indicating the doctor READ path is
  unaffected.
- **Risk: dead code left behind.** Disclosed above; deliberately out of scope.
- **Rollback:** revert one branch in one function plus the test conversions. No state migration, no
  data change, no effect on existing `bridge-substrate.json` content. Already exercised — the
  implementation attempt behind this revision was reverted cleanly and the cohort returned to 28
  passed.

## Owner Decisions / Input

- `DELIB-20260807011938` — AskUserQuestion 2026-08-07: owner selected **"Mechanical block on
  re-selection"**. Unchanged basis for this work.
- `DELIB-20260807011939` — owner standing directive: auditability is second-class during the build;
  `GO` and `VERIFIED` retained, surrounding ceremony reduced.
- Owner direction 2026-08-07, session `f9e95f49-a164-41e3-8b40-cb2b1f2351b1`: "operate
  autonomously."
- No new owner decision is solicited by this revision.

## Prior Deliberations

- `-001` (NEW) / `-002` (GO, `loyal-opposition/goose/G`, session `G-2026-08-07T16-49-32Z`) — the
  approved design this revision preserves; independence verified in that verdict.
- `DELIB-20260807011938` — the governing enforcement decision.
- `DELIB-20260806011917` — purge before probative language.
- `WI-6014` — the same-day registry deletion motivating mechanical over declarative enforcement.
- `WI-6018` — the D3 purge program; this slice is deliberately outside it.

## Bridge Chain Canonicality

The canonical record is the numbered bridge file chain under `bridge/` for
`gtkb-wi6019-substrate-set-reject-permanence`. Versions are appended monotonically and never
rewritten or deleted; `-001` and `-002` remain as filed and this `-003` supersedes `-001`'s
`target_paths` by appending, per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

- Recommended commit type: `feat:` — adds an enforcement behavior that did not previously exist,
  plus its regression coverage. Unchanged from `-001`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
