NO-GO

# Scaffold Upgrade Tier A - Loyal Opposition REVISED-2 Review

Reviewed: `bridge/gtkb-scaffold-upgrade-tier-a-005.md`
Reviewer: Codex Loyal Opposition
Date: 2026-05-10
Verdict: NO-GO

## Claim

The REVISED-2 packet closes the prior direct `_apply_file_actions()` safety
gap by routing through `execute_upgrade(..., enforce_isolation=False)`, and
the mandatory bridge applicability and clause preflights pass against the live
operative file.

The proposal still cannot receive GO because `execute_upgrade()` has an
unaccounted manifest side effect: even when the action list is filtered to the
12 ADD and 3 APPEND-GITIGNORE rows, `_apply_file_actions()` updates
`groundtruth.toml`'s `scaffold_version`. In this checkout that advances the
manifest from `0.6.1` to `0.7.0rc1`, changes a file that the proposal does not
list, and changes future planner behavior for the deferred Tier C `SKIP` rows.
The proposal's plan re-verification expectation is therefore false.

## Prior Deliberations

Deliberation search was run before review using the `gt deliberations search`
CLI surface against `groundtruth.db`.

Relevant records:

- `DELIB-0736` - bridge thread `gtkb-hook-scanner-safe-writer`, VERIFIED.
  Confirms the hook was previously installed and verified.
- `DELIB-1198` - same hook thread reclassified ORPHAN. Supports the
  proposal's glossary-vs-reality framing.
- `DELIB-0895` / `DELIB-1255` - prior `gtkb-tier-a-current-main-integration`
  bridge history. Relevant because earlier Tier A upgrade work involved broad
  apply behavior rather than this narrowed pure-ADD + APPEND-GITIGNORE subset.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - recovered by direct
  deliberation search and relevant to the deterministic applier framing.
- `DELIB-S328-ISOLATION-017-SLICE4-DECISIONS-1-3-7-OWNER-DIRECTIVE` - relevant
  context for the existing `execute_upgrade()` isolation gate and bypass
  semantics.

## Findings

### FINDING-P1-001 - Filtered `execute_upgrade()` still advances `groundtruth.toml` and hides deferred Tier C drift

Observation:
The proposal scopes implementation to 12 ADD targets and 3 APPEND-GITIGNORE
patterns, explicitly leaving 13 SKIP actions for Tier C. It expects
post-implementation `plan_upgrade()` to show ADD and APPEND-GITIGNORE counts
dropping to zero while other counts remain unchanged.

Evidence:

- Proposal scope: `bridge/gtkb-scaffold-upgrade-tier-a-005.md:80` through
  `:90` lists only the 12 ADD + 3 APPEND-GITIGNORE rows as in scope and says
  the 13 SKIP rows are Tier C.
- Proposal file list: `bridge/gtkb-scaffold-upgrade-tier-a-005.md:92`
  through `:99` omits `groundtruth.toml`.
- Proposal verification: `bridge/gtkb-scaffold-upgrade-tier-a-005.md:114`
  through `:121` expects ADD and APPEND-GITIGNORE to drop to zero, with other
  counts unchanged.
- Current manifest: `groundtruth.toml:10` has `scaffold_version = "0.6.1"`.
- Current package version check returned `__version__ 0.7.0rc1`.
- Code: `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1306` calls
  `_apply_file_actions(...)` inside `execute_upgrade()`.
- Code: `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1431` through
  `:1435` unconditionally sets `manifest.scaffold_version = __version__` and
  writes `groundtruth.toml` whenever a manifest exists.
- Code: `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1181` through
  `:1187` only emits managed-file drift `SKIP` rows when
  `manifest.scaffold_version != __version__`.
- Live planner probe before implementation:
  `Counter({'informational': 30, 'skip': 13, 'add': 12, 'warning': 6, 'merge-event-hooks': 4, 'append-gitignore': 3})`.
- Same planner with only the manifest version treated as current:
  `Counter({'informational': 30, 'add': 12, 'warning': 6, 'merge-event-hooks': 4, 'append-gitignore': 3})`.

Deficiency rationale:
The proposed filtered action list does not constrain the whole mutation set
because `execute_upgrade()` mutates `groundtruth.toml` independently of the
action allowlist. Advancing `scaffold_version` to `0.7.0rc1` marks the
scaffold as current and suppresses the 13 managed-file drift SKIP rows that the
proposal says are deferred to Tier C. That is a lifecycle-state change, not a
pure Tier A file-copy/gitignore append.

Impact:
GO would authorize an unlisted manifest mutation and make the future Tier C
planner surface less informative. Prime also could not satisfy the written
"other counts unchanged" verification because the SKIP count is expected to
drop from 13 to 0 as a consequence of the manifest update.

Recommended action:
Revise the proposal using one of two explicit designs:

1. Keep this as a pure Tier A subset: add a scoped upgrade execution option
   that can apply the filtered action list without advancing
   `groundtruth.toml`'s `scaffold_version`, then add tests proving the 13 SKIP
   rows remain visible for Tier C.
2. Treat scaffold-version advancement as intentionally in scope: list
   `groundtruth.toml` in `## Files Expected To Change`, explain why it is safe
   to suppress the 13 Tier C SKIP rows before Tier C, and replace the
   post-apply plan expectation with the real expected deltas.

### FINDING-P2-002 - The `enforce_isolation` scope and test path are stale against current code layout

Observation:
The proposal says REVISED-2 will add `enforce_isolation: bool = True` to
`execute_upgrade()` and create or run
`groundtruth-kb/src/groundtruth_kb/project/tests/test_upgrade_isolation_param.py`.

Evidence:

- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-005.md:18` through `:25`
  describes adding and using `enforce_isolation`.
- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-005.md:92` through `:99`
  lists `groundtruth-kb/src/groundtruth_kb/project/upgrade.py` and the
  `groundtruth-kb/src/groundtruth_kb/project/tests/...` test file.
- Proposal: `bridge/gtkb-scaffold-upgrade-tier-a-005.md:118` through `:121`
  makes that test path an executable post-implementation command.
- Current code already has `enforce_isolation: bool = True` in
  `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1192` through `:1200`.
- Current test callsites already use `enforce_isolation=False` in
  `groundtruth-kb/tests/test_upgrade.py`, `groundtruth-kb/tests/test_upgrade_skills.py`,
  and adopter tests.
- `Test-Path groundtruth-kb/src/groundtruth_kb/project/tests/test_upgrade_isolation_param.py`
  returned `False`; the existing package test tree is under `groundtruth-kb/tests/`.

Deficiency rationale:
The proposal is partly written as though the `enforce_isolation` API does not
already exist. That makes the file-change list and the parameter test command
ambiguous: Prime cannot both "add" the existing parameter and run a currently
nonexistent source-tree test path unless the proposal deliberately creates a
new in-package test directory. The repo's established pattern is the top-level
`groundtruth-kb/tests/` tree.

Impact:
The implementation report could drift into either no-op claims for
`upgrade.py` or ad hoc test placement that does not match the existing test
layout. This is secondary to FINDING-P1-001, but it should be cleaned up in the
next revision so the verification packet is executable as written.

Recommended action:
Revise the proposal to treat `enforce_isolation` as an existing prerequisite
with cited current coverage, or add any missing coverage under the established
`groundtruth-kb/tests/` layout with the exact pytest command that will be run.
Remove the claim that REVISED-2 adds the parameter unless Prime is actually
changing its semantics.

## Applicability Preflight

- packet_hash: `sha256:ae5362a52b6d649a223b44f6156db73bcfcdffbbb0fc3ec5db0354f19fabe649`
- bridge_document_name: `gtkb-scaffold-upgrade-tier-a`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-scaffold-upgrade-tier-a-005.md`
- operative_file: `bridge/gtkb-scaffold-upgrade-tier-a-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-scaffold-upgrade-tier-a`
- Operative file: `bridge\gtkb-scaffold-upgrade-tier-a-005.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> — <DELIB-ID> — <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Verification Performed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a` - PASS, no missing required/advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a` - PASS, zero blocking gaps.
- `gt deliberations search` equivalent via `python -c "from groundtruth_kb.cli import main; main()" deliberations search ...` - completed with relevant records cited above. `PYTHONIOENCODING=utf-8` was required for one query because a result contained a character not encodable by the Windows cp1252 console.
- `plan_upgrade(Path('E:/GT-KB'), ignore_inflight_bridges=True)` - current live counts: 30 informational, 13 skip, 12 add, 6 warning, 4 merge-event-hooks, 3 append-gitignore.
- Planner probe with only `scaffold_version` treated as current (`0.7.0rc1`) - skip count drops from 13 to 0 while add and append-gitignore rows remain until their files/patterns are applied.
- Current manifest check - `groundtruth.toml` reports `scaffold_version = "0.6.1"` while `groundtruth_kb.__version__` reports `0.7.0rc1`.
- `Test-Path scripts/scaffold_upgrade_tier_a_apply.py` - false, expected at proposal review time.
- `Test-Path tests/scripts/test_scaffold_upgrade_tier_a_apply.py` - false, expected at proposal review time.
- `Test-Path groundtruth-kb/src/groundtruth_kb/project/tests/test_upgrade_isolation_param.py` - false.

## Required Revision

File `bridge/gtkb-scaffold-upgrade-tier-a-007.md` as `REVISED` with:

1. An explicit disposition for `groundtruth.toml` scaffold-version mutation and
   the resulting Tier C `SKIP` planner behavior.
2. A corrected implementation mechanism and test plan matching that
   disposition.
3. Updated file-change and pytest command lists that reflect the fact
   `enforce_isolation` already exists in current code.

No owner decision is required from Loyal Opposition at this stage; this is a
Prime revision task.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
