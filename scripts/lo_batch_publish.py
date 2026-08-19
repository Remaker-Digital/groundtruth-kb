"""Governed batch publisher for Loyal Opposition verdicts (WI-5939).

This module is the tracked, change-controlled home for the batch verdict
publisher that previously lived as an untracked script on a runtime-state
surface. It publishes reviewer-supplied verdicts through the governed substrate
(`publish_lo_verdict`, `prepare_verdict_candidate`, and the work-intent claim
registry) while guaranteeing four properties the untracked predecessor did not:

1. **Truthful runtime provenance.** The publishing session id, harness name, and
   publication date are resolved from the runtime envelope/environment at call
   time. No session-id or date literal is embedded in this module.
2. **Computed review independence.** The responded-to artifact's author session
   is read and compared to the publishing session. Publication is refused when
   they are equal (self-review) and refused when the author session metadata is
   missing or unreadable (fail closed), per
   `.claude/rules/file-bridge-protocol.md` section Review Independence Boundary
   and `.claude/rules/codex-review-gate.md` section Review Independence Gate.
3. **Honest deliberation disclosure.** The emitted body never claims a
   deliberation-search result that was not supplied by the reviewing session.
4. **Serialized, throttled publication.** Items are published one at a time with
   a bounded minimum interval and exponential backoff on contention, because
   bridge publication is a serialized contended resource (DELIB-202667526) and
   unthrottled publication destabilizes the `bridge/*-NNN.md` aggregate
   generation (WI-5933 currentness livelock).

This module is a transport. It does not perform review; the reviewing session
supplies the findings. Its contract is that everything it writes about
provenance is true.

Input JSON schema (list of items)::

    [{"slug": str,
      "verdict": "GO" | "NO-GO" | "VERIFIED",
      "version": int | None,
      "responds": str | None,
      "title": str | None,
      "summary": str | None,
      "prior_deliberations": [str] | None,
      "findings": [{"severity", "claim", "evidence", "impact", "action"}]}]

Copyright (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from scripts.bridge_applicability_preflight import prepare_verdict_candidate  # noqa: E402
from scripts.bridge_author_metadata import (  # noqa: E402
    extract_author_metadata,
    load_author_metadata,
)
from scripts.bridge_work_intent_registry import acquire, release  # noqa: E402
from scripts.gtkb_bridge_writer import next_free_bridge_version, publish_lo_verdict  # noqa: E402

VERSIONED_RE = re.compile(r"^(?P<slug>.+)-(?P<ver>\d{3})\.md$")

ACTIONABLE_PREDECESSOR_STATUSES = frozenset({"NEW", "REVISED", "NO-ACTION"})

#: Minimum seconds between successive publications. Publication is a serialized
#: contended resource; see DELIB-202667526 and the WI-5933 livelock.
DEFAULT_MIN_INTERVAL_SECONDS = 5.0
DEFAULT_MAX_RETRIES = 4
DEFAULT_BACKOFF_BASE_SECONDS = 2.0
DEFAULT_CLAIM_TTL_SECONDS = 3600

_CONTENTION_MARKERS = (
    "another bridge publication capability is active",
    "timed out acquiring registry lock",
    "database is locked",
    "busy",
    "lock",
    "already exists",
    "git history",
    "bounded per-slug version allocation exhausted",
    "no free per-slug bridge version",
)


class PublisherProvenanceError(RuntimeError):
    """Raised when truthful publisher provenance cannot be established."""


class ReviewIndependenceError(RuntimeError):
    """Raised when review independence cannot be affirmatively established."""


def resolve_publisher_identity(
    project_root: Path,
    *,
    env: Mapping[str, str] | None = None,
    explicit: Mapping[str, Any] | None = None,
) -> dict[str, str]:
    """Resolve truthful author metadata for the publishing session.

    Fails closed rather than substituting a placeholder: a publisher that cannot
    prove who it is must not write to the governed audit trail.
    """
    environ = env if env is not None else os.environ
    try:
        metadata = load_author_metadata(project_root, explicit=explicit, env=environ)
    except Exception as exc:  # noqa: BLE001 - surfaced as a typed provenance failure
        raise PublisherProvenanceError(
            f"author metadata could not be resolved: {exc}"
        ) from exc

    session_id = str(metadata.get("author_session_context_id") or "").strip()
    if not session_id:
        raise PublisherProvenanceError(
            "publishing session context id is unresolved; set the harness session "
            "environment or open a session envelope before publishing"
        )
    identity = str(metadata.get("author_identity") or "").strip()
    if not identity:
        raise PublisherProvenanceError(
            "author identity is unresolved for the publishing session"
        )
    return {str(k): str(v) for k, v in metadata.items()}


def harness_name_from_identity(author_identity: str) -> str:
    """Extract the harness name from a ``role/harness[/id]`` author identity."""
    parts = [part for part in str(author_identity).split("/") if part]
    if len(parts) < 2:
        raise PublisherProvenanceError(
            f"author identity is not role/harness shaped: {author_identity!r}"
        )
    return parts[1]


def latest_version(project_root: Path, slug: str) -> tuple[int, Path]:
    """Return the highest existing version number and path for ``slug``."""
    best_version = 0
    best_path: Path | None = None
    for path in (project_root / "bridge").glob(f"{slug}-*.md"):
        match = VERSIONED_RE.match(path.name)
        if not match or match.group("slug") != slug:
            continue
        version = int(match.group("ver"))
        if version > best_version:
            best_version = version
            best_path = path
    if best_path is None:
        raise FileNotFoundError(f"no versioned bridge files for slug {slug!r}")
    return best_version, best_path


def read_author_session(path: Path) -> str | None:
    """Return the author session context id recorded in a bridge artifact.

    Returns ``None`` when the artifact is unreadable or records no author
    session, so callers can fail closed on an unverifiable predecessor.
    """
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    session_id = str(
        extract_author_metadata(content).get("author_session_context_id") or ""
    ).strip()
    return session_id or None


def assert_review_independence(reviewer_session: str, responds_path: Path) -> str:
    """Verify the reviewer session differs from the responded-to author session.

    This is a computed check, not an assertion: the protocol requires review
    independence to fail closed when author session metadata is missing or
    unreadable.
    """
    author_session = read_author_session(responds_path)
    if not author_session:
        raise ReviewIndependenceError(
            f"review independence cannot be verified: {responds_path.name} records no readable "
            "author_session_context_id (fail closed)"
        )
    if author_session == reviewer_session:
        raise ReviewIndependenceError(
            f"self-review refused: {responds_path.name} was authored by the publishing session {reviewer_session}"
        )
    return author_session


def findings_markdown(findings: Sequence[Mapping[str, Any]] | None) -> str:
    if not findings:
        return "_No defect findings beyond residual notes._\n"
    blocks = []
    for index, finding in enumerate(findings, 1):
        blocks.append(
            f"### Finding {index} ({finding.get('severity', 'P3')})\n\n"
            f"- **Claim:** {finding.get('claim', '')}\n"
            f"- **Evidence:** {finding.get('evidence', '')}\n"
            f"- **Impact:** {finding.get('impact', '')}\n"
            f"- **Recommended action:** {finding.get('action', '')}\n"
        )
    return "\n".join(blocks)


def prior_deliberations_markdown(item: Mapping[str, Any]) -> str:
    """Render prior deliberations without claiming an unperformed search."""
    entries = item.get("prior_deliberations")
    if entries:
        return "\n".join(f"- {entry}" for entry in entries) + "\n"
    return (
        "_No deliberation search was performed by this publishing transport. The "
        "reviewing session supplied no prior-deliberation citations for this "
        "thread; this is a disclosure of what was done, not a finding that no "
        "prior deliberations exist._\n"
    )


def build_body(
    item: Mapping[str, Any],
    *,
    next_version: int,
    responds: str,
    author_metadata: Mapping[str, str],
    reviewer_session: str,
    predecessor_session: str,
    published_date: str,
) -> str:
    """Build a verdict body whose provenance statements are all computed."""
    verdict = str(item["verdict"]).upper()
    slug = item["slug"]
    title = item.get("title") or f"{slug} review"
    summary = item.get("summary") or f"{verdict} on {responds}."
    identity = author_metadata.get("author_identity", "")
    harness_id = author_metadata.get("author_harness_id", "")
    next_step = (
        "Prime Builder may proceed only after a fresh go_implementation claim and "
        "an implementation-start packet for the exact declared targets."
        if verdict == "GO"
        else "Prime Builder must file a substantive REVISED response addressing every P0/P1 finding above."
    )
    return f"""{verdict}
::init gtkb lo
::open test
author_identity: {identity}
author_harness_id: {harness_id}
author_session_context_id: {reviewer_session}
author_model: {author_metadata.get("author_model", "")}
author_model_version: {author_metadata.get("author_model_version", "")}
author_model_configuration: {author_metadata.get("author_model_configuration", "")}

bridge_kind: lo_verdict
Document: {slug}
Version: {next_version:03d}
Date: {published_date} UTC
Responds to: {responds}
Reviewer: Loyal Opposition ({identity})

# Loyal Opposition Review - {title}

## Verdict

{summary}

## First-Line Role Eligibility And Review Independence

- Role: loyal-opposition (`::init gtkb lo`).
- Reviewer session: `{reviewer_session}`.
- Responded-to author session: `{predecessor_session}`.
- Independence: computed by comparing the two session ids above; publication
  fails closed when they are equal or when the predecessor records no readable
  author session.
- Active work-intent claim held by this session before publication.

## Findings

{findings_markdown(item.get("findings"))}

## Prior Deliberations

{prior_deliberations_markdown(item)}

## Required Next Step

{next_step}

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""


def _is_contention(exc: BaseException) -> bool:
    message = str(exc).lower()
    return any(marker in message for marker in _CONTENTION_MARKERS)


def publish_one(
    item: Mapping[str, Any],
    *,
    project_root: Path = PROJECT_ROOT,
    author_metadata: Mapping[str, str] | None = None,
    env: Mapping[str, str] | None = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_base_seconds: float = DEFAULT_BACKOFF_BASE_SECONDS,
    sleep: Any = time.sleep,
    claim_ttl_seconds: int = DEFAULT_CLAIM_TTL_SECONDS,
) -> dict[str, Any]:
    """Publish a single verdict with computed provenance and bounded retries."""
    slug = item["slug"]
    metadata = dict(
        author_metadata or resolve_publisher_identity(project_root, env=env)
    )
    reviewer_session = metadata["author_session_context_id"]
    harness_name = harness_name_from_identity(metadata["author_identity"])

    _, latest_path = latest_version(project_root, slug)
    responds = item.get("responds") or f"bridge/{latest_path.name}"
    responds_path = project_root / responds

    status = (
        latest_path.read_text(encoding="utf-8", errors="replace")
        .splitlines()[0]
        .strip()
        .upper()
    )
    if status not in ACTIONABLE_PREDECESSOR_STATUSES:
        return {
            "slug": slug,
            "ok": False,
            "error": f"latest_status_not_actionable:{status}",
        }

    try:
        predecessor_session = assert_review_independence(
            reviewer_session, responds_path
        )
    except ReviewIndependenceError as exc:
        return {"slug": slug, "ok": False, "error": f"review_independence: {exc}"}

    published_date = datetime.now(UTC).strftime("%Y-%m-%d")

    if not acquire(
        slug, reviewer_session, ttl_seconds=claim_ttl_seconds, project_root=project_root
    ):
        return {"slug": slug, "ok": False, "error": "claim_held"}

    attempt = 0
    try:
        while True:
            next_version = next_free_bridge_version(project_root, slug)
            requested = item.get("version")
            if requested is not None:
                requested_version = int(requested)
                hinted = project_root / "bridge" / f"{slug}-{requested_version:03d}.md"
                if requested_version >= 1 and not hinted.exists():
                    next_version = requested_version
            body = build_body(
                item,
                next_version=next_version,
                responds=responds,
                author_metadata=metadata,
                reviewer_session=reviewer_session,
                predecessor_session=predecessor_session,
                published_date=published_date,
            )
            try:
                body = prepare_verdict_candidate(
                    candidate_path=f"bridge/{slug}-{next_version:03d}.md",
                    content=body,
                    project_root=project_root,
                )
            except Exception as exc:  # noqa: BLE001 - reported as a per-item failure
                return {
                    "slug": slug,
                    "ok": False,
                    "error": f"prepare_failed: {type(exc).__name__}: {exc}",
                }
            try:
                published = publish_lo_verdict(
                    slug,
                    str(item["verdict"]).upper(),
                    body,
                    project_root,
                    session_id=reviewer_session,
                    harness_name=harness_name,
                    author_metadata=metadata,
                )
                return {
                    "slug": slug,
                    "ok": True,
                    "result": published.to_dict(),
                    "attempts": attempt + 1,
                }
            except Exception as exc:  # noqa: BLE001 - retried only when contention-shaped
                attempt += 1
                if attempt > max_retries or not _is_contention(exc):
                    return {
                        "slug": slug,
                        "ok": False,
                        "error": f"{type(exc).__name__}: {exc}",
                        "attempts": attempt,
                    }
                sleep(backoff_base_seconds * (2 ** (attempt - 1)))
    finally:
        try:
            release(slug, reviewer_session, project_root=project_root)
        except Exception:  # noqa: BLE001 - release is best-effort cleanup
            pass


def publish_batch(
    items: Sequence[Mapping[str, Any]],
    *,
    project_root: Path = PROJECT_ROOT,
    env: Mapping[str, str] | None = None,
    min_interval_seconds: float = DEFAULT_MIN_INTERVAL_SECONDS,
    sleep: Any = time.sleep,
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_base_seconds: float = DEFAULT_BACKOFF_BASE_SECONDS,
    on_event: Any = None,
) -> list[dict[str, Any]]:
    """Publish items serially with a bounded minimum interval between writes.

    Publication is serialized rather than concurrent: the control-plane lock and
    the platform-wide single-active-capability constraint make concurrent
    publication self-defeating, and unthrottled publication destabilizes the
    bridge aggregate generation.
    """
    metadata = resolve_publisher_identity(project_root, env=env)
    results: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if index > 0 and min_interval_seconds > 0:
            if on_event:
                on_event(
                    {
                        "event": "throttle",
                        "slug": item.get("slug"),
                        "seconds": min_interval_seconds,
                    }
                )
            sleep(min_interval_seconds)
        result = publish_one(
            item,
            project_root=project_root,
            author_metadata=metadata,
            env=env,
            max_retries=max_retries,
            backoff_base_seconds=backoff_base_seconds,
            sleep=sleep,
        )
        results.append(result)
        if on_event:
            on_event(
                {
                    "event": "published" if result.get("ok") else "failed",
                    **{k: v for k, v in result.items() if k != "result"},
                }
            )
    return results


def main(argv: Sequence[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Publish Loyal Opposition verdicts from a recommendations JSON file."
    )
    parser.add_argument(
        "recs", type=Path, help="Path to the recommendations JSON file."
    )
    parser.add_argument(
        "--min-interval-seconds",
        type=float,
        default=DEFAULT_MIN_INTERVAL_SECONDS,
        help="Minimum seconds between successive publications.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Override the project root.",
    )
    args = parser.parse_args(list(argv))

    items = json.loads(args.recs.read_text(encoding="utf-8"))

    def emit(event: Mapping[str, Any]) -> None:
        print(json.dumps(event, default=str), flush=True)

    try:
        results = publish_batch(
            items,
            project_root=args.project_root,
            min_interval_seconds=args.min_interval_seconds,
            on_event=emit,
        )
    except PublisherProvenanceError as exc:
        print(f"PROVENANCE FAILURE (fail closed): {exc}", file=sys.stderr)
        return 3

    ok = sum(1 for result in results if result.get("ok"))
    print(f"DONE {ok}/{len(results)}", flush=True)
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
