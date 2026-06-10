VERIFIED
author_identity: Codex Loyal Opposition
author_harness_id: A
author_session_context_id: codex-desktop-2026-05-27-lo-startup
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: reasoning=medium; collaboration_mode=Default
author_metadata_source: Codex desktop session environment

# VERIFIED - `gt bridge propose` Deterministic CLI

bridge_kind: lo_verdict
Document: gtkb-gt-bridge-propose-deterministic-cli
Version: 006
Author: Loyal Opposition (Codex harness A)
Date: 2026-05-27 UTC
Responds to: bridge/gtkb-gt-bridge-propose-deterministic-cli-005.md
Verdict: VERIFIED

## Claim

The implementation satisfies the approved `gt bridge propose` deterministic draft CLI scope from `bridge/gtkb-gt-bridge-propose-deterministic-cli-003.md` and the GO in `bridge/gtkb-gt-bridge-propose-deterministic-cli-004.md`.

The in-module template storage deviation is accepted for this slice because the implementation-start gate did not authorize child files under the approved `proposal_templates/` directory literal, and the implemented behavior preserves the approved deterministic scaffold, non-dispatchable draft boundary, stdlib-only rendering path, and helper-mediated filing contract.

## Evidence

- `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-gt-bridge-propose-deterministic-cli --format json --preview-lines 500`: live thread read; latest indexed operative file was `bridge/gtkb-gt-bridge-propose-deterministic-cli-005.md`.
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-gt-bridge-propose-deterministic-cli`: passed with `preflight_passed: true`, no missing required specs, and no missing advisory specs.
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-gt-bridge-propose-deterministic-cli`: passed with 0 blocking gaps.
- `python -m pytest groundtruth-kb/tests/test_cli_bridge_propose.py -q --tb=short`: 18 passed, 1 warning.
- `python -m ruff check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py groundtruth-kb/tests/test_cli_bridge_propose.py`: all checks passed.
- `python -m ruff format --check groundtruth-kb/src/groundtruth_kb/cli.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py groundtruth-kb/src/groundtruth_kb/bridge/proposal_autoload.py groundtruth-kb/tests/test_cli_bridge_propose.py`: 4 files already formatted.
- From `groundtruth-kb`: `python -m groundtruth_kb bridge propose --help`: exit 0 and lists the six proposal kinds.
- From `groundtruth-kb`: `python -m groundtruth_kb --config E:\GT-KB\groundtruth.toml bridge propose --kind implementation --wi WI-3318 --slug gtkb-smoke-bridge-propose --target-path groundtruth-kb/src/groundtruth_kb/cli.py --dry-run`: exit 0 and emitted a non-dispatchable draft containing project authorization, work item metadata, target paths, specification links, prior deliberation candidates, owner-decision placeholder, and AI-judgment placeholders without writing `.gtkb-state`.
- `groundtruth-kb/src/groundtruth_kb/cli.py` imports and registers `bridge_group`.
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py` uses stdlib `string.Template`, writes only `.gtkb-state/bridge-propose-drafts/<slug>-001.md` for non-dry-run mode, refuses overwrite, and does not write `bridge/` or `bridge/INDEX.md`.
- `groundtruth-kb/tests/test_cli_bridge_propose.py` covers dry-run no-write behavior, in-root draft path, overwrite refusal, no `bridge/` mutation, optional dependency boundary, and real package entrypoint help resolution.

## Prior Deliberations

- `DELIB-S350-BATCH7-GT-BRIDGE-PROPOSE-CLI` directly authorizes WI-3318 and records the owner directive to build `gt bridge propose --kind <type>`.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` supports moving repetitive bridge proposal scaffolding into deterministic tooling.
- `DELIB-1552` verifies the prior Deliberation Archive read-surface/template pre-population work, relevant to prior-deliberation candidate loading.
- `DELIB-1842` remains relevant bridge-helper safety precedent: final bridge filing must preserve role authority, file existence checks, and safe INDEX behavior. This implementation keeps final filing outside the draft CLI.

## Deviation Classification

The implementation stores six template shapes inside `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py` instead of standalone files under `groundtruth-kb/src/groundtruth_kb/bridge/proposal_templates/`.

This is not a blocking deviation for this slice:

- The GO authorized `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`.
- The report explains that the implementation-start authorization accepted the directory literal but rejected child template files.
- The resulting behavior is equivalent for the approved acceptance criteria.
- The CLI remains stdlib-only and does not add a base dependency.
- Tests verify all six kinds and the draft-only safety boundary.

Residual maintainability risk remains: standalone templates may be easier to review and edit. A future cleanup may either authorize `proposal_templates/**` explicitly or update the implementation-start target matcher to treat trailing-slash directory targets as child-authorizing globs.

## Risk / Impact

The verified CLI creates draft artifacts only. It does not create dispatchable bridge files, does not mutate `bridge/INDEX.md`, and does not replace the existing bridge-propose helper path. The main remaining risk is quality of auto-loaded candidate context, which is intentionally surfaced as editable draft content rather than final authority.

## Recommended Action

Prime Builder may treat WI-3318's deterministic draft CLI slice as verified. Future work may improve template storage ergonomics, but no correction is required before using the CLI for non-dispatchable draft scaffolding.

## Owner Decision Needed

None.

File bridge scan contribution: 1 entry processed.
