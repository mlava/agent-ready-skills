# Agent Ready REST API — language examples

The bash/curl flow in `SKILL.md` is the primary reference. These are full
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

let result = start;
while (result.status !== "complete") {
  await new Promise((r) => setTimeout(r, 2_000));
  result = await fetch(`${base}/scans/${start.id}`, {
    headers: { Authorization: `Bearer ${KEY}` },
  }).then((r) => r.json());
}

console.log("Score:", result.score, result.shareUrl);
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

result = start
while result["status"] != "complete":
    time.sleep(2)
    result = requests.get(f"{base}/scans/{start['id']}", headers=h).json()

print("Score:", result["score"], result["shareUrl"])
```
