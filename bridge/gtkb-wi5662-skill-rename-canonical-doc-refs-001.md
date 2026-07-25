NEW
::init gtkb pb
::open build

# WI-5662 (S1): Canonicalize stale skill-dir references in 3 canonical skill docs (isolated from WI-5640 file-move apply)

bridge_kind: prime_proposal
Document: gtkb-wi5662-skill-rename-canonical-doc-refs
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
Work Item: WI-5662

target_paths: [".claude/skills/gtkb-bridge/SKILL.md", ".claude/skills/gtkb-proposal-review/SKILL.md", ".claude/skills/gtkb-verify/SKILL.md"]

implementation_scope: documentation
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

WI-5662 (Sweep Slice S1) canonicalizes stale pre-rename skill-directory references in the canonical `.claude/skills/*/SKILL.md` documentation left behind by the WI-5651 skill rename (bare / `kb-` names → `gtkb-` prefix). A deterministic scan of the canonical skill docs finds ~30 residual stale references across three files:

- `.claude/skills/gtkb-bridge/SKILL.md` — 11 `.claude/skills/bridge/…`, 5 `.claude/skills/verify/…`, plus `send-review`, `proposal-review`, `kb-query`, `kb-session-wrap-scan`, `harness-parity-review`, `check-deliberations`, `structural-hygiene-review`, and `.codex/skills/{bridge,verify,advisory-proposal,advisory-intake,advisory-disposition}` doc references.
- `.claude/skills/gtkb-proposal-review/SKILL.md` — residual stale refs (file unmodified at HEAD).
- `.claude/skills/gtkb-verify/SKILL.md` — residual stale refs (file unmodified at HEAD).

Each stale reference is rewritten to its canonical `gtkb-`-prefixed form per `config/agent-control/gtkb-skill-rename-map.toml`. These references point at skill directories that no longer exist under the pre-rename name, so an agent following the docs hits a missing path.

**Isolation constraint (load-bearing).** The working-tree copy of `.claude/skills/gtkb-bridge/SKILL.md` commingles two distinct efforts in the same file: (a) the skill-rename fixes governed here, and (b) an *unauthorized, unverified* WI-5640 file-move-rename-canonicalization apply that rewrites `.claude/rules/*.md` references to `config/agent-control/gtkb-*.md`. WI-5640 (Stage-A) explicitly forbids apply and its latest verdict is NO-GO, so its apply output MUST NOT be committed here. This proposal governs and commits ONLY the skill-rename changes; the WI-5640 file-move lines are left unstaged in the working tree for WI-5640 to handle under its own authorization. `gtkb-proposal-review/SKILL.md` and `gtkb-verify/SKILL.md` are unmodified at HEAD (no commingling) — their fixes are fresh, path-committable edits; only `gtkb-bridge/SKILL.md` requires line-level staging to exclude the file-move lines.

The two helper resolvers that carry skill-rename fallbacks (`impl_report_bridge.py`, `revise_bridge.py`) are functional code, not documentation references, and are governed under the sibling WI-5660 revise-bridge-propose-path thread — deliberately out of scope here to keep this a clean `docs` slice.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs bridge filing authority and the append-only numbered-file audit trail this proposal enters.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this proposal to cite every relevant governing specification (satisfied by this section).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires the Project / Work Item / PAUTH / target_paths metadata present in the header above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — requires the spec-derived verification evidence in the plan below before VERIFIED.
- `GOV-STANDING-BACKLOG-001` — WI-5662 is a MemBase backlog work item under project GTKB-SKILL-RENAME-REFERENCE-SWEEP; this proposal advances it through the governed protocol.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance stance: this slice treats the canonical skill docs as durable artifacts under controlled change.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — the sweep is artifact-network work; reference integrity across the skill docs is preserved as a controlled, reviewed change rather than an ad-hoc edit.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — touching the canonical skill docs triggers the controlled-change lifecycle for those artifacts.

## Prior Deliberations

- `DELIB-202667193` — owner AskUserQuestion decisions authorizing the skill-rename reference sweep (sequence, scaffold rename, self-driving harness, scoped PAUTH). This proposal is Slice S1 of that authorized program and proceeds under the scoped PAUTH it grants.
- `DELIB-202667106` — Loyal Opposition NO-GO on an earlier canonical skill-renaming rollout; its findings motivate the isolate-only, per-slice approach taken here (no bulk uncontrolled apply).
- `DELIB-202667105` — Loyal Opposition GO on the skill-renaming rollout v003 establishing `gtkb-` as canonical; this slice completes the residual reference canonicalization that rollout began.
- This session's owner AskUserQuestion decisions (2026-07-24, session `036d7c79`) established the operative approach: govern the existing work, isolate the skill-rename changes only, and exclude the WI-5640 file-move apply. To be archived at session wrap as an `owner_conversation` deliberation.

## Owner Decisions / Input

This proposal proceeds under the standing **scoped project authorization** granted in `DELIB-202667193` (`PAUTH-GTKB-SKILL-RENAME-REFERENCE-SWEEP-…`), which authorizes the sweep slices to proceed autonomously without per-slice owner approval. Per-slice Loyal Opposition GO + VERIFIED and all safety gates remain required.

This session's owner AskUserQuestion decisions (session `036d7c79`, 2026-07-24) further authorize the operative approach:

- **Govern existing work** — govern the partially-done sweep changes rather than reset/redo.
- **Isolate skill-rename only** — commit only the skill-rename changes; leave WI-5640's un-GO'd file-move apply uncommitted for WI-5640's own authorization.

No further owner decision is required for this slice.

## Requirement Sufficiency

Existing requirements sufficient. The requirement is defined by the WI-5651 skill rename (bare / `kb-` → `gtkb-`) as canonicalized in `config/agent-control/gtkb-skill-rename-map.toml`, the WI-5662 backlog item, and the scoped PAUTH under `DELIB-202667193`. No new or revised requirement is needed; this slice completes reference canonicalization against the already-canonical skill directory names.

## Spec-Derived Verification Plan

The table below is the **spec-to-test mapping** — the specification-derived verification evidence required by `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. Because the functional change is documentation-reference canonicalization with no executable behavior, this specification-derived verification uses deterministic reference scans and isolation assertions rather than `pytest`:

| Linked spec / property | Verification command | Expected result |
|---|---|---|
| Functional (WI-5662 rename complete) | `grep -rhoE "\.(claude\|codex)/skills/[a-z0-9_-]+" .claude/skills/gtkb-bridge/SKILL.md .claude/skills/gtkb-proposal-review/SKILL.md .claude/skills/gtkb-verify/SKILL.md \| grep -vE "/gtkb-"` (post-commit) | empty — zero residual bare / `kb-` skill-dir refs |
| Isolation — exclude WI-5640 | `git show <isolate-commit> -- .claude/skills/gtkb-bridge/SKILL.md \| grep "config/agent-control/gtkb-"` | empty — no WI-5640 file-move line committed |
| Isolation — preserve WI-5640 | `git diff -- .claude/skills/gtkb-bridge/SKILL.md \| grep "config/agent-control/gtkb-"` (post-commit) | non-empty — WI-5640 file-move lines preserved unstaged |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5662-skill-rename-canonical-doc-refs` | `preflight_passed: true`, `missing_required_specs: []` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5662-skill-rename-canonical-doc-refs` | exit 0, Blocking gaps: 0 |

The functional change is documentation-reference canonicalization with no executable behavior; verification is the deterministic residual-ref scan plus the two isolation assertions (the committed diff contains no file-move line; the working tree still carries the file-move lines unstaged).

## Risk / Rollback

**Risk.** The only non-trivial risk is the line-level staging for `gtkb-bridge/SKILL.md` accidentally staging a WI-5640 file-move line into the skill-rename commit. Mitigation: the isolate patch is dry-run-validated with `git apply --check --cached` before staging, and the post-commit isolation assertions above fail verification if any `config/agent-control/gtkb-` line entered the commit. The other two docs are unmodified at HEAD, so their commits are plain path-scoped and carry no isolation risk.

**Rollback.** Single scoped commit. `git revert <isolate-commit>` (or `git reset --soft HEAD~1` before push) fully undoes the slice; the working-tree WI-5640 file-move changes are untouched because they were never staged.

## Cross-Harness Disposition

This slice modifies canonical Claude harness skill documentation (`.claude/skills/*/SKILL.md`), a harness-surface path. Per `ADR-CROSS-HARNESS-PARITY-001` (Q8) and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`:

- **Claude Code (harness B) — in scope, behavioral parity established.** The three canonical `SKILL.md` docs are the source of truth; their stale skill-dir references are canonicalized to `gtkb-` form by this slice.
- **Codex (harness A) — behavioral parity by generation.** The `.codex/skills/*` adapters are mechanically generated from the canonical `.claude/skills/*` sources via `scripts/generate_codex_skill_adapters.py`; they are not hand-maintained. This slice deliberately does NOT edit `.codex/skills/*` (they are not in `target_paths`). Codex parity is restored by regenerating the adapters in the dependency-linked sibling slice **WI-5663 (S2)**.
- **Other registered harnesses (Antigravity C, Cursor E, Ollama D, OpenRouter F, Goose G, Alibaba H) — same generated-adapter model;** parity is restored by the same S2 regeneration from the corrected canonical sources.
- **Sequencing is owner-approved, not an unmanaged break.** The S1→S2 order — fix canonical sources first, regenerate adapters second — is the explicit owner decision in `DELIB-202667193` (decision 3: "regenerate adapters ONLY after the canonical `.claude/skills` sources are fixed, or the stale text re-propagates into the generated adapters"). The transient adapter lag between the S1 commit and S2 regeneration does not worsen cross-harness state: the generated adapters already carry the same stale references pre-S1, so this slice strictly improves the canonical source while queuing the adapters for the sequenced S2 regeneration.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered bridge file for `gtkb-wi5662-skill-rename-canonical-doc-refs`; no prior version is deleted or rewritten (append-only). Dispatcher/TAFE state plus the numbered file chain are the live workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`docs` — all three target files are `SKILL.md` documentation; the change canonicalizes stale skill-directory references in prose and command examples. No source, test, or config behavior changes (the helper resolver code fixes are scoped to WI-5660, not this slice).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
