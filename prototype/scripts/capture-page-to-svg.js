/**
 * Capture http://localhost:3000/ as a vector SVG (paths, text, shapes — no raster).
 * Uses dom-to-svg in the browser. Run: node scripts/capture-page-to-svg.js
 * Ensure the dev server is running: npm run dev
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import puppeteer from 'puppeteer';
import { writeFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

const URL = 'http://localhost:3000/';
const VIEWPORT = { width: 1280, height: 900 };
const OUT_PATH = join(__dirname, '..', 'public', 'localhost-3000-capture.svg');
const BROWSER_BUNDLE = join(__dirname, 'dom-to-svg-browser.js');

async function main() {
  const browser = await puppeteer.launch({ headless: 'new' });
  try {
    const page = await browser.newPage();
    await page.setViewport(VIEWPORT);
    await page.goto(URL, { waitUntil: 'networkidle0', timeout: 15000 });
    await page.evaluate(() => window.scrollTo(0, 0));
    await new Promise((r) => setTimeout(r, 800));

    await page.addScriptTag({ path: BROWSER_BUNDLE });

    const svgString = await page.evaluate(async () => {
      if (typeof window.capturePageToVectorSvg !== 'function') {
        throw new Error('capturePageToVectorSvg not found');
      }
      return await window.capturePageToVectorSvg();
    });

    writeFileSync(OUT_PATH, svgString, 'utf8');
    const match = svgString.match(/<svg[^>]*\s+width="([^"]+)"\s+height="([^"]+)"/) ||
      svgString.match(/viewBox="[^"]*\s+([^\s"]+)\s+([^"]+)"/);
    const dims = match ? ` ${match[1]}×${match[2]}` : '';
    console.log(`Written (vector): ${OUT_PATH}${dims}`);
  } finally {
    await browser.close();
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
