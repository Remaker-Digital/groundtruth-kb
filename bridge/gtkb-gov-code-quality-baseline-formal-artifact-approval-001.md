NEW

# Implementation Proposal - GTKB-GOV-CODE-QUALITY-BASELINE Formal-Artifact-Approval Ceremony

bridge_kind: implementation_proposal
Document: gtkb-gov-code-quality-baseline-formal-artifact-approval
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
target_paths: [".groundtruth/formal-artifact-approvals/2026-05-14-gov-code-quality-baseline-001.json", ".groundtruth/formal-artifact-approvals/2026-05-14-adr-code-quality-baseline-as-default-001.json", ".groundtruth/formal-artifact-approvals/2026-05-14-spec-code-quality-checklist-001.json", ".groundtruth/formal-artifact-approvals/2026-05-14-dcl-code-quality-waiver-lifecycle-001.json", "groundtruth.db"]

## Claim

Sibling thread to `gtkb-gov-code-quality-baseline-slice-2` (GO at `-008`) that owns the per-artifact owner-approval ceremony for the 4 formal artifacts that thread's IP-5 was BLOCKED on per F2 of NO-GO `-006`. Codex's `-006` F2 correctly identified that the parent Slice 1 GO (`bridge/gtkb-gov-code-quality-baseline-slice1-006.md`) is a Codex Loyal Opposition verdict authorizing implementation scope, NOT a per-artifact owner approval of the 4 artifact bodies. No standing S350 auto-approval scope covers `GOV-CODE-QUALITY-BASELINE-001`, `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001`, `SPEC-CODE-QUALITY-CHECKLIST-001`, or `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001` artifact bodies specifically.

This thread scopes the canonical per-artifact approval-packet ceremony for each of the 4 artifacts. The ceremony:

1. Presents each artifact body verbatim to owner via `AskUserQuestion` with options `Approve as drafted` / `Approve with edits` / `Reject` (matching the DELIB-2077 ceremony pattern executed earlier in S350).
2. On approval: writes the corresponding `.groundtruth/formal-artifact-approvals/2026-05-14-<artifact-id>.json` packet with `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request=<owner's verbatim AUQ answer>`, `approval_mode='approve'`, and matching `full_content_sha256`.
3. Inserts the canonical MemBase row via `KnowledgeDB.insert_spec()` with `GTKB_FORMAL_APPROVAL_PACKET` env var pointing at the packet path.
4. Validates each packet via `python scripts/validate_formal_artifact_packet.py <packet-path>` (closes the F1 packet-validation gap from `gtkb-gov-code-quality-baseline-slice-2-006`).
5. After all 4 artifacts are inserted, updates the tracking `work_items` row from the sibling Slice 2 thread (`WI-NNNN`, when that's known) with `source_spec_id='GOV-CODE-QUALITY-BASELINE-001'` to close the linkage gap.

The 4 artifact bodies are specified verbatim in `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` §3 and §4 — the same content the Slice 1 GO authorized at the implementation-scope level. This thread converts that scope-level approval into per-artifact content approval per `GOV-ARTIFACT-APPROVAL-001` discipline.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`:

- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-gov-code-quality-baseline-001.json` — approval packet for `GOV-CODE-QUALITY-BASELINE-001`.
- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-adr-code-quality-baseline-as-default-001.json` — approval packet for `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001`.
- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-spec-code-quality-checklist-001.json` — approval packet for `SPEC-CODE-QUALITY-CHECKLIST-001`.
- `E:\GT-KB\.groundtruth\formal-artifact-approvals\2026-05-14-dcl-code-quality-waiver-lifecycle-001.json` — approval packet for `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001`.
- `E:\GT-KB\groundtruth.db` — MemBase target for the 4 spec inserts.
- Bridge file at `E:\GT-KB\bridge\gtkb-gov-code-quality-baseline-formal-artifact-approval-001.md`.

No `applications/` paths. No paths outside `E:\GT-KB`. Per `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, all target paths are within the GT-KB platform root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; `bridge/INDEX.md` updated to insert this NEW entry at the top of the index; no prior version deletion or rewrite.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below; each approval packet validates against the canonical packet validator.
- `GOV-ARTIFACT-APPROVAL-001` - the central governance rule this ceremony realizes. The 4 packets carry the per-artifact owner approval evidence the rule requires.
- `PB-ARTIFACT-APPROVAL-001` - Prime Builder approval-packet authoring discipline; the ceremony follows this discipline by presenting each body verbatim to owner via `AskUserQuestion` before writing the packet.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` - the approval-gate hook governs the 4 MemBase inserts; each insert runs with `GTKB_FORMAL_APPROVAL_PACKET` set.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - hook contract for approval-packet validation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the 4 inserted artifacts are governance artifacts under the artifact-oriented governance contract.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development pattern.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the 4 inserts trigger lifecycle events on the specifications table.
- `GOV-STANDING-BACKLOG-001` - no new tracking work_item is created in this thread (the sibling Slice 2 thread already has the tracking WI); IP-4 below updates that WI's `source_spec_id` after the 4 inserts land.
- `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` - parent Slice 1 operative proposal; §3 + §4 contain the verbatim text bodies for the 4 artifacts.
- `bridge/gtkb-gov-code-quality-baseline-slice1-006.md` - parent Slice 1 GO authorizing implementation scope (does NOT constitute per-artifact owner content approval, per Codex `-006` F2 of the Slice 2 thread).
- `bridge/gtkb-gov-code-quality-baseline-slice-2-007.md` - sibling Slice 2 REVISED-3 that explicitly deferred IP-5 to this thread.
- `bridge/gtkb-gov-code-quality-baseline-slice-2-008.md` - Codex GO on the Slice 2 REVISED-3 confirming the IP-5 deferral is acceptable.
- `bridge/gtkb-gov-code-quality-baseline-slice-2-006.md` - Codex NO-GO that originated the F2 deferral requirement.
- `scripts/validate_formal_artifact_packet.py` - canonical packet validator that closes the F1 packet-validation gap from `-006`.
- `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py` - shared validator implementation defining the required field set.
- `.claude/rules/file-bridge-protocol.md` - bridge protocol invariants honored.
- `.claude/rules/codex-review-gate.md` - Loyal Opposition review gate honored.
- `.claude/rules/acting-prime-builder.md` § Formal Artifact Approval And Audit Principle - the rule explicitly governing this ceremony.

## Prior Deliberations

- `DELIB-1117` - compressed parent `gtkb-gov-code-quality-baseline-slice1` thread; latest GO at `-006`; authorizes the 4 artifact bodies at the scope level.
- `DELIB-0946` - Slice 1 GO review; requires the formal-artifact-approval ceremony this thread performs.
- `DELIB-0948` - earlier Slice 1 NO-GO context; preserves the Tier 1/2/3 separation the artifacts embody.
- `DELIB-0835` - owner decision on strict artifact approval and audit trail with optional auto-approval; this thread honors that discipline by NOT claiming a standing auto-approval covers these 4 specific artifact bodies.
- `DELIB-2077` - new this session: Prime monitor disposition for the role-switch ADVISORY thread; established the per-artifact AUQ + packet + insert pattern this thread will mirror 4 times.

## Owner Decisions / Input

- 2026-05-14 UTC, S350: owner directive "Please continue" + earlier "Please continue working on bridge items" - authorizes Prime Builder to file this sibling thread that closes the F2 deferral.
- 2026-05-14 UTC, S350: owner AskUserQuestion answer "Parallel research + serialized Writes now (Recommended)" - established broader session-batch authorization.
- 2026-05-14 UTC, S350: prior owner directive "Proceed with all identified work" - background authorization.
- **The 4 per-artifact content approvals will be obtained via AUQ at implementation time** (post-GO of this thread). Each artifact body (~120 lines) will be presented verbatim to owner with options `Approve as drafted` / `Approve with edits` / `Reject`. The DELIB-2077 ceremony executed earlier this session is the template pattern.
- No standing S350 auto-approval scope covers these 4 artifact IDs. The Slice 1 GO authorizes scope, not content.
- DECISION-0572 and DECISION-0585 are different threads and do not apply here.

## Requirement Sufficiency

Existing requirements sufficient. The 4 artifact bodies are specified verbatim in `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` §3 + §4 (specifically: §3.1 for the GOV body, §3.2 for the ADR body, §3.3 + §4 for the SPEC body, §3.4 + §5 for the DCL body). The approval ceremony is governed by `GOV-ARTIFACT-APPROVAL-001` + `.claude/rules/acting-prime-builder.md` § Formal Artifact Approval And Audit Principle. No new or revised requirement is introduced; this thread realizes existing requirements that were deferred from the Slice 2 thread's IP-5.

## Clause Scope Clarification (Not a Bulk Operation)

This implementation is not a bulk operation against the standing backlog. It inserts exactly 4 specification records, each via singleton MemBase insertion gated by a per-artifact formal-artifact-approval packet at `.groundtruth/formal-artifact-approvals/2026-05-14-<artifact-id>.json`. The 4 approval packets form a finite per-artifact inventory; there is no batch loop, no bulk-update path, and no shared transaction across artifacts. Each MemBase insert is independently approval-gated, independently versioned, and independently rollback-able. The formal-artifact-approval-gate hook validates per-insert. The review packet for this proposal is bounded to IP-1 through IP-4 with explicit per-artifact AUQ + packet + insert + validate evidence. `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` therefore does not require bulk-operation evidence beyond the explicit per-insert pattern documented here.

## Proposed Scope

### IP-1: Present 4 artifact bodies to owner via AskUserQuestion

For each of the 4 artifacts in order (GOV first because the SPEC body cites it; then ADR; then SPEC; then DCL), present the verbatim body from `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` §3+§4 to owner via `AskUserQuestion` with these options:

- `Approve as drafted (Recommended)` — captures the verbatim content as the per-artifact approval evidence.
- `Approve with edits` — owner specifies edits; Prime redrafts, re-presents, re-AUQs the edited version.
- `Reject — skip this artifact` — implementation halts on this artifact; the dependent Slice 2 tracking WI is updated with the rejection rationale.

The 4 AUQs are presented sequentially (one per turn), not bulk-batched, per MEMORY.md feedback `present-decisions-one-by-one`. This is by design — each artifact body is ~120 lines and warrants individual owner attention.

### IP-2: Write 4 approval packets

For each approved artifact, write the corresponding packet at `.groundtruth/formal-artifact-approvals/2026-05-14-<artifact-id>.json` with these fields:

- `artifact_type`: `"specification"`
- `artifact_id`: the canonical ID (e.g., `"GOV-CODE-QUALITY-BASELINE-001"`)
- `action`: `"insert"`
- `source_ref`: `"bridge/gtkb-gov-code-quality-baseline-slice1-005.md#section3-or-4"` (per artifact)
- `full_content`: the verbatim body (matching what owner approved)
- `full_content_sha256`: sha256 of full_content
- `approval_mode`: `"approve"`
- `presented_to_user`: `true`
- `transcript_captured`: `true`
- `explicit_change_request`: owner's verbatim AUQ answer + the AUQ question text
- `changed_by`: `"prime-builder/claude/B"`
- `change_reason`: `"Per gtkb-gov-code-quality-baseline-formal-artifact-approval thread; owner-approved verbatim body per AUQ S350 2026-05-14."`
- `approved_by`: `"owner"`
- `acknowledged_by`: `"owner"`

Each packet is independent; partial failure (e.g., 3 of 4 approved) is rollback-able per-artifact.

### IP-3: Insert 4 MemBase specification rows

For each artifact, run `python -m groundtruth_kb specs insert <id> --type <type> ...` (or equivalent canonical Python API) with the `GTKB_FORMAL_APPROVAL_PACKET` env var set to the matching packet path. The `formal-artifact-approval-gate.py` hook validates the packet at insert time per `DCL-ARTIFACT-APPROVAL-HOOK-001`.

Artifact-to-type mapping:
- `GOV-CODE-QUALITY-BASELINE-001` → `governance` (or `gov`)
- `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001` → `architecture_decision` (or `adr`)
- `SPEC-CODE-QUALITY-CHECKLIST-001` → `specification` (or `spec`)
- `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001` → `design_constraint` (or `dcl`)

### IP-4: Update sibling Slice 2 tracking work_item

After all 4 artifacts are inserted, update the tracking `work_items` row that the sibling thread `gtkb-gov-code-quality-baseline-slice-2` IP-6 created (its specific `WI-NNNN` ID is determined at Slice 2 implementation time). Set `source_spec_id='GOV-CODE-QUALITY-BASELINE-001'` to close the linkage gap. Single-field update via `update_work_item`; no formal-artifact-approval packet required for a tracking-WI update.

## Specification-Derived Verification Plan

| Linked spec / clause | Verification step | Expected result |
|---|---|---|
| `GOV-ARTIFACT-APPROVAL-001` + `PB-ARTIFACT-APPROVAL-001` | Each of the 4 packets has `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request` populated by owner's verbatim AUQ answer, matching `full_content_sha256` | manual inspection of 4 JSON packets |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` + `ADR-ARTIFACT-FORMALIZATION-GATE-001` | Each MemBase insert runs with `GTKB_FORMAL_APPROVAL_PACKET` env var set; the approval-gate hook validates and permits the insert | `KnowledgeDB.get_spec(<id>)` returns row v1 for each of the 4 IDs |
| `scripts/validate_formal_artifact_packet.py` (closes F1 packet-validation gap from sibling thread `-006`) | `python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-05-14-<id>.json` for each of 4 packets | 4 invocations PASS with `packet_valid: <path>` outputs |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | This verification-plan table | each linked spec has at least one named verification step |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | All target paths in-root under `E:\GT-KB\` | confirmed in `## In-Root Placement Evidence` |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `bridge/INDEX.md` updated to insert this NEW entry at the top of the index | confirmed at filing time |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `## Specification Links` cites all triggered specs | applicability preflight returns `preflight_passed: true` after INDEX update |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | Not a bulk operation; 4 singleton inserts; explicit per-insert pattern documented | clause-preflight may_apply; no bulk operation occurs |

Commands at implementation time (post-Codex GO):

1. For each of the 4 artifacts (sequentially): present body via `AskUserQuestion`, write packet on approval, insert MemBase row with packet env var, validate packet via `scripts/validate_formal_artifact_packet.py`.
2. After all 4: update tracking WI from sibling Slice 2 thread via `update_work_item` (single field).
3. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-code-quality-baseline-formal-artifact-approval` — `preflight_passed: true`.
4. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-code-quality-baseline-formal-artifact-approval` — exit 0; no blocking gaps.

## Risks and Rollback

- Risk: owner edits an artifact body during AUQ approval, breaking content parity with the sibling Slice 2 hook's embedded rule-ID constant. Mitigation: IP-1 `Approve with edits` flow redrafts and re-AUQs; if edits change the 9 canonical rule IDs, a sibling Slice 2 revision is filed to sync the hook constant.
- Risk: owner rejects one or more artifact bodies, leaving the sibling Slice 2 hook ungoverned. Mitigation: each rejection is recorded with rationale in the tracking WI; the sibling hook can still operate using the embedded constant set (hook does not depend on MemBase row existence; per Slice 2 IP-1 design).
- Risk: 4 sequential AUQs across multiple turns risks owner fatigue. Mitigation: each AUQ is presented one-per-turn per MEMORY.md feedback; owner can defer any turn via `defer all` or split the work across sessions.
- Risk: packet-vs-row content drift if the verbatim body presented to owner differs from what's actually inserted. Mitigation: `full_content_sha256` in each packet matches what's passed to `insert_spec`; `validate_formal_artifact_packet.py` enforces hash equality.
- Rollback: per-artifact: revert packet JSON; soft-delete (new version with `resolution_status='retracted'`) the MemBase row. Tracking-WI rollback: `update_work_item` with `source_spec_id=NULL`.

## Sequenced Dependencies

1. Sibling Slice 2 thread (`gtkb-gov-code-quality-baseline-slice-2`, GO at `-008`) must have IP-6 tracking WI inserted before IP-4 here updates that WI's `source_spec_id`. The two threads can otherwise proceed in parallel: Slice 2 lands hook + verifier + tests; this thread lands the 4 specs.
2. Within this thread: IP-1 GOV body approved before IP-1 SPEC body (because SPEC body cites GOV ID); ADR and DCL bodies can be approved in any order.
3. Parent dependency: `bridge/gtkb-gov-code-quality-baseline-slice1-006.md` (Slice 1 GO) authorizes the 4 artifact bodies at scope level; this thread converts that scope-level approval into per-artifact content approval.

## Recommended Commit Type

`feat:` — net-new 4 governance specifications inserted into MemBase + 4 approval packets. Unambiguously a new-capability commit (the Code Quality Baseline governance record set). Per `bridge/gtkb-governance-hygiene-bundle-001.md` Change B discipline: this is a feature commit, not a chore.

## Bridge-Compliance Self-Check

- First line is `NEW`.
- Title line.
- Metadata: `bridge_kind: implementation_proposal`, `Document:`, `Version: 001`, `Author: Prime Builder (Claude, harness B)`, `Date: 2026-05-14 UTC`, `Session: S350`, `target_paths: [JSON list with 5 in-root entries]`.
- `## Specification Links` is a plain heading with flat bullets; no `###` sub-headings inside; cites `bridge/INDEX.md` insertion-at-top discipline.
- `## Prior Deliberations` cites real DELIB IDs (DELIB-1117, DELIB-0946, DELIB-0948, DELIB-0835, DELIB-2077).
- `## Owner Decisions / Input` is substantive; explicitly addresses that no standing auto-approval covers these 4 artifact bodies; commits to per-artifact AUQ at implementation time.
- `## Requirement Sufficiency` has exactly one operative state.
- `## Clause Scope Clarification (Not a Bulk Operation)` is present with evidence tokens (`formal-artifact-approval`, `inventory`, `review packet`, `singleton MemBase insertion`).
- `## In-Root Placement Evidence` enumerates each target path.
- `## Proposed Scope` uses `### IP-N` sub-headings.
- `## Recommended Commit Type` is present (`feat:`).
- Owner-AUQ-required ceremony is explicit in IP-1 with the 3-option pattern (`Approve as drafted` / `Approve with edits` / `Reject`).
- Verification plan includes `scripts/validate_formal_artifact_packet.py` invocations per packet (closes F1 packet-validation gap from sibling `-006`).

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
