#!/usr/bin/env python3
"""Resolve one exact, append-only bridge lifecycle without operation policy.

Only canonical ``bridge/<bridge-id>-NNN.md`` files participate. The resolver
validates structural authority and exposes separate audit, review, and
implementation views so callers do not need to reparse bridge files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

CANONICAL_STATUSES = frozenset(
    {
        "NEW",
        "REVISED",
        "GO",
        "NO-GO",
        "NO-ACTION",
        "VERIFIED",
        "DEFERRED",
        "WITHDRAWN",
        "ADVISORY",
        "ACCEPTED",
        "BLOCKED",
    }
)
PRIME_STATUSES = frozenset({"NEW", "REVISED", "NO-ACTION"})
LOYAL_OPPOSITION_STATUSES = frozenset({"GO", "NO-GO", "VERIFIED"})
PENDING_CORRECTION_DIAGNOSTIC = "PENDING_CORRECTION_NO_IMPLEMENTATION_AUTHORITY"

_PRIME_AUTHORED_STATUSES = PRIME_STATUSES | {"DEFERRED", "WITHDRAWN"}
_LOYAL_AUTHORED_STATUSES = LOYAL_OPPOSITION_STATUSES | {"ADVISORY"}
_OWNER_AUTHORED_STATUSES = frozenset({"ACCEPTED", "BLOCKED"})
_METADATA_FIELDS = ("author_identity", "Document", "Version", "Responds to")
_OBSERVED_STATUS_RE = re.compile(
    r"^(?P<status>NO-ACTION|NO-GO|WITHDRAWN|VERIFIED|REVISED|DEFERRED|ADVISORY|ACCEPTED|BLOCKED|NEW|GO)"
    r"(?=$|[^A-Z0-9-])"
)
_BRIDGE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass(frozen=True, slots=True)
class BridgeVersion:
    """One exact numbered bridge file and its strict parse classification."""

    version: int
    path: str
    status: str | None
    classification: str
    document: str | None = None
    responds_to: str | None = None
    author_identity: str | None = None
    author_role: str | None = None
    observed_status: str | None = None

    @property
    def is_strict(self) -> bool:
        return self.classification == "strict"

    @property
    def is_malformed(self) -> bool:
        return self.classification == "malformed"


@dataclass(frozen=True, slots=True)
class LifecycleDiagnostic:
    """A stable, operation-neutral lifecycle diagnostic."""

    code: str
    message: str
    path: str | None = None
    version: int | None = None


@dataclass(frozen=True, slots=True)
class BridgeLifecycleResolution:
    """Structurally valid views of one exact bridge thread."""

    bridge_id: str
    audit_versions: tuple[BridgeVersion, ...]
    latest_strict_state: BridgeVersion
    review_artifact: BridgeVersion | None
    implementation_artifact: BridgeVersion | None
    implementation_verdict: BridgeVersion | None
    quarantined_paths: tuple[str, ...]
    blocking_diagnostics: tuple[LifecycleDiagnostic, ...]


class BridgeLifecycleResolutionError(RuntimeError):
    """Raised when an exact bridge chain has no unambiguous structural result."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        path: str | None = None,
        version: int | None = None,
    ) -> None:
        self.code = code
        self.path = path
        self.version = version
        self.diagnostics = (
            LifecycleDiagnostic(
                code=code,
                message=message,
                path=path,
                version=version,
            ),
        )
        super().__init__(message)


def _fail(
    code: str,
    message: str,
    *,
    path: str | None = None,
    version: int | None = None,
) -> None:
    raise BridgeLifecycleResolutionError(code, message, path=path, version=version)


def _exact_version_paths(project_root: Path, bridge_id: str) -> list[tuple[int, Path, str]]:
    if not _BRIDGE_ID_RE.fullmatch(bridge_id) or bridge_id in {".", ".."}:
        _fail("INVALID_BRIDGE_ID", f"Invalid bridge id: {bridge_id!r}")

    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        _fail("BRIDGE_DIRECTORY_NOT_FOUND", f"Bridge directory not found: {bridge_dir}")

    exact_name_re = re.compile(rf"^{re.escape(bridge_id)}-(?P<version>\d{{3}})\.md$")
    by_version: dict[int, tuple[Path, str]] = {}
    for path in bridge_dir.iterdir():
        match = exact_name_re.fullmatch(path.name)
        if match is None:
            continue
        version = int(match.group("version"))
        rel_path = path.relative_to(project_root).as_posix()
        if version in by_version:
            prior = by_version[version][1]
            _fail(
                "DUPLICATE_BRIDGE_VERSION",
                f"Duplicate exact bridge version {version:03d}: {prior}, {rel_path}",
                path=rel_path,
                version=version,
            )
        by_version[version] = (path, rel_path)

    if not by_version:
        _fail(
            "BRIDGE_THREAD_NOT_FOUND",
            f"Bridge document not found as exact numbered files: {bridge_id}",
        )

    actual_versions = sorted(by_version)
    expected_versions = list(range(1, actual_versions[-1] + 1))
    if actual_versions != expected_versions:
        _fail(
            "NONCONTIGUOUS_BRIDGE_VERSIONS",
            f"Exact bridge versions must be contiguous from 001; found {actual_versions}, expected {expected_versions}",
        )

    return [(version, by_version[version][0], by_version[version][1]) for version in actual_versions]


def _read_strict_utf8(path: Path, rel_path: str, version: int) -> str:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        _fail(
            "BRIDGE_FILE_UNREADABLE",
            f"Bridge file cannot be read: {rel_path}: {exc}",
            path=rel_path,
            version=version,
        )
    try:
        return raw.decode("utf-8-sig", errors="strict")
    except UnicodeDecodeError as exc:
        _fail(
            "BRIDGE_FILE_INVALID_UTF8",
            f"Bridge file is not strict UTF-8-SIG: {rel_path}: {exc}",
            path=rel_path,
            version=version,
        )


def _metadata_values(
    lines: list[str],
    field: str,
    *,
    rel_path: str,
    version: int,
) -> list[str]:
    prefix = f"{field}:"
    values = [line[len(prefix) :].strip() for line in lines[1:] if line.startswith(prefix)]
    if len(values) > 1:
        _fail(
            "DUPLICATE_BRIDGE_METADATA",
            f"Bridge file has duplicate {field!r} metadata: {rel_path}",
            path=rel_path,
            version=version,
        )
    return values


def _required_metadata(
    lines: list[str],
    field: str,
    *,
    rel_path: str,
    version: int,
) -> str:
    values = _metadata_values(lines, field, rel_path=rel_path, version=version)
    if not values or not values[0]:
        _fail(
            "MISSING_BRIDGE_METADATA",
            f"Bridge file is missing {field!r} metadata: {rel_path}",
            path=rel_path,
            version=version,
        )
    return values[0]


def _author_role(author_identity: str) -> str | None:
    normalized = re.sub(r"[-_/]+", " ", author_identity.casefold())
    normalized = " ".join(normalized.split())
    if "prime builder" in normalized:
        return "prime-builder"
    if "loyal opposition" in normalized:
        return "loyal-opposition"
    if normalized == "owner" or normalized.startswith("owner "):
        return "owner"
    return None


def _validate_author_role(
    status: str,
    role: str | None,
    *,
    rel_path: str,
    version: int,
) -> None:
    if status in _PRIME_AUTHORED_STATUSES:
        allowed = {"prime-builder", "owner"} if status in {"DEFERRED", "WITHDRAWN"} else {"prime-builder"}
    elif status in _LOYAL_AUTHORED_STATUSES:
        allowed = {"loyal-opposition"}
    else:
        allowed = {"owner"}
    if role not in allowed:
        _fail(
            "WRONG_STATUS_AUTHOR_ROLE",
            f"Status {status} has wrong or unreadable author role {role!r}: {rel_path}",
            path=rel_path,
            version=version,
        )


def _parse_version(
    project_root: Path,
    bridge_id: str,
    version: int,
    path: Path,
    rel_path: str,
) -> BridgeVersion:
    try:
        resolved_path = path.resolve(strict=True)
        resolved_path.relative_to(project_root.resolve())
    except (OSError, ValueError) as exc:
        _fail(
            "BRIDGE_PATH_OUTSIDE_PROJECT",
            f"Bridge file does not resolve inside the project root: {rel_path}: {exc}",
            path=rel_path,
            version=version,
        )

    content = _read_strict_utf8(path, rel_path, version)
    lines = content.splitlines()
    line_one = lines[0] if lines else ""
    if line_one not in CANONICAL_STATUSES:
        observed_match = _OBSERVED_STATUS_RE.match(line_one)
        observed_status = observed_match.group("status") if observed_match else None
        return BridgeVersion(
            version=version,
            path=rel_path,
            status=None,
            classification="malformed",
            observed_status=observed_status,
        )

    document = _required_metadata(
        lines,
        "Document",
        rel_path=rel_path,
        version=version,
    )
    version_text = _required_metadata(
        lines,
        "Version",
        rel_path=rel_path,
        version=version,
    )
    author_identity = _required_metadata(
        lines,
        "author_identity",
        rel_path=rel_path,
        version=version,
    )
    responds_values = _metadata_values(
        lines,
        "Responds to",
        rel_path=rel_path,
        version=version,
    )
    responds_to = responds_values[0] if responds_values else None

    if document != bridge_id:
        _fail(
            "WRONG_BRIDGE_DOCUMENT",
            f"Document metadata {document!r} does not match {bridge_id!r}: {rel_path}",
            path=rel_path,
            version=version,
        )
    if version_text != f"{version:03d}":
        _fail(
            "WRONG_BRIDGE_VERSION_METADATA",
            f"Version metadata {version_text!r} does not match {version:03d}: {rel_path}",
            path=rel_path,
            version=version,
        )

    expected_response = None if version == 1 else f"bridge/{bridge_id}-{version - 1:03d}.md"
    if responds_to != expected_response:
        _fail(
            "WRONG_RESPONDS_TO_LINK",
            f"Responds to metadata {responds_to!r} does not match {expected_response!r}: {rel_path}",
            path=rel_path,
            version=version,
        )

    role = _author_role(author_identity)
    _validate_author_role(line_one, role, rel_path=rel_path, version=version)
    return BridgeVersion(
        version=version,
        path=rel_path,
        status=line_one,
        classification="strict",
        document=document,
        responds_to=responds_to,
        author_identity=author_identity,
        author_role=role,
        observed_status=line_one,
    )


def _validate_ordinary_transitions(versions: tuple[BridgeVersion, ...]) -> None:
    if not versions:
        _fail("EMPTY_BRIDGE_LIFECYCLE", "Bridge lifecycle contains no versions")

    first = versions[0]
    if first.status not in {"NEW", "REVISED", "ADVISORY"}:
        _fail(
            "INVALID_INITIAL_BRIDGE_STATUS",
            f"Initial bridge status must be NEW, REVISED, or ADVISORY; found {first.status}",
            path=first.path,
            version=first.version,
        )

    prior_go_seen = first.status == "GO"
    terminal_seen = first.status in {"VERIFIED", "WITHDRAWN", "ACCEPTED"}
    for previous, current in zip(versions, versions[1:]):
        assert previous.status is not None
        assert current.status is not None
        if terminal_seen:
            _fail(
                "VERSION_AFTER_TERMINAL_STATUS",
                f"Version {current.version:03d} follows terminal status {previous.status}",
                path=current.path,
                version=current.version,
            )

        allowed: set[str]
        if previous.status in {"NEW", "REVISED"}:
            allowed = {"GO", "NO-GO", "WITHDRAWN", "DEFERRED"}
            if prior_go_seen:
                allowed.add("VERIFIED")
        elif previous.status == "GO":
            allowed = {"NEW", "REVISED", "NO-ACTION", "DEFERRED", "WITHDRAWN"}
        elif previous.status == "NO-GO":
            allowed = {"REVISED", "NO-ACTION", "DEFERRED", "WITHDRAWN"}
        elif previous.status == "NO-ACTION":
            allowed = {"GO", "NO-GO", "VERIFIED"}
        elif previous.status == "ADVISORY":
            allowed = {"ADVISORY", "ACCEPTED", "BLOCKED", "DEFERRED", "WITHDRAWN"}
        elif previous.status in {"BLOCKED", "DEFERRED"}:
            allowed = {"REVISED", "WITHDRAWN"}
        else:
            allowed = set()

        if current.status not in allowed:
            _fail(
                "INVALID_BRIDGE_TRANSITION",
                f"Invalid bridge transition {previous.status} -> {current.status}",
                path=current.path,
                version=current.version,
            )
        prior_go_seen = prior_go_seen or current.status == "GO"
        terminal_seen = current.status in {"VERIFIED", "WITHDRAWN", "ACCEPTED"}


def _nearest_prime_artifact(
    versions: tuple[BridgeVersion, ...],
    before_index: int,
) -> BridgeVersion | None:
    for candidate in reversed(versions[:before_index]):
        if candidate.status in {"NEW", "REVISED"}:
            return candidate
    return None


def _ordinary_resolution(
    bridge_id: str,
    versions: tuple[BridgeVersion, ...],
) -> BridgeLifecycleResolution:
    _validate_ordinary_transitions(versions)
    latest = versions[-1]
    review_artifact = latest if latest.status in PRIME_STATUSES else None
    implementation_artifact: BridgeVersion | None = None
    implementation_verdict: BridgeVersion | None = None

    go_indexes = [index for index, item in enumerate(versions) if item.status == "GO"]
    if go_indexes:
        go_index = go_indexes[-1]
        go = versions[go_index]
        statuses_after_go = [item.status for item in versions[go_index + 1 :]]
        latest_status = latest.status
        latest_is_resumable_report_no_go = latest_status == "NO-GO" and any(
            status in {"NEW", "REVISED"} for status in statuses_after_go[:-1]
        )
        if latest_status == "GO" or latest_is_resumable_report_no_go:
            proposal = _nearest_prime_artifact(versions, go_index)
            if proposal is None:
                _fail(
                    "GO_WITHOUT_PRIME_ARTIFACT",
                    f"GO has no preceding Prime NEW or REVISED artifact: {go.path}",
                    path=go.path,
                    version=go.version,
                )
            implementation_artifact = proposal
            implementation_verdict = go

    return BridgeLifecycleResolution(
        bridge_id=bridge_id,
        audit_versions=versions,
        latest_strict_state=latest,
        review_artifact=review_artifact,
        implementation_artifact=implementation_artifact,
        implementation_verdict=implementation_verdict,
        quarantined_paths=(),
        blocking_diagnostics=(),
    )


def _correction_resolution(
    bridge_id: str,
    versions: tuple[BridgeVersion, ...],
    malformed_index: int,
) -> BridgeLifecycleResolution:
    malformed = versions[malformed_index]
    if malformed.observed_status not in LOYAL_OPPOSITION_STATUSES:
        _fail(
            "MALFORMED_CORRECTION_WRONG_SHAPE",
            f"Malformed correction candidate is not LO-verdict-shaped: {malformed.path}",
            path=malformed.path,
            version=malformed.version,
        )
    if malformed_index == 0:
        _fail(
            "MALFORMED_CORRECTION_MISSING_PROPOSAL",
            f"Malformed correction has no preceding Prime artifact: {malformed.path}",
            path=malformed.path,
            version=malformed.version,
        )

    proposal = versions[malformed_index - 1]
    if proposal.status not in {"NEW", "REVISED"} or proposal.author_role != "prime-builder":
        _fail(
            "MALFORMED_CORRECTION_WRONG_PREDECESSOR",
            f"Malformed correction must immediately follow a strict Prime NEW or REVISED: {malformed.path}",
            path=malformed.path,
            version=malformed.version,
        )

    strict_prefix = versions[:malformed_index]
    _validate_ordinary_transitions(strict_prefix)
    tail = versions[malformed_index + 1 :]
    if not tail:
        _fail(
            "MALFORMED_CORRECTION_INVALID_TAIL",
            "Malformed correction requires a strict Prime NO-ACTION",
            path=malformed.path,
            version=malformed.version,
        )

    no_action = tail[0]
    if no_action.status != "NO-ACTION" or no_action.author_role != "prime-builder":
        _fail(
            "MALFORMED_CORRECTION_MISSING_NO_ACTION",
            f"Malformed correction must be followed by strict Prime NO-ACTION: {malformed.path}",
            path=no_action.path,
            version=no_action.version,
        )

    if len(tail) == 1:
        diagnostic = LifecycleDiagnostic(
            code=PENDING_CORRECTION_DIAGNOSTIC,
            message="Pending corrected LO verdict; implementation authority is unavailable",
            path=no_action.path,
            version=no_action.version,
        )
        return BridgeLifecycleResolution(
            bridge_id=bridge_id,
            audit_versions=versions,
            latest_strict_state=no_action,
            review_artifact=no_action,
            implementation_artifact=None,
            implementation_verdict=None,
            quarantined_paths=(),
            blocking_diagnostics=(diagnostic,),
        )

    corrected = tail[1]
    if corrected.status not in LOYAL_OPPOSITION_STATUSES or corrected.author_role != "loyal-opposition":
        _fail(
            "MALFORMED_CORRECTION_INVALID_VERDICT",
            "Completed correction requires a strict role-correct GO, NO-GO, or VERIFIED",
            path=corrected.path,
            version=corrected.version,
        )

    if len(tail) > 2:
        if corrected.status == "VERIFIED":
            first_later = tail[2]
            _fail(
                "VERSION_AFTER_TERMINAL_STATUS",
                f"Version {first_later.version:03d} follows terminal status VERIFIED",
                path=first_later.path,
                version=first_later.version,
            )

        logical = _ordinary_resolution(
            bridge_id,
            strict_prefix + (corrected,) + tail[2:],
        )
        return BridgeLifecycleResolution(
            bridge_id=bridge_id,
            audit_versions=versions,
            latest_strict_state=logical.latest_strict_state,
            review_artifact=logical.review_artifact,
            implementation_artifact=logical.implementation_artifact,
            implementation_verdict=logical.implementation_verdict,
            quarantined_paths=(malformed.path,),
            blocking_diagnostics=logical.blocking_diagnostics,
        )

    implementation_artifact = proposal if corrected.status == "GO" else None
    implementation_verdict = corrected if corrected.status == "GO" else None
    return BridgeLifecycleResolution(
        bridge_id=bridge_id,
        audit_versions=versions,
        latest_strict_state=corrected,
        review_artifact=None,
        implementation_artifact=implementation_artifact,
        implementation_verdict=implementation_verdict,
        quarantined_paths=(malformed.path,),
        blocking_diagnostics=(),
    )


def resolve_bridge_lifecycle(
    project_root: Path,
    bridge_id: str,
) -> BridgeLifecycleResolution:
    """Resolve one exact bridge lifecycle from current numbered files.

    Structural ambiguity raises :class:`BridgeLifecycleResolutionError`; no
    stale or partial result is returned.
    """

    root = Path(project_root).resolve()
    parsed = tuple(
        _parse_version(root, bridge_id, version, path, rel_path)
        for version, path, rel_path in _exact_version_paths(root, bridge_id)
    )
    malformed_indexes = [index for index, bridge_version in enumerate(parsed) if bridge_version.is_malformed]
    if not malformed_indexes:
        return _ordinary_resolution(bridge_id, parsed)
    if len(malformed_indexes) != 1:
        malformed_paths = ", ".join(parsed[index].path for index in malformed_indexes)
        _fail(
            "MULTIPLE_MALFORMED_BRIDGE_VERSIONS",
            f"Bridge lifecycle has multiple malformed exact versions: {malformed_paths}",
        )
    return _correction_resolution(bridge_id, parsed, malformed_indexes[0])


__all__ = [
    "BridgeLifecycleResolution",
    "BridgeLifecycleResolutionError",
    "BridgeVersion",
    "LifecycleDiagnostic",
    "PENDING_CORRECTION_DIAGNOSTIC",
    "resolve_bridge_lifecycle",
]
