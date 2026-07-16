#!/usr/bin/env python3
"""One-shot dispatch helper: governance-complete GO for WI-5318/WI-5316 repair threads."""

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

SESSION_CONTEXT = "2026-07-16T22-40-43Z-loyal-opposition-E-e16758"
PROPOSAL_AUTHOR_SESSION = "019f6bf6-3e6d-7761-be14-fb894a0e84d2"
PRECEDENT_GO = PROJECT_ROOT / "bridge" / "gtkb-wi5321-wi5299-failed-verified-finalization-repair-002.md"

THREADS = (
    {
        "slug": "gtkb-wi5318-failed-verified-finalization-repair",
        "version": 6,
        "proposal_rel": "bridge/gtkb-wi5318-failed-verified-finalization-repair-004.md",
        "failed_rel": "bridge/gtkb-wi5318-modified-terminal-verdict-provenance-008.md",
        "report_rel": "bridge/gtkb-wi5318-modified-terminal-verdict-provenance-007.md",
        "expected_size": 9533,
        "expected_sha256": "E0498D4B649B8EEAC5AFE877D8E95478F8DDB2F87F9BA2D2474B62FECA00E9D3",
        "title": "WI-5318 Failed VERIFIED Finalization Repair",
    },
    {
        "slug": "gtkb-wi5316-failed-verified-finalization-repair",
        "version": 6,
        "proposal_rel": "bridge/gtkb-wi5316-failed-verified-finalization-repair-004.md",
        "failed_rel": "bridge/gtkb-wi5316-frozen-modernization-rc-contract-008.md",
        "report_rel": "bridge/gtkb-wi5316-frozen-modernization-rc-contract-007.md",
        "expected_size": 4721,
        "expected_sha256": "6E890E22F3F57A59E89560610D5FD61E56EBB0B88BF37592B2AC900AAA0DB55B",
        "title": "WI-5316 Failed VERIFIED Finalization Repair",
    },
)


def _verify_failed_verdict(path: Path, *, expected_size: int, expected_sha256: str) -> dict[str, object]:
    if not path.is_file():
        raise SystemExit(f"Missing failed verdict file: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.startswith("VERIFIED"):
        raise SystemExit(f"Failed verdict {path.name} does not start with VERIFIED")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest().upper()
    size = path.stat().st_size
    if size != expected_size:
        raise SystemExit(f"Failed verdict size mismatch for {path.name}: got {size}, expected {expected_size}")
    if digest != expected_sha256.upper():
        raise SystemExit(
            f"Failed verdict SHA-256 mismatch for {path.name}: got {digest}, expected {expected_sha256.upper()}"
        )
    return {
        "path": path.relative_to(PROJECT_ROOT).as_posix(),
        "size_bytes": size,
        "sha256": digest,
        "first_line": text.splitlines()[0],
        "has_commit_finalization_evidence": "## Commit Finalization Evidence" in text,
    }


def _verify_report(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise SystemExit(f"Missing implementation report: {path}")
    text = path.read_text(encoding="utf-8")
    first = text.splitlines()[0].strip()
    if first != "NEW":
        raise SystemExit(f"Expected {path.name} to be NEW implementation report; got {first!r}")
    return {
        "path": path.relative_to(PROJECT_ROOT).as_posix(),
        "first_line": first,
    }


def _process_thread(spec: dict[str, object]) -> dict[str, object]:
    slug = str(spec["slug"])
    version = int(spec["version"])
    proposal_path = PROJECT_ROOT / str(spec["proposal_rel"])
    failed_path = PROJECT_ROOT / str(spec["failed_rel"])
    report_path = PROJECT_ROOT / str(spec["report_rel"])
    target = PROJECT_ROOT / "bridge" / f"{slug}-{version:03d}.md"
    if target.is_file():
        raise SystemExit(f"Refusing to overwrite existing bridge file: {target}")

    proposal_content = proposal_path.read_text(encoding="utf-8")
    if not proposal_content.lstrip().startswith("REVISED"):
        raise SystemExit(f"Expected proposal {proposal_path.name} to start with REVISED")

    packet = build_packet(bridge_id=slug, content_file=proposal_path)
    applicability_exit = 0 if packet.get("preflight_passed") else 5
    if not packet.get("preflight_passed"):
        raise SystemExit(f"Applicability preflight failed for {slug}: {packet}")
    applicability_md = format_markdown(packet)

    clauses = load_clauses(PROJECT_ROOT / "config" / "governance" / "adr-dcl-clauses.toml")
    clause_results = evaluate_clauses(
        clauses,
        proposal_content,
        slug,
        [proposal_path.relative_to(PROJECT_ROOT).as_posix()],
    )
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
        raise SystemExit(f"Clause preflight blocking gaps for {slug}: {blocking}")
    clause_md = render_clause_markdown(
        slug,
        proposal_path,
        clause_results,
        content=proposal_content,
        report_only=False,
    )

    failed = _verify_failed_verdict(
        failed_path,
        expected_size=int(spec["expected_size"]),
        expected_sha256=str(spec["expected_sha256"]),
    )
    report = _verify_report(report_path)

    draft = f"""GO
author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: {SESSION_CONTEXT}
author_model: Composer
author_model_version: cursor-agent
author_model_configuration: Cursor headless bridge auto-dispatch; resolved role loyal-opposition via ::init gtkb lo
author_metadata_source: explicit_dispatch_metadata

# Loyal Opposition Verdict - GO - {spec["title"]}

bridge_kind: lo_verdict
Document: {slug}
Version: {version:03d}
Responds to: {spec["proposal_rel"]}
Date: 2026-07-16 UTC
Reviewer role: loyal-opposition (harness E, Cursor)
Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5370

## Verdict

GO. The revised implementation proposal (version 004) for {spec["title"]} is sound, well-scoped, and preserves repository hygiene and change control. Version 004 adds explicit absolute in-root evidence that satisfies `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT`, answering the version-003 NO-ACTION disposition. The repair path safely archives the untracked failed terminal verdict before removing only that file, restoring the original thread to latest `NEW` at `{report["path"]}` so Loyal Opposition can reissue governed `VERIFIED` finalization through `write_verdict.py --finalize-verified` without touching the excluded original implementation paths.

## Review Independence

The proposal author session context (`{PROPOSAL_AUTHOR_SESSION}`, Codex/A) differs from this reviewer session context (`{SESSION_CONTEXT}`, Cursor/E). Same-session self-review does not apply; independent review is satisfied.

## Prior Deliberations

- `DELIB-202666332` — Owner requires per-thread reconciliation rather than broad unrelated commits when clearing worktree dirt.
- `DELIB-202666274` — Work-tree hygiene policy requires resolving uncommitted sprawl while preserving bridge audit provenance.
- `{PRECEDENT_GO.relative_to(PROJECT_ROOT).as_posix()}` — direct precedent GO for the same bounded failed-terminal-verdict archive-and-restore pattern.
- `{spec["proposal_rel"]}` — revised in-root evidence packet under review.
- `bridge/{slug}-003.md` — NO-ACTION disposition requesting explicit in-root evidence before implementation.

## Applicability Preflight

{applicability_md}

## Clause Applicability (Slice 2; mandatory gate)

{clause_md}

## Findings

None. The proposal is compliant and sufficient for its scope.

## Failed Terminal Verdict Evidence

- Path: `{failed["path"]}` — present on disk.
- First line: `{failed["first_line"]}` (terminal `VERIFIED` without governed finalizer).
- Size: `{failed["size_bytes"]}` bytes; SHA-256: `{failed["sha256"]}`.
- `## Commit Finalization Evidence`: {"present" if failed["has_commit_finalization_evidence"] else "absent"}.
- Restored thread target: `{report["path"]}` is latest `NEW` implementation report (`{report["first_line"]}`) before the failed terminal bypass.
- Precedent alignment: matches bounded repair pattern approved at `{PRECEDENT_GO.relative_to(PROJECT_ROOT).as_posix()}`.

## Note on Version 005

Version 005 recorded a corrected GO without mandatory verbatim preflight sections. This version 006 supersedes it as the governance-complete operative GO for Prime Builder implementation-start.

## Recommended Commit Type

chore

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

    draft_path = PROJECT_ROOT / ".gtkb-state" / "bridge-verify-helper" / f"draft-{slug}-006-go.md"
    draft_path.parent.mkdir(parents=True, exist_ok=True)
    draft_path.write_text(draft, encoding="utf-8", newline="\n")
    seeded = seed_prior_deliberations(slug, draft, project_root=PROJECT_ROOT)
    verdict_path = write_bridge_file(
        slug,
        version,
        seeded,
        PROJECT_ROOT,
        require_author_metadata=False,
    )
    return {
        "slug": slug,
        "applicability_preflight_exit": applicability_exit,
        "clause_preflight_exit": clause_exit,
        "draft_path": str(draft_path),
        "verdict_path": str(verdict_path),
        "operative_proposal": proposal_path.name,
        "failed_verdict": failed,
        "report_007": report,
        "packet": packet,
    }


def main() -> int:
    results = [_process_thread(spec) for spec in THREADS]
    out_path = PROJECT_ROOT / "scripts" / "_dispatch_wi5318_wi5316_006_out.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
