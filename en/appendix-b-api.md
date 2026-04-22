---
title: "Appendix B — Public API Specification"
lang: en
license: CC-BY-NC-4.0
last_modified_at: '2026-04-20T09:17:36Z'
---




# Appendix B — Public API Specification

## Base URL

- Public: `https://rag.baiyuan.io`
- Docker internal: `http://rag:18001`

## Authentication

Every `/api/v1/*` call requires:

```http
X-RAG-API-Key: <secret>
X-Tenant-ID: <uuid>
```

## Endpoints

| Method | Path | Purpose |
|:-------|------|---------|
| GET | `/health` | Liveness; no auth |
| POST | `/api/v1/ask` | Main Q&A |
| GET | `/api/v1/knowledge-bases` | List KBs |
| POST | `/api/v1/knowledge-bases` | Create KB |
| DELETE | `/api/v1/knowledge-bases/:id` | Delete KB |
| GET | `/api/v1/documents` | List documents |
| POST | `/api/v1/documents/text` | Paste text |
| POST | `/api/v1/documents/url` | URL import |
| POST | `/api/v1/documents/file` | File upload |
| DELETE | `/api/v1/documents/:id` | Delete doc |
| POST | `/api/v1/knowledge-bases/:id/wiki/compile` | Compile Wiki |
| POST | `/api/v1/knowledge-bases/:id/wiki/lint` | Lint |
| GET | `/api/v1/knowledge-bases/:id/wiki` | List Wiki pages |
| GET | `/api/v1/knowledge-bases/:id/wiki/:slug` | Get Wiki page |
| POST | `/api/v1/wiki/patch` | GEO repair patch injection |

## POST /api/v1/ask

### Request

```json
{
  "question": "How many days for return?",
  "knowledge_base_id": "optional-uuid",
  "session_id": "optional-conv-id",
  "stream": false,
  "temperature": 0,
  "max_tokens": 800,
  "system_prompt": "optional"
}
```

### Response (non-stream)

```json
{
  "status": "success",
  "data": {
    "answer": "...",
    "sources": [{"id":"wiki:return-policy","title":"Return Policy","relevance":1.0}],
    "response_time": 0.32,
    "from_wiki": true,
    "tokens": {"prompt":0,"completion":0},
    "timestamp": "2026-04-20T08:00:00Z"
  }
}
```

### SSE Streaming

`stream:true` or `Accept: text/event-stream`:

```text
event: start
data: {"conversation_id":"uuid","intent":"knowledge"}

event: delta
data: {"content":"Our"}

event: done
data: {"answer":"...","sources":[...]}
```

## Error Codes

| HTTP | Meaning |
|:-----|---------|
| 400 | Missing parameter / bad `X-Tenant-ID` |
| 401 | Missing / invalid `X-RAG-API-Key` |
| 403 | Tenant not found / disabled |
| 404 | Resource not found |
| 429 | Rate limited |
| 500 | Internal error |

## Rate Limit

600 req/min/tenant default; enterprise negotiable.

## Examples

### cURL

```bash
curl -X POST https://rag.baiyuan.io/api/v1/ask \
  -H "X-RAG-API-Key: $KEY" \
  -H "X-Tenant-ID: $TENANT" \
  -H "Content-Type: application/json" \
  -d '{"question":"Warranty duration?","session_id":"u1"}'
```

### TypeScript

```typescript
const res = await fetch('https://rag.baiyuan.io/api/v1/ask', {
  method: 'POST',
  headers: {
    'X-RAG-API-Key': process.env.RAG_KEY!,
    'X-Tenant-ID': process.env.TENANT!,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({question:'Warranty duration?'}),
});
const { data } = await res.json();
console.log(data.answer);
```

### Python (SSE)

```python
import httpx
with httpx.stream('POST', 'https://rag.baiyuan.io/api/v1/ask',
    headers={'X-RAG-API-Key': key, 'X-Tenant-ID': tenant,
             'Accept': 'text/event-stream'},
    json={'question':'Warranty duration?', 'stream': True},
) as r:
    for line in r.iter_lines():
        print(line)
```
