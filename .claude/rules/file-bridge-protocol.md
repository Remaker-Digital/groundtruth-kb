# File Bridge Protocol

The bridge between Prime Builder and Loyal Opposition uses a shared directory
of versioned markdown files governed by a single index file.

## Directory

`bridge/` at project root. All proposal, review, and verification documents
live here as numbered markdown files.

## Mandatory Root Boundary Gate

Every bridge proposal, review, implementation report, and verification must
comply with `.claude/rules/project-root-boundary.md`: all active GT-KB files and
artifacts must remain within `E:\GT-KB`; all GT-KB demo/application files must
remain within `E:\GT-KB\applications\`. Agent Red files are not GT-KB files and
must not be used as live GT-KB artifacts. There are no exceptions. A bridge item
that depends on a live path outside those roots is `NO-GO`.

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
derived from live `bridge/INDEX.md`, the approved proposal file, and the GO
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
4. After drafting (and before filing or after editing the INDEX entry), run:

   ```
   python scripts/bridge_applicability_preflight.py --bridge-id <intended-bridge-id>
   ```

   The expected result is `preflight_passed: true`,
   `missing_required_specs: []`, `missing_advisory_specs: []`. Any non-empty
   `missing_*_specs` list is a self-detected defect; revise the proposal before
   INDEX update or before re-saving the file.

5. Record the resulting `packet_hash` from the preflight output in the proposal
   as evidence of self-check (optional but recommended for auditability).

Loyal Opposition (Codex) MUST issue NO-GO on any bridge proposal whose
preflight on its own operative file does not pass. Codex's NO-GO message must
include the offending `missing_*_specs` list.

The catch-22 case (preflight requires INDEX entry to know the operative file):
if the INDEX entry doesn't yet exist, manually grep the draft text against the
`applies_when_*` patterns in `config/governance/spec-applicability.toml`. After
filing the INDEX entry, run the preflight once and revise if it fails.

This subsection operationalizes
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (proposal must cite all
relevant specs) and is mechanically enforced by
`.claude/hooks/bridge-compliance-gate.py` per the companion bridge thread
`bridge/gtkb-pre-filing-preflight-hook-NNN.md`. Until the hook upgrade lands,
this subsection is rule-cited soft authority; Codex's NO-GO at review time
remains the reliable feedback loop.

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

## Index File

`bridge/INDEX.md` is the single coordination file. Both agents read and write
it. Format:

```
Document: {descriptive-name}
{STATUS}: bridge/{descriptive-name}-{NNN}.md
{STATUS}: bridge/{descriptive-name}-{NNN}.md
...
```

Each document entry starts with a `Document:` line followed by one or more
versioned file lines. The latest version is always at the top of the version
list within each entry. New document entries are inserted at the top of the
index file (after the header comments).

## Statuses

| Status | Set by | Meaning |
|--------|--------|---------|
| NEW | Prime | Fresh proposal awaiting review |
| REVISED | Prime | Updated proposal after a NO-GO |
| GO | Loyal Opposition | Proposal approved for implementation |
| NO-GO | Loyal Opposition | Proposal requires changes before approval |
| VERIFIED | Loyal Opposition | Post-implementation verification passed |
| ADVISORY | Loyal Opposition | Owner-initiated advisory report; non-dispatchable; awaiting Prime acknowledgement and disposition decision (NOT awaiting GO/NO-GO/VERIFIED). |

## Advisory Reports

**Purpose:** Owner-initiated advisory reports are first-class workflow state, not transport workarounds via `NO-GO@001`.

**Routing:** ADVISORY entries are Axis-2 (non-dispatchable). The cross-harness event-driven trigger SHOULD exclude ADVISORY rows from actionable-signature computation. Per-parser inventory is owned by the parallel `gtkb-bridge-advisory-status-001` runtime thread.

**Authority:** Loyal Opposition authors ADVISORY entries; Prime acknowledges and either (a) files a normal NEW implementation proposal converting the advisory, (b) defers explicitly with documented defer-trigger, or (c) rejects with documented rationale.

**Expected Prime response:** cite advisory in any follow-on conversion proposal's `Prior Deliberations` and `Source advisory` fields.

**Dashboard semantics:** ADVISORY rows are NOT failed proposals; dashboard counts must distinguish them from NO-GO entries. Exact dashboard-counter behavior is owned by the sibling `gtkb-advisory-report-dashboard-counters-spec` thread.

## Prime Workflow

1. Write the proposal as `bridge/{name}-001.md`
2. Open `bridge/INDEX.md` and insert a new entry at the top:
   ```
   Document: {name}
   NEW: bridge/{name}-001.md
   ```
3. Continue working on other tasks
4. Periodically scan the index for GO or NO-GO responses (scheduled every 3 minutes)
5. On GO: proceed with implementation
6. On NO-GO: read the NO-GO file, address findings, save revised file with
   incremented version, and insert a REVISED line at the top of that entry:
   ```
   Document: {name}
   REVISED: bridge/{name}-003.md
   NO-GO: bridge/{name}-002.md
   NEW: bridge/{name}-001.md
   ```

## Loyal Opposition Workflow

1. Periodically scan the index for NEW or REVISED entries (automated every 3 minutes)
2. Process entries starting from the oldest (bottom of the index)
3. Read the indicated file and perform the review
4. Save review findings as a new version with incremented number
5. Insert the verdict line at the top of that entry's version list:
   ```
   GO: bridge/{name}-002.md
   NEW: bridge/{name}-001.md
   ```
   or:
   ```
   NO-GO: bridge/{name}-002.md
   NEW: bridge/{name}-001.md
   ```

## Post-Implementation Verification

After Prime implements a GO'd proposal:
1. Prime saves a post-implementation report as a new version with incremented number
2. Prime inserts a NEW line at the top of that entry
3. Loyal Opposition reviews and responds with VERIFIED or NO-GO

## Index Maintenance

When `INDEX.md` exceeds ~200 lines, the agent inserting a new entry may remove
the oldest entries from the bottom of the file. Archived entries and their
corresponding bridge files remain on disk for historical reference.

## Guardrails

- Both agents must read the full entry (all versions) before acting on any
  single version
- Never delete bridge files — they form the audit trail
- If both agents write to INDEX.md simultaneously, the second writer must
  re-read and merge (simple append conflict resolution)
- The index is the source of truth for workflow state — not the files themselves

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

A bridge file MAY be committed without an INDEX entry when the commit message tags it as a parked draft (e.g., `... 18.C draft parked`). The applicability preflight tool returns `ERR_NO_INDEX_ENTRY` for such files; that is expected behavior and not a defect.

Parked drafts are deliberate work-in-progress artifacts that must NOT trigger Loyal Opposition review until they are promoted by:

1. Adding an INDEX entry with status `NEW` or `REVISED`.
2. The promotion commit message explicitly states `<bridge-id>: parked draft promoted to <status>`.

Audits SHOULD identify parked drafts in their inventory phase but MUST NOT flag them as orphans without checking the originating commit message for the `parked` tag.
