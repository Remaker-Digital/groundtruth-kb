"""Manifest-driven baseline neutralization executor (Phase A, slice 1).

Landed by bridge/gtkb-baseline-correction-and-goose-projector-slice-1 (GO at
-004) under implementation-start packet authority. Reads the classification
manifest produced by the 14-agent verification workflow plus the owner-ratified
lens-reconciliation decisions, and applies the MECHANICAL categories to the
neutral baseline:

- TOKENIZE_PATH / SHARED_HELPER_PATH / NEUTRALIZE_PROSE occurrences whose
  manifest entry carries an exact replacement string, applied only when the
  current line still matches the recorded snippet (drift-safe; mismatches are
  logged, never guessed).
- DELETE_LINE occurrences, with the lens-mandated block extension for the
  bridge-axis-2-surface legacy fallback (G5).
- RENAME_NEUTRALIZE files under the G1 canonical rename map, including
  intra-baseline reference rewrites.

Deliberately NOT handled here (handcraft or later phase): WHOLESALE_RELOCATE
(A1 split, MemBase relocations), STRUCTURAL_CONVERT (settings.json ->
hooks/manifest.toml), RELOCATE_SNIPPET (needs per-snippet MemBase targets,
G4), and the A5-deferred formal artifacts.

Every action is appended to an execution log (JSONL) for the implementation
report; the run is idempotent (a second run finds nothing left to apply).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASELINE = PROJECT_ROOT / ".harness-baseline-configuration"
MANIFEST = PROJECT_ROOT / ".gtkb-state" / "baseline-neutralization" / "classification-20260813.json"
LOG_PATH = PROJECT_ROOT / ".gtkb-state" / "baseline-neutralization" / "execution-log.jsonl"

# G1 canonical rename map (lens-reconciliation decisions 2026-08-14).
RENAME_MAP = {
    "rules/codex-knowledge-base-index.md": "rules/loyal-opposition-knowledge-base-index.md",
    "rules/codex-loyal-opposition-runbook.md": "rules/loyal-opposition-runbook.md",
    "rules/codex-review-checklists.md": "rules/loyal-opposition-review-checklists.md",
    "rules/codex-review-gate.md": "rules/counterpart-review-gate.md",
    "rules/codex-review-operating-contract.md": "rules/review-operating-contract.md",
    "rules/codex-session-bootstrap.md": "rules/session-bootstrap.md",
    "rules/codex-standing-priorities.md": "rules/standing-priorities.md",
    "rules/codex-way-of-working.md": "rules/way-of-working.md",
    "hooks/directive-enforcement-claude-adapter.py": "hooks/directive-enforcement-adapter.py",
}

MECHANICAL_CATEGORIES = {"TOKENIZE_PATH", "SHARED_HELPER_PATH", "NEUTRALIZE_PROSE", "DELETE_LINE"}

# G5: single-line delete that must take its whole block (file -> line -> range).
BLOCK_DELETES = {("hooks/bridge-axis-2-surface.py", 122): (120, 124)}


@dataclass
class Stats:
    applied: int = 0
    deleted: int = 0
    renamed: int = 0
    refs_rewritten: int = 0
    snippet_mismatch: int = 0
    already_applied: int = 0
    skipped_category: int = 0
    log: list[dict] = field(default_factory=list)


def _norm(text: str) -> str:
    return unicodedata.normalize("NFKC", text).strip()


def _snippet_matches(line: str, snippet: str) -> bool:
    if not snippet:
        return True
    a, b = _norm(line), _norm(snippet)
    return b in a or a in b or a[:60] == b[:60]


def apply_occurrences(stats: Stats, dry_run: bool) -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for entry in data["files"]:
        rel = entry["path"].replace("\\", "/")
        if entry.get("disposition") not in {"EDIT", "RENAME_NEUTRALIZE"}:
            continue
        path = BASELINE / rel
        if not path.is_file():
            stats.log.append({"action": "missing_file", "path": rel})
            continue
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        occurrences = sorted(
            (o for o in entry.get("occurrences") or [] if o.get("category") in MECHANICAL_CATEGORIES),
            key=lambda o: o.get("line", 0),
            reverse=True,
        )
        changed = False
        pending_block_deletes: list[tuple[int, int]] = []
        for occ in occurrences:
            cat, line_no = occ["category"], occ.get("line", 0)
            idx = line_no - 1
            if idx < 0 or idx >= len(lines):
                stats.log.append({"action": "line_out_of_range", "path": rel, "line": line_no})
                continue
            if cat == "DELETE_LINE":
                rng = BLOCK_DELETES.get((rel, line_no))
                pending_block_deletes.append(rng if rng else (line_no, line_no))
                continue
            replacement = occ.get("replacement") or ""
            if not replacement:
                stats.skipped_category += 1
                stats.log.append({"action": "no_replacement", "path": rel, "line": line_no, "category": cat})
                continue
            current = lines[idx].rstrip("\r\n")
            if _norm(current) == _norm(replacement):
                stats.already_applied += 1
                continue
            if not _snippet_matches(current, occ.get("snippet") or ""):
                stats.snippet_mismatch += 1
                stats.log.append(
                    {
                        "action": "snippet_mismatch",
                        "path": rel,
                        "line": line_no,
                        "expected": (occ.get("snippet") or "")[:120],
                        "found": current[:120],
                    }
                )
                continue
            eol = "\r\n" if lines[idx].endswith("\r\n") else "\n"
            lines[idx] = replacement.rstrip("\r\n") + eol
            stats.applied += 1
            stats.log.append({"action": "replace", "path": rel, "line": line_no, "category": cat})
            changed = True
        for start, end in sorted(pending_block_deletes, reverse=True):
            del lines[start - 1 : end]
            stats.deleted += end - start + 1
            stats.log.append({"action": "delete_lines", "path": rel, "from": start, "to": end})
            changed = True
        if changed and not dry_run:
            path.write_text("".join(lines), encoding="utf-8")


def apply_renames(stats: Stats, dry_run: bool) -> None:
    for old_rel, new_rel in RENAME_MAP.items():
        old_path, new_path = BASELINE / old_rel, BASELINE / new_rel
        if not old_path.is_file():
            if new_path.is_file():
                stats.log.append({"action": "rename_already_done", "path": old_rel})
            continue
        if not dry_run:
            new_path.parent.mkdir(parents=True, exist_ok=True)
            old_path.rename(new_path)
        stats.renamed += 1
        stats.log.append({"action": "rename", "from": old_rel, "to": new_rel})
    # Rewrite intra-baseline references to renamed basenames.
    basename_map = {Path(o).name: Path(n).name for o, n in RENAME_MAP.items()}
    pattern = re.compile("|".join(re.escape(k) for k in sorted(basename_map, key=len, reverse=True)))
    for path in BASELINE.rglob("*"):
        if not path.is_file() or path.suffix not in {".md", ".py", ".toml", ".json"}:
            continue
        text = path.read_text(encoding="utf-8", errors="surrogateescape")
        new_text, count = pattern.subn(lambda m: basename_map[m.group(0)], text)
        if count:
            if not dry_run:
                path.write_text(new_text, encoding="utf-8", errors="surrogateescape")
            stats.refs_rewritten += count
            stats.log.append({"action": "refs_rewritten", "path": str(path.relative_to(BASELINE)), "count": count})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if not MANIFEST.is_file():
        print(f"manifest missing: {MANIFEST}", file=sys.stderr)
        return 2
    stats = Stats()
    apply_occurrences(stats, args.dry_run)
    apply_renames(stats, args.dry_run)
    if not args.dry_run:
        with LOG_PATH.open("a", encoding="utf-8") as fh:
            for row in stats.log:
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(
        json.dumps(
            {
                "dry_run": args.dry_run,
                "replacements_applied": stats.applied,
                "lines_deleted": stats.deleted,
                "files_renamed": stats.renamed,
                "intra_baseline_refs_rewritten": stats.refs_rewritten,
                "snippet_mismatches_logged": stats.snippet_mismatch,
                "already_applied": stats.already_applied,
                "skipped_no_replacement": stats.skipped_category,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
