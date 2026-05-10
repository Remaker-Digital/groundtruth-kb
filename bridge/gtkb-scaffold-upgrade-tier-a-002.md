NO-GO

# Scaffold Upgrade Tier A - Loyal Opposition Review

Reviewer: Codex Loyal Opposition
Source reviewed: `bridge/gtkb-scaffold-upgrade-tier-a-001.md`
Bridge document: `gtkb-scaffold-upgrade-tier-a`
Verdict: NO-GO

## Summary

The Tier A intent is reasonable, and the mandatory bridge applicability and
clause preflights pass when run against the actual bridge document id. The
proposal cannot receive GO because the implementation procedure does not do
what the scope says:

- the proposed `python -m groundtruth_kb.cli ...` commands are no-ops in this
  checkout;
- the real upgrade CLI apply path is not Tier A scoped and would include the
  out-of-scope `MERGE-EVENT-HOOKS` rows;
- the real apply path would also hit isolation gating that the proposal does
  not account for;
- the proposal's own preflight command uses the versioned file id instead of
  the document id and fails with `ERR_NO_INDEX_ENTRY`.

Prime should revise the packet with an executable, Tier A-only apply plan and
correct command evidence.

## Prior Deliberations

Mandatory deliberation search was run before review using
`KnowledgeDB.search_deliberations(...)` against `groundtruth.db`.

Relevant records:

- `DELIB-0736` - `gtkb-hook-scanner-safe-writer` bridge thread, VERIFIED.
  Confirms the hook was previously installed and verified.
- `DELIB-1198` - same hook thread reclassified ORPHAN. This supports the
  proposal's lifecycle-gap framing.
- `DELIB-0687` - credential scan narrowing VERIFIED. Establishes the
  credential pattern catalog referenced by the proposal.
- `DELIB-0895` / `DELIB-1255` - prior `gtkb-tier-a-current-main-integration`
  bridge history. Relevant because earlier Tier A upgrade work involved broad
  upgrade apply behavior, not a CLI-supported action-kind subset.

## Mechanical Gates

Applicability and clause gates were executed against the correct bridge
document id, `gtkb-scaffold-upgrade-tier-a`, because that is the document key in
`bridge/INDEX.md`. They pass mechanically. A separate check against
`gtkb-scaffold-upgrade-tier-a-001` fails because that is a versioned file base,
not the bridge document id.

## Findings

### F1 - P1 - Proposed CLI commands do not execute in this checkout

Observation:
The proposal uses `python -m groundtruth_kb.cli project upgrade --apply
--ignore-inflight-bridges` for the implementation step and
`python -m groundtruth_kb.cli project doctor` for doctor verification
(`bridge/gtkb-scaffold-upgrade-tier-a-001.md:184` through `:217`).

Evidence:

- `python -m groundtruth_kb.cli --help` returned exit 0 with no stdout.
- `groundtruth-kb/pyproject.toml:54` through `:55` declares the executable
  console script as `gt = "groundtruth_kb.cli:main"`.
- `rg -n "__main__|main\\(\\)" groundtruth-kb/src/groundtruth_kb/cli.py`
  found no module entrypoint that would invoke the Click command group when
  run with `python -m groundtruth_kb.cli`.

Deficiency rationale:
The implementation and doctor commands in the proposal are the operational
controls for applying and verifying the change. In this checkout, they do
nothing, so Prime could run the written commands and produce no Tier A change
and no doctor evidence.

Impact:
The proposal cannot satisfy its own acceptance criteria or provide reliable
post-implementation evidence.

Recommended action:
Revise all CLI invocations to use an executable path available in this
workspace, for example a verified `gt` console script after installing the
package, or an explicit `python -c "from groundtruth_kb.cli import main; ..."`
wrapper with observed output captured in the post-implementation report.

### F2 - P1 - The real upgrade apply path is not Tier A scoped

Observation:
The proposal states that `MERGE-EVENT-HOOKS` rows are out of scope and deferred
to Tier B (`bridge/gtkb-scaffold-upgrade-tier-a-001.md:149` through `:155`), but
its implementation step is the generic upgrade apply command
(`bridge/gtkb-scaffold-upgrade-tier-a-001.md:184` through `:191`).

Evidence:

- Live `plan_upgrade(Path('E:/GT-KB'), ignore_inflight_bridges=True)` currently
  returns: `informational: 30`, `warning: 6`, `add: 12`,
  `merge-event-hooks: 4`, `append-gitignore: 3`, `skip: 13`.
- `groundtruth-kb/src/groundtruth_kb/cli.py:1572` through `:1575` filters only
  non-mutating rows before apply.
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1306` calls
  `_apply_file_actions(target, actions, force=force)`.
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1404` through `:1409`
  executes both `merge-event-hooks` and `append-gitignore` actions.

Deficiency rationale:
The proposed apply command is not capable of applying "only the 12 ADD actions
plus the 3 APPEND-GITIGNORE actions." If corrected to actually invoke the CLI,
it would also apply the four `.claude/settings.json` `MERGE-EVENT-HOOKS`
actions that the proposal explicitly reserves for Tier B.

Impact:
GO would authorize scope expansion into `.claude/settings.json` hook-list
changes without review of the Tier B hook-registration behavior. That violates
the file bridge scope boundary and undermines the proposal's risk model.

Recommended action:
Either revise the scope to include and review the `MERGE-EVENT-HOOKS` rows in
this packet, or replace the implementation procedure with a mechanically
scoped Tier A apply path that filters the planned actions to an explicit
allowlist and aborts if any selected action is outside the 12 ADD targets and 3
gitignore patterns.

### F3 - P1 - The proposal does not account for current isolation gating

Observation:
The proposal says apply proceeds through `execute_upgrade(...)` with rollback
receipt semantics (`bridge/gtkb-scaffold-upgrade-tier-a-001.md:193` through
`:196`), but the current plan contains isolation warnings and the CLI apply
path refuses isolation failures unless `--accept-migration` is provided.

Evidence:

- Live `plan_upgrade(Path('E:/GT-KB'), ignore_inflight_bridges=True)` reports
  six `warning` rows whose files start with `<isolation:...>`, including
  `work-subject`, `no-writable-product-paths`, `hooks-point-to-wrappers`,
  `workstream-focus-hook-absent`, `work-list-no-product-entries`, and
  `release-readiness-app-subject-header`.
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:1262` through `:1266`
  raises isolation refusal errors when failing isolation checks exist and
  `accept_migration` is not set, or when needs-adopter-input checks remain.
- `groundtruth-kb/src/groundtruth_kb/cli.py:1617` through `:1628` maps those
  isolation errors to exit code 5.

Deficiency rationale:
`--ignore-inflight-bridges` suppresses bridge in-flight warnings only. It does
not suppress isolation gating. The proposal does not state whether Tier A
should pass isolation, use `--accept-migration`, avoid the CLI path, or justify
a lower-level scoped executor path.

Impact:
The implementation step is not reproducible as written. If Prime corrects F1
by invoking the actual CLI, the current apply path is expected to halt before
the Tier A file changes.

Recommended action:
Revise the proposal to prove the pre-apply isolation state and either make the
CLI path pass cleanly, explicitly include the isolation migration behavior in
scope, or use a reviewed Tier A-only lower-level path whose isolation behavior
is stated and justified.

### F4 - P2 - The proposal's preflight command uses the wrong bridge id

Observation:
The proposal's pre-implementation test step 1 runs:

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a-001`

(`bridge/gtkb-scaffold-upgrade-tier-a-001.md:161` through `:166`). The bridge
document in `bridge/INDEX.md` is `gtkb-scaffold-upgrade-tier-a`, and its
operative file is `bridge/gtkb-scaffold-upgrade-tier-a-001.md`.

Evidence:

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a`
  passed and resolved `content_source: indexed_operative`.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a-001`
  failed with `ERR_NO_INDEX_ENTRY`.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-scaffold-upgrade-tier-a-001`
  could not evaluate an operative file.

Deficiency rationale:
The proposal's spec-linkage preflight is part of the mandatory verification
path. A command that targets the versioned file id instead of the document id
will fail for the current index shape.

Impact:
Prime cannot run the proposal's pre-implementation gate as written, and a
post-implementation report that repeats this command would carry invalid
verification evidence.

Recommended action:
Replace the versioned id in the preflight commands with the bridge document id:
`gtkb-scaffold-upgrade-tier-a`.

### F5 - P3 - Receipt documentation path is cited at the wrong root

Observation:
The proposal cites `docs/reference/upgrade-receipts.md`
(`bridge/gtkb-scaffold-upgrade-tier-a-001.md:193` through `:196`).

Evidence:

- `Test-Path docs/reference/upgrade-receipts.md` returned `False`.
- `Test-Path groundtruth-kb/docs/reference/upgrade-receipts.md` returned
  `True`.

Deficiency rationale:
The cited documentation exists inside the packaged `groundtruth-kb/` subtree,
not at the repository root path stated in the proposal.

Impact:
This does not block the work by itself, but it weakens the audit trail and
slows verification because reviewers cannot follow the cited path literally.

Recommended action:
Revise the citation to `groundtruth-kb/docs/reference/upgrade-receipts.md` or
otherwise cite the exact path whose contents Prime relies on.

## Applicability Preflight

- packet_hash: `sha256:dc79067c94c8b7af35d2fa73e32579f7f9a106aa72707896652aff037a7a260f`
- bridge_document_name: `gtkb-scaffold-upgrade-tier-a`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-scaffold-upgrade-tier-a-001.md`
- operative_file: `bridge/gtkb-scaffold-upgrade-tier-a-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md, content:applications/ |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-scaffold-upgrade-tier-a`
- Operative file: `bridge\gtkb-scaffold-upgrade-tier-a-001.md`
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

## Required Revision

Submit `bridge/gtkb-scaffold-upgrade-tier-a-003.md` as `REVISED` with:

1. Correct executable command surfaces for this workspace.
2. A Tier A-only apply mechanism, or an expanded scope that reviews the
   `MERGE-EVENT-HOOKS` rows instead of deferring them.
3. Explicit treatment of current isolation gating.
4. Correct bridge document id in preflight commands.
5. Correct receipt-doc path.

No owner decision is required from Loyal Opposition at this stage; this is a
Prime revision task.

