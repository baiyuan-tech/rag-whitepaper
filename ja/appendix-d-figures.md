---
title: "付録 D — 図表索引"
lang: ja
license: CC-BY-NC-4.0
last_modified_at: '2026-04-20T09:17:36Z'
---




# 付録 D — 図表索引

## 章別図

| 番号 | 図 | 種類 | 所在 |
|------|----|------|------|
| Fig 0 | RAG 基盤を共有する 3 製品 | Mermaid flowchart | README |
| Fig 1-1 | 幻覚根因内訳 | Mermaid pie | Ch 1 |
| Fig 1-2 | 三層防御 | Mermaid flowchart | Ch 1 |
| Fig 2-1 | `/api/v1/ask` シーケンス | Mermaid sequence | Ch 2 |
| Fig 2-2 | コンポーネント配置 | Mermaid flowchart | Ch 2 |
| Fig 3-1 | L1 3 路投票 | Mermaid flowchart | Ch 3 |
| Fig 3-2 | Wiki Lint 5 種 | Mermaid flowchart | Ch 3 |
| Fig 5-1 | 7 層フォールバックツリー | Mermaid flowchart | Ch 5 |
| Fig 5-2 | 3 段階降格状態マシン | Mermaid stateDiagram | Ch 5 |
| Fig 7-1 | Document ライフサイクル | Mermaid stateDiagram | Ch 7 |
| Fig 7-2 | サイトクロールフロー | Mermaid flowchart | Ch 7 |
| Fig 7-3 | 取り込みパイプライン | Mermaid flowchart | Ch 7 |
| Fig 8-1 | Intent 4 分岐 | Mermaid flowchart | Ch 8 |
| Fig 8-2 | Handoff 五状態 | Mermaid stateDiagram | Ch 8 |
| Fig 8-3 | Mirror モード | Mermaid flowchart | Ch 8 |
| Fig 9-1 | GEO-RAG 共有・双方向 | Mermaid flowchart | Ch 9 |
| Fig 9-2 | Ground Truth 閉ループ | Mermaid sequence | Ch 9 |
| Fig 10-1 | PIF AI 公 + 私 KB | Mermaid flowchart | Ch 10 |
| Fig 10-2 | 16 文書生成パイプライン | Mermaid sequence | Ch 10 |

## 主要表

章ごと参照：幻覚根因と修正層（Ch 1）、企業規模 vs トークン費用（Ch 1）、DB スキーマ全景（Ch 2）、技術選定（Ch 2）、Wiki 指標比較（Ch 3）、ベクトルストレージ比較（Ch 4）、Chunking 3 戦略（Ch 4）、Embedding モデル比較（Ch 4）、各 fallback ノード命中率（Ch 5）、脅威モデル（Ch 6）、6 種取り込み形式（Ch 7）、SSE イベント（Ch 8）、Handoff 状態行動（Ch 8）、brand_entities/brand_facts（Ch 9）、共有指標（Ch 9）、PIF 16 文書（Ch 10）、各文書 RAG 依存度（Ch 10）、横断ケース対比（Ch 11）、2026 ロードマップ（Ch 12）。

## 作図規格

- Mermaid 10.x
- 配色：テーマ中立（light/dark 自動）
- 命名：`Fig N-x`（N = 章番号、0 = README）
- Caption：図下方イタリック `*Fig N-x: 説明*`
- 複雑図は `assets/figures/figN-x.svg` バックアップ（PDF 用）

## PDF エクスポート

Mermaid は `mmdc` で SVG 化、LaTeX に埋め込み。フォント：Noto Sans CJK TC（zh-TW）、Noto Serif CJK JP（ja）、default serif（en）。

## 読者フィードバック

図表の誤りや代替案は GitHub Issue `[figure]` タグで。
