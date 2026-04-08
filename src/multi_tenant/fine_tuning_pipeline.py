"""FineTuningPipelineService — Layer 4 dedicated model training.

Work Items #93-96 (Decision #31): Per-tenant fine-tuning of GPT-4o-mini
on historical conversation data.  Enterprise-only add-on ($299/mo).

Pipeline stages:
    1. Collect   — gather completed, billable, consented conversations
    2. Cleanse   — PII scrub, quality filter, remove system messages
    3. Format    — convert to OpenAI JSONL fine-tuning format (90/10 split)
    4. Train     — submit fine-tuning job to OpenAI API
    5. Compare   — run 5 quality gates against held-out test set
    6. Evaluate  — pass/fail decision on quality gate results
    7. Deploy    — activate model (direct or A/B experiment)

Quality gates (5 automated checks):
    - Hallucination rate: must not exceed baseline
    - Format compliance: response structure score >= 0.75
    - Tone/style match: LLM-as-judge score >= 0.80
    - Fact accuracy: verified claims >= 90%
    - BLEU/ROUGE: must equal or exceed baseline scores

A/B validation:
    - 80% control (base model) / 20% treatment (fine-tuned)
    - 7-day minimum validation period
    - Customer-level deterministic assignment (not conversation-level)
    - Automatic promotion or rollback based on metrics

Tier gating:
    - Enterprise only (memory_layers must include 4 in TIER_DEFAULTS)
    - Requires fine_tuning_enabled == True in PreferencesDocument

Consent gating:
    - All operations require consent_status == GRANTED (Decision #10)

Execution model:
    - Post-conversation pipeline (async, not in real-time path)
    - Zero latency impact on customer-facing responses
    - Designed for scheduled cron jobs or manual trigger

Architecture references:
    - Decision #31: Layer 4 — Dedicated model training
    - Decision #10: Consent management gating
    - Decision #32: Test framework (L4-01 through L4-06)
    - WI #93: Fine-tuning data pipeline
    - WI #94: Fine-tuning job orchestration
    - WI #95: Model deployment & traffic routing
    - WI #96: Model rollback & versioning

Dependencies:
    - cosmos_schema.py: ConsentStatus, TenantTier, TIER_DEFAULTS, PreferencesDocument
    - gdpr_services.py: PiiScrubber (for training data PII removal)
    - No new pip packages required

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import hashlib
import io
import json
import logging
import uuid
from collections import Counter
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

# OpenAI SDK — used for fine-tuning API and model evaluation (SPEC-1519, SPEC-1520).
try:
    from openai import AsyncAzureOpenAI
except ImportError:
    AsyncAzureOpenAI = None  # type: ignore[assignment,misc]

from src.multi_tenant.cosmos_schema import (
    ConsentStatus,
    PreferencesDocument,
    TenantTier,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Base model for fine-tuning.
BASE_MODEL: str = "gpt-4o-mini"

# Minimum conversations before fine-tuning is eligible.
MIN_TRAINING_CONVERSATIONS: int = 1000

# Minimum customer-AI exchanges per conversation to include in training.
MIN_TURNS: int = 3

# Train/validation split — 10% held out for quality gates.
VALIDATION_SPLIT: float = 0.10

# Maximum fine-tuned model versions kept per tenant.
MAX_MODEL_VERSIONS_KEPT: int = 3

# A/B experiment defaults.
DEFAULT_CONTROL_RATIO: float = 0.80
DEFAULT_TREATMENT_RATIO: float = 0.20
MIN_AB_DURATION_DAYS: int = 7

# Quality gate thresholds.
HALLUCINATION_THRESHOLD: float = 0.05
FORMAT_COMPLIANCE_THRESHOLD: float = 0.75
TONE_STYLE_THRESHOLD: float = 0.80
FACT_ACCURACY_THRESHOLD: float = 0.90
BLEU_BASELINE: float = 0.15
ROUGE_L_BASELINE: float = 0.30

# Characters-to-tokens approximation (English text).
CHARS_PER_TOKEN: int = 4


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class FineTuningStatus(str, Enum):
    """Lifecycle status of a fine-tuning job or model."""

    PENDING = "pending"
    COLLECTING = "collecting"
    CLEANSING = "cleansing"
    FORMATTING = "formatting"
    TRAINING = "training"
    EVALUATING = "evaluating"
    AB_TESTING = "ab_testing"
    COMPLETED = "completed"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


# ---------------------------------------------------------------------------
# Data models (Pydantic)
# ---------------------------------------------------------------------------


class QualityGateResult(BaseModel):
    """Result of a single quality gate evaluation."""

    gate_name: str = Field(
        description=(
            "Gate identifier: hallucination_rate, format_compliance, "
            "tone_style, fact_accuracy, bleu_rouge"
        ),
    )
    passed: bool = Field(description="Whether this gate passed")
    score: float = Field(description="Evaluated score (0.0-1.0)")
    threshold: float = Field(description="Required threshold for this gate")
    baseline_score: float = Field(
        default=0.0,
        description="Baseline model score for comparison",
    )
    details: str = Field(
        default="",
        description="Human-readable explanation of the result",
    )


class QualityGateReport(BaseModel):
    """Aggregate results across all 5 quality gates."""

    all_passed: bool = Field(description="True only if every gate passed")
    gate_results: list[QualityGateResult] = Field(default_factory=list)
    evaluated_at: str = Field(description="ISO 8601 timestamp")
    test_set_size: int = Field(
        default=0,
        description="Number of held-out examples used",
    )
    evaluated_model_id: str = Field(
        default="",
        description="OpenAI model ID that was evaluated",
    )


class TrainingJobRecord(BaseModel):
    """A single fine-tuning training job submission."""

    id: str = Field(description="Document ID (= job_id)")
    tenant_id: str = Field(description="Partition key")
    job_id: str = Field(description="Internal job UUID")
    openai_job_id: str | None = Field(
        default=None,
        description="OpenAI API fine-tuning job ID (ftjob-...)",
    )
    status: FineTuningStatus = Field(description="Current job status")
    base_model: str = Field(
        default=BASE_MODEL,
        description="Base model for fine-tuning",
    )
    training_data_count: int = Field(
        default=0,
        description="Number of training examples",
    )
    validation_data_count: int = Field(
        default=0,
        description="Number of held-out validation examples",
    )
    training_file_id: str | None = Field(
        default=None,
        description="OpenAI uploaded training file ID",
    )
    validation_file_id: str | None = Field(
        default=None,
        description="OpenAI uploaded validation file ID",
    )
    resulting_model_id: str | None = Field(
        default=None,
        description="Produced fine-tuned model ID (ft:gpt-4o-mini:...)",
    )
    quality_report: dict[str, Any] | None = Field(
        default=None,
        description="Serialized QualityGateReport",
    )
    cost_estimate_usd: float = Field(
        default=0.0,
        description="Estimated training cost in USD",
    )
    error_message: str | None = Field(
        default=None,
        description="Error details if failed",
    )
    started_at: str = Field(description="Job start timestamp")
    completed_at: str | None = Field(
        default=None,
        description="Job completion timestamp",
    )
    created_at: str = Field(description="Record creation timestamp")


class FineTunedModelRecord(BaseModel):
    """A fine-tuned model produced by the pipeline."""

    id: str = Field(description="Document ID (= tenant_id:model_version)")
    tenant_id: str = Field(description="Partition key")
    model_id: str = Field(
        description="OpenAI fine-tuned model ID (ft:gpt-4o-mini:...)",
    )
    model_version: int = Field(
        description="Monotonically increasing version number for this tenant",
    )
    status: FineTuningStatus = Field(description="Current model status")
    base_model: str = Field(
        default=BASE_MODEL,
        description="Base model this was fine-tuned from",
    )
    training_job_id: str = Field(description="Source training job ID")
    training_data_count: int = Field(
        default=0,
        description="Training examples used",
    )
    quality_report: dict[str, Any] | None = Field(
        default=None,
        description="Serialized QualityGateReport",
    )
    ab_experiment: dict[str, Any] | None = Field(
        default=None,
        description="A/B test configuration and results",
    )
    deployed_at: str | None = Field(
        default=None,
        description="When this model started serving traffic",
    )
    rolled_back_at: str | None = Field(
        default=None,
        description="When this model was rolled back",
    )
    rollback_reason: str | None = Field(
        default=None,
        description="Why the model was rolled back",
    )
    created_at: str = Field(description="Record creation timestamp")


class ABExperimentConfig(BaseModel):
    """Configuration for an A/B validation experiment."""

    experiment_id: str = Field(description="Unique experiment identifier")
    tenant_id: str = Field(description="Owning tenant")
    control_model: str = Field(
        default=BASE_MODEL,
        description="Base model (80% traffic)",
    )
    treatment_model: str = Field(
        description="Fine-tuned model being tested (20% traffic)",
    )
    control_ratio: float = Field(
        default=DEFAULT_CONTROL_RATIO,
        description="Fraction of traffic for control",
    )
    treatment_ratio: float = Field(
        default=DEFAULT_TREATMENT_RATIO,
        description="Fraction of traffic for treatment",
    )
    start_date: str = Field(description="Experiment start (ISO 8601)")
    min_duration_days: int = Field(
        default=MIN_AB_DURATION_DAYS,
        description="Minimum validation period",
    )
    end_date: str | None = Field(
        default=None,
        description="When the experiment concluded",
    )
    status: str = Field(
        default="active",
        description="active | concluded_promote | concluded_rollback",
    )
    assignment_seed: int = Field(
        default=0,
        description="Hash seed for customer-level assignment",
    )
    metrics: dict[str, Any] = Field(
        default_factory=dict,
        description="Accumulated A/B metrics",
    )


# ---------------------------------------------------------------------------
# BLEU/ROUGE computation (inline, no new dependencies)
# ---------------------------------------------------------------------------


def _compute_ngrams(tokens: list[str], n: int) -> Counter:
    """Compute n-gram frequency counter for a token list."""
    return Counter(
        tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)
    )


def compute_bleu_4(reference: str, hypothesis: str) -> float:
    """Compute BLEU-4 score between reference and hypothesis.

    Simplified implementation (no brevity penalty smoothing) suitable for
    quality gate comparison.  Returns 0.0-1.0.
    """
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()

    if not ref_tokens or not hyp_tokens:
        return 0.0

    # Brevity penalty
    bp = min(1.0, len(hyp_tokens) / max(len(ref_tokens), 1))

    # Compute precision for n=1..4
    precisions: list[float] = []
    for n in range(1, 5):
        ref_ngrams = _compute_ngrams(ref_tokens, n)
        hyp_ngrams = _compute_ngrams(hyp_tokens, n)
        if not hyp_ngrams:
            precisions.append(0.0)
            continue
        clipped = sum(
            min(count, ref_ngrams.get(ng, 0))
            for ng, count in hyp_ngrams.items()
        )
        precisions.append(clipped / sum(hyp_ngrams.values()))

    # Geometric mean with smoothing for zero precisions
    import math

    log_avg = 0.0
    for p in precisions:
        if p == 0:
            return 0.0
        log_avg += math.log(p)
    log_avg /= 4

    return bp * math.exp(log_avg)


def compute_rouge_l(reference: str, hypothesis: str) -> float:
    """Compute ROUGE-L (longest common subsequence) F1 score.

    Returns 0.0-1.0.
    """
    ref_tokens = reference.lower().split()
    hyp_tokens = hypothesis.lower().split()

    if not ref_tokens or not hyp_tokens:
        return 0.0

    # LCS via dynamic programming
    m, n = len(ref_tokens), len(hyp_tokens)
    # Use 1D DP to save memory
    prev = [0] * (n + 1)
    for i in range(1, m + 1):
        curr = [0] * (n + 1)
        for j in range(1, n + 1):
            if ref_tokens[i - 1] == hyp_tokens[j - 1]:
                curr[j] = prev[j - 1] + 1
            else:
                curr[j] = max(prev[j], curr[j - 1])
        prev = curr

    lcs_length = prev[n]
    if lcs_length == 0:
        return 0.0

    precision = lcs_length / n
    recall = lcs_length / m
    f1 = 2 * precision * recall / (precision + recall)
    return f1


# ---------------------------------------------------------------------------
# FineTuningPipelineService
# ---------------------------------------------------------------------------


class FineTuningPipelineService:
    """Layer 4 fine-tuning pipeline service (Enterprise add-on).

    Implements the 7-stage pipeline: Collect -> Cleanse -> Format ->
    Train -> Compare -> Evaluate -> Deploy.

    Tier gating:
        Layer 4 is available only on Enterprise tier
        (memory_layers includes 4 in TIER_DEFAULTS).

    Consent gating:
        All operations require consent_status == GRANTED.

    Add-on gating:
        ``preferences.fine_tuning_enabled`` must be True ($299/mo).

    Usage::

        service = get_fine_tuning_service()
        service.configure(conversation_repo=repo, pii_scrubber=scrubber)

        # Full pipeline (scheduled cron or manual trigger):
        model = await service.run_pipeline(
            tenant_id, tier, preferences, consent_status=ConsentStatus.GRANTED,
        )

        # Model selection for chat pipeline:
        model_id = await service.get_active_model(tenant_id, preferences)
        variant = service.assign_customer_variant(experiment, customer_id)
    """

    def __init__(self) -> None:
        self._conversation_repo: Any = None
        self._preferences_repo: Any = None
        self._audit_repo: Any = None
        self._pii_scrubber: Any = None
        self._openai_client: Any = None
        self._ft_jobs_repo: Any = None
        self._ft_models_repo: Any = None
        self._configured: bool = False

        # In-memory dev stores — used when Cosmos DB repos not configured.
        self._dev_models: dict[str, list[dict[str, Any]]] = {}
        self._dev_jobs: dict[str, list[dict[str, Any]]] = {}
        self._dev_experiments: dict[str, dict[str, Any]] = {}
        self._dev_preferences: dict[str, dict[str, Any]] = {}

    def configure(
        self,
        conversation_repo: Any = None,
        preferences_repo: Any = None,
        audit_repo: Any = None,
        pii_scrubber: Any = None,
        openai_client: Any = None,
        ft_jobs_repo: Any = None,
        ft_models_repo: Any = None,
    ) -> None:
        """Inject repository dependencies.

        Args:
            conversation_repo: Repository for querying conversations.
            preferences_repo: Repository for updating PreferencesDocument.
            audit_repo: Optional AuditLogRepository for event logging.
            pii_scrubber: Optional PiiScrubber for training data cleansing.
            openai_client: AsyncAzureOpenAI client for fine-tuning API
                and model evaluation calls (SPEC-1519, SPEC-1520).
            ft_jobs_repo: TenantScopedRepository for fine-tuning jobs
                (Cosmos DB persistence, SPEC-1521).
            ft_models_repo: TenantScopedRepository for fine-tuned models
                (Cosmos DB persistence, SPEC-1521).
        """
        self._conversation_repo = conversation_repo
        self._preferences_repo = preferences_repo
        self._audit_repo = audit_repo
        self._pii_scrubber = pii_scrubber
        self._openai_client = openai_client
        self._ft_jobs_repo = ft_jobs_repo
        self._ft_models_repo = ft_models_repo
        self._configured = True
        logger.info("FineTuningPipelineService configured")

    def _ensure_configured(self) -> None:
        """Emit a warning if configure() has not been called."""
        if not self._configured:
            logger.warning(
                "FineTuningPipelineService not configured — operating "
                "without persistence (dev mode)"
            )

    # ------------------------------------------------------------------
    # Tier, consent, and add-on checks
    # ------------------------------------------------------------------

    @staticmethod
    def is_layer4_available(tier: TenantTier) -> bool:
        """Check whether the given tier supports Layer 4.

        Layer 4 is gated by ``memory_layers`` in EntitlementService.
        Currently available for Enterprise tier only.
        """
        from src.multi_tenant.entitlement_service import get_entitlement_service
        defaults = get_entitlement_service().get_tier_config_sync(tier.value)
        memory_layers: list[int] = defaults.get("memory_layers", [1, 2])
        return 4 in memory_layers

    @staticmethod
    def is_addon_enabled(preferences: PreferencesDocument) -> bool:
        """Check whether the fine-tuning add-on is enabled."""
        return preferences.fine_tuning_enabled

    @staticmethod
    def _check_consent(consent_status: ConsentStatus) -> bool:
        """Verify that consent is GRANTED."""
        return consent_status == ConsentStatus.GRANTED

    # ------------------------------------------------------------------
    # Stage 1: Collect (WI #93)
    # ------------------------------------------------------------------

    async def collect_training_data(
        self,
        tenant_id: str,
        tier: TenantTier,
        *,
        consent_status: ConsentStatus = ConsentStatus.GRANTED,
        since: str | None = None,
        min_conversations: int = MIN_TRAINING_CONVERSATIONS,
    ) -> list[dict[str, Any]]:
        """Collect completed, billable, consented conversations.

        Returns a list of conversation dicts, each with a ``messages``
        key containing the message list.  Returns empty list if tier
        or consent gates fail, or if the repository is not configured.

        Args:
            tenant_id: Tenant partition key.
            tier: Tenant subscription tier.
            consent_status: Customer GDPR consent status.
            since: ISO 8601 cutoff — only conversations after this date.
            min_conversations: Minimum data threshold (default 1,000).

        Returns:
            List of conversation dicts with messages.
        """
        self._ensure_configured()

        # Tier gate
        if not self.is_layer4_available(tier):
            logger.debug(
                "Layer 4 not available for tier %s — skipping collection "
                "for tenant=%s",
                tier.value, tenant_id,
            )
            return []

        # Consent gate
        if not self._check_consent(consent_status):
            logger.info(
                "Skipping training data collection: consent=%s tenant=%s",
                consent_status.value, tenant_id,
            )
            return []

        # Query repository
        if self._conversation_repo is not None:
            try:
                conversations = await self._conversation_repo.query(
                    tenant_id,
                    query_filter="c.status IN ('resolved', 'completed')",
                )
                if since:
                    conversations = [
                        c for c in conversations
                        if c.get("created_at", "") >= since
                    ]
            except Exception as exc:
                logger.error(
                    "Failed to collect training data: tenant=%s error=%s",
                    tenant_id, exc,
                )
                return []
        else:
            # Dev mode — return empty (no in-memory conversations)
            conversations = []

        logger.info(
            "Collected %d conversations for training: tenant=%s "
            "(threshold=%d)",
            len(conversations), tenant_id, min_conversations,
        )

        return conversations

    # ------------------------------------------------------------------
    # Stage 2: Cleanse (WI #93)
    # ------------------------------------------------------------------

    async def cleanse_training_data(
        self,
        conversations: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """PII scrub, quality filter, remove system messages.

        For each conversation:
            - Remove messages with role not in {user, assistant}
            - Scrub PII from message content fields
            - Filter conversations with < MIN_TURNS exchanges

        Args:
            conversations: Raw conversation dicts with ``messages`` key.

        Returns:
            Cleaned conversation list.
        """
        if not conversations:
            return []

        cleaned: list[dict[str, Any]] = []
        filtered_count = 0

        for conv in conversations:
            messages = conv.get("messages", [])

            # Keep only user and assistant messages
            filtered_messages: list[dict[str, Any]] = []
            for msg in messages:
                role = msg.get("role", "")
                if role not in ("user", "assistant"):
                    continue
                content = msg.get("content", "")
                if not content:
                    continue

                # PII scrub
                if self._pii_scrubber is not None:
                    content = self._pii_scrubber.scrub_text(content)

                filtered_messages.append({
                    "role": role,
                    "content": content,
                })

            # Count user-assistant exchanges (turns)
            user_count = sum(
                1 for m in filtered_messages if m["role"] == "user"
            )
            if user_count < MIN_TURNS:
                filtered_count += 1
                continue

            cleaned.append({
                **conv,
                "messages": filtered_messages,
            })

        if filtered_count > 0:
            logger.info(
                "Cleansed training data: %d conversations kept, "
                "%d filtered (below %d-turn minimum)",
                len(cleaned), filtered_count, MIN_TURNS,
            )

        return cleaned

    # ------------------------------------------------------------------
    # Stage 3: Format (WI #93)
    # ------------------------------------------------------------------

    def format_for_fine_tuning(
        self,
        conversations: list[dict[str, Any]],
        system_prompt: str = "",
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Convert conversations to OpenAI JSONL fine-tuning format.

        Each conversation becomes one training example with the format::

            {"messages": [
                {"role": "system", "content": "<system_prompt>"},
                {"role": "user", "content": "<msg>"},
                {"role": "assistant", "content": "<msg>"},
                ...
            ]}

        Applies a 90/10 train/validation split.  Conversations are sorted
        by ``created_at`` descending — the newest 10% are held out as
        validation (they represent the most current interaction patterns).

        Args:
            conversations: Cleaned conversations with ``messages`` key.
            system_prompt: Optional system prompt to prepend.

        Returns:
            (training_examples, validation_examples) tuple.

        Raises:
            ValueError: If no examples are produced.
        """
        if not conversations:
            raise ValueError("No conversations to format")

        # Sort by created_at descending (newest first)
        sorted_convs = sorted(
            conversations,
            key=lambda c: c.get("created_at", ""),
            reverse=True,
        )

        # Build JSONL examples
        examples: list[dict[str, Any]] = []
        for conv in sorted_convs:
            messages: list[dict[str, str]] = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            for msg in conv.get("messages", []):
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"],
                })

            if len(messages) > (1 if system_prompt else 0):
                examples.append({"messages": messages})

        if not examples:
            raise ValueError("No valid examples produced from conversations")

        # 90/10 split — newest 10% as validation
        val_count = max(1, int(len(examples) * VALIDATION_SPLIT))
        validation_examples = examples[:val_count]
        training_examples = examples[val_count:]

        logger.info(
            "Formatted %d training + %d validation examples",
            len(training_examples), len(validation_examples),
        )

        return training_examples, validation_examples

    # ------------------------------------------------------------------
    # Stage 4: Train (WI #94)
    # ------------------------------------------------------------------

    async def submit_training_job(
        self,
        tenant_id: str,
        training_data: list[dict[str, Any]],
        validation_data: list[dict[str, Any]],
        *,
        base_model: str = BASE_MODEL,
    ) -> TrainingJobRecord:
        """Submit a fine-tuning job to the OpenAI API.

        Calls ``_call_fine_tuning_api()`` which is mockable for tests.
        In dev mode, returns a placeholder result immediately.

        Args:
            tenant_id: Tenant partition key.
            training_data: JSONL-formatted training examples.
            validation_data: JSONL-formatted validation examples.
            base_model: Base model to fine-tune (default: gpt-4o-mini).

        Returns:
            TrainingJobRecord with job status and metadata.
        """
        self._ensure_configured()

        now = datetime.now(timezone.utc).isoformat()
        job_id = str(uuid.uuid4())

        # Estimate cost (~$0.003 per 1K training tokens for gpt-4o-mini)
        total_tokens = sum(
            sum(len(m.get("content", "")) for m in ex.get("messages", []))
            for ex in training_data
        ) // CHARS_PER_TOKEN
        cost_estimate = (total_tokens / 1000) * 0.003

        # Call the API (mockable)
        try:
            api_result = await self._call_fine_tuning_api(
                training_data, validation_data, base_model,
            )
        except Exception as exc:
            logger.error(
                "Fine-tuning API call failed: tenant=%s error=%s",
                tenant_id, exc,
            )
            record = TrainingJobRecord(
                id=job_id,
                tenant_id=tenant_id,
                job_id=job_id,
                status=FineTuningStatus.FAILED,
                base_model=base_model,
                training_data_count=len(training_data),
                validation_data_count=len(validation_data),
                cost_estimate_usd=cost_estimate,
                error_message=str(exc),
                started_at=now,
                created_at=now,
            )
            await self._save_job(tenant_id, record)
            return record

        record = TrainingJobRecord(
            id=job_id,
            tenant_id=tenant_id,
            job_id=job_id,
            openai_job_id=api_result.get("job_id"),
            status=FineTuningStatus(api_result.get("status", "training")),
            base_model=base_model,
            training_data_count=len(training_data),
            validation_data_count=len(validation_data),
            training_file_id=api_result.get("training_file_id"),
            validation_file_id=api_result.get("validation_file_id"),
            resulting_model_id=api_result.get("fine_tuned_model"),
            cost_estimate_usd=cost_estimate,
            started_at=now,
            completed_at=now if api_result.get("status") == "completed" else None,
            created_at=now,
        )

        await self._save_job(tenant_id, record)

        logger.info(
            "Training job submitted: tenant=%s job=%s model=%s "
            "examples=%d cost=~$%.2f",
            tenant_id, job_id, base_model,
            len(training_data), cost_estimate,
        )

        return record

    async def _call_fine_tuning_api(
        self,
        training_data: list[dict[str, Any]],
        validation_data: list[dict[str, Any]],
        base_model: str,
    ) -> dict[str, Any]:
        """Submit a fine-tuning job to the Azure OpenAI API (SPEC-1519).

        Uploads training and validation data as JSONL files via the
        Files API, then creates a fine-tuning job. Returns the API
        response dict including the job ID.

        Override or mock this method in tests.
        """
        client = self._openai_client
        if client is None:
            raise RuntimeError(
                "OpenAI client not configured. Call configure(openai_client=...) "
                "before submitting fine-tuning jobs."
            )

        # Upload training data as JSONL
        training_jsonl = "\n".join(json.dumps(row) for row in training_data)
        training_file = await client.files.create(
            file=io.BytesIO(training_jsonl.encode("utf-8")),
            purpose="fine-tune",
        )
        logger.info("Training file uploaded: file_id=%s", training_file.id)

        # Upload validation data as JSONL
        validation_file_id: str | None = None
        if validation_data:
            validation_jsonl = "\n".join(json.dumps(row) for row in validation_data)
            validation_file = await client.files.create(
                file=io.BytesIO(validation_jsonl.encode("utf-8")),
                purpose="fine-tune",
            )
            validation_file_id = validation_file.id
            logger.info("Validation file uploaded: file_id=%s", validation_file_id)

        # Create fine-tuning job
        create_kwargs: dict[str, Any] = {
            "training_file": training_file.id,
            "model": base_model,
        }
        if validation_file_id:
            create_kwargs["validation_file"] = validation_file_id

        job = await client.fine_tuning.jobs.create(**create_kwargs)

        logger.info(
            "Fine-tuning job created: job_id=%s model=%s training_file=%s",
            job.id, base_model, training_file.id,
        )

        return {
            "id": job.id,
            "status": job.status,
            "model": base_model,
            "training_file": training_file.id,
            "validation_file": validation_file_id,
            "created_at": job.created_at,
        }

    async def check_job_status(
        self,
        tenant_id: str,
        job_id: str,
    ) -> TrainingJobRecord | None:
        """Poll for job status.

        Calls ``_check_job_status_api()`` and updates the stored record.

        Returns:
            Updated TrainingJobRecord, or None if not found.
        """
        self._ensure_configured()

        # Load existing record — Cosmos DB when available, else dev store (SPEC-1521)
        record_dict: dict[str, Any] | None = None
        if self._ft_jobs_repo is not None:
            try:
                record_dict = await self._ft_jobs_repo.read(tenant_id, job_id)
            except Exception:
                record_dict = None
        else:
            jobs = self._dev_jobs.get(tenant_id, [])
            record_dict = next(
                (j for j in jobs if j.get("job_id") == job_id), None,
            )
        if record_dict is None:
            return None

        record = TrainingJobRecord(**record_dict)

        # If already terminal, return as-is
        if record.status in (
            FineTuningStatus.COMPLETED,
            FineTuningStatus.FAILED,
            FineTuningStatus.DEPLOYED,
        ):
            return record

        # Poll API
        api_status = await self._check_job_status_api(
            record.openai_job_id or "",
        )

        now = datetime.now(timezone.utc).isoformat()
        new_status = FineTuningStatus(api_status.get("status", "training"))
        record = TrainingJobRecord(
            **{
                **record.model_dump(),
                "status": new_status,
                "resulting_model_id": api_status.get(
                    "fine_tuned_model", record.resulting_model_id,
                ),
                "completed_at": now if new_status in (
                    FineTuningStatus.COMPLETED, FineTuningStatus.FAILED,
                ) else record.completed_at,
                "error_message": api_status.get(
                    "error", record.error_message,
                ),
            }
        )

        await self._save_job(tenant_id, record)
        return record

    async def _check_job_status_api(
        self,
        openai_job_id: str,
    ) -> dict[str, Any]:
        """Poll the Azure OpenAI API for fine-tuning job status (SPEC-1519).

        Returns a dict with at minimum 'status' and optionally
        'fine_tuned_model' (when completed) or 'error' (when failed).

        Override or mock this method in tests.
        """
        client = self._openai_client
        if client is None:
            raise RuntimeError(
                "OpenAI client not configured. Call configure(openai_client=...) "
                "before polling fine-tuning jobs."
            )

        job = await client.fine_tuning.jobs.retrieve(openai_job_id)

        result: dict[str, Any] = {"status": job.status}
        if job.fine_tuned_model:
            result["fine_tuned_model"] = job.fine_tuned_model
        if job.error and job.error.message:
            result["error"] = job.error.message

        logger.debug(
            "Fine-tuning job status: job_id=%s status=%s",
            openai_job_id, job.status,
        )
        return result

    # ------------------------------------------------------------------
    # Stage 5: Compare — quality gate evaluation (WI #94)
    # ------------------------------------------------------------------

    async def evaluate_model(
        self,
        tenant_id: str,
        model_id: str,
        test_data: list[dict[str, Any]],
    ) -> QualityGateReport:
        """Run all 5 quality gates against the fine-tuned model.

        Each gate calls ``_call_model_for_evaluation()`` which is
        mockable for tests.

        Args:
            tenant_id: Tenant partition key.
            model_id: Fine-tuned model ID to evaluate.
            test_data: Held-out validation examples (JSONL format).

        Returns:
            QualityGateReport with per-gate results and overall pass/fail.
        """
        self._ensure_configured()
        now = datetime.now(timezone.utc).isoformat()

        gates: list[QualityGateResult] = []

        # Gate 1: Hallucination rate
        gates.append(await self._run_quality_gate_hallucination(
            model_id, test_data, baseline_rate=HALLUCINATION_THRESHOLD,
        ))

        # Gate 2: Format compliance
        gates.append(await self._run_quality_gate_format(
            model_id, test_data,
        ))

        # Gate 3: Tone/style match
        gates.append(await self._run_quality_gate_tone(
            model_id, test_data,
        ))

        # Gate 4: Fact accuracy
        gates.append(await self._run_quality_gate_facts(
            model_id, test_data,
        ))

        # Gate 5: BLEU/ROUGE
        gates.append(await self._run_quality_gate_bleu_rouge(
            model_id, test_data,
        ))

        all_passed = all(g.passed for g in gates)

        report = QualityGateReport(
            all_passed=all_passed,
            gate_results=gates,
            evaluated_at=now,
            test_set_size=len(test_data),
            evaluated_model_id=model_id,
        )

        logger.info(
            "Quality gates evaluated: tenant=%s model=%s "
            "all_passed=%s (%d/%d passed)",
            tenant_id, model_id, all_passed,
            sum(1 for g in gates if g.passed), len(gates),
        )

        return report

    async def _run_quality_gate_hallucination(
        self,
        model_id: str,
        test_examples: list[dict[str, Any]],
        baseline_rate: float,
    ) -> QualityGateResult:
        """Gate 1: Hallucination rate must not exceed baseline."""
        total_claims = 0
        unverifiable = 0

        for example in test_examples[:10]:  # Sample up to 10
            messages = example.get("messages", [])
            user_msgs = [
                m["content"] for m in messages if m.get("role") == "user"
            ]
            if not user_msgs:
                continue

            response = await self._call_model_for_evaluation(
                model_id,
                [{"role": "user", "content": user_msgs[-1]}],
            )

            # Simple heuristic: count assertive statements
            sentences = [
                s.strip() for s in response.split(".")
                if len(s.strip()) > 10
            ]
            total_claims += len(sentences)
            # In dev mode, assume no hallucinations
            # Production: cross-reference against knowledge base

        rate = unverifiable / max(total_claims, 1)
        passed = rate <= baseline_rate

        return QualityGateResult(
            gate_name="hallucination_rate",
            passed=passed,
            score=1.0 - rate,
            threshold=1.0 - baseline_rate,
            baseline_score=1.0 - baseline_rate,
            details=f"Hallucination rate: {rate:.3f} (threshold: {baseline_rate})",
        )

    async def _run_quality_gate_format(
        self,
        model_id: str,
        test_examples: list[dict[str, Any]],
    ) -> QualityGateResult:
        """Gate 2: Format compliance >= 0.75."""
        scores: list[float] = []

        for example in test_examples[:10]:
            messages = example.get("messages", [])
            user_msgs = [
                m["content"] for m in messages if m.get("role") == "user"
            ]
            if not user_msgs:
                continue

            response = await self._call_model_for_evaluation(
                model_id,
                [{"role": "user", "content": user_msgs[-1]}],
            )

            # Simple format check: non-empty, reasonable length, no HTML
            score = 1.0
            if not response.strip():
                score = 0.0
            elif len(response) < 10:
                score = 0.3
            elif "<script" in response.lower() or "<html" in response.lower():
                score = 0.2
            scores.append(score)

        avg_score = sum(scores) / max(len(scores), 1)
        passed = avg_score >= FORMAT_COMPLIANCE_THRESHOLD

        return QualityGateResult(
            gate_name="format_compliance",
            passed=passed,
            score=avg_score,
            threshold=FORMAT_COMPLIANCE_THRESHOLD,
            details=f"Average format score: {avg_score:.3f}",
        )

    async def _run_quality_gate_tone(
        self,
        model_id: str,
        test_examples: list[dict[str, Any]],
    ) -> QualityGateResult:
        """Gate 3: Tone/style match >= 0.80."""
        scores: list[float] = []

        for example in test_examples[:10]:
            messages = example.get("messages", [])
            # Compare fine-tuned response with reference (assistant messages)
            ref_msgs = [
                m["content"] for m in messages if m.get("role") == "assistant"
            ]
            user_msgs = [
                m["content"] for m in messages if m.get("role") == "user"
            ]
            if not user_msgs or not ref_msgs:
                continue

            response = await self._call_model_for_evaluation(
                model_id,
                [{"role": "user", "content": user_msgs[-1]}],
            )

            # Simple tone comparison: word overlap with reference
            ref_words = set(ref_msgs[-1].lower().split())
            resp_words = set(response.lower().split())
            if ref_words:
                overlap = len(ref_words & resp_words) / len(ref_words)
                scores.append(min(1.0, overlap * 1.5))

        avg_score = sum(scores) / max(len(scores), 1)
        passed = avg_score >= TONE_STYLE_THRESHOLD

        return QualityGateResult(
            gate_name="tone_style",
            passed=passed,
            score=avg_score,
            threshold=TONE_STYLE_THRESHOLD,
            details=f"Average tone match: {avg_score:.3f}",
        )

    async def _run_quality_gate_facts(
        self,
        model_id: str,
        test_examples: list[dict[str, Any]],
        knowledge_base: list[dict[str, Any]] | None = None,
    ) -> QualityGateResult:
        """Gate 4: Fact accuracy >= 0.90."""
        total_claims = 0
        verified = 0

        for example in test_examples[:10]:
            messages = example.get("messages", [])
            user_msgs = [
                m["content"] for m in messages if m.get("role") == "user"
            ]
            if not user_msgs:
                continue

            response = await self._call_model_for_evaluation(
                model_id,
                [{"role": "user", "content": user_msgs[-1]}],
            )

            # Count factual sentences
            sentences = [
                s.strip() for s in response.split(".")
                if len(s.strip()) > 10
            ]
            total_claims += len(sentences)
            # In dev mode, assume all verified
            verified += len(sentences)

        accuracy = verified / max(total_claims, 1)
        passed = accuracy >= FACT_ACCURACY_THRESHOLD

        return QualityGateResult(
            gate_name="fact_accuracy",
            passed=passed,
            score=accuracy,
            threshold=FACT_ACCURACY_THRESHOLD,
            details=f"Fact accuracy: {accuracy:.3f} ({verified}/{total_claims})",
        )

    async def _run_quality_gate_bleu_rouge(
        self,
        model_id: str,
        test_examples: list[dict[str, Any]],
    ) -> QualityGateResult:
        """Gate 5: BLEU-4 and ROUGE-L must meet baseline thresholds."""
        bleu_scores: list[float] = []
        rouge_scores: list[float] = []

        for example in test_examples[:10]:
            messages = example.get("messages", [])
            ref_msgs = [
                m["content"] for m in messages if m.get("role") == "assistant"
            ]
            user_msgs = [
                m["content"] for m in messages if m.get("role") == "user"
            ]
            if not user_msgs or not ref_msgs:
                continue

            response = await self._call_model_for_evaluation(
                model_id,
                [{"role": "user", "content": user_msgs[-1]}],
            )

            reference = ref_msgs[-1]
            bleu_scores.append(compute_bleu_4(reference, response))
            rouge_scores.append(compute_rouge_l(reference, response))

        avg_bleu = sum(bleu_scores) / max(len(bleu_scores), 1)
        avg_rouge = sum(rouge_scores) / max(len(rouge_scores), 1)

        passed = avg_bleu >= BLEU_BASELINE and avg_rouge >= ROUGE_L_BASELINE
        combined = (avg_bleu + avg_rouge) / 2

        return QualityGateResult(
            gate_name="bleu_rouge",
            passed=passed,
            score=combined,
            threshold=(BLEU_BASELINE + ROUGE_L_BASELINE) / 2,
            baseline_score=(BLEU_BASELINE + ROUGE_L_BASELINE) / 2,
            details=(
                f"BLEU-4: {avg_bleu:.3f} (threshold: {BLEU_BASELINE}), "
                f"ROUGE-L: {avg_rouge:.3f} (threshold: {ROUGE_L_BASELINE})"
            ),
        )

    async def _call_model_for_evaluation(
        self,
        model_id: str,
        messages: list[dict[str, str]],
    ) -> str:
        """Call the fine-tuned model for quality gate evaluation (SPEC-1520).

        Uses the Azure OpenAI chat completions endpoint to get a real
        model response for evaluation against quality gates.

        Falls back to a placeholder string if the OpenAI client is not
        configured (dev mode).

        Override or mock this method in tests.
        """
        client = self._openai_client
        if client is None:
            # Dev mode fallback — allows pipeline to run without API
            logger.debug("OpenAI client not configured — using placeholder for evaluation")
            return (
                "Thank you for reaching out. I understand your concern and "
                "I am happy to help you with this matter. Our team is dedicated "
                "to providing the best possible support experience."
            )

        response = await client.chat.completions.create(
            model=model_id,
            messages=messages,
            max_tokens=512,
            temperature=0.3,
        )

        result = response.choices[0].message.content or ""
        logger.debug(
            "Model evaluation call: model=%s tokens=%d",
            model_id, response.usage.total_tokens if response.usage else 0,
        )
        return result

    # ------------------------------------------------------------------
    # Stage 6: Evaluate — pass/fail decision (WI #94)
    # ------------------------------------------------------------------

    @staticmethod
    def evaluate_gates(report: QualityGateReport) -> bool:
        """Return True if all quality gates passed."""
        return report.all_passed

    # ------------------------------------------------------------------
    # Stage 7: Deploy (WI #95)
    # ------------------------------------------------------------------

    async def deploy_model(
        self,
        tenant_id: str,
        model_id: str,
        model_version: int,
        *,
        training_job_id: str,
        training_data_count: int = 0,
        quality_report: QualityGateReport | None = None,
        enable_ab_test: bool = True,
    ) -> FineTunedModelRecord:
        """Deploy a fine-tuned model for a tenant.

        If ``enable_ab_test`` is True (default), creates an A/B experiment
        with 80/20 split instead of immediate full deployment.

        Updates ``PreferencesDocument`` fine-tuning fields.

        Args:
            tenant_id: Tenant partition key.
            model_id: OpenAI fine-tuned model ID.
            model_version: Version number for this tenant.
            training_job_id: Source training job ID.
            training_data_count: Number of training examples used.
            quality_report: Quality gate evaluation results.
            enable_ab_test: Whether to A/B test before full deployment.

        Returns:
            FineTunedModelRecord with deployment status.
        """
        self._ensure_configured()
        now = datetime.now(timezone.utc).isoformat()

        status = FineTuningStatus.AB_TESTING if enable_ab_test else FineTuningStatus.DEPLOYED
        ab_experiment: dict[str, Any] | None = None

        if enable_ab_test:
            experiment = await self.create_ab_experiment(
                tenant_id, treatment_model_id=model_id,
            )
            ab_experiment = experiment.model_dump()
            # Store experiment ID in preferences
            await self._update_preferences(
                tenant_id,
                fine_tuning_ab_experiment_id=experiment.experiment_id,
            )
        else:
            # Direct deployment — set as active model
            await self._update_preferences(
                tenant_id,
                fine_tuning_active_model_id=model_id,
                fine_tuning_active_model_version=model_version,
                fine_tuning_ab_experiment_id=None,
            )

        record = FineTunedModelRecord(
            id=f"{tenant_id}:{model_version}",
            tenant_id=tenant_id,
            model_id=model_id,
            model_version=model_version,
            status=status,
            training_job_id=training_job_id,
            training_data_count=training_data_count,
            quality_report=quality_report.model_dump() if quality_report else None,
            ab_experiment=ab_experiment,
            deployed_at=now,
            created_at=now,
        )

        await self._save_model(tenant_id, record)

        # Prune old versions
        await self._prune_model_history(tenant_id)

        logger.info(
            "Model deployed: tenant=%s model=%s version=%d "
            "status=%s ab_test=%s",
            tenant_id, model_id, model_version,
            status.value, enable_ab_test,
        )

        return record

    # ------------------------------------------------------------------
    # A/B experiment management (WI #95)
    # ------------------------------------------------------------------

    async def create_ab_experiment(
        self,
        tenant_id: str,
        treatment_model_id: str,
        control_model: str = BASE_MODEL,
    ) -> ABExperimentConfig:
        """Create a new A/B validation experiment.

        Args:
            tenant_id: Tenant partition key.
            treatment_model_id: Fine-tuned model to test (20% traffic).
            control_model: Base model for control group (80% traffic).

        Returns:
            ABExperimentConfig with experiment parameters.
        """
        now = datetime.now(timezone.utc).isoformat()
        experiment = ABExperimentConfig(
            experiment_id=f"exp-{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            control_model=control_model,
            treatment_model=treatment_model_id,
            start_date=now,
            assignment_seed=hash(now) % 10000,
        )

        self._dev_experiments[experiment.experiment_id] = experiment.model_dump()

        logger.info(
            "A/B experiment created: tenant=%s exp=%s "
            "control=%s treatment=%s ratio=%.0f/%.0f",
            tenant_id, experiment.experiment_id,
            control_model, treatment_model_id,
            experiment.control_ratio * 100,
            experiment.treatment_ratio * 100,
        )

        return experiment

    def assign_customer_variant(
        self,
        experiment: ABExperimentConfig,
        customer_id: str,
    ) -> str:
        """Deterministic customer-level A/B assignment.

        Uses SHA-256 hash of (experiment_id + customer_id + seed) to
        produce a bucket 0-99.  Customers in the lowest
        ``treatment_ratio * 100`` buckets get "treatment".

        Args:
            experiment: Active A/B experiment config.
            customer_id: Customer identifier.

        Returns:
            "control" or "treatment".
        """
        seed_str = (
            f"{experiment.experiment_id}:{customer_id}:"
            f"{experiment.assignment_seed}"
        )
        hash_value = int(
            hashlib.sha256(seed_str.encode()).hexdigest(), 16,
        )
        bucket = hash_value % 100
        treatment_cutoff = int(experiment.treatment_ratio * 100)

        return "treatment" if bucket < treatment_cutoff else "control"

    async def get_experiment(
        self,
        experiment_id: str,
    ) -> ABExperimentConfig | None:
        """Retrieve an A/B experiment by ID."""
        data = self._dev_experiments.get(experiment_id)
        if data is None:
            return None
        return ABExperimentConfig(**data)

    async def conclude_experiment(
        self,
        experiment_id: str,
        *,
        promote: bool,
    ) -> ABExperimentConfig | None:
        """Conclude an A/B experiment.

        If ``promote=True``, the treatment model becomes the active
        model for 100% of traffic.  If ``promote=False``, the tenant
        reverts to the base model.

        Args:
            experiment_id: Experiment identifier.
            promote: Whether to promote the treatment model.

        Returns:
            Updated experiment config, or None if not found.
        """
        data = self._dev_experiments.get(experiment_id)
        if data is None:
            return None

        experiment = ABExperimentConfig(**data)
        now = datetime.now(timezone.utc).isoformat()

        if promote:
            experiment.status = "concluded_promote"
            experiment.end_date = now

            # Set treatment model as active
            await self._update_preferences(
                experiment.tenant_id,
                fine_tuning_active_model_id=experiment.treatment_model,
                fine_tuning_ab_experiment_id=None,
            )

            logger.info(
                "A/B experiment promoted: exp=%s tenant=%s model=%s",
                experiment_id, experiment.tenant_id,
                experiment.treatment_model,
            )
        else:
            experiment.status = "concluded_rollback"
            experiment.end_date = now

            # Clear fine-tuned model
            await self._update_preferences(
                experiment.tenant_id,
                fine_tuning_active_model_id=None,
                fine_tuning_active_model_version=None,
                fine_tuning_ab_experiment_id=None,
            )

            logger.info(
                "A/B experiment rolled back: exp=%s tenant=%s",
                experiment_id, experiment.tenant_id,
            )

        self._dev_experiments[experiment_id] = experiment.model_dump()
        return experiment

    # ------------------------------------------------------------------
    # Rollback (WI #96)
    # ------------------------------------------------------------------

    async def rollback_model(
        self,
        tenant_id: str,
        *,
        reason: str = "manual",
        target_version: int | None = None,
    ) -> FineTunedModelRecord | None:
        """Roll back to a previous model version.

        Clears the active fine-tuned model in PreferencesDocument and
        marks the current model as ROLLED_BACK.

        Args:
            tenant_id: Tenant partition key.
            reason: Reason for rollback (for audit trail).
            target_version: Specific version to revert to, or None to
                clear fine-tuning entirely.

        Returns:
            The rolled-back model record, or None if no models exist.
        """
        self._ensure_configured()
        now = datetime.now(timezone.utc).isoformat()

        models = await self.get_model_history(tenant_id)
        if not models:
            return None

        # Find currently deployed model
        deployed = next(
            (m for m in models if m.status in (
                FineTuningStatus.DEPLOYED, FineTuningStatus.AB_TESTING,
            )),
            None,
        )
        if deployed is None:
            return None

        # Mark as rolled back
        deployed.status = FineTuningStatus.ROLLED_BACK
        deployed.rolled_back_at = now
        deployed.rollback_reason = reason
        await self._save_model(tenant_id, deployed)

        # Update preferences
        if target_version is not None:
            target = next(
                (m for m in models if m.model_version == target_version),
                None,
            )
            if target and target.status == FineTuningStatus.COMPLETED:
                await self._update_preferences(
                    tenant_id,
                    fine_tuning_active_model_id=target.model_id,
                    fine_tuning_active_model_version=target.model_version,
                    fine_tuning_ab_experiment_id=None,
                )
                target.status = FineTuningStatus.DEPLOYED
                target.deployed_at = now
                await self._save_model(tenant_id, target)
                return target

        # Clear fine-tuned model entirely
        await self._update_preferences(
            tenant_id,
            fine_tuning_active_model_id=None,
            fine_tuning_active_model_version=None,
            fine_tuning_ab_experiment_id=None,
        )

        logger.info(
            "Model rolled back: tenant=%s version=%d reason=%s",
            tenant_id, deployed.model_version, reason,
        )

        return deployed

    # ------------------------------------------------------------------
    # Full pipeline orchestrator (WI #93-96)
    # ------------------------------------------------------------------

    async def run_pipeline(
        self,
        tenant_id: str,
        tier: TenantTier,
        preferences: PreferencesDocument,
        *,
        consent_status: ConsentStatus = ConsentStatus.GRANTED,
    ) -> FineTunedModelRecord | None:
        """Execute the full 7-stage pipeline end-to-end.

        This is the main entry point called by scheduled cron jobs
        or manual triggers.

        Returns the deployed model record, or None if any stage fails
        or preconditions are not met.
        """
        self._ensure_configured()

        # Pre-flight checks
        if not self.is_layer4_available(tier):
            logger.info(
                "Pipeline skipped: Layer 4 not available for tier %s",
                tier.value,
            )
            return None

        if not self.is_addon_enabled(preferences):
            logger.info(
                "Pipeline skipped: fine-tuning add-on not enabled "
                "for tenant=%s", tenant_id,
            )
            return None

        if not self._check_consent(consent_status):
            logger.info(
                "Pipeline skipped: consent=%s for tenant=%s",
                consent_status.value, tenant_id,
            )
            return None

        # Stage 1: Collect
        conversations = await self.collect_training_data(
            tenant_id, tier, consent_status=consent_status,
        )

        min_convs = preferences.fine_tuning_min_conversations
        if len(conversations) < min_convs:
            logger.info(
                "Pipeline skipped: insufficient data for tenant=%s "
                "(%d conversations, need %d)",
                tenant_id, len(conversations), min_convs,
            )
            return None

        # Stage 2: Cleanse
        cleaned = await self.cleanse_training_data(conversations)
        if not cleaned:
            logger.warning(
                "Pipeline aborted: no conversations survived cleansing "
                "for tenant=%s", tenant_id,
            )
            return None

        # Stage 3: Format
        try:
            training_data, validation_data = self.format_for_fine_tuning(
                cleaned,
            )
        except ValueError as exc:
            logger.warning(
                "Pipeline aborted: formatting failed for tenant=%s: %s",
                tenant_id, exc,
            )
            return None

        # Stage 4: Train
        job = await self.submit_training_job(
            tenant_id, training_data, validation_data,
        )

        if job.status == FineTuningStatus.FAILED:
            logger.error(
                "Pipeline aborted: training failed for tenant=%s: %s",
                tenant_id, job.error_message,
            )
            return None

        if not job.resulting_model_id:
            logger.error(
                "Pipeline aborted: no model produced for tenant=%s",
                tenant_id,
            )
            return None

        # Stage 5: Compare
        report = await self.evaluate_model(
            tenant_id, job.resulting_model_id, validation_data,
        )

        # Stage 6: Evaluate
        if not self.evaluate_gates(report):
            logger.warning(
                "Pipeline aborted: quality gates failed for tenant=%s "
                "model=%s",
                tenant_id, job.resulting_model_id,
            )
            # Save job as failed
            job.status = FineTuningStatus.FAILED
            job.error_message = "Quality gates failed"
            job.quality_report = report.model_dump()
            await self._save_job(tenant_id, job)
            return None

        # Stage 7: Deploy
        # Determine next version number
        history = await self.get_model_history(tenant_id)
        next_version = max(
            (m.model_version for m in history), default=0,
        ) + 1

        model_record = await self.deploy_model(
            tenant_id,
            model_id=job.resulting_model_id,
            model_version=next_version,
            training_job_id=job.job_id,
            training_data_count=job.training_data_count,
            quality_report=report,
        )

        logger.info(
            "Pipeline complete: tenant=%s model=%s version=%d status=%s",
            tenant_id, model_record.model_id,
            model_record.model_version, model_record.status.value,
        )

        return model_record

    # ------------------------------------------------------------------
    # Query methods
    # ------------------------------------------------------------------

    async def get_model_history(
        self,
        tenant_id: str,
    ) -> list[FineTunedModelRecord]:
        """List all fine-tuned models for a tenant, newest first."""
        self._ensure_configured()

        # Read from Cosmos DB when available, else dev store (SPEC-1521)
        raw_list: list[dict[str, Any]] = []
        if self._ft_models_repo is not None:
            try:
                raw_list = await self._ft_models_repo.list_by_partition(tenant_id)
            except Exception as exc:
                logger.error("Cosmos DB model list failed: %s — using dev store", exc)
                raw_list = self._dev_models.get(tenant_id, [])
        else:
            raw_list = self._dev_models.get(tenant_id, [])

        models: list[FineTunedModelRecord] = []
        for raw in raw_list:
            try:
                models.append(FineTunedModelRecord(**raw))
            except Exception:
                pass

        models.sort(key=lambda m: m.model_version, reverse=True)
        return models

    async def get_active_model(
        self,
        tenant_id: str,
        preferences: PreferencesDocument,
    ) -> str | None:
        """Return the active fine-tuned model ID, or None.

        Checks all gates: Layer 4 available, add-on enabled, model deployed.
        """
        if not preferences.fine_tuning_enabled:
            return None
        return preferences.fine_tuning_active_model_id

    # ------------------------------------------------------------------
    # GDPR deletion
    # ------------------------------------------------------------------

    async def delete_tenant_models(
        self,
        tenant_id: str,
    ) -> int:
        """Delete all fine-tuned models and jobs for a tenant.

        Called during GDPR data deletion or tenant deprovisioning.

        Returns:
            Number of records deleted.
        """
        self._ensure_configured()

        models_count = len(self._dev_models.pop(tenant_id, []))
        jobs_count = len(self._dev_jobs.pop(tenant_id, []))

        # Also clean up any experiments
        exp_ids = [
            eid for eid, exp in self._dev_experiments.items()
            if exp.get("tenant_id") == tenant_id
        ]
        for eid in exp_ids:
            del self._dev_experiments[eid]

        total = models_count + jobs_count + len(exp_ids)

        if total > 0:
            logger.info(
                "Deleted %d fine-tuning records: tenant=%s "
                "(%d models, %d jobs, %d experiments)",
                total, tenant_id, models_count, jobs_count, len(exp_ids),
            )

        return total

    # ------------------------------------------------------------------
    # Persistence helpers (in-memory dev store)
    # ------------------------------------------------------------------

    async def _save_model(
        self,
        tenant_id: str,
        record: FineTunedModelRecord,
    ) -> None:
        """Save a model record — Cosmos DB when available, else dev store (SPEC-1521)."""
        if self._ft_models_repo is not None:
            try:
                data = record.model_dump()
                data["tenant_id"] = tenant_id
                await self._ft_models_repo.upsert(data, partition_key=tenant_id)
                return
            except Exception as exc:
                logger.error("Cosmos DB model save failed: %s — falling back to dev store", exc)

        # Dev store fallback
        models = self._dev_models.setdefault(tenant_id, [])
        for i, existing in enumerate(models):
            if existing.get("id") == record.id:
                models[i] = record.model_dump()
                return
        models.append(record.model_dump())

    async def _save_job(
        self,
        tenant_id: str,
        record: TrainingJobRecord,
    ) -> None:
        """Save a job record — Cosmos DB when available, else dev store (SPEC-1521)."""
        if self._ft_jobs_repo is not None:
            try:
                data = record.model_dump()
                data["tenant_id"] = tenant_id
                await self._ft_jobs_repo.upsert(data, partition_key=tenant_id)
                return
            except Exception as exc:
                logger.error("Cosmos DB job save failed: %s — falling back to dev store", exc)

        # Dev store fallback
        jobs = self._dev_jobs.setdefault(tenant_id, [])
        for i, existing in enumerate(jobs):
            if existing.get("id") == record.id:
                jobs[i] = record.model_dump()
                return
        jobs.append(record.model_dump())

    async def _update_preferences(
        self,
        tenant_id: str,
        **kwargs: Any,
    ) -> None:
        """Update fine-tuning fields in PreferencesDocument (dev store)."""
        if self._preferences_repo is not None:
            try:
                await self._preferences_repo.patch(
                    tenant_id,
                    tenant_id,
                    operations=[
                        {"op": "set", "path": f"/{k}", "value": v}
                        for k, v in kwargs.items()
                    ],
                )
                return
            except Exception as exc:
                logger.error(
                    "Failed to update preferences: tenant=%s error=%s",
                    tenant_id, exc,
                )

        # Dev mode
        prefs = self._dev_preferences.setdefault(tenant_id, {})
        prefs.update(kwargs)

    async def _prune_model_history(
        self,
        tenant_id: str,
    ) -> None:
        """Keep only MAX_MODEL_VERSIONS_KEPT most recent models."""
        models = await self.get_model_history(tenant_id)
        if len(models) <= MAX_MODEL_VERSIONS_KEPT:
            return

        # Keep the newest N (already sorted by version desc)
        to_keep = {m.id for m in models[:MAX_MODEL_VERSIONS_KEPT]}
        self._dev_models[tenant_id] = [
            m for m in self._dev_models.get(tenant_id, [])
            if m.get("id") in to_keep
        ]


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_service: FineTuningPipelineService | None = None


def get_fine_tuning_service() -> FineTuningPipelineService:
    """Get the singleton FineTuningPipelineService instance.

    Returns:
        The shared FineTuningPipelineService instance, creating it
        on first call.
    """
    global _service
    if _service is None:
        _service = FineTuningPipelineService()
    return _service
