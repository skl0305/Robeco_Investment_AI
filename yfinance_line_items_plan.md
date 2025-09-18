# 📊 YFINANCE LINE ITEMS SELECTION PLAN

## 🎯 DATA STRUCTURE ANALYSIS

### Key Findings:
- **Years Available**: Last 5 years with exact timestamps (e.g., 2024-09-30)
- **Data Quality**: Real values in actual dollar amounts (not millions/billions)
- **Consistency**: Line item names are consistent across companies
- **Format**: All values are raw numbers that need formatting

## 📈 INCOME STATEMENT - Selected Line Items

### 🏆 PRIORITY 1 (Core Items - Always Include):
1. **Total Revenue** - Main revenue line
2. **Gross Profit** - Revenue minus cost of goods sold
3. **Operating Income** - Core operating profitability  
4. **Net Income** - Bottom line profit
5. **Diluted EPS** - Earnings per share (formatted differently)

### 🥈 PRIORITY 2 (If Available):
6. **EBITDA** - Earnings before interest, taxes, depreciation, amortization
7. **Operating Expense** - Total operating costs
8. **Tax Provision** - Tax expense

### 💡 Reasoning:
- Covers full income statement flow: Revenue → Gross → Operating → Net
- EPS is special (already per-share, not total dollars)
- EBITDA is key for valuation multiples

## 📋 BALANCE SHEET - Selected Line Items  

### 🏆 PRIORITY 1 (Core Items - Always Include):
1. **Total Assets** - Size of company
2. **Current Assets** - Short-term liquidity
3. **Total Debt** - All debt obligations
4. **Current Liabilities** - Short-term obligations  
5. **Stockholders Equity** - Shareholder value

### 🥈 PRIORITY 2 (If Available):
6. **Working Capital** - Current Assets - Current Liabilities
7. **Cash And Cash Equivalents** - Liquidity position
8. **Net PPE** - Property, plant, equipment

### 💡 Reasoning:
- Covers key balance sheet categories: Assets, Liabilities, Equity
- Working Capital shows operational efficiency
- Debt levels critical for financial health

## 💰 CASH FLOW STATEMENT - Selected Line Items

### 🏆 PRIORITY 1 (Core Items - Always Include):
1. **Operating Cash Flow** - Cash from operations
2. **Investing Cash Flow** - Capital allocation (usually negative)
3. **Financing Cash Flow** - Debt/equity activities
4. **Free Cash Flow** - Operating CF minus CapEx
5. **Capital Expenditure** - Investment in assets (negative)

### 🥈 PRIORITY 2 (If Available):  
6. **Changes In Cash** - Net change in cash position
7. **Cash Dividends Paid** - Shareholder returns
8. **Repurchase Of Capital Stock** - Share buybacks

### 💡 Reasoning:
- Three main cash flow categories covered
- Free Cash Flow is key valuation metric
- CapEx shows investment intensity

## 🎨 FORMATTING STRATEGY

### Value Formatting:
- **Billions**: $281.7B (if ≥ $1B)
- **Millions**: $245M (if ≥ $1M) 
- **Thousands**: $245K (if ≥ $1K)
- **EPS Special**: $14.25 (always show decimals)
- **Percentages**: +15.2% / -2.8% (with color coding)

### Color Coding:
- **Green (positive)**: Revenue growth, profit increases, positive cash flow
- **Red (negative)**: Losses, cash outflows, debt increases
- **Gray (neutral)**: Stable metrics, N/A values

## 🏗️ HTML TABLE STRUCTURE

```html
<table class="financial-table">
    <thead>
        <tr>
            <th>INCOME STATEMENT</th>
            <th class="text-right">2024</th>
            <th class="text-right">2023</th>
            <th class="text-right">2022</th>
            <th class="text-right">YoY %</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Total Revenue</td>
            <td class="text-right">$281.7B</td>
            <td class="text-right">$245.1B</td>
            <td class="text-right">$211.9B</td>
            <td class="text-right positive">+14.9%</td>
        </tr>
        <!-- More rows... -->
    </tbody>
</table>
```

## ✅ IMPLEMENTATION BENEFITS

1. **Real Company Data**: Uses actual yfinance financials, not fake data
2. **Actual Dates**: Shows real reporting periods (2024, 2023, 2022)  
3. **Important Metrics**: Covers all key financial statement line items
4. **Professional Format**: Clean, investment-grade presentation
5. **Zero AI Complexity**: Pre-built tables eliminate generation overhead

This plan ensures we use the most important and consistently available yfinance data while maintaining professional investment report standards.