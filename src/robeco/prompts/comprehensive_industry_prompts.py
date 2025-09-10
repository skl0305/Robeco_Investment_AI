#!/usr/bin/env python3
"""
Comprehensive Industry-Specific Analysis Framework
Covers 50+ specific industries with granular metrics and analysis approaches
"""

from datetime import datetime
import json
from typing import Dict, Any, Optional

class ComprehensiveIndustryDetector:
    """
    Granular industry detection with 50+ specific industry frameworks
    """
    
    @staticmethod
    def detect_industry(financial_data: Dict[str, Any]) -> str:
        """
        Detect specific industry from yfinance data
        """
        info = financial_data.get("info", {})
        sector = info.get('sector', '').lower()
        industry = info.get('industry', '').lower()
        company_name = info.get('longName', '').lower()
        
        # === REAL ESTATE INVESTMENT TRUSTS (REITs) ===
        if 'reit - industrial' in industry or 'industrial reit' in company_name:
            return 'reit_industrial'
        elif 'reit - residential' in industry or 'residential reit' in company_name:
            return 'reit_residential'  
        elif 'reit - specialty' in industry or ('reit' in industry and ('tower' in company_name or 'data' in company_name)):
            return 'reit_specialty'
        elif 'reit - retail' in industry or 'retail reit' in company_name:
            return 'reit_retail'
        elif 'reit - office' in industry or 'office reit' in company_name:
            return 'reit_office'
        elif 'reit - healthcare' in industry or 'healthcare reit' in company_name:
            return 'reit_healthcare'
        elif 'real estate' in sector or 'reit' in industry:
            return 'reit_general'
        
        # === BANKING & FINANCIAL SERVICES ===
        elif 'banks - diversified' in industry:
            return 'banks_diversified'
        elif 'banks - regional' in industry:
            return 'banks_regional'
        elif 'credit services' in industry:
            return 'credit_services'
        elif 'asset management' in industry:
            return 'asset_management'
        elif 'insurance' in industry and 'life' in industry:
            return 'insurance_life'
        elif 'insurance' in industry and 'property' in industry:
            return 'insurance_property_casualty'
        elif 'mortgage finance' in industry:
            return 'mortgage_finance'
        elif 'capital markets' in industry:
            return 'capital_markets'
        
        # === TECHNOLOGY SECTOR ===
        elif 'software - application' in industry:
            return 'software_application'
        elif 'software - infrastructure' in industry:
            return 'software_infrastructure'
        elif 'semiconductors' in industry:
            return 'semiconductors'
        elif 'consumer electronics' in industry:
            return 'consumer_electronics'
        elif 'computer hardware' in industry:
            return 'computer_hardware'
        elif 'information technology services' in industry:
            return 'it_services'
        elif 'electronic gaming & multimedia' in industry:
            return 'gaming_multimedia'
        elif 'internet content & information' in industry:
            return 'internet_content'
        elif 'solar' in industry:
            return 'solar_technology'
        
        # === HEALTHCARE SECTOR ===
        elif 'drug manufacturers - general' in industry:
            return 'pharma_large_cap'
        elif 'drug manufacturers - specialty & generic' in industry:
            return 'pharma_specialty'
        elif 'biotechnology' in industry:
            return 'biotechnology'
        elif 'medical devices' in industry:
            return 'medical_devices'
        elif 'diagnostics & research' in industry:
            return 'diagnostics_research'
        elif 'medical instruments & supplies' in industry:
            return 'medical_instruments'
        elif 'healthcare plans' in industry:
            return 'healthcare_plans'
        elif 'health information services' in industry:
            return 'health_information'
        
        # === ENERGY SECTOR ===
        elif 'oil & gas integrated' in industry:
            return 'oil_gas_integrated'
        elif 'oil & gas e&p' in industry:
            return 'oil_gas_exploration'
        elif 'oil & gas midstream' in industry:
            return 'oil_gas_midstream'
        elif 'oil & gas refining & marketing' in industry:
            return 'oil_gas_refining'
        elif 'oil & gas equipment & services' in industry:
            return 'oil_gas_services'
        elif 'renewable energy' in industry:
            return 'renewable_energy'
        
        # === UTILITIES ===
        elif 'utilities - regulated electric' in industry:
            return 'utilities_electric'
        elif 'utilities - regulated gas' in industry:
            return 'utilities_gas'
        elif 'utilities - regulated water' in industry:
            return 'utilities_water'
        elif 'utilities - renewable' in industry:
            return 'utilities_renewable'
        elif 'utilities - diversified' in industry:
            return 'utilities_diversified'
        
        # === CONSUMER CYCLICAL ===
        elif 'auto manufacturers' in industry:
            return 'auto_manufacturers'
        elif 'auto parts' in industry:
            return 'auto_parts'
        elif 'internet retail' in industry:
            return 'internet_retail'
        elif 'specialty retail' in industry:
            return 'specialty_retail'
        elif 'home improvement retail' in industry:
            return 'home_improvement_retail'
        elif 'apparel retail' in industry:
            return 'apparel_retail'
        elif 'restaurants' in industry:
            return 'restaurants'
        elif 'hotels, motels & cruise lines' in industry:
            return 'hospitality'
        elif 'residential construction' in industry:
            return 'residential_construction'
        elif 'footwear & accessories' in industry:
            return 'footwear_accessories'
        elif 'furnishings, fixtures & appliances' in industry:
            return 'home_furnishings'
        
        # === CONSUMER DEFENSIVE ===
        elif 'discount stores' in industry:
            return 'discount_stores'
        elif 'grocery stores' in industry:
            return 'grocery_stores'
        elif 'beverages - non-alcoholic' in industry:
            return 'beverages_non_alcoholic'
        elif 'beverages - alcoholic' in industry:
            return 'beverages_alcoholic'
        elif 'food processing' in industry:
            return 'food_processing'
        elif 'packaged foods' in industry:
            return 'packaged_foods'
        elif 'personal care products' in industry:
            return 'personal_care'
        elif 'household & personal products' in industry:
            return 'household_products'
        elif 'tobacco' in industry:
            return 'tobacco'
        
        # === INDUSTRIALS ===
        elif 'aerospace & defense' in industry:
            return 'aerospace_defense'
        elif 'construction & engineering' in industry:
            return 'construction_engineering'
        elif 'industrial machinery' in industry:
            return 'industrial_machinery'
        elif 'electrical equipment & parts' in industry:
            return 'electrical_equipment'
        elif 'transportation & logistics' in industry:
            return 'transportation_logistics'
        elif 'airlines' in industry:
            return 'airlines'
        elif 'railroads' in industry:
            return 'railroads'
        elif 'waste management' in industry:
            return 'waste_management'
        
        # === MATERIALS ===
        elif 'chemicals' in industry:
            return 'chemicals'
        elif 'steel' in industry:
            return 'steel'
        elif 'aluminum' in industry:
            return 'aluminum'
        elif 'copper' in industry:
            return 'copper'
        elif 'gold' in industry:
            return 'gold_mining'
        elif 'building materials' in industry:
            return 'building_materials'
        elif 'paper & paper products' in industry:
            return 'paper_products'
        
        # === COMMUNICATION SERVICES ===
        elif 'telecommunications services' in industry:
            return 'telecommunications'
        elif 'wireless telecommunications services' in industry:
            return 'wireless_telecom'
        elif 'entertainment' in industry:
            return 'entertainment'
        elif 'publishing' in industry:
            return 'publishing'
        elif 'advertising agencies' in industry:
            return 'advertising'
        
        # Fallback to sector-based detection
        elif 'technology' in sector:
            return 'technology_general'
        elif 'healthcare' in sector:
            return 'healthcare_general'
        elif 'financial' in sector:
            return 'financial_general'
        elif 'energy' in sector:
            return 'energy_general'
        elif 'utilities' in sector:
            return 'utilities_general'
        elif 'consumer' in sector:
            return 'consumer_general'
        elif 'industrial' in sector:
            return 'industrials_general'
        elif 'materials' in sector:
            return 'materials_general'
        elif 'communication' in sector:
            return 'communication_general'
        
        return 'general_corporate'
    
    @staticmethod
    def get_industry_framework(industry: str) -> Dict[str, Any]:
        """
        Get comprehensive industry-specific analysis framework
        """
        
        industry_frameworks = {
            # === REIT INDUSTRIES ===
            'reit_industrial': {
                'name': 'Industrial & Logistics REITs',
                'key_metrics': ['FFO per Share', 'AFFO per Share', 'Same-Store NOI Growth', 'Occupancy Rate', 
                               'Average Lease Term', 'Rent Spreads', 'Development Yield', 'Warehouse Utilization'],
                'valuation_methods': ['P/FFO Multiple', 'P/AFFO Multiple', 'NAV per Share', 'Dividend Discount Model'],
                'focus_areas': ['E-commerce Growth Impact', 'Supply Chain Optimization', 'Last-Mile Delivery Demand'],
                'key_drivers': ['E-commerce penetration', 'Supply chain reshoring', 'Automation adoption'],
                'research_keywords': ['industrial REIT', 'logistics', 'warehouse', 'e-commerce', 'supply chain', 'last mile'],
                'peer_comparison': ['PLD', 'EXR', 'PSA', 'CXW'],
                'cyclical_factors': ['Economic growth', 'Trade volumes', 'Inventory cycles']
            },
            
            'reit_residential': {
                'name': 'Residential REITs',
                'key_metrics': ['FFO per Share', 'Same-Store Revenue Growth', 'Occupancy Rate', 'Average Rent per Unit',
                               'Rent Growth Rate', 'Tenant Turnover', 'Revenue per Available Room (RevPAR)', 'Development Pipeline'],
                'valuation_methods': ['P/FFO Multiple', 'NAV per Share', 'Replacement Cost Analysis'],
                'focus_areas': ['Housing Demand Trends', 'Rental Market Dynamics', 'Development Pipeline Quality'],
                'key_drivers': ['Household formation', 'Home affordability', 'Migration patterns'],
                'research_keywords': ['residential REIT', 'apartments', 'rent growth', 'occupancy', 'housing demand'],
                'peer_comparison': ['AVB', 'EQR', 'MAA', 'UDR'],
                'cyclical_factors': ['Interest rates', 'Employment levels', 'Demographics']
            },
            
            'reit_specialty': {
                'name': 'Specialty REITs (Cell Towers, Data Centers)',
                'key_metrics': ['FFO per Share', 'Tenant Escalations', 'Tower Utilization', 'Power Usage Effectiveness (PUE)',
                               'Contracted Revenue %', 'Average Lease Term', 'Development Capex ROI', 'Churn Rate'],
                'valuation_methods': ['DCF with Terminal Value', 'Sum-of-Parts Valuation', 'Replacement Cost'],
                'focus_areas': ['5G Infrastructure Demand', 'Cloud Computing Growth', 'Edge Computing Trends'],
                'key_drivers': ['Mobile data growth', 'Cloud adoption', 'Digital transformation'],
                'research_keywords': ['cell towers', 'data centers', '5G', 'cloud computing', 'digital infrastructure'],
                'peer_comparison': ['AMT', 'CCI', 'EQIX', 'DLR'],
                'cyclical_factors': ['Technology cycles', 'Regulatory changes', 'Spectrum auctions']
            },
            
            # === BANKING INDUSTRIES ===
            'banks_diversified': {
                'name': 'Large Diversified Banks',
                'key_metrics': ['Net Interest Margin (NIM)', 'Return on Assets (ROA)', 'Return on Equity (ROE)', 
                               'Tier 1 Capital Ratio', 'Common Equity Tier 1 (CET1)', 'Efficiency Ratio', 'Credit Loss Rate'],
                'valuation_methods': ['Price-to-Tangible Book Value', 'Price-to-Earnings', 'Dividend Discount Model'],
                'focus_areas': ['Interest Rate Sensitivity', 'Credit Quality Trends', 'Fee Income Diversification'],
                'key_drivers': ['Interest rate environment', 'Credit cycle', 'Regulatory environment'],
                'research_keywords': ['large bank', 'NIM', 'credit quality', 'capital ratios', 'fee income'],
                'peer_comparison': ['JPM', 'BAC', 'WFC', 'C'],
                'cyclical_factors': ['Economic growth', 'Interest rates', 'Credit cycles']
            },
            
            'banks_regional': {
                'name': 'Regional Banks',
                'key_metrics': ['Net Interest Margin (NIM)', 'Loan Growth', 'Deposit Growth', 'Cost of Funds',
                               'Non-Performing Assets (NPAs)', 'Provision Expense', 'Operating Leverage', 'Tangible Book Value'],
                'valuation_methods': ['Price-to-Tangible Book Value', 'Price-to-Earnings', 'Sum-of-Parts'],
                'focus_areas': ['Local Market Share', 'Commercial Real Estate Exposure', 'Deposit Franchise Quality'],
                'key_drivers': ['Regional economic health', 'Commercial real estate', 'Interest rate sensitivity'],
                'research_keywords': ['regional bank', 'loan growth', 'deposit costs', 'CRE exposure', 'local markets'],
                'peer_comparison': ['USB', 'PNC', 'TFC', 'RF'],
                'cyclical_factors': ['Regional economic cycles', 'Real estate cycles', 'Rate environment']
            },
            
            # === TECHNOLOGY INDUSTRIES ===
            'software_application': {
                'name': 'Application Software Companies',
                'key_metrics': ['Annual Recurring Revenue (ARR)', 'Revenue Growth Rate', 'Gross Margin', 'Rule of 40',
                               'Customer Acquisition Cost (CAC)', 'Customer Lifetime Value (CLV)', 'Net Revenue Retention', 'Churn Rate'],
                'valuation_methods': ['Price-to-Sales Multiple', 'EV/Revenue', 'Discounted Cash Flow'],
                'focus_areas': ['Subscription Model Metrics', 'Customer Retention', 'Market Penetration'],
                'key_drivers': ['Digital transformation', 'Cloud adoption', 'AI integration'],
                'research_keywords': ['SaaS', 'application software', 'ARR', 'subscription model', 'cloud software'],
                'peer_comparison': ['CRM', 'ADBE', 'NOW', 'WDAY'],
                'cyclical_factors': ['Technology spending cycles', 'Enterprise budgets', 'Digital transformation pace']
            },
            
            'semiconductors': {
                'name': 'Semiconductor Industry',
                'key_metrics': ['Revenue per Wafer', 'Fab Utilization Rate', 'ASP Trends', 'R&D Intensity',
                               'Design Win Pipeline', 'Inventory Turns', 'Gross Margin', 'Process Technology Leadership'],
                'valuation_methods': ['Price-to-Sales Multiple', 'EV/EBITDA', 'Sum-of-Parts'],
                'focus_areas': ['Process Technology Advantage', 'End Market Exposure', 'Capital Intensity'],
                'key_drivers': ['AI demand', 'Automotive electrification', 'IoT growth'],
                'research_keywords': ['semiconductors', 'chips', 'AI processors', 'automotive chips', 'process technology'],
                'peer_comparison': ['NVDA', 'AMD', 'INTC', 'TSM'],
                'cyclical_factors': ['Semiconductor cycles', 'Inventory cycles', 'Technology transitions']
            },
            
            # === HEALTHCARE INDUSTRIES ===
            'pharma_large_cap': {
                'name': 'Large Pharmaceutical Companies',
                'key_metrics': ['R&D as % of Revenue', 'Pipeline Value', 'Patent Cliff Analysis', 'Regulatory Approvals',
                               'Market Share by Therapy Area', 'Pricing Power', 'Generic Competition Timeline'],
                'valuation_methods': ['Risk-Adjusted NPV', 'Sum-of-Parts Pipeline Valuation', 'P/E Multiple'],
                'focus_areas': ['Drug Pipeline Quality', 'Patent Expiry Timeline', 'Biosimilar Competition'],
                'key_drivers': ['Regulatory approvals', 'Patent expirations', 'Pricing environment'],
                'research_keywords': ['big pharma', 'drug pipeline', 'patent cliff', 'FDA approvals', 'biosimilars'],
                'peer_comparison': ['JNJ', 'PFE', 'MRK', 'ABBV'],
                'cyclical_factors': ['Drug development cycles', 'Regulatory cycles', 'Patent cycles']
            },
            
            'biotechnology': {
                'name': 'Biotechnology Companies',
                'key_metrics': ['Clinical Trial Pipeline', 'Cash Runway', 'R&D Burn Rate', 'Partnership Revenue',
                               'Milestone Payments', 'Regulatory Timeline', 'Peak Sales Estimates', 'Probability of Success'],
                'valuation_methods': ['Risk-Adjusted NPV', 'Probability-Weighted Scenarios', 'Comparable Transactions'],
                'focus_areas': ['Clinical Trial Progress', 'Regulatory Pathway', 'Commercial Potential'],
                'key_drivers': ['Clinical trial results', 'Regulatory decisions', 'Partnership deals'],
                'research_keywords': ['biotech', 'clinical trials', 'drug development', 'FDA pathway', 'partnerships'],
                'peer_comparison': ['GILD', 'BIIB', 'REGN', 'VRTX'],
                'cyclical_factors': ['Clinical development cycles', 'Regulatory approval cycles', 'Funding cycles']
            },
            
            # === ENERGY INDUSTRIES ===
            'oil_gas_integrated': {
                'name': 'Integrated Oil & Gas Companies',
                'key_metrics': ['Free Cash Flow Yield', 'Return on Capital Employed (ROCE)', 'Reserve Replacement Ratio',
                               'Production Growth', 'Refining Margins', 'Downstream Utilization', 'Breakeven Oil Price'],
                'valuation_methods': ['Sum-of-Parts Valuation', 'NAV Based on Reserves', 'EV/EBITDA'],
                'focus_areas': ['Integrated Value Chain', 'Capital Discipline', 'Energy Transition Strategy'],
                'key_drivers': ['Oil & gas prices', 'Refining margins', 'Global demand'],
                'research_keywords': ['integrated oil', 'refining margins', 'upstream', 'downstream', 'energy transition'],
                'peer_comparison': ['XOM', 'CVX', 'BP', 'SHEL'],
                'cyclical_factors': ['Commodity price cycles', 'Refining cycles', 'Global economic cycles']
            },
            
            # === CONSUMER INDUSTRIES ===
            'restaurants': {
                'name': 'Restaurant Chains',
                'key_metrics': ['Same-Store Sales Growth', 'Restaurant-Level Margins', 'Unit Growth Rate', 'Average Unit Volume (AUV)',
                               'Digital Sales %', 'Delivery/Takeout Mix', 'Labor Cost %', 'Food Cost %'],
                'valuation_methods': ['EV/EBITDA Multiple', 'P/E Multiple', 'Sum-of-Parts Store Valuation'],
                'focus_areas': ['Digital Transformation', 'Unit Economics', 'Brand Positioning'],
                'key_drivers': ['Consumer spending', 'Labor availability', 'Digital adoption'],
                'research_keywords': ['restaurant chain', 'same store sales', 'digital ordering', 'unit economics'],
                'peer_comparison': ['MCD', 'SBUX', 'QSR', 'YUM'],
                'cyclical_factors': ['Consumer confidence', 'Disposable income', 'Labor markets']
            },
            
            # === REMAINING CONSUMER INDUSTRIES ===
            'internet_retail': {
                'name': 'Internet Retail Companies',
                'key_metrics': ['GMV Growth', 'Take Rate', 'Active Customers', 'Order Frequency', 'Average Order Value',
                               'Customer Acquisition Cost', 'Fulfillment Cost per Unit', 'Prime/Membership Penetration'],
                'valuation_methods': ['EV/GMV Multiple', 'Price-to-Sales', 'Customer Lifetime Value'],
                'focus_areas': ['Market Share Expansion', 'Logistics Network', 'Technology Platform'],
                'key_drivers': ['E-commerce penetration', 'Consumer behavior', 'Last-mile delivery'],
                'research_keywords': ['e-commerce', 'online retail', 'GMV', 'marketplace', 'fulfillment'],
                'peer_comparison': ['AMZN', 'SHOP', 'MELI', 'SE'],
                'cyclical_factors': ['Consumer confidence', 'Economic growth', 'Holiday seasonality']
            },
            
            'auto_manufacturers': {
                'name': 'Automotive Manufacturers',
                'key_metrics': ['Unit Sales Volume', 'Average Selling Price', 'Market Share by Region', 'EV Mix %',
                               'R&D Spending on Electrification', 'Manufacturing Capacity Utilization', 'Dealer Inventory Days'],
                'valuation_methods': ['P/E Multiple', 'EV/Sales', 'Sum-of-Parts (ICE vs EV)'],
                'focus_areas': ['Electric Vehicle Transition', 'Autonomous Driving Technology', 'Manufacturing Efficiency'],
                'key_drivers': ['EV adoption rates', 'Battery costs', 'Regulatory emissions standards'],
                'research_keywords': ['automotive', 'electric vehicles', 'EV transition', 'autonomous driving', 'battery'],
                'peer_comparison': ['TSLA', 'F', 'GM', 'TM'],
                'cyclical_factors': ['Economic cycles', 'Consumer credit', 'Commodity prices']
            },
            
            'discount_stores': {
                'name': 'Discount Retail Chains',
                'key_metrics': ['Same-Store Sales Growth', 'Inventory Turnover', 'Gross Margin %', 'Operating Margin %',
                               'Store Productivity per Sq Ft', 'E-commerce Penetration', 'Private Label %'],
                'valuation_methods': ['P/E Multiple', 'EV/EBITDA', 'Price-per-Square-Foot'],
                'focus_areas': ['Supply Chain Efficiency', 'Price Competitiveness', 'Store Format Innovation'],
                'key_drivers': ['Consumer price sensitivity', 'Supply chain optimization', 'Store expansion'],
                'research_keywords': ['discount retail', 'same store sales', 'inventory turnover', 'supply chain'],
                'peer_comparison': ['WMT', 'TGT', 'COST', 'DG'],
                'cyclical_factors': ['Consumer spending', 'Employment levels', 'Inflation impact']
            },
            
            # === INDUSTRIALS INDUSTRIES ===
            'aerospace_defense': {
                'name': 'Aerospace & Defense',
                'key_metrics': ['Order Backlog', 'Book-to-Bill Ratio', 'Defense vs Commercial Mix', 'Program Margins',
                               'Free Cash Flow Conversion', 'R&D Intensity', 'International Sales %'],
                'valuation_methods': ['P/E Multiple', 'EV/EBITDA', 'Sum-of-Parts by Program'],
                'focus_areas': ['Defense Budget Trends', 'Commercial Aviation Recovery', 'International Expansion'],
                'key_drivers': ['Defense spending', 'Air travel demand', 'Geopolitical tensions'],
                'research_keywords': ['aerospace', 'defense', 'military contracts', 'commercial aviation', 'backlog'],
                'peer_comparison': ['BA', 'LMT', 'RTX', 'GD'],
                'cyclical_factors': ['Defense budget cycles', 'Aviation cycles', 'Geopolitical cycles']
            },
            
            'railroads': {
                'name': 'Railroad Transportation',
                'key_metrics': ['Revenue per Car', 'Operating Ratio', 'Fuel Efficiency', 'Network Velocity',
                               'Intermodal Volume', 'Pricing Power', 'Capital Intensity', 'Free Cash Flow Yield'],
                'valuation_methods': ['EV/EBITDA Multiple', 'Price-to-Cash Flow', 'Replacement Value'],
                'focus_areas': ['Operational Efficiency', 'Pricing Power', 'Network Effects'],
                'key_drivers': ['Industrial production', 'Coal demand', 'Intermodal competition'],
                'research_keywords': ['railroad', 'freight', 'operating ratio', 'intermodal', 'fuel efficiency'],
                'peer_comparison': ['UNP', 'CSX', 'NSC', 'CP'],
                'cyclical_factors': ['Economic growth', 'Industrial cycles', 'Energy demand']
            },
            
            # === MATERIALS INDUSTRIES ===
            'chemicals': {
                'name': 'Chemical Companies',
                'key_metrics': ['Volume Growth', 'Price Realization', 'Capacity Utilization', 'Margin per Ton',
                               'Feedstock Costs', 'Downstream Integration %', 'Environmental Compliance Costs'],
                'valuation_methods': ['EV/EBITDA Multiple', 'Replacement Cost Analysis', 'Through-Cycle Valuation'],
                'focus_areas': ['Cost Curve Position', 'Product Mix Optimization', 'Sustainability Innovation'],
                'key_drivers': ['Industrial demand', 'Feedstock availability', 'Environmental regulations'],
                'research_keywords': ['chemicals', 'petrochemicals', 'specialty chemicals', 'feedstock', 'capacity'],
                'peer_comparison': ['DD', 'DOW', 'LYB', 'PPG'],
                'cyclical_factors': ['Chemical cycles', 'Oil price cycles', 'Industrial demand cycles']
            },
            
            # === COMMUNICATION SERVICES ===
            'telecommunications': {
                'name': 'Telecommunications Services',
                'key_metrics': ['ARPU (Average Revenue Per User)', 'Churn Rate', 'Network Coverage %', 'Spectrum Holdings',
                               'Capex as % Revenue', 'EBITDA Margin', 'Free Cash Flow After Capex', 'Fiber Penetration'],
                'valuation_methods': ['EV/EBITDA Multiple', 'Sum-of-Parts', 'Discounted Cash Flow'],
                'focus_areas': ['5G Network Deployment', 'Fiber Infrastructure', 'Competitive Positioning'],
                'key_drivers': ['5G adoption', 'Data usage growth', 'Regulatory environment'],
                'research_keywords': ['telecom', '5G', 'ARPU', 'fiber', 'wireless spectrum', 'network'],
                'peer_comparison': ['VZ', 'T', 'TMUS', 'CHTR'],
                'cyclical_factors': ['Technology upgrade cycles', 'Regulatory cycles', 'Competition intensity']
            },
            
            'entertainment': {
                'name': 'Entertainment & Media',
                'key_metrics': ['Subscriber Growth', 'ARPU', 'Content Spending', 'Subscriber Churn', 'Engagement Metrics',
                               'International Expansion', 'Ad Revenue per User', 'Content Amortization'],
                'valuation_methods': ['EV/Subscriber', 'P/E Multiple', 'Sum-of-Parts Content Library'],
                'focus_areas': ['Content Quality & Exclusivity', 'Global Expansion', 'Technology Platform'],
                'key_drivers': ['Streaming adoption', 'Content costs', 'Global expansion'],
                'research_keywords': ['streaming', 'entertainment', 'content', 'subscribers', 'media'],
                'peer_comparison': ['DIS', 'NFLX', 'WBD', 'PARA'],
                'cyclical_factors': ['Consumer discretionary spending', 'Content cycle', 'Technology disruption']
            },
            
            # === ADDITIONAL HEALTHCARE ===
            'medical_devices': {
                'name': 'Medical Device Companies',
                'key_metrics': ['Revenue Growth by Segment', 'R&D as % Revenue', 'Gross Margin by Product',
                               'Regulatory Approval Timeline', 'Hospital Capital Spending', 'International Revenue %'],
                'valuation_methods': ['P/E Multiple', 'EV/Sales', 'Sum-of-Parts by Division'],
                'focus_areas': ['Innovation Pipeline', 'Regulatory Environment', 'Hospital Spending Trends'],
                'key_drivers': ['Aging population', 'Healthcare spending', 'Regulatory approvals'],
                'research_keywords': ['medical devices', 'healthcare equipment', 'FDA approval', 'hospital spending'],
                'peer_comparison': ['ABT', 'JNJ', 'MDT', 'ISRG'],
                'cyclical_factors': ['Healthcare spending cycles', 'Regulatory approval cycles', 'Innovation cycles']
            },
            
            # === ADDITIONAL ENERGY ===
            'oil_gas_midstream': {
                'name': 'Oil & Gas Midstream/Pipeline',
                'key_metrics': ['Pipeline Utilization', 'Fee-Based Revenue %', 'Contract Coverage Ratio', 'EBITDA Multiple',
                               'Distribution Coverage Ratio', 'Growth Capex', 'DCF per Unit', 'Leverage Ratio'],
                'valuation_methods': ['EV/EBITDA Multiple', 'Dividend Discount Model', 'DCF Yield'],
                'focus_areas': ['Fee-Based Business Model', 'Pipeline Network', 'Distribution Sustainability'],
                'key_drivers': ['Energy production growth', 'Infrastructure investment', 'Regulatory environment'],
                'research_keywords': ['midstream', 'pipelines', 'MLP', 'fee-based', 'distribution coverage'],
                'peer_comparison': ['KMI', 'OKE', 'WMB', 'ENB'],
                'cyclical_factors': ['Energy production cycles', 'Infrastructure investment cycles', 'Regulatory cycles']
            },
            
            # === ADDITIONAL TECHNOLOGY ===
            'consumer_electronics': {
                'name': 'Consumer Electronics',
                'key_metrics': ['Unit Sales Growth', 'Average Selling Price', 'Gross Margin by Product', 'R&D Intensity',
                               'Market Share by Region', 'Services Revenue %', 'Ecosystem Metrics', 'Innovation Pipeline'],
                'valuation_methods': ['P/E Multiple', 'EV/Sales', 'Sum-of-Parts (Hardware vs Services)'],
                'focus_areas': ['Product Innovation Cycle', 'Services Ecosystem', 'Supply Chain Management'],
                'key_drivers': ['Consumer upgrade cycles', 'Innovation pace', 'Supply chain efficiency'],
                'research_keywords': ['consumer electronics', 'smartphones', 'innovation', 'ecosystem', 'services'],
                'peer_comparison': ['AAPL', 'SONY', 'QCOM', 'HPQ'],
                'cyclical_factors': ['Product refresh cycles', 'Consumer spending cycles', 'Technology cycles']
            },
            
            # Default fallback
            'general_corporate': {
                'name': 'General Corporate Analysis',
                'key_metrics': ['Revenue Growth', 'EBITDA Margin', 'Free Cash Flow', 'Return on Invested Capital (ROIC)',
                               'Debt-to-Equity', 'Working Capital Efficiency', 'Market Share'],
                'valuation_methods': ['P/E Multiple', 'EV/EBITDA Multiple', 'Discounted Cash Flow'],
                'focus_areas': ['Business Model Quality', 'Competitive Position', 'Financial Health'],
                'key_drivers': ['Industry growth', 'Market share', 'Operational efficiency'],
                'research_keywords': ['financial performance', 'competitive analysis', 'business model'],
                'peer_comparison': [],
                'cyclical_factors': ['Economic cycles', 'Industry cycles']
            }
        }
        
        return industry_frameworks.get(industry, industry_frameworks['general_corporate'])

class ComprehensiveIndustryPrompts:
    """
    Industry-specific prompt enhancement system
    """
    
    @staticmethod
    def get_industry_enhanced_prompt(analyst_type: str, company: str, ticker: str,
                                   financial_data: dict = None, user_query: str = "") -> str:
        """
        Generate comprehensive industry-enhanced prompt
        """
        # Detect specific industry
        industry = ComprehensiveIndustryDetector.detect_industry(financial_data or {})
        industry_framework = ComprehensiveIndustryDetector.get_industry_framework(industry)
        
        # Get base prompt
        from .institutional_analyst_prompts import InstitutionalAnalystPrompts
        base_prompt_method = getattr(InstitutionalAnalystPrompts, f'get_{analyst_type}_prompt', None)
        
        if not base_prompt_method:
            base_prompt_method = InstitutionalAnalystPrompts.get_fundamentals_prompt
        
        base_prompt = base_prompt_method(company, ticker, user_query, financial_data)
        
        # Create industry-specific enhancement
        industry_enhancement = ComprehensiveIndustryPrompts._create_industry_enhancement(
            analyst_type, industry, industry_framework, company, ticker
        )
        
        # Integrate enhancement
        enhanced_prompt = ComprehensiveIndustryPrompts._integrate_enhancement(
            base_prompt, industry_enhancement, analyst_type, industry
        )
        
        return enhanced_prompt
    
    @staticmethod
    def _create_industry_enhancement(analyst_type: str, industry: str, framework: Dict[str, Any],
                                   company: str, ticker: str) -> str:
        """
        Create detailed industry-specific enhancement
        """
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        enhancement = f"""
# COMPREHENSIVE INDUSTRY-SPECIFIC ANALYSIS FRAMEWORK
**INDUSTRY CLASSIFICATION**: {framework['name']} ({industry.upper()})
**ANALYSIS DATE**: {current_date}

## Industry-Specific Analytical Excellence
**CRITICAL {industry.upper()} METRICS** (Institutional Priority):
{chr(10).join([f"- **{metric}**: Industry-standard performance indicator for {framework['name']}" for metric in framework['key_metrics']])}

**{industry.upper()}-SPECIFIC VALUATION METHODOLOGIES**:
{chr(10).join([f"- **{method}**: Primary valuation approach for {framework['name']} sector" for method in framework['valuation_methods']])}

**INDUSTRY FOCUS AREAS FOR {analyst_type.upper()} ANALYSIS**:
{chr(10).join([f"- **{area}**: {analyst_type.title()} perspective on {framework['name']}" for area in framework['focus_areas']])}

## Key Industry Drivers & Dynamics
**PRIMARY VALUE DRIVERS**:
{chr(10).join([f"- **{driver}**: Impact on {company} performance and valuation" for driver in framework['key_drivers']])}

**CYCLICAL FACTORS**:
{chr(10).join([f"- **{factor}**: Timing and impact analysis for {framework['name']}" for factor in framework['cyclical_factors']])}

## Enhanced Competitive Intelligence
**PEER COMPARISON GROUP**: {', '.join(framework['peer_comparison']) if framework['peer_comparison'] else 'Industry-specific peer analysis'}

**TARGETED RESEARCH INTEGRATION**:
Primary Keywords: {' | '.join(framework['research_keywords'])}

**MANDATORY RESEARCH FOCUS**:
1. **{framework['name']} Industry Analysis**: Market dynamics, regulatory environment, growth trends
2. **{company} Competitive Positioning**: Market share, differentiation, strategic advantages within {framework['name']}
3. **Industry-Specific Catalysts**: {framework['name']}-relevant developments, regulatory changes, market shifts
4. **Operational Benchmarking**: {framework['key_metrics'][0]} and {framework['key_metrics'][1]} vs. industry standards

## Industry-Optimized Financial Analysis
**ANALYTICAL PRIORITIES**:
1. **Primary Performance Metric**: {framework['key_metrics'][0]} - core industry performance indicator
2. **Valuation Method**: {framework['valuation_methods'][0]} - most relevant for {framework['name']}
3. **Key Focus Area**: {framework['focus_areas'][0]} - critical success factor
4. **Primary Driver**: {framework['key_drivers'][0]} - main value creation catalyst

**INDUSTRY-SPECIFIC INTERPRETATION**:
- Standard financial ratios may be less relevant for {framework['name']} analysis
- Prioritize {framework['key_metrics'][0]}, {framework['key_metrics'][1]}, and {framework['key_metrics'][2]}
- Consider {framework['name']} industry cycles: {framework['cyclical_factors'][0]}
- Benchmark against {framework['name']} industry standards and peer performance
"""
        
        return enhancement
    
    @staticmethod
    def _integrate_enhancement(base_prompt: str, enhancement: str, analyst_type: str, industry: str) -> str:
        """
        Integrate industry enhancement into base prompt
        """
        if "# User Request" in base_prompt:
            parts = base_prompt.split("# User Request")
            enhanced_prompt = parts[0] + enhancement + "\n\n# User Request" + parts[1]
        elif "# COMPLETE UNFILTERED YFINANCE DATASET" in base_prompt:
            parts = base_prompt.split("# COMPLETE UNFILTERED YFINANCE DATASET")
            enhanced_prompt = parts[0] + enhancement + "\n\n# COMPLETE UNFILTERED YFINANCE DATASET" + parts[1]
        else:
            enhanced_prompt = base_prompt + "\n\n" + enhancement
        
        # Add final instruction
        final_instruction = f"""

## COMPREHENSIVE INDUSTRY MANDATE
Provide sophisticated {analyst_type} analysis with deep {ComprehensiveIndustryDetector.get_industry_framework(industry)['name']} industry expertise. Demonstrate mastery of industry-specific metrics, valuation methodologies, competitive dynamics, and market conditions. Your analysis must reflect institutional-grade understanding of {industry.upper()} industry fundamentals."""
        
        enhanced_prompt += final_instruction
        return enhanced_prompt

# Main integration function
def get_comprehensive_industry_prompt(analyst_type: str, company: str, ticker: str,
                                    financial_data: dict = None, user_query: str = "") -> str:
    """
    Get comprehensive industry-enhanced prompt for any analyst type
    """
    return ComprehensiveIndustryPrompts.get_industry_enhanced_prompt(
        analyst_type, company, ticker, financial_data, user_query
    )