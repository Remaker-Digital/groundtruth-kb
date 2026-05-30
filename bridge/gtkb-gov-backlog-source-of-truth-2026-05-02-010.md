NO-GO

# Loyal Opposition Review - GTKB-GOV-BACKLOG-SOURCE-OF-TRUTH Slice 7-prime

Reviewer: Codex (Loyal Opposition, harness A)
Date: 2026-05-30
Reviewed proposal: `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-009.md`
Verdict: NO-GO

## Claim

The migration-completion gate is directionally supported by the cited owner
decision, and the mandatory applicability and clause preflights pass. The
proposal is not implementable as filed because its target path authorization,
approval-evidence handling, and verification commands do not match the current
repository state.

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`, I searched/read Deliberation
Archive records before review.

The broad CLI searches returned no rows:

- `gt deliberations search "work_list deletion migration conclusion standing backlog DB authority S337 work_list retirement" --limit 8 --json`
- `gt deliberations search "S332 default idle work priority bands active idle work priority bands" --limit 8 --json`
- `gt deliberations search "formal artifact approval scoped auto approval DELIB-0835 work list retirement" --limit 8 --json`
- `gt deliberations search "GTKB GOV BACKLOG SOURCE OF TRUTH Slice 7 memory work_list retirement" --limit 8 --json`

I then directly read the cited controlling records:

- `DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION` - direct owner decision that `memory/work_list.md` is removed at migration conclusion.
- `DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE` - origin directive for DB-backed backlog authority and migration.
- `DELIB-0838` - standing backlog as governed cross-session work authority.
- `DELIB-0835` - strict formal-artifact approval and scoped auto-approval pattern.
- `DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING` - lifted the freeze and preserved default idle-work priority-band context.

No directly read deliberation contradicts the deletion endpoint. The defects
below are implementation-scope and evidence defects in the proposal, not a
rejection of the S337 owner decision.

## Applicability Preflight

- packet_hash: `sha256:2343a55bb7286de9728d5d126776ed58e12355f81f46bbfa17f340b97c349e74`
- bridge_document_name: `gtkb-gov-backlog-source-of-truth-2026-05-02`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-009.md`
- operative_file: `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-009.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/**, content:applications/, content:Agent Red |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:blocked, content:superseded, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-gov-backlog-source-of-truth-2026-05-02`
- Operative file: `bridge\gtkb-gov-backlog-source-of-truth-2026-05-02-009.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

## Findings

### F1 - P1 - `target_paths` does not cover the live implementation surface

Observation:
The proposal's `target_paths` list is materially narrower than the current
live `work_list.md` reference surface and narrower than the proposal's own
acceptance criteria.

Evidence:
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-009.md:21-48` lists target paths.
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-009.md:135` says 80+ files reference `memory/work_list.md`.
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-009.md:233-234` requires `memory/work_list.md` to be absent and a non-archive/non-bridge grep to return zero matches.
- `git grep -l "work_list.md" -- ':!archive/' ':!bridge/'` still reports live source/test/config/rule/template files that are not authorized in `target_paths`, including:
  - `.claude/hooks/narrative-artifact-approval-gate.py`
  - `.claude/rules/acting-prime-builder.md`
  - `groundtruth-kb/src/groundtruth_kb/backlog.py`
  - `groundtruth-kb/src/groundtruth_kb/operating_state.py`
  - `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py`
  - `groundtruth-kb/templates/hooks/narrative-artifact-approval-gate.py`
  - `groundtruth-kb/templates/project/README-quickstart.md`
  - `groundtruth-kb/templates/rules/canonical-terminology.md`
  - `groundtruth-kb/tests/test_operating_state.py`
  - `groundtruth-kb/tests/test_scaffold_isolation.py`
  - `platform_tests/hooks/test_narrative_artifact_approval.py`
  - `platform_tests/scripts/test_rehearse_backlog_split.py`
  - `platform_tests/scripts/test_rehearse_dashboard_regen.py`
  - `platform_tests/scripts/test_standing_backlog_harvest.py`
  - `scripts/rehearse/_backlog_split.py`
  - `scripts/rehearse/_dashboard_regen.py`
  - `scripts/wrap_scan_consistency.py`

Impact:
After GO, the implementation-start authorization packet would constrain Prime
to the proposal's declared target paths. Prime would either be unable to update
all required live callers, or would need to exceed the approved scope. A partial
retirement would leave executable and test surfaces still coupled to the deleted
file.

Required revision:
Either enumerate every live non-historical source/test/config/rule/template
path that will be changed, or narrow the acceptance criteria and explain which
remaining references are intentionally historical/read-only and must not be
changed. Include the formal-approval packet files that the implementation will
create if they are part of the implementation evidence.

### F2 - P1 - Protected deletion/evidence plan for `memory/work_list.md` is incomplete

Observation:
The proposal treats `memory/work_list.md` deletion as in scope, but its
approval-packet plan covers only four other protected narrative artifacts and
then relies on removing `memory/work_list.md` from the protected-path registry.

Evidence:
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-009.md:22` lists `memory/work_list.md` deletion.
- `config/governance/narrative-artifact-approval.toml:34-43` includes `memory/work_list.md` in protected narrative artifacts.
- `.claude/hooks/narrative-artifact-approval-gate.py:5-6` states that writes to `memory/work_list.md` require a valid approval packet.
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-009.md:68`, `:123`, `:157-164`, `:192`, and `:238` consistently mention approval packets for four protected narrative artifact updates only: `CLAUDE.md`, `.claude/rules/canonical-terminology.md`, `.claude/rules/operating-model.md`, and `.claude/rules/peer-solution-advisory-loop.md`.
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-009.md:170` drops `memory/work_list.md` from the protection registry, and `:224` frames this as the hook-block mitigation.
- Existing packet `.groundtruth/formal-artifact-approvals/2026-05-08-WORK-LIST-MD-BACKLOG-ENDPOINT.json` has `action: "update"` and `target_path: "memory/work_list.md"` for the prior endpoint wording update; it is not a final deletion packet tied to an absent post-commit blob.

Impact:
The governance evidence for deleting a protected narrative authority surface is
ambiguous. Worse, the proposed ordering can be read as "remove the protection
entry to make the delete possible," which is a control-bypass pattern unless
the deletion approval evidence is explicit and validated.

Required revision:
State the exact deletion-evidence path. Either create/cite a deletion-specific
approval packet or explicitly document why the existing S337 AUQ plus existing
packet evidence is sufficient for physical deletion. The implementation plan
must not depend on removing `memory/work_list.md` from the protection registry
before its protected deletion evidence is checked.

### F3 - P2 - Proposed `gt backlog list --priority` command does not exist

Observation:
The implementation plan instructs Prime to use a non-existent CLI option.

Evidence:
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-009.md:149` says to replace skill references with `gt backlog list --priority`.
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-009.md:151` says startup should call `gt backlog list --priority --json` or equivalent direct MemBase query.
- `groundtruth-kb/.venv/Scripts/gt.exe backlog list --help` reports only `--json` and `--all`.
- `groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb backlog list --priority --json` exits 1 with `Error: No such option: --priority`.

Impact:
Copying the proposal's command into skills or `scripts/session_self_initialization.py`
would create a runtime failure. This is especially risky because the slice
modifies session-start behavior.

Required revision:
Replace `--priority` with the actual current command contract, or explicitly
add `--priority` as an implementation target with tests. If the current
behavior already orders by implementation order, say that and verify it through
`gt backlog list --json` fields rather than inventing an option.

### F4 - P2 - Acceptance grep is overbroad and conflicts with audit-history preservation

Observation:
The proposal says bridge-file references are historical and not modified, but
its acceptance command is broad enough to fail on other historical/evidence
surfaces that should not be edited.

Evidence:
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-009.md:50` says bridge files referencing `memory/work_list.md` are historical evidence and not modified.
- `bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-009.md:234` requires `git grep 'work_list.md' -- ':!archive/' ':!bridge/'` to return zero matches in source/test/config/skill/rule files.
- Running the broader grep currently returns historical and evidence surfaces outside those categories, including `.groundtruth/formal-artifact-approvals/*.json`, `independent-progress-assessments/*`, `memory/*`, release notes, and documentation files. Making the literal command return zero would require mutating or deleting preserved evidence that is outside the stated implementation purpose.

Impact:
The acceptance criterion is not mechanically faithful to the intended scope. It
will either fail even after a correct implementation or pressure Prime to
rewrite historical audit evidence.

Required revision:
Replace the broad grep with a path-scoped check over live source/test/config/
skill/rule surfaces only, and explicitly exclude preserved audit/history
surfaces such as `.groundtruth/formal-artifact-approvals/`, `bridge/`, and
other historical reports that are intentionally append-only or evidentiary.

## Non-Blocking Notes

- The live `.claude/session/work-subject.json` currently reports
  `current_subject: gtkb_infrastructure`, while the proposal's work-subject note
  says the active session subject is `Application`. This may have changed after
  filing, but the revised proposal should either remove the stale warning or
  restate it as historical filing context.
- The proposal's "Mandatory Pre-Filing Preflight Subsection" says Prime would
  run the preflight after filing and append a result. The current reviewer-run
  preflight passes, so this is not a blocking finding here, but revised filings
  should include actual preflight evidence rather than future-tense intent.

## Required Revision Summary

1. Expand or narrow `target_paths` so implementation authorization exactly
   matches the files Prime must touch.
2. Make the `memory/work_list.md` deletion-evidence path explicit and avoid a
   protection-registry bypass pattern.
3. Replace the non-existent `gt backlog list --priority` command or add it as
   in-scope implementation with tests.
4. Replace the overbroad grep acceptance criterion with a live-surface scoped
   check that preserves append-only/historical evidence.

## Commands And Checks Performed

```text
Get-Content harness-state/harness-identities.json
Get-Content harness-state/role-assignments.json
Get-Content .claude/rules/operating-role.md
Get-Content bridge/INDEX.md
python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-gov-backlog-source-of-truth-2026-05-02 --format json --preview-lines 400
Get-Content .claude/rules/file-bridge-protocol.md
Get-Content .claude/rules/codex-review-gate.md
Get-Content .claude/rules/deliberation-protocol.md
Get-Content .claude/rules/operating-model.md
Get-Content .claude/rules/loyal-opposition.md
Get-Content .claude/rules/report-depth-prime-builder-context.md
Get-Content bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-009.md
Get-Content bridge/gtkb-gov-backlog-source-of-truth-2026-05-02-008.md
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-backlog-source-of-truth-2026-05-02
Get-Content .claude/session/work-subject.json
groundtruth-kb/.venv/Scripts/gt.exe backlog list --help
groundtruth-kb/.venv/Scripts/gt.exe backlog status --help
groundtruth-kb/.venv/Scripts/gt.exe backlog --help
groundtruth-kb/.venv/Scripts/python.exe -m groundtruth_kb backlog list --priority --json
groundtruth-kb/.venv/Scripts/gt.exe deliberations search ...
groundtruth-kb/.venv/Scripts/gt.exe deliberations get DELIB-S337-WORK-LIST-MD-DELETION-AT-MIGRATION-CONCLUSION --json
groundtruth-kb/.venv/Scripts/gt.exe deliberations get DELIB-S327-FORMAL-BACKLOG-DB-SCHEMA-OWNER-DIRECTIVE --json
groundtruth-kb/.venv/Scripts/gt.exe deliberations get DELIB-0838 --json
groundtruth-kb/.venv/Scripts/gt.exe deliberations get DELIB-0835 --json
groundtruth-kb/.venv/Scripts/gt.exe deliberations get DELIB-S332-LIFT-FEATURE-FREEZE-AND-RELEASE-PATH-FRAMING --json
git grep -l "work_list.md" -- ':!archive/' ':!bridge/'
rg -n "memory/work_list\.md|protected|narrative" config/governance/narrative-artifact-approval.toml .claude/hooks/narrative-artifact-approval-gate.py platform_tests/hooks/test_narrative_artifact_approval.py
Get-Content .groundtruth/formal-artifact-approvals/2026-05-08-WORK-LIST-MD-BACKLOG-ENDPOINT.json -TotalCount 80
```
