# Agent Ready MCP — client install configs

`SKILL.md` shows the Claude Desktop config inline. This file has the rest.

**Credential rule (applies to every snippet below):** `ar_live_...` and
`${AGENT_READY_API_KEY}` are **placeholders**. Never substitute the user's real
key into a config you generate or print. Emit the placeholder and have the user
paste their own key, or reference the `AGENT_READY_API_KEY` environment variable
so the secret never enters your output or the conversation history.

## A) Claude Desktop

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

## B) Claude Code

```bash
claude mcp add agent-ready \
  -e AGENT_READY_API_KEY=ar_live_... \
  -- npx -y agent-ready-mcp@latest
```

## C) Cursor / Cline / Continue

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

## D) Goose Desktop

Install from the extensions directory at https://block.github.io/goose/ — search "Agent Ready". Goose prompts for `AGENT_READY_API_KEY` during install. CLI:

```bash
goose configure  # add Command-line Extension, then:
# command: npx -y agent-ready-mcp@latest
# env:     AGENT_READY_API_KEY=ar_live_...
```

## E) Remote streamable-HTTP transport (no npm)

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

This bypasses `npx`/Node entirely — useful for sandboxed environments. The server card at https://agent-ready.dev/.well-known/mcp/server-card.json describes the same surface.

## Verify the install

After the client restarts, the server should advertise three tools (`scan_site`, `get_scan`, `ask`) and three prompts (`scan`, `interpret_scan`, `remediation_plan`). If it doesn't show up, check the client's MCP log for the `agent-ready` entry — most issues are typos in the config path, a missing API key env var, or stale `npx` cache (`rm -rf ~/.npm/_npx` and retry).
