"""Risk Manager Module

Implements VIX-based risk regime detection and portfolio risk controls.
Ensures portfolio adheres to position limits and adjusts allocation
targets based on market volatility conditions.
"""

import logging
from typing import Dict, List, Tuple
from enum import Enum

from config.strategy_params import (
    VIX_THRESHOLDS, RISK_MODE_ALLOCATIONS, POSITION_LIMITS
)
from config.etf_universe import ETF_UNIVERSE, AssetClass, ETFCategory
from data.models import RiskMode, PortfolioState, Position

logger = logging.getLogger(__name__)


# ============================================================================
# Risk Mode Detection
# ============================================================================

def determine_risk_mode(vix_level: float, vix_5d_avg: float) -> Tuple[RiskMode, str]:
    """Determine market risk mode based on VIX level

    Args:
        vix_level: Current VIX index value
        vix_5d_avg: 5-day average VIX

    Returns:
        Tuple of (RiskMode, description)
    """
    # Use current VIX but consider 5-day average for context
    vix_to_use = max(vix_level, vix_5d_avg)  # More conservative

    if vix_to_use < VIX_THRESHOLDS['extreme_complacency']:
        return (
            RiskMode.EXTREME_COMPLACENCY,
            f"VIX at {vix_level:.1f} indicates market complacency - reduce risk"
        )
    elif vix_to_use < VIX_THRESHOLDS['normal_upper']:
        return (
            RiskMode.NORMAL,
            f"VIX at {vix_level:.1f} indicates normal market conditions"
        )
    elif vix_to_use < VIX_THRESHOLDS['risk_off']:
        return (
            RiskMode.CAUTION,
            f"VIX at {vix_level:.1f} indicates elevated volatility - trim high-beta positions"
        )
    else:
        return (
            RiskMode.RISK_OFF,
            f"VIX at {vix_level:.1f} indicates crisis mode - defensive positioning required"
        )


def get_target_allocation(risk_mode: RiskMode) -> Dict[str, float]:
    """Get target asset class allocation for given risk mode

    Args:
        risk_mode: Current market risk mode

    Returns:
        Dict with target allocations by asset class
    """
    return RISK_MODE_ALLOCATIONS.get(
        risk_mode.value,
        RISK_MODE_ALLOCATIONS['normal']
    )


# ============================================================================
# Position Limit Validation
# ============================================================================

class PositionValidator:
    """Validates portfolio positions against strategy limits"""

    def __init__(self, portfolio: PortfolioState):
        self.portfolio = portfolio
        self.violations = []

    def validate_all(self) -> Tuple[bool, List[str]]:
        """Run all validation checks

        Returns:
            Tuple of (is_valid, list of violation messages)
        """
        self.violations = []

        self._validate_single_position_limits()
        self._validate_sector_concentration()
        self._validate_core_allocation()
        self._validate_equity_exposure()
        self._validate_cash_limit()

        is_valid = len(self.violations) == 0
        return is_valid, self.violations

    def _validate_single_position_limits(self):
        """Check individual position size limits"""
        max_position = POSITION_LIMITS['single_position_max']

        for ticker, position in self.portfolio.positions.items():
            if position.weight > max_position:
                self.violations.append(
                    f"{ticker} allocation ({position.weight:.1%}) exceeds "
                    f"max single position limit ({max_position:.1%})"
                )

    def _validate_sector_concentration(self):
        """Check sector concentration limits"""
        max_sector = POSITION_LIMITS['sector_max']

        for sector, allocation in self.portfolio.sector_breakdown.items():
            if allocation > max_sector:
                self.violations.append(
                    f"{sector} sector allocation ({allocation:.1%}) exceeds "
                    f"max sector limit ({max_sector:.1%})"
                )

    def _validate_core_allocation(self):
        """Check core allocation is within bounds"""
        core_min = POSITION_LIMITS['core_min']
        core_max = POSITION_LIMITS['core_max']
        core_actual = self.portfolio.allocation_breakdown.core

        if core_actual < core_min:
            self.violations.append(
                f"Core allocation ({core_actual:.1%}) below minimum ({core_min:.1%})"
            )
        elif core_actual > core_max:
            self.violations.append(
                f"Core allocation ({core_actual:.1%}) exceeds maximum ({core_max:.1%})"
            )

    def _validate_equity_exposure(self):
        """Check total equity exposure is within bounds"""
        equity_min = POSITION_LIMITS['equity_min']
        equity_max = POSITION_LIMITS['equity_max']

        # Calculate total equity allocation
        equity_total = sum(
            pos.weight for ticker, pos in self.portfolio.positions.items()
            if ETF_UNIVERSE[ticker]['asset_class'] == AssetClass.EQUITY
        )

        if equity_total < equity_min:
            self.violations.append(
                f"Equity exposure ({equity_total:.1%}) below minimum ({equity_min:.1%})"
            )
        elif equity_total > equity_max:
            self.violations.append(
                f"Equity exposure ({equity_total:.1%}) exceeds maximum ({equity_max:.1%})"
            )

    def _validate_cash_limit(self):
        """Check overnight cash doesn't exceed limit"""
        max_cash = POSITION_LIMITS['cash_overnight_max']
        sgov_exempt = POSITION_LIMITS['sgov_exempt']

        # Calculate cash allocation
        cash_allocation = self.portfolio.cash_balance / self.portfolio.total_value

        # Add SGOV if not exempt
        if not sgov_exempt and 'SGOV' in self.portfolio.positions:
            sgov_position = self.portfolio.positions['SGOV']
            cash_allocation += sgov_position.weight

        if cash_allocation > max_cash:
            self.violations.append(
                f"Cash allocation ({cash_allocation:.1%}) exceeds "
                f"overnight limit ({max_cash:.1%})"
            )


def validate_portfolio(portfolio: PortfolioState) -> Tuple[bool, List[str]]:
    """Convenience function to validate portfolio

    Args:
        portfolio: PortfolioState model

    Returns:
        Tuple of (is_valid, list of violations)
    """
    validator = PositionValidator(portfolio)
    return validator.validate_all()


# ============================================================================
# Risk Metrics Calculation
# ============================================================================

def calculate_portfolio_beta(
    portfolio_returns: List[float],
    benchmark_returns: List[float]
) -> float:
    """Calculate portfolio beta relative to benchmark

    Args:
        portfolio_returns: List of portfolio returns
        benchmark_returns: List of benchmark returns (same length)

    Returns:
        Portfolio beta
    """
    if len(portfolio_returns) != len(benchmark_returns) or len(portfolio_returns) < 2:
        return None

    import numpy as np

    # Convert to numpy arrays
    port_ret = np.array(portfolio_returns)
    bench_ret = np.array(benchmark_returns)

    # Calculate covariance and variance
    covariance = np.cov(port_ret, bench_ret)[0, 1]
    benchmark_variance = np.var(bench_ret)

    if benchmark_variance == 0:
        return None

    beta = covariance / benchmark_variance
    return round(float(beta), 2)


def calculate_sharpe_ratio(
    returns: List[float],
    risk_free_rate: float = 0.05
) -> float:
    """Calculate Sharpe ratio

    Args:
        returns: List of returns
        risk_free_rate: Annual risk-free rate (default: 5%)

    Returns:
        Sharpe ratio
    """
    if len(returns) < 2:
        return None

    import numpy as np

    # Convert to numpy array
    ret_array = np.array(returns)

    # Calculate mean and std
    mean_return = np.mean(ret_array)
    std_return = np.std(ret_array)

    if std_return == 0:
        return None

    # Annualize (assuming daily returns)
    annual_return = mean_return * 252
    annual_std = std_return * np.sqrt(252)

    # Calculate Sharpe ratio
    sharpe = (annual_return - risk_free_rate) / annual_std
    return round(float(sharpe), 2)


def calculate_max_drawdown(portfolio_values: List[float]) -> float:
    """Calculate maximum drawdown

    Args:
        portfolio_values: List of portfolio values over time

    Returns:
        Maximum drawdown as percentage (negative)
    """
    if len(portfolio_values) < 2:
        return 0.0

    import numpy as np

    values = np.array(portfolio_values)

    # Calculate running maximum
    running_max = np.maximum.accumulate(values)

    # Calculate drawdowns
    drawdowns = (values - running_max) / running_max

    # Get maximum drawdown
    max_dd = np.min(drawdowns)

    return round(float(max_dd), 4)


def calculate_sortino_ratio(
    returns: List[float],
    risk_free_rate: float = 0.05
) -> float:
    """Calculate Sortino ratio (uses downside deviation)

    Args:
        returns: List of returns
        risk_free_rate: Annual risk-free rate

    Returns:
        Sortino ratio
    """
    if len(returns) < 2:
        return None

    import numpy as np

    ret_array = np.array(returns)

    # Calculate mean return
    mean_return = np.mean(ret_array)

    # Calculate downside deviation (only negative returns)
    downside_returns = ret_array[ret_array < 0]
    if len(downside_returns) == 0:
        return None

    downside_std = np.std(downside_returns)

    if downside_std == 0:
        return None

    # Annualize
    annual_return = mean_return * 252
    annual_downside_std = downside_std * np.sqrt(252)

    # Calculate Sortino ratio
    sortino = (annual_return - risk_free_rate) / annual_downside_std

    return round(float(sortino), 2)


# ============================================================================
# Risk Adjustment Recommendations
# ============================================================================

def get_risk_adjustment_recommendations(
    risk_mode: RiskMode,
    current_portfolio: PortfolioState
) -> List[str]:
    """Generate recommendations for adjusting portfolio based on risk mode

    Args:
        risk_mode: Current market risk mode
        current_portfolio: Current portfolio state

    Returns:
        List of recommendation strings
    """
    recommendations = []
    target_allocation = get_target_allocation(risk_mode)

    # Calculate current equity exposure
    current_equity = sum(
        pos.weight for ticker, pos in current_portfolio.positions.items()
        if ETF_UNIVERSE[ticker]['asset_class'] == AssetClass.EQUITY
    )

    target_equity = target_allocation['equity']
    equity_delta = target_equity - current_equity

    if abs(equity_delta) > 0.05:  # 5% threshold
        if equity_delta > 0:
            recommendations.append(
                f"Increase equity exposure from {current_equity:.1%} to "
                f"{target_equity:.1%} (add {equity_delta:.1%})"
            )
        else:
            recommendations.append(
                f"Reduce equity exposure from {current_equity:.1%} to "
                f"{target_equity:.1%} (trim {abs(equity_delta):.1%})"
            )

    # Mode-specific recommendations
    if risk_mode == RiskMode.RISK_OFF:
        recommendations.extend([
            "Move to defensive positioning - prioritize capital preservation",
            "Consider increasing allocation to SGOV (cash equivalent)",
            "Trim high-beta positions (IYW, IJR, MCHI)",
            "Increase fixed income allocation (AGG, TLT)"
        ])
    elif risk_mode == RiskMode.CAUTION:
        recommendations.extend([
            "Elevated volatility detected - reduce risk in tactical satellites",
            "Consider trimming positions with outsized gains",
            "Monitor high-beta sectors (Technology, Small-Cap) closely"
        ])
    elif risk_mode == RiskMode.EXTREME_COMPLACENCY:
        recommendations.extend([
            "Market complacency detected - VIX unusually low",
            "Consider building cash reserves (SGOV) for tactical opportunities",
            "Avoid chasing momentum - risk/reward unfavorable"
        ])

    return recommendations


# ============================================================================
# Position Size Calculator
# ============================================================================

def calculate_safe_position_size(
    ticker: str,
    current_portfolio_value: float,
    sector_allocations: Dict[str, float]
) -> float:
    """Calculate maximum safe position size for an ETF

    Args:
        ticker: ETF ticker symbol
        current_portfolio_value: Current portfolio value
        sector_allocations: Current sector allocations

    Returns:
        Maximum safe position size in dollars
    """
    etf_info = ETF_UNIVERSE[ticker]
    sector = etf_info['sector']

    # Check single position limit
    max_single = POSITION_LIMITS['single_position_max']
    max_position_value = current_portfolio_value * max_single

    # Check sector limit
    max_sector = POSITION_LIMITS['sector_max']
    current_sector_allocation = sector_allocations.get(sector, 0.0)
    remaining_sector_allocation = max_sector - current_sector_allocation

    if remaining_sector_allocation <= 0:
        logger.warning(f"Sector {sector} already at limit ({current_sector_allocation:.1%})")
        return 0.0

    max_sector_value = current_portfolio_value * remaining_sector_allocation

    # Return minimum of the two constraints
    safe_size = min(max_position_value, max_sector_value)

    return round(safe_size, 2)


# ============================================================================
# Logging and Reporting
# ============================================================================

def log_risk_assessment(
    risk_mode: RiskMode,
    vix_level: float,
    portfolio: PortfolioState
):
    """Log comprehensive risk assessment

    Args:
        risk_mode: Current risk mode
        vix_level: Current VIX level
        portfolio: Portfolio state
    """
    logger.info("=" * 60)
    logger.info("RISK ASSESSMENT")
    logger.info("=" * 60)
    logger.info(f"VIX Level: {vix_level:.2f}")
    logger.info(f"Risk Mode: {risk_mode.value}")
    logger.info(f"Portfolio Value: ${portfolio.total_value:,.2f}")
    logger.info(f"Positions: {len(portfolio.positions)}")

    # Validation
    is_valid, violations = validate_portfolio(portfolio)
    if is_valid:
        logger.info("✓ Portfolio passes all risk checks")
    else:
        logger.warning(f"⚠ Portfolio has {len(violations)} violations:")
        for violation in violations:
            logger.warning(f"  - {violation}")

    # Allocation summary
    logger.info("Allocation Breakdown:")
    logger.info(f"  Core: {portfolio.allocation_breakdown.core:.1%}")
    logger.info(f"  Major Satellites: {portfolio.allocation_breakdown.major_satellites:.1%}")
    logger.info(f"  Tactical Satellites: {portfolio.allocation_breakdown.tactical_satellites:.1%}")
    logger.info(f"  Hedging: {portfolio.allocation_breakdown.hedging:.1%}")
    logger.info("=" * 60)
