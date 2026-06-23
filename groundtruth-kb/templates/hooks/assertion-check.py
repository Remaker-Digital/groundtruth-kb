#!/usr/bin/env python3
"""
Claude Code SessionStart hook — Knowledge Database assertion check + quality dashboard + session handoff.

Three responsibilities:
1. Run feature assertions and return a summary (regression guard).
2. Display a 4-metric quality dashboard (SPEC-1659/SPEC-1660).
3. Read the latest unconsumed session handoff prompt and inject it as
   context so the new session knows exactly where the previous one left off.

Stdin:  JSON (SessionStart payload)
Stdout: JSON {"additionalContext": "..."} or {}
Exit:   Always 0

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import contextlib
import json
import os
import sys
from pathlib import Path

PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
KB_DIR = PROJECT_DIR / "tools" / "knowledge-db"
AGENTS_FILE = PROJECT_DIR / "AGENTS.md"
LOYAL_OPPOSITION_SENTINEL = "This project is in Loyal Opposition mode until the owner revokes it."


def _env_flag(name: str) -> bool | None:
    """Parse an environment flag as a boolean when explicitly set."""
    value = os.environ.get(name)
    if value is None:
        return None

    value = value.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    return None


def _workspace_loyal_opposition_mode() -> bool:
    """Infer review mode from the tracked workspace contract when flags are unset."""
    try:
        return LOYAL_OPPOSITION_SENTINEL in AGENTS_FILE.read_text(encoding="utf-8")
    except OSError:
        return False


def _review_readonly_mode() -> bool:
    """Return True when the session should avoid mutating state."""
    for name in ("LOYAL_OPPOSITION_READONLY", "CODEX_REVIEW_MODE"):
        parsed = _env_flag(name)
        if parsed is not None:
            return parsed
    return _workspace_loyal_opposition_mode()


def _run_assertions(db) -> list[str]:
    """Run assertions and return context lines.

    Differentiates between expected failures (specified — not yet implemented)
    and regressions (implemented/verified — should be passing).
    """
    try:
        from assertions import run_all_assertions

        summary = run_all_assertions(db, triggered_by="session-start")
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        total = summary.get("specs_with_assertions", 0)

        lines = [f"Knowledge DB assertion check: {passed}/{total} PASS, {failed} FAIL"]

        failures = [d for d in summary.get("details", []) if not d.get("skipped") and not d["overall_passed"]]
        if failures:
            # Look up actual spec status to classify failures correctly
            regressions = []
            expected = []
            for f in failures:
                spec = db.get_spec(f["spec_id"])
                status = spec["status"] if spec else "unknown"
                if status in ("implemented", "verified"):
                    regressions.append((f, status))
                else:
                    expected.append((f, status))

            if regressions:
                lines.append("REGRESSIONS (implemented/verified specs now failing):")
                for f, status in regressions:
                    lines.append(f"  [{f['spec_id']}] ({status}) {f['title']}")
                lines.append("  ^^^ These require investigation before proceeding.")

            if expected:
                lines.append("Expected failures (specified — not yet implemented):")
                for f, status in expected:
                    lines.append(f"  [{f['spec_id']}] ({status}) {f['title']}")

        return lines
    except Exception as e:
        import traceback

        traceback.print_exc(file=sys.stderr)
        return [f"Assertion check error: {e}"]


def _check_transport_governance(db) -> list[str]:
    """Phase 0 transport governance scan — detect phantom evidence.

    Checks transport-gated specs for:
    - Tests marked 'pass' with NULL test_file
    - Tests marked 'pass' with test_file that doesn't exist on disk
    - Specs marked 'verified' with non-executable linked tests
    """
    try:
        from db import _TRANSPORT_GATED_SPECS, _resolve_test_file
    except ImportError:
        return ["Transport governance check: could not import _TRANSPORT_GATED_SPECS"]

    violations = []
    conn = db._get_conn()

    # Check 1: transport tests with pass but no/bogus test_file
    for spec_id in sorted(_TRANSPORT_GATED_SPECS):
        rows = conn.execute(
            "SELECT id, last_result, test_file FROM current_tests WHERE spec_id = ?",
            (spec_id,),
        ).fetchall()
        for row in rows:
            if row["last_result"] == "pass":
                if not row["test_file"]:
                    violations.append(
                        f"  PHANTOM: {row['id']} (linked to {spec_id}) has last_result='pass' but test_file=NULL"
                    )
                elif not _resolve_test_file(row["test_file"]):
                    violations.append(
                        f"  BOGUS: {row['id']} (linked to {spec_id}) has "
                        f"last_result='pass' but test_file='{row['test_file']}' does not exist"
                    )

    # Check 2: transport specs marked verified without full evidence
    for spec_id in sorted(_TRANSPORT_GATED_SPECS):
        spec = db.get_spec(spec_id)
        if spec and spec["status"] == "verified":
            tests = conn.execute(
                "SELECT id, test_file, last_result FROM current_tests WHERE spec_id = ?",
                (spec_id,),
            ).fetchall()
            bad = [
                r["id"]
                for r in tests
                if not r["test_file"] or not _resolve_test_file(r["test_file"]) or r["last_result"] != "pass"
            ]
            if bad or not tests:
                violations.append(
                    f"  UNVERIFIED: {spec_id} is 'verified' but lacks executable evidence "
                    f"(bad tests: {bad or 'none linked'})"
                )

    if violations:
        return [
            f"TRANSPORT GOVERNANCE VIOLATIONS ({len(violations)}):",
            *violations,
            "  ^^^ Phase 0 gate — fix before re-promoting transport specs.",
        ]
    return ["Transport governance check: 0 violations"]


def _check_untested_work_items(db) -> list[str]:
    """Check open work items for linked tests (GOV-12 / SPEC-1601 drift detection)."""
    try:
        all_wis = db.get_open_work_items()
        # Filter to truly open items (not resolved/verified/retired)
        open_wis = [wi for wi in all_wis if wi.get("resolution_status") not in ("resolved", "verified", "retired")]
        if not open_wis:
            return []

        untested = []
        for wi in open_wis:
            spec_id = wi.get("source_spec_id")
            if not spec_id:
                untested.append((wi["id"], wi["title"], "no source_spec_id"))
                continue
            tests = db.get_tests_for_spec(spec_id)
            if not tests:
                untested.append((wi["id"], wi["title"], f"spec {spec_id} has no tests"))

        if not untested:
            return [f"GOV-12 drift check: {len(open_wis)} open WIs, all have linked tests"]

        lines = [f"GOV-12 DRIFT WARNING: {len(untested)}/{len(open_wis)} open WIs missing linked tests:"]
        for wi_id, title, reason in untested:
            lines.append(f"  [{wi_id}] {title} ({reason})")
        lines.append("  ^^^ Create tests for these WIs before implementation (GOV-12).")
        return lines
    except Exception as e:
        return [f"GOV-12 drift check error: {e}"]


def _check_dcl_compliance(db) -> list[str]:
    """Check design constraint compliance at session start (GOV-20 advisory pilot)."""
    try:
        results = db.validate_dcl_constraints()
        if not results:
            return ["GOV-20 DCL check: no design constraints with assertions found"]

        passed = sum(1 for r in results if r["passed"])
        failed = [r for r in results if not r["passed"]]
        lines = [f"GOV-20 DCL compliance: {passed}/{len(results)} constraints passing"]

        if failed:
            lines.append("DCL VIOLATIONS (advisory):")
            for f in failed:
                lines.append(f"  [{f['dcl_id']}] {f['title']}")
                for r in f["results"]:
                    if not r.get("passed") and not r.get("skipped"):
                        lines.append(f"    FAIL: {r.get('description', '')}: {r.get('detail', '')}")

        return lines
    except Exception as e:
        return [f"GOV-20 DCL check error: {e}"]


def _quality_dashboard(db) -> list[str]:
    """Generate 6-metric quality dashboard with composite score (SPEC-1838/WI-1465).

    Metrics (SPEC-1838 weighted composite):
      1. Assertion Coverage  — specs with ≥1 non-stale test / implementable specs (weight 0.25)
      2. Assertion Strength  — specs with machine-verifiable assertions (weight 0.20)
      3. Test Freshness     — tests with pass/fail vs total non-stale (weight 0.20)
      4. Defect Escape Rate — open defects / total defects (weight 0.15)
      5. Change Failure Rate — regressions / total WIs (weight 0.10)
      6. Coverage Delta     — line coverage trend (weight 0.10)
    """
    try:
        conn = db._get_conn()
        summary = db.get_summary()

        # Try to use the quality_metrics module for accurate composite score
        composite_score = None
        metric_values = {}
        try:
            sys.path.insert(0, str(KB_DIR))
            from quality_score_helper import compute_dashboard_metrics

            metric_values, composite_score = compute_dashboard_metrics(db)
        except ImportError:
            pass

        # Fallback: compute metrics directly from DB
        if not metric_values:
            # --- Metric 1: Assertion Coverage (SPEC-1659) ---
            total_specs = summary.get("spec_total", 0)
            specs_with_assertions = summary.get("assertions_total", 0)
            spec_cov = (specs_with_assertions / total_specs) if total_specs else 0
            metric_values["assertion_coverage"] = spec_cov

            # --- Metric 2: Assertion Strength ---
            # Exclude governance artifact types (GOV-20): they have different test expectations
            row = conn.execute(
                """SELECT COUNT(*) AS total,
                          SUM(
                              CASE WHEN assertions IS NOT NULL AND assertions != 'null' THEN 1 ELSE 0 END
                          ) AS with_assertions
                   FROM current_specifications
                   WHERE status IN ('implemented', 'verified')
                     AND COALESCE(type, 'requirement') NOT IN
                         ('architecture_decision', 'design_constraint', 'governance', 'protected_behavior')"""
            ).fetchone()
            impl_total = row["total"] or 0
            with_assert = row["with_assertions"] or 0
            metric_values["assertion_strength"] = (with_assert / impl_total) if impl_total else 0

            # --- Metric 3: Test Freshness ---
            trace_row = conn.execute(
                """SELECT COUNT(*) AS total,
                          SUM(CASE WHEN last_result IN ('pass', 'fail') THEN 1 ELSE 0 END) AS fresh
                   FROM current_tests WHERE last_result != 'stale' OR last_result IS NULL"""
            ).fetchone()
            total_tests = trace_row["total"] or 0
            fresh_tests = trace_row["fresh"] or 0
            metric_values["test_freshness"] = (fresh_tests / total_tests) if total_tests else 0

            # --- Metric 4: Defect Escape Rate ---
            defect_wis = db.list_work_items(origin="defect")
            total_defects = len(defect_wis)
            open_defects = sum(1 for d in defect_wis if d.get("resolution_status") in ("open", "created", "specified"))
            metric_values["defect_escape_rate"] = (open_defects / total_defects) if total_defects else 0

            # --- Metric 5: Change Failure Rate ---
            regression_row = conn.execute(
                """SELECT COUNT(*) AS total,
                          SUM(CASE WHEN origin = 'regression' THEN 1 ELSE 0 END) AS regressions
                   FROM current_work_items"""
            ).fetchone()
            total_wis = regression_row["total"] or 0
            regressions = regression_row["regressions"] or 0
            metric_values["change_failure_rate"] = (regressions / total_wis) if total_wis else 0

            # --- Metric 6: Coverage Delta ---
            metric_values["coverage_delta"] = 0.5  # Neutral when no data

            # Compute composite
            weights = {
                "assertion_coverage": 0.25,
                "assertion_strength": 0.20,
                "test_freshness": 0.20,
                "defect_escape_rate": 0.15,
                "change_failure_rate": 0.10,
                "coverage_delta": 0.10,
            }
            composite_score = sum(
                (1.0 - metric_values[k] if k in ("defect_escape_rate", "change_failure_rate") else metric_values[k])
                * weights[k]
                * 100
                for k in weights
            )

        # --- Read previous composite for trend arrow ---
        prev_score = None
        try:
            prev_row = conn.execute(
                """SELECT composite_score FROM quality_scores
                   ORDER BY recorded_at DESC LIMIT 1 OFFSET 1"""
            ).fetchone()
            if prev_row:
                prev_score = prev_row[0]
        except Exception:
            pass

        trend = ""
        if prev_score is not None and composite_score is not None:
            delta = composite_score - prev_score
            if delta > 1.0:
                trend = " \u2191"  # ↑
            elif delta < -1.0:
                trend = " \u2193"  # ↓
            else:
                trend = " \u2192"  # →

        def _icon(val, good_threshold, warn_threshold, invert=False):
            if invert:
                val = 1.0 - val
            if val >= good_threshold:
                return "\u2705"
            elif val >= warn_threshold:
                return "\u26a0\ufe0f"
            return "\U0001f534"

        # --- Format dashboard ---
        sc = metric_values.get("assertion_coverage", 0)
        ass = metric_values.get("assertion_strength", 0)
        tf = metric_values.get("test_freshness", 0)
        der = metric_values.get("defect_escape_rate", 0)
        cfr = metric_values.get("change_failure_rate", 0)
        cd = metric_values.get("coverage_delta", 0.5)

        cs = composite_score or 0

        lines = [
            "",
            "\u250c\u2500 Quality Dashboard (SPEC-1838) "
            "\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500"
            "\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510",
            f"\u2502  Composite Score: {cs:.1f}/100{trend}",
            f"\u2502 {_icon(sc, 0.6, 0.3)} Assertion Coverage:  {sc:.1%} \u2014 target \u226560%",
            f"\u2502 {_icon(ass, 0.5, 0.25)} Assertion Strength:  {ass:.1%} \u2014 target \u226550%",
            f"\u2502 {_icon(tf, 0.8, 0.5)} Test Freshness:      {tf:.1%} \u2014 target >80%",
            f"\u2502 {_icon(der, 0.8, 0.5, invert=True)} Defect Escape Rate:  {der:.1%} \u2014 target <20%",
            f"\u2502 {_icon(cfr, 0.9, 0.7, invert=True)} Change Failure Rate: {cfr:.1%} \u2014 target <10%",
            f"\u2502 {_icon(cd, 0.5, 0.3)} Coverage Delta:      {cd:.1%}",
            "\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500"
            "\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500"
            "\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500"
            "\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500"
            "\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518",
        ]

        return lines
    except Exception as e:
        import traceback

        traceback.print_exc(file=sys.stderr)
        return [f"Quality dashboard error: {e}"]


def _untested_spec_report(db) -> list[str]:
    """Report implemented/verified specs with 0 tests (WI-1472).

    Helps identify high-risk gaps in test coverage at session start.
    """
    try:
        conn = db._get_conn()
        # Exclude governance artifact types (GOV-20): ADR/DCL/GOV/PB have different test expectations
        rows = conn.execute(
            """SELECT s.id, s.title, s.status FROM current_specifications s
               WHERE s.status IN ('implemented', 'verified')
                 AND COALESCE(s.type, 'requirement') NOT IN
                     ('architecture_decision', 'design_constraint', 'governance', 'protected_behavior')
                 AND NOT EXISTS (
                     SELECT 1 FROM current_tests t
                     WHERE t.spec_id = s.id AND t.last_result != 'stale'
                 )
               ORDER BY s.id"""
        ).fetchall()

        if not rows:
            return ["Untested spec check: all implemented/verified specs have tests"]

        lines = [f"UNTESTED SPECS: {len(rows)} implemented/verified specs with 0 non-stale tests:"]
        # Show top 5 highest-risk (most recent IDs first = newest specs)
        for row in rows[-5:]:
            lines.append(f"  [{row['id']}] ({row['status']}) {row['title'][:60]}")
        if len(rows) > 5:
            lines.append(f"  ... and {len(rows) - 5} more. Run /kb-query untested for full list.")

        return lines
    except Exception as e:
        return [f"Untested spec report error: {e}"]


def _read_handoff_prompt(db, consume: bool = True) -> list[str]:
    """Read the latest session handoff prompt and optionally consume it."""
    try:
        prompt = db.get_next_session_prompt()
        if not prompt:
            return []

        session_id = prompt["session_id"]
        prompt_text = prompt["prompt_text"]

        # Parse context — try parsed first, fall back to raw JSON
        context_data = prompt.get("_context_parsed") or {}
        if not context_data and prompt.get("context"):
            try:
                import json as _json

                context_data = _json.loads(prompt["context"])
            except (ValueError, TypeError):
                context_data = {}

        lines = [
            "",
            "=" * 60,
            f"  SESSION HANDOFF from {session_id}",
            "=" * 60,
        ]

        # Add structured context summary if available
        if context_data:
            if context_data.get("production_version"):
                lines.append(f"  Production: v{context_data['production_version']}")
            if context_data.get("test_count") is not None:
                tc = context_data["test_count"]
                tf = context_data.get("test_failures", 0)
                lines.append(f"  Tests: {tc} passed, {tf} failed")
            if context_data.get("wis_implemented"):
                lines.append(f"  WIs implemented: {', '.join(str(w) for w in context_data['wis_implemented'])}")
            if context_data.get("next_tasks"):
                lines.append("  Next tasks:")
                for task in context_data["next_tasks"]:
                    lines.append(f"    - {task}")

        lines.append("-" * 60)
        lines.append(prompt_text)
        lines.append("=" * 60)

        if consume:
            # Mark as consumed so the next session doesn't see it again
            db.consume_session_prompt(session_id)
        else:
            lines.append("  [review-mode] Session handoff left unconsumed")

        return lines
    except Exception as e:
        import traceback

        traceback.print_exc(file=sys.stderr)
        return [f"Session handoff read error: {e}"]


def _read_retention_cap(project_dir: Path) -> tuple[int, list[str]]:
    """Resolve the per-spec assertion_runs retention cap.

    Reads `config/governance/assertion-runs-retention.toml` (per Slice 4 IP-3).
    Default is 50 so SPEC-1662's chronic-noise classification threshold is
    reachable. Returns `(cap, log_lines)` where log_lines surfaces fallback
    diagnostics when the config is missing or malformed.
    """
    config_path = project_dir / "config" / "governance" / "assertion-runs-retention.toml"
    if not config_path.is_file():
        return 50, []
    try:
        import tomllib

        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return 50, [f"assertion-runs-retention config fallback to default 50: {exc}"]
    cap = data.get("default_runs_per_spec", 50)
    if not isinstance(cap, int) or cap <= 0:
        return 50, ["assertion-runs-retention default_runs_per_spec invalid; fallback to 50"]
    return cap, []


def _prune_assertion_runs(db) -> list[str]:
    """Prune old assertion_runs to keep DB size manageable.

    Reads the retention cap from `config/governance/assertion-runs-retention.toml`
    (default 50, the SPEC-1662 chronic-noise threshold). Each session generates
    ~1,874 assertion rows; without pruning, the table grows unboundedly. Keeping
    the configured cap per spec_id preserves enough history for trend analysis
    plus the chronic-noise classification window per SPEC-1662 (GOV-18).
    """
    cap, log_lines = _read_retention_cap(PROJECT_DIR)
    try:
        conn = db._get_conn()
        before = conn.execute("SELECT COUNT(*) FROM assertion_runs").fetchone()[0]

        # Delete all but the latest `cap` runs per spec
        conn.execute(
            """
            DELETE FROM assertion_runs
            WHERE rowid NOT IN (
                SELECT rowid FROM (
                    SELECT rowid, ROW_NUMBER() OVER (
                        PARTITION BY spec_id ORDER BY run_at DESC
                    ) AS rn
                    FROM assertion_runs
                ) WHERE rn <= ?
            )
            """,
            (cap,),
        )
        conn.commit()

        after = conn.execute("SELECT COUNT(*) FROM assertion_runs").fetchone()[0]
        pruned = before - after
        lines = list(log_lines)
        if pruned > 0:
            lines.append(f"Assertion runs pruned: {before} -> {after} ({pruned} old runs removed; cap={cap})")
        return lines
    except Exception as e:
        return [f"Assertion pruning error: {e}"]


def _check_assertion_triage_advisory() -> list[str]:
    """Surface latest assertion-triage categorization counts as advisory.

    Reads `.gtkb-state/assertion-triage/<run_id>/summary.json` for the most
    recent categorization run produced by `scripts/assertion_categorize.py`
    (Slice 3 IP-1) and emits a non-blocking summary of per-category counts.

    The check is read-only: no KB writes, no AUQ trigger, no state mutation.
    Returns an empty list when no run has occurred yet so first-session use
    surfaces no surprises.
    """
    triage_dir = PROJECT_DIR / ".gtkb-state" / "assertion-triage"
    if not triage_dir.is_dir():
        return []
    run_dirs = sorted(
        [d for d in triage_dir.iterdir() if d.is_dir() and d.name != "categories"],
        reverse=True,
    )
    if not run_dirs:
        return []
    summary_path = run_dirs[0] / "summary.json"
    if not summary_path.is_file():
        return []
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    counts = summary.get("counts_by_category", {}) or {}
    examined = summary.get("total_assertions_examined", 0)
    failing = summary.get("currently_failing", 0)
    run_id = summary.get("run_id", run_dirs[0].name)
    lines = [
        "",
        f"Assertion triage advisory (run {run_id}; {examined} examined, {failing} currently failing):",
        f"  genuine_drift:  {counts.get('genuine_drift', 0)}",
        f"  chronic_noise:  {counts.get('chronic_noise', 0)}",
        f"  flaky:          {counts.get('flaky', 0)}",
        f"  healthy:        {counts.get('healthy', 0)}",
        f"  uncategorized:  {counts.get('uncategorized', 0)}",
    ]
    if counts.get("genuine_drift", 0) > 0:
        lines.append("  ^ genuine_drift entries are highest-priority for review.")
    if counts.get("chronic_noise", 0) > 0:
        lines.append(
            "  ^ review chronic_noise candidates via "
            "`python scripts/assertion_retirement_workflow.py review-candidates`"
        )
    return lines


def main():
    # Consume stdin (required by hook protocol)
    with contextlib.suppress(json.JSONDecodeError, EOFError):
        json.loads(sys.stdin.read())

    # Check if knowledge database exists
    db_path = PROJECT_DIR / "groundtruth.db"
    if not db_path.exists():
        json.dump({}, sys.stdout)
        sys.exit(0)

    # Import DB
    sys.path.insert(0, str(KB_DIR))
    try:
        from db import KnowledgeDB

        readonly_review = _review_readonly_mode()
        db = KnowledgeDB(str(db_path))
        try:
            if readonly_review:
                # Review mode: truly non-mutating — no assertion writes,
                # no pruning, no handoff consumption. Read-only checks only.
                lines = ["Review read-only mode: skipping assertion execution (no KB writes)"]
                lines.extend(_check_untested_work_items(db))
                lines.extend(_check_transport_governance(db))
                lines.extend(_check_dcl_compliance(db))
                lines.extend(_untested_spec_report(db))
                lines.extend(_quality_dashboard(db))
                lines.extend(_check_assertion_triage_advisory())
                lines.extend(_read_handoff_prompt(db, consume=False))
            else:
                lines = _run_assertions(db)
                lines.extend(_check_untested_work_items(db))
                lines.extend(_check_transport_governance(db))
                lines.extend(_check_dcl_compliance(db))
                lines.extend(_untested_spec_report(db))
                lines.extend(_quality_dashboard(db))
                lines.extend(_check_assertion_triage_advisory())
                lines.extend(_prune_assertion_runs(db))
                lines.extend(_read_handoff_prompt(db, consume=True))
        finally:
            db.close()

        context = "\n".join(lines)
        json.dump({"additionalContext": context}, sys.stdout)

    except Exception as e:
        import traceback

        traceback.print_exc(file=sys.stderr)
        json.dump({"additionalContext": f"SessionStart hook error: {e}"}, sys.stdout)

    sys.exit(0)


if __name__ == "__main__":
    main()
