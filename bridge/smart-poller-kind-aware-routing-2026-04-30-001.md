NEW

# Smart-Poller Kind-Aware Routing Refinement

**Status:** NEW (implementation proposal)
**Date:** 2026-04-30 (S323)
**Author:** Prime Builder (Claude, current session)
**Trigger:** Owner directive 2026-04-29 (S323):
> "The poller is treating all latest GO / NO-GO entries as Prime-actionable. That over-flags stale or terminal governance/scoping entries. The latest Prime auto-dispatch explicitly reported its two selected entries as stale and took no bridge action. ... the poller should be treated as a notification aid rather than a fully correct bridge work dispatcher."

Owner additionally prioritized this fix on cumulative-token-cost grounds: every false-positive auto-dispatch costs ~50k tokens; over a busy day this compounds to the same cost class as the S308 retired-OS-poller incident.

bridge_kind: prime_proposal
work_item_ids: [GTKB-SMART-POLLER-KIND-AWARE-ROUTING]
spec_ids: [DCL-SMART-POLLER-AUTO-TRIGGER-001, DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001]
parent_bridge: bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md (VERIFIED) — original smart poller activation
target_project: gt-kb-platform (notify.py is `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` — platform code)
implementation_scope: notify.py refinement + frontmatter parser + tests
requires_review: true
requires_verification: true

---

## Specification Links

Per `.claude/rules/file-bridge-protocol.md` Mandatory Specification Linkage Gate.

**Primary specs served:**
- `DCL-SMART-POLLER-AUTO-TRIGGER-001` — "Smart poller auto-triggers harness when work waits, never when idle". KB-resolved. The current routing violates the intent: it triggers harnesses for entries where no work waits (terminal scoping GOs, closure GOs, candidate-intake GOs).
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` — mandatory mechanical enforcement when documented intent exists. KB-resolved. The "auto-trigger only when work waits" intent currently has no mechanical enforcement beyond the simple status-set membership check.

**Parent bridge:**
- `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` (VERIFIED) — original smart-poller activation that landed `notify.py`'s current routing rule.
- `bridge/gtkb-bridge-poller-p3-notify-2026-04-29-008.md` (GO at REVISED-3) — original notify-module GO that established the simple status-set routing.

**Governance specs / records that constrain this work:**
- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge/INDEX.md is canonical state; notify.py reads INDEX.md only.
- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION` — owner clarification of smart-poller dispatch objective; current docstring at `notify.py:19-24` cites this. This refinement carries the same DELIB.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — deterministic CLI / library behavior; the new routing must be deterministic (same INDEX state + same on-disk files → same classification).
- `DELIB-S308-OS-POLLER-TOKEN-REGRESSION` (substance basis: `.claude/rules/bridge-essential.md` §"Incident History" S308 entry) — token cost is a first-class operational metric; this proposal addresses cumulative auto-dispatch cost.

**Adjacent / parallel work:**
- `bridge/spawned-harness-role-defer-durable-record-2026-04-29-004.md` (GO) — different aspect of smart-poller dispatch (role source). This refinement is orthogonal: role-source and entry-classification are independent dispatch dimensions.

**Rule files that constrain this work:**
- `.claude/rules/project-root-boundary.md` — all artifacts under `E:\GT-KB`.
- `.claude/rules/file-bridge-protocol.md` — defines status vocabulary the routing parses.
- `.claude/rules/bridge-essential.md` — `INDEX.md` is canonical; routing must not mutate it.
- `.claude/rules/codex-review-gate.md` — Codex review skill consumes routing output via notification artifacts.

---

## Specification-Derived Verification (Linked-Spec-to-Test Matrix)

Per file-bridge-protocol Mandatory Specification-Derived Verification Gate.

| Linked spec / rule / record | Derived test | Coverage rationale |
|---|---|---|
| **DCL-SMART-POLLER-AUTO-TRIGGER-001** ("auto-trigger when work waits, never when idle") | `test_dispatchable_excludes_terminal_scoping_GO` + `test_dispatchable_excludes_closure_GO` + `test_dispatchable_excludes_candidate_intake_GO` + `test_dispatchable_includes_implementation_proposal_GO` + `test_dispatchable_includes_implementation_proposal_NO_GO` | Each test exercises a specific bridge_kind class; the routing must include the actionable kinds and exclude the terminal/scoping kinds. |
| **DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001** | `test_routing_uses_bridge_kind_when_present` + `test_routing_falls_back_to_status_only_when_kind_missing` | Mechanical = the routing IS the kind-classifier. Fallback covers bridges without `bridge_kind:`. |
| **`notify.py` routing contract** (parent docstring + AGENTS.md:153-159) | `test_notification_artifact_surfaces_all_actionable_for_recipient` (existing; carries forward) + `test_notification_artifact_marks_dispatchable_subset_separately` (NEW) | Surfacing for "Continue Last Session" remains intact; auto-dispatch consumes the new dispatchable subset. |
| **`DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION`** (carried forward from current `notify.py:19-24` docstring) | `test_routing_docstring_cites_delib_s319_and_this_refinement` (asserts module docstring carries both citations after refinement) | Audit trail preservation. |
| **`DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`** | `test_routing_output_is_deterministic_for_identical_input` — three consecutive calls with the same `parse_result` + same on-disk frontmatter produce byte-identical output. | Determinism is the property. |
| **GOV-FILE-BRIDGE-AUTHORITY-001 (no INDEX mutation)** | `test_routing_makes_zero_writes_to_bridge_index_md` | Read-only contract. |
| **`.claude/rules/project-root-boundary.md`** | `test_routing_reads_no_files_outside_e_gt_kb` — frontmatter-parsing path uses only `project_root`-relative `top.file_path`. | Path discipline. |
| **`.claude/rules/file-bridge-protocol.md`** | Procedural for proposal-author, not runtime invariant. | **Waiver: review-only / no derived test.** |
| **`.claude/rules/bridge-essential.md`** (no mutation of INDEX) | Covered by `test_routing_makes_zero_writes_to_bridge_index_md` above. | No separate test needed. |
| **`.claude/rules/codex-review-gate.md`** | Procedural. | **Waiver: review-only / no derived test.** |
| **Frontmatter parser correctness** | `test_frontmatter_parser_extracts_bridge_kind` + `test_frontmatter_parser_handles_missing_bridge_kind` + `test_frontmatter_parser_handles_unrecognized_bridge_kind` + `test_frontmatter_parser_handles_malformed_file` | Parser robustness. |
| **Feature-flag fallback** (env var `GTKB_NOTIFY_KIND_AWARE_ROUTING`) | `test_kind_aware_routing_disabled_falls_back_to_status_only` (`=0` → original behavior) + `test_kind_aware_routing_enabled_by_default` (env unset → kind-aware) | Safe rollback path; matches Codex Q3 pattern from prior REVISED-1 acceptance. |
| **Backward compatibility (existing tests)** | Existing `test_bridge_notify.py` + `test_bridge_poller_runner.py` continue to pass without modification (or with minimal parameter additions). | Non-regression on the canonical surface. |

Release-gate inclusion: `python scripts/release_candidate_gate.py --skip-frontend` runs the full bridge-poller test suite.

---

## Prior Deliberations

Per `.claude/rules/deliberation-protocol.md`:

- **Owner directive 2026-04-29 (S323):** the routing-defect observation that drives this proposal. To be archived as `DELIB-S323-SMART-POLLER-KIND-AWARE-ROUTING-DIRECTIVE` at session-wrap.
- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION` — current routing docstring cites this; carried forward.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — supports the deterministic per-kind classifier.
- `bridge/gtkb-bridge-poller-notify-activation-2026-04-29-012.md` (VERIFIED) — parent activation; demonstrates pattern.
- No prior deliberation reverses this approach.

---

## 1. Implementation Design

### 1.1 Bridge-Kind Classification

The current `notify.py` routes solely on `top.status`. This refinement adds a `bridge_kind`-aware classifier. The vocabulary is messy (25+ distinct values across existing bridges); rather than canonicalize all of them, the classifier uses **substring grouping**:

```python
# Substring tokens checked against the lowercased bridge_kind value.
# Order matters: most specific first.
_KIND_TERMINAL_ON_GO_TOKENS: Final[tuple[str, ...]] = (
    "scoping",                  # implementation_scoping, governance_scoping_proposal, scoping_proposal, scoping_addendum
    "closure",
    "parking",                  # parking_acknowledgement
    "index_reconciliation",
    "thread_reconciliation",
    "operational_state_change",
    "candidate_spec_intake",    # owner approves candidates; not Prime impl
    "verification",             # standalone verification reports without follow-up
    "review",                   # Codex review file (rare bridge_kind value)
)

_KIND_DISPATCHABLE_ON_GO_TOKENS: Final[tuple[str, ...]] = (
    "implementation_proposal",
    "implementation_slice",
    "multiphase_implementation",
    "fix",
    "governance_proposal",      # NOT governance_scoping_proposal (matched first by terminal)
    "architecture_proposal",
)

# Generic "proposal" alone is ambiguous — defer to status-only fallback rather
# than risk false negatives on bridges that use the bare term.

def classify_top_file_dispatchability(
    project_root: Path,
    top_file_path: str,
    top_status: str,
) -> Literal["dispatchable", "terminal", "ambiguous"]:
    """Classify whether the top entry is genuinely actionable for auto-dispatch.

    Reads the bridge_kind: field from the top file's header. Returns:
    - "dispatchable" — auto-dispatch SHOULD spawn a harness for this entry
    - "terminal" — auto-dispatch SHOULD NOT spawn for this entry (notification
      surface still includes it for "Continue Last Session" continuity)
    - "ambiguous" — fall back to status-only (current behavior); typically
      bridges without bridge_kind: or with bare "proposal" / unrecognized values

    Read-only against the top file. Graceful degradation on any read error.
    """
    full_path = project_root / top_file_path
    try:
        with full_path.open("r", encoding="utf-8") as fh:
            # Read up to first 4KB; bridge_kind: is always in the header section
            head = fh.read(4096)
    except (OSError, UnicodeDecodeError):
        return "ambiguous"

    bridge_kind = _extract_bridge_kind(head)
    if not bridge_kind:
        return "ambiguous"

    bk_lower = bridge_kind.lower()

    # Check terminal tokens first (more specific)
    for token in _KIND_TERMINAL_ON_GO_TOKENS:
        if token in bk_lower:
            return "terminal"

    for token in _KIND_DISPATCHABLE_ON_GO_TOKENS:
        if token in bk_lower:
            return "dispatchable"

    return "ambiguous"


def _extract_bridge_kind(header: str) -> str | None:
    """Extract `bridge_kind: <value>` from a markdown header block.
    
    Tolerant of whitespace and YAML-frontmatter or freeform-header placement.
    Returns the trimmed value or None if not found.
    """
    pattern = re.compile(r"^bridge_kind:\s*(\S+)", re.MULTILINE)
    match = pattern.search(header)
    return match.group(1).strip() if match else None
```

### 1.2 Routing Function Refinement

```python
@dataclass(frozen=True)
class ActionablePending:
    """One document's currently-actionable top status for a specific recipient."""
    document_name: str
    top_status: str
    top_file: str
    index_line_number: int
    dispatchable: bool                         # NEW field; True = auto-dispatch eligible
    classification: str                        # NEW field; "dispatchable" / "terminal" / "ambiguous"


def compute_actionable_pending(
    parse_result: ParseResult,
    *,
    project_root: Path,
) -> tuple[list[ActionablePending], list[ActionablePending]]:
    """Compute current-state actionable pending entries with kind-aware dispatchability.
    
    Behavior:
    - Returns the same surface-actionable lists as before (GO/NO-GO → Prime; 
      NEW/REVISED → Codex). This preserves "Continue Last Session" continuity.
    - Each entry carries a NEW `dispatchable` flag computed from the top file's
      bridge_kind:. Auto-dispatch consumers should filter on this flag.
    - Feature flag GTKB_NOTIFY_KIND_AWARE_ROUTING (default 1; "0" disables and
      treats all entries as dispatchable, matching pre-refinement behavior).
    """
    # ... (existing skeleton; kind-aware classification injected per entry) ...
```

### 1.3 Notification Artifact Schema

The JSON artifact gains a new field per entry:

```json
{
  "schema_version": 3,             // bumped from 2
  "recipient": "prime",
  "written_at": "...",
  "poller_run_id": "...",
  "pending_actions": [
    {
      "document_name": "...",
      "top_status": "GO",
      "top_file": "bridge/...",
      "index_line_number": 42,
      "dispatchable": true,         // NEW
      "classification": "dispatchable"  // NEW: "dispatchable" / "terminal" / "ambiguous"
    }
  ],
  "summary": "..."
}
```

Schema version bump from 2 to 3. Existing schema-v2 readers continue to work (new fields optional in the reader).

### 1.4 Auto-Dispatch Consumer Update (out of scope for this slice)

The auto-dispatch logic (in `scripts/run_smart_bridge_poller.ps1` / `scripts/run_smart_bridge_poller.vbs` / wherever the spawn happens) should consult the new `dispatchable` field. **That consumer change is OUT OF SCOPE for this slice;** this slice only adds the classification + schema field. A follow-on slice will update the dispatch consumer once this lands.

Until the consumer slice lands, the new `dispatchable` field is metadata that's ignored — auto-dispatch behavior is unchanged. This is INTENTIONAL: it lets us validate the classification logic in production via observation before any behavior change.

### 1.5 Feature Flag

`GTKB_NOTIFY_KIND_AWARE_ROUTING` (default `1`):
- `=1` (default): kind-aware classification is computed and added to artifacts.
- `=0`: classification step is skipped; all entries get `dispatchable: true` and `classification: "ambiguous"`. Equivalent to pre-refinement behavior.

Environment-variable-based, settable via `.env.local`, no code change required to disable.

---

## 2. Files Touched

**Modified (groundtruth-kb package — gt-kb-platform code):**
- `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` — add `_extract_bridge_kind`, `classify_top_file_dispatchability`, the `dispatchable` + `classification` fields on `ActionablePending`, and the schema-v3 bump (~80 LOC added).
- `groundtruth-kb/tests/test_bridge_notify.py` — add tests per §Spec-Derived Verification (~150 LOC added).

**Modified (release gate):**
- `scripts/release_candidate_gate.py` — already runs `groundtruth-kb/tests/test_bridge_notify.py`; no wiring change.

**NOT touched (per scope discipline):**
- Auto-dispatch consumers (PS1 / VBS / spawn logic) — out of scope; follow-on slice.
- `scripts/bridge_notify_reader.py` — already tolerant of unknown JSON fields per Python json semantics; no change required.
- Existing schema-v2 readers — backward-compatible; new fields are optional.
- `.claude/settings.json` / `.codex/hooks.json` — no hook registration change.
- `bridge/INDEX.md` — runner is read-only.

---

## 3. Verification Plan

### 3.1 Tests (per Spec-Derived Verification matrix)

```bash
PYTHONIOENCODING=utf-8 python -m pytest \
  --rootdir=E:/GT-KB/groundtruth-kb \
  --override-ini=testpaths=tests \
  E:/GT-KB/groundtruth-kb/tests/test_bridge_notify.py -v --tb=short
```

All tests in §Spec-Derived Verification must pass.

### 3.2 Production-State Validation (post-impl)

After landing, the post-impl report must include a snapshot of the live notification artifact for Prime:

```bash
python scripts/bridge_notify_reader.py
```

The output must show, for each currently-pending GO/NO-GO entry:
- `document_name`
- `top_status`
- `dispatchable` (true / false)
- `classification` ("dispatchable" / "terminal" / "ambiguous")

The owner can then verify the classification matches reality. If specific entries are misclassified, the substring-token lists in §1.1 can be tuned in a follow-on slice.

### 3.3 Non-Regression

- Existing surface routing (which entries appear in the notification artifact) UNCHANGED — `dispatchable=False` entries still appear, just with the new field set to false.
- "Continue Last Session" startup-disclosure path UNCHANGED — uses the surface routing.
- Auto-dispatch behavior UNCHANGED in this slice — consumer not yet updated.

---

## 4. Acceptance Criteria

1. **Functional:** all tests in §Spec-Derived Verification pass.
2. **Frontmatter parsing:** `_extract_bridge_kind` correctly extracts the value from headers in YAML-frontmatter, freeform-header, and missing-field cases.
3. **Substring classification:** the dispatchable/terminal token lists in §1.1 cover the top 10 most-frequent bridge_kind values per the inventory at S323 (`scoping*`, `closure`, `implementation_proposal`, `implementation_slice`, `post_implementation*`, `fix`, `governance_*`, `candidate_spec_intake`, `verification`, `review`).
4. **Schema bump:** notification JSON artifact carries `schema_version: 3` and includes `dispatchable` + `classification` fields per entry.
5. **Backward compatibility:** schema-v2 readers continue to parse the artifact (new fields are optional).
6. **Feature flag:** `GTKB_NOTIFY_KIND_AWARE_ROUTING=0` reverts to pre-refinement behavior (all entries `dispatchable: true`).
7. **Determinism:** three consecutive calls with the same input produce byte-identical output.
8. **Read-only contract:** zero writes to `bridge/INDEX.md`, zero writes outside `E:\GT-KB`.
9. **Surface preservation:** existing `compute_actionable_pending` recipient lists unchanged — kind-aware classification only adds metadata, doesn't filter the lists.
10. **Codex consumability:** notification artifact format documented + readable by both `bridge_notify_reader.py` and any review-skill prompt that reads JSON.

---

## 5. Sequencing and Concurrency

Internal: single coherent slice (notify.py + tests).

External:
- Independent of in-flight bridges. No file-collisions with the 3 active REVISEDs (verified-runner, candidate-spec-intake, decision-tracker) or the umbrella threads.
- **Follow-on slice (separate bridge after VERIFIED):** auto-dispatch consumer update — modify the spawn logic to filter on `dispatchable=true` before spawning a harness. That's where the actual token-cost reduction lands.

Concurrency: `notify.py` is read-mostly; only writes are atomic-rename of notification artifacts (pre-existing pattern).

---

## 6. Project Root Boundary

Per `.claude/rules/project-root-boundary.md`:
- All new and modified files under `E:\GT-KB`.
- Platform code: `groundtruth-kb/src/groundtruth_kb/bridge/notify.py` + `groundtruth-kb/tests/test_bridge_notify.py`.
- **Not Agent Red application code:** no files under `applications/Agent_Red/`. notify.py governs ALL bridges across the platform.
- Frontmatter reads use `project_root`-relative paths from the existing `top.file_path`; no new path discipline needed.

---

## 7. Out of Scope

- **Auto-dispatch consumer update** (the actual spawn-filtering) — separate follow-on bridge after this slice VERIFIED. This slice produces the classification metadata; the next slice consumes it.
- **bridge_kind vocabulary canonicalization** — too disruptive for this slice (would touch every bridge file). The substring-grouping approach in §1.1 absorbs the messy vocabulary.
- **Staleness detection** (entries past N days old without follow-up activity) — separate feature; orthogonal to kind classification.
- **Owner-decision-tracker false-positive cleanup** (the 23 pending-decisions accumulator) — separate scope; addressed by `gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md` which is in Codex's queue.
- **Codex's parallel auto-dispatch** — Codex consumes its own notification artifact. The schema bump is forward-compatible; Codex's reader already ignores unknown fields. No coordination needed for this slice.

---

## 8. Rollback Plan

To revert this slice without code change:
- Set environment variable `GTKB_NOTIFY_KIND_AWARE_ROUTING=0` (in `.env.local` or shell). The new fields are still emitted for compatibility, but classification is forced to "ambiguous" / dispatchable=true. Equivalent to pre-refinement behavior.

To revert entirely:
1. `git revert <impl-commit>` reverts both notify.py changes and the new tests.
2. Schema reverts to v2.
3. No KB or DA state affected.

---

## 9. Open Questions for Loyal Opposition Review

1. **Substring grouping vs. canonicalization:** §1.1 uses substring tokens against the lowercased bridge_kind. This is fast to ship but risks false negatives on novel bridge_kind values. Codex preference: keep substring approach (this slice) and propose canonicalization as a follow-on, OR fold canonicalization into this slice?
2. **The `review` token in `_KIND_TERMINAL_ON_GO_TOKENS`:** `bridge_kind: review` (28 occurrences) is used by Codex review files. Routing them as terminal-on-GO seems correct (a review GO is the verdict, not Prime work). Confirm or flag?
3. **The `verification` token in `_KIND_TERMINAL_ON_GO_TOKENS`:** `bridge_kind: verification` (8 occurrences) is similar. Confirm or flag?
4. **Bare `proposal` (41 occurrences):** §1.1 defers bare-proposal to "ambiguous" → falls back to status-only routing (current behavior). Acceptable, or should bare proposal default to "dispatchable" since the historical precedent has been "GO on a proposal means impl"?
5. **Frontmatter read budget:** §1.1 reads up to 4KB of header. This adds ~16ms × N-documents to the routing call (N is typically 25). Acceptable per-poll cost?
6. **Schema-version bump (2 → 3):** is the bump warranted here, or should the new fields be optional within v2 for back-compat-by-default? §1.3 chose v3 to make the contract explicit.

---

## 10. Aligns With

- `DCL-SMART-POLLER-AUTO-TRIGGER-001` (auto-trigger only when work waits — this fix actualizes the intent).
- `DCL-MECHANICAL-ENFORCEMENT-MANDATORY-001` (mechanical enforcement of the smart-poller objective).
- `DELIB-S319-SMART-POLLER-OBJECTIVE-CLARIFICATION` (carries forward; cited in updated docstring).
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (deterministic kind classifier).
- Owner directive 2026-04-29 (S323) — substance basis.
- `feedback_smart_poller_advisory_only.md` (auto-memory) — captures the same observation in human-readable form.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
