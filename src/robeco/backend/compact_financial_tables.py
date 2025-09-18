#!/usr/bin/env python3
"""
Compact Financial Tables Generator
Creates modern, compact, and well-designed financial statement tables with comprehensive yfinance metrics
"""

def format_financial_value(value, is_percentage=False):
    """Format financial values for display"""
    if value is None or value == 'N/A':
        return 'N/A'
    
    try:
        if isinstance(value, str):
            if value in ['N/A', '', 'nan', 'NaN']:
                return 'N/A'
            value = float(value.replace(',', '').replace('$', '').replace('%', ''))
        
        if abs(value) >= 1e12:  # Trillions
            return f"${value/1e12:.1f}T"
        elif abs(value) >= 1e9:  # Billions
            return f"${value/1e9:.1f}B"
        elif abs(value) >= 1e6:  # Millions
            return f"${value/1e6:.0f}M"
        elif abs(value) >= 1e3:  # Thousands
            return f"${value/1e3:.0f}K"
        elif is_percentage:
            return f"{value:.1f}%"
        else:
            return f"${value:.0f}"
            
    except (ValueError, TypeError):
        return 'N/A'

def calculate_yoy_change(current, previous):
    """Calculate year-over-year percentage change"""
    try:
        if current is None or previous is None:
            return 'N/A'
        if isinstance(current, str) or isinstance(previous, str):
            return 'N/A'
        if previous == 0:
            return 'N/A'
        
        change = ((current - previous) / abs(previous)) * 100
        if change > 0:
            return f"+{change:.1f}%"
        else:
            return f"{change:.1f}%"
    except:
        return 'N/A'

def generate_compact_income_statement_table(income_data, years):
    """Generate a compact, modern income statement table with comprehensive metrics"""
    
    if not income_data or not years or len(years) < 2:
        return "<p style='color: #666; font-style: italic;'>Income statement data not available</p>"
    
    # Use only 3 most recent years for compactness
    display_years = years[:3] if len(years) >= 3 else years
    
    html = f"""
<div style="margin: 20px 0;">
    <table style="
        width: 100%; 
        border-collapse: collapse; 
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif; 
        font-size: 11px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border-radius: 8px;
        overflow: hidden;
        background: white;
    ">
        <thead>
            <tr style="background: linear-gradient(135deg, #2C5282 0%, #3182CE 100%); color: white; height: 45px;">
                <th style="text-align: left; padding: 12px 16px; font-weight: 600; font-size: 12px; border: none;">
                    INCOME STATEMENT
                </th>"""
    
    # Add year headers with exact dates
    for year in display_years:
        # Show the exact date as provided (2024-09-30)
        year_header = year
        html += f"""
                <th style="text-align: right; padding: 12px 10px; font-weight: 600; font-size: 11px; border: none;">
                    {year_header}
                </th>"""
    
    # Add YoY change header
    html += """
                <th style="text-align: right; padding: 12px 10px; font-weight: 600; font-size: 11px; border: none;">
                    YoY %
                </th>
            </tr>
        </thead>
        <tbody>"""
    
    # Comprehensive financial metrics from yfinance - Professional Investment Banking Standard
    key_metrics = [
        ('Total Revenue', ['Total Revenue', 'Operating Revenue']),
        ('Cost of Revenue', ['Cost Of Revenue', 'Reconciled Cost Of Revenue']),
        ('Gross Profit', ['Gross Profit']),
        ('R&D Expenses', ['Research And Development']),
        ('SG&A Expenses', ['Selling General And Administration']),
        ('Total OpEx', ['Operating Expense', 'Total Expenses']),
        ('Operating Income', ['Operating Income', 'Total Operating Income As Reported']),
        ('Depreciation', ['Depreciation', 'Reconciled Depreciation']),
        ('EBITDA', ['EBITDA', 'Normalized EBITDA']),
        ('EBIT', ['EBIT']),
        ('Interest Expense', ['Interest Expense Non Operating', 'Interest Expense']),
        ('Interest Income', ['Interest Income Non Operating', 'Interest Income']),
        ('Other Income', ['Other Income Expense', 'Other Non Operating Income Expenses']),
        ('Pretax Income', ['Pretax Income']),
        ('Tax Provision', ['Tax Provision']),
        ('Tax Rate %', ['Tax Rate For Calcs']),
        ('Net Income', ['Net Income', 'Net Income Common Stockholders']),
        ('Basic EPS', ['Basic EPS']),
        ('Diluted EPS', ['Diluted EPS']),
        ('Basic Shares Outstanding', ['Basic Average Shares']),
        ('Diluted Shares Outstanding', ['Diluted Average Shares']),
        ('Weighted Avg Shares', ['Weighted Average Shares', 'Weighted Average Shares Diluted'])
    ]
    
    row_count = 0
    for metric_name, possible_keys in key_metrics:
        # Find the metric in the data
        metric_value = None
        for key in possible_keys:
            for year in display_years:
                if year in income_data and key in income_data[year]:
                    metric_value = key
                    break
            if metric_value:
                break
        
        if not metric_value:
            continue
            
        # Alternate row colors
        row_bg = "#F8FAFC" if row_count % 2 == 0 else "#FFFFFF"
        row_count += 1
        
        html += f"""
            <tr style="background: {row_bg}; height: 35px; border-bottom: 1px solid #E2E8F0;">
                <td style="padding: 8px 16px; font-weight: 500; color: #2D3748; border: none; font-size: 11px;">
                    {metric_name}
                </td>"""
        
        # Add values for each year
        values = []
        for year in display_years:
            if year in income_data and metric_value in income_data[year]:
                value = income_data[year][metric_value]
                formatted_value = format_financial_value(value, is_percentage=(metric_name.endswith('%')))
                values.append(value)
            else:
                formatted_value = 'N/A'
                values.append(None)
                
            # Color coding for positive/negative values
            color = "#059669" if formatted_value.startswith('+') or (formatted_value.startswith('$') and not formatted_value.startswith('$-')) else "#DC2626" if formatted_value.startswith('$-') else "#374151"
            
            html += f"""
                <td style="text-align: right; padding: 8px 10px; color: {color}; font-weight: 500; border: none; font-size: 11px;">
                    {formatted_value}
                </td>"""
        
        # Calculate and add YoY change
        if len(values) >= 2 and values[0] is not None and values[1] is not None:
            yoy_change = calculate_yoy_change(values[0], values[1])
            yoy_color = "#059669" if yoy_change.startswith('+') else "#DC2626" if yoy_change.startswith('-') else "#6B7280"
        else:
            yoy_change = 'N/A'
            yoy_color = "#6B7280"
            
        html += f"""
                <td style="text-align: right; padding: 8px 10px; color: {yoy_color}; font-weight: 600; font-size: 10px; border: none;">
                    {yoy_change}
                </td>
            </tr>"""
    
    html += """
        </tbody>
    </table>
</div>"""
    
    return html

def generate_compact_balance_sheet_table(balance_data, years):
    """Generate a compact, modern balance sheet table with comprehensive metrics"""
    
    if not balance_data or not years or len(years) < 2:
        return "<p style='color: #666; font-style: italic;'>Balance sheet data not available</p>"
    
    display_years = years[:3] if len(years) >= 3 else years
    
    html = f"""
<div style="margin: 20px 0;">
    <table style="
        width: 100%; 
        border-collapse: collapse; 
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif; 
        font-size: 11px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border-radius: 8px;
        overflow: hidden;
        background: white;
    ">
        <thead>
            <tr style="background: linear-gradient(135deg, #5B21B6 0%, #7C3AED 100%); color: white; height: 45px;">
                <th style="text-align: left; padding: 12px 16px; font-weight: 600; font-size: 12px; border: none;">
                    BALANCE SHEET
                </th>"""
    
    # Add year headers with exact dates
    for year in display_years:
        # Show the exact date as provided (2024-09-30)
        year_header = year
        html += f"""
                <th style="text-align: right; padding: 12px 10px; font-weight: 600; font-size: 11px; border: none;">
                    {year_header}
                </th>"""
    
    html += """
                <th style="text-align: right; padding: 12px 10px; font-weight: 600; font-size: 11px; border: none;">
                    YoY %
                </th>
            </tr>
        </thead>
        <tbody>"""
    
    # Comprehensive balance sheet metrics - Investment Banking Standard
    key_metrics = [
        ('Total Assets', ['Total Assets']),
        ('Current Assets', ['Current Assets']),
        ('Cash & Cash Equivalents', ['Cash And Cash Equivalents', 'Cash']),
        ('Short Term Investments', ['Other Short Term Investments']),
        ('Accounts Receivable', ['Accounts Receivable']),
        ('Inventory', ['Inventory']),
        ('PPE (Net)', ['Net PPE', 'Properties']),
        ('Goodwill', ['Goodwill']),
        ('Intangible Assets', ['Other Intangible Assets']),
        ('Current Liabilities', ['Current Liabilities']),
        ('Accounts Payable', ['Accounts Payable']),
        ('Current Debt', ['Current Debt']),
        ('Long-term Debt', ['Long Term Debt']),
        ('Total Debt', ['Total Debt']),
        ('Total Liabilities', ['Total Liabilities Net Minority Interest']),
        ('Shareholders Equity', ['Total Equity Gross Minority Interest', 'Stockholders Equity', 'Total Equity']),
        ('Retained Earnings', ['Retained Earnings']),
        ('Working Capital', ['Working Capital']),
        ('Tangible Book Value', ['Tangible Book Value']),
        ('Book Value Per Share', ['Book Value Per Share'])
    ]
    
    row_count = 0
    for metric_name, possible_keys in key_metrics:
        # Find the metric in the data
        metric_value = None
        for key in possible_keys:
            for year in display_years:
                if year in balance_data and key in balance_data[year]:
                    metric_value = key
                    break
            if metric_value:
                break
        
        if not metric_value:
            continue
            
        # Alternate row colors
        row_bg = "#F8FAFC" if row_count % 2 == 0 else "#FFFFFF"
        row_count += 1
        
        html += f"""
            <tr style="background: {row_bg}; height: 35px; border-bottom: 1px solid #E2E8F0;">
                <td style="padding: 8px 16px; font-weight: 500; color: #2D3748; border: none; font-size: 11px;">
                    {metric_name}
                </td>"""
        
        # Add values for each year
        values = []
        for year in display_years:
            if year in balance_data and metric_value in balance_data[year]:
                value = balance_data[year][metric_value]
                formatted_value = format_financial_value(value)
                values.append(value)
            else:
                formatted_value = 'N/A'
                values.append(None)
                
            # Color coding for positive/negative values
            color = "#059669" if formatted_value.startswith('$') and not formatted_value.startswith('$-') else "#DC2626" if formatted_value.startswith('$-') else "#374151"
            
            html += f"""
                <td style="text-align: right; padding: 8px 10px; color: {color}; font-weight: 500; border: none; font-size: 11px;">
                    {formatted_value}
                </td>"""
        
        # Calculate and add YoY change
        if len(values) >= 2 and values[0] is not None and values[1] is not None:
            yoy_change = calculate_yoy_change(values[0], values[1])
            yoy_color = "#059669" if yoy_change.startswith('+') else "#DC2626" if yoy_change.startswith('-') else "#6B7280"
        else:
            yoy_change = 'N/A'
            yoy_color = "#6B7280"
            
        html += f"""
                <td style="text-align: right; padding: 8px 10px; color: {yoy_color}; font-weight: 600; font-size: 10px; border: none;">
                    {yoy_change}
                </td>
            </tr>"""
    
    html += """
        </tbody>
    </table>
</div>"""
    
    return html

def generate_compact_cashflow_table(cashflow_data, years):
    """Generate a compact, modern cash flow table with comprehensive metrics"""
    
    if not cashflow_data or not years or len(years) < 2:
        return "<p style='color: #666; font-style: italic;'>Cash flow data not available</p>"
    
    display_years = years[:3] if len(years) >= 3 else years
    
    html = f"""
<div style="margin: 20px 0;">
    <table style="
        width: 100%; 
        border-collapse: collapse; 
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif; 
        font-size: 11px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        border-radius: 8px;
        overflow: hidden;
        background: white;
    ">
        <thead>
            <tr style="background: linear-gradient(135deg, #059669 0%, #10B981 100%); color: white; height: 45px;">
                <th style="text-align: left; padding: 12px 16px; font-weight: 600; font-size: 12px; border: none;">
                    CASH FLOW STATEMENT
                </th>"""
    
    # Add year headers with exact dates
    for year in display_years:
        # Show the exact date as provided (2024-09-30)
        year_header = year
        html += f"""
                <th style="text-align: right; padding: 12px 10px; font-weight: 600; font-size: 11px; border: none;">
                    {year_header}
                </th>"""
    
    html += """
                <th style="text-align: right; padding: 12px 10px; font-weight: 600; font-size: 11px; border: none;">
                    YoY %
                </th>
            </tr>
        </thead>
        <tbody>"""
    
    # Comprehensive cash flow metrics - Investment Banking Standard
    key_metrics = [
        ('Operating Cash Flow', ['Operating Cash Flow']),
        ('Depreciation & Amortization', ['Depreciation', 'Amortization']),
        ('Changes in Working Capital', ['Change In Working Capital']),
        ('Deferred Tax', ['Deferred Tax']),
        ('Stock Based Compensation', ['Stock Based Compensation']),
        ('Capital Expenditure', ['Capital Expenditure']),
        ('Free Cash Flow', ['Free Cash Flow']),
        ('Acquisitions', ['Net Business Purchase And Sale']),
        ('Investment Activities', ['Purchase Of Investment']),
        ('Sale of Investments', ['Sale Of Investment']),
        ('Investing Cash Flow', ['Investing Cash Flow']),
        ('Debt Issuance', ['Long Term Debt Issuance']),
        ('Debt Repayment', ['Long Term Debt Payments']),
        ('Dividends Paid', ['Cash Dividends Paid', 'Dividends Paid']),
        ('Share Repurchases', ['Repurchase Of Capital Stock']),
        ('Financing Cash Flow', ['Financing Cash Flow']),
        ('Net Change in Cash', ['Changes In Cash'])
    ]
    
    row_count = 0
    for metric_name, possible_keys in key_metrics:
        # Find the metric in the data
        metric_value = None
        for key in possible_keys:
            for year in display_years:
                if year in cashflow_data and key in cashflow_data[year]:
                    metric_value = key
                    break
            if metric_value:
                break
        
        if not metric_value:
            continue
            
        # Alternate row colors
        row_bg = "#F8FAFC" if row_count % 2 == 0 else "#FFFFFF"
        row_count += 1
        
        html += f"""
            <tr style="background: {row_bg}; height: 35px; border-bottom: 1px solid #E2E8F0;">
                <td style="padding: 8px 16px; font-weight: 500; color: #2D3748; border: none; font-size: 11px;">
                    {metric_name}
                </td>"""
        
        # Add values for each year
        values = []
        for year in display_years:
            if year in cashflow_data and metric_value in cashflow_data[year]:
                value = cashflow_data[year][metric_value]
                formatted_value = format_financial_value(value)
                values.append(value)
            else:
                formatted_value = 'N/A'
                values.append(None)
                
            # Color coding for positive/negative values
            color = "#059669" if formatted_value.startswith('$') and not formatted_value.startswith('$-') else "#DC2626" if formatted_value.startswith('$-') else "#374151"
            
            html += f"""
                <td style="text-align: right; padding: 8px 10px; color: {color}; font-weight: 500; border: none; font-size: 11px;">
                    {formatted_value}
                </td>"""
        
        # Calculate and add YoY change
        if len(values) >= 2 and values[0] is not None and values[1] is not None:
            yoy_change = calculate_yoy_change(values[0], values[1])
            yoy_color = "#059669" if yoy_change.startswith('+') else "#DC2626" if yoy_change.startswith('-') else "#6B7280"
        else:
            yoy_change = 'N/A'
            yoy_color = "#6B7280"
            
        html += f"""
                <td style="text-align: right; padding: 8px 10px; color: {yoy_color}; font-weight: 600; font-size: 10px; border: none;">
                    {yoy_change}
                </td>
            </tr>"""
    
    html += """
        </tbody>
    </table>
</div>"""
    
    return html