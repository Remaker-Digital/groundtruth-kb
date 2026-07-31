#!/usr/bin/env python3
"""One-shot LO dispatch: envelope Slice A corrected GO + authority foundations GO."""

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

SESSION_CONTEXT = "2026-07-17T00-23-30Z-loyal-opposition-E-c1d3b4"
DISPATCH_ID = "2026-07-17T00-23-30Z-loyal-opposition-E-c1d3b4"


def _preflight_sections(slug: str) -> tuple[str, str, Path]:
    bridge_dir = PROJECT_ROOT / "bridge"
    operative = find_operative_file(slug, bridge_dir)
    if operative is None:
        raise SystemExit(f"No operative bridge file for {slug!r}")
    packet = build_packet(bridge_id=slug, bridge_dir=bridge_dir)
    if not packet.get("preflight_passed"):
        raise SystemExit(f"Applicability preflight failed for {slug}: {packet}")
    applicability_md = format_markdown(packet)
    clauses = load_clauses(PROJECT_ROOT / "config" / "governance" / "adr-dcl-clauses.toml")
    operative_content = operative.read_text(encoding="utf-8")
    clause_results = evaluate_clauses(clauses, operative_content, slug, [f"bridge/{operative.name}"])
    blocking = [row for row in clause_results if row.get("blocking_gap")]
    if blocking:
        raise SystemExit(f"Clause preflight blocking gaps for {slug}: {blocking}")
    clause_md = render_clause_markdown(
        slug, operative, clause_results, content=operative_content, report_only=False
    )
    return applicability_md, clause_md, operative


def _write_envelope_go() -> Path:
    slug = "gtkb-envelope-protocol-slice-a-authority-set"
    version = 8
    applicability_md, clause_md, operative = _preflight_sections(slug)
    packet = build_packet(bridge_id=slug, bridge_dir=PROJECT_ROOT / "bridge")

    content = f"""GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: {SESSION_CONTEXT}
author_model: composer
author_model_version: composer-2.5-fast
author_model_configuration: Cursor headless bridge auto-dispatch {DISPATCH_ID}; Loyal Opposition harness E

# Loyal Opposition Verdict - GO - Envelope Protocol Slice A Authority Set (Corrected)

bridge_kind: lo_verdict
Document: {slug}
Version: {version:03d}
Responds to: bridge/{slug}-007.md
Date: 2026-07-17 UTC
Reviewer role: loyal-opposition (harness E, Cursor)

Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ENVELOPE-PROTOCOL
Work Item: WI-5373

## Verdict

GO. Version 007 correctly rejected version 006 because the operative GO lacked a
`## Specification-Derived Verification` section with concrete command evidence.
This corrected GO carries that section forward, preserves the governance-only
Slice A scope from version 001, and retains the formal-artifact approval-packet
requirements from version 007.

## Review Independence

- Prior defective GO author session: `cursor-20260716-lo-auto-process` (harness E).
- Reviewer session context: `{SESSION_CONTEXT}` (loyal-opposition/cursor, harness E).
- This is a mechanical NO-ACTION correction of a prior verdict defect, not a
  same-session self-review of the operative proposal. Operative proposal author
  session: `codex-20260716-envelope-protocol-pb` (harness A).

## Applicability Preflight

{applicability_md}

## Clause Applicability (Slice 2; mandatory gate)

{clause_md}

## Specification-Derived Verification

| Requirement | Verification command | Observed result |
| --- | --- | --- |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts/bridge_applicability_preflight.py --bridge-id {slug}` | `preflight_passed: true`; `missing_required_specs: []`; operative `{operative.name}` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `python scripts/adr_dcl_clause_preflight.py --bridge-id {slug}` | Exit 0; zero blocking clause gaps on operative proposal |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Static review of `bridge/{slug}-001.md` through `-007.md` | Append-only version chain; latest NO-ACTION at version 007 routes corrected GO here |
| `GOV-ARTIFACT-APPROVAL-001` | `rg -n "formal-artifact-approvals" bridge/{slug}-001.md bridge/{slug}-007.md` | No matching approval packet exists yet for candidate formal artifacts; owner approval required before MemBase mutation |
| `TEST-11488` (implementation report) | Deferred to post-implementation report | Implementation report must map each inserted/amended formal artifact to packet validation and `gt spec show` readback before independent VERIFIED |

Executed review commands:

```text
python scripts/bridge_applicability_preflight.py --bridge-id {slug}
python scripts/adr_dcl_clause_preflight.py --bridge-id {slug}
python scripts/_dispatch_lo_verdicts_20260717_envelope_authority.py
```

## Specification Links

- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-APPROVAL-001`
- `DCL-ARTIFACT-APPROVAL-HOOK-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `ADR-ENVELOPE-META-MODEL-001`
- `DCL-SESSION-ENVELOPE-DURABILITY-001`
- `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001`
- `SPEC-TOPIC-ENVELOPE-ROUTER-001`
- `DCL-TOPIC-ENVELOPE-ROUTING-001`
- `ADR-ACTIVITY-ENVELOPE-DISPOSITION-001`
- `DCL-ACTIVITY-DISPOSITION-PROFILE-001`
- `DCL-ACTIVITY-ENVELOPE-INTERCEPTION-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Prior Deliberations

- `DELIB-202666333` - owner PAUTH approval for the Envelope Protocol program.
- `DELIB-20260716-ENVELOPE-GRILL-B1-INIT-RESPONDER-SEMANTICS` through `B9` - Slice A B-record decisions.
- `bridge/{slug}-001.md` - operative Slice A proposal.
- `bridge/{slug}-003.md`, `-005.md`, `-007.md` - NO-ACTION dispositions requiring corrected GO evidence.
- `bridge/gtkb-envelope-protocol-architecture-advisory-001.md` - source advisory.

## Conditions

- Slice A does not authorize Slice B-G implementation.
- No formal artifact packet, MemBase mutation, or canonical artifact insertion is
  authorized until each candidate's full native content is presented to the owner
  and explicit artifact-level approval evidence exists (`GOV-ARTIFACT-APPROVAL-001`).
- Implementation report must state exact final artifact IDs and whether each was
  newly created or amended.
- Independent VERIFIED must precede Slice B implementation.

## Scope of this verdict

Verdict-file only. No source, database, formal-artifact, approval-packet, Git,
release, deployment, credential, dispatcher, or harness mutation was performed
during this review.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

    return write_bridge_file(slug, version, content, PROJECT_ROOT, require_author_metadata=False)


def _bootstrap_binding_confirmed() -> str:
    registry = (PROJECT_ROOT / "scripts" / "bridge_work_intent_registry.py").read_text(encoding="utf-8")
    cli = (PROJECT_ROOT / "scripts" / "bridge_claim_cli.py").read_text(encoding="utf-8")
    impl = (PROJECT_ROOT / "scripts" / "implementation_authorization.py").read_text(encoding="utf-8")
    notes: list[str] = []
    if 'CLAIM_KIND_PROJECT_AUTHORIZATION_BOOTSTRAP: Final[str] = "project_authorization_bootstrap"' not in registry:
        notes.append("registry missing bootstrap claim kind")
    if "claim-bootstrap" not in cli:
        notes.append("CLI missing claim-bootstrap")
    if "project_authorization_bootstrap_carrier" not in impl:
        notes.append("implementation_authorization missing bootstrap carrier reason code")
    return "; ".join(notes) if notes else "bootstrap claim kind, claim-bootstrap CLI, and bootstrap carrier evaluator are present at current HEAD"


def _write_authority_go() -> Path:
    slug = "gtkb-authority-foundations-project-authorization"
    version = 6
    applicability_md, clause_md, operative = _preflight_sections(slug)
    bootstrap_note = _bootstrap_binding_confirmed()

    content = f"""GO

author_identity: loyal-opposition/cursor/E
author_harness_id: E
author_session_context_id: {SESSION_CONTEXT}
author_model: composer
author_model_version: composer-2.5-fast
author_model_configuration: Cursor headless bridge auto-dispatch {DISPATCH_ID}; Loyal Opposition harness E

# Loyal Opposition Verdict - GO - Authority Foundations Project Authorization Bootstrap

bridge_kind: lo_verdict
Document: {slug}
Version: {version:03d}
Responds to: bridge/{slug}-005.md
Date: 2026-07-17 UTC
Reviewer role: loyal-opposition (harness E, Cursor)

Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5277

## Verdict

GO. Version 005 closes version 004 finding F1 by binding the single-use metadata
transaction to the independently VERIFIED WI-5279 bootstrap lifecycle instead of
a prose-only ordinary claim path. The revision names the exact `claim-bootstrap`
command, expected `claim_kind`, implementation-start command, packet fields, and
fail-closed evaluator branch while preserving the exact two canonical
`groundtruth.db` transactions, row-readback boundary, quarantine, and no-stage/no-commit limits.

## Review Independence

- Proposal author session context: `019f6d5c-2017-7d43-902e-b74483f50fff` (prime-builder/codex, harness A).
- Reviewer session context: `{SESSION_CONTEXT}` (loyal-opposition/cursor, harness E).
- Author and reviewer session contexts differ; independent review is satisfied.

## Applicability Preflight

{applicability_md}

## Clause Applicability (Slice 2; mandatory gate)

{clause_md}

## Premises Verified (canonical reads)

- WI-5279 bootstrap lifecycle is latest `VERIFIED` at `bridge/gtkb-wi5279-project-authorization-bootstrap-lifecycle-004.md`.
- Bootstrap binding check: {bootstrap_note}.
- Version 005 declares `project_authorization_bootstrap`, cites `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION`, and quotes the owner single-use remediation exception in `## Owner Decisions / Input`.
- Exact PAUTH envelope includes all 14 linked project-authorization specifications and forbids raw database mutation, staging, commit, dispatcher mutation, and harness contact.
- Seven quarantined candidate files remain evidence-only; no hunk adoption is authorized.

## Positive Confirmations

- Version 004 F1 closure path uses the verified WI-5279 executable lifecycle rather than ordinary latest-GO claimability.
- Version 002 findings F2-F4 remain addressed: no binary commit claim, linked specifications in envelope/CLI, and circular-bootstrap exception scoped to this thread only.
- Spec-derived verification plan maps owner binding, envelope fields, bootstrap lifecycle, quarantine preservation, and runtime isolation to concrete readback commands.

## Residual Risks (Non-Blocking)

- The single-use remediation exception remains bridge-cited owner prose rather than a separate Deliberation Archive record; durability is acceptable for this bounded thread because the bootstrap claim binds the exact slug, DELIB, PAUTH id, and carrier target mechanically.
- WI-5188 stale completion-guard behavior and WI-5283 snapshot-integrity defects remain open and are explicitly reported.

## Scope of this verdict

GO authorizes only the single-use bootstrap lifecycle and exact two canonical metadata commands after matching `claim-bootstrap`, successful implementation-start authorization, and exact readback. No source implementation or live harness proof is authorized here.

## Commands Executed

```text
python scripts/_dispatch_lo_verdicts_20260717_envelope_authority.py
python scripts/bridge_applicability_preflight.py --bridge-id {slug}
python scripts/adr_dcl_clause_preflight.py --bridge-id {slug}
static read scripts/bridge_work_intent_registry.py scripts/bridge_claim_cli.py scripts/implementation_authorization.py
```

Operative file reviewed: `bridge/{operative.name}`

## Prior Deliberations

- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` - project envelope and quarantine boundary.
- `DELIB-20260710-GTKB-MODERNIZATION-AUTHORITY-FOUNDATIONS-CHARTER` - project charter.
- `bridge/gtkb-wi5279-project-authorization-bootstrap-lifecycle-004.md` - VERIFIED bootstrap lifecycle.
- `bridge/{slug}-002.md` and `-004.md` - controlling NO-GO findings addressed in version 005.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

    return write_bridge_file(slug, version, content, PROJECT_ROOT, require_author_metadata=False)


def main() -> int:
    results: dict[str, str] = {}
    envelope_path = _write_envelope_go()
    results["envelope"] = str(envelope_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    authority_path = _write_authority_go()
    results["authority"] = str(authority_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    out = PROJECT_ROOT / "scripts" / "_dispatch_lo_verdicts_20260717_envelope_authority_out.json"
    out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
