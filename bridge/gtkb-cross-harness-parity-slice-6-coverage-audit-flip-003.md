NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 0eb73a79-4ad6-40c0-88e9-16f797f0ef2e
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive Prime Builder

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION
Project: PROJECT-GTKB-CROSS-HARNESS-PARITY
Work Item: WI-4892

Document: gtkb-cross-harness-parity-slice-6-coverage-audit-flip
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-06-27 UTC
Responds to: bridge/gtkb-cross-harness-parity-slice-6-coverage-audit-flip-002.md (GO)
Recommended commit type: feat

target_paths: ["config/agent-control/harness-capability-registry.toml", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", ".github/workflows/groundtruth-kb-tests.yml", "platform_tests/scripts/test_parity_discovery_diff.py", "platform_tests/scripts/test_parity_coverage_complete.py"]

## Post-Implementation Report

Implementation of Slice 6 (`WI-4892`, the final slice) per the GO at `-002`. All
five `target_paths` implemented within scope. The coverage audit is **complete**:
the discovery-diff reports **0 unwaived asymmetries** and the enforcement is now
mandatory. The cross-harness behavioral-parity program (Slices 1–6) is fully
implemented: detect → prevent → conform → **gate**.

## What Was Built

1. **`config/agent-control/harness-capability-registry.toml`** — added **22
   capabilities + 18 typed `[[parity_waivers]]`** (deterministically generated;
   surfaces + rationale per `DELIB-20266285`):
   - **Group A (4 unifications)** — one capability with both per-harness surfaces
     each: `hook.directive-enforcement`, `hook.formal-artifact-approval`,
     `hook.sot-read-discipline`, `hook.wi-id-collision-gate` (resolves 8 findings).
   - **Group B (3 codex-only) + Group C (15 claude-only)** — single-harness
     capability + a typed waiver for the absent harness
     (`owner_approval_ref = "DELIB-20266285"`, `review_trigger` set; reason_class
     `hard-limitation` for the apply_patch adapter, else `harness-surface-difference`).
   `last_updated` bumped; `--validate-schema` clean.
2. **`groundtruth-kb/src/groundtruth_kb/project/doctor.py`** — promoted
   `_check_parity_discovery_diff`: an unwaived asymmetry now returns
   `status="fail"` (was `warning`); 0 unwaived → `pass`; run/config errors stay
   fail-soft `warning`.
3. **`.github/workflows/groundtruth-kb-tests.yml`** — added a
   "Cross-harness parity discovery-diff hard gate" step
   (`python scripts/parity_discovery_diff.py`, exits non-zero on asymmetry) and
   expanded the path triggers to the parity surfaces (registry, diff script,
   `.claude/settings.json`, `.codex/hooks.json`, `platform_tests/scripts/test_parity_*`).
4. **`platform_tests/scripts/test_parity_discovery_diff.py`** — flipped the
   doctor-check test: `test_doctor_check_passes_on_clean_live_tree` (0 unwaived →
   `pass`, the regression guard) + `test_doctor_check_fails_on_synthetic_asymmetry`
   (tmp tree with copied diff scripts + live projection + an asymmetric config →
   `fail`).
5. **`platform_tests/scripts/test_parity_coverage_complete.py`** (new) — asserts
   0 unwaived asymmetries live, every waiver validates + cites `owner_approval_ref`,
   and the full schema is valid.

## Specification Links (carried forward)

- `ADR-CROSS-HARNESS-PARITY-001` (§5 step 6 final enforcement; Q4 applicability;
  Q7 typed-waiver discipline).
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — **PARITY-DIFF-WIRED** completed
  (doctor FAIL + CI hard gate); **PARITY-WAIVER-SCHEMA** exercised by the 18
  waivers; **PARITY-APPLICABILITY-RULE** by the unifications.
- `GOV-20`; `GOV-FILE-BRIDGE-AUTHORITY-001`;
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`;
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001`;
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory).

## Requirement Sufficiency

Existing requirements sufficient. The slice completes the already-specified §5
step 6 enforcement + PARITY-DIFF-WIRED / PARITY-WAIVER-SCHEMA assertions; the
batch waiver is owner-approved (`DELIB-20266285`). No new requirement introduced.

## Cross-Harness Disposition

`target_paths` do NOT touch the harness-surface marker set; they are the
capability registry, the platform doctor, the platform CI workflow, and platform
tests — harness-agnostic. Declared proactively: **universal** applicability, no
per-harness runtime divergence; the registry edits encode the owner-approved
per-harness waiver dispositions (the explicit opposite of an undeclared
asymmetry). **In-root:** all artifacts (the `groundtruth-kb/src/...` doctor edit,
the registry, the CI workflow, the tests, this bridge file) are written in-root
under the GT-KB project root; the diff emits to stdout / an in-root path.
**Waivers:** the 18 owner-approved typed waivers under `DELIB-20266285`.

## Spec-to-Test Mapping + Verification Evidence

| Linked assertion | Derived test(s) | Result |
|---|---|---|
| PARITY-DIFF-WIRED (doctor FAIL) | `test_doctor_check_passes_on_clean_live_tree`, `test_doctor_check_fails_on_synthetic_asymmetry` | PASS |
| PARITY-DIFF-WIRED (CI hard gate) | `groundtruth-kb-tests.yml` step runs `scripts/parity_discovery_diff.py` (exit 0 verified) | PASS |
| PARITY-WAIVER-SCHEMA (18 waivers valid + owner_approval_ref) | `test_every_waiver_validates_and_cites_owner_ref` | PASS |
| Coverage complete (0 unwaived) | `test_zero_unwaived_asymmetries_live`, `test_full_parity_schema_valid_live` | PASS |
| PARITY-APPLICABILITY-RULE (unifications) | full parity suite + `--validate-schema` | PASS |
| Behavior preservation | Slice 2/3/5 parity suites | PASS |

Commands run and observed results:

- `python -m pytest platform_tests/scripts/test_parity_discovery_diff.py platform_tests/scripts/test_parity_coverage_complete.py platform_tests/scripts/test_session_topic_envelope_router.py platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_cross_harness_parity_schema.py -q`
  → **47 passed**.
- `python scripts/parity_discovery_diff.py` → **Unwaived asymmetries: 0**; CLI
  **exit 0** (the CI hard gate passes).
- `python scripts/check_harness_parity.py --validate-schema` → **parity schema OK**.
- `gt project doctor` → `[OK] no unwaived cross-harness hook asymmetry
  (population: claude, codex)` — the check is now FAIL-promoted and PASSes on the
  clean tree (and FAILs on a synthetic asymmetry, per the test).
- `ruff check <changed>` → **All checks passed**; `ruff format --check` → clean.

Note (non-blocking): the 4 pre-existing `-k bridge_compliance` failures (WI-4890)
are unrelated to parity and out of scope per GOV-15.

## Acceptance Criteria

- ✅ All 26 asymmetries resolved (4 unify) or owner-waived (18 typed waivers) →
  discovery-diff reports 0 unwaived.
- ✅ Doctor `_check_parity_discovery_diff` promoted WARN→FAIL (PASS on clean,
  FAIL on asymmetry).
- ✅ Release/CI hard gate added (CI step runs the diff CLI).
- ✅ Every waiver validates + cites `DELIB-20266285`.

## Owner Decisions / Input

Both owner decisions captured via AskUserQuestion on 2026-06-27: full Slice 6
(audit all 26 + flip) AND batch-waive Groups B+C as harness-surface-difference,
recorded as **`DELIB-20266285`** (`AUQ-S20260627-PARITY-SLICE6-GROUPC-BATCH-WAIVE`,
answer "Batch-waive all as harness-difference") — the `owner_approval_ref` cited
by every waiver. Implementation authority flows from
`PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION` (active), with **WI-4892**
the active project member. Registry/doctor/CI/tests are platform code/config (no
GOV/ADR/DCL/SPEC artifact, no protected narrative file), so no formal-artifact
approval packet is required.

## Prior Deliberations

- `DELIB-20266285` — the owner batch-waiver decision (the waiver authority + full
  per-hook disposition table).
- `bridge/gtkb-cross-harness-parity-slice-6-coverage-audit-flip-002.md` — the GO
  this report responds to (Cursor LO, harness E; separation check passed).
- `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY` — §5 step 6 + §3 Q6 ramp + Q7.
- `bridge/gtkb-cross-harness-parity-slice-3-discovery-diff-004.md` — the
  discovery-diff + doctor WARN this slice promotes to FAIL.
- `bridge/gtkb-cross-harness-parity-slice-5-open-conformance-006.md` — Slice-5
  VERIFIED (27→26).

## Recommended Commit Type

`feat:` — completes the parity enforcement (registry coverage audit + doctor
WARN→FAIL + CI hard gate + tests). On this VERIFIED the program is complete and
`PROJECT-GTKB-CROSS-HARNESS-PARITY` auto-retires.
