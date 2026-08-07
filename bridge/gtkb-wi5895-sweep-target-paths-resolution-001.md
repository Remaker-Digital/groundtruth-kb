NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: f60c8a1c-ab58-4887-a466-8b8444126390
author_model: Claude Opus 5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb; build activity envelope
author_metadata_source: session envelope (worker_role_provenance)

bridge_kind: prime_proposal
Document: gtkb-wi5895-sweep-target-paths-resolution
Version: 001
Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5895
Recommended commit type: fix:
target_paths: ["scripts/auto_finalize_sweep.py", "platform_tests/scripts/test_auto_finalize_sweep_target_paths.py"]

# GT-KB Bridge Implementation Proposal - WI-5895 sweep target_paths resolution - 001

## Bridge Filing Discipline

Filed as `bridge/gtkb-wi5895-sweep-target-paths-resolution-001.md`, the first
entry in a new append-only chain of numbered bridge files; prior versions are
never deleted or rewritten. Written through
`scripts.gtkb_bridge_writer.write_bridge_file` so the file carries a consumed
publication-capability receipt.

## Problem

The auto-finalization sweep asks the wrong file for `target_paths`, so it can
never satisfy its own "implementation already committed" precondition for the
large majority of terminal verdicts.

Exact chain in `scripts/auto_finalize_sweep.py`:

- L320 `m = _RESPONDS_RE.search(content)` - resolves the responded-to path from the verdict.
- L333 `report_content = _read(report_rel)` - reads the **implementation report**.
- L334 `targets, tp_why = _target_paths(report_content or "")`
- L219-229 `_target_paths(...)` -> `return extract_target_paths(report_content), "ok"`

Implementation reports do not re-declare `target_paths:`; by convention they
carry a `## Files Changed` prose section. `extract_target_paths` therefore raises
`AuthorizationError("Approved proposal is missing concrete target_paths or Files
Expected To Change")`, which is **verbatim** the sweep's logged skip reason.

Confirmed empirically this session against `gtkb-w0-gate-false-positive-repair`:
`-001` (approved proposal) parses **16 paths** cleanly; `-003` (implementation
report) raises exactly that exception.

WI-5894 established the population: of 25,545 recorded skips, unparseable target
paths account for **20,135 events across 79 distinct verdicts (~79%)**, versus
237 events over 9 verdicts (<1%) for body validation.

## Why the obvious fix is insufficient

The intuitive repair is to follow the report's `Approved proposal:` line to the
GO'd proposal. A repository-wide census taken for this proposal shows that would
under-deliver:

| Measure | Count |
| --- | --- |
| Numbered bridge files | 15,576 across 2,511 chains |
| Files declaring `target_paths:` | 4,983 |
| Files declaring `Approved proposal:` | **1,667** |
| Files declaring `Responds to:` | 6,589 |
| **Chains where a backward walk finds `target_paths`** | **1,973 / 2,511 (78.6%)** |
| Chains with no `target_paths` anywhere | 538 (21.4%) |

`Approved proposal:` is present in only 1,667 of 15,576 files, so keying on it
leaves most chains unresolved. A **backward walk over the numbered chain** to the
most recent version carrying a parseable `target_paths:` line resolves 78.6% of
chains and depends on no single metadata key.

Note on the two ~79% figures: WI-5894's 79% measures *skip events attributable to
this cause*; the 78.6% here measures *chains resolvable by backward walk*. They
are different populations and must not be treated as the same number.

## Proposed Change

1. `scripts/auto_finalize_sweep.py` - replace the single-file lookup at L334
   with a resolver that walks the numbered chain backwards from the verdict
   version and returns the first parseable `target_paths:` declaration,
   preserving the existing report-first attempt as the first step so current
   behaviour is a strict subset. When no version in the chain declares
   `target_paths`, skip with a **distinct** reason (e.g.
   `no target_paths anywhere in chain`) so the 538-chain residue is
   distinguishable in `sweep.jsonl` from the current conflated message.
2. `platform_tests/scripts/test_auto_finalize_sweep_target_paths.py` (new) -
   fixture chains asserting: report-only declaration resolves; proposal-only
   declaration resolves via backward walk; no-declaration chain yields the
   distinct skip reason and does not raise; and the resolver never reaches
   outside its own slug's chain.

## Scope boundary - this finalizes nothing by itself

Per WI-5894, correcting this resolver moves affected verdicts from
skip-reason-one to skip-reason-two (protected-commit authorization) and
finalizes none on its own. That is the expected and intended outcome: the value
is that the sweep's reported reason becomes **true**, so the residual blockers
become visible instead of being masked by a resolver defect. No change to
commit behaviour, staging, or the sweep's verdict-file-only invariant is in
scope.

### KB / MemBase mutation scope

This implementation performs no MemBase mutation. It edits one script and adds
one test; it inserts, updates and retires nothing in `groundtruth.db`, which is
correctly absent from `target_paths`. Tests bind to fixture chains under
`tmp_path`, never canonical bridge state.

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-FILE-BRIDGE-AUTHORITY-001` already
requires a durable, accurate bridge audit trail, and the auto-finalization sweep
is governed narrative at `.claude/rules/auto-finalization-sweep.md`. This work
restores conformance; no new requirement is needed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail and finalization durability; the sweep exists to serve it.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` - the sweep's skip reason must reflect the actual blocking condition rather than a resolver artifact.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `GOV-WORK-TREE-HYGIENE-001` - ruff gates on the changed Python file.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the diagnosis was preserved on WI-5895 v3 before this proposal was drafted.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development decision underlying that stance.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - localising a P0 root cause is a capture-threshold event, discharged by WI-5895 v3 and this proposal.

## Owner Decisions / Input

- Owner instruction 2026-08-07 (session `f60c8a1c`), after both prior threads
  became blocked on manual Loyal Opposition: "Choose a task and keep working."
  WI-5895 was selected as the highest-priority item that is P0, open, unproposed,
  and whose root cause this session had already localised with evidence.
- Owner standing directive `DELIB-20260807-DISPATCHER-DISABLED-MANUAL-BRIDGE-OPERATION`
  applies: this proposal awaits a manual Loyal Opposition session and must not be
  read as requiring dispatch activation.
- No owner waiver is requested.

## Prior Deliberations

- WI-5894 - established the skip-reason distribution (20,135 events / 79 verdicts / ~79%) and the caveat that fixing one floor moves verdicts to the next.
- WI-5895 v3 - carries this session's root-cause localisation, cited above.
- WI-5825 - the recovery classes that constitute the downstream residue once this resolver is correct.
- `DELIB-202667533` (AT-01) - owner-ratified commit-first-publish-after finalization ordering.
- `DELIB-20266278` - owner authorization of the dispatch-treadmill-drain program, under which the sweep was built.
- `bridge/gtkb-w0-gate-false-positive-repair-001.md` / `-003.md` - the specimen chain used for empirical confirmation.

## Specification-Derived Verification Plan

| Specification / requirement | Test or verification command | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` resolver correctness | `pytest platform_tests/scripts/test_auto_finalize_sweep_target_paths.py -q` | proposal-only chain resolves via backward walk; report-only chain still resolves |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` reason truthfulness | no-declaration fixture chain | distinct skip reason emitted; no exception; not conflated with the resolver defect |
| Chain isolation | fixture with two adjacent slugs | resolver never reads outside its own slug's chain |
| Regression safety | `pytest platform_tests/scripts/test_auto_finalize_sweep*.py -q` | existing sweep tests remain green |
| `GOV-WORK-TREE-HYGIENE-001` | `ruff check` and `ruff format --check` on the changed file | clean on both gates |

## Risk / Rollback

- **Risk: widening what the sweep will act on.** Mitigated because the sweep's
  other invariants are untouched - independence, implementation-already-committed,
  the finalization/checker floor, and verdict-file-only staging all still gate the
  commit. A resolved `target_paths` list only lets the sweep evaluate those gates
  instead of skipping before reaching them.
- **Risk: backward walk picks a stale declaration.** Mitigated by taking the most
  recent declaring version at or before the verdict, and by the chain-isolation
  test.
- **Risk: no measurable finalization improvement.** Expected, per the scope
  boundary; the deliverable is reason-truthfulness, not finalization count.
  Reviewers should not treat an unchanged finalize count as failure.
- **Rollback:** revert the single script and delete the test. The sweep is
  stateless between runs and fail-soft by design, so rollback carries no
  operational risk.

## Recommended Commit Type

- Recommended commit type: `fix:` - repairs an incorrect argument to an existing
  resolver plus its skip-reason reporting; no new capability surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
