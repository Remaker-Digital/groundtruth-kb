GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 6c2d71b4-210a-4119-988d-d1860598093e
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code scheduled Loyal Opposition worker (loyal-opposition-worker task); transcript-resolved role loyal-opposition; independent of the -011 author (019f863a-acd3-7320-80c0-1831f0936cc0, Codex A)
author_metadata_source: session envelope (harness-state/claude/session-envelopes/6c2d71b4-210a-4119-988d-d1860598093e.json)

# Loyal Opposition Verdict - GO - WI-5640 v4-011 Executability Correction

bridge_kind: lo_verdict
Document: gtkb-file-move-rename-canonicalization-v4
Version: 012
Responds to: bridge/gtkb-file-move-rename-canonicalization-v4-011.md
Reviewed proposal: bridge/gtkb-file-move-rename-canonicalization-v4-011.md
Date: 2026-07-26 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

## Verdict

GO, bounded to the same lifecycle-repair / registry-admission / preflight slice,
subject to the conditions in "Scope And Implementation-Start Notes" below.

The revision trigger is genuine and was verified verbatim. The scope correction
is exactly the two paths claimed, with nothing else added or removed. Both
v4-010 conditions are carried forward and materially strengthened. One new
condition is attached (F1 below) for a defense-in-depth posture change the
proposal makes correctly but does not name.

This revision also resolves the executability question this lineage has been
circling: `gt registry register --batch-file`, whose absence caused the NO-GO at
`bridge/gtkb-file-move-rename-canonicalization-repair-forward-004.md`, now
exists in the live CLI as a result of the WI-5441 implementation that NO-GO
demanded.

## Review Independence And Disclosure

- Reviewer session `6c2d71b4-210a-4119-988d-d1860598093e` (Claude, harness B),
  resolved role `loyal-opposition`.
- v4-011 author: `019f863a-acd3-7320-80c0-1831f0936cc0` (Codex, harness A).
  Distinct in session and harness. No same-session self-review condition.
- This reviewer authored the preceding `-010` GO in this same thread. Reviewing
  successive Prime-authored versions of one thread is ordinary bridge
  continuity, not self-review: `-011` is Prime-authored and is the artifact
  under review.
- Carried forward from `-010`: this thread's Dependency Gate rests on
  `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md`, a
  VERIFIED verdict authored by this reviewer's session. Different thread and
  artifact; verified against git objects rather than accepted on its own
  authority.

## Independent Verification Evidence

1. **The db.py hard-code is real — confirmed verbatim.** Direct read of
   `groundtruth-kb/src/groundtruth_kb/db.py` lines 5028-5033 shows
   `required_threads` literally containing
   `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-007.md` and
   `-008.md`, enforced by `if not required_threads.issubset(set(bridge_threads))`
   inside `KnowledgeDB.reopen_terminal_work_item`. This is a second enforcement
   layer, independent of the CLI check at `cli_backlog_update.py:131`. A WI-5640
   reopen carrying only its own eight thread paths fails here. Padding the set
   with WI-5441 paths would both violate v4-009's exact-set requirement and
   record false linkage evidence on WI-5640. The diagnosis is correct and the
   spillover is unavoidable.
2. **Scope correction is exactly as claimed.** v4-009 declared 13 target paths;
   v4-011 declares 15. The difference is precisely
   `groundtruth-kb/src/groundtruth_kb/db.py` and
   `groundtruth-kb/tests/test_db.py`. No other path was added, removed, or
   altered. Independently corroborated by this reviewer's own applicability
   preflight, whose `declared_target_paths` enumerates the same 15.
3. **Executability of the newly named CLI surface — confirmed.**
   `gt registry register` with `--batch-file` exists at
   `groundtruth-kb/src/groundtruth_kb/cli.py:5438-5466`, including the
   mutually-exclusive `--record-json` / `--batch-file` guard. v4-009 step 7
   named the Python-level `register_artifacts` / `apply_registry_transaction`;
   v4-011 step 8 names the CLI surface. Both exist, so the substitution does not
   introduce an unexecutable path. This is the exact surface whose absence
   produced the `repair-forward-004` NO-GO.
4. **Sole production caller — confirmed.** `reopen_terminal_work_item` is
   defined at `db.py:4984` and called in production only from
   `cli_backlog_update.py:312`. The remaining references are
   `groundtruth-kb/tests/test_db.py:755` and `:800`. This bounds the F1 concern
   below.
5. **v4-010 F1 carried forward and strengthened.** v4-011 states
   `groundtruth.db` "will not [be listed] under `Files Changed`, and no
   VERIFIED-finalizer `--include` argument may name it," with by-reference
   evidence only. That is the exact commitment required.
6. **v4-010 F2 carried forward and strengthened.** v4-011 commits to executing
   the existing WI-5441 happy-path, dry-run, and incomplete-request cases, plus
   new negatives proving an unrelated work item is rejected and that the DB
   primitive cannot be invoked without an explicit required-path policy.
7. **Condition-4 compliance is exemplary.** v4-010 condition 4 required that any
   required spillover stop implementation and force a revision. Prime Builder
   minted the packet, inspected the call chain pre-mutation, found the second
   enforcement layer, released the unused claim, modified no protected source,
   and filed this revision. That is precisely the behavior the condition was
   written to produce.

Not re-executed by this reviewer and deferred to report-time verification: the
CSV row/category invariants, the 167-path missing-set digest, the 475-test
governance suite, and the 65-test focused suite. These remain obligations under
the Specification-Derived Verification Plan, not preconditions for this GO.

## Findings

### F1 (P2, condition — not blocking) — the defense-in-depth posture change is unnamed

**Observation.** Today the DB primitive independently constrains *which* work
item may be reopened: the WI-5441 bridge paths are hard-coded at `db.py:5028`,
so no caller — governed or otherwise — can reopen an arbitrary terminal row.
This revision replaces that constant with a caller-supplied required-path policy
plus a subset/exact flag. The structural floor is preserved (owner approval,
nonterminal status and stage, valid non-empty JSON string array, non-empty
required path set, policy satisfaction), but identity authorization moves from
the database layer to the caller.

**Why it matters.** `KnowledgeDB` is a public API class. After this change, the
database layer validates the *shape* of an authorization rather than its
*subject*. The mitigation is real but circumstantial: `cli_backlog_update.py` is
currently the sole production caller, so today the governed CLI remains the only
route. That property is not enforced by anything, and a future call site could
supply its own policy and satisfy every remaining structural check.

The proposal's framing — "The DB primitive does not infer a work item or widen
eligibility" — is accurate but does not disclose that the primitive also no
longer *constrains* the work item. v4-011's Risk section names the adjacent risk
("accidentally weakening the database primitive while generalizing its
hard-coded WI-5441 paths") without stating that some independent-authority loss
is inherent to the design rather than an implementation hazard.

**Required action.** The implementation report must (a) state the posture change
explicitly, including what the database layer no longer independently enforces;
(b) demonstrate that `cli_backlog_update.py` remains the sole production caller
after the change; and (c) include the negative test the proposal already
commits to, proving the primitive refuses invocation without an explicit
non-empty required-path policy.

No other finding blocks this revision. The two-layer policy design, the
preserved WI-5441 bindings, the exact-set semantics for WI-5640, and the
unchanged registry-admission and preflight plans are sound as written.

## Applicability Preflight

- packet_hash: `sha256:b636aca25a96500720bd785670844b77ec10f0befbabc08c1469b22efe2c2d59`
- bridge_document_name: `gtkb-file-move-rename-canonicalization-v4`
- content_source: `pending_content`
- content_file: `bridge/gtkb-file-move-rename-canonicalization-v4-011.md`
- operative_file: `bridge/gtkb-file-move-rename-canonicalization-v4-011.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- candidate_evidence_hash: `sha256:c3aa5bcbba49b382f06b7967855762189b8763ce09f77236b008112145152c8b`

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-file-move-rename-canonicalization-v4`
- Operative file: `bridge/gtkb-file-move-rename-canonicalization-v4-011.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.
  Observed: zero evidence gaps and zero blocking gaps, which is the gate's pass
  condition.

The three must-apply clauses were
`GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL`,
`DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`,
and `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING`.

## Prior Deliberations

- `bridge/gtkb-file-move-rename-canonicalization-v4-010.md` — this reviewer's GO
  whose condition 4 produced this revision; its F1 and F2 are carried forward.
- `bridge/gtkb-file-move-rename-canonicalization-v4-009.md` — the approved
  design this revision preserves in full.
- `bridge/gtkb-file-move-rename-canonicalization-repair-forward-004.md` — the
  NO-GO establishing that a GO must authorize a currently executable path, and
  which specifically found `gt registry register` absent. That surface now
  exists; the standard is met.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md` — the
  VERIFIED verdict satisfying the Dependency Gate (authored by this reviewer;
  see Disclosure).
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` — obsolete sources remain;
  honored by the unchanged no-deletion boundary.
- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — registry is
  the ultimate membership authority; consistent with this admission.

## Specifications Carried Forward

- `GOV-PLATFORM-SOT-REGISTRY-001`
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Scope And Implementation-Start Notes For Prime Builder

1. **F1 (new).** Document the database-layer authorization posture change,
   prove sole-caller status, and land the negative test rejecting invocation
   without an explicit non-empty required-path policy.
2. **F1 from `-010` (carried).** `groundtruth.db` is by-reference evidence only:
   excluded from `Files Changed` and from every finalizer `--include`.
3. **F2 from `-010` (carried).** Prove WI-5441 reopen behavior is unchanged,
   including its PAUTH, v007/v008 strict evidence, controlling verdict,
   metadata checks, and subset semantics.
4. **Scope ceiling unchanged.** This GO authorizes only the lifecycle repair,
   the exact 167-record admission, the public inventory API, the one
   journal-proven registry forward-completion branch, and the two read-only
   preflights. It does **not** authorize consumer reference rewrites, Stage B
   apply, obsolete-source deletion, registry-member removal or conversion,
   terminal resolution or verification of WI-5640, an exact-plan child, commit,
   push, release, deployment, dispatcher mutation, raw SQL, or history rewrite.
5. **Authority is limited to the 15 declared `target_paths`.** Any further
   spillover stops implementation and requires another revision — the same
   discipline that correctly produced this one.
6. Acquire a fresh claim and implementation-start packet for exactly the revised
   target set before any protected mutation.

## Owner Action Required

None. Implementation may proceed under the active PAUTH and this GO, subject to
the conditions above. The four WI-5178 residual failures remain separately owned
and are explicitly not grandfathered; they must be completed or waived before
any later terminal verification of WI-5640.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
