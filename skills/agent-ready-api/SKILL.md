---
name: agent-ready-api
description: Use the Agent Ready REST API to scan any public URL for AI agent-readability against the Vercel Agent Readability Spec, the llmstxt.org standard, and agent-protocol manifests (MCP server cards, A2A, agents.json, agent-permissions.json, UCP, x402, NLWeb). Activates for "scan this site for AI agent-readability", "run an Agent Ready scan on <URL>", "check the Agent Ready score for <URL>", "what's the agent-readability rating for <URL>", or any time the user wants a programmatic readability scan via HTTP. Picks this skill when the user does NOT have the Agent Ready MCP server installed — for MCP, use the `agent-ready-mcp` skill instead.
metadata:
  author: agent-ready
  version: "1.0.0"
  homepage: https://agent-ready.dev
  source: https://github.com/mlava/agent-ready-skills
---

# Agent Ready REST API

The Agent Ready REST API scores any public URL against ~60 checks across the Vercel Agent Readability Spec, the llmstxt.org standard, and the agent-protocol manifests (MCP server cards, A2A agent cards, agents.json, agent-permissions.json, UCP, x402, NLWeb). Use this skill when the user wants to run a scan programmatically without setting up an MCP server — start a scan, poll for results, summarise the highest-impact findings.

## When to use

Activate this skill when the user:

- Asks you to "scan https://example.com for AI agent-readability"
- Says "run an Agent Ready scan on <URL>"
- Asks for "the Agent Ready score for <URL>" or "the agent-readability rating for <URL>"
- References a previous scan id (e.g. `scan_01HXYZ...`) and wants you to fetch or re-interpret it
- Wants a prioritised list of fixes to make a site more visible to AI agents

If the Agent Ready MCP server is already installed in the user's client (Claude Desktop, Cursor, Cline, Continue, Goose), prefer the **`agent-ready-mcp`** skill — same surface, fewer moving parts. Use this skill only when you must talk HTTP directly.

## Step 1: Locate the API key

Agent Ready API access requires a **Pro account**. Work through these scenarios in order:

### A) `AGENT_READY_API_KEY` is already set

```bash
printenv AGENT_READY_API_KEY
```

If it returns a value, you're ready. Skip to Step 2.

### B) The key is in a `.env` file under `AGENT_READY_API_KEY`

```bash
grep '^AGENT_READY_API_KEY=' .env 2>/dev/null
```

If found:

```bash
export AGENT_READY_API_KEY=$(grep '^AGENT_READY_API_KEY=' .env | cut -d= -f2-)
```

### C) The key is in `.env` under a different variable name

Agent Ready API keys start with `ar_live_`:

```bash
grep -E 'ar_live_|agent.ready' .env 2>/dev/null
```

Inspect the output, then export the matching variable as `AGENT_READY_API_KEY`.

### D) No key found — ask the user

Direct the user to <https://agent-ready.dev/dashboard/api-keys> to issue a key (Pro plan required; sign up at <https://agent-ready.dev/pricing>).

> **Exception:** `POST /api/v1/ask` (search the Agent Ready docs) is **public**. If the user only wants to look up methodology / spec definitions, skip the key entirely and jump to Step 5.

**Important:** Once `AGENT_READY_API_KEY` is exported, pass it as the `Authorization: Bearer …` header — never in the URL or query string. Secrets in command-line arguments leak through shell history and process listings.

## Step 2: Start a scan

```bash
curl -X POST https://agent-ready.dev/api/v1/scans \
  -H "Authorization: Bearer $AGENT_READY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

The response returns **immediately** with a scan id and status:

```json
{"id":"scan_01HXYZ...","status":"queued","shareUrl":null}
```

Do **not** try to read a score from this response — it hasn't run yet. Capture `id` and continue.

Optional body fields:

- `pageLimit` (number) — cap the number of pages crawled. Defaults to the tier's limit (250 for Pro). Use a lower value (e.g. `25`) for a fast spot-check.

Pass the user's URL verbatim including scheme, path, and trailing slash. The server normalises internally and rejects private / reserved IPs at the network layer — invalid input surfaces as a clear `invalid_request` 400.

## Step 3: Poll for results

```bash
SCAN_ID="scan_01HXYZ..."

curl https://agent-ready.dev/api/v1/scans/$SCAN_ID \
  -H "Authorization: Bearer $AGENT_READY_API_KEY"
```

Typical wall-clock: **15–60 seconds** for a Pro scan. Poll every 2–3 seconds until `status` flips from `queued`/`running` to `complete`:

```bash
while true; do
  result=$(curl -s https://agent-ready.dev/api/v1/scans/$SCAN_ID \
    -H "Authorization: Bearer $AGENT_READY_API_KEY")
  status=$(echo "$result" | jq -r .status)
  if [ "$status" = "complete" ]; then break; fi
  sleep 3
done
echo "$result" | jq .
```

### Node / TypeScript

```ts
const KEY = process.env.AGENT_READY_API_KEY!;
const base = "https://agent-ready.dev/api/v1";

const start = await fetch(`${base}/scans`, {
  method: "POST",
  headers: {
    Authorization: `Bearer ${KEY}`,
    "Content-Type": "application/json",
  },
  body: JSON.stringify({ url: "https://example.com" }),
}).then((r) => r.json());

let result = start;
while (result.status !== "complete") {
  await new Promise((r) => setTimeout(r, 2_000));
  result = await fetch(`${base}/scans/${start.id}`, {
    headers: { Authorization: `Bearer ${KEY}` },
  }).then((r) => r.json());
}

console.log("Score:", result.score, result.shareUrl);
```

### Python

```python
import os, time, requests

KEY = os.environ["AGENT_READY_API_KEY"]
base = "https://agent-ready.dev/api/v1"
h = {"Authorization": f"Bearer {KEY}"}

start = requests.post(
    f"{base}/scans",
    headers={**h, "Content-Type": "application/json"},
    json={"url": "https://example.com"},
).json()

result = start
while result["status"] != "complete":
    time.sleep(2)
    result = requests.get(f"{base}/scans/{start['id']}", headers=h).json()

print("Score:", result["score"], result["shareUrl"])
```

## Step 4: Summarise the findings

The complete scan response is large (50+ checks). Don't dump raw JSON to the user. Lead with:

1. **Overall score** (0–100) and its **rating band** — `excellent` (90–100), `good` (70–89), `fair` (50–69), `needs_improvement` (0–49). Use `result.score` and `result.rating`.
2. **llms.txt sub-score** if the site has an `llms.txt` (`result.llmstxtScore`).
3. **Top 3–5 highest-impact failing checks.** Look across `result.siteChecks`, `result.pageResults[].pageChecks`, `result.protocolResults`, `result.llmstxtChecks` for `status === "fail"`. Each check entry has `name`, `message`, and `howToFix` — surface those.
4. **One-line next step.** Point the user at `result.shareUrl` for the full breakdown, or offer to draft a remediation plan from the failing checks.

Common response fields:

| Field | Meaning |
|---|---|
| `id` | Scan id |
| `status` | `queued` / `running` / `complete` |
| `score` | Overall 0–100 |
| `rating` | `excellent` / `good` / `fair` / `needs_improvement` |
| `vercelScore` | Vercel Agent Readability Spec sub-score |
| `llmstxtScore` | llmstxt.org compliance sub-score |
| `siteChecks` | Site-wide check results (S1–S15) |
| `pageResults` | Per-page check results (P1–P23) |
| `protocolResults` | Protocol manifest check results (C1–C12) |
| `llmstxtChecks` | llms.txt check results (L1–L10) |
| `pagesScanned` | Pages actually crawled |
| `pagesDiscovered` | Pages found via sitemap/discovery |
| `shareUrl` | Human-readable result page on agent-ready.dev |

## Step 5: Search the Agent Ready docs (no key required)

For "what is X" questions about a check, spec, or term, use the public `/api/v1/ask` endpoint:

```bash
curl -X POST https://agent-ready.dev/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"what does the L8 check measure?"}'
```

Returns Schema.org-typed search results over Agent Ready's methodology, glossary, and guides. No API key required.

Use this when the user asks definitional questions ("what is `llms.txt`?", "explain check S5", "what does NLWeb mean?") without giving you a URL to scan.

## Endpoints reference

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `POST` | `/api/v1/scans` | Bearer | Start a new scan |
| `GET`  | `/api/v1/scans/{id}` | Bearer | Get scan status / result |
| `GET`  | `/api/v1/scans` | Bearer | List past scans (most-recent first) |
| `POST` | `/api/v1/ask` | none | Search Agent Ready docs (NLWeb) |
| `POST` | `/api/v1/mcp` | Bearer | MCP streamable-http endpoint (use `agent-ready-mcp` skill instead) |

Full OpenAPI 3.1 spec: <https://agent-ready.dev/api/v1/openapi.json>

## Rate limits

- **10 requests per minute** per key
- **200 requests per day** per key
- Shared budget across REST and MCP surfaces

429 responses carry a `Retry-After` header (seconds). Honor it — don't busy-loop.

## Errors and recovery

| Status | Error code | What it means | Fix |
|---|---|---|---|
| 400 | `invalid_request` | Malformed body or invalid URL | The JSON body names the offending field |
| 401 | `unauthorized` / `invalid_token` | Missing or bad Bearer token | Re-check `AGENT_READY_API_KEY`; the `WWW-Authenticate` header points at the auth discovery doc |
| 403 | `subscription_required` | Authenticated but the account is on the Free tier | Direct user to <https://agent-ready.dev/pricing> |
| 429 | `rate_limited` | Over the per-minute or per-day limit | Wait `Retry-After` seconds and retry |
| 503 | `service_unavailable` | Backend (DB / scanner) is down | Retry later or escalate to the Agent Ready team |

## Discovery and reference URLs

- API quickstart: <https://agent-ready.dev/quickstart>
- API docs: <https://agent-ready.dev/docs/api>
- OpenAPI 3.1 spec: <https://agent-ready.dev/api/v1/openapi.json>
- Auth walkthrough (WorkOS `auth.md` aligned): <https://agent-ready.dev/auth>
- Dashboard (issue keys): <https://agent-ready.dev/dashboard/api-keys>
- Pricing: <https://agent-ready.dev/pricing>
- Methodology (all 60 checks): <https://agent-ready.dev/methodology>
- Discovery hints: `<https://agent-ready.dev/.well-known/oauth-protected-resource>`, `<https://agent-ready.dev/.well-known/mcp/server-card.json>`
