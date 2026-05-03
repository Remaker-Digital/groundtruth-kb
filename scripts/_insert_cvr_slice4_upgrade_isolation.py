# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Insert CVR-SLICE4-UPGRADE-ISOLATION-001 per GOV-20 Phase 1 advisory pilot.

Authority: bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-012.md (Codex VERIFIED).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "groundtruth-kb" / "src"))

from groundtruth_kb.db import KnowledgeDB  # noqa: E402

DOC_ID = "CVR-SLICE4-UPGRADE-ISOLATION-001"

CONTENT = """## Constraint Verification Review (CVR) — GTKB-ISOLATION-017 Slice 4

**Bridge thread:** `bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-011.md` (REVISED-1 post-impl) → `-012` (Codex Loyal Opposition VERIFIED).

**Purpose:** Post-implementation proof per GOV-20 Phase 1 advisory pilot. Records that the implementation honors `ADR-ISOLATION-APPLICATION-PLACEMENT-001`, the four S328 owner decisions for Slice 4, and the Phase 9 §2 obligations after the REVISED-4 partition reclassification.

## Final partition shape (post-REVISED-4)

The 9 isolation doctor checks are partitioned as 1 hard-refuse + 4 auto-fixable + 4 needs-adopter-input:

- **HARD-REFUSE (1):** `isolation:adopter-root-placement` (#1).
- **AUTO-FIXABLE (4):** `isolation:service-endpoint` (#2), `isolation:work-subject` (#3), `isolation:workstream-focus-hook-absent` (#6), `isolation:release-readiness-app-subject-header` (#8).
- **NEEDS-ADOPTER-INPUT (4):** `isolation:no-writable-product-paths` (#4), `isolation:hooks-point-to-wrappers` (#5), `isolation:work-list-no-product-entries` (#7), `isolation:chroma-regeneratable` (#9).

T11 (partition-contract test) enforces this against the live `run_isolation_checks()` return at every test run; future drift in the doctor surface fails T11 immediately.

## DCL compliance summary

Acceptance criteria from `-007` §"Acceptance Criteria" (carried through `-009` and `-011`):

1. **Specification Links cover all governing artifacts.** PASS — Codex `-008` GO + `-010` NO-GO + `-012` VERIFIED §"Gate Checks" all confirmed.
2. **Live-probed partition keys match `ToolCheck.name` values.** PASS — verified by T11 (assertion against live `run_isolation_checks()`).
3. **Partition exhaustive + no dead keys + disjoint.** PASS — T11 + T13a.
4. **Work-list scrub absent from impl surface.** PASS — `_PARTITION_*` + `_ISOLATION_FIXER_MAP` source confirms; `isolation:work-list-no-product-entries` stays in needs-adopter-input.
5. **Template registry path is `groundtruth-kb/templates/managed-artifacts.toml`.** PASS — `file.upgrade-rehearsal-recipe` row at lines 859-868.
6. **Decision 7 invariant (no rehearsal driver invocation).** PASS — T5 negative-presence test.
7. **Auto-fixer dispatch via typed `IsolationFixerResult`.** PASS — T13b/c/d.
8. **`upgrade_policy` honor as bounded governed exception.** PASS — T12a/b/c + T14.
9. **Check #6 fixer targets `.claude/hooks/workstream-focus.py`.** PASS — T15a/b.
10. **Estimated envelope.** EXCEEDED (~640 LOC source + ~620 LOC tests vs `-007`'s 200-300/400-550 ceiling). Owner CVR-time acceptance: scope was preserved; LOC delta traces to F1/F2 fix architectures + 4 NO-GO/REVISED cycles each adding mechanical-test coverage.

## Final test + lint state at VERIFIED time

Per Codex `-012` §"Verification Commands":

```text
python -m pytest groundtruth-kb/tests/test_upgrade_isolation.py -q --tb=short
23 passed, 1 skipped, 1 warning in 9.42s

python -m pytest groundtruth-kb/tests/test_upgrade.py groundtruth-kb/tests/test_upgrade_isolation.py groundtruth-kb/tests/test_doctor_isolation.py groundtruth-kb/tests/test_preflight_checks.py -q --tb=short
102 passed, 1 skipped, 1 warning in 28.92s

python -m ruff check ...
All checks passed!
```

Codex independently re-ran each command. T10 (1 skipped) is the IPR/CVR presence test — passes once this CVR insertion completes; trips green on next test run.

## Post-VERIFIED cleanups landed (per Codex `-012` §"Non-blocking Observation")

Codex flagged 3 non-blocking stale strings; cleaned up immediately post-VERIFIED:

- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:61` — partition-comment "1 + 5 + 3 = 9" updated to "1 + 4 + 4 = 9" + reclassification note.
- `groundtruth-kb/src/groundtruth_kb/project/upgrade.py:84` — surface-comment "5 isolation auto-fixers" updated to "4".
- `groundtruth-kb/templates/project/upgrade-rehearsal-recipe.md:70` — see-also bullet "5 auto-fixers" updated to "4".

Plus one owner-flagged stale string (separate from Codex's observations):

- `groundtruth-kb/src/groundtruth_kb/cli.py:953` — `--accept-migration` help text removed "hook paths" from the listed auto-fixable defects (no longer accurate post-REVISED-4).

All 4 stale references are now consistent with the live partition. Verified ruff clean + tests still pass post-cleanup.

## IPR carry-forward

`IPR-SLICE4-UPGRADE-ISOLATION-001` v1 was inserted at `-009` post-impl filing time. The IPR's content describes the pre-REVISED-4 5-fixer partition; this CVR documents the REVISED-4 4-fixer reclassification as the final state. Future readers should consult both: IPR for the original implementation contract; CVR for the verified end state.

A combined IPR v2 update could supersede both into a single point-in-time-current document; deferred as a possible future hygiene item, not blocking.

## Disclosure resolutions (carried + updated from -009 / -011)

- **Disclosure 1 (Check #3 file relocation):** RESOLVED in implementation; surface includes `.claude/session/work-subject.json` per the live doctor check. T3 + T14 cover.
- **Disclosure 2 (Check #5 conditional auto-fixability):** RESOLVED via S328 owner reclassify decision; check #5 in needs-adopter-input. Codex `-012` confirmed.
- **Disclosure 3 (`enforce_isolation: bool = True` back-door):** OPEN. Codex `-012` did not flag, accepting the minimum-change adaptation. Possible future architecture refinement: extract gate into a CLI-only function. Tracked in `-009` Disclosure 3 + `-011` Disclosure 3.
- **Disclosure 4 (Estimated envelope exceeded):** ACKNOWLEDGED at CVR; scope preserved per acceptance criterion review.

## Sequencing — what unblocks now

Per `memory/work_list.md` TOP release-path directive:

1. ~~Slice 4~~ DONE — VERIFIED at `-012`.
2. **Slice 5 — clean-adopter test suite + CI wiring + overlay tests.** NEXT actionable. Per scoping bridge `-003` §"Sequencing Constraints": "Slice 5 (tests + overlay tests + CI wiring) after Slices 1-4 VERIFIED." Now unblocked.
3. Slices 6 (docs) + 7 (examples) — parallel after Slice 5 VERIFIED.
4. Slice 8 — release ops + program closeout (after Slices 1-7 VERIFIED).
5. Release hardening — known blockers per work_list TOP step 5.
6. v0.7.0-rc1 release.

Slice 4 closure unblocks the release path's largest remaining feature work: the clean-adopter test suite that proves a fresh `gt project init` produces a fully-functional adopter without GT-KB product leakage.
"""

SUMMARY = (
    "Constraint Verification Review for GTKB-ISOLATION-017 Slice 4: post-VERIFIED "
    "proof that the implementation honors ADR-ISOLATION-APPLICATION-PLACEMENT-001 + "
    "the 4 S328 owner decisions + Phase 9 §2 obligations. Final partition (post-REVISED-4): "
    "1 hard-refuse + 4 auto-fixable + 4 needs-adopter-input = 9. Codex VERIFIED at -012 "
    "(2026-05-03). 4 post-VERIFIED stale-string cleanups landed. Slice 5 unblocked."
)


def main() -> int:
    db = KnowledgeDB(REPO_ROOT / "groundtruth.db")
    result = db.insert_document(
        id=DOC_ID,
        title="GTKB-ISOLATION-017 Slice 4 Upgrade Isolation — Constraint Verification Review",
        category="constraint_verification",
        status="approved",
        changed_by="prime-builder/claude-code",
        change_reason=(
            "GOV-20 Phase 1 advisory pilot: post-implementation verification for "
            "GTKB-ISOLATION-017 Slice 4. Codex VERIFIED at "
            "bridge/gtkb-isolation-017-slice4-upgrade-2026-05-02-012.md."
        ),
        content=CONTENT,
        tags=["GOV-20", "GTKB-ISOLATION-017", "Slice-4", "CVR", "S328", "VERIFIED"],
    )
    doc_id = result.get("id") if result else DOC_ID
    version = result.get("version") if result else "?"
    print(f"insert_document id={doc_id} version={version}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
