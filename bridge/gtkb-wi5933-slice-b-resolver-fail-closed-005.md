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
Version: 005 (REVISED; owner-authorized scope expansion under Option A)
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi5933-slice-b-resolver-fail-closed-004.md
Prior GO: bridge/gtkb-wi5933-slice-b-resolver-fail-closed-004.md
Prior design GO: bridge/gtkb-wi5933-slice-b-resolver-fail-closed-002.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5933

target_paths: ["scripts/session_role_resolution.py", ".claude/hooks/bridge-axis-2-surface.py", "config/hooks/gtkb-bridge-axis-2-surface.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/hooks/test_session_role_resolution.py", "platform_tests/scripts/test_session_role_resolution_table.py"]

**No KB mutation.** This slice performs no MemBase/KB write and does not modify
`groundtruth.db`. It changes source, harness-hook, and test files only.

**No approval-evidence work.** This slice creates no formal-artifact-approval packet and modifies no approval-packet path.

# WI-5933 Slice B REVISED (005) - owner-authorized scope expansion for fail-closed verification

## Why This Revision Exists

This revision is filed by the acting Prime Builder (harness G, goose) under an
explicit owner decision (Option A) to expand the WI-5933 Slice B target cohort
to include `platform_tests/scripts/test_session_role_resolution_table.py`.

The `-004` GO and the `-003` design are accepted unchanged in substance. C1/C2/C4/C5
and the C3 proof obligation are exactly as approved at `-002`/`-003`/`-004`. This
revision makes one scope change and records the adoption of in-progress source edits.

## Scope Change (Option A)

`platform_tests/scripts/test_session_role_resolution_table.py` is added to
`target_paths`. Rationale:

- The `-003`/`-001` mandatory command lists already run this module (e.g.
  `-003` line 219: `pytest ... test_session_role_resolution_table.py ...`), but it
  was omitted from `declared_target_paths`.
- That module's assertion-4 tests (`test_assertion4_no_marker_returns_durable`,
  `test_assertion4_compaction_resume_falls_back_to_durable`) assert the OLD
  durable-substitution behavior (role == durable on absent/stale evidence).
- C1/T1 require the resolver to fail closed (role == `None`) on absent/invalid/stale
  evidence and never return the durable role. Implementing C1 faithfully therefore
  requires updating those assertion-4 expectations.
- Editing a file outside `declared_target_paths` would be a PAUTH scope violation.
  The owner selected **Option A** to expand the cohort so those tests can be updated
  to the new fail-closed semantics as part of this slice.

This is the only scope change. The original five targets are unchanged.

## Adoption of In-Progress Source Edits

At implementation preparation, `scripts/session_role_resolution.py` and
`.claude/hooks/bridge-axis-2-surface.py` already carried unclaimed working-tree
edits implementing C1/C2/C4 (resolver returns `None` instead of durable role;
`durable_registry_role` removed from details; AXIS-2 suppress-on-unresolved). These
edits were reviewed, verified coherent (py_compile + ruff clean), and are adopted as
the implementation baseline for this slice. This revision additionally:
- updates the module docstring resolution table to the fail-closed semantics;
- removes the now-unused `_DURABLE_FALLBACK_SOURCES` constant (C2 cleanup);
- applies the same C4 change to the `config/hooks/gtkb-bridge-axis-2-surface.py`
  mirror so both AXIS-2 copies suppress on unresolved (parity).

## Authority Verification (unchanged from `-003`)

- `GOV-SESSION-ROLE-AUTHORITY-001` is deliberately absent: verified retired (v6);
  not relied upon anywhere in this proposal.
- `DCL-SESSION-ROLE-RESOLUTION-001` v7 (`status: specified`, approved 2026-07-29)
  is the controlling constraint, plus assertions `ROLE-DCL-A5` and `ROLE-DCL-A6`.
- The WI-5679 packet-completeness question is not adjudicated here and is left to
  WI-5679; this proposal does not depend on it.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority for this thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - discharged by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Test Plan maps each v7 clause to a test.
- `DCL-SESSION-ROLE-RESOLUTION-001` **v7** (`status: specified`; approved 2026-07-29) - the controlling constraint, plus assertions `ROLE-DCL-A5` and `ROLE-DCL-A6`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - platform/application placement boundary; only platform surfaces are touched.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` and `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - transcript-defined role persistence, preserved by C5.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and `ADR-CROSS-HARNESS-PARITY-001` - discharged by the Cross-Harness Disposition (both AXIS-2 copies updated in lockstep).
- `.claude/rules/file-bridge-protocol.md` section Review Independence Boundary - why a mislabelled interactive role is a review-integrity defect.
- `.claude/rules/project-root-boundary.md` - in-root containment.
- `DELIB-202667721` - owner decision behind the whole-project authorization.

`GOV-SESSION-ROLE-AUTHORITY-001` is **deliberately absent**: verified retired (v6).

## Problem Statement (unchanged from `-001`/`-003`)

`DCL-SESSION-ROLE-RESOLUTION-001` v7 states:

> When explicit session-role identity cannot be resolved from the current
> session's validated transcript or session envelope, resolution fails closed
> with a typed recovery result. It MUST NOT substitute the durable registry role
> and MUST NOT emit `session_resolver_fallback`.

`scripts/session_role_resolution.py` previously violated this by substituting the
durable registry role at the interactive-fallback return paths and exposing
`durable_registry_role` in details. The adopted edits correct both.

## Requirement Sufficiency

**Existing requirements sufficient.** `DCL-SESSION-ROLE-RESOLUTION-001` v7 is
recorded in MemBase as `specified` and was approved on 2026-07-29, and the
defect it describes is observable in live source and was independently confirmed
by the `-002`/`-004` GOs. This slice is source conformance to an existing
constraint plus an owner-authorized test-cohort expansion. No new requirement is
implied and no DCL amendment is proposed.

## Proposed Change (unchanged from `-003`; scope expanded)

- **C1** - remove the `_durable_role` substitution from the interactive path; return
  a typed unresolved result (`role_profile = None`) when explicit evidence is absent,
  invalid, or stale, preserving the existing `durable_*` source strings so the LO
  file-safety gate keeps refusing.
- **C2** - remove `durable_registry_role` and `durable_registry_authority` from
  `resolve_interactive_session_role_details`; recompute `authority_mode` without a
  durable-fallback branch (`interactive_transcript` when resolved, `unresolved`
  otherwise).
- **C3** - verification only: prove in the implementation report that no production
  emitter of `session_resolver_fallback` remains (envelope-path removal belongs to
  WI-5723).
- **C4** - both AXIS-2 copies suppress the surface on an unresolved result instead
  of coercing to `ROLE_PRIME`.
- **C5** - preserve transcript-role persistence; fail-closed applies only where no
  valid explicit evidence exists.

## Cross-Harness Disposition

The behavioural change lives in the shared `scripts/session_role_resolution.py`,
which every harness consumes, so resolver semantics are identical across harnesses
by construction.

| Harness | Surface | Disposition |
| --- | --- | --- |
| B claude | `.claude/hooks/bridge-axis-2-surface.py` | **Updated (C4).** Unresolved suppresses the surface. |
| (tracked mirror) | `config/hooks/gtkb-bridge-axis-2-surface.py` | **Updated in lockstep**; parity asserted by T5. |
| A codex | `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` | **Parity, no edit.** Already `try/except` -> `{}`; reads details via `.get()`, so removed keys degrade to `None`. |
| shared | `lo-file-safety-gate.py` / `gtkb-lo-file-safety-gate.py` | **Parity, no edit.** Already refuse on `durable_` prefix, which C1 preserves. Covered by T6. |
| C antigravity, D ollama, E cursor, F openrouter, G goose, H alibaba-cloud-studio | no harness-local role-resolution surface | **Parity via the shared resolver.** |

No owner-approved typed waiver is requested.

## Test Plan (specification-derived)

| Test | Derived from | Asserts |
| --- | --- | --- |
| T1 | v7 no-substitution clause | with no explicit evidence and a durable role present, the resolver returns `None` - never the durable role |
| T2 | v7 forbidden-label clause | no production path emits `session_resolver_fallback` (C3 proof) |
| T3 | `ROLE-DCL-A5` | invalid-role and stale-session paths return typed unresolved (`None`) with a recovery-bearing source |
| T4 | `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`, `ROLE-DCL-A6` | a validly established transcript role still resolves and persists |
| T5 | Cross-Harness Disposition | unresolved suppresses the AXIS-2 surface in both copies instead of defaulting to Prime Builder |
| T6 | Cross-Harness Disposition | the LO file-safety gate still refuses on non-explicit sources; `durable_*` strings preserved |
| T7 | v7 details-surface clause | `resolve_interactive_session_role_details` exposes no `durable_registry_role` key |
| T8 | scope expansion (Option A) | `test_session_role_resolution_table.py` assertion-4 cases updated: no-marker and stale-marker now assert `role is None` with the `durable_marker_absent` / `durable_marker_stale_session` source |

Commands to be executed and reported:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_role_resolution.py platform_tests/hooks/test_session_role_resolution.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_session_role_resolution_table.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_axis_2_role_aware.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_envelope_runtime.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/session_role_resolution.py .claude/hooks/bridge-axis-2-surface.py config/hooks/gtkb-bridge-axis-2-surface.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/session_role_resolution.py .claude/hooks/bridge-axis-2-surface.py config/hooks/gtkb-bridge-axis-2-surface.py
```

## Acceptance Criteria (unchanged; criterion 8 added)

1. The interactive resolver never returns the durable registry role.
2. No production path emits `session_resolver_fallback` (proved, not assumed).
3. `resolve_interactive_session_role_details` exposes no durable role key.
4. A validly established transcript role still resolves and persists.
5. AXIS-2 suppresses rather than defaulting to Prime Builder on unresolved.
6. The LO file-safety gate shows no behavioural regression; `durable_*` source strings preserved.
7. All listed suites pass; both ruff gates pass on the changed files.
8. `test_session_role_resolution_table.py` assertion-4 cases assert the new
   fail-closed semantics and pass (scope-expanded cohort).

## Risk and Rollback

Unchanged from `-003`. Principal risk remains session-start fragility, mitigated by
C5 + T4. The `durable_*` source strings are preserved so the out-of-scope LO
file-safety gate cannot silently stop refusing. Rollback is reverting the six target
files; no data migration, no schema change.

## Owner Decisions / Input

- **AUQ 2026-08-06 (Slice B disposition):** owner selected "Proceed under the GO".
- **AUQ 2026-08-06 (Slice B footing):** owner selected "File REVISED, then implement".
- **AUQ 2026-08-06 (Option A scope expansion):** owner authorized adding
  `platform_tests/scripts/test_session_role_resolution_table.py` to the target cohort
  so its assertion-4 tests can be updated to the fail-closed semantics.
- **Owner "Adopt" disposition (2026-08-06):** owner directed treating the in-progress
  working-tree C1/C2/C4 edits as the implementation baseline and completing the
  remaining files.
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
