REVISED

# Bridge Proposal — GTKB ADR-Evaluation Enforcement Program (Scoping; REVISED-2)

**Status:** REVISED (version 005)
**Author:** Prime Builder (Claude, S324 2026-04-30)
**Document name:** `gtkb-adr-evaluation-enforcement-2026-04-30`
**Reviewed prior version:** `bridge/gtkb-adr-evaluation-enforcement-2026-04-30-004.md` (Codex NO-GO with F1, F2 findings).

**REVISED-2 summary:** Closes -004 F1 (replaces nonexistent `--fast` flag with `--skip-frontend` and acknowledges release-gate's known infrastructure drift); closes -004 F2 (updates S1 origin plan to use the S324 owner_conversation directive as the originating DA source per `DCL-SPEC-DA-CITATION-MANDATORY-001`).

**Owner pre-approval:** Yes for the full S0–S6 program scope, groundtruth-kb upstream routing, file scoping bridge now (per S324 AskUserQuestion answers). Bridge protocol still requires Codex GO before sub-bridge filing.

---

## Closure of NO-GO Findings (-004)

### F1 Closure — Executable Release-Gate Command

**Original finding:** The per-slice verification template at `-003:165` cited `python scripts/release_candidate_gate.py --fast`. The script's argparse exposes `--require-python`, `--skip-python`, `--skip-frontend`, `--include-frontend`; it does not expose `--fast`. Same stale-CLI shape that just blocked the dashboard-link verification thread.

**Closure:** The per-slice template is updated to use `python scripts/release_candidate_gate.py --skip-frontend` (Python-only gate run; the actual flag that approximates the previously-intended "fast" semantics).

**Honest disclosure (post-cascade-resolution evidence):** During the dashboard-link verification cycle, running the corrected release-gate command surfaced multiple pre-existing infrastructure problems unrelated to ADR-evaluation: 3 ruff errors in `tests/scripts/test_run_spec_derived_tests.py` (now fixed under `dashboard-link-cascade-resolution-2026-04-30` thread), a hardcoded reference to a nonexistent test file at `release_candidate_gate.py:127` (now fixed under same thread), and a 180s pytest-internal-timeout shorter than the actual test suite duration of ~220s+ (NOT yet fixed; tracked as out-of-scope per owner "STOP cascade" direction). The S6 (CI/release scanner) slice depends on a working release-gate; this dependency is now explicit:

**S6 prerequisite (added per F1 closure):** Before S6 implementation begins, a separate "release-gate infrastructure repair" bridge thread must address the gate's pytest timeout and any additional internal failures revealed past the timeout. The recommendation in dashboard-link `-009` post-impl §"Out-of-Scope Issues Discovered" is the explicit handoff for that work.

### F2 Closure — Owner-Conversation DA Source for S1 Origin

**Original finding:** The S1 plan archived the dashboard-link bridge thread with `source_type=lo_review`. But `DCL-SPEC-DA-CITATION-MANDATORY-001` requires `owner_conversation` (originating owner input). LO review can be supporting evidence but is not the origin per the cited DCL.

**Closure:** S1's plan is updated to use the S324 owner directive as the `owner_conversation` originating DA record for `DCL-RUNTIME-URL-CONFIGURATION-001`.

**Originating owner input (verbatim, S324):**
> "How do we mechanically enforce ADR evaluations for every implementation proposal? For example we are still using hard-coded URLs in implementations."

This is followed by the owner's design articulation of:
- Required `## ADR / DCL Evaluation Matrix` section in proposals
- Machine-readable ADR/DCL scope (`path_globs`, `concern_tags`, `required_assertions`, `proposal_required`)
- Proposal validator script with applicability matching
- The specific `DCL-RUNTIME-URL-CONFIGURATION-001` with allowed-classes taxonomy
- Three enforcement points (bridge review gate, pre-implementation hook, CI/release gate)

Followed by S324 AskUserQuestion authorizations: full S0–S6 scope, groundtruth-kb upstream routing, file scoping bridge now.

**S1 DA record specification (planned for S1 implementation bridge):**

```yaml
deliberation_id: DELIB-S324-ADR-EVALUATION-ENFORCEMENT-AUTHORIZATION
source_type: owner_conversation
session_id: S324
asked_at: 2026-04-30
content: |
  Verbatim S324 owner directive: [as above]
  Followed by owner design articulation: [matrix structure, machine-readable scope,
  validator, URL DCL allowed-classes, enforcement points]
  Followed by S324 AskUserQuestion authorizations: [scope/location/timing]
outcome: program_authorized
relational_links:
  - spec: DCL-RUNTIME-URL-CONFIGURATION-001 (originating; created by S1)
  - bridge: gtkb-adr-evaluation-enforcement-2026-04-30 (program-level scoping)
supporting_evidence:
  - bridge/dashboard-link-localhost-correction-2026-04-30-* (LO review thread; empirical motivation, NOT origin)
```

The dashboard-link LO review remains as **supporting evidence** for the URL-classification gap, but is no longer cited as the originating record. The originating record is the owner directive itself.

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate:

**Direct alignment with established principles:**
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — repetitive AI-mediated governance work belongs in services. **Drives the entire program.**
- `DELIB-0874` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — artifact-oriented governance principle.

**Spec-coverage architecture this program extends:**
- `ADR-SPEC-COVERAGE-ARCHITECTURE-001` — comprehensive spec coverage architecture. **This program composes with** ADR-SPEC-COVERAGE.
- `DCL-SPEC-RELEVANCE-CLOSURE-001` — bridge proposal spec linkage must be relevance-complete. **This program extends** DCL-SPEC-RELEVANCE-CLOSURE.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — spec-linkage enforcement across all bridge submission paths. **This program depends on** the 6-path matrix.
- `DCL-VERIFIED-BRIDGE-HISTORY-001` — VERIFIED runner must operate on full bridge thread history. **This program composes with** VERIFIED-runner.
- `DCL-SPEC-TEST-IMPL-TRIAD-COMPLETENESS-001` — spec/test/impl triad must be complete or tracked-incomplete. **This program extends** triad-completeness.
- `bridge/gtkb-platform-spec-coverage-architecture-2026-04-29-005.md` — prior parallel-thread bridge.

**Formal-artifact-approval triple (this program complements):**
- `GOV-ARTIFACT-APPROVAL-001` / `ADR-ARTIFACT-FORMALIZATION-GATE-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — formal-artifact-approval gate.

**DA-origin requirement (load-bearing for F2 closure):**
- `DCL-SPEC-DA-CITATION-MANDATORY-001` — every specification must have a DA entry capturing originating user input. **S1 must comply via the S324 owner_conversation record specified in F2 closure above.**
- `DCL-SPEC-ORIGIN-DELIBERATION-SUPPORT-001` — unsupported specification authority requires owner approval/rejection request.

**Existing related gates (this program extends, not duplicates):**
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — mandates `Specification Links` heading + tokens. **S4 extends this hook.**
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED reports must carry spec-to-test mapping. **Untouched by S4.**
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` — meta-rule that governance constraints must be mechanically enforced.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — pattern for hook intent that lives in `.codex/hooks.json`.

**Rule files that constrain this work:**
- `.claude/rules/file-bridge-protocol.md` — bridge structure
- `.claude/rules/codex-review-gate.md` — protocol authority
- `.claude/rules/project-root-boundary.md` — all changes inside `E:\GT-KB`

---

## Empirical Motivation (Not Retroactive Enforcement)

The dashboard-link bridge thread (`bridge/dashboard-link-localhost-correction-2026-04-30-001.md` through `-010.md`) cycled through three NO-GO/REVISED rounds in the proposal phase plus two NO-GO/REVISED rounds in the post-impl phase. Two of the post-impl NO-GO findings (the cascade scope and the stale-CLI repetition) directly motivate slices of this program:

- **Cascade-scope NO-GO (`-010` F1)** — the bridge protocol caught implementation scope creeping outside the GO-approved 4-file boundary, even when each individual change was owner-authorized via real-time AskUserQuestion answers. This is the case the **S4 (matrix gate)** and **S5 (pre-impl gate)** are designed for: deterministic, proposal-time per-file scope enforcement that doesn't require Loyal Opposition's manual review to surface scope drift.
- **Stale-CLI NO-GO (`-008` F1 + this REVISED's own F1 closure)** — proposals citing nonexistent CLI flags. **S6 (CI/release scanner)** wouldn't have caught this directly (the CLI itself is fine; the proposal text was wrong), but a related "verification command executability" check could be added to the validator (S3) — flagged as a possible S3 sub-feature for the implementation bridge.

The dashboard-link defect serves as **empirical evidence** for the deterministic-enforcement direction. The cascade NO-GO additionally serves as evidence that the bridge protocol's GO-before-implementation rule has real teeth, even against owner-authorized changes — this program's S4 and S5 will extend that mechanical posture.

**This program does NOT retroactively reject the dashboard-link thread.** That thread is closing through its own VERIFIED cycle (parked at NO-GO `-010` pending the cascade-resolution bridge `dashboard-link-cascade-resolution-2026-04-30-001.md` to receive Codex GO).

**Future enforcement timeline:**
- After S1 creates `DCL-RUNTIME-URL-CONFIGURATION-001` (with the S324 owner_conversation DA record per F2 closure): the DCL exists but is not yet enforced.
- After S3 ships the validator: the validator can produce a receipt for any bridge proposal, but the receipt is advisory.
- After S4 ships the bridge-compliance-gate extension: bridge proposals lacking a valid matrix + receipt are auto-NO-GO. **First enforcement point.**
- After S5 ships pre-impl gate: source/config edits without GO + receipt are blocked at Edit/Write time.
- After S6 ships CI/release scanner: implementation diffs with unclassified URL/path literals fail the release gate. **Prerequisite: release-gate infrastructure repair bridge (timeout fix at minimum) before S6 can depend on the gate.**

---

## Audit (S0 preview, unchanged)

| Type | Total | with tags | with source_paths | with assertions |
|---|---|---|---|---|
| ADR | 18 | 15 (83%) | 4 (22%) | 8 (44%) |
| DCL | 31 | 28 (90%) | 12 (39%) | 24 (77%) |

Backfill scope: ~37 of 49 records lack `source_paths`.

---

## Program Structure (7 Slices)

| Slice | Surface | Deliverable | Dependencies |
|---|---|---|---|
| **S0** | Audit | `groundtruth-kb/scripts/audit_adr_dcl_metadata.py` | None |
| **S1** | DCL authoring | `DCL-RUNTIME-URL-CONFIGURATION-001` formal record + owner_conversation DA record per F2 closure (DELIB-S324-ADR-EVALUATION-ENFORCEMENT-AUTHORIZATION sourced from S324 owner directive). Approval packet must include the DA record ID and the verbatim owner directive. The dashboard-link LO review may remain as supporting_evidence in the DA record but is NOT the originating source. | S0 |
| **S2** | Backfill | `groundtruth-kb/scripts/backfill_adr_dcl_metadata.py`. Idempotent. | S0, S1 |
| **S3** | Validator | `groundtruth-kb/src/groundtruth_kb/governance/proposal_validator.py` + CLI. Receipt JSON. Closed taxonomy for non-applicable cells. **Sub-feature consideration (per -004 F1 lesson):** validator may also detect non-existent CLI flags in proposal verification commands by argparse introspection — flag this for the S3 implementation bridge. | S1, S2 |
| **S4** | Bridge gate | `.claude/hooks/bridge-compliance-gate.py` extension. Mirror in `.codex/hooks.json`. **Ratchet-semantics decision codified in implementation bridge.** | S3 |
| **S5** | Pre-impl gate | New hook `.claude/hooks/pre-impl-validator-receipt-gate.py`. Mirror in `.codex/hooks.json`. | S4 |
| **S6** | CI/release scanner | `groundtruth-kb/scripts/scan_diff_for_unclassified_literals.py` + integration into `scripts/release_candidate_gate.py`. **Prerequisite per -004 F1 closure: release-gate infrastructure repair bridge (timeout fix; hardcoded-test-list audit) must complete before S6 implementation begins.** | S3, S1, release-gate-repair bridge |

**Slice ordering:** S0 → S1 → S2 → S3 → S4 → S5 → S6 (S6 deferred per S6 prerequisite).

---

## Cross-Harness Enforcement Matrix

Per `DCL-CROSS-HARNESS-ENFORCEMENT-001` 6-path enforcement matrix:

| Path | S4 (matrix gate) | S5 (pre-impl gate) | S6 (CI/release scanner) |
|---|---|---|---|
| **Claude Code Write/Edit** | **Covered** | **Covered** | not write-time |
| **Codex apply_patch** | **Covered (mirror)** | **Covered (mirror)** | not write-time |
| **Direct shell writes** | **Gap** — ratchet decision in S4 bridge | **Gap** — same | not write-time |
| **External editors** | **Gap** — same | **Gap** — same | not write-time |
| **Direct git commits** | **Gap** — same | **Gap** — same | **Covered (downstream)** |
| **CI/PR** | not write-time | not write-time | **Covered** |

Net coverage: 4 of 6 paths fully covered by S4+S5; 2 paths (shell writes, external editors) tracked as known gaps with ratchet-decision deferral; all 6 paths covered downstream by S6 at CI/release time.

---

## Specification-Derived Verification

This is a scoping bridge; spec-to-test mapping is delegated to per-slice implementation bridges. Verification surface each slice must cover:

| Slice | Required test surface |
|---|---|
| S0 | Audit script unit tests; report format snapshot test; idempotency check |
| S1 | DCL exists with required fields; assertions field has at least 3 grep-pattern entries; approval packet validates; **originating DA record exists with relational link to the DCL and contains verbatim owner directive** |
| S2 | Backfill script unit tests covering: no-op on populated; new-population on empty; refusal-to-overwrite on owner-set value |
| S3 | Validator unit tests: applicable ADR matched by source_paths; applicable ADR matched by concern_tags; non-applicable cell with valid taxonomy passes; non-applicable cell with free-text rationale fails; missing matrix fails; receipt JSON conforms; **possibly: nonexistent-CLI-flag detection in proposal verification commands** |
| S4 | Hook test for matrix-heading regex; hook test for receipt requirement on GO INDEX line; cross-harness parity test; ratchet-semantics test |
| S5 | Hook test for receipt-required Edit/Write to source/config paths; cross-harness parity test |
| S6 | Diff scanner test fixtures: hardcoded URL with no DCL match (fails); URL classified as `test_fixture` in receipt (passes); release-gate integration test |

**Execution commands (planned for each per-slice post-impl report):**
```bash
pytest tests/  # full suite for slice's surface
python -m ruff check <changed-files>
python scripts/release_candidate_gate.py --skip-frontend
```

---

## Project Root Boundary Compliance

Per `.claude/rules/project-root-boundary.md`:

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
  - `scripts/release_candidate_gate.py` (extended, S6 — after release-gate repair prerequisite)
  - `groundtruth.db` (mutated, S1 + S2)
  - `.groundtruth/formal-artifact-approvals/*.json` (new packets)
  - `.groundtruth/proposal-validator-receipts/*.json` (new artifact class, S3)
  - Tests under `tests/`
- All cited specifications inside `E:\GT-KB` or `groundtruth.db` at project root.
- No external paths referenced.

---

## Pre-GO Drift Disposition

Scoping bridge; no source-code edits in worktree for this program.

---

## Implementation Sequence (planned for after Codex GO on REVISED-2)

1. File `bridge/gtkb-adr-evaluation-enforcement-s0-audit-2026-MM-DD-001.md` for S0.
2. After S0 VERIFIED: file S1 implementation bridge — must include the DA archival of `DELIB-S324-ADR-EVALUATION-ENFORCEMENT-AUTHORIZATION` per F2 closure before promoting `DCL-RUNTIME-URL-CONFIGURATION-001`.
3. After S1 VERIFIED: file S2 + S3 implementation bridges.
4. After S3 VERIFIED: file S4 implementation bridge with ratchet-semantics decision.
5. After S4 VERIFIED: file S5 implementation bridge.
6. **Before S6:** ensure release-gate infrastructure repair bridge has VERIFIED.
7. After release-gate repair VERIFIED + S5 VERIFIED: file S6 implementation bridge.
8. After all slices VERIFIED: program closure report.

Each sub-bridge carries its own Specification Links, ADR / DCL Evaluation Matrix (eating its own dog food once S4 lands), spec-to-test mapping, project-root-boundary compliance, and post-impl verification.

---

## Rollback Notes

- S0/S2 (scripts): pure read or idempotent write.
- S1 (DCL authoring + DA record): rollback = retire spec via `db.update_spec(status='retired')` and mark DA record as superseded.
- S3 (validator): standalone; rollback = remove script + receipt directory.
- S4 (bridge gate extension): rollback = revert hook commit; existing logic continues.
- S5 (pre-impl gate): rollback = unregister hook + revert.
- S6 (CI scanner): rollback = remove from release-candidate-gate.

Per-slice rollback isolated by commit; no cross-slice coupling.

---

## Decision Needed From Owner

This REVISED-2 proposal does not require an owner decision. Standard Codex GO/NO-GO flow applies.

(c) 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
