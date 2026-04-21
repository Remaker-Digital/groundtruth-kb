NEW

# Agent Red — Claude Design GUI-Refresh Intake (scope bridge)

**Status:** NEW
**Author:** Prime Builder (Opus 4.7)
**Date:** 2026-04-18 (S302)
**Category:** Scope bridge — exploration + process design only; NOT an implementation bridge
**Owner trigger:** 2026-04-17 backlog addition in `memory/work_list.md`; 2026-04-18 Option A decision in S302
**Parallel work:** E1 Apply `-013 REVISED` awaiting Codex verification (independent; this bridge is filed pulled-forward-just-enough per owner decision to capture first real handoff while fresh)

## Claim

Agent Red should formalize how Claude Design (`claude.ai/design`) handoffs enter the Prime/Codex governance pipeline, using the 2026-04-18 `AR-Widget-handoff.zip` as the first worked example. This bridge requests Codex review of the intake **scope**; it does not propose, authorize, or schedule any UI implementation.

## Why Now (and Why Not Later)

The owner used Claude Design to generate a widget redesign handoff on 2026-04-18 and tested the Claude-Design → coding-agent workflow by uploading the zip to this session for inspection. The inspection is complete (file list, stack/content/feature delta documented). Owner Option A decision: pull the `agent-red-claude-design-gui-refresh-intake` workstream forward just enough to capture this handoff as the worked example before memory degrades.

Rationale ranking: (1) the handoff format + my observations are fresh; (2) this is concretely cheaper than redefining the format next time; (3) the bridge does not block any Tier 1 work (A1/B1/C1 remain queued per `memory/work_list.md`); (4) per `.claude/rules/codex-review-gate.md`, filing a bridge proposal is explicitly NOT an implementation act.

## Scope (in)

1. **Define the Claude Design handoff packet format** — based on the 2026-04-18 zip's observed structure.
2. **Define the intake triage procedure** — how Prime Builder classifies incoming handoffs (design-token-only / per-feature / full-redesign) and routes them to appropriate per-feature implementation bridges.
3. **Define the design-token extraction protocol** — how the CSS custom-property system in handoffs maps to Agent Red's Preact/TypeScript theme layer without porting JSX.
4. **Define the feature-to-spec pipeline** — for net-new UX features introduced by a handoff, how they enter GOV-01 spec-first / GOV-09 owner-input-classification flow.
5. **Define the governance preservation contract** — which Agent Red features MUST survive any Claude-Design-driven refresh (GDPR consent, OTP/auth, multi-tenant isolation, a11y WCAG 2.1 AA, Chromatic + Pact + Vitest test surface).
6. **Define the review gate** — how Loyal Opposition reviews Claude Design output AND how owner visual review integrates.
7. **Define archival / DA registration** — how handoff artifacts become durable deliberation records so future refreshes can cite prior decisions.

## Scope (out)

1. **No UI implementation of any handoff design.** This bridge is process-design only.
2. **No production Agent Red widget changes.** No edits to `widget/src/**` beyond possible future separate bridges.
3. **No GT-KB changes.** Design-artifact registration concepts may reference GT-KB capability but any actual GT-KB changes are separate bridges.
4. **No bypass of Prime/Codex bridge review for any future Claude-Design-derived work.** Claude Design output becomes binding only after export → GT-KB (eventual) → bridge review → visual/a11y verification.
5. **No merge of `e1-apply` to `develop`.** Separate from this bridge.
6. **No retroactive reclassification of the 2026-04-18 handoff as implementation-ready.** It is reference material for the process, not production input.

## Worked Example — 2026-04-18 `AR-Widget-handoff.zip`

### Source

`C:\Users\micha\OneDrive\Desktop\AR-Widget-handoff.zip` (41 KB, 10 files, sha256 pending capture if owner wants git-preserved copy). Uploaded to S302 by owner on 2026-04-18 as a Claude Design workflow test.

### Contents

| Path | Size | Purpose |
|---|---|---|
| `ar-widget/README.md` | 1.6 KB | Claude Design's instructions to receiving coding agents |
| `ar-widget/project/index.html` | 1.9 KB | Host page; React 18 UMD + Babel standalone + `window.TWEAK_DEFAULTS` |
| `ar-widget/project/host.jsx` | 3.2 KB | Demo **Ember Studio** product page (non-Agent-Red brand) |
| `ar-widget/project/widget.jsx` | 13.6 KB | Main widget: teaser, trigger, chat, history, menu, rich card, rating, handoff |
| `ar-widget/project/app.jsx` | 3.0 KB | Root w/ tweak state + postMessage edit-mode protocol to parent frame |
| `ar-widget/project/bubbles.jsx` | 4.0 KB | Message-bubble variants |
| `ar-widget/project/tweaks.jsx` | 3.0 KB | Tweak-controls panel (accent/header/bubble/theme/density/size) |
| `ar-widget/project/icons.jsx` | 5.3 KB | Icon set |
| `ar-widget/project/styles.css` | 23.3 KB | Design-token system + full visual styles |
| `ar-widget/project/uploads/pasted-1776527585079-0.png` | 22 KB | User-pasted reference screenshot |

### Handoff README key guidance (quoted)

> "The design medium is **HTML/CSS/JS** — these are prototypes, not production code. Your job is to **recreate them pixel-perfectly** in whatever technology makes sense for the target codebase (React, Vue, native, whatever fits). Match the visual output; don't copy the prototype's internal structure unless it happens to fit."

> "**Don't render these files in a browser or take screenshots unless the user asks you to.** Everything you need — dimensions, colors, layout rules — is spelled out in the source."

**Implication for process design:** Claude Design's contract is *design intent, not code*. Treating JSX as authoritative would be a category error. Authoritative artifacts are: (a) CSS tokens, (b) visual output, (c) UX flow. Our intake process must reflect this.

### Stack delta — handoff vs current Agent Red widget

| | Handoff (JSX prototype) | Current `widget/` |
|---|---|---|
| Framework | React 18 UMD + Babel runtime JSX | Preact 10 + TypeScript strict |
| Build | none (runtime Babel) | Vite 6 + `tsc --noEmit` |
| Tests | none | Vitest + Testing Library + Pact contracts |
| Visual regression | none | Chromatic + Storybook 8 + axe-core a11y CI |
| Component count | ~6 in 4 JSX files | 17 components in 5,659 lines (`Panel.tsx` alone = 1,190) |
| LLM call | direct `window.claude.complete()` client-side | server-routed, spec-governed |
| Theming | CSS custom props via `data-*` on `:root` | current theme layer (to be audited) |
| Tenant isolation | none | multi-tenant architecture |
| Accessibility | basic `aria-label` | axe-core CI + Storybook a11y addon + keyboard-nav specs |
| Auth/consent | none | `ConsentBanner`, `OtpVerification`, `PhoneOtpVerification`, `PreChatForm` |

### Content delta

Demo brand in the handoff is **Ember Studio / Ember ONE headphones $349** — not Agent Red. All copy/imagery is generic placeholder. Any adopted element must undergo Agent Red content swap.

### Features in handoff but NOT current widget (= proposals if adopted, each = its own future spec+WI+bridge)

1. Persistent teaser bubble with dismiss + unread badge on trigger
2. Conversation history view (lists 3 prior chats with timestamps)
3. Header menu dropdown (mute / email chat / end chat)
4. Rich product card inserted mid-conversation
5. Handoff-to-human flow with agent-name/avatar swap
6. End-chat rating card
7. Per-message thumb up/down reactions with toggle
8. Tweak-controls panel: 6 accent colors, 4 bubble shapes, dark/light, 3 density, 3 size

### Features in current widget but NOT handoff (= MUST preserve per governance)

1. `ConsentBanner.tsx` (GDPR)
2. `OtpVerification.tsx` + `PhoneOtpVerification.tsx` (auth)
3. `PreChatForm.tsx` (identity collection)
4. `OfflineForm.tsx` (fallback)
5. `IssueReport.tsx`
6. `QuickActions.tsx` + `AnswerBlocks.tsx` (structured responses)
7. Multi-tenant isolation + SPA Control Plane governance (18 verified specs)
8. WCAG 2.1 AA (axe-core CI gate)
9. Pact backend contracts

### Design-token system worth extracting (the reusable part)

`styles.css` `:root` block (lines 6–68) defines a clean token system:

- Accent family: `--accent`, `--accent-600`, `--accent-50`, `--accent-contrast` (+ 6 preset palettes via `[data-accent="coral|indigo|emerald|amber|pink|violet"]`)
- Surface family (dark default): `--w-bg`, `--w-surface`, `--w-surface-2`, `--w-border`, `--w-border-strong`, `--w-text`, `--w-text-dim`, `--w-text-faint`
- Surface family (light override): `[data-theme="light"]` block
- Bubble family: `--w-bubble-agent`, `--w-bubble-user`, `--w-bubble-user-text`; 4 shape presets via `[data-bubble="rounded|squared|tailed|ios"]`
- Density: 2 presets via `[data-density="compact|comfortable"]`
- Size: 3 presets via `[data-size="small|medium|large"]`
- Shadow + radius: `--radius-bubble`, `--radius-widget`, `--shadow-widget`

This is **pattern-matched**, **adoptable as-is** into Agent Red's theme layer, and **risk-low** — it's data-driven via HTML attributes, no component restructuring required.

### Edit-mode protocol (Claude Design bidirectional contract)

`index.html` contains `/*EDITMODE-BEGIN*/...TWEAK_DEFAULTS...{*EDITMODE-END*/}` markers. `app.jsx` implements a postMessage protocol:

- Parent → child: `{type:"__activate_edit_mode"}` / `{type:"__deactivate_edit_mode"}`
- Child → parent: `{type:"__edit_mode_available"}` / `{type:"__edit_mode_set_keys", edits:{...}}`

This means Claude Design expects a **live-edit feedback loop**, not a one-shot export. If Agent Red UI work regularly round-trips through Claude Design, preserving that loop (versus a lossy "export → code → can't edit in Claude Design anymore") is itself a design-system decision worth surfacing.

## Proposed Process-Design Deliverables

### D1. Handoff packet format spec (KB type=`specification`)

A specification describing the minimum + optional contents of a Claude Design handoff bound for Agent Red. Fields include: README with agent instructions; `project/` tree with HTML/CSS/JS prototypes; optional `uploads/` for reference screenshots; optional edit-mode markers.

### D2. Intake triage decision matrix (KB type=`procedure`)

Procedure classifying incoming handoffs as:
- **Token-only adoption** (CSS tokens map cleanly; no new components) → narrow bridge per owner's Option B
- **Per-feature visual refresh** (one or more existing components get visual updates) → separate bridge per component
- **Net-new feature proposal** (handoff introduces UX behaviors not in current widget) → enters GOV-01/09 spec-first pipeline; one spec + WI + test per feature
- **Full redesign** (rare) → multi-phase workstream with explicit phase gates

### D3. Design-token extraction runbook (KB type=`procedure`)

Step-by-step: (a) extract `:root` tokens from `styles.css`; (b) map to Agent Red's theme layer with rename rules; (c) apply via `data-*` on widget root; (d) Chromatic baseline captures proving no regression.

### D4. Feature-to-spec pipeline

For each net-new feature identified in D2 triage: owner input classification per GOV-09 → spec creation per GOV-01 → WI creation per GOV-12 → test authoring per GOV-03 → backlog placement → bridge-governed implementation.

### D5. Governance preservation contract (KB type=`governance` addendum or new GOV)

Machine-checkable list of Agent Red widget invariants that MUST survive any Claude-Design-driven refresh. Candidates for invariants: `ConsentBanner` renders before any chat message, `OtpVerification` gates access where specified, axe-core CI gate passes at WCAG 2.1 AA, multi-tenant isolation tests pass, Pact contracts unchanged unless explicitly re-generated. Specific invariants to be enumerated during implementation of this bridge.

### D6. LO review gate + owner visual review

- LO reviews: handoff-packet-format compliance, intake-triage classification, governance-preservation contract coverage, evidence of visual/a11y regression tests.
- Owner visual review: required gate before any Claude-Design-derived PR merges to `develop`. Format: side-by-side Chromatic diff + manual owner sign-off.

### D7. DA registration + archival

Each handoff and its inspection analysis becomes a deliberation record (`source_type=owner_conversation` or `agent_analysis`), searchable via `search_deliberations()`. Handoff zip stays on OneDrive as source; durable record is the bridge document + DA row.

## Owner Decisions to Elicit

The following are owner-only decisions that the scope review should surface (Codex flags; owner answers; defaults in parentheses):

1. **D3 token mapping** — automatic (adopt handoff names 1:1) vs. curated (rename via Agent Red's theme vocabulary)? *Default: curated, with a rename map in D3.*
2. **D5 governance invariants** — is the 5-item candidate list above sufficient, or should we add more (e.g., tenant-configurable branding preservation, localization coverage)? *Default: start with 5, expand on discovery.*
3. **D6 owner-visual-review cadence** — per-PR (strict) or per-feature-batch (practical)? *Default: per-feature-batch with Chromatic + axe on every PR.*
4. **Token-only fast track** — may Prime file a narrow-scope `agent-red-widget-design-token-adoption-001` bridge in parallel with this intake bridge's implementation, to harvest the token system from the 2026-04-18 handoff without waiting for D1–D7? *Default: no, tokens wait for D3 runbook.*
5. **Handoff-zip preservation** — commit the zip to `bridge/artifacts/claude-design/` OR leave on OneDrive as authoritative source + bridge as durable record OR both? *Default: leave on OneDrive; bridge is the durable record. Binary artifacts in git are generally disfavored.*

## Next Steps After Codex GO (on scope)

This scope GO authorizes:

1. Filing `agent-red-claude-design-gui-refresh-intake-implementation-001.md` — the implementation bridge that delivers D1–D7 as KB artifacts (specifications, procedures, governance addendum).
2. Archiving DA rows for the 2026-04-18 handoff as the seed record per D7.
3. NO direct Agent Red widget writes.
4. NO GT-KB writes.

Implementation bridge can be filed immediately after this scope GO; it does not need to wait for E1 Apply VERIFIED.

## Codex Review Asks

1. Is the scope appropriately narrow (exploration + process design)?
2. Are the 7 proposed deliverables D1–D7 the right set, or should any be split/merged?
3. Are the 5 owner-elicited decisions the right ones to surface?
4. Should the governance preservation contract (D5) be a new GOV spec or an addendum to existing GOV-01/09?
5. Is handoff-zip preservation (owner decision #5) appropriately classified as owner-only, or should Prime decide?
6. Are there prior deliberations worth citing (e.g., from S297+ wiki-hygiene, SPA Control Plane reviews, multi-tenant widget governance)?

## Zero Direct-Write Commitments

This bridge, when GO'd, authorizes ONLY filing a sub-bridge. No source writes to `widget/`, `src/`, `tools/`, `docs/`, or any production-path files until the sub-bridge's own GO.

## Prior Deliberations

`search_deliberations()` for "Claude Design", "GUI refresh", "widget redesign", "design token adoption" — recommend Codex also search during review. My S302 searches for unrelated terms (DELIB-S300-001, DELIB-S300-002) returned empty, suggesting the DA may not have recent entries on this topic; treating this bridge as the seed record is acceptable per `.claude/rules/deliberation-protocol.md` "No prior deliberations found for [topic]" convention.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
