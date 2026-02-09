import pandas as pd

# Load the dataset
df = pd.read_csv('data/final_dataset.csv')

print("=== Dataset Overview ===")
print(f"Total rows: {len(df)}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nFirst few rows:")
print(df.head(10))

print("\n=== Checking for Duplicates ===")

# Check for completely duplicate rows
complete_duplicates = df.duplicated()
print(f"\n1. Complete duplicate rows: {complete_duplicates.sum()}")
if complete_duplicates.sum() > 0:
    print("Duplicate rows:")
    print(df[complete_duplicates])

# Check for duplicate dates
date_duplicates = df.duplicated(subset=['price_date'])
print(f"\n2. Duplicate dates: {date_duplicates.sum()}")
if date_duplicates.sum() > 0:
    print("\nRows with duplicate dates:")
    duplicate_dates = df[df.duplicated(subset=['price_date'], keep=False)].sort_values('price_date')
    print(duplicate_dates.head(20))

# Check for rows with same values across multiple columns
print(f"\n3. Checking for rows with identical price_value_price and price_value_yield:")
value_pattern_check = df.groupby(['price_value_price', 'price_value_yield']).size()
print(f"   Number of unique price/yield combinations: {len(value_pattern_check)}")
print(f"   Most common combinations:")
print(value_pattern_check.sort_values(ascending=False).head(10))

print("\n=== Removal Methods ===")
print("\nMethod 1: Remove complete duplicate rows")
df_no_complete_dups = df.drop_duplicates()
print(f"   Rows after removal: {len(df_no_complete_dups)} (removed {len(df) - len(df_no_complete_dups)})")

print("\nMethod 2: Remove duplicate dates (keep first)")
df_no_date_dups = df.drop_duplicates(subset=['price_date'], keep='first')
print(f"   Rows after removal: {len(df_no_date_dups)} (removed {len(df) - len(df_no_date_dups)})")

print("\nMethod 3: Remove duplicate dates (keep last)")
df_no_date_dups_last = df.drop_duplicates(subset=['price_date'], keep='last')
print(f"   Rows after removal: {len(df_no_date_dups_last)} (removed {len(df) - len(df_no_date_dups_last)})")

print("\n=== Save Cleaned Data? ===")
print("To save the cleaned data, uncomment one of these lines:")
print("# df_no_complete_dups.to_csv('data/final_dataset_cleaned.csv', index=False)")
print("# df_no_date_dups.to_csv('data/final_dataset_cleaned.csv', index=False)")
