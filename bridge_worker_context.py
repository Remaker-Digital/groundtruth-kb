from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


PROJECT_DIR = Path(__file__).resolve().parent
WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:\\[^\r\n<>]*")
ARTIFACT_NAME_RE = re.compile(
    r"\b(?:INSIGHTS-[A-Za-z0-9-]+\.md|BRIDGE-RESPONSIVENESS-LEDGER\.md|[A-Za-z0-9._-]+\.(?:md|json|txt))\b"
)
DEFAULT_MAX_DISPATCH_TARGETS = 6


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def agent_peer(agent: str) -> str:
    return "prime" if agent == "codex" else "codex"


def agent_display(agent: str) -> str:
    return "Codex" if agent == "codex" else "Prime"


def iter_text_fragments(value: Any) -> list[str]:
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
        items: list[str] = []
        for nested in value:
            items.extend(iter_text_fragments(nested))
        return items
    return []


def clean_path_candidate(raw: str) -> str:
    return raw.strip().strip("`'\"()[]{}<>").rstrip(".,:;")


def resolve_artifact_name(name: str, *, project_dir: Path = PROJECT_DIR) -> Path | None:
    candidate = Path(name)
    if candidate.is_absolute() and candidate.exists():
        return candidate.resolve()
    if not candidate.is_absolute():
        direct = (project_dir / candidate).resolve()
        if direct.exists():
            return direct

    search_roots = [
        project_dir / "independent-progress-assessments" / "CODEX-INSIGHT-DROPBOX",
        project_dir / "independent-progress-assessments",
        project_dir,
    ]
    matches: list[Path] = []
    for root in search_roots:
        if not root.exists():
            continue
        root_matches = list(root.rglob(name))
        for match in root_matches:
            if match.is_file() and match not in matches:
                matches.append(match)
        if len(matches) == 1:
            break
    if len(matches) == 1:
        return matches[0].resolve()
    return None


def _resolve_structured_artifact_ref(raw: Any, *, project_dir: Path = PROJECT_DIR) -> Path | None:
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


def discover_artifacts(context: dict[str, Any], *, project_dir: Path = PROJECT_DIR) -> list[dict[str, str]]:
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
            path = resolve_artifact_name(cleaned, project_dir=project_dir)
            if path is not None:
                found[str(path)] = {
                    "path": str(path),
                    "source": "artifact-name",
                }

    return sorted(found.values(), key=lambda item: item["path"])


def summarize_context(agent: str, context: dict[str, Any]) -> str:
    canonical = context["canonical_message"]
    latest_worker = context.get(
        "latest_non_protocol_codex_message"
        if agent == "codex"
        else "latest_non_protocol_prime_message"
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
    claimed_items: list[dict[str, Any]],
    contexts: list[dict[str, Any]],
    *,
    project_dir: Path = PROJECT_DIR,
) -> str:
    if contexts:
        context_lines = "\n".join(summarize_context(agent, context) for context in contexts)
    else:
        context_lines = "- none"
    worker_name = agent_display(agent)
    return f"""Start in Loyal Opposition mode for Agent Red in {project_dir}.

Load AGENTS.md and the required startup files under independent-progress-assessments/ before doing other work.

A bridge wake was triggered because pending work or bridge-risk signals exist for agent `{agent}`.

Canonical bridge snapshot:
{snapshot_path}

Pending new inbox count: {len(new_items)}
Pending claimed/immediate count: {len(claimed_items)}

Target thread summaries:
{context_lines}

Required actions:
1. Read the canonical bridge snapshot before narrating any pickup.
2. Process only the target thread summaries plus the pending inbox IDs listed in the canonical bridge snapshot for this wake.
3. If a target is malformed or has bridge status `invalid`, do not claim it; use `send_correction_message(...)` with the invalid message id and do not send freeform correction traffic via `send_message(...)`.
4. If a target already has a prior {worker_name} review or final outbound verdict in the snapshot, do not narrate a fresh review; treat it as resend/closure work and cite the canonical report path if present.
5. Do not auto-accept substantive work on sight; accept only after context inspection confirms the work you are actually taking.
6. Treat claimed items as active work and send status immediately if any claimed thread has exceeded the 10-minute update cadence or a thread is flagged with `claimed_thread_silence_breach`.
7. If a thread is flagged with `ack_breach` or `response_window_breach`, address that breach before lower-priority work and reflect the timing miss in independent-progress-assessments/BRIDGE-RESPONSIVENESS-LEDGER.md.
8. Process requests end-to-end without waiting for owner approval unless blocked by a true external decision.
9. If the bridge is clear after processing, state that explicitly and exit.
"""


def claimed_item_due(agent: str, item: dict[str, Any], state: dict[str, Any], cadence_minutes: int) -> bool:
    if item.get("claimed_by") != agent:
        return False

    claimed_at = _parse_iso(item.get("claimed_at"))
    if claimed_at is None:
        return True

    age_seconds = (_now() - claimed_at).total_seconds()
    if age_seconds < cadence_minutes * 60:
        return False

    last_wake = _parse_iso(state.get("last_wake_by_message", {}).get(item["id"]))
    if last_wake is None:
        return True

    return (_now() - last_wake).total_seconds() >= cadence_minutes * 60


def build_context_snapshot(
    *,
    trigger: str,
    contexts: list[dict[str, Any]],
    new_items: list[dict[str, Any]],
    due_claimed: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "generated_at": _now().isoformat(),
        "trigger": trigger,
        "new_inbox_ids": [item["id"] for item in new_items],
        "claimed_or_immediate_ids": [item["id"] for item in due_claimed],
        "contexts": contexts,
    }


def select_dispatch_batch(
    contexts: list[dict[str, Any]],
    new_items: list[dict[str, Any]],
    due_claimed: list[dict[str, Any]],
    *,
    max_targets: int = DEFAULT_MAX_DISPATCH_TARGETS,
) -> dict[str, Any]:
    if max_targets < 1:
        raise ValueError("max_targets must be at least 1")

    ordered_ids: list[str] = []
    for context in contexts:
        canonical_id = str((context.get("canonical_message") or {}).get("id") or "").strip()
        if canonical_id and canonical_id not in ordered_ids:
            ordered_ids.append(canonical_id)
    for item in list(new_items) + list(due_claimed):
        message_id = str(item.get("id") or "").strip()
        if message_id and message_id not in ordered_ids:
            ordered_ids.append(message_id)

    selected_ids = ordered_ids[:max_targets]
    selected_set = set(selected_ids)

    return {
        "contexts": [
            context
            for context in contexts
            if str((context.get("canonical_message") or {}).get("id") or "").strip() in selected_set
        ],
        "new_items": [item for item in new_items if str(item.get("id") or "").strip() in selected_set],
        "due_claimed": [item for item in due_claimed if str(item.get("id") or "").strip() in selected_set],
        "target_ids": selected_ids,
        "deferred_ids": ordered_ids[max_targets:],
    }


def _worker_context(
    bridge: Any,
    message_ref: str,
    *,
    agent: str,
) -> dict[str, Any] | None:
    context_builder = getattr(bridge, "get_worker_event_payload", None)
    if callable(context_builder):
        payload = context_builder(message_ref, agent=agent)
        if isinstance(payload, dict) and "context" in payload:
            context = payload.get("context")
            return context if isinstance(context, dict) else None
        return payload if isinstance(payload, dict) else None
    return bridge.describe_thread_context(message_ref, recipient=agent)


def build_contexts(
    bridge: Any,
    *,
    agent: str,
    explicit_refs: list[str],
    new_items: list[dict[str, Any]],
    due_claimed: list[dict[str, Any]],
    project_dir: Path = PROJECT_DIR,
    log_fn: Callable[[str], None] | None = None,
) -> list[dict[str, Any]]:
    reasons_by_id: dict[str, set[str]] = {}

    for item in new_items:
        reasons_by_id.setdefault(item["id"], set()).add("new")
    for item in due_claimed:
        reasons_by_id.setdefault(item["id"], set()).add("claimed-cadence")
    for message_ref in explicit_refs:
        context = _worker_context(bridge, message_ref, agent=agent)
        if context is None:
            if log_fn is not None:
                log_fn(f"explicit wake target unresolved: {message_ref}")
            continue
        canonical_id = context["canonical_message"]["id"]
        reasons_by_id.setdefault(canonical_id, set()).add(f"explicit:{message_ref}")

    contexts: list[dict[str, Any]] = []
    for message_id, reasons in sorted(reasons_by_id.items()):
        context = _worker_context(bridge, message_id, agent=agent)
        if context is None:
            continue
        thread_sla = context.get("thread_sla") or {}
        for risk_type in thread_sla.get("risk_types", []):
            reasons.add(risk_type)
        canonical = context.get("canonical_message") or {}
        if canonical.get("status") == "invalid":
            reasons.add("invalid")
        context["wake_reasons"] = sorted(reasons)
        context["referenced_artifacts"] = discover_artifacts(context, project_dir=project_dir)
        latest_worker = context.get(
            "latest_non_protocol_codex_message"
            if agent == "codex"
            else "latest_non_protocol_prime_message"
        )
        context["already_reviewed_hint"] = bool(
            latest_worker and latest_worker.get("id") != context["canonical_message"]["id"]
        )
        contexts.append(context)
    return contexts


def _peer_sender_for_context(agent: str, context: dict[str, Any]) -> str | None:
    canonical = context.get("canonical_message") or {}
    sender = canonical.get("sender")
    recipient = canonical.get("recipient")
    if recipient == agent and sender in {"codex", "prime"}:
        return str(sender)
    return None


def _default_action_items(outcome: str) -> list[str]:
    if outcome == "blocked":
        return [
            "Acknowledge receipt of this review",
            "Send a revised implementation or plan if further review is needed",
        ]
    if outcome == "superseded":
        return [
            "Acknowledge receipt of this update",
            "Use the newest thread guidance if further action is still needed",
        ]
    return [
        "Acknowledge receipt of this review",
        "Proceed with the next planned step only if no further review gates remain",
    ]


def repair_terminal_thread_outputs(
    bridge: Any,
    *,
    agent: str,
    target_refs: list[str],
    project_dir: Path = PROJECT_DIR,
    log_fn: Callable[[str], None] | None = None,
) -> int:
    repaired = 0
    contexts = build_contexts(
        bridge,
        agent=agent,
        explicit_refs=target_refs,
        new_items=[],
        due_claimed=[],
        project_dir=project_dir,
        log_fn=log_fn,
    )
    for context in contexts:
        canonical = context.get("canonical_message") or {}
        peer = _peer_sender_for_context(agent, context)
        if not peer:
            continue

        thread_messages = context.get("thread_messages") or []
        substantive_outbound = [
            item
            for item in thread_messages
            if item.get("sender") == agent
            and item.get("recipient") == peer
            and item.get("message_kind") == "substantive"
        ]
        valid_outbound = [item for item in substantive_outbound if item.get("status") != "invalid"]
        invalid_outbound = [item for item in substantive_outbound if item.get("status") == "invalid"]

        if valid_outbound:
            for item in invalid_outbound:
                bridge.resolve_message(
                    message_id=item["id"],
                    agent="owner",
                    outcome="superseded",
                    resolution=(
                        f"Superseded by valid substantive outbound bridge message on thread "
                        f"{context.get('thread_correlation_id')}."
                    ),
                )
            continue

        artifact_refs = [
            {"type": "file", "path": item["path"], "note": "Bridge artifact"}
            for item in context.get("referenced_artifacts", [])
        ]

        subject = ""
        body = ""
        if invalid_outbound:
            latest_invalid = invalid_outbound[-1]
            subject = str(latest_invalid.get("subject") or "").strip()
            body = str(latest_invalid.get("body") or "").strip()
        elif canonical.get("status") in {"done", "blocked", "superseded"} and canonical.get("resolution"):
            outcome = str(canonical.get("status") or "done").upper()
            subject = f"Re: {canonical.get('subject', 'Bridge thread')} — {outcome}"
            body = f"Thread completed with outcome {outcome}.\n\n{canonical.get('resolution')}"
        else:
            continue

        if not subject or not body:
            continue

        outcome_value = str(canonical.get("status") or "done").lower()
        payload = {
            "expected_response": "acknowledgement",
            "response_window": "session",
            "artifact_refs": artifact_refs,
            "action_items": _default_action_items(outcome_value),
        }
        result = bridge.send_message(
            sender=agent,
            recipient=peer,
            subject=subject,
            body=body,
            payload_json=json.dumps(payload),
            tags_json=json.dumps(["bridge-sync", "review", outcome_value or "done"]),
            priority=int(canonical.get("priority") or 2),
            correlation_id=context.get("thread_correlation_id"),
        )
        if result.get("status") == "invalid":
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
        for item in invalid_outbound:
            bridge.resolve_message(
                message_id=item["id"],
                agent="owner",
                outcome="superseded",
                resolution=(
                    f"Superseded by repaired canonical outbound bridge message {result.get('id')} "
                    f"on thread {context.get('thread_correlation_id')}."
                ),
            )
    return repaired
