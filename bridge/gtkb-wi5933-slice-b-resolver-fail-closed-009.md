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
Version: 009 (REVISED; owner-authorized scope expansion under Option A3)
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi5933-slice-b-resolver-fail-closed-008.md
Prior GOs: bridge/gtkb-wi5933-slice-b-resolver-fail-closed-002.md, -004.md, -006.md, -008.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5933

target_paths: ["scripts/session_role_resolution.py", ".claude/hooks/bridge-axis-2-surface.py", "config/hooks/gtkb-bridge-axis-2-surface.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/hooks/test_session_role_resolution.py", "platform_tests/scripts/test_session_role_resolution_table.py", "platform_tests/scripts/test_dcl_role_resolution_authority_001.py", "platform_tests/hooks/test_bridge_axis_2_role_aware.py"]

**No KB mutation.** This slice performs no MemBase/KB write and does not modify
`groundtruth.db`. It changes source, harness-hook, and test files only.

**No approval-evidence work.** This slice creates no formal-artifact-approval packet and modifies no approval-packet path.

# WI-5933 Slice B REVISED (009) - owner-authorized scope expansion (Option A3)

## Why This Revision Exists

This revision is filed by the acting Prime Builder (harness G, goose) under an
explicit owner decision (Option A3) to expand the WI-5933 Slice B target cohort a
third time, adding `platform_tests/hooks/test_bridge_axis_2_role_aware.py`.

The `-008` GO and the `-003`/`-005`/`-007` design are accepted unchanged in
substance. C1/C2/C4/C5 and the C3 proof obligation are exactly as approved. This
revision makes one additional scope change and records no design drift.

## Scope Change (Option A3)

`platform_tests/hooks/test_bridge_axis_2_role_aware.py` is added to
`target_paths`. Rationale (verified live):

- The `-003`/`-005`/`-007`/`-009` mandatory command lists run this module (e.g.
  `pytest ... test_bridge_axis_2_role_aware.py test_lo_file_safety_gate_role_resolution.py`),
  but it was omitted from `declared_target_paths` even after the Option A/A2
  expansions.
- Its `test_resolve_failsoft_defaults_prime_on_resolver_error` asserts the OLD C4
  behavior: on resolver error the AXIS-2 hook returns `ROLE_PRIME`.
- The approved C4 change makes the hook return `None` (suppress the surface) on an
  unresolved/errored role. Implementing C4 therefore breaks that assertion unless
  it is updated.
- Editing a file outside `declared_target_paths` would be a PAUTH scope violation.
  The owner selected **Option A3** to expand the cohort so that one assertion can
  be updated to the new fail-closed semantics.

This is the only additional scope change. The prior seven targets are unchanged.
(Note: the sibling `test_lo_file_safety_gate_role_resolution.py` already passes and
remains out of cohort, consistent with the prior approvals.)

## Adoption of Re-Applied Source Edits (unchanged)

`scripts/session_role_resolution.py`, `.claude/hooks/bridge-axis-2-surface.py`, and
`config/hooks/gtkb-bridge-axis-2-surface.py` carry the re-applied C1/C2/C4
implementation baseline (verified py_compile + ruff clean). The four test files
already in cohort (two `test_session_role_resolution.py`, the table test, and
`test_dcl_role_resolution_authority_001.py` R1/R2) are updated and green. This
revision adds the AXIS-2 role-aware hook test to the cohort.

## Authority Verification (unchanged from `-005`/`-007`)

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

## Problem Statement (unchanged from `-001`/`-003`/`-005`/`-007`)

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

## Proposed Change (unchanged from `-005`/`-007`; scope expanded a third time)

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

## Test Plan (specification-derived; T10 added)

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
| T9 | Option A2 scope | `test_dcl_role_resolution_authority_001.py` R1/R2 fail-closed semantics |
| T10 | Option A3 scope | `test_bridge_axis_2_role_aware.py::test_resolve_failsoft_defaults_prime_on_resolver_error` updated: resolver error -> hook returns `None` (suppress), not `ROLE_PRIME` |

Commands to be executed and reported:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_role_resolution.py platform_tests/hooks/test_session_role_resolution.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_session_role_resolution_table.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_axis_2_role_aware.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_envelope_runtime.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/session_role_resolution.py .claude/hooks/bridge-axis-2-surface.py config/hooks/gtkb-bridge-axis-2-surface.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/session_role_resolution.py .claude/hooks/bridge-axis-2-surface.py config/hooks/gtkb-bridge-axis-2-surface.py
```

## Acceptance Criteria (unchanged; criterion 10 added)

1. The interactive resolver never returns the durable registry role.
2. No production path emits `session_resolver_fallback` (proved, not assumed).
3. `resolve_interactive_session_role_details` exposes no durable role key.
4. A validly established transcript role still resolves and persists.
5. AXIS-2 suppresses rather than defaulting to Prime Builder on unresolved.
6. The LO file-safety gate shows no behavioural regression; `durable_*` source strings preserved.
7. All listed suites pass; both ruff gates pass on the changed files.
8. `test_session_role_resolution_table.py` assertion-4 cases assert fail-closed semantics and pass.
9. `test_dcl_role_resolution_authority_001.py` R1/R2 assert the new fail-closed
   semantics and pass; its two pre-existing spec-content tests (R-spec checks)
   remain disclosed and unchanged.
10. `test_bridge_axis_2_role_aware.py::test_resolve_failsoft_defaults_prime_on_resolver_error`
    asserts the fail-closed (`None`) semantics and passes (scope-expanded cohort).

## Risk and Rollback

Unchanged from `-005`/`-007`. Principal risk remains session-start fragility,
mitigated by C5 + T4. The `durable_*` source strings are preserved. Rollback is
reverting the eight target files; no data migration, no schema change.

## Owner Decisions / Input

- **AUQ 2026-08-06 (Slice B disposition):** owner selected "Proceed under the GO".
- **AUQ 2026-08-06 (Slice B footing):** owner selected "File REVISED, then implement".
- **AUQ 2026-08-06 (Option A):** owner authorized adding `test_session_role_resolution_table.py`.
- **AUQ 2026-08-06 (Option A2):** owner authorized adding `test_dcl_role_resolution_authority_001.py`.
- **AUQ 2026-08-06 (Option A3):** owner authorized adding
  `test_bridge_axis_2_role_aware.py` so its `test_resolve_failsoft_defaults_prime_on_resolver_error`
  can be updated to the fail-closed semantics.
- **Owner "Adopt" / "Re-apply and guard" dispositions (2026-08-06):** owner directed
  treating the in-progress working-tree C1/C2/C4 edits as the implementation
  baseline and re-applying them after a concurrent reset.
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
