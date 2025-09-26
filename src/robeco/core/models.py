"""
Core data models for Robeco AI System

Defines the fundamental data structures used throughout the system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class AnalysisStatus(Enum):
    """Analysis status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentType(Enum):
    """AI Agent types enumeration"""
    MARKET_RESEARCH = "market_research"
    FINANCIAL_ANALYSIS = "financial_analysis"
    TECHNICAL_ANALYSIS = "technical_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    ESG_ANALYSIS = "esg_analysis"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    INDUSTRY_ANALYSIS = "industry_analysis"
    VALUATION = "valuation"
    PORTFOLIO_ANALYSIS = "portfolio_analysis"
    INVESTMENT_STRATEGY = "investment_strategy"


@dataclass
class DataSources:
    """Data sources provided by user"""
    data_sources: str = ""
    key_information: str = ""
    investment_context: str = ""

@dataclass
class AnalysisContext:
    """Context object containing analysis parameters"""
    company_name: str
    ticker: str
    user_query: str
    analysis_focus: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: str = ""
    priority: int = 1
    data_sources: Optional[DataSources] = None
    
    def __post_init__(self):
        if not self.session_id:
            self.session_id = f"{self.ticker}_{self.timestamp.strftime('%Y%m%d_%H%M%S')}"


@dataclass
class AnalysisResult:
    """Result object containing analysis output"""
    agent_id: str
    agent_type: AgentType
    data: Dict[str, Any]
    quality_score: float
    processing_time: float
    timestamp: datetime = field(default_factory=datetime.now)
    status: AnalysisStatus = AnalysisStatus.COMPLETED
    error_message: Optional[str] = None
    data_sources: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "data": self.data,
            "quality_score": self.quality_score,
            "processing_time": self.processing_time,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status.value,
            "error_message": self.error_message,
            "data_sources": self.data_sources
        }


@dataclass
class WebSocketMessage:
    """WebSocket message structure"""
    type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    client_id: Optional[str] = None
    
    def to_json(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary"""
        return {
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "client_id": self.client_id
        }


@dataclass
class FinancialData:
    """Structured financial data from yfinance"""
    ticker: str
    company_name: str
    
    # Market data
    current_price: float
    market_cap: int
    enterprise_value: int
    
    # Valuation ratios
    pe_ratio: float
    pb_ratio: float
    ps_ratio: float
    ev_ebitda: float
    
    # Profitability metrics
    roe: float
    roa: float
    roic: float
    gross_margin: float
    operating_margin: float
    net_margin: float
    
    # Financial strength
    total_cash: int
    total_debt: int
    debt_to_equity: float
    current_ratio: float
    quick_ratio: float
    
    # Growth metrics
    revenue_growth: float
    earnings_growth: float
    free_cash_flow: int
    
    # Dividend metrics
    dividend_yield: float
    payout_ratio: float
    dividend_rate: float
    
    # Additional data
    timestamp: datetime = field(default_factory=datetime.now)
    data_quality: float = 1.0
    
    @classmethod
    def from_yfinance_info(cls, ticker: str, info: Dict[str, Any]) -> 'FinancialData':
        """Create FinancialData from yfinance info dictionary"""
        return cls(
            ticker=ticker,
            company_name=info.get('longName', ticker),
            current_price=info.get('currentPrice', info.get('regularMarketPrice', 0)),
            market_cap=info.get('marketCap', 0),
            enterprise_value=info.get('enterpriseValue', 0),
            pe_ratio=info.get('trailingPE', 0),
            pb_ratio=info.get('priceToBook', 0),
            ps_ratio=info.get('priceToSalesTrailing12Months', 0),
            ev_ebitda=info.get('enterpriseToEbitda', 0),
            roe=info.get('returnOnEquity', 0),
            roa=info.get('returnOnAssets', 0),
            roic=info.get('returnOnCapital', 0),
            gross_margin=info.get('grossMargins', 0),
            operating_margin=info.get('operatingMargins', 0),
            net_margin=info.get('netIncomeToCommon', 0),
            total_cash=info.get('totalCash', 0),
            total_debt=info.get('totalDebt', 0),
            debt_to_equity=info.get('debtToEquity', 0),
            current_ratio=info.get('currentRatio', 0),
            quick_ratio=info.get('quickRatio', 0),
            revenue_growth=info.get('revenueGrowth', 0),
            earnings_growth=info.get('earningsGrowth', 0),
            free_cash_flow=info.get('freeCashflow', 0),
            dividend_yield=info.get('dividendYield', 0),
            payout_ratio=info.get('payoutRatio', 0),
            dividend_rate=info.get('dividendRate', 0)
        )