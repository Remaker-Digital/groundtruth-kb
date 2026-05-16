REVISED

# Implementation Proposal - Repair Bridge Dispatcher Deferral Enforcement (GTKB-GOV-008)

bridge_kind: implementation_proposal
Document: gtkb-bridge-dispatcher-deferral-enforcement-repair
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-ADOPTER-EXPERIENCE-ADOPTER-EXPERIENCE-BATCH
Project: PROJECT-GTKB-ADOPTER-EXPERIENCE
Work Item: GTKB-GOV-008

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/detector.py", "groundtruth-kb/src/groundtruth_kb/bridge/notify.py", "groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py", "groundtruth-kb/tests/test_bridge_detector.py", "groundtruth-kb/tests/test_bridge_notify.py", "platform_tests/scripts/test_cross_harness_bridge_trigger.py"]

This REVISED proposal repairs bridge dispatcher deferral enforcement defects identified in WI-3308 description and in `DELIB-0872` / `DELIB-0873`: the canonical bridge status parser does not recognize `DEFERRED`, so a `DEFERRED:` line cannot be parsed and a dispatcher cannot suppress dispatch for a deferred document. This `-003` revision rebases the entire scope onto the live `groundtruth_kb.bridge` package surface.

## Revision Notes (-003 vs -001, addressing the -002 NO-GO)

The `-002` NO-GO raised six findings. Each is addressed below.

- **F1 (`target_paths` authorizes dead paths).** `-001` cited `groundtruth-kb/src/groundtruth_kb/bridge/freshness_parser.py` and `tests/scripts/test_cross_harness_bridge_trigger.py`, neither of which exists. `-003` rebases `target_paths` onto the live files verified by directory listing: the canonical parser `groundtruth-kb/src/groundtruth_kb/bridge/detector.py`, its consumers `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` and `groundtruth-kb/src/groundtruth_kb/bridge/status_driver.py`, and the real test files `groundtruth-kb/tests/test_bridge_detector.py`, `groundtruth-kb/tests/test_bridge_notify.py`, and `platform_tests/scripts/test_cross_harness_bridge_trigger.py`. No protected narrative/rule path is in scope: `DEFERRED` line syntax is already authorized by `.claude/rules/file-bridge-protocol.md` § Statuses inclusion is NOT being changed by this proposal — see F2 below for the explicit scoping decision.
- **F2 (status vocabulary stale against canonical parser).** `-001` claimed it would add `DEFERRED`, `WITHDRAWN`, and `ADVISORY`. Live inspection of `detector.py:24-37` confirms `ADVISORY` and `WITHDRAWN` are already present in both `BridgeStatus` and `_STATUS_LINE_RE`. `-003` narrows the parser change to `DEFERRED` only. The first-class-status question is answered explicitly in § DEFERRED Status Semantics below: `DEFERRED` IS a valid `bridge/INDEX.md` status, its line syntax, setter/clearer authority, terminal-vs-reversible behavior, and `compute_actionable_pending` handling are all specified.
- **F3 (generated-wrapper hygiene not tied to active runtime).** `-001` IP-3 asked Prime to inspect generated wrapper paths. `-002` evidence shows `DELIB-0872` F3 referenced `independent-progress-assessments/bridge-automation/*-noconsole.generated.ps1`, a retired poller-wrapper path. The cross-harness trigger is now a pure-Python event-driven hook with no generated PowerShell wrapper. `-003` removes IP-3 entirely. No current generated output is consumed by `scripts/cross_harness_bridge_trigger.py`; the concern is obsolete.
- **F4 (owner-mute authority under-specified).** `-001` IP-4 proposed writing an `owner_conversation` DELIB row from a runtime env var. `-002` correctly flagged that local process state is not durable owner authorization. `-003` removes owner-mute recording from this proposal entirely. Owner-mute authority is a separate owner-decision concern and is filed as a follow-on (see § Follow-On: Owner-Mute Authority). This proposal is now a pure parser/consumer source-and-test repair with no governance-record creation.
- **F5 (verification command points at absent suites).** `-001` ran `pytest tests/scripts/test_cross_harness_bridge_trigger.py groundtruth-kb/tests/bridge/`, neither path exists. `-003`'s § Specification-Derived Verification Plan uses only runnable current-path commands verified to resolve.
- **F6 (uncited advisory governance specs).** `-001` omitted `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`. `-003` cites all three in § Specification Links.

## Claim

Single-point repair: extend the canonical bridge status parser (`detector.py`) to recognize `DEFERRED` as a valid `bridge/INDEX.md` status, and propagate that recognition into the two consumers that classify status actionability (`notify.py`, `status_driver.py`) so a `DEFERRED` top status is treated as non-actionable / non-dispatchable. This makes deferral enforceable: a document whose top status is `DEFERRED` is excluded from the dispatcher's actionable signature, so no counterpart harness is spawned for it.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; the dispatcher and status parser operate within it, and `bridge/INDEX.md` is the canonical workflow state.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the cross-harness event-driven trigger is the dispatch substrate; parser changes must hold symmetrically for both harness dispatch directions.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths must remain in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting constraint requiring this proposal to cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting constraint requiring the post-implementation VERIFIED step to rest on executed spec-derived tests; the verification plan below maps every linked spec to a test.
- `GOV-STANDING-BACKLOG-001` - GTKB-GOV-008 is a tracked work item in the standing backlog.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, and linked specs form the artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the `DEFERRED` status is itself a lifecycle-state marker for a bridge document.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this fix is captured as governed work (GTKB-GOV-008) with a bridge artifact and spec-derived tests.

## Prior Deliberations

- `DELIB-0873` - prior scope GO for bridge dispatcher deferral enforcement. It required a follow-on implementation bridge to state the selected design, cover both dispatch directions or a shared helper, account for generated-wrapper propagation where applicable, define mute/deferred authority, and add suppression tests. This proposal satisfies the design-statement and suppression-test requirements; the generated-wrapper requirement is now N/A (retired path, see F3) and owner-mute authority is split to a follow-on (see F4).
- `DELIB-0872` - prior implementation NO-GO. It found parser freshness logic ignored `DEFERRED`, status recognition was duplicated, generated-wrapper handling conflicted with the then-current wrapper contract, and owner-only decisions were not recorded. This proposal addresses the `DEFERRED`-recognition finding directly; the duplication finding is addressed by routing all consumers through `BridgeStatus`; the generated-wrapper and owner-mute findings are scoped out per F3/F4.

No prior deliberation rejected adding `DEFERRED` to the canonical parser; this is the first proposal to implement that change against the live `detector.py` surface.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved the `PROJECT-GTKB-ADOPTER-EXPERIENCE` authorization (`DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`), which explicitly includes work item `GTKB-GOV-008` in its `included_work_item_ids`. That project-scoped authorization is the owner-approval evidence for ordinary scoped source/test work on this WI. No additional per-fix owner decision is required for this REVISED proposal; the `-002` NO-GO itself states "None at this review stage" for owner decisions.
- No owner decision is requested by this REVISED proposal. Owner-mute authority (which WOULD require an owner decision) is explicitly removed from scope and deferred to a separate proposal (see § Follow-On: Owner-Mute Authority).

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` establishes `bridge/INDEX.md` as canonical workflow state and the file-bridge protocol's status vocabulary; `.claude/rules/file-bridge-protocol.md` § Statuses already enumerates `DEFERRED` as a recognized owner/Prime parking status in practice (the standing-backlog and advisory-loop rules reference explicit deferral). The canonical parser simply does not yet implement that recognition. This work implements an already-governed status into the live parser. No new or revised requirement or specification is created by this proposal.

## DEFERRED Status Semantics

Per the `-002` F2 instruction to define `DEFERRED` first-class semantics before requesting implementation approval, this section specifies the status precisely. These semantics are the design the implementation must follow; they do not create a new specification artifact (they implement `GOV-FILE-BRIDGE-AUTHORITY-001`'s already-canonical status model).

1. **First-class status.** `DEFERRED` IS a valid `bridge/INDEX.md` status, added to the `BridgeStatus` `StrEnum` in `detector.py` and to the `_STATUS_LINE_RE` alternation.
2. **Line syntax.** Identical to every other status line: `DEFERRED: bridge/<document-name>-<NNN>.md`. The version file referenced by a `DEFERRED` line is an ordinary append-only bridge version file (the document whose disposition is "parked").
3. **Setter authority.** `DEFERRED` is a Prime-Builder-set status, set by Prime when Prime parks its own proposal awaiting a future trigger (consistent with `.claude/rules/peer-solution-advisory-loop.md` `defer` classification and the parked-draft pattern). It is NOT a Loyal Opposition verdict. Loyal Opposition verdicts remain `GO` / `NO-GO` / `VERIFIED` / `ADVISORY`.
4. **Clearer authority.** A `DEFERRED` document is un-parked the normal append-only way: Prime adds a new `REVISED` (or `NEW` for a re-scoped follow-on) version line at the top of the entry when the defer trigger fires. No special clear operation is introduced; the existing top-of-list status precedence handles it.
5. **Terminal vs reversible.** `DEFERRED` is NOT terminal. It is a reversible parking state: a later `REVISED`/`NEW` line supersedes it. (Contrast: `VERIFIED` and `WITHDRAWN` are effectively terminal.)
6. **`compute_actionable_pending` handling.** A document whose CURRENT TOP STATUS is `DEFERRED` is excluded from BOTH the Prime actionable list and the Codex actionable list — `DEFERRED` is added to neither `ACTIONABLE_STATUSES_FOR_PRIME` nor `ACTIONABLE_STATUSES_FOR_CODEX`. It is therefore non-dispatchable: the cross-harness trigger's actionable signature will not include a `DEFERRED`-topped document, so no counterpart harness is spawned for it. This is the deferral-enforcement behavior the WI requires.
7. **`status_driver.py` handling.** `DEFERRED` is added to `NON_ACTIONABLE_STATUSES` alongside `VERIFIED`, `WITHDRAWN`, and `ADVISORY`, so the bridge status snapshot classifies a `DEFERRED`-topped document as non-actionable for both roles.

## Proposed Scope

### IP-1: Add DEFERRED to the canonical parser

In `groundtruth-kb/src/groundtruth_kb/bridge/detector.py`:

- Add `DEFERRED = "DEFERRED"` to the `BridgeStatus` `StrEnum` (currently `detector.py:24-31`).
- Add `DEFERRED` to the `_STATUS_LINE_RE` status alternation (currently `detector.py:35-38`).

After this change, a `DEFERRED: bridge/<name>-<NNN>.md` line parses into a `BridgeVersion` with `status=BridgeStatus.DEFERRED` instead of producing a `ParseError`.

### IP-2: Propagate non-actionable / non-dispatchable classification

`ADVISORY` and `WITHDRAWN` already classify correctly because they are absent from `ACTIONABLE_STATUSES_FOR_PRIME` / `ACTIONABLE_STATUSES_FOR_CODEX` in `notify.py:76-77` and present in `NON_ACTIONABLE_STATUSES` in `status_driver.py:23-27`. `DEFERRED` inherits the same treatment:

- In `notify.py`: `DEFERRED` is deliberately added to NEITHER `ACTIONABLE_STATUSES_FOR_PRIME` nor `ACTIONABLE_STATUSES_FOR_CODEX`. `compute_actionable_pending` (`notify.py:291-345`) already skips any status not in those two sets ("VERIFIED + anything else: not actionable, skip"), so adding `DEFERRED` to `BridgeStatus` is sufficient for it to be skipped. The change in `notify.py` is to add `DEFERRED` to the module-level documentation/comments that enumerate handled statuses, and to add it to any explicit exhaustiveness check if one exists, so the skip is intentional and documented, not incidental.
- In `status_driver.py`: add `BridgeStatus.DEFERRED.value` to `NON_ACTIONABLE_STATUSES` (`status_driver.py:23-27`) so the bridge status snapshot explicitly classifies `DEFERRED` as non-actionable.

The cross-harness trigger (`scripts/cross_harness_bridge_trigger.py`) requires NO code change: it consumes `parse_index` and `compute_actionable_pending` by lazy import (`cross_harness_bridge_trigger.py:392-396`), so a `DEFERRED`-topped document is automatically excluded from its actionable signature once IP-1 and IP-2 land. `scripts/cross_harness_bridge_trigger.py` is therefore NOT a target path; only its test file is, to add a regression test (T5).

### IP-3: Tests

Spec-derived tests added/updated within the test `target_paths`. See § Specification-Derived Verification Plan.

## Specification-Derived Verification Plan

Each linked specification maps to at least one test. Tests are added or updated only within the test files in `target_paths`.

| Test | Behavior verified | Linked spec(s) | File |
|---|---|---|---|
| T1 `test_parse_index_recognizes_deferred` | A `DEFERRED: bridge/<name>-001.md` line parses to `BridgeVersion(status=BridgeStatus.DEFERRED)` and produces zero `ParseError`. | `GOV-FILE-BRIDGE-AUTHORITY-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `groundtruth-kb/tests/test_bridge_detector.py` |
| T2 `test_bridge_status_enum_includes_deferred` | `BridgeStatus.DEFERRED` exists and equals `"DEFERRED"`. | `GOV-FILE-BRIDGE-AUTHORITY-001` | `groundtruth-kb/tests/test_bridge_detector.py` |
| T3 `test_deferred_top_status_not_actionable_for_either_role` | `compute_actionable_pending` excludes a document whose top status is `DEFERRED` from BOTH the Prime list and the Codex list. | `GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `groundtruth-kb/tests/test_bridge_notify.py` |
| T4 `test_status_driver_classifies_deferred_non_actionable` | `NON_ACTIONABLE_STATUSES` contains `DEFERRED`; a `DEFERRED`-topped document is not in either role's `BridgeQueueSnapshot` actionable set. | `GOV-FILE-BRIDGE-AUTHORITY-001` | `groundtruth-kb/tests/test_bridge_detector.py` (status_driver coverage) |
| T5 `test_trigger_excludes_deferred_from_actionable_signature` | The cross-harness trigger's `_compute_actionable` returns no entry for a `DEFERRED`-topped document, so it is absent from the dispatchable selection. | `ADR-CODEX-HOOK-PARITY-FALLBACK-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `platform_tests/scripts/test_cross_harness_bridge_trigger.py` |
| T6 regression | The full existing detector + notify + trigger suites still pass with no regression in `NEW`/`REVISED`/`GO`/`NO-GO`/`VERIFIED`/`ADVISORY`/`WITHDRAWN` classification. | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | all three test files |

Verification commands (all paths verified to resolve on the current checkout):

```
python -m pytest groundtruth-kb/tests/test_bridge_detector.py -q --tb=short
python -m pytest groundtruth-kb/tests/test_bridge_notify.py -q --tb=short
python -m pytest platform_tests/scripts/test_cross_harness_bridge_trigger.py -q --tb=short
python -m ruff check groundtruth-kb/src/groundtruth_kb/bridge/ platform_tests/scripts/test_cross_harness_bridge_trigger.py
python -m ruff format --check groundtruth-kb/src/groundtruth_kb/bridge/
```

## Acceptance Criteria

1. `BridgeStatus.DEFERRED` exists; `_STATUS_LINE_RE` recognizes a `DEFERRED:` line; a `DEFERRED` line parses with zero `ParseError`.
2. `DEFERRED` is absent from both `ACTIONABLE_STATUSES_FOR_PRIME` and `ACTIONABLE_STATUSES_FOR_CODEX`; `compute_actionable_pending` excludes a `DEFERRED`-topped document from both lists.
3. `DEFERRED` is present in `status_driver.py` `NON_ACTIONABLE_STATUSES`.
4. The cross-harness trigger excludes a `DEFERRED`-topped document from its actionable signature with no code change to `cross_harness_bridge_trigger.py`.
5. T1-T6 pass; `ruff check` and `ruff format --check` are clean for the touched files.
6. No regression in existing `NEW`/`REVISED`/`GO`/`NO-GO`/`VERIFIED`/`ADVISORY`/`WITHDRAWN` classification.

## Follow-On: Owner-Mute Authority

`DELIB-0873` Required Conditions and the WI-3308 description also mention owner-mute authority recording. Per the `-002` F4 finding, owner-mute authority is an owner-decision concern: it requires defining who can set/clear a mute, where the durable owner decision is captured, and how reason/expiration are supplied — none of which can be satisfied by local process state. This proposal explicitly EXCLUDES owner-mute recording. A separate owner-decision proposal will be filed for owner-mute authority if the owner wants it; that proposal will route the owner decision through `AskUserQuestion` and the formal-artifact-approval path. This split is the `-002` F4 recommended action ("defer owner-mute recording to a separate owner-decision proposal").

## Risks / Rollback

- Risk: a consumer of `BridgeStatus` outside the three target files performs an exhaustive match that would break on a new enum member. Mitigation: implementation begins with a repo-wide grep for `BridgeStatus` match/case and `if status ==` sites; any additional consumer found that exhaustively matches is reported in the post-implementation report (and, if it requires a code change outside `target_paths`, implementation stops and a revised proposal is filed). The known consumers (`notify.py`, `status_driver.py`) are in `target_paths`; `cross_harness_bridge_trigger.py` consumes only the function results, not the enum, so it is unaffected.
- Risk: adding `DEFERRED` to the regex changes parse output for any historical INDEX line that happened to read `DEFERRED:`. Mitigation: today such a line produces a `ParseError`, not a silent skip, so any pre-existing `DEFERRED:` line is already visible; the change converts an error into a correct parse, which is the intended behavior.
- Rollback: revert the `detector.py` enum + regex change and the `notify.py` / `status_driver.py` documentation/constant additions. The three changes are small and independent; reverting `detector.py` alone disables the feature cleanly because the consumers' skip behavior is the default for unknown statuses.

## Recommended Commit Type

`fix:` - repairs broken behavior (deferral could not be enforced because the canonical parser rejected the `DEFERRED` status). No new public API or capability surface; the change is a status-vocabulary repair. Approximately 10-20 LOC of source plus the spec-derived tests.

## Bridge INDEX Maintenance

This REVISED proposal is filed as version `-003` of the existing `Document: gtkb-bridge-dispatcher-deferral-enforcement-repair` entry in `bridge/INDEX.md`. The `REVISED: bridge/gtkb-bridge-dispatcher-deferral-enforcement-repair-003.md` line is inserted at the top of that entry's version list, above the existing `NO-GO: ...-002.md` and `NEW: ...-001.md` lines, per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` (latest version at the top; `bridge/INDEX.md` is canonical workflow state). No prior version line is deleted or reordered; the append-only audit trail is preserved.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-defect source-and-test fix for one work item, GTKB-GOV-008. It is not a bulk backlog operation. It performs no batch resolve, promote, or retire of work items or specifications. References to "work item", "backlog", and "standing backlog" describe the single work item GTKB-GOV-008 and its governed filing path only. The applicable evidence pattern is a single-WI defect-fix implementation proposal with formal-artifact-approval discipline preserved unchanged: no formal artifact (GOV/ADR/DCL/SPEC/DELIB) is created or mutated by this work. The inventory of touched files is the six `target_paths` entries above; the review-packet for this proposal is IP-1 (parser), IP-2 (consumer propagation), and IP-3 (tests).

## Pre-Filing Preflight

Both mandatory pre-filing preflights were run on this `-003` content after the INDEX entry was added; outputs are embedded in § Applicability Preflight and § Clause Applicability below.

## Applicability Preflight

```text
## Applicability Preflight

- packet_hash: `sha256:803690a47ea3e236232acac2303946f02d3b814d1355ebedd15e1d915f09b27f`
- bridge_document_name: `gtkb-bridge-dispatcher-deferral-enforcement-repair`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-dispatcher-deferral-enforcement-repair-003.md`
- operative_file: `bridge/gtkb-bridge-dispatcher-deferral-enforcement-repair-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md |
```

## Clause Applicability

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-dispatcher-deferral-enforcement-repair`
- Operative file: `bridge\gtkb-bridge-dispatcher-deferral-enforcement-repair-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no owner waiver line is cited. Clauses with `enforcement_mode = "advisory"`
are reported but never gate._
```
