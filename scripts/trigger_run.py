"""Trigger a test run on staging."""

import json
import os
import sys
import urllib.request

from _env import load_env_local

load_env_local()

suite = sys.argv[1] if len(sys.argv) > 1 else "pipeline"
base = os.environ.get("STAGING_URL", "")  # SPEC-0058: No hardcoded FQDNs
if not base:
    print("Error: STAGING_URL env var not set", file=sys.stderr)
    sys.exit(1)
url = f"{base}/api/superadmin/tests/run"

# SPEC-0058: API key from env var, not hardcoded
spa = os.environ.get("STAGING_SPA_KEY", "")
if not spa:
    print("Error: STAGING_SPA_KEY env var not set", file=sys.stderr)
    sys.exit(1)
body = json.dumps({"suite": suite, "environment": "staging"}).encode()
req = urllib.request.Request(
    url,
    data=body,
    headers={
        "X-API-Key": spa,
        "Content-Type": "application/json",
    },
)

with urllib.request.urlopen(req, timeout=60) as resp:
    data = json.loads(resp.read())
    print(json.dumps(data, indent=2))
