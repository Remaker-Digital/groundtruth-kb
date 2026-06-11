NEW

bridge_kind: prime_proposal
Document: gtkb-fab-16-harness-parity-remediation
Version: 001
Author: prime-builder (Claude Opus 4.8, harness B) — interactive owner session
Date: 2026-06-10

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4428
Project Authorization: PAUTH-FAB16-20260610

author_identity: prime-builder
author_harness_id: B
author_session_context_id: d2f32e6b-5441-45b3-b355-097a2507f5f7
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: interactive owner session, ::init gtkb pb

target_paths: ["config/agent-control/harness-capability-registry.toml", "scripts/check_harness_parity.py", "scripts/generate_codex_skill_adapters.py", ".antigravity/**", ".codex/skills/**", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/**"]

No KB mutation: all FAB-16 changes are config (harness-capability-registry.toml), source (the parity checker + adapter generator), regenerated adapter outputs, and doctor — no `groundtruth.db` write. `groundtruth.db` is intentionally NOT in target_paths. Any harness role/status change remains out of scope (the Goose disposition is a classification correction, not a role transaction).

---

# FAB-16 — Harness Parity Remediation

WI-4428 (FAB-16) of PROJECT-FABLE-INVESTIGATION. Findings: HYG-061 (Antigravity skill-adapter drift),
HYG-062 (Goose registry/classification), HYG-063 (hardcoded parity fallback). Source advisory:
`bridge/gtkb-fable-investigation-advisory-001.md` (v2 admit table). Couples to FAB-15 (the registry
topology restore).

## Summary

- **HYG-061 (Antigravity adapters):** the Antigravity skill adapters have drifted — live 22 STALE + 14
  MISSING; `check_harness_parity.py --harness antigravity --json` exits 1.
- **HYG-062 (Goose classification):** Goose (identity E) has zero entries in
  `config/agent-control/harness-capability-registry.toml` and no headless invocation surface, with
  status=suspended — so the parity checker treats it as a dispatch harness with capability gaps. Owner
  clarification: **Goose is the desktop UI front-end for interactive sessions that use the OpenRouter (F)
  cloud models — it is not an independent dispatch harness.**
- **HYG-063 (parity fallback):** `check_harness_parity.py:26` hardcodes
  `_FALLBACK_KNOWN_HARNESSES = ("claude", "codex")`, a two-vendor fallback that misrepresents the real
  fleet (A–F) when the registry projection is unavailable.

## Specification Links

- `GOV-HARNESS-ROLE-PORTABILITY-001` — the harness model; roles attach to harnesses by owner assignment,
  not vendor (HYG-063 fallback removal aligns with this).
- `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` — multi-harness configuration; the parity checker must reflect
  the configured fleet, and Goose's UI-client classification must be representable (HYG-062, HYG-063).
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — the capability floor the Antigravity adapter regen restores and
  that Goose (as a non-dispatch UI client) is explicitly outside (HYG-061, HYG-062).
- `GOV-08` (Knowledge Database is the single source of truth) — the parity checker derives the known-harness
  set from the canonical registry projection, not a hardcode (HYG-063).
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — cross-harness coverage; the adapter parity keeps the harness surfaces
  consistent (HYG-061).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all FAB-16 changes are in-root; see Isolation Placement
  Compliance below.
- `GOV-STANDING-BACKLOG-001` — WI-4428 is the governed backlog authority; absorbs the overlapping items.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — durable-artifact lifecycle for the registry/config changes.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed under `bridge/` with a matching `NEW` INDEX entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — all relevant specs cited here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — verification derived below.

## Prior Deliberations

- `bridge/gtkb-fable-investigation-advisory-001.md` — chartering advisory (HYG-061/062/063 v2 admits).
- `DELIB-FABLE-GRILL-20260610-Q1..Q7` — project chartering decisions.
- `DELIB-FAB16-REMEDIATION-20260610` — this cluster's owner clarification + determined fixes (below).
- _FAB-15 (`gtkb-fab-15-role-narrative-spec-reconciliation`) restores the registry topology this parity
  work assumes; FAB-16 keeps the harness surfaces consistent with that restored fleet._

## Owner Decisions / Input

Collected via `AskUserQuestion` on 2026-06-10, persisted to `DELIB-FAB16-REMEDIATION-20260610`:

1. **HYG-062 = Goose is the desktop UI for OpenRouter interactive sessions (owner clarification, verbatim:
   "Goose is merely providing the desktop UI for interactive sessions with OpenRouter cloud models. It is
   not directly relevant.").** Therefore classify Goose (E) as a UI client / non-dispatch designation so the
   parity checker stops flagging it for a missing headless surface; build no headless wrapper; do not retire
   Goose (it remains the OpenRouter interactive desktop UI).
2. **HYG-061 = regenerate the Antigravity adapters** (determined fix, restores parity).
3. **HYG-063 = remove the hardcoded ('claude','codex') parity fallback** (determined fix, derive from the
   canonical registry projection).

## Requirement Sufficiency

**Existing requirements sufficient.** The disposition is fixed by `DELIB-FAB16-REMEDIATION-20260610`; the
governing specifications (`GOV-HARNESS-ROLE-PORTABILITY-001`, `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001`,
`GOV-HARNESS-ONBOARDING-CONTRACT-001`, `GOV-08`, `DCL-CROSS-HARNESS-ENFORCEMENT-001`) already constrain the
harness-model, parity, and onboarding surfaces. No new requirement is needed. The Goose UI-client
designation is a classification representable within the existing capability-registry schema (or a small
schema note), not a new requirement.

## Scope and Boundaries

In scope: the Goose UI-client classification + the two determined fixes. Out of scope and explicitly
excluded: building a Goose headless wrapper (owner: no); retiring Goose (owner: keep as OpenRouter UI); any
harness role/status transaction (that is FAB-15's registry restore); deploy/push. This proposal absorbs the
advisory's overlap for FAB-16 (the parity-remediation items 3459/4364) by describing them here.

## Proposed Implementation

**Area 1 — HYG-062 Goose classification.** Add a `config/agent-control/harness-capability-registry.toml`
entry (or designation field) classifying Goose (E) as a desktop UI client for interactive OpenRouter (F)
sessions, with `no headless invocation surface` recorded as intentional. Update `check_harness_parity.py`
to recognize the UI-client classification and exclude such entries from the headless-capability parity gap.

**Area 2 — HYG-061 Antigravity adapter regen.** Run the adapter generator
(`generate_codex_skill_adapters.py` / the antigravity equivalent) with `--harness antigravity
--update-registry` to regenerate the 22 STALE + 14 MISSING adapters; verify
`check_harness_parity.py --harness antigravity --json` exits 0.

**Area 3 — HYG-063 parity-fallback removal.** Replace `_FALLBACK_KNOWN_HARNESSES = ("claude", "codex")`
with the known-harness set derived from the canonical registry projection
(`groundtruth_kb.harness_projection`), so the parity checker reflects the real A–F fleet even when a
projection read degrades.

## Isolation Placement Compliance

`ADR-ISOLATION-APPLICATION-PLACEMENT-001`: all FAB-16 changes are in-root under `E:\GT-KB\` — the capability
registry under `config/agent-control/`, the parity checker + adapter generator under `scripts/`, the
regenerated adapter outputs under `.antigravity/` and `.codex/skills/`, the doctor update in the in-root
`groundtruth-kb/src/groundtruth_kb/` tree, and this bridge file under `E:\GT-KB\bridge\`. The cluster
relocates no file, touches no `applications/` subtree, and writes no out-of-root artifact.

## Spec-Derived Verification Plan

| Spec / requirement | Derived test |
|---|---|
| `GOV-GTKB-MULTI-HARNESS-ROLE-CONFIG-001` (HYG-062) | test: Goose (E) is classified as a UI client; `check_harness_parity.py` no longer reports Goose as a harness missing a headless surface; the OpenRouter UI relationship is recorded |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` + `DCL-CROSS-HARNESS-ENFORCEMENT-001` (HYG-061) | test: after regen, `check_harness_parity.py --harness antigravity --json` exits 0 (0 STALE, 0 MISSING) |
| `GOV-HARNESS-ROLE-PORTABILITY-001` + `GOV-08` (HYG-063) | test: the parity checker's known-harness set derives from the registry projection (A–F), not a hardcode; a degraded-projection path does not silently fall back to two vendors |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `pytest platform_tests/scripts/...` + `ruff check` AND `ruff format --check` on changed Python |

## Acceptance Criteria

1. Goose (E) is classified as a UI client for OpenRouter interactive sessions; the parity checker stops
   flagging it for a missing headless surface; no headless wrapper is built and Goose is not retired.
2. The Antigravity adapters are regenerated; `check_harness_parity.py --harness antigravity` exits 0.
3. The hardcoded `("claude","codex")` fallback is removed; the known-harness set derives from the registry.
4. All new tests pass; `ruff check` and `ruff format --check` clean on every changed Python file.

## Bridge Protocol Compliance

Filed at `bridge/gtkb-fab-16-harness-parity-remediation-001.md` with a matching `NEW` entry at the top of
`bridge/INDEX.md`; append-only. `GOV-FILE-BRIDGE-AUTHORITY-001` is honored; nothing implements until Loyal
Opposition records `GO`.

## Risk and Rollback

- **Risk — the Goose UI-client classification hides a real harness gap:** the classification only applies to
  Goose, which the owner has confirmed is a UI shell for OpenRouter, not a dispatch harness; the parity
  checker still flags genuine dispatch harnesses. **Rollback:** revert the registry entry + checker change.
- **Risk — adapter regen produces a bad adapter:** the regen is the documented generator path; parity exit-0
  is the acceptance gate. **Rollback:** restore the prior adapter set from git.
- **Risk — deriving the known-harness set from the projection fails when the projection is unavailable:** the
  replacement keeps a safe degraded behavior (report the projection error) rather than silently assuming two
  vendors. **Rollback:** revert to the prior constant.

## Recommended Implementation Routing

**Cheap-model-draftable for Areas 2–3 once GO'd** (mechanical regen + constant replacement); **Opus/Codex for
Area 1** (the Goose classification touches the harness model + parity checker semantics). Coordinate with
FAB-15 (the registry restore).

## Recommended Commit Type

`fix:` — repairs harness-parity drift (Antigravity adapters), a misclassification (Goose treated as a
dispatch harness), and a two-vendor hardcode, with a small `feat:`-class addition (the UI-client
classification in the capability registry).
