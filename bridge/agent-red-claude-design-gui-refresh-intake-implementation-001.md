NEW

# Agent Red — Claude Design GUI-Refresh Intake Implementation Bridge

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S302)
**Parent scope bridge:** `bridge/agent-red-claude-design-gui-refresh-intake-001.md` (NEW)
**Scope GO:** `bridge/agent-red-claude-design-gui-refresh-intake-002.md` (GO with 6 required conditions)
**Category:** Implementation bridge — delivers D1–D7 as KB artifacts + DA procedure. NO widget/source writes, NO GT-KB writes.

## Claim

Create the seven deliverables defined by the scope bridge (§Proposed Process-Design Deliverables D1–D7) as Knowledge Database artifacts and a Deliberation Archive registration procedure. Scope is strictly additive to the KB and one new DA procedure script; no edits to `widget/`, `src/`, GT-KB, or any production code path.

## Explicit Non-Scope (Codex Condition 1)

**No widget or source implementation of any kind.** This bridge does not propose, authorize, schedule, or pre-approve any changes to:

- `widget/src/**` (Preact components, theme layer, routing, state)
- `widget/package.json` or build configuration
- `src/**` (backend)
- `docs/**` (beyond the KB documents D1–D7 explicitly create)
- `.github/workflows/**` (including Chromatic — addressed in D6 as a future work item, not this bridge's scope)
- Any GT-KB source or templates
- The `e1-apply` worktree branch
- Main Agent Red `develop` branch content outside the bridge/DA surfaces

**Nothing in this bridge, if GO'd, authorizes binding visual, UX, or behavioral changes to the Agent Red widget.** Every subsequent per-feature or design-token bridge retains full Prime/Codex review per `.claude/rules/codex-review-gate.md`.

## Response to Scope-GO Required Conditions

Discharging each of the 6 conditions from `-002`:

### C1 — No widget/source implementation in this bridge

Stated above in §Explicit Non-Scope.

### C2 — DA writes gated by this bridge's own GO (fixes scope-bridge F1 wording)

The scope bridge `-001` §Next Steps wording was ambiguous (stated DA archival was authorized by the scope GO). **Correction:** no DA write occurs on the scope GO. The DA registration procedure (D7) is designed + implemented by this bridge. The first DA insertion (for the 2026-04-18 handoff seed record) happens only after this impl bridge itself achieves GO + implementation + post-impl VERIFIED. Every D1–D7 artifact is gated by this bridge.

### C3 — Correct current-state counts (distinguish source vs Storybook)

Live counts as of 2026-04-18 on `develop @ 34905dc3`:

```
$ ls widget/src/components/*.tsx | wc -l
17                                     (total .tsx files)

$ ls widget/src/components/*.stories.tsx | wc -l
2                                      (Storybook story files: MessageBubble.stories.tsx, MessageList.stories.tsx)

$ ls widget/src/components/*.tsx | grep -v stories | wc -l
15                                     (source components)

$ wc -l widget/src/components/Panel.tsx
1190                                   (Panel.tsx, on develop @ 34905dc3)
```

**Note on Panel.tsx discrepancy:** Codex review reported 1088 lines; my local `wc -l` on develop reports 1190. Possible explanation: Codex may have inspected `main` (older) or a different tree state. Both values will be refreshed at D1 implementation time with the commit SHA captured in the spec text.

**Source component list (15 files):** AnswerBlocks, ChatRating, ConsentBanner, Header, InputBar, IssueReport, Launcher, MessageBubble, MessageList, OfflineForm, OtpVerification, Panel, PhoneOtpVerification, PreChatForm, QuickActions.

### C4 — Add 6th owner decision on edit-mode roundtrip preservation

See §Owner Decisions to Elicit, item 6 below.

### C5 — Cite related DELIB-0200, DELIB-0368, DELIB-0463

See §Prior Deliberations below.

### C6 — Pre-merge visual review artifact path

See §D6 — now includes explicit pre-merge artifact options (not the current post-merge-only Chromatic workflow).

## Deliverables

Each of D1–D7 is a KB artifact or procedure script. Listed with target KB type, estimated size, and acceptance criteria.

### D1 — Handoff Packet Format Spec

**KB type:** `specification` (type='protocol')
**Working title:** `SPEC-CD-HANDOFF-FORMAT-001 — Claude Design Handoff Packet Format`
**Acceptance criteria:**

- Documents the mandatory contents of a Claude Design handoff: `{root}/README.md` with receiving-agent instructions, `{root}/project/` subdirectory, mandatory file types (HTML entry + CSS + at least one JSX/component), optional `uploads/` for reference images, optional edit-mode markers.
- Lists the five Claude Design observables captured from the 2026-04-18 worked example: React UMD + Babel runtime, design-token system in `:root`, `data-*` attribute-driven theming, `postMessage` edit-mode protocol, inline demo-brand placeholder copy.
- Includes at least one machine-checkable assertion: "if an incoming zip claims to be a Claude Design handoff, it MUST contain `README.md` + `project/index.html` at minimum."
- Does NOT prescribe handoff naming convention or archival path (those are owner-decided per D7).

### D2 — Intake Triage Decision Matrix

**KB type:** `procedure`
**Working title:** `PROC-CD-INTAKE-TRIAGE-001 — Claude Design Handoff Triage`
**Acceptance criteria:**

- Defines the 4 triage outcomes: (a) Token-only adoption, (b) Per-feature visual refresh, (c) Net-new feature proposal, (d) Full redesign (rare).
- For each outcome: entry signals, required artifacts, routing destination, Prime vs owner decision boundaries.
- (a) routes to a narrow `agent-red-widget-design-token-adoption-NNN` bridge; (b) routes to per-component visual-refresh bridges; (c) routes to GOV-01/GOV-09 spec-first pipeline (one spec + WI + test per new feature); (d) routes to multi-phase workstream.
- Includes the 2026-04-18 handoff as worked example: classifies as **(a) Token-only adoption candidate + (c) Net-new feature proposals** (design tokens are cleanly adoptable; teaser/history/menu/rich-card/reactions/rating are net-new features each requiring own spec).

### D3 — Design-Token Extraction Runbook

**KB type:** `procedure`
**Working title:** `PROC-CD-TOKEN-EXTRACTION-001 — Design Token Extraction from Claude Design`
**Acceptance criteria:**

- 4-step runbook: (1) extract `:root` tokens from handoff `styles.css`; (2) map to Agent Red theme layer via rename rules (owner decision: auto-adopt vs curated — default curated); (3) apply via `data-*` on widget root; (4) Chromatic baseline diff proves no existing-flow regressions.
- Includes the token catalog extracted from the 2026-04-18 worked example as an appendix (accent family, surface family dark+light, bubble shape map, density map, size map, shadow + radius).
- Explicit guard: tokens adopted via this runbook do NOT imply any component or behavior change. Only CSS custom property values are updated.
- Explicit guard: the runbook produces a proposal, not a PR. Every token adoption still passes through a bridge before merge.

### D4 — Feature-to-Spec Pipeline Procedure

**KB type:** `procedure`
**Working title:** `PROC-CD-FEATURE-TO-SPEC-001 — Claude Design Feature to Spec Pipeline`
**Acceptance criteria:**

- Defines the flow: owner classifies feature (GOV-09) → Prime creates spec + WI (GOV-01 + GOV-12) → Prime creates test per GOV-03 → WI enters backlog → backlog prioritization → implementation bridge.
- Special-cases Claude Design: the "owner input classification" step for Claude Design features is triggered by the handoff triage (D2), not by a direct owner prompt. Prime may file the spec with owner review.
- Includes 6 new-feature candidates identified from the 2026-04-18 worked example (teaser, history, menu, rich card, reactions, rating, handoff-to-human, tweaks panel) as pre-filled input-classification rows; actual spec creation waits for explicit owner approval per feature.
- Defines rollback: if a feature spec is rejected post-implementation, the runbook points back to the bridge + KB for retroactive un-wiring.

### D5 — NEW Topic-Specific Governance Artifact (per Codex F2)

**KB type:** `governance` (type='protected_behavior')
**Working title:** `GOV-CD-PRESERVATION — Claude Design Refresh Preservation Contract`
**Acceptance criteria:**

- **NEW topic-specific governance artifact**, cross-linked to (not modifying) GOV-01, GOV-09, GOV-12. Codex F2 explicit preference recorded here.
- Enumerates machine-checkable invariants that MUST survive any Claude-Design-driven refresh. Initial candidate set (to be refined during implementation):
  - **I1** ConsentBanner renders before any chat message post-init (tenant-configurable; test: `tests/widget/test_widget_consent_ordering.py`).
  - **I2** OTP-gated flows require both email and phone verification where specified (multi-tenant-aware; tests: `tests/unit/test_widget_otp_verification.py`, `tests/chat/test_identity_preprocessor.py`).
  - **I3** axe-core CI gate passes at WCAG 2.1 AA (`.github/workflows/accessibility.yml`).
  - **I4** Tenant isolation preserved (transport layer tenant check tests: `tests/flows/test_flow_auth_boundaries.py`).
  - **I5** Pact contracts unchanged unless explicitly re-generated with Pact broker publish (existing CI).
  - **I6** Widget builds clean under `tsc --noEmit` + Vite build (strict TS).
- Each invariant has a protected-behavior assertion per GOV-20 DCL pattern (machine-checkable).
- Sets precedent: future per-feature Claude Design refresh bridges MUST cite this artifact and show how the refresh satisfies each invariant (or propose an explicit owner-ratified exception).

### D6 — Review Gate + Pre-Merge Visual Artifact Path (fixes scope F4)

**KB type:** `procedure` (nested under D5 or stand-alone per Codex review)
**Working title:** `PROC-CD-REVIEW-GATE-001 — Claude Design Refresh Review Gate`
**Acceptance criteria:**

- **LO review:** handoff-packet-format compliance (D1), intake-triage classification (D2), governance-preservation contract coverage (D5).
- **Pre-merge visual artifact path (addresses Codex F4):** Codex noted Chromatic is currently **push-only on `develop` = post-merge baseline capture, not pre-merge gate** (`.github/workflows/chromatic.yml`). D6 must therefore define a pre-merge artifact path that does NOT rely on current Chromatic alone. Proposed options (to be selected at implementation time, owner decides):
  - **Option D6-a:** Storybook static build artifact attached to every Claude-Design-derived PR (via a new pre-merge workflow step). Reviewer downloads, inspects in browser.
  - **Option D6-b:** Local before/after screenshots captured by the bridge author, inlined into the bridge document (evidence section).
  - **Option D6-c:** Chromatic PR-build link (requires upgrading the Chromatic workflow to run on PR branches, not just develop — separate bridge).
  - **Option D6-d:** Explicit side-by-side review gallery HTML published as PR artifact.
  - **Option D6-e (recommended):** Combination of D6-a + D6-b as minimum; D6-c if the Chromatic workflow is ever upgraded.
- **Owner visual review:** explicit owner sign-off gate before merge. Cadence is owner-only to decide (per scope bridge owner decision #3); Prime recommends per-feature-batch cadence with Chromatic + axe on every PR (unchanged).

### D7 — DA Registration + Archival Procedure

**KB type:** `procedure` + small script (`scripts/archive_claude_design_handoff.py`)
**Working title:** `PROC-CD-DA-ARCHIVAL-001 — Claude Design Handoff DA Registration`
**Acceptance criteria:**

- Script accepts a handoff zip path, inspection markdown, and owner metadata.
- Produces one or more DA rows per handoff: `source_type='agent_analysis'` for Prime's inspection record, `source_type='owner_conversation'` for any owner decisions captured mid-handoff.
- Includes content-hash idempotence check (do not double-insert same analysis).
- Redacts binary artifact bytes (handoff zip contents not inlined; metadata + file list + inspection observations inlined).
- Archival of the 2026-04-18 seed handoff happens as the post-impl VERIFIED step of this bridge, NOT on scope GO (fixes scope F1).
- Script is additive to `scripts/` directory; zero touches to existing DA harvest scripts.

## Owner Decisions to Elicit

Six decisions (five from scope bridge + one new per Codex C4):

1. **D3 token mapping** — automatic (adopt handoff names 1:1) vs. curated (rename via Agent Red's theme vocabulary)? *Default: curated, with a rename map in D3.*
2. **D5 governance invariant scope** — is the I1-I6 candidate set sufficient, or should we add more (e.g., tenant-configurable branding preservation, localization coverage, perf budget)? *Default: start with 6, expand on discovery.*
3. **D6 owner-visual-review cadence** — per-PR (strict) or per-feature-batch (practical)? *Default: per-feature-batch with Chromatic + axe on every PR.*
4. **Token-only fast track** — may Prime file a narrow `agent-red-widget-design-token-adoption-001` bridge in parallel with this impl bridge's VERIFIED, to harvest the token system from the 2026-04-18 handoff without waiting for all D1–D7? *Default: no, tokens wait for D3 runbook.*
5. **Handoff-zip preservation** — commit to `bridge/artifacts/claude-design/` OR leave on OneDrive as authoritative source + bridge as durable record OR both? *Default: leave on OneDrive; bridge is the durable record.*
6. **(NEW per Codex C4) Edit-mode roundtrip preservation** — is preserving Claude Design's bidirectional `postMessage` edit-mode protocol (observed in the 2026-04-18 handoff's `index.html` EDITMODE markers and `app.jsx` listener) a **product/process requirement** (Agent Red widget round-trips through Claude Design regularly, so the export → code → re-edit loop must survive) OR an **archival observation** (interesting but one-way: once code lands, the live Claude Design link is accepted as lossy)? *Default: archival observation, unless owner confirms a design-system workflow assumes continuous round-trip.*

## Pre-Merge Visual Artifact Path Recommendation (per Codex F4 / C6)

Current state: `.github/workflows/chromatic.yml` runs on push to `develop` only — it captures post-merge baselines, not pre-merge reviews. This means a Claude-Design-derived PR could theoretically merge to `develop` with no visual review.

**Prime's recommendation for Option D6-e (combination):**

- **Minimum (this bridge's own deliverable):** D6 includes a new procedure requiring bridge authors to attach local before/after screenshots (Option D6-b) OR a Storybook static build (Option D6-a) to any Claude-Design-derived PR's bridge document as inline evidence.
- **Aspirational (separate future bridge):** Upgrade the Chromatic workflow to build on PR branches (Option D6-c). Defer to future `agent-red-chromatic-pr-gate-001` bridge; NOT scoped here.
- **Fallback for specific-change reviews:** Explicit side-by-side HTML gallery (Option D6-d) attached to the bridge.

This resolves F4 without scope-creeping into CI workflow changes.

## Prior Deliberations (per Codex C5)

**No exact prior deliberations found for Claude Design GUI-refresh intake.** `search_deliberations()` on `Claude Design`, `GUI refresh`, `widget redesign`, `design token adoption`, and `Agent Red widget design tokens` returned related-but-non-exact matches (confirmed by both Prime and Codex in S302).

Related context deliberations considered per `.claude/rules/deliberation-protocol.md`:

- **DELIB-0200** (`INSIGHTS-2026-03-30-11-56-COMPETITIVE-ANALYSIS-WIDGET-AND-CHAT-QUALITY.md`) — recommends sequencing widget capability/action surface before deeper quality/fine-tuning work. **Relevance:** suggests D2 triage should weight widget capability additions (teaser, history, reactions, handoff) as a distinct category from polish features.
- **DELIB-0368** (`INSIGHTS-2026-04-01-23-29-13-S252-WIDGET-CHAT-PROPOSAL-REVIEW.md`) — rejected stale widget/chat roadmap, required current-state re-baselining. **Relevance:** reinforces Codex F3 (current-state counts must be live at spec-write time, not carried forward from memory).
- **DELIB-0463** (`INSIGHTS-2026-04-03-13-27-52-PRIME-WIDGET-AUDIT-ACTION-PLAN.md`) — established staging-backed widget audit sequence, emphasized runtime evidence. **Relevance:** D6 review-gate design should require runtime evidence (screenshots, Storybook build, or axe output) — not just static source review.

These three DELIBs confirm the shape of this bridge (staged, evidence-first, preservation-aware) rather than contradicting it. No exact prior decision on Claude Design intake requires refresh.

## Scope (explicitly enumerated)

| # | Deliverable | KB type | Artifact path (working) | Tests required |
|---|---|---|---|---|
| D1 | Handoff format spec | specification | KB `SPEC-CD-HANDOFF-FORMAT-001` | structural assertion in spec |
| D2 | Triage decision matrix | procedure | KB `PROC-CD-INTAKE-TRIAGE-001` | text reference test |
| D3 | Token extraction runbook | procedure | KB `PROC-CD-TOKEN-EXTRACTION-001` | text reference test |
| D4 | Feature-to-spec pipeline | procedure | KB `PROC-CD-FEATURE-TO-SPEC-001` | text reference test |
| D5 | Governance preservation contract | governance (protected_behavior) | KB `GOV-CD-PRESERVATION` | 6 DCL assertions (I1–I6) |
| D6 | Review gate procedure | procedure | KB `PROC-CD-REVIEW-GATE-001` | text reference test |
| D7 | DA registration procedure + script | procedure + `scripts/archive_claude_design_handoff.py` | KB `PROC-CD-DA-ARCHIVAL-001` + script file | script unit tests + idempotence test |

Total estimated effort: ~8-12 KB inserts (1 spec + 5 procedures + 1 governance artifact + 6 DCL assertions) + 1 new script (~200 lines) + ~3 test files. Single-bridge atomic commit feasible; 1-2 session-sized implementation.

## Implementation Plan (commit-sized slices)

1. **Slice A (specs + procedures):** D1 + D2 + D3 + D4 as KB inserts. Zero code.
2. **Slice B (governance):** D5 + 6 DCL assertion records + assertion-check validation. Zero code.
3. **Slice C (review gate):** D6. Zero code.
4. **Slice D (DA + script):** D7 KB procedure + `scripts/archive_claude_design_handoff.py` + unit tests. One new script file, ~200 lines.
5. **Slice E (seed record):** Archive 2026-04-18 handoff as first DA row via D7 script.

Each slice is a separate commit on `develop`. Bridge VERIFIED lands after Slice E.

## Verification Gates

On post-impl report to this bridge:

- [ ] All 7 KB artifacts inserted with correct types (1 spec, 5 procedures, 1 governance). Query `db.list_specs(type=...)` shows each.
- [ ] D5 has 6 DCL assertion records; `kb-assert` run reports I1–I6 status.
- [ ] `scripts/archive_claude_design_handoff.py` exists with tests in `tests/scripts/test_archive_claude_design_handoff.py`; `pytest` passes.
- [ ] 1 seed DA row exists for the 2026-04-18 handoff (`search_deliberations('Claude Design handoff 2026-04-18')`).
- [ ] No changes to `widget/**`, `src/**`, GT-KB, `.github/workflows/**` (confirmable via git diff stat).
- [ ] All 6 Codex conditions from `-002` are referenceable from the final artifacts (each artifact cites which condition it addresses).

## Zero Widget/GT-KB Writes

Restated for emphasis: this bridge, if GO'd, authorizes KB inserts + 1 new script + its tests. Nothing else. Any future Claude-Design-derived widget change — even as small as a token value update — is a separate bridge.

## Codex Review Asks

1. Are the 7 KB artifact types correctly chosen (1 spec, 5 procedures, 1 governance)?
2. Is the D5 invariant set I1-I6 appropriately scoped, or should any be split/merged?
3. Is the D6 pre-merge visual artifact recommendation (combination D6-a + D6-b minimum; D6-c aspirational in future bridge) acceptable?
4. Is the 5-slice implementation plan reasonable, or should any slices be merged/split?
5. Is the 2026-04-18 seed-record archival as a post-impl step the right fence (vs gated separately)?
6. Any additional invariants or cross-links Codex would add to D5?

## Requested Verdict

**GO** for filing this impl bridge's 5-slice implementation plan, OR **NO-GO** with specific findings.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
