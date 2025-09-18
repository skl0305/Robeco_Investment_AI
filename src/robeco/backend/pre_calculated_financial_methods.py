"""
Pre-calculated financial statement methods for direct AI prompt integration.
These methods extract and format financial data outside the AI prompt for better reliability.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

def extract_pre_calculated_financial_tables(financial_data: Dict) -> Dict[str, Any]:
    """Pre-calculate all financial statement values for direct use in AI prompt"""
    logger.info("📊 Pre-calculating financial statement table values for AI prompt")
    
    try:
        # Extract raw statements
        income_annual = financial_data.get('income_statement_annual', {})
        balance_annual = financial_data.get('balance_sheet_annual', {})
        cashflow_annual = financial_data.get('cashflow_annual', {})
        
        # Get available years (sorted newest to oldest)
        years = sorted(income_annual.keys(), reverse=True) if income_annual else []
        logger.info(f"📅 Available financial years: {years}")
        
        # Pre-calculate Income Statement Table
        income_table = calculate_income_statement_table(income_annual, years)
        
        # Pre-calculate Balance Sheet Table  
        balance_table = calculate_balance_sheet_table(balance_annual, years)
        
        # Pre-calculate Cash Flow Table
        cashflow_table = calculate_cashflow_table(cashflow_annual, years)
        
        return {
            'income_statement_table': income_table,
            'balance_sheet_table': balance_table,
            'cashflow_table': cashflow_table,
            'years_available': years,
            'data_quality': {
                'income_data_available': bool(income_annual),
                'balance_data_available': bool(balance_annual),
                'cashflow_data_available': bool(cashflow_annual)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Error pre-calculating financial tables: {e}")
        return {
            'income_statement_table': {},
            'balance_sheet_table': {},
            'cashflow_table': {},
            'years_available': [],
            'data_quality': {
                'income_data_available': False,
                'balance_data_available': False,
                'cashflow_data_available': False
            }
        }

def calculate_income_statement_table(income_annual: Dict, years: List[str]) -> Dict[str, Any]:
    """Calculate comprehensive pre-formatted income statement table data"""
    try:
        table_data = {}
        recent_years = years[:4] if isinstance(years, list) and len(years) >= 4 else (years if isinstance(years, list) else [])
        
        for year in recent_years:
            year_data = income_annual.get(year, {})
            
            # Extract comprehensive income statement items (using exact yfinance field names)
            revenue = safe_extract_financial_value(year_data, ['Total Revenue', 'Operating Revenue'])
            cost_of_revenue = safe_extract_financial_value(year_data, ['Cost Of Revenue'])
            gross_profit = safe_extract_financial_value(year_data, ['Gross Profit'])
            operating_expense = safe_extract_financial_value(year_data, ['Operating Expense'])
            rd_expense = safe_extract_financial_value(year_data, ['Research And Development'])
            sga_expense = safe_extract_financial_value(year_data, ['Selling General And Administration'])
            operating_income = safe_extract_financial_value(year_data, ['Operating Income'])
            interest_expense = safe_extract_financial_value(year_data, ['Interest Expense'])
            other_income = safe_extract_financial_value(year_data, ['Other Income Expense'])
            pretax_income = safe_extract_financial_value(year_data, ['Pretax Income'])
            tax_provision = safe_extract_financial_value(year_data, ['Tax Provision'])
            net_income = safe_extract_financial_value(year_data, ['Net Income'])
            diluted_eps = safe_extract_financial_value(year_data, ['Diluted EPS'])
            basic_eps = safe_extract_financial_value(year_data, ['Basic EPS'])
            ebitda = safe_extract_financial_value(year_data, ['EBITDA', 'Normalized EBITDA'])
            ebit = safe_extract_financial_value(year_data, ['EBIT'])
            
            # Calculate margins and ratios
            gross_margin = (gross_profit / revenue * 100) if revenue and gross_profit else None
            operating_margin = (operating_income / revenue * 100) if revenue and operating_income else None
            net_margin = (net_income / revenue * 100) if revenue and net_income else None
            ebitda_margin = (ebitda / revenue * 100) if revenue and ebitda else None
            tax_rate = (tax_provision / pretax_income * 100) if pretax_income and tax_provision else None
            
            table_data[year] = {
                'revenue': format_financial_number(revenue),
                'cost_of_revenue': format_financial_number(cost_of_revenue),
                'gross_profit': format_financial_number(gross_profit),
                'rd_expense': format_financial_number(rd_expense),
                'sga_expense': format_financial_number(sga_expense),
                'operating_expense': format_financial_number(operating_expense),
                'operating_income': format_financial_number(operating_income),
                'interest_expense': format_financial_number(interest_expense),
                'other_income': format_financial_number(other_income),
                'pretax_income': format_financial_number(pretax_income),
                'tax_provision': format_financial_number(tax_provision),
                'net_income': format_financial_number(net_income),
                'diluted_eps': f"${diluted_eps:.2f}" if diluted_eps else "N/A",
                'basic_eps': f"${basic_eps:.2f}" if basic_eps else "N/A",
                'ebitda': format_financial_number(ebitda),
                'ebit': format_financial_number(ebit),
                'gross_margin': f"{gross_margin:.1f}%" if gross_margin else "N/A",
                'operating_margin': f"{operating_margin:.1f}%" if operating_margin else "N/A",
                'net_margin': f"{net_margin:.1f}%" if net_margin else "N/A",
                'ebitda_margin': f"{ebitda_margin:.1f}%" if ebitda_margin else "N/A",
                'tax_rate': f"{tax_rate:.1f}%" if tax_rate else "N/A"
            }
        
        # Calculate YoY changes for latest vs previous year
        if len(recent_years) >= 2:
            latest_year = recent_years[0]
            previous_year = recent_years[1]
            latest_data = income_annual.get(latest_year, {})
            previous_data = income_annual.get(previous_year, {})
            
            table_data['yoy_changes'] = calculate_financial_yoy_changes(latest_data, previous_data)
        
        return {
            'years': recent_years,
            'data': table_data,
            'has_data': bool(table_data)
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculating income statement table: {e}")
        return {'years': [], 'data': {}, 'has_data': False}

def calculate_balance_sheet_table(balance_annual: Dict, years: List[str]) -> Dict[str, Any]:
    """Calculate comprehensive pre-formatted balance sheet table data"""
    try:
        table_data = {}
        recent_years = years[:4] if isinstance(years, list) and len(years) >= 4 else (years if isinstance(years, list) else [])
        
        for year in recent_years:
            year_data = balance_annual.get(year, {})
            
            # Extract comprehensive balance sheet items (using exact yfinance field names)
            # Assets
            total_assets = safe_extract_financial_value(year_data, ['Total Assets'])
            current_assets = safe_extract_financial_value(year_data, ['Current Assets'])
            cash_equivalents = safe_extract_financial_value(year_data, ['Cash And Cash Equivalents'])
            receivables = safe_extract_financial_value(year_data, ['Receivables', 'Accounts Receivable'])
            inventory = safe_extract_financial_value(year_data, ['Inventory'])
            ppe_net = safe_extract_financial_value(year_data, ['Net PPE'])
            goodwill = safe_extract_financial_value(year_data, ['Goodwill'])
            
            # Liabilities
            total_liabilities = safe_extract_financial_value(year_data, ['Total Liabilities Net Minority Interest'])
            current_liabilities = safe_extract_financial_value(year_data, ['Current Liabilities'])
            accounts_payable = safe_extract_financial_value(year_data, ['Accounts Payable'])
            total_debt = safe_extract_financial_value(year_data, ['Total Debt'])
            long_term_debt = safe_extract_financial_value(year_data, ['Long Term Debt'])
            current_debt = safe_extract_financial_value(year_data, ['Current Debt'])
            
            # Equity
            total_equity = safe_extract_financial_value(year_data, ['Common Stock Equity', 'Stockholders Equity'])
            retained_earnings = safe_extract_financial_value(year_data, ['Retained Earnings'])
            working_capital = safe_extract_financial_value(year_data, ['Working Capital'])
            
            # Calculate ratios and metrics
            current_ratio = (current_assets / current_liabilities) if current_assets and current_liabilities else None
            quick_ratio = ((current_assets - inventory) / current_liabilities) if current_assets and inventory and current_liabilities else None
            debt_equity = (total_debt / total_equity) if total_debt and total_equity else None
            debt_assets = (total_debt / total_assets) if total_debt and total_assets else None
            asset_turnover = None  # Would need revenue from income statement
            roa_approx = None  # Would need net income from income statement
            
            table_data[year] = {
                'total_assets': format_financial_number(total_assets),
                'current_assets': format_financial_number(current_assets),
                'cash_equivalents': format_financial_number(cash_equivalents),
                'receivables': format_financial_number(receivables),
                'inventory': format_financial_number(inventory),
                'ppe_net': format_financial_number(ppe_net),
                'goodwill': format_financial_number(goodwill),
                'total_liabilities': format_financial_number(total_liabilities),
                'current_liabilities': format_financial_number(current_liabilities),
                'accounts_payable': format_financial_number(accounts_payable),
                'total_debt': format_financial_number(total_debt),
                'long_term_debt': format_financial_number(long_term_debt),
                'current_debt': format_financial_number(current_debt),
                'total_equity': format_financial_number(total_equity),
                'retained_earnings': format_financial_number(retained_earnings),
                'working_capital': format_financial_number(working_capital),
                'current_ratio': f"{current_ratio:.2f}" if current_ratio else "N/A",
                'quick_ratio': f"{quick_ratio:.2f}" if quick_ratio else "N/A",
                'debt_equity_ratio': f"{debt_equity:.2f}" if debt_equity else "N/A",
                'debt_assets_ratio': f"{debt_assets:.2f}" if debt_assets else "N/A"
            }
        
        # Calculate YoY changes
        if len(recent_years) >= 2:
            latest_year = recent_years[0]
            previous_year = recent_years[1]
            latest_data = balance_annual.get(latest_year, {})
            previous_data = balance_annual.get(previous_year, {})
            
            table_data['yoy_changes'] = calculate_financial_yoy_changes(latest_data, previous_data)
        
        return {
            'years': recent_years,
            'data': table_data,
            'has_data': bool(table_data)
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculating balance sheet table: {e}")
        return {'years': [], 'data': {}, 'has_data': False}

def calculate_cashflow_table(cashflow_annual: Dict, years: List[str]) -> Dict[str, Any]:
    """Calculate comprehensive pre-formatted cash flow table data"""
    try:
        table_data = {}
        recent_years = years[:4] if isinstance(years, list) and len(years) >= 4 else (years if isinstance(years, list) else [])
        
        for year in recent_years:
            year_data = cashflow_annual.get(year, {})
            
            # Extract comprehensive cash flow items (using exact yfinance field names)
            # Operating Activities
            operating_cf = safe_extract_financial_value(year_data, ['Operating Cash Flow'])
            net_income_continuing = safe_extract_financial_value(year_data, ['Net Income From Continuing Operations'])
            depreciation = safe_extract_financial_value(year_data, ['Depreciation And Amortization'])
            working_capital_change = safe_extract_financial_value(year_data, ['Change In Working Capital'])
            stock_compensation = safe_extract_financial_value(year_data, ['Stock Based Compensation'])
            
            # Investing Activities
            investing_cf = safe_extract_financial_value(year_data, ['Investing Cash Flow'])
            capex = safe_extract_financial_value(year_data, ['Capital Expenditure'])
            business_acquisitions = safe_extract_financial_value(year_data, ['Purchase Of Business'])
            investment_purchases = safe_extract_financial_value(year_data, ['Purchase Of Investment'])
            investment_sales = safe_extract_financial_value(year_data, ['Sale Of Investment'])
            
            # Financing Activities
            financing_cf = safe_extract_financial_value(year_data, ['Financing Cash Flow'])
            debt_issuance = safe_extract_financial_value(year_data, ['Issuance Of Debt'])
            debt_repayment = safe_extract_financial_value(year_data, ['Repayment Of Debt'])
            stock_repurchases = safe_extract_financial_value(year_data, ['Repurchase Of Capital Stock'])
            dividends_paid = safe_extract_financial_value(year_data, ['Cash Dividends Paid'])
            
            # Other
            cash_beginning = safe_extract_financial_value(year_data, ['Beginning Cash Position'])
            cash_ending = safe_extract_financial_value(year_data, ['End Cash Position'])
            
            # Calculate key metrics
            free_cf = (operating_cf + capex) if operating_cf and capex else None
            free_cf_alt = safe_extract_financial_value(year_data, ['Free Cash Flow'])  # Some companies report this directly
            if free_cf_alt:
                free_cf = free_cf_alt
            
            capex_revenue_ratio = None  # Would need revenue from income statement
            fcf_conversion = (free_cf / net_income_continuing) if free_cf and net_income_continuing else None
            
            table_data[year] = {
                'operating_cashflow': format_financial_number(operating_cf),
                'net_income_continuing': format_financial_number(net_income_continuing),
                'depreciation': format_financial_number(depreciation),
                'working_capital_change': format_financial_number(working_capital_change),
                'stock_compensation': format_financial_number(stock_compensation),
                'investing_cashflow': format_financial_number(investing_cf),
                'capex': format_financial_number(capex),
                'business_acquisitions': format_financial_number(business_acquisitions),
                'investment_purchases': format_financial_number(investment_purchases),
                'investment_sales': format_financial_number(investment_sales),
                'financing_cashflow': format_financial_number(financing_cf),
                'debt_issuance': format_financial_number(debt_issuance),
                'debt_repayment': format_financial_number(debt_repayment),
                'stock_repurchases': format_financial_number(stock_repurchases),
                'dividends_paid': format_financial_number(dividends_paid),
                'cash_beginning': format_financial_number(cash_beginning),
                'cash_ending': format_financial_number(cash_ending),
                'free_cashflow': format_financial_number(free_cf),
                'fcf_conversion_ratio': f"{fcf_conversion:.2f}" if fcf_conversion else "N/A"
            }
        
        # Calculate YoY changes
        if len(recent_years) >= 2:
            latest_year = recent_years[0]
            previous_year = recent_years[1]
            latest_data = cashflow_annual.get(latest_year, {})
            previous_data = cashflow_annual.get(previous_year, {})
            
            table_data['yoy_changes'] = calculate_financial_yoy_changes(latest_data, previous_data)
        
        return {
            'years': recent_years,
            'data': table_data,
            'has_data': bool(table_data)
        }
        
    except Exception as e:
        logger.error(f"❌ Error calculating cash flow table: {e}")
        return {'years': [], 'data': {}, 'has_data': False}

def safe_extract_financial_value(year_data: Dict, field_names: List[str]) -> float:
    """Safely extract financial value from multiple possible field names"""
    for field_name in field_names:
        if field_name in year_data and year_data[field_name] is not None:
            try:
                return float(year_data[field_name])
            except (ValueError, TypeError):
                continue
    return None

def format_financial_number(value: float) -> str:
    """Format financial number for display"""
    if value is None:
        return "N/A"
    
    abs_value = abs(value)
    if abs_value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif abs_value >= 1e6:
        return f"${value/1e6:.1f}M"
    elif abs_value >= 1e3:
        return f"${value/1e3:.0f}K"
    else:
        return f"${value:.2f}"

def calculate_financial_yoy_changes(latest_data: Dict, previous_data: Dict) -> Dict[str, str]:
    """Calculate year-over-year percentage changes for key financial metrics"""
    yoy_changes = {}
    
    # Common metrics to calculate YoY for (using exact yfinance field names)
    metrics_to_track = [
        'Total Revenue', 'Operating Revenue', 'Gross Profit', 'Operating Income', 'Net Income',
        'Total Assets', 'Current Assets', 'Total Debt', 'Common Stock Equity', 'Stockholders Equity',
        'Operating Cash Flow', 'Capital Expenditure'
    ]
    
    for metric in metrics_to_track:
        latest = safe_extract_financial_value(latest_data, [metric])
        previous = safe_extract_financial_value(previous_data, [metric])
        
        if latest is not None and previous is not None and previous != 0:
            change = ((latest - previous) / abs(previous)) * 100
            yoy_changes[metric] = f"{change:+.1f}%"
        else:
            yoy_changes[metric] = "N/A"
    
    return yoy_changes

def convert_processed_to_raw_format(processed_data: Dict, statement_type: str) -> Dict:
    """Convert processed financial data back to raw yfinance format for compact tables"""
    raw_data = {}
    
    for year, year_data in processed_data.items():
        if year == 'yoy_changes':
            continue
            
        raw_year_data = {}
        
        if statement_type == 'income':
            # Map processed keys back to yfinance keys
            key_mapping = {
                'revenue': 'Total Revenue',
                'cost_of_revenue': 'Cost Of Revenue', 
                'gross_profit': 'Gross Profit',
                'operating_income': 'Operating Income',
                'net_income': 'Net Income',
                'diluted_eps': 'Diluted EPS',
                'ebitda': 'EBITDA'
            }
        elif statement_type == 'balance':
            key_mapping = {
                'total_assets': 'Total Assets',
                'cash_equivalents': 'Cash And Cash Equivalents',
                'total_debt': 'Total Debt',
                'current_debt': 'Current Debt',
                'long_term_debt': 'Long Term Debt',
                'total_equity': 'Total Equity Gross Minority Interest'
            }
        elif statement_type == 'cashflow':
            key_mapping = {
                'operating_cashflow': 'Operating Cash Flow',
                'capex': 'Capital Expenditure',
                'free_cashflow': 'Free Cash Flow',
                'investing_cashflow': 'Investing Cash Flow',
                'financing_cashflow': 'Financing Cash Flow'
            }
        else:
            key_mapping = {}
        
        # Convert formatted values back to numbers
        for processed_key, raw_key in key_mapping.items():
            if processed_key in year_data:
                formatted_value = year_data[processed_key]
                if formatted_value and formatted_value != 'N/A':
                    # Convert formatted string back to number
                    try:
                        if '$' in formatted_value:
                            # Remove $ and convert B/M/K to numbers
                            clean_value = formatted_value.replace('$', '').replace(',', '')
                            if 'B' in clean_value:
                                raw_data.setdefault(year, {})[raw_key] = float(clean_value.replace('B', '')) * 1e9
                            elif 'M' in clean_value:
                                raw_data.setdefault(year, {})[raw_key] = float(clean_value.replace('M', '')) * 1e6
                            elif 'K' in clean_value:
                                raw_data.setdefault(year, {})[raw_key] = float(clean_value.replace('K', '')) * 1e3
                            else:
                                raw_data.setdefault(year, {})[raw_key] = float(clean_value)
                        else:
                            raw_data.setdefault(year, {})[raw_key] = float(formatted_value.replace('%', ''))
                    except (ValueError, TypeError):
                        continue
    
    return raw_data

def generate_ready_to_use_prompt_data(pre_calculated_tables: Dict) -> str:
    """Generate comprehensive ready-to-use HTML tables for AI prompt"""
    
    # Import the new compact table generators
    try:
        from compact_financial_tables import (
            generate_compact_income_statement_table,
            generate_compact_balance_sheet_table,
            generate_compact_cashflow_table
        )
        use_compact_tables = True
    except ImportError:
        logger.warning("⚠️ Compact tables not available, using legacy tables")
        use_compact_tables = False
    
    income_table = pre_calculated_tables.get('income_statement_table', {})
    balance_table = pre_calculated_tables.get('balance_sheet_table', {})
    cashflow_table = pre_calculated_tables.get('cashflow_table', {})
    years = pre_calculated_tables.get('years_available', [])
    
    prompt_data = f"""
======================================================================================
📊 COMPREHENSIVE PRE-CALCULATED FINANCIAL STATEMENT TABLES (READY TO USE)
======================================================================================

**🎯 SLIDE 8 - INCOME STATEMENT TABLE (id="slide-financial-income-statement"):**
Years Available: {', '.join(years[:4]) if isinstance(years, list) else 'None'}
Data Quality: {income_table.get('has_data', False)}

**COMPLETE HTML TABLE - COPY EXACTLY INTO SLIDE HTML:**
"""
    
    # Generate comprehensive Income Statement HTML
    if use_compact_tables and income_table.get('has_data') and income_table.get('data'):
        # Convert processed data back to raw format for compact tables
        raw_income_data = convert_processed_to_raw_format(income_table.get('data', {}), 'income')
        prompt_data += generate_compact_income_statement_table(raw_income_data, years)
    elif income_table.get('has_data') and income_table.get('data'):
        prompt_data += generate_income_statement_html_table(income_table)
    else:
        prompt_data += "<p>Income statement data not available</p>\n"
    
    prompt_data += f"""

**🎯 SLIDE 9 - BALANCE SHEET TABLE (id="slide-financial-balance-sheet"):**
Data Quality: {balance_table.get('has_data', False)}

**COMPLETE HTML TABLE - COPY EXACTLY INTO SLIDE HTML:**
"""
    
    # Generate comprehensive Balance Sheet HTML
    if use_compact_tables and balance_table.get('has_data') and balance_table.get('data'):
        # Convert processed data back to raw format for compact tables
        raw_balance_data = convert_processed_to_raw_format(balance_table.get('data', {}), 'balance')
        prompt_data += generate_compact_balance_sheet_table(raw_balance_data, years)
    elif balance_table.get('has_data') and balance_table.get('data'):
        prompt_data += generate_balance_sheet_html_table(balance_table)
    else:
        prompt_data += "<p>Balance sheet data not available</p>\n"
    
    prompt_data += f"""

**🎯 SLIDE 10 - CASH FLOW TABLE (id="slide-financial-cash-flow-statement"):**
Data Quality: {cashflow_table.get('has_data', False)}

**COMPLETE HTML TABLE - COPY EXACTLY INTO SLIDE HTML:**
"""
    
    # Generate comprehensive Cash Flow HTML
    if use_compact_tables and cashflow_table.get('has_data') and cashflow_table.get('data'):
        # Convert processed data back to raw format for compact tables
        raw_cashflow_data = convert_processed_to_raw_format(cashflow_table.get('data', {}), 'cashflow')
        prompt_data += generate_compact_cashflow_table(raw_cashflow_data, years)
    elif cashflow_table.get('has_data') and cashflow_table.get('data'):
        prompt_data += generate_cashflow_html_table(cashflow_table)
    else:
        prompt_data += "<p>Cash flow data not available</p>\n"
    
    prompt_data += f"""

======================================================================================
🚨 CRITICAL INSTRUCTIONS FOR AI ANALYSIS:
======================================================================================

**MANDATORY REQUIREMENTS:**
1. **USE ONLY THE PRE-CALCULATED DATA ABOVE** - Do NOT try to extract financial data
2. **COPY HTML TABLES EXACTLY** - Paste the complete table HTML into each slide
3. **ANALYZE THE DISPLAYED DATA** - Focus on trends, ratios, and year-over-year changes
4. **WRITE COMPREHENSIVE ANALYSIS** - 400-600 words per statement explaining:
   - Key financial trends and performance indicators
   - Margin analysis and profitability metrics
   - Working capital and liquidity position
   - Cash flow quality and capital allocation
   - Investment implications and risk factors

**DATA YEARS AVAILABLE:** {', '.join(years[:4]) if isinstance(years, list) else 'None'}
**TOTAL FIELDS PER STATEMENT:**
- Income Statement: 21 key metrics + ratios
- Balance Sheet: 20 key metrics + ratios  
- Cash Flow: 18 key metrics + ratios

**EXAMPLE ANALYSIS APPROACH:**
"Based on the financial data shown in the table above, [Company] demonstrates [trend]. 
The revenue growth of [X]% year-over-year indicates [analysis]. Operating margins 
of [Y]% compared to [Z]% in the prior year suggest [implications]..."

======================================================================================
"""
    
    return prompt_data

def generate_income_statement_html_table(income_table: Dict) -> str:
    """Generate comprehensive HTML table for income statement"""
    data = income_table.get('data', {})
    years_raw = income_table.get('years', [])
    years = years_raw[:3] if isinstance(years_raw, list) else []  # Latest 3 years
    
    if not data or not years:
        return "<p>Income statement data not available</p>\n"
    
    html = """
<table class="financial-table-compact" style="width:100%; border-collapse: collapse; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 15px 0; font-size: 13px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
    <thead>
        <tr style="background: linear-gradient(135deg, #003f5f 0%, #1565C0 100%); color: white; height: 40px;">
            <th style="text-align:left; padding:8px 12px; border:none; font-weight: 600; font-size: 14px;">INCOME STATEMENT</th>
"""
    
    for year in years:
        short_year = year[-2:] if len(year) >= 2 else year  # Show only last 2 digits  
        html += f'            <th style="text-align:right; padding:8px 10px; border:none; font-weight: 600; font-size: 13px;">FY{short_year}</th>\n'
    html += '            <th style="text-align:right; padding:8px 10px; border:none; font-weight: 600; font-size: 13px;">Δ%</th>\n'
    html += """        </tr>
    </thead>
    <tbody style="background: white;">
"""
    
    # Revenue section
    revenue_rows = [
        ('Total Revenue', 'revenue', 'Total Revenue'),
        ('Cost of Revenue', 'cost_of_revenue', 'Cost Of Revenue'),
        ('Gross Profit', 'gross_profit', 'Gross Profit')
    ]
    
    for display_name, data_key, yoy_key in revenue_rows:
        html += f'        <tr><td style="padding:8px; border:1px solid #ddd; font-weight:bold;">{display_name}</td>'
        for year in years:
            value = data.get(year, {}).get(data_key, 'N/A')
            html += f'<td style="text-align:right; padding:8px; border:1px solid #ddd;">{value}</td>'
        yoy_change = data.get('yoy_changes', {}).get(yoy_key, 'N/A')
        color = "#228B22" if yoy_change != 'N/A' and '+' in str(yoy_change) else "#DC143C" if yoy_change != 'N/A' and '-' in str(yoy_change) else "#666"
        html += f'<td style="text-align:right; padding:8px; border:1px solid #ddd; color:{color};">{yoy_change}</td></tr>\n'
    
    # Operating section  
    html += '        <tr style="background-color: #f8f9fa;"><td colspan="5" style="padding:4px; border:1px solid #ddd; font-size:12px; color:#666;">OPERATING METRICS</td></tr>\n'
    
    operating_rows = [
        ('R&D Expense', 'rd_expense', 'Research And Development'),
        ('SG&A Expense', 'sga_expense', 'Selling General And Administration'),
        ('Operating Income', 'operating_income', 'Operating Income'),
        ('EBITDA', 'ebitda', 'EBITDA'),
        ('EBIT', 'ebit', 'EBIT')
    ]
    
    for display_name, data_key, yoy_key in operating_rows:
        html += f'        <tr><td style="padding:8px; border:1px solid #ddd;">{display_name}</td>'
        for year in years:
            value = data.get(year, {}).get(data_key, 'N/A')
            html += f'<td style="text-align:right; padding:8px; border:1px solid #ddd;">{value}</td>'
        yoy_change = data.get('yoy_changes', {}).get(yoy_key, 'N/A')
        color = "#228B22" if yoy_change != 'N/A' and '+' in str(yoy_change) else "#DC143C" if yoy_change != 'N/A' and '-' in str(yoy_change) else "#666"
        html += f'<td style="text-align:right; padding:8px; border:1px solid #ddd; color:{color};">{yoy_change}</td></tr>\n'
    
    # Net income section
    html += '        <tr style="background-color: #f8f9fa;"><td colspan="5" style="padding:4px; border:1px solid #ddd; font-size:12px; color:#666;">NET INCOME & EPS</td></tr>\n'
    
    bottom_rows = [
        ('Interest Expense', 'interest_expense', 'Interest Expense'),
        ('Pretax Income', 'pretax_income', 'Pretax Income'),
        ('Tax Provision', 'tax_provision', 'Tax Provision'),
        ('Net Income', 'net_income', 'Net Income'),
        ('Diluted EPS', 'diluted_eps', 'Diluted EPS'),
    ]
    
    for display_name, data_key, yoy_key in bottom_rows:
        html += f'        <tr><td style="padding:8px; border:1px solid #ddd; font-weight:{"bold" if "Net Income" in display_name else "normal"};">{display_name}</td>'
        for year in years:
            value = data.get(year, {}).get(data_key, 'N/A')
            style = 'text-align:right; padding:8px; border:1px solid #ddd;'
            if "Net Income" in display_name:
                style += ' font-weight:bold; background-color:#f0f8ff;'
            html += f'<td style="{style}">{value}</td>'
        yoy_change = data.get('yoy_changes', {}).get(yoy_key, 'N/A')
        color = "#228B22" if yoy_change != 'N/A' and '+' in str(yoy_change) else "#DC143C" if yoy_change != 'N/A' and '-' in str(yoy_change) else "#666"
        html += f'<td style="text-align:right; padding:8px; border:1px solid #ddd; color:{color};">{yoy_change}</td></tr>\n'
    
    # Margins section
    html += '        <tr style="background-color: #f8f9fa;"><td colspan="5" style="padding:4px; border:1px solid #ddd; font-size:12px; color:#666;">PROFITABILITY MARGINS</td></tr>\n'
    
    margin_rows = [
        ('Gross Margin', 'gross_margin'),
        ('Operating Margin', 'operating_margin'),
        ('EBITDA Margin', 'ebitda_margin'),
        ('Net Margin', 'net_margin'),
        ('Tax Rate', 'tax_rate')
    ]
    
    for display_name, data_key in margin_rows:
        html += f'        <tr style="background-color:#fffacd;"><td style="padding:8px; border:1px solid #ddd; font-style:italic;">{display_name}</td>'
        for year in years:
            value = data.get(year, {}).get(data_key, 'N/A')
            html += f'<td style="text-align:right; padding:8px; border:1px solid #ddd; font-style:italic;">{value}</td>'
        html += '<td style="text-align:right; padding:8px; border:1px solid #ddd;">-</td></tr>\n'
    
    html += """    </tbody>
</table>
"""
    
    return html

def generate_balance_sheet_html_table(balance_table: Dict) -> str:
    """Generate comprehensive HTML table for balance sheet"""
    data = balance_table.get('data', {})
    years_raw = balance_table.get('years', [])
    years = years_raw[:3] if isinstance(years_raw, list) else []  # Latest 3 years
    
    if not data or not years:
        return "<p>Balance sheet data not available</p>\n"
    
    html = """
<table class="financial-table" style="width:100%; border-collapse: collapse; font-family: Arial, sans-serif; margin: 20px 0;">
    <thead>
        <tr style="background-color: #003f5f; color: white;">
            <th style="text-align:left; padding:12px; border:1px solid #ddd;">BALANCE SHEET</th>
"""
    
    for year in years:
        html += f'            <th style="text-align:right; padding:12px; border:1px solid #ddd;">{year}</th>\n'
    html += '            <th style="text-align:right; padding:12px; border:1px solid #ddd;">YoY %</th>\n'
    html += """        </tr>
    </thead>
    <tbody>
"""
    
    # Assets section
    html += '        <tr style="background-color: #e8f4f8;"><td colspan="5" style="padding:8px; border:1px solid #ddd; font-weight:bold; color:#003f5f;">ASSETS</td></tr>\n'
    
    asset_rows = [
        ('Total Assets', 'total_assets', 'Total Assets'),
        ('Current Assets', 'current_assets', 'Current Assets'),
        ('Cash & Equivalents', 'cash_equivalents', 'Cash And Cash Equivalents'),
        ('Receivables', 'receivables', 'Receivables'),
        ('Inventory', 'inventory', 'Inventory'),
        ('PP&E (Net)', 'ppe_net', 'Net PPE'),
        ('Goodwill', 'goodwill', 'Goodwill')
    ]
    
    for display_name, data_key, yoy_key in asset_rows:
        html += f'        <tr><td style="padding:8px; border:1px solid #ddd; font-weight:{"bold" if "Total Assets" in display_name else "normal"};">{display_name}</td>'
        for year in years:
            value = data.get(year, {}).get(data_key, 'N/A')
            style = 'text-align:right; padding:8px; border:1px solid #ddd;'
            if "Total Assets" in display_name:
                style += ' font-weight:bold; background-color:#f0f8ff;'
            html += f'<td style="{style}">{value}</td>'
        yoy_change = data.get('yoy_changes', {}).get(yoy_key, 'N/A')
        color = "#228B22" if yoy_change != 'N/A' and '+' in str(yoy_change) else "#DC143C" if yoy_change != 'N/A' and '-' in str(yoy_change) else "#666"
        html += f'<td style="text-align:right; padding:8px; border:1px solid #ddd; color:{color};">{yoy_change}</td></tr>\n'
    
    # Liabilities section
    html += '        <tr style="background-color: #ffeee8;"><td colspan="5" style="padding:8px; border:1px solid #ddd; font-weight:bold; color:#8B4513;">LIABILITIES</td></tr>\n'
    
    liability_rows = [
        ('Total Liabilities', 'total_liabilities', 'Total Liabilities Net Minority Interest'),
        ('Current Liabilities', 'current_liabilities', 'Current Liabilities'),
        ('Accounts Payable', 'accounts_payable', 'Accounts Payable'),
        ('Total Debt', 'total_debt', 'Total Debt'),
        ('Long-term Debt', 'long_term_debt', 'Long Term Debt'),
        ('Current Debt', 'current_debt', 'Current Debt')
    ]
    
    for display_name, data_key, yoy_key in liability_rows:
        html += f'        <tr><td style="padding:8px; border:1px solid #ddd; font-weight:{"bold" if "Total Liabilities" in display_name else "normal"};">{display_name}</td>'
        for year in years:
            value = data.get(year, {}).get(data_key, 'N/A')
            style = 'text-align:right; padding:8px; border:1px solid #ddd;'
            if "Total Liabilities" in display_name:
                style += ' font-weight:bold; background-color:#fff0f0;'
            html += f'<td style="{style}">{value}</td>'
        yoy_change = data.get('yoy_changes', {}).get(yoy_key, 'N/A')
        color = "#228B22" if yoy_change != 'N/A' and '+' in str(yoy_change) else "#DC143C" if yoy_change != 'N/A' and '-' in str(yoy_change) else "#666"
        html += f'<td style="text-align:right; padding:8px; border:1px solid #ddd; color:{color};">{yoy_change}</td></tr>\n'
    
    # Equity section
    html += '        <tr style="background-color: #e8f8e8;"><td colspan="5" style="padding:8px; border:1px solid #ddd; font-weight:bold; color:#006400;">EQUITY</td></tr>\n'
    
    equity_rows = [
        ('Total Equity', 'total_equity', 'Common Stock Equity'),
        ('Retained Earnings', 'retained_earnings', 'Retained Earnings'),
        ('Working Capital', 'working_capital', 'Working Capital')
    ]
    
    for display_name, data_key, yoy_key in equity_rows:
        html += f'        <tr><td style="padding:8px; border:1px solid #ddd; font-weight:{"bold" if "Total Equity" in display_name else "normal"};">{display_name}</td>'
        for year in years:
            value = data.get(year, {}).get(data_key, 'N/A')
            style = 'text-align:right; padding:8px; border:1px solid #ddd;'
            if "Total Equity" in display_name:
                style += ' font-weight:bold; background-color:#f0fff0;'
            html += f'<td style="{style}">{value}</td>'
        yoy_change = data.get('yoy_changes', {}).get(yoy_key, 'N/A')
        color = "#228B22" if yoy_change != 'N/A' and '+' in str(yoy_change) else "#DC143C" if yoy_change != 'N/A' and '-' in str(yoy_change) else "#666"
        html += f'<td style="text-align:right; padding:8px; border:1px solid #ddd; color:{color};">{yoy_change}</td></tr>\n'
    
    # Ratios section
    html += '        <tr style="background-color: #f8f9fa;"><td colspan="5" style="padding:4px; border:1px solid #ddd; font-size:12px; color:#666;">KEY RATIOS</td></tr>\n'
    
    ratio_rows = [
        ('Current Ratio', 'current_ratio'),
        ('Quick Ratio', 'quick_ratio'),
        ('Debt/Equity Ratio', 'debt_equity_ratio'),
        ('Debt/Assets Ratio', 'debt_assets_ratio')
    ]
    
    for display_name, data_key in ratio_rows:
        html += f'        <tr style="background-color:#fffacd;"><td style="padding:8px; border:1px solid #ddd; font-style:italic;">{display_name}</td>'
        for year in years:
            value = data.get(year, {}).get(data_key, 'N/A')
            html += f'<td style="text-align:right; padding:8px; border:1px solid #ddd; font-style:italic;">{value}</td>'
        html += '<td style="text-align:right; padding:8px; border:1px solid #ddd;">-</td></tr>\n'
    
    html += """    </tbody>
</table>
"""
    
    return html

def generate_cashflow_html_table(cashflow_table: Dict) -> str:
    """Generate comprehensive HTML table for cash flow statement"""
    data = cashflow_table.get('data', {})
    years_raw = cashflow_table.get('years', [])
    years = years_raw[:3] if isinstance(years_raw, list) else []  # Latest 3 years
    
    if not data or not years:
        return "<p>Cash flow data not available</p>\n"
    
    html = """
<table class="financial-table" style="width:100%; border-collapse: collapse; font-family: Arial, sans-serif; margin: 20px 0;">
    <thead>
        <tr style="background-color: #003f5f; color: white;">
            <th style="text-align:left; padding:12px; border:1px solid #ddd;">CASH FLOW STATEMENT</th>
"""
    
    for year in years:
        html += f'            <th style="text-align:right; padding:12px; border:1px solid #ddd;">{year}</th>\n'
    html += '            <th style="text-align:right; padding:12px; border:1px solid #ddd;">YoY %</th>\n'
    html += """        </tr>
    </thead>
    <tbody>
"""
    
    # Operating activities
    html += '        <tr style="background-color: #e8f4f8;"><td colspan="5" style="padding:8px; border:1px solid #ddd; font-weight:bold; color:#003f5f;">OPERATING ACTIVITIES</td></tr>\n'
    
    operating_rows = [
        ('Operating Cash Flow', 'operating_cashflow', 'Operating Cash Flow'),
        ('Net Income (Continuing)', 'net_income_continuing', 'Net Income From Continuing Operations'),
        ('Depreciation & Amortization', 'depreciation', 'Depreciation And Amortization'),
        ('Working Capital Change', 'working_capital_change', 'Change In Working Capital'),
        ('Stock Compensation', 'stock_compensation', 'Stock Based Compensation')
    ]
    
    for display_name, data_key, yoy_key in operating_rows:
        html += f'        <tr><td style="padding:8px; border:1px solid #ddd; font-weight:{"bold" if "Operating Cash Flow" in display_name else "normal"};">{display_name}</td>'
        for year in years:
            value = data.get(year, {}).get(data_key, 'N/A')
            style = 'text-align:right; padding:8px; border:1px solid #ddd;'
            if "Operating Cash Flow" in display_name:
                style += ' font-weight:bold; background-color:#f0f8ff;'
            html += f'<td style="{style}">{value}</td>'
        yoy_change = data.get('yoy_changes', {}).get(yoy_key, 'N/A')
        color = "#228B22" if yoy_change != 'N/A' and '+' in str(yoy_change) else "#DC143C" if yoy_change != 'N/A' and '-' in str(yoy_change) else "#666"
        html += f'<td style="text-align:right; padding:8px; border:1px solid #ddd; color:{color};">{yoy_change}</td></tr>\n'
    
    # Investing activities
    html += '        <tr style="background-color: #ffeee8;"><td colspan="5" style="padding:8px; border:1px solid #ddd; font-weight:bold; color:#8B4513;">INVESTING ACTIVITIES</td></tr>\n'
    
    investing_rows = [
        ('Investing Cash Flow', 'investing_cashflow', 'Investing Cash Flow'),
        ('Capital Expenditure', 'capex', 'Capital Expenditure'),
        ('Business Acquisitions', 'business_acquisitions', 'Purchase Of Business'),
        ('Investment Purchases', 'investment_purchases', 'Purchase Of Investment'),
        ('Investment Sales', 'investment_sales', 'Sale Of Investment')
    ]
    
    for display_name, data_key, yoy_key in investing_rows:
        html += f'        <tr><td style="padding:8px; border:1px solid #ddd; font-weight:{"bold" if "Investing Cash Flow" in display_name else "normal"};">{display_name}</td>'
        for year in years:
            value = data.get(year, {}).get(data_key, 'N/A')
            style = 'text-align:right; padding:8px; border:1px solid #ddd;'
            if "Investing Cash Flow" in display_name:
                style += ' font-weight:bold; background-color:#fff0f0;'
            html += f'<td style="{style}">{value}</td>'
        yoy_change = data.get('yoy_changes', {}).get(yoy_key, 'N/A')
        color = "#228B22" if yoy_change != 'N/A' and '+' in str(yoy_change) else "#DC143C" if yoy_change != 'N/A' and '-' in str(yoy_change) else "#666"
        html += f'<td style="text-align:right; padding:8px; border:1px solid #ddd; color:{color};">{yoy_change}</td></tr>\n'
    
    # Financing activities
    html += '        <tr style="background-color: #e8f8e8;"><td colspan="5" style="padding:8px; border:1px solid #ddd; font-weight:bold; color:#006400;">FINANCING ACTIVITIES</td></tr>\n'
    
    financing_rows = [
        ('Financing Cash Flow', 'financing_cashflow', 'Financing Cash Flow'),
        ('Debt Issuance', 'debt_issuance', 'Issuance Of Debt'),
        ('Debt Repayment', 'debt_repayment', 'Repayment Of Debt'),
        ('Stock Repurchases', 'stock_repurchases', 'Repurchase Of Capital Stock'),
        ('Dividends Paid', 'dividends_paid', 'Cash Dividends Paid')
    ]
    
    for display_name, data_key, yoy_key in financing_rows:
        html += f'        <tr><td style="padding:8px; border:1px solid #ddd; font-weight:{"bold" if "Financing Cash Flow" in display_name else "normal"};">{display_name}</td>'
        for year in years:
            value = data.get(year, {}).get(data_key, 'N/A')
            style = 'text-align:right; padding:8px; border:1px solid #ddd;'
            if "Financing Cash Flow" in display_name:
                style += ' font-weight:bold; background-color:#f0fff0;'
            html += f'<td style="{style}">{value}</td>'
        yoy_change = data.get('yoy_changes', {}).get(yoy_key, 'N/A')
        color = "#228B22" if yoy_change != 'N/A' and '+' in str(yoy_change) else "#DC143C" if yoy_change != 'N/A' and '-' in str(yoy_change) else "#666"
        html += f'<td style="text-align:right; padding:8px; border:1px solid #ddd; color:{color};">{yoy_change}</td></tr>\n'
    
    # Summary section
    html += '        <tr style="background-color: #f8f9fa;"><td colspan="5" style="padding:4px; border:1px solid #ddd; font-size:12px; color:#666;">CASH POSITION & METRICS</td></tr>\n'
    
    summary_rows = [
        ('Cash Beginning', 'cash_beginning'),
        ('Cash Ending', 'cash_ending'),
        ('Free Cash Flow', 'free_cashflow'),
        ('FCF Conversion Ratio', 'fcf_conversion_ratio')
    ]
    
    for display_name, data_key in summary_rows:
        html += f'        <tr style="background-color:#{"fffacd" if "Free Cash Flow" in display_name else "white"};"><td style="padding:8px; border:1px solid #ddd; font-weight:{"bold" if "Free Cash Flow" in display_name else "normal"}; font-style:{"italic" if "Ratio" in display_name else "normal"};">{display_name}</td>'
        for year in years:
            value = data.get(year, {}).get(data_key, 'N/A')
            style = f'text-align:right; padding:8px; border:1px solid #ddd; font-weight:{"bold" if "Free Cash Flow" in display_name else "normal"}; font-style:{"italic" if "Ratio" in display_name else "normal"};'
            html += f'<td style="{style}">{value}</td>'
        html += '<td style="text-align:right; padding:8px; border:1px solid #ddd;">-</td></tr>\n'
    
    html += """    </tbody>
</table>
"""
    
    return html