"""A/B testing framework for conversation quality experiments (SPEC-0621).

Provides a generalized experiment service that allows merchants to run
controlled experiments on conversation configuration — quality thresholds,
system prompt variations, escalation sensitivity, etc.

Key design decisions:
- Customer-level assignment (SHA-256 deterministic hashing, reused from
  fine_tuning_pipeline.py) ensures the same customer always sees the same
  variant within an experiment.
- Experiment lifecycle: draft -> pending_review -> active -> concluded
  (SPEC-0626 editorial review gate).
- Configuration-centric: variants are named configuration overrides
  (not model swaps).

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_CONTROL_RATIO = 0.80
DEFAULT_TREATMENT_RATIO = 0.20
MIN_EXPERIMENT_DURATION_DAYS = 3
MAX_ACTIVE_EXPERIMENTS_PER_TENANT = 3
SUGGESTION_RATE_LIMIT_PER_HOUR = 5


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ExperimentStatus(str, Enum):
    """Experiment lifecycle states (SPEC-0626)."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    ACTIVE = "active"
    PENDING_CONCLUSION = "pending_conclusion"
    CONCLUDED_PROMOTE = "concluded_promote"
    CONCLUDED_ROLLBACK = "concluded_rollback"


# Valid state transitions — key is current state, values are allowed next states
VALID_TRANSITIONS: dict[ExperimentStatus, set[ExperimentStatus]] = {
    ExperimentStatus.DRAFT: {
        ExperimentStatus.PENDING_REVIEW,
    },
    ExperimentStatus.PENDING_REVIEW: {
        ExperimentStatus.ACTIVE,
        ExperimentStatus.DRAFT,  # rejection returns to draft
    },
    ExperimentStatus.ACTIVE: {
        ExperimentStatus.PENDING_CONCLUSION,
    },
    ExperimentStatus.PENDING_CONCLUSION: {
        ExperimentStatus.CONCLUDED_PROMOTE,
        ExperimentStatus.CONCLUDED_ROLLBACK,
        ExperimentStatus.ACTIVE,  # merchant can reject conclusion
    },
    ExperimentStatus.CONCLUDED_PROMOTE: set(),
    ExperimentStatus.CONCLUDED_ROLLBACK: set(),
}


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


class VariantConfig(BaseModel):
    """Configuration overrides for an experiment variant.

    Each key-value pair overrides a field in the tenant's conversation
    configuration.  Supported override keys mirror MerchantQualityConfig
    plus system prompt and escalation fields.
    """

    name: str = Field(description="Variant display name (e.g., 'Stricter QA')")
    description: str = Field(
        default="", description="Human-readable description of what this variant tests"
    )
    config_overrides: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Configuration overrides applied to this variant. "
            "Keys match tenant config fields: quality_threshold, "
            "escalation_threshold, consecutive_low_turns, "
            "enable_quality_feedback, enable_quality_escalation, "
            "system_prompt_suffix, custom_instructions_append, etc."
        ),
    )


class ExperimentConfig(BaseModel):
    """Full configuration for a conversation quality A/B experiment."""

    experiment_id: str = Field(description="Unique experiment identifier")
    tenant_id: str = Field(description="Owning tenant")
    name: str = Field(description="Experiment display name")
    description: str = Field(default="", description="Experiment purpose")
    hypothesis: str = Field(
        default="",
        description="What the experiment aims to prove or disprove",
    )

    # Variants
    control: VariantConfig = Field(
        description="Control variant (current production config)"
    )
    treatment: VariantConfig = Field(
        description="Treatment variant (proposed changes)"
    )
    control_ratio: float = Field(
        default=DEFAULT_CONTROL_RATIO,
        ge=0.05,
        le=0.95,
        description="Fraction of traffic for control (0.05-0.95)",
    )

    # Audience
    audience_mode: str = Field(
        default="all",
        description="Audience selection: 'all', 'percentage', or 'segment'",
    )
    audience_percentage: float = Field(
        default=100.0,
        ge=1.0,
        le=100.0,
        description="Percentage of customers included (when audience_mode='percentage')",
    )
    audience_segment: str | None = Field(
        default=None,
        description="Segment identifier (when audience_mode='segment')",
    )

    # Schedule
    start_date: str | None = Field(
        default=None, description="Experiment start (ISO 8601)"
    )
    end_date: str | None = Field(
        default=None, description="Experiment end (ISO 8601, null = manual)"
    )
    min_duration_days: int = Field(
        default=MIN_EXPERIMENT_DURATION_DAYS,
        ge=1,
        le=90,
        description="Minimum experiment duration before conclusion allowed",
    )

    # State
    status: ExperimentStatus = Field(
        default=ExperimentStatus.DRAFT,
        description="Current lifecycle state",
    )
    assignment_seed: int = Field(
        default=0,
        description="Hash seed for deterministic customer assignment",
    )
    created_at: str = Field(
        default="", description="When the experiment was created (ISO 8601)"
    )
    concluded_at: str | None = Field(
        default=None, description="When the experiment concluded"
    )

    # KPI tracking keys
    metric_keys: list[str] = Field(
        default_factory=lambda: [
            "quality_score",
            "satisfaction",
            "session_length",
            "escalation_rate",
            "conversion_rate",
        ],
        description="Metrics to track for this experiment",
    )

    # AI-generated metadata
    ai_rationale: str = Field(
        default="",
        description="AI explanation of why this experiment was designed this way",
    )
    conclusion_recommendation: str | None = Field(
        default=None,
        description="AI recommendation at conclusion time (promote/rollback + reasoning)",
    )

    @field_validator("audience_mode")
    @classmethod
    def validate_audience_mode(cls, v: str) -> str:
        allowed = {"all", "percentage", "segment"}
        if v not in allowed:
            raise ValueError(f"audience_mode must be one of {allowed}")
        return v

    @property
    def treatment_ratio(self) -> float:
        return round(1.0 - self.control_ratio, 4)


# ---------------------------------------------------------------------------
# Assignment Logic
# ---------------------------------------------------------------------------


def assign_variant(
    experiment: ExperimentConfig,
    customer_id: str,
) -> str:
    """Deterministic customer-level A/B assignment.

    Uses SHA-256 hash of (experiment_id + customer_id + seed) to produce
    a bucket 0-99.  Replicates the algorithm from fine_tuning_pipeline.py.

    Args:
        experiment: Active experiment config.
        customer_id: Customer identifier.

    Returns:
        "control" or "treatment".
    """
    seed_str = (
        f"{experiment.experiment_id}:{customer_id}:"
        f"{experiment.assignment_seed}"
    )
    hash_value = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16)
    bucket = hash_value % 100
    treatment_cutoff = int(experiment.treatment_ratio * 100)

    return "treatment" if bucket < treatment_cutoff else "control"


def get_variant_config(
    experiment: ExperimentConfig,
    variant: str,
) -> VariantConfig:
    """Return the VariantConfig for a given variant name."""
    if variant == "treatment":
        return experiment.treatment
    return experiment.control


# ---------------------------------------------------------------------------
# Experiment Service
# ---------------------------------------------------------------------------


class ExperimentService:
    """Manages A/B experiment lifecycle.

    In production, experiments are stored in the tenant's Cosmos document
    under an ``ab_experiments`` key.  For unit testing, an in-memory store
    is used (pass ``store={}``).
    """

    def __init__(self, store: dict[str, dict[str, Any]] | None = None):
        self._store: dict[str, dict[str, Any]] = store if store is not None else {}

    # -- CRUD ---------------------------------------------------------------

    def create_experiment(
        self,
        tenant_id: str,
        name: str,
        control: VariantConfig,
        treatment: VariantConfig,
        *,
        description: str = "",
        hypothesis: str = "",
        control_ratio: float = DEFAULT_CONTROL_RATIO,
        audience_mode: str = "all",
        audience_percentage: float = 100.0,
        audience_segment: str | None = None,
        end_date: str | None = None,
        min_duration_days: int = MIN_EXPERIMENT_DURATION_DAYS,
        metric_keys: list[str] | None = None,
        ai_rationale: str = "",
    ) -> ExperimentConfig:
        """Create a new experiment in draft status."""
        now = datetime.now(timezone.utc).isoformat()
        experiment = ExperimentConfig(
            experiment_id=f"exp-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            name=name,
            description=description,
            hypothesis=hypothesis,
            control=control,
            treatment=treatment,
            control_ratio=control_ratio,
            audience_mode=audience_mode,
            audience_percentage=audience_percentage,
            audience_segment=audience_segment,
            end_date=end_date,
            min_duration_days=min_duration_days,
            status=ExperimentStatus.DRAFT,
            assignment_seed=hash(now) % 10000,
            created_at=now,
            metric_keys=metric_keys
            or [
                "quality_score",
                "satisfaction",
                "session_length",
                "escalation_rate",
                "conversion_rate",
            ],
            ai_rationale=ai_rationale,
        )

        self._store[experiment.experiment_id] = experiment.model_dump(mode="json")

        logger.info(
            "Experiment created: tenant=%s exp=%s name=%s status=draft",
            tenant_id,
            experiment.experiment_id,
            name,
        )
        return experiment

    def get_experiment(self, experiment_id: str) -> ExperimentConfig | None:
        """Retrieve an experiment by ID."""
        data = self._store.get(experiment_id)
        if data is None:
            return None
        return ExperimentConfig(**data)

    def list_experiments(
        self,
        tenant_id: str | None = None,
        status: ExperimentStatus | None = None,
    ) -> list[ExperimentConfig]:
        """List experiments, optionally filtered by tenant and/or status."""
        results = []
        for data in self._store.values():
            if tenant_id and data.get("tenant_id") != tenant_id:
                continue
            if status and data.get("status") != status.value:
                continue
            results.append(ExperimentConfig(**data))
        return results

    def get_active_experiment(
        self, tenant_id: str
    ) -> ExperimentConfig | None:
        """Return the active experiment for a tenant (if any)."""
        active = self.list_experiments(
            tenant_id=tenant_id, status=ExperimentStatus.ACTIVE
        )
        return active[0] if active else None

    # -- State Transitions --------------------------------------------------

    def _transition(
        self,
        experiment_id: str,
        target_status: ExperimentStatus,
    ) -> ExperimentConfig:
        """Transition an experiment to a new status with validation."""
        experiment = self.get_experiment(experiment_id)
        if experiment is None:
            raise ValueError(f"Experiment {experiment_id} not found")

        current = experiment.status
        allowed = VALID_TRANSITIONS.get(current, set())
        if target_status not in allowed:
            raise ValueError(
                f"Invalid transition: {current.value} -> {target_status.value}. "
                f"Allowed: {[s.value for s in allowed]}"
            )

        experiment.status = target_status

        if target_status == ExperimentStatus.ACTIVE and not experiment.start_date:
            experiment.start_date = datetime.now(timezone.utc).isoformat()

        if target_status in (
            ExperimentStatus.CONCLUDED_PROMOTE,
            ExperimentStatus.CONCLUDED_ROLLBACK,
        ):
            experiment.concluded_at = datetime.now(timezone.utc).isoformat()

        self._store[experiment_id] = experiment.model_dump(mode="json")

        logger.info(
            "Experiment transition: exp=%s %s -> %s",
            experiment_id,
            current.value,
            target_status.value,
        )
        return experiment

    def submit_for_review(self, experiment_id: str) -> ExperimentConfig:
        """Submit a draft experiment for merchant review (SPEC-0626)."""
        return self._transition(experiment_id, ExperimentStatus.PENDING_REVIEW)

    def approve_experiment(self, experiment_id: str) -> ExperimentConfig:
        """Merchant approves experiment -> active (SPEC-0626)."""
        return self._transition(experiment_id, ExperimentStatus.ACTIVE)

    def reject_experiment(self, experiment_id: str) -> ExperimentConfig:
        """Merchant rejects experiment -> back to draft (SPEC-0626)."""
        return self._transition(experiment_id, ExperimentStatus.DRAFT)

    def request_conclusion(
        self,
        experiment_id: str,
        recommendation: str = "",
    ) -> ExperimentConfig:
        """AI recommends concluding -> pending merchant approval (SPEC-0626)."""
        exp = self._transition(experiment_id, ExperimentStatus.PENDING_CONCLUSION)
        if recommendation:
            exp.conclusion_recommendation = recommendation
            self._store[experiment_id] = exp.model_dump(mode="json")
        return exp

    def conclude_promote(self, experiment_id: str) -> ExperimentConfig:
        """Merchant approves promotion of treatment config."""
        return self._transition(experiment_id, ExperimentStatus.CONCLUDED_PROMOTE)

    def conclude_rollback(self, experiment_id: str) -> ExperimentConfig:
        """Merchant approves rollback to control config."""
        return self._transition(experiment_id, ExperimentStatus.CONCLUDED_ROLLBACK)

    def reject_conclusion(self, experiment_id: str) -> ExperimentConfig:
        """Merchant rejects conclusion -> experiment continues."""
        return self._transition(experiment_id, ExperimentStatus.ACTIVE)
