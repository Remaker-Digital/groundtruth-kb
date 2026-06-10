REVISED

# Implementation Proposal - bridge-skill Protected-File Write Helper (WI-3281)

bridge_kind: prime_proposal
Document: gtkb-bridge-skill-protected-write-helper
Version: 003
Author: Prime Builder (Claude, harness B)
Date: 2026-05-15 UTC
Session: S353+

Project Authorization: PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BATCH
Project: PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS
Work Item: WI-3281

target_paths: [".claude/skills/bridge/helpers/protected_write.py", ".claude/skills/bridge/SKILL.md", ".codex/skills/bridge/SKILL.md", "platform_tests/skills/test_protected_write_helper.py"]

This REVISED proposal adds a bridge-skill helper that prepares and validates a narrative-artifact approval packet, writes the protected file with explicit LF semantics, then runs the universal-floor evidence checker (`scripts/check_narrative_artifact_evidence.py`) against the written path so the author has a deterministic, audited protected-write path that does not depend on PreToolUse interception.

## Revision Notes

This `-003` revises `-001` (NEW) to address every finding in the `-002` NO-GO. Each finding is mapped to its remedy:

- **F1 (P1) — `Path.write_text` does not trigger the narrative-artifact PreToolUse gate.** The `-001` design claimed the helper would write "through a Python subprocess that the PreToolUse hook intercepts cleanly." That claim was false: a Python helper invoked from a Bash command line is a Bash tool call from the harness perspective, not a `Write`/`Edit` tool call, so `.claude/hooks/narrative-artifact-approval-gate.py` (which exits unless `tool_name` is `Write` or `Edit`, lines 232-233) never inspects the write. `-003` adopts the NO-GO's acceptable revision path (1): the helper is a **deterministic protected-writer** that (a) validates the narrative approval packet, (b) writes the target with explicit LF normalization and the same `sha256(UTF-8)` content discipline the evidence checker expects, then (c) runs `scripts/check_narrative_artifact_evidence.py --paths <target>` and fails non-zero if the universal-floor evidence checker reports a finding. The helper is documented as a **universal-floor evidence path**, NOT as a PreToolUse interception. No claim of hook interception remains anywhere in this proposal. See revised IP-1 and the Enforcement Model section below.
- **F1 (P1) — tests must exercise the actual boundary.** The `-001` test `test_helper_env_var_propagates` is removed. `-003` IP-3 tests exercise the real boundary: they invoke `scripts/check_narrative_artifact_evidence.py` via its `evaluate(...)` entry point (and the helper end to end) and assert pass/fail against real packet + staged-content fixtures. No test asserts that a PreToolUse hook fired.
- **F2 (P2) — skill adapter parity outside authorized scope.** The `-001` `target_paths` updated only `.claude/skills/bridge/SKILL.md`. `-003` adds `.codex/skills/bridge/SKILL.md` to `target_paths` and adds adapter regeneration + the `--check` parity gate to the verification plan (IP-4). The bridge skill is an explicitly cross-harness surface; the canonical SKILL.md edit is followed by `python scripts/generate_codex_skill_adapters.py --update-registry`, and `--check` is asserted clean.
- Mandatory preflights were re-run on this `-003` content; outputs are embedded in the Applicability Preflight and Clause Applicability sections below. The three advisory specs the `-002` preflight flagged uncited (`ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`) are now cited in Specification Links.

No new scope is introduced beyond the F2-required adapter file and the corrected test lane; the WI-3281 intent (reduce blocked-Write friction for narrative-artifact authoring) is unchanged.

## Claim

Helper invocation: `python .claude/skills/bridge/helpers/protected_write.py --target <path> --content-file <path> --packet <packet-path>`. The helper validates the approval packet against the proposed content's sha256, writes the content to the target with LF normalization, then runs `scripts/check_narrative_artifact_evidence.py --paths <target>` to confirm the universal-floor evidence gate would clear the write. The helper exits non-zero (and reports the cited rule) when packet validation fails or the evidence checker reports a finding. The helper is a deterministic universal-floor evidence path; it makes no claim of harness PreToolUse interception.

## Enforcement Model (corrects -001 F1)

The narrative-artifact approval discipline has two layers, both anchored on `config/governance/narrative-artifact-approval.toml` as the single source of truth for protected-path matching:

1. **Layer A — Claude PreToolUse `Write|Edit` UX** (`.claude/hooks/narrative-artifact-approval-gate.py`). This is a best-effort, harness-specific real-time check. It fires ONLY for actual `Write`/`Edit` harness tool calls. It does NOT fire for a Bash-invoked Python script.
2. **Layer C — universal harness-agnostic floor** (`scripts/check_narrative_artifact_evidence.py`, run from `.githooks/pre-commit`). This hard-blocks the commit regardless of which harness produced the staged change.

This proposal's helper operates against **Layer C**. It does not, and cannot, drive Layer A. The helper validates the packet and runs the Layer-C evidence checker against the freshly-written file so the author gets the Layer-C verdict immediately at write time rather than discovering a failure at commit time. The proposal explicitly does NOT claim the helper causes any PreToolUse hook to fire.

The Layer-C evidence checker's `evaluate(...)` entry point checks staged blobs; the helper additionally supports a `--paths` invocation that the checker already exposes for explicit (non-staged) path checks (`scripts/check_narrative_artifact_evidence.py:31`, `--paths` argument; `evaluate(root, paths=[...])`). Where the helper needs to verify content that is written-but-not-yet-staged, it stages the target (or computes the equivalent blob hash) before invoking the checker so the checker's staged-blob lookup resolves; the helper documents this staging step explicitly. The helper never bypasses the checker.

## In-Root Placement Evidence

All target paths in-root under `E:\GT-KB`. `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` satisfied. No path resolves outside `E:\GT-KB`.

## Specification Links

- `GOV-ARTIFACT-APPROVAL-001` - helper preserves the formal/narrative-artifact approval evidence contract; the helper's purpose is to make that contract easier to satisfy, never to weaken it.
- `DCL-ARTIFACT-APPROVAL-HOOK-001` - the approval-hook design constraint; the helper validates a narrative approval packet of the schema this DCL governs.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; the bridge skill is the surface this helper extends and this proposal is a bridge artifact.
- `SPEC-AUQ-POLICY-ENGINE-001` - deterministic policy-engine surface; the narrative-artifact gate participates in the AUQ policy engine and the helper threads its packet evidence.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement; all target paths are in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - cross-cutting constraint requiring this proposal to cite every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - cross-cutting constraint requiring the VERIFIED step to rest on executed spec-derived tests; the Specification-Derived Verification Plan maps each linked spec to a test.
- `GOV-STANDING-BACKLOG-001` - WI-3281 is a tracked backlog work item; this is a single-WI implementation, not a bulk backlog operation.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Claude/Codex parity; the bridge skill is a cross-harness surface and the canonical SKILL.md edit must be regenerated to the Codex adapter.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable artifact-graph model; the WI, bridge thread, helper, and tests form the artifact graph for this work.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - artifact lifecycle trigger discipline; WI-3281 triggers this implementation proposal which triggers its spec-derived tests.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - artifact-oriented governance baseline; this fix is captured as governed work (WI-3281) with a bridge artifact and spec-derived tests.

## Prior Deliberations

- `DELIB-1901` - records the verified narrative-artifact approval extension, including the current two-layer design (Claude PreToolUse `Write|Edit` UX layer plus the universal pre-commit evidence floor). This is the deliberation the `-002` NO-GO cited to establish the correct enforcement model; `-003` aligns the helper with the Layer-C universal floor described there.
- `DELIB-0835` - the owner decision requiring full native-format artifact presentation and approval evidence; the helper's packet-validation step exists to make that evidence reliably attached to a protected write.
- `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS` - batch-4 owner authorization; authorizes `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS` and includes WI-3281.

## Owner Decisions / Input

This proposal depends on owner approval and is authorized by the following owner decision:

- 2026-05-14 UTC, S350+: owner approved the `GTKB-APPROVAL-PACKET-ERGONOMICS` project authorization (`PAUTH-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-APPROVAL-PACKET-ERGONOMICS-BATCH`), whose `included_work_item_ids` include `WI-3281`. The authorization is live and active in MemBase (`current_project_authorizations`), with `allowed_mutation_classes` `["hook_upgrade", "cli_extension", "test_addition", "spec_status_promotion"]`. WI-3281 is an active member of `PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS` (membership `PWM-PROJECT-GTKB-APPROVAL-PACKET-ERGONOMICS-WI-3281`).
- Owner-decision evidence: `DELIB-S350-BATCH4-FOUR-PROJECT-AUTHORIZATIONS`. Formal-artifact-approval packet `.groundtruth/formal-artifact-approvals/2026-05-14-batch4-four-project-authorizations.json`.

No new owner decision is required for this `-003` revision; the revision corrects design and verification errors within the already-authorized WI-3281 scope.

## Requirement Sufficiency

Existing requirements sufficient. WI-3281's description specifies the helper need (reduce recurring blocked-Write friction for narrative-artifact authoring). `GOV-ARTIFACT-APPROVAL-001` and `DCL-ARTIFACT-APPROVAL-HOOK-001` already specify the narrative-artifact approval evidence contract the helper preserves. No new or revised requirement or specification is created by this work. The helper introduces only an internal author-convenience surface; it changes neither the approval contract nor the protected-path set.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is a single-WI implementation. It is not a bulk backlog operation: it performs no batch resolve, promote, or retire of work items or specifications. References to "work item", "backlog", and "standing backlog" describe the single work item WI-3281 and its governed filing path only. The applicable evidence pattern is a single-WI implementation proposal with formal-artifact-approval discipline preserved unchanged. The review-packet inventory is one bridge thread: IP-1 (helper) + IP-2 (canonical SKILL.md) + IP-3 (tests) + IP-4 (Codex adapter parity). No formal artifact (GOV/ADR/DCL/SPEC) is created or mutated.

## Bridge INDEX Maintenance

`bridge/INDEX.md` is the canonical bridge workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`. This `-003` REVISED file is recorded by inserting a `REVISED: bridge/gtkb-bridge-skill-protected-write-helper-003.md` line at the top of the existing `Document: gtkb-bridge-skill-protected-write-helper` entry, above the `-002` NO-GO and `-001` NEW lines. The append-only version chain (`-001` NEW, `-002` NO-GO, `-003` REVISED) is preserved; no prior file or INDEX line is deleted or rewritten.

## Proposed Scope

### IP-1: Helper module (redesigned per -002 F1)

`.claude/skills/bridge/helpers/protected_write.py`:

1. Parse args: `--target` (protected path, relative to project root), `--content-file` (or `--content-stdin`), `--packet` (path to the narrative approval packet JSON).
2. Read the proposed content and compute `sha256(content_utf8)`.
3. Validate the narrative approval packet: confirm it is valid JSON, `artifact_type == "narrative_artifact"`, all required fields present per `config/governance/narrative-artifact-approval.toml` `[approval_packet].required_fields`, `target_path` matches `--target`, and `full_content_sha256` matches the proposed content's sha256. On any failure, exit non-zero and print the failing condition with the cited rule (`GOV-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001`). Reuse the validation logic of `scripts/check_narrative_artifact_evidence.py` where practical (import its `_validate_packet` / `_find_matching_packet` helpers rather than duplicating the schema), so the helper and the universal floor cannot drift.
4. Confirm the target path matches a protected narrative-artifact pattern (per the config); if it does not, exit non-zero (the helper is for protected files only — an unprotected path needs no packet and should use an ordinary Write).
5. Write the content to the target via `Path.write_text` with LF normalization (`newline="\n"`, content `\r\n`/`\r` collapsed to `\n`), matching the byte discipline the evidence checker's `sha256(UTF-8)` comparison expects.
6. Run `scripts/check_narrative_artifact_evidence.py` against the written target (via subprocess `--paths <target>`, or by importing and calling its `evaluate(root, paths=[target])` entry point). If the checker reports `status == "fail"`, exit non-zero and surface the checker's findings verbatim. The checker is the authority; the helper never overrides a checker finding.
7. Exit 0 only when packet validation passes AND the evidence checker clears the written path.

The helper explicitly does NOT claim to drive the Claude PreToolUse hook. Its docstring states it is a Layer-C universal-floor evidence path.

### IP-2: Canonical SKILL.md update

In `.claude/skills/bridge/SKILL.md`, add a "Protected-file Writes" subsection documenting the helper. The documentation states plainly: the helper is a deterministic universal-floor evidence path (Layer C), NOT a PreToolUse interception; for protected narrative-artifact files the author may use the helper to get the Layer-C verdict at write time; the helper's clean exit means the same evidence checker that runs at `.githooks/pre-commit` would also clear the staged file.

### IP-3: Tests (redesigned per -002 F1 — exercise the real boundary)

`platform_tests/skills/test_protected_write_helper.py` (new file; same lane as the sibling bridge-skill helper tests `test_bridge_revise_helper.py`, `test_bridge_impl_report_helper.py`):

Test fixtures: a sample narrative-artifact target path (matching a protected pattern from `config/governance/narrative-artifact-approval.toml`) plus matching and mismatching narrative approval packets. Tests:

- Success path: valid packet whose `full_content_sha256` matches the content; helper writes the file and the universal-floor evidence checker clears it; helper exits 0.
- Hash mismatch fails: packet `full_content_sha256` does not match the content; helper exits non-zero before writing or rejects at the checker step; no false success.
- Invalid packet fails: missing required field / wrong `artifact_type`; helper exits non-zero with the cited rule.
- Unprotected target rejected: a path that matches no protected pattern is rejected (helper is protected-path-only).
- LF normalization: content authored with `\r\n` is written as `\n` and the resulting blob sha256 matches the packet's `full_content_sha256`.
- Evidence-checker integration: a deliberately evidence-deficient write (e.g., no packet on disk in the packets directory) makes `scripts/check_narrative_artifact_evidence.py` report a finding, and the helper surfaces that finding and exits non-zero. This test feeds real paths into the checker's `evaluate(...)` entry point — it is the boundary assertion required by `-002` F1.

No test asserts that a PreToolUse hook fired. The boundary under test is the universal-floor evidence checker (`scripts/check_narrative_artifact_evidence.py`) and the helper end to end.

### IP-4: Codex skill-adapter parity (added per -002 F2)

After the canonical `.claude/skills/bridge/SKILL.md` edit, regenerate the Codex adapter: `python scripts/generate_codex_skill_adapters.py --update-registry`. The Codex adapter at `.codex/skills/bridge/SKILL.md` carries a `<!-- GTKB-CODEX-SKILL-ADAPTER -->` marker and is never edited directly; it is regenerated from canonical. The adapter file is listed in `target_paths` because the regeneration writes it. The `skill.bridge` capability is registered in `config/agent-control/harness-capability-registry.toml` with `[capabilities.codex] surface = ".codex/skills/bridge/SKILL.md"`, `status = "adapter"`. Verification asserts `python scripts/generate_codex_skill_adapters.py --check` reports no drift after regeneration.

## Specification-Derived Verification Plan

Each linked specification maps to at least one executed test or verification command. Tests are added or updated within the `target_paths` test file.

| Linked specification | Verification |
|---|---|
| `GOV-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` | `test_helper_writes_with_valid_packet`, `test_helper_rejects_invalid_packet`, `test_helper_rejects_hash_mismatch` — helper validates the narrative approval packet against the content before writing. |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` (universal floor) | `test_helper_surfaces_evidence_checker_finding` — helper runs `scripts/check_narrative_artifact_evidence.py` against the written path and fails on a checker finding (the real-boundary assertion per -002 F1). |
| `GOV-ARTIFACT-APPROVAL-001` (protected-path scope) | `test_helper_rejects_unprotected_target` — helper is protected-path-only. |
| `DCL-ARTIFACT-APPROVAL-HOOK-001` (byte discipline) | `test_helper_lf_normalizes_content` — LF normalization keeps the blob sha256 equal to the packet hash. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `python scripts/generate_codex_skill_adapters.py --check` reports no drift after canonical SKILL.md edit + regeneration. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | the SKILL.md "Protected-file Writes" subsection documents the helper for the bridge skill surface; presence asserted by `test_skill_md_references_helper`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`, `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | satisfied structurally by this Specification-Derived Verification Plan and the embedded preflights. |
| `GOV-STANDING-BACKLOG-001`, `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | governance/framing specs; satisfied by the single-WI artifact-graph framing (WI-3281 -> bridge thread -> helper -> tests) and in-root placement; no separate runtime test. |

Verification commands:

```
python -m pytest platform_tests/skills/test_protected_write_helper.py -v
python scripts/generate_codex_skill_adapters.py --check
python -m ruff check .
python -m ruff format --check .
```

## Acceptance Criteria

1. IP-1 helper landed; the helper validates the narrative approval packet, writes with LF normalization, and runs `scripts/check_narrative_artifact_evidence.py` against the written path; it exits non-zero on packet-validation failure or any evidence-checker finding.
2. The helper's docstring and the SKILL.md documentation describe it as a Layer-C universal-floor evidence path; no text claims PreToolUse interception.
3. IP-3 tests land in `platform_tests/skills/test_protected_write_helper.py`; all tests pass; at least one test feeds real paths into the universal-floor evidence checker; no test asserts a PreToolUse hook fired.
4. IP-2 canonical SKILL.md updated; IP-4 Codex adapter `.codex/skills/bridge/SKILL.md` regenerated; `python scripts/generate_codex_skill_adapters.py --check` reports no drift.
5. `ruff check` and `ruff format --check` are clean.
6. Both bridge preflights pass on this proposal (embedded below).

## Files Expected To Change

- `.claude/skills/bridge/helpers/protected_write.py` — new deterministic protected-writer helper (Layer-C evidence path).
- `.claude/skills/bridge/SKILL.md` — canonical "Protected-file Writes" subsection documenting the helper.
- `.codex/skills/bridge/SKILL.md` — regenerated Codex adapter (written by `generate_codex_skill_adapters.py`; never hand-edited).
- `platform_tests/skills/test_protected_write_helper.py` — new spec-derived tests exercising the real evidence-checker boundary.

## Risks / Rollback

- Risk: the helper's `--paths` invocation of the evidence checker depends on the target being resolvable as a staged blob (the checker's `_staged_blob_sha256` reads `git show :<path>`). Mitigation: the helper stages the target before invoking the checker, or computes the equivalent blob hash and uses the checker's pure `evaluate(...)` path with explicit paths; the helper documents this step. Tests cover the staged and the explicit-paths cases.
- Risk: schema drift between the helper's packet validation and the universal floor. Mitigation: the helper imports `scripts/check_narrative_artifact_evidence.py` validation helpers rather than re-implementing the schema, so the two cannot diverge.
- Risk: Codex adapter drift if regeneration is skipped. Mitigation: IP-4 makes regeneration explicit and `--check` is an acceptance criterion.
- Rollback: remove `.claude/skills/bridge/helpers/protected_write.py` and `platform_tests/skills/test_protected_write_helper.py`; revert the SKILL.md subsection; regenerate the Codex adapter to drop the subsection. No production runtime path depends on the helper, so rollback is fully reversible.

## Recommended Commit Type

`feat:` — new skill helper plus its spec-derived tests and the regenerated Codex adapter. Net new author-convenience surface; ~110 LOC helper + tests.

## Applicability Preflight

Command: `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-skill-protected-write-helper`

```text
## Applicability Preflight

- packet_hash: `sha256:10e065bda2c1012b7f3d892a0b871bb6cda72ddedfdb82a0b25d2755e812cbde`
- bridge_document_name: `gtkb-bridge-skill-protected-write-helper`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-bridge-skill-protected-write-helper-003.md`
- operative_file: `bridge/gtkb-bridge-skill-protected-write-helper-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:deliberation, content:MemBase |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:Specification-Derived Verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |
```

Result: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`. The three advisory specs the `-002` preflight flagged uncited are now cited.

## Clause Applicability

Command: `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-skill-protected-write-helper`

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-skill-protected-write-helper`
- Operative file: `bridge\gtkb-bridge-skill-protected-write-helper-003.md`
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

1. Is importing `scripts/check_narrative_artifact_evidence.py`'s validation helpers into the skill helper (to prevent schema drift) acceptable, or should the helper shell out to the checker exclusively?
2. Is staging the target before the checker's staged-blob lookup the right approach, or is the pure `evaluate(root, paths=[...])` path preferred even though it still reads `git show :<path>` for blob bytes?

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
