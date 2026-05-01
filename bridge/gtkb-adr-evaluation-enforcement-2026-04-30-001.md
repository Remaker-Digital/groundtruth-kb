NEW

# Bridge Proposal — GTKB ADR-Evaluation Enforcement Program (Scoping)

**Status:** NEW (version 001)
**Author:** Prime Builder (Claude, S324 2026-04-30)
**Document name:** `gtkb-adr-evaluation-enforcement-2026-04-30`
**Trigger:** S324 owner directive after the dashboard-link bridge thread (`bridge/dashboard-link-localhost-correction-2026-04-30-*`) cycled through two NO-GO/REVISED rounds. The hardcoded `127.0.0.1` URL was a `DCL-RUNTIME-URL-CONFIGURATION` class violation that should have been caught at proposal time by a deterministic ADR/DCL applicability check, not by Loyal Opposition's manual review. This bridge proposes the program that turns ADR/DCL evaluation from "Loyal Opposition should notice" into a deterministic proposal gate.

**Owner pre-approval:** Yes — for the full S0-S6 program scope, groundtruth-kb upstream routing, file scoping bridge now (per S324 AskUserQuestion answers). Bridge protocol still requires Codex GO before sub-bridge filing per `.claude/rules/codex-review-gate.md`.

**Scoping bridge intent:** Establish the program's slice structure, dependencies, and acceptance criteria. Each slice files its own implementation bridge. This scoping bridge authorizes Prime to file sub-bridges for S0-S6 in sequence (or parallel where dependencies permit) under the standard NEW -> review -> GO -> impl -> post-impl -> VERIFIED protocol.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

**Direct alignment with established principles:**
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (`.claude/rules/acting-prime-builder.md` Deterministic Services Principle) — repetitive AI-mediated governance work where AI substantive contribution is < 20% of total work belongs in services. ADR/DCL applicability evaluation is exactly this: a per-proposal lookup of "which ADRs apply to these touched files" is mechanical given metadata; the AI value-add is the rationale for "applies but N/A" cases. **Drives the entire program.**
- `DELIB-0874` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance principle. ADR/DCL applicability matrix is itself an artifact; the validator receipt is itself an artifact.
- `GOV-ARTIFACT-APPROVAL-001` / `ADR-ARTIFACT-FORMALIZATION-GATE-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — formal-artifact-approval gate which this program complements (formal-approval gate verifies approval evidence; ADR-evaluation gate verifies architectural compliance). Different concerns, same defense-in-depth pattern.

**Existing related gates (this program extends, not replaces):**
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandates `## Specification Links` heading + tokens. Currently enforced by `.claude/hooks/bridge-compliance-gate.py:_has_concrete_spec_links`. **S4 extends this hook to also require `## ADR / DCL Evaluation Matrix` heading.**
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED reports must carry spec-to-test mapping. Same hook enforces. **S4 extension does not modify this check; both gates run together.**
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` — meta-rule that governance constraints must be mechanically enforced. **Authorizes this program's existence.**
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — pattern for hook intent that lives in `.codex/hooks.json` even when the runtime is not active on Windows. **S4/S5 follow this pattern: register hook intent in both `.claude/settings.json` and `.codex/hooks.json`.**

**Rule files that constrain this work:**
- `.claude/rules/file-bridge-protocol.md` — bridge structure
- `.claude/rules/codex-review-gate.md` — protocol authority
- `.claude/rules/project-root-boundary.md` — all changes inside `E:\GT-KB`; upstream platform code in `groundtruth-kb/src/groundtruth_kb/...`

**Concrete worked example (empirical evidence motivating this work):**
- `bridge/dashboard-link-localhost-correction-2026-04-30-001.md` through `-005.md` — 2 NO-GO/REVISED cycles. The hardcoded URL was an unclassified runtime-URL literal; a deterministic gate with `DCL-RUNTIME-URL-CONFIGURATION-001` and the matrix would have rejected `-001` immediately on the missing matrix, and `-003` on the missing URL classification. ~3 round trips of token spend would have collapsed to 1.

---

## Audit (S0 preview)

Direct query against `groundtruth.db.specifications` (latest version per id, type IN ['architecture_decision', 'design_constraint']):

| Type | Total | with tags | with source_paths | with assertions |
|---|---|---|---|---|
| ADR | 18 | 15 (83%) | 4 (22%) | 8 (44%) |
| DCL | 31 | 28 (90%) | 12 (39%) | 24 (77%) |

**Backfill scope estimate:** ~37 of 49 records lack `source_paths` — that is the principal gap. Existing `tags` are well-populated but mix theme tags (`design-constraint`, `mechanical-enforcement`) with topic tags (`smart-poller`, `session-startup`); S2 must decide between use-as-is (cheap, lossy matcher) or normalize-to-`concern_tags`-taxonomy (expensive, more deterministic). S0's audit deliverable formalizes this decision with concrete coverage data.

---

## Program Structure (7 Slices)

| Slice | Surface | Deliverable | Dependencies |
|---|---|---|---|
| **S0** | Audit | `groundtruth-kb/scripts/audit_adr_dcl_metadata.py` produces a structured report on `tags`/`source_paths`/`assertions` population per ADR/DCL; identifies records needing backfill; recommends `concern_tags` normalization decision. | None |
| **S1** | DCL authoring | `DCL-RUNTIME-URL-CONFIGURATION-001` formal record in `groundtruth.db` with `tags`/`source_paths`/`assertions` populated. Allowed-classes taxonomy: route_or_path_only, test_fixture, doc_example, dev_only_guarded, generated_local_dashboard_with_adr, config_or_env_resolved. Approval packet per `GOV-ARTIFACT-APPROVAL-001`. | S0 (audit informs scope) |
| **S2** | Backfill | `groundtruth-kb/scripts/backfill_adr_dcl_metadata.py` populates `source_paths` (path globs) and normalizes `tags` to `concern_tags` for the ~37 records lacking `source_paths`. Idempotent (running twice produces no-op). Owner-reviewed batches of 5-10 per commit. | S0 (audit), S1 (taxonomy decision codified in one record) |
| **S3** | Validator | `groundtruth-kb/src/groundtruth_kb/governance/proposal_validator.py` + `groundtruth-kb/scripts/validate_bridge_proposal.py` CLI. Takes bridge document name; returns receipt JSON to `.groundtruth/proposal-validator-receipts/<bridge>-<version>.json`. Receipt schema: `{proposal_path, proposal_sha, validator_version, run_at, applicable_adrs, applicable_dcls, matrix_completeness_verdict, missing_adrs, missing_dcls, malformed_n_a_cells, overall_verdict}`. Closed taxonomy for "N/A with rationale": `out_of_scope_path`, `non_applicable_concern`, `superseded_by_<ADR-ID>`, `waiver_<DELIB-ID>`. | S1 (DCL exists), S2 (records have metadata) |
| **S4** | Bridge gate | `.claude/hooks/bridge-compliance-gate.py` extended: require `## ADR / DCL Evaluation Matrix` heading on bridge proposal Write/Edit; require valid validator receipt before allowing GO line in INDEX.md. Mirror in `.codex/hooks.json` per `ADR-CODEX-HOOK-PARITY-FALLBACK-001`. | S3 (validator must exist) |
| **S5** | Pre-impl gate | New hook `.claude/hooks/pre-impl-validator-receipt-gate.py` (or extension of existing): on `Edit`/`Write` to source/config paths, require latest GO bridge for the working scope to have a passing validator receipt. Mirror in `.codex/hooks.json`. | S4 (gate hook precedent) |
| **S6** | CI/release scanner | `groundtruth-kb/scripts/scan_diff_for_unclassified_literals.py` + integration into `scripts/release_candidate_gate.py`. Scans implementation diffs for URL/origin/loopback/path literals; cross-references against in-scope DCL receipts; fails the gate on unclassified literals. | S3 (validator), S1 (DCL defining the literal classes) |

**Slice ordering:** S0 -> S1 -> S2 -> S3 -> S4 -> S5 -> S6. S2 and S3 can overlap once S1 lands. S5 and S6 can run in parallel after S4.

**Ratchet semantics decision (deferred to S4):** Per the design discussion, the gate must decide between (a) phased — gate enforces only on bridges filed after a cutoff date — or (b) auto-grandfather by bridge-thread-start-date with remediation work items. S4's implementation bridge will propose one and document the chosen ratchet in the bridge-compliance-gate hook source.

---

## Specification-Derived Verification

This is a scoping bridge; the spec-to-test mapping is delegated to per-slice implementation bridges per `.claude/rules/file-bridge-protocol.md`. The mapping below establishes the verification surface each slice must cover:

| Slice | Required test surface |
|---|---|
| S0 | Audit script unit tests; report format snapshot test; idempotency check (running twice produces same report bytes) |
| S1 | DCL exists in groundtruth.db with required fields; assertions field has at least 3 grep-pattern entries; approval packet validates through `formal-artifact-approval-gate.py` |
| S2 | Backfill script unit tests covering: no-op on already-populated record; new-population on empty record; refusal-to-overwrite on owner-set value |
| S3 | Validator unit tests covering: applicable ADR matched by source_paths; applicable ADR matched by concern_tags; N/A cell with valid taxonomy passes; N/A cell with free-text rationale fails; missing matrix fails; receipt JSON conforms to schema |
| S4 | Hook test for matrix-heading regex; hook test for receipt requirement on GO INDEX line; cross-harness parity test (`.codex/hooks.json` mirrors) |
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
  - `.groundtruth/formal-artifact-approvals/*.json` (new approval packet for S1's DCL)
  - `.groundtruth/proposal-validator-receipts/*.json` (new artifact class, S3)
  - Tests under `tests/` for each slice
- All cited specifications inside `E:\GT-KB` or `groundtruth.db` at the project root.
- No external paths (`E:\Claude-Playground`, home-directory, sibling checkouts) are referenced.
- Upstream routing (per S324 owner direction): platform code lives in `groundtruth-kb/`; adopters consume via `gt project upgrade` after upstream VERIFIED.

---

## Pre-GO Drift Disposition

This is a scoping bridge, not an implementation bridge. No source-code edits exist in the worktree for this program. All implementation will be authored after sub-bridge GO per the standard codex-review-gate flow.

---

## Implementation Sequence (planned for after Codex GO on this scoping bridge)

1. File `bridge/gtkb-adr-evaluation-enforcement-s0-audit-2026-MM-DD-001.md` for S0.
2. After S0 VERIFIED: file S1 implementation bridge.
3. After S1 VERIFIED: file S2 + S3 implementation bridges (S3 may begin once S2 is in flight; full GO requires S2 VERIFIED).
4. After S3 VERIFIED: file S4 implementation bridge.
5. After S4 VERIFIED: file S5 + S6 implementation bridges in parallel.
6. After S5 + S6 VERIFIED: program closure report.

Each sub-bridge carries its own Specification Links, ADR/DCL Evaluation Matrix (eating its own dog food once S4 lands), spec-to-test mapping, project-root-boundary compliance, and post-impl verification.

---

## Rollback Notes

- S0/S2 (audit + backfill scripts): pure read or idempotent write; no rollback needed.
- S1 (DCL authoring): formal record in groundtruth.db; rollback = retire the spec via `db.update_spec(status='retired')`.
- S3 (validator): standalone; rollback = remove script + receipt directory.
- S4 (bridge gate extension): rollback = revert hook commit; existing bridge-compliance-gate logic continues.
- S5 (pre-impl gate): rollback = unregister hook + revert; existing codex-review-gate continues.
- S6 (CI scanner): rollback = remove from release-candidate-gate; standalone script remains for manual use.

Per-slice rollback isolated by commit; no cross-slice coupling that would force coordinated revert.

---

## Decision Needed From Owner

None for this scoping bridge. Standard Codex GO/NO-GO flow applies. Per S324 directives, the program is owner-pre-approved at the program level; sub-bridges still require Codex GO per slice.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
