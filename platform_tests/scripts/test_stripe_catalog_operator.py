"""The catalog operator preserves its mapped-product-only update mode offline."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def operator(monkeypatch, tmp_path):
    error_type = type("StripeError", (Exception,), {})
    stripe = SimpleNamespace(
        api_key=None,
        StripeError=error_type,
        Product=SimpleNamespace(retrieve=Mock(), modify=Mock()),
        StripeClient=Mock(side_effect=AssertionError("Creation is forbidden in update mode")),
    )
    monkeypatch.setitem(sys.modules, "stripe", stripe)
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    spec = importlib.util.spec_from_file_location("catalog_operator", ROOT / "scripts/stripe/create_product_catalog.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert stripe.api_key is None
    assert module.OUTPUT_PATH == ROOT / "applications/Agent_Red/config/stripe_product_ids.json"
    monkeypatch.setattr(module, "OUTPUT_PATH", tmp_path / "catalog.json")
    return module, stripe


def test_missing_key_refuses_before_any_stripe_operation(operator):
    module, stripe = operator
    assert module.main([]) == 1
    stripe.StripeClient.assert_not_called()
    stripe.Product.retrieve.assert_not_called()
    stripe.Product.modify.assert_not_called()


def test_update_only_uses_exact_mapping_and_rerun_changes_nothing(operator, monkeypatch):
    module, stripe = operator
    monkeypatch.setenv("STRIPE_SECRET_KEY", "fixture-key")
    catalog = {
        "tiers": {"old_custom_name": {"product_id": "prod_old"}},
        "packs": {"pack": {"product_id": "prod_pack"}},
        "addons": {"addon": {"product_id": "prod_addon"}},
    }
    module.OUTPUT_PATH.write_text(json.dumps(catalog), encoding="utf-8")
    before = module.OUTPUT_PATH.read_bytes()
    products = {
        "prod_old": SimpleNamespace(tax_code="wrong"),
        "prod_pack": SimpleNamespace(),
        "prod_addon": SimpleNamespace(tax_code=module.TAX_CODE_SAAS_B2B),
    }
    stripe.Product.retrieve.side_effect = products.__getitem__

    def modify(product_id, *, tax_code):
        products[product_id].tax_code = tax_code

    stripe.Product.modify.side_effect = modify
    assert module.main(["--update-tax-codes"]) == 0
    assert [call.args[0] for call in stripe.Product.retrieve.call_args_list] == list(products)
    assert [call.args[0] for call in stripe.Product.modify.call_args_list] == ["prod_old", "prod_pack"]
    assert module.main(["--update-tax-codes"]) == 0
    assert stripe.Product.modify.call_count == 2
    stripe.StripeClient.assert_not_called()
    assert module.OUTPUT_PATH.read_bytes() == before


@pytest.mark.parametrize("operation", ["retrieve", "modify"])
def test_tax_update_failure_is_nonzero_and_preserves_mapping(operator, monkeypatch, operation):
    module, stripe = operator
    monkeypatch.setenv("STRIPE_SECRET_KEY", "fixture-key")
    module.OUTPUT_PATH.write_text('{"tiers":{"x":{"product_id":"prod_x"}}}', encoding="utf-8")
    before = module.OUTPUT_PATH.read_bytes()
    stripe.Product.retrieve.return_value = SimpleNamespace(tax_code=None)
    getattr(stripe.Product, operation).side_effect = stripe.StripeError("fixture failure")
    assert module.main(["--update-tax-codes"]) == 1
    assert module.OUTPUT_PATH.read_bytes() == before
    stripe.StripeClient.assert_not_called()


@pytest.mark.parametrize(
    "catalog",
    [
        None,
        "{",
        "{}",
        '{"tiers": []}',
        '{"tiers":{"valid":{"product_id":"prod_good"},"invalid":{"product_id":"bad id"}}}',
    ],
)
def test_invalid_catalog_refuses_before_first_remote_effect(operator, monkeypatch, catalog):
    module, stripe = operator
    monkeypatch.setenv("STRIPE_SECRET_KEY", "fixture-key")
    if catalog is not None:
        module.OUTPUT_PATH.write_text(catalog, encoding="utf-8")
    assert module.main(["--update-tax-codes"]) == 1
    stripe.Product.retrieve.assert_not_called()
    stripe.Product.modify.assert_not_called()
    stripe.StripeClient.assert_not_called()


def test_catalog_creation_failure_preserves_previous_mapping(operator, monkeypatch):
    module, stripe = operator
    monkeypatch.setenv("STRIPE_SECRET_KEY", "fixture-key")
    module.OUTPUT_PATH.write_text("previous mapping", encoding="utf-8")
    stripe.StripeClient.side_effect = None
    monkeypatch.setattr(module, "ensure_billing_meter", lambda client: "meter_fixture")
    monkeypatch.setattr(module, "create_subscription_tiers", Mock(side_effect=stripe.StripeError("creation failed")))
    assert module.main([]) == 1
    assert module.OUTPUT_PATH.read_text(encoding="utf-8") == "previous mapping"
