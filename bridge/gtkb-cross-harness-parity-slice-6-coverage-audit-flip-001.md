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
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-27 UTC
Recommended commit type: feat

target_paths: ["config/agent-control/harness-capability-registry.toml", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", ".github/workflows/groundtruth-kb-tests.yml", "platform_tests/scripts/test_parity_discovery_diff.py", "platform_tests/scripts/test_parity_coverage_complete.py"]

## Summary

Slice 6 (final) of `PROJECT-GTKB-CROSS-HARNESS-PARITY` completes the coverage
audit of the 26 remaining discovery-diff hook-surface asymmetries and promotes
the enforcement from advisory to mandatory (advisory §5 step 6 / Q6 ramp):

1. **Resolve Group A (4 naming-pairs)** by registering unifying capabilities
   with both per-harness surfaces.
2. **Register-and-waive Groups B+C (18 hooks)** as Slice-2 typed waivers under
   the owner-approval reference `DELIB-20266285` (owner AUQ 2026-06-27
   "Batch-waive all as harness-difference").
3. **Promote the doctor check `_check_parity_discovery_diff` WARN→FAIL** — after
   (1)+(2) the diff reports **0 unwaived asymmetries**, so the check can fail
   hard on any future regression.
4. **Add a release/CI hard gate** — a step in `groundtruth-kb-tests.yml` runs
   `python scripts/parity_discovery_diff.py` (exit non-zero on unwaived
   asymmetry), plus a coverage-completeness regression test.

After this slice the cross-harness behavioral-parity invariant is fully
enforced: detect (Slice 3) → prevent (Slice 4) → conform (Slice 5) → **gate**
(Slice 6).

## Specification Links

- `ADR-CROSS-HARNESS-PARITY-001` (accepted) — the invariant; §5 step 6 final
  enforcement (doctor WARN→FAIL + release/CI hard gate); Q4 applicability +
  Q7 typed-waiver discipline.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` (specified) — assertion
  **PARITY-DIFF-WIRED** (Slices 3, 6: doctor WARN then FAIL + release/CI hard
  gate) is completed here; **PARITY-WAIVER-SCHEMA** is exercised by the 18 typed
  waivers; **PARITY-APPLICABILITY-RULE** by the unifications.
- `GOV-20`; `GOV-FILE-BRIDGE-AUTHORITY-001`;
  `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`;
  `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`;
  `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (doctor.py edit is platform-internal,
  in-root); `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
  (advisory).

The proposed tests derive from the linked specs: the coverage-completeness test
maps to PARITY-DIFF-WIRED + PARITY-WAIVER-SCHEMA; the updated doctor-check test
maps to the WARN→FAIL promotion.

## Requirement Sufficiency

Existing requirements sufficient. The slice completes the already-specified §5
step 6 enforcement and the PARITY-DIFF-WIRED / PARITY-WAIVER-SCHEMA assertions.
No new or revised requirement is introduced; the batch waiver is owner-approved
(`DELIB-20266285`).

## Cross-Harness Disposition

`target_paths` do NOT touch the harness-surface marker set
(`.claude/settings.json`, `.codex/hooks.json`, `.claude/hooks/**`,
`.codex/gtkb-hooks/**`, skills dirs) — they are the capability registry, the
platform doctor, the platform CI workflow, and platform tests, all
harness-agnostic. The disposition is declared proactively: the change has
**universal** applicability, introduces no per-harness runtime divergence, and
the registry edits encode the owner-approved per-harness waiver dispositions.
All artifacts are written in-root under the GT-KB project root. The 18 waivers
are the explicit, owner-approved declarations of legitimate harness-surface
difference (the opposite of an undeclared asymmetry).

## Design

### A. Registry — `config/agent-control/harness-capability-registry.toml`

**Group A — 4 unifying capabilities** (each `kind="hook"`,
`applicability="universal"`, with `[capabilities.claude]` + `[capabilities.codex]`
surfaces), resolving 8 findings:

| capability id | claude surface | codex surface |
|---|---|---|
| `hook.directive-enforcement` | `.claude/hooks/directive-enforcement-claude-adapter.py` | `.codex/gtkb-hooks/directive-enforcement.cmd` |
| `hook.formal-artifact-approval` | `.claude/hooks/formal-artifact-approval-gate.py` | `.codex/gtkb-hooks/formal-artifact-approval.cmd` |
| `hook.sot-read-discipline` | `.claude/hooks/sot-read-discipline.py` | `.codex/gtkb-hooks/sot-read-discipline-bash-adapter.py` |
| `hook.wi-id-collision-gate` | `.claude/hooks/bridge-proposal-wi-id-collision-gate.py` | `.codex/gtkb-hooks/wi-id-collision-gate.cmd` |

**Groups B+C — 18 single-harness capabilities + 18 `[[parity_waivers]]` records**
(each waiver: `capability_id`, `harness` = the absent harness, `reason_class`,
`rationale`, `owner_approval_ref = "DELIB-20266285"`, `review_trigger`). Group B
(3, codex-present / claude-waived): `bridge-compliance-gate-apply-patch-adapter`
(hard-limitation), `codex-mcp-worker-guard`, `bridge-compliance-audit`
(harness-surface-difference). Group C (15, claude-present / codex-waived):
`assertion-check`, `bridge-axis-2-surface`, `delib-search-gate`,
`delib-search-tracker`, `dispatch_blackbox_gate`, `gov09-capture`,
`intake-classifier`, `kb-not-markdown`, `narrative-artifact-approval-gate`,
`owner-decision-capture`, `owner-decision-tracker`, `scanner-safe-writer`,
`session-start-governance`, `session_self_initialization`, `spec-before-code`
(all harness-surface-difference; per-hook rationale in `DELIB-20266285`).

`last_updated` bumped. After this edit `scripts/check_harness_parity.py
--validate-schema` stays clean and `parity_discovery_diff` reports **0 unwaived
asymmetries**.

### B. Doctor WARN→FAIL — `groundtruth-kb/src/groundtruth_kb/project/doctor.py`

Promote `_check_parity_discovery_diff`: an unwaived asymmetry now returns
`status="fail"` (was `warning`); 0 unwaived returns `pass`; run/config errors
stay fail-soft `warning`. Update the message to drop the "WARN at Slice 3"
framing. This makes `gt project doctor` fail hard on any future undeclared
cross-harness asymmetry.

### C. Release/CI hard gate — `.github/workflows/groundtruth-kb-tests.yml`

Add a step that runs `python scripts/parity_discovery_diff.py` (the CLI already
exits non-zero on unwaived asymmetry), failing the platform test job on any
regression — an explicit CI hard gate independent of the doctor.

### D. Tests

- `platform_tests/scripts/test_parity_discovery_diff.py` (update): flip
  `test_doctor_check_warns_on_live_asymmetry_never_fails` to assert the check is
  now FAIL-capable — `pass` on the clean live tree (0 unwaived), and `fail` (not
  `warning`) on a synthetic unwaived-asymmetry fixture.
- `platform_tests/scripts/test_parity_coverage_complete.py` (new): assert
  `run_discovery_diff(PROJECT_ROOT).overall_status == "PASS"` (0 unwaived) and
  that every `[[parity_waivers]]` record validates (`validate_parity_waiver`) and
  cites `owner_approval_ref` — the coverage-completeness CI gate.

## Test Plan / Spec-Derived Verification

| Linked spec / assertion | Derived test | Command |
|---|---|---|
| PARITY-DIFF-WIRED (doctor FAIL + CI gate) | flipped doctor-check test + coverage-complete test | `python -m pytest platform_tests/scripts/test_parity_discovery_diff.py platform_tests/scripts/test_parity_coverage_complete.py -q` |
| PARITY-WAIVER-SCHEMA (18 waivers valid) | coverage-complete waiver-validation test | `python -m pytest platform_tests/scripts/test_parity_coverage_complete.py -q` |
| PARITY-APPLICABILITY-RULE (unifications) | schema-valid + diff clean | `python scripts/check_harness_parity.py --validate-schema` |
| Diff clean (0 unwaived) | `python scripts/parity_discovery_diff.py` exits 0 | `python scripts/parity_discovery_diff.py` |
| Behavior preservation | Slice 2/3/5 parity suites green | `python -m pytest platform_tests/scripts/test_parity_discovery_diff.py platform_tests/scripts/test_check_harness_parity.py platform_tests/scripts/test_cross_harness_parity_schema.py platform_tests/scripts/test_session_topic_envelope_router.py -q` |
| Lint + format | changed files clean | `ruff check <changed>` and `ruff format --check <changed>` |

Acceptance: `parity_discovery_diff` reports 0 unwaived asymmetries; `gt project
doctor` shows the parity check at PASS (and would FAIL on a synthetic
regression); the CI step runs the diff as a hard gate; all 18 waivers validate
and cite `DELIB-20266285`; existing parity suites stay green.

## Owner Decisions / Input

The batch-waiver of Groups B+C is owner-approved via AskUserQuestion on
2026-06-27 (`AUQ-S20260627-PARITY-SLICE6-GROUPC-BATCH-WAIVE`, answer
"Batch-waive all as harness-difference"), captured as `DELIB-20266285` — the
`owner_approval_ref` cited by every waiver record. The owner separately approved
the full-Slice-6 scope (audit all 26 + flip) via AUQ. Implementation authority
flows from `PAUTH-PROJECT-GTKB-CROSS-HARNESS-PARITY-IMPLEMENTATION` (active),
with **WI-4892** the active project member. The registry, doctor, CI workflow,
and tests are platform code/config (no GOV/ADR/DCL/SPEC artifact, no protected
narrative file), so no formal-artifact approval packet is required.

## Prior Deliberations

- `DELIB-20266285` — the owner batch-waiver decision (this slice's waiver
  authority) with the full per-hook disposition table.
- `DELIB-S20260626-CROSS-HARNESS-PARITY-ADVISORY` — §5 step 6 (final
  enforcement) + §3 Q6 (WARN→FAIL ramp + release/CI hard gate) + Q7 (typed
  waivers).
- `DELIB-S20260626-PARITY-INTERVIEW-CLUSTER2-ENFORCEMENT` — Q5-Q8 enforcement.
- `bridge/gtkb-cross-harness-parity-slice-3-discovery-diff-004.md` — the
  discovery-diff + doctor WARN this slice promotes.
- `bridge/gtkb-cross-harness-parity-slice-5-open-conformance-006.md` — Slice-5
  VERIFIED; the first conformance case that took the count 27→26.

## Risk / Rollback

- **Risk:** promoting the doctor to FAIL could block `gt project doctor` if a
  waiver is malformed or a unification is wrong. *Mitigation:* the
  coverage-complete test + `--validate-schema` + the live diff run are all green
  before the flip; the check stays fail-soft `warning` on run/config errors
  (only a genuine unwaived asymmetry is `fail`).
- **Risk:** a waiver hides a real future conform-need. *Mitigation:* every waiver
  carries a `review_trigger` so it resurfaces at the next parity audit; the
  batch is owner-approved and documented per-hook in `DELIB-20266285`.
- **Risk:** the CI workflow edit breaks the platform test job. *Mitigation:* the
  added step is a single isolated `run:` invoking the diff CLI; it fails only on
  unwaived asymmetry (currently 0).
- **Rollback:** revert the registry capability+waiver additions, the doctor
  FAIL promotion, the CI step, and the test updates; the diff reverts to 26
  WARN-level findings (the post-Slice-5 state). No governance residue
  (`DELIB-20266285` remains as an archived decision).
