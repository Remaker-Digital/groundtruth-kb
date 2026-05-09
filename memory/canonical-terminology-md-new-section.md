## GT-KB DA Read-Surface and Operational Vocabulary (S331 backfill)

Per `GOV-GLOSSARY-AS-DA-READ-SURFACE-001`, this section adds glossary entries
for load-bearing concepts identified during S331 as canonical but previously
absent from the glossary. Each entry follows the field convention (Definition,
optional Canonical alias, Not to be confused with, Source, Implementation
pointer). Source citations resolve to Deliberation Archive records or MemBase
specifications per `DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001`.

### isolation

**Definition:** Full-lifecycle independence between the GT-KB platform and any
application built using it. The platform must be able to evolve and release on
its own cadence; an application must be deployable and lifecycle-tracked
independently of platform internals. Isolation motivates application-directory
portability, asymmetric write authority, and separate-repository topology
decisions; relocation of files into `applications/` is one consequence of
isolation, not the definition.

**Canonical alias:** lifecycle independence.

**Not to be confused with:** sandboxing or process isolation (those are runtime
concerns, not lifecycle ones); file-relocation under `applications/` (that is
one consequence — the S331 wrong-frame failure).

**Source:** `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT` (S319, 2026-04-28,
owner verbatim); `DELIB-0877` (industry-alignment critique, 2026-04-22);
"S321 owner directive: platform app non specific" (DA title); `DELIB-0879`
(`GTKB-ISOLATION-002` topology plan, 2026-04-22);
`DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (S331 owner clarification:
ZIP-portability test; scope-bound write enforcement).

**Implementation pointer:** `applications/<name>/` placement convention per
`ADR-ISOLATION-APPLICATION-PLACEMENT-001`; bridge thread family
`gtkb-isolation-016` … `gtkb-isolation-018-*`.

### session scope

**Definition:** The declared write-authority boundary for an AI session: one
of `GT-KB`, `Application`, or `GT-KB+Application` (exceptional). Scope is
declared at session start and mechanically enforced by hook-level write gating
once the enforcement layer lands.

**Not to be confused with:** `work subject` (work subject names the active
subject area; session scope names the write-authority boundary).

**Source:** `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (S331;
three-mode declaration as runtime invariant for lifecycle independence);
`DELIB-0877` (asymmetric safety model, 2026-04-22); `DELIB-0876` (durable
session work subject — adjacent governance).

**Implementation pointer:** Currently advisory-only via
`.claude/session/work-subject.json`. Mechanical enforcement is future work
tracked under a separate proposal.

### bias case

**Definition:** A failure mode in which an AI agent, given two roughly
equivalent options, reliably prefers one over another in a way that produces
wrong outcomes. The wrong option was actively chosen over the right one.

**Not to be confused with:** `salience case` (the right option was never on
the candidate list at all); "bias" used loosely for any agent failure (the
term is reserved for actively-chosen-over).

**Source:** `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (S331;
owner-articulated diagnostic distinction); `ADR-DA-READ-SURFACE-PLACEMENT-001`
(alternatives-considered analysis: Path B rejection rationale references
workaround behavior; Path D rationale uses bias-aligned framing).

**Implementation pointer:** Diagnostic frame in proposal evaluation; not a
runtime construct.

### salience case

**Definition:** A failure mode in which an AI agent does not consider a
relevant option because it is not on the natural retrieval path at the moment
of decision. The correct option was never weighed.

**Not to be confused with:** `bias case` (option weighed and rejected);
"salience" in the sense of "importance".

**Source:** `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (S331;
aware-but-unused resources indicate placement/salience problem, not
discipline problem); `ADR-DA-READ-SURFACE-PLACEMENT-001` (S331
procedural-failure context that motivated Path D selection).

**Implementation pointer:** Diagnostic frame; informs placement decisions for
resources that are aware-but-unused.

### placement

**Definition:** A design pattern in which a resource is positioned on a path
the agent already traverses (e.g., the always-loaded glossary, the bridge
proposal template, the session-start payload), rather than gated behind a new
behavior the agent must remember to perform. Placement is bias-aligned and
salience-aligned: it makes the resource reachable through existing
reach-patterns rather than fighting agent defaults.

**Canonical alias:** bias-aligned placement.

**Not to be confused with:** enforcement (placement makes the resource
reachable; enforcement gates a behavior). Placement and enforcement are
complementary; the design choice is which to apply when.

**Source:** `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (S331;
placement-over-coercion principle); `ADR-DA-READ-SURFACE-PLACEMENT-001`
(Phase 0; placement codified as the chosen design path).

**Implementation pointer:** Primary design lens for
`GOV-GLOSSARY-AS-DA-READ-SURFACE-001` and downstream phases.

### glossary as DA read surface

**Definition:** The architectural role assigned to
`.claude/rules/canonical-terminology.md` by
`GOV-GLOSSARY-AS-DA-READ-SURFACE-001`: the glossary is the agent-side primary
read path for prior-decision consultation; the Deliberation Archive is the
substrate the glossary cites. Direct DA semantic search is the long-tail /
audit / rationale-deep-dive path.

**Not to be confused with:** treating the glossary as a complete substitute
for the DA (it is the read path, not the substrate); treating the DA as
deprecated (it remains the rationale and provenance store).

**Source:** `GOV-GLOSSARY-AS-DA-READ-SURFACE-001` (Phase 0);
`ADR-DA-READ-SURFACE-PLACEMENT-001` (Phase 0);
`DCL-GLOSSARY-DA-CITATION-COMPLETENESS-001` (Phase 0);
`DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (S331 owner-approved
framing).

**Implementation pointer:** This entry is itself an instance of the
principle: it cites the formal artifacts that define it.

### harness

**Definition:** An AI coding harness; the runtime/identity layer that hosts
an AI model and implements roles. Examples: Claude Code (currently harness
ID `B`), Codex CLI (currently harness ID `A`). Harness identity is
installation-stable; roles attach to harnesses by owner assignment, not by
vendor.

**Canonical alias:** AI coding harness.

**Not to be confused with:** model (e.g., Opus 4.7, GPT-5.3-Codex) — a
harness hosts a model; the same model can run in different harnesses. Role
assignment (see `role assignment`) is separate from harness identity.

**Source:** `DELIB-0830` (Loyal Opposition assumes acting Prime Builder);
`DELIB-0831` (Prime/LO are portable across harnesses); `DELIB-0832` (GT-KB
installs configure Prime Builder).

**Implementation pointer:** `harness-state/harness-identities.json`;
`scripts/harness_identity.py` (identity-change CLI);
`.claude/rules/operating-role.md`.

### harness identity

**Definition:** The persistent, installation-stable ID assigned to each
installed AI coding harness on a workstation. IDs (`A`, `B`, `C`, …) are
unique and do not change after initial assignment except through an explicit
owner-requested identity change operation. Startup resolves the active
harness's identity from the persistent record before any role lookup.

**Not to be confused with:** session ID; model name; role assignment (the
role attached to the harness).

**Source:** `DELIB-0832` (GT-KB installs configure harness identity);
`DELIB-0831` (harness portability requires identity stability).

**Implementation pointer:** `harness-state/harness-identities.json`;
`python scripts/harness_identity.py set --harness-name <name>
--harness-id <id> --owner-requested`.

### role assignment

**Definition:** The binding of an AI coding harness to a role (Prime Builder
or Loyal Opposition). The owner assigns the Prime Builder role; the bridge
counterpart is always Loyal Opposition. The role map records one role per
harness ID. Switching a harness to Prime Builder demotes all other recorded
harnesses to Loyal Opposition in the same update.

**Canonical alias:** operating role.

**Not to be confused with:** harness identity (the ID is stable; the role
attached to it can change). The role attaches to the harness ID, not to a
model, vendor name, or transient session.

**Source:** `DELIB-0830` (LO assumes acting Prime Builder); `DELIB-0831`
(Prime/LO are portable); `DELIB-0832` (installation-time role
configuration).

**Implementation pointer:** `harness-state/role-assignments.json`;
`.claude/rules/operating-role.md`; `.claude/rules/prime-builder-role.md`;
`.claude/rules/loyal-opposition.md`.

### bridge thread

**Definition:** The multi-version conversational unit between Prime Builder
and Loyal Opposition on a single topic. A bridge thread is identified by a
kebab-case slug and consists of an ordered sequence of versioned files
(`bridge/<slug>-001.md`, `-002.md`, …) plus a single entry in
`bridge/INDEX.md`. The thread terminates at `VERIFIED` or owner-directed
retirement.

**Not to be confused with:** bridge file (a single version within a thread);
bridge document (the full version chain).

**Source:** `GOV-FILE-BRIDGE-AUTHORITY-001` (live bridge index authority).

**Implementation pointer:** `bridge/<slug>-NNN.md`; `bridge/INDEX.md`;
`.claude/rules/file-bridge-protocol.md`.

### GO / NO-GO / VERIFIED

**Definition:** The terminal verdicts in the file-bridge protocol, set by
Loyal Opposition. `GO` approves a `NEW` or `REVISED` proposal for
implementation. `NO-GO` requires Prime Builder revision. `VERIFIED` is dated
evidence that an implementation report has been verified against the linked
specifications. `NEW` (Prime-set, fresh proposal) and `REVISED` (Prime-set,
after a NO-GO) are upstream Prime-side states.

**Not to be confused with:** test pass/fail (a single test result); spec
status fields like `specified`, `implemented`, `verified` (those are MemBase
spec lifecycle states, distinct from bridge verdicts).

**Source:** `GOV-FILE-BRIDGE-AUTHORITY-001`.

**Implementation pointer:** Verdict lines in `bridge/<slug>-NNN.md` and the
corresponding `bridge/INDEX.md` entry; `.claude/rules/file-bridge-protocol.md`
§ Statuses.

### Loyal Opposition advisory

**Definition:** A Codex-initiated bridge entry that delivers an advisory
recommendation to Prime Builder, distinct from a Prime-initiated proposal.
An LO advisory is filed at `bridge/<slug>-001.md` with status `NO-GO`
(deliberate) and a `bridge_kind: loyal_opposition_advisory` header. It tasks
Prime Builder with filing a normal implementation proposal that converts the
advisory into scoped, testable GT-KB work.

**Not to be confused with:** an LO review verdict on a Prime proposal (those
carry GO/NO-GO/VERIFIED against an existing Prime-filed
`NEW`/`REVISED`/post-implementation report).

**Source:** `GOV-FILE-BRIDGE-AUTHORITY-001`.

**Implementation pointer:** `bridge_kind: loyal_opposition_advisory` header
field; precedent bootstrap pattern at
`bridge/gtkb-canonical-terminology-system-context-model-advisory-2026-05-07-001.md`.

### applicability preflight

**Definition:** The mandatory mechanical bridge gate that checks a bridge
proposal/report's `Specification Links` section against
`config/governance/spec-applicability.toml` for cross-cutting specs triggered
by the proposal's path or content. The gate emits a packet hash that LO
verdicts cite. Returns `preflight_passed: false` when required cross-cutting
specs are missing.

**Not to be confused with:** `clause preflight` (a finer-grained sibling
that checks ADR/DCL clause-level evidence, not just citation presence).

**Source:** `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (the
constraint the gate enforces).

**Implementation pointer:**
`python scripts/bridge_applicability_preflight.py --bridge-id <id>`;
`.claude/rules/file-bridge-protocol.md` § Mandatory Pre-Filing Preflight
Subsection.

### clause preflight

**Definition:** The mandatory companion preflight that asks, for each
ADR/DCL clause registered in `config/governance/adr-dcl-clauses.toml`,
whether the bridge proposal/report shows evidence satisfying the clause.
Emits an exit-5 blocking gate when any `must_apply` clause with both
`severity = "blocking"` and `enforcement_mode = "blocking"` lacks satisfying
evidence and is not explicitly owner-waived.

**Not to be confused with:** `applicability preflight` (citation presence
only). Clause preflight is finer-grained: it inspects clause-level evidence.

**Source:** `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (the
constraint the gate enforces).

**Implementation pointer:**
`python scripts/adr_dcl_clause_preflight.py --bridge-id <id>`;
`--report-only` is diagnostic only.

### bridge compliance gate

**Definition:** A `PreToolUse` Write hook
(`.claude/hooks/bridge-compliance-gate.py`) that fails the Write of bridge
proposals/reports lacking required protocol elements. Currently enforces the
`Owner Decisions / Input` section requirement when the proposal/report
depends on owner approval.

**Not to be confused with:** the applicability/clause preflight tools (those
are reviewer-run gates; the compliance gate is author-side at Write time).

**Source:** `SPEC-AUQ-POLICY-ENGINE-001` (deterministic policy engine that
the gate participates in);
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (Owner Decisions /
Input section is a linkage requirement).

**Implementation pointer:** `.claude/hooks/bridge-compliance-gate.py`
registered on `PreToolUse(Write|Edit)`;
`.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input
Section Gate.

### scanner-safe-writer

**Definition:** A credential-scan PreToolUse hook that scans Write/Edit
content against the canonical credential catalog
(`CREDENTIAL_PATTERNS + BASH_EXTRAS`, PII excluded) and blocks writes
containing credential-shaped spans. The hook applies to direct Write/Edit
tool calls; helper scripts that bypass the Write tool require their own scan
implementation.

**Not to be confused with:** the bridge-propose helper's internal credential
scan (a separate implementation of the same patterns for helper-mediated
writes).

**Source:** `DELIB-0687` (VERIFIED Credential Scan Narrowing
Post-Implementation Verification — establishes the canonical credential
pattern set); `GOV-ARTIFACT-APPROVAL-001` (credential safety as part of the
formal-artifact-approval discipline).

**Implementation pointer:** `.claude/hooks/scanner-safe-writer.py`;
`.claude/skills/bridge-propose/SKILL.md` (helper-side scan).

### owner-decision tracker

**Definition:** A `Stop`-mode hook
(`.claude/hooks/owner-decision-tracker.py`) that detects prose decision-ask
patterns in agent output and refuses turn-end when no `AskUserQuestion` tool
call occurred in the same turn. Records detected questions in
`memory/pending-owner-decisions.md`.

**Not to be confused with:** the `bridge compliance gate` (Write-time hook
on proposals); the `AskUserQuestion` tool itself (the tracker enforces use
of the tool, not the tool itself).

**Source:** `SPEC-AUQ-POLICY-ENGINE-001` (central deterministic policy
engine returning canonical outcomes); `SPEC-AUQ-NO-LLM-CLASSIFIER-001`
(deterministic-only; no LLM classifiers).

**Implementation pointer:** `.claude/hooks/owner-decision-tracker.py`
registered on `Stop`. `memory/pending-owner-decisions.md` is the durable
record.

### prose decision-ask pattern

**Definition:** A pattern class (regex-detectable) in agent output that
resembles asking the owner for a decision in prose rather than via
`AskUserQuestion`. The owner-decision tracker's `PROSE_DECISION_PATTERNS`
constant defines the patterns. When detected without an accompanying
`AskUserQuestion` call in the same turn, the tracker blocks turn-end.

**Not to be confused with:** factual reporting that mentions pending
decisions (those are status updates, not asks); status-update questions
like a single `?`.

**Source:** `SPEC-AUQ-NO-LLM-CLASSIFIER-001` (deterministic patterns, not
LLM classification); `SPEC-AUQ-POLICY-ENGINE-001` (engine that consumes the
patterns).

**Implementation pointer:** Pattern definitions in
`.claude/hooks/owner-decision-tracker.py`. Avoid quoting matched fragments
verbatim in prose to prevent recursive re-firing.

### AskUserQuestion

**Definition:** The Claude Code tool that presents a structured question to
the owner with 2-4 mutually-exclusive options, producing a clickable popup
that captures the answer inline. Per the AUQ-only enforcement stack, this
is the only valid channel for collecting owner decisions in scope
(approvals, waivers, priority choices, formal artifact approvals,
requirement clarifications, destructive actions, deployments, blocking
owner decisions).

**Canonical alias:** AUQ.

**Not to be confused with:** prose decision-ask patterns (anti-patterns);
status-update reports (factual, not decision-asking).

**Source:** `SPEC-AUQ-POLICY-ENGINE-001`; `SPEC-AUQ-NO-LLM-CLASSIFIER-001`.

**Implementation pointer:** Claude Code built-in tool. Codex parity is
forward-compatible per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`. Mechanical
enforcement via `.claude/hooks/owner-decision-tracker.py`.

### operating model

**Definition:** The canonical operating-model artifact for GT-KB at
`.claude/rules/operating-model.md`. Carries rule-cited soft authority:
cited by `.claude/rules/loyal-opposition.md` and `AGENTS.md` as the
operating-model reference; its terminology and framing are the alignment
baseline for future remediation work. No hook or test mechanically enforces
compliance with this artifact's text.

**Not to be confused with:** an architectural specification (the
operating-model is current how-it-works narrative; specifications are
what-must-do constraints); a vision document.

**Source:** `DELIB-S324-OM-DELTA-0001-CHOICE` (LO authority over
requirements); `DELIB-S324-OM-DELTA-0003-CHOICE`
(application/project/platform/hosted-application terminology);
`DELIB-S324-OM-DELTA-0004-CHOICE` (backlog ordering semantics).

**Implementation pointer:** `.claude/rules/operating-model.md`. Future
changes require an owner-approved bridge proposal and a
formal-artifact-approval packet.

### work subject

**Definition:** The startup-payload concept that names the active subject
area of a session: `gtkb_infrastructure` (the default; owner direction
interpreted as GroundTruth-KB platform work) or `application` (owner
direction interpreted as work on a named adopter/demo application). The
work subject is recorded in `.claude/session/work-subject.json` and is set
by owner commands at session start.

**Canonical alias:** active work subject.

**Not to be confused with:** `session scope` (the write-authority boundary;
subject names what's being worked on, scope names which paths can be
written). Bridge role slot and harness topology are separate dimensions in
the same state file.

**Source:** `DELIB-0876` (durable session work subject);
`DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (S331 distinction
between work subject and session scope).

**Implementation pointer:** `.claude/session/work-subject.json`. Owner
commands: `work subject GT-KB`, `application mode`, `agent red mode`.

### smart poller

**Definition:** The verified bridge-poller automation that scans
`bridge/INDEX.md` periodically and dispatches the appropriate harness when
a recipient's actionable queue signature changes. The smart poller is
monitoring/dispatch infrastructure only; `bridge/INDEX.md` remains the
canonical workflow state.

**Not to be confused with:** the retired `OS poller` class (halted
2026-04-25 per owner directive). The smart poller is the current canonical
automation path; the OS poller class must not be re-enabled as a
substitute.

**Source:** `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` (smart poller spawns
headless harness instances when actionable);
`DCL-SMART-POLLER-AUTO-TRIGGER-001` (smart poller auto-triggers harness
when work waits); `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` (opt-out
when functional); `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION` (spawn
to notify architecture); `DELIB-S321-SMART-POLLER-AUTO-TRIGGER` (S321
owner directive).

**Implementation pointer:** Windows scheduled task `GTKB-SmartBridgePoller`;
lock at `.gtkb-state/bridge-poller/bridge-poller-runner.lock`; runner
`groundtruth-kb/scripts/bridge_poller_runner.py`.

### OS poller

**Definition:** The retired bridge-poller class (Windows scheduled tasks
`AgentRedFileBridgeIndexScan-*`, `AgentRedBridgeLivenessAlert`,
`AgentRedPollerLivenessWatcher`; the foreground watchdog; the
`.claude/hooks/poller-freshness.py` hook; the in-session `CronCreate`
poller). All members of this class were halted 2026-04-25 per owner
directive after a 10x session token-cost regression and must not be
re-enabled as a substitute for the smart poller.

**Not to be confused with:** `smart poller` (the verified replacement;
canonical when healthy).

**Source:** `DELIB-S319-SMART-POLLER-POLICY-CLARIFICATION` (covers
OLD-poller halt context).

**Implementation pointer:** Listed in `.claude/rules/bridge-essential.md`
§ Operational Mode for do-not-re-enable reference. Re-enabling requires
explicit owner approval and the cost/benefit analysis required by
`bridge-essential.md` § Re-Enabling Pollers.

### doctor

**Definition:** The GT-KB diagnostic surface (typically invoked as
`gt platform doctor` or equivalent) that runs structured health checks
against platform infrastructure: smart-poller liveness, bridge state,
scaffold drift, KB integrity, dashboard reachability, and other configured
checks. The doctor is the canonical predicate for several rule-cited
conditions.

**Not to be confused with:** test runs (pytest, ruff, etc.);
release-candidate gate (`scripts/release_candidate_gate.py`).

**Source:** `SPEC-DA-DOCTOR-CHECK` (doctor bridge-thread coverage check);
`SPEC-DSI-DOCTOR-CHECK-001` (doctor invariant reporting
spec-derivation-gate alignment).

**Implementation pointer:** `groundtruth-kb/` doctor implementation.
Specific checks: `_check_smart_bridge_poller`, `_check_bridge_poller`,
scaffold drift, etc.

### release manifest

**Definition:** A versioned enumeration of the deployable components that
constitute a tagged release of the GT-KB platform or a hosted application.
The manifest accompanies the release tag and identifies constituent
component versions so that the release can be reproduced, rolled back, or
audited.

**Not to be confused with:** a release-readiness report (evidence that a
build is safe to deploy; the manifest is the inventory of what's in the
build); a deployment record (post-deployment audit; the manifest is
build-time).

**Source:** `GOV-RELEASE-READINESS-GOVERNED-TESTING-001` (production
release readiness requires governed test evidence; release manifest is the
inventory anchor for that evidence).

**Implementation pointer:** Implementation is intended-but-partial as of
2026-04-30 per `.claude/rules/operating-model.md` §3. Future formal spec
under `GOV-RELEASE-MANIFEST-README-001` (candidate; not yet inserted).

### deliberation harvest

**Definition:** The DA write-side pipeline that captures session content
(LO reports, bridge threads, post-implementation reports, owner decisions)
into the Deliberation Archive table in MemBase plus the ChromaDB semantic
index. Runs as part of session wrap.

**Not to be confused with:** the Deliberation Archive itself (the
destination); direct DA queries (the read-side counterpart).

**Source:** `SPEC-DA-HARVEST-INCLUSION`; `SPEC-DA-HARVEST-EXCLUSION`;
`SPEC-DA-MECHANICAL-ENFORCE`; `SPEC-DA-RETROACTIVE-SWEEP`.

**Implementation pointer:** `python scripts/harvest_session_deliberations.py`;
`.claude/rules/deliberation-protocol.md` § When To Archive Deliberations.

### formal-artifact-approval packet

**Definition:** The per-artifact owner-approval evidence record stored at
`.groundtruth/formal-artifact-approvals/<date>-<artifact-id>.json`,
required before a formal artifact (GOV/ADR/DCL/PB/SPEC/narrative-artifact/
deliberation) is inserted into MemBase or written to a protected file.
Required fields include `artifact_type`, `artifact_id`, `action`,
`full_content`, `full_content_sha256`, `presented_to_user=true`,
`transcript_captured=true`, `explicit_change_request`, `changed_by`,
`change_reason`, `approved_by=owner`. The
`formal-artifact-approval-gate.py` and `narrative-artifact-approval-gate.py`
PreToolUse hooks gate the write on packet presence + matching content
hash.

**Canonical alias:** approval packet.

**Not to be confused with:** the bridge GO verdict (a bridge GO authorizes
Prime to proceed to per-artifact approval collection; it does not replace
the per-artifact packet).

**Source:** `GOV-ARTIFACT-APPROVAL-001`; `PB-ARTIFACT-APPROVAL-001`;
`DCL-ARTIFACT-APPROVAL-HOOK-001`.

**Implementation pointer:**
`.groundtruth/formal-artifact-approvals/<date>-<artifact-id>.json`. Env
vars `GTKB_FORMAL_APPROVAL_PACKET` or
`GTKB_NARRATIVE_ARTIFACT_APPROVAL_PACKET` reference the packet at hook
check time. `config/governance/narrative-artifact-approval.toml` defines
the protected-path patterns for narrative artifacts.

### canonical artifact

**Definition:** An artifact that has been formalized into MemBase or a
protected narrative-authority file with matching
formal-artifact-approval-packet evidence. Includes MemBase rows for GOV /
ADR / DCL / PB / SPEC / REQ types, Deliberation Archive records, and the
protected narrative artifacts at `.claude/rules/*.md`, `AGENTS.md`,
`CLAUDE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE-ARCHITECTURE.md`, and
`memory/work_list.md`. Canonical artifacts are subject to append-only
versioning discipline.

**Not to be confused with:** operational state files (`MEMORY.md`,
`memory/*.md` topic files, `.claude/session/*.json`) — those are
notepad-tier per ADR-0001, high-churn, not canonical.

**Source:** `GOV-ARTIFACT-APPROVAL-001`; `PB-ARTIFACT-APPROVAL-001`.

**Implementation pointer:** Canonical artifacts are gated by
formal-artifact-approval-gate.py (MemBase rows) or
narrative-artifact-approval-gate.py (protected `.md` files) at write time.

### interrogative default

**Definition:** Prime Builder's default posture toward owner factual
claims about GT-KB capabilities, implementation, history, or state: verify
the claim against the existing evidence trail (rule files, KB records, git
history, runtime artifacts) before treating it as canonical input. Where
the statement is incorrect or partial, surface the correction with
evidence; offer the corrected statement as a candidate specification. The
interrogative default does NOT apply to claims the agent cannot verify
(e.g., owner-stated business facts, customer information, organizational
decisions).

**Not to be confused with:** disagreement or pushback in general — the
interrogative default is specifically about verifying owner factual claims
about GT-KB itself.

**Source:** `DELIB-S324-PB-INTERROGATION-DIRECTIVE` (S324 owner directive
establishing the interrogative default).

**Implementation pointer:** Posture, not runtime construct. Applied by
Prime Builder during owner-input processing per
`.claude/rules/operating-model.md` §1 and
`.claude/rules/prime-builder-role.md`.

### specify-on-contact

**Definition:** Governance principle (CLAUDE.md governance index entry
GOV-06): when previously unspecified code is touched, it becomes
controlled. Mirrored at the terminology layer by
`DCL-CONCEPT-ON-CONTACT-001`. Touching a code surface that lacks a
specification triggers specification creation; touching a load-bearing
concept that lacks a glossary entry triggers glossary promotion (per the
DCL).

**Not to be confused with:** the GOV-09 owner-input classification rule
(specification language triggers spec-first workflow);
`DCL-CONCEPT-ON-CONTACT-001` is parallel, not replacement.

**Source:** `DCL-CONCEPT-ON-CONTACT-001` (Phase 0; terminology-layer
mirror that explicitly references the GOV-06 specify-on-contact
precedent).

**Implementation pointer:** Specify-on-contact at the code layer is
enforced through normal Prime Builder spec-first discipline at code-touch
time. The terminology-layer mirror (`DCL-CONCEPT-ON-CONTACT-001`) is
staged across Phase 3 (Stage A) and Phase 6 (Stages B and C).

---

