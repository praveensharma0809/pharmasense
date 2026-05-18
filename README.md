# 💊 PharmaSense — Pharmaceutical Sales Intelligence Platform

> End-to-end data analytics platform: ETL pipeline + normalized SQL warehouse + interactive dashboard surfacing 15 business insights from 66K+ pharma sales transactions.

**Built for:** ZS Associates BTSA Application | **Tech Stack:** Python • SQL • SQLite • Streamlit • Pandas

---

## 📊 Dashboard Preview

![Dashboard Overview](docs/screenshots/Screenshot%202026-05-18%20104547.png)

**Key Features:**
- Real-time KPI tracking ($1.56M revenue across 66,381 transactions)
- Product performance analysis (8 drug categories)
- Regional revenue distribution (5 markets)
- Temporal trend analysis (monthly growth + hourly patterns)
- Advanced business analytics (Pareto 80/20, customer segmentation, cross-sell)

---

## 🎯 The Business Problem

A pharmaceutical company has 50K+ rows of hourly sales data scattered across 8 drug categories, but no structured way to answer critical business questions:

- Which products are declining? Which regions underperform?
- Who are our top customers driving 80% of revenue?
- What's our month-over-month growth trajectory?
- Which products sell together (cross-sell opportunities)?

**PharmaSense solves this** by transforming raw CSV data into a queryable SQL warehouse with 15 pre-built analytics queries, surfaced through an interactive dashboard.

---

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────────┐
│                    RAW DATA (Kaggle Dataset)                    │
│   50,532 rows • 8 drug categories • Hourly sales (2014)         │
└────────────────────────────┬────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│                  ETL PIPELINE (Python + Pandas)                 │
│   Extract → Transform → Load                                    │
│   • Parse dates, clean nulls                                    │
│   • Melt wide → long format                                     │
│   • Create normalized dimensions                                │
│   • Calculate revenue (quantity × price)                        │
└────────────────────────────┬────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│              DATA WAREHOUSE (SQLite - Star Schema)              │
│                                                                 │
│   products (8) ──┐                                              │
│   regions (5) ───┼──► sales (66,381) ◄─── customers (20)       │
│                  │       [Fact Table]                           │
│                  │                                              │
│   • 3NF normalized • Foreign keys • Indexed                     │
└────────────────────────────┬────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│               SQL ANALYTICS (15 Business Queries)               │
│   • Top products (JOIN + GROUP BY)                              │
│   • MoM growth (LAG window function)                            │
│   • Top 3 per region (ROW_NUMBER + PARTITION BY)                │
│   • Pareto 80/20 (cumulative SUM)                               │
│   • Cross-sell (self-join)                                      │
└────────────────────────────┬────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│                    STREAMLIT DASHBOARD                          │
│   Interactive UI • Real-time querying • Business insights       │
└─────────────────────────────────────────────────────────────────┘

---

## 🗄️ Database Schema (Star Schema)
┌─────────────────────────┐
│   products (Dimension)  │
├─────────────────────────┤
│ product_id (PK)         │
│ product_code (UNIQUE)   │
│ product_name            │
│ category                │
│ therapeutic_class       │
│ unit_price              │
└───────────┬─────────────┘
│ FK
│
┌───────────▼─────────────┐         ┌──────────────────────┐
│   sales (Fact Table)    │         │  regions (Dimension) │
├─────────────────────────┤         ├──────────────────────┤
│ sale_id (PK)            │         │ region_id (PK)       │
│ sale_datetime           │         │ region_name          │
│ product_id (FK) ────────┤         │ country              │
│ customer_id (FK) ───┐   │         │ zone                 │
│ quantity             │   │         └───────┬──────────────┘
│ revenue              │   │                 │ FK
│ year, month, hour    │   │                 │
└──────────────────────┘   │         ┌───────▼──────────────┐
│         │ customers (Dimension)│
│         ├──────────────────────┤
│         │ customer_id (PK)     │
└────────►│ customer_name        │
│ customer_type        │
│ region_id (FK)       │
└──────────────────────┘

**Design Principles:**
- **3NF Normalization** — Product info stored once, referenced 66K times via foreign keys
- **Star Schema** — Sales fact table + dimension tables for flexible analytics
- **Indexed** — Fast queries on `sale_datetime`, `product_id`, `customer_id`

---

## 📈 Key Insights Discovered

![Regional Analysis](docs/screenshots/Screenshot%202026-05-18%20104616.png)

**1. Product Concentration Risk**
- Top 3 products (Anxiolytics, Paracetamol, Respiratory Drugs) account for **~48% of total revenue**
- Declining products identified: opportunity for targeted intervention

**2. Regional Performance Gap**
- East Serbia leads with **$474K revenue** (+30% above average)
- North Serbia underperforms at **$157K** (−66% vs leader)
- **Actionable:** Reallocate sales resources to underperforming regions

![Customer Segmentation](docs/screenshots/Screenshot%202026-05-18%20104659.png)

**3. Customer Segmentation (RFM-Lite)**
- **VIP customers** (10 pharmacies) drive **51% of cumulative revenue**
- Hospital segment has **3.2x higher transaction volume** than retail
- **Actionable:** VIP retention program + hospital-focused sales strategy

**4. Temporal Patterns**

![Hourly Pattern](docs/screenshots/Screenshot%202026-05-18%20104639.png)

- Peak sales hours: **10 AM - 2 PM** (midday spike)
- Monthly revenue grew **+14% in Jan 2014** then stabilized
- **Actionable:** Optimize staffing and inventory for peak hours

**5. Cross-Sell Opportunities**
- Paracetamol + Anxiolytics co-occur in **38% of same-day purchases**
- **Actionable:** Bundle pricing for frequently paired products

---

## 🔍 The 15 Business Questions (SQL Analytics)

Each query demonstrates advanced SQL features:

| # | Question | SQL Features | Business Value |
|---|---|---|---|
| **Q1** | Top 10 products by revenue | `JOIN`, `GROUP BY`, `ORDER BY` | Identify revenue drivers |
| **Q2** | Monthly revenue trend | Date functions, aggregation | Track growth trajectory |
| **Q3** | Regional revenue contribution | Multi-table `JOIN`, subquery | Geographic performance |
| **Q4** | Avg order value by customer type | `JOIN`, `GROUP BY`, `AVG` | Customer segment analysis |
| **Q5** | Products sold per quarter | Date parsing, `COUNT DISTINCT` | Portfolio activity tracking |
| **Q6** | **Month-over-month growth rate** | **CTE + `LAG` window function** | Identify acceleration/deceleration |
| **Q7** | **Top 3 products per region** | **`ROW_NUMBER` + `PARTITION BY`** | Regional preferences |
| **Q8** | Customer segmentation (RFM) | `CASE` statements, segmentation | VIP identification |
| **Q9** | Products with declining sales | Multiple CTEs, period comparison | Early warning system |
| **Q10** | Day-of-week sales pattern | `CASE` + weekday extraction | Optimize staffing |
| **Q11** | **Running cumulative revenue** | **Window function (no PARTITION)** | Track toward targets |
| **Q12** | **Cross-sell opportunities** | **Self-join on sales** | Bundle recommendations |
| **Q13** | **Category YoY growth** | **`LAG` with `PARTITION BY`** | Strategic planning |
| **Q14** | **Pareto 80/20 analysis** | **Cumulative `SUM` + threshold** | Focus retention efforts |
| **Q15** | Hourly sales pattern | `GROUP BY` hour, aggregation | Delivery schedule optimization |

**View all queries:** [`sql/queries.sql`](sql/queries.sql)

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/praveensharma0809/pharmasense.git
cd pharmasense

# Install dependencies
pip install -r requirements.txt

# Run ETL pipeline (builds the database)
python src/etl.py

# Launch dashboard
streamlit run dashboard/app.py
```

**Requirements:** Python 3.9+, ~20 MB disk space

---

## 📂 Project Structure
pharmasense/
├── README.md                   # You are here
├── requirements.txt
├── data/
│   ├── raw/
│   │   └── saleshourly.csv     # Source dataset (50K rows)
│   └── processed/
│       └── pharmasense.db      # SQLite warehouse (66K sales)
├── src/
│   ├── database.py             # Schema initialization
│   ├── etl.py                  # Extract-Transform-Load pipeline
│   └── analytics.py            # Query execution wrapper
├── sql/
│   ├── schema.sql              # Table definitions + foreign keys
│   └── queries.sql             # 15 business analytics queries
├── dashboard/
│   └── app.py                  # Streamlit interactive UI
└── docs/
├── architecture.md         # System design
├── schema.md               # Database ER diagram
└── screenshots/            # Dashboard previews

---

## 🛠️ Tech Stack & Rationale

| Component | Technology | Why This Choice |
|---|---|---|
| **Language** | Python 3.10 | Industry standard for data pipelines |
| **Database** | SQLite | Zero-config, portable, supports advanced SQL |
| **ETL** | Pandas | Standard for data transformation |
| **SQL** | Raw SQL (no ORM) | Demonstrates SQL proficiency directly |
| **Dashboard** | Streamlit | Built for data apps, rapid iteration |
| **Version Control** | Git + GitHub | Industry standard |

---

## 💡 What I Learned Building This

**Technical Skills:**
- Designed a **normalized 3NF star schema** with proper foreign key constraints
- Wrote **15 production-grade SQL queries** including window functions (`LAG`, `ROW_NUMBER`), CTEs, and self-joins
- Built a **reusable ETL pipeline** with clear separation of concerns (extract → transform → load)
- Transformed **wide-format data into queryable long format** (50K rows → 66K normalized transactions)

**Business Thinking:**
- Translated abstract business questions into structured SQL queries
- Identified **Pareto principle** in action (20% of customers = 51% of revenue)
- Discovered actionable insights (regional gaps, cross-sell opportunities, peak hours)

**Data Engineering:**
- Handled **messy real-world data** (date parsing, nulls, type coercion)
- Indexed strategically for query performance
- Synthesized missing dimensions (regions, customers) to enable richer analytics

**This project mirrors real ZS client engagements:** taking raw pharma data, structuring it for analytics, and surfacing insights that drive business decisions.

---

## 🎓 About Me

**Praveen Sharma** | B.Tech IT (AI & ML) | Building production-ready data & AI systems

**Recent Work:**
- **AI Research Intern** at IIT Mandi (IKSMHA Centre) — Built production-ready bilingual Text-to-Speech system
- **ML Engineer Apprentice** at Skill India Digital Hub — Explored classical ML across domains
- **Software Engineering Intern** at Bluestock — Developed IPO Web Application + REST API

**Skills:** Python • SQL • Machine Learning • Data Engineering • End-to-End Pipelines

📫 **Connect:** [LinkedIn](https://www.linkedin.com/in/praveensharma08) | [GitHub](https://github.com/praveensharma0809)

---

## 📝 License

This project is open-source for educational and portfolio purposes.

**Dataset:** [Pharmaceutical Sales Data (Kaggle)](https://www.kaggle.com/datasets/milanzdravkovic/pharma-sales-data)

---

<p align="center">Built with Python, SQL, and analytical rigor | May 2026</p>