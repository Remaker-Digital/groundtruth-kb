---
name: Production deploy gate via env token
description: Deploy requires env token set only when tests pass AND owner approves test results — owner controls test approval, not deploy
type: feedback
---

Production deployment requires an environment token. The token is set based on two conditions: (1) tests pass, and (2) owner approves that test results indicate expected successful deployment. The owner's point of control is the approval of the test results that are executed — not the deploy itself.

**Why:** Owner directive S218. Separates what the owner approves (test quality/completeness) from what the system enforces (deploy gate). The hook checks the token; if absent or stale, deploy is blocked. This pattern is similar to aviation airworthiness certificates.

**How to apply:** Implement a PreToolUse hook that checks for an env token before `deploy.py production` can execute. The token should be set by a script that: (a) verifies test results meet threshold, (b) records owner approval timestamp. Token expires after each new build to prevent stale approvals.
