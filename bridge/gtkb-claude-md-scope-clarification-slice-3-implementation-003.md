REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 39611c3e-b51e-43f1-aa37-5ec4be3894b0
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning

Project Authorization: PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3-V2
Project: PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION
Work Item: WI-3438

# GT-KB CLAUDE.md Scope Clarification - Slice 3 - Implementation - 003 (REVISED-1)

Document: gtkb-claude-md-scope-clarification-slice-3-implementation
Version: 003 (REVISED-1; responds to Codex NO-GO at -002)
Date: 2026-05-29 UTC
Responds to NO-GO: bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-002.md
Supersedes: bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-001.md
Carries forward GO: bridge/gtkb-claude-md-scope-clarification-slice-2-004.md
Parent governance review: bridge/gtkb-claude-md-scope-clarification-slice-2-003.md

## Claim

This REVISED is an implementation proposal that addresses both Codex F1 and F2 findings at `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-002.md`:

- **F1 (SECURITY.md sequencing)**: revised implementation sequence — `git mv` of root SECURITY.md happens FIRST (preserves Agent Red policy content at applications/Agent_Red/SECURITY.md), THEN new root stub creation. Added content-specific verification.
- **F2 (PAUTH allowed_mutation_classes gap)**: revoked the original `PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3` and issued `PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3-V2` with extended `allowed_mutation_classes` to cover `work_item_lifecycle_update`, `project_authorization_completion`, and `deliberation_record_create`.

All embedded content (rewritten platform CLAUDE.md, new applications/Agent_Red/CLAUDE.md, root SECURITY.md stub, CLAUDE-ARCHITECTURE.md line-12 fix, narrative-artifact-approval.toml addition, canonical-terminology.md update, 7-packet plan) carries forward from -001 unchanged. This REVISED narrowly addresses the two implementation-plan defects Codex identified.

## Specification Links

- `GOV-01` — CLAUDE.md ≤300 lines; verified by `wc -l CLAUDE.md` post-implementation.
- `GOV-08` — KB is truth; narrative-artifact permitted-markdown exception (extended to `applications/<name>/CLAUDE.md`).
- `GOV-09` — Owner input classification.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — live bridge index authority. This REVISED is filed at `bridge/` with an INDEX update inserting `REVISED: bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-003.md` at the top of the document's existing entry per the protocol's newest-first convention; prior `NO-GO: -002.md` and `NEW: -001.md` lines preserved; no deletion or rewrite of prior versions.
- `GOV-ARTIFACT-APPROVAL-001` — 7 narrative-artifact approval packets required.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative-artifact mutation gate.
- `DCL-CONCEPT-ON-CONTACT-001` — load-bearing concept surfacing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this Specification Links section enumerates linkage for the implementation proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Specification-Derived Verification Plan below lists spec-derived commands including the F1 content-separation checks for SECURITY.md.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — `applications/<name>/` placement; all new applications/Agent_Red/* targets comply.
- `ADR-0001` — Three-Tier Memory Architecture.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable artifact graph preservation.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — narrative-artifact lifecycle.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance.
- `GOV-AGENT-RED-NESTED-IN-APPLICATIONS-001` — Agent Red placement.
- `.claude/rules/operating-role.md` — durable role assignment in JSON.
- `.claude/rules/bridge-essential.md` §"Operational Mode" — cross-harness event-driven trigger.
- `.claude/rules/operating-model.md` §1, §2.
- `.claude/rules/canonical-terminology.md`.
- `.claude/rules/canonical-terminology.toml` dual-agent profile.
- `.claude/rules/project-root-boundary.md`.
- `.claude/rules/file-bridge-protocol.md`.
- `config/governance/narrative-artifact-approval.toml`.
- `AGENTS.md` line 11.
- `PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3-V2` (new authorization with extended `allowed_mutation_classes` per F2; supersedes revoked V1).

## PAUTH Supersession Note

`PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3` (V1) revoked 2026-05-29 via `gt projects revoke-authorization` per Codex F2 finding. `PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3-V2` issued 2026-05-29 via `gt projects authorize` with the original 6 mutation classes plus 3 additional KB-mutation classes:

- `work_item_lifecycle_update` (for WI-3438 open → in_progress → done transitions during Slice 3 implementation)
- `project_authorization_completion` (for `gt projects complete-authorization PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3-V2` at end of Slice 3)
- `deliberation_record_create` (for `gt deliberations record` capturing the 4-AUQ owner-decision chain as harvested `source_type=owner_conversation` records)

Plus a new `--forbid` clause: "raw db.insert_* calls outside governed CLI surfaces" — explicitly forbidding direct SQLite writes.

## F1 Correction — SECURITY.md Sequencing

Per Codex F1: the -001 proposal's per-file disposition declared the new root stub creation AFTER the `git mv`, but the -001 implementation sequence said "Create new root SECURITY.md stub BEFORE running git mv of old root SECURITY.md content". That ordering risked the new stub overwriting the root path before the Agent Red content could be moved out, corrupting the content split.

**Corrected Implementation Sequence for SECURITY.md** (replaces step 8 of -001's Implementation Sequence):

8. **SECURITY.md content-preserving move + stub creation** (atomic):
   a. **First**: `git mv SECURITY.md applications/Agent_Red/SECURITY.md` — moves the Agent Red security policy content from root to its application-side destination. After this step, no `SECURITY.md` exists at root.
   b. **Second**: Write new root `SECURITY.md` platform stub (content per "Embedded Content — Root SECURITY.md (New Platform Stub per F5)" section of -001). This creates a fresh root `SECURITY.md` with platform-level content; no risk of overwriting the Agent Red policy because that content is already at the new app-side path.
   c. **Stage both changes together** with `git add SECURITY.md applications/Agent_Red/SECURITY.md` for atomic commit.
   d. **Verify content separation** before staging is finalized:
      - `head -1 SECURITY.md` should show the new platform stub header.
      - `head -1 applications/Agent_Red/SECURITY.md` should show the original Agent Red policy header.

## F2 Correction — Project Authorization Scope Reconciled

Per Codex F2: the -001 proposal declared MemBase mutations under `groundtruth.db` target_paths but the cited PAUTH (V1) did not declare matching `allowed_mutation_classes`. PAUTH V2 above resolves this by enumerating all KB mutation classes Slice 3 will perform.

**Per-`groundtruth.db`-mutation authorization mapping**:

| Slice 3 KB write | PAUTH V2 allowed_mutation_class | Governed CLI surface |
|---|---|---|
| WI-3438 lifecycle state updates (open → in_progress → done) | `work_item_lifecycle_update` | `gt backlog update` (governed CLI; no raw `db.insert_*`) |
| `gt projects complete-authorization PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3-V2` at end | `project_authorization_completion` | `gt projects complete-authorization` |
| `gt deliberations record` for 4-AUQ owner-decision chain harvest | `deliberation_record_create` | `gt deliberations record --source-type owner_conversation` |

All MemBase writes go through governed CLI surfaces; raw `db.insert_*` calls are explicitly forbidden by PAUTH V2's `--forbid` clause.

## Owner Decisions / Input

4-AUQ owner-decision chain from -001 still authorizes this work; no new owner AUQ required for this REVISED (F1 is mechanical sequence fix; F2 is mechanical PAUTH scope reconciliation; both within owner-already-authorized scope):

1. **Approach selection** (Slice 1 GO at scoping-002): "C: Split (recommended)"
2. **Scope expansion**: "Expand Slice 2 to 18.I scope"
3. **F1 metadata-mismatch** (Slice 2 NO-GO -002 / REVISED -003 / GO -004): "Reframe Slice 2 as governance review"
4. **F4 registry-expansion**: "Expand registry to protect app-side files"

Per-protected-mutation approval packets remain owner-AUQ at write time per `DCL-ARTIFACT-APPROVAL-HOOK-001`.

## Prior Deliberations

- `DELIB-S330-AGENT-RED-NESTED-IN-APPLICATIONS-RULE` (PAUTH V2 owner-decision basis; foundational rule this Slice 3 operationalizes)
- `DELIB-0877` (industry-alignment critique for GT-KB/application separation)
- `DELIB-0785` (GT-KB has own release-readiness lifecycle separate from Agent Red)
- `DELIB-0834` (Agent Red as fully conformant application sustained by GT-KB)
- `DELIB-0023` (Membase / Agent Red coupling source-of-truth problem)
- `DELIB-0876` (durable work subject framing)
- `DELIB-0501` (Agent Red Large-Scale Commercial Production Plan)
- `DELIB-0327` (Hotfix / WIP Coexistence Operating Model)
- `DELIB-S331-DA-READ-SURFACE-CORRECTION-FOUNDATIONS` (placement-over-coercion design)
- `DELIB-0706` (spec pipeline features are GT-KB product features)
- `DELIB-0719` (repo-tracked MEMORY.md placement)

Bridge thread family (added -002 NO-GO + this REVISED-003):
- `bridge/gtkb-claude-md-scope-clarification-scoping-001.md`, `-002.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-2-001.md`, `-002.md`, `-003.md`, `-004.md`
- `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-001.md` (NEW; superseded by this REVISED)
- `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-002.md` (Codex NO-GO F1/F2)

## Reference to -001 for Carry-Forward Embedded Content

The following sections in -001 carry forward to this REVISED unchanged; refer to `bridge/gtkb-claude-md-scope-clarification-slice-3-implementation-001.md` for the verbatim content embedded as code blocks. The implementation proposal here uses the same Slice 3 plan; the only changes are F1 and F2 corrections above.

- "Embedded Content — Root CLAUDE.md (Rewritten Platform Content)" (~265 lines; F2/F3 corrections from Slice 2 REVISED-003 already applied in -001)
- "Embedded Content — applications/Agent_Red/CLAUDE.md (New Application-Scope File)" (~75 lines)
- "Embedded Content — Root SECURITY.md (New Platform Stub per F5)" (~25 lines)
- "CLAUDE-ARCHITECTURE.md Line-12 Path Fix" (single-line edit: obsolete E:\Claude-Playground path → E:\GT-KB\applications\Agent_Red\)
- "Embedded Content — narrative-artifact-approval.toml Addition (per F4)" (`application-scope-rules` block protecting `applications/*/CLAUDE.md` etc.)
- "canonical-terminology.md Update Plan (per F4)" (extend canonical-artifact definition around line 1288)
- "Per-File Disposition Matrix (Implementation)" (12-row matrix)
- "Approval-Packet Plan (7 Packets)" (per-packet artifact_id / action / target_path / hash source)

## target_paths

- `CLAUDE.md` (update; Packet 1)
- `CLAUDE-REFERENCE.md` (delete via git mv; Packet 2)
- `CLAUDE-ARCHITECTURE.md` (delete via git mv + line-12 edit; Packet 3)
- `SECURITY.md` (delete via git mv THEN create new platform stub per F1 corrected sequence; not in protected_artifacts; no packet)
- `CONTRIBUTING.md`, `CHANGELOG.md`, `CLAUDE_ARCHIVE.md` (delete via git mv; not protected)
- `applications/Agent_Red/CLAUDE.md` (create; Packet 4; newly protected per F4)
- `applications/Agent_Red/CLAUDE-REFERENCE.md` (create via git mv; Packet 5; newly protected per F4)
- `applications/Agent_Red/CLAUDE-ARCHITECTURE.md` (create via git mv + line-12 edit; Packet 6; newly protected per F4)
- `applications/Agent_Red/CLAUDE_ARCHIVE.md`, `applications/Agent_Red/CONTRIBUTING.md`, `applications/Agent_Red/CHANGELOG.md`, `applications/Agent_Red/SECURITY.md` (create via git mv; not protected)
- `config/governance/narrative-artifact-approval.toml` (update; self-excluded; no packet)
- `.claude/rules/canonical-terminology.md` (update; Packet 7; protected)
- `.groundtruth/formal-artifact-approvals/2026-05-29-*.json` (7 packet files)
- `groundtruth.db` (MemBase mutations via governed CLI per PAUTH V2 allowed_mutation_classes: `work_item_lifecycle_update` for WI-3438; `project_authorization_completion` for PAUTH V2; `deliberation_record_create` for AUQ harvest. Raw `db.insert_*` forbidden by PAUTH V2.)

## Requirement Sufficiency

Existing requirements sufficient. No new specifications. This REVISED operates within already-canonical specifications + PAUTH V2 supersedes V1 to align with proposal scope (mechanical reconciliation per Codex F2, not a new requirement).

## Specification-Derived Verification Plan

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, all spec-derived verification commands the implementation report will execute:

| Verification | Command | Expected |
|---|---|---|
| GOV-01 line cap | `wc -l CLAUDE.md` | ≤300 |
| Doctor required_startup_terms | `grep -c "MemBase\\|Deliberation Archive\\|MEMORY.md\\|Prime Builder\\|Loyal Opposition" CLAUDE.md` | ≥5 |
| Doctor dual-agent profile | `python -m groundtruth_kb project doctor` | PASS for canonical-terminology |
| Platform-side cross-refs | `grep -rn "CLAUDE.md" .claude/rules/ AGENTS.md` | All references resolvable |
| App-side cross-refs landed | `grep -rn "applications/Agent_Red/CLAUDE" .claude/rules/ CLAUDE.md` | New refs landed |
| Registry expansion present | `grep -A4 "application-scope-rules" config/governance/narrative-artifact-approval.toml` | Block present |
| Protected-pattern enforcement test | Test Write to `applications/Agent_Red/CLAUDE.md` without packet | Blocked by hook |
| Pre-commit narrative gate | `python scripts/check_narrative_artifact_evidence.py --staged` (with packets staged) | PASS |
| README link integrity | `test -f SECURITY.md` | exit 0 |
| **Root SECURITY.md is platform stub (F1)** | `head -1 SECURITY.md` | `# Security Policy — GroundTruth-KB Platform` |
| **App-side SECURITY.md is Agent Red policy (F1)** | `grep -q "covers the Agent Red platform" applications/Agent_Red/SECURITY.md` | exit 0 |
| 7 approval packets present | `ls .groundtruth/formal-artifact-approvals/2026-05-29-*.json \| wc -l` | 7 |
| Hash match per packet | sha256 verification per packet | No assertion error |
| PAUTH V2 completion at end | `python -m groundtruth_kb projects complete-authorization PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3-V2 --change-reason "Slice 3 implementation VERIFIED"` | Authorization completed cleanly |

## Risk / Rollback

- **Risk**: Approval-packet hash mismatch at write time. Mitigation: compute SHA-256 from final LF-normalized content before staging the packet.
- **Risk**: Doctor profile term-check fails if F2/F3 corrections dropped a required_startup_term. Mitigation: pre-commit `grep -c` verification step.
- **Risk**: Cross-references break if heading wording changes. Mitigation: Governance Index heading wording preserved (canonical-terminology.md:1328 anchor).
- **Risk**: New `applications/*/CLAUDE.md` protected patterns not matched by hook. Mitigation: test-write verification command.
- **Risk** (per F1): SECURITY.md content swap if sequence reversed. Mitigation: F1-corrected step 8 (above) forces `git mv` BEFORE root stub creation. Content-specific verification commands catch drift.
- **Risk**: Parallel session contamination. Mitigation: verify clean working tree of target paths before each protected mutation.
- **Rollback**: `git restore` reverts root file changes; `rm -rf applications/Agent_Red/{CLAUDE,CLAUDE-REFERENCE,CLAUDE-ARCHITECTURE,CLAUDE_ARCHIVE,CONTRIBUTING,CHANGELOG,SECURITY}.md`; `rm .groundtruth/formal-artifact-approvals/2026-05-29-*.json`; `git restore config/governance/narrative-artifact-approval.toml .claude/rules/canonical-terminology.md`; if Slice 3 abandoned mid-implementation also revoke PAUTH V2 via `gt projects revoke-authorization PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3-V2`.

## Implementation Sequence (F1-Corrected at Step 8)

1. Stage `narrative-artifact-approval.toml` update (registry expansion) — landing this FIRST ensures new `applications/*/CLAUDE.md` patterns are protected by the time app-side files are created.
2. Generate Packet 7 for canonical-terminology.md update; Write the canonical-terminology.md edit.
3. Generate Packet 1 for CLAUDE.md update; Write the platform CLAUDE.md rewrite.
4. Generate Packet 4 for applications/Agent_Red/CLAUDE.md create; Write the new app-side CLAUDE.md.
5. `git mv CLAUDE-REFERENCE.md applications/Agent_Red/CLAUDE-REFERENCE.md`; generate Packets 2 (root delete) and 5 (app-side create).
6. `git mv CLAUDE-ARCHITECTURE.md applications/Agent_Red/CLAUDE-ARCHITECTURE.md`; edit line 12; generate Packets 3 (root delete) and 6 (app-side create).
7. `git mv` for CLAUDE_ARCHIVE.md, CONTRIBUTING.md, CHANGELOG.md (no packets).
8. **SECURITY.md content-preserving move + stub (F1-corrected)**: see F1 Correction section above — `git mv SECURITY.md applications/Agent_Red/SECURITY.md` FIRST, then Write new root platform stub, stage atomically, verify content separation.
9. Run all verification commands per the Specification-Derived Verification Plan; collect results.
10. Update WI-3438 lifecycle state to in_progress during implementation, then to done post-VERIFIED (via `gt backlog update`; per PAUTH V2 `work_item_lifecycle_update`).
11. After Codex VERIFIED on post-impl report: `gt projects complete-authorization PAUTH-GTKB-CLAUDE-MD-SCOPE-CORRECTION-SLICE-3-V2`.
12. File post-implementation report at version `-NNN` for Codex VERIFIED review.

## Owner Action Required

After Codex GO on this REVISED:
1. Owner is presented with the 7 approval packets via AskUserQuestion (one per protected mutation; packet content shown verbatim).
2. Owner approves each packet.
3. Prime Builder executes the Implementation Sequence (with F1-corrected step 8).
4. Verification runs (including F1 content-separation checks); post-implementation report filed.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
