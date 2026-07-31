REVISED
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f0c8ce96-8652-4240-994b-42a6d03516e3
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

# Bridge Proposal - gtkb-wi5117-adapter-generator-atomic-write - 003 (REVISED: cite established PROJECT-GTKB-TREE-STABILIZATION authorization)

bridge_kind: prime_proposal
Document: gtkb-wi5117-adapter-generator-atomic-write
Version: 003
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-10 UTC
Responds-To: bridge/gtkb-wi5117-adapter-generator-atomic-write-002.md (GO)

Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5117
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-TREE-STABILIZATION-WI-5117-ATOMIC-WRITE-AUTHORIZATION

target_paths: ["scripts/generate_codex_skill_adapters.py", "scripts/generate_antigravity_skill_adapters.py", "scripts/generate_api_skill_adapters.py", "scripts/_wrap_io.py", "platform_tests/scripts/test_generate_codex_skill_adapters.py", "platform_tests/scripts/test_generate_antigravity_skill_adapters.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

## Why This Revision

The `-001` proposal (GO at `-002`) cited `Project Authorization: pending` because
PROJECT-GTKB-TREE-STABILIZATION had no standing PAUTH and the owner AUQ selected
"File proposal now, authorize at GO." The GO's Condition 2 required establishing
that authorization before source mutation, and Condition 1 required sequencing
after WI-5095 (which shares five target files). Both conditions are now satisfied:

- **Condition 2 (authorization) established.** Owner AUQ 2026-07-10 authorized a
  WI-5117-scoped PROJECT-GTKB-TREE-STABILIZATION authorization, captured as
  `DELIB-202665932` and materialized as
  `PAUTH-PROJECT-GTKB-TREE-STABILIZATION-TREE-STABILIZATION-WI-5117-ATOMIC-WRITE-AUTHORIZATION`
  (scoped to WI-5117; allowed mutation: source + test; forbidden: deployment,
  credential-change, kb-schema-mutation). This REVISED cites that real PAUTH so
  the implementation-start packet validates (the `-001` `pending` string blocked
  `begin`).
- **Condition 1 (WI-5095 sequencing) satisfied.** WI-5095 Slice A is VERIFIED and
  committed (`fd36d92c`); its four shared files are at HEAD (LF), so WI-5117
  implements on a clean, non-commingled base.

The **design is unchanged** from `-001` (LO already GO'd it at `-002`). The write
sites were re-confirmed against the committed WI-5095 base (line numbers shifted
under the WI-5095 refactor but the calls persist).

## Problem

The three skill-adapter generators write adapter files, resource files, and the
adapter registry with direct, non-atomic filesystem writes. A direct
`write_text`/`write_bytes` is not atomic: a transient mid-write `OSError`
(WI-5117 observed `Errno 22` on `.agent/skills/MANIFEST.json`, cleared on retry)
fails the generator run and can leave a partially-written or truncated target.
GT-KB's own runtime writers already use atomic write-to-temp + `os.replace`
(`scripts/_wrap_io.py::_atomic_write_text`, `bridge_dispatch_starvation_telemetry.py`,
`bridge_lease_registry.py`, `bridge_dispatch_reset.py::_write_json_atomic`); the
adapter generators are the outlier.

## Proposed Fix (re-confirmed write sites on the committed WI-5095 base)

1. `scripts/_wrap_io.py`: add `_atomic_write_bytes(path, content)` alongside the
   existing `_atomic_write_text(path, content)` (same `.tmp` + `os.replace`
   discipline; same-filesystem sibling temp).
2. Route the direct write calls through the atomic helpers, preserving `mkdir`,
   the `existing == content` short-circuit, `--check` early-return,
   `RESOURCE_EXCLUDED_PREFIXES`, registry `source_sha256`, and parity semantics:
   - `scripts/generate_codex_skill_adapters.py`: `_write_if_changed`
     (`path.write_text`, L261), `_write_bytes_if_changed` (`path.write_bytes`,
     L272), and `update_registry` (`registry_path.write_text`, L353).
   - `scripts/generate_antigravity_skill_adapters.py`: `update_registry`
     (`registry_path.write_text`, L177). Its adapter-body writes reuse the codex
     `_write_if_changed`, covered by (2a).
   - `scripts/generate_api_skill_adapters.py`: `_write_if_changed`
     (`path.write_text`, L210).

Only the final commit-of-bytes-to-disk becomes atomic. No behavioral change to
generated output, `--check`, resource-exclusion, registry `source_sha256`, the
`--update-registry` deprecated-no-op (WI-5095), or parity is intended.

Out of scope: any adapter content/format change; harness surfaces outside the
generators; the WI-5095 registry reconciliation (separately owner-deferred).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge-governed source/test change, approved before protected mutation.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` - implementation-start authorization now established via the cited PAUTH.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` - the PAUTH does not bypass the GO or the implementation-start packet.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project / Work Item / Project Authorization metadata above.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete specification linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the report will map focused tests to the linked specs.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths are GT-KB platform files inside `E:\GT-KB`.
- `GOV-STANDING-BACKLOG-001` - WI-5117 is the active backlog record for this defect.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - defect, proposal, verification, report stay linked through governed artifacts.

## Prior Deliberations

- `DELIB-WI5116-PHASE1-SWEEP-DIAGNOSIS-20260709` - the tree-stabilization diagnosis that surfaced the adapter/scratch churn class this WI belongs to.
- This thread `-001`/`-002` (GO) - the atomic-write design LO already approved; this REVISED only wires the now-established project authorization and re-confirms the write sites on the committed WI-5095 base.
- `DELIB-202665932` (owner_decision) - the WI-5117-scoped PROJECT-GTKB-TREE-STABILIZATION authorization backing the cited PAUTH.
- WI-5095 thread (VERIFIED, commit `fd36d92c`) - the committed base this WI implements on; its adapter-only-refresh + LF finalization are the immediate predecessor to these write sites.
- _No prior deliberations on the atomic-write approach itself: it remains the novel single-concern defect fix the `-001`/`-002` GO reviewed._

## Owner Decisions / Input

- AskUserQuestion 2026-07-09 "File proposal now, authorize at GO" - authorized filing `-001` ahead of the project authorization.
- AskUserQuestion 2026-07-10 (authorization scope) - owner selected "Scoped to WI-5117"; captured as `DELIB-202665932` and materialized as the cited PAUTH.
- AskUserQuestion 2026-07-10 (next action) - owner selected "Start WI-5117 now", authorizing this REVISED filing and the subsequent implementation on the committed WI-5095 base.
- No credential change, deployment, force-push, or sandbox weakening is requested or authorized.

## Requirement Sufficiency

Existing requirements sufficient. WI-5117's acceptance ("route the generator
writes through the established atomic write pattern"), the GT-KB atomic-write
convention, and `GOV-STANDING-BACKLOG-001` govern this bounded defect repair. No
new or revised requirement is required before implementation begins after LO
re-GO and the implementation-start packet.

## Spec-Derived Verification Plan

Focused tests land in `platform_tests/scripts/test_generate_codex_skill_adapters.py`
and `platform_tests/scripts/test_generate_antigravity_skill_adapters.py`.

| Spec / governing surface | Verification |
| --- | --- |
| WI-5117 acceptance (atomic write) | A test patching the generator's final write so a simulated mid-write `OSError` leaves the pre-existing target intact (no partial/truncated content) and no stray sibling `.tmp` remains; plus a test asserting the generators route writes through `_wrap_io._atomic_write_text` / `_atomic_write_bytes`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest (`--basetemp .harness-tmp/wi5117`), plus `ruff check` and `ruff format --check` on the changed files, cited in the report. |
| Regression safety | Run the existing generator suites to confirm no change to generated output, `--check`, or registry `source_sha256` handling. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Before source edits, create the implementation-start packet from the fresh GO on this REVISED and cite it. |

Expected focused commands:

    groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_generate_codex_skill_adapters.py platform_tests/scripts/test_generate_antigravity_skill_adapters.py -q --tb=short --basetemp .harness-tmp/wi5117
    groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/generate_codex_skill_adapters.py scripts/generate_antigravity_skill_adapters.py scripts/generate_api_skill_adapters.py scripts/_wrap_io.py
    groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/generate_codex_skill_adapters.py scripts/generate_antigravity_skill_adapters.py scripts/generate_api_skill_adapters.py scripts/_wrap_io.py

## Risk And Rollback

- Risk: a stray sibling `.tmp` on process-kill between write and replace. Mitigation: unique sibling temp + cleanup-on-exception; `os.replace` is atomic for same-filesystem moves.
- Risk: a subtle behavior change to `--check` or change-detection. Mitigation: keep the `existing == content` short-circuit and `--check` early-return exactly as-is; only the final disk-commit path changes; the existing generator regression suites gate this.
- Risk: `_wrap_io` coupling from the generators. Mitigation: `_wrap_io` is a stdlib-only, side-effect-free io helper in `scripts/`; reuse is DRYer than a fourth copy.
- Rollback: single-commit revert of the changed write calls + the added `_atomic_write_bytes`. No data, credential, or KB rollback in scope.

## Recommended Commit Type

Recommended commit type: `fix` - repairs a reliability defect (non-atomic adapter-generator writes that fail a run and can leave partial files) with no new user-facing capability surface.

## Pre-Filing Preflight Subsection

Applicability and ADR/DCL clause preflights are run against this REVISED body via
`--content-file` before filing; expected `preflight_passed: true`,
`missing_required_specs: []`, and clause preflight `Blocking gaps: 0`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
