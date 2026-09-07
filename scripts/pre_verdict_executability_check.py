"""pre_verdict_executability_check.py - W0.4 pre-verdict executability checker.

Deterministic, read-only CLI that evaluates whether a bridge thread's latest
NEW/REVISED/NO-ACTION proposal/report is EXECUTABLE (a GO on it can be
implemented without a post-GO correction loop). Four gates move the gates
measured to fail AFTER GO (WI-5767) to the PRE-verdict boundary:

- Gate A: PAUTH mutation-class match (operation-time evaluator, import not fork)
- Gate B: cross-harness projection parity
- Gate C: verdict-completeness preconditions (applicability + clause preflights)
- Gate D: mintability (work-intent claim probe + packet-shape prerequisites)

Exit contract: 0 = executable; 5 = named gaps; 2 = usage/thread-resolution error.

Authority: bridge/gtkb-w0-executable-go-pre-verdict-validation-001.md (GO at -002);
DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001; DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]

GAP_KEYS = ("gate", "code", "detail")

UNRESOLVED_PLACEHOLDER_RE = re.compile(r"\bPLACEHOLDER(?:_[A-Z0-9]+)+\b|<fill in [^>\n]+>")


def _json_out(gaps: list[dict[str, str]], executable: bool) -> str:
    return json.dumps({"executable": executable, "gaps": gaps}, indent=2)


def _load_latest_operative(slug: str) -> tuple[str, str] | None:
    """Return (content, relative_path) of the latest NEW/REVISED/NO-ACTION file, or None."""
    import bridge_thread_files as btf

    files = btf.versioned_bridge_files(PROJECT_ROOT, slug)
    candidates = []
    for rel in files:
        relp = Path(rel)
        status = btf.status_from_bridge_file(relp if relp.is_absolute() else PROJECT_ROOT / relp)
        if status in ("NEW", "REVISED", "NO-ACTION"):
            candidates.append((status, relp))
    if not candidates:
        return None
    # latest = highest version number
    candidates.sort(key=lambda pair: btf.parse_versioned_bridge_filename(Path(pair[1]).name)[1])
    status, rel = candidates[-1]
    return (open(rel if rel.is_absolute() else PROJECT_ROOT / rel, encoding="utf-8-sig").read(), str(rel))


def _project_authorization(content: str) -> dict[str, Any] | None:
    import implementation_authorization as ia

    m = re.search(r"(?im)^Project Authorization:\s*(?P<id>[^\s]+)", content)
    if not m:
        return None
    try:
        # WI-6024 bridge-function repair: extract_and_validate_project_authorization
        # requires (project_root, proposal, spec_links); previously called with a
        # single id, which always raised TypeError and falsely reported
        # pauth_metadata_missing on Gate A.
        return ia.extract_and_validate_project_authorization(PROJECT_ROOT, content, ia.extract_spec_links(content))
    except Exception:
        return None


def _gate_a(content: str) -> list[dict[str, str]]:
    """PAUTH mutation-class match using the canonical operation-time evaluator."""
    import implementation_authorization as ia
    from groundtruth_kb.governance import project_authorization_operation_time as pa

    gaps: list[dict[str, str]] = []
    try:
        targets = ia.extract_target_paths(content)
    except Exception:
        targets = []
    if not targets:
        return gaps
    try:
        taxonomy = pa.load_operation_taxonomy(PROJECT_ROOT)
    except Exception:
        taxonomy = None
    pauth = _project_authorization(content)
    # Expand raw allowed_mutation_classes (e.g. "config") into family names
    # (e.g. "configuration") via the canonical operation-time evaluator, so the
    # membership test below compares like-for-like with classify_target's
    # returned family name. Without this expansion, any proposal whose target
    # paths classify as "configuration" is falsely reported
    # pauth_mutation_class_not_allowed even when the PAUTH records "config".
    _allowed_raw = (pauth or {}).get("allowed_mutation_classes", [])
    allowed = set(pa.mutation_class_families(_allowed_raw, taxonomy)) if _allowed_raw else set()
    try:
        classified = [pa.classify_target(t, taxonomy) for t in targets]
    except Exception:
        classified = []
    for ct in classified:
        if allowed and ct.mutation_class not in allowed:
            gaps.append(
                {
                    "gate": "A",
                    "code": "pauth_mutation_class_not_allowed",
                    "detail": f"{ct.path} classifies as {ct.mutation_class}",
                }
            )
    # WI-6130: a Project Authorization row is required only when a protected
    # mutation class (configuration/source/test) is present. Metadata-only
    # targets (groundtruth.db, .groundtruth/*) do not require PAUTH; the
    # canonical packet-free implementation-start path in
    # implementation_authorization.py mirrors this via
    # PROJECT_AUTHORIZATION_REQUIRED_MUTATION_CLASSES. Mirror that set here so
    # this gate agrees with the operation-time evaluator and does not falsely
    # fail a metadata-only proposal with pauth_metadata_missing. When
    # classification itself fails (empty classified), stay conservative and
    # still require PAUTH (fail closed).
    if (
        not allowed
        and pauth is None
        and (
            not classified
            or any(ct.mutation_class in ia.PROJECT_AUTHORIZATION_REQUIRED_MUTATION_CLASSES for ct in classified)
        )
    ):
        gaps.append({"gate": "A", "code": "pauth_metadata_missing", "detail": "no Project Authorization row resolved"})
    return gaps


def _gate_b(content: str) -> list[dict[str, str]]:
    """Cross-harness projection parity: .claude counterpart projections must be declared."""
    import implementation_authorization as ia

    gaps: list[dict[str, str]] = []
    try:
        targets = ia.extract_target_paths(content)
    except Exception:
        targets = []
    declared = set(targets)
    for t in targets:
        rel = t.replace("\\", "/")
        if not (rel.startswith(".claude/skills/") or rel.startswith(".claude/hooks/")):
            continue
        name = rel.split("/")[-1]
        # Enumerate on-disk counterparts under .codex/.cursor/.goose and templates
        counterparts = []
        for base in (".codex", ".cursor", ".goose"):
            p = PROJECT_ROOT / base / rel[len(".claude/") :]
            if p.exists():
                counterparts.append(str(p.relative_to(PROJECT_ROOT)).replace("\\", "/"))
        if rel.startswith(".claude/hooks/"):
            tpl = PROJECT_ROOT / "groundtruth-kb/templates/hooks" / name
            if tpl.exists():
                counterparts.append(str(tpl.relative_to(PROJECT_ROOT)).replace("\\", "/"))
        for cp in counterparts:
            if cp not in declared:
                gaps.append(
                    {
                        "gate": "B",
                        "code": "cross_harness_projection_missing",
                        "detail": f"{cp} exists on disk but is absent from target_paths",
                    }
                )
    return gaps


def _gate_c(slug: str, draft_body: str | None) -> list[dict[str, str]]:
    gaps: list[dict[str, str]] = []
    r = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts/bridge_applicability_preflight.py"), "--bridge-id", slug],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    # WI-6024 bridge-function repair: the preflight emits `preflight_passed: `true``
    # with Markdown backticks; the former exact-substring match never fired, so Gate C
    # always reported applicability_preflight_gap despite a passing preflight.
    if r.returncode != 0 or not re.search(r"preflight_passed:\s*`?true`?", r.stdout):
        gaps.append(
            {
                "gate": "C",
                "code": "applicability_preflight_gap",
                "detail": "bridge_applicability_preflight did not pass",
            }
        )
    r2 = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts/adr_dcl_clause_preflight.py"), "--bridge-id", slug],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    if r2.returncode == 5:
        gaps.append(
            {
                "gate": "C",
                "code": "clause_preflight_gap",
                "detail": "adr_dcl_clause_preflight reports a blocking clause gap",
            }
        )
    if draft_body:
        for heading in ("## Applicability Preflight", "## Clause Applicability"):
            if heading not in draft_body:
                gaps.append(
                    {"gate": "C", "code": "verdict_sections_missing", "detail": f"draft verdict body missing {heading}"}
                )
    return gaps


def _gate_d(slug: str, content: str, session_id: str | None, *, drafting: bool = False) -> list[dict[str, str]]:
    import implementation_authorization as ia

    gaps: list[dict[str, str]] = []
    r = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "scripts/bridge_claim_cli.py"), "status", slug],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    try:
        claim = json.loads(r.stdout or "null")
    except Exception:
        claim = None
    # WI-6144: an expired or TTL-lapsed claim is treated as absent. The claim
    # record carries `expired` / `lapsed_go_implementation` from claim_status.
    claim_is_expired = bool(claim and (claim.get("expired") is True or claim.get("lapsed_go_implementation") is True))
    if claim_is_expired:
        claim = None
    # WI-6144: the foreign-session hold applies only during drafting. An
    # independent reviewer is by definition a different session, so a
    # verification/review pass must not be blocked by a residual claim row.
    if drafting and claim and claim.get("session_id") and claim.get("session_id") != session_id:
        gaps.append(
            {
                "gate": "D",
                "code": "claim_held_by_foreign_session",
                "detail": f"work-intent claim held by {claim.get('session_id')}",
            }
        )
    if not ia.REQUIREMENT_SUFFICIENCY_RE.search(content):
        gaps.append(
            {
                "gate": "D",
                "code": "requirement_sufficiency_gap",
                "detail": "proposal lacks a bounded Requirement Sufficiency phrase",
            }
        )
    return gaps


def _check(slug: str, draft_body: str | None, session_id: str | None) -> tuple[list[dict[str, str]], bool]:
    operative = _load_latest_operative(slug)
    if operative is None:
        # No NEW/REVISED/NO-ACTION operative -> cannot evaluate (usage/thread-resolution error)
        raise SystemExit(2)
    content, _rel = operative
    gaps: list[dict[str, str]] = []
    gaps.extend(_gate_a(content))
    gaps.extend(_gate_b(content))
    gaps.extend(_gate_c(slug, draft_body))
    gaps.extend(_gate_d(slug, content, session_id, drafting=draft_body is not None))
    # dedupe
    seen = set()
    uniq = []
    for g in gaps:
        key = (g["gate"], g["code"], g["detail"])
        if key not in seen:
            seen.add(key)
            uniq.append(g)
    return uniq, not uniq


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bridge-id", required=True)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--draft-verdict-body", type=Path, default=None)
    parser.add_argument("--session-id", default=os.environ.get("GOOSE_SESSION_ID"))
    args = parser.parse_args(argv)
    draft = None
    if args.draft_verdict_body is not None:
        draft = args.draft_verdict_body.read_text(encoding="utf-8")
    try:
        gaps, executable = _check(args.bridge_id, draft, args.session_id)
    except SystemExit as exc:
        if args.json:
            print(_json_out([], False))
        return int(exc.code or 2)
    if args.json:
        print(_json_out(gaps, executable))
    else:
        for g in gaps:
            print(f"[{g['gate']}] {g['code']}: {g['detail']}")
    return 0 if executable else 5


if __name__ == "__main__":
    raise SystemExit(main())
