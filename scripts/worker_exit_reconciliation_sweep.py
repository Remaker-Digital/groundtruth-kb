#!/usr/bin/env python
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Out-of-band reconciliation of runtime state stranded by non-wrapping workers.

WI-6037 Slice 1. GT-KB releases work-intent claims, disposes implementation-start
authorization packets, and cleans scratch drafts through in-process paths. A worker
killed by an external timeout never reaches any of them, so every such kill strands
state that later sessions read as live.

**Why this is not a ``Stop`` hook.** The existing sweeper precedent,
``scripts/auto_finalize_sweep.py``, is registered on ``Stop``. ``Stop`` is precisely the
event a hard-killed worker never reaches, so that shape cannot address this class.
Reconciliation must run out-of-band from the dying process: at the next session's start,
or from an operator invocation. Slice 1 therefore delivers a standalone invocable script;
hook registration is deliberately deferred to Slice 2 (``.claude/settings.json`` carries
uncommitted changes from another lane at the time of writing).

**Report-only by default.** A bare invocation mutates nothing. ``--apply`` is required to
reclaim, and even then only records whose own recorded expiry has passed are touched.

Invariants (all test-encoded in
``platform_tests/scripts/test_worker_exit_reconciliation_sweep.py``):

1. Report-only by default; a bare run is side-effect free.
2. Never reclaim live state -- a record not expired by its own recorded TTL is never
   touched under either mode.
3. Never touch the bridge audit trail -- no ``bridge/*.md`` file is read for mutation,
   deleted, rewritten, moved, or staged.
4. Never touch git -- no ``git`` subprocess is invoked.
5. Idempotent -- a second ``--apply`` immediately after the first reclaims nothing.
6. Audit-logged -- every reclaim and every skip is appended with a reason.
7. Fail-soft -- an unreadable or corrupt record is skipped with a reason, never raised.

Authority: WI-6037; ``bridge/gtkb-wi6037-worker-exit-reconciliation-sweep-002.md`` (GO);
``PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730``.

Out of scope for this slice: session-envelope closure (owned by WI-5281) and bulk storage
reclamation (owned by WI-5855).
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

WORK_INTENT_DIR = (".gtkb-state", "work-intent")
IMPL_AUTH_DIR = (".gtkb-state", "implementation-authorizations")
DRAFT_DIRS = ((".tmp-lo-verdict-drafts",),)
AUDIT_LOG = (".gtkb-state", "worker-exit-reconciliation", "sweep.jsonl")

#: Packet pointer files are state, not reclaimable records; they are rewritten by the
#: next ``begin`` and must never be reclaimed on their own.
POINTER_FILENAMES = frozenset({"current.json"})

#: Default age after which an untracked scratch draft is considered abandoned. Drafts
#: carry no self-recorded expiry, so age is the only available signal; the threshold is
#: deliberately generous and configurable.
DEFAULT_DRAFT_MAX_AGE_HOURS = 24.0


@dataclass(frozen=True)
class Candidate:
    """One reconcilable record, with the reason it was or was not selected."""

    kind: str
    path: str
    expired: bool
    reason: str
    expires_at: str | None = None


@dataclass
class SweepResult:
    """Outcome of one sweep. ``reclaimed`` is always empty in report-only mode."""

    applied: bool
    candidates: list[Candidate] = field(default_factory=list)
    reclaimed: list[str] = field(default_factory=list)
    skipped: list[Candidate] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "applied": self.applied,
            "candidate_count": len(self.candidates),
            "reclaimed_count": len(self.reclaimed),
            "skipped_count": len(self.skipped),
            "error_count": len(self.errors),
            "candidates": [asdict(c) for c in self.candidates],
            "reclaimed": list(self.reclaimed),
            "skipped": [asdict(c) for c in self.skipped],
            "errors": list(self.errors),
        }


def _now() -> datetime:
    return datetime.now(UTC)


def _parse_timestamp(raw: object) -> datetime | None:
    """Parse a recorded ISO-8601 expiry. Returns ``None`` when unparseable.

    Unparseable is deliberately NOT treated as expired: invariant 2 says live state is
    never reclaimed, and a record whose expiry cannot be read is not known to be dead.
    """

    if not isinstance(raw, str) or not raw.strip():
        return None
    text = raw.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - invariant 7: corrupt records are skipped, not raised
        return None
    return data if isinstance(data, dict) else None


def _iter_files(directory: Path, suffix: str) -> Iterator[Path]:
    if not directory.is_dir():
        return
    for path in sorted(directory.rglob(f"*{suffix}")):
        if path.is_file():
            yield path


def _expiry_candidates(
    project_root: Path,
    *,
    parts: tuple[str, ...],
    kind: str,
    expiry_keys: tuple[str, ...],
    now: datetime,
) -> Iterator[Candidate]:
    """Yield candidates for a class whose records carry their own recorded expiry."""

    directory = project_root.joinpath(*parts)
    for path in _iter_files(directory, ".json"):
        rel = path.relative_to(project_root).as_posix()
        if path.name in POINTER_FILENAMES:
            yield Candidate(kind, rel, False, "pointer file; not a reclaimable record")
            continue
        record = _read_json(path)
        if record is None:
            yield Candidate(kind, rel, False, "unreadable or non-object record; skipped (invariant 7)")
            continue
        raw = next((record[k] for k in expiry_keys if k in record), None)
        expires = _parse_timestamp(raw)
        if expires is None:
            yield Candidate(kind, rel, False, "no parseable recorded expiry; not known to be dead")
            continue
        stamp = expires.isoformat()
        if expires > now:
            yield Candidate(kind, rel, False, "still live by its own recorded TTL", stamp)
            continue
        yield Candidate(kind, rel, True, "expired by its own recorded TTL", stamp)


def _draft_candidates(project_root: Path, *, now: datetime, max_age_hours: float) -> Iterator[Candidate]:
    """Yield abandoned scratch drafts. Drafts carry no expiry, so age is the signal."""

    for parts in DRAFT_DIRS:
        directory = project_root.joinpath(*parts)
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(project_root).as_posix()
            try:
                mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
            except OSError:
                yield Candidate("draft", rel, False, "stat failed; skipped (invariant 7)")
                continue
            age_hours = (now - mtime).total_seconds() / 3600.0
            if age_hours < max_age_hours:
                yield Candidate("draft", rel, False, f"age {age_hours:.1f}h below {max_age_hours:.1f}h threshold")
                continue
            yield Candidate("draft", rel, True, f"abandoned draft, age {age_hours:.1f}h", mtime.isoformat())


def collect_candidates(
    project_root: Path,
    *,
    now: datetime | None = None,
    draft_max_age_hours: float = DEFAULT_DRAFT_MAX_AGE_HOURS,
) -> list[Candidate]:
    """Enumerate every reconcilable record. Pure: performs no mutation."""

    moment = now or _now()
    found: list[Candidate] = []
    found.extend(
        _expiry_candidates(
            project_root,
            parts=WORK_INTENT_DIR,
            kind="work_intent_claim",
            expiry_keys=("ttl_expires_at", "expires_at"),
            now=moment,
        )
    )
    found.extend(
        _expiry_candidates(
            project_root,
            parts=IMPL_AUTH_DIR,
            kind="implementation_authorization_packet",
            expiry_keys=("expires_at",),
            now=moment,
        )
    )
    found.extend(_draft_candidates(project_root, now=moment, max_age_hours=draft_max_age_hours))
    return found


def _append_audit(project_root: Path, entries: list[dict[str, Any]]) -> None:
    """Append audit records. Never raises: audit failure must not abort reconciliation."""

    if not entries:
        return
    log_path = project_root.joinpath(*AUDIT_LOG)
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            for entry in entries:
                handle.write(json.dumps(entry, sort_keys=True) + "\n")
    except Exception:  # noqa: BLE001 - invariant 7
        return


def run_sweep(
    project_root: Path,
    *,
    apply: bool = False,
    now: datetime | None = None,
    draft_max_age_hours: float = DEFAULT_DRAFT_MAX_AGE_HOURS,
) -> SweepResult:
    """Enumerate reconcilable residue and, only when ``apply`` is true, reclaim it.

    Reclamation is confined to the enumerated record files. No bridge file, no git
    object, and no record that is still live by its own recorded expiry is touched.
    """

    moment = now or _now()
    candidates = collect_candidates(project_root, now=moment, draft_max_age_hours=draft_max_age_hours)
    result = SweepResult(applied=apply, candidates=candidates)
    audit: list[dict[str, Any]] = []
    stamp = moment.isoformat()

    for candidate in candidates:
        if not candidate.expired:
            result.skipped.append(candidate)
            audit.append({"at": stamp, "action": "skip", **asdict(candidate)})
            continue
        if not apply:
            audit.append({"at": stamp, "action": "would_reclaim", **asdict(candidate)})
            continue
        target = project_root / candidate.path
        try:
            target.unlink()
        except Exception as exc:  # noqa: BLE001 - invariant 7
            message = f"{candidate.path}: {exc}"
            result.errors.append(message)
            audit.append({"at": stamp, "action": "error", "detail": message, **asdict(candidate)})
            continue
        result.reclaimed.append(candidate.path)
        audit.append({"at": stamp, "action": "reclaim", **asdict(candidate)})

    _append_audit(project_root, audit)
    return result


def render_summary(result: SweepResult) -> str:
    """Render a compact human summary."""

    mode = "APPLY" if result.applied else "REPORT-ONLY"
    lines = [
        f"worker-exit reconciliation sweep [{mode}]",
        f"  candidates : {len(result.candidates)}",
        f"  reclaimable: {sum(1 for c in result.candidates if c.expired)}",
        f"  reclaimed  : {len(result.reclaimed)}",
        f"  skipped    : {len(result.skipped)}",
        f"  errors     : {len(result.errors)}",
    ]
    if not result.applied and any(c.expired for c in result.candidates):
        lines.append("  (report-only: nothing was mutated; re-run with --apply to reclaim)")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default=".", help="GT-KB project root.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Reclaim expired records. Without this flag the sweep mutates nothing.",
    )
    parser.add_argument(
        "--draft-max-age-hours",
        type=float,
        default=DEFAULT_DRAFT_MAX_AGE_HOURS,
        help="Age after which a scratch draft is considered abandoned.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve()
    result = run_sweep(root, apply=args.apply, draft_max_age_hours=args.draft_max_age_hours)
    print(json.dumps(result.as_dict(), indent=2, sort_keys=True) if args.json else render_summary(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
