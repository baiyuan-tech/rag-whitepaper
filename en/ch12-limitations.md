---
title: "Chapter 12 — Limitations, Open Problems, Future Work"
chapter: 12
lang: en
license: CC-BY-NC-4.0
---

# Chapter 12 — Limitations, Open Problems, Future Work

> The honest chapter. What we haven't solved, what we might reverse, what's coming.

## 12.1 Engineering Limitations

### 12.1.1 pgvector Scale Ceiling

Per-tenant embeddings at ~100k volume: HNSW P95 < 120 ms. Past 5M, performance degrades. **If any tenant hits 5M, evaluate Qdrant/Milvus migration or sharding.**

### 12.1.2 Chinese Tokenization Long Tail

`zh_parser` (SCWS-based) misses new words, brand names, product names. We patch with synonym dictionaries — ongoing maintenance burden. Experimental alternative: **LLM-time tokenization** — better accuracy, +100 ms, higher cost.

### 12.1.3 No Multimodal Yet

Text only. Real knowledge is mixed:

- Product photo + text description
- Construction workflow diagram
- Cosmetic SDS PDF with tables and chemical structures

CLIP-style multimodal embedding experimental; targeted 2026 Q3.

### 12.1.4 Single Region

Deployed only in AWS Tokyo. EU compliance needs EU region. Docker Compose architecture doesn't support multi-region; needs K8s refactor.

## 12.2 Algorithmic Limitations

### 12.2.1 Wiki Compile LLM Bias

LLM-authored Wiki has systematic biases: Western-centric examples, inconsistent transliteration, stale post-training-cutoff knowledge. Our mitigations (strict "chunks-only" instruction, cross-chunk consistency lint) partially help but **don't fix the root**.

### 12.2.2 RRF k=60 Is Empirical

The paper suggests 60, but gives no theoretical justification. We haven't run sufficient A/B to validate it for Chinese. **Worth revisiting.**

### 12.2.3 Intent Classifier Drift

GPT-4o-mini misclassifies vague openings ("I was wondering..."). Knowledge → smalltalk means the customer gets a polite non-answer. Fix direction: expanded training set + confidence threshold + dual-path on low confidence.

### 12.2.4 Chinese NLI Availability

English NLI (DeBERTa-v3-NLI) is excellent. Chinese NLI quality varies; we use mDeBERTa-multi + human audit at ~85% accuracy. Production-grade Chinese NLI is an **open problem**.

## 12.3 Commercial Limitations

### 12.3.1 Pricing-Cost Misalignment

Current pricing by message count. Actual cost varies:

- Simple CS ask: USD 0.001
- PIF regulatory citation: USD 0.02
- NLI + Rerank high-precision: USD 0.05

High-precision tenants underpay; low-precision overpay. **2026 Q3: precision-tier pricing.**

### 12.3.2 Cross-Product Cost Attribution

Shared infra is wonderful; "GEO-triggered RAG repair token usage" is hard to attribute. Currently GEO API calls count against RAG tenant quota — financially imprecise.

### 12.3.3 Breaking Changes Cost

Upgrading embedding model (`text-embedding-3-small` → `-large`) requires full re-embed. For a large tenant: USD 2,000+. We've deferred such upgrades — **tech debt accumulates.**

## 12.4 Open Problems

### 12.4.1 Wiki Fresh vs Stale Balance

How often to compile?

- Daily: waste (most pages unchanged)
- Monthly: stale for regulated domains
- Event-driven: "change" itself is hard to define

Current: fingerprint + weekly lint + manual trigger — no clean theory.

### 12.4.2 User Authority vs RAG Authority

Customer says "your website says CEO is Bob." RAG Wiki says "Alice." Who wins?

- Trust RAG: maybe the customer was spoofed
- Trust customer: maybe our system is stale

This is a **trust chain** problem with no engineering answer yet.

### 12.4.3 Does Long-Context LLM End RAG?

Claude 200k, Gemini 2M — tempting to "stuff everything in prompt." Our position: **RAG doesn't die, it mutates.**

- Cost: 200k input per query → USD 0.5+, unsustainable
- "Lost in the middle" — LLMs lose focus in ultra-long contexts
- Permission control: multi-tenant can't put everything in LLM

**L1 Wiki becomes the tool to align LLM attention precisely**, rather than a substitute for vector retrieval.

### 12.4.4 Multimodal L1 Wiki

Text Wiki is natural. What is a Wiki for images / video / audio?

- Formula photo → OCR + visual description?
- Construction video → timeline of events?
- Meeting recording → summary + speaker separation?

No unified answer.

## 12.5 Next 12-Month Roadmap

Tentative (subject to market feedback):

| Quarter | Item | Priority |
|---------|------|----------|
| 2026 Q2 | Multimodal embedding (CLIP-style) | High |
| 2026 Q2 | Rerank default-on evaluation | Medium |
| 2026 Q2 | GEO ↔ RAG Wiki patch API launch | High |
| 2026 Q3 | Precision-tier pricing | High |
| 2026 Q3 | EU region deployment (K8s) | Medium |
| 2026 Q3 | Japanese NLI self-training | Medium |
| 2026 Q4 | Long-context + Wiki hybrid strategy | Medium |
| 2026 Q4 | Self-hosted edition | Low |

### 12.5.1 Living Document

This book is a living document: minor versions each quarter, major annually. GitHub Issues capture reader feedback. Updates in `CHANGELOG.md`.

---

## Key Takeaways

- pgvector needs migration plan past 5M vectors
- Chinese tokenization, multimodal, multi-region are main engineering gaps
- LLM bias in Wiki compile, RRF k=60 empirical, Chinese NLI quality are algorithmic gaps
- Pricing ↔ cost, cross-product attribution, breaking changes are commercial gaps
- Long-context LLMs reshape, don't end, RAG
- 2026 roadmap centers on multimodal, Wiki patch API, precision-tier pricing

## References

- [Lost in the Middle — Liu et al.][lost] · [Qdrant vs pgvector][bench]

[lost]: https://arxiv.org/abs/2307.03172
[bench]: https://github.com/pgvector/pgvector/discussions

---

**Navigation**: [← Ch 11](./ch11-case-studies.md) · [📖 Contents](./README.md) · [Appendix A →](./appendix-a-glossary.md)
