"""Response tone preset tests (B3, SPEC-1871).

Tests for the preset mapping layer over brand_voice, formality_level,
and response_length.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import pytest

from src.multi_tenant.system_prompt_builder import (
    _TONE_PRESETS,
    _resolve_tone_preset,
)


class _MockPrefs:
    """Lightweight stand-in for PreferencesDocument."""

    def __init__(
        self,
        *,
        response_tone_preset: str | None = None,
        brand_voice: str | None = None,
        formality_level: str | None = None,
        response_length: str | None = None,
    ):
        self.response_tone_preset = response_tone_preset
        self.brand_voice = brand_voice
        self.formality_level = formality_level
        self.response_length = response_length


class TestTonePresetResolution:
    """B3: _resolve_tone_preset maps presets to existing fields (SPEC-1871)."""

    def test_professional_preset(self):
        """Professional preset: formal, standard."""
        bv, fl, rl = _resolve_tone_preset(
            _MockPrefs(response_tone_preset="professional")
        )
        assert "professional" in bv.lower()
        assert fl == "formal"
        assert rl == "standard"

    def test_friendly_preset(self):
        """Friendly preset: balanced, standard."""
        bv, fl, rl = _resolve_tone_preset(
            _MockPrefs(response_tone_preset="friendly")
        )
        assert "friendly" in bv.lower()
        assert fl == "balanced"
        assert rl == "standard"

    def test_casual_preset(self):
        """Casual preset: casual, concise."""
        bv, fl, rl = _resolve_tone_preset(
            _MockPrefs(response_tone_preset="casual")
        )
        assert "casual" in bv.lower()
        assert fl == "casual"
        assert rl == "concise"

    def test_expert_preset(self):
        """Expert preset: formal, detailed."""
        bv, fl, rl = _resolve_tone_preset(
            _MockPrefs(response_tone_preset="expert")
        )
        assert "authoritative" in bv.lower()
        assert fl == "formal"
        assert rl == "detailed"

    def test_custom_preset_uses_individual_fields(self):
        """Custom preset falls through to merchant's individual fields."""
        bv, fl, rl = _resolve_tone_preset(
            _MockPrefs(
                response_tone_preset="custom",
                brand_voice="snarky and witty",
                formality_level="casual",
                response_length="concise",
            )
        )
        assert bv == "snarky and witty"
        assert fl == "casual"
        assert rl == "concise"

    def test_null_preset_uses_individual_fields(self):
        """Null/None preset falls through to individual fields."""
        bv, fl, rl = _resolve_tone_preset(
            _MockPrefs(
                response_tone_preset=None,
                brand_voice="warm and empathetic",
                formality_level="balanced",
                response_length="detailed",
            )
        )
        assert bv == "warm and empathetic"
        assert fl == "balanced"
        assert rl == "detailed"

    def test_preset_overrides_individual_fields(self):
        """Preset values take precedence over conflicting individual fields."""
        bv, fl, rl = _resolve_tone_preset(
            _MockPrefs(
                response_tone_preset="professional",
                brand_voice="totally casual dude",
                formality_level="casual",
                response_length="concise",
            )
        )
        # Preset wins
        assert "professional" in bv.lower()
        assert fl == "formal"
        assert rl == "standard"

    def test_all_presets_exist(self):
        """All documented presets are defined in _TONE_PRESETS."""
        assert set(_TONE_PRESETS.keys()) == {
            "professional", "friendly", "casual", "expert",
        }

    def test_each_preset_has_required_keys(self):
        """Every preset maps all three fields."""
        for name, preset in _TONE_PRESETS.items():
            assert "brand_voice" in preset, f"{name} missing brand_voice"
            assert "formality_level" in preset, f"{name} missing formality_level"
            assert "response_length" in preset, f"{name} missing response_length"


class TestPreferencesDocumentField:
    """B3: response_tone_preset field exists on PreferencesDocument."""

    def test_field_exists_with_correct_default(self):
        """response_tone_preset is an optional field defaulting to None."""
        from src.multi_tenant.cosmos_schema import PreferencesDocument

        fields = PreferencesDocument.model_fields
        assert "response_tone_preset" in fields
        assert fields["response_tone_preset"].default is None
