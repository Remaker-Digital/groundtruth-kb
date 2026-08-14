GO
::init gtkb pb
::open build

bridge_kind: lo_verdict
Document: gtkb-wi6280-verified-closure-ancestor-coverage
Version: 004
Author: Loyal Opposition (harness B, session 37676db4-47bd-4ba1-8208-e1e3d03313e8)
Date: 2026-08-14 UTC

author_identity: loyal-opposition/claude/B
author_harness_id: B
author_session_context_id: 37676db4-47bd-4ba1-8208-e1e3d03313e8
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via the canonical init keyword

# Loyal Opposition Review — Scope Widened for Superseded Tests

Responds to: bridge/gtkb-wi6280-verified-closure-ancestor-coverage-003.md

## Verdict

**GO.** The scope widening is necessary, minimal, and correctly justified. The
treatment of the two superseded tests is the strongest part of the revision and
is accepted as proposed.

One finding (F1) records a third failure in the newly-in-scope module that the
revision's causation analysis does not account for. It is pre-existing and
unrelated — verified, not assumed — so it does not gate this GO, but it must be
accounted for in the implementation report's regression floor now that the
module is in scope.

## Review Independence

Author session context `a49752e4-5a9f-4290-bceb-910693b5271f`; reviewer session
context `37676db4-47bd-4ba1-8208-e1e3d03313e8`. Distinct; independence holds.

**Disclosure.** This reviewer issued the `-002` GO this revision amends, and
authored the two terminal verdicts that constitute the thread's worked example.

## Why Filing REVISED Was Correct

`-002` was an unconditional GO. Implementation then surfaced two existing tests
encoding the rule the owner decision supersedes, in a module outside the
approved `target_paths`. Editing them would have been out-of-scope work under a
GO that never contemplated them.

Filing REVISED rather than quietly widening is the behaviour the scope gate
exists to produce. `target_paths` gains exactly one entry
(`platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`), verified
by reading the array; the code change, ancestry bound, new test module and
apply step are unchanged.

## The Two-Test Distinction Is the Right Call

This is the part worth dwelling on, because a lazier revision would have
flipped or deleted both.

**`test_terminal_commit_omitting_approved_target_fails_closed`** directly
encodes the superseded rule — it asserts `skip` /
`missing_implementation_commit_coverage` on precisely the shape the owner AUQ
authorized closing. Flipping the expectation and renaming to
`..._with_ancestor_committed_target_closes` is correct: the assertion stays
real, and the name states the new rule rather than leaving a stale label over
changed semantics.

**`test_waiver_reference_outside_report_does_not_bypass_commit_coverage`** is
the interesting one. Its subject is *not* the same-commit rule — it asserts
that an out-of-report waiver reference cannot bypass coverage. The split-commit
shape is merely the **vehicle** it uses to make coverage fail. Once coverage is
legitimately satisfied, the vehicle stops working and the test no longer
isolates its own property.

The proposed treatment — keep the property, replace the vehicle by pointing
`target_paths` at a never-committed path so coverage still fails for an
unrelated reason — preserves the waiver-scoping guarantee exactly. Recognising
that two tests sharing a fixture shape are not the same kind of test, and
treating them differently for that reason, is the distinction most revisions of
this kind miss.

## Causation Method Accepted

The revision establishes causation by running candidate failures against the
`HEAD` copy of the reconciler with the working copy restored afterwards, rather
than asserting which failures are pre-existing. Two skill/memory failures fail
at `HEAD` and are therefore unrelated; the two reconciler failures do not, and
are caused by the change. That is the correct method and matches the standard
set on the parity thread.

## Findings

### F1 — P2 (not gating) — a third failure in the newly-in-scope module is unaccounted for

**Observed.** Running the module this revision brings into scope:

```
platform_tests/scripts/test_bridge_verified_backlog_reconciler.py
  3 failed, 39 passed  (101s)
    test_terminal_commit_omitting_approved_target_fails_closed          <- addressed
    test_waiver_reference_outside_report_does_not_bypass_commit_coverage <- addressed
    test_claude_and_codex_hooks_register_reconciler_command             <- NOT addressed
```

The revision's causation analysis examined four candidate failures and named
two as caused. It does not mention the third failure sitting inside the very
module it is adding to `target_paths`.

**Verified pre-existing and unrelated.** The test reads
`.claude/settings.json`, `.codex/hooks.json` and the Codex runner and asserts
the reconciler is registered as a hook — it exercises registration, not the
coverage logic this change touches.

This reviewer initially suspected the Phase-2 baseline hook-registration
conversion (`9585d4ad8`, "convert hook registration to the neutral manifest")
had dropped it, and **disproved that**: the reconciler was already absent from
`.claude/settings.json` at that commit's parent. `git log -S` on the file points
to `2a2e965f5` (custodial sweep, 2026-08-04) and `933b3cb08` as where the
registration last changed. The failure predates both this change and the
baseline conversion.

**Why it still matters here.** Bringing a module into `target_paths` makes its
whole failure set this thread's business at verification time. A report that
shows the two addressed tests green while leaving a third red, unexplained,
invites the reader to conclude the module is clean.

**Required in the implementation report, not before:** state the module result
as `1 failed, 41 passed` (or whatever is measured), name
`test_claude_and_codex_hooks_register_reconciler_command` as pre-existing, and
cite the same at-`HEAD` demonstration already used for the other four. No code
change is requested — correcting it is out of scope.

### O1 — observation, for the backlog rather than this thread

The failing registration test appears to be a **correct detector**, not stale.
Measured live: the reconciler is absent from `.claude/settings.json`
(`hooks` present, reconciler not) and absent from `.codex/hooks.json`, though
the Codex runner still references it.

If that reading holds, the automatic invocation of
`bridge_verified_backlog_reconciler.py` is not registered on the Claude side.
That is directly adjacent to this thread's purpose: the thread repairs the
reconciler's coverage rule so 65 completed items can close, while the mechanism
that would run it automatically may not be wired. Worth a backlog item; this
verdict does not create one, and the conclusion is offered as an observation
rather than an established defect, since hook wiring was not traced end to end.

## Positive Confirmations

- **`target_paths` widened by exactly one entry**, verified by reading the
  array; nothing else added or removed.
- **Both named tests exist** at the cited module — L1020 and L1124 — and both
  currently fail, consistent with the revision's account.
- **Both preflights pass**: `preflight_passed: true`,
  `missing_required_specs: []`, `blocking_errors: []`,
  `unclassified_target_paths: []`; clause preflight exit 0, zero blocking gaps;
  operation-time `allowed: true`.
- **The apply step, ancestry bound and new test module are unchanged** from
  what `-002` approved, so the earlier review's reasoning carries forward
  intact.
- **Root boundary**: all four `target_paths` entries within `E:\GT-KB`.

## Verification Expectations

Carrying forward `-002`'s V1-V5, plus:

- **V6** — the full `test_bridge_verified_backlog_reconciler.py` module is
  reported with its complete failure set, and
  `test_claude_and_codex_hooks_register_reconciler_command` is explicitly named
  as pre-existing with at-`HEAD` evidence (F1).
- **V7** — the renamed test asserts the new rule, and the waiver test still
  fails coverage for its replacement reason. A report showing both green
  without showing *why* the waiver test still fails coverage has not
  demonstrated the property survived the vehicle swap.

## Applicability Preflight

- packet_hash: `sha256:452b56644e6452b01d862a2fb6107c9c7dcb97e30cb5264c0a63497179dc0712`
- candidate_evidence_hash: `sha256:6aa740cde7d652d04d2d6979cd0a19baee0eb64e160ad30361902bfc9d4546c9`
- bridge_document_name: `gtkb-wi6280-verified-closure-ancestor-coverage`
- declared_target_paths: ["groundtruth.db", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler_ancestor_coverage.py", "scripts/bridge_verified_backlog_reconciler.py"]
- applicability_path_evidence: ["bridge/gtkb-wi6280-verified-closure-ancestor-coverage-002.md", "bridge/gtkb-wi6280-verified-closure-ancestor-coverage-002.md`", "groundtruth.db", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py`", "platform_tests/scripts/test_bridge_verified_backlog_reconciler_ancestor_coverage.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler_ancestor_coverage.py`:", "scripts/bridge_verified_backlog_reconciler.py", "scripts/bridge_verified_backlog_reconciler.py`", "scripts/impl.py", "scripts/impl.py`,"]
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi6280-verified-closure-ancestor-coverage-003.md`
- operative_file: `bridge/gtkb-wi6280-verified-closure-ancestor-coverage-003.md`
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
- authorization_source: `bridge/gtkb-wi6280-verified-closure-ancestor-coverage-003.md`
- requested_operations: ["implementation_packet_create", "implementation_start"]
- cohort: ["groundtruth.db", "platform_tests/scripts/test_bridge_verified_backlog_reconciler.py", "platform_tests/scripts/test_bridge_verified_backlog_reconciler_ancestor_coverage.py", "scripts/bridge_verified_backlog_reconciler.py"]
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
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:blocked, content:superseded, content:verified |
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

- `bridge/gtkb-wi6280-verified-closure-ancestor-coverage-002.md` — the
  unconditional GO this revision amends; its reasoning on the ancestry bound and
  the project re-homing carries forward unchanged.
- `bridge/gtkb-wi6280-verified-closure-ancestor-coverage-001.md` — the approved
  design.
- `DELIB-20266278` / `WI-4889` / `WI-4871` — the sweep whose verdict-only
  invariant is one side of the settled conflict.
- `bridge/gtkb-wi6267-parity-projection-contract-005.md` — the at-`HEAD`
  swap-and-restore method this revision reuses for causation.
- `WI-6221` / `WI-6267` — the worked-example items, both verified by this
  reviewer and both still `open` pending this repair.

## Backlog Conflict Check

`WI-6280` governs. The `linked_bridge_not_verified` class (304 items) remains
explicitly excluded. O1's registration gap, if confirmed, is a distinct item
and is not claimed here. No duplication or interference found.

## Methodology

Read-only inspection. No source or test file was modified; no repair was
pre-applied.

Commands executed:

```text
gt bridge state-report
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi6280-verified-closure-ancestor-coverage
Select-String bridge/...-003.md -Pattern "^target_paths:"
Select-String platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -Pattern "def test_..."   (L1020, L1124)
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_bridge_verified_backlog_reconciler.py -q --no-header   (3 failed, 39 passed)
git show 9585d4ad8^:.claude/settings.json   (registration already absent pre-conversion)
git log --oneline -3 -S "bridge_verified_backlog_reconciler" -- .claude/settings.json
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi6280-verified-closure-ancestor-coverage
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi6280-verified-closure-ancestor-coverage
```

**Not verified:** the revision's at-`HEAD` causation run was not re-executed;
the current three-failure state plus the independent `git log -S` trace were
used instead, which corroborate it. The proposed new expectations for the two
superseded tests were read as described, not applied. O1's hook-wiring
conclusion was not traced end to end and is offered as an observation.

## Recommended Commit Type

Recommended commit type: `fix`

Unchanged from `-001` — one function widened plus test corrections, repairing a
governed behavior that is specified but not firing.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
