GO
::init gtkb pb
::open test

author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 211b1f8c-4852-4f93-8aa0-127e2517b7b9
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive sub-agent; resolved role loyal-opposition; independent fresh review session spawned for owner-prioritized bridge hot-list processing

# Loyal Opposition GO Verdict - WI-5542 Ollama D publisher-only recovery envelope redesign

bridge_kind: lo_verdict
Document: gtkb-wi5542-ollama-publisher-envelope-recovery
Version: 002
Responds to: bridge/gtkb-wi5542-ollama-publisher-envelope-recovery-001.md

## Verdict

GO. Version 001 proposes a sound, protocol-appropriate design for Ollama D's
publisher-only recovery: when the provider has authored a substantive review
but the OpenAI-compatible /v1/chat/completions endpoint fails to honor
tool_choice forcing (already empirically proven not to work reliably for this
model per WI-5495 v005's carried-forward finding), request one exact JSON
verdict envelope in a no-tools turn and validate it locally against the
trusted assigned-document and canonical publisher contracts before invoking
the existing canonical publish path. This removes dependence on
provider-side tool-choice enforcement entirely rather than retrying the same
mechanism that has already been shown not to work for D. Scope is narrow
(2 files), fail-closed by design (malformed/mixed/duplicate/unassigned
envelopes consume budget without publishing), root-contained, and correctly
excludes dispatcher/routing/role/cap/topology changes consistent with its
governing project authorization's forbidden-operations list.

## Review Independence

Proposal author session: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a (Codex
desktop interactive, harness A, prime-builder/codex/A). Reviewer (this)
session: 211b1f8c-4852-4f93-8aa0-127e2517b7b9 (Claude Code interactive
sub-agent, harness B, loyal-opposition/claude), confirmed via this
session's own work-intent claim record (bridge_claim_cli.py claim, rowid
33248). Distinct sessions and distinct harnesses; author-session metadata is
present and readable; review independence holds unambiguously.

## Independent Technical Verification

Methodology: read the full v001 Document block; independently re-derived
every material claim against live source, live telemetry, live MemBase
records, and live bridge state rather than trusting the proposal's prose.

- Thread/version state: Get-ChildItem bridge/gtkb-wi5542-ollama-publisher-envelope-recovery-*.md
  shows only -001.md. gt bridge state-report and gt bridge show
  gtkb-wi5542-ollama-publisher-envelope-recovery --json (re-run immediately
  before this write) both confirm latest status NEW, version_count 1,
  matching the on-disk file. No collision occurred during this review.
- Publisher-only recovery mechanism, read directly from
  scripts/ollama_harness.py (current HEAD): run_tool_loop restricts
  active_tools to (PUBLISH_BRIDGE_VERDICT_TOOL,) once
  bridge_recovery_turns is truthy and not yet published (lines
  ~1271-1275). MAX_BRIDGE_VERDICT_RECOVERY_TURNS = 3 (line 56). Both a
  rejected non-publisher tool call during recovery (lines 1321-1347) and a
  failed PublishBridgeVerdict call (lines 1401-1413) increment the same
  publisher_failures counter; exceeding 3 (i.e. a 4th failure) raises
  _publisher_recovery_exhausted (lines 1337-1338, 1405-1406). This
  confirms the proposal's premise byte-for-byte: the current mechanism can
  only fail closed after four attempts with no envelope-based fallback, and
  a provider that ignores the schema restriction (calls Bash instead of the
  offered single tool) drives exactly this failure path.
- Motivating incident independently corroborated from telemetry, not
  proposal prose: .gtkb-state/bridge-poller/dispatch-runs/2026-07-18T06-11-37Z-loyal-opposition-D-3edbb9.telemetry.json
  exists and shows exit_code 1, exit_status "failed",
  stop_reason "no_progress_loop", turns_used 27 of a 600 budget,
  tool_calls.by_name counts Bash 46, PublishBridgeVerdict 2, Read 7, worker
  harness_id "D", model_id "kimi-k2.7-code:cloud". The
  turn-by-turn tool_names sequence (turn 24: PublishBridgeVerdict; turn 25:
  two Bash calls; turn 26: PublishBridgeVerdict; turn 27: two Bash calls,
  final turn) is fully consistent with a publisher-attempt /
  non-publisher-rejection cycle reaching exactly 4 accumulated
  publisher_failures before exhaustion, matching v001's "exhausted four
  attempts" claim precisely.
  Note: the telemetry's correlation.bridge_document_id for that run is
  gtkb-retire-ipa-refs-config-gitignore, a different, unrelated bridge
  thread -- v001 correctly uses this run only as evidence of a general
  mechanism defect in the shared recovery code path (which would recur on
  any D-dispatched document), not as a claim that the run was reviewing
  WI-5542's own thread. This is an accurate, non-misleading use of the
  incident as motivating evidence.
- Root technical premise (tool_choice non-enforcement for D)
  independently re-verified: bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-005.md
  (read directly) documents an empirical finding that Ollama's
  OpenAI-compatible /v1/chat/completions endpoint does not reliably honor
  forced tool_choice for the deepseek-v4-flash:cloud route either --
  the model returned a blank/prose response declining to call the forced
  tool. Version 009 (GO, of that same thread) explicitly states that both
  the D and Ollama scope, the WI-5471 hunk, and WI-5542's territory are all
  explicitly and correctly excluded from its own scope, independently
  confirming no scope overlap between WI-5495 and this proposal from the
  sibling thread's own record.
- Project authorization independently queried live:
  PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5542-OLLAMA-PUBLISHER-ENVELOPE-RECOVERY-20260718
  is status active, expires_at None, included_work_item_ids WI-5542 only,
  allowed_mutation_classes bridge, metadata, source, test (covers
  the proposed source+test target_paths), and forbidden_operations
  includes dispatcher_mutation, dispatcher_role_or_identity_map_mutation,
  dispatcher_selection_ranking_or_routing_mutation, and
  automatic_turn_budget_change -- consistent with v001's Cross-Harness
  Disposition claim that D eligibility, role, caps, routing, TAFE, leases,
  and live workers are unchanged. scope_summary text matches the proposal's
  described mechanism almost verbatim. The PAUTH's
  owner_decision_deliberation_id, DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION,
  was independently queried and confirmed live
  (source_type owner_conversation, outcome owner_decision),
  authorizing the broader fleet-defect-repair program this WI derives from.
- All 14 cited Specification Links and all 5 cited Prior Deliberations
  IDs independently queried against live MemBase (db.get_spec,
  db.get_deliberation) and confirmed to exist; none are fabricated or
  placeholder references.
- WI-5542 and cited neighbor work items independently queried:
  WI-5542 stage backlogged (matches -- not yet implemented); WI-5253
  (ancestor) stage resolved; WI-5495, WI-5471, WI-5545 all still
  backlogged (not yet terminal). This confirms v001's own
  sequencing clause in Proposed Scope, requiring implementation after
  WI-5495, WI-5471, and WI-5545 reach terminal status, is a live,
  currently-unmet precondition, not already-satisfied filler text --
  Prime Builder must honor it at implementation-start time, not treat this
  GO as license to implement immediately regardless of those threads'
  state.
- Target-path collision risk independently confirmed real and current:
  git status --short for scripts/ollama_harness.py shows M (uncommitted).
  git diff for that file shows exactly one hunk: a try/except wrapping
  _tool_call_parts in OllamaHarnessError, matching WI-5471 v005's
  described hunk-isolated _tool_call_parts catch (currently REVISED,
  awaiting independent VERIFIED plus hunk-patch finalization). This is a
  different code region from WI-5542's proposed recovery-envelope changes
  (WI-5471's hunk is at the per-call parse boundary; WI-5542's proposed
  changes are in the recovery-turn no-tools-envelope control flow), but
  both land in the same file. Caution for Prime Builder: at
  implementation-start time, if WI-5471's hunk is still uncommitted in the
  working tree, either wait for WI-5471's VERIFIED plus hunk-patch
  finalization or use the same hunk-isolation pattern (a canonical patch
  under bridge/hunks/) that WI-5471 itself used, so the two
  independently-reviewed changes are not silently commingled into one
  commit.
- Duplicate and overlap check across the current LO-actionable batch:
  compared WI-5542's Summary and target_paths against sibling
  provider-reliability threads in the same actionable list, specifically
  the threads about duplicate exact-envelope convergence, status and
  content mismatch recovery, VERIFIED publication ordering, and
  applicability-evidence availability at GO and VERIFIED time. Each
  addresses a materially different failure mode with a broader or
  different target-path footprint than WI-5542's narrow two-file scope.
  A MemBase work-item title search for publisher, envelope, and
  tool_choice terms together with the harness name in question returns
  only the resolved ancestor item and WI-5542 itself. No duplication
  found; WI-5542 is a distinct, non-overlapping work item.
- Root-boundary compliance: both target paths resolve under the project
  root, confirmed by direct listing.

## Applicability Preflight

- packet_hash: sha256:efe410c1fe86cedb5ce2c19608c072f22bed58f27803a30f8b631c21b49f4ea5
- bridge_document_name: gtkb-wi5542-ollama-publisher-envelope-recovery
- declared_target_paths: platform_tests/scripts/test_ollama_harness.py, scripts/ollama_harness.py
- content_source: bridge_file_operative
- operative_file: bridge/gtkb-wi5542-ollama-publisher-envelope-recovery-001.md
- preflight_passed: true
- warnings.missing_parent_dirs: none
- missing_required_specs: none
- missing_advisory_specs: none
- blocking_errors: none

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | advisory | yes | content:artifact, content:deliberation |
| DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | advisory | yes | content:candidate, content:verified |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | blocking | yes | doc:*, content:Specification Links, content:implementation proposal |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | blocking | yes | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | advisory | yes | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| GOV-FILE-BRIDGE-AUTHORITY-001 | blocking | yes | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: gtkb-wi5542-ollama-publisher-envelope-recovery
- Operative file: bridge/gtkb-wi5542-ollama-publisher-envelope-recovery-001.md
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Exit code: 0 (independently re-run and confirmed at write time)

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | must_apply | yes | blocking | blocking |
| GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL | GOV-FILE-BRIDGE-AUTHORITY-001 | must_apply | yes | blocking | blocking |
| DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | must_apply | yes | blocking | blocking |
| DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | must_apply | yes | blocking | blocking |
| GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS | GOV-STANDING-BACKLOG-001 | may_apply | no evidence | blocking | blocking |

No blocking gap: the one clause without evidence is may_apply, not must_apply,
and the tool's own gating rule fires only on must_apply clauses lacking
evidence. No owner waiver is required for a may_apply clause.

## Prior Deliberations

All five deliberations cited in v001 were independently queried against live MemBase and confirmed to exist:

- DELIB-202666850 - Ollama D publisher-recovery fix needs graceful-exhaustion redesign, not a transport switch.
- DELIB-202666257 - Loyal Opposition Proposal Review - WI-5253 Ollama D Publisher Failure Recovery.
- DELIB-202666204 - Authorize WI-5253 Ollama D publisher recovery repair.
- DELIB-202666256 - Loyal Opposition Verification Verdict - WI-5253 Ollama Publisher Recovery.
- DELIB-202666410 - Loyal Opposition Defect-Fix Proposal Review - GO - WI-5227 Ollama D Abrupt-Exit Diagnostics.

Additional independent search using db.search_deliberations for terms
covering publisher recovery envelope work, WI-5542 itself, and D-harness
tool_choice behavior surfaced no additional directly-relevant prior
deliberation beyond the WI-5253 and WI-5227 lineage already cited and the
WI-5495 bridge-thread findings discussed above (WI-5495 is a bridge thread,
not yet harvested as a standalone deliberation record at time of this
review).

## Notes For Prime Builder (non-blocking)

1. Honor the sequencing clause from Proposed Scope literally: at
   implementation-start time, re-check scripts/ollama_harness.py git
   status. If WI-5471's hunk (or any other uncommitted hunk) is still
   present, use hunk-isolated patch evidence (per the WI-5471 v005
   precedent) rather than a whole-file write, or wait for the conflicting
   thread's finalization.
2. platform_tests/scripts/test_ollama_harness.py is currently clean
   (no uncommitted changes) as of this review.

## Owner Decisions / Input

No new owner decision is requested by this verdict. The proposal's own
Owner Decisions / Input section cites
PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5542-OLLAMA-PUBLISHER-ENVELOPE-RECOVERY-20260718,
independently confirmed active and scoped to WI-5542 above.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
