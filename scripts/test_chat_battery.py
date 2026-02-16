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

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Auto-load .env.local (transient credentials must never be hardcoded)
# ---------------------------------------------------------------------------
_env_local = Path(__file__).resolve().parent.parent / ".env.local"
if _env_local.is_file():
    with open(_env_local) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _, _v = _line.partition("=")
                _k, _v = _k.strip(), _v.strip()
                if _k and _v and _k not in os.environ:
                    os.environ[_k] = _v

API = os.environ.get(
    "PROD_URL",
    "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
)
WIDGET_KEY = os.environ.get("PREVIEW_WIDGET_KEY", "")
if not WIDGET_KEY:
    sys.exit("ERROR: PREVIEW_WIDGET_KEY not set. Load .env.local or set env var.")


async def chat(message: str, conv_id: str | None = None) -> tuple[str, str, list[str]]:
    """Send a message and get the streamed response.

    Returns (response_text, conversation_id, stages).
    """
    import aiohttp

    headers = {"X-Widget-Key": WIDGET_KEY, "Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        # Create conversation if needed
        if not conv_id:
            async with session.post(
                f"{API}/api/chat/conversations", headers=headers, json={}
            ) as resp:
                data = await resp.json()
                conv_id = data["conversation_id"]

        # Send message first, then connect SSE with a small delay.
        # The SSE manager buffers events per conversation (up to 100),
        # so events that arrive before the client connects are replayed
        # via Last-Event-ID.  We use a brief wait between message send
        # and SSE connect to let the pipeline begin processing.
        async with session.post(
            f"{API}/api/chat/message",
            headers=headers,
            json={"conversation_id": conv_id, "content": message},
        ) as resp:
            msg_data = await resp.json()
            if not msg_data.get("accepted"):
                return f"(message rejected: {msg_data})", conv_id, []

        # Brief pause then read SSE (buffered events will be replayed)
        await asyncio.sleep(0.5)

        tokens = []
        stages = []
        start = time.monotonic()
        timeout = aiohttp.ClientTimeout(total=40)

        try:
            async with session.get(
                f"{API}/api/chat/stream/{conv_id}",
                headers={"X-Widget-Key": WIDGET_KEY},
                timeout=timeout,
            ) as resp:
                # Parse proper SSE format:
                #   event: token
                #   id: 6
                #   data: {"text": "Hello", "sequence": 1}
                buffer = ""
                done = False
                no_data_since = time.monotonic()

                async for chunk in resp.content.iter_any():
                    text = chunk.decode("utf-8", errors="replace")
                    buffer += text
                    no_data_since = time.monotonic()

                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        stripped = line.strip()

                        if not stripped:
                            continue

                        if stripped.startswith("event: "):
                            pass  # event type
                        elif stripped.startswith("id: ") or stripped.startswith("retry: "):
                            pass
                        elif stripped.startswith("data: "):
                            raw = stripped[6:]
                            if raw == "[DONE]":
                                done = True
                                break
                            try:
                                d = json.loads(raw)
                                if "text" in d and "sequence" in d:
                                    tokens.append(d["text"])
                                elif "stage" in d:
                                    stages.append(f"{d['stage']}:{d.get('status','?')}")
                                elif "detail" in d:
                                    tokens.append(f"[ERROR: {d['detail']}]")
                            except json.JSONDecodeError:
                                pass
                        elif stripped.startswith("{"):
                            try:
                                d = json.loads(stripped)
                                if "text" in d and "sequence" in d:
                                    tokens.append(d["text"])
                                elif "stage" in d:
                                    stages.append(f"{d['stage']}:{d.get('status','?')}")
                                elif "detail" in d:
                                    tokens.append(f"[ERROR: {d['detail']}]")
                            except json.JSONDecodeError:
                                pass

                    if done:
                        break
        except asyncio.TimeoutError:
            tokens.append("[TIMEOUT]")

        elapsed = time.monotonic() - start
        response = "".join(tokens)

        # If we got no tokens, the pipeline may have completed before
        # our SSE connection.  Wait briefly for persistence, then retrieve
        # the conversation state to get the response from message history.
        if not tokens and conv_id:
            await asyncio.sleep(3)
            try:
                async with session.get(
                    f"{API}/api/chat/conversations/{conv_id}",
                    headers={"X-Widget-Key": WIDGET_KEY},
                ) as resp:
                    if resp.status == 200:
                        state_data = await resp.json()
                        for msg in reversed(state_data.get("messages", [])):
                            if msg.get("role") in ("assistant", "ai"):
                                response = msg.get("content", "")
                                break
            except Exception:
                pass

        return response, conv_id, stages


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
                w in l for w in ["recommend", "suggest", "ideal", "good fit", "perfect", "great fit", "great for", "best", "right for", "suit"]
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
            "stays_helpful": lambda r, l: any(
                w in l for w in ["help", "assist", "agent red", "customer", "question"]
            ),
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
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
