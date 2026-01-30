# Agent Red Customer Engagement — Terms of Service

> **Status:** DRAFT — For internal review only. Not yet published.
> **Version:** 0.1.0
> **Last Updated:** 2026-01-29
> **Legal Review Required:** Yes — must be reviewed by qualified legal counsel before publication.

---

## Terms of Service

**Effective Date:** [TO BE SET AT PUBLICATION]

These Terms of Service ("Terms") govern your access to and use of the Agent Red Customer Engagement platform ("Service"), operated by VanDusen & Palmeter, LLC, doing business as Remaker Digital ("Company", "we", "us", or "our").

By accessing or using the Service, you agree to be bound by these Terms. If you are using the Service on behalf of an organization, you represent that you have authority to bind that organization to these Terms.

---

### 1. Definitions

**"Account"** means the account you create to access the Service.

**"API"** means the application programming interface provided by the Service for programmatic access.

**"API Key"** means the unique authentication credential issued to you for API access.

**"Content"** means any data, text, information, or other materials submitted to, processed by, or generated through the Service.

**"Customer Data"** means any data you or your end users submit to the Service, including but not limited to customer inquiries, product information, order data, and knowledge base content.

**"End Users"** means the individuals who interact with the Service through your deployment (e.g., your customers submitting support inquiries).

**"Service"** means the Agent Red Customer Engagement platform, including the web application, API, documentation, and any related services.

**"Persistent Customer Memory"** means the Service's multi-layer personalization system that builds customer context, conversation history, and learned preferences across support sessions to enable personalized responses.

**"Dedicated Model Training"** means the optional Enterprise add-on that fine-tunes a per-customer AI model using that Customer's own historical conversation data, subject to explicit opt-in consent.

**"Subscription"** means the paid plan you select to access the Service, as described in Section 5.

---

### 2. Account Registration and Security

2.1. **Registration.** You must create an Account to use the Service. You agree to provide accurate, current, and complete information during registration.

2.2. **Account Security.** You are responsible for maintaining the security of your Account credentials, including API Keys. You must notify us immediately at security@remakerdigital.com if you become aware of any unauthorized access to your Account.

2.3. **Account Responsibility.** You are responsible for all activities that occur under your Account, whether or not authorized by you.

2.4. **Age Requirement.** You must be at least 18 years of age to create an Account and use the Service.

---

### 3. Use of the Service

3.1. **License Grant.** Subject to these Terms and payment of applicable fees, we grant you a limited, non-exclusive, non-transferable, revocable license to access and use the Service during your Subscription period.

3.2. **Acceptable Use.** You agree to use the Service only for lawful purposes and in accordance with these Terms. You shall not:

   (a) Use the Service to process, store, or transmit content that is unlawful, harmful, threatening, abusive, harassing, defamatory, or otherwise objectionable;

   (b) Attempt to gain unauthorized access to the Service, other accounts, or any related systems or networks;

   (c) Interfere with or disrupt the integrity or performance of the Service;

   (d) Reverse engineer, decompile, disassemble, or otherwise attempt to derive the source code of the Service;

   (e) Use the Service to build a competing product or service;

   (f) Exceed the usage limits of your Subscription tier;

   (g) Share, transfer, or sublicense your Account or API Keys to any third party without our prior written consent;

   (h) Use the Service in any manner that could damage, disable, overburden, or impair the Service;

   (i) Use automated means to access the Service beyond the provided API, unless expressly authorized.

3.3. **API Usage.** If you access the Service through the API, you agree to comply with our API documentation and any rate limits associated with your Subscription tier.

3.4. **Third-Party Integrations.** The Service may integrate with third-party platforms (e.g., Shopify, Zendesk). Your use of such integrations is subject to the respective third party's terms of service. We are not responsible for third-party services.

---

### 4. Customer Data and Privacy

4.1. **Data Ownership.** You retain all rights, title, and interest in your Customer Data. We do not claim ownership of any Customer Data.

4.2. **Data Processing.** We process Customer Data solely to provide the Service to you. Our processing of personal data is governed by our [Privacy Policy](/privacy) and, where applicable, our [Data Processing Agreement](/dpa).

4.3. **AI Processing.** The Service uses artificial intelligence models to process customer inquiries. Customer Data may be sent to AI model providers (e.g., Azure OpenAI Service) for processing. We implement PII tokenization to protect personally identifiable information before it is sent to third-party AI services.

4.4. **Data Retention.** Customer Data is retained for the duration of your Subscription. Upon termination, we will delete your Customer Data within 30 days, unless retention is required by law. You may request data export at any time during your Subscription.

4.5. **Data Security.** We implement industry-standard security measures to protect Customer Data, including encryption in transit (TLS) and at rest, access controls, and regular security reviews. See our [Service Level Agreement](/sla) for specific commitments.

4.6. **Data Location.** Customer Data is processed and stored in Microsoft Azure data centers in the United States (East US 2 region).

4.7. **Personalization and Model Training.**

   (a) **Persistent Customer Memory.** The Service includes Persistent Customer Memory, which processes Customer Data to personalize support interactions. Layers 1–3 (Customer Context, Conversation Memory, and Cross-Session Learning) operate automatically as part of the Service's core functionality based on your Subscription tier. No additional consent is required for these layers.

   (b) **Dedicated Model Training (Opt-In).** Enterprise Customers may opt in to Dedicated Model Training by providing explicit written consent through the Service dashboard or a signed order form. Dedicated Model Training uses only that Customer's own historical conversation data to fine-tune a per-customer AI model. Customer data is never combined with other Customers' data for training purposes.

   (c) **Consent Revocation.** You may revoke consent for Dedicated Model Training at any time through the Service dashboard. Upon revocation, all future training is halted and the fine-tuned model is deleted within 30 days. Revocation does not affect the lawfulness of processing performed before revocation.

   (d) **Clarification.** Persistent Customer Memory Layers 1–3 do not constitute "model training" as referenced in the Privacy Policy Section 3.2. These layers store and retrieve customer-specific data at inference time — they do not modify AI model weights. Only Layer 4 (Dedicated Model Training) involves modification of model weights and requires explicit opt-in consent.

---

### 5. Subscription Plans and Fees

5.1. **Plans.** The Service is offered through the following Subscription tiers with included monthly conversation allowances:

   - **Starter:** $149/month or $1,490/year — 1,000 included conversations per month ($0.04/conversation overage)
   - **Professional:** $399/month or $3,990/year — 5,000 included conversations per month ($0.025/conversation overage)
   - **Enterprise:** $999/month or $9,990/year — 20,000 included conversations per month ($0.015/conversation overage)

5.2. **Add-On Modules.** Additional modules may be purchased separately, subject to tier eligibility:

   - Multi-Language Pack: $99/month (All tiers)
   - Advanced Analytics: $149/month (Professional, Enterprise)
   - Mailchimp Integration: $49/month (Professional, Enterprise)
   - Google Analytics Integration: $49/month (Professional, Enterprise)
   - White-Label Package: $399/month (Enterprise only)
   - Priority Support Upgrade: $99/month (Starter, Professional)
   - Custom Integration Dev: $299/month (Enterprise only)
   - Dedicated Model Training: $299/month (Enterprise only; requires opt-in consent per Section 4.7)

5.3. **Billing.** Subscription fees are billed in advance on a monthly or annual basis, depending on the plan selected. All fees are in United States Dollars (USD).

5.4. **Payment.** Payment is due upon invoice. We accept major credit cards and other payment methods as indicated during checkout. You authorize us to charge your designated payment method for all applicable fees.

5.5. **Price Changes.** We may change our pricing with at least 30 days' prior written notice. Price changes will take effect at the start of your next billing cycle.

5.6. **Taxes.** All fees are exclusive of applicable taxes. You are responsible for all sales, use, and other taxes associated with your Subscription, excluding taxes based on our net income.

5.7. **Overages.** If you exceed the conversation limits of your Subscription tier, we will notify you and may either (a) upgrade your Subscription to an appropriate tier, or (b) throttle your usage until the next billing period. We will not charge overage fees without your prior consent.

---

### 6. Free Trials

6.1. **Trial Period.** We may offer a free trial period at our discretion. During the trial, you may access the Service with limited functionality.

6.2. **Trial Conversion.** At the end of the trial period, you must select a paid Subscription to continue using the Service. If you do not select a plan, your access will be suspended.

6.3. **No Obligation.** Free trials do not create any obligation to purchase a Subscription.

---

### 7. Intellectual Property

7.1. **Our IP.** The Service, including all software, algorithms, designs, documentation, and trademarks, is owned by VanDusen & Palmeter, LLC. Nothing in these Terms transfers any intellectual property rights to you, except the limited license granted in Section 3.1.

7.2. **Your IP.** You retain all intellectual property rights in your Customer Data and any content you create using the Service.

7.3. **Feedback.** If you provide suggestions, ideas, or feedback about the Service ("Feedback"), you grant us a worldwide, perpetual, irrevocable, royalty-free license to use, modify, and incorporate such Feedback into the Service without restriction or obligation to you.

---

### 8. Warranties and Disclaimers

8.1. **Our Warranty.** We warrant that the Service will perform materially in accordance with our published documentation during your Subscription period.

8.2. **Disclaimer.** EXCEPT AS EXPRESSLY SET FORTH IN SECTION 8.1, THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE." WE DISCLAIM ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.

8.3. **AI Limitations.** The Service uses artificial intelligence to generate responses. AI-generated content may not always be accurate, complete, or appropriate. You are responsible for reviewing and validating any AI-generated responses before they are presented to your End Users.

8.4. **No Guarantee.** We do not guarantee that the Service will be uninterrupted, error-free, or free of harmful components.

---

### 9. Limitation of Liability

9.1. **Cap.** TO THE MAXIMUM EXTENT PERMITTED BY LAW, OUR TOTAL LIABILITY TO YOU FOR ALL CLAIMS ARISING UNDER OR RELATED TO THESE TERMS SHALL NOT EXCEED THE TOTAL FEES PAID BY YOU IN THE TWELVE (12) MONTHS IMMEDIATELY PRECEDING THE EVENT GIVING RISE TO THE CLAIM.

9.2. **Exclusion.** IN NO EVENT SHALL WE BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO LOSS OF PROFITS, DATA, BUSINESS, OR GOODWILL, REGARDLESS OF WHETHER WE HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

9.3. **Essential Purpose.** THE LIMITATIONS IN THIS SECTION SHALL APPLY NOTWITHSTANDING THE FAILURE OF THE ESSENTIAL PURPOSE OF ANY LIMITED REMEDY.

---

### 10. Indemnification

10.1. **Your Indemnity.** You agree to indemnify, defend, and hold harmless the Company and its officers, directors, employees, and agents from any claims, liabilities, damages, losses, and expenses (including reasonable attorneys' fees) arising from:

   (a) Your use of the Service;
   (b) Your violation of these Terms;
   (c) Your Customer Data;
   (d) Your End Users' use of the Service.

---

### 11. Term and Termination

11.1. **Term.** These Terms are effective when you create an Account and continue until terminated.

11.2. **Termination by You.** You may terminate your Subscription at any time through your Account settings. Termination takes effect at the end of your current billing period. No refunds are provided for partial billing periods.

11.3. **Termination by Us.** We may suspend or terminate your Account if:

   (a) You breach these Terms and fail to cure the breach within 14 days of notice;
   (b) You fail to pay applicable fees within 30 days of the due date;
   (c) We are required to do so by law;
   (d) We determine, in our sole discretion, that your use poses a security risk to the Service or other users.

11.4. **Effect of Termination.** Upon termination:

   (a) Your license to use the Service immediately ceases;
   (b) You must cease all use of the Service and API Keys;
   (c) We will make your Customer Data available for export for 30 days, after which it will be deleted;
   (d) Sections 4.1, 7, 8.2, 9, 10, and 13 survive termination.

---

### 12. Modifications to Terms

12.1. **Changes.** We may modify these Terms at any time by posting updated Terms on our website. We will provide at least 30 days' notice of material changes via email or through the Service.

12.2. **Acceptance.** Your continued use of the Service after the effective date of modified Terms constitutes acceptance. If you do not agree with the modified Terms, you must stop using the Service and terminate your Account.

---

### 13. General Provisions

13.1. **Governing Law.** These Terms are governed by the laws of the State of Delaware, United States, without regard to conflict of law principles.

13.2. **Dispute Resolution.** Any dispute arising from these Terms shall be resolved through binding arbitration administered by the American Arbitration Association under its Commercial Arbitration Rules, with arbitration conducted in Delaware. The arbitrator's decision shall be final and binding.

13.3. **Class Action Waiver.** You agree to resolve disputes with us on an individual basis. You waive any right to participate in class actions, class arbitrations, or representative proceedings.

13.4. **Severability.** If any provision of these Terms is found unenforceable, the remaining provisions shall remain in full force and effect.

13.5. **Entire Agreement.** These Terms, together with the Privacy Policy, SLA, and any applicable Data Processing Agreement, constitute the entire agreement between you and the Company regarding the Service.

13.6. **Assignment.** You may not assign these Terms without our prior written consent. We may assign these Terms in connection with a merger, acquisition, or sale of all or substantially all of our assets.

13.7. **Waiver.** Our failure to enforce any provision of these Terms shall not be deemed a waiver of that provision.

13.8. **Notices.** Notices to you will be sent to the email address associated with your Account. Notices to us should be sent to:

   VanDusen & Palmeter, LLC (DBA Remaker Digital)
   Email: legal@remakerdigital.com

13.9. **Force Majeure.** We shall not be liable for any failure or delay in performance due to causes beyond our reasonable control, including but not limited to acts of God, natural disasters, pandemics, war, terrorism, labor disputes, or failure of third-party services.

---

### Contact

If you have questions about these Terms, contact us at:

**VanDusen & Palmeter, LLC (DBA Remaker Digital)**
Email: legal@remakerdigital.com
Website: https://remakerdigital.com

---

*© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

> **IMPORTANT NOTICE:** This document is an AI-generated draft provided for internal planning purposes only. It is NOT legal advice. This document must be reviewed and approved by qualified legal counsel before publication or use. Do not rely on this draft as a binding legal document.
