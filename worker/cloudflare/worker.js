/**
 * pocket-mew — minimal Cloudflare Worker relay (demo)
 *
 * Bind a KV namespace as TOUCH_QUEUE (key: "latest" or a small list).
 * For production: add auth headers, rate limits, and a real queue.
 *
 * Routes:
 *   POST /touch  — hardware pushes an event
 *   GET  /poll   — host consumes one event
 *   GET  /peek   — host inspects without consuming
 */

const QUEUE_KEY = "events";

async function readQueue(env) {
  const raw = await env.TOUCH_QUEUE.get(QUEUE_KEY);
  if (!raw) return [];
  try {
    const arr = JSON.parse(raw);
    return Array.isArray(arr) ? arr : [];
  } catch {
    return [];
  }
}

async function writeQueue(env, arr) {
  // keep last 20 events max
  const trimmed = arr.slice(-20);
  await env.TOUCH_QUEUE.put(QUEUE_KEY, JSON.stringify(trimmed));
}

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/$/, "") || "/";

    // Optional shared-secret gate (set WORKER_TOKEN in Worker env)
    if (env.WORKER_TOKEN) {
      const auth = request.headers.get("authorization") || "";
      const token = auth.startsWith("Bearer ") ? auth.slice(7) : "";
      const q = url.searchParams.get("token") || "";
      if (token !== env.WORKER_TOKEN && q !== env.WORKER_TOKEN) {
        return json({ error: "unauthorized" }, 401);
      }
    }

    if (request.method === "POST" && path === "/touch") {
      let body;
      try {
        body = await request.json();
      } catch {
        return json({ error: "invalid json" }, 400);
      }
      const event = {
        type: body.type || "touch",
        peak_raw: body.peak_raw ?? 0,
        duration_ms: body.duration_ms ?? 0,
        curve: Array.isArray(body.curve) ? body.curve : [],
        ts: Date.now(),
      };
      const q = await readQueue(env);
      q.push(event);
      await writeQueue(env, q);
      return json({ ok: true });
    }

    if (request.method === "GET" && path === "/poll") {
      const q = await readQueue(env);
      if (!q.length) return json({ event: null });
      const event = q.shift();
      await writeQueue(env, q);
      return json({ event });
    }

    if (request.method === "GET" && path === "/peek") {
      const q = await readQueue(env);
      return json({ events: q, latest: q[q.length - 1] || null });
    }

    return json({
      service: "pocket-mew-relay",
      routes: ["POST /touch", "GET /poll", "GET /peek"],
    });
  },
};
