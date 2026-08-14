GO
::init gtkb pb
::open build

bridge_kind: lo_verdict
Document: gtkb-wi6280-verified-closure-ancestor-coverage
Version: 002
Author: Loyal Opposition (harness B, session 37676db4-47bd-4ba1-8208-e1e3d03313e8)
Date: 2026-08-14 UTC

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 37676db4-47bd-4ba1-8208-e1e3d03313e8
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via the canonical init keyword

# Loyal Opposition Review — Widen VERIFIED Closure Coverage to Ancestor Commits

Responds to: bridge/gtkb-wi6280-verified-closure-ancestor-coverage-001.md

## Verdict

**GO.** The defect is real and reproduced, the mechanism is correctly located,
the ancestry constraint is the right bound on a gate-loosening change, and the
owner decision selecting this remedy is on record.

The proposal asks the reviewer to scrutinise its project re-homing rather than
take it as given, and offers the ground on which it should be NO-GO'd. That
challenge is answered directly below: the re-home survives, on substantive
grounds independent of its convenience.

## Review Independence

Author session context `a49752e4-5a9f-4290-bceb-910693b5271f`
(`prime-builder/claude/B`); reviewer session context
`37676db4-47bd-4ba1-8208-e1e3d03313e8` (`loyal-opposition/claude/B`, model
`claude-opus-5`). Distinct; independence holds.

**Disclosure with unusual weight here.** This reviewer authored the terminal
`VERIFIED` verdicts for both threads the proposal uses as its worked example —
`gtkb-wi6221-tool-use-is-a-test-directive` (`0e770e89d`) and
`gtkb-wi6267-parity-projection-contract` (`f5e10d902`). That is a conflict
worth naming: the proposal's central evidence is this reviewer's own output.
It also means the "these are genuinely complete" half of the claim rests on
first-hand knowledge rather than inference, which is stated so the owner can
weigh it either way.

## The Project Re-Homing — the challenge the proposal raised

**Upheld. This is bridge-protocol work.**

The proposal discloses that `WI-6280` was created under
`PROJECT-GTKB-GET-HEALTHY-PHASE-2` and filed under
`PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`, that the move is *convenient*
because the Phase-2 authorization is include-listed and does not name
`WI-6280` while this project's is list-free, and that if the work is Phase-2
scope the correct path is an owner-approved include-list amendment and this
filing should be NO-GO'd.

Verified rather than accepted:

- **The convenience is real.** `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
  v2 is `active` with `included_work_item_ids` empty — genuinely list-free —
  and its class set (`source`, `test`, `test_addition`, `configuration`,
  `documentation`, `metadata`, `governance_evidence`, `bridge`) covers this
  thread without amendment. So the incentive the proposal names exists.
- **The substantive grounds hold independently.** The changed surface is
  `scripts/bridge_verified_backlog_reconciler.py`, which implements
  `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`. That is bridge-protocol
  closure infrastructure. Nothing in scope touches baseline neutralization,
  projection, or any Phase-2 deliverable.
- **The precedent is consistent, not constructed.** `WI-6277`, `WI-6278` and
  `WI-6279` — the three sibling defects from the same investigation — are all
  recorded under `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`. The re-home
  follows a pattern set before this thread existed.

The proposal's own framing is the correct test and it passes: Phase 2 is the
**victim** of this defect, not its scope. Two Phase-2 items cannot close
*because* the bridge closure path is broken; that makes Phase 2 the beneficiary
of the repair, not its owner. A defect is homed by what it breaks, not by who
is inconvenienced.

Had the substantive grounds been absent, the convenience would have decided it
and this would be a NO-GO. They are present, so it is not.

## Findings

### Confirmed — the defect, at source

`scripts/bridge_verified_backlog_reconciler.py` line 445, read directly:

```python
missing = [path for path in (verdict_rel_path, *target_paths) if not _target_covered_by_commit(path, changed_paths)]
```

Every implementation `target_path` is tested against the changed-path set of
the single commit that last touched the verdict file. Work committed before the
verdict cannot satisfy it, and commit history does not change, so the block is
permanent — as claimed.

### Confirmed — the two governed mechanisms genuinely conflict

This is the part that makes the change necessary rather than merely convenient.

- `.claude/rules/file-bridge-protocol.md` § "Mandatory VERIFIED
  Commit-Finalization Gate" requires one transaction carrying the verified
  implementation paths **and** the verdict artifact.
- `.claude/rules/auto-finalization-sweep.md`, owner-authorized under
  `DELIB-20266278`, states the invariant "**Verdict-file only** — the sweep
  commits only `bridge/*.md` files; it never stages source or test files", and
  gates eligibility on the implementation being *already committed separately*.

A thread finalized under the second can never satisfy the first. Both are
governed and owner-authorized, so this is not a defect in either rule's
application — it is an unresolved contradiction between them, and the owner AUQ
recorded in this proposal is the settlement.

### Confirmed — the worked example, with first-hand knowledge

`WI-6221` and `WI-6267` both read `Stage: backlogged`, `Resolution Status:
open` against live MemBase, while their bridge threads are terminal `VERIFIED`
and their implementations are committed. This reviewer verified and finalized
both earlier today, so the "implemented, verified and committed" half is not
inferred from the proposal.

The shape is exactly as described: the finalization commit carries only bridge
files, the implementation sits in an earlier commit, and coverage reports
`false`.

### The ancestry constraint is the correct bound

The change loosens a gate, so the whole review turns on what stops it
loosening too far. Scope 3 is that bound: a path whose latest commit is not an
ancestor of the verdict commit stays uncovered, implemented via
`git merge-base --is-ancestor`. This correctly rejects both failure modes that
matter — implementation committed *after* verification, and implementation on
an unrelated branch — and two tests pin each directly.

Scope 2 keeping the verdict file's own same-commit rule intact is equally
important and correctly preserved: the "a verdict exists and is committed"
invariant does not move, so `GOV-FILE-BRIDGE-AUTHORITY-001`'s audit-trail
property survives the change.

The residual risk the proposal accepts — that ancestor-committed work is
trusted as what the verdict verified, on the strength of the verdict's own
`target_paths` — is stated accurately. That is the same trust the same-commit
rule already placed in the declaration; only the commit boundary moves. Worth
the owner knowing it is a trust relocation, not a trust removal.

### Scope item 4 (apply) needs no separate approval

Running the reconciler with `--apply` across up to 65 rows is a MemBase
mutation, correctly declared (`kb_mutation_in_scope: true`, `groundtruth.db` in
`target_paths`), and operation-time evaluation returns `allowed: true`.

It also requires no additional owner decision on its own account:
`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` makes VERIFIED-driven
completion and retirement automatic *without* owner confirmation. Applying the
reconciler is what that governance specifies, not an extra step this thread
invents.

## Positive Confirmations

- **Both preflights pass**: `preflight_passed: true`,
  `missing_required_specs: []`, `blocking_errors: []`,
  `unclassified_target_paths: []`; clause preflight exit 0, zero blocking gaps;
  operation-time `allowed: true` including the KB-mutation path.
- **Out-of-scope list is disciplined and correct**: the `by_reference_waiver`
  path is left untouched, `--repair-overbroad` is untouched, the
  `linked_bridge_not_verified` class (304 items) is correctly identified as a
  different question, and neither governed rule's *text* is edited — the
  proposal changes behavior to match the owner's settlement rather than quietly
  rewriting a rule.
- **The verification plan tests the constraint, not just the feature**: three of
  nine rows exist to prove the gate still refuses things (`committed after
  verdict`, `unrelated branch`, `never committed`), which is the right balance
  for a loosening change.
- **Regression floor is the full module set**, with any pre-existing failures to
  be shown identical at `HEAD` — the method established on the parity thread.
- **Honest scoping of the sweep's role**: only 2 commits match the sweep's
  finalization pattern, and the proposal says so, declining to overstate the
  sweep as the sole source when any commit-before-verdict workflow produces the
  shape.
- **Root boundary**: all three `target_paths` entries within `E:\GT-KB`.

## Verification Expectations

- **V1** — the live before/after `--dry-run` comparison is reported with actual
  counts, and `missing_implementation_commit_coverage` is shown falling from
  65. The report must state the *after* number, not merely that it fell.
- **V2** — `WI-6221` and `WI-6267` specifically move to resolved, since they are
  the named worked example.
- **V3** — the three negative rows pass: a path committed after the verdict, a
  path on an unrelated branch, and a never-committed path all remain uncovered.
  A report showing only positive rows has not demonstrated the bound holds.
- **V4** — the applied set is enumerated in the implementation report, per the
  proposal's own rollback commitment, so any subset can be reversed by
  compensating version.
- **V5** — full `test_bridge_verified_backlog_reconciler*.py` module set with
  pre-existing failures shown identical at `HEAD`; both ruff gates run
  separately.

## Applicability Preflight

- packet_hash: `sha256:a7e078dab0726fefb036d9ee763cf22d48047f52c29fadc4abe17e550c94f311`
- candidate_evidence_hash: `sha256:337f0def5086ce481bbda77de4e48631224663152ebf0440bc977992583815e3`
- bridge_document_name: `gtkb-wi6280-verified-closure-ancestor-coverage`
- declared_target_paths: ["groundtruth.db", "platform_tests/scripts/test_bridge_verified_backlog_reconciler_ancestor_coverage.py", "scripts/bridge_verified_backlog_reconciler.py"]
- applicability_path_evidence: ["bridge/*.md`", "groundtruth.db", "platform_tests/scripts/test_bridge_verified_backlog_reconciler_ancestor_coverage.py", "scripts/bridge_verified_backlog_reconciler.py", "scripts/bridge_verified_backlog_reconciler.py`"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi6280-verified-closure-ancestor-coverage-001.md`
- operative_file: `bridge/gtkb-wi6280-verified-closure-ancestor-coverage-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
- blocking_errors: []

### Project Authorization Operation-Time Evaluation

- phase: `proposal`
- status: `allowed`
- reason_code: `allowed`
- authorization_id: `PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730`
- authorization_version: `2`
- project_id: `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY`
- authorization_source: `bridge/gtkb-wi6280-verified-closure-ancestor-coverage-001.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["groundtruth.db", "platform_tests/scripts/test_bridge_verified_backlog_reconciler_ancestor_coverage.py", "scripts/bridge_verified_backlog_reconciler.py"]
- allowed: `true`
- evaluator: `project-authorization-operation-time-enforcement` v`1`
- evaluator_sha256: `F67A2F9A31DEB6A98B253580570FCBD7526FA6875BE01F0DD94C987943B2BF42`
- taxonomy: v`2` `8FC36B9EAC57B15E1F431B5E8B30935B5EFFC9526DFB898DF3CE75CBD22C9C7E`

| Operation | Allowed | Reason Code | Reason |
| --- | --- | --- | --- |
| `implementation_packet_create` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |
| `implementation_start` | `true` | `allowed` | The requested operation and every target class are PAUTH-allowed. |

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6280-verified-closure-ancestor-coverage` — exit 0 (mandatory mode).

- Evidence gaps in must_apply clauses: 0
- **Blocking gaps: 0**

### Blocking Gaps

None.

## Prior Deliberations

- `DELIB-20266278` — owner authorization of the treadmill-drain program and the
  auto-finalization sweep whose verdict-only invariant is one side of the
  conflict this thread settles.
- `WI-4889` / `WI-4871` — the sweep and the untracked-VERIFIED guard it drains;
  relevant because the rejected option would have re-opened that treadmill.
- `WI-6277`, `WI-6278`, `WI-6279` — the sibling defects establishing the
  re-homing precedent, verified as recorded under this project.
- `bridge/gtkb-wi6221-tool-use-is-a-test-directive-004.md` and
  `bridge/gtkb-wi6267-parity-projection-contract-006.md` — the two terminal
  verdicts this reviewer authored that constitute the worked example.
- The proposal's own note that no prior deliberation proposed an ancestry-based
  rule is consistent with this reviewer's searches this session; the
  same-commit requirement appears to predate consideration of the split-commit
  case.

## Backlog Conflict Check

`WI-6280` governs. The `linked_bridge_not_verified` class (304 items) is
explicitly excluded and remains open work. `WI-6277`/`6278`/`6279` are siblings
in the same project, not duplicates of this scope. No interference found.

## Methodology

Read-only inspection. No source file was modified and no repair was pre-applied.

Commands executed:

```text
gt bridge state-report
gt bridge show gtkb-wi6218-membase-committable-dump   (contention check, separate thread)
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi6280-verified-closure-ancestor-coverage
gt backlog show WI-6221 ; gt backlog show WI-6267            (worked example state)
gt backlog show WI-6277 ; WI-6278 ; WI-6279                  (re-homing precedent)
Get-Content scripts/bridge_verified_backlog_reconciler.py    (line 445 claim)
groundtruth-kb/.venv/Scripts/python.exe -c "<project_authorizations read: status, included_work_item_ids, allowed_mutation_classes>"
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi6280-verified-closure-ancestor-coverage
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6280-verified-closure-ancestor-coverage
```

**Not verified:** the `--dry-run` census (399 candidates, 14 resolve, 65
missing coverage, and the four other skip-reason counts) was not re-run — it
is a long full-backlog scan, and V1 requires it to be re-measured and reported
at verification time anyway. The two named worked-example items were confirmed
individually instead, which is the load-bearing part. The `git merge-base
--is-ancestor` memoization behaviour was not exercised.

## Recommended Commit Type

Recommended commit type: `fix`

Matches the described diff — one function widened plus regression tests,
repairing a governed behavior that is specified but not firing. No new
capability surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
