"""
Stripe webhook handler.

Receives Stripe webhook events, verifies signatures, and dispatches to
per-event-type handlers. Subscription lifecycle events trigger tenant
provisioning and state management.

Endpoint:
    POST /api/webhooks/stripe

Handled events:
    - checkout.session.completed
    - customer.subscription.created
    - customer.subscription.updated
    - customer.subscription.deleted
    - invoice.payment_succeeded
    - invoice.payment_failed
    - invoice.finalization_failed

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

import stripe
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from src.integrations.provisioning import (
    BillingChannel,
    activate_tenant,
    auto_provision_superadmin,
    auto_provision_widget_key,
    deactivate_tenant,
    flag_payment_issue,
    provision_tenant,
    update_tenant,
)
from src.integrations.stripe_packs import credit_pack_balance
from src.integrations.stripe_usage import reset_usage

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
if not _WEBHOOK_SECRET:
    logger.warning(
        "STRIPE_WEBHOOK_SECRET is not set — webhook signature verification "
        "will fail. Set this after configuring the webhook in Stripe Dashboard."
    )

# ---------------------------------------------------------------------------
# WI #162: Stripe webhook IP allowlisting (defense-in-depth)
#
# Stripe publishes their webhook source IP ranges. When STRIPE_IP_ALLOWLIST
# is enabled, requests from non-Stripe IPs are rejected before signature
# verification. This is optional — signature verification alone is
# cryptographically sufficient, but IP allowlisting adds network-level
# defense against replay attacks with stolen signatures.
#
# Stripe IP ranges: https://docs.stripe.com/ips#webhook-notifications
# ---------------------------------------------------------------------------

# Stripe webhook source IP ranges (CIDR notation)
# Updated: 2026-02-03. Check Stripe docs for current ranges.
STRIPE_WEBHOOK_IP_RANGES: list[str] = [
    "3.18.12.63",
    "3.130.192.149",
    "13.235.14.237",
    "13.235.122.149",
    "18.211.135.69",
    "35.154.171.200",
    "52.15.183.38",
    "54.88.130.119",
    "54.88.130.237",
    "54.187.174.169",
    "54.187.205.235",
    "54.187.216.72",
]

# Enable IP allowlisting via env var (disabled by default — Stripe CLI uses localhost)
_ENABLE_IP_ALLOWLIST = os.environ.get("STRIPE_IP_ALLOWLIST_ENABLED", "false").lower() == "true"

# Build set for O(1) lookup (individual IPs, not CIDR — Stripe publishes /32s)
_ALLOWED_IPS: set[str] = set(STRIPE_WEBHOOK_IP_RANGES)
# Always allow localhost for development (Stripe CLI forwarding)
_ALLOWED_IPS.update({"127.0.0.1", "::1", "localhost"})


def _check_stripe_ip(request: Request) -> bool:
    """Check if the request originates from a known Stripe IP.

    Checks X-Forwarded-For (if behind a reverse proxy like App Gateway)
    and falls back to the direct client IP.

    Returns True if IP is allowed or allowlisting is disabled.
    """
    if not _ENABLE_IP_ALLOWLIST:
        return True

    # Check X-Forwarded-For first (Azure App Gateway sets this)
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        # First IP in the chain is the original client
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else ""

    if client_ip in _ALLOWED_IPS:
        return True

    logger.warning(
        "Stripe webhook rejected: IP %s not in allowlist (enable_allowlist=%s)",
        client_ip, _ENABLE_IP_ALLOWLIST,
    )
    return False

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])

# ---------------------------------------------------------------------------
# Idempotency tracking
#
# In production, processed event IDs would be stored in Cosmos DB with a
# TTL matching Stripe's retry window (72 hours). For now, we use an
# in-memory set that resets on restart. This is safe for development and
# prevents duplicate processing within a single process lifetime.
# ---------------------------------------------------------------------------

_processed_events: set[str] = set()

_MAX_PROCESSED_CACHE = 10_000  # Prevent unbounded memory growth


def _is_duplicate(event_id: str) -> bool:
    """Check if we've already processed this event."""
    if event_id in _processed_events:
        return True
    if len(_processed_events) >= _MAX_PROCESSED_CACHE:
        # Evict ~half to prevent unbounded growth (arbitrary order — set is unordered).
        # In production, Cosmos DB TTL handles this.
        to_remove = list(_processed_events)[: _MAX_PROCESSED_CACHE // 2]
        for eid in to_remove:
            _processed_events.discard(eid)
    _processed_events.add(event_id)
    return False


# ---------------------------------------------------------------------------
# Event dispatcher
# ---------------------------------------------------------------------------

# Maps Stripe event type strings to handler functions.
# Handlers receive the full event object and return a dict summary.
_EVENT_HANDLERS: dict[str, Any] = {}


def _handles(event_type: str):
    """Decorator to register a handler for a Stripe event type."""

    def decorator(func):
        _EVENT_HANDLERS[event_type] = func
        return func

    return decorator


# ---------------------------------------------------------------------------
# Webhook endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/stripe",
    status_code=200,
    summary="Receive Stripe webhook events",
    description="Receives and processes Stripe webhook events. Verifies signature, checks for duplicates, and dispatches to the appropriate event handler.",
    responses={
        400: {"description": "Invalid payload or signature verification failed"},
        403: {"description": "Webhook source IP not in allowlist"},
        500: {"description": "Webhook secret not configured"},
    },
)
async def stripe_webhook(request: Request) -> JSONResponse:
    """Receive and process Stripe webhook events.

    1. Verify the webhook signature using STRIPE_WEBHOOK_SECRET.
    2. Check for duplicate events (idempotency).
    3. Dispatch to the appropriate event handler.
    4. Return 200 to acknowledge receipt (Stripe retries on non-2xx).
    """
    # WI #162: IP allowlist check (defense-in-depth, before signature verification)
    if not _check_stripe_ip(request):
        raise HTTPException(
            status_code=403,
            detail="Webhook source IP not in allowlist.",
        )

    # Read raw body for signature verification
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if not _WEBHOOK_SECRET:
        logger.error("Cannot verify webhook: STRIPE_WEBHOOK_SECRET not configured.")
        raise HTTPException(
            status_code=500,
            detail="Webhook secret not configured.",
        )

    # Verify signature
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=_WEBHOOK_SECRET,
        )
    except ValueError:
        logger.warning("Webhook payload could not be decoded.")
        raise HTTPException(status_code=400, detail="Invalid payload.")
    except stripe.SignatureVerificationError:
        logger.warning("Webhook signature verification failed.")
        raise HTTPException(status_code=400, detail="Invalid signature.")

    event_id: str = event["id"]
    event_type: str = event["type"]

    # Idempotency check
    if _is_duplicate(event_id):
        logger.info("Duplicate event ignored: %s (%s)", event_id, event_type)
        return JSONResponse(
            status_code=200,
            content={"status": "duplicate", "event_id": event_id},
        )

    # Dispatch to handler
    handler = _EVENT_HANDLERS.get(event_type)
    if handler is None:
        logger.debug("Unhandled event type: %s (%s)", event_type, event_id)
        return JSONResponse(
            status_code=200,
            content={"status": "ignored", "event_type": event_type},
        )

    logger.info("Processing event: %s (%s)", event_type, event_id)

    try:
        result = await handler(event)
    except Exception:
        logger.exception("Error processing event %s (%s)", event_type, event_id)
        # Return 200 to prevent Stripe from retrying an event we can't process.
        # The error is logged for investigation. In production, this would
        # also fire an alert via Application Insights.
        return JSONResponse(
            status_code=200,
            content={"status": "error", "event_id": event_id},
        )

    logger.info("Event processed: %s (%s) → %s", event_type, event_id, result)
    # Return minimal response — detailed result is logged, not exposed via HTTP
    return JSONResponse(
        status_code=200,
        content={"status": "processed", "event_id": event_id, "event_type": event_type},
    )


# ---------------------------------------------------------------------------
# Event handlers
# ---------------------------------------------------------------------------


@_handles("checkout.session.completed")
async def handle_checkout_completed(event: dict) -> dict:
    """Customer completed a Checkout Session.

    Handles two types of checkout completions:

    1. **Subscription checkout** (mode=subscription):
       Primary trigger for tenant provisioning. Calls provision_tenant()
       to create or update the tenant record. The session metadata
       contains the tier, interval, and selected add-ons.

    2. **Pack purchase** (mode=payment, agent_red_pack in metadata):
       Credits the purchased conversation pack to the customer's balance.
       Pack conversations are consumed before overage billing kicks in.
    """
    session = event["data"]["object"]
    metadata = session.get("metadata", {})

    # ---------------------------------------------------------------
    # Conversation pack purchase (one-time payment)
    # ---------------------------------------------------------------
    pack_id = metadata.get("agent_red_pack")
    if pack_id:
        customer_id = session.get("customer")
        conversations_str = metadata.get("agent_red_pack_conversations", "0")

        try:
            conversations = int(conversations_str)
        except (ValueError, TypeError):
            logger.error(
                "Invalid pack conversations value: %s (session=%s)",
                conversations_str,
                session.get("id"),
            )
            conversations = 0

        if customer_id and conversations > 0:
            credit_result = credit_pack_balance(
                stripe_customer_id=customer_id,
                pack_id=pack_id,
                conversations=conversations,
            )

            logger.info(
                "Pack purchase completed: customer=%s pack=%s conversations=%d",
                customer_id,
                pack_id,
                conversations,
            )

            return {
                "action": "pack_purchased",
                "stripe_customer_id": customer_id,
                "pack_id": pack_id,
                "conversations": conversations,
                "total_remaining": credit_result["total_remaining"],
                "checkout_session_id": session.get("id"),
                "amount_total": session.get("amount_total"),
                "currency": session.get("currency"),
            }
        else:
            logger.warning(
                "Pack purchase with missing data: customer=%s conversations=%d session=%s",
                customer_id,
                conversations,
                session.get("id"),
            )
            # Return early — do NOT fall through to subscription provisioning.
            # A pack checkout (identified by agent_red_pack metadata) with
            # corrupt data should be logged and investigated, not treated
            # as a subscription checkout.
            return {
                "action": "pack_purchase_failed",
                "reason": "missing_customer_or_conversations",
                "stripe_customer_id": customer_id,
                "pack_id": pack_id,
                "conversations": conversations,
                "checkout_session_id": session.get("id"),
            }

    # ---------------------------------------------------------------
    # Subscription checkout (recurring billing)
    # ---------------------------------------------------------------
    provisioning_payload = {
        "action": "provision_tenant",
        "stripe_customer_id": session.get("customer"),
        "stripe_subscription_id": session.get("subscription"),
        "customer_email": (
            session.get("customer_details", {}).get("email")
            if session.get("customer_details")
            else None
        ),
        "tier": metadata.get("agent_red_tier"),
        "interval": metadata.get("agent_red_interval"),
        "addons": (
            metadata.get("agent_red_addons", "").split(",")
            if metadata.get("agent_red_addons")
            else []
        ),
        "checkout_session_id": session.get("id"),
        "amount_total": session.get("amount_total"),
        "currency": session.get("currency"),
    }

    logger.info(
        "Tenant provisioning triggered: customer=%s tier=%s interval=%s",
        provisioning_payload["stripe_customer_id"],
        provisioning_payload["tier"],
        provisioning_payload["interval"],
    )

    # Provision tenant via channel-agnostic provisioning service
    tenant = await provision_tenant(
        billing_channel=BillingChannel.STRIPE,
        tier=provisioning_payload["tier"],
        interval=provisioning_payload["interval"],
        addons=provisioning_payload["addons"],
        stripe_customer_id=provisioning_payload["stripe_customer_id"],
        stripe_subscription_id=provisioning_payload["stripe_subscription_id"],
        customer_email=provisioning_payload["customer_email"],
    )
    provisioning_payload["tenant_id"] = tenant.tenant_id
    provisioning_payload["tenant_status"] = tenant.status.value

    # Auto-provision superadmin team member for the new tenant.
    # This creates the owner's per-user API key (shown once in the
    # response). Failures are logged but do not block provisioning.
    superadmin_key = await auto_provision_superadmin(
        tenant_id=tenant.tenant_id,
        customer_email=provisioning_payload["customer_email"] or "",
    )
    if superadmin_key:
        provisioning_payload["superadmin_api_key"] = superadmin_key

    # Auto-provision widget key for the new tenant.
    # This generates a pk_live_ key and stores the hash on TenantDocument.
    # Failures are logged but do not block provisioning.
    widget_key = await auto_provision_widget_key(tenant_id=tenant.tenant_id)
    if widget_key:
        provisioning_payload["widget_key"] = widget_key

    # Send welcome email with credentials (failures don't block provisioning)
    customer_email = provisioning_payload.get("customer_email")
    if customer_email:
        from src.multi_tenant.welcome_email import send_welcome_email

        await send_welcome_email(
            to_email=customer_email,
            tenant_id=tenant.tenant_id,
            superadmin_key=superadmin_key,
            widget_key=widget_key,
            tier=provisioning_payload.get("tier"),
        )

    return provisioning_payload


@_handles("customer.subscription.created")
async def handle_subscription_created(event: dict) -> dict:
    """Subscription activated after successful payment.

    Records the subscription details. In most cases,
    checkout.session.completed fires first and handles provisioning;
    this handler confirms the subscription is active.
    """
    subscription = event["data"]["object"]
    metadata = subscription.get("metadata", {})

    result = {
        "action": "subscription_activated",
        "stripe_subscription_id": subscription["id"],
        "stripe_customer_id": subscription.get("customer"),
        "status": subscription.get("status"),
        "tier": metadata.get("agent_red_tier"),
        "interval": metadata.get("agent_red_interval"),
        "current_period_start": subscription.get("current_period_start"),
        "current_period_end": subscription.get("current_period_end"),
    }

    logger.info(
        "Subscription activated: sub=%s customer=%s tier=%s status=%s",
        result["stripe_subscription_id"],
        result["stripe_customer_id"],
        result["tier"],
        result["status"],
    )

    # Activate tenant — mark as fully operational after payment confirmation
    tenant = await activate_tenant(stripe_customer_id=result["stripe_customer_id"])
    if tenant:
        result["tenant_id"] = tenant.tenant_id
        result["tenant_status"] = tenant.status.value
    else:
        # Tenant may not exist yet if checkout.session.completed hasn't
        # been processed. This is a timing issue — the tenant will be
        # activated when the checkout event arrives.
        logger.warning(
            "No tenant found to activate for customer=%s — "
            "checkout.session.completed may not have been processed yet.",
            result["stripe_customer_id"],
        )

    return result


@_handles("customer.subscription.updated")
async def handle_subscription_updated(event: dict) -> dict:
    """Subscription changed — tier upgrade/downgrade, interval change, or add-on modification.

    Compares previous_attributes to detect what changed.
    """
    subscription = event["data"]["object"]
    previous = event["data"].get("previous_attributes", {})
    metadata = subscription.get("metadata", {})

    changes: list[str] = []

    # Detect status change (e.g., active → past_due)
    if "status" in previous:
        changes.append(f"status: {previous['status']} → {subscription['status']}")

    # Detect plan/item changes
    if "items" in previous:
        changes.append("subscription_items_changed")

    # Detect metadata changes (tier/interval)
    if "metadata" in previous:
        prev_meta = previous["metadata"]
        if prev_meta.get("agent_red_tier") != metadata.get("agent_red_tier"):
            changes.append(
                f"tier: {prev_meta.get('agent_red_tier')} → {metadata.get('agent_red_tier')}"
            )
        if prev_meta.get("agent_red_interval") != metadata.get("agent_red_interval"):
            changes.append(
                f"interval: {prev_meta.get('agent_red_interval')} → {metadata.get('agent_red_interval')}"
            )

    # Detect cancel_at_period_end
    if "cancel_at_period_end" in previous:
        if subscription.get("cancel_at_period_end"):
            changes.append("scheduled_cancellation")
        else:
            changes.append("cancellation_reversed")

    result = {
        "action": "subscription_updated",
        "stripe_subscription_id": subscription["id"],
        "stripe_customer_id": subscription.get("customer"),
        "status": subscription.get("status"),
        "tier": metadata.get("agent_red_tier"),
        "changes": changes,
    }

    logger.info(
        "Subscription updated: sub=%s changes=%s",
        result["stripe_subscription_id"],
        changes,
    )

    # Apply tier/interval/add-on changes to tenant record
    new_tier = metadata.get("agent_red_tier")
    new_interval = metadata.get("agent_red_interval")
    new_addons_str = metadata.get("agent_red_addons", "")
    new_addons = new_addons_str.split(",") if new_addons_str else None

    tenant = await update_tenant(
        tier=new_tier,
        interval=new_interval,
        addons=new_addons,
        stripe_customer_id=result["stripe_customer_id"],
    )
    if tenant:
        result["tenant_id"] = tenant.tenant_id
        result["tenant_status"] = tenant.status.value

    # Respond to subscription status transitions that Stripe reports
    # via subscription.updated (in addition to invoice-level events).
    # This ensures tenant status stays in sync even if invoice events
    # are delayed or arrive out of order.
    current_status = subscription.get("status")
    if "status" in previous and result.get("stripe_customer_id"):
        prev_status = previous["status"]
        if current_status == "past_due" and prev_status != "past_due":
            flagged = await flag_payment_issue(
                stripe_customer_id=result["stripe_customer_id"],
            )
            if flagged:
                result["tenant_status"] = flagged.status.value
        elif current_status == "active" and prev_status == "past_due":
            activated = await activate_tenant(
                stripe_customer_id=result["stripe_customer_id"],
            )
            if activated:
                result["tenant_status"] = activated.status.value

    return result


@_handles("customer.subscription.deleted")
async def handle_subscription_deleted(event: dict) -> dict:
    """Subscription cancelled — begin tenant deactivation.

    Starts a grace period before data deletion. The tenant's access
    is restricted but data is preserved for the grace period defined
    in the SLA (30 days per legal/sla/SERVICE-LEVEL-AGREEMENT.md).
    """
    subscription = event["data"]["object"]
    metadata = subscription.get("metadata", {})

    result = {
        "action": "subscription_cancelled",
        "stripe_subscription_id": subscription["id"],
        "stripe_customer_id": subscription.get("customer"),
        "tier": metadata.get("agent_red_tier"),
        "canceled_at": subscription.get("canceled_at"),
        "ended_at": subscription.get("ended_at"),
        "grace_period_days": 30,
    }

    logger.info(
        "Subscription cancelled: sub=%s customer=%s — 30-day grace period begins",
        result["stripe_subscription_id"],
        result["stripe_customer_id"],
    )

    # Begin tenant deactivation with 30-day grace period
    tenant = await deactivate_tenant(stripe_customer_id=result["stripe_customer_id"])
    if tenant:
        result["tenant_id"] = tenant.tenant_id
        result["tenant_status"] = tenant.status.value
        result["grace_period_ends_at"] = tenant.grace_period_ends_at

    return result


@_handles("invoice.payment_succeeded")
async def handle_payment_succeeded(event: dict) -> dict:
    """Invoice paid successfully — record payment and reset billing cycle.

    This fires for both initial subscription payments and recurring
    renewals. For metered billing, this confirms the overage charges
    for the previous period were collected.
    """
    invoice = event["data"]["object"]

    result = {
        "action": "payment_succeeded",
        "stripe_invoice_id": invoice["id"],
        "stripe_subscription_id": invoice.get("subscription"),
        "stripe_customer_id": invoice.get("customer"),
        "amount_paid": invoice.get("amount_paid"),
        "currency": invoice.get("currency"),
        "billing_reason": invoice.get("billing_reason"),
        "period_start": invoice.get("period_start"),
        "period_end": invoice.get("period_end"),
    }

    logger.info(
        "Payment succeeded: invoice=%s sub=%s amount=%s %s reason=%s",
        result["stripe_invoice_id"],
        result["stripe_subscription_id"],
        result["amount_paid"],
        result["currency"],
        result["billing_reason"],
    )

    # Reset usage counters on subscription renewal so the new billing
    # period starts at zero. "subscription_cycle" indicates a recurring
    # renewal (not the first payment or a manual invoice).
    if result["billing_reason"] == "subscription_cycle" and result["stripe_customer_id"]:
        reset_usage(result["stripe_customer_id"])
        result["usage_reset"] = True

    # Re-activate tenant if payment succeeds (clears past_due status).
    # This covers the case where a previously failed payment retry succeeds.
    if result["stripe_customer_id"]:
        tenant = await activate_tenant(stripe_customer_id=result["stripe_customer_id"])
        if tenant:
            result["tenant_id"] = tenant.tenant_id
            result["tenant_status"] = tenant.status.value
        else:
            # Expected race condition: invoice.payment_succeeded may fire
            # before checkout.session.completed creates the tenant.
            # The tenant will be activated by handle_subscription_created
            # or when checkout.session.completed arrives and provisions it.
            logger.warning(
                "No tenant found to activate for customer=%s — "
                "checkout.session.completed may not have been processed yet.",
                result["stripe_customer_id"],
            )

    return result


@_handles("invoice.payment_failed")
async def handle_payment_failed(event: dict) -> dict:
    """Invoice payment failed — flag the issue and begin retry logic.

    Stripe automatically retries failed payments per the configured
    retry schedule. This handler notifies the customer and flags
    the tenant for potential access restriction.
    """
    invoice = event["data"]["object"]

    result = {
        "action": "payment_failed",
        "stripe_invoice_id": invoice["id"],
        "stripe_subscription_id": invoice.get("subscription"),
        "stripe_customer_id": invoice.get("customer"),
        "amount_due": invoice.get("amount_due"),
        "currency": invoice.get("currency"),
        "attempt_count": invoice.get("attempt_count"),
        "next_payment_attempt": invoice.get("next_payment_attempt"),
        "billing_reason": invoice.get("billing_reason"),
    }

    logger.info(
        "Payment failed: invoice=%s sub=%s amount=%s %s attempt=%s next=%s",
        result["stripe_invoice_id"],
        result["stripe_subscription_id"],
        result["amount_due"],
        result["currency"],
        result["attempt_count"],
        (
            datetime.fromtimestamp(result["next_payment_attempt"], tz=timezone.utc).isoformat()
            if result["next_payment_attempt"]
            else "no_retry"
        ),
    )

    # Flag tenant for payment issue (sets status to PAST_DUE)
    if result["stripe_customer_id"]:
        tenant = await flag_payment_issue(stripe_customer_id=result["stripe_customer_id"])
        if tenant:
            result["tenant_id"] = tenant.tenant_id
            result["tenant_status"] = tenant.status.value

    # TODO (Phase 2.2): Send payment failure notification to customer
    # await notification_service.send_payment_failed(result)

    return result


@_handles("invoice.finalization_failed")
async def handle_finalization_failed(event: dict) -> dict:
    """Invoice could not be finalized — likely a Stripe Tax failure.

    When ``automatic_tax`` is enabled on subscriptions, Stripe Tax must
    determine the customer's location to calculate tax. If the customer's
    address is missing or invalid, the invoice cannot be finalized and
    this event fires. Without handling it, subscription renewals silently
    stall.

    The ``automatic_tax.status`` field on the invoice indicates the
    cause:
      - ``requires_location_inputs`` — address data is insufficient
      - ``failed`` — tax calculation encountered an error
      - ``complete`` — tax was calculated (unlikely in this event)
    """
    invoice = event["data"]["object"]
    automatic_tax = invoice.get("automatic_tax", {})
    last_error = invoice.get("last_finalization_error", {})

    result = {
        "action": "invoice_finalization_failed",
        "stripe_invoice_id": invoice["id"],
        "stripe_subscription_id": invoice.get("subscription"),
        "stripe_customer_id": invoice.get("customer"),
        "automatic_tax_status": automatic_tax.get("status"),
        "error_type": last_error.get("type"),
        "error_message": last_error.get("message"),
    }

    logger.warning(
        "Invoice finalization failed: invoice=%s customer=%s "
        "tax_status=%s error=%s",
        result["stripe_invoice_id"],
        result["stripe_customer_id"],
        result["automatic_tax_status"],
        result["error_message"] or result["error_type"] or "unknown",
    )

    # Flag the tenant so the customer portal can prompt for address update
    if result["stripe_customer_id"]:
        tenant = await flag_payment_issue(
            stripe_customer_id=result["stripe_customer_id"],
        )
        if tenant:
            result["tenant_id"] = tenant.tenant_id
            result["tenant_status"] = tenant.status.value

    # TODO (Phase 2.2): Send notification asking customer to update
    # their billing address via the Stripe Customer Portal.

    return result
