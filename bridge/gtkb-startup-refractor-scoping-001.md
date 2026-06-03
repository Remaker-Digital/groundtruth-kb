NEW

bridge_kind: governance_review
Document: gtkb-startup-refractor-scoping
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC
Session: 2026-06-03 interactive Prime Builder (session-stated role via `::init gtkb pb`; durable harness B is suspended/role-empty)
Recommended commit type: docs
Self-check preflights: to be run against this operative file before INDEX finalization; Codex MUST rerun both `bridge_applicability_preflight.py` and `adr_dcl_clause_preflight.py` against the live operative file and include the regenerated sections in any verdict.

author_identity: Claude Code Prime Builder (interactive, session-stated PB)
author_harness_id: B
author_session_context_id: 2026-06-03-gtkb-startup-refractor-scoping
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style, interactive session-stated PB (::init gtkb pb)

# GTKB-STARTUP-REFRACTOR-001 — Startup Consolidation Umbrella Scoping Proposal

## Source / Owner Directive

This proposal converts the Loyal Opposition advisory `STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02` (`independent-progress-assessments/CODEX-INSIGHT-DROPBOX/STARTUP-PROCEDURE-REFRACTOR-ADVISORY-2026-05-02-23-52.md`) into a governed slice plan, per the peer/advisory-loop convention that Prime converts standing advisories into scoped, reviewable bridge work. The advisory enumerated nine findings (F1–F9) and a nine-criterion backlog definition for `GTKB-STARTUP-REFRACTOR-001` ("Consolidate role startup and glossary loading").

F1 (explicit glossary loading at startup) is already **VERIFIED** via the sibling thread `gtkb-startup-refractor-glossary-load-surface` (six versions; see Prior Deliberations). This scoping proposal decomposes the **remaining** findings (F2–F9) plus one code-consolidation target discovered during 2026-06-03 scoping (SessionStart hook duplication) into reviewable slices. It authorizes no source, test, hook, configuration, or KB mutation; each slice will be its own NEW/REVISED proposal with its own `target_paths`, implementation authorization, and verification plan.

## Proposal Kind

This is a **scoping (umbrella) governance-review proposal**. It frames the work for Loyal Opposition review and decomposes it into slices. Its `target_paths` are limited to this bridge file and `bridge/INDEX.md`. `bridge_kind: governance_review` is self-declared for exemption from `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` (scoping/umbrella artifact, not implementation-targeting).

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § "Mandatory Owner Decisions / Input Section Gate". This proposal depends on owner approval (it is filed under an interactive PB session, not a durable PB harness) and cites the AUQ-only enforcement rule.

1. **Owner AskUserQuestion (2026-06-03)** — "How should I proceed [given B is suspended]?" → Owner selected **"Run this session as Prime Builder"**, then activated the session-stated PB role via the canonical init keyword `::init gtkb pb` (ephemeral marker `.claude/session/active-session-role.json`, `source: init_keyword`, confirmed). This authorizes Prime Builder operation for this session per `GOV-SESSION-ROLE-AUTHORITY-001` + `DCL-SESSION-ROLE-RESOLUTION-001`.
2. **Owner AskUserQuestion (2026-06-03)** — "Which PB focus?" → Owner selected **"GTKB-STARTUP-REFRACTOR-001 (P1)"**.
3. **Owner AskUserQuestion (2026-06-03)** — "What should the first slice be?" → Owner selected **"Scoping proposal first"** (decompose F2–F9 into a slice plan; no code yet).

The AUQ answers authorize filing of THIS scoping proposal only. Per-slice implementation work requires per-slice proposals and per-slice owner-approval evidence as the slices land.

Downstream owner decisions deferred to future AUQs (not asked here):

- **F3 archive-path retention** — whether to retain any legacy-archive read allowance in machine-local settings for manual recovery (advisory F3 marks this "possibly yes").
- **F5 Loyal Opposition bridge-processing authority** — the single clarifying approval reconciling `CODEX-STANDING-PRIORITIES.md` (no separate approval needed) vs `AGENTS.md`/startup-service (ask-before-processing).
- **F9 deletion** — deletion (vs archive/classify-only) of retired startup/control surfaces.
- **Glossary term-by-term review** — the advisory's one-term-at-a-time owner approval workflow is a separate owner-driven track, not a slice in this umbrella.

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` § "Mandatory Specification Linkage Gate".

- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the bridge protocol used to file this scoping proposal and its slices.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — this proposal self-declares `bridge_kind: governance_review` for the scoping/umbrella exemption.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal's linkage compliance (shown here); it authorizes no implementation, so per-slice linkage lands per-slice.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — per-slice verification compliance; this scoping proposal's verification is structural (see § Specification-Derived Verification Plan).
- `GOV-SESSION-SELF-INITIALIZATION-001` — governs the fresh-session self-initialization/startup-disclosure experience that Slices A/C/E reshape.
- `DCL-SESSION-STARTUP-TOKEN-BUDGET-001` — startup token-budget constraint motivating F4 de-duplication (Slice C) and the role-overlay split.
- `GOV-SESSION-ROLE-AUTHORITY-001` — durable vs session-stated role authority; the SessionStart hooks (Slice D) implement its resolution; unchanged by this work.
- `DCL-SESSION-ROLE-RESOLUTION-001` — deterministic role-resolution table the SessionStart hooks consume; Slice D must preserve it byte-for-byte in behavior.
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` and `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` — init-keyword parsing/assertion implemented in the twin SessionStart hooks; Slice D's shared-module extraction must preserve them.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Slice D (hook de-dup) must preserve Claude/Codex SessionStart parity; the existing parity tests are the contract.
- `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` — govern Slice C protected-narrative rewrites (CLAUDE.md / AGENTS.md repoints) via per-artifact formal-artifact-approval packets.
- `GOV-STANDING-BACKLOG-001` — governs the sub-WI decomposition recorded under `PROJECT-GTKB-STARTUP-REFRACTOR-001`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — blocking. All artifacts produced or modified by this proposal and its slices reside in-root under `E:\GT-KB`; this scoping proposal's `target_paths` (the bridge file and `bridge/INDEX.md`) are in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory. The refactor is a durable multi-artifact landing (control-map, manifest, overlays, narrative repoints, hook module, doctor checks), not a single code change.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory. Artifact-oriented stance applies across the slices.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory. The proposal names done (F1), remaining (F2–F9), discovered (hook de-dup), and deferred (F9 deletion, glossary review) lifecycle states with appropriate transition language.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md` § "Prime Builder — Before Proposing". Deliberation Archive searched for prior startup-refactor, glossary-load, and startup-disclosure reviews.

- `DELIB-2743` — Compressed bridge thread `gtkb-startup-refractor-glossary-load-surface` (6 versions, VERIFIED): the F1 glossary-load slice already landed. This proposal explicitly does not re-do it.
- `DELIB-2327` — Loyal Opposition Verification (VERIFIED) of the glossary-load surface.
- `DELIB-2328` — Loyal Opposition Review (GO) of the glossary-load surface.
- `DELIB-2329` — Loyal Opposition Review (NO-GO) of the glossary-load surface (the revision history feeding the VERIFIED).
- `DELIB-2078` — Owner approval for the init-keyword startup-disclosure relay specification; informs Slice D (hooks) and Slice C (overlay/index) so the disclosure-relay contract is preserved.
- `DELIB-1081` — Startup First-Response Directive Repair; historical context for the generated startup service that Slices A/C/E touch.

_No prior deliberation rejects the consolidation taxonomy proposed here; the F1 slice's VERIFIED history is the precedent that this umbrella continues._

## Requirement Sufficiency

**New or revised requirement required before implementation.**

Rationale: this scoping proposal authorizes only the decomposition. Several slices *create* governing artifacts (Slice A: a role-neutral startup-control map + role-capability manifest; Slice C: role overlays + a startup index) or *amend protected narrative* (Slice C). Those per-slice proposals will capture or cite the governing requirements (the advisory's nine acceptance criteria are the candidate requirement surface) and obtain per-slice owner-approval evidence before any source/narrative/KB mutation.

## target_paths

This scoping proposal authorizes only:

- `bridge/gtkb-startup-refractor-scoping-001.md` (this file)
- `bridge/INDEX.md` (entry insertion via the serialized `gt bridge index` path)

No source files. No test files. No hook files. No rule/narrative files. No spec inserts. Per-slice proposals declare their own `target_paths` matching their authorization scope. Post-GO, the sub-WI decomposition (below) is recorded under `PROJECT-GTKB-STARTUP-REFRACTOR-001` via its own implementation-start packet derived from this GO.

## Specification-Derived Verification Plan (for this scoping proposal)

Verification of this scoping proposal is structural — there is no runtime behavior to test. This umbrella defines no spec-to-test mapping of its own (no code lands in this thread); each per-slice proposal carries its own spec-to-test mapping with `python -m pytest` and `ruff` command evidence and observed results. Codex verification of this scoping artifact checks:

1. **F1 already-done claim accuracy** — confirm `gtkb-startup-refractor-glossary-load-surface` is VERIFIED and that `scripts/startup_glossary_load.py` + its `session_self_initialization.py` integration exist, so no slice re-does F1.
2. **Finding-to-slice coverage** — confirm every remaining advisory finding (F2, F3, F4, F5, F6, F7, F8, F9) maps to exactly one slice or a named deferred follow-on, with none dropped.
3. **Slice decomposition coherence** — confirm each slice has a stated goal, target surfaces, risk/gating, and dependency ordering; confirm no two slices silently overlap the same source files.
4. **Owner Decisions / Input substance** — confirm the section enumerates the three AUQ answers authorizing this scope and the deferred-AUQ list.
5. **Prior Deliberations substantiveness** — confirm real DELIB-IDs (not placeholders) and that the F1 VERIFIED precedent is cited.
6. **Applicability preflight** — Codex MUST run `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-startup-refractor-scoping` and include the `Applicability Preflight` section; `missing_required_specs: []` expected.
7. **Clause applicability preflight** — Codex MUST run `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-startup-refractor-scoping` (without `--report-only`) and include the `Clause Applicability` section; treat exit 5 as a NO-GO blocker absent an explicit owner-waiver line.

Per-slice spec-to-test verification plans (with `python -m pytest` / `ruff` evidence) land with per-slice proposals.

## Project Decomposition (Proposed Slices)

Recommended order: A → B → E → C → D (low-risk/foundational and security first; protected-narrative repoints next; highest-blast-radius hook de-dup last). Each becomes a sub-WI under `PROJECT-GTKB-STARTUP-REFRACTOR-001` after GO.

### Slice A — Startup-control inventory + role-capability manifest (covers F2 + F8 + F9-classify) — P1

**Goal**: one role-neutral source-of-truth inventory of startup control surfaces, ending the contradiction between `config/agent-control/CONTROL-MAP.md`, `REVIEW-MODE-SETUP.md`, and the live startup set.

**Surfaces (new/additive)**: a `SESSION-STARTUP-CONTROL-MAP` listing required startup files, role overlays, the generated startup service, live settings files, skills/commands/agents, plugin/MCP assumptions, and known local-only surfaces; a role-capability manifest (PB / LO / shared / owner-gated skills, agents, commands, plugin assumptions, verification command per capability); classification of stale/retired surfaces as active/deprecated/archive/generated (classify-only; no deletion).

**Risk/gating**: additive documentation + classification; low blast radius; foundational for later slices. No owner decision for classification.

### Slice B — Machine-local settings hygiene (covers F3) — P1

**Goal**: remove obsolete/destructive/credential-bearing allowances from `.claude/settings.local.json`.

**Scope**: remove the legacy archive-path read/`rm`/`rmdir` allowances prohibited by `.claude/rules/project-root-boundary.md`; remove any literal credential-bearing command allowance; separate Prime Builder write permissions from Loyal Opposition review permissions; add a sanitized tracked baseline or a doctor check for local settings.

**Risk/gating**: security-relevant; owner decision required only for any deliberate archive-path retention (deferred AUQ above). Credential lifecycle/rotation itself is owner territory and out of scope.

### Slice C — Role-neutral startup index + role overlays (covers F4 + F7) — P2

**Goal**: collapse duplicated startup content into a short role-neutral index plus compact Prime Builder and Loyal Opposition overlays; repoint `CLAUDE.md`, `AGENTS.md`, and the generated startup payload to the index instead of restating the procedure.

**Surfaces**: new `SESSION-STARTUP-INDEX` + PB/LO overlay artifacts; edits to `CLAUDE.md` and `AGENTS.md` (protected narrative → per-artifact formal-artifact-approval packets); `scripts/session_self_initialization.py` payload references.

**Risk/gating**: touches protected narrative; each protected file needs an approval packet; preserves the init-keyword disclosure-relay contract (`DELIB-2078`, `GOV-SESSION-SELF-INITIALIZATION-001`).

### Slice D — SessionStart hook de-duplication (discovered 2026-06-03) — P2

**Goal**: extract the ~250 character-identical lines shared by `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` (StartupDecision enum, role-set resolution, ephemeral-marker lifecycle, dispatch-context templates) into one shared stdlib-light module, leaving thin per-harness wrappers; convert the byte-identity parity tests into "wrapper imports shared module" assertions.

**Risk/gating**: highest blast radius (every session start); must preserve the stdlib-light/fast-import property that motivated the original duplication, plus `ADR-CODEX-HOOK-PARITY-FALLBACK-001` parity, `DCL-SESSION-ROLE-RESOLUTION-001`, and the init-keyword contracts. Sequenced last, after the recently-VERIFIED active-status-capability-gate work in this same hook area settles, to avoid collision.

### Slice E — Loyal Opposition startup text + authority fixes (covers F5 + F6) — P2

**Goal**: make the generated session-focus wording role-conditional (F6: PB waits for focus selection; LO uses the next owner message / actionable bridge queue), and resolve the LO bridge-processing authority contradiction (F5) between `CODEX-STANDING-PRIORITIES.md` and `AGENTS.md`/startup-service.

**Surfaces**: `scripts/session_self_initialization.py` (role-conditional wording) and the conflicting authority docs.

**Risk/gating**: small targeted edits; F5 needs the single owner clarifying approval (deferred AUQ above).

### Deferred follow-ons (not slices in this umbrella)

- **F9 deletion** — removal (vs archive) of classified stale surfaces, owner-gated after Slice A classification.
- **Glossary term-by-term review** — the advisory's one-term-at-a-time owner-approval workflow, a separate owner-driven track.

## Risk & Rollback

This scoping proposal carries no implementation risk: it authorizes only the bridge file write + `bridge/INDEX.md` entry insertion. Bridge-protocol rollback is "supersede in the next version" (append-only). Per-slice risk and rollback land with per-slice proposals.

## Out of Scope

- Any source, test, hook, configuration, deployment, or KB mutation other than this bridge file + `bridge/INDEX.md`. All such work lands in per-slice proposals.
- Re-doing F1 (glossary load), which is VERIFIED.
- The glossary content review (term-by-term), which is a separate owner-driven track.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
