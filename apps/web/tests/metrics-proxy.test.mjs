// codex P2: with API_KEY set on the backend, the dashboard must still load metrics,
// and the key must stay on the server (never in browser code).
// Run: cd apps/web && npm test   (Node >= 22.18 strips the route's TypeScript types)
import assert from 'node:assert/strict';
import { once } from 'node:events';
import { readFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { test } from 'node:test';

const page = new URL('../app/dashboard/page.tsx', import.meta.url);
const route = new URL('../app/api/metrics/daily/route.ts', import.meta.url);

test('dashboard fetches metrics from the same-origin server route, never the backend directly', async () => {
  const src = await readFile(page, 'utf8');
  assert.match(src, /fetch\(\s*['"]\/api\/metrics\/daily['"]/);
  assert.doesNotMatch(src, /localhost:8000|127\.0\.0\.1:8000/);
  assert.doesNotMatch(src, /api[_-]?key/i);
});

test('metrics route calls the backend with the server-only API key', async (t) => {
  const seen = [];
  const backend = createServer((req, res) => {
    seen.push({ url: req.url, key: req.headers['x-api-key'] });
    if (req.headers['x-api-key'] !== 'server-secret') {
      res.writeHead(401, { 'content-type': 'application/json' }).end('{"error":{"code":"UNAUTHORIZED"}}');
      return;
    }
    res.writeHead(200, { 'content-type': 'application/json' }).end('{"metrics":[]}');
  });
  backend.listen(0, '127.0.0.1');
  await once(backend, 'listening');
  t.after(() => backend.close());

  process.env.SYNARCH_API_URL = `http://127.0.0.1:${backend.address().port}`;
  process.env.SYNARCH_API_KEY = 'server-secret';
  const { GET } = await import(route.href);
  const res = await GET();

  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { metrics: [] });
  assert.deepEqual(seen, [{ url: '/api/v1/metrics/daily', key: 'server-secret' }]);
});

test('metrics route source never reads a browser-exposed (NEXT_PUBLIC_) key', async () => {
  const src = await readFile(route, 'utf8');
  assert.doesNotMatch(src, /NEXT_PUBLIC_[A-Z_]*KEY/);
  assert.doesNotMatch(src, /^['"]use client['"]/m);
});
