<!--
THIS FILE IS A PROJECTION, NOT CANONICAL.
Projected from the neutral harness baseline by the GT-KB projection engine.
Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
`gt harness project goose`. If a needed change cannot be made through
the baseline and re-projection, file a work item against the projector
(GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
-->
# File Bridge Protocol

The bridge between Prime Builder and Loyal Opposition uses bridge state
bridge state plus a shared directory of versioned markdown audit files.

> Bridge state and status-bearing numbered bridge files are canonical.

## Directory

`bridge/` at project root. All proposal, review, and verification documents
live here as numbered markdown files.

## Mandatory Root Boundary Gate

Every bridge proposal, review, implementation report, and verification must
comply with `.goose/rules/project-root-boundary.md`: all active GT-KB files and
artifacts must remain within `E:\GT-KB`; all GT-KB application files must remain
within `E:\GT-KB\applications\`. Agent Red is the reference adopter application
for GT-KB at `applications/Agent_Red/`; its subtree is in scope for GT-KB bridge
review. Unqualified GT-KB tooling references must not resolve
silently to Agent Red's lifecycle-independent repository or CI surfaces. There
are no exceptions to the root-containment rule. A bridge item that depends on a
live path outside those roots is `NO-GO`.

## Mandatory Specification Linkage Gate

Every implementation proposal must include a `Specification Links` section
before it can receive `GO`. The section must cite every relevant governing
specification, rule, ADR, DCL, proposal standard, or other durable specification
artifact that constrains the proposed implementation. A proposal with no linked
specification surface is invalid and must receive `NO-GO`.

Loyal Opposition MUST reject all implementation proposals that are not linked to
specifications. Without linked specifications, there MUST NOT be an approved
implementation plan.

The proposal must also state how the proposed tests derive from those linked
specifications. Loyal Opposition review must independently check the list for
omissions. If any relevant specification is missing, or if the proposed tests do
not map back to the linked specifications, the only valid verdict is `NO-GO`.

## Mandatory Implementation Proposal Metadata

Implementation proposals that request source, test, script, hook,
configuration, deployment, repository-state, or KB-mutation work must include:

1. `target_paths` metadata listing the concrete files or globs authorized for
   implementation.
2. A `Requirement Sufficiency` subsection with exactly one operative state:
   `Existing requirements sufficient` or
   `New or revised requirement required before implementation`.
3. A specification-derived verification plan mapping the linked requirements to
   tests or verification commands.

## Mandatory Pre-Filing Preflight Subsection

Before writing or revising any bridge proposal at
`bridge/<descriptive-name>-NNN.md`, Prime Builder MUST:

1. Read `config/governance/spec-applicability.toml` to know which
   cross-cutting specs are triggered by the planned proposal text (path,
   content, doc-name regex matrix).
2. KB-search for cross-cutting governance specs governing the *artifact type*
   the proposal will create or modify (e.g., a DELIB insert triggers
   `GOV-ARTIFACT-APPROVAL-001`; a bridge proposal itself triggers the
   always-blocking cross-cutting bridge-governance set).
3. Cite every triggered required + advisory spec in the proposal's
   `Specification Links` section.
4. After drafting and before filing, run:

   ```
   python scripts/bridge_applicability_preflight.py --bridge-id <intended-bridge-id>
   ```

   The expected result is `preflight_passed: true`,
   `missing_required_specs: []`, `missing_advisory_specs: []`. Any non-empty
   `missing_*_specs` list is a self-detected defect; revise the proposal before
   filing or before re-saving the file.

5. Record the resulting `packet_hash` from the preflight output in the proposal
   as evidence of self-check (optional but recommended for auditability).

Loyal Opposition MUST issue NO-GO on any bridge proposal whose
preflight on its own operative file does not pass. The Loyal Opposition NO-GO message must
include the offending `missing_*_specs` list.

If the preflight cannot resolve the intended operative file from bridge state
state and the numbered bridge file chain, treat that as a tooling defect and
repair the resolver before relying on the result.

This subsection operationalizes
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (proposal must cite all
relevant specs) and is mechanically enforced by
`.goose/hooks/bridge-compliance-gate.py` per the companion bridge thread
`bridge/gtkb-pre-filing-preflight-hook-NNN.md`. Until the hook upgrade lands,
this subsection is rule-cited soft authority; the Loyal Opposition NO-GO at review time
remains the reliable feedback loop.

## Mandatory Pre-Drafting Claim Step

Before substantive drafting begins on any bridge thread (NEW, REVISED, or
post-implementation report), Prime Builder MUST acquire a work-intent claim via:

```text
python scripts/bridge_claim_cli.py claim <slug>
```

The claim establishes a holder record at `.gtkb-state/work-intent/<slug>.json`
that other Prime sessions (interactive or auto-dispatched) consult before
drafting. A claim is required even when no other session is currently working
the thread; the claim is the audit-trail evidence that THIS session committed
to the work.

Claim exit code 0 authorizes drafting. Exit code 2 (held by another session)
requires Prime to either select a different thread or, if the holder appears
stale, surface the situation via AskUserQuestion before forcing through.

The bridge-compliance-gate PreToolUse hook ENFORCES this rule at file-Write
time: a Write to `bridge/<slug>-NNN.md` without a prior claim by this session
is blocked with a clear error citing this rule.

Claim release happens automatically when the helper completes a successful
Write, or via TTL expiry (10 minutes default), or via explicit `release` for
abandoned work.

## Mandatory Specification-Derived Verification Gate

An implementation cannot receive `VERIFIED` unless the verification procedure
creates or identifies tests derived from the specifications linked in the
implementation proposal and executes those tests against the implementation.

The post-implementation report must include:

- the linked specifications carried forward from the proposal;
- a spec-to-test mapping showing which tests cover which specification clauses
  or acceptance criteria;
- the exact commands used to execute those tests;
- the observed results.

If a linked specification has no executed test coverage, Loyal Opposition must
issue `NO-GO` unless the owner explicitly approves a documented waiver for that
specific specification and risk.

## Mandatory VERIFIED Commit-Finalization Gate

The work item becomes terminal at the **work-product commit**. The `VERIFIED`
verdict is the post-commit signal that the verified work is already committed.

Loyal Opposition performs finalization in this order:

1. Verify the work product against the linked specifications.
2. Create the local git commit containing the verified implementation and report
   paths. The commit message MUST cite every work item it retires, in the form
   `(WI-NNNN)`.
3. Only after that commit succeeds, write the `VERIFIED` verdict as the next
   numbered bridge file.

The `VERIFIED` verdict artifact is **excluded** from the commit created in step
2. It is written afterward, and it carries the resulting commit SHA as
post-commit evidence.

Emitting the verdict releases the locks and holds associated with the work item
and the bridge thread, and notifies the platform. It is bridge notification and
audit-trail hygiene; the commit in step 2 is what makes the work terminal.

If the commit in step 2 fails, Loyal Opposition fails closed and writes no
terminal `VERIFIED` file.

A tool or workflow that writes `VERIFIED` before the work-product commit, or
that places the verdict inside that commit, is defective and must be repaired
rather than worked around.

Reviewers may run the verdict helper without finalization flags to seed Prior
Deliberations, then review and prune the draft body before finalization.

### Pre-File Code-Quality Gates (lint AND format are separate)

Before filing a post-implementation report whose changes include Python files,
Prime Builder MUST run BOTH repo-native code-quality gates on the changed files
and report the results:

- `ruff check <changed.py>` (lint), and
- `ruff format --check <changed.py>` (formatting).

These are SEPARATE gates: code that passes `ruff check` can still fail
`ruff format --check`. Loyal Opposition verification and CI both enforce
`ruff format --check`, so a report filed without it risks a `NO-GO` solely on
formatting. The `scripts/check_ruff_format.py` guardrail (active via
`.githooks/pre-commit`) enforces the format gate at commit time as a backstop;
the pre-file run above is what prevents the verification-time `NO-GO`. Resolve a
ruff-capable interpreter deterministically — the project venv has `ruff` even
when the default `python` does not.

## Mandatory Applicability Preflight Gate

Before Loyal Opposition issues `GO` or `VERIFIED`, it must run the mechanical
bridge applicability preflight:

```text
python scripts/bridge_applicability_preflight.py --bridge-id <document-name>
```

The generated `Applicability Preflight` section must be included in the
verdict file. `GO` and `VERIFIED` are valid only when the preflight reports
`missing_required_specs: []`. If the preflight reports missing required
cross-cutting specifications, Loyal Opposition must issue `NO-GO` unless the
proposal or implementation report is revised to cite and satisfy those
specifications.

The applicability preflight is a mechanical floor, not a ceiling. Loyal
Opposition remains responsible for identifying relevant specifications that
are not yet represented in `config/governance/spec-applicability.toml` and
should raise omissions as findings or propose registry updates.

## Mandatory Simpler-Alternative Section In GO Verdicts

Every `GO` verdict must include a `## Simpler Alternative Considered` section
naming the simpler design Loyal Opposition weighed against the approved design,
and why the approved design was preferred.

This applies the rejected-alternatives discipline that ADRs already carry to
routine approvals, so a `GO` records what was weighed rather than only what was
accepted. It extends the same pattern as the mandatory `Applicability Preflight`
and `Clause Applicability` sections above.

Scope: `GO` verdicts only. `NO-GO` is already a rejection and needs no rejected
alternative; `VERIFIED` is post-commit evidence rather than an approval decision.

"No simpler alternative exists" is a permitted answer only when the reviewer
states what was considered and why it does not apply. A bare denial is not a
considered alternative. Mechanical enforcement can detect an absent or
placeholder section; it cannot detect an insincere one, and this section does
not claim otherwise.

Authority: `GOV-FILE-BRIDGE-AUTHORITY-001`; owner AUQ 2026-08-21 Item D;
WI-6742.

## Clause-Test Preflight (Advisory; Slice 1)

A companion preflight surface, `scripts/adr_dcl_clause_preflight.py`, asks
a finer-grained question than the applicability preflight above: for each
ADR/DCL clause registered in `config/governance/adr-dcl-clauses.toml`, does
the bridge proposal/report show evidence that satisfies the clause? It
emits a "Clause Applicability" section listing each clause with its
applicability verdict (`must_apply` / `may_apply` / `not_applicable`) and,
for `must_apply` clauses, whether satisfying evidence was found.

**Slice 1 is advisory only.** The clause-test preflight is NOT a blocking
gate. It always exits 0 — even when blocking-severity clauses lack
satisfying evidence. Reviewers MAY consult its output during review, but
`GO` and `VERIFIED` decisions are not yet conditioned on its result. Slice 2
of `gtkb-adr-dcl-clause-test-enforcement` is the future bridge thread that
will promote selected blocking clauses to a hard gate, after Slice-1
feedback has tightened the applicability triggers and evidence patterns.

Source: `bridge/gtkb-adr-dcl-clause-test-enforcement-001.md` (GO at -002).

## File Naming

`{descriptive-name}-{NNN}.md`

- `descriptive-name`: kebab-case description of the proposal or review topic
- `NNN`: zero-padded version number starting at 001, incremented for each
  revision or review response

Examples:
- `widget-refactor-001.md` (Prime's initial proposal)
- `widget-refactor-002.md` (Loyal Opposition review with GO or NO-GO)
- `widget-refactor-003.md` (Prime's revision after NO-GO)

## Bridge State Publication

Bridge state is the canonical coordination state. New bridge writes must go through the governed bridge
writer path, which publishes bridge state and writes the status-bearing
numbered bridge file.

## Statuses

Canon section 6 fixes the vocabulary at exactly twelve. The code of record is
`CANONICAL_STATUSES` in `groundtruth_kb.bridge.vocabulary`, the single source
named by `SPEC-BRIDGE-STATUS-PHASE-DISTINCT-001` clause 5.

| Status | Set by | Meaning |
|--------|--------|---------|
| NEW | Prime Builder | Fresh implementation proposal. Addressed to Loyal Opposition. |
| REVISED | Prime Builder | Revised implementation proposal after a NO-GO. Addressed to Loyal Opposition. |
| READY | Prime Builder | Implementation report, valid only after GO. Must carry `bridge_kind: implementation_report`, which the governed writer validates. READY cannot begin a thread. It replaces the historical use of NEW for post-implementation reports. |
| VERDICT-REJECTED | Prime Builder | Rejects a governance-noncompliant, Prime-addressed Loyal Opposition verdict and routes a fresh Loyal Opposition correction. |
| BLOCKED | Prime Builder | The typed refusal a headless session returns instead of a NEW proposal when the work item's parent project reads `not authorized` at filing time. Begins a thread and may occupy no other position; requests no review; not dispatchable; carries the project id, the observed authorization value, and the time of the read. An interactive session asks the owner instead. |
| GO | Loyal Opposition | Approves a proposal for implementation. Addressed to Prime Builder. |
| NO-GO | Loyal Opposition | Rejects a proposal and requires revision. Addressed to Prime Builder. It has exactly one form. |
| NOT-READY | Loyal Opposition | Rejects an implementation report and requires a corrected report. The report-phase counterpart of NO-GO, so that no token is lawful in both the proposal phase and the report phase. |
| SUPERSEDED | Loyal Opposition | Closes a non-terminal chain whose subject no longer exists: retired by canon or by formal record, absorbed into other work, or already landed elsewhere. Asserts nothing about verification. Must cite the canonical evidence that the subject is gone and name the carrier of any residual work. Terminal and not dispatchable; never authored while another context holds a work-intent claim on the chain. |
| VERIFIED | Loyal Opposition | Records review completion for the exact reviewed bytes. Terminal for that snapshot and not dispatchable; only a fresh Loyal Opposition VERIFIED over the exact final bytes may follow it, per section 7. |
| WITHDRAWN | Prime Builder | Valid only before GO. Terminal and not dispatchable. |
| ADVISORY | Either role | Informational at any time. Not dispatchable, and not part of an implementation lifecycle. |

NO-ACTION and DEFERRED are obsolete and invalid. New writes reject both.
Historical files bearing them are inert historical text: they confer no
routing, lifecycle, claim, lease, or implementation state, are never rewritten
or normalized, and no alias or crosswalk exists.

## Post-Verdict Transition Table

The single authoritative transition table is the `TRANSITIONS` constant in
`groundtruth_kb.bridge.vocabulary` (the code of record). This section renders
that table; the doc-code consistency test
`platform_tests/scripts/test_bridge_protocol_transition_table_consistency.py`
asserts the rendering matches the constant.

The successor relation is a pure function of the current status. No entry
consults thread history, per `SPEC-BRIDGE-STATUS-PHASE-DISTINCT-001` clause 4.

| Previous status | Allowed successors |
|---|---|
| BLOCKED | NEW, WITHDRAWN |
| NEW | GO, NO-GO, WITHDRAWN, SUPERSEDED |
| REVISED | GO, NO-GO, WITHDRAWN, SUPERSEDED |
| GO | READY, VERDICT-REJECTED, SUPERSEDED |
| READY | VERIFIED, NOT-READY, SUPERSEDED |
| NOT-READY | READY, VERDICT-REJECTED, SUPERSEDED |
| NO-GO | REVISED, WITHDRAWN, VERDICT-REJECTED, SUPERSEDED |
| VERDICT-REJECTED | GO, NO-GO, NOT-READY, SUPERSEDED |
| VERIFIED | VERIFIED |
| ADVISORY | ADVISORY |

`WITHDRAWN` and `SUPERSEDED` are terminal and have no successors, so they carry no row.

`NO-GO` has exactly one form. It is authored by Loyal Opposition, rejects a
proposal, and routes to Prime Builder for `REVISED`. A failed project commit is
canonical finalization state, never a verdict: it returns the affected work item
to Loyal Opposition for fresh verification without inserting any
Dispatcher-authored bridge status. `NO-GO -> READY` is invalid, and READY is
absent from the row accordingly.

`VERIFIED` is terminal for its exact reviewed snapshot. When canonical
project/work-item state records a pre-commit verified-byte change or a failed
project commit, Loyal Opposition may append a fresh `VERIFIED` over the exact
final bytes; nothing else may follow it.

Report rejection is never `NO-GO`; it is `NOT-READY`.

`VERDICT-REJECTED` may immediately follow only an agent-authored,
Prime-addressed Loyal Opposition `GO`, `NO-GO`, or `NOT-READY`. It may never
follow `VERIFIED`, `WITHDRAWN`, `SUPERSEDED`, `BLOCKED`, or `ADVISORY`: those
are non-dispatchable or terminal, and no Prime Builder receives or rejects them.

A later `ADVISORY` on the same advisory thread is the latest advisory message.
No other status may follow `ADVISORY`. Work derived from an advisory begins a
fresh `NEW` chain that cites it.

`SUPERSEDED` may follow any non-terminal status, because a subject can be
retired at any point in a chain's life and the chain must be closable when it
is. It may never follow `VERIFIED`, `WITHDRAWN`, `ADVISORY`, or `BLOCKED`.
Because it may follow a Prime-addressed status, the authoring Loyal Opposition
must show the chain is not live: no work-intent claim held by another context.

`BLOCKED` begins a thread and may occupy no other position, because the
authorization check happens only before a NEW proposal and a change in project
authorization does not affect a chain already initiated. It is followed only by
`NEW` or `WITHDRAWN`.

Chains committed before this vocabulary took effect may encode superseded
pairs, most commonly `GO -> NEW` from the retired practice of filing a report
as a second `NEW`. Those are accepted when reading committed history only, via
`HISTORICAL_TRANSITIONS` in the same module. They confer no write authority.

## Review Independence Boundary

Formal bridge review must come from a **different model session context** than
the one that authored or implemented the artifact under review — shared context
means the verifier likely inherits the same assumptions and errors. Full
normative block: `config/agent-control/SESSION-STARTUP-INDEX.md` §
Session-context review independence (normative).

Bridge review independence is determined by session context, not by harness ID
or durable registry role (routing labels only). A review or verification is
invalid when the reviewer session context equals the bridge artifact author's
`author_session_context_id`, or when the author session metadata is missing or
unreadable under the dispatcher fail-closed rules.

Interactive sessions remain bound to the owner-declared resolved role for that
session. An interactive session must not switch from Prime Builder to Loyal
Opposition, or from Loyal Opposition to Prime Builder, merely because the same
harness has a durable assignment or could be selected by headless dispatch.

## Body Status-Token Rule

Versioned bridge files (`bridge/<slug>-NNN.md`) MUST begin with a canonical
status token on the first non-blank line: one of the twelve statuses in
`CANONICAL_STATUSES` (`NEW`, `REVISED`, `READY`, `VERDICT-REJECTED`, `GO`,
`NO-GO`, `NOT-READY`, `VERIFIED`, `WITHDRAWN`, `SUPERSEDED`, `BLOCKED`, or
`ADVISORY`). Headings and prose
follow the token. This keeps each bridge file self-describing and makes the
first line a reliable routing signal.

The rule is mechanically enforced by `.goose/hooks/bridge-compliance-gate.py`
(activated byte-for-byte from
`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`): a `Write` of a
versioned bridge file whose first non-blank line is not a recognized status
token is hard-blocked. The rule fires only on the `Write` tool (full file
content); `Edit` operations are not subject to it. Files that already exist on
disk with a non-canonical first line are grandfathered, so the rule never
retroactively breaks historical bridge files on overwrite. Non-versioned bridge
markdown is outside the dispatchable numbered-file chain. `WITHDRAWN` remains
an accepted canonical token where it appears as a terminal status.

### Complete authored heads are order-independent at the writer (WI-6538)

A bridge artifact head is COMPLETE when all three required elements - a canonical
status token, one `::init gtkb <pb|lo>` line, and one `::open <activity>` line -
are present within the first three non-blank lines, with the responder role and
activity valid for that status.

A complete head is correct in ANY order. Owner canon does not fix the order of
the three lines, and a complete-but-disordered head is not an error.

The governed writer therefore MUST preserve a complete authored head byte-for-byte.
`normalize_bridge_envelope_head` in `scripts/gtkb_bridge_writer.py` returns such
content unmodified; normalization is reserved for heads that are INCOMPLETE or
MALFORMED, which is where it materializes the missing elements. A writer that
rebuilds a complete head into a canonical order is mutating an artifact that was
never in error, and is defective.

This clause governs the writer surface only. It does not restate, relax, or
override any line-position requirement enforced elsewhere, including at the
artifact-head envelope gate; where a consumer imposes a stricter position
constraint, that constraint is owned by its own surface and is out of scope here.

Source: `GTKB-GOV-PROPOSAL-STANDARDS` Slice 1
(`DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE`; GO at
`bridge/gtkb-gov-proposal-standards-slice1-025.md`).

## VERDICT-REJECTED Status

`VERDICT-REJECTED` is a **Prime Builder-authored** rejection of a
governance-noncompliant, Prime-addressed Loyal Opposition verdict (`GO`,
`NO-GO`, or `NOT-READY`). It routes a fresh Loyal Opposition correction and is
Loyal-Opposition-actionable. It may never follow `VERIFIED`, `WITHDRAWN`,
`SUPERSEDED`, or `ADVISORY`. An `ADVISORY` thread carries no verdict to reject:
later advisory messages stay `ADVISORY`, and work derived from an advisory
begins a fresh `NEW` chain that cites it.

## Advisory Reports

**Purpose:** Advisory reports are first-class workflow state, not transport workarounds via `NO-GO@001`. They may be owner-initiated (owner asks LO to investigate a peer system) or LO-initiated (LO surfaces a finding during normal review).

**Routing:** ADVISORY entries are owner-visible informational input. They are not Prime-actionable, not Loyal-Opposition-actionable, never assigned, and non-dispatchable for headless runs. `ACTIONABLE_STATUSES_FOR_PRIME` in `groundtruth_kb.bridge.notify` is GO/NO-GO only, so `compute_actionable_pending` does not surface ADVISORY in the Prime actionable list. Manual `/bridge` scans may list them under `owner_visible`; `bridge-axis-2-surface.py` also filters non-dispatchable items, so AXIS-2 surfacing of ADVISORY status entries is a separate follow-on concern.

**Authority:** Loyal Opposition (or owner-direction) authors ADVISORY entries; Prime Builder acknowledges in an interactive session and dispositions through owner-deliberation / UAQ flows, producing one of: (a) a normal NEW implementation proposal converting the advisory (`adopt` / `adapt`), (b) an explicit deferral with documented defer-trigger, or (c) a documented rejection (`reject`).

**Expected Prime response:** cite advisory in any follow-on conversion proposal's `Prior Deliberations` and `Source advisory` fields.

**Dashboard semantics:** ADVISORY rows are NOT failed proposals; dashboard counts must distinguish them from NO-GO entries. Exact dashboard-counter behavior is owned by the sibling `gtkb-advisory-report-dashboard-counters-spec` thread.

## BLOCKED Status

`BLOCKED` is the **Prime Builder-authored** typed refusal a headless session
returns instead of a `NEW` proposal when the work item's parent project reads
`not authorized` at filing time. It begins a thread and may occupy no other
position, requests no review, is not dispatchable, and carries the project id,
the observed authorization value, and the time of the read. An interactive
session asks the owner instead. The thread continues only when Prime Builder
files `NEW` (the project is authorized) or `WITHDRAWN`.

## Prime Workflow

1. Write the proposal as `bridge/{name}-001.md` through the governed bridge
   writer path
2. Let the governed writer publish bridge state.
3. Continue working on other tasks
4. Periodically scan bridge state for GO, NO-GO, or NOT-READY
   responses; those are dispatchable implementation/revision work.
   ADVISORY is owner-visible informational input (never assigned or dispatched). Skip
   WITHDRAWN, SUPERSEDED, BLOCKED, and VERIFIED as non-actionable.
5. On GO: proceed with implementation
6. On NO-GO: read the NO-GO file, address findings, save revised file with
   incremented version, and use the governed writer to publish a REVISED state.

## Loyal Opposition Workflow

1. Periodically scan bridge state for NEW, REVISED, READY, or VERDICT-REJECTED
   entries; skip ADVISORY, WITHDRAWN, SUPERSEDED, BLOCKED, and VERIFIED as
   non-actionable for Loyal Opposition review work.
2. Process entries starting from the oldest actionable item.
3. Read the indicated file and perform the review
4. Save review findings as a new version with incremented number
5. Use the governed writer to publish the verdict state for that thread.

## Post-Implementation Verification

After Prime implements a GO'd proposal:
1. Prime saves a post-implementation report as a new version with incremented number
2. Every post-implementation report publishes as a `READY` entry through the
   governed writer, carrying `bridge_kind: implementation_report`. `READY` is
   valid only after `GO` and cannot begin a thread. It replaces the historical
   use of `NEW` for reports.
3. Loyal Opposition reviews and responds with `NOT-READY`, or records
   `VERIFIED`.
4. After a `NOT-READY`, the corrected report publishes as `READY` again — never
   `NEW` and never `REVISED`, which belong to the proposal phase. No token is
   lawful in both phases, which is the point of the READY/NOT-READY pair.

## Bridge State Maintenance

Bridge state is maintained by the governed bridge writer/reconcile
path. Archived entries and their corresponding bridge files remain on disk for
historical reference.

## Guardrails

- Both agents must read the full entry (all versions) before acting on any
  single version
- Never delete bridge files — they form the audit trail
- Use the governed bridge writer/reconcile path for state repair rather than
  hand-merging coordination data.
- bridge state is the source of truth for workflow state.

## Mandatory Owner Decisions / Input Section Gate

Implementation proposals and reports that depend on owner approval — citing Sub-slice B's AUQ-only rule (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md`), referencing AskUserQuestion answers, or otherwise indicating owner-decision scope — MUST include a non-empty `Owner Decisions / Input` section enumerating the relevant AskUserQuestion evidence.

The bridge-compliance-gate hook (`.goose/hooks/bridge-compliance-gate.py`) mechanically enforces this requirement at Write time.

The check fires conditionally — proposals that do NOT depend on owner approval (routine refactors, scaffold updates, etc.) are not affected. Loyal Opposition verdict files (lines starting with `GO`, `NO-GO`, or `VERIFIED`) are explicitly excluded because they are evidence narratives, not approval claims.

## Conventional Commits Type Discipline (Implementation Reports)

Per `bridge/gtkb-governance-hygiene-bundle-001.md` (Change B; rationale: S333 audit FINDING-P0-001 — commit `721f7c69` was labeled `chore` despite adding ~13 K LOC of net infrastructure):

Implementation reports filed for `VERIFIED` review MUST include a recommended Conventional Commits type for the eventual commit. Accepted values: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`, `build:`, `ci:`, `perf:`, `style:`. The recommendation appears in a section titled `## Recommended Commit Type` (or as part of an existing `## Files Changed` / `## Summary` section explicitly tagged `Recommended commit type:`).

Loyal Opposition validates that the recommended type matches the diff stat:

- `feat:` for net-new modules, scripts, hooks, skills, or capabilities.
- `fix:` for repairs to broken behavior with no new capability surface.
- `refactor:` for restructuring without behavior change.
- `chore:` for true maintenance-only changes (dependency bumps without code, README touches, etc.).
- `docs:` for governance/rule/runbook-only edits.
- `test:` for test-only additions.

The discipline does not mandate any specific type; it requires the choice to be declared and justified, so commit-history-driven tooling (release notes, changelogs, semantic-version inference) doesn't mis-categorize sweeping changes.

## Parked-Draft Pattern

Per `bridge/gtkb-governance-hygiene-bundle-001.md` (Change D; rationale: S333 audit FINDING-P4-001 — `bridge/gtkb-isolation-018-slice-c-docs-cluster-001.md` was committed at `cd8f27ce` without an INDEX entry, which the bridge applicability preflight tool legitimately surfaces as `ERR_NO_INDEX_ENTRY`):

A bridge file MAY be committed without becoming dispatcher-actionable when the commit message tags it as a parked draft (e.g., `... 18.C draft parked`). The applicability preflight tool should report such files as non-actionable drafts rather than live queue work.

Parked drafts are deliberate work-in-progress artifacts that must NOT trigger Loyal Opposition review until they are promoted by:

1. Publishing bridge state with status `NEW` or `REVISED`.
2. The promotion commit message explicitly states `<bridge-id>: parked draft promoted to <status>`.

Audits SHOULD identify parked drafts in their inventory phase but MUST NOT flag them as orphans without checking the originating commit message for the `parked` tag.
