NEW

bridge_kind: implementation_proposal
Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3372

Document: gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-06-04 UTC
Reviewer: Loyal Opposition
Recommended commit type: docs

author_identity: Claude Code Prime Builder (interactive, durable PB)
author_harness_id: B
author_session_context_id: 9935375e-0c75-4f43-8f9e-d6355bd604bf
author_model: Claude Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI, explanatory output style

target_paths: []

implementation_scope: none
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-3372 Slice 1 — closure proposal for already-landed KB-mutation target_paths check

## Proposal Claim

This proposal performs no MemBase mutation and executes no KB writes. (Self-demonstration of `_kb_mutation_target_paths_ask_reason`'s negation path: this single prose sentence trips `KB_MUTATION_NEGATION_RE` and short-circuits `_declares_kb_mutation` to False, allowing the proposal to proceed past the check it is itself filing closure for.)

Request `VERIFIED` verdict on WI-3372 ("Bridge-compliance check: require groundtruth.db in target_paths when a proposal declares KB mutation") based on existing implementation and parameterized test coverage. Slice 1 = closure-only; no new code mutation. Future Slice 2 (if needed) would address the 42-line line-count drift between active hook (1313 LOC) and template (1271 LOC) — separately scoped.

The WI's `related_bridge_threads` field lists 3 entries — all S358 NO-GO'd proposals that motivated the check (W1/W2/W3). None is a closure thread for WI-3372 itself, which is why the WI remains `open` despite the work being landed. This proposal supplies the missing closure-cycle artifact.

## Implementation Evidence (already landed; cited as inspection targets, not modified)

**Active hook — `.claude/hooks/bridge-compliance-gate.py`:**
- `_kb_mutation_target_paths_ask_reason(content)` at lines 631-648 implements the check: only fires on `PENDING_PREFLIGHT_STATUSES` (NEW/REVISED), exempts metadata-only `bridge_kind`s via `_bridge_kind_is_metadata_exempt`, calls `_declares_kb_mutation` to detect MemBase-mutation language, then asserts `groundtruth.db` (path-normalized) in `target_paths`. Returns a blocking message if the mutation is declared without inclusion.
- `_declares_kb_mutation(content)` at lines 624-628 uses `KB_MUTATION_DECLARATION_RE` with `KB_MUTATION_NEGATION_RE` short-circuit to avoid false positives on prose that merely *mentions* MemBase.
- Wired into the main deny-reason path at `_deny_reason_for_content` line 588: `kb_mutation_reason = _kb_mutation_target_paths_ask_reason(content)` → returned as deny reason when non-None.

**Template — `groundtruth-kb/templates/hooks/bridge-compliance-gate.py`:**
- Same function set present (`grep _kb_mutation_target_paths_ask_reason` shows lines 178+/588+/614+/621+/628+ matching the active hook semantically). Templates are byte-similar though not byte-identical (line-count drift noted above; outside Slice 1 scope).

## Test Coverage (already landed; cited as inspection targets, not modified)

**`platform_tests/hooks/test_bridge_compliance_gate_kb_mutation_target_paths.py`** — parameterized over BOTH `LIVE_HOOK` and `TEMPLATE_HOOK` via the `gate` fixture (`_load_gate` at lines 22-28):

1. `test_kb_mutation_without_groundtruth_db_asks` (positive case — mutation declared, missing → ask returned, message contains `groundtruth.db`)
2. `test_kb_mutation_with_groundtruth_db_passes` (happy path — mutation declared + included → no ask)
3. `test_kb_mutation_with_dot_prefixed_groundtruth_db_passes` (`./groundtruth.db` normalization)
4. `test_membase_mention_only_not_flagged` (false-positive guard — content discusses MemBase but declares no mutation)
5. `test_metadata_exempt_bridge_kind_not_flagged` (exemption for metadata bridge_kinds)

Verification command Codex may run:
```
python -m pytest platform_tests/hooks/test_bridge_compliance_gate_kb_mutation_target_paths.py -v
```

## Specification Links

- `WI-3372` — work item under closure; project_id `PROJECT-GTKB-RELIABILITY-FIXES`, approval_state `auq_resolved` (owner pre-approved scope).
- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` — active standing authorization; `allowed_mutation_classes: ["source", "test_addition", "hook_upgrade"]`; `included_work_item_ids: null` (open scope within project); WI-3372 confirmed active member via `current_project_work_item_memberships` row `PWM-PROJECT-GTKB-RELIABILITY-FIXES-WI-3372` (status active; intentionally linked per S358 reconciliation 2026-05-18: "link the deterministic target_paths-completeness check follow-on (WI-3372) to the reliability fast-lane project so PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING covers it by membership").
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge protocol + INDEX canonicality.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this proposal cites all relevant specs in machine-readable form.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — spec-to-test mapping satisfied by the 5 parameterized tests above.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — 3 project-linkage header lines present at top (`Project Authorization`, `Project`, `Work Item`).
- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` — VERIFIED on this thread should trigger WI-3372 auto-retirement via the standard scanner path.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — PAUTH envelope model.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all referenced paths within `E:\GT-KB`.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — artifact-oriented governance.

## Owner Decisions / Input

- WI-3372's `approval_state = 'auq_resolved'` records prior owner AUQ approval of the implementation scope.
- Standing `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` is active (no expiration) and covers WI-3372 by membership (per evidence above).
- No new AUQ required for this verification-only closure proposal; `target_paths: []` declares no new mutation.
- This proposal does not request waiver or new approval; it requests Codex inspect existing artifacts (hook + tests) and issue `VERIFIED` if the work satisfies WI-3372's acceptance.

## Requirement Sufficiency

Existing requirements sufficient. No new specification, no source/test/hook mutation. The WI's acceptance ("deterministic bridge-compliance check that flags any bridge implementation proposal whose text declares MemBase / KB-mutation work...while omitting groundtruth.db from its target_paths") is satisfied by the cited landed implementation and tests. This proposal is the closure-cycle artifact the WI lacks.

## Prior Deliberations

- S358 W1/W2/W3 (`bridge/gtkb-s358-w1-retirement-machinery-correction-002.md`, `bridge/gtkb-s358-w2-agent-red-gov-trio-v2-002.md`, `bridge/gtkb-s358-w3-requirements-collection-hook-title-fix-002.md`) — three sequential Codex NO-GOs for the same `groundtruth.db`-missing-from-target_paths defect. Flagged as Opportunity Radar candidate that motivated WI-3372.
- Auto-memory observation from this session: WI-3372's `project_name` field had to be deliberately reconciled (DELIB-2505, DELIB-2506; `gt projects reconcile-doubled-prefix` 2026-05-29) to remove a phantom doubled-prefix membership; the canonical `PROJECT-GTKB-RELIABILITY-FIXES` row is the one PAUTH coverage flows through.
- No prior Deliberation Archive entries specifically for this Slice-1 closure proposal (novel closure-cycle artifact for an already-landed check).

## Specification-Derived Verification Plan

| Spec | Evidence |
|------|----------|
| WI-3372 acceptance (deterministic Write-time check) | `_kb_mutation_target_paths_ask_reason` in `.claude/hooks/bridge-compliance-gate.py:631`; wired at `_deny_reason_for_content:588`. |
| WI-3372 acceptance (template parity for the gate semantics) | `_kb_mutation_target_paths_ask_reason` present in `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` (grep-verified at lines 178+/588+/614+/621+/628+). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `platform_tests/hooks/test_bridge_compliance_gate_kb_mutation_target_paths.py` — 5 tests parameterized over both surfaces; verification command `python -m pytest platform_tests/hooks/test_bridge_compliance_gate_kb_mutation_target_paths.py -v`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | This proposal's `## Specification Links` section above. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | The 3 header lines at lines 4-6 of this proposal. |
| `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` | Codex VERIFIED on this thread → auto-retirement scanner advances WI-3372 to `verified`/`done` per project completion criteria. |

## Risk / Rollback

This proposal mutates no files (`target_paths: []`). The only artifact created is this bridge document itself plus its INDEX entry. Rollback = file is part of the audit trail and is not removed (per bridge file append-only invariant); a future revision can supersede or withdraw via a `-002` version if Codex finds the framing inadequate.

## Filing Evidence (for GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL)

Bridge artifact `bridge/gtkb-bridge-compliance-require-groundtruth-db-in-target-paths-slice-1-001.md` filed under bridge/ with an INDEX update inserting the entry at the top of bridge/INDEX.md (via `scripts/bridge_index_writer.atomic_index_update` for serialized lock-protected write). No deletion or rewrite of prior versions; INDEX canonicality preserved per GOV-FILE-BRIDGE-AUTHORITY-001.

## Out of Slice 1 scope (candidate Slice 2 if needed)

- The 42-line drift between active hook and template (`1313` vs `1271` lines) covers more than the KB-mutation check; closing that drift requires per-hunk reconciliation work beyond WI-3372's scope. If Codex deems the line-count drift a blocking concern for closure, that's Slice 2 work (separate proposal).
