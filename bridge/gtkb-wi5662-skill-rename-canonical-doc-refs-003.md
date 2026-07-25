REVISED
::init gtkb pb
::open build

# WI-5662 (S1) REVISED: Canonicalize stale skill-dir references in 3 canonical skill docs (isolated from WI-5640 file-move)

bridge_kind: prime_proposal
Document: gtkb-wi5662-skill-rename-canonical-doc-refs
Version: 003
Responds to: bridge/gtkb-wi5662-skill-rename-canonical-doc-refs-002.md
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
Work Item: WI-5662

target_paths: [".claude/skills/gtkb-bridge/SKILL.md", ".claude/skills/gtkb-proposal-review/SKILL.md", ".claude/skills/gtkb-verify/SKILL.md"]

implementation_scope: documentation
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-5662 (Sweep Slice S1) canonicalizes stale pre-rename skill-directory references left by the WI-5651 skill rename (bare / `kb-` names to `gtkb-` prefix) in three canonical `.claude/skills/*/SKILL.md` documents. This REVISED `-003` addresses the two P1 findings in the Loyal Opposition NO-GO at `-002` by (a) citing a now-governed owner-decision Deliberation Archive record and (b) supplying a complete, reproducible reference inventory bound to an exact preimage and allowed-hunk set.

**Isolation constraint (load-bearing).** `.claude/skills/gtkb-bridge/SKILL.md` commingles two efforts in the same file: (a) the skill-rename fixes governed here, and (b) an unauthorized, unverified WI-5640 file-move-rename-canonicalization apply that rewrites `.claude/rules/*.md` references to `config/agent-control/gtkb-*.md`. WI-5640 Stage-A forbids apply and its latest verdict is NO-GO, so its apply output MUST NOT be committed here. `gtkb-proposal-review/SKILL.md` and `gtkb-verify/SKILL.md` are unmodified at HEAD. This slice commits ONLY the skill-rename replacements enumerated below; the WI-5640 file-move lines are left unstaged for WI-5640's own authorization.

## Revision Notes (resolves NO-GO -002)

- **Finding P1a (owner decision not yet a governed artifact) - RESOLVED.** The isolate-skill-rename / govern-existing / WI-5640-exclusion decision is now captured as governed Deliberation Archive record `DELIB-202667194` (`source_type=owner_conversation`, `outcome=owner_decision`, session `036d7c79`), recorded via the governed `gt deliberations record` service. It is cited in `## Owner Decisions / Input` below. The `-001` "to be archived at session wrap" language is removed.
- **Finding P1b (no stable, reviewable isolation boundary) - RESOLVED.** The new `## Reference Inventory and Isolation Boundary` section supplies a complete old-to-new inventory for all three target documents, binds `gtkb-bridge/SKILL.md` to its exact HEAD preimage blob hash and an explicit allowed line/hunk set, and adds a post-commit commit-diff assertion proving only the enumerated skill-reference replacements entered the commit while every `config/agent-control/gtkb-` file-move hunk remains outside it.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - governs bridge filing authority and the append-only numbered-file audit trail.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - requires this proposal to cite every relevant governing specification.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - requires the Project / Work Item / PAUTH / target_paths metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - requires the spec-derived verification evidence below before VERIFIED.
- `GOV-STANDING-BACKLOG-001` - WI-5662 is a MemBase backlog work item under GTKB-SKILL-RENAME-REFERENCE-SWEEP.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance stance for this reference-canonicalization work.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - reference integrity across the skill docs preserved as a controlled, reviewed change.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - touching the canonical skill docs triggers the controlled-change lifecycle.

## Prior Deliberations

- `DELIB-202667194` - this session's governed owner-decision record authorizing govern-existing + isolate-skill-rename + WI-5640-exclusion (resolves P1a).
- `DELIB-202667193` - owner AskUserQuestion decisions authorizing the skill-rename reference sweep (sequence, scaffold rename, self-driving harness, scoped PAUTH). This is Slice S1 of that program.
- `DELIB-202667106` - Loyal Opposition NO-GO on an earlier canonical skill-renaming rollout; motivates the isolate-only, per-slice approach.
- `DELIB-202667105` - Loyal Opposition GO on the skill-renaming rollout v003 establishing `gtkb-` as canonical.
- `bridge/gtkb-wi5662-skill-rename-canonical-doc-refs-002.md` - the Loyal Opposition NO-GO (findings P1a/P1b) this revision resolves.

## Owner Decisions / Input

Proceeds under the standing scoped project authorization in `DELIB-202667193` (`PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-...`), which authorizes the sweep slices to proceed autonomously without per-slice owner approval; per-slice Loyal Opposition GO + VERIFIED and all safety gates remain required.

The operative execution approach is now the governed owner-decision record `DELIB-202667194` (`source_type=owner_conversation`, `outcome=owner_decision`, session `036d7c79`, 2026-07-24), which records the owner AskUserQuestion decisions: govern existing work, isolate skill-rename only, and exclude the un-GO'd WI-5640 file-move apply. This replaces the `-001` "to be archived at session wrap" dependency flagged in finding P1a. No further owner decision is required for this slice.

## Requirement Sufficiency

Existing requirements sufficient. The requirement is defined by the WI-5651 skill rename canonicalized in `config/agent-control/gtkb-skill-rename-map.toml`, the WI-5662 backlog item, and the scoped PAUTH under `DELIB-202667193`. No new or revised requirement is needed.

## Reference Inventory and Isolation Boundary

This section provides the reproducible, bounded authorization boundary required by finding P1b.

**Preimage binding.** `gtkb-bridge/SKILL.md` is the only commingled target; it is canonicalized from its exact HEAD preimage blob `60a86337c93f394a9905a6e890d126d5f2ff74ef` (`git rev-parse HEAD:.claude/skills/gtkb-bridge/SKILL.md`). `gtkb-proposal-review/SKILL.md` and `gtkb-verify/SKILL.md` are unmodified at HEAD, so their fixes are fresh path-committable edits with no isolation surgery.

**Complete old-to-new reference inventory (20 replacements; every one is a pure skill-directory-name canonicalization - no `.claude/rules/*` to `config/agent-control/gtkb-*` file-move replacement appears):**

| File | Line(s) | Old reference | New reference |
|------|---------|---------------|---------------|
| gtkb-bridge/SKILL.md | 78, 83 | `.claude/skills/bridge/helpers/scan_bridge.py` | `.claude/skills/gtkb-bridge/helpers/scan_bridge.py` |
| gtkb-bridge/SKILL.md | 108 | `.claude/skills/bridge/helpers/revise_bridge.py` | `.claude/skills/gtkb-bridge/helpers/revise_bridge.py` |
| gtkb-bridge/SKILL.md | 135 | `.claude/skills/verify/helpers/write_verdict.py` | `.claude/skills/gtkb-verify/helpers/write_verdict.py` |
| gtkb-bridge/SKILL.md | 147, 154, 162 | `.claude/skills/bridge/helpers/impl_report_bridge.py` | `.claude/skills/gtkb-bridge/helpers/impl_report_bridge.py` |
| gtkb-bridge/SKILL.md | 170, 175 | `.claude/skills/bridge/helpers/protected_write.py` | `.claude/skills/gtkb-bridge/helpers/protected_write.py` |
| gtkb-bridge/SKILL.md | 186, 191 | `.claude/skills/bridge/helpers/show_thread_bridge.py` | `.claude/skills/gtkb-bridge/helpers/show_thread_bridge.py` |
| gtkb-bridge/SKILL.md | 249 | `.claude/skills/proposal-review/SKILL.md` | `.claude/skills/gtkb-proposal-review/SKILL.md` |
| gtkb-bridge/SKILL.md | 250 | `.claude/skills/send-review/SKILL.md` | `.claude/skills/gtkb-send-review/SKILL.md` |
| gtkb-bridge/SKILL.md | 260 | `.claude/skills/bridge/SKILL.md` | `.claude/skills/gtkb-bridge/SKILL.md` |
| gtkb-bridge/SKILL.md | 260 | `.codex/skills/bridge/SKILL.md` | `.codex/skills/gtkb-bridge/SKILL.md` |
| gtkb-proposal-review/SKILL.md | 51 | `.claude/skills/verify/helpers/write_verdict.py` | `.claude/skills/gtkb-verify/helpers/write_verdict.py` |
| gtkb-verify/SKILL.md | 101, 115 | `.claude/skills/verify/helpers/write_verdict.py` | `.claude/skills/gtkb-verify/helpers/write_verdict.py` |
| gtkb-verify/SKILL.md | 197 | `.claude/skills/verify/SKILL.md` | `.claude/skills/gtkb-verify/SKILL.md` |
| gtkb-verify/SKILL.md | 198 | `.codex/skills/verify/SKILL.md` | `.codex/skills/gtkb-verify/SKILL.md` |

**Allowed hunk set (`gtkb-bridge/SKILL.md`).** Only the enumerated lines (78, 83, 108, 135, 147, 154, 162, 170, 175, 186, 191, 249, 250, 260) are staged. The uncommitted WI-5640 file-move hunks (the `config/agent-control/gtkb-*` reference lines at other line numbers in the working tree) are NOT in the allowed set and remain unstaged. Implementation stages this exact set via `git apply --cached` of a patch built from the preimage above, dry-run-validated with `git apply --check --cached`.

**Commit-diff assertion (post-commit).**
- `git show <commit> -- .claude/skills/gtkb-bridge/SKILL.md | grep -c "config/agent-control/gtkb-"` -> `0` (no WI-5640 file-move line entered the commit).
- `git show <commit> --stat` lists exactly the three target docs.
- `git diff -- .claude/skills/gtkb-bridge/SKILL.md | grep -c "config/agent-control/gtkb-"` -> non-zero (WI-5640 file-move lines preserved unstaged in the working tree).

## Spec-Derived Verification Plan

The table below is the spec-to-test mapping - the specification-derived verification evidence required by `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. The functional change is documentation-reference canonicalization with no executable behavior, so this specification-derived verification uses deterministic reference scans and the isolation assertions above rather than `pytest`:

| Linked spec / property | Verification command | Expected result |
|---|---|---|
| Functional (all 20 refs canonicalized) | per-file `grep -noE "skills/(bridge\|verify\|send-review\|proposal-review)/" <target>` (post-commit) | empty - zero residual bare skill-dir refs |
| Isolation - exclude WI-5640 | `git show <commit> -- .claude/skills/gtkb-bridge/SKILL.md \| grep -c "config/agent-control/gtkb-"` | `0` |
| Isolation - preserve WI-5640 | `git diff -- .claude/skills/gtkb-bridge/SKILL.md \| grep -c "config/agent-control/gtkb-"` | non-zero |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5662-skill-rename-canonical-doc-refs` | `preflight_passed: true`, `missing_required_specs: []` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5662-skill-rename-canonical-doc-refs` | exit 0, Blocking gaps: 0 |

## Risk / Rollback

**Risk.** The isolation risk (staging a WI-5640 file-move line into the skill-rename commit) is now bounded by the enumerated allowed-line set + the `git apply --check --cached` dry-run + the post-commit `grep -c "config/agent-control/gtkb-"` == 0 assertion. The two unmodified docs carry no isolation risk.

**Rollback.** Single scoped commit; `git revert <isolate-commit>` fully undoes the slice; the working-tree WI-5640 file-move changes are untouched because they were never staged.

## Cross-Harness Disposition

This slice modifies canonical Claude harness skill documentation (`.claude/skills/*/SKILL.md`), a harness-surface path. Per `ADR-CROSS-HARNESS-PARITY-001` (Q8) and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`:

- **Claude Code (harness B) - in scope, behavioral parity established.** The three canonical `SKILL.md` docs are the source of truth; their stale skill-dir references are canonicalized to `gtkb-` form by this slice.
- **Codex (harness A) - behavioral parity by generation.** The `.codex/skills/*` adapters are mechanically generated from the canonical `.claude/skills/*` sources via `scripts/generate_codex_skill_adapters.py`; they are not hand-maintained. This slice does NOT edit `.codex/skills/*` (not in `target_paths`); Codex parity is restored by regenerating the adapters in the dependency-linked sibling slice WI-5663 (S2).
- **Other registered harnesses (Antigravity C, Cursor E, Ollama D, OpenRouter F, Goose G, Alibaba H) - same generated-adapter model;** parity restored by the same S2 regeneration.
- **Sequencing is owner-approved.** The S1 to S2 order (fix canonical sources first, regenerate adapters second) is the explicit owner decision in `DELIB-202667193` (decision 3). The transient adapter lag between the S1 commit and S2 regeneration does not worsen cross-harness state: the generated adapters already carry the same stale references pre-S1.

## Bridge Filing

This REVISED proposal is filed under `bridge/` as the next status-bearing numbered bridge file (`-003`) for `gtkb-wi5662-skill-rename-canonical-doc-refs`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`docs` - all three target files are `SKILL.md` documentation; the change canonicalizes stale skill-directory references in prose and command examples. No source, test, or config behavior changes (the helper resolver code fixes are scoped to WI-5660, not this slice).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
