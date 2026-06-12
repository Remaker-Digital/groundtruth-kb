# Protected Behavior Regression Gate (Phase A.2)

Run these 11 grep assertions before every build. Each must find >= 1 match.

| PB | Pattern | File | Min |
|----|---------|------|-----|
| PB-001 | `injectWidget` | admin/standalone/layouts/StandaloneLayout.tsx | 1 |
| PB-002 | `icon-master.svg` | admin/standalone/index.html | 1 |
| PB-003 | `icon-master.svg` | admin/provider/index.html | 1 |
| PB-010 | `Save your configuration first` | src/multi_tenant/activation_service.py | 2 |
| PB-011 | `isProOrHigher` | admin/standalone/pages/MemoryPrivacy.tsx | 1 |
| PB-020 | `send_team_invite_alert` | src/multi_tenant/admin_team_api.py | 1 |
| PB-021 | `admin_url` | src/multi_tenant/alert_delivery.py | 2 |
| PB-022 | `resend-invite` | src/multi_tenant/admin_team_api.py | 1 |
| PB-023a | `find_superadmin_email` | src/chat/pipeline/critic_escalation.py | 1 |
| PB-023b | `recipient_emails` | src/multi_tenant/alert_delivery.py | 3 |
| PB-030 | `VITE_API_URL` | docs/operations/build-deploy-procedure.md | 1 |

**If ANY assertion fails, STOP. A protected behavior was removed (regression).**

## Automated Check

```bash
# Run all PB assertions in sequence
grep -c "injectWidget" admin/standalone/layouts/StandaloneLayout.tsx
grep -c "icon-master.svg" admin/standalone/index.html
grep -c "icon-master.svg" admin/provider/index.html
grep -c "Save your configuration first" src/multi_tenant/activation_service.py
grep -c "isProOrHigher" admin/standalone/pages/MemoryPrivacy.tsx
grep -c "send_team_invite_alert" src/multi_tenant/admin_team_api.py
grep -c "admin_url" src/multi_tenant/alert_delivery.py
grep -c "resend-invite" src/multi_tenant/admin_team_api.py
grep -c "find_superadmin_email" src/chat/pipeline/critic_escalation.py
grep -c "recipient_emails" src/multi_tenant/alert_delivery.py
grep -c "VITE_API_URL" docs/operations/build-deploy-procedure.md
```
