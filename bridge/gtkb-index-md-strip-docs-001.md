NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: da5d93b8-0408-4770-ad6f-00b65fe21530
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory; mode=auto
author_metadata_source: interactive-prime-session

Project Authorization: PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4797

# INDEX.md Residue Strip — Docs + mkdocs Tranche (WI-4797)

Document: gtkb-index-md-strip-docs
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-25 UTC
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4797
Recommended commit type: docs

## Summary

First strip tranche (S1) under the GO-terminal classification contract
(`gtkb-index-md-classified-inventory`, GO at -002). Removes obsolete
`bridge/INDEX.md`-as-live-queue operational framing from 10 reach-path documentation
files, rewriting each to the canonical post-cutover model: **after WI-4510 Phase-3
(2026-06-15), TAFE-backed bridge state plus the status-bearing numbered files under
`bridge/` are canonical**, dispatch is the cross-harness event-driven trigger inspecting
dispatcher/TAFE state, and manual scans read that state. Two dated audit reports are
reclassified QUARANTINE Q1 and left untouched. The mkdocs site regenerates from the
edited source (the generated `site/**` is QUARANTINE Q3 — edit the source, not the
artifact).

This is the docs half of the owner directive's first concrete instance: purge the
retired `bridge/INDEX.md` aggregate's operational residue from load-bearing reach-path
artifacts so it stops competing with canonical sources in agent session-context.

## Specification Links

- `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` (v1, specified) — the constraint this tranche
  satisfies for the S1 surface: the STRIP set's obsolete references are removed (the docs
  surface of clause 3). The spec-derived completeness/safety test is defined below.
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` (v1, specified) — the standing obligation;
  this tranche is part of the paired purge work the obligation requires for the
  `bridge/INDEX.md` retirement.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this `## Specification Links`
  section cites every governing spec; verification derives from them.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the post-implementation report carries
  the spec-derived strip-completeness/KEEP-intact test; mapping in the Verification Plan.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — filed through the governed no-index bridge path; the
  rewrites describe the canonical TAFE/dispatcher authority this spec defines, and the
  QUARANTINE rule preserves the append-only bridge audit trail.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — the rewrites point readers at the current canonical
  bridge state, not the deprecated aggregate; KEEP rule K1 protects the live
  `SESSION-STARTUP-INDEX.md` (not in this tranche's target set).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (CLAUSE-IN-ROOT) — every target path resolves
  in-root under `E:\GT-KB\groundtruth-kb\docs\`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` /
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — this tranche is the lifecycle artifact the
  `bridge/INDEX.md` retirement trigger produces; it preserves traceability across the docs, the
  classification contract, and the new completeness test.

## Prior Deliberations

- `gtkb-index-md-classified-inventory` (GO at -002, terminal) — the blessed STRIP/KEEP/
  QUARANTINE classification contract this tranche executes against; S1 is the docs surface it
  defines. Every disposition below applies the contract's deterministic decision rule.
- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` (v1) — owner authorization;
  AUQ Q1 "residue only, keep guards" fixes the KEEP/QUARANTINE boundaries.
- `gtkb-obsolete-reference-purge-methodology-adr-dcl` (GO at -004, terminal) — the methodology
  ADR/DCL this tranche operationalizes for the docs surface.
- `DELIB-0862` (v1) — pre-removal snapshot precedent for QUARANTINE-with-justification (freeze
  dated records, do not edit them).
- `DELIB-20260673` (v1) — SoT fragmentation evidence: divergent retired aliases competing with
  canonical sources; the motivation for stripping reach-path operational residue.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirements are the GO-terminal classification
contract (`gtkb-index-md-classified-inventory`) plus `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001`
and `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001`. This tranche implements the S1 docs disposition
those artifacts already fixed; it creates no new requirement.

## Target Paths

target_paths: ["groundtruth-kb/docs/architecture/product-split.md", "groundtruth-kb/docs/architecture/isolation.md", "groundtruth-kb/docs/start-here.md", "groundtruth-kb/docs/day-in-the-life.md", "groundtruth-kb/docs/tutorials/dual-agent-setup.md", "groundtruth-kb/docs/tutorials/bridge-smart-poller.md", "groundtruth-kb/docs/tutorials/bridge-os-scheduler.md", "groundtruth-kb/docs/method/12-file-bridge-automation.md", "groundtruth-kb/docs/reference/cli.md", "groundtruth-kb/docs/reference/canonical-terminology-detail.md", "platform_tests/governance/test_index_md_classification_contract.py"]

## Per-File Disposition (deterministic, per the contract's decision rule)

| File | refs | Disposition | Rewrite approach |
|------|------|-------------|------------------|
| `docs/architecture/product-split.md` | 1 | STRIP | L51 "INDEX.md is the authoritative review queue" -> "TAFE-backed bridge state plus the status-bearing numbered files under `bridge/` are the authoritative review queue (after the 2026-06-15 WI-4510 Phase-3 cutover)". |
| `docs/architecture/isolation.md` | 1 | STRIP | L257 replace "`bridge/INDEX.md` and the bridge proposal/review files are filesystem-resident" -> "the bridge proposal/review files and TAFE/dispatcher bridge state are filesystem-resident". |
| `docs/start-here.md` | 2 | STRIP | L353 "inserts a NEW entry at the top of `bridge/INDEX.md`" -> "publishes a NEW entry to TAFE/dispatcher bridge state"; L361 "Both agents poll `bridge/INDEX.md` on a 3-minute cadence via the OS scheduler" -> describe the cross-harness event-driven trigger (no polling; OS scheduler retired). |
| `docs/day-in-the-life.md` | 3 | STRIP | L98 drop "a `bridge/INDEX.md`" from the upgrade-adds list / reframe to dispatcher state; L200 manual-scan fallback -> "manual bridge-state scans"; L209 "update `bridge/INDEX.md`" -> "publish a verdict to bridge state". |
| `docs/tutorials/dual-agent-setup.md` | 5 | STRIP | Rewrite the bridge-automation section to the dispatcher/TAFE model: L26 file-list entry, L65 trigger-fires-on-INDEX, L71 manual-scan, L113 "Register it in `bridge/INDEX.md`". Condense L42's deprecation note to a one-line historical pointer without the literal path token. |
| `docs/tutorials/bridge-smart-poller.md` | 1 | STRIP | Doc documents the retired smart poller; L26 trigger-inspects-INDEX -> dispatcher/TAFE state; add/confirm a retired-mechanism pointer. |
| `docs/tutorials/bridge-os-scheduler.md` | 1 | STRIP | Doc documents the retired OS scheduler; L19 manual-INDEX-scan -> manual bridge-state scan. |
| `docs/method/12-file-bridge-automation.md` | 3 | STRIP | L40 mermaid `IDX[bridge/INDEX.md]` -> dispatcher/TAFE state node; L51 table row "Authoritative review queue and status index" -> TAFE/dispatcher state; L130 manual-scan fallback. |
| `docs/reference/cli.md` | 1 | STRIP | L144 "`bridge` reports live `bridge/INDEX.md` latest-status counts" -> "reports live dispatcher/TAFE latest-status counts". |
| `docs/reference/canonical-terminology-detail.md` | 7 | STRIP | Bridge-thread / GO-NO-GO / smart-poller / cross-harness-trigger / single-harness-dispatcher glossary entries: replace operational `bridge/INDEX.md` framing with TAFE/dispatcher state; historical mentions reworded to "the legacy bridge index aggregate (retired 2026-06-15)" without the literal path token. |
| `docs/reports/non-disruptive-upgrade-audit.md` | 7 | **QUARANTINE Q1** | Dated point-in-time upgrade audit; references describe the audit's own findings, not live guidance. **Not edited.** |
| `docs/reports/agent-red-classification.md` | 1 | **QUARANTINE Q1** | Dated point-in-time classification table. **Not edited.** |

**Rewrite invariant:** every STRIP edit removes the literal `bridge/INDEX.md` token from the
10 target docs (replaced with canonical dispatcher/TAFE language, or a historical phrase that
does not use the path token). This makes the completeness test a clean deterministic grep.

## Verification Plan (Specification-Derived)

New test `platform_tests/governance/test_index_md_classification_contract.py` (the shared
contract test named in the inventory's verification plan; this tranche creates it scoped to the
docs surface; later tranches extend it):

### Specification-Derived Verification — Spec-to-Test Mapping

| Linked spec / clause | Spec-to-test mapping | Command |
|----------------------|----------------------|---------|
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` (STRIP set emptied — docs surface) | `test_docs_strip_completeness` asserts zero `bridge/INDEX.md` tokens remain in the 10 S1 target docs | `python -m pytest platform_tests/governance/test_index_md_classification_contract.py -q --tb=short` |
| `DELIB-...-DIRECTIVE-20260624` AUQ Q1 (KEEP intact) | `test_keep_guard_machinery_intact` asserts the guard files (`scripts/protected_mutation_guard.py`, `.claude/hooks/bridge-compliance-gate.py`, `.claude/hooks/lo-file-safety-gate.py`, `scripts/check_skill_health.py`) still reference `bridge/INDEX.md` (count > 0) | same |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (QUARANTINE audit untouched) | `test_quarantine_reports_untouched` asserts the 2 dated reports still contain their `bridge/INDEX.md` references (not stripped) | same |
| Code quality | `ruff check` + `ruff format --check` on the new test | `python -m ruff check platform_tests/governance/test_index_md_classification_contract.py` ; `python -m ruff format --check <same>` |

Post-impl evidence will also include a manual `mkdocs build` (or a note that the site
regenerates from source) confirming no broken internal links from the rewrites.

## Risk / Rollback

- **Risk: over-strip a legitimate reference.** Mitigated by the per-file table (each edit is
  scoped and listed) and the deterministic rule; historical context is preserved by rewording,
  not deleting meaning.
- **Risk: a "report" is actually live guidance, not a dated record.** Both QUARANTINE files are
  point-in-time audits (row-numbered findings, "Today:" language); their references describe the
  audit, not bridge operation. LO is invited to confirm the QUARANTINE call per file.
- **Risk: broken mkdocs internal links.** Mitigated by a post-edit `mkdocs build` check.
- **Rollback:** all edits are scoped to the 10 docs + 1 new test; reverting them restores prior
  state with no other coupling. The bridge audit trail (QUARANTINE) is never touched.

## Owner Decisions / Input

This tranche proceeds under the governed PAUTH; it cites the AUQ-only rule. Authorizing evidence:

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` (2026-06-24) — owner directive
  authorizing the project and the STRIP/KEEP/QUARANTINE classification (AUQ Q1).
- AskUserQuestion (2026-06-25, this session) — owner selected **"Full project scope"** for the
  PAUTH, then **"Keep building tranches"**, authorizing this docs tranche under
  `PAUTH-PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE-IMPLEMENTATION-2026-06-25`.

No new owner decision is required to GO this tranche. One per-file judgment is surfaced for LO
review: the QUARANTINE Q1 call on the two `docs/reports/*` files.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
