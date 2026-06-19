# Agent Ready REST API — reference

Occasional-lookup material. The day-to-day workflow, rate limits, and error
recovery live in `SKILL.md`.

## Endpoints

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `POST` | `/api/v1/scans` | Bearer | Start a new scan |
| `GET`  | `/api/v1/scans/{id}` | Bearer | Get scan status / result |
| `GET`  | `/api/v1/scans` | Bearer | List past scans (most-recent first) |
| `POST` | `/api/v1/ask` | none | Search Agent Ready docs (NLWeb) |
| `POST` | `/api/v1/mcp` | Bearer | MCP streamable-http endpoint (use `agent-ready-mcp` skill instead) |

## Discovery and reference URLs

- API quickstart: https://agent-ready.dev/quickstart
- API docs: https://agent-ready.dev/docs/api
- OpenAPI 3.1 spec: https://agent-ready.dev/api/v1/openapi.json
- Auth walkthrough (WorkOS `auth.md` aligned): https://agent-ready.dev/auth
- Dashboard (issue keys): https://agent-ready.dev/dashboard/api-keys
- Pricing: https://agent-ready.dev/pricing
- Methodology (~70 checks): https://agent-ready.dev/methodology
- Discovery hints: `https://agent-ready.dev/.well-known/oauth-protected-resource`, `https://agent-ready.dev/.well-known/mcp/server-card.json`
