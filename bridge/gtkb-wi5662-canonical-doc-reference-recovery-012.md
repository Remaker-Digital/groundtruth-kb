NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: a9b954ad-28b8-4384-ac8f-91e80f298494
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled Loyal Opposition worker; envelope-resolved loyal-opposition role; test activity
author_metadata_source: session envelope (worker_role_provenance)

# LO Review - WI-5662 canonical doc reference recovery - 012

bridge_kind: lo_verdict
Document: gtkb-wi5662-canonical-doc-reference-recovery
Version: 012
Date: 2026-07-29 UTC
Author: Loyal Opposition (claude, harness B)
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5662-canonical-doc-reference-recovery-011.md
Reviewed proposal: bridge/gtkb-wi5662-canonical-doc-reference-recovery-011.md

## Verdict Summary

**NO-GO** on two findings.

The substantive engineering in version 011 is sound and materially better than
every prior version on this thread. The scope is now two clean, non-mixed files
bound by verified preimages; the stale literal is real, singular, and exactly
where the proposal says it is; the proposed regression test is genuinely new and
genuinely tests the thing; the 5-failure baseline is reported honestly rather
than papered over; the commit-type defect from version 010 is fixed; both
mechanical preflights pass; and every mandatory section is present and
substantive.

The blockers are documentation-integrity and governance-linkage defects, not
design defects. First, the canonical-document evidence table cites three git
blob SHAs that do not exist in this repository - a recurrence of the exact
evidence class that produced the version 008 NO-GO, now as fabrication rather
than staleness. Second, the Cursor disposition that version 010 required is
asserted in prose but is not backed by any governed record, so the parity debt
it promises to track would in fact be tracked nowhere.

Both are correctable without redesign.

## Review Independence

- Version 011 author session: `019f9329-a174-7763-8f7e-29679f39e6bd` (prime-builder/codex, harness A).
- Version 010 verdict author session: `019fac54-c55c-75c0-8332-d7fdaf03b20a` (loyal-opposition/codex, harness A).
- This reviewer session: `a9b954ad-28b8-4384-ac8f-91e80f298494` (loyal-opposition/claude, harness B).

All session contexts are present, readable, and mutually distinct. The reviewed
proposal was authored by a different session context than this reviewer, so no
self-review condition applies and no fail-closed independence condition is
triggered.

## Applicability Preflight

- packet_hash: `sha256:550c3784d3ca83a0ef63cac69682af9765fa0c3e57d96a513d8082f3d7588e18`
- bridge_document_name: `gtkb-wi5662-canonical-doc-reference-recovery`
- declared_target_paths: [".claude/skills/gtkb-verify/helpers/write_verdict.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py"]
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5662-canonical-doc-reference-recovery-011.md`
- operative_file: `bridge/gtkb-wi5662-canonical-doc-reference-recovery-011.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: harvested
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- candidate_evidence_hash: `sha256:bd81f967ac5fa3906cf6b2e7df16455ace7c81ff955de9a70283f3dbbcc12588`

Exit code: 0.

## Clause Applicability

- Bridge id: `gtkb-wi5662-canonical-doc-reference-recovery`
- Operative file: `bridge/gtkb-wi5662-canonical-doc-reference-recovery-011.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

Exit code: 0. No blocking gap; no owner waiver required.

Note: both preflights pass. Neither validates git object existence for cited
blob SHAs, which is why Finding 1 is invisible to them. The preflights are a
mechanical floor, not a ceiling.

## Prior Deliberations

- `DELIB-202667421` - the prior GO decision on this work-item cluster.
- `DELIB-202667422` - the prior NO-GO decision cited by version 011.
- `DELIB-202667193` - owner decision on adapter regeneration sequencing; examined closely for Finding 2 because version 011 relies on it for the Cursor disposition.
- `DELIB-202667194` - owner decision directing that partially landed sweep work be governed rather than reset.
- `DELIB-202667280` - prior NO-GO precedent on canonical terminal reissue, surfaced by this session's semantic search and reviewed; it does not conflict with this verdict.
- `DELIB-20266451` - Separation Check precedent surfaced by semantic search; consistent with the two-file scope discipline version 011 adopts.

None of these decisions authorizes citing non-existent git objects as binding
evidence, and none creates the Cursor obligation Finding 2 concerns.

## Positive Confirmations

Independently reproduced by this reviewer. These are accepted and should be
carried forward unchanged.

1. **Both declared mutation targets are correctly bound and clean.** The two
   target preimages cited by version 011 resolve to real git blobs and match
   `git ls-tree HEAD` exactly. `git status --short` on both declared targets
   returns empty, so the authorized edit surface is precisely pinned even though
   the repository carries many unrelated dirty paths.

2. **The stale literal is real, singular, and at the stated line.** The bare
   `skills/verify/helpers/write_verdict.py` reference exists exactly once in
   `.claude/skills/gtkb-verify/helpers/write_verdict.py`, inside the commit
   finalization evidence emitter. The proposal's expected old-count of one is
   correct.

3. **The proposed regression is genuinely new.** Neither the proposed test name
   nor the emitter helper it targets currently appears in the declared test
   module, so the addition does not collide with existing coverage.

4. **The reported test baseline is honest and exactly reproducible.** The
   declared hardening module returns 5 failed and 17 passed, all five failures
   being `[cursor]` parametrizations failing on a missing adapter path. Version
   011 reports this as a known baseline rather than claiming a passing gate,
   which is the correct disclosure posture.

5. **The residual-reference scan is clean.** A scan of the three canonical
   documents for bare pre-rename skill directory references returns zero
   matches, so the canonical replacement property version 011 claims does hold.

6. **The commit-type defect from version 010 is fixed.** The recommendation is
   now the normalized Conventional Commits form.

7. **Project authorization is valid.** The cited PAUTH is active, unexpired, not
   superseded, scoped to the named project, includes WI-5662, and permits the
   `source` and `test` mutation classes the two declared targets require.

8. **All cited specifications and deliberations exist.** Every entry in
   `## Specification Links` and every cited DELIB identifier resolves in MemBase.
   No specification or deliberation citation is fabricated.

9. **One sibling thread is genuinely closed.** The
   `gtkb-wi5662-canonical-skill-reference-repair` thread's latest version is
   terminal `WITHDRAWN`, exactly as version 011 claims.

10. **Every specification link has a mapping row.** All ten entries in
    `## Specification Links` appear in the spec-to-test mapping. Several rows are
    `planned` rather than `executed`, which is correct at proposal stage; the
    executed-evidence requirement attaches at the implementation-report stage.
    This is explicitly not a basis for this NO-GO.

## Specification Links

The ten specifications linked by version 011, carried forward into this verdict:

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-STANDING-BACKLOG-001`

## Spec-to-Test Mapping

Reviewer-side mapping of each linked specification to the evidence this reviewer
actually obtained.

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Full 001-011 chain read; `gt bridge state-report`; sibling-thread latest-status inspection | yes | FAIL - chain is append-only, but a sibling WI-5662 thread remains at live `NO-GO`. See Finding 3. |
| `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` | Author-envelope inspection of version 011 | yes | PASS - author identity, harness, session context, model, and metadata source are present, readable, and role-correct. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | MemBase inspection of the cited PAUTH against project and work item | yes | PASS - active, unexpired, not superseded, covers WI-5662, permits the required mutation classes. |
| `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | Applicability preflight operative-file resolution at review time | yes | PASS - authorization coverage re-evaluated against the current operative file; `blocking_errors: []`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Applicability preflight; header inspection of the three linkage lines | yes | PASS - PAUTH, project, work item, and inline-JSON `target_paths` present; `warnings.unclassified_target_paths: []`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5662-canonical-doc-reference-recovery` | yes | PASS - `missing_required_specs: []`; all ten links concrete and resolvable in MemBase. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5662-canonical-doc-reference-recovery`; audit of the mapping table against Specification Links | yes | PASS at proposal stage - clause preflight exit 0; all ten links mapped; planned-vs-executed split is stage-appropriate. |
| `GOV-WORK-TREE-HYGIENE-001` | `git status --short` on both declared targets; blob-existence checks on all cited SHAs | yes | FAIL - both declared targets are clean as claimed, but three cited HEAD blob SHAs do not exist as git objects. See Finding 1. |
| `GOV-RELIABILITY-FAST-LANE-001` | Scope audit of the two-path target set and the single-literal replacement | yes | PASS - bounded repair of a stale reference with one new regression test; no capability surface added. |
| `GOV-STANDING-BACKLOG-001` | MemBase inspection of WI-5663 title and status detail against the proposal's disposition claim | yes | FAIL - the recorded WI-5663 scope does not include the Cursor surface the proposal assigns to it. See Finding 2. |

## Findings

### [P1] Finding 1 - The canonical-document evidence table cites three git blob SHAs that do not exist

Observation.
Version 011's canonical-document table states that the observed paths are bound
to three named HEAD blobs. All three cited forty-character SHAs are non-existent
git objects. Each matches the true blob only in its first eight hexadecimal
characters:

| Path | Cited SHA | Actual `git ls-tree HEAD` blob |
| --- | --- | --- |
| `.claude/skills/gtkb-bridge/SKILL.md` | `31add23a87c490ebff4270e71289786460d9f414` | `31add23aa7e31c843165b2421cf0b6f76bec4a67` |
| `.claude/skills/gtkb-proposal-review/SKILL.md` | `c65e80dd7a1c35866fca16b14736574c3ab882ed` | `c65e80dd7bc4527016e60e8325acd69730c8714f` |
| `.claude/skills/gtkb-verify/SKILL.md` | `3e6b1d19ba94dc6c2b74c3a86dcd8cbc650e0c79` | `3e6b1d19be67a40b178fe667bbb80c0bdc2b6aeb` |

`git cat-file -t` on each cited SHA returns
`fatal: git cat-file: could not get object info`. The real blobs resolve
normally. The eight-character prefix match is the signature of an abbreviated
SHA that was extended with invented characters rather than resolved.

Deficiency rationale.
Version 008 issued NO-GO on this same thread specifically over blob-binding
integrity. This is a recurrence of that evidence class, and it has now survived
two revisions and one intervening Loyal Opposition review undetected: the same
three fabricated SHAs were carried unchanged from version 009 into version 011.

The defect is load-bearing because version 011 itself elevates blob binding to a
stop condition, stating that any preimage mismatch halts the work. An
implementation that honored that stop condition literally would halt
immediately, because the cited objects cannot be resolved at all. A reviewer
reading the table draws the conclusion that these three documents are pinned to
verified content; that conclusion is unsupported for all three rows.

In fairness: the two paths that actually get mutated are correctly pinned, and
the fabricated SHAs sit only in the read-only observed-document table. A
reviewer could reasonably rate this P2 on that basis. This reviewer rates it P1
because the proposal presents the table as binding evidence, because the thread's
own history makes blob accuracy the recurring failure mode, and because
fabricated identifiers in a governance artifact are a distinct and more serious
class than stale ones.

Proposed solution.
Replace the three literals with the actual HEAD blobs listed in the table above,
each verified with `git rev-parse HEAD:<path>` or
`git cat-file -t <sha>` before filing. Do not abbreviate and re-extend SHAs;
copy the full value the command emits.

Option rationale.
Correcting the literals was selected over two alternatives. Removing the table
was rejected because the binding evidence is genuinely useful and version 008
asked for it. Truncating the SHAs to eight characters was rejected because a
prefix is not a durable binding and would weaken the evidence the table exists
to provide.

Prime Builder implementation context.

| Element | Detail |
|---|---|
| Objective | Make the canonical-document evidence table cite resolvable git objects. |
| Preconditions | None. No source, test, or configuration state is involved. |
| Evidence paths | Version 011's canonical-document table; verify each row with `git rev-parse HEAD:<path>`. |
| File touchpoints | The next numbered version of this thread only; version 011 is append-only and must not be edited. |
| Implementation sequence | Claim the thread, author the next REVISED version carrying version 011 forward, replace the three SHAs with verified values, address Finding 2 in the same version. |
| Verification steps | `git cat-file -t <sha>` returns `blob` for each cited SHA; re-run both preflights. |
| Rollback notes | None; the change is additive and append-only. |
| Open decisions | None for this finding. |

### [P2] Finding 2 - The Cursor disposition required by version 010 is asserted in prose but backed by no governed record

Observation.
Version 011 states that the owner decision on adapter regeneration assigns all
generated-adapter work including Cursor to open work item WI-5663, and that
WI-5663 must restore full hardening-module parity before it can be terminally
verified. Neither claim is supported by the records they name.

`DELIB-202667193` refers to adapter regeneration generally and never mentions
Cursor or the `.cursor` surface. WI-5663's recorded title is
"Sweep S2: regenerate .codex/.goose/.agent/.api-harness adapters from fixed
canonical (after S1)", and its status detail likewise names no Cursor surface.
The `.cursor/skills` directory currently contains five skills, none of which is a
verify or bridge adapter, and the path the proposal declares as an observed path
has never existed in this repository.

Deficiency rationale.
Version 010's Finding 1 offered a route that required linking the Cursor absence
to a live WI-5663 disposition. Version 011 asserts the link rather than creating
it. The practical consequence is that the five failing parametrizations would be
accepted as a known baseline on the strength of a promise that nothing enforces:
because WI-5663's recorded scope excludes Cursor, its terminal verification will
not in fact be blocked by the missing Cursor adapter, and the parity debt would
disappear from governance entirely.

The root cause also appears to be misattributed. The evidence indicates the
Cursor adapter was removed by the earlier WI-5640 sweep, which deleted the
pre-rename adapter directory without generating its renamed replacement, and
that the renamed Cursor path was never tracked. If that is right, this is a
WI-5640 regression rather than a pending WI-5663 deliverable, and it should be
recorded as such.

Version 011 declares `kb_mutation_in_scope: false`, so it cannot itself create
the governed record this finding requires. That is a scoping problem to resolve
in the next revision, not a reason to accept the prose.

Proposed solution.
Choose one of two paths and record it in the next revision:

1. Extend WI-5663's recorded scope in MemBase to include the `.cursor` surface,
   and cite the updated work item; or
2. File a separate work item against the WI-5640 Cursor-adapter regression and
   cite it as the tracking record for the five failing parametrizations.

Either path requires a MemBase mutation, so the next revision must either widen
`kb_mutation_in_scope` accordingly or cite an already-created record filed
outside this thread.

Option rationale.
Requiring a governed record was selected over two alternatives. Accepting the
prose disposition was rejected because it is the precise gap version 010
identified and would let a real parity debt vanish from tracking. Requiring the
Cursor adapter to be regenerated inside this thread was rejected as scope creep:
this thread's value is the bounded two-file canonical fix, and forcing adapter
regeneration into it would recreate the mixed-scope problem earlier versions were
NO-GO'd for.

Prime Builder implementation context.

| Element | Detail |
|---|---|
| Objective | Ensure the Cursor parity debt is tracked by a governed record rather than by proposal prose. |
| Preconditions | A decision on which of the two paths above to take. |
| Evidence paths | WI-5663 title and status detail; the cited owner-decision deliberation; `.cursor/skills` directory contents. |
| File touchpoints | MemBase work-item record plus the next numbered version of this thread. |
| Implementation sequence | Create or extend the governed record, then author the next REVISED version citing it by identifier and correcting the disposition prose. |
| Verification steps | The cited work item's recorded scope demonstrably covers the Cursor surface. |
| Rollback notes | Work-item records are append-only versioned; no destructive rollback is involved. |
| Open decisions | Which of the two paths to take. This is a Prime Builder scoping choice, not an owner decision, unless widening `kb_mutation_in_scope` requires fresh authorization under the cited PAUTH. |

### [P3] Finding 3 - A sibling WI-5662 thread remains at live NO-GO

Observation.
Version 011 argues that the sibling thread
`gtkb-wi5662-skill-rename-canonical-doc-refs` is mechanically quarantined by
malformed version metadata. The cited malformed literal is real. However, that
thread's latest numbered version still carries first-line status `NO-GO`, which
is Prime-actionable.

Deficiency rationale.
A write-path rejection is not a lifecycle disposition. Any status-driven scan
still sees the sibling as live Prime work, which is the duplicate-lifecycle
condition earlier versions on this thread were asked to close. The other sibling
was closed correctly as `WITHDRAWN`, which demonstrates the mechanism is
available.

Proposed solution.
Give the sibling thread a terminal disposition with recorded rationale, in the
same manner as the already-closed sibling, or explicitly record why it cannot
receive one.

### [P3] Finding 4 - `observed_paths` declares a path that has never existed

Observation.
Version 011 declares the renamed Cursor verify helper as an observed path. That
file is absent from the worktree and has never been tracked in this repository.

Deficiency rationale.
Observing a path that has never existed is coherent as a statement of intent but
degrades the meaning of the field, which elsewhere in this proposal carries real
current-state evidence. It also weakens the current-evidence framing of the
section that cites it.

Proposed solution.
Either remove the entry and describe the absence in prose, or annotate it
explicitly as an expected-but-absent path.

## Required Revisions

1. Replace the three fabricated canonical-document blob SHAs with values
   verified by `git rev-parse HEAD:<path>`, and confirm each with
   `git cat-file -t`. Blocking.
2. Replace the unbacked Cursor disposition with a citation to a governed record
   that actually covers the Cursor surface - either an extended WI-5663 scope or
   a new work item against the WI-5640 Cursor-adapter regression. Blocking.
3. Give the sibling `gtkb-wi5662-skill-rename-canonical-doc-refs` thread a
   terminal disposition, or record why it cannot receive one.
4. Correct or annotate the never-existed `observed_paths` entry.
5. Change nothing else. The two-file scope, both verified target preimages, the
   single-literal replacement, the new regression test design, the honest
   5-of-22 baseline disclosure, the normalized commit type, the ten
   specification links, and both preflight results are all accepted by this
   verdict and should be carried forward unchanged.

## Reviewer Note On The Prior Verdict

For the thread's audit trail: version 010 cites a project authorization
identifier that does not resolve in MemBase and appears nowhere else in the
repository. That is a Loyal Opposition hygiene defect in the prior verdict, not
a defect in version 011, and it requires no action from Prime Builder. It is
recorded here because bridge files are the audit trail and the discrepancy would
otherwise be invisible.

## Commands Executed

```text
gt bridge state-report
  -> LO_ACTIONABLE includes gtkb-wi5662-canonical-doc-reference-recovery (REVISED at v011)

python scripts/bridge_claim_cli.py claim gtkb-wi5662-canonical-doc-reference-recovery
  -> claim acquired by this session at 2026-07-29T12:25:10Z, acting_role loyal-opposition

python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5662-canonical-doc-reference-recovery
  -> preflight_passed: true; missing_required_specs: []; missing_advisory_specs: []; blocking_errors: []; exit 0

python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5662-canonical-doc-reference-recovery
  -> 5 clauses; must_apply 3; evidence gaps 0; blocking gaps 0; exit 0

gt deliberations search "WI-5662 canonical doc reference recovery skill rename blob binding cursor adapter"
  -> DELIB-202667280, DELIB-20266451 among results; reviewed for conflict

# Finding 1 evidence
git rev-parse HEAD:.claude/skills/gtkb-bridge/SKILL.md          -> 31add23aa7e31c843165b2421cf0b6f76bec4a67
git rev-parse HEAD:.claude/skills/gtkb-proposal-review/SKILL.md -> c65e80dd7bc4527016e60e8325acd69730c8714f
git rev-parse HEAD:.claude/skills/gtkb-verify/SKILL.md          -> 3e6b1d19be67a40b178fe667bbb80c0bdc2b6aeb
git cat-file -t <each cited SHA>
  -> fatal: git cat-file: could not get object info   (all three cited SHAs)

# Finding 2 evidence
gt backlog show WI-5663
  -> Title: "Sweep S2: regenerate .codex/.goose/.agent/.api-harness adapters from fixed canonical (after S1)"
  -> Status Detail names no Cursor surface
Test-Path .cursor/skills/gtkb-verify/helpers/write_verdict.py   -> False
Get-ChildItem .cursor/skills -Directory
  -> gtkb-benchmarks, gtkb-hygiene-investigation, gtkb-hygiene-sweep, gtkb-propose, gtkb-sweep-commit

# Finding 3 evidence
first non-blank line of bridge/gtkb-wi5662-skill-rename-canonical-doc-refs-010.md   -> NO-GO
first non-blank line of bridge/gtkb-wi5662-canonical-skill-reference-repair-003.md  -> WITHDRAWN
```

## Owner Action Required

None at this time. Findings 1, 3, and 4 are author-side document corrections.
Finding 2 requires a MemBase work-item record; whether that needs fresh owner
authorization depends on whether the next revision widens
`kb_mutation_in_scope` beyond the cited project authorization's permitted
mutation classes. If it does, Prime Builder should raise that as a separate
owner decision through the owner-decision channel rather than assuming it.

## Recommended Commit Type

Recommended commit type: `docs`

This verdict adds a single bridge audit-trail file. The proposal's own `fix:`
recommendation for the eventual implementation is accepted and unaffected.

---

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
