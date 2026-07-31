NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: dbc5c1cd-13f2-4ff8-81a5-a80c06799bae
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal
Document: gtkb-wi5678-genericize-advisory-role-framing
Version: 001
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5678

target_paths: [".claude/rules/canonical-terminology.md", ".claude/rules/file-bridge-protocol.md", ".claude/skills/gtkb-advisory-proposal/SKILL.md", ".claude/skills/gtkb-bridge/SKILL.md", ".codex/skills/gtkb-advisory-proposal/SKILL.md", ".codex/skills/gtkb-bridge/SKILL.md"]

# Defect-Fix Proposal — genericize LO-only Advisory Proposal framing to role-agnostic

## Claim

Advisory-framing documentation describes Advisory Proposals as
Loyal-Opposition-only. That contradicts (a) the enforced, already role-neutral
`bridge_kind` enum per `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`, and (b) owner
decision `DELIB-202667454`. This is documentation-vs-enforced-code drift: the
code is already role-agnostic, so the fix is doc reconciliation only, with no
behavioral change and no `bridge_kind` rename.

## Defect / Reproduction

Enforced enum (`DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`):
`{governance_advisory, implementation_report, index_reconciliation, lo_verdict,
operational_state_change, prime_proposal}`.

Reproduced in session dbc5c1cd (2026-07-24): filing an advisory with
`bridge_kind: loyal_opposition_advisory` — the value the current documentation
instructs — raised:

    BridgeComplianceError: [Governance] Invalid bridge_kind:
    'loyal_opposition_advisory'. Must be one of ['governance_advisory', ...]
    per DCL-BRIDGE-KIND-TAXONOMY-ENUM-001.

Re-filing with `governance_advisory` succeeded. Two advisories were then filed
by a Prime Builder session — `bridge/gtkb-wi5676-ban-gate-author-identity-false-positive-001.md`
and `bridge/gtkb-wi5677-begin-commit-after-report-nogo-gap-001.md` — empirically
demonstrating that advisory filing is role-agnostic in the enforced mechanism.

Drifted surfaces:

1. `.claude/skills/gtkb-bridge/SKILL.md` — states the non-implementation
   exemption set is `{spec_intake, governance_review, loyal_opposition_advisory}`;
   all three values are absent from the enforced enum.
2. `.claude/skills/gtkb-advisory-proposal/SKILL.md` — "Use this skill when Loyal
   Opposition, advisory mode, or a review session finds..." (role-restrictive).
3. `.claude/rules/file-bridge-protocol.md` — ADVISORY status row "Set by: Loyal
   Opposition", plus LO-only language in the Advisory Reports section.
4. `.claude/rules/canonical-terminology.md` — the "Loyal Opposition advisory"
   glossary entry.

## Proposed Scope

1. `gtkb-bridge/SKILL.md`: replace the stale exemption set with the enforced
   enum's non-implementation kinds per `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`
   (notably `governance_advisory`).
2. `gtkb-advisory-proposal/SKILL.md`: genericize trigger framing to role-neutral
   ("any role — Prime Builder or Loyal Opposition — may file...").
3. `file-bridge-protocol.md`: change the ADVISORY "Set by" cell to role-neutral
   and genericize the Advisory Reports section.
4. `canonical-terminology.md`: genericize the "Loyal Opposition advisory" entry
   to a role-neutral "governance advisory" entry, retaining the prior term as a
   historical alias so existing citations still resolve.

Documentation only. No source, hook, helper, or enum change is proposed.

## In-Root Placement Evidence

All four target paths are inside `E:\GT-KB`: `.claude/rules/canonical-terminology.md`,
`.claude/rules/file-bridge-protocol.md`, `.claude/skills/gtkb-advisory-proposal/SKILL.md`,
`.claude/skills/gtkb-bridge/SKILL.md`.

## Reviewer Note — tracked vs local skill surfaces

`.claude/rules/*.md` are tracked. `.claude/skills/*.md` are local-only in this
checkout, with tracked sources under `groundtruth-kb/templates/` and/or
`config/agent-control/`. The reviewer is asked to confirm whether the tracked
skill-source surfaces should be edited in the same slice or deferred to a
companion thread; this proposal declares only the four paths above.

## Cross-Harness Disposition

Per `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` (PARITY-DISPOSITION-GATE) and
`ADR-CROSS-HARNESS-PARITY-001` Q8, this slice touches `.claude/skills/**`, so
disposition is declared per applicable harness:

| Harness | Surface | Disposition |
| --- | --- | --- |
| Claude Code (B) | `.claude/skills/gtkb-advisory-proposal/SKILL.md`, `.claude/skills/gtkb-bridge/SKILL.md` | **Behavioral parity — canonical source edited.** Both are in `target_paths`. |
| Codex (A) | `.codex/skills/gtkb-advisory-proposal/SKILL.md`, `.codex/skills/gtkb-bridge/SKILL.md` (generated adapters, declared in `.codex/skills/MANIFEST.json`) | **Behavioral parity — adapters regenerated in-slice** from the canonical Claude sources via the governed adapter-generation path. Both are in `target_paths`. `MANIFEST.json` is NOT modified (no skill added, removed, or renamed). |
| Antigravity (C), Cursor, Ollama (D), OpenRouter | No skill-adapter surface exists for these two skills | **Not applicable** — no parity obligation; no waiver required. |

Because this slice is documentation-only and changes no skill behavior, parity
here means identical role-agnostic wording across the Claude canonical sources
and the Codex adapters; there is no executable behavior to diverge.

**Reviewer risk note.** `.codex/skills/gtkb-bridge/SKILL.md` is currently
modified in the working tree by a concurrent session. Adapter regeneration must
be hunk-isolated so the concurrent change is not captured, or the reviewer may
prefer to narrow this slice to the Claude canonical sources plus a companion
adapter thread. The reviewer is asked to choose; both paths are declared here so
the decision is explicit rather than implied.

## Specification Links

- `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` — the enforced role-neutral enum the documentation must match (governing authority).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority governing ADVISORY status.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable artifact reconciliation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — doc drift is a repair-class lifecycle trigger.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — artifact-oriented development framing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — satisfied by this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — satisfied by the verification plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — satisfied by the project-linkage triple above.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — placement/isolation authority for the multi-harness skill surfaces (`.claude/skills/**`, `.codex/skills/**`) touched by this slice; all target paths remain in-root and within their declared harness surfaces, and no application-scoped placement is affected.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` — parity disposition gate satisfied by the Cross-Harness Disposition section above.
- `ADR-CROSS-HARNESS-PARITY-001` — cross-harness parity decision basis (Q8 disposition requirement).

## Prior Deliberations

- `DELIB-202667454` — owner decision that Advisory Proposals are role-agnostic; the mandating decision for this repair.
- `DELIB-202667470` — owner authorization to implement WI-5678.
- `DELIB-20263636` — Advisory Report Template Spec REVISED-1 (template authority for ADVISORY sections).
- `DELIB-1500` / `DELIB-20263729` — Bridge ADVISORY status + ADVISORY_REPORT message type.
- `DELIB-202665912` — WI-5055 Advisory Proposal Skill verification.

## Owner Decisions / Input

- `DELIB-202667454` (AUQ `AUQ-defect-log-advisory-role-agnostic-2026-07-24`): "Advisory Proposals *are not* restricted to any role. Any direction that contradicts this is obsolete and must be purged. If you find any contrary direction, please create repair WI and initiate the fix."
- `DELIB-202667470` (owner authorization, 2026-07-24): "I authorize these: WI-5676, WI-5677, WI-5678. Please proceed with implementation."
- Reviewer decision requested: tracked-skill-source scope per the Reviewer Note above.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001` already
specifies the role-neutral enum, and `DELIB-202667454` already records the
owner's role-agnostic ruling. This slice reconciles documentation to those
existing requirements; it creates no new behavior and therefore needs no new or
revised requirement before implementation.

## Specification-Derived Verification Plan

| Requirement (linked spec) | Test / command | Expected |
| --- | --- | --- |
| Docs match enforced enum (`DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`) | grep the 4 targets for `loyal_opposition_advisory`, `spec_intake`, `governance_review` | no stale exemption values remain; `governance_advisory` present |
| Role-neutral framing (`DELIB-202667454`) | grep the 4 targets for LO-only advisory-authoring phrasing | none remain; role-neutral wording present |
| Historical alias retained | grep `canonical-terminology.md` for the prior term as alias | present as historical alias |
| Terminology consistency (`GOV-FILE-BRIDGE-AUTHORITY-001`) | `gt project doctor` canonical-terminology check | pass |
| Behavior unchanged (docs-only) | a Prime Builder session can file `governance_advisory` | already demonstrated by the two advisories cited above |

## Acceptance Criteria

- All four surfaces read role-agnostic; documentation and enforced enum reconciled.
- No LO-only advisory-restriction language remains in the four target paths.
- Prior term retained as a historical alias in canonical-terminology.
- Canonical-terminology doctor check passes.
- No source/runtime change; scoped commit contains only the four declared paths.

## Risks / Rollback

Low — documentation only; the `bridge_kind` token is already `governance_advisory`
in code, so there is no runtime risk. Residual risk is citation breakage for the
retired term, mitigated by retaining it as a historical alias. Rollback: revert
the scoped commit.

## Recommended Commit Type

Recommended commit type: `docs`
