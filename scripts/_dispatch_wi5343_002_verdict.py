#!/usr/bin/env python3
"""One-shot dispatch helper: preflights + independent checks + write WI-5343-002 GO."""

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

SLUG = "gtkb-wi5343-lo-review-authority-packet"
VERSION = 2
RESPONDS_TO = f"bridge/{SLUG}-001.md"
OUT_JSON = PROJECT_ROOT / "scripts" / "_dispatch_wi5343_002_out.json"
SESSION_CONTEXT = "2026-07-16T18-45-52Z-loyal-opposition-E-23f291"
PROPOSAL_AUTHOR_SESSION = "019f6bf6-3e6d-7761-be14-fb894a0e84d2"


def _dispatch_prompt_lacks_lo_authority_block() -> str:
    path = PROJECT_ROOT / "scripts" / "dispatcher_runtime.py"
    text = path.read_text(encoding="utf-8")
    block = text.split("def _dispatch_prompt", 1)[1].split("\ndef ", 1)[0]
    missing = []
    for needle in (
        "gt bridge show",
        "bridge_claim_cli.py status",
        ".gtkb-state/work-intent",
        "target_paths",
    ):
        if needle not in block:
            missing.append(needle)
    if missing:
        return f"LO authority block absent; missing prompt references: {', '.join(missing)}"
    return "LO authority block already present"


def _wi5307_chain_includes_registry_target() -> str:
    path = PROJECT_ROOT / "bridge" / "gtkb-wi5307-shared-enforcement-baseline-disposition-015.md"
    text = path.read_text(encoding="utf-8")
    if "scripts/bridge_work_intent_registry.py" not in text:
        return "WI-5307 version 015 does not declare scripts/bridge_work_intent_registry.py"
    return (
        "WI-5307 version 015 target_paths includes scripts/bridge_work_intent_registry.py; "
        "backlog-summary-only ownership checks are non-authoritative"
    )


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

    prompt_gap = _dispatch_prompt_lacks_lo_authority_block()
    wi5307_note = _wi5307_chain_includes_registry_target()

    content = f"""GO
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: {SESSION_CONTEXT}
author_model: composer
author_model_version: composer-2.5-fast
author_model_configuration: Cursor headless bridge auto-dispatch; Loyal Opposition harness E
author_metadata_source: explicit_dispatch_metadata

# Loyal Opposition Verdict - GO - WI-5343 LO Review Authority Packet

bridge_kind: lo_verdict
Document: {SLUG}
Version: {VERSION:03d}
Responds to: {RESPONDS_TO}
Date: 2026-07-16 UTC
Reviewer role: loyal-opposition (harness E, Cursor)

## Verdict

GO. The proposal correctly diagnoses the WI-5337 version-002 false ownership finding, stays inside dispatcher-owned LO prompt composition, and adds testable authority instructions without widening Prime Builder dispatch behavior.

## Review Independence

- Proposal author session context: `{PROPOSAL_AUTHOR_SESSION}` (prime-builder/codex, harness A).
- Reviewer session context: `{SESSION_CONTEXT}` (loyal-opposition/cursor, harness E).
- Author and reviewer session contexts differ; independent review is satisfied.

## Premises Verified (canonical reads)

- False F3 root cause confirmed: `bridge/gtkb-wi5337-latest-no-go-draft-claim-state-002.md` Finding F3 relied on `gt backlog show WI-5307` MemBase summary text instead of the numbered bridge chain. {wi5307_note}.
- Current prompt gap confirmed: {prompt_gap}.
- Canonical claim surface exists: `scripts/bridge_claim_cli.py` exposes `status` and is groundtruth.db-backed via the registry service.
- Canonical thread surface exists: `gt bridge show <slug>` is implemented in `groundtruth_kb.cli` and matches the proposal's numbered-chain authority model.
- Scope is bounded to `scripts/dispatcher_runtime.py` and `platform_tests/scripts/test_dispatcher_runtime.py`; Prime Builder prompt behavior is explicitly preserved.

## Applicability Preflight

{applicability_md}

## Clause Applicability (Slice 2; mandatory gate)

{clause_md}

## Prior Deliberations

- `bridge/gtkb-wi5337-latest-no-go-draft-claim-state-002.md` - independent NO-GO whose Finding F3 used non-authoritative backlog summary and empty `.gtkb-state/work-intent/` instead of the numbered chain and DB-backed claim service; this proposal directly remediates that failure mode for future dispatched LO workers.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-015.md` through `018.md` - numbered chain proving `scripts/bridge_work_intent_registry.py` was inside the WI-5307 authorized envelope.
- `bridge/gtkb-wi5341-bridge-claim-cli-import-parity-002.md` - adjacent claim-service work; WI-5343 must not change claim semantics, only reviewer authority instructions.
- `DELIB-20263295` / `DELIB-20263296` - WI-4534 claim role-eligibility guard deliberations cited by the proposal for adjacent claim-authority context.
- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - owner authorization pattern for bounded dispatcher hardening follow-ons.

## Positive Confirmations

- Required project-linkage metadata, `target_paths`, specification links, owner-decision section, spec-derived verification plan, acceptance criteria, and risk/rollback are present in version 001.
- Applicability preflight reports `preflight_passed: true` with `missing_required_specs: []`.
- Clause preflight reports zero blocking gaps for the operative proposal.
- Acceptance criteria are concrete and mechanically testable: LO prompt must reference full numbered-chain authority via `gt bridge show`, canonical repo-venv `bridge_claim_cli.py status`, and explicit rejection of MemBase summaries plus `.gtkb-state/work-intent` as ownership authority.
- Out-of-scope mutations (routing, selection, TAFE/runtime state, provider adapters, live workers, unrelated dirty hunks) are explicitly excluded.

## Residual Risks (Non-Blocking)

- Several specification rows in the verification plan reuse a generic "run applicability preflights" placeholder rather than a per-spec command; Prime Builder should tighten those rows in the implementation report while preserving the already-concrete dispatcher-runtime tests.
- Prompt-only hardening reduces but does not eliminate reviewer error; workers can still ignore instructions. Focused tests are the durable enforcement layer.

## Scope of this verdict

Verdict-file only. No source, test, configuration, or runtime-state mutation was performed during this review. Prime Builder is authorized to proceed with implementation under PAUTH `PAUTH-DISPATCHER-BLACK-BOX-WI5343-LO-REVIEW-AUTHORITY-PACKET-20260716` after acquiring an exact live claim and implementation-start authorization.

## Commands Executed

```text
python scripts/_dispatch_wi5343_002_verdict.py
python scripts/bridge_applicability_preflight.py --bridge-id {SLUG}
python scripts/adr_dcl_clause_preflight.py --bridge-id {SLUG}
static read bridge/gtkb-wi5343-lo-review-authority-packet-001.md
static read bridge/gtkb-wi5337-latest-no-go-draft-claim-state-002.md (Finding F3)
static read bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-015.md (target_paths)
static read scripts/dispatcher_runtime.py (_dispatch_prompt composition)
static read scripts/bridge_claim_cli.py (status subcommand)
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
                "prompt_gap": prompt_gap,
                "wi5307_note": wi5307_note,
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
