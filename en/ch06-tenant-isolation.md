---
title: "Chapter 6 — Three-Layer Tenant Isolation"
chapter: 6
lang: en
license: CC-BY-NC-4.0
last_modified_at: '2026-04-20T09:41:51+08:00'
---


# Chapter 6 — Three-Layer Tenant Isolation

> The headlines about multi-tenant SaaS aren't "lacked features." They're "Customer A saw Customer B's data." This chapter is the floor.

## 6.1 Threat Model

| Threat | Attack path | Mitigating layer |
|--------|-------------|-----------------|
| T1 Forged header | Swap `X-Tenant-ID` | Layer 1 |
| T2 SQL injection | Bypass WHERE clause | Layer 2 + 3 |
| T3 Internal mistake | Admin runs cross-tenant query | Layer 2 |
| T4 App bug | New endpoint skips tenant filter | Layer 2 + 3 |

All four have real incidents in 2024–2025. No single layer suffices.

## 6.2 Layer 1: App Identity Injection

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

- API key binds to one tenant; cannot spoof another
- Key stored as SHA-256 hash; DB leak ≠ key leak

## 6.3 Layer 2: PostgreSQL RLS

```sql
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
CREATE POLICY documents_tenant ON documents
  USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
  WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true)::uuid);
```

App side:

```typescript
async function withTenantConnection<T>(tid: string, fn: (c: PgClient) => Promise<T>) {
  const c = await pool.connect();
  try {
    await c.query(`SET LOCAL app.current_tenant_id = '${tid}'`);
    return await fn(c);
  } finally { c.release(); }
}
```

### 6.3.1 Three Traps

1. **Pool setting leak**: use `SET LOCAL`, not `SET`
2. **Superuser bypass**: PostgreSQL superuser ignores all RLS — never connect app as superuser
3. **`BYPASSRLS` role attribute**: CI check:

```sql
SELECT rolname FROM pg_roles
WHERE rolbypassrls = true AND rolcanlogin = true;
```

## 6.4 Layer 3: Query-Level Predicates

Even with RLS we require explicit `WHERE tenant_id = $x`:

```typescript
// ❌ relies on RLS only
const docs = await client.query('SELECT * FROM documents');

// ✅ double insurance
const docs = await client.query(
  'SELECT * FROM documents WHERE tenant_id = $1', [tenantId]
);
```

Reasons: RLS could be accidentally disabled, code review is easier, and optimizer plan is more aggressive.

Enforced via ORM wrapper:

```typescript
class TenantScopedDb {
  constructor(private client: PgClient, private tenantId: string) {}
  documents() { return this.client.selectFrom('documents').where('tenant_id','=',this.tenantId); }
}
```

Linter bans raw `client.query()` calls.

## 6.5 Connection Pool and search_path

```typescript
async function acquireClient(tenantId: string) {
  const c = await pool.connect();
  await c.query('RESET app.current_tenant_id');
  await c.query(`SET LOCAL app.current_tenant_id = '${tenantId}'`);
  await c.query('SET LOCAL search_path = public');
  return c;
}
```

Monitoring: if any connection's `current_setting()` disagrees with request header → page.

## 6.6 Superuser Bypass Reality

- Production superuser access limited to CTO + SRE lead, via bastion with session recording
- DB proxy intercepts superuser queries; rejects or appends `WHERE tenant_id = pg_current_tenant()` automatically

## 6.7 Testing

CI runs per PR:

```sql
-- all tenant tables must have RLS
SELECT schemaname, tablename, rowsecurity FROM pg_tables
WHERE schemaname='public' AND tablename IN ('documents','chunks','embeddings','wiki_pages','queries');
```

```typescript
it('prevents cross-tenant read', async () => {
  const tA = await createTenant();
  const tB = await createTenant();
  const doc = await createDocument(tA.id, 'secret A');
  const r = await withTenant(tB.id, db =>
    db.selectFrom('documents').where('id','=',doc.id).executeTakeFirst());
  expect(r).toBeUndefined();
});
```

Quarterly red-team review: SQLi variants, header forgery, JWT tampering, race conditions.

---

## Key Takeaways

- Multi-tenant isolation is three-layer defense-in-depth; miss one = one extra hole
- Layer 1: validate API key ↔ tenant binding
- Layer 2: PostgreSQL RLS + FORCE, disable superuser app connection, CI check `BYPASSRLS`
- Layer 3: ORM-enforced tenant-scope, raw queries linted out
- Connection pool uses `SET LOCAL` + reset every acquire
- CI runs cross-tenant read/write tests on every PR

## References

- [PostgreSQL RLS][pg-rls] · [OWASP Multi-Tenancy][owasp]

[pg-rls]: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
[owasp]: https://cheatsheetseries.owasp.org/cheatsheets/Multi_Tenancy_Cheat_Sheet.html

---

**Navigation**: [← Ch 5](./ch05-fallback-economics.md) · [📖 Contents](./README.md) · [Ch 7 →](./ch07-ingestion.md)
