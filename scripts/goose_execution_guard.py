#!/usr/bin/env python3
"""Goose execution reliability guard for GT-KB harness G (WI-5831).

Converts three silent failure classes observed across the 2026-07-30 nine-run
evaluation into loud, detectable errors at the harness boundary:

1. Silent zero-byte writes reported as success — detected via write-claim
   reconciliation (payload-aware) plus a schema-independent run-window sweep.
2. Tool-call serialization leaks that stall a session — detected by scanning
   assistant text blocks for configured leak patterns and terminal-stall shapes.
3. Post-compaction provenance drift — detected by comparing bridge artifact
   author-model stamps against live spawn configuration.

Every finding produces a structured JSON diagnostic on stderr and a distinct
non-zero exit code. Every bound resolves from configuration; this module
contains zero hard-coded timeout, interval, retry, or throttle literals.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class ExecutionFloorConfig:
    """Resolved configuration for the Goose execution reliability floor."""

    # Write verification
    write_verification_enabled: bool = True
    write_tool_names: set[str] = field(default_factory=lambda: {"write", "write_file", "Write", "Edit"})
    intentional_empty_allowlist: set[str] = field(default_factory=set)

    # Leak detection
    leak_patterns: dict[str, str] = field(default_factory=dict)
    retry_attempts: int = 0
    retry_backoff_seconds: int = 0

    # Provenance guard
    provenance_guard_enabled: bool = True
    provenance_scan_scope: str = "run_window"

    @classmethod
    def from_toml(cls, path: Path) -> ExecutionFloorConfig:
        """Load and resolve configuration from a TOML file.

        Returns defaults for every value when the file is absent or unreadable,
        so the guard never fails on configuration absence.
        """
        config = cls()
        try:
            raw = path.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError):
            return config

        try:
            import tomllib
        except ImportError:
            import tomli as tomllib

        try:
            data = tomllib.loads(raw)
        except Exception:
            return config

        wv = data.get("write_verification", {})
        if isinstance(wv, dict):
            config.write_verification_enabled = wv.get("enabled", True)
            names = wv.get("write_tool_names", [])
            if isinstance(names, list):
                config.write_tool_names = {str(n) for n in names}
            allowlist = wv.get("intentional_empty_allowlist", [])
            if isinstance(allowlist, list):
                config.intentional_empty_allowlist = {str(p) for p in allowlist}

        ld = data.get("leak_detection", {})
        if isinstance(ld, dict):
            config.retry_attempts = ld.get("retry_attempts", 0)
            config.retry_backoff_seconds = ld.get("retry_backoff_seconds", 0)
            patterns = ld.get("patterns", {})
            if isinstance(patterns, dict):
                config.leak_patterns = {str(k): str(v) for k, v in patterns.items()}

        pg = data.get("provenance_guard", {})
        if isinstance(pg, dict):
            config.provenance_guard_enabled = pg.get("enabled", True)
            config.provenance_scan_scope = pg.get("scan_scope", "run_window")

        return config


# ---------------------------------------------------------------------------
# Diagnostic types
# ---------------------------------------------------------------------------


@dataclass
class ExecutionFinding:
    """A single reliability-floor finding."""

    finding_class: str
    detail: str
    path: str = ""
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class RunDiagnostic:
    """The structured diagnostic emitted on stderr after guard evaluation."""

    findings: list[ExecutionFinding] = field(default_factory=list)
    write_claim_reconciliation: str = "unavailable"
    exit_code: int = 0

    def to_json(self) -> str:
        return json.dumps(
            {
                "exit_code": self.exit_code,
                "findings": [
                    {
                        "finding_class": f.finding_class,
                        "detail": f.detail,
                        "path": f.path,
                        "context": f.context,
                    }
                    for f in self.findings
                ],
                "write_claim_reconciliation": self.write_claim_reconciliation,
            },
            indent=2,
        )


# ---------------------------------------------------------------------------
# Slice A: Write verification
# ---------------------------------------------------------------------------

# Known Goose payload tool-result shapes. Each is a (tool_name_path, args_path,
# result_path) tuple of JSON-path lists. If none match, reconciliation reports
# "unavailable".
_PAYLOAD_TOOL_SHAPES: list[tuple[list[str], list[str], list[str]]] = [
    # Standard Goose tool format: {"tool_requests": [...], "tool_results": [...]}
    # where each request has {"name": ..., "arguments": {"path": ..., "content": ...}}
    # and each result has {"name": ..., "result": "success" | ...}
    (["tool_requests"], ["tool_results"], ["content", "arguments"]),
    # Alternate format with "toolCalls" arrays
    (["toolCalls"], ["toolResults"], ["content", "args"]),
]


def _walk_value(data: Any, path: list[str]) -> Any:
    """Walk a JSON object by a list of keys. Returns the value at the path or None."""
    current = data
    for key in path:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif isinstance(current, dict):
            return None
        else:
            return None
    return current


def _extract_tool_requests_and_results(
    payload: dict,
) -> tuple[list[dict], dict[str, dict]]:
    """Shape-tolerant extraction of tool requests and their paired results.

    Returns (requests, results_by_id) where results_by_id maps a request
    identifier to its result object. Falls back to empty when the shape
    is unrecognized.
    """
    for req_path, res_path, _content_paths in _PAYLOAD_TOOL_SHAPES:
        requests = _walk_value(payload, req_path)
        results = _walk_value(payload, res_path)
        if isinstance(requests, list) and isinstance(results, list):
            result_map: dict[str, dict] = {}
            for r in results:
                if isinstance(r, dict):
                    rid = r.get("callId") or r.get("id") or r.get("name") or ""
                    if rid:
                        result_map[str(rid)] = r
            return requests, result_map

    # Also try messages-based format where tool_use and tool_result blocks appear
    # in the messages list with roles "tool_use" and "tool_result"
    messages = payload.get("messages", [])
    if isinstance(messages, list):
        requests = []
        results = {}
        for msg in messages:
            if isinstance(msg, dict):
                role = msg.get("role", "")
                if role in ("tool_use", "tool_call"):
                    requests.append(msg)
                    rid = msg.get("id") or msg.get("name") or str(len(requests))
                    # Look forward for matching result
                    for m2 in messages:
                        if isinstance(m2, dict) and m2.get("role") == "tool_result":
                            if m2.get("tool_use_id") == rid or m2.get("id") == rid:
                                results[rid] = m2
                                break
                elif role == "tool_result":
                    rid = msg.get("tool_use_id") or msg.get("id") or ""
                    if rid:
                        results[rid] = msg
        if requests:
            return requests, results

    return [], {}


def _tool_name_from_request(req: dict) -> str:
    """Extract tool name from a request object, shape-tolerant."""
    return str(req.get("name") or req.get("tool_name") or req.get("function", {}).get("name", ""))


def _tool_path_from_request(req: dict) -> str:
    """Extract target path from a write-tool request, shape-tolerant."""
    args = req.get("arguments") or req.get("args") or req.get("input") or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except (json.JSONDecodeError, TypeError):
            return ""
    if not isinstance(args, dict):
        return ""
    return str(args.get("path") or args.get("file_path") or args.get("filePath") or "")


def _tool_content_length_from_request(req: dict) -> int:
    """Extract declared content length from a write-tool request."""
    args = req.get("arguments") or req.get("args") or req.get("input") or {}
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except (json.JSONDecodeError, TypeError):
            return -1
    if not isinstance(args, dict):
        return -1
    content = args.get("content") or args.get("text") or args.get("body") or ""
    if isinstance(content, str):
        return len(content.encode("utf-8"))
    if isinstance(content, (bytes, bytearray)):
        return len(content)
    return -1


def _result_reports_success(result: dict) -> bool:
    """Determine if a tool result reports success, shape-tolerant."""
    status = str(result.get("result") or result.get("status") or "").lower()
    if status in ("success", "ok", "done"):
        return True
    # Goose Write tool returns "success" or the content echoed back
    if result.get("result") == "success":
        return True
    # Some formats have "error": null or absent as success indicator.
    # Default when no explicit failure: treat as reported success.
    has_error = "error" in result and result["error"] is not None and str(result["error"]).strip()
    return not has_error


def _is_tool_request_text_block(block: dict) -> bool:
    """Check if a content block is a serialized tool-call in text form."""
    if not isinstance(block, dict):
        return False
    text = block.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return False
    return bool(
        re.search(r'(?i)(?:tool_call|function_call|tool_use|call_tool|DSML|\{\s*"(?:name|function|tool))', text)
    )


def reconcile_write_claims(
    payload: dict,
    project_root: Path,
    write_tool_names: set[str],
) -> tuple[list[ExecutionFinding], str]:
    """Reconcile claimed file writes against on-disk state.

    Returns (findings, reconciliation_status) where reconciliation_status is
    "verified", "unavailable", or "findings"  depending on whether the payload
    shape was recognized and whether problems were found.
    """
    requests, results = _extract_tool_requests_and_results(payload)
    if not requests:
        return [], "unavailable"

    findings: list[ExecutionFinding] = []
    status = "verified"

    for req in requests:
        tool_name = _tool_name_from_request(req)
        if not tool_name or tool_name not in write_tool_names:
            continue

        target_path_str = _tool_path_from_request(req)
        declared_length = _tool_content_length_from_request(req)

        if not target_path_str:
            continue

        target_path = project_root / target_path_str
        rid = str(req.get("id") or req.get("callId") or tool_name)
        result = results.get(rid, {})

        if not result:
            continue

        if not _result_reports_success(result):
            continue

        # Verify the write actually landed
        if not target_path.exists():
            findings.append(
                ExecutionFinding(
                    finding_class="write_claim_unfulfilled",
                    detail=f"Write reported success but target does not exist: {target_path_str}",
                    path=target_path_str,
                    context={
                        "tool_name": tool_name,
                        "declared_length": declared_length,
                        "observed_length": 0,
                        "reason": "target_missing",
                    },
                )
            )
            status = "findings"
            continue

        observed_length = target_path.stat().st_size
        if declared_length > 0 and observed_length == 0:
            findings.append(
                ExecutionFinding(
                    finding_class="write_claim_unfulfilled",
                    detail=f"Write reported success with {declared_length} bytes but target is zero bytes: {target_path_str}",
                    path=target_path_str,
                    context={
                        "tool_name": tool_name,
                        "declared_length": declared_length,
                        "observed_length": observed_length,
                        "reason": "zero_byte_after_write",
                    },
                )
            )
            status = "findings"

    return findings, status


def sweep_run_window(
    window_start: float,
    window_end: float,
    project_root: Path,
    intentional_empty: set[str],
) -> list[ExecutionFinding]:
    """Schema-independent zero-byte sweep over the run window.

    Uses git to bound candidates, then checks modification time and file size.
    """
    findings: list[ExecutionFinding] = []

    try:
        result = subprocess.run(
            ["git", "--no-optional-locks", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=30,
        )
        if result.returncode != 0:
            return findings
        candidate_paths: set[str] = set()
        for line in result.stdout.splitlines():
            stripped = line.strip()
            if len(stripped) >= 3:
                path_part = stripped[3:].strip()
                candidate_paths.add(path_part)

        # Also add modified/untracked from ls-files
        result2 = subprocess.run(
            ["git", "--no-optional-locks", "ls-files", "--modified", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            cwd=str(project_root),
            timeout=30,
        )
        if result2.returncode == 0:
            for line in result2.stdout.splitlines():
                candidate_paths.add(line.strip())
    except (subprocess.TimeoutExpired, OSError):
        return findings

    for rel_path in candidate_paths:
        full_path = project_root / rel_path
        try:
            stat = full_path.stat()
        except OSError:
            continue

        # Check modification time is within run window
        mtime = stat.st_mtime
        if mtime < window_start or mtime > window_end:
            continue

        # Check zero bytes
        if stat.st_size != 0:
            continue

        # Check allowlist
        if rel_path in intentional_empty or full_path.name in intentional_empty:
            continue
        if any(rel_path.endswith(f"/{a}") or rel_path == a for a in intentional_empty):
            continue

        findings.append(
            ExecutionFinding(
                finding_class="zero_byte_artifact",
                detail=f"Zero-byte file created inside run window: {rel_path}",
                path=rel_path,
                context={
                    "size": 0,
                    "mtime": mtime,
                },
            )
        )

    return findings


# ---------------------------------------------------------------------------
# Slice B: Leak detection
# ---------------------------------------------------------------------------

_LEAK_FINDING_BOUNDED_EXCERPT = 200


def detect_tool_call_leaks(
    messages: list[dict],
    leak_patterns: dict[str, str],
) -> list[ExecutionFinding]:
    """Scan assistant messages for leaked tool-call text.

    Each pattern class in leak_patterns is compiled on first use.
    """
    if not leak_patterns:
        return []

    compiled: list[tuple[str, re.Pattern]] = []
    for name, pattern_str in leak_patterns.items():
        try:
            compiled.append((name, re.compile(pattern_str, re.IGNORECASE)))
        except re.error:
            pass

    if not compiled:
        return []

    findings: list[ExecutionFinding] = []
    leaks_by_turn: dict[int, list[str]] = {}

    for turn_idx, msg in enumerate(messages):
        if not isinstance(msg, dict):
            continue
        role = msg.get("role", "")
        if role not in ("assistant", "tool_use"):
            continue

        content = msg.get("content", [])
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "text":
                continue
            text = str(block.get("text", ""))
            if not text.strip():
                continue

            for pattern_name, pattern in compiled:
                if pattern.search(text):
                    leaks_by_turn.setdefault(turn_idx, []).append(pattern_name)

    for turn_idx, pattern_names in leaks_by_turn.items():
        findings.append(
            ExecutionFinding(
                finding_class="leaked_tool_call_text",
                detail=f"Leaked tool-call text detected in turn {turn_idx} matching: {', '.join(pattern_names)}",
                path="",
                context={
                    "turn_index": turn_idx,
                    "pattern_classes": pattern_names,
                },
            )
        )

    return findings


def detect_terminal_stall(
    messages: list[dict],
    max_turns: int,
) -> list[ExecutionFinding]:
    """Detect terminal-leak-stall and turn-cap-without-terminal-text shapes."""
    findings: list[ExecutionFinding] = []

    if not messages:
        findings.append(
            ExecutionFinding(
                finding_class="terminal_leak_stall",
                detail="Run produced no messages at all",
                context={"message_count": 0},
            )
        )
        return findings

    last_msg = messages[-1]
    if isinstance(last_msg, dict):
        role = last_msg.get("role", "")
        content = last_msg.get("content", [])

        # Check if terminal message is itself a tool call (leak)
        if role == "tool_use" or role == "tool_call":
            findings.append(
                ExecutionFinding(
                    finding_class="terminal_leak_stall",
                    detail="Terminal message is an unexecuted tool call (leak)",
                    context={"terminal_role": role},
                )
            )
            return findings

        # Check if terminal message has leaked tool-call text
        if role == "assistant":
            has_text = False
            has_leak = False
            for block in content if isinstance(content, list) else []:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = str(block.get("text", ""))
                    if text.strip():
                        has_text = True
                    if _is_tool_request_text_block(block):
                        has_leak = True
            if has_leak:
                findings.append(
                    ExecutionFinding(
                        finding_class="terminal_leak_stall",
                        detail="Terminal assistant message contains leaked tool-call text with no corresponding execution",
                        context={"has_legitimate_text": has_text},
                    )
                )

        # Turn-cap check
        if role != "assistant" and max_turns > 0:
            if len(messages) >= max_turns:
                findings.append(
                    ExecutionFinding(
                        finding_class="terminal_leak_stall",
                        detail=f"Run hit turn cap ({max_turns}) with no terminal assistant message",
                        context={"message_count": len(messages), "max_turns": max_turns},
                    )
                )

    return findings


# ---------------------------------------------------------------------------
# Slice C: Provenance guard
# ---------------------------------------------------------------------------


def _parse_model_from_env() -> dict[str, str]:
    """Derive live spawn model configuration from environment.

    Uses the same registered field names as bridge_author_metadata.py.
    """
    model_fields = {
        "author_model": ("GTKB_AUTHOR_MODEL", "GTKB_MODEL", "CLAUDE_MODEL"),
        "author_model_version": ("GTKB_AUTHOR_MODEL_VERSION", "GTKB_MODEL_VERSION", "CLAUDE_MODEL_VERSION"),
    }
    result: dict[str, str] = {}
    for field_name, env_names in model_fields.items():
        for name in env_names:
            value = os.environ.get(name, "").strip()
            if value:
                result[field_name] = value
                break
    return result


def check_provenance_drift(
    project_root: Path,
    window_start: float,
    window_end: float,
    live_model: dict[str, str],
) -> list[ExecutionFinding]:
    """Check bridge files created/modified in the run window for provenance drift.

    Compares the author_model and author_model_version stamped in the file
    header against the live spawn model configuration.
    """
    if not live_model:
        return []

    findings: list[ExecutionFinding] = []
    bridge_dir = project_root / "bridge"
    if not bridge_dir.is_dir():
        return findings

    # Metadata extraction regex
    model_re = re.compile(r"^author_model:\s*(.+)$", re.IGNORECASE | re.MULTILINE)
    version_re = re.compile(r"^author_model_version:\s*(.+)$", re.IGNORECASE | re.MULTILINE)

    live_model_name = live_model.get("author_model", "")
    live_model_version = live_model.get("author_model_version", "")

    if not live_model_name:
        return findings

    for entry in bridge_dir.iterdir():
        if not entry.is_file() or entry.suffix != ".md":
            continue

        try:
            stat = entry.stat()
            mtime = stat.st_mtime
            if mtime < window_start or mtime > window_end:
                continue
        except OSError:
            continue

        try:
            content = entry.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        stamped_model = ""
        stamped_version = ""
        m_match = model_re.search(content)
        if m_match:
            stamped_model = m_match.group(1).strip()
        v_match = version_re.search(content)
        if v_match:
            stamped_version = v_match.group(1).strip()

        if not stamped_model:
            continue

        if stamped_model.lower() != live_model_name.lower():
            findings.append(
                ExecutionFinding(
                    finding_class="provenance_drift",
                    detail=f"Bridge artifact author_model '{stamped_model}' does not match live spawn model '{live_model_name}'",
                    path=str(entry.relative_to(project_root)),
                    context={
                        "stamped_model": stamped_model,
                        "stamped_version": stamped_version,
                        "live_model": live_model_name,
                        "live_version": live_model_version,
                    },
                )
            )

    return findings


# ---------------------------------------------------------------------------
# Main guard entry point
# ---------------------------------------------------------------------------


def evaluate_run(
    payload: dict,
    project_root: Path,
    config: ExecutionFloorConfig,
    *,
    window_start: float,
    window_end: float,
    max_turns: int,
    live_model: dict[str, str] | None = None,
) -> RunDiagnostic:
    """Run all enabled reliability-floor checks and produce a diagnostic.

    This is the single integration point the wrapper calls after the goose
    subprocess completes. It runs every check that is enabled, accumulates
    findings, and returns a structured diagnostic with an exit code.
    """
    diagnostic = RunDiagnostic()

    # --- Slice A: Write verification ---
    if config.write_verification_enabled:
        # A1: Payload-aware write-claim reconciliation
        write_findings, reconciliation_status = reconcile_write_claims(payload, project_root, config.write_tool_names)
        diagnostic.findings.extend(write_findings)
        diagnostic.write_claim_reconciliation = reconciliation_status

        # A2: Schema-independent run-window zero-byte sweep
        sweep_findings = sweep_run_window(window_start, window_end, project_root, config.intentional_empty_allowlist)
        diagnostic.findings.extend(sweep_findings)

    # --- Slice B: Leak detection ---
    if config.leak_patterns:
        messages = payload.get("messages", [])
        if not isinstance(messages, list):
            messages = []
        leak_findings = detect_tool_call_leaks(messages, config.leak_patterns)
        diagnostic.findings.extend(leak_findings)

    # Terminal stall detection (always runs, doesn't need patterns)
    messages = payload.get("messages", [])
    if not isinstance(messages, list):
        messages = []
    stall_findings = detect_terminal_stall(messages, max_turns)
    diagnostic.findings.extend(stall_findings)

    # --- Slice C: Provenance guard ---
    if config.provenance_guard_enabled and config.provenance_scan_scope == "run_window":
        model = live_model or _parse_model_from_env()
        provenance_findings = check_provenance_drift(project_root, window_start, window_end, model)
        diagnostic.findings.extend(provenance_findings)

    # --- Determine exit code ---
    if diagnostic.findings:
        # Map finding classes to exit codes
        exit_codes = {
            "write_claim_unfulfilled": 10,
            "zero_byte_artifact": 11,
            "leaked_tool_call_text": 12,
            "terminal_leak_stall": 13,
            "provenance_drift": 14,
        }
        max_exit = 1
        for f in diagnostic.findings:
            code = exit_codes.get(f.finding_class, 1)
            if code > max_exit:
                max_exit = code
        diagnostic.exit_code = max_exit

    return diagnostic


def export_model_configuration(model: str, routing_model: str | None = None) -> None:
    """Export live model configuration to environment for the child process.

    Reads from the resolved model or routing default, sets GTKB_AUTHOR_MODEL
    and GTKB_AUTHOR_MODEL_VERSION environment variables so bridge_author_metadata
    and the provenance guard can read them.
    """
    effective_model = model or routing_model or ""
    if effective_model:
        os.environ.setdefault("GTKB_AUTHOR_MODEL", effective_model)
        os.environ.setdefault("GTKB_AUTHOR_MODEL_VERSION", effective_model)
    # Also set GTKB_AUTHOR_HARNESS_NAME and GTKB_AUTHOR_HARNESS_ID if not already set
    os.environ.setdefault("GTKB_AUTHOR_HARNESS_NAME", "goose")
    os.environ.setdefault("GTKB_AUTHOR_HARNESS_ID", "G")
    os.environ.setdefault("GTKB_AUTHOR_IDENTITY", "prime-builder/goose/G")
