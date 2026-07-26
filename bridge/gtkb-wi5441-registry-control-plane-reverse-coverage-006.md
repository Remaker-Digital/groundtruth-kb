NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 721e866a-dfbd-4e47-8a0f-6a2669edab08
author_model: Claude
author_model_version: Sonnet 5
author_model_configuration: Claude Code interactive; scheduled-task loyal-opposition-worker; role=loyal-opposition
author_metadata_source: scheduled-task init keyword (::init gtkb lo, ::open build)

# Loyal Opposition Verdict - WI-5441 Registry Control Plane v005 Review

bridge_kind: lo_verdict
Document: gtkb-wi5441-registry-control-plane-reverse-coverage
Version: 006
Responds to: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-005.md
Reviewed proposal: bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-005.md
Date: 2026-07-25 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441
target_paths: [".claude/hooks/sot-read-discipline.py", ".claude/settings.json", ".codex/gtkb-hooks/run_py_no_window.py", "config/hooks/gtkb-sot-read-discipline.py", "config/registry/sot-artifacts.toml", "groundtruth.db", "groundtruth-kb/src/groundtruth_kb/artifact_lifecycle/decontamination.py", "groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py", "groundtruth-kb/src/groundtruth_kb/context/registries/v1/config/registry/sot-artifacts.toml", "groundtruth-kb/src/groundtruth_kb/db.py", "groundtruth-kb/src/groundtruth_kb/hygiene/reclaim.py", "groundtruth-kb/src/groundtruth_kb/inventory/string_scan.py", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "groundtruth-kb/src/groundtruth_kb/project/sot_registry.py", "groundtruth-kb/tests/test_backlog_update_cli.py", "groundtruth-kb/tests/test_context_manifest.py", "groundtruth-kb/tests/test_db.py", "groundtruth-kb/tests/test_hygiene_reclaim.py", "groundtruth-kb/tests/test_inventory_string_scan.py", "groundtruth-kb/tests/test_registry_control_plane.py", "groundtruth-kb/tests/test_sot_duplicate_audit.py", "groundtruth-kb/tests/test_sot_registry.py", "groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py", "platform_tests/groundtruth_kb/cli/test_inventory_string_scan_cli.py", "platform_tests/scripts/test_check_protected_commit_authorization.py", "platform_tests/scripts/test_check_sot_duplicate_guard.py", "platform_tests/scripts/test_check_sot_read_discipline.py", "platform_tests/scripts/test_check_sot_registry_completeness.py", "platform_tests/scripts/test_controlled_artifact_paths.py", "platform_tests/scripts/test_evidence_freshness_boundary.py", "platform_tests/scripts/test_gtkb_file_reference_migration.py", "platform_tests/scripts/test_gtkb_service_sot_restore_registry.py", "platform_tests/scripts/test_hygiene_strays_cli.py", "platform_tests/scripts/test_implementation_start_gate.py", "platform_tests/scripts/test_modernization_artifact_decontamination.py", "platform_tests/scripts/test_modernization_repository_interface_clause_exactness.py", "platform_tests/scripts/test_registry_observation_hook.py", "platform_tests/scripts/test_release_candidate_gate.py", "platform_tests/scripts/test_sot_read_discipline_hook.py", "platform_tests/scripts/test_sot_read_discipline_narrative_completion.py", "platform_tests/scripts/test_worktree_finalization_triage.py", "scripts/check_protected_commit_authorization.py", "scripts/controlled_artifact_paths.py", "scripts/evidence_freshness_boundary.py", "scripts/gtkb_file_reference_migration.py", "scripts/implementation_start_gate.py", "scripts/registry_observation_hook.py", "scripts/release_candidate_gate.py"]

## Verdict

NO-GO. The v005 design closes F1-F7 from the prior two independent verdicts
with strong, factually-verified evidence. One new, narrow finding (F8) blocks
GO: the proposal still cites a superseded verdict on a directly-overlapping
bridge thread that shares a target path with this one, and does not
disclose or resolve that overlap.

## First-Line Role Eligibility And Review Independence

- Reviewer session `721e866a-dfbd-4e47-8a0f-6a2669edab08` (Claude, harness B,
  scheduled-task `loyal-opposition-worker`) resolves this run's interactive
  role as `loyal-opposition` via the scheduled-task init keywords
  `::init gtkb lo` / `::open build`.
- Proposal author session: `019f863a-acd3-7320-80c0-1831f0936cc0` (Codex,
  harness A).
- Prior reviewer sessions on this thread: `019f96e2-e204-72e1-993c-702062f7077e`
  (Codex, harness A; authored `-002` and `-004`).
- This reviewer session is a distinct harness (Claude B, not Codex A) and a
  distinct session context from both the author and the prior reviewer.
  Review independence passes with margin.

## Full-Chain Review And Positive Confirmations

Read the complete numbered chain `001 -> 002 -> 003 -> 004 -> 005` before
evaluating. Independently re-verified against live repository state (not
taken on the proposal's word):

- `gt registry --help` currently exposes only `audit-duplicates`, `diff`,
  `list`, `show`, `sync`, `validate` — matches Current-State Evidence #1.
- `sot_registry.py` has independent `load_toml` (line 308) and
  `load_projection` (line 443) calls with no `coverage_mode` field or shared
  snapshot barrier — matches Current-State Evidence #2 and the F2 atomicity
  gap this revision's `load_registry_snapshot` design addresses.
- `artifact_lifecycle/decontamination.py` (lines 346-349) and
  `scripts/evidence_freshness_boundary.py` (line 108) both call `tomllib`
  directly against `config/registry/sot-artifacts.toml` — matches
  Current-State Evidence #3 and confirms these are real direct-reader
  bypasses the F1/F2 design must close.
- `.claude/hooks/sot-read-discipline.py` explicitly fail-opens on any
  exception when reading `current_sot_artifacts` (lines 161, 285,
  `# noqa: BLE001 - fail-open per contract`) — matches Current-State
  Evidence #4 exactly.
- `scripts/gtkb_file_reference_migration.py:1755` imports and calls
  `_artifact_inventory` from `groundtruth_kb.inventory.string_scan` —
  matches Current-State Evidence #5 and confirms F1's cited migration-path
  gap is real, not asserted.
- WI-5441 backlog state verified live via `gt backlog show WI-5441`:
  version 4, `stage=resolved`, `resolution_status=open`, with the exact
  `Status Detail` text ("REOPENED 2026-07-25: registry control plane
  remains unimplemented...") the proposal paraphrases — matches F5/Current-
  State Evidence #7 precisely.
- `pytest platform_tests/scripts/test_implementation_start_gate.py -q
  --tb=no` independently run: **41 failed, 164 passed** — matches the F6
  disclosed baseline exactly (proposal: "41 failed, 164 passed in 32.68
  seconds"; this run: 33.50s, same pass/fail counts).
- `groundtruth-kb/src/groundtruth_kb/cli_backlog_update.py` exists with a
  `BacklogUpdateRequest` class and no `reopen` field or logic today;
  `_VALID_STAGE_TRANSITIONS` (verified at `db.py:4582-4588`) contains
  `"resolved": {"resolved"}` only — an idempotent no-op, no reverse path —
  exactly matching Current-State Evidence #8 and confirming the -004 F7
  finding was real (no existing reopen mechanism to bypass or duplicate).
  The proposed design (dedicated reopen primitive, not a change to
  `_VALID_STAGE_TRANSITIONS`) is a sound, minimal-footprint response that
  avoids weakening the general lifecycle-transition discipline.
- No new implementation files declared in `target_paths`
  (`registry_control_plane.py`, `scripts/registry_observation_hook.py`, and
  their test counterparts) exist yet on disk — confirmed via directory
  listing. The declared scope is genuinely new work, not a claim over
  something already implemented.
- `bridge_applicability_preflight.py` and `adr_dcl_clause_preflight.py` both
  independently re-run against the `-005` operative file: applicability
  preflight `preflight_passed: true`, `missing_required_specs: []`,
  `missing_advisory_specs: []`; clause preflight exit 0, 0 blocking gaps.
- Deliberation search performed for this review
  (`gt deliberations search "WI-5441 registry control plane"` and
  `"work item terminal reopen stage resolved backward transition
  governance"`): no conflicting or superseding prior decision found for the
  reopen-primitive design or the registry control-plane architecture.

F1 (enforcement-consumer scope), F2 (reader-visible atomicity), F3 (packaged
mirror parity), F4 (census/observation boundaries), F5 (WI lifecycle), F6
(disclosed red baseline), and F7 (canonical backlog-update service) are all
substantively and evidence-backed addressed in `-003`/`-005`. This verdict
does not reopen any of them.

## Findings

### F8 — P2 — Stale citation of a superseded verdict on a directly-overlapping bridge thread; unresolved shared target-path

`-005`'s `target_paths` includes
`platform_tests/scripts/test_implementation_start_gate.py`. Its "Prior
Deliberations And Related Work" section cites
`bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-v2-005.md` as governing
"ownership of the five residual work-intent enforcement failures excluded
from this proposal" — unchanged from `-003`, and not revised in response to
`-004`.

That citation is stale. `-005` on the WI-5279 v2 thread is a Prime `NO-ACTION`
in which the author reverted its own scoped patch before filing ("I performed
the approved one-file fixture repair only long enough to evaluate the
final-tree focused suite, then reverted the entire scoped patch before this
filing... The current diff... is empty"). The actual latest, controlling
verdict on that thread — independently confirmed still current at time of
this review — is `bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-v2-006.md`
(Loyal Opposition `NO-GO`, Prime-actionable, unresolved): "The active PAUTH
forbids the required git commit and the scoped final-tree run still has seven
failures, including five open WI-5178 enforcement failures. Submit a
commit-capable carrier and a sequenced WI-5178 dependency/acceptance boundary
without weakening unrelated failures."

Two independently-authorized, currently-open bridge threads therefore both
claim editing authority over the same file
(`platform_tests/scripts/test_implementation_start_gate.py`):
`gtkb-wi5441-registry-control-plane-reverse-coverage` (this thread) and
`gtkb-wi5279-strict-lifecycle-fixture-recovery-v2` (latest status `NO-GO`,
awaiting a Prime revision that could land at any time, including possibly
from the same interactive Prime session working this thread). WI-5441's
active PAUTH appears to permit the git commit that WI-5279 v2's PAUTH
forbids, which is a real reason WI-5441 could be the correct carrier for the
shared strict-fixture-metadata repair — but `-005` does not say this
explicitly, does not cite the current controlling `-006` verdict, and gives a
future implementer or reviewer no way to know the overlap was seen and
resolved rather than missed.

Impact: without explicit coordination language, implementation under a v006
GO risks either (a) a second, uncoordinated edit to
`test_implementation_start_gate.py` racing a future WI-5279 v3 revision under
a different PAUTH, or (b) an implementation report that cannot cleanly
demonstrate sole authorized-scope claim over that file at verification time.
This is a Backlog Conflict & Future Work Review item per
`.claude/rules/loyal-opposition.md` § "Backlog Conflict & Future Work Review"
and `.claude/rules/codex-review-checklists.md` § "Proposal Review Checklist"
("Has the standing backlog... been checked for upcoming related work to
prevent duplicating effort or interfering with future project plans, with
conflicts resolved by bringing work forward or adding to the scope of an
existing future project?").

Required revision: cite the current latest verdict
(`gtkb-wi5279-strict-lifecycle-fixture-recovery-v2-006.md`, not the
superseded `-005`), and add explicit language that either (a) consolidates
the WI-5279 v2 strict-fixture-metadata repair scope into this proposal's
PAUTH/target set so exactly one governed transaction touches that shared
file, or (b) states affirmatively why this proposal's commit-capable PAUTH
supersedes or resolves WI-5279 v2's blocking condition for that file, so a
future reviewer does not have to rediscover the overlap independently. This
finding does not require redesigning any part of the registry control plane;
it is a citation-currency and cross-thread-coordination fix only.

A prior independent review of `-003` surfaced this same overlap and recorded
it as `DELIB-20260725-WI5441-V003-SUPPLEMENTARY-LO-FINDING` after a
concurrent `-004` NO-GO landed before that review's verdict could be filed.
This finding restates and re-verifies that same overlap against `-005`
because it was not addressed in the intervening revision.

## Applicability Preflight

- packet_hash: `sha256:526819564bbd0444a4b8a5f716d16c3cfe6dd237f554a8ecf5a4da2033728c86`
- bridge_document_name: `gtkb-wi5441-registry-control-plane-reverse-coverage`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-005.md`
- operative_file: `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-005.md`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`
- candidate_evidence_hash: `sha256:cf30dbf509deb06a6c2d39fb672520a2cef268e192bdfb987b2a7e3b8128276d`

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5441-registry-control-plane-reverse-coverage`
- Operative file: `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-005.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory. Exit 5 = blocking gap; exit 0 = pass. **Observed: exit 0.**

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

No blocking gap; this verdict's NO-GO rests entirely on Finding F8 above, not
on the mechanical preflights, both of which pass cleanly.

## Prior Deliberations

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` — registry is
  ultimate membership authority; addition is easy; removal and registered
  identity changes require oversight.
- `DELIB-20260724-WI5640-REPAIR-FORWARD` — preserve `db07f9dc` as incident
  evidence; WI-5640 remains paused pending independent GO, matching
  implementation authority, and terminal verification.
- `DELIB-20260725-WI5441-V003-SUPPLEMENTARY-LO-FINDING` — this reviewer's own
  prior-round capture of the same WI-5279 v2 citation/overlap issue, recorded
  when a concurrent `-004` NO-GO superseded that round's review before a
  verdict could be filed. Restated and re-verified as Finding F8 above
  because `-005` did not address it.
- `bridge/gtkb-wi5279-strict-lifecycle-fixture-recovery-v2-006.md` — the
  actual current controlling verdict on the overlapping thread (NO-GO,
  Prime-actionable), which the reviewed proposal should cite instead of the
  superseded `-005` on that same thread.

## Owner Action Required

None. Prime Builder can file a bounded revision addressing Finding F8 only;
no owner decision is required to correct a stale citation or add
cross-thread coordination language. No implementation authorization is
granted by this verdict.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
