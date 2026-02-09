"""
INDON45 Bond + BTC Coupon Reinvestment Strategy - Complete Analysis
====================================================================
This script simulates buying INDON45 bonds and converting all coupons to BTC
Tracks daily P&L for both bond position and BTC portfolio
"""

import pandas as pd
import numpy as np
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================
INITIAL_INVESTMENT_USD = 100000
COUPON_RATE_ANNUAL = 0.05125  # 5.125% for INDON45
COUPON_SEMIANNUAL = COUPON_RATE_ANNUAL / 2

# ============================================================================
# STEP 1: Load your data
# ============================================================================
# Load daily price data (REPLACE WITH YOUR ACTUAL FILE)
daily_df = pd.read_csv('final_dataset_cleaned.csv')
daily_df['price_date'] = pd.to_datetime(daily_df['price_date'])
daily_df = daily_df.sort_values('price_date').reset_index(drop=True)

# Load coupon payment data (REPLACE WITH YOUR ACTUAL FILE)
coupons_df = pd.read_csv('indon45_btc_simulation.csv')
coupons_df['coupon_date'] = pd.to_datetime(coupons_df['coupon_date'])

print("="*80)
print("DATA LOADED")
print("="*80)
print(f"Daily data: {len(daily_df)} rows from {daily_df['price_date'].min().date()} to {daily_df['price_date'].max().date()}")
print(f"Coupon payments: {len(coupons_df)} payments")
print(f"Total coupons received: ${coupons_df['coupon_usd'].sum():,.2f}")

# ============================================================================
# STEP 2: Calculate bond position
# ============================================================================
PURCHASE_DATE = daily_df['price_date'].min()
PURCHASE_PRICE = daily_df.loc[daily_df['price_date'] == PURCHASE_DATE, 'price_value_price'].values[0]
NOMINAL_OWNED = INITIAL_INVESTMENT_USD / (PURCHASE_PRICE / 100)

print(f"\nBond purchased on {PURCHASE_DATE.date()} at {PURCHASE_PRICE}% of par")
print(f"Nominal owned: ${NOMINAL_OWNED:,.2f}")

# ============================================================================
# STEP 3: Create daily tracking dataset
# ============================================================================
print(f"\nProcessing {len(daily_df)} days of data...")

daily_tracking = []

for idx, row in daily_df.iterrows():
    current_date = row['price_date']
    current_bond_price = row['price_value_price']
    current_bond_yield = row['price_value_yield']
    current_btc_price = row['btc_close']

    # Find BTC holdings as of this date
    coupons_received_mask = coupons_df['coupon_date'] <= current_date
    btc_holdings = coupons_df.loc[coupons_received_mask, 'btc_cumulative'].max() if coupons_received_mask.any() else 0

    # Calculate total USD coupons received
    total_coupons_usd = coupons_df.loc[coupons_received_mask, 'coupon_usd'].sum() if coupons_received_mask.any() else 0
    num_coupons = coupons_received_mask.sum()

    # Bond calculations
    bond_market_value = NOMINAL_OWNED * (current_bond_price / 100)
    bond_pnl_usd = bond_market_value - INITIAL_INVESTMENT_USD
    bond_pnl_pct = (bond_pnl_usd / INITIAL_INVESTMENT_USD) * 100

    # BTC calculations
    btc_portfolio_value = btc_holdings * current_btc_price
    btc_pnl_usd = btc_portfolio_value - total_coupons_usd
    btc_pnl_pct = (btc_pnl_usd / total_coupons_usd * 100) if total_coupons_usd > 0 else 0

    # Total portfolio
    total_portfolio_value = bond_market_value + btc_portfolio_value
    total_pnl_usd = bond_pnl_usd + btc_pnl_usd
    total_pnl_pct = (total_pnl_usd / INITIAL_INVESTMENT_USD) * 100

    daily_tracking.append({
        'date': current_date,
        'bond_price': current_bond_price,
        'bond_yield': current_bond_yield,
        'bond_market_value': bond_market_value,
        'bond_pnl_usd': bond_pnl_usd,
        'bond_pnl_pct': bond_pnl_pct,
        'num_coupons_received': num_coupons,
        'coupons_received_usd': total_coupons_usd,
        'btc_price': current_btc_price,
        'btc_holdings': btc_holdings,
        'btc_portfolio_value': btc_portfolio_value,
        'btc_pnl_usd': btc_pnl_usd,
        'btc_pnl_pct': btc_pnl_pct,
        'total_portfolio_value': total_portfolio_value,
        'total_pnl_usd': total_pnl_usd,
        'total_pnl_pct': total_pnl_pct
    })

tracking_df = pd.DataFrame(daily_tracking)

# ============================================================================
# STEP 4: Calculate summary statistics
# ============================================================================
latest = tracking_df.iloc[-1]
days_held = (tracking_df['date'].iloc[-1] - tracking_df['date'].iloc[0]).days
annualized_return = (latest['total_pnl_pct'] / 100) / (days_held / 365) * 100

best_day = tracking_df.loc[tracking_df['total_pnl_usd'].idxmax()]
worst_day = tracking_df.loc[tracking_df['total_pnl_usd'].idxmin()]

print("\n" + "="*80)
print("COMPREHENSIVE PORTFOLIO SUMMARY")
print("="*80)

print("\n📊 BOND POSITION (INDON45)")
print("-" * 80)
print(f"Initial Investment:        ${INITIAL_INVESTMENT_USD:>15,.2f}")
print(f"Purchase Price:            {PURCHASE_PRICE:>15.2f}% of par")
print(f"Nominal Owned:             ${NOMINAL_OWNED:>15,.2f}")
print(f"Current Bond Price:        {latest['bond_price']:>15.2f}% of par")
print(f"Current Market Value:      ${latest['bond_market_value']:>15,.2f}")
print(f"Bond P&L:                  ${latest['bond_pnl_usd']:>15,.2f} ({latest['bond_pnl_pct']:>6.2f}%)")

print("\n💰 COUPON INCOME")
print("-" * 80)
print(f"Total Coupons Received:    ${latest['coupons_received_usd']:>15,.2f}")
print(f"Number of Payments:        {int(latest['num_coupons_received']):>15}")
print(f"Average per Payment:       ${latest['coupons_received_usd'] / max(latest['num_coupons_received'], 1):>15,.2f}")

print("\n₿ BITCOIN PORTFOLIO")
print("-" * 80)
print(f"Total BTC Accumulated:     {latest['btc_holdings']:>15.8f} BTC")
if latest['btc_holdings'] > 0:
    print(f"Average Buy Price:         ${latest['coupons_received_usd'] / latest['btc_holdings']:>15,.2f}")
print(f"Current BTC Price:         ${latest['btc_price']:>15,.2f}")
print(f"BTC Portfolio Value:       ${latest['btc_portfolio_value']:>15,.2f}")
print(f"BTC P&L:                   ${latest['btc_pnl_usd']:>15,.2f} ({latest['btc_pnl_pct']:>6.2f}%)")

print("\n🎯 TOTAL PORTFOLIO")
print("-" * 80)
print(f"Bond Market Value:         ${latest['bond_market_value']:>15,.2f}")
print(f"BTC Portfolio Value:       ${latest['btc_portfolio_value']:>15,.2f}")
print(f"Total Portfolio Value:     ${latest['total_portfolio_value']:>15,.2f}")
print(f"Total P&L:                 ${latest['total_pnl_usd']:>15,.2f} ({latest['total_pnl_pct']:>6.2f}%)")

print("\n📈 PERFORMANCE METRICS")
print("-" * 80)
print(f"Days Held:                 {days_held:>15}")
print(f"Annualized Return:         {annualized_return:>15.2f}%")
print(f"Best Day P&L:              ${best_day['total_pnl_usd']:>15,.2f} on {best_day['date'].date()}")
print(f"Worst Day P&L:             ${worst_day['total_pnl_usd']:>15,.2f} on {worst_day['date'].date()}")

# ============================================================================
# STEP 5: Save all outputs
# ============================================================================
print("\n" + "="*80)
print("SAVING FILES...")
print("="*80)

# Daily tracking
tracking_df.to_csv('portfolio_daily_tracking.csv', index=False)
print("✓ Saved: portfolio_daily_tracking.csv")

# Summary report
summary_data = {
    'Metric': [
        'Initial Investment',
        'Purchase Price (% of par)',
        'Nominal Owned',
        'Current Bond Price (% of par)',
        'Current Bond Market Value',
        'Bond P&L (USD)',
        'Bond P&L (%)',
        '',
        'Total Coupons Received (USD)',
        'Number of Coupon Payments',
        'Average Coupon per Payment',
        '',
        'Total BTC Accumulated',
        'Average BTC Buy Price',
        'Current BTC Price',
        'BTC Portfolio Value',
        'BTC P&L (USD)',
        'BTC P&L (%)',
        '',
        'Total Portfolio Value',
        'Total P&L (USD)',
        'Total P&L (%)',
        'Days Held',
        'Annualized Return (%)'
    ],
    'Value': [
        f"${INITIAL_INVESTMENT_USD:,.2f}",
        f"{PURCHASE_PRICE:.2f}%",
        f"${NOMINAL_OWNED:,.2f}",
        f"{latest['bond_price']:.2f}%",
        f"${latest['bond_market_value']:,.2f}",
        f"${latest['bond_pnl_usd']:,.2f}",
        f"{latest['bond_pnl_pct']:.2f}%",
        '',
        f"${latest['coupons_received_usd']:,.2f}",
        f"{int(latest['num_coupons_received'])}",
        f"${latest['coupons_received_usd'] / max(latest['num_coupons_received'], 1):,.2f}",
        '',
        f"{latest['btc_holdings']:.8f} BTC",
        f"${latest['coupons_received_usd'] / latest['btc_holdings']:,.2f}" if latest['btc_holdings'] > 0 else "N/A",
        f"${latest['btc_price']:,.2f}",
        f"${latest['btc_portfolio_value']:,.2f}",
        f"${latest['btc_pnl_usd']:,.2f}",
        f"{latest['btc_pnl_pct']:.2f}%",
        '',
        f"${latest['total_portfolio_value']:,.2f}",
        f"${latest['total_pnl_usd']:,.2f}",
        f"{latest['total_pnl_pct']:.2f}%",
        f"{days_held}",
        f"{annualized_return:.2f}%"
    ]
}

summary_df = pd.DataFrame(summary_data)
summary_df.to_csv('portfolio_summary.csv', index=False)
print("✓ Saved: portfolio_summary.csv")

# Coupon log
coupons_df.to_csv('coupon_log.csv', index=False)
print("✓ Saved: coupon_log.csv")

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print("\nFiles created:")
print("1. portfolio_daily_tracking.csv  - Daily P&L tracking")
print("2. portfolio_summary.csv         - Summary statistics")
print("3. coupon_log.csv               - Coupon payment history")