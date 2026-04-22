---
title: "付録 A — 用語集"
lang: ja
license: CC-BY-NC-4.0
last_modified_at: '2026-04-20T09:17:36Z'
---




# 付録 A — 用語集

`*` 印は百原造語。英字順。

## A–F

- **Answer Cache**：Redis キャッシュ、`sha256(normalize(q)+tenant+kb)` → answer、TTL 600s
- **AXP** *：AI-ready eXchange Page、GEO 核心
- **BM25**：キーワード検索採点（`ts_rank_cd` で近似）
- **Brand Entity**：`brand_entities` の Organization / Service / Person レコード
- **ChainPoll** *：LLM 複数呼び出し多数決で幻覚検知ノイズ削減
- **Chunk**：最小検索単位、通常 500 token
- **ClaimReview**：Schema.org 型、主張真偽標示
- **Degraded Mode**：圧力下降格状態
- **Document**：KB の原データ単位
- **Embedding**：テキスト → ベクトル、デフォルト 1536 次元
- **Fallback**：L1 miss 時の L2 遷移
- **FORCE RLS**：PostgreSQL テーブル owner も policy に従わせる
- **FTS**：Full Text Search（`tsvector`）

## G–L

- **GEO**：Generative Engine Optimization（姉妹製品）
- **GIN Index**：PostgreSQL 反転索引
- **Ground Truth**：権威事実集（`brand_facts`）
- **Handoff** *：AI → 人間引継ぎ五状態マシン
- **HNSW**：pgvector デフォルト ANN
- **Intent Routing** *：knowledge / smalltalk / handoff / opinion 四分類
- **JSON-LD**：Schema.org 直列化
- **Knowledge Base (KB)**：テナント下の論理知識集、複数 KB 可
- **L1 Wiki** *：Layer 1 DB キャッシュ済みコンパイル済みサマリー
- **L2 RAG** *：Layer 2 pgvector + BM25 + RRF
- **Lint**：Wiki 一貫性・事実の毎日チェック
- **LLM**：Large Language Model

## M–R

- **Mirror Mode**：真人支援時に AI 自動送信せず提案のみ
- **NLI**：Natural Language Inference 三値分類
- **PIF**：Product Information File（姉妹製品）
- **pgvector**：PostgreSQL ベクトル拡張
- **Provider Router** *：マルチベンダー LLM ルーティングとフォールバック
- **RAG**：Retrieval Augmented Generation
- **Reciprocal Rank Fusion (RRF)**：`score = Σ 1/(k + rank_i)`、k=60
- **Rerank**：上位 K を cross-encoder で精排
- **Redis Streams**：Redis メッセージブローカー
- **RLS**：Row-Level Security

## S–Z

- **Schema.org**：構造化データ語彙
- **Semantic Cache** *：ベクトル類似度ベース answer cache
- **Session State**：Redis の会話状態（最近 N ラウンド）
- **Slug**：Wiki ページの URL 対応キー
- **Source Hash**：文書 sha256、重複削除
- **SSE**：Server-Sent Events
- **Superuser Bypass**：PostgreSQL superuser の RLS 無視
- **Tenant**：SaaS 顧客単位
- **Three-Layer Isolation** *：App + DB + Query 防御
- **tsvector / tsquery**：PostgreSQL FTS 型
- **Wiki Compile** *：chunks → wiki_pages 生成
- **zhparser**：PostgreSQL 中国語分詞
