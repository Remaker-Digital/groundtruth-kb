#!/usr/bin/env python3
"""WI-5027 read-only worktree finalization triage planner.

The planner turns current dirty git status into deterministic action buckets for
human/bridge follow-up. It never stages, commits, deletes, stashes, ignores, or
mutates repository state; every potentially-destructive or cross-session action
is reported as blocked until a later apply packet supplies specific evidence.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BRIDGE_STATUS_TOKENS = {
    "ADVISORY",
    "DEFERRED",
    "GO",
    "NEW",
    "NO-GO",
    "REVISED",
    "VERIFIED",
    "WITHDRAWN",
}

FORBIDDEN_OPERATIONS = (
    "credential_lifecycle",
    "deploy",
    "git_push_force",
    "secret_value_disclosure",
    "destructive_bulk_cleanup",
    "broad_bulk_status_mutation",
    "stash_drop",
    "branch_worktree_prune",
    "untracked_file_deletion",
    "committing_another_session_stale_work_without_specific_apply_evidence",
)

PROTECTED_PREFIXES = (
    ".claude/hooks/",
    ".claude/rules/",
    ".codex/gtkb-hooks/",
    ".github/workflows/",
    "config/",
    "groundtruth-kb/src/",
    "groundtruth-kb/tests/",
    "platform_tests/",
    "scripts/",
    "tests/",
)

PROTECTED_EXACT = {
    ".dockerignore",
    "Dockerfile",
    "Dockerfile.test",
    "Dockerfile.ui",
    "docker-compose.yml",
    "env.local",
    ".env",
    "env.staging",
    "shopify.app.toml",
}

HARNESS_RUNTIME_PREFIXES = (
    ".agent/",
    ".api-harness/",
    ".claude/session/",
    ".claude/worktrees/",
    ".cursor/gtkb-hooks/",
    ".gtkb-state/",
)

HARNESS_RUNTIME_NAMES = (
    "last-session-start.json",
    "last-user-visible-startup",
    "workstream-focus.cmd",
)

SCRATCH_NAME_MARKERS = (
    ".harness-tmp",
    ".loyal-opposition",
    ".temp_verdict_body",
    "_temp_draft",
)

BRIDGE_VERSION_RE = re.compile(r"^bridge/(?P<slug>.+)-(?P<version>\d{3})\.md$")


class TriageError(RuntimeError):
    """Raised when fresh read-only state cannot be collected."""


@dataclass(frozen=True)
class GitStatusEntry:
    status: str
    path: str
    tracked: bool

    @property
    def change_kind(self) -> str:
        if self.status == "??":
            return "untracked"
        if "D" in self.status:
            return "deleted"
        if "R" in self.status:
            return "renamed"
        if "C" in self.status:
            return "copied"
        return "modified"


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_git(root: Path, args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise TriageError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def _normalize_path(path: str) -> str:
    return path.replace("\\", "/")


def parse_porcelain_z(output: str) -> list[GitStatusEntry]:
    """Parse `git status --porcelain=v1 -z` output into stable entries."""
    entries: list[GitStatusEntry] = []
    tokens = output.split("\0")
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if not token:
            continue
        if len(token) < 4:
            continue
        status = token[:2]
        raw_path = token[3:]
        if not raw_path:
            continue
        entries.append(
            GitStatusEntry(
                status=status,
                path=_normalize_path(raw_path),
                tracked=status != "??",
            )
        )
        if "R" in status or "C" in status:
            index += 1
    return sorted(entries, key=lambda entry: entry.path)


def collect_git_status(root: Path) -> list[GitStatusEntry]:
    output = _run_git(root, ["status", "--porcelain=v1", "-z", "--untracked-files=all"])
    return parse_porcelain_z(output)


def _first_nonblank_token(path: Path) -> str | None:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    return stripped.split(maxsplit=1)[0]
    except OSError:
        return None
    return None


def _bridge_match(rel_path: str) -> re.Match[str] | None:
    return BRIDGE_VERSION_RE.match(rel_path)


def _bridge_thread_state(root: Path, slug: str) -> dict[str, Any]:
    versions: list[dict[str, Any]] = []
    for path in sorted((root / "bridge").glob(f"{slug}-[0-9][0-9][0-9].md")):
        rel = path.relative_to(root).as_posix()
        match = _bridge_match(rel)
        if not match:
            continue
        token = _first_nonblank_token(path)
        versions.append(
            {
                "path": rel,
                "version": int(match.group("version")),
                "status": token if token in BRIDGE_STATUS_TOKENS else "UNKNOWN",
            }
        )
    latest = versions[-1] if versions else None
    return {
        "slug": slug,
        "latest_status": latest["status"] if latest else None,
        "latest_version": latest["version"] if latest else None,
        "versions": versions,
    }


def _is_protected_path(rel_path: str) -> bool:
    return rel_path in PROTECTED_EXACT or rel_path.startswith(PROTECTED_PREFIXES)


def _is_harness_runtime_projection(rel_path: str) -> bool:
    if rel_path.startswith(HARNESS_RUNTIME_PREFIXES):
        return True
    name = Path(rel_path).name
    return any(name == marker or name.startswith(marker) for marker in HARNESS_RUNTIME_NAMES)


def _is_scratch_junk(rel_path: str) -> bool:
    parts = Path(rel_path).parts
    name = Path(rel_path).name
    if any(marker in parts or marker == name for marker in SCRATCH_NAME_MARKERS):
        return True
    lowered = rel_path.lower()
    return "draft" in lowered and (lowered.endswith(".tmp") or "/draft" in lowered or "\\draft" in lowered)


def _bridge_action(status: str | None) -> tuple[str, str]:
    if status == "VERIFIED":
        return (
            "blocked_commit_requires_specific_apply_evidence",
            "terminal bridge verdict may be finalizable, but Batch A1 forbids committing another session's stale work "
            "without specific apply evidence",
        )
    if status in {"GO", "NO-GO", "NEW", "REVISED", "ADVISORY", "DEFERRED", "WITHDRAWN"}:
        return (
            "manual_bridge_protocol_review",
            "dirty bridge chain must be handled through the bridge protocol and append-only audit trail",
        )
    return (
        "blocked_unrecognized_bridge_file",
        "bridge file does not expose a recognized first-line status token",
    )


def classify_entry(root: Path, entry: GitStatusEntry) -> dict[str, Any]:
    rel_path = entry.path
    item: dict[str, Any] = {
        "path": rel_path,
        "git_status": entry.status,
        "change_kind": entry.change_kind,
        "tracked": entry.tracked,
    }

    match = _bridge_match(rel_path)
    if match:
        token = _first_nonblank_token(root / rel_path)
        bridge_status = token if token in BRIDGE_STATUS_TOKENS else "UNKNOWN"
        action, reason = _bridge_action(bridge_status)
        item.update(
            {
                "bucket": "bridge_thread_chain",
                "candidate_action": action,
                "reason": reason,
                "bridge_status": bridge_status,
                "thread": _bridge_thread_state(root, match.group("slug")),
                "forbidden_operations_enforced": [
                    "broad_bulk_status_mutation",
                    "committing_another_session_stale_work_without_specific_apply_evidence",
                ],
            }
        )
        return item

    if _is_scratch_junk(rel_path):
        item.update(
            {
                "bucket": "scratch_junk",
                "candidate_action": "blocked_untracked_file_deletion_requires_apply_evidence",
                "reason": "scratch/junk-looking path; Batch A1 forbids destructive cleanup and untracked deletion",
                "forbidden_operations_enforced": [
                    "destructive_bulk_cleanup",
                    "untracked_file_deletion",
                ],
            }
        )
        return item

    if _is_harness_runtime_projection(rel_path):
        item.update(
            {
                "bucket": "harness_runtime_projection",
                "candidate_action": "blocked_auto_ignore_requires_separate_apply_evidence",
                "reason": "harness/runtime projection may be regenerated noise, but Batch A1 is report-only",
                "forbidden_operations_enforced": [
                    "destructive_bulk_cleanup",
                    "untracked_file_deletion",
                ],
            }
        )
        return item

    if _is_protected_path(rel_path):
        item.update(
            {
                "bucket": "protected_source_test_config",
                "candidate_action": "manual_review_protected_change",
                "reason": "protected source/test/config path requires bridge-scoped implementation or separate finalization evidence",
                "forbidden_operations_enforced": [
                    "broad_bulk_status_mutation",
                    "committing_another_session_stale_work_without_specific_apply_evidence",
                ],
            }
        )
        return item

    item.update(
        {
            "bucket": "manual_owner_review",
            "candidate_action": "manual_review_unclassified_dirty_path",
            "reason": "dirty path is outside known safe report-only buckets",
            "forbidden_operations_enforced": [
                "destructive_bulk_cleanup",
                "untracked_file_deletion",
                "committing_another_session_stale_work_without_specific_apply_evidence",
            ],
        }
    )
    return item


def build_plan(root: Path) -> dict[str, Any]:
    root = root.resolve()
    entries = collect_git_status(root)
    items = [classify_entry(root, entry) for entry in entries]
    buckets: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        buckets.setdefault(str(item["bucket"]), []).append(item)

    bucket_summaries = [
        {
            "bucket": bucket,
            "count": len(bucket_items),
            "candidate_actions": sorted({str(item["candidate_action"]) for item in bucket_items}),
        }
        for bucket, bucket_items in sorted(buckets.items())
    ]
    return {
        "generated_at": _now(),
        "root": str(root),
        "read_only": True,
        "candidate_actions_only": True,
        "source_commands": {
            "git_status": "git status --porcelain=v1 -z --untracked-files=all",
            "bridge_state": "status-bearing bridge/<slug>-NNN.md first-line tokens",
        },
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "counts": {
            "dirty_paths": len(items),
            "buckets": {summary["bucket"]: summary["count"] for summary in bucket_summaries},
        },
        "bucket_summaries": bucket_summaries,
        "items": sorted(items, key=lambda item: str(item["path"])),
    }


def format_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Worktree Finalization Triage",
        "",
        f"- generated_at: `{plan['generated_at']}`",
        f"- root: `{plan['root']}`",
        f"- dirty_paths: `{plan['counts']['dirty_paths']}`",
        "- read_only: `true`",
        "- candidate_actions_only: `true`",
        "",
        "## Buckets",
    ]
    for summary in plan["bucket_summaries"]:
        actions = ", ".join(f"`{action}`" for action in summary["candidate_actions"])
        lines.append(f"- `{summary['bucket']}`: {summary['count']} paths; actions: {actions}")
    lines.extend(["", "## Items"])
    for item in plan["items"]:
        lines.append(f"- `{item['path']}` -> `{item['bucket']}` / `{item['candidate_action']}` ({item['reason']})")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only WI-5027 worktree finalization triage planner.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT, help="Repository root to inspect.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Output format.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        plan = build_plan(args.root)
    except TriageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "markdown":
        sys.stdout.write(format_markdown(plan))
    else:
        sys.stdout.write(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
