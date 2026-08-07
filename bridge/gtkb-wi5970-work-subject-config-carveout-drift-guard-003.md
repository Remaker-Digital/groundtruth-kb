REVISED
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
Version: 003
Date: 2026-08-07 UTC
Responds to: bridge/gtkb-wi5970-work-subject-config-carveout-drift-guard-002.md
Prior GO: bridge/gtkb-wi5970-work-subject-config-carveout-drift-guard-002.md

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5970
related_work_items: ["WI-5100", "WI-5957", "WI-5617", "WI-5933"]

target_paths: ["scripts/workstream_focus.py", "platform_tests/hooks/test_workstream_focus.py"]
implementation_scope: work_subject_config_carveout_residual_and_drift_guard
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

**No KB mutation.** No MemBase write; `groundtruth.db` is not modified.
**No approval-evidence work.** No formal-artifact-approval packet is created.
**No dispatcher or TAFE mutation.**

# WI-5970 REVISED (003) - residual scope after owner-directed de-confliction with WI-5957

## Why This Revision Exists

This revision narrows scope under an explicit owner decision. It is not a
response to a defect finding: `-002` is a clean `GO` and its design is accepted
unchanged in substance. The change is de-confliction.

After `-002` was issued, a **duplicate-overlapping GO'd thread** was discovered:
`bridge/gtkb-wi5957-config-hooks-platform-classification-002.md` declares
**byte-identical `target_paths`** to this thread and fixes the same classifier
defect for `config/hooks/`.

Filing timeline (file mtimes, verified 2026-08-07):

| Time (UTC) | Event |
|---|---|
| 00:16:47 | `gtkb-wi5957-config-hooks-platform-classification-001.md` filed `NEW` |
| 00:31:12 | `gtkb-wi5957-config-hooks-platform-classification-002.md` `GO` |
| 00:51:38 | `gtkb-wi5970-...-001.md` filed `NEW` (this thread) |
| 01:13:12 | `gtkb-wi5970-...-002.md` `GO` |

WI-5957 has precedence on both filing and approval. This thread is the later
duplicate on the overlapping portion.

**Authoring-miss disclosure (this thread's fault, recorded for process
learning).** WI-5957 was live and already `GO`-approved when `-001` was filed and
was not detected. Three checks were run and none could surface it: the
Deliberation Archive search could not (the DA harvests at session wrap, and
WI-5957 was 35 minutes old); the backlog `--match` queries used
`title:classify_root` and `title:work-subject`, neither of which matches
WI-5957's title ("Classify `config/hooks/**` as a platform governance surface");
and the GO-queue triage ran before 00:31, when WI-5957 was still `NEW`. The
missing check was a scan of the **Loyal Opposition / `NEW` queue for in-flight
threads declaring overlapping `target_paths`**. That gap is generalized as
Follow-On 4.

## Scope Change (owner-directed)

`config/hooks/` is **removed** from this thread's C1. WI-5957 owns it.

Residual C1 (unchanged in mechanism, reduced in set) - add to
`CURRENT_REPO_BRIDGE_OR_GOVERNANCE_PREFIXES`:

- `config/file-reference-migration/`
- `config/dispatcher-next/`

C2 (the drift guard) is **retained in full**. It is this thread's unique
contribution: WI-5957's own disposition describes its change as *"one added
tuple entry plus additive test cases"*, so it extends the hard-coded tuple and
does not close the recurrence class. Without C2 the enumeration-only test that
allowed this defect to recur after WI-5100 remains in place.

Everything else from `-001` - the evidence base, the rejected alternatives, the
specification links, the risk analysis - stands unchanged.

## Sequencing Precondition (new; load-bearing)

WI-5957 **must land before** this thread implements. The order is not
cosmetic:

- C2's drift guard walks the live `config/` tree and fails on any subdir
  classifying `application_product` that is not on the expected-application
  allowlist. If this thread implements first, `config/hooks/` is still uncarved
  and the guard fails on it - correctly, but for a directory this thread no
  longer owns.
- Implementing in the declared order means that when C2 runs, `config/hooks/` is
  already carved out by WI-5957 and the guard passes cleanly across the whole
  live tree.

If WI-5957 is withdrawn or its scope changes before this thread implements, this
thread must re-file a REVISED restoring `config/hooks/` to C1 rather than
silently leaving it uncarved.

## Working-Tree Contamination Disclosure (new; blocks both threads)

Both declared targets were verified clean when `-001` was filed
(2026-08-07T00:51Z). They are **dirty now**, and the bytes belong to
**neither** this thread nor WI-5957:

```
 M scripts/workstream_focus.py                    92 +/-
 M platform_tests/hooks/test_workstream_focus.py 123 +/-
```

All three hunks in `scripts/workstream_focus.py` sit in the startup-relay region
(`@@ -1767,0 +1768,39`, `@@ -1805,17 +1844,4`, `@@ -1952,6 +1978,26`) and
introduce `_dispatch_detached_startup_relay_refresh`, a detached background
refresh of the startup relay cache. That is unrelated to `config/`
classification. Verified live: none of `config/hooks/`,
`config/file-reference-migration/`, or `config/dispatcher-next/` is present in
the working tree, so **neither carve-out thread has begun implementing**.

A scan of every live non-terminal bridge thread declaring either target path
returns exactly two threads - WI-5957 and WI-5970 - so the startup-relay work is
**undeclared by any live thread with these targets**.

This is the precise condition that produced `DELIB-202666054`, the WI-5100
verification `NO-GO`: a whole-file stage during finalization would sweep the
third party's bytes into this thread's commit and corrupt that work's audit
trail. Acceptance criterion 8 below therefore remains a hard pause-and-report
gate, and it is currently **unsatisfied**.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge audit-trail authority; the numbered
  chain discipline this REVISED follows.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - project-scoped implementation
  authorization; discharged by the PAUTH binding above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - discharged here.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification plan below
  maps each acceptance criterion to a test.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project/work-item
  linkage in the metadata block.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - platform surfaces only; no
  `applications/` path touched; the change preserves rather than blurs the
  platform/application classification boundary.
- `GOV-RELIABILITY-FAST-LANE-001` - small bounded defect fix.
- `GOV-WORK-TREE-HYGIENE-001` - the contamination disclosure and the
  pause-and-report gate above.
- `.claude/rules/project-root-boundary.md` - in-root containment.
- `.claude/rules/codex-review-gate.md` - the implementation-start gate this
  defect interacts with.

## Prior Deliberations

- `DELIB-202666054` - WI-5100 carve-out verification `NO-GO`. Load-bearing
  twice: it settles that the carve-out design is correct (*"not a defect in
  WI-5100's logic... The carve-out itself is correct"*), and it names the
  commingled-tree finalizability hazard that is **live right now** on both target
  files (see Working-Tree Contamination Disclosure).
- `DELIB-1035` - GTKB Work Subject And Root Enforcement (subsystem under repair).
- `DELIB-20264063` - First-Class Project Artifacts And Subject Workflow Model.
- `bridge/gtkb-wi5957-config-hooks-platform-classification-002.md` - the
  precedence-holding sibling `GO` this revision de-conflicts against; cited as
  live authority for the `config/hooks/` portion now removed from this thread.
- `bridge/gtkb-wi5970-work-subject-config-carveout-drift-guard-002.md` - this
  thread's own prior `GO`, whose design is carried forward unchanged.
- WI-5100's acceptance summary required a `classify_root` assertion over
  platform config paths; it was written as a fixed tuple, which is the mechanism
  by which the defect recurred. C2 addresses that directly.

## Owner Decisions / Input

- **Owner AUQ, 2026-08-07 - "wi5957 lands, then REVISE wi5970 to residual".**
  Presented with four de-confliction options (this option; withdraw WI-5970
  entirely; WI-5970 supersedes WI-5957; pause both pending tree cleanup), the
  owner selected letting WI-5957 keep precedence and narrowing this thread to
  the residual scope. This revision is the direct discharge of that decision.
- **Owner directive, 2026-08-07 - "File the carve-out fix."** The directive that
  authorized `-001`.
- **`DELIB-202666054`** - the WI-5100 verification `NO-GO` shaping acceptance
  criterion 8.
- No new owner decision is requested. The `config/` default-inversion question
  remains deferred to Follow-On 1.

## Requirement Sufficiency

**Existing requirements sufficient.** WI-5100 established that GT-KB platform
config must classify as governance. This thread completes that requirement's
coverage for the residual directories and hardens its test. No new requirement is
introduced and none is revised. The scope reduction is an owner-directed
de-confliction, not a requirement change.

## Specification-Derived Verification Plan

| Requirement | Test / command | Required observed behavior |
|---|---|---|
| Residual C1 | `test_classify_root_config_platform_carveout` (rewritten) | `config/file-reference-migration/wi5640.toml` classifies `current_repo_bridge_or_governance`. |
| Pending dir covered | new case, same test | `config/dispatcher-next/requirements-spike.txt` classifies governance though the directory does not exist yet - unblocking the GO-approved WI-5617 thread. |
| WI-5957 boundary respected | live probe | `config/hooks/gtkb-bridge-axis-2-surface.py` classifies governance **via WI-5957's entry**; this thread's diff contains no `config/hooks/` string. |
| C2 drift guard fails correctly | new negative case | A synthetic uncarved, unallowlisted `config/<name>/` subdir causes the guard to fail with a message naming the directory and the remedy. |
| C2 passes on the live tree | rewritten test | With WI-5957 landed, every live `config/` subdir classifies governance. |
| Blanket fallback preserved | retained line-1062 assertion | `config/app-settings.toml` still classifies `application_product`. |
| No collateral change | `test_classify_root_4_categories` | Unchanged. |
| Full module regression | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_workstream_focus.py -q` | All pass. |
| Code quality (both gates) | `ruff check` and `ruff format --check` on both changed files | Both pass; separate gates. |

## Acceptance Criteria

1. Only the two declared `target_paths` change.
2. `config/file-reference-migration/` and `config/dispatcher-next/` classify
   `current_repo_bridge_or_governance`.
3. This thread's diff contains **no** `config/hooks/` entry; that carve-out
   arrives from WI-5957 and is verified present, not re-added here.
4. The blanket `"config/"` `APPLICATION_PREFIXES` entry is unchanged, and a
   `config/` path outside every platform subdir still classifies
   `application_product`.
5. The rewritten test fails when a synthetic uncarved `config/` subdir is
   introduced, with a remedy-naming failure message.
6. `platform_tests/hooks/test_workstream_focus.py` passes in full; no other test
   module regresses.
7. Both ruff gates pass on both changed files.
8. **Preimage cleanliness (per `DELIB-202666054`) - currently UNSATISFIED.**
   Implementation begins only after both target files are clean in `git status`.
   They carry undeclared third-party startup-relay work today. If that work is
   still present at implementation start, implementation **pauses and reports**
   rather than committing mixed work.
9. **Sequencing.** WI-5957 is landed before this thread implements; if it is
   withdrawn or rescoped first, this thread re-files a REVISED restoring
   `config/hooks/` rather than leaving it uncarved.
10. No KB row, TAFE/dispatcher state, formal artifact, credential, deployment, or
    external system is mutated; no commit is created by Prime Builder -
    finalization remains the Loyal Opposition atomic step.

## Risk and Rollback

- **Risk: sequencing violated.** If this thread implements before WI-5957, C2
  fails on the uncarved `config/hooks/`. Bounded by acceptance criteria 3 and 9,
  and the failure is loud rather than silent.
- **Risk: commingled tree at finalization.** The WI-5100 failure mode, live
  today. Bounded by acceptance criterion 8's pause-and-report gate.
- **Risk: over-broad carve-out.** Bounded - both remaining directories are
  demonstrably GT-KB platform surfaces, the blanket fallback is retained, and
  acceptance criterion 4 tests it.
- **Rollback:** revert both files. Additive prefix entries plus a test rewrite;
  no data migration, no schema change.

## Follow-On (not in this scope)

1. **Invert the `config/` classification default** - the structurally stronger
   fix WI-5100's acceptance summary named; changes adopter-visible scaffolding
   behavior, so it needs an owner decision.
2. **Classifier reconciliation** - `PAUTH classify_target` and
   `workstream_focus.classify_root` answer overlapping questions with divergent
   taxonomies and nothing checks them against each other.
3. **Author-time visibility** - surfacing `classify_root` in the applicability
   preflight would have caught WI-5617's and WI-5933's unwritable targets at
   authorship.
4. **Overlapping-`target_paths` detection (new).** Nothing warned that two GO'd
   threads declared byte-identical `target_paths`. Work-intent claims are
   **slug-scoped, not path-scoped**, so both threads legitimately held valid
   claims simultaneously; the collision was invisible to the claim system and to
   both reviewers. A preflight check that scans live non-terminal threads for
   overlapping `target_paths` and warns at filing time would have prevented this
   duplication - and would also have caught the WI-5100 commingling that
   produced `DELIB-202666054`. Recommended as its own tracked item.

## Bridge Chain Discipline

This artifact is filed as
`bridge/gtkb-wi5970-work-subject-config-carveout-drift-guard-003.md`, the next
numbered file in this thread. The numbered bridge files under `bridge/` are
canonical and append-only: no prior version is deleted or rewritten, and the
`-002` `GO` it responds to is preserved intact. The sibling thread
`bridge/gtkb-wi5957-config-hooks-platform-classification-002.md` is cited as
read-only evidence and is not modified - its disposition belongs to its own
session. `GO -> REVISED` is a lawful transition per the Post-Verdict Transition
Table.

## Root Boundary Compliance

All artifacts are in-root under `E:/GT-KB`. Both declared targets are in-root
platform paths and this bridge file resides under `E:/GT-KB/bridge/`. No
`applications/` path is touched.

## Recommended Commit Type

`fix:` - repairs a defect in which authorized work is silently unwritable. No new
capability surface; the test rewrite hardens an existing assertion.

## DISARM - Implementation

This file requests review only. It grants no protected-edit, claim, start,
finalization, or cleanup authority. Implementation requires a Loyal Opposition
`GO` on this revision, a fresh work-intent claim, an implementation-start
authorization packet created from that `GO`, WI-5957 landed, and clean preimages
on both target files.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
