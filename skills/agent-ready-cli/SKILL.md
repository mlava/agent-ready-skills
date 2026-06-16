---
name: agent-ready-cli
description: Use the Agent Ready command-line client to scan any public URL for AI agent-readability against the Vercel Agent Readability Spec, the llmstxt.org standard, and agent-protocol manifests (MCP server cards, A2A, agents.json, agent-permissions.json, UCP, x402, NLWeb). Activates for "scan this site with the agent-ready CLI", "run agent-ready scan {URL} in the terminal", "agent-ready get {id}", "agent-ready list", "agent-ready ask {question}", or any time the user wants a one-command terminal scan with no fetch wiring and no MCP install. Pick this skill when the agent can run shell commands. For raw HTTP, use the `agent-ready-api` skill; for MCP-native tool calls, use `agent-ready-mcp`.
metadata:
  author: agent-ready
  version: "1.0.0"
  homepage: https://agent-ready.dev
  source: https://github.com/mlava/agent-ready-skills
---

# Agent Ready CLI

The Agent Ready CLI (`agent-ready`, published to npm as [`agent-ready-scanner`](https://www.npmjs.com/package/agent-ready-scanner)) scores any public URL against ~60 checks across the Vercel Agent Readability Spec, the llmstxt.org standard, and the agent-protocol manifests (MCP server cards, A2A, agents.json, agent-permissions.json, UCP, x402, NLWeb). It's a thin zero-dependency wrapper over the hosted [agent-ready.dev REST API](https://agent-ready.dev/api/v1/openapi.json) — no scanning happens locally.

Use this skill when you can run shell commands and want the fewest moving parts: one command starts a scan, polls to completion, and prints a summary — no HTTP wiring, no MCP client config. It's also the right fit for scripting, because it emits machine-readable JSON to stdout and uses distinct exit codes.

## When to use

Activate this skill when the user:

- Asks you to "scan https://example.com with the agent-ready CLI" or "run an Agent Ready scan in the terminal"
- Wants a quick one-shot scan and you have a shell available
- References a previous scan id and wants `agent-ready get <id>`
- Wants to list past scans (`agent-ready list`) or search the docs (`agent-ready ask`)
- Is scripting / piping scan results into other tools (`--json`, exit codes)

Choose a sibling skill instead when:

- You need raw HTTP control or there's no shell — use **`agent-ready-api`**.
- The user runs an MCP client (Claude Desktop, Cursor, Cline, Continue, Goose) and wants tool-native calls — use **`agent-ready-mcp`**.

All three talk to the same REST API and share one rate-limit budget.

## Step 1: Confirm Node and reach the CLI

The CLI needs **Node.js ≥ 20.10**. No install is required — run it on demand with `npx`:

```bash
npx agent-ready-scanner --version
```

If the user will use it repeatedly, install it globally (this provides the `agent-ready` command):

```bash
npm install -g agent-ready-scanner
agent-ready --version
```

> **Naming gotcha:** the npm package is `agent-ready-scanner` — the bare
> `agent-ready` name is blocked by npm's similarity policy. The installed
> **command** is still `agent-ready`. With `npx`, you must use the package
> name: `npx agent-ready-scanner …`.

Throughout this skill, `agent-ready <cmd>` means the installed command; substitute `npx agent-ready-scanner <cmd>` if it isn't installed globally.

## Step 2: Locate the API key

`scan`, `get`, and `list` require a **Pro API key** (keys start with `ar_live_`). `ask` is **public** — skip to Step 6 if that's all the user needs.

Work through these in order:

### A) `AGENT_READY_API_KEY` is already set

```bash
printenv AGENT_READY_API_KEY
```

If it returns a value, the CLI picks it up automatically. Skip to Step 3.

### B) The key is in a `.env` file

```bash
grep -E 'ar_live_|AGENT_READY_API_KEY' .env 2>/dev/null
```

If found under `AGENT_READY_API_KEY`:

```bash
export AGENT_READY_API_KEY=$(grep '^AGENT_READY_API_KEY=' .env | cut -d= -f2-)
```

If it's under a different variable name, export the matching value as `AGENT_READY_API_KEY`.

### C) No key found — ask the user

Direct the user to <https://agent-ready.dev/dashboard/api-keys> to issue a key (Pro plan required; sign up at <https://agent-ready.dev/pricing>).

**Important:** prefer the `AGENT_READY_API_KEY` env var over the `--api-key` flag. A key passed as a command-line argument leaks through shell history and process listings.

## Step 3: Scan a URL

```bash
agent-ready scan https://example.com
```

This starts the scan, polls until it completes (typically 15–60 s), and prints a formatted readability summary — score, rating band, llms.txt sub-score, and the highest-impact failing checks.

Pass the URL verbatim, including scheme, path, and trailing slash. The server normalises internally and rejects private / reserved IPs at the network layer; bad input surfaces as a clear usage or `invalid_request` error.

Useful options:

| Option | Description |
|---|---|
| `--page-limit <n>` | Cap pages crawled (e.g. `25` for a fast spot-check) |
| `--no-wait` | Queue the scan and print its id without polling |
| `--poll-interval <s>` | Seconds between status polls (default 2) |
| `--timeout <s>` | Max seconds to wait for completion (default 120) |
| `--json` | Emit the raw scan result as JSON (stdout) |

```bash
agent-ready scan https://example.com --page-limit 25
agent-ready scan https://example.com --no-wait      # queue only, prints the id
agent-ready scan https://example.com --json | jq '.score'
```

When you use `--no-wait`, capture the printed scan id and fetch it later with `get` (Step 4).

## Step 4: Fetch a scan by id

```bash
agent-ready get V1StGXR8_Z
agent-ready get V1StGXR8_Z --json
```

Use this for scans started with `--no-wait`, or when the user references an existing scan id.

## Step 5: List past scans

```bash
agent-ready list
agent-ready list --limit 5
agent-ready list --cursor 2026-05-30T00:00:00.000Z   # next page
```

Newest first. The `--cursor` value comes from the previous page's output.

## Step 6: Search the docs (no key required)

```bash
agent-ready ask "how is the score calculated?"
agent-ready ask "what does check S4 do?" --type checks
agent-ready ask "summarize the llms.txt requirements" --mode summarize
```

`ask` runs a natural-language (NLWeb) search over Agent Ready's own methodology, check registry, and supported specs. Public — no API key. Use it for definitional questions ("what is `llms.txt`?", "explain check L8") when there's no URL to scan.

## Step 7: Summarise findings, don't dump raw JSON

The default (non-`--json`) output is already a human summary — relay it. If you used `--json`, lead with:

1. **Overall score** (0–100) and its **rating band** — `excellent` (90–100), `good` (70–89), `fair` (50–69), `needs_improvement` (0–49).
2. **llms.txt sub-score** if the site has an `llms.txt`.
3. **Top 3–5 highest-impact failing checks** (`status: "fail"`). Each has `name`, `message`, and `howToFix` — surface those, not the raw JSON.
4. **One-line next step** — point at the `shareUrl` for the full breakdown, or offer to draft a remediation plan.

Check categories: **S1–S15** site-wide · **P1–P23** per-page · **L1–L10** llmstxt.org · **C1–C12** protocol manifests.

## Global options

| Option | Description |
|---|---|
| `--json` | Output raw JSON instead of formatted text |
| `--api-key <key>` | Override `AGENT_READY_API_KEY` (prefer the env var) |
| `--base-url <url>` | Override `AGENT_READY_API_URL` (e.g. local dev) |
| `--no-color` | Disable coloured output (`NO_COLOR` is also honoured) |
| `-h, --help` | Show help |
| `-v, --version` | Show version |

`--json` output goes to **stdout**; progress and errors go to **stderr**, so you can pipe JSON safely.

## Environment variables

| Variable | Default | Purpose |
|---|---|---|
| `AGENT_READY_API_KEY` | — | Pro API key for `scan` / `get` / `list` |
| `AGENT_READY_API_URL` | `https://agent-ready.dev` | API base URL |
| `AGENT_READY_SCAN_TIMEOUT_MS` | `120000` | Overall scan wait budget |
| `AGENT_READY_GET_TIMEOUT_MS` | `10000` | Per-request timeout |

## Exit codes

| Code | Meaning | Recovery |
|---|---|---|
| `0` | Success | — |
| `1` | API error, scan failed, or scan timed out | Read the stderr message. For a timeout, re-run `get <id>` — the scan may still finish server-side. |
| `2` | Usage error (bad arguments) | Fix the command; `agent-ready --help` lists valid options. |

Common API errors surfaced on stderr: `unauthorized` (missing/invalid key — check `AGENT_READY_API_KEY`), `subscription_required` (Free tier — see <https://agent-ready.dev/pricing>), `rate_limited` (10 req/min, 200 req/day per key — wait and retry), `invalid_request` (the message names the offending field).

## Discovery and reference

- npm package: <https://www.npmjs.com/package/agent-ready-scanner>
- CLI source: <https://github.com/mlava/agent-ready-cli>
- API quickstart: <https://agent-ready.dev/quickstart>
- OpenAPI 3.1 spec: <https://agent-ready.dev/api/v1/openapi.json>
- Methodology (all 60 checks): <https://agent-ready.dev/methodology>
- Dashboard (issue keys): <https://agent-ready.dev/dashboard/api-keys>
- Pricing: <https://agent-ready.dev/pricing>
