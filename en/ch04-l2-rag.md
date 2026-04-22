---
title: "Chapter 4 — L2 RAG: pgvector + BM25 + RRF"
chapter: 4
lang: en
license: CC-BY-NC-4.0
last_modified_at: '2026-04-20T09:17:36Z'
---




# Chapter 4 — L2 RAG: pgvector + BM25 + RRF

> Vector retrieval understands meaning. BM25 understands keywords. RRF needs no tuning. We put all three in one PostgreSQL instance.

## 4.1 Why pgvector Over Standalone Vector DBs

| Option | Pros | Cons | Chosen |
|--------|------|------|--------|
| **pgvector** | Same Postgres, txn, simple ops | Weaker at extreme scale | ✅ |
| Pinecone | Managed, zero-ops | Extra cost, vendor lock-in | ❌ |
| Qdrant | Open-source, Rust-fast | One more service | ❌ |
| Milvus | Massive scale | K8s heavy | ❌ |
| Weaviate | GraphQL nice | Smaller community | ❌ |

Deciding factors: single-point-of-failure and ops complexity. pgvector collapses storage into main Postgres, gaining atomicity, unified backup, shared RLS, JOIN-friendly schema. Trade-off is ~30% lower performance at >100M vectors — irrelevant for our per-tenant scale.

## 4.2 Chunking Strategies

Three strategies by document type:

### 4.2.1 Fixed Window + Overlap

```typescript
function chunkByFixedWindow(text: string, size = 500, overlap = 80) {
  const chunks = [];
  for (let i = 0; i < text.length; i += size - overlap) {
    chunks.push(text.slice(i, i + size));
  }
  return chunks;
}
```

### 4.2.2 Structure-Aware (Markdown/HTML)

Split by headings, preserve `title_hierarchy` (e.g., `["Ch 4", "4.2"]`) in chunk metadata for later boosting.

### 4.2.3 Semantic Chunking

For long research papers and legal text, ask an LLM to locate topic boundaries. Expensive but one-time cost per document.

### 4.2.4 Chunk Schema

```sql
CREATE TABLE chunks (
    id               UUID PRIMARY KEY,
    tenant_id        UUID NOT NULL,
    document_id      UUID NOT NULL REFERENCES documents(id),
    position         INT NOT NULL,
    content          TEXT NOT NULL,
    title_path       TEXT[],
    token_count      INT NOT NULL,
    fts              tsvector GENERATED ALWAYS AS
                     (to_tsvector('zh_parser', content)) STORED,
    meta             JSONB,
    created_at       TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_chunks_fts ON chunks USING GIN(fts);
```

Generated `fts` column powers BM25 via GIN index.

## 4.3 Embedding Model Choice

| Model | Dim | USD/1M tokens | Use |
|-------|-----|--------------|-----|
| `text-embedding-3-small` (OpenAI) | 1536 | 0.02 | Default |
| `text-embedding-3-large` (OpenAI) | 3072 | 0.13 | High precision |
| `BAAI/bge-m3` (self-host) | 1024 | Electricity | Japanese / multilingual |

Lessons: dim >1536 adds ~3% accuracy but doubles storage/query; never mix models in the same collection.

## 4.4 HNSW Index Tuning

```sql
CREATE INDEX idx_embeddings_hnsw ON embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

Dynamic `ef_search` at query time:

- Low QPS (<10): `ef_search = 100` (precision)
- High QPS (>50): `ef_search = 20` (latency)

## 4.5 BM25 via tsvector

Pure vector retrieval misses exact-keyword queries. PostgreSQL's `tsvector` + `ts_rank_cd` approximates BM25:

```sql
SELECT chunk_id, ts_rank_cd(fts, q, 32) AS score
FROM chunks, plainto_tsquery('zh_parser', $1) q
WHERE tenant_id = $2 AND fts @@ q
ORDER BY score DESC LIMIT 20;
```

- `zh_parser` for Chinese tokenization
- `ts_rank_cd` flag 32 is fair to short chunks
- `plainto_tsquery` sanitizes user input

Japanese uses `mecab`; English uses `english` configuration. Multilingual tenants store `lang` in `chunks.meta` and switch accordingly.

## 4.6 Reciprocal Rank Fusion

$$
\text{score}(d) = \sum_{r \in R} \frac{1}{k + \text{rank}_r(d)}
$$

Implementation:

```typescript
function rrfFusion(vec, bm25, k = 60) {
  const scores = new Map();
  for (const r of vec) scores.set(r.chunk_id, (scores.get(r.chunk_id) ?? 0) + 1/(k + r.rank));
  for (const r of bm25) scores.set(r.chunk_id, (scores.get(r.chunk_id) ?? 0) + 1/(k + r.rank));
  return [...scores].map(([id, s]) => ({id, s})).sort((a,b) => b.s - a.s);
}
```

RRF > weighted average because:

| Compare | RRF | Weighted Avg |
|---------|-----|--------------|
| Tuning | Only k (usually 60) | Vector vs BM25 weights |
| Scale sensitivity | Uses rank, not scores | Requires normalization |
| Paper support | TREC 2009 validated | Ad hoc |
| Outlier robustness | High | Low |

Measured: RRF lifts Recall@10 by 8–12% over pure vector, and 3% over our best-tuned weighted average.

## 4.7 Rerank: When to Enable

Rerank (Cohere / bge-reranker-v2) adds 5–10% Recall@5 at cost of +250 ms latency and per-query API spend. Default off; enable per-tenant for high-precision domains (legal, medical, regulatory):

```typescript
if (tenant.config.rerank_enabled) {
  const reranked = await cohereRerank({
    query: question, documents: fused.slice(0, 50).map(r => r.content), top_n: 10,
  });
  return reranked;
}
```

Ch 12 discusses whether to make rerank default-on.

---

## Key Takeaways

- pgvector chosen for reduced SPOF and ops simplicity, not peak performance
- Three chunking strategies (fixed / structure / semantic) by document type
- Dynamic `ef_search` trades precision vs latency at query time
- BM25 via PostgreSQL `tsvector` covers the keyword gap vector retrieval leaves
- RRF fuses multiple retrieval paths without weight tuning
- Rerank tenant-opt-in for high-precision domains

## References

- [pgvector][pgv] · [RRF paper][rrf] · [BGE-M3][bge] · [Cohere Rerank][rerank]

[pgv]: https://github.com/pgvector/pgvector
[rrf]: https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf
[bge]: https://huggingface.co/BAAI/bge-m3
[rerank]: https://docs.cohere.com/docs/rerank-overview

---

**Navigation**: [← Ch 3](./ch03-l1-wiki.md) · [📖 Contents](./README.md) · [Ch 5 →](./ch05-fallback-economics.md)
