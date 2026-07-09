NEW

# gtkb-platform-tests-ruff-recleanup — Re-clean regressed ruff E,F violations in platform_tests (Lint CI gate red on main)

bridge_kind: prime_proposal
Document: gtkb-platform-tests-ruff-recleanup
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-09 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: f2a9adc9-78e8-4333-9d55-70f0b30d0fba
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code interactive; resolved role prime-builder via ::init gtkb pb

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-5099

target_paths: ["platform_tests/groundtruth_kb/governance/test_push_preflight.py", "platform_tests/hooks/test_bridge_axis_2_role_aware.py", "platform_tests/hooks/test_bridge_compliance_gate_finalization_evidence.py", "platform_tests/scripts/conftest.py", "platform_tests/scripts/test_claude_session_start_dispatcher.py", "platform_tests/scripts/test_codex_session_start_dispatcher.py", "platform_tests/scripts/test_fab09_safety_gate_registration.py", "platform_tests/scripts/test_fab14_directive_hook_coverage.py", "platform_tests/scripts/test_governing_specs_preserved.py", "platform_tests/scripts/test_gtkb_scoped_client.py", "platform_tests/scripts/test_ops_activity_context.py", "platform_tests/scripts/test_repair_codex_dotdir_acl.py", "platform_tests/scripts/test_single_harness_dispatcher_task_installer.py", "platform_tests/scripts/test_spec_coherence_cli.py", "platform_tests/scripts/test_work_intent_auto_extend.py", "platform_tests/scripts/test_worker_packet_authorization_envelope.py", "platform_tests/skills/test_auto_retire_actuation_helper_parity.py", "platform_tests/skills/test_verified_finalization_validation_hardening.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

A GitHub operations sweep of the platform repo (`Remaker-Digital/groundtruth-kb`) on 2026-07-09 found the `Lint` CI workflow failing on `main` (last push 2026-07-01), with all 21 open PRs inheriting that red because they build against a broken base. Root cause: 25 ruff `E,F` violations have regressed into `platform_tests/` across 18 files — 14 `E501` (line-too-long), 9 `E741` (ambiguous variable name `l`), 1 `E402` (module import not at top of file), and 1 `F821` (undefined name `Any` in `platform_tests/hooks/test_bridge_axis_2_role_aware.py:80`). The CI Lint step runs `ruff check applications/Agent_Red/src/ platform_tests/ --select E,F` and fails on exactly these.

This proposal is a reliability fast-lane re-clean (per `GOV-RELIABILITY-FAST-LANE-001`) that fixes all 25 violations in the 18 listed test files so the Lint gate returns to green. Twenty-four fixes are mechanical (wrap long lines to <= 120; rename the ambiguous `l` variables; move the misplaced import to the top of its file). The remaining fix is a genuine correctness repair: `test_bridge_axis_2_role_aware.py` references the `Any` type name without importing it (`F821`), a real defect independent of style — the fix adds `from typing import Any`, which also resolves the paired `E402` in the same file.

This is a **regression** of previously-VERIFIED work: `WI-3423` / bridge thread `gtkb-platform-tests-ruff-cleanup` (14 versions, VERIFIED — `DELIB-20261887`) cleaned `platform_tests/` to zero `E,F` violations. The violations recurred because the `Lint` check is not a **required** branch-protection check, so non-compliant test files merged past the advisory-red gate. The durable fix — promoting `Lint` to a required check — is out of scope for this fast-lane re-clean and is captured separately (see Owner Decisions / Input). This proposal restores the green baseline; the gate-hardening prevents the next recurrence.

## Specification Links

- `GOV-RELIABILITY-FAST-LANE-001` — governs this proposal's fast-lane eligibility: a small, low-risk, test-only defect fix authorized under the reliability fast-lane standing authorization by project membership.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — governs the bridge audit trail and the append-only numbered-file discipline this proposal is filed under.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — requires this proposal to cite all governing specifications (satisfied by this section).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — requires Project / PAUTH / Work-Item linkage (satisfied by the metadata block: `PROJECT-GTKB-RELIABILITY-FIXES` / `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` / `WI-5099`).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — governs the verification gate: verification derives from the requirement that `ruff check --select E,F` over the CI paths reports zero errors (see Spec-Derived Verification Plan).
- `GOV-STANDING-BACKLOG-001` — governs `WI-5099` as the tracked backlog authority for this work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — the platform/application isolation-placement boundary. This proposal **complies by construction**: all 18 `target_paths` are under `platform_tests/` (platform scope); no `applications/Agent_Red/` file is created, modified, or required. The `applications/Agent_Red/src/` reference in the Summary and Verification Plan is only the CI Lint step's read-only scan scope (already clean there, zero `E,F` violations) — a path argument, not a mutation target.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — the work is captured as a durable artifact (`WI-5099`) with a bridge audit trail rather than transient chat.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — this proposal preserves the fix as a governed artifact network (WI -> bridge proposal -> verification) per artifact-oriented governance.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — the regression triggers the defect/regression lifecycle: a new work item (`WI-5099`, origin `regression`) plus this implementation proposal.

## Prior Deliberations

- `DELIB-20261887` — bridge thread `gtkb-platform-tests-ruff-cleanup` (14 versions, VERIFIED; `WI-3423`). **This proposal is a regression of that VERIFIED cleanup.** It applies the same class of fix (ruff `E,F` compliance in `platform_tests/`) to violations that recurred after that thread verified a zero-violation baseline. It does not revisit a rejected approach — it re-establishes an accepted one and identifies why it decayed (the Lint check is advisory, not required).
- `DELIB-20266486` — per-artifact approval creating `PAUTH-WI-3423-PLATFORM-TESTS-RUFF-001` for the original cleanup. Cited to show the prior cleanup's authorization lineage; this proposal instead relies on the project-membership standing authorization rather than a new per-fix PAUTH.
- `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION` — owner decision establishing the reliability fast-lane and the standing authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` that authorizes this WI by project membership.

## Owner Decisions / Input

Implementation authorization is provided by the reliability fast-lane **standing** authorization `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` (owner decision `DELIB-S351-RELIABILITY-FAST-LANE-DIRECTION`), which covers work items by active `PROJECT-GTKB-RELIABILITY-FIXES` membership with no per-fix authorization. `WI-5099` is an active member of that project.

In-session owner input (2026-07-09, this Prime Builder session): the owner authorized filing this proposal via `AskUserQuestion`, selecting "Draft Lint fix proposal" as the next step after the GitHub ops sweep diagnosis. Scope was explicitly filing-only — the proposal still requires Loyal Opposition `GO` before any implementation.

No further owner decision blocks review. The durable gate-hardening follow-on (make `Lint` a required branch-protection check) is a separate backlog item to be captured; it is NOT authorized or requested by this proposal.

## Requirement Sufficiency

Existing requirements sufficient. The governing requirement — that `platform_tests/` (and `applications/Agent_Red/src/`) pass `ruff check --select E,F` — is already established by the CI `Lint` workflow and the previously-VERIFIED `WI-3423` baseline (`DELIB-20261887`). No new or revised requirement is needed; this proposal restores compliance with an existing requirement. Fast-lane eligibility is governed by `GOV-RELIABILITY-FAST-LANE-001`.

## Spec-Derived Verification Plan

Verification derives from the linked requirement (zero `E,F` violations over the CI paths) per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`:

1. Lint gate (primary acceptance) — reproduces the failing CI step; expect **zero** errors after the fix:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check applications/Agent_Red/src/ platform_tests/ --select E,F
```

2. Format gate — the separate `ruff format --check` gate that CI and Loyal Opposition also enforce; expect no reformat on the 18 `target_paths` files:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check <the 18 target_paths files>
```

3. Behavior preservation — the touched files are tests; confirm they still collect and pass, especially `platform_tests/hooks/test_bridge_axis_2_role_aware.py` after the `from typing import Any` import fix resolves the `F821`:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest <the touched test files> -q --no-header
```

Expected result: (1) exits 0 with no violations; (2) reports all 18 files already formatted; (3) all touched tests collect and pass. Any remaining `E,F` violation, or any touched test failing to collect/pass, is a NO-GO.

## Risk / Rollback

Risk surface is minimal and contained: changes are confined to 18 `platform_tests/` test files — no production/source module, no governance rule, no bridge protocol, no KB mutation (`kb_mutation_in_scope: false`, `implementation_scope: source`). The `E501`/`E741`/`E402` fixes are non-semantic (line wrapping, variable rename, import relocation); the single semantic change (adding `from typing import Any`) makes a previously-undefined name resolvable and can only fix, not regress, behavior. Rollback is a single `git revert` of the one implementing commit; because the scope is test-only, revert cannot affect platform runtime behavior.

## Bridge Filing

This proposal is filed under `bridge/` as the next status-bearing numbered
bridge file for `gtkb-platform-tests-ruff-recleanup`; no prior version is deleted or rewritten
(append-only). Dispatcher/TAFE state plus the numbered file chain are the live
workflow state per `GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix` — repairs the failing `Lint` CI gate (`E501`/`E741`/`E402` compliance) and a genuine `F821` undefined-name defect in a test module. The change adds no new capability and is not a pure formatting-only style change (the `F821`/`E402` are correctness / import-hygiene repairs), so `fix:` is more accurate than `style:` or `test:`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
