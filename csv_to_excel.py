import pandas as pd

# Convert a single CSV file to Excel
def csv_to_excel(csv_file, excel_file):
    df = pd.read_csv(csv_file)
    df.to_excel(excel_file, index=False, engine='openpyxl')
    print(f"Converted: {csv_file} -> {excel_file}")

# Example usage - uncomment the file you want to convert:

# Convert final_dataset
csv_to_excel('/Users/frederickmarvel/GodlHodl/backtest/strat_1/testing/portfolio_daily_tracking.csv', 'data/final_result_port.xlsx')

# Convert portfolio_summary
# csv_to_excel('backtest/strat_1/testing/portfolio_summary.csv', 'backtest/strat_1/testing/portfolio_summary.xlsx')

# Convert indonprice
# csv_to_excel('indon/indonprice.csv', 'indon/indonprice.xlsx')

# Convert indonyield
# csv_to_excel('indon/indonyield.csv', 'indon/indonyield.xlsx')

print("\nDone!")
