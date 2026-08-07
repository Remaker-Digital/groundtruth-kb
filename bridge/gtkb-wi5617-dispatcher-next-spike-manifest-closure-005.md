NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 7c5bf02a-db61-459e-9321-695a31696526
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: implementation_report
Document: gtkb-wi5617-dispatcher-next-spike-manifest-closure
Version: 005
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi5617-dispatcher-next-spike-manifest-closure-004.md
Approved proposal: bridge/gtkb-wi5617-dispatcher-next-spike-manifest-closure-003.md

Project Authorization: PAUTH-DISPATCHER-NEXT-PROGRAM-20260719
Project: PROJECT-GTKB-DISPATCHER-NEXT-CONTROL-PLANE
Work Item: WI-5617

target_paths: ["config/dispatcher/requirements-dispatcher-next-spike.txt", "platform_tests/groundtruth_kb/test_dispatcher_next_spike_manifest.py"]
implementation_scope: source_and_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

**No KB mutation.** This implementation performed no MemBase write and did not modify
`groundtruth.db`.
**No approval-evidence work.** No formal-artifact-approval packet was created and no
approval-packet path was written.
**No dispatcher or TAFE mutation.** No dispatcher configuration, substrate, scheduled task,
routing rule, or harness registry entry was changed. The file added under
`config/dispatcher/` is a dependency-pin manifest; it is read by no dispatcher code. The
legacy TAFE/dispatcher remains quiesced per `DELIB-20260806011871`.

# WI-5617 - Implementation Report: Dispatcher Next spike manifest declared

## Verification Request

Post-implementation report for the `GO` at
`bridge/gtkb-wi5617-dispatcher-next-spike-manifest-closure-004.md`, approving the REVISED
proposal at `-003`. Implemented by session `7c5bf02a-db61-459e-9321-695a31696526`
(Claude harness B) under implementation-start packet
`.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5617-dispatcher-next-spike-manifest-closure.json`.

This closes the sole surviving blocker of the Dispatcher Next foundation spike.

## Root Boundary Compliance

All artifacts are in-root under `E:/GT-KB`. Both created files are in-root platform paths
and this bridge file resides under `E:/GT-KB/bridge/`. No `applications/` path is touched.

## Specification Links

Carried forward verbatim from `-003`; no link added, dropped, or reinterpreted.

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority for this thread.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - discharged by the PAUTH v5 binding above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - discharged by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - discharged by the Spec-to-Test Mapping
  below.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - platform surfaces only.
- `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`,
  `.claude/rules/project-root-boundary.md`.
- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - owner decision behind the
  program authorization.

## Prior Deliberations

Carried forward from `-001`/`-003`, plus implementation-time findings:

- `DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION` - master program authorization.
- `DELIB-20260806011871` - legacy TAFE/dispatcher quiesce; scoped to exclude Dispatcher Next.
- `WI-5966` - `.txt` is unclassifiable by extension; the original cohort path could never be
  authorized. This is why the manifest had never been created.
- `WI-5972` - the two-classifier gap that made `-001`'s first relocation unimplementable.
- `WI-5827` - the wedged-thread survey; adjacent context for the foundation thread.

## Requirement Sufficiency

Existing requirements sufficient, unchanged from `-003`. No requirement was created or
revised.

## Implemented Change

### C1 - Pinned-dependency manifest created

`config/dispatcher/requirements-dispatcher-next-spike.txt` declares exactly the two pins the
foundation asserts at runtime:

```
dbos==2.27.0
a2a-sdk==1.1.1
```

Values were read from `dependency_versions()` at implementation time rather than
transcribed, then pinned by the guard below.

The header comment records why the file exists (the asserted environment must be
reconstructable) and why it lives here rather than at the package root, citing WI-5966 and
WI-5972 so a future reader does not "tidy" it back to an unauthorizable location.

### C2 - Drift guard created

`platform_tests/groundtruth_kb/test_dispatcher_next_spike_manifest.py` asserts the manifest
and `dependency_versions()` agree exactly, in both directions, and that every manifest line
is an exact `==` pin. A manifest that disagreed with the code would be worse than no
manifest, so the guard tests set-equality per-name and per-version, not merely presence.

### Files changed

| File | Change |
| --- | --- |
| `config/dispatcher/requirements-dispatcher-next-spike.txt` | new; 2 pins + provenance header |
| `platform_tests/groundtruth_kb/test_dispatcher_next_spike_manifest.py` | new; 10 tests |

No `dispatcher_next/` source file was modified. The five previously-existing cohort targets
are untouched.

## Spec-to-Test Mapping

| Spec / acceptance criterion | Test | Result |
| --- | --- | --- |
| AC1 - manifest exists, completing the cohort | `test_t1_manifest_exists_and_declares_pins` | PASS |
| AC2 - pins equal `dependency_versions()` in both directions (`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`) | `test_t2_manifest_matches_dependency_versions_exactly`, `test_t3_no_pin_missing_from_manifest`, `test_t3b_no_extra_pin_in_manifest`, `test_t3c_versions_agree_per_dependency` | PASS |
| AC3 - every line is an exact `==` pin | `test_t4_every_pin_is_an_exact_equality_pin`, `test_t4b_parser_rejects_non_exact_pins` | PASS |
| AC4 - no regression in the foundation suite | `platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py` | PASS (11 passed - identical to the pre-change baseline) |
| AC5 - both ruff gates pass | `ruff check` / `ruff format --check` | PASS (exit 0 / exit 0) |

`test_t4b` is included because a drift guard is only meaningful if its parser would actually
reject drift; it asserts the pin regex rejects `>=`, bare names, `~=`, and `<`.

## Commands Executed

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_dispatcher_next_spike_manifest.py -q
  -> 10 passed, 1 warning in 0.98s

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/groundtruth_kb/test_dispatcher_next_foundation.py -q
  -> 11 passed, 1 warning in 33.91s

groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/groundtruth_kb/test_dispatcher_next_spike_manifest.py
  -> All checks passed!  (exit 0)

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/groundtruth_kb/test_dispatcher_next_spike_manifest.py
  -> 1 file already formatted  (exit 0)
```

The foundation suite's 11 passed is byte-identical to the baseline recorded in `-001`
(11 passed in 23.97s), confirming the additive change disturbs nothing.

## Acceptance Criteria Check

| # | Criterion | Status | Evidence |
| --- | --- | --- | --- |
| 1 | Manifest exists at the authorizable path, completing the sixth cohort target | MET | T1; file created at `config/dispatcher/requirements-dispatcher-next-spike.txt` |
| 2 | Pins equal `dependency_versions()` exactly, both directions | MET | T2, T3, T3b, T3c |
| 3 | Every manifest line is an exact `==` pin | MET | T4, T4b |
| 4 | Foundation suite shows no regression | MET | 11 passed, matching baseline |
| 5 | Both ruff gates pass | MET | exit 0 / exit 0 |

All five criteria met. No criterion is waived or partially met.

## Relocation Confirmed Working

`-003` relocated the manifest to `config/dispatcher/` after `-001`'s
`config/dispatcher-next/` path proved unimplementable (WI-5972: it satisfied
`classify_target` but not `classify_root`). That relocation is now confirmed empirically -
the file Write succeeded on the first attempt with no work-subject refusal, and the
implementation-start packet minted cleanly against the declared cohort. Both classifiers
accept the path in practice, not only in the pre-measurement.

## Downstream Effect

The Dispatcher Next foundation cohort is now complete: all six targets exist, and the
foundation suite passes. On `VERIFIED`, WI-5617's substantive blocker is closed.

**One caveat, disclosed rather than implied:** closing this cohort does not by itself make
the historical thread `gtkb-dispatcher-next-foundation-spike` resolvable. That thread carries
two correction-eligible entries (`-002` decorated status token, `-013` out-of-role
`VERIFIED`) and is handled separately under WI-5967, whose own REVISED at
`bridge/gtkb-wi5967-verdict-role-transition-guard-and-correction-003.md` withdraws the
earlier claim that a single corrective chain would unwedge it. WI-5618's stated precondition
is "after WI-5617 proves the substrate"; the substrate is proven and now fully declared, but
the reviewer should be aware the historical thread remains separately blocked.

## Risk and Rollback

- **Risk: the manifest drifts from the constants.** The material risk, since a wrong manifest
  is worse than none. Mitigated by T2/T3/T3b/T3c, which fail on any divergence in either
  direction.
- **Risk: pins captured from a stale environment.** Values were read from
  `dependency_versions()` at implementation time and are asserted equal by the guard, so a
  stale transcription cannot survive the test.
- **Risk: someone relocates the manifest back to a "conventional" package root.** Mitigated
  by the header comment recording WI-5966 and WI-5972 with the reason.
- **Rollback:** delete both files. The change is purely additive; the foundation suite passes
  without them (it did before this change).

## Loyal Opposition Asks

1. Confirm the manifest matches `dependency_versions()` and that the drift guard would
   actually catch divergence (T2-T3c, T4b).
2. Confirm the foundation suite result is a true non-regression against the `-001` baseline.
3. Return `VERIFIED` only if all five acceptance criteria are satisfied; otherwise `NO-GO`
   with exact findings.

## Owner Decisions / Input

No new owner decision was required or taken for this implementation.

- **Owner directive 2026-08-06:** "Prioritize the Dispatcher Next program and drive it to
  completion", and "rehome and drive it". This work is the first substantive step of that
  directive.
- **`DELIB-20260719-DISPATCHER-NEXT-MASTER-PB-AUTHORIZATION`** - owner decision behind
  `PAUTH-DISPATCHER-NEXT-PROGRAM-20260719`, the authorization this work files under.
- **`DELIB-20260806011871`** - legacy TAFE/dispatcher quiesce, scoped to exclude the
  Dispatcher Next program.

## Recommended Commit Type

`feat:` - the change adds a new declared artifact (the pinned-dependency manifest) plus its
guard test. Not `chore:` because the manifest is a load-bearing reproducibility declaration
for a P0 program foundation; not `fix:` because no previously-working behaviour was broken.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
