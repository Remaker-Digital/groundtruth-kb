"""Render docs/evidence.md from docs/_generated/evidence_metrics.json.

`docs/evidence.md` is a *generated* file on this workstream. The canonical
provenance record is `docs/_generated/evidence_metrics.json`; this script
deterministically renders that JSON into the adopter-facing markdown so the
two artifacts cannot drift.

Usage:
    python scripts/render_evidence_md.py              # write docs/evidence.md
    python scripts/render_evidence_md.py --to <path>  # write to an explicit path

Exit codes:
    0 — markdown rendered (or printed to --to path).
    2 — JSON missing, malformed, or required fields absent.

Relationship to `scripts/collect_evidence_metrics.py`:
- The collector writes the JSON.
- This renderer writes the markdown *from* the JSON.
- `collect_evidence_metrics.py --verify` additionally renders a fresh
  markdown to a temp path and diffs it against the committed markdown; any
  divergence fails the gate.

Codex condition P1-1 (bridge/gtkb-start-here-adopter-rewrite-implementation-006.md):
- docs/evidence.md must be an exact render of the committed JSON.
- Developers edit the template in this file, not the rendered markdown.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = REPO_ROOT / "docs" / "_generated" / "evidence_metrics.json"
DEFAULT_OUTPUT_PATH = REPO_ROOT / "docs" / "evidence.md"


def _format_value(value: Any) -> str:
    """Render a metric value as a compact human-readable string."""
    if isinstance(value, dict):
        # Specifically: {"status": "pass", "source_files": N}
        if value.get("status") == "pass" and "source_files" in value:
            return f"pass across {value['source_files']} source files"
        # Generic fallback — stable ordered serialization.
        return json.dumps(value, sort_keys=True)
    if isinstance(value, float):
        return f"{value:g}%" if 0 < value <= 100 else f"{value:g}"
    return str(value)


def _format_percent(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:g}%"
    return str(value)


def render(data: dict[str, Any]) -> str:
    """Render the evidence markdown from a loaded evidence-metrics dict.

    The layout is f-string-driven rather than Jinja-templated to keep the
    renderer a single stdlib file. Every surface visible to adopters is
    derived from the JSON; no content lives only in this template.
    """
    required_top = {"generated_at_commit", "generated_at_utc", "gate_bound", "live_snapshot"}
    missing = required_top - set(data)
    if missing:
        raise ValueError(f"evidence_metrics.json missing required top-level fields: {sorted(missing)}")

    commit = data["generated_at_commit"]
    timestamp = data["generated_at_utc"]
    gate_bound = data["gate_bound"]
    live_snapshot = data["live_snapshot"]

    # Build gate-bound table.
    # Expected gate-bound metrics (by name). We render whatever is present;
    # unknown rows appear with a pass-through provenance footnote.
    gate_rows: list[str] = []
    gate_footnotes: list[str] = []
    for idx, m in enumerate(gate_bound, start=1):
        name = m["metric_name"]
        value = m["value"]
        if name == "test_count":
            display_name = "Tests collected"
            value_str = _format_value(value)
            note = "deterministic; exact equality enforced on re-run"
        elif name == "mypy_strict":
            display_name = "`mypy --strict`"
            value_str = _format_value(value)
            note = "src/groundtruth_kb/"
        elif name == "docstring_coverage_percent":
            display_name = "Docstring coverage"
            value_str = _format_percent(value)
            note = "public API only, per `scripts/audit_docstrings.py`"
        else:
            display_name = name
            value_str = _format_value(value)
            note = m.get("source_scope", "")
        footnote_label = f"gate{idx}"
        gate_rows.append(f"| {display_name} | {value_str}[^{footnote_label}] | {note} |")
        scope_text = m["source_scope"].rstrip(".")
        gate_footnotes.append(
            f"[^{footnote_label}]: `{m['command']}` — commit `{m['commit_sha']}` — generated {m['timestamp_utc']}. "
            f"Scope: {scope_text}."
        )

    # Build live-snapshot section.
    live_rows: list[str] = []
    live_footnotes: list[str] = []
    for idx, m in enumerate(live_snapshot, start=1):
        name = m["metric_name"]
        value = m["value"]
        if name == "specs_specified":
            display_name = "Specs (specified)"
            note = "count at last `scripts/collect_evidence_metrics.py` run"
        elif name == "specs_verified":
            display_name = "Specs (verified)"
            note = "count at last `scripts/collect_evidence_metrics.py` run"
        elif name == "deliberations_total":
            display_name = "Deliberations (local archive)"
            note = "count at last `scripts/collect_evidence_metrics.py` run. Reference install only, not Agent Red."
        else:
            display_name = name
            note = m.get("source_scope", "")
        footnote_label = f"live{idx}"
        live_rows.append(f"| {display_name} | {_format_value(value)}[^{footnote_label}] | {note} |")
        repro = m.get("reproducibility", "local_install_snapshot")
        scope_text = m["source_scope"]
        if not scope_text.endswith("."):
            scope_text = scope_text + "."
        live_footnotes.append(
            f"[^{footnote_label}]: `{m['command']}` — commit `{m['commit_sha']}` — generated {m['timestamp_utc']}. "
            f"Scope: {scope_text} Reproducibility: `{repro}` — **this value will differ on a fresh "
            f"`gt project init` and is NOT compared by `--verify`**."
        )

    gate_table = "\n".join(gate_rows) if gate_rows else "| (no gate-bound metrics) | — | — |"
    live_table = "\n".join(live_rows) if live_rows else "| (no live-snapshot metrics) | — | — |"
    gate_footer = "\n".join(gate_footnotes)
    live_footer = "\n".join(live_footnotes)

    md = f"""# Evidence

This page documents **live metrics from the reference implementation**.
Every row carries a generating command, a commit SHA, and a generation date
as a footnote. Numbers without provenance are forbidden on this page.

!!! note "This page is generated"
    `docs/evidence.md` is rendered from `docs/_generated/evidence_metrics.json`
    by `scripts/render_evidence_md.py`. Do not hand-edit this file.
    Edit the JSON via `python scripts/collect_evidence_metrics.py`, then
    regenerate this page via `python scripts/render_evidence_md.py`.

!!! note "Reading this page"
    A single snapshot is not a trend. The metrics below answer the
    question: "at commit X, on a fresh install, what is true?" They do
    not answer "how fast is this moving?" That is what session wrap-up
    reports are for.

## Machine-Verifiable Metrics (reproducible at commit `{commit}`)

These metrics are deterministic at a fixed commit. `scripts/collect_evidence_metrics.py --verify`
compares each row's `metric_name`, `value`, `command`, `source_scope`, and
`nondeterminism` classification against the committed JSON, and fails on any
mismatch. `commit_sha` and `timestamp_utc` are re-stamped on every run and are
NOT compared against the fresh run (they would diverge by design), but the
committed JSON's `commit_sha` must equal the top-level `generated_at_commit`
and that value is surfaced in the section heading above.

| Metric | Value | Notes |
|--------|-------|-------|
{gate_table}

{gate_footer}

## Live Reference-Install Snapshot (local dev DB, regenerated on every run)

These metrics are pulled from the gitignored local `groundtruth.db`. They
are informative, not gate-bound: a fresh `gt project init` creates an empty
database, so these values will differ on any other machine. They are
regenerated on every `scripts/collect_evidence_metrics.py` run, but
`--verify` does NOT compare them.

| Metric | Value | Notes |
|--------|-------|-------|
{live_table}

{live_footer}

## Deterministic vs. Non-Deterministic Metrics

Every machine-verifiable metric above is classified as **deterministic**:
at a fixed commit, running the generating command twice returns the same
value. No tolerance is applied. Evidence drift is surfaced by
`scripts/collect_evidence_metrics.py --verify` as an exact mismatch.

Live-snapshot metrics are **reproducibility: local_install_snapshot** — a
deterministic query against a non-deterministic database. They carry full
provenance but are explicitly excluded from the fail-closed gate.

If a future metric is introduced that is genuinely non-deterministic (for
example, timing-based measurements), it must declare the nondeterminism
source and the allowed tolerance in both the collector code and this page.
A vague "+/-1 for test-collection noise" is not an acceptable contract;
deterministic metrics get exact equality.

## Curated Context

Some evidence cannot be auto-collected from a single commit. These
sections are curated from session wrap-up reports and bridge threads:

### Bridge Round-Trip Cycle Times (reference project)

From recent VERIFIED bridge threads on Agent Red:

- `gtkb-start-here-adopter-rewrite-implementation` scope review cycle:
  proposal -> Codex GO in under 30 minutes on 2026-04-17.
- `gtkb-non-disruptive-upgrade-investigation-006` VERIFIED:
  scope draft -> Codex GO -> 1023-line investigation report -> VERIFIED in
  a single session (S299-continuation).
- `gtkb-phase-a-metrics-collector-004` VERIFIED: headless Claude thread
  implementation (pid-spawned) -> Codex verification in ~13 minutes total
  round-trip.

These are **representative samples from the Agent Red reference project**,
not claims about what every adopter project will achieve. An adopter's
cycle time depends on Codex availability, proposal complexity, and
whether the proposal needs one revision or several.

### Phase A Shipping Summary (reference project)

As of 2026-04-17, the Agent Red reference project has completed the
GT-KB Operational Skills Tier A Phase A workstream. Six implementation
bridges VERIFIED, 14 commits from v0.5.0 to v0.6.0, wheel shipped to
PyPI.

This is curated, not auto-collected. It ages the moment the next release
ships; the bridge index and KB are the authoritative sources.

## How to Regenerate This Page

```powershell
cd groundtruth-kb
python scripts/collect_evidence_metrics.py
python scripts/render_evidence_md.py
```

The collector rewrites `docs/_generated/evidence_metrics.json` (both
gate-bound and live-snapshot sections). The renderer then rewrites this
page from the JSON.

To verify the stored JSON matches the current state of the repo AND that
the rendered markdown matches the committed markdown:

```powershell
python scripts/collect_evidence_metrics.py --verify
```

Exit code 0 means the stored gate-bound metrics match the fresh collection
*and* `docs/evidence.md` is byte-identical to a fresh render from the
committed JSON. Exit code 1 means drift was detected; the offending rows
or markdown lines are printed.

---

*Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

*Generated from `docs/_generated/evidence_metrics.json` at commit `{commit}` on {timestamp}.*
"""
    return md


def load_json(path: Path = JSON_PATH) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"{path.relative_to(REPO_ROOT)} does not exist. Run collect_evidence_metrics.py first.")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path.relative_to(REPO_ROOT)} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{path.relative_to(REPO_ROOT)} must contain a JSON object at the top level.")
    return data


def write_markdown(content: str, output_path: Path = DEFAULT_OUTPUT_PATH) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--to",
        type=Path,
        default=None,
        help="Write rendered markdown to this path instead of docs/evidence.md.",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=JSON_PATH,
        help="Path to evidence_metrics.json (default: docs/_generated/evidence_metrics.json).",
    )
    args = parser.parse_args()

    try:
        data = load_json(args.json)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    try:
        md = render(data)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    output_path = args.to if args.to is not None else DEFAULT_OUTPUT_PATH
    write_markdown(md, output_path)
    try:
        rel = output_path.relative_to(REPO_ROOT)
    except ValueError:
        rel = output_path
    print(f"Wrote {len(md.splitlines())} lines to {rel}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
