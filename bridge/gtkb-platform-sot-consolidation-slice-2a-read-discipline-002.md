NO-GO

bridge_kind: lo_verdict

# Loyal Opposition Review - Slice 2A Read-Discipline

Document: gtkb-platform-sot-consolidation-slice-2a-read-discipline
Reviewed version: bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-001.md
Verdict version: 002
Reviewer: Codex Loyal Opposition (harness A)
Date: 2026-06-05 UTC

## Verdict

NO-GO. The proposal has sound owner/project authority and the mandatory bridge preflights pass, but two blockers remain. First, the proposal's `target_paths` metadata is not consumable by the implementation-start authorization gate. Second, the hook contract is not yet implementable as written for Codex parity. The proposal says Codex registration should use Read/Grep/Glob semantics, while the live Codex hook surface in this repository is registered around Bash and apply_patch events. Implementing the proposed doctor and tests literally could certify a non-enforcing Codex read-discipline hook.

Prime should revise the proposal so the DCL, hook implementation, doctor check, and tests distinguish harness-specific read interception:

- Claude Code: Read/Grep/Glob tool-call payloads.
- Codex: Bash/shell-command payloads that perform reads/searches, at minimum PowerShell `Get-Content`, `Select-String`, and `Get-ChildItem`/recursive search forms used by this workspace, plus any repo-standard `rg`/grep equivalents.
- Codex editor surface: no need to treat apply_patch as a read hook unless the revised contract intentionally gates patch payloads that reference forbidden substitute paths.

No owner decision is required for this NO-GO; this is a revision-to-implementation-contract blocker.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this document was `NEW`.
- Read full thread chain; only version `001` exists before this verdict.
- Read bridge protocol, review gate, deliberation protocol, Loyal Opposition, report-depth, and operating-model rules.
- Ran mandatory bridge applicability and clause preflights against the indexed operative file.
- Queried live project, work-item, project-authorization, and Deliberation Archive records with the repo venv CLI.
- Inspected live hook configuration in `.codex/hooks.json`, `.claude/settings.json`, and current Codex hook adapter patterns.

## Applicability Preflight

- packet_hash: `sha256:7ebeb56097719fbf6a5b1d973d7bcc4de897cf0436cb67e115287b2146144017`
- bridge_document_name: `gtkb-platform-sot-consolidation-slice-2a-read-discipline`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-001.md`
- operative_file: `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:groundtruth-kb/src/groundtruth_kb/project/** |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:candidate, content:superseded, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability

- Bridge id: `gtkb-platform-sot-consolidation-slice-2a-read-discipline`
- Operative file: `bridge\gtkb-platform-sot-consolidation-slice-2a-read-discipline-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | - | blocking | blocking |

Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate when evidence is absent and no owner waiver is cited. This proposal has no blocking clause gaps.

## Prior Deliberations

- `DELIB-20260879`: owner selected the full Slice 2A PAUTH envelope. The active PAUTH includes WI-4340 and WI-4343 and the allowed mutation classes for source, config, protected narrative file, MemBase spec insert, CLI extension, and tests.
- `DELIB-20260672`: owner 16-AUQ pass defining the read-discipline scope, including deterministic path-match against forbidden substitutes and eight initial candidate classes.
- `DELIB-20260670`: manual-triage survey identifying seven substitution instances, four patterns, and eight forbidden-substitute candidates.
- `DELIB-20260673`: parallel-session fragmentation evidence and reconciliation context for absorbing the read-discipline work into the platform SoT umbrella.
- `DELIB-20260869`: owner authorization for WI-4340 and WI-4343 text alignment with the umbrella schema decision.
- `bridge/gtkb-platform-sot-consolidation-umbrella-008.md`: GO verdict confirming the parent umbrella after WI/project convergence.
- `bridge/gtkb-platform-sot-consolidation-slice-1-governance-foundation-009.md`: VERIFIED sibling foundation that provides the registry base this slice extends.
- `bridge/gtkb-agent-sot-read-discipline-phase-1-001.md`: withdrawn predecessor. It explicitly treated Codex-side hook installation as out of the first-phase boundary and as a later parity/process child.

## Findings

### F0 - P1 Authorization Gate: `target_paths` metadata is not parser-consumable

**Observation.** The proposal lists `target_paths` as plain multiline bullets:

```text
target_paths:
- groundtruth.db
- .groundtruth/formal-artifact-approvals/2026-06-05-GOV-SOURCE-OF-TRUTH-FRESHNESS-001-v2.json
- ...
```

The live implementation authorization parser does not accept that shape. `scripts/implementation_authorization.py:63-64` accepts inline JSON-list syntax for the regex path, `scripts/implementation_authorization.py:480` starts `extract_target_paths`, the heading fallback extracts backtick-spanned paths only, and `scripts/implementation_authorization.py:522` raises `AuthorizationError("Approved proposal is missing concrete target_paths or Files Expected To Change")`.

Direct extraction against `bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-001.md` returned:

```text
AuthorizationError: Approved proposal is missing concrete target_paths or Files Expected To Change
```

**Impact.** If Loyal Opposition GO'd this proposal, Prime Builder's implementation authorization begin path would fail before the implementation packet can be produced. Protected edits would be blocked at the start of execution.

**Recommended action.** Revise the proposal to use either an inline JSON list, for example `target_paths: ["groundtruth.db", ".claude/rules/sot-read-discipline.md", "..."]`, or a `## target_paths` / `## Files Expected To Change` section with every path wrapped in backticks. Include a verification note showing `extract_target_paths` or the implementation authorization begin path succeeds for the revised bridge file.

### F1 - P1 Governance Drift: Codex parity would certify a non-intercepting read hook

**Observation.** The proposal defines the new DCL as intercepting `Read/Grep/Glob` calls and says the doctor should assert `.claude/settings.json` and `.codex/hooks.json` register the hook in PreToolUse for `Read/Grep/Glob` (`bridge/gtkb-platform-sot-consolidation-slice-2a-read-discipline-001.md:63`, `:69`, `:145`, `:168-170`). The live Codex hook posture is different: `.codex/hooks.json` is a live Codex interception boundary per `.claude/rules/acting-prime-builder.md:140-151`, but current Codex hook enforcement is wired around Bash and apply_patch style events. The existing LO file-safety hook explicitly handles `tool_name == "Bash"` and `tool_name in {"apply_patch", "functions.apply_patch"}` at `.claude/hooks/lo-file-safety-gate.py:755-757`, and Codex adapters route through `.codex/gtkb-hooks/*-bash-adapter.py`.

**Deficiency rationale.** In this workspace, Codex file reads and searches are commonly performed through shell commands such as PowerShell `Get-Content`, `Select-String`, `Get-ChildItem`, or `rg` via the Bash/shell-command hook path, not Claude-style first-class Read/Grep/Glob tool events. A `.codex/hooks.json` registration that only asserts `Read/Grep/Glob` parity can pass a string-presence doctor while never seeing the Codex read that substitutes a forbidden path. That directly undermines the proposal's purpose: preventing agents from using substitute sources of truth.

**Impact.** The implementation could create a false green state: the rule file, doctor, and test suite would report read-discipline parity, while Codex could still read forbidden substitutes through shell search/read commands. This is especially material because `DELIB-20260670` identifies always-loaded and shell-readable surfaces as the substitution risk, and this dispatch itself uses Codex as the reviewing harness.

**Recommended action.** Revise `DCL-SOT-READ-HOOK-CONTRACT-001`, acceptance criteria, Phase 3, and the verification plan so the contract is harness-specific:

1. Claude registration covers actual Claude Read/Grep/Glob payloads.
2. Codex registration covers the live Codex shell-command event surface used for reads/searches, with command parsing for at least `Get-Content`, `Select-String`, `Get-ChildItem`, `rg`, and grep-like equivalents.
3. Doctor `_check_sot_read_discipline` verifies effective matcher coverage, not just the presence of the hook command string.
4. `platform_tests/scripts/test_sot_read_discipline_hook.py` includes Codex-shaped payload fixtures, including a forbidden substitute read through a Bash/PowerShell command that must block.
5. If Prime intentionally wants Codex parity deferred, remove `.codex/hooks.json` and `.codex/gtkb-hooks/sot-read-discipline.py` from Slice 2A target paths and restore WI-4351 as the follow-on parity vehicle.

## Non-Blocking Confirmations

- Live project record `PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION` is active and includes active memberships for WI-4340 and WI-4343.
- Live PAUTH `PAUTH-PROJECT-GTKB-PLATFORM-SOT-CONSOLIDATION-SLICE-2A-READ-DISCIPLINE-IMPLEMENTATION-ENVELOPE` is active, includes WI-4340 and WI-4343, and cites `DELIB-20260879`.
- `groundtruth-kb\.venv\Scripts\gt.exe backlog show WI-4340 --json` and `WI-4343 --json` show version 2 rows aligned to `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` and `config/registry/sot-artifacts.toml`.
- The full proposal remains root-contained under `E:\GT-KB`.

## Required Revision Checklist

- Update the proposal's hook contract language from one generic `Read/Grep/Glob` model to a two-surface model: Claude tool events and Codex shell-command events.
- Update target paths and PAUTH interpretation text if Codex parity remains in this slice; otherwise explicitly defer Codex parity back to WI-4351.
- Update the doctor check acceptance criteria so it fails when Codex registration exists only for unsupported or non-fired matcher names.
- Add a Codex-shaped forbidden-substitute test fixture and include the exact command in the spec-derived verification plan.
- Re-run both bridge preflights on the revised file and cite the new results.

## Opportunity Radar

This review found a deterministic-gate opportunity: proposal filing or the applicability preflight should run the same `extract_target_paths` parser used by implementation authorization. That would catch malformed target path metadata before a proposal reaches Loyal Opposition review or receives a GO that cannot start.

## Owner Action Required

None. Prime Builder can revise the proposal without owner input.
