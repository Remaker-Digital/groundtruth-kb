NEW

# Bridge Proposal - gtkb-wi5117-adapter-generator-atomic-write - 001

bridge_kind: prime_proposal
Document: gtkb-wi5117-adapter-generator-atomic-write
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-09 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: de1dc180-4fab-4763-84c9-62b7849e68d1
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5117
Project Authorization: pending (owner AUQ 2026-07-09 selected "File proposal now, authorize at GO"; PROJECT-GTKB-TREE-STABILIZATION has no standing PAUTH; implementation-start authorization to be established at GO time per GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001)

target_paths: ["scripts/generate_codex_skill_adapters.py", "scripts/generate_antigravity_skill_adapters.py", "scripts/generate_api_skill_adapters.py", "scripts/_wrap_io.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py", "platform_tests/scripts/test_generate_antigravity_skill_adapters.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Problem

The three skill-adapter generators write adapter files, resource files, and the
adapter registry with direct, non-atomic filesystem writes:

- `scripts/generate_codex_skill_adapters.py`: `_write_if_changed` (`path.write_text`, ~L261),
  `_write_bytes_if_changed` (`path.write_bytes`, ~L272), and the registry write
  (`registry_path.write_text`, ~L375).
- `scripts/generate_antigravity_skill_adapters.py`: registry write
  (`registry_path.write_text`, ~L182) and its `_write_*` helpers.
- `scripts/generate_api_skill_adapters.py`: `_write_if_changed`
  (`path.write_text`, ~L210) and registry write.

A direct `write_text`/`write_bytes` is not atomic: a transient mid-write
`OSError` (WI-5117 observed `Errno 22` on `.agent/skills/MANIFEST.json`, which
cleared on retry) fails the generator run and can leave a partially-written or
truncated target file. GT-KB's own runtime writers already use the atomic
write-to-temp + `os.replace` pattern (e.g. `scripts/_wrap_io.py::_atomic_write_text`,
`scripts/bridge_dispatch_starvation_telemetry.py::_atomic_write`,
`scripts/bridge_lease_registry.py`, `groundtruth-kb/src/groundtruth_kb/bridge_dispatch_reset.py::_write_json_atomic`).
The adapter generators are the outlier and are therefore fragile.

## Proposed Fix

Route all adapter-generator file writes through an atomic write-to-sibling-temp
+ `os.replace` path, reusing the existing helper rather than adding a fourth
copy of the pattern:

1. `scripts/_wrap_io.py`: add `_atomic_write_bytes(path, content)` alongside the
   existing `_atomic_write_text(path, content)` (same `.tmp` + `os.replace`
   discipline; the module already documents the Windows same-filesystem
   atomicity guarantee).
2. `scripts/generate_codex_skill_adapters.py`,
   `scripts/generate_antigravity_skill_adapters.py`,
   `scripts/generate_api_skill_adapters.py`: replace the direct
   `path.write_text(...)` / `path.write_bytes(...)` / `registry_path.write_text(...)`
   calls inside `_write_if_changed` / `_write_bytes_if_changed` / the registry
   writer with `_wrap_io._atomic_write_text` / `_atomic_write_bytes`. The
   `mkdir(parents=True, exist_ok=True)` and change-detection (`existing == content`
   short-circuit, `--check` mode) semantics are preserved; only the final commit
   of bytes to disk becomes atomic.

No behavioral change to generated output, `--check` mode, resource-exclusion
prefixes (`RESOURCE_EXCLUDED_PREFIXES`), registry `source_sha256` handling, or
parity semantics is intended; the change is confined to how the final write hits
disk.

Out of scope: WI-5115 (already remediated 2026-07-09 - helper scratch already
defaults to `.gtkb-state/`); the `--update-registry` unsupported-parity
protection path (unchanged); any adapter content/format change; harness surfaces
outside the generators (`.claude/hooks`, settings, skills bodies).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this source/test change is bridge-governed and approved before protected mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation-start authorization is established at GO time (authorization pending per owner AUQ).
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - no standing authorization is claimed; this proposal does not bypass the GO or implementation-start packet.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites the governing specification surfaces.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the report will map focused tests to the linked specs.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the Project / Work Item metadata above.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are GT-KB platform files inside `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - WI-5117 is the active backlog record for this defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the defect and its fix are preserved as durable bridge/work-item evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - defect, proposal, verification, and report stay linked through governed artifacts.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-5117 advances through the standard defect-fix lifecycle triggers.

## Prior Deliberations

- `DELIB-WI5116-PHASE1-SWEEP-DIAGNOSIS-20260709` - the tree-stabilization diagnosis session that surfaced the adapter/scratch churn class this WI belongs to.
- _No prior deliberations specific to adapter-generator atomic writes: this is a novel single-concern defect fix with no prior DA precedent on the atomic-write approach for the generators._

## Owner Decisions / Input

- Owner AUQ 2026-07-09 (detected_via ask_user_question): "File proposal now, authorize at GO" - authorizes filing this NEW proposal ahead of project authorization; implementation-start authorization for PROJECT-GTKB-TREE-STABILIZATION is to be established at GO time.
- Owner AUQ 2026-07-09: "File WI-5117; close WI-5115" - confirmed WI-5115 is already remediated (closed) and WI-5117 is the sole real durable fix in plan item 3.
- No credential change, deployment, force-push, or sandbox weakening is requested or authorized.

## Requirement Sufficiency

Existing requirements sufficient. WI-5117's acceptance ("add atomic write to both
generators"), the established GT-KB atomic-write pattern, and
`GOV-STANDING-BACKLOG-001` govern this bounded defect repair. No new or revised
requirement is required before implementation begins after LO GO and
implementation-start authorization.

## Spec-Derived Verification Plan

Focused tests land in `platform_tests/scripts/test_generate_codex_skill_adapters.py`
and `platform_tests/scripts/test_generate_antigravity_skill_adapters.py` (and the
api-generator test if present).

| Spec / governing surface | Verification |
| --- | --- |
| WI-5117 acceptance (atomic write) | Add a test that patches the generator's write path so a simulated mid-write `OSError` on the final commit leaves the pre-existing target file intact (no partial/truncated content) and no stray sibling `.tmp` remains; and a test asserting the generators route writes through `_wrap_io._atomic_write_text` / `_atomic_write_bytes`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run the focused pytest with `--basetemp .gtkb-state/pytest-tmp/wi5117`, plus `ruff check` and `ruff format --check` on the changed files, and cite exact pass results in the report. |
| Regression safety | Run the existing generator suites (`test_generate_codex_skill_adapters.py`, `test_generate_antigravity_skill_adapters.py`, and any api-generator test) to confirm no change to generated output, `--check` mode, or registry `source_sha256` handling. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Before source edits, establish implementation-start authorization for this GO (and the project authorization settled per the owner "authorize at GO" decision), and cite the packet. |

Expected focused commands:

groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py -q --tb=short --basetemp .gtkb-state/pytest-tmp/wi5117

groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/generate_codex_skill_adapters.py scripts/generate_antigravity_skill_adapters.py scripts/generate_api_skill_adapters.py scripts/_wrap_io.py

groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/generate_codex_skill_adapters.py scripts/generate_antigravity_skill_adapters.py scripts/generate_api_skill_adapters.py scripts/_wrap_io.py

## Risk And Rollback

- Risk: introducing a sibling `.tmp` then `os.replace` could leave a stray temp file if the process is killed between write and replace. Mitigation: use a unique temp name in the target directory and clean up on exception; `os.replace` is atomic for same-filesystem moves (the temp is a sibling of the target).
- Risk: a subtle behavior change to `--check` mode or change-detection. Mitigation: keep the `existing == content` short-circuit and `--check` early-return exactly as-is; only the final disk-commit path changes; the existing generator regression suites gate this.
- Risk: `_wrap_io` coupling from the generators. Mitigation: `_wrap_io` is a stdlib-only, side-effect-free io helper in `scripts/`; reusing its atomic primitives is DRYer than a fourth copy and matches the tracked-surface-bias preference.
- Rollback: single-commit revert of the changed write calls + the added `_atomic_write_bytes` restores the prior direct-write behavior; no data, credential, or KB rollback is in scope.

## Recommended Commit Type

`fix:` - repairs a reliability defect (non-atomic adapter-generator writes that fail a run and can leave partial files) with no new user-facing capability surface.

## Pre-Filing Preflight Subsection

Applicability and ADR/DCL clause preflights are run against this proposal body via
`--content-file` before filing; expected `preflight_passed: true`,
`missing_required_specs: []`, and clause preflight `Blocking gaps: 0`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
