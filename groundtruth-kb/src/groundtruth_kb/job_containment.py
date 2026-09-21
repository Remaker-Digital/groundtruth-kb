"""Win32 job-object containment shared by ``gt dashboard start``/``stop`` and the domain-service launcher.

Owner ruling D27 (2026-09-18): one implementation of the mechanics for both consumers. A consumer creates one named
kill-on-close job per runtime root (its own prefix + the first 24 hex digits of the sha256 of the normalized root,
so a dashboard job and a domain-service job for one root never collide), creates each child suspended, places it in
the job and only then resumes it; a child that cannot be placed or resumed is ended while still suspended and
``ContainmentError`` is raised, so no process executes an instruction outside the job (an assignment refused
with ERROR_ACCESS_DENIED just after the job terminated its members is retried for up to two seconds
first). ``inherit_job=True`` hands the
child the job handle, so the job outlives its launcher (the dashboard); ``False`` keeps the launcher's handle the
only one, so the launcher's exit ends the tree (the domain service). ``stop_job`` ends every member of an open job
and confirms each one. Off Windows the identity helpers read ``/proc``; the job primitives are reached only behind
the callers' platform guards. Consumers keep their own thin wrappers as the seam their tests patch (``assign=``,
``resume=``, ``members=``).
"""

from __future__ import annotations

import contextlib
import ctypes
import functools
import hashlib
import os
import subprocess
import sys
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION = 1
JOB_OBJECT_BASIC_PROCESS_ID_LIST = 3
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
JOB_OBJECT_ALL_ACCESS = 0x1F001F
CREATE_SUSPENDED = 0x00000004
THREAD_SUSPEND_RESUME = 0x0002
TH32CS_SNAPTHREAD = 0x00000004
HANDLE_FLAG_INHERIT = 0x0001
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
SYNCHRONIZE = 0x00100000
ERROR_FILE_NOT_FOUND = 2
ERROR_ACCESS_DENIED = 5
ERROR_GEN_FAILURE = 31
ERROR_INVALID_PARAMETER = 87
# A job that has just terminated its members can refuse a new member with ERROR_ACCESS_DENIED while the kernel
# finishes that termination; the new child is still suspended, so the assignment is retried this long.
ASSIGNMENT_RETRY_SECONDS = 2.0
ERROR_ALREADY_EXISTS = 183
ERROR_MORE_DATA = 234
JOB_NAME_DIGEST_LENGTH = 24


class ProcessIdentity(TypedDict):
    pid: int
    created_at: str
    executable: str


@dataclass(frozen=True)
class StoppedProcess:
    """One member ``stop_job`` accounted for: ended by the stop, or found already exited."""

    pid: int
    executable: str
    outcome: str


class ContainmentError(RuntimeError):
    """A child could not be placed in the job or resumed; it was ended while still suspended."""


class JobAlreadyExists(ContainmentError):
    """The job name is already held (another launch is in progress or the name is held elsewhere)."""

    def __init__(self, name: str) -> None:
        super().__init__(f"job {name} already exists")
        self.name = name


class JobTerminationRefused(ContainmentError):
    """The job refused the termination request."""


class JobTerminationUnconfirmed(ContainmentError):
    """The termination request was accepted but a member had not ended within the wait."""


if sys.platform == "win32":
    from ctypes import wintypes

    class _JobBasicLimit(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class _JobIoCounters(ctypes.Structure):
        _fields_ = [
            (name, ctypes.c_uint64)
            for name in (
                "ReadOperationCount",
                "WriteOperationCount",
                "OtherOperationCount",
                "ReadTransferCount",
                "WriteTransferCount",
                "OtherTransferCount",
            )
        ]

    class _JobExtendedLimit(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", _JobBasicLimit),
            ("IoInfo", _JobIoCounters),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    class _JobBasicAccounting(ctypes.Structure):
        _fields_ = [
            ("TotalUserTime", ctypes.c_int64),
            ("TotalKernelTime", ctypes.c_int64),
            ("ThisPeriodTotalUserTime", ctypes.c_int64),
            ("ThisPeriodTotalKernelTime", ctypes.c_int64),
            ("TotalPageFaultCount", wintypes.DWORD),
            ("TotalProcesses", wintypes.DWORD),
            ("ActiveProcesses", wintypes.DWORD),
            ("TotalTerminatedProcesses", wintypes.DWORD),
        ]

    class _ThreadEntry(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ThreadID", wintypes.DWORD),
            ("th32OwnerProcessID", wintypes.DWORD),
            ("tpBasePri", wintypes.LONG),
            ("tpDeltaPri", wintypes.LONG),
            ("dwFlags", wintypes.DWORD),
        ]

    @functools.cache
    def kernel32() -> ctypes.WinDLL:
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel.OpenProcess.restype = wintypes.HANDLE
        kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
        kernel.CloseHandle.restype = wintypes.BOOL
        kernel.GetProcessTimes.argtypes = (wintypes.HANDLE,) + (ctypes.POINTER(wintypes.FILETIME),) * 4
        kernel.GetProcessTimes.restype = wintypes.BOOL
        kernel.QueryFullProcessImageNameW.argtypes = (
            wintypes.HANDLE,
            wintypes.DWORD,
            wintypes.LPWSTR,
            ctypes.POINTER(wintypes.DWORD),
        )
        kernel.QueryFullProcessImageNameW.restype = wintypes.BOOL
        kernel.WaitForSingleObject.argtypes = (wintypes.HANDLE, wintypes.DWORD)
        kernel.WaitForSingleObject.restype = wintypes.DWORD
        kernel.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
        kernel.CreateJobObjectW.restype = wintypes.HANDLE
        kernel.OpenJobObjectW.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR)
        kernel.OpenJobObjectW.restype = wintypes.HANDLE
        kernel.SetInformationJobObject.argtypes = (wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD)
        kernel.SetInformationJobObject.restype = wintypes.BOOL
        kernel.QueryInformationJobObject.argtypes = (
            wintypes.HANDLE,
            ctypes.c_int,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.DWORD),
        )
        kernel.QueryInformationJobObject.restype = wintypes.BOOL
        kernel.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
        kernel.AssignProcessToJobObject.restype = wintypes.BOOL
        kernel.TerminateJobObject.argtypes = (wintypes.HANDLE, wintypes.UINT)
        kernel.TerminateJobObject.restype = wintypes.BOOL
        kernel.IsProcessInJob.argtypes = (wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL))
        kernel.IsProcessInJob.restype = wintypes.BOOL
        kernel.SetHandleInformation.argtypes = (wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD)
        kernel.SetHandleInformation.restype = wintypes.BOOL
        kernel.CreateToolhelp32Snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
        kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
        kernel.Thread32First.argtypes = (wintypes.HANDLE, ctypes.POINTER(_ThreadEntry))
        kernel.Thread32First.restype = wintypes.BOOL
        kernel.Thread32Next.argtypes = (wintypes.HANDLE, ctypes.POINTER(_ThreadEntry))
        kernel.Thread32Next.restype = wintypes.BOOL
        kernel.OpenThread.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        kernel.OpenThread.restype = wintypes.HANDLE
        kernel.ResumeThread.argtypes = (wintypes.HANDLE,)
        kernel.ResumeThread.restype = wintypes.DWORD
        return kernel


def close_handle(handle: int) -> None:
    if sys.platform == "win32":
        kernel32().CloseHandle(handle)


def image_name(handle: int) -> str:
    """The normalized executable path of an open process handle (empty when it cannot be read)."""
    if sys.platform != "win32":
        return ""
    from ctypes import wintypes

    size = wintypes.DWORD(32768)
    name = ctypes.create_unicode_buffer(size.value)
    if not kernel32().QueryFullProcessImageNameW(handle, 0, name, ctypes.byref(size)):
        return ""
    return os.path.normcase(name.value)


@contextlib.contextmanager
def windows_process(
    pid: int,
) -> Iterator[tuple[ProcessIdentity | None, tuple[ctypes.WinDLL, int] | None]]:
    """Hold the process object while inspecting identity and, if requested, stopping its tree."""
    from ctypes import wintypes

    kernel = kernel32()
    handle: int = kernel.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE, False, pid)
    if not handle:
        error = ctypes.get_last_error()
        if error == ERROR_INVALID_PARAMETER:  # no process with this ID
            yield None, None
            return
        raise OSError(error, "process inspection failed")
    try:
        if kernel.WaitForSingleObject(handle, 0) == 0:
            yield None, None
            return
        times = [wintypes.FILETIME() for _ in range(4)]
        if not kernel.GetProcessTimes(handle, *(ctypes.byref(value) for value in times)):
            raise OSError(ctypes.get_last_error(), "process creation time unavailable")
        executable = image_name(handle)
        if not executable:
            # The process object still exists but its image cannot be read (ERROR_GEN_FAILURE 31 or
            # ERROR_ACCESS_DENIED 5 while its address space is torn down): it is ending. Like a Linux
            # zombie it has no current identity, so it is not alive and never positively identified.
            yield None, None
            return
        record: ProcessIdentity = {
            "pid": pid,
            "created_at": str((times[0].dwHighDateTime << 32) | times[0].dwLowDateTime),
            "executable": executable,
        }
        yield record, (kernel, handle)
    finally:
        kernel.CloseHandle(handle)


def process_identity(pid: int) -> ProcessIdentity | None:
    if type(pid) is not int or pid <= 0:
        return None
    if sys.platform == "win32":
        with windows_process(pid) as (record, _):
            return record
    process = Path("/proc") / str(pid)
    try:
        fields = (process / "stat").read_text().rsplit(")", 1)[1].split()
        if fields[0] == "Z":
            return None
        return {"pid": pid, "created_at": fields[19], "executable": str((process / "exe").resolve(strict=True))}
    except FileNotFoundError:
        return None


def pid_alive(pid: int) -> bool:
    return process_identity(pid) is not None


def job_name(prefix: str, runtime_root: Path) -> str:
    """The session-local job name for a runtime root: the consumer's prefix + a digest of the normalized root."""
    digest = hashlib.sha256(os.path.normcase(str(runtime_root.resolve())).encode("utf-8")).hexdigest()
    return prefix + digest[:JOB_NAME_DIGEST_LENGTH]


def create_job(name: str, *, inheritable: bool) -> int:
    """Create the named kill-on-close job; refuse a name that already exists (``JobAlreadyExists``).

    ``OSError`` when the job cannot be created or configured. ``inheritable=True`` marks the handle inheritable so
    a child created with ``inherit_job=True`` keeps the job alive after this process ends.
    """
    kernel = kernel32()
    ctypes.set_last_error(0)
    job: int | None = kernel.CreateJobObjectW(None, name)
    if not job:
        raise OSError(ctypes.get_last_error(), f"job {name} could not be created")
    if ctypes.get_last_error() == ERROR_ALREADY_EXISTS:
        kernel.CloseHandle(job)
        raise JobAlreadyExists(name)
    limits = _JobExtendedLimit()
    limits.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    configured = kernel.SetInformationJobObject(
        job, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION, ctypes.byref(limits), ctypes.sizeof(limits)
    )
    if configured and inheritable:
        configured = kernel.SetHandleInformation(job, HANDLE_FLAG_INHERIT, HANDLE_FLAG_INHERIT)
    if not configured:
        error = ctypes.get_last_error()
        kernel.CloseHandle(job)
        raise OSError(error, f"job {name} could not be configured")
    return job


def open_job(name: str) -> int | None:
    """Open the named job, or None when no such job exists (no launch holds it)."""
    kernel = kernel32()
    job: int | None = kernel.OpenJobObjectW(JOB_OBJECT_ALL_ACCESS, False, name)
    if job:
        return job
    error = ctypes.get_last_error()
    if error == ERROR_FILE_NOT_FOUND:
        return None
    raise OSError(error, f"job {name} could not be opened")


def job_member_pids(job: int) -> list[int]:
    """Every process currently in the job."""
    from ctypes import wintypes

    kernel = kernel32()
    capacity = 64
    while True:

        class PidList(ctypes.Structure):
            _fields_ = [
                ("NumberOfAssignedProcesses", wintypes.DWORD),
                ("NumberOfProcessIdsInList", wintypes.DWORD),
                ("ProcessIdList", ctypes.c_size_t * capacity),
            ]

        buffer = PidList()
        returned = wintypes.DWORD(0)
        if kernel.QueryInformationJobObject(
            job, JOB_OBJECT_BASIC_PROCESS_ID_LIST, ctypes.byref(buffer), ctypes.sizeof(buffer), ctypes.byref(returned)
        ):
            if buffer.NumberOfProcessIdsInList >= buffer.NumberOfAssignedProcesses:
                return [int(pid) for pid in buffer.ProcessIdList[: buffer.NumberOfProcessIdsInList]]
        elif ctypes.get_last_error() != ERROR_MORE_DATA:
            raise OSError(ctypes.get_last_error(), "job members could not be listed")
        capacity *= 4


def job_active_processes(job: int) -> int:
    from ctypes import wintypes

    accounting = _JobBasicAccounting()
    returned = wintypes.DWORD(0)
    if not kernel32().QueryInformationJobObject(
        job,
        JOB_OBJECT_BASIC_ACCOUNTING_INFORMATION,
        ctypes.byref(accounting),
        ctypes.sizeof(accounting),
        ctypes.byref(returned),
    ):
        raise OSError(ctypes.get_last_error(), "job accounting unavailable")
    return int(accounting.ActiveProcesses)


def assign_to_job(job: int, process: subprocess.Popen[bytes]) -> bool:
    return bool(kernel32().AssignProcessToJobObject(job, int(process._handle)))  # type: ignore[attr-defined]


def resume_primary_thread(process: subprocess.Popen[bytes]) -> bool:
    """Resume the one thread of a process created suspended (``Popen`` keeps no thread handle)."""
    kernel = kernel32()
    snapshot: int = kernel.CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
    if not snapshot or snapshot == ctypes.c_void_p(-1).value:
        return False
    resumed = False
    try:
        entry = _ThreadEntry()
        entry.dwSize = ctypes.sizeof(entry)
        found = kernel.Thread32First(snapshot, ctypes.byref(entry))
        while found:
            if entry.th32OwnerProcessID == process.pid:
                thread: int = kernel.OpenThread(THREAD_SUSPEND_RESUME, False, entry.th32ThreadID)
                if thread:
                    previous = kernel.ResumeThread(thread)
                    kernel.CloseHandle(thread)
                    resumed = resumed or previous != 0xFFFFFFFF
            found = kernel.Thread32Next(snapshot, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    return resumed


def end_suspended(process: subprocess.Popen[bytes]) -> None:
    """End a process that was never allowed to run and reap it."""
    if process.poll() is None:
        process.kill()
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.wait(timeout=15)


def start_contained(
    argv: list[str],
    environment: dict[str, str],
    job: int,
    *,
    inherit_job: bool,
    cwd: Path | None = None,
    stdout: Any = None,
    stderr: Any = None,
    assign: Callable[[int, subprocess.Popen[bytes]], bool] = assign_to_job,
    resume: Callable[[subprocess.Popen[bytes]], bool] = resume_primary_thread,
) -> subprocess.Popen[bytes]:
    """Create a process suspended, place it in the job, then let it run.

    The process cannot execute (and so cannot create a descendant) before it is in the job. ``inherit_job=True``
    marks the handle inheritable and lists it in the child's inheritable handle list, so the job outlives this
    launcher; ``False`` passes nothing, so the launcher's handle stays the last one. An assignment refused with
    ERROR_ACCESS_DENIED is retried for ``ASSIGNMENT_RETRY_SECONDS`` while the child stays suspended. If it cannot
    be placed in the job or resumed it is ended while still suspended, leaving no child and no descendant, and
    ``ContainmentError`` is raised. ``assign``/``resume`` are the consumers' patch seams; production passes the
    module functions.
    """
    startup: subprocess.STARTUPINFO | None = None
    if inherit_job:
        if not kernel32().SetHandleInformation(job, HANDLE_FLAG_INHERIT, HANDLE_FLAG_INHERIT):
            raise OSError(ctypes.get_last_error(), "job handle could not be made inheritable")
        startup = subprocess.STARTUPINFO()
        startup.lpAttributeList = {"handle_list": [job]}
    process = subprocess.Popen(
        argv,
        cwd=cwd,
        env=environment,
        stdout=stdout,
        stderr=stderr,
        startupinfo=startup,
        creationflags=CREATE_SUSPENDED | getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    deadline = time.monotonic() + ASSIGNMENT_RETRY_SECONDS
    while True:
        ctypes.set_last_error(0)
        if assign(job, process):
            break
        # Read the Win32 error before ending the child so the refusal names its cause.
        error = ctypes.get_last_error()
        if error != ERROR_ACCESS_DENIED or time.monotonic() >= deadline:
            end_suspended(process)
            raise ContainmentError(
                f"process {process.pid} could not be placed in the job (Win32 error {error}); ended before it ran"
            )
        time.sleep(0.05)  # the child is suspended; it cannot run or spawn while the job settles
    if not resume(process):
        # resume_primary_thread's last foreign call is the snapshot walk, so no Win32 code is claimed here.
        end_suspended(process)
        raise ContainmentError(f"process {process.pid} could not be resumed; ended before it ran")
    return process


def stop_job(
    job: int,
    name: str,
    *,
    timeout: float = 15.0,
    members: Callable[[int], list[int]] | None = None,
) -> list[StoppedProcess]:
    """Terminate every member of an open job and confirm each one ended; report what was accounted for.

    ``JobTerminationRefused`` when the job refuses termination; ``JobTerminationUnconfirmed`` when a held member
    handle stays unsignalled or the job still counts an active process after ``timeout`` seconds. ``members`` is
    the consumer's patch seam for member enumeration.
    """
    from ctypes import wintypes

    kernel = kernel32()
    held: list[tuple[int, int | None, str, str]] = []  # pid, handle, executable, outcome
    for pid in (members or job_member_pids)(job):
        opened: int | None = kernel.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE, False, pid)
        if not opened:
            error = ctypes.get_last_error()
            if error == ERROR_INVALID_PARAMETER:  # exited between enumeration and inspection
                held.append((pid, None, "", "exited"))
                continue
            raise OSError(error, f"job member {pid} could not be inspected")
        in_job = wintypes.BOOL(0)
        if not kernel.IsProcessInJob(opened, job, ctypes.byref(in_job)) or not in_job.value:
            kernel.CloseHandle(opened)  # the number was reused by a process outside the job: never waited on
            held.append((pid, None, "", "exited"))
            continue
        outcome = "exited" if kernel.WaitForSingleObject(opened, 0) == 0 else "terminated"
        held.append((pid, opened, image_name(opened), outcome))
    try:
        if not kernel.TerminateJobObject(job, 1):
            raise JobTerminationRefused(f"job {name} refused termination: WinError {ctypes.get_last_error()}")
        deadline = time.monotonic() + timeout
        unconfirmed = []
        for pid, handle, executable, _outcome in held:
            if handle is None:
                continue
            remaining = max(0.0, deadline - time.monotonic())
            if kernel.WaitForSingleObject(handle, int(remaining * 1000)) != 0:
                unconfirmed.append(f"{pid} ({executable})")
        if unconfirmed:
            raise JobTerminationUnconfirmed(
                f"job {name} was terminated but these members had not ended after {timeout:g} s: "
                + ", ".join(unconfirmed)
            )
        while job_active_processes(job) and time.monotonic() < deadline:
            time.sleep(0.05)
        active = job_active_processes(job)
        if active:
            raise JobTerminationUnconfirmed(f"job {name} still counts {active} active process(es) after termination")
    finally:
        for _pid, handle, _executable, _outcome in held:
            if handle is not None:
                kernel.CloseHandle(handle)
    return [StoppedProcess(pid, executable, outcome) for pid, _handle, executable, outcome in held]
