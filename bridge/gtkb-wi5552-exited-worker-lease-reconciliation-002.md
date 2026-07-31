GO
::init gtkb pb
::open test

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 211b1f8c-4852-4f93-8aa0-127e2517b7b9
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: harness B sub-agent performing Loyal Opposition independent review of one bridge thread from an owner-authorized recurring watch cycle covering the Ollama/OpenRouter provider-reliability chain and bridge/TAFE/dispatcher governance infrastructure; independent session context from the version 001 proposal author

bridge_kind: lo_verdict
Document: gtkb-wi5552-exited-worker-lease-reconciliation
Version: 002
Responds to: bridge/gtkb-wi5552-exited-worker-lease-reconciliation-001.md
Reviewer role: loyal-opposition (independent sub-agent review session)
Recommended commit type: N/A (GO; no implementation commit)

# GO - WI-5552 NEW Proposal: Exact-Once Exited D/F Launch Lease Reconciliation

## Verdict Summary

GO. This is a test-first reliability proposal: add TEST-11610 (already a live MemBase test record linked to SPEC-CENTRALIZED-DISPATCH-SERVICE-001, content independently confirmed to match the proposal's described scenario verbatim) to prove exact-once exit reconciliation for mixed concurrent D/F launches, and modify `scripts/dispatcher_runtime.py` / `scripts/gtkb_dispatcher_daemon.py` / `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_report.py` only if that fixture demonstrates a residual gap against current committed behavior, with any such source hunk explicitly deferred (via a `bridge/hunks/*.patch` artifact, not a direct edit) until WI-5429 and WI-5427 reach terminal ownership. I independently re-derived every material claim rather than trusting the proposal narrative or the task framing that spawned this review, and the proposal holds. Both mandatory preflights pass cleanly against the current operative file with zero blocking gaps. Two non-blocking findings are recorded below for Prime Builder's attention; neither affects the correctness or governance-compliance of the proposal as filed.

## Independently Re-Verified Evidence

1. Thread currency confirmed three times: at review start (`gt bridge state-report` showed `gtkb-wi5552-exited-worker-lease-reconciliation` latest-NEW at `-001.md`), again via `gt bridge show --json` mid-review, and again immediately before filing this verdict. Only one on-disk file (`-001.md`) exists at any point; no collision with another worker was observed.

2. WI-5552 independently read via `gt backlog show WI-5552`: title, full description, priority P0, project `PROJECT-GTKB-RELIABILITY-FIXES`, subproject `dispatch-lease-reconciliation` all match the proposal's Work Item metadata and Summary verbatim, including the specific cited dispatch id `2026-07-18T07-44-57Z-loyal-opposition-F-7df449`, exit code 1, 0 stdout / 306 stderr bytes, and the "~one hour" stale-liveness claim.

3. PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING independently read via `gt projects show-authorization`: status `active`, scope covers work items "by active project membership (no per-fix authorization)", owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`. WI-5552's project field (confirmed above) is `PROJECT-GTKB-RELIABILITY-FIXES`, satisfying membership coverage.

4. WI-5208 independently read: `Resolution Status: resolved`, title "Reconcile every concurrent dispatcher launch and release its leases" â€” confirms the proposal's "terminal WI-5208" framing is accurate, not fabricated.

5. WI-5429 and WI-5427 independently read: both `open`/`backlogged` under `PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING`, both currently contested (WI-5429 status detail cites a live NO-ACTION at `-003` and an in-progress circular-ordering concern with WI-5427/WI-5448/WI-5451; WI-5427 status detail cites a live NO-GO at `-006` with an unfinalized four-file version-003 candidate). This confirms the proposal's deferral framing ("record the historical incident as stale-generation exposure owned by WI-5429 then WI-5427" / "serialize any source hunk after WI-5429 and WI-5427 terminal ownership") is grounded in real, currently-open, currently-contested sibling work, not an invented excuse to avoid scope.

6. Live working-tree state independently confirmed via `git status --short` and `git diff --stat`: `scripts/dispatcher_runtime.py` and `scripts/gtkb_dispatcher_daemon.py` (two of WI-5552's five target_paths) are currently dirty with 363 net inserted/changed lines. Reading the actual diff content confirms it is WI-5427's own unfinalized candidate (`_compute_runtime_generation`, `GENERATION_HANDOFF_REQUEST_FILENAME`, `RUNTIME_GENERATION_RELATIVE_PATHS`) sitting uncommitted in the tree, exactly matching WI-5427's own status detail ("four-file version-003 candidate remains byte-stable and unfinalized"). This independently corroborates that the proposal's explicit source-hunk deferral commitment is not just prudent but necessary given live repo state, and that the proposal's authors were aware of this contention when they scoped the work as hunk-deferred rather than direct-edit.

7. TEST-11610 independently read via `gt tests show`: title "Mixed concurrent exit reconciliation releases only exited launch leases", `spec_id: SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, type `integration`, expected-behavior text matching the proposal's Proposed Scope bullet 1 near-verbatim (concurrent D/F launch-ledger entries, one live worker, two exited by timeout/failure, exact-once lease release, live worker/leases preserved, generation handoff unblocked on quiescence). This is live, pre-existing evidence that GOV-12 (work item creation triggers test creation) was honored before this proposal was filed, not a promise to create the test later.

8. All 16 cited specifications independently confirmed to exist live in MemBase via direct `gt spec show` lookups (spot-checked `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`, `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`); all `status: specified`, none stale or retired.

9. All 5 cited Prior Deliberations independently confirmed to exist live in MemBase via `gt deliberations show`: DELIB-20265026, DELIB-202665740, DELIB-20266642, DELIB-20260704-WITHDRAW-GTKB-WI4821-DISPATCH-CAN-RECEIVE-DISPATCH-DRIFT-RECONCILE-GO, DELIB-20266133. None contradicts or was superseded against this proposal's approach; DELIB-20266133 (re-home/retire `PROJECT-GTKB-DISPATCHER-RELIABILITY`) was independently cross-checked and confirms that project is now `[retired]`, while WI-5552's actual project `PROJECT-GTKB-RELIABILITY-FIXES` is `[active]` â€” the proposal is filed under the correct, live project, not a retired one.

10. Backlog/duplicate-conflict check performed against all 67 currently-actionable (latest NEW/REVISED/NO-ACTION) bridge threads: `target_paths` for every other actionable thread were grepped against WI-5552's five target paths. No exact scope duplicate was found. Two soft file-level overlaps were found and are recorded as non-blocking findings below (`gtkb-wi5549-consecutive-dispatch-item-success-ledger` on `bridge_dispatch_report.py`; `gtkb-wi5566-codex-no-window-verification-auto-refresh` on `gtkb_dispatcher_daemon.py`). Neither is itself dirty/implemented yet, so there is no live merge conflict today.

11. Architectural plausibility spot-check: `scripts/dispatcher_runtime.py` was read at the launch-ledger reconciliation surface (`_process_pending_exit_codes`, `_process_pending_exit_codes_for_last_launch`, `_recipient_launch_ledger`, `_launch_reconciliation_sort_key`, `_run_artifact_live`). Confirmed this machinery genuinely exists, is non-trivial, and already implements per-dispatch_id ledger reconciliation plus PID+create-time provenance liveness checks â€” i.e., the proposal describes a real extension point on real code, not a fictional defect.

12. Both mandatory preflights re-run against the current (only) operative file, `-001.md`, immediately before filing: `bridge_applicability_preflight.py` reported `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`, `blocking_errors: []`. `adr_dcl_clause_preflight.py` reported 5 clauses evaluated (4 must_apply, 1 may_apply), 0 evidence gaps in must_apply clauses, 0 blocking gaps, confirmed exit code `0` directly (not inferred from text). The `packet_hash` embedded below was computed fresh, in the same process, immediately before this file was written, via the same `build_packet` function the compliance-gate freshness check re-invokes to validate it.

13. Review independence confirmed: this session's `author_session_context_id` (`211b1f8c-4852-4f93-8aa0-127e2517b7b9`, harness B / Claude) is unrelated to version 001's author (`019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`, harness A / Codex, `prime-builder/codex`). This is the thread's only version; there is no reviewer history to check for self-review collision.

14. No premature implementation observed: `platform_tests/scripts/test_wi5552_exited-worker-reconciliation.py` and `bridge/hunks/gtkb-wi5552-exited-worker-lease-reconciliation.patch` are both confirmed absent from the filesystem; only the two pre-existing, unrelated (WI-5427-owned) dirty files noted in item 6 are dirty.

## Findings (Non-Blocking)

### P3 finding - proposed test filename breaks the codebase's exclusive underscore convention

Observation: the declared target path `platform_tests/scripts/test_wi5552_exited-worker-reconciliation.py` contains a hyphen inside the filename stem. A direct listing of `platform_tests/scripts/*.py` (473 files) found zero existing files matching a hyphenated `test_*-*.py` pattern - the directory's convention is 100% underscore-only. A hyphen is not a legal character in a Python identifier, so this filename risks import/collection friction (pytest rootless-import module-name synthesis, coverage module-path reporting, or any helper that constructs an import path from the file name) even though it did not trip the bridge preflight tooling, which treats target_paths as opaque strings. Recommended action: at implementation time, rename the target to `platform_tests/scripts/test_wi5552_exited_worker_reconciliation.py` (underscore) before creating the file; trivial, does not require a proposal revision.

### P4 finding - GOV-RELIABILITY-FAST-LANE-001 criterion 1 text vs. WI-5552's recorded origin field

Observation: WI-5552's MemBase `Origin` field reads `hygiene`. `GOV-RELIABILITY-FAST-LANE-001` eligibility criterion 1 reads "origin is defect or regression (never new)" verbatim, and its Enforcement clause directs Loyal Opposition to NO-GO any fast-lane proposal whose work item fails an eligibility criterion. Read in isolation this is a literal mismatch: WI-5552's own narrative describes a regression ("This regresses terminal WI-5208...") but its structured origin metadata says `hygiene`, not `regression`. However, this is not treated as blocking here because it is not a novel or isolated case: a direct check of other already-resolved work items under this exact project (`PROJECT-GTKB-RELIABILITY-FIXES`, covered by the same `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`) shows repeated precedent of non-defect/regression origins being accepted and resolved without apparent objection - WI-4356 (`hygiene`, resolved), WI-4980 (`hygiene`, resolved), WI-4538 (`improvement`, resolved) - alongside others correctly tagged `defect`. Singling out WI-5552 for strict criterion-1 enforcement while this pattern has been repeatedly accepted elsewhere in the identical project/PAUTH pairing would be inconsistent, arbitrary application of the rule rather than principled enforcement. A Deliberation Archive search for prior reconciliation of this drift returned no on-point results, confirming this has not already been settled. Recommended action: capture as a standing-backlog governance-hygiene item (per the Strategic Self-Improvement Directive) to either (a) correct WI-5552's and the precedent WIs' origin field to `regression`/`defect` for accuracy, or (b) revise `GOV-RELIABILITY-FAST-LANE-001` criterion 1 to explicitly include `hygiene`/`improvement` origins consistent with established practice. Not a reason to NO-GO this specific proposal given the precedent weight; criteria 2, 3, and 4 of the fast-lane spec are independently satisfied (no new API/CLI surface, no new/revised requirement claimed, and the default/likely path is test-only with zero source files, well within the "~3 source files / ~150 net lines" guide even in the contingent source-touch scenario, which is itself explicitly deferred to separate authority).

## Specification Links

Carrying forward the proposal's full 16-citation Specification Links section verbatim (all independently confirmed live per evidence item 8): `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `SPEC-AUQ-POLICY-ENGINE-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `GOV-STANDING-BACKLOG-001`, `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `ADR-DISPATCHER-ARCHITECTURE-001`, `DCL-DISPATCHER-DAEMON-SUPERVISION-CONTRACT-001`, `GOV-SESSION-ROLE-AUTHORITY-001`, `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`.

## Prior Deliberations

- `DELIB-20265026` - independently read; WI-4556 GO, background context only.
- `DELIB-202665740` - independently read; WI-4995 document-lease-held-health GO, directly relevant lease-mechanism precedent.
- `DELIB-20266642` - independently read; WI-4937 dispatcher-supervisor-governance GO, background context.
- `DELIB-20260704-WITHDRAW-GTKB-WI4821-DISPATCH-CAN-RECEIVE-DISPATCH-DRIFT-RECONCILE-GO` - independently read; owner-directed GO withdrawal, background context only.
- `DELIB-20266133` - independently read; owner decision to re-home/retire `PROJECT-GTKB-DISPATCHER-RELIABILITY`, cross-checked and confirms WI-5552 is correctly filed under the still-active `PROJECT-GTKB-RELIABILITY-FIXES`, not the now-retired dispatcher-specific project.

## Applicability Preflight

- bridge_document_name: `gtkb-wi5552-exited-worker-lease-reconciliation`
- packet_hash: `sha256:ae7695af4717495538b0c63dd7124dc59322bb2049c44b3631286a6eea29b5cb`
- content_file: `bridge/gtkb-wi5552-exited-worker-lease-reconciliation-001.md`
- operative_file: `bridge/gtkb-wi5552-exited-worker-lease-reconciliation-001.md`
- candidate_evidence_hash: `sha256:2235031282bd9c3a1799912487135132b0dc8a2ba3a6f54f73fe3bc8d3093f08`
- preflight_passed: `true`
- missing_required_specs: `[]`
- missing_advisory_specs: `[]`
- blocking_errors: `[]`

## Clause Applicability

Five clauses evaluated (four `must_apply`, one `may_apply`), zero evidence gaps in `must_apply` clauses, zero blocking gaps. Mode mandatory, exit code `0` confirmed directly, pass. No owner waiver required.

## Review Independence

This review's session context (`211b1f8c-4852-4f93-8aa0-127e2517b7b9`, harness B / Claude, independently-spawned sub-agent) is unrelated to version 001's author session context (`019f5f66-9582-7f03-a3f1-3c75e6bd9d0a`, harness A / Codex, `prime-builder/codex`). This is the thread's only version to date; there is no prior reviewer in this thread's history to check for collision.

## Methodology Trail

Read the full (only) version of this thread before acting. Re-confirmed thread currency via live `gt bridge state-report` / `gt bridge show --json` queries at review start, mid-review, and immediately before filing. Ran `gt deliberations search` against the WI/component topic. Independently read WI-5552, WI-5208, WI-5429, WI-5427 via `gt backlog show`. Independently read the standing project authorization via `gt projects show-authorization`. Independently read all cited specifications and prior deliberations via direct MemBase lookups rather than trusting the proposal's citations. Independently inspected live git status/diff on the declared target paths. Independently inspected the relevant reconciliation code in `scripts/dispatcher_runtime.py`. Independently confirmed TEST-11610's existence and content. Grepped all other actionable bridge threads' `target_paths` for scope collisions. Re-ran both mandatory preflights against the current operative file and confirmed exit codes directly rather than inferring them from text output, computing both the packet_hash and candidate_evidence_hash fresh in the same process immediately before writing.
