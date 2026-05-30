REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 39611c3e-b51e-43f1-aa37-5ec4be3894b0
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning

# GT-KB CLAUDE.md Scope Clarification - Slice 2 - 003 (REVISED-1)

bridge_kind: governance_review

Document: gtkb-claude-md-scope-clarification-slice-2
Version: 003 (REVISED-1; responds to Codex NO-GO at -002)
Date: 2026-05-29 UTC
Responds to NO-GO: bridge/gtkb-claude-md-scope-clarification-slice-2-002.md
Supersedes: bridge/gtkb-claude-md-scope-clarification-slice-2-001.md
Carries forward GO: bridge/gtkb-claude-md-scope-clarification-scoping-002.md

## Claim

This REVISED reframes Slice 2 as a **true governance review** (the bridge_kind classification it has always carried) per Codex Finding F1 of `bridge/gtkb-claude-md-scope-clarification-slice-2-002.md`. Implementation work is deferred to a follow-on Slice 3 that will carry proper `Project Authorization` / `Project` / `Work Item` metadata for protected narrative-artifact mutations.

Slice 2 (this version) provides the governance design: the per-file disposition matrix, corrections to embedded content sections that had stale guidance (Codex F2/F3), the protected-artifact registry expansion required to close the F4 governance gap, and the root SECURITY.md stub plan (F5). The actual file writes, `git mv` operations, registry update, and approval-packet generation happen in Slice 3.

Owner decisions this session (via AskUserQuestion 2026-05-29) authorize this reframe:
- **F1**: "How should the REVISED address the bridge_kind/implementation-metadata mismatch?" → **"Reframe Slice 2 as governance review"**
- **F4**: "How should the REVISED handle the protected-artifact registry gap for new applications/Agent_Red/* files?" → **"Expand registry to protect app-side files"**

## Specification Links

Carries forward from -001 (all 16 specs cited). Re-stated here for compliance.

- `GOV-01` — CLAUDE.md ≤300 lines (Slice 3 verification).
- `GOV-08` — KB is truth; narrative-artifact permitted-markdown exception.
- `GOV-09` — Owner input classification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — live bridge index authority. This REVISED is filed at `bridge/INDEX.md` with `REVISED: bridge/gtkb-claude-md-scope-clarification-slice-2-003.md` inserted at the top of the document's existing entry per the protocol's newest-first convention; -001 (NEW) and -002 (NO-GO) version lines preserved; no deletion or rewrite of prior versions.
- `GOV-ARTIFACT-APPROVAL-001` — Slice 3 approval packets (count revised upward to 7 per F4 decision; see below).
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative-artifact mutation gate.
- `DCL-CONCEPT-ON-CONTACT-001` — load-bearing concept surface.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — proposal must cite governing specs; this REVISED enumerates them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Slice 3 will execute spec-derived verification.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — `applications/<name>/` placement.
- `ADR-0001` — Three-Tier Memory Architecture.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable artifact graph preservation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — narrative-artifact lifecycle trigger discipline.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance baseline.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` — Agent Red placement.
- `.claude/rules/operating-role.md` (new citation per F2) — durable role assignment in `harness-state/role-assignments.json`; markdown files cannot override.
- `.claude/rules/bridge-essential.md` §"Operational Mode" (new citation per F3) — cross-harness event-driven trigger as canonical bridge automation path.
- `.claude/rules/operating-model.md` §1, §2.
- `.claude/rules/canonical-terminology.md`.
- `.claude/rules/canonical-terminology.toml` dual-agent profile.
- `.claude/rules/project-root-boundary.md`.
- `.claude/rules/file-bridge-protocol.md`.
- `config/governance/narrative-artifact-approval.toml`.
- `AGENTS.md` line 11.

## Owner Decisions / Input

Four owner AskUserQuestion answers this session authorize this REVISED:

1. **Slice 1 → Slice 2 approach selection** (this session, earlier): "Codex GO at -002. Which structural approach should Slice 2 implement?" → **"C: Split (recommended)"**.
2. **Slice 2 scope expansion** (this session, earlier): "ISOLATION-018 already planned CLAUDE.md correction as part of sub-slices 18.I + 18.K... How should Slice 2 relate?" → **"Expand Slice 2 to 18.I scope"**.
3. **F1 metadata-mismatch resolution** (this session, just now): "How should the REVISED address the bridge_kind/implementation-metadata mismatch?" → **"Reframe Slice 2 as governance review"**.
4. **F4 registry-expansion resolution** (this session, just now): "How should the REVISED handle the protected-artifact registry gap for new applications/Agent_Red/* files?" → **"Expand registry to protect app-side files"**.

All captured in chat transcript; will be harvested to the Deliberation Archive at session wrap.

## Prior Deliberations

Carries forward from -001 (DELIB-0877, DELIB-0785, DELIB-0834, DELIB-0023, DELIB-0876, DELIB-0501, DELIB-0327, DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS, DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE, DELIB-0706, DELIB-0719). Codex confirmed all DELIB IDs exist via direct `get_deliberation` at -002 line 64.

Additional cross-references for this REVISED:
- `bridge/gtkb-claude-md-scope-clarification-slice-2-002.md` — Codex NO-GO with Findings F1-F5; recommended-action language carried forward into corrections below.

## Per-File Disposition Matrix (Unchanged from -001)

The 11-file disposition is the same as -001; the corrections in this REVISED do not change which files move. Re-stated for clarity:

| # | File | Lines | Current scope | Disposition (Slice 3) | Approval packet count |
|---|---|---|---|---|---|
| 1 | `README.md` | 86 | Platform | NO CHANGE (but see F5 below — update line 45 link IF root SECURITY.md is moved instead of stubbed) | No |
| 2 | `CLAUDE.md` | 301 | Mixed | SPLIT — platform stays at root (~260 lines after F2/F3 corrections); app content → `applications/Agent_Red/CLAUDE.md` | 1 (root update) + 1 (app-side create; newly protected per F4) |
| 3 | `CONTRIBUTING.md` | 67 | Agent Red | MOVE → `applications/Agent_Red/CONTRIBUTING.md` | No |
| 4 | `vision.md` | 2 | Platform | NO CHANGE | No |
| 5 | `MEMORY.md` (root) | 41 | Platform doctor marker | NO CHANGE | No |
| 6 | `CHANGELOG.md` | 146 | Agent Red | MOVE → `applications/Agent_Red/CHANGELOG.md` | No |
| 7 | `SECURITY.md` | 48 | Agent Red | MOVE → `applications/Agent_Red/SECURITY.md` + create new platform-level root stub (per F5) | No (move); New root stub also not in protected_artifacts |
| 8 | `CLAUDE-ARCHITECTURE.md` | 259 | Agent Red (stale) | MOVE + UPDATE → `applications/Agent_Red/CLAUDE-ARCHITECTURE.md` | 1 (root delete) + 1 (app-side create; newly protected per F4) |
| 9 | `CLAUDE-REFERENCE.md` | 263 | Agent Red | MOVE → `applications/Agent_Red/CLAUDE-REFERENCE.md` | 1 (root delete) + 1 (app-side create; newly protected per F4) |
| 10 | `CLAUDE_ARCHIVE.md` | 2293 | Agent Red historical | MOVE → `applications/Agent_Red/CLAUDE_ARCHIVE.md` | No |
| 11 | `AGENTS.md` | 292 | Platform | NO CHANGE (resolves OQ-4) | No |

**Slice 3 approval-packet count revised: 7 packets** (was 3 in -001; F4 decision adds 3 app-side creates as newly-protected; plus 1 packet for canonical-terminology.md update reflecting the new protected paths).

Plus 1 non-packet registry write: `config/governance/narrative-artifact-approval.toml` is self-excluded by the registry's own `excluded_by_design` pattern.

## F1 Correction — Reframe as Governance Review (No Implementation Targets)

Per owner AUQ decision: this slice does NOT carry implementation target_paths or generate approval packets directly. Slice 3 is the implementation slice. This Slice 2 REVISED-003 provides the governance design that Slice 3 implements.

What this means concretely:
- No `## target_paths` section in Slice 2.
- No `## Approval-Packet Plan` section in Slice 2 (only the Slice 3 plan is documented under "Slice 3 Implementation Plan" below).
- No `Project Authorization` / `Project` / `Work Item` lines required (`bridge_kind: governance_review` exemption is now valid).
- Slice 3 will be filed as a separate bridge thread (slug TBD; likely `gtkb-claude-md-scope-clarification-slice-3-implementation`) with full implementation metadata.

## F2 Correction — Embedded Role-Precedence Paragraph

Per Codex F2: my Slice 2-001 embedded text said `Role precedence: obey the newest owner role assignment reflected in AGENTS.md and the startup role-mapping rules under .claude/rules/`. This is incorrect because `.claude/rules/operating-role.md:7-17` says the durable role record lives in `harness-state/role-assignments.json` and no markdown rule file can override it.

**Replacement paragraph for the new platform CLAUDE.md** (replaces the line in -001's embedded content):

```text
**Role precedence:** active role is resolved at session start from `harness-state/harness-identities.json` (persistent harness identity) and `harness-state/role-assignments.json` (role set; the single source-of-truth durable role map). `.claude/rules/operating-role.md`, `AGENTS.md`, and `.claude/rules/*.md` files are explanatory guidance only — they describe behavior contracts but cannot override the durable role assignment map. If markdown text and the durable map differ, the durable map wins; surface the divergence as a defect rather than acting on the markdown.
```

## F3 Correction — Embedded Bridge Operating Section

Per Codex F3: my Slice 2-001 embedded text preserved stale manual-only dispatch framing (`Both agents scan the index when triggered manually by the owner... Automated polling was halted 2026-04-25`) and a Prime-only queue filter for the session-start bridge scan (`look for entries with GO or NO-GO status`). The current canonical state per `.claude/rules/bridge-essential.md` §"Operational Mode" is the cross-harness event-driven trigger with role-specific actionable filters.

**Replacement paragraph for "Operating procedure" bullets** (replaces the corresponding block in -001's embedded content):

```text
**Operating procedure.** File-based bridge protocol. See `.claude/rules/file-bridge-protocol.md` and `.claude/rules/bridge-essential.md` §"Operational Mode".

- **DO NOT implement anything without first preparing an implementation proposal and having it reviewed by Codex.**
- **All implementation proposals MUST be reviewed by Codex before any code is written.**
- **All post-implementation reports MUST be reviewed by Codex before committing.**
- **Propose:** Save proposal to `bridge/{name}-001.md`, add NEW entry to `bridge/INDEX.md`.
- **Review:** Codex scans INDEX for NEW/REVISED entries, reviews, adds GO or NO-GO version.
- **Execute:** After Codex GO, implement code, tests, and verify.
- **Report:** Save post-implementation report as new version, add NEW entry for verification.
- **Verify:** Codex reviews report and adds VERIFIED or NO-GO version.
- **Dispatch:** Bridge dispatch automation is the **cross-harness event-driven trigger** at `scripts/cross_harness_bridge_trigger.py`, registered as PostToolUse and Stop hooks in `.claude/settings.json` and `.codex/hooks.json`. The trigger fires on tool-use and Stop events. It dispatches Codex on latest `NEW` or `REVISED` (Loyal-Opposition-actionable) and Prime on latest `GO` or `NO-GO` (Prime-Builder-actionable). `VERIFIED` is terminal and not dispatched. The retired OS pollers and the retired smart poller are archived; do not re-enable without owner approval per `.claude/rules/bridge-essential.md` §"Re-Enabling Pollers".
- **Manual scan is fallback** when the trigger is unhealthy or intentionally stopped: the owner triggers a bridge scan with a brief prompt such as `Bridge` or `Bridge scan`; agents then read `bridge/INDEX.md` and act on role-appropriate actionable entries.
```

**Replacement for "Session Start: Bridge Index Scan"** (replaces the corresponding section in -001's embedded content):

```text
### Session Start: Bridge Index Scan (Mandatory)

At session start, scan `bridge/INDEX.md` for pending work using a **role-specific** filter:

1. **Read** `bridge/INDEX.md` and look for actionable entries for the active role:
   - **Prime Builder sessions:** look for latest `GO` or `NO-GO` per thread (Codex's verdicts on Prime's proposals/reports).
   - **Loyal Opposition sessions:** look for latest `NEW` or `REVISED` per thread (Prime's proposals/reports awaiting review).
2. **Report** any findings: "Bridge scan: N entries need attention" or "Bridge scan: clear."
3. **Process** the oldest actionable entry first.

The cross-harness event-driven trigger (registered as PostToolUse + Stop hooks per `.claude/rules/bridge-essential.md`) handles inter-session dispatch automatically; the session-start scan above is the in-session entry point and ensures awareness of items that landed while the session was idle.
```

## F4 Correction — Protected-Artifact Registry Expansion Plan (For Slice 3)

Per owner AUQ decision "Expand registry to protect app-side files": Slice 3 will update `config/governance/narrative-artifact-approval.toml` to add `applications/*/CLAUDE.md`, `applications/*/CLAUDE-REFERENCE.md`, and `applications/*/CLAUDE-ARCHITECTURE.md` as protected patterns.

**Proposed addition to `config/governance/narrative-artifact-approval.toml`** (after the existing `role-and-governance-rules` block):

```toml
[[protected_artifacts]]
id = "application-scope-rules"
description = "Application-scope narrative authority surfaces for managed applications under applications/<name>/. Per F4 decision in bridge/gtkb-claude-md-scope-clarification-slice-2-003.md."
patterns = [
  "applications/*/CLAUDE.md",
  "applications/*/CLAUDE-REFERENCE.md",
  "applications/*/CLAUDE-ARCHITECTURE.md",
]
required_evidence = [
  "approval_packet",
  "presented_to_user=true",
  "transcript_captured=true",
  "explicit_change_request",
]
```

`config/governance/narrative-artifact-approval.toml` is self-excluded from the protected-artifact registry (it cannot gate edits to itself); no approval packet is required for this registry update. However the update WILL be bridge-reviewed in Slice 3.

**Corresponding update to `.claude/rules/canonical-terminology.md`** (this file IS protected; needs an approval packet in Slice 3): the "canonical artifact" definition (around line 1288) will be extended to list `applications/<name>/CLAUDE.md`, `applications/<name>/CLAUDE-REFERENCE.md`, and `applications/<name>/CLAUDE-ARCHITECTURE.md` alongside the existing root paths, with a brief note explaining that application-scope authority extends to per-application narrative artifacts under the canonical placement.

## F5 Correction — Root SECURITY.md Platform Stub

Per Codex F5: README.md line 45 links to root SECURITY.md; moving root SECURITY.md without a replacement breaks that link.

**Slice 3 plan**: keep a root `SECURITY.md` as a platform-level dispatcher stub. Proposed content:

```markdown
# Security Policy — GroundTruth-KB Platform

This is the platform-level security policy entry point for GroundTruth-KB.

## Reporting a Vulnerability

To report a vulnerability in the GroundTruth-KB platform itself (governance contract, role enforcement, approval-packet evidence layer, secrets scanning, doctor checks, CLI surfaces), email **security@remakerdigital.com**.

To report a vulnerability in a specific application managed by GT-KB, see the per-application security policy:

- **Agent Red Customer Experience:** [`applications/Agent_Red/SECURITY.md`](applications/Agent_Red/SECURITY.md)

## Platform Security Practices

The GroundTruth-KB platform enforces:
- Pre-commit secrets scanning via `gt secrets scan --staged --fail-on verified-provider`.
- Narrative-artifact approval-packet evidence layer via `scripts/check_narrative_artifact_evidence.py` (universal `.githooks/pre-commit` floor).
- Append-only versioning of canonical artifacts in MemBase.
- Role-based authority via `harness-state/role-assignments.json` durable role map.
- Bridge-protocol GO/NO-GO/VERIFIED audit trail for governance-sensitive changes.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
```

This root stub is not in `protected_artifacts` (the existing SECURITY.md pattern is not in the registry); no approval packet required. The stub satisfies the README.md:45 link and preserves a platform-level security-policy affordance for GitHub repository-level security discovery.

`README.md:45` remains unchanged; the link target continues to be `SECURITY.md`, which now points to the platform-level stub above rather than Agent-Red-specific content.

## Slice 3 Implementation Plan (Forward Reference; NOT This Slice)

Slice 3 is the implementation slice that will carry the work documented here. It will be filed as a separate bridge thread with:

- `bridge_kind`: implementation (no exemption)
- `Project Authorization: PAUTH-...` (TBD — to be created or selected before Slice 3 filing)
- `Project: PROJECT-...` (TBD)
- `Work Item: WI-NNNN` (TBD)

**Slice 3 target_paths** (preview; will be re-stated in Slice 3 proposal):
- `CLAUDE.md` (update; root protected; packet 1)
- `CLAUDE-REFERENCE.md` (delete; root protected; packet 2)
- `CLAUDE-ARCHITECTURE.md` (delete; root protected; packet 3)
- `SECURITY.md` (rewrite as platform stub; not in protected_artifacts; no packet)
- `applications/Agent_Red/CLAUDE.md` (create; newly protected per F4; packet 4)
- `applications/Agent_Red/CLAUDE-REFERENCE.md` (create; newly protected per F4; packet 5)
- `applications/Agent_Red/CLAUDE-ARCHITECTURE.md` (create; newly protected per F4; packet 6)
- `applications/Agent_Red/CLAUDE_ARCHIVE.md` (create via git mv; not protected; no packet)
- `applications/Agent_Red/CONTRIBUTING.md` (create via git mv; not protected; no packet)
- `applications/Agent_Red/CHANGELOG.md` (create via git mv; not protected; no packet)
- `applications/Agent_Red/SECURITY.md` (create via git mv; not protected; no packet)
- `CONTRIBUTING.md`, `CHANGELOG.md`, `CLAUDE_ARCHIVE.md` (delete via git mv; not protected; no packet)
- `config/governance/narrative-artifact-approval.toml` (update; self-excluded; no packet)
- `.claude/rules/canonical-terminology.md` (update; protected; packet 7)
- `.groundtruth/formal-artifact-approvals/2026-05-NN-*` (7 new packets)

**Slice 3 approval-packet count: 7** (4 more than -001's count, due to F4 registry expansion adding 3 newly-protected app-side creates + 1 canonical-terminology.md update).

The embedded content for the new platform CLAUDE.md and new applications/Agent_Red/CLAUDE.md from -001, AS CORRECTED by F2 and F3 above, will be re-embedded in Slice 3 with the corrections applied. The CLAUDE-REFERENCE.md and CLAUDE_ARCHIVE.md move-only operations preserve content hash from source. The CLAUDE-ARCHITECTURE.md line-12 path fix is described as the diff in -001 "CLAUDE-ARCHITECTURE.md Line-12 Path Fix" section.

## Bridge Index Entry

This REVISED is filed at `bridge/` with an INDEX update that inserts `REVISED: bridge/gtkb-claude-md-scope-clarification-slice-2-003.md` at the top of the document's existing entry per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`. The prior version lines (`NO-GO: -002.md`, `NEW: -001.md`) are preserved; no deletion or rewrite of prior versions. The INDEX entry will read top-to-bottom: REVISED, NO-GO, NEW.

## Specification-Derived Verification Plan

Slice 2 is a governance review; no source/test/config mutations. Verification:
- Mandatory applicability preflight passes (`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-claude-md-scope-clarification-slice-2`) with `missing_required_specs: []`.
- Mandatory clause preflight passes (`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-claude-md-scope-clarification-slice-2`) with no blocking gaps.
- Codex review issues GO or NO-GO based on whether the F1-F5 corrections satisfy the -002 findings.

Slice 3 (implementation) verification will additionally include the Slice 1 Conditions 4-5 evidence (GOV-01 `wc -l`, doctor profile term check, cross-ref grep, narrative-artifact pre-commit gate), plus verification that the new `applications/*/CLAUDE.md` protected pattern correctly applies (test write to `applications/Agent_Red/CLAUDE.md` without approval packet should be blocked by the registry-driven hook).

## Requirement Sufficiency

Existing requirements sufficient. This REVISED operates within already-canonical specifications:
- `.claude/rules/operating-role.md` (F2 corrects to align with existing canonical role-precedence rule).
- `.claude/rules/bridge-essential.md` (F3 corrects to align with existing canonical bridge-operational-mode rule).
- `config/governance/narrative-artifact-approval.toml` excluded_by_design rationale for self-management (F4 registry expansion is governed by existing schema; no new spec needed).
- `README.md` link convention (F5 stub satisfies existing link without introducing new requirement).
- Two new owner AUQ answers this session (F1, F4) authorize the slice-2-as-governance-review reframe and registry expansion.

No new requirements need to be authored; this REVISED operationalizes existing canonical artifacts with the corrections Codex required.

## Risk / Rollback

- **Risk (Slice 2)**: None substantive — governance review only; no source mutations.
- **Risk (Slice 3, downstream)**: Approval-packet hash mismatch at write time, doctor profile term check failure if F2/F3 corrections accidentally drop required_startup_terms, broken cross-references if section anchors change. All mitigated by the verification plan; if Slice 3 NO-GO surfaces additional issues, REVISED loops continue.
- **Risk (F4 registry expansion)**: Hook (`.claude/hooks/narrative-artifact-approval-gate.py` + `scripts/check_narrative_artifact_evidence.py`) must correctly match the new `applications/*/CLAUDE.md` patterns. Mitigation: Slice 3 verification includes an explicit test write to confirm the new pattern is enforced.
- **Rollback (Slice 2)**: `git restore bridge/INDEX.md`; no other state changes.
- **Rollback (Slice 3)**: `git restore` all touched files; remove approval packets; revert registry expansion; revert canonical-terminology.md update.

## Follow-On Slices (Updated; Slice 3 is the Next Bridge Thread)

- **Slice 3 (next; separate bridge thread)** — implementation of the corrected plan: file rewrites, `git mv` operations, registry expansion, canonical-terminology.md update, 7 approval packets. Filed with proper PROJECT/WI/PAUTH metadata.
- **Slice 4 (separate)** — CLAUDE-REFERENCE.md content scope review (the content itself; this slice only moves it).
- **Slice 5 (separate)** — CLAUDE-ARCHITECTURE.md inventory rewrite for current GT-KB / Agent Red structure beyond the line-12 path fix.
- **Slice 6 (separate)** — `applications/` directory hygiene (95 `_test_*` rehearsal-artifact directories cleanup).
- **Future** — auto-load mechanism for `applications/<name>/CLAUDE.md` when work subject is `application`.
- **Future** — ISOLATION-018 sub-slices 18.J (repo separation) and 18.L (verification).

## Owner Action Required

Owner has already AUQ-answered F1 and F4 this session, plus the Slice 1 → Slice 2 approach selection and the 18.I scope expansion. No additional owner AUQ is required for this REVISED to receive Codex review.

After Codex GO on this REVISED:
1. Prime Builder files Slice 3 as a separate bridge thread with full PROJECT/WI/PAUTH metadata.
2. Slice 3 carries forward this design (corrected embedded content from F2/F3, registry-expansion plan from F4, SECURITY.md stub from F5) into a concrete implementation proposal.
3. Codex reviews Slice 3; on GO, owner presents 7 approval packets via AskUserQuestion (one per protected mutation).
4. Implementation executes; post-implementation report files for VERIFIED review.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
