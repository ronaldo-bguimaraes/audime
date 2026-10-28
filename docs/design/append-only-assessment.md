# Assessment — Append-only RAW Layer Proposal

> **Data**: 2026-07-05
> **Status**: Assessed (recommendation: **reject pure append-only, adopt hybrid elements**)
>
> Nota: este documento é histórico. Os nomes de papel (`product_owner`, `tech_lead`,
> `qa_engineer`…) referem-se ao processo de squad aposentado em 2026-10 e são
> preservados como registro de quem levantou cada ponto.

---

## Table of Contents

1. [Pro/Con Comparison](#1-procon-comparison)
2. [Schema Mapping](#2-schema-mapping)
3. [Critical Blockers](#3-critical-blockers)
4. [Hybrid Recommendations](#4-hybrid-recommendations)
5. [Updated Recommendation](#5-updated-recommendation)
6. [Plan Amendments](#6-plan-amendments)

---

## 1. Pro/Con Comparison

### SCD Type 1 (Current Plan)

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| **Complexity** | ✅ Low | UPDATE by PK, same `id_nota` throughout. No query rewrites. |
| **Auditability** | ✅ Sufficient | `raw.importacao` preserves every HTML download with SHA-256. Old Nota state can be reconstructed by re-parsing old HTML. |
| **Storage growth** | ✅ Negligible | ~3KB per nota, 6000 existing rows ~18MB. 10 reprocesses per nota over 5 years ~180MB total. Trivial. |
| **Query overhead** | ✅ None | `SELECT * FROM raw.nota WHERE id_usuario = ?` — unchanged. |
| **UNIQUE safety net** | ✅ Preserved | `UNIQUE(chave, id_usuario)` prevents accidental duplicates on normal extraction. |
| **Data migration** | ✅ Minimal | 2 new nullable columns on `core.extracao`. Zero changes to `raw`. |
| **id_nota stability** | ✅ Stable | Frontend bookmarks, fatura links, API references all remain valid. |
| **Staging impact** | ⚠️ Manageable | FK relaxation needed (already planned as CAT-RP-021). Staging pipeline UPDATE (CAT-RP-022). |
| **Effort** | ✅ ~10 days | Well-understood scope. Single sprint. |

### Append-only RAW Layer (Proposed)

| Criterion | Score | Rationale |
|-----------|-------|-----------|
| **Complexity** | 🔴 High | Every query needs `ROW_NUMBER()` or `WHERE is_current = TRUE`. All endpoints rewritten. |
| **Auditability** | ✅✅ Full | Every parsed version retained. No need to re-parse HTML for historical state. |
| **Storage growth** | ✅ Negligible | Same math — ~180MB over 5 years. Not a concern. |
| **Query overhead** | 🔴 Permanent tax | Every "get current" query requires window function or MV. Developers must remember the filter. |
| **UNIQUE safety net** | 🔴 Lost | Constraint must be dropped, removing duplicate protection for normal extractions. |
| **Data migration** | 🔴 Complex | Drop constraint, add version columns, backfill 6000 rows, recreate indexes. Migration downgrade may fail if versions exist. |
| **id_nota stability** | 🔴 Broken | Changes on every reprocess. Breaks frontend, fatura linking, analytics drill-down. Requires UUID or redirect mitigation. |
| **Staging impact** | 🔴 Severe | `staging.nota_normalizada.id_nota` FK points to old version. Forces staging versioning question now. |
| **Effort** | 🔴 ~20–26 days | 2–2.5× SCD Type 1. Multi-sprint scope. |

### Verdict

The squad **unanimously recommends SCD Type 1** for this sprint. Append-only is architecturally elegant for data-lake/medallion architectures but creates disproportionate complexity for an operational personal finance app where the primary access pattern is "show me my current data."

However, the squad identified several **hybrid elements** from the append-only proposal that should be adopted.

---

## 2. Schema Mapping

How current tables would map under the append-only proposal:

### `raw.nota`

| Current (SCD-1) | Append-only Equivalent |
|-----------------|----------------------|
| `id_nota` (PK) | Unchanged — still PK |
| `chave` (varchar 44) | Unchanged |
| `id_usuario` | Unchanged |
| `UNIQUE(chave, id_usuario)` | **DROPPED** |
| *(no version columns)* | New: `version INTEGER DEFAULT 1` |
| *(no current flag)* | New: `is_current BOOLEAN DEFAULT TRUE` |
| *(no lineage)* | New: `previous_version_id BIGINT → raw.nota.id_nota` (nullable) |
| *(no stable ref)* | New: `nota_uuid UUID NOT NULL UNIQUE` (stable across versions) |
| Index: unique constraint | Index: `UNIQUE(chave, id_usuario) WHERE is_current = TRUE` (partial PG index) |

### `raw.item_nota`

**Status: Already append-compatible — no schema changes needed.**

```
Extraction 1 → Nota(id=1) → ItemNota(id=1, id_nota=1), ItemNota(id=2, id_nota=1)
Extraction 2 (reprocess) → Nota(id=42) → ItemNota(id=3, id_nota=42), ItemNota(id=4, id_nota=42)
```

Each version's items point to their own `id_nota`. Old items naturally preserved with the old Nota version.

### `raw.importacao`

**Status: Already append-only — no changes needed.** Each download already creates a new row. This is the existing audit trail.

### `staging.nota_normalizada`

| Current | Append-only Problem |
|---------|-------------------|
| `id_nota → raw.nota.id_nota` | After reprocess, this FK points to **old** version (not current) |
| Single row per `id_nota` | Staging would accumulate duplicates: one per version |

**Under append-only, staging must either:**
- **(a)** UPDATE `id_nota` reference to latest raw version (mutable FK — messy)
- **(b)** Become versioned itself (SCD-2 on staging — larger scope)
- **(c)** Deduplicate by `chave_acesso` instead of `id_nota` (staging becomes canonical)

### `staging.item_normalizado`

Same problem as `nota_normalizada`: `id_item_nota → raw.item_nota.id_item_nota` would point to the old item version.

---

## 3. Critical Blockers

These are the reasons the squad recommends **against** pure append-only in this sprint.

### 🔴 Blocker 1: Business Key Ambiguity (tech_lead)

The proposal uses `(chave, id_usuario)` as the business key for `ROW_NUMBER() PARTITION BY`. But `chave` (the NFC-e access key) is **parsed from HTML** and can be wrong. If a parser fix changes the `chave` on reprocess:

| Scenario | Old chave | New chave | Same partition? |
|----------|-----------|-----------|-----------------|
| Parser was correct | `123...` | `123...` | ✅ Same |
| Parser extracted wrong field | `abc...` | `321...` | ❌ **Different** |

**Result**: The old (wrong) Nota is still "current" under its old chave partition. The new (correct) Nota starts a new partition. Now you have **two "current" Notas** for the same real-world invoice. The append-only model cannot detect that the new row replaces the old one when the identity key itself was wrong.

**Mitigation**: Don't use a business key on RAW at all. RAW is an event log, not an entity store. Business keys belong at the staging layer.

### 🔴 Blocker 2: `id_nota` Instability (developer, qa_engineer)

Under append-only, every reprocess generates a new `id_nota` PK. This breaks:

| Consumer | Impact |
|----------|--------|
| Frontend bookmarks | `/notas/5` → 404 after reprocess |
| Fatura linking | `PATCH /notas/{id}/vincular-fatura` links old version |
| Analytics drill-down | References stale version |
| API caching | Client-side cache has stale IDs |
| Staging FKs | Point to old version |

**No cheap mitigation exists**. UUID stable references, redirect chains, or full API rewrites are all multi-day efforts.

### 🔴 Blocker 3: UNIQUE Constraint Loss (product_manager, qa_engineer)

The `UNIQUE(chave, id_usuario)` constraint is a **critical data quality gate**:

- **Normal extraction**: User accidentally runs the same URL twice → `IntegrityError` → clean error. Without the constraint, both succeed silently → duplicate entries.
- **Parser regression**: Bad parser produces wrong data → extraction fails on constraint → user knows something is wrong. Without it, bad data enters silently.
- **TOC/TOU race**: Even with app-level dedup (SELECT before INSERT), two concurrent requests can race past the check. The UNIQUE constraint eliminates this race.

### 🔴 Blocker 4: Staging Layer Breakage (tech_lead, product_owner)

`staging.nota_normalizada.id_nota → raw.nota.id_nota` is a **hard FK**. Under append-only:

1. After first reprocess, staging FK points to old `id_nota` (stale data)
2. The `normalizar_notas()` pipeline currently skips by `id_nota` → would create duplicates
3. The FK prevents dropping the old Nota row (not that you'd want to, but still)
4. Fixing this forces the **full SCD-2 on staging** question now, not later

The current plan already fixes the staging FK issue (CAT-RP-021, CAT-RP-022). Append-only makes it worse.

### ⚠️ Blocker 5: Existing Data Migration Footprint (developer)

| Step | Complexity |
|------|-----------|
| Drop `UNIQUE(chave, id_usuario)` | Simple ALTER, but **downgrade fails** if multiple versions exist later |
| Add `version`, `is_current`, `previous_version_id` | 3 new columns, index creation |
| Add `nota_uuid` | New column, must backfill UUIDs for 6000+ rows |
| Create partial unique index | `CREATE UNIQUE INDEX ... WHERE is_current = TRUE` |
| Backfill existing data | `is_current = TRUE, version = 1` for all 6000 rows |
| Migration downgrade | Restoring UNIQUE constraint requires deduplication if any reprocess happened → could fail |

**Estimate**: ~3× the migration work of SCD Type 1.

### 🔴 Blocker 6: Effort and Regression Risk (developer, qa_engineer)

| Dimension | SCD Type 1 | Append-only |
|-----------|-----------|-------------|
| Implementation effort | ~10 days | ~20–26 days (2–2.5×) |
| Files changed | ~10 | ~12–14 |
| Test scenarios | ~23 | ~31 (8 new) |
| Existing tests broken | 0 expected | 10–15 expected |
| Query audit needed | None | Full codebase |
| Frontend impact | None | Significant (API contract breaks) |

---

## 4. Hybrid Recommendations

While the squad recommends **rejecting pure append-only**, several elements from the proposal are worth adopting as improvements to the SCD Type 1 plan.

### ✅ Adopt: Invert Item Delete/Insert Order (from product_owner)

**Current plan**: DELETE old items, then INSERT new items. Risk: if process fails between DELETE and INSERT, items are lost.

**Recommended change**: INSERT new items FIRST, then DELETE old items that are NOT in the new set.

```python
# Before (SCD Type 1 plan):
db.query(ItemNota).filter(ItemNota.id_nota == nota.id_nota).delete()
for item_data in nota_extraida.items:
    db.add(ItemNota(**item_data, id_nota=nota.id_nota, ...))

# After (safer):
new_item_ids = []
for item_data in nota_extraida.items:
    new_item = ItemNota(**item_data, id_nota=nota.id_nota, ...)
    db.add(new_item)
    db.flush()
    new_item_ids.append(new_item.id_item_nota)
# Now delete only items NOT in the new set:
db.query(ItemNota).filter(
    ItemNota.id_nota == nota.id_nota,
    ~ItemNota.id_item_nota.in_(new_item_ids)
).delete(synchronize_session=False)
```

Or even simpler: use `SAVEPOINT` around the pair, or keep the existing order but document the transactional guarantee (the DELETE+INSERT are in the same transaction; a failure before commit rolls back both).

### ✅ Adopt: Staging Version Awareness (from tech_lead)

**Current plan**: Staging pipeline UPDATEs in-place (CAT-RP-022). This works with SCD Type 1.

**Hybrid improvement**: Even with SCD Type 1 on raw, staging should be designed so it could later adopt SCD Type 2 without re-architecture. Implementation suggestions:

- Make `staging.nota_normalizada.id_nota` **not** rely on raw PK stability — this is already in CAT-RP-021
- Add a **`chave_acesso` column** to staging (already exists) as the dedup key
- The staging pipeline should later support `valid_from`/`valid_to`/`is_current` columns (deferred to Phase 2)

### ✅ Adopt: `reprocess_reason` Column (from product_owner)

Add an optional text field documenting *why* the reprocess was triggered:

```python
reprocess_reason = sa.Column(sa.Text, nullable=True)
```

Stored in `core.extracao` alongside `reprocess_count` and `reprocessed_at`. Helps users understand which parser fix prompted the reprocess.

### ✅ Adopt: Immutability Principle for `raw.importacao` (from append-only proposal)

Already satisfied — `raw.importacao` is already append-only. Document this explicitly as a design invariant:
> `raw.importacao` rows are NEVER updated or deleted. They are the immutable audit log of all downloads.

### ❌ Reject: Full Append-only RAW Layer

The blockers in §3 are too severe for this sprint. Defer to a future "RAW layer versioning" sprint if:
- Full parsed-history audit trail becomes a user requirement
- Staging layer has been migrated to SCD Type 2
- The effort (~20+ days) can be scoped as a dedicated sprint

### ❌ Reject: Dropping UNIQUE(chave, id_usuario)

The constraint is too valuable as a data quality gate. Keep it.

### ❌ Reject: `is_current` / `version` on raw.nota

These belong on `staging` (Phase 2 SCD Type 2). The raw layer is operational — staging is analytical.

### ❌ Reject: `ROW_NUMBER()` for latest-state derivation

Without version columns on raw, there's no stable business key to partition by (see Blocker 1). Derivation logic belongs in staging/analytics.

### ⚠️ Accept conditionally: Safer failure recovery

**From product_owner's risk assessment**: The SCD Type 1 plan's DELETE+INSERT for items has a theoretical data-loss window if the process fails between DELETE and INSERT, before the transaction commits.

**Resolution**: The plan's transaction design (§3.4) already handles this:

```
Step 1: Create Importacao → db.commit() ← ALWAYS persisted (download record only)
Step 2: Parse HTML (in-memory, no DB impact)
Step 3: upsert_nota() (UPDATE/DELETE/INSERT) → in transaction
Step 4: db.commit() ← atomic: all raw + staging changes or none
Step 5: Status = DONE → db.commit()
```

If steps 2–4 fail before step 4's commit, the transaction is rolled back. The DELETE never becomes visible. This is safe. **Document this guarantee explicitly** in the worker code and acceptance criteria.

---

## 5. Updated Recommendation

### Primary Recommendation: **Proceed with SCD Type 1 (as planned)**

The existing plan at `plan.md` is sound. The squad's analysis confirms:

| Squad Member | Verdict |
|-------------|---------|
| **product_manager** | SCD Type 1 wins on all dimensions. Append-only adds complexity for no user-facing benefit. |
| **tech_lead** | Append-only has critical blockers (business key ambiguity, staging FK instability, id_nota breakage). SCD Type 1 with hybrid improvements. |
| **product_owner** | SCD Type 1 scores 4.5/5 vs append-only 2.5/5 against original goals. Staging breakage is a dealbreaker. |
| **developer** | SCD Type 1 = ~10 days. Append-only = ~20–26 days (2–2.5× effort). Multiple code-level blockers. |
| **qa_engineer** | SCD Type 1 is substantially easier to test. Append-only breaks 10–15 existing tests and requires full query audit. |

### Secondary Recommendation: Adopt Hybrid Elements

Three specific improvements to the current plan:

1. **Safer item replacement** — INSERT new items, THEN DELETE old (instead of DELETE-then-INSERT)
2. **Staging double-dedup** — staging pipeline deduplicates by `chave_acesso` in addition to `id_nota`, making it resilient to future versioning
3. **Document `importacao` immutability** — explicitly state that `raw.importacao` is append-only and serves as the immutable audit log

### Deferred: Full Append-only RAW

If the team wants to pursue append-only in the future, the prerequisites are:
1. Staging layer already on SCD Type 2
2. Stable business key mechanism (not `(chave, id_usuario)` alone)
3. UUID-based stable references for all frontend-facing APIs
4. Dedicated sprint with 20+ day scope

---

## 6. Plan Amendments

### Amendment 1: CAT-RP-006 — Worker upsert strategy (safer order)

**Change**: In the item replacement logic, INSERT new items **before** DELETEing old ones. Update the pseudocode in §3.3:

```python
# 3. Replace raw items (INSERT first, THEN DELETE)
new_items = []
for item_data in nota_extraida.items:
    new_item = ItemNota(**item_data, id_nota=nota.id_nota, id_usuario=id_usuario)
    db.add(new_item)
    db.flush()
    new_items.append(new_item)

# Now delete items NOT in the new set (avoids data-loss window)
db.query(ItemNota).filter(
    ItemNota.id_nota == nota.id_nota,
    ~ItemNota.id_item_nota.in_([i.id_item_nota for i in new_items])
).delete(synchronize_session=False)
```

**Rationale**: If the process fails between DELETE and INSERT, the transaction rolls back — so the original order is actually safe within a transaction. But the INSERT-first order is more robust against future refactors that might split the transaction.

### Amendment 2: CAT-RP-022 — Transform pipeline (dual dedup)

**Change**: Update `normalizar_notas()` to deduplicate by **both** `id_nota` and `chave_acesso`:

```python
# Before (current plan):
staging_nota = db.query(NotaNormalizada).filter_by(id_nota=nota.id_nota).first()

# After (hybrid — resilient to future changes):
staging_nota = db.query(NotaNormalizada).filter(
    or_(
        NotaNormalizada.id_nota == nota.id_nota,
        NotaNormalizada.chave_acesso == nota.chave
    )
).first()
```

**Rationale**: If a future sprint adopts versioning on staging, the dedup-by-chave logic is already in place.

### Amendment 3: New CAT-RP-028 — Document `importacao` immutability

**New acceptance criterion**:

> **CAT-RP-028 — `raw.importacao` is append-only and immutable**
>
> **Condition**: The `raw.importacao` table is explicitly documented as an append-only, immutable audit log. No code path shall UPDATE or DELETE an `importacao` row after creation. The only write operation is INSERT.
>
> **Evidence**: A comment in the `Importacao` model class documents this invariant. Code review confirms no UPDATE or DELETE statements target `importacao` rows.
>
> **Test**: Integration test verifies that after reprocess, all `importacao` rows for an `id_extracao` are intact and have distinct `imported_at` timestamps.

### Amendment 4: CAT-RP-008 — Rollback guarantee documentation

**Change**: Add explicit documentation that the worker's transaction design guarantees:

> The DELETE of old `raw.item_nota` rows and INSERT of new ones occur **within the same database transaction** as the Nota UPDATE and staging updates. If any step in the upsert fails, the entire transaction is rolled back, and old data remains intact. The `raw.importacao` row created in step 1 is the only persistent side effect of a failed reprocess, and it is preserved intentionally for download auditing.

### Summary of Plan Changes

| Change | Type | Impact |
|--------|------|--------|
| Item replacement order (INSERT-first) | Implementation detail | Reduces theoretical risk window |
| Staging dual dedup (id_nota + chave) | Implementation detail | Future-proofs for Phase 2 SCD-2 |
| CAT-RP-028 (importacao immutability) | New criterion | Documentation + 1 test |
| CAT-RP-008 documentation | Clarification | No code change |
| All other SCD Type 1 plan elements | **No change** | Retained as-is |

---

## Appendix: Squad Members and Their Findings

| Squad Member | Key Insight |
|-------------|-------------|
| **product_manager** | UNIQUE constraint is a critical data quality gate. Dropping it introduces silent duplicate risk. SCD Type 1 wins on all product dimensions. |
| **tech_lead** | Business key ambiguity (chave changes on parser fix) is the fatal flaw. Window function partitioning breaks when the partition key changes. |
| **product_owner** | Staging FK breakage is a dealbreaker. Append-only would create more problems than it solves. Recommended INSERT-before-DELETE for items. |
| **developer** | Effort is 2–2.5× for append-only. `id_nota` instability is the #1 code-level blocker. Every API endpoint needs rewriting. |
| **qa_engineer** | Append-only breaks 10–15 existing tests. Requires 8 new complex scenarios vs 0 for SCD Type 1. Regression risk is HIGH vs LOW. |
