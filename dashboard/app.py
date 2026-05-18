import streamlit as st
import pandas as pd
import sqlite3
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

DB_PATH = "data/processed/pharmasense.db"

def run_query(query: str) -> pd.DataFrame:
    """Execute SQL and return DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Page config
st.set_page_config(
    page_title="PharmaSense | Pharma Intelligence",
    page_icon="💊",
    layout="wide"
)

st.title("💊 PharmaSense")
st.caption("Pharmaceutical Sales Intelligence Platform")

# KPI Row
col1, col2, col3, col4 = st.columns(4)

total_revenue = run_query("SELECT SUM(revenue) AS r FROM sales").iloc[0]['r']
col1.metric("Total Revenue", f"${total_revenue:,.0f}")

total_orders = run_query("SELECT COUNT(*) AS c FROM sales").iloc[0]['c']
col2.metric("Total Transactions", f"{total_orders:,}")

avg_order = total_revenue / total_orders if total_orders > 0 else 0
col3.metric("Avg Transaction", f"${avg_order:.2f}")

active_products = run_query("SELECT COUNT(DISTINCT product_id) AS p FROM sales").iloc[0]['p']
col4.metric("Active Products", active_products)

st.markdown("---")

# Section 1: Top Products
st.header("📊 Top Performing Products")
top_products = run_query("""
    SELECT p.product_name, SUM(s.revenue) AS revenue
    FROM sales s 
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.product_name
    ORDER BY revenue DESC 
    LIMIT 8
""")
st.bar_chart(top_products.set_index('product_name'))

# Section 2: Regional Performance
col1, col2 = st.columns(2)

with col1:
    st.subheader("Regional Revenue Distribution")
    regional = run_query("""
        SELECT r.region_name, SUM(s.revenue) AS revenue
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
        JOIN regions r ON c.region_id = r.region_id
        GROUP BY r.region_name
        ORDER BY revenue DESC
    """)
    st.dataframe(regional, use_container_width=True)

with col2:
    st.subheader("Customer Type Performance")
    customer_type = run_query("""
        SELECT c.customer_type, 
               COUNT(DISTINCT s.sale_id) AS transactions,
               ROUND(SUM(s.revenue), 2) AS revenue
        FROM sales s
        JOIN customers c ON s.customer_id = c.customer_id
        GROUP BY c.customer_type
        ORDER BY revenue DESC
    """)
    st.dataframe(customer_type, use_container_width=True)

st.markdown("---")

# Section 3: Time Analysis
st.header("📈 Temporal Trends")

tab1, tab2 = st.tabs(["Monthly Trend", "Hourly Pattern"])

with tab1:
    monthly = run_query("""
        SELECT strftime('%Y-%m', sale_datetime) AS month, 
               SUM(revenue) AS revenue
        FROM sales 
        GROUP BY month 
        ORDER BY month
    """)
    st.line_chart(monthly.set_index('month'))

with tab2:
    hourly = run_query("""
        SELECT hour, SUM(revenue) AS revenue
        FROM sales
        GROUP BY hour
        ORDER BY hour
    """)
    st.bar_chart(hourly.set_index('hour'))

st.markdown("---")

# Section 4: Advanced Analytics
st.header("🔍 Business Insights")

insight_type = st.selectbox(
    "Select Analysis:",
    [
        "Top Customers (Pareto 80/20)",
        "Customer Segmentation",
        "Product Cross-Sell Opportunities",
        "Month-over-Month Growth"
    ]
)

if insight_type == "Top Customers (Pareto 80/20)":
    query = """
        WITH customer_revenue AS (
            SELECT c.customer_name, SUM(s.revenue) AS total_revenue
            FROM customers c
            JOIN sales s ON c.customer_id = s.customer_id
            GROUP BY c.customer_id, c.customer_name
        ),
        ranked AS (
            SELECT customer_name, total_revenue,
                   SUM(total_revenue) OVER (ORDER BY total_revenue DESC) AS cumulative,
                   SUM(total_revenue) OVER () AS grand_total
            FROM customer_revenue
        )
        SELECT customer_name, 
               ROUND(total_revenue, 2) AS revenue,
               ROUND(100.0 * cumulative / grand_total, 2) AS cumulative_pct
        FROM ranked
        WHERE cumulative <= grand_total * 0.8
        ORDER BY total_revenue DESC
    """
    
elif insight_type == "Customer Segmentation":
    query = """
        SELECT c.customer_name, c.customer_type,
               COUNT(DISTINCT s.sale_id) AS frequency,
               ROUND(SUM(s.revenue), 2) AS monetary,
               CASE 
                   WHEN SUM(s.revenue) > 50000 THEN 'VIP'
                   WHEN SUM(s.revenue) > 20000 THEN 'High Value'
                   WHEN SUM(s.revenue) > 5000 THEN 'Mid Value'
                   ELSE 'Low Value'
               END AS segment
        FROM customers c
        JOIN sales s ON c.customer_id = s.customer_id
        GROUP BY c.customer_id
        ORDER BY monetary DESC
    """
    
elif insight_type == "Product Cross-Sell Opportunities":
    query = """
        SELECT p1.product_name AS product_a,
               p2.product_name AS product_b,
               COUNT(*) AS co_occurrence
        FROM sales s1
        JOIN sales s2 ON s1.customer_id = s2.customer_id 
            AND DATE(s1.sale_datetime) = DATE(s2.sale_datetime)
            AND s1.product_id < s2.product_id
        JOIN products p1 ON s1.product_id = p1.product_id
        JOIN products p2 ON s2.product_id = p2.product_id
        GROUP BY p1.product_name, p2.product_name
        HAVING co_occurrence > 50
        ORDER BY co_occurrence DESC
        LIMIT 10
    """
    
else:  # Month-over-Month Growth
    query = """
        WITH monthly_revenue AS (
            SELECT strftime('%Y-%m', sale_datetime) AS month,
                   SUM(revenue) AS revenue
            FROM sales
            GROUP BY month
        )
        SELECT month, ROUND(revenue, 2) AS revenue,
               ROUND(LAG(revenue) OVER (ORDER BY month), 2) AS prev_month,
               ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month)) 
                     / LAG(revenue) OVER (ORDER BY month), 2) AS growth_pct
        FROM monthly_revenue
        ORDER BY month
    """

result = run_query(query)
st.dataframe(result, use_container_width=True)

st.markdown("---")
st.caption("Built by Praveen Sharma | [GitHub](https://github.com/praveensharma0809/pharmasense) | [LinkedIn](https://www.linkedin.com/in/praveensharma08)")