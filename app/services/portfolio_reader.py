import pandas as pd
from pathlib import Path
from datetime import datetime


def read_portfolio_excel(file_path="Stock.xlsx"):
    """Read Indian stock portfolio from Excel file"""
    try:
        if not Path(file_path).exists():
            print(f"❌ {file_path} not found. Please create it with columns: Company Name, Total Quantity, Avg Trading Price")
            return None

        df = pd.read_excel(file_path)
        required_cols = ['Company Name', 'Total Quantity', 'Avg Trading Price']
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            print(f"❌ Missing columns in Excel: {missing_cols}")
            return None

        df_renamed = df.rename(columns={
            'Company Name': 'Company',
            'Total Quantity': 'Shares',
            'Avg Trading Price': 'Cost_Per_Share',
            'LTP': 'Current_Price'
        })

        df_renamed['Ticker'] = df_renamed['Company'].str.upper().str.replace(' ', '')
        
        if 'Current_Price' not in df_renamed.columns:
            df_renamed['Current_Price'] = df_renamed['Cost_Per_Share']

        if 'Sector' not in df_renamed.columns:
            df_renamed['Sector'] = 'Unknown'

        return df_renamed

    except Exception as e:
        print(f"❌ Error reading Excel file: {e}")
        return None


def format_indian_portfolio_data(df):
    """Format Indian portfolio data for AI analysis"""
    portfolio_summary = []
    total_value = 0
    sector_allocation = {}

    for _, row in df.iterrows():
        shares = row['Shares']
        cost = row['Cost_Per_Share']
        current = row.get('Current_Price', cost)
        sector = row.get('Sector', 'Unknown')

        total_cost = shares * cost
        current_value = shares * current
        gain_loss = current_value - total_cost
        gain_loss_pct = (gain_loss / total_cost) * 100 if total_cost > 0 else 0

        total_value += current_value

        if sector in sector_allocation:
            sector_allocation[sector] += current_value
        else:
            sector_allocation[sector] = current_value

        portfolio_summary.append(
            f"- {row['Ticker']} ({row['Company']}): {shares} shares, "
            f"Cost: ₹{cost:.2f}, Current: ₹{current:.2f}, "
            f"P&L: ₹{gain_loss:.2f} ({gain_loss_pct:.1f}%), Sector: {sector}"
        )

    sector_breakdown = []
    for sector, value in sector_allocation.items():
        percentage = (value / total_value) * 100 if total_value > 0 else 0
        sector_breakdown.append(f"  {sector}: ₹{value:.2f} ({percentage:.1f}%)")

    result = "\n".join(portfolio_summary)
    result += f"\n\nTotal Portfolio Value: ₹{total_value:.2f}"
    result += f"\n\nSector Allocation:\n" + "\n".join(sector_breakdown)

    return result


def get_portfolio_summary(portfolio_df):
    """Get portfolio summary for display"""
    total_value = (portfolio_df['Shares'] * portfolio_df['Current_Price']).sum()
    return f"💰 Current Portfolio Value: ₹{total_value:.2f}"


def validate_portfolio_data(df):
    """Validate portfolio data for completeness"""
    if df is None or df.empty:
        return False, "Portfolio data is empty"
    
    required_cols = ['Company', 'Shares', 'Cost_Per_Share', 'Current_Price']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        return False, f"Missing required columns: {missing_cols}"
    
    # Check for negative values
    if (df['Shares'] <= 0).any():
        return False, "Shares must be positive numbers"
    
    if (df['Cost_Per_Share'] <= 0).any():
        return False, "Cost per share must be positive numbers"
    
    if (df['Current_Price'] <= 0).any():
        return False, "Current price must be positive numbers"
    
    return True, "Portfolio data is valid"


