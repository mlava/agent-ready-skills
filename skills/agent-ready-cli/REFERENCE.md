# Agent Ready CLI — reference

Occasional-lookup material. The scan/get/list/ask workflow lives in `SKILL.md`.

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

Common API errors surfaced on stderr: `unauthorized` (missing/invalid key — check `AGENT_READY_API_KEY`), `subscription_required` (Free tier — see https://agent-ready.dev/pricing), `rate_limited` (10 req/min, 200 req/day per key — wait and retry), `invalid_request` (the message names the offending field).

## Discovery and reference URLs

- npm package: https://www.npmjs.com/package/agent-ready-scanner
- CLI source: https://github.com/mlava/agent-ready-cli
- API quickstart: https://agent-ready.dev/quickstart
- OpenAPI 3.1 spec: https://agent-ready.dev/api/v1/openapi.json
- Methodology (all 60 checks): https://agent-ready.dev/methodology
- Dashboard (issue keys): https://agent-ready.dev/dashboard/api-keys
- Pricing: https://agent-ready.dev/pricing
