"""No-index bridge file writer used by governed bridge helpers.

The current bridge model uses dispatcher/TAFE state plus status-bearing
numbered files under ``bridge/``. This module only writes a new numbered file
after caller-side validation has passed; it never mutates aggregate queue state.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.bridge_author_metadata import (
    ensure_author_metadata,
    extract_author_metadata,
    is_synthetic_session_context_id,
)
from scripts.verdict_evidence_anchor_preflight import (
    validate_verdict_evidence_anchors,
    violation_summary,
)
from scripts.windows_subprocess import no_window_subprocess_kwargs


def _bridge_file_committed_in_git(target: Path, project_root: Path) -> bool:
    """Return True when *target* appears in git history, even if absent on disk.

    Prevents recreating a numbered bridge file at the same version as a
    previously committed but now-deleted file.  Fail-open: returns False on
    any subprocess / git error so a missing git installation or repository
    does not create a spurious hard-block.
    """
    try:
        rel = target.relative_to(project_root).as_posix()
    except ValueError:
        return False
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-1", "--", rel],
            cwd=str(project_root),
            capture_output=True,
            timeout=5,
            **no_window_subprocess_kwargs(),
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


VALID_STATUSES: frozenset[str] = frozenset(
    {"NEW", "REVISED", "GO", "NO-GO", "NO-ACTION", "VERIFIED", "ADVISORY", "DEFERRED"}
)
PRIME_STATUSES: frozenset[str] = frozenset({"NEW", "REVISED", "NO-ACTION"})
LOYAL_OPPOSITION_STATUSES: frozenset[str] = frozenset({"GO", "NO-GO", "VERIFIED", "ADVISORY"})

PRIME_ROLE_SLOT = "prime-builder"
LOYAL_OPPOSITION_ROLE_SLOT = "loyal-opposition"
PROVIDER_VERDICT_STATUSES: frozenset[str] = frozenset({"GO", "NO-GO", "VERIFIED"})
PROVIDER_VERDICT_GUARDS: tuple[Path, ...] = (
    Path(".claude/hooks/scanner-safe-writer.py"),
    Path(".claude/hooks/bridge-compliance-gate.py"),
)
_DOCUMENT_LINE_RE = re.compile(r"(?im)^\s*Document:\s*`?(?P<value>[A-Za-z0-9_.-]+)`?\s*$")
_VERSION_LINE_RE = re.compile(r"(?im)^\s*Version:\s*`?(?P<value>\d{3})\b")
_BRIDGE_KIND_RE = re.compile(r"(?im)^\s*bridge_kind:\s*`?(?P<value>[A-Za-z0-9_.-]+)`?\s*$")
_SAFE_SLUG_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
_PATCH_PATH_RE = re.compile(r"(?m)^\+\+\+ b/(?P<path>[^\r\n]+)$")


class BridgeError(Exception):
    """Base class for bridge writer errors."""


class BridgeConflictError(BridgeError):
    """Live disk state conflicts with the proposed bridge file write."""


class BridgeTransitionError(BridgeError):
    """Proposed status transition is illegal for the calling workflow."""


class BridgeEvidenceAnchorError(BridgeError):
    """A gated verdict (NO-GO/VERIFIED) cites evidence anchors that do not exist.

    Raised by ``write_bridge_file`` per WI-4520 so the helper-routed verdict
    chokepoint (post-implementation VERIFIED finalize, impl-report, revise)
    cannot persist a verdict whose cited line/string anchors are fabricated.
    """


class BridgePublicationError(BridgeError):
    """A provider-backed Loyal Opposition verdict could not be published safely."""


@dataclass(frozen=True)
class PublishedBridgeVerdict:
    document_name: str
    verdict: str
    verdict_path: str
    commit_sha: str | None
    claim_released: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "document_name": self.document_name,
            "verdict": self.verdict,
            "verdict_path": self.verdict_path,
            "commit_sha": self.commit_sha,
            "claim_released": self.claim_released,
        }


def _synthetic_session_context_id_for_content(content: str) -> str | None:
    session_context_id = extract_author_metadata(content).get("author_session_context_id")
    if is_synthetic_session_context_id(session_context_id):
        return str(session_context_id).strip().strip("`")
    return None


def _reject_synthetic_session_context_id(content: str) -> None:
    synthetic_session_context_id = _synthetic_session_context_id_for_content(content)
    if synthetic_session_context_id:
        raise BridgeTransitionError(
            "bridge artifact author_session_context_id must be a real session context id; "
            f"got synthetic harness placeholder {synthetic_session_context_id!r}. "
            "The authoring session or dispatcher must provide concrete metadata before write."
        )


def _bridge_dir(project_root: Path) -> Path:
    return project_root / "bridge"


def _first_status(content: str) -> str:
    for line in content.splitlines():
        value = line.strip()
        if value:
            return value.split(maxsplit=1)[0].upper()
    return ""


def _provider_relative_path(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError as exc:
        raise BridgePublicationError(f"provider verdict path escapes project root: {path}") from exc


def _trusted_author_content(
    content: str,
    *,
    project_root: Path,
    author_metadata: Mapping[str, object],
) -> str:
    existing = extract_author_metadata(content)
    for key, expected in author_metadata.items():
        actual = str(existing.get(key) or "").strip().strip("`")
        expected_text = str(expected or "").strip().strip("`")
        if actual and actual != expected_text:
            raise BridgePublicationError(
                f"provider verdict author metadata conflict for {key}: got {actual!r}, expected {expected_text!r}"
            )
    normalized = ensure_author_metadata(content, project_root=project_root, explicit=author_metadata)
    normalized_metadata = extract_author_metadata(normalized)
    missing = [key for key in author_metadata if not str(normalized_metadata.get(key) or "").strip()]
    if missing:
        raise BridgePublicationError(f"provider verdict is missing trusted author metadata: {', '.join(missing)}")
    return normalized


def _resolve_lo_worker(project_root: Path, *, session_id: str, harness_name: str) -> Mapping[str, object]:
    try:
        from groundtruth_kb.session.envelope import EnvelopeError, resolve_worker_role_provenance
    except ImportError as exc:
        raise BridgePublicationError("provider verdict worker-role resolver is unavailable") from exc
    try:
        provenance = resolve_worker_role_provenance(
            project_root,
            current_session_id=session_id,
            harness_name=harness_name,
        )
    except EnvelopeError as exc:
        raise BridgePublicationError(f"provider verdict worker-role provenance is unavailable: {exc}") from exc
    if provenance.get("role") != LOYAL_OPPOSITION_ROLE_SLOT:
        raise BridgePublicationError(
            "PublishBridgeVerdict requires a document-authoritative loyal-opposition worker session"
        )
    return provenance


def _claim_holder(project_root: Path, document_name: str) -> Mapping[str, object] | None:
    try:
        from scripts.bridge_work_intent_registry import current_holder

        return current_holder(document_name, project_root=project_root)
    except Exception as exc:
        raise BridgePublicationError(f"provider verdict claim lookup failed: {exc}") from exc


def _release_claim(project_root: Path, document_name: str, session_id: str) -> None:
    try:
        from scripts.bridge_work_intent_registry import release

        release(document_name, session_id, project_root=project_root)
    except Exception as exc:
        raise BridgePublicationError(f"provider verdict was published but claim release failed: {exc}") from exc


def _thread_state(project_root: Path, document_name: str) -> tuple[Path, int, str, str]:
    try:
        from scripts.bridge_thread_files import (
            parse_versioned_bridge_filename,
            status_from_bridge_file,
            versioned_bridge_files,
        )
    except ImportError as exc:
        raise BridgePublicationError("canonical bridge-thread reader is unavailable") from exc

    files = versioned_bridge_files(project_root, document_name)
    if not files:
        raise BridgePublicationError(f"bridge thread {document_name!r} has no numbered files")
    latest = files[-1]
    parsed = parse_versioned_bridge_filename(latest.name)
    latest_status = status_from_bridge_file(latest)
    if parsed is None or latest_status is None:
        raise BridgePublicationError(f"bridge thread {document_name!r} has unreadable latest state")
    latest_content = latest.read_text(encoding="utf-8", errors="replace")
    return latest, parsed[1] + 1, latest_status, latest_content


def _validate_provider_transition(*, latest_status: str, latest_content: str, verdict: str) -> None:
    bridge_kind_match = _BRIDGE_KIND_RE.search(latest_content)
    bridge_kind = bridge_kind_match.group("value").lower() if bridge_kind_match else ""
    implementation_report = bridge_kind == "implementation_report"
    if implementation_report:
        allowed = {"NO-GO", "VERIFIED"}
    elif latest_status in {"NEW", "REVISED", "NO-ACTION"}:
        allowed = {"GO", "NO-GO"}
    else:
        allowed = set()
    if verdict not in allowed:
        raise BridgeTransitionError(
            f"provider verdict {verdict} is invalid after {latest_status} (bridge_kind={bridge_kind or 'unknown'})"
        )


def _hook_block_reason(data: Mapping[str, Any]) -> str | None:
    hook_output = data.get("hookSpecificOutput")
    if isinstance(hook_output, Mapping):
        decision = str(hook_output.get("permissionDecision") or "").strip().lower()
        if decision in {"ask", "block", "deny"}:
            return str(
                hook_output.get("permissionDecisionReason")
                or hook_output.get("additionalContext")
                or f"hook decision={decision}"
            )
    decision = str(data.get("decision") or "").strip().lower()
    if decision in {"ask", "block", "deny"}:
        return str(data.get("reason") or f"hook decision={decision}")
    return None


def _run_provider_verdict_guards(
    *,
    project_root: Path,
    target: Path,
    content: str,
    session_id: str,
    author_metadata: Mapping[str, object],
) -> None:
    payload = {
        "cwd": str(project_root),
        "project_root": str(project_root),
        "session_id": session_id,
        "tool_name": "Write",
        "tool_input": {"file_path": _provider_relative_path(target, project_root), "content": content},
    }
    env = dict(os.environ)
    env.update(
        {
            "GTKB_AUTHOR_IDENTITY": str(author_metadata["author_identity"]),
            "GTKB_AUTHOR_HARNESS_ID": str(author_metadata["author_harness_id"]),
            "GTKB_AUTHOR_SESSION_CONTEXT_ID": str(author_metadata["author_session_context_id"]),
            "GTKB_AUTHOR_MODEL": str(author_metadata["author_model"]),
            "GTKB_AUTHOR_MODEL_VERSION": str(author_metadata["author_model_version"]),
            "GTKB_AUTHOR_MODEL_CONFIGURATION": str(author_metadata["author_model_configuration"]),
        }
    )
    for relative_guard in PROVIDER_VERDICT_GUARDS:
        guard = project_root / relative_guard
        if not guard.is_file():
            raise BridgePublicationError(f"provider verdict guard is missing: {relative_guard.as_posix()}")
        result = subprocess.run(
            [sys.executable, str(guard)],
            cwd=project_root,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
            env=env,
            **no_window_subprocess_kwargs(),
        )
        if result.returncode != 0:
            raise BridgePublicationError(
                f"provider verdict guard exited nonzero: {relative_guard.as_posix()} ({result.returncode})"
            )
        stdout = (result.stdout or "").strip()
        if not stdout:
            raise BridgePublicationError(f"provider verdict guard emitted empty output: {relative_guard.as_posix()}")
        try:
            data = json.loads(stdout)
        except json.JSONDecodeError as exc:
            raise BridgePublicationError(
                f"provider verdict guard emitted malformed JSON: {relative_guard.as_posix()}"
            ) from exc
        if not isinstance(data, Mapping):
            raise BridgePublicationError(f"provider verdict guard output is not an object: {relative_guard.as_posix()}")
        reason = _hook_block_reason(data)
        if reason:
            raise BridgePublicationError(f"provider verdict guard denied publication: {reason}")


def _finalize_verified_provider_verdict(
    *,
    project_root: Path,
    document_name: str,
    content: str,
    include_paths: Sequence[str],
    hunk_patch_paths: Sequence[str],
    commit_message: str,
    env: Mapping[str, str],
) -> Mapping[str, object]:
    helper = project_root / ".claude" / "skills" / "verify" / "helpers" / "write_verdict.py"
    if not helper.is_file():
        raise BridgePublicationError("canonical VERIFIED finalizer is unavailable")
    args = [
        sys.executable,
        str(helper),
        "--slug",
        document_name,
        "--finalize-verified",
        "--project-root",
        str(project_root),
        "--no-prepopulate",
        "--commit-message",
        commit_message,
    ]
    for path in include_paths:
        args.extend(("--include", path))
    for path in hunk_patch_paths:
        args.extend(("--hunk-patch", path))
    result = subprocess.run(
        args,
        cwd=project_root,
        input=content,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=900,
        check=False,
        env=dict(env),
        **no_window_subprocess_kwargs(),
    )
    if result.returncode != 0:
        raise BridgePublicationError(
            "canonical VERIFIED finalizer failed: " + (result.stderr or result.stdout or "unknown failure").strip()
        )
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise BridgePublicationError("canonical VERIFIED finalizer returned malformed JSON") from exc
    if not isinstance(data, Mapping):
        raise BridgePublicationError("canonical VERIFIED finalizer returned a non-object result")
    return data


def _modified_tracked_include_paths(project_root: Path, include_paths: Sequence[str]) -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", *include_paths],
        cwd=project_root,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
        **no_window_subprocess_kwargs(),
    )
    if result.returncode != 0:
        raise BridgePublicationError(
            "could not determine modified tracked VERIFIED include paths: "
            + (result.stderr or result.stdout or "git diff failed").strip()
        )
    return {line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()}


def _hunk_patch_covered_paths(project_root: Path, hunk_patch_paths: Sequence[str]) -> set[str]:
    covered: set[str] = set()
    root = project_root.resolve()
    for raw_path in hunk_patch_paths:
        patch = (root / raw_path).resolve()
        try:
            patch.relative_to(root)
        except ValueError as exc:
            raise BridgePublicationError(f"VERIFIED hunk patch escapes project root: {raw_path}") from exc
        try:
            content = patch.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise BridgePublicationError(f"VERIFIED hunk patch is unreadable: {raw_path}") from exc
        covered.update(match.group("path").strip() for match in _PATCH_PATH_RE.finditer(content))
    return covered


def write_bridge_file(
    document_name: str,
    version: int,
    content: str,
    project_root: Path,
    *,
    author_metadata: Mapping[str, object] | None = None,
    require_author_metadata: bool = True,
) -> Path:
    """Write ``bridge/<document>-<NNN>.md`` and re-read to verify.

    Raises ``BridgeConflictError`` if the file already exists. Status transition
    validation is owned by the caller's latest-status scan because dispatcher
    state, not this low-level writer, decides queue actionability.
    """

    if version < 1:
        raise BridgeTransitionError(f"bridge version must be positive; got {version}")
    target = _bridge_dir(project_root) / f"{document_name}-{version:03d}.md"
    if target.exists():
        raise BridgeConflictError(f"{target} already exists; refusing to overwrite")
    if _bridge_file_committed_in_git(target, project_root):
        raise BridgeConflictError(
            f"{target} exists in git history; refusing to recreate at the same version. "
            "Use the next version number to append a new bridge entry."
        )
    anchor_violations = validate_verdict_evidence_anchors(content, project_root=project_root)
    if anchor_violations:
        raise BridgeEvidenceAnchorError(
            "refusing to write verdict with fabricated evidence anchors (WI-4520): "
            + violation_summary(anchor_violations)
            + ". Fix the citation, or mark the finding [inference] / [no exact anchor] / [absent]."
        )
    content_to_write = (
        ensure_author_metadata(content, project_root=project_root, explicit=author_metadata)
        if require_author_metadata
        else content
    )
    _reject_synthetic_session_context_id(content_to_write)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("x", encoding="utf-8", newline="") as handle:
            handle.write(content_to_write)
    except FileExistsError as exc:
        raise BridgeConflictError(f"{target} already exists; refusing to overwrite") from exc
    except OSError:
        target.unlink(missing_ok=True)
        raise
    written = target.read_text(encoding="utf-8")
    if written != content_to_write:
        target.unlink(missing_ok=True)
        raise BridgeConflictError(f"post-write verification failed for {target}: content on disk differs")
    return target


def publish_lo_verdict(
    document_name: str,
    verdict: str,
    content: str,
    project_root: Path,
    *,
    session_id: str,
    harness_name: str,
    author_metadata: Mapping[str, object],
    include_paths: Sequence[str] = (),
    hunk_patch_paths: Sequence[str] = (),
    commit_message: str = "",
) -> PublishedBridgeVerdict:
    """Publish one provider-backed Loyal Opposition verdict through governed helpers."""

    root = project_root.resolve()
    normalized_verdict = verdict.strip().upper()
    if not document_name or _SAFE_SLUG_RE.fullmatch(document_name) is None:
        raise BridgePublicationError("provider verdict slug must be a non-empty canonical bridge slug")
    if normalized_verdict not in PROVIDER_VERDICT_STATUSES:
        raise BridgePublicationError(
            f"provider verdict must be one of {sorted(PROVIDER_VERDICT_STATUSES)}; got {verdict!r}"
        )
    if not session_id.strip():
        raise BridgePublicationError("provider verdict requires a concrete worker session id")

    provenance = _resolve_lo_worker(root, session_id=session_id, harness_name=harness_name)
    if provenance.get("role") != LOYAL_OPPOSITION_ROLE_SLOT:
        raise BridgePublicationError(
            "PublishBridgeVerdict requires a document-authoritative loyal-opposition worker session"
        )
    expected_harness_id = str(author_metadata.get("author_harness_id") or "").strip()
    if expected_harness_id and str(provenance.get("harness_id") or "") != expected_harness_id:
        raise BridgePublicationError("provider verdict harness metadata conflicts with worker-role provenance")

    holder = _claim_holder(root, document_name)
    if holder is None:
        raise BridgePublicationError(f"provider verdict requires an active claim for {document_name!r}")
    if str(holder.get("session_id") or "") != session_id:
        raise BridgePublicationError(f"provider verdict claim for {document_name!r} is held by another session")

    latest_path, next_version, latest_status, latest_content = _thread_state(root, document_name)
    _validate_provider_transition(
        latest_status=latest_status,
        latest_content=latest_content,
        verdict=normalized_verdict,
    )
    if _first_status(content) != normalized_verdict:
        raise BridgePublicationError("provider verdict content first status does not match the verdict argument")
    document_match = _DOCUMENT_LINE_RE.search(content)
    if document_match and document_match.group("value") != document_name:
        raise BridgePublicationError("provider verdict content Document field does not match the claimed thread")
    version_match = _VERSION_LINE_RE.search(content)
    if version_match and int(version_match.group("value")) != next_version:
        raise BridgePublicationError(
            f"provider verdict content Version must be {next_version:03d}; got {version_match.group('value')}"
        )
    latest_rel = _provider_relative_path(latest_path, root)
    if latest_rel not in content.replace("\\", "/"):
        raise BridgePublicationError(f"provider verdict must respond to current latest entry {latest_rel}")

    trusted_metadata = dict(author_metadata)
    trusted_metadata["author_session_context_id"] = session_id
    content_to_publish = _trusted_author_content(
        content,
        project_root=root,
        author_metadata=trusted_metadata,
    )
    target = _bridge_dir(root) / f"{document_name}-{next_version:03d}.md"
    _run_provider_verdict_guards(
        project_root=root,
        target=target,
        content=content_to_publish,
        session_id=session_id,
        author_metadata=trusted_metadata,
    )

    commit_sha: str | None = None
    if normalized_verdict == "VERIFIED":
        if not include_paths or not commit_message.strip():
            raise BridgePublicationError("VERIFIED publication requires include_paths and commit_message")
        modified_tracked = _modified_tracked_include_paths(root, include_paths)
        covered_by_hunks = _hunk_patch_covered_paths(root, hunk_patch_paths)
        uncovered = sorted(modified_tracked - covered_by_hunks)
        if uncovered:
            raise BridgePublicationError(
                "VERIFIED modified tracked include paths require explicit reviewed hunk patches: "
                + ", ".join(uncovered)
            )
        env = dict(os.environ)
        env.update(
            {
                "GTKB_AUTHOR_IDENTITY": str(trusted_metadata["author_identity"]),
                "GTKB_AUTHOR_HARNESS_ID": str(trusted_metadata["author_harness_id"]),
                "GTKB_AUTHOR_SESSION_CONTEXT_ID": session_id,
                "GTKB_AUTHOR_MODEL": str(trusted_metadata["author_model"]),
                "GTKB_AUTHOR_MODEL_VERSION": str(trusted_metadata["author_model_version"]),
                "GTKB_AUTHOR_MODEL_CONFIGURATION": str(trusted_metadata["author_model_configuration"]),
            }
        )
        finalization = _finalize_verified_provider_verdict(
            project_root=root,
            document_name=document_name,
            content=content_to_publish,
            include_paths=include_paths,
            hunk_patch_paths=hunk_patch_paths,
            commit_message=commit_message,
            env=env,
        )
        verdict_path = str(finalization.get("verdict_path") or _provider_relative_path(target, root))
        commit_sha = str(finalization.get("commit_sha") or "") or None
    else:
        path = write_bridge_file(
            document_name,
            next_version,
            content_to_publish,
            root,
            require_author_metadata=False,
        )
        verdict_path = _provider_relative_path(path, root)

    _release_claim(root, document_name, session_id)
    return PublishedBridgeVerdict(
        document_name=document_name,
        verdict=normalized_verdict,
        verdict_path=verdict_path,
        commit_sha=commit_sha,
        claim_released=True,
    )
