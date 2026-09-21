"""groundtruth_kb.job_containment: one named kill-on-close job per runtime root and consumer prefix; a child is
placed in the job before it executes an instruction (created suspended, assigned, resumed) and is ended while still
suspended when it cannot be; an inherited handle keeps the job alive past its creator while a sole handle ends the
tree on close; stop_job ends every member, reports an already-exited one, and refuses with typed errors."""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path

import pytest

from groundtruth_kb import job_containment
from groundtruth_kb.job_containment import (
    ContainmentError,
    JobAlreadyExists,
    JobTerminationRefused,
    JobTerminationUnconfirmed,
    StoppedProcess,
    assign_to_job,
    close_handle,
    create_job,
    job_active_processes,
    job_member_pids,
    job_name,
    open_job,
    pid_alive,
    process_identity,
    start_contained,
    stop_job,
)

WINDOWS_ONLY = pytest.mark.skipif(sys.platform != "win32", reason="job containment is a Windows mechanism")
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
PREFIX = "Local\\gtkb-test-"

# A child that records that it ran, then sleeps.
SLEEPER = (
    "import os, pathlib, sys, time\n"
    "pathlib.Path(sys.argv[1]).write_text(str(os.getpid()), encoding='utf-8')\n"
    "time.sleep(300)\n"
)
# A child that records that it ran, starts a real descendant and records the descendant's pid, then sleeps.
SPAWNER = (
    "import os, pathlib, subprocess, sys, time\n"
    "marker, record = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])\n"
    "marker.write_text(str(os.getpid()), encoding='utf-8')\n"
    "grandchild = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(300)'])\n"
    "record.write_text(str(grandchild.pid), encoding='utf-8')\n"
    "time.sleep(300)\n"
)


def _sleeper(marker: Path) -> list[str]:
    return [sys.executable, "-c", SLEEPER, str(marker)]


def _spawner(marker: Path, record: Path) -> list[str]:
    return [sys.executable, "-c", SPAWNER, str(marker), str(record)]


def _eventually(condition: Callable[[], bool], seconds: float) -> bool:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(0.1)
    return condition()


def _written(path: Path) -> bool:
    return path.exists() and bool(path.read_text(encoding="utf-8").strip())


def _read_pid(path: Path) -> int:
    assert _eventually(lambda: _written(path), 30), f"{path.name} was not written by the stand-in"
    return int(path.read_text(encoding="utf-8"))


def _end(process: subprocess.Popen[bytes] | None) -> None:
    if process is not None and process.poll() is None:
        process.kill()
        process.wait(timeout=15)


def _end_pid(pid: int | None) -> None:
    if pid and pid_alive(pid):
        subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True, timeout=30)


def _unique_name(tmp_path: Path, salt: str = "") -> str:
    return job_name(PREFIX, tmp_path / salt if salt else tmp_path)


def test_job_name_is_the_prefix_plus_24_hex_digits_of_the_normalized_root(tmp_path: Path) -> None:
    name = job_name("Local\\x-", tmp_path)
    digest = hashlib.sha256(os.path.normcase(str(tmp_path.resolve())).encode("utf-8")).hexdigest()
    assert name == "Local\\x-" + digest[:24]
    suffix = name[len("Local\\x-") :]
    assert len(suffix) == 24 and all(c in "0123456789abcdef" for c in suffix)
    assert job_name("Local\\x-", tmp_path / ".." / tmp_path.name) == name, "the root is normalized first"
    other = job_name("Local\\y-", tmp_path)
    assert other != name and other[len("Local\\y-") :] == name[len("Local\\x-") :]


def test_process_identity_of_self_and_absence_after_child_exit() -> None:
    identity = process_identity(os.getpid())
    assert identity is not None
    assert identity["pid"] == os.getpid() and identity["created_at"]
    assert Path(identity["executable"]).is_file()
    assert process_identity(os.getpid()) == identity
    assert process_identity(0) is None and pid_alive(-1) is False
    child = subprocess.Popen([sys.executable, "-c", "pass"], creationflags=NO_WINDOW)
    child.wait(timeout=30)
    assert pid_alive(child.pid) is False


@WINDOWS_ONLY
@pytest.mark.timeout(120)
def test_process_identity_treats_an_ending_process_without_image_as_gone(monkeypatch: pytest.MonkeyPatch) -> None:
    """A process whose image can no longer be read because it is ending has no identity and is not alive.

    f21-full-20260920T1337 and T1401: pid_alive raised OSError 31, then OSError 5, for a grandchild caught
    mid-termination. The branch does not depend on the error code: an unreadable image on an open,
    unsignalled process yields no identity, which liveness polls read as gone and which never identifies
    a member for a stop. The current process, whose image is readable, keeps its identity.
    """
    assert process_identity(os.getpid()) is not None
    monkeypatch.setattr(job_containment, "image_name", lambda handle: "")
    assert process_identity(os.getpid()) is None and pid_alive(os.getpid()) is False


@WINDOWS_ONLY
def test_create_job_refuses_a_held_name_open_finds_it_and_an_empty_job_vanishes_on_close(tmp_path: Path) -> None:
    name = _unique_name(tmp_path)
    job = create_job(name, inheritable=False)
    assert job
    try:
        with pytest.raises(JobAlreadyExists, match=re.escape(name)) as refused:
            create_job(name, inheritable=False)
        assert refused.value.name == name and isinstance(refused.value, ContainmentError)
        found = open_job(name)
        assert found is not None
        close_handle(found)
        assert open_job(name + "-absent") is None
    finally:
        close_handle(job)
        job = None
    assert open_job(name) is None, "an empty job must vanish with its last handle"


@WINDOWS_ONLY
@pytest.mark.timeout(120)
def test_start_contained_places_the_child_in_the_job_before_it_runs_and_stop_job_ends_it(tmp_path: Path) -> None:
    name = _unique_name(tmp_path)
    marker = tmp_path / "ran.txt"
    job = create_job(name, inheritable=True)
    process = None
    try:
        process = start_contained(
            _sleeper(marker),
            dict(os.environ),
            job,
            inherit_job=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        assert process.pid in job_member_pids(job)
        assert job_active_processes(job) >= 1
        assert _eventually(lambda: _written(marker), 30), "the contained child did not run"
        members = job_member_pids(job)
        stopped = stop_job(job, name)
        # A venv redirector interpreter adds its real child to the job: the launched pid is reported, every member
        # is terminated with its executable named, and the report covers exactly what the job held.
        by_pid = {entry.pid: entry for entry in stopped}
        assert process.pid in by_pid and set(by_pid) == set(members)
        assert by_pid[process.pid] == StoppedProcess(process.pid, by_pid[process.pid].executable, "terminated")
        assert all(entry.outcome == "terminated" and entry.executable for entry in stopped)
        assert process.wait(timeout=10) is not None
        assert job_active_processes(job) == 0
        assert pid_alive(process.pid) is False
    finally:
        _end(process)
        close_handle(job)
        job = None
    assert open_job(name) is None


@WINDOWS_ONLY
@pytest.mark.timeout(120)
@pytest.mark.parametrize("failure", ["assignment_refused", "resume_failed"])
def test_start_contained_ends_a_child_that_cannot_be_assigned_or_resumed_before_it_runs(
    tmp_path: Path, failure: str
) -> None:
    name = _unique_name(tmp_path)
    marker = tmp_path / "ran.txt"
    captured: list[subprocess.Popen[bytes]] = []

    def assign(job: int, process: subprocess.Popen[bytes]) -> bool:
        captured.append(process)
        return failure != "assignment_refused" and assign_to_job(job, process)

    def refuse_resume(process: subprocess.Popen[bytes]) -> bool:
        return False

    resume = refuse_resume if failure == "resume_failed" else job_containment.resume_primary_thread
    job = create_job(name, inheritable=False)
    try:
        with pytest.raises(ContainmentError, match="ended before it ran"):
            start_contained(
                _sleeper(marker),
                dict(os.environ),
                job,
                inherit_job=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                assign=assign,
                resume=resume,
            )
        assert captured and captured[0].poll() is not None, "the uncontainable child must be ended"
        assert not marker.exists(), "the child ran before containment was established"
        assert _eventually(lambda: job_member_pids(job) == [], 10), "the ended child still counts as a member"
    finally:
        for process in captured:
            _end(process)
        close_handle(job)


@WINDOWS_ONLY
@pytest.mark.timeout(120)
@pytest.mark.parametrize("outcome", ["settles", "permanent"])
def test_start_contained_retries_a_momentarily_refused_assignment(tmp_path: Path, outcome: str) -> None:
    """ERROR_ACCESS_DENIED right after a job terminated its members is retried while the child stays suspended.

    f21-full-20260920T1311 refused the assignment at this call site without a captured code; the development
    reproduction that followed correction 18 captured Win32 error 5 immediately after stop_job. A refusal that
    settles lets the child run inside the job; one that never settles ends the suspended child within the
    retry window and names the error.
    """
    import ctypes

    name = _unique_name(tmp_path)
    marker = tmp_path / "ran.txt"
    attempts: list[int] = []
    captured: list[subprocess.Popen[bytes]] = []

    def assign(job: int, process: subprocess.Popen[bytes]) -> bool:
        captured.append(process)
        attempts.append(len(attempts) + 1)
        if outcome == "permanent" or len(attempts) <= 2:
            ctypes.set_last_error(job_containment.ERROR_ACCESS_DENIED)
            return False
        return assign_to_job(job, process)

    job = create_job(name, inheritable=False)
    process = None
    try:
        if outcome == "settles":
            process = start_contained(
                _sleeper(marker),
                dict(os.environ),
                job,
                inherit_job=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                assign=assign,
            )
            # A venv redirector interpreter adds its real child to the job moments after resume.
            assert len(attempts) == 3 and process.pid in job_member_pids(job)
            assert _eventually(lambda: _written(marker), 30), "the contained child did not run after the retry"
        else:
            started = time.monotonic()
            with pytest.raises(ContainmentError, match=r"Win32 error 5.*ended before it ran"):
                start_contained(
                    _sleeper(marker),
                    dict(os.environ),
                    job,
                    inherit_job=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    assign=assign,
                )
            assert len(attempts) > 1 and time.monotonic() - started < 30
            assert captured and captured[0].poll() is not None and not marker.exists()
    finally:
        _end(process)
        for child in captured:
            _end(child)
        close_handle(job)


@WINDOWS_ONLY
@pytest.mark.timeout(120)
def test_inherited_handle_keeps_the_job_alive_and_an_uninherited_handle_ends_the_tree_on_close(
    tmp_path: Path,
) -> None:
    """(a) the dashboard shape: the child inherits the handle, so the job is found by name after the creator closed
    its own handle and stop_job ends child and descendant; (b) the domain-service shape: no inheritance, so closing
    the creator's handle ends the child and its descendant."""
    name = _unique_name(tmp_path, "inherited")
    marker, record = tmp_path / "a-ran.txt", tmp_path / "a-grandchild.txt"
    job = create_job(name, inheritable=True)
    found = None
    process = None
    grandchild = None
    try:
        process = start_contained(
            _spawner(marker, record),
            dict(os.environ),
            job,
            inherit_job=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        grandchild = _read_pid(record)
        assert {process.pid, grandchild} <= set(job_member_pids(job)), "the descendant was born outside the job"
        close_handle(job)
        job = None
        found = open_job(name)
        assert found is not None, "the inherited handle did not keep the job alive"
        stopped = stop_job(found, name)
        assert {process.pid, grandchild} <= {entry.pid for entry in stopped}
        assert all(entry.outcome == "terminated" and entry.executable for entry in stopped)
        assert process.wait(timeout=15) is not None
        assert _eventually(lambda: not pid_alive(grandchild), 15), "the descendant survived the stop"
        close_handle(found)
        found = None
        assert open_job(name) is None
    finally:
        _end(process)
        _end_pid(grandchild)
        for handle in (job, found):
            if handle is not None:
                close_handle(handle)

    name2 = _unique_name(tmp_path, "sole")
    marker2, record2 = tmp_path / "b-ran.txt", tmp_path / "b-grandchild.txt"
    job2 = create_job(name2, inheritable=False)
    process2 = None
    grandchild2 = None
    try:
        process2 = start_contained(
            _spawner(marker2, record2),
            dict(os.environ),
            job2,
            inherit_job=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        grandchild2 = _read_pid(record2)
        assert {process2.pid, grandchild2} <= set(job_member_pids(job2)), "the descendant was born outside the job"
        assert process2.poll() is None and pid_alive(grandchild2)
        close_handle(job2)
        job2 = None
        assert process2.wait(timeout=15) is not None, "the child survived the last handle"
        assert _eventually(lambda: not pid_alive(grandchild2), 15), "the descendant survived the last handle"
        assert open_job(name2) is None
    finally:
        _end(process2)
        _end_pid(grandchild2)
        if job2 is not None:
            close_handle(job2)


@WINDOWS_ONLY
@pytest.mark.timeout(120)
def test_stop_job_reports_an_exited_member_and_raises_typed_refusals(tmp_path: Path) -> None:
    name = _unique_name(tmp_path)
    job = create_job(name, inheritable=False)
    gone = None
    live = None
    kernel = job_containment.kernel32()
    try:
        gone = start_contained(
            _sleeper(tmp_path / "gone.txt"),
            dict(os.environ),
            job,
            inherit_job=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        assert _eventually(lambda: _written(tmp_path / "gone.txt"), 30)
        subprocess.run(["taskkill", "/PID", str(gone.pid), "/F"], capture_output=True, timeout=30)
        assert gone.wait(timeout=15) is not None
        exited_pid = gone.pid
        stopped = stop_job(job, name, members=lambda job: [exited_pid])
        assert [(entry.pid, entry.outcome) for entry in stopped] == [(exited_pid, "exited")]

        live = start_contained(
            _sleeper(tmp_path / "live.txt"),
            dict(os.environ),
            job,
            inherit_job=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        assert _eventually(lambda: _written(tmp_path / "live.txt"), 30)
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(kernel, "TerminateJobObject", lambda job, code: 0)
            with pytest.raises(JobTerminationRefused, match="refused termination"):
                stop_job(job, name)
        assert live.poll() is None, "a refused termination must leave the member running"

        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(job_containment, "job_active_processes", lambda job: 1)
            with pytest.raises(JobTerminationUnconfirmed, match="still counts"):
                stop_job(job, name, timeout=2.0)
        assert live.wait(timeout=15) is not None, "the job was terminated before the count was read"
        assert job_active_processes(job) == 0
    finally:
        _end(gone)
        _end(live)
        close_handle(job)
