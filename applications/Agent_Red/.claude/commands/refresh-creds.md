---
description: "Refresh test credentials from Azure Key Vault and update .env.local."
argument-hint: "[staging|prod] [--verify]"
---

# Refresh Test Credentials

Pull current credentials from Azure Key Vault and update .env.local.

## Behavior

```bash
python scripts/refresh_test_credentials.py --env ${ARGUMENTS:-staging}
```

Use `--verify` to just check current credentials without refreshing.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
