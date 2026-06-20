# File Bridge Protocol

The bridge between Prime Builder and Loyal Opposition uses dispatcher/TAFE
bridge state plus a shared directory of versioned markdown audit files.

> **2026-06-15 bridge cutover note:** After WI-4510 Phase-3, TAFE-backed bridge
> state and status-bearing numbered bridge files are canonical.

## Directory

`bridge/` at project root. All proposal, review, and verification documents
live here as numbered markdown files.

## Mandatory Root Boundary Gate

Every bridge proposal, review, implementation report, and verification must
comply with `.claude/rules/project-root-boundary.md`: all active GT-KB files and
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

## Mandatory Implementation-Start Authorization Metadata

Implementation proposals that request source, test, script, hook,
configuration, deployment, repository-state, or KB-mutation work must include:

1. `target_paths` metadata listing the concrete files or globs authorized for
   implementation.
2. A `Requirement Sufficiency` subsection with exactly one operative state:
   `Existing requirements sufficient` or
   `New or revised requirement required before implementation`.
3. A specification-derived verification plan mapping the linked requirements to
   tests or verification commands.

When an implementation proposal depends on a project-scoped implementation
authorization, it should also cite machine-readable metadata lines for
`Project Authorization`, `Project`, and the applicable `Work Item`. These lines
let `scripts/implementation_authorization.py` validate that the authorization is
current, active, unexpired, tied to the cited project, and either includes the
work item or covers it through active project membership. Project authorization
metadata never broadens `target_paths` and never replaces the live latest-`GO`
requirement.

After Loyal Opposition records `GO`, Prime Builder runs:

```text
python scripts/implementation_authorization.py begin --bridge-id <document-name>
```

The resulting packet is session-local implementation-scope evidence. It must be
derived from TAFE-backed bridge state, the approved proposal file, and the GO
verdict file. It expires, fails closed on bridge status drift, and cannot
replace formal-artifact approval packets.

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

Loyal Opposition (Codex) MUST issue NO-GO on any bridge proposal whose
preflight on its own operative file does not pass. Codex's NO-GO message must
include the offending `missing_*_specs` list.

If the preflight cannot resolve the intended operative file from dispatcher/TAFE
state and the numbered bridge file chain, treat that as a tooling defect and
repair the resolver before relying on the result.

This subsection operationalizes
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (proposal must cite all
relevant specs) and is mechanically enforced by
`.claude/hooks/bridge-compliance-gate.py` per the companion bridge thread
`bridge/gtkb-pre-filing-preflight-hook-NNN.md`. Until the hook upgrade lands,
this subsection is rule-cited soft authority; Codex's NO-GO at review time
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

A `VERIFIED` verdict is a commit-finalization outcome, not a file-only bridge
status. Loyal Opposition MUST NOT leave a terminal `VERIFIED` bridge file in
the worktree unless the same local transaction creates the git commit that
contains:

- the verified implementation/report paths; and
- the new `VERIFIED` verdict artifact.

The verification helper path is:

```text
python .claude/skills/verify/helpers/write_verdict.py --slug <document-name> --body-file <reviewed-verdict-body> --finalize-verified --no-prepopulate --commit-message "<type(scope): message>" --include <verified-path> [--include <verified-path> ...]
```

Reviewers first run the helper without `--finalize-verified` when they need
Prior Deliberations seeding, then review and prune the draft. The final
`--finalize-verified` invocation uses the reviewed body. The helper writes the
next numbered verdict, stages only the declared verified path set plus that
verdict, and runs a local `git commit`. If staging or commit creation fails, the
helper removes the just-written `VERIFIED` verdict and fails closed. The verdict
file records pre-commit evidence such as intended commit subject and staged path
set; the final commit SHA is emitted by the helper after success and must not be
self-embedded in the committed verdict file.

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

After the WI-4510 Phase-3 cutover, TAFE-backed bridge state is the canonical
coordination state. New bridge writes must go through the governed bridge
writer path, which publishes dispatcher/TAFE state and writes the status-bearing
numbered bridge file.

## Statuses

| Status | Set by | Meaning |
|--------|--------|---------|
| NEW | Prime | Fresh proposal awaiting review |
| REVISED | Prime | Updated proposal after a NO-GO |
| GO | Loyal Opposition | Proposal approved for implementation |
| NO-GO | Loyal Opposition | Proposal requires changes before approval |
| VERIFIED | Loyal Opposition | Post-implementation verification passed |
| ADVISORY | Loyal Opposition | Advisory report; actionable by Prime Builder in interactive sessions to trigger owner-deliberation / UAQ disposition; non-dispatchable for headless runs (`_derive_dispatchable` returns False). NOT awaiting GO/NO-GO/VERIFIED. |
| DEFERRED | Owner | Owner-directed parked bridge state; non-actionable until the owner-directed clear/resume condition is met. |

## Review Independence Boundary

Bridge review independence is determined by session context, not by harness ID
alone. A review or verification is invalid when the reviewer session context is
the same as the bridge artifact author's `author_session_context_id`, or when
the author session metadata is missing or unreadable under the dispatcher
fail-closed rules. The same harness may author a proposal in one session and
review it in a different, unrelated session context only when the reviewer is
operating under a valid Loyal Opposition role or dispatch context.

Interactive sessions remain bound to the owner-declared resolved role for that
session. An interactive session must not switch from Prime Builder to Loyal
Opposition, or from Loyal Opposition to Prime Builder, merely because the same
harness has a durable assignment or could be selected by headless dispatch.

## Body Status-Token Rule

Versioned bridge files (`bridge/<slug>-NNN.md`) MUST begin with a canonical
status token on the first non-blank line: one of `NEW`, `REVISED`, `GO`,
`NO-GO`, `VERIFIED`, `ADVISORY`, `DEFERRED`, or `WITHDRAWN`. Headings and prose
follow the token. This keeps each bridge file self-describing and makes the
first line a reliable routing signal.

The rule is mechanically enforced by `.claude/hooks/bridge-compliance-gate.py`
(activated byte-for-byte from
`groundtruth-kb/templates/hooks/bridge-compliance-gate.py`): a `Write` of a
versioned bridge file whose first non-blank line is not a recognized status
token is hard-blocked. The rule fires only on the `Write` tool (full file
content); `Edit` operations are not subject to it. Files that already exist on
disk with a non-canonical first line are grandfathered, so the rule never
retroactively breaks historical bridge files on overwrite. Non-versioned bridge
markdown is outside the dispatchable numbered-file chain. `WITHDRAWN` remains
an accepted canonical token where it appears as a terminal status.

Source: `GTKB-GOV-PROPOSAL-STANDARDS` Slice 1
(`DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE`; GO at
`bridge/gtkb-gov-proposal-standards-slice1-025.md`).

## Advisory Reports

**Purpose:** Advisory reports are first-class workflow state, not transport workarounds via `NO-GO@001`. They may be owner-initiated (owner asks LO to investigate a peer system) or LO-initiated (LO surfaces a finding during normal review).

**Routing:** ADVISORY entries are Prime-actionable for interactive sessions and non-dispatchable for headless runs. `ACTIONABLE_STATUSES_FOR_PRIME` in `groundtruth_kb.bridge.notify` includes `ADVISORY`, so `compute_actionable_pending` surfaces them in the Prime actionable list; the `_derive_dispatchable` invariant returns False for non-GO/NEW/REVISED/NO-GO statuses, so every headless dispatch surface (cross-harness trigger, single-harness dispatcher) filters them out before spawning. Manual `/bridge` scans show them; `bridge-axis-2-surface.py` also filters non-dispatchable items, so AXIS-2 surfacing of ADVISORY status entries is a separate follow-on concern.

**Authority:** Loyal Opposition (or owner-direction) authors ADVISORY entries; Prime Builder acknowledges in an interactive session and dispositions through owner-deliberation / UAQ flows, producing one of: (a) a normal NEW implementation proposal converting the advisory (`adopt` / `adapt`), (b) an explicit deferral with documented defer-trigger, or (c) a documented rejection (`reject`).

**Expected Prime response:** cite advisory in any follow-on conversion proposal's `Prior Deliberations` and `Source advisory` fields.

**Dashboard semantics:** ADVISORY rows are NOT failed proposals; dashboard counts must distinguish them from NO-GO entries. Exact dashboard-counter behavior is owned by the sibling `gtkb-advisory-report-dashboard-counters-spec` thread.

## DEFERRED Status

`DEFERRED` is owner-only bridge parking state. It is not a Prime Builder
revision, not a Loyal Opposition verdict, and not a replacement for parked
drafts.

A `DEFERRED` entry MUST be recorded as both:

1. dispatcher/TAFE lifecycle state for the thread; and
2. a versioned bridge file whose first non-blank line is exactly `DEFERRED`.

The `DEFERRED` file MUST include:

- concrete `Owner Decisions / Input` evidence, such as a cited DELIB/AUQ or an
  explicit owner directive;
- a deferral reason; and
- a clear/resume condition describing when the thread becomes actionable again.

`DEFERRED` is non-actionable for Prime Builder, Loyal Opposition, bridge
dispatch, and normal scan queues. It may be cleared only by owner-directed
follow-up that files the next appropriate lifecycle entry. Parked drafts remain
unindexed work-in-progress files; `DEFERRED` is indexed workflow state.

## Prime Workflow

1. Write the proposal as `bridge/{name}-001.md` through the governed bridge
   writer path
2. Let the governed writer publish TAFE-backed bridge state.
3. Continue working on other tasks
4. Periodically scan TAFE/dispatcher bridge state for GO, NO-GO, or ADVISORY
   responses; GO and NO-GO are dispatchable implementation/revision work,
   ADVISORY is interactive-only disposition work (non-dispatchable). Skip
   DEFERRED, WITHDRAWN, and VERIFIED as non-actionable.
5. On GO: proceed with implementation
6. On NO-GO: read the NO-GO file, address findings, save revised file with
   incremented version, and use the governed writer to publish a REVISED state.

## Loyal Opposition Workflow

1. Periodically scan TAFE/dispatcher bridge state for NEW or REVISED entries;
   skip ADVISORY, DEFERRED, WITHDRAWN, and VERIFIED as non-actionable for Loyal
   Opposition review work.
2. Process entries starting from the oldest actionable item.
3. Read the indicated file and perform the review
4. Save review findings as a new version with incremented number
5. Use the governed writer to publish the verdict state for that thread.

## Post-Implementation Verification

After Prime implements a GO'd proposal:
1. Prime saves a post-implementation report as a new version with incremented number
2. Prime uses the governed writer to publish a NEW verification-request entry
3. Loyal Opposition reviews and responds with NO-GO, or records VERIFIED only
   through the commit-finalization helper so the verified work, implementation
   report, and verdict artifact enter git history in the same local commit.

## Bridge State Maintenance

Dispatcher/TAFE state is maintained by the governed bridge writer/reconcile
path. Archived entries and their corresponding bridge files remain on disk for
historical reference.

## Guardrails

- Both agents must read the full entry (all versions) before acting on any
  single version
- Never delete bridge files — they form the audit trail
- Use the governed bridge writer/reconcile path for state repair rather than
  hand-merging coordination data.
- TAFE-backed bridge state is the source of truth for workflow state.

## Mandatory Owner Decisions / Input Section Gate

Implementation proposals and reports that depend on owner approval — citing Sub-slice B's AUQ-only rule (`bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006.md`), referencing AskUserQuestion answers, or otherwise indicating owner-decision scope — MUST include a non-empty `Owner Decisions / Input` section enumerating the relevant AskUserQuestion evidence.

The bridge-compliance-gate hook (`.claude/hooks/bridge-compliance-gate.py`) mechanically enforces this requirement at Write time. Loyal Opposition issues NO-GO when an applicable proposal/report lacks the section. Codex review checks the section's substance; placeholder content (`tbd`, `todo`, `n/a`, `none`, `not applicable`, `no relevant`) is rejected.

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

1. Publishing dispatcher/TAFE state with status `NEW` or `REVISED`.
2. The promotion commit message explicitly states `<bridge-id>: parked draft promoted to <status>`.

Audits SHOULD identify parked drafts in their inventory phase but MUST NOT flag them as orphans without checking the originating commit message for the `parked` tag.
