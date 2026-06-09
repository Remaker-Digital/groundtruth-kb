"""Cross-reference 871 extracted specs against 163 Knowledge Database entries.

For each KB entry (work item), finds which extracted specs relate to it.
Identifies specs that are not covered by any KB entry (new specifications).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import os
import sys
import re
from collections import defaultdict
from pathlib import Path

# Windows UTF-8 safety
sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", errors="replace", buffering=1)

# Per S307 hardcoded-path directive: discover repo root from script location.
# scripts/ lives at the repo root; docs/ and tools/knowledge-db are siblings.
_REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = str(_REPO_ROOT / "docs")
KB_PATH = str(_REPO_ROOT / "tools" / "knowledge-db")
MERGED_FILE = os.path.join(DOCS_DIR, "specs-merged-organized.json")
OUTPUT_FILE = os.path.join(DOCS_DIR, "specs-kb-crossref.json")


def load_merged_specs():
    """Load the merged organized specs."""
    with open(MERGED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Flatten all specs from all domains
    all_specs = []
    for domain, specs in data["domains"].items():
        for s in specs:
            s["domain"] = domain
            all_specs.append(s)
    return all_specs


def load_kb_entries():
    """Load KB entries with their titles, descriptions, and status."""
    sys.path.insert(0, KB_PATH)
    from db import KnowledgeDB

    db = KnowledgeDB()
    entries = db.list_specs()
    db.close()
    return entries


def extract_keywords(text):
    """Extract meaningful keywords from text for matching."""
    text = text.lower()
    # Remove common words
    stop_words = {
        "the",
        "a",
        "an",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "shall",
        "can",
        "must",
        "need",
        "for",
        "of",
        "in",
        "on",
        "at",
        "to",
        "from",
        "with",
        "by",
        "as",
        "or",
        "and",
        "not",
        "but",
        "if",
        "then",
        "than",
        "that",
        "this",
        "which",
        "what",
        "when",
        "where",
        "how",
        "all",
        "each",
        "every",
        "both",
        "few",
        "more",
        "most",
        "other",
        "some",
        "such",
        "no",
        "nor",
        "only",
        "own",
        "same",
        "so",
        "very",
        "just",
        "also",
        "into",
        "about",
        "up",
        "out",
        "its",
        "it",
        "implement",
        "approved",
        "implementation",
        "add",
        "update",
        "create",
        "ensure",
        "include",
        "provide",
        "support",
        "display",
        "show",
    }
    words = re.findall(r"\b[a-z][a-z0-9_-]+\b", text)
    return set(w for w in words if w not in stop_words and len(w) > 2)


def match_spec_to_kb(spec_text, kb_entries):
    """Find KB entries that relate to a given spec text."""
    spec_keywords = extract_keywords(spec_text)
    if not spec_keywords:
        return []

    matches = []
    for entry in kb_entries:
        kb_text = f"{entry.get('title', '')} {entry.get('description', '')}".lower()
        kb_keywords = extract_keywords(kb_text)

        if not kb_keywords:
            continue

        overlap = spec_keywords & kb_keywords
        # Need at least 2 shared keywords and meaningful overlap
        if len(overlap) >= 2:
            score = len(overlap) / max(len(spec_keywords), 1)
            if score >= 0.15:  # At least 15% keyword overlap
                matches.append(
                    {
                        "kb_id": entry.get("id", "?"),
                        "kb_title": entry.get("title", "?")[:100],
                        "kb_status": entry.get("status", "?"),
                        "overlap_keywords": sorted(list(overlap))[:10],
                        "score": round(score, 3),
                    }
                )

    # Sort by score descending, return top matches
    matches.sort(key=lambda x: -x["score"])
    return matches[:3]


def main():
    print("Loading merged specs...")
    all_specs = load_merged_specs()
    print(f"  {len(all_specs)} specs loaded")

    print("Loading KB entries...")
    kb_entries = load_kb_entries()
    print(f"  {len(kb_entries)} KB entries loaded")

    print("\nCross-referencing specs against KB...")
    covered = []  # Specs that map to at least one KB entry
    uncovered = []  # Specs with no KB match (new specifications)
    kb_decomposition = defaultdict(list)  # KB ID -> list of related specs

    for i, spec in enumerate(all_specs):
        if (i + 1) % 100 == 0:
            print(f"  Processing {i + 1}/{len(all_specs)}...")

        matches = match_spec_to_kb(spec["text"], kb_entries)
        if matches:
            covered.append(
                {
                    "spec_id": spec["spec_id"],
                    "text": spec["text"][:200],
                    "domain": spec["domain"],
                    "best_kb_match": matches[0],
                    "all_kb_matches": matches,
                }
            )
            for m in matches:
                kb_decomposition[m["kb_id"]].append(
                    {
                        "spec_id": spec["spec_id"],
                        "text": spec["text"][:150],
                        "score": m["score"],
                    }
                )
        else:
            uncovered.append(
                {
                    "spec_id": spec["spec_id"],
                    "text": spec["text"],
                    "domain": spec["domain"],
                    "source_type": spec["source_type"],
                }
            )

    # KB entries that have NO matching specs
    covered_kb_ids = set(kb_decomposition.keys())
    all_kb_ids = set(str(e.get("id", "?")) for e in kb_entries)
    orphan_kb = all_kb_ids - covered_kb_ids

    print(f"\n  Results:")
    print(f"    Specs with KB match: {len(covered)} ({len(covered) / len(all_specs) * 100:.1f}%)")
    print(f"    Specs with NO KB match (new): {len(uncovered)} ({len(uncovered) / len(all_specs) * 100:.1f}%)")
    print(f"    KB entries with matching specs: {len(covered_kb_ids)}/{len(all_kb_ids)}")
    print(f"    KB entries with NO matching specs: {len(orphan_kb)}")

    # Uncovered specs by domain
    uncovered_by_domain = defaultdict(int)
    for s in uncovered:
        uncovered_by_domain[s["domain"]] += 1
    print(f"\n  Uncovered specs by domain:")
    for domain, count in sorted(uncovered_by_domain.items(), key=lambda x: -x[1]):
        print(f"    {domain}: {count}")

    # KB decomposition stats
    decomp_sizes = [len(specs) for specs in kb_decomposition.values()]
    if decomp_sizes:
        print(f"\n  KB decomposition stats:")
        print(f"    KB entries decomposed: {len(decomp_sizes)}")
        print(f"    Avg specs per KB entry: {sum(decomp_sizes) / len(decomp_sizes):.1f}")
        print(f"    Max specs per KB entry: {max(decomp_sizes)}")
        print(f"    Min specs per KB entry: {min(decomp_sizes)}")

    # Build output
    output = {
        "summary": {
            "total_specs": len(all_specs),
            "specs_with_kb_match": len(covered),
            "specs_without_kb_match": len(uncovered),
            "kb_entries_with_specs": len(covered_kb_ids),
            "kb_entries_without_specs": len(orphan_kb),
            "uncovered_by_domain": dict(sorted(uncovered_by_domain.items(), key=lambda x: -x[1])),
        },
        "kb_decomposition": {
            kb_id: sorted(specs, key=lambda x: -x["score"]) for kb_id, specs in sorted(kb_decomposition.items())
        },
        "uncovered_specs": uncovered,
        "orphan_kb_entries": sorted(list(orphan_kb)),
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n  Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
