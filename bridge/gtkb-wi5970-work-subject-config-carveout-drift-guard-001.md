NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 345fab55-33fc-40c1-933b-d2413de27158
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

bridge_kind: prime_proposal
Document: gtkb-wi5970-work-subject-config-carveout-drift-guard
Version: 001
Date: 2026-08-07 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5970
related_work_items: ["WI-5100", "WI-5617", "WI-5933"]

target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py"]
implementation_scope: work_subject_config_carveout_completion_and_drift_guard
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

**No KB mutation.** This proposal performs no MemBase write and does not modify
`groundtruth.db`. (WI-5970 itself was captured before filing, under the owner
directive cited below; that capture is complete and is not part of this scope.)
**No approval-evidence work.** This proposal creates no formal-artifact-approval
packet and writes no approval-packet path.
**No dispatcher or TAFE mutation.** No dispatcher configuration, substrate,
scheduled task, routing rule, or harness registry entry is changed.

# WI-5970 - Complete the work-subject `config/` carve-out and replace its enumeration-only test with a drift guard

## Summary

Two independent path classifiers disagree about GT-KB platform paths under
`config/`, and the disagreement silently makes GO-approved, PAUTH-authorized
work unimplementable:

```
config/dispatcher-next/requirements-spike.txt
  PAUTH classify_target           -> configuration        (ALLOWS; packet mints)
  workstream_focus.classify_root  -> application_product  (HARD-BLOCKS the Write)
```

WI-5100 fixed this class in 2026-07-09 for the six platform config subdirs that
existed then. It fixed them by **enumeration**, and its regression test asserts
a **hard-coded tuple** of those same six paths. A test that lists paths cannot
fail for a path it does not list, so every platform config subdir added since
has silently reproduced the original defect.

This proposal (C1) completes the enumeration and (C2) replaces the
enumeration-only assertion with a drift guard that walks the live `config/`
tree, so the next occurrence is a test failure at authorship time instead of a
hard block at implementation time.

## Live Anchor Evidence (every anchor verified 2026-08-07)

1. `scripts/workstream_focus.py:238-249` - `APPLICATION_PREFIXES` contains a
   blanket `"config/"` entry at line 241.
2. `scripts/workstream_focus.py:252-276` -
   `CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES` carries the WI-5100 carve-out at
   lines 266-271 (`config/agent-control/`, `config/dispatcher/`,
   `config/governance/`, `config/harness-parity/`, `config/project-templates/`,
   `config/registry/`). The comment at lines 260-265 states the fall-through
   explicitly: *"Any `config/<other>` path still falls through to
   application_product."*
3. `scripts/workstream_focus.py:2234-2240` - `classify_root` checks governance
   prefixes BEFORE `APPLICATION_PREFIXES`, which is why the carve-out wins for
   listed dirs and only for listed dirs.
4. Live `classify_root` over every `config/` subdir on disk (measured
   2026-08-07):

```
config/agent-control/            current_repo_bridge_or_governance   78 files
config/dispatcher/               current_repo_bridge_or_governance    3 files
config/file-reference-migration/ application_product                  1 file
config/governance/               current_repo_bridge_or_governance   25 files
config/harness-parity/           current_repo_bridge_or_governance    1 file
config/hooks/                    application_product                 38 files
config/project-templates/        current_repo_bridge_or_governance    1 file
config/registry/                 current_repo_bridge_or_governance    2 files
```

5. `config/hooks/` holds 38 GT-KB platform hook files - including
   `gtkb-credential-scan.py`, `gtkb-bridge-compliance-gate.py`,
   `gtkb-bridge-axis-2-surface.py`, `gtkb-assertion-check.py`. These are
   platform governance surfaces by any reading; classifying them as application
   product is plainly wrong.
6. `config/file-reference-migration/` holds `wi5640.toml`, the WI-5640
   skill-rename file-reference migration config. Platform.
7. `config/dispatcher-next/` does not exist yet; it is created by
   `bridge/gtkb-wi5617-dispatcher-next-spike-manifest-closure` (GO at `-002`).
   Note the near-miss: `config/dispatcher/` IS carved out,
   `config/dispatcher-next/` is not - one hyphen apart.
8. `platform_tests/hooks/test_workstream_focus.py:1043-1062` -
   `test_classify_root_config_platform_carveout` iterates a hard-coded
   seven-entry tuple (six dirs; `config/agent-control/` appears twice) and then
   asserts at line 1062 that `config/app-settings.toml` still classifies
   `application_product`. That last assertion is deliberate and is preserved by
   this proposal: the blanket fallback is correct for genuine application config.
9. Blocked live work, both reproduced this session:
   - `bridge/gtkb-wi5617-dispatcher-next-spike-manifest-closure` (GO at `-002`):
     PAUTH allowed both targets and an implementation-start packet minted
     successfully, then the Write of
     `config/dispatcher-next/requirements-spike.txt` was hard-blocked by the
     `GTKB-WORK-SUBJECT` PreToolUse hook.
   - `bridge/gtkb-wi5933-slice-b-resolver-fail-closed` (GO at `-008`): target
     `config/hooks/gtkb-bridge-axis-2-surface.py` classifies
     `application_product` and will hit the same block.

## Proposed Change

### C1 - Complete the carve-out

Add three entries to `CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES` alongside the
existing WI-5100 block:

- `config/hooks/`
- `config/file-reference-migration/`
- `config/dispatcher-next/`

`config/dispatcher-next/` is included ahead of the directory's creation
deliberately: it is the prefix that unblocks the already-GO-approved WI-5617
thread, and adding a prefix for a not-yet-existing directory is inert until that
directory exists.

The blanket `"config/"` entry in `APPLICATION_PREFIXES` is **left unchanged**.
Inverting the default (making `config/` governance and carving out application
config) is the alternative WI-5100's own acceptance summary named, and it is
deliberately NOT taken here - see Rejected Alternatives.

### C2 - Replace the enumeration-only test with a drift guard

Rewrite `test_classify_root_config_platform_carveout` so it walks the live
`config/` directory rather than a hard-coded tuple:

- Enumerate every immediate subdirectory of `config/` on disk.
- Assert each classifies `ROOT_CURRENT_REPO_BRIDGE_OR_GOVERNANCE`, UNLESS its
  name appears in a new explicit module-level constant
  `_EXPECTED_APPLICATION_CONFIG_SUBDIRS` in the test module (empty today - the
  GT-KB repo currently has no genuine application config subdir).
- On failure, emit a message naming the offending directory and the exact
  remedy (add it to the carve-out, or declare it application config in the
  allowlist).
- Retain the existing line-1062 assertion that a `config/` path outside any
  platform subdir still classifies `application_product`, so C1 cannot be
  misread as removing the blanket fallback.

The guard converts "a new platform config dir silently blocks authorized work"
into "the test suite fails the moment the directory is added."

## Rejected Alternatives

1. **Invert the `config/` default** (governance by default, carve out
   application config). Named by WI-5100's acceptance summary as an option.
   Rejected for this thread: `classify_root` is shared with the adopter
   scaffolding contract, where `config/` legitimately IS application config.
   Inverting changes adopter-visible behavior and warrants its own owner
   decision. C2's drift guard captures most of the safety benefit without the
   adopter-facing risk. Recorded as Follow-On 1.
2. **Relocate the WI-5617 manifest again** to an already-carved-out directory.
   Rejected: that stacks a second workaround on the first (WI-5617 had already
   relocated once to satisfy the PAUTH classifier) and leaves `config/hooks/`
   and every future platform config dir still broken.
3. **Add `config/hooks/` only** (the minimum to unblock WI-5933). Rejected: it
   repeats WI-5100's enumeration mistake and would leave WI-5617 blocked.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority for this thread.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project-scoped implementation
  authorization; discharged by the PAUTH binding in the metadata block.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - discharged by this
  section.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan maps
  each acceptance criterion to a test.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project/work-item
  linkage in the metadata block (WI-5970 created under
  PROJECT-GTKB-HOUSEKEEPING-HARDENING; whole-project PAUTH cited).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - platform surfaces only; no
  `applications/` path is touched, and the change explicitly preserves the
  platform/application classification boundary rather than blurring it.
- `GOV-RELIABILITY-FAST-LANE-001` - small bounded defect fix.
- `.claude/rules/project-root-boundary.md` - in-root containment.
- `.claude/rules/codex-review-gate.md` - the implementation-start authorization
  gate this defect interacts with.

## Prior Deliberations

Deliberation search executed 2026-08-07:
`gt deliberations search "work subject classifier config application_product carve-out" --limit 6`.

- `DELIB-202666054` (top hit, semantic score 1.001) - **Verification Verdict,
  WI-5100 work-subject `config/` platform-classification carve-out (NO-GO).**
  Directly on point and load-bearing for this proposal in two ways. First, it
  settles the design question: *"This is a finalizability / scoped-commit NO-GO,
  not a defect in WI-5100's logic. The carve-out itself is correct and its
  regression test passes."* The carve-out approach is therefore
  precedent-accepted in substance. Second, it names the exact hazard this thread
  must avoid: WI-5100 failed verification because
  `scripts/workstream_focus.py` was a commingled working tree carrying a second
  thread's (WI-5083) separately-GO-approved but unreported change, so a
  whole-file stage would have corrupted that thread's audit trail. Preimage
  cleanliness is therefore an explicit precondition below, re-verified at
  implementation start.
- `DELIB-1035` - GTKB Work Subject And Root Enforcement (the subsystem being
  corrected).
- `DELIB-20264063` - First-Class Project Artifacts And Subject Workflow Model
  (the work-subject taxonomy).
- WI-5100's own acceptance summary named both remedies (extend the carve-out, or
  replace the blanket entry) and required *"a platform_tests assertion covering
  classify_root over these platform config paths."* That assertion was written
  as a fixed tuple, which is the precise mechanism by which the defect recurred.
  C2 addresses that gap directly.
- No prior deliberation proposes a live-tree drift guard for this classifier;
  C2 is novel and is flagged as such for review.

## Owner Decisions / Input

- **Owner directive, 2026-08-07 (this session, verbatim): "File the carve-out
  fix."** This proposal is the direct discharge of that instruction. The
  directive followed a session report that presented the classifier
  disagreement, its confirmed blast radius (two GO-approved threads), and the
  recommendation that the fix required its own thread because
  `scripts/workstream_focus.py` appears in no current `target_paths`.
- **`DELIB-202666054`** - the WI-5100 verification NO-GO whose findings shape
  the preimage-cleanliness precondition and confirm the carve-out design.
- No new owner decision is requested by this proposal. The scope question the
  owner may wish to weigh - whether to invert the `config/` default - is
  deliberately deferred to Follow-On 1 rather than bundled here.

## Requirement Sufficiency

**Existing requirements sufficient.** The work-subject boundary is already
specified, and WI-5100 established that GT-KB platform config must classify as
governance. This thread completes that established requirement's coverage and
hardens its test; it introduces no new requirement and revises none.

## Specification-Derived Verification Plan

| Requirement | Test / command | Required observed behavior |
|---|---|---|
| C1 - platform config classifies governance | `test_classify_root_config_platform_carveout` (rewritten) | Every live `config/` subdir classifies `current_repo_bridge_or_governance`; `config/hooks/`, `config/file-reference-migration/` flip from `application_product`. |
| C1 - pending dir covered | new case in same test | `config/dispatcher-next/requirements-spike.txt` classifies `current_repo_bridge_or_governance` even though the directory does not exist yet. |
| C2 - drift guard actually fails | new negative case | A synthetic unknown `config/<name>/` subdir that is neither carved out nor allowlisted causes the guard to fail with the remedy message. |
| Blanket fallback preserved | retained line-1062 assertion | `config/app-settings.toml` still classifies `application_product`. |
| No collateral classification change | `test_classify_root_4_categories` | Unchanged: `src/`, `.claude/rules/`, `bridge/`, `AGENTS.md`, `README.md` classify as before. |
| Live unblock proof | `classify_root` probe on the two blocked targets | `config/dispatcher-next/requirements-spike.txt` and `config/hooks/gtkb-bridge-axis-2-surface.py` both classify `current_repo_bridge_or_governance`. |
| Full module regression | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_workstream_focus.py -q` | All pass. |
| Code quality (both gates) | `ruff check` and `ruff format --check` on both changed files | Both pass; separate gates per the bridge protocol. |

## Acceptance Criteria

1. Only the two declared `target_paths` change.
2. Every live `config/` subdir classifies `current_repo_bridge_or_governance`.
3. `config/dispatcher-next/` classifies governance despite not existing yet,
   unblocking the GO-approved WI-5617 thread.
4. The blanket `"config/"` `APPLICATION_PREFIXES` entry is unchanged, and a
   `config/` path outside every platform subdir still classifies
   `application_product`.
5. The rewritten test fails when a synthetic uncarved `config/` subdir is
   introduced, and its failure message names the directory and the remedy.
6. `platform_tests/hooks/test_workstream_focus.py` passes in full; no other
   test module regresses.
7. Both ruff gates pass on both changed files.
8. **Preimage cleanliness (per `DELIB-202666054`):** implementation begins only
   after re-verifying that `scripts/workstream_focus.py` and
   `platform_tests/hooks/test_workstream_focus.py` are clean in `git status`.
   Both were verified clean at 2026-08-07T00:4xZ when this proposal was filed.
   If either carries another thread's bytes at implementation start,
   implementation pauses and reports rather than committing mixed work.
9. No KB row, TAFE/dispatcher state, formal artifact, credential, deployment, or
   external system is mutated; no commit is created by Prime Builder -
   finalization remains the Loyal Opposition atomic step.

## Risk and Rollback

- **Risk: over-broad carve-out.** Adding a prefix moves files from
  application-product to governance classification, which *widens* what a
  GT-KB-subject session may write. Bounded: all three directories are
  demonstrably GT-KB platform surfaces (evidence items 5-7), the blanket
  fallback is retained, and acceptance criterion 4 tests it.
- **Risk: the drift guard becomes noisy for adopters.** Bounded:
  `platform_tests/` is GT-KB's own suite and is not scaffolded into adopter
  projects, so the live-tree walk only ever sees the GT-KB repo's `config/`.
- **Risk: commingled tree at implementation start.** This is the failure that
  NO-GO'd WI-5100. Bounded by acceptance criterion 8's pause-and-report rule.
- **Rollback:** revert both files. The change is additive to a prefix tuple plus
  a test rewrite; no data migration, no schema change, no behavior depends on
  the new prefixes existing.

## Follow-On (not in this scope)

1. **Invert the `config/` classification default.** WI-5100's acceptance summary
   named replacing the blanket `config/` application prefix with specific
   application-config subpaths. That is the structurally stronger fix and would
   retire the enumeration entirely, but it changes adopter-visible scaffolding
   behavior and needs an owner decision. Recommended as its own tracked item.
2. **Classifier reconciliation.** `PAUTH classify_target` and
   `workstream_focus.classify_root` answer overlapping questions with
   independent, divergent taxonomies, and nothing checks them against each
   other. A conformance test asserting the two agree on platform-vs-application
   placement would catch this whole disagreement class, not just its `config/`
   instance. Recommended as its own tracked item.
3. **Author-time visibility.** Neither proposal authors nor LO reviewers
   currently check `classify_root` when declaring `target_paths`; both WI-5617
   and WI-5933 passed authorship and review while carrying a target that could
   not be written. Surfacing work-subject classification in the applicability
   preflight output would close that gap.

## Bridge Chain Discipline

This artifact is filed as
`bridge/gtkb-wi5970-work-subject-config-carveout-drift-guard-001.md`, the first
numbered file of a new thread. The numbered bridge files under `bridge/` are
canonical and append-only: this proposal deletes no bridge file and rewrites no
prior version of any thread. The two blocked threads it cites are referenced by
their versioned paths -
`bridge/gtkb-wi5617-dispatcher-next-spike-manifest-closure-002.md` and
`bridge/gtkb-wi5933-slice-b-resolver-fail-closed-008.md` - as read-only evidence;
neither is modified, and each remains owned by its own thread. The WI-5100
predecessor chain is likewise cited, not amended.

## Root Boundary Compliance

All artifacts are in-root under `E:/GT-KB`. Both declared targets are in-root
platform paths and this bridge file resides under `E:/GT-KB/bridge/`. No
generated artifact is written outside the project root. No `applications/` path
is touched.

## Recommended Commit Type

`fix:` - repairs a defect in which authorized work is silently unwritable. No
new capability surface is added; the test rewrite hardens an existing assertion
rather than introducing new behavior.

## DISARM - Implementation

This file requests review only. It grants no protected-edit, claim, start,
finalization, or cleanup authority. Implementation requires the Loyal Opposition
GO on this thread, a fresh work-intent claim, an implementation-start
authorization packet created from that GO, and clean preimages on both target
files.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
