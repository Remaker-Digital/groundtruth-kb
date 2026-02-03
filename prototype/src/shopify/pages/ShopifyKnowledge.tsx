// (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React, { useState, useMemo, useCallback } from 'react';
import {
  Page,
  LegacyCard,
  DataTable,
  Modal,
  TextField,
  Select,
  Badge,
  Button,
  Banner,
  Text,
  Box,
  InlineStack,
  BlockStack,
} from '@shopify/polaris';
import { KNOWLEDGE_ARTICLES } from '../../data/mockData';
import type { KnowledgeArticle } from '../../data/mockData';

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const CATEGORIES = ['All', 'Policies', 'Shipping', 'Products', 'Sales', 'Services'];

const CATEGORY_OPTIONS = CATEGORIES.filter((c) => c !== 'All').map((c) => ({
  label: c,
  value: c,
}));

const STATUS_OPTIONS = [
  { label: 'Published', value: 'published' },
  { label: 'Draft', value: 'draft' },
  { label: 'Archived', value: 'archived' },
];

const CATEGORY_BADGE_TONE: Record<string, 'info' | 'success' | 'warning' | 'critical' | undefined> = {
  Policies: 'info',
  Shipping: undefined,
  Products: 'success',
  Sales: 'warning',
  Services: undefined,
};

const STATUS_BADGE_TONE: Record<string, 'success' | 'attention' | undefined> = {
  published: 'success',
  draft: 'attention',
  archived: undefined,
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

interface ArticleFormState {
  title: string;
  category: string;
  content: string;
  status: string;
}

const emptyForm: ArticleFormState = {
  title: '',
  category: 'Policies',
  content: '',
  status: 'draft',
};

// ---------------------------------------------------------------------------
// Main Component
// ---------------------------------------------------------------------------

export function ShopifyKnowledge() {
  const [articles, setArticles] = useState<KnowledgeArticle[]>(KNOWLEDGE_ARTICLES);
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [modalOpen, setModalOpen] = useState(false);
  const [editingArticle, setEditingArticle] = useState<KnowledgeArticle | null>(null);
  const [form, setForm] = useState<ArticleFormState>(emptyForm);

  // Filtered articles
  const filteredArticles = useMemo(() => {
    return articles.filter((article) => {
      const matchesCategory = categoryFilter === 'All' || article.category === categoryFilter;
      const matchesStatus = statusFilter === 'All' || article.status === statusFilter.toLowerCase();
      return matchesCategory && matchesStatus;
    });
  }, [articles, categoryFilter, statusFilter]);

  // Summary stats
  const stats = useMemo(() => {
    const published = articles.filter((a) => a.status === 'published');
    const avgUsage =
      published.length > 0
        ? Math.round(published.reduce((sum, a) => sum + a.usageCount, 0) / published.length)
        : 0;
    return {
      total: articles.length,
      published: published.length,
      avgUsage,
    };
  }, [articles]);

  // Handlers
  const handleAddArticle = useCallback(() => {
    setEditingArticle(null);
    setForm(emptyForm);
    setModalOpen(true);
  }, []);

  const handleEditArticle = useCallback((article: KnowledgeArticle) => {
    setEditingArticle(article);
    setForm({
      title: article.title,
      category: article.category,
      content: article.content,
      status: article.status,
    });
    setModalOpen(true);
  }, []);

  const handleArchiveArticle = useCallback((articleId: string) => {
    setArticles((prev) =>
      prev.map((a) => (a.id === articleId ? { ...a, status: 'archived' as const } : a))
    );
  }, []);

  const handleSave = useCallback(() => {
    if (editingArticle) {
      setArticles((prev) =>
        prev.map((a) =>
          a.id === editingArticle.id
            ? {
                ...a,
                title: form.title,
                category: form.category,
                content: form.content,
                status: form.status as KnowledgeArticle['status'],
                lastUpdated: new Date().toISOString().split('T')[0],
              }
            : a
        )
      );
    } else {
      const newArticle: KnowledgeArticle = {
        id: `kb-${String(articles.length + 1).padStart(3, '0')}`,
        title: form.title,
        category: form.category,
        content: form.content,
        status: form.status as KnowledgeArticle['status'],
        lastUpdated: new Date().toISOString().split('T')[0],
        author: 'Admin',
        usageCount: 0,
        helpfulRate: 0,
      };
      setArticles((prev) => [...prev, newArticle]);
    }
    setModalOpen(false);
  }, [editingArticle, form, articles.length]);

  const handleCloseModal = useCallback(() => {
    setModalOpen(false);
  }, []);

  // Build DataTable rows
  const rows = filteredArticles.map((article) => [
    // Title (clickable)
    <Button key={`title-${article.id}`} variant="plain" onClick={() => handleEditArticle(article)}>
      {article.title}
    </Button>,
    // Category
    <Badge key={`cat-${article.id}`} tone={CATEGORY_BADGE_TONE[article.category]}>
      {article.category}
    </Badge>,
    // Status
    <Badge
      key={`status-${article.id}`}
      tone={STATUS_BADGE_TONE[article.status]}
    >
      {article.status.charAt(0).toUpperCase() + article.status.slice(1)}
    </Badge>,
    // Last Updated
    article.lastUpdated,
    // Usage Count
    article.usageCount.toLocaleString(),
    // Helpful Rate
    article.helpfulRate > 0 ? `${article.helpfulRate}%` : '--',
    // Actions
    <InlineStack key={`actions-${article.id}`} gap="200">
      <Button size="slim" onClick={() => handleEditArticle(article)}>Edit</Button>
      {article.status !== 'archived' && (
        <Button size="slim" variant="secondary" onClick={() => handleArchiveArticle(article.id)}>Archive</Button>
      )}
    </InlineStack>,
  ]);

  // Filter tabs using Polaris Tabs pattern via Select dropdowns in a toolbar
  const categorySelectOptions = CATEGORIES.map((c) => ({ label: c, value: c }));
  const statusSelectOptions = [
    { label: 'All', value: 'All' },
    { label: 'Published', value: 'published' },
    { label: 'Draft', value: 'draft' },
    { label: 'Archived', value: 'archived' },
  ];

  return (
    <Page
      title="Knowledge Base"
      primaryAction={{ content: 'Add Article', onAction: handleAddArticle }}
    >
      <BlockStack gap="400">
        {/* Summary banner */}
        <Banner tone="info">
          <Text as="span" variant="bodyMd">
            {stats.total} articles total, {stats.published} published, {stats.avgUsage.toLocaleString()} avg monthly usage
          </Text>
        </Banner>

        {/* Filter bar */}
        <LegacyCard sectioned>
          <InlineStack gap="400" blockAlign="center" wrap>
            <div style={{ minWidth: 160 }}>
              <Select
                label="Category"
                labelInline
                options={categorySelectOptions}
                value={categoryFilter}
                onChange={setCategoryFilter}
              />
            </div>
            <div style={{ minWidth: 160 }}>
              <Select
                label="Status"
                labelInline
                options={statusSelectOptions}
                value={statusFilter}
                onChange={setStatusFilter}
              />
            </div>
            <Text as="span" variant="bodySm" tone="subdued">
              Showing {filteredArticles.length} of {articles.length} articles
            </Text>
          </InlineStack>
        </LegacyCard>

        {/* Data table */}
        <LegacyCard>
          <DataTable
            columnContentTypes={['text', 'text', 'text', 'text', 'numeric', 'text', 'text']}
            headings={['Title', 'Category', 'Status', 'Last Updated', 'Usage Count', 'Helpful Rate', 'Actions']}
            rows={rows}
            sortable={[true, false, false, true, true, true, false]}
            defaultSortDirection="descending"
            initialSortColumnIndex={4}
            footerContent={
              filteredArticles.length === 0
                ? 'No articles match your filters.'
                : `${filteredArticles.length} article${filteredArticles.length !== 1 ? 's' : ''}`
            }
          />
        </LegacyCard>
      </BlockStack>

      {/* Add / Edit Modal */}
      <Modal
        open={modalOpen}
        onClose={handleCloseModal}
        title={editingArticle ? 'Edit Article' : 'Add Article'}
        primaryAction={{
          content: 'Save',
          onAction: handleSave,
          disabled: !form.title.trim() || !form.content.trim(),
        }}
        secondaryActions={[
          {
            content: 'Cancel',
            onAction: handleCloseModal,
          },
        ]}
      >
        <Modal.Section>
          <BlockStack gap="400">
            <TextField
              label="Title"
              placeholder="Article title"
              value={form.title}
              onChange={(value) => setForm((f) => ({ ...f, title: value }))}
              autoComplete="off"
            />
            <Select
              label="Category"
              options={CATEGORY_OPTIONS}
              value={form.category}
              onChange={(value) => setForm((f) => ({ ...f, category: value }))}
            />
            <div>
              <TextField
                label="Content"
                placeholder="Write the article content here... (Production will use Tiptap rich text editor)"
                value={form.content}
                onChange={(value) => setForm((f) => ({ ...f, content: value }))}
                multiline={8}
                autoComplete="off"
              />
              <Box paddingBlockStart="100">
                <Text as="p" variant="bodySm" tone="subdued">
                  Prototype uses plain text. Production will use a rich text editor with formatting, images, and tables.
                </Text>
              </Box>
            </div>
            <Select
              label="Status"
              options={STATUS_OPTIONS}
              value={form.status}
              onChange={(value) => setForm((f) => ({ ...f, status: value }))}
            />
          </BlockStack>
        </Modal.Section>
      </Modal>
    </Page>
  );
}
