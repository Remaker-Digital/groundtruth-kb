NEW

# Implementation Proposal - /verify Verdict-Author Skill Slice 1 (skill scaffolding + spec-to-test mapping)

bridge_kind: implementation_proposal
Document: gtkb-verify-verdict-author-skill-slice-1
Version: 001
Author: Prime Builder (Claude, harness B)
Date: 2026-05-14 UTC
Session: S350
Source: WI-3261 (Verification mechanics: /verify verdict-author skill + spec-to-test mapping helper)
Recommended commit type: feat
target_paths: [".claude/skills/verify/SKILL.md", ".codex/skills/verify/SKILL.md", ".codex/skills/MANIFEST.json", "config/agent-control/harness-capability-registry.toml", "platform_tests/skills/test_verify_skill_scaffolding.py"]

## Summary

Implement WI-3261 Slice 1 by adding a canonical `/verify` skill at `.claude/skills/verify/SKILL.md` (Claude Code canonical) with a generated Codex adapter at `.codex/skills/verify/SKILL.md`. The skill scaffolds the structural conventions for Loyal Opposition's post-implementation `VERIFIED`/`NO-GO` verdict files: header metadata, prior-deliberation search guidance, applicability + clause preflight invocation conventions, the spec-to-test mapping table, positive confirmations, finding structure, revision-required guidance for `NO-GO`, executed commands block, and owner-action-required footer.

The skill is documentation + procedural orchestration only. It does NOT itself execute the preflights, does NOT bypass the bridge protocol, and does NOT mutate `bridge/INDEX.md`. The eventual verdict file is written by Loyal Opposition through the normal bridge write channel (the existing helper-mediated path or direct `Write` of a completed verdict file at `bridge/<slug>-<next>.md` followed by INDEX update).

Slice 1 is intentionally minimal: skill scaffolding + adapter parity + tests. The companion spec-to-test mapping computation helper (reading `config/governance/spec-applicability.toml` + `config/governance/adr-dcl-clauses.toml` to suggest candidate test commands per cited spec) is deferred to Slice 2; this slice documents the structural conventions only.

## In-Root Placement Evidence

All target paths are in-root under `E:\GT-KB`. Bridge file at `E:\GT-KB\bridge\gtkb-verify-verdict-author-skill-slice-1-001.md`. Targets at `E:\GT-KB\.claude\skills\verify\SKILL.md`, `E:\GT-KB\.codex\skills\verify\SKILL.md`, `E:\GT-KB\.codex\skills\MANIFEST.json`, `E:\GT-KB\config\agent-control\harness-capability-registry.toml`, `E:\GT-KB\platform_tests\skills\test_verify_skill_scaffolding.py`. No `applications/` paths; no Agent Red paths.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority; the verdict file output produced by this skill flows through the canonical bridge channel.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every relevant governing specification.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the spec-to-test mapping section the skill scaffolds operationalizes this constraint for post-impl verdicts.
- `GOV-STANDING-BACKLOG-001` - implements MemBase backlog item WI-3261; one tracking item under `GTKB-DETERMINISTIC-SERVICES-001`.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all targets are in-root and not under `applications/`; the skill is platform infrastructure, not adopter-application code.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - mandates generated Codex adapter at `.codex/skills/verify/SKILL.md` via `scripts/generate_codex_skill_adapters.py`; adapter SHA contract honored.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the skill is itself an artifact governing future verdict-file artifacts.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - skill scaffolding makes verdict authoring an artifact-governed activity rather than session-local memory.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the skill is invoked when a post-implementation report (NEW status on a post-GO thread) enters Loyal Opposition's actionable queue.
- `GOV-ARTIFACT-APPROVAL-001` - no protected narrative artifact is mutated by this slice; the new skill file is project-local skill infrastructure and not a protected `.claude/rules/*.md`, `AGENTS.md`, `CLAUDE*.md`, or `memory/work_list.md` write.
- `.claude/rules/loyal-opposition.md` - canonical LO behavior the skill orchestrates without overriding.
- `.claude/rules/file-bridge-protocol.md` - "Mandatory Specification-Derived Verification Gate" is the contract whose ergonomics the skill improves.
- `.claude/rules/codex-review-gate.md` - "no implementation without GO" gate; the skill produces a verdict file that ITSELF flows through the same gate when LO writes it.
- `.claude/rules/project-root-boundary.md` - all target paths within `E:\GT-KB`.

## Prior Deliberations

- `DELIB-1866` - Loyal Opposition Response: GTKB-DB-BACKUP-001 - example of spec-derived verification framing in a recent verdict.
- `DELIB-1853` - LO Review: GTKB Spec Lifecycle Schema Migration - cites spec-to-test linkage scrutiny.
- `DELIB-1844` - LO Review: ADR-Evaluation Enforcement S0 Audit Script REVISED-2 - example of spec-derived verification rejection patterns the skill formalizes.
- `DELIB-1565` - bridge skill unification review context; precedent for canonical-skill + Codex-adapter parity (the same pattern `gtkb-bridge` uses).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - owner directive that repeated AI plumbing should become deterministic services; verdict-authoring scaffolding is in scope.
- `bridge/gtkb-bridge-impl-report-skill-001-001.md` and chain - sibling helper precedent in WI-3258 (implementation-report side) for WI-3261 (verdict side).
- `bridge/gtkb-bridge-revision-skill-001-009.md` - VERIFIED sibling helper pattern (`/bridge revise`).
- WI-3261 row in MemBase `current_work_items` - authoritative backlog item for this proposal.

No cited deliberation authorizes bypassing bridge review, specification linkage, credential scanning, implementation-start authorization, or the spec-derived verification gate.

## Owner Decisions / Input

Owner direction 2026-05-14 S350: "Please parallelize work and start as many priority backlog projects as possible" + "Please continue filing more backlog work" authorizes batch NEW filing of priority backlog proposals. Per-proposal Codex GO required before implementation. Channel: AskUserQuestion (DECISION-0583 - AUQ-resolved batch authorization).

No additional per-slice owner decision is required for this NEW filing. Implementation will not begin until Codex records `GO` and the implementation-start authorization packet is created from that verdict. No deployment, credential lifecycle action, production operation, Agent Red live artifact mutation, Git history rewrite, or formal GOV/SPEC/PB/ADR/DCL mutation is in scope for Slice 1.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal is NOT a bulk operation against the standing backlog or MemBase. It implements exactly one MemBase backlog item (WI-3261) by adding one new skill artifact pair (`.claude/skills/verify/SKILL.md` canonical + `.codex/skills/verify/SKILL.md` adapter) plus the manifest/registry/test entries required by the existing adapter-parity contract. No formal-artifact-approval packet is required because no protected narrative artifact (`.claude/rules/*.md`, `AGENTS.md`, `CLAUDE*.md`, `memory/work_list.md`) is mutated; the inventory for this slice is the IP-1 through IP-4 enumeration in `## Implementation Plan` below.

Tokens for clause-preflight evidence: `inventory` (the IP enumeration), `formal-artifact-approval` (none required; the skill file is project-local skill infrastructure, not a protected narrative artifact under `GOV-ARTIFACT-APPROVAL-001`'s narrative-artifact scope).

## Requirement Sufficiency

Existing requirements sufficient.

The governing backlog item (WI-3261), `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`, `GOV-FILE-BRIDGE-AUTHORITY-001`, `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`, the sibling helper precedent (`gtkb-bridge-impl-report-skill-001` chain), and the existing `gtkb-bridge` skill structure provide sufficient requirements for this implementation proposal. No new specification authoring or owner clarification is required before Slice 1 implementation.

## Implementation Plan

### IP-1: Author canonical `/verify` skill at `.claude/skills/verify/SKILL.md`

Create the canonical skill file with the following structural conventions:

1. **Frontmatter:**
   - `name: gtkb-verify`
   - `description:` one-paragraph summary that triggers the skill on "verify a post-implementation report", "author VERIFIED/NO-GO verdict", or "review impl report for spec-derived testing".
   - `allowed-tools: Read, Bash, Grep, Glob, Write` (Write for the final verdict file).

2. **Body sections:**
   - **Operation summary** - one paragraph framing: this skill helps Loyal Opposition author post-implementation verdicts that satisfy the Mandatory Specification-Derived Verification Gate.
   - **When to invoke** - bullet list: latest status on thread is NEW and the latest version is a post-implementation report (i.e., the GO already happened in an earlier version); user explicitly asks `/verify <slug>`; bridge scan surfaces the thread as actionable for Loyal Opposition.
   - **Mandatory pre-write steps** - numbered list:
     1. Read the full thread version chain (all prior `bridge/<slug>-NNN.md`).
     2. Confirm latest status is NEW on a post-GO thread.
     3. Run `python scripts/bridge_applicability_preflight.py --bridge-id <slug>` and capture output.
     4. Run `python scripts/adr_dcl_clause_preflight.py --bridge-id <slug>` (no `--report-only`).
     5. Run a deliberation search per `.claude/rules/deliberation-protocol.md`.
     6. Identify the linked specifications carried forward from the GO'd proposal.
     7. Build the spec-to-test mapping table (Slice 1: manual; Slice 2 will compute candidates).
     8. Execute the spec-derived tests and capture exact commands + observed results.
   - **Verdict file template** - the structural conventions for `bridge/<slug>-<next>.md`:
     - Line 1: verdict word (`VERIFIED` or `NO-GO`) on its own line.
     - Header block: `bridge_kind: verification_verdict`, `Document:`, `Version:`, `Author:`, `Date:`, `Reviewer:`, `Responds to:` (the post-impl report version), `Recommended commit type:` (only for `VERIFIED`).
     - `## Applicability Preflight` - verbatim output from the applicability preflight tool.
     - `## Clause Applicability` - verbatim output from the clause preflight tool (`## Blocking Gaps` subsection if exit 5).
     - `## Prior Deliberations` - DELIB citations.
     - `## Specifications Carried Forward` - list mirroring the proposal's Specification Links.
     - `## Spec-to-Test Mapping` - table: `| Specification | Test or Verification Command | Executed | Result |`.
     - `## Positive Confirmations` - bullet list of what passed.
     - `## Findings` (for `NO-GO`) - structured per `.claude/rules/report-depth.md` and `.claude/rules/report-depth-prime-builder-context.md`.
     - `## Required Revisions` (for `NO-GO`) - finding-by-finding required changes.
     - `## Commands Executed` - exact shell commands run during review with observed output excerpts.
     - `## Owner Action Required` (optional) - any owner decision the verdict surfaces.
   - **Gate enforcement** - explicit reminders:
     - VERIFIED requires every linked spec to have at least one executed test row with `Executed: yes`.
     - Untested linked specifications require explicit owner waiver lines.
     - Clause preflight exit 5 with no owner-waiver line = NO-GO.
     - Missing required cross-cutting specs = NO-GO until proposal/report is revised.
   - **Non-bypass guarantees** - the skill does NOT itself execute the preflights or tests (the reviewer runs them); it does NOT write `bridge/INDEX.md` (the reviewer/helper does); it does NOT short-circuit Loyal Opposition's judgment.
   - **Cross-harness implementation notes** - body identical between Claude Code and Codex via adapter pipeline; adapter at `.codex/skills/verify/SKILL.md` carries the `<!-- GTKB-CODEX-SKILL-ADAPTER -->` marker; do NOT edit the adapter directly.
   - **Companion skills** - link to `gtkb-bridge`, `gtkb-proposal-review`, `gtkb-send-review`.
   - Copyright footer.

### IP-2: Generate Codex adapter at `.codex/skills/verify/SKILL.md`

Run `python scripts/generate_codex_skill_adapters.py` to generate the adapter from the canonical. The adapter body must be byte-identical to the canonical body modulo the generated-block per `feedback_codex_adapter_sha_is_script_normalized_body.md` discipline; SHA stored in MANIFEST is `sha256(_strip_generated_block(text).rstrip() + "\n")`.

### IP-3: Register the skill in `config/agent-control/harness-capability-registry.toml`

Add a registry entry for `gtkb-verify`:
- skill name, canonical path, codex adapter path, role-applicability (`loyal-opposition`).

Add the skill entry to `.codex/skills/MANIFEST.json` with the computed normalized-body SHA.

### IP-4: Tests at `platform_tests/skills/test_verify_skill_scaffolding.py`

10-15 deterministic tests (see `## Test Mapping` below). No network, no external commands; pure file-content + manifest-parity assertions.

## Test Mapping

| # | Test name | Verifies | Linked specification |
|---|---|---|---|
| 1 | `test_canonical_skill_file_exists` | `.claude/skills/verify/SKILL.md` exists and is in-root | `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, `.claude/rules/project-root-boundary.md` |
| 2 | `test_canonical_skill_frontmatter_present` | YAML frontmatter parses; `name: gtkb-verify`; `description` non-empty | skill discovery; trigger semantics |
| 3 | `test_canonical_skill_required_sections` | Body contains all required H2 sections (Operation summary, When to invoke, Mandatory pre-write steps, Verdict file template, Gate enforcement, Non-bypass guarantees, Cross-harness implementation notes, Companion skills) | structural completeness |
| 4 | `test_verdict_template_includes_spec_to_test_table` | Verdict template documents the `Spec-to-Test Mapping` table with the four required columns | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` |
| 5 | `test_verdict_template_includes_applicability_preflight_section` | Verdict template documents `Applicability Preflight` section verbatim-output convention | `.claude/rules/file-bridge-protocol.md` Mandatory Applicability Preflight Gate |
| 6 | `test_verdict_template_includes_clause_applicability_section` | Verdict template documents `Clause Applicability` section + `Blocking Gaps` subsection convention | `.claude/rules/file-bridge-protocol.md` Clause-Test Preflight |
| 7 | `test_skill_documents_no_index_mutation` | Body explicitly states the skill does NOT mutate `bridge/INDEX.md` | non-bypass guarantee; `GOV-FILE-BRIDGE-AUTHORITY-001` |
| 8 | `test_skill_documents_preflight_invocations` | Body cites exact `bridge_applicability_preflight.py` and `adr_dcl_clause_preflight.py` invocations | `.claude/rules/file-bridge-protocol.md` |
| 9 | `test_codex_adapter_file_exists` | `.codex/skills/verify/SKILL.md` exists | `ADR-CODEX-HOOK-PARITY-FALLBACK-001` |
| 10 | `test_codex_adapter_body_matches_canonical_normalized_sha` | adapter normalized-body SHA matches canonical normalized-body SHA (per `_strip_generated_block` contract) | `ADR-CODEX-HOOK-PARITY-FALLBACK-001` adapter SHA contract |
| 11 | `test_codex_adapter_has_generated_marker` | adapter contains `<!-- GTKB-CODEX-SKILL-ADAPTER -->` marker | adapter parity discipline |
| 12 | `test_manifest_entry_present` | `.codex/skills/MANIFEST.json` includes the `gtkb-verify` entry with stored SHA | manifest parity |
| 13 | `test_registry_entry_present` | `config/agent-control/harness-capability-registry.toml` includes a `[[skills]]` (or equivalent) entry naming `gtkb-verify` with role-applicability `loyal-opposition` | registry parity |
| 14 | `test_skill_documents_NO_GO_findings_structure` | Body cites `.claude/rules/report-depth.md` for finding structure | `.claude/rules/loyal-opposition.md` |
| 15 | `test_target_paths_all_within_gtkb_root` | All declared target paths in the test fixture resolve under `E:\GT-KB` | `.claude/rules/project-root-boundary.md` |

## Risk and Rollback

**Risk:** Adopters mistakenly invoke `/verify` expecting it to execute preflights/tests for them and miss running them. **Mitigation:** explicit "Non-bypass guarantees" + "Mandatory pre-write steps" sections; skill description states it scaffolds verdict authoring, not preflight execution.

**Risk:** Adapter drift if canonical is edited without regeneration. **Mitigation:** existing adapter-SHA test pipeline + Test #10 enforces normalized-body parity; CI surfaces drift.

**Risk:** Slice-1 scaffolding documents a structural convention that future verdicts won't actually adopt. **Mitigation:** Test #4-8 lock the structural conventions; Slice 2 will additionally provide a computed spec-to-test candidate helper that produces tabular output matching the documented columns.

**Rollback:** Delete the four new files (skill canonical, adapter, test file, test entry in manifest) and revert registry TOML entry. No MemBase state mutated; no INDEX.md state mutated.

## Acceptance Criteria

1. `.claude/skills/verify/SKILL.md` exists and renders the structural conventions defined in IP-1.
2. `.codex/skills/verify/SKILL.md` exists, carries the generated-marker, and its normalized-body SHA equals the canonical's.
3. `.codex/skills/MANIFEST.json` and `config/agent-control/harness-capability-registry.toml` include the new skill entry.
4. All tests in `platform_tests/skills/test_verify_skill_scaffolding.py` pass.
5. Applicability preflight and clause preflight on this proposal pass at file time and at any subsequent revision time.
6. No `bridge/INDEX.md` mutation by the skill itself; no preflight or test execution by the skill itself.

## Verification Plan

Map per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

| Linked specification | Verification step |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Tests #7 (no INDEX mutation), #8 (documents preflight invocations); manual inspection that skill produces a verdict file consumed by the existing bridge channel. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | The applicability preflight on this proposal must pass; checked at file time and at any REVISED. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Tests #4 (spec-to-test table documented), #14 (NO-GO findings structure documented); this proposal's own Verification Plan exhibits the pattern. |
| `GOV-STANDING-BACKLOG-001` | One tracking work item (WI-3261); no bulk mutation; Clause Scope Clarification section documents non-bulk evidence. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Tests #1 and #15 (all targets within `E:\GT-KB`, not under `applications/`). |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Tests #9, #10, #11 (adapter exists, normalized SHA parity, generated marker). |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | Skill is itself an artifact; Test #1 verifies its presence; Test #3 verifies its structural completeness. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Manifest + registry entries (Tests #12, #13) make the skill governed infrastructure. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | "When to invoke" section of the skill documents the lifecycle trigger (post-impl report enters LO actionable queue). |
| `GOV-ARTIFACT-APPROVAL-001` | No protected narrative artifact mutated; no formal-artifact-approval packet required (documented in Clause Scope Clarification). |

Execution commands:

```
pytest platform_tests/skills/test_verify_skill_scaffolding.py -v
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-verify-verdict-author-skill-slice-1
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-verify-verdict-author-skill-slice-1
python scripts/generate_codex_skill_adapters.py --check
```

## Applicability Preflight

(To be embedded verbatim from `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-verify-verdict-author-skill-slice-1 --content-file <this file>` after INDEX entry exists; pre-filing the operative file uses `--content-file` mode per the catch-22 note in `.claude/rules/file-bridge-protocol.md`. Expected result: `preflight_passed: true`, `missing_required_specs: []`, `missing_advisory_specs: []`.)

End of proposal.
