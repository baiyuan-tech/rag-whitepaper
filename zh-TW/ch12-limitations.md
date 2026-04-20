---
title: "Chapter 12 — 限制、未解問題與未來工作"
description: "百原 RAG 平台的工程限制、未解問題、對業界開放討論的挑戰"
chapter: 12
part: 5
word_count: 4100
lang: zh-TW
authors:
  - name: 百原科技
    url: https://baiyuan.io
license: CC-BY-NC-4.0
keywords:
  - 限制
  - Future Work
  - pgvector 規模
  - 多模態
  - 長文
last_updated: 2026-04-20
---

# Chapter 12 — 限制、未解問題與未來工作

> 白皮書最誠實的一章。我們做得不夠好的、沒解決的、之後可能反悔的都寫在這。

## 目錄

- [12.1 工程性限制](#121-工程性限制)
- [12.2 演算法性限制](#122-演算法性限制)
- [12.3 商業性限制](#123-商業性限制)
- [12.4 未解問題](#124-未解問題)
- [12.5 未來 12 個月路線圖](#125-未來-12-個月路線圖)

---

## 12.1 工程性限制

### 12.1.1 pgvector 的規模上限

目前單租戶 embedding 數在 10 萬量級，pgvector HNSW 查詢 P95 < 120ms。但突破 500 萬後性能明顯下滑。**未來 12 個月若某租戶達 500 萬向量，需評估遷至 Qdrant / Milvus** 或分片。

### 12.1.2 中文分詞的長尾

`zh_parser`（基於 SCWS）對新詞、商標、產品名的切詞不理想。我們靠「同義詞字典」+ 人工維護彌補，但字典維護是持續工。

實驗中的方案：**LLM 即時分詞**。效果好但成本高、延遲差 100ms。

### 12.1.3 多模態還沒做

目前只處理文字。但現實知識常是：

- 產品圖 + 文字描述
- 施工流程圖
- 化粧品成分 SDS PDF 的表格與化學結構

CLIP-style 多模態 embedding 已在實驗，預計 2026 Q3 推出。

### 12.1.4 單區部署

目前只在 AWS 東京區。歐盟客戶法遵上需要 EU 區。K8s 重構後才能跨區，目前 Docker Compose 架構不支援。

## 12.2 演算法性限制

### 12.2.1 Wiki Compile 的 LLM 偏見

Wiki 頁是 LLM 寫的，LLM 有系統性偏見。例如：

- 傾向用西方案例舉例
- 對中文專有名詞音譯不一致
- 對時間敏感事實易犯「凍結 training cutoff 前的版本」

我們的補救：

- Compile 時強制要求「只用提供的 chunks」
- Wiki Lint 有跨 chunks 一致性檢查
- 但**根本問題沒解**

### 12.2.2 RRF 的 k=60 是經驗值

RRF 論文建議 k=60，但沒解釋為什麼。我們也沒做足夠 AB 測試證明 60 對中文場景最佳。**可能這個魔法數字該調**，但尚未投入資源量測。

### 12.2.3 Intent Classifier 的錯分

GPT-4o-mini 做的 intent 分類，對「我想問」「請教」這類模糊開頭，分類偶爾飄。誤把 knowledge 分為 smalltalk = 客戶被禮貌回覆而非實際答案。

修復方向：擴大訓練集 + 啟用 confidence threshold，低 confidence 時同時走兩條路（保守）。

### 12.2.4 NLI 中文模型的可用性

英文 NLI（DeBERTa-v3-NLI）很好用。中文 NLI 品質落差大，我們用 **mDeBERTa（多語）+ 人工校驗**組合，精度約 85%。生產級中文 NLI 仍是 open problem。

## 12.3 商業性限制

### 12.3.1 定價與成本不匹配

目前定價按「訊息數量」，但實際成本差異很大：

- 簡單客服 ask：成本 USD 0.001 / 次
- PIF 法規引用：成本 USD 0.02 / 次
- 帶 NLI + Rerank 的高精度場景：USD 0.05 / 次

高精度租戶被低估，低精度租戶被高估。**2026 Q3 計畫改用「精度階層定價」**。

### 12.3.2 三條產品線的內部成本分攤

共用基礎設施很棒，但「GEO 觸發 RAG 修復佔用多少 Token」這種跨產品帳難分。**目前 GEO 的 API 呼叫也算在 RAG 租戶 quota 裡**，財務上略不精確。

### 12.3.3 Breaking Changes 的代價

升級 embedding 模型（`text-embedding-3-small` → `text-embedding-3-large`）意味著全量 re-embed。對大租戶一次成本 USD 2,000+。目前我們擋下升級，代價是**技術債累積**。

## 12.4 未解問題

以下幾個是本書作者目前都沒有好答案，歡迎業界討論：

### 12.4.1 Wiki 的 Fresh 與 Stale 平衡

Wiki 編譯頻率該多高？

- 每日編譯：成本高、CPU 浪費（多數頁無變動）
- 每月編譯：法規場景過時
- 事件驅動：chunks 變動觸發 → 但「變動」本身難定義

目前用 fingerprint + 每週 lint + 人工觸發，但沒有清楚的理論。

### 12.4.2 使用者權威 vs RAG 權威

當使用者說「你們官網說 CEO 是 Bob」，但 RAG Wiki 是「Alice」。誰對？

- 信 RAG：使用者可能被假網站騙
- 信使用者：系統可能過時

這是一個**信任鏈條**問題，還沒有工程解。

### 12.4.3 Long Context LLM 是否終結 RAG

Claude Opus 200k context、Gemini 2M context — 看起來可以「把全公司文件塞進 prompt」。

我們的立場：**RAG 不會消失，但會變形**。

- 成本：200k context × 輸入單價，單次查詢 USD 0.5+，不可持續
- 注意力：LLM 在超長上下文中間會「迷失」（lost in the middle）
- 權限控制：多租戶場景不可能把全部文件塞給 LLM

**L1 Wiki 會變成「精準對齊 LLM 注意力」的手段**，而非傳統向量檢索的替代。

### 12.4.4 多模態的 L1 Wiki

純文字 Wiki 好編。圖片、影片、音訊的 Wiki 該長什麼樣？

- 一張配方圖 → 轉文字 OCR + 視覺描述？
- 施工影片 → 轉時間軸事件列表？
- 音訊會議錄音 → 轉摘要 + 發言者分離？

沒有統一答案。

## 12.5 未來 12 個月路線圖

暫定的優先次序（可能依市場反應調整）：

| 季 | 項目 | 優先 |
|----|-----|-----|
| 2026 Q2 | 多模態 embedding（CLIP-style） | 高 |
| 2026 Q2 | Rerank 全租戶預設啟用評估 | 中 |
| 2026 Q2 | GEO ↔ RAG Wiki patch API 上線 | 高 |
| 2026 Q3 | 精度階層定價 | 高 |
| 2026 Q3 | EU 區部署（需 K8s） | 中 |
| 2026 Q3 | 日文 NLI 模型自訓 | 中 |
| 2026 Q4 | Long context + Wiki 的混合策略 | 中 |
| 2026 Q4 | 開放 Self-Hosted 版本 | 低 |

### 12.5.1 本書會隨工程推進更新

本書採 Living Document 模式：

- 每季末 minor version（v1.1, v1.2...）
- 當年度一次 major（v2.0）
- GitHub Issues 收錄讀者意見
- 更新內容在 `CHANGELOG.md`

---

## 本章要點

- pgvector 500 萬向量後需評估遷移
- 中文分詞、多模態、跨區部署是主要工程限制
- Wiki Compile 的 LLM 偏見、RRF k=60 的經驗值、中文 NLI 品質是主要演算法限制
- 三條產品線的成本分攤、breaking changes 成本是主要商業限制
- Long context LLM 不會終結 RAG，但會改寫角色
- 2026 路線圖優先解多模態、Wiki patch API、精度階層定價

## 參考資料

- [Lost in the Middle — Liu et al. 2023][lost]
- [Qdrant vs pgvector Benchmark][pgv-bench]

[lost]: https://arxiv.org/abs/2307.03172
[pgv-bench]: https://github.com/pgvector/pgvector/discussions

## 修訂記錄

| 日期 | 版本 | 說明 |
|------|------|------|
| 2026-04-20 | v1.0 | 初稿 |

---

**導覽**：[← Ch 11: 真實觀察](./ch11-case-studies.md) · [📖 目次](../README.md) · [附錄 A →](./appendix-a-glossary.md)
