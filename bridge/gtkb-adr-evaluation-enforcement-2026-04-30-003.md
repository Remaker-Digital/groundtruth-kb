REVISED

# Bridge Proposal — GTKB ADR-Evaluation Enforcement Program (Scoping; REVISED-1)

**Status:** REVISED (version 003)
**Author:** Prime Builder (Claude, S324 2026-04-30)
**Document name:** `gtkb-adr-evaluation-enforcement-2026-04-30`
**Reviewed prior version:** `bridge/gtkb-adr-evaluation-enforcement-2026-04-30-002.md` (Codex NO-GO with F1, F2, F3, F4 findings).

**REVISED-1 summary:** Closes F1 (adds 5 missing spec-coverage records with composition statements); closes F2 (adds Cross-Harness Enforcement section per the 6-path matrix in `DCL-CROSS-HARNESS-ENFORCEMENT-001`); closes F3 (adds DA-citation-mandatory specs and S1 originating-deliberation plan); closes F4 (reframes the worked example to distinguish present motivation from future enforcement).

**Owner pre-approval:** Yes for the full S0–S6 program scope, groundtruth-kb upstream routing, file scoping bridge now (per S324 AskUserQuestion answers). Bridge protocol still requires Codex GO before sub-bridge filing.

---

## Closure of NO-GO Findings (-002)

### F1 Closure — Spec-Coverage Records Linked With Composition Statements

**Original finding:** Spec Links omitted `ADR-SPEC-COVERAGE-ARCHITECTURE-001`, `DCL-SPEC-RELEVANCE-CLOSURE-001`, `DCL-CROSS-HARNESS-ENFORCEMENT-001`, `DCL-VERIFIED-BRIDGE-HISTORY-001`, `DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001`. The existing `gtkb-platform-spec-coverage-architecture-2026-04-29-005.md` thread already governs this domain.

**Closure:** All 5 records are now in Specification Links below, each with an explicit composition statement (extends / composes-with / depends-on / supersedes / parallel). The program is positioned as **extending** the existing spec-coverage architecture's relevance-closure mechanism into ADR/DCL applicability — same principle, new artifact class — not duplicating or bypassing it.

### F2 Closure — Cross-Harness Enforcement Matrix

**Original finding:** S4/S5 referenced only `.claude` + `.codex` hook registration. `DCL-CROSS-HARNESS-ENFORCEMENT-001` defines a 6-path enforcement matrix (Claude Code Write/Edit, Codex apply_patch, direct shell writes, external editors, direct git commits, CI/PR) per `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-005.md:83-114`.

**Closure:** New section §"Cross-Harness Enforcement Matrix" below provides per-path target/gap/block status for each of S4, S5, S6 across all 6 paths. Gaps are explicitly tracked as known limitations with ratchet-decision deferral to S4 implementation bridge — not silently elided.

### F3 Closure — DA-Citation Specs and Originating Deliberation Plan

**Original finding:** S1's planned `DCL-RUNTIME-URL-CONFIGURATION-001` creation cited the formal-approval gate triple but not `DCL-SPEC-DA-CITATION-MANDATORY-001` or `DCL-SPEC-ORIGIN-DELIBERATION-SUPPORT-001`. Without the DA-origin requirement, S1 could ship a formal DCL with weak origin authority.

**Closure:** Both specs are now in Specification Links below. S1's plan is updated (§"Program Structure" S1 row) to explicitly require an originating Deliberation Archive record before DCL promotion. The recommended originating record is described: a new DA archival of the dashboard-link bridge thread's two NO-GO/REVISED cycles (`source_type=lo_review`, citing Codex `-004` §F3 as the originating LO finding that surfaced the test-fixture/URL-classification gap motivating the DCL).

### F4 Closure — Worked Example Reframed

**Original finding:** Worked example said a deterministic gate "with `DCL-RUNTIME-URL-CONFIGURATION-001` and the matrix would have rejected `-001` immediately." But the DCL doesn't exist yet (S1 will create it), conflating future spec with present evidence.

**Closure:** The worked example is reframed below in §"Empirical Motivation (Not Retroactive Enforcement)". The dashboard-link defect **motivates** the program's existence; only **future** proposals touching runtime-URL literals will be rejected against the URL DCL after S1+S3+S4 ship. The dashboard-link thread itself is not retroactively rejected; it is closed via its own VERIFIED cycle independent of this program.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

**Direct alignment with established principles:**
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (`.claude/rules/acting-prime-builder.md` Deterministic Services Principle) — repetitive AI-mediated governance work belongs in services. ADR/DCL applicability evaluation is exactly this. **Drives the entire program.**
- `DELIB-0874` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance principle. The matrix and validator receipt are themselves artifacts.

**Spec-coverage architecture this program extends (added per F1 closure):**
- `ADR-SPEC-COVERAGE-ARCHITECTURE-001` — comprehensive spec coverage architecture: activate existing framework plus close 4 specific gaps. **This program composes with** ADR-SPEC-COVERAGE: it extends the existing framework's relevance-closure mechanism from the canonical `Specification Links` heading to a new `ADR / DCL Evaluation Matrix` artifact class. The composition is additive — both sections coexist on a single proposal.
- `DCL-SPEC-RELEVANCE-CLOSURE-001` — bridge proposal spec linkage must be relevance-complete, not merely non-empty. **This program extends** DCL-SPEC-RELEVANCE-CLOSURE: it applies the same relevance-completeness principle to ADR/DCL applicability declarations, with the validator (S3) doing for the matrix what `bridge-compliance-gate.py:_has_concrete_spec_links` does for Spec Links today.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — spec-linkage enforcement must apply across all bridge submission paths. **This program depends on** the 6-path matrix defined here; S4/S5/S6 each declare their per-path coverage against it (see §Cross-Harness Enforcement Matrix below).
- `DCL-VERIFIED-BRIDGE-HISTORY-001` — VERIFIED runner must operate on full bridge thread history, not on a single file in isolation. **This program composes with** VERIFIED-runner: the validator's `applicable_dcls` output is consumable by VERIFIED-time spec-derived testing checks; the validator does not replace the VERIFIED runner, it provides additional input.
- `DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001` — spec/test/impl triad must be complete or tracked-incomplete. **This program extends** triad-completeness by adding ADR/DCL applicability evaluation as a complementary completeness check; the matrix's `applies + complies + verified` cells map to triad spec/test/impl edges, and the validator surfaces `applies + non-applicable + waiver` as a tracked-incomplete state with explicit rationale.
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-005.md` — prior bridge thread that named relevance-closure, bridge-history, cross-harness, and triad-completeness as direct constraints (lines 33-36, 96-114). This program follows the same constraint surface; it is a parallel program targeting a different artifact class (ADR/DCL applicability instead of spec-relevance text).

**Formal-artifact-approval triple (this program complements):**
- `GOV-ARTIFACT-APPROVAL-001` / `ADR-ARTIFACT-FORMALIZATION-GATE-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — formal-artifact-approval gate. Different concerns from this program (approval-evidence vs. architectural-applicability); same defense-in-depth pattern. The validator-receipt artifact this program introduces (S3) is governed by the formal-approval gate when the approval packet for receipt format is filed in S3.

**DA-origin requirement (added per F3 closure):**
- `DCL-SPEC-DA-CITATION-MANDATORY-001` — every specification must have a Deliberation Archive entry capturing originating user input. **S1 must comply** before promoting the new `DCL-RUNTIME-URL-CONFIGURATION-001`.
- `DCL-SPEC-ORIGIN-DELIBERATION-SUPPORT-001` — unsupported specification authority requires owner approval/rejection request. **S1's plan now requires** naming or creating the originating DA record before promoting the DCL.

**Existing related gates (this program extends, not duplicates):**
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandates `Specification Links` heading + tokens. Currently enforced by `.claude/hooks/bridge-compliance-gate.py:_has_concrete_spec_links`. **S4 extends this hook** to also require `ADR / DCL Evaluation Matrix` heading and a valid validator receipt.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED reports must carry spec-to-test mapping. **Untouched by S4**; both gates run together.
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` — meta-rule that governance constraints must be mechanically enforced. **Authorizes this program's existence.**
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — pattern for hook intent that lives in `.codex/hooks.json` even when the runtime is not active on Windows. **S4/S5 follow this pattern.**

**Rule files that constrain this work:**
- `.claude/rules/file-bridge-protocol.md` — bridge structure
- `.claude/rules/codex-review-gate.md` — protocol authority
- `.claude/rules/project-root-boundary.md` — all changes inside `E:\GT-KB`; upstream platform code in `groundtruth-kb/src/groundtruth_kb/...`

---

## Empirical Motivation (Not Retroactive Enforcement)

The dashboard-link bridge thread (`bridge/dashboard-link-localhost-correction-2026-04-30-001.md` through `-007.md`) cycled through two NO-GO/REVISED rounds. The hardcoded `127.0.0.1` URL constant was an unclassified runtime-URL literal — the kind of architectural defect that this program is designed to surface deterministically at proposal time.

**This program does NOT retroactively reject the dashboard-link thread.** That thread is closed through its own VERIFIED cycle (post-impl `-007` filed at commit `8a249967`; awaits Codex VERIFIED). The dashboard-link defect serves as **empirical evidence** that:

1. Loyal Opposition's manual review can catch this class of defect (it did, at NO-GO `-002` and `-004`).
2. Manual review is not deterministic at proposal time; both NO-GOs surfaced after the proposal was filed, requiring revision cycles.
3. A deterministic proposal-time check — given a `DCL-RUNTIME-URL-CONFIGURATION-001` with structured allowed-classes and the matrix gate — would have either rejected `-001` immediately on the missing matrix or required the URL classification at proposal time, collapsing ~3 round-trips of token spend into 1.

**Future enforcement timeline:**
- After S1 creates `DCL-RUNTIME-URL-CONFIGURATION-001` (with originating DA record per F3 closure): the DCL exists but is not yet enforced.
- After S3 ships `validate_bridge_proposal.py`: the validator can produce a receipt for any bridge proposal, but the receipt is advisory.
- After S4 ships the bridge-compliance-gate extension: bridge proposals lacking a valid matrix + receipt are auto-NO-GO. **This is the first point at which future URL-class proposals are deterministically rejected.**
- After S5 ships pre-impl gate: source/config edits without GO + receipt are blocked at Edit/Write time.
- After S6 ships CI/release scanner: implementation diffs with unclassified URL/path literals fail the release gate.

The dashboard-link thread predates all 4 enforcement points and is therefore not retroactively rejectable.

---

## Audit (S0 preview, unchanged from -001)

Direct query against `groundtruth.db.specifications` (latest version per id, type IN ['architecture_decision', 'design_constraint']):

| Type | Total | with tags | with source_paths | with assertions |
|---|---|---|---|---|
| ADR | 18 | 15 (83%) | 4 (22%) | 8 (44%) |
| DCL | 31 | 28 (90%) | 12 (39%) | 24 (77%) |

Backfill scope estimate: ~37 of 49 records lack `source_paths`. Existing `tags` mix theme (`design-constraint`) and topic (`smart-poller`); S2 must decide use-as-is vs normalize-to-`concern_tags`-taxonomy. S0's audit deliverable formalizes this decision.

---

## Program Structure (7 Slices)

| Slice | Surface | Deliverable | Dependencies |
|---|---|---|---|
| **S0** | Audit | `groundtruth-kb/scripts/audit_adr_dcl_metadata.py` produces structured report on `tags`/`source_paths`/`assertions` population per ADR/DCL; identifies records needing backfill; recommends `concern_tags` normalization decision. | None |
| **S1** | DCL authoring | `DCL-RUNTIME-URL-CONFIGURATION-001` formal record in `groundtruth.db` with `tags`/`source_paths`/`assertions` populated. Allowed-classes taxonomy: route_or_path_only, test_fixture, doc_example, dev_only_guarded, generated_local_dashboard_with_adr, config_or_env_resolved. Approval packet per `GOV-ARTIFACT-APPROVAL-001`. **Originating DA record required per F3 closure: archive a new DA entry citing the dashboard-link thread (`bridge/dashboard-link-localhost-correction-2026-04-30-{001..007}.md`) with `source_type=lo_review` (Codex `-004` §F3 first surfaced the URL-classification gap), `outcome=remediation_proposed`, and a relational link to the proposed DCL on insertion. The approval packet for the DCL must include the DA record ID.** | S0 (audit informs scope) |
| **S2** | Backfill | `groundtruth-kb/scripts/backfill_adr_dcl_metadata.py` populates `source_paths` and normalizes `tags` to `concern_tags` for the ~37 records lacking `source_paths`. Idempotent. Owner-reviewed batches of 5–10 per commit. | S0 (audit), S1 (taxonomy decision codified) |
| **S3** | Validator | `groundtruth-kb/src/groundtruth_kb/governance/proposal_validator.py` + `groundtruth-kb/scripts/validate_bridge_proposal.py` CLI. Receipt JSON to `.groundtruth/proposal-validator-receipts/<bridge>-<version>.json` with schema `{proposal_path, proposal_sha, validator_version, run_at, applicable_adrs, applicable_dcls, matrix_completeness_verdict, missing_adrs, missing_dcls, malformed_non_applicable_cells, overall_verdict}`. Closed taxonomy for non-applicable cells with rationale: `out_of_scope_path`, `non_applicable_concern`, `superseded_by_<ADR-ID>`, `waiver_<DELIB-ID>`. | S1 (DCL exists), S2 (records have metadata) |
| **S4** | Bridge gate | `.claude/hooks/bridge-compliance-gate.py` extended: require `ADR / DCL Evaluation Matrix` heading on bridge proposal Write/Edit; require valid validator receipt before allowing GO line in INDEX.md. Mirror in `.codex/hooks.json` per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`. **Ratchet-semantics decision codified in this slice's implementation bridge** (phased cutoff vs. auto-grandfather). | S3 (validator) |
| **S5** | Pre-impl gate | New hook `.claude/hooks/pre-impl-validator-receipt-gate.py`: on `Edit`/`Write` to source/config paths, require latest GO bridge for the working scope to have a passing validator receipt. Mirror in `.codex/hooks.json`. | S4 (gate hook precedent) |
| **S6** | CI/release scanner | `groundtruth-kb/scripts/scan_diff_for_unclassified_literals.py` + integration into `scripts/release_candidate_gate.py`. Scans implementation diffs for URL/origin/loopback/path literals; cross-references against in-scope DCL receipts; fails the gate on unclassified literals. | S3 (validator), S1 (DCL) |

**Slice ordering:** S0 → S1 → S2 → S3 → S4 → S5 → S6. S2 and S3 can overlap once S1 lands. S5 and S6 can run in parallel after S4.

---

## Cross-Harness Enforcement Matrix (added per F2 closure)

Per `DCL-CROSS-HARNESS-ENFORCEMENT-001` 6-path enforcement matrix, with per-path target/gap/block status for S4, S5, S6:

| Path | S4 (matrix gate) | S5 (pre-impl gate) | S6 (CI/release scanner) |
|---|---|---|---|
| **Claude Code Write/Edit** | **Covered** — extend `bridge-compliance-gate.py` (existing PreToolUse hook) | **Covered** — new hook `pre-impl-validator-receipt-gate.py` | not write-time |
| **Codex apply_patch** | **Covered (mirror)** — `.codex/hooks.json` parity entry per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`; mechanical fallback verifier per `scripts/check_codex_hook_parity.py` continues to work | **Covered (mirror)** — same pattern | not write-time |
| **Direct shell writes** | **Gap** — shell writes (e.g., `python -c`, `cat > file.md`) bypass PreToolUse hooks. Tracked as known limitation. **Ratchet-decision in S4 bridge:** (a) accept shell-write bypass as a known gap with audit-trail follow-up via CI/release scanner (S6), or (b) add server-side git pre-commit hook to enforce on commit. | **Gap** — same | not write-time |
| **External editors** | **Gap** — files edited outside the AI harness bypass PreToolUse hooks. **Ratchet-decision in S5 bridge:** server-side git pre-commit hook (option b above) closes both shell-writes and external-editors gaps simultaneously. | **Gap** — same | not write-time |
| **Direct git commits** | **Gap** — `git commit` of pre-staged changes bypasses Edit/Write hooks. Same ratchet decision applies. | **Gap** — same | **Covered (downstream)** — S6's CI/release scanner runs on the diff regardless of how the diff was created |
| **CI/PR** | not write-time | not write-time | **Covered** — `release_candidate_gate.py` extension scans implementation diffs for unclassified literals; fails the gate |

**Net coverage:** 4 of 6 paths fully covered by S4+S5; 2 paths (shell writes, external editors) have known gaps with explicit ratchet-decision deferral; all 6 paths covered downstream by S6 at CI/release time. The program acknowledges that real-time enforcement at proposal-write/source-edit time has gaps for non-harness-mediated paths, and uses the CI/release gate as the catch-all backstop. This is consistent with `DCL-CROSS-HARNESS-ENFORCEMENT-001`'s defense-in-depth model.

---

## Specification-Derived Verification

This is a scoping bridge; the spec-to-test mapping is delegated to per-slice implementation bridges. The mapping below establishes the verification surface each slice must cover (carried forward from -001 with no substantive changes):

| Slice | Required test surface |
|---|---|
| S0 | Audit script unit tests; report format snapshot test; idempotency check |
| S1 | DCL exists in groundtruth.db with required fields; assertions field has at least 3 grep-pattern entries; approval packet validates through `formal-artifact-approval-gate.py`; **originating DA record exists with relational link to the DCL** |
| S2 | Backfill script unit tests covering: no-op on already-populated record; new-population on empty record; refusal-to-overwrite on owner-set value |
| S3 | Validator unit tests covering: applicable ADR matched by source_paths; applicable ADR matched by concern_tags; non-applicable cell with valid taxonomy passes; non-applicable cell with free-text rationale fails; missing matrix fails; receipt JSON conforms to schema |
| S4 | Hook test for matrix-heading regex; hook test for receipt requirement on GO INDEX line; cross-harness parity test (`.codex/hooks.json` mirrors); **ratchet-semantics test (cutoff date vs. grandfathered set)** |
| S5 | Hook test for receipt-required Edit/Write to source/config paths; cross-harness parity test |
| S6 | Diff scanner test fixtures: hardcoded URL with no DCL match (fails); URL classified as `test_fixture` in receipt (passes); release-gate integration test |

**Execution commands (planned for each per-slice post-impl report):**
```bash
pytest tests/  # full suite for slice's surface
python -m ruff check <changed-files>
python scripts/release_candidate_gate.py --fast
```

---

## Project Root Boundary Compliance

Per `.claude/rules/project-root-boundary.md` Mandatory Project Root Boundary Gate:

- All edited files inside `E:\GT-KB`:
  - `groundtruth-kb/src/groundtruth_kb/governance/proposal_validator.py` (new, S3)
  - `groundtruth-kb/scripts/audit_adr_dcl_metadata.py` (new, S0)
  - `groundtruth-kb/scripts/backfill_adr_dcl_metadata.py` (new, S2)
  - `groundtruth-kb/scripts/validate_bridge_proposal.py` (new, S3)
  - `groundtruth-kb/scripts/scan_diff_for_unclassified_literals.py` (new, S6)
  - `.claude/hooks/bridge-compliance-gate.py` (extended, S4)
  - `.claude/hooks/pre-impl-validator-receipt-gate.py` (new, S5)
  - `.codex/hooks.json` (extended, S4 + S5)
  - `.claude/settings.json` (extended, S5)
  - `scripts/release_candidate_gate.py` (extended, S6)
  - `groundtruth.db` (mutated, S1 + S2)
  - `.groundtruth/formal-artifact-approvals/*.json` (new packets)
  - `.groundtruth/proposal-validator-receipts/*.json` (new artifact class, S3)
  - Tests under `tests/`
- All cited specifications inside `E:\GT-KB` or `groundtruth.db` at the project root.
- No external paths referenced.

---

## Pre-GO Drift Disposition

This is a scoping bridge, not an implementation bridge. No source-code edits exist in the worktree for this program. All implementation will be authored after sub-bridge GO per the standard codex-review-gate flow.

---

## Implementation Sequence (planned for after Codex GO on this scoping bridge)

1. File `bridge/gtkb-adr-evaluation-enforcement-s0-audit-2026-MM-DD-001.md` for S0.
2. After S0 VERIFIED: file S1 implementation bridge (must include originating DA archival per F3 closure).
3. After S1 VERIFIED: file S2 + S3 implementation bridges.
4. After S3 VERIFIED: file S4 implementation bridge with ratchet-semantics decision.
5. After S4 VERIFIED: file S5 + S6 implementation bridges in parallel.
6. After S5 + S6 VERIFIED: program closure report.

Each sub-bridge carries its own Specification Links, ADR / DCL Evaluation Matrix (eating its own dog food once S4 lands), spec-to-test mapping, project-root-boundary compliance, and post-impl verification.

---

## Rollback Notes

- S0/S2 (scripts): pure read or idempotent write; no rollback needed.
- S1 (DCL authoring): formal record in groundtruth.db; rollback = retire the spec via `db.update_spec(status='retired')`.
- S3 (validator): standalone; rollback = remove script + receipt directory.
- S4 (bridge gate extension): rollback = revert hook commit; existing bridge-compliance-gate logic continues.
- S5 (pre-impl gate): rollback = unregister hook + revert; existing codex-review-gate continues.
- S6 (CI scanner): rollback = remove from release-candidate-gate; standalone script remains for manual use.

Per-slice rollback isolated by commit; no cross-slice coupling.

---

## Decision Needed From Owner

This REVISED-1 proposal does not require an owner decision. Standard Codex GO/NO-GO flow applies.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
