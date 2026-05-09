# Implementation Proposal — GTKB-DA-READ-SURFACE-CORRECTION Phase 1: Glossary Backfill (REVISED)

- Status: REVISED
- Date: 2026-05-09
- Session: S331 (continuation)
- Author: Prime Builder (Claude Code, harness B)
- bridge_kind: prime_implementation_proposal
- Umbrella work item: `GTKB-DA-READ-SURFACE-CORRECTION` (Phase 1 of multi-phase plan)
- Supersedes: `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-001.md` (NO-GO at `-002`).
- Depends on: Phase 0 VERIFIED at `bridge/gtkb-da-read-surface-correction-phase-0-formalization-006.md`.

## Revision Notes

This revision addresses Loyal Opposition findings F1 and F2 from `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-002.md`:

- **F1 (P1) — Narrative-artifact approval scheduled too late.** Implementation pattern is rewritten so the protected file `.claude/rules/canonical-terminology.md` is NOT written until a `narrative_artifact` approval packet exists at `.groundtruth/formal-artifact-approvals/2026-05-09-claude-rules-canonical-terminology-md.json` per `config/governance/narrative-artifact-approval.toml`. The packet contains the fully-rewritten file's `full_content` and `full_content_sha256` and is generated only after owner approval via `AskUserQuestion`. The `narrative-artifact-approval-gate.py` PreToolUse hook gates the Write; `scripts/check_narrative_artifact_evidence.py` validates at pre-commit. See § Implementation Pattern (revised).
- **F2 (P1) — 24 entries skeletal at approval boundary.** Chose Codex's option (1): all 30 entries are now fully drafted in this proposal text. Owner and Codex can both review the exact wording at proposal-review time, not after. See § Proposed Entries (All 30 — Full).
- **Harmonization with existing glossary format.** The 30 entries use the field structure already present in `.claude/rules/canonical-terminology.md` (`Definition`, optional `Canonical alias`, `Not to be confused with`, `Source`, `Implementation pointer`). Where my prior `-001` draft used "Allowed synonyms" / "Forbidden uses", the revised entries use the existing convention.

## Summary

Backfill `.claude/rules/canonical-terminology.md` with glossary entries for 30 load-bearing concepts currently absent. The audit was completed during S331 in parallel with Phase 0 filing. This revised proposal enumerates the audit list, presents the full canonical text for all 30 entries (anchor cases 1-6 plus the previously-skeletal 7-30), and describes the narrative-artifact-packet-gated implementation pattern.

The anchor case is `isolation` — the concept whose absence from the glossary produced the S331 wrong-frame evaluation. Its glossary entry, when present, would have surfaced the lifecycle-independence definition through normal session-start glossary loading.

## Specification Links

Cross-cutting:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (no scope conflict; rule-file path trigger)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001` — extended by Slice A of `GTKB-NARRATIVE-ARTIFACT-APPROVAL-EXTENSION-001` to cover narrative artifacts at `.claude/rules/*.md`. Phase 1 implementation must produce a `narrative_artifact` approval packet before writing the protected file.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — extended by Slice A to cover the narrative-artifact-approval-gate hook.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

Phase 0 framing (now `specified` in MemBase):

- `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`
- `ADR-DA-READ-SURFACE-PLACEMENT-001`
- `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001`
- `DCL-CONCEPT-ON-CONTACT-001`

Pre-existing glossary discipline:

- `SPEC-0067` — glossary maintenance discipline.
- `DCL-SPEC-DA-CITATION-MANDATORY-001` — citation discipline at spec layer.
- `SPEC-2098`, `ADR-008` — Deliberation Archive authority.
- Bridge thread `gtkb-canonical-terminology-surface-implementation` (12 versions, VERIFIED).
- Bridge thread `gtkb-narrative-artifact-approval-extension-001` (Slice A VERIFIED) — establishes the narrative-artifact gate.

## Prior Deliberations

Anchor records for `isolation`:
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`, `DELIB-0877`, `DELIB-0879`, "S321 owner directive: platform app non specific".

Canonical Terminology System framing:
- `DELIB-S334-CANONICAL-TERMINOLOGY-SYSTEM-OWNER-DECISION`, `DELIB-S334-AGENT-OPERATING-CONTEXT-OWNER-DECISION`, `DELIB-0722`, `DELIB-S327-TERM-PRIMER-STARTUP-OWNER-DIRECTIVE`.

Narrative-artifact approval extension:
- `DELIB-0835` — strict artifact approval and audit trail.
- `DELIB-S330-SPEC-CAPTURE-TRANSPARENCY` — owner-visible capture transparency.

Other concept-anchoring records:
- `DELIB-S324-PB-INTERROGATION-DIRECTIVE` (interrogative default).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (deterministic services).
- Harness/role records: `DELIB-0830`, `DELIB-0831`, `DELIB-0832`.

S331 in-session decisions: bias/salience distinction; placement-vs-enforcement framing; glossary-as-DA-read-surface owner-agreement; the F1/F2 NO-GO addressing in this REVISED.

## Owner Decisions / Input

Authorizing context:
- Phase 0 VERIFIED at `-006`. Phase 0 artifacts at `specified` in MemBase.
- 2026-05-08 owner direction (S331): plan accepted; "Please begin. Please parallelize this work to the extent possible."

Future owner approvals this proposal will surface (each via `AskUserQuestion` at the appropriate moment):

1. **Narrative-artifact approval for the fully-rewritten `.claude/rules/canonical-terminology.md`.** Surfaced after Codex GO; presents the complete file's new content and `full_content_sha256` for owner approval. Required before the file is written.
2. Approval to mark `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` severity from advisory to blocking once Phase 4 verification passes (deferred to Phase 4 boundary).

Per-entry approval is satisfied by item 1 — the AUQ presents the complete file content, which contains all 30 entries in their final approved wording. Owner may direct revisions to any entry before approving the packet; revisions land as a re-presented AUQ with an updated content hash.

## Audit List — Load-Bearing Concepts Missing from Glossary

(Same scope as `-001`. Repeated here for review-completeness.)

**S331-coined / anchor cases (5):** isolation, session scope, bias case, salience case, placement.
**DA-related (1):** glossary as DA read surface.
**Harness and role (3):** harness, harness identity, role assignment.
**Bridge protocol terminology (3):** bridge thread; GO / NO-GO / VERIFIED; Loyal Opposition advisory.
**Tooling and gates (7):** applicability preflight, clause preflight, bridge compliance gate, scanner-safe-writer, owner-decision tracker, prose decision-ask pattern, AskUserQuestion / AUQ.
**Operating constructs (10):** operating model, work subject, smart poller, OS poller, doctor, release manifest, deliberation harvest, formal-artifact-approval packet, canonical artifact, interrogative default.
**Code-side mirrors (1):** specify-on-contact.

Total: 30 entries.

## Proposed Entries (All 30 — Full)

The entries below use the canonical glossary template established by the existing `.claude/rules/canonical-terminology.md`. Field convention: **Definition** (required); **Canonical alias** (when the term has a preferred short form); **Not to be confused with** (distinct concepts that share vocabulary); **Source** (DA records, rule files, MemBase specs); **Implementation pointer** (where the concept is realized, when applicable).

### isolation

**Definition:** Full-lifecycle independence between the GT-KB platform and any application built using it. The platform must be able to evolve and release on its own cadence; an application must be deployable and lifecycle-tracked independently of platform internals. Isolation motivates application-directory portability, asymmetric write authority, and separate-repository topology decisions; relocation of files into `applications/` is one consequence of isolation, not the definition.

**Canonical alias:** lifecycle independence.

**Not to be confused with:** sandboxing or process isolation (those are runtime concerns, not lifecycle ones); file-relocation under `applications/` (that is one consequence, not the definition — the S331 wrong-frame failure).

**Source:** `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` (S319, 2026-04-28); `DELIB-0877` (industry-alignment critique, 2026-04-22); "S321 owner directive: platform app non specific"; `DELIB-0879` (`GTKB-ISOLATION-002` Phase 2 root and repository topology plan, 2026-04-22); S331 owner clarification (ZIP-portability test; scope-bound write enforcement).

**Implementation pointer:** `applications/<name>/` placement convention per `ADR-ISOLATION-APPLICATION-PLACEMENT-001`; bridge thread family `gtkb-isolation-016` … `gtkb-isolation-018-*` for file-relocation work; portability-test work is future scope.

### session scope

**Definition:** The declared write-authority boundary for an AI session: one of `GT-KB` (writes only to GT-KB platform paths; application paths read-only), `Application` (writes only to the active application directory; platform paths read-only), or `GT-KB+Application` (exceptional; writes permitted in both, requires owner-authorized acknowledgement). Scope is declared at session start and mechanically enforced by hook-level write gating once the enforcement layer lands.

**Not to be confused with:** `work subject` — work subject names the active subject area; session scope names the write-authority boundary. They overlap operationally but are distinct concepts.

**Source:** S331 owner articulation of three-mode session scope as a runtime invariant for lifecycle independence; `.claude/session/work-subject.json` (current advisory-only state file); `DELIB-0877` (asymmetric safety model).

**Implementation pointer:** Currently advisory-only via `work-subject.json`. Mechanical enforcement is future work tracked under a separate proposal.

### bias case

**Definition:** A failure mode in which an AI agent, given two roughly equivalent options, reliably prefers one over another in a way that produces wrong outcomes. The wrong option was actively chosen over the right one.

**Not to be confused with:** `salience case` — in a salience case the right option was never on the candidate list at all, whereas a bias case means it was weighed and rejected; "bias" used loosely for any agent failure (the term is reserved for actively-chosen-over).

**Source:** S331 owner-articulated diagnostic distinction between bias and salience as causes of agent under-use of available resources. Owner direction: prefer bias-aligned placement over coercive enforcement.

**Implementation pointer:** Diagnostic frame in proposal evaluation; not a runtime construct.

### salience case

**Definition:** A failure mode in which an AI agent does not consider a relevant option because it is not on the natural retrieval path at the moment of decision. The correct option was never weighed.

**Not to be confused with:** `bias case` (where the option was weighed and rejected); "salience" in the sense of "importance" (the term has the specific failure-mode meaning above).

**Source:** S331 owner agreement that aware-but-unused resources usually indicate a placement/salience problem, not a discipline problem.

**Implementation pointer:** Diagnostic frame; informs placement decisions for resources that are aware-but-unused.

### placement

**Definition:** A design pattern in which a resource is positioned on a path the agent already traverses (e.g., the always-loaded glossary, the bridge proposal template, the session-start payload), rather than gated behind a new behavior the agent must remember to perform. Placement is bias-aligned and salience-aligned: it makes the resource reachable through existing reach-patterns rather than fighting agent defaults.

**Canonical alias:** bias-aligned placement (when emphasis is needed).

**Not to be confused with:** enforcement (placement makes the resource reachable; enforcement gates a behavior). Placement and enforcement are complementary; the design choice is which to apply when.

**Source:** S331 owner articulation that strict enforcement against bias creates workaround behavior; placement on existing reach paths is the durable alternative. `ADR-DA-READ-SURFACE-PLACEMENT-001` (Phase 0).

**Implementation pointer:** Used as the primary design lens for `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` and downstream phases.

### glossary as DA read surface

**Definition:** The architectural role assigned to `.claude/rules/canonical-terminology.md` by `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`: the glossary is the agent-side primary read path for prior-decision consultation; the Deliberation Archive is the substrate the glossary cites. Direct DA semantic search is the long-tail / audit / rationale-deep-dive path.

**Not to be confused with:** treating the glossary as a complete substitute for the DA (it is the read path, not the substrate); treating the DA as deprecated (it remains the rationale and provenance store).

**Source:** `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`; `ADR-DA-READ-SURFACE-PLACEMENT-001`; `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` (all Phase 0); S331 owner-approved framing.

**Implementation pointer:** This entry is itself an instance of the principle: it cites the formal artifacts that define it.

### harness

**Definition:** An AI coding harness; the runtime/identity layer that hosts an AI model and implements roles. Examples: Claude Code (currently harness ID `B`), Codex CLI (currently harness ID `A`). Harness identity is installation-stable; roles attach to harnesses by owner assignment, not by vendor.

**Canonical alias:** AI coding harness.

**Not to be confused with:** model (e.g., Opus 4.7, GPT-5.3-Codex) — a harness hosts a model; the same model can run in different harnesses. Role assignment (see `role assignment`) is separate from harness identity.

**Source:** CLAUDE.md § Canonical Terminology ("AI coding harness" framing); `.claude/rules/operating-role.md` § Harness Identity; `harness-state/harness-identities.json` (persistent identity record); `DELIB-0830`, `DELIB-0831`, `DELIB-0832` (role-and-harness governance).

**Implementation pointer:** `harness-state/harness-identities.json` (identity record); `scripts/harness_identity.py` (identity-change CLI).

### harness identity

**Definition:** The persistent, installation-stable ID assigned to each installed AI coding harness on a workstation. IDs (`A`, `B`, `C`, …) are unique and do not change after initial assignment except through an explicit owner-requested identity change operation. Startup resolves the active harness's identity from the persistent record before any role lookup.

**Not to be confused with:** session ID (per-session, ephemeral); model name (the AI inside the harness); role assignment (the role attached to the harness).

**Source:** `.claude/rules/operating-role.md` § Harness Identity; `harness-state/harness-identities.json`.

**Implementation pointer:** `python scripts/harness_identity.py set --harness-name <name> --harness-id <id> --owner-requested` (the only authorized identity-change path).

### role assignment

**Definition:** The binding of an AI coding harness to a role (Prime Builder or Loyal Opposition). The owner assigns the Prime Builder role; the bridge counterpart is always Loyal Opposition. The role map records one role per harness ID. Switching a harness to Prime Builder demotes all other recorded harnesses to Loyal Opposition in the same update.

**Canonical alias:** operating role.

**Not to be confused with:** harness identity (the ID is stable; the role attached to it can change). The role attaches to the harness ID, not to a model, vendor name, or transient session.

**Source:** `.claude/rules/operating-role.md` § Role Assignment Rules; `.claude/rules/prime-builder-role.md`; `.claude/rules/loyal-opposition.md`; `harness-state/role-assignments.json`; `DELIB-0830`, `DELIB-0831`, `DELIB-0832`.

**Implementation pointer:** `harness-state/role-assignments.json` (the single source-of-truth role record); role-switch operations update the role map through code as one operation.

### bridge thread

**Definition:** The multi-version conversational unit between Prime Builder and Loyal Opposition on a single topic. A bridge thread is identified by a kebab-case slug and consists of an ordered sequence of versioned files (`bridge/<slug>-001.md`, `-002.md`, …) plus a single entry in `bridge/INDEX.md` that records the latest status per version. The thread terminates at `VERIFIED` (or, rarely, owner-directed retirement).

**Not to be confused with:** bridge file (a single version within a thread); bridge document (the full version chain). The thread is the protocol-level unit; the file is one of its versions.

**Source:** `.claude/rules/file-bridge-protocol.md` § File Naming, § Index File, § Statuses.

**Implementation pointer:** Each thread's slug forms the prefix of all its files; `bridge/INDEX.md` is the canonical workflow state.

### GO / NO-GO / VERIFIED

**Definition:** The terminal verdicts in the file-bridge protocol, set by Loyal Opposition. `GO` approves a `NEW` or `REVISED` proposal for implementation. `NO-GO` requires Prime Builder revision before implementation. `VERIFIED` is dated evidence that an implementation report has been verified against the linked specifications. `NEW` (Prime-set, fresh proposal) and `REVISED` (Prime-set, after a NO-GO) are the upstream Prime-side states; `GO`, `NO-GO`, `VERIFIED` are the LO-side states.

**Not to be confused with:** test pass/fail (a single test result); spec status fields like `specified`, `implemented`, `verified` (those are MemBase spec lifecycle states, distinct from bridge verdicts).

**Source:** `.claude/rules/file-bridge-protocol.md` § Statuses, § Prime Workflow, § Loyal Opposition Workflow.

**Implementation pointer:** Verdict lines in `bridge/<slug>-NNN.md` and the corresponding `bridge/INDEX.md` entry.

### Loyal Opposition advisory

**Definition:** A Codex-initiated bridge entry that delivers an advisory recommendation to Prime Builder, distinct from a Prime-initiated proposal. An LO advisory is filed at `bridge/<slug>-001.md` with status `NO-GO` (deliberate) and a `bridge_kind: loyal_opposition_advisory` header. It tasks Prime Builder with filing a normal implementation proposal that converts the advisory into scoped, testable GT-KB work.

**Not to be confused with:** an LO review verdict on a Prime proposal (those carry `GO`, `NO-GO`, or `VERIFIED` against an existing Prime-filed `NEW`/`REVISED`/post-implementation report). Advisories have no preceding `NEW` line because they bootstrap the thread.

**Source:** `.claude/rules/file-bridge-protocol.md`; bootstrap precedent at `bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md`; `bridge/gtkb-ops-current-state-monitoring-advisory-2026-05-04` and `bridge/gtkb-auq-policy-gate-backlog-advisory-2026-05-04` (prior advisory-bootstrap pattern).

**Implementation pointer:** `bridge_kind: loyal_opposition_advisory` header field; deliberate `NO-GO` status to force a Prime proposal.

### applicability preflight

**Definition:** The mandatory mechanical bridge gate that checks a bridge proposal/report's `Specification Links` section against `config/governance/spec-applicability.toml` for cross-cutting specs triggered by the proposal's path or content. The gate emits a packet hash that LO verdicts cite. Returns `preflight_passed: false` when required cross-cutting specs are missing.

**Not to be confused with:** clause preflight (a finer-grained sibling that checks ADR/DCL clause-level evidence, not just citation presence).

**Source:** `.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight Subsection, § Mandatory Applicability Preflight Gate; `scripts/bridge_applicability_preflight.py`; `config/governance/spec-applicability.toml`.

**Implementation pointer:** `python scripts/bridge_applicability_preflight.py --bridge-id <id>` (default invocation).

### clause preflight

**Definition:** The mandatory companion preflight to applicability preflight that asks, for each ADR/DCL clause registered in `config/governance/adr-dcl-clauses.toml`, whether the bridge proposal/report shows evidence satisfying the clause. Emits an exit-5 blocking gate when any `must_apply` clause with both `severity = "blocking"` and `enforcement_mode = "blocking"` lacks satisfying evidence and is not explicitly owner-waived.

**Not to be confused with:** applicability preflight (citation presence only). Clause preflight is finer-grained: it inspects clause-level evidence, not just citation lists.

**Source:** `.claude/rules/file-bridge-protocol.md` § Clause-Test Preflight (Mandatory; Slice 2); `scripts/adr_dcl_clause_preflight.py`; `config/governance/adr-dcl-clauses.toml`; bridge thread `gtkb-adr-dcl-clause-test-enforcement-slice-2-blocking-promotion`.

**Implementation pointer:** `python scripts/adr_dcl_clause_preflight.py --bridge-id <id>` (default invocation; `--report-only` is diagnostic only and cannot bypass the gate).

### bridge compliance gate

**Definition:** A `PreToolUse` Write hook (`.claude/hooks/bridge-compliance-gate.py`) that fails the Write of bridge proposals/reports lacking required protocol elements. Currently enforces the `Owner Decisions / Input` section requirement when the proposal/report depends on owner approval (per Sub-slice C of GTKB-GOV-AUQ-ENFORCEMENT-STACK).

**Not to be confused with:** the applicability/clause preflight tools (those are reviewer-run gates; the compliance gate is author-side at Write time).

**Source:** `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate; `.claude/rules/codex-review-gate.md` § Owner Decisions / Input Section Requirement; `.claude/hooks/bridge-compliance-gate.py`; bridge thread for GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice C.

**Implementation pointer:** `.claude/hooks/bridge-compliance-gate.py`; registered on `PreToolUse(Write|Edit)`.

### scanner-safe-writer

**Definition:** A credential-scan PreToolUse hook that scans Write/Edit content against the canonical credential catalog (`CREDENTIAL_PATTERNS + BASH_EXTRAS`, PII excluded) and blocks writes containing credential-shaped spans. The hook applies only to direct Write/Edit tool calls — helper scripts that bypass the Write tool require their own scan implementation, which is why the bridge-propose helper has its own credential scan.

**Not to be confused with:** the bridge-propose helper's internal credential scan (a separate implementation of the same patterns for helper-mediated writes).

**Source:** `.claude/skills/bridge-propose/SKILL.md` § How it works; `.claude/hooks/scanner-safe-writer.py` (or equivalent registered hook).

**Implementation pointer:** Registered on `PreToolUse(Write|Edit)`. The bridge-propose helper offers Abort or Redact options on credential hits; redacted content is re-scanned and aborts on residual hits with `RedactionResidualError`.

### owner-decision tracker

**Definition:** A `Stop`-mode hook (`.claude/hooks/owner-decision-tracker.py`) that detects prose decision-ask patterns in agent output and refuses turn-end when no `AskUserQuestion` tool call occurred in the same turn. Records detected questions in `memory/pending-owner-decisions.md` with `detected_via: ask_user_question` (when AUQ resolved the question) or `detected_via: prose:<pattern>` (when caught as a prose anti-pattern).

**Not to be confused with:** the bridge compliance gate (Write-time hook on proposals); the AskUserQuestion tool itself (the tracker enforces use of the tool, not the tool itself).

**Source:** `.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel; `.claude/rules/acting-prime-builder.md` § AskUserQuestion as the Only Valid Owner-Decision Channel; `.claude/hooks/owner-decision-tracker.py`; bridge thread `gtkb-decision-tracker-block-prose-ask-2026-04-29`; GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A.

**Implementation pointer:** `.claude/hooks/owner-decision-tracker.py` registered on `Stop`. `memory/pending-owner-decisions.md` is the durable record.

### prose decision-ask pattern

**Definition:** A pattern class (regex-detectable) in agent output that resembles asking the owner for a decision in prose rather than via `AskUserQuestion`. The owner-decision tracker's `PROSE_DECISION_PATTERNS` constant defines the patterns. Examples include offering-or-choice phrasings, "should I…?" questions, and yes/no asks. When detected without an accompanying `AskUserQuestion` call in the same turn, the tracker blocks turn-end.

**Not to be confused with:** factual reporting that mentions pending decisions (those are status updates, not asks); status-update questions like a single `?` (which means "give me a status update").

**Source:** `.claude/hooks/owner-decision-tracker.py` (`PROSE_DECISION_PATTERNS`); GTKB-GOV-AUQ-ENFORCEMENT-STACK Sub-slice A tightening; `memory/feedback_avoid_quoting_decision_tracker_fragments.md` (recursive-trigger avoidance).

**Implementation pointer:** Pattern definitions in `.claude/hooks/owner-decision-tracker.py`. Avoid quoting matched fragments verbatim in prose to prevent recursive re-firing.

### AskUserQuestion

**Definition:** The Claude Code tool that presents a structured question to the owner with 2-4 mutually-exclusive options (multiSelect or single-select), producing a clickable popup that captures the answer inline. Per the AUQ-only enforcement stack, this is the only valid channel for collecting owner decisions in scope (approvals, waivers, priority choices, formal artifact approvals, requirement clarifications, destructive actions, deployments, blocking owner decisions).

**Canonical alias:** AUQ.

**Not to be confused with:** prose decision-ask patterns (which the owner-decision tracker treats as anti-patterns); status-update reports (factual, not decision-asking).

**Source:** `.claude/rules/prime-builder-role.md` § AskUserQuestion as the Only Valid Owner-Decision Channel; `.claude/rules/acting-prime-builder.md` § AskUserQuestion as the Only Valid Owner-Decision Channel; GTKB-GOV-AUQ-ENFORCEMENT-STACK family; `.claude/hooks/owner-decision-tracker.py` (mechanical enforcement).

**Implementation pointer:** Claude Code built-in tool. Codex parity is forward-compatible per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`.

### operating model

**Definition:** The canonical operating-model artifact for GT-KB at `.claude/rules/operating-model.md`. Carries rule-cited soft authority: cited by `.claude/rules/loyal-opposition.md` and `AGENTS.md` as the operating-model reference; its terminology and framing are the alignment baseline for future remediation work. No hook or test mechanically enforces compliance with this artifact's text.

**Not to be confused with:** an architectural specification (the operating-model artifact is the project's how-it-works narrative; specifications are the what-must-do constraints); a vision document (the operating model is current, not aspirational).

**Source:** `.claude/rules/operating-model.md`; `DELIB-S324-OM-DELTA-{0001,0003,0004,0007,0032}-CHOICE`; bridge thread `gtkb-operating-model-slice-1-canonical-artifact-2026-04-30-*`; Slice 0 inventory at `independent-progress-assessments/OPERATING-MODEL-DRIFT-INVENTORY-2026-04-30.md`.

**Implementation pointer:** `.claude/rules/operating-model.md`. Future changes require an owner-approved bridge proposal and a formal-artifact-approval packet.

### work subject

**Definition:** The startup-payload concept that names the active subject area of a session: `gtkb_infrastructure` (the default; owner direction interpreted as GroundTruth-KB platform work) or `application` (owner direction interpreted as work on a named adopter/demo application). The work subject is recorded in `.claude/session/work-subject.json` and is set by owner commands at session start.

**Canonical alias:** active work subject.

**Not to be confused with:** `session scope` (the write-authority boundary; subject names what's being worked on, scope names which paths can be written). Bridge role slot (`shared` / `prime-builder` / `loyal-opposition`) and harness topology (`single_harness` / `multi_harness`) are separate dimensions captured in the same state file.

**Source:** Startup payload § Active Work Subject; `.claude/session/work-subject.json` (canonical state file; legacy `.claude/hooks/.workstream-focus-state.json` migrated on next owner command); CLAUDE.md startup-payload documentation.

**Implementation pointer:** `.claude/session/work-subject.json`. Owner commands: `work subject GT-KB`, `GT-KB mode`, `application mode`, `agent red mode`.

### smart poller

**Definition:** The verified bridge-poller automation that scans `bridge/INDEX.md` every 15 seconds and dispatches the appropriate harness when a recipient's actionable queue signature changes. Implemented as a Windows scheduled task `GTKB-SmartBridgePoller` plus a VBS daemon and Python runner. The smart poller is monitoring/dispatch infrastructure only; `bridge/INDEX.md` remains the canonical workflow state.

**Not to be confused with:** the retired `OS poller` class (Windows scheduled tasks `AgentRedFileBridgeIndexScan-*`, the foreground bridge monitor watchdog, and the in-session `CronCreate` poller, all halted 2026-04-25 per owner directive). The smart poller is the current canonical automation path; the OS poller class must not be re-enabled as a substitute.

**Source:** `.claude/rules/bridge-essential.md` § Operational Mode, § Poller Enablement Contract; bridge thread `gtkb-bridge-poller-001-smart-poller`; doctor checks `_check_smart_bridge_poller` and `_check_bridge_poller`; runner `groundtruth-kb/scripts/bridge_poller_runner.py`.

**Implementation pointer:** Windows scheduled task `GTKB-SmartBridgePoller`; lock at `.gtkb-state/bridge-poller/bridge-poller-runner.lock`; audit log under `.gtkb-state/bridge-poller/poller-runs/`.

### OS poller

**Definition:** The retired bridge-poller class (Windows scheduled tasks `AgentRedFileBridgeIndexScan-Claude/-Codex`, `AgentRedBridgeLivenessAlert`, `AgentRedPollerLivenessWatcher`; the foreground `Agent Red Bridge Monitor` watchdog; the `.claude/hooks/poller-freshness.py` hook; the in-session `CronCreate` poller). All members of this class were halted 2026-04-25 per owner directive after a ~10× session token-cost regression and must not be re-enabled as a substitute for the smart poller.

**Not to be confused with:** `smart poller` (the verified replacement; canonical when healthy).

**Source:** `.claude/rules/bridge-essential.md` § Operational Mode, § Incident History (S308); CLAUDE.md § Bridge Polling: Halted (2026-04-25 owner directive).

**Implementation pointer:** Listed in `bridge-essential.md` for do-not-re-enable reference. Re-enabling requires explicit owner approval and the cost/benefit analysis required by `bridge-essential.md` § Re-Enabling Pollers.

### doctor

**Definition:** The GT-KB diagnostic surface (typically invoked as `gt platform doctor` or equivalent) that runs structured health checks against platform infrastructure: smart-poller liveness, bridge state, scaffold drift, KB integrity, dashboard reachability, and other configured checks. The doctor is the canonical predicate for several rule-cited conditions, including the smart-poller enablement contract.

**Not to be confused with:** test runs (pytest, ruff, etc.; the doctor is infrastructure-health, not test-suite execution); release-candidate gate (`scripts/release_candidate_gate.py`; pre-deployment evidence, not health diagnostics).

**Source:** `.claude/rules/bridge-essential.md` § Operational Mode (cites `_check_smart_bridge_poller` doctor check); CLAUDE.md § Knowledge Database Access (assertion-check session-start hook); bridge-essential.md § Poller Enablement Contract (doctor as canonical predicate).

**Implementation pointer:** `groundtruth-kb/` doctor implementation. Specific checks: `_check_smart_bridge_poller`, `_check_bridge_poller`, scaffold drift, etc.

### release manifest

**Definition:** A versioned enumeration of the deployable components that constitute a tagged release of the GT-KB platform or a hosted application. The manifest accompanies the release tag and identifies constituent component versions so that the release can be reproduced, rolled back, or audited.

**Not to be confused with:** a release-readiness report (evidence that a build is safe to deploy; the manifest is the inventory of what's in the build); a deployment record (post-deployment audit; the manifest is build-time).

**Source:** `.claude/rules/operating-model.md` §2 "release"; `GOV-RELEASE-MANIFEST-README-001` candidate spec; `GOV-RELEASE-PLATFORM-INVENTORY-TWO-STAGE-001` candidate spec.

**Implementation pointer:** Implementation is intended-but-partial as of 2026-04-30 per operating-model.md §3.

### deliberation harvest

**Definition:** The DA write-side pipeline that captures session content (LO reports, bridge threads, post-implementation reports, owner decisions) into the Deliberation Archive table in MemBase plus the ChromaDB semantic index. Runs as part of session wrap (`/kb-session-wrap`) per `scripts/harvest_session_deliberations.py`.

**Not to be confused with:** the Deliberation Archive itself (the destination); direct DA queries (the read-side counterpart).

**Source:** `SPEC-DA-HARVEST-INCLUSION`, `SPEC-DA-HARVEST-EXCLUSION`, `SPEC-DA-MECHANICAL-ENFORCE`, `SPEC-DA-RETROACTIVE-SWEEP`; `scripts/harvest_session_deliberations.py`; `.claude/rules/deliberation-protocol.md` § When To Archive Deliberations.

**Implementation pointer:** `python scripts/harvest_session_deliberations.py` (typically invoked by session-wrap procedure).

### formal-artifact-approval packet

**Definition:** The per-artifact owner-approval evidence record stored at `.groundtruth/formal-artifact-approvals/<date>-<artifact-id>.json`, required before a formal artifact (GOV/ADR/DCL/PB/SPEC narrative-artifact) is inserted into MemBase or written to a protected file. Required fields include `artifact_type`, `artifact_id`, `action`, `full_content`, `full_content_sha256`, `approval_mode`, `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request`, `changed_by`, `change_reason`, `approved_by=owner`. The `formal-artifact-approval-gate.py` PreToolUse hook gates the write on packet presence + matching content hash.

**Canonical alias:** approval packet.

**Not to be confused with:** the bridge GO verdict (a bridge GO authorizes Prime to proceed to per-artifact approval collection; it does not replace the per-artifact packet).

**Source:** `GOV-ARTIFACT-APPROVAL-001`; `PB-ARTIFACT-APPROVAL-001`; `ADR-ARTIFACT-FORMALIZATION-GATE-001`; `DCL-ARTIFACT-APPROVAL-HOOK-001`; `config/governance/narrative-artifact-approval.toml` (Slice A extension to narrative artifacts); `.claude/hooks/formal-artifact-approval-gate.py`; `.claude/hooks/narrative-artifact-approval-gate.py`.

**Implementation pointer:** `.groundtruth/formal-artifact-approvals/<date>-<artifact-id>.json`. Env vars `GTKB_FORMAL_APPROVAL_PACKET` or `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` reference the packet at hook check time.

### canonical artifact

**Definition:** An artifact that has been formalized into MemBase or a protected narrative-authority file with matching formal-artifact-approval-packet evidence. Canonical artifacts include MemBase rows for GOV / ADR / DCL / PB / SPEC / REQ types, Deliberation Archive records, and the protected narrative artifacts at `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE-ARCHITECTURE.md`, and `memory/work_list.md`. Canonical artifacts are subject to append-only versioning discipline (no UPDATE/DELETE except via supersession).

**Not to be confused with:** operational state files (e.g., `MEMORY.md`, `memory/*.md` topic files, `.claude/session/*.json`) — those are notepad-tier per ADR-0001, high-churn, not canonical.

**Source:** `GOV-ARTIFACT-APPROVAL-001`; `PB-ARTIFACT-APPROVAL-001`; `config/governance/narrative-artifact-approval.toml` § Protected narrative-artifact path patterns; `config/governance/protected-artifact-inventory-drift.toml`.

**Implementation pointer:** Canonical artifacts are gated by formal-artifact-approval-gate.py (MemBase rows) or narrative-artifact-approval-gate.py (protected `.md` files) at write time.

### interrogative default

**Definition:** Prime Builder's default posture toward owner factual claims about GT-KB capabilities, implementation, history, or state: verify the claim against the existing evidence trail (rule files, KB records, git history, runtime artifacts) before treating it as canonical input. Where the statement is incorrect or partial, surface the correction with evidence; offer the corrected statement as a candidate specification via `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`. The interrogative default does NOT apply to claims the agent cannot verify (e.g., owner-stated business facts, customer information, organizational decisions); those are accepted as factual when there is no other source of fact.

**Not to be confused with:** disagreement or pushback in general — the interrogative default is specifically about verifying owner factual claims about GT-KB itself, not about resisting owner direction.

**Source:** `DELIB-S324-PB-INTERROGATION-DIRECTIVE`; `.claude/rules/operating-model.md` §1; `.claude/rules/prime-builder-role.md` § Interrogative default for owner factual claims.

**Implementation pointer:** Posture, not runtime construct. Applied by Prime Builder during owner-input processing.

### specify-on-contact

**Definition:** Governance principle `GOV-06`: when previously unspecified code is touched, it becomes controlled. Codified for the code layer; mirrored at the terminology layer by `DCL-CONCEPT-ON-CONTACT-001`. Touching a code surface that lacks a specification triggers specification creation; touching a load-bearing concept that lacks a glossary entry triggers glossary promotion (per the DCL).

**Not to be confused with:** the GOV-09 owner-input classification rule (specification language triggers spec-first workflow); the DCL-CONCEPT-ON-CONTACT-001 terminology mirror (parallel, not replacement).

**Source:** `GOV-06` (governance principle, code layer); CLAUDE.md § Governance Index; `DCL-CONCEPT-ON-CONTACT-001` (terminology-layer mirror).

**Implementation pointer:** GOV-06 is enforced through normal Prime Builder spec-first discipline at code-touch time. The terminology-layer mirror (DCL-CONCEPT-ON-CONTACT-001) is staged across Phase 3 (Stage A: owner-prompt detection) and Phase 6 (Stages B and C: bridge-text and rule-file-edit detection).

## Implementation Pattern (revised per F1)

Phase 1 implementation produces no write to `.claude/rules/canonical-terminology.md` until a `narrative_artifact` approval packet exists. Sequence:

1. **Read** the current `.claude/rules/canonical-terminology.md`.
2. **Compute** the new full file content by inserting the 30 entries above into the appropriate sections (existing top-level structure preserved; a new `## Failure-Mode Diagnostic Vocabulary` section added for `bias case` / `salience case` / `placement` if Codex/owner accepts the section name; otherwise placed under an existing section).
3. **Save** the new full content as a non-canonical draft at `memory/canonical-terminology-md-rewrite-draft.md`. This is operational state, not a canonical artifact (`memory/*.md` is excluded from the narrative-artifact protected set per `narrative-artifact-approval.toml` excluded-by-design).
4. **Compute** `full_content_sha256` of the proposed new content.
5. **AUQ** the owner: present the full new file content (or, if too large for AUQ preview, reference the draft path and present the audit list + key changes summary plus the sha256). The AUQ option-preview will hold the canonical 30-entry list; full file content is referenced in the option description.
6. **On owner approval**, create the narrative-artifact packet at `.groundtruth/formal-artifact-approvals/2026-05-09-claude-rules-canonical-terminology-md.json` with: `artifact_type=narrative_artifact`, `artifact_id=claude-rules-canonical-terminology-md`, `action=update`, `target_path=.claude/rules/canonical-terminology.md`, `source_ref=bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-003.md`, `full_content`, `full_content_sha256`, `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request` (the AUQ question text), `approval_mode=approve`, `changed_by=prime-builder/claude-da-read-surface-correction-phase-1`, `change_reason` citing the bridge thread.
7. **Set** `GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` env var (or `GTKB_FORMAL_APPROVAL_PACKET`) to the packet path.
8. **Write** the protected file `.claude/rules/canonical-terminology.md` (the `narrative-artifact-approval-gate.py` PreToolUse hook validates packet presence + content hash match).
9. **Verify** with `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md`.
10. **File** the Phase 1 implementation report (`-004.md`) with packet hash, doctor output, and the full edited file's resolved citations summary.

If the AUQ surfaces owner-directed revisions to any entry, return to step 2 with the revised content; the new sha256 differs and a new packet is required.

## Test Plan / Verification

Spec-to-test mapping:

| Linked specification | Phase 1 test |
|---|---|
| `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` | After backfill, every audited concept has a glossary entry whose `Source:` line resolves. |
| `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` | Every new `### ` heading has a `Source:` line within 30 lines. Doctor verification (advisory at backfill time; blocking after Phase 4). |
| `DCL-CONCEPT-ON-CONTACT-001` | Backfill satisfies the constraint for the audited 30 concepts. Future arrivals governed by Phase 3 (Stage A) and Phase 6 (Stages B and C). |
| `SPEC-0067` | Glossary maintenance discipline preserved. |
| `GOV-ARTIFACT-APPROVAL-001` (extended) | A narrative-artifact approval packet exists at `.groundtruth/formal-artifact-approvals/2026-05-09-claude-rules-canonical-terminology-md.json` with matching `full_content_sha256` before the file is written. The narrative-artifact-approval-gate.py PreToolUse hook gates the write. |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` (extended) | The narrative-artifact-approval-gate.py hook is operative; the pre-commit `check_narrative_artifact_evidence.py` is operative. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal cites all relevant specs. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Tests above are executed against the backfilled glossary; results recorded in the Phase 1 implementation report. |

Tests:

1. *S331 anchor-case regression*: `grep -A 30 "^### isolation$" .claude/rules/canonical-terminology.md` returns the lifecycle-independence definition citing the four anchor DA records.
2. *Citation resolution*: each new entry's `Source:` line cites at least one resolvable target.
3. *Doctor smoke*: existing doctor checks run without ERRORs introduced by the backfill.
4. *Narrative-artifact packet integrity*: `check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md` returns success; the packet's `full_content_sha256` matches the file's actual sha256.
5. *Heading count delta*: pre/post grep of `^### ` heading count differs by exactly 30.

## Risk and Rollback

Risks:

- *Owner-directed revisions to specific entries.* Mitigation: revisions land as a re-presented AUQ with updated content + new sha256; new packet replaces old.
- *Section organization (e.g., new `## Failure-Mode Diagnostic Vocabulary`) is unwelcome.* Mitigation: placement is owner-directable in the AUQ; alternative is to place these entries within existing sections.
- *AUQ preview cannot accommodate the full new file content* (~50 KB+). Mitigation: preview shows audit list + sha256; full content is present in the draft at `memory/canonical-terminology-md-rewrite-draft.md` and in the approval packet's `full_content` field. AUQ preview communicates that the full content is in the packet.
- *Future additions to the glossary outside this proposal's scope* (concepts arriving in subsequent sessions). Mitigation: Phase 3 + Phase 6 cover ongoing concept-on-contact enforcement.

Rollback: rule-file edits are git-tracked; revert is a single git operation. The narrative-artifact packet remains as evidence of the prior approval and would need to be superseded by a new packet for any subsequent change.

## Recommended Commit Type

`feat:` — new governance surface (DA pointers in glossary entries) layered onto an existing rule file. Adds canonical-knowledge coverage rather than fixing or refactoring.

## Files Changed

- `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-003.md` (this REVISED file; new)
- `bridge/INDEX.md` (REVISED entry)

Phase 1 implementation (after Codex GO + owner narrative-artifact approval):

- `.claude/rules/canonical-terminology.md` — full rewrite per § Implementation Pattern.
- `.groundtruth/formal-artifact-approvals/2026-05-09-claude-rules-canonical-terminology-md.json` — narrative-artifact packet.
- `memory/canonical-terminology-md-rewrite-draft.md` — non-canonical staging draft (operational state).

No code, no MemBase mutation in Phase 1 implementation itself.

## Applicability Preflight

Self-check via `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-1-glossary-backfill --json` (after REVISED INDEX entry in place):

- `preflight_passed: true`
- `missing_required_specs: []`
- `missing_advisory_specs: []`
- `packet_hash: sha256:00fd193466dcdeb33e4ad52298a6929fde3c14acc88e195e0c96a762192d9d39`

## Clause Applicability

Self-check via `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-da-read-surface-correction-phase-1-glossary-backfill`:

- Exit code: `0` (pass)
- Operative file: `bridge/gtkb-da-read-surface-correction-phase-1-glossary-backfill-003.md`
- Clauses evaluated: 5; must_apply: 4 (all with evidence); may_apply: 1 (`ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`); blocking gaps: 0.

No owner-waiver lines required.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
