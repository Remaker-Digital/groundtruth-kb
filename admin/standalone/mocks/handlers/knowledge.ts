// @ts-nocheck
/**
 * Mock handlers — Knowledge Base endpoints.
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { GET, POST, PUT, DELETE } from '../router';
import { getStore } from '../store';
import type { MockRequest, MockResponse } from '../router';

export function registerKnowledgeHandlers(): void {
  const s = () => getStore().knowledge;

  GET('/api/admin/knowledge', (_req: MockRequest): MockResponse => {
    const articles = s().articles;
    return { status: 200, body: { articles, total: articles.length } };
  });

  // Templates (used by OnboardingWizard) — MUST be before /:id to avoid being caught by parameterized route
  GET('/api/admin/knowledge/templates', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { templates: [] } };
  });

  POST('/api/admin/knowledge/templates/:id/apply', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { articlesCreated: 0, articlesFailed: 0, totalChars: 0 } };
  });

  // Staleness — MUST be before /:id
  GET('/api/admin/knowledge/staleness', (_req: MockRequest): MockResponse => {
    return { status: 200, body: s().staleness };
  });

  GET('/api/admin/knowledge/stale', (_req: MockRequest): MockResponse => {
    const stale = s().articles.filter((a: Record<string, unknown>) => a.stalenessCategory === 'aging' || a.stalenessCategory === 'stale');
    return { status: 200, body: { entries: stale, total: stale.length } };
  });

  // Export — MUST be before /:id
  GET('/api/admin/knowledge/export', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { csv: "id,title,category,status", filename: "knowledge-export.csv" } };
  });

  // Suggestions (used by OnboardingWizard) — MUST be before /:id
  GET('/api/admin/knowledge/suggestions', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { suggestions: [] } };
  });

  // Knowledge Score (SPEC-1873) — MUST be before /:id
  GET('/api/admin/knowledge/score', (_req: MockRequest): MockResponse => {
    return {
      status: 200,
      body: {
        score: 74.2,
        factors: {
          coverage: 0.82,
          relevance: 0.71,
          escalationRate: 0.12,
          freshness: 0.65,
        },
        totalConversations: 342,
        unansweredCount: 28,
        kbEntryCount: 156,
        freshEntryCount: 101,
        trend: {
          direction: 'up',
          delta: 3.1,
          previous: 71.1,
        },
      },
    };
  });

  // Gap Review (SPEC-1873) — MUST be before /:id
  GET('/api/admin/knowledge/gaps/review', (_req: MockRequest): MockResponse => {
    return {
      status: 200,
      body: {
        tenantId: 'demo-tenant-001',
        since: '2026-03-01T00:00:00Z',
        until: '2026-03-31T00:00:00Z',
        totalGaps: 28,
        clusters: [
          {
            intent: 'return_policy',
            sampleQuestion: 'What is your return policy for opened items?',
            frequency: 8,
            lastOccurrence: '2026-03-30T14:22:00Z',
            suggestedAction: 'Add KB article covering opened-item return conditions',
            priorityScore: 0.85,
            conversationIds: ['conv-001', 'conv-003', 'conv-009', 'conv-015', 'conv-022', 'conv-028', 'conv-031', 'conv-044'],
          },
          {
            intent: 'shipping_international',
            sampleQuestion: 'Do you ship to Canada? How long does it take?',
            frequency: 5,
            lastOccurrence: '2026-03-29T09:15:00Z',
            suggestedAction: 'Create international shipping FAQ with country-specific timelines',
            priorityScore: 0.72,
            conversationIds: ['conv-007', 'conv-012', 'conv-019', 'conv-033', 'conv-041'],
          },
          {
            intent: 'warranty_claim',
            sampleQuestion: 'How do I file a warranty claim for a defective product?',
            frequency: 3,
            lastOccurrence: '2026-03-28T16:45:00Z',
            suggestedAction: 'Add warranty claim process documentation',
            priorityScore: 0.58,
            conversationIds: ['conv-005', 'conv-018', 'conv-037'],
          },
          {
            intent: 'bulk_discount',
            sampleQuestion: 'Are there discounts for bulk orders over 50 units?',
            frequency: 2,
            lastOccurrence: '2026-03-25T11:30:00Z',
            suggestedAction: 'Document bulk pricing tiers and contact process',
            priorityScore: 0.35,
            conversationIds: ['conv-014', 'conv-039'],
          },
        ],
      },
    };
  });

  GET('/api/admin/knowledge/:id', (req: MockRequest): MockResponse => {
    const article = s().articles.find((a: Record<string, unknown>) => a.id === req.params.id);
    if (!article) return { status: 404, body: { detail: 'Article not found' } };
    return { status: 200, body: article };
  });

  POST('/api/admin/knowledge', (req: MockRequest): MockResponse => {
    const store = getStore();
    const id = 'kb-' + String(store.knowledge.articles.length + 1).padStart(3, '0');
    const article = {
      id, title: req.body?.title ?? 'New Article', content: req.body?.content ?? '',
      category: req.body?.category ?? 'general', status: 'draft',
      entryType: 'manual', is_active: true,
      createdAt: new Date().toISOString(), updatedAt: new Date().toISOString(),
    };
    store.knowledge.articles.push(article);
    return { status: 201, body: article };
  });

  PUT('/api/admin/knowledge/:id', (req: MockRequest): MockResponse => {
    const store = getStore();
    const idx = store.knowledge.articles.findIndex((a: Record<string, unknown>) => a.id === req.params.id);
    if (idx === -1) return { status: 404, body: { detail: 'Article not found' } };
    store.knowledge.articles[idx] = { ...store.knowledge.articles[idx], ...req.body, updatedAt: new Date().toISOString() };
    return { status: 200, body: store.knowledge.articles[idx] };
  });

  DELETE('/api/admin/knowledge/:id', (req: MockRequest): MockResponse => {
    const store = getStore();
    store.knowledge.articles = store.knowledge.articles.filter((a: Record<string, unknown>) => a.id !== req.params.id);
    return { status: 200, body: { success: true } };
  });

  // Upload (simplified — returns success with mock entry IDs)
  POST('/api/admin/knowledge/upload', (_req: MockRequest): MockResponse => {
    return {
      status: 200,
      body: {
        source_type: 'file', source_filename: 'uploaded-doc.pdf',
        entries_created: 3, total_chars: 4500,
        entry_ids: ['kb-upload-001', 'kb-upload-002', 'kb-upload-003'],
        parent_entry_id: 'kb-upload-001',
      },
    };
  });

  // Import from URL
  POST('/api/admin/knowledge/import-url', (req: MockRequest): MockResponse => {
    return {
      status: 200,
      body: {
        source_type: 'url', source_url: req.body?.url ?? 'https://example.com',
        entries_created: 2, total_chars: 3200,
        entry_ids: ['kb-url-001', 'kb-url-002'],
        parent_entry_id: 'kb-url-001',
      },
    };
  });

  POST('/api/admin/knowledge/:id/verify', (req: MockRequest): MockResponse => {
    const store = getStore();
    const article = store.knowledge.articles.find((a: Record<string, unknown>) => a.id === req.params.id);
    if (article) {
      (article as Record<string, unknown>).lastVerifiedAt = new Date().toISOString();
      (article as Record<string, unknown>).stalenessCategory = 'fresh';
      (article as Record<string, unknown>).stalenessScore = 0;
    }
    return { status: 200, body: { success: true } };
  });

  // Conflict scan
  POST('/api/admin/knowledge/scan', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { conflicts: [], total: 0 } };
  });

  // Ingestion (used by OnboardingWizard)
  POST('/api/admin/knowledge/ingest', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { job_id: 'mock-job-001', status: 'completed' } };
  });

  GET('/api/admin/knowledge/ingest/status', (_req: MockRequest): MockResponse => {
    return { status: 200, body: { job_id: 'mock-job-001', status: 'completed', progress: 100 } };
  });

}
