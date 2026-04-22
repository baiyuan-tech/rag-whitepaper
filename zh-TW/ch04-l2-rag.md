---
title: "Chapter 4 — L2 RAG：pgvector + BM25 + RRF 混合檢索"
description: "L2 向量檢索 + 關鍵詞檢索 + RRF 融合排序的實作細節與效能數字"
chapter: 4
part: 2
word_count: 5400
lang: zh-TW
authors:
  - name: 百原科技
    url: https://baiyuan.io
license: CC-BY-NC-4.0
keywords:
  - pgvector
  - BM25
  - RRF
  - HNSW
  - tsvector
  - 混合檢索
  - Chunking
last_updated: 2026-04-20
last_modified_at: '2026-04-22T03:40:36Z'
---





# Chapter 4 — L2 RAG：pgvector + BM25 + RRF 混合檢索

> 向量檢索懂語意、BM25 懂關鍵詞、RRF 不用調權重。把這三樣湊在同一個 PostgreSQL 實例裡，是百原 RAG 的 L2。

## 目錄

- [4.1 為何選 pgvector 而非獨立向量庫](#41-為何選-pgvector-而非獨立向量庫)
- [4.2 Chunking 策略](#42-chunking-策略)
- [4.3 Embedding 模型選擇](#43-embedding-模型選擇)
- [4.4 HNSW 索引調校](#44-hnsw-索引調校)
- [4.5 BM25 全文檢索](#45-bm25-全文檢索)
- [4.6 Reciprocal Rank Fusion](#46-reciprocal-rank-fusion)
- [4.7 Rerank：要不要加](#47-rerank要不要加)

---

## 4.1 為何選 pgvector 而非獨立向量庫

2024 年做技術選型時，我們評比了 5 個選項：

| 方案 | 優點 | 缺點 | 我們的考量 |
|-----|------|------|----------|
| **pgvector** | 與主 DB 同一 Postgres、txn 保證、運維簡單 | 大規模性能稍遜 | ✅ 採用 |
| Pinecone | 託管、無維運 | 額外費用、無 txn | ❌ 費用、廠商鎖定 |
| Qdrant | 開源、Rust 性能好 | 另一套服務要運維 | ❌ 多一個 SPOF |
| Milvus | 超大規模 | K8s 架構重 | ❌ Overkill |
| Weaviate | GraphQL 介面漂亮 | 社群較小 | ❌ 長期風險 |

決定的關鍵是**單點故障**與**運維複雜度**。SaaS 早期階段如果多加一個向量庫服務，任何一端 Down 都會影響使用者。pgvector 把向量儲存併入主 Postgres，有四個直接效益：

1. **原子性**：document 寫入與 embedding 寫入在同一 txn，不會有資料不一致
2. **備份一致**：pg_dump 就備份全部，不用另外管向量庫
3. **權限統一**：RLS 同步覆蓋向量表
4. **JOIN 方便**：`SELECT c.*, e.embedding FROM chunks c JOIN embeddings e USING (chunk_id)` 直接查

缺點是大規模（>1 億向量）時 pgvector HNSW 比 Qdrant 慢約 30%。但我們單租戶通常 10 萬向量以下，離天花板很遠。

## 4.2 Chunking 策略

「如何把文件切成 chunks」是 RAG 最被低估的決策。百原用三套策略依文件類型切換：

### 4.2.1 固定字數 + 重疊窗

最簡單，適用於無結構 txt / 長段落 PDF：

```typescript
function chunkByFixedWindow(text: string, size = 500, overlap = 80): string[] {
  const chunks = [];
  for (let i = 0; i < text.length; i += size - overlap) {
    chunks.push(text.slice(i, i + size));
  }
  return chunks;
}
```

- **size 500**：對 embedding 模型夠短（embeddings-3-small 上限 8,191 token，我們遠低於）
- **overlap 80**：保留語境，避免答案剛好切在邊界

### 4.2.2 結構感知切法（Markdown / HTML）

如果文件是 Markdown 或 HTML，優先依標題切：

```typescript
function chunkByStructure(md: string): Chunk[] {
  const sections = splitByHeadings(md, { maxLevel: 3 });
  return sections.map(s => ({
    content: s.body,
    title_hierarchy: s.ancestors,  // ["Ch 4", "4.2", "4.2.2"]
    token_count: countTokens(s.body),
  }));
}
```

`title_hierarchy` 存成 chunk 欄位，**檢索時可用來做 boosting**（例如 "4.2.2" 命中則順帶顯示 4.2 的標題）。

### 4.2.3 語義切法（Semantic Chunking）

對長篇研究論文、法規條文，用 LLM 做語義邊界判斷：

```text
[PROMPT]
以下文字可能橫跨多個語義主題。請找出主題切換的位置，輸出切點的字元 index。
文字：{text}
輸出格式：JSON array of integers
```

雖然呼叫 LLM 貴，但**一次離線切好終身受益**。我們對 PIF AI 的法規條文用這種切法。

### 4.2.4 Chunk 欄位設計

```sql
CREATE TABLE chunks (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id        UUID NOT NULL,
    document_id      UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    position         INT NOT NULL,            -- 第幾個 chunk
    content          TEXT NOT NULL,
    title_path       TEXT[],                  -- ["Ch 4", "4.2"]
    token_count      INT NOT NULL,
    char_count       INT NOT NULL,
    fts              tsvector GENERATED ALWAYS AS
                     (to_tsvector('zh_parser', content)) STORED,
    meta             JSONB,                   -- 自訂標籤、source_url 片段等
    created_at       TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_chunks_doc ON chunks(document_id, position);
CREATE INDEX idx_chunks_fts ON chunks USING GIN(fts);
```

`fts` 是 `tsvector` **generated column** — 寫入時自動產生，查詢時走 GIN 索引，BM25 所需的關鍵詞檢索靠它。

## 4.3 Embedding 模型選擇

目前使用：

| 模型 | 維度 | 單價（USD / 1M token） | 用途 |
|-----|------|----------------------|------|
| OpenAI `text-embedding-3-small` | 1536 | 0.02 | 預設，中英混合表現佳 |
| OpenAI `text-embedding-3-large` | 3072 | 0.13 | 高精度需求租戶 |
| `BAAI/bge-m3` (self-host) | 1024 | 電費 | 日文／多語言場景 |

幾個實務經驗：

1. **維度不是越大越好**：3072 維比 1536 維精度提升 ~3%，但儲存成本和查詢時間多 100%
2. **中文選 OpenAI 或 BGE-M3 都可**：純中文場景 BGE-M3 稍好，但 OpenAI 中英混合更穩
3. **Embedding 不要省錢混用**：同一 collection 內必須用同一模型，否則餘弦相似度無意義

## 4.4 HNSW 索引調校

pgvector 支援 IVF-Flat 與 HNSW 兩種 ANN 索引。我們全面用 HNSW：

```sql
CREATE INDEX idx_embeddings_hnsw ON embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

兩個參數：

- **m = 16**：每個節點的鄰居數，越大記憶體越多、召回率越高
- **ef_construction = 64**：建索引時的搜索範圍，越大索引越精準、建索引時間越長

查詢時可以調 `ef_search`：

```sql
SET hnsw.ef_search = 40;  -- default 40
SELECT chunk_id, 1 - (embedding <=> $1::vector) AS similarity
FROM embeddings
WHERE tenant_id = $2
ORDER BY embedding <=> $1::vector
LIMIT 20;
```

`ef_search` 越大越精準但越慢。Pilot 階段我們動態調整：

- 低 QPS（< 10 qps）：`ef_search = 100`（精度優先）
- 高 QPS（> 50 qps）：`ef_search = 20`（延遲優先）

## 4.5 BM25 全文檢索

單靠向量檢索有一個致命弱點：**精確詞彙不存在的情境**。例如使用者問「退貨要 7 天嗎？」向量會召回很多「退貨」相關片段，但可能錯過正好寫著「7 天鑑賞期」的那一段（語意相近但用詞不同）。

BM25 全文檢索補這個洞。PostgreSQL 原生 `tsvector` + `tsquery` 加上 `ts_rank` 足以模擬 BM25：

```sql
SELECT chunk_id, ts_rank_cd(fts, q, 32) AS score
FROM chunks, plainto_tsquery('zh_parser', $1) q
WHERE tenant_id = $2 AND fts @@ q
ORDER BY score DESC
LIMIT 20;
```

三個細節：

- **`zh_parser`** 是我們 install 的 PostgreSQL 中文分詞擴充（基於 SCWS）
- **`ts_rank_cd`** 的 flag `32` 表示 `rank / (rank + 1)`，對短 chunk 公平
- **`plainto_tsquery`** 處理使用者輸入的斷詞，防 SQL 注入

### 4.5.1 日文／多語言

日文用 `mecab` 分詞：

```sql
CREATE TEXT SEARCH CONFIGURATION japanese (COPY = simple);
ALTER TEXT SEARCH CONFIGURATION japanese
  ALTER MAPPING FOR word, numword, asciiword, hword
  WITH simple;
-- 實際生產用 PGroonga 或 textsearch_ja 效果更好
```

英文直接用 `english` configuration。多語言租戶在 `chunks.meta.lang` 記錄語系，查詢時挑對應 configuration。

## 4.6 Reciprocal Rank Fusion

有了向量檢索（語意）和 BM25（關鍵詞），如何合併？我們選 **Reciprocal Rank Fusion (RRF)**：

$$
\text{score}(d) = \sum_{r \in R} \frac{1}{k + \text{rank}_r(d)}
$$

其中 $R$ 是每一路的排序結果、$\text{rank}_r(d)$ 是文件 $d$ 在路 $r$ 的排名（從 1 開始），$k = 60$ 是常數。

實作：

```typescript
function rrfFusion(
  vectorResults: { chunk_id: string; rank: number }[],
  bm25Results: { chunk_id: string; rank: number }[],
  k = 60,
): FusedResult[] {
  const scores = new Map<string, number>();
  for (const r of vectorResults) {
    scores.set(r.chunk_id, (scores.get(r.chunk_id) ?? 0) + 1 / (k + r.rank));
  }
  for (const r of bm25Results) {
    scores.set(r.chunk_id, (scores.get(r.chunk_id) ?? 0) + 1 / (k + r.rank));
  }
  return [...scores.entries()]
    .map(([chunk_id, score]) => ({ chunk_id, score }))
    .sort((a, b) => b.score - a.score);
}
```

為什麼選 RRF 而非加權平均？

| 比較項 | RRF | 加權平均 |
|-------|-----|---------|
| 需要調參 | 只有 k（通常 60） | 需調向量 vs BM25 權重 |
| 分數尺度 | 不敏感（用排名） | 必須標準化 |
| 論文支持 | TREC 2009 多次驗證 | 各家各自調 |
| 對 outlier | 魯棒 | 敏感 |

RRF 的核心洞察：**排名比分數穩定**。同一個 chunk 在向量檢索的 cosine 分數是 0.82、在 BM25 的 ts_rank 是 4.7 — 這兩個數不能直接相加；但兩路的 rank（都是「第 2 名」）可以直接用 RRF 公式。

實測 RRF 在百原資料上比純向量檢索 **Recall@10 高 8–12%**，比加權平均（我們反覆調參 2 週的最佳結果）**高 3%**。

## 4.7 Rerank：要不要加

Rerank 是把 top-20 或 top-50 的結果用 cross-encoder（如 Cohere Rerank 或 bge-reranker-v2）精排。這步通常能再提升 Recall@5 約 5–10%，但代價是：

- 每 query 多呼叫一次 Rerank API（成本、延遲）
- self-host reranker 需要 GPU

我們目前**不預設啟用 Rerank**，只對高精度需求的租戶（PIF 法規、金融、醫療）開啟：

```typescript
if (tenant.config.rerank_enabled) {
  const reranked = await cohereRerank({
    query: question,
    documents: fusedResults.slice(0, 50).map(r => r.content),
    top_n: 10,
  });
  return reranked;
}
return fusedResults.slice(0, 10);
```

Ch 12 會討論 Rerank 何時該預設啟用。

---

## 本章要點

- pgvector 選型的關鍵是**減少 SPOF** 與**運維簡化**，不是純性能
- Chunking 有三策略：固定窗 / 結構感知 / 語義切，依文件類型切換
- HNSW 索引的 `ef_search` 支援查詢時動態調整，換取精度 vs 延遲
- BM25 補向量檢索的「精確詞彙」弱點，中文用 `zh_parser`、日文用 `mecab`
- RRF 合併多路檢索，不需調權重、對 outlier 魯棒
- Rerank 不預設啟用，僅高精度需求租戶開啟

## 參考資料

- [pgvector README][pgv]
- [RRF: Cormack et al. 2009][rrf]
- [BGE-M3 Multilingual Embedding][bge-m3]
- [Cohere Rerank API][cohere-rerank]
- [zhparser PostgreSQL Chinese Tokenizer][zhparser]

[pgv]: https://github.com/pgvector/pgvector
[rrf]: https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf
[bge-m3]: https://huggingface.co/BAAI/bge-m3
[cohere-rerank]: https://docs.cohere.com/docs/rerank-overview
[zhparser]: https://github.com/amutu/zhparser

## 修訂記錄

| 日期 | 版本 | 說明 |
|------|------|------|
| 2026-04-20 | v1.0 | 初稿 |

---

**導覽**：[← Ch 3: L1 Wiki](./ch03-l1-wiki.md) · [📖 目次](../README.md) · [Ch 5: L1→L2 Fallback →](./ch05-fallback-economics.md)
