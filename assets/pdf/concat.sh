#!/usr/bin/env bash
# concat.sh <lang>
#   Concatenate chapters into a single whitepaper.md for PDF build.
#   Strips per-chapter YAML frontmatter (PDF uses assets/pdf/metadata-<lang>.yaml).
#   Strips <script type="application/ld+json"> HTML comment blocks.
#   Strips per-chapter navigation footers.

set -euo pipefail

LANG_DIR="${1:-zh-TW}"

if [[ ! -d "${LANG_DIR}" ]]; then
  echo "Language directory not found: ${LANG_DIR}" >&2
  exit 1
fi

# Deterministic order: ch01..ch12, then appendix-a..d
FILES=(
  "${LANG_DIR}/ch01-"*.md
  "${LANG_DIR}/ch02-"*.md
  "${LANG_DIR}/ch03-"*.md
  "${LANG_DIR}/ch04-"*.md
  "${LANG_DIR}/ch05-"*.md
  "${LANG_DIR}/ch06-"*.md
  "${LANG_DIR}/ch07-"*.md
  "${LANG_DIR}/ch08-"*.md
  "${LANG_DIR}/ch09-"*.md
  "${LANG_DIR}/ch10-"*.md
  "${LANG_DIR}/ch11-"*.md
  "${LANG_DIR}/ch12-"*.md
  "${LANG_DIR}/appendix-"*.md
)

for f in "${FILES[@]}"; do
  [[ -f "$f" ]] || continue
  # Strip YAML frontmatter (between first two "---" lines)
  # Strip JSON-LD HTML comment blocks
  # Strip per-chapter navigation footer lines (zh-TW / en / ja)
  awk '
    BEGIN { fm=0; inld=0 }
    NR==1 && /^---[[:space:]]*$/ { fm=1; next }
    fm==1 && /^---[[:space:]]*$/ { fm=0; next }
    fm==1 { next }
    /^<!--[[:space:]]*AI-friendly/ { inld=1; next }
    inld==1 && /^-->/ { inld=0; next }
    inld==1 { next }
    /^<script type="application\/ld\+json">/ { inld=1; next }
    inld==1 && /^<\/script>/ { inld=0; next }
    inld==1 { next }
    /^\*\*導覽\*\*/ { next }
    /^\*\*Navigation\*\*/ { next }
    /^\*\*ナビゲーション\*\*/ { next }
    { print }
  ' "$f"
  echo ""
  echo "\\newpage"
  echo ""
done
