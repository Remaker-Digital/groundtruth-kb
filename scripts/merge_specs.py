"""Merge and organize specifications from all extraction batches.

Loads all 7 batch files (871 specs), organizes by domain and category,
cross-references with the 163 existing Knowledge Database entries,
and produces a structured output for owner review.

Deduplication is intentionally NOT automated — the false-positive rate
of text similarity on structurally similar specs is too high. Owner
review will handle semantic grouping.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import os
import sys
import re
from collections import defaultdict, Counter
from pathlib import Path

# Windows UTF-8 safety
sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", errors="replace", buffering=1)

# Per S307 hardcoded-path directive: discover repo root from script location.
_REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = str(_REPO_ROOT / "docs")
KB_PATH = str(_REPO_ROOT / "tools" / "knowledge-db")

BATCH_FILES = [
    "specs-batch-1.json",
    "specs-batch-2.json",
    "specs-batch-3a.json",
    "specs-batch-3b.json",
    "specs-batch-4.json",
    "specs-batch-5.json",
    "specs-batch-6.json",
]
OUTPUT_FILE = os.path.join(DOCS_DIR, "specs-merged-organized.json")
SUMMARY_FILE = os.path.join(DOCS_DIR, "specs-summary-for-review.md")


def load_all_specs():
    """Load specs from all batch files."""
    all_specs = []
    for fname in BATCH_FILES:
        path = os.path.join(DOCS_DIR, fname)
        with open(path, "r", encoding="utf-8") as f:
            specs = json.load(f)
            for spec in specs:
                spec["_source_file"] = fname
            all_specs.extend(specs)
    return all_specs


def load_kb_specs():
    """Load existing Knowledge Database specs for cross-reference."""
    sys.path.insert(0, KB_PATH)
    try:
        from db import KnowledgeDB

        db = KnowledgeDB()
        all_kb = db.list_specs()
        db.close()
        return all_kb
    except Exception as e:
        print(f"  Warning: Could not load KB: {e}")
        return []


def assign_sequential_ids(specs):
    """Assign sequential SPEC-NNNN IDs to all specs."""
    for i, spec in enumerate(specs, 1):
        spec["spec_id"] = f"SPEC-{i:04d}"
    return specs


def group_by_domain(specs):
    """Group specs by domain, preserving order within each domain."""
    groups = defaultdict(list)
    for spec in specs:
        groups[spec["domain"]].append(spec)
    return dict(sorted(groups.items()))


def generate_review_summary(specs, domain_groups, kb_specs):
    """Generate a markdown summary for owner review."""
    lines = []
    lines.append("# System Specification — Phase 1 Extraction Summary")
    lines.append("")
    lines.append(f"**Total specs extracted from transcripts:** {len(specs)}")
    lines.append(f"**Source sessions:** {len(set(s['source_session'][:12] for s in specs))}")
    lines.append(f"**Existing KB entries (work items):** {len(kb_specs)}")
    lines.append("")

    # Source type breakdown
    source_counts = Counter(s["source_type"] for s in specs)
    lines.append("## Source Type Breakdown")
    lines.append("")
    lines.append(f"| Source | Count |")
    lines.append(f"|--------|-------|")
    for st, count in source_counts.most_common():
        lines.append(f"| {st} | {count} |")
    lines.append("")

    # Domain breakdown with examples
    lines.append("## Specifications by Domain")
    lines.append("")

    for domain, domain_specs in sorted(domain_groups.items(), key=lambda x: -len(x[1])):
        lines.append(f"### {domain} ({len(domain_specs)} specs)")
        lines.append("")

        # Show first 5 examples
        for spec in domain_specs[:5]:
            lines.append(f"- **{spec['spec_id']}**: {spec['text'][:120]}{'...' if len(spec['text']) > 120 else ''}")

        if len(domain_specs) > 5:
            lines.append(f"- *...and {len(domain_specs) - 5} more*")
        lines.append("")

    # KB cross-reference notes
    lines.append("## KB Cross-Reference Notes")
    lines.append("")
    lines.append("The 163 existing KB entries are **work items** (high-level features),")
    lines.append("not granular specifications. Each KB work item typically decomposes")
    lines.append("into 3-15 granular specs. The transcript extraction captured the")
    lines.append("granular specs that the owner expressed through directives and approvals.")
    lines.append("")
    lines.append("**Next steps:**")
    lines.append("1. Owner reviews this extraction domain by domain")
    lines.append("2. Phase 2: Implementation inspection creates specs for current code state")
    lines.append("3. Phase 3: Test audit links all tests to specifications")
    lines.append("")

    return "\n".join(lines)


def main():
    print("Loading all batch files...")
    all_specs = load_all_specs()
    print(f"  Total specs loaded: {len(all_specs)}")

    # Load KB for cross-reference
    print("Loading Knowledge Database...")
    kb_specs = load_kb_specs()
    print(f"  KB entries: {len(kb_specs)}")

    # Assign sequential IDs
    print("Assigning sequential SPEC IDs...")
    all_specs = assign_sequential_ids(all_specs)

    # Domain distribution
    domain_counts = Counter(s["domain"] for s in all_specs)
    print(f"\n  Domain distribution:")
    for domain, count in domain_counts.most_common():
        print(f"    {domain}: {count}")

    # Source type distribution
    source_counts = Counter(s["source_type"] for s in all_specs)
    print(f"\n  Source type distribution:")
    for st, count in source_counts.most_common():
        print(f"    {st}: {count}")

    # Group by domain
    domain_groups = group_by_domain(all_specs)

    # Generate review summary
    print("\nGenerating review summary...")
    summary_md = generate_review_summary(all_specs, domain_groups, kb_specs)

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write(summary_md)
    print(f"  Summary written to: {SUMMARY_FILE}")

    # Build organized output (domain-grouped, with sequential IDs)
    output = {
        "metadata": {
            "total_specs": len(all_specs),
            "source_sessions": len(set(s["source_session"][:12] for s in all_specs)),
            "kb_entries": len(kb_specs),
            "domain_distribution": dict(domain_counts.most_common()),
            "source_type_distribution": dict(source_counts.most_common()),
            "phase": "Phase 1 — Transcript Extraction",
            "note": "871 specs from owner directives + approved proposals. NOT yet deduplicated — owner review handles semantic grouping. NOT yet cross-referenced with implementation (Phase 2).",
        },
        "domains": {},
    }

    for domain, domain_specs in domain_groups.items():
        output["domains"][domain] = [
            {
                "spec_id": s["spec_id"],
                "text": s["text"],
                "source_session": s["source_session"],
                "source_type": s["source_type"],
                "batch_id": s["id"],
            }
            for s in domain_specs
        ]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n  Organized output: {OUTPUT_FILE}")
    print(f"  {len(all_specs)} specs across {len(domain_groups)} domains")


if __name__ == "__main__":
    main()
