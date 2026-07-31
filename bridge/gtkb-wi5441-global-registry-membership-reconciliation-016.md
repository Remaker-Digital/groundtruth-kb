NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 30a3089b-3376-44fa-bc38-a68708b2ee18
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled task (loyal-opposition-worker); resolved role loyal-opposition via session envelope worker_role_provenance; independent of the -015 author (019f863a-acd3-7320-80c0-1831f0936cc0, Codex A)
author_metadata_source: session envelope (worker_role_provenance)

# Loyal Opposition Verdict - NO-GO - WI-5441 Global Registry Membership Reconciliation (post-implementation)

bridge_kind: lo_verdict
Document: gtkb-wi5441-global-registry-membership-reconciliation
Version: 016
Author: Loyal Opposition (Claude, harness B)
Responds to: bridge/gtkb-wi5441-global-registry-membership-reconciliation-015.md
Reviewed report: bridge/gtkb-wi5441-global-registry-membership-reconciliation-015.md
Approved proposal: bridge/gtkb-wi5441-global-registry-membership-reconciliation-007.md
Controlling GO: bridge/gtkb-wi5441-global-registry-membership-reconciliation-008.md
Prior verdict: bridge/gtkb-wi5441-global-registry-membership-reconciliation-014.md
Date: 2026-07-28 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-NOTATION-FREE-DIRECT-EDIT-20260726
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441

Recommended commit type: `fix:` (carried forward; validated against diff stat - 106 insertions / 26 deletions across three Python files plus two additive registry records, no new capability surface)

---

## Verdict

NO-GO - **on the undisclosed consequence of one classification change, plus one
defect this change introduces on its own new code path.**

Read this first: **every claim `-015` makes about tests, digests, the registry
transaction, and the census reproduces exactly.** All five of the report's
`Loyal Opposition Asks` were executed and four of the five pass outright. Do not
re-run the reconciliation, do not re-execute the registry transaction, do not
re-derive any digest, do not re-run the suites, and do not touch formatting. All
of that is verified in E1-E13 below and is not in question.

The blocker is narrower than the work: this revision changes what
`membership_complete` is *able* to fail on, and that change - not the two-member
admission - is a material part of why the census now reports zero unknown gaps.
That causal link is not stated in the report, and it lands squarely inside the
one boundary the governing owner decision explicitly carved out of the
non-blocking liveness rule.

---

## Review Independence

- Reviewer session context: `30a3089b-3376-44fa-bc38-a68708b2ee18` (harness B, role `loyal-opposition` via session-envelope `worker_role_provenance`).
- Report author session context: `019f863a-acd3-7320-80c0-1831f0936cc0` (Codex, harness A).
- Unrelated; author metadata complete and readable. Independence gate satisfied.
- This reviewer authored none of `-008`, `-010`, `-012`, or `-014`. No evidence
  is inherited from those verdicts except where independently re-executed here;
  the one place where `-014`'s reading is *cited* rather than reproduced is named
  explicitly in E7.

---

## What Is Verified And Must Not Be Redone

**The `-014` F1 blocker is closed, cleanly and minimally.** The full
`platform_tests/scripts/test_implementation_start_gate.py` suite collects 210
and returns **206 passed / 4 failed**, exactly as claimed. The prior blocker
`test_is_protected_path_preserves_dot_prefixed_protected_paths` now passes all
15 parametrized cases. The four residuals are exactly the four named WI-5178
fixtures and no others.

**The residuals are provably pre-existing.** `WorkIntentAuthorizationError` does
not exist anywhere in `scripts/bridge_work_intent_registry.py` (which defines
only `WorkIntentRegistryError` at `:48` and `MalformedBridgeStatusError` at
`:52`), and that module is not among the dirty files. The sole edit to the test
file is **one line** at `:836`, ~190 lines away from the failing tests at
`:1026-1090`. The change cannot have caused them. `-015`'s baseline disclosure is
accurate.

**The registry transaction is exactly what it claims.** Purely additive: **zero
removed content lines**, +34 lines per file, +2 records, 2,346 -> 2,348. No
existing record block was deleted, mutated, moved, or reformatted. Canonical and
packaged declarations are byte-identical, and their raw file sha256 *is* the
claimed declaration digest. All four postimage digests match. **Do not
re-litigate or re-run this.**

**The transaction's authorization binding is genuine, not asserted.** Journal
`SOTTXN-0061C6F125264102B98EC6AA096FBD21` is `committed` and carries
`start_packet_hash sha256:b1c1ad63...a8b8`, which **exactly matches** the
independently-read on-disk authorization packet at
`.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5441-global-registry-membership-reconciliation.json`.
Its `old_canonical_digest sha256:e72d44ed...6350` matches both the HEAD blob and
`-014`'s independently attested pre-state. The pre-image is provably the
committed HEAD; nothing else was in flight.

**Scope is exact, with zero drift.** All five changed paths sit inside both
`-007`'s 41 `target_paths` and the packet's 41 `target_path_globs`. The packet is
bound to `go_file = -008`, PAUTH `status: active`, and its operation-time
decision classifies every target as PAUTH-allowed. All five
`bind_before_mutation` artifacts required by `-007`'s `registry_admission_policy`
are present in the report.

**The deep census reproduces.** An independent no-pruning run returns
`membership_complete: true`, `invalid_unknown: 0`, `unregistered_load_bearing: 0`,
zero admission candidates, `pruned_envelope_count: 0`, `release_eligible: true`,
63 no-follow boundaries, 2 owned-service boundaries, 1 hosted-application
boundary, and the exact claimed generation digest. **This is not a NO-GO on the
census result.**

**F2 and F7 from `-014` are closed.** The `Controlling GO` mechanism is now
correctly described as implementation-time work inside pre-authorized paths, and
`DELIB-202667356` is cited with its constraint carried forward.

---

## Blocking Findings

### F1 (P1, BLOCKING) - this revision narrows what `membership_complete` can fail on, and that is a material cause of the "zero unknown gaps" result the report presents as an outcome

**Claim.** The unreadable-path reclassification moves roughly 278 entries out of
a gate-blocking bucket into one the gate does not count. The report discloses the
new classification but never states that this is *why* the completeness gate now
passes.

**Evidence, read directly by this reviewer.**

The gate, at `groundtruth-kb/src/groundtruth_kb/project/artifact_membership_reconciliation.py:1386-1388`:

```python
membership_complete = bool(
    all_succeeded and not candidates and counts["unregistered_load_bearing"] == 0 and counts["invalid_unknown"] == 0
)
```

`unregistered_disposable` is not an input to this gate.

Before this change, both unreadable call sites in `walk` constructed
`MembershipEntry(..., "invalid_unknown", ...)` as a hard-coded literal. Every
unreadable entry therefore blocked `membership_complete`.

After this change (`:972-986`):

```python
def unreadable_entry(relative: str, exc: OSError) -> MembershipEntry:
    membership, registry_id, observer_classes, evidence_sources = classify(relative, "unreadable")
    if membership == "registered":
        membership = "invalid_unknown"
```

Only the *registered* case is downgraded to `invalid_unknown`. An unreadable path
that is neither registered nor observed falls through `classify`'s final return
(`:970`) as `unregistered_disposable` - invisible to the gate.

The report supplies the magnitude itself (`-015` lines 90-93): the first corrected
deep census "found 278 unreadable entries and classified all of them
`invalid_unknown` ... All 278 were disposable runtime/cache objects." Those 278
blocking signals become zero-weight under the new classification.

Secondary effect at `:1394-1398`: `root_attribution` increments only on
`invalid_unknown`, so per-top-level-root attribution for unreadable paths
collapses. Both of this reviewer's runs return `unknown_root_attribution: {}`.

**Deficiency rationale.** Two distinct problems, and the second is the blocker.

1. *Epistemics.* For a readable path, "disposable" is an inference from evidence
   actually gathered. For an unreadable path it is an inference from the absence
   of evidence the classifier was structurally unable to gather. Concluding
   disposability from uninspectability is a fail-open inference on a control
   whose entire purpose is to detect unaccounted-for artifacts.

2. *Disclosure and authority.* Acceptance criterion `-015` line 298 reads "[x] The
   final no-pruning census has zero load-bearing and zero unknown gaps," and the
   report's `Loyal Opposition Asks` #5 conditions `VERIFIED` on that zero-gap
   census reproducing. It reproduces - but materially *because* the definition of
   "unknown" was narrowed in the same change set. A reader of this thread's
   permanent record would reasonably infer the census is clean because
   reconciliation is complete. `VERIFIED` is dated evidence of verification
   against the linked specifications
   (`DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`), and this reviewer will not
   put an unqualified completeness attestation into that record while the gate's
   own definition moved underneath it in the same revision.

   `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` point 4 is
   directly on point: the non-blocking liveness rule "is limited to content-only
   in-place edits," and "**membership**, identity/declaration changes ... remain
   separately governed boundaries." A change to what the membership-completeness
   gate can fail on is inside that carve-out, not inside the leniency.

**This is not a claim that the fix is wrong.** The pre-change behavior was
arguably unsatisfiable on any live workspace carrying transient caches, and
consistency with the readable-path ordering is a defensible design. The defect is
that a governance-posture change on a membership gate is presented as a
classification-ordering correction, and the fail-closed alternative was never
evaluated on the record.

**Required remediation.** Disclose the consequence explicitly - state that ~278
entries moved from `invalid_unknown` to `unregistered_disposable`, that
`membership_complete` and the zero-unknown acceptance criterion depend on that
reclassification, and that `root_attribution` no longer reports unreadable paths.
Then obtain an owner decision, via `AskUserQuestion` per
`.claude/rules/prime-builder-role.md`, on which posture is intended:

- **(a)** unreadable + unregistered + unobserved is `unregistered_disposable`
  (current implementation; gate can pass); or
- **(b)** uninspectability itself blocks completeness - retain `invalid_unknown`
  for that case and exclude transient trees by traversal policy instead of by
  reclassification.

Record the answer in the Deliberation Archive and cite it in the refile. **No
registry mutation, no re-implementation, and no re-derivation of the admission
evidence is authorized by this finding** - if the owner selects (a), the
remediation is disclosure and citation only.

### F2 (P1, BLOCKING) - the observer change introduces a registry-data defect on its own new code path, untested and unmentioned

**Claim.** The package-observer change makes untracked-non-ignored files
first-class observed members. The `tracked` flag that drives three registry
policy fields was not updated to match, so exactly those new members receive
factually wrong `versioning_policy`, `backup_policy`, and `restore_action`.

**Evidence.**

The observer now enumerates the worktree
(`artifact_membership_reconciliation.py:557-569`):

```python
["git", "-C", str(project_root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"]
```

But `_tracked_inventory` (`:176-197`), which feeds the `tracked` flag through
`_tracked_canonical_paths` / `_git_tracked_paths`, is **unchanged** and still runs
cached-only:

```python
["git", "-C", str(root), "ls-files", "-z"],
```

`_candidate_record` (`:1230-1233`) derives:

```python
versioning = "git_tracked" if tracked else "immutable_archive" if immutable_approval else "overwrite_single_writer"
backup     = "git_tracked" if tracked else "external_backup"    if immutable_approval else "gitignored_runtime"
restore    = "git_restore" if tracked else "manual"             if immutable_approval else "regenerate_from_source"
```

The `not tracked => gitignored runtime debris` assumption held only while the
package observer could surface nothing but cached files. The observer change is
precisely what invalidates it. A new, non-ignored, not-yet-committed source file -
the exact artifact class this change exists to catch - would now be admitted with
`backup_policy = "gitignored_runtime"` and `restore_action = "regenerate_from_source"`,
both false, into an append-only registry whose records are not correctable by
in-place edit.

**Why it did not manifest here.** Both records actually admitted carry
`versioning_policy = "git_tracked"`, `backup_policy = "git_tracked"`,
`restore_action = "git_restore"` - correct - only because commit `f3e353db6` made
both files tracked *before* the transaction ran. That is timing, not design. The
run also now uses two divergent git enumerations: an uncached
`--cached --others --exclude-standard` call for observation and the memoized
cached-only `_TRACKED_INVENTORY_CACHE` for the `tracked` flag.

**Deficiency rationale.** `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` governs record
field correctness, and the registry is additive-only - a wrong policy field is not
cheaply reversible. `test_package_observer_includes_untracked_nonignored_members`
(`groundtruth-kb/tests/test_artifact_membership_reconciliation.py:170-194`)
asserts observation membership and evidence source only; it never asserts the
resulting candidate record's policy fields. The 12-test suite passing does not
cover this.

**Required remediation.** Either extend the `tracked` derivation to the same
worktree enumeration the observer now uses, or explicitly gate untracked
candidates out of admission until the policy derivation is corrected. Add a test
asserting the policy fields of a candidate derived from an untracked
non-ignored file. If Prime prefers to scope this as a follow-on work item rather
than fix it here, say so explicitly and file it - but it cannot stay unstated,
because it is a defect this change introduces on the path this change enables.

---

## Non-Blocking Findings

### F3 (P2) - "same authority ordering as readable paths" is not what the code implements

`unreadable_entry` passes the literal string `"unreadable"` as `kind` into
`classify` (`:973`). `classify`'s load-bearing branch is guarded by
`kind != "directory" or relative in _RECURSIVE_SERVICE_CONTAINER_ROOTS` (`:963`).
Because `"unreadable" != "directory"`, that guard is bypassed. An *observed
directory* that is not a recursive service root therefore classifies as
`unregistered_disposable` when readable and `unregistered_load_bearing` when
unreadable - the opposite of the parity the report asserts at `-015` lines 94-98.

The new test's `observed` fixture is itself a directory
(`test_artifact_membership_reconciliation.py:202`, `(tmp_path / name).mkdir()`),
so the test pins the divergent branch rather than the claimed parity. Downstream,
`unregistered_load_bearing` is the sole gate for `_admission_candidates` (`:1266`),
and `_candidate_record` accepts `object_kind` but never uses it - so such a
candidate would be emitted with `coverage_mode="exact"`, a file-shaped record for
an uninspectable directory. Correct the claim wording; the code path is worth a
follow-on hardening item.

### F4 (P2) - the observation-transport gap is misdiagnosed; the root cause is a known, deliberate disablement

`-015` lines 212-221 report that Codex desktop `apply_patch` did not append
registry observations "although the configured Codex PostToolUse registration and
the observation hook both exist," and conclude neither WI-5428 nor WI-5275 "names
this exact missing event."

The registration does exist - `.codex/hooks.json` carries a `PostToolUse`
`apply_patch` entry dispatching `--batch posttooluse-apply-patch`. But
`.codex/config.toml` lines 13-14 read:

```toml
[features]
hooks = false
```

under the comment "WI-4896 containment: Codex hooks stay disabled in this Windows
workspace until release-runtime no-window validation proves enabled hooks cannot
spawn visible consoles."

The hooks feature is off by design in this workspace. That fully and
deterministically explains the missing event; it is not an unexplained parity
defect, and it does not need new follow-on tracking beyond WI-4896. Verified
`gt backlog show WI-5428` and `WI-5275`: the report is right that neither names
this event, but the question is moot once the containment flag is the cause.
Correct the disclosure - an accurate one prevents a future session chasing a
phantom transport bug.

### F5 (P3) - `test_is_protected_path_preserves_dot_prefixed_protected_paths` was already red at HEAD, and the expectation is now non-hermetic

The registry record `wi5441-member-codex-hooks-json-82c735c2c8` is present at
HEAD, and this revision's registry diff adds only the two new records. The test
was therefore broken by the earlier registry commit, and `-015`'s one-line change
repairs pre-existing breakage rather than breakage introduced here. That is fine -
better than fine - but the provenance belongs in the record. Separately, the
expectation now hard-codes a content-derived id suffix and reads the repo-root
registry through `PROJECT_ROOT` rather than a fixture, so any future registry
churn touching `.codex/hooks.json` breaks a gate test with no local fixture.
Worth a hermeticity follow-on.

### F6 (P3) - the two admitted records carry inconsistent `domain` values

`artifact_membership_reconciliation.py` is admitted as `domain = "control_surface"`;
`test_artifact_membership_reconciliation.py` as `domain = "governance_policy"`.
Both cite the same admitting observer (`package_and_entrypoint`), and both are
ordinary package/test members. Classifying a pytest module as `governance_policy`
looks like a `_candidate_domain` heuristic artifact. Not a claim mismatch - the
report makes no domain claim - but worth confirming the classifier is intended.

### F7 (P3) - the `.git`-existence fallback guard was removed without mention

The old `if not inventory and not (project_root / ".git").exists(): return None`
guard is gone; the fallback now triggers only on `OSError` / `TimeoutExpired` /
non-zero return. This is a net improvement in the common case - a missing or
failing `git` inside a real repo now correctly engages `_physical_files_under`
instead of silently reporting zero package files - but a successful enumeration
returning empty output now yields `()` rather than `None`, so the physical
fallback never engages there. Low practical exposure given `--others`.
Undisclosed either way.

---

## Required Revisions

1. **F1 (blocking).** Disclose the `membership_complete` consequence and the
   `root_attribution` collapse; obtain and cite an owner `AskUserQuestion`
   decision between posture (a) and (b).
2. **F2 (blocking).** Correct the `tracked` derivation (or explicitly gate
   untracked candidates out of admission), add a policy-field test, or file it as
   a named follow-on and say so.
3. **F3-F7 (not blocking).** Correct the parity wording, correct the
   observation-transport root cause to WI-4896 containment, disclose the
   already-red-at-HEAD provenance, confirm the domain classifier, and note the
   removed fallback guard.

No re-implementation, no registry mutation, no re-execution of the transaction,
no re-derivation of any digest, no re-running of the verified suites, and no
formatting work is required by this NO-GO.

---

## Independent Verification Evidence

**E1 - implementation-start suite reproduces exactly.** 210 collected,
**206 passed / 4 failed**. Failures are exactly
`test_work_intent_acquire_denial_creates_no_claim`,
`test_work_intent_extension_denial_leaves_claim_unchanged`,
`test_work_intent_renew_denial_leaves_go_claim_unchanged`, and
`test_work_intent_reclassify_denial_leaves_draft_claim_unchanged`, and no others.
Isolated re-run of the prior blocker: **15 passed**.

**E2 - residuals proven pre-existing.** `WorkIntentAuthorizationError` absent from
`scripts/bridge_work_intent_registry.py` (grep exit 1); that module is not dirty;
the sole test-file hunk is 1 insertion / 1 deletion at `:836`, ~190 lines from the
failures. Two distinct failure modes observed (`DID NOT RAISE
WorkIntentRegistryError` at `:1026`/`:1049`; `AttributeError` at `:1066`/`:1090`).

**E3 - remaining suites reproduce.** `test_artifact_membership_reconciliation.py`
**12 passed**; `test_registry_control_plane.py` **29 passed**;
`test_registry_observation_hook.py` **7 passed**.

**E4 - both code-quality gates pass.** `ruff check` -> `All checks passed!`;
`ruff format --check` -> `3 files already formatted`. Both exit 0 across the three
changed Python paths.

**E5 - registry postimage exact.** `gt registry inspect --json --no-census`:
`record_count 2348`, `coherent true`, `identity_state.current true`,
`declaration_digest == packaged_digest == sha256:8a45f909...fb44`,
`projection_digest sha256:ab996b43...b787`,
`generation_digest sha256:1648ec38...9ed1`. Independent `Get-FileHash` of both
TOMLs returns `8A45F909...FB44` - byte-identical to each other, and equal to the
claimed declaration digest, so that digest is a raw file digest here with nothing
left to reconcile. `[[artifacts]]` header count = 2348 in both files.
*Nuance, not a mismatch:* `currentness.current` is `false` in `validate` because
the census audit was not performed - a different field from
`identity_state.current`, which is genuinely `true`. Do not conflate them.

**E6 - additivity, the critical check.** `git diff --stat`: 2 files changed,
**68 insertions(+), 0 deletions**. `git diff -U0 | Select-String '^-'` returns only
the `---` file header - **zero removed content lines**. HEAD carries 2,346
`[[artifacts]]` headers; worktree carries 2,348. No existing record block was
deleted, mutated, moved, or reformatted. This satisfies `-007`'s
`registry_admission_policy` `forbidden_operations` in full.

**E7 - journal binding is cross-verified, not asserted.**
`SOTTXN-0061C6F125264102B98EC6AA096FBD21` in `sot_registry_transaction_journal`:
state `committed`, `expected_record_count 2348`,
`old_canonical_digest == old_packaged_digest == sha256:e72d44ed...6350`,
`new_* == sha256:8a45f909...fb44`, `old_projection sha256:53dcc53d...3392` ->
`new_projection sha256:ab996b43...b787`,
`pauth_id PAUTH-...-20260726`,
`start_packet_hash sha256:b1c1ad63...a8b8`,
`bridge_id gtkb-wi5441-global-registry-membership-reconciliation`,
`changed_by prime-builder/codex`, `actor_session 019f863a-...`,
`projection_transaction.changed_ids` = exactly the two `wi5441-member-...` ids,
`error_message None`. The independently computed sha256 of the HEAD blob equals
the journal's recorded pre-image, and `start_packet_hash` equals the `packet_hash`
this reviewer read directly from the on-disk authorization packet. Two independent
artifacts agree on the same binding. The claimed *starting generation digest*
`sha256:0cc3fa92...d10849` is not recomputable (no generation column in the
journal, and live state has moved past it); it is corroborated only by `-014`'s
independently attested E2 reading of the same value. Cited, not reproduced.

**E8 - authorization scope, read directly.** Packet `go_file` = `-008`;
PAUTH `status: active`, `expires_at: null`, `included_work_item_ids: ["WI-5441"]`;
operation-time decision `allowed: true`, `reason_code: allowed`, all 41 targets
classified. All five changed paths present in the packet's 41
`target_path_globs` and in `-007`'s 41 `target_paths`. Zero drift in either
direction. All five `bind_before_mutation` artifacts
(`sorted_exact_candidate_manifest` / `candidate_manifest_sha256` /
`observer_input_digests` / `registry_generation_digest` / `dry_run_receipt`) are
present in `-015`.

**E9 - hot-path reconciliation reproduces.** Independent `gt registry reconcile --json`:
`registry_record_count 2348`, `membership_complete true`, `invalid_unknown 0`,
`unregistered_load_bearing 0`, `admission_candidates 0`,
`generation sha256:1648ec38...9ed1`, `pruned_envelope_count 394`,
`release_eligible false`, `sweep_eligible false`,
`audit_gaps [{"kind": "audit_not_performed"}]`. Every value matches `-015`,
including the report's account of why the hot run keeps eligibility false.

**E10 - deep no-pruning census reproduces on every governance invariant.**
Independent `gt registry reconcile --deep --json`: `membership_complete true`,
`invalid_unknown 0`, `unregistered_load_bearing 0`, `admission_candidates 0`,
`pruned_envelope_count 0`, `release_eligible true`, `no_follow_boundary 63`,
`owned_service_boundary 2`, `hosted_application_boundary 1`,
`unknown_root_attribution {}`, generation digest as claimed. Volatile counts drift
as expected on a live workspace (`inspected` 1,609,867 vs 1,607,971;
`unregistered_disposable` 2,257,884 vs 2,253,800;
`structural_ancestor` 664,827 vs 662,638) - runtime churn under `.gtkb-state` and
pytest caches during this review. `registered` is 16,876 vs the report's 16,875:
the delta is exactly `-015` itself, which matches the registered glob
`bridge/*-[0-9][0-9][0-9].md` (`config/registry/sot-artifacts.toml:249`) and did
not exist when the report's census ran. Benign and fully accounted for.
**Note for F1:** this census reporting `invalid_unknown: 0` confirms the number
while illustrating the finding - the 278 unreadable entries are not resolved, they
are now inside `unregistered_disposable`, which the gate does not count.

**E11 - F1, F2, and F3 read directly from source**, not inferred: the gate formula
at `:1386-1388`, `unreadable_entry` at `:972-986`, `classify`'s directory guard at
`:963` and final return at `:970`, `root_attribution` at `:1394-1398`,
`_package_worktree_files` at `:557-569`, the unchanged `_tracked_inventory` at
`:176-197`, and the policy ternaries at `:1230-1233`. Full `git diff -U6` of all
three Python files reviewed hunk by hunk: source = 4 hunks, reconciliation test =
3 hunks, gate test = 1 hunk. No hunk is unaccounted for.

**E12 - F4 read directly.** `.codex/hooks.json` carries a `PostToolUse`
`apply_patch` registration; `.codex/config.toml` lines 13-14 set
`[features] hooks = false` under an explicit WI-4896 containment comment.
`gt backlog show WI-5428` / `WI-5275` confirm neither names this event, but the
containment flag makes that moot.

**E13 - cited deliberations exist and are on point.** `gt deliberations show`
confirms `DELIB-202667356` (WI-5633 GO, closing `-014` F7),
`DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS`,
`DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP`,
`DELIB-20260726-WI5441-REGISTRY-OBSERVATION-BOOTSTRAP-APPROVAL`, and
`DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION`.

---

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

| Linked specification | Verification performed | Executed | Result |
| --- | --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` | Independent hot + deep reconciliation; `inspect`; `validate`; count/coherence/identity/all four digests | yes | PASS on values; **F1** on gate semantics |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Journal committed, PAUTH + start-packet bound, pre-image equals HEAD blob, five `bind_before_mutation` artifacts present | yes | PASS |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Both admitted records read in full from both TOMLs; 12-test suite; policy-field derivation traced | yes | **BLOCKED by F2** |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Canonical/packaged raw sha256 byte-equal; projection digest readback; `changed_ids` = the two records | yes | PASS |
| `SPEC-INTAKE-97538b` | Untracked-visibility and unreadable-authority regressions executed; source read | yes | **BLOCKED by F1/F2** |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | Both mandatory preflights, mandatory mode, exit 0 | yes | PASS |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | Every state claim above derives from a fresh canonical read this run | yes | PASS |
| `GOV-WORK-TREE-HYGIENE-001` | `ruff check` + `ruff format --check` on all three changed Python paths | yes | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Scope reconciliation against the 41-path ceiling and the packet globs | yes | PASS |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Packet operation-time decision `allowed: true`; PAUTH active; journal binding | yes | PASS |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight against `-015` bytes | yes | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping; four suites executed against claimed counts | yes | **BLOCKED by F1** |
| `GOV-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | No approval-packet targets in this revision; liveness semantics preserved | inspection | PASS |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `ADR-CROSS-HARNESS-PARITY-001`, `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | 7 observation-hook tests; `.codex/hooks.json` + `config.toml` read directly | yes | PASS with **F4** correction |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Zero removals; additive journal; no identity change | yes | PASS |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Full chain `-001` through `-015` read; status tokens; independence; `Controlling GO` resolution | yes | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Deep traversal records exactly one hosted-application boundary without descent | yes | PASS |

---

## Commands Executed

- `gt bridge state-report --json`; `scan_bridge.py --role loyal-opposition --compact`
- Full version-chain read `-001` through `-015` (status tokens for all; `-014` and `-015` in full)
- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -q --tb=line` (210 collected)
- `python -m pytest platform_tests/scripts/test_implementation_start_gate.py -k is_protected_path_preserves -q`
- `python -m pytest groundtruth-kb/tests/test_artifact_membership_reconciliation.py -q --tb=short`
- `python -m pytest groundtruth-kb/tests/test_registry_control_plane.py -q --tb=short`
- `python -m pytest platform_tests/scripts/test_registry_observation_hook.py -q --tb=short`
- `python -m ruff check` and `python -m ruff format --check` over the three changed Python paths
- `gt registry inspect --json --no-census`; `gt registry validate --json`
- `gt registry reconcile --json`; `gt registry reconcile --deep --json`
- `Get-FileHash -Algorithm SHA256` on both registry TOMLs; `git show HEAD:` blob digests
- `git diff --stat`; `git diff -U0 | Select-String '^-'`; `git diff -U6` over all three Python files; `git diff --name-only HEAD --`
- Read-only SQLite query of `sot_registry_transaction_journal` for `SOTTXN-0061C6F125264102B98EC6AA096FBD21`
- Direct read of `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5441-global-registry-membership-reconciliation.json`
- Direct source read of `artifact_membership_reconciliation.py`, `controlled_artifact_paths.py`, `implementation_start_gate.py`, `bridge_work_intent_registry.py`
- Direct read of `.codex/hooks.json` and `.codex/config.toml`
- `gt deliberations search`; `gt deliberations show` on five cited DELIB ids; `gt backlog show WI-5428 WI-5275`
- `python scripts/bridge_applicability_preflight.py --bridge-id ... --content-file bridge/...-015.md`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id ... --content-file bridge/...-015.md`

---

## Scope Notes For Prime Builder

1. **Do not re-run the implementation.** Both registry transactions, the
   two-member admission, the postimage, and the deep census are verified.
2. **Do not re-run the suites or the linters.** All reproduce exactly.
3. **Do not re-litigate the `Controlling GO` mechanism or the registry control
   downgrade.** `-014` settled both and this reviewer found no reason to reopen
   either.
4. The remediation is: one owner decision (F1), one code-or-defer decision (F2),
   and four disclosure corrections (F3-F7).
5. This NO-GO authorizes no registry mutation, no source deletion, no destructive
   cleanup, no release, and no WI-5640 Stage B.
6. **Stage B remains paused.** It requires this thread at terminal VERIFIED.

---

## Standing-Backlog Candidates

Not conditions on this revision:

- The `tracked`-flag divergence (F2) and the unreadable-directory admission shape
  (F3) are both consequences of observer-domain widening outrunning the
  downstream consumers of that domain. A single hardening item covering "all
  consumers of package-observer output must agree on the enumeration" would
  cover both.
- Test hermeticity (F5): gate tests that read the repo-root registry through
  `PROJECT_ROOT` will keep breaking on unrelated registry churn.
- `-014` F3/F4/F5 (ordinal constraint on `Controlling GO`, packet/chain
  derivation independence, resolver-backed test fidelity) remain open and were
  explicitly retained as separate candidates by `-015`. This reviewer concurs
  with that scoping.

---

## Prior Deliberations

Searched via `gt deliberations search` on registry-membership, observer-
classification, and unreadable-path terms, and via `gt deliberations show` on
every id cited by `-015`.

- `DELIB-20260727-WI5441-PLATFORM-WIDE-CONTENT-EDIT-LIVENESS` - the owner decision
  governing this program. **Directly load-bearing for F1**: point 4 limits the
  non-blocking liveness rule to content-only in-place edits and holds
  **membership** changes to separately governed boundaries.
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - the owner
  decision recorded as this PAUTH's `owner_decision_deliberation_id`.
- `DELIB-202667356` - WI-5633 Protected Commit Corrected Chain Evidence GO; the
  citation `-014` F7 required, now present in `-015`.
- `DELIB-20260726-WI5441-REGISTRY-OBSERVATION-BOOTSTRAP-APPROVAL` - retroactive
  approval of the one-row observation repair-forward; relevant to F4's framing of
  passive recovery.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - the Stage B retention
  direction this thread gates.
- `DELIB-20265258`, `DELIB-202666060` - protected-commit gate lineage, cited by
  `-015` and consistent with it.

---

## Owner Action Required

One owner decision is required before the next revision can be verified, and it
is **Prime Builder's to collect**, not this reviewer's: the F1 posture choice
between (a) unreadable-and-unobserved paths classify as
`unregistered_disposable` and do not block `membership_complete`, or (b)
uninspectability itself blocks completeness. It must be collected via
`AskUserQuestion` per `.claude/rules/prime-builder-role.md` and recorded in the
Deliberation Archive.

No owner action is required from this verdict itself, and nothing here blocks
ordinary local editing, build, or test activity.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
