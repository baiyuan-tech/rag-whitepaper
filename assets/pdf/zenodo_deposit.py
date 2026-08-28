#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把建置好的 PDF 存放到 Zenodo,成為 concept DOI 底下的新版本。

**為什麼需要這支**:GitHub↔Zenodo 官方整合只封存原始碼 ZIP,不碰 release assets。
因此 v0.2 / v0.3 / v0.4 的 Zenodo 記錄全都只有 ZIP、沒有 PDF —— 而 Zenodo 落地頁的
`citation_pdf_url` 標籤是**依「記錄裡有沒有 PDF」自動決定**的,沒有 PDF 就沒有那個標籤,
Google Scholar 因此抓不到全文,從發佈至今從未具備被收錄的條件(2026-08-26 實測確認)。

**前提:GitHub↔Zenodo webhook 必須關閉。**
兩者並存會讓每次發版產生兩筆記錄(webhook 的 ZIP-only + 本腳本的 PDF 版),
且若 webhook 較晚完成,concept DOI 會指向那筆沒有 PDF 的,等於白做。
關閉位置:Zenodo → Applications → GitHub → 該 repo 的開關。

用法:
    python assets/pdf/zenodo_deposit.py --version 0.4.1 --files a.pdf b.pdf [--dry-run]

環境變數:
    ZENODO_TOKEN   必要。需 deposit:write + deposit:actions scope。
    ZENODO_CONCEPT 必要。concept record id(非 DOI 字串),例如 19994787。

`--dry-run` 會做完「建新版本 + 上傳檔案 + 寫 metadata」但**不發佈**,留下草稿供人工檢查。
草稿不會產生 DOI,可在 Zenodo 後台捨棄。發佈是不可逆的,所以預設行為要能先演練。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://zenodo.org/api"


def _req(method: str, url: str, token: str, *, data: bytes | None = None,
         content_type: str | None = None, timeout: int = 300):
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + token)
    if content_type:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read()
            return resp.status, (json.loads(body) if body else {})
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:600]
        # 刻意把 Zenodo 的錯誤訊息原樣印出 —— 這類 API 的失敗原因(scope 不足、
        # metadata 欄位缺漏)只有它自己說得清楚,包裝過就查不到了。
        sys.exit("FATAL: %s %s -> HTTP %d\n%s" % (method, url, e.code, detail))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True, help="這一版的版本字串,例如 0.4.1")
    ap.add_argument("--files", required=True, nargs="+", help="要上傳的 PDF 路徑")
    ap.add_argument("--dry-run", action="store_true", help="建草稿但不發佈")
    args = ap.parse_args()

    token = os.environ.get("ZENODO_TOKEN", "").strip()
    concept = os.environ.get("ZENODO_CONCEPT", "").strip()
    if not token:
        return int(bool(sys.stderr.write("FATAL: 缺 ZENODO_TOKEN\n"))) or 1
    if not concept.isdigit():
        return int(bool(sys.stderr.write("FATAL: ZENODO_CONCEPT 需為 record id 數字\n"))) or 1

    missing = [f for f in args.files if not os.path.isfile(f)]
    if missing:
        sys.exit("FATAL: 找不到檔案 %s" % missing)

    # concept id 解析到目前最新版 —— 新版本要從它長出來,DOI 血緣才連得上
    _, latest = _req("GET", "%s/records/%s" % (API, concept), token)
    latest_id = latest.get("id")
    print("[zenodo] concept %s -> 目前最新 record %s" % (concept, latest_id))

    _, nv = _req("POST", "%s/deposit/depositions/%s/actions/newversion" % (API, latest_id), token)
    draft_url = (nv.get("links") or {}).get("latest_draft") or ""
    draft_id = draft_url.rstrip("/").rsplit("/", 1)[-1]
    if not draft_id.isdigit():
        sys.exit("FATAL: 取不到 latest_draft(拿到 %r)" % draft_url)
    print("[zenodo] 新版本草稿 id=%s" % draft_id)

    _, draft = _req("GET", "%s/deposit/depositions/%s" % (API, draft_id), token)
    bucket = (draft.get("links") or {}).get("bucket")
    if not bucket:
        sys.exit("FATAL: 草稿沒有 bucket link")

    for path in args.files:
        name = os.path.basename(path)
        with open(path, "rb") as fh:
            payload = fh.read()
        status, _ = _req("PUT", "%s/%s" % (bucket, name), token,
                         data=payload, content_type="application/octet-stream")
        print("[zenodo] 上傳 %s (%d bytes) -> HTTP %d" % (name, len(payload), status))

    # 新版本的 version 欄位會是空的,不補就會顯示空白
    meta = dict(draft.get("metadata") or {})
    meta["version"] = args.version
    _, updated = _req("PUT", "%s/deposit/depositions/%s" % (API, draft_id), token,
                      data=json.dumps({"metadata": meta}).encode("utf-8"),
                      content_type="application/json")

    files_now = [f.get("filename") for f in (updated.get("files") or [])]
    print("[zenodo] version=%s  檔案=%s" % ((updated.get("metadata") or {}).get("version"), files_now))

    if not any(str(f).lower().endswith(".pdf") for f in files_now):
        sys.exit("FATAL: 草稿裡沒有任何 PDF —— 發佈了也不會有 citation_pdf_url,中止")

    if args.dry_run:
        print("[zenodo] --dry-run:草稿 %s 保留未發佈,請人工檢查後於後台捨棄或發佈" % draft_id)
        return 0

    _, pub = _req("POST", "%s/deposit/depositions/%s/actions/publish" % (API, draft_id), token)
    print("[zenodo] 已發佈  DOI=%s  record=%s" % (pub.get("doi"), pub.get("record_id") or pub.get("id")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
