---
title: "附錄 B — 公開 API 規格節錄"
description: "百原 RAG Platform 公開 API 精簡規格"
chapter: B
part: 6
lang: zh-TW
license: CC-BY-NC-4.0
last_updated: 2026-04-20
last_modified_at: '2026-04-22T03:40:36Z'
---





# 附錄 B — 公開 API 規格節錄

本附錄節錄百原 RAG Platform 對外 REST API 的主要端點。完整規格隨版本發布於 <https://rag.baiyuan.io/docs>。

## Base URL

- 外網：`https://rag.baiyuan.io`
- Docker 內網：`http://rag:18001`

## 認證

所有 `/api/v1/*` 端點需要兩個 header：

```http
X-RAG-API-Key: <secret>
X-Tenant-ID: <uuid>
```

## 端點總覽

| 方法 | 路徑 | 說明 |
|:----:|-----|------|
| GET | `/health` | 健康檢查，無需認證 |
| POST | `/api/v1/ask` | 主要問答 |
| GET | `/api/v1/knowledge-bases` | 列出 KB |
| POST | `/api/v1/knowledge-bases` | 建立 KB |
| DELETE | `/api/v1/knowledge-bases/:id` | 刪除 KB |
| GET | `/api/v1/documents` | 列出文件 |
| POST | `/api/v1/documents/text` | 貼文字 |
| POST | `/api/v1/documents/url` | URL 匯入 |
| POST | `/api/v1/documents/file` | 檔案上傳 |
| DELETE | `/api/v1/documents/:id` | 刪除文件 |
| POST | `/api/v1/knowledge-bases/:id/wiki/compile` | 編譯 Wiki |
| POST | `/api/v1/knowledge-bases/:id/wiki/lint` | Lint |
| GET | `/api/v1/knowledge-bases/:id/wiki` | 列 Wiki 頁 |
| GET | `/api/v1/knowledge-bases/:id/wiki/:slug` | 查 Wiki 頁 |
| POST | `/api/v1/wiki/patch` | GEO 修復注入專用 |

## POST /api/v1/ask

### Request

```json
{
  "question": "退貨要幾天？",
  "knowledge_base_id": "optional-uuid",
  "session_id": "optional-conv-id",
  "stream": false,
  "temperature": 0,
  "max_tokens": 800,
  "system_prompt": "optional"
}
```

### Response（非串流）

```json
{
  "status": "success",
  "data": {
    "answer": "...",
    "sources": [
      {"id": "wiki:return-policy", "title": "退貨政策", "relevance": 1.0}
    ],
    "response_time": 0.32,
    "from_wiki": true,
    "tokens": {"prompt": 0, "completion": 0},
    "timestamp": "2026-04-20T08:00:00Z"
  }
}
```

### 串流模式（SSE）

`stream: true` 或 `Accept: text/event-stream`：

```text
event: start
data: {"conversation_id":"uuid","intent":"knowledge"}

event: delta
data: {"content":"我們的"}

event: done
data: {"answer":"...","sources":[...]}
```

## 錯誤碼

| HTTP | 意義 |
|:----:|------|
| 400 | 缺必要參數 / `X-Tenant-ID` 格式錯 |
| 401 | `X-RAG-API-Key` 缺或錯 |
| 403 | 租戶不存在 / 停用 |
| 404 | 資源不存在 |
| 429 | Rate limit |
| 500 | 內部錯誤 |

## 速率限制

- 預設：600 req / min / tenant
- 企業版可調整

## 範例：cURL

```bash
curl -X POST https://rag.baiyuan.io/api/v1/ask \
  -H "X-RAG-API-Key: $KEY" \
  -H "X-Tenant-ID: $TENANT" \
  -H "Content-Type: application/json" \
  -d '{"question":"保固多久？","session_id":"u1"}'
```

## 範例：TypeScript

```typescript
const res = await fetch('https://rag.baiyuan.io/api/v1/ask', {
  method: 'POST',
  headers: {
    'X-RAG-API-Key': process.env.RAG_KEY!,
    'X-Tenant-ID': process.env.TENANT!,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ question: '保固多久？' }),
});
const { data } = await res.json();
console.log(data.answer);
```

## 範例：Python（SSE）

```python
import httpx

with httpx.stream('POST', 'https://rag.baiyuan.io/api/v1/ask',
    headers={
        'X-RAG-API-Key': key,
        'X-Tenant-ID': tenant,
        'Accept': 'text/event-stream',
    },
    json={'question': '保固多久？', 'stream': True},
) as r:
    for line in r.iter_lines():
        print(line)
```
