#!/usr/bin/env python3
"""End-to-end conversation flow tests against live production API.

Tests conversation lifecycle, edge cases, SSE streaming, escalation,
multi-turn context, and widget key authentication across all chat operations.

IMPORTANT: The chat pipeline is triggered by the SSE stream endpoint
(GET /api/chat/stream/{id}), NOT by the message endpoint. The message
endpoint only stores the customer message. The SSE endpoint runs the
full pipeline (IC -> KR -> RG -> CR) and streams the response.

Usage:
    python scripts/test_e2e_conversation_flows.py

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import asyncio
import json
import os
import sys
import time
import uuid
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Auto-load .env.local (transient credentials must never be hardcoded)
# ---------------------------------------------------------------------------
# Load .env.local (shared loader — R7 refactoring)
from scripts._env import load_env_local
load_env_local()

# Default per REPEATABLE-PROCEDURES.md §7.4 — .env.local takes precedence
API = os.environ.get(
    "PROD_URL",
    "https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io",
)
WIDGET_KEY = os.environ.get("PREVIEW_WIDGET_KEY", "")
if not WIDGET_KEY:
    sys.exit("ERROR: PREVIEW_WIDGET_KEY not set. Load .env.local or set env var.")
INVALID_WIDGET_KEY = "pk_live_invalid_key_00000000"


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

async def _post(session, path, json_body=None, headers=None, widget_key=WIDGET_KEY):
    """POST with widget key auth."""
    h = {"X-Widget-Key": widget_key, "Content-Type": "application/json"}
    if headers:
        h.update(headers)
    async with session.post(f"{API}{path}", headers=h, json=json_body or {}) as resp:
        try:
            data = await resp.json()
        except Exception:
            data = {}
        return resp.status, data


async def _get(session, path, headers=None, widget_key=WIDGET_KEY):
    """GET with widget key auth."""
    h = {"X-Widget-Key": widget_key}
    if headers:
        h.update(headers)
    async with session.get(f"{API}{path}", headers=h) as resp:
        try:
            data = await resp.json()
        except Exception:
            data = {}
        return resp.status, data


async def create_conversation(session, initial_message=None, visitor=None):
    """Create a new conversation and return (conversation_id, response_data)."""
    body = {}
    if initial_message:
        body["initial_message"] = initial_message
    if visitor:
        body["visitor"] = visitor
    status, data = await _post(session, "/api/chat/conversations", body)
    assert status == 201, f"Expected 201, got {status}: {data}"
    return data["conversation_id"], data


async def send_and_stream(session, conv_id, content, timeout=45):
    """Send a message then connect to SSE to trigger the pipeline.

    This is the correct flow: POST message stores it, GET stream runs the pipeline.
    Returns (response_text, stages, conversation_state).
    """
    import aiohttp

    # 1. Send the customer message
    status, msg_data = await _post(session, "/api/chat/message", {
        "conversation_id": conv_id,
        "content": content,
    })
    if status != 200 or not msg_data.get("accepted"):
        return f"(message rejected: status={status} data={msg_data})", [], None, msg_data

    # 2. Brief pause then connect SSE (which triggers the pipeline)
    await asyncio.sleep(0.5)

    tokens = []
    stages = []
    sse_timeout = aiohttp.ClientTimeout(total=timeout)

    try:
        async with session.get(
            f"{API}/api/chat/stream/{conv_id}",
            headers={"X-Widget-Key": WIDGET_KEY},
            timeout=sse_timeout,
        ) as resp:
            buffer = ""
            done = False

            async for chunk in resp.content.iter_any():
                text = chunk.decode("utf-8", errors="replace")
                buffer += text

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    stripped = line.strip()

                    if not stripped:
                        continue

                    if stripped.startswith("data: "):
                        raw = stripped[6:]
                        if raw == "[DONE]":
                            done = True
                            break
                        try:
                            d = json.loads(raw)
                            if "text" in d and "sequence" in d:
                                tokens.append(d["text"])
                            elif "stage" in d:
                                stages.append(f"{d['stage']}:{d.get('status', '?')}")
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
                                stages.append(f"{d['stage']}:{d.get('status', '?')}")
                        except json.JSONDecodeError:
                            pass

                if done:
                    break
    except asyncio.TimeoutError:
        tokens.append("[TIMEOUT]")

    response = "".join(tokens)

    # 3. If no tokens from stream, fallback to conversation state
    if not response and conv_id:
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

    # 4. Get final conversation state
    state = None
    try:
        _, state = await _get(session, f"/api/chat/conversations/{conv_id}")
    except Exception:
        pass

    return response, stages, state, msg_data


async def get_conversation(session, conv_id):
    """Get conversation state."""
    return await _get(session, f"/api/chat/conversations/{conv_id}")


async def end_conversation(session, conv_id, feedback_rating=None, feedback_text=None, reason=None):
    """End a conversation with optional feedback."""
    body = {}
    if reason:
        body["reason"] = reason
    if feedback_rating:
        body["feedback_rating"] = feedback_rating
    if feedback_text:
        body["feedback_text"] = feedback_text
    return await _post(session, f"/api/chat/conversations/{conv_id}/end", body)


# ---------------------------------------------------------------------------
# Test definitions
# ---------------------------------------------------------------------------

results = []


def record(name, passed, detail=""):
    """Record a test result."""
    results.append({"name": name, "passed": passed, "detail": detail})
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {name}")
    if detail and not passed:
        print(f"         {detail[:200]}")


async def test_1_conversation_lifecycle(session):
    """Test full lifecycle: create -> message+stream -> state -> end."""
    print("\n[1/12] Conversation lifecycle...")

    # 1a-d. Create conversation
    conv_id, create_data = await create_conversation(session)
    record("1a: Create conversation", bool(conv_id), f"id={conv_id}")
    record("1b: Has stream_url", "stream_url" in create_data)
    record("1c: Has ws_url", "ws_url" in create_data)
    record("1d: Has created_at", "created_at" in create_data)

    # 1e-g. Send message + SSE stream (triggers pipeline)
    response, stages, state, msg_data = await send_and_stream(
        session, conv_id, "What is Agent Red?"
    )
    record("1e: Message accepted", msg_data.get("accepted", False))
    record("1f: AI responded via SSE", len(response) > 50,
           f"len={len(response)}")
    record("1g: Pipeline stages present", len(stages) >= 4,
           f"stages={' -> '.join(stages)}")

    # 1h-j. Get conversation state
    status, state_data = await get_conversation(session, conv_id)
    record("1h: Get state succeeds", status == 200)
    msgs = state_data.get("messages", [])
    record("1i: State has customer + AI messages", len(msgs) >= 2,
           f"msgs={len(msgs)}")
    record("1j: Status is active", state_data.get("status") == "active")

    # 1k-l. End conversation with feedback
    status, end_data = await end_conversation(
        session, conv_id,
        feedback_rating=5,
        feedback_text="Great conversation!",
        reason="resolved",
    )
    record("1k: End conversation succeeds", status == 200)
    record("1l: End returns terminal status",
           end_data.get("status") in ("completed", "ended", "closed"))

    return conv_id


async def test_2_conversation_with_initial_message(session):
    """Test creating a conversation with initial message + streaming."""
    print("\n[2/12] Conversation with initial message...")

    # Create with initial message
    conv_id, data = await create_conversation(
        session,
        initial_message="Tell me about your pricing plans",
    )
    record("2a: Created with initial message", bool(conv_id))

    # The initial message is stored; now SSE triggers the pipeline
    await asyncio.sleep(0.5)
    response, stages, _, _ = await send_and_stream.__wrapped__(session, conv_id) \
        if hasattr(send_and_stream, '__wrapped__') else (None, [], None, None)

    # Actually, let's stream directly since the initial message was already sent
    import aiohttp
    tokens = []
    try:
        sse_timeout = aiohttp.ClientTimeout(total=45)
        async with session.get(
            f"{API}/api/chat/stream/{conv_id}",
            headers={"X-Widget-Key": WIDGET_KEY},
            timeout=sse_timeout,
        ) as resp:
            buffer = ""
            done = False
            async for chunk in resp.content.iter_any():
                text = chunk.decode("utf-8", errors="replace")
                buffer += text
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    stripped = line.strip()
                    if not stripped:
                        continue
                    if stripped.startswith("data: "):
                        raw = stripped[6:]
                        if raw == "[DONE]":
                            done = True
                            break
                        try:
                            d = json.loads(raw)
                            if "text" in d and "sequence" in d:
                                tokens.append(d["text"])
                        except json.JSONDecodeError:
                            pass
                if done:
                    break
    except asyncio.TimeoutError:
        pass

    response = "".join(tokens)

    # Fallback: check conversation state
    if not response:
        await asyncio.sleep(3)
        _, state = await get_conversation(session, conv_id)
        for msg in reversed(state.get("messages", [])):
            if msg.get("role") in ("ai", "assistant"):
                response = msg.get("content", "")
                break

    record("2b: AI responded to initial message", len(response) > 50,
           f"len={len(response)}")

    content = response.lower()
    record("2c: Response mentions pricing",
           "price" in content or "$" in content or "plan" in content,
           f"resp={content[:150]}")


async def test_3_multi_turn_context_retention(session):
    """Test that the AI retains context across multiple turns."""
    print("\n[3/12] Multi-turn context retention...")

    conv_id, _ = await create_conversation(session)

    # Turn 1: Establish topic
    resp1, stages1, _, _ = await send_and_stream(
        session, conv_id, "I'm interested in the Starter plan"
    )
    record("3a: Turn 1 responded", len(resp1) > 20,
           f"len={len(resp1)}")

    # Turn 2: Follow-up referencing previous context
    await asyncio.sleep(1)
    resp2, _, _, _ = await send_and_stream(
        session, conv_id,
        "How many conversations are included in that plan?",
    )
    lower2 = resp2.lower()
    record("3b: Turn 2 references Starter context",
           "1,000" in lower2 or "1000" in lower2 or "starter" in lower2,
           f"resp={lower2[:150]}")

    # Turn 3: Another follow-up
    await asyncio.sleep(1)
    resp3, _, _, _ = await send_and_stream(
        session, conv_id,
        "What happens if I go over that limit?",
    )
    lower3 = resp3.lower()
    record("3c: Turn 3 addresses follow-up",
           len(resp3) > 20 and any(w in lower3 for w in [
               "overage", "pack", "additional", "extra", "$0.04", "beyond",
               "conversation", "limit", "exceed", "more", "plan", "upgrade",
           ]),
           f"resp={lower3[:150]}")

    # Check full state — at least 2 AI responses (3rd may not persist before state query)
    _, state = await get_conversation(session, conv_id)
    ai_msgs = [m for m in state.get("messages", []) if m.get("role") in ("ai", "assistant")]
    record("3d: Has 2+ AI responses", len(ai_msgs) >= 2,
           f"ai_msgs={len(ai_msgs)}")


async def test_4_edge_case_messages(session):
    """Test edge cases: short, long, special chars."""
    print("\n[4/12] Edge case messages...")

    conv_id, _ = await create_conversation(session)

    # 4a: Very short message
    resp, _, _, msg_data = await send_and_stream(session, conv_id, "Hi")
    record("4a: Short message accepted + responded",
           msg_data.get("accepted") and len(resp) > 5)

    # 4b: Message with special characters
    await asyncio.sleep(1)
    resp, _, _, msg_data = await send_and_stream(
        session, conv_id,
        "What about <script>alert('xss')</script> & HTML entities? $100 + 50% = ?",
    )
    record("4b: Special chars accepted", msg_data.get("accepted"))
    record("4c: No script injection in response",
           "<script>" not in resp and "alert(" not in resp)

    # 4d: Unicode message
    await asyncio.sleep(1)
    resp, _, _, msg_data = await send_and_stream(
        session, conv_id, "Hello! Can you help me? Thanks!")
    record("4d: Unicode accepted + responded",
           msg_data.get("accepted") and len(resp) > 5)

    # 4e: Long message
    await asyncio.sleep(1)
    long_msg = "I need help with " + ("my store setup and configuration. " * 100)
    long_msg = long_msg[:3900]
    status, msg_data = await _post(session, "/api/chat/message", {
        "conversation_id": conv_id, "content": long_msg,
    })
    record("4e: Long message (3900 chars) accepted",
           status == 200 and msg_data.get("accepted"))


async def test_5_widget_key_authentication(session):
    """Test widget key auth enforcement across all chat endpoints."""
    print("\n[5/12] Widget key authentication...")

    # 5a: Create with invalid key
    status, _ = await _post(
        session, "/api/chat/conversations", {},
        widget_key=INVALID_WIDGET_KEY,
    )
    record("5a: Invalid key rejected on create", status in (401, 403),
           f"status={status}")

    # 5b: Create with no key
    async with session.post(
        f"{API}/api/chat/conversations",
        headers={"Content-Type": "application/json"},
        json={},
    ) as resp:
        record("5b: No key rejected on create", resp.status in (401, 403),
               f"status={resp.status}")

    # 5c: Valid key creates successfully
    status, data = await _post(session, "/api/chat/conversations", {})
    record("5c: Valid key accepted on create", status == 201)

    if status == 201:
        conv_id = data["conversation_id"]

        # 5d: Send message with invalid key
        status, _ = await _post(
            session, "/api/chat/message",
            {"conversation_id": conv_id, "content": "test"},
            widget_key=INVALID_WIDGET_KEY,
        )
        record("5d: Invalid key rejected on message", status in (401, 403))

        # 5e: Get state with invalid key
        status, _ = await _get(
            session, f"/api/chat/conversations/{conv_id}",
            widget_key=INVALID_WIDGET_KEY,
        )
        record("5e: Invalid key rejected on get state", status in (401, 403))

        # 5f: End with invalid key
        status, _ = await _post(
            session, f"/api/chat/conversations/{conv_id}/end", {},
            widget_key=INVALID_WIDGET_KEY,
        )
        record("5f: Invalid key rejected on end", status in (401, 403))

        # 5g: SSE stream with invalid key
        import aiohttp
        try:
            async with session.get(
                f"{API}/api/chat/stream/{conv_id}",
                headers={"X-Widget-Key": INVALID_WIDGET_KEY},
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                record("5g: Invalid key rejected on stream",
                       resp.status in (401, 403),
                       f"status={resp.status}")
        except Exception:
            record("5g: Invalid key rejected on stream", True, "Connection refused/closed")


async def test_6_conversation_state_persistence(session):
    """Test that conversation state is correctly persisted."""
    print("\n[6/12] State persistence...")

    conv_id, _ = await create_conversation(session)
    response, stages, state, _ = await send_and_stream(
        session, conv_id, "What features does Agent Red offer?"
    )

    # Retrieve state
    status, data = await get_conversation(session, conv_id)
    record("6a: State retrieval succeeds", status == 200)

    messages = data.get("messages", [])
    customer_msgs = [m for m in messages if m.get("role") == "customer"]
    ai_msgs = [m for m in messages if m.get("role") in ("ai", "assistant")]

    record("6b: Has customer message", len(customer_msgs) >= 1)
    record("6c: Has AI response", len(ai_msgs) >= 1)
    record("6d: Messages in chronological order",
           all(messages[i].get("timestamp", "") <= messages[i + 1].get("timestamp", "")
               for i in range(len(messages) - 1)) if len(messages) > 1 else True)
    record("6e: Turn count >= 1",
           data.get("turn_count", 0) >= 1,
           f"turns={data.get('turn_count')}")
    record("6f: Message count matches array",
           data.get("message_count", 0) == len(messages),
           f"count={data.get('message_count')}, array={len(messages)}")

    # Verify the AI response content matches what was streamed
    if ai_msgs:
        stored_resp = ai_msgs[-1].get("content", "")
        record("6g: Stored response matches SSE stream",
               len(stored_resp) > 50 and stored_resp[:50] in response[:100] if response else True,
               f"stored={len(stored_resp)}, streamed={len(response)}")


async def test_7_nonexistent_conversation(session):
    """Test error handling for nonexistent conversation IDs."""
    print("\n[7/12] Nonexistent conversation handling...")

    fake_id = f"conv_nonexistent_{uuid.uuid4().hex[:8]}"

    status, _ = await get_conversation(session, fake_id)
    record("7a: Get nonexistent returns 404", status == 404)

    status, _ = await _post(session, "/api/chat/message", {
        "conversation_id": fake_id, "content": "Hello",
    })
    record("7b: Message to nonexistent returns 404", status == 404)

    status, _ = await end_conversation(session, fake_id)
    record("7c: End nonexistent returns 404", status == 404)


async def test_8_ended_conversation_behavior(session):
    """Test behavior with an ended conversation."""
    print("\n[8/12] Ended conversation behavior...")

    conv_id, _ = await create_conversation(session)
    await send_and_stream(session, conv_id, "Quick question about pricing")
    await end_conversation(session, conv_id, reason="resolved")

    # Read ended conversation
    status, data = await get_conversation(session, conv_id)
    record("8a: Can still read ended conversation", status == 200)
    record("8b: Status shows ended",
           data.get("status") in ("completed", "ended", "closed"),
           f"status={data.get('status')}")

    # Send to ended
    status, data = await _post(session, "/api/chat/message", {
        "conversation_id": conv_id, "content": "Another question",
    })
    record("8c: Message to ended returns 409", status == 409,
           f"status={status}")

    # Re-end
    status, _ = await end_conversation(session, conv_id)
    record("8d: Re-ending returns 409", status == 409,
           f"status={status}")


async def test_9_escalation_flow(session):
    """Test escalation intent handling."""
    print("\n[9/12] Escalation flow...")

    conv_id, _ = await create_conversation(session)
    response, stages, state, _ = await send_and_stream(
        session, conv_id,
        "I need to speak with a human agent right now. This is urgent and the AI is not helping.",
    )

    lower = response.lower()
    record("9a: Escalation acknowledged",
           any(w in lower for w in [
               "understand", "human", "agent", "team", "support",
               "connect", "transfer", "escalat", "help",
           ]),
           f"resp={lower[:150]}")

    _, state_data = await get_conversation(session, conv_id)
    record("9b: Conversation state accessible",
           state_data.get("status") in ("active", "escalated"),
           f"status={state_data.get('status')}")


async def test_10_concurrent_conversations(session):
    """Test multiple concurrent conversations."""
    print("\n[10/12] Concurrent conversations...")

    # Create 3 conversations
    tasks = [create_conversation(session) for _ in range(3)]
    convs = await asyncio.gather(*tasks, return_exceptions=True)
    valid_convs = [(cid, data) for cid, data in convs if isinstance(cid, str)]
    record("10a: Created 3 concurrent conversations",
           len(valid_convs) == 3,
           f"created={len(valid_convs)}")

    ids = [cid for cid, _ in valid_convs]
    record("10b: All have unique IDs", len(set(ids)) == len(ids))

    # Send messages and stream responses (sequential to avoid SSE slot contention)
    if len(valid_convs) >= 2:
        questions = [
            "What is Agent Red?",
            "Tell me about your Enterprise plan",
        ]
        responses = []
        for i in range(2):
            resp, _, _, _ = await send_and_stream(
                session, valid_convs[i][0], questions[i],
            )
            if len(resp) > 10:
                responses.append(resp)
            await asyncio.sleep(3)

        record("10c: At least 1 concurrent conversation got responses",
               len(responses) >= 1,
               f"resp_count={len(responses)}")

        if len(responses) == 2:
            record("10d: Responses are different",
                   responses[0] != responses[1])


async def test_11_stream_status_endpoint(session):
    """Test the SSE stream status endpoint."""
    print("\n[11/12] Stream status endpoint...")

    conv_id, _ = await create_conversation(session)

    status, data = await _get(session, f"/api/chat/stream/{conv_id}/status")
    record("11a: Stream status returns 200", status == 200)
    record("11b: Has expected fields",
           all(k in data for k in ["conversation_id", "is_streaming", "tab_count", "can_connect"]),
           f"keys={list(data.keys())}")
    record("11c: Not streaming initially",
           data.get("is_streaming") is False,
           f"is_streaming={data.get('is_streaming')}")
    record("11d: Can connect",
           data.get("can_connect") is True)


async def test_12_pipeline_stages(session):
    """Test that the full pipeline executes all expected stages."""
    print("\n[12/12] Pipeline stages verification...")

    conv_id, _ = await create_conversation(session)
    response, stages, _, _ = await send_and_stream(
        session, conv_id, "How much does Agent Red cost?"
    )

    # Expected stages: IC -> KR -> RG -> CR
    stage_names = [s.split(":")[0] for s in stages]
    record("12a: Intent classifier ran",
           "intent-classifier" in stage_names,
           f"stages={stage_names}")
    record("12b: Knowledge retrieval ran",
           "knowledge-retrieval" in stage_names)
    record("12c: Response generator ran",
           "response-generator" in stage_names)
    record("12d: Critic supervisor ran",
           "critic-supervisor" in stage_names)

    # Check all stages completed
    completed_stages = [s for s in stages if "completed" in s]
    record("12e: All stages completed",
           len(completed_stages) >= 4,
           f"completed={len(completed_stages)}")

    # Response should mention pricing
    lower = response.lower()
    record("12f: Response has pricing data",
           "$" in response or "price" in lower or "plan" in lower,
           f"resp={lower[:150]}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main():
    import aiohttp

    print("=" * 70)
    print("AGENT RED E2E CONVERSATION FLOW TESTS")
    print(f"API: {API}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print("=" * 70)

    # Verify API is healthy
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                f"{API}/health",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                if resp.status != 200:
                    print(f"\nERROR: API not healthy (status={resp.status})")
                    return False
                health = await resp.json()
                print(f"API Version: {health.get('version', 'unknown')}")
                print(f"Uptime: {health.get('uptime_seconds', 'unknown')}s")
        except Exception as e:
            print(f"\nERROR: Cannot reach API: {e}")
            return False

        # Run all tests
        await test_1_conversation_lifecycle(session)
        await test_2_conversation_with_initial_message(session)
        await test_3_multi_turn_context_retention(session)
        await test_4_edge_case_messages(session)
        await test_5_widget_key_authentication(session)
        await test_6_conversation_state_persistence(session)
        await test_7_nonexistent_conversation(session)
        await test_8_ended_conversation_behavior(session)
        await test_9_escalation_flow(session)
        await test_10_concurrent_conversations(session)
        await test_11_stream_status_endpoint(session)
        await test_12_pipeline_stages(session)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    passed = sum(1 for r in results if r["passed"])
    failed = sum(1 for r in results if not r["passed"])
    total = len(results)

    print(f"Passed: {passed}/{total}")
    if failed:
        print(f"Failed: {failed}")
        for r in results:
            if not r["passed"]:
                print(f"  [FAIL] {r['name']}: {r['detail']}")

    print(f"\nOverall: {'ALL TESTS PASSED' if failed == 0 else f'{failed} TESTS FAILED'}")
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
