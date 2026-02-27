"""
Insert Phase 2 implementation-derived specifications into the Knowledge DB.

Reads JSON spec arrays from agent output files (or a combined JSON file),
assigns sequential SPEC-NNNN IDs starting from the next available,
and inserts into the specifications table.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import io
import json
import re
import sys
from pathlib import Path

# Windows encoding safety
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Add knowledge-db to path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools" / "knowledge-db"))
from db import KnowledgeDB

# --- Configuration ---
PHASE = "Phase 2"
CHANGED_BY = "Claude (S109)"
CHANGE_REASON = "Phase 2 implementation inspection: spec extracted from source code"

# Map agent prefixes to KB sections
AGENT_SECTION_MAP = {
    "P2A": "ADMIN_UI",
    "P2B": "CONFIG",
    "P2C": "WIDGET_AUTH_EMAIL",
    "P2D": "INFRASTRUCTURE",
    "P2E": "AGENTS_TESTING",
}

# More granular domain-to-section mapping
DOMAIN_SECTION_MAP = {
    # 2a domains
    "dashboard": "ADMIN_UI",
    "widget-config": "ADMIN_UI",
    "team-members": "ADMIN_UI",
    "knowledge-base": "ADMIN_UI",
    "memory-privacy": "ADMIN_UI",
    "inbox": "ADMIN_UI",
    "billing": "BILLING",
    "agent-config": "ADMIN_UI",
    "layout": "ADMIN_UI",
    "onboarding": "ADMIN_UI",
    "settings": "ADMIN_UI",
    # 2b domains
    "config-fields": "CONFIG",
    "config-api": "CONFIG",
    "config-models": "CONFIG",
    "field-mapping": "CONFIG",
    "field-validation": "CONFIG",
    "api-endpoints": "CONFIG",
    "api-versioning": "CONFIG",
    "tenant-config": "CONFIG",
    # 2c domains
    "widget": "WIDGET_UI",
    "widget-auth": "AUTH",
    "auth": "AUTH",
    "email": "EMAIL",
    "mfa": "AUTH",
    "rbac": "AUTH",
    "magic-link": "AUTH",
    # 2d domains
    "cosmos-repositories": "INFRASTRUCTURE",
    "middleware": "INFRASTRUCTURE",
    "rate-limiting": "INFRASTRUCTURE",
    "caching": "INFRASTRUCTURE",
    "health": "INFRASTRUCTURE",
    "messaging": "INFRASTRUCTURE",
    "nats": "INFRASTRUCTURE",
    # 2e domains
    "agents": "AGENTS",
    "testing": "TESTING",
    "agent-modules": "AGENTS",
    "test-infrastructure": "TESTING",
}


def extract_json_from_text(text: str) -> list[dict]:
    """Extract JSON array from agent output text.

    Handles both:
    - Clean JSON arrays
    - JSON embedded in ```json ... ``` fences
    - Multiple JSON blocks (takes the largest)
    """
    # Try fenced JSON blocks first
    fenced = re.findall(r'```json\s*\n(.*?)```', text, re.DOTALL)
    if fenced:
        # Take the largest fenced block
        largest = max(fenced, key=len)
        try:
            result = json.loads(largest)
            if isinstance(result, list):
                return result
        except json.JSONDecodeError:
            pass

    # Try to find a raw JSON array
    # Look for [...] patterns
    bracket_depth = 0
    start = None
    candidates = []
    for i, ch in enumerate(text):
        if ch == '[' and bracket_depth == 0:
            start = i
            bracket_depth = 1
        elif ch == '[':
            bracket_depth += 1
        elif ch == ']':
            bracket_depth -= 1
            if bracket_depth == 0 and start is not None:
                candidate = text[start:i+1]
                if len(candidate) > 100:  # Skip tiny arrays
                    candidates.append(candidate)
                start = None

    # Try parsing candidates, largest first
    for candidate in sorted(candidates, key=len, reverse=True):
        try:
            result = json.loads(candidate)
            if isinstance(result, list) and len(result) > 0:
                return result
        except json.JSONDecodeError:
            continue

    return []


def resolve_section(spec: dict) -> str:
    """Determine KB section from spec metadata."""
    domain = spec.get("domain", "").lower()
    if domain in DOMAIN_SECTION_MAP:
        return DOMAIN_SECTION_MAP[domain]

    # Fall back to agent prefix
    prefix = spec.get("spec_id", "")[:3]
    if prefix in AGENT_SECTION_MAP:
        return AGENT_SECTION_MAP[prefix]

    return "GENERAL"


def resolve_tags(spec: dict) -> list[str]:
    """Generate tags from spec metadata."""
    tags = ["phase-2", "implementation-derived"]
    domain = spec.get("domain", "")
    if domain:
        tags.append(domain.lower())
    source = spec.get("source_file", "")
    if source:
        # Extract meaningful path component
        parts = Path(source).parts
        if len(parts) >= 2:
            tags.append(parts[-2].lower())
    return tags


def main():
    if len(sys.argv) < 2:
        print("Usage: python insert_phase2_specs.py <file1.json> [file2.json ...]")
        print("  or:  python insert_phase2_specs.py --from-output <output_dir>")
        sys.exit(1)

    db = KnowledgeDB()

    # Find next available SPEC ID
    specs = db.list_specs()
    existing_nums = [
        int(s["id"].split("-")[1])
        for s in specs
        if s["id"].startswith("SPEC-") and s["id"].split("-")[1].isdigit()
    ]
    next_num = max(existing_nums) + 1 if existing_nums else 872

    # Collect all specs from input files
    all_specs = []
    for filepath in sys.argv[1:]:
        if filepath.startswith("--"):
            continue
        path = Path(filepath)
        if not path.exists():
            print(f"WARNING: {filepath} not found, skipping")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        extracted = extract_json_from_text(text)
        print(f"  {filepath}: {len(extracted)} specs extracted")
        all_specs.extend(extracted)

    if not all_specs:
        print("No specs found in input files.")
        sys.exit(1)

    print(f"\nTotal specs to insert: {len(all_specs)}")
    print(f"Starting from SPEC-{next_num:04d}")
    print()

    inserted = 0
    errors = []
    for spec in all_specs:
        spec_id = f"SPEC-{next_num:04d}"
        title = spec.get("title", "Untitled spec")[:200]
        description = spec.get("description", "")
        section = resolve_section(spec)
        tags = resolve_tags(spec)
        source_file = spec.get("source_file", "")
        source_line = spec.get("source_line", "")

        # Enrich description with source reference
        if source_file:
            description += f"\n\n[Source: {source_file}"
            if source_line:
                description += f":{source_line}"
            description += "]"

        try:
            db.insert_spec(
                id=spec_id,
                title=title,
                status="specified",
                changed_by=CHANGED_BY,
                change_reason=CHANGE_REASON,
                description=description,
                section=section,
                tags=tags,
            )
            inserted += 1
            next_num += 1
        except Exception as e:
            errors.append(f"{spec_id}: {e}")
            next_num += 1  # Still increment to avoid ID collision

    print(f"Inserted: {inserted}")
    print(f"Errors: {len(errors)}")
    for e in errors[:10]:
        print(f"  {e}")
    if len(errors) > 10:
        print(f"  ... and {len(errors) - 10} more")

    print()
    summary = db.get_summary()
    print(f"Knowledge DB now has {summary['spec_total']} specs")
    print(f"  SPEC-NNNN range: SPEC-0001 to SPEC-{next_num - 1:04d}")


if __name__ == "__main__":
    main()
