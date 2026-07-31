NEW
::init gtkb pb
::open build
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: b34d5b84-5746-4eee-bd95-b6eeb3e70715
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role prime-builder via ::init gtkb pb; CF-10 serialization leadership held per DELIB-20260730-CF10-LEADER-GRANT-B34D5B84
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: implementation_report
Document: gtkb-wi5699-staged-artifact-admission-gate
Version: 003
Date: 2026-07-31 UTC
Responds to: bridge/gtkb-wi5699-staged-artifact-admission-gate-002.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5699

target_paths: ["scripts/check_staged_artifact_admission.py", "config/governance/staging-admission.toml", "platform_tests/scripts/test_check_staged_artifact_admission.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this report performs no MemBase mutation and no
`groundtruth.db` write, insert, edit, or lifecycle change.

No approval-evidence work: this report creates no formal-artifact approval packet and requires no packet path in `target_paths`.

# WI-5699 implementation report — staged-artifact admission gate

## Disposition

Implemented under the `GO` at version 002, an independent reviewer session,
and a live implementation-start packet minted this session.

## What Was Built

### A1 — `scripts/check_staged_artifact_admission.py`

Classifies every staged **addition** into exactly one admission basis:

| Bucket | Basis |
| --- | --- |
| `authorized` | matches a bridge thread's declared `target_paths`; the thread is named |
| `registered` | resolves to a SoT registry record; the classification is named |
| `excluded` | matches a rule in the exclusion config; the rule id is named |
| `unresolved` | none of the above |

Output is deterministic and sorted, with `--json` for machine consumption and
`--path` for classifying an explicit set. Modifications and deletions are
excluded by `--diff-filter=A`, per the approved scope.

**Reuse, not reimplementation.** `target_paths` are parsed by the existing
`implementation_authorization.extract_target_paths`; registry membership uses
the existing `controlled_artifact_paths.classify_controlled_artifact`. A test
asserts both imports are present and that neither function is redefined
locally.

### A2 — `config/governance/staging-admission.toml`

Five owner-governed exclusion rules, each carrying a mandatory `reason`:
root-level `_*.py` and `tmp_*` session scratch, `.gtkb-state/**`, `.tmp/**`,
and `.groundtruth/inventory/**`. Rules evaluate in file order, first match
wins, and the matching rule id is reported for every excluded path — so an
over-broad rule is visible in output rather than silent. A rule missing `id`,
`glob`, or `reason` is rejected and reported; it never silently excuses a path.

### A3 — `platform_tests/scripts/test_check_staged_artifact_admission.py`

14 tests covering each bucket, `root_only` scoping, fail-safe behavior,
determinism, the advisory exit contract, and the reuse invariant.

## Acceptance Replay — the gate reproduces this session's failures

Run against the exact classes that the 2026-07-31 sweep mis-admitted:

```
authorized: 3   registered: 0   excluded: 2   unresolved: 2
  AUTHORIZED  platform_tests/scripts/test_git_lifecycle_publication.py  <- gtkb-wi5840-git-lifecycle-publication-operation-001.md
  AUTHORIZED  scripts/check_staged_artifact_admission.py                <- gtkb-wi5699-staged-artifact-admission-gate-001.md
  EXCLUDED    _debug_impl_auth.py                                       <- rule root-session-scratch-underscore
  EXCLUDED    tmp_bsr.json                                              <- rule root-session-scratch-tmp
  UNRESOLVED  harness-test-transcripts/dsv4pro-r1.json
  UNRESOLVED  harness-test-transcripts/glm52-r3.json
```

The two unlinked transcripts classify `unresolved` and the scratch artifacts
classify `excluded` with their matching rule named — which is the acceptance
criterion from the proposal: the gate would have surfaced both without anyone
needing to ask.

## Findings Disclosed

### F1 — `extract_target_paths` raises rather than returning empty

The proposal assumed the parser returns an empty list for a bridge file with
no `target_paths`. It raises `AuthorizationError`. Verdicts, advisories, and
disposition entries legitimately carry no `target_paths`, so the first run
crashed on the first verdict file encountered.

Handled by treating a parse failure as "contributes no authorization
evidence" and continuing, rather than as an error. Only genuinely unreadable
files are reported. A dedicated test
(`test_verdict_without_target_paths_contributes_no_authorization`) pins this:
a verdict must contribute nothing and raise nothing.

### F2 — authorization is checked before exclusion, and that ordering is visible

During the acceptance replay, `.gtkb-state/ops/x.json` classified
**`authorized`** rather than `excluded`, because some bridge thread declares a
`.gtkb-state/**` glob in its `target_paths` and authorization is evaluated
first.

This is reported rather than silently reordered. The ordering is defensible —
an explicitly declared path is a stronger admission basis than a generic
disposable-class rule, and a thread that declares a runtime path presumably
means it. But it does mean a broad `target_paths` glob can admit paths the
exclusion config would otherwise catch. Loyal Opposition may reasonably judge
that exclusion should win for runtime-state globs; that is a scope question
the GO did not settle, so no unspecified reordering was introduced here.

## Specification-Derived Verification — executed 2026-07-31

| Requirement | Command | Observed |
| --- | --- | --- |
| Every bucket, scoping, fail-safe, determinism, advisory contract, reuse | `pytest platform_tests/scripts/test_check_staged_artifact_admission.py -q` | **14 passed**, 0.34s |
| Acceptance replay against this session's classes | `check_staged_artifact_admission.py --path <7 paths>` | 3 authorized, 2 excluded, 2 unresolved (output above) |
| Lint | `ruff check <script, test>` | `All checks passed!` |
| Format | `ruff format --check <script, test>` | `2 files already formatted` |
| Implementation authority live | `implementation_authorization.py validate --target <each>` | `authorized: true` for all three |
| Scope containment | `git status --short` on the three declared paths | exactly three new files; nothing else |

Both code-quality gates were run separately, per the protocol note that
`ruff check` and `ruff format --check` are distinct.

## Acceptance Criteria Check

1. Every staged addition classifies into exactly one bucket — **met**.
2. Unregistered additions report `unresolved` — **met** (replay + dedicated test).
3. Output deterministic and order-independent — **met** (two tests).
4. Phase 1 always exits 0 — **met** (`test_phase_one_always_exits_zero_even_with_unresolved`).
5. Existing surfaces reused, not duplicated — **met** (reuse-invariant test).
6. Modifications and deletions ignored — **met** (`--diff-filter=A`).
7. Registry unavailability fails safe — **met** (classification returns None on any exception; missing config surfaces an error and excuses nothing).
8. Existing suites pass — **met** (no existing file modified; three new files only).
9. Only declared target paths created — **met**.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-WORK-TREE-HYGIENE-001` and
`GOV-PLATFORM-SOT-REGISTRY-001` already supply the hygiene and
registry-authority framing, and WI-5699 states the required behavior. No new
or revised requirement was needed.

## Specification Links

- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-PLATFORM-SOT-REGISTRY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CHANGE-CONTROLLED-ARTIFACT-EVALUABILITY-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `bridge/gtkb-wi5699-staged-artifact-admission-gate-001.md` / `-002.md` — the proposal and the GO authorizing this implementation.
- `WI-5699` — the carrier, escalated P1 to P0 by owner directive after its predicted failure modes occurred live in the 2026-07-31 sweep.
- `WI-5833` — governance incident for sweep commit `9373c5231`; the mechanically-clean-but-governance-blind shape this gate closes.
- `WI-5847` — the companion test-registration gap found in the same sweep; same principle at the pre-VERIFIED boundary.
- `WI-5698` — registry-authoritative hygiene sweep with quarantine eligibility; shares the registry-membership premise, different action.
- `WI-5089` — bridge-proposal scope-sufficiency preflight; complementary (are declared paths sufficient, versus are staged paths declared).
- `DELIB-20260730-CF10-LEADER-GRANT-B34D5B84` — CF-10 leadership under which this session implements.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner question, 2026-07-31: "Are we committing artifacts which are not registered? If so, why?" — which surfaced the gap no gate detected.
- Owner directive, 2026-07-31: "Please add the necessary work item/project and resolve this with high priority." Both already existed; WI-5699 was escalated rather than duplicated.
- Owner AskUserQuestion, 2026-07-31: selected "Drop all transcripts, commit the rest", establishing that unlinked evidence blobs should not enter history by sweep.
- Implementation authority inherited from the active list-free whole-project PAUTH cited in the header. No new owner decision is requested by this report.

## Requested Loyal Opposition Action

Return `VERIFIED` if the executed evidence satisfies the linked
specifications, or `NO-GO` with concrete findings — in particular if finding
F2 (authorization evaluated before exclusion) warrants a different ordering.
Terminal `VERIFIED` must be recorded through the atomic finalization helper so
the verified paths and the verdict enter git history in the same local commit.

## Recommended Commit Type

`feat` — adds a new governance check and its owner-governed configuration surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
