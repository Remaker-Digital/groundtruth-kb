REVISED

# Implementation Proposal - GTKB-GOV-CODE-QUALITY-BASELINE Formal-Artifact-Approval Ceremony

bridge_kind: prime_proposal
Document: gtkb-gov-code-quality-baseline-formal-artifact-approval
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: GTKB-GOV-CODE-QUALITY-BASELINE

target_paths: [".groundtruth/formal-artifact-approvals/2026-05-14-gov-code-quality-baseline-001.json", ".groundtruth/formal-artifact-approvals/2026-05-14-adr-code-quality-baseline-as-default-001.json", ".groundtruth/formal-artifact-approvals/2026-05-14-spec-code-quality-checklist-001.json", ".groundtruth/formal-artifact-approvals/2026-05-14-dcl-code-quality-waiver-lifecycle-001.json", "groundtruth.db"]

## Revision Notes

-003 addresses the `-002` NO-GO findings:

- **F1 (P1) — approval packets specified with an invalid `artifact_type`.** The `-001` proposal's IP-2 instructed Prime to write every packet with `artifact_type: "specification"`. The live shared validator (`groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:26-33`) accepts only `deliberation`, `governance`, `requirement`, `protected_behavior`, `architecture_decision`, and `design_constraint`; `"specification"` is rejected. -003 assigns each packet a validator-accepted type matching the artifact's actual formal-artifact class:
  - `GOV-CODE-QUALITY-BASELINE-001` → `governance`
  - `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001` → `architecture_decision`
  - `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001` → `design_constraint`
  - `SPEC-CODE-QUALITY-CHECKLIST-001` → `requirement`
  IP-2 and the IP-3 artifact-to-type mapping are both corrected and made consistent; the per-packet `artifact_type` is now drawn from this table, not the single literal `"specification"`. Row-vs-packet content-identity checks are added to the verification plan for all four inserts.
- **F2 (P2) — sibling tracking-WI dependency needs a fail-closed precondition.** The `-001` IP-4 updated a sibling Slice 2 tracking work item whose ID was not yet known, with no stated behavior if the row is absent. -003 adds an explicit IP-4 fail-closed precondition: resolve the exact tracking-WI ID from live MemBase before any update; if no such WI exists, skip IP-4 entirely, record the skip, and file a follow-up work item rather than inventing or guessing an ID.
- **Project-linkage metadata added.** `-001` predated the `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` linkage requirement. -003 adds the `Project Authorization` / `Project` / `Work Item` metadata block. The values are verified against live MemBase: `PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH` is `active`, its `project_id` is `PROJECT-GTKB-GOVERNANCE-HARDENING`, and its `included_work_item_ids` list contains `GTKB-GOV-CODE-QUALITY-BASELINE` — the work item this ceremony advances.

No technical-scope change beyond the F1 packet-type correction and the F2 fail-closed precondition: the ceremony still presents the four artifact bodies verbatim to the owner via AskUserQuestion, writes four per-artifact approval packets, and inserts four MemBase rows.

## Claim

Sibling thread to `gtkb-gov-code-quality-baseline-slice-2` (GO at `-008`) that owns the per-artifact owner-approval ceremony for the 4 formal artifacts that thread's IP-5 was BLOCKED on per F2 of NO-GO `-006`. Codex's `-006` F2 correctly identified that the parent Slice 1 GO (`bridge/gtkb-gov-code-quality-baseline-slice1-006.md`) is a Codex Loyal Opposition verdict authorizing implementation scope, NOT a per-artifact owner approval of the 4 artifact bodies. No standing S350 auto-approval scope covers `GOV-CODE-QUALITY-BASELINE-001`, `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001`, `SPEC-CODE-QUALITY-CHECKLIST-001`, or `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001` artifact bodies specifically.

This thread scopes the canonical per-artifact approval-packet ceremony for each of the 4 artifacts. The ceremony:

1. Presents each artifact body verbatim to owner via `AskUserQuestion` with options `Approve as drafted` / `Approve with edits` / `Reject` (matching the DELIB-2077 ceremony pattern executed earlier in S350).
2. On approval: writes the corresponding `.groundtruth/formal-artifact-approvals/2026-05-14-<artifact-id>.json` packet with `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request=<owner's verbatim AUQ answer>`, `approval_mode='approve'`, the validator-accepted per-artifact `artifact_type` (see IP-2), and matching `full_content_sha256`.
3. Inserts the canonical MemBase row via `KnowledgeDB.insert_spec()` with `GTKB_FORMAL_APPROVAL_PACKET` env var pointing at the packet path.
4. Validates each packet via `python scripts/validate_formal_artifact_packet.py <packet-path>` (closes the F1 packet-validation gap from `gtkb-gov-code-quality-baseline-slice-2-006`).
5. After all 4 artifacts are inserted, conditionally updates the tracking `work_items` row from the sibling Slice 2 thread per the IP-4 fail-closed precondition below.

The 4 artifact bodies are specified verbatim in `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` §3 and §4 — the same content the Slice 1 GO authorized at the implementation-scope level. This thread converts that scope-level approval into per-artifact content approval per `GOV-ARTIFACT-APPROVAL-001` discipline.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`:

- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-gov-code-quality-baseline-001.json` — approval packet for `GOV-CODE-QUALITY-BASELINE-001`.
- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-adr-code-quality-baseline-as-default-001.json` — approval packet for `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001`.
- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-spec-code-quality-checklist-001.json` — approval packet for `SPEC-CODE-QUALITY-CHECKLIST-001`.
- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-dcl-code-quality-waiver-lifecycle-001.json` — approval packet for `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001`.
- `E:\GT-KB\groundtruth.db` — MemBase target for the 4 spec inserts.
- Bridge file at `E:\GT-KB\bridge\gtkb-gov-code-quality-baseline-formal-artifact-approval-003.md`.

No `applications/` paths. No paths outside `E:\GT-KB`. Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, all target paths are within the GT-KB platform root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; `bridge/INDEX.md` updated to insert this REVISED entry at the top of the thread's entry; no prior version deletion or rewrite.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes the Project Authorization / Project / Work Item linkage metadata block, verified against live MemBase.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below; each approval packet validates against the canonical packet validator, plus row-vs-packet content-identity checks.
- `GOV-ARTIFACT-APPROVAL-001` - the central governance rule this ceremony realizes. The 4 packets carry the per-artifact owner approval evidence the rule requires.
- `PB-ARTIFACT-APPROVAL-001` - Prime Builder approval-packet authoring discipline; the ceremony follows this discipline by presenting each body verbatim to owner via `AskUserQuestion` before writing the packet.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` - the approval-gate hook governs the 4 MemBase inserts; each insert runs with `GTKB_FORMAL_APPROVAL_PACKET` set.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - hook contract for approval-packet validation; the corrected per-artifact `artifact_type` values pass this validation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the 4 inserted artifacts are governance artifacts under the artifact-oriented governance contract.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development pattern.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the 4 inserts trigger lifecycle events on the specifications table.
- `GOV-STANDING-BACKLOG-001` - no new tracking work_item is created in this thread (the sibling Slice 2 thread already has the tracking WI); IP-4 below conditionally updates that WI's `source_spec_id` after the 4 inserts land, under a fail-closed precondition.
- `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` - parent Slice 1 operative proposal; §3 + §4 contain the verbatim text bodies for the 4 artifacts.
- `bridge/gtkb-gov-code-quality-baseline-slice1-006.md` - parent Slice 1 GO authorizing implementation scope (does NOT constitute per-artifact owner content approval, per Codex `-006` F2 of the Slice 2 thread).
- `bridge/gtkb-gov-code-quality-baseline-slice-2-007.md` - sibling Slice 2 REVISED-3 that explicitly deferred IP-5 to this thread.
- `bridge/gtkb-gov-code-quality-baseline-slice-2-008.md` - Codex GO on the Slice 2 REVISED-3 confirming the IP-5 deferral is acceptable.
- `bridge/gtkb-gov-code-quality-baseline-slice-2-006.md` - Codex NO-GO that originated the F2 deferral requirement.
- `scripts/validate_formal_artifact_packet.py` - canonical packet validator that closes the F1 packet-validation gap from `-006`.
- `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py` - shared validator implementation; `VALID_ARTIFACT_TYPES` (lines 26-33) defines the accepted `artifact_type` set the corrected IP-2 conforms to.
- `.claude/rules/file-bridge-protocol.md` - bridge protocol invariants honored.
- `.claude/rules/codex-review-gate.md` - Loyal Opposition review gate honored.
- `.claude/rules/acting-prime-builder.md` § Formal Artifact Approval And Audit Principle - the rule explicitly governing this ceremony.

## Prior Deliberations

- `DELIB-1117` - compressed parent `gtkb-gov-code-quality-baseline-slice1` thread; latest GO at `-006`; authorizes the 4 artifact bodies at the scope level.
- `DELIB-0946` - Slice 1 GO review; requires the formal-artifact-approval ceremony this thread performs.
- `DELIB-0948` - earlier Slice 1 NO-GO context; preserves the Tier 1/2/3 separation the artifacts embody.
- `DELIB-0835` - owner decision on strict artifact approval and audit trail with optional auto-approval; this thread honors that discipline by NOT claiming a standing auto-approval covers these 4 specific artifact bodies.
- `DELIB-2077` - Prime monitor disposition for the role-switch ADVISORY thread; established the per-artifact AUQ + packet + insert pattern this thread mirrors 4 times.

The `-002` Codex review's deliberation search found no owner decision permitting `artifact_type: "specification"` in approval packets; -003's F1 correction conforms each packet to the live `VALID_ARTIFACT_TYPES` set instead.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner directive "Please continue" + earlier "Please continue working on bridge items" - authorizes Prime Builder to file this sibling thread that closes the F2 deferral.
- 2026-05-14 UTC, S350: owner AskUserQuestion answer "Parallel research + serialized Writes now (Recommended)" - established broader session-batch authorization.
- 2026-05-14 UTC, S350: prior owner directive "Proceed with all identified work" - background authorization.
- Project-scoped owner authorization: `PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH` (active) authorizes the `PROJECT-GTKB-GOVERNANCE-HARDENING` project and lists `GTKB-GOV-CODE-QUALITY-BASELINE` in its `included_work_item_ids`. This project authorization is additive to (not a substitute for) the per-artifact formal-artifact-approval packets below.
- **The 4 per-artifact content approvals will be obtained via AUQ at implementation time** (post-GO of this thread). Each artifact body (~120 lines) will be presented verbatim to owner with options `Approve as drafted` / `Approve with edits` / `Reject`. The DELIB-2077 ceremony executed earlier this session is the template pattern.
- No standing S350 auto-approval scope covers these 4 artifact IDs. The Slice 1 GO authorizes scope, not content; the project authorization authorizes the project, not the per-artifact bodies.
- DECISION-0572 and DECISION-0585 are different threads and do not apply here.
- The `-002` NO-GO findings (F1 invalid `artifact_type`, F2 missing fail-closed precondition) are proposal-scope corrections, not new owner-decision scope; -003 requires no new owner decision beyond the per-artifact AUQ ceremony already committed above.

## Requirement Sufficiency

Existing requirements sufficient. The 4 artifact bodies are specified verbatim in `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` §3 + §4 (specifically: §3.1 for the GOV body, §3.2 for the ADR body, §3.3 + §4 for the SPEC body, §3.4 + §5 for the DCL body). The approval ceremony is governed by `GOV-ARTIFACT-APPROVAL-001` + `.claude/rules/acting-prime-builder.md` § Formal Artifact Approval And Audit Principle. No new or revised requirement is introduced; this thread realizes existing requirements that were deferred from the Slice 2 thread's IP-5. The F1 correction conforms the packet schema to the existing validator contract; it introduces no new requirement.

## Clause Scope Clarification (Not a Bulk Operation)

This implementation is not a bulk operation against the standing backlog. It inserts exactly 4 specification records, each via singleton MemBase insertion gated by a per-artifact formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-14-<artifact-id>.json`. The 4 approval packets form a finite per-artifact inventory; there is no batch loop, no bulk-update path, and no shared transaction across artifacts. Each MemBase insert is independently approval-gated, independently versioned, and independently rollback-able. The formal-artifact-approval-gate hook validates per-insert. The review packet for this proposal is bounded to IP-1 through IP-4 with explicit per-artifact AUQ + packet + insert + validate evidence. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` therefore does not require bulk-operation evidence beyond the explicit per-insert pattern documented here.

## Proposed Scope

### IP-1: Present 4 artifact bodies to owner via AskUserQuestion

For each of the 4 artifacts in order (GOV first because the SPEC body cites it; then ADR; then SPEC; then DCL), present the verbatim body from `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` §3+§4 to owner via `AskUserQuestion` with these options:

- `Approve as drafted (Recommended)` — captures the verbatim content as the per-artifact approval evidence.
- `Approve with edits` — owner specifies edits; Prime redrafts, re-presents, re-AUQs the edited version.
- `Reject — skip this artifact` — implementation halts on this artifact; the dependent Slice 2 tracking WI is updated with the rejection rationale (subject to the IP-4 fail-closed precondition below).

The 4 AUQs are presented sequentially (one per turn), not bulk-batched, per MEMORY.md feedback `present-decisions-one-by-one`. This is by design — each artifact body is ~120 lines and warrants individual owner attention.

### IP-2: Write 4 approval packets

For each approved artifact, write the corresponding packet at `.groundtruth/formal-artifact-approvals/2026-05-14-<artifact-id>.json` with these fields:

- `artifact_type`: the validator-accepted per-artifact type drawn from this table (NOT the literal `"specification"` — see Revision Notes F1):
  - `GOV-CODE-QUALITY-BASELINE-001` → `"governance"`
  - `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001` → `"architecture_decision"`
  - `SPEC-CODE-QUALITY-CHECKLIST-001` → `"requirement"`
  - `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001` → `"design_constraint"`
  Every value is a member of `VALID_ARTIFACT_TYPES` in `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:26-33`.
- `artifact_id`: the canonical ID (e.g., `"GOV-CODE-QUALITY-BASELINE-001"`).
- `action`: `"insert"`.
- `source_ref`: `"bridge/gtkb-gov-code-quality-baseline-slice1-005.md#section3-or-4"` (per artifact).
- `full_content`: the verbatim body (matching what owner approved).
- `full_content_sha256`: sha256 of full_content.
- `approval_mode`: `"approve"`.
- `presented_to_user`: `true`.
- `transcript_captured`: `true`.
- `explicit_change_request`: owner's verbatim AUQ answer + the AUQ question text.
- `changed_by`: `"prime-builder/claude/B"`.
- `change_reason`: `"Per gtkb-gov-code-quality-baseline-formal-artifact-approval thread; owner-approved verbatim body per AUQ; packet .groundtruth/formal-artifact-approvals/2026-05-14-<artifact-id>.json."`
- `approved_by`: `"owner"`.
- `acknowledged_by`: `"owner"`.

Each packet is independent; partial failure (e.g., 3 of 4 approved) is rollback-able per-artifact.

### IP-3: Insert 4 MemBase specification rows

For each artifact, run `python -m groundtruth_kb specs insert <id> --type <spec-type> ...` (or the equivalent canonical Python API `KnowledgeDB.insert_spec()`) with the `GTKB_FORMAL_APPROVAL_PACKET` env var set to the matching packet path. The `formal-artifact-approval-gate.py` hook validates the packet at insert time per `DCL-ARTIFACT-APPROVAL-HOOK-001`.

Artifact-to-spec-type mapping (the MemBase `specifications.type` value; consistent with the packet `artifact_type` from IP-2):

- `GOV-CODE-QUALITY-BASELINE-001` → spec type `governance`
- `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001` → spec type `architecture_decision`
- `SPEC-CODE-QUALITY-CHECKLIST-001` → spec type `requirement`
- `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001` → spec type `design_constraint`

### IP-4: Conditionally update sibling Slice 2 tracking work_item (fail-closed)

After all 4 artifacts are inserted, attempt to update the tracking `work_items` row that the sibling thread `gtkb-gov-code-quality-baseline-slice-2` IP-6 created, setting `source_spec_id='GOV-CODE-QUALITY-BASELINE-001'` to close the linkage gap.

**Fail-closed precondition (per `-002` F2):**

1. Before any update, resolve the exact tracking-WI ID from live MemBase: query `work_items` for the row created by the Slice 2 IP-6 (e.g., the WI whose `change_reason` or `project_name` cites the `gtkb-gov-code-quality-baseline-slice-2` thread). The exact ID is read from live MemBase, never invented or guessed.
2. If the tracking WI exists: perform the single-field `update_work_item` setting `source_spec_id='GOV-CODE-QUALITY-BASELINE-001'`, and cite the exact resolved WI ID in the implementation report. No formal-artifact-approval packet is required for a tracking-WI `source_spec_id` update.
3. If no such tracking WI exists in live MemBase: **skip IP-4 entirely.** Do not invent a WI ID and do not block. Record the skip in the implementation report and file a follow-up work item (or note the linkage as a follow-on) so the `source_spec_id` linkage is closed once the sibling Slice 2 thread's tracking WI lands.

IP-4 is non-blocking for IP-1 through IP-3: the four artifact inserts complete and are verifiable independently of the tracking-WI linkage.

## Specification-Derived Verification Plan

| Linked spec / clause | Verification step | Expected result |
|---|---|---|
| `GOV-ARTIFACT-APPROVAL-001` + `PB-ARTIFACT-APPROVAL-001` | Each of the 4 packets has `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request` populated by owner's verbatim AUQ answer, matching `full_content_sha256`, and a `VALID_ARTIFACT_TYPES`-member `artifact_type` | manual inspection of 4 JSON packets |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` + `ADR-ARTIFACT-FORMALIZATION-GATE-001` | Each MemBase insert runs with `GTKB_FORMAL_APPROVAL_PACKET` env var set; the approval-gate hook validates and permits the insert (the corrected per-artifact `artifact_type` passes validation) | `KnowledgeDB.get_spec(<id>)` returns row v1 for each of the 4 IDs |
| `scripts/validate_formal_artifact_packet.py` (closes F1 packet-validation gap; `-002` F1 invalid-type fix) | `python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-05-14-<id>.json` for each of 4 packets | 4 invocations PASS — each packet's `artifact_type` is validator-accepted |
| `-002` F1 — row-vs-packet content identity | For each of the 4 inserts, confirm the MemBase row body equals the packet `full_content` and the row hashes to the packet `full_content_sha256` | 4 row-vs-packet content-identity checks PASS |
| `-002` F2 — IP-4 fail-closed precondition | Resolve the sibling tracking WI from live MemBase; if present, the report cites the exact ID; if absent, IP-4 is skipped and a follow-up is recorded | implementation report shows either the cited WI ID + update, or the documented skip + follow-up |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | This verification-plan table | each linked spec/clause has at least one named verification step |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | All target paths in-root under `E:\GT-KB\` | confirmed in `## In-Root Placement Evidence` |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `bridge/INDEX.md` updated to insert this REVISED entry at the top of the thread's entry | confirmed at filing time; see `## Bridge INDEX Maintenance` |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `## Specification Links` cites all triggered specs | applicability preflight returns `preflight_passed: true` after INDEX update |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | Not a bulk operation; 4 singleton inserts; explicit per-insert pattern documented | clause-preflight must_apply with evidence; no bulk operation occurs |

Commands at implementation time (post-Codex GO):

1. For each of the 4 artifacts (sequentially): present body via `AskUserQuestion`, write packet (with the validator-accepted per-artifact `artifact_type`) on approval, insert MemBase row with packet env var, validate packet via `scripts/validate_formal_artifact_packet.py`, confirm row-vs-packet content identity.
2. After all 4: run the IP-4 fail-closed precondition — resolve the sibling tracking WI from live MemBase, then conditionally `update_work_item` or skip + file follow-up.
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-code-quality-baseline-formal-artifact-approval` — `preflight_passed: true`.
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-code-quality-baseline-formal-artifact-approval` — exit 0; no blocking gaps.

## Risks and Rollback

- Risk: owner edits an artifact body during AUQ approval, breaking content parity with the sibling Slice 2 hook's embedded rule-ID constant. Mitigation: IP-1 `Approve with edits` flow redrafts and re-AUQs; if edits change the 9 canonical rule IDs, a sibling Slice 2 revision is filed to sync the hook constant.
- Risk: owner rejects one or more artifact bodies, leaving the sibling Slice 2 hook ungoverned. Mitigation: each rejection is recorded with rationale in the tracking WI (subject to the IP-4 fail-closed precondition); the sibling hook can still operate using the embedded constant set (hook does not depend on MemBase row existence; per Slice 2 IP-1 design).
- Risk: 4 sequential AUQs across multiple turns risks owner fatigue. Mitigation: each AUQ is presented one-per-turn per MEMORY.md feedback; owner can defer any turn or split the work across sessions.
- Risk: packet-vs-row content drift if the verbatim body presented to owner differs from what's actually inserted. Mitigation: `full_content_sha256` in each packet matches what's passed to `insert_spec`; `validate_formal_artifact_packet.py` enforces hash equality; the verification plan adds an explicit row-vs-packet content-identity check.
- Risk (F2): the sibling tracking WI does not exist when IP-4 runs. Mitigation: the IP-4 fail-closed precondition resolves the ID from live MemBase and skips + files a follow-up if absent — no invented ID, no mid-implementation block.
- Rollback: per-artifact: revert packet JSON; soft-delete (new version with `resolution_status='retracted'`) the MemBase row. Tracking-WI rollback: `update_work_item` with `source_spec_id=NULL`.

## Sequenced Dependencies

1. Sibling Slice 2 thread (`gtkb-gov-code-quality-baseline-slice-2`, GO at `-008`) should have its IP-6 tracking WI inserted before IP-4 here updates that WI's `source_spec_id`; the IP-4 fail-closed precondition handles the case where it has not. The two threads can otherwise proceed in parallel: Slice 2 lands hook + verifier + tests; this thread lands the 4 specs.
2. Within this thread: IP-1 GOV body approved before IP-1 SPEC body (because the SPEC body cites the GOV ID); ADR and DCL bodies can be approved in any order.
3. Parent dependency: `bridge/gtkb-gov-code-quality-baseline-slice1-006.md` (Slice 1 GO) authorizes the 4 artifact bodies at scope level; this thread converts that scope-level approval into per-artifact content approval.

## Bridge INDEX Maintenance

This `-003` revision is filed at `bridge/gtkb-gov-code-quality-baseline-formal-artifact-approval-003.md` per the `.claude/rules/file-bridge-protocol.md` File Naming convention. The `bridge/INDEX.md` update inserts a `REVISED: bridge/gtkb-gov-code-quality-baseline-formal-artifact-approval-003.md` line at the top of the existing `Document: gtkb-gov-code-quality-baseline-formal-artifact-approval` entry, above the prior `NO-GO` and `NEW` lines. The prior `-001` and `-002` versions are preserved unchanged — no deletion, no rewrite — consistent with the append-only bridge audit trail. `bridge/INDEX.md` remains the canonical workflow-state authority for this thread.

## Recommended Commit Type

`feat:` — net-new 4 governance specifications inserted into MemBase + 4 approval packets. Unambiguously a new-capability commit (the Code Quality Baseline governance record set). Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline: this is a feature commit, not a chore.

## Applicability Preflight

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-code-quality-baseline-formal-artifact-approval` — run against the `-003` operative file with the INDEX entry in place; exit 0:

```
- packet_hash: sha256:7bce20873d8173e251c4a4d5354f273693609b914dfeb764c6c4c9018e197856
- bridge_document_name: gtkb-gov-code-quality-baseline-formal-artifact-approval
- content_source: indexed_operative
- content_file: bridge/gtkb-gov-code-quality-baseline-formal-artifact-approval-003.md
- operative_file: bridge/gtkb-gov-code-quality-baseline-formal-artifact-approval-003.md
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
```

## Clause Applicability

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-code-quality-baseline-formal-artifact-approval` — run against the `-003` operative file; exit 0; 5 must_apply clauses, 0 evidence gaps, 0 blocking gaps:

```
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
```

| Clause | Applicability | Evidence found |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | must_apply | yes |

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
