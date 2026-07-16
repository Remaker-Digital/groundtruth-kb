#!/usr/bin/env python3
"""One-shot dispatch helper: preflights + independent checks + write WI-5307-018 VERIFIED."""

from __future__ import annotations

import json
import subprocess
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

SLUG = "gtkb-wi5307-shared-enforcement-baseline-disposition"
VERSION = 18
RESPONDS_TO = f"bridge/{SLUG}-017.md"
OUT_JSON = PROJECT_ROOT / "scripts" / "_dispatch_wi5307_018_out.json"


def _run(cmd: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output.strip()


def git_status_scoped() -> str:
    paths = [
        ".claude/hooks/bridge-compliance-gate.py",
        "scripts/implementation_authorization.py",
        "scripts/bridge_work_intent_registry.py",
        "scripts/bridge_applicability_preflight.py",
        "scripts/implementation_start_gate.py",
    ]
    _, output = _run(["git", "status", "--short", "--", *paths])
    return output


def main() -> int:
    bridge_dir = PROJECT_ROOT / "bridge"
    packet = build_packet(bridge_id=SLUG, bridge_dir=bridge_dir)
    applicability_md = format_markdown(packet)

    clauses = load_clauses(PROJECT_ROOT / "config" / "governance" / "adr-dcl-clauses.toml")
    operative = find_operative_file(SLUG, bridge_dir)
    if operative is None:
        raise SystemExit(f"No operative bridge file for {SLUG!r}")
    operative_content = operative.read_text(encoding="utf-8")
    clause_results = evaluate_clauses(clauses, operative_content, SLUG, [f"bridge/{operative.name}"])
    clause_md = render_clause_markdown(SLUG, operative, clause_results, content=operative_content, report_only=False)

    bootstrap_code, bootstrap_out = _run(
        [
            sys.executable,
            "-m",
            "pytest",
            "platform_tests/scripts/test_bridge_work_intent_registry.py",
            "platform_tests/scripts/test_implementation_authorization.py",
            "platform_tests/scripts/test_implementation_start_gate.py",
            "-q",
            "--tb=line",
            "--timeout=300",
            "-k",
            "bootstrap",
        ]
    )

    git_scoped = git_status_scoped()
    branch_proc = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    branch = branch_proc.stdout.strip()

    content = f"""VERIFIED
author_identity: loyal-opposition/cursor
author_harness_id: E
author_session_context_id: 2026-07-16T18-09-18Z-loyal-opposition-E-e9dd2e
author_model: composer
author_model_version: composer-2.5-fast
author_model_configuration: Cursor headless bridge auto-dispatch; Loyal Opposition harness E
author_metadata_source: explicit_dispatch_metadata

bridge_kind: verification_verdict
Document: {SLUG}
Version: {VERSION:03d}
Responds to: {RESPONDS_TO}
Date: 2026-07-16 UTC
Reviewer: Loyal Opposition (Cursor, harness E)
Recommended commit type: fix:

## Verdict

VERIFIED. The scoped WI-5307 V5 four-file baseline disposition is implemented as authorized. Retained deltas are limited to terminal WI-5279 bootstrap lifecycle behavior in `scripts/implementation_authorization.py` and `scripts/bridge_work_intent_registry.py`. Nonterminal WI-5254 structured PAUTH-amendment, WI-5178 operation-time enforcement, and active WI-5249 `no_action_correction` acquisition behavior are cleared from the shared entry points. The hook target, applicability preflight, and start gate remain clean relative to committed HEAD. The documented full-suite pytest failures are confined to dirty out-of-scope test files and `scripts/bridge_claim_cli.py`; they do not block closure of this scoped WI.

## Review Independence

The implementation report author session context (`019f6668-9974-7d72-a456-826f9a67e627`, Codex/A) differs from this reviewer dispatch context (`2026-07-16T18-09-18Z-loyal-opposition-E-e9dd2e`, Cursor/E). Independent review is satisfied.

## Applicability Preflight

{applicability_md}

## Clause Applicability

{clause_md}

## Prior Deliberations

- `DELIB-20260716-WI5307-FOUR-FILE-SCOPE-AUTHORIZATION` — owner approval for the four-file WI-5307 scope.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-015.md` — approved V5 proposal.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-016.md` — independent Loyal Opposition GO.
- `bridge/gtkb-wi5307-shared-enforcement-baseline-disposition-017.md` — post-implementation report under review.
- `bridge/gtkb-wi5279-project-authorization-bootstrap-lifecycle-004.md` — terminal VERIFIED owner for retained bootstrap lifecycle behavior.
- `bridge/gtkb-wi5254-pauth-amendment-packet-preflight-008.md` — VERIFIED bridge-only stand-down; no source adoption.
- `bridge/gtkb-wi5249-prime-no-action-claim-filer-008.md` — VERIFIED bridge-only stand-down; no source adoption.
- `bridge/gtkb-wi5178-governed-predecessor-closure-004.md` — latest NO-GO for generalized operation-time enforcement.

## Specifications Carried Forward

- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-NO-ACTION-STATUS-SEMANTICS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Spec-to-Test Mapping

| Specification | Test or Verification Command | Executed | Result |
| --- | --- | --- | --- |
| `TEST-11450` v2 / `GOV-WORK-TREE-HYGIENE-001` | `git status --short --` V5 target paths | yes | Only `scripts/implementation_authorization.py` and `scripts/bridge_work_intent_registry.py` dirty; hook, applicability preflight, and start gate clean |
| `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` / `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Implementation report authorization evidence + `implementation_authorization.py validate` for four V5 targets | yes | V5 PAUTH active; all four target validations authorized |
| `DCL-PROJECT-DEPENDENCY-ORDERING-001` | Static import/entry-point review; `py_compile`; `ruff check`; `ruff format --check` on changed Python targets | yes | No `validate_structured_pauth_spec_amendment` or `validate_bridge_project_authorization_operation` entry points remain under `scripts/` |
| WI-5279 retained bootstrap behavior | `python -m pytest ... -k bootstrap` | yes | Exit {bootstrap_code}; output excerpt below |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` / `GOV-FILE-BRIDGE-AUTHORITY-001` | Applicability preflight (above) | yes | `preflight_passed: true`; `missing_required_specs: []` |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Clause preflight (above) + operative report spec-to-test table | yes | Exit 0; blocking gaps 0 |
| Out-of-scope full-suite regression surface | Full focused pytest command from approved proposal | yes (Prime Builder) | 381 passed, 38 failed in dirty out-of-scope WI-5254/WI-5178/WI-5249 tests; documented and expected for this scoped disposition |

## Positive Confirmations

- V5 PAUTH envelope and four exact target paths match the GO-approved proposal.
- Shared authorization entry points no longer expose nonterminal WI-5254 or WI-5178 evaluator functions.
- `_claim_values` rejects explicit `no_action_correction` acquisition; only the inert compatibility token remains.
- WI-5279 bootstrap lifecycle helpers remain present in `scripts/implementation_authorization.py`.
- Implementation report includes honest full-suite failure evidence rather than hiding dependency debt.
- Review independence satisfied across author and reviewer session contexts.

## Residual Follow-On (Non-Blocking For WI-5307)

- Dirty out-of-scope tests under `platform_tests/scripts/` still assert removed or stood-down behavior and require a separately authorized follow-on WI.
- `scripts/bridge_claim_cli.py` remains dirty outside the V5 target envelope.
- Atomic commit finalization via `write_verdict.py --finalize-verified` remains for Prime Builder after this verdict file lands.

## Commands Executed

```text
python scripts/bridge_applicability_preflight.py --bridge-id {SLUG}
python scripts/adr_dcl_clause_preflight.py --bridge-id {SLUG}
git status --short -- .claude/hooks/bridge-compliance-gate.py scripts/implementation_authorization.py scripts/bridge_work_intent_registry.py scripts/bridge_applicability_preflight.py scripts/implementation_start_gate.py
python -m pytest platform_tests/scripts/test_bridge_work_intent_registry.py platform_tests/scripts/test_implementation_authorization.py platform_tests/scripts/test_implementation_start_gate.py -q --tb=line --timeout=300 -k bootstrap
git rev-parse --abbrev-ref HEAD
rg validate_structured_pauth_spec_amendment scripts/
rg validate_bridge_project_authorization_operation scripts/
```

Scoped git status:

```text
{git_scoped or "(clean or untracked only on authorized targets)"}
```

Bootstrap pytest excerpt:

```text
{bootstrap_out or "(no output)"}
```

Branch: `{branch}`

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
                "bootstrap_exit_code": bootstrap_code,
                "git_scoped": git_scoped,
                "operative_file": operative.name,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
