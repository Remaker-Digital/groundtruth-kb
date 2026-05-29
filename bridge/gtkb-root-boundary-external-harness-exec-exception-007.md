NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-29-root-boundary-external-harness-exec-exception-post-impl
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Post-Implementation Report: External Harness Executable Root-Boundary Exception (007)

bridge_kind: implementation_report
Document: gtkb-root-boundary-external-harness-exec-exception
Version: 007 (NEW post-impl, requesting VERIFIED)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-29 UTC
Implements: WI-3434
Work Item: WI-3434
Project: PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY
Project Authorization: PAUTH-PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY-001
target_paths: [".claude/rules/project-root-boundary.md", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_external_harness_exec_boundary.py", ".groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json"]
Implements GO: bridge/gtkb-root-boundary-external-harness-exec-exception-006.md
Recommended commit type: feat:

## Summary

Implemented the bounded External Harness Executable Resolution Exception per the GO'd proposal at -005 / GO at -006. The implementation comprises four artifacts:

1. **Rule amendment** (`.claude/rules/project-root-boundary.md`): inserted the new section "External Harness Executable Resolution Exception" immediately after "Sandbox Output Exception". The amendment text is byte-identical to the proposal -005 §"Proposed Amendment Text" block. The core directive for project artifacts is preserved verbatim; the bound is harness-specific and registry-enumerated.
2. **Narrative-artifact approval packet** (`.groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json`): created via `python -m groundtruth_kb generate-approval-packet --kind narrative` per the schema-aligned packet plan in -005. Owner-visible packet display + AskUserQuestion approval captured in the same session transcript before the protected Write.
3. **Doctor check** (`_check_external_harness_exec_boundary` in `groundtruth-kb/src/groundtruth_kb/project/doctor.py`): the deterministic bound enforcement. Loads the harness registry, AST-scans `scripts/cross_harness_bridge_trigger.py` and `scripts/verify_antigravity_dispatch.py` for literal `shutil.which` / `subprocess.{run,Popen,call,check_output,check_call}` invocations, classifies each literal command against the registry-enumerated allowed set, in-root Python toolchain, and in-root absolute paths. Registered in `run_doctor` immediately after `_check_cross_harness_trigger` under the `p.includes_bridge` block.
4. **Spec-derived tests** (`platform_tests/scripts/test_external_harness_exec_boundary.py`): four cases per proposal -005 §"Implementation Plan" item 5 — (a) PASS on registry-enumerated commands, (b) FAIL on synthetic non-harness literal subprocess call, (c) WARN on missing registry, (d) deterministic + read-only.

WI-3349 (headless Gemini LO dispatch verification) is scoped as a separate follow-on thread per proposal -005 §"Implementation Plan" item 8.

## Owner Decisions / Input

- **S366 AUQ (prior session)** = "Amend root-boundary rule (Recommended)". Captured durably as `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` (v1, owner_decision, owner-attributed). Authorized the protected-rule amendment with the bounded shape implemented in this report.
- **S372 AUQ (this session)** = "Approve as shown". Owner-visible display of the post-edit `.claude/rules/project-root-boundary.md` content (6,115 bytes, 91 lines, LF-normalized) + `full_content_sha256: 2d5506013dbaf77f72b6fa02cc9dd4eae64f480631989b504f978394f14fa5b8` was presented in the transcript before the protected Write. Owner answer mapped to `approval_mode: approve`. Captured in the resulting packet file at `.groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json` (fields `presented_to_user: true`, `transcript_captured: true`, `approved_by: owner`).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — root-boundary spec; core invariant preserved for project artifacts, bound is the deterministic doctor check.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this report carries forward the proposal's spec links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the doctor check + 4 spec-derived tests + Slice C evidence floor provide spec-to-test mapping.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — Project + Work Item + PAUTH declared in header.
- `GOV-STANDING-BACKLOG-001` — WI-3434 active under PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY.
- `GOV-ARTIFACT-APPROVAL-001`, `PB-ARTIFACT-APPROVAL-001`, `DCL-ARTIFACT-APPROVAL-HOOK-001` — protected narrative-artifact edit gated by approval packet.
- `config/governance/narrative-artifact-approval.toml` — protected narrative-artifact registry; pre-commit evidence floor.
- `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py` — live packet schema; packet fields validated by `validate_packet()`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — durable traceability from owner decision to rule amendment to doctor check to tests.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — WI-3434 lifecycle advance to implemented.
- `GOV-ENV-LOCAL-AUTHORITY-001` — resolution mechanism (b) cited in the amendment.
- `REQ-HARNESS-REGISTRY-001` — registry-enumerated harness command names sourced by the check.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001`, `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` — cross-harness dispatch substrate scope.
- `SPEC-AUQ-POLICY-ENGINE-001` — owner authorization via AskUserQuestion (S366 + S372).
- `GOV-20` — design-constraint enforcement pattern (deterministic doctor check).

## Requirement Sufficiency

Existing requirements sufficient. The owner decision (DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION) provides the requirement; this implementation realizes it as a bounded rule amendment + deterministic doctor check + 4 spec-derived tests. No new SPEC strictly required; the proposal noted a future DCL formalization is optional.

## WI Citation Disclosure

Declares work for **WI-3434** only (the External Harness Exec Boundary amendment scope per `PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY` and `PAUTH-PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY-001`).

`WI-3349` is referenced as **context only** (the downstream consumer that resumes verification of headless Gemini LO dispatch after this amendment lands VERIFIED; scoped as a separate follow-on thread per proposal -005 §"Implementation Plan" item 8). No source, test, or KB mutation in this report touches `WI-3349`'s implementation surface; the citation is the carry-forward continuity reference to the prior NO-GO chain that motivated the governance amendment.

## Prior Deliberations

- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` (v1): owner S366 AUQ decision authorizing the amendment shape. Load-bearing decision.
- `bridge/gtkb-root-boundary-external-harness-exec-exception-006.md` (Codex GO this thread): the GO that this report implements.
- `bridge/gtkb-root-boundary-external-harness-exec-exception-005.md` (Prime REVISED-2 this thread): the proposal text and Approval Packet Plan that this report executes.
- `bridge/gtkb-root-boundary-external-harness-exec-exception-004.md` (Codex NO-GO REVISED-1): the F1+F2 findings closed in -005.
- `bridge/gtkb-root-boundary-external-harness-exec-exception-002.md` (Codex NO-GO original): the P1-001 finding closed in REVISED-1.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-012.md` (Codex NO-GO): twice required either root-contained design or governance amendment; this amendment satisfies the latter.
- `DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT` (v1): the superseded mechanism-level decision; this amendment resolves at the governance level.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`: isolation/lifecycle framing the root-boundary rule serves; the amendment preserves it for project artifacts.

## Spec-to-Test Mapping (Actual Results)

| Specification | Verification | Command | Result |
|---|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | this report filed; INDEX updated after this report lands | `bridge/INDEX.md` update | PASS (post-Write) |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | rule amendment preserves project-artifact invariant verbatim; bound is deterministic doctor check | inspection of post-edit rule text | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | 4 spec-derived test cases (PASS/FAIL/WARN/determinism) | `python -m pytest platform_tests/scripts/test_external_harness_exec_boundary.py -v` | PASS (4/4) |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | header Project/WI/PAUTH lines present; PAUTH active | inspection of report header | PASS |
| `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` | approval packet generated via `generate-approval-packet --validate-after`; sha256 matches on-disk file | `python -m groundtruth_kb generate-approval-packet --kind narrative --validate-after --json` | PASS (packet validates; sha256 = 2d5506...4fa5b8 matches) |
| `config/governance/narrative-artifact-approval.toml` (Slice C pre-commit floor) | staged rule file evidence-checked against on-disk packet | `python scripts/check_narrative_artifact_evidence.py --staged` | PASS (1 cleared) |
| `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py` (live schema) | packet passes `validate_packet()` at write + read-back | `--validate-after` flag on CLI | PASS |
| External harness exec boundary (rule + doctor check) | doctor check registered + executes on current tree | `python -m groundtruth_kb project doctor` | PASS (`cross-harness exec resolution bounded to registry-enumerated harness commands (3 enumerated: ['claude', 'codex', 'gemini'])`) |

## Verification Evidence

### V1. Tooling probe (session start)

```
$ python -c "import groundtruth_kb; print('PY_OK', groundtruth_kb.__file__)" && echo "PY_EXIT=$?"
PY_OK E:\GT-KB\groundtruth-kb\src\groundtruth_kb\__init__.py
PY_EXIT=0

$ echo "BASH_OK marker-7fa2c1"; echo "BASH_EXIT=$?"
BASH_OK marker-7fa2c1
BASH_EXIT=0
```

Tool channels reliable (stdout + exit code in sync) before any protected mutation.

### V2. Implementation-start authorization packet

```
$ python scripts/implementation_authorization.py begin --bridge-id gtkb-root-boundary-external-harness-exec-exception
```

Result: packet created. `latest_status: GO`, `go_file: bridge/gtkb-root-boundary-external-harness-exec-exception-006.md`, `proposal_file: bridge/gtkb-root-boundary-external-harness-exec-exception-005.md`, `expires_at: 2026-05-30T01:11:36Z`, all 4 `target_paths` covered. `packet_hash: sha256:3e48dcc5...30bde0348`.

### V3. Narrative-artifact approval packet generation

```
$ python -m groundtruth_kb generate-approval-packet \
    --kind narrative \
    --target .claude/rules/project-root-boundary.md \
    --artifact-id claude-rules-project-root-boundary-md \
    --action update \
    --source-ref bridge/gtkb-root-boundary-external-harness-exec-exception-006.md \
    --explicit-change-request "Insert External Harness Executable Resolution Exception section after Sandbox Output Exception per DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION and bridge gtkb-root-boundary-external-harness-exec-exception (GO@-006)" \
    --change-reason "bridge/gtkb-root-boundary-external-harness-exec-exception-006.md" \
    --approval-mode approve \
    --changed-by claude-prime-builder \
    --out .groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json \
    --validate-after --json
```

Result: packet file written + validated via `validate_packet()`. Key fields:

- `artifact_type: narrative_artifact`
- `artifact_id: claude-rules-project-root-boundary-md` (slug form per Codex advisory at -006)
- `target_path: .claude/rules/project-root-boundary.md`
- `source_ref: bridge/gtkb-root-boundary-external-harness-exec-exception-006.md`
- `action: update`
- `approval_mode: approve`
- `approved_by: owner`
- `changed_by: claude-prime-builder`
- `full_content_sha256: 2d5506013dbaf77f72b6fa02cc9dd4eae64f480631989b504f978394f14fa5b8`
- `presented_to_user: true`, `transcript_captured: true`

### V4. Slice C pre-commit narrative-artifact evidence floor

```
$ git add -- .claude/rules/project-root-boundary.md
$ python scripts/check_narrative_artifact_evidence.py --staged
PASS narrative-artifact evidence (1 cleared)
```

Result: PASS. Staged blob sha256 matches `full_content_sha256` in the on-disk packet.

### V5. Spec-derived test suite

```
$ python -m pytest platform_tests/scripts/test_external_harness_exec_boundary.py -v
============================= test session starts =============================
...
collecting ... collected 4 items

test_external_harness_exec_boundary.py::test_pass_when_only_registry_enumerated_harness_commands_resolve_out_of_root PASSED [ 25%]
test_external_harness_exec_boundary.py::test_fail_when_non_harness_literal_subprocess_call_introduced PASSED [ 50%]
test_external_harness_exec_boundary.py::test_warn_when_harness_registry_missing PASSED [ 75%]
test_external_harness_exec_boundary.py::test_check_is_deterministic_and_read_only PASSED [100%]

============================== 4 passed in 0.29s ==============================
```

Result: 4/4 PASS. All proposal-specified test cases pass.

### V6. Doctor check registration + execution

```
$ python -m groundtruth_kb project doctor 2>&1 | grep -A 0 "External harness\|cross-harness exec"
  [OK]  cross-harness exec resolution bounded to registry-enumerated harness commands (3 enumerated: ['claude', 'codex', 'gemini']); no literal non-harness commands in scanned surface(s)
```

Result: PASS. The check is registered immediately after `_check_cross_harness_trigger` and reports PASS on the current tree (3 harness commands enumerated; no literal non-harness exec resolutions in the scanned surfaces).

### V7. Ruff lint

```
$ python -m ruff check groundtruth-kb/src/groundtruth_kb/project/doctor.py platform_tests/scripts/test_external_harness_exec_boundary.py
All checks passed!
```

Result: clean.

## Files Changed

- `.claude/rules/project-root-boundary.md` — inserted the new "External Harness Executable Resolution Exception" section (no other changes; existing text preserved verbatim).
- `groundtruth-kb/src/groundtruth_kb/project/doctor.py` — added `import ast`; added module-level constants `_HARNESS_EXEC_SCAN_TARGETS`, `_HARNESS_EXEC_INROOT_TOOLCHAIN`, `_HARNESS_EXEC_SUBPROCESS_METHODS`; added `_extract_literal_command(ast.Call)` helper; added `_check_external_harness_exec_boundary(target: Path) -> ToolCheck`; registered the check in `run_doctor` after `_check_cross_harness_trigger`.
- `platform_tests/scripts/test_external_harness_exec_boundary.py` — new file, 4 spec-derived test cases.
- `.groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json` — new narrative-artifact approval packet (gitignored; local evidence per Slice C).

## Acceptance Criteria Check

| Criterion | Status | Evidence |
|---|---|---|
| Codex returns GO on REVISED-2 proposal | DONE | `bridge/gtkb-root-boundary-external-harness-exec-exception-006.md` GO |
| Approval packet written with owner-approved content + schema-aligned field set | DONE | V3; `--validate-after` passed |
| Rule amended with bounded exception section; narrative-artifact-approval-gate validates Write against packet sha256 | DONE | V3 + V4; rule on-disk sha matches packet `full_content_sha256` |
| `_check_external_harness_exec_boundary` implemented + registered; PASS on current tree | DONE | V6 |
| `test_external_harness_exec_boundary.py` (4 cases) passes | DONE | V5 |
| Doctor check FAILs on synthetic non-harness out-of-root project dependency | DONE | V5 case (b) |
| `python scripts/check_narrative_artifact_evidence.py --staged` PASSES with positive evidence captured | DONE | V4 |
| Codex returns VERIFIED on the post-impl report | PENDING | this report |
| WI-3349 resumption thread filed after VERIFIED | DEFERRED | scoped as follow-on per proposal -005 |

## Loyal Opposition Asks

1. Confirm V3 packet generation matches the schema-aligned plan from -005 (artifact_id slug form per the -006 advisory, action=update, approval_mode=approve).
2. Confirm V4 Slice C pre-commit evidence floor PASS satisfies the `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` gate clause.
3. Confirm V6 doctor check PASS satisfies the proposal's "doctor-enforced bound" requirement.
4. Confirm V5 case (b) FAIL on a synthetic non-harness literal subprocess call satisfies the "FAIL on a genuine non-harness out-of-root project dependency" requirement.
5. Confirm V5 case (c) WARN on missing harness registry satisfies the "WARN if a harness resolution mechanism is present but the registry is missing the command" intent (this implementation interprets the registry-missing path as the canonical WARN case; commentary welcome on whether a finer-grained "registry-present-but-incomplete" detector is required).
6. Confirm deferring WI-3349 resumption to a separate follow-on thread is acceptable.
7. Confirm `Recommended commit type: feat:` matches the diff stat (net-new doctor check + spec-derived tests + governance amendment + approval packet).

## Risk and Rollback

Implementation risks identified at proposal time remain as scoped; mitigations are now realized:

- **Exception over-broadening**: doctor check + V5 case (b) test prove FAIL on non-harness out-of-root project deps. Bound is mechanical, not advisory.
- **Consistency with existing dispatch**: V6 doctor PASS on the current tree confirms `scripts/cross_harness_bridge_trigger.py` and `scripts/verify_antigravity_dispatch.py` use parametrized (non-literal) command lists from the registry projection — the amendment retroactively legitimizes the existing working pattern, no behavior change required.
- **Approval-packet date drift**: V3 confirms the packet date (2026-05-29) matches the implementation day. No re-revision required.

Rollback: revert the rule section + doctor changes (`git restore .claude/rules/project-root-boundary.md groundtruth-kb/src/groundtruth_kb/project/doctor.py`); remove the test file (`rm platform_tests/scripts/test_external_harness_exec_boundary.py`); delete the approval packet JSON (gitignored; local-only). No MemBase mutation to roll back.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
