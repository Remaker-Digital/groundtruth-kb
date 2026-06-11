#!/usr/bin/env python
"""Deterministic QA linter for cheap-model-drafted bridge proposal bodies.

WI-4437 of PROJECT-FABLE-INVESTIGATION (campaign-support tooling). Authorized by
``bridge/gtkb-cheap-draft-linter-002.md`` (Codex GO) under
``PAUTH-DRAFTLINTER-20260610`` / ``DELIB-DRAFTLINTER-20260610``.

The cheap-drafting workflow has a local model (Qwen) draft a proposal body that
Opus then finalizes and files. This linter runs a set of *deterministic*,
*read-only* checks on the drafted body BEFORE Opus finalization so the mechanical
cheap-model failure modes (hallucinated paths/spec-ids, missing structure,
placeholder text, rubber-stamp verification) are caught at ~0 tokens instead of
in an Opus review pass or a Codex GO/NO-GO cycle.

Design contract (per the GO constraints):
  * READ-ONLY. The linter never writes a file, never mutates MemBase, and never
    rewrites the draft. Its only side effect is printing a JSON report.
  * ADVISORY. A linter PASS is not approval to skip Opus finalization or Codex
    review; it is a quality floor for the author's drafting step.
  * NOT a bridge hook. It is invoked manually in the drafting workflow.

It operationalizes ``SPEC-1662`` (GOV-18 assertion quality) and
``DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE`` (mechanical verification, not
AI-trusting-AI).

Exit code: 0 when no check FAILs (warnings allowed); 1 when any check FAILs.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path

# --- Constants -------------------------------------------------------------

# Project root = the directory that contains this script's ``scripts/`` parent.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Canonical MemBase lives at the project root (per the campaign playbook).
DEFAULT_DB = PROJECT_ROOT / "groundtruth.db"

# A repo-style path token: at least one ``/`` and a trailing file extension.
# Anchored so a leading word/slash char does not bleed in (avoids matching the
# tail of a URL or a longer token). Globs/placeholders are filtered separately.
_PATH_TOKEN_RE = re.compile(r"(?<![\w/])([\w.\-]+(?:/[\w.\-]+)+\.\w{1,6})")

_HYG_ID_RE = re.compile(r"\bHYG-\d{3}\b")

# Specification id prefixes recognised by MemBase (DELIB is a deliberation, not
# a spec, so it is intentionally excluded).
_SPEC_ID_RE = re.compile(r"\b(?:SPEC|GOV|ADR|DCL|PB|REQ)-[A-Z0-9][A-Z0-9\-]*\b")

# Heading -> the canonical section it satisfies. A draft must carry one heading
# matching each required section (case-insensitive substring on heading text).
_REQUIRED_SECTIONS = {
    "summary": ("summary",),
    "scope": ("scope",),
    "implementation": ("proposed implementation", "implementation"),
    "verification": ("verification",),
    "acceptance": ("acceptance",),
    "risk": ("risk",),
}

# Whole-word placeholder tokens that always indicate an unfinished draft.
_PLACEHOLDER_WORDS = ("tbd", "todo", "fixme", "tk", "xxx")
# Angle/curly-bracket template markers, e.g. ``<fill>`` ``<topic>`` ``{{x}}``.
_PLACEHOLDER_TEMPLATE_RE = re.compile(r"<[a-z][a-z0-9_\- ]{0,40}>|\{\{[^}]+\}\}", re.IGNORECASE)
# Bare ``n/a`` / ``none`` count as placeholders ONLY when they are a line's whole
# content (a hollow section body), not when they appear inside legitimate prose.
_HOLLOW_LINE_RE = re.compile(r"^\s*(n/a|none|tbd)\s*$", re.IGNORECASE)

# Concrete-assertion signals for the GOV-18 rubber-stamp check: a verification
# section must contain at least one measurable PASS/FAIL signal, not just prose.
_CONCRETE_ASSERTION_RE = re.compile(
    r"\bpytest\b|\bruff\b|\bassert\b|\bPASS\b|\bFAIL\b|\bexit\s*0\b|"
    r"\bTest-Path\b|\bpreflight_passed\b|\d+\s*/\s*\d+|==|grep_absent|"
    r"\bos\.path\.exists\b",
)


# --- Helpers ---------------------------------------------------------------


def _split_sections(text: str) -> dict[str, str]:
    """Map each markdown heading (lower-cased text) to that section's body."""
    sections: dict[str, str] = {}
    current = "_preamble"
    buf: list[str] = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            sections[current] = "\n".join(buf)
            current = line.lstrip("#").strip().lower()
            buf = []
        else:
            buf.append(line)
    sections[current] = "\n".join(buf)
    return sections


def _target_paths_line(text: str) -> set[str]:
    """Path tokens declared on the ``target_paths:`` metadata line are exempt
    from the cited-path check (they may name files the impl will create)."""
    out: set[str] = set()
    for line in text.splitlines():
        if line.strip().lower().startswith("target_paths"):
            out.update(_PATH_TOKEN_RE.findall(line))
    return out


def _result(name: str, status: str, findings: list[str]) -> dict:
    return {"name": name, "status": status, "findings": findings}


# --- Individual checks -----------------------------------------------------


def check_paths(text: str, new_paths: set[str]) -> dict:
    """Check 1 — every repo-style path token resolves under the project root."""
    exempt = _target_paths_line(text) | set(new_paths)
    findings: list[str] = []
    seen: set[str] = set()
    for token in _PATH_TOKEN_RE.findall(text):
        if token in seen or token in exempt:
            continue
        seen.add(token)
        if any(c in token for c in "*<>{}") or "://" in token:
            continue  # glob / placeholder / URL — not a concrete path claim
        if not (PROJECT_ROOT / token).exists():
            findings.append(f"cited path does not resolve: {token}")
    return _result("cited_path_resolution", "fail" if findings else "pass", findings)


def check_hyg_ids(text: str, hyg_ids: set[str] | None) -> dict:
    """Check 2 — every cited HYG-id is in the cluster's frozen baseline set."""
    cited = set(_HYG_ID_RE.findall(text))
    if hyg_ids is None:
        note = f"no --hyg-ids baseline provided; cited: {sorted(cited) or 'none'}"
        return _result("hyg_id_match", "skip", [note])
    stray = sorted(cited - hyg_ids)
    findings = [f"HYG id not in cluster baseline: {i}" for i in stray]
    return _result("hyg_id_match", "fail" if findings else "pass", findings)


def check_phantom_spec(text: str, db_path: Path) -> dict:
    """Check 3 — every cited spec id exists in ``current_specifications``."""
    cited = sorted(set(_SPEC_ID_RE.findall(text)))
    if not cited:
        return _result("phantom_spec", "pass", [])
    if not db_path.exists():
        return _result(
            "phantom_spec",
            "skip",
            [f"MemBase not found at {db_path}; spec existence not verified"],
        )
    # Read-only connection (mode=ro). No mutation is ever issued.
    uri = f"file:{db_path.as_posix()}?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
        try:
            rows = conn.execute("SELECT id FROM current_specifications").fetchall()
        finally:
            conn.close()
    except sqlite3.Error as exc:
        return _result("phantom_spec", "skip", [f"MemBase read error: {exc}"])
    known = {r[0] for r in rows}
    findings = [f"phantom spec id (not in MemBase): {i}" for i in cited if i not in known]
    return _result("phantom_spec", "fail" if findings else "pass", findings)


def check_sections(text: str) -> dict:
    """Check 4 — all required proposal sections are present as headings."""
    headings = [line.lstrip("#").strip().lower() for line in text.splitlines() if line.lstrip().startswith("#")]
    blob = "\n".join(headings)
    missing = [name for name, aliases in _REQUIRED_SECTIONS.items() if not any(alias in blob for alias in aliases)]
    findings = [f"missing required section: {name}" for name in missing]
    return _result("required_sections", "fail" if findings else "pass", findings)


def check_placeholders(text: str) -> dict:
    """Check 5 — no placeholder / unfinished-draft markers."""
    findings: list[str] = []
    lowered = text.lower()
    for word in _PLACEHOLDER_WORDS:
        if re.search(rf"\b{re.escape(word)}\b", lowered):
            findings.append(f"placeholder token present: {word}")
    for m in _PLACEHOLDER_TEMPLATE_RE.findall(text):
        findings.append(f"template placeholder present: {m}")
    for line in text.splitlines():
        if _HOLLOW_LINE_RE.match(line):
            findings.append(f"hollow section body: {line.strip()!r}")
    return _result("placeholder", "fail" if findings else "pass", sorted(set(findings)))


def check_assertion_floor(text: str) -> dict:
    """Check 6 — the verification section carries >=1 concrete assertion (GOV-18)."""
    sections = _split_sections(text)
    verification_bodies = [body for heading, body in sections.items() if "verification" in heading]
    if not verification_bodies:
        # Section-presence is check 4's job; here we only judge rubber-stamping.
        return _result(
            "assertion_floor",
            "warn",
            ["no verification section found to assess for concrete assertions"],
        )
    combined = "\n".join(verification_bodies)
    if _CONCRETE_ASSERTION_RE.search(combined):
        return _result("assertion_floor", "pass", [])
    return _result(
        "assertion_floor",
        "fail",
        ["verification section has no concrete assertion (rubber-stamp risk; GOV-18)"],
    )


# --- Orchestration ---------------------------------------------------------


def lint(
    text: str,
    *,
    hyg_ids: set[str] | None = None,
    db_path: Path | None = None,
    new_paths: set[str] | None = None,
) -> dict:
    """Run all checks and return the structured report (pure; no I/O writes)."""
    db_path = db_path or DEFAULT_DB
    new_paths = new_paths or set()
    checks = [
        check_paths(text, new_paths),
        check_hyg_ids(text, hyg_ids),
        check_phantom_spec(text, db_path),
        check_sections(text),
        check_placeholders(text),
        check_assertion_floor(text),
    ]
    summary = {"pass": 0, "fail": 0, "warn": 0, "skip": 0}
    for c in checks:
        summary[c["status"]] = summary.get(c["status"], 0) + 1
    return {
        "ok": summary["fail"] == 0,
        "checks": checks,
        "summary": summary,
    }


def _parse_id_list(raw: str | None) -> set[str] | None:
    if raw is None:
        return None
    candidate = Path(raw)
    text = candidate.read_text(encoding="utf-8") if candidate.exists() else raw
    return set(re.findall(r"HYG-\d{3}", text))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "draft",
        nargs="?",
        default="-",
        help="path to the draft body file, or '-' for stdin (default)",
    )
    parser.add_argument(
        "--hyg-ids",
        help="comma/space list of the cluster's frozen HYG ids, or a file path",
    )
    parser.add_argument(
        "--new-paths",
        default="",
        help="comma-separated path tokens the impl will create (exempt from check 1)",
    )
    parser.add_argument(
        "--db",
        default=str(DEFAULT_DB),
        help="path to MemBase (groundtruth.db); read-only",
    )
    args = parser.parse_args(argv)

    if args.draft == "-":
        text = sys.stdin.read()
    else:
        text = Path(args.draft).read_text(encoding="utf-8")

    new_paths = {p.strip() for p in args.new_paths.split(",") if p.strip()}
    report = lint(
        text,
        hyg_ids=_parse_id_list(args.hyg_ids),
        db_path=Path(args.db),
        new_paths=new_paths,
    )
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
