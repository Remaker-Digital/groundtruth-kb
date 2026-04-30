REVISED

# Smart-Poller Kind-Aware Routing Refinement (REVISED-2)

**Status:** REVISED (REVISED-2; supersedes `-003` after Codex NO-GO at `-004`)
**Date:** 2026-04-30 (S323)
**Author:** Prime Builder (Claude, current session)
**Trigger:** Codex NO-GO at `bridge/smart-poller-kind-aware-routing-2026-04-30-004.md` with two blocking findings (F1: default-enabled `dispatchable` expression contradicts stated "ambiguous = status-only fallback" rule and would suppress ambiguous entries; F2: `post_implementation*` status-dependent behavior is described in test names and acceptance criteria but not actually modeled by the kind-only classifier).

bridge_kind: implementation_proposal
work_item_ids: [GTKB-SMART-POLLER-KIND-AWARE-ROUTING]
spec_ids: [DCL-SMART-POLLER-AUTO-TRIGGER-001, DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001]
parent_bridge: bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md (VERIFIED)
target_project: gt-kb-platform
implementation_scope: notify.py + bridge_poller_runner.py + bridge_notify_reader.py + tests
requires_review: true
requires_verification: true

---

## Specification Links

(Carried forward from `-003`.) Plus:
- `bridge/smart-poller-kind-aware-routing-2026-04-30-004.md` (Codex NO-GO) — drives this REVISED-2.

---

## Change Log Vs `-003`

| Change | Driving finding | Section |
|---|---|---|
| **`dispatchable` invariant simplified to `classification != "terminal"`.** Eliminates the contradiction between the inline expression and the stated "ambiguous = status-only fallback" rule. With the invariant: terminal entries are non-dispatchable; dispatchable entries are dispatchable; ambiguous entries are dispatchable (preserving current behavior for legacy bridges + bare `proposal` + unrecognized kinds). | F1 | §1.2, §1.3, test mapping |
| **Token lists narrowed to unambiguous cases only.** `_KIND_TERMINAL_TOKENS` keeps only kinds that are unambiguously terminal-on-actionable-status: `scoping`, `closure`, `parking`, `index_reconciliation`, `thread_reconciliation`, `operational_state_change`, `candidate_spec_intake`. `_KIND_DISPATCHABLE_TOKENS` keeps unambiguous dispatchable kinds + adds `post_implementation` and `post_impl` (kebab/snake variants normalized) and `implementation_report`. **Dropped from `_KIND_TERMINAL_TOKENS`: `review` and `verification`** — those have mixed semantics in practice and now classify as ambiguous → dispatchable, preferring false positive (small token cost on ~36 mixed-kind threads) over false negative (missed Prime work). | F2 + Codex Q2/Q3 | §1.1 |
| **`post_implementation_report` status-aware framing removed.** REVISED-2 classifies kind-only (no top-status input). Test names updated: `test_post_implementation_report_classifies_as_dispatchable` (was `…_classifies_as_dispatchable_when_NO_GO`). The status-aware behavior happens implicitly upstream in `compute_actionable_pending`: GO/NO-GO routes to Prime; VERIFIED routes to no one. So a `post_implementation_report` with VERIFIED top status NEVER reaches the classifier (already filtered by upstream status logic). With the F1 fix, a NO-GO chain on `post_implementation_report` is correctly dispatched. Acceptance criterion 14 reworded. | F2 | §1.1, §test mapping, §4 |
| **Kebab/snake normalization.** `bridge_kind` is lowercased AND has `-` replaced with `_` before token matching. This catches `post-implementation-report` (3 occurrences) which underscore-only matching would miss. | bug catch from inventory | §1.1 |
| **Reader column rendering is unconditional.** Per Codex Q2 answer: not gated by `GTKB_NOTIFY_KIND_AWARE_ROUTING`. Always renders columns. Explicit in §1.4. | Codex Q2 | §1.4 |
| **Regression test added per Codex required action 1:** `test_default_enabled_routing_dispatches_ambiguous_legacy_proposal_chain` — fixture: bridge with `bridge_kind: proposal` (bare) on the operative Prime version + GO top status. Default flag enabled. Asserts `dispatchable=True` AND `_dispatch_if_needed` includes the entry. | F1 | test mapping |
| **Regression test added per Codex required action 3:** `test_default_enabled_routing_dispatches_post_implementation_NO_GO_chain` — fixture: bridge with `bridge_kind: post_implementation_report` on operative Prime version + NO-GO top status. Default flag enabled. Asserts `dispatchable=True`. | F2 | test mapping |

All sections of `-003` not listed above are preserved unchanged.

---

## 1. Implementation Design (REVISED-2 — F1 + F2 fixes)

### 1.1 Token Lists (REVISED per F1 + F2)

```python
# Kebab/snake normalization: bridge_kind is lowercased then "-" → "_" before
# token matching. Catches post-implementation-report (kebab variant in inventory).

_KIND_TERMINAL_TOKENS: Final[tuple[str, ...]] = (
    "scoping",                # implementation_scoping, governance_scoping_proposal, scoping_proposal, scoping_addendum
    "closure",
    "parking",                # parking_acknowledgement
    "index_reconciliation",
    "thread_reconciliation",
    "operational_state_change",
    "candidate_spec_intake",
)
# DROPPED from -003: "review" and "verification". Mixed semantics in practice;
# now ambiguous → dispatchable. Trades small token cost on ~36 threads for
# false-negative safety.

_KIND_DISPATCHABLE_TOKENS: Final[tuple[str, ...]] = (
    "implementation_proposal",
    "implementation_slice",
    "multiphase_implementation",
    "fix",
    "governance_proposal",
    "architecture_proposal",
    "post_implementation",       # post_implementation_report, post_implementation_report_revision (substring), post-implementation-report (after kebab-norm)
    "post_impl",                 # post_impl_report
    "implementation_report",
)

# Bare "proposal" + "review" + "verification" + anything unrecognized →
# ambiguous → dispatchable (per F1 invariant below).
```

Token-matching order: terminal first (terminal is more specific — `governance_scoping_proposal` matches `scoping` before it would match `governance_proposal`).

### 1.2 The Invariant (per Codex F1)

```python
def is_dispatchable(classification: Literal["dispatchable", "terminal", "ambiguous"]) -> bool:
    """The single rule: terminal entries are NOT dispatched; everything else IS.
    
    This includes ambiguous entries — preserving the legacy fallback rule
    that bridges without bridge_kind, bare "proposal", review, verification,
    or unrecognized kinds remain dispatch-eligible (avoids false-negative
    suppression of legitimate Prime work).
    """
    return classification != "terminal"
```

**Why this works:**
- Dispatchable kinds (implementation/governance/architecture proposals, slices, fixes, post-impl reports, implementation reports) → dispatched. ✓
- Terminal kinds (scoping/closure/parking/etc.) → NOT dispatched. ✓ (THE BUG FIX.)
- Ambiguous kinds (legacy without `bridge_kind`, bare `proposal`, review, verification, unrecognized) → dispatched as fallback. ✓ (PRESERVES LEGACY BEHAVIOR.)

The `compute_actionable_pending` upstream filter already ensures only Prime-actionable status entries (GO/NO-GO) reach this classifier on the Prime side, and only Codex-actionable status entries (NEW/REVISED) reach it on the Codex side. VERIFIED entries are never in either list, so a `post_implementation_report` with VERIFIED top status is implicitly excluded by upstream status logic — no status-aware classifier needed.

### 1.3 `compute_actionable_pending` (REVISED per F1)

```python
def compute_actionable_pending(
    parse_result: ParseResult,
    *,
    project_root: Path,
) -> tuple[list[ActionablePending], list[ActionablePending]]:
    actionable_for_prime: list[ActionablePending] = []
    actionable_for_codex: list[ActionablePending] = []
    
    for doc in parse_result.documents:
        if not doc.versions:
            continue
        top = doc.versions[0]
        if not (project_root / top.file_path).is_file():
            continue
        
        classification = classify_document_dispatchability(project_root, doc)
        dispatchable = is_dispatchable(classification)  # The F1 fix invariant.
        # Note: feature flag is checked at the consumer (bridge_poller_runner)
        # not here. The metadata is always emitted; the consumer decides
        # whether to act on it.
        
        entry = ActionablePending(
            document_name=doc.name,
            top_status=str(top.status.value),
            top_file=top.file_path,
            index_line_number=top.line_number,
            dispatchable=dispatchable,
            classification=classification,
        )
        status_str = str(top.status.value)
        if status_str in ACTIONABLE_STATUSES_FOR_PRIME:
            actionable_for_prime.append(entry)
        elif status_str in ACTIONABLE_STATUSES_FOR_CODEX:
            actionable_for_codex.append(entry)
    
    return actionable_for_prime, actionable_for_codex
```

### 1.4 Reader Column Rendering (per Codex Q2 answer)

`scripts/bridge_notify_reader.py:format_orient_section` ALWAYS renders the new `Dispatchable` and `Classification` columns, regardless of `GTKB_NOTIFY_KIND_AWARE_ROUTING`. The rendering is observability; it does not alter dispatch behavior. Per Codex Q2: "Do not gate reader column rendering on the feature flag. Rendering Dispatchable and Classification unconditionally is useful observability."

### 1.5 Dispatch Consumer Filter (preserved from `-003` §1.3)

`bridge_poller_runner._dispatch_if_needed` filters on `entry.dispatchable` before signature/spawn, gated by `GTKB_NOTIFY_KIND_AWARE_ROUTING` (default `1`). Audit emits `no_pending_after_filter` when filtering removes all entries; `filtered_terminal_count` reports how many were filtered. Unchanged from `-003`.

### 1.6 Operative Prime Version Resolution (preserved from `-003` §1.1)

`find_operative_prime_version(doc)` returns the latest NEW or REVISED version. Unchanged from `-003`.

---

## 2. Specification-Derived Verification (REVISED test mapping)

| Linked spec / rule / record | Derived test | Coverage rationale |
|---|---|---|
| **DCL-SMART-POLLER-AUTO-TRIGGER-001** (per-kind correctness) | `test_dispatchable_excludes_terminal_candidate_spec_intake_GO_verdict_chain` + `test_dispatchable_excludes_terminal_scoping_GO_verdict_chain` + `test_dispatchable_excludes_terminal_closure_GO_verdict_chain` + `test_dispatchable_includes_implementation_proposal_GO_verdict_chain` + `test_dispatchable_includes_implementation_proposal_NO_GO_verdict_chain` + `test_dispatchable_includes_implementation_slice_GO_verdict_chain` | Per-kind correctness using real verdict-chain fixtures. |
| **F1 invariant (`dispatchable = classification != "terminal"`)** | **`test_dispatchable_invariant_terminal_returns_false`** + **`test_dispatchable_invariant_dispatchable_returns_true`** + **`test_dispatchable_invariant_ambiguous_returns_true`** (the F1 fix) | The invariant directly. |
| **F1 regression (Codex required action 1)** | **`test_default_enabled_routing_dispatches_ambiguous_legacy_proposal_chain`** — fixture: bridge with `bridge_kind: proposal` (bare) on operative Prime version + GO top status. Default flag enabled. Asserts `dispatchable=True` AND `_dispatch_if_needed` includes the entry in spawn list. | The exact case Codex required to verify. |
| **F2 fix (post-impl status-aware behavior simplified)** | `test_post_implementation_report_classifies_as_dispatchable` + `test_post_impl_report_classifies_as_dispatchable` + `test_post_implementation_report_revision_classifies_as_dispatchable` + `test_post_implementation_kebab_variant_classifies_as_dispatchable_after_normalization` | Kind-only classification per F2 simplification. |
| **F2 regression (Codex required action 3)** | **`test_default_enabled_routing_dispatches_post_implementation_NO_GO_chain`** — fixture: bridge with `bridge_kind: post_implementation_report` on operative Prime version + NO-GO top status. Default flag enabled. Asserts `dispatchable=True`. | The exact case Codex required to verify. |
| **F2 implicit-VERIFIED filtering** | `test_post_implementation_report_VERIFIED_top_never_reaches_classifier` — fixture: bridge thread with VERIFIED top status. Asserts the entry is excluded from both `actionable_for_prime` and `actionable_for_codex` lists upstream of classification. | Implicit status filtering by upstream `compute_actionable_pending`. |
| **DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001** (operational fix lands in this slice) | `test_dispatch_consumer_skips_terminal_entries` + `test_dispatch_consumer_includes_dispatchable_entries` + `test_dispatch_consumer_includes_ambiguous_entries_under_default_flag` (NEW per F1) + `test_dispatch_consumer_signature_uses_filtered_list` | Token-cost reduction is observable in the runner's spawn list. |
| **F3 (reader unconditional column rendering, per Codex Q2)** | `test_format_orient_section_includes_dispatchable_column_unconditionally` + `test_format_orient_section_includes_classification_column_unconditionally` + `test_format_orient_section_renders_terminal_entries_with_visible_marker` + `test_format_orient_section_renders_columns_when_flag_disabled` | Observability is not flag-gated. |
| **Kebab/snake normalization** | `test_kebab_kind_normalized_to_snake_for_token_matching` | Inventory has `post-implementation-report` (3 occurrences). |
| **Operative-proposal resolution (preserved from `-003`)** | `test_find_operative_prime_version_returns_latest_REVISED` + `test_find_operative_prime_version_returns_latest_NEW_when_no_REVISED` + `test_find_operative_prime_version_returns_None_when_no_NEW_or_REVISED` + `test_find_operative_prime_version_skips_codex_authored_GO_NO_GO_VERIFIED` | F1 of -002 — preserved. |
| **Codex Q2 (`review` token now ambiguous)** | `test_review_kind_classifies_as_ambiguous_and_dispatches_under_default_flag` — fixture: `bridge_kind: review` + GO top status. Default flag enabled. Asserts `dispatchable=True`. | REVISED-2 dropped `review` from terminal tokens; safer default. |
| **Codex Q3 (`verification` token now ambiguous)** | `test_verification_kind_classifies_as_ambiguous_and_dispatches_under_default_flag` | Same as above. |
| **Codex Q4 (bare `proposal`)** | `test_bare_proposal_kind_classifies_as_ambiguous_and_dispatches` | Per Codex Q4: "ambiguous fallback acceptable for legacy ambiguity". |
| **Codex Q6 (schema-v3 readers updated together)** | `test_canonical_reader_returns_schema_v3_artifact_with_new_fields` + `test_format_orient_section_handles_schema_v3` (and rejects v2 explicitly) | Schema bump completeness. |
| **`DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`** (carried forward) | `test_routing_docstring_cites_delib_s319_and_this_refinement` | Audit trail. |
| **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** | `test_routing_output_is_deterministic_for_identical_input` | Determinism. |
| **GOV-FILE-BRIDGE-AUTHORITY-001** | `test_routing_makes_zero_writes_to_bridge_index_md` | Read-only. |
| **`.claude/rules/project-root-boundary.md`** | `test_routing_reads_no_files_outside_e_gt_kb` | Path discipline. |
| **`.claude/rules/file-bridge-protocol.md`** | Procedural. | **Waiver: review-only / no derived test.** |
| **`.claude/rules/bridge-essential.md`** | Covered above. | No separate test. |
| **`.claude/rules/codex-review-gate.md`** | Procedural. | **Waiver: review-only / no derived test.** |
| **Frontmatter parser robustness** | `test_frontmatter_parser_extracts_bridge_kind` + `test_frontmatter_parser_handles_missing_bridge_kind` + `test_frontmatter_parser_handles_unrecognized_bridge_kind` + `test_frontmatter_parser_handles_malformed_file` | Parser. |
| **Feature-flag fallback (`GTKB_NOTIFY_KIND_AWARE_ROUTING`)** | `test_kind_aware_routing_disabled_treats_all_as_dispatchable_in_dispatch` (`=0` → all dispatchable in spawn path) + `test_kind_aware_routing_enabled_by_default_filters_terminal_in_dispatch` (default → filtered spawn) | Safe rollback. |
| **Backward compatibility (existing tests)** | Existing `test_bridge_notify.py` + `test_bridge_poller_runner.py` continue to pass after parameter additions. | Non-regression. |

Release-gate inclusion: `python scripts/release_candidate_gate.py --skip-frontend` runs the full bridge-poller test suite.

---

## Prior Deliberations

(Carried forward from `-003`.) Plus:
- `bridge/smart-poller-kind-aware-routing-2026-04-30-004.md` (Codex NO-GO) — drives this REVISED-2.

---

## 3. Verification Plan (preserved from `-003` §3 except)

§3.2 Production-State Validation now also includes a check that an ambiguous-kind chain (e.g., a real `bridge_kind: proposal` thread) appears in the Prime dispatch path, NOT filtered out:

```bash
# Look up an ambiguous-kind chain currently in the actionable lists; assert
# it is dispatchable=true in the JSON artifact.
python -c "
import json
art = json.load(open('.gtkb-state/bridge-poller/notifications/pending-bridge-action-prime.json'))
ambiguous_dispatchable = [a for a in art['pending_actions'] if a.get('classification') == 'ambiguous' and a.get('dispatchable')]
assert ambiguous_dispatchable or not [a for a in art['pending_actions'] if a.get('classification') == 'ambiguous'], \
    f'ambiguous entries not dispatchable: {ambiguous_dispatchable}'
print(f'{len(ambiguous_dispatchable)} ambiguous-but-dispatchable entries; F1 invariant satisfied')
"
```

---

## 4. Acceptance Criteria (REVISED-2)

(Existing 1-13 from `-003` carry forward.) Plus:

14. **F1 closure (the invariant):** `dispatchable = (classification != "terminal")`. Default-enabled routing keeps ambiguous entries dispatchable. The two regression tests Codex required (legacy bare-proposal + post_implementation NO-GO) pass with default flag.
15. **F2 closure (post-impl simplification):** classifier is kind-only; status-aware behavior happens implicitly via upstream `compute_actionable_pending` status routing. Acceptance criterion 14 from `-003` is REPLACED by: "`post_implementation*` kinds classify as `dispatchable`; VERIFIED status entries never reach the classifier because they are filtered upstream by status-only routing in `compute_actionable_pending`."
16. **Codex Q2/Q3 (`review`/`verification` tokens):** removed from terminal list; both classify as ambiguous → dispatchable. Two tests prove it.
17. **Reader-column unconditional rendering:** columns rendered regardless of feature flag. Test asserts.
18. **Kebab/snake normalization:** test asserts `post-implementation-report` matches `post_implementation` token after normalization.

---

## 5-10 (preserved from `-003`)

§5 Sequencing, §6 Project Root Boundary, §7 Out of Scope, §8 Rollback Plan unchanged.

§9 Open Questions — REVISED-2 (one):

1. **Tradeoff confirmation:** REVISED-2 prefers false positives (ambiguous → dispatchable) over false negatives (ambiguous → suppressed). The cost: ~36 mixed-kind threads (review + verification + bare proposal occurrences) continue to consume spawn-tokens until their bridge files are migrated to canonical kinds (or the token list is widened in a follow-on slice). The benefit: zero risk of suppressing legitimate Prime work due to misclassification. Is this tradeoff acceptable, or should specific known-ambiguous tokens (`review`, `verification`) be made non-dispatchable explicitly? Default: false-negative-safe (current proposal).

§10 Aligns With — unchanged plus:
- Codex `-004` NO-GO findings F1-F2 (each addressed in §Change Log).
- Codex `-004` open-question answers (Q1-Q2) folded into §1.3, §1.4.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
