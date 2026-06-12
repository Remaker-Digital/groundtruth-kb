#!/usr/bin/env python3
"""Helper for filing bridge post-implementation reports.

The helper has three modes:

- ``plan_report`` inspects a latest-GO bridge thread without mutation.
- ``scaffold_report`` writes a non-dispatchable draft under
  ``.gtkb-state/bridge-impl-reports/drafts/``.
- ``file_report`` writes ``bridge/<slug>-NNN.md`` and inserts a live ``NEW:``
  row on the same ``Document:`` entry after credential and concurrency gates.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_BRIDGE_DIR = PROJECT_ROOT / "bridge"
DEFAULT_DRAFT_DIR = PROJECT_ROOT / ".gtkb-state" / "bridge-impl-reports" / "drafts"
BRIDGE_PROPOSE_HELPER = PROJECT_ROOT / ".claude" / "skills" / "bridge-propose" / "helpers" / "write_bridge.py"

if str(PROJECT_ROOT / "groundtruth-kb" / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "groundtruth-kb" / "src"))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

ensure_author_metadata = importlib.import_module("scripts.bridge_author_metadata").ensure_author_metadata
_bridge_writer = importlib.import_module("scripts.gtkb_bridge_writer")
PRIME_ROLE_SLOT = _bridge_writer.PRIME_ROLE_SLOT
WriterBridgeConflictError = _bridge_writer.BridgeConflictError
WriterBridgeTransitionError = _bridge_writer.BridgeTransitionError
insert_index_status = _bridge_writer.insert_index_status
validate_transition = _bridge_writer.validate_transition
write_bridge_file = _bridge_writer.write_bridge_file


class BridgeImplReportError(RuntimeError):
    """Base error for implementation-report helper failures."""


class BridgeDocumentNotFoundError(BridgeImplReportError):
    """Raised when ``bridge/INDEX.md`` lacks an exact ``Document: <slug>`` entry."""


class BridgeLatestStatusError(BridgeImplReportError):
    """Raised when write-capable operations are requested for a non-GO thread."""


class BridgeFileAlreadyExistsError(BridgeImplReportError):
    """Raised when the target bridge report or draft already exists."""


class BridgeIndexConflictError(BridgeImplReportError):
    """Raised when ``bridge/INDEX.md`` changes during live filing."""


class BridgeApprovedProposalNotFoundError(BridgeImplReportError):
    """Raised when a latest-GO thread has no prior proposal version to carry forward."""


@dataclass(frozen=True)
class BridgeVersion:
    status: str
    rel_path: str
    abs_path: Path
    version: int


@dataclass(frozen=True)
class ImplReportPlan:
    slug: str
    latest_status: str
    latest_path: str
    next_version: int
    report_path: str
    draft_path: str
    index_line: str
    proposal_path: str
    go_path: str
    linked_specs: tuple[str, ...]
    files_changed: tuple[str, ...]
    version_chain: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_STATUS_LINE_RE = re.compile(
    r"^(NEW|REVISED|GO|NO-GO|VERIFIED|WITHDRAWN|ADVISORY|DEFERRED|ACCEPTED|BLOCKED):\s*(bridge/.+\.md)$"
)
_SECTION_RE_TEMPLATE = r"^##\s+{heading}\s*$"
_VERSION_RE = re.compile(r"-(\d{3})\.md$")


def _load_bridge_propose_helper():
    spec = importlib.util.spec_from_file_location("bridge_propose_write_bridge", BRIDGE_PROPOSE_HELPER)
    if spec is None or spec.loader is None:
        raise BridgeImplReportError(f"Could not load bridge-propose helper at {BRIDGE_PROPOSE_HELPER}")
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
        match = _STATUS_LINE_RE.match(line)
        if not match:
            continue
        rel_path = match.group(2)
        version_match = _VERSION_RE.search(rel_path)
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


def _latest_version(versions: list[BridgeVersion]) -> BridgeVersion:
    return versions[0]


def _highest_version(versions: list[BridgeVersion]) -> int:
    return max(version.version for version in versions)


def _find_approved_proposal(versions: list[BridgeVersion]) -> BridgeVersion:
    for version in versions[1:]:
        if version.status in {"NEW", "REVISED"}:
            return version
    raise BridgeApprovedProposalNotFoundError("Latest-GO thread has no prior NEW/REVISED proposal version")


def _extract_section(text: str, heading: str) -> str:
    pattern = re.compile(_SECTION_RE_TEMPLATE.format(heading=re.escape(heading)), re.IGNORECASE | re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def _extract_linked_specs(proposal_text: str) -> tuple[str, ...]:
    section = _extract_section(proposal_text, "Specification Links")
    specs: list[str] = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line.startswith("-"):
            continue
        item = line.lstrip("-").strip()
        item = item.strip("`").strip()
        if item and item not in specs:
            specs.append(item)
    return tuple(specs)


def _format_spec_links(specs: tuple[str, ...]) -> str:
    if not specs:
        return "- _No linked specifications found in approved proposal._"
    return "\n".join(f"- `{spec}`" for spec in specs)


def _table_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def _extract_acceptance_criteria(proposal_text: str) -> tuple[str, ...]:
    section = _extract_section(proposal_text, "Acceptance Criteria")
    criteria: list[str] = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if line.startswith("- [") or line.startswith("-"):
            criteria.append(line)
    return tuple(criteria)


def _git_lines(args: list[str], *, cwd: Path) -> tuple[str, ...]:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
    )
    if result.returncode != 0:
        return ()
    return tuple(line for line in result.stdout.splitlines() if line.strip())


def _files_changed(project_root: Path) -> tuple[str, ...]:
    return _git_lines(["diff", "--name-only", "HEAD", "--"], cwd=project_root)


def _diff_stat(project_root: Path) -> tuple[str, ...]:
    return _git_lines(["diff", "--stat", "HEAD", "--"], cwd=project_root)


def _recommend_commit_type(files_changed: tuple[str, ...]) -> tuple[str, str]:
    if not files_changed:
        return (
            "feat:",
            "Review the final diff; defaulting to feat: because this helper workflow adds a bridge capability.",
        )
    normalized = [path.replace("\\", "/") for path in files_changed]
    test_like = [path for path in normalized if path.startswith(("tests/", "platform_tests/")) or "/tests/" in path]
    doc_like = [path for path in normalized if path.endswith((".md", ".rst")) or "/docs/" in path]
    capability_like = [
        path
        for path in normalized
        if path.startswith((".claude/skills/", ".codex/skills/", "scripts/", "groundtruth-kb/src/"))
    ]
    if len(test_like) == len(normalized):
        return ("test:", "All changed paths are test paths.")
    if len(doc_like) == len(normalized):
        return ("docs:", "All changed paths are documentation or rule markdown.")
    if capability_like:
        return ("feat:", "The diff adds or changes skill, script, or platform capability surfaces.")
    return ("refactor:", "Review the final diff; changed paths do not map cleanly to a narrower type.")


def plan_report(
    slug: str,
    *,
    bridge_dir: Path | None = None,
    draft_dir: Path | None = None,
    require_latest_go: bool = True,
) -> ImplReportPlan:
    bridge_root = bridge_dir or DEFAULT_BRIDGE_DIR
    draft_root = draft_dir or DEFAULT_DRAFT_DIR
    versions = _parse_versions(slug, bridge_root)
    latest = _latest_version(versions)
    if require_latest_go and latest.status != "GO":
        raise BridgeLatestStatusError(
            f"implementation-report helper requires latest bridge status GO; got {latest.status}"
        )
    approved_proposal = _find_approved_proposal(versions)
    proposal_text = (
        approved_proposal.abs_path.read_text(encoding="utf-8") if approved_proposal.abs_path.is_file() else ""
    )
    next_version = _highest_version(versions) + 1
    report_rel = f"bridge/{slug}-{next_version:03d}.md"
    return ImplReportPlan(
        slug=slug,
        latest_status=latest.status,
        latest_path=latest.rel_path,
        next_version=next_version,
        report_path=report_rel,
        draft_path=str((draft_root / f"{slug}-{next_version:03d}.md").relative_to(PROJECT_ROOT))
        if _is_under(draft_root, PROJECT_ROOT)
        else str(draft_root / f"{slug}-{next_version:03d}.md"),
        index_line=f"NEW: {report_rel}",
        proposal_path=approved_proposal.rel_path,
        go_path=latest.rel_path,
        linked_specs=_extract_linked_specs(proposal_text),
        files_changed=_files_changed(bridge_root.parent),
        version_chain=tuple(version.rel_path for version in versions),
    )


def build_report_skeleton(slug: str, *, bridge_dir: Path | None = None) -> str:
    bridge_root = bridge_dir or DEFAULT_BRIDGE_DIR
    plan = plan_report(slug, bridge_dir=bridge_root)
    proposal_path = bridge_root.parent / plan.proposal_path
    proposal_text = proposal_path.read_text(encoding="utf-8") if proposal_path.is_file() else ""
    acceptance_criteria = _extract_acceptance_criteria(proposal_text)
    commit_type, commit_reason = _recommend_commit_type(plan.files_changed)
    diff_stat = _diff_stat(bridge_root.parent)

    spec_rows = "\n".join(
        f"| `{_table_escape(spec)}` | Record command(s) and observed result covering this linked specification. |"
        for spec in plan.linked_specs
    )
    if not spec_rows:
        spec_rows = "| _No linked specifications found_ | Reconcile before filing for verification. |"
    criteria_lines = (
        "\n".join(acceptance_criteria)
        if acceptance_criteria
        else "- [ ] Reconcile approved proposal acceptance criteria."
    )
    files_lines = (
        "\n".join(f"- `{path}`" for path in plan.files_changed)
        if plan.files_changed
        else "- _No dirty files detected by git diff._"
    )
    stat_lines = "\n".join(f"    {line}" for line in diff_stat) if diff_stat else "    _No git diff stat available._"

    return (
        "NEW\n\n"
        f"# GT-KB Bridge Implementation Report - {slug} - {plan.next_version:03d}\n\n"
        f"bridge_kind: implementation_report\n"
        f"Document: {slug}\n"
        f"Version: {plan.next_version:03d} (NEW; post-implementation report)\n"
        f"Responds to GO: {plan.go_path}\n"
        f"Approved proposal: {plan.proposal_path}\n"
        f"Recommended commit type: {commit_type}\n\n"
        "## Implementation Claim\n\n"
        "Describe the completed implementation and the user-visible or governance-visible behavior it changes.\n\n"
        "## Specification Links\n\n"
        f"{_format_spec_links(plan.linked_specs)}\n\n"
        "## Owner Decisions / Input\n\n"
        "No new owner decision is required by this implementation report. Carry forward any proposal-specific owner "
        "evidence here if applicable.\n\n"
        "## Prior Deliberations\n\n"
        f"- `{plan.proposal_path}` - approved implementation proposal carried forward.\n"
        f"- `{plan.go_path}` - Loyal Opposition GO verdict authorizing implementation.\n\n"
        "## Specification-Derived Verification Plan\n\n"
        "| Spec / governing surface | Executed verification evidence |\n"
        "| --- | --- |\n"
        f"{spec_rows}\n\n"
        "## Commands Run\n\n"
        "- `python -m pytest <target> -q --tb=short` - replace with exact command(s) run.\n\n"
        "## Observed Results\n\n"
        "- Replace with exact observed pass/fail output summaries.\n\n"
        "## Files Changed\n\n"
        f"{files_lines}\n\n"
        "## Recommended Commit Type\n\n"
        f"- Recommended commit type: `{commit_type}`\n"
        f"- Diff-stat justification: {commit_reason}\n\n"
        "```text\n"
        f"{stat_lines}\n"
        "```\n\n"
        "## Acceptance Criteria Status\n\n"
        f"{criteria_lines}\n\n"
        "## Risk And Rollback\n\n"
        "Document residual risk and the rollback path for the changed files. Bridge audit files remain append-only.\n\n"
        "## Loyal Opposition Asks\n\n"
        "1. Verify the implementation against the linked specifications and executed command evidence.\n"
        "2. Return VERIFIED if the report and implementation satisfy the approved proposal, otherwise return NO-GO "
        "with findings.\n"
    )


def scaffold_report(
    slug: str,
    *,
    bridge_dir: Path | None = None,
    draft_dir: Path | None = None,
) -> Path:
    bridge_root = bridge_dir or DEFAULT_BRIDGE_DIR
    draft_root = draft_dir or DEFAULT_DRAFT_DIR
    plan = plan_report(slug, bridge_dir=bridge_root, draft_dir=draft_root)
    draft_path = draft_root / f"{slug}-{plan.next_version:03d}.md"
    if draft_path.exists():
        raise BridgeFileAlreadyExistsError(f"Draft already exists: {draft_path}")
    draft_path.parent.mkdir(parents=True, exist_ok=True)
    draft_path.write_text(build_report_skeleton(slug, bridge_dir=bridge_root), encoding="utf-8", newline="\n")
    return draft_path


def file_report(
    slug: str,
    *,
    content: str | None = None,
    content_path: Path | None = None,
    bridge_dir: Path | None = None,
) -> Path:
    bridge_root = bridge_dir or DEFAULT_BRIDGE_DIR
    plan = plan_report(slug, bridge_dir=bridge_root)
    live_path = bridge_root.parent / plan.report_path
    index_path = bridge_root / "INDEX.md"
    if live_path.exists():
        raise BridgeFileAlreadyExistsError(f"Live bridge file already exists: {live_path}")
    if content is None and content_path is not None:
        content = content_path.read_text(encoding="utf-8")
    if content is None:
        content = build_report_skeleton(slug, bridge_dir=bridge_root)
    if not content.lstrip().startswith("NEW"):
        raise BridgeImplReportError("Implementation report content must start with NEW")

    helper = _load_bridge_propose_helper()
    hits = helper.scan_credential_hits(content)
    helper.handle_hits_abort_or_redact(content, hits, mode="abort")
    content = ensure_author_metadata(content, project_root=bridge_root.parent)

    original_index = index_path.read_text(encoding="utf-8")
    if index_path.read_text(encoding="utf-8") != original_index:
        raise BridgeIndexConflictError("bridge/INDEX.md changed before live file write")

    try:
        validate_transition(slug, "NEW", PRIME_ROLE_SLOT, bridge_root.parent)
        write_bridge_file(slug, plan.next_version, content, bridge_root.parent, require_author_metadata=False)
        insert_index_status(
            slug,
            plan.next_version,
            "NEW",
            bridge_root.parent,
            expected_index_raw=original_index,
        )
    except WriterBridgeTransitionError as exc:
        raise BridgeLatestStatusError(str(exc)) from exc
    except WriterBridgeConflictError as exc:
        if "already exists" in str(exc):
            raise BridgeFileAlreadyExistsError(str(exc)) from exc
        raise BridgeIndexConflictError(str(exc)) from exc
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
    parser.add_argument("--draft-dir", type=Path, default=DEFAULT_DRAFT_DIR)
    parser.add_argument("--content-file", type=Path)
    args = parser.parse_args(argv)

    if args.mode == "plan":
        print(
            json.dumps(
                plan_report(args.slug, bridge_dir=args.bridge_dir, draft_dir=args.draft_dir).to_dict(),
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if args.mode == "scaffold":
        path = scaffold_report(args.slug, bridge_dir=args.bridge_dir, draft_dir=args.draft_dir)
        print(str(path))
        return 0
    path = file_report(args.slug, content_path=args.content_file, bridge_dir=args.bridge_dir)
    print(str(path))
    return 0


__all__ = [
    "BridgeApprovedProposalNotFoundError",
    "BridgeDocumentNotFoundError",
    "BridgeFileAlreadyExistsError",
    "BridgeImplReportError",
    "BridgeIndexConflictError",
    "BridgeLatestStatusError",
    "build_report_skeleton",
    "file_report",
    "plan_report",
    "scaffold_report",
]


if __name__ == "__main__":
    raise SystemExit(_main())
