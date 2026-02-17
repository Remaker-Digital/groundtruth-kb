#!/usr/bin/env python3
"""
Integration test runner script.

This script runs the integration tests with proper environment setup
and provides detailed reporting of test results.

Usage:
    python scripts/run-integration-tests.py [test_pattern]

Examples:
    python scripts/run-integration-tests.py                    # Run all tests
    python scripts/run-integration-tests.py stripe             # Run Stripe tests only
    python scripts/run-integration-tests.py shopify            # Run Shopify tests only
    python scripts/run-integration-tests.py config             # Run config validation only

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# Load .env.local (shared loader — R7 refactoring)
from scripts._env import load_env_local


def load_test_environment() -> bool:
    """Load test environment configuration."""
    env_file = Path(".env.local")
    if env_file.exists():
        load_env_local()
        print(f"✅ Loaded environment from {env_file}")
        return True
    else:
        print("❌ .env.local not found")
        print("   Run: python scripts/setup-integration-testing.py")
        return False


def check_prerequisites() -> bool:
    """Check that all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Check USE_REAL_APIS
    if os.environ.get("USE_REAL_APIS", "false").lower() != "true":
        print("❌ USE_REAL_APIS must be set to 'true' for integration testing")
        return False
    
    # Check Stripe credentials
    stripe_key = os.environ.get("STRIPE_SECRET_KEY", "")
    if not stripe_key.startswith("sk_test_"):
        print("❌ STRIPE_SECRET_KEY must be a test mode key (sk_test_...)")
        return False
    
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    if not webhook_secret.startswith("whsec_"):
        print("❌ STRIPE_WEBHOOK_SECRET must be set")
        return False
    
    print("✅ Prerequisites check passed")
    return True


def build_pytest_command(test_pattern: Optional[str] = None) -> List[str]:
    """Build the pytest command with appropriate options."""
    cmd = [
        "python", "-m", "pytest",
        "tests/integration_real_services.py",
        "-v",  # Verbose output
        "-s",  # Don't capture output
        "--tb=short",  # Short traceback format
        "--color=yes",  # Colored output
    ]
    
    # Add test pattern filtering
    if test_pattern:
        if test_pattern == "config":
            cmd.extend(["-k", "test_stripe_configuration or test_shopify_configuration or test_stripe_catalog"])
        elif test_pattern == "stripe":
            cmd.extend(["-k", "Stripe"])
        elif test_pattern == "shopify":
            cmd.extend(["-k", "Shopify"])
        elif test_pattern == "webhook":
            cmd.extend(["-k", "webhook"])
        elif test_pattern == "e2e":
            cmd.extend(["-k", "EndToEnd"])
        else:
            cmd.extend(["-k", test_pattern])
    
    return cmd


def run_tests(test_pattern: Optional[str] = None) -> int:
    """Run the integration tests."""
    print(f"\n🧪 Running integration tests{f' (pattern: {test_pattern})' if test_pattern else ''}...")
    print("=" * 60)
    
    cmd = build_pytest_command(test_pattern)
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 130
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return 1


def print_usage() -> None:
    """Print usage information."""
    print("Usage: python scripts/run-integration-tests.py [test_pattern]")
    print()
    print("Test patterns:")
    print("  config    - Run configuration validation tests only")
    print("  stripe    - Run Stripe integration tests only")
    print("  shopify   - Run Shopify integration tests only")
    print("  webhook   - Run webhook processing tests only")
    print("  e2e       - Run end-to-end flow tests only")
    print("  <custom>  - Run tests matching custom pattern")
    print()
    print("Examples:")
    print("  python scripts/run-integration-tests.py")
    print("  python scripts/run-integration-tests.py stripe")
    print("  python scripts/run-integration-tests.py config")


def main() -> int:
    """Main function."""
    print("🚀 Agent Red Integration Test Runner")
    print("=" * 40)
    
    # Parse command line arguments
    test_pattern = None
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help", "help"]:
            print_usage()
            return 0
        test_pattern = sys.argv[1]
    
    # Load environment
    if not load_test_environment():
        return 1
    
    # Check prerequisites
    if not check_prerequisites():
        return 1
    
    # Run tests
    exit_code = run_tests(test_pattern)
    
    # Print summary
    print("\n" + "=" * 60)
    if exit_code == 0:
        print("🎉 All integration tests passed!")
    elif exit_code == 130:
        print("⚠️  Tests were interrupted")
    else:
        print(f"❌ Integration tests failed (exit code: {exit_code})")
        print("\nTroubleshooting:")
        print("1. Check your .env.local configuration")
        print("2. Verify Stripe test account setup")
        print("3. Ensure webhook endpoints are configured")
        print("4. Run: python scripts/setup-integration-testing.py")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())