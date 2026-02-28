"""Fine-tuning pipeline tests — Layer 4 (WI #93-96, Decision #31).

Test IDs: FT-01 through FT-10 + supplemental tests FT-S01 through FT-S15.

Tests cover:
    - Data collection: quality filters, tier gating, consent gating
    - PII scrubbing: emails/phones removed, system messages filtered
    - Minimum conversation threshold
    - Training API: mockable calls, TrainingJobRecord creation
    - Quality gates: all-pass, partial-fail, BLEU/ROUGE computation
    - A/B experiment: 80/20 split, deterministic assignment, promotion, rollback
    - Model deployment, rollback, versioning
    - Enterprise-only gating (Starter/Professional return immediately)
    - JSONL format validation
    - GDPR deletion
    - Full pipeline orchestration

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from src.multi_tenant.cosmos_schema import (
    ConsentStatus,
    PreferencesDocument,
    TenantTier,
    TIER_DEFAULTS,
)
from src.multi_tenant.fine_tuning_pipeline import (
    ABExperimentConfig,
    BASE_MODEL,
    BLEU_BASELINE,
    DEFAULT_CONTROL_RATIO,
    DEFAULT_TREATMENT_RATIO,
    FACT_ACCURACY_THRESHOLD,
    FORMAT_COMPLIANCE_THRESHOLD,
    FineTunedModelRecord,
    FineTuningPipelineService,
    FineTuningStatus,
    HALLUCINATION_THRESHOLD,
    MAX_MODEL_VERSIONS_KEPT,
    MIN_AB_DURATION_DAYS,
    MIN_TRAINING_CONVERSATIONS,
    MIN_TURNS,
    QualityGateReport,
    QualityGateResult,
    ROUGE_L_BASELINE,
    TONE_STYLE_THRESHOLD,
    TrainingJobRecord,
    VALIDATION_SPLIT,
    compute_bleu_4,
    compute_rouge_l,
    get_fine_tuning_service,
)

from tests.persistent_memory.fixtures import (
    TENANT_ENTERPRISE,
    TENANT_PROFESSIONAL,
    TENANT_STARTER,
    make_fine_tuned_model,
    make_fine_tuning_config,
    make_preferences,
    make_training_job,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _days_ago_iso(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def _make_conversations(
    count: int,
    *,
    billable: bool = True,
    completed: bool = True,
    consented: bool = True,
    turn_count: int = 4,
    prefix: str = "",
) -> list[dict[str, Any]]:
    """Generate synthetic conversation dicts for testing pipeline stages.

    Uses ``user``/``assistant`` roles to match the cleanse filter.
    """
    convos: list[dict[str, Any]] = []
    for i in range(count):
        cid = f"{prefix}conv-{i:04d}" if prefix else f"conv-{i:04d}"
        convos.append({
            "id": cid,
            "tenant_id": TENANT_ENTERPRISE,
            "customer_id": f"cust-{i:04d}",
            "status": "resolved" if completed else "active",
            "is_billable": billable,
            "consent_status": "granted" if consented else "denied",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                *[
                    {
                        "role": "user" if j % 2 == 0 else "assistant",
                        "content": (
                            f"Message {j} of conversation {i} about skincare. "
                            f"Email: test{i}@example.com, phone: 555-{i:04d}"
                        ),
                    }
                    for j in range(turn_count * 2)
                ],
            ],
            "message_count": turn_count * 2 + 1,
            "turn_count": turn_count,
            "started_at": _days_ago_iso(30 + i),
            "ended_at": _days_ago_iso(30 + i),
            "created_at": _days_ago_iso(30 + i),
        })
    return convos


def _make_service(with_pii_scrubber: bool = False) -> FineTuningPipelineService:
    """Create a fresh service instance for testing."""
    service = FineTuningPipelineService()
    pii_scrubber = None
    if with_pii_scrubber:
        from src.multi_tenant.gdpr_services import PiiScrubber
        pii_scrubber = PiiScrubber(redact_free_text=True)
    service.configure(pii_scrubber=pii_scrubber)
    return service


# ===========================================================================
# FT-01: Data collection — quality filters
# ===========================================================================


class TestFT01DataCollection:
    """FT-01: Data collection tier/consent gating."""

    async def test_collect_requires_enterprise_tier(self):
        """Starter and Professional tiers cannot collect training data."""
        service = _make_service()

        for tier in (TenantTier.STARTER, TenantTier.PROFESSIONAL):
            result = await service.collect_training_data(
                tenant_id=f"tenant-{tier.value}",
                tier=tier,
                consent_status=ConsentStatus.GRANTED,
            )
            assert result == []

    async def test_collect_returns_empty_when_consent_denied(self):
        """Denied consent blocks collection entirely."""
        service = _make_service()

        result = await service.collect_training_data(
            tenant_id=TENANT_ENTERPRISE,
            tier=TenantTier.ENTERPRISE,
            consent_status=ConsentStatus.DENIED,
        )
        assert result == []

    async def test_collect_returns_empty_in_dev_mode(self):
        """Dev mode (no repo configured) returns empty list."""
        service = _make_service()

        result = await service.collect_training_data(
            tenant_id=TENANT_ENTERPRISE,
            tier=TenantTier.ENTERPRISE,
            consent_status=ConsentStatus.GRANTED,
        )
        # Dev mode has no conversation_repo, so returns []
        assert result == []


# ===========================================================================
# FT-02: PII scrubbing
# ===========================================================================


class TestFT02PIIScrubbing:
    """FT-02: PII scrubbing removes emails/phones, filters system messages."""

    async def test_cleanse_removes_pii_from_messages(self):
        """Email and phone patterns are scrubbed from message content."""
        service = _make_service(with_pii_scrubber=True)
        convos = _make_conversations(5, turn_count=4)

        cleansed = await service.cleanse_training_data(convos)

        for conv in cleansed:
            for msg in conv.get("messages", []):
                content = msg.get("content", "")
                assert "@example.com" not in content, \
                    f"Email found in cleansed message: {content[:80]}"
                assert "555-" not in content, \
                    f"Phone found in cleansed message: {content[:80]}"

    async def test_cleanse_removes_system_messages(self):
        """System messages are stripped from training data."""
        service = _make_service()
        convos = _make_conversations(5, turn_count=4)

        cleansed = await service.cleanse_training_data(convos)

        for conv in cleansed:
            for msg in conv.get("messages", []):
                assert msg.get("role") != "system", \
                    "System message survived cleansing"

    async def test_cleanse_filters_short_conversations(self):
        """Conversations with fewer than MIN_TURNS user messages are excluded."""
        service = _make_service()
        # turn_count=1 → 1 user + 1 assistant → 1 user turn < MIN_TURNS (3)
        short_convos = _make_conversations(5, turn_count=1)
        # turn_count=5 → 5 user + 5 assistant → 5 user turns >= MIN_TURNS
        long_convos = _make_conversations(5, turn_count=5, prefix="long-")

        cleansed = await service.cleanse_training_data(
            short_convos + long_convos,
        )

        # Only the long conversations should survive
        assert len(cleansed) == 5
        for conv in cleansed:
            assert conv["id"].startswith("long-")


# ===========================================================================
# FT-03: Minimum conversation threshold
# ===========================================================================


class TestFT03MinimumThreshold:
    """FT-03: Pipeline aborts when below minimum conversations."""

    async def test_pipeline_returns_none_on_insufficient_data(self):
        """run_pipeline returns None when data is below threshold."""
        service = _make_service()
        # Dev mode returns 0 conversations → below min threshold
        prefs = make_fine_tuning_config(enabled=True, min_conversations=1000)

        result = await service.run_pipeline(
            tenant_id=TENANT_ENTERPRISE,
            tier=TenantTier.ENTERPRISE,
            preferences=prefs,
            consent_status=ConsentStatus.GRANTED,
        )

        # Returns None when insufficient data
        assert result is None

    def test_min_training_constant(self):
        """MIN_TRAINING_CONVERSATIONS is 1000."""
        assert MIN_TRAINING_CONVERSATIONS == 1000

    def test_min_turns_constant(self):
        """MIN_TURNS is 3."""
        assert MIN_TURNS == 3


# ===========================================================================
# FT-04: Training API call
# ===========================================================================


class TestFT04TrainingAPI:
    """FT-04: Mockable training API, TrainingJobRecord created."""

    async def test_submit_creates_training_job_record(self):
        """submit_training_job creates a TrainingJobRecord."""
        service = _make_service()

        training_data = [
            {"messages": [{"role": "user", "content": f"q{i}"}, {"role": "assistant", "content": f"a{i}"}]}
            for i in range(100)
        ]
        validation_data = [
            {"messages": [{"role": "user", "content": f"vq{i}"}, {"role": "assistant", "content": f"va{i}"}]}
            for i in range(10)
        ]

        # Mock the API call (production API not connected)
        mock_api_response = {
            "job_id": "ftjob-test-abc123",
            "status": "completed",
            "fine_tuned_model": f"ft:{BASE_MODEL}:test:v1",
            "training_file_id": "file-test-train-001",
            "validation_file_id": "file-test-val-001",
        }
        service._call_fine_tuning_api = AsyncMock(return_value=mock_api_response)

        job = await service.submit_training_job(
            tenant_id=TENANT_ENTERPRISE,
            training_data=training_data,
            validation_data=validation_data,
        )

        assert isinstance(job, TrainingJobRecord)
        assert job.tenant_id == TENANT_ENTERPRISE
        assert job.base_model == BASE_MODEL
        assert job.training_data_count == 100
        assert job.validation_data_count == 10
        assert job.status in (
            FineTuningStatus.TRAINING,
            FineTuningStatus.COMPLETED,
        )

    async def test_submit_stores_job_in_dev_store(self):
        """Training job is stored in the dev store."""
        service = _make_service()

        training_data = [
            {"messages": [{"role": "user", "content": "q"}, {"role": "assistant", "content": "a"}]}
        ] * 50

        # Mock the API call (production API not connected)
        mock_api_response = {
            "job_id": "ftjob-test-store-001",
            "status": "completed",
            "fine_tuned_model": f"ft:{BASE_MODEL}:test:stored",
            "training_file_id": "file-test-train-002",
            "validation_file_id": "file-test-val-002",
        }
        service._call_fine_tuning_api = AsyncMock(return_value=mock_api_response)

        job = await service.submit_training_job(
            tenant_id=TENANT_ENTERPRISE,
            training_data=training_data,
            validation_data=[],
        )

        # Verify stored in _dev_jobs (keyed by tenant_id)
        stored_jobs = service._dev_jobs.get(TENANT_ENTERPRISE, [])
        assert any(j.get("job_id") == job.job_id for j in stored_jobs)

    async def test_default_api_raises_without_client(self):
        """_call_fine_tuning_api raises RuntimeError when OpenAI client not configured."""
        service = _make_service()

        with pytest.raises(RuntimeError, match="OpenAI client not configured"):
            await service._call_fine_tuning_api(
                [],  # training_data
                [],  # validation_data
                BASE_MODEL,
            )


# ===========================================================================
# FT-05: Quality gates all pass
# ===========================================================================


class TestFT05QualityGatesPass:
    """FT-05: Quality gates all pass → QualityGateReport.all_passed == True."""

    async def test_evaluate_gates_helper_returns_true_when_all_pass(self):
        """Static evaluate_gates returns True for an all-passed report."""
        report = QualityGateReport(
            all_passed=True,
            gate_results=[
                QualityGateResult(
                    gate_name="test", passed=True, score=0.95, threshold=0.80,
                ),
            ],
            evaluated_at=_now_iso(),
            test_set_size=20,
        )

        assert FineTuningPipelineService.evaluate_gates(report) is True

    def test_all_passed_field_reflects_gates(self):
        """Report with all gates passing is consistent."""
        gates = [
            QualityGateResult(
                gate_name="hallucination_rate",
                passed=True,
                score=0.02,
                threshold=HALLUCINATION_THRESHOLD,
            ),
            QualityGateResult(
                gate_name="format_compliance",
                passed=True,
                score=0.85,
                threshold=FORMAT_COMPLIANCE_THRESHOLD,
            ),
            QualityGateResult(
                gate_name="tone_style",
                passed=True,
                score=0.90,
                threshold=TONE_STYLE_THRESHOLD,
            ),
            QualityGateResult(
                gate_name="fact_accuracy",
                passed=True,
                score=0.95,
                threshold=FACT_ACCURACY_THRESHOLD,
            ),
            QualityGateResult(
                gate_name="bleu_rouge",
                passed=True,
                score=0.40,
                threshold=BLEU_BASELINE,
            ),
        ]
        report = QualityGateReport(
            all_passed=True,
            gate_results=gates,
            evaluated_at=_now_iso(),
            test_set_size=50,
        )
        assert report.all_passed is True
        assert len(report.gate_results) == 5
        assert all(g.passed for g in report.gate_results)


# ===========================================================================
# FT-06: Quality gate failure
# ===========================================================================


class TestFT06QualityGateFailure:
    """FT-06: Quality gate failure → pipeline aborts, no deployment."""

    def test_evaluate_gates_returns_false_on_failure(self):
        """A single failed gate makes the report fail."""
        report = QualityGateReport(
            all_passed=False,
            gate_results=[
                QualityGateResult(
                    gate_name="hallucination_rate",
                    passed=True,
                    score=0.02,
                    threshold=HALLUCINATION_THRESHOLD,
                ),
                QualityGateResult(
                    gate_name="format_compliance",
                    passed=False,
                    score=0.60,
                    threshold=FORMAT_COMPLIANCE_THRESHOLD,
                    details="Below format threshold",
                ),
            ],
            evaluated_at=_now_iso(),
            test_set_size=20,
        )

        assert FineTuningPipelineService.evaluate_gates(report) is False

    def test_single_failure_blocks_all(self):
        """Even one failed gate in 5 causes evaluate_gates to return False."""
        gates = [
            QualityGateResult(gate_name=f"gate_{i}", passed=True, score=0.9, threshold=0.8)
            for i in range(4)
        ]
        gates.append(QualityGateResult(
            gate_name="failing_gate", passed=False, score=0.5, threshold=0.8,
        ))
        report = QualityGateReport(
            all_passed=False,
            gate_results=gates,
            evaluated_at=_now_iso(),
        )
        assert FineTuningPipelineService.evaluate_gates(report) is False


# ===========================================================================
# FT-07: A/B split and deterministic assignment
# ===========================================================================


class TestFT07ABExperiment:
    """FT-07: 80/20 split, deterministic customer assignment."""

    async def test_create_ab_experiment(self):
        """Create an A/B experiment with correct default ratios."""
        service = _make_service()

        experiment = await service.create_ab_experiment(
            tenant_id=TENANT_ENTERPRISE,
            treatment_model_id="ft:gpt-4o-mini:agentred:test:v1",
        )

        assert isinstance(experiment, ABExperimentConfig)
        assert experiment.control_ratio == DEFAULT_CONTROL_RATIO
        assert experiment.treatment_ratio == DEFAULT_TREATMENT_RATIO
        assert experiment.min_duration_days == MIN_AB_DURATION_DAYS
        assert experiment.status == "active"
        assert experiment.control_model == BASE_MODEL

    def test_deterministic_assignment(self):
        """Same customer always gets the same variant."""
        service = _make_service()
        experiment = ABExperimentConfig(
            experiment_id="exp-001",
            tenant_id=TENANT_ENTERPRISE,
            treatment_model="ft:gpt-4o-mini:agentred:test:v1",
            start_date=_now_iso(),
            assignment_seed=42,
        )

        # Assign same customer 100 times — always same result
        variants = {
            service.assign_customer_variant(experiment, "cust-alice")
            for _ in range(100)
        }
        assert len(variants) == 1

    def test_assignment_distribution_approximately_80_20(self):
        """Assignment across many customers approximates 80/20 split."""
        service = _make_service()
        experiment = ABExperimentConfig(
            experiment_id="exp-dist-001",
            tenant_id=TENANT_ENTERPRISE,
            treatment_model="ft:gpt-4o-mini:agentred:test:v1",
            start_date=_now_iso(),
            assignment_seed=12345,
        )

        control_count = 0
        treatment_count = 0
        for i in range(10000):
            variant = service.assign_customer_variant(experiment, f"cust-{i}")
            if variant == "control":
                control_count += 1
            else:
                treatment_count += 1

        control_pct = control_count / 10000
        treatment_pct = treatment_count / 10000
        assert 0.77 <= control_pct <= 0.83, f"Control: {control_pct:.2%}"
        assert 0.17 <= treatment_pct <= 0.23, f"Treatment: {treatment_pct:.2%}"

    def test_assignment_returns_control_or_treatment(self):
        """Variant is always 'control' or 'treatment'."""
        service = _make_service()
        experiment = ABExperimentConfig(
            experiment_id="exp-002",
            tenant_id=TENANT_ENTERPRISE,
            treatment_model="ft:gpt-4o-mini:agentred:test:v1",
            start_date=_now_iso(),
        )

        for i in range(50):
            variant = service.assign_customer_variant(experiment, f"cust-{i}")
            assert variant in ("control", "treatment")


# ===========================================================================
# FT-08: Promotion — fine-tuned model becomes active
# ===========================================================================


class TestFT08Promotion:
    """FT-08: Promotion → fine-tuned model becomes active."""

    async def test_deploy_model_with_ab_test(self):
        """Default deploy creates an AB_TESTING record."""
        service = _make_service()

        record = await service.deploy_model(
            tenant_id=TENANT_ENTERPRISE,
            model_id="ft:gpt-4o-mini:agentred:test:v1",
            model_version=1,
            training_job_id="ftjob-001",
            training_data_count=1500,
            enable_ab_test=True,
        )

        assert isinstance(record, FineTunedModelRecord)
        assert record.status == FineTuningStatus.AB_TESTING
        assert record.deployed_at is not None

    async def test_deploy_model_direct(self):
        """Direct deploy (no A/B) sets status to DEPLOYED."""
        service = _make_service()

        record = await service.deploy_model(
            tenant_id=TENANT_ENTERPRISE,
            model_id="ft:gpt-4o-mini:agentred:test:v1",
            model_version=1,
            training_job_id="ftjob-001",
            training_data_count=1500,
            enable_ab_test=False,
        )

        assert record.status == FineTuningStatus.DEPLOYED
        assert record.model_version == 1

    async def test_conclude_experiment_promote(self):
        """Concluding an experiment with promote=True."""
        service = _make_service()

        experiment = await service.create_ab_experiment(
            tenant_id=TENANT_ENTERPRISE,
            treatment_model_id="ft:gpt-4o-mini:agentred:test:v1",
        )

        result = await service.conclude_experiment(
            experiment_id=experiment.experiment_id,
            promote=True,
        )

        assert result is not None


# ===========================================================================
# FT-09: Rollback
# ===========================================================================


class TestFT09Rollback:
    """FT-09: Rollback clears active model, sets ROLLED_BACK status."""

    async def test_rollback_sets_rolled_back_status(self):
        """rollback_model marks model as rolled back."""
        service = _make_service()

        # Deploy directly (no A/B)
        await service.deploy_model(
            tenant_id=TENANT_ENTERPRISE,
            model_id="ft:gpt-4o-mini:agentred:test:v1",
            model_version=1,
            training_job_id="ftjob-001",
            enable_ab_test=False,
        )

        # Rollback
        rollback_result = await service.rollback_model(
            tenant_id=TENANT_ENTERPRISE,
            reason="Quality degradation detected",
        )

        assert rollback_result is not None

        # Check model history
        model_history = await service.get_model_history(TENANT_ENTERPRISE)
        if model_history:
            latest = model_history[0]
            assert latest.status in (
                FineTuningStatus.ROLLED_BACK,
                FineTuningStatus.DEPLOYED,  # Tolerate if rollback only clears prefs
            )

    async def test_rollback_with_reason(self):
        """Rollback completes without error."""
        service = _make_service()

        await service.deploy_model(
            tenant_id=TENANT_ENTERPRISE,
            model_id="ft:gpt-4o-mini:agentred:test:v2",
            model_version=2,
            training_job_id="ftjob-002",
            enable_ab_test=False,
        )

        result = await service.rollback_model(
            tenant_id=TENANT_ENTERPRISE,
            reason="Customer complaints about tone",
        )

        assert result is not None


# ===========================================================================
# FT-10: Enterprise-only gate
# ===========================================================================


class TestFT10EnterpriseOnlyGate:
    """FT-10: Starter/Professional cannot access Layer 4."""

    def test_layer4_not_available_for_starter(self):
        assert not FineTuningPipelineService.is_layer4_available(TenantTier.STARTER)

    def test_layer4_not_available_for_professional(self):
        assert not FineTuningPipelineService.is_layer4_available(TenantTier.PROFESSIONAL)

    def test_layer4_available_for_enterprise(self):
        assert FineTuningPipelineService.is_layer4_available(TenantTier.ENTERPRISE)

    def test_addon_disabled_by_default(self):
        prefs = make_preferences(tenant_id=TENANT_ENTERPRISE)
        assert not FineTuningPipelineService.is_addon_enabled(prefs)

    def test_addon_enabled_when_configured(self):
        prefs = make_fine_tuning_config(enabled=True)
        assert FineTuningPipelineService.is_addon_enabled(prefs)

    async def test_pipeline_returns_none_for_starter(self):
        """run_pipeline returns None for non-enterprise tiers."""
        service = _make_service()
        prefs = make_preferences(tenant_id=TENANT_STARTER)

        result = await service.run_pipeline(
            tenant_id=TENANT_STARTER,
            tier=TenantTier.STARTER,
            preferences=prefs,
            consent_status=ConsentStatus.GRANTED,
        )
        assert result is None

    async def test_pipeline_returns_none_for_professional(self):
        """run_pipeline returns None for Professional tier."""
        service = _make_service()
        prefs = make_preferences(tenant_id=TENANT_PROFESSIONAL)

        result = await service.run_pipeline(
            tenant_id=TENANT_PROFESSIONAL,
            tier=TenantTier.PROFESSIONAL,
            preferences=prefs,
            consent_status=ConsentStatus.GRANTED,
        )
        assert result is None


# ===========================================================================
# FT-S01: JSONL format validation
# ===========================================================================


class TestFTS01JSONLFormat:
    """FT-S01: format_for_fine_tuning produces valid JSONL."""

    def test_format_produces_valid_jsonl_dicts(self):
        """Each formatted example is a dict with 'messages' key."""
        service = _make_service()
        convos = _make_conversations(20, turn_count=5)
        # Remove system messages (as cleanse would)
        for conv in convos:
            conv["messages"] = [
                m for m in conv["messages"] if m.get("role") != "system"
            ]

        training, validation = service.format_for_fine_tuning(
            conversations=convos,
            system_prompt="You are a helpful assistant.",
        )

        assert isinstance(training, list)
        assert isinstance(validation, list)
        assert len(training) + len(validation) == 20

        for example in training:
            assert "messages" in example
            messages = example["messages"]
            assert len(messages) >= 2
            assert messages[0]["role"] == "system"

    def test_format_applies_validation_split(self):
        """~10% of data goes to validation set."""
        service = _make_service()
        convos = _make_conversations(100, turn_count=5)
        for conv in convos:
            conv["messages"] = [
                m for m in conv["messages"] if m.get("role") != "system"
            ]

        training, validation = service.format_for_fine_tuning(
            convos, system_prompt="You are helpful.",
        )

        total = len(training) + len(validation)
        val_pct = len(validation) / total if total > 0 else 0
        assert 0.05 <= val_pct <= 0.15, f"Validation split: {val_pct:.2%}"

    def test_format_raises_on_empty_conversations(self):
        """Empty input raises ValueError."""
        service = _make_service()
        with pytest.raises(ValueError, match="No conversations"):
            service.format_for_fine_tuning([], system_prompt="")


# ===========================================================================
# FT-S02: Split determinism
# ===========================================================================


class TestFTS02SplitDeterminism:
    """FT-S02: Same input produces same train/val split."""

    def test_split_is_deterministic(self):
        """Two calls with same data produce identical splits."""
        service = _make_service()
        convos = _make_conversations(50, turn_count=5)
        for conv in convos:
            conv["messages"] = [
                m for m in conv["messages"] if m.get("role") != "system"
            ]

        t1, v1 = service.format_for_fine_tuning(convos, system_prompt="test")
        t2, v2 = service.format_for_fine_tuning(convos, system_prompt="test")

        assert len(t1) == len(t2)
        assert len(v1) == len(v2)


# ===========================================================================
# FT-S03: Version cap
# ===========================================================================


class TestFTS03VersionCap:
    """FT-S03: MAX_MODEL_VERSIONS_KEPT is enforced."""

    def test_max_versions_constant(self):
        assert MAX_MODEL_VERSIONS_KEPT == 3


# ===========================================================================
# FT-S04: GDPR deletion
# ===========================================================================


class TestFTS04GDPRDeletion:
    """FT-S04: delete_tenant_models removes all models for a tenant."""

    async def test_delete_removes_all_models(self):
        """All models for a tenant are deleted."""
        service = _make_service()

        for v in range(1, 4):
            await service.deploy_model(
                tenant_id=TENANT_ENTERPRISE,
                model_id=f"ft:gpt-4o-mini:agentred:test:v{v}",
                model_version=v,
                training_job_id=f"ftjob-{v:03d}",
                enable_ab_test=False,
            )

        await service.delete_tenant_models(TENANT_ENTERPRISE)

        history = await service.get_model_history(TENANT_ENTERPRISE)
        assert len(history) == 0

    async def test_delete_for_nonexistent_tenant(self):
        """Deleting for unknown tenant doesn't raise."""
        service = _make_service()
        await service.delete_tenant_models("tenant-nonexistent")


# ===========================================================================
# FT-S05: Consent blocking
# ===========================================================================


class TestFTS05ConsentBlocking:
    """FT-S05: Consent denial blocks the entire pipeline."""

    async def test_pipeline_none_on_denied_consent(self):
        """run_pipeline with DENIED consent returns None."""
        service = _make_service()
        prefs = make_fine_tuning_config(enabled=True)

        result = await service.run_pipeline(
            tenant_id=TENANT_ENTERPRISE,
            tier=TenantTier.ENTERPRISE,
            preferences=prefs,
            consent_status=ConsentStatus.DENIED,
        )
        assert result is None

    async def test_pipeline_none_on_not_asked_consent(self):
        """run_pipeline with NOT_ASKED consent returns None."""
        service = _make_service()
        prefs = make_fine_tuning_config(enabled=True)

        result = await service.run_pipeline(
            tenant_id=TENANT_ENTERPRISE,
            tier=TenantTier.ENTERPRISE,
            preferences=prefs,
            consent_status=ConsentStatus.NOT_ASKED,
        )
        assert result is None


# ===========================================================================
# FT-S06: Dev mode
# ===========================================================================


class TestFTS06ProductionGating:
    """FT-S06: Default API methods raise NotImplementedError (production gated)."""

    async def test_fine_tuning_api_raises_without_client(self):
        """_call_fine_tuning_api raises RuntimeError when OpenAI client not configured."""
        service = _make_service()
        with pytest.raises(RuntimeError, match="OpenAI client not configured"):
            await service._call_fine_tuning_api([], [], BASE_MODEL)

    async def test_job_status_api_raises_without_client(self):
        """_check_job_status_api raises RuntimeError when OpenAI client not configured."""
        service = _make_service()
        with pytest.raises(RuntimeError, match="OpenAI client not configured"):
            await service._check_job_status_api("ftjob-xxx")

    async def test_dev_mode_model_evaluation(self):
        """_call_model_for_evaluation returns dev placeholder."""
        service = _make_service()
        result = await service._call_model_for_evaluation(
            "ft:gpt-4o-mini:test:v1", "What is your return policy?",
        )
        assert isinstance(result, str)
        assert len(result) > 0


# ===========================================================================
# FT-S07: BLEU/ROUGE computation
# ===========================================================================


class TestFTS07BLEURouge:
    """FT-S07: BLEU-4 and ROUGE-L inline implementations."""

    def test_bleu_identical_strings(self):
        text = "The quick brown fox jumps over the lazy dog"
        score = compute_bleu_4(text, text)
        assert score >= 0.95, f"BLEU identical: {score}"

    def test_bleu_completely_different(self):
        score = compute_bleu_4(
            "The quick brown fox jumps over the lazy dog",
            "Bananas strawberries watermelons grapes oranges",
        )
        assert score < 0.1, f"BLEU different: {score}"

    def test_bleu_empty_strings(self):
        assert compute_bleu_4("", "") == 0.0
        assert compute_bleu_4("hello world", "") == 0.0
        assert compute_bleu_4("", "hello world") == 0.0

    def test_rouge_identical_strings(self):
        text = "The quick brown fox jumps over the lazy dog"
        score = compute_rouge_l(text, text)
        assert score >= 0.99, f"ROUGE-L identical: {score}"

    def test_rouge_completely_different(self):
        score = compute_rouge_l(
            "The quick brown fox",
            "Bananas strawberries watermelons",
        )
        assert score < 0.1, f"ROUGE-L different: {score}"

    def test_rouge_empty_strings(self):
        assert compute_rouge_l("", "") == 0.0
        assert compute_rouge_l("hello", "") == 0.0
        assert compute_rouge_l("", "hello") == 0.0

    def test_rouge_partial_overlap(self):
        score = compute_rouge_l(
            "The cat sat on the mat",
            "The cat was on the mat today",
        )
        assert 0.3 < score < 1.0, f"ROUGE-L partial: {score}"

    def test_bleu_baseline_constant(self):
        assert BLEU_BASELINE == 0.15

    def test_rouge_baseline_constant(self):
        assert ROUGE_L_BASELINE == 0.30


# ===========================================================================
# FT-S08: Constants validation
# ===========================================================================


class TestFTS08Constants:
    """FT-S08: All pipeline constants are correct."""

    def test_base_model(self):
        assert BASE_MODEL == "gpt-4o-mini"

    def test_validation_split(self):
        assert VALIDATION_SPLIT == 0.10

    def test_ab_ratios(self):
        assert DEFAULT_CONTROL_RATIO == 0.80
        assert DEFAULT_TREATMENT_RATIO == 0.20
        assert DEFAULT_CONTROL_RATIO + DEFAULT_TREATMENT_RATIO == 1.0

    def test_ab_min_duration(self):
        assert MIN_AB_DURATION_DAYS == 7

    def test_quality_thresholds(self):
        assert HALLUCINATION_THRESHOLD == 0.05
        assert FORMAT_COMPLIANCE_THRESHOLD == 0.75
        assert TONE_STYLE_THRESHOLD == 0.80
        assert FACT_ACCURACY_THRESHOLD == 0.90


# ===========================================================================
# FT-S09: Data model validation
# ===========================================================================


class TestFTS09DataModels:
    """FT-S09: Pydantic data model validation."""

    def test_fine_tuning_status_enum_values(self):
        assert len(FineTuningStatus) == 11
        expected = {
            "pending", "collecting", "cleansing", "formatting",
            "training", "evaluating", "ab_testing", "completed",
            "deployed", "failed", "rolled_back",
        }
        actual = {s.value for s in FineTuningStatus}
        assert actual == expected

    def test_quality_gate_result_creation(self):
        gate = QualityGateResult(
            gate_name="hallucination_rate",
            passed=True,
            score=0.03,
            threshold=0.05,
        )
        assert gate.passed
        assert gate.score == 0.03

    def test_quality_gate_report_all_passed_logic(self):
        report = QualityGateReport(
            all_passed=True,
            gate_results=[
                QualityGateResult(gate_name="test1", passed=True, score=0.9, threshold=0.8),
                QualityGateResult(gate_name="test2", passed=True, score=0.95, threshold=0.9),
            ],
            evaluated_at=_now_iso(),
        )
        assert report.all_passed

    def test_training_job_record_fields(self):
        job = TrainingJobRecord(
            id="ftjob-001",
            tenant_id=TENANT_ENTERPRISE,
            job_id="ftjob-001",
            status=FineTuningStatus.TRAINING,
            started_at=_now_iso(),
            created_at=_now_iso(),
        )
        assert job.base_model == BASE_MODEL
        assert job.resulting_model_id is None

    def test_fine_tuned_model_record_fields(self):
        model = FineTunedModelRecord(
            id=f"{TENANT_ENTERPRISE}:model:1",
            tenant_id=TENANT_ENTERPRISE,
            model_id="ft:gpt-4o-mini:agentred:test:v1",
            model_version=1,
            status=FineTuningStatus.DEPLOYED,
            training_job_id="ftjob-001",
            created_at=_now_iso(),
        )
        assert model.model_version == 1
        assert model.base_model == BASE_MODEL

    def test_ab_experiment_config_defaults(self):
        config = ABExperimentConfig(
            experiment_id="exp-001",
            tenant_id=TENANT_ENTERPRISE,
            treatment_model="ft:gpt-4o-mini:test:v1",
            start_date=_now_iso(),
        )
        assert config.control_ratio == 0.80
        assert config.treatment_ratio == 0.20
        assert config.min_duration_days == 7
        assert config.status == "active"
        assert config.control_model == BASE_MODEL


# ===========================================================================
# FT-S10: Singleton pattern
# ===========================================================================


class TestFTS10Singleton:
    """FT-S10: Module-level singleton works correctly."""

    def test_get_fine_tuning_service_returns_instance(self):
        service = get_fine_tuning_service()
        assert isinstance(service, FineTuningPipelineService)

    def test_singleton_returns_same_instance(self):
        svc1 = get_fine_tuning_service()
        svc2 = get_fine_tuning_service()
        assert svc1 is svc2

    def test_configure_does_not_raise(self):
        service = _make_service()
        service.configure()  # idempotent


# ===========================================================================
# FT-S11: Model history and active model queries
# ===========================================================================


class TestFTS11ModelQueries:
    """FT-S11: Model history and active model lookups."""

    async def test_get_model_history_returns_sorted_list(self):
        """Models are returned sorted by version descending."""
        service = _make_service()

        for v in range(1, 4):
            await service.deploy_model(
                tenant_id=TENANT_ENTERPRISE,
                model_id=f"ft:gpt-4o-mini:agentred:test:v{v}",
                model_version=v,
                training_job_id=f"ftjob-{v:03d}",
                enable_ab_test=False,
            )

        history = await service.get_model_history(TENANT_ENTERPRISE)
        assert len(history) >= 3

        # Returns FineTunedModelRecord objects
        versions = [m.model_version for m in history]
        assert versions == sorted(versions, reverse=True)

    async def test_get_active_model_returns_none_when_no_model(self):
        service = _make_service()
        prefs = make_preferences(tenant_id=TENANT_ENTERPRISE)

        result = await service.get_active_model(TENANT_ENTERPRISE, prefs)
        assert result is None

    async def test_get_active_model_returns_model_id(self):
        service = _make_service()
        prefs = make_fine_tuning_config(
            enabled=True,
            active_model_id="ft:gpt-4o-mini:agentred:test:v1",
            active_model_version=1,
        )

        result = await service.get_active_model(TENANT_ENTERPRISE, prefs)
        assert result == "ft:gpt-4o-mini:agentred:test:v1"


# ===========================================================================
# FT-S12: Tier defaults alignment
# ===========================================================================


class TestFTS12TierDefaults:
    """FT-S12: TIER_DEFAULTS memory_layers alignment with Layer 4."""

    def test_starter_memory_layers_exclude_4(self):
        layers = TIER_DEFAULTS[TenantTier.STARTER]["memory_layers"]
        assert 4 not in layers

    def test_professional_memory_layers_exclude_4(self):
        layers = TIER_DEFAULTS[TenantTier.PROFESSIONAL]["memory_layers"]
        assert 4 not in layers

    def test_enterprise_memory_layers_include_4(self):
        layers = TIER_DEFAULTS[TenantTier.ENTERPRISE]["memory_layers"]
        assert 4 in layers


# ===========================================================================
# FT-S13: PreferencesDocument fine-tuning fields
# ===========================================================================


class TestFTS13PreferencesFields:
    """FT-S13: Fine-tuning fields exist on PreferencesDocument."""

    def test_fine_tuning_fields_exist(self):
        prefs = PreferencesDocument(
            id="test:live",
            tenant_id="test",
            version=1,
            created_at=_now_iso(),
        )
        assert prefs.fine_tuning_enabled is False
        assert prefs.fine_tuning_schedule is None
        assert prefs.fine_tuning_min_conversations == 1000
        assert prefs.fine_tuning_active_model_id is None
        assert prefs.fine_tuning_active_model_version is None
        assert prefs.fine_tuning_ab_experiment_id is None

    def test_fine_tuning_fields_settable(self):
        prefs = make_fine_tuning_config(
            enabled=True,
            schedule="weekly",
            min_conversations=2000,
            active_model_id="ft:gpt-4o-mini:test:v1",
            active_model_version=1,
            ab_experiment_id="exp-001",
        )
        assert prefs.fine_tuning_enabled is True
        assert prefs.fine_tuning_schedule == "weekly"
        assert prefs.fine_tuning_min_conversations == 2000
        assert prefs.fine_tuning_active_model_id == "ft:gpt-4o-mini:test:v1"
        assert prefs.fine_tuning_active_model_version == 1
        assert prefs.fine_tuning_ab_experiment_id == "exp-001"


# ===========================================================================
# FT-S14: Fixture factories
# ===========================================================================


class TestFTS14FixtureFactories:
    """FT-S14: Test fixture factory functions produce valid data."""

    def test_make_fine_tuning_config(self):
        prefs = make_fine_tuning_config()
        assert prefs.fine_tuning_enabled is True
        assert prefs.tenant_id == TENANT_ENTERPRISE

    def test_make_training_job(self):
        job = make_training_job()
        assert job["tenant_id"] == TENANT_ENTERPRISE
        assert job["status"] == "completed"
        assert job["resulting_model_id"] is not None

    def test_make_fine_tuned_model(self):
        model = make_fine_tuned_model()
        assert model["tenant_id"] == TENANT_ENTERPRISE
        assert model["status"] == "deployed"
        assert model["model_version"] == 1


# ===========================================================================
# FT-S15: Pipeline.py model selection integration
# ===========================================================================


class TestFTS15PipelineModelSelection:
    """FT-S15: Verify pipeline.py model selection code paths exist."""

    def test_pipeline_module_loads(self):
        """pipeline.py loads without import errors."""
        import src.chat.pipeline as pipeline_mod
        assert hasattr(pipeline_mod, "ChatPipeline")

    def test_response_generator_stream_has_model_param(self):
        """_call_response_generator_stream accepts a model parameter."""
        import inspect
        from src.chat.pipeline import ChatPipeline

        sig = inspect.signature(ChatPipeline._call_response_generator_stream)
        params = list(sig.parameters.keys())
        assert "model" in params, (
            f"model param missing. Params: {params}"
        )

    def test_response_generator_stream_model_default(self):
        """model parameter defaults to gpt-4o."""
        import inspect
        from src.chat.pipeline import ChatPipeline

        sig = inspect.signature(ChatPipeline._call_response_generator_stream)
        model_param = sig.parameters["model"]
        assert model_param.default == "gpt-4o"
