#!/usr/bin/env python3
"""
PreToolUse hook: bridge compliance gate.

Checks if a file being written matches a bridge proposal in NEW, REVISED, or
NO-GO status. Emits an ask checkpoint if the proposal hasn't been approved.

Uses latest-status-per-document parsing: only the first status line after
each Document: header is considered (newest-first per bridge protocol).

Hook type: PreToolUse (tools: Write, Edit)

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

BRIDGE_INDEX_FILENAME = "bridge/INDEX.md"
WRITE_TOOLS = {"Write", "Edit"}
PENDING_PREFLIGHT_STATUSES = {"NEW", "REVISED"}
SPEC_LINK_HEADING_RE = re.compile(
    r"^#{1,6}\s*(?:relevant\s+|linked\s+|governing\s+)?specification(?:\s+links?|\s+references?|\s*)$",
    re.IGNORECASE,
)
SPEC_LINK_TOKEN_RE = re.compile(
    r"\b(?:SPEC|GOV|ADR|DCL|PB|REQ)-[A-Z0-9][A-Z0-9_.-]*\b"
    r"|(?:^|[`(\s])(?:\.claude/rules|groundtruth-kb/docs|docs|bridge)/[^\s`)]+",
    re.IGNORECASE | re.MULTILINE,
)
SPEC_PLACEHOLDER_RE = re.compile(r"\b(?:tbd|todo|none|n/a|not applicable|no relevant)\b", re.IGNORECASE)
OWNER_DECISIONS_PLACEHOLDER_LINE_RE = re.compile(
    r"^[\s>*`_\-:]*"
    r"(?:tbd|todo|none|n/a|not applicable|no relevant(?: owner decisions?)?)"
    r"[\s.`_\-:]*$",
    re.IGNORECASE,
)
SPEC_TEST_HEADING_RE = re.compile(
    r"^#{1,6}\s*(?:spec(?:ification)?[-\s]+to[-\s]+test|specification[-\s]+derived\s+verification)",
    re.IGNORECASE,
)
COMMAND_EVIDENCE_RE = re.compile(
    r"\b(?:python -m pytest|pytest|ruff|npm test|pnpm test|uv run|make test)\b",
    re.IGNORECASE,
)
APPLICABILITY_PREFLIGHT_HEADING_RE = re.compile(
    r"^#{1,6}\s*applicability\s+preflight\s*$",
    re.IGNORECASE,
)
PREFLIGHT_PACKET_HASH_RE = re.compile(
    r"\bpacket_hash\s*:\s*`?sha256:[0-9a-f]{64}`?",
    re.IGNORECASE,
)
PREFLIGHT_MISSING_REQUIRED_RE = re.compile(
    r"\bmissing_required_specs\s*:\s*(?:\[\s*\]|`?\[\s*\]`?|none|None|NONE)",
    re.IGNORECASE,
)

# Owner Decisions / Input section gate (Sub-slice C of GTKB-GOV-AUQ-ENFORCEMENT-STACK).
# Per bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-003.md
# (Codex GO at -004): conditional check that fires only when proposal/report content
# indicates owner-approval scope. Verdict files (GO/NO-GO/VERIFIED first line) are
# excluded — they are evidence narratives, not approval claims.
OWNER_DECISIONS_HEADING_RE = re.compile(
    r"^#{1,6}\s*Owner Decisions(?:\s*/\s*Input)?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
OWNER_APPROVAL_MARKER_RES = (
    # Marker 1: cites Sub-slice B's VERIFIED rule (the AUQ-only rule)
    re.compile(
        r"gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006\.md",
        re.IGNORECASE,
    ),
    # Marker 2: AUQ + decision-context phrase within ~200 chars
    re.compile(
        r"\b(?:AUQ|AskUserQuestion)\b[^.]{0,200}\b(?:answer|approval|decision|directive|authorize|authorization)\b",
        re.IGNORECASE,
    ),
)

ADVISORY_REPORT_HEADER_FIELDS = ("bridge_kind", "Document", "Version", "Author", "Date")
ADVISORY_REPORT_SECTIONS = (
    "Source",
    "Claim",
    "Owner Decision Needed",
    "Recommended Prime Action",
    "Classification Slot",
)
AUDIT_OUTPUT_RELATIVE_PATH = Path(".codex") / "gtkb-hooks" / "last-bridge-audit.json"


def _parse_bridge_index(index_path: Path) -> dict[str, str]:
    """
    Returns {document_name: latest_status}.
    Only the first status line per document entry is considered (latest version).
    """
    result: dict[str, str] = {}
    current_doc: str | None = None
    current_doc_status_seen: bool = False

    try:
        lines = index_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return result

    for line in lines:
        line = line.strip()
        if line.startswith("Document:"):
            current_doc = line.removeprefix("Document:").strip()
            current_doc_status_seen = False
        elif current_doc and not current_doc_status_seen:
            for status in ("VERIFIED", "GO", "NO-GO", "ADVISORY", "REVISED", "NEW"):
                if line.startswith(status + ":"):
                    result[current_doc] = status
                    current_doc_status_seen = True
                    break

    return result


def _first_nonblank_line(content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _is_bridge_markdown_file(file_path: str) -> bool:
    normalized = file_path.replace("\\", "/")
    if not normalized.endswith(".md"):
        return False
    return "/bridge/" in f"/{normalized}" and not normalized.endswith("/bridge/INDEX.md")


def _extract_bridge_id_from_path(file_path: str) -> str | None:
    filename = Path(file_path.replace("\\", "/")).name
    match = re.match(r"(?P<bridge_id>.+)-\d{3}\.md$", filename)
    return match.group("bridge_id") if match else None


def _has_concrete_spec_links(content: str) -> bool:
    lines = content.splitlines()
    start: int | None = None
    for idx, line in enumerate(lines):
        if SPEC_LINK_HEADING_RE.match(line.strip()):
            start = idx + 1
            break
    if start is None:
        return False

    section: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        section.append(line)
    section_text = "\n".join(section).strip()
    return bool(
        section_text and not SPEC_PLACEHOLDER_RE.search(section_text) and SPEC_LINK_TOKEN_RE.search(section_text)
    )


def _has_spec_derived_verification(content: str) -> bool:
    return bool(
        _has_concrete_spec_links(content)
        and SPEC_TEST_HEADING_RE.search(content)
        and COMMAND_EVIDENCE_RE.search(content)
    )


def _proposal_claims_owner_approval(content: str) -> bool:
    """Return True when proposal content signals dependence on owner approval.

    Self-citing (Owner Decisions / Input heading present) also counts as a
    claim because the author invoked the contract. The hook then verifies
    the section is substantive, not placeholder-only.
    """
    if OWNER_DECISIONS_HEADING_RE.search(content):
        return True
    return any(p.search(content) for p in OWNER_APPROVAL_MARKER_RES)


def _has_concrete_owner_decisions_section(content: str) -> bool:
    """Section heading present AND section text non-empty AND not placeholder-only."""
    lines = content.splitlines()
    start: int | None = None
    for i, line in enumerate(lines):
        if OWNER_DECISIONS_HEADING_RE.match(line.strip()):
            start = i + 1
            break
    if start is None:
        return False
    section: list[str] = []
    for line in lines[start:]:
        if line.strip().startswith("#"):
            break
        section.append(line)
    text = "\n".join(section).strip()
    if not text:
        return False
    nonblank_lines = [line for line in (ln.strip() for ln in section) if line]
    return any(not OWNER_DECISIONS_PLACEHOLDER_LINE_RE.match(line) for line in nonblank_lines)


def _advisory_report_template_gaps(content: str) -> list[str]:
    gaps: list[str] = []
    first_line = _first_nonblank_line(content)
    if first_line != "ADVISORY":
        gaps.append("first line ADVISORY")
    for field in ADVISORY_REPORT_HEADER_FIELDS:
        if not re.search(rf"^{re.escape(field)}\s*:", content, re.IGNORECASE | re.MULTILINE):
            gaps.append(f"header field {field}")
    for section in ADVISORY_REPORT_SECTIONS:
        if not re.search(rf"^#{{1,6}}\s*{re.escape(section)}\s*$", content, re.IGNORECASE | re.MULTILINE):
            gaps.append(f"section ## {section}")
    return gaps


def _is_template_shaped_advisory_report(content: str) -> bool:
    return not _advisory_report_template_gaps(content)


def _has_clean_applicability_preflight(content: str) -> bool:
    lines = content.splitlines()
    start: int | None = None
    for idx, line in enumerate(lines):
        if APPLICABILITY_PREFLIGHT_HEADING_RE.match(line.strip()):
            start = idx + 1
            break
    if start is None:
        return False

    section: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        section.append(line)
    section_text = "\n".join(section)
    return bool(PREFLIGHT_PACKET_HASH_RE.search(section_text) and PREFLIGHT_MISSING_REQUIRED_RE.search(section_text))


def _root_contained_scratch_path(cwd: Path, bridge_id: str) -> Path:
    root = cwd.resolve()
    scratch_dir = root / ".tmp" / "bridge-preflight-hook"
    scratch_dir.mkdir(parents=True, exist_ok=True)
    scratch = scratch_dir / f"{bridge_id}-{uuid4().hex}.md"
    scratch.resolve().relative_to(root)
    return scratch


def _run_pending_applicability_preflight(
    *,
    cwd: Path,
    file_path: str,
    bridge_id: str,
    content: str,
) -> tuple[bool, str]:
    scratch_path: Path | None = None
    try:
        scratch_path = _root_contained_scratch_path(cwd, bridge_id)
        scratch_path.write_text(content, encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                "scripts/bridge_applicability_preflight.py",
                "--bridge-id",
                bridge_id,
                "--content-file",
                str(scratch_path),
                "--json",
            ],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        print(f"[Governance] Bridge applicability preflight warning for {file_path}: {exc}", file=sys.stderr)
        return True, ""
    finally:
        if scratch_path is not None:
            try:
                scratch_path.unlink(missing_ok=True)
            except OSError as exc:
                print(f"[Governance] Could not remove bridge preflight scratch file: {exc}", file=sys.stderr)

    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
    if result.returncode not in (0, 5):
        print(
            f"[Governance] Bridge applicability preflight warning for {file_path}: {combined_output}",
            file=sys.stderr,
        )
        return True, ""
    try:
        packet = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(
            f"[Governance] Bridge applicability preflight warning for {file_path}: invalid JSON output",
            file=sys.stderr,
        )
        return True, ""
    missing_required = packet.get("missing_required_specs") or []
    if missing_required:
        return False, json.dumps(missing_required)
    return True, ""


def _read_proposal_target_paths(index_path: Path, doc_name: str) -> list[str]:
    """Read target_paths from the latest proposal file's frontmatter."""
    # Find the latest proposal file path from the index
    try:
        lines = index_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    in_doc = False
    latest_file: str | None = None
    for line in lines:
        line = line.strip()
        if line.startswith("Document:") and line.removeprefix("Document:").strip() == doc_name:
            in_doc = True
            continue
        if in_doc and line.startswith("Document:"):
            break
        if in_doc and latest_file is None:
            for status in ("VERIFIED", "GO", "NO-GO", "ADVISORY", "REVISED", "NEW"):
                if line.startswith(status + ":"):
                    latest_file = line.split(":", 1)[1].strip()
                    break

    if not latest_file:
        return []

    proposal_path = index_path.parent.parent / latest_file
    try:
        content = proposal_path.read_text(encoding="utf-8")
    except OSError:
        return []

    # Look for target_paths in frontmatter or proposal body
    # Simple heuristic: look for target_paths: [...] or target_paths lines
    paths: list[str] = []
    for fline in content.splitlines():
        m = re.match(r"^\s*target_paths?\s*[:=]\s*(.+)", fline, re.IGNORECASE)
        if m:
            raw = m.group(1).strip()
            # Support JSON array or comma-separated
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    paths.extend(str(p) for p in parsed)
                else:
                    paths.append(str(parsed))
            except json.JSONDecodeError:
                for p in re.split(r"[,\s]+", raw):
                    p = p.strip("\"' ")
                    if p:
                        paths.append(p)
    return paths


def _deny_reason_for_content(
    *,
    cwd_path: Path,
    file_path: str,
    content: str,
    run_pending_preflight: bool = True,
) -> str | None:
    if _is_bridge_markdown_file(file_path) and content:
        first_line = _first_nonblank_line(content)
        if first_line == "ADVISORY" and not _is_template_shaped_advisory_report(content):
            return (
                "[Governance] ADVISORY bridge reports must match the verified ADVISORY report template: "
                "first line ADVISORY; header fields bridge_kind, Document, Version, Author, Date; "
                "sections ## Source, ## Claim, ## Owner Decision Needed, "
                "## Recommended Prime Action, and ## Classification Slot."
            )
        if first_line in {"GO", "VERIFIED"} and not _has_clean_applicability_preflight(content):
            return (
                "[Governance] GO and VERIFIED bridge verdicts must include a clean "
                "Applicability Preflight section with packet_hash and "
                "missing_required_specs: []. Generate it with "
                "python scripts/bridge_applicability_preflight.py --bridge-id <document-name>. "
                "(Hard-block per mechanical cross-cutting specification applicability gate.)"
            )
        if first_line == "VERIFIED" and not _has_spec_derived_verification(content):
            return (
                "[Governance] VERIFIED bridge reports must carry Specification Links, "
                "a spec-to-test mapping, and executed test command evidence. "
                "(Hard-block per DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 + "
                "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.)"
            )
        if (
            first_line != "ADVISORY"
            and not first_line.startswith(("GO", "NO-GO", "VERIFIED"))
            and not _has_concrete_spec_links(content)
        ):
            return (
                "[Governance] Implementation proposals must include concrete Specification Links "
                "before bridge submission. "
                "(Hard-block per DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.)"
            )
        if (
            first_line != "ADVISORY"
            and not first_line.startswith(("GO", "NO-GO", "VERIFIED"))
            and _proposal_claims_owner_approval(content)
            and not _has_concrete_owner_decisions_section(content)
        ):
            return (
                "[Governance] Bridge proposals/reports that claim owner-approval scope must "
                "include a non-empty Owner Decisions / Input section enumerating the "
                "AskUserQuestion answers that authorize the work. "
                "(Hard-block per Sub-slice C of GTKB-GOV-AUQ-ENFORCEMENT-STACK; "
                "see bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-003.md.)"
            )
        if run_pending_preflight and first_line in PENDING_PREFLIGHT_STATUSES:
            bridge_id = _extract_bridge_id_from_path(file_path)
            if bridge_id:
                preflight_ok, error_msg = _run_pending_applicability_preflight(
                    cwd=cwd_path,
                    file_path=file_path,
                    bridge_id=bridge_id,
                    content=content,
                )
                if not preflight_ok:
                    return (
                        "[Governance] Pre-filing applicability preflight failed: "
                        f"file_path={file_path}; "
                        f"missing_required_specs={error_msg}. Run "
                        f"python scripts/bridge_applicability_preflight.py --bridge-id {bridge_id} "
                        "for full output. (Hard-block per "
                        "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 "
                        "mechanical enforcement.)"
                    )
    return None


def _write_audit_result(*, cwd_path: Path, file_path: str, content: str, reason: str | None) -> None:
    output_path = cwd_path / AUDIT_OUTPUT_RELATIVE_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "audit_mode": True,
        "file_path": file_path,
        "preflight_passed": reason is None,
        "decision": "pass" if reason is None else "deny",
        "reason": reason,
    }
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _audit_only(argv: list[str]) -> int:
    cwd_path = Path.cwd().resolve()
    file_path = ""
    if "--file-path" in argv:
        idx = argv.index("--file-path")
        if idx + 1 < len(argv):
            file_path = argv[idx + 1]
    if not file_path:
        try:
            payload = json.loads(sys.stdin.read() or "{}")
        except json.JSONDecodeError:
            payload = {}
        cwd_path = Path(str(payload.get("cwd") or ".")).resolve()
        tool_input = payload.get("tool_input") or {}
        file_path = str(tool_input.get("file_path") or "")
        content = str(tool_input.get("content") or "")
    else:
        target = (cwd_path / file_path).resolve()
        try:
            content = target.read_text(encoding="utf-8")
        except OSError:
            content = ""
    reason = _deny_reason_for_content(
        cwd_path=cwd_path,
        file_path=file_path,
        content=content,
        run_pending_preflight=True,
    )
    _write_audit_result(cwd_path=cwd_path, file_path=file_path, content=content, reason=reason)
    print("{}")
    return 0


def main() -> None:
    try:
        from groundtruth_kb.governance.output import emit_ask, emit_deny, emit_pass
    except ImportError:

        def emit_ask(event: str, reason: str) -> None:  # type: ignore[misc]
            out = {
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "permissionDecision": "ask",
                    "permissionDecisionReason": reason,
                    "additionalContext": reason,
                }
            }
            print(json.dumps(out))

        def emit_deny(event: str, reason: str) -> None:  # type: ignore[misc]
            out = {
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                    "additionalContext": reason,
                }
            }
            print(json.dumps(out))

        def emit_pass() -> None:  # type: ignore[misc]
            print("{}")

    if "--audit-only" in sys.argv:
        sys.exit(_audit_only(sys.argv[1:]))

    if "--self-test" in sys.argv:
        emit_ask(
            "PreToolUse",
            "[Governance] Bridge compliance gate active. Ensure bridge proposal has GO status before implementing.",
        )
        sys.exit(0)

    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        emit_pass()
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    cwd = payload.get("cwd", ".")
    cwd_path = Path(cwd).resolve()

    if tool_name not in WRITE_TOOLS:
        emit_pass()
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        emit_pass()
        sys.exit(0)

    content = str(tool_input.get("content", ""))
    reason = _deny_reason_for_content(
        cwd_path=cwd_path,
        file_path=file_path,
        content=content,
        run_pending_preflight=tool_name == "Write",
    )
    if reason:
        emit_deny("PreToolUse", reason)
        sys.exit(0)

    index_path = cwd_path / BRIDGE_INDEX_FILENAME
    if not index_path.exists():
        emit_pass()
        sys.exit(0)

    doc_statuses = _parse_bridge_index(index_path)
    file_path_normalized = file_path.replace("\\", "/")

    for doc_name, status in doc_statuses.items():
        if status in ("NEW", "REVISED", "NO-GO"):
            target_paths = _read_proposal_target_paths(index_path, doc_name)
            for tp in target_paths:
                tp_norm = tp.replace("\\", "/")
                if file_path_normalized.endswith(tp_norm) or tp_norm == file_path_normalized:
                    if status == "NO-GO":
                        emit_ask(
                            "PreToolUse",
                            f"[Governance] Bridge proposal for this module has NO-GO status. "
                            f"Review Codex findings at bridge/{doc_name} before implementing.",
                        )
                    else:
                        emit_ask(
                            "PreToolUse",
                            f"[Governance] Bridge proposal for {doc_name} is pending Codex review ({status}). "
                            f"Wait for GO verdict before implementing.",
                        )
                    sys.exit(0)

    emit_pass()
    sys.exit(0)


if __name__ == "__main__":
    main()
