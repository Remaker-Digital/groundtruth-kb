NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Defect-Fix Proposal - Bridge gate detectors require magic content phrases, surfacing failures late

bridge_kind: prime_proposal
Document: gtkb-bridge-gate-detectors-magic-content-phrases
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3463

target_paths: ["scripts/adr_dcl_clause_preflight.py", "platform_tests/scripts/test_adr_dcl_clause_preflight.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

The ADR/DCL clause preflight gate (`scripts/adr_dcl_clause_preflight.py`) tells an author *that* a `must_apply` blocking clause lacks satisfying evidence, but not *how* to satisfy it: the gap summary returned by `evaluate_evidence` is `f"Evidence missing: {clause.evidence_required}"` (a prose restatement), and neither the rendered "Blocking Gaps" nor "Evidence Gaps" section surfaces the clause's actual `evidence_pattern` — the literal token surface the author must include for the gate to clear. The result is the defect class described in WI-3463: a structurally well-formed artifact fails the gate on phrasing (a "magic content phrase" the author did not happen to write), and the author learns the failure only at preflight/commit time with no actionable guidance on the satisfying token. This fix makes the late-surfacing diagnostic actionable by emitting the satisfying `evidence_pattern` (and, for refuted evidence, the matched `failure_pattern`) inline in the gap output. It is a diagnostic-only change: applicability classification, evidence detection, owner-waiver handling, exit codes, and gate semantics are unchanged.

## Defect / Reproduction

Observed instances (origin of WI-3463), both from S372: `bridge/gtkb-project-completion-scanner-addressing-thread-fix-015.md` and `bridge/gtkb-implements-link-backfill-phase2-scoping-001.md` each had to hand-add a "Bridge Protocol Handling" paragraph to clear `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` (the no-index successor of the WI's `CLAUSE-INDEX-IS-CANONICAL`). The gate keyed on author-supplied content tokens matching the clause `evidence_pattern` rather than on a structural fact, so well-formed artifacts failed on phrasing and the author learned only after filing. The same defect class also affects `implementation_authorization.py` requirement-sufficiency phrasing (tracked separately as WI-3454, the sibling parser-phrase friction).

Reproduction (logical): construct bridge content that fires a blocking clause's applicability axes (so `applicability == "must_apply"`) but omits the clause's `evidence_pattern` token surface — e.g., content that triggers `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` via its `applies_when_content` regex yet never writes a `bridge/<slug>-NNN.md` / "numbered bridge files" / "append-only" phrase. Run `python scripts/adr_dcl_clause_preflight.py --content-file <draft>`. Today the exit-5 report's Blocking Gaps entry shows `Gap: Evidence missing: <evidence_required>` and `Evidence required: <evidence_required>`, but never the literal `evidence_pattern` the author must satisfy. Expected after the fix: the same entry additionally shows the satisfying `evidence_pattern` (and, when a `failure_pattern` refuted the evidence, the matched failure marker), so the author can repair the phrasing on the spot without re-deriving the detector regex from the TOML registry.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/adr_dcl_clause_preflight.py`, `platform_tests/scripts/test_adr_dcl_clause_preflight.py`. The change touches only the GT-KB platform preflight script and its platform test; no application/adopter surface is involved and no generated artifact is written outside the root.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the clause preflight is the mechanical floor enforcing bridge-authority clauses; this fix improves the actionability of that gate's diagnostic output without weakening its authority, and the defect's most-cited offending clause (`CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL`) is derived from this spec.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix preserves the durable governance artifact (the clause registry + preflight gate) while reducing the per-instance authoring friction that pushes well-formed artifacts to fail on phrasing.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all governing specs (mandatory linkage), and the clause it most directly improves the diagnostics for (`DCL-...-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS`) is itself enforced by the gate being fixed.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives tests from the cited specs (mandatory), and this is the governing authority for the spec-to-test clause whose late-surfacing diagnostics this fix improves.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal carries Project Authorization / Project / Work Item linkage lines (mandatory) consumed by the project-authorization validator.
- `SPEC-AUQ-POLICY-ENGINE-001` - confirms no AskUserQuestion owner decision is added or bypassed by this diagnostic-only change; the fix introduces no new owner-decision surface and the existing owner-waiver line remains the only sanctioned blocking-gap bypass.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform preflight module (`scripts/...`) and platform tests; no application-placement boundary is crossed and all output paths remain in-root under `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - WI-3463 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the preflight is invoked identically by both harnesses' review paths; this diagnostic-only change does not alter the harness-parity surface (no hook registration, no Codex/Claude divergence introduced).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the gate verdict remains artifact-backed (clause registry evidence patterns); the fix only makes the missing-evidence narrative self-describing rather than requiring the author to re-derive the pattern from the registry.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the fix touches an existing tracked source surface plus its test (the contact triggers a test update, satisfied by the verification plan); no new artifact type or lifecycle state is introduced.

## Prior Deliberations

- `DELIB-20263745` - Loyal Opposition Review - Bridge Compliance Gate WI-AUTO Regex Fix - prior precedent for a defect fix that adjusted a bridge-gate detector pattern; relevant because it establishes the pattern of correcting gate-detector friction at the diagnostic/detection layer.
- `DELIB-2660` - Loyal Opposition Verdict - Project Completion Scanner Addressing-Thread Fix - 002 - verdict context for `bridge/gtkb-project-completion-scanner-addressing-thread-fix-015`, one of the two S372 artifacts that had to hand-add a magic phrase to clear this gate (a direct instance of the defect under repair).
- `DELIB-20261139` - Loyal Opposition Verdict - Directive Enforcement Registry P1+P2 Combined REVISED-003 - registry-driven enforcement precedent showing the project's pattern of keeping enforcement registry-backed while tuning author-facing friction.
- `DELIB-20265457` - Owner decision authorizing the PROJECT-GTKB-RELIABILITY-FIXES proposal batch (this WI is in scope).

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (`DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`) - WI-3463 is origin=defect, single-concern, introduces no new public surface and no new/revised spec, and is bounded to ~1 source file + 1 test (well under the fast-lane size guide), so it is covered by the reliability fast-lane standing authorization through active project membership.
- `DELIB-20265457` - owner AUQ (2026-06-21) directing authoring of NEW proposals for all open PROJECT-GTKB-RELIABILITY-FIXES work items; WI-3463 (P3 defect) is in that batch scope.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` - the standing fast-lane authorization (carried by PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING) that authorizes small single-concern defect fixes to proceed through the bridge protocol without per-item fresh owner approval.

## Requirement Sufficiency

Existing requirements sufficient. `GOV-FILE-BRIDGE-AUTHORITY-001` (and the derived blocking clauses in `config/governance/adr-dcl-clauses.toml`) already establish that the clause preflight is the mechanical floor for bridge-authority compliance. This fix improves only the actionability of that gate's missing-evidence diagnostic; it adds no new requirement, changes no clause registry entry, and alters no gate behavior or owner-decision surface. No new or revised requirement/specification is introduced.

## Proposed Scope

1. In `scripts/adr_dcl_clause_preflight.py`, make the missing-evidence diagnostic self-describing by surfacing the satisfying `evidence_pattern` (and, when applicable, the refuting `failure_pattern`) inline:
   - In `evaluate_evidence`, when the `evidence_pattern` does not match, include the literal pattern in the returned gap summary (e.g., `"Evidence missing: <evidence_required> (add text matching evidence pattern: <evidence_pattern>)"`). When a `failure_pattern` refutes otherwise-present evidence, include the matched failure marker in the gap summary so the author knows which token to remove/rephrase. The `(evidence_found, reasons, gap_summary)` return shape is unchanged; only the gap-summary string is enriched.
   - In `render_markdown`, extend the existing "Blocking Gaps" section (and the "Evidence Gaps" advisory section) to add a line surfacing `r.clause.evidence_pattern` (the satisfying token surface) alongside the existing `Evidence required:` line, so the rendered report is actionable without consulting the TOML registry.
   - The change is additive to the diagnostic narrative only. It does NOT modify `evaluate_applicability`, the `must_apply`/`may_apply`/`not_applicable` classification, the `evidence_pattern`/`failure_pattern` matching logic, owner-waiver detection, the `EXIT_BLOCKING_GAP` (5) / `0` exit-code semantics, the clause registry (`config/governance/adr-dcl-clauses.toml` is untouched), or the bridge-compliance Write-time gate.
2. Add paired regression tests in `platform_tests/scripts/test_adr_dcl_clause_preflight.py` following the established calibration shape (see verification plan): one asserting the enriched gap surfaces the satisfying `evidence_pattern`, one asserting the existing pass/exit-0 path is unaffected.

This is the defect-removal path (candidate direction (b) from the WI: emit the missing-phrase guidance inline). The WI's broader candidate directions (a) "bridge-propose helper pre-populates the required phrases" and (c) "relax detectors to structural checks (e.g., key CLAUSE on actual structural fact rather than a prose phrase)" are larger behavior/architecture changes that would alter authoring or gate semantics and require their own requirement work; they are explicitly out of scope for this fast-lane defect fix and may be filed as follow-on work items.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` (gate diagnostics must be actionable for the bridge-authority clause) | `test_blocking_gap_report_surfaces_satisfying_evidence_pattern` | A bridge draft that fires a blocking clause at `must_apply` but omits its `evidence_pattern` exits 5 AND the rendered Blocking Gaps section contains the clause's literal `evidence_pattern` text (the satisfying token surface), not only the `evidence_required` prose. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (gap summary carries the satisfying pattern) | `test_evaluate_evidence_gap_summary_includes_evidence_pattern` | `evaluate_evidence` on a must_apply blocking clause with no matching evidence returns a `gap_summary` whose text includes the clause's `evidence_pattern`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (no false-positive regression) | `test_blocking_evidence_present_still_exits_zero_unchanged` | A draft whose content satisfies the clause `evidence_pattern` still exits 0 and renders no Blocking Gaps section (the diagnostic enrichment does not change the pass path). |

Execution commands:
- `python -m pytest platform_tests/scripts/test_adr_dcl_clause_preflight.py -q --tb=short`
- `python -m ruff check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py`
- `python -m ruff format --check scripts/adr_dcl_clause_preflight.py platform_tests/scripts/test_adr_dcl_clause_preflight.py`

## Acceptance Criteria

1. When a `must_apply` blocking clause lacks satisfying evidence, the exit-5 report's Blocking Gaps entry surfaces the clause's literal `evidence_pattern` (the satisfying token surface) in addition to the existing `evidence_required` prose; when a `failure_pattern` refuted the evidence, the matched failure marker is surfaced so the author knows which token to remove/rephrase.
2. Gate semantics are unchanged: applicability classification, evidence/failure pattern matching, owner-waiver handling, and the exit-5/exit-0 codes behave exactly as before; `config/governance/adr-dcl-clauses.toml` is not modified.
3. The new derived tests pass; the full `platform_tests/scripts/test_adr_dcl_clause_preflight.py` suite passes; `ruff check` and `ruff format --check` are clean on the two changed files.

## Risks / Rollback

- Risk: an enriched gap-summary string could break a brittle test that asserts the exact prior gap text. Mitigation: the existing gap-detection test (`test_evidence_detection_true_negative_with_gap_summary`) asserts only that the gap is non-empty (`gap is not None and len(gap) > 0`), so an enriched string still satisfies it; new assertions are additive substring checks. The implementation will re-run the full suite to confirm no exact-match assertion regresses.
- Risk: over-disclosure — surfacing a regex could be read as noisy. Mitigation: the pattern is already present in `evidence_reasons` detector notes today (e.g., `"evidence pattern \`...\` did not match"`); this fix promotes that same information into the primary gap line where the author looks first, so it adds no new disclosure class.
- Risk: scope creep toward candidate directions (a)/(c). Mitigation: this proposal is explicitly bounded to the diagnostic narrative; no change to authoring helpers, the Write-time compliance gate, or the clause registry.
- Rollback: revert the two changed files (`scripts/adr_dcl_clause_preflight.py`, `platform_tests/scripts/test_adr_dcl_clause_preflight.py`); the change is a string enrichment plus additive tests, fully reversible with no migration and no registry/config change.

## Files Expected To Change

- `scripts/adr_dcl_clause_preflight.py`
- `platform_tests/scripts/test_adr_dcl_clause_preflight.py`

## Recommended Commit Type

`fix`
