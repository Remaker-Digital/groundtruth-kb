#!/usr/bin/env python3
"""gtkb-propose scaffolding helper (PROJECT-GTKB-GOV-PROPOSAL-STANDARDS Slice 4).

Emits a *structurally compliant* bridge-proposal scaffold so an author clears
the bridge-compliance gates (body-status-token, project-linkage metadata,
inline-JSON target_paths, concrete Specification Links, seeded Prior
Deliberations, spec-derived verification heading) BEFORE Codex review rather
than in a revise loop. The composer counterpart to the gtkb-bridge-propose
*writer* skill: this helper never writes to ``bridge/`` or MemBase — it reads
MemBase read-only and writes only a draft under
``.gtkb-state/propose-drafts/``. The author fills the ``TODO:`` placeholders,
runs the printed self-review checklist, then hands the body to
``gtkb-bridge-propose`` for the credential-scanned write + INDEX insert.

GO: bridge/gtkb-proposal-standards-propose-scaffold-skill-002.md
Authorization: PAUTH-PROJECT-GTKB-GOV-PROPOSAL-STANDARDS-SLICES-1-4.

Usage:
    python scripts/gtkb_propose_scaffold.py scaffold \
        --slug my-thread --work-item WI-1234 --project PROJECT-X \
        --pauth PAUTH-X [--slice 2] [--bridge-kind implementation_proposal] \
        [--target-path scripts/foo.py --target-path tests/test_foo.py]
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BRIDGE_INDEX = PROJECT_ROOT / "bridge" / "INDEX.md"
DRAFTS_DIR = PROJECT_ROOT / ".gtkb-state" / "propose-drafts"
GROUNDTRUTH_DB = PROJECT_ROOT / "groundtruth.db"

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Specs that always govern an implementation-targeting bridge proposal; the
# scaffold pre-lists them so the mandatory applicability preflight passes.
ALWAYS_APPLICABLE_SPECS = (
    "GOV-FILE-BRIDGE-AUTHORITY-001",
    "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
    "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
    "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
    "GOV-STANDING-BACKLOG-001",
)

# The required top-level sections the bridge-compliance gate + protocol expect.
REQUIRED_SECTIONS = (
    "## Summary",
    "## Specification Links",
    "## Prior Deliberations",
    "## Owner Decisions / Input",
    "## Requirement Sufficiency",
    "## Spec-Derived Verification Plan",
    "## Risk / Rollback",
    "## Bridge Filing (INDEX-Canonical)",
    "## Recommended Commit Type",
)

# Heading for the verification section. MUST contain a substring recognized by
# the impl-start gate's VERIFICATION_HEADING_TOKENS ("spec-derived verification"
# and "verification plan" both match this heading).
VERIFICATION_HEADING = "## Spec-Derived Verification Plan"

_AUTHOR_METADATA_STUB = (
    "author_identity: TODO: Prime Builder identity\n"
    "author_harness_id: TODO: harness id (e.g. B)\n"
    "author_session_context_id: TODO: session context id\n"
    "author_model: TODO: model name\n"
    "author_model_version: TODO: model version\n"
    "author_model_configuration: TODO: configuration\n"
)


def validate_slug(slug: str) -> str | None:
    """Return an error string when ``slug`` is not canonical kebab-case, else None."""
    if not slug or not SLUG_RE.match(slug):
        return (
            f"slug {slug!r} is not canonical kebab-case "
            r"(^[a-z0-9]+(-[a-z0-9]+)*$); use lowercase words separated by single hyphens"
        )
    return None


def _index_document_slugs(index_text: str) -> set[str]:
    """Return the set of ``Document:`` slugs present in a bridge INDEX text."""
    return {m.group(1).strip() for m in re.finditer(r"^Document:\s*(\S+)\s*$", index_text, re.MULTILINE)}


def slug_collision(slug: str, index_path: Path | None = None) -> str | None:
    """Return an error string when ``slug`` already names a Document entry in the
    bridge INDEX, else None. Missing INDEX degrades to no-collision."""
    path = index_path or BRIDGE_INDEX
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError:
        return None
    if slug in _index_document_slugs(text):
        return f"slug {slug!r} already has a Document entry in {path}; choose a distinct slug"
    return None


def seed_prior_deliberations(
    slug: str,
    work_item: str,
    db_path: Path | None = None,
    limit: int = 5,
) -> list[tuple[str, str]]:
    """Return up to ``limit`` (DELIB-ID, title) candidates for the topic.

    Read-only. Degrades to an empty list when the DB or the deliberations table
    is unavailable so the helper never hard-fails on environment.
    """
    path = db_path or GROUNDTRUTH_DB
    if not path.is_file():
        return []
    query = f"{slug.replace('-', ' ')} {work_item}".strip()
    terms = [t for t in re.split(r"\s+", query) if len(t) > 2]
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=5)
        conn.row_factory = sqlite3.Row
        # Lightweight LIKE-based candidate surfacing over current deliberations;
        # the skill layer may substitute richer semantic search, but this keeps
        # the helper dependency-free and deterministic for tests.
        like_clauses = " OR ".join(["title LIKE ?"] * len(terms)) or "1=0"
        params = [f"%{t}%" for t in terms]
        rows = conn.execute(
            f"SELECT id, title FROM current_deliberations WHERE {like_clauses} ORDER BY id DESC LIMIT ?",
            (*params, limit),
        ).fetchall()
        return [(r["id"], r["title"] or "") for r in rows]
    except (sqlite3.Error, OSError):
        return []
    finally:
        if conn is not None:
            conn.close()


def _prior_deliberations_block(candidates: list[tuple[str, str]]) -> str:
    if not candidates:
        return "_No prior deliberations: TODO state the reason this topic has no DA precedent (novel topic)._\n"
    lines = [f"- `{cid}` — {title}" for cid, title in candidates]
    lines.append(
        "- TODO: prune the seeded candidates above to the genuinely relevant ones "
        "and explain how this proposal builds on / differs from each."
    )
    return "\n".join(lines) + "\n"


def _specification_links_block(specs: list[str]) -> str:
    lines = [f"- `{sid}` — TODO: how this spec governs the work." for sid in specs]
    lines.append("- TODO: add any further governing specs; remove any that do not apply.")
    return "\n".join(lines) + "\n"


def build_scaffold(
    *,
    slug: str,
    work_item: str,
    project: str,
    pauth: str,
    target_paths: list[str],
    bridge_kind: str = "implementation_proposal",
    slice_n: int | None = None,
    prior_deliberations: list[tuple[str, str]] | None = None,
    specification_links: list[str] | None = None,
) -> str:
    """Build a structurally compliant NEW bridge-proposal scaffold body."""
    specs = list(specification_links or ALWAYS_APPLICABLE_SPECS)
    delibs = prior_deliberations or []
    tp_json = json.dumps(target_paths or ["TODO/relative/path.py"])
    slice_label = f" (Slice {slice_n})" if slice_n is not None else ""

    return f"""NEW

# {slug}{slice_label} — TODO: concise proposal title

bridge_kind: {bridge_kind}
Document: {slug}
Version: 001
Author: TODO: Prime Builder (harness)
Date: TODO UTC

{_AUTHOR_METADATA_STUB}
Project Authorization: {pauth}
Project: {project}
Work Item: {work_item}

target_paths: {tp_json}

implementation_scope: TODO: source | governance | protocol
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Summary

TODO: what this proposal does and why (one or two paragraphs).

## Specification Links

{_specification_links_block(specs)}
## Prior Deliberations

{_prior_deliberations_block(delibs)}
## Owner Decisions / Input

TODO: if this proposal depends on owner approval, enumerate the AskUserQuestion
evidence (DELIB id / directive) that authorizes it; otherwise state that no
owner decision is required and why.

## Requirement Sufficiency

TODO: choose exactly one operative state:
- Existing requirements sufficient — cite the governing requirements; OR
- New or revised requirement required before implementation.

{VERIFICATION_HEADING}

TODO: map each linked specification to a test or verification command and the
expected result. Prefer the repo venv interpreter for reproducible evidence:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest <path> -q --no-header -p no:cacheprovider
```

## Risk / Rollback

TODO: risk surface + single-commit rollback note.

## Bridge Filing (INDEX-Canonical)

This proposal is filed under `bridge/` with a `NEW` entry inserted at the top of
the `{slug}` document list in `bridge/INDEX.md`; no prior version is deleted or
rewritten (append-only). `bridge/INDEX.md` remains the canonical workflow state
per `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL`.

## Recommended Commit Type

TODO: feat | fix | refactor | chore | docs | test (justified by the diff).

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
"""


def self_review_checklist(slug: str) -> str:
    """Return the pre-filing self-review checklist (commands the author runs)."""
    return f"""Self-review checklist before filing {slug!r} (fix any failure, then re-check):

1. Mandatory applicability preflight (expect preflight_passed: true, missing_required_specs: []):
   python scripts/bridge_applicability_preflight.py --bridge-id {slug}
2. Mandatory clause preflight (expect Blocking gaps: 0):
   python scripts/adr_dcl_clause_preflight.py --bridge-id {slug}
3. Phantom-spec sweep — confirm EVERY cited SPEC/GOV/ADR/DCL/PB id exists in the
   live specifications table (a phantom citation passes preflights but is caught
   at review).
4. target_paths is parseable inline JSON (impl-start `begin` requires inline-JSON
   or a `## target_paths` heading; a bold label is NOT parsed).
5. The verification section heading contains a VERIFICATION_HEADING_TOKENS
   substring (this scaffold uses {VERIFICATION_HEADING!r}).
6. First non-blank line is a canonical status token (NEW) — body-status-token rule.
7. Replace every remaining `TODO:` placeholder with real content.

When green, hand the filled draft body to the gtkb-bridge-propose skill for the
credential-scanned write + INDEX insert (do NOT write bridge/ from this helper).
"""


def write_draft(slug: str, content: str, project_root: Path | None = None) -> Path:
    """Write the scaffold to ``.gtkb-state/propose-drafts/<slug>-001.md`` and return it."""
    root = project_root or PROJECT_ROOT
    drafts = root / ".gtkb-state" / "propose-drafts"
    drafts.mkdir(parents=True, exist_ok=True)
    target = drafts / f"{slug}-001.md"
    target.write_text(content, encoding="utf-8", newline="\n")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sc = sub.add_parser("scaffold", help="Emit a compliant proposal scaffold draft.")
    sc.add_argument("--slug", required=True)
    sc.add_argument("--work-item", required=True)
    sc.add_argument("--project", required=True)
    sc.add_argument("--pauth", required=True)
    sc.add_argument("--slice", type=int, default=None)
    sc.add_argument("--bridge-kind", default="implementation_proposal")
    sc.add_argument("--target-path", action="append", default=[], dest="target_paths")
    sc.add_argument("--no-write", action="store_true", help="Print to stdout without writing a draft.")
    args = parser.parse_args(argv)

    slug_err = validate_slug(args.slug)
    if slug_err:
        print(f"ERROR: {slug_err}", file=sys.stderr)
        return 2
    collision = slug_collision(args.slug)
    if collision:
        print(f"ERROR: {collision}", file=sys.stderr)
        return 2

    delibs = seed_prior_deliberations(args.slug, args.work_item)
    body = build_scaffold(
        slug=args.slug,
        work_item=args.work_item,
        project=args.project,
        pauth=args.pauth,
        target_paths=args.target_paths,
        bridge_kind=args.bridge_kind,
        slice_n=args.slice,
        prior_deliberations=delibs,
    )

    if args.no_write:
        print(body)
    else:
        path = write_draft(args.slug, body)
        print(f"Draft scaffold written: {path}")
    print()
    print(self_review_checklist(args.slug))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
