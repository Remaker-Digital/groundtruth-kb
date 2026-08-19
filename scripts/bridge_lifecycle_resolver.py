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

from groundtruth_kb.bridge.versioned_files import parse_bridge_header_block

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

# The single in-code authority for ordinary bridge transitions (WI-5827).
# Each key is a previous status; the value is the base set of lawful successor
# statuses. Post-``NO-GO``, the lawful Prime statuses are ``REVISED`` and
# ``NO-ACTION`` (per DCL-NO-ACTION-STATUS-SEMANTICS-001); ``DEFERRED`` (owner
# parking) and ``WITHDRAWN`` (terminal) complete the set. ``NEW`` is never a
# lawful successor to ``NO-GO``. Narrative surfaces (the canonical file-bridge
# protocol prose and its generated projection) render this table and are bound
# to it by ``platform_tests/scripts/
# test_bridge_protocol_transition_table_consistency.py``.
ORDINARY_TRANSITIONS: dict[str, frozenset[str]] = {
    "NEW": frozenset({"GO", "NO-GO", "WITHDRAWN", "DEFERRED"}),
    "REVISED": frozenset({"GO", "NO-GO", "WITHDRAWN", "DEFERRED"}),
    "GO": frozenset({"GO", "NEW", "REVISED", "NO-ACTION", "DEFERRED", "WITHDRAWN"}),
    "NO-GO": frozenset({"GO", "REVISED", "NO-ACTION", "DEFERRED", "WITHDRAWN"}),
    "NO-ACTION": frozenset({"GO", "NO-GO", "VERIFIED"}),
    "ADVISORY": frozenset({"ADVISORY", "ACCEPTED", "BLOCKED", "DEFERRED", "WITHDRAWN"}),
    "BLOCKED": frozenset({"REVISED", "WITHDRAWN"}),
    "DEFERRED": frozenset({"REVISED", "WITHDRAWN"}),
}

# Post-GO augmentations to ORDINARY_TRANSITIONS, applied only once a GO has
# been seen earlier in the chain (``prior_go_seen``).
#
# A Prime NEW filed after a GO is normally an implementation report.
# An owner may explicitly defer that report's VERIFIED because its
# intermediate worktree cannot be finalized, then require a fresh
# reviewed REVISED proposal for the corrective implementation that
# will make the single governed commit possible.  That edge still
# has no implementation authority: the REVISED remains LO-review
# actionable until a later independent GO.
#
# Additionally, post-GO NEW/REVISED reports may receive a terminal VERIFIED.
POST_GO_REPORT_AUGMENTATIONS: dict[str, frozenset[str]] = {
    "NEW": frozenset({"REVISED", "VERIFIED"}),
    "REVISED": frozenset({"VERIFIED"}),
}

_PRIME_AUTHORED_STATUSES = PRIME_STATUSES | {"DEFERRED", "WITHDRAWN"}
_LOYAL_AUTHORED_STATUSES = LOYAL_OPPOSITION_STATUSES
_OWNER_AUTHORED_STATUSES = frozenset({"ACCEPTED", "BLOCKED"})
_METADATA_FIELDS = ("author_identity", "Document", "Version", "Responds to")

# WI-5827 N1 - enumerated key-synonym resolution. A closed, enumerated
# allowlist (not a pattern). `_metadata_values` consults the canonical key
# first; only when it yields no value does it try each synonym in declared
# order, returning the first hit. Any key outside the canonical set and this
# table continues to fail closed. Adding a synonym requires a governed change
# to this table, not a parser behavior change (reconciliation with WI-5636's
# retain-fail-closed-for-arbitrary-metadata stance).
_METADATA_KEY_SYNONYMS: dict[str, tuple[str, ...]] = {
    "Responds to": (
        "Reviewed",
        "Responds-To",
        "Responds to NO-GO",
        "Responds to GO",
        "revised_document",
    ),
}

# WI-5827 N2 - trailing-parenthetical value normalization. Applied once (not
# repeatedly) to `Version` and `Responds to` values to strip a single trailing
# parenthetical annotation before the exact equality comparison. The raw
# pre-normalization value is preserved on `BridgeVersion` for audit.
_TRAILING_ANNOTATION_RE = re.compile(r"\s*\([^()]*\)\s*$")

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
    # WI-5827 N2: raw pre-normalization metadata values, preserved for audit
    # when a single trailing parenthetical annotation is stripped.
    raw_version: str | None = None
    raw_responds_to: str | None = None

    @property
    def is_strict(self) -> bool:
        return self.classification == "strict"

    @property
    def is_malformed(self) -> bool:
        return self.classification == "malformed"

    @property
    def is_legacy(self) -> bool:
        return self.classification == "legacy"


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


def _exact_version_paths(
    project_root: Path, bridge_id: str
) -> list[tuple[int, Path, str]]:
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

    return [
        (version, by_version[version][0], by_version[version][1])
        for version in actual_versions
    ]


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
    # WI-5827 N1: consults the canonical key first, then each enumerated
    # synonym in declared order. Only when the canonical key yields no value
    # are synonyms consulted. A duplicate value against any of the consulted
    # keys remains a hard failure.
    candidates = (field,) + _METADATA_KEY_SYNONYMS.get(field, ())
    values: list[str] = []
    for candidate in candidates:
        prefix = f"{candidate}:"
        for line in lines[1:]:
            if line.startswith(prefix):
                values.append(line[len(prefix) :].strip())
        if values:
            break
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


def _strip_trailing_annotation(value: str) -> str:
    """WI-5827 N2: strip a single trailing parenthetical annotation.

    Applied once (not repeatedly) to a metadata value before the exact
    equality comparison. Values with no trailing parenthetical are returned
    unchanged. The raw value is preserved by the caller for audit.
    """
    return _TRAILING_ANNOTATION_RE.sub("", value, count=1)


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
    if status == "ADVISORY":
        # ADVISORY is informational, non-authoritative, and non-dispatchable.
        # Owner canon permits any operating role to author one; unlike a Prime
        # proposal or Loyal Opposition verdict, it carries no role-owned
        # lifecycle authority.
        allowed = {"prime-builder", "loyal-opposition", "owner"}
    elif status in _PRIME_AUTHORED_STATUSES:
        allowed = (
            {"prime-builder", "owner"}
            if status in {"DEFERRED", "WITHDRAWN"}
            else {"prime-builder"}
        )
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


_ENVELOPE_HEAD_PREFIXES = ("::init", "::open")


def _artifact_head_lines(lines):
    """Yield lines with any leading ``::init`` / ``::open`` envelope removed.

    The canonical bridge artifact head is ``::init gtkb <pb|lo>`` / ``::open
    <activity>`` / ``<status token>``; the legacy order put the status token
    first. Skipping leading envelope markers makes both orders resolve to the
    same status token.
    """
    index = 0
    while index < len(lines) and lines[index].strip().startswith(
        _ENVELOPE_HEAD_PREFIXES
    ):
        index += 1
    return lines[index:]


def _artifact_head_status(text):
    """Return the header-block status line used for strict vs malformed classification.

    Exact status tokens found anywhere in the first three non-blank lines
    (order immaterial) are returned as the bare token. A status line with
    trailing text is returned whole so the decorated-verdict malformation
    path stays intact.
    """
    parsed = parse_bridge_header_block(text)
    if parsed.status is not None and parsed.status_line_exact:
        return parsed.status
    if parsed.status_line:
        return parsed.status_line
    for line in _artifact_head_lines(text.splitlines()):
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


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
    line_one = _artifact_head_status(content)
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
    raw_version = _required_metadata(
        lines,
        "Version",
        rel_path=rel_path,
        version=version,
    )
    # WI-5827 N2: normalize a single trailing parenthetical annotation on the
    # Version value before the exact comparison; preserve the raw value.
    version_text = _strip_trailing_annotation(raw_version)
    responds_values = _metadata_values(
        lines,
        "Responds to",
        rel_path=rel_path,
        version=version,
    )
    if not responds_values:
        # Compatibility fallback: some LO-authored bridge files use "Reviewed:"
        # as the predecessor pointer instead of the canonical "Responds to:".
        # When "Responds to" is absent, "Reviewed" (if present and pointing to
        # the expected predecessor) is accepted as structurally equivalent.
        # This is a general robustness rule (Postel's Law), not a thread-specific
        # concession.  The canonical field takes precedence when both are present.
        responds_values = _metadata_values(
            lines,
            "Reviewed",
            rel_path=rel_path,
            version=version,
        )
    raw_responds_to = responds_values[0] if responds_values else None
    # WI-5827 N2: normalize a single trailing parenthetical annotation on the
    # Responds to value before the exact comparison; preserve the raw value.
    responds_to = (
        _strip_trailing_annotation(raw_responds_to) if raw_responds_to else None
    )

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

    expected_response = (
        None if version == 1 else f"bridge/{bridge_id}-{version - 1:03d}.md"
    )
    if responds_to != expected_response:
        _fail(
            "WRONG_RESPONDS_TO_LINK",
            f"Responds to metadata {responds_to!r} does not match {expected_response!r}: {rel_path}",
            path=rel_path,
            version=version,
        )

    # GOV-DOCUMENT-AUTHOR-PROVENANCE-001 is forward-only: pre-contract bridge
    # files are grandfathered, not backfilled. A canonical-status version with
    # structurally valid Document/Version/Responds-to but no author_identity
    # header predates the provenance contract; callers that select this
    # version as operative (implementation proposal or GO) re-validate
    # provenance before relying on it.
    author_identity_values = _metadata_values(
        lines,
        "author_identity",
        rel_path=rel_path,
        version=version,
    )
    author_identity = author_identity_values[0] if author_identity_values else None
    if author_identity is None:
        return BridgeVersion(
            version=version,
            path=rel_path,
            status=line_one,
            classification="legacy",
            document=document,
            responds_to=responds_to,
            author_identity=None,
            author_role=None,
            observed_status=line_one,
            raw_version=raw_version,
            raw_responds_to=raw_responds_to,
        )

    role = _author_role(author_identity)
    if role is None and line_one != "VERIFIED":
        return BridgeVersion(
            version=version,
            path=rel_path,
            status=line_one,
            classification="legacy",
            document=document,
            responds_to=responds_to,
            author_identity=author_identity,
            author_role=None,
            observed_status=line_one,
            raw_version=raw_version,
            raw_responds_to=raw_responds_to,
        )
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
        raw_version=raw_version,
        raw_responds_to=raw_responds_to,
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

        # WI-5827: consume the module-level authoritative table (base map plus
        # the documented post-GO augmentations); no allowed set changes.
        allowed: set[str] = set(ORDINARY_TRANSITIONS.get(previous.status, frozenset()))
        if prior_go_seen:
            allowed |= POST_GO_REPORT_AUGMENTATIONS.get(previous.status, frozenset())

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
        post_go_versions = versions[go_index + 1 :]
        statuses_after_go = [item.status for item in post_go_versions]
        latest_status = latest.status
        owner_deferred_reproposal = any(
            previous.status == "NEW" and current.status == "REVISED"
            for previous, current in zip(post_go_versions, post_go_versions[1:])
        )
        latest_is_resumable_report_no_go = (
            latest_status == "NO-GO"
            and any(status in {"NEW", "REVISED"} for status in statuses_after_go[:-1])
            and not owner_deferred_reproposal
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
            # Implementation authority must never derive from a grandfathered
            # (legacy) version: GOV-DOCUMENT-AUTHOR-PROVENANCE-001 tolerates
            # missing provenance for non-operative history, not for the exact
            # proposal/GO pair that authorizes implementation.
            if proposal.is_legacy:
                _fail(
                    "OPERATIVE_VERSION_MISSING_PROVENANCE",
                    f"Operative implementation proposal has no author_identity (legacy version): {proposal.path}",
                    path=proposal.path,
                    version=proposal.version,
                )
            if go.is_legacy:
                _fail(
                    "OPERATIVE_VERSION_MISSING_PROVENANCE",
                    f"Operative GO verdict has no author_identity (legacy version): {go.path}",
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
    if (
        proposal.status not in {"NEW", "REVISED"}
        or proposal.author_role != "prime-builder"
    ):
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
    if (
        corrected.status not in LOYAL_OPPOSITION_STATUSES
        or corrected.author_role != "loyal-opposition"
    ):
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
    malformed_indexes = [
        index
        for index, bridge_version in enumerate(parsed)
        if bridge_version.is_malformed
    ]
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
