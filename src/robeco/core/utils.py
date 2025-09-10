"""
Utility functions for Robeco AI System

Common helper functions used throughout the system.
"""

import logging
import logging.config
from typing import Dict, Any, Optional, Union
from decimal import Decimal
from datetime import datetime, timedelta
import json
import asyncio
import functools


def setup_logging(config: Dict[str, Any]) -> None:
    """Setup logging configuration"""
    logging.config.dictConfig(config)


def format_currency(amount: Union[int, float, Decimal], currency: str = "USD") -> str:
    """Format currency with proper symbols and formatting"""
    if amount is None or amount == 0:
        return "N/A"
    
    if abs(amount) >= 1e12:
        return f"${amount/1e12:.2f}T"
    elif abs(amount) >= 1e9:
        return f"${amount/1e9:.2f}B"
    elif abs(amount) >= 1e6:
        return f"${amount/1e6:.2f}M"
    elif abs(amount) >= 1e3:
        return f"${amount/1e3:.2f}K"
    else:
        return f"${amount:.2f}"


def format_percentage(value: Union[int, float], decimal_places: int = 2) -> str:
    """Format percentage with proper formatting"""
    if value is None:
        return "N/A"
    return f"{value:.{decimal_places}%}"


def format_ratio(value: Union[int, float], decimal_places: int = 2) -> str:
    """Format financial ratios"""
    if value is None or value == 0:
        return "N/A"
    return f"{value:.{decimal_places}f}"


def calculate_metrics(financial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate derived financial metrics"""
    metrics = {}
    
    try:
        # Calculate additional ratios
        market_cap = financial_data.get('marketCap', 0)
        total_revenue = financial_data.get('totalRevenue', 0)
        free_cashflow = financial_data.get('freeCashflow', 0)
        shares_outstanding = financial_data.get('sharesOutstanding', 0)
        
        if market_cap and total_revenue:
            metrics['price_to_sales'] = market_cap / total_revenue
        
        if free_cashflow and shares_outstanding:
            metrics['fcf_per_share'] = free_cashflow / shares_outstanding
        
        # Calculate growth rates
        revenue_growth = financial_data.get('revenueGrowth', 0)
        earnings_growth = financial_data.get('earningsGrowth', 0)
        
        if revenue_growth and earnings_growth:
            metrics['earnings_revenue_growth_ratio'] = earnings_growth / revenue_growth
        
        # Calculate efficiency metrics
        total_assets = financial_data.get('totalAssets', 0)
        if total_revenue and total_assets:
            metrics['asset_turnover'] = total_revenue / total_assets
        
    except (ZeroDivisionError, TypeError):
        pass
    
    return metrics


def validate_ticker(ticker: str) -> bool:
    """Validate ticker symbol format"""
    if not ticker:
        return False
    
    # Basic validation - alphanumeric and dots/hyphens allowed
    import re
    pattern = r'^[A-Z0-9\.\-]{1,10}$'
    return bool(re.match(pattern, ticker.upper()))


def parse_timeframe(timeframe: str) -> timedelta:
    """Parse timeframe string to timedelta"""
    timeframe = timeframe.lower()
    
    if timeframe.endswith('d'):
        days = int(timeframe[:-1])
        return timedelta(days=days)
    elif timeframe.endswith('w'):
        weeks = int(timeframe[:-1])
        return timedelta(weeks=weeks)
    elif timeframe.endswith('m'):
        months = int(timeframe[:-1])
        return timedelta(days=months * 30)  # Approximate
    elif timeframe.endswith('y'):
        years = int(timeframe[:-1])
        return timedelta(days=years * 365)  # Approximate
    else:
        raise ValueError(f"Invalid timeframe format: {timeframe}")


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system operations"""
    import re
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove extra spaces and trim
    filename = ' '.join(filename.split())
    return filename.strip()


def calculate_quality_score(data: Dict[str, Any], weights: Optional[Dict[str, float]] = None) -> float:
    """Calculate data quality score based on completeness and accuracy"""
    if not data:
        return 0.0
    
    default_weights = {
        'completeness': 0.4,
        'accuracy': 0.3,
        'timeliness': 0.2,
        'consistency': 0.1
    }
    
    if weights:
        default_weights.update(weights)
    
    scores = {}
    
    # Completeness: percentage of non-null values
    total_fields = len(data)
    non_null_fields = sum(1 for v in data.values() if v is not None and v != '')
    scores['completeness'] = non_null_fields / total_fields if total_fields > 0 else 0
    
    # Accuracy: basic validation (non-negative for financial metrics)
    valid_fields = 0
    numeric_fields = 0
    for key, value in data.items():
        if isinstance(value, (int, float)):
            numeric_fields += 1
            if key.lower() in ['price', 'market_cap', 'revenue'] and value >= 0:
                valid_fields += 1
            elif value is not None:
                valid_fields += 1
    
    scores['accuracy'] = valid_fields / numeric_fields if numeric_fields > 0 else 1.0
    
    # Timeliness: assume recent data is good (placeholder)
    scores['timeliness'] = 1.0
    
    # Consistency: placeholder (would need historical data)
    scores['consistency'] = 1.0
    
    # Weighted average
    quality_score = sum(scores[metric] * weight for metric, weight in default_weights.items())
    return min(max(quality_score, 0.0), 1.0)  # Clamp between 0 and 1


def retry_async(max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0, 
                jitter: bool = True, retryable_exceptions: tuple = None):
    """Enhanced decorator for retrying async functions with intelligent error handling"""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            import random
            last_exception = None
            
            # Default retryable exceptions for Gemini API
            default_retryable = (
                ConnectionError, TimeoutError, OSError,
                # Add common HTTP errors that should be retried
                Exception  # Will filter more specifically below
            )
            
            exceptions_to_retry = retryable_exceptions or default_retryable
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_msg = str(e).lower()
                    
                    # Enhanced error classification for Gemini API
                    should_retry = False
                    
                    # Always retry these specific errors
                    if any(retryable in error_msg for retryable in [
                        '500 internal', 'service unavailable', '502 bad gateway', 
                        '503 service unavailable', '504 gateway timeout',
                        'connection error', 'timeout', 'temporary failure',
                        'rate limit', 'quota exceeded', 'resource exhausted'
                    ]):
                        should_retry = True
                    
                    # Don't retry authentication or permission errors
                    elif any(non_retryable in error_msg for non_retryable in [
                        '401 unauthorized', '403 forbidden', 'invalid api key',
                        '400 bad request', 'permission denied', 'api key not valid'
                    ]):
                        should_retry = False
                        logging.getLogger('robeco.retry').error(
                            f"Non-retryable error on attempt {attempt + 1}: {e}"
                        )
                    
                    # For other exceptions, check if they match retryable types
                    else:
                        should_retry = isinstance(e, exceptions_to_retry)
                    
                    if attempt < max_retries and should_retry:
                        # Enhanced backoff with jitter to prevent thundering herd
                        base_delay = delay * (backoff_factor ** attempt)
                        if jitter:
                            # Add random jitter (±25%)
                            jitter_range = base_delay * 0.25
                            actual_delay = base_delay + random.uniform(-jitter_range, jitter_range)
                        else:
                            actual_delay = base_delay
                        
                        # Cap maximum delay at 30 seconds
                        actual_delay = min(actual_delay, 30.0)
                        
                        logging.getLogger('robeco.retry').warning(
                            f"Attempt {attempt + 1} failed with {type(e).__name__}: {e}. "
                            f"Retrying in {actual_delay:.2f}s..."
                        )
                        
                        await asyncio.sleep(actual_delay)
                    else:
                        # Log final failure
                        if should_retry:
                            logging.getLogger('robeco.retry').error(
                                f"All {max_retries + 1} attempts failed. Final error: {e}"
                            )
                        raise last_exception
            
        return wrapper
    return decorator


def time_execution(func):
    """Decorator to time function execution"""
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = await func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logging.getLogger('robeco.performance').info(
                f"{func.__name__} executed in {execution_time:.3f} seconds"
            )
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logging.getLogger('robeco.performance').error(
                f"{func.__name__} failed after {execution_time:.3f} seconds: {e}"
            )
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            execution_time = (datetime.now() - start_time).total_seconds()
            logging.getLogger('robeco.performance').info(
                f"{func.__name__} executed in {execution_time:.3f} seconds"
            )
            return result
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logging.getLogger('robeco.performance').error(
                f"{func.__name__} failed after {execution_time:.3f} seconds: {e}"
            )
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime and other objects"""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        # Handle pandas Timestamp objects
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        # Handle pandas NaT (Not a Time) objects
        elif str(type(obj)) == "<class 'pandas._libs.tslibs.nattype.NaTType'>":
            return None
        # Handle numpy int64 and other numpy types
        elif hasattr(obj, 'item'):
            return obj.item()
        # Handle numpy arrays
        elif hasattr(obj, 'tolist'):
            return obj.tolist()
        return super().default(obj)


def _convert_keys(obj):
    """Recursively convert dictionary keys to strings"""
    if isinstance(obj, dict):
        return {str(k): _convert_keys(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_keys(item) for item in obj]
    elif hasattr(obj, 'isoformat'):  # pandas Timestamp
        return obj.isoformat()
    elif hasattr(obj, 'item'):  # numpy types
        return obj.item()
    elif hasattr(obj, 'tolist'):  # numpy arrays
        return obj.tolist()
    else:
        return obj

def safe_json_dumps(obj: Any, **kwargs) -> str:
    """Safely serialize object to JSON"""
    # First convert all keys to strings and handle complex objects
    cleaned_obj = _convert_keys(obj)
    return json.dumps(cleaned_obj, cls=JSONEncoder, **kwargs)


def get_system_info() -> Dict[str, Any]:
    """Get system information for monitoring"""
    import platform
    import psutil
    
    return {
        'platform': platform.platform(),
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total,
        'memory_available': psutil.virtual_memory().available,
        'memory_usage_percent': psutil.virtual_memory().percent,
        'disk_usage_percent': psutil.disk_usage('/').percent,
        'timestamp': datetime.now().isoformat()
    }