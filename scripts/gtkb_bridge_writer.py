"""No-index bridge file writer used by governed bridge helpers.

The current bridge model uses dispatcher/TAFE state plus status-bearing
numbered files under ``bridge/``. This module only writes a new numbered file
after caller-side validation has passed; it never mutates aggregate queue state.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
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


# WI-5935 Slice E: closing instruction carried by every filed bridge artifact.
_CLOSING_INSTRUCTION = "When you are finished working, close your session envelope by invoking ::wrap."


VALID_STATUSES: frozenset[str] = frozenset(
    {"NEW", "REVISED", "GO", "NO-GO", "NO-ACTION", "VERIFIED", "ADVISORY", "DEFERRED", "WITHDRAWN"}
)
PRIME_STATUSES: frozenset[str] = frozenset({"NEW", "REVISED", "NO-ACTION"})
LOYAL_OPPOSITION_STATUSES: frozenset[str] = frozenset({"GO", "NO-GO", "VERIFIED", "ADVISORY"})
ENVELOPE_RESPONDER_BY_STATUS: Mapping[str, str] = {
    # The envelope names the next responder, not the author of the artifact.
    "NEW": "lo",
    "REVISED": "lo",
    "NO-ACTION": "lo",
    # ADVISORY is Loyal-Opposition-authored and Prime-actionable for interactive
    # disposition per the file-bridge protocol. Its absence here left the Loyal
    # Opposition advisory channel with no governed filing path at all.
    "ADVISORY": "pb",
    "GO": "pb",
    "NO-GO": "pb",
    "VERIFIED": "pb",
}
ENVELOPE_ACTIVITY_VALUES: frozenset[str] = frozenset({"ops", "deliberation", "build", "test", "spec", "project"})
LO_ENVELOPE_BRIDGE_KINDS: frozenset[str] = frozenset({"lo_verdict", "loyal_opposition_review", "verification_verdict"})

PRIME_ROLE_SLOT = "prime-builder"
LOYAL_OPPOSITION_ROLE_SLOT = "loyal-opposition"
PROVIDER_VERDICT_STATUSES: frozenset[str] = frozenset({"GO", "NO-GO", "VERIFIED"})
PROVIDER_VERDICT_STATUS_MISMATCH_CODE = "GTKB_PROVIDER_VERDICT_STATUS_MISMATCH"
PROVIDER_RUNTIME_MODEL_FIELDS: tuple[str, ...] = (
    "author_model",
    "author_model_version",
    "author_model_configuration",
)
PROVIDER_VERDICT_GUARDS: tuple[Path, ...] = (
    Path(".claude/hooks/scanner-safe-writer.py"),
    Path(".claude/hooks/bridge-compliance-gate.py"),
)
_DOCUMENT_LINE_RE = re.compile(r"(?im)^\s*Document:\s*`?(?P<value>[A-Za-z0-9_.-]+)`?\s*$")
_VERSION_LINE_RE = re.compile(r"(?im)^\s*Version:\s*`?(?P<value>\d{3})\b")
_BRIDGE_KIND_RE = re.compile(r"(?im)^\s*bridge_kind:\s*`?(?P<value>[A-Za-z0-9_.-]+)`?\s*$")
_ENVELOPE_INIT_RE = re.compile(r"^::init gtkb (?P<role>pb|lo)$")
_ENVELOPE_OPEN_RE = re.compile(r"^::open (?P<activity>ops|deliberation|build|test|spec|project)$")
_SAFE_SLUG_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
_PATCH_PATH_RE = re.compile(r"(?m)^(?:---|\+\+\+) (?P<path>[^\r\n]+)$")
_DIFF_GIT_PATH_RE = re.compile(r"(?m)^diff --git a/(?P<old>.*?) b/(?P<new>[^\r\n]*)$")
_PATCH_SHA256_DECL_RE = re.compile(r"(?i)\b(?:patch\s+)?sha-?256\b[^0-9a-f]*(?P<value>[0-9a-f]{64})")
_PATCH_SIZE_DECL_RE = re.compile(r"(?i)\b(?:patch\s+)?size\b[^0-9]*(?P<value>\d+)\s*(?:bytes?)?")


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


class BridgeComplianceError(BridgeError):
    """Bridge compliance audit denied or could not evaluate candidate content."""


class BridgeEnvelopeError(BridgeError):
    """Bridge artifact-head envelope lines are missing, malformed, or inconsistent."""


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


def _relative_to_project(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _bridge_compliance_gate_path(project_root: Path) -> Path:
    local_gate = project_root / ".claude" / "hooks" / "bridge-compliance-gate.py"
    if local_gate.is_file():
        return local_gate
    for parent in Path(__file__).resolve().parents:
        gate = parent / ".claude" / "hooks" / "bridge-compliance-gate.py"
        if gate.is_file():
            return gate
    raise BridgeComplianceError("bridge-compliance-gate.py is unavailable; refusing helper-managed bridge write")


def run_bridge_compliance_audit(
    *,
    file_path: Path,
    content: str,
    project_root: Path,
) -> dict[str, object]:
    """Run the bridge-compliance gate in audit mode for in-memory content."""

    gate_path = _bridge_compliance_gate_path(project_root)
    payload = {
        "cwd": str(project_root.resolve()),
        "tool_input": {
            "file_path": _relative_to_project(file_path, project_root),
            "content": content,
        },
    }
    with tempfile.TemporaryDirectory(prefix="gtkb-bridge-compliance-") as tmp:
        audit_output = Path(tmp) / "audit.json"
        result = subprocess.run(
            [
                sys.executable,
                str(gate_path),
                "--audit-only",
                "--audit-output",
                str(audit_output),
            ],
            cwd=project_root,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
            **no_window_subprocess_kwargs(),
        )
        if result.returncode != 0:
            raise BridgeComplianceError(
                "bridge-compliance audit failed to execute: "
                f"returncode={result.returncode} stdout={result.stdout!r} stderr={result.stderr!r}"
            )
        try:
            audit = json.loads(audit_output.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise BridgeComplianceError("bridge-compliance audit did not produce readable JSON") from exc
    if audit.get("decision") != "pass":
        reason = audit.get("reason") or "bridge-compliance audit denied the candidate bridge file"
        raise BridgeComplianceError(str(reason))
    return audit


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


def _bridge_kind(content: str) -> str:
    match = _BRIDGE_KIND_RE.search(content)
    return match.group("value").lower() if match else ""


def default_bridge_envelope_activity(content: str, status: str) -> str:
    """Return the Slice B default activity for a status-bearing bridge artifact."""

    normalized_status = status.strip().upper()
    if normalized_status in ENVELOPE_RESPONDER_BY_STATUS:
        return "build"
    bridge_kind = _bridge_kind(content)
    if bridge_kind in LO_ENVELOPE_BRIDGE_KINDS:
        return "test"
    return "build"


def _validate_activity(activity: str) -> str:
    normalized = activity.strip()
    if normalized not in ENVELOPE_ACTIVITY_VALUES:
        allowed = ", ".join(sorted(ENVELOPE_ACTIVITY_VALUES))
        raise BridgeEnvelopeError(f"invalid bridge envelope activity {activity!r}; expected one of: {allowed}")
    return normalized


def _bridge_envelope_indices(lines: Sequence[str]) -> tuple[list[int], list[int]]:
    init_indices: list[int] = []
    open_indices: list[int] = []
    for idx, line in enumerate(lines[1:], start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        if stripped.startswith("::init"):
            init_indices.append(idx)
        if stripped.startswith("::open"):
            open_indices.append(idx)
    return init_indices, open_indices


def _validated_existing_envelope(
    *,
    lines: Sequence[str],
    status: str,
    expected_role: str,
    expected_activity: str,
) -> set[int]:
    init_indices, open_indices = _bridge_envelope_indices(lines)
    if not init_indices and not open_indices:
        return set()
    if len(init_indices) != 1 or len(open_indices) != 1:
        raise BridgeEnvelopeError(
            "bridge artifact-head envelope must contain exactly one ::init line and exactly one ::open line"
        )
    init_idx = init_indices[0]
    open_idx = open_indices[0]
    if open_idx != init_idx + 1:
        raise BridgeEnvelopeError("bridge artifact-head envelope lines must be adjacent")

    init_line = lines[init_idx].strip()
    open_line = lines[open_idx].strip()
    init_match = _ENVELOPE_INIT_RE.fullmatch(init_line)
    if init_match is None:
        raise BridgeEnvelopeError(f"malformed bridge envelope ::init line for {status}: {init_line!r}")
    actual_role = init_match.group("role")
    if actual_role != expected_role:
        raise BridgeEnvelopeError(
            f"bridge envelope responder-role mismatch for {status}: got {actual_role!r}, expected {expected_role!r}"
        )

    open_match = _ENVELOPE_OPEN_RE.fullmatch(open_line)
    if open_match is None:
        raise BridgeEnvelopeError(f"malformed or invalid bridge envelope ::open line for {status}: {open_line!r}")
    actual_activity = open_match.group("activity")
    if actual_activity != expected_activity:
        raise BridgeEnvelopeError(
            f"bridge envelope activity mismatch for {status}: got {actual_activity!r}, expected {expected_activity!r}"
        )
    return {init_idx, open_idx}


def validate_bridge_envelope_head(
    content: str,
    *,
    require_dispatchable: bool = False,
    activity: str | None = None,
) -> None:
    """Validate bridge artifact-head envelope lines without modifying content."""

    lines = content.splitlines()
    if not lines:
        return
    status = _first_status(content)
    if status not in VALID_STATUSES:
        return

    init_indices, open_indices = _bridge_envelope_indices(lines)
    expected_role = ENVELOPE_RESPONDER_BY_STATUS.get(status)
    if expected_role is None:
        if init_indices or open_indices:
            raise BridgeEnvelopeError(f"bridge status {status} has no formal responder-role envelope mapping")
        return

    selected_activity = _validate_activity(activity or default_bridge_envelope_activity(content, status))
    if not init_indices and not open_indices:
        if require_dispatchable:
            raise BridgeEnvelopeError(
                f"dispatchable bridge status {status} requires line 2 '::init gtkb {expected_role}' "
                f"and line 3 '::open {selected_activity}'"
            )
        return
    kept = _validated_existing_envelope(
        lines=lines,
        status=status,
        expected_role=expected_role,
        expected_activity=selected_activity,
    )
    if require_dispatchable and kept != {1, 2}:
        raise BridgeEnvelopeError("bridge artifact-head envelope must occupy fixed lines 2 and 3")


def normalize_bridge_envelope_head(content: str, *, activity: str | None = None) -> str:
    """Materialize or canonicalize the Slice B bridge artifact-head envelope."""

    lines = content.splitlines()
    if not lines:
        return content
    status = _first_status(content)
    if status not in VALID_STATUSES:
        return content

    init_indices, open_indices = _bridge_envelope_indices(lines)
    expected_role = ENVELOPE_RESPONDER_BY_STATUS.get(status)
    if expected_role is None:
        if init_indices or open_indices or activity is not None:
            raise BridgeEnvelopeError(f"bridge status {status} has no formal responder-role envelope mapping")
        return content

    selected_activity = _validate_activity(activity or default_bridge_envelope_activity(content, status))
    if len(init_indices) != 1 or len(open_indices) != 1:
        remove_indices = set(init_indices) | set(open_indices)
    else:
        remove_indices = _validated_existing_envelope(
            lines=lines,
            status=status,
            expected_role=expected_role,
            expected_activity=selected_activity,
        )
    body_lines = [line.rstrip("\r") for idx, line in enumerate(lines) if idx not in remove_indices]
    envelope_lines = [f"::init gtkb {expected_role}", f"::open {selected_activity}"]
    normalized_lines = [body_lines[0], *envelope_lines, *body_lines[1:]]
    trailing_newline = "\n" if content.endswith(("\n", "\r")) else ""
    return "\n".join(normalized_lines) + trailing_newline


def _provider_relative_path(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError as exc:
        raise BridgePublicationError(f"provider verdict path escapes project root: {path}") from exc


def _normalize_provider_runtime_model_metadata(
    content: str,
    *,
    author_metadata: Mapping[str, object],
) -> str:
    trusted_values: dict[str, str] = {}
    for key in PROVIDER_RUNTIME_MODEL_FIELDS:
        value = str(author_metadata.get(key) or "").strip().strip("`")
        if not value:
            raise BridgePublicationError(f"provider verdict is missing trusted author metadata: {key}")
        trusted_values[key] = value

    lines = content.split("\n")
    seen: set[str] = set()
    for idx, line in enumerate(lines):
        match = re.match(r"^(author_[a-z0-9_]+):", line.strip("\n"), re.IGNORECASE)
        if match:
            key = match.group(1).lower()
            if key in trusted_values:
                lines[idx] = f"{key}: {trusted_values[key]}"
                seen.add(key)
    missing_keys = [key for key in PROVIDER_RUNTIME_MODEL_FIELDS if key not in seen]
    if missing_keys:
        insertion_at = 0
        for idx, line in enumerate(lines):
            if re.match(r"^author_[a-z0-9_]+:", line.strip("\n"), re.IGNORECASE):
                insertion_at = idx + 1
        for offset, key in enumerate(missing_keys):
            lines.insert(insertion_at + offset, f"{key}: {trusted_values[key]}")
    return "\n".join(lines)


def _trusted_author_content(
    content: str,
    *,
    project_root: Path,
    author_metadata: Mapping[str, object],
) -> str:
    content = _normalize_provider_runtime_model_metadata(content, author_metadata=author_metadata)
    existing = extract_author_metadata(content)
    for key, expected in author_metadata.items():
        if key in PROVIDER_RUNTIME_MODEL_FIELDS:
            continue
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


def _release_claim(
    project_root: Path,
    document_name: str,
    session_id: str,
    *,
    claim_registry: Any | None = None,
) -> None:
    try:
        if claim_registry is None:
            from scripts.bridge_work_intent_registry import release
        else:
            release = claim_registry.release

        release(document_name, session_id, project_root=project_root)
    except Exception as exc:
        raise BridgePublicationError(f"bridge publication claim release failed: {exc}") from exc


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
) -> tuple[dict[str, object], ...]:
    evidence: list[dict[str, object]] = []
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
            raise BridgePublicationError(f"bridge publication guard denied publication: {reason}")
        evidence.append({"guard": relative_guard.as_posix(), "result": dict(data)})
    return tuple(evidence)


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
    helper = project_root / ".claude" / "skills" / "gtkb-verify" / "helpers" / "write_verdict.py"
    if not helper.is_file():
        # WI-5661: fall back to the pre-rename skill dir for backward compatibility
        # (WI-5651 renamed verify -> gtkb-verify; a future re-rename must not re-break this).
        _legacy = project_root / ".claude" / "skills" / "verify" / "helpers" / "write_verdict.py"
        if _legacy.is_file():
            helper = _legacy
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


def _patch_path_token(path_text: str) -> str | None:
    path_text = path_text.split("\t", 1)[0].strip()
    if path_text == "/dev/null":
        return None
    if path_text.startswith(("a/", "b/")):
        path_text = path_text[2:]
    return path_text.replace("\\", "/")


def _patch_header_text(raw_line: bytes, raw_path: str) -> str:
    try:
        return raw_line.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BridgePublicationError(f"VERIFIED hunk patch has a non-UTF-8 path header: {raw_path}") from exc


def _patch_paths_from_bytes(patch_bytes: bytes, raw_path: str) -> set[str]:
    paths: set[str] = set()
    for raw_line in patch_bytes.splitlines():
        if raw_line.startswith(b"diff --git "):
            line = _patch_header_text(raw_line, raw_path)
            match = _DIFF_GIT_PATH_RE.match(line)
            if match is None:
                continue
            for group_name in ("old", "new"):
                path_text = _patch_path_token(match.group(group_name))
                if path_text is not None:
                    paths.add(path_text)
            continue
        if not raw_line.startswith((b"--- ", b"+++ ")):
            continue
        line = _patch_header_text(raw_line, raw_path)
        match = _PATCH_PATH_RE.match(line)
        if match is not None:
            path_text = _patch_path_token(match.group("path"))
            if path_text is not None:
                paths.add(path_text)
    return paths


def _section_body(text: str, heading: str) -> str:
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.IGNORECASE | re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        return ""
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def _declared_hunk_path(line: str) -> str | None:
    if not re.match(r"(?i)^\s*[-*]?\s*hunk patch\s*:", line):
        return None
    value = line.split(":", 1)[1].strip()
    code_match = re.search(r"`([^`]+)`", value)
    if code_match:
        return code_match.group(1).replace("\\", "/")
    return value.split()[0].replace("\\", "/") if value.split() else None


def _hunk_patch_metadata_from_report(report_text: str) -> dict[str, dict[str, object]]:
    section = _section_body(report_text, "Hunk Patch Evidence")
    if not section:
        return {}
    metadata: dict[str, dict[str, object]] = {}
    current_path: str | None = None
    for line in section.splitlines():
        declared_path = _declared_hunk_path(line)
        if declared_path:
            current_path = declared_path.lstrip("./")
            metadata.setdefault(current_path, {})
            continue
        if current_path is None:
            continue
        sha_match = _PATCH_SHA256_DECL_RE.search(line)
        if sha_match:
            metadata[current_path]["sha256"] = sha_match.group("value").lower()
            continue
        size_match = _PATCH_SIZE_DECL_RE.search(line)
        if size_match:
            metadata[current_path]["size_bytes"] = int(size_match.group("value"))
    return metadata


def _validate_hunk_patch_metadata(
    *,
    raw_path: str,
    patch_rel_path: str,
    patch_bytes: bytes,
    report_metadata: Mapping[str, Mapping[str, object]],
) -> None:
    declared = report_metadata.get(patch_rel_path, {})
    actual_sha = hashlib.sha256(patch_bytes).hexdigest()
    declared_sha = declared.get("sha256")
    if declared_sha is not None and str(declared_sha).lower() != actual_sha:
        raise BridgePublicationError(
            f"VERIFIED hunk patch SHA-256 mismatch for {raw_path}: declared {declared_sha}, actual {actual_sha}"
        )
    actual_size = len(patch_bytes)
    declared_size = declared.get("size_bytes")
    if declared_size is not None and int(declared_size) != actual_size:
        raise BridgePublicationError(
            f"VERIFIED hunk patch size mismatch for {raw_path}: declared {declared_size}, actual {actual_size}"
        )


def _hunk_patch_apply_check(
    project_root: Path, patch: Path, *, reverse: bool = False
) -> subprocess.CompletedProcess[str]:
    args = ["git", "apply", "--binary", "--check"]
    if reverse:
        args.append("--reverse")
    args.append(str(patch))
    return subprocess.run(
        args,
        cwd=project_root,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=False,
        **no_window_subprocess_kwargs(),
    )


def _assert_hunk_patch_git_applyable(project_root: Path, patch: Path, raw_path: str) -> None:
    forward = _hunk_patch_apply_check(project_root, patch)
    if forward.returncode == 0:
        return
    reverse = _hunk_patch_apply_check(project_root, patch, reverse=True)
    if reverse.returncode == 0:
        return
    failure = (forward.stderr or forward.stdout or reverse.stderr or reverse.stdout).strip()
    raise BridgePublicationError(f"VERIFIED hunk patch is not Git-applyable: {raw_path}: {failure}")


def _hunk_patch_covered_paths(
    project_root: Path,
    hunk_patch_paths: Sequence[str],
    *,
    latest_content: str = "",
) -> set[str]:
    covered: set[str] = set()
    root = project_root.resolve()
    report_metadata = _hunk_patch_metadata_from_report(latest_content)
    for raw_path in hunk_patch_paths:
        patch = (root / raw_path).resolve()
        try:
            patch_rel_path = patch.relative_to(root).as_posix()
        except ValueError as exc:
            raise BridgePublicationError(f"VERIFIED hunk patch escapes project root: {raw_path}") from exc
        try:
            patch_bytes = patch.read_bytes()
        except OSError as exc:
            raise BridgePublicationError(f"VERIFIED hunk patch is unreadable: {raw_path}") from exc
        _validate_hunk_patch_metadata(
            raw_path=raw_path,
            patch_rel_path=patch_rel_path,
            patch_bytes=patch_bytes,
            report_metadata=report_metadata,
        )
        covered.update(_patch_paths_from_bytes(patch_bytes, raw_path))
        _assert_hunk_patch_git_applyable(root, patch, raw_path)
    return covered


@dataclass(frozen=True)
class _PendingBridgePublication:
    capability: str
    capability_hash: str
    target_path: str
    session_id: str
    content_digest: str
    document_name: str
    version: int
    status: str


_PENDING_BRIDGE_PUBLICATIONS: dict[str, _PendingBridgePublication] = {}


def _pending_publication_sidecar_path(target: Path, project_root: Path) -> Path:
    try:
        relative = target.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError as exc:
        raise BridgePublicationError(f"pending bridge target escapes project root: {target}") from exc
    digest = hashlib.sha256(relative.encode("utf-8")).hexdigest()[:16]
    return project_root / ".gtkb-state" / "bridge-publication-pending" / f"{target.stem}-{digest}.json"


def _write_pending_publication_sidecar(
    publication: _PendingBridgePublication,
    *,
    target: Path,
    project_root: Path,
) -> Path:
    """Persist secret-free recovery context before the bridge file is created."""

    sidecar = _pending_publication_sidecar_path(target, project_root)
    payload = {
        "schema_version": 1,
        "capability_hash": publication.capability_hash,
        "content_digest": publication.content_digest,
        "created_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "document_name": publication.document_name,
        "session_id": publication.session_id,
        "status": publication.status,
        "target_path": publication.target_path,
        "version": publication.version,
    }
    sidecar.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(prefix=sidecar.name + ".", suffix=".tmp", dir=sidecar.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, sidecar)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return sidecar


def _load_pending_publication_sidecar(target: Path, project_root: Path) -> dict[str, object] | None:
    sidecar = _pending_publication_sidecar_path(target, project_root)
    if not sidecar.is_file():
        return None
    try:
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        raise BridgePublicationError(f"pending bridge publication sidecar is unreadable: {sidecar}") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise BridgePublicationError(f"pending bridge publication sidecar is malformed: {sidecar}")
    expected = target.resolve().relative_to(project_root.resolve()).as_posix()
    if str(payload.get("target_path") or "") != expected:
        raise BridgePublicationError("pending bridge publication sidecar target binding mismatch")
    document_name = str(payload.get("document_name") or "")
    status = str(payload.get("status") or "")
    session_id = str(payload.get("session_id") or "")
    capability_hash = str(payload.get("capability_hash") or "")
    content_digest = str(payload.get("content_digest") or "")
    version = payload.get("version")
    if (
        not document_name
        or status not in VALID_STATUSES
        or not session_id
        or not re.fullmatch(r"sha256:[0-9a-f]{64}", capability_hash)
        or not re.fullmatch(r"sha256:[0-9a-f]{64}", content_digest)
        or not isinstance(version, int)
        or version < 1
        or expected != f"bridge/{document_name}-{version:03d}.md"
    ):
        raise BridgePublicationError("pending bridge publication sidecar bindings are malformed")
    return payload


def _delete_pending_publication_sidecar(target: Path, project_root: Path) -> None:
    _pending_publication_sidecar_path(target, project_root).unlink(missing_ok=True)


def _registry_publication_enabled(project_root: Path) -> bool:
    canonical = project_root / "config" / "registry" / "sot-artifacts.toml"
    packaged = (
        project_root
        / "groundtruth-kb"
        / "src"
        / "groundtruth_kb"
        / "context"
        / "registries"
        / "v1"
        / "config"
        / "registry"
        / "sot-artifacts.toml"
    )
    if not canonical.exists():
        return False
    missing = [path for path in (packaged, project_root / "groundtruth.db") if not path.is_file()]
    if missing:
        rendered = ", ".join(_relative_to_project(path, project_root) for path in missing)
        raise BridgePublicationError(f"configured registry publication control plane is incomplete: {rendered}")
    return True


def _publication_compliance_digest(
    *,
    audit: Mapping[str, object],
    guards: Sequence[Mapping[str, object]],
) -> str:
    payload = json.dumps(
        {"bridge_compliance": dict(audit), "guards": [dict(item) for item in guards]},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _publication_author_session(content: str) -> tuple[str, Mapping[str, object]]:
    metadata = extract_author_metadata(content)
    session_id = str(metadata.get("author_session_context_id") or "").strip().strip(chr(96))
    if not session_id:
        raise BridgePublicationError("bridge publication requires author_session_context_id")
    return session_id, metadata


def _compensate_publication(
    *,
    publication: _PendingBridgePublication,
    project_root: Path,
    reason: str,
) -> None:
    try:
        from groundtruth_kb.project.registry_control_plane import compensate_bridge_publication

        compensate_bridge_publication(
            capability=publication.capability,
            target_path=publication.target_path,
            session_id=publication.session_id,
            reason=reason,
            changed_by="bridge-publication-writer",
            project_root=project_root,
        )
        _delete_pending_publication_sidecar(
            project_root / publication.target_path,
            project_root,
        )
    except Exception as exc:
        raise BridgePublicationError(
            "BRIDGE_PUBLICATION_REPAIR_REQUIRED: compensation could not restore the "
            f"aggregate preimage; file and claim are retained: {exc}"
        ) from exc


def finalize_pending_bridge_publication(target: Path, project_root: Path) -> None:
    """Release the exact claim only after an outer VERIFIED commit succeeds."""

    key = str(target.resolve())
    publication = _PENDING_BRIDGE_PUBLICATIONS.get(key)
    if publication is None:
        pending = _load_pending_publication_sidecar(target, project_root)
        if pending is not None and _registry_publication_enabled(project_root):
            from groundtruth_kb.project.registry_control_plane import recover_bridge_publication

            session_id = str(pending.get("session_id") or "")
            receipt = recover_bridge_publication(
                target_path=str(pending.get("target_path") or ""),
                session_id=session_id,
                mode="finalize",
                changed_by="bridge-publication-writer",
                change_reason="Recover interrupted bridge publication after outer commit",
                expected_capability_hash=str(pending.get("capability_hash") or ""),
                expected_content_digest=str(pending.get("content_digest") or ""),
                expected_document_name=str(pending.get("document_name") or ""),
                expected_version=int(pending.get("version") or 0),
                expected_status=str(pending.get("status") or ""),
                project_root=project_root,
            )
            document_name = Path(receipt.target_path).name.rsplit("-", 1)[0]
            _release_claim(project_root, document_name, session_id)
            try:
                _delete_pending_publication_sidecar(target, project_root)
            except OSError:
                pass
            return
        content = target.read_text(encoding="utf-8")
        session_id, _ = _publication_author_session(content)
        holder = _claim_holder(project_root, target.name.rsplit("-", 1)[0])
        if holder is not None and str(holder.get("session_id") or "") == session_id:
            _release_claim(project_root, target.name.rsplit("-", 1)[0], session_id)
        return
    document_name = Path(publication.target_path).name.rsplit("-", 1)[0]
    _release_claim(project_root, document_name, publication.session_id)
    try:
        _delete_pending_publication_sidecar(target, project_root)
    except OSError:
        pass
    _PENDING_BRIDGE_PUBLICATIONS.pop(key, None)


def rollback_pending_bridge_publication(
    target: Path,
    project_root: Path,
    *,
    reason: str,
) -> None:
    """Compensate an uncommitted VERIFIED verdict while retaining its claim."""

    key = str(target.resolve())
    publication = _PENDING_BRIDGE_PUBLICATIONS.get(key)
    if publication is None:
        if not _registry_publication_enabled(project_root):
            target.unlink(missing_ok=True)
            return
        pending = _load_pending_publication_sidecar(target, project_root)
        if pending is None:
            raise BridgePublicationError(
                "BRIDGE_PUBLICATION_REPAIR_REQUIRED: pending capability context is unavailable; "
                "file and claim are retained"
            )
        from groundtruth_kb.project.registry_control_plane import recover_bridge_publication

        recover_bridge_publication(
            target_path=str(pending.get("target_path") or ""),
            session_id=str(pending.get("session_id") or ""),
            mode="rollback",
            changed_by="bridge-publication-writer",
            change_reason=reason,
            expected_capability_hash=str(pending.get("capability_hash") or ""),
            expected_content_digest=str(pending.get("content_digest") or ""),
            expected_document_name=str(pending.get("document_name") or ""),
            expected_version=int(pending.get("version") or 0),
            expected_status=str(pending.get("status") or ""),
            project_root=project_root,
        )
        _delete_pending_publication_sidecar(target, project_root)
        return
    _compensate_publication(publication=publication, project_root=project_root, reason=reason)
    _PENDING_BRIDGE_PUBLICATIONS.pop(key, None)


def _append_closing_instruction(content: str) -> str:
    """Append the WI-5935 Slice E closing-instruction footer to a bridge artifact."""
    if _CLOSING_INSTRUCTION in content:
        return content
    return content.rstrip("\n") + "\n\n---\n\n" + _CLOSING_INSTRUCTION + "\n"


def write_bridge_file(
    document_name: str,
    version: int,
    content: str,
    project_root: Path,
    *,
    author_metadata: Mapping[str, object] | None = None,
    require_author_metadata: bool = True,
    release_claim: bool = True,
    claim_registry: Any | None = None,
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
    content_to_write = normalize_bridge_envelope_head(content_to_write)
    content_to_write = _append_closing_instruction(content_to_write)
    _reject_synthetic_session_context_id(content_to_write)
    try:
        from scripts.bridge_applicability_preflight import (
            prepare_verdict_candidate,
            verdict_candidate_needs_preparation,
        )

        if verdict_candidate_needs_preparation(content_to_write):
            content_to_write = prepare_verdict_candidate(
                candidate_path=target,
                content=content_to_write,
                project_root=project_root,
            )
    except (OSError, SystemExit, ValueError) as exc:
        raise BridgeComplianceError(f"verdict candidate preparation failed closed: {exc}") from exc
    audit = run_bridge_compliance_audit(
        file_path=target,
        content=content_to_write,
        project_root=project_root,
    )
    typed_publication = _registry_publication_enabled(project_root)
    publication: _PendingBridgePublication | None = None
    status = _first_status(content_to_write)
    if typed_publication:
        if status not in VALID_STATUSES:
            raise BridgePublicationError("typed bridge publication requires a canonical first-line status")
        session_id, metadata = _publication_author_session(content_to_write)
        guards = _run_provider_verdict_guards(
            project_root=project_root,
            target=target,
            content=content_to_write,
            session_id=session_id,
            author_metadata=metadata,
        )
        compliance_digest = _publication_compliance_digest(audit=audit, guards=guards)
        try:
            from groundtruth_kb.project.registry_control_plane import (
                mint_bridge_publication_capability,
            )
            from groundtruth_kb.project.timer_config import (
                resolve_protected_commit_timers,
            )

            timers = resolve_protected_commit_timers(project_root=project_root)

            minted = mint_bridge_publication_capability(
                document_name=document_name,
                version=version,
                status=status,
                target_path=target,
                content=content_to_write.encode("utf-8"),
                session_id=session_id,
                compliance_digest=compliance_digest,
                ttl_seconds=timers.bridge_publication_capability_ttl_seconds,
                project_root=project_root,
            )
        except Exception as exc:
            raise BridgePublicationError(f"typed bridge publication authorization failed: {exc}") from exc
        publication = _PendingBridgePublication(
            capability=str(minted["capability"]),
            capability_hash=str(
                minted.get("capability_hash")
                or "sha256:" + hashlib.sha256(str(minted["capability"]).encode("utf-8")).hexdigest()
            ),
            target_path=str(minted["target_path"]),
            session_id=session_id,
            content_digest=str(
                minted.get("content_digest") or "sha256:" + hashlib.sha256(content_to_write.encode("utf-8")).hexdigest()
            ),
            document_name=document_name,
            version=version,
            status=status,
        )
        try:
            _write_pending_publication_sidecar(
                publication,
                target=target,
                project_root=project_root,
            )
        except Exception as exc:
            _compensate_publication(
                publication=publication,
                project_root=project_root,
                reason=f"pending publication sidecar write failed: {exc}",
            )
            raise BridgePublicationError(f"pending publication sidecar write failed: {exc}") from exc

    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with target.open("x", encoding="utf-8", newline="") as handle:
            handle.write(content_to_write)
    except FileExistsError as exc:
        if publication is not None:
            _compensate_publication(
                publication=publication,
                project_root=project_root,
                reason="exclusive create lost a publication race",
            )
        raise BridgeConflictError(f"{target} already exists; refusing to overwrite") from exc
    except OSError as exc:
        if publication is not None:
            _compensate_publication(
                publication=publication,
                project_root=project_root,
                reason=f"exclusive bridge write failed: {exc}",
            )
        else:
            target.unlink(missing_ok=True)
        raise

    try:
        written = target.read_text(encoding="utf-8")
    except OSError as exc:
        if publication is not None:
            _compensate_publication(
                publication=publication,
                project_root=project_root,
                reason=f"post-write bridge reread failed: {exc}",
            )
            raise BridgePublicationError(
                f"post-write verification failed for {target} and was compensated: {exc}"
            ) from exc
        target.unlink(missing_ok=True)
        raise
    if written != content_to_write:
        if publication is not None:
            _compensate_publication(
                publication=publication,
                project_root=project_root,
                reason="post-write byte verification failed",
            )
        else:
            target.unlink(missing_ok=True)
        raise BridgeConflictError(f"post-write verification failed for {target}: content on disk differs")

    if publication is not None:
        try:
            from groundtruth_kb.project.registry_control_plane import (
                consume_bridge_publication_capability,
            )

            consume_bridge_publication_capability(
                capability=publication.capability,
                target_path=publication.target_path,
                content=content_to_write.encode("utf-8"),
                session_id=publication.session_id,
                changed_by="bridge-publication-writer",
                change_reason=f"Publish {document_name} version {version:03d} status {status}",
                project_root=project_root,
            )
            if release_claim:
                _release_claim(
                    project_root,
                    document_name,
                    publication.session_id,
                    claim_registry=claim_registry,
                )
                try:
                    _delete_pending_publication_sidecar(target, project_root)
                except OSError:
                    pass
            else:
                _PENDING_BRIDGE_PUBLICATIONS[str(target.resolve())] = publication
        except Exception as exc:
            _compensate_publication(
                publication=publication,
                project_root=project_root,
                reason=f"publication observation or claim release failed: {exc}",
            )
            raise BridgePublicationError(
                f"bridge publication failed after exclusive create and was compensated: {exc}"
            ) from exc
    elif release_claim:
        session_id, _ = _publication_author_session(content_to_write)
        if claim_registry is not None:
            _release_claim(
                project_root,
                document_name,
                session_id,
                claim_registry=claim_registry,
            )
        else:
            holder = _claim_holder(project_root, document_name)
            if holder is not None and str(holder.get("session_id") or "") == session_id:
                _release_claim(project_root, document_name, session_id)
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
    content_first_status = _first_status(content)
    if content_first_status != normalized_verdict:
        reported_content_status = (
            content_first_status
            if content_first_status in PROVIDER_VERDICT_STATUSES
            else ("<missing>" if not content_first_status else "<invalid>")
        )
        raise BridgePublicationError(
            f"{PROVIDER_VERDICT_STATUS_MISMATCH_CODE}: no publication occurred; "
            f"verdict_argument={normalized_verdict}; content_first_status={reported_content_status}; "
            "choose the intended substantive verdict and resend matching verdict and content-first-status values"
        )
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
    content_to_publish = normalize_bridge_envelope_head(content_to_publish)
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
        covered_by_hunks = _hunk_patch_covered_paths(root, hunk_patch_paths, latest_content=latest_content)
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

    return PublishedBridgeVerdict(
        document_name=document_name,
        verdict=normalized_verdict,
        verdict_path=verdict_path,
        commit_sha=commit_sha,
        claim_released=True,
    )
