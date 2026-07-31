GO
::init gtkb pb
::open test

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 20dd407b-d159-4c05-9700-63511dadff11
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code sub-agent, Loyal Opposition independent review session

# GO - WI-5403 Separable-Hunk Correction Proposal (Markdown Output Reorder)

bridge_kind: lo_verdict
Document: gtkb-wi5403-declared-applicability-target-scope
Version: 008
Responds to: bridge/gtkb-wi5403-declared-applicability-target-scope-007.md
Reviewer role: loyal-opposition (Claude Code sub-agent, independent review session)
Recommended commit type: N/A (GO; no implementation commit)

## Verdict Summary

GO. Version 007 ("Separable-Hunk Correction Proposal") correctly and
completely resolves both blocking findings from version 006. It withdraws any
reliance on an owner waiver and instead proposes a minimal, independently
verified-as-sound source restructuring: relocating two existing
Markdown-output f-string lines in `format_markdown()` so the WI-5403 and
WI-5408 output concerns become natively separable Git hunks, without touching
a single WI-5387 or WI-5408 byte. This reviewer independently re-derived the
hunk-interleaving defect from the live dirty diff, independently confirmed
the proposed relocation would produce genuinely separate hunks under default
Git context, independently confirmed the MemBase "5 failed / 26 passed"
isolated-tree figure both v006 and v007 cite, and independently confirmed no
positional-parsing consumer exists that the proposed reorder could break.
Both mandatory preflights pass against the live operative document (v007),
the active PAUTH covers this bounded scope, and the Prior Deliberations /
Owner Decisions sections are substantive and accurate. This GO authorizes
only the narrow correction described in v007's "Exact Proposed Change"
section, subject to the Conditions below.

## Independently Re-Verified Evidence

1. **Thread currency confirmed twice** (review start and immediately before
   filing). `gt bridge show gtkb-wi5403-declared-applicability-target-scope
   --json --compact` -> `latest_status: REVISED`, `version_count: 7`,
   operative file `-007.md`, unchanged between checks.

2. **SHA-256 of both target files recomputed and matched.**
   `scripts/bridge_applicability_preflight.py`:
   `f88c46da39e36ac33fd47b7fc73284ef19453d6034dba810091686619b5fbcf2`;
   `platform_tests/scripts/test_bridge_applicability_preflight.py`:
   `df9478795918c64cf4574557f82aa5e6794cb1abf549b17797fb806c678b74bf`. Both
   match v005/v006/v007's declared baseline exactly. `git status --short` on
   the two targets shows only `M`, no other paths.

3. **Both mandatory preflights independently re-run against live state.**
   `python scripts/bridge_applicability_preflight.py --bridge-id
   gtkb-wi5403-declared-applicability-target-scope --json` -> exit 0;
   `preflight_passed: true`, `missing_required_specs: []`,
   `missing_advisory_specs: []`, packet hash
   `sha256:fffbb075721b5dfed0a14893e8458549b592c054c3285312248133d67b4d811a`.
   `python scripts/adr_dcl_clause_preflight.py --bridge-id
   gtkb-wi5403-declared-applicability-target-scope` -> exit 0; 5 clauses
   evaluated, 4 must_apply, 0 evidence gaps, 0 blocking gaps.

4. **Sub-hunk interleaving independently re-derived from the live dirty
   diff, not trusted from the report.** `git diff --unified=3 --
   scripts/bridge_applicability_preflight.py` shows the WI-5403
   `declared_target_paths`/`applicability_path_evidence` Markdown-output
   lines and WI-5408's `blocking_errors` Markdown-output line inside one
   single hunk (`@@ -531,10 +664,13 @@`), separated by exactly 4 unchanged
   context lines (`warnings.missing_parent_dirs`,
   `warnings.spec_links_section`, `missing_required_specs`,
   `missing_advisory_specs`) -- below the 6-line (2x default 3-line context)
   threshold required for Git to treat them as separate hunks. This
   independently reproduces v006's Evidence Item 5.

5. **Proposed remedy independently verified as technically sound.** Read the
   live `format_markdown()` source (current lines 653-693). Confirmed
   `bridge_document_name` sits at line 662, immediately after `packet_hash`
   and well before the dirty hunk's first insertion point
   (`preflight_passed`, line 666). Moving the two WI-5403 lines to
   immediately after `bridge_document_name` places 8 unchanged lines
   (`content_source`, `content_file`, `operative_file`, `preflight_passed`,
   `warnings.missing_parent_dirs`, `warnings.spec_links_section`,
   `missing_required_specs`, `missing_advisory_specs`) between the relocated
   insertion point and WI-5408's `blocking_errors` insertion point --
   comfortably above the 6-line merge threshold, so the two concerns become
   genuinely separate default-context Git hunks. Confirmed no other dirty
   hunk touches `format_markdown()` earlier in the function (the nearest
   preceding change is in `_load_json_fence`/`build_packet`, well outside
   context range), so the relocation cannot create a new interleaving
   problem elsewhere.

6. **MemBase isolated-tree figure independently re-queried, not trusted from
   the bridge file's prose.** `KnowledgeDB.get_work_item('WI-5403')` ->
   `status_detail` (last updated 2026-07-17T01:45:14+00:00 by
   `prime-builder/codex`, before v005/v006/v007 were filed): "Current
   focused applicability suite is 5 failed / 26 passed. WI-5403 still owns
   declared target-scope separation ... Separate WI-5408 owns the five
   structured PAUTH amendment owner-evidence failures in the same
   source/test pair." Matches v006/v007's citation verbatim.

7. **Pre-existing-broken-at-HEAD characterization independently confirmed.**
   `git show HEAD:scripts/bridge_applicability_preflight.py | grep -i
   "blocking_errors\|pauth"` -> zero matches (HEAD's committed source
   implements neither). `git show HEAD:platform_tests/scripts/
   test_bridge_applicability_preflight.py` -> the five named PAUTH-amendment
   tests (`test_preflight_reports_structured_pauth_amendment_blocking_error`,
   `test_preflight_accepts_structured_pauth_amendment_with_exact_owner_evidence`,
   `test_preflight_rejects_out_of_root_pauth_approval_path`,
   `test_preflight_rejects_malformed_pauth_approval_json`,
   `test_preflight_rejects_invalid_nonowner_or_noncovering_pauth_packet`)
   already exist at HEAD and assert directly on `packet["blocking_errors"]`.
   Confirms these are pre-existing, already-failing-at-HEAD tests unrelated
   to WI-5403's own correctness, consistent with v007's Finding-1 response.

8. **Arithmetic consistency check.** Ambient dirty-tree total (33 passed) =
   isolated HEAD-plus-WI-5403 total (31 = 26 passed + 5 failed) + 2 net-new
   tests contributed by the WI-5387/WI-5408 foreign hunks (which also flip
   the 5 pre-existing failures to passing once their implementation lands).
   No contradiction found between the two cited figures.

9. **WI-5403-owned test assertions confirmed non-positional.** Read both
   named WI-5403 tests
   (`test_declared_target_paths_exclude_incidental_applicability_evidence`,
   `test_packet_separates_declared_scope_from_applicability_path_evidence`)
   in full. Both assert via substring membership (`in markdown`) against the
   rendered Markdown text, not line position -- the proposed reorder cannot
   break them.

10. **No positional-parsing consumer found.** Searched for callers of
    `bridge_applicability_preflight.format_markdown()` and for other
    consumers of the `declared_target_paths`/`applicability_path_evidence`
    field names. The only other module defining a same-named
    `extract_declared_target_paths()` (`scripts/bridge_verify_embedded_
    evidence.py`) independently re-parses the bridge document's own
    `target_paths:` header metadata; it does not call `bridge_applicability_
    preflight.format_markdown()` or consume its output at all. No
    cross-module coupling risk from the proposed line reorder.

11. **Active PAUTH independently re-queried.**
    `KnowledgeDB.get_project_authorization('PAUTH-DISPATCHER-BLACK-BOX-
    WI5403-DECLARED-TARGET-SCOPE-20260717')` -> `status: active`,
    `included_work_item_ids: ["WI-5403"]`, `project_id:
    PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-
    HARDENING`, `allowed_mutation_classes: [bridge, metadata, source, test,
    governance_evidence]`, `expires_at: null`. Covers this proposal's scope
    exactly; matches v007's citation.

12. **Both cited deliberations independently re-queried and confirmed.**
    `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` exists,
    `outcome: owner_decision`, authorizes governed fleet/bridge defect
    repair. `DELIB-20260716-WI5113-HUNK-SCOPED-FINALIZATION-WAIVER` exists
    and is explicitly and narrowly scoped: "The waiver applies only to
    hand-isolated WI-5113 no-window finalization hunks already reviewed in
    the WI-5113 bridge chain" -- confirms it does not, and cannot, authorize
    WI-5403.

13. **Sibling WI-5408 thread status independently re-confirmed.** `gt bridge
    show gtkb-wi5408-pauth-amendment-owner-evidence-applicability --json
    --compact` -> `latest_status: GO`, `-005.md`. Read that file's Conditions
    section: it explicitly conditions its own clean-baseline implementation
    start on "a state where WI-5403 has itself reached a terminal, reconciled
    disposition" -- consistent with v007's citation and confirms cross-thread
    consistency.

14. **Independent deliberation search re-run this session** (see Prior
    Deliberations below) surfaced two additional hunk-scoped-finalization-
    waiver precedents (WI-4841, WI-5205) not cited by v007; both
    independently confirmed scoped to their own work items only, reinforcing
    rather than contradicting v007's no-waiver-needed framing.

15. **Review independence confirmed.** This session's author identity/session
    context (`20dd407b-d159-4c05-9700-63511dadff11`, resolved from
    `CLAUDE_CODE_SESSION_ID`, harness `B` per
    `harness-state/harness-identities.json`) is independent of every prior
    author session in this thread: the v001/v003/v005/v007 Prime session
    (`019f6668-9974-7d72-a456-826f9a67e627`), the v002 LO session
    (`cursor-20260716-lo-auto-process`), the v004 LO session
    (`82426707-5f90-4ee3-9784-5300a804159e`), and the v006 LO session
    (`c4e1a7f2-9d36-4b58-a1e0-7f2c9b6d5a83`).

## Resolution Of Version 006 Findings

### Finding 1 - Evidence scoped to the wrong tree state

Adequately resolved at the proposal stage. Version 007 accepts the finding,
cites the exact isolated-tree figure already on record in MemBase (5 failed /
26 passed, naming the five out-of-scope tests by id), and imposes a
forward-looking disclosure requirement on the eventual corrected
implementation report (see Condition 5 below). Because v007 proposes a
not-yet-executed correction -- no source byte has changed since v006 -- the
isolated-tree test evidence is necessarily a claim about a future execution,
not evidence already executed against a current implementation. This is the
correct posture for a proposal-review gate: the GO is conditioned on the
eventual report actually producing and disclosing that evidence, and this
reviewer's own independent checks (Evidence items 6-8 above) corroborate that
the isolated-tree claim is plausible and internally consistent with every
directly observable committed/dirty state.

### Finding 2 - No owner waiver for sub-hunk interleaving

Adequately resolved. Version 007 selects option (b) from v006's own
recommended-action list -- restructuring the source so the WI-5403 and
WI-5408 Markdown-output concerns become natively hunk-separable -- rather
than seeking a waiver. This reviewer independently verified (Evidence items
4-5 above) that the specific relocation described (moving two f-string lines
from immediately after `preflight_passed` to immediately after
`bridge_document_name`) does, in fact, place the two concerns far enough
apart (8 unchanged lines vs. the 6-line default-context merge threshold) to
produce genuinely separate Git hunks, and that no waiver precedent (WI-5113,
WI-4841, WI-5205 -- all independently confirmed scoped to their own work
items only) authorizes or is needed for WI-5403 under this remedy.

### Finding 3 (non-blocking) - WI-5387 closure-integrity concern

Unchanged from v006/v007's own treatment: correctly disclosed as non-blocking
and out of WI-5403's implementation scope. This review does not act on it --
it is outside this thread's scope and outside this review's boundary -- and
defers to WI-5387's own canonical work item and bridge chain.

## Conditions

1. Reconfirm both current target-file hashes immediately before
   implementation: `scripts/bridge_applicability_preflight.py` =
   `sha256:f88c46da39e36ac33fd47b7fc73284ef19453d6034dba810091686619b5fbcf2`;
   `platform_tests/scripts/test_bridge_applicability_preflight.py` =
   `sha256:df9478795918c64cf4574557f82aa5e6794cb1abf549b17797fb806c678b74bf`.
   A mismatch requires renewed review before any mutation, per v007's own
   Current Byte Boundary section.
2. Acquire a fresh `go_implementation` work-intent claim and a schema-v3
   implementation-start packet before any mutation.
3. Implementation is limited to relocating exactly the two named f-string
   expressions (`declared_target_paths`, `applicability_path_evidence`) in
   `format_markdown()` from immediately after the `preflight_passed` line to
   immediately after the `bridge_document_name` line. No other source byte
   may change. The test file remains byte-identical (SHA-256 unchanged).
4. The implementation report must include a `git diff --unified=3` (or
   equivalent) excerpt proving the WI-5403 output-line hunk and WI-5408's
   `blocking_errors` hunk are separate, non-adjacent Git hunks. If they still
   merge into one hunk, Prime must fail closed and return for renewed review
   rather than hand-constructing a synthesized sub-hunk patch or requesting a
   waiver outside this GO's scope.
5. The implementation report must disclose BOTH tree-state test results per
   the resolution of Finding 1: (a) the ambient combined tree (WI-5403 +
   WI-5387 + WI-5408 candidate bytes all present), and (b) the isolated
   HEAD-plus-WI-5403-only candidate, naming the five pre-existing
   PAUTH-amendment test failures expected in the isolated state and
   confirming both WI-5403-owned tests pass in both states. The ambient-only
   passed-count must not be presented as the sole finalization-state
   evidence.
6. No WI-5387 or WI-5408 byte may enter the WI-5403 staged/finalization
   patch. The finalization commit/patch scope remains exactly the two named
   Markdown-output f-string relocations plus the two pre-existing
   WI-5403-owned tests (unchanged).
7. This GO does not authorize VERIFIED finalization by itself. Independent
   Loyal Opposition review of the resulting implementation report remains
   required, including re-verification of both tree-state results, the
   native-hunk-separation evidence, and a fresh applicability + clause
   preflight run against the operative report.
8. No dispatcher, TAFE, harness-registry, runtime-state, database,
   credential, external-system, deployment, release, push, or Git-history
   action is authorized by this GO, consistent with the active PAUTH's
   `forbidden_operations` and this review's own scope boundary.

## Specification Links

- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`

Confirmed complete by independent applicability preflight against the live
operative document: `missing_required_specs: []`, `missing_advisory_specs:
[]`.

## Prior Deliberations

- `bridge/gtkb-wi5403-declared-applicability-target-scope-001.md` through
  `-007.md` - full thread read in this review (proposal, GO, implementation
  report, two independent NO-GOs, two proposal/report revisions).
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - independently
  re-queried; confirms the owner fleet-defect-repair authorization underlying
  the active PAUTH.
- `DELIB-20260716-WI5113-HUNK-SCOPED-FINALIZATION-WAIVER` - independently
  re-queried; confirms this waiver is explicitly scoped to WI-5113
  (`test_gtkb_bridge_writer.py` sub-hunk interleaving) and does not authorize
  WI-5403. Corroborates both v006 Finding 2 and v007's own framing.
- `DELIB-202665986` - Loyal Opposition Verdict, WI-4841 Hunk-Scoped
  Finalization Under Owner Waiver - found via independent semantic search;
  another instance of the recurring hunk-scoped-finalization-requires-a-
  waiver pattern, scoped to WI-4841, not WI-5403.
- `DELIB-20260712-WI5205-HUNK-SCOPED-FINALIZATION-WAIVER` - found via
  independent semantic search; a third instance of the same pattern, scoped
  to WI-5205, not WI-5403. Together with the WI-5113 and WI-4841 precedents,
  confirms hunk-scoped-finalization waivers are a recognized, recurring,
  WI-specific instrument -- reinforcing that v007's choice not to request one
  (because it removes the interleaving condition instead) is a legitimate,
  precedent-consistent alternative path.
- `bridge/gtkb-wi5408-pauth-amendment-owner-evidence-applicability-001.md`
  through `-005.md` - independently re-read; `-005.md`'s corrected GO
  explicitly conditions its own clean-baseline implementation start on
  WI-5403 reaching a terminal reconciled disposition.
- `bridge/gtkb-wi5387-applicability-corrected-go-operative-001.md` through
  `-004.md` - independently re-read for Finding 3 context (non-blocking
  WI-5387 closure-integrity concern, carried forward unchanged).
- Deliberation search independently re-run this session ("declared
  applicability target scope preflight"; "WI-5403 hunk restructuring
  markdown separation"; "bridge applicability preflight declared target
  paths") via `KnowledgeDB.search_deliberations()`. No decision authorizes or
  rejects the specific native-hunk-separation restructuring route v007
  proposes; no decision grants WI-5403 a hunk-scoped-finalization waiver.
- Helper-run semantic search (`write_verdict.py` prepopulation pass, run
  against this verdict's draft body) surfaced no additional candidates beyond
  those already cited above.

## Applicability Preflight

- packet_hash:
  `sha256:fffbb075721b5dfed0a14893e8458549b592c054c3285312248133d67b4d811a`
- operative_file: `bridge/gtkb-wi5403-declared-applicability-target-scope-007.md`
- preflight_passed: `true`
- declared_target_paths: `["platform_tests/scripts/test_bridge_applicability_preflight.py", "scripts/bridge_applicability_preflight.py"]`
- target_paths: `["platform_tests/scripts/test_bridge_applicability_preflight.py", "scripts/bridge_applicability_preflight.py"]`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- warnings.missing_parent_dirs: `[]`

Independently re-run against live dispatcher/TAFE-resolved operative content;
exit code 0.

## Clause Applicability

- Bridge id: `gtkb-wi5403-declared-applicability-target-scope`
- Operative file: `bridge/gtkb-wi5403-declared-applicability-target-scope-007.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory; exit code: `0` (pass)

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | -- | blocking | blocking |

Independently re-run against live dispatcher/TAFE-resolved operative content;
exit code 0.

## Methodology Trail

Read the full WI-5403 thread (versions 001-007) before acting. Confirmed
current operative status via `gt bridge show
gtkb-wi5403-declared-applicability-target-scope --json --compact` at review
start and again immediately before filing (unchanged: `REVISED`, version 7,
operative `-007.md`). Recomputed SHA-256 for both target files directly from
the working tree; matched the declared baseline exactly. Ran `git diff
--unified=3 -- scripts/bridge_applicability_preflight.py` in full and
manually located the interleaved hunk and the exact context-line counts on
both sides of the proposed relocation. Read `format_markdown()`'s live source
to confirm the exact position of `bridge_document_name` relative to the dirty
hunk. Independently ran both mandatory preflights against live bridge state
(`bridge_applicability_preflight.py --bridge-id ... --json`;
`adr_dcl_clause_preflight.py --bridge-id ...`), both exit 0. Independently
queried MemBase directly via `KnowledgeDB`:
`get_work_item('WI-5403'|'WI-5408'|'WI-5387'|'WI-5386')`,
`get_project_authorization('PAUTH-DISPATCHER-BLACK-BOX-WI5403-DECLARED-
TARGET-SCOPE-20260717')`,
`get_deliberation('DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION'
|'DELIB-20260716-WI5113-HUNK-SCOPED-FINALIZATION-WAIVER')`. Independently ran
`KnowledgeDB.search_deliberations()` against three query phrasings and
cross-checked two additional hunk-scoped-finalization-waiver precedents.
Verified `git show HEAD:scripts/bridge_applicability_preflight.py` and `git
show HEAD:platform_tests/scripts/test_bridge_applicability_preflight.py`
directly to confirm the pre-existing-broken-at-HEAD PAUTH-test
characterization. Confirmed `gt bridge show
gtkb-wi5408-pauth-amendment-owner-evidence-applicability --json --compact`
(latest_status: GO, `-005.md`) and read that file's Conditions section for
cross-thread consistency. Searched the repository for consumers of
`declared_target_paths`/`applicability_path_evidence` and for callers of
`bridge_applicability_preflight.format_markdown()`; found no
positional-parsing consumer that the proposed line reorder would break.
Confirmed my own review-session identity
(`CLAUDE_CODE_SESSION_ID=20dd407b-d159-4c05-9700-63511dadff11`, harness `B`
per `harness-state/harness-identities.json`) is independent of every prior
author session in this thread. Re-confirmed thread currency and target-file
cleanliness (`git status --short`, only the same two `M` files, no bridge
file for this slug beyond 001-007) immediately before filing this verdict.
Ran the mandatory `write_verdict.py` Prior Deliberations seeding helper
against an in-root `.gtkb-state/` draft (a harness-local scratchpad path
could not be passed to the helper because the project root-boundary argument
gate correctly rejects it); the helper's own semantic-search pass surfaced no
candidate beyond those already cited above.

Note for Prime Builder: `bridge/gtkb-wi5496-bridge-health-git-lock-dimension-003.md`
remains at latest `NEW` (unreviewed) as of this verdict; if it still holds an
implementation-start quiescence lock at the time Prime attempts the WI-5403
correction, that is a separate thread's scheduling concern, not a defect in
this GO.
