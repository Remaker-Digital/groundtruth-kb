#!/usr/bin/env python3
"""Helper for filing completed bridge REVISED versions.

The helper has two lifecycles:

- ``scaffold_revision`` writes a non-dispatchable draft under
  ``.gtkb-state/bridge-revisions/drafts/``.
- ``file_revision`` files completed content as ``bridge/<slug>-NNN.md`` and
  inserts the live ``REVISED:`` line only after validation gates pass.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_BRIDGE_DIR = PROJECT_ROOT / "bridge"
DEFAULT_DRAFT_DIR = PROJECT_ROOT / ".gtkb-state" / "bridge-revisions" / "drafts"
BRIDGE_PROPOSE_HELPER = PROJECT_ROOT / ".claude" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"

if str(PROJECT_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))


class BridgeRevisionError(RuntimeError):
    """Base error for revision-helper failures."""


class BridgeDocumentNotFoundError(BridgeRevisionError):
    """Raised when ``bridge/INDEX.md`` lacks an exact ``Document: <slug>`` entry."""


class BridgeLatestStatusError(BridgeRevisionError):
    """Raised when write-capable operations are requested for a non-NO-GO thread."""


class BridgeRevisionPlaceholderError(BridgeRevisionError):
    """Raised when completed content still contains draft placeholders."""


class BridgePreflightError(BridgeRevisionError):
    """Raised when candidate-content preflights fail before live filing."""


class BridgeIndexConflictError(BridgeRevisionError):
    """Raised when ``bridge/INDEX.md`` changes during live filing."""


class BridgeFileAlreadyExistsError(BridgeRevisionError):
    """Raised when the target live bridge version already exists."""


@dataclass(frozen=True)
class BridgeVersion:
    status: str
    rel_path: str
    abs_path: Path
    version: int


@dataclass(frozen=True)
class RevisionPlan:
    slug: str
    latest_status: str
    latest_path: str
    next_version: int
    live_path: str
    draft_path: str
    index_line: str
    findings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


FINDING_RE = re.compile(
    r"^\s*(?:#{2,6}\s*)?(?P<label>(?:F\d+|Finding\b)[^\n]{0,160}(?:P[0-4][^\n]{0,120})?)",
    re.IGNORECASE,
)
PLACEHOLDER_RES = (
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\bTBD\b", re.IGNORECASE),
    re.compile(r"<\s*fill\s+in", re.IGNORECASE),
    re.compile(r"draft_only\s*:\s*true", re.IGNORECASE),
    re.compile(r"_No prior deliberations:\s*<fill in reason before filing>\._", re.IGNORECASE),
    re.compile(r"^\s*(?:response|resolution)\s*:\s*(?:TODO|TBD|<fill in)", re.IGNORECASE | re.MULTILINE),
)


def _load_bridge_propose_helper():
    spec = importlib.util.spec_from_file_location("bridge_propose_write_bridge", BRIDGE_PROPOSE_HELPER)
    if spec is None or spec.loader is None:
        raise BridgeRevisionError(f"Could not load bridge-propose helper at {BRIDGE_PROPOSE_HELPER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_index(bridge_dir: Path) -> str:
    index_path = bridge_dir / "INDEX.md"
    if not index_path.is_file():
        raise BridgeDocumentNotFoundError(f"Bridge index not found: {index_path}")
    return index_path.read_text(encoding="utf-8")


def _parse_versions(slug: str, bridge_dir: Path) -> list[BridgeVersion]:
    text = _read_index(bridge_dir)
    versions: list[BridgeVersion] = []
    in_doc = False
    root = bridge_dir.parent
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("Document:"):
            if in_doc:
                break
            in_doc = line.removeprefix("Document:").strip() == slug
            continue
        if not in_doc:
            continue
        if line == "":
            break
        match = re.match(r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY):\s*(bridge/.+\.md)$", line)
        if not match:
            continue
        rel_path = match.group(2)
        version_match = re.search(r"-(\d{3})\.md$", rel_path)
        versions.append(
            BridgeVersion(
                status=match.group(1),
                rel_path=rel_path,
                abs_path=root / rel_path,
                version=int(version_match.group(1)) if version_match else 0,
            )
        )
    if not versions:
        raise BridgeDocumentNotFoundError(f"No exact bridge document entry found for {slug!r}")
    return versions


def _highest_version(versions: list[BridgeVersion]) -> int:
    return max(version.version for version in versions)


def _latest_version(versions: list[BridgeVersion]) -> BridgeVersion:
    return versions[0]


def extract_findings(text: str) -> tuple[str, ...]:
    findings: list[str] = []
    for line in text.splitlines():
        match = FINDING_RE.match(line)
        if not match:
            continue
        label = re.sub(r"\s+", " ", match.group("label")).strip(" :-")
        if label and label not in findings:
            findings.append(label)
    return tuple(findings)


def plan_revision(slug: str, *, bridge_dir: Path | None = None, draft_dir: Path | None = None) -> RevisionPlan:
    bridge_root = bridge_dir or DEFAULT_BRIDGE_DIR
    draft_root = draft_dir or DEFAULT_DRAFT_DIR
    versions = _parse_versions(slug, bridge_root)
    latest = _latest_version(versions)
    latest_text = latest.abs_path.read_text(encoding="utf-8") if latest.abs_path.is_file() else ""
    next_version = _highest_version(versions) + 1
    live_rel = f"bridge/{slug}-{next_version:03d}.md"
    return RevisionPlan(
        slug=slug,
        latest_status=latest.status,
        latest_path=latest.rel_path,
        next_version=next_version,
        live_path=live_rel,
        draft_path=str((draft_root / f"{slug}-{next_version:03d}.md").relative_to(PROJECT_ROOT))
        if _is_under(draft_root, PROJECT_ROOT)
        else str(draft_root / f"{slug}-{next_version:03d}.md"),
        index_line=f"REVISED: {live_rel}",
        findings=extract_findings(latest_text),
    )


def _prior_proposal_has_owner_decisions(versions: list[BridgeVersion]) -> bool:
    for version in versions[1:]:
        if version.status in {"NEW", "REVISED"} and version.abs_path.is_file():
            text = version.abs_path.read_text(encoding="utf-8")
            if "Owner Decisions / Input" in text or "AskUserQuestion" in text or "owner decision" in text.lower():
                return True
    return False


def _scaffold_body(slug: str, plan: RevisionPlan, include_owner_decisions: bool) -> str:
    finding_sections = "\n".join(
        f"### {finding}\n\nResponse: <fill in concrete correction before filing>\n" for finding in plan.findings
    )
    if not finding_sections:
        finding_sections = "### Finding Review\n\nResponse: <fill in concrete correction before filing>\n"
    owner_section = (
        "## Owner Decisions / Input\n\n"
        "<fill in carried-forward owner-decision evidence or state why none is newly required before filing>\n\n"
        if include_owner_decisions
        else ""
    )
    return (
        "REVISED\n\n"
        f"# Bridge Revision Draft - {slug}\n\n"
        "draft_only: true\n"
        f"intended_live_path: `{plan.live_path}`\n"
        f"responds_to: `{plan.latest_path}`\n\n"
        "## Revision Claim\n\n<fill in completed revision claim before filing>\n\n"
        "## Specification Links\n\n<fill in all relevant governing specifications before filing>\n\n"
        "## Prior Deliberations\n\n_No prior deliberations: <fill in reason before filing>._\n\n"
        f"{owner_section}"
        "## Findings Addressed\n\n"
        f"{finding_sections}\n"
        "## Scope Changes\n\n<fill in scope changes or state none before filing>\n\n"
        "## Pre-Filing Preflight Subsection\n\n"
        "<run applicability and clause preflights before filing>\n\n"
        "## Verification Plan\n\n<fill in spec-to-test mapping before filing>\n\n"
        "## Risk And Rollback\n\n<fill in risks and rollback before filing>\n"
    )


def scaffold_revision(
    slug: str,
    *,
    bridge_dir: Path | None = None,
    draft_dir: Path | None = None,
) -> Path:
    bridge_root = bridge_dir or DEFAULT_BRIDGE_DIR
    draft_root = draft_dir or DEFAULT_DRAFT_DIR
    versions = _parse_versions(slug, bridge_root)
    if _latest_version(versions).status != "NO-GO":
        raise BridgeLatestStatusError("scaffold mode requires latest bridge status NO-GO")
    plan = plan_revision(slug, bridge_dir=bridge_root, draft_dir=draft_root)
    draft_path = draft_root / f"{slug}-{plan.next_version:03d}.md"
    if draft_path.exists():
        raise BridgeFileAlreadyExistsError(f"Draft already exists: {draft_path}")
    draft_path.parent.mkdir(parents=True, exist_ok=True)
    draft_path.write_text(
        _scaffold_body(slug, plan, _prior_proposal_has_owner_decisions(versions)),
        encoding="utf-8",
        newline="\n",
    )
    return draft_path


def _placeholder_hits(content: str) -> list[str]:
    hits: list[str] = []
    for pattern in PLACEHOLDER_RES:
        match = pattern.search(content)
        if match:
            hits.append(match.group(0))
    return hits


def _assert_completed_revision(content: str) -> None:
    if content.lstrip().splitlines()[0].strip() != "REVISED":
        raise BridgeRevisionPlaceholderError("Completed revision content must start with REVISED")
    hits = _placeholder_hits(content)
    if hits:
        raise BridgeRevisionPlaceholderError(f"Completed revision content still contains placeholders: {hits}")


def _run_preflight_command(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )


def _run_candidate_preflights(slug: str, candidate_path: Path, *, project_root: Path = PROJECT_ROOT) -> None:
    commands = [
        [
            sys.executable,
            "scripts/bridge_applicability_preflight.py",
            "--bridge-id",
            slug,
            "--content-file",
            str(candidate_path),
            "--json",
        ],
        [
            sys.executable,
            "scripts/adr_dcl_clause_preflight.py",
            "--bridge-id",
            slug,
            "--content-file",
            str(candidate_path),
        ],
    ]
    for command in commands:
        result = _run_preflight_command(command, cwd=project_root)
        if result.returncode != 0:
            output = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
            raise BridgePreflightError(f"Candidate preflight failed ({' '.join(command)}): {output}")


def _insert_revised_index_line(index_text: str, slug: str, line_to_insert: str) -> str:
    lines = index_text.splitlines(keepends=True)
    out: list[str] = []
    inserted = False
    in_doc = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("Document:"):
            if in_doc and not inserted:
                raise BridgeDocumentNotFoundError(f"Document entry for {slug!r} had no version lines")
            out.append(line)
            in_doc = stripped.removeprefix("Document:").strip() == slug
            continue
        if in_doc and not inserted and stripped:
            out.append(line_to_insert + "\n")
            inserted = True
            in_doc = False
        out.append(line)
    if in_doc and not inserted:
        out.append(line_to_insert + "\n")
        inserted = True
    if not inserted:
        raise BridgeDocumentNotFoundError(f"No exact bridge document entry found for {slug!r}")
    return "".join(out)


def file_revision(
    slug: str,
    *,
    content: str | None = None,
    draft_path: Path | None = None,
    bridge_dir: Path | None = None,
    run_preflights: bool = True,
) -> Path:
    if content is None:
        if draft_path is None:
            raise BridgeRevisionError("file mode requires content or draft_path")
        content = draft_path.read_text(encoding="utf-8")
    _assert_completed_revision(content)

    bridge_root = bridge_dir or DEFAULT_BRIDGE_DIR
    versions = _parse_versions(slug, bridge_root)
    latest = _latest_version(versions)
    if latest.status != "NO-GO":
        raise BridgeLatestStatusError(f"file mode requires latest bridge status NO-GO; got {latest.status}")
    plan = plan_revision(slug, bridge_dir=bridge_root)
    live_path = bridge_root.parent / plan.live_path
    index_path = bridge_root / "INDEX.md"
    if live_path.exists():
        raise BridgeFileAlreadyExistsError(f"Live bridge file already exists: {live_path}")

    helper = _load_bridge_propose_helper()
    hits = helper.scan_credential_hits(content)
    helper.handle_hits_abort_or_redact(content, hits, mode="abort")

    original_index = index_path.read_text(encoding="utf-8")
    candidate_dir = PROJECT_ROOT / ".tmp" / "bridge-revisions"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    candidate_path = candidate_dir / f"{slug}-{plan.next_version:03d}.candidate.md"
    try:
        candidate_path.write_text(content, encoding="utf-8", newline="\n")
        if run_preflights:
            _run_candidate_preflights(slug, candidate_path)
        if index_path.read_text(encoding="utf-8") != original_index:
            raise BridgeIndexConflictError("bridge/INDEX.md changed before live file write")
        live_path.parent.mkdir(parents=True, exist_ok=True)
        live_path.write_text(content, encoding="utf-8", newline="\n")
        new_index = _insert_revised_index_line(original_index, slug, plan.index_line)
        temp_path = index_path.with_name(f"{index_path.name}.tmp.{os.getpid()}")
        temp_path.write_text(new_index, encoding="utf-8", newline="\n")
        try:
            if index_path.read_text(encoding="utf-8") != original_index:
                temp_path.unlink(missing_ok=True)
                raise BridgeIndexConflictError("bridge/INDEX.md changed during live filing")
            os.replace(temp_path, index_path)
        except Exception:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            raise
    finally:
        candidate_path.unlink(missing_ok=True)
    # WI-3364: best-effort event-driven bridge/INDEX.md archival trim.
    try:
        import sys as _sys
        _trim_scripts = str(bridge_root.parent / "scripts")
        if _trim_scripts not in _sys.path:
            _sys.path.insert(0, _trim_scripts)
        from bridge_index_archival import maybe_archive_and_prune_index as _trim
        _trim(bridge_root.parent, current_thread=slug)
    except Exception:  # noqa: BLE001 - archival must never fail a bridge write
        pass
    return live_path


def _is_under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("plan", "scaffold", "file"))
    parser.add_argument("slug")
    parser.add_argument("--bridge-dir", type=Path, default=DEFAULT_BRIDGE_DIR)
    parser.add_argument("--draft-path", type=Path)
    parser.add_argument("--content-file", type=Path)
    args = parser.parse_args(argv)

    if args.mode == "plan":
        print(json.dumps(plan_revision(args.slug, bridge_dir=args.bridge_dir).to_dict(), indent=2, sort_keys=True))
        return 0
    if args.mode == "scaffold":
        path = scaffold_revision(args.slug, bridge_dir=args.bridge_dir)
        print(str(path))
        return 0
    content = args.content_file.read_text(encoding="utf-8") if args.content_file else None
    path = file_revision(args.slug, content=content, draft_path=args.draft_path, bridge_dir=args.bridge_dir)
    print(str(path))
    return 0


__all__ = [
    "BridgeDocumentNotFoundError",
    "BridgeFileAlreadyExistsError",
    "BridgeIndexConflictError",
    "BridgeLatestStatusError",
    "BridgePreflightError",
    "BridgeRevisionPlaceholderError",
    "extract_findings",
    "file_revision",
    "plan_revision",
    "scaffold_revision",
]


if __name__ == "__main__":
    raise SystemExit(_main())
