---
title: "第 12 章 — 限界・未解問題・今後の課題"
chapter: 12
lang: ja
license: CC-BY-NC-4.0
---

# 第 12 章 — 限界・未解問題・今後の課題

> 白皮書で最も誠実な章。解けてないこと、反転の可能性を書く。

## 12.1 工学的限界

### 12.1.1 pgvector のスケール

単一テナント embedding 10 万量級、HNSW P95 < 120 ms。500 万超で性能低下。**500 万到達テナントが出たら Qdrant / Milvus 移行またはシャーディング検討**。

### 12.1.2 中国語分詞の長尾

`zh_parser`（SCWS）は新語、商標、製品名を誤分。同義語辞書で補うが維持負担。実験中：**LLM リアルタイム分詞** — 精度良いがコスト高 + 100 ms。

### 12.1.3 マルチモーダル未対応

テキストのみ。現実の知識は混合（製品写真、施工フロー図、化粧品 SDS PDF の表と化学構造）。CLIP-style 多モーダル実験中、2026 Q3 予定。

### 12.1.4 単一リージョン

AWS 東京のみ。EU 顧客は EU 区必要。Docker Compose 単一区、K8s リファクタ後に対応。

## 12.2 アルゴリズム的限界

### 12.2.1 Wiki Compile の LLM バイアス

LLM バイアスは系統的：西洋事例偏重、中国語固有名詞音訳不一致、時間敏感事実で training cutoff 以前で停滞。補正手段（「chunks のみ使用」、cross-chunks 一貫性 lint）は部分的。**根本は未解**。

### 12.2.2 RRF k=60 は経験値

論文は 60 推奨だが理論根拠なし。中文シナリオでの A/B 未実施。**要検証**。

### 12.2.3 Intent Classifier 誤分

GPT-4o-mini が曖昧開頭で誤分。knowledge → smalltalk 誤分で顧客が丁寧に無答返される。修正方向：訓練集拡張 + confidence threshold。

### 12.2.4 中国語 NLI モデル

英語 NLI（DeBERTa-v3）は優秀。中国語 NLI は品質差大、mDeBERTa-multi + 人手で 85% 精度。生産級中文 NLI は **open problem**。

## 12.3 商業的限界

### 12.3.1 料金とコストの不整合

現在メッセージ数で課金。実コストは大きく差：

- 単純 CS：USD 0.001/件
- PIF 法規引用：USD 0.02/件
- NLI + Rerank 高精度：USD 0.05/件

高精度テナント過小課金、低精度過大課金。**2026 Q3 精度階層料金**計画。

### 12.3.2 製品横断コスト按分

共通基盤は良いが、「GEO が起動した RAG 修復の token 利用」は按分困難。現状 GEO API 呼び出しも RAG テナント quota に計上、財務精度低。

### 12.3.3 Breaking Changes

embedding 更新（3-small → 3-large）で全量再計算。大テナント 1 回 USD 2,000+。現在保留、**技術負債蓄積**。

## 12.4 未解問題

### 12.4.1 Wiki の Fresh vs Stale

コンパイル頻度：

- 毎日：高コスト、CPU 無駄
- 毎月：規制場面で古い
- イベント駆動：「変動」自体の定義困難

現状：fingerprint + 週次 lint + 手動トリガ。理論未整備。

### 12.4.2 ユーザ権威 vs RAG 権威

顧客「御社サイトは CEO を Bob と書いている」、RAG Wiki は「Alice」。どちらが正？**信頼連鎖**問題、工学解決なし。

### 12.4.3 Long Context LLM は RAG を終わらせるか

Claude 200k、Gemini 2M — 「全社文書を prompt に入れる」誘惑。我々の立場：**RAG は死なないが変形する**。

- コスト：200k input/回 → USD 0.5+、持続不能
- 注意：「lost in the middle」
- 権限：マルチテナントで全文書を LLM に入れる不可

**L1 Wiki は LLM 注意を精密に整列するツールになる**。

### 12.4.4 マルチモーダル L1 Wiki

テキスト Wiki は自然。画像／動画／音声の Wiki は？

- 配合写真 → OCR + 視覚記述？
- 施工動画 → タイムライン？
- 会議録音 → 要約 + 話者分離？

統一解なし。

## 12.5 次 12 ヶ月ロードマップ

| 四半期 | 項目 | 優先度 |
|-------|-----|-------|
| 2026 Q2 | マルチモーダル embedding | 高 |
| 2026 Q2 | Rerank デフォルト化評価 | 中 |
| 2026 Q2 | GEO ↔ RAG Wiki patch API | 高 |
| 2026 Q3 | 精度階層料金 | 高 |
| 2026 Q3 | EU 区（K8s 必須） | 中 |
| 2026 Q3 | 日本語 NLI 自訓 | 中 |
| 2026 Q4 | Long context + Wiki ハイブリッド | 中 |
| 2026 Q4 | Self-Hosted 版 | 低 |

### 12.5.1 本書は更新継続

- 四半期末に minor（v1.1, v1.2...）
- 年次 major（v2.0）
- GitHub Issues で読者意見
- `CHANGELOG.md` で更新内容

---

## 本章のポイント

- pgvector 500 万ベクトル超で移行検討
- 中国語分詞、マルチモーダル、跨区配置は主要工学制限
- Wiki LLM バイアス、RRF k=60 経験値、中国語 NLI 品質が主要アルゴ制限
- 料金-コスト整合、横断按分、breaking changes は主要商業制限
- Long context LLM は RAG を終わらせないが役割を書き換える
- 2026 ロードマップはマルチモーダル、Wiki patch、精度階層優先

---

**ナビゲーション**：[← 第 11 章](./ch11-case-studies.md) · [📖 目次](./README.md) · [付録 A →](./appendix-a-glossary.md)
