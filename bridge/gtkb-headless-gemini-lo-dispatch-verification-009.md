REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-headless-gemini-substrate-revised-9-registry-path
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Headless Gemini LO Dispatch Verification REVISED-9: registry-stored absolute command path

bridge_kind: implementation_proposal
Document: gtkb-headless-gemini-lo-dispatch-verification
Version: 009 (REVISED proposal; architectural-path change per S364 owner AUQ)
Responds-To: bridge/gtkb-headless-gemini-lo-dispatch-verification-008.md (Codex NO-GO on -007 post-impl)
Carries-Forward: bridge/gtkb-headless-gemini-lo-dispatch-verification-003.md (original GO'd proposal)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-28 UTC
Implements: WI-3349 (End-to-end Gemini CLI headless LO-review dispatch verification)
Project Authorization: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-ANTIGRAVITY-INTEGRATION-IMPLEMENTATION-AUTHORIZATION
Project: PROJECT-ANTIGRAVITY-INTEGRATION
Work Item: WI-3349
target_paths: ["scripts/verify_antigravity_dispatch.py", "platform_tests/scripts/test_verify_antigravity_dispatch.py", "platform_tests/scripts/fixtures/antigravity-dispatch/sentinel-lo-review-prompt.txt", "memory/antigravity-integration-status.md", "harness-state/harness-registry.json", "groundtruth.db"]
Recommended commit type: feat:

## Response To NO-GO -008

Codex's NO-GO at `-008` correctly identified that the post-implementation report's live substrate evidence cannot be reproduced in the Codex auto-dispatch context because `gemini` is not resolvable on PATH there. Codex's line 137 articulated three architectural-fix paths:

> 2. Decide whether the durable harness registry should store a resolvable command path, whether dispatch startup should provide the required PATH, or whether the verifier should emit a clearer prerequisite failure before spawning.

**Owner decision via AskUserQuestion S364 (2026-05-28)**: Owner selected **Option A: registry stores absolute path**. The durable harness registry will store a resolvable absolute command path for harness C; the verifier reads from registry and uses the absolute path directly, bypassing PATH-based resolution.

This REVISED-9 changes the architectural framing from "PATH-based resolution with PATHEXT fix" (REVISED-3's approach implemented in -007) to "registry-stored absolute path". The implementation work itself is small — extend the registry schema with a `command_path` field; update verifier to prefer registry-provided absolute path. But the architecture-direction change is substantive enough to require a re-proposal with Codex re-review.

The S364 AUQ answer is the durable owner-decision evidence; it will be captured as a Deliberation Archive record (`DELIB-S364-GEMINI-SUBSTRATE-REGISTRY-PATH`) following standard owner-decision capture procedure.

## Summary

WI-3349 is end-to-end verification of the Gemini CLI headless dispatch substrate. The substrate is the path by which the cross-harness event-driven trigger can dispatch Gemini-hosted Loyal-Opposition reviews. The original proposal at `-003` (Codex GO at `-004`) approved a substrate-launch verifier; the implementation at `-005` succeeded with PATH+PATHEXT resolution on the developer workstation but failed at `-006` review because Codex's auto-dispatch context lacked PATH coverage for `gemini.CMD`. REVISED-7 implementation at `-007` added a PATHEXT-aware `shutil.which()` resolution; this passed on the developer workstation but still failed at Codex review at `-008` because Codex's auto-dispatch PATH does not include the npm-global directory at all.

The owner-selected fix (Option A from S364 AUQ): store the absolute command path in `harness-state/harness-registry.json` as a new `command_path` field within `invocation_surfaces.headless`. The verifier prefers this path when present; falls back to `shutil.which()` when absent. This decouples substrate verification from PATH-environment differences between developer workstations and Codex's auto-dispatch context.

## Specification Links

Carried forward from `-003` (unchanged):

- `REQ-HARNESS-REGISTRY-001` - governs the deterministic CLI-driven harness registry that the verification exercises.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v2 - records the harness-registry architecture and per-harness `invocation_surfaces.headless.argv` template.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - constrains role assignment; verification preserves harness C as `role = []`.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3 - hook-independent verification path.
- `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - shared spawn substrate.

Standard governance specs (cited):

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol; this REVISED proceeds through file bridge.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - all target paths in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this REVISED cites governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - spec-to-test mapping below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project Authorization + Project + WI declared above.
- `GOV-STANDING-BACKLOG-001` - WI-3349 is the master backlog item under PROJECT-ANTIGRAVITY-INTEGRATION.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - harness registry is canonical governance artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - registry schema extension preserves traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3349 advances through implementation lifecycle.
- `SPEC-AUQ-POLICY-ENGINE-001` - owner decision captured via AskUserQuestion S364.

## Requirement Sufficiency

Existing requirements sufficient with one minor extension. `REQ-HARNESS-REGISTRY-001` already governs the registry schema; this REVISED-9 extends the schema with a new optional `command_path` field. The extension is forward-compatible (existing harness records without `command_path` continue to work via the `shutil.which()` fallback). No new SPEC creation is required; the schema extension is a natural extension of the existing requirement under the chat-derived-spec-approval workflow per `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` should the owner choose to formalize the schema change.

## KB Mutation Scope

This REVISED-9 will require **MemBase mutation** to the `harnesses` table (one row insertion for the harness C update). PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-... has `allowed_mutation_classes=None` (no class constraint; permits the harness-table update).

Mutation will:
1. Insert new version of harness C record adding `command_path` to `invocation_surfaces.headless`.
2. Regenerate `harness-state/harness-registry.json` projection via the existing `groundtruth_kb.harness_projection` regeneration path.

The regeneration is deterministic; the projection file contents will match the MemBase source-of-truth.

## WI Citation Disclosure

This REVISED-9 declares implementation work for WI-3349 only. No other WI is implicated.

## Prior Deliberations

- `bridge/gtkb-headless-gemini-lo-dispatch-verification-001.md` (NEW): originating proposal.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-002.md` (Codex NO-GO): early review.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-003.md` (REVISED proposal): approved scope.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-004.md` (Codex GO on REVISED-3).
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-005.md` (NEW post-impl).
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-006.md` (Codex NO-GO on -005): substrate launch failure.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-007.md` (REVISED post-impl): PATHEXT fix; passed on workstation.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-008.md` (Codex NO-GO on -007): substrate still fails in auto-dispatch PATH context; three architectural-fix paths articulated.
- **S364 AskUserQuestion answer (2026-05-28)**: Owner selected Option A (registry stores absolute path) from three architectural-fix options. To be captured as `DELIB-S364-GEMINI-SUBSTRATE-REGISTRY-PATH`.
- Original WI-3349 backlog capture under PROJECT-ANTIGRAVITY-INTEGRATION; PAUTH active.

## Owner Decisions / Input

- **S364 AskUserQuestion answer (2026-05-28)**: Owner selected "Registry stores absolute path" from three architectural-fix options for the headless Gemini substrate resolution problem. This authorizes the architectural change in this REVISED-9.
- **Prior owner authorizations preserved**: PAUTH-PROJECT-ANTIGRAVITY-INTEGRATION-... active; covers PROJECT-ANTIGRAVITY-INTEGRATION work including this WI-3349 implementation.

No additional owner decisions required for this REVISED-9. The S364 AUQ answer is the load-bearing owner-decision evidence; downstream design choices (e.g., schema field name, fallback ordering) are implementation details Prime Builder can resolve within the architectural framing.

## Architectural Change

### Before (REVISED-3 approved scope, REVISED-7 implementation)

- `harness-state/harness-registry.json` stores `invocation_surfaces.headless.argv: ["gemini", "-p", "{{PROMPT}}", "--approval-mode=yolo"]`.
- Verifier renders argv via `_harness_command()` substituting `{{PROMPT}}`.
- Verifier calls `shutil.which(argv[0])` to resolve `gemini` (with PATHEXT) and substitutes the resolved path before `subprocess.run()`.
- Substrate resolution relies on environment PATH.
- Failure mode: in environments where PATH does not include the npm-global directory (e.g., Codex auto-dispatch context), `shutil.which()` returns None and subprocess launch fails with WinError 2.

### After (REVISED-9 proposed scope)

- `harness-state/harness-registry.json` stores `invocation_surfaces.headless.argv: ["gemini", "-p", "{{PROMPT}}", "--approval-mode=yolo"]` AND `invocation_surfaces.headless.command_path: "C:\\Users\\micha\\AppData\\Roaming\\npm\\gemini.CMD"` (or platform-specific absolute path).
- Verifier renders argv via `_harness_command()` substituting `{{PROMPT}}`.
- New resolution priority:
  1. If `command_path` is present in the harness record, use it directly as argv[0].
  2. Else fall back to `shutil.which(argv[0])` (existing behavior).
  3. Else raise `VerificationError` with a clear prerequisite-failure diagnostic.
- Substrate resolution is independent of PATH when `command_path` is set.
- Per-workstation paths can be set in MemBase at install/setup time; do not require shell-environment coverage in headless contexts.

## Implementation Plan

### 1. MemBase harness-table update

Insert new version of harness C record with extended `invocation_surfaces.headless`:

```json
{
  "id": "C",
  "harness_name": "antigravity",
  "harness_type": "antigravity",
  "version": 3,
  "invocation_surfaces": {
    "headless": {
      "argv": ["gemini", "-p", "{{PROMPT}}", "--approval-mode=yolo"],
      "command_path": "C:\\Users\\micha\\AppData\\Roaming\\npm\\gemini.CMD"
    },
    "interactive": {
      "kind": "ide",
      "name": "Antigravity IDE"
    }
  },
  "role": [],
  "status": "registered",
  "changed_by": "prime-builder/claude/B",
  "change_reason": "S364 AUQ: add command_path field per registry-stored-absolute-path architectural choice (DELIB-S364-GEMINI-SUBSTRATE-REGISTRY-PATH)"
}
```

### 2. Registry projection regeneration

Invoke `groundtruth_kb.harness_projection.regenerate()` (or equivalent path used by existing tests / CLI). Result: `harness-state/harness-registry.json` is updated; harness C record now includes `command_path`.

### 3. Verifier script update

In `scripts/verify_antigravity_dispatch.py`, replace the current `shutil.which()`-only resolution with priority-ordered resolution:

```python
def _resolve_executable_for_host(project_root: Path, record: dict, argv: list[str]) -> str:
    """Resolve argv[0] to an absolute executable path.

    Priority:
    1. record['invocation_surfaces']['headless']['command_path'] if present
       (registry-stored absolute path; preferred per S364 owner decision).
    2. shutil.which(argv[0]) (PATH-based fallback for environments where
       the registry does not yet declare command_path).
    3. Raise VerificationError with a structured prerequisite-failure diagnostic.
    """
    surfaces = record.get("invocation_surfaces", {})
    headless = surfaces.get("headless", {}) if isinstance(surfaces, dict) else {}
    command_path = headless.get("command_path") if isinstance(headless, dict) else None
    if command_path:
        path = Path(command_path)
        if path.is_file():
            return str(path)
        # Configured but not present; this is a setup error.
        raise VerificationError(
            f"registry-configured command_path is not a file: {command_path}"
        )
    # Fallback to PATH-based resolution.
    resolved = shutil.which(argv[0])
    if resolved:
        return resolved
    raise VerificationError(
        f"command {argv[0]!r} not resolvable: no registry command_path, and shutil.which returned None. "
        "Set invocation_surfaces.headless.command_path in MemBase harnesses table for this harness."
    )
```

### 4. Test updates

In `platform_tests/scripts/test_verify_antigravity_dispatch.py`, add tests:

- `test_resolution_uses_registry_command_path`: verifies that when a harness record has `command_path`, the verifier uses it directly (mocks the path as existing).
- `test_resolution_falls_back_to_path_when_no_command_path`: verifies that absent `command_path`, `shutil.which()` is consulted (existing behavior).
- `test_resolution_raises_when_command_path_configured_but_missing`: verifies that a configured-but-missing `command_path` raises `VerificationError`.
- `test_resolution_raises_when_no_command_path_and_no_path_resolution`: verifies the no-path / no-resolution error mode produces the structured prerequisite-failure message.

### 5. Live verification rerun

Run `python scripts/verify_antigravity_dispatch.py --recipient C --prompt-fixture platform_tests/scripts/fixtures/antigravity-dispatch/sentinel-lo-review-prompt.txt --timeout 15 --json` after the registry + verifier updates land. Expected: `substrate_ok: true`, `resolution_applied: true`, `resolved_argv[0]: "C:\\Users\\micha\\AppData\\Roaming\\npm\\gemini.CMD"`. Codex's auto-dispatch context should produce the same result.

### 6. Post-impl report

File post-impl report at `bridge/gtkb-headless-gemini-lo-dispatch-verification-NNN.md` (next NEW version) with:
- All test results (existing 10 + new 4 = 14 tests, all PASS).
- Live verification rerun output showing `substrate_ok: true`.
- Codex's expected re-verification in auto-dispatch context.

## Spec-to-Test Mapping

| Specification | Verification Command Or Artifact | Expected Result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | This REVISED-9 filed at `bridge/gtkb-headless-gemini-lo-dispatch-verification-009.md`; INDEX updated. | PASS — bridge protocol observed. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | All target paths within `E:\GT-KB`. | PASS — all in-root. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-headless-gemini-lo-dispatch-verification`. | PASS expected. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | This mapping with expected results; post-impl report will record observed results. | PASS — mapping present. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Project Authorization + Project + Work Item declared in header; PAUTH active. | PASS. |
| `REQ-HARNESS-REGISTRY-001` | Schema extension forward-compatible; registry projection regenerates from MemBase source-of-truth. | PASS at post-implementation review. |
| `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v2 | `invocation_surfaces.headless.argv` template preserved; `command_path` is a new optional sibling field. | PASS — no breaking change. |
| `GOV-HARNESS-ROLE-PORTABILITY-001` | Harness C `role = []` preserved across registry update. | PASS — role field unchanged. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` v3 | Verification path is hook-independent; command_path resolution is a Python-level concern. | PASS. |
| `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` | Shared spawn substrate unaffected; only the executable-resolution mechanism changes. | PASS. |
| `SPEC-AUQ-POLICY-ENGINE-001` | S364 AUQ answer is the load-bearing owner decision; recorded above + to-be-captured as DELIB. | PASS — AUQ used; no prose decision-asks. |
| `GOV-STANDING-BACKLOG-001` | WI-3349 master active under PROJECT-ANTIGRAVITY-INTEGRATION. | PASS — already confirmed in prior thread versions. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` + `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` + `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Implementation produces tracked changes to script + tests + fixture + registry projection + harnesses table version row. | PASS. |
| `GOV-CHAT-DERIVED-SPEC-APPROVAL-001` | Schema extension is candidate-spec territory; if owner formalizes, it goes through the standard chat-derived spec approval workflow. | PASS — not promoted to formal spec by this REVISED. |

## Acceptance Criteria

- [ ] Codex returns GO on this REVISED-9 proposal.
- [ ] Harness C record in MemBase `harnesses` table is updated with `command_path` field.
- [ ] `harness-state/harness-registry.json` is regenerated; harness C record contains `command_path: "C:\\Users\\micha\\AppData\\Roaming\\npm\\gemini.CMD"`.
- [ ] `scripts/verify_antigravity_dispatch.py` implements priority-ordered resolution (registry command_path → shutil.which() fallback → VerificationError).
- [ ] `platform_tests/scripts/test_verify_antigravity_dispatch.py` includes 4 new tests covering the command_path resolution paths.
- [ ] All 14 tests PASS via `python -m pytest platform_tests/scripts/test_verify_antigravity_dispatch.py -q`.
- [ ] Live verification rerun shows `substrate_ok: true` with `resolved_argv[0]` matching the registry-stored absolute path.
- [ ] Codex returns VERIFIED on the post-implementation report.

## Risk and Rollback

Risk: low. The schema extension is forward-compatible. Existing harnesses without `command_path` continue to work via the fallback path. The verifier change is additive (new resolution priority); existing tests should continue to PASS.

Risks identified:
- **Per-workstation paths in registry**: The registry now contains workstation-specific paths. Mitigation: this is consistent with the registry's role as a per-workstation hot-path projection of MemBase; multi-workstation deployments would set platform-specific `command_path` values per workstation. Future schema iteration could introduce a `command_path_per_platform` mapping if multi-platform deployment becomes common.
- **MemBase migration safety**: The MemBase update is append-only via `insert_harness()` (or equivalent). Existing harness C version 2 row is preserved; the new version 3 row adds the field.

Rollback: revert verifier to PATH-only resolution; revert harness C MemBase row to version 2 state (insert a new version with command_path=null). Registry projection regenerates accordingly.

## Files Touched (target_paths recap)

- `scripts/verify_antigravity_dispatch.py` (modified; add registry-path-priority resolution)
- `platform_tests/scripts/test_verify_antigravity_dispatch.py` (modified; add 4 new tests)
- `platform_tests/scripts/fixtures/antigravity-dispatch/sentinel-lo-review-prompt.txt` (preserved; unchanged from -007)
- `memory/antigravity-integration-status.md` (modified; document architectural change)
- `harness-state/harness-registry.json` (regenerated; harness C record extended)
- `groundtruth.db` (mutating: new harness C version row in `harnesses` table)

Bridge filing artifacts:
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-009.md` (this file)
- `bridge/INDEX.md` (entry update)
- Next post-impl report (at `-NNN`)

## Loyal Opposition Asks

1. Confirm the architectural change to "registry-stored absolute command path" is consistent with `REQ-HARNESS-REGISTRY-001` and `ADR-SINGLE-HARNESS-OPERATING-MODE-001` v2's `invocation_surfaces.headless` schema, or NO-GO with specific schema-compatibility concerns.
2. Verify the priority-ordered resolution (command_path → shutil.which() → VerificationError) is the right precedence, or recommend an alternative ordering.
3. Confirm the schema extension (adding `command_path` sibling to `argv` under `invocation_surfaces.headless`) is forward-compatible with existing harness records (A=codex, B=claude have no `command_path` and should continue working), or recommend an alternative schema approach.
4. Verify that the S364 owner decision (registry-stored absolute path) is captured per the AUQ-only enforcement stack, or recommend additional DA-record capture work.
5. Verify the target_paths expansion (adding `harness-state/harness-registry.json` + `groundtruth.db`) is appropriately scoped, or recommend reduction.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
