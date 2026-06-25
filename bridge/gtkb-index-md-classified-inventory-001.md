NEW
author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 03d07d0c-f6a6-4bef-96aa-9d6a06a6ba9d-prime-builder
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory; mode=auto
author_metadata_source: interactive-prime-session

bridge_kind: governance_review

# INDEX.md Reference Classification Contract (WI-4796 — basis for the strip tranches)

Document: gtkb-index-md-classified-inventory
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-06-24 UTC
Project: PROJECT-GTKB-OBSOLETE-REFERENCE-PURGE
Work Item: WI-4796

## Bridge-Kind Disclosure

`bridge_kind: governance_review`. This proposal asks Loyal Opposition to review and
bless the **classification contract** that the strip tranches (WI-4797..WI-4800) will
execute against. It introduces **no source code or KB-row changes**; the deliverable
is the deterministic STRIP / KEEP / QUARANTINE policy plus the category inventory that
applies it. Blessing this contract before any stripping is the safeguard that prevents
the catastrophic failure mode the scan surfaced: a blanket strip would erase the live
`config/agent-control/SESSION-STARTUP-INDEX.md` and the guard machinery.

## Summary

The string `INDEX.md` is overloaded across the GT-KB tree. A faithful execution of the
owner directive ("strip obsolete `bridge/INDEX.md` references; quarantine historical
ones") therefore REQUIRES a classification step before any edit. This contract fixes
that classification deterministically so every strip tranche operates from one blessed
rule set, and so a post-strip check can prove completeness (STRIP set emptied) and
safety (KEEP set intact).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this thread is filed through the governed no-index bridge path; TAFE/dispatcher state plus this status-bearing numbered file are canonical; the QUARANTINE class below preserves the append-only bridge audit trail this spec protects.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this `## Specification Links` section cites every governing spec; verification derives from them (see Verification Plan).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the strip tranches' VERIFIED reports will carry spec-derived verification against this contract; the spec-to-test mapping is defined in `### Specification-Derived Verification — Spec-to-Test Mapping`.
- `ADR-OBSOLETE-REFERENCE-PURGE-OBLIGATION-001` / `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` (proposed, sibling thread `gtkb-obsolete-reference-purge-methodology-adr-dcl`) — this contract is the concrete classification the methodology mandates; the DCL's "STRIP/KEEP/QUARANTINE classification" requirement is satisfied for the `bridge/INDEX.md` retirement by this artifact.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — KEEP rule K1 protects the current SoT artifact (`SESSION-STARTUP-INDEX.md`) from being mistaken for the retired aggregate.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the contract is the lifecycle artifact produced by the `bridge/INDEX.md` retirement trigger.
- `.claude/rules/project-root-boundary.md` — every classified surface is in-root under `E:\GT-KB` (the home-dir Claude memory in the STRIP set is reached under the owner's cross-root memory-purge authorization, AUQ Q3); all paths cited resolve in-root or to the explicitly-authorized harness-memory store.
- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` — owner authorization + AUQ Q1 ("residue only, keep guards") is the source of the KEEP/QUARANTINE boundaries below.

## Prior Deliberations

- `DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` (v1) — authorizing decision; AUQ Q1 "residue only, keep guards" directly fixes the KEEP boundary (guard machinery) and the QUARANTINE boundary (audit trail).
- `DELIB-0862` (v1) — pre-removal snapshot of `bridge/INDEX.md` before stripping historical comment lines: precedent for QUARANTINE-with-justification (freeze, then leave).
- `DELIB-2506` (v1) — "Re-link to Retired Canonical": adjacent disposition for references to a retired canonical; here the disposition is per-reference classification rather than re-link.
- `DELIB-20260673` (v1) — SoT fragmentation from divergent retired aliases; motivates the K1 rule (never strip the current `SESSION-STARTUP-INDEX.md`, which shares the `*INDEX.md` shape).

## Requirement Sufficiency

New requirement required before implementation. This contract IS the requirement that
the strip tranches implement against; it is authorized as spec/governance capture by
`DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624` and is reviewed here before
any strip tranche files. The strip tranches will each carry Requirement Sufficiency =
"Existing requirements sufficient" citing this contract.

## The Classification Contract

A reference is classified by the artifact it NAMES and the role of the file it lives in.

### KEEP — never strip

- **K1 (current artifact).** Any reference to `config/agent-control/SESSION-STARTUP-INDEX.md`, `CODEX-KNOWLEDGE-BASE-INDEX.md`, `CURSOR-KNOWLEDGE-BASE-INDEX.md`, `search_index.json`, or any `*-INDEX.md` that is NOT the retired `bridge/INDEX.md` aggregate. These name live/current artifacts. (~7,561 + ~2,057 live hits.)
- **K2 (guard/enforcement machinery).** References to `bridge/INDEX.md` whose purpose is to BLOCK or DETECT recreation of the retired aggregate: `scripts/protected_mutation_guard.py`, `.claude/hooks/bridge-compliance-gate.py` (+ `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`), `.claude/hooks/lo-file-safety-gate.py`, `scripts/check_skill_health.py`, `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py`, and their tests (`platform_tests/scripts/test_check_commit_pathspec_safety.py`, scaffold-guard tests). A guard must name what it forbids.

### QUARANTINE — never edit (append-only / regenerable)

- **Q1 (append-only audit trail).** `bridge/**` (proposals, reports, verdicts), `independent-progress-assessments/**`, `groundtruth-kb/evidence/**`, `bridge/.authority-cutover/INDEX.frozen-*.md`.
- **Q2 (session transcripts).** `*.jsonl` harness transcripts (in-root and home-dir). Immutable replay/audit.
- **Q3 (generated / cache / archive).** mkdocs `groundtruth-kb/site/**`, KB exports `knowledge-export-*.json`, `.groundtruth/session/**` wrap-scan reports, `.uv-cache*/**`, `**/.venv/**`, `.claude/worktrees/**`, `.pytest-*/**`, `*.bak`/`*.backup*`/`*.drift`, `archive/**`. Regenerated from source or transient; strip the source, not the artifact.

### STRIP / UPDATE — obsolete operational framing (the actual target)

References to the retired `bridge/INDEX.md` aggregate that TEACH or INSTRUCT the old model in a load-bearing reach-path artifact:

- **S1 docs/tutorials** (WI-4797): `groundtruth-kb/docs/tutorials/{dual-agent-setup,bridge-smart-poller,bridge-os-scheduler}.md`, `start-here.md`, `method/12-file-bridge-automation.md`, `reference/cli.md`, `reference/canonical-terminology-detail.md` where they describe `bridge/INDEX.md` as a live queue. (Historical reports `reports/non-disruptive-upgrade-audit.md`, `reports/agent-red-classification.md` → reclassify to QUARANTINE Q1 if they are dated point-in-time records.)
- **S2 tests** (WI-4798): the non-guard subset of the ~28 `groundtruth-kb/tests/**` files that assert retired-queue `bridge/INDEX.md` behavior. Per-test triage required: guard/regression tests are K2 (KEEP).
- **S3 skill-docs** (WI-4799): `.claude/skills/bridge-reconciliation/SKILL.md` + `.codex/`, `.cursor/`, `.agent/` mirrors + `groundtruth-kb/templates/skills/bridge/SKILL.md` where they instruct `bridge/INDEX.md` handling beyond the guard-aware "do not recreate" note.
- **S4 editable harness memory** (WI-4800): in-root `memory/*.md` (~14) + home-dir Claude `memory/*.md` (~94) carrying obsolete `bridge/INDEX.md` operational guidance. Authorized cross-root per AUQ Q3.

### Deterministic decision rule

For each candidate reference R to `bridge/INDEX.md`: if R is in a Q-class path -> QUARANTINE; else if R's enclosing construct blocks/detects recreation -> KEEP (K2); else if R names a non-`bridge/INDEX.md` `*INDEX.md` -> KEEP (K1); else -> STRIP/UPDATE, routed to the S-tranche matching its surface.

## Target Paths / KB Artifacts

target_paths: ["(governance_review: classification contract only; no source/KB mutation in this proposal)"]

The contract is the reviewable deliverable. The strip tranches (separate bridge threads)
carry their own `target_paths` enumerating the concrete S1..S4 files they edit, each under
the project authorization and bridge GO.

## Verification Plan (Specification-Derived)

1. **Safety (KEEP intact).** After all strip tranches reach VERIFIED, a re-scan shows the K1 and K2 reference counts are unchanged (the current `SESSION-STARTUP-INDEX.md` refs and the guard refs survive).
2. **Completeness (STRIP emptied).** The re-scan shows zero remaining obsolete `bridge/INDEX.md` operational-framing references in the S1..S4 surfaces (each either removed or individually re-justified KEEP/QUARANTINE).
3. **Audit untouched.** No `bridge/**`, `independent-progress-assessments/**`, or `*.jsonl` file is modified (Q1/Q2 invariant).

### Specification-Derived Verification — Spec-to-Test Mapping

This governance_review proposal runs no source/tests at proposal time; the mapping below
is what each strip tranche's post-GO implementation report executes as Specification-Derived
Verification:

| Linked spec | Spec-to-test mapping | Command |
|-------------|----------------------|---------|
| `DCL-OBSOLETE-REFERENCE-PURGE-PAIRING-001` (STRIP set emptied) | `test_index_md_strip_completeness` asserts zero obsolete `bridge/INDEX.md` operational refs remain in the tranche's S-surface | `python -m pytest platform_tests/governance/test_index_md_classification_contract.py -q` |
| `DELIB-...-DIRECTIVE-20260624` Q1 (KEEP intact) | `test_index_md_keep_set_intact` asserts K1 (`SESSION-STARTUP-INDEX.md`) and K2 (guard) reference counts are unchanged post-strip | `python -m pytest platform_tests/governance/test_index_md_classification_contract.py -q` |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (audit untouched) | `test_index_md_audit_trail_untouched` asserts no `bridge/**`/IPA/`*.jsonl` file changed | `python -m pytest platform_tests/governance/test_index_md_classification_contract.py -q` |

`ruff check` / `ruff format --check` apply to any Python the strip tranches touch (tests).

## Risk / Rollback

- **Risk:** mis-triage of a test (S2) — classifying a guard test as STRIP would remove regression protection. Mitigation: the decision rule routes guard-purpose refs to K2; S2 requires explicit per-test review, and tranche WI-4798's proposal lists each test's disposition for LO review.
- **Risk:** a historical-report doc (S1) is actually a dated record (should be Q1). Mitigation: the contract flags `reports/*` for reclassification review; tranche WI-4797 confirms per-file.
- **Rollback:** this proposal mutates nothing. Each strip tranche is independently revertible (scoped edits; bridge audit trail preserved).

## Owner Decisions / Input

Depends on owner approval; cites the AUQ-only rule. Authorizing evidence
(`DELIB-OWNER-OBSOLETE-REFERENCE-PURGE-DIRECTIVE-20260624`, AskUserQuestion 2026-06-24):

- **Q1 "Residue only, keep guards"** — defines KEEP (K2 guards) and QUARANTINE (audit) vs STRIP.
- **Q3 "Editable memory only; transcripts stay"** — S4 covers editable `memory/*.md`; Q2 quarantines `*.jsonl` transcripts.
- **"Please proceed" + "Keep building project tranches"** (2026-06-24) — owner authorized continuing to file project tranches while LO dispatch recovers.
