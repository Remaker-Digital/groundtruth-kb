"""S153 Phase 3 — Retire process/governance directive specs as OBSOLETE.

Per owner directive: process/governance directives are not specifications.
Content already reflected in CLAUDE.md governance rules (GOV-01..17) or
MEMORY.md session procedures. One-time tasks and outdated directives retired.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys

sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()

SESSION = "S153"

# Process/governance specs to retire with reasons
process_specs = {
    # Already covered by GOV rules in CLAUDE.md
    "SPEC-0224": "Process directive — covered by GOV-12 (WI triggers tests) and GOV-13 (phase assignment)",
    "SPEC-0274": "Process directive — covered by GOV-04 (maturation) and session wrap-up procedure",
    "SPEC-0343": "Process directive — covered by GOV-12 (WI triggers tests) and backlog workflow",
    "SPEC-0344": "Process directive — covered by specification workflow in CLAUDE.md",
    "SPEC-0600": "Process directive — duplicate of SPEC-0274, covered by session wrap-up procedure",
    "SPEC-0729": "Process directive — covered by GOV-07 (no fixes during testing) and GOV-12",
    "SPEC-0730": "Process directive — duplicate of SPEC-0274/0600",
    "SPEC-0783": "Process directive — covered by GOV-15 (test fix gate)",
    "SPEC-0790": "Process directive — covered by GOV-10 (live interfaces only)",
    "SPEC-0791": "Process directive — covered by GOV-07 (defects as WIs) and GOV-12",
    "SPEC-0773": "Process directive — specific test ordering rule, covered by PLAN-001 phases",
    "SPEC-0774": "Process directive — covered by GOV-07 (no fixes during testing)",
    # Quality/release gate process directives
    "SPEC-0834": "Process directive — quality standard for GA release, covered by GOV-17 (quality first)",
    "SPEC-0835": "Process directive — quality standard for GA release, covered by GOV-17",
    "SPEC-0836": "Process directive — beta feedback process, covered by release plan",
    # One-time tasks or outdated directives
    "SPEC-0226": "One-time task — re-test after CSS changes; CSS centralization not yet done",
    "SPEC-0232": "One-time task — merge test procedures 4 and 8; no longer applicable",
    "SPEC-0276": "Outdated session instruction — session init now uses CLAUDE.md + hooks",
    "SPEC-0278": "One-time task — comprehensive WI review; completed in prior sessions",
    "SPEC-0314": "Outdated session instruction — P1 pre-launch tests",
    "SPEC-0341": "Process directive — adversarial testing timing, not a code specification",
    "SPEC-0351": "One-time task — security assessment of dev environment",
    "SPEC-0410": "Outdated release scope — blocked capabilities list from early planning",
    "SPEC-0414": "Process directive — beta issue priority, covered by GOV-17",
    "SPEC-0447": "Process directive — timing of new features, not a specification",
    "SPEC-0466": "Outdated session directive — parallel work instruction",
    "SPEC-0467": "Outdated priority assignment — Provider monitoring RB priorities",
    "SPEC-0468": "Outdated priority assignment — Provider monitoring Critical priorities",
    "SPEC-0469": "Outdated priority assignment — Provider monitoring HV priority upgrade",
    "SPEC-0470": "Process directive — memory issue priority, covered by GOV-17",
    "SPEC-0492": "Process directive — procedure content requirement, already practiced",
    "SPEC-0511": "One-time task — KB context efficiency review",
    "SPEC-0536": "Process directive — external URL testing, covered by PLAN-001 phases",
    "SPEC-0540": "One-time task — competitive analysis to KB",
    "SPEC-0556": "Process directive — WI grouping style, project management preference",
    "SPEC-0561": "Process directive — re-testing scope, project management approach",
    "SPEC-0645": "Process directive — copy-of-record location rule, covered by GOV-08 (KB is truth)",
    "SPEC-0742": "One-time task — alignment audit across 4 systems",
    "SPEC-0745": "One-time decision — PTU deferred; already captured",
    "SPEC-0780": "Process directive — release plan steps, covered by release plan DOC-135",
    "SPEC-0786": "Process directive — provisioning smoke test step, covered by PLAN-001",
    "SPEC-0788": "Process directive — SPA provisioning pre-test, covered by PLAN-001",
    "SPEC-0798": "Process directive — owner working style preference (WIs one at a time)",
    "SPEC-0808": "Process directive — WI grouping preference",
    "SPEC-0826": "Outdated release checklist — remaining 1.0 WIs",
    "SPEC-0844": "One-time directive — build and deploy before go/no-go",
    "SPEC-0855": "One-time setup — GitHub repo/board association",
    "SPEC-0618": "Process directive — add chat widget tests to plan; test creation governed by GOV-12",
    "SPEC-0737": "Process directive — UI review methodology",
    "SPEC-0738": "Process directive — UI review methodology",
    # Old-format IDs
    "202": "Process directive — deploy and verify, one-time task instruction",
}

total = 0
for sid, reason in process_specs.items():
    db.update_spec(
        sid,
        changed_by=SESSION,
        change_reason=f"OBSOLETE — {reason}. Owner directive: process directives are not specifications.",
        status="retired",
    )
    print(f"  Retired {sid}: {reason[:60]}...")
    total += 1

print(f"\n--- Retired {total} process/governance specs ---")
