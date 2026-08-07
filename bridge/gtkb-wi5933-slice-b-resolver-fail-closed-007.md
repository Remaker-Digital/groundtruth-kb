REVISED
::init gtkb pb
::open build

author_identity: prime-builder/goose/G
author_harness_id: G
author_session_context_id: G-2026-08-06T00-56-43Z
author_model: DeepSeek V4 Flash 0731
author_model_version: deepseek-v4-flash-0731
author_model_configuration: goose-desktop-interactive; role=prime-builder; ::init gtkb pb; build activity
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: prime_proposal
Document: gtkb-wi5933-slice-b-resolver-fail-closed
Version: 007 (REVISED; owner-authorized scope expansion under Option A2)
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi5933-slice-b-resolver-fail-closed-006.md
Prior GO: bridge/gtkb-wi5933-slice-b-resolver-fail-closed-006.md
Prior design GOs: bridge/gtkb-wi5933-slice-b-resolver-fail-closed-002.md, -004.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5933

target_paths: ["scripts/session_role_resolution.py", ".claude/hooks/bridge-axis-2-surface.py", "config/hooks/gtkb-bridge-axis-2-surface.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/hooks/test_session_role_resolution.py", "platform_tests/scripts/test_session_role_resolution_table.py", "platform_tests/scripts/test_dcl_role_resolution_authority_001.py"]

**No KB mutation.** This slice performs no MemBase/KB write and does not modify
`groundtruth.db`. It changes source, harness-hook, and test files only.

**No approval-evidence work.** This slice creates no formal-artifact-approval packet and modifies no approval-packet path.

# WI-5933 Slice B REVISED (007) - owner-authorized scope expansion (Option A2)

## Why This Revision Exists

This revision is filed by the acting Prime Builder (harness G, goose) under an
explicit owner decision (Option A2) to expand the WI-5933 Slice B target cohort
a second time, adding `platform_tests/scripts/test_dcl_role_resolution_authority_001.py`.

The `-006` GO and the `-003`/`-005` design are accepted unchanged in substance.
C1/C2/C4/C5 and the C3 proof obligation are exactly as approved. This revision
makes one additional scope change and records no design drift.

## Scope Change (Option A2)

`platform_tests/scripts/test_dcl_role_resolution_authority_001.py` is added to
`target_paths`. Rationale (verified live):

- The `-003`/`-005`/`-007` mandatory command lists run this module (e.g.
  `-003` line 219: `pytest ... test_dcl_role_resolution_authority_001.py
  test_session_role_resolution_table.py ...`), but it was omitted from
  `declared_target_paths` even after the Option A expansion.
- Its R1/R2 behavioral tests (`test_r1_marker_role_wins_over_mismatched_durable`,
  `test_r2_registry_is_fallback_only`) assert the OLD durable-substitution
  behavior: on absent marker they require `role in (ROLE_PRIME, ROLE_LO)` and
  treat the durable registry role as the fallback.
- C1/T1 require the resolver to fail closed (`role is None`) on absent/invalid/stale
  evidence and never return the durable role. Implementing C1 therefore breaks
  R1/R2 unless those assertions are updated.
- Editing a file outside `declared_target_paths` would be a PAUTH scope violation.
  The owner selected **Option A2** to expand the cohort so R1/R2 can be updated to
  the new fail-closed semantics.

Two tests in that module (`test_gov_session_role_authority_001_dispatcher_only`
and `test_dcl_session_role_resolution_001_enforcement_gate_split`) are
**pre-existing** MemBase spec-content assertions, independent of the resolver
change; they are not modified by this slice and their pre-existing status is
disclosed in the implementation report.

This is the only additional scope change. The prior six targets are unchanged.

## Adoption of In-Progress Source Edits (unchanged)

`scripts/session_role_resolution.py`, `.claude/hooks/bridge-axis-2-surface.py`,
and `config/hooks/gtkb-bridge-axis-2-surface.py` carry the adopted C1/C2/C4
implementation baseline (verified py_compile + ruff clean). This revision
reaffirms that baseline and the completed six-file test cohort.

## Authority Verification (unchanged from `-005`)

- `GOV-SESSION-ROLE-AUTHORITY-001` is deliberately absent: verified retired (v6).
- `DCL-SESSION-ROLE-RESOLUTION-001` v7 (`status: specified`, approved 2026-07-29)
  is the controlling constraint, plus assertions `ROLE-DCL-A5` and `ROLE-DCL-A6`.
- The WI-5679 packet-completeness question is not adjudicated here.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority for this thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - discharged by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Test Plan maps each v7 clause to a test.
- `DCL-SESSION-ROLE-RESOLUTION-001` **v7** (`status: specified`; approved 2026-07-29) - the controlling constraint, plus assertions `ROLE-DCL-A5` and `ROLE-DCL-A6`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - platform/application placement boundary.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` and `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - transcript-defined role persistence, preserved by C5.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and `ADR-CROSS-HARNESS-PARITY-001` - both AXIS-2 copies updated in lockstep.
- `.claude/rules/file-bridge-protocol.md` section Review Independence Boundary.
- `.claude/rules/project-root-boundary.md` - in-root containment.
- `DELIB-202667721` - owner decision behind the whole-project authorization.

`GOV-SESSION-ROLE-AUTHORITY-001` is **deliberately absent**: verified retired (v6).

## Problem Statement (unchanged from `-001`/`-003`/`-005`)

`DCL-SESSION-ROLE-RESOLUTION-001` v7:

> When explicit session-role identity cannot be resolved from the current
> session's validated transcript or session envelope, resolution fails closed
> with a typed recovery result. It MUST NOT substitute the durable registry role
> and MUST NOT emit `session_resolver_fallback`.

## Requirement Sufficiency

**Existing requirements sufficient.** `DCL-SESSION-ROLE-RESOLUTION-001` v7 is
recorded in MemBase as `specified` and was approved on 2026-07-29. This slice is
source conformance to an existing constraint plus an owner-authorized test-cohort
expansion. No new requirement is implied and no DCL amendment is proposed.

## Proposed Change (unchanged from `-005`; scope expanded a second time)

- **C1** - remove the `_durable_role` substitution; return typed unresolved
  (`role_profile = None`) when explicit evidence is absent, invalid, or stale,
  preserving `durable_*` source strings.
- **C2** - remove `durable_registry_role`/`durable_registry_authority` from
  `resolve_interactive_session_role_details`; recompute `authority_mode` without a
  durable-fallback branch.
- **C3** - verification only: prove no production emitter of `session_resolver_fallback`
  remains (envelope-path removal belongs to WI-5723).
- **C4** - both AXIS-2 copies suppress the surface on an unresolved result.
- **C5** - preserve transcript-role persistence.

## Cross-Harness Disposition

The behavioural change lives in the shared `scripts/session_role_resolution.py`,
which every harness consumes, so resolver semantics are identical across harnesses
by construction.

| Harness | Surface | Disposition |
| --- | --- | --- |
| B claude | `.claude/hooks/bridge-axis-2-surface.py` | **Updated (C4).** Unresolved suppresses the surface. |
| (tracked mirror) | `config/hooks/gtkb-bridge-axis-2-surface.py` | **Updated in lockstep**; parity asserted by T5. |
| A codex | `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` | **Parity, no edit.** |
| shared | `lo-file-safety-gate.py` / `gtkb-lo-file-safety-gate.py` | **Parity, no edit.** `durable_*` preserved. |
| C-H other harnesses | no harness-local role-resolution surface | **Parity via the shared resolver.** |

No owner-approved typed waiver is requested.

## Test Plan (specification-derived; T8/T9 added)

| Test | Derived from | Asserts |
| --- | --- | --- |
| T1 | v7 no-substitution clause | no explicit evidence -> resolver returns `None`, never durable role |
| T2 | v7 forbidden-label clause | no production path emits `session_resolver_fallback` (C3 proof) |
| T3 | `ROLE-DCL-A5` | invalid/stale paths return typed unresolved (`None`) |
| T4 | `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`, `ROLE-DCL-A6` | valid transcript role still resolves/persists |
| T5 | Cross-Harness Disposition | unresolved suppresses AXIS-2 surface in both copies |
| T6 | Cross-Harness Disposition | LO file-safety gate still refuses; `durable_*` preserved |
| T7 | v7 details-surface clause | details expose no `durable_registry_role` key |
| T8 | Option A scope | table assertion-4 cases assert fail-closed semantics |
| T9 | Option A2 scope | `test_dcl_role_resolution_authority_001.py` R1/R2 updated: absent/invalid/stale evidence yields `role is None`; `_durable_role`-derived baseline replaced by `None` expectation |

Commands to be executed and reported:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_role_resolution.py platform_tests/hooks/test_session_role_resolution.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_session_role_resolution_table.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_axis_2_role_aware.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_envelope_runtime.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/session_role_resolution.py .claude/hooks/bridge-axis-2-surface.py config/hooks/gtkb-bridge-axis-2-surface.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/session_role_resolution.py .claude/hooks/bridge-axis-2-surface.py config/hooks/gtkb-bridge-axis-2-surface.py
```

## Acceptance Criteria (unchanged; criterion 9 added)

1. The interactive resolver never returns the durable registry role.
2. No production path emits `session_resolver_fallback` (proved, not assumed).
3. `resolve_interactive_session_role_details` exposes no durable role key.
4. A validly established transcript role still resolves and persists.
5. AXIS-2 suppresses rather than defaulting to Prime Builder on unresolved.
6. The LO file-safety gate shows no behavioural regression; `durable_*` source strings preserved.
7. All listed suites pass; both ruff gates pass on the changed files.
8. `test_session_role_resolution_table.py` assertion-4 cases assert fail-closed semantics and pass.
9. `test_dcl_role_resolution_authority_001.py` R1/R2 assert the new fail-closed
   semantics and pass (scope-expanded cohort); its two pre-existing
   spec-content tests (R-spec checks) remain disclosed and unchanged.

## Risk and Rollback

Unchanged from `-005`. Principal risk remains session-start fragility, mitigated by
C5 + T4. The `durable_*` source strings are preserved. Rollback is reverting the
seven target files; no data migration, no schema change.

## Owner Decisions / Input

- **AUQ 2026-08-06 (Slice B disposition):** owner selected "Proceed under the GO".
- **AUQ 2026-08-06 (Slice B footing):** owner selected "File REVISED, then implement".
- **AUQ 2026-08-06 (Option A):** owner authorized adding
  `test_session_role_resolution_table.py` to the cohort.
- **AUQ 2026-08-06 (Option A2):** owner authorized adding
  `test_dcl_role_resolution_authority_001.py` to the cohort so its R1/R2 tests
  can be updated to the fail-closed semantics.
- **Owner "Adopt" disposition (2026-08-06):** owner directed treating the in-progress
  working-tree C1/C2/C4 edits as the implementation baseline.
- **`DELIB-202668164`** - owner authorization for the consolidated session-role purge lane.
- **`AUQ-20260729-PROGRAM-WAVE1-GATES` CF-01** - owner requires fail-closed unresolved identity.
- **`DELIB-202667721`** - owner decision behind the whole-project authorization.

## Recommended Commit Type

`fix:` - brings existing source into conformance with an approved design constraint
and removes an incorrect-role defect.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
