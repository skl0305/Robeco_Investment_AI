"""
Data processing utilities for financial data

Handles data cleaning, transformation, and enrichment.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from ..core.utils import calculate_quality_score


class DataProcessor:
    """Processes and enriches financial data"""
    
    def __init__(self):
        self.processed_cache = {}
    
    def process_financial_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw financial data into structured format
        
        Args:
            raw_data: Raw data from yfinance_fetcher
            
        Returns:
            Processed and enriched financial data
        """
        processed = {
            "ticker": raw_data.get("ticker", ""),
            "processed_timestamp": datetime.now().isoformat(),
            "data_quality_score": raw_data.get("data_quality_score", 0.0),
            "processed_metrics": {},
            "trend_analysis": {},
            "comparative_metrics": {},
            "risk_indicators": {}
        }
        
        # Process key metrics
        if "key_metrics" in raw_data:
            processed["processed_metrics"] = self._enhance_key_metrics(
                raw_data["key_metrics"]
            )
        
        # Process market data for trends
        if "market_data" in raw_data:
            processed["trend_analysis"] = self._analyze_price_trends(
                raw_data["market_data"]
            )
        
        # Process financial statements
        if "financial_statements" in raw_data:
            processed["financial_ratios"] = self._calculate_financial_ratios(
                raw_data["financial_statements"]
            )
        
        return processed
    
    def _enhance_key_metrics(self, key_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance key metrics with additional calculations"""
        enhanced = key_metrics.copy()
        
        # Calculate additional ratios
        if key_metrics.get("market_cap") and key_metrics.get("free_cashflow"):
            enhanced["price_to_fcf"] = key_metrics["market_cap"] / key_metrics["free_cashflow"]
        
        # Risk indicators
        enhanced["debt_risk"] = "High" if key_metrics.get("debt_equity", 0) > 1.0 else "Low"
        enhanced["liquidity_risk"] = "High" if key_metrics.get("current_ratio", 0) < 1.0 else "Low"
        
        return enhanced
    
    def _analyze_price_trends(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze price trends from market data"""
        trends = {}
        
        # Analyze different time periods
        for period in ["1mo", "3mo", "6mo", "1y"]:
            period_key = f"history_{period}"
            if period_key in market_data:
                period_data = market_data[period_key]
                if "price_change" in period_data:
                    trends[f"{period}_trend"] = {
                        "direction": "up" if period_data["price_change"] > 0 else "down",
                        "magnitude": abs(period_data["price_change"]),
                        "percentage": (period_data["price_change"] / period_data.get("latest_price", 1)) * 100
                    }
        
        return trends
    
    def _calculate_financial_ratios(self, financial_statements: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate additional financial ratios"""
        ratios = {}
        
        # This would contain more sophisticated ratio calculations
        # based on the financial statements data
        
        return ratios