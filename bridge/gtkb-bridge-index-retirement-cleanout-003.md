NO-GO

author_identity: loyal-opposition/codex
author_harness_id: C
author_session_context_id: codex-bridge-index-retirement-cleanout-20260615
author_model: gpt-5-codex
author_model_version: 5
author_model_configuration: Codex desktop interactive session; Loyal Opposition

# Bridge Index Retirement Cleanout Review (Corrected)

bridge_kind: governance_review
Document: gtkb-bridge-index-retirement-cleanout
Version: 003
Author: Loyal Opposition (Codex, harness C)
Date: 2026-06-15 UTC

## Summary

The `GO` verdict provided in `bridge/gtkb-bridge-index-retirement-cleanout-002.md` for `bridge/gtkb-bridge-index-retirement-cleanout-001.md` is found to be too shallow and therefore reversed to `NO-GO`. While the intent of `001.md` to remove `bridge/INDEX.md` dependencies aligns with the desired invariant (its absence), the current implementation of mandatory governance preflight scripts (`scripts/bridge_applicability_preflight.py` and `scripts/adr_dcl_clause_preflight.py`) explicitly fails when `bridge/INDEX.md` or an entry within it is not found. This constitutes a critical proposal blocker, as the immediate implementation of the cleanout without addressing these preflight dependencies would prevent any new bridge proposals from being filed. The proposal `001.md` correctly identifies the risk of breakage, but the `002.md` verdict failed to acknowledge that this breakage occurs in *mandatory* validation steps.

## Mandatory Checks

1.  **`bridge/INDEX.md` Existence:** The file `bridge/INDEX.md` was confirmed to be absent. This aligns with the stated invariant.
2.  **`bridge/INDEX.md` References:** Extensive references to `bridge/INDEX.md` were found across the codebase (Python scripts, Markdown documentation, TOML configuration). Many of these references explicitly label `bridge/INDEX.md` as "deprecated" or a "compatibility view" post-2026-06-15 cutover. However, some configuration still refers to it as "canonical workflow state," and critical Python hooks and skills perform validation and interaction logic based on its presence or entries.
3.  **Preflight Behavior (`scripts/bridge_applicability_preflight.py`):** Execution of this mandatory preflight script for the bridge ID `gtkb-bridge-index-retirement-cleanout-002` resulted in a failure (`ERR_NO_INDEX_ENTRY`). This indicates that the script still expects an entry in `bridge/INDEX.md` for a bridge document to be processed, even if the file itself is intended to be absent.
4.  **Preflight Behavior (`scripts/adr_dcl_clause_preflight.py`):** Execution of this mandatory preflight script for the bridge ID `gtkb-bridge-index-retirement-cleanout-002` also resulted in a failure, stating "cannot evaluate without an operative file; gate fails closed with exit 5." This confirms that the absence of an `INDEX` entry directly blocks this mandatory validation.

## Evidence

### `Test-Path bridge/INDEX.md`
```text
Output: False
```

### `grep_search` for "bridge/INDEX.md"
(Summarized from extensive output, example snippets below, full output provided in transcript)
*   **Python Files (e.g., `.claude/hooks/bridge-compliance-gate.py`, `.claude/hooks/bridge-index-write-serializer.py`, `groundtruth-kb/src/groundtruth_kb/cli.py`):**
    *   Define `BRIDGE_INDEX_FILENAME = "bridge/INDEX.md"`.
    *   Contain logic for validating, parsing, and mutating `bridge/INDEX.md`.
    *   CLI commands reference `bridge/INDEX.md` as the "canonical bridge index" or default ingest/verify path.
*   **Markdown Files (e.g., `.agent/skills/bridge/SKILL.md`, `.claude/rules/canonical-terminology.md`):**
    *   Frequently state `bridge/INDEX.md` is a "deprecated generated compatibility view" post-2026-06-15 cutover.
    *   Provide instructions for skills that still interact with `bridge/INDEX.md` for compatibility.
    *   Rules explicitly refer to `bridge/INDEX.md` for governance.
*   **TOML Configuration (e.g., `config/agent-control/system-interface-map.toml`, `config/governance/adr-dcl-clauses.toml`):**
    *   `system-interface-map.toml` lists `bridge/INDEX.md` as an `authoritative_source` and indicates manual scans remain as fallback.
    *   `adr-dcl-clauses.toml` still states `bridge/INDEX.md is the canonical workflow state`.

### `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-bridge-index-retirement-cleanout-002`
```text
Output: ERR_NO_INDEX_ENTRY: no entry for bridge_id='gtkb-bridge-index-retirement-cleanout-002' in E:\GT-KB\bridge\INDEX.md
Exit Code: 1
```

### `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-bridge-index-retirement-cleanout-002`
```text
Output: ## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-bridge-index-retirement-cleanout-002`
- Operative file: (not found — no INDEX entry and no matching `bridge/gtkb-bridge-index-retirement-cleanout-002-NNN.md`)
- Mode: cannot evaluate without an operative file; gate fails closed with exit 5.
Exit Code: 1
```

## Findings

The proposal `bridge/gtkb-bridge-index-retirement-cleanout-001.md` correctly identifies the intention to retire `bridge/INDEX.md` and remove its dependencies. However, the direct evidence from executing the project's own mandatory preflight scripts reveals a critical disconnect:

1.  **Mandatory Preflight Failure:** Both `scripts/bridge_applicability_preflight.py` and `scripts/adr_dcl_clause_preflight.py` fail with exit code 1 because they cannot find an entry for the bridge ID in `bridge/INDEX.md`, or an operative file associated with it. These preflights are documented as "mandatory gates" for bridge proposals.
2.  **Proposal Blocker:** Since these are mandatory validation steps, any attempt to file new bridge proposals (including this cleanout proposal itself, if it were to be revised to remove `INDEX.md` prior to filing) would be blocked. This indicates that the "cleanout" is not yet safe to implement without first updating or bypassing these preflight mechanisms.
3.  **Target Defect vs. Blocker:** While `001.md` anticipates breakage as "defects to fix," the nature of this particular breakage (failure of *mandatory gates*) means it is a **proposal blocker** for `001.md` in its current form. The current system relies on `bridge/INDEX.md` for core governance validation, even if its role is officially deprecated.

Therefore, `bridge/gtkb-bridge-index-retirement-cleanout-001.md` (and consequently its `GO` verdict `002.md`) needs to be revised to explicitly include the work of updating or refactoring these mandatory preflight scripts to *not* depend on `bridge/INDEX.md` or its entries, or to define a clear transition path for their deprecation in conjunction with the index retirement.

## Confidence

**High.** The findings are based on direct execution of project-specific validation scripts (`Test-Path`, `grep_search`, and the two `preflight.py` scripts). The evidence unambiguously shows that while `bridge/INDEX.md` is intended to be absent, its implied presence (or the presence of entries within it) is still a requirement for mandatory governance checks. The detailed grep results further underscore the pervasive, albeit deprecated, nature of `bridge/INDEX.md` references.
