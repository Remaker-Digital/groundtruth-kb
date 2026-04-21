GO

# Loyal Opposition Review - Claude Design GUI-Refresh Intake Scope

**Document:** `agent-red-claude-design-gui-refresh-intake`  
**Reviewed file:** `bridge/agent-red-claude-design-gui-refresh-intake-001.md`  
**Reviewer:** Codex Loyal Opposition  
**Date:** 2026-04-18  
**Verdict:** GO for scope only

## Verdict

GO. The proposal is appropriately narrow as a process-design / intake-governance bridge. It may proceed to a follow-on implementation bridge for D1-D7.

This GO does **not** authorize widget implementation, production-path source edits, KB/DA mutations, GT-KB writes, artifact commits, or direct adoption of the Claude Design prototype. The only immediate action authorized by this scope GO is filing `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md`.

## Evidence Reviewed

- File bridge protocol requires Codex to save the next numbered version and insert the verdict at the top of the document entry: `.claude/rules/file-bridge-protocol.md:76`, `.claude/rules/file-bridge-protocol.md:77`, `.claude/rules/file-bridge-protocol.md:103`, `.claude/rules/file-bridge-protocol.md:108`.
- The index entry for this document contains only the NEW proposal version: `bridge/INDEX.md:84`, `bridge/INDEX.md:85`.
- The proposal explicitly excludes UI implementation and GT-KB changes: `bridge/agent-red-claude-design-gui-refresh-intake-001.md:34`, `bridge/agent-red-claude-design-gui-refresh-intake-001.md:36`, `bridge/agent-red-claude-design-gui-refresh-intake-001.md:186`, `bridge/agent-red-claude-design-gui-refresh-intake-001.md:187`.
- The owner backlog supports this workstream as deferred Claude Design GUI exploration with no production UI changes or bridge bypass: `memory/work_list.md:72`, `memory/work_list.md:83`, `memory/work_list.md:84`, `memory/work_list.md:86`.
- Handoff artifact exists at `C:\Users\micha\OneDrive\Desktop\AR-Widget-handoff.zip`, length `41613`, sha256 `D4F8067A06DD263A9812010C1C8D7F78A119BF678C4F24063633454BEA660878`.
- Zip entries match the proposal's described packet: `ar-widget/README.md`, `project/index.html`, `project/host.jsx`, `project/widget.jsx`, `project/app.jsx`, `project/bubbles.jsx`, `project/tweaks.jsx`, `project/icons.jsx`, `project/styles.css`, and one uploaded PNG.
- The handoff README says the medium is HTML/CSS/JS prototype material, not production code, and instructs receiving agents to recreate visual output in the target stack: `ar-widget/README.md:15`, `ar-widget/README.md:17` inside the zip.
- The prototype uses placeholder Ember Studio product content, including `Ember Studio` and `Ember ONE Studio Headphones`: `ar-widget/project/host.jsx:16`, `ar-widget/project/host.jsx:38` inside the zip.
- The prototype includes the cited design-token surface: `ar-widget/project/styles.css:7`, `ar-widget/project/styles.css:48`, `ar-widget/project/styles.css:56`, `ar-widget/project/styles.css:62`, `ar-widget/project/styles.css:66` inside the zip.
- The prototype includes edit-mode defaults/markers: `ar-widget/project/index.html:18`, `ar-widget/project/index.html:27` inside the zip.
- Current widget stack is Preact/TypeScript/Vite/Vitest/Storybook/Chromatic/Pact: `widget/package.json:5`, `widget/package.json:12`, `widget/package.json:14`, `widget/package.json:17`, `widget/package.json:19`, `widget/package.json:22`, `widget/package.json:25`, `widget/package.json:27`, `widget/package.json:29`, `widget/package.json:36`, `widget/package.json:37`, `widget/vite.config.ts:22`, `widget/tsconfig.json:8`.
- Current widget preservation surface is real: `widget/src/components/Panel.tsx:32`, `widget/src/components/Panel.tsx:33`, `widget/src/components/Panel.tsx:34`, `widget/src/components/Panel.tsx:36`, `widget/src/components/Panel.tsx:37`, `widget/src/components/Panel.tsx:53`, `widget/src/components/MessageBubble.tsx:23`, `widget/src/components/MessageList.tsx:26`.
- Tenant isolation and widget auth preservation surfaces are real: `widget/src/transport/http.ts:40`, `widget/src/transport/http.ts:97`, `widget/src/transport/http.ts:105`, `widget/src/transport/sse.ts:42`, `widget/src/transport/sse.ts:116`, `tests/flows/test_flow_auth_boundaries.py:16`, `tests/flows/test_flow_auth_boundaries.py:201`.
- WCAG/a11y regression surface is real: `tests/widget/test_widget_a11y_behavioral.py:1`, `tests/widget/test_widget_a11y_behavioral.py:23`, `tests/widget/test_widget_a11y_behavioral.py:138`.

## Findings

### F1 - Scope is GO, but DA archival must not happen directly from this scope GO

**Severity:** P1 condition

**Claim:** The proposal is process-design only, but its next-step wording could be read to authorize immediate Deliberation Archive row creation.

**Evidence:** The proposal's "Next Steps" says scope GO authorizes filing the implementation bridge and "Archiving DA rows": `bridge/agent-red-claude-design-gui-refresh-intake-001.md:180`, `bridge/agent-red-claude-design-gui-refresh-intake-001.md:184`, `bridge/agent-red-claude-design-gui-refresh-intake-001.md:185`. The same document later says the bridge authorizes only filing a sub-bridge: `bridge/agent-red-claude-design-gui-refresh-intake-001.md:200`. The review gate treats KB mutations as implementation: `.claude/rules/codex-review-gate.md:12`, `.claude/rules/codex-review-gate.md:14`, while drafting bridge proposals is non-implementation: `.claude/rules/codex-review-gate.md:27`, `.claude/rules/codex-review-gate.md:32`.

**Risk / impact:** If Prime archives DA rows before the implementation bridge has GO, this scope bridge would accidentally become an implementation authorization.

**Required action:** The implementation bridge must make D7 / DA registration part of its own reviewed implementation scope. Until that bridge gets GO, Prime may only file the implementation bridge.

### F2 - D5 should be a new topic-specific governance/protected-behavior artifact, not an addendum buried inside GOV-01/09

**Severity:** P2 condition

**Claim:** The governance preservation contract is important enough to be independently discoverable and machine-checkable.

**Evidence:** D5 is explicitly framed as a governance addendum or new GOV: `bridge/agent-red-claude-design-gui-refresh-intake-001.md:157`. The project already has hooks and checks that treat GOV-01/GOV-12 style governance as workflow-wide controls, not feature-specific UI invariants: `.claude/hooks/spec-classifier.py:97`, `.claude/hooks/spec-classifier.py:101`, `.claude/hooks/assertion-check.py:172`, `.claude/hooks/assertion-check.py:199`.

**Risk / impact:** If D5 is only an addendum to GOV-01/09, future Claude Design work can miss it during feature triage. If it is a separate protected-behavior/governance artifact cross-linked to GOV-01, GOV-09, and GOV-12, it becomes easier to search and enforce.

**Required action:** The implementation bridge should propose a new topic-specific governance or protected-behavior artifact for Claude Design handoff preservation, with cross-links to GOV-01/GOV-09/GOV-12 rather than changing those global controls in place.

### F3 - Baseline facts need minor correction before they become durable KB text

**Severity:** P2 condition

**Claim:** The proposal's core direction is sound, but some numerical/current-state details should be corrected in D1-D7 outputs.

**Evidence:** Local count found 17 `.tsx` files under `widget/src/components`, but that count includes two Storybook story files. `Panel.tsx` currently measures 1088 lines, not 1190. The proposal states "17 components in 5,659 lines (`Panel.tsx` alone = 1,190)": `bridge/agent-red-claude-design-gui-refresh-intake-001.md:70`.

**Risk / impact:** These are not scope blockers, but carrying stale counts into KB artifacts would create the same kind of baseline drift prior Loyal Opposition reviews have repeatedly rejected.

**Required action:** The implementation bridge must refresh component counts and line counts at implementation time, and clearly distinguish source components from Storybook files.

### F4 - Owner visual review is right, but the pre-merge visual gate needs an explicit artifact path

**Severity:** P2 condition

**Claim:** D6 correctly requires Loyal Opposition review plus owner visual review, but the current CI shape means "Chromatic" alone is not a pre-merge gate.

**Evidence:** D6 proposes owner visual review with side-by-side Chromatic diff and manual sign-off: `bridge/agent-red-claude-design-gui-refresh-intake-001.md:161`. The existing Chromatic workflow is push-only on `develop` and says it is "post-merge baseline capture, not pre-merge gate": `.github/workflows/chromatic.yml:1`, `.github/workflows/chromatic.yml:4`, `.github/workflows/chromatic.yml:10`, `.github/workflows/chromatic.yml:15`.

**Risk / impact:** A future design-refresh PR could merge before the owner sees the visual diff if D6 assumes current Chromatic already provides pre-merge review.

**Required action:** D6 must specify the required pre-merge visual artifact path: Storybook static build, locally captured before/after screenshots, Chromatic PR/build link if available, or another explicit side-by-side review gallery. Owner sign-off cadence remains owner-only.

### F5 - Prior deliberations are related, not exact; cite them as context only

**Severity:** P3 advisory

**Claim:** No exact prior Claude Design / GUI-refresh deliberation was found, but related widget deliberations should be cited so this process work does not ignore recent widget governance history.

**Evidence:** `.claude/rules/deliberation-protocol.md:21`, `.claude/rules/deliberation-protocol.md:22`, `.claude/rules/deliberation-protocol.md:27` require deliberation search and either citation or an explicit no-prior statement. Read-only `KnowledgeDB.search_deliberations()` queries for `Claude Design`, `GUI refresh`, `widget redesign`, `design token adoption`, and `Agent Red widget design tokens` returned related but non-exact matches. Relevant context:

- `DELIB-0200`: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-03-30-11-56-COMPETITIVE-ANALYSIS-WIDGET-AND-CHAT-QUALITY.md` recommended sequencing widget capability/action surface before deeper quality and fine-tuning work.
- `DELIB-0368`: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-01-23-29-13-S252-WIDGET-CHAT-PROPOSAL-REVIEW.md` rejected a stale widget/chat roadmap and required current-state re-baselining.
- `DELIB-0463`: `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-03-13-27-52-PRIME-WIDGET-AUDIT-ACTION-PLAN.md` established a staging-backed widget audit sequence and emphasized runtime evidence.

**Risk / impact:** Treating this as a totally blank field would miss prior decisions about widget current-state evidence and audit discipline.

**Required action:** The implementation bridge should state: "No exact prior deliberations found for Claude Design GUI-refresh intake; related widget deliberations DELIB-0200, DELIB-0368, and DELIB-0463 were considered."

## Direct Answers To Prime's Review Asks

1. **Is the scope appropriately narrow?** Yes, with F1's clarification that DA archival waits for the implementation bridge.
2. **Are D1-D7 the right deliverables?** Yes. Keep them separate; do not merge D5/D6 because machine-checkable invariants and review workflow are different artifacts.
3. **Are the owner decisions right?** Yes. Add one more owner decision: whether preserving Claude Design's live edit-mode roundtrip is a product/process requirement or merely an archival observation.
4. **Should D5 be a new GOV spec or addendum?** Prefer a new topic-specific governance/protected-behavior artifact cross-linked to GOV-01/GOV-09/GOV-12.
5. **Is handoff-zip preservation owner-only?** Yes. It involves binary artifact policy and an owner OneDrive source path, so Prime may recommend but should not decide unilaterally.
6. **Are prior deliberations worth citing?** Yes, related context only: DELIB-0200, DELIB-0368, DELIB-0463. No exact prior Claude Design GUI-refresh intake deliberation found.

## Required Conditions For The Follow-On Implementation Bridge

1. It must explicitly state no widget/source implementation is included.
2. It must include D1-D7 as KB/procedure/governance/DA deliverables, with DA writes gated by that bridge's own GO.
3. It must correct current-state counts and distinguish source components from Storybook files.
4. It must include the new owner decision about Claude Design edit-mode roundtrip preservation.
5. It must cite related deliberations DELIB-0200, DELIB-0368, and DELIB-0463 as context, while stating that no exact prior Claude Design GUI-refresh intake deliberation was found.
6. It must define a pre-merge visual review artifact path rather than relying on the current post-merge Chromatic workflow alone.

## Verification Commands

Read-only commands were used to verify the proposal:

- `Get-Content -Raw .claude/rules/file-bridge-protocol.md`
- `Get-Content -Raw bridge/agent-red-claude-design-gui-refresh-intake-001.md`
- targeted `Select-String` reads against `bridge/INDEX.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/codex-review-gate.md`, `memory/work_list.md`, widget source files, and tests
- read-only zip inspection via `[System.IO.Compression.ZipFile]::OpenRead()`
- `Get-FileHash C:\Users\micha\OneDrive\Desktop\AR-Widget-handoff.zip -Algorithm SHA256`
- read-only `KnowledgeDB.search_deliberations()` queries for the five required topic terms

No test suite was run because this was a scope/proposal review with no code changes.
