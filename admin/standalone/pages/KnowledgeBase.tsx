// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

import React, { useState, useMemo, useCallback, useRef } from 'react';
import {
  Paper,
  Table,
  TextInput,
  Select,
  Modal,
  Textarea,
  Button,
  Badge,
  Group,
  Stack,
  Title,
  Text,
  ActionIcon,
  SimpleGrid,
  Loader,
  Center,
  Tabs,
  Progress,
  Alert,
  Accordion,
  Tooltip,
} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useKnowledgeBase, useSaveKBArticle, useUploadFile, useImportUrl, useExportCSV, useStalenessSummary, useVerifyEntry } from '../../shared/hooks/index';
import type { KBArticle, KBArticleStatus, KBUploadResult } from '../../shared/types/index';

const BRAND_RED = '#ff3621';

const CATEGORIES = ['All', 'Policies', 'Shipping', 'Products', 'Sales', 'Services'];
const STATUSES = ['All', 'Published', 'Draft', 'Archived'];
const ACCEPTED_FILE_TYPES = '.pdf,.docx,.csv,.txt';

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

const stalenessColorMap: Record<string, string> = {
  fresh: 'green',
  aging: 'yellow',
  stale: 'red',
  very_stale: 'red',
};

const stalenessLabelMap: Record<string, string> = {
  fresh: 'Fresh',
  aging: 'Aging',
  stale: 'Stale',
  very_stale: 'Very stale',
};

// ---------------------------------------------------------------------------
// Icons as inline SVGs
// ---------------------------------------------------------------------------

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

const UploadIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="17 8 12 3 7 8" />
    <line x1="12" y1="3" x2="12" y2="15" />
  </svg>
);

const DownloadIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="7 10 12 15 17 10" />
    <line x1="12" y1="15" x2="12" y2="3" />
  </svg>
);

const CheckIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12" />
  </svg>
);

const ScanIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    <line x1="12" y1="8" x2="12" y2="12" />
    <line x1="12" y1="16" x2="12.01" y2="16" />
  </svg>
);

const AlertTriangleIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
    <line x1="12" y1="9" x2="12" y2="13" />
    <line x1="12" y1="17" x2="12.01" y2="17" />
  </svg>
);

// ---------------------------------------------------------------------------
// Conflict scan types
// ---------------------------------------------------------------------------

interface ConflictPair {
  entryAId: string;
  entryATitle: string;
  entryBId: string;
  entryBTitle: string;
  conflictType: string;
  severity: string;
  embeddingSimilarity: number;
  contentOverlap: number;
  titleSimilarity: number;
  conflictingFacts: string[];
  resolution: string;
}

interface ScanResult {
  tenantId: string;
  scannedAt: string;
  totalEntriesScanned: number;
  entriesWithEmbeddings: number;
  entriesWithoutEmbeddings: number;
  conflicts: ConflictPair[];
  highCount: number;
  mediumCount: number;
  lowCount: number;
  scanDurationMs: number;
}

const severityColorMap: Record<string, string> = {
  high: 'red',
  medium: 'orange',
  low: 'yellow',
};

const conflictTypeLabel: Record<string, string> = {
  near_duplicate: 'Near duplicate',
  conflicting: 'Conflicting information',
  topical_overlap: 'Topical overlap',
  similar_titles: 'Similar titles',
};

// ---------------------------------------------------------------------------
// Form state
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
// Helpers
// ---------------------------------------------------------------------------

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '--';
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return iso;
  }
}

// ---------------------------------------------------------------------------
// Page component
// ---------------------------------------------------------------------------

export const KnowledgeBasePage: React.FC = () => {
  const { apiFetch, onNotify } = useAppContext();

  // API hooks
  const kbResult = useKnowledgeBase(apiFetch);
  const articles: KBArticle[] = kbResult.data?.articles ?? [];
  const { save, loading: saving, error: saveError } = useSaveKBArticle(apiFetch);
  const { upload: uploadFile, loading: uploading, error: uploadError, progress: uploadProgress, reset: resetUpload } = useUploadFile(apiFetch);
  const { importUrl, loading: importing, error: importError } = useImportUrl(apiFetch);
  const { exportCSV, loading: exporting } = useExportCSV(apiFetch);

  // Staleness hooks
  const { data: stalenessData, refetch: refetchStaleness } = useStalenessSummary(apiFetch);
  const { verify, loading: verifying } = useVerifyEntry(apiFetch);

  // Local UI state
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string | null>('All');
  const [statusFilter, setStatusFilter] = useState<string | null>('All');
  const [modalOpened, { open: openModal, close: closeModal }] = useDisclosure(false);
  const [importModalOpened, { open: openImportModal, close: closeImportModal }] = useDisclosure(false);
  const [editingArticle, setEditingArticle] = useState<KBArticle | null>(null);
  const [form, setForm] = useState<ArticleFormState>(emptyForm);
  const [importUrl2, setImportUrl2] = useState('');
  const [uploadResult, setUploadResult] = useState<KBUploadResult | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Conflict scan state
  const [scanModalOpened, { open: openScanModal, close: closeScanModal }] = useDisclosure(false);
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [scanError, setScanError] = useState<string | null>(null);

  // Filter articles
  const filteredArticles = useMemo(() => {
    return articles.filter((article) => {
      const matchesSearch =
        search === '' ||
        (article.title ?? '').toLowerCase().includes(search.toLowerCase()) ||
        (article.content ?? '').toLowerCase().includes(search.toLowerCase());
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
    const published = articles.filter((a) => a.status === 'published').length;
    const draft = articles.filter((a) => a.status === 'draft').length;
    return { total: articles.length, published, draft };
  }, [articles]);

  // Handlers
  const handleAddArticle = () => {
    setEditingArticle(null);
    setForm(emptyForm);
    openModal();
  };

  const handleEditArticle = (article: KBArticle) => {
    setEditingArticle(article);
    setForm({
      title: article.title ?? '',
      category: article.category ?? 'Policies',
      content: article.content ?? '',
      status: article.status ?? 'draft',
    });
    openModal();
  };

  const handleArchiveArticle = async (article: KBArticle) => {
    const result = await save({ ...article, status: 'archived' as KBArticleStatus });
    if (result) {
      onNotify(`"${article.title}" archived`, 'success');
      kbResult.refetch();
    } else {
      onNotify(saveError || 'Failed to archive article', 'error');
    }
  };

  const handleSave = async () => {
    const articleData: Partial<KBArticle> = {
      title: form.title,
      category: form.category,
      content: form.content,
      status: form.status as KBArticleStatus,
      entryType: 'article',
    };
    if (editingArticle) articleData.id = editingArticle.id;

    const result = await save(articleData);
    if (result) {
      onNotify(editingArticle ? 'Article updated successfully' : 'Article created successfully', 'success');
      kbResult.refetch();
      closeModal();
    } else {
      onNotify(saveError || 'Failed to save article', 'error');
    }
  };

  const handleVerify = useCallback(
    async (entryId: string) => {
      const result = await verify(entryId);
      if (result) {
        onNotify('Article verified as current', 'success');
        kbResult.refetch();
        refetchStaleness();
      } else {
        onNotify('Failed to verify article', 'error');
      }
    },
    [verify, onNotify, kbResult, refetchStaleness],
  );

  const handleOpenImport = useCallback(() => {
    setUploadResult(null);
    resetUpload();
    setImportUrl2('');
    openImportModal();
  }, [resetUpload, openImportModal]);

  const handleFileUpload = useCallback(
    async (file: File) => {
      const result = await uploadFile(file);
      if (result) {
        setUploadResult(result);
        onNotify(`Imported ${result.entries_created} entries from ${file.name}`, 'success');
      } else {
        onNotify('File upload failed', 'error');
      }
    },
    [uploadFile, onNotify],
  );

  const handleFileDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (uploading) return;
      const file = e.dataTransfer.files?.[0];
      if (file) handleFileUpload(file);
    },
    [handleFileUpload, uploading],
  );

  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFileUpload(file);
      if (fileInputRef.current) fileInputRef.current.value = '';
    },
    [handleFileUpload],
  );

  const handleUrlImport = useCallback(async () => {
    const trimmed = importUrl2.trim();
    if (!trimmed) return;
    const result = await importUrl(trimmed);
    if (result) {
      setUploadResult(result);
      onNotify(`Imported ${result.entries_created} entries from URL`, 'success');
    } else {
      onNotify('URL import failed', 'error');
    }
  }, [importUrl2, importUrl, onNotify]);

  const handleImportDone = useCallback(() => {
    setUploadResult(null);
    closeImportModal();
    kbResult.refetch();
  }, [closeImportModal, kbResult]);

  const handleExport = useCallback(async () => {
    const ok = await exportCSV();
    if (ok) {
      onNotify('Knowledge base exported as CSV', 'success');
    } else {
      onNotify('Export failed', 'error');
    }
  }, [exportCSV, onNotify]);

  const handleScan = useCallback(async (force = false) => {
    setScanning(true);
    setScanError(null);
    try {
      const qs = force ? '?force=true' : '';
      const resp = await apiFetch(`/api/admin/knowledge/scan${qs}`, { method: 'POST' });
      if (resp.ok) {
        const data: ScanResult = await resp.json();
        setScanResult(data);
        openScanModal();
        const total = data.highCount + data.mediumCount + data.lowCount;
        if (total > 0) {
          onNotify(`Scan found ${total} issue${total === 1 ? '' : 's'} (${data.highCount} high, ${data.mediumCount} medium, ${data.lowCount} low)`, 'warning');
        } else {
          onNotify('No conflicts or duplicates found', 'success');
        }
      } else if (resp.status === 503) {
        setScanError('Conflict scanner is not available. This feature requires embedding support.');
        onNotify('Conflict scanner not available', 'error');
      } else {
        const text = await resp.text().catch(() => 'Unknown error');
        setScanError(text);
        onNotify('Scan failed', 'error');
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Network error';
      setScanError(msg);
      onNotify('Scan failed: ' + msg, 'error');
    } finally {
      setScanning(false);
    }
  }, [apiFetch, onNotify, openScanModal]);

  // Loading state
  if (kbResult.loading && articles.length === 0) {
    return (
      <Center py="xl">
        <Loader color={BRAND_RED} />
      </Center>
    );
  }

  // Error state
  if (kbResult.error && articles.length === 0) {
    return (
      <Stack gap="lg">
        <div>
          <Title order={2}>Knowledge base</Title>
          <Text c="dimmed" size="sm">Manage articles your AI uses to answer customers</Text>
        </div>
        <Paper p="xl" radius="md" withBorder>
          <Text c="red" ta="center">Failed to load knowledge base: {kbResult.error}</Text>
          <Center mt="md">
            <Button variant="default" onClick={kbResult.refetch}>Retry</Button>
          </Center>
        </Paper>
      </Stack>
    );
  }

  return (
    <Stack gap="lg">
      {/* Page header */}
      <div>
        <Title order={2}>Knowledge base</Title>
        <Text c="dimmed" size="sm">
          Manage articles your AI uses to answer customers
        </Text>
      </div>

      {/* Top bar: Search + Filters + Action buttons */}
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
          <Group gap="sm">
            <Tooltip label="Detect duplicate, overlapping, or contradictory entries that may cause inconsistent AI responses" multiline w={260} withArrow>
              <Button
                leftSection={<ScanIcon />}
                variant="default"
                onClick={() => handleScan(false)}
                loading={scanning}
                disabled={articles.length === 0}
              >
                Scan for conflicts
              </Button>
            </Tooltip>
            <Tooltip label="Download all knowledge base entries as a CSV file for backup or editing" multiline w={220} withArrow>
              <Button
                leftSection={<DownloadIcon />}
                variant="default"
                onClick={handleExport}
                loading={exporting}
                disabled={articles.length === 0}
              >
                Export CSV
              </Button>
            </Tooltip>
            <Tooltip label="Upload PDF, DOCX, CSV, or TXT files, or import from a URL to bulk-create entries" multiline w={240} withArrow>
              <Button
                leftSection={<UploadIcon />}
                variant="default"
                onClick={handleOpenImport}
              >
                Import
              </Button>
            </Tooltip>
            <Tooltip label="Create a new knowledge base article. Articles give your AI specific information to reference when answering customer questions." multiline w={260} withArrow>
              <Button
                leftSection={<PlusIcon />}
                color={BRAND_RED}
                onClick={handleAddArticle}
              >
                Add article
              </Button>
            </Tooltip>
          </Group>
        </Group>
      </Paper>

      {/* Summary stats -- 4 cards: Total, Published, Draft, Needs Attention */}
      <SimpleGrid cols={{ base: 1, xs: 4 }} spacing="md">
        <Paper p="md" radius="md" withBorder>
          <Text size="xs" c="dimmed" fw={600} mb={4}>Total articles</Text>
          <Text size="xl" fw={700} lh={1}>{stats.total}</Text>
        </Paper>
        <Paper p="md" radius="md" withBorder>
          <Text size="xs" c="dimmed" fw={600} mb={4}>Published</Text>
          <Text size="xl" fw={700} lh={1} c="green">{stats.published}</Text>
        </Paper>
        <Paper p="md" radius="md" withBorder>
          <Text size="xs" c="dimmed" fw={600} mb={4}>Draft</Text>
          <Text size="xl" fw={700} lh={1} c="yellow.7">{stats.draft}</Text>
        </Paper>
        <Tooltip label="Articles marked stale or very stale that should be reviewed for accuracy" multiline w={240} withArrow>
          <Paper p="md" radius="md" withBorder style={{ cursor: 'help' }}>
            <Text size="xs" c="dimmed" fw={600} mb={4}>Needs attention</Text>
            <Text size="xl" fw={700} lh={1} c="red">
              {(stalenessData?.staleCount ?? 0) + (stalenessData?.veryStaleCount ?? 0)}
            </Text>
          </Paper>
        </Tooltip>
      </SimpleGrid>

      {/* Articles table */}
      <Paper p="md" radius="md" withBorder>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Title</Table.Th>
              <Table.Th>Category</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Freshness</Table.Th>
              <Table.Th>Last updated</Table.Th>
              <Table.Th style={{ textAlign: 'right' }}>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {filteredArticles.map((article) => (
              <Table.Tr key={article.id}>
                <Table.Td>
                  <Text size="sm" fw={500}>{article.title}</Text>
                </Table.Td>
                <Table.Td>
                  {article.category ? (
                    <Badge size="sm" variant="light" color={categoryColorMap[article.category] || 'gray'}>
                      {article.category}
                    </Badge>
                  ) : (
                    <Text size="xs" c="dimmed">--</Text>
                  )}
                </Table.Td>
                <Table.Td>
                  {article.status ? (
                    <Badge size="sm" variant="light" color={statusColorMap[article.status] || 'gray'}>
                      {article.status}
                    </Badge>
                  ) : (
                    <Text size="xs" c="dimmed">--</Text>
                  )}
                </Table.Td>
                <Table.Td>
                  <Badge size="sm" variant="light" color={stalenessColorMap[article.stalenessCategory ?? ''] || 'gray'}>
                    {stalenessLabelMap[article.stalenessCategory ?? ''] || '--'}
                  </Badge>
                </Table.Td>
                <Table.Td>
                  <Text size="sm" c="dimmed">{formatDate(article.updatedAt)}</Text>
                </Table.Td>
                <Table.Td>
                  <Group gap={4} justify="flex-end" wrap="nowrap">
                    {(article.stalenessCategory === 'stale' || article.stalenessCategory === 'aging' || article.stalenessCategory === 'very_stale') && (
                      <ActionIcon variant="subtle" color="green" size="sm" onClick={() => handleVerify(article.id)} title="Mark as verified" loading={verifying}>
                        <CheckIcon />
                      </ActionIcon>
                    )}
                    <ActionIcon variant="subtle" color="gray" size="sm" onClick={() => handleEditArticle(article)} title="Edit article">
                      <EditIcon />
                    </ActionIcon>
                    {article.status !== 'archived' && (
                      <ActionIcon variant="subtle" color="gray" size="sm" onClick={() => handleArchiveArticle(article)} title="Archive article" loading={saving}>
                        <ArchiveIcon />
                      </ActionIcon>
                    )}
                  </Group>
                </Table.Td>
              </Table.Tr>
            ))}
            {filteredArticles.length === 0 && (
              <Table.Tr>
                <Table.Td colSpan={6}>
                  <Text ta="center" c="dimmed" py="xl">No articles match your filters.</Text>
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
        title={<Text fw={600} size="lg">{editingArticle ? 'Edit article' : 'Add article'}</Text>}
        size="lg"
        radius="md"
      >
        <Stack gap="md">
          <TextInput label="Title" placeholder="Article title" value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.currentTarget.value }))} required />
          <Select label="Category" data={CATEGORIES.filter((c) => c !== 'All')} value={form.category} onChange={(val) => setForm((f) => ({ ...f, category: val || 'Policies' }))} required />
          <Textarea label="Content" placeholder="Write the article content here..." value={form.content} onChange={(e) => setForm((f) => ({ ...f, content: e.currentTarget.value }))} minRows={8} autosize maxRows={16} required />
          <Select label="Status" data={[{ value: 'published', label: 'Published' }, { value: 'draft', label: 'Draft' }, { value: 'archived', label: 'Archived' }]} value={form.status} onChange={(val) => setForm((f) => ({ ...f, status: val || 'draft' }))} required />
          {saveError && <Text size="sm" c="red">{saveError}</Text>}
          <Group justify="flex-end" mt="md">
            <Button variant="default" onClick={closeModal}>Cancel</Button>
            <Button color={BRAND_RED} onClick={handleSave} disabled={!form.title.trim() || !form.content.trim()} loading={saving}>
              {editingArticle ? 'Save changes' : 'Create article'}
            </Button>
          </Group>
        </Stack>
      </Modal>

      {/* Import Modal */}
      <Modal
        opened={importModalOpened}
        onClose={() => { closeImportModal(); setUploadResult(null); }}
        title={<Text fw={600} size="lg">Import content</Text>}
        size="lg"
        radius="md"
      >
        {uploadResult ? (
          <Stack gap="md" ta="center" py="lg">
            <Text size="xl">{String.fromCodePoint(0x2705)}</Text>
            <Title order={3}>Import successful</Title>
            <Text c="dimmed">
              Created {uploadResult.entries_created} {uploadResult.entries_created === 1 ? 'entry' : 'entries'} from{' '}
              {uploadResult.source_filename || uploadResult.source_url || 'document'}{' '}
              ({Math.round(uploadResult.total_chars / 1000)}K characters)
            </Text>
            <Group justify="center" mt="md">
              <Button color={BRAND_RED} onClick={handleImportDone}>
                Back to knowledge base
              </Button>
            </Group>
          </Stack>
        ) : (
          <Tabs defaultValue="file">
            <Tabs.List mb="lg">
              <Tabs.Tab value="file">Upload file</Tabs.Tab>
              <Tabs.Tab value="url">Import URL</Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="file">
              <Stack gap="md">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept={ACCEPTED_FILE_TYPES}
                  onChange={handleFileInputChange}
                  style={{ display: 'none' }}
                />
                <Paper
                  p="xl"
                  radius="md"
                  withBorder
                  onDragOver={(e: React.DragEvent) => { e.preventDefault(); setDragOver(true); }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={handleFileDrop}
                  onClick={() => !uploading && fileInputRef.current?.click()}
                  style={{
                    cursor: uploading ? 'default' : 'pointer',
                    borderStyle: 'dashed',
                    borderColor: dragOver ? BRAND_RED : undefined,
                    backgroundColor: dragOver ? `${BRAND_RED}08` : undefined,
                    textAlign: 'center',
                    opacity: uploading ? 0.7 : 1,
                    transition: 'all 0.2s ease',
                  }}
                >
                  {uploading ? (
                    <Stack gap="sm" align="center">
                      <Loader size="sm" color={BRAND_RED} />
                      <Text size="sm" fw={500}>
                        {uploadProgress === 'uploading' ? 'Uploading...' : 'Processing document...'}
                      </Text>
                      <Progress
                        value={uploadProgress === 'uploading' ? 40 : 80}
                        color={BRAND_RED}
                        w={200}
                        size="xs"
                        animated
                      />
                    </Stack>
                  ) : (
                    <Stack gap="xs" align="center">
                      <Text size="xl">{String.fromCodePoint(0x1F4C4)}</Text>
                      <Text size="sm" fw={500}>Drop a file here or click to browse</Text>
                      <Text size="xs" c="dimmed">Supported: PDF, DOCX, CSV, TXT (max 50MB)</Text>
                    </Stack>
                  )}
                </Paper>
                {uploadError && <Text size="sm" c="red">{uploadError}</Text>}
              </Stack>
            </Tabs.Panel>

            <Tabs.Panel value="url">
              <Stack gap="md">
                <TextInput
                  label="Website URL"
                  placeholder="https://example.com/faq"
                  value={importUrl2}
                  onChange={(e) => setImportUrl2(e.currentTarget.value)}
                  disabled={importing}
                />
                <Text size="xs" c="dimmed">
                  We'll extract text content from the page and create knowledge base entries.
                </Text>
                {importError && <Text size="sm" c="red">{importError}</Text>}
                <Group justify="flex-end">
                  <Button
                    color={BRAND_RED}
                    onClick={handleUrlImport}
                    disabled={!importUrl2.trim()}
                    loading={importing}
                  >
                    Import
                  </Button>
                </Group>
              </Stack>
            </Tabs.Panel>
          </Tabs>
        )}
      </Modal>

      {/* Conflict Scan Results Modal */}
      <Modal
        opened={scanModalOpened}
        onClose={closeScanModal}
        title={<Text fw={600} size="lg">Conflict scan results</Text>}
        size="xl"
        radius="md"
      >
        {scanError && (
          <Alert color="red" title="Scan error" mb="md">
            {scanError}
          </Alert>
        )}

        {scanResult && (
          <Stack gap="md">
            {/* Summary stats */}
            <SimpleGrid cols={{ base: 2, xs: 4 }} spacing="sm">
              <Paper p="sm" radius="md" withBorder>
                <Text size="xs" c="dimmed" fw={600}>Entries scanned</Text>
                <Text size="lg" fw={700}>{scanResult.totalEntriesScanned}</Text>
              </Paper>
              <Paper p="sm" radius="md" withBorder>
                <Text size="xs" c="dimmed" fw={600}>With embeddings</Text>
                <Text size="lg" fw={700}>{scanResult.entriesWithEmbeddings}</Text>
              </Paper>
              <Paper p="sm" radius="md" withBorder>
                <Text size="xs" c="dimmed" fw={600}>Scan time</Text>
                <Text size="lg" fw={700}>{scanResult.scanDurationMs < 1000 ? `${scanResult.scanDurationMs}ms` : `${(scanResult.scanDurationMs / 1000).toFixed(1)}s`}</Text>
              </Paper>
              <Paper p="sm" radius="md" withBorder>
                <Text size="xs" c="dimmed" fw={600}>Issues found</Text>
                <Text size="lg" fw={700} c={scanResult.highCount > 0 ? 'red' : scanResult.mediumCount > 0 ? 'orange' : 'green'}>
                  {scanResult.highCount + scanResult.mediumCount + scanResult.lowCount}
                </Text>
              </Paper>
            </SimpleGrid>

            {/* Severity breakdown */}
            {(scanResult.highCount > 0 || scanResult.mediumCount > 0 || scanResult.lowCount > 0) && (
              <Group gap="sm">
                {scanResult.highCount > 0 && (
                  <Badge size="lg" color="red" variant="light">
                    {scanResult.highCount} high severity
                  </Badge>
                )}
                {scanResult.mediumCount > 0 && (
                  <Badge size="lg" color="orange" variant="light">
                    {scanResult.mediumCount} medium
                  </Badge>
                )}
                {scanResult.lowCount > 0 && (
                  <Badge size="lg" color="yellow" variant="light">
                    {scanResult.lowCount} low
                  </Badge>
                )}
              </Group>
            )}

            {/* No issues state */}
            {scanResult.conflicts.length === 0 && (
              <Alert color="green" title="All clear" variant="light">
                No conflicts, duplicates, or overlapping content detected in your knowledge base.
              </Alert>
            )}

            {/* Conflict list */}
            {scanResult.conflicts.length > 0 && (
              <Accordion variant="separated" radius="md">
                {scanResult.conflicts.map((conflict, idx) => (
                  <Accordion.Item key={`${conflict.entryAId}-${conflict.entryBId}-${idx}`} value={`conflict-${idx}`}>
                    <Accordion.Control>
                      <Group gap="sm" wrap="nowrap">
                        <Badge size="sm" color={severityColorMap[conflict.severity] || 'gray'} variant="filled" style={{ flexShrink: 0 }}>
                          {conflict.severity.toUpperCase()}
                        </Badge>
                        <Badge size="sm" color="gray" variant="light" style={{ flexShrink: 0 }}>
                          {conflictTypeLabel[conflict.conflictType] || conflict.conflictType}
                        </Badge>
                        <Text size="sm" truncate="end" style={{ flex: 1 }}>
                          {conflict.entryATitle} &harr; {conflict.entryBTitle}
                        </Text>
                      </Group>
                    </Accordion.Control>
                    <Accordion.Panel>
                      <Stack gap="sm">
                        <SimpleGrid cols={2} spacing="sm">
                          <Paper p="sm" radius="sm" withBorder>
                            <Text size="xs" c="dimmed" fw={600} mb={4}>Article A</Text>
                            <Text size="sm" fw={500}>{conflict.entryATitle}</Text>
                          </Paper>
                          <Paper p="sm" radius="sm" withBorder>
                            <Text size="xs" c="dimmed" fw={600} mb={4}>Article B</Text>
                            <Text size="sm" fw={500}>{conflict.entryBTitle}</Text>
                          </Paper>
                        </SimpleGrid>

                        <Group gap="lg">
                          <Tooltip label="How similar the article content embeddings are (0-1)">
                            <Text size="xs" c="dimmed">
                              Embedding similarity: <Text span fw={600}>{(conflict.embeddingSimilarity * 100).toFixed(1)}%</Text>
                            </Text>
                          </Tooltip>
                          <Tooltip label="Percentage of overlapping content between the two articles">
                            <Text size="xs" c="dimmed">
                              Content overlap: <Text span fw={600}>{(conflict.contentOverlap * 100).toFixed(1)}%</Text>
                            </Text>
                          </Tooltip>
                          <Tooltip label="How similar the article titles are (0-1)">
                            <Text size="xs" c="dimmed">
                              Title similarity: <Text span fw={600}>{(conflict.titleSimilarity * 100).toFixed(1)}%</Text>
                            </Text>
                          </Tooltip>
                        </Group>

                        {conflict.conflictingFacts.length > 0 && (
                          <Alert color="orange" variant="light" title="Conflicting facts" icon={<AlertTriangleIcon />}>
                            <Stack gap={4}>
                              {conflict.conflictingFacts.map((fact, fi) => (
                                <Text key={fi} size="sm">{fact}</Text>
                              ))}
                            </Stack>
                          </Alert>
                        )}

                        <Paper p="sm" radius="sm" style={{ backgroundColor: 'var(--mantine-color-dark-7)' }}>
                          <Text size="xs" c="dimmed" fw={600} mb={4}>Suggested resolution</Text>
                          <Text size="sm">{conflict.resolution}</Text>
                        </Paper>
                      </Stack>
                    </Accordion.Panel>
                  </Accordion.Item>
                ))}
              </Accordion>
            )}

            {/* Footer actions */}
            <Group justify="space-between" mt="sm">
              <Text size="xs" c="dimmed">
                Scanned at {(() => {
                  try { return new Date(scanResult.scannedAt).toLocaleString(); }
                  catch { return scanResult.scannedAt; }
                })()}
                {scanResult.entriesWithoutEmbeddings > 0 && (
                  <> &middot; {scanResult.entriesWithoutEmbeddings} entries skipped (no embeddings)</>
                )}
              </Text>
              <Group gap="sm">
                <Button variant="default" size="sm" onClick={() => handleScan(true)} loading={scanning}>
                  Re-scan (force)
                </Button>
                <Button color={BRAND_RED} size="sm" onClick={closeScanModal}>
                  Close
                </Button>
              </Group>
            </Group>
          </Stack>
        )}
      </Modal>
    </Stack>
  );
};
