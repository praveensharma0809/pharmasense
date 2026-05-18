# PharmaSense Database Schema (Star Schema)

## Entity-Relationship Diagram
┌─────────────────────────────────────┐
│          PRODUCTS (Dimension)        │
├─────────────────────────────────────┤
│ • product_id (PK)                    │
│ • product_code (UNIQUE)              │
│ • product_name                       │
│ • category                           │
│ • therapeutic_class                  │
│ • unit_price                         │
└──────────────┬──────────────────────┘
│
│ FK (product_id)
│
┌──────────────▼──────────────────────┐        ┌─────────────────────────────────────┐
│         SALES (Fact Table)          │        │       REGIONS (Dimension)            │
├─────────────────────────────────────┤        ├─────────────────────────────────────┤
│ • sale_id (PK)                      │        │ • region_id (PK)                     │
│ • sale_datetime                     │        │ • region_name                        │
│ • product_id (FK) ─────────────────►│        │ • country                            │
│ • customer_id (FK) ─────┐           │        │ • zone                               │
│ • quantity               │           │        └──────────────┬──────────────────────┘
│ • revenue                │           │                       │
│ • year                   │           │                       │ FK (region_id)
│ • month                  │           │                       │
│ • hour                   │           │        ┌──────────────▼──────────────────────┐
│ • weekday                │           │        │       CUSTOMERS (Dimension)          │
└──────────────────────────┘           │        ├─────────────────────────────────────┤
│        │ • customer_id (PK)                   │
└───────►│ • customer_name                      │
│ • customer_type                      │
│ • region_id (FK)                     │
└─────────────────────────────────────┘

## Table Definitions

### 1. products (Dimension Table)
**Purpose:** Master list of pharmaceutical products

| Column | Type | Constraints | Description |
|---|---|---|---|
| product_id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| product_code | TEXT | UNIQUE, NOT NULL | ATC drug code (M01AB, N02BA, etc.) |
| product_name | TEXT | NOT NULL | Human-readable product name |
| category | TEXT | NOT NULL | Drug category (Pain Relief, Mental Health, etc.) |
| therapeutic_class | TEXT | | Medical classification (NSAIDs, Analgesics, etc.) |
| unit_price | REAL | NOT NULL | Price per unit |

**Sample Data:**
product_idproduct_codeproduct_namecategoryunit_price1M01ABAnti-inflammatory (Indometacin)Pain Relief12.502N02BEParacetamolPain Relief6.503N05BAnxiolyticsMental Health22.00

---

### 2. regions (Dimension Table)
**Purpose:** Geographic market segmentation

| Column | Type | Constraints | Description |
|---|---|---|---|
| region_id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| region_name | TEXT | NOT NULL | Region name (East Serbia, West Serbia, etc.) |
| country | TEXT | DEFAULT 'Serbia' | Country code |
| zone | TEXT | | Urban/Rural/Mixed classification |

**Sample Data:**
region_idregion_namecountryzone1North SerbiaSerbiaUrban2East SerbiaSerbiaMixed3Central SerbiaSerbiaUrban

---

### 3. customers (Dimension Table)
**Purpose:** Customer/account master

| Column | Type | Constraints | Description |
|---|---|---|---|
| customer_id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique identifier |
| customer_name | TEXT | NOT NULL | Customer name |
| customer_type | TEXT | NOT NULL | Hospital, Retail Pharmacy, Online Pharmacy |
| region_id | INTEGER | FOREIGN KEY → regions(region_id) | Geographic assignment |

**Sample Data:**
customer_idcustomer_namecustomer_typeregion_id1Hospital AHospital22Pharmacy MOnline Pharmacy13Pharmacy PRetail Pharmacy3

---

### 4. sales (Fact Table)
**Purpose:** Transactional sales records

| Column | Type | Constraints | Description |
|---|---|---|---|
| sale_id | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique transaction ID |
| sale_datetime | TEXT | NOT NULL | ISO timestamp (YYYY-MM-DD HH:MM:SS) |
| product_id | INTEGER | FOREIGN KEY → products(product_id) | Product sold |
| customer_id | INTEGER | FOREIGN KEY → customers(customer_id) | Buyer |
| quantity | REAL | NOT NULL | Units sold |
| revenue | REAL | NOT NULL | Total transaction value (quantity × price) |
| year | INTEGER | NOT NULL | Extracted for easy filtering |
| month | INTEGER | NOT NULL | 1-12 |
| hour | INTEGER | NOT NULL | 0-23 |
| weekday | TEXT | NOT NULL | Monday, Tuesday, etc. |

**Sample Data:**
sale_idsale_datetimeproduct_idcustomer_idquantityrevenueyearmonthhour12014-02-01 08:00:00240.6710.5520141822014-02-01 08:00:003140.403.2820141832014-02-01 08:00:004182.0013.00201418

---

## Indexes (Query Optimization)

```sql
CREATE INDEX idx_sales_datetime ON sales(sale_datetime);
CREATE INDEX idx_sales_product ON sales(product_id);
CREATE INDEX idx_sales_customer ON sales(customer_id);
CREATE INDEX idx_sales_year_month ON sales(year, month);
```

**Why these indexes:**
- `sale_datetime` — Time-series queries (monthly trends, date ranges)
- `product_id` — Product performance queries (top sellers, declining products)
- `customer_id` — Customer segmentation, Pareto analysis
- `(year, month)` — Composite index for period-based aggregations

---

## Sample Query Path

**Business Question:** *"Which region has the highest revenue for pain relief drugs?"*

**Query Flow:**

Start at: sales (fact table)
JOIN products ON product_id → Filter category = 'Pain Relief'
JOIN customers ON customer_id
JOIN regions ON region_id
GROUP BY region_name
SUM(revenue)
ORDER BY revenue DESC


**SQL:**
```sql
SELECT 
    r.region_name,
    SUM(s.revenue) AS total_revenue
FROM sales s
JOIN products p ON s.product_id = p.product_id
JOIN customers c ON s.customer_id = c.customer_id
JOIN regions r ON c.region_id = r.region_id
WHERE p.category = 'Pain Relief'
GROUP BY r.region_name
ORDER BY total_revenue DESC;
```

**Result:**
region_nametotal_revenueEast Serbia285,432.18Central Serbia231,109.55South Serbia189,221.33

---

## Design Rationale

### Why Star Schema?

**Star schema** (fact table + dimension tables) is the industry standard for analytics databases because:

1. **Query Performance:** Fewer joins than snowflake schema
2. **Business Logic:** Dimensions represent "who/what/where", facts represent "transactions"
3. **Flexibility:** Easy to add new dimensions without restructuring facts
4. **Aggregation-Friendly:** GROUP BY dimensions, SUM/AVG facts

### Why 3NF Normalization?

**Third Normal Form** eliminates redundancy:
- Product name stored **once** in `products`, not 66,381 times in `sales`
- Region info stored **once** in `regions`, not duplicated per customer
- **Result:** Smaller database, no update anomalies, referential integrity via foreign keys

### Why SQLite?

For a portfolio/demo project:
- **Zero configuration** — no server setup
- **Portable** — single `.db` file
- **Full SQL support** — window functions, CTEs, joins, indexes
- **Fast enough** — handles 100K+ rows easily

For production at scale (like real ZS work), this would be **PostgreSQL** or **Snowflake**.

---

## Schema Evolution Notes

If this were a production system, next steps would include:

1. **Time dimension table** — Separate calendar table for date-based analytics
2. **Supplier dimension** — Track which suppliers provide each product
3. **Promotion dimension** — Track discount campaigns and their impact
4. **Slowly Changing Dimensions (SCD)** — Track historical changes (e.g., customer changing regions)
5. **Partitioning** — Partition `sales` by year/month for query performance at scale
6. **Data quality constraints** — CHECK constraints on revenue > 0, quantity > 0