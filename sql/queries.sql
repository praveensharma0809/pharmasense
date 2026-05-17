-- PharmaSense: 15 Business Analytics Queries
-- Each query answers a critical business question using advanced SQL

-- ============================================================
-- TIER 1: FOUNDATIONAL QUERIES (Q1-Q5)
-- ============================================================

-- Q1: Top 10 best-selling products by revenue
-- Business value: Identify which drugs drive the most revenue
SELECT 
    p.product_name,
    p.category,
    SUM(s.revenue) AS total_revenue,
    SUM(s.quantity) AS units_sold,
    ROUND(AVG(s.revenue), 2) AS avg_transaction_value
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 10;

-- Q2: Monthly revenue trend (last 12 months)
-- Business value: Track revenue growth/decline over time
SELECT 
    strftime('%Y-%m', sale_datetime) AS month,
    SUM(revenue) AS monthly_revenue,
    COUNT(DISTINCT sale_id) AS transactions,
    ROUND(AVG(revenue), 2) AS avg_transaction
FROM sales
WHERE sale_datetime >= date('now', '-12 months')
GROUP BY month
ORDER BY month;

-- Q3: Regional revenue contribution
-- Business value: Understand geographic performance distribution
SELECT 
    r.region_name,
    r.zone,
    SUM(s.revenue) AS region_revenue,
    COUNT(DISTINCT s.sale_id) AS transactions,
    ROUND(100.0 * SUM(s.revenue) / (SELECT SUM(revenue) FROM sales), 2) AS pct_of_total
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
JOIN regions r ON c.region_id = r.region_id
GROUP BY r.region_id, r.region_name, r.zone
ORDER BY region_revenue DESC;

-- Q4: Average order value by customer type
-- Business value: Identify which customer segments are most valuable
SELECT 
    c.customer_type,
    COUNT(DISTINCT s.sale_id) AS total_orders,
    ROUND(AVG(s.revenue), 2) AS avg_order_value,
    ROUND(SUM(s.revenue), 2) AS total_revenue,
    ROUND(SUM(s.quantity), 2) AS total_units
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY c.customer_type
ORDER BY avg_order_value DESC;

-- Q5: Unique products sold per quarter
-- Business value: Track product portfolio activity over time
SELECT 
    strftime('%Y', sale_datetime) AS year,
    'Q' || ((CAST(strftime('%m', sale_datetime) AS INTEGER) - 1) / 3 + 1) AS quarter,
    COUNT(DISTINCT product_id) AS unique_products,
    SUM(revenue) AS quarter_revenue
FROM sales
GROUP BY year, quarter
ORDER BY year, quarter;


-- ============================================================
-- TIER 2: INTERMEDIATE QUERIES (Q6-Q10) - Window Functions
-- ============================================================

-- Q6: Month-over-month revenue growth rate
-- Business value: Identify acceleration or deceleration in sales
-- SQL Features: CTE, LAG window function
WITH monthly_revenue AS (
    SELECT 
        strftime('%Y-%m', sale_datetime) AS month,
        SUM(revenue) AS revenue
    FROM sales
    GROUP BY month
)
SELECT 
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS prev_month_revenue,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (ORDER BY month)) 
        / LAG(revenue) OVER (ORDER BY month), 
        2
    ) AS growth_pct
FROM monthly_revenue
ORDER BY month;

-- Q7: Top 3 products per region
-- Business value: Regional product preferences for targeted marketing
-- SQL Features: ROW_NUMBER, PARTITION BY
WITH product_region_sales AS (
    SELECT 
        r.region_name,
        p.product_name,
        SUM(s.revenue) AS revenue,
        ROW_NUMBER() OVER (
            PARTITION BY r.region_name 
            ORDER BY SUM(s.revenue) DESC
        ) AS rank
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    JOIN customers c ON s.customer_id = c.customer_id
    JOIN regions r ON c.region_id = r.region_id
    GROUP BY r.region_name, p.product_id, p.product_name
)
SELECT region_name, product_name, revenue, rank
FROM product_region_sales
WHERE rank <= 3
ORDER BY region_name, rank;

-- Q8: Customer segmentation by purchase volume
-- Business value: Identify VIP vs low-value customers for tiered service
SELECT 
    c.customer_name,
    c.customer_type,
    COUNT(DISTINCT s.sale_id) AS frequency,
    ROUND(SUM(s.revenue), 2) AS monetary,
    CASE 
        WHEN SUM(s.revenue) > 50000 AND COUNT(DISTINCT s.sale_id) > 1000 THEN 'VIP'
        WHEN SUM(s.revenue) > 20000 THEN 'High Value'
        WHEN SUM(s.revenue) > 5000 THEN 'Mid Value'
        ELSE 'Low Value'
    END AS segment
FROM customers c
JOIN sales s ON c.customer_id = s.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_type
ORDER BY monetary DESC;

-- Q9: Products with declining sales (last 3 months vs prior 3 months)
-- Business value: Early warning system for inventory or marketing issues
-- SQL Features: CTEs, multiple aggregations
WITH recent AS (
    SELECT product_id, SUM(revenue) AS recent_revenue
    FROM sales
    WHERE sale_datetime >= date('2014-10-01')  -- Using actual data range
    GROUP BY product_id
),
prior AS (
    SELECT product_id, SUM(revenue) AS prior_revenue
    FROM sales
    WHERE sale_datetime >= date('2014-07-01') 
      AND sale_datetime < date('2014-10-01')
    GROUP BY product_id
)
SELECT 
    p.product_name,
    p.category,
    ROUND(prior.prior_revenue, 2) AS prior_period,
    ROUND(recent.recent_revenue, 2) AS recent_period,
    ROUND(
        100.0 * (recent.recent_revenue - prior.prior_revenue) / prior.prior_revenue,
        2
    ) AS change_pct
FROM products p
JOIN prior ON p.product_id = prior.product_id
JOIN recent ON p.product_id = recent.product_id
WHERE recent.recent_revenue < prior.prior_revenue
ORDER BY change_pct ASC;

-- Q10: Day-of-week sales pattern
-- Business value: Optimize staffing and inventory based on weekly cycles
SELECT 
    weekday,
    COUNT(*) AS total_sales,
    ROUND(AVG(revenue), 2) AS avg_revenue,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY weekday
ORDER BY 
    CASE weekday
        WHEN 'Monday' THEN 1
        WHEN 'Tuesday' THEN 2
        WHEN 'Wednesday' THEN 3
        WHEN 'Thursday' THEN 4
        WHEN 'Friday' THEN 5
        WHEN 'Saturday' THEN 6
        WHEN 'Sunday' THEN 7
    END;


-- ============================================================
-- TIER 3: ADVANCED QUERIES (Q11-Q15) - Analytical Depth
-- ============================================================

-- Q11: Running cumulative revenue
-- Business value: Track progress toward annual revenue targets
-- SQL Features: Window function without PARTITION
WITH daily_revenue AS (
    SELECT 
        DATE(sale_datetime) AS sale_date,
        SUM(revenue) AS daily_total
    FROM sales
    GROUP BY sale_date
)
SELECT 
    sale_date,
    daily_total,
    SUM(daily_total) OVER (ORDER BY sale_date) AS cumulative_revenue
FROM daily_revenue
ORDER BY sale_date
LIMIT 100;  -- Showing first 100 days

-- Q12: Cross-sell opportunities (products often bought together)
-- Business value: Bundle recommendations for marketing campaigns
-- SQL Features: Self-join
SELECT 
    p1.product_name AS product_a,
    p2.product_name AS product_b,
    COUNT(*) AS co_occurrence
FROM sales s1
JOIN sales s2 
    ON s1.customer_id = s2.customer_id 
    AND DATE(s1.sale_datetime) = DATE(s2.sale_datetime)
    AND s1.product_id < s2.product_id
JOIN products p1 ON s1.product_id = p1.product_id
JOIN products p2 ON s2.product_id = p2.product_id
GROUP BY p1.product_name, p2.product_name
HAVING co_occurrence > 50
ORDER BY co_occurrence DESC
LIMIT 10;

-- Q13: Category-level year-over-year growth
-- Business value: Strategic planning for product categories
-- SQL Features: LAG with PARTITION BY
WITH yearly_category AS (
    SELECT 
        p.category,
        strftime('%Y', s.sale_datetime) AS year,
        SUM(s.revenue) AS revenue
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.category, year
)
SELECT 
    category,
    year,
    ROUND(revenue, 2) AS revenue,
    ROUND(LAG(revenue) OVER (PARTITION BY category ORDER BY year), 2) AS prev_year_revenue,
    ROUND(
        100.0 * (revenue - LAG(revenue) OVER (PARTITION BY category ORDER BY year)) 
        / LAG(revenue) OVER (PARTITION BY category ORDER BY year),
        2
    ) AS yoy_growth_pct
FROM yearly_category
ORDER BY category, year;

-- Q14: Top customers contributing 80% of revenue (Pareto analysis)
-- Business value: Focus retention efforts on high-impact accounts
-- SQL Features: Multiple window functions, cumulative calculation
WITH customer_revenue AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        SUM(s.revenue) AS total_revenue
    FROM customers c
    JOIN sales s ON c.customer_id = s.customer_id
    GROUP BY c.customer_id, c.customer_name
),
ranked AS (
    SELECT 
        customer_name,
        total_revenue,
        SUM(total_revenue) OVER (ORDER BY total_revenue DESC) AS cumulative,
        SUM(total_revenue) OVER () AS grand_total
    FROM customer_revenue
)
SELECT 
    customer_name,
    ROUND(total_revenue, 2) AS revenue,
    ROUND(100.0 * cumulative / grand_total, 2) AS cumulative_pct
FROM ranked
WHERE cumulative <= grand_total * 0.8
ORDER BY total_revenue DESC;

-- Q15: Hourly sales pattern (peak hours identification)
-- Business value: Optimize delivery schedules and staffing
SELECT 
    hour,
    COUNT(*) AS total_sales,
    ROUND(AVG(revenue), 2) AS avg_revenue,
    ROUND(SUM(revenue), 2) AS total_revenue
FROM sales
GROUP BY hour
ORDER BY hour;