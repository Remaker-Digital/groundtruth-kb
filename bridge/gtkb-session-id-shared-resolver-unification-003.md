REVISED

# Unify session-id resolution into one module: shared SET + per-surface order (REVISED-1)

bridge_kind: prime_proposal

author_identity: Prime Builder
author_harness_id: B
author_session_context_id: 544048b6-8b36-4469-8727-e77bf6a32333
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: explanatory output style; Claude Code

revision_reason: REVISED-1 over -001 to close Codex NO-GO -002 F1 and adopt the
owner's design decision (2026-06-03 AUQ: "Shared SET, per-surface order"). -002
correctly found that the marker writer (`scripts/workstream_focus.py`) and the
doctor marker resolver deliberately resolve `GTKB_SESSION_ID` FIRST (session-role
continuity), which is a DIFFERENT precedence policy from the bridge surfaces
(live-harness-first). -001 wrongly imposed one global order on the marker writer
and omitted the doctor + marker parity tests from scope. This revision: (1) keeps
both precedence policies, (2) makes the new module the single membership authority
plus the home of BOTH explicit order constants, (3) expands scope to the doctor
and the two marker parity tests, and (4) honors the doctor's packaging constraint
(it keeps a parity-tested copy rather than importing repo-root `scripts/`).

target_paths: ["scripts/gtkb_session_id.py", "scripts/bridge_claim_cli.py", "scripts/workstream_focus.py", ".claude/hooks/bridge-compliance-gate.py", ".claude/hooks/bridge-axis-2-surface.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_gtkb_session_id.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/hooks/test_bridge_compliance_gate_work_intent.py", "platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py", "platform_tests/skills/test_bridge_propose_helper_work_intent.py", "platform_tests/hooks/test_workstream_focus_session_role_marker.py", "platform_tests/scripts/test_doctor_session_role_marker.py"]

Project Authorization: PAUTH-WI-4270-SESSION-ID-SHARED-RESOLVER
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4270

## Summary

The session-id env-var list is hand-maintained in two families that each
disagreed internally, and the original Claude Code defect was a MEMBERSHIP
omission (`CLAUDE_CODE_SESSION_ID`) in the bridge family — not an ordering
problem. The minimal fix (committed `ea2040a5`, VERIFIED at
`bridge/gtkb-claude-code-session-id-env-var-gap-012.md`) appended the missing
var per-tuple but left the duplication. This proposal centralizes membership in
one module while preserving each family's deliberate precedence.

### Two intentional precedence policies (the key correction from -002)

- **Bridge work-intent family** (`WORK_INTENT_SESSION_ENV_VARS` /
  `SESSION_ENV_VARS`): live-harness-first — explicit payload/arg, then
  `CLAUDE_SESSION_ID`, `CLAUDE_CODE_SESSION_ID`, `GTKB_INHERITED_SESSION_ID`,
  `CODEX_SESSION_ID`, `CODEX_THREAD_ID`, `ANTIGRAVITY_SESSION_ID`,
  `GTKB_SESSION_ID` (7 members). Surfaces: `scripts/bridge_claim_cli.py`,
  `.claude/hooks/bridge-compliance-gate.py`, `.claude/hooks/bridge-axis-2-surface.py`,
  `.claude/skills/bridge-propose/helpers/write_bridge.py`, and the two template
  mirrors.
- **Marker-continuity family** (`_SESSION_ID_ENV_FALLBACKS`): `GTKB_SESSION_ID`
  FIRST so an inherited/dispatched GT-KB session id wins over ambient harness
  env (`GTKB_SESSION_ID`, `CODEX_SESSION_ID`, `CODEX_THREAD_ID`,
  `CLAUDE_SESSION_ID`, `CLAUDE_CODE_SESSION_ID` — 5 members). Surfaces:
  `scripts/workstream_focus.py` (marker writer) and
  `groundtruth-kb/src/groundtruth_kb/project/doctor.py` (doctor marker
  resolver). Existing tests assert this `GTKB_SESSION_ID`-first precedence.

Both families already include `CLAUDE_CODE_SESSION_ID` post-`ea2040a5`. The
remaining defect is the duplication (membership can silently drift again, which
is exactly how the original omission happened). This proposal eliminates that
drift while keeping behavior identical.

## Owner Decisions / Input

Owner AskUserQuestion decisions, 2026-06-03 (the only valid owner-decision
channel per `.claude/rules/prime-builder-role.md`):

1. **DECISION-0899** — design = shared resolution helper.
2. **DECISION-0900** — project home = `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`.
3. **DECISION-0901** — minimal fix first (done), shared helper as follow-on.
4. **2026-06-03 "File the WI-4270 follow-on now."**
5. **2026-06-03 "Authorize + file now"**, captured as `DELIB-20260625`,
   authorizing WI-4270 implementation via `PAUTH-WI-4270-SESSION-ID-SHARED-RESOLVER`.
6. **2026-06-03 marker-precedence AUQ — "Shared SET, per-surface order (full
   unification)"**: the owner chose to keep the marker writer + doctor unified
   to the shared module while preserving their distinct `GTKB_SESSION_ID`-first
   precedence (over scoping the marker writer out, and over parking the thread).

## Specification Links

Blocking (required) cross-cutting specs:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (v1, verified) — a single membership
  authority hardens the work-intent contract against the recurrence class.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (v1, specified).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` (v1, specified) — concrete
  including-PAUTH/Project/WI metadata cited.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` (v1, specified) — WI-4270
  is an active project member explicitly included by the cited PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (v1, specified) — the
  verification plan maps specs to tests, including the marker + doctor tests.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (v1, specified) — all touched files
  are in-root; `applications/Agent_Red/` untouched.

Advisory cross-cutting specs:

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `GOV-STANDING-BACKLOG-001` (v1).

Predecessor + precedent:

- `bridge/gtkb-claude-code-session-id-env-var-gap-001.md` … `-012.md`
  (minimal fix VERIFIED + committed `ea2040a5`).
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` + `DCL-SESSION-ROLE-RESOLUTION-001`
  (v1, specified) — established the marker-continuity precedence and
  `CLAUDE_CODE_SESSION_ID` recognition this proposal centralizes.

Rule-cited soft authority:

- `.claude/rules/file-bridge-protocol.md` (claim step, pre-filing preflight,
  implementation-start authorization metadata).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — duplicated env lists are
  drift-prone plumbing; one membership authority + drift-lock tests is the
  deterministic-service realization.

## Prior Deliberations

- `DELIB-20260625` — owner authorization to implement WI-4270.
- `bridge/gtkb-session-id-shared-resolver-unification-002.md` — Codex NO-GO F1
  (marker precedence conflict); this REVISED-1 closes all five required
  revisions.
- `bridge/gtkb-claude-code-session-id-env-var-gap-012.md` — predecessor minimal
  fix VERIFIED.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` Slice 2/4 deliberations —
  origin of the marker-continuity precedence + the doctor parity-not-import
  packaging decision (Codex Review Ask 2).

## Requirement Sufficiency

Existing requirements sufficient. Behavior-preserving refactor; no new
requirement, policy, or external contract. No new spec required.

## Implementation-Start Authorization Evidence

- `Project Authorization: PAUTH-WI-4270-SESSION-ID-SHARED-RESOLVER` is active,
  unexpired, on the active project, explicitly includes WI-4270, and authorizes
  `hook_upgrade, source, cli_extension, test_addition` (covers the new module +
  the doctor `source` edit + the test additions; forbids deploy/push-force/
  spec-deletion — none used). Owner decision: `DELIB-20260625`.
- `Work Item: WI-4270` is an active project member, satisfying both the
  Write-time membership/inclusion gate and the impl-start gate.

After GO: `python scripts/implementation_authorization.py begin --bridge-id gtkb-session-id-shared-resolver-unification`.

## Bridge INDEX Update Evidence

This REVISED-1 inserts `REVISED: bridge/gtkb-session-id-shared-resolver-unification-003.md`
at the top of this document's version list in `bridge/INDEX.md`, preserving the
prior `NO-GO: ...-002.md` and `NEW: ...-001.md` rows. Append-only; no prior
version deleted or rewritten; `bridge/INDEX.md` remains canonical. Satisfies
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Implementation Plan

1. **New module `scripts/gtkb_session_id.py`** (stdlib-only, hook-safe), the
   single membership authority + home of both order constants:
   - `SESSION_ID_ENV_VARS`: canonical SET (membership authority) = the 7-member
     union of all known session-id env vars.
   - `BRIDGE_WORK_INTENT_ORDER`: the 7 in live-harness-first order (exactly the
     current post-`ea2040a5` bridge order). A permutation of the SET.
   - `MARKER_CONTINUITY_ORDER`: the 5 marker members in `GTKB_SESSION_ID`-first
     order (exactly the current marker order). A documented SUBSET of the SET
     (intentionally excludes `GTKB_INHERITED_SESSION_ID`, `ANTIGRAVITY_SESSION_ID`
     to preserve current marker behavior).
   - `resolve_session_id(explicit=None, *, order=BRIDGE_WORK_INTENT_ORDER, environ=None)`:
     returns `explicit` when truthy, else first non-empty env var in `order`,
     else `""`.

2. **Bridge family** — `scripts/bridge_claim_cli.py` (direct import, arg-first
   via `resolve_session_id(arg, order=BRIDGE_WORK_INTENT_ORDER)`);
   `.claude/hooks/bridge-compliance-gate.py` + `.claude/hooks/bridge-axis-2-surface.py`
   + `.claude/skills/bridge-propose/helpers/write_bridge.py` use the fail-soft
   try/except + verbatim-local-fallback import pattern the gate already uses for
   `REQUIRED_AUTHOR_METADATA_FIELDS` (a hook never throws). Payload-first
   precedence in the gate is unchanged. Template mirrors updated byte-for-byte.

3. **Marker family** — `scripts/workstream_focus.py` `_SESSION_ID_ENV_FALLBACKS`
   delegates to `gtkb_session_id.MARKER_CONTINUITY_ORDER` (direct import; same 5
   members, `GTKB_SESSION_ID`-first — behavior identical).

4. **Doctor packaging constraint** — `groundtruth-kb/src/groundtruth_kb/project/doctor.py`
   MUST NOT import repo-root `scripts/` (per the existing comment / Codex Review
   Ask 2). It keeps its own `_SESSION_ID_ENV_FALLBACKS` copy; the existing
   parity test is extended to assert that copy equals
   `gtkb_session_id.MARKER_CONTINUITY_ORDER`, so the packaged doctor stays
   import-clean while being drift-locked to the shared authority.

## Out-of-Scope Observations (For Codex Adjudication)

- The doctor comment at `doctor.py:2815-2816` references
  `scripts.session_role_resolution._SESSION_ID_ENV_FALLBACKS`, but
  `scripts/session_role_resolution.py` defines no such constant (it takes
  `current_session_id` as a parameter). The comment is stale; correcting it is a
  docs nit left out of this behavior-focused scope (can fold into the doctor
  edit or a follow-on).
- The peripheral attribution/log tuples in `scripts/bridge_author_metadata.py`,
  `scripts/gtkb_bridge_writer.py`, `scripts/wrap_scan_cross_artifact_drift.py`
  remain out of scope (non-resolution attribution fields); a follow-on can
  migrate them to `SESSION_ID_ENV_VARS`.

## Spec-Derived Verification Plan

| Spec | Tests / Evidence |
|------|------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Integration test: a claim recorded under `CLAUDE_CODE_SESSION_ID` passes the gate holder check without `--session-id` (already dogfooded live). |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight `preflight_passed: true`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` + `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` | `implementation_authorization.py begin` -> `authorized: true`; Write-time membership/inclusion gate passed at filing. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping + tests T1-T7 + executed-command evidence in the post-impl report. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `rg --hidden SESSION_ID_ENV_VARS -l` lists only in-root files. |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` + `DCL-SESSION-ROLE-RESOLUTION-001` | Existing marker + doctor precedence tests (T6/T7) still PASS unchanged (marker behavior preserved). |

Tests (all within `target_paths`):

- **T1** `test_gtkb_session_id.py` — `resolve_session_id` precedence per order:
  `CLAUDE_CODE_SESSION_ID` resolves when sole; `explicit` wins; `CLAUDE_SESSION_ID`
  beats `CLAUDE_CODE_SESSION_ID` in `BRIDGE_WORK_INTENT_ORDER`; `GTKB_SESSION_ID`
  beats all in `MARKER_CONTINUITY_ORDER`; `""` when empty.
- **T2 (drift-lock, the recurrence guard)** `test_gtkb_session_id.py` —
  `set(BRIDGE_WORK_INTENT_ORDER) == set(SESSION_ID_ENV_VARS)` (bridge order is a
  full permutation); `set(MARKER_CONTINUITY_ORDER) <= set(SESSION_ID_ENV_VARS)`
  (marker is a documented subset); no order has duplicates or unknown members.
- **T3** `test_bridge_claim_cli.py` (extend) — claim resolves `CLAUDE_CODE_SESSION_ID`
  without `--session-id` (delegation intact).
- **T4** `test_bridge_compliance_gate_work_intent.py` (extend) — gate resolves
  `CLAUDE_CODE_SESSION_ID`, still prefers `payload.session_id`; fail-soft
  fallback tuple equals `BRIDGE_WORK_INTENT_ORDER`.
- **T5** `test_bridge_axis_2_surface_work_intent.py` + `test_bridge_propose_helper_work_intent.py`
  (extend) — parallel bridge-family assertions incl. fallback==canonical.
- **T6** `test_workstream_focus_session_role_marker.py` (extend) — existing
  `GTKB_SESSION_ID`-first assertion still PASSES; add: marker writer's order
  equals `gtkb_session_id.MARKER_CONTINUITY_ORDER`.
- **T7** `test_doctor_session_role_marker.py` (extend) — existing
  `GTKB_SESSION_ID`-first assertion still PASSES; add parity: doctor's
  `_SESSION_ID_ENV_FALLBACKS` equals `gtkb_session_id.MARKER_CONTINUITY_ORDER`.
- **Template-match** — existing byte-for-byte template-match tests for
  `bridge-compliance-gate.py` and `write_bridge.py` still PASS.

Execution (post-impl): `groundtruth-kb\.venv\Scripts\python.exe -m pytest`
over all 7 test files above + the gate-family sweep
`-k "bridge_compliance or bridge_author or template or session_role_marker"`,
plus `ruff check` + `ruff format --check` on every changed `.py`.

## Risk

Low-moderate. Behavior-preserving (both families keep their exact current order
+ membership; bridge already VERIFIED via `ea2040a5`; marker tests pass
unchanged). The gate import is fail-soft (never throws). The doctor keeps a
parity-tested copy, honoring the packaging boundary. Drift-lock + parity tests
prevent silent divergence. Higher-care item: the doctor edit touches packaged
`groundtruth_kb` source, so its parity test must be confirmed green before the
post-impl report.

## Rollback

`git revert` the implementation commit. No state migration, no canonical
artifact mutation. The committed minimal fix (`ea2040a5`) stays in force, so
reverting does not reintroduce the original defect.

## Acceptance Criteria

1. `scripts/gtkb_session_id.py` exists with `SESSION_ID_ENV_VARS`,
   `BRIDGE_WORK_INTENT_ORDER`, `MARKER_CONTINUITY_ORDER`, and `resolve_session_id`.
2. Bridge family (claim CLI, compliance gate, axis-2 surface, bridge-propose
   helper, both templates) resolves via the shared `BRIDGE_WORK_INTENT_ORDER`.
3. Marker writer resolves via shared `MARKER_CONTINUITY_ORDER`; doctor keeps a
   parity-tested copy equal to it (no scripts/ import).
4. Drift-lock (T2) + both marker/doctor precedence tests (T6/T7) + template-match
   tests PASS; existing marker `GTKB_SESSION_ID`-first behavior unchanged.
5. Tests T1-T7 PASS; `ruff check` + `ruff format --check` PASS on changed files.
6. No previously-passing test regresses.
7. Applicability preflight `preflight_passed: true`; clause preflight zero
   blocking gaps; `implementation_authorization.py begin` -> `authorized: true`.

## KB/MemBase Mutation

None. Implementation touches only source files and tests (see `target_paths`);
no `groundtruth.db` mutation. The KB operations referenced (WI-4270 capture,
`DELIB-20260625`, the PAUTH) were completed authorization-setup through governed
CLIs, not implementation-phase mutations.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights
reserved.
