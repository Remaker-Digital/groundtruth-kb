const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, Header, Footer, AlignmentType, HeadingLevel, BorderStyle,
  WidthType, ShadingType, PageBreak, PageNumber, TabStopType, TabStopPosition,
  LevelFormat, VerticalAlign,
} = require("docx");

// Per S307 hardcoded-path directive: discover repo root from this script's
// location. This file is at docs/generate-exec-summary.js; the repo root is
// its parent directory. Using path.resolve(__dirname, "..", ...) makes the
// script portable across workstations (no machine-local literals).
const REPO_ROOT = path.resolve(__dirname, "..");

// Brand color
const BRAND = "FF3621";
const BRAND_DARK = "CC2B1A";
const HEADER_BG = "2D2D2D";
const LIGHT_BG = "F9F9F9";
const LIGHT_BRAND_BG = "FFF0ED";
const MID_GRAY = "666666";
const BORDER_COLOR = "DDDDDD";
const WHITE = "FFFFFF";
const BLACK = "000000";

// Logo
// Per S307: derive from REPO_ROOT (computed via __dirname above), not literal.
const logoData = fs.readFileSync(
  path.resolve(REPO_ROOT, "branding", "logo", "PNG", "NEW-BLOCK-LOGO-HORIZONTAL-LIGHT.png")
);

// Table helpers
const thinBorder = { style: BorderStyle.SINGLE, size: 1, color: BORDER_COLOR };
const borders = { top: thinBorder, bottom: thinBorder, left: thinBorder, right: thinBorder };
const noBorders = {
  top: { style: BorderStyle.NONE, size: 0 },
  bottom: { style: BorderStyle.NONE, size: 0 },
  left: { style: BorderStyle.NONE, size: 0 },
  right: { style: BorderStyle.NONE, size: 0 },
};
const cellMargins = { top: 60, bottom: 60, left: 100, right: 100 };
const TABLE_WIDTH = 9360;

function headerCell(text, width, opts = {}) {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: opts.fill || HEADER_BG, type: ShadingType.CLEAR },
    margins: cellMargins,
    verticalAlign: VerticalAlign.CENTER,
    children: [
      new Paragraph({
        alignment: opts.align || AlignmentType.LEFT,
        children: [new TextRun({ text, bold: true, color: opts.color || WHITE, font: "Arial", size: 18 })],
      }),
    ],
  });
}

function dataCell(text, width, opts = {}) {
  const runs = Array.isArray(text)
    ? text
    : [new TextRun({ text, font: "Arial", size: 18, color: opts.color || BLACK, bold: opts.bold || false })];
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: opts.fill ? { fill: opts.fill, type: ShadingType.CLEAR } : undefined,
    margins: cellMargins,
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({ alignment: opts.align || AlignmentType.LEFT, children: runs })],
  });
}

function brandCell(text, width, opts = {}) {
  return dataCell(text, width, { ...opts, fill: LIGHT_BRAND_BG, bold: true, color: BRAND_DARK });
}

function sectionTitle(text) {
  return new Paragraph({
    spacing: { before: 300, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: BRAND, space: 4 } },
    children: [new TextRun({ text, bold: true, font: "Arial", size: 26, color: BRAND })],
  });
}

function bodyText(text, opts = {}) {
  return new Paragraph({
    spacing: { after: opts.afterSpacing || 120 },
    alignment: opts.align || AlignmentType.LEFT,
    children: [new TextRun({ text, font: "Arial", size: 20, color: opts.color || "333333" })],
  });
}

function smallText(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 80 },
    alignment: opts.align || AlignmentType.LEFT,
    children: [new TextRun({ text, font: "Arial", size: 16, color: opts.color || MID_GRAY, italics: opts.italics || false })],
  });
}

function spacer(size = 100) {
  return new Paragraph({ spacing: { before: size, after: 0 }, children: [] });
}

// ─── Footer ───
function makeFooter() {
  return new Footer({
    children: [
      new Paragraph({
        border: { top: { style: BorderStyle.SINGLE, size: 2, color: BORDER_COLOR, space: 4 } },
        spacing: { before: 60 },
        tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
        children: [
          new ImageRun({
            type: "png",
            data: logoData,
            transformation: { width: 100, height: 22 },
            altText: { title: "Remaker Digital Logo", description: "Remaker Digital company logo", name: "logo" },
          }),
          new TextRun({ text: "  ", font: "Arial", size: 14 }),
          new TextRun({
            text: "\u00A9 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.",
            font: "Arial",
            size: 14,
            color: MID_GRAY,
          }),
          new TextRun({ text: "\t", font: "Arial", size: 14 }),
          new TextRun({ text: "Page ", font: "Arial", size: 14, color: MID_GRAY }),
          new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 14, color: MID_GRAY }),
        ],
      }),
    ],
  });
}

// ═══════════════════════════════════════════════════════════════
// PAGE 1: Cover / Executive Summary
// ═══════════════════════════════════════════════════════════════

const page1 = [
  spacer(600),
  // Logo at top
  new Paragraph({
    alignment: AlignmentType.LEFT,
    children: [
      new ImageRun({
        type: "png",
        data: logoData,
        transformation: { width: 200, height: 44 },
        altText: { title: "Remaker Digital Logo", description: "Remaker Digital company logo", name: "logo-cover" },
      }),
    ],
  }),
  spacer(400),
  // Title
  new Paragraph({
    spacing: { after: 80 },
    children: [new TextRun({ text: "Agent Red Customer Experience", font: "Arial", size: 44, bold: true, color: BLACK })],
  }),
  new Paragraph({
    spacing: { after: 40 },
    children: [new TextRun({ text: "Executive Summary", font: "Arial", size: 36, color: BRAND })],
  }),
  new Paragraph({
    spacing: { after: 300 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BRAND, space: 8 } },
    children: [new TextRun({ text: "AI-Powered Customer Engagement Platform for E-Commerce", font: "Arial", size: 22, color: MID_GRAY })],
  }),
  spacer(200),
  // Executive overview
  new Paragraph({
    spacing: { after: 60 },
    children: [new TextRun({ text: "Overview", font: "Arial", size: 24, bold: true, color: BLACK })],
  }),
  bodyText(
    "Agent Red is a multi-tenant SaaS platform that delivers AI-powered customer service for e-commerce merchants. " +
    "Built on a proprietary 6-agent AI pipeline with 4-layer persistent customer memory, it provides fast, accurate, " +
    "and safety-validated automated responses at a fraction of competitor costs. The platform supports both Shopify-embedded " +
    "and standalone deployment models, with full white-label capability for enterprise partners. Currently in late beta " +
    "with production infrastructure deployed on Microsoft Azure, Agent Red is progressing through final production-readiness gates.",
    { afterSpacing: 200 }
  ),
  // Key metrics box
  new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [1872, 1872, 1872, 1872, 1872],
    rows: [
      new TableRow({
        children: [
          headerCell("Specifications", 1872, { align: AlignmentType.CENTER }),
          headerCell("Tests", 1872, { align: AlignmentType.CENTER }),
          headerCell("API Endpoints", 1872, { align: AlignmentType.CENTER }),
          headerCell("Backend Modules", 1872, { align: AlignmentType.CENTER }),
          headerCell("Widget Footprint", 1872, { align: AlignmentType.CENTER }),
        ],
      }),
      new TableRow({
        children: [
          brandCell("2,092", 1872, { align: AlignmentType.CENTER }),
          brandCell("11,055", 1872, { align: AlignmentType.CENTER }),
          brandCell("140+", 1872, { align: AlignmentType.CENTER }),
          brandCell("89", 1872, { align: AlignmentType.CENTER }),
          brandCell("~17KB gzip", 1872, { align: AlignmentType.CENTER }),
        ],
      }),
    ],
  }),
  spacer(200),
  // Distribution channels
  new Paragraph({
    spacing: { after: 60 },
    children: [new TextRun({ text: "Distribution Channels", font: "Arial", size: 24, bold: true, color: BLACK })],
  }),
  new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [3120, 3120, 3120],
    rows: [
      new TableRow({
        children: [
          headerCell("Shopify App Store", 3120, { align: AlignmentType.CENTER }),
          headerCell("Standalone (API Key)", 3120, { align: AlignmentType.CENTER }),
          headerCell("White-Label / OEM", 3120, { align: AlignmentType.CENTER }),
        ],
      }),
      new TableRow({
        children: [
          dataCell("Native Theme App Extension, Polaris admin, Shopify Billing API", 3120, { fill: LIGHT_BG }),
          dataCell("Any website via embed script, Mantine admin dashboard, Stripe billing", 3120, { fill: LIGHT_BG }),
          dataCell("Full branding removal, custom domains, CSS theming, reseller portal (Enterprise)", 3120, { fill: LIGHT_BG }),
        ],
      }),
    ],
  }),
  new Paragraph({ children: [new PageBreak()] }),
];

// ═══════════════════════════════════════════════════════════════
// PAGE 2: Technology & Architecture
// ═══════════════════════════════════════════════════════════════

const page2 = [
  sectionTitle("Technology & Architecture"),
  smallText("Full-stack platform architecture — from widget to infrastructure", { italics: true }),
  spacer(80),
  // Architecture diagram as layered table
  // Layer 1: Presentation
  new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [4680, 4680],
    rows: [
      new TableRow({
        children: [
          headerCell("PRESENTATION LAYER", TABLE_WIDTH, { fill: "4A90D9", align: AlignmentType.CENTER }),
          // merge hack: make second cell same header
        ].slice(0, 1).concat([
          headerCell("", 4680, { fill: "4A90D9" }),
        ]),
      }),
      new TableRow({
        children: [
          dataCell("Chat Widget (Preact + TypeScript, ~17KB gzip, Shadow DOM)", 4680, { fill: "E8F0FE" }),
          dataCell("Admin Dashboards: Shopify Polaris | Standalone Mantine | Provider Console (20 pages)", 4680, { fill: "E8F0FE" }),
        ],
      }),
    ],
  }),
  spacer(40),
  // Layer 2: API Gateway
  new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [
      new TableRow({
        children: [headerCell("API GATEWAY", 9360, { fill: "3D7ABF", align: AlignmentType.CENTER })],
      }),
      new TableRow({
        children: [dataCell("FastAPI (Python) — 44 routers, 140+ routes, 9 middleware layers, triple auth (Shopify JWT + API key + widget key)", 9360, { fill: "D6E4F0" })],
      }),
    ],
  }),
  spacer(40),
  // Layer 3: AI Pipeline
  new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [1560, 1560, 1560, 1560, 1560, 1560],
    rows: [
      new TableRow({
        children: [headerCell("6-AGENT AI PIPELINE (AGNTCY A2A Protocol)", 9360, { fill: BRAND, align: AlignmentType.CENTER })].concat(
          [1560, 1560, 1560, 1560, 1560].map(w => headerCell("", w, { fill: BRAND }))
        ),
      }),
      new TableRow({
        children: [
          dataCell("Intent Classifier", 1560, { fill: LIGHT_BRAND_BG, align: AlignmentType.CENTER }),
          dataCell("Knowledge Retrieval (BM25+Vector+RRF)", 1560, { fill: LIGHT_BRAND_BG, align: AlignmentType.CENTER }),
          dataCell("Response Generator (GPT-4o)", 1560, { fill: LIGHT_BRAND_BG, align: AlignmentType.CENTER }),
          dataCell("Critic Supervisor (fail-closed)", 1560, { fill: LIGHT_BRAND_BG, align: AlignmentType.CENTER }),
          dataCell("Escalation Handler", 1560, { fill: LIGHT_BRAND_BG, align: AlignmentType.CENTER }),
          dataCell("Analytics Collector", 1560, { fill: LIGHT_BRAND_BG, align: AlignmentType.CENTER }),
        ],
      }),
    ],
  }),
  spacer(40),
  // Layer 4: Data
  new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [1872, 1872, 1872, 1872, 1872],
    rows: [
      new TableRow({
        children: [headerCell("DATA & SERVICES LAYER", 9360, { fill: "2D6A4F", align: AlignmentType.CENTER })].concat(
          [1872, 1872, 1872, 1872].map(w => headerCell("", w, { fill: "2D6A4F" }))
        ),
      }),
      new TableRow({
        children: [
          dataCell("Azure Cosmos DB (20 collections, Vector Search)", 1872, { fill: "E8F5E9", align: AlignmentType.CENTER }),
          dataCell("Azure OpenAI (GPT-4o, GPT-4o-mini, Embeddings)", 1872, { fill: "E8F5E9", align: AlignmentType.CENTER }),
          dataCell("NATS Messaging (tenant isolation)", 1872, { fill: "E8F5E9", align: AlignmentType.CENTER }),
          dataCell("Redis Cache (cross-replica invalidation)", 1872, { fill: "E8F5E9", align: AlignmentType.CENTER }),
          dataCell("Azure Key Vault (per-tenant secrets)", 1872, { fill: "E8F5E9", align: AlignmentType.CENTER }),
        ],
      }),
    ],
  }),
  spacer(40),
  // Layer 5: Infrastructure
  new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [3120, 3120, 3120],
    rows: [
      new TableRow({
        children: [headerCell("INFRASTRUCTURE (Microsoft Azure)", 9360, { fill: "555555", align: AlignmentType.CENTER })].concat(
          [3120, 3120].map(w => headerCell("", w, { fill: "555555" }))
        ),
      }),
      new TableRow({
        children: [
          dataCell("Azure Container Apps (auto-scaling, zero to N)", 3120, { fill: LIGHT_BG, align: AlignmentType.CENTER }),
          dataCell("Azure Container Registry", 3120, { fill: LIGHT_BG, align: AlignmentType.CENTER }),
          dataCell("OpenTelemetry Observability", 3120, { fill: LIGHT_BG, align: AlignmentType.CENTER }),
        ],
      }),
    ],
  }),
  spacer(160),
  // Key design decisions
  new Paragraph({
    spacing: { after: 80 },
    children: [new TextRun({ text: "Key Design Decisions", font: "Arial", size: 22, bold: true, color: BLACK })],
  }),
  new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [2800, 6560],
    rows: [
      new TableRow({ children: [headerCell("Decision", 2800), headerCell("Detail", 6560)] }),
      new TableRow({ children: [
        dataCell("Multi-tenant isolation", 2800, { bold: true }),
        dataCell("Every layer enforces tenant boundaries: database partitioning, NATS topic namespacing, API key scoping, rate limiting per tenant", 6560),
      ]}),
      new TableRow({ children: [
        dataCell("Fail-closed Critic", 2800, { bold: true, fill: LIGHT_BG }),
        dataCell("Every AI response is validated by the Critic Supervisor before delivery. If the Critic is unavailable, responses are blocked (fail-closed), not passed through", 6560, { fill: LIGHT_BG }),
      ]}),
      new TableRow({ children: [
        dataCell("AGNTCY open-source SDK", 2800, { bold: true }),
        dataCell("Agent-to-Agent (A2A) and Model Context Protocol (MCP) for inter-agent communication. Transport via SLIM/NATS with in-process fallback", 6560),
      ]}),
    ],
  }),
  new Paragraph({ children: [new PageBreak()] }),
];

// ═══════════════════════════════════════════════════════════════
// PAGE 3: Persistent Memory + Testing & CI/CD
// ═══════════════════════════════════════════════════════════════

const page3 = [
  sectionTitle("Persistent Customer Memory"),
  smallText("Agent Red\u2019s primary technical differentiator \u2014 no competitor offers per-customer vector RAG over historical transcripts", { italics: true }),
  spacer(60),
  // 4-layer memory diagram
  new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [1200, 2400, 5760],
    rows: [
      new TableRow({ children: [headerCell("Layer", 1200, { align: AlignmentType.CENTER }), headerCell("Name", 2400), headerCell("Description", 5760)] }),
      new TableRow({ children: [
        dataCell("L1", 1200, { align: AlignmentType.CENTER, fill: "E3F2FD", bold: true }),
        dataCell("Customer Profile", 2400, { fill: "E3F2FD", bold: true }),
        dataCell([
          new TextRun({ text: "All tiers", font: "Arial", size: 18, bold: true, color: "1565C0" }),
          new TextRun({ text: " \u2014 Structured context (name, email, order history, preferences) injected into every AI interaction", font: "Arial", size: 18 }),
        ], 5760, { fill: "E3F2FD" }),
      ]}),
      new TableRow({ children: [
        dataCell("L2", 1200, { align: AlignmentType.CENTER, fill: "E8F5E9", bold: true }),
        dataCell("Conversation Memory", 2400, { fill: "E8F5E9", bold: true }),
        dataCell([
          new TextRun({ text: "All tiers", font: "Arial", size: 18, bold: true, color: "2E7D32" }),
          new TextRun({ text: " \u2014 Vectorized transcripts with semantic search via Cosmos DB DiskANN. AI recalls past conversations automatically.", font: "Arial", size: 18 }),
        ], 5760, { fill: "E8F5E9" }),
      ]}),
      new TableRow({ children: [
        dataCell("L3", 1200, { align: AlignmentType.CENTER, fill: "FFF3E0", bold: true }),
        dataCell("Cross-Session Learning", 2400, { fill: "FFF3E0", bold: true }),
        dataCell([
          new TextRun({ text: "Professional+", font: "Arial", size: 18, bold: true, color: "E65100" }),
          new TextRun({ text: " \u2014 Extracted patterns, preferences, and communication style. Pattern decay ensures relevance over time.", font: "Arial", size: 18 }),
        ], 5760, { fill: "FFF3E0" }),
      ]}),
      new TableRow({ children: [
        dataCell("L4", 1200, { align: AlignmentType.CENTER, fill: "FCE4EC", bold: true }),
        dataCell("Dedicated Model Training", 2400, { fill: "FCE4EC", bold: true }),
        dataCell([
          new TextRun({ text: "Enterprise add-on ($299/mo)", font: "Arial", size: 18, bold: true, color: "C62828" }),
          new TextRun({ text: " \u2014 Per-customer AI fine-tuning with quality gates and A/B validation.", font: "Arial", size: 18 }),
        ], 5760, { fill: "FCE4EC" }),
      ]}),
    ],
  }),
  spacer(40),
  smallText("Marginal cost: ~$0.01/customer/month for Layers 1\u20132. No competitor has confirmed implementing per-customer vector RAG over historical transcripts.", { italics: true }),
  spacer(200),
  // Testing & CI/CD
  sectionTitle("Testing & CI/CD"),
  spacer(60),
  // CI/CD pipeline diagram
  new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [1872, 1872, 1872, 1872, 1872],
    rows: [
      new TableRow({ children: [headerCell("END-TO-END DEVELOPMENT PIPELINE", 9360, { fill: "37474F", align: AlignmentType.CENTER })].concat(
        [1872, 1872, 1872, 1872].map(w => headerCell("", w, { fill: "37474F" }))
      )}),
      new TableRow({ children: [
        dataCell([
          new TextRun({ text: "1 ", font: "Arial", size: 24, bold: true, color: BRAND }),
          new TextRun({ text: "GitHub Actions", font: "Arial", size: 17, bold: true }),
          new TextRun({ text: "\nPR validation, unit tests, linting", font: "Arial", size: 15, color: MID_GRAY }),
        ], 1872, { fill: LIGHT_BG, align: AlignmentType.CENTER }),
        dataCell([
          new TextRun({ text: "2 ", font: "Arial", size: 24, bold: true, color: BRAND }),
          new TextRun({ text: "Staging Deploy", font: "Arial", size: 17, bold: true }),
          new TextRun({ text: "\nAzure Container Apps", font: "Arial", size: 15, color: MID_GRAY }),
        ], 1872, { fill: LIGHT_BG, align: AlignmentType.CENTER }),
        dataCell([
          new TextRun({ text: "3 ", font: "Arial", size: 24, bold: true, color: BRAND }),
          new TextRun({ text: "Smoke Tests", font: "Arial", size: 17, bold: true }),
          new TextRun({ text: "\nWidget health, config, SSE", font: "Arial", size: 15, color: MID_GRAY }),
        ], 1872, { fill: LIGHT_BG, align: AlignmentType.CENTER }),
        dataCell([
          new TextRun({ text: "4 ", font: "Arial", size: 24, bold: true, color: BRAND }),
          new TextRun({ text: "Loyal Opposition", font: "Arial", size: 17, bold: true }),
          new TextRun({ text: "\nIndependent AI review (GO/NO-GO)", font: "Arial", size: 15, color: MID_GRAY }),
        ], 1872, { fill: LIGHT_BG, align: AlignmentType.CENTER }),
        dataCell([
          new TextRun({ text: "5 ", font: "Arial", size: 24, bold: true, color: BRAND }),
          new TextRun({ text: "Production", font: "Arial", size: 17, bold: true }),
          new TextRun({ text: "\nApproval-gated deploy", font: "Arial", size: 15, color: MID_GRAY }),
        ], 1872, { fill: LIGHT_BG, align: AlignmentType.CENTER }),
      ]}),
    ],
  }),
  spacer(100),
  // Test metrics
  new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [2340, 2340, 2340, 2340],
    rows: [
      new TableRow({ children: [
        headerCell("Offline Tests", 2340, { align: AlignmentType.CENTER }),
        headerCell("Live E2E Tests", 2340, { align: AlignmentType.CENTER }),
        headerCell("Mock E2E Tests", 2340, { align: AlignmentType.CENTER }),
        headerCell("Assertion Runs", 2340, { align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        brandCell("6,053", 2340, { align: AlignmentType.CENTER }),
        brandCell("936", 2340, { align: AlignmentType.CENTER }),
        brandCell("527", 2340, { align: AlignmentType.CENTER }),
        brandCell("121,658", 2340, { align: AlignmentType.CENTER }),
      ]}),
    ],
  }),
  spacer(80),
  bodyText(
    "Development follows a specification-first methodology (GOV-01): every feature begins as a formal specification in the Knowledge Database, " +
    "generates work items and tests, then proceeds through implementation with append-only change control. " +
    "A Loyal Opposition (independent AI reviewer) evaluates every implementation before production promotion, issuing GO/NO-GO verdicts with evidence-based findings."
  ),
  new Paragraph({ children: [new PageBreak()] }),
];

// ═══════════════════════════════════════════════════════════════
// PAGE 4: Competitor Comparison
// ═══════════════════════════════════════════════════════════════

const page4 = [
  sectionTitle("Competitive Positioning"),
  smallText("Feature and cost comparison against leading customer engagement platforms", { italics: true }),
  spacer(80),
  // Feature matrix
  new Paragraph({
    spacing: { after: 80 },
    children: [new TextRun({ text: "Feature Comparison", font: "Arial", size: 22, bold: true, color: BLACK })],
  }),
  new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [1800, 1890, 1890, 1890, 1890],
    rows: [
      new TableRow({ children: [
        headerCell("Capability", 1800),
        headerCell("Agent Red", 1890, { fill: BRAND }),
        headerCell("Intercom", 1890),
        headerCell("Zendesk", 1890),
        headerCell("Tidio", 1890),
      ]}),
      ...([
        ["AI Pipeline Agents", "6 specialized", "1 (Fin)", "1", "1 (Lyro)"],
        ["Persistent Memory", "4 layers (vector RAG)", "Recent history", "Current ticket", "None"],
        ["Safety Validation", "Fail-closed Critic", "Content filter", "None", "None"],
        ["KB Search Method", "Hybrid BM25+Vector+RRF", "Fin AI search", "Help center", "FAQ keyword"],
        ["Widget Size (gzip)", "~17KB", "~80\u2013100KB", "~60KB", "~40\u201360KB"],
        ["Shopify Native", "Theme App Extension", "External script", "External script", "Theme block"],
        ["Response Latency P50", "1,500ms target", "7,000ms published", "Unknown", "Unknown"],
        ["White-Label", "Full (Enterprise)", "Limited", "No", "No"],
        ["A/B Testing", "Built-in", "No", "Highest tier only", "No"],
        ["GDPR Compliance", "Built-in (scrub/export/delete)", "Add-on", "Add-on", "Basic"],
      ].map((row, i) => new TableRow({
        children: [
          dataCell(row[0], 1800, { bold: true, fill: i % 2 ? LIGHT_BG : undefined }),
          dataCell(row[1], 1890, { fill: i % 2 ? LIGHT_BRAND_BG : "FFF8F6", bold: true, color: BRAND_DARK }),
          dataCell(row[2], 1890, { fill: i % 2 ? LIGHT_BG : undefined }),
          dataCell(row[3], 1890, { fill: i % 2 ? LIGHT_BG : undefined }),
          dataCell(row[4], 1890, { fill: i % 2 ? LIGHT_BG : undefined }),
        ],
      }))),
    ],
  }),
  spacer(160),
  // Cost comparison
  new Paragraph({
    spacing: { after: 80 },
    children: [new TextRun({ text: "Cost Comparison at 1,000 Conversations/Month", font: "Arial", size: 22, bold: true, color: BLACK })],
  }),
  new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [2340, 2340, 2340, 2340],
    rows: [
      new TableRow({ children: [
        headerCell("Agent Red", 2340, { fill: BRAND, align: AlignmentType.CENTER }),
        headerCell("Intercom", 2340, { align: AlignmentType.CENTER }),
        headerCell("Zendesk", 2340, { align: AlignmentType.CENTER }),
        headerCell("Tidio", 2340, { align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        brandCell("$149/mo", 2340, { align: AlignmentType.CENTER }),
        dataCell("$1,090/mo", 2340, { align: AlignmentType.CENTER }),
        dataCell("$963/mo", 2340, { align: AlignmentType.CENTER }),
        dataCell("$290/mo", 2340, { align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        dataCell("Baseline", 2340, { align: AlignmentType.CENTER, fill: LIGHT_BRAND_BG, bold: true }),
        dataCell("7.3x more expensive", 2340, { align: AlignmentType.CENTER, fill: LIGHT_BG, color: "C62828" }),
        dataCell("6.5x more expensive", 2340, { align: AlignmentType.CENTER, fill: LIGHT_BG, color: "C62828" }),
        dataCell("1.9x more expensive", 2340, { align: AlignmentType.CENTER, fill: LIGHT_BG, color: "E65100" }),
      ]}),
    ],
  }),
  spacer(100),
  bodyText(
    "Tiered pricing: Starter ($149/mo, 1,000 conversations), Professional ($399/mo, 5,000), Enterprise ($999/mo, 20,000). " +
    "Prepaid conversation packs available at further discount. Gross margin: 76\u201390% across all scenarios. " +
    "At 5,000 conversations/month, Agent Red Professional costs $399 versus $1,450\u2013$5,051 for competitors."
  ),
  new Paragraph({ children: [new PageBreak()] }),
];

// ═══════════════════════════════════════════════════════════════
// PAGE 5: Maturity & Readiness
// ═══════════════════════════════════════════════════════════════

const page5 = [
  sectionTitle("Maturity & Readiness Assessment"),
  smallText("Honest assessment of platform maturity across key dimensions", { italics: true }),
  spacer(80),
  // Maturity scorecard
  new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [1800, 1200, 6360],
    rows: [
      new TableRow({ children: [headerCell("Dimension", 1800), headerCell("Rating", 1200, { align: AlignmentType.CENTER }), headerCell("Evidence", 6360)] }),
      ...([
        ["Architecture", "Advanced", "89 modules, 20 Cosmos collections, 6-agent pipeline, multi-tenant isolation at every layer, fail-closed safety"],
        ["Testing", "Advanced", "11,055 tests, 121K+ assertion runs, specification-first methodology, independent Loyal Opposition review"],
        ["CI/CD", "Established", "GitHub Actions + Azure DevOps, staging/production separation, approval-gated deploys, automated smoke tests"],
        ["Security", "Established", "Zero-knowledge architecture (planned), Azure Key Vault encryption, GDPR compliance (scrub/export/delete), fail-closed Critic, rate limiting"],
        ["Documentation", "Advanced", "2,092 specifications, 235 documents, 17 operational procedures, Docusaurus documentation site"],
        ["Production Ops", "Early", "Beta deployment on Azure Container Apps, 1 tenant provisioned, deploy procedures implemented, staging verified"],
        ["Ecosystem", "Early", "Shopify native integration, Stripe billing, 18-spec integration framework with Zendesk, Slack, and Google Docs adapters"],
      ].map((row, i) => {
        const ratingColor = row[1] === "Advanced" ? "2E7D32" : row[1] === "Established" ? "1565C0" : "E65100";
        const ratingBg = row[1] === "Advanced" ? "E8F5E9" : row[1] === "Established" ? "E3F2FD" : "FFF3E0";
        return new TableRow({ children: [
          dataCell(row[0], 1800, { bold: true, fill: i % 2 ? LIGHT_BG : undefined }),
          new TableCell({
            borders,
            width: { size: 1200, type: WidthType.DXA },
            shading: { fill: ratingBg, type: ShadingType.CLEAR },
            margins: cellMargins,
            verticalAlign: VerticalAlign.CENTER,
            children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
              new TextRun({ text: row[1], bold: true, font: "Arial", size: 18, color: ratingColor }),
            ]})],
          }),
          dataCell(row[2], 6360, { fill: i % 2 ? LIGHT_BG : undefined }),
        ]});
      })),
    ],
  }),
  spacer(160),
  // Current status
  new Paragraph({
    spacing: { after: 80 },
    children: [new TextRun({ text: "Current Status", font: "Arial", size: 22, bold: true, color: BLACK })],
  }),
  bodyText(
    "Agent Red is in late beta. Production infrastructure is deployed on Microsoft Azure with all core features implemented and tested. " +
    "The platform is progressing through final production-readiness gates including deploy pipeline hardening, independent review cycles, " +
    "and operational procedure verification. Architecture, testing, and documentation maturity are significantly ahead of typical beta-stage products."
  ),
  spacer(120),
  // Roadmap
  new Paragraph({
    spacing: { after: 80 },
    children: [new TextRun({ text: "Roadmap Highlights", font: "Arial", size: 22, bold: true, color: BLACK })],
  }),
  new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [2340, 2340, 2340, 2340],
    rows: [
      new TableRow({ children: [
        headerCell("Zero-Knowledge Architecture", 2340, { fill: BRAND, align: AlignmentType.CENTER }),
        headerCell("WhatsApp Channel", 2340, { align: AlignmentType.CENTER }),
        headerCell("Enhanced A/B Testing", 2340, { align: AlignmentType.CENTER }),
        headerCell("Marketplace Integrations", 2340, { align: AlignmentType.CENTER }),
      ]}),
      new TableRow({ children: [
        dataCell("Operator cannot read tenant data. Envelope encryption with per-tenant DEKs. 31 work items planned.", 2340, { fill: LIGHT_BRAND_BG }),
        dataCell("WhatsApp Business escalation channel. Deep-link from chat to WhatsApp via merchant client ID.", 2340, { fill: LIGHT_BG }),
        dataCell("Statistical significance testing, SHA-256 assignment, experiment management UI.", 2340, { fill: LIGHT_BG }),
        dataCell("Expanded vendor adapters beyond Zendesk, Slack, and Google Docs.", 2340, { fill: LIGHT_BG }),
      ]}),
    ],
  }),
  spacer(200),
  // Contact
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 100 },
    border: { top: { style: BorderStyle.SINGLE, size: 2, color: BORDER_COLOR, space: 8 } },
    children: [
      new TextRun({ text: "Remaker Digital", font: "Arial", size: 20, bold: true, color: BLACK }),
      new TextRun({ text: "  |  ", font: "Arial", size: 20, color: MID_GRAY }),
      new TextRun({ text: "remakerdigital.com", font: "Arial", size: 20, color: BRAND }),
      new TextRun({ text: "  |  ", font: "Arial", size: 20, color: MID_GRAY }),
      new TextRun({ text: "info@remakerdigital.com", font: "Arial", size: 20, color: BRAND }),
    ],
  }),
];

// ═══════════════════════════════════════════════════════════════
// BUILD DOCUMENT
// ═══════════════════════════════════════════════════════════════

const doc = new Document({
  creator: "Remaker Digital",
  title: "Agent Red Customer Experience \u2014 Executive Summary",
  description: "Executive summary for technical evaluation of Agent Red AI customer engagement platform",
  styles: {
    default: {
      document: { run: { font: "Arial", size: 20 } },
    },
  },
  sections: [
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1200, right: 1200, bottom: 1400, left: 1200 },
        },
      },
      footers: { default: makeFooter() },
      children: [...page1, ...page2, ...page3, ...page4, ...page5],
    },
  ],
});

Packer.toBuffer(doc).then((buffer) => {
  // Per S307: write to docs/ alongside this script, derived from __dirname.
  const outPath = path.resolve(__dirname, "Agent-Red-Executive-Summary.docx");
  fs.writeFileSync(outPath, buffer);
  console.log("DOCX written to:", outPath);
  console.log("Size:", (buffer.length / 1024).toFixed(1), "KB");
});
