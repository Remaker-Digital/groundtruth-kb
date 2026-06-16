REVISED

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: codex-bridge-index-retirement-cleanout-final-sweep-20260615
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Prime Builder

# Bridge Index Retirement Cleanout Proposal - Final Sweep Addendum

bridge_kind: prime_proposal
Document: gtkb-bridge-index-retirement-cleanout
Version: 005
Responds to: bridge/gtkb-bridge-index-retirement-cleanout-004.md
Author: Prime Builder (Codex, harness A)
Date: 2026-06-15 UTC

Project Authorization: PAUTH-PROJECT-GTKB-COST-AUTODISPATCH-WI-4578-DISPATCH-ORTHOGONALITY-CLI
Project: PROJECT-GTKB-TYPED-ARTIFACT-FLOW-ENGINE
Work Item: WI-4578

target_paths: ["groundtruth.db", "AGENTS.md", "CLAUDE.md", "README.md", "CONTRIBUTING.md", "CHANGELOG.md", ".agent/skills/**", ".api-harness/skills/**", ".claude/rules/**", ".claude/skills/**", ".claude/hooks/**", ".claude/settings.json", ".codex/skills/**", ".codex/hooks.json", "config/agent-control/**", "config/dispatcher/**", "config/governance/**", "config/registry/**", "docs/**", "applications/Agent_Red/docs/**", "scripts/**", "groundtruth-kb/docs/**", "groundtruth-kb/src/**", "groundtruth-kb/templates/**", "groundtruth-kb/tests/**", "platform_tests/**", "harness-state/harness-registry.json", "harness-state/harness-identities.json", "bridge/gtkb-bridge-index-retirement-cleanout-*.md", "bridge/gtkb-lo-review-dispatch-reliability-*.md", "bridge/INDEX.md"]

implementation_scope: final_inventory_addendum, source, config, cli, tests, skills, hooks, templates, protected_narrative, historical_classification, harness_dispatch_reliability
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Summary

This addendum records the final read-only search pass after `004`. It does not
change the proposed direction. It strengthens the conclusion that the
`bridge/INDEX.md` retirement is a no-backward-compatibility system cutover, not
a documentation cleanup.

The desired invariant remains:

- `bridge/INDEX.md` must not exist.
- No active helper, scaffold, doctor, hook, skill, CLI, prompt, or status surface
  may recreate it or require it.
- Historical references may remain only when clearly labeled as historical
  audit/import fixtures.

## Additional Sweep Evidence

Final read-only search patterns included:

```text
bridge/INDEX\.md|bridge\\INDEX\.md|INDEX\.md
generated compatibility|compatibility view|compatibility output|generated view|legacy compatibility|dual-write|dual write
sole authoritative|canonical.*index|index.*canonical|index_authority|index authority|live contents.*bridge
cli_bridge_index|bridge_index|index_mutation|INDEX_FILENAME|index_path|render.*index|scan.*index
```

The search excluded `bridge/**`, `archive/**`, `memory/**`,
`**/session-envelope-archive/**`, and drift backups. Generated docs build assets
also contain stale strings, but those should be handled as rebuild outputs after
their source documents are corrected, not as hand-edited source authority.

Newly emphasized active cleanup classes:

- `AGENTS.md` still tells Loyal Opposition startup to scan live
  `bridge/INDEX.md` and calls it the sole authoritative bridge state.
- `config/registry/sot-artifacts.toml` still records `bridge/INDEX.md` as a
  source-of-truth artifact path.
- `config/governance/adr-dcl-clauses.toml` still contains
  `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.
- `groundtruth-kb/src/groundtruth_kb/project/preflight.py` still scans
  `bridge/INDEX.md` for in-flight bridge awareness.
- `groundtruth-kb/src/groundtruth_kb/session/handoff.py` still parses
  `bridge/INDEX.md` and tells agents to read it.
- `groundtruth-kb/src/groundtruth_kb/project/scaffold.py` still generates an
  initial `bridge/INDEX.md` and inserts index-based startup language.
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` still treats missing or
  malformed `bridge/INDEX.md` as a bridge-health problem in multiple checks.
- Template hooks such as `bridge-compliance-gate.py`,
  `delib-search-gate.py`, `delib-search-tracker.py`, and
  `session-start-governance.py` still have index constants or index-derived
  active-bridge logic.
- Platform hook tests still construct or exempt `bridge/INDEX.md`, which means
  the cleanup needs explicit test rewrites rather than broad deletion.

## Code Quality Baseline

| Rule ID | Applies? | Compliance plan | Verification | Waiver / N/A reason |
|---|---|---|---|---|
| CQ-SECRETS-001 | Yes | Search and rewrite active bridge text without exposing credential-bearing files. | Credential scan and changed-file review. | |
| CQ-PATHS-001 | Yes | Keep cleanup inside `E:\GT-KB` and the target paths above. | Root-boundary review. | |
| CQ-COMPLEXITY-001 | Yes | Remove index-only code paths rather than adding compatibility shims. | Old-symbol search and source review. | |
| CQ-CONSTANTS-001 | Yes | Replace index constants with dispatcher/TAFE constants or remove them. | Ruff and targeted tests. | |
| CQ-SECURITY-001 | Yes | Keep production/cloud mutation oversight independent from bridge health. | Prompt/rule review. | |
| CQ-DOCS-001 | Yes | Rewrite active guidance to no-index dispatcher/TAFE operation. | `rg` search with historical-only allowlist. | |
| CQ-TESTS-001 | Yes | Update tests to prove no index creation and no index dependency. | Targeted pytest commands in `004`. | |
| CQ-LOGGING-001 | Yes | Health must report real work-delivery evidence, not just config presence. | Dispatch-health JSON assertions. | |
| CQ-VERIFICATION-001 | Yes | Treat every missing-index failure as a defect until explicitly classified historical. | Search, CLI, and pytest verification. | |

## Implementation Delta

`004` remains the controlling implementation plan. Add these details to the
first implementation slice:

1. Correct `AGENTS.md` and startup overlays before relying on fresh-session
   behavior from any harness.
2. Remove `bridge/INDEX.md` from source-of-truth registries.
3. Replace project preflight, session handoff, scaffold, and doctor checks with
   dispatcher/TAFE or versioned-file discovery.
4. Rewrite template hooks and golden tests so newly scaffolded projects do not
   recreate the retired index.
5. Rebuild or refresh generated docs assets only after source docs are fixed;
   do not preserve stale generated compatibility language as authority.

## LO Review Status

This revision still requires a trustworthy Loyal Opposition review. Current
evidence does not justify treating Ollama, OpenRouter, or Antigravity as fully
healthy LO reviewers for this cleanup yet. The companion proposal
`bridge/gtkb-lo-review-dispatch-reliability-001.md` remains necessary.

If cheap LO review cannot be made reliable quickly, file and review a temporary
topology change that allows headless Codex to act as Loyal Opposition for this
proposal class. Do not change harness routing as an unreviewed shortcut.

## Spec-Derived Verification Additions

Add these checks to the `004` verification plan:

```text
rg -n "bridge/INDEX[.]md|bridge\\INDEX[.]md|INDEX[.]md|compatibility view|compatibility output|INDEX_FILENAME|index_path" AGENTS.md config/registry config/governance groundtruth-kb/src/groundtruth_kb/project groundtruth-kb/src/groundtruth_kb/session groundtruth-kb/templates platform_tests --glob "!archive/**" --glob "!**/__pycache__/**"
```

Expected: no active references except historical/audit/import fixtures that are
explicitly labeled historical and cannot be used as live authority.

```text
python -m pytest groundtruth-kb/tests/test_doctor.py groundtruth-kb/tests/test_scaffold_smoke.py platform_tests/hooks/test_bridge_compliance_gate_body_status_token.py platform_tests/hooks/test_bridge_axis_2_surface_governance_review_terminal.py -q --tb=short
```

Expected: tests pass with no generated or required `bridge/INDEX.md`.
