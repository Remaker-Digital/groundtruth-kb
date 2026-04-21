#!/usr/bin/env node

import { spawnSync } from "node:child_process";
import { readdirSync, statSync } from "node:fs";
import path from "node:path";
import process from "node:process";

const root = process.cwd();
const docsDir = path.join(root, "docs");
const configPath = ".markdown-link-check.json";

function collectMarkdownFiles(dir) {
  const entries = readdirSync(dir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...collectMarkdownFiles(fullPath));
    } else if (entry.isFile() && fullPath.endsWith(".md")) {
      files.push(fullPath);
    }
  }

  return files;
}

if (!statSync(docsDir, { throwIfNoEntry: false })?.isDirectory()) {
  console.error(`Docs directory not found: ${docsDir}`);
  process.exit(1);
}

const markdownFiles = collectMarkdownFiles(docsDir).map((filePath) =>
  path.relative(root, filePath).replaceAll(path.sep, "/"),
);
if (markdownFiles.length === 0) {
  console.error(`No markdown files found under ${docsDir}`);
  process.exit(1);
}

const npxBin = process.platform === "win32" ? "npx.cmd" : "npx";
const batchSize = 10;
let exitCode = 0;

for (let index = 0; index < markdownFiles.length; index += batchSize) {
  const batch = markdownFiles.slice(index, index + batchSize);
  const result = spawnSync(
    npxBin,
    ["--yes", "markdown-link-check", "--config", configPath, ...batch],
    {
      cwd: root,
      encoding: "utf8",
      shell: process.platform === "win32",
      stdio: "inherit",
    },
  );

  if (result.error) {
    console.error(result.error.message);
    process.exit(1);
  }

  if (result.status !== 0) {
    exitCode = result.status ?? 1;
  }
}

process.exit(exitCode);
