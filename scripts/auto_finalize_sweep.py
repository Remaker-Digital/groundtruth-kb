#!/usr/bin/env python3
"""WI-4889: auto-finalization sweep for untracked terminal VERIFIED verdicts.

Shared Stop-hook service registered in BOTH ``.claude/settings.json`` and
``.codex/hooks.json`` (the same cross-harness pattern as
``scripts/dispatcher_runtime.py``). On turn-end it drains the dispatch
durability treadmill created by the PHASE-Y dispatcher-daemon go-live
(``DELIB-20266272``): the dispatchable Loyal Opposition harness (Cursor-E)
writes terminal ``VERIFIED`` verdicts but cannot commit them, and no dispatchable
hooked Prime Builder is available to finalize, so verdicts accumulate untracked
and re-fail the WI-4871 guard.

Contract (see ``.claude/rules/auto-finalization-sweep.md``):

- **Cheap-gated:** the only unconditional work is the WI-4871 enumeration
  (``git ls-files --others bridge`` + first-token ``VERIFIED``); commits run
  only when eligible untracked terminal VERIFIED verdicts exist.
- **Eligibility (both required):** (1) the verdict's
  ``author_session_context_id`` differs from the report it ``Responds to``
  (independence; self-review / missing metadata is skipped), and (2) the
  responded-to report's ``target_paths`` are all already committed (clean in
  ``git status``); a dirty/untracked impl path is skipped for manual handling.
- **Verdict-file only:** commits the verdict file plus its untracked
  ``bridge/<slug>-NNN.md`` thread-chain files; NEVER stages source/test.
- **No-capture:** commits exactly the chain via a pathspec-limited partial
  commit (``git commit -- <chain>``), so the caller's working index (which may
  hold unrelated staged changes) is never captured.
- **Lock/contention-safe:** a failed commit (pre-commit gate block,
  ``.git/index.lock`` contention, concurrent ref update) unstages the chain and
  returns without spinning; the verdict is left for the next run.
- **Idempotent + audit-logged:** a second run finds nothing; every finalize/skip
  is appended to ``.gtkb-state/auto-finalize-sweep/sweep.jsonl``.

Fail-soft: any unexpected error is swallowed and the hook exits 0 so it never
blocks turn-end. Disable with ``GTKB_AUTO_FINALIZE_SWEEP_DISABLE=1``.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = _SCRIPTS_DIR.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
_VERIFY_HELPERS = PROJECT_ROOT / ".claude" / "skills" / "gtkb-verify" / "helpers"
if str(_VERIFY_HELPERS) not in sys.path:
    sys.path.insert(0, str(_VERIFY_HELPERS))
from windows_subprocess import no_window_subprocess_kwargs  # noqa: E402

AUDIT_DIR = PROJECT_ROOT / ".gtkb-state" / "auto-finalize-sweep"
AUDIT_LOG = AUDIT_DIR / "sweep.jsonl"
GIT_TIMEOUT_SECONDS = int(os.environ.get("GTKB_AUTO_FINALIZE_GIT_TIMEOUT_SECONDS", "60"))

_VERSION_RE = re.compile(r"-(\d{3})\.md$")
_RESPONDS_RE = re.compile(r"^Responds to:\s*(?:GO\s+)?(bridge/[^\s]+-\d{3}\.md)", re.MULTILINE)
_AUTHOR_ID_RE = re.compile(r"^author_identity:\s*(.+?)\s*$", re.MULTILINE)


def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _actor_context() -> dict:
    """Best-effort actor attribution for audit rows (WI-5767 C1).

    A stable source label, process id, and only available normalized
    harness/session identifiers with their provenance. Missing identity
    variables never block audit append or sweep execution.
    """
    context: dict = {"actor_source": "auto-finalize-sweep", "pid": os.getpid()}
    harness = os.environ.get("GTKB_HARNESS_NAME") or os.environ.get("HARNESS_NAME")
    if harness:
        context["harness_name"] = harness.strip()
        context["harness_provenance"] = "env"
    session_id = (
        os.environ.get("GOOSE_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID") or os.environ.get("GTKB_SESSION_ID")
    )
    if session_id:
        context["session_id"] = session_id.strip()
        context["session_provenance"] = "env"
    return context


def _audit(event: dict) -> None:
    event = {"ts": _now(), **_actor_context(), **event}
    try:
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        with AUDIT_LOG.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=True, sort_keys=True) + "\n")
    except OSError:
        pass


def _git(args: list[str], *, env: dict | None = None, timeout: int | None = None) -> subprocess.CompletedProcess:
    command = ["git", "-C", str(PROJECT_ROOT), *args]
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            env=env,
            timeout=timeout if timeout is not None else GIT_TIMEOUT_SECONDS,
            **no_window_subprocess_kwargs(),
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        detail = f"git subprocess timed out after {exc.timeout} seconds: {' '.join(command)}"
        return subprocess.CompletedProcess(command, 124, stdout, (stderr + "\n" + detail).strip())


def _enumerate_untracked_verified() -> list[str]:
    """Mirror doctor._check_untracked_terminal_verified_verdicts (WI-4871)."""
    result = _git(["ls-files", "--others", "--exclude-standard", "bridge"])
    if result.returncode != 0:
        return []
    found: list[str] = []
    for line in result.stdout.splitlines():
        rel = line.strip().replace("\\", "/")
        if not rel.endswith(".md"):
            continue
        try:
            content = (PROJECT_ROOT / rel).read_text(encoding="utf-8")
        except OSError:
            continue
        first_nonblank = ""
        for raw in content.splitlines():
            if raw.strip():
                first_nonblank = raw.strip()
                break
        if first_nonblank == "VERIFIED":
            found.append(rel)
    return sorted(found)


def _all_untracked_bridge_md() -> list[str]:
    """All untracked ``bridge/*.md`` files (the whole untracked thread surface)."""
    result = _git(["ls-files", "--others", "--exclude-standard", "bridge"])
    if result.returncode != 0:
        return []
    return sorted(
        line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip().endswith(".md")
    )


def _planner_report_only() -> dict:
    """Consult the shared WI-4979 planner in report-only mode, fail-soft."""
    try:
        import worktree_finalization_triage as triage  # type: ignore[import-not-found]

        plan = triage.build_plan(PROJECT_ROOT)
        return {"status": "ok", "summary": triage.summarize_plan(plan)}
    except Exception as exc:  # noqa: BLE001 - Stop-hook advisory must fail soft
        return {"status": "error", "reason": repr(exc)}


def _slug_of(rel: str) -> str | None:
    name = Path(rel).name
    m = _VERSION_RE.search(name)
    if not m:
        return None
    return name[: m.start()]


def _read(rel: str) -> str | None:
    try:
        return (PROJECT_ROOT / rel).read_text(encoding="utf-8")
    except OSError:
        return None


def _author_session_context_id(content: str) -> str | None:
    for raw in content.splitlines():
        if raw.startswith("author_session_context_id:"):
            value = raw.split(":", 1)[1].strip()
            return value or None
    return None


def _is_path_committed(path: str) -> bool:
    """True when ``path`` has no uncommitted (staged/unstaged/untracked) change."""
    result = _git(["status", "--porcelain", "--", path])
    if result.returncode != 0:
        return False
    status_lines = [line for line in result.stdout.splitlines() if line.strip()]
    if not status_lines:
        return True
    if any(line[:2] != " M" for line in status_lines):
        return False
    # Windows/autocrlf can surface CR-at-EOL-only noise in temp repos; keep
    # rejecting every other status form and require both diffs to be clean.
    unstaged = _git(["diff", "--quiet", "--ignore-cr-at-eol", "--", path])
    cached = _git(["diff", "--cached", "--quiet", "--ignore-cr-at-eol", "--", path])
    return unstaged.returncode == 0 and cached.returncode == 0


def _independent(verdict_content: str, report_rel: str) -> tuple[bool, str]:
    verdict_author = _author_session_context_id(verdict_content)
    report_content = _read(report_rel)
    if report_content is None:
        return False, f"responded-to report {report_rel} unreadable"
    report_author = _author_session_context_id(report_content)
    if not verdict_author or not report_author:
        return False, "missing author_session_context_id on verdict or report"
    if verdict_author == report_author:
        return False, "self-review: verdict author session equals report author session"
    return True, "independent"


def _target_paths(report_content: str) -> tuple[list[str] | None, str]:
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        from implementation_authorization import (  # type: ignore[import-not-found]
            AuthorizationError,
            extract_target_paths,
        )
    except Exception as exc:  # pragma: no cover - import-environment guard
        return None, f"extract_target_paths unavailable: {exc}"
    try:
        return extract_target_paths(report_content), "ok"
    except AuthorizationError as exc:
        return None, f"no parseable target_paths: {exc}"
    except Exception as exc:  # pragma: no cover - defensive
        return None, f"target_paths parse error: {exc}"


def _target_paths_from_chain(slug: str, verdict_rel: str, report_rel: str) -> tuple[list[str] | None, str]:
    """Resolve declared ``target_paths`` from a thread's own numbered chain.

    Report-first: a report carrying its own declaration wins, because it is the
    artifact the verdict responds to. Otherwise walk backward through the
    thread's earlier versions, since a proposal often declares the cohort that
    its report only narrates.

    The walk never leaves ``slug``'s own files. A declaration belonging to a
    different thread is not authority for this one, so a chain with no
    declaration of its own reports a distinct reason rather than borrowing one.
    """
    if _slug_of(verdict_rel) != slug or _slug_of(report_rel) != slug:
        return None, f"chain artifacts do not belong to {slug}"

    report_content = _read(report_rel)
    if report_content is not None:
        targets, _why = _target_paths(report_content)
        if targets:
            return targets, "report"

    match = _VERSION_RE.search(Path(report_rel).name)
    # Walk strictly below the report; the report itself was just checked.
    for version in range(int(match.group(1)) - 1 if match else 0, 0, -1):
        content = _read(f"bridge/{slug}-{version:03d}.md")
        if content is None:
            continue
        targets, _why = _target_paths(content)
        if targets:
            return targets, f"backward-walk v{version:03d}"

    return None, "no target_paths anywhere in chain"


def _canonical_verdict_skip_reason(verdict_rel: str, verdict_content: str) -> str | None:
    try:
        from write_verdict import VerifiedFinalizationError, validate_verified_body  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - import-environment guard
        return f"canonical finalizer validation unavailable: {exc}"
    try:
        validate_verified_body(verdict_content, project_root=PROJECT_ROOT)
    except VerifiedFinalizationError as exc:
        return f"canonical_finalizer_rejects_verdict_body: {exc}"

    try:
        import check_protected_commit_authorization as protected_commit  # type: ignore[import-not-found]
    except Exception as exc:  # pragma: no cover - import-environment guard
        return f"protected commit authorization checker unavailable: {exc}"
    try:
        result = protected_commit.evaluate(PROJECT_ROOT, paths=[verdict_rel])
    except Exception as exc:  # noqa: BLE001 - fail closed for stop-hook safety
        return f"protected_commit_authorization_error: {exc}"
    if result.get("status") != "pass":
        findings = result.get("findings") or []
        reasons = [
            f"{finding.get('path', verdict_rel)}: {finding.get('reason', 'unknown reason')}" for finding in findings
        ]
        reason = "; ".join(reasons) if reasons else "checker returned failure"
        return f"protected_commit_authorization_rejects_terminal_verdict: {reason}"
    return None


def _commit_chain(slug: str, chain: list[str], message: str) -> tuple[bool, str]:
    """Commit only ``chain`` via a pathspec-limited partial commit.

    ``git commit -- <chain>`` commits exactly the listed paths regardless of what
    else is in the index, so the caller's unrelated staged changes are preserved
    (never captured). On any failure (pre-commit gate block, ``.git/index.lock``
    contention, concurrent ref update) the just-staged chain is unstaged and the
    function returns without spinning, so the verdict is left untracked for the
    next run or manual handling.
    """
    r = _git(["add", "--", *chain])
    if r.returncode != 0:
        return False, f"add failed: {(r.stderr or r.stdout).strip()[:300]}"
    r = _git(["commit", "-m", message, "--", *chain])
    if r.returncode != 0:
        # Roll the chain back out of the index; leave the caller's index intact.
        _git(["reset", "-q", "HEAD", "--", *chain])
        return False, f"commit blocked/failed: {(r.stderr or r.stdout).strip()[:300]}"
    return True, "committed"


def _author_label(verdict_content: str) -> str:
    m = _AUTHOR_ID_RE.search(verdict_content)
    if not m:
        return "LO"
    ident = m.group(1).strip()
    # e.g. "loyal-opposition/cursor" -> "Cursor-LO"
    harness = ident.split("/")[-1] if "/" in ident else ident
    return f"{harness.capitalize()}-LO"


def sweep(*, dry_run: bool = False) -> dict:
    """Run one sweep pass. Returns a structured summary (also returned for tests)."""
    summary: dict = {"finalized": [], "skipped": [], "errors": []}
    untracked = _enumerate_untracked_verified()
    if not untracked:
        return summary
    try:
        summary["planner"] = _planner_report_only()
    except Exception as exc:  # noqa: BLE001 - Stop-hook advisory must fail soft
        summary["planner"] = {"status": "error", "reason": repr(exc)}
    if summary["planner"].get("status") == "error":
        _audit({"action": "planner_error", "reason": summary["planner"].get("reason")})

    all_untracked = _all_untracked_bridge_md()
    handled_slugs: set[str] = set()

    for verdict_rel in untracked:
        slug = _slug_of(verdict_rel)
        if slug is None or slug in handled_slugs:
            continue
        content = _read(verdict_rel)
        if content is None:
            summary["skipped"].append({"verdict": verdict_rel, "reason": "unreadable"})
            continue

        m = _RESPONDS_RE.search(content)
        if not m:
            summary["skipped"].append({"verdict": verdict_rel, "reason": "no Responds-to report reference"})
            _audit({"action": "skip", "verdict": verdict_rel, "reason": "no Responds-to report reference"})
            continue
        report_rel = m.group(1)

        ok, why = _independent(content, report_rel)
        if not ok:
            summary["skipped"].append({"verdict": verdict_rel, "reason": why})
            _audit({"action": "skip", "verdict": verdict_rel, "reason": why})
            continue

        report_content = _read(report_rel)
        targets, tp_why = _target_paths(report_content or "")
        if targets is None:
            summary["skipped"].append({"verdict": verdict_rel, "reason": tp_why})
            _audit({"action": "skip", "verdict": verdict_rel, "reason": tp_why})
            continue
        dirty = [p for p in targets if not _is_path_committed(p)]
        if dirty:
            reason = f"verified impl not committed: {', '.join(sorted(dirty))}"
            summary["skipped"].append({"verdict": verdict_rel, "reason": reason})
            _audit({"action": "skip", "verdict": verdict_rel, "reason": reason})
            continue

        canonical_skip = _canonical_verdict_skip_reason(verdict_rel, content)
        if canonical_skip:
            summary["skipped"].append({"verdict": verdict_rel, "reason": canonical_skip})
            _audit({"action": "skip", "verdict": verdict_rel, "reason": canonical_skip})
            continue

        # Eligible. Stage the verdict + all untracked chain .md files for this slug.
        chain = sorted(rel for rel in all_untracked if _slug_of(rel) == slug)
        version = _VERSION_RE.search(Path(verdict_rel).name)
        version_tag = f"-{version.group(1)}" if version else ""
        label = _author_label(content)
        message = f"chore(bridge): finalize {label} {slug} VERIFIED verdict ({version_tag})"

        if dry_run:
            summary["finalized"].append({"slug": slug, "chain": chain, "message": message, "dry_run": True})
            handled_slugs.add(slug)
            continue

        ok, why = _commit_chain(slug, chain, message)
        if ok:
            summary["finalized"].append({"slug": slug, "chain": chain})
            _audit({"action": "finalize", "slug": slug, "chain": chain, "message": message})
            handled_slugs.add(slug)
        else:
            summary["errors"].append({"slug": slug, "reason": why})
            _audit({"action": "error", "slug": slug, "reason": why})
            # Do not spin/retry; leave for the next run or manual handling.

    return summary


def probe() -> dict:
    """WI-5767 C1: read-only sweep probe.

    Reuses the sweep planner in dry-run and emits a schema-versioned report of
    the terminal backlog, would-finalize cohort, blocked cohort, and skip-reason
    histogram. Probe mode MUST NOT commit, append audit rows, alter bridge
    state, or change normal Stop-hook behavior.
    """
    # Suppress audit-row appends during the probe so it is strictly read-only:
    # the dry-run sweep would otherwise write skip/finalize audit rows through
    # _audit. We temporarily no-op _audit for the probe pass.
    original_audit = _audit

    def _noop_audit(event: dict) -> None:  # type: ignore[no-untyped-def]
        return None

    globals()["_audit"] = _noop_audit
    try:
        summary = sweep(dry_run=True)
    finally:
        globals()["_audit"] = original_audit
    would_finalize = [item["slug"] for item in summary.get("finalized", [])]
    skipped = summary.get("skipped", [])
    blocked = [
        {"verdict": item["verdict"], "reason": item.get("reason", "unknown")}
        for item in skipped
        if item.get("reason") and "impl not committed" in str(item["reason"])
    ]
    histogram: dict[str, int] = {}
    for item in skipped:
        reason = str(item.get("reason", "unknown"))
        key = reason.split(":")[0][:80] if reason else "unknown"
        histogram[key] = histogram.get(key, 0) + 1
    return {
        "schema_version": 1,
        "terminal_verified_backlog": summary.get("finalized", []) + skipped,
        "would_finalize": would_finalize,
        "blocked": blocked,
        "skip_reason_histogram": histogram,
    }


def main() -> int:
    if os.environ.get("GTKB_AUTO_FINALIZE_SWEEP_DISABLE") == "1":
        return 0
    # WI-5767 C1: opt-in read-only probe mode emits JSON to stdout and exits.
    if "--probe" in sys.argv:
        sys.stdout.write(json.dumps(probe(), indent=2, sort_keys=True) + "\n")
        return 0
    # Stop-hook payload arrives on stdin; we do not need it. Drain to avoid blocking.
    try:
        if not sys.stdin.isatty():
            sys.stdin.read()
    except Exception:
        pass
    try:
        sweep()
    except Exception as exc:  # pragma: no cover - fail-soft hook contract
        _audit({"action": "fatal", "reason": repr(exc)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
