"""Tests for Structured Answer Blocks extraction (SPEC-1867).

Covers:
    - Steps extraction from numbered lists
    - FAQ extraction from Q&A pairs
    - Action extraction from markdown links with action verbs
    - No blocks from plain text
    - Combined extraction
    - Edge cases (single item, missing patterns)

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations


from src.chat.blocks import (
    extract_actions,
    extract_blocks,
    extract_faq,
    extract_steps,
)


# ---------------------------------------------------------------------------
# Steps extraction
# ---------------------------------------------------------------------------


class TestExtractSteps:
    def test_numbered_list(self) -> None:
        text = "Here's how to return an item:\n1. Find your order number\n2. Go to the returns page\n3. Select the item to return\n4. Print the shipping label"
        result = extract_steps(text)
        assert result is not None
        assert result["type"] == "steps"
        assert len(result["items"]) == 4
        assert "order number" in result["items"][0]

    def test_step_prefix_pattern(self) -> None:
        text = "Step 1: Open settings\nStep 2: Click on profile\nStep 3: Update your email"
        result = extract_steps(text)
        assert result is not None
        assert len(result["items"]) == 3

    def test_single_item_not_a_list(self) -> None:
        text = "1. This is the only step"
        result = extract_steps(text)
        assert result is None  # Need at least 2

    def test_no_numbered_items(self) -> None:
        text = "This is a plain paragraph with no numbered steps."
        result = extract_steps(text)
        assert result is None

    def test_title_extraction(self) -> None:
        text = "How to track your order\n1. Go to order tracking\n2. Enter your order number\n3. View status"
        result = extract_steps(text)
        assert result is not None
        assert result["title"] is not None
        assert "track" in result["title"].lower()


# ---------------------------------------------------------------------------
# FAQ extraction
# ---------------------------------------------------------------------------


class TestExtractFaq:
    def test_qa_pattern(self) -> None:
        text = "Q: What is your return policy?\nA: We accept returns within 30 days.\nQ: How long do refunds take?\nA: Refunds are processed in 5-7 business days."
        result = extract_faq(text)
        assert result is not None
        assert result["type"] == "faq"
        assert len(result["items"]) == 2
        assert "return policy" in result["items"][0]["question"]

    def test_bold_question_format(self) -> None:
        text = "**What is your return policy?**\nWe accept returns within 30 days.\n\n**How long do refunds take?**\nRefunds are processed in 5-7 business days."
        result = extract_faq(text)
        assert result is not None
        assert result["type"] == "faq"
        assert len(result["items"]) == 2
        assert "return policy" in result["items"][0]["question"]
        assert "30 days" in result["items"][0]["answer"]

    def test_no_qa_pattern(self) -> None:
        text = "This is a regular response without any Q&A formatting."
        result = extract_faq(text)
        assert result is None


# ---------------------------------------------------------------------------
# Action extraction
# ---------------------------------------------------------------------------


class TestExtractActions:
    def test_action_link(self) -> None:
        text = "You can [Track Your Order](https://example.com/tracking) here."
        result = extract_actions(text)
        assert len(result) == 1
        assert result[0]["type"] == "action"
        assert result[0]["label"] == "Track Your Order"
        assert result[0]["url"] == "https://example.com/tracking"

    def test_non_action_link(self) -> None:
        text = "Read about our [privacy policy](https://example.com/privacy)."
        result = extract_actions(text)
        assert len(result) == 0  # "privacy policy" doesn't contain action verbs

    def test_multiple_action_links(self) -> None:
        text = "[Track Order](https://a.com/track) or [Contact Us](https://a.com/contact)"
        result = extract_actions(text)
        assert len(result) == 2

    def test_caps_at_three(self) -> None:
        text = (
            "[Track 1](https://a.com/1) "
            "[Track 2](https://a.com/2) "
            "[Track 3](https://a.com/3) "
            "[Track 4](https://a.com/4)"
        )
        blocks = extract_blocks(text)
        action_blocks = [b for b in blocks if b["type"] == "action"]
        assert len(action_blocks) <= 3


# ---------------------------------------------------------------------------
# Combined extraction
# ---------------------------------------------------------------------------


class TestExtractBlocks:
    def test_plain_text_no_blocks(self) -> None:
        text = "Thanks for reaching out! Your order is on its way."
        blocks = extract_blocks(text)
        assert blocks == []

    def test_steps_and_actions(self) -> None:
        text = (
            "Here's how to return:\n"
            "1. Go to returns page\n"
            "2. Select your item\n"
            "3. Print label\n\n"
            "[Start Return](https://example.com/returns)"
        )
        blocks = extract_blocks(text)
        types = [b["type"] for b in blocks]
        assert "steps" in types
        assert "action" in types

    def test_empty_string(self) -> None:
        assert extract_blocks("") == []

    def test_block_ordering(self) -> None:
        """Steps should come before FAQ, FAQ before actions."""
        text = (
            "[Visit Store](https://example.com/shop)\n\n"
            "Q: Is it free?\nA: Yes it is.\n\n"
            "1. First step\n2. Second step"
        )
        blocks = extract_blocks(text)
        types = [b["type"] for b in blocks]
        if "steps" in types and "faq" in types:
            assert types.index("steps") < types.index("faq")
        if "faq" in types and "action" in types:
            assert types.index("faq") < types.index("action")
