REVISED

# gtkb-wi3459-release-skill-adapter-hygiene - revised target scope for adapter hygiene

bridge_kind: prime_proposal
Document: gtkb-wi3459-release-skill-adapter-hygiene
Version: 005
Responds-To: bridge/gtkb-wi3459-release-skill-adapter-hygiene-004.md
Author: Codex Prime Builder
Date: 2026-06-28 UTC

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 2026-06-28T04-18-22Z-prime-builder-A-ac276e
author_model: GPT-5
author_model_version: GPT-5 Codex
author_model_configuration: Codex bridge auto-dispatch; approval_policy=never; workspace-write sandbox

Project Authorization: PAUTH-PROJECT-GTKB-SKILL-MODERNIZATION-SKILL-MODERNIZATION-BOUNDED-IMPLEMENTATION-2026-06-23
Project: PROJECT-GTKB-SKILL-MODERNIZATION
Work Item: WI-3459

target_paths: [".claude/skills/verify/helpers/gtkb-remove-orphaned-bridge-authority-direction-switch-004-body.md", ".claude/skills/verify/helpers/gtkb-remove-orphaned-bridge-authority-direction-switch-004-draft.md", ".claude/skills/verify/helpers/gtkb-remove-orphaned-bridge-authority-direction-switch-004-final.md", ".claude/skills/verify/helpers/gtkb-wi4761-restore-ci-testing-integration-health-014-body.md", ".codex/skills/**", ".codex/skills/MANIFEST.json", ".codex/skills/decision-capture/helpers/__pycache__/record_decision.cpython-314.pyc", ".codex/skills/spec-intake/helpers/__pycache__/spec_intake.cpython-314.pyc", ".codex/skills/verify/helpers/__pycache__/write_verdict.cpython-314.pyc", "config/agent-control/harness-capability-registry.toml", "platform_tests/scripts/test_no_tracked_skill_helper_scratch.py"]

implementation_scope: scaffold_update,test_addition,config_registry_edit,generated_adapter_update
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Revision Claim

This REVISED proposal answers `bridge/gtkb-wi3459-release-skill-adapter-hygiene-004.md` by expanding the target-path envelope for the already-approved WI-3459 hygiene work. No implementation files are changed by this revision. It requests Loyal Opposition review of the corrected scope so Prime Builder can rerun the adapter generator and cleanup pass without crossing the implementation-start authorization boundary.

The live Prime Builder dispatch rechecked the current generator drift on 2026-06-28:

```text
groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --check --update-registry
Codex skill adapters: would update 3 file(s)
- .codex/skills/decision-capture/helpers/__pycache__/record_decision.cpython-314.pyc
- .codex/skills/spec-intake/helpers/__pycache__/spec_intake.cpython-314.pyc
- config/agent-control/harness-capability-registry.toml
```

The previous GO was too narrow because it did not authorize the registry output and the currently observed cache cleanup targets. The revised `target_paths` cover the generator's deterministic Codex adapter output surface, the manifest, the registry output, the currently observed helper cache files, the original canonical scratch-file deletions, and the focused helper-scratch regression test.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - protected skill adapter, registry, and test files require bridge GO plus implementation-start authorization.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this revision cites governing specs and maps the revised scope to verification commands.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - this revision carries PAUTH, project, work item, and concrete target paths.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the later implementation report must map these specs to executed evidence.
- `GOV-STANDING-BACKLOG-001` - `WI-3459` remains the open backlog authority for clean-tree skill adapter regeneration and parity follow-on work.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation remains bounded by the active skill-modernization PAUTH.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the release-blocking hygiene finding is preserved through the bridge audit trail.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - completed verdict/report scratch artifacts should not masquerade as reusable helper source.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - this release-blocking adapter drift is formalized as bridge-scoped implementation work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all work remains under the GT-KB root and does not rely on external Agent Red surfaces.
- `ADR-CROSS-HARNESS-PARITY-001` - skill-surface changes must preserve cross-harness parity or declare a waiver.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - harness-surface proposals require an explicit Cross-Harness Disposition section.

## Prior Deliberations

- `DELIB-20265586` - owner authorized the bounded 2026-06-23 project implementation set, including the active PAUTH for `WI-3459`.
- `DELIB-S20260626-PARITY-INTERVIEW-CLUSTER2-ENFORCEMENT` - owner selected layered parity enforcement and required Cross-Harness Disposition for harness-surface proposals.
- `WI-3459` - remains open under `PROJECT-GTKB-SKILL-MODERNIZATION`; current status says the item was expanded with harness capability registry drift.
- `bridge/gtkb-wi3459-release-skill-adapter-hygiene-001.md` - original proposal.
- `bridge/gtkb-wi3459-release-skill-adapter-hygiene-002.md` - original GO verdict.
- `bridge/gtkb-wi3459-release-skill-adapter-hygiene-003.md` - blocked implementation report identifying target-path mismatch.
- `bridge/gtkb-wi3459-release-skill-adapter-hygiene-004.md` - NO-GO requiring target-path expansion.

## Owner Decisions / Input

Existing AUQ-backed owner authorization is carried forward through `DELIB-20265586` and PAUTH `PAUTH-PROJECT-GTKB-SKILL-MODERNIZATION-SKILL-MODERNIZATION-BOUNDED-IMPLEMENTATION-2026-06-23`. This auto-dispatch cannot request interactive owner input, and no new owner decision is required for the revised target list because `WI-3459` is snapshot-included in the active project authorization.

## Requirement Sufficiency

Existing requirements sufficient - the NO-GO identified a scope-envelope defect, not a missing product or governance requirement. The active work item, project authorization, bridge chain, and parity-governance deliberation are enough to request the corrected implementation target list.

## Finding Response

### Finding 1: Scope Blocker (Target-Path Mismatch)

Response: accepted. The previous proposal under-scoped the live generator outputs. This revision adds:

- `.codex/skills/**` and `.codex/skills/MANIFEST.json` for deterministic Codex adapter generator outputs.
- `config/agent-control/harness-capability-registry.toml` for the registry output that the generator currently reports.
- `.codex/skills/decision-capture/helpers/__pycache__/record_decision.cpython-314.pyc` and `.codex/skills/spec-intake/helpers/__pycache__/spec_intake.cpython-314.pyc` for the currently observed cache cleanup targets.
- The original canonical `.claude/skills/verify/helpers/*` scratch artifact paths and focused regression-test path from the approved proposal.

No generator source change is proposed. If implementation discovers a new outside-scope mutation target after a fresh implementation-start packet, Prime Builder must stop and file another bridge revision rather than partially implementing.

## Proposed Implementation

1. Create a fresh implementation-start packet from the revised GO, then rerun `scripts/generate_codex_skill_adapters.py --check --update-registry` to confirm the current update set.
2. Remove the stale canonical and Codex helper scratch/cache artifacts only within the revised target envelope.
3. Regenerate Codex skill adapters and registry metadata through the existing generator.
4. Add or update `platform_tests/scripts/test_no_tracked_skill_helper_scratch.py` so tracked helper directories cannot carry verdict-body, draft, final, temporary, or Python cache artifacts.
5. Keep the implementation reductive: no warning prose, workaround docs, or alternate authority surfaces.

## Cross-Harness Disposition

- Claude skill surface: canonical `.claude/skills/verify/helpers` loses only completed verdict/report scratch artifacts named in `target_paths`; reusable helper source remains in place.
- Codex skill surface: generated `.codex/skills/**` mirrors, manifest, helper cache cleanup, and registry metadata are in scope so the Codex adapter generator can converge cleanly.
- API, Cursor, and Antigravity surfaces: not targeted by this slice. The current release blocker is the Codex adapter/registry check named above; no waiver is requested for other harness surfaces.

## Pre-Filing Preflight Subsection

Candidate preflights are run against this exact revision file before live filing. The filing helper reruns the applicability and clause preflights before writing `bridge/gtkb-wi3459-release-skill-adapter-hygiene-005.md`.

## Spec-Derived Verification Plan

| Spec / governing surface | Planned verification |
| --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi3459-release-skill-adapter-hygiene --session-id <dispatch-session>` and `groundtruth-kb/.venv/Scripts/python.exe scripts/implementation_authorization.py begin --bridge-id gtkb-wi3459-release-skill-adapter-hygiene --session-id <dispatch-session>`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi3459-release-skill-adapter-hygiene` must report no missing required or advisory specs. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/gt.exe projects show PROJECT-GTKB-SKILL-MODERNIZATION`, `groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-3459 --json`, and `groundtruth-kb/.venv/Scripts/gt.exe projects authorizations PROJECT-GTKB-SKILL-MODERNIZATION --json`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The post-implementation report must map each linked specification to executed command evidence. |
| `GOV-STANDING-BACKLOG-001` / `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | The commands above must show `WI-3459` open and included in an active PAUTH. |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | `groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --check --update-registry` must pass after implementation, and the Cross-Harness Disposition section must remain accurate. |
| Target-path scope | `groundtruth-kb/.venv/Scripts/python.exe scripts/proposal_target_paths_coverage_preflight.py --content-file bridge/gtkb-wi3459-release-skill-adapter-hygiene-005.md --strict` must pass after filing. |
| Scratch-artifact hygiene | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_no_tracked_pyc_artifacts.py platform_tests/scripts/test_no_tracked_skill_helper_scratch.py -q --tb=short` must pass after implementation. |
| Generator behavior | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py -q --tb=short` must pass after implementation. |
| Formatting/lint | `groundtruth-kb/.venv/Scripts/python.exe -m ruff check platform_tests/scripts/test_no_tracked_skill_helper_scratch.py` and `groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check platform_tests/scripts/test_no_tracked_skill_helper_scratch.py` must pass if that test is created or changed. |

## Acceptance Criteria

- `scripts/generate_codex_skill_adapters.py --check --update-registry` exits 0 after implementation.
- The implementation-start packet authorizes every mutation required by the generator and cleanup pass.
- No tracked `.claude/skills/**/helpers` or `.codex/skills/**/helpers` file matches the scratch/verdict-body/cache patterns covered by the new regression test.
- No tracked `.pyc` or `__pycache__` artifact exists.
- Codex adapter helper mirrors remain current with mirrorable canonical helper files.
- The implementation report carries forward this revised target-path scope and exact command evidence.

## Risk And Rollback

Risk remains low but the target envelope is intentionally broader than the original proposal because the generator owns a deterministic subtree and registry output. The implementation remains constrained by WI-3459, the revised target list, and the implementation-start packet. Rollback is a single revert of the eventual implementation commit, which restores the pre-cleanup adapter drift and helper scratch state.

## Commands Run Before Filing

```text
groundtruth-kb/.venv/Scripts/gt.exe harness roles
groundtruth-kb/.venv/Scripts/gt.exe bridge dispatch status
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --format json
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/show_thread_bridge.py gtkb-wi3459-release-skill-adapter-hygiene --format json --preview-lines 1200
groundtruth-kb/.venv/Scripts/gt.exe bridge show gtkb-wi3459-release-skill-adapter-hygiene --json
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_claim_cli.py claim gtkb-wi3459-release-skill-adapter-hygiene --session-id 2026-06-28T04-18-22Z-prime-builder-A-ac276e --ttl-seconds 7200
groundtruth-kb/.venv/Scripts/python.exe scripts/generate_codex_skill_adapters.py --check --update-registry
groundtruth-kb/.venv/Scripts/gt.exe projects show PROJECT-GTKB-SKILL-MODERNIZATION
groundtruth-kb/.venv/Scripts/gt.exe backlog show WI-3459 --json
groundtruth-kb/.venv/Scripts/gt.exe projects authorizations PROJECT-GTKB-SKILL-MODERNIZATION --json
groundtruth-kb/.venv/Scripts/gt.exe deliberations search "WI-3459 skill adapter registry parity Codex adapter hygiene" --limit 8
```

File bridge scan contribution: 1 entry processed.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
