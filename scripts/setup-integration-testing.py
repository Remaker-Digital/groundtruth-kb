#!/usr/bin/env python3
"""
Integration testing setup script.

This script helps configure the environment for integration testing with
real Stripe test mode and Shopify partner sandbox. It validates credentials,
creates necessary Stripe products, and verifies the setup.

Usage:
    python scripts/setup-integration-testing.py

Prerequisites:
    - Stripe test account with API keys
    - Shopify Partner account with app created
    - Environment variables configured in .env.local

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to sys.path so 'src' package is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import stripe

# Load .env.local (shared loader — R7 refactoring)
from scripts._env import load_env_local


def load_environment() -> bool:
    """Load environment variables from .env.local."""
    env_file = Path(".env.local")
    if not env_file.exists():
        print("❌ .env.local file not found")
        print("   Create .env.local with your Stripe and Shopify credentials")
        print("   See docs/INTEGRATION-TESTING-SETUP.md for details")
        return False

    load_env_local()
    print(f"✅ Loaded environment from {env_file}")
    return True


def validate_stripe_config() -> bool:
    """Validate Stripe configuration and test API connectivity."""
    print("\n🔍 Validating Stripe configuration...")
    
    api_key = os.environ.get("STRIPE_SECRET_KEY", "")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    
    if not api_key:
        print("❌ STRIPE_SECRET_KEY not set")
        return False
    
    if not api_key.startswith("sk_test_"):
        print("❌ STRIPE_SECRET_KEY must be a test mode key (sk_test_...)")
        print("   Never use live keys for integration testing!")
        return False
    
    if not webhook_secret:
        print("❌ STRIPE_WEBHOOK_SECRET not set")
        return False
    
    if not webhook_secret.startswith("whsec_"):
        print("❌ STRIPE_WEBHOOK_SECRET must start with 'whsec_'")
        return False
    
    # Test API connectivity
    stripe.api_key = api_key
    try:
        account = stripe.Account.retrieve()
        print(f"✅ Stripe API connection successful")
        print(f"   Account ID: {account.id}")
        print(f"   Country: {account.get('country', 'unknown')}")

        # Check live mode - handle different Stripe SDK versions
        is_livemode = account.get("livemode", None)
        if is_livemode is None:
            # Newer SDK versions or sandbox: infer from API key prefix
            is_test = api_key.startswith("sk_test_")
            print(f"   Test mode: {is_test} (inferred from API key prefix)")
            if not is_test:
                print("❌ API key is not a test key - use test mode only!")
                return False
        else:
            print(f"   Test mode: {not is_livemode}")
            if is_livemode:
                print("❌ Account is in live mode - use test mode only!")
                return False
        
    except stripe.StripeError as e:
        print(f"❌ Stripe API connection failed: {e}")
        return False
    
    return True


def validate_shopify_config() -> bool:
    """Validate Shopify configuration."""
    print("\n🔍 Validating Shopify configuration...")
    
    api_key = os.environ.get("SHOPIFY_API_KEY", "")
    api_secret = os.environ.get("SHOPIFY_API_SECRET", "")
    
    if not api_key:
        print("❌ SHOPIFY_API_KEY not set")
        return False
    
    if not api_secret:
        print("❌ SHOPIFY_API_SECRET not set")
        return False
    
    print(f"✅ Shopify API credentials configured")
    print(f"   API Key: {api_key[:8]}...")
    print(f"   API Secret: {api_secret[:8]}...")
    
    # Note: We can't easily test Shopify API connectivity without a shop domain
    # and access token, which requires app installation
    print("   ⚠️  Full Shopify API testing requires app installation on a test store")
    
    return True


def check_stripe_products() -> bool:
    """Check if Stripe products exist and are properly configured."""
    print("\n🔍 Checking Stripe product catalog...")
    
    catalog_file = Path("config/stripe_product_ids.json")
    if not catalog_file.exists():
        print("❌ config/stripe_product_ids.json not found")
        return False
    
    try:
        with open(catalog_file) as f:
            catalog = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in catalog file: {e}")
        return False
    
    if catalog.get("mode") != "test":
        print("❌ Catalog is not in test mode")
        return False
    
    print("✅ Product catalog loaded")
    
    # Verify products exist in Stripe
    missing_products = []
    
    for tier_name, tier_data in catalog.get("tiers", {}).items():
        product_id = tier_data.get("product_id")
        if product_id:
            try:
                product = stripe.Product.retrieve(product_id)
                print(f"   ✅ {tier_name}: {product.name}")
            except stripe.StripeError:
                missing_products.append(f"{tier_name} ({product_id})")
    
    for pack_name, pack_data in catalog.get("packs", {}).items():
        product_id = pack_data.get("product_id")
        if product_id:
            try:
                product = stripe.Product.retrieve(product_id)
                print(f"   ✅ {pack_name}: {product.name}")
            except stripe.StripeError:
                missing_products.append(f"{pack_name} ({product_id})")
    
    if missing_products:
        print(f"❌ Missing products in Stripe: {', '.join(missing_products)}")
        print("   Run: python scripts/stripe/create_product_catalog.py")
        return False
    
    return True


def test_webhook_endpoint() -> bool:
    """Test webhook endpoint configuration."""
    print("\n🔍 Testing webhook endpoint...")
    
    base_url = os.environ.get("APP_BASE_URL", "http://localhost:8080")
    webhook_url = f"{base_url}/api/webhooks/stripe"
    
    print(f"   Webhook URL: {webhook_url}")
    
    # List webhook endpoints to see if ours is configured
    try:
        endpoints = stripe.WebhookEndpoint.list()
        
        matching_endpoints = [
            ep for ep in endpoints.data 
            if webhook_url in ep.url
        ]
        
        if matching_endpoints:
            endpoint = matching_endpoints[0]
            print(f"✅ Webhook endpoint found: {endpoint.id}")
            print(f"   Status: {endpoint.status}")
            print(f"   Events: {len(endpoint.enabled_events)} configured")
            
            required_events = {
                "checkout.session.completed",
                "customer.subscription.created", 
                "customer.subscription.updated",
                "customer.subscription.deleted",
                "invoice.payment_succeeded",
                "invoice.payment_failed",
                "invoice.finalization_failed",
            }
            
            configured_events = set(endpoint.enabled_events)
            missing_events = required_events - configured_events
            
            if missing_events:
                print(f"   ⚠️  Missing events: {', '.join(missing_events)}")
            else:
                print("   ✅ All required events configured")
            
        else:
            print(f"ℹ️  No dashboard webhook endpoint found for {webhook_url}")
            print("   This is OK if using Stripe CLI: stripe listen --forward-to localhost:8000/api/webhooks/stripe")
        
    except stripe.StripeError as e:
        print(f"❌ Failed to list webhook endpoints: {e}")
        return False
    
    return True


def create_test_env_template() -> None:
    """Create a .env.local template if it doesn't exist."""
    env_file = Path(".env.local")
    if env_file.exists():
        return
    
    template = """# Agent Red Integration Testing Configuration
# Copy your actual values here - never commit this file!

# Enable real API integration testing
USE_REAL_APIS=true

# Stripe test mode configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_test_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Shopify partner app configuration  
SHOPIFY_API_KEY=your_shopify_api_key_here
SHOPIFY_API_SECRET=your_shopify_api_secret_here

# Application configuration
APP_BASE_URL=http://localhost:8080
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Optional: Shopify billing test mode
SHOPIFY_BILLING_TEST=true
"""
    
    with open(env_file, "w") as f:
        f.write(template)
    
    print(f"📝 Created {env_file} template")
    print("   Edit this file with your actual credentials")


def run_sample_integration_test() -> bool:
    """Run a simple integration test to verify everything works."""
    print("\n🧪 Running sample integration test...")
    
    try:
        # Test Stripe checkout session creation
        from src.integrations.stripe_catalog import load_catalog
        
        catalog = load_catalog()
        tier = catalog.get_tier("starter")
        
        # Create a minimal checkout session
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{
                "price": tier.monthly_price_id,
                "quantity": 1,
            }],
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            metadata={"test": "integration_setup"},
        )
        
        print(f"✅ Test checkout session created: {session.id}")
        print(f"   URL: {session.url}")
        
        # Clean up - expire the session
        stripe.checkout.Session.expire(session.id)
        print("✅ Test session cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample test failed: {e}")
        return False


def main() -> int:
    """Main setup function."""
    print("🚀 Agent Red Integration Testing Setup")
    print("=" * 50)
    
    # Load environment
    if not load_environment():
        create_test_env_template()
        return 1
    
    # Validate configurations
    stripe_ok = validate_stripe_config()
    shopify_ok = validate_shopify_config()
    
    if not stripe_ok:
        print("\n❌ Stripe configuration failed")
        print("   See docs/INTEGRATION-TESTING-SETUP.md for setup instructions")
        return 1
    
    if not shopify_ok:
        print("\n❌ Shopify configuration failed") 
        print("   See docs/INTEGRATION-TESTING-SETUP.md for setup instructions")
        return 1
    
    # Check products
    if not check_stripe_products():
        print("\n❌ Product catalog validation failed")
        return 1
    
    # Test webhook setup
    test_webhook_endpoint()
    
    # Run sample test
    if not run_sample_integration_test():
        print("\n❌ Sample integration test failed")
        return 1
    
    print("\n🎉 Integration testing setup complete!")
    print("\nNext steps:")
    print("1. Start the application: uvicorn src.main:app --reload --port 8080")
    print("2. Run integration tests: pytest tests/integration_real_services.py -v")
    print("3. Optional: Use Stripe CLI for webhook testing")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())