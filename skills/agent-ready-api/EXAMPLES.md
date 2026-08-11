# Agent Ready REST API — language examples

The shell flow in `SKILL.md` is the primary reference. These are full
start-and-poll equivalents in other languages — read this file only when you
are scripting in one of them.

## Node / TypeScript

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

// Terminal states are "completed" and "failed" — loop while it is "running",
// never until it equals "completed", or a failed scan spins forever.
let result = start;
while (result.status === "running") {
  await new Promise((r) => setTimeout(r, 2_000));
  result = await fetch(`${base}/scans/${start.id}`, {
    headers: { Authorization: `Bearer ${KEY}` },
  }).then((r) => r.json());
}
if (result.status !== "completed") {
  throw new Error(`Scan ${result.status}: the site could not be read`);
}

console.log(
  "Score:",
  result.vercelScore,
  `https://agent-ready.dev/scan/${result.shareToken}`,
);
```

## Python

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

# Terminal states are "completed" and "failed" — loop while it is "running",
# never until it equals "completed", or a failed scan spins forever.
result = start
while result["status"] == "running":
    time.sleep(2)
    result = requests.get(f"{base}/scans/{start['id']}", headers=h).json()

if result["status"] != "completed":
    raise SystemExit(f"Scan {result['status']}: the site could not be read")

print(
    "Score:",
    result["vercelScore"],
    f"https://agent-ready.dev/scan/{result['shareToken']}",
)
```
