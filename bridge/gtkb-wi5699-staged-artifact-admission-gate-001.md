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

bridge_kind: prime_proposal
Document: gtkb-wi5699-staged-artifact-admission-gate
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5699

target_paths: ["scripts/check_staged_artifact_admission.py", "config/governance/staging-admission.toml", "platform_tests/scripts/test_check_staged_artifact_admission.py"]
implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this proposal performs no MemBase mutation and no
`groundtruth.db` write, insert, edit, or lifecycle change.

No approval-evidence work: this proposal creates no formal-artifact approval packet, writes no narrative-artifact approval evidence, and requires no approval-packet path in `target_paths`.

# Staged-artifact admission gate — every added path must be authorized, registered, or explicitly excluded

## Problem — predicted by WI-5699, reproduced live on 2026-07-31

WI-5699 states the requirement directly: *"Integrate pre-sweep
admission/currentness checks so new load-bearing files are surfaced before
staging. Unregistered disposable files and runtime scratch must not be swept
into commits."* No such check exists. The owner-authorized whole-worktree
sweep this session reproduced every failure mode the work item predicts:

1. **Runtime scratch was staged.** 28 debug artifacts — `_debug_impl_auth*.py`,
   `_scan2.py`, `_find_free_go.py`, `tmp_classify.py`, `tmp_bsr.json` (643 KB),
   `tmp_go_list.txt` (760 KB), ~2 MB total. Three were being actively written
   by a concurrent session at the moment of staging.
2. **Unregistered artifacts were staged.** 10 of 11 harness-test transcripts
   (~30 MB) had no `target_paths` coverage in any bridge thread. They would
   have entered permanent history as evidence blobs with zero governance
   linkage.
3. **Nothing surfaced either condition.** Both were caught by a human asking
   *"Are we committing artifacts which are not registered?"* — not by any gate.

**The structural finding.** Seven verification gates ran and all passed green:
secrets scan, `py_compile`, `ruff check`, `ruff format --check`, pytest,
dev-environment inventory drift, and narrative-artifact evidence. Every one of
them validates a **property of** a file — is it formatted, does it compile,
is it free of secrets, does a protected path carry its required evidence.
**None validates a file's right to be present at all.** A pipeline composed entirely
of property checks cannot detect an unregistered artifact.

That is the same shape as governance incident `WI-5833` (sweep commit
`9373c5231`, 1235 files / 210K insertions): mechanically clean, governance-blind.
The admission question is orthogonal to every existing gate, so it needs its
own gate rather than an extension of one.

## Proposed Change

### A1 — `scripts/check_staged_artifact_admission.py`

A deterministic, read-only check that classifies every **staged addition**
(`git diff --cached --name-only --diff-filter=A`) into exactly one bucket:

| Bucket | Admission basis |
| --- | --- |
| `authorized` | the path matches a `target_paths` entry of some bridge thread |
| `registered` | `classify_controlled_artifact()` resolves it to a registry record |
| `excluded` | the path matches a rule in the exclusion config (A2) |
| **`unresolved`** | none of the above — the finding this gate exists to produce |

Output is deterministic and sorted, with `--json` for machine consumption,
listing all four buckets and, for each `authorized` path, the thread that
authorizes it. This satisfies WI-5699's *"show included, excluded, and
unresolved paths deterministically."*

**Reuse, not reimplementation.** Bridge `target_paths` are parsed with the
existing `implementation_authorization.extract_target_paths()`; registry
membership uses the existing
`controlled_artifact_paths.classify_controlled_artifact()`. This proposal adds
no second parser and no second registry reader.

**Modifications and deletions are out of scope.** The admission question is
"may this file exist," which applies to additions. An edit to an existing file
is already governed by the protected-path and narrative-evidence gates.

### A2 — `config/governance/staging-admission.toml`

Owner-governed exclusion rules, so "this is disposable" is a recorded
decision rather than a per-sweep judgement call. Seeded from the classes
actually observed this session:

- session scratch: `_*.py`, `tmp_*` at repository root
- runtime state: `.gtkb-state/**`, `.tmp/**`
- generated inventory: `.groundtruth/inventory/**`

Each rule carries a `reason` field. Rules are exact-prefix or glob, evaluated
deterministically in file order, first match wins. Adding a rule is a
configuration change reviewable on its own merits — which is the point: the
disposable set becomes an artifact instead of a habit.

### A3 — Two-phase enforcement

**Phase 1 (this proposal): advisory.** The check always exits 0 and prints its
classification. This mirrors the established GT-KB pattern used by the ADR/DCL
clause preflight (Slice 1 advisory → Slice 2 blocking) and lets the exclusion
config be tuned against real sweeps before anything can block a commit.

**Phase 2 (separate proposal, not requested here): blocking.** Promote
`unresolved` to a non-zero exit and register the check in the sweep path.
Deliberately deferred: a blocking gate seeded from an untuned exclusion config
would block legitimate work on day one.

### Explicitly out of scope

- **Wiring into `.claude/skills/gtkb-sweep-commit/SKILL.md`.** That file is a
  narrative artifact, and `narrative_artifact` is not an allowed mutation class
  under the cited PAUTH, so this slice does not touch it and creates no approval packet for it.
  Phase 1 is invoked explicitly; skill wiring accompanies the Phase 2
  promotion, which is where that separate evidence obligation is discharged.
- **Replacing `git add -A` with a registry-derived include set.** That is
  WI-5699's other half. This slice makes the *problem visible* first; deriving
  the include set is the natural follow-on once the classifier is proven.
- **Modifying any existing gate.** Nothing about the seven current checks
  changes.
- **Test-artifact registration** — that boundary is `WI-5847`.

## Requirement Sufficiency

Existing requirements sufficient. WI-5699 already states the required
behavior; `GOV-WORK-TREE-HYGIENE-001` and `GOV-PLATFORM-SOT-REGISTRY-001`
supply the hygiene and registry-authority framing. No new or revised
requirement is needed.

## Specification-Derived Verification

| Requirement | Verification | Expected result |
| --- | --- | --- |
| Bridge-authorized additions classify `authorized` | Fixture: added path listed in a thread's `target_paths` | bucket `authorized`, authorizing thread named |
| Registry-registered additions classify `registered` | Fixture: path resolving to a registry record | bucket `registered` |
| Config-excluded additions classify `excluded` | Fixtures for each seeded rule class | bucket `excluded`, matching rule reported |
| **Unregistered additions classify `unresolved`** | Fixture reproducing this session: a transcript-like added file with no coverage | bucket `unresolved` |
| Scratch reproduction | Fixtures named `_debug_x.py`, `tmp_y.json` at root | bucket `excluded` via scratch rules |
| Modifications and deletions ignored | Staged `M` and `D` entries present | absent from all buckets |
| Phase-1 advisory never blocks | Run with unresolved paths present | exit code 0 |
| Deterministic output | Same input twice, and shuffled input order | byte-identical output both times |
| No second parser introduced | Grep for `extract_target_paths` / `classify_controlled_artifact` imports | both reused, no local reimplementation |
| Registry unavailable fails safe | Registry read raises | unresolved reported, exit 0, error surfaced not swallowed |
| No regression | Existing controlled-artifact and authorization suites | all pass |

Commands to be executed and reported in the implementation report:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_staged_artifact_admission.py -q --tb=short
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_check_protected_commit_authorization.py platform_tests/scripts/test_implementation_authorization_terminal_evidence.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check scripts/check_staged_artifact_admission.py platform_tests/scripts/test_check_staged_artifact_admission.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check scripts/check_staged_artifact_admission.py platform_tests/scripts/test_check_staged_artifact_admission.py
```

**Acceptance replay.** The implementation report will run the check against the
exact staged set from this session's sweep and demonstrate that the 10 unlinked
transcripts classify `unresolved` and the 28 scratch artifacts classify
`excluded` — proving the gate would have surfaced both without anyone needing
to ask.

## Acceptance Criteria

1. Every staged addition classifies into exactly one of the four buckets.
2. Unregistered additions with no bridge or registry coverage report `unresolved`.
3. Output is deterministic and order-independent.
4. Phase 1 always exits 0.
5. Existing `target_paths` and registry surfaces are reused, not duplicated.
6. Modifications and deletions are ignored.
7. Registry unavailability fails safe and surfaces the error.
8. Existing suites pass.
9. Only the three declared target paths are created or modified.

## Bridge Chain Discipline

Filed as `bridge/gtkb-wi5699-staged-artifact-admission-gate-001.md`, the first
numbered file of a fresh append-only chain. No prior versioned bridge file is
deleted, rewritten, or renumbered.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5699 (escalated P1->P0 2026-07-31 by owner directive); owner question 'Are we committing artifacts which are not registered? If so, why?'; owner directive 'add the necessary work item/project and resolve this with high priority'; live sweep evidence this session",
  "canonical_authority": "GOV-WORK-TREE-HYGIENE-001; GOV-PLATFORM-SOT-REGISTRY-001; GOV-FILE-BRIDGE-AUTHORITY-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "primary_route": "python scripts/check_staged_artifact_admission.py [--json]",
  "before_behavior": "No admission check exists at the staging boundary. Every verification gate validates a property of a file; none validates its right to be present. Unregistered artifacts and runtime scratch stage silently and pass all gates green.",
  "after_behavior": "Every staged addition is deterministically classified as authorized, registered, excluded, or unresolved, with the authorizing thread or matching rule named. Phase 1 reports without blocking.",
  "self_descriptive_naming": "The script name states the boundary and the question; the four bucket names state the admission basis; each exclusion rule carries a reason field.",
  "obsolete_guidance_disposition": "No guidance is retired. All seven existing gates, the protected-path checker, the narrative-evidence gate, and the sweep skill remain exactly as they are; this adds an orthogonal check beside them.",
  "history_preservation": "No history is rewritten. The check is read-only: it inspects the git index and reports. It stages nothing, unstages nothing, and mutates no file.",
  "worker_loading_paths": [],
  "superseded_guidance": [],
  "baseline": {
    "admission_check_exists": false,
    "unregistered_additions_detected": false,
    "exclusion_rules_are_governed_config": false,
    "existing_gates_count": 7
  },
  "expected_result": {
    "admission_check_exists": true,
    "unregistered_additions_detected": true,
    "exclusion_rules_are_governed_config": true,
    "existing_gates_count": 7,
    "phase1_can_block_commit": false
  },
  "rollback": {
    "instructions": "Delete the three added files; no existing file is modified.",
    "verification": "Confirm the sweep path, all seven gates, and the protected-commit checker behave exactly as before."
  },
  "hard_invariants": [
    "the check is read-only and never stages, unstages, or modifies any file",
    "no existing gate is modified",
    "Phase 1 always exits 0",
    "bridge target_paths parsing reuses extract_target_paths",
    "registry membership reuses classify_controlled_artifact",
    "every staged addition lands in exactly one bucket"
  ],
  "fail_closed_conditions": [
    "registry read fails: report unresolved and surface the error rather than assuming admission",
    "a bridge file cannot be parsed: exclude it from authorization evidence and report it",
    "a path matches no rule and no coverage: report unresolved"
  ],
  "essential_context_preservation": "Preserve all seven existing verification gates, the protected-commit authorization checker, the narrative-artifact evidence gate, and the sweep skill's operating rules unchanged."
}
```

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

- `WI-5699` — the carrier; its description already specifies this behavior, escalated to P0 by owner directive after the predicted failure occurred live.
- `WI-5833` — governance incident for sweep commit `9373c5231`; the same mechanically-clean-but-governance-blind shape this gate closes.
- `WI-5847` — the companion test-registration gap found in the same sweep; same principle at the pre-VERIFIED boundary.
- `WI-5698` — registry-authoritative hygiene sweep with quarantine eligibility; adjacent, shares the registry-membership-as-authority premise, different action (quarantine vs admission).
- `WI-5089` — bridge-proposal scope-sufficiency preflight (GO-lane `target_paths` understatement); complementary — that checks whether declared paths are sufficient, this checks whether staged paths are declared.
- `WI-5836` — cross-thread target-path collisions found this session; same `target_paths` surface consumed for a different invariant.
- `DELIB-20260730-CF10-LEADER-GRANT-B34D5B84` — CF-10 leadership under which this session files.


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Owner Decisions / Input

- Owner question, 2026-07-31: *"Are we committing artifacts which are not registered? If so, why?"* — which surfaced the gap that no gate detected.
- Owner directive, 2026-07-31: *"Please add the necessary work item/project and resolve this with high priority."* Both already existed; WI-5699 was escalated P1→P0 rather than duplicated, and this proposal is the resolution step.
- Owner AskUserQuestion, 2026-07-31: selected **"Drop all transcripts, commit the rest"**, establishing that unlinked evidence blobs should not enter history by sweep.
- Implementation authority is inherited from the active list-free whole-project PAUTH cited in the header. No new owner decision is requested by this proposal.

## Risk And Rollback

Principal risk is false `unresolved` classification creating noise — a
legitimately-authorized file reported because its `target_paths` entry uses a
glob form the matcher does not handle. This is precisely why Phase 1 is
advisory: the classifier is tuned against real sweeps before it can block
anything, and a false positive in Phase 1 costs a line of output, not a
blocked commit.

Secondary risk is the exclusion config becoming a dumping ground that quietly
re-admits everything. Mitigated by requiring a `reason` per rule and by
reporting the matching rule for every excluded path, so over-broad rules are
visible in the output rather than silent.

Rollback is deletion of the three added files; no existing file is modified,
so nothing needs restoring.

## Recommended Commit Type

`feat` — adds a new governance check and its configuration surface.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
