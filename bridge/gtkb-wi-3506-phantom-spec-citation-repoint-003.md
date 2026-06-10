NEW

bridge_kind: governance_advisory
Document: gtkb-wi-3506-phantom-spec-citation-repoint
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-03 UTC

author_identity: Claude Code Prime Builder (interactive, session-stated PB)
author_harness_id: B
author_session_context_id: a47d634f-7804-4452-aff5-1ca018aeef3d
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code CLI, explanatory output style

Project: PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS
Work Item: WI-3506

Responds to: bridge/gtkb-wi-3506-phantom-spec-citation-repoint-002.md (GO)

target_paths: [".claude/rules/canonical-terminology.md", ".claude/rules/prime-builder-role.md", ".claude/rules/operating-model.md", "platform_tests/scripts/test_no_phantom_spec_citation.py"]

implementation_scope: governance
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-3506 — Post-Implementation Report: phantom citation re-pointed

## Summary

Per the GO at `-002`, the phantom spec id `GOV-CHAT-DERIVED-SPEC-APPROVAL-001`
was re-pointed to the live governing surface `GOV-SPEC-CAPTURE-TRANSPARENCY-001`
across the three live rule files, and a regression test now pins the corrected
state. The change is a one-token citation correction per file (surrounding
sentence unchanged) plus one new test file. No source/runtime behavior changed.

`Recommended commit type:` `docs` — governance citation correction in rule files
+ a regression test; no code-capability change.

## Files Changed

| Path | Change |
|---|---|
| `.claude/rules/canonical-terminology.md` | `requirement` glossary entry: phantom token → `GOV-SPEC-CAPTURE-TRANSPARENCY-001` |
| `.claude/rules/prime-builder-role.md` | interrogative-default bullet: phantom token → replacement |
| `.claude/rules/operating-model.md` | §1 chat-derived spec capture sentence: phantom token → replacement |
| `platform_tests/scripts/test_no_phantom_spec_citation.py` | new regression lock (2 tests) |

## Specification Links

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `PB-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `bridge/gtkb-wi-3506-phantom-spec-citation-repoint-001.md` — the GO'd proposal.
- `bridge/gtkb-wi-3506-phantom-spec-citation-repoint-002.md` — Codex GO + the four implementation-report conditions satisfied here.
- WI-3506 (`PROJECT-GTKB-SOURCE-OF-TRUTH-FRESHNESS`) — originating defect; documented decision path (b).
- `bridge/gtkb-source-of-truth-freshness-governance-004.md` — Codex NO-GO that first caught the phantom propagating from rule text.
- `DELIB-2521` — owner-decision capture establishing `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` (S376).

## Owner Decisions / Input

- **Owner AskUserQuestion (2026-06-03)** — glossary-review disposition for the `requirement` term: "Fold into WI-3506 (all 3 files)" — re-point the phantom to `GOV-SPEC-CAPTURE-TRANSPARENCY-001` across all three citing rule files via the bridge protocol + per-file narrative-approval packets. This is the owner-decision authority for the protected-narrative edits (no PAUTH; per-file narrative-approval packets carry the per-artifact approval).

## Spec-to-Test Mapping and Verification Evidence

All commands run from `E:\GT-KB`.

| Specification / Condition | Test / Check | Command | Observed |
|---|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — phantom absent, replacement present in the 3 rule files | `test_no_phantom_spec_citation.py` (`test_phantom_absent_from_rule_files`, `test_replacement_present_in_rule_files`) | `uv run --with pytest --with pytest-timeout python -m pytest platform_tests/scripts/test_no_phantom_spec_citation.py -q --no-header -p no:cacheprovider` | `2 passed` |
| `GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — narrative-approval evidence for the 3 edited protected files | `scripts/check_narrative_artifact_evidence.py` | `python scripts/check_narrative_artifact_evidence.py --paths .claude/rules/canonical-terminology.md .claude/rules/prime-builder-role.md .claude/rules/operating-model.md --json` | `status: pass`; `cleared`: all 3 paths; `findings: []` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — lint/format gates on the new test | `ruff check` / `ruff format --check` | `python -m ruff check platform_tests/scripts/test_no_phantom_spec_citation.py` ; `python -m ruff format --check ...` | `All checks passed!` ; `1 file already formatted` |

### Narrative-artifact approval packets (one per edited protected file)

| Packet | target_path | full_content_sha256 (8) |
|---|---|---|
| `.groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-canonical-terminology-md.json` | `.claude/rules/canonical-terminology.md` | `ed18f6d0` |
| `.groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-prime-builder-role-md.json` | `.claude/rules/prime-builder-role.md` | `18e12344` |
| `.groundtruth/formal-artifact-approvals/2026-06-03-claude-rules-operating-model-md.json` | `.claude/rules/operating-model.md` | `71480f77` |

Each packet hashes the staged blob (`git cat-file -p :<path>`) so the
commit-time `narrative-artifact-approval-gate.py` floor matches.

### Confirmation of corrected state

- `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` occurrences across the three live rule files: **0** (phantom absent).
- `GOV-SPEC-CAPTURE-TRANSPARENCY-001` present in all three live rule files: **yes**.

## Out of Scope (Restated)

- `groundtruth-kb/templates/rules/canonical-terminology.md` — the scaffold copy still carries the same phantom citation. The owner scoped this change to the three live rule files; the scaffold follow-up is tracked separately (Opportunity Radar in `-002` flagged it; Prime will capture it as a follow-on WI).
- Historical `bridge/*.md` audit-trail files that mention the phantom are append-only and are intentionally not touched.

## Risk / Rollback

Low: single-token citation corrections (sentence meaning preserved) + one new
test. Rollback is a single-commit revert. No runtime/behavior change.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
