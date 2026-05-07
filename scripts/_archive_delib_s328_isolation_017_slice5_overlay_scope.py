# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Archive DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE.

Captures the S328 owner AskUserQuestion decision authorizing partial
deferral of the 3 Phase 6 overlay tests originally bound to Slice 5 by
the scoping bridge `gtkb-isolation-017-scoping-003.md` lines 143-145.

Per Codex `gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-002.md`
F1 NO-GO: the original Slice 5 NEW (`-001`) deferred all 3 overlay tests
without an owner-approved scoping revision. This DELIB IS that scoping
revision. REVISED-1 (`-003`) cites this DELIB as the supersession authority.

Run: python scripts/_archive_delib_s328_isolation_017_slice5_overlay_scope.py \\
       --formal-approval-packet \\
       .groundtruth/formal-artifact-approvals/2026-05-03-isolation-017-slice5-overlay-scope.json
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402
from scripts._kb_attribution import resolve_changed_by  # noqa: E402

DELIB_ID = "DELIB-S328-ISOLATION-017-SLICE5-OVERLAY-SCOPE-REVISION-OWNER-DIRECTIVE"

CONTENT = """## Context

GTKB-ISOLATION-017 scoping bridge `bridge/gtkb-isolation-017-scoping-003.md` (Codex GO at `-004`) §"Slice 5 — Clean-adopter test suite + CI wiring + overlay tests" lines 133-149 binds Slice 5 to deliver 3 Phase 6 overlay tests:

- Phase 6 overlay refresh test (line 143).
- Phase 6 overlay stale-detection test (line 144).
- Phase 6 overlay disposability test (line 145).

Per Phase 9 §"Exit Criteria" §4 lines 346-348: "Phase 6 overlay refresh and stale detection behave as specified for the clean adopter: overlays refresh on demand, stale overlays emit warnings, and overlays are disposable."

## Probe finding (S328, 2026-05-03)

Live source probe of `groundtruth-kb/src/`:

- `grep -rE "def.*overlay|class.*Overlay" groundtruth-kb/src/`: 0 matches.
- `grep -rE "chroma_regen|reindex|chromadb_regen" groundtruth-kb/src/`: 0 matches in the user-facing CLI/library surface; only `scripts/rehearse/_chromadb_regen.py` exists (the Phase 8 rehearsal-driver lane, not an adopter API).

The chroma cache (`.groundtruth-chroma/`) IS the overlay surface per the inventory plan at `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md:234`: "Treat as cache/overlay. It should be disposable and rebuildable from authoritative records."

**Of the 3 overlay tests:**

- **Stale-detection** is implementable today; covered by Slice 1's `_check_isolation_chroma_regeneratable` (check #9, `isolation:chroma-regeneratable`) at `groundtruth-kb/src/groundtruth_kb/project/doctor_isolation.py:515-544`. The test wraps the existing check in the clean-adopter test surface.
- **Refresh on demand** requires a user-facing chroma-regeneration API (e.g., `groundtruth_kb.project.chroma.regenerate(target)` or `gt project chroma regenerate`). Such an API does NOT exist in the current codebase.
- **Disposability** requires the same regeneration API to round-trip "delete cache → regenerate → assert state matches." Same missing capability.

## Owner directive (S328, 2026-05-03 — verbatim)

Surfaced via AskUserQuestion at S328 after Codex `-002` F1 NO-GO. Question (verbatim from prompt):

> "Codex `-002` F1 NO-GO on Slice 5: the scoping bridge GO'd 3 Phase 6 overlay tests (refresh / stale-detection / disposability), but only stale-detection is implementable today (covered by Slice 1's check #9). Refresh + disposability need a user-facing chroma-regeneration API that doesn't exist in the codebase. How should I scope-resolve this for Slice 5 REVISED-1?"

Owner answer (verbatim from response):

> "Implement stale-detection in Slice 5; defer refresh+disposability via owner-approved scoping revision (Recommended)"

Per the option description: "REVISED-1 ships test_overlay_stale_detection.py (1 of 3) wrapping Slice 1's check #9 in the clean-adopter test surface. The other 2 (refresh + disposability) defer to a follow-on slice via this AskUserQuestion as the owner-approved scoping revision (Codex path 2). REVISED-1 cites this DELIB as the supersession authority. Backlog row added for the deferred tests. Pre-Slice-8 freeze applies to the overlay-impl follow-on."

## Resolution: scoping revision authorized

The Slice 5 acceptance criteria from `bridge/gtkb-isolation-017-scoping-003.md` lines 143-145 are revised as follows for the duration of the GTKB-ISOLATION-017 program:

- **Slice 5 retains:** Phase 6 overlay stale-detection test (line 144). Implementable via wrapping Slice 1 check #9 in the clean-adopter test surface.
- **Slice 5 defers:** Phase 6 overlay refresh test (line 143) + Phase 6 overlay disposability test (line 145). Both blocked on the absence of a user-facing chroma-regeneration API.
- **Follow-on slice ("Slice 5.5") authorized** for the deferred 2 tests + the chroma-regeneration API they require. Tracked as a memory/work_list.md row (added at this DELIB archival time). Standard NEW → review → GO → impl → post-impl → VERIFIED bridge cycle when filed. Sequencing: deferred under the GTKB-ISOLATION-017 Slice 8 freeze unless owner elevates.

This DELIB IS the owner-approved scoping revision per Codex `-002` F1 recommended action path 2 ("File or cite an owner-approved requirement/scoping revision that explicitly moves the three overlay tests to a named follow-on slice"). REVISED-1 (`bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-003.md`) cites this DELIB as the governing scoping artifact for the partial-deferral.

## Disposition for downstream slices

- **Slice 6 (docs)**: §"Service-down behavior documentation" + "Overlay fallback semantics documentation" per Phase 9 §6 + §4 lines 351-352. Documentation may forward-reference the deferred Slice 5.5 implementation; not blocking.
- **Slice 7 (examples)**: §"Each example contains a dashboard rendering step that exercises the Phase 6 overlay and Phase 4 service paths together" per Phase 9 §7 line 175. Examples may use the existing overlay-stale-detection contract; live overlay refresh exercise blocks on Slice 5.5 impl.
- **Slice 8 (release closeout)**: post-Phase-9 acceptance gate may exclude the 2 deferred overlay capabilities from the v0.7.0-rc1 release scope, OR include them as a release-version-pin condition. Surfaced to owner at Slice 8 filing time per scoping bridge Decision Map row 5.

## Sequencing constraint

Slice 5.5 (the follow-on slice for refresh + disposability + chroma-regen API) does NOT block the v0.7.0-rc1 release path UNLESS the owner judges those capabilities release-blocking at Slice 8 acceptance-gate time. Default: defer beyond v0.7.0-rc1.

## Cited authorities

- `bridge/gtkb-isolation-017-scoping-003.md` lines 143-145 (original Slice 5 acceptance criteria — partially revised here).
- `bridge/gtkb-isolation-017-scoping-004.md` (Codex GO on the original scoping).
- `bridge/gtkb-isolation-017-slice5-clean-adopter-tests-2026-05-03-002.md` (Codex `-002` NO-GO F1 — the immediate driver).
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-APPLICATION-ISOLATION-INVENTORY-AND-PHASE-PLAN-2026-04-22.md:234` (chroma-as-overlay framing).
- `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/GTKB-ISOLATION-009-PHASE9-ADOPTER-PACKAGING-AND-VALIDATION-PLAN-2026-04-23.md` lines 346-348 (overlay-behavior contract).
- `feedback_scope_reduction_as_no_go_response.md` (S315) — applied here in the proactive form: claim less than evidence supports, defer to follow-on slice with explicit owner approval.
"""

SUMMARY = (
    "S328 owner AskUserQuestion decision authorizing partial deferral of 2 of 3 "
    "Phase 6 overlay tests originally bound to GTKB-ISOLATION-017 Slice 5 by "
    "scoping bridge `-003` lines 143-145. Stale-detection (Slice 1 check #9 wrap) "
    "stays in Slice 5; refresh + disposability defer to a named follow-on slice "
    "(Slice 5.5) due to absent user-facing chroma-regeneration API. This DELIB "
    "IS the supersession authority per Codex `-002` F1 path 2; REVISED-1 (-003) "
    "cites it. Slice 5.5 sequencing: deferred beyond v0.7.0-rc1 unless owner "
    "elevates at Slice 8 acceptance-gate time."
)


def main() -> int:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    result = db.insert_deliberation(
        id=DELIB_ID,
        source_type="owner_conversation",
        title="S328 owner directive: GTKB-ISOLATION-017 Slice 5 overlay-test scope revision (defer 2 of 3 to Slice 5.5)",
        summary=SUMMARY,
        content=CONTENT,
        changed_by=resolve_changed_by(),
        change_reason=(
            "Archive S328 owner scoping-revision decision per Codex `-002` F1 path 2. "
            "Authorizes partial deferral of overlay tests; ships stale-detection in "
            "Slice 5, defers refresh + disposability to Slice 5.5. REVISED-1 (-003) "
            "cites this DELIB as the supersession authority for the original "
            "scoping bridge -003 lines 143-145."
        ),
        outcome="owner_decision",
        session_id="S328",
        source_ref="owner_conversation:2026-05-03-S328-isolation-017-slice5-overlay-scope-revision",
    )
    delib_id = result.get("id") if result else DELIB_ID
    version = result.get("version") if result else "?"
    print(f"insert_deliberation id={delib_id} version={version}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
