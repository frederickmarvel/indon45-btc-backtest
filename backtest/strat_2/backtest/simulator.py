import pandas as pd
import numpy as np
import os

# --- 1. SET YOUR FILE PATHS HERE ---
MARKET_DATA_PATH = "/Users/frederickmarvel/GodlHodl/backtest/strat_2/trend_indicator/merged_trend_macro_dataset.csv"
COUPON_DATA_PATH = "/Users/frederickmarvel/GodlHodl/backtest/strat_2/backtest/coupon_data.csv" # Update if this is different
OUTPUT_PATH = "/Users/frederickmarvel/GodlHodl/backtest/strat_2/backtest/portfolio_results.csv"

def run_simulation():
    # Load Market Data
    if not os.path.exists(MARKET_DATA_PATH):
        print(f"Error: Market file not found at {MARKET_DATA_PATH}")
        return
    
    df_market = pd.read_csv(MARKET_DATA_PATH)
    df_market['Tanggal'] = pd.to_datetime(df_market['Tanggal'])
    
    # Forward fill missing macro data (weekends)
    df_market[['price_value_price', 'price_value_yield']] = df_market[['price_value_price', 'price_value_yield']].ffill()
    
    # Load Coupon Data (Create dummy if not exists or load)
    # If you haven't saved your coupon data to a CSV yet, you can define it here:
    coupons = {
        'coupon_date': ['2021-07-15', '2022-01-15', '2022-07-15', '2023-01-15', '2023-07-15', 
                        '2024-01-15', '2024-07-15', '2025-01-15', '2025-07-15', '2026-01-15'],
        'coupon_usd': [1990.29] * 10
    }
    df_coupons = pd.DataFrame(coupons)
    df_coupons['coupon_date'] = pd.to_datetime(df_coupons['coupon_date'])

    # Sort market data chronologically
    df_market = df_market.sort_values('Tanggal').reset_index(drop=True)

    # --- 2. Simulation Setup ---
    INITIAL_CASH = 0  
    cash = INITIAL_CASH
    btc_units = 0
    current_allocation = None # Will be set after first 3-day confirmation
    
    portfolio_history = []

    print(f"Starting simulation with ${INITIAL_CASH}...")

    # --- 3. Simulation Loop ---
    for i in range(len(df_market)):
        row = df_market.iloc[i]
        today = row['Tanggal']
        price = row['Price']
        trend = row['Trend_Indicator']
        
        # A. Inject Coupon Cash
        coupon_amt = df_coupons[df_coupons['coupon_date'] == today]['coupon_usd'].sum()
        if coupon_amt > 0:
            cash += coupon_amt

        # B. 3-Day Rule logic
        target_btc_pct = current_allocation
        if i >= 2:
            last_3_trends = df_market['Trend_Indicator'].iloc[i-2 : i+1].values
            if np.all(last_3_trends == last_3_trends[0]):
                val = last_3_trends[0]
                # Map trend to allocation
                mapping = {1.0: 1.0, 0.5: 0.75, 0.0: 0.5, -0.5: 0.25, -1.0: 0.0}
                target_btc_pct = mapping.get(val, current_allocation)

        # C. Initial Buy (If we haven't started yet)
        if current_allocation is None and target_btc_pct is not None:
            current_allocation = target_btc_pct

        # D. Rebalance (Only if allocation changed)
        total_value = cash + (btc_units * price)
        
        if target_btc_pct is not None and target_btc_pct != current_allocation:
            target_btc_value = total_value * target_btc_pct
            btc_units = target_btc_value / price
            cash = total_value - target_btc_value
            current_allocation = target_btc_pct

        # E. Record Daily Stats
        portfolio_history.append({
            'Tanggal': today,
            'Price': price,
            'Trend': trend,
            'Cash': cash,
            'BTC_Units': btc_units,
            'BTC_Value': btc_units * price,
            'Total_Value': total_value,
            'Allocation': current_allocation,
            'Coupon_Received': coupon_amt
        })

    # Save and Print Summary
    results = pd.DataFrame(portfolio_history)
    results.to_csv(OUTPUT_PATH, index=False)
    
    print("\n--- Backtest Results ---")
    print(f"Final Value: ${results['Total_Value'].iloc[-1]:,.2f}")
    print(f"Output saved to: {OUTPUT_PATH}")
    return results

if __name__ == "__main__":
    run_simulation()