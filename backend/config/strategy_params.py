"""Strategy Parameters Configuration

Defines the growth-aggressive investment strategy parameters including:
- Position limits and allocation rules
- VIX-based risk thresholds
- Trading rules and constraints
- Radar scan trigger levels
- Rebalancing criteria
"""

from typing import Dict

# ============================================================================
# Position Limits - Growth-Aggressive Profile
# ============================================================================
# These limits reflect the user's actual aggressive portfolio (95% equity,
# concentrated positions in IYW @26% and ITA @20%)

POSITION_LIMITS: Dict[str, float] = {
    'core_min': 0.25,                # Minimum core allocation (lower than conservative)
    'core_max': 0.40,                # Maximum core allocation
    'single_position_max': 0.30,     # Max % in any single ETF (user has IVV at 30%)
    'sector_max': 0.50,              # Max % in any sector (allow concentrated bets)
    'tactical_position_max': 0.30,   # Max % in single tactical satellite
    'equity_min': 0.85,              # Minimum equity exposure (aggressive)
    'equity_max': 1.00,              # Can be 100% equities
    'cash_overnight_max': 0.05,      # Project requirement (5% max cash)
    'sgov_exempt': True,             # SGOV doesn't count toward cash limit
}


# ============================================================================
# VIX-Based Risk Thresholds
# ============================================================================
# Aggressive profile uses higher VIX thresholds before reducing risk
# (Conservative would use VIX > 30 for risk-off, we use VIX > 35)

VIX_THRESHOLDS: Dict[str, float] = {
    'extreme_complacency': 15.0,     # VIX < 15: Market too complacent, reduce risk
    'normal_lower': 15.0,            # VIX 15-25: Normal market conditions
    'normal_upper': 25.0,
    'caution': 25.0,                 # VIX 25-35: Elevated volatility, trim high-beta
    'risk_off': 35.0,                # VIX > 35: Defensive mode (higher than standard 30)
}


# ============================================================================
# Risk Mode Equity Allocations
# ============================================================================
# Dynamic equity allocation based on VIX regime

RISK_MODE_ALLOCATIONS: Dict[str, Dict[str, float]] = {
    'extreme_complacency': {         # VIX < 15
        'equity': 0.85,              # Reduce from 95% to 85%
        'fixed_income': 0.10,
        'cash_equivalent': 0.05,
        'description': 'Market overheated - trim winners, build cash'
    },
    'normal': {                      # VIX 15-25
        'equity': 0.95,              # Full aggressive allocation
        'fixed_income': 0.05,
        'cash_equivalent': 0.00,
        'description': 'Normal operations - fully invested per strategy'
    },
    'caution': {                     # VIX 25-35
        'equity': 0.80,              # Trim high-beta satellites
        'fixed_income': 0.15,
        'cash_equivalent': 0.05,
        'description': 'Elevated vol - reduce risk assets, increase bonds'
    },
    'risk_off': {                    # VIX > 35
        'equity': 0.60,              # Significant de-risking
        'fixed_income': 0.20,
        'cash_equivalent': 0.20,
        'description': 'Crisis mode - capital preservation priority'
    },
}


# ============================================================================
# Radar Scan Triggers
# ============================================================================
# Thresholds for flagging ETFs for deep analysis (Scalpel Dive)

RADAR_TRIGGERS: Dict[str, float | bool | int] = {
    'price_move_threshold': 0.015,     # 1.5% daily move (vs 2% conservative)
    'volume_spike_threshold': 1.30,    # 130% of 30-day avg (vs 150% conservative)
    'price_stddev_threshold': 2.0,     # 2 standard deviations from mean
    'momentum_crossover': True,        # Flag moving average crossovers
    'focus_list_max_size': 7,          # Max ETFs on daily Focus List
    'focus_list_min_size': 0,          # Allow empty Focus List on quiet days
    'rsi_overbought': 70.0,            # RSI threshold for overbought
    'rsi_oversold': 30.0,              # RSI threshold for oversold
}


# ============================================================================
# Trading Rules
# ============================================================================
# Constraints from project requirements and practical considerations

TRADING_RULES: Dict[str, float | bool] = {
    'commission_per_trade': 10.00,     # $10 flat commission per trade
    'allow_margin': False,             # No margin trading allowed
    'allow_partial_shares': False,     # Only whole shares
    'min_trade_size_usd': 500.00,      # Don't trade < $500 (commission = 2% drag)
    'max_trades_per_day': 10,          # Practical limit for execution
    'min_days_between_sells': 0,       # Can sell anytime
}


# ============================================================================
# Rebalancing Triggers
# ============================================================================
# When to trigger rebalancing vs accepting drift

REBALANCE_TRIGGERS: Dict[str, float | int] = {
    'core_drift_threshold': 0.10,      # Rebalance if core drifts >10% from target
    'position_drift_threshold': 0.05,  # Rebalance if position drifts >5%
    'days_between_rebalance': 7,       # Minimum 7 days between full rebalances
    'max_commission_pct': 0.005,       # Don't rebalance if commissions > 0.5% of portfolio
}


# ============================================================================
# Technical Indicator Parameters
# ============================================================================
# Parameters for calculating technical indicators in Radar Scan

TECHNICAL_PARAMS: Dict[str, int] = {
    'sma_short': 20,                   # 20-day simple moving average
    'sma_medium': 50,                  # 50-day simple moving average
    'sma_long': 200,                   # 200-day simple moving average
    'rsi_period': 14,                  # 14-day RSI
    'volume_lookback': 30,             # 30-day volume average
    'volatility_lookback': 30,         # 30-day volatility (for std dev)
    'bollinger_period': 20,            # Bollinger Band period
    'bollinger_stddev': 2,             # Bollinger Band std dev multiplier
    'macd_fast': 12,                   # MACD fast EMA
    'macd_slow': 26,                   # MACD slow EMA
    'macd_signal': 9,                  # MACD signal line
}


# ============================================================================
# Prospectus Settings
# ============================================================================
# Requirements for generating prospectus-ready justifications

PROSPECTUS_SETTINGS: Dict[str, int | bool] = {
    'min_justification_length': 100,   # Min characters for justification
    'include_prospectus_snippet': True,# Generate copy-paste ready text
    'prospectus_snippet_length': 300,  # Target length for snippet (words)
    'require_quantitative_evidence': True,  # Must include quant metrics
    'require_qualitative_evidence': True,   # Must include qual narrative
    'require_risk_assessment': True,   # Must include risk discussion
}


# ============================================================================
# News & LLM Settings
# ============================================================================
# Configuration for news analysis and LLM usage

NEWS_LLM_SETTINGS: Dict[str, int | str] = {
    'news_articles_per_etf': 5,        # Fetch top 5 articles per ETF
    'news_lookback_days': 2,           # Last 2 days of news
    'news_min_relevance': 0.3,         # Min relevance score to use article
    'llm_max_tokens': 500,             # Max tokens for LLM response
    'llm_temperature': 0.3,            # Low temperature for consistent output
    'llm_timeout_seconds': 30,         # Timeout for LLM API calls
}


# ============================================================================
# Data Fetching Settings
# ============================================================================
# Parameters for market data collection

DATA_SETTINGS: Dict[str, str | int] = {
    'market_data_period': '90d',       # 90 days for moving averages
    'market_data_interval': '1d',      # Daily bars
    'vix_ticker': '^VIX',              # VIX index ticker
    'benchmark_ticker': 'SPY',         # Benchmark for comparison
    'rate_limit_delay': 1.0,           # Seconds between API calls
    'max_retries': 3,                  # Max retries for failed API calls
    'retry_delay': 2.0,                # Seconds between retries
}


# ============================================================================
# Portfolio Settings
# ============================================================================
# Initial portfolio configuration

PORTFOLIO_SETTINGS: Dict[str, float | str] = {
    'initial_capital': 100000.00,      # Starting capital
    'portfolio_start_date': '2025-09-29',  # Project start date
    'target_return_annual': 0.10,      # 10% annual return target
    'max_drawdown_threshold': 0.20,    # Alert if drawdown > 20%
}


# ============================================================================
# Helper Functions
# ============================================================================

def get_risk_mode_from_vix(vix_level: float) -> str:
    """Determine risk mode based on VIX level

    Args:
        vix_level: Current VIX index value

    Returns:
        Risk mode: 'extreme_complacency', 'normal', 'caution', or 'risk_off'
    """
    if vix_level < VIX_THRESHOLDS['extreme_complacency']:
        return 'extreme_complacency'
    elif vix_level < VIX_THRESHOLDS['normal_upper']:
        return 'normal'
    elif vix_level < VIX_THRESHOLDS['risk_off']:
        return 'caution'
    else:
        return 'risk_off'


def get_target_allocation(risk_mode: str) -> Dict[str, float]:
    """Get target asset allocation for a given risk mode

    Args:
        risk_mode: Risk mode string

    Returns:
        Dictionary with target allocations
    """
    return RISK_MODE_ALLOCATIONS.get(risk_mode, RISK_MODE_ALLOCATIONS['normal'])


def validate_position_size(ticker: str, allocation: float, sector_allocation: float) -> bool:
    """Validate if a position size meets strategy constraints

    Args:
        ticker: ETF ticker
        allocation: Proposed allocation (0-1)
        sector_allocation: Current total sector allocation

    Returns:
        True if position is valid, False otherwise
    """
    if allocation > POSITION_LIMITS['single_position_max']:
        return False
    if sector_allocation > POSITION_LIMITS['sector_max']:
        return False
    return True


def calculate_commission_cost(num_trades: int) -> float:
    """Calculate total commission cost for trades

    Args:
        num_trades: Number of trades to execute

    Returns:
        Total commission cost in dollars
    """
    return num_trades * TRADING_RULES['commission_per_trade']


def should_execute_trade(trade_value: float) -> bool:
    """Check if trade value meets minimum threshold

    Args:
        trade_value: Dollar value of proposed trade

    Returns:
        True if trade should be executed, False otherwise
    """
    return trade_value >= TRADING_RULES['min_trade_size_usd']
