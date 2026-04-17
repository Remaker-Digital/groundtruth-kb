# Azure Enterprise Readiness

This page is the wiki-ready summary for GroundTruth-KB Azure Enterprise
Readiness. It mirrors the source documentation so the GitHub Wiki can stay
short, visual, and current.

## One-Page Summary

GroundTruth-KB keeps the default scaffold lightweight, then adds an opt-in
Azure enterprise readiness envelope for teams that need SaaS deployment
evidence. The envelope is made of specifications, ADR prompts, assertions,
doctor checks, runbooks, and deploy evidence artifacts.

```mermaid
flowchart LR
    Starter["starter<br/>local-first default"]
    Candidate["production-candidate<br/>Azure decisions recorded"]
    Enterprise["enterprise-ready<br/>buyer evidence"]
    Regulated["regulated-enterprise<br/>industry controls"]

    Starter --> Candidate --> Enterprise --> Regulated
```

## What GT-KB Owns

```mermaid
flowchart TB
    subgraph GTKB["GT-KB owns"]
        Specs["Specs"]
        ADRs["ADR templates"]
        Assertions["Assertions"]
        Doctor["Doctor checks"]
        Runbooks["Runbook templates"]
    end

    subgraph Team["Application team owns"]
        Decisions["Instance decisions"]
        IaC["Production IaC"]
        Pipeline["CI/CD"]
        Azure["Azure runtime state"]
        Ops["Operations"]
    end

    Specs --> Decisions
    ADRs --> Decisions
    Assertions --> Pipeline
    Doctor --> Pipeline
    Runbooks --> Ops
    Decisions --> IaC
    Pipeline --> Azure
    Azure --> Doctor
```

GT-KB does not own a customer's Azure subscription or deploy pipeline. It
owns the readiness workflow that makes Azure decisions recorded,
reviewable, and verifiable.

## Readiness Categories

```mermaid
flowchart TB
    Readiness["Azure readiness"]
    Readiness --> LZ["Landing zone<br/>subscriptions, management groups, policy, tags"]
    Readiness --> Identity["Identity<br/>OIDC, managed identity, RBAC, B2B/B2C"]
    Readiness --> Tenancy["Tenancy<br/>tenant definition, isolation model, lifecycle"]
    Readiness --> Secrets["Secrets<br/>Key Vault, rotation, no static CI secrets"]
    Readiness --> CICD["CI/CD<br/>plan/apply, approvals, drift, evidence"]
    Readiness --> Obs["Observability<br/>logs, metrics, traces, SLOs"]
    Readiness --> DR["DR<br/>RPO, RTO, restore tests"]
    Readiness --> Cost["Cost<br/>budgets, tags, FinOps cadence"]
    Readiness --> Compliance["Compliance<br/>control mapping, audit trail, data boundary"]
```

## Tier Matrix

| Capability | starter | production-candidate | enterprise-ready | regulated-enterprise |
|------------|:-------:|:--------------------:|:----------------:|:--------------------:|
| Local specs/assertions | yes | yes | yes | yes |
| Docker/provider stubs | yes | yes | yes | yes |
| Compute target ADR | no | yes | yes | yes |
| OIDC deploy pattern | no | yes | yes | yes |
| Key Vault pattern | no | yes | yes | yes |
| Landing zone ADR | no | optional | yes | yes |
| Tenancy tests | no | basic | required | required |
| Cost budgets | no | optional | required | required |
| Observability/SLOs | no | basic | required | required |
| DR restore evidence | no | optional | required | required |
| Compliance mapping | no | no | baseline | regulation-specific |

## Verification Model

```mermaid
flowchart TD
    Offline["Offline doctor<br/>no Azure API calls"]
    Live["Live doctor<br/>explicit --live"]
    Evidence["Readiness result JSON"]
    Deploy["Deployment evidence bundle"]

    Offline --> Evidence
    Live --> Evidence
    Evidence --> Deploy
```

Offline checks inspect local specs, ADRs, workflow files, IaC text, and
assertions. Live checks call Azure APIs only when explicitly requested.

## First Implementation Bridge

The first implementation bridge should be taxonomy-first, not IaC-first:

`gtkb-azure-enterprise-readiness-taxonomy`

Follow-on bridges can add spec scaffolding, ADR activation, IaC skeletons,
CI/CD gates, offline doctor checks, live doctor checks, and operational docs.

## Source Of Truth

The full maintained source page is
[`docs/reference/azure-readiness-taxonomy.md`](../reference/azure-readiness-taxonomy.md).
