#!/usr/bin/env node
/**
 * Verifica contraste WCAG dos pares texto/fundo definidos em src/index.css.
 * Falha (exit 1) se algum par ficar abaixo do mínimo.
 *
 * Uso: node scripts/check-contrast.mjs
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const css = readFileSync(join(here, "..", "src", "index.css"), "utf8");

const DARK_MARKER = "@media (prefers-color-scheme: dark)";
const darkStart = css.indexOf(DARK_MARKER);
if (darkStart === -1) {
  console.error("Não encontrei o bloco de dark mode em index.css");
  process.exit(1);
}

function tokensIn(block) {
  const map = {};
  for (const m of block.matchAll(/--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})\b/g)) {
    map[`--${m[1]}`] = m[2];
  }
  return map;
}

const light = tokensIn(css.slice(0, darkStart));
const darkBlock = css.slice(darkStart);
const dark = { ...light, ...tokensIn(darkBlock) };

const PAIRS = [
  ["--text-h", "--bg", 4.5],
  ["--text", "--bg", 4.5],
  ["--text-secondary", "--bg", 4.5],
  ["--text-muted", "--bg", 4.5],
  ["--text-h", "--surface", 4.5],
  ["--text-muted", "--surface", 4.5],
  ["--accent", "--bg", 4.5],
  ["--positive", "--bg", 4.5],
  ["--negative", "--bg", 4.5],
];

function channel(v) {
  const c = v / 255;
  return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
}

function luminance(hex) {
  const n = parseInt(hex.slice(1), 16);
  return (
    0.2126 * channel((n >> 16) & 255) +
    0.7152 * channel((n >> 8) & 255) +
    0.0722 * channel(n & 255)
  );
}

function ratio(a, b) {
  const [l1, l2] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (l1 + 0.05) / (l2 + 0.05);
}

let failures = 0;
let checks = 0;

for (const [themeName, theme] of [
  ["light", light],
  ["dark", dark],
]) {
  for (const [fgKey, bgKey, min] of PAIRS) {
    const fg = theme[fgKey];
    const bg = theme[bgKey];
    if (!fg || !bg) {
      console.error(`✗ ${themeName}: token ausente (${fgKey} ou ${bgKey})`);
      failures++;
      continue;
    }
    const value = ratio(fg, bg);
    checks++;
    if (value < min) {
      console.error(
        `✗ ${themeName}: ${fgKey} sobre ${bgKey} = ${value.toFixed(2)}:1 (mín ${min})`,
      );
      failures++;
    }
  }
}

if (failures > 0) {
  console.error(`\n${failures} par(es) reprovado(s) de ${checks}.`);
  process.exit(1);
}

console.log(`OK — ${checks} pares de contraste ≥ 4.5:1 (light + dark).`);
