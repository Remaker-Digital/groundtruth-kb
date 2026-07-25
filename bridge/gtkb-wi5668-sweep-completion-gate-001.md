NEW
::init gtkb lo
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: c58a8564-bed2-41d4-851b-075b84e86797
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Document: gtkb-wi5668-sweep-completion-gate
Version: 001
bridge_kind: prime_proposal
Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5668
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_doctor_skill_rename_sweep.py"]

# WI-5668 — Sweep completion gate: doctor check for zero remaining pre-rename skill references

## Motivation

The GTKB-SKILL-RENAME-REFERENCE-SWEEP program (slices S1-S6) needs a mechanical completion gate so its incompleteness stays visible and "done" is objective (count = 0) rather than a judgment call. Per the Deterministic Services Principle, the driver should be a deterministic check, not session memory. This adds that ratchet: a `gt project doctor` check that reports the count of remaining bare pre-rename skill-directory references and WARNs while any remain.

## Proposed Change

1. Add `_check_skill_rename_reference_sweep(target)` to `groundtruth-kb/src/groundtruth_kb/project/doctor.py`, returning a `ToolCheck`:
   - `name="skill-rename-reference-sweep"`, `required=False`, `found=True`.
   - `status="warning"` with `message` = the count + up to ~8 sample `path:line` hits while count > 0; `status="pass"` with a "0 remaining" message at zero.
   - `required=False` (surfaced warning, not a hard release-block) initially, so it never breaks an unrelated release while the program is in flight; a follow-on may promote it to `required=True` once the count is near zero.
2. Register the check in the doctor report build (the `checks.append(...)` block near the other hygiene checks, e.g., adjacent to `_check_untracked_terminal_verified_verdicts`).
3. Add `platform_tests/scripts/test_doctor_skill_rename_sweep.py`: seed a temp tree with a bare `skills/<name>/` reference → assert the check returns `warning` with count >= 1 and the offending path in the message; remove it → assert `pass`; assert excluded paths (bridge/, archive, .gtkb-state) do NOT count.

### Detection design

- Enumerate the current `.claude/skills/` directory names; derive the set of pre-rename bare names as `{name.removeprefix("gtkb-") for name in current_dirs}` intersected with names that were actually renamed (a `gtkb-<name>` dir exists). This makes the check self-maintaining — it flags references to any bare name whose canonical is now `gtkb-<name>`, without hardcoding a 43-skill list.
- Enumerate candidate files via `git ls-files` (tracked only) and scan for `skills/<bare>/` references (both `.claude/skills/<bare>/` and quoted `"<bare>"` path segments in a `skills` Path construction) where `<bare>` is in the derived set.
- EXCLUDE: `bridge/**` (append-only audit trail), `RETIRED-*/**`, `BARRED-*/**`, `archive/**`, `archive-*/**` (historical), and `.gtkb-state/**` (runtime + this program's own tracking drafts). These retain bare refs intentionally and must never be edited (per the sweep scope + PAUTH forbids).
- Count remaining hits; report count + sample. Scaffold/template refs under `groundtruth-kb/templates/**` ARE counted (owner directed the scaffold cluster be renamed to gtkb-*, slice S6), so they correctly keep the gate non-zero until S6 lands.

## Specification Links

- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — a repetitive/deterministic completion signal belongs in a service (this check), not session memory.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — the bridge/verify skill tooling whose canonical references this gate enforces.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — the sweep project's standing PAUTH under which this WI proceeds.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — implementation-proposal specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-derived unit test for the check.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — in-root placement; this change is platform-only (`groundtruth-kb/src`, `platform_tests`) and touches no `applications/<child>` subtree. Satisfied.

## Requirement Sufficiency

Existing requirements sufficient. The gtkb- rename is authoritative (`DELIB-202667105`/`202667106`; the capability registry is already gtkb-*), and the owner directed a mechanical completion gate (`DELIB-202667193`). This adds the deterministic enforcement mechanism for that existing target state; no new or revised requirement. An optional companion DCL formalizing the "all live references are canonical gtkb-" constraint (with the check as its assertion) is a possible later enhancement, not required here.

## Owner Decisions / Input

- Owner AUQ 2026-07-24 (session `c58a8564-bed2-41d4-851b-075b84e86797`, archived as `DELIB-202667193`): "full self-driving harness," which explicitly includes a mechanical completion gate that stays loud until the sweep is done. Owner then directed "kick off WI-5668" (this proposal).

## Prior Deliberations

- `DELIB-FAB19-REMEDIATION-20260610` — deterministic hygiene-detector expansion precedent (owner-approved deterministic detectors wired into the health surface); this check follows that pattern.
- `DELIB-1473` — Loyal Opposition Advisory: LO Hygiene Assessment Skill (hygiene-detection framing).
- `DELIB-202667105` (Canonical Skill Renaming Rollout v003 — GO) / `DELIB-202667106` (rollout — NO-GO) — the authoritative rename this gate enforces.
- `DELIB-202667193` — the owner decisions establishing the self-driving harness and this completion gate.
- Workflow `w0yjqag3h` (2026-07-24) — the exhaustive verified inventory of remaining pre-rename references the gate must drive to zero.

## Verification Plan (Spec-to-Test Mapping)

| Concern | Test / command | Expected |
| --- | --- | --- |
| Warns while refs remain | `test_doctor_skill_rename_sweep`: seed temp tree with a bare `skills/<name>/` ref | check returns `status="warning"`, count >= 1, offending path in message |
| Passes at zero | remove the seeded ref | check returns `status="pass"` |
| Exclusions honored | seed bare refs under bridge/, archive/, .gtkb-state/ | those do NOT increment the count |
| Self-maintaining derivation | current gtkb- dirs drive the bare-name set (no hardcoded list) | derived set matches renamed skills |
| Code quality | `ruff check` + `ruff format --check` on both changed files | pass |

## Risk And Rollback

Risk: low. Net-new, self-contained check; `required=False` so it surfaces as a warning without hard-failing any existing release or unrelated doctor run. Read-only (git ls-files + scan); no mutation. Rollback: remove the check function + its registration line + the test.

## Recommended Commit Type

`feat:` — net-new doctor check plus its test (additive completion-enforcement capability).

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
