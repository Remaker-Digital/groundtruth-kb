/**
 * CopilotKnowledge — Co-Pilot Knowledge Management page (SPEC-1578).
 *
 * Four tabs: Documents, Ingestion, Schedule, Parameters.
 * Manages admin documentation for the Co-Pilot agent.
 *
 * APIs:
 *   GET    /api/superadmin/copilot/documents
 *   POST   /api/superadmin/copilot/documents
 *   PUT    /api/superadmin/copilot/documents/:id
 *   DELETE /api/superadmin/copilot/documents/:id
 *   POST   /api/superadmin/copilot/ingest/docs-site
 *   POST   /api/superadmin/copilot/ingest/url
 *   POST   /api/superadmin/copilot/re-embed
 *   GET    /api/superadmin/copilot/stats
 *   POST   /api/superadmin/copilot/test-query
 *   GET    /api/superadmin/copilot/config/schedule
 *   PUT    /api/superadmin/copilot/config/schedule
 *   GET    /api/superadmin/copilot/config/retrieval
 *   PUT    /api/superadmin/copilot/config/retrieval
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  Badge,
  Button,
  Card,
  Group,
  NumberInput,
  Paper,
  Select,
  SimpleGrid,
  Slider,
  Stack,
  Table,
  Tabs,
  Text,
  Textarea,
  TextInput,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { LoadingState } from '../../shared/LoadingState';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface CopilotDocument {
  id: string;
  documentCategory: string;
  title: string;
  content: string;
  tags: string[];
  isActive: boolean;
  contentHash: string | null;
  embeddingModel: string | null;
  embeddedAt: string | null;
  sourceFile: string | null;
  createdAt: string;
  updatedAt: string;
}

interface DocumentListResponse {
  documents: CopilotDocument[];
  total: number;
}

interface CopilotStats {
  totalDocuments: number;
  activeDocuments: number;
  byCategory: Record<string, number>;
  embeddedCount: number;
  staleCount: number;
  embeddingModel: string;
}

interface IngestionResponse {
  created: number;
  updated: number;
  skipped: number;
  errors: Array<{ file: string; message: string }>;
}

interface ScheduleConfig {
  scanFrequency: string;
  scanScope: string;
  lastScanAt: string | null;
  nextScanAt: string | null;
  scanHistory: Array<Record<string, unknown>>;
}

interface RetrievalConfig {
  vectorWeight: number;
  bm25Weight: number;
  rrfK: number;
  topK: number;
  minScore: number;
  updatedAt: string | null;
  updatedBy: string | null;
}

interface TestQueryResult {
  id: string;
  title: string;
  category: string;
  rrfScore: number;
  snippet: string;
}

interface TestQueryResponse {
  query: string;
  results: TestQueryResult[];
  totalDocuments: number;
}

// ---------------------------------------------------------------------------
// Documents Tab
// ---------------------------------------------------------------------------

function DocumentsTab() {
  const { apiFetch, onNotify } = useProviderContext();
  const [docs, setDocs] = useState<CopilotDocument[]>([]);
  const [stats, setStats] = useState<CopilotStats | null>(null);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [docRes, statsRes] = await Promise.all([
        apiFetch('/api/superadmin/copilot/documents'),
        apiFetch('/api/superadmin/copilot/stats'),
      ]);
      if (docRes.ok) {
        const data: DocumentListResponse = await docRes.json();
        setDocs(data.documents ?? []);
      }
      if (statsRes.ok) {
        setStats(await statsRes.json());
      }
    } catch {
      onNotify('Failed to load documents', 'error');
    } finally {
      setLoading(false);
    }
  }, [apiFetch, onNotify]);

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) return <LoadingState text="Loading documents" />;

  return (
    <Stack gap="md">
      {/* Stats cards */}
      {stats && (
        <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md">
          <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
            <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Total Documents</Text>
            <Text fw={700} size="xl" c={tokens.textPrimary} mt={4}>{stats.totalDocuments}</Text>
          </Card>
          <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
            <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Active</Text>
            <Text fw={700} size="xl" c={tokens.success} mt={4}>{stats.activeDocuments}</Text>
          </Card>
          <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
            <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Embedded</Text>
            <Text fw={700} size="xl" c={tokens.chartBlue} mt={4}>{stats.embeddedCount}</Text>
          </Card>
          <Card withBorder padding="lg" radius="md" bg={tokens.surface}>
            <Text c="dimmed" size="xs" tt="uppercase" fw={600}>Stale</Text>
            <Text fw={700} size="xl" c={stats.staleCount > 0 ? tokens.danger : tokens.textMuted} mt={4}>
              {stats.staleCount}
            </Text>
          </Card>
        </SimpleGrid>
      )}

      {/* Category breakdown */}
      {stats && Object.keys(stats.byCategory ?? {}).length > 0 && (
        <Paper withBorder radius="md" bg={tokens.surface} p="md">
          <Text size="sm" fw={500} c={tokens.textSecondary} mb="sm">Categories</Text>
          <Group gap="sm">
            {Object.entries(stats.byCategory ?? {}).map(([cat, count]) => (
              <Badge key={cat} variant="light" color="blue" size="lg">
                {cat.replace(/_/g, ' ')}: {count}
              </Badge>
            ))}
          </Group>
        </Paper>
      )}

      {/* Documents table */}
      <Paper withBorder radius="md" bg={tokens.surface} style={{ overflow: 'auto' }}>
        <Table striped highlightOnHover>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>Title</Table.Th>
              <Table.Th>Category</Table.Th>
              <Table.Th>Tags</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Embedded</Table.Th>
              <Table.Th>Updated</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {docs.length === 0 ? (
              <Table.Tr>
                <Table.Td colSpan={6}>
                  <Text c="dimmed" ta="center" py="md">No documents yet</Text>
                </Table.Td>
              </Table.Tr>
            ) : (
              docs.map((doc) => (
                <Table.Tr key={doc.id}>
                  <Table.Td>
                    <Text size="xs" fw={500} c={tokens.textSecondary}>{doc.title}</Text>
                  </Table.Td>
                  <Table.Td>
                    <Badge variant="light" color="blue" size="sm">
                      {doc.documentCategory?.replace(/_/g, ' ') ?? '\u2014'}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Group gap={4}>
                      {(doc.tags ?? []).slice(0, 3).map((tag) => (
                        <Badge key={tag} variant="outline" size="xs" color="gray">{tag}</Badge>
                      ))}
                    </Group>
                  </Table.Td>
                  <Table.Td>
                    <Badge
                      variant="filled"
                      size="sm"
                      color={doc.isActive ? 'green' : 'red'}
                    >
                      {doc.isActive ? 'Active' : 'Inactive'}
                    </Badge>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c={doc.embeddedAt ? tokens.success : tokens.textMuted}>
                      {doc.embeddedAt ? '\u2713' : '\u2014'}
                    </Text>
                  </Table.Td>
                  <Table.Td>
                    <Text size="xs" c="dimmed">
                      {doc.updatedAt ? new Date(doc.updatedAt).toLocaleDateString() : '\u2014'}
                    </Text>
                  </Table.Td>
                </Table.Tr>
              ))
            )}
          </Table.Tbody>
        </Table>
      </Paper>
    </Stack>
  );
}

// ---------------------------------------------------------------------------
// Ingestion Tab
// ---------------------------------------------------------------------------

function IngestionTab() {
  const { apiFetch, onNotify } = useProviderContext();
  const [ingesting, setIngesting] = useState(false);
  const [reembedding, setReembedding] = useState(false);
  const [result, setResult] = useState<IngestionResponse | null>(null);
  const [urlImport, setUrlImport] = useState({ url: '', category: '', title: '' });

  const handleIngest = async () => {
    setIngesting(true);
    setResult(null);
    try {
      const res = await apiFetch('/api/superadmin/copilot/ingest/docs-site', { method: 'POST' });
      if (res.ok) {
        const data: IngestionResponse = await res.json();
        setResult(data);
        onNotify(`Ingestion complete: ${data.created} created, ${data.updated} updated, ${data.skipped} skipped`, 'success');
      } else {
        const err = await res.json().catch(() => ({ detail: 'Unknown error' }));
        onNotify(err.detail || 'Ingestion failed', 'error');
      }
    } catch {
      onNotify('Network error during ingestion', 'error');
    } finally {
      setIngesting(false);
    }
  };

  const handleReembed = async () => {
    setReembedding(true);
    try {
      const res = await apiFetch('/api/superadmin/copilot/re-embed', { method: 'POST' });
      if (res.ok) {
        const data: IngestionResponse = await res.json();
        onNotify(`Re-embedding complete: ${data.updated} documents updated`, 'success');
      } else {
        onNotify('Re-embedding failed', 'error');
      }
    } catch {
      onNotify('Network error during re-embedding', 'error');
    } finally {
      setReembedding(false);
    }
  };

  const handleUrlImport = async () => {
    if (!urlImport.url) return;
    try {
      const res = await apiFetch('/api/superadmin/copilot/ingest/url', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: urlImport.url,
          document_category: urlImport.category || 'general',
          title: urlImport.title || undefined,
        }),
      });
      if (res.ok) {
        onNotify('URL imported successfully', 'success');
        setUrlImport({ url: '', category: '', title: '' });
      } else {
        const err = await res.json().catch(() => ({ detail: 'Import failed' }));
        onNotify(err.detail || 'URL import failed', 'error');
      }
    } catch {
      onNotify('Network error during URL import', 'error');
    }
  };

  return (
    <Stack gap="lg">
      {/* Batch ingestion */}
      <Paper withBorder radius="md" bg={tokens.surface} p="md">
        <Text size="sm" fw={500} c={tokens.textSecondary} mb="sm">
          Batch Ingestion
          <HelpTooltip text="Scan docs/admin-guide/*.md and create/update documents. Unchanged files are skipped via content hash." />
        </Text>
        <Group gap="md">
          <Button
            onClick={handleIngest}
            loading={ingesting}
            color="blue"
            variant="filled"
          >
            Scan Docs Site
          </Button>
          <Button
            onClick={handleReembed}
            loading={reembedding}
            color="violet"
            variant="light"
          >
            Re-Embed All
          </Button>
        </Group>
        {result && (
          <Paper withBorder radius="md" p="sm" mt="md" bg={tokens.surface}>
            <Group gap="lg">
              <Text size="sm" c={tokens.success}>Created: {result.created}</Text>
              <Text size="sm" c={tokens.chartBlue}>Updated: {result.updated}</Text>
              <Text size="sm" c={tokens.textMuted}>Skipped: {result.skipped}</Text>
              {(result.errors ?? []).length > 0 && (
                <Text size="sm" c={tokens.danger}>Errors: {result.errors.length}</Text>
              )}
            </Group>
          </Paper>
        )}
      </Paper>

      {/* URL import */}
      <Paper withBorder radius="md" bg={tokens.surface} p="md">
        <Text size="sm" fw={500} c={tokens.textSecondary} mb="sm">
          URL Import
          <HelpTooltip text="Fetch content from a URL and create a document. HTTPS only." />
        </Text>
        <Stack gap="sm">
          <TextInput
            label="URL"
            placeholder="https://example.com/docs/guide"
            value={urlImport.url}
            onChange={(e) => setUrlImport({ ...urlImport, url: e.target.value })}
          />
          <Group gap="sm" grow>
            <TextInput
              label="Title (optional)"
              placeholder="Guide Title"
              value={urlImport.title}
              onChange={(e) => setUrlImport({ ...urlImport, title: e.target.value })}
            />
            <TextInput
              label="Category"
              placeholder="getting_started"
              value={urlImport.category}
              onChange={(e) => setUrlImport({ ...urlImport, category: e.target.value })}
            />
          </Group>
          <Button onClick={handleUrlImport} color="blue" variant="light" disabled={!urlImport.url}>
            Import URL
          </Button>
        </Stack>
      </Paper>
    </Stack>
  );
}

// ---------------------------------------------------------------------------
// Schedule Tab
// ---------------------------------------------------------------------------

function ScheduleTab() {
  const { apiFetch, onNotify } = useProviderContext();
  const [schedule, setSchedule] = useState<ScheduleConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch('/api/superadmin/copilot/config/schedule');
        if (res.ok && !cancelled) {
          setSchedule(await res.json());
        }
      } catch {
        if (!cancelled) onNotify('Failed to load schedule', 'error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch, onNotify]);

  const handleSave = async () => {
    if (!schedule) return;
    setSaving(true);
    try {
      const res = await apiFetch('/api/superadmin/copilot/config/schedule', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scan_frequency: schedule.scanFrequency,
          scan_scope: schedule.scanScope,
        }),
      });
      if (res.ok) {
        setSchedule(await res.json());
        onNotify('Schedule updated', 'success');
      } else {
        onNotify('Failed to update schedule', 'error');
      }
    } catch {
      onNotify('Network error saving schedule', 'error');
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <LoadingState text="Loading schedule" />;
  if (!schedule) return <Text c="dimmed" ta="center">Unable to load schedule</Text>;

  return (
    <Stack gap="lg">
      <Paper withBorder radius="md" bg={tokens.surface} p="md">
        <Text size="sm" fw={500} c={tokens.textSecondary} mb="sm">
          Scan Schedule
          <HelpTooltip text="Configure automatic re-ingestion frequency. Manual means no automatic scanning." />
        </Text>
        <Group gap="md" align="end">
          <Select
            label="Frequency"
            data={[
              { value: 'manual', label: 'Manual Only' },
              { value: 'daily', label: 'Daily' },
              { value: 'weekly', label: 'Weekly' },
            ]}
            value={schedule.scanFrequency}
            onChange={(val) => setSchedule({ ...schedule, scanFrequency: val || 'manual' })}
            style={{ width: 200 }}
          />
          <Select
            label="Scope"
            data={[
              { value: 'docs-site', label: 'Docs Site' },
              { value: 'urls', label: 'Registered URLs' },
              { value: 'both', label: 'Both' },
            ]}
            value={schedule.scanScope}
            onChange={(val) => setSchedule({ ...schedule, scanScope: val || 'docs-site' })}
            style={{ width: 200 }}
          />
          <Button onClick={handleSave} loading={saving} color="blue">
            Save Schedule
          </Button>
        </Group>
      </Paper>

      {/* Timing info */}
      <Paper withBorder radius="md" bg={tokens.surface} p="md">
        <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
          <div>
            <Text size="xs" c="dimmed" tt="uppercase" fw={600}>Last Scan</Text>
            <Text size="sm" c={tokens.textPrimary} mt={4}>
              {schedule.lastScanAt ? new Date(schedule.lastScanAt).toLocaleString() : '\u2014 Never'}
            </Text>
          </div>
          <div>
            <Text size="xs" c="dimmed" tt="uppercase" fw={600}>Next Scan</Text>
            <Text size="sm" c={tokens.textPrimary} mt={4}>
              {schedule.nextScanAt ? new Date(schedule.nextScanAt).toLocaleString() : '\u2014 Manual'}
            </Text>
          </div>
        </SimpleGrid>
      </Paper>

      {/* Scan history */}
      {(schedule.scanHistory ?? []).length > 0 && (
        <Paper withBorder radius="md" bg={tokens.surface} p="md">
          <Text size="sm" fw={500} c={tokens.textSecondary} mb="sm">Scan History</Text>
          <Table striped>
            <Table.Thead>
              <Table.Tr>
                <Table.Th>Timestamp</Table.Th>
                <Table.Th>Created</Table.Th>
                <Table.Th>Updated</Table.Th>
                <Table.Th>Skipped</Table.Th>
                <Table.Th>Errors</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {(schedule.scanHistory ?? []).map((entry, i) => (
                <Table.Tr key={i}>
                  <Table.Td>
                    <Text size="xs" c="dimmed">
                      {entry.timestamp ? new Date(String(entry.timestamp)).toLocaleString() : '\u2014'}
                    </Text>
                  </Table.Td>
                  <Table.Td><Text size="xs">{String(entry.created ?? 0)}</Text></Table.Td>
                  <Table.Td><Text size="xs">{String(entry.updated ?? 0)}</Text></Table.Td>
                  <Table.Td><Text size="xs">{String(entry.skipped ?? 0)}</Text></Table.Td>
                  <Table.Td><Text size="xs">{String(entry.errors ?? 0)}</Text></Table.Td>
                </Table.Tr>
              ))}
            </Table.Tbody>
          </Table>
        </Paper>
      )}
    </Stack>
  );
}

// ---------------------------------------------------------------------------
// Parameters Tab
// ---------------------------------------------------------------------------

function ParametersTab() {
  const { apiFetch, onNotify } = useProviderContext();
  const [config, setConfig] = useState<RetrievalConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testQuery, setTestQuery] = useState('');
  const [testResult, setTestResult] = useState<TestQueryResponse | null>(null);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await apiFetch('/api/superadmin/copilot/config/retrieval');
        if (res.ok && !cancelled) {
          setConfig(await res.json());
        }
      } catch {
        if (!cancelled) onNotify('Failed to load retrieval config', 'error');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch, onNotify]);

  const handleSave = async () => {
    if (!config) return;
    setSaving(true);
    try {
      const res = await apiFetch('/api/superadmin/copilot/config/retrieval', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vector_weight: config.vectorWeight,
          bm25_weight: config.bm25Weight,
          rrf_k: config.rrfK,
          top_k: config.topK,
          min_score: config.minScore,
        }),
      });
      if (res.ok) {
        setConfig(await res.json());
        onNotify('Retrieval parameters saved', 'success');
      } else {
        const err = await res.json().catch(() => ({ detail: 'Save failed' }));
        onNotify(err.detail || 'Failed to save parameters', 'error');
      }
    } catch {
      onNotify('Network error saving parameters', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleTestQuery = async () => {
    if (!testQuery.trim()) return;
    setTesting(true);
    setTestResult(null);
    try {
      const res = await apiFetch('/api/superadmin/copilot/test-query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: testQuery, top_k: config?.topK ?? 5 }),
      });
      if (res.ok) {
        setTestResult(await res.json());
      } else {
        onNotify('Test query failed', 'error');
      }
    } catch {
      onNotify('Network error during test query', 'error');
    } finally {
      setTesting(false);
    }
  };

  if (loading) return <LoadingState text="Loading retrieval config" />;
  if (!config) return <Text c="dimmed" ta="center">Unable to load retrieval config</Text>;

  return (
    <Stack gap="lg">
      {/* Retrieval parameter sliders */}
      <Paper withBorder radius="md" bg={tokens.surface} p="md">
        <Text size="sm" fw={500} c={tokens.textSecondary} mb="md">
          Retrieval Parameters
          <HelpTooltip text="Tune the hybrid search algorithm. Changes apply to the next Co-Pilot query." />
        </Text>
        <Stack gap="md">
          <div>
            <Text size="xs" c={tokens.textMuted} mb={4}>
              Vector Weight: {config.vectorWeight.toFixed(2)}
            </Text>
            <Slider
              min={0} max={1} step={0.05}
              value={config.vectorWeight}
              onChange={(val) => setConfig({ ...config, vectorWeight: val })}
              marks={[{ value: 0, label: '0' }, { value: 0.5, label: '0.5' }, { value: 1, label: '1' }]}
            />
          </div>
          <div>
            <Text size="xs" c={tokens.textMuted} mb={4}>
              BM25 Weight: {config.bm25Weight.toFixed(2)}
            </Text>
            <Slider
              min={0} max={1} step={0.05}
              value={config.bm25Weight}
              onChange={(val) => setConfig({ ...config, bm25Weight: val })}
              marks={[{ value: 0, label: '0' }, { value: 0.5, label: '0.5' }, { value: 1, label: '1' }]}
            />
          </div>
          <Group gap="md" grow>
            <NumberInput
              label="RRF k"
              description="Rank fusion constant (1-100)"
              min={1} max={100}
              value={config.rrfK}
              onChange={(val) => setConfig({ ...config, rrfK: typeof val === 'number' ? val : 60 })}
            />
            <NumberInput
              label="Top K"
              description="Results to return (1-20)"
              min={1} max={20}
              value={config.topK}
              onChange={(val) => setConfig({ ...config, topK: typeof val === 'number' ? val : 5 })}
            />
            <NumberInput
              label="Min Score"
              description="Minimum relevance (0-1)"
              min={0} max={1} step={0.05} decimalScale={2}
              value={config.minScore}
              onChange={(val) => setConfig({ ...config, minScore: typeof val === 'number' ? val : 0.1 })}
            />
          </Group>
          <Group gap="md">
            <Button onClick={handleSave} loading={saving} color="blue">
              Save Parameters
            </Button>
            {config.updatedAt && (
              <Text size="xs" c="dimmed">
                Last saved: {new Date(config.updatedAt).toLocaleString()}
              </Text>
            )}
          </Group>
        </Stack>
      </Paper>

      {/* Test query */}
      <Paper withBorder radius="md" bg={tokens.surface} p="md">
        <Text size="sm" fw={500} c={tokens.textSecondary} mb="sm">
          Test Query
          <HelpTooltip text="Run a test query against the knowledge base using current parameters." />
        </Text>
        <Group gap="md" align="end">
          <Textarea
            label="Query"
            placeholder="How do I configure the widget?"
            value={testQuery}
            onChange={(e) => setTestQuery(e.target.value)}
            style={{ flex: 1 }}
            autosize
            minRows={1}
            maxRows={3}
          />
          <Button onClick={handleTestQuery} loading={testing} color="violet" variant="light">
            Search
          </Button>
        </Group>

        {testResult && (
          <Stack gap="sm" mt="md">
            <Text size="xs" c="dimmed">
              {testResult.results.length} results from {testResult.totalDocuments} documents
            </Text>
            {testResult.results.map((r, i) => (
              <Paper key={i} withBorder radius="sm" p="sm" bg={tokens.surface}>
                <Group gap="xs" mb={4}>
                  <Badge variant="light" color="blue" size="xs">{r.category}</Badge>
                  <Text size="xs" fw={600} c={tokens.textPrimary}>{r.title}</Text>
                  <Badge variant="filled" color="violet" size="xs">
                    {r.rrfScore.toFixed(3)}
                  </Badge>
                </Group>
                <Text size="xs" c={tokens.textMuted}>{r.snippet}</Text>
              </Paper>
            ))}
          </Stack>
        )}
      </Paper>
    </Stack>
  );
}

// ---------------------------------------------------------------------------
// Main Page Component
// ---------------------------------------------------------------------------

export function CopilotKnowledgePage() {
  return (
    <Stack gap="lg">
      <Group gap="xs">
        <Title order={3} c={tokens.textPrimary}>Co-Pilot Knowledge</Title>
        <HelpTooltip text="Manage admin documentation for the Co-Pilot agent. Documents are vectorized and used for semantic search during admin conversations." />
      </Group>

      <Tabs defaultValue="documents" variant="outline">
        <Tabs.List>
          <Tabs.Tab value="documents">Documents</Tabs.Tab>
          <Tabs.Tab value="ingestion">Ingestion</Tabs.Tab>
          <Tabs.Tab value="schedule">Schedule</Tabs.Tab>
          <Tabs.Tab value="parameters">Parameters</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="documents" pt="md">
          <DocumentsTab />
        </Tabs.Panel>
        <Tabs.Panel value="ingestion" pt="md">
          <IngestionTab />
        </Tabs.Panel>
        <Tabs.Panel value="schedule" pt="md">
          <ScheduleTab />
        </Tabs.Panel>
        <Tabs.Panel value="parameters" pt="md">
          <ParametersTab />
        </Tabs.Panel>
      </Tabs>
    </Stack>
  );
}
