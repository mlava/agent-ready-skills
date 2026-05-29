---
name: agent-ready-mcp
description: Install and use the Agent Ready MCP server to scan any URL for AI agent-readability via MCP tool calls. Activates for "install agent-ready mcp", "set up agent-ready in Claude Desktop / Cursor / Cline / Goose / Continue", "add agent-ready as an MCP tool", "scan this site via agent-ready", "run scan_site / get_scan / ask via MCP". Pick this skill when the user wants tool-native access to Agent Ready — no curl, no fetch wiring. For direct REST access without MCP, use the `agent-ready-api` skill instead.
metadata:
  author: agent-ready
  version: "1.0.0"
  homepage: https://agent-ready.dev
  source: https://github.com/mlava/agent-ready-skills
---

# Agent Ready MCP server

The Agent Ready MCP server exposes the ~60-check agent-readability scan as MCP tools. Install once and your agent can run scans, fetch previous results, and search the Agent Ready docs through MCP-native tool calls — no HTTP wiring required.

This skill covers two distinct phases:

1. **Install and configure** the server in the user's MCP client (Claude Desktop, Claude Code, Cursor, Cline, Continue, Goose, or any other streamable-HTTP / stdio MCP host).
2. **Use** the tools and prompts the server exposes once it's running.

The server is published to npm as [`agent-ready-mcp`](https://www.npmjs.com/package/agent-ready-mcp); source at <https://github.com/mlava/agent-ready-mcp>.

## When to use

Activate this skill when the user:

- Asks you to "install agent-ready" or "add agent-ready" as an MCP server in any client
- Says "set up agent-ready in Claude Desktop / Cursor / Cline / Continue / Goose"
- After install: asks you to "scan <URL>" or "run the agent-ready scan" with the MCP tools available
- References the tools `scan_site`, `get_scan`, `ask`, or the prompts `scan`, `interpret_scan`, `remediation_plan`

If the user does **not** have an MCP client and just wants to call the REST API with curl / fetch / requests, use the **`agent-ready-api`** skill instead.

## Step 1: Get an API key

Agent Ready API access requires a **Pro account**. Issue a key at <https://agent-ready.dev/dashboard/api-keys> (sign up at <https://agent-ready.dev/pricing> if needed). Keys begin with `ar_live_…`.

The `ask` MCP tool is **public** and works without a key — it queries Agent Ready's own docs. The other tools (`scan_site`, `get_scan`) require the key.

## Step 2: Install the server

Pick the snippet for the user's MCP client.

### A) Claude Desktop

Edit the config file:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "agent-ready": {
      "command": "npx",
      "args": ["-y", "agent-ready-mcp@latest"],
      "env": {
        "AGENT_READY_API_KEY": "ar_live_..."
      }
    }
  }
}
```

Quit and reopen Claude Desktop.

### B) Claude Code

```bash
claude mcp add agent-ready \
  -e AGENT_READY_API_KEY=ar_live_... \
  -- npx -y agent-ready-mcp@latest
```

### C) Cursor / Cline / Continue

Same shape as Claude Desktop — add to the client's MCP config (path varies by client):

```json
{
  "mcpServers": {
    "agent-ready": {
      "command": "npx",
      "args": ["-y", "agent-ready-mcp@latest"],
      "env": { "AGENT_READY_API_KEY": "ar_live_..." }
    }
  }
}
```

### D) Goose Desktop

Install from the extensions directory at <https://block.github.io/goose/> — search "Agent Ready". Goose prompts for `AGENT_READY_API_KEY` during install. CLI:

```bash
goose configure  # add Command-line Extension, then:
# command: npx -y agent-ready-mcp@latest
# env:     AGENT_READY_API_KEY=ar_live_...
```

### E) Remote streamable-HTTP transport (no npm)

For clients that speak the streamable-HTTP MCP transport, point directly at the hosted endpoint instead of running the stdio wrapper:

```json
{
  "mcpServers": {
    "agent-ready": {
      "transport": "streamable-http",
      "url": "https://agent-ready.dev/api/v1/mcp",
      "headers": {
        "Authorization": "Bearer ${AGENT_READY_API_KEY}"
      }
    }
  }
}
```

This bypasses `npx`/Node entirely — useful for sandboxed environments. The server card at <https://agent-ready.dev/.well-known/mcp/server-card.json> describes the same surface.

### Verify the install

After the client restarts, the server should advertise three tools (`scan_site`, `get_scan`, `ask`) and three prompts (`scan`, `interpret_scan`, `remediation_plan`). If it doesn't show up, check the client's MCP log for the `agent-ready` entry — most issues are typos in the config path, a missing API key env var, or stale `npx` cache (`rm -rf ~/.npm/_npx` and retry).

## Step 3: Pick the right tool

| Tool | Use when |
|---|---|
| **`scan_site`** | User wants a **fresh scan** of a URL. Takes `url` (required) and optional `pageLimit`. |
| **`get_scan`** | User references an **existing scan id** (e.g. `scan_01HXYZ...`) or asks you to re-fetch a previous scan. |
| **`ask`** | User asks a **definitional** question about a check, spec, or term ("what is `llms.txt`?", "explain check L8") — no URL involved. **No API key required.** |

For end-to-end workflows that combine these, prefer the **prompts** the server already wires up — don't reconstruct the workflow with raw tool calls:

| Prompt | Workflow |
|---|---|
| `scan` | Fresh scan + high-level summary |
| `interpret_scan` | Plain-English explanation of a scan's findings |
| `remediation_plan` | Prioritised fix-it doc. Optional `focus`: `"seo"` or `"agents"` |

If the user describes a flow like "scan and summarise", "explain this scan", or "give me a fix-it plan from this scan", invoke the matching prompt by name.

## Step 4: Pass the URL verbatim

For `scan_site` and `get_scan`, pass the input exactly as the user gave it — scheme, path, trailing slash, all of it. The server normalises internally (lowercases the host, strips fragments) and will reject private / reserved IPs at the network layer, so invalid URLs surface as a clear `invalid_request` error from the tool.

## Step 5: Handle the "running" placeholder

`scan_site` polls the hosted API for up to ~60 seconds. If the scan hasn't completed by then, the tool returns:

```json
{
  "id": "abc1234567",
  "status": "running",
  "pollUrl": "/api/v1/scans/abc1234567",
  "message": "Scan still running after the local poll deadline. Call get_scan with this id to fetch the final result."
}
```

Tell the user the scan is in progress, surface the id, and offer to call `get_scan` with that id when they're ready. **Do not** loop `get_scan` automatically — wait for the user.

## Step 6: Summarise findings, don't dump raw JSON

The completed result has 50+ check entries across four categories. Lead with:

1. **Overall agent-readability score** (0–100) and rating band (Excellent / Good / Fair / Needs Improvement)
2. **llms.txt sub-score** if the site has an `llms.txt`
3. **Top 3–5 highest-impact failing checks** (`status: "fail"` in `details`). Each check has `name`, `message`, and `howToFix` — surface those, not the raw JSON.
4. **One-line next step** — point at `shareUrl` for the full breakdown, or offer to invoke `remediation_plan` for a structured fix-it doc.

Common check categories:

- **S1–S15** — site-wide (llms.txt, robots.txt, sitemaps, AGENTS.md, HTTPS, OpenAPI)
- **P1–P23** — per-page (meta tags, JSON-LD, headings, markdown mirrors, content negotiation, code-block language, JS-rendering dependency)
- **L1–L10** — llmstxt.org compliance
- **C1–C12** — protocol manifests (MCP server cards, A2A, agents.json, agent-permissions.json, UCP, x402, NLWeb)

## Errors and recovery

- **`unauthorized` / 401** — `AGENT_READY_API_KEY` missing or invalid. Verify the env var is set in the MCP client config (not just your shell).
- **`subscription_required` / 403** — key valid but the account is on the Free tier. Send the user to <https://agent-ready.dev/pricing>.
- **`rate_limited` / 429** — 10 req/min, 200 req/day per key. The response carries `Retry-After`.
- **`invalid_request` / 400** — usually a malformed URL. The error message names the offending field.

## Discovery and reference

- Server source: <https://github.com/mlava/agent-ready-mcp>
- npm package: <https://www.npmjs.com/package/agent-ready-mcp>
- MCP server card: <https://agent-ready.dev/.well-known/mcp/server-card.json>
- API quickstart: <https://agent-ready.dev/quickstart>
- Auth walkthrough: <https://agent-ready.dev/auth>
- Methodology (all 60 checks): <https://agent-ready.dev/methodology>
- Dashboard (issue keys): <https://agent-ready.dev/dashboard/api-keys>
