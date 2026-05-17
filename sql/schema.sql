-- PharmaSense Database Schema
-- Normalized 3NF design for pharma sales analytics

PRAGMA foreign_keys = ON;

-- Dimension Table: Products (Drug Categories)
CREATE TABLE IF NOT EXISTS products (
    product_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    product_code    TEXT UNIQUE NOT NULL,  -- ATC code: M01AB, N02BA, etc.
    product_name    TEXT NOT NULL,
    category        TEXT NOT NULL,
    therapeutic_class TEXT NOT NULL,
    unit_price      REAL NOT NULL
);

-- Dimension Table: Regions
CREATE TABLE IF NOT EXISTS regions (
    region_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name     TEXT UNIQUE NOT NULL,
    country         TEXT DEFAULT 'Serbia',
    zone            TEXT
);

-- Dimension Table: Customers (Pharmacies/Hospitals)
CREATE TABLE IF NOT EXISTS customers (
    customer_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name   TEXT NOT NULL,
    customer_type   TEXT NOT NULL,  -- 'Hospital', 'Retail Pharmacy', 'Online'
    region_id       INTEGER NOT NULL,
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
);

-- Fact Table: Sales Transactions
CREATE TABLE IF NOT EXISTS sales (
    sale_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_datetime   TEXT NOT NULL,  -- ISO format: YYYY-MM-DD HH:00:00
    product_id      INTEGER NOT NULL,
    customer_id     INTEGER NOT NULL,
    quantity        REAL NOT NULL,
    revenue         REAL NOT NULL,
    year            INTEGER NOT NULL,
    month           INTEGER NOT NULL,
    hour            INTEGER NOT NULL,
    weekday         TEXT NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_sales_datetime ON sales(sale_datetime);
CREATE INDEX IF NOT EXISTS idx_sales_product ON sales(product_id);
CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id);
CREATE INDEX IF NOT EXISTS idx_sales_year_month ON sales(year, month);