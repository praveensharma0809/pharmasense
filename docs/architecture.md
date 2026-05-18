# PharmaSense Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         RAW DATA LAYER                          │
│                                                                 │
│   ┌─────────────────────────────────────────────────────┐     │
│   │  Kaggle Pharma Sales Dataset (50K+ rows)            │     │
│   │  • Hourly sales data (2014)                         │     │
│   │  • 8 drug categories (ATC codes)                    │     │
│   │  • CSV format (2.6 MB)                              │     │
│   └─────────────────────────────────────────────────────┘     │
│                            │                                    │
└────────────────────────────┼────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ETL PIPELINE (Python)                     │
│                                                                 │
│   EXTRACT → TRANSFORM → LOAD                                   │
│   ────────────────────────────────────────────────────         │
│   • Read CSV with pandas                                       │
│   • Parse dates, handle nulls                                  │
│   • Melt wide format → long format                             │
│   • Create normalized dimensions (products, regions, customers)│
│   • Calculate revenue (quantity × price)                       │
│   • Insert into SQLite with foreign keys                       │
│                            │                                    │
└────────────────────────────┼────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATA WAREHOUSE (SQLite)                       │
│                                                                 │
│   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐     │
│   │  products    │   │   regions    │   │  customers   │     │
│   │  (8 rows)    │   │   (5 rows)   │   │  (20 rows)   │     │
│   └──────┬───────┘   └──────┬───────┘   └──────┬───────┘     │
│          │                  │                  │               │
│          └──────────────────┼──────────────────┘               │
│                             │                                  │
│                   ┌─────────▼─────────┐                        │
│                   │      sales        │                        │
│                   │  (66,381 rows)    │                        │
│                   │   fact table      │                        │
│                   └───────────────────┘                        │
│                                                                 │
│   • 3NF normalized schema                                      │
│   • Foreign key constraints                                    │
│   • Indexed on date, product_id                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQL ANALYTICS LAYER                          │
│                                                                 │
│   15 Business Questions (queries.sql)                          │
│   ────────────────────────────────────────                     │
│   • Top products by revenue (GROUP BY + JOIN)                  │
│   • Regional analysis (multi-table JOIN)                       │
│   • Month-over-month growth (LAG window function)              │
│   • Top 3 per region (ROW_NUMBER + PARTITION BY)               │
│   • Customer segmentation (CASE statements)                    │
│   • Pareto 80/20 analysis (cumulative SUM)                     │
│   • Cross-sell opportunities (self-join)                       │
│                            │                                    │
└────────────────────────────┼────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              DASHBOARD (Streamlit)                              │
│                                                                 │
│   • KPI cards ($1.56M revenue, 66K transactions)               │
│   • Product performance chart                                  │
│   • Regional breakdown                                         │
│   • Temporal trends (monthly, hourly)                          │
│   • Business insights dropdown                                 │
│      - Pareto analysis                                         │
│      - Customer segmentation                                   │
│      - MoM growth                                              │
│      - Cross-sell matrix                                       │
└─────────────────────────────────────────────────────────────────┘
```