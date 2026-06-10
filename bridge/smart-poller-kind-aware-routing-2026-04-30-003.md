REVISED

# Smart-Poller Kind-Aware Routing Refinement (REVISED-1)

**Status:** REVISED (REVISED-1; supersedes `-001` after Codex NO-GO at `-002`)
**Date:** 2026-04-30 (S323)
**Author:** Prime Builder (Claude, current session)
**Trigger:** Codex NO-GO at `bridge/smart-poller-kind-aware-routing-2026-04-30-002.md` with three blocking findings (F1: classifier reads the wrong file — top GO/NO-GO is an LO verdict file lacking `bridge_kind:`; F2: actual auto-dispatch behavior unchanged in `-001` since consumer was deferred; F3: validation surface requires `bridge_notify_reader.py` updates that `-001` excluded from scope).

bridge_kind: prime_proposal
work_item_ids: [GTKB-SMART-POLLER-KIND-AWARE-ROUTING]
spec_ids: [DCL-SMART-POLLER-AUTO-TRIGGER-001, DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001]
parent_bridge: bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md (VERIFIED)
target_project: gt-kb-platform
implementation_scope: notify.py + bridge_poller_runner.py + bridge_notify_reader.py + tests
requires_review: true
requires_verification: true

---

## Specification Links

(Carried forward from `-001` §Specification Links.) Plus:
- `bridge/smart-poller-kind-aware-routing-2026-04-30-002.md` (Codex NO-GO) — drives this REVISED-1.

---

## Change Log Vs `-001`

| Change | Driving finding | Section |
|---|---|---|
| **Classifier reads bridge_kind from the operative Prime proposal version**, not the top file. New helper `find_operative_prime_version(document)` returns the latest version with status NEW or REVISED (ordered most-recent-first; documents store top-of-list as v[0]). The classifier reads `bridge_kind:` from THAT file. Falls back to top-file read for documents whose only versions are GO/NO-GO/VERIFIED (rare; treated as ambiguous). | F1 | §1.1, §1.2, test mapping |
| **Dispatch consumer filter included in this same slice** (no follow-on slice). `bridge_poller_runner._dispatch_if_needed` now filters its `pending_by_recipient` lists on `entry.dispatchable` BEFORE signature check + spawn. The filter is gated by feature flag `GTKB_NOTIFY_KIND_AWARE_ROUTING` (default `1`); `=0` disables filtering and matches pre-refinement behavior. The actual token-cost reduction lands in this slice. | F2 | §1.3, test mapping |
| **`scripts/bridge_notify_reader.py` included in scope.** `format_orient_section` extends the orient table with `Dispatchable` and `Classification` columns. Test coverage proves the table renders both. | F3 | §1.4, §Files Touched, test mapping |
| Test mapping expanded: per-kind dispatch fixtures (terminal `candidate_spec_intake` GO verdict whose reviewed proposal carries the kind; dispatchable `implementation_proposal` GO verdict whose reviewed proposal carries the kind; NO-GO revision-needed verdict; legacy no-kind fallback). | F1, F2, F3, Codex Q1 | test mapping |
| `review` and `verification` token confirmation tests added per Codex Q2/Q3. | Codex Q2/Q3 | test mapping |
| Reader-render tests added so schema-v3 fields display per Codex Q6 (do not rely on "unknown JSON fields ignored"). | Codex Q6, F3 | test mapping |

All sections of `-001` not listed above are preserved unchanged.

---

## Specification-Derived Verification (Linked-Spec-to-Test Matrix — REVISED)

| Linked spec / rule / record | Derived test | Coverage rationale |
|---|---|---|
| **DCL-SMART-POLLER-AUTO-TRIGGER-001** ("auto-triggers when work waits, never when idle") | (per-kind, all NEW) `test_dispatchable_excludes_terminal_candidate_spec_intake_GO_verdict_chain` + `test_dispatchable_excludes_terminal_scoping_GO_verdict_chain` + `test_dispatchable_excludes_closure_GO_verdict_chain` + `test_dispatchable_includes_implementation_proposal_GO_verdict_chain` + `test_dispatchable_includes_implementation_proposal_NO_GO_verdict_chain` + `test_dispatchable_includes_implementation_slice_GO_verdict_chain`. **Each fixture models a real bridge chain: top is a GO/NO-GO verdict file lacking bridge_kind; reviewed-proposal version carries the canonical bridge_kind.** Per Codex F1. | Per-kind classification correctness against the real verdict-vs-proposal pattern. |
| **DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001** | `test_dispatch_consumer_skips_terminal_entries` + `test_dispatch_consumer_includes_dispatchable_entries` + `test_dispatch_consumer_falls_back_to_status_only_for_ambiguous` — exercise `bridge_poller_runner._dispatch_if_needed` with a mixed pending list; assert spawn fires only for dispatchable entries. **This is the test that proves the operational fix lands in this slice (per Codex F2).** | Mechanical enforcement of the "auto-trigger when work waits" intent. |
| **F1: operative-proposal resolution** | `test_find_operative_prime_version_returns_latest_REVISED` + `test_find_operative_prime_version_returns_latest_NEW_when_no_REVISED` + `test_find_operative_prime_version_returns_None_when_no_NEW_or_REVISED` + `test_find_operative_prime_version_skips_codex_authored_GO_NO_GO_VERIFIED` | Version-traversal correctness. |
| **F2: dispatch consumer filter** | `test_dispatch_consumer_signature_uses_filtered_list` — when filtering changes the pending list, signature changes and a fresh dispatch fires; when filtering removes everything, dispatch records `no_pending` instead of spawning. | Spawn behavior is gated on the filtered list, not the raw list. |
| **F3: reader column rendering** | `test_format_orient_section_includes_dispatchable_column` + `test_format_orient_section_includes_classification_column` + `test_format_orient_section_renders_terminal_entries_with_visible_marker` (e.g., row prefix `(terminal)`) | Reader surface displays the new fields. |
| **Codex Q2 (`review` token)** | `test_review_kind_classifies_as_terminal` — fixture using `bridge_kind: review` (rare but real). | Token correctness. |
| **Codex Q3 (`verification` vs `post_implementation`)** | `test_verification_kind_classifies_as_terminal` + `test_post_implementation_report_kind_classifies_as_dispatchable_when_NO_GO` + `test_post_implementation_report_kind_classifies_as_terminal_when_VERIFIED` | Implementation reports must NOT be accidentally suppressed when their NO-GO needs Prime fix. |
| **Codex Q4 (bare `proposal`)** | `test_bare_proposal_kind_classifies_as_ambiguous_with_status_only_fallback` + `test_classification_field_records_ambiguous_explicitly` | Bare proposal preserves legacy behavior; classification field records ambiguity per Codex Q4 second clause. |
| **Codex Q6 (schema-v3 readers updated together)** | `test_canonical_reader_returns_schema_v3_artifact_with_new_fields` + `test_format_orient_section_handles_schema_v3` (and rejects v2 explicitly) — proves all readers updated. | Schema bump completeness. |
| **`DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`** (carried forward) | `test_routing_docstring_cites_delib_s319_and_this_refinement` | Audit trail preservation. |
| **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** | `test_routing_output_is_deterministic_for_identical_input` (three consecutive calls produce byte-identical output) | Determinism is the property. |
| **GOV-FILE-BRIDGE-AUTHORITY-001** | `test_routing_makes_zero_writes_to_bridge_index_md` | Read-only contract. |
| **`.claude/rules/project-root-boundary.md`** | `test_routing_reads_no_files_outside_e_gt_kb` | Path discipline. |
| **`.claude/rules/file-bridge-protocol.md`** | Procedural for proposal author. | **Waiver: review-only / no derived test.** |
| **`.claude/rules/bridge-essential.md`** (no INDEX mutation) | Covered by `test_routing_makes_zero_writes_to_bridge_index_md`. | No separate test. |
| **`.claude/rules/codex-review-gate.md`** | Procedural. | **Waiver: review-only / no derived test.** |
| **Frontmatter parser robustness** | `test_frontmatter_parser_extracts_bridge_kind` + `test_frontmatter_parser_handles_missing_bridge_kind` + `test_frontmatter_parser_handles_unrecognized_bridge_kind` + `test_frontmatter_parser_handles_malformed_file` | Parser. |
| **Feature-flag fallback** (env var `GTKB_NOTIFY_KIND_AWARE_ROUTING`) | `test_kind_aware_routing_disabled_falls_back_to_status_only_in_dispatch` (`=0` → original spawn behavior preserved) + `test_kind_aware_routing_enabled_by_default_filters_dispatch` (default → filtered spawn) | Safe rollback. |
| **Backward compatibility (existing tests)** | Existing `test_bridge_notify.py` + `test_bridge_poller_runner.py` continue to pass after parameter additions. | Non-regression. |

Release-gate inclusion: `python scripts/release_candidate_gate.py --skip-frontend` runs the full bridge-poller test suite.

---

## Prior Deliberations

(Carried forward from `-001`.) Plus:
- `bridge/smart-poller-kind-aware-routing-2026-04-30-002.md` (Codex NO-GO) — drives this REVISED-1.

---

## 1. Implementation Design (REVISED — F1 + F2 + F3 fixes)

### 1.1 Bridge-Kind Resolution from the Operative Prime Proposal (per Codex F1)

```python
def find_operative_prime_version(doc: BridgeDocument) -> BridgeVersion | None:
    """Return the latest Prime-authored version (NEW or REVISED) in the document.
    
    BridgeDocument.versions is ordered most-recent-first. Status NEW and REVISED
    are Prime-authored; GO, NO-GO, VERIFIED are Codex-authored verdict files
    that do not carry bridge_kind: metadata.
    
    Returns None if the document has no NEW/REVISED versions (rare; e.g., a
    thread initialized by a Codex-authored entry).
    """
    for version in doc.versions:
        if version.status in (BridgeStatus.NEW, BridgeStatus.REVISED):
            return version
    return None


def classify_document_dispatchability(
    project_root: Path,
    doc: BridgeDocument,
) -> Literal["dispatchable", "terminal", "ambiguous"]:
    """Classify whether the document's current top entry should auto-dispatch.
    
    Reads bridge_kind from the operative Prime proposal version (latest NEW or
    REVISED), NOT from the top file (which is typically a Codex verdict file
    without bridge_kind). Per Codex F1.
    
    Returns:
    - "dispatchable" — auto-dispatch SHOULD spawn a harness
    - "terminal" — auto-dispatch SHOULD NOT spawn (notification surface preserved)
    - "ambiguous" — fall back to status-only routing (current behavior)
    """
    operative = find_operative_prime_version(doc)
    if operative is None:
        return "ambiguous"
    
    full_path = project_root / operative.file_path
    try:
        with full_path.open("r", encoding="utf-8") as fh:
            head = fh.read(4096)
    except (OSError, UnicodeDecodeError):
        return "ambiguous"
    
    bridge_kind = _extract_bridge_kind(head)
    if not bridge_kind:
        return "ambiguous"
    
    bk_lower = bridge_kind.lower()
    
    # Terminal tokens (most specific first; "scoping" matches before
    # "implementation_scoping" suffix shape; "candidate_spec_intake" matched as
    # exact substring).
    for token in _KIND_TERMINAL_ON_GO_TOKENS:
        if token in bk_lower:
            return "terminal"
    
    for token in _KIND_DISPATCHABLE_ON_GO_TOKENS:
        if token in bk_lower:
            return "dispatchable"
    
    return "ambiguous"
```

(Token lists unchanged from `-001` §1.1.)

### 1.2 `compute_actionable_pending` updated to use document-level classification

```python
def compute_actionable_pending(
    parse_result: ParseResult,
    *,
    project_root: Path,
) -> tuple[list[ActionablePending], list[ActionablePending]]:
    """Compute current-state actionable pending entries with kind-aware classification.
    
    Per Codex F1 (REVISED-1): classification reads bridge_kind from the operative
    Prime proposal version within the document, NOT the top verdict file.
    """
    actionable_for_prime: list[ActionablePending] = []
    actionable_for_codex: list[ActionablePending] = []
    
    for doc in parse_result.documents:
        if not doc.versions:
            continue
        top = doc.versions[0]
        if not (project_root / top.file_path).is_file():
            continue
        
        # NEW per F1: classify from the operative Prime proposal, not top file.
        classification = classify_document_dispatchability(project_root, doc)
        dispatchable = (classification == "dispatchable") or (
            classification == "ambiguous" and _kind_aware_routing_disabled()
        )
        # When the feature flag is OFF, treat all entries as dispatchable
        # (preserves pre-refinement behavior). When ON, ambiguous entries fall
        # through to status-only routing — but the SPAWN consumer treats
        # ambiguous as dispatchable to avoid suppressing legacy bridges
        # that haven't been migrated yet. Tests assert this.
        
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

### 1.3 Dispatch Consumer Filter (per Codex F2)

In `groundtruth-kb/scripts/bridge_poller_runner.py`, modify `_dispatch_if_needed`:

```python
def _dispatch_if_needed(
    *,
    state_dir: Path,
    project_root: Path,
    run_id: str,
    pending_by_recipient: dict[BridgeAgent, list[ActionablePending]],
    max_items: int,
) -> dict[str, object]:
    state = _load_dispatch_state(state_dir)
    # ... (existing setup unchanged) ...
    
    for recipient, items in pending_by_recipient.items():
        # NEW per F2: filter on dispatchable BEFORE signature check.
        # Feature flag GTKB_NOTIFY_KIND_AWARE_ROUTING (default 1) gates this;
        # =0 reverts to current behavior.
        if _kind_aware_routing_enabled():
            filtered_items = [it for it in items if getattr(it, "dispatchable", True)]
        else:
            filtered_items = list(items)
        
        signature = _pending_signature(filtered_items)
        # ... (rest of existing logic uses filtered_items instead of items) ...
        
        if not filtered_items:
            recipient_state["last_result"] = "no_pending_after_filter" if items else "no_pending"
            results[recipient.value] = {
                "launched": False,
                "reason": "no_pending_after_filter" if items else "no_pending",
                "filtered_terminal_count": len(items) - len(filtered_items),
            }
        elif prior_signature == signature:
            recipient_state["last_result"] = "unchanged"
            results[recipient.value] = {"launched": False, "reason": "unchanged"}
        else:
            launch = _launch_harness(
                # ... pass filtered_items, not items ...
                items=filtered_items,
            )
            # ...
```

The new result code `no_pending_after_filter` makes the cost reduction observable in the audit log: when the filter removes all entries, the audit record makes it visible that the filter (not absence of work) caused the no-spawn.

### 1.4 Reader Column Update (per Codex F3)

In `scripts/bridge_notify_reader.py`, extend `format_orient_section`:

```python
def format_orient_section(artifact: NotificationArtifact | None) -> str:
    # ... (existing absent / empty / version-mismatch checks unchanged) ...
    
    lines = [
        f"### Smart-poller notification — {len(artifact.pending_actions)} pending action(s)",
        "",
        f"_Source: ...; written {artifact.written_at}_",
        "",
        "| Document | Status | File | INDEX line | Dispatchable | Classification |",
        "|---|---|---|---|---|---|",
    ]
    for item in artifact.pending_actions:
        dispatchable_marker = "✓" if getattr(item, "dispatchable", True) else "—"
        classification = getattr(item, "classification", "ambiguous")
        terminal_prefix = "(terminal) " if classification == "terminal" else ""
        lines.append(
            f"| `{terminal_prefix}{item.document_name}` | **{item.top_status}** | "
            f"`{item.top_file}` | {item.index_line_number} | "
            f"{dispatchable_marker} | {classification} |"
        )
    return "\n".join(lines)
```

The terminal-prefix `(terminal)` makes "we're not spawning for this" visible in the orient block. Combined with the `Dispatchable` and `Classification` columns, an owner reading the orient can see exactly which entries the auto-dispatch is intentionally skipping.

### 1.5 Schema v3 (unchanged from `-001` §1.3)

Per Codex Q6 acceptance: schema bump 2 → 3. All in-repo readers and tests updated together. The defensive `schema_version != NOTIFY_SCHEMA_VERSION` check in `format_orient_section:64` continues to work: when this slice updates `NOTIFY_SCHEMA_VERSION = 3` in `notify.py`, the reader auto-tracks because it imports the constant. Existing v2-on-disk artifacts (none in production; only test fixtures) will fall through the version check and produce empty sections — this is intentional defensive behavior.

### 1.6 Feature Flag (REVISED per F2 — flag now gates dispatch consumer too)

`GTKB_NOTIFY_KIND_AWARE_ROUTING` (default `1`):
- `=1` (default): kind-aware classification computed; dispatch consumer filters on `dispatchable`; reader renders new columns.
- `=0`: classification step still computes (no harm), but dispatch consumer treats all entries as dispatchable. Reader still renders columns. Equivalent to pre-refinement behavior in the spawn path.

The flag is a *consumer-gating* flag, not a *computation-gating* flag — kind-aware metadata is always emitted (no harm), but consumers only act on it when the flag is set.

---

## 2. Files Touched (REVISED per F2 + F3)

**Modified (groundtruth-kb package — gt-kb-platform code):**
- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` — add `_extract_bridge_kind`, `find_operative_prime_version`, `classify_document_dispatchability`, the `dispatchable` + `classification` fields on `ActionablePending`, schema-v3 bump, feature-flag helpers (~120 LOC added).
- `groundtruth-kb/scripts/bridge_poller_runner.py` — modify `_dispatch_if_needed` to filter on `dispatchable` before spawn (~25 LOC added).
- `groundtruth-kb/tests/test_bridge_notify.py` — add tests per §Spec-Derived Verification (~250 LOC added).
- `groundtruth-kb/tests/test_bridge_poller_runner.py` — add dispatch-filter tests (~80 LOC added).

**Modified (Agent-Red-side repo scripts):**
- `scripts/bridge_notify_reader.py` — extend orient table with `Dispatchable` + `Classification` columns + `(terminal)` row prefix (~15 LOC added).

**NOT touched:**
- `bridge/INDEX.md` — runner is read-only.
- Existing schema-v2 readers — none in production.

---

## 3. Verification Plan

### 3.1 Tests (per Spec-Derived Verification matrix)

```bash
PYTHONIOENCODING=utf-8 python -m pytest \
  --rootdir=E:/GT-KB/groundtruth-kb \
  --override-ini=testpaths=tests \
  E:/GT-KB/groundtruth-kb/tests/test_bridge_notify.py \
  E:/GT-KB/groundtruth-kb/tests/test_bridge_poller_runner.py \
  -v --tb=short
```

All tests in §Spec-Derived Verification must pass.

### 3.2 Production-State Validation (post-impl) — REVISED per F3

After landing, the post-impl report must show the JSON artifact directly (not just the reader output, which was the F3 problem):

```bash
# JSON artifact (authoritative; shows new fields explicitly)
cat .gtkb-state/bridge-poller/notifications/pending-bridge-action-prime.json | python -m json.tool

# Reader output (UI surface; should now have Dispatchable + Classification columns)
python scripts/bridge_notify_reader.py
```

The first command MUST show `dispatchable` and `classification` fields per pending action; the second MUST show the columns and `(terminal)` prefix where applicable.

### 3.3 Dispatch Audit Validation (post-impl) — NEW per F2

After landing, the audit log at `.gtkb-state/bridge-poller/audit/audit-{run_id}.jsonl` must show, for at least one run with a known terminal entry, an `_dispatch_if_needed` result code of `no_pending_after_filter` with a non-zero `filtered_terminal_count`. This proves the operational fix is actually firing in production.

### 3.4 Non-Regression

- Existing `test_bridge_notify.py` + `test_bridge_poller_runner.py` tests continue to pass.
- Surface routing (which entries appear in notification artifact) UNCHANGED — terminal entries still appear, just with the new columns indicating dispatch is suppressed.
- "Continue Last Session" startup-disclosure path UNCHANGED — uses surface routing.

---

## 4. Acceptance Criteria (REVISED)

(Existing 1-10 from `-001` carry forward.) Plus:

11. **F1 closure (operative-proposal resolution):** `find_operative_prime_version` returns the latest NEW or REVISED version from the document; classification reads bridge_kind from THAT file. Six fixture-based tests (terminal candidate_spec_intake / scoping / closure GO verdict chains; dispatchable implementation_proposal / implementation_slice GO verdict chains; NO-GO revision-needed verdict) prove the resolution works.
12. **F2 closure (dispatch behavior changes in this slice):** `bridge_poller_runner._dispatch_if_needed` filters its pending list on `dispatchable` before signature/spawn. Three tests prove it (skips_terminal / includes_dispatchable / falls_back_for_ambiguous). Production audit log MUST record `no_pending_after_filter` events when the filter removes entries — this is the observable token-cost reduction.
13. **F3 closure (reader updated):** `format_orient_section` renders `Dispatchable` + `Classification` columns + `(terminal)` row prefix. Three tests prove rendering. Validation command in §3.2 inspects JSON artifact directly (canonical) plus the reader (UI).
14. **Codex Q2/Q3:** `review` and `verification` kinds classify as terminal-on-GO; `post_implementation_report` and variants classify as dispatchable-on-NO-GO (Prime fix expected) and terminal-on-VERIFIED (closure).
15. **Codex Q6:** all in-repo readers + tests updated together for schema-v3.

---

## 5-10 (preserved from `-001`)

§5 Sequencing, §6 Project Root Boundary, §7 Out of Scope, §8 Rollback Plan unchanged from `-001` except:
- §7 Out of Scope: "Auto-dispatch consumer update" REMOVED — now in scope per F2.
- §8 Rollback Plan: feature flag now gates dispatch consumer; setting `=0` reverts spawn behavior to pre-refinement.

§9 Open Questions — REVISED-1 (fewer):

1. **Audit log result code naming:** §1.3 introduces `no_pending_after_filter` as a new result. Acceptable, or prefer a different name (e.g., `filtered_to_zero`)?
2. **Feature flag scope:** the flag now gates dispatch consumer behavior. Should it ALSO gate the reader column rendering (so `=0` shows the old reader without new columns)? §1.4 currently always renders columns regardless of flag. Codex preference?

§10 Aligns With — unchanged plus:
- Codex `-002` NO-GO findings F1-F3 (each addressed in §Change Log).
- Codex `-002` open-question answers (Q1-Q6) folded into §1 + test mapping.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
