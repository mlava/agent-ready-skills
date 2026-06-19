# agent-ready-skills

[Agent Skills](https://www.skills.sh/) for using [**Agent Ready**](https://agent-ready.dev) — the agent-readability scanner that scores any URL against the Vercel Agent Readability Spec, the llmstxt.org standard, and the agent-protocol manifests (MCP server cards, A2A, agents.json, agent-permissions.json, UCP, x402, NLWeb).

Install one of the skills below and your AI agent can run scans, fetch results, and search the Agent Ready docs without any further setup.

Or add all three at once with the whole-repo form:

```bash
npx skills add mlava/agent-ready-skills
```

Browse the rendered docs on skills.sh: <https://www.skills.sh/mlava/agent-ready-skills>

## Skills

### [`agent-ready-api`](skills/agent-ready-api/SKILL.md)

Use the REST API directly. Best when:

- You don't have an MCP host (you're driving a curl / Node / Python script)
- You want the leanest possible dependency surface
- You need a one-shot scan from a CI step, a serverless function, or a notebook

Install:

```bash
npx skills add mlava/agent-ready-skills/skills/agent-ready-api
```

### [`agent-ready-mcp`](skills/agent-ready-mcp/SKILL.md)

Use the MCP server (`agent-ready-mcp` on npm) inside Claude Desktop, Claude Code, Cursor, Cline, Continue, Goose, or any other MCP host. Best when:

- You already have one of those clients running
- You want tool-native invocation — no curl, no fetch wiring
- You want the workflow prompts (`scan`, `interpret_scan`, `remediation_plan`)

Install:

```bash
npx skills add mlava/agent-ready-skills/skills/agent-ready-mcp
```

### [`agent-ready-cli`](skills/agent-ready-cli/SKILL.md)

Use the `agent-ready` command-line client (`agent-ready-scanner` on npm). Best when:

- The agent can run shell commands and you want one command, zero wiring
- You don't want to install an MCP server or write fetch/polling code
- You're scripting — machine-readable `--json` to stdout, distinct exit codes

Install:

```bash
npx skills add mlava/agent-ready-skills/skills/agent-ready-cli
```

## What is Agent Ready?

[Agent Ready](https://agent-ready.dev) runs ~70 checks across four spec families:

- **Vercel Agent Readability Spec** — 15 site-wide + 23 per-page checks (llms.txt, robots.txt, sitemap.xml, sitemap.md, AGENTS.md, JSON-LD, headings, markdown mirrors, content negotiation, code-block language tags, JS-rendering)
- **llmstxt.org** — 10 checks against the llms.txt file format
- **Agent protocols** — MCP server cards (SEP-1649), A2A agent cards, agents.json, agent-permissions.json, UCP, x402, NLWeb
- **Authentication discovery** — RFC 9728 PRM + RFC 8414 AS metadata, WorkOS `auth.md`

Pricing:

| Plan | Price | Pages/scan | Scans | API access |
|---|---|---|---|---|
| Free | $0 / month | 25 | 10 / 30 days | No |
| Pro  | $19 / month | 250 | 50 / month | Yes (10 req/min, 200/day) |

Issue a Pro API key at <https://agent-ready.dev/dashboard/api-keys>.

## Authentication

All three skills expect the API key as the environment variable **`AGENT_READY_API_KEY`** (begins with `ar_live_…`).

- For **`agent-ready-mcp`**, set it inside the MCP client's server config — not your shell — so the spawned `npx` process inherits it.
- For **`agent-ready-api`**, set it in your shell, your `.env`, or wherever the agent picks up environment variables before running curl / fetch.
- For **`agent-ready-cli`**, set it in your shell or `.env`; the CLI reads it automatically (prefer this over the `--api-key` flag, which leaks through shell history).

The `ask` tool/command (NLWeb-style search over Agent Ready's docs) is **public** and works without a key.

## Reference

- Browse on skills.sh: <https://www.skills.sh/mlava/agent-ready-skills>
- Agent Ready homepage: <https://agent-ready.dev>
- API quickstart: <https://agent-ready.dev/quickstart>
- API docs: <https://agent-ready.dev/docs/api>
- OpenAPI 3.1 spec: <https://agent-ready.dev/api/v1/openapi.json>
- MCP server card: <https://agent-ready.dev/.well-known/mcp/server-card.json>
- MCP server source: <https://github.com/mlava/agent-ready-mcp>
- MCP npm: <https://www.npmjs.com/package/agent-ready-mcp>
- CLI source: <https://github.com/mlava/agent-ready-cli>
- CLI npm: <https://www.npmjs.com/package/agent-ready-scanner>
- Auth walkthrough: <https://agent-ready.dev/auth>
- Methodology: <https://agent-ready.dev/methodology>

## License

[MIT](LICENSE)
