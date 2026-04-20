---
title: "第 6 章 — 三層テナント分離"
chapter: 6
lang: ja
license: CC-BY-NC-4.0
---

# 第 6 章 — 三層テナント分離

> マルチテナント SaaS で最もニュースになるのは「機能不足」ではなく「A が B のデータを見た」。本章は底線。

## 6.1 脅威モデル

| 脅威 | 攻撃路径 | 緩和層 |
|-----|---------|-------|
| T1 ヘッダ偽造 | `X-Tenant-ID` すり替え | L1 |
| T2 SQL Injection | WHERE 回避 | L2 + L3 |
| T3 内部人員ミス | 管理者が他テナント誤検索 | L2 |
| T4 アプリバグ | 新 endpoint が tenant 条件忘れ | L2 + L3 |

4 種とも 2024–2025 年に実例あり。単層では不十分。

## 6.2 Layer 1: App 層身分注入

```typescript
export async function tenantMiddleware(req, res, next) {
  const apiKey = req.headers['x-rag-api-key'];
  const claimed = req.headers['x-tenant-id'];
  if (!apiKey || !claimed) return res.status(401).json({error:'missing credentials'});
  const owner = await db.query(
    'SELECT tenant_id FROM api_keys WHERE key_hash=$1 AND revoked_at IS NULL',
    [hash(apiKey)],
  );
  if (!owner.rows[0] || owner.rows[0].tenant_id !== claimed) {
    return res.status(403).json({error:'tenant mismatch'});
  }
  req.tenant_id = claimed;
  next();
}
```

- API key と tenant の紐付け：他テナント詐称不可
- Key は SHA-256 ハッシュで保存：DB 漏洩 ≠ key 漏洩

## 6.3 Layer 2: PostgreSQL RLS

```sql
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
CREATE POLICY documents_tenant ON documents
  USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
  WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true)::uuid);
```

```typescript
async function withTenantConnection(tid, fn) {
  const c = await pool.connect();
  try {
    await c.query(`SET LOCAL app.current_tenant_id = '${tid}'`);
    return await fn(c);
  } finally { c.release(); }
}
```

### 3 つの罠

1. **プール設定漏れ**：`SET LOCAL` 必須（`SET` ではない）
2. **Superuser バイパス**：PostgreSQL superuser は RLS 無視 — アプリは絶対 superuser で接続しない
3. **`BYPASSRLS` 属性**：CI チェック

```sql
SELECT rolname FROM pg_roles WHERE rolbypassrls = true AND rolcanlogin = true;
```

## 6.4 Layer 3: Query 層述語

RLS があっても明示的 `WHERE tenant_id = $x` を要求：

```typescript
// ❌ RLS だけに依存
const docs = await client.query('SELECT * FROM documents');

// ✅ 二重保険
const docs = await client.query(
  'SELECT * FROM documents WHERE tenant_id = $1', [tenantId]
);
```

理由：RLS が誤って無効化される可能性、コードレビュー容易、optimizer がインデックスを活用。ORM ラッパーで強制し、raw `client.query()` を Linter で禁止。

## 6.5 コネクションプールと search_path

```typescript
async function acquireClient(tenantId) {
  const c = await pool.connect();
  await c.query('RESET app.current_tenant_id');
  await c.query(`SET LOCAL app.current_tenant_id = '${tenantId}'`);
  await c.query('SET LOCAL search_path = public');
  return c;
}
```

## 6.6 Superuser バイパスの現実

- 本番 superuser は CTO + SRE lead のみ、bastion 経由でセッション録画
- DB プロキシが superuser クエリを傍受、`WHERE tenant_id` なければ自動付加または拒否

## 6.7 テスト

```sql
-- テナントテーブルすべてに RLS
SELECT schemaname, tablename, rowsecurity FROM pg_tables
WHERE schemaname='public' AND tablename IN ('documents','chunks','embeddings','wiki_pages','queries');
```

```typescript
it('テナント横断読み取りを防ぐ', async () => {
  const tA = await createTenant();
  const tB = await createTenant();
  const doc = await createDocument(tA.id, 'secret A');
  const r = await withTenant(tB.id, db =>
    db.selectFrom('documents').where('id','=',doc.id).executeTakeFirst());
  expect(r).toBeUndefined();
});
```

四半期ごとにレッドチーム演習：SQLi、ヘッダ偽造、JWT 改ざん、競合状態。

---

## 本章のポイント

- 三層防御、欠けば穴増
- Layer 1: API key ↔ tenant 紐付け検証
- Layer 2: PostgreSQL RLS + FORCE、superuser 接続禁止
- Layer 3: ORM 強制 tenant-scope、raw query 禁止
- プールは `SET LOCAL` + 取得毎 reset
- CI で横断読み書きテスト

---

**ナビゲーション**：[← 第 5 章](./ch05-fallback-economics.md) · [📖 目次](./README.md) · [第 7 章 →](./ch07-ingestion.md)
