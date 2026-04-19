import type { ParseResponse, ParsedParams, ResearchResult } from "./types";

const BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function parseQuery(query: string): Promise<ParseResponse> {
  const r = await fetch(`${BASE}/parse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!r.ok) throw new Error(`/parse failed: ${r.status} ${await r.text()}`);
  return r.json();
}

export async function runResearch(params: ParsedParams): Promise<ResearchResult> {
  const r = await fetch(`${BASE}/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ params }),
  });
  if (!r.ok) throw new Error(`/research failed: ${r.status} ${await r.text()}`);
  return r.json();
}
