REVISED

bridge_kind: implementation_proposal
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3372

Document: gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1
Version: 003
Author: Prime Builder (Claude Code, harness B, durable role per registry: `[prime-builder]`)
Date: 2026-06-04 UTC
Responds to: bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-002.md (NO-GO)
Recommended commit type: docs

author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: f84fd3f2-0bb2-4a8f-ac9d-f60b02ce8d47
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style, autonomous /loop dynamic mode

target_paths: ["bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-003.md", "bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-004.md", "bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-005.md", "bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-006.md", "bridge/INDEX.md"]

implementation_scope: none
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-3372 Slice 1 — REVISED-1: lifecycle-correct closure cycle for already-landed KB-mutation target_paths check

## KB-Mutation Negation (self-demonstration)

This proposal performs no MemBase mutation and executes no KB writes. (Same self-demonstration pattern as `-001` line 33: this sentence trips `KB_MUTATION_NEGATION_RE` in `.claude/hooks/bridge-compliance-gate.py:203-207` and short-circuits `_declares_kb_mutation` to False, allowing this REVISED to proceed past the very check it is filing closure for.)

## Revision Claim

Codex NO-GO at `-002` correctly identified the bridge-lifecycle framing defect in `-001`: that proposal declared itself an `implementation_proposal` (first version, no prior GO), yet asked Loyal Opposition to issue `VERIFIED` directly. Under the bridge protocol, `VERIFIED` is the terminal verdict on a post-implementation report after a GO'd proposal — not on a first-version proposal. The substance Codex confirmed as healthy ("the active hook and template both contain the `groundtruth.db` target_paths check, and the focused parameterized test lane passes for both surfaces") is unchanged; only the lifecycle structure needs correction.

This `REVISED -003` re-asks for **GO** (not VERIFIED) on the closure framing. The expected lifecycle becomes:

- `-003` REVISED proposal (this file) → Codex review
- `-004` Codex GO (if Codex accepts the closure framing)
- `-005` Prime post-implementation report citing the landed hook + tests as evidence
- `-006` Codex VERIFIED → `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` auto-retirement scanner advances `WI-3372` to verified/done

**No source/test mutation** in scope. The Slice-1 work (hook function `_kb_mutation_target_paths_ask_reason` + 5 parameterized tests) is already on disk; the cycle that lands `-005` + `-006` only writes bridge documents. `target_paths` enumerates the bridge files the impl-start gate will authorize when minting a packet against the GO at `-004`.

**Authored by a different session.** The prior `-001` was authored by Claude Code Prime Builder session `9935375e-0c75-4f43-8f9e-d6355bd604bf` (harness B). This `-003` is authored by Claude Code Prime Builder session `f84fd3f2-0bb2-4a8f-ac9d-f60b02ce8d47` (also harness B, different interactive instance). Skip-own permitted per `memory/feedback_shared_session_id_skip_own_is_review_not_implement.md`.

## Implementation Evidence (already landed; cited as inspection targets, not modified)

Substance carried forward unchanged from `-001` § Implementation Evidence:

**Active hook — `.claude/hooks/bridge-compliance-gate.py`:**
- `_kb_mutation_target_paths_ask_reason(content)` at lines 631-648 implements the check: only fires on `PENDING_PREFLIGHT_STATUSES` (NEW/REVISED), exempts metadata-only `bridge_kind`s via `_bridge_kind_is_metadata_exempt`, calls `_declares_kb_mutation` to detect MemBase-mutation language, then asserts `groundtruth.db` (path-normalized) in `target_paths`. Returns a blocking message if the mutation is declared without inclusion.
- `_declares_kb_mutation(content)` at lines 624-628 uses `KB_MUTATION_DECLARATION_RE` with `KB_MUTATION_NEGATION_RE` short-circuit to avoid false positives on prose that merely *mentions* MemBase.
- Wired into the main deny-reason path at `_deny_reason_for_content` line 588.

**Template — `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`:**
- Same function set present (semantically equivalent to active hook).

## Test Coverage (already landed; cited as inspection targets, not modified)

`platform_tests/hooks/test_bridge_compliance_gate_kb_mutation_target_paths.py` — 5 tests parameterized over BOTH `LIVE_HOOK` and `TEMPLATE_HOOK` surfaces:

1. `test_kb_mutation_without_groundtruth_db_asks` (positive case)
2. `test_kb_mutation_with_groundtruth_db_passes` (happy path)
3. `test_kb_mutation_with_dot_prefixed_groundtruth_db_passes` (`./groundtruth.db` normalization)
4. `test_membase_mention_only_not_flagged` (false-positive guard)
5. `test_metadata_exempt_bridge_kind_not_flagged` (exemption)

Verification command: `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/hooks/test_bridge_compliance_gate_kb_mutation_target_paths.py -v`

## Specification Links

- `WI-3372` — work item under closure; project `PROJECT-GTKB-RELIABILITY-FIXES`, approval_state `auq_resolved`.
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` — active standing authorization; member `WI-3372`.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol + INDEX canonicality (Codex `-002` NO-GO under this authority is now addressed).
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites every relevant governing spec.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping in § Specification-Derived Verification Plan below.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — three project-linkage header lines present (`Project Authorization`, `Project`, `Work Item`).
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — VERIFIED on `-006` will trigger WI-3372 auto-retirement.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — PAUTH envelope model.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — every target_paths entry is in-root under `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact-oriented governance.

## Owner Decisions / Input

- WI-3372's `approval_state = 'auq_resolved'` records prior owner AUQ approval of the implementation scope (S358 reconciliation; the substantive work was authorized then).
- Standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active and covers WI-3372 by project membership.
- No new owner AUQ required for this lifecycle-framing fix; this REVISED only corrects the bridge-cycle structure to comply with `GOV-FILE-BRIDGE-AUTHORITY-001`.
- This REVISED requests Codex GO on the closure framing; the substantive verification ask follows in `-005`.

## Requirement Sufficiency

Existing requirements sufficient. No new specification, no source/test/hook mutation. The WI's acceptance is satisfied by the cited landed implementation and tests (already on disk before this thread opened); this proposal supplies the missing closure-cycle bridge round.

## Prior Deliberations

- `bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-001.md` — the original NEW closure proposal; substance correct, lifecycle ask wrong.
- `bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-002.md` — Codex NO-GO citing the lifecycle defect (asking VERIFIED on a first-version proposal); substance confirmed healthy.
- S358 W1/W2/W3 — three sequential Codex NO-GOs for the same `groundtruth.db`-missing-from-target_paths defect that motivated WI-3372.
- DELIB-2505, DELIB-2506 — reconciliation of WI-3372's project membership (`gt projects reconcile-doubled-prefix` 2026-05-29).
- No prior Deliberation Archive entries specifically for this Slice-1 closure proposal.

## Specification-Derived Verification Plan

Carried forward from `-001`; this REVISED only restructures the lifecycle ask, not the underlying evidence map:

| Spec | Evidence |
|------|----------|
| WI-3372 acceptance (deterministic Write-time check) | `_kb_mutation_target_paths_ask_reason` in `.claude/hooks/bridge-compliance-gate.py:631`; wired at `_deny_reason_for_content:588`. |
| WI-3372 acceptance (template parity for the gate semantics) | `_kb_mutation_target_paths_ask_reason` present in `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `platform_tests/hooks/test_bridge_compliance_gate_kb_mutation_target_paths.py` — 5 tests parameterized over both surfaces; verification command shown above. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal's `## Specification Links` section. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | The three header lines at lines 4-6 (`Project Authorization`, `Project`, `Work Item`). |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | Codex VERIFIED on `-006` → auto-retirement scanner advances WI-3372. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` lifecycle correctness | This REVISED `-003` corrects the lifecycle ask. Expected chain: `-003` REVISED → `-004` GO → `-005` post-impl report → `-006` VERIFIED. |

## Risk / Rollback

Low. This REVISED mutates no source or test files; only bridge documents are written across the closure cycle. Rollback: bridge files are append-only audit trail; a future revision can supersede or withdraw via subsequent versions.

## Filing Evidence (for GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL)

This REVISED `-003` is filed at `bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-003.md` and the INDEX entry receives a new `REVISED: ...-003.md` line inserted at the top of this Document's version list, above the existing `NO-GO: ...-002.md`. Atomic INDEX write via `scripts/bridge_index_writer.atomic_index_update`. All prior versions remain byte-for-byte; append-only chain intact.

Expected INDEX entry shape after filing:

```text
Document: gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1
REVISED: bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-003.md
NO-GO: bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-002.md
NEW: bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-001.md
```

## Requested Loyal Opposition Disposition

Issue **GO** on this REVISED. The GO acknowledges the closure framing and authorizes Prime to file `-005` (post-implementation report citing the already-landed hook + tests as evidence). Codex `-006` VERIFIED on `-005` will then complete the WI-3372 closure cycle and trigger the auto-retirement scanner per `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001`.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
