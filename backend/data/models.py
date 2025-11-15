"""Pydantic Data Models

Defines all data structures used throughout the application for:
- Portfolio state and positions
- Daily analysis and recommendations
- Market data and news
- Transaction history
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class ActionType(str, Enum):
    """Trade action types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    INITIATE = "INITIATE"
    TRIM = "TRIM"
    ADD = "ADD"


class PriorityLevel(str, Enum):
    """Recommendation priority"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RiskMode(str, Enum):
    """Market risk regime"""
    EXTREME_COMPLACENCY = "extreme_complacency"
    NORMAL = "normal"
    CAUTION = "caution"
    RISK_OFF = "risk_off"


class MarketRegime(str, Enum):
    """Market trend regime"""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"


class TriggerType(str, Enum):
    """Radar scan trigger types"""
    VOLUME_SPIKE = "volume_spike"
    PRICE_MOVE = "price_move"
    MOMENTUM_CROSSOVER = "momentum_crossover"
    RSI_EXTREME = "rsi_extreme"
    MANUAL = "manual"


# ============================================================================
# Portfolio Models
# ============================================================================

class Position(BaseModel):
    """Individual position in the portfolio"""
    ticker: str
    shares: int
    cost_basis: float
    current_price: float
    market_value: float
    weight: float = Field(ge=0.0, le=1.0)
    unrealized_gain: float
    unrealized_gain_pct: float

    @property
    def daily_gain(self) -> float:
        """Calculate daily gain (requires price history)"""
        return self.unrealized_gain


class AllocationBreakdown(BaseModel):
    """Portfolio allocation breakdown"""
    core: float = Field(ge=0.0, le=1.0)
    major_satellites: float = Field(ge=0.0, le=1.0, default=0.0)
    tactical_satellites: float = Field(ge=0.0, le=1.0, default=0.0)
    hedging: float = Field(ge=0.0, le=1.0, default=0.0)

    @field_validator('core', 'major_satellites', 'tactical_satellites', 'hedging')
    @classmethod
    def validate_allocation(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError('Allocation must be between 0 and 1')
        return v


class SectorBreakdown(BaseModel):
    """Sector allocation breakdown"""
    allocations: Dict[str, float] = Field(default_factory=dict)

    def add_sector(self, sector: str, allocation: float):
        """Add or update sector allocation"""
        self.allocations[sector] = allocation

    @property
    def total(self) -> float:
        """Total allocation across all sectors"""
        return sum(self.allocations.values())


class RiskMetrics(BaseModel):
    """Portfolio risk metrics"""
    sharpe_ratio_30d: Optional[float] = None
    volatility_30d: Optional[float] = None
    max_drawdown: Optional[float] = None
    beta_to_spy: Optional[float] = None
    correlation_to_spy: Optional[float] = None
    var_95: Optional[float] = None  # Value at Risk
    sortino_ratio: Optional[float] = None


class PortfolioState(BaseModel):
    """Complete portfolio state snapshot"""
    as_of: datetime
    initial_capital: float
    total_value: float
    cash_balance: float
    total_return_pct: float
    daily_return_pct: float
    positions: Dict[str, Position]
    allocation_breakdown: AllocationBreakdown
    sector_breakdown: Dict[str, float] = Field(default_factory=dict)
    geography_breakdown: Dict[str, float] = Field(default_factory=dict)
    risk_metrics: RiskMetrics

    @property
    def total_equity_value(self) -> float:
        """Total value of equity positions"""
        return sum(pos.market_value for pos in self.positions.values())

    @property
    def total_unrealized_gain(self) -> float:
        """Total unrealized gains across all positions"""
        return sum(pos.unrealized_gain for pos in self.positions.values())

    @property
    def position_count(self) -> int:
        """Number of positions held"""
        return len(self.positions)


# ============================================================================
# Market Data Models
# ============================================================================

class PriceData(BaseModel):
    """Price and volume data for an ETF"""
    ticker: str
    current_price: float
    price_change_1d: float
    price_change_5d: Optional[float] = None
    price_change_30d: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    volume_today: int
    volume_30d_avg: int
    volume_ratio: float  # today's volume / 30-day avg


class TechnicalIndicators(BaseModel):
    """Technical analysis indicators"""
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[str] = None
    bollinger_upper: Optional[float] = None
    bollinger_lower: Optional[float] = None
    bollinger_position: Optional[str] = None  # "upper_band", "middle", "lower_band"


class NewsArticle(BaseModel):
    """News article data"""
    title: str
    source: str
    url: str
    published_at: datetime
    description: Optional[str] = None
    content: Optional[str] = None


class NewsAnalysis(BaseModel):
    """News analysis for an ETF"""
    ticker: str
    news_count: int
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    relevance_score: float = Field(ge=0.0, le=1.0)
    headlines: List[str] = Field(default_factory=list)
    llm_summary: Optional[str] = None
    key_themes: List[str] = Field(default_factory=list)
    risk_factors: List[str] = Field(default_factory=list)


# ============================================================================
# Analysis Models
# ============================================================================

class MarketOverview(BaseModel):
    """Daily market overview"""
    vix_level: float
    vix_change_pct: float
    vix_5d_avg: float
    risk_mode: RiskMode
    sp500_close: float
    sp500_return_1d: float
    sp500_return_5d: Optional[float] = None
    market_regime: MarketRegime
    key_macro_events: List[str] = Field(default_factory=list)


class FocusListItem(BaseModel):
    """ETF flagged for deep analysis"""
    ticker: str
    trigger_type: TriggerType
    trigger_value: float
    trigger_description: str
    price_data: PriceData
    technical_indicators: TechnicalIndicators
    news_analysis: Optional[NewsAnalysis] = None
    recommendation: ActionType


class AllocationDetails(BaseModel):
    """Allocation change details for a recommendation"""
    current_allocation: float = Field(ge=0.0, le=1.0)
    target_allocation: float = Field(ge=0.0, le=1.0)
    allocation_change: float
    shares_current: int
    shares_target: int
    shares_to_trade: int


class TransactionDetails(BaseModel):
    """Transaction execution details"""
    estimated_price: float
    estimated_cost: float
    commission: float
    total_cost: float
    execution_timeframe: str
    source_of_funds: Optional[str] = None


class Justification(BaseModel):
    """Trade justification with evidence"""
    thesis: str
    quantitative_evidence: Dict[str, str]
    qualitative_evidence: Dict[str, str]
    risk_assessment: Dict[str, str]
    holding_period: str
    review_triggers: List[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    """Trade recommendation"""
    ticker: str
    action: ActionType
    priority: PriorityLevel
    confidence: float = Field(ge=0.0, le=1.0)
    allocation: AllocationDetails
    transaction_details: TransactionDetails
    justification: Justification
    prospectus_text: str


class PortfolioSnapshot(BaseModel):
    """Portfolio snapshot for daily analysis"""
    total_value: float
    daily_return_pct: float
    total_return_pct: float
    sharpe_ratio_30d: Optional[float] = None
    max_drawdown: Optional[float] = None
    days_since_inception: int
    allocation_breakdown: Dict[str, float]
    top_performers_1d: List[Dict[str, float]] = Field(default_factory=list)
    top_performers_mtd: List[Dict[str, float]] = Field(default_factory=list)


class ExecutionSummary(BaseModel):
    """Analysis execution summary"""
    analysis_quality: str  # "high", "medium", "low"
    focus_list_count: int
    recommendations_count: int
    api_calls_made: Dict[str, int]
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class DailyAnalysis(BaseModel):
    """Complete daily analysis output"""
    date: str
    timestamp: datetime
    execution_time_seconds: float
    market_overview: MarketOverview
    focus_list: List[FocusListItem]
    recommendations: List[Recommendation]
    portfolio_snapshot: PortfolioSnapshot
    execution_summary: ExecutionSummary


# ============================================================================
# Transaction Models
# ============================================================================

class Transaction(BaseModel):
    """Individual transaction record"""
    id: str
    date: str
    ticker: str
    action: ActionType
    shares: int
    price: float
    commission: float
    total_cost: float
    justification: str
    analysis_reference: Optional[str] = None


class TransactionHistory(BaseModel):
    """Complete transaction history"""
    transactions: List[Transaction] = Field(default_factory=list)
    summary: Dict[str, float] = Field(default_factory=dict)

    def add_transaction(self, txn: Transaction):
        """Add a transaction to history"""
        self.transactions.append(txn)
        self._update_summary()

    def _update_summary(self):
        """Update summary statistics"""
        self.summary = {
            "total_transactions": len(self.transactions),
            "total_commissions_paid": sum(t.commission for t in self.transactions),
            "total_bought": sum(t.total_cost for t in self.transactions if t.action in [ActionType.BUY, ActionType.INITIATE]),
            "total_sold": sum(t.total_cost for t in self.transactions if t.action == ActionType.SELL),
        }


# ============================================================================
# API Response Models
# ============================================================================

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, bool]


class AnalysisRequest(BaseModel):
    """Request for manual analysis run"""
    date: Optional[str] = None
    force_refresh: bool = False
    include_news: bool = True
    include_llm: bool = True
