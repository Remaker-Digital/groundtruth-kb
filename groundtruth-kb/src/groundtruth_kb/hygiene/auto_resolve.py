"""WI-4979 report-only work-tree auto-resolve planner.

This module is the canonical dirty-state planning engine shared by the
WI-5027 finalization triage script and the WI-4979 actuator surfaces. It
performs fresh read-only git/bridge inspection, emits deterministic candidate
actions and evidence requirements, and never stages, commits, deletes, stashes,
ignores, prunes, or mutates repository state.
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

PROJECT_ROOT = Path(__file__).resolve().parents[4]

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

ACTUATOR_ACTIONS = (
    "safe_commit",
    "auto_ignore",
    "auto_drop_byte_identical",
    "manual_owner_review",
    "skip",
)

ACTION_EVIDENCE_REQUIREMENTS: dict[str, tuple[str, ...]] = {
    "safe_commit": (
        "independent terminal VERIFIED verdict or equivalent item-specific approval",
        "all implementation target_paths clean before commit",
        "pathspec-limited commit evidence",
    ),
    "auto_ignore": (
        "artifact classified as regenerated harness/runtime projection",
        "explicit ignore-rule target and rollback evidence",
        "owner/governance evidence for changing ignore behavior",
    ),
    "auto_drop_byte_identical": (
        "byte-identical duplicate content hash",
        "non-authoritative scratch classification",
        "item-specific apply evidence permitting deletion",
    ),
    "manual_owner_review": (
        "human or bridge review of the dirty path",
        "specific disposition before mutation",
    ),
    "skip": ("recent, active-session, registered, or otherwise preserved state",),
}

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


class AutoResolveError(RuntimeError):
    """Raised when fresh read-only state cannot be collected."""


TriageError = AutoResolveError


@dataclass(frozen=True)
class GitStatusEntry:
    """One parsed `git status --porcelain=v1 -z` entry."""

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
        raise AutoResolveError(f"git {' '.join(args)} failed: {detail}")
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
        if not token or len(token) < 4:
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


def _action_fields(
    action: str,
    *,
    apply_status: str,
    forbidden_operations: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "actuator_action": action,
        "apply_status": apply_status,
        "required_evidence": list(ACTION_EVIDENCE_REQUIREMENTS[action]),
        "forbidden_operations_enforced": list(forbidden_operations),
        "report_only": True,
    }


def _bridge_action(status: str | None) -> tuple[str, str, str, str, tuple[str, ...]]:
    if status == "VERIFIED":
        return (
            "blocked_commit_requires_specific_apply_evidence",
            "safe_commit",
            "blocked_missing_specific_apply_evidence",
            "terminal bridge verdict may be finalizable, but Batch A1 forbids committing another session's stale work "
            "without specific apply evidence",
            (
                "broad_bulk_status_mutation",
                "committing_another_session_stale_work_without_specific_apply_evidence",
            ),
        )
    if status in {"GO", "NO-GO", "NEW", "REVISED", "ADVISORY", "DEFERRED", "WITHDRAWN"}:
        return (
            "manual_bridge_protocol_review",
            "manual_owner_review",
            "blocked_bridge_protocol_required",
            "dirty bridge chain must be handled through the bridge protocol and append-only audit trail",
            ("broad_bulk_status_mutation",),
        )
    return (
        "blocked_unrecognized_bridge_file",
        "manual_owner_review",
        "blocked_unrecognized_bridge_status",
        "bridge file does not expose a recognized first-line status token",
        ("broad_bulk_status_mutation",),
    )


def classify_entry(root: Path, entry: GitStatusEntry) -> dict[str, Any]:
    """Classify one dirty path into a deterministic report-only action plan."""
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
        candidate_action, actuator_action, apply_status, reason, forbidden = _bridge_action(bridge_status)
        item.update(
            {
                "bucket": "bridge_thread_chain",
                "candidate_action": candidate_action,
                "reason": reason,
                "bridge_status": bridge_status,
                "thread": _bridge_thread_state(root, match.group("slug")),
                **_action_fields(
                    actuator_action,
                    apply_status=apply_status,
                    forbidden_operations=forbidden,
                ),
            }
        )
        return item

    if _is_scratch_junk(rel_path):
        item.update(
            {
                "bucket": "scratch_junk",
                "candidate_action": "blocked_untracked_file_deletion_requires_apply_evidence",
                "reason": "scratch/junk-looking path; Batch A1 forbids destructive cleanup and untracked deletion",
                **_action_fields(
                    "auto_drop_byte_identical",
                    apply_status="blocked_requires_byte_identical_apply_evidence",
                    forbidden_operations=("destructive_bulk_cleanup", "untracked_file_deletion"),
                ),
            }
        )
        return item

    if _is_harness_runtime_projection(rel_path):
        item.update(
            {
                "bucket": "harness_runtime_projection",
                "candidate_action": "blocked_auto_ignore_requires_separate_apply_evidence",
                "reason": "harness/runtime projection may be regenerated noise, but Batch A1 is report-only",
                **_action_fields(
                    "auto_ignore",
                    apply_status="blocked_requires_ignore_apply_evidence",
                    forbidden_operations=("destructive_bulk_cleanup", "untracked_file_deletion"),
                ),
            }
        )
        return item

    if _is_protected_path(rel_path):
        item.update(
            {
                "bucket": "protected_source_test_config",
                "candidate_action": "manual_review_protected_change",
                "reason": (
                    "protected source/test/config path requires bridge-scoped implementation "
                    "or separate finalization evidence"
                ),
                **_action_fields(
                    "manual_owner_review",
                    apply_status="manual_review_required",
                    forbidden_operations=(
                        "broad_bulk_status_mutation",
                        "committing_another_session_stale_work_without_specific_apply_evidence",
                    ),
                ),
            }
        )
        return item

    item.update(
        {
            "bucket": "manual_owner_review",
            "candidate_action": "manual_review_unclassified_dirty_path",
            "reason": "dirty path is outside known safe report-only buckets",
            **_action_fields(
                "manual_owner_review",
                apply_status="manual_review_required",
                forbidden_operations=(
                    "destructive_bulk_cleanup",
                    "untracked_file_deletion",
                    "committing_another_session_stale_work_without_specific_apply_evidence",
                ),
            ),
        }
    )
    return item


def build_plan(root: Path) -> dict[str, Any]:
    """Return the read-only action plan for current dirty git state."""
    root = root.resolve()
    entries = collect_git_status(root)
    items = [classify_entry(root, entry) for entry in entries]
    buckets: dict[str, list[dict[str, Any]]] = {}
    actuator_counts = {action: 0 for action in ACTUATOR_ACTIONS}
    for item in items:
        buckets.setdefault(str(item["bucket"]), []).append(item)
        action = str(item["actuator_action"])
        actuator_counts[action] = actuator_counts.get(action, 0) + 1

    bucket_summaries = [
        {
            "bucket": bucket,
            "count": len(bucket_items),
            "candidate_actions": sorted({str(item["candidate_action"]) for item in bucket_items}),
            "actuator_actions": sorted({str(item["actuator_action"]) for item in bucket_items}),
        }
        for bucket, bucket_items in sorted(buckets.items())
    ]
    return {
        "schema_version": "1",
        "generated_at": _now(),
        "root": str(root),
        "read_only": True,
        "candidate_actions_only": True,
        "classification_engine": "groundtruth_kb.hygiene.auto_resolve",
        "source_commands": {
            "git_status": "git status --porcelain=v1 -z --untracked-files=all",
            "bridge_state": "status-bearing bridge/<slug>-NNN.md first-line tokens",
        },
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "action_taxonomy": list(ACTUATOR_ACTIONS),
        "required_evidence_by_action": {
            action: list(requirements) for action, requirements in ACTION_EVIDENCE_REQUIREMENTS.items()
        },
        "counts": {
            "dirty_paths": len(items),
            "buckets": {summary["bucket"]: summary["count"] for summary in bucket_summaries},
            "actuator_actions": actuator_counts,
        },
        "bucket_summaries": bucket_summaries,
        "items": sorted(items, key=lambda item: str(item["path"])),
    }


def summarize_plan(plan: dict[str, Any]) -> dict[str, Any]:
    counts = plan.get("counts", {})
    action_counts = counts.get("actuator_actions", {}) if isinstance(counts, dict) else {}
    return {
        "dirty_paths": int(counts.get("dirty_paths", 0)) if isinstance(counts, dict) else 0,
        "actuator_actions": {
            action: int(count)
            for action, count in sorted(action_counts.items())
            if isinstance(count, int) and count > 0
        },
        "read_only": bool(plan.get("read_only", False)),
        "candidate_actions_only": bool(plan.get("candidate_actions_only", False)),
    }


def refuse_apply(plan: dict[str, Any], *, evidence_refs: tuple[str, ...] = ()) -> dict[str, Any]:
    """Return a deterministic refusal packet for live apply attempts."""
    return {
        "applied": False,
        "status": "refused",
        "reason": (
            "WI-4979 implements report-only planning and guarded refusal only; live mutation requires a later "
            "item-specific apply packet and bridge approval."
        ),
        "evidence_refs": list(evidence_refs),
        "plan_summary": summarize_plan(plan),
        "forbidden_operations": list(FORBIDDEN_OPERATIONS),
        "required_evidence_by_action": {
            action: list(requirements) for action, requirements in ACTION_EVIDENCE_REQUIREMENTS.items()
        },
    }


def format_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Worktree Finalization Triage / Auto-Resolve Plan",
        "",
        f"- generated_at: `{plan['generated_at']}`",
        f"- root: `{plan['root']}`",
        f"- dirty_paths: `{plan['counts']['dirty_paths']}`",
        "- read_only: `true`",
        "- candidate_actions_only: `true`",
        f"- classification_engine: `{plan['classification_engine']}`",
        "",
        "## Buckets",
    ]
    for summary in plan["bucket_summaries"]:
        candidates = ", ".join(f"`{action}`" for action in summary["candidate_actions"])
        actuator_actions = ", ".join(f"`{action}`" for action in summary["actuator_actions"])
        lines.append(
            f"- `{summary['bucket']}`: {summary['count']} paths; "
            f"candidate_actions: {candidates}; actuator_actions: {actuator_actions}"
        )
    lines.extend(["", "## Items"])
    for item in plan["items"]:
        lines.append(
            f"- `{item['path']}` -> `{item['bucket']}` / `{item['candidate_action']}` / "
            f"`{item['actuator_action']}` ({item['apply_status']}; {item['reason']})"
        )
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read-only WI-4979 worktree auto-resolve planner.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT, help="Repository root to inspect.")
    parser.add_argument("--format", choices=("json", "markdown"), default="json", help="Output format.")
    parser.add_argument("--apply", action="store_true", help="Refuse live apply and emit required evidence.")
    parser.add_argument("--evidence", action="append", default=(), help="Item-specific apply evidence reference.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        plan = build_plan(args.root)
    except AutoResolveError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.apply:
        refusal = refuse_apply(plan, evidence_refs=tuple(args.evidence or ()))
        sys.stdout.write(json.dumps(refusal, indent=2, sort_keys=True) + "\n")
        return 2

    if args.format == "markdown":
        sys.stdout.write(format_markdown(plan))
    else:
        sys.stdout.write(json.dumps(plan, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
