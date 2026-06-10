NEW

# Unify session-id resolution into a single shared helper (eliminate the duplicated env-var lists)

bridge_kind: prime_proposal

author_identity: Prime Builder
author_harness_id: B
author_session_context_id: 544048b6-8b36-4469-8727-e77bf6a32333
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: explanatory output style; Claude Code

target_paths: ["scripts/gtkb_session_id.py", "scripts/bridge_claim_cli.py", "scripts/workstream_focus.py", ".claude/hooks/bridge-compliance-gate.py", ".claude/hooks/bridge-axis-2-surface.py", ".claude/skills/bridge-propose/helpers/write_bridge.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "groundtruth-kb/templates/skills/bridge-propose/helpers/write_bridge.py", "platform_tests/scripts/test_gtkb_session_id.py", "platform_tests/scripts/test_bridge_claim_cli.py", "platform_tests/hooks/test_bridge_compliance_gate_work_intent.py", "platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py", "platform_tests/skills/test_bridge_propose_helper_work_intent.py"]

Project Authorization: PAUTH-WI-4270-SESSION-ID-SHARED-RESOLVER
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-4270

## Summary

The session-id env-var list is hand-maintained in 6+ places that disagreed in
both membership and order. The immediate symptom — Claude Code's
`CLAUDE_CODE_SESSION_ID` being unrecognized by the bridge claim CLI and the
compliance gate — was fixed by the minimal-additive change committed as
`ea2040a5` (`fix(bridge): add CLAUDE_CODE_SESSION_ID env-var fallback to
work-intent resolution`), VERIFIED at
`bridge/gtkb-claude-code-session-id-env-var-gap-012.md`. That fix appended one
env-var line to each tuple but **left the duplication in place** — the
root cause that produced the drift remains.

This proposal completes the owner-decided fix (AUQ DECISION-0899: "Shared
helper") by extracting a single shared resolver so the lists can no longer
drift. It is a behavior-preserving refactor on top of the committed minimal
fix; the env-var recognition itself is already verified and in production.

Current duplicated copies (post-`ea2040a5`):

- `scripts/bridge_claim_cli.py` `SESSION_ENV_VARS` (arg-first via
  `_resolve_session_id`).
- `.claude/hooks/bridge-compliance-gate.py` `WORK_INTENT_SESSION_ENV_VARS`
  (`_resolve_work_intent_session_id` reads hook-stdin `payload.session_id`
  first, then the env list).
- `.claude/skills/bridge-propose/helpers/write_bridge.py`
  `WORK_INTENT_SESSION_ENV_VARS` (`resolve_work_intent_session_id(environ=...)`).
- `.claude/hooks/bridge-axis-2-surface.py` `WORK_INTENT_SESSION_ENV_VARS`.
- `scripts/workstream_focus.py` (marker writer; a third ordering that already
  included `CLAUDE_CODE_SESSION_ID` and so was untouched by `ea2040a5`).
- Two template mirrors under `groundtruth-kb/templates/` kept byte-for-byte in
  lockstep with their active counterparts by a template-match regression test.

Dogfood evidence captured while filing this proposal: with the minimal fix
committed, `python scripts/bridge_claim_cli.py claim
gtkb-session-id-shared-resolver-unification` succeeded WITHOUT `--session-id`,
resolving `CLAUDE_CODE_SESSION_ID`. This proposal does not change that behavior;
it removes the duplication that made the original omission possible.

## Owner Decisions / Input

This proposal is authorized by owner AskUserQuestion decisions on 2026-06-03
(the only valid owner-decision channel per
`.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid
Owner-Decision Channel):

1. **DECISION-0899 — design = shared resolution helper.** Owner selected
   "Shared helper" over minimal-additive and over a hybrid: one shared
   resolver, single documented precedence (payload/arg first, then a unified
   env list INCLUDING `CLAUDE_CODE_SESSION_ID`), consumed by the claim CLI,
   the marker writer, and the compliance gate.
2. **DECISION-0900 — project home = `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`.**
3. **DECISION-0901 — sequencing.** Owner selected "Let minimal land; shared
   helper = follow-on": the minimal fix lands first (now done, `ea2040a5` /
   VERIFIED `-012`), and this shared-helper unification is the sequenced
   follow-on captured as WI-4270.
4. **2026-06-03 follow-on AUQ — "File the WI-4270 follow-on now."**
5. **2026-06-03 authorization AUQ — "Authorize + file now"**, captured as
   `DELIB-20260625` (`source_type=owner_conversation`, `outcome=owner_decision`),
   which authorizes WI-4270 implementation via the narrow PAUTH cited above.

## Specification Links

Blocking (required) cross-cutting specs:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (v1, verified) — the work-intent claim/
  Write-gate contract is the mechanical enforcement of the canonical bridge
  index; a single authoritative session-id resolver hardens that contract
  against the recurrence class that produced the original omission.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (v1, specified) —
  this proposal cites every relevant cross-cutting governance specification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` (v1, specified) — this
  proposal carries machine-readable `Project Authorization`, `Project`, and
  `Work Item` metadata that resolve to an active, including authorization.
- `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` (v1, specified) — WI-4270
  is an active member of the cited project and is explicitly included by the
  cited PAUTH.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (v1, specified) — the
  Spec-Derived Verification Plan below maps each cited spec to concrete tests;
  the post-implementation report must carry the same mapping and execute the
  tests to receive VERIFIED.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (v1, specified) — all touched
  files are in-root under `E:\GT-KB`; platform-scope only;
  `applications/Agent_Red/` is untouched.

Advisory cross-cutting specs (matched by the applicability registry):

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (v1, verified) — this proposal cites
  prior MemBase records and Deliberation Archive entries rather than restating
  them.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (v1, verified) — WI-4270 was captured
  via the governed `gt backlog add` candidate path and reframed via
  `gt backlog update`; this NEW proposal follows the bridge lifecycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (v1, verified) — owner decisions, the
  work item, and tests are represented through canonical artifact classes.
- `GOV-STANDING-BACKLOG-001` (v1, verified) — WI-4270 is a visibility-preserving
  single-item backlog candidate (P2), now promoted to active implementation via
  this proposal.

Predecessor + precedent:

- `bridge/gtkb-claude-code-session-id-env-var-gap-001.md` … `-012.md`
  (predecessor thread; minimal fix VERIFIED at `-012`, committed `ea2040a5`).
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` + `DCL-SESSION-ROLE-RESOLUTION-001`
  (v1, specified) — established `CLAUDE_CODE_SESSION_ID` recognition and the
  read-at-call-site fallback-chain semantics this helper centralizes.

Rule-cited soft authority:

- `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Drafting Claim Step,
  § Mandatory Pre-Filing Preflight Subsection, § Mandatory Implementation-Start
  Authorization Metadata.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — a session-id env list copied
  into 6+ files is exactly the drift-prone plumbing this principle says belongs
  in one shared service; the shared helper + drift-lock test is that
  realization.

## Prior Deliberations

- Predecessor thread `gtkb-claude-code-session-id-env-var-gap` (NEW `-001`
  through VERIFIED `-012`): landed the minimal `CLAUDE_CODE_SESSION_ID`
  recognition fix and surfaced, via the `-003` and `-006` NO-GO findings, the
  parser/format and project-linkage gates this proposal satisfies up front
  (inline-JSON `target_paths`; concrete including-PAUTH/WI metadata).
- `DELIB-20260625` (this session): owner authorization to implement WI-4270
  under a narrow PAUTH.
- `bridge/gtkb-interactive-session-role-override-slice-2-session-role-marker-002.md`
  … `-008.md`: established `CLAUDE_CODE_SESSION_ID` as the Claude Code
  session-id env var and added it to `scripts/workstream_focus.py` + the
  doctor's marker resolver — the precedent generalized here.
- `DELIB-2618`, `DELIB-2583`, `DELIB-2644`: nearby interactive-session-role /
  marker-resolution deliberations corroborating the recognition direction.
- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS`: placement principle —
  the original defect was a traversed path (the gate's env list) missing a
  resource (the live env var); centralizing removes the per-copy miss.

## Requirement Sufficiency

Existing requirements sufficient. This is a behavior-preserving refactor that
unifies the already-verified resolution behavior; it introduces no new
requirement, policy, or external contract. No new spec is required.

## Implementation-Start Authorization Evidence

- `Project Authorization: PAUTH-WI-4270-SESSION-ID-SHARED-RESOLVER` is active,
  unexpired, attached to the active project
  `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, explicitly includes WI-4270 in
  `included_work_item_ids`, and authorizes mutation classes `hook_upgrade,
  source, cli_extension, test_addition` (forbids `deploy, git_push_force,
  spec_deletion` — none used). Its authorizing owner decision is
  `DELIB-20260625`.
- `Work Item: WI-4270` (origin defect, P2) is an active member of the project
  in `current_project_work_item_memberships`. The PAUTH therefore satisfies
  both the Write-time bridge-compliance membership/inclusion gate
  (`DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP`)
  and the implementation-start authorization gate.
- No cited spec link is in the PAUTH's `excluded_spec_ids` (empty).

After GO, Prime Builder runs
`python scripts/implementation_authorization.py begin --bridge-id gtkb-session-id-shared-resolver-unification`
to mint the implementation-start packet before any protected edit.

## Bridge INDEX Update Evidence

This NEW proposal is filed as `bridge/gtkb-session-id-shared-resolver-unification-001.md`
with a new `Document:` entry inserted at the top of `bridge/INDEX.md`
(`NEW: bridge/gtkb-session-id-shared-resolver-unification-001.md`). The update
is append-only; no prior bridge file or INDEX row is deleted or rewritten, and
`bridge/INDEX.md` remains the canonical workflow state. This satisfies
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Implementation Plan

1. **New shared helper `scripts/gtkb_session_id.py`** (stdlib-only, hook-safe):
   - `SESSION_ID_ENV_VARS`: the single canonical ordered tuple —
     `("CLAUDE_SESSION_ID", "CLAUDE_CODE_SESSION_ID", "GTKB_INHERITED_SESSION_ID",
     "CODEX_SESSION_ID", "CODEX_THREAD_ID", "ANTIGRAVITY_SESSION_ID",
     "GTKB_SESSION_ID")`. `CLAUDE_CODE_SESSION_ID` sits immediately after
     `CLAUDE_SESSION_ID` so an explicit `CLAUDE_SESSION_ID` operator override
     still wins (precedence preserved, matching the committed minimal fix).
   - `resolve_session_id(explicit=None, *, environ=None)`: returns `explicit`
     (hook `payload.session_id` or CLI `--session-id`) when truthy, else the
     first non-empty env var in `SESSION_ID_ENV_VARS`, else `""`.

2. **`scripts/bridge_claim_cli.py`**: delegate `_resolve_session_id` to
   `gtkb_session_id.resolve_session_id(arg_value, ...)`; the "required" error
   enumerates `SESSION_ID_ENV_VARS` (direct import — checkout always has the
   module on `scripts/`).

3. **`scripts/workstream_focus.py`**: replace its divergent tuple with the
   shared `SESSION_ID_ENV_VARS` / `resolve_session_id`. Behavior-preserving
   (it already included `CLAUDE_CODE_SESSION_ID`; only the order is unified).

4. **`.claude/hooks/bridge-compliance-gate.py`** and
   **`.claude/hooks/bridge-axis-2-surface.py`**: import `SESSION_ID_ENV_VARS`
   from `scripts.gtkb_session_id` using the SAME fail-soft try/except +
   local-fallback pattern the gate already uses for
   `REQUIRED_AUTHOR_METADATA_FIELDS`. The local fallback is a verbatim copy so
   a hook NEVER throws on a partial install (a throwing gate would block all
   bridge Writes). `_resolve_work_intent_session_id` keeps payload-first
   precedence; only the env list source changes.

5. **`.claude/skills/bridge-propose/helpers/write_bridge.py`**: same fail-soft
   import + fallback; `resolve_work_intent_session_id` delegates.

6. **Template mirrors** updated byte-for-byte in lockstep with their active
   counterparts; the fail-soft fallback keeps freshly-scaffolded adopter hooks
   working before they have the shared module (no `templates/scripts/` tree).

## KB/MemBase Mutation

None. This implementation touches only source files and tests (see
`target_paths`); it performs no `groundtruth.db` / MemBase mutation, which is
why `groundtruth.db` is intentionally absent from `target_paths`. The KB
operations referenced elsewhere in this proposal (the WI-4270 backlog capture,
`DELIB-20260625`, and the `PAUTH-WI-4270-SESSION-ID-SHARED-RESOLVER`
authorization) are completed authorization-setup provenance performed before
implementation through governed CLIs, plus read-only verification queries —
not implementation-phase mutations this proposal authorizes.

## Spec-Derived Verification Plan

| Spec | Tests / Evidence |
|------|------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Integration test (T-INT): a claim recorded under a `CLAUDE_CODE_SESSION_ID` value passes the compliance gate holder check for the same session without `--session-id`. Plus the live dogfood claim already captured. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Pre-filing applicability preflight on this file + the post-impl report reports `preflight_passed: true`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` + `DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001` | `implementation_authorization.py begin` yields `authorized: true` from the PAUTH/Project/WI triad; the Write-time membership/inclusion gate passed at filing. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping + tests T1-T5 + post-impl executed-command evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `rg --hidden SESSION_ID_ENV_VARS -l` lists only in-root files; no `applications/Agent_Red/` match. |
| `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` + `DCL-SESSION-ROLE-RESOLUTION-001` | T1-T2 assert precedence + `CLAUDE_CODE_SESSION_ID` inclusion equal to the verified minimal-fix behavior. |

Tests (added/extended; all within `target_paths`):

- **T1** `platform_tests/scripts/test_gtkb_session_id.py` — `resolve_session_id`
  returns `CLAUDE_CODE_SESSION_ID` when it is the only env var set; returns
  `explicit` when supplied; returns `CLAUDE_SESSION_ID` when both it and
  `CLAUDE_CODE_SESSION_ID` are set (precedence); returns `""` when nothing set.
- **T2 (drift-lock)** `platform_tests/scripts/test_gtkb_session_id.py` — assert
  every consumer's fail-soft fallback tuple equals
  `gtkb_session_id.SESSION_ID_ENV_VARS` (copies can never silently drift again
  — the core recurrence guard).
- **T3** `platform_tests/scripts/test_bridge_claim_cli.py` (extend) — `claim`
  resolves `CLAUDE_CODE_SESSION_ID` without `--session-id` (delegation intact).
- **T4** `platform_tests/hooks/test_bridge_compliance_gate_work_intent.py`
  (extend) — `_resolve_work_intent_session_id` resolves `CLAUDE_CODE_SESSION_ID`
  and still prefers `payload.session_id`.
- **T5** `platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py`
  (extend) + `platform_tests/skills/test_bridge_propose_helper_work_intent.py`
  (extend) — parallel resolution assertions for those surfaces.
- **T-INT** (integration; in T4's module) — claim-recorded-then-gate-holder
  round-trip with `CLAUDE_CODE_SESSION_ID` only.
- **Template-match** — existing byte-for-byte template-match tests for
  `bridge-compliance-gate.py` and `write_bridge.py` must still PASS.

Execution (post-impl): `groundtruth-kb\.venv\Scripts\python.exe -m pytest
platform_tests/scripts/test_gtkb_session_id.py
platform_tests/scripts/test_bridge_claim_cli.py
platform_tests/hooks/test_bridge_compliance_gate_work_intent.py
platform_tests/hooks/test_bridge_axis_2_surface_work_intent.py
platform_tests/skills/test_bridge_propose_helper_work_intent.py -v`, plus the
gate-family sweep `-k "bridge_compliance or bridge_author or template"` and
`ruff check` + `ruff format --check` on every changed `.py`.

## Risk

Low. This is a behavior-preserving refactor on top of an already-VERIFIED fix.
The gate import is fail-soft (try/except with verbatim local fallback), so a
hook never throws. Drift-lock (T2) and template-match tests prevent silent
divergence. `workstream_focus.py` already included the var, so its unification
is order-only.

## Rollback

`git revert` the implementation commit. No state migration, no canonical
artifact mutation, no fixture change beyond the new/extended tests. The
committed minimal fix (`ea2040a5`) remains in force, so reverting this refactor
does not reintroduce the original defect.

## Acceptance Criteria

1. `scripts/gtkb_session_id.py` exists with `SESSION_ID_ENV_VARS` (incl.
   `CLAUDE_CODE_SESSION_ID`) and `resolve_session_id`.
2. The claim CLI, marker writer, compliance gate, bridge-axis-2 surface, and
   bridge-propose helper all resolve session id through the shared helper
   (directly, or fail-soft for hooks).
3. A Claude Code session resolves session id (claim + gate) with no
   `--session-id`, exactly as the committed minimal fix already does.
4. Drift-lock test (T2) and the byte-for-byte template-match tests PASS.
5. Tests T1-T5 + T-INT PASS; `ruff check` and `ruff format --check` PASS on all
   changed files.
6. No previously-passing test regresses.
7. Pre-filing applicability preflight on the post-impl report reports
   `preflight_passed: true` with `missing_required_specs: []`; clause preflight
   reports zero blocking gaps; `implementation_authorization.py begin` reports
   `authorized: true`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights
reserved.
