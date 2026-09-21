#!/usr/bin/env python3
"""Comprehensive chat quality test battery.

Tests multiple conversation scenarios against the live production API
and evaluates response quality.

Usage:
    python scripts/test_chat_battery.py
"""
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlsplit

# ---------------------------------------------------------------------------
# Auto-load .env.local (transient credentials must never be hardcoded)
# ---------------------------------------------------------------------------
# Load .env.local (shared loader — R7 refactoring)
REPO_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = REPO_ROOT / "applications/Agent_Red"
sys.path.insert(0, str(REPO_ROOT))

from scripts._env import load_env_local  # noqa: E402 - standalone script bootstrap

API = ""
WIDGET_KEY = ""


async def chat(message: str, conv_id: str | None = None) -> tuple[str, str, list[str]]:
    """Return the persisted reply to this message, plus confirmed stream appendices."""
    import codecs

    import aiohttp

    headers = {"X-Widget-Key": WIDGET_KEY, "Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        if not conv_id:
            async with session.post(f"{API}/api/chat/conversations", headers=headers, json={}) as resp:
                resp.raise_for_status()
                conv_id = (await resp.json())["conversation_id"]

        async with session.post(
            f"{API}/api/chat/message",
            headers=headers,
            json={"conversation_id": conv_id, "content": message},
        ) as resp:
            resp.raise_for_status()
            accepted = await resp.json()
        customer_id = accepted.get("message_id")
        before_turn = accepted.get("turn_count")
        if (
            accepted.get("accepted") is not True
            or accepted.get("conversation_id") != conv_id
            or not isinstance(customer_id, str)
            or not customer_id
            or type(before_turn) is not int
        ):
            raise RuntimeError("Chat acknowledgement did not identify the accepted message")

        await asyncio.sleep(0.5)
        stages, appendix, pending_appendix = [], [], []
        done_turn = None
        saw_application_event = False
        reply_id = None
        retracted_text = None
        after_reply = False
        stream_error = False
        buffer = ""
        decoder = codecs.getincrementaldecoder("utf-8")()
        try:
            async with session.get(
                f"{API}/api/chat/stream/{conv_id}",
                headers={"X-Widget-Key": WIDGET_KEY},
                timeout=aiohttp.ClientTimeout(total=40),
            ) as resp:
                resp.raise_for_status()
                async for chunk in resp.content.iter_any():
                    buffer += decoder.decode(chunk)
                    buffer = buffer.replace("\r\n", "\n")
                    while "\n\n" in buffer:
                        block, buffer = buffer.split("\n\n", 1)
                        event = ""
                        data_lines = []
                        for line in block.splitlines():
                            if line.startswith("event:"):
                                event = line[6:].strip()
                            elif line.startswith("data:"):
                                data_lines.append(line[5:].lstrip())
                        if not event and not data_lines:
                            continue  # SSE heartbeat or comment.
                        saw_application_event = True
                        data = json.loads("\n".join(data_lines))
                        if not isinstance(data, dict):
                            raise RuntimeError("Invalid chat stream event")
                        if event == "done":
                            count = data.get("turn_count")
                            if data.get("conversation_id") != conv_id or type(count) is not int:
                                raise RuntimeError("Chat completion does not identify this conversation")
                            if count <= before_turn:
                                # The endpoint replays previous turns from its buffer.
                                stages, appendix, pending_appendix = [], [], []
                                reply_id = retracted_text = None
                                after_reply = False
                                continue
                            done_turn = count
                            break
                        if event == "error":
                            stream_error = True
                        elif event == "stage":
                            stages.append(f"{data['stage']}:{data.get('status', '?')}")
                        elif event == "validated":
                            if data.get("conversation_id") != conv_id:
                                raise RuntimeError("Validated reply belongs to another conversation")
                            message_id = data.get("message_id")
                            if not isinstance(message_id, str) or not message_id:
                                raise RuntimeError("Validated reply has no message identity")
                            if message_id in {"escalation", "escalation_email_required"}:
                                if not after_reply:
                                    raise RuntimeError("Escalation appendix has no confirmed base reply")
                                appendix.extend(pending_appendix)
                                pending_appendix = []
                            else:
                                reply_id = message_id
                                after_reply = True
                                appendix, pending_appendix = [], []
                        elif event == "retracted":
                            retracted_text = data.get("fallback_text")
                            if not isinstance(retracted_text, str):
                                raise RuntimeError("Retracted reply has no fallback text")
                            reply_id = None
                            after_reply = True
                            appendix, pending_appendix = [], []
                        elif event == "token" and after_reply:
                            pending_appendix.append(data["text"])
                    if done_turn is not None:
                        break
        except TimeoutError as error:
            raise RuntimeError("Chat stream timed out") from error
        if stream_error:
            raise RuntimeError("Chat stream reported an error")
        if done_turn is None and (saw_application_event or buffer.strip()):
            raise RuntimeError("Chat stream ended before current-turn completion")
        if pending_appendix:
            raise RuntimeError("Chat stream contains an unconfirmed response appendix")

        # A completed-message reconnect can intentionally return an empty stream.
        # Both that case and normal completion must resolve the exact current reply.
        async with session.get(f"{API}/api/chat/conversations/{conv_id}", headers={"X-Widget-Key": WIDGET_KEY}) as resp:
            resp.raise_for_status()
            state = await resp.json()
        state_turn = state.get("turn_count")
        if (
            state.get("conversation_id") != conv_id
            or type(state_turn) is not int
            or state_turn <= before_turn
            or (done_turn is not None and state_turn != done_turn)
        ):
            raise RuntimeError("Persisted conversation does not confirm this completed turn")
        found_customer = False
        for item in state.get("messages", []):
            if item.get("role") == "customer":
                if found_customer:
                    break
                found_customer = item.get("message_id") == customer_id
            elif found_customer and item.get("role") == "ai":
                response = item.get("content")
                if not isinstance(response, str) or not response:
                    break
                if reply_id is not None and item.get("message_id") != reply_id:
                    raise RuntimeError("Validated reply does not match the persisted current reply")
                if retracted_text is not None and response != retracted_text:
                    raise RuntimeError("Retracted fallback does not match the persisted current reply")
                return response + "".join(appendix), conv_id, stages
        raise RuntimeError("No persisted AI reply follows the acknowledged customer message")


def evaluate_response(test_name: str, message: str, response: str, criteria: dict) -> dict:
    """Evaluate a response against quality criteria.

    Returns dict with pass/fail for each criterion.
    """
    result = {"test": test_name, "message": message, "response": response, "checks": {}}
    lower = response.lower()

    for check_name, check_fn in criteria.items():
        passed = check_fn(response, lower)
        result["checks"][check_name] = passed

    all_passed = all(result["checks"].values())
    result["passed"] = all_passed
    return result


async def main():
    global API, WIDGET_KEY
    load_env_local(env_file=APP_ROOT / ".env.local")
    API = os.environ.get("PROD_URL", "").rstrip("/")
    WIDGET_KEY = os.environ.get("PREVIEW_WIDGET_KEY", "")
    target = urlsplit(API)
    if (
        target.scheme not in {"http", "https"}
        or not target.hostname
        or target.query
        or target.fragment
        or target.username is not None
        or target.password is not None
        or not WIDGET_KEY
    ):
        print("ERROR: PROD_URL and PREVIEW_WIDGET_KEY must identify the selected application")
        return False
    print("=" * 70)
    print("AGENT RED CHAT QUALITY TEST BATTERY")
    print(f"API: {API}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print("=" * 70)

    results = []

    # ---------------------------------------------------------------
    # Test 1: Pricing question (the critical test)
    # ---------------------------------------------------------------
    print("\n[1/8] Pricing question...")
    resp, conv_id, stages = await chat("How much does Agent Red cost?")
    r = evaluate_response(
        "Pricing",
        "How much does Agent Red cost?",
        resp,
        {
            "mentions_starter": lambda r, l: "starter" in l,
            "mentions_professional": lambda r, l: "professional" in l,
            "mentions_enterprise": lambda r, l: "enterprise" in l,
            "has_149": lambda r, l: "$149" in r,
            "has_399": lambda r, l: "$399" in r,
            "has_999": lambda r, l: "$999" in r,
            "has_conversations": lambda r, l: "conversation" in l,
            "no_check_website": lambda r, l: "check" not in l or "website" not in l,
            "not_empty": lambda r, l: len(r) > 50,
        },
    )
    results.append(r)
    print(f"  {'PASS' if r['passed'] else 'FAIL'}: {r['checks']}")
    print(f"  Response preview: {resp[:200]}...")

    # ---------------------------------------------------------------
    # Test 2: Greeting
    # ---------------------------------------------------------------
    print("\n[2/8] Greeting...")
    resp, _, _ = await chat("Hello!")
    r = evaluate_response(
        "Greeting",
        "Hello!",
        resp,
        {
            "is_warm": lambda r, l: any(w in l for w in ["hello", "hi", "welcome", "hey", "great"]),
            "offers_help": lambda r, l: any(w in l for w in ["help", "assist", "question"]),
            "no_product_dump": lambda r, l: "$149" not in r and "$399" not in r,
            "reasonable_length": lambda r, l: 20 < len(r) < 500,
        },
    )
    results.append(r)
    print(f"  {'PASS' if r['passed'] else 'FAIL'}: {r['checks']}")
    print(f"  Response: {resp[:200]}")

    # ---------------------------------------------------------------
    # Test 3: Features question
    # ---------------------------------------------------------------
    print("\n[3/8] Features question...")
    resp, _, _ = await chat("What features does Agent Red offer?")
    r = evaluate_response(
        "Features",
        "What features does Agent Red offer?",
        resp,
        {
            "mentions_ai": lambda r, l: "ai" in l or "artificial" in l,
            "mentions_specific_feature": lambda r, l: any(
                w in l for w in ["memory", "personalization", "knowledge", "widget", "shopify", "integration"]
            ),
            "not_generic": lambda r, l: len(r) > 100,
            "no_check_website": lambda r, l: "check" not in l or "website" not in l,
        },
    )
    results.append(r)
    print(f"  {'PASS' if r['passed'] else 'FAIL'}: {r['checks']}")
    print(f"  Response preview: {resp[:200]}...")

    # ---------------------------------------------------------------
    # Test 4: Multi-turn conversation (pricing follow-up)
    # ---------------------------------------------------------------
    print("\n[4/8] Multi-turn: pricing then follow-up...")
    resp1, conv_id, _ = await chat("What are your pricing plans?")
    await asyncio.sleep(2)
    resp2, _, _ = await chat("Which plan would you recommend for a small store?", conv_id)
    r = evaluate_response(
        "Multi-turn follow-up",
        "Which plan would you recommend for a small store?",
        resp2,
        {
            "mentions_starter": lambda r, l: "starter" in l,
            "makes_recommendation": lambda r, l: any(
                w in l
                for w in [
                    "recommend",
                    "suggest",
                    "ideal",
                    "good fit",
                    "perfect",
                    "great fit",
                    "great for",
                    "best",
                    "right for",
                    "suit",
                ]
            ),
            "not_empty": lambda r, l: len(r) > 50,
        },
    )
    results.append(r)
    print(f"  {'PASS' if r['passed'] else 'FAIL'}: {r['checks']}")
    print(f"  Response preview: {resp2[:200]}...")

    # ---------------------------------------------------------------
    # Test 5: Installation/setup question
    # ---------------------------------------------------------------
    print("\n[5/8] Installation question...")
    resp, _, _ = await chat("How do I install Agent Red on my Shopify store?")
    r = evaluate_response(
        "Installation",
        "How do I install Agent Red on my Shopify store?",
        resp,
        {
            "mentions_shopify": lambda r, l: "shopify" in l,
            "has_steps": lambda r, l: any(w in l for w in ["step", "1.", "first", "install"]),
            "mentions_app": lambda r, l: "app" in l,
            "not_empty": lambda r, l: len(r) > 100,
        },
    )
    results.append(r)
    print(f"  {'PASS' if r['passed'] else 'FAIL'}: {r['checks']}")
    print(f"  Response preview: {resp[:200]}...")

    # ---------------------------------------------------------------
    # Test 6: Competitor comparison
    # ---------------------------------------------------------------
    print("\n[6/8] Competitor comparison...")
    resp, _, _ = await chat("How does Agent Red compare to Tidio?")
    r = evaluate_response(
        "Competitor comparison",
        "How does Agent Red compare to Tidio?",
        resp,
        {
            "mentions_tidio": lambda r, l: "tidio" in l,
            "mentions_advantage": lambda r, l: any(
                w in l for w in ["cheaper", "affordable", "cost", "price", "advantage", "competitive", "saving"]
            ),
            "not_empty": lambda r, l: len(r) > 80,
        },
    )
    results.append(r)
    print(f"  {'PASS' if r['passed'] else 'FAIL'}: {r['checks']}")
    print(f"  Response preview: {resp[:200]}...")

    # ---------------------------------------------------------------
    # Test 7: Out-of-scope question (should handle gracefully)
    # ---------------------------------------------------------------
    print("\n[7/8] Out-of-scope question...")
    resp, _, _ = await chat("What's the weather like today?")
    r = evaluate_response(
        "Out-of-scope",
        "What's the weather like today?",
        resp,
        {
            "doesnt_fabricate_weather": lambda r, l: "sunny" not in l and "rain" not in l and "degrees" not in l,
            "stays_helpful": lambda r, l: any(w in l for w in ["help", "assist", "agent red", "customer", "question"]),
            "not_empty": lambda r, l: len(r) > 20,
        },
    )
    results.append(r)
    print(f"  {'PASS' if r['passed'] else 'FAIL'}: {r['checks']}")
    print(f"  Response: {resp[:200]}")

    # ---------------------------------------------------------------
    # Test 8: Escalation intent
    # ---------------------------------------------------------------
    print("\n[8/8] Escalation request...")
    resp, _, stages = await chat("I need to speak with a human agent immediately, this is urgent!")
    r = evaluate_response(
        "Escalation",
        "I need to speak with a human agent immediately, this is urgent!",
        resp,
        {
            "acknowledges_request": lambda r, l: any(
                w in l for w in ["understand", "help", "human", "agent", "team", "support", "connect", "transfer"]
            ),
            "not_empty": lambda r, l: len(r) > 20,
        },
    )
    results.append(r)
    print(f"  {'PASS' if r['passed'] else 'FAIL'}: {r['checks']}")
    print(f"  Stages: {' -> '.join(stages)}")
    print(f"  Response: {resp[:200]}")

    # ---------------------------------------------------------------
    # Summary
    # ---------------------------------------------------------------
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"Passed: {passed}/{total}")
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        failed_checks = [k for k, v in r["checks"].items() if not v]
        if failed_checks:
            print(f"  [{status}] {r['test']}: failed={failed_checks}")
        else:
            print(f"  [{status}] {r['test']}")

    print(f"\nOverall: {'ALL TESTS PASSED' if passed == total else f'{total - passed} TESTS FAILED'}")
    return passed == total


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
