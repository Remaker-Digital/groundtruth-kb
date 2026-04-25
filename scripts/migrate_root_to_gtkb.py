#!/usr/bin/env python3
"""GT-KB root directory migration: Claude-Playground -> GT-KB.

This script is a teaching-grade reference for one-shot path-literal migrations
in a GroundTruth-KB-style repository. Read it as a worked example of:

  * deterministic find/replace with an explicit exclusion policy,
  * mechanical safety belts that prevent accidental source-tree corruption,
  * self-protection (the script must never rewrite its own REPLACEMENTS table),
  * scope scoping by owner directive (active operational code is out of scope
    for literal substitution; that work happens via per-file refactor — see
    `bridge/gtkb-root-directory-migration-post-verify-008.md` and the S307
    hardcoded-path directive at
    `independent-progress-assessments/CODEX-INSIGHT-DROPBOX/INSIGHTS-2026-04-24-20-35-HARDCODED-PATH-DIRECTIVE.md`).

Three modes:

    --dry-run   Walk repo, identify candidate replacements, write a stable
                report at scripts/migration-dryrun-report.txt. No mutations.
                Use this to bound the scope of any subsequent --execute.
    --execute   Walk repo and apply replacements. Mutates working tree.
                Per the S307 hardcoded-path directive, this mode is appropriate
                only for narrative documentation surfaces (Cat 5). Active
                operational code (Cat 1) must be refactored to use discovered
                or environment-supplied paths, never one-literal-for-another.
    --verify    Walk repo and report:
                  Section A (BLOCKER): residual REPLACEMENTS patterns.
                    Nonzero count -> exit code 1. Used as a CI / pre-merge
                    regression gate to catch new operational hits in PRs.
                  Section B (AUDIT): bare ambiguous tokens for human review.
                    Reported informationally only.

Safety belt:
    safety_check() refuses to run from any path matching SOURCE_PATH_MARKERS.
    This makes accidental source corruption mechanically impossible: even if
    someone clones the old tree at `E:\\Claude-Playground\\...` and tries to
    run --execute there, the script aborts with exit code 2 before walking.

Self-protection:
    EXCLUDE_GLOBS contains "scripts/migrate_root_to_gtkb.py" and
    "scripts/_migration_simulate.py". This is essential because the script's
    REPLACEMENTS table contains the source-path patterns it is built to
    detect; without self-exclusion, an --execute pass would rewrite those
    patterns and silently destroy the verifier's audit/re-run capability.

Why a custom is_excluded() instead of pathspec/gitignore?
    The match semantics here are simpler than gitignore (we don't need
    negation, complex globbing, or .gitignore-relative reroots), and a
    dependency on `pathspec` would couple the migration tool to a package
    install path that itself violates the no-hardcoded-paths principle in a
    bootstrap setting. The matcher uses only `fnmatch` from the standard
    library and a small prefix-startswith convention for `**` patterns.
    Note: the matcher's prefix branch is literal (no `*` expansion in the
    prefix) — see `bridge/gtkb-root-directory-migration-014.md` for the
    discovery and the exact-rooted glob convention.

Per bridge thread `gtkb-root-directory-migration-{001..016}` and follow-up
post-verify thread `gtkb-root-directory-migration-post-verify-{001..009}`.
GO conditions in `bridge/gtkb-root-directory-migration-post-verify-009.md`.

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import argparse
import fnmatch
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Order matters: more-specific patterns first.
# Path-form variants seen in this repo's tracked files:
#   {uppercase, lowercase} drive
#   X {backslash, forward-slash, JSON-escaped, double-slash-prefix}
# Plus the Claude auto-memory mangled form.
# RESTORATION NOTE (post-verify-008 Phase 0): the REPLACEMENTS table below
# was found corrupted at session start — every find-string had been overwritten
# with its replace-value (a no-op table that detected nothing). Root cause:
# the script lacked self-protection; an earlier --execute pass had rewritten
# its own REPLACEMENTS source. Self-protection is now in EXCLUDE_GLOBS below.
# The values below are restored to the canonical mapping per parent thread
# `-005` (the original migration script proposal).
REPLACEMENTS: list[tuple[str, str]] = [
    # --- Uppercase drive E: ---
    (r"E:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement",
     r"E:\GT-KB"),
    ("E:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement",
     "E:/GT-KB"),
    (r"E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement",
     r"E:\\GT-KB"),
    # --- Lowercase drive e: (per -002 F2a) ---
    (r"e:\Claude-Playground\CLAUDE-PROJECTS\Agent Red Customer Engagement",
     r"e:\GT-KB"),
    ("e:/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement",
     "e:/GT-KB"),
    (r"e:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement",
     r"e:\\GT-KB"),
    # --- Double-slash-prefix form (per -004 F2) ---
    # Claude permissions in .claude/settings.local.json use //e/... to express
    # absolute paths.
    ("//E/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement",
     "//E/GT-KB"),
    ("//e/Claude-Playground/CLAUDE-PROJECTS/Agent Red Customer Engagement",
     "//e/GT-KB"),
    # --- Claude auto-memory mangled form ---
    ("E--Claude-Playground-CLAUDE-PROJECTS-Agent-Red-Customer-Engagement",
     "E--GT-KB"),
]

# Patterns surfaced by --verify Section B for human audit only. These bare
# ambiguous tokens may legitimately appear in narrative text (e.g., discussing
# the prior naming, product references) but may also indicate path-fragment
# leftovers REPLACEMENTS missed. Do NOT cause --verify to fail.
AUDIT_PATTERNS: list[str] = [
    "Claude-Playground",
    "Agent Red Customer Engagement",
]

# Source-pattern markers for safety belt: refuse to run if REPO_ROOT contains
# any of these strings. Mechanical guarantee against accidental source-tree
# corruption.
SOURCE_PATH_MARKERS: list[str] = [
    "Claude-Playground",
]

# Files NOT processed.
EXCLUDE_GLOBS: list[str] = [
    # Audit trail - bridge protocol forbids modifying historical bridge files
    "bridge/*.md",
    # Owner message archives (historical)
    "docs/owner-messages*.json",
    "docs/owner-messages*.txt",
    # Historical extraction snapshots
    "docs/system-specification-*.json",
    # Session archives
    "CLAUDE_ARCHIVE.md",
    "memory/s*-handoff.md",
    # Archived docs
    "docs/archive/**",
    # Historical LO reports
    "independent-progress-assessments/CODEX-INSIGHT-DROPBOX/**",
    "independent-progress-assessments/LOYAL-OPPOSITION-LOG.md",
    # Git internals
    ".git/**",
    # Binary embeddings
    ".groundtruth-chroma/**",
    # Generated/vendor
    "node_modules/**",
    ".venv/**",
    "venv/**",
    "**/__pycache__/**",
    ".pytest_cache/**",
    # Generated test/type-check caches (per -002 F3)
    ".hypothesis/**",
    ".mypy_cache/**",
    ".ruff_cache/**",
    # Build/dist
    "dist/**",
    "build/**",
    ".next/**",
    # NEW per -004 F3: historical/generated copies outside active surface
    ".claude/worktrees/**",            # embedded git worktrees with own copies
    "scripts/archive/**",              # historical handoff/migration scripts
    "scripts/pre-flight-results/**",   # generated pre-flight check output
    ".claude/hooks/.codex-bridge-*.json",  # auto-generated bridge state
    # NEW per -014 F1: runtime/log surfaces that mutate during scans.
    # Exact rooted paths only (per -014 F2: avoid interior-** under the
    # current is_excluded engine).
    "logs/**",                                                  # top-level runtime logs
    "independent-progress-assessments/bridge-automation/logs/**",  # bridge poller logs
    # Recursive-copy artifact under bridge-automation (a sub-tree mirror of
    # the same logs path, observed in the -013 dry-run).
    "independent-progress-assessments/bridge-automation/independent-progress-assessments/**",
    "memory/grafana/logs/**",                                   # grafana runtime logs
    "tools/grafana/grafana-13.0.1/data/log/**",                 # bundled grafana log subtree
    "widget/node_modules/**",                                   # nested storybook cache
    "docs-site/.docusaurus/**",                                 # docusaurus build cache
    ".claude/_drift-backup-2026-04-23-S304/**",                 # S304 incident-recovery snapshot
    ".claude/hooks/.codex-bridge-*.log",                        # bridge worker log (companion to .json above)
    ".claude/hooks/.prime-bridge-*",                            # prime-bridge runtime cache (logs + state)
    "scripts/migration-dryrun-report.txt",                      # this script's own output (self-reflexive)
    # NEW per post-verify-008 (Phase 0): self-protection. Without these, the
    # script would rewrite its own REPLACEMENTS table during --execute and
    # silently destroy the verifier's audit/re-run mechanism. See module
    # docstring "Self-protection" section for the rationale.
    "scripts/migrate_root_to_gtkb.py",
    "scripts/_migration_simulate.py",
    # NEW per post-verify-006 owner Decision #5 (archive scope). One-shot
    # session utilities are moved to per-area `archive/` directories; the
    # verifier should not flag them as residuals.
    "independent-progress-assessments/archive/**",
]

# Binary file extensions to never process.
BINARY_EXTENSIONS: set[str] = {
    ".db", ".sqlite", ".sqlite3", ".sqlite-shm", ".sqlite-wal",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".webp",
    ".pdf", ".zip", ".tar", ".gz", ".7z",
    ".exe", ".dll", ".so", ".dylib",
    ".pyc", ".pyo",
    ".ttf", ".otf", ".woff", ".woff2",
    ".mp3", ".mp4", ".wav", ".ogg",
    ".whl", ".egg",
}


def safety_check() -> None:
    """Refuse to run if invoked from a source-marker path.

    Makes accidental source corruption mechanically impossible.
    """
    repo_root_str = str(REPO_ROOT)
    for marker in SOURCE_PATH_MARKERS:
        if marker in repo_root_str:
            print("REFUSING TO RUN", file=sys.stderr)
            print(f"  Script invoked from: {repo_root_str}", file=sys.stderr)
            print(f"  Path contains source marker: '{marker}'",
                  file=sys.stderr)
            print("  This script must run from the destination tree "
                  "(e.g. E:\\GT-KB\\).", file=sys.stderr)
            print("  If this is intentional, edit SOURCE_PATH_MARKERS "
                  "in the script.", file=sys.stderr)
            sys.exit(2)


def is_excluded(rel_path: Path) -> bool:
    """Return True if a relative path matches any exclusion glob."""
    posix_str = rel_path.as_posix()
    for glob in EXCLUDE_GLOBS:
        if "**" in glob:
            prefix = glob.split("**")[0].rstrip("/")
            if prefix and posix_str.startswith(prefix):
                return True
            continue
        if fnmatch.fnmatch(posix_str, glob):
            return True
        if "/" not in glob and fnmatch.fnmatch(rel_path.name, glob):
            return True
    return False


def is_binary(path: Path) -> bool:
    """Heuristic binary detection: extension match or null-byte sniff."""
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return True
    try:
        with path.open("rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return True
    except OSError:
        return True
    return False


def apply_replacements(content: str) -> tuple[str, dict[str, int]]:
    """Apply all replacements; return new content + per-pattern counts."""
    counts: dict[str, int] = {}
    for find, replace in REPLACEMENTS:
        n = content.count(find)
        if n > 0:
            content = content.replace(find, replace)
            counts[find] = n
    return content, counts


def walk_repo() -> list[Path]:
    """Yield relative paths of files candidate for processing."""
    candidates: list[Path] = []
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(REPO_ROOT)
        if is_excluded(rel):
            continue
        if is_binary(path):
            continue
        candidates.append(rel)
    return candidates


def cmd_dry_run() -> int:
    """Preview mode: walk, identify changes, write report. No mutations."""
    candidates = walk_repo()
    print(f"Scanning {len(candidates)} candidate files...", file=sys.stderr)

    report_lines: list[str] = []
    report_lines.append("# Migration dry-run report")
    report_lines.append("")
    report_lines.append(f"Scanned: {len(candidates)} files")
    report_lines.append("")

    total_changes = 0
    files_with_changes = 0
    pattern_totals: dict[str, int] = {find: 0 for find, _ in REPLACEMENTS}

    for rel in sorted(candidates):
        path = REPO_ROOT / rel
        try:
            content = path.read_text(encoding="utf-8",
                                     errors="surrogateescape")
        except OSError as e:
            report_lines.append(f"SKIP (read failed): {rel.as_posix()}: {e}")
            continue

        new_content, counts = apply_replacements(content)
        if new_content == content:
            continue

        files_with_changes += 1
        file_total = sum(counts.values())
        total_changes += file_total
        for k, v in counts.items():
            pattern_totals[k] = pattern_totals.get(k, 0) + v

        report_lines.append(f"## {rel.as_posix()}")
        report_lines.append(f"  Total replacements: {file_total}")
        for find, n in counts.items():
            replace = next(r for f, r in REPLACEMENTS if f == find)
            report_lines.append(f"    {n}x  '{find}' -> '{replace}'")
        report_lines.append("")

    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## Summary")
    report_lines.append(f"Files with changes: {files_with_changes}")
    report_lines.append(f"Total replacements: {total_changes}")
    report_lines.append("")
    report_lines.append("Per-pattern counts:")
    for find, total in pattern_totals.items():
        replace = next(r for f, r in REPLACEMENTS if f == find)
        report_lines.append(f"  {total:5d}  '{find}' -> '{replace}'")

    report_path = REPO_ROOT / "scripts" / "migration-dryrun-report.txt"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Wrote report: {report_path}", file=sys.stderr)
    print(f"  Files with changes: {files_with_changes}", file=sys.stderr)
    print(f"  Total replacements: {total_changes}", file=sys.stderr)
    return 0


def cmd_execute() -> int:
    """Apply mode: walk, apply replacements, mutate working tree."""
    candidates = walk_repo()
    print(f"Executing on {len(candidates)} candidate files...",
          file=sys.stderr)

    files_changed = 0
    total_changes = 0

    for rel in sorted(candidates):
        path = REPO_ROOT / rel
        try:
            content = path.read_text(encoding="utf-8",
                                     errors="surrogateescape")
        except OSError as e:
            print(f"SKIP (read failed): {rel.as_posix()}: {e}",
                  file=sys.stderr)
            continue

        new_content, counts = apply_replacements(content)
        if new_content == content:
            continue

        path.write_text(new_content, encoding="utf-8",
                        errors="surrogateescape")
        files_changed += 1
        n = sum(counts.values())
        total_changes += n
        print(f"  {n:4d}  {rel.as_posix()}", file=sys.stderr)

    print(f"Done: {files_changed} files, {total_changes} replacements",
          file=sys.stderr)
    return 0


def cmd_verify() -> int:
    """Verify mode. Two-section scan:
      Section A (BLOCKER): residuals of any REPLACEMENTS pattern.
                           Nonzero -> exit code 1.
      Section B (AUDIT):   bare ambiguous tokens for human review.
                           Reported only.
    """
    candidates = walk_repo()
    print(f"Verifying across {len(candidates)} files...", file=sys.stderr)

    blockers: list[tuple[Path, str, int]] = []
    audits: list[tuple[Path, str, int]] = []

    for rel in sorted(candidates):
        path = REPO_ROOT / rel
        try:
            content = path.read_text(encoding="utf-8",
                                     errors="surrogateescape")
        except OSError:
            continue

        for find, _ in REPLACEMENTS:
            n = content.count(find)
            if n > 0:
                blockers.append((rel, find, n))

        for token in AUDIT_PATTERNS:
            n = content.count(token)
            if n > 0:
                audits.append((rel, token, n))

    print("\n=== Section A: BLOCKER residuals ===", file=sys.stderr)
    if blockers:
        print(f"FOUND {len(blockers)} blocker rows:\n", file=sys.stderr)
        for rel, find, n in blockers:
            preview = find[:60] + ("..." if len(find) > 60 else "")
            print(f"  {n:4d}  {rel.as_posix()}: '{preview}'",
                  file=sys.stderr)
    else:
        print("OK: no blocker residuals.", file=sys.stderr)

    print("\n=== Section B: AUDIT findings (informational) ===",
          file=sys.stderr)
    if audits:
        print(f"FOUND {len(audits)} audit rows (human review):\n",
              file=sys.stderr)
        for rel, token, n in audits:
            print(f"  {n:4d}  {rel.as_posix()}: '{token}'", file=sys.stderr)
    else:
        print("OK: no audit findings.", file=sys.stderr)

    return 1 if blockers else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="GT-KB root directory migration find/replace.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true",
                       help="Preview changes; write report; no mutations.")
    group.add_argument("--execute", action="store_true",
                       help="Apply changes to working tree.")
    group.add_argument("--verify", action="store_true",
                       help="Two-section scan for residuals + audit tokens.")
    args = parser.parse_args()

    safety_check()

    if args.dry_run:
        return cmd_dry_run()
    if args.execute:
        return cmd_execute()
    if args.verify:
        return cmd_verify()
    return 1


if __name__ == "__main__":
    sys.exit(main())
