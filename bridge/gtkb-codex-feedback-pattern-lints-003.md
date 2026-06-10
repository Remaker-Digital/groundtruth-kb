REVISED

# Implementation Proposal - Codex Feedback Pattern Lints (WI-3268)

bridge_kind: prime_proposal
Document: gtkb-codex-feedback-pattern-lints
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH
Project: PROJECT-GTKB-GOVERNANCE-HARDENING
Work Item: WI-3268

target_paths: ["scripts/bridge_proposal_pattern_lint.py", "platform_tests/scripts/test_bridge_proposal_pattern_lint.py"]

This REVISED proposal lands a pre-filing lint catching the four recurring Codex NO-GO mechanical patterns recorded for WI-3268. The work item's accepted scope is the four pattern classes seeded at `archive/backlog-adds-2026-05-11/add_backlog_items.py:101-116` and recorded in the live MemBase `WI-3268` row.

## Revision Notes

-003 addresses the `-002` NO-GO findings:

- **F1 (P1) — lint set did not match the recorded WI-3268 scope.** The `-001` proposal's four patterns were bare `pytest`, `Codex VERIFIED (pending)`, **missing CODEX-WAY-OF-WORKING reference**, and missing `OWNER ACTION REQUIRED` section. The recorded WI-3268 scope (in-root seed `archive/backlog-adds-2026-05-11/add_backlog_items.py:101-116`, lines `(a)`-`(d)`) is: bare `pytest`; `Codex VERIFIED (pending)` wording; **PowerShell-fragile inline-Python escaping with `\"` inside `python -c "..."`**; and missing standalone `OWNER ACTION REQUIRED` block evidence requirement. -003 restores the recorded pattern set exactly: pattern 3 is now the PowerShell-fragile inline-Python escaping defect, and the non-recorded "missing CODEX-WAY-OF-WORKING reference" lint is dropped (not split off — it was never part of WI-3268's accepted scope). The lint inventory now matches WI-3268's accepted scope one-to-one.
- **F2 (P1) — owner-action lint weaker than the governing protocol.** The `-001` owner-action check looked only for a presence-only title-case `## Owner Action Required` heading. -003 makes the lint check for the exact literal heading `OWNER ACTION REQUIRED` AND the six required field labels mandated by `independent-progress-assessments/CODEX-WAY-OF-WORKING.md:150-160`: `Status:`, `Decision / Question:`, `Needed from Mike:`, `Why it matters:`, `Options:`, and `Reply requested:`. A heading present without the complete field set is flagged.
- **F3 (P1) — test target outside the platform test lane.** The `-001` proposal put tests under the stale `tests/scripts/` tree. Current pytest config is `testpaths = ["platform_tests", "applications/Agent_Red/tests"]` and CI runs `python -m pytest platform_tests/ -q`. -003 retargets the test module to `platform_tests/scripts/test_bridge_proposal_pattern_lint.py`, updates `target_paths`, and updates the acceptance command.
- **F4 (P2) — unresolved out-of-root source-evidence filename.** The `-001` proposal cited `feedback_bridge_protocol_iteration_throughput_s341.md` as the pattern-source evidence; that file is not under `E:\GT-KB`, violating `.claude/rules/project-root-boundary.md`. -003 replaces it with two in-root sources: the live MemBase `WI-3268` work-item row, and the in-root backlog-add seed artifact `archive/backlog-adds-2026-05-11/add_backlog_items.py:101-116` (explicitly identified as the historical seed evidence for WI-3268's pattern inventory).
- **Advisory specs cited.** The `-002` applicability preflight reported advisory omissions; -003 cites `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` in `## Specification Links`.

## Claim

CLI: `python scripts/bridge_proposal_pattern_lint.py --bridge-id <id>`. Reads the bridge proposal file, checks for WI-3268's four recorded recurring patterns, emits a per-pattern report with a remediation hint per detected pattern. Non-blocking by default; `--strict` returns a non-zero exit code on any detection (matching the WI-3268 acceptance "exit-1 on detection").

## In-Root Placement Evidence

All target paths in-root within `E:\GT-KB`: `scripts/bridge_proposal_pattern_lint.py` and `platform_tests/scripts/test_bridge_proposal_pattern_lint.py`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; the lint catches recurring pre-filing violations of the bridge protocol.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - proposal-linkage constraint; one of the recurring-defect surfaces the lint guards.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this proposal includes the Project Authorization / Project / Work Item linkage metadata block.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping; also the constraint behind the bare-`pytest` lint pattern (correct invocation `python -m pytest`).
- `SPEC-AUQ-POLICY-ENGINE-001` - the lint is a deterministic policy-engine-style read surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root only; all target paths in-root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance; the lint output is a governed pre-filing artifact-quality surface.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the lint operates on the bridge-proposal artifact.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact-lifecycle trigger discipline; the lint runs at the pre-filing lifecycle stage.
- `GOV-STANDING-BACKLOG-001` - WI-3268 is a tracked backlog work item.
- `.claude/rules/file-bridge-protocol.md` - bridge statuses, file naming, INDEX maintenance; the source of the recurring patterns being linted.
- `independent-progress-assessments/CODEX-WAY-OF-WORKING.md` - the governing `OWNER ACTION REQUIRED` block protocol (heading + six required field labels) that the owner-action lint enforces.
- `.claude/rules/codex-review-gate.md` - mandatory Codex review before implementation.
- `.claude/rules/project-root-boundary.md` - all touched paths and all source evidence within E:\GT-KB.

## Prior Deliberations

- `DELIB-1640` (cited in the `-002` NO-GO) - prior NO-GO deliberation involving bridge-compliance / proposal-standard failure patterns; precedent for the recurring-defect class the lint addresses.
- `DELIB-0993` (cited in the `-002` NO-GO) - prior NO-GO deliberation in the same bridge-compliance failure-pattern family.
- `DELIB-1859` (cited in the `-002` NO-GO) - prior NO-GO deliberation, proposal-standard failure pattern.
- `DELIB-1853` (cited in the `-002` NO-GO) - prior NO-GO deliberation, bridge-compliance failure pattern.

No prior deliberation rejects a pre-filing pattern-lint surface; the `-002` Codex review's findings were proposal-scope corrections (pattern-inventory fidelity, owner-action protocol mapping, test lane, source evidence), all addressed above.

## Owner Decisions / Input

- 2026-05-14 UTC, S350+: owner approved the `GTKB-GOVERNANCE-HARDENING` authorization batch including WI-3268. Channel: AskUserQuestion; formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`; project authorization `PAUTH-PROJECT-GTKB-GOVERNANCE-HARDENING-GOVERNANCE-HARDENING-BATCH` (active).
- No further AUQ required for this revision: the `-002` NO-GO findings are proposal-scope corrections (pattern-inventory restoration to the recorded WI-3268 scope, owner-action lint strengthening, test-lane retarget, in-root source-evidence substitution), not new scope; no new requirement, no protected-file mutation, no destructive action, no deployment, no waiver requested.

## Requirement Sufficiency

Existing requirements sufficient. WI-3268's recorded description (in-root seed `archive/backlog-adds-2026-05-11/add_backlog_items.py:101-116`, mirrored in the live MemBase `WI-3268` row) enumerates the four pattern classes and the Slice-1 acceptance ("lint detects all 4 pattern classes + emits remediation hint + exit-1 on detection"). No new or revised requirement or specification is created by this work; -003 restores fidelity to the existing recorded scope.

## Clause Scope Clarification (Not a Bulk Operation)

Not a bulk operation. One WI; member of `PROJECT-GTKB-GOVERNANCE-HARDENING` per the `formal-artifact-approval` packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`. This slice performs no batch resolve, promote, or retire of work items or specifications; it does not invoke `gt batch` or any inventory-class operation. The lint is a read-only surface — it reads a single bridge-proposal file and emits a report; it performs no MemBase write. References to "work item", "backlog", and "standing backlog" describe the single WI `WI-3268` and its governed filing path only. Review-packet inventory: IP-1 (lint script) + IP-2 (tests), single thread.

## Bridge INDEX Maintenance

This `-003` revision is filed at `bridge/gtkb-codex-feedback-pattern-lints-003.md` per the `.claude/rules/file-bridge-protocol.md` File Naming convention. The `bridge/INDEX.md` update inserts a `REVISED: bridge/gtkb-codex-feedback-pattern-lints-003.md` line at the top of the existing `Document: gtkb-codex-feedback-pattern-lints` entry, above the prior `NO-GO` and `NEW` lines. The prior `-001` and `-002` versions are preserved unchanged — no deletion, no rewrite — consistent with the append-only bridge audit trail. `bridge/INDEX.md` remains the canonical workflow-state authority for this thread.

## Proposed Scope

### IP-1: Pattern lints

`scripts/bridge_proposal_pattern_lint.py` checks for WI-3268's four recorded recurring patterns:

1. **Bare `pytest` command** (recorded WI-3268 pattern (a)): a `pytest` token used as a command invocation that is not preceded by `python -m `. Flag with the remediation hint to use `python -m pytest`.
2. **"Codex VERIFIED (pending)" framing** (recorded WI-3268 pattern (b)): the literal substring `Codex VERIFIED (pending)` (and close variants such as `Codex VERIFIED(pending)`) on a pre-implementation proposal. Flag — a pre-implementation proposal cites `Codex GO`, not a pre-authored verdict status; the remediation hint says to use `Codex GO`.
3. **PowerShell-fragile inline-Python escaping** (recorded WI-3268 pattern (c)): a `python -c "..."` invocation whose embedded Python string contains backslash-escaped double quotes (`\"`), which is fragile under PowerShell parsing. Flag with the remediation hint to use a heredoc, a temp script file, or single-quoted Python literals instead of `\"`-escaped inline strings.
4. **Missing standalone `OWNER ACTION REQUIRED` block** (recorded WI-3268 pattern (d)): when the proposal text indicates owner input is required (pending-owner-input phrasing) AND narrative-artifact / formal-artifact approval packets are part of scope, require a standalone block with the **exact literal heading `OWNER ACTION REQUIRED`** plus all six required field labels from `CODEX-WAY-OF-WORKING.md:150-160`: `Status:`, `Decision / Question:`, `Needed from Mike:`, `Why it matters:`, `Options:`, and `Reply requested:`. Flag when the heading is absent, or when the heading is present but any required field label is missing.

CLI: `python scripts/bridge_proposal_pattern_lint.py --bridge-id <id> [--strict]`. Non-blocking by default; `--strict` exits non-zero on any detection.

The lint is scoped to bridge-proposal files. Its owner-action check (pattern 4) validates the structural shape a bridge proposal/report can carry — the literal heading and the field labels; it does not attempt to judge owner-action visibility in interactive chat output, which is out of scope for a static bridge-file lint.

### IP-2: Tests

Each pattern gets a positive case (defect present, flagged) and a negative case (defect absent or correctly formed, not flagged), plus exit-code tests for `--strict` and default mode.

## Specification-Derived Verification Plan

| Behavior | Test | Derived from |
|---|---|---|
| Bare `pytest` flagged | `test_bare_pytest_flagged` | WI-3268 pattern (a); DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 |
| `python -m pytest` not flagged | `test_python_m_pytest_not_flagged` | WI-3268 pattern (a) negative case |
| `Codex VERIFIED (pending)` flagged | `test_codex_verified_pending_flagged` | WI-3268 pattern (b); GOV-FILE-BRIDGE-AUTHORITY-001 (verdicts are LO-set) |
| `Codex GO` framing not flagged | `test_codex_go_framing_not_flagged` | WI-3268 pattern (b) negative case |
| PowerShell-fragile inline-Python `\"` escaping flagged | `test_powershell_fragile_inline_python_escaping_flagged` | WI-3268 pattern (c); restores recorded scope |
| Heredoc / single-quoted inline Python not flagged | `test_safe_inline_python_not_flagged` | WI-3268 pattern (c) negative case |
| Missing `OWNER ACTION REQUIRED` heading flagged | `test_missing_owner_action_required_heading_flagged` | WI-3268 pattern (d); CODEX-WAY-OF-WORKING.md:143-160 |
| `OWNER ACTION REQUIRED` heading present but missing required field labels flagged | `test_owner_action_required_incomplete_fields_flagged` | WI-3268 pattern (d); CODEX-WAY-OF-WORKING.md:150-160 (six required labels) |
| Complete `OWNER ACTION REQUIRED` block not flagged | `test_owner_action_required_complete_not_flagged` | WI-3268 pattern (d) negative case |
| `--strict` exits non-zero on detection | `test_strict_mode_exits_nonzero` | WI-3268 acceptance "exit-1 on detection" |
| Default mode exits 0 (non-blocking) | `test_default_exit_zero` | WI-3268 acceptance (non-blocking default) |

Run: `python -m pytest platform_tests/scripts/test_bridge_proposal_pattern_lint.py -v` (from `E:\GT-KB`; `platform_tests` is in the root `testpaths` and is the lane CI exercises via `python -m pytest platform_tests/ -q`).

## Acceptance Criteria

- IP-1, IP-2 landed; all 11 tests in the verification plan PASS.
- The lint detects all four recorded WI-3268 pattern classes (a-d) and emits a per-pattern remediation hint.
- The owner-action lint (pattern 4) checks the exact literal `OWNER ACTION REQUIRED` heading and all six required field labels.
- `--strict` exits non-zero on any detection; default mode is non-blocking (exit 0).
- The lint reads only the named bridge-proposal file; it performs no MemBase write.
- Both preflights PASS; `python -m ruff check` and `python -m ruff format --check` are clean for the touched files.

## Files Expected To Change

- `scripts/bridge_proposal_pattern_lint.py` — new pre-filing lint script (four WI-3268 pattern checks, `--strict` mode).
- `platform_tests/scripts/test_bridge_proposal_pattern_lint.py` — new test module, 11 spec-derived tests, in the collected platform test lane CI exercises.

## Risks / Rollback

- Risk: false positives reduce lint usefulness. Mitigation: configurable severity per pattern; the lint is non-blocking by default, so a false positive does not gate filing unless `--strict` is explicitly requested.
- Risk: pattern 3 (inline-Python escaping) heuristic over- or under-matches code-fenced examples. Mitigation: the detector targets `python -c "..."` invocations containing `\"`; the negative-case test `test_safe_inline_python_not_flagged` guards against over-matching safe forms.
- Rollback: remove the lint script and the test file. No MemBase or protected-file change to revert.

## Recommended Commit Type

`feat` - new pre-filing lint tool (script + tests). Net source is the new lint script plus its 11 spec-derived tests.

## Applicability Preflight

`python scripts/bridge_applicability_preflight.py --bridge-id gtkb-codex-feedback-pattern-lints` — run against the `-003` operative file with the INDEX entry in place; exit 0:

```
- packet_hash: sha256:3352e7e760b321b9d452d6936b16b06150f0f3786a5fb0fe0787b16d54bedf39
- bridge_document_name: gtkb-codex-feedback-pattern-lints
- content_source: indexed_operative
- content_file: bridge/gtkb-codex-feedback-pattern-lints-003.md
- operative_file: bridge/gtkb-codex-feedback-pattern-lints-003.md
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
```

All previously-omitted advisory specs (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) now cited; `missing_advisory_specs` is empty.

## Clause Applicability

`python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-codex-feedback-pattern-lints` — run against the `-003` operative file; exit 0; 5 must_apply clauses, 0 evidence gaps, 0 blocking gaps:

```
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
```

| Clause | Applicability | Evidence found |
|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | must_apply | yes |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | must_apply | yes |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | must_apply | yes |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | must_apply | yes |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | must_apply | yes |

End of proposal.
