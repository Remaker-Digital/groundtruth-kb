/**
 * AlertConfig — Alert rules and history management.
 *
 * Two tabs: Rules (CRUD) and History (list + acknowledge).
 * Create, edit, enable/disable, and delete alert rules.
 * View firing history with severity badges and acknowledge.
 *
 * API: GET/POST/PUT/DELETE /api/superadmin/alerts/rules
 *      GET /api/superadmin/alerts/history
 *      POST .../acknowledge
 *      POST .../evaluate
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import {
  ActionIcon,
  Badge,
  Button,
  Card,
  Group,
  Loader,
  Modal,
  NumberInput,
  Select,
  Stack,
  Switch,
  Table,
  Tabs,
  Text,
  Textarea,
  TextInput,
  Title,
} from '@mantine/core';
import { useProviderContext } from '../layouts/ProviderLayout';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { tokens } from '../../shared/theme/styles';

// ---------------------------------------------------------------------------
// Types (matches camelCase serialization)
// ---------------------------------------------------------------------------

interface AlertCondition {
  metric: string;
  operator: string;
  threshold: number;
}

interface AlertRule {
  ruleId: string;
  ruleType: string;
  name: string;
  description: string;
  enabled: boolean;
  condition: AlertCondition;
  notificationChannels: string[];
  cooldownMinutes: number;
  runbookUrl: string;
  createdAt: string;
  updatedAt: string;
}

interface AlertRuleListResponse {
  rules: AlertRule[];
  total: number;
}

interface AlertHistoryItem {
  alertId: string;
  alertDate: string;
  ruleId: string;
  ruleName: string;
  ruleType: string;
  tenantId?: string;
  triggeredAt: string;
  resolvedAt: string | null;
  severity: string;
  message: string;
  metricValue: number;
  thresholdValue: number;
  acknowledged: boolean;
  acknowledgedBy: string | null;
}

interface AlertHistoryResponse {
  alerts: AlertHistoryItem[];
  total: number;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const RULE_TYPE_OPTIONS = [
  { value: 'queue_depth', label: 'Queue Depth' },
  { value: 'secret_expiry', label: 'Secret Expiry' },
  { value: 'circuit_breaker', label: 'Circuit Breaker' },
  { value: 'sla_breach', label: 'SLA Breach' },
  { value: 'incident', label: 'Incident' },
  { value: 'quality_regression', label: 'Quality Regression' },
];

const OPERATOR_OPTIONS = [
  { value: 'gt', label: '> (greater than)' },
  { value: 'lt', label: '< (less than)' },
  { value: 'gte', label: '>= (greater or equal)' },
  { value: 'lte', label: '<= (less or equal)' },
  { value: 'eq', label: '= (equal)' },
  { value: 'ne', label: '!= (not equal)' },
  { value: 'lt_delta', label: 'Δ< (delta less than)' },
];

const SEVERITY_COLORS: Record<string, string> = {
  info: 'blue',
  warning: 'orange',
  critical: 'red',
};

const TYPE_COLORS: Record<string, string> = {
  queue_depth: 'cyan',
  secret_expiry: 'violet',
  circuit_breaker: 'orange',
  sla_breach: 'red',
  incident: 'pink',
  quality_regression: 'teal',
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function formatDate(iso: string): string {
  if (!iso) return '\u2014';
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

function formatCondition(c: AlertCondition): string {
  const ops: Record<string, string> = {
    gt: '>', lt: '<', gte: '>=', lte: '<=', eq: '=', ne: '!=', lt_delta: 'Δ<',
  };
  return `${c.metric || '?'} ${ops[c.operator] || c.operator} ${c.threshold}`;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export function AlertConfigPage() {
  const { apiFetch, onNotify } = useProviderContext();

  // Rules state
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [rulesLoading, setRulesLoading] = useState(true);

  // History state
  const [history, setHistory] = useState<AlertHistoryItem[]>([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  // Create/Edit modal
  const [modalOpen, setModalOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<AlertRule | null>(null);
  const [formName, setFormName] = useState('');
  const [formType, setFormType] = useState<string | null>('queue_depth');
  const [formDesc, setFormDesc] = useState('');
  const [formMetric, setFormMetric] = useState('');
  const [formOperator, setFormOperator] = useState<string | null>('gt');
  const [formThreshold, setFormThreshold] = useState<number>(0);
  const [formCooldown, setFormCooldown] = useState<number>(60);
  const [formRunbook, setFormRunbook] = useState('');
  const [saving, setSaving] = useState(false);

  const fetchRules = useCallback(async () => {
    try {
      const res = await apiFetch('/api/superadmin/alerts/rules');
      if (res.ok) {
        const data: AlertRuleListResponse = await res.json();
        setRules(data.rules);
      } else {
        onNotify('Failed to load alert rules', 'error');
      }
    } catch {
      onNotify('Network error loading rules', 'error');
    } finally {
      setRulesLoading(false);
    }
  }, [apiFetch, onNotify]);

  const fetchHistory = useCallback(async () => {
    try {
      const res = await apiFetch('/api/superadmin/alerts/history?days=30&limit=200');
      if (res.ok) {
        const data: AlertHistoryResponse = await res.json();
        setHistory(data.alerts);
      } else {
        onNotify('Failed to load alert history', 'error');
      }
    } catch {
      onNotify('Network error loading history', 'error');
    } finally {
      setHistoryLoading(false);
    }
  }, [apiFetch, onNotify]);

  useEffect(() => {
    fetchRules();
    fetchHistory();
  }, [fetchRules, fetchHistory]);

  const openCreateModal = () => {
    setEditingRule(null);
    setFormName('');
    setFormType('queue_depth');
    setFormDesc('');
    setFormMetric('');
    setFormOperator('gt');
    setFormThreshold(0);
    setFormCooldown(60);
    setFormRunbook('');
    setModalOpen(true);
  };

  const openEditModal = (rule: AlertRule) => {
    setEditingRule(rule);
    setFormName(rule.name);
    setFormType(rule.ruleType);
    setFormDesc(rule.description);
    setFormMetric(rule.condition.metric);
    setFormOperator(rule.condition.operator);
    setFormThreshold(rule.condition.threshold);
    setFormCooldown(rule.cooldownMinutes);
    setFormRunbook(rule.runbookUrl);
    setModalOpen(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = {
        name: formName,
        ruleType: formType || 'queue_depth',
        description: formDesc,
        condition: {
          metric: formMetric,
          operator: formOperator || 'gt',
          threshold: formThreshold,
        },
        notificationChannels: editingRule?.notificationChannels ?? ['email'],
        cooldownMinutes: formCooldown,
        runbookUrl: formRunbook,
      };

      const url = editingRule
        ? `/api/superadmin/alerts/rules/${editingRule.ruleId}`
        : '/api/superadmin/alerts/rules';
      const method = editingRule ? 'PUT' : 'POST';

      const res = await apiFetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        onNotify(editingRule ? 'Rule updated' : 'Rule created', 'success');
        setModalOpen(false);
        await fetchRules();
      } else {
        onNotify('Failed to save rule', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleToggleEnabled = async (rule: AlertRule) => {
    try {
      const res = await apiFetch(`/api/superadmin/alerts/rules/${rule.ruleId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled: !rule.enabled }),
      });
      if (res.ok) {
        onNotify(`Rule ${!rule.enabled ? 'enabled' : 'disabled'}`, 'success');
        await fetchRules();
      } else {
        onNotify('Failed to toggle rule', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    }
  };

  const handleDelete = async (rule: AlertRule) => {
    try {
      const res = await apiFetch(`/api/superadmin/alerts/rules/${rule.ruleId}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        onNotify('Rule deleted', 'success');
        await fetchRules();
      } else {
        onNotify('Failed to delete rule', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    }
  };

  const handleAcknowledge = async (item: AlertHistoryItem) => {
    try {
      const res = await apiFetch(
        `/api/superadmin/alerts/history/${item.alertId}/acknowledge?alert_date=${encodeURIComponent(item.alertDate)}`,
        { method: 'POST' },
      );
      if (res.ok) {
        onNotify('Alert acknowledged', 'success');
        await fetchHistory();
      } else {
        onNotify('Failed to acknowledge', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    }
  };

  const handleEvaluate = async () => {
    try {
      const res = await apiFetch('/api/superadmin/alerts/evaluate', { method: 'POST' });
      if (res.ok) {
        const result = await res.json();
        onNotify(result.evaluated ? 'Evaluation complete' : result.message || 'Evaluation skipped', 'success');
        await fetchHistory();
      } else {
        onNotify('Evaluation failed', 'error');
      }
    } catch {
      onNotify('Network error', 'error');
    }
  };

  return (
    <Stack gap="lg">
      <Group justify="space-between" align="baseline">
        <Title order={3} c={tokens.textPrimary}>Alert Configuration</Title><HelpTooltip text="Define rules that monitor system metrics and trigger alerts when thresholds are exceeded. Rules are evaluated every 5 minutes." />
        <Group gap="sm">
          <Button variant="light" color="orange" size="sm" onClick={handleEvaluate}>
            Evaluate Now
          </Button>
          <Button color="action" size="sm" onClick={openCreateModal}>
            Create Rule
          </Button>
        </Group>
      </Group>

      <Tabs defaultValue="rules" color="action">
        <Tabs.List>
          <Tabs.Tab value="rules">Rules ({rules.length})</Tabs.Tab>
          <Tabs.Tab value="history">History ({history.length})</Tabs.Tab>
        </Tabs.List>

        {/* Rules Tab */}
        <Tabs.Panel value="rules" pt="md">
          {rulesLoading ? (
            <Stack align="center" mt="xl">
              <Loader color="action" />
              <Text c="dimmed" size="sm">Loading rules...</Text>
            </Stack>
          ) : rules.length === 0 ? (
            <Text c="dimmed" ta="center" mt="xl">No alert rules configured.</Text>
          ) : (
            <Table striped highlightOnHover>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Name</Table.Th>
                  <Table.Th>Type</Table.Th>
                  <Table.Th>Condition</Table.Th>
                  <Table.Th>Cooldown<HelpTooltip text="Minimum time between repeated alerts for the same rule. Prevents alert fatigue." /></Table.Th>
                  <Table.Th>Enabled</Table.Th>
                  <Table.Th>Actions</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {rules.map((rule) => (
                  <Table.Tr key={rule.ruleId}>
                    <Table.Td>
                      <Text size="sm" fw={500} c={tokens.textSecondary}>{rule.name}</Text>
                      {rule.description && (
                        <Text size="xs" c="dimmed" lineClamp={1}>{rule.description}</Text>
                      )}
                    </Table.Td>
                    <Table.Td>
                      <Badge variant="light" color={TYPE_COLORS[rule.ruleType] ?? 'gray'} size="sm">
                        {rule.ruleType.replace(/_/g, ' ')}
                      </Badge>
                    </Table.Td>
                    <Table.Td>
                      <Text size="xs" ff="monospace" c={tokens.textMuted}>
                        {formatCondition(rule.condition)}
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      <Text size="xs" c={tokens.textMuted}>{rule.cooldownMinutes}m</Text>
                    </Table.Td>
                    <Table.Td>
                      <Switch
                        checked={rule.enabled}
                        onChange={() => handleToggleEnabled(rule)}
                        size="sm"
                        color="green"
                      />
                    </Table.Td>
                    <Table.Td>
                      <Group gap="xs">
                        <Button variant="subtle" size="xs" onClick={() => openEditModal(rule)}>
                          Edit
                        </Button>
                        <Button variant="subtle" color="red" size="xs" onClick={() => handleDelete(rule)}>
                          Delete
                        </Button>
                      </Group>
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          )}
        </Tabs.Panel>

        {/* History Tab */}
        <Tabs.Panel value="history" pt="md">
          {historyLoading ? (
            <Stack align="center" mt="xl">
              <Loader color="action" />
              <Text c="dimmed" size="sm">Loading history...</Text>
            </Stack>
          ) : history.length === 0 ? (
            <Text c="dimmed" ta="center" mt="xl">No alert history.</Text>
          ) : (
            <Table striped highlightOnHover>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>Rule</Table.Th>
                  <Table.Th>Type</Table.Th>
                  {history.some((h) => h.tenantId) && <Table.Th>Tenant</Table.Th>}
                  <Table.Th>Severity</Table.Th>
                  <Table.Th>Message</Table.Th>
                  <Table.Th>Value</Table.Th>
                  <Table.Th>Triggered</Table.Th>
                  <Table.Th>Status</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {history.map((item) => (
                  <Table.Tr key={item.alertId}>
                    <Table.Td>
                      <Text size="sm" c={tokens.textSecondary}>{item.ruleName}</Text>
                    </Table.Td>
                    <Table.Td>
                      <Badge variant="light" color={TYPE_COLORS[item.ruleType] ?? 'gray'} size="xs">
                        {item.ruleType.replace(/_/g, ' ')}
                      </Badge>
                    </Table.Td>
                    {history.some((h) => h.tenantId) && (
                      <Table.Td>
                        <Text size="xs" c={tokens.textSecondary}>{item.tenantId || '\u2014'}</Text>
                      </Table.Td>
                    )}
                    <Table.Td>
                      <Badge variant="filled" color={SEVERITY_COLORS[item.severity] ?? 'gray'} size="xs">
                        {item.severity}
                      </Badge>
                    </Table.Td>
                    <Table.Td>
                      <Text size="xs" c={tokens.textMuted} lineClamp={2}>{item.message}</Text>
                    </Table.Td>
                    <Table.Td>
                      <Text size="xs" ff="monospace" c={tokens.textSecondary}>
                        {item.metricValue} / {item.thresholdValue}
                      </Text>
                    </Table.Td>
                    <Table.Td>
                      <Text size="xs" c="dimmed">{formatDate(item.triggeredAt)}</Text>
                    </Table.Td>
                    <Table.Td>
                      {item.acknowledged ? (
                        <Badge variant="light" color="green" size="xs">
                          Ack: {item.acknowledgedBy ?? 'system'}
                        </Badge>
                      ) : (
                        <Button
                          variant="light"
                          color="orange"
                          size="xs"
                          onClick={() => handleAcknowledge(item)}
                        >
                          Acknowledge
                        </Button>
                      )}
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          )}
        </Tabs.Panel>
      </Tabs>

      {/* Create/Edit Rule Modal */}
      <Modal
        opened={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingRule ? 'Edit Alert Rule' : 'Create Alert Rule'}
        size="lg"
        styles={{ content: { backgroundColor: tokens.surface }, header: { backgroundColor: tokens.surface } }}
      >
        <Stack gap="md">
          <TextInput
            label="Name"
            placeholder="Alert rule name"
            value={formName}
            onChange={(e) => setFormName(e.currentTarget.value)}
            required
            styles={{ input: { backgroundColor: tokens.page, borderColor: tokens.border, color: tokens.textPrimary } }}
          />
          <Select
            label="Rule Type"
            data={RULE_TYPE_OPTIONS}
            value={formType}
            onChange={setFormType}
            disabled={!!editingRule}
            styles={{ input: { backgroundColor: tokens.page, borderColor: tokens.border, color: tokens.textPrimary } }}
          />
          <Textarea
            label="Description"
            placeholder="What this rule monitors"
            value={formDesc}
            onChange={(e) => setFormDesc(e.currentTarget.value)}
            minRows={2}
            styles={{ input: { backgroundColor: tokens.page, borderColor: tokens.border, color: tokens.textPrimary } }}
          />

          <Text size="sm" fw={600} c={tokens.textMuted} tt="uppercase">Condition</Text><HelpTooltip text="Define when this rule fires. The metric is compared to the threshold using the selected operator." />
          <Group grow>
            <TextInput
              label="Metric"
              placeholder="e.g. queue_depth, error_rate"
              value={formMetric}
              onChange={(e) => setFormMetric(e.currentTarget.value)}
              styles={{ input: { backgroundColor: tokens.page, borderColor: tokens.border, color: tokens.textPrimary } }}
            />
            <Select
              label="Operator"
              data={OPERATOR_OPTIONS}
              value={formOperator}
              onChange={setFormOperator}
              styles={{ input: { backgroundColor: tokens.page, borderColor: tokens.border, color: tokens.textPrimary } }}
            />
            <NumberInput
              label="Threshold"
              value={formThreshold}
              onChange={(v) => setFormThreshold(typeof v === 'number' ? v : 0)}
              styles={{ input: { backgroundColor: tokens.page, borderColor: tokens.border, color: tokens.textPrimary } }}
            />
          </Group>

          <Group grow>
            <NumberInput
              label="Cooldown (minutes)"
              value={formCooldown}
              onChange={(v) => setFormCooldown(typeof v === 'number' ? v : 60)}
              min={1}
              styles={{ input: { backgroundColor: tokens.page, borderColor: tokens.border, color: tokens.textPrimary } }}
            />
            <TextInput
              label="Runbook URL"
              placeholder="https://..."
              value={formRunbook}
              onChange={(e) => setFormRunbook(e.currentTarget.value)}
              styles={{ input: { backgroundColor: tokens.page, borderColor: tokens.border, color: tokens.textPrimary } }}
            />
          </Group>

          <Group justify="flex-end">
            <Button variant="subtle" onClick={() => setModalOpen(false)}>Cancel</Button>
            <Button
              color="action"
              loading={saving}
              disabled={!formName.trim()}
              onClick={handleSave}
            >
              {editingRule ? 'Update Rule' : 'Create Rule'}
            </Button>
          </Group>
        </Stack>
      </Modal>
    </Stack>
  );
}
