REVISED

bridge_kind: prime_proposal
Document: gtkb-fab-16-harness-parity-remediation
Version: 003
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-11
Responds-To: bridge/gtkb-fab-16-harness-parity-remediation-002.md

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4428
Project Authorization: PAUTH-FAB16-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: 9660f4cb-1b84-410e-a024-febdabe7c541
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["config/agent-control/harness-capability-registry.toml", "scripts/check_harness_parity.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/**"]

No KB mutation: all (re-scoped) FAB-16 changes are config (harness-capability-registry.toml), source (the parity checker), and doctor — no `groundtruth.db` write. `groundtruth.db` is intentionally NOT in target_paths. No harness role/status transaction (the Goose disposition is a classification/exclusion correction, not a role transaction; that remains FAB-15's domain).

---

# FAB-16 — Harness Parity Remediation (re-scoped)

WI-4428 (FAB-16) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-061 (Antigravity skill-adapter drift),
HYG-062 (Goose classification), HYG-063 (hardcoded parity fallback). Source advisory:
`bridge/gtkb-fable-investigation-advisory-001.md` (v2 admit table). Couples to FAB-15 (the registry
topology restore).

## Revision Scope

This REVISED-003 supersedes the GO'd `-001` scope. During implementation under the GO at `-002`, two
material facts emerged that the GO could not have anticipated:

1. **Area 2 (HYG-061 Antigravity adapter regen) is BLOCKED — re-scoped OUT.** Running
   `scripts/generate_antigravity_skill_adapters.py --update-registry` updates only the registry TOML and
   writes **no** adapter files, yet `config/agent-control/harness-capability-registry.toml` declares **36**
   antigravity skill adapters. `.antigravity/` holds only 5 files (config.toml, README.md, 3 scratch) and
   no generated adapters, so `check_harness_parity.py --harness antigravity` stays FAIL (22 STALE + 14
   MISSING) after regen. **The GO's Area-2 acceptance gate — "Antigravity parity returning 0 stale and 0
   missing adapters after regen" — is therefore UNREACHABLE with the current generator.** The
   generator↔registry drift is itself a distinct defect, filed as a standalone backlog item (the 4441
   generator-defect work item, `origin=defect`, `component=cross-harness-tooling`). Area 2 is deferred
   behind that item; FAB-16 no longer claims the antigravity regen.

2. **Area 1 (HYG-062 Goose) is SHARPENED per a superseding owner decision.** `DELIB-FAB16-GOOSE-NO-ROLE-
   OPENROUTER-SDK-20260611` (owner, 2026-06-11, verbatim: *"Goose does not need to have any role in GT-KB.
   Goose is acting as a desktop UI for the OpenRouter cloud API and nothing more. OpenRouter participates
   in the bridge via the SDK."*) **supersedes the `-001` "add a Goose UI-client registry entry" framing.**
   Goose (E) is NOT a GT-KB dispatch harness or bridge participant — it needs no operating role, no
   headless surface, and no capability-floor obligation. The correct fix is to make the parity checker
   **stop treating Goose as a dispatch harness** (classify it as a no-role UI client / exclude it from the
   dispatch-projection parity selection), while OpenRouter (F) remains the SDK bridge participant. Still no
   headless wrapper, still no Goose retirement.

3. **Area 3 (HYG-063) is unchanged in intent but narrowed to what is genuinely open.** Live-state
   inspection shows `check_harness_parity.py` already derives its known-harness set from
   `load_harness_projection`; the remaining work is removing the residual `_FALLBACK_KNOWN_HARNESSES =
   ("claude", "codex")` hardcode and making the degraded-projection path report the projection error rather
   than silently assuming two vendors.

`target_paths` are narrowed accordingly: the Area-2 regen surfaces (`scripts/generate_codex_skill_adapters.py`,
`.antigravity/**`, `.codex/skills/**`) are REMOVED; the registry, the parity checker, the doctor, and the
tests remain.

## Summary

- **HYG-061 (Antigravity adapters):** DEFERRED — blocked on the generator defect (the 4441 item); the
  generator emits 0 of the 36 registry-declared adapters, so parity cannot reach 0/0 from FAB-16.
- **HYG-062 (Goose classification):** Goose (E) has no GT-KB role; it is purely OpenRouter's desktop UI.
  The parity checker must stop treating it as a dispatch harness (no-role UI-client exclusion).
- **HYG-063 (parity fallback):** remove the residual `("claude","codex")` hardcode; the degraded-projection
  path reports the projection failure rather than silently assuming two vendors.

## Specification Links

- `GOV-HARNESS-ROLE-PORTABILITY-001` — the harness model; roles attach to harnesses by owner assignment,
  not vendor (HYG-063 fallback removal aligns with this).
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — multi-harness configuration; the parity checker must reflect
  the configured fleet, and Goose's no-role/non-dispatch status must be representable (HYG-062, HYG-063).
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — the capability floor that Goose (a no-role UI client) is
  explicitly outside; the floor still governs genuine dispatch harnesses (HYG-062; the deferred HYG-061).
- `GOV-08` (Knowledge Database is the single source of truth) — the parity checker derives the known-harness
  set from the canonical registry projection, not a hardcode (HYG-063).
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — cross-harness coverage; excluding a non-dispatch UI client keeps the
  parity surface honest (HYG-062).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all FAB-16 changes are in-root; see Isolation Placement
  Compliance below.
- `GOV-STANDING-BACKLOG-001` — WI-4428 is the governed backlog authority; the deferred Area 2 is tracked as
  a separate standalone backlog item.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle for the registry/checker changes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `REVISED` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-061/062/063 v2 admits).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB16-REMEDIATION-20260610` — this cluster's original owner clarification + determined fixes.
- `DELIB-FAB16-GOOSE-NO-ROLE-OPENROUTER-SDK-20260611` — the **superseding** owner decision: Goose has no
  GT-KB role; it is OpenRouter's desktop UI; OpenRouter is the SDK bridge participant. Refines HYG-062 away
  from the `-001` "UI-client registry entry" framing toward a no-role/non-dispatch exclusion.
- _FAB-15 (`gtkb-fab-15-role-narrative-spec-reconciliation`) restores the registry topology this parity
  work assumes; FAB-16 keeps the harness surfaces consistent with that restored fleet._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10 (`DELIB-FAB16-REMEDIATION-20260610`) and refined on 2026-06-11
(`DELIB-FAB16-GOOSE-NO-ROLE-OPENROUTER-SDK-20260611`):

1. **HYG-062 = Goose has no GT-KB role (superseding).** Goose (E) is purely OpenRouter's desktop UI;
   OpenRouter (F) is the SDK bridge participant. The parity checker must stop treating Goose as a dispatch
   harness (no-role UI-client exclusion); build no headless wrapper; do not retire Goose.
2. **HYG-061 = regenerate the Antigravity adapters** — re-scoped OUT of FAB-16: the generator emits 0 of 36
   declared adapters (the 4441 generator-defect item), so the regen acceptance gate is unreachable until
   that defect is fixed.
3. **HYG-063 = remove the hardcoded ('claude','codex') parity fallback** — derive from the canonical
   registry projection; report a degraded projection rather than a two-vendor assumption.

## Requirement Sufficiency

**Existing requirements sufficient.** The dispositions are fixed by `DELIB-FAB16-REMEDIATION-20260610` and
the superseding `DELIB-FAB16-GOOSE-NO-ROLE-OPENROUTER-SDK-20260611`; the governing specifications
(`GOV-HARNESS-ROLE-PORTABILITY-001`, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`,
`GOV-HARNESS-ONBOARDING-CONTRACT-001`, `GOV-08`, `DCL-CROSS-HARNESS-ENFORCEMENT-001`) already constrain the
harness-model, parity, and onboarding surfaces. No new requirement is needed. The Goose no-role exclusion
is representable within the existing capability-registry + parity-checker semantics.

## Scope and Boundaries

In scope: the Goose no-role/non-dispatch exclusion (Area 1) + the parity-fallback removal (Area 3). Out of
scope and explicitly excluded: the Antigravity adapter regen (Area 2 — deferred behind the 4441
generator-defect item until the generator emits the declared adapters); building a Goose headless wrapper
(owner: no); retiring Goose (owner: keep as OpenRouter UI); any harness role/status transaction (FAB-15's
registry restore); mutating the external Agent Red repository; deploy/push. This proposal absorbs the
advisory's overlap for FAB-16 (the parity-remediation items 3459/4364) by describing them here.

## Proposed Implementation

**Area 1 — HYG-062 Goose no-role exclusion.** In `config/agent-control/harness-capability-registry.toml`,
record Goose (E) as a no-role desktop UI client for interactive OpenRouter (F) sessions (no headless surface,
no capability-floor obligation, intentional). In `scripts/check_harness_parity.py`, exclude no-role
UI-client entries from the dispatch-projection parity selection so Goose is no longer reported as a harness
missing a headless surface. OpenRouter (F) remains the SDK bridge participant; no role transaction.

**Area 3 — HYG-063 parity-fallback removal.** Remove the residual `_FALLBACK_KNOWN_HARNESSES = ("claude",
"codex")` hardcode in `scripts/check_harness_parity.py`; rely on the known-harness set derived from the
canonical registry projection (`groundtruth_kb.harness_projection`), and make the degraded-projection path
report the projection failure explicitly rather than silently assuming two vendors. Reconcile the doctor's
harness-parity surface with the same derived set where it consumes the checker.

**Area 2 — DEFERRED.** The Antigravity adapter regen is not attempted in FAB-16; it is tracked by the 4441
generator-defect work item (`scripts/generate_antigravity_skill_adapters.py` emits 0 of 36 declared
adapters). When that generator defect is fixed, antigravity parity can reach 0/0 in a follow-on.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all (re-scoped) FAB-16 changes are in-root under `E:\GT-KB\` —
the capability registry under `config/agent-control/`, the parity checker under `scripts/`, the doctor
update in the in-root `groundtruth-kb/src/groundtruth_kb/` tree, tests under `platform_tests/`, and this
bridge file under `E:\GT-KB\bridge\`. The cluster relocates no file, touches no `applications/` subtree, and
writes no out-of-root artifact.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` + `DCL-CROSS-HARNESS-ENFORCEMENT-001` (HYG-062) | test: Goose (E) is recorded as a no-role UI client; `check_harness_parity.py` no longer reports Goose as a dispatch harness missing a headless surface; genuine dispatch harnesses are still evaluated |
| `GOV-HARNESS-ROLE-PORTABILITY-001` + `GOV-08` (HYG-063) | test: the parity checker's known-harness set derives from the registry projection (the real fleet), not a hardcode; a degraded-projection path reports the projection failure rather than silently falling back to `("claude","codex")` |
| Area 2 deferral (HYG-061) | confirmation: FAB-16 does NOT assert antigravity parity 0/0; the generator defect is tracked by the 4441 standalone item |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` + `ruff check` AND `ruff format --check` on changed Python |

## Acceptance Criteria

1. Goose (E) is recorded as a no-role UI client for OpenRouter interactive sessions; the parity checker stops
   flagging it as a dispatch harness; no headless wrapper is built and Goose is not retired.
2. The `("claude","codex")` fallback hardcode is removed; the known-harness set derives from the registry
   projection; the degraded-projection path reports the failure explicitly.
3. Area 2 (antigravity regen) is explicitly deferred to the 4441 generator-defect item; FAB-16 makes no
   antigravity parity 0/0 claim.
4. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Backlog Visibility

FAB-16 is WI-4428 under `GOV-STANDING-BACKLOG-001`; this REVISED performs no bulk backlog operation. The
re-scoped-out Area 2 is captured as a standalone defect inventory item (the 4441 generator-defect work item,
`origin=defect`, `approval_state=unapproved`) for future consideration — a self-improvement capture, not an
implementation approval.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-16-harness-parity-remediation-003.md` with a matching `REVISED` line inserted at
the top of `bridge/INDEX.md` (above the `-002` GO); append-only — no prior version deleted or rewritten. This
REVISED narrows a GO'd scope after implementation surfaced an unreachable acceptance gate; nothing implements
on the narrowed scope until Loyal Opposition records a fresh `GO`. `GOV-FILE-BRIDGE-AUTHORITY-001` is honored.

## Risk and Rollback

- **Risk — the Goose no-role exclusion hides a real harness gap:** the exclusion applies only to a harness
  the owner has confirmed has no GT-KB role (OpenRouter's UI shell); the parity checker still evaluates every
  genuine dispatch harness. **Rollback:** revert the registry marker + checker change.
- **Risk — deriving the known-harness set from the projection fails when the projection is unavailable:** the
  replacement reports the projection error rather than silently assuming two vendors. **Rollback:** revert to
  the prior constant.
- **Risk — deferring Area 2 leaves antigravity parity FAIL:** that FAIL is pre-existing and now correctly
  attributed to the generator defect (the 4441 item) rather than masked by an unreachable FAB-16 acceptance
  gate. **Rollback:** n/a (no change to the antigravity surface in this REVISED).

## Recommended Implementation Routing

**Opus/Codex** — the Goose exclusion + the projection-derived known-harness set touch the harness-model and
parity-checker semantics; not cheap-model candidates. Coordinate with FAB-15 (the registry restore).

## Recommended Commit Type

`fix:` — repairs a harness misclassification (Goose treated as a dispatch harness) and a two-vendor hardcode
fallback, with a small `feat:`-class addition (the no-role UI-client classification in the capability
registry). The antigravity adapter regen is deferred to a separate defect item.
