# Shopify Partner Program & App Store Research

> **Project:** Agent Red Customer Engagement
> **Purpose:** Formal reference document covering the Shopify Partner Program, App Store listing process, partner tiers, optimization strategies, and related programs relevant to Agent Red's go-to-market strategy
> **Date:** 2026-01-30
> **Scope:** 8 research areas (App Store approval, partner tiers, growth benefits, ASO, Plus Partners, Built for Shopify, competitions, certifications)
> **Data Note:** This research is based on publicly available Shopify documentation and partner resources as of early 2026. All program requirements, fees, and criteria should be verified against the live Shopify Partner documentation before making commitments. Items marked [VERIFY] require live confirmation. URLs are provided for verification wherever possible.

---

## Table of Contents

1. [App Store Approval Process](#1-app-store-approval-process)
   - [1.1 Overview](#11-overview)
   - [1.2 Steps to Get a Public App Listed](#12-steps-to-get-a-public-app-listed)
   - [1.3 What the App Review Team Checks](#13-what-the-app-review-team-checks)
   - [1.4 Mandatory Technical Requirements](#14-mandatory-technical-requirements)
   - [1.5 App Listing Requirements](#15-app-listing-requirements)
   - [1.6 Common Rejection Reasons](#16-common-rejection-reasons)
   - [1.7 Review Timeline](#17-review-timeline)
   - [1.8 Pre-Submission Checklist](#18-pre-submission-checklist)
2. [Partner Program Structure](#2-partner-program-structure)
   - [2.1 Overview](#21-overview)
   - [2.2 Partner Types](#22-partner-types)
   - [2.3 Revenue Share Model](#23-revenue-share-model)
   - [2.4 Partner Dashboard](#24-partner-dashboard)
3. [Enhanced Relationship Benefits](#3-enhanced-relationship-benefits)
   - [3.1 Growth-Based Benefits](#31-growth-based-benefits)
   - [3.2 Staff Picks and Featured Apps](#32-staff-picks-and-featured-apps)
   - [3.3 Co-Marketing Opportunities](#33-co-marketing-opportunities)
   - [3.4 Partner Managers](#34-partner-managers)
   - [3.5 Early API Access and Beta Programs](#35-early-api-access-and-beta-programs)
   - [3.6 Shopify Editions and Events](#36-shopify-editions-and-events)
   - [3.7 App Store Advertising](#37-app-store-advertising)
4. [App Store Optimization (ASO)](#4-app-store-optimization-aso)
   - [4.1 Search Algorithm Factors](#41-search-algorithm-factors)
   - [4.2 Listing Optimization Best Practices](#42-listing-optimization-best-practices)
   - [4.3 Reviews and Ratings Strategy](#43-reviews-and-ratings-strategy)
   - [4.4 Category and Keyword Strategy](#44-category-and-keyword-strategy)
5. [Shopify Plus Partner Program](#5-shopify-plus-partner-program)
   - [5.1 What It Is](#51-what-it-is)
   - [5.2 Requirements](#52-requirements)
   - [5.3 Benefits](#53-benefits)
   - [5.4 Relevance to Agent Red](#54-relevance-to-agent-red)
6. [Built for Shopify Program](#6-built-for-shopify-program)
   - [6.1 What It Is](#61-what-it-is)
   - [6.2 Requirements](#62-requirements)
   - [6.3 Benefits](#63-benefits)
   - [6.4 Relevance to Agent Red](#64-relevance-to-agent-red)
7. [Shopify App Challenges and Competitions](#7-shopify-app-challenges-and-competitions)
   - [7.1 Shopify App Challenge](#71-shopify-app-challenge)
   - [7.2 Shopify Editions Tie-Ins](#72-shopify-editions-tie-ins)
   - [7.3 Hackathons and Community Events](#73-hackathons-and-community-events)
8. [Partner Academy and Certifications](#8-partner-academy-and-certifications)
   - [8.1 Shopify Partner Academy](#81-shopify-partner-academy)
   - [8.2 Available Certifications](#82-available-certifications)
   - [8.3 Marketplace Advantages](#83-marketplace-advantages)
9. [Strategic Relevance to Agent Red](#9-strategic-relevance-to-agent-red)
10. [Key URLs Reference](#10-key-urls-reference)

---

## 1. App Store Approval Process

### 1.1 Overview

The Shopify App Store (https://apps.shopify.com) is the primary marketplace where Shopify merchants discover, evaluate, and install apps. Getting listed requires building a Shopify app that conforms to Shopify's technical standards, submitting it through the Partner Dashboard, and passing a manual review by Shopify's App Review Team.

There are two types of Shopify apps:

| App Type | Visibility | Distribution | Review Required |
|----------|-----------|--------------|-----------------|
| **Public app** | Listed on Shopify App Store | Any merchant can install | Yes -- full app review |
| **Custom app** | Not listed; private | Specific merchants only (via install link) | No formal review |
| **Unlisted app** | Not listed; discoverable via direct link | Specific merchants via URL | Lighter review [VERIFY current process] |

Agent Red would be a **public app** listed on the Shopify App Store for discovery by Shopify merchants.

**Key documentation URLs:**
- App requirements: https://shopify.dev/docs/apps/launch/app-requirements-checklist
- Listing in the App Store: https://shopify.dev/docs/apps/launch
- App submission: https://shopify.dev/docs/apps/launch/submit
- App review FAQ: https://shopify.dev/docs/apps/launch/app-review

### 1.2 Steps to Get a Public App Listed

The end-to-end process to go from zero to a live Shopify App Store listing:

**Step 1: Create a Shopify Partner Account (free)**
- URL: https://partners.shopify.com/signup
- No cost. Provides access to the Partner Dashboard.
- Agent Red already has a Shopify Partner developer account (per CLAUDE.md: "Shopify Partner: Developer account -- Active").

**Step 2: Create the App in the Partner Dashboard**
- Navigate to Apps > Create app in the Partner Dashboard.
- Choose "Public app" distribution.
- Configure the app URL (your application's entry point), redirect URLs for OAuth, and allowed redirection URL(s).
- Shopify generates the API key and API secret key for your app.

**Step 3: Build the App to Shopify's Technical Standards**
- Implement OAuth 2.0 authentication flow.
- Use Shopify App Bridge for embedded app experience.
- Implement the Shopify Billing API if charging merchants.
- Follow all mandatory technical requirements (see Section 1.4).
- Test using a Shopify development store (free, unlimited through Partner Dashboard).

**Step 4: Create the App Listing**
- In Partner Dashboard > App listing.
- Write app name, tagline, detailed description.
- Upload screenshots (desktop and mobile).
- Record or upload a demo video [VERIFY if still optional or recommended].
- Define pricing plans (free, recurring charge, usage-based, or one-time).
- Select app category and add search keywords.
- Provide support contact information and URLs (FAQ, docs, support email).
- Add a privacy policy URL.

**Step 5: Complete the Pre-Submission Checklist**
- Shopify provides a built-in checklist within the Partner Dashboard.
- All checklist items must be resolved before submission.
- Includes technical checks, listing quality checks, and policy compliance.

**Step 6: Submit for Review**
- Click "Submit for review" in the Partner Dashboard.
- Include testing instructions for the review team (login credentials for a test account, test store URL, walkthrough steps).
- Provide a test Shopify development store with the app already installed and configured.

**Step 7: App Review**
- Shopify's App Review Team manually tests the app.
- They check technical requirements, user experience, listing accuracy, and policy compliance.
- Communication happens via email through the Partner Dashboard.

**Step 8: Review Outcome**
- **Approved** -- App goes live on the Shopify App Store.
- **Changes Required** -- Shopify provides specific feedback on what must be fixed. You fix and resubmit.
- **Rejected** -- Rare for first submissions; more common if the app fundamentally violates policies.

**Step 9: Post-Approval**
- App is live and discoverable.
- Monitor reviews, respond to merchant feedback.
- Maintain compliance with ongoing requirements (updates for new API versions, etc.).

### 1.3 What the App Review Team Checks

The App Review Team evaluates submissions across several dimensions:

#### Technical Compliance

| Check | What They Verify | Consequence of Failure |
|-------|-----------------|----------------------|
| OAuth implementation | Correct OAuth 2.0 flow; no hardcoded tokens; proper scope requests | Rejection |
| App Bridge usage | App uses Shopify App Bridge for embedded experience | Rejection |
| Billing API | If app charges, it uses Shopify Billing API (not third-party billing inside the app) | Rejection |
| API version | App uses a supported (non-deprecated) API version | Changes required |
| Webhook handling | Proper webhook registration and processing | Changes required |
| GDPR compliance | Handles mandatory GDPR webhooks (customer data request, customer data erasure, shop data erasure) | Rejection |
| Session token auth | Uses session tokens (not cookies) for authentication in embedded apps | Rejection [VERIFY: requirement may have evolved] |
| HTTPS | All endpoints use HTTPS | Rejection |

#### User Experience

| Check | What They Verify |
|-------|-----------------|
| Onboarding flow | App provides clear setup steps after installation |
| Empty states | App handles cases where no data exists gracefully |
| Error handling | App shows user-friendly error messages, not raw errors |
| Loading states | App shows loading indicators for async operations |
| Responsive design | App works on different screen sizes within the Shopify admin |
| Navigation | App uses Shopify Polaris design system or follows admin design conventions |
| Uninstall flow | App cleans up gracefully; no orphaned data or broken references |

#### Listing Quality

| Check | What They Verify |
|-------|-----------------|
| Description accuracy | App does what the listing says it does |
| Screenshots | Match the actual app experience; not misleading |
| Pricing clarity | Pricing is transparent; no hidden charges |
| Contact information | Valid support email, documentation URL |
| Privacy policy | Privacy policy URL is valid and covers data handling |
| No keyword stuffing | App name and description are not stuffed with irrelevant keywords |

#### Policy Compliance

| Check | What They Verify |
|-------|-----------------|
| No data selling | App does not sell merchant or customer data |
| Minimal data access | App requests only the API scopes it actually needs |
| No competing services | App does not redirect merchants away to a competing platform [VERIFY scope of this policy] |
| No deceptive practices | No fake reviews, no misleading claims |
| Content policy | No prohibited content types |
| Speed and performance | App does not significantly slow down the merchant's storefront (if storefront-facing) |

### 1.4 Mandatory Technical Requirements

These are non-negotiable. An app will not pass review without them.

#### 1.4.1 OAuth 2.0 Authentication

All public Shopify apps must authenticate using OAuth 2.0. The flow:

```
1. Merchant clicks "Install" on App Store listing
2. Shopify redirects to your app's auth URL with shop, timestamp, hmac
3. Your app verifies the hmac signature
4. Your app redirects to Shopify's /admin/oauth/authorize with:
   - client_id (your API key)
   - scope (requested permissions, e.g., read_products,read_orders)
   - redirect_uri (your callback URL)
   - state (nonce for CSRF protection)
5. Merchant sees permission screen and clicks "Install app"
6. Shopify redirects to your redirect_uri with authorization code
7. Your app exchanges the code for a permanent access token via POST /admin/oauth/access_token
8. Store the access token securely (Agent Red: Key Vault)
```

**Key requirements:**
- HMAC validation on every callback from Shopify
- State parameter for CSRF protection
- Access tokens stored securely (never in client-side code, URLs, or logs)
- Support for token rotation if/when Shopify issues new tokens

**Documentation:** https://shopify.dev/docs/apps/auth/oauth

#### 1.4.2 Shopify App Bridge

App Bridge is Shopify's JavaScript library for building embedded apps that run inside the Shopify admin. It provides:

| Feature | Purpose |
|---------|---------|
| Navigation | Manage app navigation within the Shopify admin |
| TitleBar | Control the title bar of the embedded app |
| Toast | Show notification toasts |
| Modal | Display modal dialogs |
| ResourcePicker | Let merchants select products, collections, etc. |
| Loading | Show/hide loading bars |
| Redirect | Navigate within the Shopify admin |
| SessionToken | Get authenticated session tokens |

**Requirements:**
- All embedded apps must use App Bridge (version 3.x or later as of 2024-2025; [VERIFY current required version])
- Non-embedded apps are generally discouraged for new public apps [VERIFY current policy]
- App Bridge is loaded via `@shopify/app-bridge` npm package or CDN

**Documentation:** https://shopify.dev/docs/api/app-bridge

#### 1.4.3 Shopify Billing API

If your app charges merchants (Agent Red does), you **must** use the Shopify Billing API. Third-party payment processing within the app is not allowed for recurring charges.

The Billing API supports:

| Charge Type | Shopify Object | Use Case |
|-------------|---------------|----------|
| Recurring charge | `RecurringApplicationCharge` | Monthly subscription fees |
| Usage charge | `UsageCharge` (capped) | Per-use or metered billing |
| One-time charge | `ApplicationCharge` | One-time purchases |

**Critical detail -- Revenue Share:**
Shopify takes a revenue share on all charges processed through the Billing API:

| Scenario | Shopify's Cut | Developer Keeps |
|----------|--------------|-----------------|
| Standard apps (all developers as of Aug 2024) | **0% on first $1M USD lifetime earnings** | 100% |
| After $1M lifetime earnings | **15%** of revenue [VERIFY: was 20% pre-2024, reduced to 15%] | 85% |

[VERIFY: Shopify announced in 2023-2024 a reduction from 20% to 15% revenue share for apps earning over $1M. Confirm the exact current structure and whether the $1M threshold is per-year or lifetime.]

**Important implications for Agent Red pricing:**
- Agent Red's $149/$399/$999 pricing runs through Shopify Billing API when installed via the App Store
- For the first $1M in revenue, Agent Red keeps 100%
- After $1M, Shopify takes 15%, meaning Agent Red nets ~$127/$339/$849 per subscription at list price [VERIFY exact current rate]
- This revenue share applies ONLY to installs through the Shopify App Store; direct sales (through Agent Red's own website using Stripe) would not be subject to this share

**Documentation:** https://shopify.dev/docs/apps/billing

#### 1.4.4 GDPR Mandatory Webhooks

All Shopify apps must implement three GDPR-related webhook endpoints:

| Webhook | Trigger | Required Response |
|---------|---------|-------------------|
| `customers/data_request` | Merchant's customer requests their data (GDPR right of access) | Return all data your app stores about the customer |
| `customers/redact` | Merchant's customer requests data deletion (GDPR right to erasure) | Delete all stored customer data within 30 days |
| `shop/redact` | Merchant uninstalls the app and 48 hours have passed | Delete all stored merchant data within 30 days |

**Requirements:**
- Endpoints must be registered in the app setup
- Endpoints must respond with HTTP 200 within 5 seconds
- Actual processing can be asynchronous
- Failure to implement these results in automatic rejection

**Documentation:** https://shopify.dev/docs/apps/webhooks/configuration/mandatory-webhooks

#### 1.4.5 Content Security Policy (CSP)

Embedded apps must work within Shopify's Content Security Policy headers. Key constraints:

- No inline scripts (use nonces or external script files)
- Frame-ancestors must allow embedding in the Shopify admin
- All external resources must be loaded over HTTPS

#### 1.4.6 API Versioning

Shopify APIs use calendar-based versioning (e.g., `2024-01`, `2024-04`, `2024-07`, `2024-10`). Requirements:

- Apps must use a supported (non-deprecated) API version
- Shopify supports each version for approximately 12 months after release
- Deprecated versions receive 9 months notice before removal
- Apps using deprecated versions receive warnings and eventually break

**Documentation:** https://shopify.dev/docs/api/usage/versioning

### 1.5 App Listing Requirements

The app listing is the storefront page that merchants see. Requirements:

#### Required Listing Elements

| Element | Requirement | Best Practice |
|---------|------------|---------------|
| **App name** | Unique, not misleading, no trademarked terms | Clear, descriptive, includes primary value prop |
| **Tagline** | Short description (approx. 80 chars) | Focus on the key benefit |
| **Detailed description** | Accurate description of app functionality | Structured with headers, bullets, clear feature list |
| **Key benefits** | Up to 4 key benefits [VERIFY exact number] | Outcome-focused, not feature-focused |
| **Screenshots** | Minimum 3 screenshots [VERIFY]; desktop required | Show key features, onboarding, and results; annotate with callouts |
| **Demo video** | Optional but recommended [VERIFY if now required] | 1-3 minutes, show key workflows |
| **Icon** | 1200x1200 px [VERIFY dimensions] | Match your brand, follow Shopify guidelines |
| **Pricing** | Transparent pricing with plan details | Show all costs including any usage-based fees |
| **Category** | Select primary category | Choose the most relevant; affects search placement |
| **Support** | Support email + at least one support resource URL | Docs, FAQ, or help center URL |
| **Privacy policy** | URL to your privacy policy | Must cover how merchant and customer data is handled |

#### Prohibited in Listings

- Keyword stuffing (repeating keywords unnaturally)
- Mentioning competitors by name in a derogatory way
- Misleading screenshots or mockups not reflecting actual app
- Claiming "official" Shopify endorsement
- Including pricing for other platforms
- Excessive use of emojis or special characters
- External links that bypass Shopify's billing (for paid features)

### 1.6 Common Rejection Reasons

Based on publicly documented rejection patterns from Shopify's app review process and developer community reports:

| Rejection Reason | Category | How to Avoid |
|-----------------|----------|-------------|
| **Not using Billing API** for charges | Technical | All recurring/usage charges must go through Shopify Billing API |
| **Requesting excessive API scopes** | Technical | Request only scopes you actually use; justify each scope |
| **Missing GDPR webhooks** | Technical | Implement all three mandatory webhooks before submission |
| **Poor onboarding experience** | UX | Provide clear setup wizard or getting-started guide after install |
| **Broken OAuth flow** | Technical | Test OAuth with a fresh development store; handle edge cases (re-install, scope changes) |
| **Listing does not match app** | Listing | Ensure screenshots and description exactly match the current app |
| **No clear value proposition** | Listing | Description must clearly explain what the app does and why merchants need it |
| **App crashes or errors during review** | Quality | Thoroughly QA in a development store; provide test instructions |
| **Missing privacy policy** | Policy | Must have a valid privacy policy URL covering Shopify data |
| **App loads too slowly** | Performance | Target sub-3-second load time within embedded admin |
| **Not using App Bridge** | Technical | All embedded apps must use App Bridge for navigation, auth, and UI |
| **Deprecated API version** | Technical | Use a current, supported API version |
| **App redirects outside Shopify** | UX | Keep the primary experience within the Shopify admin; external links should be supplementary |

### 1.7 Review Timeline

| Stage | Typical Duration | Notes |
|-------|-----------------|-------|
| Initial submission to first response | **5-10 business days** | Can be longer during peak periods (BFCM, Editions launches) |
| Resubmission after changes | **3-7 business days** | Faster because reviewer has prior context |
| Total time (first submission, no issues) | **1-2 weeks** | If app meets all requirements |
| Total time (with 1-2 rounds of feedback) | **2-4 weeks** | Common for first-time app developers |
| Total time (complex app or significant issues) | **4-8 weeks** | Rare; indicates fundamental issues |

[VERIFY: Review timelines may have changed. Shopify has historically varied between 5-15 business days for initial reviews. Check https://shopify.dev/docs/apps/launch/app-review for current estimates.]

**Tips to speed up review:**
- Provide detailed testing instructions (step-by-step, with test data)
- Include a pre-configured development store with sample data
- Address all pre-submission checklist items before submitting
- Respond quickly to reviewer feedback

### 1.8 Pre-Submission Checklist

Shopify provides a built-in checklist in the Partner Dashboard. The following is a comprehensive checklist combining Shopify's requirements and best practices:

#### Technical Readiness

- [ ] OAuth 2.0 flow works correctly (install, re-install, token exchange)
- [ ] HMAC validation on all Shopify callbacks
- [ ] App Bridge integrated (latest supported version)
- [ ] Session tokens used for authentication (not cookies)
- [ ] Billing API implemented (if app charges)
- [ ] All three GDPR webhooks implemented and responding HTTP 200
- [ ] Using a supported (non-deprecated) API version
- [ ] All endpoints use HTTPS
- [ ] Webhook subscriptions registered and handling events correctly
- [ ] Proper error handling throughout the app
- [ ] App uninstall handler cleans up data appropriately
- [ ] Content Security Policy compatible with Shopify admin embedding
- [ ] Rate limiting compliance (Shopify API: 2 requests/second for REST, bucket-based for GraphQL)

#### User Experience Readiness

- [ ] Clear onboarding flow after installation
- [ ] Empty states handled gracefully
- [ ] Loading indicators for async operations
- [ ] Error messages are user-friendly (not raw error dumps)
- [ ] Navigation follows Shopify admin patterns
- [ ] Polaris design system used (recommended, not strictly required for all elements) [VERIFY]
- [ ] Mobile-responsive within admin context
- [ ] Help/documentation accessible from within the app

#### Listing Readiness

- [ ] App name finalized and unique
- [ ] Tagline written (concise, benefit-focused)
- [ ] Detailed description written (accurate, structured)
- [ ] Key benefits defined (outcome-focused)
- [ ] Screenshots captured (minimum required count, annotated)
- [ ] Demo video recorded (if applicable)
- [ ] App icon designed to spec
- [ ] Pricing plans configured in Partner Dashboard
- [ ] Category selected
- [ ] Support email configured
- [ ] Documentation/FAQ URL provided
- [ ] Privacy policy URL provided and valid

#### Testing Readiness

- [ ] App tested on a fresh development store (not just the dev store you built on)
- [ ] App tested with sample merchant data (products, orders, customers)
- [ ] OAuth flow tested with a clean install (no residual state)
- [ ] Uninstall and re-install tested
- [ ] Testing instructions written for the reviewer
- [ ] Test account credentials prepared for reviewer
- [ ] All features described in the listing are functional and testable

---

## 2. Partner Program Structure

### 2.1 Overview

The Shopify Partner Program (https://www.shopify.com/partners) is free to join and provides access to tools, resources, and revenue opportunities for developers, designers, and agencies building on the Shopify platform.

**Key fact:** There are no formalized partner tiers (Bronze, Silver, Gold, Platinum) in the Shopify Partner Program. Shopify does **not** use a tiered partner structure like Salesforce (Consulting, Ridge, Crest, Summit) or Microsoft (Gold, Silver). Instead, Shopify differentiates partners by **type** and offers informal benefits that scale with performance and engagement.

### 2.2 Partner Types

Shopify categorizes partners by their business model, not by achievement level:

| Partner Type | Description | Primary Revenue Model | Relevance to Agent Red |
|-------------|-------------|----------------------|----------------------|
| **App developers** | Build and sell apps on the Shopify App Store | Revenue share from app charges | **Primary** -- Agent Red is an app developer |
| **Theme developers** | Build and sell themes on the Shopify Theme Store | Revenue share from theme sales | Not relevant |
| **Shopify Plus Partners** | Certified agencies/developers for enterprise merchants | Service fees + referral commissions | Potentially relevant later (see Section 5) |
| **Referral partners** | Refer new merchants to Shopify | Referral bounties | Not primary |
| **Affiliate partners** | Drive Shopify sign-ups via content/marketing | Affiliate commissions | Not primary |

### 2.3 Revenue Share Model

#### App Revenue Share (Current as of 2024)

Shopify revised its revenue share model in 2023-2024 to be significantly more favorable to developers:

| Revenue Tier | Shopify's Cut | Developer Keeps | Notes |
|-------------|--------------|-----------------|-------|
| First $1,000,000 USD in lifetime app revenue | **0%** | **100%** | Shopify takes nothing on the first $1M |
| Revenue above $1,000,000 USD | **15%** | **85%** | Reduced from 20% (pre-2023 rate) |

[VERIFY: The exact threshold ($1M) and rate (15%) against https://shopify.dev/docs/apps/billing. Shopify announced this change at Shopify Editions 2023/2024. Confirm whether this is per-calendar-year or lifetime cumulative.]

**Historical context:**
- Pre-2021: Shopify took 20% of all app revenue
- 2021: Shopify introduced the $1M/0% threshold (keeping 20% above $1M)
- 2023-2024: Shopify reduced the above-$1M rate from 20% to 15%

**Impact on Agent Red:**
- At $149-$999/month per customer, Agent Red would need approximately 83-558 customers (depending on plan mix) to hit $1M cumulative app revenue
- Realistically, Agent Red will operate in the 0% revenue share tier for its first 1-3 years
- This makes the Shopify App Store an extremely cost-effective distribution channel

#### Referral Revenue

Shopify also pays partners for referring new merchants to Shopify itself:

| Referral Type | Bounty | Notes |
|-------------|--------|-------|
| Standard Shopify plan referral | 100% of merchant's first 2 monthly payments [VERIFY] | For merchants who sign up for a paid Shopify plan via your referral |
| Shopify Plus referral | Varies (historically $2,000-$5,000 per referral) [VERIFY] | For enterprise merchants |

This is separate from app revenue and is not a primary revenue model for Agent Red.

### 2.4 Partner Dashboard

The Shopify Partner Dashboard (https://partners.shopify.com) provides:

| Feature | Description |
|---------|-------------|
| App management | Create, configure, and manage app listings |
| Analytics | Installs, uninstalls, revenue, conversion funnel |
| Payouts | Revenue tracking and payout management |
| Development stores | Unlimited free development stores for testing |
| Staff accounts | Manage team access to the partner account |
| Support tickets | Direct communication with Shopify Partner Support |
| Changelog | API and platform updates relevant to partners |
| App reviews | View and respond to merchant reviews |

---

## 3. Enhanced Relationship Benefits

### 3.1 Growth-Based Benefits

While Shopify does not have formal partner tiers, there are informal benefits that become available as an app grows in installs, revenue, and quality:

| Growth Milestone (Informal) | Potential Benefits | How to Access |
|----------------------------|-------------------|---------------|
| **Early stage** (0-100 installs) | Standard partner support, documentation, dev stores | Automatic with Partner account |
| **Growing** (100-1,000 installs) | Potential for App Store editorial features, improved review team responsiveness | Organic; based on quality metrics |
| **Established** (1,000-10,000 installs) | Potential dedicated partner support contact, beta feature access invitations | By invitation or application |
| **Major** (10,000+ installs) | Dedicated partner manager, co-marketing opportunities, Shopify event invitations, early API access | By invitation |
| **Top-tier** (50,000+ installs or significant revenue) | Strategic partnership discussions, joint marketing campaigns, Shopify keynote mentions | By relationship |

**Important caveat:** These are approximations based on community reports and publicly available information. Shopify does not publish exact thresholds for when these benefits activate. The progression is informal and relationship-driven, not programmatic.

### 3.2 Staff Picks and Featured Apps

#### Staff Picks

Shopify's editorial team curates "Staff Picks" collections on the App Store. These are apps that the Shopify team has identified as particularly high-quality, well-designed, or useful.

**Criteria (based on publicly available guidance and community consensus):**

| Factor | Importance | Notes |
|--------|-----------|-------|
| App quality and reliability | High | Low crash rate, fast performance, polished UX |
| Merchant ratings and reviews | High | Consistently high ratings (4.5+ stars) |
| Unique value proposition | High | Solves a problem in a distinctive way |
| Design quality | Medium-High | Follows Shopify Polaris, clean UI |
| Onboarding experience | Medium | Easy setup, clear time-to-value |
| Support responsiveness | Medium | Quick, helpful responses to merchant reviews and support requests |
| Innovation | Medium | Novel use of Shopify APIs, creative solutions |

**How to get selected:**
- There is no application process for Staff Picks
- Shopify's editorial team selects apps at their discretion
- Building a high-quality, well-reviewed app is the best strategy
- Engaging with the Shopify community (forums, events) may increase visibility

#### Featured Apps / Collections

The Shopify App Store homepage and category pages feature curated collections:

| Collection Type | Examples | Selection Method |
|----------------|---------|-----------------|
| Staff picks | Top picks across categories | Editorial curation |
| Category leaders | Top apps per category (e.g., "Best customer service apps") | Algorithmic + editorial |
| Seasonal collections | "BFCM preparation", "Back to school" | Editorial, seasonal |
| New and noteworthy | Recently launched high-quality apps | Editorial |
| Trending | Apps gaining rapid adoption | Algorithmic |

### 3.3 Co-Marketing Opportunities

As an app grows, the following co-marketing opportunities may become available:

| Opportunity | Typical Threshold | Format |
|-------------|------------------|--------|
| Shopify blog feature | Established app with good story | Blog post, case study |
| Shopify social media mention | High-quality, growing app | Tweet, LinkedIn post |
| Partner case study | Significant merchant success stories | Written case study on Shopify.com |
| Webinar co-hosting | Established partner with expertise | Joint webinar on partner's domain |
| Shopify event speaking slot | Top-tier partner | Conference talk at Shopify Unite/Editions |
| Email newsletter feature | Established app, seasonal relevance | Featured in Shopify's merchant-facing emails |
| App Store banner/spotlight | Top-performing or editorially selected | Featured placement on App Store homepage |

**How to pursue co-marketing:**
1. Build a great app with strong reviews
2. Create merchant success stories / case studies
3. Engage with Shopify's partner team (via partner manager if assigned, or via partner support)
4. Propose co-marketing ideas proactively
5. Participate in Shopify community events and forums

### 3.4 Partner Managers

Shopify assigns dedicated partner managers to high-performing partners. There is no published threshold, but based on community reports:

| Factor | Approximate Threshold | Notes |
|--------|----------------------|-------|
| App installs | 5,000-10,000+ active installs | Higher install counts more likely to get a dedicated contact |
| Revenue | Significant and growing | Revenue trajectory matters as much as absolute amount |
| Strategic alignment | N/A | Apps in categories Shopify is prioritizing may get attention sooner |
| Plus ecosystem participation | Shopify Plus Partner status | Plus Partners tend to get dedicated contacts sooner |

**What a partner manager provides:**
- Direct communication channel to Shopify
- Advance notice of platform changes
- Introduction to relevant Shopify teams (marketing, product, enterprise)
- Strategic guidance on app positioning
- Faster escalation for technical issues
- Invitations to exclusive events and betas

[VERIFY: Whether Shopify still assigns dedicated partner managers at the same thresholds, or if the model has changed.]

### 3.5 Early API Access and Beta Programs

Shopify operates several beta and early access programs:

| Program | Access Level | How to Join |
|---------|-------------|-------------|
| **Developer Preview** | Early access to upcoming API versions | Available to all partners via unstable API version (`unstable`) |
| **Beta programs** | Pre-release features and APIs | By invitation (based on app relevance, partner relationship) |
| **Shopify Functions beta** | Shopify's server-side extension framework | Available to partners building checkout/discount extensions |
| **AI integration betas** | Early access to Shopify's AI features (Sidekick, etc.) | By invitation [VERIFY current AI beta programs] |

**How to get invited to beta programs:**
- Express interest through Partner Dashboard or partner manager
- Have an app that would benefit from and meaningfully test the beta feature
- Participate in the Shopify developer community (forums, GitHub discussions)
- Attend Shopify events where betas are announced

### 3.6 Shopify Editions and Events

Shopify hosts several events relevant to partners:

| Event | Type | Frequency | Relevance |
|-------|------|-----------|-----------|
| **Shopify Editions** | Major product announcement | Twice per year (Winter + Summer) | New features, API changes, platform direction; attend to understand upcoming opportunities |
| **Shopify Unite** | Developer/partner conference | Annual (historically; now merged with Editions) [VERIFY current status] | Technical deep dives, networking, partner recognition |
| **Shopify Partner Town Halls** | Virtual partner-facing updates | Periodic | Platform updates, Q&A with Shopify teams |
| **Shopify Community Events** | Local meetups and virtual events | Ongoing | Networking, community building |

**Editions** is the most important event. Shopify announces major platform changes that directly affect app developers. Attending (virtually or in person) provides:
- Early awareness of API changes
- Networking with other partners and Shopify staff
- Potential for app exposure if your category is featured
- Context for planning product roadmap

### 3.7 App Store Advertising

As of late 2024-early 2025, Shopify was exploring or had introduced paid advertising in the App Store:

| Feature | Status | Details |
|---------|--------|---------|
| **Shopify App Store Ads** | Introduced / Testing [VERIFY current availability] | Pay-per-click ads within App Store search results |
| **Search ads** | Available [VERIFY] | Bid on keywords to appear in sponsored positions |
| **Category ads** | Available [VERIFY] | Sponsored placement within category pages |
| **Retargeting** | Unknown | Not publicly documented as available [VERIFY] |

[VERIFY: Shopify introduced App Store ads around 2024. The program may have expanded since then. Check https://shopify.dev/docs/apps/launch/promote for current options and pricing.]

**If available, this is highly relevant for Agent Red's launch strategy.** Paid app store ads could accelerate initial installs and reviews, which in turn improve organic ranking.

**Other promotional options:**
- External advertising (Google Ads, social media) driving traffic to the App Store listing
- Content marketing (blog posts, comparisons) linking to the App Store listing
- Shopify Community forum participation (helpful posts with app link in profile)
- Partner with complementary apps for cross-promotion

---

## 4. App Store Optimization (ASO)

### 4.1 Search Algorithm Factors

Shopify's App Store search algorithm determines which apps appear when merchants search. Based on publicly available information and community analysis, the following factors are believed to influence ranking:

| Factor | Weight (Estimated) | Details |
|--------|-------------------|---------|
| **Relevance (keyword match)** | High | App name, tagline, description, and category match to search query |
| **Install count** | High | Total and recent installs; momentum matters |
| **Rating** | High | Average star rating (higher is better) |
| **Review count** | Medium-High | More reviews signal trust and adoption |
| **Review recency** | Medium | Recent reviews weighted more than old reviews |
| **Retention rate** | Medium-High | Ratio of installs to uninstalls; Shopify tracks this internally |
| **Conversion rate** | Medium | Percentage of listing views that result in installs |
| **App quality signals** | Medium | Crash rate, support response time, API error rates |
| **Revenue/Billing** | Low-Medium | Apps that generate revenue through Billing API may receive slight preference [speculative] |
| **Built for Shopify badge** | Medium | Badge holders may receive ranking boost (see Section 6) |
| **Recency** | Low-Medium | Newer apps may get temporary visibility boost |
| **Listing completeness** | Low-Medium | Complete listings (video, screenshots, detailed description) may rank higher |

**Important:** Shopify does not publicly document its search ranking algorithm. These factors are inferred from community analysis, Shopify's public guidance, and observed patterns. Treat as directional, not definitive.

### 4.2 Listing Optimization Best Practices

#### App Name

| Practice | Example | Notes |
|----------|---------|-------|
| Include primary keyword | "Agent Red AI Customer Service" | Primary keyword: customer service |
| Keep concise | Max ~30 characters for display purposes [VERIFY] | Longer names get truncated in search results |
| Avoid keyword stuffing | Do not: "Agent Red Customer Service Chatbot AI Helpdesk Support" | Will trigger review rejection |
| Brand first, keyword second | "Agent Red -- AI Customer Service" or "Agent Red Customer Engagement" | Brand recognition + searchability |

**Recommendation for Agent Red:** "Agent Red AI Customer Service" or "Agent Red -- AI Customer Support" (contains "customer service" or "customer support" -- the highest-volume search terms in this category).

#### Tagline

The tagline appears directly below the app name in search results. It is critical for click-through rate.

| Practice | Notes |
|----------|-------|
| Lead with the key benefit | Not "Six AI agents for your store" but "Answer 90% of customer questions automatically" |
| Include secondary keyword | "AI-powered customer service for Shopify stores" |
| Keep under 80 characters | Truncation varies by display context |
| Quantify if possible | "Resolve 90% of tickets automatically. Save 80% on support costs." |

#### Description

The detailed description supports SEO and conversion. Structure:

1. **Opening paragraph** -- Clear statement of what the app does and who it is for
2. **Key benefits** (3-5 bullet points) -- Outcome-focused, quantified where possible
3. **How it works** -- Brief overview of the user experience
4. **Features list** -- Detailed feature breakdown
5. **Pricing transparency** -- Clear pricing summary
6. **Social proof** (if available) -- Metrics, testimonials, case study references
7. **Support and resources** -- How to get help

#### Screenshots

| Best Practice | Details |
|--------------|---------|
| First screenshot = hero shot | Most impactful view of the app (dashboard, key feature) |
| Annotate with callouts | Add text overlays explaining what the user is seeing |
| Show the embedded admin context | Screenshot within the Shopify admin frame |
| Include before/after or metrics | "Before: 50 tickets/day. After: 5 tickets/day." |
| Desktop first, then mobile | Desktop screenshots are displayed more prominently [VERIFY] |
| Minimum 3, ideal 5-6 | Cover onboarding, key features, settings, results |

### 4.3 Reviews and Ratings Strategy

Reviews are one of the strongest ranking and conversion signals. Strategy:

| Tactic | Implementation | Timing |
|--------|---------------|--------|
| **In-app review prompt** | After a positive outcome (resolved tickets, good metrics), show a prompt linking to the App Store review page | After 2-4 weeks of active use (not immediately after install) |
| **Respond to every review** | Public response to all reviews, especially negative ones | Within 24-48 hours |
| **Act on feedback** | Implement commonly requested features; report back in review responses | Ongoing |
| **Support quality** | Excellent support prevents negative reviews before they happen | Ongoing |
| **Avoid fake reviews** | Shopify detects and penalizes fake or incentivized reviews | Never |

**Rating thresholds (approximate impact on conversion):**
- 4.5+ stars: Strong positive signal, eligible for editorial features
- 4.0-4.4 stars: Good, competitive range
- 3.5-3.9 stars: Below average for App Store; merchants become cautious
- Below 3.5 stars: Significant conversion penalty; investigate and address root causes

**Review velocity:** A steady stream of recent reviews is more valuable than a large number of old reviews. This suggests ongoing review solicitation is important.

### 4.4 Category and Keyword Strategy

#### Category Selection

Agent Red's primary category would be in the **Customer support** or **Customer service** area of the Shopify App Store.

Relevant Shopify App Store categories (structure may change; [VERIFY current categories]):

| Category | Subcategory | Fit for Agent Red |
|----------|------------|-------------------|
| Customer support | Chat, Messaging | Primary |
| Customer support | FAQ & help center | Secondary |
| Customer support | Feedback & surveys | Partial |
| Marketing | Email marketing | Indirect (through Mailchimp integration) |
| Sales | Live chat | Partial |

**Recommendation:** Select "Customer support" as the primary category. This is where merchants actively searching for Agent Red's value proposition will be browsing.

#### Keyword Strategy

Target keywords (sorted by estimated relevance and search volume):

| Keyword / Phrase | Estimated Volume | Competition | Priority |
|-----------------|-----------------|-------------|----------|
| customer service | High | High | Primary |
| customer support | High | High | Primary |
| AI customer service | Medium | Medium | Primary |
| chatbot | High | Very High | Secondary |
| live chat | High | Very High | Secondary (not Agent Red's primary model) |
| helpdesk | Medium | High | Secondary |
| AI chatbot | Medium | High | Secondary |
| automated support | Medium | Medium | Primary |
| customer engagement | Medium | Medium | Primary |
| order tracking | Medium | Medium | Tertiary |
| FAQ automation | Low-Medium | Low | Tertiary |
| AI agents | Low | Low | Emerging |

**Keyword placement priority:**
1. App name (highest weight)
2. Tagline (high weight)
3. Description opening paragraph (medium weight)
4. Feature descriptions (medium weight)
5. Keywords field in listing [VERIFY if Shopify has a dedicated keywords/tags field]

---

## 5. Shopify Plus Partner Program

### 5.1 What It Is

The Shopify Plus Partner Program is a separate, invite-or-application-based program for agencies, system integrators, and technology providers that serve enterprise-level Shopify merchants (those on Shopify Plus, which starts at ~$2,300/month [VERIFY current pricing]).

**URL:** https://www.shopify.com/plus/partners

This is distinct from the regular Shopify Partner Program. It is oriented toward service providers (agencies building stores, migrating platforms, etc.) rather than app developers. However, there is a "Technology Partner" track within Plus that is relevant for app developers.

### 5.2 Requirements

| Requirement | Details |
|-------------|---------|
| **Demonstrated expertise** | Track record of successful Shopify Plus implementations or integrations |
| **Technical capability** | Proven ability to work with Shopify Plus-specific features (Scripts, Flow, Launchpad, etc.) |
| **Client portfolio** | Evidence of enterprise-level client work |
| **Application process** | Must apply and be accepted; not automatic |
| **Certification** | Shopify Plus certifications may be required or strongly recommended [VERIFY] |

**For technology partners (app developers):**
| Requirement | Details |
|-------------|---------|
| Active public app | Must have a live app on the Shopify App Store |
| Plus merchant adoption | Some or growing usage by Shopify Plus merchants |
| Enterprise-grade features | App must support the needs of enterprise merchants (scalability, SLA, support) |
| Integration quality | High-quality integration with Plus-specific features |

### 5.3 Benefits

| Benefit | Description |
|---------|-------------|
| **Plus merchant referrals** | Shopify may refer Plus merchants to recommended technology partners |
| **Plus Partner Directory listing** | Visibility on Shopify's Plus Partner Directory |
| **Plus merchant events** | Invitations to enterprise-focused events and roundtables |
| **Dedicated Plus partner manager** | Single point of contact within the Plus team |
| **Co-marketing with Plus team** | Joint case studies, webinars, and content focused on enterprise use cases |
| **Early access** | Beta access to Plus-specific features and APIs |
| **Higher merchant quality** | Plus merchants are higher-revenue, longer-retention customers |
| **Training and resources** | Access to Plus-specific training materials and documentation |

### 5.4 Relevance to Agent Red

| Dimension | Assessment |
|-----------|-----------|
| **Immediate relevance (Launch 1.0)** | Low. Agent Red is a new app; Plus Partner status requires demonstrated enterprise traction. |
| **6-12 month relevance** | Medium. If Agent Red's Enterprise tier ($999/month) gains traction with Plus merchants, pursuing Plus Partner status would make sense. |
| **Strategic alignment** | High. Shopify Plus merchants are the highest-value segment for Agent Red (Enterprise tier, white-label, custom integrations). |
| **Recommendation** | Do not apply at launch. Build adoption first. Apply for Plus Partner status once Agent Red has 5-10 Plus merchant customers and can demonstrate enterprise-grade reliability. |

---

## 6. Built for Shopify Program

### 6.1 What It Is

"Built for Shopify" is a quality certification badge that Shopify awards to apps meeting elevated technical and quality standards. It was introduced in 2023 as a way to signal to merchants which apps meet Shopify's highest integration standards.

The badge appears on the app's listing in the Shopify App Store, providing a visual trust signal to merchants.

**URL:** https://shopify.dev/docs/apps/launch/built-for-shopify

### 6.2 Requirements

To earn the Built for Shopify badge, an app must meet all of the following criteria:

#### Technical Requirements

| Requirement | Details |
|-------------|---------|
| **Shopify App Bridge** | Must use the latest version of App Bridge |
| **Embedded app** | Must be an embedded app (runs within the Shopify admin) |
| **Shopify CLI** | Built with Shopify CLI tooling [VERIFY if strictly required or recommended] |
| **Polaris design system** | Uses Shopify Polaris for UI components |
| **Session tokens** | Uses session token authentication (not cookies) |
| **GraphQL API** | Uses the GraphQL Admin API (not just REST) [VERIFY requirement scope] |
| **App extensions** | Uses Shopify app extensions where applicable (e.g., theme app extensions for storefront integrations, checkout extensions) |
| **API versioning** | Uses a current, non-deprecated API version |
| **Webhooks** | Proper webhook implementation including mandatory GDPR webhooks |
| **Billing API** | Uses Shopify Billing API for charges |

#### Quality Requirements

| Requirement | Details |
|-------------|---------|
| **Performance** | App loads quickly, no significant performance degradation |
| **Stability** | Low error/crash rate |
| **Onboarding** | Clear, guided onboarding experience |
| **Support quality** | Responsive support with good merchant satisfaction |
| **Ratings** | Minimum rating threshold (4.0+ stars [VERIFY exact threshold]) |
| **Review count** | Minimum number of reviews [VERIFY if there is a minimum] |
| **Active development** | Evidence of ongoing maintenance and updates |

#### Business Requirements

| Requirement | Details |
|-------------|---------|
| **Active app** | App must be live on the Shopify App Store |
| **Sufficient installs** | Must have a meaningful number of active installs [VERIFY threshold] |
| **Compliance** | No policy violations or unresolved merchant complaints |

### 6.3 Benefits

| Benefit | Details |
|---------|---------|
| **Trust badge** | "Built for Shopify" badge displayed on app listing |
| **Search ranking boost** | Badge holders may receive improved ranking in App Store search [VERIFY] |
| **Merchant confidence** | Badge signals quality, increasing conversion rate from views to installs |
| **Editorial consideration** | Badge holders may be more likely to be featured in collections and Staff Picks |
| **Partner team attention** | Badge holders demonstrate commitment, potentially leading to better partner relationship |

### 6.4 Relevance to Agent Red

| Dimension | Assessment |
|-----------|-----------|
| **Should Agent Red pursue this?** | Yes, absolutely. It should be a goal for Q2-Q3 2026. |
| **Can it be achieved at launch?** | Unlikely. The program requires live app with active installs and reviews first. |
| **Technical readiness** | Agent Red should build to Built for Shopify standards from day one (App Bridge, Polaris, GraphQL, session tokens) even if the badge is earned later. |
| **Timeline estimate** | 3-6 months after app launch (need installs, reviews, stability track record) |
| **Action items** | Build with Polaris UI components; use GraphQL Admin API; implement all required technical standards from launch. This avoids retrofitting later. |

---

## 7. Shopify App Challenges and Competitions

### 7.1 Shopify App Challenge

Shopify has historically run app development challenges/competitions:

| Event | Details | Relevance |
|-------|---------|-----------|
| **Shopify App Challenge** | Periodic competition for new apps built on specific themes or using specific APIs | High visibility if won; cash prizes + App Store promotion |
| **Frequency** | Not annual; tied to platform launches or specific initiatives | Unpredictable |
| **Themes** | Past challenges have focused on: commerce, B2B, AI, checkout extensions, POS | AI-focused challenges would be directly relevant to Agent Red |

[VERIFY: Check https://shopify.dev for any currently active or announced app challenges. Shopify does not run these on a fixed schedule.]

**Past notable challenges:**
- Shopify has run challenges tied to new platform features (e.g., when they launched checkout extensions, they encouraged app development in that area)
- Prizes have included cash awards ($10,000-$50,000 [VERIFY past prize amounts]), App Store promotion, and meetings with Shopify leadership
- AI-themed challenges have become more common as Shopify invests in AI (Sidekick, etc.)

### 7.2 Shopify Editions Tie-Ins

Around Shopify Editions announcements, Shopify often highlights apps that use newly announced features. This creates an organic opportunity:

| Strategy | Implementation |
|----------|---------------|
| Watch Editions announcements | Monitor for new APIs, features, and platform directions |
| Build for new features quickly | Be among the first apps to integrate newly announced capabilities |
| Submit for editorial consideration | After implementing a new feature, reach out to Shopify's partner team highlighting your early adoption |

### 7.3 Hackathons and Community Events

| Event Type | Where to Find | Notes |
|-----------|---------------|-------|
| Shopify-sponsored hackathons | Shopify developer community, Shopify events page | Periodic, usually virtual |
| Community hackathons | Dev.to, MLH, Devpost | Third-party hackathons sometimes include Shopify tracks |
| Partner meetups | Shopify Community Events page | Local and virtual networking |

**Recommendation for Agent Red:** Monitor Shopify's developer blog (https://shopify.dev/blog) and the Shopify Community forums for announced challenges. If an AI-themed challenge is announced, Agent Red should participate -- the visibility and credibility from winning or placing are substantial.

---

## 8. Partner Academy and Certifications

### 8.1 Shopify Partner Academy

The Shopify Partner Academy (https://academy.shopify.com [VERIFY current URL]) provides free online courses and certifications for partners.

| Feature | Details |
|---------|---------|
| **Cost** | Free |
| **Format** | Online, self-paced |
| **Content** | Courses on Shopify fundamentals, app development, store setup, business growth |
| **Certifications** | Official Shopify certifications upon passing exams |
| **Languages** | Available in multiple languages [VERIFY current list] |

### 8.2 Available Certifications

| Certification | Audience | Content | Duration | Relevance to Agent Red |
|-------------|---------|---------|----------|----------------------|
| **Shopify App Development** | Developers | Building apps, API usage, App Bridge, billing | ~4-8 hours [VERIFY] | High -- validates app development competency |
| **Shopify Foundations** | All partners | Shopify platform basics, ecosystem overview | ~2-4 hours | Medium -- useful background knowledge |
| **Product Fundamentals** | Merchants/agencies | Understanding Shopify products and features | ~2-3 hours | Low -- merchant-focused |
| **Shopify Plus Fundamentals** | Plus-focused partners | Plus-specific features, enterprise use cases | ~3-5 hours [VERIFY] | Medium -- useful if pursuing Plus merchants |
| **Business Fundamentals** | All partners | Running a Shopify partner business | ~2-4 hours | Low -- general business content |

[VERIFY: The specific certifications available change over time. Check https://academy.shopify.com for the current catalog. Shopify may have added AI-specific or advanced development certifications since May 2025.]

### 8.3 Marketplace Advantages

| Certification Advantage | Details |
|------------------------|---------|
| **Partner Directory badge** | Certified partners may display badges in the partner directory |
| **Merchant trust** | Certifications signal expertise to merchants evaluating your app |
| **App review context** | Certification may provide marginal goodwill during app review (not formally documented as a factor) |
| **Plus Partner eligibility** | Certifications may be required or advantageous for Plus Partner applications |
| **Team competency** | Useful for onboarding new team members to the Shopify ecosystem |

**Recommendation for Agent Red:**
- Complete "Shopify App Development" certification before submitting the app -- it ensures the team understands all app requirements
- Complete "Shopify Plus Fundamentals" if pursuing enterprise (Plus) merchants
- Certifications are free and relatively quick; the ROI is positive even if the marketplace benefit is marginal

---

## 9. Strategic Relevance to Agent Red

### 9.1 Summary Assessment

| Topic | Relevance | Priority | Action Timeline |
|-------|-----------|----------|-----------------|
| **Shopify App Store listing** | Critical | P0 | Phase 2.1 (build as Shopify app) |
| **App Store approval** | Critical | P0 | Must pass review before launch |
| **Built for Shopify badge** | High | P1 | Build to standards from day one; apply after 3-6 months |
| **App Store Optimization** | High | P0 | Optimize listing at launch; iterate based on data |
| **Reviews strategy** | High | P1 | Implement in-app review prompts after initial installs |
| **App Store Ads** | Medium-High | P2 | Consider at launch for initial visibility boost [VERIFY availability] |
| **Partner certifications** | Medium | P1 | Complete before app submission |
| **Shopify Plus Partners** | Medium | P3 | Apply after 5-10 Plus merchant customers |
| **App challenges** | Low-Medium | Opportunistic | Monitor and participate when relevant |
| **Co-marketing** | Low (initially) | P3+ | Pursue after establishing traction |
| **Partner manager** | Low (initially) | Organic | Becomes available as app grows |

### 9.2 Dual-Channel Strategy: App Store + Direct Sales

The Stripe evaluation (STRIPE-PLATFORM-EVALUATION.md) established Stripe as the billing platform for direct sales. The Shopify App Store serves as a parallel distribution channel:

| Channel | Role | Billing | Revenue Share | Audience |
|---------|------|---------|--------------|----------|
| **Shopify App Store** | Discovery and distribution | Shopify Billing API | 0% (first $1M), then 15% | Shopify merchants browsing the App Store |
| **Agent Red website (agentred.io)** | Direct sales, SEO, content marketing | Stripe | 0% (Stripe has no revenue share; only processing fees ~4%) | All e-commerce businesses (broader audience) |

**This dual-channel approach maximizes reach:**
- The App Store provides zero-cost discovery among Shopify's millions of merchants
- Direct sales via the website maximize margin (no 15% share) and reach non-Shopify merchants
- Both channels can coexist; the pricing should be consistent to avoid channel conflict

### 9.3 Key Decisions for Phase 2.1

| Decision | Options | Recommendation |
|----------|---------|----------------|
| Build as native Shopify app or standalone with Shopify integration? | (A) Fully embedded Shopify app, (B) Standalone with Shopify OAuth connector | (A) Fully embedded -- maximizes App Store eligibility and "Built for Shopify" potential |
| Price through Shopify Billing API or external? | (A) Shopify Billing only, (B) Stripe only, (C) Both | (C) Both -- Shopify Billing for App Store installs, Stripe for direct website sales |
| Use Polaris design system? | (A) Yes throughout, (B) Custom UI | (A) Yes -- required for Built for Shopify, provides consistent admin experience |
| GraphQL or REST API? | (A) GraphQL, (B) REST, (C) Both | (A) GraphQL primary -- required for Built for Shopify, more efficient for complex queries |

---

## 10. Key URLs Reference

### Shopify Partner Program

| Resource | URL |
|----------|-----|
| Shopify Partners Home | https://www.shopify.com/partners |
| Partner Signup | https://partners.shopify.com/signup |
| Partner Dashboard | https://partners.shopify.com |
| Partner Academy | https://academy.shopify.com |
| Shopify Plus Partners | https://www.shopify.com/plus/partners |

### App Development

| Resource | URL |
|----------|-----|
| Shopify Dev Documentation | https://shopify.dev |
| App Requirements Checklist | https://shopify.dev/docs/apps/launch/app-requirements-checklist |
| App Submission Guide | https://shopify.dev/docs/apps/launch/submit |
| App Review Process | https://shopify.dev/docs/apps/launch/app-review |
| Built for Shopify | https://shopify.dev/docs/apps/launch/built-for-shopify |
| App Promotion | https://shopify.dev/docs/apps/launch/promote |

### Technical Documentation

| Resource | URL |
|----------|-----|
| OAuth Documentation | https://shopify.dev/docs/apps/auth/oauth |
| App Bridge | https://shopify.dev/docs/api/app-bridge |
| Billing API | https://shopify.dev/docs/apps/billing |
| Mandatory Webhooks (GDPR) | https://shopify.dev/docs/apps/webhooks/configuration/mandatory-webhooks |
| Polaris Design System | https://polaris.shopify.com |
| GraphQL Admin API | https://shopify.dev/docs/api/admin-graphql |
| REST Admin API | https://shopify.dev/docs/api/admin-rest |
| API Versioning | https://shopify.dev/docs/api/usage/versioning |

### Shopify App Store

| Resource | URL |
|----------|-----|
| Shopify App Store | https://apps.shopify.com |
| Customer Service Category | https://apps.shopify.com/categories/customer-support [VERIFY exact URL] |

### Community and Events

| Resource | URL |
|----------|-----|
| Shopify Developer Blog | https://shopify.dev/blog |
| Shopify Community Forums | https://community.shopify.com |
| Shopify Changelog | https://shopify.dev/changelog |
| Shopify Editions | https://www.shopify.com/editions [VERIFY] |

---

## Appendix A: Items Requiring Live Verification

The following items in this document are marked [VERIFY] and should be confirmed against live Shopify documentation before making commitments:

| Item | Section | Verification URL |
|------|---------|-----------------|
| Revenue share: 0% up to $1M, 15% above | 1.4.3, 2.3 | https://shopify.dev/docs/apps/billing |
| Whether $1M threshold is lifetime or annual | 2.3 | https://shopify.dev/docs/apps/billing |
| App review timeline (5-10 business days) | 1.7 | https://shopify.dev/docs/apps/launch/app-review |
| App Store ads availability and pricing | 3.7 | https://shopify.dev/docs/apps/launch/promote |
| Built for Shopify exact rating threshold | 6.2 | https://shopify.dev/docs/apps/launch/built-for-shopify |
| Built for Shopify install minimum | 6.2 | https://shopify.dev/docs/apps/launch/built-for-shopify |
| Current App Bridge required version | 1.4.2 | https://shopify.dev/docs/api/app-bridge |
| Demo video required vs optional | 1.5 | https://shopify.dev/docs/apps/launch/submit |
| Screenshot minimum count and dimensions | 1.5 | https://shopify.dev/docs/apps/launch/submit |
| App icon dimensions | 1.5 | https://shopify.dev/docs/apps/launch/submit |
| Current Shopify Plus pricing | 5.1 | https://www.shopify.com/plus |
| Academy certification catalog | 8.2 | https://academy.shopify.com |
| Polaris requirement strictness | 1.8 | https://shopify.dev/docs/apps/launch/built-for-shopify |
| GraphQL requirement scope for BfS | 6.2 | https://shopify.dev/docs/apps/launch/built-for-shopify |
| Active app challenges | 7.1 | https://shopify.dev |
| Unite vs Editions event status | 3.6 | https://www.shopify.com/editions |
| Referral bounty current amounts | 2.3 | https://www.shopify.com/partners |

---

*Research prepared for Agent Red Customer Engagement Phase 2.1 platform and go-to-market planning.*
*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
