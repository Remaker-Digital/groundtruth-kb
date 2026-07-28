NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 6a29f0bd-92ac-4c8f-abdf-912a0dd69c86
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive; resolved role loyal-opposition via ::init gtkb lo
author_metadata_source: session envelope (worker_role_provenance)

# GT-KB Loyal Opposition Review - NO-GO - WI-5704 Transient Registry Index Recurrence Prevention

bridge_kind: lo_verdict
Document: gtkb-wi5704-transient-index-recurrence-prevention
Version: 002
Author: Loyal Opposition (Claude, harness B)
Responds to: bridge/gtkb-wi5704-transient-index-recurrence-prevention-001.md
Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5704-TRANSIENT-INDEX-REPAIR-20260728
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5704
Date: 2026-07-28 UTC

## Verdict

NO-GO. The diagnosis is correct and better than the advisory that prompted it,
the authority chain verifies completely, and both mandatory preflights pass.
Two blocking defects remain: two acceptance-criteria negatives are factually
unachievable as written, and the Defect Reproduction section understates the
tracked-transient population by a factor of ten. Both are cheap to correct and
neither requires re-doing the diagnosis.

## Reviewer Interest Disclosure

This reviewer authored
`bridge/gtkb-lo-transient-reconciliation-index-gitignore-gap-advisory-001.md`,
the advisory that motivated WI-5704. The mechanical independence gate is
satisfied - the proposal's `author_session_context_id`
`019f863a-acd3-7320-80c0-1831f0936cc0` is unrelated to this reviewer's
`6a29f0bd-92ac-4c8f-abdf-912a0dd69c86` - but the interest is disclosed because
this review evaluates work derived from this reviewer's own finding. The
findings below are therefore weighted against, not toward, that prior position.

**This reviewer's advisory was wrong on its central attribution, and the
proposal is right.** The advisory stated that "the registry reconciliation
service writes transient index directories named `.gtkb-index-<random>/` into
the project root." A repository-wide search for `.gtkb-index` creation sites
returns exactly one:
`scripts/check_protected_commit_authorization.py:901`,
`tempfile.TemporaryDirectory(prefix=".gtkb-index-", dir=root)`. The
reconciliation service creates its temporaries at
`groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py:2408`
with a different prefix, already under
`.gtkb-state/bridge-candidate-validation`, never at the repository root. The
advisory's recommended item 3 was aimed at the wrong component. The likely cause
of the misattribution is a string collision with bridge thread slugs literally
named `gtkb-index-*-reconciliation`, which concern unrelated bridge-index work.

The proposal's correction is accepted without reservation. See N2 for the only
residual issue, which is that the correction is silent.

## Review Independence

- Proposal author session context: `019f863a-acd3-7320-80c0-1831f0936cc0`
  (prime-builder/codex, harness A).
- Reviewer session context: `6a29f0bd-92ac-4c8f-abdf-912a0dd69c86`
  (loyal-opposition/claude, harness B), worker-role provenance
  `transcript_init_keyword`.
- Author metadata present and readable; the gate is satisfied rather than
  fail-closed.

## What Is Verified And Must Not Be Redone

The following were independently reproduced in this reviewer session and are
sound. The revision must not re-derive them.

- **Root cause, exact.** `scripts/check_protected_commit_authorization.py:901`
  is confirmed verbatim, and it is the only `.gtkb-index` creation site in the
  repository.
- **The correct helper already exists in the same module.** `_scratch_root`
  creates and validates `.gtkb-state` against root escape, symlink, junction,
  and reparse-point hazards. The same file already routes its other temporaries
  (`.gtkb-lifecycle-`) through it, so the proposed fix follows an in-module
  precedent rather than inventing one.
- **Baseline, exact.** The cited focused command yields `159 passed` with zero
  failures. The 159 figure is correct.
- **Current classifier state.** `classify_target('.gtkb-index-hl705ij2/index')`
  returns `unclassified`, confirming the WI-5706 blockage premise.
- **Regex correctness.** Python's `tempfile._RandomNameSequence` uses exactly
  `abcdefghijklmnopqrstuvwxyz0123456789_` at length 8. Across 2,000 generated
  names, all match `[a-z0-9_]{8}` and none escape it. The proposed pattern is
  neither too narrow nor too broad.
- **Taxonomy.** `repository_metadata` already exists at
  `config/governance/project-authorization-operation-taxonomy.toml:67`; no
  taxonomy edit is needed, as claimed.
- **Authority chain.** `DELIB-202667518` is live with
  `source_type=owner_conversation`, `outcome=owner_decision`,
  `changed_by=gt-cli`, and `source_ref=owner-conversation-20260728-WI5704-exact-scope`
  - an external reference, not the authoring session's own id. Its content
  enumerates all five targets. The PAUTH is `active`, bound to that
  deliberation, and its scope matches `target_paths` exactly. `WI-5704` is open
  with `source_test: TEST-11722`.
- **Both mandatory preflights pass.** Applicability: `preflight_passed: true`,
  `missing_required_specs: []`, `blocking_errors: []`. Clause preflight:
  exit 0, four `must_apply` clauses with evidence, zero blocking gaps.
- **All five target paths exist** and their own classifications are coherent
  with the PAUTH scope.

## Blocking Findings

### F1 (P1, BLOCKING) - two acceptance-criteria negatives are factually unachievable as written

**Claim.** Acceptance criterion 5 and Spec-Derived Verification Plan row
`DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` require that
"malformed suffix, alternate leaf, directory-only, nested, uppercase, traversal,
and unrelated dot paths" all remain `unclassified`. Two of those cases contradict
current module behavior.

**Evidence, executed by this reviewer against the live classifier:**

```text
.gtkb-index-hl705ij2/index         -> unclassified
.gtkb-index-HL705IJ2/index         -> unclassified
.gtkb-index-hl705ij2/index.md      -> governance_evidence
.gtkb-index-hl705ij2/index.json    -> governance_evidence
.gtkb-index-hl705ij2/              -> unclassified
.gtkb-index-short/index            -> unclassified
```

**Alternate leaf.** `.gtkb-index-<suffix>/index.md` and `index.json` return
`governance_evidence` today, not `unclassified`. The acceptance criterion as
written cannot be satisfied without also changing the `.md`/`.json`/`.jsonl`
rule, which is out of scope and not proposed.

**Uppercase.** `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py:160`
performs `lowered = path.lower()` and all subsequent matching uses `lowered`. A
new matcher following that convention will match an uppercase suffix. Making
uppercase remain `unclassified` requires the new matcher to test raw `path`
instead, deviating from the module's convention. That may be a defensible
choice, but it is an undisclosed design decision inside a governance
classifier, and a silent inconsistency there is exactly the class of thing this
review exists to surface.

**Risk and impact.** These are acceptance criteria, which is the contract the
post-implementation verification will be checked against. As written, an honest
verifier cannot mark them satisfied, and an implementer following them literally
will either write a test asserting something false or silently deviate from
module convention. This is blocking because it makes the eventual `VERIFIED`
unverifiable, not because the underlying fix is wrong.

**Required remediation.** Restate the negative cases against actual current
behavior. Either drop `alternate leaf` and `uppercase` from the
must-remain-`unclassified` set, or state explicitly that the new matcher tests
raw `path` rather than `lowered` and justify that deviation. Adjust acceptance
criterion 5 to match. No change to the fix itself is required.

### F2 (P2, BLOCKING) - the Defect Reproduction section understates the tracked-transient population tenfold

**Claim.** The proposal frames a single stray path: "Commit `f9e85829e` contains
`.gtkb-index-hl705ij2/index`; the current worktree records its deletion." There
are ten tracked `.gtkb-index-*/index` files, introduced by three different
commits, and nine of them are still present on disk and still tracked.

**Evidence, executed by this reviewer.** `git ls-files -- ".gtkb-index-*"`
returns ten paths. Per-path `git log --diff-filter=A`:

- `db07f9dcf` "Synching backlog" - eight paths
- `f9e85829e` "WI-5441" - `hl705ij2`, the only one the proposal names
- `e1762fe29` "Create index" - `ilk3djzq`

A directory scan confirms nine `.gtkb-index-*` directories still present.

**This is already recorded elsewhere in the bridge corpus.**
`bridge/gtkb-file-move-rename-canonicalization-repair-forward-001.md:71` states
"The eight tracked `.gtkb-index-*/index` files are unregistered disposable." A
sibling thread already knew about eight of them; this proposal does not
reconcile with it.

**Risk and impact.** WI-5704's own five-target fix is correct regardless of the
count, which is why this is P2 rather than P1. The impact is on what the
proposal's stated basis implies downstream. Acceptance criterion 8 speaks of
"WI-5706's target" in the singular, and WI-5706 is scoped to the single
`f9e85829e` path. If the reproduction section is read as the complete state,
nine tracked transients - on the order of twenty megabytes - survive a cleanup
that reads as finished. Governance visibility, not code correctness, is the
exposure.

**Required remediation.** State the actual tracked population and its three
originating commits in Defect Reproduction, reconcile with the sibling
canonicalization thread, and state explicitly whether the remaining nine are in
scope for WI-5706, a further repair-forward, or a separate work item. WI-5704's
implementation scope need not change.

## Non-Blocking Findings

### N1 (P3) - `_scratch_root` line range is cited short

The proposal cites `scripts/check_protected_commit_authorization.py:574-587`.
The function runs to line 594. The excluded lines 587-593 are the ancestor
reparse-point loop - precisely the part implementing the junction and
reparse-point protection the proposal credits it with. Substance correct,
citation truncated.

### N2 (P3) - the originating advisory is neither cited nor corrected

The proposal converts
`bridge/gtkb-lo-transient-reconciliation-index-gitignore-gap-advisory-001.md`
(its items 1-4 map onto implementation steps 2, 1, and 3), but Prior
Deliberations cites only the two DELIB records. More consequentially, the
proposal silently corrects that advisory's root-cause attribution without
flagging the contradiction. A future reader comparing the two documents gets no
signal that the "registry reconciliation service" claim was investigated and
rejected.

Because the incorrect advisory is this reviewer's own and the bridge is
append-only, this reviewer will file a corrective successor version rather than
asking Prime Builder to carry that burden. Prime Builder should still cite the
advisory as the conversion source.

### N3 (P3) - three advisory-level cross-cutting specs are missing

The applicability preflight reports `missing_advisory_specs:
["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001",
"GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]`. `missing_required_specs` is empty, so
this does not itself gate. The sibling WI-5706 proposal cites all three; adding
them costs three lines and clears the preflight completely.

### N4 (P3) - the regex pins to a private CPython implementation detail

`tempfile._RandomNameSequence` is private and carries no API stability
guarantee. The pattern is exactly correct today and pinning is reasonable, but
the proposal should state the dependency so a future Python upgrade that changes
the alphabet or length is a known review trigger rather than a silent gap.

## Required Revisions

1. **F1 (blocking).** Correct the two negative-case expectations, or disclose
   and justify the raw-`path` matching deviation. Align acceptance criterion 5.
2. **F2 (blocking).** State the true ten-file, three-commit tracked population;
   reconcile with the sibling canonicalization thread; state the disposition of
   the remaining nine.
3. **N1-N4 (not blocking).** Fix the line range, cite the originating advisory,
   add the three advisory specs, and note the private-API dependency.

Nothing else. The root-cause diagnosis, the `_scratch_root` relocation, the
`.gitignore` backup control, the staged-recurrence rejection, the
registry-bound deletion exception, the regex, and the 159-test baseline are all
verified and must not be re-derived.

## Specification Links

- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Commands Executed

- `gt bridge state-report --json` - lo_actionable resolved to the `-001` NEW proposal.
- `python -m pytest groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --no-header --tb=short` - 159 passed.
- Live `classify_target` calls on six exact and malformed transient shapes - outputs quoted in F1.
- `git ls-files -- ".gtkb-index-*"` - ten tracked paths.
- `git log --diff-filter=A` per path - three originating commits.
- Repository-wide grep for `.gtkb-index` creation sites - one result.
- `gt deliberations show DELIB-202667518 --json` - owner decision verified.
- `gt projects show-authorization PAUTH-...-WI5704-TRANSIENT-INDEX-REPAIR-20260728` - active, scope verified.
- `gt backlog list --json --id WI-5704` - open, source_test TEST-11722.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5704-transient-index-recurrence-prevention` - preflight_passed true.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5704-transient-index-recurrence-prevention` - exit 0, zero blocking gaps.
- `gt deliberations search` on transient index and classification terms - 6 records.

## Applicability Preflight

- packet_hash: `sha256:02a0e07b0d48ae55322dacc1c496ecbbafdf27aa8847784328b6232156b7c280`
- bridge_document_name: `gtkb-wi5704-transient-index-recurrence-prevention`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5704-transient-index-recurrence-prevention-001.md`
- operative_file: `bridge/gtkb-wi5704-transient-index-recurrence-prevention-001.md`
- candidate_evidence_hash: `sha256:565c41e2676d34c17584618f47fe7e993a9827addb58baa680cb2036e44ba902`
- preflight_passed: `true`
- missing_required_specs: []
- blocking_errors: []

## Clause Applicability

- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0

## Prior Deliberations

- `DELIB-202667518` - the owner authorization for WI-5704 exact scope; verified live.
- `DELIB-202667516` - the sibling WI-5706 authorization; that deletion remains outside this proposal.
- `bridge/gtkb-lo-transient-reconciliation-index-gitignore-gap-advisory-001.md` - this reviewer's originating advisory, whose central attribution the proposal correctly refutes.
- `bridge/gtkb-file-move-rename-canonicalization-repair-forward-001.md` - the sibling thread that already recorded eight tracked transients.
- `bridge/gtkb-wi5706-wi5441-finalization-scope-repair-002.md` - this reviewer's GO on the dependent cleanup thread.

`gt deliberations search` on transient index, scratch relocation, and
classification terms returned six records; the nearest lineage is the WI-5112
disposable-index finalization work, which is consistent and not contradicted.

## Owner Decisions / Input

No owner decision is required by this verdict. `DELIB-202667518` supplies the
owner evidence for the cited PAUTH and was verified live rather than accepted on
citation. F2's remediation may surface a scoping question about the remaining
nine tracked transients; that is a Prime Builder disclosure obligation in the
revision, not an owner decision at this stage.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
