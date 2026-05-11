# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Sales Agent — In-line Purchase Completion MCP Server (SPEC-1709).

Enables product discovery, cart management, and checkout within the
chat interface.  Integrates with Shopify Storefront API, Stripe,
and order management systems.

PCI scope: Payment operations generate secure checkout links rather
than handling card data directly.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

AGENT_ID = "sales"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


@dataclass
class CartItem:
    """Item in a shopping cart."""

    product_id: str
    variant_id: str = ""
    product_name: str = ""
    quantity: int = 1
    unit_price: float = 0.0

    @property
    def total_price(self) -> float:
        return self.unit_price * self.quantity


@dataclass
class Cart:
    """Shopping cart for a conversation."""

    cart_id: str
    tenant_id: str
    conversation_id: str
    items: list[CartItem] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    @property
    def total(self) -> float:
        return sum(item.total_price for item in self.items)

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)


@dataclass
class ProductResult:
    """Search result for a product."""

    product_id: str
    title: str
    description: str = ""
    price: float = 0.0
    currency: str = "USD"
    available: bool = True
    image_url: str = ""
    variants: list[dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Agent tools
# ---------------------------------------------------------------------------


class SalesAgentTools:
    """Tool implementations for the Sales Agent.

    Each method maps to an MCP tool capability defined in agents.yaml.
    """

    def __init__(self) -> None:
        self._carts: dict[str, Cart] = {}  # conversation_id → cart
        self._products: dict[str, list[ProductResult]] = {}  # tenant_id → catalog

    async def search_products(
        self,
        tenant_id: str,
        query: str,
        *,
        limit: int = 10,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search product catalog.

        Tool: sales.search_products

        In production, delegates to Shopify Storefront API.
        """
        products = self._products.get(tenant_id, [])
        query_lower = query.lower()

        results = [
            p for p in products
            if query_lower in p.title.lower() or query_lower in p.description.lower()
        ]

        if category:
            results = [p for p in results if category.lower() in p.description.lower()]

        return [
            {
                "product_id": p.product_id,
                "title": p.title,
                "description": p.description,
                "price": p.price,
                "currency": p.currency,
                "available": p.available,
                "image_url": p.image_url,
            }
            for p in results[:limit]
        ]

    async def manage_cart(
        self,
        tenant_id: str,
        conversation_id: str,
        action: str,
        *,
        product_id: str = "",
        variant_id: str = "",
        quantity: int = 1,
    ) -> dict[str, Any]:
        """Manage shopping cart (add, remove, update, clear, view).

        Tool: sales.manage_cart
        """
        cart_key = conversation_id
        if cart_key not in self._carts:
            self._carts[cart_key] = Cart(
                cart_id=f"cart-{conversation_id}",
                tenant_id=tenant_id,
                conversation_id=conversation_id,
            )
        cart = self._carts[cart_key]

        if action == "add":
            # Look up product
            product = self._find_product(tenant_id, product_id)
            item = CartItem(
                product_id=product_id,
                variant_id=variant_id,
                product_name=product.title if product else product_id,
                quantity=quantity,
                unit_price=product.price if product else 0.0,
            )
            cart.items.append(item)

        elif action == "remove":
            cart.items = [i for i in cart.items if i.product_id != product_id]

        elif action == "update":
            for item in cart.items:
                if item.product_id == product_id:
                    item.quantity = quantity
                    break

        elif action == "clear":
            cart.items = []

        return {
            "cart_id": cart.cart_id,
            "item_count": cart.item_count,
            "total": cart.total,
            "items": [
                {
                    "product_id": i.product_id,
                    "product_name": i.product_name,
                    "quantity": i.quantity,
                    "unit_price": i.unit_price,
                    "total_price": i.total_price,
                }
                for i in cart.items
            ],
        }

    async def check_inventory(
        self,
        tenant_id: str,
        product_id: str,
        *,
        variant_id: str = "",
    ) -> dict[str, Any]:
        """Check product inventory/availability.

        Tool: sales.check_inventory
        """
        product = self._find_product(tenant_id, product_id)
        if not product:
            return {"available": False, "error": "Product not found"}

        return {
            "product_id": product_id,
            "title": product.title,
            "available": product.available,
            "price": product.price,
        }

    async def create_checkout(
        self,
        tenant_id: str,
        conversation_id: str,
        *,
        email: str = "",
    ) -> dict[str, Any]:
        """Create a secure checkout link for the current cart.

        Tool: sales.create_checkout

        PCI note: Generates a link to the hosted checkout page.
        Card data is never handled directly.
        """
        cart = self._carts.get(conversation_id)
        if not cart or not cart.items:
            return {"error": "Cart is empty"}

        # In production, this would call Shopify/Stripe checkout API
        checkout_url = f"https://checkout.example.com/{cart.cart_id}"

        return {
            "checkout_url": checkout_url,
            "cart_id": cart.cart_id,
            "total": cart.total,
            "item_count": cart.item_count,
            "email": email,
        }

    async def track_order(
        self,
        tenant_id: str,
        order_id: str,
    ) -> dict[str, Any]:
        """Track an order by ID.

        Tool: sales.track_order
        """
        # In production, delegates to order management system
        return {
            "order_id": order_id,
            "status": "processing",
            "tracking_url": "",
            "note": "Order tracking via Shopify/Stripe API",
        }

    # -- Helpers ------------------------------------------------------------

    def _find_product(
        self, tenant_id: str, product_id: str
    ) -> ProductResult | None:
        """Find a product by ID in the tenant's catalog."""
        products = self._products.get(tenant_id, [])
        return next((p for p in products if p.product_id == product_id), None)

    def seed_products(self, tenant_id: str, products: list[ProductResult]) -> None:
        """Seed product catalog for testing."""
        self._products[tenant_id] = products
