NEW

# Phase-1 Rule-Files: drop legacy-mirror compat narrative from 8 protected files + delete 2 overlay files + glossary entrypoint entry

bridge_kind: implementation_proposal
Document: gtkb-harness-state-sot-consolidation-phase-1-rule-files
Version: 001
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-8
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
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

target_paths: ["groundtruth.db", ".claude/rules/operating-role.md", ".claude/rules/canonical-terminology.md", ".claude/rules/acting-prime-builder.md", ".claude/rules/bridge-essential.md", ".claude/rules/codex-session-bootstrap.md", ".claude/rules/prime-builder-role.md", "CLAUDE.md", "AGENTS.md", "harness-state/claude/operating-role.md", "harness-state/codex/operating-role.md", ".groundtruth/formal-artifact-approvals/2026-06-05-RULE-operating-role-md.json", ".groundtruth/formal-artifact-approvals/2026-06-05-RULE-canonical-terminology-md.json", ".groundtruth/formal-artifact-approvals/2026-06-05-RULE-acting-prime-builder-md.json", ".groundtruth/formal-artifact-approvals/2026-06-05-RULE-bridge-essential-md.json", ".groundtruth/formal-artifact-approvals/2026-06-05-RULE-codex-session-bootstrap-md.json", ".groundtruth/formal-artifact-approvals/2026-06-05-RULE-prime-builder-role-md.json", ".groundtruth/formal-artifact-approvals/2026-06-05-NARRATIVE-CLAUDE-md.json", ".groundtruth/formal-artifact-approvals/2026-06-05-NARRATIVE-AGENTS-md.json", "platform_tests/scripts/test_rule_files_role_assignments_cleanup.py"]

# KB-mutation note: groundtruth.db is in target_paths ONLY for work-item status resolution
# (WI-4330/4331/4332/4338) at completion. No spec inserts (Foundation landed the specs).
# Each protected-narrative EDIT requires its own formal-artifact-approval packet (8 packets,
# enumerated in target_paths). The 2 harness-state/*/operating-role.md DELETIONS are NOT
# protected narrative (outside the .claude/rules/ pattern) and need no packet.

requires_verification: true
implementation_scope: implementation

## Why this proposal

The umbrella GO at -004 authorizes Phase-1 via 4 child bridges. Foundation (Child 1) is VERIFIED at -012, exporting `groundtruth_kb.harness_projection.{read_roles, read_identity, read_capabilities}`. This is the Rule-Files child (Child 2; WI-4330 + WI-4331 + WI-4332 + WI-4338): remove stale legacy-mirror compatibility narrative that still presents the RETIRED `harness-state/role-assignments.json` as if it were live/authoritative, citing instead the canonical roles SoT (`harness-state/harness-registry.json`) and the canonical reader entrypoint. This child is one of the two referencer-migration prerequisites (with scripts-source) that the mirror-retirement child (Child 4) requires VERIFIED before `harness-state/role-assignments.json` can be deleted.

## Owner-Approval Gate (read first)

**This child cannot be implemented without 8 owner-approved formal-artifact-approval packets.** All 8 edit targets are protected narrative under `config/governance/narrative-artifact-approval.toml` "role-and-governance-rules" (`patterns = [".claude/rules/*.md", "AGENTS.md", "CLAUDE.md", ...]`; `required_evidence = ["approval_packet", "presented_to_user=true", "transcript_captured=true", "explicit_change_request"]`). The `narrative-artifact-approval-gate.py` PreToolUse hook hard-blocks each edit without a matching packet. This is a governed gate, not a defect: it is the deliberate owner-consent boundary for protected role/governance narrative.

Implementation therefore proceeds in two stages: (1) Codex GO on this proposal (validates the approach + exact deltas before owner effort); (2) per-file owner approval of the 8 packets via the governed packet workflow (each delta presented in native review format, owner-acknowledged, transcript-captured), then the edits + 2 deletions land. The 2 overlay deletions require no packet.

## Scope (per WI)

### WI-4330 — `.claude/rules/*.md` legacy-mirror compat-clause removal (6 files)

A fresh grep finds the compat narrative in 6 rule files (umbrella projected ~5). Disposition distinguishes **stale-authority/compat clauses to DROP** from **legitimate retired-historical-evidence to KEEP** (the latter accurately frames the mirror as retired and is provenance, not active guidance):

| File | Disposition |
|------|-------------|
| `.claude/rules/operating-role.md` | DROP the compat parentheticals at L13, L90 ("legacy mirror at role-assignments.json is an orphan compatibility surface... not authoritative") — replace with citation of `harness-registry.json` + the `harness_projection` entrypoint where state semantics matter. KEEP L34/L79/L143 (retirement-provenance prose). |
| `.claude/rules/codex-session-bootstrap.md` | Repoint stale bootstrap guidance (L15/L79/L119/L124/L154) that cites the mirror as a live read source → canonical entrypoint / registry. (Highest-churn file: bootstrap text reads as if the mirror is current.) |
| `.claude/rules/acting-prime-builder.md` | Update L25 role-record reference to cite the registry SoT; retain provenance framing. |
| `.claude/rules/bridge-essential.md` | Update the legacy-mirror narrative (~L145) to cite the registry SoT (note: this file is gated by the Slice-2A SoT-read-discipline hook; reads may need `GTKB_SOT_READ_DISCIPLINE_BYPASS=1` per `.claude/rules/sot-read-discipline.md`). |
| `.claude/rules/prime-builder-role.md` | Update L16/L84 role-record references to cite the registry SoT exclusively. |
| `.claude/rules/canonical-terminology.md` | Covered under WI-4338 below (glossary). |

### WI-4331 — `CLAUDE.md` + `AGENTS.md` role-precedence paragraphs

- `CLAUDE.md:7` — the "Role precedence:" paragraph currently names `harness-identities.json` + `harness-registry.json` AND adds "The legacy `harness-state/role-assignments.json` mirror is an orphan compatibility surface and is not authoritative." DROP the legacy-mirror sentence; cite only the registry SoT + `groundtruth_kb.harness_projection` entrypoint.
- `AGENTS.md` L37 + L52-53 + L243 — analogous treatment: drop the dual-source legacy-mirror narrative; cite the registry SoT + canonical entrypoint.

### WI-4332 — delete 2 overlay rule files

- DELETE `harness-state/claude/operating-role.md` (337 bytes; legacy pointer "retained only to avoid broken historical references"; incorrectly cites role-assignments.json as authority).
- DELETE `harness-state/codex/operating-role.md` (337 bytes; identical legacy pointer).
- Deletion-risk check (done): a repo-wide grep for these overlay paths finds NO active code/rule references; all `operating-role.md` mentions in CLAUDE.md/AGENTS.md/canonical-terminology.md refer to the ROOT-LEVEL `.claude/rules/operating-role.md` (distinct file, remains active). Deletion orphans nothing.

### WI-4338 — `canonical-terminology.md` glossary

- Update the "role assignment" (L704/L729), "operating role" (L955/L958/L974) glossary entries: drop the legacy-mirror parentheticals; cite the registry SoT + add the canonical entrypoint (`groundtruth_kb.harness_projection.read_roles` / `gt harness role`).
- Update "harness identity" (L686/L700): add cross-reference to `read_identity` (already clean of the mirror).
- ADD a new glossary entry "canonical reader entrypoint" per `DCL-CONCEPT-ON-CONTACT-001` (first-contact concept introduced by Foundation): definition + canonical alias + not-to-be-confused-with + source (DCL-HARNESS-STATE-SOT-READER-CONTRACT-001) + implementation pointer (`groundtruth_kb.harness_projection.{read_roles,read_identity,read_capabilities}`).

## Specification Links

| Spec | Severity | Trigger | How this proposal complies |
|------|----------|---------|---------------------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | doc:*, path:bridge/** | Filed via `bridge/INDEX.md` as NEW versioned bridge file. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | doc:*, content:Specification Links | This section. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | doc:*, content:VERIFIED, verification | §Specification-Derived Verification Plan: grep-absent assertion for stale-authority compat-clauses + overlay-deletion confirmation. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | content:protected narrative edits | 8 formal-artifact-approval packets enumerated in target_paths; per-packet owner approval per `DCL-ARTIFACT-APPROVAL-HOOK-001` + `narrative-artifact-approval-gate.py`. |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` | blocking | content:harness-state reads, canonical entrypoint | Narrative now cites the entrypoint/registry as the single read path. |
| `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` | blocking | content:3 SoT surfaces, retired paths | Narrative consolidated onto the registry SoT; retired-path framing made consistent. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` | blocking | content:source of truth | Single-sourced narrative authority; stale dual-source removed. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | blocking | path:harness-state/**, content:harness | Narrative + overlay cleanup; no role-set VALUE changes. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | content:PAUTH | PAUTH rowid 134 v2; covers WI-4330/4331/4332/4338. `protected_narrative_file` + `file_deletion` are in `allowed_mutation_classes`. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | content:PAUTH envelope | PAUTH cites DELIB-20260668 + DELIB-20260880. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | content:project authorization | PAUTH cites 5 framing specs + the Foundation specs satisfied. |
| `GOV-STANDING-BACKLOG-001` | blocking | path:work_items | WI-4330 primary; WI-4331/4332/4338 bundled; all in PROJECT-GTKB-HARNESS-STATE-SOT-CONSOLIDATION. |
| `GOV-12` (WI triggers tests) | blocking | path:work_items, test creation | 1 new platform test (grep-absent assertion). |
| `DCL-CONCEPT-ON-CONTACT-001` | blocking | content:new concepts | New "canonical reader entrypoint" glossary entry added (WI-4338). |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | content:E:\GT-KB | All paths within `E:\GT-KB`. |
| `.claude/rules/project-root-boundary.md` | blocking | path:E:\GT-KB | All target_paths under `E:\GT-KB`. |
| `GOV-08` (KB is truth) | blocking | foundational | Registry SoT canonical; narrative re-pointed to it. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | content:specification, work item, owner decision | Narrative consolidation + glossary + deletions as governed artifacts. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | content:artifact, deliberation | Durable governance-narrative consolidation. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | content:retired | Overlay files retired (deleted); mirror references reframed retired; advances mirror-retirement readiness. |

## Requirement Sufficiency

**Existing requirements sufficient.** Owner-decision evidence: `DELIB-20260668` (8-AUQ — records the directive to remove non-SoT harness-state/role references) + `DELIB-20260669` (drift evidence) + `DELIB-20260880` (PAUTH v2). No new requirement; this delivers the recorded WI-4330/4331/4332/4338 scope. The per-file narrative-packet owner approvals are the governed *consent* mechanism for the protected edits, not new requirements.

## Prior Deliberations

- `bridge/gtkb-platform-sot-consolidation-umbrella-008.md` — grand-umbrella GO.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-001..004` — Phase-1 umbrella; GO at -004; Child 2 scope at §"Child 2 — rule-files".
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-foundation-012.md` — sibling VERIFIED; provides the entrypoint the narrative now cites.
- `bridge/gtkb-harness-state-sot-consolidation-phase-1-scripts-source-003.md` — sibling (code/config migration), GO at -004, in verify; the two referencer-migration prerequisites for mirror-retirement.
- `DELIB-20260668` — 8-AUQ scope authority (remove non-SoT role references).
- `DELIB-20260669` — drift evidence.
- `DELIB-20260880` — PAUTH v2 amendment.
- `bridge/gtkb-retire-role-assignments-mirror-slice-1-seed-repoint-008.md` — predecessor mirror-retirement slice (VERIFIED).

No previously rejected approach is being revisited.

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate.

| Decision | Channel | Authority | Shapes |
|---|---|---|---|
| Phase-1 scope + remove non-SoT role refs | AskUserQuestion | DELIB-20260668 (8-AUQ) | Narrative compat-clause removal is recorded scope |
| Delete 2 overlay files (AUQ#5) | AskUserQuestion | DELIB-20260668 (AUQ#5) | WI-4332 overlay deletions |
| PAUTH v2 (covers WI-4330..4338) | AskUserQuestion | DELIB-20260880 | PAUTH coverage |

**Implementation-time owner approvals required (8):** one formal-artifact-approval packet per protected file (`operating-role.md`, `canonical-terminology.md`, `acting-prime-builder.md`, `bridge-essential.md`, `codex-session-bootstrap.md`, `prime-builder-role.md`, `CLAUDE.md`, `AGENTS.md`). These are presented per-file at implementation time after GO; they authorize the specific deltas, not re-litigate the scope (which DELIB-20260668 already settled).

## Acceptance Criteria

1. **8 protected files edited** under owner-approved packets: legacy-mirror compat clauses dropped; narrative cites `harness-registry.json` + `harness_projection` entrypoint; legitimate retirement-provenance prose retained.
2. **2 overlay files deleted:** `harness-state/{claude,codex}/operating-role.md` removed; no orphaned references.
3. **Glossary updated:** 3 entries de-mirror'd + cite entrypoint; new "canonical reader entrypoint" entry added.
4. **Grep verification:** `.claude/rules/*.md` + CLAUDE.md + AGENTS.md contain no role-assignments.json **stale-authority/compat-clause** (no "orphan compatibility surface... not authoritative" parentheticals, no read-from-mirror instructions); remaining mentions are enumerated retirement-provenance evidence.
5. **No orphaned overlay refs:** grep confirms `operating-role.md` mentions resolve to the root `.claude/rules/operating-role.md`, not the deleted overlays.
6. **Doctor canonical-terminology check** PASSes (required terms preserved).
7. **WI resolution:** WI-4330/4331/4332/4338 resolved.

## Phased Implementation Plan

1. **Generate 8 narrative-artifact-approval packets** (one per protected file) with the exact deltas; present each to owner; capture transcript + acknowledgment.
2. **Apply edits** to the 8 protected files (compat-clause drops + entrypoint citations + glossary).
3. **Delete** the 2 overlay files.
4. **Write** `platform_tests/scripts/test_rule_files_role_assignments_cleanup.py` (grep-absent assertion for stale-authority compat-clauses in the 8 files + overlay-absence + new glossary entry present).
5. **Verify:** run the test + `gt project doctor` canonical-terminology check + the harness-state SoT doctor check; ruff N/A (no Python edits beyond the test).
6. **Resolve** WI-4330/4331/4332/4338; **file** `-002.md` post-impl report (NEW) with spec-to-test mapping + preflights. (Pre-file: inline-JSON target_paths; `extract_target_paths` self-check.)

## Specification-Derived Verification Plan

| Spec / requirement | Test / check | Acceptance |
|---|---|---|
| WI-4330/4331 compat-clause removal | `test_rule_files_role_assignments_cleanup.py` (grep-absent) | 0 stale-authority/compat clauses in the 8 files; provenance mentions enumerated |
| WI-4332 overlay deletion | same test (path-absence) | `harness-state/{claude,codex}/operating-role.md` absent; no orphaned refs |
| WI-4338 glossary | same test + `gt project doctor` canonical-terminology | "canonical reader entrypoint" entry present; required terms preserved; entries cite entrypoint |
| `GOV-ARTIFACT-APPROVAL-001` | packet presence at write time | 8 packets exist with matching content hashes + presented_to_user=true |
| `DCL-HARNESS-STATE-SOT-READER-CONTRACT-001` | narrative grep | narrative cites the entrypoint/registry as the read path |

## Risk and Rollback

**Risk 1 — owner-packet burden (8 approvals).** Real and unavoidable (governed gate). Mitigation: the deltas are tightly scoped (drop specific compat parentheticals + add entrypoint citations); each packet presents a small, reviewable diff; scope is pre-settled by DELIB-20260668 so approvals confirm wording, not policy. If the owner prefers, Codex may NO-GO with a request to split into per-file or per-WI sub-children for incremental approval.

**Risk 2 — over-deletion of legitimate provenance.** Some role-assignments mentions are accurate retirement records (not stale authority). Mitigation: the disposition table distinguishes DROP vs KEEP per file/line; verification asserts 0 stale-*authority* (not 0 mentions); Codex review invited to flag any mis-classified line.

**Risk 3 — overlay deletion orphans a reference.** Mitigation: repo-wide grep done (no active refs to the overlay paths); the test asserts post-deletion that `operating-role.md` mentions resolve to the root rule file.

**Risk 4 — bridge-essential.md read gated by SoT-read-discipline hook.** Mitigation: implementation uses `GTKB_SOT_READ_DISCIPLINE_BYPASS=1` for the read with rationale logged per `.claude/rules/sot-read-discipline.md`; the edit itself is via the normal packet-gated Write.

**Rollback:** Edits are `protected_narrative_file` class, file-level reversible via git; deletions reversible via git restore. No spec mutations. If Codex NO-GO: no narrative mutations occur (impl is post-GO + post-packet); this bridge file is superseded by REVISED-N.

## Pre-Filing Preflight Subsection

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-rule-files
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-harness-state-sot-consolidation-phase-1-rule-files
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight green.

---

*Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>*
