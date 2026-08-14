NEW
::init gtkb lo
::open build
author_identity: claude
author_harness_id: B
author_session_context_id: a49752e4-5a9f-4290-bceb-910693b5271f
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via the canonical init keyword


# Implementation Report — Teach the Parity Checker the Projection Contract

bridge_kind: implementation_report
Document: gtkb-wi6267-parity-projection-contract
Version: 005
Author: Prime Builder (harness B, claude)
Date: 2026-08-14 UTC

Work Item: WI-6267
Project: PROJECT-GTKB-GET-HEALTHY-PHASE-2
Project Authorization: PAUTH-GET-HEALTHY-PHASE-2-EXECUTION-20260814

target_paths: ["scripts/check_harness_parity.py", "platform_tests/scripts/test_check_harness_parity_projection.py"]

implementation_scope: source
requires_review: false
requires_verification: true
kb_mutation_in_scope: false

This implementation performs no MemBase mutation; it changes one checker
script and adds one regression-test module.

Responds to: bridge/gtkb-wi6267-parity-projection-contract-004.md

---

## Headline — V1 is NOT met, by design of the truth rather than of the fix

The `-003` acceptance criterion V1 was "`--harness goose` reports zero STALE
rows". **It does not.** Measured after the change: `STALE: 24`.

All four approved mechanisms are repaired and every false positive is gone.
The 24 rows that remain are **true positives** that the broken generator check
was masking, and they live in
`config/agent-control/gtkb-harness-capability-registry.toml` — outside this
thread's `target_paths`. Reaching literal zero would require editing the
registry, which is a different change needing its own review.

This is stated first rather than buried, because a report that satisfied V1 by
widening scope to the registry, or by quietly relaxing the hash check, would be
the exact failure the `-002`/`-004` reviews were guarding against.

## Commit

`63add93e2c73200e56c55914b91c6480be96c64d` — 2 files changed, 320 insertions,
3 deletions.

## Files Changed

| Path | Change |
| --- | --- |
| `scripts/check_harness_parity.py` | four mechanism repairs (M1-M4) |
| `platform_tests/scripts/test_check_harness_parity_projection.py` | new, 15 tests |

## What Landed, by Mechanism

**M1 — routing.** `_status_for_surface` now resolves
`projection_engine` from the registry before the `manifest_adapters` branch. A
harness declaring an engine takes `GTKB-<HARNESS>-SKILL-ADAPTER`; the API-stub
branch is otherwise untouched. Enumerated: `goose` is the only harness
declaring `projection_engine`; `cursor`, `ollama`, `openrouter` and
`alibaba-cloud-studio` declare `skill_adapter_manifest` alone and keep the API
branch, pinned by `test_manifest_only_harnesses_keep_the_api_branch`.

**M2 — generator resolution.** `expected_generator = projection_engine or
ADAPTER_GENERATOR_BY_MARKER.get(expected_marker)`. The static map is unchanged
and still holds exactly the three stub markers
(`test_stub_generator_map_is_unchanged`). Registry-derived resolution was
chosen over a hard-coded goose row so a Phase-D cutover does not silently
re-break parity.

**M3 — marker grammar.** `_find_markers` tries the engine's
`MARKER-BEGIN` / `MARKER-END` form first and falls through to the existing
`MARKER` / `MARKER -->` form. The stub path is byte-unchanged; both grammars
are pinned by test, as is the absent-block case.

**M4 — expected-content oracle.** `_render_expected_adapter` gained
`projection_harness`; when set it returns
`project_harness.build_plan(harness).writes[surface]`. The plan is memoised in
`_PROJECTION_PLAN_CACHE`, built lazily on first use, so a run that selects no
projected harness pays nothing. The exception clause around the render call was
widened to `OSError`/`RuntimeError` so an engine failure reports a diagnostic
STALE rather than crashing the run — the `-004` Risk/Rollback requirement.

## Spec-to-Test Mapping

| Spec / criterion | Verification | Result |
| --- | --- | --- |
| `GOV-HARNESS-NEUTRAL-BASELINE-001` ob.2 (parity must be able to validate projections) — V1 | `check_harness_parity.py --harness goose` | **PARTIAL** — `STALE 44 -> 24`, `PASS 0 -> 20`. False positives eliminated; 24 true positives remain, out of scope (see below) |
| `SPEC-1662` / GOV-18 (assertion meaningfulness) — V2 | tampered-body, wrong-digest and missing-block tests | **PASS** — `test_tampered_body_is_detected`, `test_wrong_digest_is_visible_to_the_hash_comparison`, `test_missing_block_yields_no_generator_identity` |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` (stub family unaffected) — V3 | API-branch test + live codex re-run | **PASS** — counts byte-identical before/after (below) |
| `-003` Scope 3 (both grammars) — V4 | `test_find_markers_parses_begin_end_grammar`, `..._stub_grammar_unchanged`, `..._returns_none_when_block_absent` | **PASS** |
| `-003` Scope 1 (routing predicate) — V5 | `test_projection_engine_routes_to_own_marker`, `test_manifest_only_harnesses_keep_the_api_branch` | **PASS** |
| Pre-file code-quality gates — V6 | `ruff check` and `ruff format --check`, run separately | **PASS** |

## Commands Executed

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi6267-parity-projection-contract
groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi6267-parity-projection-contract
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_harness_parity_projection.py -q --tb=short --timeout=120
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_check_harness_parity_projection.py platform_tests/scripts/test_check_harness_parity_entrypoint_import.py platform_tests/scripts/test_harness_projection.py platform_tests/scripts/test_harness_projection_reader.py platform_tests/scripts/test_parity_coverage_complete.py platform_tests/scripts/test_parity_discovery_diff.py platform_tests/scripts/test_parity_strict_on_rename.py -q --tb=short --timeout=180
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity_projection.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/check_harness_parity.py platform_tests/scripts/test_check_harness_parity_projection.py
groundtruth-kb/.venv/Scripts/python.exe scripts/check_harness_parity.py --harness goose
groundtruth-kb/.venv/Scripts/python.exe scripts/check_harness_parity.py --harness codex
```

Observed results:

```text
15 passed, 1 warning in 3.12s                     (new module)
6 failed, 91 passed, 1 warning in 23.25s          (affected-module set)
All checks passed!                                (ruff check)
2 files already formatted                         (ruff format --check)

AFTER  codex : Counts: DEGRADED: 3, EXTRA: 1, PASS: 14, STALE: 44, UNSUPPORTED: 11, WARN: 1
AFTER  goose : Counts: EXTRA: 1, PASS: 20, STALE: 24, UNSUPPORTED: 24
BEFORE codex : Counts: DEGRADED: 3, EXTRA: 1, PASS: 14, STALE: 44, UNSUPPORTED: 11, WARN: 1
BEFORE goose : Counts: EXTRA: 1, STALE: 44, UNSUPPORTED: 24
```

## The 6 Failures in the Affected-Module Set Are Pre-Existing

Six tests fail in the affected-module run. They were **not** caused by this
change, and this is measured rather than asserted: the committed `HEAD` version
of `check_harness_parity.py` was swapped in by file copy (no git index
operation, so the reviewer-staged carryover was untouched) and the same six
node ids were run:

```text
6 failed, 1 warning in 0.52s
FAILED test_check_harness_parity.py::test_repository_registry_covers_project_skills
FAILED test_check_harness_parity.py::test_repository_registry_has_no_unclassified_missing_rows
FAILED test_parity_coverage_complete.py::test_zero_unwaived_asymmetries_live
FAILED test_parity_discovery_diff.py::test_open_asymmetry_resolved_post_slice5
FAILED test_parity_discovery_diff.py::test_doctor_check_passes_on_clean_live_tree
FAILED test_parity_discovery_diff.py::test_doctor_check_fails_on_synthetic_asymmetry
```

Identical set, identical order, at `HEAD`. The working copy was restored and
verified byte-equal afterwards. The regression floor is therefore the full
affected-module set at 91 passed with these six pre-existing failures held
constant — not the new file in isolation.

## Why 24 STALE Remain — the Diagnosis

Every residual row carries one note: `Registry source_sha256 does not match the
canonical source.` That check sits *after* the generator check, so these
capabilities never reached it before; the repair unmasked them.

Measured against `config/agent-control/gtkb-harness-capability-registry.toml`:

- Of 44 goose adapter entries, **20 declared `source_sha256` values match** the
  canonical baseline source and **24 do not**. The 20 matches prove the hash
  algorithm agrees, so the 24 are genuine content drift, not a method mismatch.
- The computed hash is **identical** whether the goose or API marker is used
  (`goose == api` for every sampled entry), so the routing change did not move
  these values.
- All 44 entries point at `.harness-baseline-configuration/`, the correct tree.
- The projections themselves are **current**: `--check` reports `0 drifted of
  127 managed`, and each projected block's `Canonical source sha256` matches the
  current source (e.g. `gtkb-bridge` = `d42f8c4d4fee…` in both).

So the baseline skill sources changed after the registry was stamped, and only
the registry metadata is stale. Codex shows the same class at `STALE 44`,
unchanged before and after this change — evidence the condition is independent
of this repair.

Captured as **WI-6275** rather than absorbed. A blind hash refresh would mask
real drift, so it needs its own proposal and review; the registry is also
outside this thread's `target_paths`.

**The verifier's decision:** whether V1 as literally worded ("zero STALE") is
met-in-substance by "all false positives eliminated, residual rows are true
positives outside scope", or whether this thread must stay open until WI-6275
lands. Prime Builder's position is the former, but the call belongs to review,
and the parent thread's F1 PASS route depends on the answer.

## Author Provenance Correction — `-004` F1

`-004` F1 found that `-003` declared `author_identity: prime-builder/codex`,
`author_harness_id: A` while its header read "harness B", and required the true
values in this report.

**The true authoring harness is `claude`, harness ID `B`**, model
`claude-opus-5`, session context `a49752e4-5a9f-4290-bceb-910693b5271f`. The
header was right; the metadata block was wrong. The same wrong attribution is
on `bridge/gtkb-wi6221-tool-use-is-a-test-directive-003.md`, filed in the same
window.

**Cause, reproduced.** `scripts/bridge_author_metadata.py`
`_resolve_durable_identity_fields` (lines 470-491): when `GTKB_HARNESS_NAME` is
unset and there is no dispatch run-id, it falls back to *the harness holding the
durable `prime-builder` role, narrowed by dispatchability*. Three harnesses hold
that durable role — A/codex, B/claude, G/goose — and the dispatchability filter
selects A. Probed directly:

```text
resolution, empty env (as filed) : {"author_identity": "prime-builder/codex", "author_harness_id": "A"}
resolution, GTKB_HARNESS_NAME=claude: {"author_identity": "prime-builder/claude", "author_harness_id": "B"}
```

This report was filed with `GTKB_HARNESS_NAME=claude` set, so its own metadata
block should read `prime-builder/claude` / `B`; the verifier should confirm that
on the artifact rather than take this paragraph's word for it.

**Why it matters beyond bookkeeping.** Durable registry role is documented as a
routing label, not an identity oracle, and the session-stated interactive role
governs attribution per `DCL-SESSION-ROLE-RESOLUTION-001` and
`GOV-SESSION-ROLE-AUTHORITY-001`. The resolver inverts that. It also fails
silently: the applicability preflight reported `author_metadata_warnings: []`
for a document naming two different harnesses. Review independence was never at
risk — `author_session_context_id` resolved correctly and is the actual
independence key — but an automated consumer cannot reconcile the record.

Captured as **WI-6271** (P1). The attestation service thread
(`gtkb-session-role-attestation-service-slice-1`, GO at `-004`) is the designed
structural fix; WI-6271 records the concrete reproduction and the interim
workaround.

The two affected artifacts are append-only and are not rewritten. The
correction lives here, in the audit trail, per bridge discipline.

## Other Findings Captured at Point of Discovery

Under the directive landed by WI-6221 this session:

- **WI-6272** — `...-20260814B` claims supersession of `...-20260814` in prose
  while `superseded_by` is null and both are active with identical include
  lists.
- **WI-6273** — no authorization template grants the `bridge` mutation class,
  so every new PAUTH permits implementation but blocks its own report step;
  hit and patched three times in this program now.
- **WI-6274** — the worktree carries 565 unstaged and 27 staged deletions of
  tracked files, pre-existing at session start. Mitigated here by pathspec-
  limited commits with the staged count verified at 33 before and after each.
- **WI-6275** — the registry hash drift above.

One further observation, not yet a work item: while editing
`scripts/check_harness_parity.py` a governance banner fired reading "Bridge
proposal for this module has NO-GO status. Review Codex findings at
`bridge/gtkb-adbr-t0-mechanism-repair`". That thread is a 2026-08-08 NO-GO whose
`target_paths` are `config/agent-control/*`, `.claude/rules/**` and
`.claude/skills/*/helpers/**` — it does not touch this module, and a live packet
for this thread was held at the time. This is a live reproduction of the
banner-precedence defect already scoped as D1 of
`gtkb-wi6216-tool-and-gate-defect-corpus-slice-1`, and is recorded here as
evidence for that thread rather than duplicated as a new item.

## Acceptance Criteria Check

| `-004` expectation | Status |
| --- | --- |
| V1 zero STALE on goose | **Not met** — 24 remain, all true positives outside `target_paths`; see diagnosis |
| V2 wrong-digest and missing-block still STALE; tampered body detected | Met |
| V3 API fixture validates a stub; codex re-run shows no regression | Met — codex counts byte-identical |
| V4 both ruff gates run separately on both files | Met |
| F1 author provenance corrected | Met — corrected above with cause and reproduction |

## Commit Discipline

Pathspec-limited to the two target paths. The new test file was staged
individually with `git add -- <path>` because an untracked file cannot be
addressed by a pathspec commit; the staged count went 33 -> 34 -> 33 across the
operation, so the reviewer-staged carryover was neither captured nor disturbed.

## Specification Links

Carried forward unchanged from the `-003` proposal.

- `GOV-HARNESS-NEUTRAL-BASELINE-001` v1 — obligation 2.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — the capability floor parity enforces.
- `SPEC-1662` (GOV-18) — assertion meaningfulness.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v5 — every claim here rests on a fresh
  reproduction recorded in this session.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` v1;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` v1;
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` v1.
- `GOV-FILE-BRIDGE-AUTHORITY-001` v4.

## Owner Decisions / Input

- Owner goal directive (this session): complete GET HEALTHY PHASE 2
  implemented, tested and committed.
- Owner decisions `DELIB-20260814-PHASE2-PAUTH-BRIDGE-MUTATION-CLASS` and
  `DELIB-20260814-PHASE2-PAUTH-BRIDGE-CLASS-NON-B` (AskUserQuestion,
  2026-08-14) added the `bridge` mutation class to both Phase-2 execution
  authorizations, which is what permits this report to be filed at all.
- No new owner decision is requested. The V1 shortfall is a review judgement,
  not an owner waiver request, unless the verifier concludes otherwise.

## Prior Deliberations

- `bridge/gtkb-wi6267-parity-projection-contract-004.md` — the GO on the
  corrected mechanism, and F1 on author provenance.
- `bridge/gtkb-wi6267-parity-projection-contract-003.md` — the corrected
  four-mechanism scope this implements.
- `bridge/gtkb-wi6267-parity-projection-contract-002.md` — the earlier GO on
  the two-mechanism scope, superseded.
- `bridge/gtkb-baseline-correction-and-goose-projector-slice-1-006.md` — F1,
  whose PASS route depends on this thread; the V1 question above determines
  whether that route is now open.
- `bridge/gtkb-lo-tooling-defect-advisory-014.md` — the misreporting-instrument
  inventory; M3, M4 and the banner false positive are further members.

## Recommended Commit Type

`fix` — repairs incorrect checker behaviour with regression tests. Landed as
`fix(parity): ...` at `63add93e2`; 320 insertions of which the majority is the
new test module, no new capability surface, so `fix` matches the diff stat.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
