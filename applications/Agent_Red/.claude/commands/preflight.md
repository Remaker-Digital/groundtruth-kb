---
description: "Run pre-deployment checklist against staging or production environment."
argument-hint: "[staging|prod]"
---

# Pre-flight Deployment Check

Run the pre-flight checklist script against the target environment.

## Behavior

```bash
python scripts/pre_flight_checklist.py --env ${ARGUMENTS:-staging}
```

Parse output for PASS/FAIL. Highlight any blocking issues.

If all checks pass, print: `Pre-flight: READY for deployment`
If any fail, print: `Pre-flight: BLOCKED — N issues` with details.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
