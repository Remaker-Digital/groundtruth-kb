#!/usr/bin/env python3
"""Plan and safely finalize accumulated terminal VERIFIED bridge threads.

WI-6073 supplies a narrowly bound transaction context to the ordinary
protected-commit hook.  It never repairs bridge publication capabilities or
writes ``groundtruth.db``; candidates needing either action are explicit skips.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import sqlite3
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts import check_protected_commit_authorization as commit_gate  # noqa: E402
from scripts.bridge_author_metadata import author_metadata_gaps, extract_author_metadata  # noqa: E402
from scripts.bridge_lifecycle_resolver import (  # noqa: E402
    BridgeLifecycleResolutionError,
    resolve_bridge_lifecycle,
)
from scripts.bridge_review_independence import verdict_self_review_reason  # noqa: E402
from scripts.gtkb_bridge_writer import BridgeComplianceError, run_bridge_compliance_audit  # noqa: E402
from scripts.implementation_authorization import (  # noqa: E402
    AuthorizationError,
    load_named_packet,
    path_authorized,
    validate_packet_project_authorization_operation,
)
from scripts.verdict_evidence_anchor_preflight import validate_verdict_evidence_anchors  # noqa: E402

AUTHORITY_BRIDGE_ID = commit_gate.BATCH_FINALIZATION_AUTHORITY
OWNER_DECISION_ID = commit_gate.BATCH_FINALIZATION_OWNER_DECISION
PROJECT_AUTHORIZATION_ID = commit_gate.BATCH_FINALIZATION_PAUTH
RUNTIME_REL = commit_gate.BATCH_FINALIZATION_REL
MANIFEST_ENV = commit_gate.BATCH_FINALIZATION_ENV
DIRECT_VERDICT_RE = re.compile(r"^bridge/(?P<slug>[A-Za-z0-9][A-Za-z0-9_.-]*)-(?P<version>[0-9]{3})\.md$")
SUBJECT_RE = re.compile(r"(?m)^- Intended commit subject:\s*`([^`\r\n]+)`\s*$")
CHANGED_PATH_ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|")


class BatchFinalizationError(RuntimeError):
    """Raised when the batch itself cannot continue safely."""


class CandidateRefusal(BatchFinalizationError):
    """Raised for a candidate-local refusal that does not stop other threads."""


@dataclass(frozen=True, slots=True)
class SkipReason:
    code: str
    detail: str


@dataclass(frozen=True, slots=True)
class CandidatePlan:
    slug: str
    verdict_path: str
    verdict_digest: str
    intended_subject: str | None
    declared_paths: tuple[str, ...]
    selected_paths: tuple[str, ...]
    unchanged_declared_paths: tuple[str, ...]
    excluded_dirty_paths: tuple[str, ...]
    path_digests: tuple[tuple[str, str], ...]
    reasons: tuple[SkipReason, ...]
    commit_sha: str | None = None

    @property
    def ready(self) -> bool:
        return not self.reasons and self.commit_sha is None


@dataclass(frozen=True, slots=True)
class BatchPlan:
    schema_version: int
    operation: str
    base_head: str
    base_ref: str
    authority_bridge_id: str
    owner_decision_id: str
    project_authorization_id: str
    staged_paths: tuple[str, ...]
    candidates: tuple[CandidatePlan, ...]
    plan_digest: str


def _run_git(
    root: Path,
    *args: str,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        env=env,
        input=input_text,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if check and result.returncode != 0:
        raise BatchFinalizationError(
            f"git {' '.join(args)} failed with exit {result.returncode}: {(result.stderr or result.stdout).strip()}"
        )
    return result


def _z_paths(result: subprocess.CompletedProcess[str]) -> set[str]:
    if result.returncode != 0:
        raise BatchFinalizationError((result.stderr or result.stdout).strip())
    return {item.replace("\\", "/") for item in result.stdout.split("\0") if item}


def _head(root: Path) -> str:
    return _run_git(root, "rev-parse", "HEAD").stdout.strip()


def _head_ref(root: Path, head_oid: str | None = None) -> str:
    result = _run_git(root, "symbolic-ref", "-q", "HEAD", check=False)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    oid = head_oid or _head(root)
    return f"DETACHED:{oid}"


def _ref_target(head_ref: str) -> str:
    return "HEAD" if head_ref.startswith("DETACHED:") else head_ref


def _dirty_paths(root: Path) -> set[str]:
    tracked = _z_paths(_run_git(root, "diff", "--name-only", "-z", "HEAD", "--"))
    untracked = _z_paths(_run_git(root, "ls-files", "--others", "--exclude-standard", "-z", "--"))
    return tracked | untracked


def _staged_paths(root: Path, *, env: dict[str, str] | None = None) -> set[str]:
    return _z_paths(_run_git(root, "diff", "--cached", "--name-only", "-z", "--", env=env))


def _sha256_bytes(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def _open_db_readonly(root: Path) -> sqlite3.Connection:
    path = (root / "groundtruth.db").resolve()
    if not path.is_file():
        raise sqlite3.OperationalError(f"database is absent: {path}")
    return sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)


def _path_digest(root: Path, rel_path: str) -> str:
    path = root / rel_path
    if not path.exists():
        return "deleted"
    if not path.is_file():
        return "not-a-file"
    return _sha256_bytes(path.read_bytes())


def _first_status(content: str) -> str:
    return next((line.strip() for line in content.splitlines() if line.strip()), "")


def discover_terminal_verified(
    root: Path,
    *,
    slug: str | None = None,
    dirty_paths: set[str] | None = None,
) -> tuple[str, ...]:
    """Return direct, dirty bridge candidates only; cleanup-evidence is excluded."""

    dirty = _dirty_paths(root) if dirty_paths is None else dirty_paths
    candidates: list[str] = []
    for rel_path in sorted(dirty):
        match = DIRECT_VERDICT_RE.fullmatch(rel_path)
        if match is None or (slug is not None and match.group("slug") != slug):
            continue
        path = root / rel_path
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        if _first_status(content) == "VERIFIED":
            candidates.append(rel_path)
    return tuple(candidates)


def _publication_reason(root: Path, verdict_path: str, verdict_digest: str) -> SkipReason | None:
    try:
        conn = _open_db_readonly(root)
    except sqlite3.Error as exc:
        return SkipReason("publication_capability_unreadable", f"publication capability evidence is unreadable: {exc}")
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM sot_registry_bridge_publication_capabilities "
            "WHERE target_path = ? ORDER BY rowid DESC LIMIT 1",
            (verdict_path,),
        ).fetchone()
        if row is None:
            return SkipReason(
                "publication_capability_missing", "registered bridge path lacks exact publication capability evidence"
            )
        state = row["capability_state"]
        if state != "consumed":
            return SkipReason(
                "publication_capability_not_consumed",
                f"bridge publication capability is not consumed ({state!r})",
            )
        identity = DIRECT_VERDICT_RE.fullmatch(verdict_path)
        if (
            identity is None
            or row["authority_kind"] != "bridge_publication"
            or row["operation"] != "bridge_publication"
            or row["document_name"] != identity.group("slug")
            or int(row["version"]) != int(identity.group("version"))
            or row["target_path"] != verdict_path
            or not row["consumed_at"]
            or not row["result_digest"]
            or not row["revision_id"]
            or row["failure_reason"]
            or row["compensation_revision_id"]
            or row["compensation_digest"]
        ):
            return SkipReason("publication_capability_invalid", "bridge publication capability linkage is incomplete")
        if row["content_digest"] != verdict_digest:
            return SkipReason(
                "publication_content_drift",
                "bridge publication staged content digest mismatch",
            )
    except (sqlite3.Error, TypeError, ValueError) as exc:
        return SkipReason("publication_capability_unreadable", f"publication capability evidence is unreadable: {exc}")
    finally:
        conn.close()
    return None


def _foreign_claim_collisions(root: Path, slug: str, selected_paths: tuple[str, ...]) -> dict[str, list[str]]:
    """Map selected paths to other active GO claims whose packet scope covers them."""

    from scripts import bridge_work_intent_registry

    try:
        conn = _open_db_readonly(root)
        rows = conn.execute("SELECT thread_slug FROM work_intent_claims ORDER BY thread_slug").fetchall()
    except sqlite3.Error as exc:
        raise BatchFinalizationError(f"active work-intent inventory is unreadable: {exc}") from exc
    finally:
        if "conn" in locals():
            conn.close()
    collisions: dict[str, list[str]] = {}
    for (other_slug,) in rows:
        if other_slug in {slug, AUTHORITY_BRIDGE_ID}:
            continue
        try:
            holder = bridge_work_intent_registry.current_holder(other_slug, project_root=root)
        except bridge_work_intent_registry.WorkIntentRegistryError as exc:
            raise BatchFinalizationError(f"active claim {other_slug!r} is unreadable: {exc}") from exc
        if not holder or holder.get("claim_kind") != "go_implementation":
            continue
        try:
            packet = load_named_packet(root, other_slug)
        except AuthorizationError:
            # The claim still owns its work intent even when its authorization
            # packet cannot currently be used. With no trustworthy narrower
            # scope, conservatively fence every candidate path.
            for path in selected_paths:
                collisions.setdefault(path, []).append(f"{other_slug} (scope unreadable)")
            continue
        for path in selected_paths:
            if path_authorized(packet, path):
                collisions.setdefault(path, []).append(other_slug)
    return collisions


def _dedupe_reasons(reasons: list[SkipReason]) -> tuple[SkipReason, ...]:
    unique: dict[tuple[str, str], SkipReason] = {(reason.code, reason.detail): reason for reason in reasons}
    return tuple(unique[key] for key in sorted(unique))


def _reported_changed_paths(root: Path, report_text: str) -> tuple[tuple[str, ...], str | None]:
    section = commit_gate._section_body(report_text, "Files Changed") or commit_gate._section_body(
        report_text, "Changed Files"
    )
    if not section:
        return (), "implementation report lacks a Files Changed section"
    paths = tuple(
        match.group(1)
        for line in section.splitlines()
        if (match := CHANGED_PATH_ROW_RE.match(line.strip())) is not None
    )
    if not paths:
        if re.search(r"(?im)^\s*[-*]?\s*none\b", section) or re.search(
            r"(?i)\b(no|zero)\s+(source\s+)?(file\s+)?changes?\b", section
        ):
            return (), None
        return (), "implementation report Files Changed section has no exact path rows"
    errors = [commit_gate._manifest_path_error(root, path) for path in paths]
    errors = [error for error in errors if error is not None]
    if errors:
        return (), "; ".join(errors)
    if len(paths) != len(set(paths)):
        return (), "implementation report Files Changed section contains duplicate paths"
    return paths, None


def _candidate_plan(
    root: Path,
    verdict_path: str,
    *,
    dirty_paths: set[str],
    staged_paths: set[str],
    authority_packet: dict[str, Any] | None,
    authority_error: str | None,
) -> CandidatePlan:
    match = DIRECT_VERDICT_RE.fullmatch(verdict_path)
    if match is None:  # discovery makes this unreachable; retained as fail-closed API behavior
        raise BatchFinalizationError(f"candidate is not a direct numbered bridge file: {verdict_path}")
    slug = match.group("slug")
    reasons: list[SkipReason] = []
    try:
        content_bytes = (root / verdict_path).read_bytes()
        content = content_bytes.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        content_bytes = b""
        content = ""
        reasons.append(SkipReason("candidate_unreadable", str(exc)))
    verdict_digest = _sha256_bytes(content_bytes)
    manifest_paths, manifest_errors = commit_gate._parse_transaction_manifest(root, content)
    reasons.extend(SkipReason("manifest_invalid", error) for error in manifest_errors)
    subject_matches = SUBJECT_RE.findall(content)
    intended_subject = subject_matches[0].strip() if len(subject_matches) == 1 else None
    if intended_subject is None:
        reasons.append(
            SkipReason("commit_subject_missing", "VERIFIED candidate must declare exactly one intended commit subject")
        )

    chain = None
    report_text = ""
    reported_changed: tuple[str, ...] = ()
    try:
        resolution = resolve_bridge_lifecycle(root, slug)
        latest = resolution.latest_strict_state
        if resolution.blocking_diagnostics:
            reasons.append(SkipReason("lifecycle_diagnostics", "terminal thread has blocking lifecycle diagnostics"))
        if latest.path != verdict_path or latest.status != "VERIFIED":
            reasons.append(SkipReason("not_latest_verified", "candidate is not the exact latest strict VERIFIED state"))
        chain = commit_gate._approved_chain(root, resolution)
        report_text = (root / chain.report_path).read_text(encoding="utf-8")
        reported_changed, reported_error = _reported_changed_paths(root, report_text)
        if reported_error is not None:
            reasons.append(SkipReason("changed_path_evidence_invalid", reported_error))
    except (BridgeLifecycleResolutionError, commit_gate.GateError, OSError, ValueError) as exc:
        reasons.append(SkipReason("approved_chain_invalid", str(exc)))

    chain_dirty = sorted(
        path
        for path in dirty_paths
        if (chain_match := DIRECT_VERDICT_RE.fullmatch(path)) is not None and chain_match.group("slug") == slug
    )
    attributable_dirty = set(chain_dirty) | set(reported_changed)
    selected = tuple(path for path in manifest_paths if path in dirty_paths and path in attributable_dirty)
    unchanged = tuple(path for path in manifest_paths if path not in dirty_paths)
    excluded_dirty = tuple(path for path in manifest_paths if path in dirty_paths and path not in attributable_dirty)
    if verdict_path not in selected:
        reasons.append(SkipReason("candidate_not_dirty", "VERIFIED candidate is not in its dirty transaction set"))
    unbound_chain = sorted(set(chain_dirty) - set(selected))
    if unbound_chain:
        reasons.append(
            SkipReason("unbound_chain_paths", f"dirty bridge chain paths are absent from the manifest: {unbound_chain}")
        )
    unbound_reported = sorted((set(reported_changed) & dirty_paths) - set(manifest_paths))
    if unbound_reported:
        reasons.append(
            SkipReason(
                "reported_paths_not_declared",
                f"reported changed paths are dirty but absent from the verdict manifest: {unbound_reported}",
            )
        )
    staged_overlap = sorted(set(selected) & staged_paths)
    if staged_overlap:
        reasons.append(
            SkipReason(
                "real_index_overlap", f"candidate paths are already staged by another transaction: {staged_overlap}"
            )
        )
    try:
        foreign_claims = _foreign_claim_collisions(root, slug, selected)
    except BatchFinalizationError as exc:
        reasons.append(SkipReason("claim_inventory_unreadable", str(exc)))
    else:
        if foreign_claims:
            reasons.append(
                SkipReason(
                    "foreign_work_intent_collision",
                    "candidate paths are held by another active implementation claim: "
                    + json.dumps(foreign_claims, sort_keys=True),
                )
            )

    protected_paths = [path for path in selected if commit_gate.is_protected_path(path, project_root=root)]
    if chain is not None:
        try:
            packet, packet_errors = commit_gate._load_finalized_packet(
                root,
                slug,
                chain,
                protected_paths,
                batch_authority_packet=authority_packet,
            )
            if packet is None:
                reasons.extend(SkipReason("historical_packet_invalid", error) for error in packet_errors)
            self_review = verdict_self_review_reason(
                content,
                slug,
                root,
                expected_artifact_path=chain.report_path,
            )
            if self_review is not None:
                reasons.append(SkipReason("review_independence_failed", self_review))
            candidate_sessions = commit_gate.AUTHOR_SESSION_RE.findall(content)
            report_sessions = commit_gate.AUTHOR_SESSION_RE.findall(report_text)
            if len(candidate_sessions) != 1 or len(report_sessions) != 1:
                reasons.append(
                    SkipReason("session_metadata_invalid", "candidate and report need singular session metadata")
                )
            elif candidate_sessions[0] == report_sessions[0]:
                reasons.append(
                    SkipReason("same_session_self_review", "VERIFIED candidate is a same-session self-review")
                )
        except (commit_gate.GateError, OSError, ValueError) as exc:
            reasons.append(SkipReason("approved_chain_invalid", str(exc)))

    metadata_gaps = author_metadata_gaps(extract_author_metadata(content))
    if metadata_gaps:
        reasons.append(SkipReason("author_metadata_invalid", ", ".join(metadata_gaps)))
    anchor_errors = validate_verdict_evidence_anchors(content, project_root=root)
    if anchor_errors:
        reasons.append(SkipReason("evidence_anchors_invalid", str(anchor_errors)))
    if authority_error is not None:
        reasons.append(SkipReason("batch_authority_invalid", authority_error))
    elif authority_packet is not None:
        try:
            validate_packet_project_authorization_operation(
                root,
                authority_packet,
                requested_operations=["protected_mutation"],
                target_paths=protected_paths,
            )
        except AuthorizationError as exc:
            reasons.append(SkipReason("batch_pauth_invalid", str(exc)))

    publication_reason = _publication_reason(root, verdict_path, verdict_digest)
    if publication_reason is not None:
        reasons.append(publication_reason)
    else:
        try:
            run_bridge_compliance_audit(file_path=root / verdict_path, content=content, project_root=root)
        except (BridgeComplianceError, OSError, subprocess.SubprocessError) as exc:
            reasons.append(SkipReason("applicability_freshness_invalid", str(exc)))

    path_digests = tuple((path, _path_digest(root, path)) for path in selected)
    return CandidatePlan(
        slug=slug,
        verdict_path=verdict_path,
        verdict_digest=verdict_digest,
        intended_subject=intended_subject,
        declared_paths=tuple(manifest_paths),
        selected_paths=selected,
        unchanged_declared_paths=unchanged,
        excluded_dirty_paths=excluded_dirty,
        path_digests=path_digests,
        reasons=_dedupe_reasons(reasons),
    )


def _plan_payload(plan: BatchPlan | dict[str, Any]) -> dict[str, Any]:
    payload = asdict(plan) if isinstance(plan, BatchPlan) else dict(plan)
    payload.pop("plan_digest", None)
    return payload


def _plan_digest(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return _sha256_bytes(encoded)


def build_plan(root: Path = PROJECT_ROOT, *, slug: str | None = None) -> BatchPlan:
    root = root.resolve()
    base_head = _head(root)
    base_ref = _head_ref(root, base_head)
    dirty = _dirty_paths(root)
    staged = _staged_paths(root)
    authority_packet: dict[str, Any] | None
    authority_error: str | None = None
    try:
        authority_packet = load_named_packet(root, AUTHORITY_BRIDGE_ID)
    except AuthorizationError as exc:
        authority_packet = None
        authority_error = str(exc)

    candidates = [
        _candidate_plan(
            root,
            path,
            dirty_paths=dirty,
            staged_paths=staged,
            authority_packet=authority_packet,
            authority_error=authority_error,
        )
        for path in discover_terminal_verified(root, slug=slug, dirty_paths=dirty)
    ]

    owners: dict[str, list[str]] = {}
    for candidate in candidates:
        for path in candidate.selected_paths:
            owners.setdefault(path, []).append(candidate.slug)
    collisions = {path: slugs for path, slugs in owners.items() if len(slugs) > 1}
    if collisions:
        rewritten: list[CandidatePlan] = []
        for candidate in candidates:
            own_collisions = {path: collisions[path] for path in candidate.selected_paths if path in collisions}
            if own_collisions:
                reason = SkipReason(
                    "dirty_path_collision",
                    "dirty path is declared by multiple terminal threads: "
                    + json.dumps(own_collisions, sort_keys=True),
                )
                candidate = replace(candidate, reasons=_dedupe_reasons([*candidate.reasons, reason]))
            rewritten.append(candidate)
        candidates = rewritten

    unsigned = {
        "schema_version": 1,
        "operation": "verified_batch_finalize_plan",
        "base_head": base_head,
        "base_ref": base_ref,
        "authority_bridge_id": AUTHORITY_BRIDGE_ID,
        "owner_decision_id": OWNER_DECISION_ID,
        "project_authorization_id": PROJECT_AUTHORIZATION_ID,
        "staged_paths": tuple(sorted(staged)),
        "candidates": tuple(candidates),
    }
    digest_payload = json.loads(json.dumps(unsigned, default=lambda value: asdict(value)))
    return BatchPlan(**unsigned, plan_digest=_plan_digest(digest_payload))


def _index_digest(root: Path) -> str:
    git_dir = Path(_run_git(root, "rev-parse", "--absolute-git-dir").stdout.strip())
    index = git_dir / "index"
    return _sha256_bytes(index.read_bytes()) if index.is_file() else "absent"


def _index_entries(root: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    result = _run_git(root, "ls-files", "--stage", "-z")
    for record in result.stdout.split("\0"):
        if not record:
            continue
        metadata, separator, path = record.partition("\t")
        if not separator or not path:
            raise BatchFinalizationError("real Git index emitted an invalid staged-entry record")
        entries[path.replace("\\", "/")] = metadata
    return entries


def _assert_candidate_unchanged(root: Path, candidate: CandidatePlan) -> None:
    changed = [path for path, expected in candidate.path_digests if _path_digest(root, path) != expected]
    if changed:
        raise BatchFinalizationError(f"candidate worktree content drifted after planning: {changed}")


def _manifest_payload(
    *,
    candidate: CandidatePlan,
    head_oid: str,
    head_ref: str,
    authority_packet: dict[str, Any],
    plan_digest: str,
) -> dict[str, Any]:
    start = authority_packet.get("implementation_start")
    session_id = start.get("session_id") if isinstance(start, dict) else None
    created_at = datetime.now(UTC)
    payload: dict[str, Any] = {
        "schema_version": 1,
        "operation": "verified_batch_finalize",
        "authority_bridge_id": AUTHORITY_BRIDGE_ID,
        "authority_packet_hash": authority_packet.get("packet_hash"),
        "authority_session_id": session_id,
        "owner_decision_id": OWNER_DECISION_ID,
        "project_authorization_id": PROJECT_AUTHORIZATION_ID,
        "head_oid": head_oid,
        "head_ref": head_ref,
        "candidate_bridge_id": candidate.slug,
        "candidate_path": candidate.verdict_path,
        "candidate_content_digest": candidate.verdict_digest,
        "selected_paths": sorted(candidate.selected_paths),
        "declared_paths": list(candidate.declared_paths),
        "plan_digest": plan_digest,
        "created_at": created_at.isoformat().replace("+00:00", "Z"),
        "expires_at": (created_at + timedelta(minutes=2)).isoformat().replace("+00:00", "Z"),
        "nonce": secrets.token_hex(16),
    }
    payload["candidate_plan_digest"] = commit_gate._batch_candidate_plan_hash(payload)
    payload["manifest_hash"] = commit_gate._batch_manifest_hash(payload)
    return payload


@contextmanager
def _runtime_manifest(root: Path, payload: dict[str, Any]) -> Iterator[str]:
    directory = root / RUNTIME_REL
    directory.mkdir(parents=True, exist_ok=True)
    handle, name = tempfile.mkstemp(prefix="candidate-", suffix=".json", dir=directory)
    path = Path(name)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        yield path.relative_to(root).as_posix()
    finally:
        path.unlink(missing_ok=True)
        try:
            directory.rmdir()
        except OSError:
            pass


@contextmanager
def _temporary_index(root: Path, head_oid: str) -> Iterator[dict[str, str]]:
    git_dir = Path(_run_git(root, "rev-parse", "--absolute-git-dir").stdout.strip())
    handle, name = tempfile.mkstemp(prefix="gtkb-batch-index-", dir=git_dir)
    os.close(handle)
    path = Path(name)
    path.unlink(missing_ok=True)
    env = dict(os.environ)
    env["GIT_INDEX_FILE"] = str(path)
    try:
        _run_git(root, "read-tree", head_oid, env=env)
        yield env
    finally:
        path.unlink(missing_ok=True)


@contextmanager
def _batch_lock(root: Path) -> Iterator[None]:
    git_dir = Path(_run_git(root, "rev-parse", "--absolute-git-dir").stdout.strip())
    lock = git_dir / "gtkb-batch-finalize.lock"
    try:
        handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise BatchFinalizationError(f"another batch finalizer holds {lock}") from exc
    try:
        os.write(handle, f"pid={os.getpid()}\n".encode("ascii"))
        yield
    finally:
        os.close(handle)
        lock.unlink(missing_ok=True)


def _canonical_hook_dir(root: Path) -> Path:
    hooks = root / ".githooks"
    hook = hooks / "pre-commit"
    resolved_root = root.resolve(strict=True)
    try:
        resolved_hooks = hooks.resolve(strict=True)
        resolved_hook = hook.resolve(strict=True)
        resolved_hook.relative_to(resolved_root)
    except (OSError, ValueError) as exc:
        raise BatchFinalizationError("canonical pre-commit hook is absent or escapes the project root") from exc
    if (
        resolved_hook.parent != resolved_hooks
        or commit_gate._path_is_linklike(hooks)
        or commit_gate._path_is_linklike(hook)
        or not resolved_hook.is_file()
    ):
        raise BatchFinalizationError("canonical pre-commit hook path is linked or invalid")
    try:
        hook_text = resolved_hook.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise BatchFinalizationError(f"canonical pre-commit hook is unreadable: {exc}") from exc
    if "scripts/check_protected_commit_authorization.py --staged" not in hook_text:
        raise BatchFinalizationError("canonical pre-commit hook does not invoke the protected-commit gate")
    return resolved_hooks


def _commit_message(candidate: CandidatePlan, plan_digest: str) -> str:
    return (
        f"{candidate.intended_subject}\n\n"
        "Prime-operated finalization of a reviewer-authored VERIFIED verdict.\n"
        f"Authority: WI-6073 / {OWNER_DECISION_ID}\n"
        f"Reviewer-authored-verdict: {candidate.verdict_path}\n"
        f"Batch-plan-digest: {plan_digest}\n"
    )


def _commit_candidate(
    root: Path,
    candidate: CandidatePlan,
    *,
    authority_packet: dict[str, Any],
    plan_digest: str,
    expected_head: str,
    expected_ref: str,
) -> str:
    if not candidate.ready:
        raise CandidateRefusal("candidate is not ready")
    if _head(root) != expected_head:
        raise BatchFinalizationError("HEAD changed after the batch plan was accepted")
    if _head_ref(root, expected_head) != expected_ref:
        raise BatchFinalizationError("the symbolic HEAD ref changed after the batch plan was accepted")
    _assert_candidate_unchanged(root, candidate)
    overlap = sorted(set(candidate.selected_paths) & _staged_paths(root))
    if overlap:
        raise CandidateRefusal(f"candidate paths entered the real staged index: {overlap}")
    foreign_claims = _foreign_claim_collisions(root, candidate.slug, candidate.selected_paths)
    if foreign_claims:
        raise CandidateRefusal(
            "candidate paths entered another active work-intent scope: " + json.dumps(foreign_claims, sort_keys=True)
        )
    git_dir = Path(_run_git(root, "rev-parse", "--absolute-git-dir").stdout.strip())
    if (git_dir / "index.lock").exists():
        raise BatchFinalizationError("the real Git index is locked; batch finalization did not start")
    real_index_before = _index_digest(root)
    real_entries_before = _index_entries(root)
    real_staged_before = _staged_paths(root)

    with _temporary_index(root, expected_head) as env:
        _run_git(root, "add", "-A", "-f", "--", *candidate.selected_paths, env=env)
        temp_staged = _staged_paths(root, env=env)
        if temp_staged != set(candidate.selected_paths):
            raise CandidateRefusal(f"temporary staged set differs from candidate transaction: {sorted(temp_staged)}")
        payload = _manifest_payload(
            candidate=candidate,
            head_oid=expected_head,
            head_ref=expected_ref,
            authority_packet=authority_packet,
            plan_digest=plan_digest,
        )
        with _runtime_manifest(root, payload) as manifest_rel:
            env[MANIFEST_ENV] = manifest_rel
            temporary_index = Path(env["GIT_INDEX_FILE"])
            temporary_index_before = _sha256_bytes(temporary_index.read_bytes())
            hooks = _canonical_hook_dir(root)
            hook_path = hooks / "pre-commit"
            hook_digest = _sha256_bytes(hook_path.read_bytes())
            hook = _run_git(
                root,
                "-c",
                f"core.hooksPath={hooks}",
                "hook",
                "run",
                "pre-commit",
                env=env,
                check=False,
            )
            if hook.returncode != 0:
                detail = (hook.stderr or hook.stdout).strip()
                raise CandidateRefusal(f"pre-commit gate refused candidate: {detail}")
            if _sha256_bytes(hook_path.read_bytes()) != hook_digest:
                raise BatchFinalizationError("the canonical pre-commit hook changed while authorization was running")
            if _sha256_bytes(temporary_index.read_bytes()) != temporary_index_before:
                raise BatchFinalizationError("the disposable Git index changed after authorization")
        _assert_candidate_unchanged(root, candidate)
        if _head(root) != expected_head:
            raise BatchFinalizationError("HEAD changed while the candidate hook was running")
        if _head_ref(root, expected_head) != expected_ref:
            raise BatchFinalizationError("the symbolic HEAD ref changed while the candidate hook was running")
        if _index_digest(root) != real_index_before:
            raise BatchFinalizationError("the real Git index changed while the candidate hook was running")
        tree = _run_git(root, "write-tree", env=env).stdout.strip()
        commit = _run_git(
            root,
            "commit-tree",
            tree,
            "-p",
            expected_head,
            env=env,
            input_text=_commit_message(candidate, plan_digest),
        ).stdout.strip()
        ref_target = _ref_target(expected_ref)
        update = _run_git(root, "update-ref", ref_target, commit, expected_head, check=False)
        if update.returncode != 0:
            raise BatchFinalizationError(
                f"HEAD compare-and-swap failed; candidate commit is unreachable: {(update.stderr or update.stdout).strip()}"
            )
        if _head_ref(root, commit) != expected_ref:
            rollback = _run_git(root, "update-ref", ref_target, expected_head, commit, check=False)
            if rollback.returncode != 0:
                raise BatchFinalizationError("symbolic HEAD changed after commit publication and rollback failed")
            raise BatchFinalizationError("symbolic HEAD changed during commit publication; candidate was rolled back")

    committed_paths = _z_paths(_run_git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z", commit))
    parent = _run_git(root, "rev-parse", f"{commit}^").stdout.strip()
    if committed_paths != set(candidate.selected_paths) or parent != expected_head:
        rollback = _run_git(root, "update-ref", ref_target, expected_head, commit, check=False)
        if rollback.returncode != 0:
            raise BatchFinalizationError("created commit failed path/parent verification and HEAD rollback also failed")
        raise BatchFinalizationError("created commit failed exact path or parent verification; HEAD was rolled back")

    realign = _run_git(root, "reset", "-q", commit, "--", *candidate.selected_paths, check=False)
    if realign.returncode != 0:
        rollback = _run_git(root, "update-ref", ref_target, expected_head, commit, check=False)
        if rollback.returncode != 0:
            raise BatchFinalizationError("candidate committed but real-index realignment and HEAD rollback both failed")
        raise BatchFinalizationError("real-index realignment failed; candidate commit was rolled back")
    if _staged_paths(root) != real_staged_before:
        rollback = _run_git(root, "update-ref", ref_target, expected_head, commit, check=False)
        restore = _run_git(root, "reset", "-q", expected_head, "--", *candidate.selected_paths, check=False)
        if rollback.returncode != 0 or restore.returncode != 0:
            raise BatchFinalizationError("real staged set changed and HEAD/index rollback failed")
        raise BatchFinalizationError("real staged set changed during finalization; candidate commit was rolled back")
    selected = set(candidate.selected_paths)
    unrelated_before = {path: value for path, value in real_entries_before.items() if path not in selected}
    unrelated_after = {path: value for path, value in _index_entries(root).items() if path not in selected}
    if unrelated_after != unrelated_before:
        rollback = _run_git(root, "update-ref", ref_target, expected_head, commit, check=False)
        restore = _run_git(root, "reset", "-q", expected_head, "--", *candidate.selected_paths, check=False)
        if rollback.returncode != 0 or restore.returncode != 0:
            raise BatchFinalizationError("unrelated real-index entries changed and HEAD/index rollback failed")
        raise BatchFinalizationError("unrelated real-index entries changed; candidate commit was rolled back")
    return commit


def apply_plan(
    root: Path,
    plan: BatchPlan,
    *,
    expected_plan_digest: str,
    slugs: set[str] | None = None,
) -> BatchPlan:
    if plan.plan_digest != expected_plan_digest:
        raise BatchFinalizationError(
            f"plan digest mismatch: expected {expected_plan_digest}, current {plan.plan_digest}"
        )
    try:
        authority_packet = load_named_packet(root, AUTHORITY_BRIDGE_ID)
    except AuthorizationError as exc:
        raise BatchFinalizationError(f"batch authority packet is invalid: {exc}") from exc
    current_head = plan.base_head
    expected_ref = plan.base_ref
    results: list[CandidatePlan] = []
    with _batch_lock(root):
        for candidate in plan.candidates:
            if slugs is not None and candidate.slug not in slugs:
                results.append(candidate)
                continue
            if not candidate.ready:
                results.append(candidate)
                continue
            try:
                commit = _commit_candidate(
                    root,
                    candidate,
                    authority_packet=authority_packet,
                    plan_digest=plan.plan_digest,
                    expected_head=current_head,
                    expected_ref=expected_ref,
                )
            except CandidateRefusal as exc:
                reason = SkipReason("apply_refused", str(exc))
                results.append(replace(candidate, reasons=_dedupe_reasons([*candidate.reasons, reason])))
                continue
            current_head = commit
            results.append(replace(candidate, commit_sha=commit))
    return replace(plan, candidates=tuple(results))


def _render(plan: BatchPlan) -> dict[str, Any]:
    payload = asdict(plan)
    payload["summary"] = {
        "candidates": len(plan.candidates),
        "ready": sum(candidate.ready for candidate in plan.candidates),
        "skipped": sum(bool(candidate.reasons) for candidate in plan.candidates),
        "committed": sum(candidate.commit_sha is not None for candidate in plan.candidates),
    }
    return payload


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan", help="Read-only candidate enumeration and refusal report.")
    plan.add_argument("--slug")
    plan.add_argument("--json", action="store_true")
    apply = subparsers.add_parser("apply", help="Apply an exact previously reviewed plan.")
    apply.add_argument("--expected-plan-digest", required=True)
    apply.add_argument("--owner-decision", required=True)
    apply.add_argument("--project-authorization", required=True)
    selection = apply.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true")
    selection.add_argument("--slug")
    apply.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = args.project_root.resolve()
    slug = getattr(args, "slug", None)
    plan = build_plan(root, slug=slug)
    if args.command == "apply":
        if args.owner_decision != OWNER_DECISION_ID:
            raise BatchFinalizationError(f"apply requires owner decision {OWNER_DECISION_ID}")
        if args.project_authorization != PROJECT_AUTHORIZATION_ID:
            raise BatchFinalizationError(f"apply requires project authorization {PROJECT_AUTHORIZATION_ID}")
        if args.slug is not None and not plan.candidates:
            raise BatchFinalizationError(f"requested candidate {args.slug!r} is not a dirty terminal VERIFIED thread")
        selected_slugs = None if args.all else {args.slug}
        plan = apply_plan(
            root,
            plan,
            expected_plan_digest=args.expected_plan_digest,
            slugs=selected_slugs,
        )
    payload = _render(plan)
    if getattr(args, "json", False):
        sys.stdout.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    else:
        summary = payload["summary"]
        sys.stdout.write(
            f"Batch VERIFIED finalization: {summary['candidates']} candidate(s), "
            f"{summary['ready']} ready, {summary['skipped']} skipped, {summary['committed']} committed\n"
        )
        sys.stdout.write(f"Plan digest: {plan.plan_digest}\n")
        for candidate in plan.candidates:
            outcome = candidate.commit_sha or ("ready" if candidate.ready else "skipped")
            sys.stdout.write(f"- {candidate.slug}: {outcome}\n")
            for reason in candidate.reasons:
                sys.stdout.write(f"    {reason.code}: {reason.detail}\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BatchFinalizationError as exc:
        sys.stderr.write(f"batch VERIFIED finalization failed: {exc}\n")
        raise SystemExit(2) from exc
