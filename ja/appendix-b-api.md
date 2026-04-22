---
title: "付録 B — 公開 API 規格"
lang: ja
license: CC-BY-NC-4.0
last_modified_at: '2026-04-22T03:40:36Z'
---





# 付録 B — 公開 API 規格

## Base URL

- 外部：`https://rag.baiyuan.io`
- Docker 内部：`http://rag:18001`

## 認証

すべての `/api/v1/*` に 2 ヘッダ必須：

```http
X-RAG-API-Key: <secret>
X-Tenant-ID: <uuid>
```

## エンドポイント一覧

| メソッド | パス | 用途 |
|:-------|-----|------|
| GET | `/health` | ヘルスチェック、認証不要 |
| POST | `/api/v1/ask` | メイン Q&A |
| GET | `/api/v1/knowledge-bases` | KB 一覧 |
| POST | `/api/v1/knowledge-bases` | KB 作成 |
| DELETE | `/api/v1/knowledge-bases/:id` | KB 削除 |
| GET | `/api/v1/documents` | 文書一覧 |
| POST | `/api/v1/documents/text` | テキスト貼付 |
| POST | `/api/v1/documents/url` | URL 取込 |
| POST | `/api/v1/documents/file` | ファイルアップロード |
| DELETE | `/api/v1/documents/:id` | 文書削除 |
| POST | `/api/v1/knowledge-bases/:id/wiki/compile` | Wiki コンパイル |
| POST | `/api/v1/knowledge-bases/:id/wiki/lint` | Lint |
| GET | `/api/v1/knowledge-bases/:id/wiki` | Wiki 一覧 |
| GET | `/api/v1/knowledge-bases/:id/wiki/:slug` | Wiki 取得 |
| POST | `/api/v1/wiki/patch` | GEO 修復注入 |

## POST /api/v1/ask

### Request

```json
{
  "question": "返品は何日？",
  "knowledge_base_id": "optional-uuid",
  "session_id": "optional-conv-id",
  "stream": false,
  "temperature": 0,
  "max_tokens": 800
}
```

### Response（非ストリーム）

```json
{
  "status": "success",
  "data": {
    "answer": "...",
    "sources": [{"id":"wiki:return-policy","title":"返品","relevance":1.0}],
    "response_time": 0.32,
    "from_wiki": true,
    "tokens": {"prompt":0,"completion":0},
    "timestamp": "2026-04-20T08:00:00Z"
  }
}
```

### SSE

`stream:true` または `Accept: text/event-stream`：

```text
event: start
data: {"conversation_id":"uuid","intent":"knowledge"}

event: delta
data: {"content":"私たちの"}

event: done
data: {"answer":"...","sources":[...]}
```

## エラーコード

| HTTP | 意味 |
|:-----|------|
| 400 | パラメータ不足 |
| 401 | API key 欠落 / 不正 |
| 403 | テナント存在せず |
| 404 | リソース無し |
| 429 | レート制限 |
| 500 | 内部エラー |

## レート制限

デフォルト 600 req/min/tenant、企業版要相談。

## 例

### cURL

```bash
curl -X POST https://rag.baiyuan.io/api/v1/ask \
  -H "X-RAG-API-Key: $KEY" \
  -H "X-Tenant-ID: $TENANT" \
  -H "Content-Type: application/json" \
  -d '{"question":"保証期間は？","session_id":"u1"}'
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
  body: JSON.stringify({question:'保証期間は？'}),
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
    json={'question':'保証期間は？', 'stream': True},
) as r:
    for line in r.iter_lines():
        print(line)
```
