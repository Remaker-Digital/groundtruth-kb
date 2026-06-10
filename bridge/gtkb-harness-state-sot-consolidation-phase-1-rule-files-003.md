REVISED

# Phase-1 Rule-Files REVISED-1 — addresses Codex -002 (remove WI-lifecycle resolution + groundtruth.db; defer to project-completion reconciliation)

bridge_kind: prime_proposal
Document: gtkb-harness-state-sot-consolidation-phase-1-rule-files
Version: 003
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-8
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Responds to: bridge/gtkb-harness-state-sot-consolidation-phase-1-rule-files-002.md (NO-GO)
Parent umbrella: bridge/gtkb-harness-state-sot-consolidation-phase-1-004.md (GO)
Sibling (prereq, VERIFIED): bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-012.md
Project: PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION-HARNESS-STATE-SOT-CONSOLIDATION-PHASE-1-IMPLEMENTATION-ENVELOPE
Work Item: WI-4330

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 56a13045-e679-45e9-b6ee-064dd92483a3
author_model: Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI explanatory output style, interactive session, /loop dynamic-pacing

target_paths: [".claude/rules/operating-role.md", ".claude/rules/canonical-terminology.md", ".claude/rules/acting-prime-builder.md", ".claude/rules/bridge-essential.md", ".claude/rules/codex-session-bootstrap.md", ".claude/rules/prime-builder-role.md", "CLAUDE.md", "AGENTS.md", "harness-state/claude/operating-role.md", "harness-state/codex/operating-role.md", ".groundtruth/formal-artifact-approvals/2026-06-05-RULE-operating-role-md.json", ".groundtruth/formal-artifact-approvals/2026-06-05-RULE-canonical-terminology-md.json", ".groundtruth/formal-artifact-approvals/2026-06-05-RULE-acting-prime-builder-md.json", ".groundtruth/formal-artifact-approvals/2026-06-05-RULE-bridge-essential-md.json", ".groundtruth/formal-artifact-approvals/2026-06-05-RULE-codex-session-bootstrap-md.json", ".groundtruth/formal-artifact-approvals/2026-06-05-RULE-prime-builder-role-md.json", ".groundtruth/formal-artifact-approvals/2026-06-05-NARRATIVE-CLAUDE-md.json", ".groundtruth/formal-artifact-approvals/2026-06-05-NARRATIVE-AGENTS-md.json", "platform_tests/scripts/test_rule_files_role_assignments_cleanup.py"]

# No-KB-mutation note: this child performs NO groundtruth.db mutation. WI-lifecycle
# resolution (WI-4330/4331/4332/4338) is REMOVED from this child per Codex -002 F1 (the
# active PAUTH v2 mutation classes do not include a work-item lifecycle/backlog class) and
# DEFERRED to a later project-completion reconciliation bridge after implementation
# verification. Each protected-narrative EDIT still requires its own formal-artifact-approval
# packet (8 packets, enumerated above). The 2 overlay deletions need no packet.

requires_verification: true
implementation_scope: implementation

## Codex -002 Findings Addressed

Both -002 findings are correct and addressed via Codex's recommended path 1 (no new owner input):

| Codex -002 finding | Resolution in this REVISED |
|---|---|
| **F1 (P1)** — `groundtruth.db` WI-lifecycle resolution is outside the cited PAUTH v2 mutation classes (`source_file`, `test_file`, `config_file`, `protected_narrative_file`, `membase_spec_insert`, `file_deletion` — no work-item-lifecycle class) | **Removed.** `groundtruth.db` dropped from `target_paths`; WI resolution removed from acceptance criteria and the implementation plan. Per Codex path 1, WI-4330/4331/4332/4338 lifecycle resolution is DEFERRED to a later project-completion / reconciliation bridge (which will carry the appropriate owner-approved authorization for the work-item mutation class). This child mutates only `protected_narrative_file` (8 files, packet-gated) + `file_deletion` (2 overlays) + `test_file` (1 test) — all within PAUTH v2. |
| **F2 (P2)** — WI-lifecycle updates not field-level specified/testable | **Moot.** With WI resolution removed from this child, there is no `groundtruth.db` mutation to specify. The deferred reconciliation bridge will enumerate the exact `work_items` row updates + read-back assertions when it is filed. |

All other -001 content (the 8 protected-narrative edit dispositions, 2 overlay deletions, glossary entrypoint entry, spec links, owner-approval gate) carries forward unchanged.

## Why this proposal

The umbrella GO at -004 authorizes Phase-1 via 4 child bridges. Foundation (Child 1) is VERIFIED at -012, exporting `groundtruth_kb.harness_projection.{read_roles, read_identity, read_capabilities}`. This is the Rule-Files child (Child 2; WI-4330 + WI-4331 + WI-4332 + WI-4338): remove stale legacy-mirror compatibility narrative that still presents the RETIRED `harness-state/role-assignments.json` as if live/authoritative, citing instead the canonical roles SoT (`harness-state/harness-registry.json`) and the canonical reader entrypoint. This child + scripts-source are the two referencer-migration prerequisites that mirror-retirement (Child 4) requires VERIFIED before `harness-state/role-assignments.json` can be deleted.

## Owner-Approval Gate (read first)

**This child cannot be implemented without 8 owner-approved formal-artifact-approval packets.** All 8 edit targets are protected narrative under `config/governance/narrative-artifact-approval.toml` "role-and-governance-rules" (`patterns = [".claude/rules/*.md", "AGENTS.md", "CLAUDE.md", ...]`; `required_evidence = ["approval_packet", "presented_to_user=true", "transcript_captured=true", "explicit_change_request"]`). The `narrative-artifact-approval-gate.py` PreToolUse hook hard-blocks each edit without a matching packet. This is a governed gate, not a defect.

Implementation proceeds in two stages: (1) Codex GO on this proposal (validates the approach + exact deltas before owner effort); (2) per-file owner approval of the 8 packets via the governed packet workflow, then the edits + 2 deletions land. The 2 overlay deletions require no packet.

## Scope (per WI)

### WI-4330 — `.claude/rules/*.md` legacy-mirror compat-clause removal (6 files)

Disposition distinguishes **stale-authority/compat clauses to DROP** from **legitimate retired-historical-evidence to KEEP**:

| File | Disposition |
|------|-------------|
| `.claude/rules/operating-role.md` | DROP the compat parentheticals at L13, L90 ("legacy mirror at role-assignments.json is an orphan compatibility surface... not authoritative") — replace with citation of `harness-registry.json` + the `harness_projection` entrypoint where state semantics matter. KEEP L34/L79/L143 (retirement-provenance prose). |
| `.claude/rules/codex-session-bootstrap.md` | Repoint stale bootstrap guidance (L15/L79/L119/L124/L154) that cites the mirror as a live read source → canonical entrypoint / registry. |
| `.claude/rules/acting-prime-builder.md` | Update L25 role-record reference to cite the registry SoT; retain provenance framing. |
| `.claude/rules/bridge-essential.md` | Update the legacy-mirror narrative (~L145) to cite the registry SoT (file is gated by the Slice-2A SoT-read-discipline hook; reads may need `GTKB_SOT_READ_DISCIPLINE_BYPASS=1`). |
| `.claude/rules/prime-builder-role.md` | Update L16/L84 role-record references to cite the registry SoT exclusively. |
| `.claude/rules/canonical-terminology.md` | Covered under WI-4338 (glossary). |

### WI-4331 — `CLAUDE.md` + `AGENTS.md` role-precedence paragraphs

- `CLAUDE.md:7` — DROP the legacy-mirror sentence from the "Role precedence:" paragraph; cite only the registry SoT + `groundtruth_kb.harness_projection` entrypoint.
- `AGENTS.md` L37 + L52-53 + L243 — analogous treatment.

### WI-4332 — delete 2 overlay rule files

- DELETE `harness-state/claude/operating-role.md` (337 bytes; legacy pointer).
- DELETE `harness-state/codex/operating-role.md` (337 bytes; identical legacy pointer).
- Deletion-risk check (done): repo-wide grep finds NO active code/rule references to these overlay paths; all `operating-role.md` mentions resolve to the ROOT-LEVEL `.claude/rules/operating-role.md` (distinct, remains active).

### WI-4338 — `canonical-terminology.md` glossary

- Update "role assignment" (L704/L729) + "operating role" (L955/L958/L974): drop legacy-mirror parentheticals; cite registry SoT + entrypoint.
- Update "harness identity" (L686/L700): add cross-reference to `read_identity`.
- ADD a new glossary entry "canonical reader entrypoint" per `DCL-CONCEPT-ON-CONTACT-001`.

## Specification Links

| Spec | Severity | Trigger | How this proposal complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via `bridge/INDEX.md` as REVISED versioned bridge file. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification | §Specification-Derived Verification Plan: grep-absent assertion + overlay-deletion confirmation. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:protected narrative edits | 8 formal-artifact-approval packets enumerated in target_paths; per-packet owner approval per `narrative-artifact-approval-gate.py`. |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` | blocking | content:harness-state reads, canonical entrypoint | Narrative now cites the entrypoint/registry as the single read path. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | blocking | content:3 SoT surfaces, retired paths | Narrative consolidated onto the registry SoT; retired-path framing consistent. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:source of truth | Single-sourced narrative authority; stale dual-source removed. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | path:harness-state/**, content:harness | Narrative + overlay cleanup; no role-set VALUE changes. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | PAUTH rowid 134 v2; `protected_narrative_file` + `file_deletion` + `test_file` classes cover ALL mutations in this REVISED (no work-item-lifecycle mutation remains). |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH cites DELIB-20260668 + DELIB-20260880. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 framing specs + Foundation specs satisfied. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items | WI-4330 primary; WI-4331/4332/4338 bundled. This child does NOT mutate work-item rows; backlog visibility maintained; lifecycle resolution deferred to reconciliation bridge. |
| `GOV-12` (WI triggers tests) | blocking | path:work_items, test creation | 1 new platform test (grep-absent assertion). |
| `DCL-CONCEPT-ON-CONTACT-001` | blocking | content:new concepts | New "canonical reader entrypoint" glossary entry added (WI-4338). |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | content:E:\GT-KB | All paths within `E:\GT-KB`. |
| `.claude/rules/project-root-boundary.md` | blocking | path:E:\GT-KB | All target_paths under `E:\GT-KB`. |
| `GOV-08` (KB is truth) | blocking | foundational | Registry SoT canonical; narrative re-pointed to it. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, work item, owner decision | Narrative consolidation + glossary + deletions as governed artifacts. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | Durable governance-narrative consolidation. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:retired | Overlay files retired (deleted); mirror references reframed retired; advances mirror-retirement readiness. |

## Requirement Sufficiency

**Existing requirements sufficient.** Owner-decision evidence: `DELIB-20260668` (8-AUQ) + `DELIB-20260669` (drift evidence) + `DELIB-20260880` (PAUTH v2). No new requirement and (per the F1 fix) no new authorization is invoked — WI resolution is removed, keeping all mutations inside PAUTH v2's classes. The per-file narrative-packet owner approvals are the governed consent mechanism for the protected edits.

## Prior Deliberations

- `bridge/gtkb-platform-sot-consolidation-umbrella-008.md` — grand-umbrella GO.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-001..004` — Phase-1 umbrella; GO at -004.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-012.md` — sibling VERIFIED; provides the entrypoint.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-rule-files-002.md` — Codex NO-GO that drove this revision (F1 PAUTH-class gap + F2 WI-field specificity). Both correct; both addressed via path 1 (remove WI resolution).
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-003.md` — sibling (code/config migration), in verify.
- `DELIB-20260668` — 8-AUQ scope authority (remove non-SoT role references; AUQ#5 overlay deletion).
- `DELIB-20260669` — drift evidence.
- `DELIB-20260880` — PAUTH v2 amendment (preserved v1 mutation-class list — the F1 basis).
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008.md` — predecessor mirror-retirement slice (VERIFIED).

No previously rejected approach is being revisited.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate.

| Decision | Channel | Authority | Shapes |
|---|---|---|---|
| Phase-1 scope + remove non-SoT role refs | AskUserQuestion | DELIB-20260668 (8-AUQ) | Narrative compat-clause removal is recorded scope |
| Delete 2 overlay files (AUQ#5) | AskUserQuestion | DELIB-20260668 (AUQ#5) | WI-4332 overlay deletions |
| PAUTH v2 (covers WI-4330..4338) | AskUserQuestion | DELIB-20260880 | PAUTH coverage |

**Implementation-time owner approvals required (8):** one formal-artifact-approval packet per protected file, presented per-file at implementation time after GO. **No work-item-lifecycle owner authorization is needed for THIS child** (WI resolution deferred to a separate reconciliation bridge).

## Acceptance Criteria

1. **8 protected files edited** under owner-approved packets: legacy-mirror compat clauses dropped; narrative cites `harness-registry.json` + `harness_projection` entrypoint; legitimate retirement-provenance prose retained.
2. **2 overlay files deleted:** `harness-state/{claude,codex}/operating-role.md` removed; no orphaned references.
3. **Glossary updated:** 3 entries de-mirror'd + cite entrypoint; new "canonical reader entrypoint" entry added.
4. **Grep verification:** `.claude/rules/*.md` + CLAUDE.md + AGENTS.md contain no role-assignments.json **stale-authority/compat-clause**; remaining mentions are enumerated retirement-provenance evidence.
5. **No orphaned overlay refs:** grep confirms `operating-role.md` mentions resolve to the root `.claude/rules/operating-role.md`.
6. **Doctor canonical-terminology check** PASSes (required terms preserved).

(WI-4330/4331/4332/4338 lifecycle resolution is intentionally NOT an acceptance criterion of this child; deferred to a later project-completion reconciliation bridge per Codex -002 F1.)

## Phased Implementation Plan

1. **Generate 8 narrative-artifact-approval packets** (one per protected file) with the exact deltas; present each to owner; capture transcript + acknowledgment.
2. **Apply edits** to the 8 protected files (compat-clause drops + entrypoint citations + glossary).
3. **Delete** the 2 overlay files.
4. **Write** `platform_tests/scripts/test_rule_files_role_assignments_cleanup.py` (grep-absent assertion for stale-authority compat-clauses + overlay-absence + new glossary entry present).
5. **Verify:** run the test + `gt project doctor` canonical-terminology check + the harness-state SoT doctor check.
6. **File** `-004.md` post-impl report (NEW) with spec-to-test mapping + preflights. (Pre-file: inline-JSON target_paths; `extract_target_paths` self-check.) The report records that WI lifecycle resolution is deferred (not claimed resolved).

## Specification-Derived Verification Plan

| Spec / requirement | Test / check | Acceptance |
|---|---|---|
| WI-4330/4331 compat-clause removal | `test_rule_files_role_assignments_cleanup.py` (grep-absent) | 0 stale-authority/compat clauses in the 8 files; provenance mentions enumerated |
| WI-4332 overlay deletion | same test (path-absence) | `harness-state/{claude,codex}/operating-role.md` absent; no orphaned refs |
| WI-4338 glossary | same test + `gt project doctor` canonical-terminology | "canonical reader entrypoint" entry present; required terms preserved; entries cite entrypoint |
| `GOV-ARTIFACT-APPROVAL-001` | packet presence at write time | 8 packets exist with matching content hashes + presented_to_user=true |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` | narrative grep | narrative cites the entrypoint/registry as the read path |

## Risk and Rollback

**Risk 1 — owner-packet burden (8 approvals).** Real, unavoidable (governed gate). Mitigation: tightly-scoped deltas; each packet a small reviewable diff; scope pre-settled by DELIB-20260668. Codex may NO-GO with a request to split into per-file sub-children for incremental approval.

**Risk 2 — over-deletion of legitimate provenance.** Mitigation: disposition table distinguishes DROP vs KEEP per file/line; verification asserts 0 stale-*authority* (not 0 mentions).

**Risk 3 — overlay deletion orphans a reference.** Mitigation: repo-wide grep done (no active refs); test asserts post-deletion resolution to the root rule file.

**Risk 4 — bridge-essential.md read gated by SoT-read-discipline hook.** Mitigation: `GTKB_SOT_READ_DISCIPLINE_BYPASS=1` for the read with rationale logged; edit via the packet-gated Write.

**Rollback:** Edits are `protected_narrative_file` class, file-level reversible via git; deletions reversible via git restore. No spec mutations, no KB mutations. If Codex NO-GO: no narrative mutations occur (impl is post-GO + post-packet); this bridge file is superseded by REVISED-N.

## Pre-Filing Preflight Subsection

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-rule-files
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-rule-files
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight green.

---

*Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>*
