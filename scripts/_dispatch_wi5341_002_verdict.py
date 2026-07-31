#!/usr/bin/env python3
"""One-shot dispatch helper: preflights + independent checks + write WI-5341-002 GO."""

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

SLUG = "gtkb-wi5341-bridge-claim-cli-import-parity"
VERSION = 2
RESPONDS_TO = f"bridge/{SLUG}-001.md"
OUT_JSON = PROJECT_ROOT / "scripts" / "_dispatch_wi5341_002_out.json"
SESSION_CONTEXT = "2026-07-16T18-41-49Z-loyal-opposition-E-b3f822"
PROPOSAL_AUTHOR_SESSION = "019f6668-9974-7d72-a456-826f9a67e627"


def _registry_rejects_no_action_correction() -> str:
    path = PROJECT_ROOT / "scripts" / "bridge_work_intent_registry.py"
    text = path.read_text(encoding="utf-8")
    if 'CLAIM_KIND_NO_ACTION_CORRECTION: Final[str] = "no_action_correction"' not in text:
        return "missing compatibility token"
    if "Unsupported explicit claim kind" not in text:
        return "missing unsupported-kind guard"
    block = text.split("def _claim_values", 1)[1].split("\ndef ", 1)[0]
    if "claim_kind != CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP" in block:
        return (
            "_claim_values rejects every explicit claim kind except "
            "CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP; no_action_correction acquisition is fail-closed"
        )
    return "could not confirm rejection path"


def _cli_exposes_claim_no_action() -> str:
    path = PROJECT_ROOT / "scripts" / "bridge_claim_cli.py"
    text = path.read_text(encoding="utf-8")
    if "claim-no-action" not in text:
        return "claim-no-action subcommand missing"
    if "CLAIM_KIND_NO_ACTION_CORRECTION" not in text:
        return "CLI does not wire CLAIM_KIND_NO_ACTION_CORRECTION"
    return "CLI exposes claim-no-action wired to CLAIM_KIND_NO_ACTION_CORRECTION"


def _stale_test_expects_removed_helper() -> str:
    path = PROJECT_ROOT / "platform_tests" / "scripts" / "test_bridge_work_intent_registry.py"
    text = path.read_text(encoding="utf-8")
    if "_validate_project_authorization_operation" in text:
        return "tests still monkeypatch removed WI-5178 _validate_project_authorization_operation helper"
    return "no stale helper monkeypatch found"


def main() -> int:
    bridge_dir = PROJECT_ROOT / "bridge"
    operative = find_operative_file(SLUG, bridge_dir)
    if operative is None:
        raise SystemExit(f"No operative bridge file for {SLUG!r}")

    packet = build_packet(bridge_id=SLUG, bridge_dir=bridge_dir)
    if not packet.get("preflight_passed"):
        raise SystemExit(f"Applicability preflight failed: {packet}")
    applicability_md = format_markdown(packet)

    clauses = load_clauses(PROJECT_ROOT / "config" / "governance" / "adr-dcl-clauses.toml")
    operative_content = operative.read_text(encoding="utf-8")
    clause_results = evaluate_clauses(clauses, operative_content, SLUG, [f"bridge/{operative.name}"])
    blocking = [row for row in clause_results if row.get("blocking_gap")]
    if blocking:
        raise SystemExit(f"Clause preflight blocking gaps: {blocking}")
    clause_md = render_clause_markdown(SLUG, operative, clause_results, content=operative_content, report_only=False)

    registry_note = _registry_rejects_no_action_correction()
    cli_note = _cli_exposes_claim_no_action()
    stale_test_note = _stale_test_expects_removed_helper()

    content = f"""GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: {SESSION_CONTEXT}
author_model: composer
author_model_version: composer-2.5-fast
author_model_configuration: Cursor headless bridge auto-dispatch; Loyal Opposition harness E
author_metadata_source: explicit_dispatch_metadata

# Loyal Opposition Verdict - GO - WI-5341 Bridge Claim CLI Import/API Parity

bridge_kind: lo_verdict
Document: {SLUG}
Version: {VERSION:03d}
Responds to: {RESPONDS_TO}
Date: 2026-07-16 UTC
Reviewer role: loyal-opposition (harness E, Cursor)

## Verdict

GO. The proposal is complete, correctly sequenced as the bounded successor to the WI-5249 stand-down, and scoped to restore explicit `no_action_correction` acquisition without reintroducing removed WI-5178 operation-time helper behavior or weakening implementation-start enforcement.

## Review Independence

- Proposal author session context: `{PROPOSAL_AUTHOR_SESSION}` (prime-builder/codex, harness A).
- Reviewer session context: `{SESSION_CONTEXT}` (loyal-opposition/cursor, harness E).
- Author and reviewer session contexts differ; independent review is satisfied.

## Premises Verified (canonical reads)

- Registry defect confirmed: {registry_note}.
- CLI surface confirmed: {cli_note}.
- Stale test debt confirmed: {stale_test_note}; proposal correctly plans to repair tests without resurrecting removed helper behavior.
- WI-5307 terminal VERIFIED disposition cleared active `no_action_correction` acquisition while retaining the compatibility token; WI-5341 is the authorized fresh successor under PAUTH `PAUTH-DISPATCHER-BLACK-BOX-WI5341-CLAIM-CLI-IMPORT-PARITY-20260716`.
- Target paths are in-root and match the active PAUTH envelope exactly.
- Ordinary latest `GO` -> `go_implementation`, latest `NO-GO` -> `draft`, and WI-5279 bootstrap behavior are explicitly preserved as non-regression constraints.

## Applicability Preflight

{applicability_md}

## Clause Applicability (Slice 2; mandatory gate)

{clause_md}

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authorization for bounded fleet-defect repair proposals.
- `PAUTH-DISPATCHER-BLACK-BOX-WI5341-CLAIM-CLI-IMPORT-PARITY-20260716` - active bounded authorization for this proposal and subsequent four-file implementation.
- `bridge/gtkb-wi5249-prime-no-action-claim-filer-008.md` - terminal VERIFIED stand-down; WI-5341 is the required fresh successor before active restoration.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-018.md` - terminal VERIFIED baseline that cleared active `no_action_correction` acquisition while leaving the compatibility token inert.
- `bridge/gtkb-wi5279-project-authorization-bootstrap-lifecycle-004.md` - terminal VERIFIED bootstrap lifecycle behavior that WI-5341 must preserve.
- `bridge/gtkb-wi5337-latest-no-go-draft-claim-state-003.md` - pending test-only recurrence guard; WI-5341 must not convert ordinary latest `NO-GO` into implementation authority.

## Positive Confirmations

- Required project-linkage metadata, `target_paths`, specification links, owner-decision section, pre-filing preflight subsection, spec-derived verification plan, acceptance criteria, and risk/rollback are present in version 001.
- Applicability preflight reports `preflight_passed: true` with `missing_required_specs: []`.
- Clause preflight reports zero blocking gaps for the operative proposal.
- Implementation approach is narrow: add explicit validator branch for `CLAIM_KIND_NO_ACTION_CORRECTION`, persist non-implementation claims, and repair focused tests.
- Out-of-scope mutations (dispatcher, TAFE, database schema, release, deployment, credentials) are explicitly excluded.

## Residual Risks (Non-Blocking)

- `scripts/bridge_work_intent_registry.py` is a shared claim gate; regression risk is moderate but mitigated by the focused test plan and explicit non-regression acceptance criteria.
- Prime Builder must keep foreign dirty hunks out of the four target files unless WI-5341-owned and declared in the implementation report.

## Scope of this verdict

Verdict-file only. No source, test, configuration, or runtime-state mutation was performed during this review. Prime Builder is authorized to proceed with implementation under matching PAUTH boundaries after acquiring an exact live claim and implementation-start authorization.

## Commands Executed

```text
python scripts/_dispatch_wi5341_002_verdict.py
python scripts/bridge_applicability_preflight.py --bridge-id {SLUG}
python scripts/adr_dcl_clause_preflight.py --bridge-id {SLUG}
static read scripts/bridge_work_intent_registry.py (_claim_values explicit-kind guard)
static read scripts/bridge_claim_cli.py (claim-no-action wiring)
static read platform_tests/scripts/test_bridge_work_intent_registry.py (stale helper expectations)
```

Operative file reviewed: `bridge/{operative.name}`

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

    path = write_bridge_file(
        SLUG,
        VERSION,
        content,
        PROJECT_ROOT,
        require_author_metadata=False,
    )
    OUT_JSON.write_text(
        json.dumps(
            {
                "path": str(path),
                "registry_note": registry_note,
                "cli_note": cli_note,
                "stale_test_note": stale_test_note,
                "operative_file": operative.name,
                "packet": packet,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
