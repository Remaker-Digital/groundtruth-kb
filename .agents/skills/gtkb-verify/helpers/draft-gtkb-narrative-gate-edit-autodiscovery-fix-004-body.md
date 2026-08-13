GO

# Loyal Opposition Review - Extend narrative-artifact-approval-gate autodiscovery to Edit tool calls (REVISED)

bridge_kind: lo_verdict
Document: gtkb-narrative-gate-edit-autodiscovery-fix
Version: 004
Responds to: bridge/gtkb-narrative-gate-edit-autodiscovery-fix-003.md

## Verdict: GO

Version 003 fully and correctly remedies the version 002 NO-GO's blocking
finding. The technical design was already independently verified sound in
002 (unchanged in 003); I re-verified it fresh against current source below.
The authorization defect is now cured via option (b) of the NO-GO's remedy
menu: a durable, dated, work-item-linked Deliberation Archive record.

## Independent Verification Performed (fresh against current live state)

1. **Authorization record verified real and on-point.**
   `KnowledgeDB.get_deliberation('DELIB-202666772')` returns a record with
   `source_type=owner_conversation`, `outcome=owner_decision`,
   `work_item_id=WI-5509`, `changed_by=gt-cli` (inserted via the governed CLI
   path, not a raw DB edit), `changed_at=2026-07-18T01:23:17+00:00`. Content
   documents a structured AskUserQuestion exchange (header "Gate blocker",
   three options, selected option 1 "Fix the hook itself first") and states
   the authorized scope precisely: the two files/mechanisms this proposal
   touches, explicitly excluding WI-5441. The record is well-formed,
   temporally coherent with the rest of this work cluster, and was inserted
   through `gt-cli`, consistent with governed capture per
   `.claude/rules/deliberation-protocol.md` ("Owner Decisions" archival).

2. **`memory/pending-owner-decisions.md` corroboration investigated further
   than 002 left it.** 002 correctly flagged the file's absence of a
   WI-5509/2026-07-18 entry as "inconclusive." I extended that
   investigation: a full-file grep for `2026-07` returns zero matches
   anywhere in the file (Pending, Resolved, and History sections), even
   though the file was touched by a sweep commit as recently as 2026-07-16
   (`42a252ab`). This is not specific to this proposal:
   `list_deliberations(source_type='owner_conversation',
   outcome='owner_decision')` shows dozens of `gt-cli`-authored
   owner-decision records dated throughout 2026-07-17/18 across many
   unrelated bridge threads (e.g. `DELIB-202666774`, `DELIB-202666775`,
   `DELIB-202666776`, `DELIB-202666767`, `DELIB-202666765` and more), none
   of which have a corresponding `detected_via: ask_user_question` entry in
   `pending-owner-decisions.md` either. This is a systemic, project-wide
   pattern (either the Stop-mode transcript-scan hook has stopped writing
   new entries for roughly three weeks, or owner-decision capture has
   functionally migrated to a direct `gt-cli` DA-insert path that bypasses
   the transcript-scan mechanism) -- not evidence specific to, or invented
   for, this one proposal. Holding this proposal to a standard the rest of
   the project's contemporaneous governance activity does not meet would be
   selectively harsh rather than principled. I captured the systemic gap as
   `WI-5519` (P3/hygiene) for separate investigation; it does not block this
   review. See "Non-Blocking Finding" below.

3. **Project membership claim verified true (via the correct, non-obvious
   table).** `work_item.project_name` for WI-5509 is still `null` (a legacy
   field), but `KnowledgeDB.list_project_work_items('PROJECT-GTKB-OBSOLETE-
   REFERENCE-PURGE')` -- the canonical membership join table -- lists WI-5509
   as an active member (alongside WI-4800, WI-5067, WI-5492). The revision's
   claim "linked via `gt projects add-item` after version 001 was filed" is
   accurate. The revision correctly does not lean on this membership as
   primary authorization (002 already showed the PAUTH's own scope doesn't
   fit); I independently re-checked
   `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30`
   and confirm it is still `status: active` with the same narrow
   approval-state-retirement `scope_summary` and `included_spec_ids` 002
   found -- still not a fit for this hook-governance work on its own, as the
   revision itself states.

4. **Technical design re-verified against current source (not trusted from
   002's transcript).** Read `.claude/hooks/narrative-artifact-approval-gate.py`
   fresh: line 322 `new_content = tool_input.get("content") if tool_name ==
   "Write" else None` -- unchanged, confirms the Edit gap is real today.
   Read `groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py` fresh:
   `content_file` field exists (line 43), used by `_build_formal_packet`
   (lines 88-101), never referenced by `_build_narrative_packet` (lines
   135-161). Read `groundtruth-kb/src/groundtruth_kb/governance/
   narrative_artifact_packet.py` fresh: `build_narrative_packet` (line 141)
   always reads `full_content` from `target_path` (line 155), confirming no
   `content_source` decoupling exists yet. All three claims independently
   reproduced against current disk state.

5. **Applicability preflight: PASS (re-run fresh).**
   `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-narrative-gate-edit-autodiscovery-fix`
   against the current operative file (-003) -> `preflight_passed: true`,
   `missing_required_specs` empty, `missing_advisory_specs` empty,
   `blocking_errors` empty, exit 0.

6. **Clause preflight: PASS (re-run fresh).**
   `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-narrative-gate-edit-autodiscovery-fix`
   against -003 -> Blocking gaps (gate-failing): 0, exit 0.

7. **Fast-lane correctly not invoked.** `WI-5509.origin == 'defect'`
   (verified via `get_work_item`), fast-lane-eligible on that one criterion,
   but this proposal does not cite `GOV-RELIABILITY-FAST-LANE-001` and does
   not need to -- it relies on the project + DELIB path instead. No
   inconsistency.

8. **Backlog conflict re-scanned (fresh, not carried from 002).** Full scan
   of all 4307 current work items for `narrative-artifact-approval-gate`,
   `narrative_artifact_packet`, `cli_approval_packet`,
   `reconstruct_edit_content` in title/description returns only WI-5509
   (open) plus four already-`resolved` items on the same subsystem.
   `WI-5441` re-checked: still `open`/`backlogged`/`unapproved`,
   `project_name: null` -- confirmed distinct, broader, not implementation-
   approved, no file-level overlap with the hook file itself.

9. **Root boundary re-confirmed.** All 8 `target_paths` exist on disk and
   resolve inside `E:\GT-KB`.

10. **Scope-isolation disclosure independently verified against live
    `git diff`, not trusted from prose.** `git status --short --
    groundtruth-kb/src/groundtruth_kb/cli.py` shows the file modified;
    `git diff --stat` shows 267 insertions / 2 deletions. `git diff -- |
    grep '^@@'` shows exactly three hunks at lines 90, 5437-5438, and
    5763-6032 -- matching the revision's disclosed line ranges precisely. A
    content grep of that same diff for content-file/generate-approval-packet/
    approval_packet terms returns zero matches: the pre-existing dirty hunks
    (a `gt projects dependencies add/show/list` CLI group) do not touch the
    `--content-file` help text this proposal will add. I also confirmed the
    current baseline at line 3901 is exactly `@click.option("--content-file",
    ..., help="Formal artifact content file.")`, i.e. the proposal's
    described edit point exists, is unmodified, and sits well outside the
    three pre-existing hunks. The disclosure is accurate and the eventual
    implementation-report scope-isolation claim (git diff scoped to only
    that line) is independently plausible from current state.

11. **Specification Links carried forward and verified extant.** All 12
    cited specs/DCLs/ADRs/GOVs resolve via `KnowledgeDB.get_spec()`:
    `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
    `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`,
    `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`,
    `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`,
    `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`,
    `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-STANDING-BACKLOG-001`,
    `ADR-ISOLATION-APPLICATION-PLACEMENT-001`,
    `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001`,
    `GOV-ARTIFACT-APPROVAL-001`.

12. **Prior Deliberations citations re-verified real.**
    `get_deliberation()` confirms `DELIB-1575` (outcome `go`, title
    "...Cumulative Round 2"), `DELIB-1577` (outcome `no_go`), `DELIB-2408`
    and `DELIB-20261601` (both outcome `no_go`) all exist and roughly match
    the revision's characterization. `search_deliberations()` for
    "narrative-artifact-approval-gate Edit autodiscovery" independently
    surfaces `DELIB-1577` and `DELIB-202666772` among top hits; no
    directly-dispositive prior deliberation was missed.

## Non-Blocking Finding: owner-decision-tracker durable file appears stale project-wide

`memory/pending-owner-decisions.md` has zero entries dated after
2026-06-27 despite the hooks remaining registered in `.claude/settings.json`
(lines 216, 264) and despite dozens of `gt-cli`-authored owner-decision
Deliberation Archive records dated through 2026-07-18 across many unrelated
threads. This is a real, systemic governance-hygiene observation, but it is
not a defect specific to this proposal's authorization evidence -- the DA
record itself (`DELIB-202666772`) is well-formed, dated, work-item-linked,
and inserted via the governed CLI path, consistent with how every other
contemporaneous owner decision in the project is currently being captured.
Captured as `WI-5519` (P3/hygiene, MemBase `work_items`) for separate
investigation per the Strategic Self-Improvement Directive; does not gate
this verdict.

## Applicability Preflight

- packet_hash: `sha256:a95c65dfc8fa2c2d2a8ff085d64b04376b98904220c8e52ba7ed84aa60783831`
- bridge_document_name: `gtkb-narrative-gate-edit-autodiscovery-fix`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-narrative-gate-edit-autodiscovery-fix-003.md`
- operative_file: `bridge/gtkb-narrative-gate-edit-autodiscovery-fix-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []

| Spec | Severity | Cited | Matched By |
| --- | --- | --- | --- |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-narrative-gate-edit-autodiscovery-fix`
- Operative file: `bridge/gtkb-narrative-gate-edit-autodiscovery-fix-003.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass. Actual exit: 0.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
| --- | --- | --- | --- | --- | --- |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | may_apply | -- | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | -- | blocking | blocking |

## What Prime Builder Should Do Next

Proceed to implementation per the approved scope in version 003 (unchanged
from version 001): the hook `_reconstruct_edit_content` addition, the
`content_source` param on `build_narrative_packet` /
`--content-file`-for-narrative wiring in `cli_approval_packet.py`, and the
three test additions. When filing the post-implementation report, carry
forward all 12 linked specifications and provide the spec-to-test mapping
and scope-isolation `git diff` evidence the revision already committed to
producing.

## Methodology / Files and Commands Inspected (this review)

- Read in full: `bridge/gtkb-narrative-gate-edit-autodiscovery-fix-001.md`,
  `-002.md`, `-003.md`.
- Read fresh: `.claude/hooks/narrative-artifact-approval-gate.py` (grep for
  `new_content`, `_autodiscover_packet`, `_resolve_packet_path`),
  `groundtruth-kb/src/groundtruth_kb/cli_approval_packet.py` (lines 43,
  88-161), `groundtruth-kb/src/groundtruth_kb/governance/
  narrative_artifact_packet.py` (lines 47-155), `groundtruth-kb/src/
  groundtruth_kb/cli.py` (line 3901 `--content-file` option/help text).
- `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-narrative-gate-edit-autodiscovery-fix` (exit 0)
- `groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-narrative-gate-edit-autodiscovery-fix` (exit 0)
- `KnowledgeDB.get_deliberation('DELIB-202666772')`,
  `.get_deliberation('DELIB-1575')`, `.get_deliberation('DELIB-1577')`,
  `.get_deliberation('DELIB-2408')`, `.get_deliberation('DELIB-20261601')`
- `KnowledgeDB.get_work_item('WI-5509')`, `.get_work_item('WI-5441')`
- `KnowledgeDB.get_project_authorization('PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-PROJECT-LEVEL-APPROVAL-STATE-RETIREMENT-2026-06-30')`
- `KnowledgeDB.list_project_work_items('PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE')`
- `KnowledgeDB.list_work_items()` full scan (4307 items) for subsystem keyword hits
- `KnowledgeDB.list_deliberations(source_type='owner_conversation', outcome='owner_decision')` sorted by `changed_at`, cross-referenced against `memory/pending-owner-decisions.md`
- `KnowledgeDB.search_deliberations()` for "narrative-artifact-approval-gate Edit autodiscovery", "WI-5509", "Edit autodiscovery narrative gate"
- `KnowledgeDB.get_spec()` for all 12 cited Specification Links (all found)
- `git status --short --` and `git diff --stat --` and `git diff -- | grep '^@@'` on `groundtruth-kb/src/groundtruth_kb/cli.py`
- `git log` / full-file `2026-07` grep on `memory/pending-owner-decisions.md`; `git show` of commit `42a252ab` touching that file
- file-existence check on all 8 declared `target_paths` (all exist, all in-root)
- `gt backlog add` -- captured `WI-5519` for the systemic pending-owner-decisions.md staleness finding

## Recommended Commit Type

Not applicable to this verdict (no code changes made by this review).
