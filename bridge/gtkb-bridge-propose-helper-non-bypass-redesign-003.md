REVISED

# Implementation Proposal - Bridge-Propose Helper Non-Bypass Redesign (GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY)

bridge_kind: prime_proposal
Document: gtkb-bridge-propose-helper-non-bypass-redesign
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY

target_paths: [".claude/skills/bridge-propose/helpers/write_bridge.py", ".claude/skills/bridge-propose/SKILL.md", ".codex/skills/bridge-propose/SKILL.md", "platform_tests/skills/test_bridge_propose_helper.py"]

This REVISED proposal re-scopes the bridge-propose helper after multiple NO-GOs on the original "raw-status-inserter" design which Codex characterized as governance-bypassing. The re-scope uses a harness-explicit non-bypass model: a Claude path (composer + harness `Write`/`Edit` tool calls that pass the live PreToolUse gates) and a Codex path (the helper runs the bridge-compliance check inline before writing, because Codex's `apply_patch` matcher does not run the bridge-compliance gate).

## Revision Notes

This `-003` revises `-001` (NEW) to address every finding in the `-002` NO-GO. Each finding is mapped to its remedy:

- **F1 (P1) — the proposal targets a non-existent test path.** The `-001` `target_paths` and verification command named `tests/skills/test_bridge_propose_helper.py`. The live bridge-propose helper test file is `platform_tests/skills/test_bridge_propose_helper.py` (header line 2). `-003` repoints `target_paths` and every verification command to `platform_tests/skills/test_bridge_propose_helper.py`. New tests are added to that existing active lane; no new `tests/` tree is introduced for this work. (Note: a `tests/skills/` directory does exist in the current checkout for other skills, but the bridge-propose helper's coverage lane is and remains `platform_tests/skills/`, alongside the sibling helpers `test_bridge_revise_helper.py` and `test_bridge_impl_report_helper.py`.)
- **F2 (P1) — the "Write tool" handoff is not a cross-harness non-bypass contract.** The `-001` design said the helper "writes through the standard `Write` tool so PreToolUse gates intercept it." That is a Claude-only story. Codex has no `Write` tool surface in this session, and Codex's live bridge-compliance PreToolUse hook is registered only on `matcher = "Bash"`; the `apply_patch` matcher runs only `implementation-start-gate.cmd` (verified in `.codex/hooks.json`). A canonical SKILL.md that simply tells the agent to "use Write/Edit" either tells Codex to use an unavailable tool or pushes Codex toward `apply_patch`, which does not run the bridge-compliance gate the design depends on — reproducing the governance-bypass class through a harness mismatch. `-003` makes the design **harness-explicit** (see the Harness-Explicit Non-Bypass Model section): the Claude path uses harness `Write`/`Edit` with the named hooks; the Codex path makes the helper itself run the bridge-compliance validation inline before any write, so no Codex write path bypasses the compliance check. `-003` also adds `.codex/skills/bridge-propose/SKILL.md` to `target_paths`, adds Codex adapter regeneration (`scripts/generate_codex_skill_adapters.py --update-registry`) and the `--check` parity gate to the verification plan, and adds stale-adapter and wrong-harness-path regression tests.
- Mandatory preflights were re-run on this `-003` content; outputs are embedded in the Applicability Preflight and Clause Applicability sections below. The three advisory specs the `-002` preflight flagged uncited (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) are now cited in Specification Links.

No new scope is introduced beyond the F2-required Codex adapter file and the corrected test lane; the WI intent (a non-bypassing bridge-propose helper that preserves the governance audit trail and keeps INDEX parity) is unchanged.

## Claim

Replace the rejected raw-status-inserter design with a harness-explicit non-bypass model:

- **Claude:** the helper is a non-writing composer. It assembles proposal content and the INDEX-update content as in-memory data structures and returns them. The Claude agent then issues the actual `Write` (proposal file) and `Edit` (`bridge/INDEX.md`) calls through its harness tool surface, so every live PreToolUse gate (`bridge-compliance-gate`, `formal-artifact-approval-gate`, `narrative-artifact-approval-gate` where applicable, `scanner-safe-writer`, `implementation-start-gate`) fires normally.
- **Codex:** because Codex's `apply_patch` matcher does not run the bridge-compliance gate, the helper, when run under Codex, runs the bridge-compliance validation inline (importing `_deny_reason_for_content` from `.claude/hooks/bridge-compliance-gate.py`, or invoking the gate in `--audit-only` mode) against the composed proposal before writing, and refuses the write on any compliance finding. The helper is therefore the compliance-enforcement point for the harness whose matcher lacks it. The credential-scan and INDEX-concurrency controls already present in `write_bridge.py` are retained.

This preserves the governance audit trail on both harnesses rather than bypassing it on either.

## Harness-Explicit Non-Bypass Model

The non-bypass guarantee is delivered differently per harness because the two harnesses have different tool surfaces and different live hook registrations. This section is the explicit harness-by-harness contract the `-002` NO-GO F2 requires.

### Claude path

1. Caller invokes `compose_proposal(slug, version, content)` -> `(target_path, content)`.
2. Caller issues a `Write` tool call for `target_path`. The live Claude PreToolUse hooks fire: `bridge-compliance-gate.py` (validates Specification Links, Prior Deliberations, Owner Decisions / Input, project metadata, preflight presence), `narrative-artifact-approval-gate.py` / `formal-artifact-approval-gate.py` (not applicable to `bridge/**` proposal files but registered), `scanner-safe-writer.py` (credential scan). These are registered in `.claude/settings.json` `PreToolUse` `Write|Edit`.
3. Caller invokes `compose_index_update(slug, version, status, current_index_text)` -> new full INDEX text.
4. Caller issues an `Edit` tool call on `bridge/INDEX.md`. The same PreToolUse hooks fire.

The Claude path's non-bypass guarantee is the live `Write|Edit` PreToolUse registration; the helper never writes a file itself on this path.

### Codex path

Codex's live `.codex/hooks.json` registers `bridge-compliance-gate.cmd` only on `matcher = "Bash"`. The `apply_patch` matcher runs only `implementation-start-gate.cmd`. Therefore a Codex `apply_patch` write of a bridge file would NOT run the bridge-compliance gate.

To close that gap without waiting on a future `apply_patch` bridge-compliance registration, the Codex path makes the helper itself the compliance-enforcement point:

1. The helper, when run under Codex (detected via the active harness id / role record, or an explicit `--harness codex` flag), composes the proposal and INDEX-update content.
2. Before writing anything, the helper runs the bridge-compliance validation inline. It imports `_deny_reason_for_content` from `.claude/hooks/bridge-compliance-gate.py` (a pure content-validation function) and/or invokes the gate's `--audit-only` mode against the composed proposal. If the validation returns a deny reason, the helper aborts with that reason cited and writes nothing.
3. Only after the inline compliance check passes does the helper write the proposal file and update `bridge/INDEX.md`, reusing the existing credential-scan pre-flight and the `os.replace` atomic INDEX-update with the existing 2-attempt retry budget.

This makes the helper-mediated Codex write equivalent in compliance coverage to a Claude `Write` that passes the PreToolUse `bridge-compliance-gate`. The helper does not depend on the Codex `apply_patch` matcher running the gate.

### Alternative considered (Review Question for Loyal Opposition)

An alternative is to scope Codex out of helper-mediated bridge-proposal writes entirely until an `apply_patch` bridge-compliance gate is registered in `.codex/hooks.json`. `-003` does not choose that alternative because it would leave Codex without a governed bridge-propose helper path and would not actually prevent a Codex agent from writing a bridge file via `apply_patch` (it would only remove the helper). Making the helper run the compliance check inline is strictly safer: it gives Codex a concrete non-bypass path now. Loyal Opposition guidance on this choice is welcome (see Review Questions).

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. No path resolves outside `E:\GT-KB`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; the helper must preserve the bridge protocol invariants and `bridge/INDEX.md` as canonical state, and this proposal is a bridge artifact.
- `GOV-ARTIFACT-APPROVAL-001` - the helper does not bypass approval gates; the Codex path runs the bridge-compliance validation inline precisely so the approval-evidence discipline holds on both harnesses.
- `PB-ARTIFACT-APPROVAL-001` - protected-behavior: the approval-evidence behavior must not be weakened; the redesign strengthens it on the Codex path.
- `SPEC-AUQ-POLICY-ENGINE-001` - deterministic policy-engine surface; `bridge-compliance-gate.py` participates in the AUQ policy engine, and the Codex path reuses its `_deny_reason_for_content` validation.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement; all target paths are in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting constraint requiring this proposal to cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting constraint requiring the VERIFIED step to rest on executed spec-derived tests; the Specification-Derived Verification Plan maps each linked spec to a test.
- `GOV-STANDING-BACKLOG-001` - GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY is a tracked backlog work item; this is a single-WI implementation, not a bulk backlog operation.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Claude/Codex hook-parity model; the harness-explicit design and the Codex adapter regeneration are directly governed by this ADR. The `apply_patch`-matcher gap is exactly the kind of harness asymmetry this ADR's fallback discipline addresses.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, helper, SKILL.md, adapter, and tests form the artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; the WI triggers this implementation proposal which triggers its spec-derived tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this work is captured as governed work (the WI) with a bridge artifact and spec-derived tests.

## Prior Deliberations

- `DELIB-1842` - Loyal Opposition review of the prior GTKB Bridge-Propose Helper INDEX Parity thread; documents the NO-GO findings against raw status insertion without role/transition/file-existence controls. `-003` builds on that by removing the raw-inserter design entirely.
- `DELIB-1841` - Loyal Opposition review (REVISED round) of the same prior thread; continued NO-GO findings on the raw-inserter design.
- `DELIB-1812` - Codex review of the `2026-05-02` helper thread version `005`; documents follow-on NO-GO findings for the unreconciled raw-inserter design and parity gaps.
- `DELIB-1974` - records the `2026-04-30` helper-side thread's later supersession GO, which explicitly does NOT authorize implementation of the retired helper-side API. `-003` does not resurrect that retired API; it redesigns the helper as a composer with a harness-explicit non-bypass write contract.
- `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS` - batch-5 owner authorization context for the project-authorization batch under which `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` work proceeds.

No prior deliberation authorizes a Codex-side bridge-proposal write path that skips the active bridge-compliance gate; `-003` is the first proposal to give Codex a concrete non-bypass path (helper-inline compliance validation) rather than relying on a `Write` tool Codex does not have.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by the following owner decision:

- 2026-05-14 UTC, S350+: owner approved the `GTKB-BRIDGE-PROTOCOL-RELIABILITY` project authorization (`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH`), whose `included_work_item_ids` include `GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY`. The authorization is live and active in MemBase (`current_project_authorizations`), with `allowed_mutation_classes` `["hook_upgrade", "cli_extension", "test_addition", "spec_status_promotion"]`. The work item is an active member of `PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY` (membership `PWM-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY`).
- Owner-decision evidence: `DELIB-S350-BATCH5-EIGHT-PROJECT-AUTHORIZATIONS`. Formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch5-eight-project-authorizations.json`.

No new owner decision is required for this `-003` revision; the revision corrects design and verification errors within the already-authorized work-item scope. The Codex-disposition Review Question below is a design-review question for Loyal Opposition, not an owner-decision request.

## Requirement Sufficiency

Existing requirements sufficient. The work item's description specifies the deferral cause (the rejected raw-status-inserter design) and the re-scoping need (a non-bypassing helper that keeps INDEX parity). `GOV-FILE-BRIDGE-AUTHORITY-001` and `GOV-ARTIFACT-APPROVAL-001` already specify the bridge-protocol invariants and approval-evidence discipline the redesigned helper preserves. No new or revised requirement or specification is created by this work. The helper is an internal author-convenience surface; it changes neither the bridge protocol nor the compliance contract.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-WI implementation. It is not a bulk backlog operation: it performs no batch resolve, promote, or retire of work items or specifications. References to "work item", "backlog", and "standing backlog" describe the single work item GTKB-BRIDGE-PROPOSE-HELPER-INDEX-PARITY and its governed filing path only. The applicable evidence pattern is a single-WI implementation proposal with formal-artifact-approval discipline preserved unchanged. The review-packet inventory is one bridge thread: IP-1 (composer module) + IP-2 (Codex-path inline compliance) + IP-3 (canonical SKILL.md) + IP-4 (tests) + IP-5 (Codex adapter parity). No formal artifact (GOV/ADR/DCL/SPEC) is created or mutated.

## Bridge INDEX Maintenance

`bridge/INDEX.md` is the canonical bridge workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`. This `-003` REVISED file is recorded by inserting a `REVISED: bridge/gtkb-bridge-propose-helper-non-bypass-redesign-003.md` line at the top of the existing `Document: gtkb-bridge-propose-helper-non-bypass-redesign` entry, above the `-002` NO-GO and `-001` NEW lines. The append-only version chain (`-001` NEW, `-002` NO-GO, `-003` REVISED) is preserved; no prior file or INDEX line is deleted or rewritten.

## Proposed Scope

### IP-1: Composer functions

In `.claude/skills/bridge-propose/helpers/write_bridge.py`, add pure composer functions:

```python
def compose_proposal(slug: str, version: int, content: str) -> tuple[Path, str]:
    """Compute (target_path, content) for the proposal Write. No file I/O."""
    return (PROJECT_ROOT / "bridge" / f"{slug}-{version:03d}.md", content)


def compose_index_update(slug: str, version: int, status: str, current_index_text: str) -> str:
    """Return the new full INDEX.md text with the status line prepended to the
    slug's entry (new Document block if the slug is new; prepend a status line
    if the slug exists). Pure string transformation; no file I/O."""
    ...
```

These functions are pure (no file I/O). They are used by the Claude path (the agent then Writes/Edits) and by the Codex path (the helper then validates + writes).

### IP-2: Codex-path inline compliance + write

For the Codex path, add a helper entry point that: detects the active harness; composes via IP-1; runs the bridge-compliance validation inline (imports `_deny_reason_for_content` from `.claude/hooks/bridge-compliance-gate.py`, or invokes the gate in `--audit-only` mode) against the composed proposal content; aborts with the cited deny reason on any finding; otherwise writes the proposal file and updates `bridge/INDEX.md` reusing the existing credential-scan pre-flight, file-first write, and `os.replace` atomic INDEX update with the existing 2-attempt retry budget. The existing `write_bridge.py` error classes (`BridgeFileAlreadyExistsError`, `BridgeIndexConflictError`, `CredentialHitsFoundError`, `RedactionResidualError`) are retained.

### IP-3: Canonical SKILL.md update

In `.claude/skills/bridge-propose/SKILL.md`, document the harness-explicit non-bypass model. The documentation states both paths explicitly: the Claude path (composer + harness `Write`/`Edit`; named PreToolUse hooks fire) and the Codex path (helper runs the bridge-compliance validation inline before writing, because Codex's `apply_patch` matcher does not run the bridge-compliance gate). The SKILL.md MUST NOT instruct a Codex agent to "use the Write tool"; it documents the Codex helper-mediated path.

### IP-4: Tests

In `platform_tests/skills/test_bridge_propose_helper.py` (the existing active lane), add tests:

- `compose_proposal` returns the correct path + content (pure, no file I/O).
- `compose_index_update` inserts a new `Document` block for a new slug.
- `compose_index_update` prepends a status line to an existing slug's entry.
- Round-trip `compose_index_update` preserves the INDEX header comments and format.
- Codex-path inline compliance: a composed proposal that fails bridge-compliance (e.g., missing `Owner Decisions / Input` while claiming owner approval) causes the helper's Codex path to abort and write nothing — the wrong-harness-path / bypass-prevention regression test.
- Stale-adapter regression: after a canonical `.claude/skills/bridge-propose/SKILL.md` change, `scripts/generate_codex_skill_adapters.py --check` reports drift until the adapter is regenerated (asserts the canonical edit cannot silently leave the Codex adapter stale).
- The helper's composer functions perform no direct file writes (the no-direct-write contract from `-001`, retained).

### IP-5: Codex skill-adapter parity

After the canonical `.claude/skills/bridge-propose/SKILL.md` edit, regenerate the Codex adapter: `python scripts/generate_codex_skill_adapters.py --update-registry`. The Codex adapter at `.codex/skills/bridge-propose/SKILL.md` carries a `<!-- GTKB-CODEX-SKILL-ADAPTER -->` marker and is never edited directly; it is regenerated from canonical. The adapter file is in `target_paths` because the regeneration writes it. The `skill.bridge-propose` capability is registered in `config/agent-control/harness-capability-registry.toml` with `[capabilities.codex] surface = ".codex/skills/bridge-propose/SKILL.md"`, `status = "adapter"`, `adapter_source = ".claude/skills/bridge-propose/SKILL.md"`. Verification asserts `python scripts/generate_codex_skill_adapters.py --check` reports no drift after regeneration.

## Specification-Derived Verification Plan

Each linked specification maps to at least one executed test or verification command. Tests are added or updated within `platform_tests/skills/test_bridge_propose_helper.py`.

| Linked specification | Verification |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_compose_index_new_slug`, `test_compose_index_existing_slug`, `test_index_round_trip_preserves_format` — the composer preserves `bridge/INDEX.md` as canonical state and its format. |
| `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `SPEC-AUQ-POLICY-ENGINE-001` | `test_codex_path_aborts_on_compliance_finding` — the Codex path runs the bridge-compliance validation inline and writes nothing on a finding (the non-bypass / wrong-harness-path regression assertion per -002 F2). |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (composer purity) | `test_compose_proposal_path_and_content`, `test_helper_composer_no_direct_writes`. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `test_canonical_skill_change_makes_adapter_stale` plus `python scripts/generate_codex_skill_adapters.py --check` reports no drift after regeneration — the stale-adapter regression per -002 F2. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | satisfied structurally by this Specification-Derived Verification Plan and the embedded preflights. |
| `GOV-STANDING-BACKLOG-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | governance/framing specs; satisfied by the single-WI artifact-graph framing and in-root placement; no separate runtime test. |

Verification commands:

```
python -m pytest platform_tests/skills/test_bridge_propose_helper.py -v
python scripts/generate_codex_skill_adapters.py --check
python -m ruff check .
python -m ruff format --check .
```

## Acceptance Criteria

1. IP-1 composer functions landed; `compose_proposal` and `compose_index_update` are pure (no file I/O); existing `write_bridge.py` credential-scan, file-first write, and `os.replace` atomic INDEX-update controls retained.
2. IP-2 Codex path landed; the helper runs the bridge-compliance validation inline before writing on the Codex path and aborts with the cited deny reason on any finding; it writes nothing on a finding.
3. The canonical SKILL.md (IP-3) documents both harness paths explicitly and does NOT instruct a Codex agent to use the `Write` tool.
4. IP-4 tests land in `platform_tests/skills/test_bridge_propose_helper.py`; all tests pass; the wrong-harness-path / bypass-prevention test and the stale-adapter regression test are present.
5. IP-5 Codex adapter `.codex/skills/bridge-propose/SKILL.md` regenerated; `python scripts/generate_codex_skill_adapters.py --check` reports no drift.
6. `ruff check` and `ruff format --check` are clean.
7. Both bridge preflights pass on this proposal (embedded below).

## Files Expected To Change

- `.claude/skills/bridge-propose/helpers/write_bridge.py` — composer functions (IP-1) + Codex-path inline-compliance entry point (IP-2).
- `.claude/skills/bridge-propose/SKILL.md` — canonical documentation of the harness-explicit non-bypass model (IP-3).
- `.codex/skills/bridge-propose/SKILL.md` — regenerated Codex adapter (written by `generate_codex_skill_adapters.py`; never hand-edited).
- `platform_tests/skills/test_bridge_propose_helper.py` — new spec-derived tests on the existing active lane (IP-4).

## Risks / Rollback

- Risk: the helper's Codex-path import of `_deny_reason_for_content` from `.claude/hooks/bridge-compliance-gate.py` couples the helper to the hook's internal API. Mitigation: prefer the gate's `--audit-only` subprocess mode (a stable CLI surface) over the private import where practical; tests pin the chosen entry point. If the gate's content-validation API is not import-stable, the helper invokes the gate as a subprocess.
- Risk: harness detection misidentifies the active harness, applying the wrong path. Mitigation: an explicit `--harness {claude,codex}` flag overrides auto-detection; the Claude path's safety does not depend on detection (the agent issues the Write either way); the Codex path's inline compliance check is strictly additive and never weakens safety if applied under Claude.
- Risk: Codex adapter drift if regeneration is skipped. Mitigation: IP-5 makes regeneration explicit; `--check` is an acceptance criterion; the stale-adapter regression test asserts the canonical edit cannot silently leave the adapter stale.
- Rollback: revert the composer functions and the Codex-path entry point in `write_bridge.py`; revert the SKILL.md documentation; regenerate the Codex adapter to the prior state; remove the new tests. The existing `write_bridge.py` behavior is preserved as the fallback. Fully reversible.

## Recommended Commit Type

`feat:` — adds the composer functions, the Codex-path inline-compliance write entry point, the harness-explicit SKILL.md documentation, the regenerated Codex adapter, and spec-derived tests. New non-bypass capability surface; ~120 LOC of helper changes + tests.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-propose-helper-non-bypass-redesign`

```text
## Applicability Preflight

- packet_hash: `sha256:2b229483cedc85ba26a5960579f77ff3c6623594bd50604cd8090d6933e2d612`
- bridge_document_name: `gtkb-bridge-propose-helper-non-bypass-redesign`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-propose-helper-non-bypass-redesign-003.md`
- operative_file: `bridge/gtkb-bridge-propose-helper-non-bypass-redesign-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:verified, content:retired |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

Result: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. The three advisory specs the `-002` preflight flagged uncited are now cited.

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-propose-helper-non-bypass-redesign`

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-propose-helper-non-bypass-redesign`
- Operative file: `bridge\gtkb-bridge-propose-helper-non-bypass-redesign-003.md`
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
```

Result: exit 0; 5/5 `must_apply` clauses with evidence; 0 blocking gaps.

## Review Questions for Loyal Opposition

1. The Codex-disposition choice: `-003` makes the helper run the bridge-compliance validation inline on the Codex path (giving Codex a concrete non-bypass path now), rather than scoping Codex out until an `apply_patch` bridge-compliance gate is registered. Is the inline-validation approach acceptable, or does Loyal Opposition prefer scoping Codex out (with the noted caveat that scoping the helper out does not prevent a Codex `apply_patch` bridge-file write)?
2. Should the Codex-path inline compliance reuse the gate via the private `_deny_reason_for_content` import or via the `--audit-only` subprocess CLI? `-003` prefers the subprocess CLI as the more stable surface; guidance is welcome.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
