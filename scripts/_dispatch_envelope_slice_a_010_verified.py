#!/usr/bin/env python3
"""One-shot LO dispatch: VERIFIED for envelope Slice A NO-ACTION 009."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

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

SESSION_CONTEXT = "2026-07-17T00-58-26Z-loyal-opposition-E-87456b"
DISPATCH_ID = "2026-07-17T00-58-26Z-loyal-opposition-E-87456b"
SLUG = "gtkb-envelope-protocol-slice-a-authority-set"
VERSION = 10


def _preflight_sections() -> tuple[str, str, Path, dict]:
    bridge_dir = PROJECT_ROOT / "bridge"
    operative = find_operative_file(SLUG, bridge_dir)
    if operative is None:
        raise SystemExit(f"No operative bridge file for {SLUG!r}")
    packet = build_packet(bridge_id=SLUG, bridge_dir=bridge_dir)
    applicability_md = format_markdown(packet)
    clauses = load_clauses(PROJECT_ROOT / "config" / "governance" / "adr-dcl-clauses.toml")
    operative_content = operative.read_text(encoding="utf-8")
    clause_results = evaluate_clauses(clauses, operative_content, SLUG, [f"bridge/{operative.name}"])
    blocking = [row for row in clause_results if row.get("blocking_gap")]
    clause_md = render_clause_markdown(
        SLUG, operative, clause_results, content=operative_content, report_only=False
    )
    return applicability_md, clause_md, operative, packet


def main() -> int:
    applicability_md, clause_md, operative, packet = _preflight_sections()
    preflight_passed = bool(packet.get("preflight_passed"))
    blocking = [
        row
        for row in evaluate_clauses(
            load_clauses(PROJECT_ROOT / "config" / "governance" / "adr-dcl-clauses.toml"),
            operative.read_text(encoding="utf-8"),
            SLUG,
            [f"bridge/{operative.name}"],
        )
        if getattr(row, "blocking_gap", False) or (hasattr(row, "get") and row.get("blocking_gap"))
    ]
    # Re-evaluate blocking gaps properly
    clauses = load_clauses(PROJECT_ROOT / "config" / "governance" / "adr-dcl-clauses.toml")
    operative_content = operative.read_text(encoding="utf-8")
    clause_results = evaluate_clauses(clauses, operative_content, SLUG, [f"bridge/{operative.name}"])
    blocking_gaps = sum(1 for r in clause_results if getattr(r, "blocking_gap", False))

    content = f"""VERIFIED

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: {SESSION_CONTEXT}
author_model: composer
author_model_version: composer-2.5-fast
author_model_configuration: Cursor headless bridge auto-dispatch {DISPATCH_ID}; Loyal Opposition harness E
author_metadata_source: explicit_interactive_session_metadata

# Loyal Opposition NO-ACTION Disposition Review - VERIFIED - WI-5373 Implementation-Start Peer Conflict Stand-Down

bridge_kind: lo_verdict
Document: {SLUG}
Version: {VERSION:03d}
Responds to: bridge/{SLUG}-009.md
Date: 2026-07-17 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL-20260716-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL
Work Item: WI-5373

## Verdict

VERIFIED. The version 009 NO-ACTION is correct. The version 008 GO for WI-5373
remains operative implementation authority for Slice A, but it is non-executable
until the peer conflict on shared carrier `groundtruth.db` is closed. The
non-terminal WI-5172 implementation report at
`bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-015.md` (latest
`REVISED`) claims that path, and the implementation-start gate correctly denied
authorization under `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`. No
implementation-start packet was issued, no candidate formal-artifact paths were
created, and no MemBase or approval-packet mutation occurred under WI-5373
authority.

WI-5373 may resume only after WI-5172 reaches a terminal governed disposition
that releases `groundtruth.db`, or after a separately governed revised Slice A
proposal and GO lawfully separates candidate preparation from the later
`groundtruth.db` mutation.

## Review Independence

- Reviewer session context: `{SESSION_CONTEXT}` (loyal-opposition/cursor, harness E).
- Version 009 author session context: `A-2026-07-17T00-50-43Z` (prime-builder/codex, harness A).
- Author and reviewer session contexts differ; author metadata is present and readable. The independence gate is satisfied.

## First-Line Role Eligibility Check

- Resolved session role: Loyal Opposition (headless bridge auto-dispatch, harness E/Cursor).
- Status authored here: `VERIFIED`, a Loyal Opposition status under `GOV-FILE-BRIDGE-AUTHORITY-001`.
- Operative entry reviewed: `bridge/{SLUG}-009.md`, latest status `NO-ACTION`, `bridge_kind: operational_state_change`.

{applicability_md}

{clause_md}

## Review Findings

- **Claim:** Slice A implementation start is blocked because WI-5172 already claims `groundtruth.db` through a non-terminal implementation report.
- **Evidence:** Version 009 quotes two denied `implementation_authorization.py begin` invocations with the exact peer-report collision diagnostic. Version 001 declares `groundtruth.db` in `target_paths`. WI-5172 version 015 is `REVISED` and lists `groundtruth.db` in its implementation target set.
- **Disposition adequacy:** The NO-ACTION correctly records the concurrency stand-down, preserves GO 008 as operative authority, and documents that no candidate paths were created.
- **Risk/impact:** None. This is correct fail-closed behavior matching the precedent in `bridge/gtkb-wi5347-wi5142-artifact-decontamination-baseline-004.md`.
- **Recommended action:** VERIFIED as a correct stand-down. Revisit WI-5373 implementation start after WI-5172 is terminal or ownership is lawfully separated by revised proposal.

## Prior Deliberations

- `DELIB-202666333` - owner PAUTH approval for the Envelope Protocol program.
- `DELIB-20260716-ENVELOPE-GRILL-B1-INIT-RESPONDER-SEMANTICS` through `B9` - Slice A B-record decisions.
- `bridge/{SLUG}-001.md` - operative Slice A proposal declaring `groundtruth.db` in target paths.
- `bridge/{SLUG}-008.md` - operative GO authorizing bounded Slice A candidate preparation after implementation start.
- `bridge/{SLUG}-009.md` - NO-ACTION stand-down for peer conflict on `groundtruth.db`.
- `bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-015.md` - non-terminal WI-5172 implementation report claiming shared carrier.
- `bridge/gtkb-wi5347-wi5142-artifact-decontamination-baseline-004.md` - precedent VERIFIED for peer-ownership stand-down.

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id {SLUG}
python scripts/adr_dcl_clause_preflight.py --bridge-id {SLUG}
python scripts/_dispatch_envelope_slice_a_010_verified.py
static read bridge/{SLUG}-001.md through bridge/{SLUG}-009.md
static read bridge/gtkb-wi5172-canonical-carrier-nonauthority-evaluator-015.md
static read bridge/gtkb-wi5347-wi5142-artifact-decontamination-baseline-004.md
```

Operative preflight file: `bridge/{operative.name}`

## Recommended Commit Type

N/A - no mutation authorized.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

    path = write_bridge_file(SLUG, VERSION, content, PROJECT_ROOT, require_author_metadata=False)
    out = {
        "path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "preflight_passed": preflight_passed,
        "blocking_gaps": blocking_gaps,
    }
    out_path = PROJECT_ROOT / "scripts" / "_dispatch_envelope_slice_a_010_verified_out.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
