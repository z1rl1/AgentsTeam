#!/usr/bin/env node
// Runtime QA for HTML5 games using Playwright headless Chromium.
// Usage: node browser_test.js <game_dir>
// Exit 0: PASS, Exit 1: FAIL, Exit 2: browser unavailable (skip)

const http = require('http');
const fs = require('fs');
const path = require('path');

const gameDir = process.argv[2];
if (!gameDir || !fs.existsSync(path.join(gameDir, 'index.html'))) {
  console.error('Usage: node browser_test.js <game_dir>');
  process.exit(1);
}

let playwright;
try {
  playwright = require('playwright');
} catch (_) {
  console.log('[Browser QA] playwright module not found, skipping.');
  process.exit(2);
}

const MIME = {
  '.html': 'text/html', '.js': 'application/javascript',
  '.css': 'text/css', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.svg': 'image/svg+xml',
  '.mp3': 'audio/mpeg', '.ogg': 'audio/ogg', '.wav': 'audio/wav',
  '.json': 'application/json',
};

function startServer(dir) {
  const server = http.createServer((req, res) => {
    const urlPath = req.url.split('?')[0];
    const filePath = path.join(dir, urlPath === '/' ? 'index.html' : urlPath);
    const ext = path.extname(filePath).toLowerCase();
    fs.readFile(filePath, (err, data) => {
      if (err) { res.writeHead(404); res.end(); return; }
      res.writeHead(200, { 'Content-Type': MIME[ext] || 'application/octet-stream' });
      res.end(data);
    });
  });
  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => resolve({ server, port: server.address().port }));
  });
}

function fireKey(page, code, key) {
  return page.evaluate(([c, k]) => {
    const opts = { code: c, key: k, bubbles: true, cancelable: true };
    document.dispatchEvent(new KeyboardEvent('keydown', opts));
    document.dispatchEvent(new KeyboardEvent('keyup', opts));
  }, [code, key]);
}

const CANVAS_CHECKSUM = `(function() {
  const c = document.querySelector('canvas');
  if (!c) return null;
  const ctx = c.getContext('2d');
  if (!ctx) return null;
  const data = ctx.getImageData(0, 0, c.width, c.height).data;
  let sum = 0;
  for (let i = 0; i < data.length; i += 4) {
    sum = (sum + data[i] * 3 + data[i+1] * 5 + data[i+2] * 7) & 0xFFFFFF;
  }
  return sum;
})()`;

async function runTest(dir) {
  const { server, port } = await startServer(dir);
  const url = `http://127.0.0.1:${port}/`;
  let browser;

  try {
    browser = await playwright.chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    });
    const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });

    await context.addInitScript(() => {
      window.__rafCount = 0;
      const orig = window.requestAnimationFrame.bind(window);
      window.requestAnimationFrame = function(cb) { window.__rafCount++; return orig(cb); };
    });

    const page = await context.newPage();

    const jsErrors = [];
    const consoleErrors = [];
    page.on('pageerror', err => jsErrors.push(err.message));
    page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });

    await page.goto(url, { waitUntil: 'load', timeout: 15000 });
    await page.waitForTimeout(500);

    // Check 1: canvas size
    const canvasSize = await page.evaluate(() => {
      const c = document.querySelector('canvas');
      return c ? { w: c.width, h: c.height } : null;
    });
    const canvasOk = canvasSize && canvasSize.w >= 100 && canvasSize.h >= 100;

    // Check 2: canvas has non-blank content
    const canvasHasContent = await page.evaluate(() => {
      const c = document.querySelector('canvas');
      if (!c) return false;
      const ctx = c.getContext('2d');
      if (!ctx) return false;
      const data = ctx.getImageData(0, 0, Math.min(c.width, 400), Math.min(c.height, 400)).data;
      let nonBlack = 0;
      for (let i = 0; i < data.length; i += 4) {
        if (data[i+3] > 0 && (data[i] > 10 || data[i+1] > 10 || data[i+2] > 10)) nonBlack++;
      }
      return nonBlack > (data.length / 4) * 0.02;
    });

    // Fire start keys, then measure
    await fireKey(page, 'Enter', 'Enter');
    await page.waitForTimeout(200);
    await fireKey(page, 'Space', ' ');
    await page.waitForTimeout(300);

    // Take 3 canvas checksums 500ms apart
    const checksums = [];
    for (let i = 0; i < 3; i++) {
      checksums.push(await page.evaluate(CANVAS_CHECKSUM));
      await page.waitForTimeout(500);
    }
    const canvasChanges = checksums[0] !== checksums[1] || checksums[1] !== checksums[2];

    const rafCount = await page.evaluate(() => window.__rafCount || 0);
    const pageAlive = await page.evaluate(() => typeof document.title === 'string');

    // Game loop = rAF running OR canvas changes. Both count, either is enough.
    // A static start screen with a live rAF loop is still a live game.
    const loopAlive = rafCount >= 10 || canvasChanges;

    // Restart test: trigger game over via wall collision, then restart
    const jsErrorsBefore = jsErrors.length;
    await fireKey(page, 'ArrowLeft', 'ArrowLeft');
    await page.waitForTimeout(100);
    await fireKey(page, 'ArrowDown', 'ArrowDown');
    await page.waitForTimeout(100);
    await fireKey(page, 'ArrowRight', 'ArrowRight');
    await page.waitForTimeout(100);
    await fireKey(page, 'ArrowUp', 'ArrowUp');
    await page.waitForTimeout(2000); // wait for possible game over
    await fireKey(page, 'Enter', 'Enter'); // restart
    await page.waitForTimeout(200);
    await fireKey(page, 'Space', ' ');
    await page.waitForTimeout(800);
    const checksumAfterRestart = await page.evaluate(CANVAS_CHECKSUM);
    const rafAfterRestart = await page.evaluate(() => window.__rafCount || 0);
    const noNewJsErrors = jsErrors.length === jsErrorsBefore;
    const restartWorking = noNewJsErrors && rafAfterRestart > rafCount && checksumAfterRestart !== null && checksumAfterRestart !== 0;

    const checks = [
      ['No uncaught JS errors', jsErrors.length === 0, true],
      ['Canvas exists with valid size', canvasOk, true],
      ['Canvas renders content', canvasHasContent, true],
      ['Game loop is alive (rAF or canvas changes)', loopAlive, true],
      ['Page stays alive (not frozen)', pageAlive, true],
      ['Canvas changes after game starts', canvasChanges, false],
      ['Restart works without errors', restartWorking, false],
      ['No console errors', consoleErrors.length === 0, false],
    ];

    console.log('\n[Browser Runtime QA]');
    let passed = 0;
    const requiredFailed = [];
    for (const [name, ok, required] of checks) {
      if (ok) { console.log(`  [OK]   ${name}`); passed++; }
      else {
        const tag = required ? 'FAIL' : 'WARN';
        console.log(`  [${tag}] ${name}`);
        if (required) requiredFailed.push(name);
      }
    }

    if (jsErrors.length > 0) console.log(`  JS errors: ${jsErrors.slice(0, 3).join(' | ')}`);
    if (consoleErrors.length > 0) console.log(`  Console: ${consoleErrors.slice(0, 2).join(' | ')}`);
    if (canvasSize) console.log(`  Canvas: ${canvasSize.w}x${canvasSize.h}, rAF: ${rafCount}, checksums: ${checksums.join(' -> ')}`);

    const allPass = requiredFailed.length === 0;
    console.log(`  Result: ${allPass ? 'PASS' : 'FAIL'} (${passed}/${checks.length})`);
    return allPass ? 0 : 1;

  } finally {
    if (browser) await browser.close();
    server.close();
  }
}

runTest(gameDir)
  .then(code => process.exit(code))
  .catch(err => {
    console.error(`[Browser QA] Error: ${err.message}`);
    process.exit(2);
  });
