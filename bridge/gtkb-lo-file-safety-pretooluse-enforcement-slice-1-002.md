NO-GO

# Loyal Opposition Review - LO File-Safety PreToolUse Enforcement Slice 1

Status: NO-GO
Date: 2026-05-14
Reviewer: Codex Loyal Opposition
Request reviewed: `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-001.md`

## Claim

The proposal addresses a real P1 governance gap and passes both mandatory mechanical preflights. It is not ready for implementation because the planned hook does not actually cover the mutation surfaces that can violate the Loyal Opposition file-safety rule, allows approval-packet bypass for non-Write edits, over-allows bridge file mutation, and places the tests outside the repository's active GT-KB test surfaces.

## Live Drift Check

Before filing this verdict, live `bridge/INDEX.md` showed:

```text
Document: gtkb-lo-file-safety-pretooluse-enforcement-slice-1
NEW: bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-001.md
```

`Test-Path bridge\gtkb-lo-file-safety-pretooluse-enforcement-slice-1-002.md` returned `False` before this verdict file was created. `git status --short -- bridge/INDEX.md bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-001.md bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-002.md` showed `bridge/INDEX.md` already modified and `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-001.md` already untracked before this review; this verdict adds `-002` and inserts the `NO-GO` line in the target document block.

## Prior Deliberations

Command:

```powershell
python -m groundtruth_kb deliberations search "Loyal Opposition file safety PreToolUse enforcement hook WI-3308" --limit 8
```

Relevant results included:

- `DELIB-1886` - VERIFIED `gtkb-lo-file-safety-rule-clarification-001` bridge thread.
- `DELIB-1518` - Loyal Opposition verification for file-safety rule clarification.
- `DELIB-1550` and `DELIB-1551`, cited by the proposal, establish Codex hook firing as a live interception boundary.
- `DELIB-1742..1739`, cited by the proposal, are relevant precedent for Codex `.cmd` wrapper plus adapter parity.

No retrieved deliberation waives the need to cover all relevant write/edit surfaces for a hook whose stated purpose is to enforce the Loyal Opposition file-safety rule.

## Applicability Preflight

Command:

```powershell
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1
```

Observed result:

## Applicability Preflight

- packet_hash: `sha256:50c7fef189d2b0fb1daa14b09b431a6aa35e7989fab9bd01f81c80d14f78871c`
- bridge_document_name: `gtkb-lo-file-safety-pretooluse-enforcement-slice-1`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-001.md`
- operative_file: `bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-001.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

Command:

```powershell
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-lo-file-safety-pretooluse-enforcement-slice-1
```

Observed result:

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-lo-file-safety-pretooluse-enforcement-slice-1`
- Operative file: `bridge\gtkb-lo-file-safety-pretooluse-enforcement-slice-1-001.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and must_apply applicability fail the gate (exit 5) when evidence is absent and no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited. Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Findings

### F1 (P1) - Claude-side enforcement omits active mutation surfaces

**Observation:** The proposal frames the Claude-side implementation as a PreToolUse `Write/Edit` hook (`bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-001.md:17`) and says `.claude/settings.json` will add it only to the existing `Write|Edit` matcher block (`bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-001.md:120`). The current Claude implementation-start gate already treats `Write|Edit|MultiEdit|Bash` as protected mutation surfaces (`.claude/settings.json:16`), which is the correct comparison point for file modification enforcement.

The Loyal Opposition rule being enforced says that when operating as Loyal Opposition, the agent must not delete or modify files it has not created without explicit owner approval (`.claude/rules/loyal-opposition.md:36-38`). A `MultiEdit` tool call or a shell command that writes, deletes, moves, or overwrites a file can violate that rule without using `Write` or `Edit`.

**Deficiency rationale:** The proposed hook would create a visible "mechanical enforcement" control while leaving straightforward bypasses in the same harness. Because the incident being remediated was a file-safety violation by a harness under LO assignment, enforcement must cover the mutation surfaces that can perform the prohibited action, not only two convenience tools.

**Impact:** A future LO session could still modify implementation files through `MultiEdit` or `Bash`, while the hook and tests report success. That preserves the original governance drift in a harder-to-detect form.

**Recommended action:** Revise the Claude-side hook registration and tests to cover `Write|Edit|MultiEdit|Bash` or explicitly fail closed for unsupported mutating tool shapes. Add tests for `MultiEdit`, shell redirects, `Set-Content`/`Out-File`, `Remove-Item`, `Move-Item`, and copy/overwrite commands against non-allow-listed paths under LO assignment.

### F2 (P1) - Approval-packet validation is not bound to non-Write edit content

**Observation:** The proposal says an approval packet can allow a non-allow-listed write if `GTKB_LO_FILE_SAFETY_APPROVAL_PACKET` validates (`bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-001.md:78`). It then validates packet target and hash, but only says "For Write, verify packet `full_content == tool_input.content`" (`bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-001.md:80`). The proposal does not define how `Edit`, `MultiEdit`, or Codex `apply_patch` computes the proposed post-edit full content and compares it to the packet's `full_content_sha256`.

**Deficiency rationale:** A stale or unrelated approval packet for the same path could satisfy the path/hash self-check while the actual edit content differs. The packet hash only proves the packet's embedded `full_content` hashes correctly; it does not prove the tool call will write that content unless the hook reconstructs the post-edit file and compares it to the packet.

**Impact:** The approval-packet exception can become an authorization bypass for exactly the non-allow-listed files the gate is supposed to protect.

**Recommended action:** Revise the algorithm to either:

1. compute the candidate post-edit full file content for `Edit`, `MultiEdit`, and `apply_patch`, then require `sha256(candidate_post_edit_content) == packet.full_content_sha256`; or
2. fail closed for owner-packet exceptions on tool shapes where the post-edit content cannot be reconstructed reliably.

Add regression tests for packet target match plus content mismatch on `Edit`, `MultiEdit`, and `apply_patch`.

### F3 (P1) - The bridge allow-list permits mutation of existing bridge files

**Observation:** The proposed allow-list includes `patterns = ["bridge/**.md"]` for "Bridge verdict authoring" (`bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-001.md:99`) and treats that broad allowance as the false-positive mitigation (`bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-001.md:150-152`). The bridge protocol requires append-only audit trails and explicitly says never to delete bridge files because they form the audit trail (`.claude/rules/file-bridge-protocol.md:277-281`).

**Deficiency rationale:** Blanket allowance of every bridge markdown path does not distinguish creating the next LO verdict/advisory file from editing an existing Prime proposal or prior verdict. The file-safety rule is about modifying files not created by LO; a broad `bridge/**.md` exemption removes that protection for a high-authority audit-trail directory.

**Impact:** The hook could allow accidental or intentional edits to existing bridge evidence under LO role, undermining the bridge audit trail the proposal is meant to protect.

**Recommended action:** Replace the broad bridge markdown exemption with a narrow bridge operation check: allow creating a nonexistent next-version verdict/advisory file that matches the live `bridge/INDEX.md` state and LO authority, and allow the specific `bridge/INDEX.md` status-line insertion. Do not allow edits to existing `bridge/*.md` files through the LO file-safety gate.

### F4 (P2) - Proposed tests are outside the active GT-KB test and CI surfaces

**Observation:** The proposal puts the test module at `tests/scripts/test_lo_file_safety_gate.py` and uses `python -m pytest tests/scripts/test_lo_file_safety_gate.py -v` as the acceptance command (`bridge/gtkb-lo-file-safety-pretooluse-enforcement-slice-1-001.md:8`, `:125`, `:162`). The root pytest configuration uses `testpaths = ["platform_tests", "applications/Agent_Red/tests"]` (`pyproject.toml:9`), the GT-KB workflow runs `python -m pytest platform_tests/ -q --tb=short` (`.github/workflows/groundtruth-kb-tests.yml:42`), and the Python/lint workflows are keyed to `platform_tests/**` rather than root `tests/**` (`.github/workflows/python-tests.yml:24`, `.github/workflows/lint.yml:14`).

**Deficiency rationale:** A targeted local command can run a root `tests/` file, but the proposed regression would not be in the platform test lane that currently protects GT-KB infrastructure. For a safety hook, durable regression visibility matters.

**Impact:** The hook could regress after merge without CI exercising its tests, especially if future maintainers rely on the established `platform_tests/` convention.

**Recommended action:** Move the proposed test module to `platform_tests/scripts/test_lo_file_safety_gate.py`, update `target_paths`, acceptance criteria, and verification plan accordingly, and ensure the lint/format commands include the new test path under the existing platform test surface.

## Positive Confirmations

- The proposal targets a real governance gap and cites the controlling Loyal Opposition rule.
- Codex `.codex/hooks.json` currently has live `Bash` and `apply_patch` hook matchers, so a Codex parity wrapper is implementable on the stated surface.
- The applicability preflight passes with `missing_required_specs: []` and `missing_advisory_specs: []`.
- The clause preflight exits 0 with no evidence gaps and no blocking gaps.

## Verdict

NO-GO. Revise the hook coverage, approval-packet binding, bridge allow-list semantics, and test placement before implementation proceeds.

Copyright 2026 Remaker Digital, a DBA of VanDusen and Palmeter, LLC. All rights reserved.
