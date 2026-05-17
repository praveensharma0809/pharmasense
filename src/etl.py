import pandas as pd
import numpy as np
from pathlib import Path
from database import get_connection, init_db
from datetime import datetime

# Product mapping (ATC codes to readable names)
PRODUCT_MAP = {
    'M01AB': {'name': 'Anti-inflammatory (Indometacin)', 'category': 'Pain Relief', 'class': 'NSAIDs', 'price': 12.50},
    'M01AE': {'name': 'Anti-inflammatory (COX-2)', 'category': 'Pain Relief', 'class': 'NSAIDs', 'price': 15.75},
    'N02BA': {'name': 'Salicylic Acid (Aspirin)', 'category': 'Pain Relief', 'class': 'Analgesics', 'price': 8.20},
    'N02BE': {'name': 'Paracetamol', 'category': 'Pain Relief', 'class': 'Analgesics', 'price': 6.50},
    'N05B': {'name': 'Anxiolytics', 'category': 'Mental Health', 'class': 'Psychiatric', 'price': 22.00},
    'N05C': {'name': 'Sedatives/Hypnotics', 'category': 'Mental Health', 'class': 'Psychiatric', 'price': 18.50},
    'R03': {'name': 'Respiratory Drugs', 'category': 'Respiratory', 'class': 'Inhalers', 'price': 28.00},
    'R06': {'name': 'Antihistamines', 'category': 'Allergy', 'class': 'Antiallergics', 'price': 10.25},
}

REGIONS = [
    {'name': 'North Serbia', 'zone': 'Urban'},
    {'name': 'South Serbia', 'zone': 'Rural'},
    {'name': 'East Serbia', 'zone': 'Mixed'},
    {'name': 'West Serbia', 'zone': 'Urban'},
    {'name': 'Central Serbia', 'zone': 'Urban'},
]

CUSTOMER_TYPES = ['Hospital', 'Retail Pharmacy', 'Online Pharmacy']

def extract(file_path: str) -> pd.DataFrame:
    """Read raw Excel file."""
    print("⏳ Extracting data...")
    df = pd.read_csv(file_path)
    print(f"✓ Extracted {len(df):,} rows, {len(df.columns)} columns")
    return df

def transform(df: pd.DataFrame) -> dict:
    """Clean data and create normalized tables."""
    print("⏳ Transforming data...")
    
    # 1. Create products dimension
    products = []
    for code, info in PRODUCT_MAP.items():
        products.append({
            'product_code': code,
            'product_name': info['name'],
            'category': info['category'],
            'therapeutic_class': info['class'],
            'unit_price': info['price']
        })
    products_df = pd.DataFrame(products)
    
    # 2. Create regions dimension
    regions_df = pd.DataFrame(REGIONS)
    regions_df.columns = ['region_name', 'zone']
    regions_df['country'] = 'Serbia'
    
    # 3. Create customers dimension (synthesized)
    np.random.seed(42)  # Reproducible
    customers = []
    for i in range(1, 21):  # 20 customers
        customers.append({
            'customer_name': f'{"Hospital" if i <= 8 else "Pharmacy"} {chr(64+i)}',
            'customer_type': np.random.choice(CUSTOMER_TYPES),
            'region_id': np.random.randint(1, 6)  # Will map to regions 1-5
        })
    customers_df = pd.DataFrame(customers)
    
    # 4. Create sales fact table
    print("⏳ Building fact table (this may take a minute)...")
    
    # Parse datetime
    df['sale_datetime'] = pd.to_datetime(df['datum'], format='mixed', dayfirst=True)
    
    # Melt from wide to long format (each drug becomes a separate row)
    drug_cols = ['M01AB', 'M01AE', 'N02BA', 'N02BE', 'N05B', 'N05C', 'R03', 'R06']
    
    sales_records = []
    for idx, row in df.iterrows():
        if idx % 10000 == 0:
            print(f"  Processing row {idx:,}/{len(df):,}...")
        
        for drug_code in drug_cols:
            quantity = row[drug_code]
            if quantity > 0:  # Only create sales records where quantity > 0
                # Assign random customer
                customer_id = np.random.randint(1, 21)
                
                # Get product_id (will be 1-8 based on insertion order)
                product_id = drug_cols.index(drug_code) + 1
                
                # Calculate revenue
                revenue = quantity * PRODUCT_MAP[drug_code]['price']
                
                sales_records.append({
                    'sale_datetime': row['sale_datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                    'product_id': product_id,
                    'customer_id': customer_id,
                    'quantity': quantity,
                    'revenue': round(revenue, 2),
                    'year': row['Year'],
                    'month': row['Month'],
                    'hour': row['Hour'],
                    'weekday': row['Weekday Name']
                })
    
    sales_df = pd.DataFrame(sales_records)
    
    print(f"✓ Transformed into {len(sales_df):,} sales transactions")
    
    return {
        'products': products_df,
        'regions': regions_df,
        'customers': customers_df,
        'sales': sales_df
    }

def load(tables: dict):
    """Load transformed data into SQLite."""
    print("⏳ Loading data into database...")
    conn = get_connection()
    
    # Load in order (dimensions first, then facts)
    for name in ['products', 'regions', 'customers', 'sales']:
        df = tables[name]
        df.to_sql(name, conn, if_exists='append', index=False)
        print(f"✓ Loaded {len(df):,} rows into {name}")
    
    conn.close()
    print("✓ ETL pipeline complete!")

def run_pipeline():
    """Execute full ETL pipeline."""
    print("\n" + "="*60)
    print("PharmaSense ETL Pipeline")
    print("="*60 + "\n")
    
    # Initialize database
    init_db()
    
    # ETL
    df = extract("data/raw/saleshourly.csv")
    tables = transform(df)
    load(tables)
    
    print("\n" + "="*60)
    print("✓ SUCCESS: Database ready for analytics!")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_pipeline()