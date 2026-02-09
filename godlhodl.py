import sqlite3
import pandas as pd
import os

DB_NAME = 'godlhodl.db'

def clean_and_load(conn, file_path, table_name, is_indo=False):
    """One function to handle both BTC and XAU loading using Pandas"""
    if not os.path.exists(file_path):
        print(f"Skipping {file_path}: File not found")
        return

    df = pd.read_csv(file_path)
    
    # Map Indonesian/US column names to standard SQLite columns
    cols = {
        'Tanggal': 'date', 'Date': 'date',
        'Terakhir': 'price', 'Price': 'price',
        'Pembukaan': 'open', 'Open': 'open',
        'Tertinggi': 'high', 'High': 'high',
        'Terendah': 'low', 'Low': 'low',
        'Vol.': 'volume', 'Vol': 'volume',
        'Perubahan%': 'change_pct', 'Change %': 'change_pct'
    }
    df.rename(columns=cols, inplace=True)

    # Fast cleaning: replace commas/dots based on locale
    for col in ['price', 'open', 'high', 'low']:
        if is_indo:
            df[col] = df[col].astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        else:
            df[col] = df[col].astype(str).str.replace(',', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Standardize date format
    df['date'] = pd.to_datetime(df['date'], dayfirst=is_indo).dt.strftime('%Y-%m-%d')

    # Dump to SQL (Pandas handles the 'CREATE TABLE' and 'INSERT' automatically)
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"Loaded {len(df)} records into {table_name}")

def main():
    conn = sqlite3.connect(DB_NAME)

    # 1. Load Data
    clean_and_load(conn, 'data/btcusd_2015_2026.csv', 'btcusd', is_indo=True)
    clean_and_load(conn, 'data/xauusd_2015_2026.csv', 'xauusd', is_indo=False)

    # 2. Calculate XAU/BTC using SQL (much faster than looping in Python)
    conn.execute("DROP TABLE IF EXISTS xaubtc")
    conn.execute('''
        CREATE TABLE xaubtc AS 
        SELECT 
            b.date,
            (x.price / b.price) as price,
            b.price as btc_price,
            x.price as xau_price
        FROM btcusd b
        JOIN xauusd x ON b.date = x.date
        WHERE b.price > 0
    ''')
    
    # 3. Quick check
    sample = pd.read_sql("SELECT * FROM xaubtc ORDER BY date DESC LIMIT 5", conn)
    print("\n--- Recent XAU/BTC Ratios ---")
    print(sample)

    conn.close()
    print("\n✓ Database updated.")

if __name__ == "__main__":
    main()