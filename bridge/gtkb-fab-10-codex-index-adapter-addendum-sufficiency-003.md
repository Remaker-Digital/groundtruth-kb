NEW

bridge_kind: implementation_report
Document: gtkb-fab-10-codex-index-adapter-addendum-sufficiency
Version: 003
Responds-To: bridge/gtkb-fab-10-codex-index-adapter-addendum-sufficiency-002.md
Approved-Proposal: bridge/gtkb-fab-10-codex-index-adapter-addendum-sufficiency-001.md
Author: prime-builder (Codex, harness A) - interactive owner session
Date: 2026-06-12

Project: PROJECT-FABLE-INVESTIGATION
Work Item: WI-4422
Project Authorization: PAUTH-FAB10-20260610

author_identity: prime-builder
author_harness_id: A
author_session_context_id: 019ebd61-0067-73d0-bc59-142681b70a9e
author_model: GPT-5
author_model_version: 5
author_model_configuration: Codex desktop, Prime Builder bridge queue processing

target_paths: [".codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py", "platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py"]

KB mutation: groundtruth.db is NOT in target_paths. No MemBase mutations in this report.

Recommended commit type: fix:

---

# FAB-10 Codex INDEX Adapter Addendum Sufficiency - Implementation Report

## Implementation Claim

Implemented the corrected FAB-10 Codex INDEX adapter addendum approved at
`bridge/gtkb-fab-10-codex-index-adapter-addendum-sufficiency-002.md`.

The Codex apply-patch adapter now treats normalized `bridge/INDEX.md` as a
bridge target in addition to versioned `bridge/*-NNN.md` files. When Codex
`apply_patch` edits `bridge/INDEX.md`, the adapter extracts the post-patch
content and forwards a synthetic Claude-style `Write` payload to the canonical
`.claude/hooks/bridge-compliance-gate.py`. This closes the HYG-039 parity gap
without duplicating INDEX parsing policy in the Codex adapter.

The implementation also adds focused regression tests proving:

- `bridge/INDEX.md` update patches are extracted as bridge writes;
- malformed `bridge/INDEX.md` patches propagate the canonical gate denial
  through the adapter path; and
- existing versioned bridge-file extraction behavior remains intact.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - `bridge/INDEX.md` is canonical bridge workflow state and must be protected from malformed writes.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - Codex hook parity requires the apply-patch adapter to enforce the same bridge-compliance gate as Claude Write/Edit.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the implementation-start authorization packet minted successfully from the corrected proposal.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this report carries forward the approved proposal's linked governing specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - verification below is derived from the linked specs and acceptance criteria.
- `GOV-STANDING-BACKLOG-001` - WI-4422 remains the governed backlog authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - both changed paths are in-root under `E:\GT-KB`.

## Owner Decisions / Input

No new owner decision was required. This implementation preserves the owner
selected FAB-10 HYG-039 scope from `DELIB-FAB10-REMEDIATION-20260610`: INDEX
well-formedness protection now, helper-only CAS-protected INDEX writes later.

## Prior Deliberations

- `DELIB-FAB10-REMEDIATION-20260610` - owner selected INDEX well-formedness lint now and helper-only writes later.
- `DELIB-20261697` - harvested Loyal Opposition GO for the original FAB-10 proposal.
- `bridge/gtkb-fab-10-dispatch-telemetry-claim-contract-001.md` and `-002.md` - original FAB-10 proposal and GO verdict.
- `bridge/gtkb-fab-10-codex-index-adapter-addendum-001.md` and `-002.md` - first addendum and GO, later withdrawn because the proposal lacked `## Requirement Sufficiency`.
- `bridge/gtkb-fab-10-codex-index-adapter-addendum-003.md` - withdrawal of the mechanically unusable first addendum.
- `bridge/gtkb-fab-10-codex-index-adapter-addendum-sufficiency-001.md` and `-002.md` - corrected addendum and GO.

## Specification-Derived Verification

| Spec / requirement | Executed verification evidence | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `test_extract_bridge_writes_includes_bridge_index_update`; `test_apply_patch_adapter_rejects_malformed_bridge_index_via_canonical_gate` | `bridge/INDEX.md` patches are treated as bridge writes and canonical gate denial is propagated. |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` | Adapter keeps a thin delegation model through `_run_canonical`; test monkeypatch proves the INDEX write reaches that delegation boundary. | PASS. No duplicate INDEX parsing policy added to the Codex adapter. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | `python scripts\implementation_authorization.py begin --bridge-id gtkb-fab-10-codex-index-adapter-addendum-sufficiency` | Authorized; packet hash `sha256:e06546ebac3f27d691c2bf774258694db11ea0f96e94e4d43e39d9c0b141a408`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused pytest, ruff lint, ruff format check, and py_compile commands listed below. | PASS. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Changed paths are `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py` and `platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py`. | Both are under `E:\GT-KB`; no application relocation or out-of-root dependency. |

## Commands Run

```powershell
python scripts\implementation_authorization.py begin --bridge-id gtkb-fab-10-codex-index-adapter-addendum-sufficiency
python -m pytest platform_tests\scripts\test_bridge_compliance_gate_apply_patch_adapter.py -q --tb=short --basetemp=.gtkb-state\pytest-tmp-fab10-adapter
python -m ruff check .codex\gtkb-hooks\bridge-compliance-gate-apply-patch-adapter.py platform_tests\scripts\test_bridge_compliance_gate_apply_patch_adapter.py
python -m ruff format --check .codex\gtkb-hooks\bridge-compliance-gate-apply-patch-adapter.py platform_tests\scripts\test_bridge_compliance_gate_apply_patch_adapter.py
python -m py_compile .codex\gtkb-hooks\bridge-compliance-gate-apply-patch-adapter.py platform_tests\scripts\test_bridge_compliance_gate_apply_patch_adapter.py
```

## Observed Results

- Implementation-start authorization: authorized; packet hash `sha256:e06546ebac3f27d691c2bf774258694db11ea0f96e94e4d43e39d9c0b141a408`.
- Focused pytest: `3 passed in 0.23s`.
- Ruff lint: `All checks passed!`.
- Ruff format: `2 files already formatted`.
- Py compile: passed with exit code 0.

## Files Changed

- `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py`
  - adds `BRIDGE_INDEX_FILE = "bridge/INDEX.md"`;
  - updates `_is_bridge_target()` so normalized `bridge/INDEX.md` is forwarded to the canonical gate;
  - updates the extraction docstring to describe versioned bridge files plus INDEX.
- `platform_tests/scripts/test_bridge_compliance_gate_apply_patch_adapter.py`
  - adds focused tests for INDEX extraction, canonical denial propagation, and existing versioned bridge-file behavior.

No FAB12, bridge withdrawal, or unrelated worktree files are claimed as part of this implementation report.

## Acceptance Criteria Status

1. LO returns GO for this corrected addendum. PASS - `bridge/gtkb-fab-10-codex-index-adapter-addendum-sufficiency-002.md`.
2. `implementation_authorization.py begin` returns an authorization packet. PASS - packet hash above.
3. Codex apply-patch edits to `bridge/INDEX.md` are forwarded to the canonical bridge-compliance gate. PASS - adapter predicate and tests.
4. Malformed INDEX content that the live gate rejects is also rejected through the Codex adapter path. PASS - focused denial propagation test.
5. Focused tests and lint pass. PASS - pytest, ruff, format, and py_compile evidence above.

## Risk And Rollback

Risk is low. The adapter remains a thin dispatcher to the canonical gate and
only expands the target predicate by one canonical bridge path. Rollback is a
file-level revert of `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py`
and removal of the focused test file.

## Loyal Opposition Asks

1. Verify the adapter change against the linked specifications and command evidence above.
2. Return `VERIFIED` if the implementation satisfies the corrected addendum, otherwise return `NO-GO` with concrete findings.
