NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 5ce32d92-003b-4a04-a5f9-d3de2493c992
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal
Document: gtkb-wi5933-slice-b-resolver-fail-closed
Version: 001
Date: 2026-08-06 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5933

target_paths: ["scripts/session_role_resolution.py", ".claude/hooks/bridge-axis-2-surface.py", "config/hooks/gtkb-bridge-axis-2-surface.py", "platform_tests/scripts/test_session_role_resolution.py", "platform_tests/hooks/test_session_role_resolution.py"]

**No KB mutation.** This slice performs no MemBase/KB write and does not modify
`groundtruth.db`. It changes source, harness-hook, and test files only. The
DCL and deliberation records cited throughout are read as existing governing
authority; none is created, amended, or versioned by this work.

# WI-5933 Slice B - make interactive session-role resolution fail closed (DCL v7 conformance)

## Root Boundary Compliance

All artifacts are in-root under `E:/GT-KB`. Every declared target is an in-root
path, and this bridge file resides under `E:/GT-KB/bridge/`. No generated
artifact is written outside the project root. No application-placement boundary
is crossed: this slice touches only platform surfaces under `E:/GT-KB/scripts/`,
`E:/GT-KB/.claude/hooks/`, `E:/GT-KB/config/hooks/`, and
`E:/GT-KB/platform_tests/`, and no file under `applications/`.

## Problem Statement

`DCL-SESSION-ROLE-RESOLUTION-001` **v7** (status `specified`) is unambiguous:

> When explicit session-role identity cannot be resolved from the current
> session's validated transcript or session envelope, resolution fails closed
> with a typed recovery result. It MUST NOT substitute the durable registry role
> and MUST NOT emit `session_resolver_fallback`.

and:

> The session resolver may not consult or substitute the durable registry role
> and may not label any result `session_resolver_fallback`.

`scripts/session_role_resolution.py` does all three forbidden things today:

| Line | Code | DCL v7 violation |
| --- | --- | --- |
| 164 | `durable = _durable_role(project_root, harness_name)` | resolver consults the durable registry role |
| 180 | `fallback = envelope_role if envelope_role is not None else durable` | resolver **substitutes** the durable registry role |
| 244 | `"durable_registry_role": durable` | resolver surfaces the durable role to worker consumers |
| envelope open path | emits `session_resolver_fallback` | forbidden label |

Line 180's `fallback` value is returned on **four** paths
(`fallback_absent_source`, `fallback_invalid_source`, `fallback_stale_source`,
and the no-marker path), so any interactive session lacking valid explicit role
evidence silently receives the durable registry role instead of a typed
unresolved result.

### First-hand reproduction (this session, 2026-08-05)

This session opened with the canonical init keyword `::init gtkb pb`. Its
envelope nevertheless recorded:

```
role: loyal-opposition
role_resolved: loyal-opposition
init_keyword: null
worker_role_provenance.role_resolution_source: session_resolver_fallback
worker_role_provenance.session_id: 8208f14b-...   (a different session)
```

The durable registry role for harness B is `loyal-opposition`, so the resolver
substituted it and labelled the result with the exact string v7 forbids. The
consequence was concrete: governed bridge filing refused the session until the
envelope was re-opened with correct provenance. A Prime Builder session was
silently presented as Loyal Opposition - the precise mislabelling class that
review independence depends on not happening.

## Consumer Analysis

Thirty files reference the resolver, its details function,
`_DURABLE_FALLBACK_SOURCES`, or `durable_registry_role`. The production
(non-test) consumers and their current handling:

| Consumer | Current handling | Impact of fail-closed |
| --- | --- | --- |
| `.claude/hooks/lo-file-safety-gate.py` and `config/hooks/gtkb-lo-file-safety-gate.py` | `if str(_outcome).startswith("durable_"): return False` | **already fail-closed**; discriminates on the source prefix and refuses durable-derived authority. Behaviour preserved. |
| `.claude/hooks/bridge-axis-2-surface.py` and `config/hooks/gtkb-bridge-axis-2-surface.py` | `return role_profile if role_profile in (ROLE_PRIME, ROLE_LO) else ROLE_PRIME` | **must change**: silently coerces any non-role value to Prime Builder, so an unresolved result would become Prime Builder authority. |
| `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` | wrapped in `try/except` returning `{}` | already fail-soft; a typed unresolved result degrades to no role evidence. |
| `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | reports role state | reporting surface; renders "unresolved" rather than a substituted role. Treated as a follow-on reporting slice, not a behaviour gate. |
| `groundtruth-kb/src/groundtruth_kb/session/envelope.py` | emits provenance including the forbidden label | the `session_resolver_fallback` emission is removed by this slice's resolver contract change. |

The key structural finding: the `durable_*` source-prefix convention **already
exists and is already treated as non-authoritative** by the safety gate. The
defect is that the resolver returns the durable role as the *role value* while
merely flagging the source, so any consumer that reads the role and ignores the
source silently inherits durable authority. Slice B removes the substitution so
the role value itself carries no durable authority.

Test consumers requiring update include
`platform_tests/scripts/test_session_role_resolution.py` and
`platform_tests/hooks/test_session_role_resolution.py`. Reviewed but not
modified: `platform_tests/scripts/test_dcl_role_resolution_authority_001.py`
(the DCL conformance module, which encodes v7 assertions and should *gain*
coverage from this change rather than need relaxation).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority for this thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - discharged by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the Test Plan maps each v7 clause to a test.
- `DCL-SESSION-ROLE-RESOLUTION-001` **v7** - the controlling constraint; clauses quoted above, plus assertions `ROLE-DCL-A5` (unresolved evidence fails before protected work with recovery) and `ROLE-DCL-A6` (explicit interactive owner direction resolves and persists).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - platform/application placement boundary; this slice touches only platform surfaces in-root and no `applications/` path, as declared under Root Boundary Compliance.
- `GOV-SESSION-ROLE-AUTHORITY-001` - durable vs session-stated authority split.
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001` and `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001` - transcript-defined role persistence, which this change must preserve.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and `ADR-CROSS-HARNESS-PARITY-001` - harness-surface parity; discharged by the Cross-Harness Disposition section below.
- `.claude/rules/operating-role.md` and `.claude/rules/prime-builder-role.md` - narrative role-authority surfaces.
- `.claude/rules/file-bridge-protocol.md` section Review Independence Boundary - why a mislabelled interactive role is a review-integrity defect, not a cosmetic one.
- `.claude/rules/project-root-boundary.md` - in-root containment for all targets.
- `DELIB-202667721` - owner decision behind the whole-project authorization.

## Prior Deliberations

- `DELIB-202668164` - owner authorization for the consolidated, serialized
  session-role purge lane; establishes the Slice A / Slice B split that this
  proposal completes.
- `AUQ-20260729-PROGRAM-WAVE1-GATES` CF-01 - the owner decision behind DCL v7:
  unresolved identity must fail closed, durable-registry fallback is forbidden,
  and the `session_resolver_fallback` label is removed.
- `DELIB-202667742` - emergency repair authorization for interactive role
  persistence across session boundaries.
- `DELIB-202668165` - retroactive approval of the Slice A emergency-bootstrap
  repair; Slice A is landed (`b638b42da`) and independently verified.
- WI-5679 (`gtkb-wi5679-session-role-keying-continuity-*`, 16 versions) -
  **adjacent, not duplicate**: it concerns stale ambient session-id keying after
  restart, in a different project. This slice does not alter session-id keying.

## Requirement Sufficiency

Existing requirements sufficient. DCL v7 is approved (`status: specified`) and
already mandates the target behaviour; this slice is source conformance to an
existing constraint, not a new requirement. No DCL amendment is required, and
none is proposed.

## Proposed Change

### C1 - Remove durable substitution from the resolver

Delete the `else durable` substitution at line 180 and the `_durable_role` read
at line 164 from the interactive resolution path. When explicit evidence is
absent, invalid, or stale, return a **typed unresolved result** rather than a
role value, preserving the existing source discrimination
(`*_absent`, `*_invalid_role`, `*_stale_session`) so consumers that already key
on it keep working.

### C2 - Remove durable exposure from the details function

Remove `durable_registry_role` (line 244) and the accompanying
`durable_registry_authority` narrative from
`resolve_interactive_session_role_details`, and recompute `authority_mode`
without a durable-fallback branch.

### C3 - Remove the forbidden `session_resolver_fallback` label

Eliminate the label from the envelope-open / session-start provenance path so no
worker document can record it, per the explicit v7 prohibition.

### C4 - Update the coercing consumer

Change both copies of the AXIS-2 surface so an unresolved result suppresses the
surface rather than defaulting to `ROLE_PRIME`. The `lo-file-safety-gate` copies
need no behavioural change (already fail-closed) but are re-verified.

### C5 - Preserve interactive persistence

The transcript-defined role must continue to persist across compaction, resume,
and contiguous SessionStart boundaries per
`DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`. Fail-closed applies only when
there is **no** valid explicit evidence; it must not weaken persistence of a
validly established transcript role.

## Cross-Harness Disposition

This slice touches a harness-surface file (`.claude/hooks/bridge-axis-2-surface.py`)
and its tracked mirror, so parity is declared per harness. The behavioural change
itself lives in the shared `scripts/session_role_resolution.py`, which every
harness consumes, so resolver semantics are identical across all harnesses by
construction.

| Harness | Surface | Disposition |
| --- | --- | --- |
| B claude | `.claude/hooks/bridge-axis-2-surface.py` | **Updated (C4).** Unresolved role suppresses the AXIS-2 surface instead of coercing to `ROLE_PRIME`. |
| (tracked mirror) | `config/hooks/gtkb-bridge-axis-2-surface.py` | **Updated in lockstep** with the Claude copy; parity of the changed logic asserted by T5. |
| A codex | `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` | **Behavioural parity, no edit required.** Already wraps `resolve_interactive_session_role_details` in `try/except` returning `{}`, so a typed unresolved result degrades to "no role evidence" - the intended fail-closed outcome. Re-verified, not modified. |
| shared | `.claude/hooks/lo-file-safety-gate.py` / `config/hooks/gtkb-lo-file-safety-gate.py` | **Behavioural parity, no edit required.** Both already refuse authority when the source starts with `durable_`. Regression-covered by T6. |
| C antigravity, D ollama, E cursor, F openrouter, G goose, H alibaba-cloud-studio | no harness-local AXIS-2 or role-resolution hook surface | **Parity via the shared resolver.** These harnesses consume role resolution only through `scripts/session_role_resolution.py`; C1-C3 applies to them identically with no harness-local edit. |

No owner-approved typed waiver is requested: every applicable harness reaches
behavioural parity either by edit or by existing fail-closed/fail-soft handling.

## Test Plan (specification-derived)

| Test | Derived from | Asserts |
| --- | --- | --- |
| T1 | DCL v7 "MUST NOT substitute the durable registry role" | with no explicit evidence and a durable role present, the resolver returns unresolved - never the durable role |
| T2 | DCL v7 forbidden-label clause | no code path emits `session_resolver_fallback`; asserted by source scan plus resolver output |
| T3 | `ROLE-DCL-A5` | invalid-role and stale-session marker paths return typed unresolved with a recovery-bearing source, not a substituted role |
| T4 | `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`, `ROLE-DCL-A6` | a validly established transcript role still resolves and persists (no regression from C1) |
| T5 | Cross-Harness Disposition (AXIS-2) | an unresolved result suppresses the AXIS-2 surface instead of defaulting to Prime Builder, in both copies |
| T6 | Cross-Harness Disposition (LO file-safety gate) | the gate still refuses authority when the source is non-explicit, with no behavioural regression |
| T7 | DCL v7 details-surface clause | `resolve_interactive_session_role_details` exposes no `durable_registry_role` key |

Commands to be executed and reported:

```
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_role_resolution.py platform_tests/hooks/test_session_role_resolution.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_dcl_role_resolution_authority_001.py platform_tests/scripts/test_session_role_resolution_table.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_axis_2_role_aware.py platform_tests/scripts/test_lo_file_safety_gate_role_resolution.py -q
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_session_self_initialization.py platform_tests/scripts/test_session_envelope_runtime.py -q
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/session_role_resolution.py .claude/hooks/bridge-axis-2-surface.py config/hooks/gtkb-bridge-axis-2-surface.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/session_role_resolution.py .claude/hooks/bridge-axis-2-surface.py config/hooks/gtkb-bridge-axis-2-surface.py
```

## Acceptance Criteria

1. The interactive resolver never returns the durable registry role.
2. No path emits `session_resolver_fallback`.
3. `resolve_interactive_session_role_details` exposes no durable role key.
4. A validly established transcript role still resolves and persists (T4).
5. AXIS-2 suppresses rather than defaulting to Prime Builder on unresolved (T5).
6. The LO file-safety gate shows no behavioural regression (T6).
7. All listed suites pass; both ruff gates pass on the changed files.

## Risk and Rollback

- **Risk: this subsystem is fragile and load-bearing at session start.** The
  highest-consequence failure mode is a session that cannot establish any role
  and therefore cannot work. Mitigated by C5 + T4 (persistence preserved) and by
  the fact that fail-closed applies only where evidence is genuinely absent -
  the same condition that today produces a *wrong* role.
- **Risk: hidden consumers beyond the 30 enumerated files.** Mitigated by running
  the session-start, envelope-runtime, doctor-marker, and hook suites listed
  above, not only the resolver's own tests.
- **Risk: some consumer depends on always receiving a role.** That dependency is
  precisely the DCL v7 violation; where found it is corrected (C4) rather than
  preserved.
- **Rollback:** revert the five target files. No data migration, no schema
  change, no committed state to unwind.

## Owner Decisions / Input

- **Owner directive 2026-08-06 (this session):** "Proceed with WI-5941 and Slice
  B" - authorizes preparing this proposal now.
- **`DELIB-202668164`** - owner authorization for the consolidated session-role
  purge lane and the Slice A/B split; Slice B is the remaining half.
- **`AUQ-20260729-PROGRAM-WAVE1-GATES` CF-01** - the owner decision requiring
  unresolved identity to fail closed and forbidding both durable-registry
  fallback and the `session_resolver_fallback` label. DCL v7 records it at the
  requirement layer; this slice implements it in source.
- **`DELIB-202667721`** - owner decision behind the whole-project authorization
  covering WI-5933 as an active member work item.

## Recommended Commit Type

`fix:` - brings existing source into conformance with an already-approved design
constraint and removes an incorrect-role defect. No new capability surface.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
