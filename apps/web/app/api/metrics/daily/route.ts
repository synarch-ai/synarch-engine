// Server-side route for the dashboard's metrics (codex P2).
// The browser calls this same-origin route, and this handler calls the backend with
// SYNARCH_API_KEY, which only the server reads (it is never NEXT_PUBLIC_*), so the
// key never reaches client code. It forwards one fixed GET endpoint and nothing else.
export const dynamic = 'force-dynamic';

const DEFAULT_API_URL = 'http://127.0.0.1:8000';

export async function GET(): Promise<Response> {
  const base = (process.env.SYNARCH_API_URL || DEFAULT_API_URL).replace(/\/+$/, '');
  const headers: Record<string, string> = { accept: 'application/json' };
  const apiKey = process.env.SYNARCH_API_KEY;
  if (apiKey) headers['x-api-key'] = apiKey;

  try {
    const upstream = await fetch(`${base}/api/v1/metrics/daily`, { headers, cache: 'no-store' });
    return new Response(await upstream.text(), {
      status: upstream.status,
      headers: {
        'content-type': upstream.headers.get('content-type') ?? 'application/json',
        'cache-control': 'no-store',
      },
    });
  } catch {
    return new Response(
      JSON.stringify({ error: { code: 'UPSTREAM_UNAVAILABLE', message: 'Metrics backend is unreachable.' } }),
      { status: 502, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } },
    );
  }
}
