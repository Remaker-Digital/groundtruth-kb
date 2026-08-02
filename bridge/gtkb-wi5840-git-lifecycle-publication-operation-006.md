NO-GO
author_session_context_id: 019fbbaf-1da4-74c3-a48a-c287cbe4361f

# Loyal Opposition Review — WI-5840 revised governed publication report

bridge_kind: lo_verdict
Document: gtkb-wi5840-git-lifecycle-publication-operation
Version: 006
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5840-git-lifecycle-publication-operation-005.md
Controlling GO: bridge/gtkb-wi5840-git-lifecycle-publication-operation-002.md

## Verdict: NO-GO — verification evidence remains incomplete

The report is substantially more evaluable than version 003: it now supplies
implementation-start evidence, a specification-to-test mapping, commands, and
an explicit disclosure of its remaining coverage gaps.  It nevertheless cannot
receive `VERIFIED`.  The approved proposal required an individual test for
*every* enumerated fail-closed condition, whereas version 005 identifies seven
conditions that the current publication test module does not exercise.  A
passing 16-test lane is positive evidence, not evidence that the omitted paths
stop before their next side effect.

No terminal verdict or commit-finalization attempt was made.

## Findings

### P1 — seven approved fail-closed conditions lack publication-path tests

**Observation.** Version 001's verification matrix requires fixtures for the
empty range, unresolvable object, unexpected object type, index mutation,
incorrect candidate parentage, candidate more than one commit ahead, and the
source/destination rename denial. Version 005's `Disclosed coverage gaps`
section confirms those first six are untested and that the rename denial is
only indirectly covered by an existing `validate_remote_push` test. A fresh
read of `platform_tests/scripts/test_git_lifecycle_publication.py` finds 16
tests; none has a name or fixture for those seven cases. The enforcement paths
are present in `groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py`
at `_assert_candidate_shape`, `_enumerate_range`, and the pre-push index
recheck, but source presence is not executed specification-derived evidence.

**Impact.** The operation creates refs and can push. An unexercised
fail-closed branch can allow a side effect after a malformed range, changed
index, malformed candidate, or renamed destination has reached the operation.
The report's claim that every enumerated condition stops before the next side
effect is therefore not proven.

**Required revision.** Add focused fixtures in the already-declared
`platform_tests/scripts/test_git_lifecycle_publication.py` for all seven
conditions. Each must assert the exact denial/reason and that no later
mutating command occurs (`update-ref` and push where applicable). Re-run the
focused lane plus the three declared regression suites, ruff check, and ruff
format check; carry the new executed results into a `REVISED` report.

**Option rationale.** Exercising the approved gates is the minimal,
reversible path inside the existing target set. Treating the untested paths as
acceptable, or expanding the operation's scope, would weaken the original
acceptance criterion instead of proving it.

### P3 — current report omits one advisory applicability link

**Observation.** The fresh applicability preflight identifies
`DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` as an uncited advisory specification.

**Impact.** This does not block this `NO-GO`, but the report is less complete
than the governing applicability matrix expects and will create avoidable
review churn after the P1 evidence is added.

**Required revision.** Add that DCL to version 005's carried-forward
`Specification Links` and map its lifecycle evidence in the revised report.

## Positive verification

I independently ran:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_git_lifecycle_publication.py -q --tb=short
```

Result: `16 passed, 1 warning in 54.88s`. The warning is pytest's existing
unknown `asyncio_mode` configuration warning. This confirms the reported lane
passes but does not supply the seven missing cases above.

## Backlog approval observation — owner queue only

`groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-5840 --json` currently
reports `approval_state: "unapproved"`, `stage: "backlogged"`, and
`resolution_status: "open"`. This review makes no MemBase or backlog mutation.
The state is recorded for the owner's existing approval queue; it is not
implementation approval and must be reconciled by an owner-directed action.

## First-line eligibility and independence

- The owner-designated Loyal Opposition reviewer session is
  `019fbbaf-1da4-74c3-a48a-c287cbe4361f`.
- The reviewed REVISED report's author session is
  `f89ba0ce-8697-4a2b-91a5-0018de0b1f28`; it is different. No same-session
  review condition exists.
- Review eligibility is evaluated solely on those session contexts. No harness,
  dispatcher, durable-role, or model label was used as an eligibility rule.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:78c994cce8b5b0624ce84616439bdf48ee1902ee99f6b780bce9d0e801c8efef`
- bridge_document_name: `gtkb-wi5840-git-lifecycle-publication-operation`
- declared_target_paths: ["groundtruth-kb/src/groundtruth_kb/git_lifecycle/__main__.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/commands.py", "groundtruth-kb/src/groundtruth_kb/git_lifecycle/service.py", "platform_tests/scripts/test_git_lifecycle_publication.py"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5840-git-lifecycle-publication-operation-005.md`
- operative_file: `bridge/gtkb-wi5840-git-lifecycle-publication-operation-005.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: ["DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]
- blocking_errors: []
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5840-git-lifecycle-publication-operation`
- Operative file: `bridge\\gtkb-wi5840-git-lifecycle-publication-operation-005.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

## Prior Deliberations

- `DELIB-20260731-WI5840-PAUTH-PERMIT-GIT-COMMIT` — owner decision on the
  project PAUTH's finalization operation, which preserved all review and
  verification gates.
- `DELIB-20260730-CLEAN-BRANCH-PUBLICATION-CURRENT-HEAD-SELECTION` — bounded
  publication preparation does not authorize a push or waive later gates.
- `bridge/gtkb-wi5840-git-lifecycle-publication-operation-001.md` through
  `-005.md` — full chain read; version 005 openly reports the evidence gap.

## Prime Builder revision context

| Element | Required state |
| --- | --- |
| Objective | Prove every approved fail-closed publication condition before verification. |
| Preconditions | Resolve WI-5840's owner-approval state; keep the latest NO-GO and controlling GO intact. |
| Evidence paths | `service.py` guards and `test_git_lifecycle_publication.py` fixtures cited above. |
| File touchpoint | `platform_tests/scripts/test_git_lifecycle_publication.py`; do not broaden scope without a new reviewed proposal. |
| Sequence | Add seven fixtures; run focused and regression lanes; run both ruff gates; file `REVISED` with exact results. |
| Rollback | Revert only the new test additions through a separately governed change if they prove invalid. |
| Open decision | Owner reconciliation of WI-5840's `unapproved` backlog state. |

## Role-conflict corrective capture

Any labels assigning a role other than the owner's explicit Loyal Opposition
direction are conflict evidence only, not review-eligibility restrictions.
The duplicate-checked non-approval capture is
`bridge/gtkb-lo-role-authority-conflict-correction-001.md`; no duplicate
ADVISORY is created here.

## Non-approval boundary

This file is a Loyal Opposition verdict only. It authorizes no implementation,
backlog change, dispatcher/TAFE action, Git write, push, or release. No
non-bridge file was changed.
