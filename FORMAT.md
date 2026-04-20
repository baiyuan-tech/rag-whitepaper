# 白皮書文件格式規範

本書所有 `.md` 檔須遵循以下規範，目的是讓 GitHub 正確渲染、LLM 易於解析與引用、搜尋/AI 爬蟲能抽出結構化實體。

## 1. Frontmatter（YAML）

每個章節檔首行必須是 YAML frontmatter：

```yaml
---
title: "Chapter N — 章節主題"
description: "一句話描述（< 160 字元，用於 OG/Twitter preview 與 LLM summary）"
chapter: N
part: 1-5
word_count: 2000
lang: zh-TW
authors:
  - name: 百原科技
    url: https://baiyuan.io
license: CC-BY-NC-SA-4.0
keywords:
  - GEO
  - Generative Engine Optimization
  - 關鍵字 3-8 個
last_updated: YYYY-MM-DD
canonical: https://baiyuan.io/whitepaper/zh-TW/chNN-slug
---
```

## 2. 檔案結構

```markdown
<frontmatter>

# H1 章節標題（全檔唯一）

> 引言句（灰底 blockquote，一句話）

## 目錄

- [N.1 小節](#n1-小節)
- [N.2 小節](#n2-小節)
...

---

## N.1 第一小節

內容⋯⋯

### N.1.1 子小節（如需）

⋯⋯

## N.2 第二小節

⋯⋯

---

## 本章要點

- 3–5 條 bullet，用於 LLM 摘錄

## 參考資料

[numbered list 或 reference-style links]

## 修訂記錄

| 日期 | 版本 | 說明 |
|------|------|------|
| YYYY-MM-DD | v1.0 | 初稿 |

---

**導覽**：[← 上一章](./chNN-prev.md) · [目次](../README.md) · [下一章 →](./chNN-next.md)
```

## 3. 標題規則

- 每檔僅一個 H1
- H2 以 `N.1`、`N.2` 編號，與章節序列對齊
- 標題不含 emoji（避免 anchor 不穩）
- 標題不含 Markdown 特殊字元（`.` `:` `-` 除外）

## 4. 圖表

- **流程/架構圖**：優先用 Mermaid fenced block（```mermaid），GitHub 原生渲染
- **資料圖**：用 Markdown table；複雜視覺化留給獨立 PNG/SVG（放 `assets/figN-xx.svg`）
- **圖表 caption**：圖下方以斜體 `*Fig N-x: 說明*`
- 圖片必須有 alt text：`![alt text](path)`

## 5. 程式碼區塊

- 一律標語言：```` ```javascript ````、```` ```sql ````、```` ```yaml ````
- 沒有適用語言時用 ```` ```text ````
- 行內 code 用單一反引號包裹

## 6. 表格

- 使用 GFM pipe 語法
- 第一列標題、第二列分隔；欄位對齊用 `:---`、`:---:`、`---:`

## 7. 連結

- 外部連結：reference-style，`[文字][ref]`；`[ref]: url` 集中在章末「參考資料」
- 內部跨章連結：相對路徑 `./chNN-slug.md`
- 連結文字須具描述性，不用「點這裡」「連結」

## 8. 字符規範

- 用 ASCII 雙引號 `"` 而非 `「」`（但中文行文中的「」是允許的）
- 數字與單位間留空白：`30,000 字`、`25 億次/日`
- 中英文間留空白：`使用 ChatGPT 時`
- 日期統一 ISO 8601：`2026-04-18`
- 避免全形標點混用，逗號句號用全形、括號內層用半形

## 9. 語意標記

- **粗體**用於關鍵術語首次定義
- *斜體*用於書名、強調
- `code` 用於程式符號、檔名、API endpoint
- blockquote（>）僅用於章首引言與重要引用

## 10. 隱私與可揭露邊界

- 客戶名一律匿名（Brand A–E）
- 第三方廠商不點名（以架構層議題描述）
- 實際數字若為商業敏感，改以聚合或範圍（例：「約 30–40%」）
- API key、環境變數、內部路徑不得出現

## 11. LLM / GEO 友善標記

每個章節最末在 frontmatter 後可加 `<script type="application/ld+json">` HTML 區塊（GitHub 會忽略但保留於 source），包含 Schema.org `TechArticle` 結構：

```html
<!-- AI-friendly structured metadata (hidden from GitHub render) -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "Chapter N — 章節主題",
  "description": "...",
  "author": {"@type": "Organization", "name": "百原科技"},
  "datePublished": "YYYY-MM-DD",
  "inLanguage": "zh-TW",
  "isPartOf": {
    "@type": "Book",
    "name": "百原GEO Platform 技術白皮書",
    "url": "https://github.com/baiyuan/geo-whitepaper"
  },
  "keywords": "GEO, Generative Engine Optimization, ..."
}
</script>
```

## 12. 一致的前後導覽

每章末尾的導覽列格式固定：

```text
**導覽**：[← Ch N-1: 上章標題](./chNN-prev.md) · [📖 目次](../README.md) · [Ch N+1: 下章標題 →](./chNN-next.md)
```

頭尾章例外：

- Ch 1：`[📖 目次](../README.md) · [Ch 2 →](./ch02-system-overview.md)`
- Ch 13：`[← Ch 12](./ch12-constitution.md) · [📖 目次](../README.md) · [附錄 A →](./appendix-a-glossary.md)`
