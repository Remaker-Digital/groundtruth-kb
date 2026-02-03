// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React, { useState, useMemo } from 'react';
import {
  Paper,
  Table,
  TextInput,
  Select,
  Modal,
  Textarea,
  Button,
  Badge,
  Progress,
  Group,
  Stack,
  Title,
  Text,
  ActionIcon,
  SimpleGrid,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { KNOWLEDGE_ARTICLES, KnowledgeArticle } from '../../data/mockData';

const BRAND_RED = '#C41E2A';

const CATEGORIES = ['All', 'Policies', 'Shipping', 'Products', 'Sales', 'Services'];
const STATUSES = ['All', 'Published', 'Draft', 'Archived'];

const statusColorMap: Record<string, string> = {
  published: 'green',
  draft: 'yellow',
  archived: 'gray',
};

const categoryColorMap: Record<string, string> = {
  Policies: 'blue',
  Shipping: 'violet',
  Products: 'teal',
  Sales: 'orange',
  Services: 'pink',
};

// Icons as inline SVGs
const EditIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
  </svg>
);

const ArchiveIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="21 8 21 21 3 21 3 8" />
    <rect x="1" y="3" width="22" height="5" />
    <line x1="10" y1="12" x2="14" y2="12" />
  </svg>
);

const PlusIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="5" x2="12" y2="19" />
    <line x1="5" y1="12" x2="19" y2="12" />
  </svg>
);

const SearchIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="11" cy="11" r="8" />
    <line x1="21" y1="21" x2="16.65" y2="16.65" />
  </svg>
);

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

export function KnowledgeBasePage() {
  const [articles, setArticles] = useState<KnowledgeArticle[]>(KNOWLEDGE_ARTICLES);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string | null>('All');
  const [statusFilter, setStatusFilter] = useState<string | null>('All');
  const [modalOpened, { open: openModal, close: closeModal }] = useDisclosure(false);
  const [editingArticle, setEditingArticle] = useState<KnowledgeArticle | null>(null);
  const [form, setForm] = useState<ArticleFormState>(emptyForm);

  // Filter articles
  const filteredArticles = useMemo(() => {
    return articles.filter((article) => {
      const matchesSearch =
        search === '' ||
        article.title.toLowerCase().includes(search.toLowerCase()) ||
        article.content.toLowerCase().includes(search.toLowerCase());
      const matchesCategory =
        !categoryFilter || categoryFilter === 'All' || article.category === categoryFilter;
      const matchesStatus =
        !statusFilter ||
        statusFilter === 'All' ||
        article.status === statusFilter.toLowerCase();
      return matchesSearch && matchesCategory && matchesStatus;
    });
  }, [articles, search, categoryFilter, statusFilter]);

  // Summary stats
  const stats = useMemo(() => {
    const published = articles.filter((a) => a.status === 'published');
    const drafts = articles.filter((a) => a.status === 'draft');
    const avgHelpful =
      published.length > 0
        ? Math.round(
            published.reduce((sum, a) => sum + a.helpfulRate, 0) / published.length
          )
        : 0;
    return {
      total: articles.length,
      published: published.length,
      draft: drafts.length,
      avgHelpful,
    };
  }, [articles]);

  const handleAddArticle = () => {
    setEditingArticle(null);
    setForm(emptyForm);
    openModal();
  };

  const handleEditArticle = (article: KnowledgeArticle) => {
    setEditingArticle(article);
    setForm({
      title: article.title,
      category: article.category,
      content: article.content,
      status: article.status,
    });
    openModal();
  };

  const handleArchiveArticle = (articleId: string) => {
    setArticles((prev) =>
      prev.map((a) => (a.id === articleId ? { ...a, status: 'archived' as const } : a))
    );
  };

  const handleSave = () => {
    if (editingArticle) {
      // Update existing
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
      // Create new
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
    closeModal();
  };

  return (
    <Stack gap="lg">
      {/* Page header */}
      <div>
        <Title order={2}>Knowledge Base</Title>
        <Text c="dimmed" size="sm">
          Manage articles your AI uses to answer customers
        </Text>
      </div>

      {/* Top bar: Search + Filters + Add button */}
      <Paper p="md" radius="md" withBorder>
        <Group justify="space-between" wrap="wrap" gap="sm">
          <Group gap="sm" wrap="wrap" style={{ flex: 1 }}>
            <TextInput
              placeholder="Search articles..."
              leftSection={<SearchIcon />}
              value={search}
              onChange={(e) => setSearch(e.currentTarget.value)}
              style={{ minWidth: 220, flex: 1, maxWidth: 360 }}
            />
            <Select
              placeholder="Category"
              data={CATEGORIES}
              value={categoryFilter}
              onChange={setCategoryFilter}
              clearable={false}
              w={160}
            />
            <Select
              placeholder="Status"
              data={STATUSES}
              value={statusFilter}
              onChange={setStatusFilter}
              clearable={false}
              w={140}
            />
          </Group>
          <Button
            leftSection={<PlusIcon />}
            color={BRAND_RED}
            onClick={handleAddArticle}
          >
            Add Article
          </Button>
        </Group>
      </Paper>

      {/* Summary stats */}
      <SimpleGrid cols={{ base: 2, sm: 4 }} spacing="md">
        <Paper p="md" radius="md" withBorder>
          <Text size="xs" c="dimmed" tt="uppercase" fw={600} mb={4}>
            Total Articles
          </Text>
          <Text size="xl" fw={700} lh={1}>
            {stats.total}
          </Text>
        </Paper>
        <Paper p="md" radius="md" withBorder>
          <Text size="xs" c="dimmed" tt="uppercase" fw={600} mb={4}>
            Published
          </Text>
          <Text size="xl" fw={700} lh={1} c="green">
            {stats.published}
          </Text>
        </Paper>
        <Paper p="md" radius="md" withBorder>
          <Text size="xs" c="dimmed" tt="uppercase" fw={600} mb={4}>
            Draft
          </Text>
          <Text size="xl" fw={700} lh={1} c="yellow.7">
            {stats.draft}
          </Text>
        </Paper>
        <Paper p="md" radius="md" withBorder>
          <Text size="xs" c="dimmed" tt="uppercase" fw={600} mb={4}>
            Avg Helpful Rate
          </Text>
          <Text size="xl" fw={700} lh={1}>
            {stats.avgHelpful}%
          </Text>
        </Paper>
      </SimpleGrid>

      {/* Articles table */}
      <Paper p="md" radius="md" withBorder>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Title</Table.Th>
              <Table.Th>Category</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Last Updated</Table.Th>
              <Table.Th style={{ textAlign: 'right' }}>Usage Count</Table.Th>
              <Table.Th style={{ minWidth: 160 }}>Helpful Rate</Table.Th>
              <Table.Th style={{ textAlign: 'right' }}>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {filteredArticles.map((article) => (
              <Table.Tr key={article.id}>
                <Table.Td>
                  <Text size="sm" fw={500}>
                    {article.title}
                  </Text>
                </Table.Td>
                <Table.Td>
                  <Badge
                    size="sm"
                    variant="light"
                    color={categoryColorMap[article.category] || 'gray'}
                  >
                    {article.category}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Badge
                    size="sm"
                    variant="light"
                    color={statusColorMap[article.status] || 'gray'}
                  >
                    {article.status}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Text size="sm" c="dimmed">
                    {article.lastUpdated}
                  </Text>
                </Table.Td>
                <Table.Td style={{ textAlign: 'right' }}>
                  <Text size="sm">{article.usageCount.toLocaleString()}</Text>
                </Table.Td>
                <Table.Td>
                  <Group gap="xs" wrap="nowrap">
                    <Progress
                      value={article.helpfulRate}
                      color={article.helpfulRate >= 90 ? 'green' : article.helpfulRate >= 70 ? 'yellow' : 'red'}
                      size="sm"
                      style={{ flex: 1 }}
                    />
                    <Text size="xs" c="dimmed" w={36} ta="right">
                      {article.helpfulRate}%
                    </Text>
                  </Group>
                </Table.Td>
                <Table.Td>
                  <Group gap={4} justify="flex-end" wrap="nowrap">
                    <ActionIcon
                      variant="subtle"
                      color="gray"
                      size="sm"
                      onClick={() => handleEditArticle(article)}
                      title="Edit article"
                    >
                      <EditIcon />
                    </ActionIcon>
                    {article.status !== 'archived' && (
                      <ActionIcon
                        variant="subtle"
                        color="gray"
                        size="sm"
                        onClick={() => handleArchiveArticle(article.id)}
                        title="Archive article"
                      >
                        <ArchiveIcon />
                      </ActionIcon>
                    )}
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {filteredArticles.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={7}>
                  <Text ta="center" c="dimmed" py="xl">
                    No articles match your filters.
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Paper>

      {/* Add / Edit Modal */}
      <Modal
        opened={modalOpened}
        onClose={closeModal}
        title={
          <Text fw={600} size="lg">
            {editingArticle ? 'Edit Article' : 'Add Article'}
          </Text>
        }
        size="lg"
        radius="md"
      >
        <Stack gap="md">
          <TextInput
            label="Title"
            placeholder="Article title"
            value={form.title}
            onChange={(e) => setForm((f) => ({ ...f, title: e.currentTarget.value }))}
            required
          />
          <Select
            label="Category"
            data={CATEGORIES.filter((c) => c !== 'All')}
            value={form.category}
            onChange={(val) => setForm((f) => ({ ...f, category: val || 'Policies' }))}
            required
          />
          <div>
            <Textarea
              label="Content"
              placeholder="Write the article content here..."
              value={form.content}
              onChange={(e) =>
                setForm((f) => ({ ...f, content: e.currentTarget.value }))
              }
              minRows={8}
              autosize
              maxRows={16}
              required
            />
            <Text size="xs" c="dimmed" mt={4}>
              Prototype uses plain text. Production will use Tiptap rich text editor with
              formatting, images, and tables.
            </Text>
          </div>
          <Select
            label="Status"
            data={[
              { value: 'published', label: 'Published' },
              { value: 'draft', label: 'Draft' },
              { value: 'archived', label: 'Archived' },
            ]}
            value={form.status}
            onChange={(val) => setForm((f) => ({ ...f, status: val || 'draft' }))}
            required
          />
          <Group justify="flex-end" mt="md">
            <Button variant="default" onClick={closeModal}>
              Cancel
            </Button>
            <Button
              color={BRAND_RED}
              onClick={handleSave}
              disabled={!form.title.trim() || !form.content.trim()}
            >
              {editingArticle ? 'Save Changes' : 'Create Article'}
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
}
