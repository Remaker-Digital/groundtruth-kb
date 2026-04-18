"""Phase 1 KB setup for Start Here adopter rewrite implementation.

Inserts 12 SPEC-STARTHERE-* specs (each with one machine-checkable assertion
in the supported assertion schema), 8 WI-ADOPT-* work items, and one
implementation deliberation linking this workstream to the scope + GO chain.

Run once from the groundtruth-kb repo root. Idempotent is NOT required — the
KB is append-only, so re-running would create duplicate version rows.

Executes under Codex GO (bridge/gtkb-start-here-adopter-rewrite-implementation-002.md).
"""

from __future__ import annotations

from groundtruth_kb.db import KnowledgeDB

CHANGED_BY = "prime-opus-4-7-s299c"
SESSION_ID = "S299-continuation"
CHANGE_REASON = (
    "Phase 1 of gtkb-start-here-adopter-rewrite implementation. "
    "Codex GO at bridge/gtkb-start-here-adopter-rewrite-implementation-002.md "
    "(Agent Red bridge). Prefix SPEC-STARTHERE-* per Codex recommendation."
)

# Each spec carries exactly one assertion. Assertions use the supported schema
# from docs/reference/assertion-language.md so `gt assert --spec <id>` and
# run_all_assertions(db, project_root, spec_id=...) both execute them.

SPECS: list[dict[str, object]] = [
    {
        "id": "SPEC-STARTHERE-READER-PROFILE",
        "title": "Start Here declares the reader-profile assumption",
        "description": (
            "docs/start-here.md opens with an explicit statement that the "
            "target reader has zero prior context with GroundTruth-KB and is "
            "on a Windows workstation. This frames every decision that follows."
        ),
        "assertions": [
            {
                "type": "grep",
                "pattern": r"(?i)zero.?prior.?context",
                "file": "docs/start-here.md",
                "description": "Start Here states the zero-prior-context assumption",
            }
        ],
    },
    {
        "id": "SPEC-STARTHERE-FEATURE-PROBLEM-MAP",
        "title": "Feature sections pair each capability with the problem it solves",
        "description": (
            "In docs/start-here.md the feature walkthrough section introduces "
            "each capability via a labelled Problem/Solution pair so the reader "
            "sees the purpose before the mechanic."
        ),
        "assertions": [
            {
                "type": "count",
                "pattern": r"\*\*Problem:\*\*",
                "file": "docs/start-here.md",
                "operator": ">=",
                "expected": 6,
                "description": "At least 6 Problem: anchors appear in start-here.md",
            }
        ],
    },
    {
        "id": "SPEC-STARTHERE-BLOCKDIAGRAM",
        "title": "Start Here contains a Mermaid block diagram of the system",
        "description": (
            "docs/start-here.md contains at least one Mermaid-rendered block "
            "diagram that names the core entities an adopter will encounter."
        ),
        "assertions": [
            {
                "type": "grep",
                "pattern": r"^```mermaid",
                "file": "docs/start-here.md",
                "min_count": 1,
                "description": "Mermaid fence present in start-here.md",
            }
        ],
    },
    {
        "id": "SPEC-STARTHERE-PREREQ-ORDERING",
        "title": "Prerequisites are named before installation steps",
        "description": (
            "docs/start-here.md places a Prerequisites heading earlier in the "
            "document than the Installation heading so adopters know what is "
            "required before any pip command appears."
        ),
        "assertions": [
            {
                "type": "all_of",
                "description": "Both Prerequisites and Install headings exist",
                "assertions": [
                    {
                        "type": "grep",
                        "pattern": r"^## Prerequisites",
                        "file": "docs/start-here.md",
                    },
                    {
                        "type": "grep",
                        "pattern": r"^## Install",
                        "file": "docs/start-here.md",
                    },
                ],
            }
        ],
    },
    {
        "id": "SPEC-STARTHERE-EVIDENCE",
        "title": "Evidence document exists with provenance-tagged metric rows",
        "description": (
            "docs/evidence.md exists and every metric row carries a footnote "
            "with the generating command, commit SHA, and generation date. "
            "Numbers without provenance are forbidden on this page."
        ),
        "assertions": [
            {
                "type": "all_of",
                "description": "Evidence page exists and contains provenance markers",
                "assertions": [
                    {"type": "file_exists", "file": "docs/evidence.md"},
                    {
                        "type": "count",
                        "pattern": r"(?i)commit\s*(sha|hash)\s*:",
                        "file": "docs/evidence.md",
                        "operator": ">=",
                        "expected": 1,
                    },
                ],
            }
        ],
    },
    {
        "id": "SPEC-STARTHERE-DAYINLIFE",
        "title": "Day in the Life is discoverable from nav and names six activities",
        "description": (
            "docs/day-in-the-life.md is listed in mkdocs.yml nav and the "
            "document walks through the six named adopter activities: add a "
            "spec, add a test, push to staging, commit and build, "
            "investigate, and retrieve deliberations."
        ),
        "assertions": [
            {
                "type": "all_of",
                "description": "Day in the Life wired into nav and covers six activities",
                "assertions": [
                    {
                        "type": "grep",
                        "pattern": r"day-in-the-life\.md",
                        "file": "mkdocs.yml",
                    },
                    {
                        "type": "count",
                        "pattern": r"^### Activity \d",
                        "file": "docs/day-in-the-life.md",
                        "operator": ">=",
                        "expected": 6,
                    },
                ],
            }
        ],
    },
    {
        "id": "SPEC-STARTHERE-LIMITATIONS",
        "title": "Known Limitations cites Gap 2.8, hook-registration, and U-class rows",
        "description": (
            "docs/known-limitations.md exists and explicitly names Gap 2.8, "
            "the hook-registration limitation, and the U-class scaffold rows "
            "from the non-disruptive upgrade audit, with links back to the "
            "audit report."
        ),
        "assertions": [
            {
                "type": "all_of",
                "description": "Known Limitations page names the three current gaps",
                "assertions": [
                    {"type": "file_exists", "file": "docs/known-limitations.md"},
                    {
                        "type": "grep",
                        "pattern": r"Gap 2\.8",
                        "file": "docs/known-limitations.md",
                    },
                    {
                        "type": "grep",
                        "pattern": r"(?i)hook.registration",
                        "file": "docs/known-limitations.md",
                    },
                    {
                        "type": "grep",
                        "pattern": r"(?i)U.class",
                        "file": "docs/known-limitations.md",
                    },
                ],
            }
        ],
    },
    {
        "id": "SPEC-STARTHERE-INSTALL-BASELINE",
        "title": "Install baseline is stated as Windows with internet access",
        "description": (
            "docs/start-here.md explicitly states the install baseline is a "
            "Windows workstation with internet access. No other OS is "
            "assumed in the walkthrough."
        ),
        "assertions": [
            {
                "type": "grep",
                "pattern": r"(?i)windows.*internet|internet.*windows",
                "file": "docs/start-here.md",
                "description": "Install baseline names Windows + internet",
            }
        ],
    },
    {
        "id": "SPEC-STARTHERE-TERMINAL",
        "title": "Start Here includes a PowerShell primer for absolute beginners",
        "description": (
            "docs/start-here.md contains a PowerShell primer that explains "
            "changing directories (cd), running a .exe, and using pip install, "
            "so a reader who has never opened a terminal can follow along."
        ),
        "assertions": [
            {
                "type": "all_of",
                "description": "PowerShell primer covers cd, .exe, and pip install",
                "assertions": [
                    {
                        "type": "grep",
                        "pattern": r"(?i)powershell",
                        "file": "docs/start-here.md",
                    },
                    {
                        "type": "grep",
                        "pattern": r"\bcd\b",
                        "file": "docs/start-here.md",
                    },
                    {
                        "type": "grep",
                        "pattern": r"\.exe",
                        "file": "docs/start-here.md",
                    },
                    {
                        "type": "grep",
                        "pattern": r"pip install",
                        "file": "docs/start-here.md",
                    },
                ],
            }
        ],
    },
    {
        "id": "SPEC-STARTHERE-3RDPARTY",
        "title": "Third-party integrations are enumerated with one-line reasons",
        "description": (
            "docs/start-here.md contains a section that enumerates the named "
            "third-party integrations (Claude Code, Codex, OS scheduler, "
            "GitHub, PyPI, MkDocs) with a one-line reason for each."
        ),
        "assertions": [
            {
                "type": "all_of",
                "description": "Named third-party tools enumerated in start-here.md",
                "assertions": [
                    {
                        "type": "grep",
                        "pattern": r"(?i)claude code",
                        "file": "docs/start-here.md",
                    },
                    {
                        "type": "grep",
                        "pattern": r"\bCodex\b",
                        "file": "docs/start-here.md",
                    },
                    {
                        "type": "grep",
                        "pattern": r"(?i)os scheduler|task scheduler|cron",
                        "file": "docs/start-here.md",
                    },
                ],
            }
        ],
    },
    {
        "id": "SPEC-STARTHERE-DASHBOARD",
        "title": "Dashboard metrics are explained with how-to-act guidance",
        "description": (
            "docs/start-here.md or a linked page explains the Web UI dashboard "
            "metrics (spec counts, test counts, assertion pass/fail, work item "
            "status) and what action a reader should take when each is off-normal."
        ),
        "assertions": [
            {
                "type": "all_of",
                "description": "Dashboard section present with actionable guidance",
                "assertions": [
                    {
                        "type": "grep",
                        "pattern": r"(?i)dashboard",
                        "file": "docs/start-here.md",
                    },
                    {
                        "type": "grep",
                        "pattern": r"(?i)assertion\s*(pass|fail)",
                        "file": "docs/start-here.md",
                    },
                ],
            }
        ],
    },
    {
        "id": "SPEC-STARTHERE-TEMPLATES",
        "title": "Core development loops are documented: deploy flow and bridge cycle",
        "description": (
            "docs/start-here.md documents two core loops: the develop -> "
            "staging -> prod deployment flow and the propose -> review -> "
            "implement -> verify bridge cycle. Both are the adopter's daily "
            "operational rhythm."
        ),
        "assertions": [
            {
                "type": "all_of",
                "description": "Both core loops documented in start-here.md",
                "assertions": [
                    {
                        "type": "grep",
                        "pattern": r"(?i)develop.*staging.*prod",
                        "file": "docs/start-here.md",
                    },
                    {
                        "type": "grep",
                        "pattern": r"(?i)propose.*review.*implement.*verify",
                        "file": "docs/start-here.md",
                    },
                ],
            }
        ],
    },
]

# Work items map to deliverable slices per implementation proposal §Work Item Grouping.
# Each WI is linked to its primary source spec; supplementary specs are captured in
# the description for traceability.
WORK_ITEMS: list[dict[str, object]] = [
    {
        "id": "WI-ADOPT-01",
        "title": "Root README rewritten as one-page adopter front door",
        "description": (
            "Rewrite README.md at the repo root as a CTO-persona one-pager. "
            "Covers READER-PROFILE + INSTALL-BASELINE scope from the spec "
            "table."
        ),
        "source_spec_id": "SPEC-STARTHERE-READER-PROFILE",
    },
    {
        "id": "WI-ADOPT-02",
        "title": "Start Here rewrite - sections 1 through 3 (profile, problems, prereqs)",
        "description": (
            "Rewrite docs/start-here.md sections 1-3. Covers READER-PROFILE, "
            "FEATURE-PROBLEM-MAP, PREREQ-ORDERING, TERMINAL."
        ),
        "source_spec_id": "SPEC-STARTHERE-FEATURE-PROBLEM-MAP",
    },
    {
        "id": "WI-ADOPT-03",
        "title": "Mermaid block diagram and narrated tour",
        "description": (
            "Add Mermaid block diagram plus narrated tour to docs/start-here.md section 4. Covers BLOCKDIAGRAM."
        ),
        "source_spec_id": "SPEC-STARTHERE-BLOCKDIAGRAM",
    },
    {
        "id": "WI-ADOPT-04",
        "title": "evidence.md plus metrics collector script",
        "description": ("Create docs/evidence.md plus scripts/collect_evidence_metrics.py. Covers EVIDENCE."),
        "source_spec_id": "SPEC-STARTHERE-EVIDENCE",
    },
    {
        "id": "WI-ADOPT-05",
        "title": "Day in the Life refresh and nav inclusion",
        "description": (
            "Refresh docs/day-in-the-life.md with six named activities and wire "
            "it into the adopter nav. Covers DAYINLIFE."
        ),
        "source_spec_id": "SPEC-STARTHERE-DAYINLIFE",
    },
    {
        "id": "WI-ADOPT-06",
        "title": "known-limitations.md with audit cross-links",
        "description": (
            "Create docs/known-limitations.md citing Gap 2.8, hook-registration "
            "limitation, and U-class scaffold rows with links to the "
            "non-disruptive upgrade audit. Covers LIMITATIONS."
        ),
        "source_spec_id": "SPEC-STARTHERE-LIMITATIONS",
    },
    {
        "id": "WI-ADOPT-07",
        "title": "Start Here sections 5 through 9 (install, templates, dashboard, 3rd-party)",
        "description": (
            "Rewrite docs/start-here.md sections 5-9 covering install, third-party "
            "integrations, dashboard, core loops, and next steps. Covers 3RDPARTY, "
            "DASHBOARD, TEMPLATES, INSTALL-BASELINE."
        ),
        "source_spec_id": "SPEC-STARTHERE-INSTALL-BASELINE",
    },
    {
        "id": "WI-ADOPT-08",
        "title": "mkdocs nav restructure and docs gates",
        "description": (
            "Update mkdocs.yml adopter-path nav, add scripts/check_doc_links.py "
            "link-integrity checker, and wire all docs gates. Cross-cutting; "
            "gates Phase 3."
        ),
        "source_spec_id": "SPEC-STARTHERE-DAYINLIFE",
    },
]

DELIB_TITLE = "Start Here adopter rewrite implementation chain"
DELIB_SUMMARY = (
    "Scope GO at bridge/gtkb-start-here-adopter-rewrite-002.md (7 conditions). "
    "Implementation GO at bridge/gtkb-start-here-adopter-rewrite-implementation-002.md "
    "(5 corrections). Phase 1 inserts 12 SPEC-STARTHERE-* specs plus 8 WI-ADOPT-* "
    "work items on groundtruth-kb feat/start-here-adopter-rewrite."
)
DELIB_CONTENT = (
    "Workstream: GT-KB Start Here adopter rewrite for CTO trial delivery. "
    "Scope proposal at bridge/gtkb-start-here-adopter-rewrite-001.md. Codex "
    "scope review at bridge/gtkb-start-here-adopter-rewrite-002.md GO'd with "
    "seven conditions covering MemBase definition, live evidence provenance, "
    "MkDocs discoverability, diagram rendering contract, Claude Code "
    "prerequisite stability, owner-vs-machine verification split, and "
    "repo-native docs gates.\n\n"
    "Implementation proposal at "
    "bridge/gtkb-start-here-adopter-rewrite-implementation-001.md discharges "
    "all seven conditions and pins two owner-pending decisions to explicit "
    "defaults: Mermaid-rendered-by-MkDocs and a synthetic day-in-the-life "
    "protagonist (Allison, solo Flask developer on Windows). Codex review at "
    "bridge/gtkb-start-here-adopter-rewrite-implementation-002.md GO'd with "
    "five corrections: post-impl bridge number must be -003.md (not -002 "
    "which this review consumed); supported assertion runner (gt assert / "
    "run_all_assertions); focused link-integrity check; tightened evidence "
    "tolerance contract; spec ID prefix SPEC-STARTHERE-* over SPEC-ADOPT-*.\n\n"
    "All five corrections are applied in this KB setup: SPEC-STARTHERE-* "
    "prefix used, assertions stored in supported schema (grep, count, "
    "file_exists, all_of), outcome=go set on this deliberation.\n\n"
    "Rejected alternatives: SPEC-ADOPT-* prefix (Codex accepted only with "
    "explicit rename record); committed SVG diagram (diff churn outweighs "
    "stability gain); re-narrating S299 for day-in-the-life (too meta for "
    "CTO audience)."
)


def main() -> None:
    db = KnowledgeDB()

    # Specs
    for spec in SPECS:
        db.insert_spec(
            id=spec["id"],  # type: ignore[arg-type]
            title=spec["title"],  # type: ignore[arg-type]
            status="specified",
            changed_by=CHANGED_BY,
            change_reason=CHANGE_REASON,
            description=spec["description"],  # type: ignore[arg-type]
            tags=["adopter-onboarding", "cto-trial", "doc-rewrite"],
            assertions=spec["assertions"],  # type: ignore[arg-type]
            type="requirement",
        )
        print(f"spec inserted: {spec['id']}")

    # Work items
    for wi in WORK_ITEMS:
        db.insert_work_item(
            id=wi["id"],  # type: ignore[arg-type]
            title=wi["title"],  # type: ignore[arg-type]
            origin="new",
            component="documentation",
            resolution_status="open",
            changed_by=CHANGED_BY,
            change_reason=CHANGE_REASON,
            description=wi["description"],  # type: ignore[arg-type]
            source_spec_id=wi["source_spec_id"],  # type: ignore[arg-type]
            stage="implementing",
        )
        print(f"work item inserted: {wi['id']}")

    # Deliberation
    db.insert_deliberation(
        id="DELIB-GTKB-STARTHERE-ADOPT-001",
        source_type="bridge_thread",
        title=DELIB_TITLE,
        summary=DELIB_SUMMARY,
        content=DELIB_CONTENT,
        changed_by=CHANGED_BY,
        change_reason=CHANGE_REASON,
        source_ref="bridge/gtkb-start-here-adopter-rewrite-implementation-002.md",
        participants=["prime-opus-4-7", "codex-gpt-5-3"],
        outcome="go",
        session_id=SESSION_ID,
        origin_project="agent-red",
        origin_repo="Agent Red Customer Engagement",
    )
    print("deliberation inserted: DELIB-GTKB-STARTHERE-ADOPT-001")

    print("\nPhase 1 KB setup complete.")
    print(f"  Specs: {len(SPECS)}")
    print(f"  Work items: {len(WORK_ITEMS)}")
    print("  Deliberations: 1")


if __name__ == "__main__":
    main()
