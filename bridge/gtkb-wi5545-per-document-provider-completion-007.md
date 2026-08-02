REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; unpublished substantive v007 candidate; dispatcher/TAFE deliberately disabled and untouched
author_metadata_source: explicit_owner_direction

# WI-5545 — Revised Per-Document Provider Completion

bridge_kind: prime_proposal
Document: gtkb-wi5545-per-document-provider-completion
Version: 007
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5545-per-document-provider-completion-006.md
Carries forward: bridge/gtkb-wi5545-per-document-provider-completion-001.md
Supersedes Prime dispositions: bridge/gtkb-wi5545-per-document-provider-completion-003.md; bridge/gtkb-wi5545-per-document-provider-completion-005.md

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5545-PER-DOCUMENT-PROVIDER-COMPLETION-20260718
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5545

target_paths: ["scripts/cloud_harness_base.py", "platform_tests/scripts/test_cloud_harness_base.py", "scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_harness.py"]

implementation_scope: source | test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

No KB mutation: this proposal performs no MemBase mutation and no
`groundtruth.db` write; `groundtruth.db` is intentionally not in
`target_paths`.

---

## Candidate And Non-Authorization Boundary

This is a complete substantive revision prepared in response to v006. It is
not a live bridge file and does not authorize implementation. Until these exact
bytes are filed through the governed writer and receive a fresh independent
Loyal Opposition `GO`, no source or test write may begin. Historical v002 and
v004 `GO` files are chain evidence only and must not be reused as current
implementation approval.

Preparing this candidate creates no work-intent claim or implementation-start
packet and changes no bridge, project, database, source, test, configuration,
dispatcher, TAFE, provider, lease, role, route, allowance, Git, deployment,
release, credential, or external-system state. Only the requested unpublished
temp file is created.

## Revision Claim

Prime Builder accepts v006's finding that v003 and v005 could not terminalize
the approved but unimplemented work. Prime Builder withdraws both
`disposition-close` assertions in full. `NO-ACTION` is non-terminal, absence of
a claim is not completion evidence, and no implementation report, verification
result, owner withdrawal, or superseding technical design exists in those
carriers.

This revision restores and refreshes the full v001 four-path implementation
proposal. The defect remains present in both provider loops: one global
`bridge_verdict_published` boolean can become true after the first successful
publication in a two-document assignment, allowing final assistant text while
another assigned document remains unadvanced. The correction tracks governed
publication per assigned document and accepts provider completion only after
every actionable assigned document has advanced exactly once.

## Finding-By-Finding Response To Version 006

### Finding 1 — V005 Cannot Override The Approved Work

Accepted. V005 contains no implementation, test, verification, owner
withdrawal, or revised-scope evidence. It is non-terminal and is expressly
withdrawn by this revision. V003 is withdrawn for the same reason.

### Finding 2 — V004 Did Not Implement Or Supersede V001

Accepted. V004 reviewed only the invalid v003 carrier and incorrectly accepted
its non-implementation disposition. It neither performed nor verified the
v001 work. This v007 responds to the current v006 NO-GO and requires a new
independent review of the complete refreshed proposal.

### Finding 3 — Lack Of A Claim Is Not Terminal Evidence

Accepted. Current claim status is `null`, no named WI-5545 implementation-start
packet exists, all four target paths are clean, and no WI-5545 source/test
implementation is present. Those facts prove that the work is still pending;
they do not cancel it.

### Finding 4 — Preserve The Review Lane

Accepted. The valid next lifecycle is v007 `REVISED` → fresh independent
`GO` → exact claim and schema-v3 start → implementation report → independent
`VERIFIED` and focused finalization. `NO-ACTION` is not used as closure.

## Requirement Sufficiency

Existing requirements sufficient.

The work item, active exact WI-5545 PAUTH v2, centralized dispatch-service contract,
harness-onboarding contract, file-bridge authority, and specification-derived
verification requirements define the correction. The trusted existing
`groundtruth_kb.bridge_dispatch_worker_context.build_worker_context_packet`
facade already supplies worker-scoped assigned content. No new ADR, DCL, owner
choice, dispatcher route, or per-work-item approval is required.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `SPEC-AUQ-POLICY-ENGINE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-RELIABILITY-FAST-LANE-001`
- `GOV-WORK-TREE-HYGIENE-001`

## Prior Deliberations And Governed Evidence

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` — controlling
  owner evidence for the bounded exact WI-5545 PAUTH, while preserving all
  later bridge/start/verification gates.
- `DELIB-20260716-WI5169-ALIBABA-H-REARM-BUDGET-LIVE` — existing provider
  budget/eligibility precedent carried forward from v001; no budget change is
  proposed here.
- `DELIB-20265026`, `DELIB-202666237`, `DELIB-20265391`, and
  `DELIB-202666250` — provider failure, verdict, and publisher-recovery
  precedents carried forward from v001.
- `DELIB-202666167` and `DELIB-202666168` — terminal WI-5207 evidence for the
  complementary dispatcher-side partial-batch detector. WI-5545 prevents the
  provider loop from exiting early rather than duplicating that detector.
- `DELIB-202666399` — terminal WI-5211 evidence establishing D/F governed
  verdict publication; WI-5545 adds per-assigned-document completion after the
  publication tool already exists.
- `bridge/gtkb-wi5545-per-document-provider-completion-001.md` — complete
  original four-target proposal carried forward here.
- `bridge/gtkb-wi5545-per-document-provider-completion-002.md` — independent
  technical confirmation of the one-global-boolean defect; retained as review
  history, not reused as v007 approval.
- `bridge/gtkb-wi5545-per-document-provider-completion-006.md` — current
  strict-valid NO-GO requiring this substantive revision.
- `bridge/gtkb-wi5495-publisher-recovery-tool-choice-forcing-011.md` and
  commit `6a8822689` — terminal/finalized WI-5495 predecessor.
- `bridge/gtkb-wi5471-toolcall-arg-parse-resilience-006.md` and commit
  `5a49705c3` — terminal/finalized WI-5471 predecessor.

No durable deliberation cancels or supersedes WI-5545. No owner decision makes
legacy per-WI `approval_state` an implementation authority.

## Owner Decisions / Input

The operative owner evidence is
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION`, embodied by active,
unexpired exact PAUTH
`PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5545-PER-DOCUMENT-PROVIDER-COMPLETION-20260718`
version 2. It includes only WI-5545, permits bridge, metadata, source, and test
classes, and uses the current canonical forbidden-operation tokens. Candidate
operation-time evaluation returns `allowed` for both packet creation and
implementation start across the four declared targets.

Version 2 is an append-only taxonomy normalization of v1 under the unchanged
owner decision and technical scope. It replaces v1's unregistered
machine-readable spellings with the canonical forbidden list:
`credential_lifecycle`, `destructive_cleanup`, `dispatcher_mutation`,
`external_system_mutation`, `git_history_rewrite`, `git_push`,
`production_deployment`, and `release`. The narrower v1 prohibitions remain
binding in v2 scope prose: no secret-value disclosure, direct harness-to-harness
invocation, provider request, dispatcher configuration/role/identity/selection/
ranking/routing change, automatic turn-budget change, or automatic production-
dispatch selection change. This normalization changes no owner-approved work.

No new owner decision or AUQ is required. WI-5545 is an active member of the
active owner-approved reliability project. Its legacy
`approval_state=unapproved` compatibility value is not authority under the
project-only approval model. Fresh independent GO, claim, start, target
collision checks, implementation report, and VERIFIED remain mandatory.

## Exact Current State And Target Preimages

Read-only observations at `2026-08-01T13:54:09.3638848Z` established:

- Project `PROJECT-GTKB-RELIABILITY-FIXES` is active version 1. Membership
  `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-5545` is active version 1; WI-5545 is
  P0, open, and backlogged.
- Operative exact WI-specific PAUTH
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5545-PER-DOCUMENT-PROVIDER-COMPLETION-20260718`
  is active version 2 with no expiry, includes only WI-5545, and permits the
  exact four-path source/test cohort at operation time.
- Append-only v1 history records the original narrow envelope. Version 2
  normalizes only the machine-readable forbidden-operation tokens and retains
  all v1 narrow exclusions in binding scope prose.
- Current physical bridge head is v006 `NO-GO`, SHA-256
  `e021c180b0666829c1d80495e844584b84441c4a184a2631e292acf00e14b0cc`.
- `scripts/cloud_harness_base.py` is clean, 115,468 bytes, SHA-256
  `53809f1e8748566335d7a08b282d594f690431d7bdf47a33d0681f61f3cd5bf5`.
- `platform_tests/scripts/test_cloud_harness_base.py` is clean, 101,582 bytes,
  SHA-256
  `68bb0334a4eb7c15835cf96622392f8c69f5ad244612475fd45ff325cb4fd3f1`.
- `scripts/ollama_harness.py` is clean, 68,954 bytes, SHA-256
  `b13f453c29b99c5cb5919649b8bc11bc160f94cdf94e8e3fee1feefa8a442ef1`.
- `platform_tests/scripts/test_ollama_harness.py` is clean, 63,707 bytes,
  SHA-256
  `47a713da83d6e6c366989df5094905529204c872fa49cca28fd769e8ee7a88ef`.
- Current Git HEAD is `75decbfa704fe50288aecbc5669def329a0825df`.
- `bridge_claim_cli.py status gtkb-wi5545-per-document-provider-completion`
  returned `null`.
- Named packet
  `.gtkb-state/implementation-authorizations/by-bridge/gtkb-wi5545-per-document-provider-completion.json`
  is absent. The current compact packet inventory found zero valid packets.
- WI-5495 is physically terminal VERIFIED at v011 and its historical claim is
  expired. WI-5471 is physically terminal VERIFIED at v006 and has no claim.
- Current code still contains the single global boolean at
  `scripts/cloud_harness_base.py:2383` with first-success assignment at line
  2657, and at `scripts/ollama_harness.py:1268` with first-success assignment
  at line 1424. Neither source has assigned-slug or per-document publication
  tracking. The target tests have no two-document completion fixtures.

These hashes are proposal evidence, not future preimage waivers. The start
gate must recompute exact bytes and Git status after a fresh v007 GO.

## Cleared Predecessors And Shared-Target Collision State

The two explicit v001 predecessors are cleared:

- WI-5495: v011 VERIFIED and focused-finalized in commit `6a8822689`.
- WI-5471: v006 VERIFIED and focused-finalized in commit `5a49705c3`.

The following nonterminal proposal threads declare at least one shared target:

- WI-5216 `gtkb-wi5216-denial-loop-recovery-reliability-fixes` — v006 NO-GO;
- WI-5216 `gtkb-wi5216-provider-verdict-denial-loop-recovery` — v006 NO-GO;
- WI-5542 `gtkb-wi5542-ollama-publisher-envelope-recovery` — v006 NO-GO;
- WI-5578 `gtkb-wi5578-provider-verdict-status-consistency-recovery` — v004
  NO-GO;
- WI-5599 `gtkb-wi5599-provider-duplicate-envelope-recovery` — v002 NO-GO;
  and
- WI-5600 `gtkb-wi5600-provider-applicability-preflight-recovery` — v002
  NO-GO.

Those threads currently hold no clean target bytes or valid implementation
packet and do not block filing/review of v007. Their existence still requires a
fresh operation-time collision check. If any becomes GO, acquires a claim/start,
or changes a target before WI-5545 begins, WI-5545 must stop and establish an
explicit ordering or hunk-safe non-overlap disposition. It may not absorb,
overwrite, or silently sequence around foreign work.

## Exact Implementation Design

### 1. Resolve The Trusted Assignment Set

In both provider loops, load the current worker's dispatch assignment only
through
`groundtruth_kb.bridge_dispatch_worker_context.build_worker_context_packet(project_root, self_only=True)`.
Do not read dispatcher/TAFE files, launch records, lease state, or environment
internals directly. Require packet preflight `PASS`, no blockers, and a
non-empty `assigned_content` list.

Normalize the distinct `document_name` values from `assigned_content`. Retain
only documents whose assigned current status is role-actionable for the Loyal
Opposition worker (`NEW`, `REVISED`, or `NO-ACTION`). Reject missing, malformed,
ambiguous, or duplicate assignment identities fail-closed. The assignment
packet is read once per provider-loop invocation; do not expand its set from
model output.

### 2. Track Completion Per Assigned Document

Replace the one global completion boolean with explicit per-run state:

- immutable `assigned_document_slugs`;
- mutable `pending_document_slugs`, initially the full actionable assignment;
  and
- `published_document_slugs`, initially empty.

Parse the target bridge slug and requested verdict from each
`PublishBridgeVerdict` tool call before publisher execution. A slug not in the
trusted assignment, a slug already published in this run, or a slug not
pending must produce a correlated actionable tool error and must not invoke
the canonical publisher. A role-ineligible verdict must continue to fail
through existing publisher authority checks.

Only after the canonical publisher returns the existing mechanically trusted
success result for that same pending slug may the loop move the slug from
pending to published. Failed, denied, malformed, mismatched, or ambiguous
publisher results do not advance completion.

### 3. Enforce All-Document Completion

Final assistant text or a blank completion is accepted only when
`pending_document_slugs` is empty. After one success in a multi-document
assignment, keep the provider loop active and present a deterministic recovery
message naming the remaining assigned document count without exposing
unassigned content. Existing bounded provider/turn recovery semantics remain
controlling. Exhaustion or a provider failure while documents remain pending
must return the existing actionable failure shape and must never count as
completion.

Single-document assignments preserve their current successful behavior. Zero
actionable assigned documents fail closed rather than silently treating the
run as complete.

### 4. Preserve Provider Parity And Boundaries

Implement equivalent assigned-document invariants in the shared cloud adapter
used by F/OpenRouter and in the D/Ollama adapter. Preserve provider-specific
transport, error, and tool-call parsing behavior. Harness A remains PB-only and
unchanged. B, C, E, and H roles, eligibility, routes, caps, and providers are
unchanged. D and F retain their existing resolved per-harness dispatch limits;
this proposal neither hard-codes nor changes those values.

### 5. No New Timing Or Concurrency Constants

Do not add any hard-coded timeout, TTL, expiry, grace interval, retry count,
backoff, throttle, threshold, fan-out limit, max-items value, or per-harness
concurrency limit. The implementation must use existing centrally resolved
provider/turn budgets and assignment caps. Any measured need to change those
values is separate Timer Governance work under WI-5806 and WI-5807 and must be
configured through the selected canonical SoT, not source literals.

The 82.1-second read of 551 historical implementation packets observed during
this audit is already tracked by WI-5598 and coordinated with WI-5806/WI-5807.
It is not duplicated here and does not justify a new local timer.

## Cross-Harness Disposition

- **A / Codex**: PB-only lane unchanged; no provider-loop behavior change.
- **D / Ollama**: direct source/test target; every assigned actionable document
  must publish exactly once before completion.
- **F / OpenRouter**: direct source/test target through the shared cloud
  adapter; same invariant as D.
- **B, C, E, H**: no role, eligibility, routing, cap, provider, or runtime
  change.

## Intuitiveness Review

```json
{
  "decision": "pass",
  "normal_flow": "A provider assigned two bridge documents must visibly advance both documents before its final response can complete the dispatch.",
  "single_document_flow": "A one-document assignment retains the current successful publish-then-complete behavior.",
  "error_flow": "Wrong, duplicate, unassigned, malformed, or denied verdict calls return a correlated actionable error and do not consume another document's completion state.",
  "operator_model": "The trusted assignment packet defines the finite checklist; publisher success checks off exactly one matching item."
}
```

## Non-Impairment Review

```json
{
  "decision": "pass",
  "preserved": [
    "canonical governed PublishBridgeVerdict authority and numbered-file publication",
    "existing provider transport and tool-call parsing behavior",
    "fixed A/D/F topology and current centrally resolved per-harness limits",
    "roles, eligibility, routing, leases, allowances, and live-worker behavior",
    "independent review, claim, implementation-start, verification, and finalization gates",
    "application isolation and the E:/GT-KB root boundary",
    "dispatcher and TAFE disabled/untouched state"
  ],
  "excluded": [
    "dispatcher or TAFE reads through internal runtime paths",
    "dispatcher configuration, routing, selection, ranking, role, identity, or automatic budget changes",
    "new hard-coded timing, retry, threshold, fan-out, max-items, or concurrency values",
    "provider requests, credentials, deployment, release, Git push, and unrelated files"
  ],
  "conclusion": "The change tightens completion accounting without widening provider, routing, timing, concurrency, or bridge authority."
}
```

## Specification-Derived Verification Plan

| Requirement | Executed evidence required | Required result |
|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`, `GOV-FILE-BRIDGE-AUTHORITY-001` | Re-read physical v007 head, fresh independent GO, exact PAUTH, claim/start, all four preimages, Git cleanliness, and shared-target collision state immediately before mutation. | V007 is current; exact authority exists; targets match; no foreign owner or unapproved byte is adopted. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Add a two-document F fixture in `platform_tests/scripts/test_cloud_harness_base.py`: publish the first assigned slug, return final text, publish the second, then return final text. | First final text is rejected/recovered; second publication advances only its slug; final text is accepted only after both succeed. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`, `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Add the equivalent two-document D fixture in `platform_tests/scripts/test_ollama_harness.py`. | D enforces the same per-document completion invariant as F while preserving Ollama-specific transport behavior. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | In both test modules, attempt a wrong/unassigned slug, duplicate publication, malformed slug/result, publisher denial, and role-ineligible verdict. Spy on canonical publisher invocation and inspect correlated tool errors. | Wrong/duplicate/unassigned calls are rejected before publisher execution; failed/denied/malformed calls do not advance pending state; role authority remains fail-closed. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Run paired parametrized assertions over D and F for assignment resolution, first success, remaining work, duplicate rejection, and all-complete acceptance. | Equivalent invariants and outcomes hold across both provider adapter families. |
| `SPEC-AUQ-POLICY-ENGINE-001` | Exercise missing, blocked, ambiguous, empty, and duplicate worker-context assignment packets. | Machine-resolvable errors remain automatic and actionable; no owner prompt or AUQ is introduced for runtime faults. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-RELIABILITY-FAST-LANE-001` | Run `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_cloud_harness_base.py platform_tests/scripts/test_ollama_harness.py -q --tb=short`. | Complete affected provider test modules pass, including new TEST-11604 coverage. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `GOV-WORK-TREE-HYGIENE-001` | Run Ruff check, Ruff format check, Python compilation on all four targets, and `git diff --check`. | All mechanical gates pass and the diff contains only the four approved targets plus governed evidence. |
| Timer/concurrency SoT directive; WI-5806/WI-5807 | Inspect the exact source diff for numeric timing/retry/backoff/threshold/fan-out/max-items/concurrency additions and trace every existing budget/cap lookup. | No new hard-coded value in those classes; existing centrally resolved values are reused unchanged. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`, `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Run applicability and mandatory clause preflights against exact filed v007 and later implementation-report bytes. | No missing required/advisory specification, blocking error, evidence gap, or blocking clause gap. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Compare target metadata, claim/start paths, Git diff, and implementation report. | All implementation paths remain the four declared files under `E:/GT-KB`; no adopter path changes. |
| Fresh substantive proof after VERIFIED | In a separately authorized, non-mutating production observation after independent verification/finalization, observe dispatcher-produced two-document D and F assignments. | Each provider advances every assigned document through the canonical publisher; topology and allowances remain unchanged. No provider request is authorized by WI-5545 itself. |

## Exact Implementation Sequence

1. Publish this complete v007 through the governed bridge writer and obtain a
   fresh independent Loyal Opposition GO on v007.
2. Reconfirm WI-5495 and WI-5471 remain terminal/finalized and all four target
   paths remain clean at the recorded or explicitly reconciled bytes.
3. Re-read all target-overlapping threads and fail closed on any active claim,
   packet, post-implementation report, dirty byte, or incompatible GO.
4. Acquire one exact WI-5545 work-intent claim and one matching schema-v3
   implementation-start packet for exactly the four declared targets.
5. Add failing two-document, invalid/duplicate/unassigned-slug, packet-error,
   and single-document-preservation tests before or with the source correction.
6. Implement per-assigned-document state in the cloud and Ollama provider loops
   using only the worker-context facade and canonical publisher result.
7. Run the complete specification-derived test and mechanical matrix, including
   the no-new-hard-coded-timing/concurrency diff audit.
8. Release the exact claim and file a complete four-target implementation
   report with observed results for independent verification.

No step uses or activates TAFE, mutates dispatcher state/configuration, invokes
a provider, changes live workers, changes timing/concurrency values, or writes
outside the four targets and governed bridge/evidence artifacts.

## Acceptance Criteria

- V003 and v005 disposition-close assertions are expressly withdrawn and do
  not terminalize the chain.
- A fresh independent GO reviews v007; historical v002/v004 are not reused.
- WI-5495 and WI-5471 remain terminal/finalized and their landed behavior is
  preserved.
- The assignment set comes only from
  `build_worker_context_packet(project_root, self_only=True)` and cannot be
  expanded by model output.
- A two-document D or F assignment cannot complete after one publication.
- Each successful canonical publication advances exactly its matching pending
  assigned slug.
- Wrong, duplicate, unassigned, malformed, denied, or role-ineligible calls do
  not advance completion; where required, they fail before publisher execution.
- Final provider text is accepted only when every actionable assigned document
  has advanced; incomplete exhaustion remains actionable and non-terminal.
- Single-document behavior and provider-specific transport remain intact.
- No new hard-coded timer, TTL, retry, backoff, throttle, threshold, fan-out,
  max-items, or concurrency value is added.
- The four exact target modules pass TEST-11604, full affected tests, Ruff,
  formatting, compilation, diff checks, applicability, and mandatory clauses.
- Dispatcher/TAFE, routes, roles, eligibility, leases, allowances, provider
  requests, credentials, Git push, deployment, release, and unrelated paths
  remain untouched.
- Only independent VERIFIED plus focused finalization can close WI-5545.

## Risks And Rollback

The principal behavioral risk is an adapter loop that never completes because
its pending set is constructed incorrectly or a legitimate publisher success
is not matched to its assigned slug. The mitigation is one immutable trusted
assignment snapshot, exact slug matching, paired D/F multi-document tests,
single-document regression coverage, and use of existing centrally resolved
bounded provider/turn behavior. No new local timer may mask a state defect.

The principal concurrency risk is shared-target adoption. All four targets are
currently clean, but six nonterminal proposals declare overlapping paths. A
fresh operation-time collision check is mandatory after GO and before start.
Any new owner, dirty byte, report, or incompatible approval stops WI-5545 for
explicit ordering or hunk-safe reconciliation.

Rollback under separate authority reverts only the four approved source/test
changes. It must preserve append-only bridge history and must not remove landed
WI-5495/WI-5471 behavior. If whole-file rollback would remove another work
item's later hunk, use a governed hunk-scoped rollback. Rollback never mutates
TAFE, dispatcher configuration/runtime, timing/concurrency SoT, provider state,
credentials, deployment, release, or Git history.

## Pre-Filing Preflight Subsection

Before any live filing, run these read-only gates against this exact candidate:

1. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5545-per-document-provider-completion --content-file .tmp-wi5545-v007.md --json`;
2. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5545-per-document-provider-completion --content-file .tmp-wi5545-v007.md`; and
3. the canonical bridge-compliance audit using prospective path
   `bridge/gtkb-wi5545-per-document-provider-completion-007.md`.

Measured during candidate completion before live filing:

- `preflight_passed: true`;
- `missing_required_specs: []`;
- `missing_advisory_specs: []`;
- `blocking_errors: []`;
- operative PAUTH:
  `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-WI5545-PER-DOCUMENT-PROVIDER-COMPLETION-20260718`
  v2, operation-time status `allowed` for the exact four-path source/test
  cohort;
- author metadata warnings, missing parent directories, and unclassified
  targets: empty;
- mandatory clause preflight: 5 clauses evaluated, 4 `must_apply`, 1
  `may_apply`, 0 must-apply evidence gaps, 0 blocking gaps, exit 0; and
- prospective canonical bridge-compliance audit: `decision: pass`,
  `preflight_passed: true`.

The final exact-candidate packet hash is external audit evidence because
embedding a content hash changes the hashed bytes. Any later byte change
requires all three checks to rerun, and the governed writer must rerun them at
publication time. Preparing this candidate does not publish it.

## Files Expected To Change

- `scripts/cloud_harness_base.py`
- `platform_tests/scripts/test_cloud_harness_base.py`
- `scripts/ollama_harness.py`
- `platform_tests/scripts/test_ollama_harness.py`

## Recommended Commit Type

`fix(dispatch)` because the implementation corrects provider-loop completion
accounting for dispatcher-assigned bridge documents.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
