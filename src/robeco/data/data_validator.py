"""
Data validation utilities for financial data

Validates data quality, completeness, and consistency.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import numpy as np

from ..core.utils import calculate_quality_score


class DataValidator:
    """Validates financial data quality and consistency"""
    
    def __init__(self):
        self.validation_rules = self._initialize_rules()
    
    def validate_comprehensive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate comprehensive financial data
        
        Args:
            data: Financial data to validate
            
        Returns:
            Validation results with scores and issues
        """
        validation_result = {
            "overall_score": 0.0,
            "validation_timestamp": datetime.now().isoformat(),
            "category_scores": {},
            "issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        # Validate each data category
        categories = {
            "basic_info": self._validate_basic_info,
            "financial_statements": self._validate_financial_statements,
            "market_data": self._validate_market_data,
            "ownership_data": self._validate_ownership_data
        }
        
        category_scores = []
        
        for category, validator in categories.items():
            if category in data or category.replace("_", "") in data:
                score, issues = validator(data.get(category, data.get(category.replace("_", ""), {})))
                validation_result["category_scores"][category] = score
                validation_result["issues"].extend(issues)
                category_scores.append(score)
        
        # Calculate overall score
        validation_result["overall_score"] = np.mean(category_scores) if category_scores else 0.0
        
        # Generate recommendations
        validation_result["recommendations"] = self._generate_recommendations(validation_result)
        
        return validation_result
    
    def _validate_basic_info(self, info_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Validate basic company information"""
        score = 1.0
        issues = []
        
        required_fields = [
            "marketCap", "enterpriseValue", "trailingPE", "priceToBook",
            "returnOnEquity", "debtToEquity", "currentRatio"
        ]
        
        missing_fields = [field for field in required_fields if not info_data.get(field)]
        if missing_fields:
            score -= 0.1 * len(missing_fields)
            issues.append(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Validate reasonable ranges
        if info_data.get("trailingPE", 0) > 100:
            score -= 0.1
            issues.append("Unusually high P/E ratio (>100)")
        
        if info_data.get("debtToEquity", 0) > 500:
            score -= 0.1
            issues.append("Very high debt-to-equity ratio (>500%)")
        
        return max(score, 0.0), issues
    
    def _validate_financial_statements(self, financial_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Validate financial statements data"""
        score = 1.0
        issues = []
        
        # Check if we have both annual and quarterly data
        if not financial_data.get("annual", {}):
            score -= 0.3
            issues.append("Missing annual financial statements")
        
        if not financial_data.get("quarterly", {}):
            score -= 0.2
            issues.append("Missing quarterly financial statements")
        
        return max(score, 0.0), issues
    
    def _validate_market_data(self, market_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Validate market and price data"""
        score = 1.0
        issues = []
        
        # Check for different time periods
        expected_periods = ["history_1mo", "history_3mo", "history_1y"]
        missing_periods = [period for period in expected_periods if period not in market_data]
        
        if missing_periods:
            score -= 0.1 * len(missing_periods)
            issues.append(f"Missing market data for periods: {', '.join(missing_periods)}")
        
        return max(score, 0.0), issues
    
    def _validate_ownership_data(self, ownership_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Validate ownership and holdings data"""
        score = 1.0
        issues = []
        
        if not ownership_data.get("institutional_holders"):
            score -= 0.2
            issues.append("Missing institutional holdings data")
        
        if not ownership_data.get("major_holders"):
            score -= 0.1
            issues.append("Missing major holders data")
        
        return max(score, 0.0), issues
    
    def _generate_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        if validation_result["overall_score"] < 0.7:
            recommendations.append("Consider using alternative data sources to improve data quality")
        
        if "Missing required fields" in str(validation_result["issues"]):
            recommendations.append("Check if ticker symbol is correct and company data is available")
        
        return recommendations
    
    def _initialize_rules(self) -> Dict[str, Any]:
        """Initialize validation rules"""
        return {
            "min_data_quality": 0.6,
            "required_fields": {
                "basic_info": ["marketCap", "trailingPE", "returnOnEquity"],
                "financial_statements": ["annual", "quarterly"],
                "market_data": ["history_1y"]
            },
            "reasonable_ranges": {
                "trailingPE": {"min": 0, "max": 100},
                "debtToEquity": {"min": 0, "max": 500},
                "currentRatio": {"min": 0, "max": 10}
            }
        }