NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-30-ruff-format-pre-file-gate-post-impl
author_model: claude-opus-4-8
author_model_version: 4.8-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3473
Implements: WI-3473

# Post-Implementation Report - Catch `ruff format --check` pre-file: active-hook guardrail + rule-based checklist (WI-3473)

bridge_kind: implementation_report
Document: gtkb-ruff-format-pre-file-gate
Version: 009 (NEW post-impl, requesting VERIFIED)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-30 UTC
Session: S372
Implements GO: bridge/gtkb-ruff-format-pre-file-gate-008.md
Recommended commit type: feat:

target_paths: ["scripts/check_ruff_format.py", ".githooks/pre-commit", ".claude/rules/file-bridge-protocol.md", ".groundtruth/formal-artifact-approvals/2026-05-30-claude-rules-file-bridge-protocol-md.json", "platform_tests/scripts/test_check_ruff_format.py"]

## Summary

Implemented WI-3473 per GO@-008. Two halves of the owner's "Both" design:

1. **Mechanical guardrail** — `scripts/check_ruff_format.py` (stdlib-only; deterministic venv-first ruff resolver) wired into the ACTIVE `.githooks/pre-commit` (after the narrative-evidence check). Blocks any commit whose staged Python is unformatted.
2. **Pre-file checklist** — a "Pre-File Code-Quality Gates" subsection added to `.claude/rules/file-bridge-protocol.md`'s Mandatory Specification-Derived Verification Gate (owner-approved narrative-artifact packet), instructing Prime to run BOTH `ruff check` and `ruff format --check` before filing a post-impl report.

No `.codex/skills/*`, `.codex/skills/MANIFEST.json`, or `config/agent-control/harness-capability-registry.toml` were touched (the REVISED-3 redirection that avoided the adapter-machinery drift). Confirmed by `git status` (V7).

## Owner Decisions / Input

- **S372 AUQ #1** = "Start WI-3473"; **#2** = "Both: guardrail + checklist"; **#3** = "Checklist in file-bridge-protocol rule"; **#4** = "Approve as shown" on the narrative packet (rule content + sha256 `ab2bb0d5...e97d5` presented before the protected write). The packet records `approved_by: owner`, `presented_to_user: true`, `transcript_captured: true`.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — guardrail/test/hook half covered by the standing PAUTH via WI-3473 membership (origin=defect).
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec links carried forward.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping with actual results below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project Authorization + Project + Work Item header present.
- `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` — the protected rule edit is authorized by the owner-approved narrative packet.
- `config/governance/narrative-artifact-approval.toml` — protected registry + Slice C evidence floor (`check_narrative_artifact_evidence.py`).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` / `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — standing PAUTH for the source/hook/test half.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all paths in-root; no `applications/**`.
- `GOV-STANDING-BACKLOG-001` — WI-3473 active under PROJECT-GTKB-RELIABILITY-FIXES.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic guardrail (subprocess + deterministic resolver; no LLM).
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — (advisory) durable governance artifacts; WI-3473 lifecycle advances.

## Requirement Sufficiency

Existing requirements sufficient. The standard (`ruff format`) already exists; this added the missing pre-file (rule) + commit-time (active hook) enforcement points. No new GOV/SPEC/ADR/DCL.

## WI Citation Disclosure

Declares work for **WI-3473** only.

## Prior Deliberations

- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — standing reliability fast-lane.
- `bridge/gtkb-ruff-format-pre-file-gate-002/-004/-006.md` (Codex NO-GOs) — the findings closed across REVISED-2/-3/-4 (active hook, venv resolver, advisory specs, generator output set, packet CLI fields).
- `bridge/gtkb-ruff-format-pre-file-gate-008.md` (Codex GO) — the GO this report implements.
- `bridge/gtkb-root-boundary-external-harness-exec-exception-006/-007.md` — narrative-packet workflow precedent (followed here).
- `bridge/gtkb-implements-link-backfill-phase2-implementation-004/-006.md` — the formatter-gate NO-GO that motivated WI-3473.

## Spec-to-Test Mapping (Actual Results)

| Specification / Behavior | Test / Verification | Result |
|---|---|---|
| Guardrail PASS when staged Python formatted | `test_main_passes_on_formatted`, `test_check_files_passes_on_formatted` | PASS |
| Guardrail FAIL (exit 1) when unformatted | `test_main_blocks_unformatted`, `test_check_files_fails_on_unformatted` | PASS |
| No-op PASS when no Python staged | `test_main_passes_when_no_python_staged` | PASS |
| Non-Python ignored | `test_main_ignores_non_python`, `test_staged_python_files_filters_to_py` | PASS |
| F2: deterministic venv-first resolution (no fail-open) | `test_resolve_ruff_prefers_venv` | PASS |
| F2: WARN/FAIL boundary gated on venv presence | `test_venv_python_presence_boundary` | PASS |
| Active `.githooks/pre-commit` blocks unformatted in THIS checkout | V6 dry-run | PASS |
| `GOV-ARTIFACT-APPROVAL-001` rule edit authorized | V4 packet generated + validated; sha matches owner-approved | PASS |
| -006 F1: packet carries required fields | V4 `--validate-after --json` fields | PASS |
| Slice C narrative-evidence floor | V5 `check_narrative_artifact_evidence.py --staged` | PASS |
| Dogfood: new files pass ruff check + format | V3 | PASS |
| No adapter/manifest/registry touched | V7 `git status` | PASS |

`9 passed` (`python -m pytest platform_tests/scripts/test_check_ruff_format.py -q`).

## Verification Evidence

### V1. Implementation-start packet (from GO@-008)

```
python scripts/implementation_authorization.py begin --bridge-id gtkb-ruff-format-pre-file-gate
```
`latest_status: GO`, `go_file: -008`, PAUTH `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING`, 5 target_paths, `expires_at: 2026-05-30T13:34:09Z`.

### V2. Tests

```
python -m pytest platform_tests/scripts/test_check_ruff_format.py -q --tb=short
=> 9 passed
```

### V3. Dogfood ruff (the fix's own files pass the gate it installs)

```
python -m ruff check scripts/check_ruff_format.py platform_tests/scripts/test_check_ruff_format.py
=> All checks passed!
python -m ruff format --check scripts/check_ruff_format.py platform_tests/scripts/test_check_ruff_format.py
=> 2 files already formatted
```
(The format gate initially flagged the test file as would-reformat; `ruff format` was run and the file re-checked clean — the new gate caught its own artifact.)

### V4. Narrative-artifact approval packet (owner-approved; post-edit content)

```
python -m groundtruth_kb generate-approval-packet --kind narrative \
  --target .claude/rules/file-bridge-protocol.md \
  --artifact-id claude-rules-file-bridge-protocol-md --action update \
  --source-ref bridge/gtkb-ruff-format-pre-file-gate-008.md \
  --explicit-change-request "<owner-visible change text>" \
  --change-reason "bridge/gtkb-ruff-format-pre-file-gate-008.md" \
  --approval-mode approve --changed-by claude-prime-builder \
  --out .groundtruth/formal-artifact-approvals/2026-05-30-claude-rules-file-bridge-protocol-md.json \
  --validate-after --json
```
Result (packet validated):
- `artifact_type: narrative_artifact`
- `target_path: .claude/rules/file-bridge-protocol.md`
- `action: update`, `approval_mode: approve`, `approved_by: owner`
- `full_content_sha256: ab2bb0d5c50a74402f44fda13b8f341a72990ac91fe7d72b188202b3b54e97d5` (matches the owner-approved sha presented via AskUserQuestion)
- `explicit_change_request` non-empty (391 chars), `change_reason: bridge/gtkb-ruff-format-pre-file-gate-008.md`
- `presented_to_user: true`, `transcript_captured: true`

Order note: the packet was first generated before the on-disk edit (captured pre-edit content, sha `73ac55eb...`); that mis-generation was deleted, the approved post-edit content written to disk, and the packet regenerated so `full_content_sha256` matches the owner-approved value (the correct write-then-generate order per the root-boundary precedent).

### V5. Slice C narrative-evidence floor

```
git add .claude/rules/file-bridge-protocol.md
python scripts/check_narrative_artifact_evidence.py --staged
=> PASS narrative-artifact evidence (1 cleared)
```

### V6. Active-hook dry-run (THIS checkout)

The full `.githooks/pre-commit` was run (`bash .githooks/pre-commit`) and confirmed to execute its check chain (secret scan, inventory-drift, narrative-evidence). The ruff guardrail step — the exact line the hook invokes, `python scripts/check_ruff_format.py --staged` — was demonstrated against real staging:

```
# unformatted staged .py:
[FAIL] ruff format: staged Python file(s) would be reformatted:
Would reformat: _ruffgate_demo.py
  Remedy: run  ruff format _ruffgate_demo.py
STEP_EXIT=1

# formatted staged .py:
[PASS] ruff format: 1 staged Python file(s) formatted
STEP_EXIT=0
```
Throwaway demo file cleaned up (`git restore --staged` + `rm`); no residue.

### V7. No forbidden paths; changed-file set

```
git status --short -- <5 target paths>
M  .claude/rules/file-bridge-protocol.md
 M .githooks/pre-commit
?? platform_tests/scripts/test_check_ruff_format.py
?? scripts/check_ruff_format.py
git status --short -- .codex/skills/bridge/SKILL.md .codex/skills/MANIFEST.json config/agent-control/harness-capability-registry.toml
=> (empty — none touched)
```
The narrative packet exists at `.groundtruth/formal-artifact-approvals/2026-05-30-claude-rules-file-bridge-protocol-md.json` (gitignored local evidence).

## Files Changed

| Path | Kind | In target_paths? |
|---|---|---|
| `scripts/check_ruff_format.py` | new (stdlib guardrail + venv-first resolver) | YES |
| `.githooks/pre-commit` | edit (added ruff-format guardrail invocation) | YES |
| `.claude/rules/file-bridge-protocol.md` | edit (Pre-File Code-Quality Gates subsection; narrative-packet authorized) | YES |
| `platform_tests/scripts/test_check_ruff_format.py` | new (9 tests) | YES |
| `.groundtruth/formal-artifact-approvals/2026-05-30-claude-rules-file-bridge-protocol-md.json` | new (narrative packet; gitignored) | YES |

## Commit-Time Consideration (disclosed)

The full `.githooks/pre-commit` run blocked at the inventory-drift check on the staged `.claude/rules/file-bridge-protocol.md` with `role-and-governance-rules requires governance_review` (the `config/governance/protected-artifact-inventory-drift.toml` gate). This is a SEPARATE commit-time governance gate for the rule edit, distinct from the ruff guardrail. At commit time (post-VERIFIED), Prime will satisfy it via the documented governance-review evidence path (the narrative packet + Slice C evidence are present; if the drift gate requires additional review evidence, Prime will provide it before committing the rule file). Flagged here for transparency; it does not affect the ruff guardrail's correctness.

## Acceptance Criteria Check

| Criterion | Status | Evidence |
|---|---|---|
| Codex GO on REVISED-4 | DONE | -008 |
| Impl-start packet activated | DONE | V1 |
| Owner-approved narrative packet (content + sha256; validates) | DONE | V4 |
| IP-1..IP-4 landed; tests + ruff check + format clean (dogfood); Slice C PASS | DONE | V2, V3, V5 |
| Active-hook dry-run blocks unformatted, passes formatted | DONE | V6 |
| No `.codex`/MANIFEST/registry touched | DONE | V7 |
| Post-impl report with evidence | DONE | this report |
| Codex VERIFIED | PENDING | this report |

## Risk and Rollback

Risk realized as low. Guardrail additive on the active hook; venv-first resolver (no fail-open). Protected-rule edit gated by owner packet + Slice C floor. No adapter machinery touched.

Rollback: revert the 4 source/hook/test/rule files (the `.githooks/pre-commit` + rule edits revert cleanly); delete the packet JSON (gitignored). No data/state to roll back.

## Loyal Opposition Asks

1. Confirm V6 satisfies the active-hook block/pass requirement (full hook executes; ruff step blocks unformatted / passes formatted via the exact hook invocation line; the inventory-drift block on the rule file is a separate commit-time gate, disclosed).
2. Confirm V4 packet (sha matches owner-approved; required fields present) + V5 Slice C PASS authorize the protected rule edit.
3. Confirm V7 shows no `.codex`/MANIFEST/registry drift (the REVISED-3 redirection held).
4. Note any spec to add to Specification Links.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
