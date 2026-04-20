---
title: "附錄 D — 配圖總表"
description: "全書圖表索引與規格"
chapter: D
part: 6
lang: zh-TW
license: CC-BY-NC-4.0
last_updated: 2026-04-20
last_modified_at: '2026-04-20T09:10:35Z'
---



# 附錄 D — 配圖總表

本附錄彙整全書所有 Mermaid 圖與 table，供查閱。

## 章節圖索引

| 編號 | 圖名 | 類型 | 所在章節 |
|------|------|------|---------|
| Fig 0 | 百原產品三支柱與 RAG 基礎設施關係 | Mermaid flowchart | README |
| Fig 1-1 | 幻覺根因分佈 | Mermaid pie | Ch 1 |
| Fig 1-2 | 三層租戶隔離的縱深防禦 | Mermaid flowchart | Ch 1 |
| Fig 2-1 | `/api/v1/ask` 完整呼叫序列 | Mermaid sequence | Ch 2 |
| Fig 2-2 | 百原 RAG 組件分工與資料流 | Mermaid flowchart | Ch 2 |
| Fig 3-1 | 三路投票決定 L1 是否命中 | Mermaid flowchart | Ch 3 |
| Fig 3-2 | Wiki Lint 五類檢查 | Mermaid flowchart | Ch 3 |
| Fig 5-1 | 從問題到答案的 7 層 fallback 決策樹 | Mermaid flowchart | Ch 5 |
| Fig 5-2 | 系統壓力下的三級降級狀態機 | Mermaid stateDiagram | Ch 5 |
| Fig 7-1 | Document 生命週期 | Mermaid stateDiagram | Ch 7 |
| Fig 7-2 | 站內爬蟲流程 | Mermaid flowchart | Ch 7 |
| Fig 7-3 | Ingestion 流水線 | Mermaid flowchart | Ch 7 |
| Fig 8-1 | 四類 intent 分流 | Mermaid flowchart | Ch 8 |
| Fig 8-2 | Handoff 五態機 | Mermaid stateDiagram | Ch 8 |
| Fig 8-3 | Mirror 模式 | Mermaid flowchart | Ch 8 |
| Fig 9-1 | RAG 與 GEO 的共用與雙向流 | Mermaid flowchart | Ch 9 |
| Fig 9-2 | Ground Truth 閉環修復流程 | Mermaid sequence | Ch 9 |
| Fig 10-1 | PIF AI 的公 + 私雙 KB 架構 | Mermaid flowchart | Ch 10 |
| Fig 10-2 | 16 項文件生成流水線 | Mermaid sequence | Ch 10 |

## 主要表格索引

| 表名 | 所在章節 |
|------|---------|
| 幻覺根因與解方層級 | Ch 1 |
| 企業 RAG 月查詢量 vs Token 費用 | Ch 1 |
| 資料表 schema 全景 | Ch 2 |
| 技術選型決策 | Ch 2 |
| Wiki 命中評測比較 | Ch 3 |
| 向量儲存方案比較 | Ch 4 |
| Chunking 策略三種 | Ch 4 |
| Embedding 模型比較 | Ch 4 |
| 各 fallback 節點命中率與延遲 | Ch 5 |
| 威脅模型 | Ch 6 |
| 六種攝取來源支援格式 | Ch 7 |
| SSE 事件協定 | Ch 8 |
| Handoff 狀態行為 | Ch 8 |
| brand_entities / brand_facts schema | Ch 9 |
| 共用指標 Dashboard | Ch 9 |
| PIF 16 項文件 | Ch 10 |
| 各項文件 RAG 依賴程度 | Ch 10 |
| 跨案例指標對比 | Ch 11 |
| 2026 路線圖 | Ch 12 |

## 製圖規格

- **Mermaid 版本**：GitHub 2026 年預設支援的 10.x
- **色彩**：不指定主題，隨 GitHub light/dark 自適應
- **命名**：Fig N-x，N 為章號（README 為 0），x 為該章流水號
- **Caption 格式**：`*Fig N-x: 說明*`（圖下方斜體）
- **備援 SVG**：複雜圖另存 `assets/figures/figN-x.svg`，PDF 匯出用

## PDF 匯出注意

本書有 PDF 版本（隨 GitHub Release）。PDF 匯出時：

- Mermaid 先以 `mmdc` 轉 SVG
- SVG 嵌入 LaTeX，保留向量清晰
- 中文字型用 `Noto Sans CJK TC`（繁）/ `Noto Serif CJK JP`（日）

## 讀者回饋

若發現圖表錯誤、有建議的替代畫法，請開 GitHub Issue 標 `[figure]`。
