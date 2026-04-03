## Summary

<!-- Brief description of what this PR does and why -->

## Change Class (S251 OM-2 — Required)

<!-- Select ONE. This determines the release gates required for production promotion. -->

- [ ] **Class A** — UI-only, no widget/chat/auth/config effect
- [ ] **Class B** — Admin/config/integration change
- [ ] **Class C** — Widget, auth, tenant routing, chat transport, activation, migration, or AI-path change

> **Class C changes require live widget conversation proof in staging and a production canary post-deploy.**
> If unsure, classify as C. Under-classification is a release-governance violation.

## Test Plan

<!-- How was this tested? What should reviewers verify? -->

## Checklist

- [ ] Tests pass locally
- [ ] No new lint warnings
- [ ] Protected behaviors unaffected (or spec updated)
- [ ] Change class is accurate for the blast radius of this PR
