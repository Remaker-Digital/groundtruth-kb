# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Helper utilities for Loyal Opposition verdict authoring."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any


def _discover_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "scripts" / "bridge_author_metadata.py").is_file():
            return parent
    return Path(__file__).resolve().parents[4]


PROJECT_ROOT = _discover_project_root()
GROUNDTRUTH_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if GROUNDTRUTH_SRC.is_dir() and str(GROUNDTRUTH_SRC) not in sys.path:
    sys.path.insert(0, str(GROUNDTRUTH_SRC))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from groundtruth_kb.bridge.prior_deliberations import (  # noqa: E402
    pre_populate_prior_deliberations,
)

DEFAULT_VERDICT_PREPOPULATION_LOG = Path(".gtkb-state/bridge-verify-helper/last-prepopulation.json")


def seed_prior_deliberations(
    slug: str,
    body: str,
    *,
    db: Any | bool | None = None,
    glossary_path: Path | None = None,
    log_path: Path | bool | None = DEFAULT_VERDICT_PREPOPULATION_LOG,
    pre_populate: bool = True,
) -> str:
    """Seed a verdict body's ``## Prior Deliberations`` section."""
    if not pre_populate:
        return body
    return pre_populate_prior_deliberations(
        slug,
        body,
        db=db,
        glossary_path=glossary_path,
        log_path=log_path,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Seed a verdict body's Prior Deliberations section.",
    )
    parser.add_argument("--slug", required=True, help="Bridge thread slug shared by the verdict.")
    parser.add_argument(
        "--body-file",
        type=Path,
        help="Read the verdict body from this UTF-8 file. Defaults to stdin.",
    )
    parser.add_argument(
        "--no-semantic-search",
        action="store_true",
        help="Disable KnowledgeDB semantic search and use glossary seeds only.",
    )
    parser.add_argument(
        "--no-log",
        action="store_true",
        help="Disable the verify-side prepopulation audit log.",
    )
    parser.add_argument(
        "--no-prepopulate",
        action="store_true",
        help="Return the body unchanged for explicit opt-out workflows.",
    )
    args = parser.parse_args(argv)

    if args.body_file is not None:
        body = args.body_file.read_text(encoding="utf-8")
    else:
        body = sys.stdin.read()

    seeded = seed_prior_deliberations(
        args.slug,
        body,
        db=False if args.no_semantic_search else None,
        log_path=False if args.no_log else DEFAULT_VERDICT_PREPOPULATION_LOG,
        pre_populate=not args.no_prepopulate,
    )
    sys.stdout.write(seeded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
