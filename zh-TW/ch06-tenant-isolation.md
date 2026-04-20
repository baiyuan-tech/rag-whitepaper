---
title: "Chapter 6 — 三層租戶隔離"
description: "App / DB / Query 三層縱深防禦、RLS 的陷阱、superuser bypass 問題、連線池"
chapter: 6
part: 3
word_count: 5200
lang: zh-TW
authors:
  - name: 百原科技
    url: https://baiyuan.io
license: CC-BY-NC-4.0
keywords:
  - Multi-Tenant
  - Row-Level Security
  - PostgreSQL
  - 租戶隔離
  - 資安
last_updated: 2026-04-20
---

# Chapter 6 — 三層租戶隔離

> 多租戶 SaaS 最常上新聞的不是功能不夠，是 A 客戶看到 B 客戶的資料。本章三層是百原的底線防禦。

## 目錄

- [6.1 威脅模型](#61-威脅模型)
- [6.2 Layer 1：App 層身分注入](#62-layer-1app-層身分注入)
- [6.3 Layer 2：PostgreSQL RLS](#63-layer-2postgresql-rls)
- [6.4 Layer 3：Query 層條件](#64-layer-3query-層條件)
- [6.5 連線池與 search_path 的坑](#65-連線池與-search_path-的坑)
- [6.6 Superuser Bypass 的現實](#66-superuser-bypass-的現實)
- [6.7 測試：怎麼驗證有效](#67-測試怎麼驗證有效)

---

## 6.1 威脅模型

我們把租戶隔離的威脅分四類：

| 威脅 | 攻擊路徑 | 緩解層 |
|-----|---------|-------|
| **T1 惡意租戶偽造 header** | 改 `X-Tenant-ID` 指向其他租戶 | L1 |
| **T2 SQL Injection** | 繞過應用層 WHERE 子句 | L2 + L3 |
| **T3 內部人員誤操作** | 工程師用 admin 角色直連 DB 查錯租戶 | L2 |
| **T4 應用 Bug** | 某新 endpoint 忘記加 tenant_id 條件 | L2 + L3 |

這四類都有真實發生過的產業案例。**任一層單獨都不夠，必須三層同時存在**。

## 6.2 Layer 1：App 層身分注入

每個對 RAG API 的請求都必須帶：

```http
POST /api/v1/ask HTTP/1.1
X-RAG-API-Key: <secret>
X-Tenant-ID: <uuid>
Content-Type: application/json

{"question": "..."}
```

middleware 驗證：

```typescript
export async function tenantMiddleware(req, res, next) {
  const apiKey = req.headers['x-rag-api-key'];
  const claimedTenantId = req.headers['x-tenant-id'];

  if (!apiKey || !claimedTenantId) {
    return res.status(401).json({ error: 'missing credentials' });
  }

  // 驗 API key 關聯的 tenant_id 與 header 中的 tenant_id 一致
  const keyOwner = await db.query(
    'SELECT tenant_id FROM api_keys WHERE key_hash = $1 AND revoked_at IS NULL',
    [hash(apiKey)],
  );

  if (!keyOwner.rows[0] || keyOwner.rows[0].tenant_id !== claimedTenantId) {
    return res.status(403).json({ error: 'tenant mismatch' });
  }

  req.tenant_id = claimedTenantId;
  next();
}
```

兩個關鍵細節：

1. **API Key 與 Tenant ID 綁定**：API Key 一定只能用於其所屬的 tenant，不能用 A 的 key 冒充 B
2. **Key 用 hash 儲存**：`api_keys.key_hash` 存 SHA-256，洩漏 DB 不等於洩漏 key

## 6.3 Layer 2：PostgreSQL RLS

所有租戶相關表啟用 Row-Level Security：

```sql
-- 每張表都這樣做
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;

CREATE POLICY documents_tenant ON documents
  USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
  WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true)::uuid);
```

- `USING` 控制讀（SELECT / UPDATE 過濾、DELETE 過濾）
- `WITH CHECK` 控制寫（INSERT 強制欄位相符）
- `FORCE ROW LEVEL SECURITY` **連表 owner 也會被 policy 約束**（3.4 會解釋為何這很重要）

應用層在每次連線拿出來後設定租戶：

```typescript
async function withTenantConnection<T>(
  tenantId: string,
  fn: (client: PgClient) => Promise<T>,
): Promise<T> {
  const client = await pool.connect();
  try {
    await client.query(`SET LOCAL app.current_tenant_id = '${tenantId}'`);
    return await fn(client);
  } finally {
    client.release();
  }
}
```

**`SET LOCAL`** 關鍵：只在目前 txn 內有效，`RELEASE` 歸還 pool 時自動重置。

### 6.3.1 RLS 的三個陷阱

**陷阱一：Connection Pool 洩漏設定**

如果沒用 `SET LOCAL`、改用 `SET`，設定會殘留到下次連線取出。於是 A 租戶設的 tenant_id 被 B 租戶的請求重用 — **直接跨租戶讀到對方資料**。

**陷阱二：superuser 自動繞過 RLS**

PostgreSQL 預設 `superuser` 角色忽略所有 RLS。**應用層千萬不能用 superuser 連線**。我們用的 `rag_app_user` 角色：

```sql
CREATE ROLE rag_app_user WITH LOGIN PASSWORD 'xxx' NOSUPERUSER;
GRANT CONNECT ON DATABASE rag TO rag_app_user;
GRANT USAGE ON SCHEMA public TO rag_app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO rag_app_user;
```

**陷阱三：`BYPASSRLS` 屬性**

角色可能誤設 `BYPASSRLS`：

```sql
-- 危險！
ALTER ROLE rag_app_user BYPASSRLS;
```

某些開發工具（DBeaver、DataGrip）安裝時會建 BYPASSRLS role。我們在 CI 加檢查：

```sql
SELECT rolname FROM pg_roles WHERE rolbypassrls = true AND rolcanlogin = true;
-- 如果回傳非空，CI 失敗
```

## 6.4 Layer 3：Query 層條件

即使有 RLS，我們仍要求每個 SQL 顯式加 `WHERE tenant_id = $x`：

```typescript
// ❌ 不要這樣寫（依賴 RLS）
const docs = await client.query('SELECT * FROM documents');

// ✅ 這樣寫（雙保險）
const docs = await client.query(
  'SELECT * FROM documents WHERE tenant_id = $1',
  [tenantId],
);
```

為什麼要雙保險？三個理由：

1. **RLS 可能被 Bug 關掉**（DBA 誤操作、migration 寫錯）
2. **Code Review 更好審**：看 SQL 就知道有沒有檔租戶
3. **Explain Plan 更準**：PostgreSQL 優化器看到顯式條件，走 index 更積極

我們的 ORM（Kysely / Drizzle）封裝 tenant-scoped queries：

```typescript
class TenantScopedDb {
  constructor(private client: PgClient, private tenantId: string) {}

  documents() {
    return this.client.selectFrom('documents')
      .where('tenant_id', '=', this.tenantId);
  }

  // ... 其他表 ...
}
```

**應用碼不允許直接 client.query()**，必須經過 TenantScopedDb。Linter 規則擋：

```javascript
// eslint-plugin-baiyuan/no-raw-query
'no-restricted-syntax': [
  'error',
  {
    selector: 'CallExpression[callee.object.name="client"][callee.property.name="query"]',
    message: 'Use TenantScopedDb instead of raw client.query',
  }
]
```

## 6.5 連線池與 search_path 的坑

Node.js 的 `pg` pool 預設 10 連線。當 A 租戶的 query 還沒結束、B 租戶搶到同一個 connection 時，如果沒正確 reset，`app.current_tenant_id` 會殘留。

我們三道保險：

1. **每次取連線強制 reset**：

```typescript
async function acquireClient(tenantId: string) {
  const c = await pool.connect();
  await c.query('RESET app.current_tenant_id');  // 清除殘留
  await c.query(`SET LOCAL app.current_tenant_id = '${tenantId}'`);
  return c;
}
```

2. **監控指標**：若某連線 `current_setting()` 與請求 header 不一致，立即告警

3. **`search_path` 同時鎖定**：避免跨 schema 汙染

```sql
SET LOCAL search_path = public;
```

## 6.6 Superuser Bypass 的現實

內部人員、DBA、SRE 偶爾需要 superuser 權限排錯。三個原則：

1. **Production DB 的 superuser 僅限 CTO + SRE lead**（兩人，用 KMS 托管）
2. **任何 superuser session 強制走 bastion**，bastion 錄 full session log
3. **Superuser 查詢自動加 tenant scope hint**（下一段）

### 6.6.1 即席查詢的租戶鎖定

我們的 DB proxy 攔 superuser 查詢，如果 SQL 沒有 `WHERE tenant_id` 且訪問了 tenant-scoped 表，**強制加 `AND tenant_id = pg_current_tenant()`** 或 reject。這是額外一層「人類友善的」保護。

## 6.7 測試：怎麼驗證有效

隔離測試是**不能靠手動跑一次就算**。我們 CI 每個 PR 跑：

### 6.7.1 RLS Enabled 檢查

```sql
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public' AND tablename IN (
  'documents', 'chunks', 'embeddings', 'wiki_pages',
  'queries', 'handoff_sessions', 'semantic_cache'
);
-- rowsecurity 必須全為 true
```

### 6.7.2 跨租戶查詢整合測試

```typescript
describe('tenant isolation', () => {
  it('prevents cross-tenant read', async () => {
    const tenantA = await createTenant();
    const tenantB = await createTenant();
    const docA = await createDocument(tenantA.id, 'secret A');

    const resultB = await withTenant(tenantB.id, db =>
      db.selectFrom('documents').where('id', '=', docA.id).executeTakeFirst()
    );
    expect(resultB).toBeUndefined();  // 必定看不到
  });

  it('prevents cross-tenant write', async () => {
    const tenantA = await createTenant();
    const tenantB = await createTenant();

    await expect(withTenant(tenantB.id, db =>
      db.insertInto('documents').values({
        tenant_id: tenantA.id,  // 故意寫錯
        title: 'x',
      }).execute()
    )).rejects.toThrow(/row-level security/);
  });
});
```

這兩個測試必須過才能 merge。

### 6.7.3 紅藍對抗

每季一次由外部滲透團隊（或內部紅藍演習）嘗試跨租戶讀取，測試覆蓋：

- SQLi 各種變形
- Header 偽造
- JWT tampering
- Race condition（並發請求搶 connection）

---

## 本章要點

- 多租戶 SaaS 隔離是三層縱深防禦，缺一不可
- Layer 1：App 層驗證 `X-RAG-API-Key` 與 `X-Tenant-ID` 綁定
- Layer 2：PostgreSQL RLS + `FORCE ROW LEVEL SECURITY`，禁用 superuser 連線
- Layer 3：ORM 強制 tenant-scoped，原生 query 被 Linter 擋下
- 連線池用 `SET LOCAL` 並每次 reset，防止設定洩漏
- CI 自動跑跨租戶讀寫測試，確保任何 PR 不破壞隔離

## 參考資料

- [PostgreSQL Row-Level Security 官方文件][pg-rls]
- [pg_roles catalog][pg-roles]
- [OWASP Multi-Tenancy Cheat Sheet][owasp]

[pg-rls]: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
[pg-roles]: https://www.postgresql.org/docs/current/view-pg-roles.html
[owasp]: https://cheatsheetseries.owasp.org/cheatsheets/Multi_Tenancy_Cheat_Sheet.html

## 修訂記錄

| 日期 | 版本 | 說明 |
|------|------|------|
| 2026-04-20 | v1.0 | 初稿 |

---

**導覽**：[← Ch 5: Fallback](./ch05-fallback-economics.md) · [📖 目次](../README.md) · [Ch 7: 知識攝取 →](./ch07-ingestion.md)
