---
title: "附錄 A — 詞彙表"
description: "百原 RAG 白皮書完整術語定義"
chapter: A
part: 6
lang: zh-TW
license: CC-BY-NC-4.0
last_updated: 2026-04-20
last_modified_at: '2026-04-20T09:17:36Z'
---




# 附錄 A — 詞彙表

本附錄彙整全書使用的術語，按英文字母與中文筆畫排序。標註 `*` 者為百原造詞或特定實踐命名。

## A–F

- **Answer Cache**：Redis 鍵值緩存，`sha256(normalize(question) + tenant + kb)` → answer，TTL 600 秒
- **AXP***：AI-ready eXchange Page。GEO Platform 核心，詳 GEO 白皮書
- **BM25**：Best Matching 25。關鍵詞檢索評分函式，PostgreSQL 用 `ts_rank_cd` 近似
- **Brand Entity**：`brand_entities` 表中的 Organization / Service / Person 記錄，供 GEO 與 RAG 共用
- **Chunk**：文件切片後的最小檢索單位，通常 500 token
- **ChainPoll***：同一 prompt 對 LLM 多次呼叫（預設 3 次）後多數決，降低幻覺偵測噪音
- **ClaimReview**：Schema.org 型別，用於標注聲明真偽
- **CS**：Customer Service，AI 客服 SaaS 簡稱
- **Degraded Mode**：系統壓力下的降級狀態，暫停 Rerank / 降級模型 / 僅回 L1
- **Document**：知識庫中的一份原始資料，可進一步切 chunks
- **Embedding**：文本向量化結果，本平台預設 1536 維
- **Fallback**：L1 miss 時自動退到 L2 的機制
- **FTS**：Full Text Search，PostgreSQL `tsvector` 提供
- **FORCE RLS**：PostgreSQL 強制 RLS，使表 owner 也受 policy 約束

## G–L

- **GEO**：Generative Engine Optimization。百原姐妹產品，geo.baiyuan.io
- **GIN Index**：PostgreSQL Generalized Inverted Index，用於陣列與 tsvector
- **Ground Truth**：GEO 中的權威事實集合，來自 `brand_facts`
- **Handoff***：AI 客服轉交真人客服的五態機
- **HNSW**：Hierarchical Navigable Small World，pgvector 預設 ANN 索引
- **Intent Routing***：使用者訊息先經 intent classifier 分類為 knowledge / smalltalk / handoff / opinion
- **IVF-Flat**：Inverted File + Flat，pgvector 另一種 ANN 索引
- **JSON-LD**：JSON for Linking Data。Schema.org 主要序列化格式
- **Knowledge Base（KB）**：租戶下的邏輯知識庫，一租戶可多 KB
- **L1 Wiki***：Layer 1 DB-cached compiled summaries
- **L2 RAG***：Layer 2 pgvector + BM25 + RRF 混合檢索
- **Lint**：Wiki 一致性與事實檢查，每日 cron 跑
- **LLM**：Large Language Model

## M–R

- **Mirror Mode**：真人客服工作時 AI 在旁建議但不送出的模式
- **Multi-Tenant**：多租戶 SaaS 架構
- **NLI**：Natural Language Inference，三值分類（entailment / contradiction / neutral）
- **Ordinal Ranking**：RRF 使用排序位置而非分數的設計
- **PIF**：Product Information File。百原姐妹產品 pif.baiyuan.io
- **pgvector**：PostgreSQL 向量擴充
- **Provider Router***：多家 LLM 供應商的路由與容錯機制
- **RAG**：Retrieval Augmented Generation
- **Reciprocal Rank Fusion（RRF）**：`score = Σ 1/(k + rank_i)`，多路檢索合併
- **Rerank**：對 top-K 結果用 cross-encoder 精排
- **Redis Streams**：Redis 的 message broker，百原 ingestion pipeline 使用
- **RLS**：Row-Level Security

## S–Z

- **Schema.org**：structured data 詞彙表
- **Semantic Cache***：向量相似度匹配的答案快取
- **Session State**：對話狀態，Redis 存最近 N 輪
- **Slug**：Wiki 頁的 URL-friendly key，如 `return-policy`
- **Source Hash**：文件內容 sha256，用於去重
- **SSE**：Server-Sent Events，串流輸出協定
- **Superuser Bypass**：PostgreSQL superuser 預設繞過 RLS 的行為
- **Tenant**：租戶，SaaS 的客戶單位
- **Three-Layer Isolation***：App / DB / Query 三層租戶隔離
- **tsvector / tsquery**：PostgreSQL 全文檢索的向量 / 查詢型別
- **Wiki Compile***：把 chunks 編譯成結構化 Wiki 頁的過程
- **WHERE tenant_id = ?**：Query 層的防禦式 tenant scoping
- **zhparser**：PostgreSQL 中文分詞擴充
