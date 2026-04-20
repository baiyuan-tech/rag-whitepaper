---
title: "第 4 章 — L2 RAG: pgvector + BM25 + RRF"
chapter: 4
lang: ja
license: CC-BY-NC-4.0
last_modified_at: '2026-04-20T09:10:35Z'
---



# 第 4 章 — L2 RAG: pgvector + BM25 + RRF

> ベクトルは意味、BM25 はキーワード、RRF は調整不要。3 つを同一 PostgreSQL に収める。

## 4.1 なぜ pgvector か

| 選択肢 | 利点 | 欠点 | 採用 |
|-------|------|------|------|
| **pgvector** | 同一 Postgres、txn、運用簡易 | 超大規模で性能劣り | ✅ |
| Pinecone | マネージド | 追加費用、ベンダーロック | ❌ |
| Qdrant | OSS、Rust 高速 | 別サービス | ❌ |
| Milvus | 大規模 | K8s 重い | ❌ |
| Weaviate | GraphQL | コミュニティ小 | ❌ |

決め手：SPOF 削減と運用シンプル。pgvector は atomic txn、統一バックアップ、RLS 共有、JOIN 便利。1 億超ベクトルで 30% 性能劣るが、テナント規模で無関係。

## 4.2 Chunking 戦略

### 4.2.1 固定窓 + 重複

```typescript
function chunkByFixedWindow(text, size = 500, overlap = 80) {
  const chunks = [];
  for (let i = 0; i < text.length; i += size - overlap) {
    chunks.push(text.slice(i, i + size));
  }
  return chunks;
}
```

### 4.2.2 構造感知（Markdown / HTML）

見出しで分割し `title_hierarchy` を chunk metadata に保存。

### 4.2.3 意味切り

長編論文、法規文に LLM で境界判定。

### 4.2.4 スキーマ

```sql
CREATE TABLE chunks (
    id UUID PRIMARY KEY, tenant_id UUID, document_id UUID,
    position INT, content TEXT, title_path TEXT[],
    token_count INT,
    fts tsvector GENERATED ALWAYS AS (to_tsvector('zh_parser', content)) STORED,
    meta JSONB, created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_chunks_fts ON chunks USING GIN(fts);
```

## 4.3 Embedding モデル

| モデル | 次元 | USD/1M | 用途 |
|-------|------|--------|------|
| OpenAI 3-small | 1536 | 0.02 | デフォルト |
| OpenAI 3-large | 3072 | 0.13 | 高精度 |
| BGE-M3 | 1024 | 電気代 | 日本語、多言語 |

次元増で精度 +3%、コスト倍。コレクション内でのモデル混用不可。

## 4.4 HNSW 調整

```sql
CREATE INDEX idx_embeddings_hnsw ON embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

クエリ時 `ef_search` 動的調整：低 QPS で 100、高 QPS で 20。

## 4.5 BM25 via tsvector

```sql
SELECT chunk_id, ts_rank_cd(fts, q, 32) AS score
FROM chunks, plainto_tsquery('zh_parser', $1) q
WHERE tenant_id = $2 AND fts @@ q
ORDER BY score DESC LIMIT 20;
```

中国語 `zh_parser`、日本語 `mecab`、英語 `english`。多言語テナントは `chunks.meta.lang` で切替。

## 4.6 Reciprocal Rank Fusion

$$
\text{score}(d) = \sum_{r \in R} \frac{1}{k + \text{rank}_r(d)}
$$

```typescript
function rrfFusion(vec, bm25, k = 60) {
  const scores = new Map();
  for (const r of vec) scores.set(r.chunk_id, (scores.get(r.chunk_id) ?? 0) + 1/(k + r.rank));
  for (const r of bm25) scores.set(r.chunk_id, (scores.get(r.chunk_id) ?? 0) + 1/(k + r.rank));
  return [...scores].map(([id, s]) => ({id, s})).sort((a,b) => b.s - a.s);
}
```

加重平均より RRF：調整最小、スケール非依存、TREC 2009 実証、外れ値にロバスト。

実測：純ベクトルより Recall@10 +8–12%、2 週調整の加重平均より +3%。

## 4.7 Rerank

Rerank（Cohere / bge-reranker-v2）で Recall@5 +5–10%、+250 ms。デフォルト OFF、高精度テナント（法務、医療、規制）のみ ON。

```typescript
if (tenant.config.rerank_enabled) {
  const reranked = await cohereRerank({
    query: question, documents: fused.slice(0, 50).map(r => r.content), top_n: 10,
  });
  return reranked;
}
```

---

## 本章のポイント

- pgvector 選定の軸は SPOF 削減と運用簡易、ピーク性能ではない
- 3 つの chunking 戦略を文書タイプで切替
- `ef_search` をクエリ時に動的調整
- BM25 がベクトル検索のキーワード欠落を補う
- RRF は多路融合の調整不要手法
- Rerank はデフォルト OFF、高精度テナントのみ有効化

---

**ナビゲーション**：[← 第 3 章](./ch03-l1-wiki.md) · [📖 目次](./README.md) · [第 5 章 →](./ch05-fallback-economics.md)
