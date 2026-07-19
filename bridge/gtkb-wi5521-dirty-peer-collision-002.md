GO
::init gtkb pb
::open test

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 211b1f8c-4852-4f93-8aa0-127e2517b7b9
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent session; independent Loyal Opposition review spawned from an owner-authorized recurring watch cycle covering the Ollama/OpenRouter provider-reliability chain and bridge/TAFE/dispatcher governance infrastructure; resolved role loyal-opposition

# LO Review - Proposal GO (gtkb-wi5521-dirty-peer-collision)

bridge_kind: lo_verdict
Document: gtkb-wi5521-dirty-peer-collision
Version: 002
Responds to: bridge/gtkb-wi5521-dirty-peer-collision-001.md
Reviewer role: loyal-opposition (fresh independent sub-agent session)
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5521
Recommended commit type: N/A (GO; no LO-authored implementation commit)

## Verdict Summary

GO. Both described gaps in `peer_report_dirty_path_collision_reason` are real
and independently reproduced against live source and live git state, not
merely taken on the proposal's word. The proposed remedy is correctly scoped,
reuses existing tested extraction infrastructure (`extract_target_paths`), and
its acceptance criteria precisely and self-consistently exclude the one
existing regression sub-case (terminal-VERIFIED-always-allows) that the fix
must intentionally change, rather than glossing over the conflict.
Specification linkage, prior deliberations, project authorization, and both
mandatory preflights are all independently confirmed live. No duplicate or
overlapping open thread was found.

## Independently Re-Verified Evidence

1. **Thread currency confirmed twice.** `gt bridge state-report` and `gt
   bridge show gtkb-wi5521-dirty-peer-collision --json`, run both before deep
   review and again immediately before this write, both show
   `latest_status: NEW`, `version_count: 1`, operative file
   `bridge/gtkb-wi5521-dirty-peer-collision-001.md` -- matching the sole
   on-disk file. No collision with another worker on this thread.

2. **Gap 1 (VERIFIED/WITHDRAWN peer exclusion) independently confirmed in
   source.** `scripts/implementation_authorization.py`
   `_peer_implementation_report_paths` (line 1412 as read) contains
   `if entry.latest_status in {"VERIFIED", "WITHDRAWN"}: return []` exactly as
   described -- a peer thread that reaches VERIFIED is unconditionally
   excluded from dirty-path collision scanning regardless of whether its
   underlying diff has actually landed in a commit.

3. **Gap 1's live real-world instance confirmed still open.**
   `git status --porcelain -- 'bridge/gtkb-wi5387-applicability-corrected-go-operative*.md'`
   shows all four files of that thread as `??` (untracked) right now. WI-5387
   (MemBase `stage=resolved`) cites a terminal VERIFIED verdict at `-004.md`
   that has never been committed -- the exact failure mode Gap 1 describes,
   live in this worktree today, and the reason WI-5502 exists.

4. **Gap 2 (heading-only extraction) independently confirmed in source.**
   `_reported_paths_from_implementation_report` (line 1356 as read) filters to
   `normalized_heading not in {"files changed", "implemented paths"}` only --
   no structured-metadata fallback exists today.

5. **Gap 2's cited historical example independently confirmed.**
   `bridge/gtkb-wi5403-declared-applicability-target-scope-005.md`
   (`bridge_kind: implementation_report`) uses `## Exact WI-5403 Ownership`,
   not `Files Changed`/`Implemented Paths` -- confirmed by direct grep and
   read of the file. That same report's header (line 27) carries
   `target_paths: ["scripts/bridge_applicability_preflight.py",
   "platform_tests/scripts/test_bridge_applicability_preflight.py"]`,
   confirming the proposed "extract structured target_paths and union" remedy
   would directly resolve this exact cited case using the header-metadata
   convention every proposal and report already carries.

6. **Proposed remedy reuses existing, tested infrastructure.**
   `extract_target_paths()` (line 738 of the same module) already parses this
   exact header `target_paths:` form (via `TARGET_PATHS_RE`) plus two
   documented fallback forms, and is already used elsewhere in the module for
   proposal-target extraction. Reusing it for implementation-report extraction
   is a low-risk design choice, not a new parsing surface.

7. **Existing regression-preservation claim independently verified accurate,
   including its precise boundary.**
   `platform_tests/scripts/test_implementation_authorization.py::test_peer_report_dirty_path_guard_allows_terminal_clean_same_thread_and_nonoverlap`
   (lines 355-371 as read) bundles four assertions: same-thread, nonoverlap,
   clean-path, and a VERIFIED-peer-always-allows case (lines 369-371,
   unconditional -- no git-commit distinction in the synthetic `tmp_path`
   fixture). The proposal's acceptance criterion 4 ("current-thread,
   clean-path, nonoverlap, bootstrap, and unreadable-peer regression cases
   remain unchanged") correctly omits the VERIFIED-terminal-allows sub-case
   from the preserved set, since that is precisely the behavior acceptance
   criteria 2-3 require the fix to change. This is a materially correct,
   non-hand-wavy scoping of the regression boundary -- no discrepancy found
   between the claim and the actual test code.

8. **Predecessor sequencing independently confirmed consistent.** WI-5521's
   own MemBase `status_detail` and the cited PAUTH's `scope_summary` both
   state implementation is hard-gated behind terminal WI-5382 and WI-5454.
   Live MemBase confirms neither is yet terminal: WI-5382 is at Prime
   `NO-ACTION` v011 (`bridge/gtkb-wi5382-invalid-terminal-verdict-reissue-011.md`),
   WI-5454 is a fresh `NEW` v001
   (`bridge/gtkb-wi5454-post-go-chain-state-001.md`). This GO approves the
   design; it does not and cannot force `begin` to succeed while the declared
   hard-gate predecessors remain non-terminal -- that is enforced separately
   at implementation-start time per `DCL-PROJECT-DEPENDENCY-ORDERING-001`.

9. **Declared target-path cleanliness independently confirmed to match
   WI-5521's own status_detail.**
   `git status --porcelain -- scripts/implementation_authorization.py
   platform_tests/scripts/test_implementation_authorization.py` shows
   `scripts/implementation_authorization.py` clean and
   `platform_tests/scripts/test_implementation_authorization.py`
   foreign-modified (`M`) -- exactly as WI-5521's MemBase status_detail
   states. This dirty test target will independently block `begin` at
   implementation-start time regardless of this GO, until resolved (expected
   to clear once WI-5382/WI-5454 finalize).

10. **All 18 cited Specification Links independently confirmed present in
    MemBase** via `KnowledgeDB.get_spec()` -- zero missing.

11. **All 5 cited Prior Deliberations independently confirmed present in
    MemBase** via `KnowledgeDB.get_deliberation()` -- zero missing.
    `DELIB-202666060` (WI-5105 Finalization Commingle Guard GO) is the
    correct, directly on-point predecessor citation: this proposal explicitly
    extends that guard.

12. **Cited project authorization independently confirmed live and
    matching.** `PAUTH-DISPATCHER-BLACK-BOX-WI5521-DIRTY-PEER-COLLISION-20260718`:
    `status=active`, `expires_at=null`,
    `included_work_item_ids=["WI-5521"]`. Its `scope_summary` is
    near-verbatim consistent with the proposal's "Proposed Scope" section
    (same hard-gate conditions, same structured-target_paths-union mechanism,
    same terminal-VERIFIED-until-in-HEAD relaxation). Its
    `owner_decision_deliberation_id`
    (`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`)
    independently confirmed present with `source_type=owner_conversation`,
    `outcome=owner_decision`.

13. **No duplicate or overlapping open thread found.** `gt bridge
    state-report`'s LO-actionable list and a MemBase backlog text search for
    "peer_report_dirty_path_collision_reason" and "dirty path collision" both
    return only WI-5521/this thread. WI-5105 (the predecessor this extends) is
    `resolution_status=resolved`, not a live conflicting thread. WI-5382 and
    WI-5454 target the same file but address distinct, non-overlapping
    defects in it (implementation-start packet-publish silence;
    `_post_go_chain_state` misclassification) and are explicitly sequenced
    ahead of this thread by project membership order, not duplicated by it.

14. **Review independence confirmed.** This review's session context
    (`211b1f8c-4852-4f93-8aa0-127e2517b7b9`, harness B / Claude, a fresh
    independent sub-agent session spawned from an owner-authorized recurring
    watch cycle) differs from the proposal's `author_session_context_id`
    (`019f6668-9974-7d72-a456-826f9a67e627`, harness A / Codex). Both are
    populated and readable; no fail-closed condition applies.

## Minor Observation (non-blocking)

The proposal's relaxation targets terminal `VERIFIED` peers specifically; a
terminal `WITHDRAWN` peer keeps the current unconditional exclusion. No live
evidence shows this as a current problem (unlike the VERIFIED/uncommitted
case, which has a concrete live instance in WI-5387/WI-5502), and a withdrawn
thread's risk profile genuinely differs from a verified-but-uncommitted one,
so this does not block GO. Worth a one-line note in the implementation report
confirming this is a deliberate scope boundary rather than an oversight.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` -- confirmed present, `specified`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` -- confirmed present, `verified`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` -- confirmed
  present; satisfied (18 concrete links, evidence-checked).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` -- confirmed present;
  proposal's Specification-Derived Verification Plan maps every linked spec
  to a verification method.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` -- confirmed present;
  satisfied (PAUTH + Project + Work Item + target_paths all present and
  cross-checked live).
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` -- confirmed present;
  satisfied (bridge GO required and being sought here before any
  implementation).
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` -- confirmed
  present; deferred to implementation-start time as designed.
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` -- confirmed present; PAUTH
  envelope independently verified bounded and active.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` -- confirmed present; independently
  verified the hard-gate on WI-5382/WI-5454 is real and currently unsatisfied
  (Evidence 8), which is correct proposal-stage behavior, not a defect.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` -- confirmed present;
  Intuitiveness/Non-Impairment Disposition block present and internally
  consistent with the rest of the proposal.
- `GOV-WORK-TREE-HYGIENE-001` -- confirmed present.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` -- confirmed present; both target
  paths independently confirmed in-root.
- `GOV-STANDING-BACKLOG-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`,
  `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `SPEC-AUQ-POLICY-ENGINE-001`
  -- confirmed present (standard auto-linked governing specs for this
  project's bridge threads).

## Prior Deliberations

- `DELIB-202666060` -- Loyal Opposition Verdict -- GO -- WI-5105 Finalization
  Commingle Guard. Confirmed present; this is the direct predecessor guard
  WI-5521 extends.
- `DELIB-202666393`, `DELIB-202666411`, `DELIB-202666557`, `DELIB-20265893`
  -- confirmed present in MemBase; standard sibling-thread/dependency-
  disposition citations for this project, consistent with the proposal's
  stated scope.
- Deliberation search ("peer_report_dirty_path_collision_reason"; "dirty peer
  collision guard terminal VERIFIED uncommitted") returned no additional
  directly-on-point prior deliberation beyond DELIB-202666060 already cited.

## Applicability Preflight

- packet_hash: `sha256:fbf92ffa68978f2bd6ae8d0a40406b578fb63875031600fe21854522b477596e`
- bridge_document_name: `gtkb-wi5521-dirty-peer-collision`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5521-dirty-peer-collision-001.md`
- operative_file: `bridge/gtkb-wi5521-dirty-peer-collision-001.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: sha256:480631d1046636b3716ba6471394a5831f2062250cd47ca81b6f2003d3afdfa5

Independently re-run fresh for this review via
`python scripts/bridge_applicability_preflight.py --bridge-id
gtkb-wi5521-dirty-peer-collision --content-file
bridge/gtkb-wi5521-dirty-peer-collision-001.md` (the explicit `--content-file`
form, matching the exact code path the bridge-compliance-gate freshness
re-check itself uses internally: `content_source=pending_content`). The
`--bridge-id`-only CLI form resolves the operative version through the index
instead (`content_source=bridge_file_operative`) and, while reporting the same
`declared_target_paths`/`missing_required_specs`, embeds a different
`content_source` string in the hashed packet and therefore reports a different
`packet_hash` for the identical underlying bytes -- a reproducibility quirk
between the two `build_packet()` call paths worth a follow-up hygiene note,
not a substantive discrepancy in preflight outcome.

## Clause Applicability

- Clauses evaluated: 5; must_apply: 4, may_apply: 1
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code `0` (pass)

Independently re-run fresh for this review.

## Conditions

- Acquire a fresh `go_implementation` claim and schema-v3 implementation-start
  packet before any mutation; `begin` is expected to fail closed until
  WI-5382 and WI-5454 are both terminal and both exact targets are clean
  (Evidence 8-9) -- this is expected, correct behavior, not a defect to work
  around.
- Stay within the declared exact targets
  (`scripts/implementation_authorization.py`,
  `platform_tests/scripts/test_implementation_authorization.py`); no
  foreign-hunk adoption unless expressly authorized.
- When updating
  `test_peer_report_dirty_path_guard_allows_terminal_clean_same_thread_and_nonoverlap`,
  explicitly split or adjust the VERIFIED sub-case (current lines 369-371) to
  reflect the new in-HEAD-dependent semantics rather than silently leaving an
  assertion that contradicts the new logic; keep the other three bundled
  sub-assertions (same-thread, nonoverlap, clean-path) passing unchanged.
- Independent LO VERIFIED and focused finalization required after the
  implementation report, with executed spec-derived tests per the proposal's
  Specification-Derived Verification Plan.
- No Git push, release, deployment, credential lifecycle, or destructive
  cleanup under this GO (matches the cited PAUTH's `forbidden_operations`).

## Methodology Trail

Read the full (single-version) thread. Ran `gt bridge state-report` and
`gt bridge show --json` twice (pre-review and immediately pre-write) to
confirm currency. Read `scripts/implementation_authorization.py` directly
(`peer_report_dirty_path_collision_reason`, `_peer_implementation_report_paths`,
`_reported_paths_from_implementation_report`, `extract_target_paths`) to
independently verify both claimed gaps against live source rather than
trusting the proposal's prose. Ran `git status --porcelain` against the
WI-5387 bridge-thread files and against both of this proposal's declared
target paths. Read `bridge/gtkb-wi5403-declared-applicability-target-scope-005.md`
directly (grep + full section read) to confirm the cited heading-mismatch
example and its header `target_paths:` metadata. Read
`platform_tests/scripts/test_implementation_authorization.py` (existing
peer-collision test block, lines ~300-392) to verify the "preserve existing
regression cases" claim against actual test code, not just prose. Queried
MemBase directly (`KnowledgeDB.get_spec`, `get_deliberation`,
`get_project_authorization`) for all 18 specification links, all 5 prior
deliberations, and the cited PAUTH. Queried MemBase backlog for WI-5521,
WI-5502, WI-5387, WI-5382, WI-5454, and WI-5105 to cross-check sequencing and
duplication claims. Ran both mandatory preflights fresh via their CLI entry
points. Searched deliberations semantically for the guard topic. Searched the
backlog and bridge state-report for duplicate/overlapping open work.
