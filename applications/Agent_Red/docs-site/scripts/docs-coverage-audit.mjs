#!/usr/bin/env node

/**
 * Documentation Coverage Audit Script
 *
 * Reads docs-inventory.yml and produces a coverage report showing
 * documentation completeness across Diataxis content types.
 *
 * Usage: node scripts/docs-coverage-audit.js
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const inventoryPath = resolve(__dirname, '..', 'docs-inventory.yml');

// Simple YAML parser for the inventory format (avoids adding js-yaml dependency)
// Extracts feature names, categories, and status values
function parseInventory(content) {
  const features = [];
  let currentFeature = null;
  let currentType = null;

  for (const line of content.split('\n')) {
    const trimmed = line.trim();

    // Feature name
    const nameMatch = trimmed.match(/^- name:\s*(.+)/);
    if (nameMatch) {
      if (currentFeature) features.push(currentFeature);
      currentFeature = {
        name: nameMatch[1].replace(/^["']|["']$/g, ''),
        category: null,
        tutorial: null,
        how_to: null,
        reference: null,
        explanation: null,
      };
      currentType = null;
      continue;
    }

    if (!currentFeature) continue;

    // Category
    const catMatch = trimmed.match(/^category:\s*(.+)/);
    if (catMatch) {
      currentFeature.category = catMatch[1];
      continue;
    }

    // Diataxis type headers
    if (trimmed === 'tutorial:') { currentType = 'tutorial'; continue; }
    if (trimmed === 'how_to:') { currentType = 'how_to'; continue; }
    if (trimmed === 'reference:') { currentType = 'reference'; continue; }
    if (trimmed === 'explanation:') { currentType = 'explanation'; continue; }

    // Status within a type
    const statusMatch = trimmed.match(/^status:\s*(.+)/);
    if (statusMatch && currentType && currentFeature) {
      currentFeature[currentType] = statusMatch[1].replace(/^["']|["']$/g, '');
      continue;
    }
  }

  if (currentFeature) features.push(currentFeature);
  return features;
}

function generateReport(features) {
  const types = ['tutorial', 'how_to', 'reference', 'explanation'];
  const statuses = ['complete', 'partial', 'placeholder', 'missing', 'deferred', 'n/a'];

  console.log('='.repeat(70));
  console.log('  Agent Red Documentation Coverage Report');
  console.log('='.repeat(70));
  console.log();

  // Overall summary
  const totalSlots = features.length * types.length;
  const counts = {};
  for (const s of statuses) counts[s] = 0;

  for (const feature of features) {
    for (const type of types) {
      const status = feature[type] || 'missing';
      counts[status] = (counts[status] || 0) + 1;
    }
  }

  console.log('  OVERALL SUMMARY');
  console.log('-'.repeat(40));
  console.log(`  Total feature x type slots:  ${totalSlots}`);
  console.log(`  Complete:                    ${counts.complete} (${pct(counts.complete, totalSlots)})`);
  console.log(`  Partial:                     ${counts.partial} (${pct(counts.partial, totalSlots)})`);
  console.log(`  Placeholder:                 ${counts.placeholder} (${pct(counts.placeholder, totalSlots)})`);
  console.log(`  Missing:                     ${counts.missing} (${pct(counts.missing, totalSlots)})`);
  console.log(`  Deferred:                    ${counts.deferred} (${pct(counts.deferred, totalSlots)})`);
  console.log(`  N/A:                         ${counts['n/a']} (${pct(counts['n/a'], totalSlots)})`);
  console.log();

  // Actionable coverage (excluding deferred and n/a)
  const actionable = totalSlots - counts.deferred - counts['n/a'];
  const documented = counts.complete + counts.partial + counts.placeholder;
  console.log(`  ACTIONABLE COVERAGE (excl. deferred & n/a)`);
  console.log('-'.repeat(40));
  console.log(`  Actionable slots:            ${actionable}`);
  console.log(`  Documented (any level):      ${documented} (${pct(documented, actionable)})`);
  console.log(`  Gaps (missing):              ${counts.missing} (${pct(counts.missing, actionable)})`);
  console.log();

  // Per-type breakdown
  console.log('  BY DIATAXIS TYPE');
  console.log('-'.repeat(40));
  for (const type of types) {
    const typeCounts = {};
    for (const s of statuses) typeCounts[s] = 0;
    for (const feature of features) {
      const status = feature[type] || 'missing';
      typeCounts[status] = (typeCounts[status] || 0) + 1;
    }
    const label = type.replace('_', '-').padEnd(12);
    const done = typeCounts.complete + typeCounts.partial;
    const total = features.length - typeCounts.deferred - typeCounts['n/a'];
    console.log(`  ${label}  ${done}/${total} documented  (${pct(done, total)})`);
  }
  console.log();

  // Per-category breakdown
  console.log('  BY CATEGORY');
  console.log('-'.repeat(40));
  const categories = [...new Set(features.map(f => f.category))];
  for (const cat of categories) {
    const catFeatures = features.filter(f => f.category === cat);
    let catComplete = 0;
    let catTotal = 0;
    for (const feature of catFeatures) {
      for (const type of types) {
        const status = feature[type] || 'missing';
        if (status !== 'deferred' && status !== 'n/a') {
          catTotal++;
          if (status === 'complete' || status === 'partial') catComplete++;
        }
      }
    }
    const label = cat.padEnd(14);
    console.log(`  ${label}  ${catComplete}/${catTotal} documented  (${pct(catComplete, catTotal)})`);
  }
  console.log();

  // Gap list
  console.log('  GAPS (missing, not deferred)');
  console.log('-'.repeat(40));
  let gapCount = 0;
  for (const feature of features) {
    for (const type of types) {
      const status = feature[type] || 'missing';
      if (status === 'missing') {
        console.log(`  - ${feature.name} > ${type.replace('_', '-')}`);
        gapCount++;
      }
    }
  }
  if (gapCount === 0) console.log('  None!');
  console.log();
  console.log('='.repeat(70));
}

function pct(n, total) {
  if (total === 0) return '0%';
  return `${Math.round((n / total) * 100)}%`;
}

// Main
try {
  const content = readFileSync(inventoryPath, 'utf-8');
  const features = parseInventory(content);
  generateReport(features);
} catch (err) {
  console.error(`Error reading inventory: ${err.message}`);
  process.exit(1);
}
