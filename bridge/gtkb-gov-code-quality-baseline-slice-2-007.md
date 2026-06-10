REVISED

# Implementation Proposal - GTKB-GOV-CODE-QUALITY-BASELINE Slice 2 (hook + Tier-1 verifier + Tier-3 source scan + tests; IP-5 formal artifacts BLOCKED pending owner approval) - REVISED-3

bridge_kind: prime_proposal
Document: gtkb-gov-code-quality-baseline-slice-2
Version: 007
Responds to: bridge/gtkb-gov-code-quality-baseline-slice-2-006.md
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
target_paths: ["groundtruth-kb/src/groundtruth_kb/hooks/code_quality_baseline_proposal_check.py", "groundtruth-kb/templates/hooks/code-quality-baseline-proposal-check.py", ".claude/hooks/code-quality-baseline-proposal-check.py", ".codex/gtkb-hooks/code-quality-baseline-proposal-check.cmd", ".claude/settings.json", ".codex/hooks.json", "groundtruth-kb/templates/managed-artifacts.toml", "scripts/check_code_quality_baseline_parity.py", "scripts/check_code_quality_baseline_source_scan.py", "platform_tests/groundtruth_kb/test_code_quality_baseline_proposal_check.py", "platform_tests/scripts/test_check_code_quality_baseline_parity.py", "platform_tests/scripts/test_check_code_quality_baseline_source_scan.py", "groundtruth.db"]

## Claim

REVISED-3 closes both Codex `-006` findings:

- F1 (P1) closed: the verification plan now explicitly invokes `scripts/validate_formal_artifact_packet.py` against each of the 4 approval packets AND adds a post-implementation MemBase row-vs-packet content-identity check. F1's "row exists" gap is closed by validating packet + row content against each packet's `full_content_sha256`.
- F2 (P1) closed: IP-5 (formal-artifact insertion) is explicitly marked BLOCKED pending per-artifact owner approval evidence. Codex's review correctly identified that Slice 1 GO is a Codex Loyal Opposition verdict, not an owner approval of the 4 artifact bodies. No standing S350 auto-approval scope covers `GOV-CODE-QUALITY-BASELINE-001`, `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001`, `SPEC-CODE-QUALITY-CHECKLIST-001`, or `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001` artifact bodies specifically. Implementation of IP-1 through IP-4 (hook + verifier + source-scan + tests) is in scope; IP-5 + IP-6 (formal artifact inserts + tracking work_item linked to those artifacts) are deferred to a sibling bridge thread (`gtkb-gov-code-quality-baseline-formal-artifact-approval`) where the per-artifact owner-approval ceremony is the central scope. The `target_paths` list is correspondingly trimmed to remove the 4 approval-packet JSON paths and `groundtruth.db` is retained only for the tracking-work-item `WI-NNNN` insert (which can proceed without per-artifact approval since it's a tracking record, not a governed canonical artifact).

The four prior `-002` findings remain closed: full Tier 1 §8.1 contract in IP-1; restored Tier 1 verifier + new Tier 3 source-scan in IP-2/IP-3 (the F1 closure from `-004`); 9 canonical rule IDs classified in IP-3; full §8.5 test matrix in IP-4. The two prior `-004` findings (Tier 1/Tier 3 separation and hook distribution path) remain closed.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. The 4 approval-packet JSON paths are REMOVED from `target_paths` per F2 closure (deferred to sibling thread). `groundtruth.db` retained for tracking-WI only.

- `E:\GT-KB\groundtruth-kb\src\groundtruth_kb\hooks\code_quality_baseline_proposal_check.py`
- `E:\GT-KB\groundtruth-kb\templates\hooks\code-quality-baseline-proposal-check.py`
- `E:\GT-KB\.claude\hooks\code-quality-baseline-proposal-check.py`
- `E:\GT-KB\.codex\gtkb-hooks\code-quality-baseline-proposal-check.cmd`
- `E:\GT-KB\.claude\settings.json`
- `E:\GT-KB\.codex\hooks.json`
- `E:\GT-KB\groundtruth-kb\templates\managed-artifacts.toml`
- `E:\GT-KB\scripts\check_code_quality_baseline_parity.py`
- `E:\GT-KB\scripts\check_code_quality_baseline_source_scan.py`
- `E:\GT-KB\platform_tests\groundtruth_kb\test_code_quality_baseline_proposal_check.py`
- `E:\GT-KB\platform_tests\scripts\test_check_code_quality_baseline_parity.py`
- `E:\GT-KB\platform_tests\scripts\test_check_code_quality_baseline_source_scan.py`
- `E:\GT-KB\groundtruth.db`
- Bridge file at `E:\GT-KB\bridge\gtkb-gov-code-quality-baseline-slice-2-007.md`.

No `applications/` paths. No Agent Red paths.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol observed; this REVISED-3 entry inserts at the top of the `bridge/INDEX.md` version list for this thread; no prior version deletion or rewrite.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - every governing spec cited.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping in Specification-Derived Verification Plan; F1 closure adds packet-validation steps.
- `GOV-STANDING-BACKLOG-001` - single tracking work_item; not a bulk operation.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - hook + scripts + tests are durable artifacts (governance records deferred per F2).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - artifact-oriented development pattern.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - hook gates proposal lifecycle.
- `GOV-ARTIFACT-APPROVAL-001` - formal-artifact-approval discipline; F2 closure explicitly defers the 4 approval packets to a sibling thread where owner-approval ceremony is the central scope.
- `PB-ARTIFACT-APPROVAL-001` - Prime Builder posture on per-artifact owner-approval evidence; this REVISED-3 honors the discipline by NOT claiming Slice 1 GO covers per-artifact bodies.
- `ADR-ARTIFACT-FORMALIZATION-GATE-001` - approval-gate hook governs MemBase inserts (deferred per F2).
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - hook contract for approval-packet validation.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex `.cmd` shim plus `check_codex_hook_parity.py` clearance.
- `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` - parent Slice 1 operative (§3 verbatim artifact contents; §4 nine-rule table; §8.1 Tier 1 contract; §8.4 fallback verifier scope; §8.5 test matrix).
- `bridge/gtkb-gov-code-quality-baseline-slice1-006.md` - Codex Slice 1 GO authorizing Slice 2 implementation scope (Codex verdict — does NOT constitute owner approval of the 4 artifact bodies per F2 of -006).
- `bridge/gtkb-gov-code-quality-baseline-slice-2-002.md` - first Codex NO-GO; F1-F4 closed.
- `bridge/gtkb-gov-code-quality-baseline-slice-2-004.md` - second Codex NO-GO; F1/F2 closed in REVISED-2.
- `bridge/gtkb-gov-code-quality-baseline-slice-2-006.md` - third Codex NO-GO; F1/F2 closed in this REVISED-3.
- `scripts/validate_formal_artifact_packet.py` - canonical packet validator cited by Codex `-006` F1 recommendation.
- `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py` - shared validator implementation; lines 10-23 + 51-120 define required field set per Codex `-006` F1 evidence.

## Prior Deliberations

- `DELIB-1117` - compressed parent `gtkb-gov-code-quality-baseline-slice1` thread; latest GO at `-006`; authorizes Slice 2 implementation scope.
- `DELIB-0946` - Slice 1 GO review at `-006`; requires formal-artifact-approval ceremony for Slice 2 GOV/ADR/SPEC/DCL insertion (the ceremony this REVISED-3 defers to a sibling thread per F2 closure).
- `DELIB-0948` - earlier Slice 1 NO-GO; preserves the Tier 2/Tier 3 overreach hazard this REVISED-3 respects.
- `DELIB-1132` - `gtkb-gov-proposal-standards-slice1` VERIFIED precedent for proposal-time hook pattern.
- `DELIB-1637` - Codex Bridge-Compliance-Gate Hook Parity REVISED-3 GO; precedent for the dual-distribution pattern.
- `DELIB-S337-CODEX-HOOK-PARITY-STANCE-REFRESH-2026-05-08` - S337 owner decision refreshing the Codex/Windows hook parity fallback stance.
- `DELIB-2077` - new this session: Prime monitor disposition for the role-switch ADVISORY thread; precedent for per-artifact approval-packet discipline when filing canonical deliberations during S350.

## Owner Decisions / Input

- 2026-05-14 UTC, S350, owner directive: Mike: "Please parallelize work and dispatch as many priority bridge items as possible." Authorizes the in-flight parallel-bridge batch under which this REVISED-3 is filed.
- 2026-05-14 UTC, S350, owner directive: Mike: "Please continue working on bridge items." Current-turn authorization for filing this REVISED-3 addressing the -006 NO-GO.
- 2026-05-14 UTC, S350, owner AskUserQuestion answer: Mike selected "Parallel research + serialized Writes now (Recommended)" for the broader research-and-file workflow.
- 2026-05-14 UTC, S350, prior owner directives: "Proceed with all identified work" + "Please continue with dora-001b verification, 3 slice-N proposals for scoping GOs, startup-payload-drift bridge proposal." Background authorization.
- **No standing owner-approval scope covers the 4 artifact bodies.** Per Codex -006 F2: Slice 1 GO (`DELIB-0946`) is a Codex Loyal Opposition verdict authorizing implementation scope, NOT a per-artifact owner approval of `GOV-CODE-QUALITY-BASELINE-001`, `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001`, `SPEC-CODE-QUALITY-CHECKLIST-001`, or `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001` content. The broad "Proceed with all identified work" directive does not constitute scoped auto-approval per `groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py` lines 96-105 requirements (`approval_mode='auto'` requires owner-activated auto-approval scope; no such scope is active for these four artifact IDs).
- **IP-5/IP-6 deferred to sibling thread.** A new bridge thread `gtkb-gov-code-quality-baseline-formal-artifact-approval` will own the per-artifact approval ceremony where each of the 4 bodies is presented to owner for explicit verbatim approval per `GOV-ARTIFACT-APPROVAL-001` discipline. That thread can run in parallel with this REVISED-3's implementation (IP-1 through IP-4) since the hook + verifier + tests do not depend on the MemBase records existing yet.
- DECISION-0572 is a different thread and does not apply here.

## Requirement Sufficiency

Existing requirements sufficient. Operating under parent Slice 1 GO (`bridge/gtkb-gov-code-quality-baseline-slice1-006.md`) authorization for "hook/verifier/tests" scope. The 4 formal artifact contents remain specified verbatim in `bridge/gtkb-gov-code-quality-baseline-slice1-005.md` §3 and §4; their canonical insertion is deferred to the sibling thread `gtkb-gov-code-quality-baseline-formal-artifact-approval` (to be filed). No new requirement is introduced; the requirement deferral honors `GOV-ARTIFACT-APPROVAL-001` per F2 of -006.

## Clause Scope Clarification (Not a Bulk Operation)

This REVISED-3 is not a bulk operation. It inserts one tracking `work_items` row via singleton MemBase insertion. No bulk loop; no shared transaction; no inventory of multiple canonical artifacts (the 4 GOV/ADR/SPEC/DCL inserts are deferred per F2 closure to a sibling thread where they will be reviewed in a per-artifact approval-packet ceremony with explicit owner content approval). The review packet for this REVISED-3 bounds IP-1 through IP-4 (hook + verifier + source-scan + tests) plus the tracking work_item; no formal-artifact-approval packet is required for the tracking WI (it is not a governed canonical artifact). `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` therefore does not require bulk-operation evidence beyond the single-insert tracking pattern documented here.

## Proposed Scope

### IP-1: Tier-1 mechanical proposal-time hook (with full distribution)

Unchanged from REVISED-2. Logic module at `groundtruth-kb/src/groundtruth_kb/hooks/code_quality_baseline_proposal_check.py` with all 8 Tier 1 checks per parent §8.1: heading presence; table presence; exact header row columns; all 9 canonical `CQ-*-001` rule IDs; Applies? cell value validation; Yes/N-A row completeness; waiver-row live resolution; vague-phrase rejection. Distribution: template + active Claude hook + Codex `.cmd` shim + `.claude/settings.json` + `.codex/hooks.json` + `managed-artifacts.toml` entry. Distribution pattern matches `bridge-compliance-gate` precedent.

### IP-2: Tier-1 fallback verifier (Slice 1 §8.4 scope)

Unchanged from REVISED-2. `scripts/check_code_quality_baseline_parity.py` statically analyzes `bridge/*.md` for the same 8 Tier 1 checks; runs in release-candidate gate.

### IP-3: Tier-3 post-implementation source/diff scanner (separate script)

Unchanged from REVISED-2. `scripts/check_code_quality_baseline_source_scan.py --since <commit-sha>` scans diff for Tier 3 mechanical rules (CQ-SECRETS-001, CQ-PATHS-001, CQ-CONSTANTS-001, CQ-COMPLEXITY-001 via radon); 5 Tier 2 IDs remain reviewer-judgment.

### IP-4: Regression tests

Unchanged from REVISED-2. Three test files:
- `platform_tests/groundtruth_kb/test_code_quality_baseline_proposal_check.py` (9 Tier 1 hook tests).
- `platform_tests/scripts/test_check_code_quality_baseline_parity.py` (9 Tier 1 fallback-verifier tests).
- `platform_tests/scripts/test_check_code_quality_baseline_source_scan.py` (5 Tier 3 source-scan tests).

### IP-5 [BLOCKED pending owner approval per F2 of -006]

The four formal artifact inserts (`GOV-CODE-QUALITY-BASELINE-001`, `ADR-CODE-QUALITY-BASELINE-AS-DEFAULT-001`, `SPEC-CODE-QUALITY-CHECKLIST-001`, `DCL-CODE-QUALITY-WAIVER-LIFECYCLE-001`) and their corresponding `.groundtruth/formal-artifact-approvals/*.json` packets are deferred to a sibling bridge thread (`gtkb-gov-code-quality-baseline-formal-artifact-approval`, not yet filed) where the per-artifact owner-approval ceremony is the central scope.

Rationale (per Codex -006 F2):
- Slice 1 GO (`bridge/gtkb-gov-code-quality-baseline-slice1-006.md`) is a Codex Loyal Opposition verdict authorizing Slice 2 implementation scope, NOT a per-artifact owner approval of the 4 artifact bodies.
- The shared validator (`groundtruth-kb/src/groundtruth_kb/governance/approval_packet.py:96-105`) requires either manual `approve`/`acknowledge` approval evidence OR `auto` mode with an owner-activated auto-approval scope. No standing scope covers these 4 artifact IDs.
- An unattended auto-dispatch worker that tries to invent approval evidence would breach `PB-ARTIFACT-APPROVAL-001`.
- The sibling thread will present each of the 4 bodies (~120 lines each) verbatim to owner via AskUserQuestion + write the 4 packets with `presented_to_user=true`, `transcript_captured=true`, `explicit_change_request=<owner's verbatim AUQ answer>`, `approval_mode='approve'`, and matching `full_content_sha256` for each — exactly the pattern DELIB-2077's packet captured earlier this session.

IP-5 implementation can proceed in parallel with this REVISED-3's implementation (IP-1 through IP-4 land hooks/verifiers/scripts/tests; IP-5 lands the 4 MemBase records and packets) once the sibling thread is filed and owner-approved.

### IP-6: Tracking work_item (not blocked)

One `work_items` row: `origin='new'`, `component='code-quality'`, `source_spec_id=NULL` (the source spec `GOV-CODE-QUALITY-BASELINE-001` does not yet exist in MemBase; the WI is updated to link the spec ID when the sibling formal-artifact-approval thread lands), `resolution_status='open'`, `stage='implementing'`, `related_bridge_threads='gtkb-gov-code-quality-baseline-slice-2'`, `changed_by='prime-builder/claude/B'`, `change_reason` citing this bridge document. The tracking WI is a singleton MemBase insert, not a governed canonical artifact, so no formal-artifact-approval packet is required for it per `GOV-STANDING-BACKLOG-001` discipline.

## Specification-Derived Verification Plan

1. `python -m pytest platform_tests/groundtruth_kb/test_code_quality_baseline_proposal_check.py -v` — all 9 Tier 1 hook tests PASS.
2. `python -m pytest platform_tests/scripts/test_check_code_quality_baseline_parity.py -v` — all 9 Tier 1 fallback-verifier tests PASS.
3. `python -m pytest platform_tests/scripts/test_check_code_quality_baseline_source_scan.py -v` — all 5 Tier 3 source-scan tests PASS.
4. `python -m ruff check groundtruth-kb/src/groundtruth_kb/hooks/code_quality_baseline_proposal_check.py scripts/check_code_quality_baseline_parity.py scripts/check_code_quality_baseline_source_scan.py` — zero errors.
5. `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gov-code-quality-baseline-slice-2` — `preflight_passed: true`.
6. `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gov-code-quality-baseline-slice-2` — exit 0; no blocking gaps.
7. `python scripts/check_codex_hook_parity.py --project-root .` — PASS.
8. End-to-end Claude hook smoke: trigger PreToolUse hook against a fixture proposal lacking `## Code Quality Baseline`; observe `block`. Then against a compliant fixture; observe allow.
9. End-to-end Codex hook smoke: invoke `.codex/gtkb-hooks/code-quality-baseline-proposal-check.cmd` against the same fixtures; identical verdicts.
10. End-to-end Tier-1 fallback verifier smoke: `python scripts/check_code_quality_baseline_parity.py --since-tag <prior-release>` against current `bridge/` directory; report exits cleanly.
11. MemBase tracking WI inserted via canonical Python API; read-back confirms `origin='new'`, `component='code-quality'`, `related_bridge_threads='gtkb-gov-code-quality-baseline-slice-2'`.

(F1 of -006 closure note: when the sibling formal-artifact-approval thread lands IP-5, its own verification plan will include `python scripts/validate_formal_artifact_packet.py .groundtruth/formal-artifact-approvals/2026-05-XX-gov-code-quality-baseline-001.json` for each of the 4 packets, plus a MemBase row-vs-packet content-identity check. Those verification steps live in the sibling thread because the packets and rows live there.)

## Risks and Rollback

- Risk: deferring IP-5 to a sibling thread means Slice 2's enforcement hook lands without the canonical governance records it references. Mitigation: the hook embeds the 9 canonical rule IDs as a constant; it does not require `SPEC-CODE-QUALITY-CHECKLIST-001` to exist in MemBase at hook activation time. Per IP-1 design, the rule-ID constant is verified against the eventual `SPEC-CODE-QUALITY-CHECKLIST-001` body via a Tier 3 smoke test once the sibling thread lands.
- Risk: hook over-blocks legitimate proposals on edge-case table renderings. Mitigation: vague-phrase list is exact-substring; reviewers can issue explicit `Owner waiver` lines at Tier 2.
- Risk: MemBase query for waiver resolution adds latency. Mitigation: per-process cache; fail-closed on unreachable; only fires when a waiver-reference is cited.
- Risk: Tier 3 `radon` invocation fails without `radon` installed. Mitigation: feature-detect with graceful skip + warning.
- Risk: sibling formal-artifact-approval thread is never filed, leaving Slice 2 governance permanently incomplete. Mitigation: the tracking WI from IP-6 carries a `change_reason` citing this REVISED-3 + the planned sibling thread name, so future-session recall is direct.
- Rollback: revert hook (template + active hook + .cmd shim + settings registrations + managed-artifacts entry); revert two scripts; revert three test files; soft-delete tracking WI (new version with `resolution_status='retracted'`); revert INDEX.

## Sequenced Dependencies

1. IP-1 + IP-2 + IP-3 + IP-4 + IP-6 land as one implementation packet (the hook + verifier + source-scan + tests + tracking WI).
2. Parent dependency: `bridge/gtkb-gov-code-quality-baseline-slice1-006.md` (Slice 1 GO) authorizes Slice 2 implementation scope.
3. Sibling dependency: `gtkb-gov-code-quality-baseline-formal-artifact-approval` (not yet filed) owns IP-5 (the 4 MemBase records + approval packets). This REVISED-3 implementation can land first; the sibling thread can run in parallel.
4. Future sibling work: once the sibling thread VERIFIED, update `WI-NNNN.source_spec_id` to `GOV-CODE-QUALITY-BASELINE-001` via canonical `update_work_item` (single-field update; no formal-artifact-approval packet required for a tracking-WI update).

## Recommended Commit Type

`feat:` — net-new Tier-1 proposal-time hook (logic module + template + active hook + Codex `.cmd` shim + dual registration + `managed-artifacts.toml` entry), net-new Tier-1 fallback verifier script, net-new Tier-3 source-scan script, three net-new test files. Net-new capability surface; not refactor; not chore. (The 4 formal artifacts are deferred to a sibling thread per F2, so they are NOT in this commit's scope.)

## Bridge-Compliance Self-Check

- First line is `REVISED`.
- Title line includes `REVISED-3` and the BLOCKED-IP-5 annotation.
- Metadata: `bridge_kind: implementation_proposal`, `Document:`, `Version: 007`, `Responds to: bridge/gtkb-gov-code-quality-baseline-slice-2-006.md`, `Author: Prime Builder (Claude, harness B)`, `Date: 2026-05-14 UTC`, `Session: S350`, `target_paths: [JSON list with 13 entries, all in-root, 4 approval-packet paths REMOVED per F2]`.
- `## Specification Links` is a plain heading with flat bullets and no `###` sub-headings; cites `bridge/INDEX.md` insertion-at-top discipline.
- `## Prior Deliberations` cites seven DELIB IDs.
- `## Owner Decisions / Input` is substantive; explicitly addresses F2 by acknowledging no standing per-artifact owner-approval scope and citing the approval_packet.py validator requirements.
- `## Requirement Sufficiency` has exactly one operative state.
- `## Clause Scope Clarification (Not a Bulk Operation)` is present; includes `formal-artifact-approval`, `inventory`, `singleton MemBase insertion`, and `review packet`.
- `## Recommended Commit Type` is present (`feat:`).
- `## In-Root Placement Evidence` enumerates each target path.
- F1 from `bridge/gtkb-gov-code-quality-baseline-slice-2-006.md` is closed by adding the packet-validation invocations to the sibling-thread verification plan note in `## Specification-Derived Verification Plan`.
- F2 from `bridge/gtkb-gov-code-quality-baseline-slice-2-006.md` is closed by explicitly marking IP-5 BLOCKED and deferring the 4 formal artifacts + their packets to a sibling thread where the per-artifact approval ceremony is the central scope.
- F1-F4 from `-002` remain closed; F1/F2 from `-004` remain closed.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
