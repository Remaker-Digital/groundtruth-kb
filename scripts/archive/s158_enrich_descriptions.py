#!/usr/bin/env python3
"""
S158 Batch Description Enrichment — Generate descriptions for NULL-description specs.

Strategy:
1. For specs with assertions containing file paths, generate description from
   title + source file context
2. For specs without assertions, generate description from title alone
3. Only targets specs with titles < 100 chars (longer titles are self-describing)
4. Skips retired specs

Template: "[Title restated as a requirement]. [Source file context if available]."

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import sys
import re
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR / "tools" / "knowledge-db"))

from db import KnowledgeDB

CHANGED_BY = "S158-audit"


# Map common file paths to human-readable descriptions
FILE_CONTEXT = {
    "pyproject.toml": "project configuration",
    "conftest.py": "shared test infrastructure",
    "requirements": "dependency management",
    ".github": "CI/CD pipeline",
    "admin/standalone": "standalone admin console",
    "admin/provider": "provider (SPA) admin console",
    "admin/shopify": "Shopify embedded admin",
    "admin/shared": "shared admin components",
    "widget/": "customer-facing chat widget",
    "src/multi_tenant/middleware": "multi-tenant middleware",
    "src/multi_tenant/auth": "authentication",
    "src/multi_tenant/endpoints": "API endpoints",
    "src/multi_tenant/orchestrator": "AI pipeline orchestrator",
    "src/multi_tenant/cosmos_schema": "Cosmos DB schema",
    "src/multi_tenant/activation_service": "widget activation",
    "src/multi_tenant/mutation_executor": "configuration persistence",
    "src/multi_tenant/alert_delivery": "email/notification delivery",
    "src/multi_tenant/security": "security hardening",
    "src/multi_tenant/repository": "data access layer",
    "src/multi_tenant/cost_analytics": "cost tracking",
    "src/multi_tenant/fields.yaml": "tenant schema definitions",
    "src/app/": "application lifecycle",
    "Dockerfile": "container build",
    "scripts/": "operational scripts",
    "branding/": "brand assets",
    "docs/": "documentation",
    "CLAUDE": "project governance",
    "knowledge.db": "knowledge database",
    ".claude/hooks": "session hooks",
}


def get_source_context(assertions_json: str | None) -> str:
    """Extract source file context from assertion data."""
    if not assertions_json:
        return ""

    try:
        assertions = json.loads(assertions_json)
    except (json.JSONDecodeError, TypeError):
        return ""

    files = set()
    for a in assertions:
        f = a.get("file", "")
        if f:
            files.add(f)

    if not files:
        return ""

    # Map to human-readable context
    contexts = []
    for f in files:
        matched = False
        for path_fragment, description in FILE_CONTEXT.items():
            if path_fragment in f:
                if description not in contexts:
                    contexts.append(description)
                matched = True
                break
        if not matched:
            # Use filename as context
            basename = Path(f).stem
            readable = basename.replace("_", " ").replace("-", " ")
            if readable not in contexts:
                contexts.append(readable)

    source_files = ", ".join(sorted(files)[:2])  # Max 2 files
    context_str = " and ".join(contexts[:2]) if contexts else ""

    parts = []
    if context_str:
        parts.append(f"Part of {context_str}")
    parts.append(f"[Source: {source_files}]")
    return ". ".join(parts)


def title_to_description(title: str, source_ctx: str) -> str:
    """Convert a spec title to a meaningful description."""
    # Clean up title
    desc = title.strip()

    # Make it a complete sentence if it isn't one
    if not desc.endswith((".","!","?")):
        desc = desc + "."

    # Add source context if available
    if source_ctx:
        desc = f"{desc} {source_ctx}"

    return desc


def main():
    db_path = PROJECT_DIR / "tools" / "knowledge-db" / "knowledge.db"
    db = KnowledgeDB(str(db_path))

    try:
        conn = db._get_conn()

        # Get all NULL-description, non-retired specs with short titles
        rows = conn.execute("""
            SELECT id, title, assertions FROM current_specifications
            WHERE description IS NULL
            AND status NOT IN ('retired')
            AND LENGTH(title) < 100
            ORDER BY id
        """).fetchall()

        print(f"Found {len(rows)} short-title specs with NULL descriptions")
        print()

        count = 0
        errors = 0
        for row in rows:
            spec_id = row["id"]
            title = row["title"]
            assertions = row["assertions"]

            source_ctx = get_source_context(assertions)
            description = title_to_description(title, source_ctx)

            try:
                db.update_spec(
                    spec_id,
                    changed_by=CHANGED_BY,
                    change_reason="S158 audit: auto-generated description from title + source context",
                    description=description,
                )
                count += 1
                if count % 25 == 0:
                    print(f"  ... {count} specs enriched")
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"  ERR {spec_id}: {str(e)[:80]}")

        print(f"\nEnriched: {count} specs")
        if errors:
            print(f"Errors: {errors}")

        # Now handle long-title specs (100+ chars) — just set description = title
        rows2 = conn.execute("""
            SELECT id, title, assertions FROM current_specifications
            WHERE description IS NULL
            AND status NOT IN ('retired')
            AND LENGTH(title) >= 100
            ORDER BY id
        """).fetchall()

        print(f"\nFound {len(rows2)} long-title specs with NULL descriptions")
        count2 = 0
        for row in rows2:
            spec_id = row["id"]
            title = row["title"]
            assertions = row["assertions"]

            source_ctx = get_source_context(assertions)
            # For long titles, use the title as-is (it's already descriptive)
            description = title.strip()
            if source_ctx:
                description = f"{description}. {source_ctx}"

            try:
                db.update_spec(
                    spec_id,
                    changed_by=CHANGED_BY,
                    change_reason="S158 audit: description from title (self-describing)",
                    description=description,
                )
                count2 += 1
                if count2 % 50 == 0:
                    print(f"  ... {count2} specs enriched")
            except Exception as e:
                errors += 1

        print(f"Enriched: {count2} long-title specs")

        # Final count
        remaining = conn.execute("""
            SELECT COUNT(*) FROM current_specifications
            WHERE description IS NULL AND status NOT IN ('retired')
        """).fetchone()[0]
        print(f"\nRemaining NULL descriptions: {remaining}")
        print(f"Total enriched: {count + count2}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
