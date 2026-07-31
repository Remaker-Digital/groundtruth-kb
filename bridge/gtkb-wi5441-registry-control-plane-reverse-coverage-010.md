NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 7ae5b0ad-3cdf-4d13-b503-bcf4cf126c6d
author_model: Claude
author_model_version: Sonnet 5
author_model_configuration: Claude Code interactive; scheduled-task loyal-opposition-worker; role=loyal-opposition
author_metadata_source: scheduled-task init keyword (::init gtkb lo, ::open build)

# Loyal Opposition Verdict - WI-5441 Registry Control Plane v009 Verification

bridge_kind: lo_verdict
Document: gtkb-wi5441-registry-control-plane-reverse-coverage
Version: 010
Responds to: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-009.md
Reviewed implementation report: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-009.md
Approved proposal: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-007.md
Prior GO: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-008.md
Date: 2026-07-25 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: [".claude/hooks/sot-read-discipline.py", ".claude/settings.json", ".codex/gtkb-hooks/run_py_no_window.py", "config/hooks/gtkb-sot-read-discipline.py", "config/registry/sot-artifacts.toml", "groundtruth.db", "groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py", "groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/tests/test_backlog_update_cli.py", "groundtruth-kb/tests/test_context_manifest.py", "groundtruth-kb/tests/test_db.py", "groundtruth-kb/tests/test_hygiene_reclaim.py", "groundtruth-kb/tests/test_inventory_string_scan.py", "groundtruth-kb/tests/test_registry_control_plane.py", "groundtruth-kb/tests/test_sot_duplicate_audit.py", "groundtruth-kb/tests/test_sot_registry.py", "groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py", "platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", "platform_tests/scripts/test_check_sot_duplicate_guard.py", "platform_tests/scripts/test_check_sot_read_discipline.py", "platform_tests/scripts/test_check_sot_registry_completeness.py", "platform_tests/scripts/test_controlled_artifact_paths.py", "platform_tests/scripts/test_evidence_freshness_boundary.py", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "platform_tests/scripts/test_gtkb_service_sot_restore_registry.py", "platform_tests/scripts/test_hygiene_strays_cli.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_modernization_artifact_decontamination.py", "platform_tests/scripts/test_modernization_repository_interface_clause_exactness.py", "platform_tests/scripts/test_registry_observation_hook.py", "platform_tests/scripts/test_release_candidate_gate.py", "platform_tests/scripts/test_sot_read_discipline_hook.py", "platform_tests/scripts/test_sot_read_discipline_narrative_completion.py", "platform_tests/scripts/test_worktree_finalization_triage.py", "scripts/check_protected_commit_authorization.py", "scripts/controlled_artifact_paths.py", "scripts/evidence_freshness_boundary.py", "scripts/gtkb_file_reference_migration.py", "scripts/implementation_start_gate.py", "scripts/registry_observation_hook.py", "scripts/release_candidate_gate.py"]

## Verdict

NO-GO. The underlying registry-control-plane implementation is substantively
sound and I independently re-verified nearly every material claim in the
report (see "Independent Verification Evidence" below) - every check matched
the report's stated numbers exactly. This is not a rejection of the
engineering work. It is blocked on two findings: one is a genuine hazard in
how this report is positioned for the mandatory commit-finalization gate
(F1, blocking), and one is an unaddressed coordination gap versus a sibling
bridge thread this report's own safeguard was supposed to catch (F2, must be
disclosed/resolved before VERIFIED).

## First-Line Role Eligibility And Review Independence

- Reviewer session `7ae5b0ad-3cdf-4d13-b503-bcf4cf126c6d` (Claude, harness B,
  scheduled-task `loyal-opposition-worker`) resolves this run's interactive
  role as `loyal-opposition` via `::init gtkb lo` / `::open build` (confirmed
  against `.claude/session/envelope.json`: `role_resolved: loyal-opposition`).
- Report/proposal author session: `019f863a-acd3-7320-80c0-1831f0936cc0`
  (Codex, harness A) - distinct harness and distinct session from this
  reviewer.
- The prior `-008` GO was authored by a different Claude/harness-B session
  (`721e866a-dfbd-4e47-8a0f-6a2669edab08`), also distinct from this reviewer
  session. Review independence passes with margin for both the proposal
  author and the prior reviewer.

## Findings

### F1 (P1, blocking) - `groundtruth.db` cannot be safely included in the mandatory VERIFIED finalization commit as currently claimed

**Claim under review:** The report's `## Files Changed` section lists
`groundtruth.db (projection, journal, revisions, WI/event/backlog evidence)`
as a changed artifact of this implementation, on equal footing with the other
32 source/test/config paths.

**Evidence:**

- `groundtruth.db` is 736 MB on disk (`du -h groundtruth.db` = `736M`).
- `git ls-files --error-unmatch -- groundtruth.db` fails
  (`did not match any file(s) known to git`) - it is **not currently git
  tracked**.
- `git check-ignore -v groundtruth.db` returns `.gitignore:180:groundtruth.db
  groundtruth.db` - it is **explicitly git-ignored**.
- `git log --oneline -1 -- groundtruth.db` resolves to commit `7c033d11c
  chore(git): untrack groundtruth.db from the index to stop object-store
  bloat (WI-5431)` - the database was **deliberately removed from git
  tracking** to fix a prior object-store bloat defect, and that commit is
  the immediately-preceding commit on `research` per the session's git log.
- The mandatory `VERIFIED` finalization path is
  `.claude/skills/gtkb-verify/helpers/write_verdict.py --finalize-verified`
  per `.claude/rules/file-bridge-protocol.md` "Mandatory VERIFIED
  Commit-Finalization Gate" and `.claude/rules/loyal-opposition.md`
  "VERIFIED Commit Finalization" - LO must use this helper and cannot record
  `VERIFIED` any other way.
- That helper's `_assert_include_set_covers_report_claims` (write_verdict.py
  lines 417-443) parses the latest implementation report's `## Files
  Changed` section and **requires every claimed path to appear in
  `--include`**, raising `VerifiedFinalizationError` otherwise. Line 381
  explicitly special-cases `groundtruth.db` as an always-recognized claimed
  path regardless of extension-pattern matching
  (`or raw in {"pyproject.toml", "groundtruth.toml", "groundtruth.db"}`), so
  this is not an incidental parser miss - the helper is designed to treat a
  literal `groundtruth.db` mention as claimed.
- Included paths not covered by a `--hunk-patch` are staged via
  `git add -f -- <path>` (write_verdict.py line ~1196) - the `-f`/`--force`
  flag **overrides `.gitignore`**.
- The report's `## Owner Decisions / Input` and body contain no
  "By-Reference Finalization Waiver" / "Finalization Waiver" language (the
  helper's only recognized escape hatch per `_report_has_by_reference_finalization_waiver`,
  lines 405-414, which requires "by-reference" + "waiver" +
  ("owner" or "delib-") together) - so no waiver currently exempts this
  claim.

**Risk/impact:** As the report is currently written, Loyal Opposition cannot
run the mandatory finalization helper without either (a) force-adding a
736 MB SQLite database back into git history - directly reversing the
WI-5431 object-store-bloat fix that was committed one commit prior on this
same branch - or (b) hitting a hard `VerifiedFinalizationError` because a
claimed path is missing from `--include`. Neither outcome is acceptable, and
there is no currently-valid way to record `VERIFIED` for this report through
the governed path.

**Recommended action:** Revise `## Files Changed` (or add an explicit
per-clause `## By-Reference Finalization Waiver` section citing an owner
decision, if the intent is genuinely to keep `groundtruth.db` out of the git
commit while still counting its mutation as verified evidence) so that
`groundtruth.db` is cited as evidence via its already-recorded digests/receipts
in `## Registry Transaction Evidence` (declaration digest, projection digest,
receipt digest, bootstrap journal ID - all independently re-derivable via
`gt registry inspect --no-census --json`, which I ran and which matches the
report's cited digests exactly) rather than listed as a path destined for
`--include`/commit inclusion. This is a report-authoring correction, not a
re-implementation; no source/test change is implicated by this finding.

### F2 (P2, must be disclosed/resolved before VERIFIED) - the proposal's own cross-thread coordination safeguard did not check a sibling WI-5279 bridge thread with a live, un-dispositioned `GO`

**Claim under review:** `-007`'s "Cross-Thread Coordination And Consolidation"
section and `-009`'s "Shared-File Hunk Inventory" both state that WI-5441 is
"the sole implementation carrier" for the shared
`platform_tests/scripts/test_implementation_start_gate.py` hunks, and that
the only relevant WI-5279 state is
`bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-v2-006.md` (latest
NO-GO, unclaimed).

**Evidence:**

- `gt bridge threads --wi WI-5279 --json` returns **three** distinct WI-5279
  threads, not one: `gtkb-wi5279-project-authorization-bootstrap-lifecycle`
  (latest NO-GO), `gtkb-wi5279-strict-lifecycle-fixture-recovery-v2` (latest
  NO-GO at `-006`, the thread this proposal/report cites), and
  `gtkb-wi5279-strict-lifecycle-fixture-recovery` (**no `-v2` suffix** -
  latest status **GO** at `-004`).
- `bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-004.md` is a live,
  independently-authored LO `GO` (author `loyal-opposition/codex`, harness A,
  session `A-2026-07-24T15-42-00Z`, dated 2026-07-24) targeting exactly
  `platform_tests/scripts/test_implementation_start_gate.py` for exactly the
  same defect class this proposal absorbed: repairing
  `_proposal()`, `_go_verdict_body()`, `_write_implementation_report()`, the
  direct deferred fixture, and `_write_verified_thread()` to emit strict
  numbered-bridge lifecycle metadata. This is a **different bridge thread**
  from the `-v2` thread, not a duplicate name for it.
- `grep` for `gtkb-wi5279-strict-lifecycle-fixture-recovery` (base slug
  without the `-v2` suffix) against `-007` returns **zero matches** - this
  non-`-v2` thread is never mentioned anywhere in the reviewed proposal or
  report chain.
- `ls .gtkb-state/work-intent/` finds no such directory at all - there is no
  live claim on either WI-5279 thread, consistent with the report's
  unclaimed-ness claim for the `-v2` thread, but this also confirms the
  non-`-v2` thread's `GO` is equally unclaimed and therefore equally
  actionable by a future Prime Builder session or the dispatcher (which
  currently shows `codex:A` as a dispatchable Prime Builder target).
- I independently re-ran the full
  `platform_tests/scripts/test_implementation_start_gate.py` module against
  the current working tree: `206 passed, 4 failed` (same four WI-5178-scoped
  node IDs the report names). This confirms the strict-lifecycle-fixture
  repair that the non-`-v2` thread's `GO` would have authorized has **already
  been performed** - by this WI-5441 transaction, under the `-v2` thread's
  guidance, with no acknowledgment that a second, un-consulted `GO`
  authorized (and remains open to authorize) the identical repair on the
  identical file.

**Risk/impact:** `gtkb-wi5279-strict-lifecycle-fixture-recovery` (non-`-v2`)
carries a live, Prime-actionable `GO` on a file this transaction has already
mutated and (pending resolution of F1) is about to commit. If a future Prime
Builder session or the dispatcher picks up that `GO` - nothing currently
prevents this, since it is unclaimed and un-superseded - it would attempt to
"repair" a file whose fixture producers no longer match the `GO`'s original
baseline (`41 failed, 164 passed` at commit `c0c4c40e`), very likely
producing a conflicting diff, wasted implementation work, or confusion about
which of two same-named-work threads is authoritative. This is precisely the
failure mode the proposal's own "Cross-Thread Coordination And
Consolidation" section and pre-mutation check were designed to prevent; the
safeguard checked the wrong (or an incomplete) set of WI-5279 threads.

**Recommended action:** Before (or as part of) the next revision, Prime
Builder must either (a) formally close/withdraw
`gtkb-wi5279-strict-lifecycle-fixture-recovery` (non-`-v2`) citing this
VERIFIED-pending WI-5441 evidence as the reason the repair is already done,
or (b) demonstrate why that thread's live `GO` does not in fact create a
conflicting authorization. Per the Loyal Opposition "Backlog Conflict &
Future Work Review" duty and the strategic self-improvement directive, this
should also be captured as a standing-backlog follow-up so it is not lost if
the next revision does not fully resolve it.

## Independent Verification Evidence (methodology trail)

All of the following were run independently by this reviewer against the
current working tree (not taken from the report's assertions):

- `git status --short` matches the report's `## Files Changed` list exactly
  (all 30 tracked-path modifications plus 4 new untracked files; the 9
  untracked `bridge/gtkb-wi5441-*-00{1..9}.md` chain files are also present
  and unaccounted for in any commit).
- All four new files exist on disk with substantive content:
  `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py`
  (80,395 bytes), `groundtruth-kb/tests/test_registry_control_plane.py`
  (17,843 bytes), `scripts/registry_observation_hook.py` (5,533 bytes,
  executable), `platform_tests/scripts/test_registry_observation_hook.py`
  (6,034 bytes).
- WI-5441 KB state: `version=6`, `stage=implementing`,
  `resolution_status=in_progress`, `change_reason` cites this exact `-008`
  GO - matches the report's lifecycle-repair claim exactly.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5441-registry-control-plane-reverse-coverage`
  against the `-009` operative file: `preflight_passed: true`,
  `missing_required_specs: []` (two advisory-only specs unmatched:
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
  - non-blocking, noted for completeness).
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5441-registry-control-plane-reverse-coverage`:
  exit `0`, 0 blocking gaps, 3 must_apply clauses all with evidence found.
- `groundtruth-kb/tests/test_registry_control_plane.py` -> **17 passed**
  (report claimed 17 passed).
- `groundtruth-kb/tests/test_sot_registry.py` -> **19 passed** (report
  claimed 19 passed).
- `platform_tests/scripts/test_registry_observation_hook.py` -> **7 passed**
  (consistent with report's combined 76-passed pre-bootstrap figure).
- `platform_tests/scripts/test_implementation_start_gate.py` (full module)
  -> **206 passed, 4 failed**, exact same four node IDs
  (`test_work_intent_acquire_denial_creates_no_claim`,
  `test_work_intent_extension_denial_leaves_claim_unchanged`,
  `test_work_intent_renew_denial_leaves_go_claim_unchanged`,
  `test_work_intent_reclassify_denial_leaves_draft_claim_unchanged`), all
  attributable to the out-of-scope WI-5178
  `scripts/bridge_work_intent_registry.py` surface - matches the report
  exactly.
- `groundtruth-kb/tests/test_context_manifest.py` -> 1 failed, 13 passed;
  the one failure (`test_packaged_v1_snapshot_matches_source_checkout_registry_inputs`,
  diverging on `config/agent-control/activity-disposition-profiles.toml`) is
  confirmed pre-existing/unrelated - that file is not among WI-5441's
  32 touched paths.
- `ruff check` on the 18 changed Python paths sampled - **all checks
  passed** (the `.claude/settings.json` false-positive `B018` finding from
  my first attempt was my own testing artifact from linting a JSON file as
  Python, not a real defect; the report separately and correctly validated
  `.claude/settings.json` via `python -m json.tool`).
- `ruff format --check` on the four new files -> **4 files already
  formatted**.
- `git diff --check` -> exit 0, only benign LF/CRLF conversion warnings (no
  conflict markers, no trailing whitespace defects).
- `gt registry inspect --no-census --json` -> `coherent: true`,
  `record_count: 54`, `declaration_digest`, `projection_digest`, and
  `packaged_digest` all byte-for-byte match the digests cited in the
  report's "Registry Transaction Evidence" section. One informational,
  non-blocking observation: `currentness.current: false` with one stale
  entry (`bridge-versioned-files`) - this reflects normal, expected drift
  from new bridge files (including this very verdict) being added since the
  report's own last observation of that virtual/opaque-container entry, not
  a coherence defect (`coherent: true` is the load-bearing signal for
  split-brain/partial-transaction safety, and it holds).
- Direct-reader-retirement claim: searched
  `groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py`,
  `scripts/evidence_freshness_boundary.py`, and
  `.claude/hooks/sot-read-discipline.py` for `current_sot_artifacts` ->
  **zero matches** in all three - confirms these named consumers no longer
  query the projection table directly.
- Required deliberation search performed via
  `groundtruth_kb deliberations search "registry control plane reverse
  coverage WI-5441"` (see `## Prior Deliberations` below for citations
  surfaced).

## Applicability Preflight

- packet_hash: `sha256:9ac212b941b74c0716fb3448d30a2682bec1c028c54180280eb9ed41fc3a7bbe`
- candidate_evidence_hash: `sha256:247634fb65c82000ae72407923cc2098beb6ae86d5f8dc97c6af9b773cce2679`
- bridge_document_name: `gtkb-wi5441-registry-control-plane-reverse-coverage`
- content_source: `bridge_file_operative`
- operative_file: `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-009.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]`
- blocking_errors: `[]`

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5441-registry-control-plane-reverse-coverage`
- Operative file: `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-009.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass. **Observed: exit 0.**

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | - | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

## Prior Deliberations

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - registry
  is ultimate membership authority; addition is easy; removal and registered
  identity changes require oversight. Directly relevant to F1: it does not
  authorize re-adding a deliberately untracked artifact to git as a side
  effect of registry-transaction evidence citation.
- `DELIB-20260724-WI5640-REPAIR-FORWARD` - WI-5640 remains paused pending
  independent GO, matching implementation authority, and terminal
  verification; unaffected by this NO-GO.
- `DELIB-20260725-WI5441-V003-SUPPLEMENTARY-LO-FINDING` - this reviewer
  chain's own prior capture of a WI-5279 citation/overlap issue on the
  `-v2` thread; F2 in this verdict identifies a related but distinct gap
  (a second, un-consulted WI-5279 thread), not a re-litigation of the
  already-resolved `-v2` citation issue.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-006.md` and
  `-008.md` - prior NO-GO/GO on this thread; the F1/F2 findings in this
  verdict are new (not previously raised) and specific to the `-009`
  implementation report's finalization readiness, not the `-007` proposal's
  design.
- `bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-004.md` and `-001.md`
  - the sibling WI-5279 thread identified in F2; cited directly above with
  full evidence.

## Scope And Revision Notes For Prime Builder

- No re-implementation is required. F1 is a report-authoring correction
  (fix how `groundtruth.db` is cited/excluded from the commit-inclusion
  claim); F2 is a bridge-hygiene disposition on a sibling thread, not a
  change to WI-5441's own source/test scope.
- Do not attempt `--finalize-verified` with `groundtruth.db` in `--include`
  under any circumstance; that would force-add a 736 MB gitignored database
  and reverse the WI-5431 fix.
- This GO'd proposal (`-007`/`-008`) and its `target_paths` remain
  otherwise sound; no new specification, target-path, or design change is
  required to close F1 or F2.

## Owner Action Required

None. Both findings are resolvable by Prime Builder revision (report
correction + a bridge-hygiene disposition on the sibling WI-5279 thread)
without a new owner decision.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
