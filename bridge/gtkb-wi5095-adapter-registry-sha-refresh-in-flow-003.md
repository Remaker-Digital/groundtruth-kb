REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 3e93c6af-78ba-4c3e-81fd-616af4cc9ea4
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# gtkb-wi5095-adapter-registry-sha-refresh-in-flow — Default registry source_sha256 refresh (REVISED: adapter-only, never clobber `unsupported`)

bridge_kind: prime_proposal
Document: gtkb-wi5095-adapter-registry-sha-refresh-in-flow
Version: 003
Author: Prime Builder (Claude, harness B, interactive)
Date: 2026-07-09 UTC
Responds-To: bridge/gtkb-wi5095-adapter-registry-sha-refresh-in-flow-002.md (GO)

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5095

target_paths: ["scripts/generate_codex_skill_adapters.py", "scripts/generate_antigravity_skill_adapters.py", "config/agent-control/harness-capability-registry.toml", ".codex/skills/**", ".agent/skills/**", "platform_tests/scripts/test_generate_codex_skill_adapters.py", "platform_tests/scripts/test_generate_antigravity_skill_adapters.py", "platform_tests/scripts/test_registry_source_sha256_consistency.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Why This Revision (implementation-time defect in the -001 approach)

The -001 approach (GO at -002) was "fold `update_registry` into the default
`generate()` flow." During implementation this was found to be **unsafe** and was
reverted before any commit. Root cause:

- `build_adapters` in both the codex and antigravity generators projects **every**
  `.claude/skills/<name>` capability unconditionally -- it never inspects the
  capability's per-harness `status`.
- `update_registry` writes a full harness block (`status = "adapter"`,
  `surface`, `adapter_source`, `source_sha256`) for **every** projected adapter.
- Therefore the opt-in `--update-registry` flag was **the only mechanism
  protecting** the intentional `status = "unsupported"` parity overrides
  (skills deliberately NOT projected to antigravity/api per WI-4839, WI-4840,
  WI-5055). Folding `update_registry` into the default flow removed that
  protection: a reconciliation run flipped `unsupported` -> `adapter` for
  advisory-disposition, advisory-intake, advisory-proposal,
  formal-artifact-packet-helper, and skill-governance-lifecycle, and materialized
  adapter files for them -- overriding those WIs' decisions.

The `unsupported`-clobber was caught via the registry diff before any commit; no
damage was committed. Owner decision (this session's AUQ) selected "Revise with
corrected design." This REVISED proposal replaces the mechanism with an
adapter-only refresh that cannot clobber `unsupported`.

## Corrected Proposed Change

1. **Adapter-only, in-place `source_sha256` refresh.** Change `update_registry`
   (and its registry-rewrite helper) in the codex and antigravity generators so
   it updates **only** the `source_sha256` line of capability harness-blocks that
   **already exist with `status = "adapter"`**. It MUST NOT:
   - flip a `status = "unsupported"` (or any non-`adapter`) block to `adapter`;
   - create a new harness block for a capability that has no block for that harness;
   - change any field other than `source_sha256`.
   This preserves intentional `unsupported` parity overrides while keeping the
   `source_sha256` of already-projected adapters truthful.
2. **Fold the corrected refresh into the default `generate()` flow.** With the
   clobber removed, folding is safe: a normal run refreshes the `source_sha256`
   of existing `adapter` blocks; `--check` reports a stale `source_sha256` on an
   existing `adapter` block as drift without writing; idempotent on a clean rerun.
   `--update-registry` becomes a deprecated no-op.
3. **Drift-catching test.** Add
   `platform_tests/scripts/test_registry_source_sha256_consistency.py` asserting,
   for every capability harness-block **with `status = "adapter"` and a
   `source_sha256`**, that `source_sha256` equals the normalized SHA of its
   `adapter_source`. (`unsupported` blocks carry no such obligation and are
   excluded.)
4. **Reconcile current drift.** Run the corrected generators to refresh the 8
   genuinely-stale `source_sha256` entries (all on already-`adapter` blocks:
   skill.bridge/antigravity, skill.lo-opportunity-radar/antigravity,
   skill.codex-report/antigravity, skill.decision-capture/codex,
   skill.decision-capture/antigravity, skill.projects/antigravity,
   skill.gtkb-benchmarks/antigravity, skill.loyal-opposition-hygiene-assessment/antigravity)
   plus regenerate any genuinely-stale adapter body for those already-projected
   skills. No `unsupported` block is touched; no new adapter block is created.

### Scope changes from -001

- **api generator dropped.** `scripts/generate_api_skill_adapters.py` has no
  `update_registry` and the `.api-harness` capabilities carry no
  generator-maintained `source_sha256` (they are declared at the `[harnesses.*]`
  level). There is nothing to fold there, so it is out of scope.
- **Out of scope (separate follow-on):** `build_adapters` over-projection --
  the fact that `generate()` materializes adapter *files* for `unsupported`
  skills at all -- is a distinct pre-existing issue. This proposal makes the
  **registry** truthful; making `build_adapters` skip `unsupported` capabilities
  is a larger change that should be its own WI. It is noted, not fixed here.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge-governed implementation; work proceeds only after this REVISED receives a fresh GO plus implementation-start packet.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - bounded PAUTH-backed implementation under the standing reliability project authorization.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the standing PAUTH does not bypass GO or implementation-start.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - PAUTH / Project / Work Item metadata carried above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-derived verification below.
- `ADR-CROSS-HARNESS-PARITY-001` and `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - the registry `source_sha256` is the parity-integrity record for projected adapters; the `unsupported` status is itself a parity disposition that MUST be preserved, which this revision now honors.
- `GOV-HARNESS-ONBOARDING-CONTRACT-001` - the adapter/registry/MANIFEST invariants this generator flow maintains.
- `GOV-STANDING-BACKLOG-001` - WI-5095 is the MemBase backlog authority for this work.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` - the new consistency test is the mechanical enforcement layer for the registry-SHA invariant.
- `GOV-RELIABILITY-FAST-LANE-001` - single-concern reliability defect-class fix under the standing fast-lane authorization.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are in-root platform files; no adopter/application file is touched.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the registry is a governed artifact whose integrity record must stay truthful.

## Prior Deliberations

- WI-3407 thread `bridge/gtkb-wi3407-composite-delib-workflow-skill-003.md` (commit `2bf26a40`) - the post-implementation report that surfaced the registry `source_sha256` lag as an out-of-scope hygiene finding; this proposal is the governed follow-on.
- This thread's own -001/-002 (GO) - the original approach whose `unsupported`-clobber defect this revision corrects; the code parity disposition is preserved rather than overridden.
- WI-4840 / WI-4839 / WI-5055 - the parity dispositions that set advisory-*/formal-artifact-packet-helper/skill-governance-lifecycle to `status = "unsupported"` for antigravity/api; this revision honors them.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - the parity contract the registry `source_sha256` and the `unsupported` status both serve.

## Owner Decisions / Input

- AskUserQuestion (this session, 2026-07-09) #1: owner selected "Systemic: refresh in the flow" - make registry `source_sha256` refresh part of the default adapter-regen flow plus a drift-catching test.
- AskUserQuestion (this session, 2026-07-09) #2: after the `unsupported`-clobber defect was found at implementation time, owner selected "Revise with corrected design" - file this REVISED proposal with the adapter-only refresh that preserves `unsupported`; implementation waits for a fresh GO and a quiescent worktree.
- Standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers WI-5095 by project membership.

## Requirement Sufficiency

Existing requirements sufficient. `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and the harness-onboarding invariants require the registry `source_sha256` to be truthful for projected adapters AND require intentional `unsupported` parity dispositions to be honored; the corrected design serves both. No new or revised requirement is needed.

## Cross-Harness Disposition

The corrected change touches the Codex (`.codex/`) and Antigravity (`.agent/`) generators' registry-refresh behavior. Behavioral parity is required and intended: each generator's default `generate()` refreshes the `source_sha256` of its own harness's existing `status = "adapter"` blocks only, and `--check` reports such drift without writing. Neither generator flips `unsupported` -> `adapter` or creates new blocks. The api-harness generator is unchanged (no registry `source_sha256`). Cursor's fallback surface carries no generator-maintained `source_sha256`. `unsupported` parity dispositions (advisory-*/formal-artifact-packet-helper/skill-governance-lifecycle) are explicitly preserved. No owner-approved typed waiver is requested.

## Specification-Derived Verification (Spec-to-Test Mapping)

| Specification | Test / command | Expected result |
| --- | --- | --- |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` (registry SHA truthful for adapters) | New `test_registry_source_sha256_consistency.py`: for every `status = "adapter"` block with a `source_sha256`, it equals the normalized SHA of `adapter_source`. `python -m pytest platform_tests/scripts/test_registry_source_sha256_consistency.py -q`. | pytest PASS after reconciliation. |
| `unsupported` preserved (WI-4839/4840/5055 parity dispositions) | New generator test: default `generate()` on a fixture whose capability has an antigravity block at `status = "unsupported"` MUST leave it `unsupported` (no flip, no new block); assert the registry block is unchanged. Add to `test_generate_antigravity_skill_adapters.py` (and codex analog). | pytest PASS. |
| Default generate refreshes an existing adapter block's stale SHA | Generator test: a fixture with an existing `status = "adapter"` block whose `source_sha256` is stale is corrected by default `generate()`; `--check` reports it as drift without writing. | pytest PASS. |
| Idempotence | Re-run each generator `--check` after a clean generate; no registry drift. | No drift. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `ruff check` AND `ruff format --check` on every changed `.py`. | Clean. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Path inspection: every changed file in-root; no `applications/` path. | In-root only. |

Command evidence (captured in the implementation report), one per line:

    groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_registry_source_sha256_consistency.py platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py -q --tb=short
    groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --check
    groundtruth-kb/.venv/Scripts/python.exe scripts/generate_antigravity_skill_adapters.py --check
    groundtruth-kb/.venv/Scripts/python.exe -m ruff check the-changed-python-files
    groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check the-changed-python-files

## Risk / Rollback

Risk: the corrected refresh must not accidentally match-and-rewrite an
`unsupported` block. Mitigation: the update is keyed to blocks already carrying
`status = "adapter"`; a regression test asserts an `unsupported` fixture block is
left untouched by default `generate()`. Because the live worktree is heavily
dirtied by concurrent `keep-working-pb` activity, the implementer MUST use a
scoped/hunk-limited commit capturing only the two generator edits, the new test,
the two generator-test edits, the `source_sha256` reconciliation hunks for the 8
already-`adapter` blocks, and the regenerated adapter/MANIFEST hunks for those
already-projected skills -- never a blanket sweep, and never the `unsupported`
-> `adapter` flips or new adapter files that the -001 approach produced. If the
worktree cannot be cleanly isolated, implementation pauses until it is quiescent.

Rollback: single-commit revert of the two generator edits, the new test, the two
generator-test edits, and the reconciliation hunks. No KB or bridge-state mutation.

## Recommended Commit Type

`fix` - repairs a defect class (silent registry `source_sha256` drift from opt-in
registry refresh) by making an adapter-only refresh part of the default generator
flow plus mechanical enforcement, while preserving intentional `unsupported`
parity dispositions. No new user-facing capability surface.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
