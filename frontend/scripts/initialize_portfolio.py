#!/usr/bin/env python3
"""Initialize Portfolio with Actual Holdings

Creates the initial portfolio state file with the user's actual ETF positions.

Portfolio Configuration:
- Initial Capital: $100,000
- Cash Balance: $23.95
- Positions:
  - IVV: 45 shares (30% allocation)
  - IYW: 128 shares (25% allocation)
  - IEMG: 303 shares (20% allocation)
  - ITA: 97 shares (20% allocation)
  - AGG: 50 shares (5% allocation)

Usage:
    python scripts/initialize_portfolio.py
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from data.models import (
    PortfolioState, Position, AllocationBreakdown, RiskMetrics
)
from data.storage import portfolio_storage
from data.data_fetcher import MarketDataFetcher

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def initialize_portfolio():
    """Initialize portfolio with actual holdings and fetch current prices"""

    logger.info("=" * 80)
    logger.info("PORTFOLIO INITIALIZATION")
    logger.info("=" * 80)
    logger.info("")

    # Portfolio configuration
    INITIAL_CAPITAL = 100000.00
    CASH_BALANCE = 23.95

    holdings = {
        'IVV': {'shares': 45, 'target_allocation': 0.30, 'cost_basis': 666.67},
        'IYW': {'shares': 128, 'target_allocation': 0.25, 'cost_basis': 195.31},
        'IEMG': {'shares': 303, 'target_allocation': 0.20, 'cost_basis': 66.01},
        'ITA': {'shares': 97, 'target_allocation': 0.20, 'cost_basis': 206.19},
        'AGG': {'shares': 50, 'target_allocation': 0.05, 'cost_basis': 100.00},
    }

    logger.info("Fetching current market prices...")
    fetcher = MarketDataFetcher()
    tickers = list(holdings.keys())
    market_data = fetcher.fetch_etf_data(tickers)

    if not market_data:
        logger.error("Failed to fetch market data. Cannot initialize portfolio.")
        sys.exit(1)

    logger.info("")
    logger.info("Building portfolio positions...")

    positions = {}
    total_equity_value = 0.0

    for ticker, config in holdings.items():
        if ticker not in market_data or market_data[ticker] is None:
            logger.error(f"Failed to fetch data for {ticker}")
            continue

        df = market_data[ticker]
        current_price = float(df['Close'].iloc[-1])
        shares = config['shares']
        cost_basis = config['cost_basis']

        market_value = shares * current_price
        total_equity_value += market_value

        unrealized_gain = shares * (current_price - cost_basis)
        unrealized_gain_pct = (current_price - cost_basis) / cost_basis if cost_basis > 0 else 0.0

        position = Position(
            ticker=ticker,
            shares=shares,
            cost_basis=cost_basis,
            current_price=current_price,
            market_value=market_value,
            weight=0.0,  # Will be calculated below
            unrealized_gain=unrealized_gain,
            unrealized_gain_pct=unrealized_gain_pct
        )

        positions[ticker] = position

        logger.info(f"  {ticker:5s}: {shares:3d} shares @ ${current_price:7.2f} = ${market_value:10.2f} "
                   f"(gain: ${unrealized_gain:+8.2f}, {unrealized_gain_pct:+6.2%})")

    # Calculate total value and weights
    total_value = total_equity_value + CASH_BALANCE

    for ticker, position in positions.items():
        position.weight = position.market_value / total_value

    logger.info("")
    logger.info(f"Total Equity Value: ${total_equity_value:,.2f}")
    logger.info(f"Cash Balance:       ${CASH_BALANCE:,.2f}")
    logger.info(f"Total Portfolio:    ${total_value:,.2f}")

    # Calculate returns
    total_return_pct = (total_value - INITIAL_CAPITAL) / INITIAL_CAPITAL
    daily_return_pct = 0.0  # Would need historical data

    logger.info(f"Total Return:       {total_return_pct:+.2%}")
    logger.info("")

    # Create allocation breakdown
    allocation_breakdown = AllocationBreakdown(
        core=0.30,  # IVV
        major_satellites=0.45,  # IYW + IEMG
        tactical_satellites=0.20,  # ITA
        hedging=0.05  # AGG
    )

    # Create sector breakdown
    sector_breakdown = {
        'Broad Market': positions['IVV'].weight,
        'Technology': positions['IYW'].weight,
        'Emerging Markets': positions['IEMG'].weight,
        'Aerospace & Defense': positions['ITA'].weight,
        'Fixed Income': positions['AGG'].weight,
    }

    # Create geography breakdown
    geography_breakdown = {
        'US': positions['IVV'].weight + positions['IYW'].weight + positions['ITA'].weight + positions['AGG'].weight,
        'Emerging Markets': positions['IEMG'].weight,
    }

    # Create risk metrics (placeholder values - would need historical data)
    risk_metrics = RiskMetrics(
        sharpe_ratio_30d=None,
        volatility_30d=None,
        max_drawdown=None,
        beta_to_spy=None,
        correlation_to_spy=None
    )

    # Create portfolio state
    portfolio = PortfolioState(
        as_of=datetime.now(),
        initial_capital=INITIAL_CAPITAL,
        total_value=total_value,
        cash_balance=CASH_BALANCE,
        total_return_pct=total_return_pct,
        daily_return_pct=daily_return_pct,
        positions=positions,
        allocation_breakdown=allocation_breakdown,
        sector_breakdown=sector_breakdown,
        geography_breakdown=geography_breakdown,
        risk_metrics=risk_metrics
    )

    # Save portfolio
    logger.info("Saving portfolio state...")
    success = portfolio_storage.save(portfolio)

    if success:
        logger.info(f"✓ Portfolio initialized successfully!")
        logger.info(f"  Saved to: {portfolio_storage.file_path}")
        logger.info("")
        logger.info("=" * 80)
        return 0
    else:
        logger.error("✗ Failed to save portfolio state")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(initialize_portfolio())
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
