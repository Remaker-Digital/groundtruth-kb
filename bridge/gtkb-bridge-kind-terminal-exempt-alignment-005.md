NEW

bridge_kind: fix
Document: gtkb-bridge-kind-terminal-exempt-alignment
Version: 005
Responds to GO: bridge/gtkb-bridge-kind-terminal-exempt-alignment-004.md
Approved proposal: bridge/gtkb-bridge-kind-terminal-exempt-alignment-003.md
Author: Prime Builder (Opus 4.8, harness B)
Date: 2026-06-01 UTC
Session: S379
Recommended commit type: fix

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-BRIDGE-PROTOCOL-RELIABILITY-BATCH
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: S379-bridge-kind-terminal-exempt-alignment-005-postimpl
author_model: Opus 4.8
author_model_version: claude-opus-4-8[1m]
author_model_configuration: Claude Code CLI explanatory output style, 1M context

target_paths: ["groundtruth-kb/src/groundtruth_kb/bridge/notify.py", "groundtruth-kb/tests/test_bridge_notify.py"]

# Post-Implementation Report — Align Dispatch-Terminal Bridge Kinds With the Compliance-Exempt Set

## Implementation Claim

Implemented the GO'd `-003` exactly as approved. Added the three compliance-exempt non-implementation `bridge_kind` tokens — `governance_review`, `spec_intake`, `loyal_opposition_advisory` — to `_KIND_TERMINAL_TOKENS` in `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`. A `GO` on any of these kinds now classifies `terminal`, so the dispatcher (and the cross-harness trigger, which imports the same classifier) does not auto-dispatch a headless Prime Builder session. Added three classification/dispatchability tests and ran `ruff format` on the test file (in-scope drift fix). All T1–T6 verification PASS.

## Specification Links

(Carried forward from GO'd `-003`.)

- `ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001` — dispatch contract; bounded away from non-implementation owner-gated GOs.
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` — auto-trigger contract; refined.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — `bridge/INDEX.md` routing authority.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — the trigger shares the classifier (verified: imports `compute_actionable_pending`).
- `GOV-ARTIFACT-APPROVAL-001` — the gate whose AXIS-2 work must not be headless-dispatched (forgery context).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage carried.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — spec linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-to-test mapping below.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (advisory) — durable artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` (advisory) — traceability.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (advisory) — lifecycle states.
- `.claude/rules/bridge-essential.md`, `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`.

## Spec-to-Test Mapping (Executed)

Per `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`. Commands run with the package venv `groundtruth-kb/.venv/Scripts/python.exe`, `PYTHONPATH=groundtruth-kb/src`. Result: **ALL PASS**.

| Test | Maps to spec | Executed check | Result |
|---|---|---|---|
| T1 | ADR-SMART-POLLER-OWNER-OUT-OF-LOOP-001, DCL-SMART-POLLER-AUTO-TRIGGER-001 | `test_classify_terminal_compliance_exempt_kinds`: `classify_document_dispatchability` → `"terminal"` for `governance_review`, `spec_intake`, `loyal_opposition_advisory` | PASS |
| T2 | GOV-ARTIFACT-APPROVAL-001 (forgery prevention) | `test_compliance_exempt_kinds_GO_not_dispatchable`: `_derive_dispatchable("GO", classify(kind))` is `False` for each kind | PASS |
| T3 | GOV-FILE-BRIDGE-AUTHORITY-001 | `test_compliance_exempt_kinds_review_paths_still_dispatchable`: `NEW`/`REVISED`/`NO-GO` still dispatchable `True` for each kind (Codex review + Prime revise preserved) | PASS |
| T4 | non-regression | Existing `test_classify_terminal_scoping_kind` / `_closure_kind` / `_dispatchable_*` / `_ambiguous_review_kind` / `_ambiguous_verification_kind` unchanged | PASS (bare `review`/`verification` still ambiguous) |
| T5 | DCL-CROSS-HARNESS-ENFORCEMENT-001 | `scripts/cross_harness_bridge_trigger.py` imports `compute_actionable_pending` from `groundtruth_kb.bridge.notify` (single classifier source; no duplicate) — the terminal change applies to both substrates | PASS (structural) |
| T6 | code quality (both changed files) | `ruff check` + `ruff format --check` on BOTH files | PASS |

Observed command output:

```text
python -m pytest groundtruth-kb/tests/test_bridge_notify.py -q   → 73 passed in 1.56s
python -m ruff check  notify.py test_bridge_notify.py            → All checks passed!
python -m ruff format --check notify.py test_bridge_notify.py    → 2 files already formatted
```

(Prior to this change: 70 tests; +3 new. `ruff format` reformatted `test_bridge_notify.py` once for pre-existing drift.)

## Implementation Steps Executed

| Step | Operation | Result |
|---|---|---|
| 1 | `python scripts/implementation_authorization.py begin --bridge-id gtkb-bridge-kind-terminal-exempt-alignment` | impl-start packet `sha256:1d296787…`; latest_status=GO; project-linkage validated |
| 2 | Edit `notify.py` `_KIND_TERMINAL_TOKENS` (+3 tokens + comment) | done (+9/-0) |
| 3 | Edit `test_bridge_notify.py` (+3 tests) | done |
| 4 | `ruff format groundtruth-kb/tests/test_bridge_notify.py` (in-scope pre-existing drift fix) | 1 file reformatted (+32/-3 total for the file incl. new tests) |
| 5 | pytest + ruff check + ruff format --check (both files) | ALL PASS |

## Files Changed

- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` — `+9/-0`: three tokens added to `_KIND_TERMINAL_TOKENS` with an explanatory comment. No logic change.
- `groundtruth-kb/tests/test_bridge_notify.py` — `+32/-3`: three new tests (`test_classify_terminal_compliance_exempt_kinds`, `test_compliance_exempt_kinds_GO_not_dispatchable`, `test_compliance_exempt_kinds_review_paths_still_dispatchable`) plus a minor in-scope `ruff format` pass on pre-existing lines (the file was an authorized `target_path`; no behavior change).

No file outside the authorized `target_paths` was mutated.

## Owner Decisions / Input

- **S379 AUQ "How far now" → "Drive the full fix now":** authorized this fix as the keystone of the forgery-prevention program.
- **S379 AUQ "Forged approval" → "Ratify + fix dispatch now":** authorized fixing the dispatch defect.
- Pure-code classifier refinement; no canonical-artifact insert, no owner-gated approval. Bounded by the validated project-linkage chain.

## Prior Deliberations

- `bridge/gtkb-dispatch-owner-approval-forgery-prevention-001.md` / `-002.md` — the incident + Codex NO-GO F1 that identified this classifier gap.
- `smart-poller-kind-aware-routing-2026-04-30-007/-009` — the routing contract this refines.
- WI `GTKB-BRIDGE-POLLER-PRIME-CLASSIFICATION-REFINEMENT` (S324) — the backlogged gap now fulfilled.

## Recommended Commit Type

`fix:` — repairs the dispatch classifier so non-implementation governance GOs are not headless-dispatched (behavior fix, no new capability). The git-committed surface is `notify.py` + `test_bridge_notify.py` (source code, not gitignored).

## Outcome

- The dispatcher's terminal set now ⊇ the compliance gate's exempt set; the two vocabularies are aligned. A `GO` on `governance_review` / `spec_intake` / `loyal_opposition_advisory` no longer auto-dispatches a headless Prime — removing the forgery enabler for owner-gated governance work, and retro-fixing the existing `…-scoping`/governance_review fleet that was wrongly dispatchable-on-GO.
- **Unblocks** re-filing the forgery-prevention incident thread as `governance_review` (now terminal → Codex can GO it without triggering dispatch) and the dedicated gate/DCL hardening follow-on.

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
