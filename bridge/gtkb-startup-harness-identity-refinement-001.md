NEW

# Defect-Fix Proposal - Repair startup harness identity resolution and validation choices for non-default harnesses

bridge_kind: prime_proposal
Document: gtkb-startup-harness-identity-refinement
Version: 001
Status: NEW
Date: 2026-06-18 UTC

author_identity: prime-builder/antigravity
author_harness_id: C
author_session_context_id: 82046f88-ed58-4828-a6a6-cbeb0685807e
author_model: antigravity
author_model_version: gemini-2.5-flash
author_model_configuration: Antigravity interactive Prime Builder session

Project Authorization: PAUTH-PROJECT-PARALLEL-DISPATCH-REMEDIATION-SWEEP-AUTHORIZE-WI-4673-IMPLEMENTATION
Project: PROJECT-PARALLEL-DISPATCH-REMEDIATION-SWEEP
Work Item: WI-4673

target_paths: ["scripts/harness_identity.py", "scripts/session_self_initialization.py"]

Defect-fix proposal focused on reproducing, correcting, and verifying a fault.

## Claim

At session start, the startup script is unable to identify non-default harnesses (e.g. `antigravity`, `ollama`, `openrouter`), reporting them as `unidentified` and failing validation choice checks on CLI commands. This proposal repairs `DEFAULT_HARNESS_IDS` in `scripts/harness_identity.py` and `--harness-name` choices in `scripts/session_self_initialization.py` to natively support all registered harnesses, and enables the startup script to persist interactive role overrides.

## Defect / Reproduction

1. Run the session self-initialization script with a non-default harness:
   `python scripts/session_self_initialization.py --fast-hook --skip-bridge-maintenance --harness-name antigravity`
2. Observed result:
   `session_self_initialization.py: error: argument --harness-name: invalid choice: 'antigravity' (choose from claude, codex)`
3. The underlying cause is that `scripts/harness_identity.py` defines `DEFAULT_HARNESS_IDS` as only containing `claude` and `codex`.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/harness_identity.py`, `scripts/session_self_initialization.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - This proposal and its report use the canonical bridge file chain.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - Keeps the defect, proposal, and report tracked as durable MemBase backlog artifacts.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - Cites all relevant specifications and concrete target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - Verification maps spec requirements to executed tests and observed output.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Integrates the project authorization, project, and work item IDs.
- `SPEC-AUQ-POLICY-ENGINE-001` - Preserves safety gates over the modified scripts.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - Confirms that files remain inside the project root directory.
- `GOV-STANDING-BACKLOG-001` - Governs the lifecycle of WI-4673.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Keeps startup behavior consistent across SDK and wrapper environments.

## Prior Deliberations

- `DELIB-20265285` - Owner approved repair of startup harness identity resolution.
- `DELIB-20261121` - Loyal Opposition Insight Report: Bridge and Multi-Harness Dispatch Analysis.
- `DELIB-1536` - Loyal Opposition Review - SessionStart Formalization (Init-Keyword Contract with Application Scope).

## Owner Decisions / Input

- Authorized by `PAUTH-PROJECT-PARALLEL-DISPATCH-REMEDIATION-SWEEP-AUTHORIZE-WI-4673-IMPLEMENTATION` following the owner's directive that "This session startup is revealing defects in the startup process."

## Requirement Sufficiency

Existing requirements are sufficient.

## Proposed Scope

1. Extend `DEFAULT_HARNESS_IDS` in `scripts/harness_identity.py` to map:
   `"antigravity": "C"`, `"ollama": "D"`, `"openrouter": "F"`.
2. Update CLI parameter choices in `scripts/session_self_initialization.py` so that it parses any harness name present in `DEFAULT_HARNESS_IDS`.
3. In `session_self_initialization.py`, write the per-session role marker file (e.g. `role-<session_id>.json`) if it matches `::init gtkb pb|lo` (or is invoked with `--harness-name` and `--role-profile`), ensuring that interactive role overrides are persisted across subsequent commands in the same session.

## Specification-Derived Verification Plan

| Specification | Verification Command or Evidence |
|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Bridge files are filed append-only with versioned naming. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `git diff` shows modifications are restricted to `scripts/harness_identity.py` and `scripts/session_self_initialization.py`. |
| `DCL-CROSS-HARNESS-ENFORCEMENT-001` | `python scripts/session_self_initialization.py --fast-hook --skip-bridge-maintenance --harness-name antigravity` runs successfully, resolving the harness ID as `C` and harness name as `antigravity` instead of `unidentified`. |

## Acceptance Criteria

- Running `session_self_initialization.py --harness-name antigravity` successfully completes and prints the correct harness ID `C`.
- Interactive session role markers are automatically created during startup if role override is supplied.
- No other hooks or dispatcher behavior is regressed.
- Ruff checks and format checks pass.

## Risks / Rollback

- Risk: incorrect default mapping could break other tools. Mitigation: the additions strictly match the persistent `harness-identities.json` mapping. Rollback is a simple git revert of the changes.

## Files Expected To Change

- `scripts/harness_identity.py`
- `scripts/session_self_initialization.py`

## Recommended Commit Type

`fix`
