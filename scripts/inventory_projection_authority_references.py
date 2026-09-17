#!/usr/bin/env python
"""WI-6305 Slice 1: inventory references to generated harness-configuration targets.

`WI-6305` eliminates dependencies from artifacts outside generated harness
configuration onto generated target content. Its acceptance criterion -- that no
residual consumer reads, cites, imports, executes, or treats a generated target
as authority -- cannot be evaluated without a complete, reproducible inventory.
This script builds that inventory. **It corrects nothing.**

Read-only by construction: it opens files for reading, writes only a structured
report under the session-scoped scratchpad, and never writes source, configuration, or any
generated target.

Search domain includes the neutral source `.harness-baseline-configuration/`
per the owner scope extension (`DELIB-20260813010684`, Q2). That extension is
load-bearing: the neutral source carries hundreds of generated-target references
of its own, and the original scope sentence excluded them.

Authority: `GOV-HARNESS-NEUTRAL-BASELINE-001`, `GOV-SOURCE-OF-TRUTH-FRESHNESS-001`,
`DCL-CROSS-HARNESS-ENFORCEMENT-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

try:
    from scripts.gtkb_session_id import session_scratch_dirname
except ImportError:  # pragma: no cover - direct script execution path
    from gtkb_session_id import session_scratch_dirname

# Generated harness-configuration roots. These directories are projections: their
# content is produced from `.harness-baseline-configuration/` by the projector and
# is never edited directly.
HARNESS_PROJECTION_DIRS: tuple[str, ...] = (
    ".claude",
    ".codex",
    ".goose",
    ".cursor",
    ".agent",
    ".api-harness",
)

_TARGET_RE = re.compile(
    r"\.(?:" + "|".join(re.escape(name.lstrip(".")) for name in HARNESS_PROJECTION_DIRS) + r")/[A-Za-z0-9_./-]+"
)

# The canonical neutral source, and the canonical helper tree. A reference that
# names one of these on the same line is paired with its real carrier.
CANONICAL_MARKERS: tuple[str, ...] = (
    ".harness-baseline-configuration/",
    "scripts/skill-helpers/",
    "scripts/harness_projection/",
)

# Sources that legitimately name generated targets because they produce or declare
# them. These are `required`, not residual consumers.
REQUIRED_SOURCE_PREFIXES: tuple[str, ...] = (
    "scripts/harness_projection/",
    ".harness-baseline-configuration/.projection-manifest.json",
    ".harness-baseline-configuration/skills/MANIFEST.json",
)
REQUIRED_SOURCE_SUFFIXES: tuple[str, ...] = ("/hooks.json",)

# Indicators that a line depends on the target operationally rather than
# describing it. Kept explicit and deterministic -- no heuristics over prose.
DEPENDENCY_MARKERS: tuple[str, ...] = (
    "python ",
    "pythonw ",
    "import ",
    "subprocess",
    "exec(",
    "open(",
    "Path(",
    "run_py_no_window",
    "$CLAUDE_PROJECT_DIR",
    "sys.path",
)

# Directories never scanned: the generated targets themselves (we inventory
# references *to* them from elsewhere), plus caches, archives and runtime state.
EXCLUDED_DIR_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        "__pycache__",
        ".venv",
        "node_modules",
        ".gtkb-state",
        ".groundtruth-chroma",
        ".pytest-tmp",
        "archive",
        "scratchpad",
    }
)

REQUIRED = "required"
RESIDUAL_CONSUMER = "residual_consumer"
ROUTED = "routed"
NARRATIVE = "narrative"

CLASSIFICATIONS: tuple[str, ...] = (REQUIRED, RESIDUAL_CONSUMER, ROUTED, NARRATIVE)

_PROSE_SUFFIXES: frozenset[str] = frozenset({".md", ".rst", ".txt"})


@dataclass(frozen=True)
class Reference:
    """One reference to a generated harness-configuration target."""

    source_path: str
    line_number: int
    target: str
    classification: str
    harness: str


def _harness_of(target: str) -> str:
    head = target.split("/", 1)[0]
    return head.lstrip(".")


# Files larger than this are not prose or source we can meaningfully classify;
# skipping them keeps a whole-tree run bounded on a repository with tens of
# thousands of materialized entries.
_MAX_FILE_BYTES = 2_000_000

_SKIPPED_SUFFIXES: frozenset[str] = frozenset(
    {".pyc", ".pyo", ".so", ".dll", ".exe", ".zip", ".whl", ".gz", ".db", ".png", ".jpg", ".gif", ".pdf", ".ico"}
)


# Windows reserved device names. A path whose stem is one of these is a device,
# not a file: `os.path.relpath` raises on it and opening it can block
# indefinitely. Encountered live in this repository during WI-6305 Slice 1.
_RESERVED_DEVICE_NAMES: frozenset[str] = frozenset(
    {"con", "prn", "aux", "nul"} | {f"com{digit}" for digit in range(1, 10)} | {f"lpt{digit}" for digit in range(1, 10)}
)


def _walk_candidate_files(project_root: Path) -> list[tuple[Path, str]]:
    """Return ``(absolute_path, repo_relative_posix)`` pairs for scannable files.

    Pruning in-walk rather than filtering afterwards is what keeps this bounded:
    the excluded trees (`.git`, `.venv`, `.pytest-tmp`, `archive`, and the
    projections themselves) hold the large majority of entries in this
    repository -- excluding `.pytest-tmp` alone took the candidate set from
    ~179k files to ~24k.

    The relative path is composed from the walk position rather than recomputed
    with ``os.path.relpath``: that avoids a per-file syscall and sidesteps a hard
    failure on Windows reserved device names.
    """
    import os

    root_str = str(project_root)
    candidates: list[tuple[Path, str]] = []
    for dirpath, dirnames, filenames in os.walk(root_str):
        rel_dir = os.path.relpath(dirpath, root_str).replace(os.sep, "/")
        at_root = rel_dir == "."
        dirnames[:] = sorted(
            name
            for name in dirnames
            # The projection directories themselves are targets, not consumers.
            if name not in EXCLUDED_DIR_NAMES and not (at_root and name in HARNESS_PROJECTION_DIRS)
        )
        for filename in sorted(filenames):
            if filename.split(".", 1)[0].lower() in _RESERVED_DEVICE_NAMES:
                continue
            if Path(filename).suffix.lower() in _SKIPPED_SUFFIXES:
                continue
            rel = filename if at_root else f"{rel_dir}/{filename}"
            candidates.append((Path(dirpath) / filename, rel))
    return candidates


def domain_coverage(project_root: Path) -> dict[str, int]:
    """Count the candidate files the scan walks inside and outside the neutral baseline.

    Coverage is proven by files walked, not by references found: a neutral baseline names no generated target, so a
    zero reference count there is the expected state, while a zero file count means the domain was not searched.
    """
    baseline_files = 0
    other_files = 0
    for _path, source_path in _walk_candidate_files(project_root):
        if source_path.startswith(".harness-baseline-configuration/"):
            baseline_files += 1
        else:
            other_files += 1
    return {"neutral_baseline_files": baseline_files, "other_files": other_files}


def classify_reference(*, source_path: str, line: str, target: str) -> str:
    """Classify one reference. Deterministic and order-sensitive.

    The order encodes precedence: a projector naming its own output is always
    ``required`` even though the line also looks operational; a reference paired
    with its canonical carrier is ``routed`` even in prose; and prose is only
    ``narrative`` when it shows no operational dependency.
    """
    if source_path.startswith(REQUIRED_SOURCE_PREFIXES) or source_path.endswith(REQUIRED_SOURCE_SUFFIXES):
        return REQUIRED
    if any(marker in line for marker in CANONICAL_MARKERS):
        return ROUTED
    is_prose = Path(source_path).suffix.lower() in _PROSE_SUFFIXES
    has_dependency = any(marker in line for marker in DEPENDENCY_MARKERS)
    if is_prose and not has_dependency:
        return NARRATIVE
    return RESIDUAL_CONSUMER


def scan(project_root: Path) -> list[Reference]:
    """Return every generated-target reference outside the projections themselves.

    Results are sorted so two runs over an unchanged tree are byte-identical.
    """
    references: list[Reference] = []
    for path, source_path in _walk_candidate_files(project_root):
        try:
            if path.stat().st_size > _MAX_FILE_BYTES:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            continue
        if not any(name in text for name in HARNESS_PROJECTION_DIRS):
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for match in _TARGET_RE.finditer(line):
                target = match.group(0)
                references.append(
                    Reference(
                        source_path=source_path,
                        line_number=line_number,
                        target=target,
                        classification=classify_reference(source_path=source_path, line=line, target=target),
                        harness=_harness_of(target),
                    )
                )
    references.sort(key=lambda ref: (ref.source_path, ref.line_number, ref.target))
    return references


def build_report(references: list[Reference]) -> dict[str, object]:
    """Build the structured report. Contains no timestamp, so it is comparable."""
    by_classification = {name: 0 for name in CLASSIFICATIONS}
    by_harness: dict[str, int] = {}
    baseline_side = 0
    for ref in references:
        by_classification[ref.classification] += 1
        by_harness[ref.harness] = by_harness.get(ref.harness, 0) + 1
        if ref.source_path.startswith(".harness-baseline-configuration/"):
            baseline_side += 1
    return {
        "schema_version": 1,
        "work_item": "WI-6305",
        "total_references": len(references),
        "baseline_side_references": baseline_side,
        "by_classification": by_classification,
        "by_harness": dict(sorted(by_harness.items())),
        "references": [asdict(ref) for ref in references],
    }


def render_markdown(report: dict[str, object]) -> str:
    by_classification = report["by_classification"]
    assert isinstance(by_classification, dict)
    lines = [
        "# Projection-authority reference inventory (WI-6305)",
        "",
        "Read-only inventory. This slice corrects nothing.",
        "",
        f"- Total references: {report['total_references']}",
        f"- Inside the neutral baseline: {report['baseline_side_references']}",
        "",
        "| Classification | Count |",
        "|---|---|",
    ]
    lines.extend(f"| `{name}` | {by_classification[name]} |" for name in CLASSIFICATIONS)
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Runtime evidence directory (default: <project-root>/scratchpad/<session>/projection-authority-inventory).",
    )
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON on stdout.")
    args = parser.parse_args(argv)

    project_root = args.project_root.resolve()
    references = scan(project_root)
    report = build_report(references)

    # Canon s17: inventory output is session-scoped scratch, never `.gtkb-state`.
    # `--out-dir` still overrides.
    out_dir = args.out_dir or (
        project_root / "scratchpad" / session_scratch_dirname() / "projection-authority-inventory"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "inventory.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out_dir / "inventory.md").write_text(render_markdown(report), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_markdown(report), end="")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
