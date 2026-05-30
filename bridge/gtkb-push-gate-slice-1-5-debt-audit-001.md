NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-push-gate-slice-1-5-debt-audit
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# PROJECT-GTKB-PUSH-GATE Slice 1.5: debt-discovery audit-only mode (minimum-viable inventory)

bridge_kind: implementation_proposal
Document: gtkb-push-gate-slice-1-5-debt-audit
Version: 001 (NEW)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-28 UTC
Implements: WI-3416 (PROJECT-GTKB-PUSH-GATE master) — Slice 1.5 sub-slice
Project Authorization: PAUTH-PROJECT-GTKB-PUSH-GATE-STANDING-SLICE-0-11
Project: PROJECT-GTKB-PUSH-GATE
Work Item: WI-3416
target_paths: ["scripts/push_gate_audit.py", "platform_tests/scripts/test_push_gate_audit.py", ".gtkb-state/push-gate/audits/"]
Recommended commit type: feat:

## Summary

This Slice 1.5 proposal implements a **minimum-viable debt-discovery audit script** that wraps existing GT-KB quality tools (ruff, mypy, pytest collection, applicability + clause preflights) into a single audit-only invocation. Its purpose is to produce the **initial debt inventory** that drives Slice 3 (debt cleanup) sizing decisions and informs subsequent slice timing.

The audit operates entirely in **audit-only mode**: it produces a structured JSON report of all violations across the codebase but **does NOT block any operation**. It does NOT install pre-push hooks, does NOT modify GitHub Actions workflows, and does NOT enable the mechanical-blocker behavior described in Slice 0's design contract. Those behaviors land in Slices 4-6.

This is intentionally a **thin slice**: minimal new code; maximum reuse of existing tools. The full canonical `gt push-gate` CLI + content-addressed cache substrate from Slice 0's design lands in a later Slice 1. Slice 1.5 produces value (the inventory) without requiring the broader CLI architecture; the audit script's outputs are forward-compatible with the canonical CLI's later JSON schema.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this proposal proceeds through the file bridge; `bridge/INDEX.md` remains workflow authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all touched paths are under `E:\GT-KB`; audit output lives at `.gtkb-state/push-gate/audits/`.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing specification surfaces and concrete target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping below maps each governing surface to verification.
- `GOV-STANDING-BACKLOG-001` - WI-3416 is the master backlog item; Slice 1.5 is a sub-slice tracked under the master.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the audit JSON report is a durable governed artifact (committable evidence).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - traceability is preserved between WI-3416, this thread, the audit script, and the inventory output.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - Slice 1.5 implementation work advances the master WI lifecycle from governance-review to first-implementation-slice.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - the audit script is a deterministic service that converts repetitive multi-tool inventory work into one invocation.
- `DELIB-2499` - S365 owner decision authorizing the standing Slice 0-11 PAUTH that this proposal cites.

## Requirement Sufficiency

Existing requirements sufficient. No new or revised specification is needed for the audit-only minimum-viable scope; existing GOV-FILE-BRIDGE-AUTHORITY-001 governance plus PAUTH-PROJECT-GTKB-PUSH-GATE-STANDING-SLICE-0-11 cover the scope. The audit script's JSON schema is a candidate requirement that will be promoted to a formal spec (`SPEC-PUSH-GATE-AUDIT-JSON-SCHEMA-001` or similar) during Slice 0's design-contract production if owner-approved.

## KB Mutation Scope

This proposal performs no MemBase mutation. The implementation does not write to `groundtruth.db`. The audit script writes evidence only to `.gtkb-state/push-gate/audits/<timestamp>/debt-inventory.json` and supporting files. `.groundtruth-chroma/` is not touched. `groundtruth.db` is intentionally excluded from target_paths.

## WI Citation Disclosure

This proposal declares implementation work for WI-3416 (master) only. References to WI-3349, WI-3394, WI-3410, WI-3411, WI-3415 in originating-context discussion are exemplar defect-class citations — they illustrate the kinds of defects the audit will surface — not implementation-scope expansions.

## Prior Deliberations

- `DELIB-2499` (S365, 2026-05-28): Owner authorization of standing PAUTH covering Slice 0-11 for PROJECT-GTKB-PUSH-GATE. Cited as the owner-decision basis for this implementation proposal.
- `bridge/gtkb-push-gate-design-governance-review-001.md` (NEW, 2026-05-28): Slice 0 governance-review proposal landing the design contract. Slice 1.5 is forward-compatible with that contract but does not block on it.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`: foundational principle this Slice 1.5 operationalizes for the audit dimension.
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`: existing release-readiness framework that the push gate's Layer 7 wraps; Slice 1.5's audit identifies the gap relative to this spec.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`: the test-coverage portion of the audit reports which specs lack derived-test coverage.

## Owner Decisions / Input

This proposal depends on the following owner decisions:

- **S365 directive** (verbatim): *"Please proceed in order. This is a very important enhancement of GT-KB."* — authorizes Slice 1.5 filing.
- **DELIB-2499** (S365 AUQ): selected "Standing Slice 0-11 (Recommended)" PAUTH scope, which covers this Slice 1.5 work.

No new owner decisions required for this proposal. The 5 deferred owner decisions surfaced in Slice 0's governance review (cleanup sequencing, override path, multi-platform CI, PR-vs-push gating, test impact analysis dependency) do NOT block Slice 1.5 because the audit-only mode does not implement those decisions; it only produces inventory data that informs them.

## Implementation Plan

### 1. Create `scripts/push_gate_audit.py`

A standalone Python script (not yet a `gt` subcommand; that integration lands in Slice 1) that:

- Accepts `--output-dir <path>` (default: `.gtkb-state/push-gate/audits/<UTC-timestamp>/`)
- Accepts `--include <layer>` and `--exclude <layer>` for selective layer execution
- Accepts `--json` for JSON-only output (default emits both human-readable summary and JSON)
- Runs five audit layers serially with structured per-layer reporting:

  **Layer A1 — Ruff lint inventory:**
  - Runs `ruff check --output-format=json --no-cache <repo>` against tracked Python files
  - Parses output into per-file violation list
  - Reports: total violations, per-rule-code counts, per-file violation counts

  **Layer A2 — Mypy type-check inventory:**
  - Runs `mypy --show-error-codes --no-pretty --strict-equality <repo>` (or current GT-KB mypy config) against tracked Python files
  - Parses output into per-file error list
  - Reports: total errors, per-error-code counts, per-file error counts

  **Layer A3 — Pytest test inventory:**
  - Runs `pytest --collect-only --quiet` against the configured test directories
  - Parses collected test ids
  - Reports: total tests collected, per-directory test counts, deselected/skipped tests
  - Does NOT execute tests in this layer (execution lands in Layer 3 of the full gate)

  **Layer A4 — Bridge applicability preflight inventory:**
  - For each bridge entry in `bridge/INDEX.md` whose latest status is `NEW` or `REVISED`, runs `python scripts/bridge_applicability_preflight.py --bridge-id <id> --json` and aggregates `missing_required_specs` and `missing_advisory_specs` counts
  - Reports: per-bridge missing-spec lists; aggregate count

  **Layer A5 — Bridge clause preflight inventory:**
  - For each bridge entry in `bridge/INDEX.md` whose latest status is `NEW` or `REVISED`, runs `python scripts/adr_dcl_clause_preflight.py --bridge-id <id>` and aggregates blocking-gap and evidence-gap counts
  - Reports: per-bridge blocking-gaps lists; aggregate count

- Emits a single aggregate JSON report at `<output-dir>/debt-inventory.json` with the union of all five layer reports
- Emits per-layer detail JSON at `<output-dir>/<layer-name>.json`
- Emits human-readable markdown summary at `<output-dir>/SUMMARY.md`
- Exits 0 in audit-only mode regardless of finding count (this is inventory, not gating)
- Exits non-zero only on infrastructure failure (e.g., ruff not installed, repo not a git repo)

### 2. Create `platform_tests/scripts/test_push_gate_audit.py`

Unit and integration tests covering:

- **Schema test:** verify the emitted `debt-inventory.json` matches the documented schema (fixed top-level keys, per-layer sub-objects, ISO-8601 timestamp format)
- **Layer-isolation test:** verify `--include A1` produces a report containing only Layer A1 results
- **Empty-violations test:** mock all underlying tools to return zero violations; verify the report correctly shows zero
- **Tool-failure test:** mock ruff to fail with exit 2 (infrastructure error); verify the audit script exits non-zero and emits a structured infrastructure-failure record
- **Aggregate consistency test:** verify the aggregate `debt-inventory.json` is the proper union of per-layer JSON files
- **Output-dir test:** verify `--output-dir` honors the explicit override
- **Default-output-dir test:** verify the default `.gtkb-state/push-gate/audits/<timestamp>/` is created with a UTC timestamp matching the expected format

### 3. Create `.gtkb-state/push-gate/audits/` directory

Empty directory marker. Audit runs populate timestamped subdirectories. Gitignored per `.gtkb-state/` convention; outputs are runtime-only inventory data, not committable evidence (consistent with the design contract's caching layer convention).

### 4. Initial audit run (verification + initial inventory capture)

Execute `python scripts/push_gate_audit.py --output-dir .gtkb-state/push-gate/audits/initial-2026-05-28/` against the current repo state. Produces the first concrete debt inventory. The post-implementation report will cite the aggregate violation count, per-layer breakdown, and projected Slice 3 (debt cleanup) scope based on the inventory data.

## Spec-to-Test Mapping

| Specification | Verification Command | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This proposal filed at `bridge/gtkb-push-gate-slice-1-5-debt-audit-001.md`; `bridge/INDEX.md` updated. | PASS - bridge protocol observed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All touched paths (`scripts/push_gate_audit.py`, `platform_tests/scripts/test_push_gate_audit.py`, `.gtkb-state/push-gate/audits/`) are under `E:\GT-KB`. | PASS - all in-root. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-push-gate-slice-1-5-debt-audit`. | PASS expected post-Write. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This table maps specs to verification; post-implementation report records observed results from initial audit run. | PASS - mapping present. |
| `GOV-STANDING-BACKLOG-001` | WI-3416 active in PROJECT-GTKB-PUSH-GATE (canonical membership repaired after WI-3411 doubled-prefix bug). | PASS - membership confirmed. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Audit script + tests + bridge audit trail preserve durable traceability between WI-3416, this thread, and the inventory outputs. | PASS - traceability preserved. |
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` | The audit script is a single CLI invocation that replaces ad-hoc multi-tool inventory ceremony. | PASS - deterministic-service shape. |
| `DELIB-2499` | The proposal cites `PAUTH-PROJECT-GTKB-PUSH-GATE-STANDING-SLICE-0-11` which itself cites DELIB-2499. | PASS - owner-decision provenance. |

## Acceptance Criteria

- [ ] Loyal Opposition returns GO on this proposal.
- [ ] `scripts/push_gate_audit.py` exists and is invokable with `--help`.
- [ ] `platform_tests/scripts/test_push_gate_audit.py` exists and all unit tests pass via `python -m pytest platform_tests/scripts/test_push_gate_audit.py -q`.
- [ ] An initial audit run at `.gtkb-state/push-gate/audits/initial-2026-05-28/` produces `debt-inventory.json`, `SUMMARY.md`, and per-layer detail JSON files.
- [ ] The initial inventory cites concrete aggregate violation counts per layer (ruff, mypy, pytest collected, applicability preflight, clause preflight).
- [ ] `groundtruth.db` is unchanged by the audit run.
- [ ] `.groundtruth-chroma/` is unchanged by the audit run.
- [ ] No `git` mutation occurs (no commits, no branch movement, no object writes).
- [ ] The audit exits 0 in audit-only mode regardless of violation count.
- [ ] Loyal Opposition returns VERIFIED on the post-implementation report.

## Risk and Rollback

Risk is low. The audit script is read-only against the codebase; its only side effect is writing to `.gtkb-state/push-gate/audits/<timestamp>/`. The new script and test file are net-new code under target_paths.

Risks identified:

- **Tool version drift**: if ruff, mypy, or pytest versions differ between developer and CI environments, the inventory counts may differ. Mitigation: the audit JSON records each tool's version in its layer record; downstream cleanup work can verify consistency.
- **Large inventory**: the first audit run may produce a very large violation count (per the no-amnesty design tension, owner expects to fix all of them eventually). Mitigation: the audit is structured for incremental cleanup — per-rule-code and per-file aggregation enables prioritized triage in Slice 3.
- **Audit-script bug producing false-negatives**: a defect in the audit script could mask real violations. Mitigation: the integration tests use deterministic fixture violations to verify the script correctly identifies them.

Rollback: delete `scripts/push_gate_audit.py` and `platform_tests/scripts/test_push_gate_audit.py`. The `.gtkb-state/push-gate/audits/` evidence directory is gitignored runtime state; no rollback required there.

## Verification Limitations Anticipated

- The audit-only mode does NOT verify the underlying tools (ruff, mypy, etc.) are themselves correctly configured for GT-KB's needs. Tool-config validation is reserved for Slice 4 (full mechanical enable).
- The audit does not yet include the hardcoded-externals AST checker — that's Slice 2 work. Layer A1 (ruff) will catch a subset of hardcode patterns via ruff's S105/S106 codes, but the comprehensive externals check lands in Slice 2.
- The audit does not include security audits (bandit, pip-audit, gitleaks) — those are Slice 5 layers.
- The audit's pytest layer is collection-only, not execution. Execution + impact-analysis caching lands in Slices 1, 2, and 3.

## Files Touched (target_paths recap)

- `scripts/push_gate_audit.py` (new)
- `platform_tests/scripts/test_push_gate_audit.py` (new)
- `.gtkb-state/push-gate/audits/` (new directory; runtime evidence only; gitignored)

Plus bridge filing artifacts:
- `bridge/gtkb-push-gate-slice-1-5-debt-audit-001.md` (this file)
- `bridge/INDEX.md` (entry update)
- `bridge/gtkb-push-gate-slice-1-5-debt-audit-NNN.md` (post-impl report)

## Loyal Opposition Asks

1. Verify the minimum-viable scoping (audit-only; wraps existing tools; no caching yet; no AST checker yet; no security layer yet) is appropriate for Slice 1.5, or NO-GO with guidance on scope adjustments.
2. Verify the 5-layer structure (A1 ruff, A2 mypy, A3 pytest collect, A4 applicability preflight, A5 clause preflight) covers the right minimum-viable inventory dimensions, or recommend additions/removals.
3. Confirm that the JSON output schema (forward-compatible with the future canonical CLI's schema) is the right scoping choice, or recommend Slice 0's design-contract production should land first.
4. Confirm that filing Slice 1.5 in parallel with Slice 0 awaiting Codex GO is appropriate (Slice 1.5 produces inventory data independent of Slice 0's design contract), or recommend serial sequencing.
5. Note any cross-cutting governance specs (beyond the cited set) that should be added to Specification Links — especially any test-infrastructure or CI-related specs that govern the audit script's integration boundary.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
