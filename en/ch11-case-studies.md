---
title: "Chapter 11 — Anonymized Tenant Observations"
chapter: 11
lang: en
license: CC-BY-NC-4.0
last_modified_at: '2026-04-20T09:17:36Z'
---




# Chapter 11 — Anonymized Tenant Observations

> Numbers don't lie. But they can stay selectively silent. This chapter puts both the good and the ugly in print.

## 11.1 Collection & Anonymization

All figures from Baiyuan Pilot: 12 tenants, ~1.2M queries in Q1 2026. Principles: aggregate only, industry-delidentified, no absolute-number stacking, granularity useful for engineers but not for architecture copying.

## 11.2 Case A — E-commerce CS (AI CS SaaS)

**Context**: Consumer electronics brand, annual revenue > USD 5M, Taiwan market. Widget + LINE deployed.

| Metric | Before | After (3 mo) |
|--------|--------|-------------|
| Daily tickets | 120 | 38 (−68%) |
| First response time | 18 min | 0.8 s |
| L1 hit rate | — | 52% |
| Cache hit rate | — | 31% |
| Monthly LLM spend | — | USD 680 |
| CSAT | 4.1/5 | 4.3/5 |
| Handoff rate | 100% | 11% |

**Observations**:

- Exceptional L1 hit rate. E-commerce FAQs are repetitive (shipping, returns, warranty). Maintaining explicit slug list lifted hit from 28% to 52%.
- 11% Handoff concentrates on special requests (custom orders, bulk, damage claims) — exactly where humans excel.
- CSAT slightly rose — not because AI answered better, but because **sub-second responses kill waiting anxiety**.

**Lesson learned**: Week 1 hallucination event — AI said free-shipping threshold was NT$500, actually NT$800. Root cause: L2 retrieved an old FAQ chunk. Fix: elevated "shipping policy" to L1 Wiki with monthly revalidation.

## 11.3 Case B — SaaS Tech Docs (AI CS)

**Context**: B2B SaaS with 300+ articles across API docs, integration guides, SDK samples. Developer self-serve.

| Metric | Value |
|--------|-------|
| Monthly queries | 120,000 |
| L1 hit rate | 38% |
| L2 with Rerank | 18% |
| Avg answer length | 340 chars |
| With code block | 61% |
| Follow-up rate | 22% |

**Observations**:

- Tech questions have lower L1 hit (38% vs 52% e-commerce) — terminology varies, topics sprawl
- Rerank lifts Recall@5 by 9% at +250ms latency
- **Conversation memory critical** — devs ask follow-ups on the same topic
- Special hallucination: **invented API endpoints** that don't exist. Needs the "endpoint whitelist" mitigation (Ch 12)

## 11.4 Case C — Cosmetics Brand (PIF AI)

**Context**: Mid-sized skincare brand, 14 SKUs needing 2026 Q1 PIF filing.

| Metric | Consultant | PIF AI |
|--------|-----------|--------|
| Per-SKU time | 30 workdays | 4 workdays |
| Per-SKU cost | USD 3,500 | USD 600 |
| Regulation update tracking | Monthly manual | Weekly auto |
| Citation traceability | 60–70% | 100% |
| TFDA first-pass approval | 70% | 88% |
| Monthly LLM spend | — | USD 320 |

**Observations**:

- PIF AI > human approval rate because auto-lint catches common mistakes (non-100% ingredient sum, missed prohibited checks)
- 95% of toxicology info comes from pre-compiled PubChem/ECHA Wiki — cuts per-ingredient lookup from 30 min to <1 s
- 100% traceable citations with `paragraph_hash` — TFDA reviewers stop questioning sources

**Lesson**: ECHA had a major 2026/02 update; old Wiki expired overnight. Added "source-change alert" — tenant Dashboard now shows "7 PIF filings cite expired data, review recommended."

## 11.5 Case D — B2B Consulting (GEO + RAG Coupled)

**Context**: B2B strategy consultancy; 10 partner bios, 30 research reports, 12 industry analyses. GEO for AI visibility + RAG for internal search. **Both share the same brand facts.**

| Metric | W0 | W6 |
|--------|-----|-----|
| AI citation rate (ChatGPT) | 18% | 41% |
| AI citation rate (Perplexity) | 22% | 58% |
| Fact accuracy (NLI) | 67% | 94% |
| Hallucination events / week | 12 | 2 |
| Avg repair latency | — | 6.2 days |
| Internal CS hit rate | 72% | 89% |

**Most striking**: Week 3 system caught Perplexity saying Partner Alice "graduated from Harvard" — actually Stanford. GEO triggered:

1. Generate ClaimReview
2. Inject into RAG Wiki (partner bio page)
3. AXP shadow doc updated
4. 6 days later Perplexity changed to "Stanford"
5. No human action needed

**This is the concrete value of deep integration.**

## 11.6 Cross-Case Patterns

| Metric | A | B | C | D |
|--------|---|---|---|---|
| L1 hit | 52% | 38% | 62% | 41% |
| Cache hit | 31% | 22% | 14% | 26% |
| Monthly cost | $680 | $450 | $320 | $520 |
| Main hallucination | Numbers | Nonexistent endpoint | None (NLI catches) | Person facts |
| Handoff rate | 11% | N/A | 24% | N/A |

**Conclusion 1**: **Structure drives L1 hit**. FAQs / regulations → 50%+. Dev docs / free Q&A → 30–40%.

**Conclusion 2**: **NLI pays off for regulated/academic domains**. +18% cost, hallucination → 0.

**Conclusion 3**: **GEO + RAG coupling shifts "brand AI health" overall**. A single metric misleads.

**Conclusion 4**: **Token cost absolute ≠ cost ratio**. E-commerce at $680 is 0.016% of revenue. PIF at $20 per $600 filing is 3.3%. PIF demands aggressive optimization.

---

## Key Takeaways

- Four cases span three product lines
- L1 hit varies 38–62% by knowledge structuring
- Handoff 11–24%, concentrated on uniquely human judgment
- NLI verification pays off in regulated scenarios
- Cross-product coupling (GEO + RAG) needs multi-axis metrics to appreciate

## References

- [CSAT methodology][csat] · [NLI fact-check][nli-paper]

[csat]: https://www.surveymonkey.com/mp/customer-satisfaction-score-csat/
[nli-paper]: https://aclanthology.org/P19-1579/

---

**Navigation**: [← Ch 10](./ch10-pif-integration.md) · [📖 Contents](./README.md) · [Ch 12 →](./ch12-limitations.md)
