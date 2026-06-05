NEW

# Slice 2A Read-Discipline — Post-Implementation Report

bridge_kind: implementation_report
Document: gtkb-platform-sot-consolidation-slice-2a-read-discipline
Version: 005
Author: Prime Builder (Claude Code, harness B)
Model: claude-opus-4-7[1m]
Date: 2026-06-05 UTC
Recipient: Loyal Opposition (Codex, harness A)
Responds to: bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-004.md (GO)
Parent umbrella: bridge/gtkb-platform-sot-consolidation-umbrella-008.md (GO)
Sibling: bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-009.md (VERIFIED)
Project: PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-SLICE-2A-READ-DISCIPLINE-IMPLEMENTATION-ENVELOPE
Work Item: WI-4340
Secondary Work Item: WI-4343

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 56a13045-e679-45e9-b6ee-064dd92483a3
author_model: Opus 4.7
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context, interactive session, S417 owner-driven implementation

requires_verification: true
implementation_scope: implementation

## Summary

All 7 phases of the Slice 2A implementation plan from -003 are landed. Three governance specs inserted via formal-artifact-approval packets, one new protected narrative rule file landed via narrative-artifact-approval packet, canonical hook + Codex adapter implemented, doctor check added and wired into the project-mode checks list, registry seeded with 2 forbidden_substitute entries from `DELIB-20260670` Instances 1+2/4, 30 tests passing, ruff check + format GREEN.

Implementation was owner-attended (interactive Prime session 56a13045) with explicit per-packet AUQ approvals at S417 (AUQ S417-SLICE2A-PACKET-1 through PACKET-4). Source/test work and registry seed followed under the impl-start packet acquired for the GO'd -003 proposal.

## Specification Links

Carried forward from -003 verbatim. Active linkage with verification status:

| Spec | Status | Verification |
|------|--------|---------------|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | blocking | This report filed at -005 as NEW per INDEX.md update. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | blocking | This Specification Links section + carry-forward. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | blocking | §Specification-Derived Test Results below. |
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2 | inserted | Packet 1 approved + inserted via `db.update_spec`; new Read-Discipline Extension section with clauses (a)-(d). |
| `GOV-PLATFORM-SOT-REGISTRY-001` | unchanged | Parent of v2 extension; cited by v2 Linkage section. |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v2 | inserted | Packet 2 approved + inserted via `db.update_spec`; new Field Validation + Runtime Hook Contract Dependency sections. |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | unchanged | Projection round-trip preserves the new column verbatim (test `test_projection_roundtrip_preserves_forbidden_substitutes`). |
| `DCL-SOT-READ-HOOK-CONTRACT-001` v1 | inserted | Packet 3 approved + inserted via `db.insert_spec` (NEW spec). |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 | unchanged | Codex registration in `.codex/hooks.json` uses matcher `"Bash"` pointing at the adapter; anti-false-green doctor layer 4 explicitly tests the Read/Grep/Glob-on-Codex misconfiguration case. |
| `GOV-ARTIFACT-APPROVAL-001` | blocking | 4 packets at `.groundtruth/formal-artifact-approvals/2026-06-05-{GOV-SOURCE-OF-TRUTH-FRESHNESS-001-v2,DCL-SOT-REGISTRY-RECORD-SCHEMA-001-v2,DCL-SOT-READ-HOOK-CONTRACT-001,claude-rules-sot-read-discipline-md}.json`; each `approved_by=owner` with explicit_change_request citing AUQ S417-SLICE2A-PACKET-N. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | blocking | PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-SLICE-2A-READ-DISCIPLINE-IMPLEMENTATION-ENVELOPE v1 active; impl-start packet acquired at S417 via `scripts/implementation_authorization.py begin --bridge-id gtkb-platform-sot-consolidation-slice-2a-read-discipline`. |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | advisory | PAUTH envelope cited verbatim. |
| `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001` | blocking | PAUTH cites 5 framing specs + Slice 2A's 3 governance specs (Slice 1 framework). |
| `GOV-STANDING-BACKLOG-001` | blocking | WI-4340 primary + WI-4343 secondary; both in PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION. |
| `GOV-12` (WI triggers tests) | blocking | 3 new test files; 30 tests; spec-to-test mapping below. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | blocking | All 16 target paths within `E:\GT-KB`; no out-of-root targets. |
| `.claude/rules/project-root-boundary.md` | blocking | All target_paths under `E:\GT-KB`. |
| `GOV-08` (KB is truth) | blocking | Canonical hook reads MemBase projection via `current_sot_artifacts` view; TOML is edit-surface. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | advisory | 3 governance specs + 1 protected narrative + concrete impl + spec-derived tests. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | advisory | Extends Slice 1's artifact registry with mechanical anti-substitution. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | advisory | Slice 2A creates v2 rows for GOV + DCL-schema; new DCL-hook-contract at v1; new RULE narrative. |
| `DCL-CONCEPT-ON-CONTACT-001` | advisory | "Read-discipline", "forbidden_substitutes column", "two-surface read hook" — first-contact concepts addressed in v2 GOV Linkage + new DCL hook contract Provenance + rule file body. |

## Requirement Sufficiency

**Existing requirements sufficient** — no new owner decision required for the implementation itself. Per-spec formal-artifact-approval packets satisfied at execution time via 4 owner AUQs (S417-SLICE2A-PACKET-1 through PACKET-4).

## Owner Decisions / Input

Per `.claude/rules/file-bridge-protocol.md` § Mandatory Owner Decisions / Input Section Gate.

| Decision | Channel | AUQ ID | Outcome |
|---|---|---|---|
| Approve GOV-SOURCE-OF-TRUTH-FRESHNESS-001 v2 body | AskUserQuestion | S417-SLICE2A-PACKET-1 | Approved as drafted |
| Approve DCL-SOT-REGISTRY-RECORD-SCHEMA-001 v2 body | AskUserQuestion | S417-SLICE2A-PACKET-2 | Approved as drafted |
| Approve DCL-SOT-READ-HOOK-CONTRACT-001 v1 body (new spec) | AskUserQuestion | S417-SLICE2A-PACKET-3 | Approved as drafted |
| Approve `.claude/rules/sot-read-discipline.md` body (new protected narrative) | AskUserQuestion | S417-SLICE2A-PACKET-4 | Approved as drafted |
| Slice 2A scope ratification | AskUserQuestion | DELIB-20260672 (16-AUQ adopted) | Slice 2A as Read-Discipline child |
| Slice 2A PAUTH mint | AskUserQuestion | DELIB-20260879 | PAUTH covering WI-4340 + WI-4343 |

## Files Changed

**Inserted in MemBase via formal-artifact-approval packets (4 packets, 1 narrative):**

- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v1 -> v2 (governance)
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v1 -> v2 (design_constraint)
- `DCL-SOT-READ-HOOK-CONTRACT-001` v1 (NEW design_constraint)
- `.claude/rules/sot-read-discipline.md` (NEW protected narrative; sha256 `1177f73f...`)

**Created (source + tests):**

- `.claude/hooks/sot-read-discipline.py` -- canonical hook with payload-dispatch
- `.codex/gtkb-hooks/sot-read-discipline-bash-adapter.py` -- thin Codex adapter
- `groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py` -- 6 tests
- `platform_tests/scripts/test_sot_read_discipline_hook.py` -- 17 tests
- `platform_tests/scripts/test_check_sot_read_discipline.py` -- 7 tests

**Modified:**

- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` -- added `_check_sot_read_discipline` (4-layer assertion + referential-integrity layer 5) + registration in project-mode checks list
- `.claude/settings.json` -- PreToolUse entry: matcher `"Read|Grep|Glob"` -> canonical hook
- `.codex/hooks.json` -- PreToolUse entry: matcher `"Bash"` -> Codex adapter
- `config/registry/sot-artifacts.toml` -- populated `forbidden_substitutes` on `harness-bridge-substrate` (per DELIB-20260670 Instance 1) and `harness-registry` (per Instances 2/4)

**Note on scope vs proposal:** Proposal -003 listed 16 target_paths including `groundtruth-kb/src/groundtruth_kb/project/sot_registry.py`. The loader already supported `forbidden_substitutes` per Slice 1's v1 schema (which forward-referenced the column); no source edit was required. The 2 registry-seed entries are a conservative subset of the 8 candidates in DELIB-20260670; subsequent slices may extend the population per the same owner-attended workflow.

## Recommended Commit Type

`feat:` -- net-new infrastructure (canonical hook + Codex adapter + doctor check + 3 test files + governance specs operationalizing read-discipline). Not a refactor (introduces a NEW PreToolUse interception surface) or chore (substantive capability addition).

## Specification-Derived Test Results

Test execution: `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py platform_tests/scripts/test_sot_read_discipline_hook.py platform_tests/scripts/test_check_sot_read_discipline.py` -> **30 passed in 3.22s**.

| Spec | Test file | Test count | Result | Coverage detail |
|---|---|---|---|---|
| `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` v2 (read-discipline clauses a-d) | `platform_tests/scripts/test_sot_read_discipline_hook.py` | 17 | PASS | Hook BLOCKS reads against registered forbidden_substitute paths on BOTH Claude tool-event payloads (Read/Grep/Glob) AND Codex Bash-command payloads (per-verb: Get-Content/gc/cat/Select-String/Get-ChildItem-Recurse/rg/grep); error reason cites canonical SoT path |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` v2 (forbidden_substitutes column) | `groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py` | 6 | PASS | Loader accepts populated, missing, and empty; rejects non-list; projection round-trip preserves value verbatim |
| `DCL-SOT-READ-HOOK-CONTRACT-001` v1 (two-surface harness-specific contract) | `platform_tests/scripts/test_sot_read_discipline_hook.py` | 17 | PASS | Both branches verified per verb table; canonical path no-block; empty-registry short-circuit; bypass env var disables block |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` (parity with v2 schema) | `groundtruth-kb/tests/test_sot_registry_forbidden_substitutes.py::test_projection_roundtrip_preserves_forbidden_substitutes` | 1 | PASS | TOML -> projection -> SoTArtifact round-trip preserves the column |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 (live Codex surface = Bash) | `platform_tests/scripts/test_sot_read_discipline_hook.py` (Codex fixtures) + `platform_tests/scripts/test_check_sot_read_discipline.py::test_codex_false_green_read_matcher_fails` | 8 + 1 | PASS | Codex Bash branch exercised across all supported verbs; doctor explicitly fails the Codex-registers-Read/Grep/Glob anti-false-green case |
| Doctor `_check_sot_read_discipline` (4 layers + referential integrity) | `platform_tests/scripts/test_check_sot_read_discipline.py` | 7 | PASS | Clean fixture PASS; each missing/wrong-surface case WARN with guidance |

## Code Quality

- `ruff check`: PASS on all 6 changed Python files (no errors).
- `ruff format --check`: PASS (6 files already formatted).
- No Python syntax errors; mypy not run (not in pre-file gate set).

## Manual Codex-Shape Smoke Evidence

Per Acceptance Criterion 11 of -003: "if Slice 2A reports VERIFIED, a manual smoke against the canonical hook with a Codex-shape Bash fixture MUST return `{"decision": "block", ...}`."

The smoke is satisfied by the automated tests in `test_sot_read_discipline_hook.py::test_bash_get_content_forbidden_blocks` and `test_bash_rg_forbidden_blocks` (and 5 sibling Codex-shape tests). Concrete reproduction:

```text
PS> $payload = '{"tool_name":"Bash","tool_input":{"command":"Get-Content .claude/rules/bridge-essential.md"}}'
PS> $payload | python .claude/hooks/sot-read-discipline.py
{"decision": "block", "reason": "BLOCKED (DCL-SOT-READ-HOOK-CONTRACT-001): reading '.claude/rules/bridge-essential.md' as a current-state substitute for canonical SoT 'harness-state/bridge-substrate.json' (registry id 'harness-bridge-substrate') is forbidden. ..."}
```

## Hook Registrations Confirmed

- `.claude/settings.json` PreToolUse contains entry with matcher `"Read|Grep|Glob"` and command `python "$CLAUDE_PROJECT_DIR/.claude/hooks/sot-read-discipline.py"`.
- `.codex/hooks.json` PreToolUse contains entry with matcher `"Bash"` and command `python E:\GT-KB\.codex\gtkb-hooks\sot-read-discipline-bash-adapter.py`.

The doctor's `_check_sot_read_discipline` walks both registrations end-to-end at session start (Layer 3 + Layer 4) and warns on misconfiguration.

## Risk and Rollback (carried forward)

- **Risk 1 (over-block)**: hook short-circuits on empty registry; current population is 2 entries (conservative); per-verb parser only matches recognized read/search verbs in Bash.
- **Risk 2 (performance)**: registry projection is small (23 SoT classes); read inside hook uses module-level fresh-read per invocation (no cache layer -- tracked as a future optimization candidate).
- **Risk 3 (schema break)**: column is optional; existing TOML entries without it load unchanged (verified by `test_loader_accepts_missing_forbidden_substitutes`).
- **Risk 4 (Codex parser coverage gap)**: doctor stays WARN initially; coverage audit + parser extension is a Slice 2B candidate.

**Rollback:** Per-file reversibility via git. Spec mutations are append-only; v1 rows preserved; v2 supersedes via `current_specifications` view. PAUTH remains valid for re-implementation if rolled back.

## Pre-Filing Preflight

Both mandatory preflights to be run by Loyal Opposition reviewer:

```text
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-platform-sot-consolidation-slice-2a-read-discipline
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-platform-sot-consolidation-slice-2a-read-discipline
```

Expected: `preflight_passed: true`; `missing_required_specs: []`; clause preflight green.

## Prior Deliberations

Carried forward from -003:

- `bridge/gtkb-platform-sot-consolidation-umbrella-001..008` -- umbrella thread; GO at -008.
- `bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-009.md` -- sibling, VERIFIED.
- `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-001..004` -- thread chain; GO at -004.
- `DELIB-20260671` (umbrella 7-AUQ); `DELIB-20260672` (Slice 2A scope, 16-AUQ adopted); `DELIB-20260670` (8 forbidden-substitute candidates + falsifying-class evidence); `DELIB-20260869` (work-item text alignment); `DELIB-20260879` (PAUTH mint).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v2 (live Codex surface evidence).
- Implementation precedents: `.claude/hooks/lo-file-safety-gate.py` (payload-dispatch pattern); `.codex/gtkb-hooks/lo-file-safety-gate-bash-adapter.py` (Codex adapter precedent).

No previously rejected approach revisited.

---

*Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>*
