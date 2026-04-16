# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Bridge Worker Context — context building, dispatch batching, and thread repair.

Provides the logic for building dispatch contexts from bridge messages,
discovering referenced artifacts, prompt construction, and terminal
thread repair.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:\\[^\r\n<>]*")
ARTIFACT_NAME_RE = re.compile(
    r"\b(?:INSIGHTS-[A-Za-z0-9-]+\.md|BRIDGE-RESPONSIVENESS-LEDGER\.md|[A-Za-z0-9._-]+\.(?:md|json|txt))\b"
)
DEFAULT_MAX_DISPATCH_TARGETS = 6
SESSION_START_SUBJECT = "Session start: report current operating state"
SESSION_START_BODY = "Report your current operating state"


def _now() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(UTC)


def _parse_iso(value: str | None) -> datetime | None:
    """Parse an ISO 8601 string into a timezone-aware datetime, or return None on failure."""
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def agent_peer(agent: str) -> str:
    """Return the opposing agent identifier for the given agent.

    Args:
        agent: Either ``"codex"`` or ``"prime"``.

    Returns:
        ``"prime"`` when ``agent`` is ``"codex"``, and ``"codex"`` otherwise.
    """
    return "prime" if agent == "codex" else "codex"


def agent_display(agent: str) -> str:
    """Return the human-readable display name for the given agent identifier.

    Args:
        agent: Either ``"codex"`` or ``"prime"``.

    Returns:
        ``"Codex"`` or ``"Prime"``.
    """
    return "Codex" if agent == "codex" else "Prime"


def dedupe_preserve_order(values: list[str]) -> list[str]:
    """Remove duplicates from a list while preserving original insertion order.

    Args:
        values: Input list of strings, possibly containing duplicates.

    Returns:
        A new list with duplicates removed, preserving the order of first occurrence.
    """
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _message_tags(message: dict[str, Any]) -> set[str]:
    """Extract a normalised set of lower-cased tag strings from a message dict."""
    raw_tags = message.get("tags")
    if not isinstance(raw_tags, list):
        return set()
    return {str(tag).strip().lower() for tag in raw_tags if str(tag).strip()}


def message_is_session_start_request(message: dict[str, Any]) -> bool:
    """Return True if the message matches the canonical session-start probe format.

    Args:
        message: A bridge message dict.

    Returns:
        ``True`` when the message subject and body match the session-start template.
    """
    subject = str(message.get("subject") or "").strip()
    body = str(message.get("body") or "").strip().rstrip(".")
    return subject == SESSION_START_SUBJECT and body == SESSION_START_BODY


def message_is_closure_only(message: dict[str, Any]) -> bool:
    """Return True if the message is purely informational closure traffic requiring no substantive reply.

    Args:
        message: A bridge message dict.

    Returns:
        ``True`` when the message content indicates it is closure-only or receipt-only.
    """
    subject = str(message.get("subject") or "").strip().lower()
    body = str(message.get("body") or "").strip().lower()
    resolution = str(message.get("resolution") or "").strip().lower()
    tags = _message_tags(message)
    text = "\n".join(fragment for fragment in (subject, body, resolution) if fragment)

    if "thread completed with outcome" in text:
        return True
    if "closure-only" in text or "receipt-only" in text:
        return True
    if "duplicate session-start probe" in text:
        return True
    if "session-start probe:" in text and "reply sent" in text:
        return True
    if "bridge-sync" in tags and ({"completed", "failed"} & tags):
        return True
    return False


def prioritize_inbox_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort inbox items so session-start probes come first and closure-only traffic comes last.

    Within each bucket, items are ordered by descending priority and then ascending
    ``created_at`` (oldest first).

    Args:
        items: A list of bridge message dicts from the inbox.

    Returns:
        A new list with the same items sorted by priority tier.
    """
    default_created_at = datetime.max.replace(tzinfo=UTC)
    enumerated = list(enumerate(items))

    def _sort_key(entry: tuple[int, dict[str, Any]]) -> tuple[int, int, datetime, int]:
        """Return a sort tuple for a single enumerated inbox item."""
        original_index, item = entry
        if message_is_session_start_request(item):
            bucket = 0
        elif message_is_closure_only(item):
            bucket = 2
        else:
            bucket = 1
        try:
            priority = -int(item.get("priority") or 0)
        except (TypeError, ValueError):
            priority = 0
        created_at = _parse_iso(item.get("created_at")) or default_created_at
        return (bucket, priority, created_at, original_index)

    return [item for _, item in sorted(enumerated, key=_sort_key)]


def iter_text_fragments(value: Any) -> list[str]:
    """Recursively collect all string leaf values from a nested dict/list/scalar.

    Args:
        value: Any Python value; strings, dicts, and lists are traversed recursively.

    Returns:
        A flat list of all string leaves found during traversal.
    """
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        items: list[str] = []
        for nested in value.values():
            items.extend(iter_text_fragments(nested))
        return items
    if isinstance(value, list):
        items_list: list[str] = []
        for nested in value:
            items_list.extend(iter_text_fragments(nested))
        return items_list
    return []


def clean_path_candidate(raw: str) -> str:
    """Strip surrounding quotes, brackets, and trailing punctuation from a raw path string.

    Args:
        raw: A raw string that may contain surrounding punctuation from markdown or logs.

    Returns:
        The cleaned string with leading/trailing noise characters removed.
    """
    return raw.strip().strip("`'\"()[]{}<>").rstrip(".,:;")


def resolve_artifact_name(name: str, *, project_dir: Path) -> Path | None:
    """Resolve an artifact name to a file path.

    Three resolution strategies:
      (a) Absolute path -> direct existence check only (never rglob).
      (b) Relative path -> try project_dir join, then rglob search.
      (c) Malformed / unparseable -> return None.

    Bridge autonomy Phase A (S259): absolute paths must never be passed
    to Path.rglob() — it raises ValueError on non-relative patterns.
    """
    if not name or not name.strip():
        return None

    candidate = Path(name)

    # (a) Absolute path — direct check only, no rglob search.
    if candidate.is_absolute():
        if candidate.exists():
            return candidate.resolve()
        return None

    # (b) Relative path — try direct join first.
    direct = (project_dir / candidate).resolve()
    if direct.exists():
        return direct

    # (b cont.) Fall back to rglob search in known directories.
    # Only filename-like patterns are safe for rglob.
    search_roots = [
        project_dir / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX",
        project_dir / "independent-progress-assessments",
        project_dir,
    ]
    matches: list[Path] = []
    for root in search_roots:
        if not root.exists():
            continue
        try:
            root_matches = list(root.rglob(name))
        except (ValueError, OSError):
            # Non-relative pattern, invalid chars, or OS-level path error.
            continue
        for match in root_matches:
            if match.is_file() and match not in matches:
                matches.append(match)
        if len(matches) == 1:
            break
    if len(matches) == 1:
        return matches[0].resolve()
    return None


def _resolve_structured_artifact_ref(raw: Any, *, project_dir: Path) -> Path | None:
    """Resolve a structured artifact reference (string or dict) to an absolute Path, or None."""
    if isinstance(raw, str):
        cleaned = clean_path_candidate(raw)
        if not cleaned:
            return None
        return resolve_artifact_name(cleaned, project_dir=project_dir)
    if not isinstance(raw, dict):
        return None

    for key in ("path", "name"):
        value = raw.get(key)
        if not isinstance(value, str):
            continue
        cleaned = clean_path_candidate(value)
        if not cleaned:
            continue
        resolved = resolve_artifact_name(cleaned, project_dir=project_dir)
        if resolved is not None:
            return resolved
    return None


def discover_artifacts(context: dict[str, Any], *, project_dir: Path) -> list[dict[str, str]]:
    """Find all referenced artifact files within a context dict and return resolved path records.

    Searches structured ``artifact_refs``, Windows absolute paths, and artifact name
    patterns found in the canonical and thread message text fields.

    Args:
        context: A bridge worker context dict containing message payloads and artifact refs.
        project_dir: Project root directory used for relative path resolution.

    Returns:
        A sorted list of ``{"path": ..., "source": ...}`` dicts for each unique artifact found.
    """
    found: dict[str, dict[str, str]] = {}

    for raw in context.get("artifact_refs", []):
        resolved = _resolve_structured_artifact_ref(raw, project_dir=project_dir)
        if resolved is None:
            continue
        found[str(resolved)] = {
            "path": str(resolved),
            "source": "structured-artifact-ref",
        }

    raw_strings: list[str] = []
    for key in (
        "canonical_message",
        "latest_non_protocol_codex_message",
        "latest_non_protocol_prime_message",
        "thread_messages",
    ):
        raw_strings.extend(iter_text_fragments(context.get(key)))

    for raw in raw_strings:
        for match in WINDOWS_PATH_RE.findall(raw):
            cleaned = clean_path_candidate(match)
            path = Path(cleaned)
            if path.exists():
                found[str(path.resolve())] = {
                    "path": str(path.resolve()),
                    "source": "absolute-path",
                }
        for match in ARTIFACT_NAME_RE.findall(raw):
            cleaned = clean_path_candidate(match)
            artifact_path = resolve_artifact_name(cleaned, project_dir=project_dir)
            if artifact_path is not None:
                found[str(artifact_path)] = {
                    "path": str(artifact_path),
                    "source": "artifact-name",
                }

    return sorted(found.values(), key=lambda item: item["path"])


def _repo_relative_artifact_path(raw: Any, *, project_dir: Path) -> str | None:
    """Convert a raw artifact reference to a repo-relative POSIX path string, or None if invalid."""
    candidate: str | None = None
    if isinstance(raw, dict):
        for key in ("path", "name"):
            value = raw.get(key)
            if isinstance(value, str) and value.strip():
                candidate = value
                break
    elif isinstance(raw, str) and raw.strip():
        candidate = raw

    if not candidate:
        return None

    cleaned = clean_path_candidate(candidate)
    if not cleaned:
        return None

    path = Path(cleaned)
    if path.is_absolute():
        try:
            relative = path.resolve().relative_to(project_dir.resolve())
        except (OSError, RuntimeError, ValueError):
            return None
    else:
        relative = path

    relative_text = relative.as_posix().strip()
    if not relative_text or relative_text.startswith("../"):
        return None
    return relative_text


def _repair_payload_artifact_refs(
    context: dict[str, Any],
    *,
    project_dir: Path,
) -> list[dict[str, str]]:
    """Build a deduplicated list of repo-relative artifact ref dicts suitable for a bridge payload."""
    refs: list[dict[str, str]] = []
    seen: set[str] = set()

    def _append_ref(raw: Any) -> None:
        """Append a single repo-relative artifact ref to refs if not already seen."""
        relative_path = _repo_relative_artifact_path(raw, project_dir=project_dir)
        if not relative_path or relative_path in seen:
            return
        seen.add(relative_path)
        refs.append({"type": "file", "path": relative_path, "note": "Bridge artifact"})

    for item in context.get("referenced_artifacts", []):
        _append_ref(item.get("path") if isinstance(item, dict) else item)

    canonical = context.get("canonical_message") or {}
    for raw in canonical.get("artifact_refs", []):
        _append_ref(raw)

    return refs


def summarize_context(agent: str, context: dict[str, Any]) -> str:
    """Format a single-context summary string for the dispatch prompt.

    Args:
        agent: The agent identifier receiving the dispatch.
        context: A bridge worker context dict.

    Returns:
        A multi-line summary string suitable for inclusion in the wake prompt.
    """
    canonical = context["canonical_message"]
    latest_worker = context.get(
        "latest_non_protocol_codex_message" if agent == "codex" else "latest_non_protocol_prime_message"
    )
    artifact_paths = [item["path"] for item in context.get("referenced_artifacts", [])]
    reasons = ",".join(context.get("wake_reasons", []))
    lines = [
        f"- {canonical['id']} | status={canonical.get('status')} | subject={canonical.get('subject')} | reasons={reasons}",
        f"  correlation={context.get('thread_correlation_id')}",
        f"  prior_{agent}_outbound={'yes' if context.get('already_reviewed_hint') else 'no'}",
    ]
    if latest_worker:
        lines.append(
            f"  latest_{agent}={latest_worker.get('id')} | {latest_worker.get('subject')} | {latest_worker.get('created_at')}"
        )
    if artifact_paths:
        lines.append(f"  artifacts={'; '.join(artifact_paths[:3])}")
    return "\n".join(lines)


def build_prompt(
    agent: str,
    snapshot_path: Path,
    new_items: list[dict[str, Any]],
    contexts: list[dict[str, Any]],
    *,
    project_dir: Path,
) -> str:
    """Construct the full wake prompt string to pass to the agent CLI subprocess.

    Args:
        agent: The agent identifier that will receive the prompt.
        snapshot_path: Path to the JSON context snapshot file written before dispatch.
        new_items: Pending inbox items included in this dispatch batch.
        contexts: Worker context dicts for the threads being dispatched.
        project_dir: Project root directory embedded in the prompt.

    Returns:
        The complete prompt string for the agent subprocess.
    """
    if contexts:
        context_lines = "\n".join(summarize_context(agent, context) for context in contexts)
    else:
        context_lines = "- none"
    worker_name = agent_display(agent)
    return f"""Start in Loyal Opposition mode in {project_dir}.

Load AGENTS.md and the required startup files under independent-progress-assessments/ before doing other work.

A bridge wake was triggered because pending work or bridge-risk signals exist for agent `{agent}`.

Canonical bridge snapshot:
{snapshot_path}

Pending new inbox count: {len(new_items)}

Target thread summaries:
{context_lines}

Required actions:
1. Read the canonical bridge snapshot before narrating any pickup.
2. Process only the target thread summaries plus the pending inbox IDs listed in the canonical bridge snapshot for this wake.
3. If a target is malformed or has bridge status `failed`, use `send_correction_message(...)` with the failed message id and do not send freeform correction traffic via `send_message(...)`.
4. If a target already has a prior {worker_name} review or final outbound verdict in the snapshot, do not narrate a fresh review; treat it as resend/closure work and cite the canonical report path if present.
5. Do not send protocol acknowledgements, acceptance notes, or negotiation-only replies. The only acceptable bridge response is a full substantive reply to the request.
6. Every peer `send_message(...)` reply must include a valid `payload_json` with `expected_response`, `artifact_refs`, and `action_items`. Do not send bare substantive replies.
7. For ordinary follow-up replies, prefer `expected_response=\"status_update\"` and carry forward the in-scope artifact refs from the thread.
8. After sending the substantive reply, resolve the original inbound request as `completed` or `failed`.
9. Process requests end-to-end without waiting for owner approval unless blocked by a true external decision.
10. If the bridge is clear after processing, state that explicitly and exit.
"""


def build_context_snapshot(
    *,
    trigger: str,
    contexts: list[dict[str, Any]],
    new_items: list[dict[str, Any]],
) -> dict[str, Any]:
    """Assemble a serialisable context snapshot dict for the dispatch prompt file.

    Args:
        trigger: Label describing what caused this dispatch (e.g. ``"resident-worker"``).
        contexts: Enriched worker context dicts for each thread in the batch.
        new_items: Raw inbox items included in this dispatch.

    Returns:
        A dict with generation timestamp, trigger, inbox IDs, and context list.
    """
    return {
        "generated_at": _now().isoformat(),
        "trigger": trigger,
        "new_inbox_ids": [item["id"] for item in new_items],
        "contexts": contexts,
    }


def select_dispatch_batch(
    contexts: list[dict[str, Any]],
    new_items: list[dict[str, Any]],
    *,
    max_targets: int = DEFAULT_MAX_DISPATCH_TARGETS,
) -> dict[str, Any]:
    """Select the highest-priority subset of contexts and items to dispatch, respecting the batch cap.

    Prioritises session-start probes, then regular items, then closure-only traffic.
    Items that exceed the cap are returned in ``deferred_ids``.

    Args:
        contexts: Enriched context dicts for candidate threads.
        new_items: Raw pending inbox items.
        max_targets: Maximum number of target message IDs to dispatch in one batch.

    Returns:
        A dict with keys ``"contexts"``, ``"new_items"``, ``"target_ids"``, and ``"deferred_ids"``.

    Raises:
        ValueError: If ``max_targets`` is less than 1.
    """
    if max_targets < 1:
        raise ValueError("max_targets must be at least 1")

    context_by_id: dict[str, dict[str, Any]] = {}
    context_order: list[str] = []
    for context in contexts:
        canonical_id = str((context.get("canonical_message") or {}).get("id") or "").strip()
        if canonical_id and canonical_id not in context_by_id:
            context_by_id[canonical_id] = context
            context_order.append(canonical_id)

    ordered_new_items = prioritize_inbox_items(new_items)
    ordered_ids: list[str] = []
    for item in ordered_new_items:
        message_id = str(item.get("id") or "").strip()
        if message_id and message_id not in ordered_ids:
            ordered_ids.append(message_id)
    for canonical_id in context_order:
        if canonical_id not in ordered_ids:
            ordered_ids.append(canonical_id)

    ordered_ids = dedupe_preserve_order(ordered_ids)

    selected_ids = ordered_ids[:max_targets]
    selected_set = set(selected_ids)

    return {
        "contexts": [context_by_id[message_id] for message_id in selected_ids if message_id in context_by_id],
        "new_items": [item for item in ordered_new_items if str(item.get("id") or "").strip() in selected_set],
        "target_ids": selected_ids,
        "deferred_ids": ordered_ids[max_targets:],
    }


def _worker_context(
    bridge: Any,
    message_ref: str,
    *,
    agent: str,
) -> dict[str, Any] | None:
    """Fetch the worker event context dict for a single message reference from the bridge."""
    context_builder = getattr(bridge, "get_worker_event_payload", None)
    if callable(context_builder):
        payload = context_builder(message_ref, agent=agent)
        if isinstance(payload, dict) and "context" in payload:
            context = payload.get("context")
            return context if isinstance(context, dict) else None
        return payload if isinstance(payload, dict) else None
    return cast(dict[str, Any] | None, bridge.describe_thread_context(message_ref, recipient=agent))


def build_contexts(
    bridge: Any,
    *,
    agent: str,
    explicit_refs: list[str],
    new_items: list[dict[str, Any]],
    project_dir: Path,
    log_fn: Callable[[str], None] | None = None,
    max_contexts: int | None = None,
) -> list[dict[str, Any]]:
    """Build enriched context dicts for all candidate dispatch targets.

    Combines new inbox items and explicit notification references, fetches their
    thread context from the bridge, and annotates each with wake reasons,
    discovered artifacts, and a prior-review hint.

    Args:
        bridge: The bridge runtime module providing ``get_worker_event_payload``.
        agent: The agent identifier for whom contexts are being built.
        explicit_refs: Message IDs surfaced directly from notification events.
        new_items: Raw pending inbox items.
        project_dir: Project root directory used for artifact resolution.
        log_fn: Optional callable for writing diagnostic log lines.
        max_contexts: Maximum number of contexts to build; ``None`` means unlimited.

    Returns:
        A list of enriched context dicts, one per unique thread.

    Raises:
        ValueError: If ``max_contexts`` is provided and less than 1.
    """
    if max_contexts is not None and max_contexts < 1:
        raise ValueError("max_contexts must be at least 1")

    reasons_by_id: dict[str, set[str]] = {}

    for item in prioritize_inbox_items(new_items):
        reasons_by_id.setdefault(item["id"], set()).add("new")
    for message_ref in explicit_refs:
        context = _worker_context(bridge, message_ref, agent=agent)
        if context is None:
            if log_fn is not None:
                log_fn(f"explicit wake target unresolved: {message_ref}")
            continue
        canonical_id = context["canonical_message"]["id"]
        reasons_by_id.setdefault(canonical_id, set()).add(f"explicit:{message_ref}")

    contexts: list[dict[str, Any]] = []
    for message_id, reasons in reasons_by_id.items():
        if max_contexts is not None and len(contexts) >= max_contexts:
            break
        # Phase A: isolate context-build failures per thread.
        # One bad message/artifact must not stop all autonomous bridge work.
        try:
            context = _worker_context(bridge, message_id, agent=agent)
            if context is None:
                continue
            canonical = context.get("canonical_message") or {}
            if canonical.get("status") == "failed":
                reasons.add("failed")
            context["wake_reasons"] = sorted(reasons)
            context["referenced_artifacts"] = discover_artifacts(context, project_dir=project_dir)
            latest_worker = context.get(
                "latest_non_protocol_codex_message" if agent == "codex" else "latest_non_protocol_prime_message"
            )
            context["already_reviewed_hint"] = bool(
                latest_worker and latest_worker.get("id") != context["canonical_message"]["id"]
            )
            contexts.append(context)
        except Exception as exc:
            if log_fn is not None:
                log_fn(
                    f"context-build failed for message {message_id}: {exc!r} — "
                    "skipping this thread, continuing with remaining targets"
                )
    return contexts


def _peer_sender_for_context(agent: str, context: dict[str, Any]) -> str | None:
    """Return the peer agent who sent the canonical message, or None if not a peer-to-peer thread."""
    canonical = context.get("canonical_message") or {}
    sender = canonical.get("sender")
    recipient = canonical.get("recipient")
    if recipient == agent and sender in {"codex", "prime"}:
        return str(sender)
    return None


def _default_action_items(outcome: str) -> list[str]:
    """Return a standard list of action items appropriate for the given thread outcome label."""
    if outcome == "blocked":
        return [
            "Send a substantive unblock plan or revised implementation if further review is needed",
            "Poll for the peer's next substantive reply before reopening this thread",
        ]
    if outcome == "superseded":
        return [
            "Use the newest thread guidance if further action is still needed",
            "Send a substantive follow-up only if the replacement thread still needs bridge work",
        ]
    return [
        "Proceed with the next planned step only if no further review gates remain",
        "Send a substantive follow-up only if further bridge coordination is still needed",
    ]


def context_requires_action(agent: str, context: dict[str, Any]) -> bool:
    """Return True if the agent still needs to take action on this thread.

    A thread requires action when there is no valid outbound substantive reply from
    this agent after the canonical message was sent, or when the only outbound
    messages have failed status.

    Args:
        agent: The agent identifier being evaluated.
        context: An enriched bridge worker context dict.

    Returns:
        ``True`` if the agent must send a substantive reply or correction.
    """
    canonical = context.get("canonical_message") or {}
    canonical_status = str(canonical.get("status") or "").strip().lower()
    request_created_at = _parse_iso(canonical.get("created_at"))
    peer = _peer_sender_for_context(agent, context)
    if not peer:
        return False

    thread_messages = context.get("thread_messages") or []
    # Count substantive AND system (correction) outbound messages as satisfying the request.
    # Corrections are sent via send_correction_message() with tags=["system"] so they get
    # message_kind="system". They are valid responses that should prevent re-dispatch.
    substantive_outbound = [
        item
        for item in thread_messages
        if item.get("sender") == agent
        and item.get("recipient") == peer
        and item.get("message_kind") in ("substantive", "system")
        and (request_created_at is None or ((_parse_iso(item.get("created_at")) or _now()) > request_created_at))
    ]
    valid_outbound = [item for item in substantive_outbound if item.get("status") != "failed"]
    invalid_outbound = [item for item in substantive_outbound if item.get("status") == "failed"]
    protocol_outbound = [
        item
        for item in thread_messages
        if item.get("sender") == agent
        and item.get("recipient") == peer
        and item.get("message_kind") == "protocol_ack"
        and (request_created_at is None or ((_parse_iso(item.get("created_at")) or _now()) > request_created_at))
    ]
    if invalid_outbound:
        return True
    if valid_outbound:
        return False

    if canonical_status in {"completed", "failed"}:
        if protocol_outbound:
            return False
        return True

    return True


def _supersede_failed_outbound_messages(
    bridge: Any,
    *,
    failed_outbound: list[dict[str, Any]],
    resolution: str,
) -> int:
    """Mark all failed outbound messages as resolved with outcome ``"failed"`` and the given resolution."""
    resolved = 0
    for item in failed_outbound:
        bridge.resolve_message(
            message_id=item["id"],
            agent="owner",
            outcome="failed",
            resolution=resolution,
        )
        resolved += 1
    return resolved


def _load_worker_health_snapshot(
    agent: str,
    *,
    project_dir: Path,
) -> dict[str, Any]:
    """Read the health JSON file for the given agent worker, returning an empty dict on error."""
    path = project_dir / ".claude" / "hooks" / f".bridge-worker-{agent}-health.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _build_operating_state_message(
    bridge: Any,
    *,
    agent: str,
    project_dir: Path,
) -> tuple[str, str]:
    """Compose a session-start operating-state reply subject and body for the given agent."""
    self_health = _load_worker_health_snapshot(agent, project_dir=project_dir)
    peer_health = _load_worker_health_snapshot(agent_peer(agent), project_dir=project_dir)
    inbox = bridge.list_inbox(agent=agent, status="pending", limit=20)
    pending_count = int(inbox.get("count", 0) or 0)

    self_status = str(self_health.get("status") or "unknown").upper()
    peer_status = str(peer_health.get("status") or "unknown").upper()
    active_targets = [
        str(message_id).strip()
        for message_id in (self_health.get("active_message_ids") or [])
        if str(message_id).strip()
    ]
    subject_suffix = self_status if self_status != "UNKNOWN" else "online"
    subject = f"{agent_display(agent)} operating state: {subject_suffix}"

    lines = [
        f"{agent_display(agent)} operating state: {self_status}.",
        "",
        f"Bridge inbox: {pending_count} pending message(s).",
        f"Peer worker status: {peer_status}.",
    ]
    if active_targets:
        lines.append(f"Active dispatch targets: {', '.join(active_targets[:3])}.")
    return subject, "\n".join(lines)


def fast_path_session_start_requests(
    bridge: Any,
    *,
    agent: str,
    target_refs: list[str],
    project_dir: Path,
    log_fn: Callable[[str], None] | None = None,
) -> int:
    """Automatically reply to session-start probes without waking the full agent subprocess.

    For each target ref that is a session-start request, this function generates an
    operating-state reply and resolves the original request as ``"completed"`` in a
    single synchronous pass.

    Args:
        bridge: The bridge runtime module providing ``send_message`` and ``resolve_message``.
        agent: The agent identifier sending the replies.
        target_refs: Message IDs to check for session-start requests.
        project_dir: Project root directory used for health snapshot and artifact resolution.
        log_fn: Optional callable for writing diagnostic log lines.

    Returns:
        Number of threads handled by the fast path.
    """
    handled = 0
    contexts = build_contexts(
        bridge,
        agent=agent,
        explicit_refs=target_refs,
        new_items=[],
        project_dir=project_dir,
        log_fn=log_fn,
    )
    for context in contexts:
        canonical = context.get("canonical_message") or {}
        peer = _peer_sender_for_context(agent, context)
        if not peer:
            continue
        thread_messages = context.get("thread_messages") or []
        session_thread = any(message_is_session_start_request(message) for message in thread_messages)
        if not session_thread and not message_is_session_start_request(canonical):
            continue

        if not message_is_session_start_request(canonical):
            resolved = bridge.resolve_message(
                message_id=canonical["id"],
                agent=agent,
                outcome="completed",
                resolution=("Session-start operating-state reply received automatically. No follow-up reply required."),
            )
            if resolved.get("ok"):
                handled += 1
                if log_fn is not None:
                    log_fn(
                        f"session-start fast path auto-resolved reply on thread "
                        f"{context.get('thread_correlation_id')}: {canonical.get('id')}"
                    )
            continue

        request_created_at = _parse_iso(canonical.get("created_at"))
        substantive_outbound = [
            item
            for item in thread_messages
            if item.get("sender") == agent
            and item.get("recipient") == peer
            and item.get("message_kind") in ("substantive", "system")
            and (request_created_at is None or ((_parse_iso(item.get("created_at")) or _now()) > request_created_at))
        ]
        valid_outbound = [item for item in substantive_outbound if item.get("status") != "failed"]
        invalid_outbound = [item for item in substantive_outbound if item.get("status") == "failed"]

        if valid_outbound:
            if str(canonical.get("status") or "").strip().lower() not in {"completed", "failed"}:
                resolved = bridge.resolve_message(
                    message_id=canonical["id"],
                    agent=agent,
                    outcome="completed",
                    resolution=(
                        f"Session-start operating-state reply already exists on thread "
                        f"{context.get('thread_correlation_id')}."
                    ),
                )
                if resolved.get("ok"):
                    handled += 1
            handled += int(
                _supersede_failed_outbound_messages(
                    bridge,
                    failed_outbound=invalid_outbound,
                    resolution=(
                        f"Superseded by valid session-start operating-state reply on "
                        f"{context.get('thread_correlation_id')}."
                    ),
                )
                > 0
            )
            continue

        artifact_refs = _repair_payload_artifact_refs(context, project_dir=project_dir)
        subject, body = _build_operating_state_message(
            bridge,
            agent=agent,
            project_dir=project_dir,
        )
        payload = {
            "expected_response": "status_update",
            "artifact_refs": artifact_refs,
            "action_items": [
                "Use this operating-state report to confirm bridge liveness for the current session.",
                "Do not request another session-start status update unless bridge state changes materially.",
            ],
        }
        result = bridge.send_message(
            sender=agent,
            recipient=peer,
            subject=subject,
            body=body,
            payload_json=json.dumps(payload),
            tags_json=json.dumps(["bridge-sync", "session-start", "status"]),
            priority=max(1, int(canonical.get("priority") or 1)),
            correlation_id=context.get("thread_correlation_id"),
        )
        if result.get("status") == "failed":
            if log_fn is not None:
                log_fn(
                    f"session-start fast path failed validation for thread "
                    f"{context.get('thread_correlation_id')}: {result.get('validation_errors')}"
                )
            continue

        resolved = bridge.resolve_message(
            message_id=canonical["id"],
            agent=agent,
            outcome="completed",
            resolution=(f"Session-start operating-state reply sent via bridge message {result.get('id')}."),
        )
        if resolved.get("ok"):
            handled += 1
        handled += int(
            _supersede_failed_outbound_messages(
                bridge,
                failed_outbound=invalid_outbound,
                resolution=(
                    f"Superseded by session-start operating-state reply {result.get('id')} "
                    f"on thread {context.get('thread_correlation_id')}."
                ),
            )
            > 0
        )
        if log_fn is not None:
            log_fn(
                f"session-start fast path replied on thread {context.get('thread_correlation_id')}: {result.get('id')}"
            )
    return handled


def repair_terminal_thread_outputs(
    bridge: Any,
    *,
    agent: str,
    target_refs: list[str],
    project_dir: Path,
    log_fn: Callable[[str], None] | None = None,
) -> int:
    """Repair threads that are stuck due to failed outbound messages or unresolved terminal states.

    Handles several repair cases without invoking the full agent subprocess:
    closure-only threads, valid substantive replies that were not closed, and
    failed outbound messages that need superseding.

    Args:
        bridge: The bridge runtime module providing ``send_message`` and ``resolve_message``.
        agent: The agent identifier performing the repairs.
        target_refs: Message IDs of threads to inspect and potentially repair.
        project_dir: Project root directory used for artifact resolution.
        log_fn: Optional callable for writing diagnostic log lines.

    Returns:
        Number of threads repaired.
    """
    repaired = 0
    contexts = build_contexts(
        bridge,
        agent=agent,
        explicit_refs=target_refs,
        new_items=[],
        project_dir=project_dir,
        log_fn=log_fn,
    )
    for context in contexts:
        canonical = context.get("canonical_message") or {}
        peer = _peer_sender_for_context(agent, context)
        if not peer:
            continue
        expected_response = str(canonical.get("expected_response") or "").strip().lower()
        canonical_status = str(canonical.get("status") or "").strip().lower()
        request_created_at = _parse_iso(canonical.get("created_at"))

        thread_messages = context.get("thread_messages") or []
        substantive_outbound = [
            item
            for item in thread_messages
            if item.get("sender") == agent
            and item.get("recipient") == peer
            and item.get("message_kind") == "substantive"
            and (request_created_at is None or ((_parse_iso(item.get("created_at")) or _now()) > request_created_at))
        ]
        valid_outbound = [item for item in substantive_outbound if item.get("status") != "failed"]
        invalid_outbound = [item for item in substantive_outbound if item.get("status") == "failed"]
        protocol_outbound = [
            item
            for item in thread_messages
            if item.get("sender") == agent
            and item.get("recipient") == peer
            and item.get("message_kind") == "protocol_ack"
            and (request_created_at is None or ((_parse_iso(item.get("created_at")) or _now()) > request_created_at))
        ]
        if message_is_closure_only(canonical):
            if canonical_status not in {"completed", "failed"}:
                resolved = bridge.resolve_message(
                    message_id=canonical["id"],
                    agent=agent,
                    outcome="completed",
                    resolution=(
                        "Closure-only or receipt-only traffic on previously handled thread. No new action required."
                    ),
                )
                if resolved.get("ok"):
                    repaired += 1
                    if log_fn is not None:
                        log_fn(
                            f"terminal repair closed closure-only thread without peer resend: "
                            f"{context.get('thread_correlation_id')}"
                        )
            repaired += int(
                _supersede_failed_outbound_messages(
                    bridge,
                    failed_outbound=invalid_outbound,
                    resolution=(
                        f"Superseded after closure-only thread cleanup on {context.get('thread_correlation_id')}."
                    ),
                )
                > 0
            )
            continue

        if valid_outbound:
            if canonical_status not in {"completed", "failed"}:
                latest_valid = valid_outbound[-1]
                resolved = bridge.resolve_message(
                    message_id=canonical["id"],
                    agent=agent,
                    outcome="completed",
                    resolution=(
                        f"Closed after substantive reply {latest_valid.get('id')} "
                        f"on thread {context.get('thread_correlation_id')}."
                    ),
                )
                if resolved.get("ok"):
                    repaired += 1
                    if log_fn is not None:
                        log_fn(
                            f"terminal repair closed request after substantive reply on "
                            f"thread {context.get('thread_correlation_id')}: {latest_valid.get('id')}"
                        )
            repaired += int(
                _supersede_failed_outbound_messages(
                    bridge,
                    failed_outbound=invalid_outbound,
                    resolution=(
                        f"Superseded by valid substantive outbound bridge message on thread "
                        f"{context.get('thread_correlation_id')}."
                    ),
                )
                > 0
            )
            continue

        if canonical_status == "completed" and protocol_outbound:
            repaired += int(
                _supersede_failed_outbound_messages(
                    bridge,
                    failed_outbound=invalid_outbound,
                    resolution=(
                        f"Superseded by legacy protocol acknowledgement on thread "
                        f"{context.get('thread_correlation_id')}."
                    ),
                )
                > 0
            )
            continue

        if canonical_status not in {"completed", "failed"} and expected_response == "acknowledgement":
            resolved = bridge.resolve_message(
                message_id=canonical["id"],
                agent=agent,
                outcome="failed",
                resolution=(
                    "Acknowledgement-only bridge requests are no longer supported. "
                    "Sender must wait for a substantive reply."
                ),
            )
            if resolved.get("ok"):
                repaired += 1
                if log_fn is not None:
                    log_fn(
                        f"terminal repair closed acknowledgement-only thread after protocol change: "
                        f"{context.get('thread_correlation_id')}"
                    )
            repaired += int(
                _supersede_failed_outbound_messages(
                    bridge,
                    failed_outbound=invalid_outbound,
                    resolution=(
                        f"Superseded after acknowledgement-only thread closure on "
                        f"{context.get('thread_correlation_id')}."
                    ),
                )
                > 0
            )
            continue

        artifact_refs = _repair_payload_artifact_refs(context, project_dir=project_dir)

        subject = ""
        body = ""
        if invalid_outbound:
            latest_invalid = invalid_outbound[-1]
            subject = str(latest_invalid.get("subject") or "").strip()
            body = str(latest_invalid.get("body") or "").strip()
        elif canonical.get("status") in {"completed", "failed"} and canonical.get("resolution"):
            outcome = str(canonical.get("status") or "done").upper()
            subject = f"Re: {canonical.get('subject', 'Bridge thread')} — {outcome}"
            body = f"Thread completed with outcome {outcome}.\n\n{canonical.get('resolution')}"
        else:
            continue

        if not subject or not body:
            continue

        outcome_value = str(canonical.get("status") or "completed").lower()
        payload = {
            "expected_response": "status_update",
            "artifact_refs": artifact_refs,
            "action_items": _default_action_items(outcome_value),
        }
        result = bridge.send_message(
            sender=agent,
            recipient=peer,
            subject=subject,
            body=body,
            payload_json=json.dumps(payload),
            tags_json=json.dumps(["bridge-sync", "review", outcome_value or "completed"]),
            priority=int(canonical.get("priority") or 2),
            correlation_id=context.get("thread_correlation_id"),
        )
        if result.get("status") == "failed":
            if log_fn is not None:
                log_fn(
                    f"terminal repair failed validation for thread {context.get('thread_correlation_id')}: "
                    f"{result.get('validation_errors')}"
                )
            continue

        repaired += 1
        if log_fn is not None:
            log_fn(
                f"terminal repair sent valid outbound for thread {context.get('thread_correlation_id')}: "
                f"{result.get('id')}"
            )
        _supersede_failed_outbound_messages(
            bridge,
            failed_outbound=invalid_outbound,
            resolution=(
                f"Superseded by repaired canonical outbound bridge message {result.get('id')} "
                f"on thread {context.get('thread_correlation_id')}."
            ),
        )
    return repaired
