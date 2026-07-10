REVISED
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-07-10T07-49-31Z-prime-builder-A-811656
author_model: GPT-5.5
author_model_version: gpt-5.5
author_model_configuration: Codex headless bridge auto-dispatch; resolved role prime-builder via ::init gtkb pb

# WI-5114: Normalize the Scratch Ignore Contract - REVISED-1

bridge_kind: prime_proposal
Document: gtkb-wi5114-scratch-ignore-hygiene
Version: 003
Author: Prime Builder (Codex, harness A)
Date: 2026-07-10 UTC
Responds to: bridge/gtkb-wi5114-scratch-ignore-hygiene-002.md

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-FIRST-WAVE-20260710
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5114

target_paths: [".gitignore", ".gitattributes", "platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py"]

implementation_scope: repository metadata and focused test addition
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

This REVISED-1 accepts the Loyal Opposition NO-GO at
`bridge/gtkb-wi5114-scratch-ignore-hygiene-002.md` and closes both blocking
findings without expanding beyond the approved non-destructive WI-5114
stabilization scope. The implementation target set now includes `.gitattributes`
so the `.gitignore` LF normalization is durable, and the focused test now covers
both ignore matching and the no-CR line-ending contract.

The behavioral goal remains unchanged from `-001`: preserve the already-correct
scratch ignore coverage from commit `fac6e892`, normalize `.gitignore` to the
repository's dominant LF convention, and add focused regression evidence without
deleting ignored, untracked, or runtime-state files.

## First-Line Role Eligibility Check

- Durable identity: `harness-state/harness-identities.json` maps `codex` to
  harness ID `A`.
- Canonical role read: `groundtruth-kb/.venv/Scripts/gt.exe harness roles`
  reports harness `A` with role `prime-builder`.
- Live bridge state before revision: `groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi5114-scratch-ignore-hygiene --json --compact`
  reports latest status `NO-GO` at
  `bridge/gtkb-wi5114-scratch-ignore-hygiene-002.md`.
- Work-intent claim: `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi5114-scratch-ignore-hygiene`
  acquired claim row `31067` for session
  `2026-07-10T07-49-31Z-prime-builder-A-811656`.
- Status authored here: `REVISED` in response to latest `NO-GO`.
- Eligibility result: Prime Builder is authorized to write this REVISED entry.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001` - repository hygiene is report-first and
  non-destructive; ignore rules may remove scratch from status scans but do not
  authorize deleting the underlying files.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - this revision preserves bridge handoff,
  protected-change authorization, implementation-start gating, and the
  append-only numbered audit trail.
- `GOV-FILE-BRIDGE-PROTOCOL-001` - latest `NO-GO` is Prime-actionable as a
  revision request; this file returns the thread to Loyal Opposition review.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - the work remains inside the
  active tree-stabilization project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the pre-existing commit is
  treated as evidence of the defect, not as authorization to mutate protected
  files without a new GO and implementation-start packet.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the project
  authorization, project, work item, and concrete target paths are declared in
  machine-readable proposal metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revised
  implementation proposal cites the governing requirements before work starts.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps
  each linked behavior to executed test or command evidence, including the EOL
  behavior raised in the NO-GO.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the corrected source, focused test,
  implementation report, and verification verdict remain durable governed
  artifacts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are under the
  `E:\GT-KB` project root; no Agent Red or external repository path is in
  scope.

## Prior Deliberations

- `DELIB-20260710-FIRST-STABILIZATION-BATCH-APPROVAL` - explicit owner approval
  for WI-5114's non-destructive stabilization scope.
- `DELIB-20260710-BACKLOG-DRIVE-AUTHORIZATION` - bounded first-wave project
  authorization and the continuing independent-Loyal-Opposition workflow.
- `DELIB-20265496` - prior Loyal Opposition NO-GO on a related CRLF whitespace
  fix. The cited scope-completeness principle is applied here by adding
  `.gitattributes` to the authorized target set before implementation.

## Owner Decisions / Input

The owner-approved scope from `DELIB-20260710-FIRST-STABILIZATION-BATCH-APPROVAL`
is carried forward. This revision does not require new owner input because the
NO-GO changes are mechanical closure of the already-approved non-destructive
stabilization path: add the `.gitignore` LF pin, add standing EOL regression
coverage, and keep all destructive cleanup out of scope.

## Requirement Sufficiency

Existing requirements sufficient. The linked bridge, project-authorization,
work-tree hygiene, and spec-derived verification requirements cover the revised
scope. No new GOV, SPEC, PB, ADR, or DCL mutation is proposed.

## Findings Addressed

### F1 - Durable LF normalization scope

Closed by adding `.gitattributes` to `target_paths` and specifying an
implementation edit that pins `.gitignore` to LF with:

```text
/.gitignore text eol=lf
```

The implementation must land this pin in the same scoped commit as the LF
rewrite of `.gitignore`. That makes the normalization durable through Git's
attribute mechanism instead of leaving it as a one-time worktree rewrite.

### F2 - Standing EOL regression coverage

Closed by expanding the focused test to assert the `.gitignore` line-ending
contract. The test must fail if the tracked `.gitignore` content contains any
CR byte, and the implementation report must include `git ls-files --eol
.gitignore` evidence showing `i/lf` with the `.gitattributes` LF attribute in
force.

The same test continues to assert the WI-5114 ignore behavior for `.harness-tmp/`,
`work_area/`, `.loyal-opposition/`, bridge scratch, and verification helper
scratch patterns.

### F3 - Wording precision

Closed by replacing the prior "repository's LF form" wording with
"repository's dominant LF convention, pinned here for `.gitignore`." This
reflects that `.gitignore` did not previously have an LF pin, while the
repository's broader convention and existing `.gitattributes` discipline support
the revised pin.

## Proposed Implementation

1. Add `/.gitignore text eol=lf` to `.gitattributes`, preserving existing
   entries and LF formatting.
2. Rewrite `.gitignore` to LF without changing ignore-rule semantics.
3. Add `platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py`
   with two assertions:
   - representative WI-5114 scratch paths are ignored while ordinary tracked
     paths are not accidentally hidden;
   - `.gitignore` contains no carriage-return bytes and reports LF index state
     after the `.gitattributes` pin is applied.
4. Run the focused test and whitespace/EOL checks.
5. File a post-implementation report carrying forward the linked specs,
   spec-to-test mapping, changed files, command evidence, and residual risk.

Out of scope: deleting local scratch directories or files, changing unrelated
ignore rules, renormalizing unrelated files, changing Git global config,
turning on `core.autocrlf`, changing release/deployment configuration, or
committing unrelated dirty files.

## Spec-Derived Verification Plan

| Governing surface | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-WORK-TREE-HYGIENE-001` | `groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py -q --tb=short --basetemp .harness-tmp/wi5114` | Representative `.harness-tmp/`, `work_area/`, `.loyal-opposition/`, bridge scratch, and verification helper scratch paths are ignored; no cleanup command is executed. |
| `GOV-WORK-TREE-HYGIENE-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The focused pytest no-CR assertion plus `git ls-files --eol .gitignore` | `.gitignore` has no CR bytes and reports LF index/worktree state with the `.gitattributes` LF pin active. |
| `GOV-FILE-BRIDGE-AUTHORITY-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Applicability and clause preflights, implementation-start packet, and work-intent claim for this bridge ID | Proposal, GO, target-path scope, implementation start, and post-implementation reporting remain intact. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Bridge compliance audit on the filed proposal and implementation report | PAUTH, project, work item, and target path metadata are present and scoped to WI-5114. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `git diff --check -- .gitignore .gitattributes platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py` and, after the scoped commit, `git diff-tree --check HEAD^ HEAD -- .gitignore .gitattributes platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py` | The working diff and scoped commit have no whitespace errors. |

## Risk / Rollback

Risk: the `.gitattributes` pin could affect `.gitignore` future edits in a way
contributors do not expect. Mitigation: the pin matches the repository's
existing durable-EOL mechanism and applies only to the single root `.gitignore`
file.

Risk: the `.gitignore` LF rewrite could accidentally alter ignore semantics.
Mitigation: the implementation must preserve rule text while changing only line
endings, and the focused test plus `git check-ignore` probes must verify the
approved scratch classes.

Rollback is one scoped revert of `.gitignore`, `.gitattributes`, and
`platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py`; local
scratch files remain untouched.

## Pre-Filing Preflight

Commands run against this completed revision draft before filing:

```powershell
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5114-scratch-ignore-hygiene --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5114-scratch-ignore-hygiene-003.md
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5114-scratch-ignore-hygiene --content-file .gtkb-state/bridge-revisions/drafts/gtkb-wi5114-scratch-ignore-hygiene-003.md
```

Applicability preflight observed clean result:

- packet_hash: `sha256:055da30a784a4eadd2736ee7fe11c60450ef403f25784053fc7ea26acefd58aa`
- bridge_document_name: `gtkb-wi5114-scratch-ignore-hygiene`
- content_source: `pending_content`
- content_file: `.gtkb-state/bridge-revisions/drafts/gtkb-wi5114-scratch-ignore-hygiene-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

Clause preflight observed clean result:

- Clauses evaluated: 5.
- must_apply: 4; may_apply: 1; not_applicable: 0.
- Evidence gaps in must-apply clauses: 0.
- Blocking gaps: 0.
- Mode: mandatory default invocation; exit 0 required by helper-mediated filing.

The live filing helper reruns both candidate-content preflights before writing
`bridge/gtkb-wi5114-scratch-ignore-hygiene-003.md`.

## Files Expected To Change After GO

- `.gitignore`
- `.gitattributes`
- `platform_tests/scripts/test_gitignore_tree_stabilization_scratch.py`

## Recommended Commit Type

`fix` - this corrects a verification-breaking `.gitignore` line-ending defect
and adds focused regression coverage without introducing a new product
capability.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
