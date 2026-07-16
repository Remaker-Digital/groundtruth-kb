#!/usr/bin/env python3
"""One-shot dispatch helper: preflights + evidence checks + WI-5211 repair GO."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))

from scripts.adr_dcl_clause_preflight import (  # noqa: E402
    evaluate_clauses,
    find_operative_file,
    load_clauses,
)
from scripts.adr_dcl_clause_preflight import (  # noqa: E402
    render_markdown as render_clause_markdown,
)
from scripts.bridge_applicability_preflight import build_packet, format_markdown  # noqa: E402
from scripts.gtkb_bridge_writer import write_bridge_file  # noqa: E402

VERIFY_HELPERS = PROJECT_ROOT / ".claude" / "skills" / "verify" / "helpers"
if str(VERIFY_HELPERS) not in sys.path:
    sys.path.insert(0, str(VERIFY_HELPERS))
from write_verdict import seed_prior_deliberations  # noqa: E402

SLUG = "gtkb-wi5211-failed-verified-finalization-repair"
VERSION = 3
RESPONDS_TO = f"bridge/{SLUG}-002.md"
DRAFT_PATH = PROJECT_ROOT / ".gtkb-state" / "bridge-verify-helper" / "draft-wi5211-repair-go.md"
OUT_JSON = PROJECT_ROOT / "scripts" / "_dispatch_wi5211_003_out.json"
SESSION_CONTEXT = "2026-07-16T21-49-33Z-loyal-opposition-E-759a46"
PROPOSAL_AUTHOR_SESSION = "019f6bf6-3e6d-7761-be14-fb894a0e84d2"

FAILED_VERDICT = PROJECT_ROOT / "bridge" / "gtkb-wi5211-df-governed-verdict-publication-parity-008.md"
IMPL_REPORT_007 = PROJECT_ROOT / "bridge" / "gtkb-wi5211-df-governed-verdict-publication-parity-007.md"
PRECEDENT_GO = PROJECT_ROOT / "bridge" / "gtkb-wi5321-wi5299-failed-verified-finalization-repair-002.md"


def _verify_failed_008_state() -> dict[str, object]:
    if not FAILED_VERDICT.is_file():
        raise SystemExit(f"Missing failed verdict file: {FAILED_VERDICT}")
    text = FAILED_VERDICT.read_text(encoding="utf-8")
    if not text.startswith("VERIFIED"):
        raise SystemExit("Failed verdict 008 does not start with VERIFIED")
    if "## Commit Finalization Evidence" in text:
        raise SystemExit("Failed verdict 008 unexpectedly contains Commit Finalization Evidence")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest().upper()
    size = FAILED_VERDICT.stat().st_size
    return {
        "path": str(FAILED_VERDICT.relative_to(PROJECT_ROOT)),
        "size_bytes": size,
        "sha256": digest,
        "first_line": text.splitlines()[0],
        "has_commit_finalization_evidence": False,
    }


def _verify_007_state() -> dict[str, object]:
    if not IMPL_REPORT_007.is_file():
        raise SystemExit(f"Missing implementation report: {IMPL_REPORT_007}")
    text = IMPL_REPORT_007.read_text(encoding="utf-8")
    first = text.splitlines()[0].strip()
    if first != "NEW":
        raise SystemExit(f"Expected 007 to be NEW implementation report; got {first!r}")
    return {
        "path": str(IMPL_REPORT_007.relative_to(PROJECT_ROOT)),
        "first_line": first,
        "bridge_kind": "implementation_report",
    }


def main() -> int:
    bridge_dir = PROJECT_ROOT / "bridge"
    operative = find_operative_file(SLUG, bridge_dir)
    if operative is None:
        raise SystemExit(f"No operative bridge file for {SLUG!r}")
    if operative.name != f"{SLUG}-002.md":
        raise SystemExit(
            f"Expected operative proposal at {SLUG}-002.md; got {operative.name}. Update VERSION if the chain advanced."
        )

    packet = build_packet(bridge_id=SLUG, bridge_dir=bridge_dir)
    applicability_exit = 0 if packet.get("preflight_passed") else 5
    if not packet.get("preflight_passed"):
        raise SystemExit(f"Applicability preflight failed (exit {applicability_exit}): {packet}")
    applicability_md = format_markdown(packet)

    clauses = load_clauses(PROJECT_ROOT / "config" / "governance" / "adr-dcl-clauses.toml")
    operative_content = operative.read_text(encoding="utf-8")
    clause_results = evaluate_clauses(clauses, operative_content, SLUG, [f"bridge/{operative.name}"])
    blocking = [
        row
        for row in clause_results
        if row.applicability == "must_apply"
        and row.evidence_found is False
        and row.clause.severity == "blocking"
        and row.clause.enforcement_mode == "blocking"
    ]
    clause_exit = 5 if blocking else 0
    if blocking:
        raise SystemExit(f"Clause preflight blocking gaps (exit {clause_exit}): {blocking}")
    clause_md = render_clause_markdown(SLUG, operative, clause_results, content=operative_content, report_only=False)

    failed_008 = _verify_failed_008_state()
    report_007 = _verify_007_state()

    draft = f"""GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: {SESSION_CONTEXT}
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor headless bridge auto-dispatch; resolved role loyal-opposition via ::init gtkb lo
author_metadata_source: explicit_dispatch_metadata

# Loyal Opposition Verdict - GO - Repair WI-5211 failed VERIFIED finalization

bridge_kind: lo_verdict
Document: {SLUG}
Version: {VERSION:03d}
Responds to: {RESPONDS_TO}
Date: 2026-07-16 UTC
Reviewer role: loyal-opposition (harness E, Cursor)

## Verdict

GO. The revised implementation proposal (version 002) for WI-5211 failed-finalization repair is sound, well-scoped, and preserves repository hygiene and change control. The repair path safely archives the untracked failed terminal verdict at version 008 before removing only that file, restoring the original WI-5211 thread to latest `NEW` at version 007 so Loyal Opposition can reissue governed `VERIFIED` finalization through `write_verdict.py --finalize-verified` without touching the already-reviewed `scripts/openrouter_harness.py` source. The WI-5370 backlog anchor correction in version 002 avoids dispatcher terminal-work-item reconciliation against resolved `WI-5211`.

## Review Independence

The proposal author session context (`{PROPOSAL_AUTHOR_SESSION}`, Codex/A) differs from this reviewer session context (`{SESSION_CONTEXT}`, Cursor/E). Same-session self-review does not apply; independent review is satisfied.

## Prior Deliberations

- `DELIB-202666332` — Owner requires per-thread reconciliation rather than broad unrelated commits when clearing worktree dirt.
- `DELIB-202666274` — Work-tree hygiene policy requires resolving uncommitted sprawl while preserving bridge audit provenance.
- `bridge/gtkb-wi5321-wi5299-failed-verified-finalization-repair-002.md` — direct precedent GO for the same bounded failed-terminal-verdict archive-and-restore pattern applied to WI-5299.
- `bridge/gtkb-wi5211-df-governed-verdict-publication-parity-005.md` through `008.md` — operative source thread that produced the failed terminal verdict being repaired here.

## Applicability Preflight

{applicability_md}

## Clause Applicability (Slice 2; mandatory gate)

{clause_md}

## Findings

None. The proposal is compliant and sufficient for its scope.

## Failed Terminal Verdict Evidence (008)

- Path: `{failed_008["path"]}` — present on disk.
- First line: `{failed_008["first_line"]}` (terminal `VERIFIED` without governed finalizer).
- Size: `{failed_008["size_bytes"]}` bytes; SHA-256: `{failed_008["sha256"]}`.
- `## Commit Finalization Evidence`: absent (`has_commit_finalization_evidence={failed_008["has_commit_finalization_evidence"]}`).
- Restored thread target: `{report_007["path"]}` is latest `NEW` implementation report (`{report_007["first_line"]}`) before the failed 008 bypass.
- Precedent alignment: matches bounded repair pattern approved at `{PRECEDENT_GO.relative_to(PROJECT_ROOT).as_posix()}`.

## Recommended Commit Type

chore

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

    DRAFT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DRAFT_PATH.write_text(draft, encoding="utf-8", newline="\n")

    seeded = seed_prior_deliberations(SLUG, draft, project_root=PROJECT_ROOT)

    path = write_bridge_file(
        SLUG,
        VERSION,
        seeded,
        PROJECT_ROOT,
        require_author_metadata=False,
    )

    result = {
        "applicability_preflight_exit": applicability_exit,
        "clause_preflight_exit": clause_exit,
        "draft_path": str(DRAFT_PATH),
        "verdict_path": str(path),
        "operative_proposal": operative.name,
        "failed_008": failed_008,
        "report_007": report_007,
        "packet": packet,
        "go_filed": True,
        "note": "LO GO filed at version 003 because version 002 is Prime Builder REVISED.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
