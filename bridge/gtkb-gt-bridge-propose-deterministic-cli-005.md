NEW

# GT-KB Bridge Implementation Report - `gt bridge propose` Deterministic CLI

bridge_kind: implementation_report
Document: gtkb-gt-bridge-propose-deterministic-cli
Version: 005 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-gt-bridge-propose-deterministic-cli-004.md
Approved proposal: bridge/gtkb-gt-bridge-propose-deterministic-cli-003.md
Project Authorization: PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-DETERMINISTIC-SERVICES-PARALLEL-BATCH-GT-BRIDGE-PROPOSE-CLI
Project: PROJECT-GTKB-DETERMINISTIC-SERVICES-001
Work Item: WI-3318
target_paths: ["groundtruth-kb/src/groundtruth_kb/cli.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py", "groundtruth-kb/src/groundtruth_kb/bridge/proposal_templates/", "groundtruth-kb/tests/test_cli_bridge_propose.py", ".claude/skills/bridge-propose/SKILL.md"]
Recommended commit type: feat:
author_identity: Codex Prime Builder
author_harness_id: A
author_session_context_id: codex-desktop-2026-05-20-gt-bridge-propose-cli
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: reasoning=medium; collaboration_mode=Default
author_metadata_source: Codex desktop session environment

## Implementation Claim

Implemented `gt bridge propose --kind <type>` as a deterministic, non-dispatchable bridge proposal draft generator. The command renders a governed proposal scaffold from MemBase work-item/project metadata, deterministic spec-link candidates, prior-deliberation candidates, owner-decision tracker matches, and target-path evidence. It writes drafts only under `.gtkb-state\bridge-propose-drafts\` unless `--dry-run` is used, refuses overwrite, and does not write `bridge\` or mutate `bridge\INDEX.md`.

The implementation preserves the existing helper-mediated bridge filing path. Authors still fill AI-judgment placeholders and then file with the existing bridge-propose helper.

## Important Scope Note

The approved proposal expected standalone Markdown templates under `groundtruth-kb/src/groundtruth_kb/bridge/proposal_templates/`. The implementation-start gate accepted the approved directory literal as a target glob but rejected child files such as `groundtruth-kb/src/groundtruth_kb/bridge/proposal_templates/implementation.md` because the authorization packet contains `proposal_templates/`, not `proposal_templates/**`.

To keep moving without widening authorization outside the live GO packet, this implementation stores the same six template shapes as stdlib `string.Template` text inside the authorized `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py` module. The public behavior, six proposal kinds, stdlib-only rendering, generated scaffold sections, and tests all landed. Loyal Opposition should classify whether this storage-location deviation is acceptable or requires a follow-up REVISED implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - final bridge writes remain helper-mediated; CLI drafts are non-dispatchable.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - generated drafts preserve proposal artifact sections and metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - generated drafts auto-populate `Specification Links` candidates.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - generated drafts include a spec-derived verification-plan placeholder and tests map specs to behavior.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - generated drafts include `Project Authorization`, `Project`, and `Work Item`.
- `SPEC-AUQ-POLICY-ENGINE-001` - CLI is a deterministic artifact-production surface.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - output path and target paths are in-root.
- `GOV-STANDING-BACKLOG-001` - CLI fails closed for unknown WIs and reads canonical MemBase work items.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - CLI introduces no hook-path changes and no optional dependency import boundary.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - source, tests, skill doc, bridge proposal, GO, and report form the traceable artifact graph.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - CLI lowers the proposal-creation lifecycle cost while preserving draft vs filed state.
- `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI` - owner authorization for WI-3318.

## Prior Deliberations

- `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI` - owner directive and authorization to build the deterministic bridge-proposal scaffold CLI.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - repetitive bridge proposal scaffolding is an automation candidate.
- `DELIB-1552` - prior DA read-surface/template pre-population context.
- `DELIB-1842` - bridge helper safety precedent requiring no bypass of role authority, existence checks, and safe index behavior.
- `bridge/gtkb-gt-bridge-propose-deterministic-cli-003.md` - approved proposal.
- `bridge/gtkb-gt-bridge-propose-deterministic-cli-004.md` - Loyal Opposition GO verdict.

No new owner decision was required.

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/cli.py` - registers the new `bridge` command group.
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py` - implements `gt bridge propose`, six template shapes, rendering, dry-run, draft writing, overwrite refusal, and user-facing handoff text.
- `groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py` - adds deterministic MemBase/spec/prior-delib/owner-decision/target-path context helpers.
- `groundtruth-kb/tests/test_cli_bridge_propose.py` - covers template rendering, autoload helpers, CLI validation, missing WI behavior, dry-run, draft output, overwrite refusal, no bridge writes, optional-dependency boundary, and help registration.
- `.claude/skills/bridge-propose/SKILL.md` - documents the optional deterministic draft scaffold while preserving helper-mediated filing as canonical.

No `groundtruth-kb/pyproject.toml` dependency change was made.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `test_auto_spec_links_cross_cutting` and rendered-template tests confirm generated drafts include `## Specification Links` and deterministic spec candidates. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_template_emits_spec_to_test_skeleton` confirms generated drafts include `## Specification-Derived Verification Plan` with `${verification_plan_table}` for AI judgment. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `test_auto_project_metadata_active_auth` and `test_implementation_template_renders` confirm active project authorization/project/WI metadata appears in generated drafts. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_cli_does_not_touch_bridge_dir`, `test_cli_dry_run_no_write`, and `test_cli_draft_path_in_root` confirm drafts go only to `.gtkb-state` and no `bridge\INDEX.md` mutation occurs. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `test_cli_draft_path_in_root` confirms draft output remains under the configured project root. |
| `GOV-STANDING-BACKLOG-001` | `test_missing_wi_clear_error` confirms unknown WIs fail closed with a clear error. |
| `SPEC-AUQ-POLICY-ENGINE-001` | `test_cli_arg_validation`, `test_cli_dry_run_no_write`, and `test_cli_refuses_overwrite` cover deterministic CLI policy behavior. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | `test_cli_bridge_propose_no_optional_deps` confirms no direct `jinja2` or `chromadb` imports and that help/dry-run work without optional extras. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | six rendered-template tests confirm every proposal kind emits a governed artifact scaffold with lifecycle-relevant sections. |
| `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI` | active authorization was opened with `python scripts\implementation_authorization.py begin --bridge-id gtkb-gt-bridge-propose-deterministic-cli`. |

## Commands Run

- `python scripts\implementation_authorization.py begin --bridge-id gtkb-gt-bridge-propose-deterministic-cli`
- `python -m pytest groundtruth-kb\tests\test_cli_bridge_propose.py -q --tb=short`
- `python -m pytest groundtruth-kb\tests\test_cli_bridge_propose.py -v --tb=short`
- `python -m ruff check groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\cli_bridge_propose.py groundtruth-kb\src\groundtruth_kb\bridge\proposal_autoload.py groundtruth-kb\tests\test_cli_bridge_propose.py`
- `python -m ruff format --check groundtruth-kb\src\groundtruth_kb\cli.py groundtruth-kb\src\groundtruth_kb\cli_bridge_propose.py groundtruth-kb\src\groundtruth_kb\bridge\proposal_autoload.py groundtruth-kb\tests\test_cli_bridge_propose.py`
- `python -m groundtruth_kb bridge propose --help` from `E:\GT-KB\groundtruth-kb`
- `python -m groundtruth_kb --config E:\GT-KB\groundtruth.toml bridge propose --kind implementation --wi WI-3318 --slug gtkb-smoke-bridge-propose --target-path groundtruth-kb/src/groundtruth_kb/cli.py --dry-run`
- `python scripts\bridge_applicability_preflight.py --bridge-id gtkb-gt-bridge-propose-deterministic-cli`
- `python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-gt-bridge-propose-deterministic-cli`

## Observed Results

- Targeted pytest passed: `18 passed, 1 warning` in the quiet run.
- Verbose targeted pytest passed: `18 passed, 1 warning`.
- Targeted `ruff check` passed: `All checks passed!`
- Targeted `ruff format --check` passed: `4 files already formatted`.
- `python -m groundtruth_kb bridge propose --help` exited 0 and showed the six accepted `--kind` values.
- Live dry-run against `WI-3318` exited 0 and emitted a draft containing `# Implementation Proposal`, `Project Authorization`, `target_paths`, and `## Specification Links`; because it used `--dry-run`, it wrote no draft file.
- Bridge applicability preflight passed for the operative proposal thread: no missing required or advisory specs.
- ADR/DCL clause preflight passed: no blocking gaps.

## Acceptance Criteria Status

- `gt bridge propose --help` resolves through the package CLI entrypoint.
- CLI imports and runs help/dry-run without optional `web` or `search` extras; no direct `jinja2` or `chromadb` imports were added.
- CLI writes only `.gtkb-state\bridge-propose-drafts\<slug>-001.md` during non-dry-run; tests confirm it does not touch `bridge\` or `bridge\INDEX.md`.
- CLI refuses to overwrite an existing draft.
- Missing or unknown `--wi` fails closed with a clear error.
- `groundtruth-kb/pyproject.toml` is unchanged.
- Targeted lint/format is clean.
- Storage-location deviation: standalone child `.md` template files were not added because the active implementation-start authorization rejected child paths under the approved `proposal_templates/` directory literal. Equivalent template behavior is implemented in the authorized CLI module.

## Clause Scope Clarification

This implementation is a single-WI deterministic-services slice for `WI-3318`. It does not file bridge proposals, does not mutate `bridge\INDEX.md`, does not resolve or retire work items, and does not change package dependencies. The review-packet inventory is:

- IP-1: six proposal template shapes implemented as stdlib `string.Template` text in the approved CLI module.
- IP-2: `gt bridge propose` command group and command registered under `gt`.
- IP-3: deterministic autoload helpers for specs, project metadata, owner decisions, prior deliberations, and in-root evidence.
- IP-4: skill documentation update describing the draft scaffold and preserving helper-mediated filing.
- IP-5: focused test coverage in `groundtruth-kb/tests/test_cli_bridge_propose.py`.

## Bridge INDEX Maintenance

After final preflight on this draft, the bridge helper will file `bridge/gtkb-gt-bridge-propose-deterministic-cli-005.md` and insert:

`NEW: bridge/gtkb-gt-bridge-propose-deterministic-cli-005.md`

under the existing `Document: gtkb-gt-bridge-propose-deterministic-cli` entry, above the prior `GO`, `REVISED`, `NO-GO`, and `NEW` rows. Prior versions remain preserved.

## Risk And Rollback

Residual risk is the storage-location deviation from filesystem template files to in-module template text. The behavior is covered by tests, but if LO requires exact IP-1 storage semantics, the follow-up should either amend the authorization target to `groundtruth-kb/src/groundtruth_kb/bridge/proposal_templates/**` or fix the implementation-start gate to treat trailing-slash directory targets as child-authorizing globs.

Rollback is straightforward: remove `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`, remove `groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py`, remove the `bridge_group` registration from `groundtruth-kb/src/groundtruth_kb/cli.py`, remove `groundtruth-kb/tests/test_cli_bridge_propose.py`, and remove the new skill documentation paragraph. Existing helper-mediated bridge filing remains unaffected.

## Loyal Opposition Asks

1. Verify the implemented CLI behavior against the approved proposal and linked specs.
2. Explicitly classify the in-module template storage deviation caused by the authorization gate's directory-target behavior.
3. Return `VERIFIED` if the behavior and documented deviation are acceptable; otherwise return `NO-GO` with concrete findings or a required follow-up.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
