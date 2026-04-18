# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Record the 13 canonical-terminology specs into the GT-KB MemBase.

Ephemeral one-time seed script used by the canonical-terminology-surface bridge.
After Phase 1 verification, this script can be safely deleted.
"""

from __future__ import annotations

from pathlib import Path

from groundtruth_kb.db import KnowledgeDB

SPECS: list[dict[str, object]] = [
    {
        "id": "SPEC-TERMINOLOGY-RECORD",
        "title": "Canonical terminology record set MUST live in GT-KB MemBase as governed document artifact",
        "description": (
            "A canonical terminology record set MUST live in MemBase as a governed "
            "document artifact with append-only versioning. The record anchors the "
            "project's vocabulary and is referenced by the scaffold templates, the "
            "doctor check, and the bridge review gate."
        ),
    },
    {
        "id": "SPEC-TERMINOLOGY-MINIMUM-SET",
        "title": "Canonical terminology MUST define the owner-listed 8 terms plus MEMBASE-4-CLAUDE.md glossary",
        "description": (
            "The record MUST define at minimum the 8 owner-listed terms (MemBase, "
            "Deliberation Archive, MEMORY.md, Knowledge Database, GroundTruth KB, "
            "GT-KB, Prime Builder, Loyal Opposition) and the full MEMBASE-4-CLAUDE.md "
            "glossary content."
        ),
    },
    {
        "id": "SPEC-TERMINOLOGY-STARTUP-VISIBLE",
        "title": "CLAUDE.md and AGENTS.md MUST contain startup-visible glossary block or pointer",
        "description": (
            "CLAUDE.md (Prime auto-load) and AGENTS.md (Codex auto-load) MUST contain "
            "a startup-visible glossary block or explicit pointer loaded by default at "
            "session start, so a fresh agent session immediately knows the canonical "
            "vocabulary without cross-referencing."
        ),
        "assertions": [
            {
                "id": "ASSERT-TERMINOLOGY-CLAUDE-MD-MEMBASE",
                "kind": "grep",
                "description": "CLAUDE.md MUST mention MemBase at least once",
                "args": {
                    "path": "CLAUDE.md",
                    "pattern": "MemBase",
                    "min_matches": 1,
                },
            }
        ],
    },
    {
        "id": "SPEC-TERMINOLOGY-TEMPLATE-INHERITANCE",
        "title": "GT-KB scaffold templates MUST produce projects with terminology block present by default",
        "description": (
            "GT-KB scaffold templates MUST produce projects where the canonical "
            "terminology block is present by default on `gt project init`. This "
            "applies to all scaffold profiles (local-only, dual-agent, "
            "dual-agent-webapp)."
        ),
    },
    {
        "id": "SPEC-TERMINOLOGY-DOCTOR-CHECK",
        "title": "gt project doctor MUST flag missing/inconsistent terminology across profile-required files",
        "description": (
            "`gt project doctor` MUST flag missing or inconsistent terminology across "
            "CLAUDE.md, AGENTS.md, MEMORY.md, docs, and templates, referenced against "
            "ADR-0001. Severity: ERROR for missing canonical terms, WARN for minor "
            "drift (per DELIB-0719)."
        ),
    },
    {
        "id": "SPEC-TERMINOLOGY-BRIDGE-GATE",
        "title": "Bridge review gate MUST require propagation targets for new canonical terms",
        "description": (
            "The bridge review gate MUST require any bridge proposal that introduces "
            "a NEW canonical term to list propagation targets (MemBase record, "
            "CLAUDE.md glossary, template, doctor check) before Codex issues GO. "
            "Prevents canonical-term drift between documentation and operational "
            "surface."
        ),
    },
    {
        "id": "SPEC-TERMINOLOGY-ASSERTION",
        "title": "A machine-verifiable assertion MUST exist on startup-visible terminology",
        "description": (
            "A machine-verifiable assertion MUST exist on SPEC-TERMINOLOGY-STARTUP-VISIBLE, "
            "e.g., `grep 'MemBase' CLAUDE.md` returns >=1 match. Runs at session start "
            "via the existing assertion-check hook to detect regressions automatically."
        ),
    },
    {
        "id": "SPEC-TERMINOLOGY-PROFILE-MATRIX",
        "title": "Doctor terminology check MUST respect profile-specific required-term matrix",
        "description": (
            "The doctor terminology check MUST respect a profile-specific matrix of "
            "required startup terms: local-only requires {MemBase, Deliberation Archive, "
            "MEMORY.md}; dual-agent and dual-agent-webapp require those plus "
            "{Prime Builder, Loyal Opposition}; harness-memory (Agent Red opt-in) skips "
            "the MEMORY.md content check."
        ),
    },
    {
        "id": "SPEC-TERMINOLOGY-CONFIG-TOML",
        "title": "Canonical terminology config MUST be profile-aware TOML scaffolded to .claude/rules/",
        "description": (
            "A profile-aware TOML config file "
            "(`.claude/rules/canonical-terminology.toml`) MUST be scaffolded into new "
            "projects, driving the doctor check and allowing project-specific overrides. "
            "Must support the 4 profiles: local-only, dual-agent, dual-agent-webapp, "
            "harness-memory."
        ),
    },
    {
        "id": "SPEC-TERMINOLOGY-UPGRADE",
        "title": "gt project upgrade MUST idempotently add canonical-terminology files to existing projects",
        "description": (
            "`gt project upgrade` MUST idempotently add the two new canonical-"
            "terminology files (`.claude/rules/canonical-terminology.md` and "
            "`.claude/rules/canonical-terminology.toml`) to existing scaffolded projects "
            "without overwriting any customization. Uses the existing "
            "`_plan_missing_managed_files` repair path driven by the managed-artifact "
            "registry."
        ),
    },
    {
        "id": "SPEC-TERMINOLOGY-DOCS-REFERENCE",
        "title": "Published reference documentation MUST exist at docs/reference/canonical-terminology.md",
        "description": (
            "A published reference page (`docs/reference/canonical-terminology.md`) "
            "MUST exist with the full glossary in Mermaid-only diagram style (per "
            "DELIB-0719). Integrated into the mkdocs Reference nav section. Template "
            "inventory docs (`docs/reference/templates.md` and `templates/README.md`) "
            "MUST list the two new canonical-terminology template files."
        ),
    },
    {
        "id": "SPEC-TERMINOLOGY-AGENTS-MD-PATH",
        "title": "Generated AGENTS.md MUST name root MEMORY.md, not memory/MEMORY.md",
        "description": (
            "The scaffolded `AGENTS.md` startup checklist MUST name root `MEMORY.md` "
            "(not `memory/MEMORY.md`) to match the scaffold contract. Current "
            "templates/project/AGENTS.md:67-70 has the bug and MUST be fixed during "
            "this work. P1-1 condition from Codex GO at "
            "bridge/gtkb-canonical-terminology-surface-implementation-006.md."
        ),
    },
    {
        "id": "SPEC-TERMINOLOGY-ALIAS-CLARITY",
        "title": "Canonical terminology MUST explicitly mark aliases vs canonical forms",
        "description": (
            "The canonical-terminology record MUST explicitly mark aliases (e.g., "
            "'GT-KB' is an alias for 'GroundTruth KB') via a disposition table. "
            "Aliases resolve to canonical forms. Prevents silent drift where an alias "
            "and its canonical form acquire divergent definitions over time."
        ),
    },
]


def main() -> int:
    db_path = Path(__file__).resolve().parent.parent / "groundtruth.db"
    db = KnowledgeDB(db_path)
    try:
        inserted = 0
        skipped = 0
        for spec in SPECS:
            existing = db.get_spec(spec["id"])  # type: ignore[arg-type]
            if existing is not None:
                print(f"SKIP {spec['id']} — already exists (version {existing['version']})")
                skipped += 1
                continue
            db.insert_spec(
                id=spec["id"],  # type: ignore[arg-type]
                title=spec["title"],  # type: ignore[arg-type]
                status="specified",
                changed_by="prime-builder",
                change_reason=(
                    "Canonical terminology surface — recorded per bridge GO at "
                    "bridge/gtkb-canonical-terminology-surface-implementation-006.md"
                ),
                description=spec.get("description"),  # type: ignore[arg-type]
                tags=["adopter-onboarding", "cto-trial", "canonical-terminology"],
                assertions=spec.get("assertions"),  # type: ignore[arg-type]
            )
            print(f"INSERT {spec['id']}")
            inserted += 1
        print(f"\nTotal inserted: {inserted}, skipped: {skipped}")
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
