---
title: "Appendix D — Figure Index"
lang: en
license: CC-BY-NC-4.0
last_modified_at: '2026-04-20T09:17:36Z'
---




# Appendix D — Figure Index

## Chapter Figures

| # | Figure | Type | Chapter |
|---|--------|------|---------|
| Fig 0 | Three Pillars sharing RAG infra | Mermaid flowchart | README |
| Fig 1-1 | Hallucination root-cause distribution | Mermaid pie | Ch 1 |
| Fig 1-2 | Three-layer defense-in-depth | Mermaid flowchart | Ch 1 |
| Fig 2-1 | `/api/v1/ask` sequence | Mermaid sequence | Ch 2 |
| Fig 2-2 | Component layout | Mermaid flowchart | Ch 2 |
| Fig 3-1 | Three-way voting for L1 hit | Mermaid flowchart | Ch 3 |
| Fig 3-2 | Wiki Lint five checks | Mermaid flowchart | Ch 3 |
| Fig 5-1 | 7-layer fallback decision tree | Mermaid flowchart | Ch 5 |
| Fig 5-2 | Three-level degradation state machine | Mermaid stateDiagram | Ch 5 |
| Fig 7-1 | Document lifecycle | Mermaid stateDiagram | Ch 7 |
| Fig 7-2 | Site scrape flow | Mermaid flowchart | Ch 7 |
| Fig 7-3 | Ingestion pipeline | Mermaid flowchart | Ch 7 |
| Fig 8-1 | Four intent routing | Mermaid flowchart | Ch 8 |
| Fig 8-2 | Handoff five-state | Mermaid stateDiagram | Ch 8 |
| Fig 8-3 | Mirror mode | Mermaid flowchart | Ch 8 |
| Fig 9-1 | GEO-RAG shared and bidirectional flow | Mermaid flowchart | Ch 9 |
| Fig 9-2 | Ground Truth closed loop | Mermaid sequence | Ch 9 |
| Fig 10-1 | PIF AI public + private KB | Mermaid flowchart | Ch 10 |
| Fig 10-2 | 16-document generation pipeline | Mermaid sequence | Ch 10 |

## Major Tables

Referenced by chapter: hallucination root causes (Ch 1), enterprise scale vs token cost (Ch 1), database schema overview (Ch 2), tech stack decisions (Ch 2), Wiki metrics comparison (Ch 3), vector storage options (Ch 4), chunking strategies (Ch 4), embedding models (Ch 4), fallback per-node stats (Ch 5), threat model (Ch 6), ingestion formats (Ch 7), SSE protocol (Ch 8), handoff state behavior (Ch 8), brand_entities / brand_facts (Ch 9), shared dashboard metrics (Ch 9), 16 PIF documents (Ch 10), RAG dependency per document (Ch 10), cross-case comparison (Ch 11), 2026 roadmap (Ch 12).

## Diagram Conventions

- Mermaid 10.x compatible
- Colors: theme-neutral (light/dark auto)
- Naming: `Fig N-x` (N = chapter number, 0 for README)
- Caption format: `*Fig N-x: description*` beneath the figure, italic
- Backup SVG for complex figures: `assets/figures/figN-x.svg` (used for PDF export)

## PDF Export

When rendered to PDF, Mermaid is converted via `mmdc` to SVG, then embedded into LaTeX for vector clarity. Fonts: Noto Sans CJK TC (zh-TW), Noto Serif CJK JP (ja), default serif (en).

## Reader Feedback

Figure errors or suggested alternatives: open a GitHub Issue with `[figure]` tag.
