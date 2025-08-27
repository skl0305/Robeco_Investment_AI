"""
Enhanced Comprehensive yfinance data fetcher

Maximizes yfinance data extraction with comprehensive financial statements, analyst coverage,
ESG metrics, ownership structure, earnings data, performance metrics, and smart ratios.
Integrated with hedge fund-grade AI analytical framework.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import yfinance as yf
import pandas as pd
import numpy as np

from ..core.models import FinancialData
from ..core.utils import retry_async, time_execution, calculate_quality_score

logger = logging.getLogger(__name__)


class YFinanceFetcher:
    """Comprehensive yfinance data fetcher with caching and error handling"""
    
    def __init__(self, cache_duration: int = 300):
        self.cache_duration = cache_duration
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_timestamps: Dict[str, datetime] = {}
        
    @time_execution
    @retry_async(max_retries=3, delay=1.0)
    async def fetch_comprehensive_data(self, ticker: str) -> Dict[str, Any]:
        """
        Fetch ALL available yfinance data for a ticker
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary containing all available financial data
        """
        # Check cache first
        cached_data = self._get_from_cache(ticker)
        if cached_data:
            logger.info(f"Using cached data for {ticker}")
            return cached_data
        
        logger.info(f"Fetching comprehensive data for {ticker}")
        
        # Initialize result structure
        result = {
            "ticker": ticker,
            "fetch_timestamp": datetime.now().isoformat(),
            "data_sources": [],
            "fetch_errors": []
        }
        
        # Create ticker object
        ticker_obj = yf.Ticker(ticker)
        
        # Fetch MAXIMUM data sources in parallel for hedge fund analysis
        fetch_tasks = [
            self._fetch_comprehensive_company_info(ticker_obj, result),
            self._fetch_comprehensive_financial_statements(ticker_obj, result),
            self._fetch_comprehensive_market_data(ticker_obj, result),
            self._fetch_comprehensive_ownership_data(ticker_obj, result),
            self._fetch_comprehensive_analyst_coverage(ticker_obj, result),
            self._fetch_comprehensive_earnings_data(ticker_obj, result),
            self._fetch_comprehensive_performance_metrics(ticker_obj, result),
            self._fetch_comprehensive_esg_sustainability(ticker_obj, result),
            self._fetch_comprehensive_dividend_info(ticker_obj, result),
            self._fetch_comprehensive_recent_news(ticker_obj, result),
            self._fetch_options_data(ticker_obj, result),
            self._fetch_calendar_data(ticker_obj, result),
        ]
        
        # Execute all fetches concurrently
        await asyncio.gather(*fetch_tasks, return_exceptions=True)
        
        # Calculate smart ratios with time-synchronized data for hedge fund analysis
        logger.info("   🧮 Calculating comprehensive smart ratios for AI agents...")
        try:
            smart_ratios = self._calculate_comprehensive_smart_ratios(result)
            result["smart_ratios"] = smart_ratios
            result["data_sources"].append("smart_ratios")
        except Exception as ratio_error:
            logger.warning(f"   ⚠️ Smart ratios calculation failed: {ratio_error}")
            result["smart_ratios"] = {'error': str(ratio_error)}
        
        # Generate AI-ready financial summary for maximum hedge fund analysis
        logger.info("   📊 Generating AI-ready financial summary...")
        try:
            ai_summary = self._generate_ai_financial_summary(result)
            result["ai_financial_summary"] = ai_summary
            result["data_sources"].append("ai_summary")
        except Exception as summary_error:
            logger.warning(f"   ⚠️ AI summary generation failed: {summary_error}")
            result["ai_financial_summary"] = {'error': str(summary_error)}
        
        # Calculate data quality score
        result["data_quality_score"] = calculate_quality_score(result)
        
        # Cache the result
        self._store_in_cache(ticker, result)
        
        logger.info(f"✅ Maximum yfinance data extraction completed for {ticker} - Ready for hedge fund AI analysis")
        return result
    
    async def _fetch_comprehensive_company_info(self, ticker_obj: yf.Ticker, result: Dict[str, Any]):
        """Fetch comprehensive company information and valuation metrics"""
        try:
            # Get comprehensive company info
            info = await asyncio.to_thread(lambda: ticker_obj.info)
            result["info"] = info
            result["data_sources"].append("info")
            
            # Clean and structure company information
            company_info = {
                'name': info.get('longName') or info.get('shortName') or 'Unknown',
                'sector': info.get('sector') or 'Unknown',
                'industry': info.get('industry') or 'Unknown',
                'country': info.get('country') or 'Unknown',
                'currency': info.get('currency') or 'USD',
                'market_cap': self._safe_number(info.get('marketCap')),
                'market_cap_display': self._format_market_cap(info.get('marketCap')),
                'employees': self._safe_number(info.get('fullTimeEmployees')),
                'website': info.get('website'),
                'business_summary': info.get('longBusinessSummary'),
                'fetched_at': datetime.now().isoformat(),
                'data_source': 'yfinance_info'
            }
            
            # Comprehensive valuation metrics
            valuation_metrics = {
                'pe_ratio': self._safe_number(info.get('trailingPE')),
                'forward_pe': self._safe_number(info.get('forwardPE')),
                'price_to_book': self._safe_number(info.get('priceToBook')),
                'price_to_sales': self._safe_number(info.get('priceToSalesTrailing12Months')),
                'ev_to_ebitda': self._safe_number(info.get('enterpriseToEbitda')),
                'peg_ratio': self._safe_number(info.get('pegRatio')),
                'market_cap': self._safe_number(info.get('marketCap')),
                'enterprise_value': self._safe_number(info.get('enterpriseValue')),
                'book_value': self._safe_number(info.get('bookValue')),
                'price_to_cash_flow': self._safe_number(info.get('priceToCashflow')),
                'fetched_at': datetime.now().isoformat(),
                'data_source': 'yfinance_info'
            }
            
            # Extract comprehensive key metrics for easy access
            result["key_metrics"] = {
                "market_cap": self._safe_number(info.get('marketCap')),
                "enterprise_value": self._safe_number(info.get('enterpriseValue')),
                "pe_ratio": self._safe_number(info.get('trailingPE')),
                "pb_ratio": self._safe_number(info.get('priceToBook')),
                "ps_ratio": self._safe_number(info.get('priceToSalesTrailing12Months')),
                "ev_ebitda": self._safe_number(info.get('enterpriseToEbitda')),
                "roe": self._safe_number(info.get('returnOnEquity')),
                "roa": self._safe_number(info.get('returnOnAssets')),
                "roic": self._safe_number(info.get('returnOnCapital')),
                "debt_equity": self._safe_number(info.get('debtToEquity')),
                "current_ratio": self._safe_number(info.get('currentRatio')),
                "dividend_yield": self._safe_number(info.get('dividendYield')),
                "revenue_growth": self._safe_number(info.get('revenueGrowth')),
                "earnings_growth": self._safe_number(info.get('earningsGrowth')),
                "free_cashflow": self._safe_number(info.get('freeCashflow')),
                "working_capital": self._safe_number(info.get('totalCash', 0) - info.get('totalDebt', 0)),
                "interest_coverage": None,  # Would need calculation from financial statements
                "asset_turnover": None,    # Would need calculation from financial statements
                "fcf_yield": None          # Would need calculation
            }
            
            # Store structured data
            result["company_info"] = company_info
            result["valuation_metrics"] = valuation_metrics
            
        except Exception as e:
            logger.error(f"Error fetching comprehensive company info: {e}")
            result["fetch_errors"].append(f"company_info: {str(e)}")
    
    def _format_market_cap(self, market_cap) -> str:
        """Format market cap for display (e.g., $3.2T, $450B)"""
        if not market_cap or pd.isna(market_cap):
            return 'N/A'
        
        try:
            value = float(market_cap)
            
            if value >= 1e12:
                return f"${value/1e12:.1f}T"
            elif value >= 1e9:
                return f"${value/1e9:.1f}B"
            elif value >= 1e6:
                return f"${value/1e6:.1f}M"
            else:
                return f"${value:,.0f}"
                
        except (ValueError, TypeError):
            return 'N/A'
    
    async def _fetch_comprehensive_financial_statements(self, ticker_obj: yf.Ticker, result: Dict[str, Any]):
        """Fetch comprehensive 3+ years of financial statements for hedge fund analysis"""
        try:
            statements_data = {}
            financial_statements = ['financials', 'balance_sheet', 'cashflow']
            
            for statement_type in financial_statements:
                try:
                    logger.info(f"   Fetching {statement_type}...")
                    
                    data = None
                    # Get the data with retry logic
                    for attempt in range(3):
                        try:
                            if statement_type == 'financials':
                                data = await asyncio.to_thread(lambda: ticker_obj.financials)
                            elif statement_type == 'balance_sheet':
                                data = await asyncio.to_thread(lambda: ticker_obj.balance_sheet)
                            elif statement_type == 'cashflow':
                                data = await asyncio.to_thread(lambda: ticker_obj.cashflow)
                            
                            # Check if data is valid DataFrame
                            if data is not None and isinstance(data, pd.DataFrame) and not data.empty:
                                break
                        except Exception as fetch_error:
                            logger.warning(f"   Attempt {attempt + 1} failed for {statement_type}: {fetch_error}")
                            if attempt < 2:
                                await asyncio.sleep(0.5)
                            else:
                                data = None
                    
                    if data is None:
                        statements_data[statement_type] = {
                            'error': f'Failed to fetch {statement_type} after retries',
                            'years_available': 0,
                            'has_data': False
                        }
                        continue
                    
                    # Convert data safely with comprehensive date handling
                    try:
                        if isinstance(data, pd.DataFrame) and not data.empty:
                            # Process column dates first to ensure consistency
                            column_mapping = {}
                            for col in data.columns:
                                if hasattr(col, 'strftime'):
                                    date_str = col.strftime('%Y-%m-%d')
                                else:
                                    date_str = str(col)
                                column_mapping[col] = date_str
                            
                            # Convert data using consistent column mapping
                            raw_dict = data.to_dict()
                            converted_dict = {}
                            for col_key, col_data in raw_dict.items():
                                date_str = column_mapping[col_key]
                                # Clean financial values
                                cleaned_data = {}
                                for metric, value in col_data.items():
                                    cleaned_data[metric] = self._safe_number(value)
                                converted_dict[date_str] = cleaned_data
                            
                            statements_data[statement_type] = {
                                'data': converted_dict,
                                'years_available': len(data.columns),
                                'has_data': len(converted_dict) > 0,
                                'fetched_at': datetime.now().isoformat(),
                                'data_source': f'yfinance_{statement_type}'
                            }
                        else:
                            statements_data[statement_type] = {
                                'data': {},
                                'years_available': 0,
                                'has_data': False,
                                'note': 'No data available'
                            }
                    except Exception as convert_error:
                        logger.error(f"   Error converting {statement_type} data: {convert_error}")
                        statements_data[statement_type] = {
                            'error': f'Data conversion failed: {str(convert_error)}',
                            'years_available': 0,
                            'has_data': False
                        }
                        
                except Exception as e:
                    logger.error(f"Error fetching {statement_type}: {e}")
                    statements_data[statement_type] = {
                        'error': str(e),
                        'years_available': 0,
                        'has_data': False
                    }
            
            result["financial_statements"] = statements_data
            result["data_sources"].extend(["financials", "balance_sheet", "cashflow"])
            
        except Exception as e:
            logger.error(f"Error fetching comprehensive financial statements: {e}")
            result["fetch_errors"].append(f"financial_statements: {str(e)}")
    
    def _safe_number(self, value) -> Optional[float]:
        """Safely convert value to number, handling None and NaN"""
        if value is None:
            return None
        
        # Check for pandas NaN
        try:
            if pd.isna(value):
                return None
        except (TypeError, ValueError):
            pass
        
        # Handle numpy types
        if hasattr(value, 'item'):
            try:
                value = value.item()
            except (ValueError, TypeError):
                pass
        
        try:
            # Convert to float and check if it's valid
            import numpy as np
            result = float(value)
            if np.isnan(result) or np.isinf(result):
                return None
            return result
        except (ValueError, TypeError, OverflowError):
            return None
    
    async def _fetch_comprehensive_market_data(self, ticker_obj: yf.Ticker, result: Dict[str, Any]):
        """Fetch comprehensive 5 years of monthly price data for hedge fund analysis"""
        try:
            logger.info("   Fetching 5 years of monthly price data...")
            
            # Calculate date range for 5 years
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5*365)  # 5 years
            
            hist_data = None
            # Try different approaches to get historical data
            for attempt in range(3):
                try:
                    # Try period-based first (more reliable)
                    if attempt == 0:
                        hist_data = await asyncio.to_thread(
                            lambda: ticker_obj.history(period="5y", interval="1mo")
                        )
                    # Try date range
                    elif attempt == 1:
                        hist_data = await asyncio.to_thread(
                            lambda: ticker_obj.history(start=start_date, end=end_date, interval="1mo")
                        )
                    # Try shorter period as fallback
                    else:
                        hist_data = await asyncio.to_thread(
                            lambda: ticker_obj.history(period="3y", interval="1mo")
                        )
                    
                    if hist_data is not None and not hist_data.empty:
                        break
                        
                except Exception as fetch_error:
                    logger.warning(f"   Price data attempt {attempt + 1} failed: {fetch_error}")
                    if attempt < 2:
                        await asyncio.sleep(0.5)
            
            if hist_data is None or hist_data.empty:
                monthly_prices = {
                    'error': 'Failed to fetch price data after all attempts',
                    'price_history': [],
                    'total_months': 0,
                    'has_data': False,
                    'fetched_at': datetime.now().isoformat()
                }
            else:
                # Convert data safely
                try:
                    # Process dates first to avoid duplicates
                    date_mapping = {}
                    for date_key in hist_data.index:
                        if hasattr(date_key, 'strftime'):
                            date_str = date_key.strftime('%Y-%m-%d')
                        else:
                            date_str = str(date_key)
                        date_mapping[date_key] = date_str
                    
                    # Process price data into clean format
                    processed_prices = []
                    
                    if 'Close' in hist_data.columns:
                        for date_key in hist_data.index:
                            date_str = date_mapping[date_key]
                            price_entry = {
                                'date': date_str,
                                'close': round(self._safe_number(hist_data.loc[date_key, 'Close']) or 0, 2),
                                'high': round(self._safe_number(hist_data.loc[date_key, 'High']) or 0, 2),
                                'low': round(self._safe_number(hist_data.loc[date_key, 'Low']) or 0, 2),
                                'volume': self._safe_number(hist_data.loc[date_key, 'Volume']) or 0
                            }
                            processed_prices.append(price_entry)
                    
                    # Sort by date chronologically
                    processed_prices.sort(key=lambda x: x['date'])
                    
                    actual_start = hist_data.index.min().strftime('%Y-%m-%d') if len(hist_data) > 0 else start_date.strftime('%Y-%m-%d')
                    actual_end = hist_data.index.max().strftime('%Y-%m-%d') if len(hist_data) > 0 else end_date.strftime('%Y-%m-%d')
                    
                    monthly_prices = {
                        'price_history': processed_prices,
                        'total_months': len(hist_data),
                        'date_range': {
                            'requested_start': start_date.strftime('%Y-%m-%d'),
                            'requested_end': end_date.strftime('%Y-%m-%d'),
                            'actual_start': actual_start,
                            'actual_end': actual_end
                        },
                        'has_data': len(processed_prices) > 0,
                        'fetched_at': datetime.now().isoformat(),
                        'data_source': 'yfinance_history_monthly'
                    }
                    
                except Exception as convert_error:
                    logger.error(f"   Error converting price data: {convert_error}")
                    monthly_prices = {
                        'error': f'Price data conversion failed: {str(convert_error)}',
                        'price_history': [],
                        'total_months': 0,
                        'has_data': False,
                        'fetched_at': datetime.now().isoformat()
                    }
            
            result["monthly_prices"] = monthly_prices
            result["data_sources"].append("monthly_prices_5y")
            
        except Exception as e:
            logger.error(f"Error fetching comprehensive market data: {e}")
            result["fetch_errors"].append(f"market_data: {str(e)}")
    
    async def _fetch_comprehensive_ownership_data(self, ticker_obj: yf.Ticker, result: Dict[str, Any]):
        """Fetch ownership and holdings data"""
        try:
            ownership_data = {}
            
            # Institutional holdings
            try:
                institutional_holders = await asyncio.to_thread(lambda: ticker_obj.institutional_holders)
                ownership_data["institutional_holders"] = institutional_holders.to_dict('records') if not institutional_holders.empty else []
            except Exception:
                pass
            
            # Major holders
            try:
                major_holders = await asyncio.to_thread(lambda: ticker_obj.major_holders)
                ownership_data["major_holders"] = major_holders.to_dict('records') if not major_holders.empty else []
            except Exception:
                pass
            
            # Mutual fund holders
            try:
                mutualfund_holders = await asyncio.to_thread(lambda: ticker_obj.mutualfund_holders)
                ownership_data["mutualfund_holders"] = mutualfund_holders.to_dict('records') if not mutualfund_holders.empty else []
            except Exception:
                pass
            
            # Insider transactions
            try:
                insider_purchases = await asyncio.to_thread(lambda: ticker_obj.insider_purchases)
                insider_roster = await asyncio.to_thread(lambda: ticker_obj.insider_roster_holders)
                insider_transactions = await asyncio.to_thread(lambda: ticker_obj.insider_transactions)
                
                ownership_data["insider_data"] = {
                    "purchases": insider_purchases.to_dict('records') if not insider_purchases.empty else [],
                    "roster": insider_roster.to_dict('records') if not insider_roster.empty else [],
                    "transactions": insider_transactions.to_dict('records') if not insider_transactions.empty else []
                }
            except Exception:
                pass
            
            result["ownership_data"] = ownership_data
            result["data_sources"].extend(["institutional_holders", "major_holders", "insider_data"])
            
        except Exception as e:
            logger.error(f"Error fetching ownership data: {e}")
            result["fetch_errors"].append(f"ownership_data: {str(e)}")
    
    async def _fetch_options_data(self, ticker_obj: yf.Ticker, result: Dict[str, Any]):
        """Fetch options chain data"""
        try:
            options_data = {}
            
            # Get options expiration dates
            options_dates = await asyncio.to_thread(lambda: ticker_obj.options)
            
            if options_dates:
                options_data["expiration_dates"] = list(options_dates)
                options_data["chains"] = {}
                
                # Get options chains for first few expiration dates
                for i, exp_date in enumerate(options_dates[:5]):  # Limit to 5 to avoid too much data
                    try:
                        option_chain = await asyncio.to_thread(
                            lambda date=exp_date: ticker_obj.option_chain(date)
                        )
                        
                        options_data["chains"][exp_date] = {
                            "calls": option_chain.calls.to_dict('records') if not option_chain.calls.empty else [],
                            "puts": option_chain.puts.to_dict('records') if not option_chain.puts.empty else []
                        }
                    except Exception as chain_error:
                        logger.warning(f"Error fetching options chain for {exp_date}: {chain_error}")
            
            result["options_data"] = options_data
            result["data_sources"].append("options")
            
        except Exception as e:
            logger.error(f"Error fetching options data: {e}")
            result["fetch_errors"].append(f"options_data: {str(e)}")
    
    async def _fetch_comprehensive_analyst_coverage(self, ticker_obj: yf.Ticker, result: Dict[str, Any]):
        """Fetch comprehensive analyst recommendations and price targets"""
        try:
            # Initialize with consistent empty structure
            analyst_data = {
                'recommendations_summary': {
                    'strong_buy': 0,
                    'buy': 0,
                    'hold': 0,
                    'sell': 0,
                    'strong_sell': 0,
                    'total_analysts': 0
                },
                'price_targets': {
                    'current': None,
                    'high': None,
                    'low': None,
                    'mean': None,
                    'upside_percent': None
                },
                'consensus': {
                    'rating': 'No Coverage',
                    'recommendation': 'No recommendations data available'
                },
                'recent_actions': [],
                'has_coverage': False,
                'data_availability': 'No analyst data available',
                'fetched_at': datetime.now().isoformat(),
                'data_source': 'yfinance_analyst'
            }
            
            # Try to fetch recommendations with multiple attempts
            recommendations = None
            for attempt in range(3):
                try:
                    recommendations = await asyncio.to_thread(lambda: ticker_obj.recommendations)
                    if recommendations is not None:
                        break
                except Exception as rec_error:
                    logger.warning(f"   Recommendation attempt {attempt + 1} failed: {rec_error}")
                    if attempt < 2:
                        await asyncio.sleep(0.5)
            
            # Process recommendations if available
            if recommendations is not None and not recommendations.empty:
                try:
                    logger.info(f"   Found {len(recommendations)} historical recommendation periods")
                    
                    # Store ALL historical recommendations
                    analyst_data['historical_recommendations'] = {}
                    
                    # Process each historical period
                    for idx, (date, recs) in enumerate(recommendations.iterrows()):
                        period_key = date.strftime('%Y-%m') if hasattr(date, 'strftime') else f"period_{idx}"
                        analyst_data['historical_recommendations'][period_key] = {
                            'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
                            'strongBuy': int(recs.get('strongBuy', 0)),
                            'buy': int(recs.get('buy', 0)),
                            'hold': int(recs.get('hold', 0)),
                            'sell': int(recs.get('sell', 0)),
                            'strongSell': int(recs.get('strongSell', 0))
                        }
                    
                    # Get latest for summary
                    latest_recs = recommendations.tail(1).iloc[0] if len(recommendations) > 0 else None
                    if latest_recs is not None:
                        # Extract recommendation counts
                        strong_buy = int(latest_recs.get('strongBuy', 0))
                        buy = int(latest_recs.get('buy', 0))
                        hold = int(latest_recs.get('hold', 0))
                        sell = int(latest_recs.get('sell', 0))
                        strong_sell = int(latest_recs.get('strongSell', 0))
                        
                        total_analysts = strong_buy + buy + hold + sell + strong_sell
                        
                        analyst_data['recommendations_summary'] = {
                            'strong_buy': strong_buy,
                            'buy': buy,
                            'hold': hold,
                            'sell': sell,
                            'strong_sell': strong_sell,
                            'total_analysts': total_analysts
                        }
                        
                        # Calculate consensus if we have analyst data
                        if total_analysts > 0:
                            buy_total = strong_buy + buy
                            sell_total = sell + strong_sell
                            
                            if buy_total > hold and buy_total > sell_total:
                                consensus_rating = 'BUY'
                            elif sell_total > hold and sell_total > buy_total:
                                consensus_rating = 'SELL'
                            else:
                                consensus_rating = 'HOLD'
                            
                            analyst_data['consensus'] = {
                                'rating': consensus_rating,
                                'recommendation': f"{total_analysts} analysts covering"
                            }
                            analyst_data['has_coverage'] = True
                            analyst_data['data_availability'] = f"{total_analysts} analyst recommendations"
                        
                        logger.info(f"   Found {total_analysts} analyst recommendations")
                        
                except Exception as process_error:
                    logger.warning(f"   Error processing recommendations: {process_error}")
            else:
                logger.info("   No analyst recommendations available from yfinance")
            
            # Try to fetch price targets
            try:
                price_targets = await asyncio.to_thread(lambda: ticker_obj.analyst_price_targets)
                if price_targets is not None and isinstance(price_targets, dict):
                    current_price = self._safe_number(price_targets.get('current'))
                    mean_target = self._safe_number(price_targets.get('mean'))
                    high_target = self._safe_number(price_targets.get('high'))
                    low_target = self._safe_number(price_targets.get('low'))
                    
                    # Calculate upside if we have both current price and mean target
                    upside_percent = None
                    if current_price and mean_target and current_price > 0:
                        upside_percent = ((mean_target - current_price) / current_price) * 100
                    
                    analyst_data['price_targets'] = {
                        'current': current_price,
                        'high': high_target,
                        'low': low_target,
                        'mean': mean_target,
                        'upside_percent': round(upside_percent, 1) if upside_percent else None
                    }
                    
                    # Update coverage status if we have price targets
                    if mean_target is not None:
                        analyst_data['has_coverage'] = True
                        if not analyst_data['data_availability'].startswith('No'):
                            analyst_data['data_availability'] += ', price targets available'
                        else:
                            analyst_data['data_availability'] = 'Price targets available'
                        
                        logger.info(f"   Found price targets: Mean ${mean_target:.2f}")
                        
            except Exception as pt_error:
                logger.warning(f"   Price targets not available: {pt_error}")
            
            result["analyst_coverage"] = analyst_data
            result["data_sources"].append("analyst")
            
        except Exception as e:
            logger.error(f"Error fetching analyst coverage: {e}")
            result["fetch_errors"].append(f"analyst_coverage: {str(e)}")
    
    async def _fetch_calendar_data(self, ticker_obj: yf.Ticker, result: Dict[str, Any]):
        """Fetch calendar events and earnings dates"""
        try:
            calendar_data = {}
            
            try:
                calendar = await asyncio.to_thread(lambda: ticker_obj.calendar)
                calendar_data["earnings_calendar"] = calendar.to_dict() if not calendar.empty else {}
            except Exception:
                pass
            
            try:
                earnings_dates = await asyncio.to_thread(lambda: ticker_obj.earnings_dates)
                calendar_data["earnings_dates"] = earnings_dates.to_dict() if not earnings_dates.empty else {}
            except Exception:
                pass
            
            result["calendar_data"] = calendar_data
            result["data_sources"].append("calendar")
            
        except Exception as e:
            logger.error(f"Error fetching calendar data: {e}")
            result["fetch_errors"].append(f"calendar_data: {str(e)}")
    
    async def _fetch_comprehensive_earnings_data(self, ticker_obj: yf.Ticker, result: Dict[str, Any]):
        """Fetch comprehensive earnings data and estimates"""
        try:
            earnings_data = {}
            
            # Get basic earnings metrics from info if available
            try:
                info = result.get("info", {})
                earnings_data.update({
                    'trailing_eps': info.get('trailingEps'),
                    'forward_eps': info.get('forwardEps'),
                    'earnings_growth': info.get('earningsGrowth'),
                    'revenue_growth': info.get('revenueGrowth'),
                    'profit_margins': info.get('profitMargins'),
                    'operating_margins': info.get('operatingMargins'),
                    'quarterly_earnings_growth': info.get('earningsQuarterlyGrowth'),
                    'quarterly_revenue_growth': info.get('revenueQuarterlyGrowth')
                })
            except Exception:
                pass
            
            # Try to get earnings calendar
            try:
                calendar = await asyncio.to_thread(lambda: ticker_obj.calendar)
                if not calendar.empty:
                    earnings_data['next_earnings_date'] = calendar.index[0].strftime('%Y-%m-%d') if len(calendar) > 0 else None
            except Exception:
                earnings_data['next_earnings_date'] = None
            
            result["earnings_data"] = earnings_data
            result["data_sources"].append("earnings")
            
        except Exception as e:
            logger.error(f"Error fetching earnings data: {e}")
            result["fetch_errors"].append(f"earnings_data: {str(e)}")
    
    async def _fetch_comprehensive_performance_metrics(self, ticker_obj: yf.Ticker, result: Dict[str, Any]):
        """Fetch comprehensive performance metrics and chart data"""
        try:
            performance_data = {}
            
            # Get basic performance data from info
            try:
                info = result.get("info", {})
                
                # Get recent price performance data (1 year for charts)
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                
                # Fetch daily data for charts
                daily_data = await asyncio.to_thread(
                    lambda: ticker_obj.history(start=start_date, end=end_date, interval="1d")
                )
                
                # Calculate performance metrics
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                week_52_high = info.get('fiftyTwoWeekHigh')
                week_52_low = info.get('fiftyTwoWeekLow')
                
                performance_data.update({
                    'current_price': current_price,
                    'week_52_high': week_52_high,
                    'week_52_low': week_52_low,
                    'day_change': info.get('regularMarketChange'),
                    'day_change_percent': info.get('regularMarketChangePercent'),
                    'average_volume': info.get('averageVolume'),
                    'beta': info.get('beta')
                })
                
                # Convert daily data to monthly for cleaner charts
                if not daily_data.empty:
                    monthly_chart = daily_data.resample('ME').agg({
                        'Open': 'first',
                        'High': 'max', 
                        'Low': 'min',
                        'Close': 'last',
                        'Volume': 'sum'
                    })
                    
                    chart_data = []
                    for date, row in monthly_chart.iterrows():
                        chart_data.append({
                            'date': date.strftime('%Y-%m-%d'),
                            'close': float(row['Close']) if pd.notna(row['Close']) else None,
                            'high': float(row['High']) if pd.notna(row['High']) else None,
                            'low': float(row['Low']) if pd.notna(row['Low']) else None,
                            'volume': float(row['Volume']) if pd.notna(row['Volume']) else None
                        })
                    
                    performance_data['chart_data_monthly'] = chart_data
                else:
                    performance_data['chart_data_monthly'] = []
                    
            except Exception as chart_error:
                logger.warning(f"Error processing performance charts: {chart_error}")
                performance_data['chart_data_monthly'] = []
            
            result["performance_metrics"] = performance_data
            result["data_sources"].append("performance")
            
        except Exception as e:
            logger.error(f"Error fetching performance metrics: {e}")
            result["fetch_errors"].append(f"performance_metrics: {str(e)}")
    
    async def _fetch_comprehensive_esg_sustainability(self, ticker_obj: yf.Ticker, result: Dict[str, Any]):
        """Fetch comprehensive ESG and sustainability metrics"""
        try:
            # Initialize with consistent structure
            esg_data = {
                'has_esg_data': False,
                'esg_scores': {
                    'total_esg_score': None,
                    'environment_score': None,
                    'social_score': None,
                    'governance_score': None,
                    'esg_percentile': None
                },
                'esg_assessment': {
                    'data_available': False,
                    'assessment_status': 'ESG Data Not Available',
                    'company_reporting': 'This company does not have ESG scores available through our data provider.'
                },
                'risk_factors': {
                    'environmental_risk': 'Not Available',
                    'social_risk': 'Not Available', 
                    'governance_risk': 'Not Available'
                },
                'sustainability_metrics': {
                    'carbon_emissions': None,
                    'water_usage': None,
                    'waste_management': None,
                    'renewable_energy': None
                },
                'data_availability': 'No ESG data available from current provider'
            }
            
            # Try to fetch ESG data
            try:
                sustainability = await asyncio.to_thread(lambda: ticker_obj.sustainability)
                if sustainability is not None and not sustainability.empty:
                    # Convert sustainability data to dict
                    sustainability_dict = sustainability.to_dict()
                    
                    # Extract ESG scores if available
                    if sustainability_dict:
                        # Get the latest ESG data
                        if hasattr(sustainability, 'columns') and len(sustainability.columns) > 0:
                            latest_col = sustainability.columns[0]
                            latest_data = sustainability[latest_col]
                            
                            if latest_data is not None:
                                # Extract common ESG metrics
                                esg_data['esg_scores'] = {
                                    'total_esg_score': latest_data.get('totalEsg'),
                                    'environment_score': latest_data.get('environmentScore'),
                                    'social_score': latest_data.get('socialScore'),
                                    'governance_score': latest_data.get('governanceScore'),
                                    'esg_percentile': latest_data.get('percentile')
                                }
                                
                                # Update assessment if we have actual scores
                                total_score = esg_data['esg_scores']['total_esg_score']
                                if total_score is not None:
                                    esg_data['esg_assessment'] = {
                                        'data_available': True,
                                        'assessment_status': 'ESG Data Available',
                                        'company_reporting': 'Company has published ESG metrics and sustainability reporting'
                                    }
                                    
                                    # Determine risk levels based on scores
                                    def score_to_risk(score):
                                        if score is None:
                                            return 'Unknown'
                                        elif score >= 70:
                                            return 'Low'
                                        elif score >= 50:
                                            return 'Medium'
                                        else:
                                            return 'High'
                                    
                                    esg_data['risk_factors'] = {
                                        'environmental_risk': score_to_risk(esg_data['esg_scores']['environment_score']),
                                        'social_risk': score_to_risk(esg_data['esg_scores']['social_score']),
                                        'governance_risk': score_to_risk(esg_data['esg_scores']['governance_score'])
                                    }
                                    
                                    esg_data['has_esg_data'] = True
                                    esg_data['data_availability'] = 'ESG scores and sustainability metrics available'
            except Exception as esg_error:
                logger.warning(f"ESG data not available: {esg_error}")
            
            result["sustainability_esg"] = esg_data
            result["data_sources"].append("esg")
            
        except Exception as e:
            logger.error(f"Error fetching ESG data: {e}")
            result["fetch_errors"].append(f"esg_data: {str(e)}")
    
    async def _fetch_comprehensive_dividend_info(self, ticker_obj: yf.Ticker, result: Dict[str, Any]):
        """Fetch comprehensive dividend information"""
        try:
            dividend_data = {}
            
            # Get basic dividend data from info
            try:
                info = result.get("info", {})
                dividend_data.update({
                    'dividend_yield': info.get('dividendYield'),
                    'dividend_rate': info.get('dividendRate'),
                    'payout_ratio': info.get('payoutRatio'),
                    'ex_dividend_date': info.get('exDividendDate'),
                    'last_dividend_value': info.get('lastDividendValue'),
                    'last_dividend_date': info.get('lastDividendDate')
                })
            except Exception:
                pass
            
            # Try to get dividend history
            try:
                dividends = await asyncio.to_thread(lambda: ticker_obj.dividends)
                if dividends is not None and not dividends.empty:
                    recent_dividends = dividends.tail(4).to_dict()  # Last 4 payments
                    dividend_data['recent_payments'] = {
                        str(date): float(amount) for date, amount in recent_dividends.items()
                    }
            except Exception:
                dividend_data['recent_payments'] = {}
            
            result["dividend_info"] = dividend_data
            result["data_sources"].append("dividend")
            
        except Exception as e:
            logger.error(f"Error fetching dividend info: {e}")
            result["fetch_errors"].append(f"dividend_info: {str(e)}")
    
    async def _fetch_comprehensive_recent_news(self, ticker_obj: yf.Ticker, result: Dict[str, Any]):
        """Fetch recent news and catalysts"""
        try:
            news_data = {
                'recent_headlines': []
            }
            
            try:
                news = await asyncio.to_thread(lambda: ticker_obj.news)
                if news and len(news) > 0:
                    # Get top 5 recent news items
                    for item in news[:5]:
                        news_item = {
                            'title': item.get('title', ''),
                            'publisher': item.get('publisher', ''),
                            'published': datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d') if item.get('providerPublishTime') else None,
                            'summary': item.get('summary', '')[:200]  # First 200 chars
                        }
                        news_data['recent_headlines'].append(news_item)
            except Exception as news_error:
                logger.warning(f"News data not available: {news_error}")
            
            result["recent_news"] = news_data
            result["data_sources"].append("news")
            
        except Exception as e:
            logger.error(f"Error fetching recent news: {e}")
            result["fetch_errors"].append(f"recent_news: {str(e)}")
    
    def _get_from_cache(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get data from cache if still valid"""
        if ticker in self.cache and ticker in self.cache_timestamps:
            cache_age = datetime.now() - self.cache_timestamps[ticker]
            if cache_age.total_seconds() < self.cache_duration:
                return self.cache[ticker]
        return None
    
    def _store_in_cache(self, ticker: str, data: Dict[str, Any]) -> None:
        """Store data in cache"""
        self.cache[ticker] = data
        self.cache_timestamps[ticker] = datetime.now()
        
        # Clean old cache entries (keep only last 100)
        if len(self.cache) > 100:
            oldest_ticker = min(self.cache_timestamps.keys(), 
                              key=lambda k: self.cache_timestamps[k])
            del self.cache[oldest_ticker]
            del self.cache_timestamps[oldest_ticker]
    
    def _calculate_comprehensive_smart_ratios(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive smart ratios for hedge fund analysis"""
        try:
            # Get data components
            company_info = data.get('company_info', {})
            financials = data.get('financial_statements', {})
            valuation = data.get('valuation_metrics', {})
            info = data.get('info', {})
            
            # Calculate current ratios from available data
            current_ratios = {
                'profitability': {
                    'net_margin': {'value': self._safe_number(info.get('profitMargins')), 'unit': '%'},
                    'roe': {'value': self._safe_number(info.get('returnOnEquity')), 'unit': '%'},
                    'roa': {'value': self._safe_number(info.get('returnOnAssets')), 'unit': '%'},
                    'gross_margin': {'value': self._safe_number(info.get('grossMargins')), 'unit': '%'},
                    'operating_margin': {'value': self._safe_number(info.get('operatingMargins')), 'unit': '%'}
                },
                'liquidity': {
                    'current_ratio': {'value': self._safe_number(info.get('currentRatio')), 'unit': 'x'},
                    'quick_ratio': {'value': self._safe_number(info.get('quickRatio')), 'unit': 'x'},
                    'cash_ratio': {'value': self._safe_number(info.get('cashRatio')), 'unit': 'x'}
                },
                'valuation': {
                    'pe_ratio': {'value': self._safe_number(info.get('trailingPE')), 'unit': 'x'},
                    'pb_ratio': {'value': self._safe_number(info.get('priceToBook')), 'unit': 'x'},
                    'ps_ratio': {'value': self._safe_number(info.get('priceToSalesTrailing12Months')), 'unit': 'x'},
                    'ev_ebitda': {'value': self._safe_number(info.get('enterpriseToEbitda')), 'unit': 'x'},
                    'peg_ratio': {'value': self._safe_number(info.get('pegRatio')), 'unit': 'x'}
                },
                'leverage': {
                    'debt_to_equity': {'value': self._safe_number(info.get('debtToEquity')), 'unit': '%'},
                    'interest_coverage': {'value': None, 'unit': 'x'},  # Would need calculation
                    'debt_to_assets': {'value': None, 'unit': '%'}      # Would need calculation
                },
                'efficiency': {
                    'asset_turnover': {'value': None, 'unit': 'x'},     # Would need calculation
                    'inventory_turnover': {'value': None, 'unit': 'x'}, # Would need calculation
                    'receivables_turnover': {'value': None, 'unit': 'x'} # Would need calculation
                }
            }
            
            # Calculate time series ratios from financial statements if available
            time_series_ratios = {}
            if financials:
                # Process financial statements for time series
                for statement_type in ['financials', 'balance_sheet', 'cashflow']:
                    statement_data = financials.get(statement_type, {}).get('data', {})
                    if statement_data:
                        for date_str, values in statement_data.items():
                            if date_str not in time_series_ratios:
                                time_series_ratios[date_str] = {
                                    'profitability': {},
                                    'liquidity': {},
                                    'efficiency': {}
                                }
                            
                            # Calculate ratios for this period
                            # This would be expanded with actual ratio calculations
                            # using the financial statement data
            
            return {
                'current_ratios': current_ratios,
                'time_series_ratios': time_series_ratios,
                'calculation_timestamp': datetime.now().isoformat(),
                'data_quality': {
                    'financial_statements_available': bool(financials),
                    'market_data_available': bool(data.get('monthly_prices', {}).get('has_data')),
                    'completeness_score': len([v for v in current_ratios['profitability'].values() if v['value'] is not None]) / 5
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating smart ratios: {e}")
            return {'error': str(e)}
    
    def _generate_ai_financial_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI-ready comprehensive financial summary for hedge fund analysis"""
        try:
            # Extract components
            company_info = data.get('company_info', {})
            valuation_metrics = data.get('valuation_metrics', {})
            financial_statements = data.get('financial_statements', {})
            earnings_data = data.get('earnings_data', {})
            analyst_coverage = data.get('analyst_coverage', {})
            performance_metrics = data.get('performance_metrics', {})
            smart_ratios = data.get('smart_ratios', {})
            
            # Create comprehensive summary for AI agents
            ai_summary = {
                'ticker': data.get('ticker', 'Unknown'),
                'company_name': company_info.get('name', 'Unknown'),
                'last_updated': datetime.now().isoformat(),
                
                # COMPLETE FINANCIAL STATEMENTS (all available years)
                'financial_statements': {
                    'income_statement': financial_statements.get('financials', {}).get('data', {}),
                    'balance_sheet': financial_statements.get('balance_sheet', {}).get('data', {}),
                    'cash_flow': financial_statements.get('cashflow', {}).get('data', {})
                },
                
                # COMPREHENSIVE MARKET DATA
                'market_data': {
                    'current_price': performance_metrics.get('current_price'),
                    'market_cap': valuation_metrics.get('market_cap'),
                    'enterprise_value': valuation_metrics.get('enterprise_value'),
                    'beta': performance_metrics.get('beta'),
                    'week_52_high': performance_metrics.get('week_52_high'),
                    'week_52_low': performance_metrics.get('week_52_low'),
                    'chart_data_monthly': performance_metrics.get('chart_data_monthly', [])
                },
                
                # COMPREHENSIVE VALUATION METRICS
                'valuation_metrics': {
                    'pe_ratio': valuation_metrics.get('pe_ratio'),
                    'pb_ratio': valuation_metrics.get('price_to_book'),
                    'ps_ratio': valuation_metrics.get('price_to_sales'),
                    'ev_ebitda': valuation_metrics.get('ev_to_ebitda'),
                    'peg_ratio': valuation_metrics.get('peg_ratio'),
                    'price_to_cash_flow': valuation_metrics.get('price_to_cash_flow'),
                    'book_value': valuation_metrics.get('book_value')
                },
                
                # COMPREHENSIVE ANALYST DATA
                'analyst_data': {
                    'recommendations': analyst_coverage.get('recommendations_summary', {}),
                    'price_targets': analyst_coverage.get('price_targets', {}),
                    'has_coverage': analyst_coverage.get('has_coverage', False),
                    'rating_summary': self._get_analyst_rating(analyst_coverage)
                },
                
                # COMPREHENSIVE EARNINGS DATA
                'earnings_data': {
                    'trailing_eps': earnings_data.get('trailing_eps'),
                    'forward_eps': earnings_data.get('forward_eps'),
                    'earnings_growth': earnings_data.get('earnings_growth'),
                    'revenue_growth': earnings_data.get('revenue_growth'),
                    'profit_margins': earnings_data.get('profit_margins'),
                    'operating_margins': earnings_data.get('operating_margins'),
                    'next_earnings_date': earnings_data.get('next_earnings_date')
                },
                
                # SMART RATIOS FOR ADVANCED ANALYSIS
                'smart_ratios': {
                    'current_ratios': smart_ratios.get('current_ratios', {}),
                    'time_series_ratios': smart_ratios.get('time_series_ratios', {})
                },
                
                # COMPREHENSIVE OWNERSHIP & DIVIDEND DATA
                'ownership_data': data.get('ownership_data', {}),
                'dividend_data': data.get('dividend_info', {}),
                
                # NEWS & ESG FOR QUALITATIVE ANALYSIS
                'recent_news': data.get('recent_news', {}),
                'esg_data': data.get('sustainability_esg', {}),
                
                # DATA QUALITY INDICATORS
                'data_completeness': {
                    'financial_statements_years': len(financial_statements.get('financials', {}).get('data', {})),
                    'monthly_price_points': len(data.get('monthly_prices', {}).get('price_history', [])),
                    'analyst_coverage': analyst_coverage.get('has_coverage', False),
                    'esg_available': data.get('sustainability_esg', {}).get('has_esg_data', False),
                    'total_data_sources': len(data.get('data_sources', [])),
                    'quality_score': data.get('data_quality_score', 0.0)
                }
            }
            
            return ai_summary
            
        except Exception as e:
            logger.error(f"Error generating AI financial summary: {e}")
            return {'error': str(e)}
    
    def _get_analyst_rating(self, analyst: Dict) -> Optional[str]:
        """Convert analyst recommendations to simple rating"""
        try:
            recs = analyst.get('recommendations_summary', {})
            if not recs:
                return None
            
            buy_total = recs.get('strong_buy', 0) + recs.get('buy', 0)
            hold_total = recs.get('hold', 0)
            sell_total = recs.get('sell', 0) + recs.get('strong_sell', 0)
            
            if buy_total > hold_total and buy_total > sell_total:
                return 'BUY'
            elif sell_total > hold_total and sell_total > buy_total:
                return 'SELL'
            else:
                return 'HOLD'
        except Exception:
            return None
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.cache),
            "cache_duration_seconds": self.cache_duration,
            "cached_tickers": list(self.cache.keys()),
            "oldest_cache_entry": min(self.cache_timestamps.values()).isoformat() if self.cache_timestamps else None,
            "newest_cache_entry": max(self.cache_timestamps.values()).isoformat() if self.cache_timestamps else None
        }