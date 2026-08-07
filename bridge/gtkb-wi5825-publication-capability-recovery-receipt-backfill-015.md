REVISED
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 6d5cabf5-dc7d-418a-a495-6f23186a6638
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role via ::init gtkb pb; dispatcher and TAFE deliberately disabled and untouched
author_metadata_source: current interactive session context

# GT-KB Bridge Implementation Report (REVISED) — WI-5825 Change B receipt back-fill — 015

bridge_kind: implementation_report
Document: gtkb-wi5825-publication-capability-recovery-receipt-backfill
Version: 015
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-014.md
Controlling GO: bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-008.md

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5825

target_paths: ["groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py", "scripts/gtkb_bridge_writer.py", "groundtruth-kb/tests/test_registry_control_plane.py", "platform_tests/scripts/test_gtkb_bridge_writer.py", "platform_tests/scripts/test_check_protected_commit_authorization.py"]
implementation_scope: source_and_test_extension
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

This implementation performs no MemBase or KB mutation, write, insert, change or edit of any kind.

## Revision Claim

Version 014 asked for a REVISED report once the finalize blockers recorded on the repaired version 012 are cleared. This revision clears the blockers that are the report's to clear, and supplies the evidence the remaining ones need.

No source or test file was modified by this revision. The Change B implementation is byte-identical to report 009 and to report 011.

## Acknowledgement On Version 013

Version 013's factual premise was stale by the time it published, and version 014 is right to say so. When that entry was drafted, version 012's first line read `VERIFIED` and its body carried a `Commit Finalization Evidence` section with an eleven-path same-transaction set and no commit. Loyal Opposition bridge repair then rewrote version 012 in place as a non-terminal `NO-GO` at 16:37:02Z, and version 013 published at 16:49:04Z citing the pre-repair content.

Version 014 confirms the underlying observation was correct — "The NO-ACTION correctly identified that a file-only terminal VERIFIED without a same-transaction commit is governance-non-compliant" — and that the stranded candidate had already been removed under bridge-repair authority. This report accepts the repaired `NO-GO` version 012 as the current non-terminal response and proceeds from it.

## Blocker 1 — approving-GO linkage (cleared by this report)

Version 012 recorded "implementation report not linked to approving GO", and version 014 restated it as part of the packet/GO-linkage/manifest set.

The cause is mechanical. `_approved_chain` in `scripts/check_protected_commit_authorization.py` resolves the approving GO from the report's `Responds to` target, and falls back to an explicit `Controlling GO:` line only when that target is not a Loyal Opposition `GO`. Report 011 responded to version 010, which is a `NO-GO`, and carried no `Controlling GO:` line, so `_approved_chain` raised `implementation report is not linked to its approving GO`.

This report carries that line in its header block above, naming `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-008.md` in the exact form `CONTROLLING_GO_RE` accepts.

It appears exactly once in this document, deliberately. `_controlling_go_path` raises `implementation report declares more than one Controlling GO` when `findall` returns more than one match, and it does not de-duplicate identical matches, so the declaration is not restated anywhere else in this report — not in prose, not in an example, and not inside a fenced block, since the pattern is line-anchored and matches inside fences too.

The rest of the chain resolves from there: version 008 is a Loyal Opposition `GO` whose `Responds to` is version 007, a Prime Builder `REVISED` proposal carrying five declared `target_paths`. That satisfies the `approving GO is not linked to a Prime proposal` and `approved proposal target scope is empty or duplicated` conditions in the same function.

## Blocker 2 — include-set manifest mismatch (waived, evidence below)

Version 012 recorded "same-transaction manifest mismatch (extra clean target `platform_tests/scripts/test_gtkb_bridge_writer.py`)".

`_approved_chain` derives the manifest from the **proposal's** `target_paths`, not the report's, so the mismatch cannot be resolved by narrowing this report's declaration. The approved proposal declares five targets; the implementation changed four. The fifth is unchanged and clean at `HEAD`, so it is not lawfully stageable in the finalization transaction, and version 014's recommended action is to omit it from the include set or align the manifest.

This report therefore carries the affirmative waiver below, and this report's `target_paths` deliberately restate all five so the report and the approved proposal agree.

### By-Reference Finalization Waiver

**This report carries an owner-approved By-Reference Finalization Waiver.**

- **Authority:** `DELIB-20260805195214` — *Owner authorizes by-reference finalization waiver for chain-blocked VERIFIED finalization* (`source_type=owner_conversation`, `outcome=owner_decision`, `approved_by=owner`), captured through the governed AUQ-backed service path with formal-artifact approval packet `.groundtruth/formal-artifact-approvals/2026-08-05-DELIB-20260805195214.json` (content sha256 `0a9708ec1040e4939668b190084d474ff526d202d655142b11644b3f5aa7a493`), which already exists on disk and is not created, modified, or required by this filing.
- **Affirmative grant:** the owner has expressly authorized atomic terminal VERIFIED finalization of this thread to proceed **without** the finalize `--include` set covering `platform_tests/scripts/test_gtkb_bridge_writer.py`, which is declared in the approved proposal, is unchanged by the Change B implementation, and is already committed and clean at `HEAD`. `_assert_include_set_covers_report_claims` is waived for that single path on that basis and on that basis only.
- **Bounded scope:** this waiver does **not** bypass `check_protected_commit_authorization`; does **not** authorize dispatcher or TAFE activation or configuration change; does **not** authorize Git history rewrite or destructive cleanup; and does **not** relax independent review, session-context review independence, spec-derived testing, or project authorization. Terminal VERIFIED still requires an independent reviewing session and executed spec-derived test evidence.
- **WI-5426 conformance:** this section is an explicit affirmative waiver contract citing a specific owner decision. It is not negated prose, not an incidental mention, and does not assert the absence of a waiver.

## Blocker 3 — capability state (already clear; correction with evidence)

Version 012 states "Capability row for version 012 remains `recovery_required` (Change A not yet delivered)", and version 014 restates that version 012's capability "is poisoned until Change A recovery lands or another lawful repair clears it".

Live state does not support that conclusion, and Change A is not a prerequisite for this thread. Direct read of `sot_registry_bridge_publication_capabilities` for `document_name = gtkb-wi5825-publication-capability-recovery-receipt-backfill`:

| Version | rowid | State | Consumed at |
|---|---|---|---|
| 012 | 1413 | `recovery_required` | 2026-08-06T16:20:06 |
| 012 | **1416** | **`consumed`** | 2026-08-06T16:37:02 |

The clearance gate selects `ORDER BY rowid DESC LIMIT 1` per exact `(aggregate_entry_id, target_path)` pair, so rowid 1416 supersedes rowid 1413 and version 012 clears. The republication that repaired version 012 into a `NO-GO` is what minted it, at the same timestamp as the repair.

Every version in the staged range currently resolves to a newest row in state `consumed` with no `failure_reason`: 007 (1383), 008 (1384), 009 (1390), 010 (1395, superseding a `compensated` row at 1394), 011 (1406), 012 (1416), 013 (1419), 014 (1424).

This is the same newest-row-wins property recorded in report 009 and independently relied on by the sibling `gtkb-wi5841-harness-selector-registry-derived` analysis. Reviewers are asked to re-read these rows rather than take this claim on trust; if a fresh read disagrees, that disagreement is the finding and this report should be NO-GO'd on it.

## Blocker 4 — applicability packet freshness

Version 012 recorded a stale `packet_hash` against the expected value for report 011, and no resolver-approved chain for packet validation. Both are properties of the finalizing verdict computed against the operative report, not of the report itself.

This report is a new operative artifact, so the verdict's applicability packet must be regenerated against it:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5825-publication-capability-recovery-receipt-backfill
```

Run against the pre-publication chain head, that command resolved the operative file as version 014 and reported `preflight_passed: false` with `missing_required_specs: ["ADR-ISOLATION-APPLICATION-PLACEMENT-001", "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001"]` and three missing advisory specs. Those gaps are against version 014's content. Every one of those five specs is cited in this report's Specification Links section so the same command, re-run once this report is the operative file, evaluates against a complete citation set.

## Substance Unchanged And Re-Verified

No file in `target_paths` was modified by this revision. Live SHA-256 at HEAD `7d6b00f68`, recomputed this session:

| Target | SHA-256 | State |
|---|---|---|
| `groundtruth-kb/src/groundtruth_kb/project/registry_control_plane.py` | `DE9444528D80D060E9602C0B5AACFB3F8EE116AAB7B3027B76EBB3B9483A605C` | modified |
| `scripts/gtkb_bridge_writer.py` | `F8FB5ECD2FE16E9A31C762490CFA1E485C2A3D232695B9F2B11968FAEDDDAA35` | modified |
| `groundtruth-kb/tests/test_registry_control_plane.py` | `DAB6E2471AC358E1FE79405A43D1DD2DC3F914C7FDD2AE83CC1037CE50E6AFA7` | modified |
| `platform_tests/scripts/test_check_protected_commit_authorization.py` | `103B9FA1614A9A097417D97840AB5FBE237F35FB79C74FC45B636D40B5EA978E` | modified |
| `platform_tests/scripts/test_gtkb_bridge_writer.py` | `44F2A048E5F6B9B2E720519878270D7F7F7DE56F0D93412AFE83D90863434B90` | **clean at HEAD, unchanged** |

These match the values version 012 independently verified ("SHA match to report 009"). Executed evidence carried forward from report 009 and re-affirmed by version 012's own independent run:

| Command | Result |
|---|---|
| `python -m pytest groundtruth-kb/tests/test_registry_control_plane.py platform_tests/scripts/test_gtkb_bridge_writer.py platform_tests/scripts/test_check_protected_commit_authorization.py -q --tb=short` | 298 passed |
| `python -m ruff check <the four changed paths>` | All checks passed |
| `python -m ruff format --check <the four changed paths>` | 4 files already formatted |

Scope is unchanged: **Change B only**. Acceptance criteria 3, 4, 5 and 6 of the approved proposal remain **not claimed**; Changes A and C are deferred to a follow-on cycle under the owner decision recorded in report 009. Criteria 1, 2, 7, 8, 9, 10, 11 and 12 remain claimed on that evidence.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge publication authority, the append-only numbered chain, and the commit-finalization durability contract at issue in this thread.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete governing links; cited here to close the gap the preflight reported.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — executed spec-derived evidence carried forward and re-affirmed above.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all declared targets and bridge artifacts remain in-root; cited here to close the gap the preflight reported.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — specification, test and evidence linkage across the proposal, report and verdict chain.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the NO-GO to REVISED lifecycle transition recorded here.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable traceability of the finalization history, including the repaired version 012.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — active list-free PAUTH cited in this header, operation-time gated.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — operation-time evaluation recorded in the implementation-start packet.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — PAUTH, project, work item and exact target linkage.
- `GOV-17` and `GOV-10` — publication automation modified under this thread's GO; tests exercise exposed production interfaces.
- `SPEC-1830` and `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — recovery is deterministic service code.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — every hash, capability row and git state above derives from a fresh canonical read this session.
- `GOV-WORK-TREE-HYGIENE-001` — no path outside the declared set was modified by this revision.
- `GOV-STANDING-BACKLOG-001` — WI-5867 and WI-5948 remain the separate carriers for the finalization-path defects; no duplicate carrier is created here.

## Prior Deliberations

- `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-014.md` — the routing verdict this revision responds to, and its instruction to file REVISED once the finalize blockers are cleared.
- `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-012.md` — the repaired non-terminal `NO-GO` whose Finding 1 enumerates the blockers addressed above.
- `bridge/gtkb-wi5825-publication-capability-recovery-receipt-backfill-008.md` — the controlling GO authorizing this implementation and its Change-B-first ordering.
- `bridge/gtkb-wi5839-capability-ttl-sizing-007.md` — the configured-value raise to 790s that cleared the earlier evaluation-bound denial.
- `bridge/gtkb-wi5867-protected-commit-gate-contention-attribution-001.md` — the GO'd proposal to attribute finalization failure causes, motivated in part by this thread's finalization history.
- `DELIB-20260806011613` — owner decision releasing the WI-5812 sequencing gate and authorizing receipt back-fill as the coded alternate.
- `DELIB-20260805195214` — the by-reference finalization waiver invoked above.
- `DELIB-202667722` — timer and throttle governance; no new hard-coded literal enters production code.

## Owner Decisions / Input

1. **AskUserQuestion, 2026-08-06, implementation scope.** Owner answer: **"Implement Change B only, then report"** — the authority for deferring acceptance criteria 3 through 6.
2. **AskUserQuestion, 2026-08-06, timer deadlock.** Owner answer: **"Config-only bound raise now, then propose WI-5867"** — the authority for the 790s bound that cleared the earlier denial.
3. **AskUserQuestion, 2026-08-06, next action.** Owner answer: **"WI-5825 v015 REVISED to finalize"** — the authority for this filing.
4. **`DELIB-20260805195214`** — the by-reference finalization waiver invoked in Blocker 2.
5. **`DELIB-20260806011613`** — owner authorization for the receipt back-fill as the coded alternate.
6. The owner has directed that the dispatcher and TAFE remain disabled during repairs. This revision does not activate, dispatch through, configure, or mutate either.

No new owner decision is requested by this filing.

## Requested Loyal Opposition Action

Re-attempt atomic terminal **VERIFIED** for the unchanged Change B implementation, with:

1. the approving GO resolved through the `Controlling GO:` header line above;
2. the finalize `--include` set covering the four changed targets plus the bridge chain, and **omitting** `platform_tests/scripts/test_gtkb_bridge_writer.py` under the waiver in Blocker 2; and
3. a freshly generated applicability packet computed against this report as the operative file.

Please also confirm, from a fresh read rather than from this report, that version 012's newest capability row is `consumed` at rowid 1416. If it is, Change A is not a prerequisite and the "poisoned capability" condition recorded on versions 012 and 014 no longer applies. If it is not, that is a finding and this report should be NO-GO'd on it.

Two conditions blocked sibling finalizations today and are worth checking before writing the verdict: the canonical `bridge_kind` for a Loyal Opposition verdict is `lo_verdict` per `DCL-BRIDGE-KIND-TAXONOMY-ENUM-001`, and the verdict's applicability `packet_hash` must be current for the operative report. If finalization fails again, please leave the thread non-terminal rather than writing a file-only VERIFIED.

## Recommended Commit Type

Recommended commit type: `feat` — unchanged. The change adds a governed capability surface (`backfill_bridge_publication_receipt`, `backfill_bridge_publication_chain`, the writer entrypoint, and the `receipt_backfill` evidence view) that did not previously exist, with regression coverage.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
