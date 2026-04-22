---
title: "Appendix A — Glossary"
lang: en
license: CC-BY-NC-4.0
last_modified_at: '2026-04-22T03:40:36Z'
---





# Appendix A — Glossary

Terms with `*` are Baiyuan coinages. Sorted alphabetically.

## A–F

- **Answer Cache**: Redis key-value cache, `sha256(normalize(q)+tenant+kb)` → answer, TTL 600s
- **AXP** *: AI-ready eXchange Page, core GEO concept
- **BM25**: Keyword retrieval scoring (via PostgreSQL `ts_rank_cd`)
- **Brand Entity**: Record in `brand_entities` (Organization / Service / Person)
- **ChainPoll** *: LLM multi-invocation majority vote for hallucination detection
- **Chunk**: Minimum retrieval unit, typically 500 tokens
- **ClaimReview**: Schema.org type for claim truth annotation
- **Degraded Mode**: System pressure state (skip rerank / lower model / L1-only)
- **Document**: Raw data unit in a KB
- **Embedding**: Text-to-vector; default 1536-dim
- **Fallback**: Automatic L1-miss-to-L2 path
- **FORCE RLS**: PostgreSQL flag making table owner obey RLS
- **FTS**: Full Text Search via `tsvector`

## G–L

- **GEO**: Generative Engine Optimization (sister product at geo.baiyuan.io)
- **GIN Index**: PostgreSQL inverted index for arrays / tsvector
- **Ground Truth**: Authoritative fact set (`brand_facts`)
- **Handoff** *: AI → human transfer five-state machine
- **HNSW**: pgvector default ANN index (Hierarchical Navigable Small World)
- **Intent Routing** *: Message classification into knowledge / smalltalk / handoff / opinion
- **JSON-LD**: Schema.org serialization format
- **Knowledge Base (KB)**: Logical grouping under a tenant; multi-KB per tenant allowed
- **L1 Wiki** *: Layer 1 DB-cached compiled summaries
- **L2 RAG** *: Layer 2 pgvector + BM25 + RRF
- **Lint**: Daily consistency/fact check on Wiki
- **LLM**: Large Language Model

## M–R

- **Mirror Mode**: AI assists human agents without auto-sending
- **NLI**: Natural Language Inference, three-way (entail / contradict / neutral)
- **PIF**: Product Information File (sister product at pif.baiyuan.io)
- **pgvector**: PostgreSQL vector extension
- **Provider Router** *: Multi-vendor LLM routing and fallback
- **RAG**: Retrieval Augmented Generation
- **Reciprocal Rank Fusion (RRF)**: `score = Σ 1/(k + rank_i)`, k=60
- **Redis Streams**: Redis message broker primitive
- **Rerank**: Cross-encoder precision reranking of top-K
- **RLS**: Row-Level Security

## S–Z

- **Schema.org**: Structured data vocabulary
- **Semantic Cache** *: Answer cache keyed by vector similarity
- **Session State**: Conversation state in Redis (last N turns)
- **Slug**: URL-friendly wiki page key
- **Source Hash**: Document sha256, deduplication
- **SSE**: Server-Sent Events streaming protocol
- **Superuser Bypass**: PostgreSQL superuser RLS override
- **Tenant**: SaaS customer unit
- **Three-Layer Isolation** *: App + DB + Query defense-in-depth
- **tsvector / tsquery**: PostgreSQL FTS types
- **Wiki Compile** *: Process to build wiki_pages from chunks
- **zhparser**: PostgreSQL Chinese tokenizer extension
