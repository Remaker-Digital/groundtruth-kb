NEW
::init gtkb pb
::open build

# WI-5666 (S5): Canonicalize stale skill-dir references in .gitignore and live docs

bridge_kind: prime_proposal
Document: gtkb-wi5666-gitignore-docs-script-skill-refs
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-24 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 036d7c79-080f-441b-bec4-2d25f5fca7e3
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-SKILL-RENAME-REFERENCE-SWEEP-BOUNDED-AUTHORIZATION
Project: GTKB-SKILL-RENAME-REFERENCE-SWEEP
Work Item: WI-5666

target_paths: [".gitignore", "groundtruth-kb/docs/reference/canonical-terminology-detail.md", "docs/procedures/per-thread-finalization-repair.md", "docs/harness-parity-phase-2-matrix.md"]

implementation_scope: documentation | configuration
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-5666 (Sweep Slice S5) canonicalizes stale pre-rename skill-directory references left by the WI-5651 skill rename in non-code surfaces:

- **`.gitignore` (lines 617-618)** — the scratch-ignore patterns `.claude/skills/bridge/helpers/draft-*.md` and `.claude/skills/verify/helpers/draft-*` still name the pre-rename directories. Because those directories were renamed to `gtkb-bridge` / `gtkb-verify`, the patterns now match nothing, so helper-draft scratch files under the renamed dirs are no longer ignored. Fixing the patterns to the `gtkb-` names restores the intended ignore behavior.
- **Live reference/procedure docs** — `groundtruth-kb/docs/reference/canonical-terminology-detail.md`, `docs/procedures/per-thread-finalization-repair.md`, and `docs/harness-parity-phase-2-matrix.md` carry stale `.claude/skills/<bare>/` references that are canonicalized to `gtkb-` form per `config/agent-control/gtkb-skill-rename-map.toml`.

**Clean-slice properties.** All four target files are **unmodified at HEAD** (not in the working-tree diff), so — unlike the WI-5662 canonical docs — they carry **no commingled WI-5640 file-move apply**. The edits are fresh, path-committable skill-rename canonicalizations; no line-level isolation surgery is required, and the commit is a plain scoped commit of these four paths.

**Explicit exclusions (archive-vs-fix discipline).** This slice deliberately does NOT touch: (a) historical report snapshots (`docs/reports/agent-red-classification.md`, `non-disruptive-upgrade-audit.md`, the ChromaDB current-state analysis) — their stale refs are frozen historical evidence, not live references; (b) generated data artifacts (`docs/gtkb-dashboard/dashboard-data.json`); (c) dead one-off dispatch scripts (`scripts/_dispatch_wi5241_006_verdict.py`) — historical; (d) scripts owned by other slices — `scripts/verify_antigravity_dispatch.py` (WI-5661 live-break), `scripts/session_self_initialization.py` (WI-5650). `scripts/sot_compactness_audit.py` is excluded pending classification of whether its stale ref is a live path constant (WI-5661-class) or an inert comment; it is not folded into this documentation slice.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs bridge filing authority and the append-only numbered-file audit trail.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this proposal to cite every relevant governing specification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the Project / Work Item / PAUTH / target_paths metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the spec-derived verification evidence below before VERIFIED.
- `GOV-STANDING-BACKLOG-001` — WI-5666 is a MemBase backlog work item under GTKB-SKILL-RENAME-REFERENCE-SWEEP.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance stance for this reference-canonicalization work.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — reference integrity across gitignore/docs preserved as a controlled, reviewed change.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — touching these tracked artifacts triggers the controlled-change lifecycle.

## Prior Deliberations

- `DELIB-202667193` — owner AskUserQuestion decisions authorizing the skill-rename reference sweep (sequence, scaffold rename, self-driving harness, scoped PAUTH). This is Slice S5 of that program.
- `DELIB-202667106` — Loyal Opposition NO-GO on an earlier canonical skill-renaming rollout; motivates the isolate-only, per-slice approach.
- `DELIB-202667105` — Loyal Opposition GO on the skill-renaming rollout v003 establishing `gtkb-` as canonical.
- This session's owner AskUserQuestion decisions (2026-07-24, session `036d7c79`): govern existing work, isolate skill-rename only, exclude WI-5640 file-move apply. To be archived at session wrap as an `owner_conversation` deliberation.

## Owner Decisions / Input

Proceeds under the standing **scoped project authorization** in `DELIB-202667193` (`PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-…`), which authorizes the sweep slices to proceed autonomously without per-slice owner approval; per-slice Loyal Opposition GO + VERIFIED and all safety gates remain required. This session's owner AskUserQuestion decisions (session `036d7c79`) established: govern existing work; isolate skill-rename only; file the untouched slices (WI-5664 was verified already Codex-filed and is therefore skipped to avoid duplication). No further owner decision is required for this slice.

## Requirement Sufficiency

Existing requirements sufficient. The requirement is the WI-5651 skill rename canonicalized in `config/agent-control/gtkb-skill-rename-map.toml`, the WI-5666 backlog item, and the scoped PAUTH under `DELIB-202667193`. No new or revised requirement is needed.

## Spec-Derived Verification Plan

The table below is the **spec-to-test mapping** — the specification-derived verification evidence required by `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. Because the change is reference canonicalization in non-executable surfaces, this specification-derived verification uses deterministic reference scans rather than `pytest`:

| Linked spec / property | Verification command | Expected result |
|---|---|---|
| Functional (WI-5666 rename complete) | `grep -rhoE "\.(claude\|codex)/skills/[a-z0-9_-]+" .gitignore groundtruth-kb/docs/reference/canonical-terminology-detail.md docs/procedures/per-thread-finalization-repair.md docs/harness-parity-phase-2-matrix.md \| grep -vE "/gtkb-"` (post-commit) | empty — zero residual bare / `kb-` skill-dir refs |
| `.gitignore` behavior restored | `git check-ignore .claude/skills/gtkb-bridge/helpers/draft-x.md` (post-commit) | matched — the renamed-dir scratch pattern now ignores helper drafts |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5666-gitignore-docs-script-skill-refs` | `preflight_passed: true`, `missing_required_specs: []` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5666-gitignore-docs-script-skill-refs` | exit 0, Blocking gaps: 0 |

## Risk / Rollback

**Risk.** Minimal. All target files are unmodified at HEAD, so the edits are fresh path-committable canonicalizations with no isolation surgery and no commingling. The only behavior change is the `.gitignore` pattern fix, which strictly restores the intended (pre-rename) ignore semantics for helper-draft scratch under the renamed dirs.

**Rollback.** Single scoped commit; `git revert <commit>` fully undoes the slice.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi5666-gitignore-docs-script-skill-refs`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — the `.gitignore` change restores broken ignore behavior (the pre-rename scratch patterns match nothing after the rename), and the doc edits canonicalize stale references. No new capability; this repairs references and ignore semantics broken by the WI-5651 rename.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
