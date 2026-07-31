REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# GT-KB Bridge Implementation Report - gtkb-wi5441-global-registry-membership-reconciliation - 017

bridge_kind: implementation_report
Document: gtkb-wi5441-global-registry-membership-reconciliation
Version: 017
Responds to: bridge/gtkb-wi5441-global-registry-membership-reconciliation-016.md
Controlling GO: bridge/gtkb-wi5441-global-registry-membership-reconciliation-008.md
Prior implementation report: bridge/gtkb-wi5441-global-registry-membership-reconciliation-015.md
Approved proposal: bridge/gtkb-wi5441-global-registry-membership-reconciliation-007.md
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
Recommended commit type: fix:

## Draft Publication Guard

The owner posture required by v016 F1 is durably captured and cited below.
This revision contains no draft sentinel and is ready for governed publication.

## Revision Claim

This revision addresses the two v016 blockers without re-running or changing the
verified two-record registry transaction. It discloses the exact effect of the
unreadable-path classification on `membership_complete` and
`unknown_root_attribution`, carries the owner's selected posture through a
Deliberation Archive citation, and makes candidate policy derivation consume the
same tracked-plus-untracked-nonignored Git enumeration as the widened package
observer.

No artifact was deleted, moved, renamed, retired, narrowed, or replaced. No
registry identity or declaration was changed. No WI-5640 Stage B apply,
obsolete-source cleanup, dispatcher activation, commit, push, release,
deployment, credential action, or history rewrite occurred.

## Response To v016 NO-GO

### F1 (P1, blocking) - disclosure and owner posture

The causal consequence is now explicit. In the first corrected deep run,
approximately 278 unreadable entries that had previously been hard-coded as
`invalid_unknown` became `unregistered_disposable` because they were neither
registered nor selected by a load-bearing observer. `membership_complete`
ignores `unregistered_disposable`, so the zero-unknown acceptance result depends
materially on that reclassification. `unknown_root_attribution` counts only
`invalid_unknown`, so those unreadable disposable paths also disappear from that
map; the final deep result is `{}`.

The owner selected posture A in
`DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE`: an unreadable path that
is both unregistered and unobserved is `unregistered_disposable` and does not
block `membership_complete`. Registered unreadable paths remain
`invalid_unknown` and block completeness. Observer-selected unreadable paths
remain `unregistered_load_bearing` and block completeness. The owner choice
governs only unreadable paths that are both unregistered and unobserved.

No registry transaction, census rerun, or admission-evidence re-derivation was
performed for F1.

### F2 (P1, blocking) - one Git-managed enumeration and policy regression

The defect is corrected in the existing authorized reconciliation source and
test. A shared `_git_managed_inventory()` now executes exactly:

```text
git -C <root> ls-files -z --cached --others --exclude-standard
```

Both `_package_worktree_files()` and candidate policy derivation consume that
same cached inventory. Existing tracked-only helpers remain unchanged for
consumers whose semantics are genuinely Git-index-only. Candidate admission now
uses `_git_managed_paths()`: tracked paths and untracked nonignored paths receive
the intended registry policy `versioning_policy = "git_tracked"`,
`backup_policy = "git_tracked"`, and `restore_action = "git_restore"`.
Ignored runtime paths are absent from this inventory and do not acquire those
policies.

If Git enumeration fails, times out, or cannot execute, the required package
observer now returns `succeeded = false` with no observations. Reconciliation
therefore emits no admission candidates and keeps `membership_complete = false`.
The prior physical fallback was removed because it could neither apply Git ignore
rules nor support truthful policy derivation. The existing tracked-only fallback
inside candidate construction remains solely for callers that inject their own
typed observer results in non-Git test roots; default production reconciliation
cannot reach admission after the required package observer fails.

The new
`test_untracked_nonignored_candidate_uses_git_managed_policy_fields` fixture
initializes a real temporary Git repository, leaves `tests/new.py` untracked and
nonignored, runs reconciliation, and asserts all three policy fields. Together
with the existing package-observer fixture, it also proves an ignored sibling is
not observed.

### F3 (P2, nonblocking) - unreadable directory wording corrected

v015's phrase "same authority ordering as readable paths" was too broad. An
unreadable object is passed as kind `unreadable`; therefore an observer-selected
unreadable directory is load-bearing, while a readable observer-selected
non-service directory can remain a structural/disposable directory. This
revision makes no claim of directory-kind parity. It also prevents
`_admission_candidates()` from emitting any exact record while
`object_kind == "unreadable"`; the load-bearing count remains nonzero and keeps
completeness false, but no file-shaped record can be proposed without inspectable
kind evidence. The unreadable-authority fixture now asserts the empty candidate
set directly.

### F4 (P2, nonblocking) - observation transport cause corrected

The missing Codex desktop observation event is explained by the deliberate
WI-4896 containment: `.codex/config.toml` sets `[features] hooks = false` even
though `.codex/hooks.json` contains the PostToolUse registration. It is not an
unexplained apply-patch transport failure and needs no duplicate item beyond
WI-4896. Passive observation remains a nonblocking repair-forward path while
that containment is active.

### F5 (P3, nonblocking) - provenance and hermeticity disclosed

The `.codex/hooks.json` expectation repaired in v015 was already red at HEAD;
the v015 registry diff did not create that break. The replacement expectation
reads the repo-root registry and hard-codes the current content-derived record
ID, so it is not hermetic against future registry churn. No additional test
change is made here; the risk remains captured in v016 for separate cleanup.

### F6 (P3, nonblocking) - domain classifier confirmed

The two admitted records intentionally receive different domains from their
paths, not from their common observer. `_candidate_domain()` maps ordinary test
surfaces containing `/test` to `governance_policy`; the implementation module
falls through to `control_surface`. The classifier is behaving as implemented.
No registry record or domain value is changed in this revision.

### F7 (P3, nonblocking) - fallback behavior corrected and disclosed

The prior `.git`-existence guard and physical fallback are now removed. A Git
invocation that fails, times out, or cannot execute makes the package observer
fail non-admitting; a regression pins `membership_complete = false`, one
`invalid_unknown` root entry, and an empty candidate list. A successful Git
invocation returning an empty inventory returns an empty package selection.
With `--others` active, any present nonignored package member makes that inventory
nonempty.

## Verified Evidence Carried Forward Without Re-Execution

Per v016, the following are independently verified and were not re-run:

- the two-record additive transaction and journal binding;
- canonical/package declaration equality and all four postimage digests;
- the 2,348-record registry identity and projection;
- the deep census and hot-path census values;
- the 206 passed / four named WI-5178 implementation-start baseline;
- the 12-test pre-F2 reconciliation suite, 29 registry-control tests, and seven
  observation-hook tests;
- the v015 source-retention, no-destruction, and database-waiver claims.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `SPEC-INTAKE-97538b`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Owner Decisions / Input

The v016 F1 posture decision is persisted as
`DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE` and carried above.
Existing owner decisions remain in force: registry membership is
the ultimate load-bearing authority; unregistered artifacts are disposable;
ordinary owner edits require no notation; an audit gap is preferable to
platform failure; identity changes remain separately governed; and obsolete
WI-5640 sources remain in place.

No new owner authorization is inferred beyond the exact unreadable-path choice.

## Prior Deliberations

- `DELIB-20260728-WI5441-UNREADABLE-UNREGISTERED-POSTURE`
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`
- `DELIB-20260724-WI5668-DUAL-AUTHORITY-COMPLETION-SCOPE`
- `DELIB-20260726-WI5441-REGISTRY-OBSERVATION-BOOTSTRAP-APPROVAL`
- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS`
- `DELIB-202667356`
- `DELIB-20265258`
- `DELIB-202666060`
- `bridge/gtkb-wi5441-global-registry-membership-reconciliation-016.md`

## Specification-Derived Verification

| Spec / governing surface | New or carried evidence | Result |
| --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Explicit F1 consequence plus owner posture; v016 independently reproduced both censuses | PASS |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Real-Git untracked/nonignored candidate asserts all three policy fields | PASS |
| `SPEC-INTAKE-97538b` | Shared Git-managed enumeration plus no candidate emission for unreadable object kind | PASS |
| `GOV-WORK-TREE-HYGIENE-001` | 14 reconciliation tests plus Ruff check and format check on the two newly changed Python files | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | WI-4896 containment is named as the actual missing-event cause | PASS with contained hooks disabled |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | New F2 regression executed; v016 independently verified the carried evidence | PASS |
| Remaining linked specifications | v016 E1-E13 independently verified the unchanged implementation and transaction evidence | PASS carried by reference |

## Focused Commands Run After v016

- Fresh work-intent claim and implementation-start packet for the v016 resumable
  report NO-GO; packet hash
  `sha256:780609d1384a205abbc3d68b55b4f47b38617fb5b9d91f2ff74279a841338a44`.
- `python -m pytest groundtruth-kb/tests/test_artifact_membership_reconciliation.py -q --tb=short`: 14 passed in 6.71s.
- `ruff check` on the reconciliation source and test: PASS.
- `ruff format --check` on the same two files: 2 files already formatted.
- Reconciliation source digest: `sha256:367d3c5afa1401f815f0ba4b2f6efde4b9badaaad06b83ca8615813c8a728560`.
- Reconciliation test digest: `sha256:839f371de9be39897178d3185176c821aaa21792b57611f2da077b04e447f6ea`.
- Final-byte passive-observation revisions:
  `SOTREV-FAB4A049232548BAAA836136DA31A67B` and
  `SOTREV-1F7180E747D945D78606A47FE4E5004B`.
- Applicability and mandatory clause preflights: PASS on final content; zero
  missing required/advisory specifications and zero blocking clause gaps.

## Files Changed

- `config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml`
- `groundtruth-kb/src/groundtruth_kb/project/artifact_membership_reconciliation.py`
- `groundtruth-kb/tests/test_artifact_membership_reconciliation.py`
- `platform_tests/scripts/test_implementation_start_gate.py`

## By-Reference Finalization Waiver

target_paths: ["groundtruth.db"]

The service-owned database carries the already-verified additive registry
transaction plus passive observation revisions. It MUST NOT be force-added,
staged, placed in `## Files Changed`, or included in the finalizer commit. This
is a finalization-mechanics waiver, not an evidence waiver.

## Acceptance Criteria Status

- [x] The F1 completeness and root-attribution consequences are explicit.
- [x] The F1 owner posture is selected, archived, and cited.
- [x] Observer and candidate policy use one Git-managed enumeration.
- [x] An untracked nonignored candidate receives correct Git policy fields.
- [x] Git-unavailable package observation fails non-admitting with no candidate.
- [x] Unreadable load-bearing objects block without emitting a kind-invalid candidate.
- [x] F3-F7 wording and provenance are corrected without unrelated code changes.
- [x] The verified registry transaction, declarations, and census are not re-run or changed.
- [x] No registered artifact is deleted, moved, renamed, retired, narrowed, or replaced.
- [x] No WI-5640 Stage B mutation occurs.

## Pre-Filing Preflight

Applicability preflight passes against this final content with no missing
required or advisory specifications and no blocking errors. Mandatory clause
preflight evaluates all applicable clauses with zero blocking gaps.

## Risk And Rollback

The new shared inventory changes no tracked-only reference-resolution semantics;
it is consumed only by package observation and admission-policy derivation. If
Git is unavailable or returns nonzero, the required observer fails and disables
admission. The fixtures cover tracked, untracked nonignored, ignored, unreadable,
and Git-unavailable members.

The F2 source/test patch is ordinarily Git-restorable. The registry transaction
is not touched and remains additive. Any request to reverse a registry identity
or policy record still requires separate oversight. WI-5640 Stage B remains
paused until this thread is terminal VERIFIED.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
