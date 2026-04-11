"""Live quality evaluation runner — executes 25 golden scenarios against production.

Connects to the production chat API via SSE to collect full AI responses,
then scores them using the quality pilot heuristic framework.

Usage:
    python evaluation/run_quality_live.py

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import os
import time
from datetime import datetime

import requests

PROD_URL = os.getenv("QUALITY_PROD_URL")
if not PROD_URL:
    raise RuntimeError("QUALITY_PROD_URL environment variable is required")
WIDGET_KEY = os.getenv("PREVIEW_WIDGET_KEY")
if not WIDGET_KEY:
    raise RuntimeError("PREVIEW_WIDGET_KEY environment variable is required")
RESULTS_DIR = "evaluation/results"
DATASET_PATH = "evaluation/datasets/response_quality.json"


def run_scenario(scenario: dict) -> dict:
    """Execute a single scenario against production and collect response."""
    sid = scenario["id"]
    msg = scenario["customer_message"]

    start_time = time.time()

    # Start conversation
    conv_r = requests.post(
        f"{PROD_URL}/api/chat/conversations",
        headers={"X-Widget-Key": WIDGET_KEY, "Content-Type": "application/json"},
        json={
            "visitor": {
                "name": f"QualityTest-{sid}",
                "email": f"quality-test-{sid}@example.com",
            },
            "page_url": "https://quality-test.com",
            "initial_message": msg,
        },
        timeout=15,
    )

    if conv_r.status_code != 201:
        return {
            "response": "",
            "escalation": False,
            "critic_verdict": "approved",
            "error": f"start:{conv_r.status_code}",
            "response_time_ms": int((time.time() - start_time) * 1000),
        }

    conv_data = conv_r.json()
    conv_id = conv_data["conversation_id"]
    stream_url = conv_data.get("stream_url", "")

    # Collect response via SSE stream
    ai_response = ""
    escalation = False
    critic_passed = True

    try:
        sse_r = requests.get(
            f"{PROD_URL}{stream_url}",
            headers={"X-Widget-Key": WIDGET_KEY, "Accept": "text/event-stream"},
            stream=True,
            timeout=20,
        )

        done = False
        for chunk in sse_r.iter_lines(decode_unicode=True):
            if not chunk or not chunk.startswith("data:"):
                continue
            try:
                event_data = json.loads(chunk[5:].strip())
                if "text" in event_data:
                    ai_response += event_data["text"]
                if event_data.get("escalated") or event_data.get("type") == "escalated":
                    escalation = True
                if "critic_passed" in event_data:
                    critic_passed = event_data["critic_passed"]
                if "turn_count" in event_data and "conversation_id" in event_data:
                    done = True
                    break
            except json.JSONDecodeError:
                pass
        if not done:
            sse_r.close()
    except requests.exceptions.ReadTimeout:
        pass

    elapsed_ms = int((time.time() - start_time) * 1000)

    # Fallback: if no response from SSE, try conversation state
    if not ai_response:
        time.sleep(2)
        state_r = requests.get(
            f"{PROD_URL}/api/chat/conversations/{conv_id}",
            headers={"X-Widget-Key": WIDGET_KEY},
            timeout=15,
        )
        if state_r.status_code == 200:
            state_data = state_r.json()
            for m in state_data.get("messages", []):
                if m.get("role") in ("ai", "assistant", "agent"):
                    ai_response = m.get("content", m.get("text", ""))
                if state_data.get("status") == "escalated":
                    escalation = True
            elapsed_ms = int((time.time() - start_time) * 1000)

    return {
        "response": ai_response,
        "escalation": escalation,
        "critic_verdict": "approved" if critic_passed else "rejected",
        "response_time_ms": elapsed_ms,
    }


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    with open(DATASET_PATH, encoding="utf-8") as f:
        data = json.load(f)
    scenarios = data["scenarios"]

    print("=== Conversation Quality Test Run ===")
    print(f"Date: {datetime.now().isoformat()[:19]}")
    print(f"Target: {PROD_URL}")
    print(f"Scenarios: {len(scenarios)}")
    print()

    responses = {}
    pipeline_errors = 0
    timing_data = {}

    for i, scenario in enumerate(scenarios):
        sid = scenario["id"]
        cat = scenario["category"]
        print(f"[{i + 1:2d}/25] {sid} [{cat:20s}]", end=" ", flush=True)

        result = run_scenario(scenario)
        responses[sid] = result
        timing_data[sid] = result["response_time_ms"]

        if result.get("error"):
            print(f"FAIL ({result['error']})")
            pipeline_errors += 1
        elif result["response"]:
            resp_preview = result["response"][:60].replace("\n", " ")
            print(f'OK  {result["response_time_ms"]:5d}ms  {len(result["response"]):4d}ch  "{resp_preview}..."')
        else:
            print(f"NO_RESPONSE  {result['response_time_ms']}ms")

    # Save raw responses
    raw_path = os.path.join(RESULTS_DIR, f"quality-raw-{datetime.now().strftime('%Y-%m-%d')}.json")
    with open(raw_path, "w") as f:
        json.dump({"responses": responses, "pipeline_errors": pipeline_errors, "timing": timing_data}, f, indent=2)

    resp_count = sum(1 for r in responses.values() if r.get("response"))
    avg_time = int(sum(timing_data.values()) / len(timing_data)) if timing_data else 0
    max_time = max(timing_data.values()) if timing_data else 0

    print("\n--- Summary ---")
    print(f"Pipeline errors: {pipeline_errors}/{len(scenarios)}")
    print(f"Responses collected: {resp_count}/{len(scenarios)}")
    print(f"Avg response time: {avg_time}ms")
    print(f"Max response time: {max_time}ms")

    # Run quality pilot scoring
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from evaluation.pilots.quality_pilot import run_pilot

    report = run_pilot(responses)

    print("\n=== Quality Pilot Report ===")
    print(
        f"Total: {report.total_scenarios} | Passed: {report.passed_scenarios} | Failed: {report.failed_scenarios} | Rate: {report.pass_rate:.1f}%"
    )
    print("\nScores (1-5, thresholds: F>=3.5, R>=3.5, T>=3.0, O>=3.5):")
    f_ok = "PASS" if report.avg_faithfulness >= 3.5 else "FAIL"
    r_ok = "PASS" if report.avg_relevancy >= 3.5 else "FAIL"
    t_ok = "PASS" if report.avg_tone >= 3.0 else "FAIL"
    o_ok = "PASS" if report.avg_overall >= 3.5 else "FAIL"
    print(f"  Faithfulness: {report.avg_faithfulness:.2f} [{f_ok}]")
    print(f"  Relevancy:    {report.avg_relevancy:.2f} [{r_ok}]")
    print(f"  Tone:         {report.avg_tone:.2f} [{t_ok}]")
    print(f"  Overall:      {report.avg_overall:.2f} [{o_ok}]")

    contains_rate = sum(1 for r in report.results if r.contains_pass) / len(report.results) * 100
    excludes_rate = sum(1 for r in report.results if r.excludes_pass) / len(report.results) * 100
    esc_acc = sum(1 for r in report.results if r.escalation_correct) / len(report.results) * 100
    print("\nPass Rates:")
    print(f"  Contains:   {contains_rate:.0f}% ({'PASS' if contains_rate >= 80 else 'FAIL'}, >=80%)")
    print(f"  Excludes:   {excludes_rate:.0f}% ({'PASS' if excludes_rate >= 90 else 'FAIL'}, >=90%)")
    print(f"  Escalation: {esc_acc:.0f}% ({'PASS' if esc_acc >= 90 else 'FAIL'}, >=90%)")

    print("\nBy Category:")
    for cat, score in sorted(report.category_scores.items()):
        print(f"  {cat:20s}: {score:.2f}")

    print("\nBy Difficulty:")
    for diff, score in sorted(report.difficulty_scores.items()):
        print(f"  {diff:10s}: {score:.2f}")

    failing = [r for r in report.results if not r.passed]
    if failing:
        print(f"\nFailing Scenarios ({len(failing)}):")
        for r in failing:
            print(
                f"  {r.scenario_id} [{r.category}/{r.difficulty}] F={r.faithfulness_score:.1f} R={r.relevancy_score:.1f} T={r.tone_score:.1f} O={r.overall_score:.1f}"
            )
            for issue in r.issues[:3]:
                print(f"    - {issue}")

    # Verdict
    below_2 = [r for r in report.results if r.overall_score < 2.0]
    below_3 = [r for r in report.results if r.overall_score < 3.0]

    if (
        report.avg_faithfulness >= 3.5
        and report.avg_relevancy >= 3.5
        and report.avg_overall >= 3.5
        and pipeline_errors <= 2
    ):
        if len(below_2) == 0 and len(below_3) == 0:
            verdict = "PASS"
        elif len(below_2) <= 3:
            verdict = "CONDITIONAL PASS"
        else:
            verdict = "FAIL"
    else:
        verdict = "FAIL"

    print(f"\n{'=' * 50}")
    print(f"VERDICT: {verdict}")
    print(f"{'=' * 50}")

    # Save report
    report_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "version": "1.51.1",
        "total_scenarios": report.total_scenarios,
        "successful_responses": resp_count,
        "pipeline_errors": pipeline_errors,
        "avg_response_time_ms": avg_time,
        "max_response_time_ms": max_time,
        "heuristic_scores": {
            "faithfulness": round(report.avg_faithfulness, 2),
            "relevancy": round(report.avg_relevancy, 2),
            "tone": round(report.avg_tone, 2),
            "overall": round(report.avg_overall, 2),
        },
        "pass_rates": {
            "contains_check": f"{contains_rate:.0f}%",
            "excludes_check": f"{excludes_rate:.0f}%",
            "escalation_accuracy": f"{esc_acc:.0f}%",
        },
        "deepeval_scores": None,
        "failing_scenarios": [
            {"id": r.scenario_id, "category": r.category, "overall": round(r.overall_score, 2), "issues": r.issues}
            for r in report.results
            if not r.passed
        ],
        "verdict": verdict,
    }

    report_path = os.path.join(RESULTS_DIR, f"quality-report-{datetime.now().strftime('%Y-%m-%d')}.json")
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)
    print(f"\nReport: {report_path}")


if __name__ == "__main__":
    main()
