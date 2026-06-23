#!/usr/bin/env python3
"""Implementation-start target_paths preflight (WI-3380).

Compares candidate implementation file paths against the latest GO-derived
``target_paths`` glob set for a bridge thread. Read-only; reports scope drift
before implementation-start, post-implementation report filing, or hook-time
enforcement turns scope mistakes into NO-GO churn.

Per the GO at bridge/gtkb-impl-start-target-paths-preflight-005.md (WI-3380):

- Resolves the latest GO file for ``--bridge-id`` from dispatcher-backed bridge
  state plus numbered bridge files via ``bridge_entry`` /
  ``approved_files_for_go`` helpers in ``scripts.implementation_authorization``.
- Reuses ``extract_target_paths()`` from the same module to parse the canonical
  ``target_paths`` JSON metadata line on the approved proposal.
- Builds the candidate set from explicit ``--candidate-paths``, ``--git-diff``
  (running ``git diff --name-only HEAD``), or the current implementation-
  authorization packet's ``target_path_globs`` when neither is supplied.
- Reuses ``path_authorized()`` for the glob-match semantics, including the
  ``/**``-suffix recursive shortcut, so behavior matches the implementation-
  start authorization gate byte-for-byte.
- Reports ``in_scope``, ``out_of_scope``, ``unused_targets``, plus a verdict
  string. Emits JSON when ``--json`` is passed; otherwise emits a compact
  human-readable summary.

Exit codes (centralized in named constants per CQ-CONSTANTS-001):

- ``EXIT_OK`` (0)            - all candidates match at least one target glob.
- ``EXIT_NO_GO_FILE`` (3)    - no GO file in the bridge chain (no implementation
  authorization to compare against).
- ``EXIT_MISSING_TARGETS`` (4) - the approved proposal has no ``target_paths``
  metadata (or it is unparseable).
- ``EXIT_SCOPE_DRIFT`` (5)   - at least one candidate is out of scope.

The script is read-only. It MUST NOT mutate bridge files, MemBase, git state,
or authorization packets.

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from implementation_authorization import (  # noqa: E402 (sys.path setup above)
    AuthorizationError,
    approved_files_for_go,
    bridge_entry,
    extract_metadata_value,
    extract_target_paths,
    load_packet,
    normalize_relative_path,
    packet_path_for_bridge,
    path_authorized,
    project_root_from_arg,
)

EXIT_OK = 0
EXIT_NO_GO_FILE = 3
EXIT_MISSING_TARGETS = 4
EXIT_SCOPE_DRIFT = 5


VERDICT_OK = "in_scope"
VERDICT_NO_GO_FILE = "no_go_file"
VERDICT_MISSING_TARGETS = "missing_target_paths"
VERDICT_SCOPE_DRIFT = "out_of_scope_drift"


KEY_BRIDGE_ID = "bridge_id"
KEY_VERDICT = "verdict"
KEY_EXIT_CODE = "exit_code"
KEY_MESSAGE = "message"
KEY_GO_FILE = "go_file"
KEY_APPROVED_PROPOSAL_FILE = "approved_proposal_file"
KEY_TARGET_PATHS = "target_paths"
KEY_CANDIDATE_PATHS = "candidate_paths"
KEY_CANDIDATE_SOURCE = "candidate_source"
KEY_IN_SCOPE = "in_scope"
KEY_OUT_OF_SCOPE = "out_of_scope"
KEY_UNUSED_TARGETS = "unused_targets"


CANDIDATE_SOURCE_EXPLICIT = "explicit"
CANDIDATE_SOURCE_GIT_DIFF = "git_diff"
CANDIDATE_SOURCE_PACKET = "authorization_packet"
CANDIDATE_SOURCE_NONE = "none"


def _normalize_candidate(project_root: Path, path_text: str) -> str:
    """Normalize candidate paths to repo-relative POSIX form.

    Reuses normalize_relative_path() when the path resolves under project_root;
    otherwise preserves the explicit candidate syntax in forward-slash form.
    This keeps root-escape paths visibly out of scope instead of normalizing
    them into an approved repo-relative target.
    """
    try:
        return normalize_relative_path(project_root, path_text)
    except (AuthorizationError, ValueError, OSError):
        return path_text.replace("\\", "/")


def _collect_from_git_diff(project_root: Path) -> list[str]:
    """Collect candidate paths from ``git diff --name-only HEAD``.

    Returns the set of files changed (modified, added, or deleted) since the
    current HEAD. Read-only; never mutates git state.
    """
    try:
        output = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=str(project_root),
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.SubprocessError, OSError):
        return []
    return [_normalize_candidate(project_root, line.strip()) for line in output.splitlines() if line.strip()]


def _collect_from_packet(project_root: Path, bridge_id: str) -> list[str]:
    """Fallback: collect candidate paths from the current impl-auth packet.

    Tries current.json first (active packet for THIS session); falls back to
    the named-cache packet for the bridge if current.json is missing or
    points at a different bridge.
    """
    try:
        packet = load_packet(project_root)
        if packet.get("bridge_id") == bridge_id:
            return list(packet.get("target_path_globs", []))
    except (AuthorizationError, FileNotFoundError, json.JSONDecodeError, OSError):
        pass

    named = packet_path_for_bridge(project_root, bridge_id)
    if named.is_file():
        try:
            data = json.loads(named.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
        return list(data.get("target_path_globs", []))
    return []


def collect_candidates(
    project_root: Path,
    bridge_id: str,
    explicit_candidates: list[str] | None,
    use_git_diff: bool,
) -> tuple[list[str], str]:
    """Resolve the candidate set + source label.

    Priority: explicit --candidate-paths > --git-diff > current packet.
    Returns (candidates, source_label) where source_label is one of the
    CANDIDATE_SOURCE_* constants.
    """
    if explicit_candidates:
        return (
            [_normalize_candidate(project_root, p) for p in explicit_candidates],
            CANDIDATE_SOURCE_EXPLICIT,
        )
    if use_git_diff:
        return _collect_from_git_diff(project_root), CANDIDATE_SOURCE_GIT_DIFF
    packet_paths = _collect_from_packet(project_root, bridge_id)
    if packet_paths:
        return packet_paths, CANDIDATE_SOURCE_PACKET
    return [], CANDIDATE_SOURCE_NONE


def _match_against_targets(candidate: str, target_paths: list[str]) -> bool:
    """True when ``candidate`` matches at least one target glob.

    Reuses path_authorized() with a synthetic packet so glob semantics
    (fnmatch + /**-suffix shortcut) match the implementation-start
    authorization gate byte-for-byte.
    """
    normalized_candidate = candidate.replace("\\", "/")
    if (
        normalized_candidate == ".."
        or normalized_candidate.startswith("../")
        or "/../" in normalized_candidate
        or normalized_candidate.endswith("/..")
    ):
        return False
    return path_authorized({"target_path_globs": target_paths}, candidate)


def run_preflight(
    project_root: Path,
    bridge_id: str,
    explicit_candidates: list[str] | None,
    use_git_diff: bool,
) -> tuple[dict[str, Any], int]:
    """Execute the preflight against the live bridge state.

    Returns (result_dict, exit_code) where exit_code is one of the EXIT_*
    constants.
    """
    result: dict[str, Any] = {
        KEY_BRIDGE_ID: bridge_id,
        KEY_VERDICT: VERDICT_OK,
        KEY_EXIT_CODE: EXIT_OK,
        KEY_MESSAGE: "",
        KEY_GO_FILE: None,
        KEY_APPROVED_PROPOSAL_FILE: None,
        KEY_TARGET_PATHS: [],
        KEY_CANDIDATE_PATHS: [],
        KEY_CANDIDATE_SOURCE: CANDIDATE_SOURCE_NONE,
        KEY_IN_SCOPE: [],
        KEY_OUT_OF_SCOPE: [],
        KEY_UNUSED_TARGETS: [],
    }

    try:
        entry = bridge_entry(project_root, bridge_id)
        approved, go_file = approved_files_for_go(entry)
    except AuthorizationError as exc:
        result[KEY_VERDICT] = VERDICT_NO_GO_FILE
        result[KEY_EXIT_CODE] = EXIT_NO_GO_FILE
        result[KEY_MESSAGE] = str(exc)
        return result, EXIT_NO_GO_FILE

    result[KEY_GO_FILE] = go_file
    result[KEY_APPROVED_PROPOSAL_FILE] = approved

    approved_full_path = project_root / approved
    try:
        markdown = approved_full_path.read_text(encoding="utf-8")
    except OSError as exc:
        result[KEY_VERDICT] = VERDICT_MISSING_TARGETS
        result[KEY_EXIT_CODE] = EXIT_MISSING_TARGETS
        result[KEY_MESSAGE] = f"cannot read approved proposal {approved}: {exc}"
        return result, EXIT_MISSING_TARGETS

    try:
        target_paths = extract_target_paths(markdown)
    except AuthorizationError as exc:
        result[KEY_VERDICT] = VERDICT_MISSING_TARGETS
        result[KEY_EXIT_CODE] = EXIT_MISSING_TARGETS
        result[KEY_MESSAGE] = str(exc)
        return result, EXIT_MISSING_TARGETS

    scope = extract_metadata_value(markdown, {"implementation scope", "implementation_scope"})
    is_design_only = scope is not None and "design-only" in scope.lower()

    if not target_paths and not is_design_only:
        result[KEY_VERDICT] = VERDICT_MISSING_TARGETS
        result[KEY_EXIT_CODE] = EXIT_MISSING_TARGETS
        result[KEY_MESSAGE] = f"approved proposal {approved} has no target_paths metadata"
        return result, EXIT_MISSING_TARGETS

    result[KEY_TARGET_PATHS] = list(target_paths)

    candidates, source = collect_candidates(project_root, bridge_id, explicit_candidates, use_git_diff)
    result[KEY_CANDIDATE_PATHS] = candidates
    result[KEY_CANDIDATE_SOURCE] = source

    in_scope: list[str] = []
    out_of_scope: list[str] = []
    matched_targets: set[str] = set()

    for candidate in candidates:
        if _match_against_targets(candidate, target_paths):
            in_scope.append(candidate)
            for tp in target_paths:
                if path_authorized({"target_path_globs": [tp]}, candidate):
                    matched_targets.add(tp)
        else:
            out_of_scope.append(candidate)

    unused = [tp for tp in target_paths if tp not in matched_targets]
    result[KEY_IN_SCOPE] = in_scope
    result[KEY_OUT_OF_SCOPE] = out_of_scope
    result[KEY_UNUSED_TARGETS] = unused

    if out_of_scope:
        result[KEY_VERDICT] = VERDICT_SCOPE_DRIFT
        result[KEY_EXIT_CODE] = EXIT_SCOPE_DRIFT
        result[KEY_MESSAGE] = (
            f"out-of-scope candidates detected against GO {go_file}: {out_of_scope}; "
            f"approved target_paths: {target_paths}"
        )
        return result, EXIT_SCOPE_DRIFT

    if not candidates:
        result[KEY_MESSAGE] = (
            f"no candidate paths supplied (source={source}); approved target_paths from {approved}: {target_paths}"
        )
        return result, EXIT_OK

    result[KEY_MESSAGE] = (
        f"all {len(in_scope)} candidate(s) in scope against {approved}; {len(unused)} unused target(s)"
    )
    return result, EXIT_OK


def _format_human(result: dict[str, Any]) -> str:
    """Format the result as a compact human-readable summary."""
    lines = [
        f"Bridge: {result[KEY_BRIDGE_ID]}",
        f"GO file: {result[KEY_GO_FILE] or '(none)'}",
        f"Approved proposal: {result[KEY_APPROVED_PROPOSAL_FILE] or '(none)'}",
        f"Target paths ({len(result[KEY_TARGET_PATHS])}): {result[KEY_TARGET_PATHS]}",
        f"Candidate paths ({len(result[KEY_CANDIDATE_PATHS])}, source={result[KEY_CANDIDATE_SOURCE]}): "
        f"{result[KEY_CANDIDATE_PATHS]}",
        f"In scope ({len(result[KEY_IN_SCOPE])}): {result[KEY_IN_SCOPE]}",
        f"Out of scope ({len(result[KEY_OUT_OF_SCOPE])}): {result[KEY_OUT_OF_SCOPE]}",
        f"Unused targets ({len(result[KEY_UNUSED_TARGETS])}): {result[KEY_UNUSED_TARGETS]}",
        f"Verdict: {result[KEY_VERDICT]} (exit {result[KEY_EXIT_CODE]})",
        f"Message: {result[KEY_MESSAGE]}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only target_paths preflight for implementation-start scope drift.",
    )
    parser.add_argument("--bridge-id", required=True, help="Bridge document id (slug)")
    parser.add_argument(
        "--candidate-paths",
        nargs="*",
        default=None,
        help="Explicit candidate file paths (repo-relative). If omitted, falls back to --git-diff or the impl-auth packet's target_path_globs.",
    )
    parser.add_argument(
        "--git-diff",
        action="store_true",
        help="Collect candidate paths from `git diff --name-only HEAD`.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON output (default: human-readable summary).",
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help="GT-KB project root (default: auto-detect via implementation_authorization.project_root_from_arg).",
    )
    args = parser.parse_args(argv)

    project_root = project_root_from_arg(args.project_root)

    result, exit_code = run_preflight(
        project_root,
        args.bridge_id,
        args.candidate_paths,
        args.git_diff,
    )

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(_format_human(result))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
