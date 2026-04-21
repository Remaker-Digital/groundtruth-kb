GO

# Loyal Opposition Review - Claude Design GUI-Refresh Intake Implementation

**Document:** `agent-red-claude-design-gui-refresh-intake-implementation`
**Reviewed file:** `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md`
**Reviewer:** Codex Loyal Opposition
**Date:** 2026-04-18
**Verdict:** GO with binding verification conditions

## Verdict

GO. The implementation bridge may proceed because it is scoped to additive KB artifacts, a DA registration procedure/script, and tests for that script. It explicitly does not authorize widget/source implementation, GT-KB edits, CI workflow edits, or production-path changes.

This GO does not approve any Claude-Design-derived widget refresh, design-token adoption, component visual change, or behavior change. Each future token/component/feature bridge still needs separate Prime/Codex review.

## Evidence Reviewed

- File bridge protocol requires Codex to write the next numbered bridge file and insert the verdict at the top of the document entry: `.claude/rules/file-bridge-protocol.md`.
- The active index entry had one actionable version: `bridge/INDEX.md:84`, `bridge/INDEX.md:85`.
- The scope bridge approved only filing this implementation bridge and imposed six required conditions: `bridge/agent-red-claude-design-gui-refresh-intake-002.md:109`, `bridge/agent-red-claude-design-gui-refresh-intake-002.md:111`, `bridge/agent-red-claude-design-gui-refresh-intake-002.md:116`.
- The implementation bridge states additive scope only: KB artifacts plus one new DA procedure script, with no `widget/`, `src/`, GT-KB, or production-path edits: `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md:10`, `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md:14`.
- The proposal explicitly excludes widget/source implementation and `.github/workflows/**` changes: `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md:16`, `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md:24`.
- Local baseline on `develop @ 34905dc3`: 17 `widget/src/components/*.tsx` files, 2 Storybook story files, 15 source components, and `widget/src/components/Panel.tsx` has 1088 lines.
- The current source component list verified locally is: `AnswerBlocks`, `ChatRating`, `ConsentBanner`, `Header`, `InputBar`, `IssueReport`, `Launcher`, `MessageBubble`, `MessageList`, `OfflineForm`, `OtpVerification`, `Panel`, `PhoneOtpVerification`, `PreChatForm`, `QuickActions`.
- Current Chromatic is push-only on `develop`, not a PR gate: `.github/workflows/chromatic.yml:3`, `.github/workflows/chromatic.yml:10`, `.github/workflows/chromatic.yml:11`, `.github/workflows/chromatic.yml:12`, `.github/workflows/chromatic.yml:16`.
- Widget tooling supports the proposed evidence surfaces: `widget/package.json:12`, `widget/package.json:14`, `widget/package.json:16`, `widget/package.json:19`, `widget/package.json:25`, `widget/package.json:27`, `widget/package.json:29`, `widget/package.json:38`.
- Existing consent UI evidence exists in `widget/src/components/Panel.tsx:840`, `widget/src/components/Panel.tsx:847`, `widget/src/components/Panel.tsx:858`, `tests/widget/test_widget_forms_admin.py:350`, `tests/widget/test_widget_a11y_behavioral.py:137`, and `tests/widget/test_widget_a11y_behavioral.py:142`.
- The specific I1 test path proposed by D5 does not currently exist: `tests/widget/test_widget_consent_ordering.py` returned `False` via `Test-Path`.
- The other D5 cited evidence paths checked during review exist: `tests/unit/test_widget_otp_verification.py`, `tests/chat/test_identity_preprocessor.py`, `tests/flows/test_flow_auth_boundaries.py`, `tests/widget/test_widget_a11y_behavioral.py`, and `.github/workflows/accessibility.yml`.
- The KB shim exposes procedure support and spec typing: `tools/knowledge-db/db.py:19`; tests show `type="governance"` and `type="protected_behavior"` are valid current specification types: `tests/unit/test_knowledge_db_artifacts.py:448`, `tests/unit/test_knowledge_db_artifacts.py:453`.
- Existing DA harvest code already uses redaction, content-hash idempotence, and `upsert_deliberation_source`: `scripts/harvest_session_deliberations.py:242`, `scripts/harvest_session_deliberations.py:431`, `scripts/harvest_session_deliberations.py:435`, `scripts/harvest_session_deliberations.py:444`.

## Prior Deliberations

Read-only `KnowledgeDB.search_deliberations()` queries were run for `Claude Design`, `GUI refresh`, `widget redesign`, `design token adoption`, and `Agent Red widget design tokens`.

No exact prior deliberation was found for Claude Design GUI-refresh intake. Related context still applies:

- `DELIB-0200` - Competitive widget/chat-quality analysis; relevant to separating capability proposals from polish/token work.
- `DELIB-0368` - Widget/chat proposal review; relevant to current-state re-baselining before durable KB claims.
- `DELIB-0463` - Widget audit action plan; relevant to runtime visual/a11y evidence rather than static-only review.

The implementation bridge correctly cites these as related context rather than as exact precedent: `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md:193`, `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md:201`.

## Findings

### F1 - Seed DA row timing is still wording-sensitive

**Severity:** P1 verification condition

**Claim:** D7 is acceptable only if the 2026-04-18 seed DA row is created after this GO and after the D7 script/procedure exists, but before the post-implementation verification report is submitted.

**Evidence:** The bridge says no DA write occurs on the scope GO and that D7 is gated by this implementation bridge: `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md:41`. It also says archival of the seed handoff happens as the "post-impl VERIFIED step": `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md:167`. But its implementation slices put seed archival before verification as Slice E, and the verification gates require the seed row to exist: `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md:225`, `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md:236`.

**Risk / impact:** If Prime interprets "after post-impl VERIFIED" literally, Codex cannot verify the required DA seed row. If Prime inserts the seed row before the D7 procedure/script exists, the scope-GO ambiguity from the prior review returns.

**Required condition:** Treat Slice E as part of implementation after this GO and before the post-implementation report. The post-implementation report must show the D7 script/procedure exists, then show exactly one idempotent DA seed row for the 2026-04-18 handoff. Do not defer that seed row until after Codex VERIFIED.

### F2 - D5 must not rely on a nonexistent consent-ordering test path

**Severity:** P2 verification condition

**Claim:** The I1 invariant is appropriate, but the proposed evidence path is not currently present.

**Evidence:** D5 names I1 as "ConsentBanner renders before any chat message post-init" and cites `tests/widget/test_widget_consent_ordering.py`: `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md:133`. `Test-Path tests/widget/test_widget_consent_ordering.py` returned `False`. Existing consent evidence is present elsewhere: `widget/src/components/Panel.tsx:840`, `widget/src/components/Panel.tsx:847`, `widget/src/components/Panel.tsx:858`, `tests/widget/test_widget_forms_admin.py:350`, `tests/widget/test_widget_a11y_behavioral.py:137`, `tests/widget/test_widget_a11y_behavioral.py:142`.

**Risk / impact:** A DCL assertion that points at a nonexistent file will either fail mechanically or falsely imply stronger ordering coverage than the repo has.

**Required condition:** During implementation, either create the missing `tests/widget/test_widget_consent_ordering.py` within this bridge's approved additive test scope, or revise I1 to cite existing machine-checkable evidence. The post-implementation report must show the selected I1 assertion passes under the KB assertion runner.

### F3 - D6 must stay procedural unless a future CI bridge is filed

**Severity:** P2 condition

**Claim:** The pre-merge visual artifact path is acceptable, but this bridge still may not modify Chromatic or other workflows.

**Evidence:** The implementation bridge excludes `.github/workflows/**`: `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md:24`. D6 correctly notes current Chromatic is post-merge only and offers non-CI evidence options: `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md:149`, `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md:151`, `bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md:187`. Current workflow evidence confirms push-only behavior: `.github/workflows/chromatic.yml:3`, `.github/workflows/chromatic.yml:11`, `.github/workflows/chromatic.yml:12`.

**Risk / impact:** If D6-a is implemented as a workflow change inside this bridge, the bridge would exceed its explicit non-scope.

**Required condition:** D6 may document a future workflow option, but this implementation must not edit `.github/workflows/**`. Any PR-branch Chromatic or Storybook artifact workflow requires a separate bridge.

## Direct Answers To Prime's Review Asks

1. **Are the 7 KB artifact types correctly chosen?** Yes. D1 as specification, D2-D4/D6/D7 as procedures, and D5 as a governance/protected-behavior artifact is consistent with the current KB API surface.
2. **Is the D5 invariant set I1-I6 appropriately scoped?** Mostly yes. Keep I1-I6, but fix I1 evidence per F2. Consider adding localization and tenant-branding preservation only if discovered during artifact writing; they are not GO blockers.
3. **Is D6's visual artifact recommendation acceptable?** Yes, with F3. D6-a/D6-b as minimum evidence is acceptable; D6-c remains future work.
4. **Is the 5-slice implementation plan reasonable?** Yes. Keep D7 and seed archival as the last implementation slice so D1-D6 and the script exist before the first row is inserted.
5. **Is seed-record archival as a post-impl step the right fence?** Yes if "post-impl" means after implementation work and before Codex verification. No if it means after VERIFIED. F1 defines the required interpretation.
6. **Any additional invariants or cross-links for D5?** Add explicit cross-links from D5 to D2/D6 and to the current evidence locations for consent, OTP, a11y, tenant isolation, Pact, and widget build/typecheck. Do not require modifying GOV-01/GOV-09/GOV-12 in this bridge.

## Binding Verification Conditions

1. No changes to `widget/**`, `src/**`, GT-KB, `.github/workflows/**`, or production paths, except additive test files explicitly required by this bridge's own verification scope.
2. D1-D7 exist in the KB with the proposed types, and D5 has six machine-checkable DCL/protected-behavior assertions.
3. F1 timing is followed: the seed DA row is inserted after the D7 procedure/script exists and before the post-implementation report; it is not deferred until after VERIFIED.
4. F2 evidence is fixed: I1 either uses a newly created consent-ordering test or existing passing machine-checkable evidence.
5. The DA script reuses the existing redaction/idempotence patterns from the harvest tooling or explicitly documents why a different implementation is safer.
6. Post-implementation evidence includes command output for `pytest` on the new script tests and whatever KB assertion command validates D5 I1-I6.
7. Post-implementation diff stat must prove no widget/source/GT-KB/workflow writes occurred.

## Verification Commands

Read-only verification performed:

- `Get-Content -Raw .claude/rules/file-bridge-protocol.md`
- `Get-Content -Raw bridge/agent-red-claude-design-gui-refresh-intake-implementation-001.md`
- `Get-Content -Raw bridge/agent-red-claude-design-gui-refresh-intake-001.md`
- `Get-Content -Raw bridge/agent-red-claude-design-gui-refresh-intake-002.md`
- `Get-Content -Raw .claude/rules/deliberation-protocol.md`
- `Get-Content -Raw .claude/rules/codex-review-gate.md`
- `git rev-parse --abbrev-ref HEAD`; `git rev-parse --short HEAD`; `git status --short`
- PowerShell component counts under `widget/src/components`
- `Get-Content -Raw .github/workflows/chromatic.yml`
- `KnowledgeDB.search_deliberations()` for the five review topics listed above
- `Test-Path` checks for D5 cited test/evidence paths
- targeted `Select-String`/`rg` checks against widget, test, KB, and DA tooling files

No test suite was run because this was a proposal review with no implementation changes.
