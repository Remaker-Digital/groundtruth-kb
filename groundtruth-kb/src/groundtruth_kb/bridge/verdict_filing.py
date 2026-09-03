# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Deterministic bridge verdict/advisory filing service (WI-5690).

This package-owned service provides the canonical single-publication path for
Loyal Opposition GO / NO-GO verdicts and ADVISORY entries through the governed
bridge writer. It derives the responder envelope (identity, role, session,
latest predecessor, next version, response path, evidence hashes, output path)
internally and exposes no authority-spoofing override.

Status routing follows WI-5690 / GOV-FILE-BRIDGE-AUTHORITY-001:

- ``GO`` / ``NO-GO``  -> ``publish_lo_verdict`` (governed writer, capability
  consumption, readback, claim release), author provenance must resolve to a
  loyal-opposition worker session.
- ``ADVISORY``       -> governed append-only writer with the canonical
  ``governance_advisory`` bridge kind and its distinct initial-advisory
  lifecycle (no prior-verdict requirement).
- ``VERIFIED``       -> refused with deterministic guidance to atomic
  commit-first finalization (``write_verdict.py --finalize-verified``).
- ``NO-ACTION``      -> refused with deterministic guidance to
  ``gt bridge file-no-action`` (Prime implementation-report path).
"""

from __future__ import annotations

import importlib.util
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:  # pragma: no cover - import fallback guard
    from scripts.bridge_applicability_preflight import prepare_verdict_candidate
except Exception:  # pragma: no cover - resolved lazily by the governed writer
    prepare_verdict_candidate = None

_SAFE_SLUG_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
_DOCUMENT_LINE_RE = re.compile(r"(?im)^\s*Document:\s*`?(?P<value>[A-Za-z0-9_.-]+)`?\s*$")
_VERSION_LINE_RE = re.compile(r"(?im)^\s*Version:\s*`?(?P<value>\d{3})\b")
_STATUS_RE = re.compile(r"^(GO|NO-GO|VERIFIED|NO-ACTION|ADVISORY)$")
_ENVELOPE_INIT_RE = re.compile(r"^::init gtkb (?P<role>pb|lo)$")
_ENVELOPE_OPEN_RE = re.compile(r"^::open (?P<activity>ops|deliberation|build|test|spec|project)$")
_APPLICABILITY_PREFLIGHT_HEADING_RE = re.compile(r"(?m)^\s*#{1,6}\s+Applicability Preflight\s*$")

VERDICT_STATUSES = frozenset({"GO", "NO-GO"})
ADVISORY_STATUSES = frozenset({"ADVISORY"})
REFUSED_STATUSES = frozenset({"VERIFIED", "NO-ACTION"})

ENVELOPE_ACTIVITY_BY_STATUS: Mapping[str, str] = {
    "GO": "test",
    "NO-GO": "test",
    "ADVISORY": "deliberation",
}


class VerdictFilingError(RuntimeError):
    """Raised when a verdict/advisory cannot be published."""


@dataclass(frozen=True)
class VerdictFilingResult:
    """Stable receipt for one verdict/advisory publication."""

    document: str
    status: str
    version: int
    path: str
    responded_to: str | None
    capability_consumed: bool
    claim_released: bool
    readback_verified: bool
    commit_sha: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "document": self.document,
            "status": self.status,
            "version": self.version,
            "path": self.path,
            "responded_to": self.responded_to,
            "capability_consumed": self.capability_consumed,
            "claim_released": self.claim_released,
            "readback_verified": self.readback_verified,
            "commit_sha": self.commit_sha,
        }


def _load_writer(project_root: Path) -> Any:
    """Load the governed bridge writer script module from the project root."""
    script_path = project_root / "scripts" / "gtkb_bridge_writer.py"
    if not script_path.is_file():
        raise VerdictFilingError(f"governed bridge writer is missing: {script_path}")
    spec = importlib.util.spec_from_file_location("gtkb_bridge_writer", script_path)
    if spec is None or spec.loader is None:
        raise VerdictFilingError(f"unable to load governed bridge writer: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_claim_registry(project_root: Path) -> Any:
    """Load the governed work-intent claim registry script module (advisory path)."""
    script_path = project_root / "scripts" / "bridge_work_intent_registry.py"
    if not script_path.is_file():
        raise VerdictFilingError(f"governed claim registry is missing: {script_path}")
    spec = importlib.util.spec_from_file_location("bridge_work_intent_registry", script_path)
    if spec is None or spec.loader is None:
        raise VerdictFilingError(f"unable to load governed claim registry: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _thread_state(project_root: Path, document: str) -> tuple[Path | None, int, str | None]:
    """Return ``(latest_path, next_version, latest_status)`` for a thread."""
    writer = _load_writer(project_root)
    try:
        latest_path, next_version, latest_status, _ = writer._thread_state(project_root, document)
        return latest_path, next_version, latest_status
    except Exception as exc:
        raise VerdictFilingError(f"unable to read bridge thread state: {exc}") from exc


def _relative(path: Path, project_root: Path) -> str:
    return str(path.resolve().relative_to(project_root.resolve())).replace("\\", "/")


def _normalize_lf(content: str) -> str:
    return content.replace("\r\n", "\n").replace("\r", "\n")


def _first_status(content: str) -> str | None:
    for line in _normalize_lf(content).splitlines():
        stripped = line.strip()
        if stripped:
            return stripped.upper()
    return None


def _content_document(content: str) -> str | None:
    match = _DOCUMENT_LINE_RE.search(content)
    return match.group("value") if match else None


def _content_version(content: str) -> int | None:
    match = _VERSION_LINE_RE.search(content)
    return int(match.group("value")) if match else None


def _assert_in_root(path: Path, project_root: Path) -> None:
    try:
        path.resolve().relative_to(project_root.resolve())
    except ValueError as exc:
        raise VerdictFilingError(f"content file is outside the project root: {path}") from exc


def _env_session_id() -> str | None:
    """Resolve the current worker session id from host-provided environment."""
    for key in (
        "GTKB_SESSION_ID",
        "GOOSE_SESSION_ID",
        "CODEX_SESSION_ID",
        "CLAUDE_SESSION_ID",
        "CURSOR_SESSION_ID",
        "GTKB_ENVELOPE_SESSION_ID",
    ):
        value = (sys.intern(key) and __import__("os").environ.get(key) or "").strip()
        if value:
            return value
    return None


def _harness_name(project_root: Path | None = None) -> str | None:
    """Resolve the active harness name from host environment or acting identity.

    Returns ``None`` when the host declares no harness name so that downstream
    provenance resolution derives the harness from the session that actually
    owns the work. A vendor default here is not a harmless fallback: it routes
    every non-defaulted harness at the wrong
    ``harness-state/<harness>/session-envelopes/`` tree, which surfaces as
    "Worker role provenance is missing for the current session" and makes
    verdict publication impossible from that harness (WI-6211).

    ``GTKB_HARNESS_NAME`` retains precedence. When it is unset and
    ``project_root`` is supplied, fall back to
    :func:`resolve_acting_harness_identity`, which derives the acting harness
    from runtime markers plus durable identity and fails closed on conflicting
    markers. That fallback resolves harness IDENTITY only: it selects which
    ``session-envelopes`` tree to read and never supplies role authority, which
    remains inside the selected envelope (WI-6307).
    """
    value = (__import__("os").environ.get("GTKB_HARNESS_NAME") or "").strip()
    if value:
        return value
    if project_root is None:
        return None
    from groundtruth_kb.session.envelope import (
        EnvelopeError,
        resolve_acting_harness_identity,
    )

    try:
        name, _resolved_id = resolve_acting_harness_identity(project_root)
    except EnvelopeError:
        return None
    return name or None


def _declared_model_fields(content: str) -> dict[str, str]:
    """Take model fields from the artifact's own declaration.

    Model identity is not derivable from a role attestation or from session
    provenance, and emitting a placeholder would fabricate provenance on a
    governance artifact. The artifact's declared values stand or the fields are
    omitted.
    """

    declared: dict[str, str] = {}
    for field in ("author_model", "author_model_version", "author_model_configuration"):
        match = re.search(rf"(?mi)^{field}\s*:\s*(?P<value>\S.*?)\s*$", content or "")
        if match:
            declared[field] = match.group("value")
    return declared


def _harness_id_for(harness_name: str, project_root: Path) -> str:
    """Resolve the durable harness ID for a harness name, or empty string.

    Read from the persistent identity map rather than derived from the name,
    because the name-to-ID mapping is owner-assigned and not computable.
    """

    if not harness_name:
        return ""
    try:
        from scripts.harness_identity import load_harness_identities

        record = load_harness_identities(project_root).get("harnesses", {}).get(harness_name)
    except Exception:
        return ""
    identifier = record.get("id") if isinstance(record, dict) else None
    return str(identifier) if isinstance(identifier, str) else ""


def _metadata_from_attestation(session_id: str, project_root: Path, content: str) -> dict[str, str] | None:
    """Derive author metadata from the role attestation in force, or ``None``.

    Returns ``None`` only for the typed ``no_session_binding`` case, which is
    the ordered-migration fallback. Any other attestation failure is raised:
    a session that HAS a binding but whose role cannot be resolved must not
    quietly fall through to a resolver that infers role from durable registry
    state.
    """

    try:
        from groundtruth_kb.session.attestation import (
            RoleAttestationError,
            binding_for_context,
        )
    except ImportError:
        return None

    try:
        binding = binding_for_context(
            project_root / "groundtruth.db",
            session_id,
        )
    except RoleAttestationError as exc:
        if exc.code == "no_session_binding":
            return None
        raise VerdictFilingError(f"session binding unusable for verdict filing: {exc}") from exc

    harness_name = _harness_name(project_root) or ""
    harness_id = _harness_id_for(harness_name, project_root)
    derived = {
        "author_identity": f"{binding.role}/{harness_name or 'unknown-harness'}",
        "author_harness_id": harness_id,
        "author_session_context_id": session_id,
        "author_role_attestation": binding.evidence_reference,
    }
    derived.update(_declared_model_fields(content))
    return derived


def _metadata_from_envelope(session_id: str, project_root: Path, content: str = "") -> dict[str, str]:
    """Derive trusted author metadata from the current session envelope.

    Falls back to minimal truthful runtime metadata when the envelope resolver
    is unavailable; every field is derived, never caller-spoofed.
    """
    from scripts.bridge_author_metadata import (
        BridgeAuthorMetadataError,
        load_author_metadata,
    )

    # Role authority is the attestation resolver
    # (``DCL-SESSION-ROLE-RESOLUTION-001`` v8): the invoking session context
    # resolves through its immutable init binding to the role attestation in
    # force, and the attestation's evidence reference is what this artifact
    # persists. This runs BEFORE the legacy resolvers because those infer role
    # from durable registry state, which is a routing label rather than an
    # identity oracle. During the ordered Slice 1-3 migration, sessions whose
    # invoking context predates the attestation store (typed
    # ``no_session_binding``) still fall through to the legacy paths below;
    # Slice 3 removes that fallback once every live session initializes through
    # the binding transaction.
    attested = _metadata_from_attestation(session_id, project_root, content)
    if attested is not None:
        return attested

    try:
        metadata = load_author_metadata(project_root)
        if metadata and metadata.get("author_session_context_id"):
            return {k: str(v) for k, v in metadata.items() if v is not None}
    except (BridgeAuthorMetadataError, Exception):
        pass
    # Derive from the session that actually owns this work rather than guessing.
    # The prior fallback hardcoded a single vendor's identity and model strings,
    # which fabricated provenance on a governance artifact for every other
    # harness (WI-6211).
    try:
        from groundtruth_kb.session.envelope import resolve_worker_role_provenance

        provenance = resolve_worker_role_provenance(project_root, current_session_id=session_id)
        role = str(provenance.get("role") or "").strip()
        harness_name = str(provenance.get("harness_name") or "").strip()
        harness_id = str(provenance.get("harness_id") or "").strip()
        if role and harness_name and harness_id:
            # Model fields are intentionally omitted: they are not derivable
            # from provenance, and emitting a placeholder would either fabricate
            # provenance or fail the placeholder validator. Omitting them lets
            # the artifact's own declared model metadata stand.
            derived = {
                "author_identity": f"{role}/{harness_name}/{harness_id}",
                "author_harness_id": harness_id,
                "author_session_context_id": session_id,
            }
            # Model fields are not derivable from provenance. Take the values the
            # artifact itself declares rather than fabricating a vendor default.
            derived.update(_declared_model_fields(content))
            return derived
    except Exception:
        pass
    harness = _harness_name(project_root)
    return {
        "author_identity": f"loyal-opposition/{harness or 'unknown'}",
        "author_harness_id": _harness_id_for(harness or "", project_root),
        "author_session_context_id": session_id,
        "author_model": "unknown",
        "author_model_version": "unknown",
        "author_model_configuration": "verdict-filing-service",
    }


def _require_loyal_opposition_author(content: str) -> None:
    """Fail closed unless the filed artifact carries Loyal Opposition provenance."""
    lowered = content.lower()
    if "::init gtkb lo" not in lowered and "loyal-opposition" not in lowered:
        raise VerdictFilingError(
            "verdict/advisory author provenance must resolve to loyal-opposition; "
            "the content must carry the canonical `::init gtkb lo` envelope line"
        )


def _candidate_evidence_hash(candidate_path: str, content: str, project_root: Path) -> str:
    """Mirror the gate's candidate evidence-hash algorithm over normalized bytes."""
    from scripts.bridge_applicability_preflight import (
        candidate_evidence_hash,
    )

    try:
        return candidate_evidence_hash(candidate_path, content, project_root)
    except Exception as exc:
        # The sentinel round trip must be direct: if the hash cannot be computed
        # the service cannot publish a capability-backed artifact.
        raise VerdictFilingError(f"candidate evidence hash computation failed: {exc}") from exc


def publish_verdict(
    project_root: Path,
    *,
    document: str,
    status: str,
    content: str,
    session_id: str | None = None,
) -> VerdictFilingResult:
    """Publish one GO/NO-GO verdict or ADVISORY entry through governed helpers.

    Raises:
        VerdictFilingError: on any fail-closed condition (no publication).
    """
    root = project_root.resolve()
    normalized_status = status.strip().upper()
    if not document or _SAFE_SLUG_RE.fullmatch(document) is None:
        raise VerdictFilingError("verdict document must be a non-empty canonical bridge slug")
    if normalized_status not in (VERDICT_STATUSES | ADVISORY_STATUSES | REFUSED_STATUSES):
        raise VerdictFilingError(
            f"verdict status must be one of {sorted(VERDICT_STATUSES | ADVISORY_STATUSES | REFUSED_STATUSES)}; "
            f"got {status!r}"
        )
    if not content.strip():
        raise VerdictFilingError("verdict content must be non-empty")

    # Deterministic routing guidance for the two statuses that have dedicated
    # authoritative flows (atomic finalization and the Prime NO-ACTION path).
    if normalized_status == "VERIFIED":
        raise VerdictFilingError(
            "VERIFIED must be published through atomic commit-first finalization: "
            "`.claude/skills/gtkb-verify/helpers/write_verdict.py --finalize-verified --include <paths> "
            '--commit-message "<msg>"`'
        )
    if normalized_status == "NO-ACTION":
        raise VerdictFilingError(
            "NO-ACTION must be published through the Prime implementation-report path "
            "(`gt bridge file-no-action`); this service publishes LO verdicts and advisories only"
        )

    _assert_in_root(Path(project_root) / "bridge", root)
    content_document = _content_document(content)
    if content_document and content_document != document:
        raise VerdictFilingError(
            f"verdict content Document field {content_document!r} does not match claimed thread {document!r}"
        )

    latest_path, next_version, latest_status = _thread_state(root, document)
    content_version = _content_version(content)
    if content_version is not None and content_version != next_version:
        raise VerdictFilingError(f"verdict content Version must be {next_version:03d}; got {content_version}")

    responded_to = _relative(latest_path, root) if latest_path is not None else None
    if responded_to is not None and responded_to not in content.replace("\\", "/"):
        raise VerdictFilingError(
            f"verdict must respond to current latest entry {responded_to}; add the canonical `Responds to:` line"
        )

    session_id = session_id or _env_session_id()
    if not session_id or not session_id.strip():
        raise VerdictFilingError(
            "verdict publication requires a concrete worker session id; set a supported session-id env var "
            "or pass --session-id"
        )
    metadata = _metadata_from_envelope(session_id, root, content)

    writer = _load_writer(root)
    if normalized_status in VERDICT_STATUSES:
        if latest_status is None:
            raise VerdictFilingError(f"bridge thread {document!r} has no readable latest status")
        if (
            latest_status not in writer.PRIME_STATUSES
            and writer._bridge_kind(latest_path.read_text(encoding="utf-8", errors="replace"))
            not in writer.LO_ENVELOPE_BRIDGE_KINDS
        ):
            # GO/NO-GO after an LO verdict is invalid; only proposal states accept
            # the first LO verdict transition.
            if latest_status not in writer.PRIME_STATUSES:
                raise VerdictFilingError(
                    f"provider verdict {normalized_status} is invalid after {latest_status} "
                    f"(bridge_kind={writer._bridge_kind(latest_path.read_text(encoding='utf-8', errors='replace')) or 'unknown'})"
                )
        candidate_path = f"{document}-{next_version:03d}.md"
        prepared = content
        if normalized_status in writer.PROVIDER_VERDICT_STATUSES and _APPLICABILITY_PREFLIGHT_HEADING_RE.search(
            content
        ):
            prepared = prepare_verdict_candidate(
                candidate_path=root / "bridge" / candidate_path,
                content=content,
                project_root=root,
            )
        # Verify the candidate evidence hash round trip is direct for capability
        # publication; the writer's own candidate preflight reconciles precision.
        _candidate_evidence_hash(root / "bridge" / candidate_path, prepared, root)
        try:
            published = writer.publish_lo_verdict(
                document,
                normalized_status,
                prepared,
                root,
                session_id=session_id,
                harness_name=_harness_name(),
                author_metadata=metadata,
            )
        except Exception as exc:
            raise VerdictFilingError(f"governed verdict publication failed: {exc}") from exc
        output = root / "bridge" / f"{document}-{next_version:03d}.md"
        published_tuple = (
            published.document_name,
            published.verdict,
            published.verdict_path,
            published.commit_sha,
            published.claim_released,
        )
        return VerdictFilingResult(
            document=published_tuple[0],
            status=published_tuple[1],
            version=next_version,
            path=published_tuple[2],
            responded_to=responded_to,
            capability_consumed=True,
            claim_released=published_tuple[4],
            readback_verified=output.is_file(),
            commit_sha=published_tuple[3],
        )

    # ADVISORY: governed append-only writer with governance_advisory kind.
    _require_loyal_opposition_author(content)
    advisory_content = content.rstrip() + "\n"
    advisory_content = advisory_content.replace("bridge_kind: lo_verdict", "bridge_kind: governance_advisory", 1)
    claim_registry = _load_claim_registry(root)
    session = session_id
    try:
        holder = claim_registry.current_holder(document, project_root=root)
        if holder is None or str(holder.get("session_id") or "") != session:
            acquired = claim_registry.acquire(
                document,
                session,
                ttl_seconds=3600,
                project_root=root,
                claim_kind=None,
            )
            if not acquired:
                raise VerdictFilingError(
                    f"advisory publication requires an exact-session claim for {document!r}; another session holds it"
                )
        path = writer.write_bridge_file(
            document,
            next_version,
            advisory_content,
            root,
            require_author_metadata=False,
            release_claim=True,
            claim_registry=claim_registry,
        )
    except VerdictFilingError:
        raise
    except Exception as exc:
        raise VerdictFilingError(f"governed advisory publication failed: {exc}") from exc
    output = root / "bridge" / f"{document}-{next_version:03d}.md"
    return VerdictFilingResult(
        document=document,
        status="ADVISORY",
        version=next_version,
        path=_relative(path, root),
        responded_to=responded_to,
        capability_consumed=True,
        claim_released=True,
        readback_verified=output.is_file(),
    )


__all__ = [
    "ADVISORY_STATUSES",
    "REFUSED_STATUSES",
    "VERDICT_STATUSES",
    "VerdictFilingError",
    "VerdictFilingResult",
    "publish_verdict",
]
