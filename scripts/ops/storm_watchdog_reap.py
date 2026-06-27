#!/usr/bin/env python3
# (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Liveness-aware reap decision for the GT-KB storm watchdog (WI-4828).

Slice 1 of the WI-4670 dispatch-storm remediation. The storm watchdog
(`harness_storm_watchdog.ps1`) historically force-terminated the whole matched
harness process family when the *raw OS-process count* exceeded a threshold.
Because one codex worker spawns ~4 OS processes while the concurrency cap
(WI-4472) bounds *logical workers* (~3/role), a within-cap number of healthy
workers blew that threshold, and the watchdog reaped healthy, in-flight,
lease-holding workers mid-task (exit 4294967295). A reaped worker writes no
verdict, so its bridge item stays actionable and is re-dispatched -- the storm.

This module is the **pure decision**: given the candidate dispatch processes and
the per-document lease records (`bridge_lease_registry`), decide which pids to
reap. It reaps only genuine orphans/corpses and over-lifetime stragglers; it
NEVER reaps a healthy in-flight lease-holder within lifetime, that worker's
process family, or a cold-start (pre-lease) process.

Separation of concerns: throttling *spawns* is the concurrency cap's job
(WI-4472); this watchdog only reaps *corpses/hangs*. The raw-count "kill the
family above 15" behavior is removed.

The decision is a pure function of ``(processes, leases, now, config)`` -- no
clock, randomness, or I/O inside ``decide_reap`` -- so it is fully unit-testable
(``platform_tests/scripts/test_storm_watchdog_reap.py``). The thin process
gather + lease read + kill execution live in ``harness_storm_watchdog.ps1`` and
this module's ``main`` glue.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_STARTUP_GRACE_SECONDS = 120
# Backstop ABOVE the run_with_status.py worker-lifetime timeout
# (DEFAULT_WORKER_LIFETIME_TIMEOUT_SECONDS = 600, WI-4806). The primary timeout
# reaps a hung worker at 600s; the watchdog only catches stragglers that
# outlived it (e.g. workers not launched through run_with_status, or where the
# primary timeout did not fire). Keep this >= the WI-4806 value + margin.
DEFAULT_MAX_LIFETIME_SECONDS = 900

# Default lease directories scanned by ``main`` / ``read_leases``. The trigger
# runs with ``--state-dir .gtkb-state/bridge-poller`` so leases live under
# ``.gtkb-state/bridge-poller/leases``; the cross-harness-trigger state dir is
# scanned too for robustness. Overridable via ``--lease-dir`` (repeatable).
DEFAULT_LEASE_DIRS = (
    ".gtkb-state/bridge-poller/leases",
    ".gtkb-state/cross-harness-trigger/leases",
)


@dataclass(frozen=True)
class Process:
    """A candidate dispatch process (gathered by the .ps1).

    ``dispatched`` marks a clearly-identifiable dispatched-worker ROOT: a
    ``codex exec`` process or a non-codex harness python (ollama/openrouter).
    It is False for helper processes (node_repl, codex-command-runner,
    codex-windows-sandbox) and for INTERACTIVE codex (``codex`` TUI, no
    ``exec``). The decider only acts on process-family components that contain a
    dispatched root, so interactive sessions -- and ambiguous orphan families
    whose dispatched root has already died -- are left untouched. This is the
    safety boundary that keeps the watchdog from reaping the owner's interactive
    Codex session.
    """

    pid: int
    ppid: int
    name: str
    create_time_epoch: float
    dispatched: bool = False


@dataclass(frozen=True)
class Lease:
    """A per-document lease record (from bridge_lease_registry)."""

    pid: int
    acquired_at_epoch: float
    doc_slug: str = ""


@dataclass(frozen=True)
class ProvenanceRecord:
    """A pid observed to belong to a dispatched run (WI-4834).

    Recorded by the watchdog glue while a process was a member of a dispatched
    component (a component containing a live ``dispatched`` root). It lets the
    decider precisely attribute an orphaned helper to a dispatched run AFTER that
    run's root has died: a still-alive process matching ``(pid,
    create_time_epoch)`` whose ``dispatch_root_pid`` is no longer alive is a
    leftover of a dead dispatched run and is reapable. Interactive sessions are
    never in a dispatched component, are never recorded, and therefore can never
    match -- so they are never reaped via this path. The ``create_time_epoch``
    match (not pid alone) guards against pid reuse re-attributing a fresh pid.
    """

    pid: int
    create_time_epoch: float
    dispatch_root_pid: int


@dataclass(frozen=True)
class ReapDecision:
    """Result of ``decide_reap``: pids to reap, pids protected, and per-pid reasons."""

    reap: list[int]
    protect: list[int]
    reasons: dict[int, str]


def _components(processes: list[Process]) -> list[set[int]]:
    """Connected components over the candidate processes via parent/child edges.

    Only edges where BOTH endpoints are candidate processes are considered, so
    the component of a worker is its dispatch process family and never reaches a
    non-candidate ancestor (the dispatcher, the shell, or the OS). This is what
    lets one lease-holder pid protect its whole healthy family without
    over-protecting unrelated processes.
    """
    pids = {p.pid for p in processes}
    parent: dict[int, int] = {p.pid: p.pid for p in processes}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for p in processes:
        if p.ppid in pids and p.ppid != p.pid:
            union(p.pid, p.ppid)

    comps: dict[int, set[int]] = {}
    for p in processes:
        comps.setdefault(find(p.pid), set()).add(p.pid)
    return list(comps.values())


def decide_reap(
    processes: list[Process],
    leases: list[Lease],
    *,
    now: float,
    startup_grace_seconds: float = DEFAULT_STARTUP_GRACE_SECONDS,
    max_lifetime_seconds: float = DEFAULT_MAX_LIFETIME_SECONDS,
    provenance: list[ProvenanceRecord] | None = None,
) -> ReapDecision:
    """Decide which candidate dispatch processes to reap.

    A running process is PROTECTED when ANY holds:
      1. it is younger than ``startup_grace_seconds`` (may be cold-starting,
         pre-lease) -> ``cold_start_grace``;
      2. its pid holds a lease acquired within ``max_lifetime_seconds`` and the
         pid is running (it is in ``processes``) -> ``live_lease_holder``;
      3. it is in the same process-family component as a (2) pid ->
         ``descendant_of_lease_holder``.

    A running process is REAPABLE otherwise:
      - its pid (or a pid in its component) holds a lease acquired
        ``>= max_lifetime_seconds`` ago -> ``over_lifetime_straggler`` (a genuine
        hang; backstop behind the WI-4806 worker-lifetime timeout);
      - else -> ``orphan_no_lease`` (a corpse/orphan: old, no live lease).

    Liveness signal: the lease pid being present in ``processes`` IS the proof
    the worker is alive, so protection does NOT depend on lease heartbeat
    freshness (a long-running worker that did not refresh its heartbeat is still
    protected while within lifetime). Heartbeat-based staleness is the lease
    registry's own reclamation concern, not the watchdog's reap criterion. The
    decision is deterministic in ``(processes, leases, now, config)``.
    """
    by_pid = {p.pid: p for p in processes}
    protective_pids = {
        lease.pid for lease in leases if lease.pid in by_pid and (now - lease.acquired_at_epoch) < max_lifetime_seconds
    }
    over_lifetime_pids = {
        lease.pid for lease in leases if lease.pid in by_pid and (now - lease.acquired_at_epoch) >= max_lifetime_seconds
    }

    comps = _components(processes)
    pid_to_comp: dict[int, set[int]] = {}
    for comp in comps:
        for pid in comp:
            pid_to_comp[pid] = comp
    protected_comp_pids: set[int] = set()
    for comp in comps:
        if comp & protective_pids:
            protected_comp_pids |= comp

    # Safety scoping: only act on process-family components that contain a
    # dispatched-worker root. Components with no dispatched root -- interactive
    # codex sessions, and ambiguous orphan families whose dispatched root has
    # already died -- are left entirely untouched (neither reaped nor reported
    # as protected). This is the guard that prevents reaping the owner's
    # interactive Codex session.
    dispatched_pids = {p.pid for p in processes if p.dispatched}
    in_scope_pids: set[int] = set()
    for comp in comps:
        if comp & dispatched_pids:
            in_scope_pids |= comp

    reap: list[int] = []
    protect: list[int] = []
    reasons: dict[int, str] = {}
    for p in processes:
        if p.pid not in in_scope_pids:
            continue
        age = now - p.create_time_epoch
        if age < startup_grace_seconds:
            protect.append(p.pid)
            reasons[p.pid] = "cold_start_grace"
            continue
        if p.pid in protected_comp_pids:
            protect.append(p.pid)
            reasons[p.pid] = "live_lease_holder" if p.pid in protective_pids else "descendant_of_lease_holder"
            continue
        comp = pid_to_comp.get(p.pid, {p.pid})
        if p.pid in over_lifetime_pids or (comp & over_lifetime_pids):
            reasons[p.pid] = "over_lifetime_straggler"
        else:
            reasons[p.pid] = "orphan_no_lease"
        reap.append(p.pid)

    # WI-4834: precise dead-root orphan attribution. Processes NOT in scope (no
    # live dispatched root in their component) are otherwise left untouched. A
    # process recorded in provenance while it was in a dispatched component --
    # matched by (pid, create_time_epoch) to guard pid reuse -- whose recorded
    # dispatch_root_pid is no longer alive is a leftover of a dead dispatched run
    # and is reapable. Unrecorded processes (interactive sessions) never match,
    # so they are never reaped here; cold-start grace is still honored.
    if provenance:
        live_pids = set(by_pid)
        prov_by_key = {(rec.pid, rec.create_time_epoch): rec for rec in provenance}
        for p in processes:
            if p.pid in in_scope_pids or p.pid in reasons:
                continue
            rec = prov_by_key.get((p.pid, p.create_time_epoch))
            if rec is None or rec.dispatch_root_pid in live_pids:
                continue
            if (now - p.create_time_epoch) < startup_grace_seconds:
                continue
            reasons[p.pid] = "orphan_dead_dispatched_root"
            reap.append(p.pid)

    return ReapDecision(reap=sorted(reap), protect=sorted(protect), reasons=reasons)


# --------------------------------------------------------------------------- #
# Thin glue (not unit-tested; the decision logic above is the tested surface). #
# --------------------------------------------------------------------------- #


def processes_from_dicts(rows: list[dict[str, Any]]) -> list[Process]:
    """Build ``Process`` records from the .ps1-supplied JSON rows."""
    out: list[Process] = []
    for row in rows:
        out.append(
            Process(
                pid=int(row["pid"]),
                ppid=int(row.get("ppid", 0)),
                name=str(row.get("name", "")),
                create_time_epoch=float(row["create_time_epoch"]),
                dispatched=bool(row.get("dispatched", False)),
            )
        )
    return out


def _parse_iso_to_epoch(value: str) -> float | None:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.timestamp()


def read_leases(lease_dirs: list[Path]) -> list[Lease]:
    """Read lease records from the given lease directories (``*.lock`` files).

    Tolerant of missing dirs and unparseable files (skipped). ``acquired_at`` is
    parsed from the ISO timestamp the lease registry writes.
    """
    leases: list[Lease] = []
    for lease_dir in lease_dirs:
        if not lease_dir.is_dir():
            continue
        for path in sorted(lease_dir.glob("*.lock")):
            try:
                record = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(record, dict):
                continue
            pid = record.get("pid")
            acquired = record.get("acquired_at")
            if not isinstance(pid, int) or not isinstance(acquired, str):
                continue
            epoch = _parse_iso_to_epoch(acquired)
            if epoch is None:
                continue
            leases.append(Lease(pid=pid, acquired_at_epoch=epoch, doc_slug=str(record.get("doc_slug", ""))))
    return leases


DEFAULT_PROVENANCE_DIR = ".gtkb-state/ops/dispatch-provenance"
_PROVENANCE_LEDGER_FILENAME = "dispatch-provenance.json"


def read_provenance(provenance_dir: Path) -> list[ProvenanceRecord]:
    """Read the dispatch-run pid-provenance ledger (WI-4834).

    Tolerant of a missing/corrupt ledger (returns ``[]``) so the watchdog fails
    soft -- no provenance means no dead-root orphan reaping, never an error.
    """
    ledger = provenance_dir / _PROVENANCE_LEDGER_FILENAME
    if not ledger.is_file():
        return []
    try:
        data = json.loads(ledger.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return []
    out: list[ProvenanceRecord] = []
    if isinstance(data, list):
        for row in data:
            if not isinstance(row, dict):
                continue
            try:
                out.append(
                    ProvenanceRecord(
                        pid=int(row["pid"]),
                        create_time_epoch=float(row["create_time_epoch"]),
                        dispatch_root_pid=int(row["dispatch_root_pid"]),
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue
    return out


def update_provenance(provenance_dir: Path, processes: list[Process], prior: list[ProvenanceRecord]) -> None:
    """Update + self-prune the pid-provenance ledger (WI-4834).

    Records every current dispatched-component member tagged with its dispatched
    root pid, carries forward prior records whose pid is still alive (so a
    just-died root's descendants stay attributable for at least one more tick),
    and drops records whose pid is gone. Best-effort: a write failure is
    swallowed (the ledger is regenerable runtime state). A direct overwrite is
    used rather than ``os.replace`` because the project root may live on a
    cloud-synced volume where rename can fail; a torn read is handled by
    ``read_provenance``'s fail-soft parse.
    """
    live_pids = {p.pid for p in processes}
    by_pid = {p.pid: p for p in processes}
    dispatched_pids = {p.pid for p in processes if p.dispatched}
    records: dict[tuple[int, float], ProvenanceRecord] = {}
    for rec in prior:
        if rec.pid in live_pids:
            records[(rec.pid, rec.create_time_epoch)] = rec
    for comp in _components(processes):
        roots = sorted(pid for pid in comp if pid in dispatched_pids)
        if not roots:
            continue
        root_pid = roots[0]
        for pid in comp:
            p = by_pid[pid]
            records[(p.pid, p.create_time_epoch)] = ProvenanceRecord(
                pid=p.pid, create_time_epoch=p.create_time_epoch, dispatch_root_pid=root_pid
            )
    payload = [
        {"pid": r.pid, "create_time_epoch": r.create_time_epoch, "dispatch_root_pid": r.dispatch_root_pid}
        for r in records.values()
    ]
    try:
        provenance_dir.mkdir(parents=True, exist_ok=True)
        (provenance_dir / _PROVENANCE_LEDGER_FILENAME).write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    except OSError:
        pass


def main(argv: list[str] | None = None) -> int:
    """CLI glue for the .ps1: read processes JSON (stdin) + leases, print decision.

    The .ps1 pipes a JSON array of ``{pid, ppid, name, create_time_epoch}`` on
    stdin, supplies ``--now`` (epoch) and optional ``--lease-dir`` overrides, and
    reads the printed ``{"reap": [...], "reasons": {...}}`` to Stop-Process only
    the reap pids. On any error the .ps1 must fail safe (reap nothing).
    """
    parser = argparse.ArgumentParser(description="Storm-watchdog liveness-aware reap decision (WI-4828).")
    parser.add_argument("--now", type=float, required=True, help="Current time as epoch seconds.")
    parser.add_argument("--lease-dir", action="append", default=None, help="Lease directory (repeatable).")
    parser.add_argument("--startup-grace-seconds", type=float, default=DEFAULT_STARTUP_GRACE_SECONDS)
    parser.add_argument("--max-lifetime-seconds", type=float, default=DEFAULT_MAX_LIFETIME_SECONDS)
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--provenance-dir",
        type=Path,
        default=Path(DEFAULT_PROVENANCE_DIR),
        help="Dispatch-run pid-provenance ledger dir (WI-4834), resolved under --project-root.",
    )
    parser.add_argument(
        "--processes-file",
        type=Path,
        default=None,
        help="JSON file of process rows. Preferred over stdin on Windows PowerShell, "
        "which can raise an OSError flushing a piped stdin. Falls back to stdin when omitted.",
    )
    args = parser.parse_args(argv)

    if args.processes_file is not None:
        raw = args.processes_file.read_text(encoding="utf-8-sig")
    else:
        raw = sys.stdin.read()
    rows = json.loads(raw) if raw.strip() else []
    if isinstance(rows, dict):
        rows = [rows]
    processes = processes_from_dicts(rows)

    lease_dir_strs = args.lease_dir if args.lease_dir else list(DEFAULT_LEASE_DIRS)
    lease_dirs = [(args.project_root / d).resolve() for d in lease_dir_strs]
    leases = read_leases(lease_dirs)

    provenance_dir = (args.project_root / args.provenance_dir).resolve()
    prior_provenance = read_provenance(provenance_dir)

    decision = decide_reap(
        processes,
        leases,
        now=args.now,
        startup_grace_seconds=args.startup_grace_seconds,
        max_lifetime_seconds=args.max_lifetime_seconds,
        provenance=prior_provenance,
    )

    # WI-4834: refresh the provenance ledger AFTER deciding, with the current
    # process set, so a just-died root's descendants stay attributable next tick.
    update_provenance(provenance_dir, processes, prior_provenance)
    print(json.dumps({"reap": decision.reap, "protect": decision.protect, "reasons": decision.reasons}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
