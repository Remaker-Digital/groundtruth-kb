# Integration Testing Setup Guide

This guide explains how to set up and run integration tests with real Stripe test mode and Shopify partner sandbox.

## Prerequisites

### 1. Stripe Test Mode Setup

1. **Create a Stripe account** (if you don't have one):
   - Go to https://stripe.com and sign up
   - Verify your email address

2. **Get your test API keys**:
   - Go to Stripe Dashboard → Developers → API keys
   - Copy your "Secret key" (starts with `sk_test_`)
   - **Never use live keys** - only test keys for integration testing

3. **Create a webhook endpoint**:
   - Go to Stripe Dashboard → Developers → Webhooks
   - Click "Add endpoint"
   - Endpoint URL: `http://localhost:8080/api/webhooks/stripe` (or your local URL)
   - Select events to send:
     - `checkout.session.completed`
     - `customer.subscription.created`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `invoice.payment_succeeded`
     - `invoice.payment_failed`
     - `invoice.finalization_failed`
   - Copy the "Signing secret" (starts with `whsec_`)

4. **Verify your products exist**:
   - The integration tests use the product IDs from `config/stripe_product_ids.json`
   - These should already exist in your Stripe test account
   - If not, run: `python scripts/stripe/create_product_catalog.py`

### 2. Shopify Partner Setup

1. **Create a Shopify Partner account**:
   - Go to https://partners.shopify.com and sign up
   - Complete the partner onboarding

2. **Create a test app**:
   - In Partner Dashboard → Apps → Create app
   - Choose "Custom app" or "Public app"
   - App name: "Agent Red Customer Experience (Test)"
   - App URL: `http://localhost:8080` (or your local URL)

3. **Configure app settings**:
   - Go to App setup → App details
   - Copy your "API key" and "API secret key"
   - Add redirect URLs:
     - `http://localhost:8080/api/shopify/billing/confirm`
     - `http://localhost:8080/auth/shopify/callback`

4. **Set up billing permissions**:
   - Go to App setup → App permissions
   - Enable "Billing" permission
   - Save the configuration

5. **Create a development store** (optional):
   - Partner Dashboard → Stores → Create store
   - Choose "Development store"
   - Install your test app on this store

### 3. Environment Configuration

Create a `.env.local` file in the project root:

```bash
# Copy from .env.example and fill in your values

# Enable real API integration testing
USE_REAL_APIS=true

# Stripe test mode configuration
STRIPE_SECRET_KEY=sk_test_your_stripe_test_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here

# Shopify partner app configuration
SHOPIFY_API_KEY=your_shopify_api_key_here
SHOPIFY_API_SECRET=your_shopify_api_secret_here

# Application base URL (for redirects)
APP_BASE_URL=http://localhost:8080

# Optional: Enable Shopify billing test mode
SHOPIFY_BILLING_TEST=true
```

**Security Note**: Never commit `.env.local` or any file containing real credentials to version control.

## Running Integration Tests

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### 2. Start the Application

```bash
# In one terminal
uvicorn src.main:app --reload --port 8080
```

### 3. Run Integration Tests

```bash
# Run all integration tests
pytest tests/integration_real_services.py -v

# Run specific test class
pytest tests/integration_real_services.py::TestStripeCheckoutIntegration -v

# Run with detailed output
pytest tests/integration_real_services.py -v -s

# Run configuration validation only
pytest tests/integration_real_services.py::test_stripe_configuration -v
pytest tests/integration_real_services.py::test_shopify_configuration -v
```

### 4. Test with Stripe CLI (Optional)

For more realistic webhook testing, use Stripe CLI to forward real events:

```bash
# Install Stripe CLI: https://stripe.com/docs/stripe-cli
stripe login

# Forward webhooks to your local server
stripe listen --forward-to localhost:8080/api/webhooks/stripe

# In another terminal, trigger test events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.created
```

## Test Coverage

The integration tests cover:

### Stripe Integration
- ✅ Checkout Session creation (all tiers, intervals, add-ons)
- ✅ Webhook signature verification
- ✅ Webhook event processing and idempotency
- ✅ Tenant provisioning and lifecycle management
- ✅ Conversation pack purchases
- ✅ Error handling and edge cases

### Shopify Integration
- ✅ Subscription creation via Billing API
- ✅ Billing status queries
- ✅ GraphQL API error handling
- ⚠️ Full flow testing (requires app installation)

### Cross-Channel Testing
- ✅ Tenant lookup by Stripe customer ID
- ✅ Tenant lookup by Shopify shop domain
- ✅ Channel-agnostic provisioning service
- ✅ End-to-end billing flows

## Troubleshooting

### Common Issues

1. **"STRIPE_SECRET_KEY must be a test mode key"**
   - Ensure your key starts with `sk_test_`
   - Never use live keys (`sk_live_`) in tests

2. **"Invalid signature" webhook errors**
   - Verify your `STRIPE_WEBHOOK_SECRET` is correct
   - Check that it starts with `whsec_`
   - Ensure the webhook endpoint is configured correctly

3. **"No such price" Stripe errors**
   - Run `python scripts/stripe/create_product_catalog.py` to create products
   - Verify `config/stripe_product_ids.json` has valid test mode IDs

4. **Shopify GraphQL errors**
   - Verify your `SHOPIFY_API_KEY` and `SHOPIFY_API_SECRET` are correct
   - Ensure your app has billing permissions enabled
   - Check that your app is properly configured in Partner Dashboard

5. **Connection refused errors**
   - Ensure the application is running on the expected port
   - Check that `APP_BASE_URL` matches your local server

### Debug Mode

Enable debug logging for more detailed output:

```bash
# Set log level in .env.local
LOG_LEVEL=DEBUG

# Run tests with debug output
pytest tests/integration_real_services.py -v -s --log-cli-level=DEBUG
```

### Manual Testing

You can also test the endpoints manually:

```bash
# Test Stripe checkout creation
curl -X POST http://localhost:8080/api/checkout/session \
  -H "Content-Type: application/json" \
  -d '{"tier": "starter", "interval": "month"}'

# Test tenant lookup
curl "http://localhost:8080/api/tenants/lookup?stripe_customer_id=cus_test_123"

# Test Shopify billing (requires valid shop domain)
curl -X POST http://localhost:8080/api/shopify/billing/subscribe \
  -H "Content-Type: application/json" \
  -d '{"tier": "starter", "interval": "month", "shop_domain": "test-shop.myshopify.com"}'
```

## CI/CD Integration

For automated testing in CI/CD pipelines:

1. **Store secrets securely**:
   - Use GitHub Secrets, Azure Key Vault, or similar
   - Never commit credentials to the repository

2. **Skip tests when credentials unavailable**:
   - Tests automatically skip when `USE_REAL_APIS=false`
   - Use `@pytest.mark.skipif` for conditional testing

3. **Use test-specific Stripe account**:
   - Create a dedicated Stripe account for CI testing
   - Use separate webhook endpoints for different environments

## Security Considerations

1. **Test mode only**: Never use live Stripe keys or real Shopify stores
2. **Credential rotation**: Regularly rotate API keys and webhook secrets
3. **Network isolation**: Run tests in isolated environments when possible
4. **Audit logging**: Monitor API usage and webhook deliveries
5. **Rate limiting**: Be aware of API rate limits during testing

## Next Steps

After integration testing passes:

1. **Deploy to staging**: Test with staging environment
2. **End-to-end testing**: Test complete user flows in browser
3. **Load testing**: Validate performance under realistic load
4. **Security testing**: Run security scans and penetration tests
5. **Production deployment**: Deploy with confidence

---

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.