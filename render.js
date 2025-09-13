#!/usr/bin/env node
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import puppeteer from 'puppeteer';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function printUsageAndExit() {
  console.error('Usage: node render.js <data.json> <template.html> <output.pdf>');
  process.exit(1);
}

function getArg(index, fallback) {
  return process.argv[index] || fallback;
}

function flattenObject(nested, prefix = '', result = {}) {
  if (nested === null || nested === undefined) {
    return result;
  }
  const isObject = typeof nested === 'object' && !Array.isArray(nested);
  if (!isObject) {
    result[prefix] = nested;
    return result;
  }
  for (const [key, value] of Object.entries(nested)) {
    const nextPrefix = prefix ? `${prefix}.${key}` : key;
    flattenObject(value, nextPrefix, result);
  }
  return result;
}

function applyTemplate(html, data) {
  const flat = flattenObject(data);
  // Also support top-level direct keys without dot notation
  for (const [key, value] of Object.entries(data)) {
    if (!(key in flat)) flat[key] = value;
  }
  return html.replace(/\{([^}]+)\}/g, (match, key) => {
    const trimmedKey = String(key).trim();
    const replacement = flat.hasOwnProperty(trimmedKey) ? (flat[trimmedKey] ?? '') : '';
    return String(replacement);
  });
}

async function render() {
  const dataPath = getArg(2);
  const templatePath = getArg(3);
  const outputPath = getArg(4);
  if (!dataPath || !templatePath || !outputPath) {
    printUsageAndExit();
  }

  const [dataJson, templateHtml] = await Promise.all([
    fs.readFile(path.resolve(__dirname, dataPath), 'utf8'),
    fs.readFile(path.resolve(__dirname, templatePath), 'utf8'),
  ]);

  const data = JSON.parse(dataJson);
  const filledHtml = applyTemplate(templateHtml, data);

  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });
  try {
    const page = await browser.newPage();
    await page.setContent(filledHtml, { waitUntil: 'networkidle0' });
    await page.emulateMediaType('print');
    await page.pdf({
      path: path.resolve(__dirname, outputPath),
      format: 'Letter',
      printBackground: true,
      margin: { top: '12mm', right: '12mm', bottom: '12mm', left: '12mm' },
    });
  } finally {
    await browser.close();
  }
}

render().catch((error) => {
  console.error('Render failed:', error);
  process.exit(1);
});

